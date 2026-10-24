# hardware.nix — Raspberry Pi 5 hardware configuration
{ config, lib, pkgs, ... }:

let
  board = config.mugge.board;
in
{
  # Pi 5 initrd modules — only what's needed to mount root from SD/USB.
  # SD (sdhci-brcmstb), RP1 xHCI (dwc3) and the RP1 MFD are built in (=y)
  # in bcm2711_defconfig. Unlike the Pi 4 there is no VL805/PCIe xHCI glue.
  boot.initrd.availableKernelModules = lib.mkForce [
    # SD card boot
    "mmc_block"          # SD/MMC block layer
    # USB storage (for USB boot or recovery)
    "sd_mod"             # SCSI disk — USB storage presents as SCSI (=y)
    "usb_storage"        # USB mass storage class (=y)
    "uas"                # USB Attached SCSI — USB 3.0 fast path (=y)
    "xhci_hcd"           # USB 3.0 HCD (=y)
    # Emergency console
    "usbhid"             # USB keyboard
    "hid_generic"        # Generic HID fallback
    # Filesystem (=y built-in, but mkForce kills auto-add from ext.nix)
    "ext4"
  ];

  # Serial console on the Pi 5 debug UART connector, plus the HDMI console.
  boot.kernelParams = [ "console=ttyAMA10,115200" "console=tty1" ];

  # The firmware applies dtoverlay= lines from config.txt to the DTB it
  # loads (one source of truth, architect ruling). NixOS must not also merge
  # overlays into its own DTB copy.
  hardware.deviceTree.overlays = lib.mkForce [ ];

  # Wired network: systemd-networkd, DHCP on the NIC matched by type and
  # driver. Wi-Fi is not configured.
  networking.useNetworkd = true;
  networking.useDHCP = false;
  systemd.network.networks."10-wired" = {
    matchConfig = {
      Type = "ether";
    } // lib.optionalAttrs (board.net.matchDriver != null) {
      Driver = board.net.matchDriver;
    };
    networkConfig = {
      DHCP = "yes";
      IPv6AcceptRA = true;
    };
    linkConfig.RequiredForOnline = "routable";
  };

  # HiFiBerry DAC+ block, layer (b): blacklist the codec modules, so the
  # card cannot appear even if an overlay gets loaded. Layer (a) is
  # force_eeprom_read=0 in config.txt (bootloader.nix).
  boot.blacklistedKernelModules = lib.mkIf board.hat.blockHifiberry [
    "snd_soc_hifiberry_dacplus"
    "snd_soc_pcm512x_i2c"
    "snd_soc_pcm512x"
  ];
}
