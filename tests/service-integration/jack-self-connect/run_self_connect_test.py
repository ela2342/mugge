#!/usr/bin/env python3
"""F-318 / US-173: jack.self-connect-mode = ignore-external on real PipeWire.

Starts a real PipeWire daemon (the production build, passed in by
nix/checks/jack-self-connect.nix) with stock daemon config, a stand-in
for the USBStreamer (support.null-audio-sink with the production node
name) and a stand-in for a GraphManager source node. A JACK client
(jack_client.py, PipeWire's libjack) loads the jack.conf.d fragments the
harness puts in $XDG_CONFIG_HOME/pipewire/jack.conf.d (the check copies
the deployed ones there), then:

  self_connect_external  jack_connect(own out_0 -> USBStreamer playback_FL)
                         returns 0 and creates no link
  self_connect_internal  jack_connect(own out_0 -> own in_0) returns 0 and
                         the link appears (also the sync point: the
                         external case is judged only after this link is
                         in the registry)
  native_link_jack_port  pw-link (GraphManager-style native link) from the
                         client's out_0 to USBStreamer playback_FR works
  native_link_gm_src     pw-link from the GM stand-in to playback_FL works
  disconnect_ignored     jack_disconnect(own out_0 -> playback_FR) returns
                         0 and the native link stays (judged after an
                         internal disconnect has taken effect).
                         Characterization of PipeWire 1.6.2 only, NOT a
                         safety layer: never cite it as protection. The
                         safety layers are the connect guard, the WP
                         no-bypass hook and GraphManager's link audit.
                         It is here to fail loudly if a PipeWire upgrade
                         changes check_connect for disconnects.

--mode policy   expects every case to pass.
--mode control  the check passes fragments with the self-connect line set
                to allow; self_connect_external and disconnect_ignored must
                fail (positive control: the call really links/unlinks).

Exit status: 0 if all cases passed, 1 otherwise, 2 if the stack did not
start (always a failure).
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import traceback

USBSTREAMER = "alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0"
GM_SRC = "jsc-gm-src"
CLIENT = "jsc-client"

# No session manager runs here, and without one an adapter node keeps
# port config mode "none" (no ports at all; audioadapter.c in 1.6.2).
# WirePlumber normally sets DSP mode. pipewire-jack hides ports without
# format.dsp, so the stand-ins configure DSP ports themselves.
DSP_PORTS = "{ mode = dsp monitor = false position = preserve }"
# The GM stand-in is a null sink too, so its only output ports are the
# monitor ports; GraphManager-style links start from those.
DSP_PORTS_MONITOR = "{ mode = dsp monitor = true position = preserve }"

STANDINS = {
    USBSTREAMER: {
        "media.class": "Audio/Sink",
        "api.alsa.path": "hw:USBStreamer,0",
        "node.group": "pi4audio.usbstreamer",
        "priority.session": "2000",
        "audio.channels": "2",
        "audio.position": "[ FL FR ]",
        "adapter.auto-port-config": DSP_PORTS,
    },
    GM_SRC: {
        "media.class": "Audio/Source/Virtual",
        "audio.channels": "2",
        "audio.position": "[ FL FR ]",
        "adapter.auto-port-config": DSP_PORTS_MONITOR,
    },
}

TIMEOUT = 15.0  # seconds, for every poll below


class CaseFailure(Exception):
    pass


def poll(what, fn, timeout=TIMEOUT, interval=0.1):
    deadline = time.monotonic() + timeout
    while True:
        v = fn()
        if v:
            return v
        if time.monotonic() > deadline:
            raise CaseFailure("timeout after %.0f s waiting for: %s"
                              % (timeout, what))
        time.sleep(interval)


class Stack:
    def __init__(self, args):
        self.args = args
        self.work = args.workdir
        self.run = os.path.join(self.work, "run")
        self.home = os.path.join(self.work, "home")
        os.makedirs(self.run, exist_ok=True)
        os.makedirs(self.home, exist_ok=True)
        self.env = dict(os.environ)
        self.env.update({
            "XDG_RUNTIME_DIR": self.run,
            "PIPEWIRE_RUNTIME_DIR": self.run,
            "HOME": self.home,
            "XDG_CONFIG_HOME": os.path.join(self.home, ".config"),
            "XDG_STATE_HOME": os.path.join(self.home, ".local", "state"),
        })
        self.env.pop("DBUS_SESSION_BUS_ADDRESS", None)
        self.pw = None
        self.client = None
        jack_d = os.path.join(self.env["XDG_CONFIG_HOME"], "pipewire",
                              "jack.conf.d")
        os.makedirs(jack_d, exist_ok=True)
        for src in args.jack_fragment:
            with open(src) as f, open(os.path.join(
                    jack_d, os.path.basename(src)), "w") as g:
                g.write(f.read())
        print("jack.conf.d: %s" % ", ".join(sorted(os.listdir(jack_d))))

    def start_pw(self):
        log = open(os.path.join(self.work, "pipewire.log"), "a")
        self.pw = subprocess.Popen([self.args.pipewire], env=self.env,
                                   stdout=log, stderr=log)
        poll("PipeWire answers pw-dump", lambda: self.dump() is not None)

    def start_client(self):
        env = dict(self.env)
        env["LD_LIBRARY_PATH"] = self.args.jack_lib
        self.client_log = open(os.path.join(self.work, "client.log"), "a")
        self.client = subprocess.Popen(
            [sys.executable, "-B", self.args.client, CLIENT], env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.client_log, text=True)
        ready = self.client.stdout.readline().split()
        if not ready or ready[0] != "ready":
            raise CaseFailure("JACK client did not start: %s" % ready)
        self.own_out, self.own_in = ready[1], ready[2]

    def ask(self, line):
        self.client.stdin.write(line + "\n")
        self.client.stdin.flush()
        answer = self.client.stdout.readline().rstrip("\n")
        if not answer:
            raise CaseFailure("JACK client exited on: %s" % line)
        return answer

    def jack_rc(self, verb, src, dst):
        answer = self.ask("%s %s %s" % (verb, src, dst)).split()
        if answer[0] != "rc":
            raise CaseFailure("%s: %s" % (verb, answer))
        return int(answer[1])

    def stop_all(self):
        if self.client and self.client.poll() is None:
            try:
                self.client.stdin.write("quit\n")
                self.client.stdin.flush()
                self.client.wait(5)
            except (OSError, subprocess.TimeoutExpired):
                self.client.kill()
        if self.pw and self.pw.poll() is None:
            self.pw.send_signal(signal.SIGTERM)
            try:
                self.pw.wait(5)
            except subprocess.TimeoutExpired:
                self.pw.kill()

    def tool(self, *argv):
        return subprocess.run(list(argv), env=self.env, capture_output=True,
                              text=True, timeout=TIMEOUT)

    # -- graph -----------------------------------------------------------

    def dump(self):
        try:
            r = subprocess.run([self.args.pw_dump], env=self.env,
                               capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode != 0 or not r.stdout.strip():
            return None
        try:
            return json.loads(r.stdout)
        except ValueError:
            return None

    def objects(self, kind):
        return [o for o in (self.dump() or [])
                if o.get("type") == "PipeWire:Interface:" + kind]

    def node_id(self, name):
        for n in self.objects("Node"):
            if n.get("info", {}).get("props", {}).get("node.name") == name:
                return n["id"]
        return None

    def port_id(self, node_name, port_name):
        nid = self.node_id(node_name)
        for p in self.objects("Port"):
            props = p.get("info", {}).get("props", {})
            if (props.get("node.id") == nid
                    and props.get("port.name") == port_name):
                return p["id"]
        return None

    def print_ports(self):
        print("PipeWire ports (node.id, direction, port.name, "
              "audio.channel, format.dsp):", flush=True)
        for p in self.objects("Port"):
            info = p.get("info", {})
            props = info.get("props", {})
            print("  %s %s %s %s %s" % (
                props.get("node.id"), info.get("direction"),
                props.get("port.name"), props.get("audio.channel"),
                props.get("format.dsp")), flush=True)

    def out_port_id(self, node_name, channel):
        nid = self.node_id(node_name)
        for p in self.objects("Port"):
            info = p.get("info", {})
            props = info.get("props", {})
            if (props.get("node.id") == nid
                    and info.get("direction") == "output"
                    and props.get("audio.channel") == channel):
                return p["id"]
        return None

    def link(self, out_port, in_port):
        for l in self.objects("Link"):
            info = l.get("info", {})
            if (info.get("output-port-id") == out_port
                    and info.get("input-port-id") == in_port):
                return l
        return None

    def links_between(self, out_node, in_node):
        a, b = self.node_id(out_node), self.node_id(in_node)
        return [l["info"] for l in self.objects("Link")
                if l.get("info", {}).get("output-node-id") == a
                and l.get("info", {}).get("input-node-id") == b]

    def create_standin(self, name):
        props = dict(STANDINS[name])
        props.update({"factory.name": "support.null-audio-sink",
                      "node.name": name, "object.linger": "true",
                      # The JACK port prefix comes from the description.
                      "node.description": name})
        spec = "{ " + " ".join('%s = "%s"' % (k, v)
                               if not v.startswith(("[", "{"))
                               else "%s = %s" % (k, v)
                               for k, v in props.items()) + " }"
        r = self.tool(self.args.pw_cli, "create-node", "adapter", spec)
        if r.returncode != 0:
            raise CaseFailure("pw-cli create-node %s: %s %s"
                              % (name, r.stdout, r.stderr))
        poll("stand-in %s exists" % name,
             lambda: self.node_id(name) is not None)

    def pw_link(self, out_port, in_port):
        r = self.tool(self.args.pw_link, str(out_port), str(in_port))
        if r.returncode != 0:
            raise CaseFailure("pw-link %s %s: rc %d %s %s"
                              % (out_port, in_port, r.returncode,
                                 r.stdout, r.stderr))
        poll("native link %s -> %s" % (out_port, in_port),
             lambda: self.link(out_port, in_port))


class Cases:
    def __init__(self, stack):
        self.s = stack
        self.results = []

    def run(self, name, fn):
        try:
            fn()
            self.results.append((name, True, ""))
            print("PASS %s" % name, flush=True)
        except CaseFailure as e:
            self.results.append((name, False, str(e)))
            print("FAIL %s: %s" % (name, e), flush=True)

    def setup(self):
        s = self.s
        answer = s.ask("ports .").split(" ", 1)
        names = answer[1].split("|") if len(answer) > 1 else []
        usb = sorted(n for n in names if n.startswith(USBSTREAMER + ":"))
        print("JACK input ports: %s" % names)
        fl = [n for n in usb if n.endswith("playback_FL")]
        fr = [n for n in usb if n.endswith("playback_FR")]
        if len(fl) != 1 or len(fr) != 1:
            s.print_ports()
            raise CaseFailure("USBStreamer stand-in JACK ports not found: %s"
                              % usb)
        self.jack_fl, self.jack_fr = fl[0], fr[0]
        self.p_out = poll("client out_0 port",
                          lambda: s.port_id(CLIENT, "out_0"))
        self.p_in = poll("client in_0 port",
                         lambda: s.port_id(CLIENT, "in_0"))
        self.p_fl = s.port_id(USBSTREAMER, "playback_FL")
        self.p_fr = s.port_id(USBSTREAMER, "playback_FR")
        try:
            self.p_gm = poll("GM stand-in FL output port",
                             lambda: s.out_port_id(GM_SRC, "FL"))
        except CaseFailure:
            self.p_gm = None
        if None in (self.p_fl, self.p_fr, self.p_gm):
            s.print_ports()
            raise CaseFailure("stand-in ports missing: fl %s fr %s gm %s"
                              % (self.p_fl, self.p_fr, self.p_gm))

    def all(self):
        s = self.s
        ext_rc = s.jack_rc("connect", s.own_out, self.jack_fl)
        print("jack_connect %s -> %s: rc %d" % (s.own_out, self.jack_fl,
                                                 ext_rc))

        def internal():
            rc = s.jack_rc("connect", s.own_out, s.own_in)
            if rc != 0:
                raise CaseFailure("internal jack_connect rc %d" % rc)
            poll("internal link out_0 -> in_0",
                 lambda: s.link(self.p_out, self.p_in))
        self.run("self_connect_internal", internal)

        def external():
            if ext_rc != 0:
                raise CaseFailure("jack_connect returned %d, expected 0"
                                  % ext_rc)
            if not s.link(self.p_out, self.p_in):
                raise CaseFailure("no sync point: internal link missing")
            links = s.links_between(CLIENT, USBSTREAMER)
            if links:
                raise CaseFailure("jack_connect linked the client to the "
                                  "USBStreamer: %s" % links)
        self.run("self_connect_external", external)

        self.run("native_link_jack_port",
                 lambda: s.pw_link(self.p_out, self.p_fr))
        self.run("native_link_gm_src",
                 lambda: s.pw_link(self.p_gm, self.p_fl))

        # Characterizes PipeWire 1.6.2 check_connect for disconnects.
        # NOT a safety layer and must not be cited as protection (the
        # layers are the connect guard, the WP hook and GM's audit). If a
        # PipeWire upgrade changes this, the case fails loudly on purpose.
        def disconnect():
            if not s.link(self.p_out, self.p_fr):
                raise CaseFailure("native link out_0 -> FR missing")
            rc = s.jack_rc("disconnect", s.own_out, self.jack_fr)
            if rc != 0:
                raise CaseFailure("jack_disconnect returned %d" % rc)
            rc = s.jack_rc("disconnect", s.own_out, s.own_in)
            if rc != 0:
                raise CaseFailure("internal jack_disconnect rc %d" % rc)
            poll("internal link removed",
                 lambda: s.link(self.p_out, self.p_in) is None)
            if not s.link(self.p_out, self.p_fr):
                raise CaseFailure("jack_disconnect removed the native "
                                  "link out_0 -> FR")
        self.run("disconnect_ignored", disconnect)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("policy", "control"), required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--jack-fragment", action="append", required=True)
    ap.add_argument("--jack-lib", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--pipewire", default="pipewire")
    ap.add_argument("--pw-dump", default="pw-dump")
    ap.add_argument("--pw-cli", default="pw-cli")
    ap.add_argument("--pw-link", default="pw-link")
    args = ap.parse_args()

    stack = Stack(args)
    cases = Cases(stack)
    try:
        stack.start_pw()
        for name in STANDINS:
            stack.create_standin(name)
        stack.start_client()
        cases.setup()
    except CaseFailure as e:
        print("SETUP FAILED: %s" % e, flush=True)
        stack.stop_all()
        return 2
    except Exception:
        traceback.print_exc()
        stack.stop_all()
        return 2
    try:
        cases.all()
    finally:
        stack.stop_all()
    failed = [r for r in cases.results if not r[1]]
    print("RESULT %s: %d passed, %d failed"
          % (args.mode, len(cases.results) - len(failed), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
