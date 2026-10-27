"""Unit tests for the one guarded Mult writer and the F-439 mute rework.

    - gain_guard.guarded_set_mult: G3, zero always allowed, a fresh open
      gate for non-zero, every gate read failure refuses (architect NB
      dabf64de), and the AE B post-write re-read (AE 00e6f49a).
    - pw_helpers.validate_mult / format_mult (G3, F-352).
    - Grep guard (PO r3 §3): no Mult write outside the helper.
    - Mute routes: MUTE = close_gate, unmute 410, status from a fresh read.
    - Gate state for the status bar: collector freshness, ws_system.
    - Thermal limiter details beyond the F-345/F-355 repros.

The defect repros themselves are in test_f439_repro.py.
"""

import ast
import asyncio
import logging
import math
import subprocess
import time
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app import gain_guard, pw_helpers, venue_routes
from app.collectors import filterchain_collector
from app.collectors.filterchain_collector import FilterChainCollector
from app.thermal_limiter import ThermalGainLimiter
from app.ws_system import _gate_section

from .f439_fakes import FakeGM, FakePipeWire, closed_port

APP_DIR = Path(__file__).resolve().parents[2] / "app"


@pytest.fixture()
def gm(monkeypatch):
    """Factory: a started FakeGM in the given mode, wired into venue_routes."""
    started = []

    def _start(gate="open", pw=None):
        fake = FakeGM(gate=gate, pw=pw).__enter__()
        started.append(fake)
        monkeypatch.setattr(venue_routes, "MOCK_MODE", False)
        monkeypatch.setattr(venue_routes, "GM_HOST", "127.0.0.1")
        monkeypatch.setattr(venue_routes, "GM_PORT", fake.port)
        return fake

    yield _start
    for fake in started:
        fake.__exit__(None, None, None)


class RecordingWriter:
    def __init__(self, ok=True, during_write=None):
        self.ok = ok
        self.during_write = during_write
        self.writes = []

    async def __call__(self, node_id, name, mult):
        self.writes.append((name, mult))
        if self.during_write and mult != 0.0:
            self.during_write()
        return self.ok


def _guard(mult, writer):
    return asyncio.run(gain_guard.guarded_set_mult(42, "gain_left_hp", mult,
                                                   write=writer))


# ---------------------------------------------------------------------------
# guarded_set_mult
# ---------------------------------------------------------------------------

class TestGuardedSetMult:

    @pytest.mark.parametrize("mode", ["closed", "error", "silent"])
    def test_zero_always_allowed_without_gate_read(self, gm, mode):
        fake = gm(mode)
        writer = RecordingWriter()
        result = _guard(0.0, writer)
        assert result.ok
        assert writer.writes == [("gain_left_hp", 0.0)]
        assert fake.commands == []

    def test_open_gate_writes_and_rereads(self, gm):
        fake = gm("open")
        writer = RecordingWriter()
        result = _guard(0.01, writer)
        assert result.ok and result.reason is None
        assert writer.writes == [("gain_left_hp", 0.01)]
        assert fake.commands == ["get_gate", "get_gate"]

    def test_closed_gate_refuses(self, gm):
        gm("closed")
        writer = RecordingWriter()
        result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_CLOSED)
        assert writer.writes == []

    def test_gm_error_refuses_as_unknown(self, gm):
        gm("error")
        writer = RecordingWriter()
        result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_UNKNOWN)
        assert writer.writes == []

    def test_gm_timeout_refuses_as_unknown(self, gm, monkeypatch):
        gm("silent")
        monkeypatch.setattr(gain_guard, "GATE_READ_TIMEOUT_S", 0.2)
        writer = RecordingWriter()

        async def timed():
            t0 = time.monotonic()
            result = await gain_guard.guarded_set_mult(
                42, "gain_left_hp", 0.01, write=writer)
            return result, time.monotonic() - t0

        # Timed inside the loop: asyncio.run also waits for the abandoned
        # RPC thread, which ends at the client's own socket timeout.
        result, elapsed = asyncio.run(timed())
        assert (result.ok, result.reason) == (False, gain_guard.GATE_UNKNOWN)
        assert writer.writes == []
        assert elapsed < 1.5

    def test_gm_unreachable_refuses_as_unknown(self, monkeypatch):
        monkeypatch.setattr(venue_routes, "MOCK_MODE", False)
        monkeypatch.setattr(venue_routes, "GM_PORT", closed_port())
        writer = RecordingWriter()
        result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_UNKNOWN)
        assert writer.writes == []

    def test_mock_gm_is_closed(self, monkeypatch):
        monkeypatch.setattr(venue_routes, "MOCK_MODE", True)
        writer = RecordingWriter()
        result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_CLOSED)
        assert writer.writes == []

    @pytest.mark.parametrize("mult", [math.nan, math.inf, -math.inf, -0.001,
                                      1.0001, 1e-40, "0.01", True, None])
    def test_invalid_value_refused_before_gate_read(self, gm, mult):
        fake = gm("open")
        writer = RecordingWriter()
        result = _guard(mult, writer)
        assert (result.ok, result.reason) == (False, gain_guard.INVALID_VALUE)
        assert writer.writes == []
        assert fake.commands == []

    def test_gate_closing_during_write_writes_zero(self, gm, caplog):
        """AE B: the gate closes between the read and the write."""
        fake = gm("open")
        writer = RecordingWriter(during_write=fake.close_gate)
        with caplog.at_level(logging.WARNING, logger="app.gain_guard"):
            result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_CLOSED)
        assert writer.writes == [("gain_left_hp", 0.01), ("gain_left_hp", 0.0)]
        assert any("writing 0" in r.getMessage() for r in caplog.records
                   if r.levelno == logging.WARNING)

    def test_gate_unreadable_after_write_writes_zero(self, gm):
        fake = gm("open")
        writer = RecordingWriter(during_write=lambda: setattr(fake, "gate", "error"))
        result = _guard(0.01, writer)
        assert (result.ok, result.reason) == (False, gain_guard.GATE_UNKNOWN)
        assert writer.writes[-1] == ("gain_left_hp", 0.0)

    def test_write_failure_reported(self, gm):
        gm("open")
        result = _guard(0.01, RecordingWriter(ok=False))
        assert (result.ok, result.reason) == (False, gain_guard.WRITE_FAILED)

    def test_default_writer_is_pw_cli(self, gm, monkeypatch):
        pw = FakePipeWire()
        monkeypatch.setattr(pw_helpers, "subprocess", types.SimpleNamespace(
            run=pw.run, TimeoutExpired=subprocess.TimeoutExpired))
        gm("open", pw=pw)
        result = asyncio.run(gain_guard.guarded_set_mult(42, "gain_left_hp", 0.001))
        assert result.ok
        assert pw.writes == [("gain_left_hp", "0.001")]


# ---------------------------------------------------------------------------
# validate_mult / format_mult
# ---------------------------------------------------------------------------

class TestValidateMult:

    @pytest.mark.parametrize("mult", [0.0, 0, 1.0, 0.001, 0.000631,
                                      pw_helpers.FLT_MIN])
    def test_valid(self, mult):
        assert pw_helpers.validate_mult(mult) == float(mult)

    @pytest.mark.parametrize("mult", [math.nan, math.inf, -math.inf, -1e-9,
                                      1.0 + 1e-9, 1e-40, 5e-324, True, "1", None])
    def test_invalid(self, mult):
        with pytest.raises(ValueError):
            pw_helpers.validate_mult(mult)

    def test_negative_zero_normalised(self):
        assert math.copysign(1.0, pw_helpers.validate_mult(-0.0)) == 1.0

    def test_format_mult(self):
        assert pw_helpers.format_mult(0.001) == "0.001"
        assert pw_helpers.format_mult(0.0) == "0"
        assert pw_helpers.format_mult(0.000630957344) == "0.000630957344"

    def test_set_mult_refuses_invalid_without_pw_cli(self, monkeypatch):
        pw = FakePipeWire()
        monkeypatch.setattr(pw_helpers, "subprocess", types.SimpleNamespace(
            run=pw.run, TimeoutExpired=subprocess.TimeoutExpired))
        assert asyncio.run(pw_helpers.set_mult(42, "gain_left_hp", math.nan)) is False
        assert pw_helpers._set_mult_sync(42, "gain_left_hp", 2.0) is None
        assert pw.calls == []


# ---------------------------------------------------------------------------
# Grep guard: one Mult writer (PO r3 §3)
# ---------------------------------------------------------------------------

_WRITER_NAMES = {"set_mult", "_set_mult_sync"}
# Top-level app modules allowed to reference the low-level writer.
_ALLOWED = {"pw_helpers.py": _WRITER_NAMES | {"pw-cli s"},
            "gain_guard.py": {"set_mult"}}


def _mult_write_refs(tree: ast.AST) -> list[tuple[int, str]]:
    refs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _WRITER_NAMES:
            refs.append((node.lineno, node.id))
        elif isinstance(node, ast.Attribute) and node.attr in _WRITER_NAMES:
            refs.append((node.lineno, node.attr))
        elif isinstance(node, ast.ImportFrom):
            refs += [(node.lineno, a.name) for a in node.names
                     if a.name in _WRITER_NAMES]
        elif isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) >= 2:
            head = [e.value for e in node.elts[:2] if isinstance(e, ast.Constant)]
            if head == ["pw-cli", "s"]:
                refs.append((node.lineno, "pw-cli s"))
    return refs


class TestOneMultWriter:

    def test_no_mult_write_outside_helper(self):
        offenders = []
        for path in sorted(APP_DIR.rglob("*.py")):
            allowed = _ALLOWED.get(path.name, set()) if path.parent == APP_DIR else set()
            for lineno, name in _mult_write_refs(ast.parse(path.read_text())):
                if name not in allowed:
                    offenders.append(f"{path.relative_to(APP_DIR)}:{lineno} {name}")
        assert offenders == [], (
            "Mult writes must go through gain_guard.guarded_set_mult: "
            + ", ".join(offenders))

    def test_guarded_writers_are_the_ones_a2_covers(self):
        """AE 262206c3 NB: every guarded Mult writer is listed in F-474 a2.

        A new caller of guarded_set_mult fails here until it is added to
        test_unmute_gate_closed.py::TestNoActionRaisesMult (or, for the
        limiter, the unit repros) with a read-back after the call.
        """
        callers = set()
        for path in sorted(APP_DIR.rglob("*.py")):
            if path.name == "gain_guard.py":
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                name = (node.id if isinstance(node, ast.Name) else
                        node.attr if isinstance(node, ast.Attribute) else None)
                if name == "guarded_set_mult":
                    callers.add(str(path.relative_to(APP_DIR)))
        assert callers == {"config_routes.py", "thermal_limiter.py"}

    def test_guard_detects_a_raw_write(self):
        src = ("from .pw_helpers import set_mult\n"
               "async def f():\n    await set_mult(1, 'gain_x', 0.5)\n"
               "cmd = ['pw-cli', 's', '1', 'Props', '{}']\n")
        names = {name for _, name in _mult_write_refs(ast.parse(src))}
        assert names == {"set_mult", "pw-cli s"}


# ---------------------------------------------------------------------------
# Mute routes (mock mode: the per-request mock GM is closed)
# ---------------------------------------------------------------------------

class TestMuteRoutes:

    def test_mute_closes_gate(self, client):
        resp = client.post("/api/v1/audio/mute")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True, "gate_open": False}

    def test_mute_sends_close_gate(self, client, gm):
        fake = gm("open")
        resp = client.post("/api/v1/audio/mute")
        assert resp.status_code == 200
        assert "close_gate" in fake.commands
        assert fake.gate == "closed"

    @pytest.mark.parametrize("mode", ["error", "unreachable"])
    def test_mute_failure_is_502(self, client, gm, monkeypatch, mode):
        if mode == "unreachable":
            monkeypatch.setattr(venue_routes, "MOCK_MODE", False)
            monkeypatch.setattr(venue_routes, "GM_PORT", closed_port())
        else:
            gm("error")
        resp = client.post("/api/v1/audio/mute")
        assert resp.status_code == 502
        assert resp.json()["error"] == "close_gate_failed"

    def test_unmute_removed(self, client):
        resp = client.post("/api/v1/audio/unmute")
        assert resp.status_code == 410
        assert resp.json()["error"] == "unmute_removed"

    def test_mute_status_mock_closed(self, client):
        assert client.get("/api/v1/audio/mute-status").json() == {
            "is_muted": True, "gate": "closed"}

    @pytest.mark.parametrize("mode,expected", [
        ("open", {"is_muted": False, "gate": "open"}),
        ("closed", {"is_muted": True, "gate": "closed"}),
        ("error", {"is_muted": False, "gate": "unknown"}),
    ])
    def test_mute_status_from_fresh_read(self, client, gm, mode, expected):
        gm(mode)
        assert client.get("/api/v1/audio/mute-status").json() == expected


# ---------------------------------------------------------------------------
# Gate state for the status bar
# ---------------------------------------------------------------------------

def _collector(state, connected=True, age=0.0):
    fc = FilterChainCollector()
    fc._state = state
    fc._connected = connected
    fc._state_time = None if state is None else time.monotonic() - age
    return fc


class TestGateState:

    def test_fresh_open(self):
        assert _collector({"gate_open": True}).gate_state() == "open"

    def test_fresh_closed(self):
        assert _collector({"gate_open": False}).gate_state() == "closed"

    def test_missing_field_is_closed(self):
        assert _collector({}).gate_state() == "closed"

    def test_no_reading_is_unknown(self):
        assert _collector(None).gate_state() == "unknown"

    def test_disconnected_is_unknown(self):
        assert _collector({"gate_open": True}, connected=False).gate_state() == "unknown"

    def test_stale_is_unknown(self):
        stale = filterchain_collector.GATE_STATE_MAX_AGE_S + 0.5
        assert _collector({"gate_open": True}, age=stale).gate_state() == "unknown"

    def test_gate_section_without_collector(self):
        assert _gate_section(None)["state"] == "unknown"
        assert _gate_section(None)["gate_open"] is False

    def test_gate_section_follows_collector(self):
        fc = _collector({"gate_open": True, "venue_loaded": True,
                         "persisted_venue": "v"})
        section = _gate_section(fc)
        assert (section["state"], section["gate_open"]) == ("open", True)
        fc._connected = False
        section = _gate_section(fc)
        assert (section["state"], section["gate_open"]) == ("unknown", False)


# ---------------------------------------------------------------------------
# Thermal limiter details
# ---------------------------------------------------------------------------

def _limiter(headroom_db, pct=80.0):
    monitor = MagicMock()
    monitor.snapshot.return_value = [
        {"name": "sat_left", "headroom_db": headroom_db, "pct_of_ceiling": pct}]
    limiter = ThermalGainLimiter(monitor, is_mock=False)
    limiter.configure_channels([
        {"name": "sat_left", "channel_index": 0,
         "gain_node_name": "gain_left_hp", "base_mult": 0.001}])
    return limiter


@pytest.fixture()
def fake_pw(monkeypatch):
    pw = FakePipeWire({"gain_left_hp": 0.001})
    monkeypatch.setattr(pw_helpers, "subprocess", types.SimpleNamespace(
        run=pw.run, TimeoutExpired=subprocess.TimeoutExpired))
    return pw


class TestThermalLimiterGuarded:

    def test_refusal_keeps_current_mult_and_logs_once(self, gm, fake_pw, caplog):
        fake = gm("open", pw=fake_pw)
        fake.gate = "closed"  # closed, but the Mult was not zeroed (TOCTOU)
        limiter = _limiter(1.0)
        ch = limiter._channels["sat_left"]
        with caplog.at_level(logging.WARNING, logger="app.thermal_limiter"):
            for t in (100.0, 101.0, 102.0):
                asyncio.run(limiter._enforce_tick(t))
        assert fake_pw.writes == []
        assert ch.current_mult == 0.001
        assert ch.blocked == gain_guard.GATE_CLOSED
        refusals = [r for r in caplog.records if "reduction not written" in r.getMessage()]
        assert len(refusals) == 1

    def test_rate_limited(self, gm, fake_pw):
        gm("open", pw=fake_pw)
        limiter = _limiter(1.0)
        asyncio.run(limiter._enforce_tick(100.0))
        limiter._monitor.snapshot.return_value[0]["headroom_db"] = 0.5
        asyncio.run(limiter._enforce_tick(100.1))
        assert len(fake_pw.writes) == 1

    def test_unreadable_live_mult_drops_cached_node_id(self, gm, fake_pw):
        gm("open", pw=fake_pw)
        limiter = _limiter(1.0)
        limiter._convolver_node_id = 7  # stale after a PipeWire restart
        real_run = fake_pw.run

        def run(args, *a, **kw):
            if args[:2] == ["pw-cli", "enum-params"] and args[2] == "7":
                return subprocess.CompletedProcess(args, 1, b"", b"no node")
            return real_run(args, *a, **kw)

        pw_helpers.subprocess.run = run
        asyncio.run(limiter._enforce_tick(100.0))
        assert limiter._convolver_node_id is None
        assert fake_pw.writes == []
        asyncio.run(limiter._enforce_tick(101.0))
        assert limiter._convolver_node_id == 42
        assert len(fake_pw.writes) == 1

    def test_read_failure_latches_fault_until_next_good_read(
            self, gm, fake_pw, caplog):
        """AE 56043d31 C3/C6(iii): no write, fault in snapshot and /ws/system."""
        from app.thermal_limiter import READBACK_FAILED
        from app.ws_system import _thermal_limiter_section
        gm("open", pw=fake_pw)
        limiter = _limiter(1.0)
        real_run = fake_pw.run
        failing = {"on": True}

        def run(args, *a, **kw):
            if failing["on"] and args[:2] == ["pw-cli", "enum-params"]:
                return subprocess.CompletedProcess(args, 1, b"", b"error")
            return real_run(args, *a, **kw)

        pw_helpers.subprocess.run = run
        app = types.SimpleNamespace(
            state=types.SimpleNamespace(thermal_limiter=limiter))
        with caplog.at_level(logging.ERROR, logger="app.thermal_limiter"):
            for t in (100.0, 101.0, 102.0):
                asyncio.run(limiter._enforce_tick(t))
        assert fake_pw.writes == []
        expected = [{"channel": "sat_left", "fault": READBACK_FAILED}]
        snap = limiter.snapshot()
        assert snap["channels"][0]["readback_fault"] == READBACK_FAILED
        assert snap["faults"] == expected and snap["degraded"] is True
        assert _thermal_limiter_section(app) == {
            "degraded": True, "faults": expected}
        latched = [r for r in caplog.records if "FAULT" in r.getMessage()]
        assert len(latched) == 1  # once per state change, not per tick

        failing["on"] = False
        asyncio.run(limiter._enforce_tick(103.0))
        assert len(fake_pw.writes) == 1
        assert limiter.snapshot()["degraded"] is False
        assert _thermal_limiter_section(app) == {"degraded": False, "faults": []}

    def test_target_at_or_above_live_never_written(self, gm, fake_pw):
        """AE 56043d31 C2/C6(ii): write iff target < live."""
        gm("open", pw=fake_pw)
        limiter = _limiter(1.0)
        target = 0.001 * limiter.compute_reduction(1.0, 80.0, "sat_left")
        for live in (target, target + 5e-7, target * 0.5):
            fake_pw.mults["gain_left_hp"] = live
            limiter._channels["sat_left"].last_update_time = 0.0
            asyncio.run(limiter._enforce_tick(100.0))
        assert fake_pw.writes == []

    def test_constant_factor_one_write_no_compounding(self, gm, fake_pw):
        """AE 56043d31 C1/C6(iv): target = base * factor, never factor * live."""
        gm("open", pw=fake_pw)
        limiter = _limiter(1.0)
        for i in range(10):
            asyncio.run(limiter._enforce_tick(100.0 + i))
        factor = limiter._channels["sat_left"].reduction_factor
        assert len(fake_pw.writes) == 1
        assert float(fake_pw.writes[0][1]) == pytest.approx(0.001 * factor, abs=1e-6)
        assert fake_pw.mults["gain_left_hp"] == pytest.approx(0.001 * factor, abs=1e-6)
