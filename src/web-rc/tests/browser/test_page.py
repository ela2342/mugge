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
