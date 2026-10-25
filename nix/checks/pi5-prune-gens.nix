# pi5-prune-gens.nix — offline test of the Pi 5 FAT generation prune (AC2a)
#
# Runs the prune step of the Pi 5 bootloader hook
# (nix/nixos/boards/pi5/prune-gens.nix, the same script the hook calls)
# against fake gens/ and profile directories, and checks which generation
# directories survive and what MAP.txt says.
#
# Usage: nix build .#checks.<system>.pi5-prune-gens
{ pkgs }:

let
  pruneGens = import ../nixos/boards/pi5/prune-gens.nix { inherit (pkgs) lib; inherit pkgs; };
in
pkgs.runCommand "pi5-prune-gens" { } ''
  set -euo pipefail

  # Fake 32-character ids.
  A=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  B=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  C=cccccccccccccccccccccccccccccccc
  D=dddddddddddddddddddddddddddddddd

  fail() { echo "FAIL: $case: $*" >&2; exit 1; }

  # setup: fresh fake FAT and profile directories.
  setup() {
    case="$1"
    root=$(mktemp -d)
    gens="$root/gens"
    profiles="$root/profiles"
    store="$root/store"
    mkdir -p "$gens" "$profiles" "$store"
  }
  # link N ID: profile generation N points at a fake toplevel for ID.
  link() {
    mkdir -p "$store/$2-nixos-system-mugge"
    ln -s "$store/$2-nixos-system-mugge" "$profiles/system-$1-link"
  }
  # gen ID: complete generation directory. part ID: no .complete.
  gen() { mkdir -p "$gens/$1"; touch "$gens/$1/Image" "$gens/$1/.complete"; }
  part() { mkdir -p "$gens/$1"; touch "$gens/$1/Image"; }
  run() { ${pruneGens} "$gens" "$profiles" "$@"; }
  # expect_dirs ID...: exactly these directories remain (sorted names).
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
  pass() { echo "PASS: $case"; }

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

  # (3) Normal deploy: new D, previous = booted = C. Older generations and
  # a stale .tmp are pruned.
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

  # (6) Fresh install: one generation, no previous, nothing booted.
  setup "6 fresh install keeps the single generation"
  link 1 $A
  gen $A
  run $A "" ""
  expect_dirs $A
  expect_map "1 $A present"
  pass

  # (7) Prev and booted differ (deploy after a deploy without reboot):
  # new D, prev C, booted B, alt C. A is pruned.
  setup "7 new, prev and booted all kept"
  link 1 $A; link 2 $B; link 3 $C; link 4 $D
  gen $A; gen $B; gen $C; gen $D
  run $D $C $B
  expect_dirs $B $C $D
  expect_map "1 $A pruned" "2 $B present" "3 $C present" "4 $D present"
  pass

  touch $out
''
