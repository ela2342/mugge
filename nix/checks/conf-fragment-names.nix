# conf-fragment-names.nix — PipeWire/WirePlumber conf.d file names (F-400)
#
# conf.d fragments load in file-name order, and a user fragment overrides
# a deployed one only under the same name. A `cp <store path> dir/` keeps
# the store hash in the name (<hash>-10-audio-settings.conf), which breaks
# both. This check reads the trees the Pi 5 production configuration
# actually deploys:
#   - /etc/pipewire (environment.etc.pipewire.source, the NixOS buildEnv
#     of every services.pipewire.configPackages entry),
#   - WirePlumber's config tree (the first XDG_DATA_DIRS entry of the
#     wireplumber user unit, the NixOS buildEnv of its configPackages).
#
# Each step fails the build:
#   0. Self-test: the name pattern rejects a store-hash name and accepts a
#      plain one (so a broken pattern cannot pass everything).
#   1. Every file in every *.conf.d directory matches
#      ^[0-9]{2}-[a-z0-9-]+\.conf$.
#   2. The fragments we deploy are present under their plain names (so the
#      check cannot pass on an empty or misplaced tree).
#
# Usage: nix build -L .#checks.aarch64-linux.conf-fragment-names
{ nixos }:

let
  inherit (nixos) pkgs config;
  inherit (pkgs) lib;
  pwTree = config.environment.etc.pipewire.source;
  wpTree = "${lib.head (lib.splitString ":"
    config.systemd.user.services.wireplumber.environment.XDG_DATA_DIRS)}/wireplumber";
  expected = [
    "${pwTree}/pipewire.conf.d/05-rt-direct.conf"
    "${pwTree}/pipewire.conf.d/10-audio-settings.conf"
    "${pwTree}/pipewire.conf.d/21-usbstreamer-playback.conf"
    "${pwTree}/pipewire.conf.d/30-filter-chain-convolver.conf"
    "${pwTree}/jack.conf.d/80-jack-no-autoconnect.conf"
    "${wpTree}/wireplumber.conf.d/50-usbstreamer-disable-acp.conf"
    "${wpTree}/wireplumber.conf.d/52-umik1-low-priority.conf"
    "${wpTree}/wireplumber.conf.d/53-deny-usbstreamer-alsa.conf"
    "${wpTree}/wireplumber.conf.d/55-mugge-no-bypass.conf"
  ];
in
pkgs.runCommand "conf-fragment-names" { } ''
  set -euo pipefail
  mkdir -p $out
  plain_name() { echo "$1" | grep -Eq '^[0-9]{2}-[a-z0-9-]+\.conf$'; }

  echo "== 0. Name pattern self-test"
  if plain_name 12zi3gy8vq0kq2r0q4w1f3b5x7l9n6m2-10-audio-settings.conf; then
    echo "self-test: pattern accepted a store-hash name" >&2
    exit 1
  fi
  if ! plain_name 10-audio-settings.conf; then
    echo "self-test: pattern rejected a plain name" >&2
    exit 1
  fi
  echo "ok   rejects <hash>-10-audio-settings.conf, accepts 10-audio-settings.conf"

  echo "== 1. conf.d file names"
  for tree in ${pwTree} ${wpTree}; do
    for d in "$tree"/*.conf.d; do
      [ -d "$d" ] || continue
      for f in "$d"/*; do
        [ -e "$f" ] || continue
        name=$(basename "$f")
        if plain_name "$name"; then
          echo "ok   $d/$name"
        else
          echo "BAD  $d/$name"
        fi
      done
    done
  done | tee $out/names.txt
  if grep -q '^BAD ' $out/names.txt; then
    echo "conf.d file names must match ^[0-9]{2}-[a-z0-9-]+\.conf$" >&2
    exit 1
  fi

  echo "== 2. Deployed fragments present under their plain names"
  for f in ${lib.escapeShellArgs expected}; do
    if [ -e "$f" ]; then
      echo "present $f"
    else
      echo "MISSING $f"
    fi
  done | tee $out/expected.txt
  if grep -q '^MISSING ' $out/expected.txt; then
    echo "a deployed fragment is missing under its plain name" >&2
    exit 1
  fi
''
