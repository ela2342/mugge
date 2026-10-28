#!/usr/bin/env python3
"""Static check: every hook named in mugge-no-bypass.lua's after/before
lists exists in the WirePlumber package.

WirePlumber ignores an after/before entry that names no registered hook,
so a finder renamed in a WirePlumber upgrade would silently drop an
ordering constraint. This check makes that fail at build time.

Usage: check_hook_names.py <mugge-no-bypass.lua> <wireplumber>/share/wireplumber/scripts
"""

import os
import re
import sys

ORDER_RX = re.compile(r"\b(after|before)\s*=\s*(\{[^}]*\}|\"[^\"]*\")")
NAME_RX = re.compile(r"\"([^\"]+)\"")
HOOK_RX = re.compile(r"^\s*name\s*=\s*\"([^\"]+)\"", re.M)


def main(script, scripts_dir):
    with open(script) as f:
        text = f.read()
    own = set(HOOK_RX.findall(text))
    wanted = []
    for _, value in ORDER_RX.findall(text):
        wanted.extend(NAME_RX.findall(value))
    if not wanted:
        print("FAIL no after/before entries found in %s" % script)
        return 1
    known = set()
    for root, _, files in os.walk(scripts_dir):
        for name in files:
            if name.endswith(".lua"):
                with open(os.path.join(root, name)) as f:
                    known.update(HOOK_RX.findall(f.read()))
    failed = 0
    for name in sorted(set(wanted)):
        if name in known:
            print("PASS %s" % name)
        elif name in own:
            print("PASS %s (own hook)" % name)
        else:
            print("FAIL %s: no such hook in %s" % (name, scripts_dir))
            failed += 1
    n = len(set(wanted))
    print("RESULT hook names: %d passed, %d failed, of %d"
          % (n - failed, failed, n))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
