{ config, lib, pkgs, ... }:
let
  allowlist = config.mugge.firewall.uiAllowlist;
in
{
  # US-163: restrict wayvnc to an allowlist of source addresses. Enabled on
  # the Pi 5 configurations; the Pi 4 keeps 5900 open until its own
  # follow-up. The web UI (8080) stays open on the LAN on every board
  # (owner ruling 2026-10-24; known risk F-037).
  options.mugge.firewall.uiAllowlist = {
    enable = lib.mkEnableOption ''
      source-address allowlist for TCP 5900 (wayvnc). When enabled, 5900
      is removed from allowedTCPPorts and only accepted from the listed
      addresses. An empty list admits no host (fail closed); IPv6 is
      dropped unless listed in v6
    '';
    v4 = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "IPv4 addresses or prefixes allowed to reach 5900.";
    };
    v6 = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "IPv6 addresses or prefixes allowed to reach 5900.";
    };
  };

  config = {
    networking = {
      hostName = "mugge";

      # nftables firewall (matches US-000a hardening)
      nftables.enable = true;
      firewall = {
        enable = true;
        allowedTCPPorts = [ 22 ]  # SSH
          ++ lib.optionals (!allowlist.enable) [ 5900 ]  # wayvnc
          ++ [ 8080 ];  # web-ui
        allowedUDPPorts = [ 5353 ];           # mDNS
        extraInputRules = lib.mkIf allowlist.enable (lib.concatStringsSep "\n" (
          lib.optional (allowlist.v4 != [ ])
            "ip saddr { ${lib.concatStringsSep ", " allowlist.v4} } tcp dport 5900 accept"
          ++ lib.optional (allowlist.v6 != [ ])
            "ip6 saddr { ${lib.concatStringsSep ", " allowlist.v6} } tcp dport 5900 accept"
        ));
      };
    };

    # SSH hardening — key-only, no root login
    services.openssh = {
      enable = true;
      settings = {
        PasswordAuthentication = false;
        KbdInteractiveAuthentication = false;
        PermitRootLogin = "no";
      };
    };

    # mDNS via avahi — hostname resolution on local network
    services.avahi = {
      enable = true;
      nssmdns4 = true;
      publish = {
        enable = true;
        addresses = true;
      };
    };
  };
}
