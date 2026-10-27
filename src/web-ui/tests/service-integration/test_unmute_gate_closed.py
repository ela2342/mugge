"""F-439: unmute must fail closed while the D-063 gate is closed.

Before the fix, unmute restored the web-ui pre-mute snapshot with no gate
check, so venue gain came back on the outputs while the GraphManager
reported the gate CLOSED (AE ruling 455e0190, F1-F3).

Both orders from F3 run against the real local-demo stack:
    (a) gate open -> gate close -> mute -> unmute
    (b) gate open -> mute -> gate close -> unmute
After the unmute, each test asserts:
    - the gate is still reported closed and the mute state is cleared (F1),
    - all 8 gain Mult params read back 0 from PipeWire,
    - level-bridge-hw-out (downstream of the gains) is at the floor.

The gate is opened through virtual_gate_open, unchanged, so the tone is
proven on hw-out before the close; a floor reading after the unmute then
cannot come from a dead tap or a missing stimulus.

Prerequisites:
    - ``nix run .#test-e2e`` (starts local-demo with the --tone stimulus)
"""

import re
import subprocess

import pytest

from fixtures.backend import (  # noqa: F401
    HW_OUT_TONE_WINDOW_DB,
    LEVEL_FLOOR_DB,
    STIMULUS_HW_OUT_CHANNELS,
    _gate_state,
    _pw_dump,
    in_window,
    tone_channels,
    tone_on_sw_tap,
    virtual_gate_open,
    wait_for_peaks,
)


pytestmark = pytest.mark.service_integration

CONVOLVER_NODE_NAME = "pi4audio-convolver"
GAIN_NAMES = (
    "gain_left_hp", "gain_right_hp", "gain_sub1_lp", "gain_sub2_lp",
    "gain_hp_l", "gain_hp_r", "gain_iem_l", "gain_iem_r",
)
FLOOR_TIMEOUT_S = 2.0


def _convolver_id() -> int:
    for obj in _pw_dump():
        props = (obj.get("info") or {}).get("props") or {}
        if props.get("node.name") == CONVOLVER_NODE_NAME:
            return obj["id"]
    pytest.fail(f"{CONVOLVER_NODE_NAME} not in pw-dump", pytrace=False)


def read_back_mults() -> dict[str, float]:
    """Read every <gain>:Mult from PipeWire; FAIL if any of the 8 is missing.

    Reads the live Props via pw-cli enum-params, never the web-ui state.
    """
    node_id = _convolver_id()
    out = subprocess.run(["pw-cli", "enum-params", str(node_id), "Props"],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        pytest.fail(f"pw-cli enum-params {node_id} failed: {out.stderr}",
                    pytrace=False)
    mults: dict[str, float] = {}
    pending = None
    for line in out.stdout.splitlines():
        key = re.search(r'String\s+"(\w+):Mult"', line)
        if key:
            pending = key.group(1)
            continue
        value = re.search(r"Float\s+([\d.eE+-]+)", line)
        if pending and value:
            mults[pending] = float(value.group(1))
        pending = None
    missing = [name for name in GAIN_NAMES if name not in mults]
    if missing:
        pytest.fail(f"Mult not read back for {missing}: {mults}", pytrace=False)
    return {name: mults[name] for name in GAIN_NAMES}


def _post_ok(api_post, path: str) -> dict:
    status, body = api_post(path)
    assert status == 200 and body.get("ok"), f"{path} failed: {status} {body}"
    return body


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
    """After unmute behind a closed gate: gate closed, unmuted, all 0, floor."""
    gate = _gate_state(base_url)
    assert gate.get("gate_open") is False, f"gate not reported closed: {gate}"
    _, mute = api_get("/api/v1/audio/mute-status")
    assert mute.get("is_muted") is False, (
        f"unmute behind a closed gate must clear the mute state: {mute}")
    mults = read_back_mults()
    live = {name: m for name, m in mults.items() if m != 0.0}
    assert not live, f"non-zero Mult behind a closed gate after unmute: {live}"
    _assert_hw_out_floor(port, "after unmute with the gate closed")


class TestUnmuteBehindClosedGate:
    """F-439 F3: unmute with the gate closed leaves every gain at 0."""

    def test_close_then_mute_then_unmute(self, virtual_gate_open, base_url,
                                         api_get, api_post, level_hw_out_port):
        """(a) gate close -> mute -> unmute: nothing is restored."""
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)

        _post_ok(api_post, "/api/v1/venue/gate/close")
        _assert_hw_out_floor(level_hw_out_port, "after gate close")
        _post_ok(api_post, "/api/v1/audio/mute")
        _post_ok(api_post, "/api/v1/audio/unmute")

        _assert_fail_closed(base_url, api_get, level_hw_out_port)

    def test_mute_then_close_then_unmute(self, virtual_gate_open, base_url,
                                         api_get, api_post, level_hw_out_port):
        """(b) mute -> gate close -> unmute: the snapshot is not restored."""
        _assert_tone_on_hw_out(level_hw_out_port, virtual_gate_open)

        _post_ok(api_post, "/api/v1/audio/mute")
        _assert_hw_out_floor(level_hw_out_port, "after mute")
        _post_ok(api_post, "/api/v1/venue/gate/close")
        _post_ok(api_post, "/api/v1/audio/unmute")

        _assert_fail_closed(base_url, api_get, level_hw_out_port)
