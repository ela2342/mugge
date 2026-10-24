# board-guard.nix — structural assertions over all NixOS configurations (US-163)
#
# Eval-only regression guard: evaluates every Pi 4 and Pi 5 configuration
# and asserts the board facts that must not drift (QE option (a)). Nothing
# is built for aarch64; the check derivation itself is a text file listing
# the passed assertions, so it runs on any CI host.
#
# Usage: nix build .#checks.<system>.board-guard
# cachedKernel: nixpkgs' aarch64-linux linux_rpi4, the kernel that
# cache.nixos.org substitutes (no local build for the bootstrap).
{ pkgs, nixosConfigurations, cachedKernel }:

let
  inherit (pkgs) lib;

  cfg = name: nixosConfigurations.${name}.config;

  # Every assertion is { name, ok }. A failure aborts evaluation with the
  # configuration and assertion name.
  check = conf: name: ok:
    if ok then "PASS ${conf}: ${name}"
    else throw "board-guard: ${conf}: ${name} FAILED";

  hasNoauto = c: builtins.elem "noauto" c.fileSystems."/boot/firmware".options;
  hasUs156Route = c: c.networking.interfaces ? end0
    && c.networking.interfaces.end0.ipv4.routes != [ ];
  tcpPorts = c: c.networking.firewall.allowedTCPPorts;
  ssh = c: c.services.openssh.settings;

  pi4 = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) [
      { name = "board is pi4"; ok = c.mugge.board.name == "pi4"; }
      { name = "PREEMPT_RT kernel variant"; ok = c.mugge.board.kernel.variant == "rt"; }
      { name = "NVMe stripped (US-114)"; ok = !c.mugge.board.kernel.keepNvme; }
      { name = "U-Boot/extlinux boot"; ok = c.boot.loader.generic-extlinux-compatible.enable; }
      { name = "no external bootloader hook"; ok = !c.boot.loader.external.enable; }
      { name = "5900/8080 open (allowlist is a follow-up)"; ok = builtins.elem 8080 (tcpPorts c) && builtins.elem 5900 (tcpPorts c); }
      { name = "US-156 lab route present"; ok = hasUs156Route c; }
      { name = "PipeWire enabled"; ok = c.services.pipewire.enable; }
    ];

  pi5Common = conf: c: [
    { name = "board is pi5"; ok = c.mugge.board.name == "pi5"; }
    { name = "NVMe kept"; ok = c.mugge.board.kernel.keepNvme; }
    { name = "external bootloader hook"; ok = c.boot.loader.external.enable; }
    { name = "no extlinux"; ok = !c.boot.loader.generic-extlinux-compatible.enable; }
    { name = "no grub"; ok = !c.boot.loader.grub.enable; }
    { name = "no NixOS DT overlays"; ok = c.hardware.deviceTree.overlays == [ ]; }
    { name = "/boot/firmware mounted at boot (F-289)"; ok = !hasNoauto c; }
    { name = "no US-156 lab route"; ok = !hasUs156Route c; }
    { name = "networkd DHCP matched on driver"; ok = c.systemd.network.networks."10-wired".matchConfig.Driver == "macb"; }
    { name = "UI allowlist enabled"; ok = c.mugge.firewall.uiAllowlist.enable; }
    { name = "5900/8080 not in allowedTCPPorts"; ok = !(builtins.elem 8080 (tcpPorts c)) && !(builtins.elem 5900 (tcpPorts c)); }
    { name = "HiFiBerry codec blacklisted"; ok = builtins.elem "snd_soc_pcm512x" c.boot.blacklistedKernelModules; }
    { name = "immutable users"; ok = !c.users.mutableUsers; }
    { name = "no root authorized_keys"; ok = c.users.users.root.openssh.authorizedKeys.keys == [ ]; }
    { name = "PermitRootLogin no"; ok = (ssh c).PermitRootLogin == "no"; }
    { name = "no password authentication"; ok = !(ssh c).PasswordAuthentication; }
    { name = "configurationRevision set"; ok = c.system.configurationRevision != null; }
  ];

  pi5Bootstrap = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) (pi5Common conf c ++ [
      { name = "cached nixpkgs kernel"; ok = c.boot.kernelPackages.kernel.outPath == cachedKernel.outPath; }
      { name = "no audio stack"; ok = !c.services.pipewire.enable; }
    ]);

  pi5Full = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) (pi5Common conf c ++ [
      { name = "PREEMPT_RT kernel variant"; ok = c.mugge.board.kernel.variant == "rt"; }
      { name = "PipeWire enabled"; ok = c.services.pipewire.enable; }
    ]);

  installer = conf:
    let
      c = cfg conf;
      withPassword = lib.filterAttrs (_: u:
        u.password != null || u.initialPassword != null || u.initialHashedPassword != null
        || (u.hashedPassword != null && u.hashedPassword != "!")) c.users.users;
    in map (a: check conf a.name a.ok) [
      { name = "board is pi5"; ok = c.mugge.board.name == "pi5"; }
      { name = "PermitRootLogin no"; ok = (ssh c).PermitRootLogin == "no"; }
      { name = "no password authentication"; ok = !(ssh c).PasswordAuthentication; }
      { name = "no keyboard-interactive authentication"; ok = !(ssh c).KbdInteractiveAuthentication; }
      { name = "no root authorized_keys"; ok = c.users.users.root.openssh.authorizedKeys.keys == [ ]; }
      { name = "no account with a password"; ok = withPassword == { }; }
      { name = "only SSH inbound"; ok = tcpPorts c == [ 22 ]; }
      { name = "no audio stack"; ok = !c.services.pipewire.enable; }
    ];

  results = pi4 "mugge" ++ pi4 "mugge-deploy"
    ++ pi5Bootstrap "mugge-pi5-bootstrap" ++ pi5Full "mugge-pi5"
    ++ installer "pi5-installer";
in
pkgs.writeText "board-guard" (lib.concatStringsSep "\n" results + "\n")
