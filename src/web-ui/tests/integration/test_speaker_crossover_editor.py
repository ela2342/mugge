"""F-374 G1: the speaker editor never silently rewrites a stored crossover.

A stored profile with an unsupported slope (96) and type ("LR4") opens in
the editor with both values shown as selected, disabled "(not supported)"
options plus an inline note.  Saving sends both values back unchanged, so
the backend keeps rejecting the save until a supported value is picked.

The stored profile is served by intercepting GET for one profile; the PUT
is intercepted too, so the repo's YAML is never written.  The backend's
rejection of the same body is covered by
tests/unit/test_speaker_crossover_validation.py.
"""

import json
import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

PROFILE = "2way-80hz-sealed"
SLOPE_96_MESSAGE = "Linkwitz-Riley crossover supports 24 or 48 dB/oct, got 96"


@pytest.fixture()
def editor(browser, mock_server):
    """Page with the stored profile replaced by a slope-96 / type-LR4 copy."""
    import urllib.request
    stored = json.loads(urllib.request.urlopen(
        f"{mock_server}/api/v1/speakers/profiles/{PROFILE}", timeout=5).read())
    stored["crossover"] = {**stored["crossover"],
                           "slope_db_per_oct": 96, "type": "LR4"}

    context = browser.new_context()
    pg = context.new_page()
    errors = []
    pg.on("console",
          lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    puts = []

    def handle(route):
        if route.request.method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(stored))
        elif route.request.method == "PUT":
            puts.append(json.loads(route.request.post_data))
            route.fulfill(status=422, content_type="application/json",
                          body=json.dumps({"error": "validation",
                                           "detail": SLOPE_96_MESSAGE}))
        else:
            route.abort()

    pg.route(f"**/api/v1/speakers/profiles/{PROFILE}", handle)
    pg.goto(mock_server)
    pg.locator('.nav-tab[data-view="config"]').click()
    expect(pg.locator("#view-config")).to_have_class(
        re.compile(r".*\bactive\b.*"))
    pg.locator(f'#spk-profile-list [data-name="{PROFILE}"]').click()
    pg.locator("#spk-edit-btn").click()
    expect(pg.locator("#spk-f-xslope")).to_be_attached()
    yield pg, stored, puts
    context.close()
    # The intercepted 422 is the only expected console error.
    real = [e for e in errors if "/ws/siggen" not in e and "/ws/pcm" not in e
            and "status of 422" not in e]
    assert not real, f"JS console errors: {real}"


def _selected(pg, select_id):
    return pg.eval_on_selector(
        f"#{select_id}",
        "s => { const o = s.options[s.selectedIndex];"
        " return {value: s.value, text: o.textContent, disabled: o.disabled}; }")


class TestStoredUnsupportedCrossover:

    def test_slope_shown_as_unsupported(self, editor):
        pg, _, _ = editor
        sel = _selected(pg, "spk-f-xslope")
        assert sel == {"value": "96", "text": "96 dB/oct (not supported)",
                       "disabled": True}
        expect(pg.locator("#spk-f-xslope-note")).to_have_text(
            "Not supported: choose 24 (LR4) or 48 (LR8)")
        options = pg.eval_on_selector_all(
            "#spk-f-xslope option:not([disabled])", "os => os.map(o => o.value)")
        assert options == ["24", "48"]

    def test_type_shown_as_unsupported(self, editor):
        pg, _, _ = editor
        sel = _selected(pg, "spk-f-xtype")
        assert sel == {"value": "LR4", "text": "LR4 (not supported)",
                       "disabled": True}
        expect(pg.locator("#spk-f-xtype-note")).to_be_visible()
        options = pg.eval_on_selector_all(
            "#spk-f-xtype option:not([disabled])", "os => os.map(o => o.value)")
        assert options == ["linkwitz-riley"]

    def test_save_sends_stored_values_unchanged(self, editor):
        pg, _, puts = editor
        pg.locator("#spk-save-btn").click()
        expect(pg.locator("#spk-form-status")).to_have_text(
            f"Error: {SLOPE_96_MESSAGE}")
        assert len(puts) == 1
        assert puts[0]["crossover"]["slope_db_per_oct"] == 96
        assert puts[0]["crossover"]["type"] == "LR4"
        # Still unsupported after the failed save; nothing rewritten.
        assert _selected(pg, "spk-f-xslope")["value"] == "96"
        assert _selected(pg, "spk-f-xtype")["value"] == "LR4"

    def test_picking_supported_value_is_sent(self, editor):
        pg, _, puts = editor
        pg.select_option("#spk-f-xslope", "24")
        pg.select_option("#spk-f-xtype", "linkwitz-riley")
        expect(pg.locator("#spk-f-xslope-note")).to_be_hidden()
        pg.locator("#spk-save-btn").click()
        expect(pg.locator("#spk-form-status")).to_contain_text("Error")
        assert puts[-1]["crossover"]["slope_db_per_oct"] == 24
        assert puts[-1]["crossover"]["type"] == "linkwitz-riley"


class TestSupportedCrossoverUnchanged:
    """A supported stored profile shows no unsupported option or note."""

    def test_shipped_profile_has_no_unsupported_option(self, browser,
                                                       mock_server):
        context = browser.new_context()
        pg = context.new_page()
        pg.goto(mock_server)
        pg.locator('.nav-tab[data-view="config"]').click()
        pg.locator(f'#spk-profile-list [data-name="{PROFILE}"]').click()
        pg.locator("#spk-edit-btn").click()
        expect(pg.locator("#spk-f-xslope")).to_be_attached()
        assert _selected(pg, "spk-f-xslope") == {
            "value": "48", "text": "48 dB/oct", "disabled": False}
        assert _selected(pg, "spk-f-xtype") == {
            "value": "linkwitz-riley", "text": "linkwitz-riley",
            "disabled": False}
        assert pg.locator("#spk-f-xslope option[disabled]").count() == 0
        assert pg.locator(".spk-form-note").count() == 0
        context.close()
