# boards/pi4 — Raspberry Pi 4B board modules (US-163)
#
# Everything that differs between the Pi 4B and the Pi 5 lives under
# nix/nixos/boards/<board>/. Each nixosConfiguration imports the shared
# configuration.nix plus exactly one board directory. The deployment method
# (repart-image.nix or disko.nix) is still added at the flake level.
#
# The nixos-hardware.nixosModules.raspberry-pi-4 import is handled at the
# flake level, not here (flake inputs are not visible to modules).
{ lib, ... }:

{
  imports = [
    ./hardware.nix
    ./firmware.nix
  ];

  # Pi 4B initrd modules — only what's needed to mount root from SD/USB.
  # Most are built-in (=y) in our kernel but listed for documentation and
  # safety (availableKernelModules silently skips missing .ko files).
  # Only mmc_block (=m) is strictly required; the rest are =y built-ins.
  boot.initrd.availableKernelModules = lib.mkForce [
    # SD card boot
    "mmc_block"          # SD/MMC block layer (=m, critical)
    # USB storage (for USB boot or recovery)
    "sd_mod"             # SCSI disk — USB storage presents as SCSI (=y)
    "usb_storage"        # USB mass storage class (=y)
    "uas"                # USB Attached SCSI — USB 3.0 fast path (=y)
    # Pi 4 USB host controllers
    "xhci_hcd"           # USB 3.0 HCD (=y)
    "xhci_pci"           # PCI glue for VL805 USB 3.0 chip (=y)
    "pcie_brcmstb"       # Pi 4 PCIe bridge — VL805 sits on PCIe (=y)
    "reset_raspberrypi"  # VL805 firmware loader via VideoCore mailbox (=y)
    # Emergency console
    "usbhid"             # USB keyboard (=y)
    "hid_generic"        # Generic HID fallback (=y)
    # Filesystem (=y built-in, but mkForce kills auto-add from ext.nix)
    "ext4"
  ];
}
