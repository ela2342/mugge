#!/usr/bin/env python3
"""Minimal JACK client for the jack.self-connect-mode test (ctypes).

Loads libjack (PipeWire's, via LD_LIBRARY_PATH from the harness), opens a
client, registers one output and one input port and activates. Then reads
commands from stdin, one per line, and answers on stdout:

  ports <regex>        -> "ports <name>|<name>|..." (input ports only)
  connect <src> <dst>  -> "rc <jack_connect return value>"
  disconnect <s> <d>   -> "rc <jack_disconnect return value>"
  quit

On start it prints "ready <out port> <in port>".
"""

import ctypes
import sys

JackPortIsInput = 0x1
JackPortIsOutput = 0x2
JackNoStartServer = 0x01
AUDIO = b"32 bit float mono audio"


def main():
    name = sys.argv[1].encode()
    jack = ctypes.CDLL("libjack.so.0")
    jack.jack_client_open.restype = ctypes.c_void_p
    jack.jack_client_open.argtypes = [ctypes.c_char_p, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int)]
    jack.jack_port_register.restype = ctypes.c_void_p
    jack.jack_port_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                        ctypes.c_char_p, ctypes.c_ulong,
                                        ctypes.c_ulong]
    jack.jack_port_name.restype = ctypes.c_char_p
    jack.jack_port_name.argtypes = [ctypes.c_void_p]
    jack.jack_activate.argtypes = [ctypes.c_void_p]
    jack.jack_get_ports.restype = ctypes.POINTER(ctypes.c_char_p)
    jack.jack_get_ports.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                    ctypes.c_char_p, ctypes.c_ulong]
    jack.jack_free.argtypes = [ctypes.c_void_p]
    for fn in (jack.jack_connect, jack.jack_disconnect):
        fn.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        fn.restype = ctypes.c_int

    status = ctypes.c_int(0)
    client = jack.jack_client_open(name, JackNoStartServer,
                                   ctypes.byref(status))
    if not client:
        print("error jack_client_open status 0x%x" % status.value, flush=True)
        return 2
    out = jack.jack_port_register(client, b"out_0", AUDIO,
                                  JackPortIsOutput, 0)
    inp = jack.jack_port_register(client, b"in_0", AUDIO,
                                  JackPortIsInput, 0)
    if not out or not inp:
        print("error jack_port_register", flush=True)
        return 2
    if jack.jack_activate(client) != 0:
        print("error jack_activate", flush=True)
        return 2
    print("ready %s %s" % (jack.jack_port_name(out).decode(),
                           jack.jack_port_name(inp).decode()), flush=True)

    for line in sys.stdin:
        cmd = line.split()
        if not cmd:
            continue
        if cmd[0] == "quit":
            break
        if cmd[0] == "ports":
            arr = jack.jack_get_ports(client, cmd[1].encode(), None,
                                      JackPortIsInput)
            names = []
            if arr:
                i = 0
                while arr[i]:
                    names.append(arr[i].decode())
                    i += 1
                jack.jack_free(arr)
            print("ports " + "|".join(names), flush=True)
        elif cmd[0] in ("connect", "disconnect"):
            fn = jack.jack_connect if cmd[0] == "connect" \
                else jack.jack_disconnect
            print("rc %d" % fn(client, cmd[1].encode(), cmd[2].encode()),
                  flush=True)
        else:
            print("error unknown command", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
