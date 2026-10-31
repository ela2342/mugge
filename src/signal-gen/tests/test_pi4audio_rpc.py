"""Tests for scripts/pi4audio-rpc against a fake RPC server (F-341, QE 315d3d5e).

The fake mimics signal-gen's RPC server: newline-delimited JSON on
127.0.0.1, one client served at a time, state broadcasts interleaved with
the reply. No Pi, no real signal-gen.
"""

import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

# PI4AUDIO_RPC: test a packaged copy instead (nix/checks/pi4audio-rpc.nix).
SCRIPT = Path(os.environ.get("PI4AUDIO_RPC")
              or Path(__file__).resolve().parent.parent / "scripts" / "pi4audio-rpc")

BROADCAST = json.dumps(
    {"type": "state", "cmd": "status", "ok": True, "playing": False,
     "signal": "silence", "freq": 0.0, "channels": [], "level_dbfs": -120.0,
     "elapsed": 0.0, "samples_generated": 0},
    separators=(",", ":"),
)
EVENT = '{"type":"event","event":"device_added"}'
STATUS_ACK = (
    '{"type":"ack","cmd":"status","ok":true,"playing":false,"signal":"silence",'
    '"freq":0.0,"channels":[],"level_dbfs":-120.0,"elapsed":0.0,'
    '"samples_generated":0,"max_level_dbfs":-20.0,"max_level_linear":0.1}'
)
ERROR_ACK = '{"type":"ack","cmd":"play","ok":false,"error":"level_dbfs -10 exceeds cap -20"}'
# rpc.rs handle_status serialize-failure fallback: no cmd field.
FALLBACK_ACK = '{"type":"ack","ok":false,"error":"internal: failed to serialize status"}'
# A broadcast whose string field contains ack-like text (t7).
DECOY = json.dumps(
    {"type": "state", "cmd": "status", "signal": 'x "type":"ack","ok":true'},
    separators=(",", ":"),
)


class FakeServer:
    """One-client-at-a-time line server, like signal-gen's accept loop.

    For each client: read one request line, send `before` lines, then
    `reply` (if not None), then keep sending broadcasts every 50 ms until the
    client closes. The time each client's EOF was seen is recorded.
    """

    def __init__(self, before=(), reply=None, hold_first=False, close_after=False):
        self.before = list(before)
        self.reply = reply
        self.hold_first = hold_first
        self.close_after = close_after
        self.requests = []
        self.eof_times = []
        self.release_first = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.port = self.sock.getsockname()[1]
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        self.sock.settimeout(0.05)
        first = True
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            with conn:
                if first and self.hold_first:
                    first = False
                    # Serve nothing; hold until released (a "busy" client).
                    self.release_first.wait(10)
                    continue
                first = False
                self._handle(conn)

    def _handle(self, conn):
        conn.settimeout(0.05)
        buf = b""
        while b"\n" not in buf and not self.stop.is_set():
            try:
                chunk = conn.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                self.eof_times.append(time.monotonic())
                return
            buf += chunk
        self.requests.append(buf.split(b"\n", 1)[0].decode())
        try:
            for line in self.before:
                conn.sendall(line.encode() + b"\n")
            if self.reply is not None:
                conn.sendall(self.reply.encode() + b"\n")
            if self.close_after:
                return
            while not self.stop.is_set():
                try:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                except socket.timeout:
                    pass
                conn.sendall(BROADCAST.encode() + b"\n")
                time.sleep(0.05)
        except OSError:
            pass
        self.eof_times.append(time.monotonic())

    def close(self):
        self.stop.set()
        self.release_first.set()
        self.sock.close()
        self.thread.join(2)


@pytest.fixture
def server_factory():
    servers = []

    def make(**kw):
        s = FakeServer(**kw)
        servers.append(s)
        return s

    yield make
    for s in servers:
        s.close()


def run(port, payload='{"cmd":"status"}', *extra, timeout=10):
    t0 = time.monotonic()
    p = subprocess.run(
        [str(SCRIPT), str(port), payload, *extra],
        capture_output=True, text=True, timeout=timeout,
    )
    return p, time.monotonic() - t0


def leftover_processes(port):
    """Script processes still alive for this port (R4: nobody holds the socket)."""
    out = subprocess.run(["ps", "-A", "-o", "pid=,command="],
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines()
            if "pi4audio-rpc" in l and f"--connected-part {port} " in l]


def test_t1_status_ack_after_broadcasts_and_event(server_factory):
    srv = server_factory(before=[BROADCAST] * 5 + [EVENT, BROADCAST], reply=STATUS_ACK)
    p, _ = run(srv.port)
    assert p.returncode == 0, p.stderr
    assert p.stdout == STATUS_ACK + "\n"
    assert srv.requests == ['{"cmd":"status"}']


def test_t2_ok_false_ack(server_factory):
    srv = server_factory(before=[BROADCAST], reply=ERROR_ACK)
    p, _ = run(srv.port, '{"cmd":"play"}')
    assert p.returncode == 1
    assert p.stdout == ERROR_ACK + "\n"


def test_t3_fallback_ack_without_cmd_is_a_failure(server_factory):
    srv = server_factory(before=[BROADCAST], reply=FALLBACK_ACK)
    p, _ = run(srv.port)
    assert p.returncode == 1
    assert p.stdout == FALLBACK_ACK + "\n"


def test_t4_never_answers_times_out_and_releases_the_socket(server_factory):
    srv = server_factory(before=[BROADCAST] * 3, reply=None)
    p, elapsed = run(srv.port)  # default deadline, 3 s
    assert p.returncode == 124
    assert p.stdout == ""
    assert "within 3 s" in p.stderr
    assert 3.0 <= elapsed < 4.5  # slack for a loaded CI runner (QE e3e9bbe6 NB)
    end = time.monotonic()
    deadline = time.monotonic() + 0.5
    while not srv.eof_times and time.monotonic() < deadline:
        time.sleep(0.02)
    assert srv.eof_times, "server never saw EOF: the socket is still held"
    assert srv.eof_times[0] <= end + 0.5
    assert leftover_processes(srv.port) == []


def test_t5_nothing_listening_fails_fast():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()  # bound once, now free: nothing listens
    p, elapsed = run(port)
    assert p.returncode == 2
    assert elapsed < 1.0
    assert "cannot connect" in p.stderr


def test_t6_busy_server_times_out_then_recovers(server_factory):
    srv = server_factory(reply=STATUS_ACK, hold_first=True)
    busy = socket.create_connection(("127.0.0.1", srv.port))
    try:
        time.sleep(0.2)  # the fake has accepted and is holding it
        p, _ = run(srv.port, '{"cmd":"status"}', "1")
        assert p.returncode == 124
        assert leftover_processes(srv.port) == []
    finally:
        busy.close()
        srv.release_first.set()
    p, _ = run(srv.port, '{"cmd":"status"}', "2")
    assert p.returncode == 0, p.stderr
    assert p.stdout == STATUS_ACK + "\n"


def test_t7_ack_text_inside_a_broadcast_is_not_the_reply(server_factory):
    srv = server_factory(before=[DECOY, BROADCAST], reply=ERROR_ACK)
    p, _ = run(srv.port, '{"cmd":"play"}')
    assert p.returncode == 1
    assert p.stdout == ERROR_ACK + "\n"


def test_server_closes_before_ack(server_factory):
    srv = server_factory(before=[BROADCAST], reply=None, close_after=True)
    p, elapsed = run(srv.port, '{"cmd":"status"}', "2")
    assert p.returncode == 3
    assert elapsed < 1.0
    assert "closed the connection" in p.stderr


@pytest.mark.parametrize("args", [
    [], ["4001"], ["x", "{}"], ["0", "{}"], ["70000", "{}"],
    ["4001", ""], ["4001", "{}\n{}"], ["4001", "{}", "soon"],
])
def test_usage_errors(args):
    p = subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, timeout=5)
    assert p.returncode == 64
