# base.nix — board-independent base system for the audio workstation (US-163)
#
# Everything a mugge machine needs to boot, be reachable and be managed:
# users, network/SSH, kernel selection, RT runtime tuning, filesystems and
# closure trims. No audio stack, display or custom services — those are
# added by configuration.nix on top of this.
#
# The Pi 5 bootstrap system (nixosConfigurations.mugge-pi5-bootstrap) imports
# only base.nix plus its board directory, so its first install needs no
# PipeWire/Mesa/Rust builds and produces no audio by construction.
{ config, lib, pkgs, ... }:

{
  imports = [
    ./boards/options.nix
    ./users.nix
    ./network.nix
    # Phase 5: PREEMPT_RT kernel (D-013 mandatory)
    ./kernel-rt.nix
    # Phase 5: RT runtime tuning (F-291: sysctl + CPU governor)
    ./rt-tuning.nix
  ];

  # System basics
  system.stateVersion = "25.11";
  time.timeZone = "Europe/Berlin";
  i18n.defaultLocale = "en_US.UTF-8";
  # US-117: Only build en_US.UTF-8 locale (full archive ~222 MiB → ~5 MiB).
  i18n.supportedLocales = [ "en_US.UTF-8/UTF-8" ];

  # Enable flakes on the target system
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
  nix.settings.trusted-users = [ "root" "ela" ];

  # F-273: Shared filesystem declarations — single source of truth for both
  # deployment paths (repart-image.nix and disko.nix). Both produce GPT disks
  # with identical filesystem labels: FIRMWARE (vfat) and NIXOS_SD (ext4).
  # Disko auto-generates fileSystems using by-partlabel/; its mkForce
  # overrides in disko.nix ensure these shared declarations win.
  fileSystems."/" = {
    device = "/dev/disk/by-label/NIXOS_SD";
    fsType = "ext4";
  };
  fileSystems."/boot/firmware" = {
    device = "/dev/disk/by-label/FIRMWARE";
    fsType = "vfat";
    # Not needed at runtime — only the VideoCore bootloader reads this
    # partition, before Linux starts. Mounted on-demand by the firmware.nix
    # activation script when updating firmware files.
    options = [ "nofail" "noauto" ];
  };

  # Closure trim — dedicated audio workstation needs none of these.
  # Audit (2026-03-29): ~5000 derivations in full closure; disabling
  # docs alone saves ~1673 derivations (~33%).
  documentation.nixos.enable = false;  # NixOS manual + manpages
  documentation.doc.enable = false;    # /share/doc tree
  services.speechd.enable = false;     # speech-dispatcher (no screen reader)
  boot.initrd.services.lvm.enable = false;  # LVM not used (simple partition)

  # US-072: Only ext4 + vfat needed (root + firmware partitions).
  # nixos-hardware raspberry-pi-4 or other imported modules may enable
  # additional filesystems by default.  ZFS is the critical one: it is an
  # out-of-tree kernel module whose build pulls the kernel -dev output
  # (full source tree rsync, ~1.5 GB) into the closure, overflowing the
  # 30 GB builder disk.  mkForce replaces the full set.
  boot.supportedFilesystems = lib.mkForce [ "ext4" "vfat" ];

  # US-072: Disable all-hardware installer defaults.
  # The nixos-hardware raspberry-pi-4 module may set enableAllHardware=true,
  # pulling ~50 SCSI/RAID/NVMe/VirtIO initrd modules.  Our custom kernel
  # (kernel-rt.nix) strips SCSI_LOWLEVEL, BLK_DEV_NVME, VIRTUALIZATION,
  # so those modules don't exist -> modules-shrunk build fails.
  hardware.enableAllHardware = lib.mkForce false;

  # Disable kernel.nix default initrd modules (ahci, sata_*, nvme, etc.).
  # Pi 4 has no SATA, NVMe, or PCI storage controllers.
  boot.initrd.includeDefaultModules = false;

  # Board-specific initrd modules: see boards/<board>/default.nix.

  # No LVM or device-mapper on this system.
  boot.initrd.kernelModules = lib.mkForce [];
}
