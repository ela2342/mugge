"""F-439 / F-410 (filed as F-474): no web UI action raises a Mult behind a
closed D-063 gate.

Before the fix, unmute restored the web-ui pre-mute snapshot with no gate
check, so venue gain came back on the outputs while the GraphManager
reported the gate CLOSED (AE 455e0190 F1-F3, AE adf62efa).  The fix (PO r3
67f15d65) makes MUTE close the gate and removes unmute (410): the only way
back is Open Gate.

Against the real local-demo stack (QE 6e0e16b1 T1, QE/AE test form 8ab9077f):
    (a) gate open -> gate close -> mute -> unmute
    (b) gate open -> mute -> gate close -> unmute          (F-474 a1)
    (c) gate open -> unmute: 410 and every gain value unchanged
    a2  gate closed, venue selected: /config/gain, unmute, venue select and
        a DJ <-> standby switch each leave all 16 gain values (8 Mult,
        8 Add) at 0 (F-474 a2, AE 1fb3da7c P1)
Read-back and floor are asserted BEFORE the status code, so a run at base
shows the restored gains rather than a status mismatch.

The gate is opened through virtual_gate_open, unchanged, so the tone is
proven on hw-out before the close; a floor reading afterwards cannot come
from a dead tap or a missing stimulus.

Prerequisites:
    - ``nix run .#test-e2e`` (starts local-demo with the --tone stimulus)
"""

import pytest

from fixtures.backend import (  # noqa: F401
    HW_OUT_TONE_WINDOW_DB,
    VENUE,
    _switch_gm_mode_detail,
    LEVEL_FLOOR_DB,
    STIMULUS_HW_OUT_CHANNELS,
    _gate_state,
    in_window,
    nonzero_gains,
    read_back_gains,
    tone_channels,
    tone_on_sw_tap,
    virtual_gate_open,
    wait_for_peaks,
)


pytestmark = pytest.mark.service_integration

FLOOR_TIMEOUT_S = 2.0


def _post_ok(api_post, path: str) -> dict:
    status, body = api_post(path)
    assert status == 200 and body.get("ok"), f"{path} failed: {status} {body}"
    return body


def _assert_unmute_removed(status: int, body: dict) -> None:
    assert status == 410 and body.get("error") == "unmute_removed", (
        f"unmute must be removed (410): {status} {body}")


def _assert_all_zero(when: str) -> None:
    live = nonzero_gains(read_back_gains())
    assert not live, f"non-zero gain behind a closed gate {when}: {live}"


def _assert_hw_out_floor(port: int, when: str) -> None:
    peaks = wait_for_peaks(port, STIMULUS_HW_OUT_CHANNELS,
                           lambda p: max(p) <= LEVEL_FLOOR_DB,
                           timeout=FLOOR_TIMEOUT_S)
    assert max(peaks) <= LEVEL_FLOOR_DB, (
        f"hw-out {peaks} not at the {LEVEL_FLOOR_DB} dBFS floor {when}")


def _assert_tone_on_hw_out(port: int, expected: float) -> None:
    mains = wait_for_peaks(port, tone_channels(),
                           lambda p: in_window(p, expected, HW_OUT_TONE_WINDOW_DB),
                           timeout=FLOOR_TIMEOUT_S)
    assert in_window(mains, expected, HW_OUT_TONE_WINDOW_DB), (
        f"precondition: hw-out mains {mains} not within "
        f"{HW_OUT_TONE_WINDOW_DB} dB of {expected} dBFS with the gate open")


def _assert_fail_closed(base_url, api_get, port: int) -> None:
    """After unmute behind a closed gate: all 0, floor, gate closed, muted."""
    _assert_all_zero("after unmute")
    _assert_hw_out_floor(port, "after unmute with the gate closed")
    gate = _gate_state(base_url)
    assert gate.get("gate_open") is False, f"gate not reported closed: {gate}"
    _, mute = api_get("/api/v1/audio/mute-status")
    assert mute.get("is_muted") is True and mute.get("gate") == "closed", (
        f"a closed gate must read as muted: {mute}")


class TestUnmuteBehindClosedGate:
    """F-439 F3: unmute with the gate closed leaves every gain at 0."""

    def test_close_then_mute_then_unmute(self, virtual_gate_open, base_url,
                                         api_get, api_post, level_hw_out_port):
        """(a) gate close -> mute -> unmute: nothing is restored."""
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)

        _post_ok(api_post, "/api/v1/venue/gate/close")
        _assert_hw_out_floor(level_hw_out_port, "after gate close")
        _post_ok(api_post, "/api/v1/audio/mute")
        status, body = api_post("/api/v1/audio/unmute")

        _assert_fail_closed(base_url, api_get, level_hw_out_port)
        _assert_unmute_removed(status, body)

    def test_mute_then_close_then_unmute(self, virtual_gate_open, base_url,
                                         api_get, api_post, level_hw_out_port):
        """(b) / F-474 a1: mute -> gate close -> unmute restores nothing."""
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)

        _post_ok(api_post, "/api/v1/audio/mute")
        _assert_hw_out_floor(level_hw_out_port, "after mute")
        _post_ok(api_post, "/api/v1/venue/gate/close")
        status, body = api_post("/api/v1/audio/unmute")

        _assert_fail_closed(base_url, api_get, level_hw_out_port)
        _assert_unmute_removed(status, body)

    def test_unmute_with_gate_open_writes_nothing(self, virtual_gate_open,
                                                  api_post, level_hw_out_port):
        """(c) gate open -> unmute: 410, and every gain value is unchanged."""
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        before = read_back_gains()

        status, body = api_post("/api/v1/audio/unmute")

        after = read_back_gains()
        assert after == before, f"unmute changed gains: {before} -> {after}"
        _assert_unmute_removed(status, body)


class TestNoActionRaisesMult:
    """F-474 a2: with the gate closed, no web UI action other than Open
    Gate raises any Mult.

    The list covers every guarded Mult writer in app/ (unit test
    test_guarded_writers_are_the_ones_a2_covers): /config/gain here, the
    thermal limiter in the unit repros (it writes only below the live Mult,
    so nothing behind a closed gate).  The mode switch uses the GM set_mode
    RPC, the same call the measurement session makes; the web UI has no
    mode route.
    """

    def test_closed_gate_stays_zero(self, virtual_gate_open, api_post,
                                    gm_port, level_hw_out_port):
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        _post_ok(api_post, "/api/v1/venue/gate/close")
        _assert_all_zero("after gate close")
        _assert_hw_out_floor(level_hw_out_port, "after gate close")

        status, body = api_post("/api/v1/config/gain",
                                {"gains": {"gain_left_hp": 0.001}})
        _assert_all_zero("after POST /config/gain")
        _assert_hw_out_floor(level_hw_out_port, "after POST /config/gain")
        assert status == 409 and body.get("reason") == "gate_closed", (
            f"/config/gain must refuse with the gate closed: {status} {body}")

        status, body = api_post("/api/v1/audio/unmute")
        _assert_all_zero("after POST /audio/unmute")
        _assert_hw_out_floor(level_hw_out_port, "after POST /audio/unmute")
        _assert_unmute_removed(status, body)

        status, body = api_post("/api/v1/venue/select", {"venue": VENUE})
        _assert_all_zero("after POST /venue/select")
        _assert_hw_out_floor(level_hw_out_port, "after POST /venue/select")
        assert status == 200 and body.get("ok"), f"venue select: {status} {body}"

        for mode in ("standby", "dj"):
            ok, detail = _switch_gm_mode_detail(mode, gm_port)
            assert ok, f"switch to {mode} failed: {detail}"
            _assert_all_zero(f"after the switch to {mode}")
            _assert_hw_out_floor(level_hw_out_port, f"after the switch to {mode}")
