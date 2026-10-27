"""F-410 (filed as F-474) b1/b2: standby zeroes every gain, with and without mute.

QE/AE test form r2 8ab9077f, released by the AE in 262206c3. Standby is
entered the way the measurement session's end path does it:
MeasurementSession._restore_production_mode (app/measurement/session.py)
sends the GM ``set_mode`` RPC and then ``await_settled``. The GM closes the
D-063 gate on standby and zeroes the gain Mults asynchronously.

- b1: standby, then POST /api/v1/audio/mute within 100 ms of set_mode
  returning. All 16 gain values (8 Mult, 8 Add) read back 0 within 2 s,
  hw-out at the floor, gate reported closed.
- b2: the same without the mute, isolating GM zeroing. A failure here is
  a separate GM defect: no retry, xfail or skip (PO 123cb139).

Each test runs 10 iterations. Every iteration opens the gate through the
product path (DJ mode, venue select, gate open) and proves the tone on
hw-out before entering standby. Each iteration prints one line
``F-474-b iter=<n> ok mults=<8 values> adds=<8 values> t_zero_ms=<ms>``
for the PR body.

Usage:
    nix run .#test-e2e
"""

import time

import pytest

from fixtures.backend import (  # noqa: F401
    GAIN_NAMES,
    HW_OUT_TONE_WINDOW_DB,
    LEVEL_FLOOR_DB,
    SETTLE_S,
    STIMULUS_HW_OUT_CHANNELS,
    VENUE,
    _api_post,
    _gate_state,
    _rpc_call,
    _switch_gm_mode_detail,
    in_window,
    nonzero_gains,
    read_back_gains,
    tone_channels,
    tone_on_sw_tap,
    virtual_gate_open,
    wait_for_peaks,
)


pytestmark = pytest.mark.service_integration

ITERATIONS = 10
MUTE_WITHIN_S = 0.1
ZERO_DEADLINE_S = 2.0
TONE_TIMEOUT_S = 2.0


def _open_gate_and_prove_tone(base_url, gm_port: int, port: int,
                              expected: float, n: int) -> None:
    """Product path back to an open gate, then the tone on the hw-out mains."""
    ok, detail = _switch_gm_mode_detail("dj", gm_port)
    assert ok, f"iter={n}: switch to dj failed: {detail}"
    status, body = _api_post(base_url, "/api/v1/venue/select", {"venue": VENUE})
    assert status == 200 and body.get("ok"), f"iter={n}: venue select: {status} {body}"
    status, body = _api_post(base_url, "/api/v1/venue/gate/open")
    assert status == 200 and body.get("gate_open"), f"iter={n}: gate open: {status} {body}"
    time.sleep(SETTLE_S)
    mains = wait_for_peaks(port, tone_channels(),
                           lambda p: in_window(p, expected, HW_OUT_TONE_WINDOW_DB),
                           timeout=TONE_TIMEOUT_S)
    assert in_window(mains, expected, HW_OUT_TONE_WINDOW_DB), (
        f"iter={n}: hw-out mains {mains} not within {HW_OUT_TONE_WINDOW_DB} dB "
        f"of {expected} dBFS with the gate open")


def _standby_like_session_end(gm_port: int, n: int) -> tuple[dict, float]:
    """set_mode standby as _restore_production_mode does; return reply and time."""
    resp = _rpc_call("127.0.0.1", gm_port, {"cmd": "set_mode", "mode": "standby"})
    returned = time.monotonic()
    assert resp.get("ok"), f"iter={n}: set_mode standby failed: {resp}"
    return resp, returned


def _await_settled(gm_port: int, resp: dict, n: int) -> None:
    settled = _rpc_call("127.0.0.1", gm_port, {
        "cmd": "await_settled",
        "since_epoch": resp.get("epoch", 0),
        "timeout_ms": 10000,
    }, timeout=15.0)
    assert settled.get("ok"), f"iter={n}: await_settled after standby: {settled}"


def _wait_all_zero(since: float, n: int) -> tuple[dict, float]:
    """Poll the read-back until all 16 gain values are 0; FAIL at 2 s."""
    while True:
        gains = read_back_gains()
        elapsed = time.monotonic() - since
        live = nonzero_gains(gains)
        if not live:
            return gains, elapsed
        assert elapsed < ZERO_DEADLINE_S, (
            f"iter={n}: gains not all 0 {ZERO_DEADLINE_S}s after standby: {live}")


def _assert_closed_and_silent(base_url, port: int, n: int) -> None:
    peaks = wait_for_peaks(port, STIMULUS_HW_OUT_CHANNELS,
                           lambda p: max(p) <= LEVEL_FLOOR_DB, timeout=ZERO_DEADLINE_S)
    assert max(peaks) <= LEVEL_FLOOR_DB, (
        f"iter={n}: hw-out {peaks} not at the {LEVEL_FLOOR_DB} dBFS floor")
    gate = _gate_state(base_url)
    assert gate.get("gate_open") is False, f"iter={n}: gate not reported closed: {gate}"


def _run(capsys, virtual_gate_open, base_url, gm_port, port, mute: bool) -> None:
    expected = virtual_gate_open
    for n in range(1, ITERATIONS + 1):
        _open_gate_and_prove_tone(base_url, gm_port, port, expected, n)

        resp, returned = _standby_like_session_end(gm_port, n)
        if mute:
            lag = time.monotonic() - returned
            assert lag < MUTE_WITHIN_S, f"iter={n}: mute sent {lag * 1000:.0f} ms late"
            status, body = _api_post(base_url, "/api/v1/audio/mute")
            assert status == 200 and body.get("ok"), f"iter={n}: mute: {status} {body}"

        gains, t_zero = _wait_all_zero(returned, n)
        _assert_closed_and_silent(base_url, port, n)
        _await_settled(gm_port, resp, n)

        mults, adds = (",".join(gains[f"{name}:{param}"].removeprefix("Float ")
                                for name in GAIN_NAMES)
                       for param in ("Mult", "Add"))
        with capsys.disabled():
            print(f"F-474-b iter={n} ok mults={mults} adds={adds} "
                  f"t_zero_ms={t_zero * 1000:.0f}")


class TestStandbyZeroesGains:
    """F-474 b1/b2: 10 iterations each, product-path re-open every time."""

    def test_b1_standby_then_mute(self, capsys, virtual_gate_open, base_url,
                                  gm_port, level_hw_out_port):
        """b1: standby + mute within 100 ms -> all 0 within 2 s, floor, closed."""
        _run(capsys, virtual_gate_open, base_url, gm_port, level_hw_out_port,
             mute=True)

    def test_b2_standby_without_mute(self, capsys, virtual_gate_open, base_url,
                                     gm_port, level_hw_out_port):
        """b2: standby alone (GM zeroing) -> all 0 within 2 s, floor, closed."""
        _run(capsys, virtual_gate_open, base_url, gm_port, level_hw_out_port,
             mute=False)
