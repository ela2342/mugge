# boards/pi5 — Raspberry Pi 5 board modules (US-163, Pi 5 bootstrap)
#
# The Pi 5 (BCM2712 + RP1 southbridge) boots directly from its EEPROM
# firmware: no bootcode.bin/start*.elf on the SD card, no U-Boot. The
# firmware reads config.txt from the FAT partition and loads kernel, initrd,
# cmdline.txt, DTB and overlays from the generation directory that config.txt
# points to (see bootloader.nix).
#
# nixos-hardware is not used for the Pi 5 (architect ruling): the kernel is
# either the cached nixpkgs linux_rpi4 (bcm2711_defconfig, which boots the
# Pi 5 with 4K pages) or our RT build (kernel-rt.nix) with the Pi 5
# bcm2712_defconfig (16K pages, US-172 R6a).
{ lib, ... }:

{
  imports = [
    ./hardware.nix
    ./bootloader.nix
  ];

  mugge.board = {
    name = "pi5";
    # Keep the NVMe driver: the Pi 5 has a PCIe connector for an NVMe HAT.
    kernel.keepNvme = true;
    # US-172 R6a: the Pi 5 kernel config for the RT build (16K pages).
    kernel.defconfig = "bcm2712_defconfig";
    # RP1 Ethernet (Cadence GEM). DHCP is matched on the driver, not on the
    # interface name: record the observed name after first boot.
    net.matchDriver = "macb";
    watchdog.device = "bcm2835-wdt";
    # A HiFiBerry DAC+ HAT is fitted on the bench Pi 5 (.88). Block it.
    hat.blockHifiberry = true;
  };

  # Owner ruling 2026-10-24: "web ui stays open! vnc is not needed right
  # now." No wayvnc and no 5900; 8080 is open on the LAN (F-037,
  # network.nix). The allowlist stays off (backlog), so it can never
  # block the web UI.
  mugge.vnc.enable = false;

  # F-367: no DRM device on the Pi 5 yet (vc4/v3d DT nodes are disabled),
  # so labwc exits and greetd restart-loops. Start greetd only when a DRM
  # card exists (any card*: card0 may be v3d once vc4 loads). A failed
  # condition skips the unit, it is neither failed nor restarting. Not a
  # StartLimit: hitting it leaves the unit failed. The display follow-up
  # story must order greetd after the DRM device, since this condition is
  # checked only once at boot.
  systemd.services.greetd.unitConfig.ConditionPathExistsGlob = "/dev/dri/card*";

  # ela's user manager (PipeWire and the audio stack) was started by the
  # greetd autologin. With greetd skipped, linger starts it at boot.
  users.users.ela.linger = true;

  # /boot/firmware is written on every switch (bootloader.nix), so it must
  # be mounted at boot (F-289). No noauto.
  fileSystems."/boot/firmware".options = lib.mkForce [ "nofail" ];

  # Key-only, declarative accounts (security ruling, AC8). ela has no
  # password at all; sudo stays passwordless (accepted risk).
  users.mutableUsers = false;
}
