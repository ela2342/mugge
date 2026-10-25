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

  # The hook text calls the exact store path the pi5-prune-gens check runs.
  # Context is dropped only for the string comparison.
  hookRunsPrune = c: lib.hasInfix
    (builtins.unsafeDiscardStringContext "${c.system.build.pi5PruneGens} ")
    (builtins.unsafeDiscardStringContext c.boot.loader.external.installHook.text);
  hasNoauto = c: builtins.elem "noauto" c.fileSystems."/boot/firmware".options;
  hasUs156Route = c: c.networking.interfaces ? end0
    && c.networking.interfaces.end0.ipv4.routes != [ ];
  fw = c: c.networking.firewall;
  tcpPorts = c: (fw c).allowedTCPPorts;
  # Every way a TCP port can be opened: global and per-interface lists and
  # ranges.
  ifaceFw = c: builtins.attrValues (fw c).interfaces;
  allTcpPorts = c: tcpPorts c ++ lib.concatMap (i: i.allowedTCPPorts) (ifaceFw c);
  allTcpRanges = c: (fw c).allowedTCPPortRanges ++ lib.concatMap (i: i.allowedTCPPortRanges) (ifaceFw c);
  allUdp = c: (fw c).allowedUDPPorts ++ (fw c).allowedUDPPortRanges
    ++ lib.concatMap (i: i.allowedUDPPorts ++ i.allowedUDPPortRanges) (ifaceFw c);
  tcpOpen = c: port: builtins.elem port (allTcpPorts c)
    || builtins.any (r: r.from <= port && port <= r.to) (allTcpRanges c);
  firewalled = c: (fw c).enable && c.networking.nftables.enable;
  withPassword = c: lib.filterAttrs (_: u:
    u.password != null || u.initialPassword != null || u.initialHashedPassword != null
    || u.hashedPasswordFile != null
    || (u.hashedPassword != null && u.hashedPassword != "!")) c.users.users;
  hifiberryModules = [ "snd_soc_hifiberry_dacplus" "snd_soc_pcm512x_i2c" "snd_soc_pcm512x" "clk_hifiberry_dacpro" ];
  ssh = c: c.services.openssh.settings;
  rootKeys = c: c.users.users.root.openssh.authorizedKeys.keys;
  configTxt = c: c.system.build.pi5ConfigTxt;
  txtLines = c: lib.splitString "\n" (configTxt c);
  hasVc4 = c: lib.hasInfix "dtoverlay=vc4-kms-v3d-pi5" (configTxt c);
  # US-172: os_prefix= and the OS file lines precede every dtoverlay=/dtparam=.
  lineIdx = c: re: lib.lists.findFirstIndex (l: builtins.match re l != null) null (txtLines c);
  firstDt = c: lineIdx c "dt(overlay|param)=.*";
  osFilesFirst = c: firstDt c != null && lib.all (re: let i = lineIdx c re; in i != null && i < firstDt c)
    [ "os_prefix=gens/@ID@/" "kernel=Image" "initramfs initrd followkernel" "cmdline=cmdline.txt" ];
  # US-172: dtparam=audio=off sets the vc4 overlay's parameter, so it
  # must directly follow that overlay line.
  audioOffAfterVc4 = c: let i = lineIdx c "dtoverlay=vc4-kms-v3d-pi5,noaudio"; in
    i != null && builtins.elemAt (txtLines c) (i + 1) == "dtparam=audio=off";
  greetdOnVc4 = c: lib.hasInfix
    ''DRIVERS=="vc4-drm", TAG+="systemd", ENV{SYSTEMD_WANTS}+="greetd.service"''
    c.services.udev.extraRules;
  # Audio, display and remote-desktop units the bootstrap must not have.
  audioUnitRe = ".*(pipewire|wireplumber|filter-chain|level-bridge|pcm-bridge|pi4audio|pi4-audio|wayvnc|labwc).*";
  audioUnits = c: builtins.filter (n: builtins.match audioUnitRe n != null)
    (builtins.attrNames c.systemd.services ++ builtins.attrNames c.systemd.user.services);
  # Matches the package name only; the rule content is reviewed in
  # configs/wireplumber/54-disable-other-alsa-cards.conf.
  hasCardBlock = c: builtins.any (p: lib.hasInfix "wireplumber-block-cards" p.name)
    c.services.pipewire.wireplumber.configPackages;

  # Real kernel attributes, not only our option (eval-only: no build).
  kernel = c: c.boot.kernelPackages.kernel;
  isRtKernel = c: (kernel c).modDirVersion == "6.12.62"
    && ((kernel c).structuredExtraConfig.PREEMPT_RT.tristate or null) == "y";

  # Evaluated kernel config value: unwraps lib.mkForce and reads the
  # tristate ("n" also covers `option no`). Missing means not set here.
  kconf = c: key: let v = (kernel c).structuredExtraConfig.${key} or null; in
    if v == null then null else (v.content or v).tristate or null;
  # F-366: NVMe-oF selects TLS and breaks TLS=no on every RT kernel.
  nvmeFabricsStripped = c: lib.all (k: kconf c k == "n") [ "NVME_FC" "NVME_TCP" "NVME_TARGET" ];

  # F-358: module-rt direct path, shared by all boards. The fragment is
  # checked in source (eval-only, no build) and must be the one copied into
  # the PipeWire config package. It only overrides the stock entry's args
  # (module.rt.args), so it must not load a module of its own. The match
  # is exact after whitespace normalization: no extra keys or sections.
  rtFragment = let
    lines = lib.splitString "\n" (builtins.readFile ../../configs/pipewire/05-rt-direct.conf);
    code = builtins.filter (l: builtins.match "[[:space:]]*#.*" l == null) lines;
  in lib.concatStringsSep " " (builtins.filter (t: builtins.isString t && t != "")
    (builtins.split "[[:space:]]+" (lib.concatStringsSep " " code)));
  rtDirect = c: rtFragment == lib.concatStringsSep " " [
      "module.rt.args = {" "nice.level = 20" "rt.prio = 88"
      "rt.time.soft = 200000" "rt.time.hard = 200000"
      "rtkit.enabled = false" "rtportal.enabled = false" "}" ]
    && builtins.any (p: lib.hasInfix "pipewire.conf.d/05-rt-direct.conf" (p.buildCommand or ""))
      c.services.pipewire.configPackages;

  pi4 = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) [
      { name = "board is pi4"; ok = c.mugge.board.name == "pi4"; }
      { name = "PREEMPT_RT kernel variant"; ok = c.mugge.board.kernel.variant == "rt"; }
      { name = "kernel 6.12.62 with PREEMPT_RT=y"; ok = isRtKernel c; }
      { name = "NVMe stripped (US-114)"; ok = !c.mugge.board.kernel.keepNvme && kconf c "BLK_DEV_NVME" == "n"; }
      { name = "NVMe-oF stripped (F-366)"; ok = nvmeFabricsStripped c; }
      { name = "U-Boot/extlinux boot"; ok = c.boot.loader.generic-extlinux-compatible.enable; }
      { name = "no external bootloader hook"; ok = !c.boot.loader.external.enable; }
      { name = "5900/8080 open (allowlist is a follow-up)"; ok = builtins.elem 8080 (tcpPorts c) && builtins.elem 5900 (tcpPorts c); }
      { name = "US-156 lab route present"; ok = hasUs156Route c; }
      { name = "PipeWire enabled"; ok = c.services.pipewire.enable; }
      { name = "module-rt direct, RTKit off (F-358)"; ok = rtDirect c; }
      { name = "no ALSA card-block rule (Pi 4 follow-up)"; ok = !hasCardBlock c; }
    ];

  pi5Common = conf: c: [
    { name = "board is pi5"; ok = c.mugge.board.name == "pi5"; }
    { name = "NVMe kept"; ok = c.mugge.board.kernel.keepNvme; }
    { name = "external bootloader hook"; ok = c.boot.loader.external.enable; }
    { name = "hook runs pi5PruneGens (AC2a check target)"; ok = hookRunsPrune c; }
    { name = "no extlinux"; ok = !c.boot.loader.generic-extlinux-compatible.enable; }
    { name = "no grub"; ok = !c.boot.loader.grub.enable; }
    { name = "no NixOS DT overlays"; ok = c.hardware.deviceTree.overlays == [ ]; }
    { name = "/boot/firmware mounted at boot (F-289)"; ok = !hasNoauto c; }
    { name = "no US-156 lab route"; ok = !hasUs156Route c; }
    { name = "networkd DHCP matched on driver"; ok = c.systemd.network.networks."10-wired".matchConfig.Driver == "macb"; }
    # Owner ruling 2026-10-24 ("web ui stays open! vnc is not needed right
    # now"); F-037 accepted risk. The allowlist moved to the backlog.
    { name = "UI allowlist disabled (cannot block 8080)"; ok = !c.mugge.firewall.uiAllowlist.enable; }
    { name = "VNC disabled"; ok = !c.mugge.vnc.enable; }
    { name = "no wayvnc unit or package"; ok = !(c.systemd.user.services ? wayvnc) && !(c.systemd.services ? wayvnc)
        && !builtins.any (p: lib.hasPrefix "wayvnc" (p.pname or p.name or "")) c.environment.systemPackages; }
    { name = "5900 not opened by any port list or range"; ok = !(tcpOpen c 5900); }
    { name = "4001/4002/9100 not opened (localhost only)"; ok = !builtins.any (tcpOpen c) [ 4001 4002 9100 ]; }
    { name = "HiFiBerry modules blacklisted"; ok = lib.all (m: builtins.elem m c.boot.blacklistedKernelModules) hifiberryModules; }
    { name = "config.txt force_eeprom_read=0"; ok = builtins.elem "force_eeprom_read=0" (txtLines c); }
    { name = "config.txt has no HiFiBerry overlay"; ok = !builtins.any (l: builtins.match "dtoverlay=.*(hifiberry|pcm512).*" l != null) (txtLines c); }
    { name = "immutable users"; ok = !c.users.mutableUsers; }
    { name = "no account with a password"; ok = withPassword c == { }; }
    { name = "firewall and nftables enabled"; ok = firewalled c; }
    { name = "disable-bt-pi5 in config.txt"; ok = lib.hasInfix "dtoverlay=disable-bt-pi5" (configTxt c); }
    { name = "config.txt: os_prefix and OS files before any dtoverlay/dtparam (US-172)"; ok = osFilesFirst c; }
    { name = "no root authorized_keys"; ok = rootKeys c == [ ] && c.users.users.root.openssh.authorizedKeys.keyFiles == [ ]; }
    { name = "PermitRootLogin no"; ok = (ssh c).PermitRootLogin == "no"; }
    { name = "no password authentication"; ok = !(ssh c).PasswordAuthentication; }
    { name = "no keyboard-interactive authentication"; ok = !(ssh c).KbdInteractiveAuthentication; }
    { name = "configurationRevision set"; ok = c.system.configurationRevision != null; }
  ];

  pi5Bootstrap = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) (pi5Common conf c ++ [
      { name = "cached nixpkgs kernel"; ok = (kernel c).outPath == cachedKernel.outPath; }
      { name = "bootstrap.minimal set"; ok = c.mugge.bootstrap.minimal; }
      { name = "no audio stack"; ok = !c.services.pipewire.enable; }
      { name = "no audio/display units"; ok = audioUnits c == [ ]; }
      { name = "no vc4-kms overlay"; ok = !hasVc4 c; }
      { name = "8080 not opened (no web UI)"; ok = !(tcpOpen c 8080); }
      { name = "TCP inbound exactly [22]"; ok = allTcpPorts c == [ 22 ] && allTcpRanges c == [ ]; }
    ]);

  pi5Full = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) (pi5Common conf c ++ [
      { name = "PREEMPT_RT kernel variant"; ok = c.mugge.board.kernel.variant == "rt"; }
      { name = "kernel 6.12.62 with PREEMPT_RT=y"; ok = isRtKernel c; }
      { name = "NVMe-oF stripped (F-366)"; ok = nvmeFabricsStripped c; }
      { name = "local NVMe not stripped"; ok = kconf c "BLK_DEV_NVME" == null; }
      { name = "bootstrap.minimal unset"; ok = !c.mugge.bootstrap.minimal; }
      { name = "vc4-kms overlay with noaudio"; ok = lib.hasInfix "dtoverlay=vc4-kms-v3d-pi5,noaudio" (configTxt c); }
      { name = "dtparam=audio=off directly after the vc4 overlay (US-172)"; ok = audioOffAfterVc4 c; }
      { name = "greetd skipped without a DRM card (F-367)"; ok = c.systemd.services.greetd.unitConfig.ConditionPathExistsGlob == "/dev/dri/card*"; }
      { name = "greetd started by the vc4 DRM card (US-172 AC8)"; ok = greetdOnVc4 c; }
      { name = "greetd started only by the udev rule (US-172 AC8)"; ok = c.systemd.services.greetd.wantedBy == [ ] && c.systemd.services.greetd.aliases == [ ]; }
      { name = "PipeWire enabled"; ok = c.services.pipewire.enable; }
      { name = "module-rt direct, RTKit off (F-358)"; ok = rtDirect c; }
      { name = "WirePlumber disables other ALSA cards"; ok = hasCardBlock c; }
      { name = "8080 open on the LAN (owner ruling, F-037)"; ok = builtins.elem 8080 (tcpPorts c); }
      { name = "TCP inbound exactly [22 8080]"; ok = lib.sort lib.lessThan (allTcpPorts c) == [ 22 8080 ] && allTcpRanges c == [ ]; }
    ]);

  installer = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) [
      { name = "board is pi5"; ok = c.mugge.board.name == "pi5"; }
      # Without the kexec phase nixos-anywhere connects as root@ (installer.nix).
      { name = "PermitRootLogin prohibit-password"; ok = (ssh c).PermitRootLogin == "prohibit-password"; }
      { name = "root keys are exactly the ela keys"; ok = rootKeys c == c.users.users.ela.openssh.authorizedKeys.keys
          && rootKeys c != [ ] && c.users.users.root.openssh.authorizedKeys.keyFiles == [ ]; }
      { name = "root locked for passwords"; ok = c.users.users.root.hashedPassword == "!"; }
      { name = "no password authentication"; ok = !(ssh c).PasswordAuthentication; }
      { name = "no keyboard-interactive authentication"; ok = !(ssh c).KbdInteractiveAuthentication; }
      { name = "no account with a password"; ok = withPassword c == { }; }
      { name = "firewall enabled"; ok = (fw c).enable; }
      { name = "only SSH inbound (TCP)"; ok = allTcpPorts c == [ 22 ] && allTcpRanges c == [ ]; }
      { name = "no UDP inbound"; ok = allUdp c == [ ]; }
      { name = "no audio stack"; ok = !c.services.pipewire.enable; }
    ];

  results = pi4 "mugge" ++ pi4 "mugge-deploy"
    ++ pi5Bootstrap "mugge-pi5-bootstrap" ++ pi5Full "mugge-pi5-deploy"
    ++ installer "pi5-installer";
in
pkgs.writeText "board-guard" (lib.concatStringsSep "\n" results + "\n")
