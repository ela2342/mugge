"""The assembled page loads and drives the setup step (US-179 AC2, AC11).

Chromium's fake media devices stand in for the mic; nothing plays here.
The full measurement run with simulated room audio is the E2E test.
"""

import pytest
from playwright.sync_api import expect

from .test_pipeline_smoke import _build, _serve

FAKE_MEDIA = [
    "--use-fake-ui-for-media-stream",
    "--use-fake-device-for-media-stream",
    "--autoplay-policy=no-user-gesture-required",
]


@pytest.fixture(scope="module")
def page_url(tmp_path_factory):
    with _serve(_build(tmp_path_factory)) as url:
        yield url + "/index.html"


@pytest.fixture()
def fake_page(browser_type):
    browser = browser_type.launch(args=FAKE_MEDIA)
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    yield page, errors
    browser.close()


def test_first_load_shows_setup_blocked(fake_page, page_url):
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    expect(page.locator("#header")).to_have_text(
        "Standalone — not connected to a mugge Pi")
    assert page.is_visible("#step-setup")
    for step in ("ack", "level", "measure", "result"):
        assert page.is_hidden(f"#step-{step}")
    assert page.is_disabled("#confirm")
    assert page.text_content("#problems") == "No audio device yet."
    assert page.text_content("#cal-status") == (
        "Uncalibrated: No calibration file loaded.")
    assert page.is_hidden("#stop")
    assert errors == []


def test_open_devices_then_declarations_gate_continue(fake_page, page_url):
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    page.click("#open")
    # Chromium's fake mic runs at 44.1 kHz: the 2a refusal (no resampling).
    expect(page.locator("#rate-lines li")).to_have_text([
        "Sample rate: 48000 Hz (output)", "Sample rate: 44100 Hz (input)"])
    expect(page.locator("#rate-refusal")).to_have_text(
        "Can't measure: this audio device runs at 44100 Hz. mugge filters "
        "need 48 kHz. Set the device to 48 kHz in your system's audio "
        "settings, then reload this page.")
    # AC3: role first; the limit is refused inline when not whole Hz (E5c).
    expect(page.locator("#limit")).to_be_disabled()
    page.check("input[name=role][value=subwoofer]")
    expect(page.locator("#limit")).to_have_value("20")
    page.fill("#limit", "40.5")
    expect(page.locator("#limit-error")).to_have_text(
        "Enter the low limit as a whole number of Hz between 20 and 50 (e.g. 40).")
    page.fill("#limit", "60")
    expect(page.locator("#limit-error")).to_have_text(
        "A subwoofer limit above 50 Hz is not supported here. Check the "
        "setting, or choose Full-range speaker.")
    page.fill("#limit", "40")
    expect(page.locator("#limit-error")).to_be_hidden()
    expect(page.locator("#capability-text")).to_have_text(
        "This subwoofer can safely play down to 40 Hz at moderate level. "
        "I have checked its spec sheet.")
    page.check("#capability")
    # A new limit clears the tick.
    page.fill("#limit", "30")
    expect(page.locator("#capability")).not_to_be_checked()
    page.check("#capability")
    page.check("input[name=enclosure][value=ported]")
    page.fill("#tuning", "35")
    expect(page.locator("#port-warning")).to_be_visible()
    # 3c (UX 64c83e3e): the label names the values; ANY change of the
    # limit or the tuning clears the tick.
    expect(page.locator("#port-confirm-text")).to_have_text(
        "I understand the risk: measure down to 30 Hz, below the port "
        "tuning of 35 Hz.")
    page.check("#port-confirm")
    page.fill("#limit", "25")
    expect(page.locator("#port-confirm")).not_to_be_checked()
    expect(page.locator("#port-confirm-text")).to_have_text(
        "I understand the risk: measure down to 25 Hz, below the port "
        "tuning of 35 Hz.")
    page.check("#port-confirm")
    page.fill("#tuning", "36")
    expect(page.locator("#port-confirm")).not_to_be_checked()
    page.fill("#tuning", "35")
    page.fill("#limit", "30")
    page.check("#capability")
    page.check("#port-confirm")
    page.select_option("#channel", "0")
    # Everything declared; the rate alone still blocks.
    expect(page.locator("#problems li")).to_have_text([
        "Can't measure: this audio device runs at 44100 Hz. mugge filters "
        "need 48 kHz. Set the device to 48 kHz in your system's audio "
        "settings, then reload this page."])
    expect(page.locator("#confirm")).to_be_disabled()
    expect(page.locator("#step-setup")).to_be_visible()
    assert errors == []


def test_hidden_holds_start_until_visible_again(fake_page, page_url):
    """Latch r2 A3: hiding the page holds Start; showing it releases it."""
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    held = "[...window.__webrcApp.flow.held]"
    page.evaluate("""() => {
        window.__hidden = false;
        Object.defineProperty(document, "hidden",
            { configurable: true, get: () => window.__hidden });
    }""")
    page.evaluate("""() => { window.__hidden = true;
        document.dispatchEvent(new Event("visibilitychange")); }""")
    assert page.evaluate(held) == ["hidden"]
    page.evaluate("""() => { window.__hidden = false;
        document.dispatchEvent(new Event("visibilitychange")); }""")
    assert page.evaluate(held) == []
    # pagehide holds; a pageshow of a visible page (bfcache) releases.
    page.evaluate("window.dispatchEvent(new Event('pagehide'))")
    assert page.evaluate(held) == ["hidden"]
    page.evaluate("window.dispatchEvent(new Event('pageshow'))")
    assert page.evaluate(held) == []
    assert errors == []


def test_hold_text_next_to_disabled_start(fake_page, page_url):
    """E6b: a hold that came while idle shows its text by the disabled Start."""
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    page.evaluate("""() => {
        const app = window.__webrcApp, f = app.flow;
        const off = { echoCancellation: false, noiseSuppression: false,
            autoGainControl: false };
        f.setAudio({ outputRate: 48000, inputRate: 48000, outputChannels: 2,
            dspSettings: off, micId: "m", micLabel: "UMIK-1" });
        f.setChannel(0);
        f.setDeclaration({ ...f.decl, role: "fullrange", limitHz: 80,
            capabilityConfirmed: true, enclosure: "closed" });
        f.confirmSetup();
        for (let i = 0; i < 4; i++) f.tickAck(i, true);
        f.acknowledge();
        f.output({ type: "stopped", cause: "heartbeat" });
        app.render();
    }""")
    hold = page.locator("#hold-text")
    expect(page.locator("#start")).to_be_disabled()
    expect(hold).to_be_visible()
    expect(hold).to_have_text(
        "Stopped for safety: the microphone level monitor stopped "
        "responding, so the sound was stopped. This can happen when the "
        "computer is busy. Go back to setup, press Use these devices, then "
        "start the level check again.")
    expect(page.locator("#notice")).to_be_hidden()
    # Released by opening the devices again.
    page.evaluate("""() => { const app = window.__webrcApp;
        app.flow.setAudio(app.flow.audio); app.render(); }""")
    expect(page.locator("#start")).to_be_enabled()
    expect(hold).to_be_hidden()
    # The result step's Start shows it too.
    page.evaluate("""() => { const app = window.__webrcApp;
        app.flow.step = "result"; app.flow.audioError(); app.render(); }""")
    expect(page.locator("#again")).to_be_disabled()
    expect(page.locator("#again-hold-text")).to_have_text(
        "Stopped: an audio error occurred. Go back to setup, press Use these "
        "devices, then start the level check again.")
    assert errors == []


def test_ack_checkboxes_gate_the_button(fake_page, page_url):
    """4a (UX 64c83e3e): one checkbox per item; the button needs them all."""
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    # Stand-in devices at 48 kHz (the fake mic runs at 44.1 kHz).
    page.evaluate("""() => {
        const app = window.__webrcApp, f = app.flow;
        const off = { echoCancellation: false, noiseSuppression: false,
            autoGainControl: false };
        f.setAudio({ outputRate: 48000, inputRate: 48000, outputChannels: 2,
            dspSettings: off, micId: "m", micLabel: "UMIK-1" });
        f.setChannel(0);
        f.setDeclaration({ ...f.decl, role: "fullrange", limitHz: 80,
            capabilityConfirmed: true, enclosure: "closed" });
        f.confirmSetup();
        app.render();
    }""")
    expect(page.locator("#step-ack")).to_be_visible()
    expect(page.locator("#ack-title")).to_have_text("Before any sound plays")
    boxes = page.locator("#ack-items input[type=checkbox]")
    expect(boxes).to_have_count(4)
    expect(page.locator("#ack-items li").nth(3)).to_have_text(
        "Sound plays on this browser's default output device. I have "
        "checked that it is connected to the speaker I want to measure.")
    expect(page.locator("#ack")).to_be_disabled()
    for i in range(3):
        boxes.nth(i).check()
    expect(page.locator("#ack")).to_be_disabled()
    boxes.nth(3).check()
    expect(page.locator("#ack")).to_be_enabled()
    boxes.nth(1).uncheck()
    expect(page.locator("#ack")).to_be_disabled()
    boxes.nth(1).check()
    page.click("#ack")
    expect(page.locator("#step-level")).to_be_visible()
    expect(page.locator("#plus")).to_have_text("+6 dB")
    # E5 D1: after a device change every box shows unticked again.
    page.evaluate("""() => {
        const app = window.__webrcApp, f = app.flow;
        f.deviceChange({ ...f.audio });
        f.setChannel(0);
        f.setDeclaration({ ...f.decl, role: "fullrange", limitHz: 80,
            capabilityConfirmed: true, enclosure: "closed" });
        f.confirmSetup();
        app.render();
    }""")
    expect(page.locator("#step-ack")).to_be_visible()
    for i in range(4):
        expect(boxes.nth(i)).not_to_be_checked()
    expect(page.locator("#ack")).to_be_disabled()
    assert errors == []


# A result as analyze returns it, set on the flow directly: the plots are
# drawn from it by app.js with the shipped spectrum-renderer.js (AC11).
_RESULT_JS = """([level, withPrediction]) => {
    const app = window.__webrcApp, f = app.flow;
    const n = 60, freqs = Float64Array.from({ length: n },
        (_, i) => 20 * Math.pow(1000, i / (n - 1)));
    const curve = (g) => Float64Array.from(freqs, (x, i) => g(x, i));
    const ir = new Float64Array(19200);
    ir[Math.round(0.105 * 48000)] = 0.8;
    const r = {
        fileName: "combined_ch1-fullrange-browser-generated.wav",
        wavBytes: new Uint8Array(4), role: "fullrange", limitHz: 80,
        channel: 0, delayS: 0.005, calibrated: false,
        measured: { freqs, db: curve(() => level) },
        ir, irStartS: -0.1,
        repeatability: { ok: true, band_hz: [80, 16000], max_abs_db: 0.6,
            limit_db: 1.0, freqs, diff_db: curve((x) => x < 80 ? 2 : 0.3) },
        prediction: { passed: true, label: "", band_hz: [80, 16000],
            freqs: withPrediction ? freqs : new Float64Array(0),
            measured_db: curve(() => 3), predicted_db: curve(() => 1),
            target_db: curve(() => 0) },
    };
    f.filters.set(0, { ...r, enclosure: "closed", preDeviceChange: false,
        downloaded: false });
    f.run.result = r;
    f.step = "result";
    app.render();
    const drawn = (id) => {
        const c = document.getElementById(id);
        const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
        let k = 0;
        for (let i = 0; i < d.length; i += 4) {
            if (d[i] !== d[0] || d[i + 1] !== d[1] || d[i + 2] !== d[2]) k++;
        }
        return { w: c.width, h: c.height, k };
    };
    return Object.fromEntries(["plot-measured", "plot-impulse",
        "plot-repeatability", "plot-prediction"].map((id) => [id, drawn(id)]));
}"""


def test_result_step_draws_the_plots(fake_page, page_url):
    page, errors = fake_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")
    flat = page.evaluate(_RESULT_JS, [-99, True])
    expect(page.locator("#step-result")).to_be_visible()
    shown = page.evaluate(_RESULT_JS, [0, True])
    for plot in shown.values():
        assert plot["w"] > 100 and plot["h"] > 50, plot
        assert plot["k"] > 500, plot
    # The measured magnitude is the renderer's mountain, not just its grid.
    assert shown["plot-measured"]["k"] > flat["plot-measured"]["k"] + 2000, (
        shown, flat)
    expect(page.locator("#plot-measured-caption")).to_have_text(
        "Measured response, 1/6-octave smoothed (0 dB = the correction's "
        "reference level)")
    expect(page.locator("#plot-repeatability-caption")).to_contain_text(
        "grey: outside the checked 80-16000 Hz.")
    expect(page.locator("#plot-prediction-figure")).to_be_visible()
    expect(page.locator("#plot-prediction-caption")).to_have_text(
        "Predicted response after correction — predicted, not measured")
    assert "phase" not in page.text_content("#step-result").lower()
    assert "coheren" not in page.text_content("#step-result").lower()
    page.evaluate(_RESULT_JS, [0, False])
    expect(page.locator("#plot-prediction-figure")).to_be_hidden()
    assert errors == []
