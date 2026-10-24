# installer.nix — RAM-only NixOS installer for the Pi 5 bootstrap (US-163)
#
# The Raspbian kernel on the Pi 5 has no kexec, so nixos-anywhere cannot
# switch into its installer the usual way. Instead (architect ruling,
# install path D):
#
#   1. Copy system.build.pi5TrybootBundle into Raspbian's /boot/firmware:
#      nixos-installer/ (kernel, initrd, cmdline.txt, DTBs, overlays) and
#      tryboot.txt. config.txt, cmdline.txt and the Raspbian kernels are
#      not touched.
#   2. sudo reboot '0 tryboot'. The firmware reads tryboot.txt instead of
#      config.txt for this one boot only; the next power cycle brings
#      Raspbian back.
#   3. The installer runs entirely from RAM (netboot layout: squashfs store
#      inside the initrd, tmpfs root), so the SD card stays unmounted and
#      nixos-anywhere --phases disko,install,reboot can repartition it.
#
# SSH (security ruling): only the users.nix keys, for ela (sudo). No
# password authentication, no root login, no account with a password or an
# empty password. Host keys are generated on each boot; the installer hop
# is the only place where host-key checking may be relaxed.
{ config, lib, pkgs, modulesPath, ... }:

let
  installerDir = "nixos-installer";

  tryboot = pkgs.writeText "tryboot.txt" ''
    # Pi 5 NixOS installer, one-shot via "reboot '0 tryboot'" (US-163).
    [all]
    arm_64bit=1
    enable_uart=1
    force_eeprom_read=0
    dtparam=audio=off
    dtoverlay=disable-bt-pi5
    kernel=Image
    initramfs initrd followkernel
    cmdline=cmdline.txt
    os_prefix=${installerDir}/
  '';

  kernelDir = config.boot.kernelPackages.kernel;
in
{
  imports = [
    "${modulesPath}/installer/netboot/netboot.nix"
    ../options.nix
    ../../users.nix
    ./hardware.nix
  ];

  mugge.board = {
    name = "pi5";
    net.matchDriver = "macb";
    hat.blockHifiberry = true;
  };

  system.stateVersion = "25.11";
  networking.hostName = "mugge-installer";

  # The cached nixpkgs RPi kernel (bcm2711_defconfig): no local kernel build.
  boot.kernelPackages = pkgs.linuxPackages_rpi4;
  # hardware.nix forces the SD/USB root modules; add the netboot store ones.
  boot.initrd.availableKernelModules = lib.mkForce [ "squashfs" "overlay" "loop" ];
  netboot.squashfsCompression = "zstd -Xcompression-level 6";

  # Accounts: ela with the users.nix keys only. root stays locked.
  users.mutableUsers = false;
  users.users.root.hashedPassword = "!";

  services.openssh = {
    enable = true;
    settings = {
      PasswordAuthentication = false;
      KbdInteractiveAuthentication = false;
      PermitRootLogin = "no";
    };
  };

  # Nothing but SSH inbound.
  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 22 ];
  };

  nix.settings = {
    experimental-features = [ "nix-command" "flakes" ];
    trusted-users = [ "root" "ela" ];
  };

  # nixos-anywhere copies the disko script and the system closure; the
  # install phase runs nixos-install from PATH on the target.
  environment.systemPackages = [
    config.system.build.nixos-install
    pkgs.dosfstools
    pkgs.e2fsprogs
    pkgs.gptfdisk
    pkgs.parted
  ];

  # Closure trims, as in base.nix.
  documentation.enable = false;
  hardware.enableAllHardware = lib.mkForce false;
  boot.initrd.includeDefaultModules = false;
  boot.supportedFilesystems = lib.mkForce [ "ext4" "vfat" "squashfs" ];
  services.speechd.enable = false;
  boot.initrd.services.lvm.enable = false;

  # Files for Raspbian's /boot/firmware.
  system.build.pi5TrybootBundle = pkgs.runCommand "pi5-tryboot-bundle" { } ''
    d=$out/${installerDir}
    mkdir -p $d
    cp ${kernelDir}/Image $d/Image
    cp ${config.system.build.netbootRamdisk}/initrd $d/initrd
    echo "init=${config.system.build.toplevel}/init ${toString config.boot.kernelParams}" > $d/cmdline.txt
    for dtb in bcm2712-rpi-5-b.dtb bcm2712d0-rpi-5-b.dtb bcm2712-d-rpi-5-b.dtb; do
      cp ${kernelDir}/dtbs/broadcom/$dtb $d/$dtb
    done
    cp -r ${kernelDir}/dtbs/overlays $d/overlays
    chmod u+w $d/overlays
    # The firmware only uses a prefixed overlays/ if it has a README.
    echo "Overlays for the Pi 5 NixOS installer" > $d/overlays/README
    cp ${tryboot} $out/tryboot.txt
    (cd $out && find . -type f | sort | xargs sha256sum) > $out/SHA256SUMS
  '';
}
