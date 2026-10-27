"""Browser E2E: MUTE closes the D-063 gate; no control raises Mult (F-439).

US-160 AC3: a browser test covers AC1 (no web UI control raises Mult while
the gate is closed) and AC2 (the visible path back is Open Gate), and
cross-checks every Mult in PipeWire with pw-cli, never the web-ui state.

    - Gate closed (GM starts closed): the panic button reads MUTED, and a
      click goes to the AUDIO GATE section; no Mult changes.
    - Gate closed: a Config tab gain apply is refused (409), the sliders
      show the server readback, and all 8 Mult stay 0.
    - Gate open (virtual_gate_open, local-demo only): a MUTE click closes
      the gate, all 8 Mult read 0, and the CONV>OUT VU and hw-out tap are
      at the floor. The next click (MUTED) sends no mute, unmute or gate
      request (QE 6e0e16b1 T6).
    - Gate open, mute answered 502 (route interception): MUTED never shows.

Usage:
    nix run .#test-e2e    # runs both service-integration and e2e tiers
"""

import json
import os
import re
import socket
import urllib.request

import pytest
from playwright.sync_api import expect

from fixtures.backend import (  # noqa: F401
    GAIN_NAMES,
    LEVEL_FLOOR_DB,
    STIMULUS_HW_OUT_CHANNELS,
    nonzero_gains,
    read_back_gains,
    tone_on_sw_tap,
    virtual_gate_open,
    wait_for_peaks,
)

pytestmark = [pytest.mark.browser, pytest.mark.slow]

WS_DATA_TIMEOUT_MS = 15_000
GATE_UI_TIMEOUT_MS = 5_000
NOT_MUTED_HOLD_MS = 3_000
HW_OUT_FLOOR_TIMEOUT_S = 2.0
RAISE_MULT = 0.01  # -40 dB, inside the slider soft cap

PANIC_TITLE_MUTE = "Mute all outputs now (closes the audio gate)"
PANIC_TITLE_MUTED = ("All outputs muted: the audio gate is closed. To play "
                     "again, use OPEN GATE in the Audio Gate section.")
GATE_CLOSED_TEXT = ("Not applied: the audio gate is closed, so no gain was "
                    "changed. Gains can only be changed while the gate is open.")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _probe_server(url: str) -> bool:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8080
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def local_demo_url():
    url = os.environ.get("LOCAL_DEMO_URL", "http://localhost:8080")
    if not _probe_server(url):
        pytest.skip(
            f"Local-demo server not reachable at {url}. "
            f"Start it with: nix run .#local-demo")
    return url


def _post(url: str, path: str) -> None:
    req = urllib.request.Request(
        f"{url}{path}", data=json.dumps({}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req, timeout=5)


def _get(url: str, path: str) -> dict:
    with urllib.request.urlopen(f"{url}{path}", timeout=5) as resp:
        return json.loads(resp.read())


@pytest.fixture()
def demo_page(browser, local_demo_url):
    """Fresh browser page navigated to the local-demo server."""
    context = browser.new_context()
    pg = context.new_page()
    pg.goto(local_demo_url)
    yield pg
    # Leave the gate closed (= muted); there is no unmute (F-439).
    try:
        _post(local_demo_url, "/api/v1/audio/mute")
    except Exception:
        pass
    context.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_for_ws_data(page, timeout_ms=WS_DATA_TIMEOUT_MS):
    """Wait until WebSocket delivers monitoring data."""
    page.locator("#sb-dsp-state").wait_for(state="attached")
    page.wait_for_function(
        "document.getElementById('sb-dsp-state').textContent !== '--'",
        timeout=timeout_ms,
    )


def _record_gate_requests(page) -> list[str]:
    """Collect every request to mute, unmute or the gate routes from now on."""
    seen: list[str] = []

    def on_request(request):
        if re.search(r"/api/v1/(audio/(mute|unmute)|venue/gate/)", request.url):
            seen.append(f"{request.method} {request.url}")
    page.on("request", on_request)
    return seen


def _dspout_readouts(page) -> list[str]:
    """CONV>OUT VU dB readouts for the hw-out channels (fed by levels_hw_out)."""
    return [page.locator(f"#meters-dspout-db-{ch}").inner_text()
            for ch in STIMULUS_HW_OUT_CHANNELS]


def _assert_all_gains_zero(when: str) -> None:
    """All 16 gain values (8 Mult, 8 Add) read 0 in PipeWire (AE 1fb3da7c P1)."""
    live = nonzero_gains(read_back_gains())
    assert not live, f"gain not 0 in PipeWire {when}: {live}"


# ===========================================================================
# Tests
# ===========================================================================

class TestMutedWhileGateClosed:
    """AC2: with the gate closed the button reads MUTED and points to Open Gate."""

    def test_closed_gate_shows_muted(self, demo_page, local_demo_url):
        _wait_for_ws_data(demo_page)
        assert _get(local_demo_url, "/api/v1/audio/mute-status")["gate"] == "closed"
        btn = demo_page.locator('[data-testid="panic-button"]')
        expect(btn).to_have_text("MUTED", timeout=GATE_UI_TIMEOUT_MS)
        expect(btn).to_have_class(re.compile(r"\bmuted\b"))
        expect(btn).to_have_attribute("title", PANIC_TITLE_MUTED)

    def test_muted_click_shows_audio_gate_section(self, demo_page):
        _wait_for_ws_data(demo_page)
        btn = demo_page.locator('[data-testid="panic-button"]')
        expect(btn).to_have_text("MUTED", timeout=GATE_UI_TIMEOUT_MS)
        requests = _record_gate_requests(demo_page)
        btn.click()
        expect(demo_page.locator("#view-config")).to_have_class(
            re.compile(r"\bactive\b"), timeout=GATE_UI_TIMEOUT_MS)
        expect(demo_page.locator("#cfg-audio-gate")).to_be_in_viewport()
        expect(btn).to_have_text("MUTED")
        assert requests == [], f"a MUTED click sent requests: {requests}"
        _assert_all_gains_zero("after a MUTED click")


class TestNoGainRaiseWhileGateClosed:
    """AC1: a Config tab gain apply cannot raise Mult with the gate closed."""

    def test_gain_apply_refused(self, demo_page, local_demo_url):
        _wait_for_ws_data(demo_page)
        _assert_all_gains_zero("before the apply")
        demo_page.locator('.nav-tab[data-view="config"]').click()
        slider = demo_page.locator("#cfg-gain-gain_left_hp")
        expect(slider).to_be_enabled(timeout=GATE_UI_TIMEOUT_MS)

        slider.evaluate(
            "(el, v) => { el.value = String(v);"
            " el.dispatchEvent(new Event('input')); }", RAISE_MULT)
        apply_btn = demo_page.locator("#cfg-gain-apply")
        expect(apply_btn).to_be_enabled()
        apply_btn.click()

        expect(demo_page.locator("#cfg-gain-status")).to_have_text(
            GATE_CLOSED_TEXT, timeout=GATE_UI_TIMEOUT_MS)
        gains = _get(local_demo_url, "/api/v1/config")["gains"]
        for name in GAIN_NAMES:
            ui = float(demo_page.locator(f"#cfg-gain-{name}").input_value())
            assert ui == pytest.approx(gains[name]["mult"]), (
                f"{name} slider {ui} != server readback {gains[name]}")
        _assert_all_gains_zero("after a refused gain apply")


class TestMuteClosesGate:
    """MUTE with the gate open closes it; PipeWire reads all Mult 0."""

    def test_mute_click_closes_gate(self, virtual_gate_open, demo_page,
                                    local_demo_url, level_hw_out_port):
        _wait_for_ws_data(demo_page)
        btn = demo_page.locator('[data-testid="panic-button"]')
        expect(btn).to_have_text("MUTE", timeout=GATE_UI_TIMEOUT_MS)
        expect(btn).to_have_attribute("title", PANIC_TITLE_MUTE)
        gains = read_back_gains()
        assert nonzero_gains(gains, "Mult"), (
            "gate open but every Mult is 0: the mute check would prove nothing")
        assert not nonzero_gains(gains, "Add"), (
            f"gate open with a non-zero Add: {nonzero_gains(gains, 'Add')}")
        demo_page.wait_for_function(
            "() => ['0', '1'].every(ch => {"
            " const el = document.getElementById('meters-dspout-db-' + ch);"
            " return el && el.textContent !== '-inf' && el.textContent !== ''; })",
            timeout=WS_DATA_TIMEOUT_MS)

        btn.click()
        expect(btn).to_have_text("MUTED", timeout=GATE_UI_TIMEOUT_MS)
        assert _get(local_demo_url, "/api/v1/audio/mute-status") == {
            "is_muted": True, "gate": "closed"}
        _assert_all_gains_zero("after a MUTE click")
        peaks = wait_for_peaks(level_hw_out_port, STIMULUS_HW_OUT_CHANNELS,
                               lambda p: max(p) <= LEVEL_FLOOR_DB,
                               timeout=HW_OUT_FLOOR_TIMEOUT_S)
        assert max(peaks) <= LEVEL_FLOOR_DB, (
            f"hw-out {peaks} not at the {LEVEL_FLOOR_DB} dBFS floor after MUTE")
        demo_page.wait_for_function(
            "(chs) => chs.every(ch =>"
            " document.getElementById('meters-dspout-db-' + ch).textContent === '-inf')",
            arg=list(STIMULUS_HW_OUT_CHANNELS), timeout=GATE_UI_TIMEOUT_MS)

        requests = _record_gate_requests(demo_page)
        btn.click()
        expect(demo_page.locator("#view-config")).to_have_class(
            re.compile(r"\bactive\b"), timeout=GATE_UI_TIMEOUT_MS)
        expect(btn).to_have_text("MUTED")
        assert requests == [], f"the second click sent requests: {requests}"
        _assert_all_gains_zero("after the second click")


class TestFailedMuteNeverShowsMuted:
    """A mute the server does not confirm must not show MUTED."""

    def test_502_mute_keeps_mute_label(self, virtual_gate_open, demo_page):
        _wait_for_ws_data(demo_page)
        btn = demo_page.locator('[data-testid="panic-button"]')
        expect(btn).to_have_text("MUTE", timeout=GATE_UI_TIMEOUT_MS)
        demo_page.route("**/api/v1/audio/mute",
                        lambda route: route.fulfill(status=502, body="bad gateway"))

        with demo_page.expect_response("**/api/v1/audio/mute") as resp:
            btn.click()
        assert resp.value.status == 502
        demo_page.wait_for_timeout(NOT_MUTED_HOLD_MS)
        expect(btn).to_have_text("MUTE")
        expect(btn).not_to_have_class(re.compile(r"\bmuted\b"))
