# prune-gens.nix — steps 1-3 of the Pi 5 bootloader hook (bootloader.nix)
#
# Usage: install-pi5-gen <fw> <toplevel> <template> <profiles> <booted> <chosen>
#   <fw>        FAT root (/boot/firmware); must be absolute and a mounted vfat
#   <toplevel>  the system toplevel being activated
#   <template>  config.txt with @ID@ for <id8> (bootloader.nix configTxt)
#   <profiles>  system profile directory (/nix/var/nix/profiles)
#   <booted>    /run/booted-system (absent in the nixos-install chroot)
#   <chosen>    /proc/device-tree/chosen/os_prefix, the prefix the firmware
#               booted from
#
# <id> is the 32-character toplevel hash, <id8> its first idLen
# characters (US-172 layout L1s, architect ruling 04d8b687). A directory
# g/<id8> is "present" for <id> only if its .complete holds <id>.
#
# 1. Generation: build g/<id8> (via g/<id8>.tmp), or reuse it if its
#    .complete holds <id>. Another <id> there is an <id8> collision: die.
# 2. Pointer: every file the firmware opens must exist in g/<id8>/ and fit
#    its path class limit (architect 2b485056 item 4.6); then write
#    config.txt. A die before this point leaves config.txt unchanged.
# 3. Prune, only if the previous os_prefix= is known (architect 63e41531
#    A3; otherwise nothing is deleted). Keeps new, previous, booted,
#    chosen and the newest other present generation, so >=2 generations
#    remain whenever >=2 exist (AC2a). "Newest other present" is the
#    highest-numbered system-N-link whose id is not <new> and that is
#    present in g/. Directories are only ever kept, never recreated.
#    Then rewrites g/MAP.txt (profile generation -> id ->
#    present/legacy/pruned).
#
# Legacy layout gens/<id> (SecSpec acb8fb17 L1-L3, architect 63e41531
# M4-M6): removed only if previous, booted and chosen are all known and
# two post-fix generations are present in g/ (so never on the first L1s
# deploy). Kept: previous, booted, chosen. Only names of exactly 32 Nix
# base32 characters (or that plus .tmp) are removed; gens/MAP.txt goes
# after g/MAP.txt is written, and gens/ itself only by rmdir. Nothing
# else at the FAT root is touched.
#
# A separate script so that nix/checks/pi5-prune-gens.nix runs exactly
# this code against fake directories. It holds no store path except its
# PATH line; binPath is exported so the check can swap in host tools (and
# a findmnt stub) and nothing else.
{ lib, pkgs, idLen, container, KERNEL_CLASS_MAX, OVERLAY_CLASS_MAX, dtbs, configTemplate }:

let
  binPath = lib.makeBinPath [ pkgs.coreutils pkgs.gnused pkgs.util-linux ];
  # Case pattern for n characters of the Nix base32 alphabet (no e o t u).
  b32 = n: lib.concatStrings (lib.genList (_: "[0-9a-df-np-sv-z]") n);
  containerDir = lib.removeSuffix "/" container;
  templateFile = pkgs.writeText "pi5-config.txt" configTemplate;
in
pkgs.writeShellScript "install-pi5-gen" ''
  set -euo pipefail
  export PATH=${binPath}
  export LC_ALL=C

  die() { echo "install-pi5-gen: $*" >&2; exit 1; }

  [ "$#" -eq 6 ] || die "usage: install-pi5-gen <fw> <toplevel> <template> <profiles> <booted> <chosen>"
  fw="$1"
  top="$2"
  template="$3"
  profiles="$4"
  bootedlink="$5"
  chosenfile="$6"

  # Never work on an empty or relative root, and never write the
  # generation tree into the root filesystem by mistake (SecSpec L5).
  # Inside the nixos-install chroot the target's /mnt/boot/firmware
  # appears as /boot/firmware, so the same check covers the install.
  [ -n "$fw" ] || die "empty FAT root"
  case "$fw" in /*) ;; *) die "FAT root '$fw' is not absolute" ;; esac
  fstype=$(findmnt -n -o FSTYPE --mountpoint "$fw" || true)
  [ "$fstype" = vfat ] || die "$fw is not a mounted vfat filesystem (got '$fstype')"

  # Firmware path class limits (US-172 R1, inclusive; bootloader.nix).
  KERNEL_CLASS_MAX=${toString KERNEL_CLASS_MAX}
  OVERLAY_CLASS_MAX=${toString OVERLAY_CLASS_MAX}

  g="$fw/${containerDir}"
  legacy="$fw/gens"
  short() { echo "$1" | cut -c1-${toString idLen}; }
  # present <id>: g/<id8> is a complete generation of exactly <id>.
  present() { [ -n "$1" ] && [ "$(cat "$g/$(short "$1")/.complete" 2>/dev/null)" = "$1" ]; }

  toplevel=$(readlink -f "$top")
  id=$(basename "$toplevel" | cut -c1-32)
  case "$id" in
    ${b32 32}) ;;
    *) die "unexpected toplevel id '$id'" ;;
  esac
  id8=$(short "$id")
  prefix="${container}$id8/"
  gen="$g/$id8"

  # The names config.txt asks for come from the template, so the copies
  # and the pointer cannot drift apart.
  tval() {
    [ "$(sed -n "/$1/p" "$template" | wc -l)" -eq 1 ] || die "config template: need exactly one $2 line"
    v=$(sed -n "s/$1/\1/p" "$template")
    case "$v" in ""|.*|*[!0-9A-Za-z._-]*) die "config template: bad $2 value '$v'" ;; esac
    echo "$v"
  }
  kname=$(tval '^kernel=\(.*\)$' kernel=)
  iname=$(tval '^initramfs \([^ ]*\) followkernel$' initramfs)
  cname=$(tval '^cmdline=\(.*\)$' cmdline=)
  overlays=$(sed -n 's/^dtoverlay=\([^,]*\).*$/\1/p' "$template")
  # Checked before any word splitting of $overlays.
  [ -z "$(printf '%s\n' "$overlays" | sed '/^$/d; /^[0-9A-Za-z_-][0-9A-Za-z._-]*$/d')" ] \
    || die "config template: bad dtoverlay name"
  [ "$(sed -n '/^os_prefix=/p' "$template")" = "os_prefix=${container}@ID@/" ] \
    || die "config template: need exactly one os_prefix=${container}@ID@/ line"

  # Previous pointer: the single os_prefix= line of the old config.txt,
  # wherever it is (architect 63e41531 A1). Zero or several such lines,
  # or any value but the two forms below: unknown.
  prev=""
  if [ -f "$fw/config.txt" ] && [ "$(sed -n '/^os_prefix=/p' "$fw/config.txt" | wc -l)" -eq 1 ]; then
    prev=$(sed -n 's/^os_prefix=//p' "$fw/config.txt")
  fi
  prevknown=""
  prev8=""
  prevlegacy=""
  case "$prev" in
    ${container}${b32 idLen}/) prevknown=1; prev8=''${prev#${container}}; prev8=''${prev8%/} ;;
    gens/${b32 32}/) prevknown=1; prevlegacy=''${prev#gens/}; prevlegacy=''${prevlegacy%/} ;;
  esac

  # Booted and chosen: "" when unknown (SecSpec L2: an unknown value never
  # widens a delete).
  booted=""
  if [ -e "$bootedlink" ]; then
    b=$(readlink -f "$bootedlink" || true)
    b=$(basename "$b" | cut -c1-32)
    case "$b" in ${b32 32}) booted="$b" ;; esac
  fi
  booted8=""
  [ -z "$booted" ] || booted8=$(short "$booted")
  chosenknown=""
  chosen8=""
  chosenlegacy=""
  if [ -r "$chosenfile" ] && c=$(tr -d '\0' < "$chosenfile"); then
    case "$c" in
      ${container}${b32 idLen}/) chosenknown=1; chosen8=''${c#${container}}; chosen8=''${chosen8%/} ;;
      gens/${b32 32}/) chosenknown=1; chosenlegacy=''${c#gens/}; chosenlegacy=''${chosenlegacy%/} ;;
    esac
  fi

  mkdir -p "$g"

  # 1. Generation directory. An existing one is reused only if its
  # .complete names this <id>; another <id> is an <id8> collision
  # (architect a8f9d760 S4).
  if [ -e "$gen/.complete" ]; then
    have=$(cat "$gen/.complete")
    [ "$have" = "$id" ] || die "id8 $id8 already holds toplevel $have, new toplevel $id." \
      "config.txt is unchanged and the running system is unaffected." \
      "Fix: any configuration change re-hashes the toplevel, or remove $gen/ once it is neither booted nor prev."
  else
    kdir=$(dirname "$(readlink -f "$toplevel/kernel")")
    rm -rf "$gen.tmp" "$gen"
    mkdir -p "$gen.tmp"
    cp -L --no-preserve=mode "$toplevel/kernel" "$gen.tmp/$kname"
    cp -L --no-preserve=mode "$toplevel/initrd" "$gen.tmp/$iname"
    echo "init=$toplevel/init $(cat "$toplevel/kernel-params")" > "$gen.tmp/$cname"
    for dtb in ${lib.escapeShellArgs dtbs}; do
      cp -L --no-preserve=mode "$kdir/dtbs/broadcom/$dtb" "$gen.tmp/$dtb"
    done
    cp -rL --no-preserve=mode "$kdir/dtbs/overlays" "$gen.tmp/overlays"
    # The firmware only uses a prefixed overlays/ if it has a README.
    echo "Overlays for NixOS generation $toplevel" > "$gen.tmp/overlays/README"
    sync -f "$gen.tmp"
    mv "$gen.tmp" "$gen"
    echo "$id" > "$gen/.complete.new"
    sync "$gen/.complete.new"
    mv "$gen/.complete.new" "$gen/.complete"
    sync "$gen/.complete" "$g"
  fi

  # 2. Pointer. Never point at an incomplete generation, nor at one the
  # firmware cannot read in full: every file it opens must exist and fit
  # its class limit (2b485056 item 4.6).
  [ "$(cat "$gen/.complete" 2>/dev/null)" = "$id" ] || die "$gen is incomplete; config.txt is unchanged"
  fits() {
    p="$prefix$3"
    [ -f "$gen/$3" ] || die "$p is missing; config.txt is unchanged"
    [ "''${#p}" -le "$2" ] || die "$p is ''${#p} characters, over the $1 class limit $2; config.txt is unchanged"
  }
  for f in "$kname" "$iname" "$cname" ${lib.escapeShellArgs dtbs}; do
    fits kernel "$KERNEL_CLASS_MAX" "$f"
  done
  for f in README overlay_map.dtb hat_map.dtb; do
    fits overlay "$OVERLAY_CLASS_MAX" "overlays/$f"
  done
  for o in $overlays; do
    fits overlay "$OVERLAY_CLASS_MAX" "overlays/$o.dtbo"
  done
  sed "s|@ID@|$id8|" "$template" > "$fw/config.txt.new"
  sync "$fw/config.txt.new"
  mv -f "$fw/config.txt.new" "$fw/config.txt"
  sync "$fw"

  # 3. Prune. Unknown previous pointer: delete nothing (63e41531 A3).
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

  if [ -n "$prevknown" ]; then
    for d in "$g"/*/; do
      d=''${d%/}
      [ -d "$d" ] && [ ! -L "$d" ] || continue
      name=$(basename "$d")
      case "$name" in
        "$id8"|"$prev8"|"$booted8"|"$chosen8"|"$alt8") ;;
        ${b32 idLen}|${b32 idLen}.tmp) rm -rf "$d" ;;
      esac
    done
  fi

  # Post-fix generations present in g/ after the prune.
  npost=0
  for d in "$g"/*/; do
    d=''${d%/}
    [ -d "$d" ] && [ ! -L "$d" ] || continue
    name=$(basename "$d")
    case "$name" in ${b32 idLen}) ;; *) continue ;; esac
    c=$(cat "$d/.complete" 2>/dev/null || true)
    case "$c" in ${b32 32}) ;; *) continue ;; esac
    [ "$(short "$c")" = "$name" ] || continue
    npost=$((npost + 1))
  done

  legacygo=""
  if [ -n "$prevknown" ] && [ -n "$booted" ] && [ -n "$chosenknown" ] && [ "$npost" -ge 2 ] \
    && present "$id" && [ -d "$legacy" ] && [ ! -L "$legacy" ]; then
    legacygo=1
  fi
  if [ -n "$legacygo" ]; then
    for d in "$legacy"/*/; do
      d=''${d%/}
      [ -d "$d" ] && [ ! -L "$d" ] || continue
      name=$(basename "$d")
      case "$name" in
        "$prevlegacy"|"$booted"|"$chosenlegacy") ;;
        ${b32 32}|${b32 32}.tmp) rm -rf "$d" ;;
      esac
    done
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

  # gens/MAP.txt only after g/MAP.txt is on disk (SecSpec 8d1e41d2).
  if [ -n "$legacygo" ]; then
    rm -f "$legacy/MAP.txt" "$legacy/MAP.txt.new"
    rmdir "$legacy" 2>/dev/null || true
    sync "$fw"
  fi
'' // { inherit binPath templateFile configTemplate idLen container KERNEL_CLASS_MAX OVERLAY_CLASS_MAX dtbs; }
