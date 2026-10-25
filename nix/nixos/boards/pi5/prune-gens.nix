# prune-gens.nix — step 3 of the Pi 5 bootloader hook (bootloader.nix)
#
# Usage: prune-pi5-gens <gens> <profiles> <new> <prev> <booted>
#   <gens>      generation directory on the FAT (/boot/firmware/gens)
#   <profiles>  system profile directory (/nix/var/nix/profiles)
#   <new>       id of the generation config.txt now points to
#   <prev>      id the previous config.txt pointed to, or ""
#   <booted>    id of /run/booted-system, or "" (nixos-install chroot)
#
# Keeps new, previous, booted and the newest other present generation, so
# >=2 generations remain whenever >=2 exist (AC2a). "Newest other present"
# is the highest-numbered system-N-link whose id is not <new> and whose
# <gens>/<id>/.complete exists. Directories are only ever kept, never
# recreated: an already-pruned generation stays pruned. Then rewrites
# <gens>/MAP.txt (profile generation -> id -> present/pruned).
#
# A separate script so that nix/checks/pi5-prune-gens.nix runs exactly
# this code against fake directories.
{ lib, pkgs }:

pkgs.writeShellScript "prune-pi5-gens" ''
  set -euo pipefail
  export PATH=${lib.makeBinPath [ pkgs.coreutils pkgs.gnused ]}

  gens="$1"
  profiles="$2"
  id="$3"
  prev="$4"
  booted="$5"

  # Newest other present generation. Compare N numerically (10 > 9), not
  # in glob order.
  alt=""
  altn=-1
  for link in "$profiles"/system-*-link; do
    [ -e "$link" ] || continue
    n=$(basename "$link" | sed 's/^system-\(.*\)-link$/\1/')
    case "$n" in ""|*[!0-9]*) continue ;; esac
    h=$(basename "$(readlink -f "$link")" | cut -c1-32)
    [ "$h" != "$id" ] || continue
    [ -e "$gens/$h/.complete" ] || continue
    if [ "$n" -gt "$altn" ]; then
      alt="$h"
      altn="$n"
    fi
  done

  for d in "$gens"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    case "$name" in
      "$id"|"$prev"|"$booted"|"$alt") ;;
      *) rm -rf "$d" ;;
    esac
  done

  # Map of profile generations to directories, for manual recovery.
  : > "$gens/MAP.txt.new"
  for link in "$profiles"/system-*-link; do
    [ -e "$link" ] || continue
    n=$(basename "$link" | sed 's/^system-\(.*\)-link$/\1/')
    h=$(basename "$(readlink -f "$link")" | cut -c1-32)
    state=pruned
    [ -e "$gens/$h/.complete" ] && state=present
    echo "$n $h $state" >> "$gens/MAP.txt.new"
  done
  sort -n "$gens/MAP.txt.new" -o "$gens/MAP.txt.new"
  sync "$gens/MAP.txt.new"
  mv -f "$gens/MAP.txt.new" "$gens/MAP.txt"
  sync "$gens"
''
