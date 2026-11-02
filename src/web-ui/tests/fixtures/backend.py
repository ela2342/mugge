"""Shared backend fixtures for service-integration and E2E tests.

These fixtures provide access to the local-demo stack's backend services
(GraphManager RPC, level-bridge TCP, pcm-bridge binary, web UI HTTP API)
without requiring a browser.  Both tests/service-integration/ and tests/e2e/
import from here.

The local-demo stack must be running before these fixtures are used.
The test-e2e.sh wrapper handles stack lifecycle.
"""

import functools
import importlib.util
import json
import os
import re
import socket
import struct
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

LOCAL_DEMO_URL = os.environ.get("LOCAL_DEMO_URL", "http://localhost:8080")
STACK_TIMEOUT = int(os.environ.get("E2E_STACK_TIMEOUT", "30"))
BACKEND_TYPE = os.environ.get("PI_AUDIO_BACKEND", "local-demo")

GM_PORT = int(os.environ.get("GM_PORT", "4002"))
SIGGEN_PORT = int(os.environ.get("SIGGEN_PORT", "4001"))
LEVEL_SW_PORT = int(os.environ.get("LEVEL_SW_PORT", "9100"))
LEVEL_HW_OUT_PORT = int(os.environ.get("LEVEL_HW_OUT_PORT", "9101"))
PCM_PORT = int(os.environ.get("PCM_PORT", "9090"))


# ---------------------------------------------------------------------------
# Stack reachability helpers
# ---------------------------------------------------------------------------

def is_reachable(url: str, timeout: float = 2.0) -> bool:
    """Check if the web UI responds to a simple GET."""
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except (urllib.error.URLError, OSError):
        return False


def wait_for_stack(url: str, timeout: int) -> bool:
    """Wait until the web UI is reachable or timeout expires."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_reachable(url):
            return True
        time.sleep(1)
    return False


def check_pw_available() -> bool:
    """Check if PipeWire is running (pw-cli info succeeds)."""
    try:
        result = subprocess.run(
            ["pw-cli", "info", "0"],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ---------------------------------------------------------------------------
# Marker registration and collection hooks
# ---------------------------------------------------------------------------

def register_markers(config):
    """Register custom markers shared by service-integration and E2E tiers."""
    config.addinivalue_line("markers", "e2e: real-stack end-to-end test")
    config.addinivalue_line("markers", "service_integration: real-stack service test (no browser)")
    config.addinivalue_line("markers", "destructive: tests that modify Pi state")
    config.addinivalue_line("markers", "slow: tests exceeding 10 s")
    config.addinivalue_line("markers", "needs_usb_audio: requires USB audio device (UMIK-1 loopback)")
    config.addinivalue_line("markers", "needs_pw: requires PipeWire running")
    config.addinivalue_line("markers", "needs_acoustic: requires physical speakers (owner-confirmed)")
    config.addinivalue_line("markers", "audio_producing: produces audio output (owner-confirmed)")


def add_backend_options(parser):
    """Add CLI options shared by service-integration and E2E tiers."""
    parser.addoption(
        "--destructive",
        action="store_true",
        default=False,
        help="Allow tests marked @pytest.mark.destructive",
    )
    parser.addoption(
        "--loopback-confirmed",
        action="store_true",
        default=False,
        help="Attest that physical loopback cables are connected (pi-loopback tier)",
    )
    parser.addoption(
        "--owner-confirmed",
        action="store_true",
        default=False,
        help="Attest that speakers are safe (pi-full tier)",
    )


def apply_backend_skips(config, items):
    """Skip tests based on available infrastructure and CLI flags."""
    pw_available = check_pw_available()
    owner_confirmed = config.getoption("--owner-confirmed", default=False)

    # Skip all tests if the local-demo stack is not reachable
    if not is_reachable(LOCAL_DEMO_URL):
        if not wait_for_stack(LOCAL_DEMO_URL, STACK_TIMEOUT):
            skip = pytest.mark.skip(
                reason=f"local-demo stack not reachable at {LOCAL_DEMO_URL}"
            )
            for item in items:
                item.add_marker(skip)
            return

    # Skip destructive tests unless --destructive is passed
    if not config.getoption("--destructive", default=False):
        skip_destructive = pytest.mark.skip(reason="requires --destructive flag")
        for item in items:
            if "destructive" in item.keywords:
                item.add_marker(skip_destructive)

    # Tier-based skipping
    for item in items:
        if "needs_pw" in item.keywords and not pw_available:
            item.add_marker(pytest.mark.skip(reason="No PipeWire available"))
        if "needs_usb_audio" in item.keywords:
            if BACKEND_TYPE not in ("pi-loopback", "pi-full"):
                item.add_marker(pytest.mark.skip(reason="No USB audio device"))
        if "needs_acoustic" in item.keywords and not owner_confirmed:
            item.add_marker(pytest.mark.skip(reason="Requires --owner-confirmed"))
        if "audio_producing" in item.keywords and not owner_confirmed:
            item.add_marker(pytest.mark.skip(reason="audio_producing requires --owner-confirmed"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def backend_type() -> str:
    """Return the current backend tier."""
    return BACKEND_TYPE


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL of the running local-demo web UI."""
    return LOCAL_DEMO_URL


@pytest.fixture(scope="session")
def local_demo_url() -> str:
    """Alias for base_url — used by some test files."""
    return LOCAL_DEMO_URL


@pytest.fixture(scope="session")
def gm_port() -> int:
    """GraphManager RPC port."""
    return GM_PORT


@pytest.fixture(scope="session")
def siggen_port() -> int:
    """signal-gen RPC port."""
    return SIGGEN_PORT


@pytest.fixture(scope="session")
def level_sw_port() -> int:
    """level-bridge-sw TCP port."""
    return LEVEL_SW_PORT


@pytest.fixture(scope="session")
def level_hw_out_port() -> int:
    """level-bridge-hw-out TCP port."""
    return LEVEL_HW_OUT_PORT


@pytest.fixture(scope="session")
def pcm_port() -> int:
    """pcm-bridge TCP port."""
    return PCM_PORT


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _api_get(base_url: str, path: str, timeout: float = 10.0):
    """GET a JSON endpoint and return (status_code, parsed_body)."""
    try:
        resp = urllib.request.urlopen(f"{base_url}{path}", timeout=timeout)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return exc.code, json.loads(body) if body else {}


def _api_post(base_url: str, path: str, body: dict | None = None, timeout: float = 10.0):
    """POST to a JSON endpoint, return (status_code, parsed_body)."""
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return exc.code, json.loads(body) if body else {}


@pytest.fixture(scope="session")
def api_get(base_url):
    """Fixture returning a GET helper bound to the live server."""
    def _get(path: str, timeout: float = 10.0):
        return _api_get(base_url, path, timeout)
    return _get


@pytest.fixture(scope="session")
def api_post(base_url):
    """Fixture returning a POST helper bound to the live server."""
    def _post(path: str, body: dict | None = None, timeout: float = 10.0):
        return _api_post(base_url, path, body, timeout)
    return _post


# ---------------------------------------------------------------------------
# TCP RPC helper (GraphManager, signal-gen)
# ---------------------------------------------------------------------------

def _rpc_call(host: str, port: int, cmd: dict, timeout: float = 5.0) -> dict:
    """Send a JSON RPC command over TCP and return the parsed response.

    The GM socket also carries push events (``{"type": "event", ...}``
    lines, e.g. link_created during a mode switch) interleaved with the
    reply. Event lines are skipped; the first non-event line whose ``cmd``
    matches (or has no ``cmd``) is the response (F-394 AC ii). Returns {}
    on connection errors, bad JSON or no response before the deadline.
    """
    deadline = time.monotonic() + timeout
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall((json.dumps(cmd) + "\n").encode())
            buf = b""
            while True:
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    msg = json.loads(line.decode())
                    if msg.get("type") == "event":
                        continue
                    if msg.get("cmd", cmd.get("cmd")) != cmd.get("cmd"):
                        continue
                    return msg
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return {}
                s.settimeout(remaining)
                chunk = s.recv(4096)
                if not chunk:
                    return {}
                buf += chunk
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


@pytest.fixture(scope="session")
def rpc_call():
    """Fixture returning a TCP RPC helper."""
    return _rpc_call


# ---------------------------------------------------------------------------
# Level-bridge TCP helper
# ---------------------------------------------------------------------------

def _read_levels(port: int, count: int = 1, timeout: float = 5.0) -> list[dict]:
    """Read JSON lines from a level-bridge TCP port."""
    results = []
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        s.settimeout(timeout)
        buf = b""
        while len(results) < count:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if line:
                    results.append(json.loads(line.decode()))
        s.close()
    except (OSError, json.JSONDecodeError):
        pass
    return results


@pytest.fixture(scope="session")
def read_levels():
    """Fixture returning a level-bridge TCP reader."""
    return _read_levels


# ---------------------------------------------------------------------------
# pcm-bridge binary reader
# ---------------------------------------------------------------------------

def _read_pcm_header(port: int, timeout: float = 5.0) -> dict | None:
    """Read one v2 binary frame header from pcm-bridge."""
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        s.settimeout(timeout)
    except OSError:
        return None

    for _ in range(10):
        buf = b""
        while len(buf) < 24:
            try:
                chunk = s.recv(24 - len(buf))
            except socket.timeout:
                break
            if not chunk:
                break
            buf += chunk

        if len(buf) < 24:
            continue

        version = buf[0]
        frame_count = struct.unpack_from("<I", buf, 4)[0]
        graph_pos = struct.unpack_from("<Q", buf, 8)[0]
        graph_nsec = struct.unpack_from("<Q", buf, 16)[0]

        # Drain the payload
        if frame_count > 0:
            payload_size = frame_count * 4 * 4  # 4 channels, float32
            remaining = payload_size
            while remaining > 0:
                try:
                    chunk = s.recv(min(remaining, 4096))
                except socket.timeout:
                    break
                if not chunk:
                    break
                remaining -= len(chunk)

        if frame_count > 0:
            s.close()
            return {
                "version": version,
                "frame_count": frame_count,
                "graph_pos": graph_pos,
                "graph_nsec": graph_nsec,
            }

    s.close()
    return None


@pytest.fixture(scope="session")
def read_pcm_header():
    """Fixture returning a pcm-bridge binary header reader."""
    return _read_pcm_header


# ---------------------------------------------------------------------------
# GM mode switching helper
# ---------------------------------------------------------------------------

def _switch_gm_mode_detail(mode: str, gm_port: int = GM_PORT,
                           timeout: float = 5.0) -> tuple[bool, dict]:
    """Switch GraphManager to the given mode via RPC and wait for reconciliation.

    Returns (ok, detail). detail holds the raw set_mode and await_settled
    replies ({} if the RPC call itself failed), so a failure can say why.
    """
    resp = _rpc_call("127.0.0.1", gm_port, {"cmd": "set_mode", "mode": mode}, timeout)
    detail = {"set_mode": resp}
    if not resp.get("ok"):
        return False, detail
    epoch = resp.get("epoch", 0)
    settled = _rpc_call("127.0.0.1", gm_port, {
        "cmd": "await_settled",
        "since_epoch": epoch,
        "timeout_ms": 10000,
    }, timeout=max(timeout, 15.0))
    detail["await_settled"] = settled
    return settled.get("ok", False), detail


def _switch_gm_mode(mode: str, gm_port: int = GM_PORT, timeout: float = 5.0) -> bool:
    """Switch GraphManager to the given mode via RPC and wait for reconciliation."""
    return _switch_gm_mode_detail(mode, gm_port, timeout)[0]


def _dj_mode_diagnostics(gm_port: int) -> str:
    """Collect GM and PipeWire state for an ensure_dj_mode failure (F-394)."""
    parts = [f"get_links: {_rpc_call('127.0.0.1', gm_port, {'cmd': 'get_links'})}"]
    for cmd in (["pw-link", "-l"],
                ["pw-metadata", "-n", "settings", "0", "clock.force-quantum"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            text = (out.stdout + out.stderr).strip()
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            text = repr(exc)
        parts.append(f"$ {' '.join(cmd)}\n{text}")
    return "\n".join(parts)


def _gm_mode(gm_port: int) -> str | None:
    """Return the mode the GM reports via get_state, or None if unreadable."""
    return _rpc_call("127.0.0.1", gm_port, {"cmd": "get_state"}).get("mode")


@pytest.fixture()
def ensure_dj_mode(gm_port):
    """Put the GM in DJ mode for one test, and back to standby afterwards.

    Tests that need the DJ signal path require the GM to be in DJ mode,
    so that the Mixxx -> convolver -> USBStreamer links exist (signal-gen
    is not linked in DJ mode).

    F-394: a failed switch is a FAIL, not a skip. DJ mode is the
    prerequisite under test, so a skip would hide a broken DJ path.
    Function scope because other modules (test_measurement,
    test_production) switch modes between DJ tests. Every use runs
    set_mode + await_settled, since "mode is dj" alone does not mean the
    links have converged. The standby teardown is checked as well.
    """
    ok, detail = _switch_gm_mode_detail("dj", gm_port)
    if not ok:
        pytest.fail(
            f"Could not switch GM to DJ mode: {detail}\n"
            f"{_dj_mode_diagnostics(gm_port)}",
            pytrace=False,
        )
    mode = _gm_mode(gm_port)
    if mode != "dj":
        pytest.fail(
            f"GM settled but reports mode {mode!r}, expected 'dj': {detail}\n"
            f"{_dj_mode_diagnostics(gm_port)}",
            pytrace=False,
        )
    yield
    ok, detail = _switch_gm_mode_detail("standby", gm_port)
    if not ok:
        pytest.fail(
            f"Could not switch GM back to standby: {detail}\n"
            f"{_dj_mode_diagnostics(gm_port)}",
            pytrace=False,
        )


# ---------------------------------------------------------------------------
# D-063 gate in the virtual stack (F-394, AE ruling Q2)
# ---------------------------------------------------------------------------

# level-bridge reports -120.0 dBFS for silence (its clamp, level-bridge
# server.rs), so the floor is the clamp value, not "anything below -120".
LEVEL_FLOOR_DB = -120.0

# hw-out channels fed by a stimulus on Mixxx out 1-2 in DJ mode: mains
# L/R (1:1) and both subs (L+R sum), routing.rs dj_links.
STIMULUS_HW_OUT_CHANNELS = (0, 1, 2, 3)


def virtual_stack_refusal(backend: str, pw_objects) -> str | None:
    """Return why opening the gate is refused, or None if it is allowed.

    The gate may only be opened in the local-demo stack, and only when its
    PipeWire graph has no ALSA hardware behind it (AE Q2 C1). The check is
    on the factory/api properties, never on node names: local-demo names
    its virtual nodes after the real USBStreamer.
    """
    if backend != "local-demo":
        return f"PI_AUDIO_BACKEND is {backend!r}, not 'local-demo'"
    if not pw_objects:
        return "pw-dump returned no objects; cannot prove there is no hardware"
    for obj in pw_objects:
        props = (obj.get("info") or {}).get("props") or {}
        factory = str(props.get("factory.name", ""))
        if (props.get("device.api") == "alsa"
                or factory.startswith("api.alsa")
                or any(str(k).startswith("api.alsa.") for k in props)):
            name = props.get("node.name") or props.get("device.name") or obj.get("id")
            return f"ALSA hardware object in the graph: {name} ({factory or 'device.api=alsa'})"
    return None


def _pw_dump() -> list:
    """Return the pw-dump object list of the stack's PipeWire, or [] on error."""
    try:
        out = subprocess.run(["pw-dump"], capture_output=True, text=True, timeout=10)
        return json.loads(out.stdout) if out.returncode == 0 else []
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def read_live_levels(port: int, count: int = 5) -> list[dict]:
    """Read level snapshots and FAIL unless the tap is live.

    A dead tap and a silent tap both read -120.0, so a floor assert alone
    would pass on a dead tap. Live means: snapshots arrive and their
    graph position advances.
    """
    lines = _read_levels(port, count=count)
    positions = [snap.get("pos") for snap in lines]
    if len(lines) < 2 or len(set(positions)) < 2:
        pytest.fail(f"level tap on port {port} is not live: {lines}", pytrace=False)
    return lines


def max_peak(lines: list[dict], channels) -> list[float]:
    """Highest peak per channel over the snapshots; FAIL if a channel is missing."""
    result = []
    for ch in channels:
        try:
            result.append(max(snap["peak"][ch] for snap in lines))
        except (KeyError, IndexError, TypeError):
            pytest.fail(f"channel {ch} missing from level snapshots: {lines}",
                        pytrace=False)
    return result


def wait_for_peaks(port: int, channels, predicate, timeout: float) -> list[float]:
    """Poll a live tap until predicate(peaks) holds; return the last peaks.

    The caller asserts on the result, so a timeout reports the last reading.
    """
    deadline = time.monotonic() + timeout
    while True:
        peaks = max_peak(read_live_levels(port, count=3), channels)
        if predicate(peaks) or time.monotonic() >= deadline:
            return peaks
        time.sleep(0.1)


CONVOLVER_NODE_NAME = "pi4audio-convolver"
GAIN_NAMES = (
    "gain_left_hp", "gain_right_hp", "gain_sub1_lp", "gain_sub2_lp",
    "gain_hp_l", "gain_hp_r", "gain_iem_l", "gain_iem_r",
)


def _convolver_id() -> int:
    for obj in _pw_dump():
        props = (obj.get("info") or {}).get("props") or {}
        if props.get("node.name") == CONVOLVER_NODE_NAME:
            return obj["id"]
    pytest.fail(f"{CONVOLVER_NODE_NAME} not in pw-dump", pytrace=False)


GAIN_PARAMS = ("Mult", "Add")
GAIN_KEYS = tuple(f"{name}:{param}" for name in GAIN_NAMES for param in GAIN_PARAMS)
# pw-cli prints Props floats with %f: this line means |v| < 5e-7 (~-126 dB);
# nan, inf and -0.000000 do not match it (AE 70541687 C2/C3).
ZERO_LINE = "Float 0.000000"


def read_back_gains() -> dict[str, str]:
    """Read all 16 gain values (8 Mult, 8 Add) from PipeWire, unparsed.

    Values come from the live Props via pw-cli enum-params, never from
    pw-dump (F-349) or the web-ui state; pw-dump only finds the node id.
    Returns the raw value line per "<gain>:<param>" key.  FAIL, printing
    the raw line, unless the line after each key is a Float line; FAIL
    unless the keys are exactly GAIN_KEYS, each once (AE 1fb3da7c P2).
    """
    node_id = _convolver_id()
    out = subprocess.run(["pw-cli", "enum-params", str(node_id), "Props"],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        pytest.fail(f"pw-cli enum-params {node_id} failed: {out.stderr}",
                    pytrace=False)
    lines = out.stdout.splitlines()
    values: dict[str, str] = {}
    for i, line in enumerate(lines):
        key = re.search(r'String\s+"(gain_\w+:(?:Mult|Add))"', line)
        if not key:
            continue
        name = key.group(1)
        raw = lines[i + 1].strip() if i + 1 < len(lines) else None
        if raw is None or not raw.startswith("Float "):
            pytest.fail(f"{name}: value line is not a Float: {raw!r}", pytrace=False)
        if name in values:
            pytest.fail(f"{name} read back twice: {values[name]!r}, {raw!r}",
                        pytrace=False)
        values[name] = raw
    missing = [k for k in GAIN_KEYS if k not in values]
    extra = sorted(set(values) - set(GAIN_KEYS))
    if missing or extra:
        pytest.fail(f"gain values read back: missing {missing}, extra {extra}: "
                    f"{values}", pytrace=False)
    return {k: values[k] for k in GAIN_KEYS}


def nonzero_gains(values: dict[str, str], param: str | None = None) -> dict[str, str]:
    """The values whose line is not exactly ZERO_LINE, optionally one param."""
    return {k: v for k, v in values.items()
            if v != ZERO_LINE and (param is None or k.endswith(f":{param}"))}


def _gate_state(base_url: str) -> dict:
    status, body = _api_get(base_url, "/api/v1/venue/current")
    return body if status == 200 else {"status": status, **(body or {})}


@functools.cache
def tone():
    """The test-e2e.sh stimulus: scripts/mixxx-substitute.py (--tone, F-394 Q1).

    Expected levels derive from its TONE_* constants, never from literals
    (AE Q1 V2). Loaded on first use, so importing this module does not need
    scripts/ or soundfile.
    """
    script = Path(__file__).resolve().parents[4] / "scripts" / "mixxx-substitute.py"
    spec = importlib.util.spec_from_file_location("mixxx_substitute", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tone_channels() -> tuple[int, ...]:
    """0-based channels the tone plays on (the mains)."""
    return tuple(range(tone().TONE_CHANNELS))


SW_TONE_WINDOW_DB = 1.0
HW_OUT_TONE_WINDOW_DB = 1.5
STIMULUS_TIMEOUT_S = 5.0
SETTLE_S = 1.0
VENUE = "local-demo"


def in_window(peaks, expected: float, window: float) -> bool:
    return all(abs(p - expected) <= window for p in peaks)


def local_demo_venue_gain_db(base_url: str) -> float:
    """Return the mains gain_db of the local-demo venue; FAIL if it is not Dirac.

    The hw-out window assumes Dirac coefficients and one gain on ch 1-2
    (AE Q1 V2), so anything else is a named FAIL, not a shifted window.
    """
    status, detail = _api_get(base_url, f"/api/v1/venue/detail?name={VENUE}")
    if status != 200:
        pytest.fail(f"venue detail for {VENUE!r} failed: {status} {detail}", pytrace=False)
    mains = [ch for ch in detail.get("channels", []) if ch["key"] in ("1_sat_l", "2_sat_r")]
    gains = {ch["gain_db"] for ch in mains}
    coeffs = {ch["coefficients"] for ch in mains}
    if len(mains) != 2 or len(gains) != 1 or coeffs != {"dirac.wav"}:
        pytest.fail(f"venue {VENUE!r} mains are not the Dirac set the hw-out "
                    f"window assumes: {mains}", pytrace=False)
    return float(gains.pop())


@pytest.fixture()
def tone_on_sw_tap(ensure_dj_mode, level_sw_port):
    """FAIL unless the --tone stimulus shows on level-bridge-sw (Q1-3, Q1-4).

    Ch 1-2 within SW_TONE_WINDOW_DB of the tone peak, ch 3-8 at the floor.
    Returns the per-channel peaks read.
    """
    time.sleep(SETTLE_S)
    t = tone()
    silent = range(len(tone_channels()), 8)
    peaks = wait_for_peaks(level_sw_port, tone_channels(),
                           lambda p: in_window(p, t.TONE_PEAK_DBFS, SW_TONE_WINDOW_DB),
                           timeout=STIMULUS_TIMEOUT_S)
    if not in_window(peaks, t.TONE_PEAK_DBFS, SW_TONE_WINDOW_DB):
        pytest.fail(
            f"stimulus (tone {t.TONE_FREQ_HZ} Hz, {t.TONE_PEAK_DBFS} dBFS peak on ch 1-2) "
            f"not on level-bridge-sw within {STIMULUS_TIMEOUT_S}s: read {peaks}",
            pytrace=False)
    rest = max_peak(read_live_levels(level_sw_port, count=3), silent)
    if max(rest) > LEVEL_FLOOR_DB:
        pytest.fail(f"level-bridge-sw ch 3-8 not silent with the tone: {rest}",
                    pytrace=False)
    return peaks


@pytest.fixture()
def virtual_gate_open(tone_on_sw_tap, base_url, level_hw_out_port):
    """Open the D-063 gate in the virtual stack for one test (AE Q2 C1-C4).

    Refuses (FAIL, never skip) unless the stack is local-demo with no ALSA
    hardware. With the tone present, checks hw-out is at the floor while
    the gate is still closed, then opens through the product path (venue
    select + gate open), so the gains are the venue's. Returns the
    expected hw-out tone peak on the mains (tone peak + venue gain_db).
    Teardown, also after a failed test: close the gate, assert the API
    reports it closed and muted (F-439: mute = gate closed, no unmute),
    assert hw-out is back at the floor and all 16 gain values read 0.
    """
    refusal = virtual_stack_refusal(BACKEND_TYPE, _pw_dump())
    if refusal:
        pytest.fail(f"Refusing to open the gate: {refusal}", pytrace=False)
    expected = tone().TONE_PEAK_DBFS + local_demo_venue_gain_db(base_url)

    closed = max_peak(read_live_levels(level_hw_out_port), STIMULUS_HW_OUT_CHANNELS)
    if max(closed) > LEVEL_FLOOR_DB:
        pytest.fail(f"hw-out not at the floor with the gate closed and the tone "
                    f"playing: {closed}", pytrace=False)

    status, body = _api_post(base_url, "/api/v1/venue/select", {"venue": VENUE})
    if status != 200 or not body.get("ok"):
        pytest.fail(f"venue select failed: {status} {body}", pytrace=False)
    try:
        status, body = _api_post(base_url, "/api/v1/venue/gate/open")
        if status != 200 or not body.get("gate_open"):
            pytest.fail(f"gate open failed: {status} {body}", pytrace=False)
        yield expected
    finally:
        _api_post(base_url, "/api/v1/venue/gate/close")
        gate = _gate_state(base_url)
        _, mute = _api_get(base_url, "/api/v1/audio/mute-status")
        if gate.get("gate_open") is not False or mute.get("is_muted") is not True:
            pytest.fail(f"teardown left gate={gate} mute={mute}", pytrace=False)
        peaks = wait_for_peaks(level_hw_out_port, STIMULUS_HW_OUT_CHANNELS,
                               lambda p: max(p) <= LEVEL_FLOOR_DB, timeout=2.0)
        if max(peaks) > LEVEL_FLOOR_DB:
            pytest.fail(f"hw-out not at the floor after gate close: {peaks}",
                        pytrace=False)
        live = nonzero_gains(read_back_gains())
        if live:
            pytest.fail(f"teardown left non-zero gains behind the closed gate: "
                        f"{live}", pytrace=False)
