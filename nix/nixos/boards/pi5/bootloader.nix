# bootloader.nix — Pi 5 direct firmware boot via generation directories
#
# The Pi 5 EEPROM bootloader reads config.txt from the FAT partition. There
# is no U-Boot and no extlinux: every NixOS generation that may be booted
# gets its own directory on the FAT, and config.txt's os_prefix= points the
# firmware at one of them.
#
# os_prefix semantics (Raspberry Pi documentation, config.txt, "os_prefix",
# https://www.raspberrypi.com/documentation/computers/config_txt.html):
#   - "Any value in os_prefix is prepended to the name of any operating
#     system files loaded by the firmware, where 'operating system files'
#     is defined to mean kernels, initramfs, cmdline.txt, .dtbs and
#     overlays." So kernel, initrd and cmdline.txt (which carries
#     init=<toplevel>/init) always switch together with the pointer.
#   - "unless the expected kernel and .dtb can be found at the new
#     location/name, the prefix is ignored (set to "")". A missing or
#     partial generation directory therefore makes the firmware look for
#     /Image at the FAT root, which does not exist: no boot. Hence the
#     explicit .complete check before the pointer is written.
#   - Overlays "will only be loaded from ${os_prefix}${overlay_prefix} ...
#     if ${os_prefix}${overlay_prefix}README exists, otherwise it ignores
#     os_prefix and treats overlays as shared." The kernel's overlays/ has
#     no README, so the hook writes one into every generation.
#
#   /boot/firmware/config.txt            pointer (os_prefix=g/<id8>/)
#   /boot/firmware/g/<id8>/              Image, initrd, cmdline.txt,
#                                        bcm2712*.dtb, overlays/, .complete
#   /boot/firmware/g/MAP.txt             system profile generation -> <id>
#
# <id> is the 32-character store hash of the system toplevel, <id8> its
# first 8 characters. .complete holds the full <id>.
#
# Layout L1s (US-172, architect ruling 04d8b687): the firmware skips any
# file whose path is longer than 48 characters. Under the old
# gens/<id>/ layout the overlay paths were 51-67 characters, so no
# dtoverlay= took effect. The longest path the firmware opens under
# g/<id8>/ is g/<id8>/overlays/vc4-kms-v3d-pi5.dtbo (40); board-guard
# asserts <= 48 for the whole set.
#
# Write sequence (architect ruling):
#   1. Build the generation in g/<id8>.tmp, fsync, rename to g/<id8>,
#      then write .complete (via .complete.new and a rename). A directory
#      without .complete is rebuilt on the next run. A .complete that
#      names another <id> is an 8-character id collision: the hook fails
#      before config.txt is written.
#   2. Check that g/<id8>/.complete names <id>, then write config.txt.new,
#      fsync, rename over config.txt, fsync the FAT root directory.
#   3. Only then prune (prune-gens.nix): keeps new, previous, booted and
#      the newest other present generation, so >=2 whenever >=2 exist
#      (AC2a). Remove all others and any stale .tmp directories. A pruned
#      generation is never recreated. The old gens/<id>/ directories are
#      removed unless previous or booted, and gens/ once it is empty.
#
# Residual risk (accepted): vfat has no atomic rename guarantee. A power
# loss during step 2 can leave config.txt missing or truncated, and the
# firmware will not boot. Recovery: mount the SD card on another machine
# and copy a config.txt that points to an existing g/<id8>/ or gens/<id>/
# (g/MAP.txt lists them). Steps 1 and 3 never touch the generation that the old
# config.txt points to, so that generation is always intact.
#
# config.txt is rendered from the generation being activated, so a
# rollback also rolls back config.txt. The bootstrap system
# (mugge.bootstrap.minimal) has no desktop and gets no vc4-kms overlay.
#
# nixos-install (chroot, no /run/booted-system): the generation install and
# the pointer write run as always; only the "keep the booted generation"
# rule has nothing to keep. A fresh install has one generation.
#
# Device tree: the firmware applies the dtoverlay= lines below to the DTB
# it loads, from g/<id8>/overlays/. NixOS does not merge overlays on the
# Pi 5 (hardware.nix).
{ config, lib, pkgs, ... }:

let
  board = config.mugge.board;

  # The DTBs the Pi 5 firmware may ask for: C1 stepping, D0 stepping, and
  # the name newer firmware uses for D0.
  pi5Dtbs = [ "bcm2712-rpi-5-b.dtb" "bcm2712d0-rpi-5-b.dtb" "bcm2712-d-rpi-5-b.dtb" ];

  # Length of <id8>, the generation directory name (layout L1s).
  idLen = 8;

  pruneGens = import ./prune-gens.nix { inherit lib pkgs idLen; };

  # The position of os_prefix= is not significant for overlays: R5s-b
  # applied them with os_prefix= last (architect ead362c2, 7f064c75). The
  # cause was the path length (header, layout L1s).
  # A dtparam= after a dtoverlay= sets a parameter of that overlay, not of
  # the base DTB. dtparam=audio=off therefore stays directly after the vc4
  # overlay (whose "audio" parameter it sets); the Pi 5 base DTBs have no
  # "audio" parameter.
  configTxt = id: ''
    # Generated by the NixOS Pi 5 bootloader hook (boards/pi5/bootloader.nix).
    # Do not edit: the next nixos-rebuild switch overwrites this file.
    [all]
    arm_64bit=1
    enable_uart=1
  '' + lib.optionalString board.hat.blockHifiberry ''
    # HiFiBerry block, layer (a): do not apply the HAT EEPROM overlay.
    force_eeprom_read=0
  '' + lib.optionalString (!config.mugge.bootstrap.minimal) ''
    # KMS display (D-022) with HDMI audio off: the USBStreamer is the only
    # audio output.
    dtoverlay=vc4-kms-v3d-pi5,noaudio
  '' + ''
    dtparam=audio=off
    dtoverlay=disable-bt-pi5
    kernel=Image
    initramfs initrd followkernel
    cmdline=cmdline.txt
    os_prefix=g/${id}/
  '';

  installHook = pkgs.writeShellScript "install-pi5-bootloader" ''
    set -euo pipefail
    export PATH=${lib.makeBinPath [ pkgs.coreutils pkgs.util-linux pkgs.gnused pkgs.findutils ]}

    top="$1"
    fw=/boot/firmware

    die() { echo "install-pi5-bootloader: $*" >&2; exit 1; }

    # Never write the generation tree into the root filesystem by mistake.
    # Inside the nixos-install chroot the target's /mnt/boot/firmware
    # appears as /boot/firmware, so the same check covers the install.
    fstype=$(findmnt -n -o FSTYPE --mountpoint "$fw" || true)
    [ "$fstype" = vfat ] || die "$fw is not a mounted vfat filesystem (got '$fstype')"

    toplevel=$(readlink -f "$top")
    id=$(basename "$toplevel" | cut -c1-32)
    case "$id" in
      *[!0-9a-z]*) die "unexpected toplevel id '$id'" ;;
      ${lib.concatStrings (lib.genList (_: "?") 32)}) ;;
      *) die "unexpected toplevel id '$id'" ;;
    esac
    id8=$(echo "$id" | cut -c1-${toString idLen})
    gens="$fw/g"
    gen="$gens/$id8"
    kdir=$(dirname "$(readlink -f "$toplevel/kernel")")

    mkdir -p "$gens"

    # 1. Generation directory. An existing one is reused only if its
    # .complete names this <id>; another <id> is an <id8> collision.
    if [ -e "$gen/.complete" ]; then
      have=$(cat "$gen/.complete")
      [ "$have" = "$id" ] || die "$gen/.complete names '$have', not $id (id8 collision); config.txt not changed"
    else
      rm -rf "$gen.tmp" "$gen"
      mkdir -p "$gen.tmp"
      cp -L --no-preserve=mode "$toplevel/kernel" "$gen.tmp/Image"
      cp -L --no-preserve=mode "$toplevel/initrd" "$gen.tmp/initrd"
      echo "init=$toplevel/init $(cat "$toplevel/kernel-params")" > "$gen.tmp/cmdline.txt"
      for dtb in ${lib.escapeShellArgs pi5Dtbs}; do
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
      sync "$gen/.complete" "$gens"
    fi

    # 2. Pointer. Never point at an incomplete generation.
    [ "$(cat "$gen/.complete" 2>/dev/null)" = "$id" ] || die "$gen is incomplete; config.txt not changed"
    # The previous os_prefix= value as written (g/<id8>/, or gens/<id>/
    # from a generation before L1s); prune-gens.nix parses it.
    prev=""
    if [ -f "$fw/config.txt" ]; then
      prev=$(sed -n 's|^os_prefix=||p' "$fw/config.txt" | head -n 1)
    fi
    cat > "$fw/config.txt.new" <<'EOF'
    ${configTxt "@ID@"}
    EOF
    sed -i "s|@ID@|$id8|" "$fw/config.txt.new"
    sync "$fw/config.txt.new"
    mv -f "$fw/config.txt.new" "$fw/config.txt"
    sync "$fw"

    # 3. Prune, then rewrite MAP.txt.
    booted=""
    if [ -e /run/booted-system ]; then
      booted=$(basename "$(readlink -f /run/booted-system)" | cut -c1-32)
    fi
    ${pruneGens} "$fw" /nix/var/nix/profiles "$id" "$prev" "$booted"
  '';
in
{
  boot.loader.external = {
    enable = true;
    inherit installHook;
  };
  # Keep nixpkgs' generic-extlinux-compatible off: nothing reads extlinux.
  boot.loader.generic-extlinux-compatible.enable = lib.mkForce false;
  # Exposed for board-guard; the hook replaces @ID@ with <id8>.
  system.build.pi5ConfigTxt = configTxt "@ID@";
  # Exposed for board-guard's path-length check (US-172 R1).
  system.build.pi5Dtbs = pi5Dtbs;
  system.build.pi5IdLen = idLen;
  # Exposed for board-guard and the pi5-prune-gens check (same script as
  # the hook runs).
  system.build.pi5PruneGens = pruneGens;
}
