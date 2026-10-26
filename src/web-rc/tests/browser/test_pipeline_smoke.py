"""The assembled site runs the pipeline in Pyodide, offline (US-179).

Builds the site with build_site.py around the vendored runtime
(WEB_RC_PYODIDE, the nix/pyodide.nix output), serves it on localhost and
aborts every request to any other host. The page drives rc-client.js:
sweep -> simulated capture -> IR -> filter -> WAV bytes -> gates ->
prediction, plus a clipped capture that must fail closed.
"""

import contextlib
import functools
import http.server
import importlib.util
import os
import threading
from pathlib import Path
from urllib.parse import urlparse

import pytest

from .. import conftest

WEB_RC = Path(__file__).resolve().parents[2]


def _build(tmp_path_factory):
    pyodide = os.environ.get("WEB_RC_PYODIDE")
    if not pyodide:
        pytest.fail("WEB_RC_PYODIDE must point at the nix/pyodide.nix output")
    spec = importlib.util.spec_from_file_location("build_site", WEB_RC / "build_site.py")
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    return bs.build(pyodide, tmp_path_factory.mktemp("site") / "out", link_pyodide=True)


@contextlib.contextmanager
def _serve(directory):
    handler = functools.partial(conftest._QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture(scope="module")
def site_url(tmp_path_factory):
    with _serve(_build(tmp_path_factory)) as url:
        yield url


SMOKE_JS = """
async () => {
  const { RcClient } = await import("/js/rc-client.js");
  const rc = new RcClient();
  const t0 = performance.now();
  await rc.ready;
  const loadMs = performance.now() - t0;
  const SR = 48000, LIMIT = 40, PRE = 24000, LAT = 1200;
  const sweep = await rc.call("make_sweep", LIMIT, 3);
  // Direct sound at -20 dB after LAT samples plus one reflection, and a
  // deterministic noise floor near -75 dBFS.
  const cap = new Float64Array(PRE + sweep.length + SR);
  let s = 12345;
  for (let i = 0; i < cap.length; i++) {
    s = (s * 1103515245 + 12345) >>> 0;
    cap[i] = ((s / 4294967296) - 0.5) * 6e-4;
  }
  for (let i = 0; i < sweep.length; i++) {
    cap[PRE + LAT + i] += 0.1 * sweep[i];
    cap[PRE + LAT + 480 + i] += 0.04 * sweep[i];
  }
  const [ir, delay] = await rc.call("ir_from_capture", cap, sweep, PRE);
  const [fir, level] = await rc.call("build_filter", ir, LIMIT);
  const wav = await rc.call("filter_wav_bytes", fir);
  const name = await rc.call("filter_filename", "left");
  const gates = await rc.call("verify_wav_bytes", wav, name, LIMIT);
  const pred = await rc.call("predict", wav, ir, LIMIT);
  const clipped = Float64Array.from(cap);
  clipped[PRE + 5000] = 1.0;
  let rejected = null;
  try {
    await rc.call("ir_from_capture", clipped, sweep, PRE);
  } catch (e) {
    rejected = { kind: e.kind, message: e.message };
  }
  let unknown = null;
  try { await rc.call("__import__", "os"); } catch (e) { unknown = e.kind; }
  rc.terminate();
  return {
    loadMs, sweepType: sweep.constructor.name, sweepLen: sweep.length,
    irType: ir.constructor.name, delay, firLen: fir.length,
    wavType: wav.constructor.name, wavLen: wav.length, name,
    gatesOk: gates.ok, gates: gates.results,
    predLabel: pred.label, predFreqs: pred.freqs.length,
    rejected, unknown,
  };
}
"""


def test_pipeline_runs_offline(page, site_url):
    seen = []

    def route(r):
        seen.append(r.request.url)
        if urlparse(r.request.url).hostname == "127.0.0.1":
            r.continue_()
        else:
            r.abort()

    page.context.route("**/*", route)
    page.goto(site_url + "/")
    out = page.evaluate(SMOKE_JS)

    offsite = [u for u in seen if urlparse(u).hostname != "127.0.0.1"]
    assert not offsite, offsite
    # The route sees the worker's loads too, so "offline" is not vacuous.
    paths = {urlparse(u).path for u in seen}
    for needed in ("/pyodide/pyodide.asm.wasm", "/py/manifest.json",
                   "/py/webrc_pipeline.py", "/py/room_correction/verify.py"):
        assert needed in paths, (needed, sorted(paths))
    assert any(p.startswith("/pyodide/scipy-") for p in paths), sorted(paths)
    assert out["sweepType"] == "Float64Array" and out["sweepLen"] == 3 * 48000
    assert out["irType"] == "Float64Array"
    assert out["delay"] == pytest.approx(1200 / 48000, abs=2 / 48000)
    assert out["firLen"] == 16384
    assert out["wavType"] == "Uint8Array" and out["wavLen"] > 16384 * 4
    assert out["name"] == "combined_left_browser-generated.wav"
    assert out["gatesOk"], [g for g in out["gates"] if not g["passed"]]
    assert out["predLabel"].startswith("Predicted residual within 3 dB: ")
    assert out["predFreqs"] > 0
    assert out["rejected"]["kind"] == "rejected"
    assert "clipped" in out["rejected"]["message"]
    assert out["unknown"] == "error"
    print(f"Pyodide load {out['loadMs']:.0f} ms")


def test_tampered_file_fails_to_load(page, tmp_path_factory):
    out = _build(tmp_path_factory)
    target = out / "py" / "room_correction" / "verify.py"
    target.write_text(target.read_text().replace("-0.5", "+6.0"))
    with _serve(out) as url:
        page.goto(url + "/")
        err = page.evaluate("""async () => {
          const { RcClient } = await import("/js/rc-client.js");
          const rc = new RcClient();
          try { await rc.ready; return null; }
          catch (e) { return e.message; }
          finally { rc.terminate(); }
        }""")
    assert err and "room_correction/verify.py: sha256" in err, err
