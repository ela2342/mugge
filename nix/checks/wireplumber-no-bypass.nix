# wireplumber-no-bypass.nix — F-318 policy test (unit + service integration)
#
# Everything under test comes from the Pi 5 production configuration, so
# the check exercises what the Pi runs:
#   - the PipeWire and WirePlumber packages (services.pipewire.package,
#     services.pipewire.wireplumber.package),
#   - WirePlumber's XDG_DATA_DIRS from its systemd user unit, i.e. the
#     configPackages (50/52/53/54/55 fragments) and extraScripts that
#     nix/nixos/audio/wireplumber.nix registers,
#   - the deployed mugge-no-bypass.lua text (extraScripts).
#
# Steps, each one fails the build:
#   1. Lua unit tests on the deployed script.
#   2. Mutation evidence: four mutants of the script must each fail (1).
#   3. Service integration, policy on: every case passes.
#   4. Negative control, policy disabled: the run must fail, the
#      default-sink pw-play case must fail because WirePlumber linked it,
#      and the default sink must be the USBStreamer stand-in.
#
# $out holds the output of every step and the WirePlumber logs.
#
# Usage: nix build -L .#checks.aarch64-linux.wireplumber-no-bypass
{ nixos }:

let
  inherit (nixos) pkgs config;
  pw = config.services.pipewire.package;
  wp = config.services.pipewire.wireplumber.package;
  wpDataDirs = config.systemd.user.services.wireplumber.environment.XDG_DATA_DIRS;
  script = pkgs.writeText "mugge-no-bypass.lua"
    config.services.pipewire.wireplumber.extraScripts."mugge-no-bypass.lua";
  tests = ../../tests/service-integration/wp-f318;
in
pkgs.runCommand "wireplumber-no-bypass" {
  nativeBuildInputs = [ pw wp pkgs.lua5_4 pkgs.python3 pkgs.pulseaudio pkgs.diffutils pkgs.gnused ];
} ''
  set -euo pipefail
  mkdir -p $out
  export HOME=$TMPDIR/home
  mkdir -p $HOME

  echo "== 1. Lua unit tests"
  lua ${tests}/test_mugge_no_bypass.lua ${script} | tee $out/unit.txt

  echo "== 2. Mutation evidence"
  mutate() {
    local name="$1" from="$2" to="$3"
    sed "s|$from|$to|" ${script} > $TMPDIR/$name.lua
    if cmp -s ${script} $TMPDIR/$name.lua; then
      echo "mutant $name: pattern not found, script changed?" >&2
      exit 1
    fi
    if lua ${tests}/test_mugge_no_bypass.lua $TMPDIR/$name.lua > $TMPDIR/$name.txt; then
      echo "mutant $name SURVIVED" | tee -a $out/mutants.txt
      exit 1
    fi
    echo "mutant $name killed: $(grep -c '^FAIL' $TMPDIR/$name.txt) failing tests" \
      | tee -a $out/mutants.txt
  }
  mutate usbstreamer-path '"usbstreamer", 1, true' '"no-such-device", 1, true'
  mutate default-filter-inverted 'if isProtected (props) then' 'if not isProtected (props) then'
  mutate capture-exempt-inverted '"^Stream/Input/") ~= nil' '"^Stream/Input/") == nil'
  mutate deny-disabled 'event:set_data ("target", nil)' '-- removed'

  run() {
    python3 ${tests}/run_policy_test.py --mode "$1" \
      --wp-data-dirs '${wpDataDirs}' \
      --workdir $TMPDIR/$1 --log-copy $out/wireplumber-$1.log
  }

  echo "== 3. Service integration, policy on"
  run policy | tee $out/policy.txt

  echo "== 4. Negative control, policy disabled"
  set +e
  run control > $out/control.txt 2>&1
  rc=$?
  set -e
  cat $out/control.txt
  if [ "$rc" -ne 1 ]; then
    echo "negative control: expected exit 1 (cases failed), got $rc" >&2
    exit 1
  fi
  if ! grep -q '^FAIL play_default .*WirePlumber linked' $out/control.txt; then
    echo "negative control: pw-play was not linked without the policy" >&2
    exit 1
  fi
  if ! grep -q '^FAIL default_sink_not_protected .*default.audio.sink is' $out/control.txt; then
    echo "negative control: the default sink was safe without the policy" >&2
    exit 1
  fi
  echo "negative control failed as expected"
''
