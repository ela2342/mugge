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

  # The hook is exactly one exec of the store path the pi5-prune-gens
  # check runs, with the rendered config template, the fixed paths and its
  # own arguments last and unchanged ("$@"). So it reads no environment
  # and adds no mode of its own: install-pi5-gen alone parses
  # [--stage-only] <toplevel> (SecSpec 6e3cfa20 SO1), and the check runs
  # it in that form. Context is dropped only for the string comparison;
  # the first line is writeShellScript's #! line.
  hookText = c: builtins.unsafeDiscardStringContext c.boot.loader.external.installHook.text;
  hookForm = c: text: let s = c.system.build.pi5PruneGens; in
    builtins.filter (l: l != "") (lib.tail (lines text)) == map builtins.unsafeDiscardStringContext [
      "set -euo pipefail"
      "exec ${s} /boot/firmware ${s.templateFile} \\"
      "  /nix/var/nix/profiles /run/booted-system /proc/device-tree/chosen/os_prefix \"$@\""
    ];
  hookRunsPrune = c: hookForm c (hookText c)
    && c.system.build.pi5PruneGens.configTemplate == configTxt c;
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
  # Text predicates take the rendered config.txt (with @ID@), so the
  # negative cases below can feed them altered texts.
  lines = t: lib.splitString "\n" t;
  txtLines = c: lines (configTxt c);
  hasVc4 = c: lib.hasInfix "dtoverlay=vc4-kms-v3d-pi5" (configTxt c);
  lineIdx = t: re: lib.lists.findFirstIndex (l: builtins.match re l != null) null (lines t);
  # US-172 R1 (architect rulings 04d8b687, 56271517, 94817076): the
  # firmware skips any file whose path is too long. Every path it opens,
  # built from the rendered config.txt with @ID@ at its real length
  # (<id8>), in two classes with inclusive limits (bootloader.nix).
  txtValues = t: re: lib.concatMap (l: let m = builtins.match re l; in
    if m == null then [ ] else m) (lines t);
  txtValue = t: re: let v = txtValues t re; in
    if builtins.length v == 1 then builtins.head v else null;
  osFiles = t: [ (txtValue t "kernel=(.*)") (txtValue t "initramfs ([^ ]+) followkernel")
    (txtValue t "cmdline=(.*)") ];
  dtoverlays = t: txtValues t "dtoverlay=([^,]*).*";
  # The prefix the firmware sees: <container><id8>/.
  fwPrefix = c: t: let v = txtValue t "os_prefix=(.*)"; b = c.system.build; in
    if v == "${b.pi5Container}@ID@/"
    then lib.replaceStrings [ "@ID@" ] [ (lib.concatStrings (lib.genList (_: "x") b.pi5IdLen)) ] v
    else null;
  kernelPaths = c: t: map (f: fwPrefix c t + f) (osFiles t ++ c.system.build.pi5Dtbs);
  overlayPaths = c: t: map (f: fwPrefix c t + "overlays/" + f)
    ([ "README" "overlay_map.dtb" "hat_map.dtb" ] ++ map (o: "${o}.dtbo") (dtoverlays t));
  within = max: p: builtins.stringLength p <= max;
  wellFormed = c: t: fwPrefix c t != null && lib.all (v: v != null) (osFiles t) && dtoverlays t != [ ];
  kernelFits = c: t: wellFormed c t && lib.all (within c.system.build.pi5KernelClassMax) (kernelPaths c t);
  overlayFits = c: t: wellFormed c t && lib.all (within c.system.build.pi5OverlayClassMax) (overlayPaths c t);
  # US-172 (AE 1a3addf3 B1): HDMI audio off on the vc4 line, and
  # dtparam=audio=off, which sets the vc4 overlay's parameter, directly
  # after that line.
  vc4Line = "dtoverlay=vc4-kms-v3d-pi5,noaudio";
  vc4Noaudio = t: builtins.elem vc4Line (lines t);
  audioOff = t: builtins.elem "dtparam=audio=off" (lines t);
  audioOffAfterVc4 = t: let i = lineIdx t (lib.escapeRegex vc4Line); in
    i != null && i + 1 < builtins.length (lines t) && builtins.elemAt (lines t) (i + 1) == "dtparam=audio=off";

  # The os_prefix= line is last, followed by exactly one "\n": an
  # unterminated last line may be lost (architect 03f33254).
  endsWithPrefix = t: let ls = lines t; n = builtins.length ls; in
    n >= 2 && builtins.elemAt ls (n - 1) == ""
      && builtins.match "os_prefix=.+" (builtins.elemAt ls (n - 2)) != null;

  # Negative cases: each alters the real rendered text in one way, and
  # the predicate must reject it (QE 74504b2f, 3f80f141, d272764d). Each
  # alteration must change the text, or the case is void.
  altered = t: from: to: let r = lib.replaceStrings [ from ] [ to ] t; in
    if r == t then throw "board-guard: negative case alters nothing ('${from}')" else r;
  filler = n: lib.concatStrings (lib.genList (_: "k") n);
  prefixLen = c: builtins.stringLength c.system.build.pi5Container + c.system.build.pi5IdLen + 1;
  # A kernel= name whose path is n characters.
  kernelAt = c: n: altered (configTxt c) "\nkernel=Image\n" "\nkernel=${filler (n - prefixLen c)}\n";
  # An extra dtoverlay= whose .dtbo path is n characters.
  overlayName = c: n: filler (n - prefixLen c - builtins.stringLength "overlays/" - builtins.stringLength ".dtbo");
  overlayAt = c: n: configTxt c + "dtoverlay=${overlayName c n}\n";
  overlayPath = c: n: fwPrefix c (overlayAt c n) + "overlays/${overlayName c n}.dtbo";
  negatives = c: let t = configTxt c; b = c.system.build; k = b.pi5KernelClassMax; o = b.pi5OverlayClassMax; in [
    { name = "kernel path at KERNEL_CLASS_MAX (${toString k}) passes"; ok = kernelFits c (kernelAt c k); }
    { name = "kernel path at KERNEL_CLASS_MAX + 1 fails"; ok = !kernelFits c (kernelAt c (k + 1)); }
    { name = "overlay path at OVERLAY_CLASS_MAX (${toString o}) is in the overlay class and within the limit";
      ok = builtins.elem (overlayPath c o) (overlayPaths c (overlayAt c o))
        && builtins.stringLength (overlayPath c o) == o && within o (overlayPath c o); }
    { name = "overlay path at OVERLAY_CLASS_MAX + 1 fails";
      ok = builtins.stringLength (overlayPath c (o + 1)) == o + 1 && !overlayFits c (overlayAt c (o + 1)); }
    { name = "os_prefix outside the container fails";
      ok = !kernelFits c (altered t "os_prefix=${b.pi5Container}@ID@/" "os_prefix=@ID@/"); }
    { name = "vc4 line without noaudio fails"; ok = !vc4Noaudio (altered t vc4Line "dtoverlay=vc4-kms-v3d-pi5"); }
    { name = "no dtparam=audio=off fails"; ok = !audioOff (altered t "dtparam=audio=off\n" ""); }
    { name = "dtparam=audio=off not directly after the vc4 line fails";
      ok = let a = altered t "${vc4Line}\ndtparam=audio=off\n" "${vc4Line}\n"; in
        audioOff (a + "dtparam=audio=off\n") && !audioOffAfterVc4 (a + "dtparam=audio=off\n"); }
    { name = "config.txt without its final newline fails";
      ok = lib.hasSuffix "\n" t && !endsWithPrefix (lib.removeSuffix "\n" t); }
    { name = "config.txt ending in a blank line fails"; ok = !endsWithPrefix (t + "\n"); }
    { name = "hook passing only \"$1\" fails";
      ok = !hookForm c (altered (hookText c) "os_prefix \"$@\"" "os_prefix \"$1\""); }
    { name = "hook selecting stage-only from the environment fails (SO1)";
      ok = !hookForm c (altered (hookText c) "set -euo pipefail\n"
        "set -euo pipefail\n[ -z \"\${STAGE_ONLY-}\" ] || set -- --stage-only \"$@\"\n"); }
  ];
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

  # US-172 GL tools option (architect 6f394d52, QE 9e6fb25b G1-G4). The
  # same configuration with the option off, for the on/off comparisons.
  glTools = [ "glmark2" "mesa-demos" "grim" ];
  glOff = conf: (nixosConfigurations.${conf}.extendModules {
    modules = [ { mugge.pi5.glDiagnostics.enable = false; } ];
  }).config;
  pkgNames = c: map (p: p.pname or (p.name or "")) c.environment.systemPackages;
  hasAllGl = c: lib.all (n: builtins.elem n (pkgNames c)) glTools;
  hasNoGl = c: !builtins.any (n: builtins.elem n glTools) (pkgNames c);
  # G2: packages only.
  unitsAndAccounts = c: map builtins.attrNames
    [ c.systemd.services c.systemd.user.services c.users.users c.users.groups ];
  # G4 (eval): the glmark2 entry builds the wayland-glesv2 flavour, which
  # is the glmark2-es2-wayland binary. The 02 read checks the file.
  glmark2Es2Wayland = c: let g = builtins.filter (p: (p.pname or "") == "glmark2") c.environment.systemPackages; in
    builtins.length g == 1
      && builtins.any (f: builtins.match "-Dflavors=(.*,)?wayland-glesv2(,.*)?" f != null) ((builtins.head g).mesonFlags or [ ]);

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

  # F-465: GM and the web UI read one packaged venues dir from the store,
  # and no unit arms a default venue (AE 013d2fa8 (B)3).
  gmUnit = c: c.systemd.user.services.pi4audio-graph-manager;
  webUnit = c: c.systemd.user.services.pi4-audio-webui;
  venuesPrefix = "PI4AUDIO_VENUES_DIR=";
  gmVenuesEnv = c: builtins.filter (e: lib.hasPrefix venuesPrefix e)
    (lib.toList (gmUnit c).serviceConfig.Environment);
  gmVenuesDir = c: lib.removePrefix venuesPrefix (builtins.head (gmVenuesEnv c));
  venueFile = "home-lab-chn50p-ultimax.yml";
  unitText = c: name: c.systemd.user.units."${name}.service".text;
  venues = c: [
    { name = "GM unit sets PI4AUDIO_VENUES_DIR exactly once (F-465)"; ok = builtins.length (gmVenuesEnv c) == 1; }
    { name = "GM venues dir is in the store (F-465)"; ok = lib.hasPrefix builtins.storeDir (gmVenuesDir c); }
    { name = "web UI uses the GM venues dir (F-465)"; ok = ((webUnit c).environment.PI4AUDIO_VENUES_DIR or null) == gmVenuesDir c; }
    { name = "venues dir not empty (F-465)"; ok = builtins.readDir (gmVenuesDir c) != { }; }
    { name = "${venueFile} packaged as committed (F-465)"; ok = builtins.pathExists "${gmVenuesDir c}/${venueFile}"
        && builtins.hashFile "sha256" "${gmVenuesDir c}/${venueFile}"
          == builtins.hashFile "sha256" ../../configs/venues/${venueFile}; }
    { name = "no PI4AUDIO_DEFAULT_VENUE in GM or web UI unit (F-465)"; ok =
        !builtins.any (n: lib.hasInfix "PI4AUDIO_DEFAULT_VENUE" (unitText c n)) [ "pi4audio-graph-manager" "pi4-audio-webui" ]; }
  ];

  pi4 = conf:
    let c = cfg conf; in map (a: check conf a.name a.ok) ([
      { name = "board is pi4"; ok = c.mugge.board.name == "pi4"; }
      { name = "no mugge.pi5 options (GL tools option is pi5 only, 6f394d52)"; ok = !(c.mugge ? pi5); }
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
    ] ++ venues c);

  # off: evaluated once per configuration.
  pi5Common = conf: c: let off = glOff conf; in [
    { name = "board is pi5"; ok = c.mugge.board.name == "pi5"; }
    { name = "NVMe kept"; ok = c.mugge.board.kernel.keepNvme; }
    { name = "external bootloader hook"; ok = c.boot.loader.external.enable; }
    { name = "hook is exactly exec pi5PruneGens <fixed paths> \"$@\" (AC2a check target, SO1)"; ok = hookRunsPrune c; }
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
    { name = "kernel class paths <= KERNEL_CLASS_MAX (US-172 R1)"; ok = kernelFits c (configTxt c); }
    { name = "overlay class paths <= OVERLAY_CLASS_MAX (US-172 R1)"; ok = overlayFits c (configTxt c); }
    { name = "config.txt ends with os_prefix= and exactly one newline (03f33254)"; ok = endsWithPrefix (configTxt c); }
    { name = "no root authorized_keys"; ok = rootKeys c == [ ] && c.users.users.root.openssh.authorizedKeys.keyFiles == [ ]; }
    { name = "PermitRootLogin no"; ok = (ssh c).PermitRootLogin == "no"; }
    { name = "no password authentication"; ok = !(ssh c).PasswordAuthentication; }
    { name = "no keyboard-interactive authentication"; ok = !(ssh c).KbdInteractiveAuthentication; }
    { name = "configurationRevision set"; ok = c.system.configurationRevision != null; }
    { name = "GL tools option on by default (6f394d52)"; ok = c.mugge.pi5.glDiagnostics.enable; }
    { name = "GL tools on: glmark2, mesa-demos, grim in systemPackages (G1)"; ok = hasAllGl c; }
    { name = "GL tools off: none of them in systemPackages (G1)"; ok = !off.mugge.pi5.glDiagnostics.enable && hasNoGl off; }
    { name = "GL tools on/off: same services, user services, users, groups (G2)"; ok = unitsAndAccounts c == unitsAndAccounts off; }
    { name = "GL tools on/off: same config.txt and kernel drv (G3)"; ok = configTxt c == configTxt off
        && (kernel c).drvPath == (kernel off).drvPath; }
    { name = "glmark2 builds glmark2-es2-wayland (G4, eval)"; ok = glmark2Es2Wayland c; }
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
      { name = "vc4-kms overlay with noaudio"; ok = vc4Noaudio (configTxt c); }
      { name = "dtparam=audio=off present"; ok = audioOff (configTxt c); }
      { name = "dtparam=audio=off directly after the vc4 overlay (US-172)"; ok = audioOffAfterVc4 (configTxt c); }
    ] ++ map (n: { name = "negative: ${n.name}"; inherit (n) ok; }) (negatives c) ++ [
      { name = "greetd skipped without a DRM card (F-367)"; ok = c.systemd.services.greetd.unitConfig.ConditionPathExistsGlob == "/dev/dri/card*"; }
      { name = "greetd started by the vc4 DRM card (US-172 AC8)"; ok = greetdOnVc4 c; }
      { name = "greetd started only by the udev rule (US-172 AC8)"; ok = c.systemd.services.greetd.wantedBy == [ ] && c.systemd.services.greetd.aliases == [ ]; }
      { name = "PipeWire enabled"; ok = c.services.pipewire.enable; }
      { name = "module-rt direct, RTKit off (F-358)"; ok = rtDirect c; }
      { name = "WirePlumber disables other ALSA cards"; ok = hasCardBlock c; }
      { name = "8080 open on the LAN (owner ruling, F-037)"; ok = builtins.elem 8080 (tcpPorts c); }
      { name = "TCP inbound exactly [22 8080]"; ok = lib.sort lib.lessThan (allTcpPorts c) == [ 22 8080 ] && allTcpRanges c == [ ]; }
    ] ++ venues c);

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
