"""Run the web-rc JS unit modules in Chromium (US-179 AC12).

Each module in tests/browser/js/*.test.js exports async test_* functions;
runner.html runs them and publishes the results for this driver.
"""

from pathlib import Path

import pytest

JS_DIR = Path(__file__).resolve().parent / "js"
MODULES = sorted(p.name for p in JS_DIR.glob("*.test.js"))


@pytest.mark.parametrize("module", MODULES)
def test_js_module(page, web_rc_url, module):
    page.goto(f"{web_rc_url}/tests/browser/runner.html?module=js/{module}")
    page.wait_for_function("window.__webrcResults && window.__webrcResults.done",
                           timeout=30000)
    out = page.evaluate("window.__webrcResults")
    assert "loadError" not in out, out.get("loadError")
    results = out["results"]
    assert results, f"{module} ran no tests"
    failed = [f"{r['name']}: {r['error']}" for r in results if not r["ok"]]
    assert not failed, "\n".join(failed)
