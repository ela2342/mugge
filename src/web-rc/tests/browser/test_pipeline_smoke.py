"""The assembled site runs the pipeline in Pyodide, offline (US-179).

Builds the site with build_site.py around the vendored runtime
(WEB_RC_PYODIDE, the nix/pyodide.nix output), serves it on localhost and
aborts every request to any other host. The page drives rc-client.js:
two simulated captures -> analyze (IRs, repeatability, filter, WAV
bytes, gates, prediction), plus a clipped capture that must fail closed.
"""

import contextlib
import functools
import http.server
import os
import threading
from urllib.parse import urlparse

import pytest

from .. import conftest


def _build(tmp_path_factory):
    pyodide = os.environ.get("WEB_RC_PYODIDE")
    if not pyodide:
        pytest.fail("WEB_RC_PYODIDE must point at the nix/pyodide.nix output")
    bs, _ = conftest.build_site_module(tmp_path_factory)
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
  const SR = 48000, LIMIT = 40, PRE = 24000, LAT = 1200, ONSET = 128;
  const sweep = await rc.call("make_sweep", LIMIT, 3);
  const played = new Float32Array(PRE + sweep.length);
  played.set(sweep, PRE);
  // Direct sound at -20 dB after LAT samples plus one reflection, and a
  // deterministic noise floor near -75 dBFS, different per capture.
  // Capture 2's output started one quantum late (onset 128).
  function capture(seed, onset) {
    const cap = new Float32Array(PRE + sweep.length + SR);
    let s = seed;
    for (let i = 0; i < cap.length; i++) {
      s = (s * 1103515245 + 12345) >>> 0;
      cap[i] = ((s / 4294967296) - 0.5) * 6e-4;
    }
    for (let i = 0; i < sweep.length; i++) {
      cap[PRE + onset + LAT + i] += 0.1 * sweep[i];
      cap[PRE + onset + LAT + 480 + i] += 0.04 * sweep[i];
    }
    return cap;
  }
  const request = {
    channel: 2, decl: { role: "subwoofer", limitHz: LIMIT },
    played, preRollS: PRE / SR, captures: [capture(12345, 0), capture(777, ONSET)],
    onsets: [0, ONSET], calibrated: false, calibrationText: null,
  };
  const r = await rc.call("analyze", request);
  const clipped = { ...request, captures: [Float32Array.from(request.captures[0]),
    request.captures[1]] };
  clipped.captures[0][PRE + 5000] = 1.0;
  let rejected = null;
  try {
    await rc.call("analyze", clipped);
  } catch (e) {
    rejected = { kind: e.kind, message: e.message };
  }
  let noRole = null;
  try {
    await rc.call("analyze", { ...request, decl: { limitHz: LIMIT } });
  } catch (e) {
    noRole = { kind: e.kind, message: e.message };
  }
  let unknown = null;
  try { await rc.call("build_filter", sweep, LIMIT); } catch (e) { unknown = e.kind; }
  // AC10 report from the result, the way the page builds it.
  const { reportChannels } = await import("/js/view.js");
  const filters = new Map([[2, { ...r, enclosure: "closed", calibrated: false,
    preDeviceChange: false }]]);
  const report = await rc.call("report_text", reportChannels({ filters }), 174);
  rc.terminate();
  return {
    loadMs, sweepType: sweep.constructor.name, sweepLen: sweep.length,
    fileName: r.fileName, wavType: r.wavBytes.constructor.name,
    wavLen: r.wavBytes.length, delay: r.delayS, irType: r.ir.constructor.name,
    gatesOk: r.gates.ok, gates: r.gates.results, repOk: r.repeatability.ok,
    repBand: r.repeatability.band_hz, pred: { ...r.prediction,
      freqs: r.prediction.freqs.length },
    measuredLen: r.measured.freqs.length, rejected, noRole, unknown, report,
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
    assert out["fileName"] == "combined_ch3-sub-browser-generated.wav"
    assert out["wavType"] == "Uint8Array" and out["wavLen"] > 16384 * 4
    assert out["irType"] == "Float64Array"
    assert out["delay"] == pytest.approx(1200 / 48000, abs=2 / 48000)
    assert out["gatesOk"], [g for g in out["gates"] if not g["passed"]]
    assert any(g["name"].startswith("Closed Loop") for g in out["gates"])
    assert out["repOk"] and out["repBand"] == [30, 200]
    pred = out["pred"]
    assert pred["label"].startswith("Predicted residual within 3 dB: ")
    assert pred["band_hz"] == [30, 200] and pred["freqs"] > 0, pred["reason"]
    assert pred["corrected_max_db"] is not None, pred["reason"]
    assert out["measuredLen"] > 0
    assert out["rejected"]["kind"] == "rejected"
    assert "clipped" in out["rejected"]["message"]
    assert "measurement 1 of 2" in out["rejected"]["message"]
    assert out["noRole"]["kind"] == "error" and "role" in out["noRole"]["message"]
    assert out["unknown"] == "error"
    report = out["report"]
    for line in ("Noise base_seed: 174", "Channel Output 3 (channel_index 2)",
                 "  Role: Subwoofer",
                 "  File: combined_ch3-sub-browser-generated.wav",
                 "  Low limit: 40 Hz, subsonic HPF at 32 Hz",
                 "  Enclosure: closed", "  Mic calibration: no",
                 f"  {pred['label']} (checked over 30-200 Hz)",
                 "  Measured uncalibrated: levels in dBFS; the microphone's "
                 "own frequency response is not compensated."):
        assert line + "\n" in report, (line, report)
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
