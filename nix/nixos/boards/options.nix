# boards/options.nix — board facts consumed by the shared modules (US-163)
#
# Shared modules must not branch on "which board is this". When a shared
# module needs a board-specific fact, it reads one of these options, and the
# board directory (boards/pi4 or boards/pi5) sets it.
{ lib, ... }:

{
  options.mugge.bootstrap.minimal = lib.mkOption {
    type = lib.types.bool;
    default = false;
    description = ''
      First-install system without display or audio stack (Pi 5
      bootstrap). Set per flake configuration, never by editing it in git,
      so the bootstrap system stays rebuildable from any commit.
    '';
  };

  options.mugge.board = {
    name = lib.mkOption {
      type = lib.types.enum [ "pi4" "pi5" ];
      description = "Which Raspberry Pi board this configuration targets.";
    };

    kernel.variant = lib.mkOption {
      type = lib.types.enum [ "rt" "rpi-cached" ];
      default = "rt";
      description = ''
        "rt": the pinned RPi 6.12.62 fork with PREEMPT_RT and the US-114
        strip list (kernel-rt.nix, D-013). Mandatory for anything that
        produces audio.
        "rpi-cached": the unmodified nixpkgs linux_rpi4 (bcm2711_defconfig,
        4K pages, non-RT), substituted from cache.nixos.org. Bootstrap only:
        lets a board's first system install without a local kernel build.
      '';
    };

    kernel.defconfig = lib.mkOption {
      type = lib.types.enum [ "bcm2711_defconfig" "bcm2712_defconfig" ];
      default = "bcm2711_defconfig";
      description = ''
        Raspberry Pi kernel defconfig for the "rt" variant (kernel-rt.nix).
        bcm2711 is the Pi 4 config (4K pages); bcm2712 is the Pi 5 config
        (16K pages). "rpi-cached" ignores it: the cached kernel is always
        bcm2711.
      '';
    };

    kernel.keepNvme = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = ''
        Keep BLK_DEV_NVME in the RT kernel. US-114 strips NVMe because the
        Pi 4B has no NVMe; the Pi 5 has a PCIe connector for an NVMe HAT.
      '';
    };

    net.matchDriver = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = ''
        Kernel driver of the wired NIC. When set, the board configures
        systemd-networkd DHCP by matching Type=ether plus this driver,
        never by interface name (a wrong name on first boot means the box
        goes dark).
      '';
    };

    watchdog.device = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = ''
        Hardware watchdog device, recorded for documentation. The watchdog
        stays disabled (O-24): an unannounced reboot is an unannounced
        USBStreamer transient.
      '';
    };

    hat.blockHifiberry = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = ''
        Block a HiFiBerry DAC+ HAT on three layers (AE ruling,
        AC hifiberry-blocked): no HAT EEPROM overlay (force_eeprom_read=0),
        blacklisted codec modules, and no ALSA card except the USBStreamer.
        An auto-loaded card would be an output outside the D-063 gate.
      '';
    };
  };
}
