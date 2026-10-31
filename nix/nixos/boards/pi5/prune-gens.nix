# prune-gens.nix — step 3 of the Pi 5 bootloader hook (bootloader.nix)
#
# Usage: prune-pi5-gens <fw> <profiles> <new> <prev> <booted>
#   <fw>        FAT root (/boot/firmware); generations live in <fw>/g
#   <profiles>  system profile directory (/nix/var/nix/profiles)
#   <new>       full id of the generation config.txt now points to
#   <prev>      os_prefix= value of the previous config.txt (g/<id8>/,
#               or gens/<id>/ from before layout L1s), or ""
#   <booted>    full id of /run/booted-system, or "" (nixos-install chroot)
#
# <id> is the 32-character toplevel hash, <id8> its first idLen
# characters (US-172 layout L1s, architect ruling 04d8b687). A directory
# g/<id8> is "present" for <id> only if its .complete holds <id>.
#
# Keeps new, previous, booted and the newest other present generation, so
# >=2 generations remain whenever >=2 exist (AC2a). "Newest other present"
# is the highest-numbered system-N-link whose id is not <new> and that is
# present in g/. Directories are only ever kept, never recreated: an
# already-pruned generation stays pruned. Then rewrites <fw>/g/MAP.txt
# (profile generation -> id -> present/legacy/pruned).
#
# Legacy layout: gens/<id> is removed unless it is previous or booted.
# gens/MAP.txt goes (g/MAP.txt lists the legacy ones), and gens/ once it
# is empty. Nothing else at the FAT root is touched.
#
# A separate script so that nix/checks/pi5-prune-gens.nix runs exactly
# this code against fake directories. PATH is set explicitly so the same
# GNU tools run on the Pi and in the check; binPath is exported so the
# check can swap in host tools and nothing else.
{ lib, pkgs, idLen }:

let
  binPath = lib.makeBinPath [ pkgs.coreutils pkgs.gnused ];
  q = n: lib.concatStrings (lib.genList (_: "?") n);
in
pkgs.writeShellScript "prune-pi5-gens" ''
  set -euo pipefail
  export PATH=${binPath}

  fw="$1"
  profiles="$2"
  id="$3"
  prev="$4"
  booted="$5"

  g="$fw/g"
  legacy="$fw/gens"
  short() { echo "$1" | cut -c1-${toString idLen}; }
  # present <id>: g/<id8> is a complete generation of exactly <id>.
  present() { [ -n "$1" ] && [ "$(cat "$g/$(short "$1")/.complete" 2>/dev/null)" = "$1" ]; }

  id8=$(short "$id")
  booted8=""
  [ -z "$booted" ] || booted8=$(short "$booted")
  prev8=""
  prevlegacy=""
  case "$prev" in
    g/${q idLen}/) prev8=''${prev#g/}; prev8=''${prev8%/} ;;
    gens/${q 32}/) prevlegacy=''${prev#gens/}; prevlegacy=''${prevlegacy%/} ;;
  esac

  # Newest other present generation. Compare N numerically (10 > 9), not
  # in glob order.
  alt8=""
  altn=-1
  for link in "$profiles"/system-*-link; do
    [ -e "$link" ] || continue
    n=$(basename "$link" | sed 's/^system-\(.*\)-link$/\1/')
    case "$n" in ""|*[!0-9]*) continue ;; esac
    h=$(basename "$(readlink -f "$link")" | cut -c1-32)
    [ "$h" != "$id" ] || continue
    present "$h" || continue
    if [ "$n" -gt "$altn" ]; then
      alt8=$(short "$h")
      altn="$n"
    fi
  done

  for d in "$g"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    case "$name" in
      "$id8"|"$prev8"|"$booted8"|"$alt8") ;;
      *) rm -rf "$d" ;;
    esac
  done

  if [ -d "$legacy" ]; then
    for d in "$legacy"/*/; do
      [ -d "$d" ] || continue
      name=$(basename "$d")
      case "$name" in
        "$prevlegacy"|"$booted") ;;
        *) rm -rf "$d" ;;
      esac
    done
    rm -f "$legacy/MAP.txt" "$legacy/MAP.txt.new"
    rmdir "$legacy" 2>/dev/null || true
    sync "$fw"
  fi

  # Map of profile generations to directories, for manual recovery.
  : > "$g/MAP.txt.new"
  for link in "$profiles"/system-*-link; do
    [ -e "$link" ] || continue
    n=$(basename "$link" | sed 's/^system-\(.*\)-link$/\1/')
    case "$n" in ""|*[!0-9]*) continue ;; esac
    h=$(basename "$(readlink -f "$link")" | cut -c1-32)
    state=pruned
    if present "$h"; then
      state=present
    elif [ -e "$legacy/$h/.complete" ]; then
      state=legacy
    fi
    echo "$n $h $state" >> "$g/MAP.txt.new"
  done
  sort -n "$g/MAP.txt.new" -o "$g/MAP.txt.new"
  sync "$g/MAP.txt.new"
  mv -f "$g/MAP.txt.new" "$g/MAP.txt"
  sync "$g"
'' // { inherit binPath; }
