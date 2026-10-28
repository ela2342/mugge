{
  description = "Pi 4B audio workstation — development environment and NixOS deployment";

  nixConfig = {
    extra-substituters = [ "https://mugge.cachix.org" ];
    extra-trusted-public-keys = [ "mugge.cachix.org-1:5p6UsgwD9LPWgJJaTGrRp5qahNcaq86Ew7Oro9HTevc=" ];
  };

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    # US-128: PipeWire 1.6.2 source — nixos-25.11 ships 1.4.9.
    # Only PW is imported from this input; everything else stays on nixos-25.11.
    nixpkgs-pw.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";
    nixos-hardware.url = "github:NixOS/nixos-hardware";
    nixgl = {
      url = "github:nix-community/nixGL";
      inputs.nixpkgs.follows = "nixpkgs";       # prevent GLIBC version mismatch
      inputs.flake-utils.follows = "flake-utils"; # deduplicate
    };
    disko = {
      url = "github:nix-community/disko";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nixpkgs-pw, flake-utils, nixos-hardware, nixgl, disko }:
    (flake-utils.lib.eachSystem [
      "x86_64-darwin"   # macOS Intel dev
      "aarch64-darwin"  # macOS Apple Silicon dev
      "aarch64-linux"   # Pi 4B deployment target
      "x86_64-linux"    # GitHub Actions CI runners
    ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = nixpkgs.lib.optionals (builtins.match ".*-linux" system != null) [
            nixgl.overlay
          ];
        };
        python = pkgs.python313;
        pycamilladsp = python.pkgs.buildPythonPackage rec {
          pname = "camilladsp";
          version = "3.0.0";
          pyproject = true;
          src = pkgs.fetchFromGitHub {
            owner = "HEnquist";
            repo = "pycamilladsp";
            rev = "v${version}";
            hash = "sha256-WyyeYAEi2s46WSSuSl/s04+yW4rXWMPUx+oT1bVP3HM=";
          };
          build-system = with python.pkgs; [ setuptools ];
          dependencies = with python.pkgs; [
            pyyaml
            websocket-client
          ];
          doCheck = false;  # tests need a running CamillaDSP instance
        };

        # Python with test dependencies — shared by checks and unit-test apps.
        testPython = python.withPackages (ps: [
          ps.mido
          ps.python-rtmidi
          ps.fastapi
          ps.uvicorn
          ps.scipy
          ps.numpy
          ps.soundfile
          ps.websockets
          ps.pyyaml
          # US-110: Passkey auth dependencies
          ps.webauthn    # py-webauthn (WebAuthn registration/authentication)
          ps.aiosqlite   # async SQLite for credential + session storage
          ps.qrcode      # QR code generation for invite links
          # Testing
          ps.pytest
          ps.httpx
          pycamilladsp
        ]);

        # Python with browser-test dependencies — adds playwright on top of testPython's deps.
        # Used by test-integration-browser app and devShell.
        e2ePython = python.withPackages (ps: [
          ps.mido
          ps.python-rtmidi
          ps.fastapi
          ps.uvicorn
          ps.scipy
          ps.numpy
          ps.soundfile
          ps.websockets
          ps.pyyaml
          # US-110: Passkey auth dependencies
          ps.webauthn
          ps.aiosqlite
          ps.qrcode
          # Testing
          ps.pytest
          ps.httpx
          pycamilladsp
          # Browser integration testing
          ps.playwright
          ps.pytest-playwright
        ]);

        # CamillaDSP binary for integration testing (TK-189).
        # Built with websocket + file backend — no JACK/PulseAudio needed.
        # The File capture/playback type is always compiled in (not a feature).
        # Used by room-correction integration tests to replace MockCamillaClient.
        camilladsp-test = pkgs.rustPlatform.buildRustPackage {
          pname = "camilladsp";
          version = "3.0.1";
          src = pkgs.fetchFromGitHub {
            owner = "HEnquist";
            repo = "camilladsp";
            rev = "v3.0.1";
            hash = "sha256-IJ1sYprBh8ys1Og3T3newIDlBlR0PoQiblbJmzLbsfs=";
          };
          cargoLock.lockFile = ./src/camilladsp-test/Cargo.lock;
          # Upstream doesn't ship a Cargo.lock — copy ours into the source.
          postPatch = ''
            cp ${./src/camilladsp-test/Cargo.lock} Cargo.lock
          '';
          # Default features = ["websocket"] — includes tungstenite WS server.
          # No extra features needed: File I/O backend is always compiled in.
          buildNoDefaultFeatures = false;
          nativeBuildInputs = [ pkgs.pkg-config ];
          buildInputs =
            pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux [ pkgs.alsa-lib ]
            ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isDarwin [
              pkgs.apple-sdk  # Provides AudioUnit, CoreAudio, CoreServices frameworks
            ];
          doCheck = false;  # CamillaDSP tests require audio hardware
        };

        # nixGL wrapper for Mixxx on non-NixOS (Debian Trixie).
        # nixGLIntel is the Mesa wrapper — works for all Mesa drivers
        # including V3D on the Pi 4. Despite the "Intel" name, it sets
        # LIBGL_DRIVERS_PATH, GBM_BACKENDS_PATH, and LD_LIBRARY_PATH
        # to point at Nix's Mesa, which contains the V3D DRI driver.
        #
        # We also prepend host PipeWire/JACK library paths so that
        # pw-jack compatibility works (Mixxx uses JACK via PipeWire).
        # On non-NixOS, PipeWire's pw-jack libraries live under the
        # host's /usr/lib, which Nix isolates away.

        mixxx-wrapped = let
          nixGLMesa = pkgs.nixgl.nixGLIntel;
        in pkgs.writeShellApplication {
          name = "mixxx";
          runtimeInputs = [ nixGLMesa pkgs.mixxx ];
          text = ''
            # Host PipeWire/JACK paths for non-NixOS Debian Trixie.
            # pw-jack provides libjack.so that routes JACK calls through
            # PipeWire. Mixxx links against JACK, so it needs to find
            # the host's pw-jack library.
            HOST_LIB="/usr/lib/${system}-gnu"
            if [ -d "$HOST_LIB/pipewire-0.3/jack" ]; then
              export LD_LIBRARY_PATH="$HOST_LIB/pipewire-0.3/jack''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
            fi

            exec nixGLIntel mixxx "$@"
          '';
        };

        # Workspace source for level-bridge + pcm-bridge + signal-gen + audio-common.
        # Cleaned to include only the workspace root and member crates.
        rustWorkspaceSrc = pkgs.lib.cleanSourceWith {
          src = ./src;
          filter = path: type:
            let baseName = builtins.baseNameOf path; in
            # Include workspace root files
            baseName == "Cargo.toml" || baseName == "Cargo.lock"
            # Include workspace member directories
            || pkgs.lib.hasPrefix (toString ./src/audio-common) (toString path)
            || pkgs.lib.hasPrefix (toString ./src/level-bridge) (toString path)
            || pkgs.lib.hasPrefix (toString ./src/pcm-bridge) (toString path)
            || pkgs.lib.hasPrefix (toString ./src/signal-gen) (toString path);
        };

        # US-128: PipeWire 1.6.2 from nixpkgs-unstable with US-112 reload patch.
        # nixos-25.11 ships PW 1.4.9; we upgrade source + nixpkgs patches from
        # nixpkgs-unstable while keeping all build deps from nixos-25.11.
        # The convolver-reload patch (1.6.2 version) uses the clean API:
        # plugin_builtin.c, spa_loop_locked, control_changed callback.
        pwUnstable = ((import nixpkgs-pw { inherit system; }).pipewire.override {
          # Disable Bluetooth codecs — build deps from nixos-25.11 may lack
          # ldacbt-dec and other BT libraries present in nixpkgs-unstable.
          bluezSupport = false;
        });
        pipewire-patched = pkgs.pipewire.overrideAttrs (oldAttrs: {
          version = pwUnstable.version;
          src = pwUnstable.src;
          # Replace mesonFlags entirely — nixos-25.11 passes -Dsystemd=enabled
          # which doesn't exist in PW 1.6.2 (renamed to -Dlibsystemd=enabled).
          mesonFlags = pwUnstable.mesonFlags;
          patches = pwUnstable.patches ++ [
            ./nix/patches/pipewire-convolver-reload.patch
          ];
        });

        # Shared PipeWire build args for Rust crates.
        rustPwBuildArgs = {
          nativeBuildInputs = [ pkgs.pkg-config pkgs.llvmPackages.libclang ];
          buildInputs = [ pkgs.pipewire ];
          LIBCLANG_PATH = "${pkgs.llvmPackages.libclang.lib}/lib";
          BINDGEN_EXTRA_CLANG_ARGS = builtins.toString [
            "-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include"
            "-isystem ${pkgs.glibc.dev}/include"
          ];
        };

        # Rust PipeWire tools (Linux-only, need libpipewire).
        # Built from the Cargo workspace (audio-common + level-bridge + pcm-bridge + signal-gen).
        level-bridge = pkgs.rustPlatform.buildRustPackage (rustPwBuildArgs // {
          pname = "level-bridge";
          version = "0.1.0";
          src = rustWorkspaceSrc;
          cargoLock.lockFile = ./src/Cargo.lock;
          buildAndTestSubdir = "level-bridge";
        });

        pcm-bridge = pkgs.rustPlatform.buildRustPackage (rustPwBuildArgs // {
          pname = "pcm-bridge";
          version = "0.1.0";
          src = rustWorkspaceSrc;
          cargoLock.lockFile = ./src/Cargo.lock;
          buildAndTestSubdir = "pcm-bridge";
        });

        signal-gen = pkgs.rustPlatform.buildRustPackage (rustPwBuildArgs // {
          pname = "pi4audio-signal-gen";
          version = "0.1.0";
          src = rustWorkspaceSrc;
          cargoLock.lockFile = ./src/Cargo.lock;
          buildAndTestSubdir = "signal-gen";
        });

        graph-manager = pkgs.rustPlatform.buildRustPackage {
          pname = "pi4audio-graph-manager";
          version = "0.1.0";
          src = ./src/graph-manager;
          cargoLock.lockFile = ./src/graph-manager/Cargo.lock;
          nativeBuildInputs = [ pkgs.pkg-config pkgs.llvmPackages.libclang ];
          buildInputs = [ pkgs.pipewire ];
          LIBCLANG_PATH = "${pkgs.llvmPackages.libclang.lib}/lib";
          BINDGEN_EXTRA_CLANG_ARGS = builtins.toString [
            "-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include"
            "-isystem ${pkgs.glibc.dev}/include"
          ];
        };

        # Repo tree that app scripts `cd` into. Must carry string context:
        # calling toString on the flake root drops it, and Nix >= 2.35 (lazy
        # trees) then never copies the source into the store, so the path
        # does not exist (F-335). `${self}` copies it once and makes it a
        # runtime dependency.
        repoSrc = "${self}";

        # Runs `cargo test ...` (its arguments) and fails if no test ran.
        # cargo exits 0 when it runs zero tests, which would hide a broken
        # source filter or path (F-335 AC5). pytest needs no wrapper: it
        # exits 5 when it collects nothing.
        cargoTestNonEmpty = pkgs.writeShellScript "cargo-test-nonempty" ''
          set -euo pipefail
          log=$(mktemp)
          trap 'rm -f "$log"' EXIT
          "$@" 2>&1 | tee "$log"
          if ! grep -qE '^test result: ok\. [1-9][0-9]* passed' "$log"; then
            echo "FAIL: no Rust tests ran for: $*" >&2
            exit 1
          fi
        '';

        # F-335 regression guard. App scripts must refer to the repo tree as
        # `repoSrc`: a path stringified without string context is never copied
        # into the store under Nix >= 2.35 (lazy trees), so the script `cd`s
        # into a store path that does not exist. This fails if any store path
        # named in an app script is missing from that script's runtime
        # closure, independent of Nix version or sandboxing. It also rejects
        # context-dropping stringification of the flake root in any .nix file.
        # CI builds it as its own T1 step; it is deliberately not a dependency
        # of test-all, since it pulls in every app's closure (browsers too).
        appSourceCheck =
          let
            scripts = pkgs.lib.mapAttrs (_: app: app.program) self.apps.${system};
          in
          pkgs.runCommand "app-source-paths" { } ''
            set -euo pipefail
            fail=0
            if grep -rnE --include='*.nix' 'toString (\./\.|self)' ${repoSrc}; then
              echo "FAIL: the flake root is stringified without context; use repoSrc"
              fail=1
            fi
            ${pkgs.lib.concatStrings (pkgs.lib.mapAttrsToList (name: script: ''
              closure=${pkgs.writeClosure [ script ]}
              for p in $(grep -oE '/nix/store/[a-z0-9]{32}-[a-zA-Z0-9+._?=-]+' ${script} | sort -u); do
                if ! grep -qxF "$p" "$closure"; then
                  echo "FAIL: app ${name} references $p outside its runtime closure"
                  fail=1
                fi
              done
            '') scripts)}
            [ "$fail" = 0 ]
            echo "Checked ${toString (builtins.length (builtins.attrNames scripts))} app scripts" > $out
          '';
      in
      {
        packages = {
          # CamillaDSP with file backend for integration testing (all platforms).
          inherit camilladsp-test;
        } // pkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          # US-112: PipeWire with convolver reload patch (for local-demo/tests).
          inherit pipewire-patched;

          # Unwrapped Mixxx (for NixOS or debugging)
          mixxx = pkgs.mixxx;

          # Wrapped Mixxx with nixGL + host PipeWire/JACK (for non-NixOS)
          mixxx-gl = mixxx-wrapped;

          # Always-on PipeWire level metering bridge for web UI (D-049).
          inherit level-bridge;

          # Passive PipeWire monitor-port PCM bridge for web UI.
          inherit pcm-bridge;

          # RT signal generator for measurement and test tooling (D-037).
          inherit signal-gen;

          # PipeWire graph manager — session manager for link topology (GM-7).
          inherit graph-manager;

          # Default package for `nix run .#` on Linux
          default = mixxx-wrapped;
        };

        devShells.default = pkgs.mkShell {
          packages = [
            e2ePython
            pkgs.playwright-driver
            pkgs.playwright-mcp        # US-109: MCP server for agent-driven browser testing
            camilladsp-test  # Real CamillaDSP for integration tests (TK-189)
            # Rust toolchain — same version as buildRustPackage uses.
            pkgs.cargo
            pkgs.rustc
            pkgs.clippy
            pkgs.rust-analyzer
          ];

          buildInputs = [
            pkgs.libsndfile
          ] ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux [
            pkgs.alsa-lib
            # PipeWire dev deps for cargo build of PW crates
            pkgs.pipewire
            pkgs.pkg-config
            pkgs.llvmPackages.libclang
          ];

          shellHook = ''
            export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
            export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
          '' + pkgs.lib.optionalString pkgs.stdenv.hostPlatform.isLinux ''
            export LIBCLANG_PATH="${pkgs.llvmPackages.libclang.lib}/lib"
            export BINDGEN_EXTRA_CLANG_ARGS="-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include -isystem ${pkgs.glibc.dev}/include"
          '' + ''

            echo "Pi 4B audio workstation dev shell"
            echo "Python: $(python3 --version)"
            echo "Rust:   $(rustc --version 2>/dev/null || echo 'not available')"
            echo "Cargo:  $(cargo --version 2>/dev/null || echo 'not available')"
            echo ""
            echo "Packages from nixpkgs: mido, python-rtmidi, fastapi,"
            echo "  uvicorn, scipy, numpy, soundfile, websockets,"
            echo "  pytest, playwright, pytest-playwright"
            echo ""

            echo "pycamilladsp: $(python3 -c 'from camilladsp.versions import VERSION; print(VERSION)' 2>/dev/null || echo 'not available')"
          '';
        };

        # -----------------------------------------------------------------
        # Checks — sandboxed test derivations for `nix flake check`
        # -----------------------------------------------------------------
        checks = {
          # US-163: eval-only structural assertions over all NixOS configs.
          board-guard = import ./nix/checks/board-guard.nix {
            inherit pkgs;
            inherit (self) nixosConfigurations;
            cachedKernel = (import nixpkgs { system = "aarch64-linux"; }).linuxPackages_rpi4.kernel;
          };

          # US-163 AC2a: offline test of the Pi 5 FAT generation prune.
          pi5-prune-gens = import ./nix/checks/pi5-prune-gens.nix {
            inherit pkgs;
            target = self.nixosConfigurations.mugge-pi5-deploy.config.system.build.pi5PruneGens;
          };
          wireplumber-no-bypass = import ./nix/checks/wireplumber-no-bypass.nix { nixos = self.nixosConfigurations.mugge-pi5-deploy; };  # F-318
          jack-self-connect = import ./nix/checks/jack-self-connect.nix { nixos = self.nixosConfigurations.mugge-pi5-deploy; };  # F-318, US-173
          conf-fragment-names = import ./nix/checks/conf-fragment-names.nix { nixos = self.nixosConfigurations.mugge-pi5-deploy; };  # F-400, US-173
          pi4audio-rpc = import ./nix/checks/pi4audio-rpc.nix { nixos = self.nixosConfigurations.mugge-pi5-deploy; };  # F-341

          app-source-paths = appSourceCheck;

          test-web-ui = pkgs.runCommand "test-web-ui" {
            nativeBuildInputs = [ testPython ];
            PI_AUDIO_MOCK = "1";
          } ''
            cp -r ${./src/web-ui} web-ui
            cp -r ${./src/room-correction} room-correction
            chmod -R u+w web-ui room-correction
            cd web-ui
            python -m pytest tests/ -v -rs --ignore=tests/integration/ --ignore=tests/e2e/ --ignore=tests/service-integration/ --tb=short
            touch $out
          '';

          test-room-correction = pkgs.runCommand "test-room-correction" {
            nativeBuildInputs = [ testPython camilladsp-test ];
            PI_AUDIO_MOCK = "1";
          } ''
            # Mirror the repo layout: room-correction resolves configs/ as ../../configs
            mkdir src
            cp -r ${./src/room-correction} src/room-correction
            cp -r ${./configs} configs
            chmod -R u+w src configs
            cp ${./src/camilladsp-test/test_config.yml} src/room-correction/test_camilladsp.yml
            test -d configs/venues && test -d configs/speakers || { echo "configs/ missing in sandbox"; exit 1; }
            cd src/room-correction
            python -m pytest tests/ -v -rs --tb=short
            touch $out
          '';

          test-midi = pkgs.runCommand "test-midi" {
            nativeBuildInputs = [ testPython ];
            PI_AUDIO_MOCK = "1";
          } ''
            cp -r ${./src/midi} midi
            cp -r ${./configs} configs
            chmod -R u+w midi configs
            cd midi
            python -m pytest tests/ -v -rs --tb=short
            touch $out
          '';

          test-drivers = pkgs.runCommand "test-drivers" {
            nativeBuildInputs = [ testPython ];
            PI_AUDIO_MOCK = "1";
          } ''
            cp -r ${./scripts/drivers} drivers
            mkdir -p scripts
            ln -s "$PWD/drivers" scripts/drivers
            chmod -R u+w drivers
            cd drivers
            python -m pytest tests/ -v -rs --tb=short
            touch $out
          '';
        } // pkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          # Rust QA gate (Tier 2): hermetic buildRustPackage tests.
          # US-075 AC 7: consolidated from fragile runCommand + buildRustPackage
          # variants into a single hermetic build per crate.
          test-graph-manager = graph-manager;
          test-level-bridge = level-bridge;
          test-pcm-bridge = pcm-bridge;
          test-signal-gen = signal-gen;
        };

        # -----------------------------------------------------------------
        # Apps — runnable test / dev commands via `nix run .#<name>`
        # -----------------------------------------------------------------
        apps = {
          test-unit = {
            type = "app";
            program = "${pkgs.writeShellScript "test-unit" ''
              set -euo pipefail
              export PI_AUDIO_MOCK=1
              cd ${repoSrc}/src/web-ui
              exec ${testPython}/bin/python -m pytest tests/unit/ -v -rs "$@"
            ''}";
          };

          test-integration-browser = {
            type = "app";
            program = "${pkgs.writeShellScript "test-integration-browser" ''
              set -euo pipefail
              export PI_AUDIO_MOCK=1
              export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
              export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
              cd ${repoSrc}/src/web-ui
              exec ${e2ePython}/bin/python -m pytest tests/integration/ -v -rs "$@"
            ''}";
          };

          # Full user journey integration test — speaker setup through verified room
          # correction.  Runs real DSP code with MockSoundDevice + Playwright
          # headless browser.  Slower than the regular integration-browser suite (~30-60s).
          test-journey = {
            type = "app";
            program = "${pkgs.writeShellScript "test-journey" ''
              set -euo pipefail
              export PI_AUDIO_MOCK=1
              export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
              export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
              cd ${repoSrc}/src/web-ui
              exec ${e2ePython}/bin/python -m pytest tests/integration/test_full_user_journey.py -v -rs "$@"
            ''}";
          };

          test-room-correction = {
            type = "app";
            program = "${pkgs.writeShellScript "test-room-correction" ''
              set -euo pipefail
              export PI_AUDIO_MOCK=1
              cd ${repoSrc}/src/room-correction
              exec ${testPython}/bin/python -m pytest tests/ -v -rs "$@"
            ''}";
          };

          # Room simulation E2E tests (T-067-6, US-067).
          # Runs sim config generator, correction roundtrip, and mock E2E tests
          # in isolated temp XDG directories. Pure Python — no PipeWire needed.
          # PW headless tests (T-067-5) extend this with a real PW instance.
          test-room-sim-e2e = {
            type = "app";
            program = "${pkgs.writeShellScript "test-room-sim-e2e" ''
              set -euo pipefail
              REPO_DIR="${repoSrc}"
              TMPBASE="''${TMPDIR:-/tmp}/room-sim-e2e-$$"
              mkdir -p "$TMPBASE"
              export XDG_RUNTIME_DIR="$TMPBASE/runtime"
              export XDG_CONFIG_HOME="$TMPBASE/config"
              export XDG_DATA_HOME="$TMPBASE/data"
              export XDG_CACHE_HOME="$TMPBASE/cache"
              export ROOM_SIM_OUTPUT_DIR="$TMPBASE/sim-output"
              mkdir -p "$XDG_RUNTIME_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" \
                       "$XDG_CACHE_HOME" "$ROOM_SIM_OUTPUT_DIR"
              chmod 700 "$XDG_RUNTIME_DIR"
              cleanup() {
                if [ "''${ROOM_SIM_KEEP_TMPDIR:-0}" = "1" ]; then
                  echo "Keeping temp dir: $TMPBASE"
                else
                  rm -rf "$TMPBASE"
                fi
              }
              trap cleanup EXIT
              export PI_AUDIO_MOCK=1
              export PYTHONDONTWRITEBYTECODE=1
              echo "=== Room Simulation E2E Tests ==="
              echo "Repo:    $REPO_DIR"
              echo "Tmp dir: $TMPBASE"
              echo "Output:  $ROOM_SIM_OUTPUT_DIR"
              echo ""
              cd "$REPO_DIR/src/room-correction"
              exec ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short \
                -k "test_sim_ or test_correction_roundtrip or test_mock_e2e" \
                "$@"
            ''}";
          };

          test-all = {
            type = "app";
            program = "${pkgs.writeShellScript "test-all" ''
              set -euo pipefail
              export PI_AUDIO_MOCK=1
              echo "=== web-ui unit tests ==="
              cd ${repoSrc}/src/web-ui
              ${testPython}/bin/python -m pytest tests/ -v -rs --ignore=tests/integration/ --ignore=tests/e2e/ --ignore=tests/service-integration/ --tb=short
              echo ""
              echo "=== room-correction tests ==="
              cd ${repoSrc}/src/room-correction
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== midi tests ==="
              cd ${repoSrc}/src/midi
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== drivers tests ==="
              cd ${repoSrc}/scripts/drivers
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== stability tests (pi5_thermal_watch, US-173 AC9) ==="
              cd ${repoSrc}/scripts/stability
              ${testPython}/bin/python -m pytest tests/ -v --tb=short
              echo ""
              echo "=== audio-common tests ==="
              cd ${repoSrc}/src
              HOME="''${HOME:-/tmp}" CARGO_TARGET_DIR="''${HOME:-/tmp}/.cargo-target/pi4audio-ws" PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH" ${cargoTestNonEmpty} cargo test --locked -p audio-common 2>&1
              echo ""
              echo "=== graph-manager tests ==="
              cd ${repoSrc}/src/graph-manager
              HOME="''${HOME:-/tmp}" CARGO_TARGET_DIR="''${HOME:-/tmp}/.cargo-target/pi4audio-gm" PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH" ${cargoTestNonEmpty} cargo test --locked --no-default-features --release 2>&1
              echo ""
              echo "All test suites passed."
              echo "(pcm-bridge and signal-gen: run nix run .#test-pcm-bridge / .#test-signal-gen on Linux)"
            ''}";
          };

          # Tier 1 — Dev loop (fast, non-hermetic cargo test wrappers).
          # NOT QA gates — use for quick iteration during development.
          test-audio-common = {
            type = "app";
            program = "${pkgs.writeShellScript "test-audio-common" ''
              set -euo pipefail
              export HOME="''${HOME:-/tmp}"
              export CARGO_TARGET_DIR="''${HOME}/.cargo-target/pi4audio-ws"
              export PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH"
              cd ${repoSrc}/src
              exec ${cargoTestNonEmpty} cargo test --locked -p audio-common "$@"
            ''}";
          };

          test-graph-manager = {
            type = "app";
            program = "${pkgs.writeShellScript "test-graph-manager" ''
              set -euo pipefail
              export HOME="''${HOME:-/tmp}"
              export CARGO_TARGET_DIR="''${HOME}/.cargo-target/pi4audio-gm"
              export PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH"
              cd ${repoSrc}/src/graph-manager
              exec ${cargoTestNonEmpty} cargo test --locked --no-default-features "$@"
            ''}";
          };

          test-everything = {
            type = "app";
            program = "${pkgs.writeShellScript "test-everything" ''
              set -euo pipefail
              echo "========== test-all (unit + integration) =========="
              export PI_AUDIO_MOCK=1
              cd ${repoSrc}/src/web-ui
              ${testPython}/bin/python -m pytest tests/ -v -rs --ignore=tests/integration/ --ignore=tests/e2e/ --ignore=tests/service-integration/ --tb=short
              echo ""
              echo "=== room-correction tests ==="
              cd ${repoSrc}/src/room-correction
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== midi tests ==="
              cd ${repoSrc}/src/midi
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== drivers tests ==="
              cd ${repoSrc}/scripts/drivers
              ${testPython}/bin/python -m pytest tests/ -v -rs --tb=short
              echo ""
              echo "=== stability tests (pi5_thermal_watch, US-173 AC9) ==="
              cd ${repoSrc}/scripts/stability
              ${testPython}/bin/python -m pytest tests/ -v --tb=short
              echo ""
              echo "=== audio-common tests ==="
              cd ${repoSrc}/src
              HOME="''${HOME:-/tmp}" CARGO_TARGET_DIR="''${HOME:-/tmp}/.cargo-target/pi4audio-ws" PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH" ${cargoTestNonEmpty} cargo test --locked -p audio-common 2>&1
              echo ""
              echo "=== graph-manager tests ==="
              cd ${repoSrc}/src/graph-manager
              HOME="''${HOME:-/tmp}" CARGO_TARGET_DIR="''${HOME:-/tmp}/.cargo-target/pi4audio-gm" PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.stdenv.cc}/bin:$PATH" ${cargoTestNonEmpty} cargo test --locked --no-default-features --release 2>&1
              echo ""
              echo "========== test-integration-browser (browser tests) =========="
              export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
              export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
              cd ${repoSrc}/src/web-ui
              ${e2ePython}/bin/python -m pytest tests/integration/ -v -rs --tb=short
              echo ""
              echo "All test suites passed (unit + integration + integration-browser)."
            ''}";
          };

        } // pkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          # PipeWire Rust tools — require libpipewire (Linux only).
          test-level-bridge = {
            type = "app";
            program = "${pkgs.writeShellScript "test-level-bridge" ''
              set -euo pipefail
              export HOME="''${HOME:-/tmp}"
              export CARGO_TARGET_DIR="''${HOME}/.cargo-target/pi4audio-ws"
              export PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.pkg-config}/bin:${pkgs.stdenv.cc}/bin:$PATH"
              export PKG_CONFIG_PATH="${pkgs.pipewire.dev}/lib/pkgconfig''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
              export LIBCLANG_PATH="${pkgs.llvmPackages.libclang.lib}/lib"
              export BINDGEN_EXTRA_CLANG_ARGS="-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include -isystem ${pkgs.glibc.dev}/include"
              cd ${repoSrc}/src
              exec ${cargoTestNonEmpty} cargo test --locked -p level-bridge "$@"
            ''}";
          };

          test-pcm-bridge = {
            type = "app";
            program = "${pkgs.writeShellScript "test-pcm-bridge" ''
              set -euo pipefail
              export HOME="''${HOME:-/tmp}"
              export CARGO_TARGET_DIR="''${HOME}/.cargo-target/pi4audio-ws"
              export PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.pkg-config}/bin:${pkgs.stdenv.cc}/bin:$PATH"
              export PKG_CONFIG_PATH="${pkgs.pipewire.dev}/lib/pkgconfig''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
              export LIBCLANG_PATH="${pkgs.llvmPackages.libclang.lib}/lib"
              export BINDGEN_EXTRA_CLANG_ARGS="-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include -isystem ${pkgs.glibc.dev}/include"
              cd ${repoSrc}/src
              exec ${cargoTestNonEmpty} cargo test --locked -p pcm-bridge "$@"
            ''}";
          };

          test-signal-gen = {
            type = "app";
            program = "${pkgs.writeShellScript "test-signal-gen" ''
              set -euo pipefail
              export HOME="''${HOME:-/tmp}"
              export CARGO_TARGET_DIR="''${HOME}/.cargo-target/pi4audio-ws"
              export PATH="${pkgs.cargo}/bin:${pkgs.rustc}/bin:${pkgs.pkg-config}/bin:${pkgs.stdenv.cc}/bin:$PATH"
              export PKG_CONFIG_PATH="${pkgs.pipewire.dev}/lib/pkgconfig''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
              export LIBCLANG_PATH="${pkgs.llvmPackages.libclang.lib}/lib"
              export BINDGEN_EXTRA_CLANG_ARGS="-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include -isystem ${pkgs.glibc.dev}/include"
              cd ${repoSrc}/src
              exec ${cargoTestNonEmpty} cargo test --locked -p pi4audio-signal-gen "$@"
            ''}";
          };

          # Local demo stack: PipeWire test env + GM + signal-gen + pcm-bridge + web-ui.
          local-demo = {
            type = "app";
            program = "${pkgs.writeShellScript "local-demo" ''
              set -euo pipefail
              export LOCAL_DEMO_GM_BIN="${graph-manager}/bin/pi4audio-graph-manager"
              export LOCAL_DEMO_SG_BIN="${signal-gen}/bin/pi4audio-signal-gen"
              export LOCAL_DEMO_LB_BIN="${level-bridge}/bin/level-bridge"
              export LOCAL_DEMO_PCM_BIN="${pcm-bridge}/bin/pcm-bridge"
              export LOCAL_DEMO_PYTHON="${testPython}/bin/python"
              export LOCAL_DEMO_PW_JACK="${pipewire-patched.jack}/bin/pw-jack"
              export LOCAL_DEMO_REPO_DIR="${repoSrc}"
              export PW_STORE="${pipewire-patched}"
              export PATH="${pkgs.ffmpeg-headless}/bin:${testPython}/bin:$PATH"
              exec ${pkgs.bash}/bin/bash ${./scripts/local-demo.sh} "$@"
            ''}";
          };

          # US-075 AC 4/5: PipeWire integration test — end-to-end verification.
          # Starts headless PW + GM + signal-gen + level-bridge + pcm-bridge,
          # verifies audio flow, link topology, and graph metadata, then tears down.
          test-integration = {
            type = "app";
            program = "${pkgs.writeShellScript "test-integration" ''
              set -euo pipefail
              export LOCAL_DEMO_GM_BIN="${graph-manager}/bin/pi4audio-graph-manager"
              export LOCAL_DEMO_SG_BIN="${signal-gen}/bin/pi4audio-signal-gen"
              export LOCAL_DEMO_LB_BIN="${level-bridge}/bin/level-bridge"
              export LOCAL_DEMO_PCM_BIN="${pcm-bridge}/bin/pcm-bridge"
              export LOCAL_DEMO_PYTHON="${testPython}/bin/python"
              export LOCAL_DEMO_PW_JACK="${pipewire-patched.jack}/bin/pw-jack"
              export LOCAL_DEMO_REPO_DIR="${repoSrc}"
              export LOCAL_DEMO_SH="${./scripts/local-demo.sh}"
              export LOCAL_DEMO_BASH="${pkgs.bash}/bin/bash"
              export PW_STORE="${pipewire-patched}"
              export PATH="${testPython}/bin:$PATH"
              exec ${pkgs.bash}/bin/bash ${./scripts/test-integration.sh} "$@"
            ''}";
          };

          # Real E2E tests — full stack (PipeWire + GM + services + web UI).
          # Starts local-demo, waits for health, runs pytest against live server.
          # Only physical audio hardware is absent. Linux-only.
          test-e2e = {
            type = "app";
            program = "${pkgs.writeShellScript "test-e2e" ''
              set -euo pipefail
              export LOCAL_DEMO_GM_BIN="${graph-manager}/bin/pi4audio-graph-manager"
              export LOCAL_DEMO_SG_BIN="${signal-gen}/bin/pi4audio-signal-gen"
              export LOCAL_DEMO_LB_BIN="${level-bridge}/bin/level-bridge"
              export LOCAL_DEMO_PCM_BIN="${pcm-bridge}/bin/pcm-bridge"
              export LOCAL_DEMO_PYTHON="${testPython}/bin/python"
              export LOCAL_DEMO_E2E_PYTHON="${e2ePython}/bin/python"
              export LOCAL_DEMO_PW_JACK="${pipewire-patched.jack}/bin/pw-jack"
              export LOCAL_DEMO_REPO_DIR="${repoSrc}"
              export LOCAL_DEMO_SH="${./scripts/local-demo.sh}"
              export LOCAL_DEMO_BASH="${pkgs.bash}/bin/bash"
              export PW_STORE="${pipewire-patched}"
              export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
              export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
              export PATH="${pkgs.curl}/bin:${pkgs.ffmpeg-headless}/bin:${e2ePython}/bin:${testPython}/bin:$PATH"
              exec ${pkgs.bash}/bin/bash ${./scripts/test-e2e.sh} "$@"
            ''}";
          };

          # Pi-loopback tests — real USB audio with patch cables, no speakers.
          # Runs E2E tests excluding acoustic tests. Requires --loopback-confirmed.
          test-pi-loopback = {
            type = "app";
            program = "${pkgs.writeShellScript "test-pi-loopback" ''
              set -euo pipefail
              export PI_AUDIO_BACKEND=pi-loopback
              cd ${repoSrc}/src/web-ui
              exec ${e2ePython}/bin/python -m pytest tests/e2e/ -v -rs -m "not needs_acoustic" --loopback-confirmed "$@"
            ''}";
          };

          # Pi-full tests — everything, owner present, speakers connected.
          test-pi-full = {
            type = "app";
            program = "${pkgs.writeShellScript "test-pi-full" ''
              set -euo pipefail
              export PI_AUDIO_BACKEND=pi-full
              cd ${repoSrc}/src/web-ui
              exec ${e2ePython}/bin/python -m pytest tests/e2e/ -v -rs --owner-confirmed --destructive "$@"
            ''}";
          };

          # US-077 DoD #2: Capture headless browser screenshots of dashboard
          # with steady-state 1 kHz sine. Starts full local-demo stack, plays
          # sine, uses Playwright to screenshot meters/spectrum, then tears down.
          capture-screenshot = {
            type = "app";
            program = "${pkgs.writeShellScript "capture-screenshot" ''
              set -euo pipefail
              export LOCAL_DEMO_GM_BIN="${graph-manager}/bin/pi4audio-graph-manager"
              export LOCAL_DEMO_SG_BIN="${signal-gen}/bin/pi4audio-signal-gen"
              export LOCAL_DEMO_LB_BIN="${level-bridge}/bin/level-bridge"
              export LOCAL_DEMO_PCM_BIN="${pcm-bridge}/bin/pcm-bridge"
              export LOCAL_DEMO_PYTHON="${testPython}/bin/python"
              export LOCAL_DEMO_E2E_PYTHON="${e2ePython}/bin/python"
              export LOCAL_DEMO_REPO_DIR="${repoSrc}"
              export PW_STORE="${pipewire-patched}"
              export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
              export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
              export PATH="${e2ePython}/bin:${testPython}/bin:$PATH"
              exec ${pkgs.bash}/bin/bash ${./scripts/screenshot-local-demo.sh} "$@"
            ''}";
          };
        };
      }
    ))
    // {
      nixosConfigurations =
        let
          system = "aarch64-linux";
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ nixgl.overlay ];
          };
          # Build our custom Rust packages for the Pi target.
          # These are passed to NixOS modules via specialArgs so service
          # units can reference Nix store paths instead of ~/bin.
          rustPwArgs = {
            nativeBuildInputs = [ pkgs.pkg-config pkgs.llvmPackages.libclang ];
            buildInputs = [ pkgs.pipewire ];
            LIBCLANG_PATH = "${pkgs.llvmPackages.libclang.lib}/lib";
            BINDGEN_EXTRA_CLANG_ARGS = builtins.toString [
              "-isystem ${pkgs.llvmPackages.libclang.lib}/lib/clang/${pkgs.llvmPackages.libclang.version}/include"
              "-isystem ${pkgs.glibc.dev}/include"
            ];
          };

          # Workspace source for level-bridge + pcm-bridge + signal-gen + audio-common.
          workspaceSrc = pkgs.lib.cleanSourceWith {
            src = ./src;
            filter = path: type:
              let baseName = builtins.baseNameOf path; in
              baseName == "Cargo.toml" || baseName == "Cargo.lock"
              || pkgs.lib.hasPrefix (toString ./src/audio-common) (toString path)
              || pkgs.lib.hasPrefix (toString ./src/level-bridge) (toString path)
              || pkgs.lib.hasPrefix (toString ./src/pcm-bridge) (toString path)
              || pkgs.lib.hasPrefix (toString ./src/signal-gen) (toString path);
          };

          # US-128: PipeWire 1.6.2 from nixpkgs-unstable for NixOS overlay.
          # Apply bluezSupport=false here so mesonFlags already have bluez
          # disabled — the NixOS overlay inherits these flags directly.
          pwUnstablePkg = ((import nixpkgs-pw { inherit system; }).pipewire.override {
            bluezSupport = false;
          });

          # Shared specialArgs for both NixOS configurations.
          sharedSpecialArgs = {
            inherit pwUnstablePkg;
            pi4audio-packages = {
              graph-manager = pkgs.rustPlatform.buildRustPackage (rustPwArgs // {
                pname = "pi4audio-graph-manager";
                version = "0.1.0";
                src = ./src/graph-manager;
                cargoLock.lockFile = ./src/graph-manager/Cargo.lock;
              });
              level-bridge = pkgs.rustPlatform.buildRustPackage (rustPwArgs // {
                pname = "level-bridge";
                version = "0.1.0";
                src = workspaceSrc;
                cargoLock.lockFile = ./src/Cargo.lock;
                buildAndTestSubdir = "level-bridge";
              });
              pcm-bridge = pkgs.rustPlatform.buildRustPackage (rustPwArgs // {
                pname = "pcm-bridge";
                version = "0.1.0";
                src = workspaceSrc;
                cargoLock.lockFile = ./src/Cargo.lock;
                buildAndTestSubdir = "pcm-bridge";
              });
              signal-gen = pkgs.rustPlatform.buildRustPackage (rustPwArgs // {
                pname = "pi4audio-signal-gen";
                version = "0.1.0";
                src = workspaceSrc;
                cargoLock.lockFile = ./src/Cargo.lock;
                buildAndTestSubdir = "signal-gen";
              });
              # F-465: venue profiles for GM and the web UI, read-only from the
              # flake source. A source path (no build), so board-guard can hash
              # the packaged files at eval time.
              venues = builtins.path {
                name = "pi4audio-venues";
                path = ./configs/venues;
                filter = path: type: type == "regular" && pkgs.lib.hasSuffix ".yml" path;
              };
              # US-173 AC9: D-069 thermal watch for Pi 5 load runs (stdlib
              # only; run with sudo). The writer adds its own "#!" line and
              # runs flake8 on the result, so the script's shebang is
              # dropped here; a second "#!" on line 2 fails E265.
              pi5-thermal-watch = let
                lines = pkgs.lib.splitString "\n"
                  (builtins.readFile ./scripts/stability/pi5_thermal_watch.py);
              in
                assert pkgs.lib.hasPrefix "#!" (builtins.head lines);
                pkgs.writers.writePython3Bin "pi5-thermal-watch" { }
                  (builtins.concatStringsSep "\n" (builtins.tail lines));
              # F-341: one-shot RPC client for the signal-gen/GM pre-flight.
              # The writer adds its own "#!" line and runs shellcheck on the
              # result, so the script's shebang is dropped here (SC1128).
              pi4audio-rpc = let
                lines = pkgs.lib.splitString "\n"
                  (builtins.readFile ./src/signal-gen/scripts/pi4audio-rpc);
              in
                assert pkgs.lib.hasPrefix "#!" (builtins.head lines);
                pkgs.writeShellApplication {
                  name = "pi4audio-rpc";
                  runtimeInputs = [ pkgs.coreutils ];
                  text = builtins.concatStringsSep "\n" (builtins.tail lines);
                };
            };
          };

          # Shared modules for both configurations.
          # US-163: board-specific modules live in nix/nixos/boards/<board>/.
          sharedModules = [
            nixos-hardware.nixosModules.raspberry-pi-4
            ./nix/nixos/configuration.nix
            ./nix/nixos/boards/pi4
            ./nix/nixos/lab/us156-route.nix
          ];

          # US-163: Pi 5 modules. No nixos-hardware (it targets the Pi 4)
          # and no US-156 lab route.
          pi5Modules = [
            ./nix/nixos/boards/pi5
            disko.nixosModules.disko
            ./nix/nixos/boards/pi5/disko.nix
            { system.configurationRevision = self.rev or self.dirtyRev or "unknown"; }
          ];
        in
        {
          # SD card image configuration (T-072-17).
          # Usage: nix build .#images.sd-card
          # F-273: Custom MBR image builder. Produces a flashable .raw.zst
          # with MBR partition table matching the proven sd-image.nix layout.
          # Both image builds and nixos-anywhere use matching filesystem labels.
          mugge = nixpkgs.lib.nixosSystem {
            inherit system;
            specialArgs = sharedSpecialArgs;
            modules = sharedModules ++ [
              ./nix/nixos/boards/pi4/repart-image.nix
            ];
          };

          # nixos-anywhere deployment configuration (T-072-18).
          # Usage: nixos-anywhere --flake .#mugge-deploy root@<target-host>
          # Also supports incremental upgrades (T-072-19):
          #   nix run nixpkgs#nixos-rebuild -- switch --flake .#mugge-deploy --target-host ela@<target-host> --sudo
          mugge-deploy = nixpkgs.lib.nixosSystem {
            inherit system;
            specialArgs = sharedSpecialArgs;
            modules = sharedModules ++ [
              disko.nixosModules.disko
              ./nix/nixos/boards/pi4/disko.nix
            ];
          };

          # Pi 5 first system (US-163): base system only, no audio stack,
          # on the nixpkgs linux_rpi4 kernel substituted from cache.nixos.org,
          # so nixos-anywhere can install it without a local kernel build.
          # Usage: nixos-anywhere --build-on remote --phases disko,install \
          #          --flake .#mugge-pi5-bootstrap root@<installer-host>
          # (Without the kexec phase nixos-anywhere connects as root@; the
          # installer allows root with the users.nix keys only. The first
          # reboot is a separate, announced step.)
          mugge-pi5-bootstrap = nixpkgs.lib.nixosSystem {
            inherit system;
            modules = [
              ./nix/nixos/base.nix
              {
                mugge.bootstrap.minimal = true;
                mugge.board.kernel.variant = "rpi-cached";
              }
            ] ++ pi5Modules;
          };

          # Pi 5 RAM installer for the tryboot install path (US-163).
          # Usage: nix build .#nixosConfigurations.pi5-installer.config.system.build.pi5TrybootBundle
          pi5-installer = nixpkgs.lib.nixosSystem {
            inherit system;
            modules = [ ./nix/nixos/boards/pi5/installer.nix ];
          };

          # Pi 5 full system: audio stack and the PREEMPT_RT kernel (D-013),
          # built natively on the Pi after the bootstrap.
          # Usage (on the Pi): nixos-rebuild switch --flake .#mugge-pi5-deploy
          mugge-pi5-deploy = nixpkgs.lib.nixosSystem {
            inherit system;
            specialArgs = sharedSpecialArgs;
            modules = [ ./nix/nixos/configuration.nix ] ++ pi5Modules;
          };
        };

      # T-072-17: SD card image output.
      # Usage: nix build .#images.sd-card
      # Produces a compressed .raw.zst MBR image flashable onto an SD card for Pi 4B.
      # F-273: Custom MBR image builder (sfdisk + mkfs, not systemd-repart).
      images.sd-card = self.nixosConfigurations.mugge.config.system.build.image;
    };
}
