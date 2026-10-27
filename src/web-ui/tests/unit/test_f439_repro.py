"""Defect repro tests closed by F-320 F / F-439 (PO r3 67f15d65, QE f5c607ef).

One named test (or group) per defect.  Each is red at base ff55d0c8 and
green at the fix; the PR body carries both runs.  They use only interfaces
that exist at base (the /api/v1/config/gain route, ThermalGainLimiter),
with fakes at the process boundary (``f439_fakes``): PipeWire behind
``subprocess.run`` and a GraphManager on a localhost port.

    F-344  a gain write raises Mult while the gate is closed or unknown.
    F-352  NaN, inf, a subnormal or > 1.0 reaches pw-cli (or is clamped).
    F-345  the thermal limiter raises Mult on recovery after a gate close,
           writes a non-zero reduction while the gate is closed, or skips
           the reduction after a gate reopen (stale cached Mult).
    F-355  a NaN headroom becomes a NaN Mult write (AC a, part of c only).
"""

import asyncio
import math
import subprocess
import types
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app import config_routes, pw_helpers, venue_routes
from app.thermal_limiter import ThermalGainLimiter

from .f439_fakes import FakeGM, FakePipeWire, closed_port

VENUE_MULT = 0.001  # the -60 dB mains default


@pytest.fixture()
def fake_pw(monkeypatch):
    pw = FakePipeWire()
    monkeypatch.setattr(pw_helpers, "subprocess", types.SimpleNamespace(
        run=pw.run, TimeoutExpired=subprocess.TimeoutExpired,
        CompletedProcess=subprocess.CompletedProcess))
    return pw


@pytest.fixture()
def gm(monkeypatch, fake_pw):
    """A started FakeGM wired into venue_routes (real client, not the mock)."""
    with FakeGM(gate="open", pw=fake_pw) as fake:
        monkeypatch.setattr(venue_routes, "MOCK_MODE", False)
        monkeypatch.setattr(venue_routes, "GM_HOST", "127.0.0.1")
        monkeypatch.setattr(venue_routes, "GM_PORT", fake.port)
        yield fake


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(config_routes, "MOCK_MODE", False)
    app = FastAPI()
    app.include_router(config_routes.router)
    # A server crash is a 500 the assertions can see, not a test error.
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _post_gain(client, raw_value: str):
    return client.post(
        "/api/v1/config/gain",
        content='{"gains": {"gain_left_hp": %s}}' % raw_value,
        headers={"Content-Type": "application/json"})


# ---------------------------------------------------------------------------
# F-344: config gain write while the gate is not open
# ---------------------------------------------------------------------------

class TestF344GainWriteNeedsOpenGate:

    def test_F344_refused_while_gate_closed(self, gm, fake_pw, client):
        gm.close_gate()
        resp = client.post("/api/v1/config/gain",
                           json={"gains": {"gain_left_hp": 0.01}})
        assert fake_pw.nonzero_writes() == [], (
            f"non-zero Mult reached pw-cli with the gate closed: {fake_pw.writes}")
        assert resp.status_code == 409, resp.text
        assert resp.json()["reason"] == "gate_closed"
        assert all(m == 0.0 for m in fake_pw.mults.values())

    def test_F344_refused_when_gm_unreachable(self, monkeypatch, fake_pw, client):
        monkeypatch.setattr(venue_routes, "MOCK_MODE", False)
        monkeypatch.setattr(venue_routes, "GM_PORT", closed_port())
        resp = client.post("/api/v1/config/gain",
                           json={"gains": {"gain_left_hp": 0.01}})
        assert fake_pw.nonzero_writes() == [], (
            f"non-zero Mult reached pw-cli with GM unreachable: {fake_pw.writes}")
        assert resp.status_code == 409, resp.text
        assert resp.json()["reason"] == "gate_unknown"


# ---------------------------------------------------------------------------
# F-352: invalid Mult values are refused, never clamped, never written
# ---------------------------------------------------------------------------

class TestF352InvalidMultRefused:

    @pytest.mark.parametrize(
        "raw", ["NaN", "Infinity", "-Infinity", "1e-40", "1.5", "-0.5"])
    def test_F352_invalid_value_never_reaches_pw_cli(
            self, monkeypatch, gm, fake_pw, client, raw):
        # config_routes runs its own subprocess calls (quantum); route
        # them to the fake too, so "no call at all" covers the module.
        monkeypatch.setattr(config_routes, "subprocess", types.SimpleNamespace(
            run=fake_pw.run, TimeoutExpired=subprocess.TimeoutExpired,
            CompletedProcess=subprocess.CompletedProcess))
        resp = _post_gain(client, raw)
        assert fake_pw.writes == [], (
            f"Mult {raw} reached pw-cli as {fake_pw.writes}")
        assert resp.status_code == 422, resp.text
        # A refused request makes no PipeWire call at all, not even a read.
        assert fake_pw.calls == [], f"422 for {raw} still ran {fake_pw.calls}"


# ---------------------------------------------------------------------------
# F-345: thermal limiter is reduce-only and never raises past a closed gate
# ---------------------------------------------------------------------------

def _limiter(headroom_db: float, pct: float) -> ThermalGainLimiter:
    monitor = MagicMock()
    monitor.snapshot.return_value = [
        {"name": "sat_left", "headroom_db": headroom_db, "pct_of_ceiling": pct}]
    limiter = ThermalGainLimiter(monitor, is_mock=False)
    limiter.configure_channels([
        {"name": "sat_left", "channel_index": 0,
         "gain_node_name": "gain_left_hp", "base_mult": VENUE_MULT}])
    return limiter


def _set_thermal(limiter, headroom_db: float, pct: float) -> None:
    limiter._monitor.snapshot.return_value = [
        {"name": "sat_left", "headroom_db": headroom_db, "pct_of_ceiling": pct}]


class TestF345LimiterReduceOnly:

    def test_F345_no_raise_on_recovery_after_gate_close(self, gm, fake_pw):
        fake_pw.mults["gain_left_hp"] = VENUE_MULT
        limiter = _limiter(headroom_db=1.0, pct=80.0)

        asyncio.run(limiter._enforce_tick(100.0))
        assert limiter._channels["sat_left"].is_limiting
        engaged_writes = list(fake_pw.writes)
        assert engaged_writes and float(engaged_writes[-1][1]) < VENUE_MULT

        gm.close_gate()  # GM zeroes every Mult
        _set_thermal(limiter, headroom_db=10.0, pct=10.0)
        asyncio.run(limiter._enforce_tick(101.0))

        assert fake_pw.writes == engaged_writes, (
            f"limiter wrote after the gate closed: {fake_pw.writes[len(engaged_writes):]}")
        assert fake_pw.mults["gain_left_hp"] == 0.0

    def test_F345_reduction_reapplied_after_gate_reopen(self, gm, fake_pw):
        """AE 56043d31 C6(i): a stale cached Mult must not skip the reduction."""
        fake_pw.mults["gain_left_hp"] = VENUE_MULT
        limiter = _limiter(headroom_db=1.0, pct=80.0)
        asyncio.run(limiter._enforce_tick(100.0))
        assert fake_pw.mults["gain_left_hp"] < VENUE_MULT
        reduced = fake_pw.mults["gain_left_hp"]

        # Close Gate -> Open Gate: GM zeroes, then restores the venue gain.
        gm.close_gate()
        gm.gate = "open"
        fake_pw.mults["gain_left_hp"] = VENUE_MULT
        asyncio.run(limiter._enforce_tick(101.0))

        assert fake_pw.mults["gain_left_hp"] == pytest.approx(reduced), (
            "limiter left the venue gain at "
            f"{fake_pw.mults['gain_left_hp']} after the gate reopened "
            f"(reduction {reduced} not re-applied; writes {fake_pw.writes})")

    def test_F345_no_reduction_write_while_gate_closed(self, gm, fake_pw):
        gm.close_gate()
        limiter = _limiter(headroom_db=1.0, pct=80.0)

        asyncio.run(limiter._enforce_tick(100.0))

        assert fake_pw.nonzero_writes() == [], (
            f"limiter wrote a non-zero Mult with the gate closed: {fake_pw.writes}")
        assert fake_pw.mults["gain_left_hp"] == 0.0


# ---------------------------------------------------------------------------
# F-355 (partial: AC a, part of c): NaN headroom never becomes a write
# ---------------------------------------------------------------------------

class TestF355NonFiniteNeverWritten:

    def test_F355_nan_headroom_not_written(self, gm, fake_pw):
        fake_pw.mults["gain_left_hp"] = VENUE_MULT
        limiter = _limiter(headroom_db=math.nan, pct=80.0)

        asyncio.run(limiter._enforce_tick(100.0))

        assert fake_pw.writes == [], f"NaN headroom was written: {fake_pw.writes}"
        assert fake_pw.mults["gain_left_hp"] == VENUE_MULT
        assert getattr(limiter._channels["sat_left"], "fault", None) == "non_finite_target"
