"""F-320 D: a watchdog unlatch writes no gain, and the gate stays closed.

The watchdog is tripped for real: a monitored node is removed from the
local-demo PipeWire graph, so GM's registry listener latches the safety
mute (no test-only trip RPC, QE f79c7a5a).  Every gain value is read back
from PipeWire (pw-cli enum-params on pi4audio-convolver), never from GM or
web-ui state.

L1 (QE f79c7a5a, AE 1e8c1fb3 NB1/NB2): remove pi4audio-convolver-out,
    wait for the latch, check open_gate is refused, unlatch, then all 16
    gain values (8 x Mult, 8 x Add) print exactly "Float 0.000000" (strict
    string match, see ZERO_LINE), get_gate is closed and
    the watchdog is not latched.  A relatch (watchdog_mute event) between
    the unlatch and the read-back is a FAIL, because its mute would hide
    what the unlatch wrote (QE ae15808b Q1).
    No hw-out claim: with -out gone there is no path to hw-out.
    L1 then restores the convolver (as in L2) for the next test.
L2: remove both convolver nodes, recreate them in a separate PipeWire
    client (``pipewire -c filter-chain.conf`` with the stack's convolver
    config), so PipeWire and GM keep running and the latch survives.  With
    the tone playing: unlatch (same relatch guard), check the tone ->
    convolver and convolver-out -> hw-out links exist, then hw-out stays at
    the floor for 2 s and
    all 16 values still print 0.000000.  Positive control: Close Gate -> Open Gate (the
    only way back, AE 55f1a1b2 cond 2) brings the tone to hw-out.

Red at base ff55d0c8 by construction: unlatch writes the watchdog's
hardcoded 0.001 / 0.000631 Mult table, and open_gate writes the venue
gains while latched.

These tests break the stack they run on.  scripts/test-e2e.sh runs them in
their own step on a fresh stack (with --destructive) and stops it after.
"""

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from fixtures.backend import (  # noqa: F401
    BACKEND_TYPE,
    GM_PORT,
    LEVEL_FLOOR_DB,
    STIMULUS_HW_OUT_CHANNELS,
    VENUE,
    _pw_dump,
    _rpc_call,
    max_peak,
    read_live_levels,
    tone_on_sw_tap,
    virtual_stack_refusal,
    wait_for_peaks,
)


pytestmark = [pytest.mark.service_integration, pytest.mark.destructive,
              pytest.mark.needs_pw]

CONVOLVER = "pi4audio-convolver"
CONVOLVER_OUT = "pi4audio-convolver-out"
GAIN_NAMES = (
    "gain_left_hp", "gain_right_hp", "gain_sub1_lp", "gain_sub2_lp",
    "gain_hp_l", "gain_hp_r", "gain_iem_l", "gain_iem_r",
)
GAIN_KEYS = tuple(f"{n}:{p}" for n in GAIN_NAMES for p in ("Mult", "Add"))

LATCH_TIMEOUT_S = 5.0
NODES_TIMEOUT_S = 10.0
FLOOR_HOLD_S = 2.0
OPEN_TIMEOUT_S = 5.0
ABOVE_FLOOR_DB = 40.0
# routing.rs MIXXX_PREFIX / USBSTREAMER_OUT_PREFIX; local-demo names its
# virtual nodes after the real devices.
TONE_NODE_PREFIX = "Mixxx"
HW_OUT_PREFIX = "alsa_output.usb-MiniDSP_USBStreamer"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gm(cmd: str, **fields) -> dict:
    return _rpc_call("127.0.0.1", GM_PORT, {"cmd": cmd, **fields})


def _watchdog() -> dict:
    resp = _gm("watchdog_status")
    if not resp.get("ok"):
        pytest.fail(f"watchdog_status failed: {resp}", pytrace=False)
    return resp["watchdog"]


def _gate_open() -> bool:
    resp = _gm("get_gate")
    if not resp.get("ok"):
        pytest.fail(f"get_gate failed: {resp}", pytrace=False)
    return resp["gate_open"]


def _node_ids(name: str) -> list[int]:
    return [obj["id"] for obj in _pw_dump()
            if obj.get("type") == "PipeWire:Interface:Node"
            and ((obj.get("info") or {}).get("props") or {}).get("node.name") == name]


def _wait(predicate, timeout: float):
    """Poll predicate() until it returns a truthy value or timeout; return it."""
    deadline = time.monotonic() + timeout
    while True:
        value = predicate()
        if value or time.monotonic() >= deadline:
            return value
        time.sleep(0.1)


def _read_gains() -> dict[str, str]:
    """Read all 16 gain values (Mult and Add) from the live convolver node.

    Source is ``pw-cli enum-params <id> Props``, never pw-dump, which prints
    NaN, -Inf and subnormals as 0.000000 (F-349; AE 70541687 C1).  Returns
    the raw stripped value line per param, unparsed; FAIL unless exactly the
    16 expected gain_* params are found, each once.
    """
    ids = _node_ids(CONVOLVER)
    if len(ids) != 1:
        pytest.fail(f"expected one {CONVOLVER} node, found {ids}", pytrace=False)
    out = subprocess.run(["pw-cli", "enum-params", str(ids[0]), "Props"],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        pytest.fail(f"pw-cli enum-params {ids[0]} failed: {out.stderr}", pytrace=False)
    values: dict[str, str] = {}
    duplicates = []
    pending = None
    for line in out.stdout.splitlines():
        key = re.search(r'String\s+"(gain_\w+:(?:Mult|Add))"', line)
        if key:
            pending = key.group(1)
            continue
        if pending:
            if pending in values:
                duplicates.append(pending)
            values[pending] = line.strip()
        pending = None
    if duplicates or set(values) != set(GAIN_KEYS):
        pytest.fail(
            f"gain params read back are not exactly the 16 expected: "
            f"missing={sorted(set(GAIN_KEYS) - set(values))} "
            f"extra={sorted(set(values) - set(GAIN_KEYS))} duplicates={duplicates} "
            f"read={values}", pytrace=False)
    return {k: values[k] for k in GAIN_KEYS}


# Strict string match, never parsed to float: nan, inf and -0.000000 all
# FAIL.  At pw-cli's %f resolution this means |v| < 5e-7, about -126 dB
# (AE 70541687 C2/C3).
ZERO_LINE = "Float 0.000000"


def _not_zero(gains: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in gains.items() if v != ZERO_LINE}


def _assert_all_zero(when: str) -> None:
    gains = _read_gains()
    bad = _not_zero(gains)
    assert not bad, f"{when}: gain values not {ZERO_LINE!r} (raw lines): {bad}"


def _destroy_nodes(name: str) -> list[int]:
    ids = _node_ids(name)
    for node_id in ids:
        out = subprocess.run(["pw-cli", "destroy", str(node_id)],
                             capture_output=True, text=True, timeout=5)
        assert out.returncode == 0, f"pw-cli destroy {node_id} ({name}) failed: {out.stderr}"
    return ids


def _wait_latched(missing: str) -> dict:
    status = _wait(lambda: (wd := _watchdog())["latched"] and wd, LATCH_TIMEOUT_S)
    assert status, (
        f"watchdog not latched {LATCH_TIMEOUT_S} s after removing {missing}: "
        f"{_watchdog()}")
    print(f"F-320D latched status: {json.dumps(status)}")
    assert missing in status["missing_nodes"], status
    return status


class _GmWindow:
    """One GM connection kept open for a test window; records every push event.

    GM broadcasts events to every connected client, so a connection opened
    before an action sees all events up to the moment it is drained.
    """

    def __init__(self):
        self._sock = socket.create_connection(("127.0.0.1", GM_PORT), timeout=5)
        self._buf = b""
        self.events: list[dict] = []

    def __enter__(self):
        # The reply proves GM is serving this connection (and so broadcasting
        # to it) before the window's first action.
        assert self.call("get_gate").get("ok"), "GM event window: get_gate failed"
        return self

    def __exit__(self, *exc):
        self._sock.close()

    def _lines(self, timeout: float):
        """Yield decoded lines until timeout passes with nothing to read."""
        while True:
            while b"\n" in self._buf:
                line, self._buf = self._buf.split(b"\n", 1)
                if line.strip():
                    yield json.loads(line)
            self._sock.settimeout(timeout)
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                return
            if not chunk:
                return
            self._buf += chunk

    def call(self, cmd: str) -> dict:
        """Send one command on this connection and return its reply ({} on timeout)."""
        self._sock.sendall((json.dumps({"cmd": cmd}) + "\n").encode())
        for msg in self._lines(timeout=5.0):
            if msg.get("type") == "event":
                self.events.append(msg)
            elif msg.get("cmd", cmd) == cmd:
                return msg
        return {}

    def drain(self, quiet_s: float = 0.5) -> None:
        for msg in self._lines(timeout=quiet_s):
            if msg.get("type") == "event":
                self.events.append(msg)


def _unlatch_and_read_back(when: str) -> None:
    """Unlatch, then check gains, gate and latch with no relatch in between.

    A relatch re-runs the safety mute (every Mult = 0.0) and so would hide
    whatever the unlatch wrote (QE ae15808b Q1).  The event connection stays
    open from before the unlatch until after the read-back; any
    watchdog_mute in that window is a FAIL.
    """
    with _GmWindow() as gm:
        reply = gm.call("watchdog_unlatch")
        gains = _read_gains()
        gate = gm.call("get_gate")
        status = gm.call("watchdog_status")
        gm.drain()
    print(f"F-320D {when}: unlatch reply={reply} events={gm.events}")
    print(f"F-320D {when}: status={json.dumps(status.get('watchdog'))} gains={gains}")
    assert reply.get("ok") is True, f"watchdog_unlatch failed: {reply}"
    mutes = [e for e in gm.events if e.get("event") == "watchdog_mute"]
    assert not mutes, (
        f"relatched before read-back: unlatch read-back not discriminating: {mutes}")
    # F-320 D: the event carries no gains (Architect a9ec4ed5).
    for event in gm.events:
        if event.get("event") == "watchdog_unlatched":
            assert event == {"type": "event", "event": "watchdog_unlatched"}, event
    bad = _not_zero(gains)
    assert not bad, f"{when}: gain values not {ZERO_LINE!r} (raw lines): {bad}"
    assert gate.get("ok") and gate.get("gate_open") is False, f"{when}: gate not closed: {gate}"
    assert status.get("ok") and status["watchdog"]["latched"] is False, (
        f"{when}: still latched after unlatch: {status}")


def _links(out_match, in_match) -> list[str]:
    """Links whose output node matches out_match and input node in_match, as text."""
    objs = _pw_dump()
    names = {o["id"]: ((o.get("info") or {}).get("props") or {}).get("node.name", "")
             for o in objs if o.get("type") == "PipeWire:Interface:Node"}
    found = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        info = o.get("info") or {}
        out_name = names.get(info.get("output-node-id"), "")
        in_name = names.get(info.get("input-node-id"), "")
        if out_match(out_name) and in_match(in_name):
            found.append(f"{out_name}:{info.get('output-port-id')} -> "
                         f"{in_name}:{info.get('input-port-id')}")
    return found


def _path_links() -> tuple[list[str], list[str]]:
    """The tone -> convolver and convolver-out -> hw-out links (DJ mode, routing.rs)."""
    tone_in = _links(lambda n: n.startswith(TONE_NODE_PREFIX), lambda n: n == CONVOLVER)
    hw_out = _links(lambda n: n == CONVOLVER_OUT, lambda n: n.startswith(HW_OUT_PREFIX))
    return tone_in, hw_out


def _assert_open_gate_refused(when: str) -> None:
    resp = _gm("open_gate")
    assert resp.get("ok") is False and str(resp.get("error", "")).startswith(
        "watchdog latched"), f"{when}: open_gate not refused: {resp}"
    assert _gate_open() is False, f"{when}: gate open after a refused open_gate"
    _assert_all_zero(f"{when}, after the refused open_gate")


def _load_venue() -> None:
    """Load venue gains, so open_gate would really write them if allowed."""
    resp = _gm("set_venue", venue=VENUE)
    assert resp.get("ok"), f"set_venue {VENUE} failed: {resp}"


@pytest.fixture(scope="module", autouse=True)
def _virtual_stack_only():
    refusal = virtual_stack_refusal(BACKEND_TYPE, _pw_dump())
    if refusal:
        pytest.fail(f"Refusing to remove PipeWire nodes: {refusal}", pytrace=False)


@pytest.fixture()
def armed_closed():
    """Precondition: watchdog armed and not latched, gate closed, gains 0."""
    status = _wait(lambda: (wd := _watchdog()).get("armed") and not wd["latched"] and wd,
                   NODES_TIMEOUT_S)
    assert status, f"watchdog not armed and unlatched: {_watchdog()}"
    if _gate_open():
        assert _gm("close_gate").get("ok")
    _assert_all_zero("precondition")
    _load_venue()
    yield
    _gm("close_gate")


@pytest.fixture(scope="module")
def recreate_convolver():
    """Return a function that recreates both convolver nodes in a new client.

    It first removes any convolver node left over, then loads the stack's
    own convolver config in a separate ``pipewire -c filter-chain.conf``
    process, so the stack's PipeWire daemon and GM keep running.  Each call
    stops the previous process first; the last one is stopped on module
    teardown.
    """
    conf = Path(os.environ["PI4AUDIO_PW_CONF_DIR"]) / "30-convolver.conf"
    assert conf.is_file(), f"stack convolver config missing: {conf}"
    tmp = Path(tempfile.mkdtemp(prefix="f320d-filter-chain-"))
    (tmp / "pipewire" / "filter-chain.conf.d").mkdir(parents=True)
    shutil.copy(conf, tmp / "pipewire" / "filter-chain.conf.d" / "30-convolver.conf")
    procs: list[subprocess.Popen] = []

    def start() -> None:
        _stop(procs)
        _destroy_nodes(CONVOLVER_OUT)
        _destroy_nodes(CONVOLVER)
        assert _wait(lambda: not _node_ids(CONVOLVER) and not _node_ids(CONVOLVER_OUT),
                     NODES_TIMEOUT_S), "old convolver nodes still in the graph"
        log = open(tmp / "filter-chain.log", "w")
        procs.append(subprocess.Popen(
            ["pipewire", "-c", "filter-chain.conf"],
            env={**os.environ, "XDG_CONFIG_HOME": str(tmp)},
            stdout=log, stderr=subprocess.STDOUT))
        present = _wait(lambda: len(_node_ids(CONVOLVER)) == 1
                        and len(_node_ids(CONVOLVER_OUT)) == 1, NODES_TIMEOUT_S)
        assert present, (
            f"convolver not recreated within {NODES_TIMEOUT_S} s: "
            f"{CONVOLVER}={_node_ids(CONVOLVER)} {CONVOLVER_OUT}={_node_ids(CONVOLVER_OUT)} "
            f"exit={procs[-1].poll()} log={(tmp / 'filter-chain.log').read_text()[-2000:]}")
        print(f"F-320D recreated convolver nodes via: pipewire -c filter-chain.conf "
              f"(pid {procs[-1].pid}, config {conf})")

    yield start
    _stop(procs)
    shutil.rmtree(tmp, ignore_errors=True)


def _stop(procs: list[subprocess.Popen]) -> None:
    while procs:
        proc = procs.pop()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def _restore_convolver(recreate) -> None:
    """Recreate the convolver and clear the latch, for the next test."""
    recreate()
    if _watchdog()["latched"]:
        assert _gm("watchdog_unlatch").get("ok"), "unlatch after restore failed"
    _gm("close_gate")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUnlatchWritesNoGain:

    def test_l1_unlatch_leaves_gains_zero_and_gate_closed(self, armed_closed,
                                                          recreate_convolver):
        try:
            removed = _destroy_nodes(CONVOLVER_OUT)
            assert removed, f"{CONVOLVER_OUT} not in the graph"
            print(f"F-320D removed {CONVOLVER_OUT} via: pw-cli destroy {removed}")
            assert _wait(lambda: not _node_ids(CONVOLVER_OUT), LATCH_TIMEOUT_S), (
                f"{CONVOLVER_OUT} still in the graph after pw-cli destroy")
            _wait_latched(CONVOLVER_OUT)
            # The gains live on the capture node; it must survive for the read-back.
            assert len(_node_ids(CONVOLVER)) == 1, (
                f"{CONVOLVER} gone after removing {CONVOLVER_OUT}; cannot read back gains")

            _assert_open_gate_refused("latched")

            _unlatch_and_read_back("L1")
        finally:
            _restore_convolver(recreate_convolver)

    def test_l2_hw_out_at_floor_after_unlatch(self, armed_closed, tone_on_sw_tap,
                                             level_hw_out_port, recreate_convolver):
        removed = _destroy_nodes(CONVOLVER_OUT) + _destroy_nodes(CONVOLVER)
        print(f"F-320D removed both convolver nodes via: pw-cli destroy {removed}")
        assert _wait(lambda: not _node_ids(CONVOLVER) and not _node_ids(CONVOLVER_OUT),
                     LATCH_TIMEOUT_S), "convolver nodes still in the graph"
        _wait_latched(CONVOLVER_OUT)

        recreate_convolver()
        assert _watchdog()["latched"], "latch lost when the convolver came back"
        _assert_open_gate_refused("latched, convolver recreated")

        _unlatch_and_read_back("L2")

        # The floor hold only discriminates if the path is live: without
        # these links hw-out would be silent at base too (QE ae15808b Q3).
        tone_in, hw_out = _wait(lambda: all(links := _path_links()) and links,
                                NODES_TIMEOUT_S) or _path_links()
        print(f"F-320D path links: tone->convolver={tone_in} convolver-out->hw-out={hw_out}")
        assert tone_in and hw_out, (
            f"signal path not linked before the floor hold: "
            f"tone->convolver={tone_in} convolver-out->hw-out={hw_out}")

        deadline = time.monotonic() + FLOOR_HOLD_S
        while time.monotonic() < deadline:
            peaks = max_peak(read_live_levels(level_hw_out_port, count=3),
                             STIMULUS_HW_OUT_CHANNELS)
            assert max(peaks) <= LEVEL_FLOOR_DB, (
                f"hw-out above the floor after unlatch with the tone playing: {peaks}")
        _assert_all_zero("after the hw-out floor hold")

        # Positive control: Close Gate -> Open Gate is the way back, and the
        # tone reaches hw-out then, so the floor reading above was not vacuous.
        assert _gm("close_gate").get("ok")
        resp = _gm("open_gate")
        assert resp.get("ok"), f"open_gate after unlatch failed: {resp}"
        peaks = wait_for_peaks(level_hw_out_port, STIMULUS_HW_OUT_CHANNELS,
                               lambda p: min(p) >= LEVEL_FLOOR_DB + ABOVE_FLOOR_DB,
                               timeout=OPEN_TIMEOUT_S)
        assert min(peaks) >= LEVEL_FLOOR_DB + ABOVE_FLOOR_DB, (
            f"positive control: no tone on hw-out after Close Gate -> Open Gate: {peaks}")
