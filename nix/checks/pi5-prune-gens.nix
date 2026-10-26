# pi5-prune-gens.nix — offline test of the Pi 5 FAT generation prune (AC2a)
#
# Runs the prune step of the Pi 5 bootloader hook against fake gens/ and
# profile directories, and checks which generation directories survive
# and what MAP.txt says.
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

  # Fake 32-character ids.
  A=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  B=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  C=cccccccccccccccccccccccccccccccc
  D=dddddddddddddddddddddddddddddddd
  X=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

  total=0
  passed=0
  fail() { echo "FAIL: $case: $*" >&2; exit 1; }

  # setup: fresh fake FAT and profile directories.
  setup() {
    case="$1"
    total=$((total + 1))
    root=$(mktemp -d)
    gens="$root/gens"
    profiles="$root/profiles"
    store="$root/store"
    mkdir -p "$gens" "$profiles" "$store"
  }
  # link N ID: profile generation N points at a fake toplevel for ID, and
  # the plain "system" link points at the newest system-N-link, as in a
  # real profiles directory.
  link() {
    mkdir -p "$store/$2-nixos-system-mugge"
    ln -s "$store/$2-nixos-system-mugge" "$profiles/system-$1-link"
    ln -sfn "system-$1-link" "$profiles/system"
  }
  # gen ID: complete generation directory. part ID: no .complete.
  gen() { mkdir -p "$gens/$1"; touch "$gens/$1/Image" "$gens/$1/.complete"; }
  part() { mkdir -p "$gens/$1"; touch "$gens/$1/Image"; }
  run() { ${pruneGens} "$gens" "$profiles" "$@"; }
  # expect_dirs ID...: exactly these directories remain.
  expect_dirs() {
    got=$(cd "$gens" && find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||' | sort | tr '\n' ' ')
    want=$(printf '%s\n' "$@" | sed '/^$/d' | sort | tr '\n' ' ')
    [ "$got" = "$want" ] || fail "dirs: got '$got', want '$want'"
  }
  # expect_map LINE...: MAP.txt is exactly these lines.
  expect_map() {
    want=$(printf '%s\n' "$@")
    got=$(cat "$gens/MAP.txt")
    [ "$got" = "$want" ] || fail "MAP.txt: got '$got', want '$want'"
  }
  pass() { passed=$((passed + 1)); echo "PASS: $case"; }

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
  [ ! -e "$gens/$B" ] || fail "$B recreated"
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
  [ ! -e "$gens/$B/.complete" ] || fail "$B/.complete created"
  expect_map "1 $A present" "2 $B pruned" "3 $C present"
  pass

  # (3) Normal deploy with 4 generations: new D, previous = booted = C
  # (alt = C too). Everything outside {new, prev, booted, alt} is pruned,
  # including a stale .tmp.
  setup "3 normal deploy keeps new and prev/booted"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  gen $A; gen $B; gen $C; gen $D
  mkdir -p "$gens/$D.tmp"
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
  # empty prev/booted.
  setup "6 fresh install keeps the single generation"
  link 1 $A
  gen $A; gen $X; part $B
  run $A "" ""
  expect_dirs $A
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

  [ "$passed" -eq "$total" ] && [ "$total" -gt 0 ] || { echo "FAIL: $passed/$total" >&2; exit 1; }
  echo "$passed/$total cases passed"
  echo "$passed/$total cases passed" > $out
''
