"""Shared fixtures for the web-rc tests (US-179)."""

import functools
import http.server
import importlib.util
import threading
from pathlib import Path

import pytest

WEB_RC_ROOT = Path(__file__).resolve().parent.parent
SRC = WEB_RC_ROOT.parent


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".wasm": "application/wasm",
    }

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="session")
def web_rc_url():
    """Serve src/web-rc as static files on an ephemeral localhost port."""
    handler = functools.partial(_QuietHandler, directory=str(WEB_RC_ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def room_correction_root():
    """The src/room-correction the tests run against.

    The one room_correction resolves to on PYTHONPATH (the read-only #66
    reference copy, until #66 is on main), else the repository's.
    """
    spec = importlib.util.find_spec("room_correction")
    if spec is not None and spec.origin:
        return Path(spec.origin).resolve().parents[1]
    return SRC / "room-correction"


def build_site_module(tmp_path_factory):
    """build_site.py, pointed at room_correction_root().

    For a root outside the repository it reads from a tree of symlinks
    (src/room-correction -> that root, src/web-ui and src/web-rc -> the
    repository's), so the manifest's source paths keep their form.
    Returns (module, repository root the manifest's sources resolve in).
    """
    spec = importlib.util.spec_from_file_location(
        "build_site", WEB_RC_ROOT / "build_site.py")
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    rc = room_correction_root()
    if rc == (SRC / "room-correction").resolve():
        return bs, SRC.parent
    repo = tmp_path_factory.mktemp("shared-tree")
    (repo / "src").mkdir()
    (repo / "src" / "room-correction").symlink_to(rc)
    (repo / "src" / "web-ui").symlink_to(SRC / "web-ui")
    (repo / "src" / "web-rc").symlink_to(WEB_RC_ROOT)
    bs.SRC = repo / "src"
    bs.WEB_RC = repo / "src" / "web-rc"
    return bs, repo
