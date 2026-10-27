"""E2E tests for US-091 / F-439: audio mute against the real stack.

Verifies mute against the real local-demo stack — no mocks.  Since F-439
(PO r3 67f15d65) mute closes the D-063 gate (GM zeroes every gain) and
there is no unmute: POST /api/v1/audio/unmute returns 410 and the only way
back is Open Gate.  mute-status is derived from a fresh gate reading.
Every mute assertion reads all 16 gain values (8 Mult, 8 Add) back from
PipeWire (pw-cli, strict "Float 0.000000"), not only the hw-out level
(QE 6e0e16b1 T2, QE/AE 8ab9077f (c), AE 1fb3da7c P1).

Signal flow in DJ mode (routing.rs dj_links):
    Mixxx substitute (--tone) -> level-bridge-sw tap
                              -> convolver (FIR + gain nodes)
                              -> USBStreamer -> level-bridge-hw-out tap

level-bridge-sw is upstream of the gain nodes, so it only proves the
stimulus is present; mute can never show there. The mute evidence is
level-bridge-hw-out, downstream of the gains (F-394, AE Q2). That tap is
silent until the D-063 gate opens, so these tests open it in the virtual
stack only (virtual_gate_open refuses anywhere else).

Prerequisites:
    - ``nix run .#test-e2e`` (starts local-demo with the --tone stimulus)

Usage:
    nix run .#test-e2e
"""

import time

import pytest

from fixtures.backend import (  # noqa: F401
    HW_OUT_TONE_WINDOW_DB,
    _gate_state,
    LEVEL_FLOOR_DB,
    nonzero_gains,
    read_back_gains,
    SETTLE_S,
    STIMULUS_HW_OUT_CHANNELS,
    in_window,
    max_peak,
    read_live_levels,
    tone_channels,
    tone_on_sw_tap,
    virtual_gate_open,
    wait_for_peaks,
)


pytestmark = pytest.mark.service_integration

# AE Q2 C4: a real signal is >= -100 dBFS and >= 40 dB above the floor;
# mute reaches the floor within 2 s.
SIGNAL_MIN_DB = -100.0
ABOVE_FLOOR_DB = 40.0
MUTE_TIMEOUT_S = 2.0
TONE_TIMEOUT_S = 2.0


def _tone_on_hw_out(port: int, expected: float) -> list[float]:
    """Assert the tone on hw-out with the gate open; return the mains peaks.

    Mains: within HW_OUT_TONE_WINDOW_DB of expected (AE Q1 V2). Subs: presence
    only (AE Q1 V3), since the L+R sum level is not pinned.
    """
    time.sleep(SETTLE_S)
    mains = wait_for_peaks(port, tone_channels(),
                           lambda p: in_window(p, expected, HW_OUT_TONE_WINDOW_DB),
                           timeout=TONE_TIMEOUT_S)
    assert in_window(mains, expected, HW_OUT_TONE_WINDOW_DB), (
        f"hw-out mains {mains} not within {HW_OUT_TONE_WINDOW_DB} dB of {expected} dBFS")
    subs = [ch for ch in STIMULUS_HW_OUT_CHANNELS if ch not in tone_channels()]
    every = max_peak(read_live_levels(port, count=3), STIMULUS_HW_OUT_CHANNELS)
    for ch, peak in zip(STIMULUS_HW_OUT_CHANNELS, every):
        assert peak >= SIGNAL_MIN_DB and peak >= LEVEL_FLOOR_DB + ABOVE_FLOOR_DB, (
            f"hw-out ch {ch + 1} {'sub ' if ch in subs else ''}peak {peak} dBFS: "
            f"no signal with the gate open")
    return mains


def _assert_closed_and_silent(base_url, port: int, when: str) -> None:
    """All 16 gain values read back 0, hw-out at the floor, gate closed."""
    live = nonzero_gains(read_back_gains())
    assert not live, f"non-zero gain {when}: {live}"
    peaks = wait_for_peaks(port, STIMULUS_HW_OUT_CHANNELS,
                           lambda p: max(p) <= LEVEL_FLOOR_DB, timeout=MUTE_TIMEOUT_S)
    assert max(peaks) <= LEVEL_FLOOR_DB, (
        f"hw-out {peaks} not at the {LEVEL_FLOOR_DB} dBFS floor "
        f"{MUTE_TIMEOUT_S}s {when}")
    gate = _gate_state(base_url)
    assert gate.get("gate_open") is False, f"gate not reported closed {when}: {gate}"


def _mute_and_assert_floor(api_post, base_url, port: int) -> None:
    status, body = api_post("/api/v1/audio/mute")
    assert status == 200 and body.get("ok"), f"Mute failed: {body}"
    _assert_closed_and_silent(base_url, port, "after mute")


class TestMuteSilencesOutput:
    """Mute via API -> gate closed, all gains 0, hw-out reports silence."""

    def test_mute_returns_ok(self, api_post):
        """POST /api/v1/audio/mute returns ok=true."""
        status, body = api_post("/api/v1/audio/mute")
        assert status == 200, f"Mute failed: {status} {body}"
        assert body.get("ok") is True, f"Mute not ok: {body}"

    def test_mute_silences_hw_out(self, virtual_gate_open, base_url, api_post,
                                  level_hw_out_port):
        """Tone on hw-out with the gate open; after mute: closed, 0, floor."""
        _tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        assert _gate_state(base_url).get("gate_open") is True
        _mute_and_assert_floor(api_post, base_url, level_hw_out_port)


class TestUnmuteRestoresNothing:
    """Mute -> unmute: 410, and every gain stays at 0 (F-410, filed as F-474).

    Rewritten from TestUnmuteRestoresSignal (QE/AE 8ab9077f (c)); it keeps
    virtual_gate_open, so the closed-gate precondition runs here too.
    """

    def test_unmute_restores_nothing(self, virtual_gate_open, base_url,
                                     api_post, api_get, level_hw_out_port):
        """After mute, unmute returns 410 and nothing comes back."""
        _tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        _mute_and_assert_floor(api_post, base_url, level_hw_out_port)

        status, body = api_post("/api/v1/audio/unmute")

        _assert_closed_and_silent(base_url, level_hw_out_port, "after unmute")
        assert status == 410 and body.get("error") == "unmute_removed", (
            f"unmute must be removed: {status} {body}")
        _, mute = api_get("/api/v1/audio/mute-status")
        assert mute.get("is_muted") is True, f"not muted after unmute: {mute}"


class TestMuteIdempotency:
    """Double mute is a safe no-op."""

    def test_double_mute_is_idempotent(self, ensure_dj_mode, api_post, api_get):
        """Muting twice returns ok both times; closed and all gains 0 after.

        The old 'already muted' detail check is replaced by D1-D4: the r3
        mute response has no detail field (QE ruling 4dac2326).
        """
        s1, b1 = api_post("/api/v1/audio/mute")
        assert s1 == 200 and b1.get("ok") is True and b1.get("gate_open") is False, (
            f"First mute failed: {s1} {b1}")

        s2, b2 = api_post("/api/v1/audio/mute")
        assert s2 == 200 and b2.get("ok") is True and b2.get("gate_open") is False, (
            f"Double mute failed: {s2} {b2}")
        live = nonzero_gains(read_back_gains())
        assert not live, f"non-zero gain after the second mute: {live}"

        _, status_body = api_get("/api/v1/audio/mute-status")
        assert status_body.get("is_muted") is True
        assert status_body.get("gate") == "closed"


class TestMuteStatusEndpoint:
    """GET /api/v1/audio/mute-status follows the gate."""

    def test_initial_muted_gate_closed(self, ensure_dj_mode, api_get):
        """GM starts with the gate closed: status shows muted, gate closed."""
        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is True, f"Expected muted: {body}"
        assert body.get("gate") == "closed", body

    def test_not_muted_while_gate_open(self, virtual_gate_open, api_get):
        """Gate open: status shows not muted."""
        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is False, f"Expected not muted: {body}"
        assert body.get("gate") == "open", body

    def test_status_after_mute(self, ensure_dj_mode, api_post, api_get):
        """After mute, status shows muted."""
        api_post("/api/v1/audio/mute")

        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is True, f"Expected muted: {body}"
        assert body.get("gate") == "closed", body

    def test_status_after_unmute(self, tone_on_sw_tap, base_url, api_post,
                                 api_get, level_hw_out_port):
        """Unmute is 410: status unchanged and muted, all gains 0, floor."""
        api_post("/api/v1/audio/mute")
        _, before = api_get("/api/v1/audio/mute-status")

        status, body = api_post("/api/v1/audio/unmute")

        _assert_closed_and_silent(base_url, level_hw_out_port, "after unmute")
        _, after = api_get("/api/v1/audio/mute-status")
        assert after == before, f"unmute changed the status: {before} -> {after}"
        assert after.get("is_muted") is True, f"not muted after unmute: {after}"
        assert status == 410 and body.get("error") == "unmute_removed", (
            f"unmute must be removed: {status} {body}")
