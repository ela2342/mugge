// rc-worker.js -- module worker running the room-correction pipeline in
// Pyodide (US-179).
//
// Loads the vendored runtime from ../pyodide/ (no network beyond this
// site), fetches every file listed in ../py/manifest.json, checks its
// sha256, writes it into the Pyodide filesystem and imports webrc_bridge.
//
// Protocol (see rc-client.js):
//   worker -> page  {type: "ready"} | {type: "failed", message}
//   page -> worker  {id, fn, args}
//   worker -> page  {id, ok: true, result} | {id, ok: false, kind, message}

import { loadPyodide } from "../pyodide/pyodide.mjs";

const PY_DIR = "/home/pyodide/webrc";
const SITE = new URL("../", import.meta.url);

function hex(buf) {
  return Array.from(new Uint8Array(buf),
    (b) => b.toString(16).padStart(2, "0")).join("");
}

async function fetchChecked(entry) {
  const resp = await fetch(new URL("py/" + entry.path, SITE));
  if (!resp.ok) throw new Error(`py/${entry.path}: HTTP ${resp.status}`);
  const data = new Uint8Array(await resp.arrayBuffer());
  const digest = hex(await crypto.subtle.digest("SHA-256", data));
  if (digest !== entry.sha256) {
    throw new Error(`py/${entry.path}: sha256 ${digest}, manifest says ` +
      entry.sha256);
  }
  return data;
}

async function init() {
  const pyodide = await loadPyodide({ indexURL: new URL("pyodide/", SITE).href });
  await pyodide.loadPackage(["numpy", "scipy"]);
  const resp = await fetch(new URL("py/manifest.json", SITE));
  if (!resp.ok) throw new Error(`py/manifest.json: HTTP ${resp.status}`);
  const manifest = await resp.json();
  for (const entry of manifest.files) {
    const data = await fetchChecked(entry);
    const path = `${PY_DIR}/${entry.path}`;
    pyodide.FS.mkdirTree(path.slice(0, path.lastIndexOf("/")));
    pyodide.FS.writeFile(path, data);
  }
  pyodide.runPython(`
import sys
sys.path.insert(0, ${JSON.stringify(PY_DIR)})
import webrc_bridge
`);
  return pyodide.globals.get("webrc_bridge");
}

const ready = init();
ready.then(
  () => postMessage({ type: "ready" }),
  (e) => postMessage({ type: "failed", message: String(e && e.message || e) }),
);

onmessage = async (event) => {
  const { id, fn, args } = event.data;
  let bridge;
  try {
    bridge = await ready;
  } catch (e) {
    postMessage({ id, ok: false, kind: "error",
      message: "pipeline failed to load: " + String(e && e.message || e) });
    return;
  }
  let out;
  try {
    const res = bridge.call(fn, args);
    out = res.toJs({ dict_converter: Object.fromEntries });
    res.destroy();
  } catch (e) {
    out = { ok: false, kind: "error", message: String(e && e.message || e) };
  }
  // Copied by structured clone; never transfer, a view could alias the
  // WASM heap.
  postMessage({ id, ...out });
};
