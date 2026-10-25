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
{ config, lib, ... }:

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

  # Owner ruling 2026-10-24: "web ui stays open! vnc is not needed right
  # now." No wayvnc and no 5900; 8080 is open on the LAN (F-037,
  # network.nix). The allowlist stays off (backlog), so it can never
  # block the web UI.
  mugge.vnc.enable = false;

  # F-367: no DRM device on the Pi 5 yet (vc4/v3d DT nodes are disabled),
  # so labwc exits and greetd restart-loops. Start greetd only when a DRM
  # card exists (any card*: card0 may be v3d once vc4 loads). A failed
  # condition skips the unit, it is neither failed nor restarting. Not a
  # StartLimit: hitting it leaves the unit failed. Kept until US-172 is
  # confirmed on the Pi 5; the udev rule below starts greetd once the
  # card appears.
  systemd.services.greetd.unitConfig.ConditionPathExistsGlob = "/dev/dri/card*";

  # US-172 AC8: start greetd when the vc4 KMS card appears, at coldplug or
  # later (module autoload), since the condition above is checked only
  # when greetd is started. Matched on the vc4 driver, so that a v3d
  # render-only card cannot start labwc before KMS exists. No After= or
  # BindsTo= on a device unit: without a card that would end in a
  # device-job timeout and a failed unit. Starting a running greetd is a
  # no-op, so later drm uevents (HDMI hotplug) do nothing.
  services.udev.extraRules = lib.mkIf config.services.greetd.enable ''
    SUBSYSTEM=="drm", KERNEL=="card[0-9]*", DRIVERS=="vc4-drm", TAG+="systemd", ENV{SYSTEMD_WANTS}+="greetd.service"
  '';

  # The udev rule is greetd's only starter (Architect). graphical.target
  # would otherwise start it twice over: through wantedBy, and through the
  # display-manager.service alias, which systemd's graphical.target Wants.
  # Either could start labwc on a v3d-only card before KMS exists.
  systemd.services.greetd.wantedBy = lib.mkIf config.services.greetd.enable (lib.mkForce [ ]);
  systemd.services.greetd.aliases = lib.mkIf config.services.greetd.enable (lib.mkForce [ ]);

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
