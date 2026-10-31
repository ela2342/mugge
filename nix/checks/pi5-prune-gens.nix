# pi5-prune-gens.nix — offline test of the Pi 5 FAT generation prune (AC2a)
#
# Runs the prune step of the Pi 5 bootloader hook against a fake FAT root
# (g/, legacy gens/) and profile directories, and checks which generation
# directories survive and what g/MAP.txt says. Layout L1s: US-172,
# architect ruling 04d8b687.
#
# target: system.build.pi5PruneGens of the Pi 5 configuration. board-guard
# asserts that the hook calls exactly this store path. On aarch64-linux the
# check runs it as is; on other hosts it runs the same script text with
# only its PATH line swapped for host tools (asserted below).
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
  hostBin = lib.makeBinPath [ pkgs.coreutils pkgs.gnused ];

  pruneGens =
    if pkgs.stdenv.hostPlatform.system == target.system then target
    else if !(lib.hasInfix "export PATH=${targetBin}\n" body)
      || lib.hasInfix builtins.storeDir (lib.replaceStrings [ targetBin ] [ "" ] body)
    then throw "pi5-prune-gens: target script has store references other than its PATH"
    else pkgs.writeShellScript "prune-pi5-gens" (lib.replaceStrings [ targetBin ] [ hostBin ] body);
in
pkgs.runCommand "pi5-prune-gens" { } ''
  set -euo pipefail

  # Fake 32-character ids. A2 shares A's first 8 characters (<id8>).
  A=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  A2=aaaaaaaazzzzzzzzzzzzzzzzzzzzzzzz
  B=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  C=cccccccccccccccccccccccccccccccc
  D=dddddddddddddddddddddddddddddddd
  E=ffffffffffffffffffffffffffffffff
  X=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

  total=0
  passed=0
  fail() { echo "FAIL: $case: $*" >&2; exit 1; }

  # short ID: <id8>, the g/ directory name.
  short() { echo "$1" | cut -c1-8; }

  # setup: fresh fake FAT root and profile directories. The FAT root holds
  # files the prune must never touch.
  setup() {
    case="$1"
    total=$((total + 1))
    root=$(mktemp -d)
    g="$root/g"
    legacy="$root/gens"
    profiles="$root/profiles"
    store="$root/store"
    mkdir -p "$g" "$profiles" "$store" "$root/overlays" "$root/t"
    touch "$root/config.txt" "$root/start4.elf" "$root/overlays/foo.dtbo" "$root/t/keep"
  }
  # link N ID: profile generation N points at a fake toplevel for ID, and
  # the plain "system" link points at the newest system-N-link, as in a
  # real profiles directory.
  link() {
    mkdir -p "$store/$2-nixos-system-mugge"
    ln -s "$store/$2-nixos-system-mugge" "$profiles/system-$1-link"
    ln -sfn "system-$1-link" "$profiles/system"
  }
  # gen ID: complete g/<id8> holding ID. part ID: no .complete.
  # lgen ID: complete legacy gens/<id> (empty .complete, as the old hook
  # wrote it).
  gen() { mkdir -p "$g/$(short "$1")"; touch "$g/$(short "$1")/Image"; echo "$1" > "$g/$(short "$1")/.complete"; }
  part() { mkdir -p "$g/$(short "$1")"; touch "$g/$(short "$1")/Image"; }
  lgen() { mkdir -p "$legacy/$1"; touch "$legacy/$1/Image" "$legacy/$1/.complete"; }
  # run NEW PREV BOOTED: PREV is an id (passed as g/<id8>/) or "".
  # runraw NEW PREV BOOTED: PREV is passed as is (an os_prefix= value).
  run() {
    p=""
    [ -z "$2" ] || p="g/$(short "$2")/"
    ${pruneGens} "$root" "$profiles" "$1" "$p" "$3"
  }
  runraw() { ${pruneGens} "$root" "$profiles" "$@"; }
  # dirsof DIR: directory names in DIR, sorted, space-separated.
  dirsof() { (cd "$1" && find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||' | sort | tr '\n' ' '); }
  # expect_dirs ID...: exactly these g/ directories remain (ids are
  # mapped to <id8>; other names are taken as is).
  expect_dirs() {
    got=$(dirsof "$g")
    want=$(for i in "$@"; do [ "$(echo -n "$i" | wc -c)" -eq 32 ] && short "$i" || echo "$i"; done | sed '/^$/d' | sort | tr '\n' ' ')
    [ "$got" = "$want" ] || fail "g/ dirs: got '$got', want '$want'"
  }
  # expect_legacy ID...: exactly these gens/ directories remain; with no
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
  # expect_map LINE...: g/MAP.txt is exactly these lines, and there is no
  # MAP.txt anywhere else.
  expect_map() {
    want=$(printf '%s\n' "$@")
    got=$(cat "$g/MAP.txt")
    [ "$got" = "$want" ] || fail "MAP.txt: got '$got', want '$want'"
    [ ! -e "$legacy/MAP.txt" ] || fail "gens/MAP.txt still exists"
    [ ! -e "$root/MAP.txt" ] || fail "MAP.txt at the FAT root"
  }
  # expect_root: the FAT root files outside g/ and gens/ are untouched.
  expect_root() {
    for f in config.txt start4.elf overlays/foo.dtbo t/keep; do
      [ -e "$root/$f" ] || fail "$f removed"
    done
  }
  pass() { expect_root; passed=$((passed + 1)); echo "PASS: $case"; }

  # (1) No-op deploy (new = prev = booted) with an older complete
  # generation: the older one is kept, 2 generations remain.
  setup "1 no-op deploy keeps newest other present"
  link 1 $A; link 2 $B; link 3 $C
  gen $B; gen $C
  run $C $C $C
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (1b) As (1) with several older complete generations: only the newest
  # other one is kept.
  setup "1b no-op deploy keeps only the newest other"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; gen $B; gen $C
  run $C $C $C
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (2a) The newest other generation is already pruned: it is not
  # recreated, nothing else is removed.
  setup "2a pruned alt is not recreated"
  link 1 $A; link 2 $B; link 3 $C
  gen $C
  run $C $C $C
  expect_dirs $C
  [ ! -e "$g/$(short $B)" ] || fail "$B recreated"
  expect_map "1 $A pruned" "2 $B pruned" "3 $C present"
  pass

  # (2b) The newest other generation has no .complete: it is not the alt
  # (removed as incomplete), the next older complete one is kept, and no
  # .complete is created.
  setup "2b incomplete alt falls back to next complete"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; part $B; gen $C
  run $C $C $C
  expect_dirs $A $C
  [ ! -e "$g/$(short $B)/.complete" ] || fail "$B/.complete created"
  expect_map "1 $A present" "2 $B pruned" "3 $C present"
  pass

  # (2c) A g/ directory whose .complete is empty (not the full id) is not
  # present: not the alt, removed.
  setup "2c empty .complete is not present"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; part $B; touch "$g/$(short $B)/.complete"; gen $C
  run $C $C $C
  expect_dirs $A $C
  expect_map "1 $A present" "2 $B pruned" "3 $C present"
  pass

  # (3) Normal deploy with 4 generations: new D, previous = booted = C
  # (alt = C too). Everything outside {new, prev, booted, alt} is pruned,
  # including stale .tmp directories.
  setup "3 normal deploy keeps new and prev/booted"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  gen $A; gen $B; gen $C; gen $D
  mkdir -p "$g/$(short $D).tmp" "$g/$(short $X).tmp"
  run $D $C $C
  expect_dirs $C $D
  expect_map "1 $A pruned" "2 $B pruned" "3 $C present" "4 $D present"
  pass

  # (4) Numeric order: system-10 is newer than system-9.
  setup "4 alt by numeric generation order"
  link 9 $A; link 10 $B; link 11 $C
  gen $A; gen $B; gen $C
  run $C $C $C
  expect_dirs $B $C
  expect_map "9 $A pruned" "10 $B present" "11 $C present"
  pass

  # (5) Rollback (T54 pattern): new B, previous = booted = C. The alt is C
  # (newest other present), A is pruned.
  setup "5 rollback keeps new and prev/booted"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; gen $B; gen $C
  run $B $C $C
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (6) Fresh install: one generation, no previous, nothing booted. Stray
  # directories (complete but unlinked, incomplete) are not kept by the
  # empty prev/booted. No gens/ is created.
  setup "6 fresh install keeps the single generation"
  link 1 $A
  gen $A; gen $X; part $B
  run $A "" ""
  expect_dirs $A
  expect_legacy
  expect_map "1 $A present"
  pass

  # (7) PO clause: the pointer selects an unbooted generation. Booted B,
  # then two deploys without a reboot: prev C (never booted), new D. Keep
  # {B, C, D}; alt = C. A is pruned.
  setup "7 new, prev and booted all kept"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  gen $A; gen $B; gen $C; gen $D
  run $D $C $B
  expect_dirs $B $C $D
  expect_map "1 $A pruned" "2 $B present" "3 $C present" "4 $D present"
  pass

  # (7b) Previous is neither booted nor the alt (booted D, switched to
  # A, then back to D without a reboot): A is kept as previous.
  setup "7b previous kept on its own"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  gen $A; gen $B; gen $C; gen $D
  run $D $A $D
  expect_dirs $A $C $D
  expect_map "1 $A present" "2 $B pruned" "3 $C present" "4 $D present"
  pass

  # (8) Booted generation without a profile link (garbage-collected
  # profile): it is kept anyway; MAP lists only linked generations.
  setup "8 unlinked booted generation kept"
  link 3 $C; link 4 $D
  gen $B; gen $C; gen $D
  run $D $C $B
  expect_dirs $B $C $D
  expect_map "3 $C present" "4 $D present"
  pass

  # (9) Idempotence: case (1) run twice gives the same result.
  setup "9 second run changes nothing"
  link 1 $A; link 2 $B; link 3 $C
  gen $B; gen $C
  run $C $C $C
  run $C $C $C
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (10) Profile entries that are not system-N-link (system-foo,
  # system-foo-link, the plain system link) are ignored for alt and MAP.
  setup "10 non-generation profile entries ignored"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; gen $B; gen $C; gen $X
  mkdir -p "$store/$X-nixos-system-mugge"
  ln -s "$store/$X-nixos-system-mugge" "$profiles/system-foo"
  ln -s "$store/$X-nixos-system-mugge" "$profiles/system-foo-link"
  run $C $C $C
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (11) Empty prev and booted (chroot reinstall over existing profiles):
  # the alt is still kept; a stray complete directory is not.
  setup "11 empty prev and booted keep no stray directory"
  link 1 $A; link 2 $B; link 3 $C
  gen $A; gen $B; gen $C; gen $X
  run $C "" ""
  expect_dirs $B $C
  expect_map "1 $A pruned" "2 $B present" "3 $C present"
  pass

  # (12) <id8> collision: g/aaaaaaaa holds A. Generation 3 is A2 (same
  # <id8>, other id): it is not present, so not the alt; the alt is A
  # (generation 1), whose directory is kept. MAP says A2 pruned. (The hook
  # itself refuses to deploy A2 over A; that is not this script.)
  setup "12 id8 collision is not present"
  link 1 $A; link 2 $B; link 3 $A2; link 4 $C
  gen $A; gen $C
  run $C "" $C
  expect_dirs $A $C
  expect_map "1 $A present" "2 $B pruned" "3 $A2 pruned" "4 $C present"
  pass

  # (13) First L1s deploy over the legacy layout: booted = prev = legacy C
  # (os_prefix=gens/C/), new D in g/. Legacy C is kept; legacy A, B and a
  # stale .tmp are removed; gens/MAP.txt is removed; gens/ stays (C).
  setup "13 first L1s deploy keeps legacy prev/booted"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  lgen $A; lgen $B; lgen $C; mkdir -p "$legacy/$X.tmp"
  printf '1 %s pruned\n' $A > "$legacy/MAP.txt"
  gen $D
  runraw $D "gens/$C/" $C
  expect_dirs $D
  expect_legacy $C
  expect_map "1 $A pruned" "2 $B pruned" "3 $C legacy" "4 $D present"
  pass

  # (14) Legacy prev and booted differ (deployed twice without a reboot
  # under the old layout, booted B, pointer C): both are kept.
  setup "14 legacy prev and booted both kept"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  lgen $A; lgen $B; lgen $C
  gen $D
  runraw $D "gens/$C/" $B
  expect_dirs $D
  expect_legacy $B $C
  expect_map "1 $A pruned" "2 $B legacy" "3 $C legacy" "4 $D present"
  pass

  # (15) Second L1s deploy after rebooting into D: prev = booted = D in
  # g/. Legacy C is neither prev nor booted and is removed, then the empty
  # gens/ itself. A legacy generation is never the alt.
  setup "15 second L1s deploy removes the legacy tree"
  link 3 $C; link 4 $D; link 5 $E
  lgen $C
  gen $D; gen $E
  run $E $D $D
  expect_dirs $D $E
  expect_legacy
  expect_map "3 $C pruned" "4 $D present" "5 $E present"
  pass

  # (16) A file in gens/ that is not a generation or MAP.txt keeps gens/
  # in place; the file is not touched.
  setup "16 foreign file keeps gens/"
  link 3 $C; link 4 $D
  lgen $C; touch "$legacy/notes.txt"
  gen $D
  run $D $D $D
  expect_dirs $D
  [ -e "$legacy/notes.txt" ] || fail "gens/notes.txt removed"
  [ -z "$(dirsof "$legacy")" ] || fail "gens/ dirs left: $(dirsof "$legacy")"
  expect_map "3 $C pruned" "4 $D present"
  pass

  # (17) Malformed previous os_prefix= values keep nothing: no prefix,
  # missing slash, short legacy id, path outside g/.
  for p in "g/$(short $C)" "gens/ccc/" "../$(short $C)/" "g/$(short $C)/x/" "$(short $C)/"; do
    setup "17 malformed prev '$p' keeps nothing"
    link 1 $A; link 2 $B; link 3 $D
    gen $B; gen $C; gen $D; lgen $C
    runraw $D "$p" ""
    expect_dirs $B $D
    expect_legacy
    expect_map "1 $A pruned" "2 $B present" "3 $D present"
    pass
  done

  [ "$passed" -eq "$total" ] && [ "$total" -gt 0 ] || { echo "FAIL: $passed/$total" >&2; exit 1; }
  echo "$passed/$total cases passed"
  echo "$passed/$total cases passed" > $out
''
