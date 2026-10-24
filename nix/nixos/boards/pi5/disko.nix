# disko.nix — SD card layout for the Pi 5 nixos-anywhere install
#
# Layout (MBR, architect ruling: the layout Raspberry Pi OS and every Pi
# firmware release are tested with):
#   Partition 1: 8 MiB to 1 GiB, primary, FAT32 (type 0x0c via parted's
#                fat32 + lba), bootable flag, label FIRMWARE — config.txt
#                plus the generation directories (bootloader.nix). Each
#                generation holds its own kernel, initrd and DTBs (~45 MB),
#                so the partition is sized for several generations
#                (architect ruling: 1 GiB, 512 MiB minimum).
#   Partition 2: rest of disk, primary, type 0x83, ext4, label NIXOS_SD —
#                NixOS root.
#
# The pinned disko only offers MBR through the deprecated "table" type, so
# evaluation prints the legacy-table warning (F-288 stays open).
#
# Running disko against the Raspbian SD card erases it. That is the
# irreversible step of the Pi 5 bootstrap and needs the owner's explicit OK.
#
# The fileSystems overrides keep the by-label/ paths shared with base.nix,
# so nixos-rebuild switch works no matter how the card was partitioned.
{ lib, ... }:

{
  fileSystems."/" = lib.mkForce {
    device = "/dev/disk/by-label/NIXOS_SD";
    fsType = "ext4";
  };

  # Mounted at boot: the bootloader hook writes to it on every switch (F-289).
  fileSystems."/boot/firmware" = lib.mkForce {
    device = "/dev/disk/by-label/FIRMWARE";
    fsType = "vfat";
    options = [ "nofail" ];
  };

  disko.devices.disk.main = {
    type = "disk";
    # SD card. A USB-stick install (fallback) overrides this with
    # --disk main /dev/sda.
    device = lib.mkDefault "/dev/mmcblk0";

    content = {
      type = "table";
      format = "msdos";
      partitions = [
        {
          part-type = "primary";
          fs-type = "fat32";
          start = "8MiB";
          end = "1GiB";
          bootable = true;
          flags = [ "lba" ];
          content = {
            type = "filesystem";
            format = "vfat";
            extraArgs = [ "-F" "32" "-n" "FIRMWARE" ];
            mountpoint = "/boot/firmware";
            mountOptions = [ "nofail" ];
          };
        }
        {
          part-type = "primary";
          start = "1GiB";
          end = "100%";
          content = {
            type = "filesystem";
            format = "ext4";
            # No U-Boot on the Pi 5, so orphan_file (F-273 note in
            # boards/pi4/disko.nix) does not need to be disabled.
            extraArgs = [ "-L" "NIXOS_SD" ];
            mountpoint = "/";
            mountOptions = [ "defaults" ];
          };
        }
      ];
    };
  };
}
