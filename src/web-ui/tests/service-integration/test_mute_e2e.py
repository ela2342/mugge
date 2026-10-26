"""E2E tests for US-091: Audio mute with dynamic gain node discovery.

Verifies mute/unmute against the real local-demo stack — no mocks.
The mute API sets all filter-chain gain nodes (linear builtin Mult params)
to 0.0; unmute restores the pre-mute values.

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
    LEVEL_FLOOR_DB,
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
# mute reaches the floor within 2 s; unmute returns within 3 dB of the
# pre-mute level within 2 s.
SIGNAL_MIN_DB = -100.0
ABOVE_FLOOR_DB = 40.0
MUTE_TIMEOUT_S = 2.0
UNMUTE_TIMEOUT_S = 2.0
UNMUTE_MATCH_DB = 3.0


def _tone_on_hw_out(port: int, expected: float) -> list[float]:
    """Assert the tone on hw-out with the gate open; return the mains peaks.

    Mains: within HW_OUT_TONE_WINDOW_DB of expected (AE Q1 V2). Subs: presence
    only (AE Q1 V3), since the L+R sum level is not pinned.
    """
    time.sleep(SETTLE_S)
    mains = wait_for_peaks(port, tone_channels(),
                           lambda p: in_window(p, expected, HW_OUT_TONE_WINDOW_DB),
                           timeout=UNMUTE_TIMEOUT_S)
    assert in_window(mains, expected, HW_OUT_TONE_WINDOW_DB), (
        f"hw-out mains {mains} not within {HW_OUT_TONE_WINDOW_DB} dB of {expected} dBFS")
    subs = [ch for ch in STIMULUS_HW_OUT_CHANNELS if ch not in tone_channels()]
    every = max_peak(read_live_levels(port, count=3), STIMULUS_HW_OUT_CHANNELS)
    for ch, peak in zip(STIMULUS_HW_OUT_CHANNELS, every):
        assert peak >= SIGNAL_MIN_DB and peak >= LEVEL_FLOOR_DB + ABOVE_FLOOR_DB, (
            f"hw-out ch {ch + 1} {'sub ' if ch in subs else ''}peak {peak} dBFS: "
            f"no signal with the gate open")
    return mains


def _mute_and_assert_floor(api_post, port: int) -> None:
    status, body = api_post("/api/v1/audio/mute")
    assert status == 200 and body.get("ok"), f"Mute failed: {body}"
    peaks = wait_for_peaks(port, STIMULUS_HW_OUT_CHANNELS,
                           lambda p: max(p) <= LEVEL_FLOOR_DB, timeout=MUTE_TIMEOUT_S)
    assert max(peaks) <= LEVEL_FLOOR_DB, (
        f"hw-out {peaks} not at the {LEVEL_FLOOR_DB} dBFS floor "
        f"{MUTE_TIMEOUT_S}s after mute")


class TestMuteSilencesOutput:
    """Mute via API -> level-bridge-hw-out reports silence."""

    def test_mute_returns_ok(self, api_post):
        """POST /api/v1/audio/mute returns ok=true."""
        status, body = api_post("/api/v1/audio/mute")
        assert status == 200, f"Mute failed: {status} {body}"
        assert body.get("ok") is True, f"Mute not ok: {body}"

        # Cleanup: unmute so subsequent tests start clean
        api_post("/api/v1/audio/unmute")

    def test_mute_silences_hw_out(self, virtual_gate_open, api_post,
                                  level_hw_out_port):
        """Tone on hw-out with the gate open; after mute, hw-out is at the floor."""
        _tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        _mute_and_assert_floor(api_post, level_hw_out_port)


class TestUnmuteRestoresSignal:
    """Mute -> unmute -> level-bridge-hw-out reports the tone again."""

    def test_unmute_restores_levels(self, virtual_gate_open, api_post,
                                    level_hw_out_port):
        """After unmute, hw-out mains return to the pre-mute tone level."""
        pre = _tone_on_hw_out(level_hw_out_port, virtual_gate_open)
        _mute_and_assert_floor(api_post, level_hw_out_port)

        status, body = api_post("/api/v1/audio/unmute")
        assert status == 200 and body.get("ok"), f"Unmute failed: {body}"
        post = wait_for_peaks(
            level_hw_out_port, tone_channels(),
            lambda p: in_window(p, virtual_gate_open, HW_OUT_TONE_WINDOW_DB),
            timeout=UNMUTE_TIMEOUT_S)
        assert in_window(post, virtual_gate_open, HW_OUT_TONE_WINDOW_DB), (
            f"hw-out mains {post} not back within {HW_OUT_TONE_WINDOW_DB} dB of "
            f"{virtual_gate_open} dBFS {UNMUTE_TIMEOUT_S}s after unmute")
        assert all(abs(a - b) <= UNMUTE_MATCH_DB for a, b in zip(pre, post)), (
            f"unmute level {post} not within {UNMUTE_MATCH_DB} dB of pre-mute {pre}")


class TestMuteIdempotency:
    """Double-mute and double-unmute are safe no-ops."""

    def test_double_mute_is_idempotent(self, ensure_dj_mode, api_post, api_get):
        """Muting twice returns ok with 'already muted' detail."""
        # First mute
        s1, b1 = api_post("/api/v1/audio/mute")
        assert s1 == 200 and b1.get("ok"), f"First mute failed: {b1}"

        # Second mute — should succeed with "already muted"
        s2, b2 = api_post("/api/v1/audio/mute")
        assert s2 == 200, f"Double mute failed: {s2} {b2}"
        assert b2.get("ok") is True
        assert "already" in b2.get("detail", "").lower(), (
            f"Expected 'already muted' detail, got: {b2}"
        )

        # Status should still show muted
        _, status_body = api_get("/api/v1/audio/mute-status")
        assert status_body.get("is_muted") is True

        # Cleanup
        api_post("/api/v1/audio/unmute")
        time.sleep(0.5)


class TestMuteStatusEndpoint:
    """GET /api/v1/audio/mute-status reflects correct state."""

    def test_initial_not_muted(self, api_post, api_get):
        """After unmute, status shows not muted."""
        # Ensure clean state — prior tests may have left system muted
        api_post("/api/v1/audio/unmute")
        time.sleep(0.5)

        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is False, f"Expected not muted: {body}"

    def test_status_after_mute(self, ensure_dj_mode, api_post, api_get):
        """After mute, status shows muted."""
        api_post("/api/v1/audio/mute")
        time.sleep(0.5)

        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is True, f"Expected muted: {body}"

        # Cleanup
        api_post("/api/v1/audio/unmute")
        time.sleep(0.5)

    def test_status_after_unmute(self, ensure_dj_mode, api_post, api_get):
        """After mute then unmute, status shows not muted."""
        api_post("/api/v1/audio/mute")
        time.sleep(0.5)
        api_post("/api/v1/audio/unmute")
        time.sleep(0.5)

        status, body = api_get("/api/v1/audio/mute-status")
        assert status == 200
        assert body.get("is_muted") is False, f"Expected not muted: {body}"
