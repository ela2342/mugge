# pi4audio-rpc.nix — the F-341 pre-flight client as deployed
#
# Everything under test comes from the Pi 5 production configuration:
# the pi4audio-rpc package that environment.systemPackages puts on the
# system PATH (nix/nixos/services/signal-gen.nix).
#
# Steps, each one fails the build:
#   0. Eval: exactly one systemPackages entry is named pi4audio-rpc
#      (otherwise the check does not evaluate).
#   1. The package provides an executable bin/pi4audio-rpc.
#   2. src/signal-gen/tests/test_pi4audio_rpc.py passes against that bin
#      (PI4AUDIO_RPC), with nothing skipped. The test file is copied in on
#      its own, so its default path to the source script does not exist:
#      a run that ignored PI4AUDIO_RPC would fail.
#   3. Negative control: the same tests against `false` must fail.
#
# $out holds the pytest output of both runs and summary.txt.
#
# Usage: nix build -L .#checks.aarch64-linux.pi4audio-rpc
{ nixos }:

let
  inherit (nixos) pkgs config;
  found = builtins.filter (p: (p.name or "") == "pi4audio-rpc")
    config.environment.systemPackages;
  rpc =
    if builtins.length found == 1 then builtins.head found
    else throw "pi4audio-rpc: expected 1 systemPackages entry, found ${toString (builtins.length found)}";
  python = pkgs.python3.withPackages (ps: [ ps.pytest ]);
  test = ../../src/signal-gen/tests/test_pi4audio_rpc.py;
in
pkgs.runCommand "pi4audio-rpc-check" {
  nativeBuildInputs = [ python pkgs.procps pkgs.gnugrep ];
} ''
  set -euo pipefail
  mkdir -p $out $TMPDIR/t
  cp ${test} $TMPDIR/t/test_pi4audio_rpc.py
  cd $TMPDIR/t

  echo "== 1. Deployed bin"
  bin=${rpc}/bin/pi4audio-rpc
  if [ ! -x "$bin" ]; then
    echo "$bin missing or not executable" >&2
    exit 1
  fi
  echo "$bin"

  pt() {
    PI4AUDIO_RPC="$1" python -B -m pytest -p no:cacheprovider -v -rs \
      test_pi4audio_rpc.py
  }

  echo "== 2. Tests against the deployed bin"
  set +e
  pt "$bin" > $out/tests.txt 2>&1
  rc=$?
  set -e
  cat $out/tests.txt
  if [ "$rc" -ne 0 ]; then
    echo "tests failed against $bin (exit $rc)" >&2
    exit 1
  fi
  if grep -qE '[0-9]+ (skipped|xfailed|xpassed)' $out/tests.txt; then
    echo "tests skipped or xfailed" >&2
    exit 1
  fi

  echo "== 3. Negative control, PI4AUDIO_RPC=false"
  set +e
  pt ${pkgs.coreutils}/bin/false > $out/control.txt 2>&1
  crc=$?
  set -e
  tail -n 3 $out/control.txt
  if [ "$crc" -ne 1 ]; then
    echo "negative control: expected exit 1 (tests failed), got $crc" >&2
    exit 1
  fi
  echo "negative control failed as expected"

  {
    echo "F-341 pi4audio-rpc check"
    echo "bin: $bin (environment.systemPackages of mugge-pi5-deploy)"
    echo "-- tests (exit 0)"
    tail -n 1 $out/tests.txt
    echo "-- negative control, PI4AUDIO_RPC=false (exit $crc)"
    tail -n 1 $out/control.txt
  } > $out/summary.txt
  cat $out/summary.txt
''
