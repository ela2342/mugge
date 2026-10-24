{ config, lib, pkgs, ... }:
let
  allowlist = config.mugge.firewall.uiAllowlist;
  vnc = config.mugge.vnc.enable;
in
{
  # US-163, owner ruling 2026-10-24: "web ui stays open! vnc is not needed
  # right now." The web UI (8080) is open on the LAN on every system that
  # runs it (known risk F-037). The Pi 5 disables VNC entirely; the Pi 4
  # keeps it open until its own follow-up. The source-address allowlist for
  # 5900 is unused for now (backlog).
  options.mugge.vnc.enable = lib.mkOption {
    type = lib.types.bool;
    default = true;
    description = "Run wayvnc (display.nix) and open TCP 5900 for it.";
  };

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
          ++ lib.optionals (vnc && !allowlist.enable) [ 5900 ]  # wayvnc
          ++ lib.optionals (!config.mugge.bootstrap.minimal) [ 8080 ];  # web-ui
        allowedUDPPorts = [ 5353 ];           # mDNS
        extraInputRules = lib.mkIf (vnc && allowlist.enable) (lib.concatStringsSep "\n" (
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
