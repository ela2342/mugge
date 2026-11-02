"""Fakes at the process boundary for the F-439 / F-320 F unit tests.

FakePipeWire replaces ``subprocess.run`` inside ``app.pw_helpers`` and
answers ``pw-dump``, ``pw-cli enum-params`` and ``pw-cli s`` from an
in-memory Mult table.  Every ``pw-cli s`` value is recorded as the raw
string that would have reached PipeWire, so a test sees exactly what was
written ("nan", "1e-40", ...).

FakeGM is a GraphManager on a localhost TCP port speaking the real JSON
lines protocol, so the real GraphManagerClient is used end to end.  The
gate modes: ``open``, ``closed``, ``error`` (ok false) and ``silent``
(never answers, for timeouts).

Both work against the code at base ff55d0c8 and at the fix, so the defect
repro tests run unchanged on both.
"""

from __future__ import annotations

import json
import re
import socket
import socketserver
import subprocess
import threading

CONVOLVER_ID = 42
CONVOLVER_NODE_NAME = "pi4audio-convolver"
GAIN_NAMES = (
    "gain_left_hp", "gain_right_hp", "gain_sub1_lp", "gain_sub2_lp",
    "gain_hp_l", "gain_hp_r", "gain_iem_l", "gain_iem_r",
)

_SET_RE = re.compile(r'"(\w+):Mult"\s+(\S+)\s*\]')


class FakePipeWire:
    """In-memory convolver Mult table behind ``subprocess.run``."""

    def __init__(self, mults: dict[str, float] | None = None):
        self.mults = dict.fromkeys(GAIN_NAMES, 0.0)
        if mults:
            self.mults.update(mults)
        self.writes: list[tuple[str, str]] = []  # (gain name, raw value)
        self.calls: list[list[str]] = []
        self.on_write = None  # callable(name, raw) run after a write lands

    def zero_all(self) -> None:
        """What GM's close_gate does to the gains."""
        for name in self.mults:
            self.mults[name] = 0.0

    def nonzero_writes(self) -> list[tuple[str, str]]:
        return [(n, v) for n, v in self.writes if float(v) != 0.0]  # nan != 0

    def _done(self, args, stdout: str, kwargs, returncode: int = 0):
        out = stdout if kwargs.get("text") else stdout.encode()
        err = "" if kwargs.get("text") else b""
        return subprocess.CompletedProcess(args, returncode, out, err)

    def run(self, args, *a, **kwargs):
        args = list(args)
        self.calls.append(args)
        if args == ["pw-dump"]:
            params = []
            for name, mult in self.mults.items():
                params += [f"{name}:Mult", mult]
            dump = [{
                "id": CONVOLVER_ID,
                "type": "PipeWire:Interface:Node",
                "info": {
                    "props": {"node.name": CONVOLVER_NODE_NAME},
                    "params": {"Props": [{}, {"params": params}]},
                },
            }]
            return self._done(args, json.dumps(dump), kwargs)
        if args[:2] == ["pw-cli", "enum-params"] and args[3:] == ["Props"]:
            lines = []
            for name, mult in self.mults.items():
                lines.append(f'      String "{name}:Mult"')
                lines.append(f"      Float {mult:f}")
            return self._done(args, "\n".join(lines) + "\n", kwargs)
        if args[:2] == ["pw-cli", "s"] and args[3] == "Props":
            m = _SET_RE.search(args[4])
            assert m, f"unparsed pw-cli s payload: {args[4]!r}"
            name, raw = m.group(1), m.group(2)
            self.writes.append((name, raw))
            self.mults[name] = float(raw)
            if self.on_write:
                self.on_write(name, raw)
            return self._done(args, "", kwargs)
        raise AssertionError(f"FakePipeWire: unexpected command {args}")


class FakeGM:
    """GraphManager stand-in: JSON lines over TCP on 127.0.0.1."""

    def __init__(self, gate: str = "open", pw: FakePipeWire | None = None):
        self.gate = gate
        self.pw = pw  # close_gate zeroes its gains, like GM
        self.commands: list[str] = []
        self._release = threading.Event()
        fake = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                for raw in self.rfile:
                    cmd = json.loads(raw).get("cmd", "")
                    fake.commands.append(cmd)
                    reply = fake._reply(cmd)
                    if reply is None:  # silent: hold the request
                        fake._release.wait()
                        return
                    self.wfile.write((json.dumps(reply) + "\n").encode())

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self._server = Server(("127.0.0.1", 0), Handler)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)

    def close_gate(self) -> None:
        self.gate = "closed"
        if self.pw is not None:
            self.pw.zero_all()

    def _reply(self, cmd: str) -> dict | None:
        if self.gate == "silent":
            return None
        if self.gate == "error":
            return {"type": "response", "cmd": cmd, "ok": False,
                    "error": "internal error"}
        base = {"type": "response", "cmd": cmd, "ok": True}
        if cmd == "close_gate":
            self.close_gate()
            return base
        if cmd == "open_gate":
            self.gate = "open"
            return base
        if cmd in ("get_gate", "get_state"):
            return {**base, "gate_open": self.gate == "open",
                    "has_pending_gains": False, "venue": "test"}
        return base

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._release.set()
        self._server.shutdown()
        self._server.server_close()


def closed_port() -> int:
    """A localhost port with nothing listening (GM unreachable)."""
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port
