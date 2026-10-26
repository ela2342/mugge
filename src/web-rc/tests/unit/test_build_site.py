"""build_site.py: layout, byte-identical shared sources, import closure (US-179 AC9)."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

WEB_RC = Path(__file__).resolve().parents[2]
REPO = WEB_RC.parents[1]

# Modules Pyodide provides (stdlib + vendored wheels) or the bundle ships.
PROVIDED = {"numpy", "scipy", "soundfile"}


@pytest.fixture(scope="module")
def bs():
    spec = importlib.util.spec_from_file_location("build_site", WEB_RC / "build_site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def site(bs, tmp_path_factory):
    fake = tmp_path_factory.mktemp("pyodide")
    (fake / "pyodide.mjs").write_text("// stub\n")
    out = tmp_path_factory.mktemp("site") / "out"
    bs.build(fake, out, link_pyodide=True)
    return out


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_shared_files_byte_identical(bs, site):
    for site_path, src in bs.shared_sources():
        assert (site / site_path).read_bytes() == src.read_bytes(), site_path


def test_manifest_matches_repo(site):
    manifest = json.loads((site / "py" / "manifest.json").read_text())
    entries = manifest["files"] + manifest["shared_web"]
    assert entries
    for e in entries:
        assert _sha(REPO / e["source"]) == e["sha256"], e["source"]
    for e in manifest["files"]:
        assert _sha(site / "py" / e["path"]) == e["sha256"], e["path"]


def test_style_css_next_to_fonts(site):
    # style.css loads fonts/... relative to itself.
    css = (site / "style.css").read_text()
    for ref in ("fonts/JetBrainsMono-Regular.woff2", "fonts/JetBrainsMono-Bold.woff2"):
        assert ref in css and (site / ref).is_file()
    assert (site / "fonts" / "LICENSE-JetBrainsMono.txt").is_file()


def test_refuses_existing_output(bs, site, tmp_path):
    with pytest.raises(SystemExit):
        bs.build(tmp_path, site, link_pyodide=True)


def _imports(path):
    """(absolute top-level names, room_correction submodules) a file imports."""
    tops, rc = set(), set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            for a in node.names:
                tops.add(a.name.split(".")[0])
                if a.name.startswith("room_correction."):
                    rc.add(a.name.split(".")[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative, inside room_correction
                if node.module:
                    rc.add(node.module.split(".")[0])
                else:
                    rc.update(a.name for a in node.names)
            elif node.module == "room_correction":
                rc.update(a.name for a in node.names)
                tops.add("room_correction")
            elif node.module.startswith("room_correction."):
                rc.add(node.module.split(".")[1])
                tops.add("room_correction")
            else:
                tops.add(node.module.split(".")[0])
    return tops, rc


def test_import_closure(site):
    """Every module the bundle imports is shipped, stdlib or a vendored wheel."""
    import sys

    py = site / "py"
    shipped_rc = {p.stem for p in (py / "room_correction").glob("*.py")}
    own = {p.stem for p in py.glob("*.py")}
    files = list((py / "room_correction").glob("*.py")) + list(py.glob("*.py"))
    for f in files:
        tops, rc = _imports(f)
        missing_rc = rc - shipped_rc
        assert not missing_rc, (f.name, missing_rc)
        for top in tops - {"room_correction"}:
            assert (top in sys.stdlib_module_names or top in PROVIDED
                    or top in own), (f.name, top)
