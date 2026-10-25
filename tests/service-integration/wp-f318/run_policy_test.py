#!/usr/bin/env python3
"""F-318 service-integration test: WirePlumber never auto-links playback.

Starts a real PipeWire and WirePlumber (the production builds and the
production WirePlumber XDG_DATA_DIRS, passed in by
nix/checks/wireplumber-no-bypass.nix), creates stand-ins for the protected
nodes, runs real clients against them and inspects the graph with pw-dump.

Stand-ins (support.null-audio-sink, created with pw-cli). Each carries
every property the policy script matches on:
  USBStreamer  node.name   = alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0
               media.class = Audio/Sink
               api.alsa.path = hw:USBStreamer,0
               node.group  = pi4audio.usbstreamer
               priority.session = 2000 (as 21-usbstreamer-playback.conf)
  Convolver    node.name   = pi4audio-convolver, media.class = Audio/Sink
  UMIK-1       node.name   = f318-umik-standin,
               media.class = Audio/Source/Virtual (a capture source)
  GM source    node.name   = f318-gm-src, media.class = Audio/Source/Virtual
               (stands in for pi4audio-convolver-out in a GM-style link)

No PipeWire production config is loaded: the 20/21/30 fragments need the
real ALSA device and FIR files. Only WirePlumber runs its production
configuration; that is the component under test.

Absence of a link is only asserted after positive evidence that
WirePlumber handled the stream (its deny line, or for --mode control the
appearance of the link). Every wait polls with a stated timeout; there are
no fixed sleeps.

--mode policy   expects every case to pass.
--mode control  disables custom.mugge-no-bypass through a user config
                fragment (negative control). The deny cases must fail.

Exit status: 0 if all cases passed, 1 otherwise, 2 if the stack did not
start (always a failure).
"""

import argparse
import json
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import time
import traceback
import wave

USBSTREAMER = "alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0"
CONVOLVER = "pi4audio-convolver"
UMIK = "f318-umik-standin"
GM_SRC = "f318-gm-src"
PROTECTED = (USBSTREAMER, CONVOLVER)

STANDINS = {
    USBSTREAMER: {
        "media.class": "Audio/Sink",
        "api.alsa.path": "hw:USBStreamer,0",
        "node.group": "pi4audio.usbstreamer",
        "priority.session": "2000",
        "audio.channels": "2",
        "audio.position": "[ FL FR ]",
    },
    CONVOLVER: {
        "media.class": "Audio/Sink",
        "audio.channels": "2",
        "audio.position": "[ FL FR ]",
    },
    UMIK: {
        "media.class": "Audio/Source/Virtual",
        "audio.channels": "1",
        "audio.position": "[ MONO ]",
    },
    GM_SRC: {
        "media.class": "Audio/Source/Virtual",
        "audio.channels": "2",
        "audio.position": "[ FL FR ]",
    },
}

TIMEOUT = 15.0  # seconds, for every poll below
LOAD_LINE = "F-318: mugge-no-bypass loaded"
DEFAULT_LINE = "is not eligible as default.audio.sink"


class CaseFailure(Exception):
    pass


class Stack:
    def __init__(self, args, workdir):
        self.args = args
        self.work = workdir
        self.run = os.path.join(workdir, "run")
        self.home = os.path.join(workdir, "home")
        os.makedirs(self.run, exist_ok=True)
        os.makedirs(self.home, exist_ok=True)
        self.env = dict(os.environ)
        self.env.update({
            "XDG_RUNTIME_DIR": self.run,
            "PIPEWIRE_RUNTIME_DIR": self.run,
            "PULSE_RUNTIME_PATH": os.path.join(self.run, "pulse"),
            "HOME": self.home,
            "XDG_CONFIG_HOME": os.path.join(self.home, ".config"),
            "XDG_STATE_HOME": os.path.join(self.home, ".local", "state"),
        })
        self.env.pop("DBUS_SESSION_BUS_ADDRESS", None)
        self.wp_env = dict(self.env)
        self.wp_env["XDG_DATA_DIRS"] = args.wp_data_dirs
        # Base level N is the WirePlumber default; s-linking info and the
        # dispatcher trace give the hook order for case_hook_order.
        self.wp_env["WIREPLUMBER_DEBUG"] = (
            "N,s-linking:I,s-mugge-no-bypass:I,wp-event-dispatcher:T")
        self.pw = None
        self.wp = None
        self.pulse = None
        self.wp_log_path = os.path.join(workdir, "wireplumber.log")
        self.wp_starts = 0
        self.children = []
        if args.mode == "control":
            d = os.path.join(self.env["XDG_CONFIG_HOME"], "wireplumber",
                             "wireplumber.conf.d")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "99-f318-negative-control.conf"),
                      "w") as f:
                f.write("wireplumber.profiles = {\n  main = {\n"
                        "    custom.mugge-no-bypass = disabled\n  }\n}\n")

    # -- processes -------------------------------------------------------

    def start_pw(self):
        log = open(os.path.join(self.work, "pipewire.log"), "a")
        self.pw = subprocess.Popen([self.args.pipewire], env=self.env,
                                   stdout=log, stderr=log)
        poll("PipeWire answers pw-dump", lambda: self.dump() is not None)

    def start_wp(self):
        log = open(self.wp_log_path, "a")
        log.write("\n==== wireplumber start %d ====\n" % (self.wp_starts + 1))
        log.flush()
        self.wp = subprocess.Popen([self.args.wireplumber], env=self.wp_env,
                                   stdout=log, stderr=log)
        self.wp_starts += 1
        poll("WirePlumber created the default metadata",
             lambda: self.wp_alive() and self.has_metadata("default"))
        if self.args.mode == "policy":
            poll("WirePlumber logged the F-318 load line",
                 lambda: self.wp_log().count(LOAD_LINE) >= self.wp_starts)

    def wp_alive(self):
        if self.wp.poll() is not None:
            raise CaseFailure("WirePlumber exited with status %s"
                              % self.wp.returncode)
        return True

    def start_pulse(self):
        log = open(os.path.join(self.work, "pipewire-pulse.log"), "a")
        self.pulse = subprocess.Popen([self.args.pipewire_pulse],
                                      env=self.env, stdout=log, stderr=log)
        poll("pipewire-pulse socket",
             lambda: os.path.exists(os.path.join(self.run, "pulse",
                                                 "native")))

    def stop(self, proc):
        if proc and proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

    def stop_all(self):
        for p in self.children:
            self.stop(p)
        self.stop(self.pulse)
        self.stop(self.wp)
        self.stop(self.pw)

    def spawn(self, argv, log=None):
        out = open(log, "a") if log else subprocess.DEVNULL
        p = subprocess.Popen(argv, env=self.env, stdout=out,
                             stderr=subprocess.STDOUT)
        self.children.append(p)
        return p

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

    def nodes(self):
        return [o for o in (self.dump() or [])
                if o.get("type") == "PipeWire:Interface:Node"]

    def node(self, **match):
        for n in self.nodes():
            props = n.get("info", {}).get("props", {})
            if all(props.get(k) == v for k, v in match.items()):
                return n
        return None

    def links(self):
        return [o["info"] for o in (self.dump() or [])
                if o.get("type") == "PipeWire:Interface:Link"]

    def links_of(self, node_id):
        return [l for l in self.links()
                if node_id in (l.get("output-node-id"),
                               l.get("input-node-id"))]

    def metadata(self, name):
        for o in self.dump() or []:
            if (o.get("type") == "PipeWire:Interface:Metadata"
                    and o.get("props", {}).get("metadata.name") == name):
                return o.get("metadata", [])
        return None

    def has_metadata(self, name):
        # pw-dump leaves out metadata objects without entries, and
        # "default" stays empty until there is a sink; pw-cli lists it.
        r = self.tool(self.args.pw_cli, "ls", "Metadata")
        return 'metadata.name = "%s"' % name in r.stdout

    def default_sink(self):
        for e in self.metadata("default") or []:
            if e.get("subject") == 0 and e.get("key") == "default.audio.sink":
                v = e.get("value")
                return v.get("name") if isinstance(v, dict) else v
        return None

    def wp_log(self):
        with open(self.wp_log_path, errors="replace") as f:
            return f.read()

    def create_standin(self, name):
        props = dict(STANDINS[name])
        props.update({"factory.name": "support.null-audio-sink",
                      "node.name": name, "object.linger": "true"})
        spec = "{ " + " ".join('%s = "%s"' % (k, v) if not v.startswith("[")
                               else "%s = %s" % (k, v)
                               for k, v in props.items()) + " }"
        r = self.tool(self.args.pw_cli, "create-node", "adapter", spec)
        if r.returncode != 0:
            raise CaseFailure("pw-cli create-node %s: %s %s"
                              % (name, r.stdout, r.stderr))
        poll("stand-in %s exists" % name,
             lambda: self.node(**{"node.name": name}) is not None)

    def destroy_node(self, name):
        n = self.node(**{"node.name": name})
        r = self.tool(self.args.pw_cli, "destroy", str(n["id"]))
        if r.returncode != 0:
            raise CaseFailure("pw-cli destroy: %s %s" % (r.stdout, r.stderr))
        poll("%s removed" % name,
             lambda: self.node(**{"node.name": name}) is None)


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


def write_silence(path, seconds=60):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(struct.pack("<hh", 0, 0) * (48000 * seconds))


# -- cases --------------------------------------------------------------

class Cases:
    def __init__(self, stack, silence):
        self.s = stack
        self.silence = silence
        self.gm_link = None

    def deny_line(self, field, value, target=None):
        pat = '%s="%s"' % (field, value)
        for line in self.s.wp_log().splitlines():
            if "F-318: denied auto-link" in line and pat in line:
                if target is None or 'to target node.name="%s"' % target \
                        in line:
                    return line
        return None

    def play(self, name, target=None, extra=(), linger=False):
        """pw-play a silent file. A denied stream gets "no target node
        available" from WirePlumber and pw-play exits; linger=True keeps
        the stream (WirePlumber sends no error to lingering nodes), for
        cases that act on the stream after the deny."""
        props = 'node.name = "%s"' % name
        if linger:
            props += " node.linger = true"
        argv = [self.s.args.pw_play, "-P", "{ %s }" % props]
        if target:
            argv += ["--target", target]
        argv += list(extra) + [self.silence]
        return self.s.spawn(argv, log=os.path.join(self.s.work,
                                                   name + ".log"))

    def expect_denied(self, name, target, field="node.name"):
        """The stream gets a deny line naming target, then has no links."""
        line = poll("deny line for %s=%s -> %s" % (field, name, target),
                    lambda: self.deny_line(field, name, target)
                    or self.linked_by(field, name))
        if not isinstance(line, str):
            raise CaseFailure("WirePlumber linked %s=%s: %s"
                              % (field, name, line))
        # The stream may be gone already (its client quit on the error),
        # so check the node.id from the deny line as well.
        m = re.search(r'node\.id="(\d+)"', line)
        ids = {int(m.group(1))} if m else set()
        n = self.s.node(**{field: name})
        if n:
            ids.add(n["id"])
        links = [l for i in ids for l in self.s.links_of(i)]
        if links:
            raise CaseFailure("%s=%s has %d links after deny: %s"
                              % (field, name, len(links), links))
        return line

    def linked_by(self, field, name):
        n = self.s.node(**{field: name})
        if not n:
            return None
        links = self.s.links_of(n["id"])
        return links or None

    def stop(self, p):
        self.s.stop(p)

    # 1
    def case_load_line(self):
        if self.s.wp_log().count(LOAD_LINE) < 1:
            raise CaseFailure("load line %r not in the WirePlumber log"
                              % LOAD_LINE)

    # 2
    def case_play_default(self):
        p = self.play("f318-play-default")
        try:
            line = self.expect_denied("f318-play-default", None)
            for field in ("node.id=", "application.name=",
                          "application.process.binary=",
                          "application.process.id=",
                          "to target node.name="):
                if field not in line:
                    raise CaseFailure("deny line lacks %s: %s"
                                      % (field, line))
            if 'pipewire.sec.pid="nil"' in line:
                raise CaseFailure("deny line has no pipewire.sec.pid: %s"
                                  % line)
            if 'application.process.binary="pw-play"' not in line \
                    and 'application.process.binary="pw-cat"' not in line:
                raise CaseFailure("deny line does not name pw-play: %s"
                                  % line)
            if not re.search(r'to target node\.name="(%s|%s)"'
                             % (re.escape(USBSTREAMER), re.escape(CONVOLVER)),
                             line):
                raise CaseFailure("deny line names no protected target: %s"
                                  % line)
            poll("pw-play quit after the deny", lambda: p.poll() is not None)
            with open(os.path.join(self.s.work, "f318-play-default.log"),
                      errors="replace") as f:
                out = f.read()
            if "no target node available" not in out:
                raise CaseFailure("pw-play was not told why: %r" % out)
        finally:
            self.stop(p)

    # 3
    def case_play_target_usbstreamer(self):
        p = self.play("f318-play-usb", USBSTREAMER)
        try:
            self.expect_denied("f318-play-usb", USBSTREAMER)
        finally:
            self.stop(p)

    # 4
    def case_play_target_convolver(self):
        p = self.play("f318-play-conv", CONVOLVER)
        try:
            self.expect_denied("f318-play-conv", CONVOLVER)
        finally:
            self.stop(p)

    # 5
    def case_metadata_move(self):
        p = self.play("f318-play-move", CONVOLVER, linger=True)
        try:
            self.expect_denied("f318-play-move", CONVOLVER)
            n = self.s.node(**{"node.name": "f318-play-move"})
            usb = self.s.node(**{"node.name": USBSTREAMER})
            r = self.s.tool(self.s.args.pw_metadata, str(n["id"]),
                            "target.object",
                            str(usb["info"]["props"]["object.serial"]))
            if r.returncode != 0:
                raise CaseFailure("pw-metadata: %s %s" % (r.stdout, r.stderr))
            self.expect_denied("f318-play-move", USBSTREAMER)
        finally:
            self.stop(p)

    # 6
    def case_pw_loopback(self):
        p = self.s.spawn([
            self.s.args.pw_loopback,
            "--capture-props", '{ node.name = "f318-loop-in" }',
            "--playback-props", '{ node.name = "f318-loop-out" }'])
        try:
            self.expect_denied("f318-loop-out", None)
        finally:
            self.stop(p)

    # 7
    def case_pulse_paplay(self):
        if not self.s.pulse:
            self.s.start_pulse()
        p = self.s.spawn([self.s.args.paplay, "--client-name=f318-paplay",
                          self.silence])
        try:
            self.expect_denied("f318-paplay", None, field="application.name")
        finally:
            self.stop(p)

    # 8
    def case_capture_source_links(self):
        rec = os.path.join(self.s.work, "umik.wav")
        p = self.s.spawn([self.s.args.pw_record, "-P",
                          '{ node.name = "f318-rec-umik" }',
                          "--target", UMIK, rec])
        try:
            umik = self.s.node(**{"node.name": UMIK})
            poll("capture stream linked from the UMIK stand-in",
                 lambda: any(l.get("output-node-id") == umik["id"]
                             for l in self.linked_by("node.name",
                                                     "f318-rec-umik") or []))
        finally:
            self.stop(p)

    # 9
    def case_monitor_capture_links(self):
        rec = os.path.join(self.s.work, "monitor.wav")
        p = self.s.spawn([self.s.args.pw_record, "-P",
                          '{ node.name = "f318-rec-mon" '
                          'stream.capture.sink = true }',
                          "--target", USBSTREAMER, rec])
        try:
            usb = self.s.node(**{"node.name": USBSTREAMER})
            poll("monitor capture linked from the USBStreamer stand-in",
                 lambda: any(l.get("output-node-id") == usb["id"]
                             for l in self.linked_by("node.name",
                                                     "f318-rec-mon") or []))
        finally:
            self.stop(p)

    def assert_default_safe(self, since):
        # The policy logs DEFAULT_LINE when it drops a candidate; without
        # it, WirePlumber picks a protected node and the check below fails.
        poll("WirePlumber evaluated default.audio.sink",
             lambda: DEFAULT_LINE in self.s.wp_log()[since:]
             or self.s.default_sink() in PROTECTED)
        d = self.s.default_sink()
        if d in PROTECTED:
            raise CaseFailure("default.audio.sink is %s" % d)

    # 10
    def case_default_sink_not_protected(self):
        self.assert_default_safe(0)

    # 11
    def case_configured_default_ignored(self):
        since = len(self.s.wp_log())
        r = self.s.tool(self.s.args.pw_metadata, "0",
                        "default.configured.audio.sink",
                        '{ "name": "%s" }' % USBSTREAMER, "Spa:String:JSON")
        if r.returncode != 0:
            raise CaseFailure("pw-metadata: %s %s" % (r.stdout, r.stderr))
        self.assert_default_safe(since)

    # 12
    def case_reenumeration(self):
        self.s.destroy_node(USBSTREAMER)
        since = len(self.s.wp_log())
        self.s.create_standin(USBSTREAMER)
        self.assert_default_safe(since)
        p = self.play("f318-play-reenum", USBSTREAMER)
        try:
            self.expect_denied("f318-play-reenum", USBSTREAMER)
        finally:
            self.stop(p)

    # 13
    def make_gm_link(self):
        r = self.s.tool(self.s.args.pw_link, "%s:capture_FL" % GM_SRC,
                        "%s:playback_FL" % USBSTREAMER)
        if r.returncode != 0:
            raise CaseFailure("pw-link: %s %s" % (r.stdout, r.stderr))
        src = self.s.node(**{"node.name": GM_SRC})
        usb = self.s.node(**{"node.name": USBSTREAMER})
        self.gm_link = (src["id"], usb["id"])
        poll("GM-style link exists", self.gm_link_present)

    def case_gm_link_survives(self):
        self.make_gm_link()
        # A WirePlumber rescan must not remove it: a denied stream forces
        # one, and its deny line shows the rescan ran.
        p = self.play("f318-play-gm", USBSTREAMER)
        try:
            self.expect_denied("f318-play-gm", USBSTREAMER)
        finally:
            self.stop(p)
        if not self.gm_link_present():
            raise CaseFailure("GM-style link removed by a WirePlumber rescan")

    def gm_link_present(self):
        src = self.s.node(**{"node.name": GM_SRC})
        usb = self.s.node(**{"node.name": USBSTREAMER})
        if not src or not usb:
            return False
        return any(l.get("output-node-id") == src["id"]
                   and l.get("input-node-id") == usb["id"]
                   for l in self.s.links())

    # 14
    def ports_of(self, name):
        n = self.s.node(**{"node.name": name})
        return sorted((o["id"], o["info"]["props"].get("port.name"))
                      for o in self.s.dump() or []
                      if o.get("type") == "PipeWire:Interface:Port" and n
                      and o["info"]["props"].get("node.id") == n["id"])

    def case_wp_restart(self):
        if self.gm_link is None:
            raise CaseFailure("no GM-style link: gm_link_survives failed")
        before = self.ports_of(USBSTREAMER)
        self.s.stop(self.s.wp)
        since = len(self.s.wp_log())
        self.s.start_wp()
        if not self.gm_link_present():
            # Stock WirePlumber re-applies the port config of every adapter
            # node it adopts, which re-creates the ports and drops their
            # links (seen with the policy disabled too). GraphManager
            # re-links; do the same and check that F-318 leaves it alone.
            print("    note: WirePlumber restart dropped the GM-style link "
                  "(USBStreamer stand-in ports %s -> %s); re-linking"
                  % (before, self.ports_of(USBSTREAMER)))
            self.make_gm_link()
        self.assert_default_safe(since)
        p = self.play("f318-play-wprestart", USBSTREAMER)
        try:
            self.expect_denied("f318-play-wprestart", USBSTREAMER)
        finally:
            self.stop(p)
        if not self.gm_link_present():
            raise CaseFailure("GM-style link removed by a WirePlumber rescan "
                              "after the restart")

    # 15
    def case_pw_restart(self):
        # systemd restarts WirePlumber with PipeWire (BindsTo); do the same.
        self.s.stop(self.s.pulse)
        self.s.pulse = None
        self.s.stop(self.s.wp)
        self.s.stop(self.s.pw)
        self.s.start_pw()
        self.s.start_wp()
        for name in STANDINS:
            self.s.create_standin(name)
        p = self.play("f318-play-pwrestart", USBSTREAMER)
        try:
            self.expect_denied("f318-play-pwrestart", USBSTREAMER)
        finally:
            self.stop(p)

    # 16
    def case_hook_order(self):
        rx = re.compile(r"dispatching event \((.*?)\) running hook "
                        r"<[^>]*>\((.*?)\)\s*$")
        groups, current = [], {}
        for line in self.s.wp_log().splitlines():
            m = rx.search(line)
            if not m or "select-target" not in m.group(1):
                continue
            ev, hook = m.groups()
            seq = current.get(ev)
            if seq is None or hook in seq:
                seq = []
                current[ev] = seq
                groups.append(seq)
            seq.append(hook)
        finders = ("linking/find-defined-target",
                   "linking/find-audio-group-target",
                   "linking/find-filter-target",
                   "linking/find-media-role-target",
                   "linking/find-default-target",
                   "linking/find-best-target",
                   "linking/get-filter-from-target")
        checked = 0
        for seq in groups:
            if "linking/mugge-deny-playback" not in seq:
                continue
            i = seq.index("linking/mugge-deny-playback")
            for f in finders:
                if f in seq and seq.index(f) > i:
                    raise CaseFailure("%s ran after the deny hook: %s"
                                      % (f, seq))
            for later in ("linking/prepare-link",
                          "linking/mugge-deny-playback-final",
                          "linking/link-target"):
                if later not in seq:
                    raise CaseFailure("%s missing from chain: %s"
                                      % (later, seq))
            order = [seq.index(h) for h in (
                "linking/mugge-deny-playback", "linking/prepare-link",
                "linking/mugge-deny-playback-final", "linking/link-target")]
            if order != sorted(order):
                raise CaseFailure("wrong hook order: %s" % seq)
            checked += 1
        if checked == 0:
            raise CaseFailure("no select-target chain with the deny hook "
                              "found in the dispatcher trace")
        print("    checked %d select-target chains" % checked)

    # 17
    def case_final_guard_silent(self):
        if "final guard fired" in self.s.wp_log():
            raise CaseFailure("the final guard fired: a hook ran after "
                              "linking/mugge-deny-playback")
        if self.s.wp.poll() is not None:
            raise CaseFailure("WirePlumber exited (%s)" % self.s.wp.returncode)


ORDER = [
    "load_line", "play_default", "play_target_usbstreamer",
    "play_target_convolver", "metadata_move", "pw_loopback", "pulse_paplay",
    "capture_source_links", "monitor_capture_links",
    "default_sink_not_protected", "configured_default_ignored",
    "reenumeration", "gm_link_survives", "wp_restart", "pw_restart",
    "hook_order", "final_guard_silent",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("policy", "control"), required=True)
    ap.add_argument("--wp-data-dirs", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--log-copy", help="copy the WirePlumber log here")
    for tool in ("pipewire", "wireplumber", "pipewire-pulse", "pw-dump",
                 "pw-cli", "pw-play", "pw-record", "pw-link", "pw-metadata",
                 "pw-loopback", "paplay"):
        ap.add_argument("--" + tool, default=shutil.which(tool))
    args = ap.parse_args()
    missing = [t for t, v in vars(args).items() if v is None
               and t != "log_copy"]
    if missing:
        print("FAIL: missing tools: %s" % ", ".join(missing))
        return 2

    os.makedirs(args.workdir, exist_ok=True)
    stack = Stack(args, args.workdir)
    silence = os.path.join(args.workdir, "silence.wav")
    write_silence(silence)
    results = []
    try:
        try:
            stack.start_pw()
            stack.start_wp()
            for name in STANDINS:
                stack.create_standin(name)
        except Exception:
            traceback.print_exc()
            for log in ("pipewire.log", "wireplumber.log"):
                path = os.path.join(args.workdir, log)
                if os.path.exists(path):
                    with open(path, errors="replace") as f:
                        print("---- last lines of %s" % log)
                        print("".join(f.readlines()[-40:]))
            d = stack.dump()
            print("---- pw-dump metadata: %s" % [
                (o.get("props", {}).get("metadata.name"),
                 len(o.get("metadata") or []))
                for o in d or [] if "Metadata" in o.get("type", "")])
            print("---- pw-cli ls Metadata:")
            print(stack.tool(args.pw_cli, "ls", "Metadata").stdout)
            print("FAIL: PipeWire/WirePlumber stack did not start")
            return 2
        cases = Cases(stack, silence)
        for name in ORDER:
            t0 = time.monotonic()
            try:
                getattr(cases, "case_" + name)()
                results.append((name, True, ""))
                print("PASS %-28s (%.1f s)" % (name, time.monotonic() - t0))
            except Exception as e:
                msg = str(e) if isinstance(e, CaseFailure) else \
                    traceback.format_exc()
                results.append((name, False, msg))
                print("FAIL %-28s (%.1f s): %s"
                      % (name, time.monotonic() - t0, msg))
    finally:
        stack.stop_all()
        if args.log_copy:
            shutil.copy(stack.wp_log_path, args.log_copy)
    passed = sum(1 for r in results if r[1])
    print("RESULT mode=%s: %d passed, %d failed, of %d"
          % (args.mode, passed, len(results) - passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
