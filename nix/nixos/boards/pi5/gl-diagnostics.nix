# gl-diagnostics.nix — GL self-test tools in the Pi 5 system (US-172)
#
# Architect ruling 6f394d52 (PO db9b7479, A11 7cfcb5cc): the tools the
# US-172 reads need ship in the production toplevel, behind one option, so
# a later PR can drop them for a lean gig image with one line.
#   glmark2     GL load client; its wayland-glesv2 flavour is the
#               glmark2-es2-wayland binary
#   mesa-demos  eglinfo
#   grim        Wayland screenshot (AC10 picture)
# Packages only: no services, units, users or groups, and none of them
# opens an audio device. Nothing else belongs in this list; a further tool
# needs its own ruling. Declared here only, so other boards have no such
# option (board-guard).
{ config, lib, pkgs, ... }:

{
  options.mugge.pi5.glDiagnostics.enable = lib.mkOption {
    type = lib.types.bool;
    default = true;
    description = "Ship the GL self-test tools glmark2, mesa-demos and grim (US-172, architect 6f394d52).";
  };

  config = lib.mkIf config.mugge.pi5.glDiagnostics.enable {
    environment.systemPackages = [ pkgs.glmark2 pkgs.mesa-demos pkgs.grim ];
  };
}
