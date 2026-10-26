# jack-self-connect.nix — F-318 / US-173 jack.self-connect-mode test
#
# Everything under test comes from the Pi 5 production configuration:
#   - the PipeWire package (services.pipewire.package) for the daemon,
#     the tools and PipeWire's libjack (its jack output),
#   - every jack.conf.d fragment in services.pipewire.configPackages,
#     i.e. what nix/nixos/audio/pipewire.nix deploys, including
#     80-jack-no-autoconnect.conf with jack.self-connect-mode.
#
# Steps, each one fails the build:
#   1. The deployed fragments contain the ignore-external line.
#   2. Service integration, policy on: every case passes (an external
#      jack_connect returns 0 and makes no link; internal connects and
#      native GraphManager-style pw-links work; jack_disconnect leaves a
#      native link alone).
#   3. Positive control: the same fragments with the line set to allow.
#      The run must fail, with self_connect_external failing because the
#      client got linked to the USBStreamer stand-in.
#
# $out holds the output of every step, the PipeWire and client logs and
# summary.txt (counts, control result, PipeWire version).
#
# Usage: nix build -L .#checks.aarch64-linux.jack-self-connect
{ nixos }:

let
  inherit (nixos) pkgs config;
  pw = config.services.pipewire.package;
  configPackages = config.services.pipewire.configPackages;
  tests = ../../tests/service-integration/jack-self-connect;
in
pkgs.runCommand "jack-self-connect" {
  nativeBuildInputs = [ pw pkgs.python3 pkgs.diffutils pkgs.gnused pkgs.gnugrep ];
} ''
  set -euo pipefail
  mkdir -p $out $TMPDIR/policy-frags $TMPDIR/control-frags
  export HOME=$TMPDIR/home
  mkdir -p $HOME

  echo "== 1. Deployed jack.conf.d fragments"
  for pkg in ${toString configPackages}; do
    if [ -d "$pkg/share/pipewire/jack.conf.d" ]; then
      cp "$pkg"/share/pipewire/jack.conf.d/*.conf $TMPDIR/policy-frags/
    fi
  done
  ls $TMPDIR/policy-frags | tee $out/fragments.txt
  if ! grep -q '^ *jack\.self-connect-mode = ignore-external$' \
      $TMPDIR/policy-frags/*.conf; then
    echo "no deployed fragment sets jack.self-connect-mode = ignore-external" >&2
    exit 1
  fi
  for f in $TMPDIR/policy-frags/*.conf; do
    sed 's|jack\.self-connect-mode = ignore-external|jack.self-connect-mode = allow|' \
      "$f" > $TMPDIR/control-frags/$(basename "$f")
  done
  if diff -r $TMPDIR/policy-frags $TMPDIR/control-frags > /dev/null; then
    echo "control fragments are identical to the policy fragments" >&2
    exit 1
  fi

  run() {
    local mode="$1" frags="$2" args=()
    for f in "$frags"/*.conf; do args+=(--jack-fragment "$f"); done
    python3 -B ${tests}/run_self_connect_test.py --mode "$mode" \
      --workdir $TMPDIR/$mode --jack-lib ${pw.jack}/lib \
      --client ${tests}/jack_client.py "''${args[@]}"
  }

  echo "== 2. Service integration, policy on"
  set +e
  run policy $TMPDIR/policy-frags > $out/policy.txt 2>&1
  rc=$?
  set -e
  cp $TMPDIR/policy/pipewire.log $out/pipewire-policy.log || true
  cp $TMPDIR/policy/client.log $out/client-policy.log || true
  cat $out/policy.txt
  if [ "$rc" -ne 0 ]; then
    echo "policy run failed (exit $rc)" >&2
    exit 1
  fi

  echo "== 3. Positive control, self-connect-mode = allow"
  set +e
  run control $TMPDIR/control-frags > $out/control.txt 2>&1
  rc=$?
  set -e
  cp $TMPDIR/control/pipewire.log $out/pipewire-control.log || true
  cp $TMPDIR/control/client.log $out/client-control.log || true
  cat $out/control.txt
  if [ "$rc" -ne 1 ]; then
    echo "positive control: expected exit 1 (cases failed), got $rc" >&2
    exit 1
  fi
  if ! grep -q '^FAIL self_connect_external: jack_connect linked the client' \
      $out/control.txt; then
    echo "positive control: jack_connect did not link with mode allow" >&2
    exit 1
  fi
  echo "positive control failed as expected"

  {
    echo "F-318 jack-self-connect check"
    echo "pipewire: ${pw.version}"
    grep '^RESULT' $out/policy.txt
    grep '^RESULT' $out/control.txt
    echo "positive control: failed as expected (self_connect_external linked)"
  } > $out/summary.txt
  cat $out/summary.txt
''
