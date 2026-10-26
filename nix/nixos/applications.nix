# applications.nix — Audio applications for the Pi 4 Audio Workstation
#
# Mixxx (DJ software) and Reaper (DAW) for the two operational modes.
# Both run under PipeWire's JACK bridge via pw-jack.
{ config, lib, pkgs, pi4audio-packages, ... }:

let
  mixxxHome = "${config.users.users.ela.home}/.mixxx";

  # US-173 AC8: Hercules DJControl MIX Ultra mapping (TK-065). Mixxx lists
  # mappings by the <name> inside the XML, not by file name. Store names may
  # not contain spaces, so builtins.path copies the XML under a name without
  # them, and the tmpfiles paths need no escaping. The mapping also loads
  # lodash.mixxx.js and midi-components-0.0.js, which Mixxx finds in its
  # own share/mixxx/controllers.
  herculesXml = builtins.path {
    path = ../../configs/mixxx/controllers + "/Hercules DJControl MIX Ultra.midi.xml";
    name = "Hercules-DJControl-MIX-Ultra.midi.xml";
  };
  herculesJs = ../../configs/mixxx/controllers/Hercules-DJControl-MIX-Ultra-scripts.js;
in
{
  # User mappings live in ~/.mixxx/controllers/ (Mixxx on Linux). 'L+'
  # replaces whatever is there with a link to the store copy, so a deploy
  # always brings the committed mapping. If the packaged Mixxx already
  # ships "Hercules DJControl Mix Ultra" in share/mixxx/controllers (P-step
  # check), drop our copy and these two links (Architect, US-173). If we
  # keep it, the mapping must name the Mixxx version it was tested with.
  #
  # TODO (US-173 P-step): soundconfig.xml. configs/mixxx/soundconfig.xml is
  # pre-D-040 (CamillaDSP device name, HP at channel offset 2) and does not
  # match GraphManager's HP ports out_4/out_5 (F-130), so it is NOT
  # installed. It is captured from Mixxx on the Pi 5 (JACK, Master ch 1-2,
  # HP ch 5-6) before the next reboot, and replaces the repo file. Then
  # install it on every boot, owned by ela and writable. Not with tmpfiles
  # C/C+: in systemd 258.3 (pinned nixpkgs) C+ only merges directories; an
  # existing file is kept (copy_files passes COPY_MERGE, never COPY_REPLACE).
  # Use a user oneshot instead, e.g.:
  #   systemd.user.services.mixxx-soundconfig = {
  #     wantedBy = [ "default.target" ];
  #     serviceConfig.Type = "oneshot";
  #     serviceConfig.ExecStart = "${pkgs.coreutils}/bin/install -m 0644 "
  #       + "${../../configs/mixxx/soundconfig.xml} ${mixxxHome}/soundconfig.xml";
  #   };
  # src/web-ui/tests/unit/test_mixxx_soundconfig.py guards the file
  # against GraphManager's DJ routing.
  systemd.tmpfiles.rules = [
    "d ${mixxxHome} 0755 ela users - -"
    "d ${mixxxHome}/controllers 0755 ela users - -"
    "L+ ${mixxxHome}/controllers/Hercules-DJControl-MIX-Ultra.midi.xml - - - - ${herculesXml}"
    "L+ ${mixxxHome}/controllers/Hercules-DJControl-MIX-Ultra-scripts.js - - - - ${herculesJs}"
  ];

  environment.systemPackages = with pkgs; [
    # ── Mixxx — DJ/PA mode ─────────────────────────────────────
    # Runs via: pw-jack mixxx
    # Hardware V3D GL (D-022) — no LIBGL_ALWAYS_SOFTWARE needed.
    # CPU ~85% with hardware GL (vs 142-166% with llvmpipe).
    mixxx

    # ── Reaper — Live vocal performance mode ───────────────────
    # Runs via: pw-jack reaper
    # nixpkgs packages Reaper for aarch64-linux.
    # US-118: VLC stub — Reaper's reaper_video.so dlopen's libvlc.so.5 for
    # video decoding only. VLC pulls ~857 MiB of transitive dependencies
    # (Samba, Qt5, ffmpeg 7, GTK4, gst-plugins-bad). Stubbing it out saves
    # that entire closure; Reaper disables video decoder gracefully.
    (reaper.override {
      vlc = pkgs.runCommand "vlc-stub" {} "mkdir -p $out/lib";
    })

    # ── Gig-day diagnosis (US-173, Architect) ──────────────────
    # Packages only, no services or listeners. alsa-utils: aplay/arecord
    # -l, amixer, aconnect, alsactl. usbutils: lsusb -t.
    alsa-utils
    usbutils

    # ── Thermal watch (US-173 AC9, D-069) ──────────────────────
    # Runs via: sudo pi5-thermal-watch --duration <s>
    # Source: scripts/stability/pi5_thermal_watch.py
    pi4audio-packages.pi5-thermal-watch

    # ── pw-jack wrapper ────────────────────────────────────────
    # Provided by the PipeWire JACK bridge (services.pipewire.jack.enable
    # in audio/pipewire.nix). Listed here as documentation — the binary
    # comes from the pipewire package, which is already in the system path
    # when services.pipewire.jack.enable = true.
  ];
}
