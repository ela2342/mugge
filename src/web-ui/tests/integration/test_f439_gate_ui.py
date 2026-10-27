"""Browser tests for the F-439 gate UI (US-160 AC1/AC2; UX 220558aa, f05b5f4a).

Status bar panic button, driven by ``/ws/system`` ``gate.state``:
    - closed:  'MUTED' (muted class); a click goes to the AUDIO GATE section
      and sends no request.
    - open:    'MUTE'; a click posts /api/v1/audio/mute.
    - unknown: 'MUTE', never 'MUTED' (GM unreachable must not look muted).

The mock GM gate is always closed, so open and unknown come from an init
script that rewrites ``gate`` in each /ws/system frame before app.js sees
it (``WS_GATE_OVERRIDE``).

Config tab gain apply:
    - 409 gate_closed (the real mock server): the sliders show a fresh
      GET /api/v1/config readback, then the warning text.
    - 409 gate_unknown with a failing readback: the sliders go disabled
      and '-- dB', with the danger text.
    - 409 without a reason, and 422: their own texts.
    page.route stands in for the server only where the mock cannot produce
    the response (gate_unknown, 422, a failing readback).

These pages check uncaught page errors, not console errors: Chromium logs
every 4xx/5xx fetch as a console error, and those responses are the point.
"""

import json
import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

UI_TIMEOUT_MS = 5_000

PANIC_TITLE_MUTE = "Mute all outputs now (closes the audio gate)"
PANIC_TITLE_MUTED = ("All outputs muted: the audio gate is closed. To play "
                     "again, use OPEN GATE in the Audio Gate section.")

GATE_CLOSED_TEXT = ("Not applied: the audio gate is closed, so no gain was "
                    "changed. Gains can only be changed while the gate is open.")
GATE_UNKNOWN_TEXT = ("Not applied: the audio gate state could not be checked, "
                     "so no gain was changed. Try again; if this keeps "
                     "happening, check that the audio services are running.")
GATE_DEFAULT_TEXT = ("Not applied: the audio gate is not confirmed open, so no "
                     "gain was changed.")
INVALID_GAIN_TEXT = "Not applied: invalid gain value, so no gain was changed."

GAIN_NODES = (
    "gain_left_hp", "gain_right_hp", "gain_sub1_lp", "gain_sub2_lp",
    "gain_hp_l", "gain_hp_r", "gain_iem_l", "gain_iem_r",
)
PROBE_GAIN = "gain_left_hp"
PROBE_MULT = 0.05

# Rewrites gate.state / gate.gate_open in every /ws/system frame.
WS_GATE_OVERRIDE = """
(state) => {
    const desc = Object.getOwnPropertyDescriptor(WebSocket.prototype, "onmessage");
    Object.defineProperty(WebSocket.prototype, "onmessage", {
        configurable: true,
        get() { return desc.get.call(this); },
        set(fn) {
            if (!fn || !this.url.includes("/ws/system")) {
                desc.set.call(this, fn);
                return;
            }
            desc.set.call(this, function (ev) {
                let data;
                try { data = JSON.parse(ev.data); } catch (e) { return fn.call(this, ev); }
                if (data && data.gate) {
                    data.gate.state = state;
                    data.gate.gate_open = state === "open";
                }
                return fn.call(this, new MessageEvent("message",
                    { data: JSON.stringify(data) }));
            });
        }
    });
}
"""


@pytest.fixture()
def open_page(browser, mock_server):
    """Factory: a page on the mock server, optionally with a gate override."""
    contexts = []
    page_errors = []

    def _open(gate_state=None):
        context = browser.new_context()
        contexts.append(context)
        if gate_state is not None:
            context.add_init_script(
                script=f"({WS_GATE_OVERRIDE})({json.dumps(gate_state)});")
        pg = context.new_page()
        pg.on("pageerror", lambda exc: page_errors.append(str(exc)))
        pg.goto(mock_server)
        pg.wait_for_function(
            "document.getElementById('sb-dsp-state').textContent !== '--'",
            timeout=UI_TIMEOUT_MS)
        return pg

    yield _open
    for context in contexts:
        context.close()
    assert not page_errors, f"uncaught page errors: {page_errors}"


def _panic(pg):
    return pg.locator('[data-testid="panic-button"]')


def _open_config(pg):
    pg.locator('.nav-tab[data-view="config"]').click()
    expect(pg.locator("#view-config")).to_have_class(re.compile(r"\bactive\b"))
    expect(pg.locator(f"#cfg-gain-{PROBE_GAIN}")).to_be_enabled(timeout=UI_TIMEOUT_MS)


def _move_probe_slider(pg):
    pg.locator(f"#cfg-gain-{PROBE_GAIN}").evaluate(
        "(el, v) => { el.value = String(v); el.dispatchEvent(new Event('input')); }",
        PROBE_MULT)
    expect(pg.locator("#cfg-gain-apply")).to_be_enabled()


def _route_json(pg, pattern, status, body):
    pg.route(pattern, lambda route: route.fulfill(
        status=status, content_type="application/json", body=json.dumps(body)))


# ---------------------------------------------------------------------------
# Status bar panic button
# ---------------------------------------------------------------------------

class TestPanicButtonGateStates:

    def test_closed_shows_muted(self, open_page):
        pg = open_page()
        btn = _panic(pg)
        expect(btn).to_have_text("MUTED", timeout=UI_TIMEOUT_MS)
        expect(btn).to_have_class(re.compile(r"\bmuted\b"))
        expect(btn).to_have_attribute("title", PANIC_TITLE_MUTED)

    def test_muted_click_goes_to_audio_gate(self, open_page):
        pg = open_page()
        mute_posts = []
        pg.on("request", lambda req: mute_posts.append(req.url)
              if "/api/v1/audio/" in req.url else None)
        btn = _panic(pg)
        expect(btn).to_have_text("MUTED", timeout=UI_TIMEOUT_MS)
        btn.click()
        expect(pg.locator("#view-config")).to_have_class(
            re.compile(r"\bactive\b"), timeout=UI_TIMEOUT_MS)
        expect(pg.locator("#cfg-audio-gate")).to_be_in_viewport()
        assert mute_posts == [], f"MUTED click sent requests: {mute_posts}"

    def test_unknown_is_not_muted(self, open_page):
        pg = open_page("unknown")
        btn = _panic(pg)
        expect(btn).to_have_text("MUTE", timeout=UI_TIMEOUT_MS)
        expect(btn).not_to_have_class(re.compile(r"\bmuted\b"))
        expect(btn).to_have_attribute("title", PANIC_TITLE_MUTE)

    def test_open_shows_mute_and_click_closes_gate(self, open_page):
        pg = open_page("open")
        btn = _panic(pg)
        expect(btn).to_have_text("MUTE", timeout=UI_TIMEOUT_MS)
        expect(btn).to_have_attribute("title", PANIC_TITLE_MUTE)
        with pg.expect_response(
                lambda r: r.url.endswith("/api/v1/audio/mute")
                and r.request.method == "POST") as resp_info:
            btn.click()
        resp = resp_info.value
        assert resp.status == 200 and resp.json() == {"ok": True, "gate_open": False}


# ---------------------------------------------------------------------------
# Config tab gain apply refusals
# ---------------------------------------------------------------------------

class TestGainApplyRefused:

    def test_gate_closed_reverts_to_readback(self, open_page, mock_server):
        pg = open_page()
        _open_config(pg)
        _move_probe_slider(pg)
        requests = []
        pg.on("request", lambda req: requests.append((req.method, req.url)))

        pg.locator("#cfg-gain-apply").click()
        status = pg.locator("#cfg-gain-status")
        expect(status).to_have_text(GATE_CLOSED_TEXT, timeout=UI_TIMEOUT_MS)
        expect(status).to_have_class(re.compile(r"\bc-warning\b"))

        paths = [(m, u.split(mock_server, 1)[-1]) for m, u in requests]
        post = paths.index(("POST", "/api/v1/config/gain"))
        assert ("GET", "/api/v1/config") in paths[post + 1:], (
            f"no readback after the refused apply: {paths}")
        gains = pg.evaluate(
            "fetch('/api/v1/config').then(r => r.json()).then(d => d.gains)")
        for name in GAIN_NODES:
            ui = float(pg.locator(f"#cfg-gain-{name}").input_value())
            assert ui == pytest.approx(min(gains[name]["mult"], 0.1)), (
                f"{name} slider {ui} != readback {gains[name]}")
        assert float(pg.locator(f"#cfg-gain-{PROBE_GAIN}").input_value()) != PROBE_MULT
        expect(pg.locator("#cfg-gain-apply")).to_be_disabled()

    def test_gate_unknown_with_failing_readback(self, open_page):
        pg = open_page()
        _open_config(pg)
        _move_probe_slider(pg)
        _route_json(pg, "**/api/v1/config/gain", 409,
                    {"ok": False, "error": "gate_not_open", "reason": "gate_unknown",
                     "applied": {}})
        _route_json(pg, "**/api/v1/config", 500, {"error": "readback failed"})

        pg.locator("#cfg-gain-apply").click()
        status = pg.locator("#cfg-gain-status")
        expect(status).to_have_text(GATE_UNKNOWN_TEXT, timeout=UI_TIMEOUT_MS)
        expect(status).to_have_class(re.compile(r"\bc-danger\b"))
        for name in GAIN_NODES:
            expect(pg.locator(f"#cfg-gain-{name}")).to_be_disabled()
            expect(pg.locator(f"#cfg-gain-value-{name}")).to_have_text("-- dB")
        expect(pg.locator("#cfg-gain-apply")).to_be_disabled()
        expect(pg.locator("#cfg-gain-reset")).to_be_disabled()

    def test_refusal_without_reason(self, open_page):
        pg = open_page()
        _open_config(pg)
        _move_probe_slider(pg)
        _route_json(pg, "**/api/v1/config/gain", 409,
                    {"ok": False, "error": "gate_not_open"})

        pg.locator("#cfg-gain-apply").click()
        status = pg.locator("#cfg-gain-status")
        expect(status).to_have_text(GATE_DEFAULT_TEXT, timeout=UI_TIMEOUT_MS)
        expect(status).to_have_class(re.compile(r"\bc-warning\b"))

    def test_invalid_value_422(self, open_page):
        pg = open_page()
        _open_config(pg)
        _move_probe_slider(pg)
        _route_json(pg, "**/api/v1/config/gain", 422,
                    {"detail": [{"msg": "Mult must be finite"}]})

        pg.locator("#cfg-gain-apply").click()
        status = pg.locator("#cfg-gain-status")
        expect(status).to_have_text(INVALID_GAIN_TEXT, timeout=UI_TIMEOUT_MS)
        expect(status).to_have_class(re.compile(r"\bc-danger\b"))
        expect(pg.locator("#cfg-gain-apply")).to_be_enabled()
