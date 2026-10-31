#!/usr/bin/env python3
"""Self-test of check_hook_order (run_policy_test.py) on synthetic logs.

The good log follows the line format of WirePlumber 0.5.12. Each bad log
is one way the hook order can break; check_hook_order must reject it, so
a broken ordering constraint fails the check instead of passing silently.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_policy_test import CaseFailure, check_hook_order  # noqa: E402

ITEM = "<WpSiAudioAdapter:0xaaaaaacb1680>"


def find(src="find-defined-target.lua:33:chunk"):
    return ("I 20:28:30.176747          s-linking %s: %s handling item "
            "116: f318-play-default (58)" % (src, ITEM))


GATE = ('I 20:28:30.177300  s-mugge-no-bypass mugge-no-bypass.lua:137:'
        'denyPlayback: %s F-318: mugge-deny-playback: denied item 116 '
        'node.name="f318-play-default" node.id="58"' % ITEM)
PREP = ("I 20:28:30.177411          s-linking prepare-link.lua:31:chunk: "
        "%s handling item 116: f318-play-default (58)" % ITEM)
OTHER = ("I 20:28:30.177500          s-linking prepare-link.lua:31:chunk: "
         "<WpSiAudioAdapter:0xaaaaaacb2000> handling item 117: "
         "f318-rec-umik (64)")
EXPECTED = ("f318-play-default",)

GOOD = [find(), find("find-best-target.lua:41:chunk"), GATE, PREP, OTHER]
BAD = {
    "gate after prepare-link": [find(), PREP, GATE],
    "gate before a finder": [find(), GATE, find("find-best-target.lua:41:"
                                                "chunk"), PREP],
    "gate before every finder": [GATE, PREP],
    "no gate": [find(), PREP],
    "gate without prepare-link": [find(), GATE],
    "empty log": [],
    "second chain without gate": GOOD + [find(), PREP],
}

failed = 0


def report(ok, name, detail=""):
    global failed
    failed += 0 if ok else 1
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, detail))


try:
    n = check_hook_order("\n".join(GOOD), EXPECTED)
    report(n == 1, "good log accepted", " (%d sequences)" % n)
except CaseFailure as e:
    report(False, "good log accepted", ": %s" % e)

for name, lines in BAD.items():
    try:
        check_hook_order("\n".join(lines), EXPECTED)
        report(False, "rejects: " + name, ": accepted")
    except CaseFailure as e:
        report(True, "rejects: " + name, " (%s)" % e)

total = 1 + len(BAD)
print("RESULT hook order self-test: %d passed, %d failed, of %d"
      % (total - failed, failed, total))
sys.exit(1 if failed else 0)
