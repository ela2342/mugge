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
# Pi 5 with 4K pages) or our RT build of the same defconfig (kernel-rt.nix).
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
    # RP1 Ethernet (Cadence GEM). DHCP is matched on the driver, not on the
    # interface name: record the observed name after first boot.
    net.matchDriver = "macb";
    watchdog.device = "bcm2835-wdt";
    # A HiFiBerry DAC+ HAT is fitted on the bench Pi 5 (.88). Block it.
    hat.blockHifiberry = true;
  };

  # Fail-closed allowlist for the web UI and wayvnc (security ruling).
  # Addresses are set per host in the flake configuration.
  mugge.firewall.uiAllowlist.enable = true;

  # Key-only, declarative accounts (security ruling, AC8). ela has no
  # password at all; sudo stays passwordless (accepted risk).
  users.mutableUsers = false;
}
