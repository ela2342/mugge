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
# file whose path is too long. Under the old gens/<id>/ layout the
# overlay paths were 51-67 characters, so no dtoverlay= took effect. Two
# path classes have separate limits (KERNEL_CLASS_MAX, OVERLAY_CLASS_MAX
# below). board-guard asserts them on the rendered config.txt, and the
# hook asserts them again on the files it wrote, before the pointer.
#
# Write sequence (architect rulings 04d8b687, 2b485056, 63e41531; all in
# prune-gens.nix):
#   1. Build the generation in g/<id8>.tmp, fsync, rename to g/<id8>,
#      then write .complete (via .complete.new and a rename). A directory
#      without .complete is rebuilt on the next run. A .complete that
#      names another <id> is an 8-character id collision: the hook fails
#      before config.txt is written.
#   2. Check that g/<id8>/.complete names <id> and that every file the
#      firmware opens exists within its class limit, then write
#      config.txt.new, fsync, rename over config.txt, fsync the FAT root.
#   3. Only then prune, and only if the previous os_prefix= is known:
#      keeps new, previous, booted, chosen (the prefix the firmware booted
#      from) and the newest other present generation, so >=2 whenever
#      >=2 exist (AC2a). A pruned generation is never recreated. The old
#      gens/<id>/ directories stay until two g/ generations exist and
#      previous, booted and chosen are all known.
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
# the pointer write run as always. With no previous config.txt nothing is
# pruned; with no booted system no gens/ directory is removed.
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

  # Layout L1s (04d8b687): the generation directory is <container><id8>/.
  # Both are parameters (architect a8f9d760, 63e41531 B); every place that
  # needs them interpolates these two values.
  idLen = 8;
  pi5Container = "g/";

  # Firmware path class limits (US-172 R1), inclusive (architect 94817076).
  # A path is the os_prefix value plus the file name, as the firmware
  # opens it.
  # Kernel class: kernel, initramfs, cmdline and pi5Dtbs. 48: DTBs and
  # kernel loaded at that length (architect 56271517, f0750f9b E2).
  KERNEL_CLASS_MAX = 48;
  # Overlay class: overlays/README, overlay_map.dtb, hat_map.dtb and every
  # dtoverlay= .dtbo. 40: R5s-c applied
  # g/<id8>/overlays/vc4-kms-v3d-pi5.dtbo at that length (architect
  # confirmation aa797ef7, amending 56271517). Raise it only after a new
  # APPLIED test at the new length.
  OVERLAY_CLASS_MAX = 40;

  pruneGens = import ./prune-gens.nix {
    inherit lib pkgs idLen KERNEL_CLASS_MAX OVERLAY_CLASS_MAX;
    container = pi5Container;
    dtbs = pi5Dtbs;
    configTemplate = configTxt "@ID@";
  };

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
    os_prefix=${pi5Container}${id}/
  '';

  # The whole install (generation, pointer, prune) is one script, so the
  # pi5-prune-gens check runs exactly this code offline. The hook's own
  # arguments go last and unchanged: nixos-rebuild calls
  # `install-pi5-bootloader <toplevel>`; the stage-only mode (architect
  # 993d02b6 Q1, SecSpec 6e3cfa20 SO1) is
  # `install-pi5-bootloader --stage-only <toplevel>`. install-pi5-gen
  # parses and checks them (prune-gens.nix).
  installHook = pkgs.writeShellScript "install-pi5-bootloader" ''
    set -euo pipefail
    exec ${pruneGens} /boot/firmware ${pruneGens.templateFile} \
      /nix/var/nix/profiles /run/booted-system /proc/device-tree/chosen/os_prefix "$@"
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
  # Exposed for board-guard's path class checks (US-172 R1).
  system.build.pi5Dtbs = pi5Dtbs;
  system.build.pi5IdLen = idLen;
  system.build.pi5Container = pi5Container;
  system.build.pi5KernelClassMax = KERNEL_CLASS_MAX;
  system.build.pi5OverlayClassMax = OVERLAY_CLASS_MAX;
  # Exposed for board-guard and the pi5-prune-gens check (same script as
  # the hook runs).
  system.build.pi5PruneGens = pruneGens;
}
