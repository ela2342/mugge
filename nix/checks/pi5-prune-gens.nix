# pi5-prune-gens.nix — offline test of the Pi 5 FAT generation install (AC2a)
#
# Runs the install script of the Pi 5 bootloader hook (generation,
# pointer, prune) against a fake FAT root (g/, legacy gens/), fake
# toplevels and profile directories, and checks which directories
# survive, what config.txt and g/MAP.txt say, and that every guard dies
# before the pointer. Layout L1s: US-172, architect rulings 04d8b687,
# 2b485056, 63e41531; SecSpec acb8fb17 L1-L5; QE c639203e, 9a21330d,
# 74504b2f, 3f80f141, da578961, ad6a8bda.
#
# target: system.build.pi5PruneGens of the Pi 5 configuration. board-guard
# asserts that the hook calls exactly this store path. The check runs the
# same script text with only its PATH line swapped for host tools and a
# findmnt stub (the fake FAT root is a plain directory); the swap is
# asserted below. The length cases are built from the target's class
# constants (CONST passes, CONST + 1 dies).
#
# Usage: nix build -L .#checks.<system>.pi5-prune-gens
{ pkgs, target }:

let
  inherit (pkgs) lib;

  targetText = builtins.unsafeDiscardStringContext target.text;
  targetBin = builtins.unsafeDiscardStringContext target.binPath;
  # writeShellScript wraps the text in the target's "#!<bash>" line and a
  # final newline; the host writeShellScript adds both again.
  body = lib.removeSuffix "\n" (lib.concatStringsSep "\n" (lib.tail (lib.splitString "\n" targetText)));

  # FAKE_FSTYPE (default vfat) is the file system the stub reports.
  findmnt = pkgs.writeShellScriptBin "findmnt" "echo \"\${FAKE_FSTYPE-vfat}\"";
  hostBin = lib.makeBinPath [ findmnt pkgs.coreutils pkgs.gnused ];
  swap = text:
    if !(lib.hasInfix "export PATH=${targetBin}\n" text)
      || lib.hasInfix builtins.storeDir (lib.replaceStrings [ targetBin ] [ "" ] text)
    then throw "pi5-prune-gens: target script has store references other than its PATH"
    else lib.replaceStrings [ targetBin ] [ hostBin ] text;
  install = pkgs.writeShellScript "install-pi5-gen" (swap body);
  # Case 8: the script with one guard replaced by `true`. The named case
  # must turn red.
  brokenTo = to: guard:
    if lib.hasInfix guard body
    then pkgs.writeShellScript "install-pi5-gen-broken" (swap (lib.replaceStrings [ guard ] [ to ] body))
    else throw "pi5-prune-gens: guard not in the script: ${guard}";
  broken = brokenTo "true";
  b32 = n: lib.concatStrings (lib.genList (_: "[0-9a-df-np-sv-z]") n);
  mutants = [
    { c = "c1"; what = "collision guard"; s = broken ''[ "$have" = "$id" ]''; }
    { c = "c9"; what = "4.6 length check"; s = broken "[ \"\${#p}\" -le \"$2\" ]"; }
    { c = "c10"; what = "4.6 existence check"; s = broken ''[ -f "$gen/$3" ]''; }
    { c = "c17"; what = "unknown-prev gate"; s = broken ''[ -n "$prevknown" ]''; }
    { c = "c13"; what = "two-generation gate"; s = broken ''[ "$npost" -ge 2 ]''; }
    { c = "c19"; what = "booted gate"; s = broken ''[ -n "$booted" ]''; }
    { c = "c20"; what = "chosen gate"; s = broken ''[ -n "$chosenknown" ]''; }
    { c = "c16b"; what = "legacy name rule"; s = brokenTo "*)" "${b32 32}|${b32 32}.tmp)"; }
    { c = "c16c"; what = "symlink skip"; s = broken ''[ ! -L "$d" ]''; }
    { c = "c26"; what = "vfat guard"; s = broken ''[ "$fstype" = vfat ]''; }
  ];

  # Config templates: the real one, and variants at and over the class
  # limits (built from the constants) or naming a missing overlay.
  T = target.configTemplate;
  K = target.KERNEL_CLASS_MAX;
  O = target.OVERLAY_CLASS_MAX;
  prefixLen = builtins.stringLength target.container + target.idLen + 1;
  filler = c: n: lib.concatStrings (lib.genList (_: c) n);
  kname = n: filler "k" (n - prefixLen);
  oname = n: filler "o" (n - prefixLen - builtins.stringLength "overlays/" - builtins.stringLength ".dtbo");
  altered = from: to: let r = lib.replaceStrings [ from ] [ to ] T; in
    if r == T then throw "pi5-prune-gens: template variant alters nothing ('${from}')" else r;
  tmpl = name: text: pkgs.writeText "pi5-config-${name}.txt" text;
  tReal = tmpl "real" T;
  tKernelAt = tmpl "kernel-at" (altered "\nkernel=Image\n" "\nkernel=${kname K}\n");
  tKernelOver = tmpl "kernel-over" (altered "\nkernel=Image\n" "\nkernel=${kname (K + 1)}\n");
  tOverlayAt = tmpl "overlay-at" (T + "dtoverlay=${oname O}\n");
  tOverlayOver = tmpl "overlay-over" (T + "dtoverlay=${oname (O + 1)}\n");
  tOverlayMissing = tmpl "overlay-missing" (T + "dtoverlay=absent-pi5\n");
  CD = lib.removeSuffix "/" target.container;
in
pkgs.runCommand "pi5-prune-gens" { } ''
  set -euo pipefail

  S=${install}
  REAL=${tReal}
  CT=${target.container}
  CD=${CD}
  K=${toString K}
  O=${toString O}

  # Fake 32-character ids (Nix base32). A2 shares A's first 8 characters
  # (<id8>). FE and FU use letters outside the alphabet: never a
  # generation name.
  A=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  A2=aaaaaaaazzzzzzzzzzzzzzzzzzzzzzzz
  B=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  C=cccccccccccccccccccccccccccccccc
  D=dddddddddddddddddddddddddddddddd
  E=ffffffffffffffffffffffffffffffff
  X=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  FE=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
  FU=uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu

  total=0
  passed=0
  fail() { echo "FAIL: $label: $*" >&2; exit 1; }
  short() { echo "$1" | cut -c1-${toString target.idLen}; }

  # setup LABEL: fresh fake FAT root, store and profiles. The FAT root
  # holds files the install must never touch. No config.txt, no booted
  # system, no chosen prefix.
  setup() {
    label="$1"
    total=$((total + 1))
    root=$(readlink -f "$(mktemp -d)")
    fw="$root/fw"
    g="$fw/$CD"
    legacy="$fw/gens"
    profiles="$root/profiles"
    store="$root/store"
    kpkg="$store/kpkg"
    mkdir -p "$fw/overlays" "$fw/t" "$profiles" "$store"
    echo start > "$fw/start4.elf"
    echo foo > "$fw/overlays/foo.dtbo"
    echo keep > "$fw/t/keep"
    mkkpkg "$kpkg"
    TMPL=$REAL
  }
  # mkkpkg DIR: fake kernel package with every file the templates name.
  mkkpkg() {
    mkdir -p "$1/dtbs/broadcom" "$1/dtbs/overlays"
    echo kernel > "$1/Image"
    for d in ${lib.escapeShellArgs target.dtbs}; do echo "$d" > "$1/dtbs/broadcom/$d"; done
    for o in $(sed -n 's/^dtoverlay=\([^,]*\).*$/\1/p' "$REAL") ${oname O} ${oname (O + 1)}; do
      echo "$o" > "$1/dtbs/overlays/$o.dtbo"
    done
    echo map > "$1/dtbs/overlays/overlay_map.dtb"
    echo hat > "$1/dtbs/overlays/hat_map.dtb"
  }
  # mktop ID [KPKG]: fake toplevel for ID.
  mktop() {
    t="$store/$1-nixos-system-mugge"
    [ ! -e "$t" ] || return 0
    mkdir -p "$t"
    ln -s "''${2:-$kpkg}/Image" "$t/kernel"
    echo "initrd $1" > "$t/initrd"
    echo quiet > "$t/kernel-params"
    touch "$t/init"
  }
  # link N ID: profile generation N points at ID's toplevel, and the plain
  # "system" link at the newest system-N-link, as in a real profiles dir.
  link() {
    mktop "$2"
    ln -s "$store/$2-nixos-system-mugge" "$profiles/system-$1-link"
    ln -sfn "system-$1-link" "$profiles/system"
  }
  # gen ID: fake complete g/<id8> holding ID. part ID: no .complete.
  # lgen ID: complete legacy gens/<id> (empty .complete, as the old hook
  # wrote it).
  gen() { mkdir -p "$g/$(short "$1")"; echo "$1" > "$g/$(short "$1")/Image"; echo "$1" > "$g/$(short "$1")/.complete"; }
  part() { mkdir -p "$g/$(short "$1")"; echo "$1" > "$g/$(short "$1")/Image"; }
  lgen() { mkdir -p "$legacy/$1"; echo "$1" > "$legacy/$1/Image"; touch "$legacy/$1/.complete"; }
  # boot ID: booted system ID, firmware booted from g/<id8>/.
  # lboot ID: booted system ID, firmware booted from gens/<id>/.
  # chosen VALUE: the firmware's os_prefix (NUL-terminated, as in /proc).
  boot() { mktop "$1"; ln -sfn "$store/$1-nixos-system-mugge" "$root/booted"; chosen "$CT$(short "$1")/"; }
  lboot() { mktop "$1"; ln -sfn "$store/$1-nixos-system-mugge" "$root/booted"; chosen "gens/$1/"; }
  chosen() { rm -rf "$root/chosen"; printf '%s\0' "$1" > "$root/chosen"; }
  # oldcfg ID: the previous config.txt points at g/<id8>/ (real template,
  # os_prefix= last). oldraw VALUE: real template with os_prefix=VALUE.
  oldcfg() { sed "s|@ID@|$(short "$1")|" "$REAL" > "$fw/config.txt"; }
  oldraw() { { sed '/^os_prefix=/d' "$REAL"; printf 'os_prefix=%s\n' "$1"; } > "$fw/config.txt"; }
  # run ID: install ID with template $TMPL. inst ID: the same, quietly,
  # to seed a real generation (and the pointer to it).
  run() {
    mktop "$1"
    "$S" "$fw" "$store/$1-nixos-system-mugge" "$TMPL" "$profiles" "$root/booted" "$root/chosen"
  }
  inst() { run "$1" > /dev/null 2>&1 || fail "seeding $1 failed"; }
  # runfail ID TEXT...: the install dies, and its message has every TEXT.
  runfail() {
    i="$1"
    shift
    if run "$i" 2> "$root/err"; then fail "install of $i did not die"; fi
    for m in "$@"; do
      grep -qF -- "$m" "$root/err" || fail "die message lacks '$m': $(cat "$root/err")"
    done
  }
  # snap [DIR]: every path under DIR (default the FAT root) with the hash
  # of each file.
  snap() {
    (cd "''${1:-$fw}" && find . | LC_ALL=C sort | while read -r f; do
      if [ -f "$f" ] && [ ! -L "$f" ]; then echo "$f $(sha256sum < "$f" | cut -d' ' -f1)"; else echo "$f"; fi
    done)
  }
  # snapold ID: snap without g/MAP.txt and without ID's g/ directory.
  snapold() { snap | grep -v -e "^\./$CD/MAP\.txt" -e "^\./$CD/$(short "$1")\(/\|$\)" || true; }
  # dirsof DIR: directory names in DIR, sorted, space-separated.
  dirsof() { (cd "$1" && find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||' | sort | tr '\n' ' '); }
  # expect_dirs ID...: exactly these g/ directories remain (ids are
  # mapped to <id8>; other names are taken as is).
  expect_dirs() {
    got=$(dirsof "$g")
    want=$(for i in "$@"; do [ "$(echo -n "$i" | wc -c)" -eq 32 ] && short "$i" || echo "$i"; done | sed '/^$/d' | sort | tr '\n' ' ')
    [ "$got" = "$want" ] || fail "$CD/ dirs: got '$got', want '$want'"
  }
  # expect_legacy NAME...: exactly these gens/ directories remain; with no
  # arguments, gens/ must be gone.
  expect_legacy() {
    if [ "$#" -eq 0 ]; then
      [ ! -e "$legacy" ] || fail "gens/ still exists: $(ls -A "$legacy" | tr '\n' ' ')"
      return 0
    fi
    got=$(dirsof "$legacy")
    want=$(printf '%s\n' "$@" | sort | tr '\n' ' ')
    [ "$got" = "$want" ] || fail "gens/ dirs: got '$got', want '$want'"
  }
  # expect_map LINE...: g/MAP.txt is exactly these lines (full ids), and
  # there is no MAP.txt at the FAT root.
  expect_map() {
    want=$(printf '%s\n' "$@")
    got=$(cat "$g/MAP.txt")
    [ "$got" = "$want" ] || fail "MAP.txt: got '$got', want '$want'"
    [ ! -e "$fw/MAP.txt" ] || fail "MAP.txt at the FAT root"
  }
  # expect_pointer ID: config.txt is the real template rendered for ID.
  expect_pointer() {
    sed "s|@ID@|$(short "$1")|" "$TMPL" | cmp -s - "$fw/config.txt" || fail "config.txt does not point at $1"
  }
  # expect_root: the FAT root files outside g/ and gens/ are untouched.
  expect_root() {
    [ "$(cat "$fw/start4.elf")" = start ] || fail "start4.elf changed"
    [ "$(cat "$fw/overlays/foo.dtbo")" = foo ] || fail "overlays/foo.dtbo changed"
    [ "$(cat "$fw/t/keep")" = keep ] || fail "t/keep changed"
  }
  pass() { expect_root; passed=$((passed + 1)); echo "PASS: $label"; }

  # ---- Steps 1-2: generation and pointer ------------------------------

  # (1) <id8> collision (QE c639203e 1, architect a8f9d760 S4): A2 has
  # A's <id8>. The install dies before the pointer with the cause, the
  # state and the fix; config.txt and g/aaaaaaaa are byte-identical.
  c1() {
    setup "1 id8 collision dies before the pointer"
    link 1 $A; link 2 $A2
    inst $A
    boot $A
    before=$(snap)
    runfail $A2 "id8 $(short $A) already holds toplevel $A, new toplevel $A2" \
      "config.txt is unchanged and the running system is unaffected" \
      "Fix: any configuration change re-hashes the toplevel, or remove $g/$(short $A)/ once it is neither booted nor prev"
    [ "$(snap)" = "$before" ] || fail "FAT changed"
    expect_pointer $A
    pass
  }

  # (2) Reuse: g/<id8> already holds this id. Nothing is copied (contents
  # and mtimes unchanged), and the pointer is written.
  c2() {
    setup "2 complete generation is reused, pointer written"
    link 1 $B; link 2 $C
    inst $C
    gen $B
    oldcfg $B
    boot $B
    touch -t 200001010000 "$g/$(short $C)/Image" "$g/$(short $C)/cmdline.txt"
    touch -t 200001010001 "$root/ref"
    contents=$(snap "$g/$(short $C)")
    run $C > /dev/null
    [ "$(snap "$g/$(short $C)")" = "$contents" ] || fail "reused generation changed"
    [ ! "$g/$(short $C)/Image" -nt "$root/ref" ] && [ ! "$g/$(short $C)/cmdline.txt" -nt "$root/ref" ] \
      || fail "reused generation rewritten"
    expect_pointer $C
    pass
  }

  # (3a) A half-written g/<id8> (no .complete) and a stale g/<id8>.tmp
  # are rebuilt; the pointer names only the complete directory.
  c3a() {
    setup "3a half-written generation is rebuilt before the pointer"
    link 1 $D
    part $D
    mkdir -p "$g/$(short $D).tmp"
    touch "$g/$(short $D)/junk" "$g/$(short $D).tmp/junk"
    run $D > /dev/null
    [ "$(cat "$g/$(short $D)/.complete")" = $D ] || fail ".complete is not $D"
    [ ! -e "$g/$(short $D)/junk" ] && [ ! -e "$g/$(short $D).tmp" ] || fail "half-written content left"
    [ "$(cat "$g/$(short $D)/cmdline.txt")" = "init=$store/$D-nixos-system-mugge/init quiet" ] || fail "cmdline.txt"
    expect_pointer $D
    pass
  }

  # (3b) The copy fails (no initrd): the install dies, config.txt is
  # byte-identical and there is no g/<id8> to point at.
  c3b() {
    setup "3b failed copy leaves no generation and no pointer"
    link 1 $C; link 2 $D
    inst $C
    boot $C
    mktop $D
    rm "$store/$D-nixos-system-mugge/initrd"
    cp "$fw/config.txt" "$root/config.before"
    runfail $D
    cmp -s "$root/config.before" "$fw/config.txt" || fail "config.txt changed"
    [ ! -e "$g/$(short $D)" ] || fail "$CD/$(short $D) exists"
    pass
  }

  # (3c) The pointer write fails (QE ad6a8bda X3): nothing is pruned, no
  # legacy dir is removed.
  c3c() {
    setup "3c failed pointer write deletes nothing"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C
    gen $D
    oldcfg $D
    boot $D
    mkdir "$fw/config.txt.new"
    before=$(snapold $E)
    runfail $E
    [ "$(snapold $E)" = "$before" ] || fail "FAT changed"
    pass
  }

  # ---- Step 2: runtime check 4.6 (QE 9a21330d cases 9-11) ------------

  # (9) A dtoverlay= .dtbo path of OVERLAY_CLASS_MAX + 1: dies, config.txt
  # and the earlier generation are byte-identical.
  c9() {
    setup "9 overlay path over OVERLAY_CLASS_MAX dies"
    link 1 $C; link 2 $D
    gen $C
    oldcfg $C
    boot $C
    TMPL=${tOverlayOver}
    before=$(snapold $D)
    runfail $D "overlays/${oname (O + 1)}.dtbo is $((O + 1)) characters, over the overlay class limit $O" \
      "config.txt is unchanged"
    [ "$(snapold $D)" = "$before" ] || fail "FAT changed"
    pass
  }
  # (9b) A kernel= path of KERNEL_CLASS_MAX + 1: dies the same way.
  c9b() {
    setup "9b kernel path over KERNEL_CLASS_MAX dies"
    link 1 $C; link 2 $D
    gen $C
    oldcfg $C
    boot $C
    TMPL=${tKernelOver}
    before=$(snapold $D)
    runfail $D "${kname (K + 1)} is $((K + 1)) characters, over the kernel class limit $K" "config.txt is unchanged"
    [ "$(snapold $D)" = "$before" ] || fail "FAT changed"
    pass
  }

  # (10) The kernel package has no overlay_map.dtb: dies.
  c10() {
    setup "10 missing overlay_map.dtb dies"
    mkkpkg "$store/kpkg2"
    rm "$store/kpkg2/dtbs/overlays/overlay_map.dtb"
    mktop $D "$store/kpkg2"
    link 1 $C; link 2 $D
    gen $C
    oldcfg $C
    boot $C
    before=$(snapold $D)
    runfail $D "overlays/overlay_map.dtb is missing; config.txt is unchanged"
    [ "$(snapold $D)" = "$before" ] || fail "FAT changed"
    pass
  }
  # (10b) config.txt names an overlay the kernel does not ship: dies.
  c10b() {
    setup "10b missing dtoverlay .dtbo dies"
    link 1 $C; link 2 $D
    gen $C
    oldcfg $C
    boot $C
    TMPL=${tOverlayMissing}
    before=$(snapold $D)
    runfail $D "overlays/absent-pi5.dtbo is missing; config.txt is unchanged"
    [ "$(snapold $D)" = "$before" ] || fail "FAT changed"
    pass
  }

  # (11) Paths of exactly KERNEL_CLASS_MAX and OVERLAY_CLASS_MAX pass
  # (inclusive, architect 94817076).
  c11() {
    setup "11 paths at the class limits pass"
    link 1 $D
    TMPL=${tKernelAt}
    run $D > /dev/null
    expect_pointer $D
    [ -f "$g/$(short $D)/${kname K}" ] || fail "kernel not at its configured name"
    rm -rf "$g/$(short $D)"
    TMPL=${tOverlayAt}
    run $D > /dev/null
    expect_pointer $D
    pass
  }

  # ---- Step 3: prune of g/ (AC2a) -------------------------------------

  # (P1) No-op deploy (new = prev = booted) with an older complete
  # generation: the older one is kept, 2 generations remain.
  p1() {
    setup "P1 no-op deploy keeps newest other present"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $B
    boot $C
    run $C
    expect_dirs $B $C
    expect_map "1 $A pruned" "2 $B present" "3 $C present"
    expect_pointer $C
    pass
  }

  # (P1b) As P1 with several older complete generations: only the newest
  # other one is kept. Run twice: the second run changes nothing.
  p1b() {
    setup "P1b no-op deploy keeps only the newest other, idempotent"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $A; gen $B
    boot $C
    run $C
    run $C
    expect_dirs $B $C
    expect_map "1 $A pruned" "2 $B present" "3 $C present"
    pass
  }

  # (P2a) The newest other generation is already pruned: it is not
  # recreated.
  p2a() {
    setup "P2a pruned alt is not recreated"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    boot $C
    run $C
    expect_dirs $C
    expect_map "1 $A pruned" "2 $B pruned" "3 $C present"
    pass
  }

  # (P2b) The newest other generation has no .complete: it is not the alt
  # (removed as incomplete), the next older complete one is kept, and no
  # .complete is created.
  p2b() {
    setup "P2b incomplete alt falls back to next complete"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $A; part $B
    boot $C
    run $C
    expect_dirs $A $C
    expect_map "1 $A present" "2 $B pruned" "3 $C present"
    pass
  }

  # (P2c) A g/ directory whose .complete is empty is not present: not the
  # alt, removed.
  p2c() {
    setup "P2c empty .complete is not present"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $A; part $B; touch "$g/$(short $B)/.complete"
    boot $C
    run $C
    expect_dirs $A $C
    expect_map "1 $A present" "2 $B pruned" "3 $C present"
    pass
  }

  # (P3) Normal deploy: new D, previous = booted = C (alt = C too).
  # Everything outside {new, prev, booted, alt} is pruned, including
  # stale .tmp directories.
  p3() {
    setup "P3 normal deploy keeps new and prev/booted"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D
    gen $A; gen $B; gen $C
    mkdir -p "$g/$(short $D).tmp" "$g/$(short $X).tmp"
    oldcfg $C
    boot $C
    run $D
    expect_dirs $C $D
    expect_map "1 $A pruned" "2 $B pruned" "3 $C present" "4 $D present"
    expect_pointer $D
    pass
  }

  # (P4) Numeric order: system-10 is newer than system-9.
  p4() {
    setup "P4 alt by numeric generation order"
    link 9 $A; link 10 $B; link 11 $C
    inst $C
    gen $A; gen $B
    boot $C
    run $C
    expect_dirs $B $C
    expect_map "9 $A pruned" "10 $B present" "11 $C present"
    pass
  }

  # (P5) Rollback (T54 pattern): new B, previous = booted = C. The alt is
  # C, A is pruned.
  p5() {
    setup "P5 rollback keeps new and prev/booted"
    link 1 $A; link 2 $B; link 3 $C
    gen $A; gen $C
    oldcfg $C
    boot $C
    run $B
    expect_dirs $B $C
    expect_map "1 $A pruned" "2 $B present" "3 $C present"
    pass
  }

  # (P6) Fresh install: no config.txt, nothing booted. The previous
  # pointer is unknown, so nothing is removed, not even strays (architect
  # 63e41531 A3). g/MAP.txt is the only map (QE c639203e 6).
  p6() {
    setup "P6 fresh install removes nothing"
    link 1 $A
    gen $X; part $B
    run $A
    expect_dirs $A $B $X
    expect_legacy
    expect_map "1 $A present"
    expect_pointer $A
    pass
  }

  # (P7) PO clause: the pointer selects an unbooted generation. Booted B,
  # then two deploys without a reboot: prev C (never booted), new D. Keep
  # {B, C, D}; alt = C. A is pruned.
  p7() {
    setup "P7 new, prev and booted all kept"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D
    gen $A; gen $B; gen $C
    oldcfg $C
    boot $B
    run $D
    expect_dirs $B $C $D
    expect_map "1 $A pruned" "2 $B present" "3 $C present" "4 $D present"
    pass
  }

  # (P7b) Previous is neither booted nor the alt: kept as previous. The
  # previous os_prefix= is the last line of config.txt, as main renders it
  # (architect 63e41531 A1, QE ad6a8bda X2).
  p7b() {
    setup "P7b previous kept on its own, parsed from the last line"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D
    inst $D
    gen $A; gen $B; gen $C
    oldcfg $A
    [ "$(tail -n 1 "$fw/config.txt")" = "os_prefix=$CT$(short $A)/" ] || fail "os_prefix= is not the last line"
    [ "$(head -n 1 "$fw/config.txt")" != "os_prefix=$CT$(short $A)/" ] || fail "os_prefix= is the first line"
    boot $D
    run $D
    expect_dirs $A $C $D
    expect_map "1 $A present" "2 $B pruned" "3 $C present" "4 $D present"
    pass
  }

  # (P8) Booted generation without a profile link: kept anyway; MAP lists
  # only linked generations.
  p8() {
    setup "P8 unlinked booted generation kept"
    link 3 $C; link 4 $D
    gen $B; gen $C
    oldcfg $C
    boot $B
    run $D
    expect_dirs $B $C $D
    expect_map "3 $C present" "4 $D present"
    pass
  }

  # (P10) Profile entries that are not system-N-link are ignored for alt
  # and MAP.
  p10() {
    setup "P10 non-generation profile entries ignored"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $A; gen $B; gen $X
    mkdir -p "$store/$X-nixos-system-mugge"
    ln -s "$store/$X-nixos-system-mugge" "$profiles/system-foo"
    ln -s "$store/$X-nixos-system-mugge" "$profiles/system-foo-link"
    boot $C
    run $C
    expect_dirs $B $C
    expect_map "1 $A pruned" "2 $B present" "3 $C present"
    pass
  }

  # (P11) Booted unknown, previous known (chroot reinstall over existing
  # profiles): g/ is pruned by the normal rules.
  p11() {
    setup "P11 unknown booted: g/ pruned normally"
    link 1 $A; link 2 $B; link 3 $C
    inst $C
    gen $A; gen $B; gen $X
    run $C
    expect_dirs $B $C
    expect_map "1 $A pruned" "2 $B present" "3 $C present"
    pass
  }

  # (P12) <id8> collision in the prune: generation 3 is A2 (A's <id8>):
  # not present, so not the alt; the alt is A. MAP says A2 pruned.
  p12() {
    setup "P12 id8 collision is not present"
    link 1 $A; link 2 $B; link 3 $A2; link 4 $C
    inst $C
    gen $A
    boot $C
    run $C
    expect_dirs $A $C
    expect_map "1 $A present" "2 $B pruned" "3 $A2 pruned" "4 $C present"
    pass
  }

  # ---- Step 3: legacy gens/ (SecSpec L1-L4, architect 63e41531 M4-M6) --

  # (13) First L1s deploy over the legacy layout: booted = prev = chosen
  # = legacy C, new D is the only g/ generation. No legacy dir is removed
  # (M5), gens/MAP.txt stays.
  c13() {
    setup "13 first L1s deploy removes no legacy dir"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D
    lgen $A; lgen $B; lgen $C; mkdir -p "$legacy/$X.tmp"
    printf '1 %s pruned\n' $A > "$legacy/MAP.txt"
    oldraw "gens/$C/"
    lboot $C
    before=$(snap "$legacy")
    run $D
    expect_dirs $D
    [ "$(snap "$legacy")" = "$before" ] || fail "gens/ changed"
    expect_map "1 $A legacy" "2 $B legacy" "3 $C legacy" "4 $D present"
    pass
  }

  # (14) Second L1s deploy without a reboot: legacy prev C, booted and
  # chosen legacy B, g/ holds D, new E. Both B and C are kept, A goes;
  # gens/MAP.txt goes, gens/ stays.
  c14() {
    setup "14 legacy prev, booted and chosen kept"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D; link 5 $E
    lgen $A; lgen $B; lgen $C
    printf '1 %s pruned\n' $A > "$legacy/MAP.txt"
    gen $D
    oldraw "gens/$C/"
    lboot $B
    run $E
    expect_dirs $D $E
    expect_legacy $B $C
    [ ! -e "$legacy/MAP.txt" ] || fail "gens/MAP.txt still exists"
    expect_map "1 $A pruned" "2 $B legacy" "3 $C legacy" "4 $D present" "5 $E present"
    pass
  }

  # (15) Second L1s deploy after rebooting into D: prev = booted = chosen
  # = D in g/. Legacy C and its stale .tmp are removed, then gens/MAP.txt
  # and the empty gens/ itself.
  c15() {
    setup "15 second L1s deploy removes the legacy tree"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C; mkdir -p "$legacy/$C.tmp"
    printf '3 %s legacy\n' $C > "$legacy/MAP.txt"
    gen $D
    oldcfg $D
    boot $D
    run $E
    expect_dirs $D $E
    expect_legacy
    expect_map "3 $C pruned" "4 $D present" "5 $E present"
    pass
  }

  # (15b) Only one valid post-fix generation (the previous one has an
  # empty .complete): no legacy delete (QE ad6a8bda X3).
  c15b() {
    setup "15b one present g/ generation: no legacy delete"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C
    part $D; touch "$g/$(short $D)/.complete"
    oldcfg $D
    boot $D
    run $E
    expect_dirs $D $E
    expect_legacy $C
    pass
  }

  # (16) A file in gens/ that is not a generation or MAP.txt keeps gens/
  # in place; the file is not touched.
  c16() {
    setup "16 foreign file keeps gens/"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C; echo notes > "$legacy/notes.txt"
    gen $D
    oldcfg $D
    boot $D
    run $E
    [ "$(cat "$legacy/notes.txt")" = notes ] || fail "gens/notes.txt changed"
    [ -d "$legacy" ] && [ -z "$(dirsof "$legacy")" ] || fail "gens/ dirs: '$(dirsof "$legacy")', want none"
    pass
  }

  # (16b) Directories in gens/ whose names are not 32 Nix base32
  # characters (or that plus .tmp) survive, and so does gens/ (L1, X5).
  c16b() {
    setup "16b foreign directory names in gens/ survive"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C; lgen $FE; lgen $FU
    mkdir -p "$legacy/notes" "$legacy/$C.bak" "$legacy/$(short $C)" "$legacy/''${C}c"
    gen $D
    oldcfg $D
    boot $D
    run $E
    expect_legacy $FE $FU notes "$C.bak" "$(short $C)" "''${C}c"
    pass
  }

  # (16c) A symlink in gens/ is not followed or removed.
  c16c() {
    setup "16c symlink in gens/ untouched"
    link 3 $C; link 4 $D; link 5 $E
    lgen $C
    mkdir -p "$root/outside"; echo out > "$root/outside/file"
    ln -s "$root/outside" "$legacy/$B"
    gen $D
    oldcfg $D
    boot $D
    run $E
    [ -L "$legacy/$B" ] && [ "$(cat "$root/outside/file")" = out ] || fail "symlink or its target touched"
    pass
  }

  # (17) Unknown previous pointer (architect 63e41531 A3, QE ad6a8bda X1):
  # nothing is removed in g/ or gens/; the pointer and g/MAP.txt are
  # written. Booted, chosen and two present generations are all known, so
  # only the previous pointer blocks.
  c17() {
    for p in "$CT$(cut -c1-7 <<< $C)/" "$CT$(cut -c1-9 <<< $C)/" "gens/$(cut -c1-31 <<< $C)/" "gens/''${C}c/" \
      "$CT"'cccccc_c/' "$CT"'cccccccC/' "gens/$(cut -c1-31 <<< $C)e/" "gens/$(cut -c1-31 <<< $C)u/" \
      "$CT$(short $C)/ " "$CT$(short $C)/"$'\r' "" "$CT$(short $C)" "../$(short $C)/" "$CT$(short $C)/x/" \
      "$(short $C)/" "two" "none"; do
      setup "17 unknown prev '$p' removes nothing"
      link 1 $A; link 2 $B; link 3 $D
      gen $A; gen $B; gen $C; lgen $A; lgen $C
      printf '1 %s legacy\n' $A > "$legacy/MAP.txt"
      case "$p" in
        two) oldcfg $C; echo "os_prefix=$CT$(short $C)/" >> "$fw/config.txt" ;;
        none) oldcfg $C; grep -v '^os_prefix=' "$fw/config.txt" > "$root/c"; mv "$root/c" "$fw/config.txt" ;;
        *) oldraw "$p" ;;
      esac
      boot $B
      before=$(snapold $D | grep -v '^\./config\.txt')
      run $D
      [ "$(snapold $D | grep -v '^\./config\.txt')" = "$before" ] || fail "a directory changed"
      expect_dirs $A $B $C $D
      expect_legacy $A $C
      expect_pointer $D
      expect_map "1 $A present" "2 $B present" "3 $D present"
      pass
    done
  }

  # (19) Booted unknown, populated gens/ (a8f9d760 S3, QE da578961 D1):
  # every legacy dir survives byte-identical, gens/ survives; g/ is
  # pruned by the normal rules.
  c19() {
    setup "19 unknown booted: gens/ untouched, g/ pruned"
    link 2 $B; link 3 $C; link 4 $D; link 5 $E
    gen $B; gen $D; lgen $C
    printf '3 %s legacy\n' $C > "$legacy/MAP.txt"
    oldcfg $D
    chosen "$CT$(short $D)/"
    before=$(snap "$legacy")
    run $E
    expect_dirs $D $E
    [ "$(snap "$legacy")" = "$before" ] || fail "gens/ changed"
    pass
  }

  # (20) chosen/os_prefix unreadable (a directory), absent or not one of
  # the two forms: every legacy dir survives (SecSpec L2).
  c20() {
    for how in unreadable absent junk; do
      setup "20 chosen $how: gens/ untouched"
      link 3 $C; link 4 $D; link 5 $E
      gen $D; lgen $C
      oldcfg $D
      boot $D
      case "$how" in
        unreadable) rm -f "$root/chosen"; mkdir "$root/chosen" ;;
        absent) rm -f "$root/chosen" ;;
        junk) chosen "/" ;;
      esac
      before=$(snap "$legacy")
      run $E 2>/dev/null
      expect_dirs $D $E
      [ "$(snap "$legacy")" = "$before" ] || fail "gens/ changed"
      pass
    done
  }

  # (21) chosen points into gens/ (tryboot of a legacy copy): that dir is
  # kept, the others go.
  c21() {
    setup "21 chosen in gens/ is kept"
    link 2 $B; link 3 $C; link 4 $D; link 5 $E
    lgen $B; lgen $C
    gen $D
    oldcfg $D
    boot $D
    chosen "gens/$B/"
    run $E
    expect_dirs $D $E
    expect_legacy $B
    pass
  }

  # (22) chosen points into g/: that g/ dir is kept.
  c22() {
    setup "22 chosen in g/ is kept"
    link 1 $A; link 2 $B; link 3 $C; link 4 $D
    gen $A; gen $B; gen $C
    oldcfg $C
    boot $C
    chosen "$CT$(short $A)/"
    run $D
    expect_dirs $A $C $D
    pass
  }

  # ---- Guards (SecSpec L5, 8d1e41d2 N4) -------------------------------

  # (24-26) Empty FAT root, relative FAT root, not vfat: die, nothing
  # touched.
  c24() {
    setup "24 empty FAT root dies"
    link 1 $D
    before=$(snap)
    if "$S" "" "$store/$D-nixos-system-mugge" "$TMPL" "$profiles" "$root/booted" "$root/chosen" 2> "$root/err"; then
      fail "did not die"
    fi
    grep -qF "empty FAT root" "$root/err" || fail "message: $(cat "$root/err")"
    [ "$(snap)" = "$before" ] || fail "FAT changed"
    pass
  }
  c25() {
    setup "25 relative FAT root dies"
    link 1 $D
    before=$(snap)
    if (cd "$root" && "$S" fw "$store/$D-nixos-system-mugge" "$TMPL" "$profiles" "$root/booted" "$root/chosen") 2> "$root/err"; then
      fail "did not die"
    fi
    grep -qF "is not absolute" "$root/err" || fail "message: $(cat "$root/err")"
    [ "$(snap)" = "$before" ] || fail "FAT changed"
    pass
  }
  c26() {
    setup "26 non-vfat FAT root dies"
    link 3 $C; link 4 $D; link 5 $E
    gen $D; lgen $C
    oldcfg $D
    boot $D
    before=$(snap)
    FAKE_FSTYPE=ext4 runfail $E "is not a mounted vfat filesystem (got 'ext4')"
    [ "$(snap)" = "$before" ] || fail "FAT changed"
    pass
  }

  cases="c1 c2 c3a c3b c3c c9 c9b c10 c10b c11 p1 p1b p2a p2b p2c p3 p4 p5 p6 p7 p7b p8 p10 p11 p12
    c13 c14 c15 c15b c16 c16b c16c c17 c19 c20 c21 c22 c24 c25 c26"
  for c in $cases; do "$c"; done
  [ "$passed" -eq "$total" ] && [ "$total" -gt 0 ] || { echo "FAIL: $passed/$total" >&2; exit 1; }

  # (8) Negative controls: each guard removed once turns its case red
  # (QE c639203e 8, da578961 C).
  nmut=0
  ${lib.concatMapStrings (m: ''
    if ( S=${m.s}; ${m.c} ) > "$TMPDIR/mutant.log" 2>&1; then
      echo "FAIL: 8 case ${m.c} passed with the ${m.what} removed" >&2
      exit 1
    fi
    echo "PASS: 8 case ${m.c} red with the ${m.what} removed"
    nmut=$((nmut + 1))
  '') mutants}

  echo "$passed/$total cases passed, $nmut/${toString (builtins.length mutants)} negative controls red"
  echo "$passed/$total cases passed, $nmut/${toString (builtins.length mutants)} negative controls red" > $out
''
