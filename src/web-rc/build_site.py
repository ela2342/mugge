"""Assemble the static standalone room-correction site (US-179).

One place defines the site layout and the list of shared sources. The Nix
derivation and the tests both call this script, so what CI tests is what
ships.

    python build_site.py --pyodide <dir> --out <dir> [--link-pyodide]

Layout of <out>:

    index.html, style.css, js/,    page, own JS, reused web-ui assets
    fonts/                          (style.css loads fonts/ relative)
    pyodide/                        vendored runtime + wheels (nix/pyodide.nix)
    py/                             Python files the worker writes into the
                                    Pyodide filesystem
    py/manifest.json                every file under py/ with its sha256

Shared sources are byte-identical copies of src/room-correction and
src/web-ui files (AC "UI reuse", AC9). manifest.json records the source
path and sha256 of each, and tests/unit/test_build_site.py checks them
against the repository.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

WEB_RC = Path(__file__).resolve().parent
SRC = WEB_RC.parent

# room_correction modules the browser pipeline imports (directly or
# transitively). No yaml, no deploy, no venue I/O.
SHARED_PY_MODULES = (
    "__init__.py",
    "closed_loop.py",
    "combine.py",
    "correction.py",
    "crossover.py",
    "deconvolution.py",
    "dsp_utils.py",
    "export.py",
    "generate_profile_filters.py",
    "iso226.py",
    "recording.py",
    "sweep.py",
    "target_curves.py",
    "verify.py",
)

# web-ui assets reused unchanged (site path -> source path).
SHARED_WEB_ASSETS = {
    "js/spectrum-renderer.js": "web-ui/static/js/spectrum-renderer.js",
    "js/pcm-worklet.js": "web-ui/static/js/pcm-worklet.js",
    "style.css": "web-ui/static/style.css",
    "fonts/JetBrainsMono-Regular.woff2": "web-ui/static/fonts/JetBrainsMono-Regular.woff2",
    "fonts/JetBrainsMono-Bold.woff2": "web-ui/static/fonts/JetBrainsMono-Bold.woff2",
    "fonts/LICENSE-JetBrainsMono.txt": "web-ui/static/fonts/LICENSE-JetBrainsMono.txt",
}

# Own Python files under src/web-rc/py (copied as-is).
OWN_PY_FILES = (
    "soundfile.py",
    "webrc_pipeline.py",
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def shared_sources():
    """(site path, source path) for every shared file, in a fixed order."""
    out = [(f"py/room_correction/{m}",
            SRC / "room-correction" / "room_correction" / m)
           for m in SHARED_PY_MODULES]
    out += [(site, SRC / src) for site, src in SHARED_WEB_ASSETS.items()]
    return out


def _copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build(pyodide_dir, out_dir, link_pyodide=False):
    out = Path(out_dir)
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing {out}")
    out.mkdir(parents=True)

    for path in sorted((WEB_RC / "static").rglob("*")):
        if path.is_file():
            _copy(path, out / path.relative_to(WEB_RC / "static"))

    manifest = {"files": []}
    for site, src in shared_sources():
        if (out / site).exists():
            raise SystemExit(f"{site} exists in static/ and as a shared file")
        _copy(src, out / site)
        if site.startswith("py/"):
            manifest["files"].append({
                "path": site[len("py/"):],
                "sha256": sha256_file(src),
                "source": str(src.relative_to(SRC.parent)),
            })
    manifest["shared_web"] = [
        {"path": site, "sha256": sha256_file(src),
         "source": str(src.relative_to(SRC.parent))}
        for site, src in shared_sources() if not site.startswith("py/")
    ]
    for name in OWN_PY_FILES:
        src = WEB_RC / "py" / name
        _copy(src, out / "py" / name)
        manifest["files"].append({
            "path": name,
            "sha256": sha256_file(src),
            "source": str(src.relative_to(SRC.parent)),
        })

    (out / "py" / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    pyodide_dir = Path(pyodide_dir)
    if not (pyodide_dir / "pyodide.mjs").is_file():
        raise SystemExit(f"{pyodide_dir} has no pyodide.mjs")
    if link_pyodide:
        os.symlink(pyodide_dir, out / "pyodide")
    else:
        shutil.copytree(pyodide_dir, out / "pyodide")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pyodide", required=True,
                    help="directory built by nix/pyodide.nix")
    ap.add_argument("--out", required=True, help="output directory (new)")
    ap.add_argument("--link-pyodide", action="store_true",
                    help="symlink pyodide/ instead of copying (tests)")
    args = ap.parse_args(argv)
    build(args.pyodide, args.out, args.link_pyodide)
    return 0


if __name__ == "__main__":
    sys.exit(main())
