# Backlog

Owner directive (2026-10-24): one active priority, US-163 (Pi 5 NixOS
bootstrap on .88). Everything below is parked. Nobody works on a backlog
item unless it blocks US-163. New findings go to the PM as one-liners and
land here. Maintained by the PM; the CM commits changes.

## Reserved IDs

Taken (not yet filed as records): F-361, F-362, F-363, F-364 (below);
F-365; F-366 (US-163 section); D-068 (T57 gate dropped); T65 = US-159
G16 reconciler test.
Next free: F-367, US-172, D-069, T66.

## US-163 text updates (critical path; one tracking batch before the PR)

- **D-068 OWNER DECISION (2026-10-24, process override, relayed by
  team-lead via CM):** "I don't think these tests even make sense to
  run before the installation." / "Drop gate, test after install."
  T57 is no longer a pre-erase gate. CM-T57-88-1 stopped; evidence so
  far kept. The suites run after the install (installed NixOS or the
  Mac VM) under the US-163 PR's Rule 13 review; Rule 13 unchanged.
  Amend AC22/T57 accordingly.
- QE post-install test plan (2026-10-24; P1-P3 complete is QE's
  precondition for Rule 13 approval of the US-163 PR):
  - P0: salvage the partial T57 evidence off .88 before the wipe.
  - P1: the installed configurationRevision is the test SHA; T48-T53
    on the bootstrap.
  - P2: code suites at that SHA, VM preferred; e2e and
    integration-browser VM-only (AC22 exception does not cover the
    NixOS image); Nix < 2.35 or stop; known non-blocking items listed.
  - P3: after the announced deploy switch: T54/T55, AC13, T53 on
    deploy, T51 deriver.
  - Deploy verb (Architect + QE, final; owner 2026-10-24: "boot is
    fine."): from the Mac, `nixos-rebuild boot --flake
    .#mugge-pi5-deploy --target-host ela@<current IP> --sudo` (now
    .89; see first-boot entry), then an announced reboot (not
    `switch`).

- Rename `mugge-pi5` to `mugge-pi5-deploy` in story and AC text
  (worker-1, 4de6cee0).
- MBR layout via disko legacy table; F-288 stays open.
- AC12a: firmware loads a prefixed overlay directory only if it contains
  a README (worker-1 finding).
- AC12a: card2 modules snd_soc_hifiberry_dacplus, pcm512x(_i2c),
  clk_hifiberry_dacpro are all `=m` (CM-OBS-.88-3). AE rules on whether
  clk_hifiberry_dacpro is blacklisted too.
- PO ruling on the owner's "web ui stays open":
  - AC10: 8080 open on the LAN by owner decision (F-037 known risk);
    5900 not listening or refused; 4001/4002/9100 localhost only;
    nftables default DROP and the v4/v6 scan stay.
  - AC15: "HTTPS reachable from the LAN"; allowlist part dropped.
  - AC20: F-037 accepted as known risk; the Pi 5 is not gig-ready; no
    amps or HP/IEM connected while F-037 is open.
  - AC21: drop the allowlist runbook part.
  - T53: negative case is "5900 refused (v4 and v6)".
  - The allowlist fail-closed + IPv6 AC moves to the backlog with F-037.
- T57: builder Nix pinned to 2.34.9 (2.34.8 has five Nix advisories of
  2026-10-13; SecSpec, CM-CHG-.88-2); record `nix --version`; every
  Rust crate shows a non-zero test count. The builder came up on 2.35.4
  (worker-1); QE ruling 2026-10-24: re-pin to 2.34.9 for the T57 test
  runs; the 2.35.4 bundle and installer builds stand; #49 only if
  2.34.9 cannot be installed.
- AC22 exception (PO, 2026-10-24, AE no veto): test-e2e may run once on
  .88 under Raspbian with the USBStreamer attached, because the owner
  states nothing is connected to any Pi output. Conditions: local-demo
  is isolated; `pw-link -l` runs before and after, against local-demo's
  PW and against Raspbian's own session PW, and confirms all test
  clients are on local-demo's remote; any link to the USBStreamer or
  HiFiBerry means stop and report to AE. Not for the NixOS image, not a
  general rule. Lapses if anything is connected to a Pi output.
  USED 2026-10-24: T57 ran on .88 as CM-T57-88-1 at fb7d557e (QE
  ruling; the Mac linux-builder VM has no user shell). Venue label:
  "aarch64 Raspbian .88, interim; CI F-335 broken". Only sandboxed
  suites ran; no non-sandboxed suite ran on .88. Stopped by D-068.
- Installer root login (item "(a)", owner approved 2026-10-24: "Allow
  it explicitly"): nixos-anywhere 1.13.0 needs root@ for
  `--phases disko,install`. RAM installer only: PermitRootLogin
  prohibit-password, root keys = ela's four users.nix keys. Bootstrap
  and deploy stay root-locked (board-guard negative test). Conditions
  (Architect, SecSpec): no --copy-host-keys; no
  /mnt/root/.ssh/authorized_keys before the first reboot; T53 `sshd -T`
  shows root login off; fix the installer.nix:18 comment. AC9a text
  ("PermitRootLogin no") needs amending for the installer.
- AD install challenges (2026-10-24; C1-C3 required before the erase):
  - C1 (bug, FIXED in 41fd1105, bundle verified): installer.nix
    SHA256SUMS lists itself, so `sha256sum -c`
    always fails. Exclude it or write outside $out; verify staged files
    on the Pi with `sha256sum -c`.
  - C2: in the installer, before disko, confirm MMC_SDHCI_BRCMSTB,
    EXT4_FS and MMC_BLOCK are =y (initrd mkForce list relies on it).
  - C3: `nixos-anywhere --phases disko,install`, no chained reboot;
    check /mnt/boot/firmware (config.txt, os_prefix gen with .complete,
    Image, initrd, cmdline init=, bcm2712 DTBs, overlays/README),
    /mnt/etc/ssh and keys, nftables allows 22; then reboot manually.
  - C4: WAIVED by the owner (2026-10-24, via team-lead): "No need to
    take a backup of the existing SD card." The pre-wipe copy-off
    (critical path step 5) is waived with it.
  - C5: record BOOT_ORDER, bootloader version, RAM, initrd size.
  - C6: lsblk size/serial check before disko; no USB storage attached;
    never leave a same-label fallback stick in at first boot.
  - C7: prove the tryboot abort path once (installer up with network,
    reboot, Raspbian untouched) before the real run.
  - C8: pause unattended-upgrades and apt timers between staging and
    the erase.
- T57 (PO OK): Pi 4 `mugge` and `images.sd-card` builds move to T55; the
  eval-only pi4-noop drvPath check stays before the PR.
- T57 (PO OK): test-e2e may run on .88 under Raspbian in a CM session.
  Isolated local-demo, no contact with USBStreamer or HiFiBerry;
  `pw-link -l` before and after, stop and report on any output link; no
  reboot or PW restart without owner warning; lab note marks the venue
  interim (CI is not replaced under Rule 13). AE holds a veto.
- AC12: record USBStreamer node, port names and profile; anything other
  than pro-audio with AUX0..7 is a FAIL (AE).
- New AC "usbstreamer-volume-replug" after T52, before T54 (AE).
- SecSpec: L1-L5 closed in 924f1058 (L6 known); AC9a passed at code
  level on 4de6cee0, recheck against the built drvPath.

- C7 passed 2026-10-24: Pi 5 booted the RAM installer, all functional
  checks OK. Record in the lab note the IP the installer and the
  installed system get (installer came up on .89, not .88). CM decided
  C7 option (a): both deviations accepted; rebooted back to Raspbian.

- Install link-loss gates (Architect, after the 20:13 eth0 drop):
  (1) a pre-chosen recovery path (USB stick vs SD re-flash) -- WAIVED.
  Owner 2026-10-24, verbatim, relayed by team-lead via CM: "We'll see
  once we are there." The owner accepts the risk of an erased,
  unbootable SD and decides recovery only if the link drops
  mid-install. (2) Installer link pre-check before disko -- stands.
  (3) On link loss: STOP, no retry, situation to the owner -- stands.
  Record in the US-163 lab note.

- **F-366** mugge-pi5-deploy RT kernel config fails: NVME_*_TCP_TLS
  select TLS, which kernel-rt.nix:150 forces to n; Pi 5 keepNvme=true
  skips the whole nvmeStrip (kernel-rt.nix:320). Blocks the post-install
  deploy step only, not the bootstrap. In US-163 scope (fix on the
  story branch). Fix APPROVED by the Architect: always strip fabrics
  (FC/TCP/TARGET), strip local only when !keepNvme, plus a board-guard
  assert on the evaluated config values on all boards. Rejected:
  dropping keepNvme, TLS=m. AE APPROVED too (no audio concerns), so a
  joint Architect + AE ruling on worker-1's diff
  /tmp/us163-nvme-fix-fb7d557e.diff (sha256 7d3630b4...b463; scratch
  worktree only). board-guard 102 PASS, mutation tests FAIL as
  intended; Pi 4 kernel drv unchanged; Pi 5 deploy configfile builds
  via Mac offload. Next: worker-1 commits it to the story branch after
  the first-boot checks; full Pi 5 deploy kernel build CM-MAC-BUILD-2;
  then, at the committed SHA and before the deploy step, AE N2 (the
  four HiFiBerry modules =m or absent) plus the modules.builtin check.
- 2026-10-24 20:28:03: Pi 5 restart CONFIRMED as the owner's power
  cycle ("It needed a power cycle", ~20:29, via team-lead). C8
  regressed on that boot (apt timers re-armed); re-stop granted as
  CM-CHG-.88-3. Tryboot READY checks passed (serial 0xa720b2a2, MAC
  88:a2:9e:8c:8d:4e, BOOT_ORDER 0xf461); previous-boot log waived (no
  persistent journal); tryboot go active. Record in the lab note.
- Install gate rulings (2026-10-24; record in the lab note and ACs):
  - Link pre-check criterion (Architect, option a): all RX/TX error
    counters 0; carrier_changes does not rise after the initial
    link-up; 1000/Full; 0% ping loss. rx_dropped is recorded, not
    gating (stack-level drops of unhandled multicast; installer showed
    103 -> 219 with 0 errors).
  - C2 (AD): accepted with changes. CONFIG_MMC_BLOCK=m is OK via initrd
    availableKernelModules. C3 gains: (i) mmc_block.ko inside the
    firmware-loaded gens/<id>/initrd, release matching the Image;
    (ii) init=<toplevel>/init in cmdline.txt, toplevel present;
    (iii) blkid labels FIRMWARE / NIXOS_SD.
  - Installer host keys logged by SecSpec: ED25519 QVn+Ta3b...MIw8,
    installer boot_id 4da95547.... disko,install GO issued to worker-1.
- First NixOS boot 2026-10-24: rebooted 18:59:09Z, back 19:00:01Z.
  DHCP 192.168.178.89 (not .88), found by MAC 88:a2:9e:8c:8d:4e. Host
  key ED25519 SHA256:a5kILUyr7XhT3D5Vdm4Z0lBDtitGOW2gb33socC/xSE (to
  SecSpec). /run/current-system = p9mzphhy... (installed bootstrap),
  kernel 6.12.47. CM ruling: target identity is host key + MAC, not
  IP; the deploy verb uses the current IP. Lease question ANSWERED,
  owner verbatim via team-lead: "I pinned the IP in the DHCP server.
  There's also always a DNS entry being generated,
  mugge.lab.andreas.org". CM verified read-only: the name resolves to
  .89 via LAN DNS 192.168.178.1 (not via the Mac's default resolvers);
  MAC and host key at .89 match. SecSpec ruling: the pinned IP is
  canonical, not the DNS name; any use of the name must match the same
  known_hosts entry (HostKeyAlias), never a fresh accept-new. HOLD on
  address updates: the owner later wrote "yes, pinned to 99" while the
  Pi is verified at .89; team-lead is asking whether that is a typo or
  a .99 pin (the Pi would move on its next lease). No .88/.89/.185
  reference changes until answered (file list with the CM).
- First-boot records on the bootstrap all green (CM; file
  ~/mugge-pi5-prewipe-20261024/firstboot-p9mzphhy.txt): T48 rev
  fb7d557e, current = booted = p9mzphhy; T49 running, 0 failed units;
  T50 54.6C, no throttle, end0 0 errors; T51 bootstrap part 6.12.47
  non-RT as designed, PAGESIZE 4096; AC9b FAT clean; T53
  permitrootlogin no, root no keys, ela 4 owner keys; firewall 22,
  5353, DHCP only; watchdog devices present, RuntimeWatchdogUSec=0;
  PipeWire absent, ALSA sees APC mini + USBStreamer, nothing opened.
  T52 and AE check #10 are deploy-image only. SecSpec: T48-T53 and
  AC9b PASS. SecSpec's nmap and @temp-ports checks are deferred to the
  US-163 PR Rule 13 review (owner: "I don't know why you do the
  portscan now?").

## P1

- **F-361** Link audit protects only ports named playback_AUX0..7
  (link_audit.rs:52). Medium while latent; High on a non-AUX name or a
  non-pro-audio profile. Fix: match by node and direction. Visible fault
  when ports don't resolve (routing.rs:316, 353); OpenGate refused with
  `output_ports_unresolved`; if ports vanish while Open, reduce-only
  close, read-back, stay Closed. Fix after US-160, before US-159, before
  any amps-on use. (AE, architect)
- local-demo.sh's isolated WirePlumber keeps the ALSA monitor on, so on
  hardware with sound cards it creates real alsa_* nodes and GM's prefix
  match could link the real USBStreamer. Fix: disable monitor.alsa in
  local-demo. Medium latent (AE; found by worker-1). Not blocking
  US-163: T57 namespace isolation covers it.
- **F-362** Silent ImportError module skips: test_filter_routes.py (85
  tests) plus four more modules. High; QE ACs 1-5. (worker-2)

## P2

- Pi 5 DHCP address: RESOLVED by the owner pinning .89 on the router
  (DNS mugge.lab.andreas.org; see US-163 first-boot entry). Remaining:
  record the final address in the AC and lab note after the Architect
  + SecSpec IP-vs-name ruling. (worker-1)
- **F-363** Purifi Qts test is order-dependent (`iterdir()[:20]`).
  Medium; QE ACs 1-4. (worker-2)
- US-159 G16 with AE amendments a-e and architect additions 1-3; test
  T65 (not T62). Medium; re-rate on (i) volume after replug, (ii) relink
  with gate_open true. Match by node and direction.
- US-159: G13 event-driven detection, pinned identity, re-adoption; T46
  "second -out node appears while Open"; Nix `managed = true` assertion
  and audit design note; G5a clarification; pinning scope note.
- US-159 U8 banner priority, replace with UX order: CLOSE FAILED >
  RESTORE FAILED > NON-FINITE AUDIO > THERMAL PROTECTION LOST >
  MEASUREMENT CONNECTION LOST > MUTED > GAIN NODES MISMATCH > FILTERS
  REJECTED > FILTER RELOAD FAILED > VERIFYING FILTERS > CLOSED.
- US-160: PO retitle; architect's G11(d) sentence applied globally;
  settle semantics, settle-timeout fault, mutation test (T61 renumber);
  UX N1-N4; AE N9 / AD L11 (AC5 ramp sentence); AD L10 (AC8 fold-in);
  AD M8 (who ships the G11(f) raw-bits reader).
- US-171: UX N6-N9; lease token from CSPRNG, at least 128 bit, never
  logged, non-holder renewal refused, localhost only (SecSpec); AE M2;
  AD L12 (signal-gen cap value, TF runs); F-360 AC2 oracle (AE N10).
- Interim rules: no manual pw-link with amps on. Never replug the
  USBStreamer with the gate Open; on drop-out close first, then
  pre-flight #10.
- AE R-88a recorded alongside the owner's "nothing is connected"; .88
  rated High as found.
- Pi 5 eth0 NO-CARRIER at 20:13:12 on 2026-10-24 is Pi-side, not
  physical. Owner: "Cable and switch port were fine. It needed a power
  cycle." Suspects: macb / BCM54213PE NIC, PHY, driver or firmware
  (seen under Raspbian 6.12.47; wlan0 .87 stayed up). Wired networking
  at gigs depends on it: check for recurrence under NixOS, and capture
  dmesg/ethtool if it does. Architect hypothesis (unverified): macb/PHY
  EEE (Energy Efficient Ethernet) link drops under load; if confirmed,
  persist `eee off` in the final configs. P2 (worker-1, CM). The
  install-time recovery path and link pre-check are US-163 gates, not
  tracked here.

## P3

- **F-364** local-demo seeds are copied 0444, so saving a profile fails
  with EACCES (local-demo.sh:676-680; speaker_routes.py:136;
  hardware_routes.py:120). Low. (worker-2)
- Security (owner: postponed): L6 allowlist format; SSH tunnel check on
  mugge-pi5; fail-closed allowlist and US-170
  parity before any amps-on use; CI: pin dorny/paths-filter,
  softprops/action-gh-release, actions/upload-artifact by SHA (MEDIUM,
  before next release); top-level `permissions: contents: read`;
  install_url has no hash check.
- ela is root-equivalent on the NixOS image: nix trusted-users
  (base.nix:33) plus NOPASSWD sudo (users.nix:14). Kept for the lab, so
  VM/Mac-built paths copy to .88 as ela unsigned and SecSpec's
  VM-signing conditions lapse. Revisit with the sudo policy before any
  multi-user or gig use. LOW (SecSpec).
- #49 follow-ups: M6/M7, L7-L9, TW docs items a-d,
  `-p no:cacheprovider`, 0444 seeds.
- Docs: CLAUDE.md IEM text (ch 7-8 via convolver since D-063) with the
  O-10 wording; #47 memory item 8 (sshd drop-ins first-value-wins);
  pi5-bootstrap.md HAT topic: add clk_hifiberry_dacpro (4th module)
  and HDMI audio on the vc4hdmi cards (AE, optional);
  status.md l.445 F-357 says High, should be Medium; US-169 AC5 citation
  separator.
- systemd-resolved listens on LLMNR 5355 tcp/udp and mDNS 5353 (all
  interfaces); the firewall drops them (only 22 reachable). Set
  services.resolved.llmnr = "false" on the final Pi 5 systems (LOW,
  SecSpec; T48 after first boot shows whether present); optionally in
  the installer too (worker-1). Confirmed on first boot: LLMNR on 5355
  (firewalled); avahi also warns about a second mDNS stack (resolved +
  avahi) -- pick one.
- systemd RebootWatchdogUSec=10min (default) arms the watchdog during
  reboots. Does O-24 cover it? Architect/AE to rule. P3 (worker-1).
- sshd AllowAgentForwarding yes (default) on the Pi 5. LOW, SecSpec to
  decide (worker-1).
- Pi 5 WiFi/BT firmware missing (brcmfmac, BCM4345C0). Note: wlan0 was
  the fallback path during the 20:13 eth0 drop (P2 item), so NixOS
  currently has no wireless fallback. P3 (worker-1).
- No vcgencmd on the Pi 5 image, so no get_throttled evidence for T50
  and gig thermal checks. P3 (worker-1).
- Nix on the installer is nixpkgs 2.31.2, below the 2026-10-13
  advisory fixes (2.34.9/2.35.3). If the final systems ship it too:
  bump nix.package or nixpkgs. LOW for now (local nix-daemon only, ela
  is root-equivalent); revisit before multi-user or amps-on use.
  (SecSpec)
- Mac disk nearly full (6.0 GiB free on 2026-10-24, falling slowly,
  CM). Clean up Nix store / old worktrees before heavy local builds.
  Also: a failed build grew the Mac store by 16 GiB vs 6.6 GiB
  expected; find out why (CM).
- **F-365** Hermetic nix checks broken in the sandbox (pre-existing; found in
  T57 by worker-1; CI never builds checks.*): checks.<sys>.test-midi
  (../../../configs resolves to /), test-room-correction (cp
  Permission denied on test_camilladsp.yml), test-web-ui (speaker
  YAMLs missing, graph_manager_client not importable). Owner QE;
  filed by worker-1, pending the drvPath-vs-main proof that it is
  pre-existing.
- Architect N1-N3 on #48 (CM PR comment).
- US-163 follow-ups (worker-1): installer has no configurationRevision.
  (wayvnc on the Pi 5: DONE in 433e16f7, VNC left out.)
- mugge remote-builder address: Mac LAN IP moved 192.168.178.26 to .36;
  mugge config still points at .26 (linux-builder VM, port 31022, works
  again per owner 2026-10-24). Fix: update to .36, or a fixed IP for the
  Mac from the router. Architect (2026-10-24): does not affect US-163;
  the stale address is the US-156 VM-subnet route via .26 in main's
  Pi 4 config. P3. Also: enable a non-root shell into the Mac
  linux-builder VM (its builder key is root-only), via an owner-config
  key for the builder user or another owner-provided route. Low (CM).
- After US-163: Pi self-rebuild via the Mac builder VM. Needs
  nix.buildMachines + distributedBuilds + known_hosts entry in the Pi
  config, a builder@ key on the Pi (a secret), and a stable Mac IP
  (.26 moved to .36; fixed IP or DHCP reservation; VM on :31022).
  SecSpec: MEDIUM -- builder is a trusted-user on the VM, so a
  compromised Pi could poison the store the Mac builds from, and the
  VM's SSH would likely need LAN exposure. Rule 13 code change, not in
  US-163 unless the owner asks. P3 (Architect).
- AE-F6 (routing.rs:423): check whether tracked; file if not.
- Add mmc_block to boot.initrd.kernelModules for an explicit load (now
  only via availableKernelModules). Not in this install; may ride with
  the F-366 commit if the Architect agrees. Low (AD).
- Lowest: Pi 5 deploy eval warns that disko's legacy "table" type is
  deprecated (migrate per disko's table-to-gpt guide). Check whether
  MBR is intentional for the Pi 5 FAT/firmware, else migrate before
  upstream removes the legacy type. Predates F-366; the install was
  not affected. (worker-1, re-reported via CM)
- US-170: Pi 4 allowlist and configurationRevision (AC1); Pi 4 WP ALSA
  rule; drvPath pin removal.

## Open PRs (2026-10-24, per CM)

Merged on owner consent "docs-only can be merged": #41 (6b30ca54), #46
(0c34fe82), #48 (17eb76a9); #47 (289390bf, 7/7 at 20a11758 after
update-branch). main is at 289390bf; the pre-PR US-163 tracking batch
bases on it. Branch protection requires up-to-date with main, so each
merge needs update-branch and 7 reconfirmations at the new head.

- #42 (team docs paths): 7/7 at 10c3938b. Owner answered A7 ("Yes,
  docs-only" for .claude/team/protocol/*.md). Owner answered Q2: a
  failed job still blocks. Its dispatch run 40099078614 FAILED (F-335
  artefact), so #42 needs a run with no failed job (after #49 or a
  re-run), then update-branch and 7 reconfirmations.
- #49 F-335 fix: new head b959e5c9 pending push voids verdicts; needs a
  fresh round and green T1-T3. Off the US-163 path.
- #43, #45, #44: need #49 on main and real green CI; #45 before #44.
- #36, #40: no Rule 13 review; owner direction needed (#40 IDs clash).
- chore/backlog (this file): no PR yet; docs-only.
