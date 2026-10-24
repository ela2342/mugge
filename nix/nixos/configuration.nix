# configuration.nix — top-level NixOS configuration for the Pi 4 Audio Workstation
#
# Imports all board-independent modules. The board directory
# (boards/pi4 or boards/pi5) and the deployment method (repart-image.nix or
# disko.nix) are added at the flake level (US-163):
#   - nixosConfigurations.mugge: boards/pi4 + repart-image.nix for image builds
#   - nixosConfigurations.mugge-deploy: boards/pi4 + disko.nix for nixos-anywhere
#
# The nixos-hardware.nixosModules.raspberry-pi-4 import is handled
# at the flake level, not here.
#
# pi4audio-packages is passed via specialArgs from flake.nix — it contains
# the Nix-built packages for our custom Rust services (graph-manager,
# level-bridge, pcm-bridge, signal-gen).
{ config, lib, pkgs, pi4audio-packages, pwUnstablePkg, ... }:

{
  imports = [
    # Board-independent base: users, network, kernel, RT tuning, filesystems
    ./base.nix
    # Phase 2: PipeWire + audio stack
    ./audio/pipewire.nix
    ./audio/wireplumber.nix
    ./audio/udev.nix
    # Phase 4: Display + applications
    ./display.nix
    ./applications.nix
    # Phase 3: Custom service modules
    ./services/graph-manager.nix
    ./services/level-bridge.nix
    ./services/pcm-bridge.nix
    ./services/signal-gen.nix
    ./services/web-ui.nix
    # Production defaults: enables all services with correct parameters
    ./production.nix
  ];

  # US-119: Trim Mesa and PipeWire closures for the Pi 4B audio workstation.
  # These overrides remove ~600+ MiB of unused dependencies from the SD image.
  nixpkgs.overlays = [(final: prev: {
    # Mesa: build only Pi 4 GPU drivers (V3D + VC4).
    # The default mesa enables ~17 gallium drivers and ~12 vulkan drivers,
    # pulling LLVM (~522 MiB) for llvmpipe/radeonsi shader compilation.
    # V3D and VC4 have their own compiler backends and do not use LLVM.
    # Restricting to Pi 4 drivers eliminates the LLVM runtime dependency.
    # D-022: hardware V3D GL is the only GPU path.
    mesa = (prev.mesa.override {
      galliumDrivers = [
        "v3d"       # Broadcom VC5 — Pi 4 3D rendering
        "vc4"       # Broadcom VC4 — Pi 0-3 compat + display
      ];
      vulkanDrivers = [
        "broadcom"  # V3D Vulkan (Pi 4)
      ];
      vulkanLayers = [];  # no debug layers on dedicated audio workstation
    }).overrideAttrs (oldAttrs: {
      # Disable features that auto-detect from buildInputs but require
      # drivers we've removed (r600/radeonsi/nouveau for VDPAU/VA-API)
      # or subsystems unused on the Pi 4 audio workstation.
      mesonFlags = (oldAttrs.mesonFlags or []) ++ [
        (prev.lib.mesonEnable "gallium-vdpau" false)  # needs r600/radeonsi/nouveau
        (prev.lib.mesonEnable "gallium-va" false)      # VA-API: no HW video decode needed
        (prev.lib.mesonEnable "intel-rt" false)        # Intel ray-tracing: not our HW
      ];

      # Remove spirv2dxil output — the DirectX SPIR-V compiler needs
      # the d3d12 gallium driver which we don't build.  Nix fails if a
      # declared output path is empty.  opencl stays: Rusticl is built
      # unconditionally (no v3d backend, but the library exists).
      outputs = prev.lib.remove "spirv2dxil"
        (oldAttrs.outputs or [ "out" ]);

      # Replace postInstall to drop the spirv2dxil moveToOutput calls.
      # opencl and cross_tools are kept; moveToOutput silently skips
      # missing driver-specific binaries (asahi_clc, intel_clc, etc.).
      postInstall = ''
        moveToOutput bin/asahi_clc $cross_tools
        moveToOutput bin/intel_clc $cross_tools
        moveToOutput bin/mesa_clc $cross_tools
        moveToOutput bin/panfrost_compile $cross_tools
        moveToOutput bin/panfrost_texfeatures $cross_tools
        moveToOutput bin/panfrostdump $cross_tools
        moveToOutput bin/vtn_bindgen2 $cross_tools

        moveToOutput "lib/lib*OpenCL*" $opencl
        mkdir -p $opencl/etc/OpenCL/vendors/
        echo $opencl/lib/libRusticlOpenCL.so > $opencl/etc/OpenCL/vendors/rusticl.icd
      '';
    });

    # PipeWire: upgrade to 1.6.2 (US-128), disable Bluetooth + libcamera.
    # Source + nixpkgs patches from nixpkgs-unstable (pwUnstablePkg);
    # build deps from nixos-25.11.  Adds US-112 convolver-reload patch.
    # D-019: Bluetooth fully disabled (kernel BT=n, dtoverlay=disable-bt).
    # US-119: libcamera not needed (audio workstation, no camera).
    pipewire = (prev.pipewire.override {
      bluezSupport = false;
    }).overrideAttrs (oldAttrs: {
      version = pwUnstablePkg.version;
      src = pwUnstablePkg.src;
      # Replace mesonFlags entirely — nixos-25.11 passes -Dsystemd=enabled
      # which doesn't exist in PW 1.6.2 (renamed to -Dlibsystemd=enabled).
      mesonFlags = pwUnstablePkg.mesonFlags ++ [
        (prev.lib.mesonEnable "libcamera" false)
      ];
      # Replace nixos-25.11 PW patches with nixpkgs-unstable versions
      # (written for 1.6.2), plus US-112 convolver-reload patch.
      patches = pwUnstablePkg.patches ++ [
        ../patches/pipewire-convolver-reload.patch
      ];
    });
  })];

  # Allow specific unfree packages (Reaper DAW)
  nixpkgs.config.allowUnfreePredicate = pkg:
    builtins.elem (lib.getName pkg) [ "reaper" ];

  # Minimal packages — dedicated audio workstation, not a dev machine.
  # US-117: git removed (~54 MiB self, ~364 MiB closure savings).
  # Use `nix shell nixpkgs#git` if needed for maintenance.
  environment.systemPackages = with pkgs; [
    vim
    htop
  ];
}
