# lab/us156-route.nix — lab-only static route (US-156)
#
# Routes the VM subnet via the gateway host. Lab network only: imported by
# the Pi 4 configurations, not by the Pi 5 ones (US-163 AC10, F-316 ruling:
# not part of the default image).
{ ... }:

{
  # Static route to VM subnet via gateway host
  networking.interfaces.end0.ipv4.routes = [{
    address = "192.168.105.0";
    prefixLength = 24;
    via = "192.168.178.26";
  }];
}
