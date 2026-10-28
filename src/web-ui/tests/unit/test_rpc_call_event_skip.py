"""F-394 AC (ii): _rpc_call must skip GM push events on the RPC socket.

GraphManager broadcasts ``{"type": "event", ...}`` lines (link_created etc.)
on every client connection, interleaved with command responses. Taking the
first line as the reply made set_mode "return" an event, and several lines
in one recv() made later calls fail to parse and return {}.
"""

import json
import socket
import sys
import threading
from pathlib import Path

_tests_dir = str(Path(__file__).resolve().parent.parent)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from fixtures.backend import _rpc_call  # noqa: E402

EVENT = b'{"type":"event","event":"link_created","output_node":"Mixxx"}\n'
SET_MODE_OK = b'{"type":"response","cmd":"set_mode","ok":true,"epoch":7}\n'
SET_MODE = {"cmd": "set_mode", "mode": "dj"}


def _serve_once(chunks):
    """Fake GM: accept one client, read its command, send chunks, close."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)

    def run():
        conn, _ = srv.accept()
        with conn:
            conn.recv(4096)
            for chunk in chunks:
                conn.sendall(chunk)
        srv.close()

    threading.Thread(target=run, daemon=True).start()
    return srv.getsockname()[1]


def _call(chunks, cmd=SET_MODE, timeout=2.0):
    return _rpc_call("127.0.0.1", _serve_once(chunks), cmd, timeout)


def test_response_only():
    assert _call([SET_MODE_OK]) == json.loads(SET_MODE_OK)


def test_event_before_response_is_skipped():
    assert _call([EVENT, SET_MODE_OK]) == json.loads(SET_MODE_OK)


def test_events_and_response_in_one_chunk():
    assert _call([EVENT + EVENT + SET_MODE_OK]) == json.loads(SET_MODE_OK)


def test_response_split_across_chunks():
    assert _call([EVENT + SET_MODE_OK[:12], SET_MODE_OK[12:]]) == json.loads(SET_MODE_OK)


def test_response_for_other_cmd_is_skipped():
    other = b'{"type":"response","cmd":"get_state","ok":true,"mode":"standby"}\n'
    assert _call([other, SET_MODE_OK]) == json.loads(SET_MODE_OK)


def test_events_only_returns_empty():
    assert _call([EVENT, EVENT]) == {}


def test_bad_json_returns_empty():
    assert _call([b"not json\n"]) == {}


def test_no_response_before_deadline_returns_empty():
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    try:
        # Connection is accepted by the backlog but never answered.
        assert _rpc_call("127.0.0.1", srv.getsockname()[1], SET_MODE, 0.3) == {}
    finally:
        srv.close()
