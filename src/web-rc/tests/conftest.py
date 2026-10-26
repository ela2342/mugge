"""Shared fixtures for the web-rc tests (US-179)."""

import functools
import http.server
import threading
from pathlib import Path

import pytest

WEB_RC_ROOT = Path(__file__).resolve().parent.parent


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
