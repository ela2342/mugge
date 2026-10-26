// Minimal in-browser test runner for the web-rc JS units.
//
// runner.html?module=js/noise.test.js imports that module, runs every
// exported `test_*` async function and publishes the results on
// window.__webrcResults for the pytest driver (test_js_units.py).

const params = new URLSearchParams(location.search);
const modPath = params.get("module");
const out = document.getElementById("out");

async function run() {
  const results = [];
  const mod = await import("./" + modPath);
  for (const [name, fn] of Object.entries(mod)) {
    if (!name.startsWith("test_") || typeof fn !== "function") continue;
    try {
      await fn();
      results.push({ name, ok: true });
    } catch (e) {
      results.push({ name, ok: false, error: String(e && e.stack || e) });
    }
  }
  return results;
}

run().then(
  (results) => {
    out.textContent = results.map(
      (r) => (r.ok ? "PASS " : "FAIL ") + r.name + (r.ok ? "" : "\n" + r.error),
    ).join("\n");
    window.__webrcResults = { done: true, results };
  },
  (e) => {
    out.textContent = "LOAD ERROR " + e;
    window.__webrcResults = { done: true, loadError: String(e && e.stack || e) };
  },
);
