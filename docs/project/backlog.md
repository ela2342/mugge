# Backlog

Owner directive (2026-10-24): one active priority, US-163 (Pi 5 NixOS
bootstrap; was Raspbian .88, now NixOS at 192.168.178.89). Everything
below is parked. Nobody works on a backlog item unless it blocks US-163.
New findings go to the PM as one-liners and
land here. Maintained by the PM; the CM commits changes.

## Reserved IDs

Taken (not yet filed as records): F-361, F-362, F-363, F-364 (below);
F-365; F-366, F-367 (US-163 section); D-068 (T57 gate dropped); T65 =
US-159 G16 reconciler test; US-172 (P1, Pi 5
local display). F-368 WITHDRAWN, never to be reused (was a
duplicate of the existing F-358 for AC13).
Next free: F-369, US-173, D-069, T66.

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
    fine."): from the Mac, the darwin `nixos-rebuild-ng` from the
    flake's nixpkgs: `nixos-rebuild-ng boot --no-reexec --flake
    .#mugge-pi5-deploy --target-host ela@192.168.178.89 --sudo`, then
    an announced reboot (not `switch`). The legacy script re-execs
    the target's aarch64 tool and fails with an exec format error.
    Put this in the deploy docs (CM, CM-DEP-.89-1).

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
    nftables default DROP stays. The v4/v6 scan is DROPPED (owner,
    2026-10-25: no port scans in QA); evidence = on-device ss.
  - AC15: "HTTPS reachable from the LAN"; allowlist part dropped.
  - AC20: F-037 accepted as known risk; the Pi 5 is not gig-ready; no
    amps or HP/IEM connected while F-037 is open. F-358 is resolved
    on the Pi 5 (AC13 PASS at 132997f9), so it is not listed next to
    F-037; the fallback did not apply (PO, 2026-10-25).
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
  COMMITTED 798f2dc7 on the story branch (parent fb7d557e); touches
  only nix/checks/board-guard.nix and nix/nixos/kernel-rt.nix; diff
  sha256 = the approved 7d3630b4...b463 (CM verified). Built in
  CM-MAC-BUILD-2 and deployed to .89 (see post-deploy entry).

- US-163 post-deploy on .89 at 798f2dc7 (QE, 2026-10-24/25):
  Deploy session CM-DEP-.89-1 (x83m7bir), 2026-10-25.
  - T51 PASS (QE RULED, final): `nix store verify -r --no-trust`
    rc=0 plus identity (current = booted = x83m7bir, deriver
    kz0j0c6f, PREEMPT_RT 6.12.62). Test text changes to `--no-trust`;
    `--sigs-needed 0` is wrong (it does not skip the trust check on
    this Nix).
  - **F-358** STATUS (PO, 2026-10-25): RESOLVED for the Pi 5 (via
    05-rt-direct.conf in US-163; AC13 PASS at 132997f9). Pi 4:
    unverified. Keep the record OPEN as "Pi 4 verification
    outstanding", linked to US-170 (Pi 4 parity); do not close.
    History: HIGH, BLOCKED US-163 (AE; worker-1 agrees): AC13 FAIL,
    PipeWire data-loop.0 at RR/20, not FIFO 88 (no daemon-reload
    involved). PO RULING (2026-10-25, supersedes the earlier "known
    deviation" ruling): "F-358 is High and BLOCKS US-163. AC13 must
    PASS, with a minimal fix on the story branch (architect ruling,
    which I accept). It's no longer a 'known deviation'. Fallback,
    only if the architect rules it after diagnosis: AC13 as FAIL and
    the F-291 port as a separate change." PO advice "F-291 port next
    after US-163" applies only in that fallback.
    Security condition (SecSpec; reviewed in Rule 13 on the PR): "limited
    to the PipeWire user service units, LimitRTPRIO capped at 88-95
    (not unlimited), no global PAM/limits.conf change and no @audio
    rtprio for ela".
    AE AC13 conditions (AE co-ruling 2026-10-25 ~08:29Z + follow-up,
    via CM):
    A1: every data-loop thread of a single pipewire PID shows FF/88 in
    `ps -L`, after a cold boot AND again after one announced PW
    restart; the pipewire journal has no RTKit lines for this boot.
    Also record the main thread's scheduling class (confirms rtkit no
    longer demotes it). A1 evidence also includes 'realtime timeout'
    = 200000/200000 (AE, via CM).
    A2: record the USB interrupt thread priority, to show 88 sits
    above it; for information, not pass/fail (recorded: USB IRQs at
    FIFO/50).
    A3: the restart interrupts the USBStreamer, so announce it to the
    owner first; under the standing "nothing is connected" statement
    an announcement is enough, no ack wait.
    A1b: exactly ONE libpipewire-module-rt is loaded, and `pw-cli ls
    Module` shows the 05-rt-direct.conf fragment's args.
    A4: the fix is its own commit on the US-163 branch; AE reviews the
    diff before deploy. Pi 4 recorded as unverified (unreachable),
    under F-358.
    AC13 acceptance (PO, 2026-10-25): AE's complete A1-A4, raw output
    recorded. Until PASS: no amps-on, HP or IEM use of the Pi 5. In the
    fallback the ban lasts until the F-291 port is merged and A1/A2
    pass.
    Fix placement agreed (PO + Architect; team-lead hold lifted; CM
    told worker-1 08:31Z): on story/US-163.
    ARCHITECT RULING (2026-10-25, via CM): MINIMAL; the fallback does
    NOT apply. Cause: RLIMIT_NICE=0, so module-rt's nice -11 gets
    EPERM and RTKit then grants RR/20. Fix: one commit, all boards: a
    new PW conf.d fragment 05-rt-direct.conf. FORM CHANGED in the F-358
    review (Architect, via CM): it uses the upstream `module.rt.args =
    {...}` override; no module.rt=false and no second module-rt entry
    (supersedes the earlier two-entry form). The user@ RTPRIO path is
    moot. No unit, PAM or limit change (narrower than the SecSpec
    condition).
    Commits (team-lead + CM, 2026-10-25): b809f9c6 (first form) +
    f29e8a0f (QE board-guard, old form) were reworked; the AE's
    b809f9c6 approval is WITHDRAWN as superseded and b809f9c6 is not
    deployed alone. Pushed: c1ff084c (fix), 42c83376 (board-guard),
    132997f9 (story/US-163 = 132997f9). Effective args: nice.level=20,
    rt.prio=88, rtkit/rtportal false, rt.time.soft/hard = 200000.
    rt.time (AE request, Architect agrees; replaces the earlier "keep
    rt.time defaults" constraint, whose premise was wrong): on the
    direct path the default -1 = RLIM_INFINITY (Architect, confirmed
    in source), so without it a runaway FIFO-88 loop would buzz into
    the amps instead of being killed and failing safe; 200 ms
    restores the RLIMIT_RTTIME watchdog.
    Reviews: Architect APPROVED f87c162b..42c83376; QE ACCEPTED the
    board-guard (token-exact since 132997f9, folds in QE nit (a)).
    AE + Architect re-review DONE: 132997f9 APPROVED by the Architect
    (unconditional, f87c162b..132997f9) and the AE (no veto); QE
    ACCEPTED the board-guard. Deployed as CM-DEP-.89-2 (see below).
    RISK (Architect): the PW main thread is now really FIFO 88, so
    the 200 ms RTTIME also covers PW startup (filter-chain init, 8
    convolvers x 16k taps; unmeasured). Post-boot evidence: pipewire
    NRestarts=0, no SIGKILL/SIGXCPU, limits 200000/200000. If PW is
    killed at startup: STOP and report to the Architect.
    AC13 must PASS with A1, A1b, A2-A4; Pi 4 recorded as unverified.
    Pi 4 precondition (AE, via Architect): "Pi 4: AC13 A1 must pass
    before next amps-on use". The fragment is shared; on the Pi 4 it
    is unverified on hardware and T55 is build-only.
    Placement is SHARED (configs/pipewire + pipewire.nix) and
    intentionally changes the Pi 4 drvPaths: flag it in the PR; T55
    rebuilds the Pi 4; Pi 4 runtime stays unverified (CM).
    More acceptance (accepted via CM): main thread FF 88 with ni
    unchanged (TS or ni 19 is a FAIL; see the P2 main-thread item).
    QE evidence: the full set after
    the cold boot AND after the PW restart; a board-guard assert that
    the fragment is present and rtkit is off, plus one mutation run;
    T51 on the new deploy.
    Update the F-358 record and status.md: resolved on Pi 5, open
    for Pi 4 verification (US-170).
  - **F-367** T49 FAIL: greetd crash-loops every ~10 s (~45 restarts
    in 8 min, not marked failed): no DRM device (vc4/v3d =m but not
    loaded, /sys/class/drm empty), so the labwc greeter cannot start.
    Medium. PO RULING (2026-10-25): guard on US-163, real fix in
    US-172 (P1). Amend the T49 criterion (QE): after >= 10 minutes
    of uptime, NRestarts <= 3 for every service, and both `systemctl
    --failed` and `systemctl --user --failed` are empty. Architect
    post-reboot checks: greetd condition-skipped; user@1000 active
    from boot without SSH; systemd --user at rtprio 95. New
    US-163 AC "no-crashloop" (PO):
    after boot no systemd unit (system or user) is failed or
    restart-looping; the display stack is disabled or guarded on this
    image while no DRM device exists; checked before Gate 2. A working
    display is NOT a US-163 AC.
  - AC12 FAIL as originally written (8in/8out, QE): PipeWire has no
    USBStreamer capture node although ALSA pcmC1D0c exists;
    level-bridge-hw-in is unlinked (existing **F-328** + **F-319**).
    PO RULING (2026-10-25; AC12 AMENDED, not waived; QE + AE agree;
    by design per F-295, not a Pi 5 regression, per the Architect):
    "AC12 (amended): Playback: 8 channels via PipeWire, profile
    pro-audio, ports playback_AUX0..7 (unchanged; anything else
    FAILS). Capture: the USBStreamer capture PCM exists at ALSA level
    with 8 channels (record the device name, e.g. pcmC?D0c, and
    `cat .../hw_params` or `arecord --dump-hw-params` output).
    PipeWire capture node: deferred per F-295 (ACP deliberately
    disabled, 20-usbstreamer.conf not deployed; GraphManager brings
    it in for Live mode). Its absence is NOT a FAIL in US-163. Its
    presence without GraphManager would be a deviation that must be
    explained." No longer blocks US-163. Live mode on the Pi 5 still
    needs the capture path: backlog with F-295/Live mode.
    F-328 reconciled (QE request; Architect recommendation, PM
    adopted): re-state F-328 as "PW capture node deferred per F-295;
    ALSA 8-in verified by hw_params (AC12)"; it stays open as the
    capture tracker. New F-328 AC (QE; found by worker-1): whatever
    opens USBStreamer capture must get Interface 2 Altset 1 (8 ch),
    not Altset 2 (4 ch), and verify the channel count once open
    (relevant to F-295). PO ADVICE (2026-10-25; owner sets the final
    priority; team-lead told the owner it stands as Medium unless
    they object): re-rate High -> **Medium**. No US-163 AC depends on it
    (AC12 amended); DJ mode needs no USBStreamer capture (measurement
    uses the separate UMIK-1); only Live mode on the Pi 5 needs it.
    Re-rate trigger: High as soon as Live mode on the Pi 5 is
    prioritised or a Pi 5 Live gig image is planned. Record update in
    the pre-PR tracking batch.
  - AE check #10 PASS (enum-params; 1+1 convolver nodes, 8 gains
    0/0). AC12a full PASS. AC14 PASS, complete (quantum base 256,
    force 1024). AC13 (F-358) is the only open AE item.
  - T50 PASS (61.2C, no throttle).
  - Pending: T48 cold boot (needs an owner power cycle).
- US-163 deploy 2 (CM-DEP-.89-2, worker-1, 2026-10-25; DONE, lock
  released; announce-only via team-lead): story/US-163 = 132997f9.
  Toplevel nkifli3r...-nixos-system-mugge-25.11.20260320.812b398,
  profile system-3, boot_id 1531f01f-e66f-4f6f-9b15-a5e9c362ee10.
  Deploy 08:49:41-08:50:05Z, warm reboot 08:51:50Z, PW restart
  08:56:26Z.
  - QE wording (agreed, verbatim): "AC13: PASS (132997f9,
    CM-DEP-.89-2). Warm reboot + PW restart accepted. RT setup is
    applied fresh at every PW start (AE A1, PO accepted, QE agrees).
    T48 power cycle: PW `ps -L` recorded once as a confirmation, not
    a gate." There is no cold-boot leg.
  - **AC13 PASS** at 132997f9 (AE; PO record): main thread and
    data-loop.0 at FF/88 after the reboot AND after the announced PW
    restart; one module-rt (A1b); RTTIME 200000/200000; no RTKit;
    NRestarts 0; A2 recorded (xhci FF 50); no startup kill. The warm
    reboot is ACCEPTED as A1 (AE: RT setup is fresh at every PW
    start). The T48 power cycle adds a confirmation `ps -L`, not a
    gate. QE verdict: AC13 PASS/CLOSED; the evidence substitute for
    the missing mod.rt journal lines is ACCEPTED, no log-level change
    (the WP nice/RTKit lines are WP's own module-rt, see the WP P1
    line).
  - no-crashloop / F-367 PASS: greetd condition-skipped; user@1000 up
    from boot via linger. T49 PASS: 11 min, max NRestarts 0.
  - T51 PASS (958 paths). Thermal max 66.65 C (below the 80 C STOP).
  - **AC14 PASS**: 16/16 gain values (8 linear x Mult/Add), all 0.
    The earlier "24" = 8 linear x (Control, Mult, Add); Control
    doesn't affect audio. AC14 count corrected to 16 (PO, AE). Future
    evidence wording: "N enumerated, 16 gain-relevant" (AE). QE
    accepts 16/16 with that wording.
  - AE: the no-amps/HP/IEM condition tied to AC13 is LIFTED from the
    RT side. Any amps-on/HP/IEM use of the Pi 5 still needs the
    owner's explicit re-confirmation plus the S-012/safety.md
    pre-flight, and the F2 metering precondition (P1). The hifiberry
    2-layer condition and the US-172 gate still stand (PO, AE).
  - hifiberry-blocked PASS via /proc/asound/cards (aplay/arecord are
    not on the image). Sink S32LE/8ch/48k.
  - P2 main-thread item NOT triggered (no startup kill).
  - Still open: T48 (now the first AC17 cycle, see pre-merge runs).
    Fan question ANSWERED (owner, 2026-10-25), see Pi 5 cooling.
  - Wording: aplay/arecord are not on the image; /proc/asound/cards
    as live evidence for hifiberry-blocked is ACCEPTED (AE, QE).
    AC12/hifiberry text updated in the pre-PR batch.
  - **AC12 PASS** (QE) at 132997f9, boot 1531f01f, CM-OBS-.89-AC12
    (read-only, 09:38Z; file observe-AC12-capture-8bea1a7f.txt):
    stream0 Capture Interface 2 Altset 1 = S32_LE, 8 ch, 44.1/48k
    (Altset 2 = 4 ch); Playback 8 ch/48k on both altsets; pcmC1D0c is
    a char device; pcm0c info binds via the card-id path and the
    stream0 header. Missing PW capture node deferred per F-295
    (F-328/F-319). Minor scope deviation logged: worker-1 also read
    boot_id (static; QE no objection).
  - Suites at 9b2879eb: darwin leg ACCEPTED (QE; nix 2.34.8 < 2.35,
    all counts > 0), all green except F-363 (pre-existing, not US-163
    scope). Lab note 9b2879eb, SecSpec OK, no cuts; story/US-163 now
    bbff469e (CM, 2026-10-25).
  - Recovery (Architect): the firmware partition keeps 2 gens, now
    nkifli3r + x83m7bir; p9mz... was pruned. The PR text and recovery
    notes use gens/x83m7bircd4b7j8wchx9k1mnilzi8kl4/ as the fallback
    generation; drop any p9mz line. Pre-PR batch. After AC18b x83 is
    pruned and the fallback becomes nkifli3r (Architect).
  - F2 (pcm-bridge/level-bridge nodes after PW restart): P1, see P1.
    The US-163 PR lists F2 as an OPEN AMPS-ON PRECONDITION, not only
    as observed (team-lead, CM).
  - US-163 status after deploy 2: the F-358 fix and the F-367 guard
    f87c162b are approved, deployed together (132997f9) and PASS.
    PASS on deploy 2 (QE): AC13 (closed), T49, T51, AC12. Still
    open: the pre-merge runs below (T48 is now the first AC17 cycle);
    the pre-PR tracking batch; then the PR and Rule 13.
  - **US-163 pre-merge runs** (rulings 2026-10-25: PO scope, QE
    adequacy, Architect technical, SecSpec). QE needs items 1-5
    BEFORE its Rule 13 approval; only T56/AC19 come after merge.
    ORDER (Architect + QE, agreed): T54 -> AC18a (no-op from a clean
    tree at 132997f9) -> land all pending branch docs commits -> CM
    merges origin/main 289390bf into the branch = M -> AC18b deploys M
    from a clean checkout -> the PR opens at M -> AC17 on M. The FAT
    keeps 2 gens, so AC18b evicts x83m7bir; T54 runs first. Item 1 can
    run at any point. QE conditions: (a) the merge diff stat is
    recorded and empty under nix/, flake.*, configs/ and src/ (CM
    verified: 132 docs/project files + 2 .claude/memories files); (b)
    the AC18b nix-diff against nkifli3r shows ONLY
    configurationRevision; (c) QE ACCEPTS the T54 evidence before
    AC18b (AC18b prunes x83); (d) if the head moves: docs-only + diff
    recorded keeps AC18b/AC17 valid; any non-docs change reruns both.
    Status (CM): CM-DEP-.89-T54 granted to worker-1, starts after
    CM-OBS-.89-T53 ends; three announced reboots.
    1. OPEN (CM-OBS-.89-T53): T53-on-deploy, ONE read-only OBSERVE
       on the running deploy. NO external port scan (owner directive,
       see the test-process rule below); the running nmap scans were
       stopped. Checks: host key a5kILUyr + MAC (PASS); `sudo sshd -T`:
       permitrootlogin, passwordauthentication,
       kbdinteractiveauthentication all no (PASS); no root
       authorized_keys; `sudo ss -ltnup` with bind addresses (v4 and
       v6): only 22 and 8080 reachable off-host, 5900 not listening,
       4001/4002/9100 on 127.0.0.1 only, 5353/udp as expected; AC15
       services up, GM gate CLOSED; 8080 HTTPS reachable from the Mac.
       The 8080 allowlist pos/neg test is moot (QE): AC10/AC15
       amendment from the owner ruling, F-037 known risk; PO words it.
       SecSpec's public-IPv6 point (two global SLAAC addresses on
       end0, one EUI-64) is answered by the on-device bind addresses;
       the rest goes to backlog (P2 router inbound-v6 item). Not an
       owner question (owner). SecSpec reviews the raw output under
       Rule 13. T54 starts once T53 closes.
    2. OPEN: T54 rollback, mandatory, no re-scope (PO). Method
       (Architect, safe now): (0) gens/MAP.txt shows "2 x83m7bir...
       present" and "3 nkifli3r... present", config.txt -> nkifli3r;
       (1) `nix-env -p /nix/var/nix/profiles/system
       --switch-generation 2` + `/nix/var/nix/profiles/system/bin/
       switch-to-configuration boot`; prune removes nothing; (2)
       announced reboot; (3) the same with generation 3; (4) announced
       reboot. Explicit --switch-generation, NOT `nixos-rebuild
       --rollback` twice (the 2nd goes to gen 1 p9mz, pruned). Pass
       (QE): (a) booted toplevel = x83m7bir; (b) it survives a 2nd
       reboot; (c) back on nkifli3r: T51 identity, AC13/T49 quick set,
       AC14/#10. AC2a evidence: pointer file + both gen dirs before
       and after, in the lab note; a rollback via the one-line
       recovery edit also proves the recovery line. Expected on x83,
       recorded, not a fail: greetd loop, PW RR 20, no linger
       (F-367/F-358). If x83 fails: card reader, config.txt ->
       gens/nkifli3r.../. Reboots announce-only.
    3. OPEN: AC18, RE-WORDED to the boot verb (PO, verbatim): "(a)
       no-op: `boot` at the same SHA creates no new generation; (b)
       `boot` at a trivially different SHA -> announced reboot -> the
       new generation is active, short re-check (no failed units,
       AC14, T52 #10)." Architect: Pi 5 toplevels embed
       configurationRevision (flake.nix:821), so any new SHA is a real
       new gen. (a) pass: no new profile gen, config.txt byte-identical,
       gens/ unchanged, no reboot. (b) = deploy of the final PR head
       SHA (docs commits are enough): new gen, pointer moved, prune
       keeps new/prev/booted, T51 identity, T49, #10. Deployed code =
       PR head code; later commits docs-only, diff recorded (QE). If
       the PR head moves after AC18b, AC18b reruns on the merge SHA;
       QE decides required vs recorded. After AC18b x83 is pruned: the
       recovery line becomes nkifli3r; update the recovery notes.
    4. OPEN: AC17, two cold power cycles stay (PO). ONE owner request
       for two back-to-back cycles on the FINAL deployed SHA (after
       AC18b; QE). The first counts as T48 (incl. AE's ps -L). Per
       boot, no intervention: SSH within 3 min; new boot_id; readlink
       + configurationRevision; both failed lists empty; kernel log
       scan with per-line disposition; get_throttled 0x0; AC14/#10.
    5. AC1a: PASS (Architect) at bbff469e vs origin/main 289390bf:
       the only change is toplevel -> etc -> pipewire-configs ->
       pi4audio-pipewire-configs (+05-rt-direct.conf, store path
       c6ry7vzk...); raw diff ac1a-nixdiff-289390bf-vs-bbff469e.txt
       (worker-1). Pending: re-run on M, same criterion; raw diff
       attached to the PR (QE). (v59's "DONE at j2ykkiil" was
       premature; the earlier eval was vs local 8nv9psc1.)
       AMENDED (PO, verbatim): "The Pi 4
       drvPath differs from main only by intended all-board changes
       listed in the PR (at least the F-358 fragment
       05-rt-direct.conf; the architect lists any others). The diff
       is shown (nix-diff or equivalent) and attached to the PR. Any
       unlisted difference is a FAIL." Evidence (Architect): nix-diff
       Pi 4 `mugge` toplevel main 8nv9psc1 vs branch j2ykkiil; only
       etc -> pipewire-configs -> pi4audio-pipewire-configs differs
       (+05-rt-direct.conf, one cp); kernel drv hsf3x9wz unchanged.
       Intended all-board list = exactly 05-rt-direct.conf.
       Base = origin/main 289390bf,
       NOT 95306f66 (local-only, unpushed; owner: leave it alone; never
       a base). Merge base
       c34f7da7; c34f7da7..289390bf is docs/tracking only. worker-1
       records both drvPaths; the CM updates the branch to 289390bf
       before the PR (test merge clean).
    6. RE-SCOPED to US-170: T55 full Pi 4 builds (`mugge`,
       `images.sd-card`) (PO, Architect concurs). The PR states this
       explicitly (QE) and keeps "Pi 4 runtime change is unverified
       on hardware".
  - US-163 PR known deviations (PO, 2026-10-25, verbatim):
    - "Pi 5 firmware merges none of the config.txt dtoverlay lines
      (vc4-kms-v3d-pi5, disable-bt-pi5). The bootloader writes
      correctly and the firmware looks in the right directory, but
      nothing is merged. Effects: no DRM device (see F-367/US-172),
      Bluetooth stays active. No US-163 AC depends on it (architect +
      PO). Fix: in US-172."
    - "The board-guard check 'disable-bt-pi5 in config.txt' is green
      but has no effect (firmware doesn't apply overlays). No false
      assurance: it only checks the file, not the effect."
  - US-163 verification note (PO): the HiFiBerry block and AC12 are
    judged against the live state (aplay/arecord -l, modules,
    /proc/device-tree), not config.txt.
    AC "hifiberry-blocked" refined (PO; AE cc'd, veto domain): PASS =
    no HiFiBerry ALSA card (aplay/arecord -l), driver module not
    loaded, no WP/PW node, AND layers (b) module blacklist and (c) WP
    rule verified live. If layer (a) force_eeprom_read=0 has no
    effect: listed as a layer deviation (defence in depth 3 -> 2
    layers), fixed in US-172. A live result that isn't clean is a
    FAIL.
    AE ACCEPTS the 3 -> 2 layer deviation (no veto) for the no-audio
    bring-up: two live-verified layers (blacklist of 4 modules, all
    =m, N2 PASS; WP rule) plus a clean live result suffice.
    Conditions (AE + PO): (1) re-check the live result at the AC13
    cold boot (no HiFiBerry card in aplay -l, the 4 modules not
    loaded, no PW/WP node), evidence in the lab note; (2) the
    deviation holds only while nothing is connected (US-172 gate).
  - Pi 5 cooling (Architect via CM): the cooling_fan DT node is
    "disabled" and there is no fan hwmon, so an Active Cooler would
    not spin. Owner question ANSWERED (2026-10-25, verbatim, via
    team-lead): "No fan, but a metal case that provides a little bit
    of cooling. Let me know if you run into temperature issues." So no
    fan config fix is needed (the disabled cooling_fan node is
    correct; Architect: nothing to fix). Reference: deploy 2 max
    66.65 C.
  - THERMAL RULE (AE + Architect; replaces the "STOP at >= 80 C"
    interim line) for every Pi 5 load run: sample thermal_zone0 AND
    cpu0 scaling_cur_freq every 10 s; record max temperature and min
    frequency. WARN at >= 75 C: report to the owner via team-lead,
    keep running. STOP at >= 80 C (Pi 5 firmware throttle onset; full
    throttle at 85 C). Any frequency drop below max during a run makes
    that run's CPU/xrun evidence INVALID, even below 80 C; the run is
    repeated (AE). A frequency drop is a finding, not a STOP
    (Architect). No builds on the Pi; all builds stay on the Mac VM
    (Architect). Gig cooling: see the P1 Pi 5 thermal soak item.
  - QE request: commit a SecSpec-vetted subset of the deploy evidence
    into the US-163 PR.
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
  MAC and host key at .89 match. SETTLED (do not re-open): address is
  192.168.178.89, pinned to the MAC (owner verbatim: "Erm, 89." and
  "It's pinned to the MAC.", correcting an earlier "pinned to 99").
  Architect + SecSpec: the pinned IP is canonical; mugge.lab.andreas.org
  is an alias only (not resolvable via the Mac's default/VPN
  resolvers); any use of the name must match the same known_hosts
  entry (HostKeyAlias), never a fresh accept-new; identity is host key
  + MAC. Reference updates (.88/.185 -> .89) are GO and UNPARKED
  (deploy done, 2026-10-25): one docs batch on the story branch (TW
  docs + CLAUDE.md, worker-1 the pi5/default.nix comment, CM routes
  .claude/team); include the nixos-rebuild-ng deploy verb. Deploy-2
  finding F3 (CM): nixpkgs 26.11 renamed the darwin nixos-rebuild-ng
  binary to `nixos-rebuild`; the deploy-verb docs (.89 batch and the
  HOWTO) use the explicit store path or the version-checked binary
  name (Architect).
- Host key a5kILUyr ACCEPTED as is (joint Architect + SecSpec): TOFU
  on a MAC-verified LAN host, current-system p9mzphhy and revision
  fb7d557e matching. CLOSED, do not re-open. No extra check for
  US-163; console comparison is a P3 item (not asked). The Architect's /mnt
  pre-reboot record instruction is withdrawn (stale state). Future
  reinstalls: see the P3 pre-generation item.
  DHCP ClientIdentifier="mac" hardening DROPPED (Architect; the lease
  is pinned to the MAC); SecSpec's client-id item closed with it.
- First-boot records on the bootstrap all green (CM; file
  ~/mugge-pi5-prewipe-20261024/firstboot-p9mzphhy.txt): T48 rev
  fb7d557e, current = booted = p9mzphhy; T49 running, 0 failed units;
  T50 54.6C, no throttle, end0 0 errors; T51 bootstrap part 6.12.47
  non-RT as designed, PAGESIZE 4096; AC9b FAT clean; T53
  permitrootlogin no, root no keys, ela 4 owner keys; firewall 22,
  5353, DHCP only; watchdog devices present, RuntimeWatchdogUSec=0;
  PipeWire absent, ALSA sees APC mini + USBStreamer, nothing opened.
  T52 and AE check #10 are deploy-image only. SecSpec: AC9b full
  PASS; T48-T53 host-side PASS. @temp-ports CLOSED (empty; worker-1's
  secspec-T48-T53-raw.txt, collected 19:02Z); UDP accepted on ss + nft
  evidence. The external TCP scan (nmap -p-) is DROPPED (owner
  2026-10-25, see the test-process rule; earlier: "I don't know why
  you do the portscan now?"); the early partial run's output is
  filed.
- **TEST-PROCESS RULE (OWNER DIRECTIVE, 2026-10-25, verbatim, via
  team-lead):** "Do not make the port scan a regular part of your
  QA. It takes forever, and does not add any value on top of an lsof
  or netstat on the device." External nmap/port scans are removed
  from T53 and from all acceptance checks from now on. Listening-port
  evidence = on-device `ss`/`netstat`/`lsof` with bind addresses (v4
  and v6). Anything left open after the on-device check goes to the
  backlog, not to the owner. Docs check (PM): no test doc names an
  external port scan (only the SecSpec role's threat-model line
  "nmap-and-poke level", which stays); nothing for the .89 docs
  batch.

## P1

- **AMPS-ON PRECONDITION** (AE + Architect): "pcm-bridge/level-bridge
  PW nodes don't come back after a PipeWire restart, so metering is
  dead until the bridges restart." P1. Seen at deploy 2: 7 vs 12
  nodes after 6 min. Why: dead meters look like "no signal", and
  with the F-358 RTTIME kill PW can restart on its own. Done when
  either: (a) preferred: the bridges follow PW restarts
  (PartOf=/BindsTo=pipewire.service or reconnect logic), verified by
  an announced PW restart with 12/12 nodes and live levels; or (b)
  defence in depth: the web UI shows meters as STALE/disconnected,
  not zero, when a bridge has no PW node. INTERIM RULE: after ANY PW
  restart (including one after an RTTIME kill), restart both bridges
  and confirm live meters before amps on. Pre-existing; does not
  block US-163; the US-163 PR lists it as an OPEN AMPS-ON
  PRECONDITION. Related to F-090 (resolved; links lost on restart),
  but this is the nodes. (CM, deploy-2 finding F2)
  UX design for (b) (UX; attached, no active work):
  1. Source of truth is the backend: the bridge or GM reports per
     meter whether its PW node is present plus the last-frame time.
     STALE = node missing OR no frame for > ~1 s. A client watchdog
     on the websocket marks everything STALE if /ws drops.
  2. Look: the bar is replaced (not held, not zero) by a hatched grey
     bar reading "NO SIGNAL DATA", never "-inf dB"; peak hold and
     clip cleared; numeric readout "--"; never green, never an empty
     black meter.
  3. Amber status-bar badge "METERS STALE -- level bridge
     disconnected (k of n)", wraps, never truncated (like the U8
     banners); in the U8 priority below CLOSED as an information
     line, not a gate state; with the gate Open it turns red: "Levels
     unknown -- gate open".
  4. Recovery: live values only after fresh frames, no false peak
     from stale buffers; the badge clears on its own.
  5. QE tests: PW restart on the real stack -> every meter STALE
     within 2 s (not a zero meter); kill one bridge -> only its
     meters stale, right k of n; drop /ws -> all STALE; recovery
     after the node returns; E2E checks DOM text, not only a CSS
     class.
- **US-172** Pi 5 local display (D-022): vc4/DRM on the Pi 5,
  greetd/labwc up, Mixxx usable on HDMI. Prerequisite for DJ mode on
  the Pi 5; sits next to the F-358/F-291 work. Starting point: the
  F-367 crash loop from the US-163 deploy (vc4 not loaded, no DRM
  device). (PO, 2026-10-25)
  Architect note: on the Pi 5 every GPU/HDMI DT node is
  status=disabled, so vc4/v3d never autoload. Finding (overlay reads
  at 798f2dc7): NO firmware overlay is applied at all, not only vc4;
  disable-bt-pi5 did not apply either (BT still on serial@7d50c000).
  Checks out: config.txt has both dtoverlay lines; gens/<id>/overlays/
  has the README and both dtbo files; chosen/os_prefix and
  chosen/overlay_prefix point at gens/<id>/overlays/. So the firmware
  looks in the right place, yet nothing is merged. First US-172 read:
  /proc/device-tree/chosen/log (firmware log) for overlay load/apply
  errors. Candidate causes: Pi 5 firmware handling of os_prefix
  overlays; the dtbo coming from the bcm2711_defconfig RT kernel
  build. Evidence: ~/mugge-pi5-prewipe-20261024/
  diag-F367-overlay*-798f2dc7.txt. greetd must also be ordered after
  the DRM device, because the f87c162b condition is checked once at
  boot. Firmware 2025-08-28, variant start_cd (CM; worker-1 reads at
  08:34:52Z). The Architect cancelled the overlay diagnosis for
  US-163; it is the US-172 starting point.
  US-172 scope extensions:
  - (PO) "dtoverlays are applied on the Pi 5 (vc4-kms-v3d-pi5,
    disable-bt-pi5); verified via the live device tree."
  - (Architect + SecSpec) board-guard checks on config.txt content
    (disable-bt-pi5, vc4 overlay) give false assurance; replace them
    with checks against the live state.
  - (PO) replace the BT check with one that works: a module blacklist
    (hci_uart/btbcm) or a runtime check (no hci0) in T48.
  - (PO, Architect) confirm against the live state that the firmware
    honours the non-overlay safety lines (dtparam=audio=off,
    force_eeprom_read=0); HiFiBerry layer (a) depends on
    force_eeprom_read.
  - GATE (AE + PO): before any amps/HP/IEM or HiFiBerry use, either
    US-172 restores HiFiBerry layer (a) or the AE re-rules.
- WirePlumber threads also get RTKit RR/20 (same RLIMIT_NICE / nice
  -11 EPERM cause as F-358). Outside AC13 and US-163 scope; after
  US-163. (Architect) Deploy-2 finding F1 (CM, QE): on the Pi 5 at
  132997f9 WirePlumber's own module-rt still logs "mod.rt: could not
  set nice-level to -11: Permission denied" and activates
  rtkit-daemon via D-Bus; PW data-loops are unaffected (FF 88). WP
  has its own module-rt config, so the F-358 fragment doesn't cover
  it. Architect RULING: BACKLOG, merged here (not a new item); later
  fix = the same module.rt.args override in a wireplumber.conf.d
  fragment. AC13 covers PipeWire only.
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
  tests) plus four more modules. High; QE ACs 1-5. (worker-2) Still
  OPEN at 9b2879eb (QE): test_filter_routes.py:34-35 skips at module
  level (`pytest.skip(..., allow_module_level=True)`); the log shows
  only "collected 903 items / 1 skipped" = the whole module, 0 of 85
  tests; the 1 web-ui unit skip IS this. The other four guarded
  modules ran (speaker_lifecycle_integration 17, activate_integration
  22, speaker_routes 177, protection_integration 30): observation
  only, their guards still mask failures. Not a US-163 blocker.
- Skip reasons invisible (QE): the integration-browser run shows 10
  skips with no reasons in the log (no -rs). Make skip reasons
  visible (cf. F-362). Low.
- **GIG-READINESS PRECONDITION: Pi 5 cooling / thermal soak** (AE +
  Architect, merged; AE criteria supersede the Architect's 30 min /
  < 80 C; not US-163). Owner: no fan, metal case; boot/idle peak
  66.65 C. Sustained DJ load (Mixxx + convolver) in a passively
  cooled, closed flight case will very likely cross 80 C; expect a
  fan or heatsink for gig use. Throttling means xruns (clicks): a
  gig-readiness precondition, not a speaker-safety veto. Test:
  passive soak first, 60 min in the closed flight case, DJ quantum
  1024, Mixxx + convolver, amps off, sampling every 10 s
  (thermal_zone0 + cpu0 freq). PASS = max < 75 C, cpu0 freq never
  below max, 0 xruns, ambient recorded (margin noted for warm
  venues). FAIL: add active cooling (or a case vent design) and
  re-run. Any cpufreq drop invalidates the run (thermal rule, US-163
  section). Links to the flight-case ventilation TODO.

## P2

- "PipeWire main thread back to SCHED_OTHER: drop the F-020
  CPUSchedulingPolicy=fifo/88 from the pipewire user unit, now that
  module-rt promotes the data loops directly (F-358). At equal FIFO
  88, main-loop work (filter-chain reload, GM link changes) can't be
  preempted by data-loop.0 on a shared core, which is an xrun risk.
  Acceptance: data loops still FF 88 (AC13 A1)." Pulled into US-163
  ONLY if the post-deploy PW startup is killed by RTTIME. When done,
  re-word the AC13 "main thread FF 88" criterion. (AE + Architect)
- Pi 5 DHCP address: RESOLVED by the owner pinning .89 on the router
  (DNS mugge.lab.andreas.org; see US-163 first-boot entry). Remaining:
  record the final address in the AC and lab note after the Architect
  + SecSpec IP-vs-name ruling. (worker-1)
- Pi 5 public IPv6 (SecSpec; left open after the on-device check):
  end0 has two global SLAAC addresses, one EUI-64 (MAC-derived).
  Check the router's inbound-v6 policy and consider privacy
  addresses. Not an owner question; not US-163. Low.
- .89 docs batch (CM): the flake.nix comment on mugge-pi5-deploy still
  says "built natively on the Pi ... nixos-rebuild switch"; the real
  route is the Mac `nixos-rebuild boot --no-reexec`. Low.
- **F-363** Purifi Qts test is order-dependent (`iterdir()[:20]`).
  Medium; QE ACs 1-4. (worker-2) Re-found by worker-1 (2026-10-25):
  test_driver_validation.py::TestRealDriverRecords::
  test_sample_real_drivers_pass FAILS on darwin on main 95306f66 and
  US-163. configs/drivers/purifi-ptt6-5w04-nfa-01/driver.yml: Qts
  0.23, but Qes 0.27 + Qms 6.3 give 0.2589 (11.2% vs 10% limit); data
  from 36386c75. The unsorted sample makes it filesystem-order
  dependent, so Linux CI may pass: latent data bug + order-dependent
  test. Fix both: (a) verify/correct Qts against the datasheet; (b)
  sort the sample or check all records. Not US-163 scope, no fix in
  that PR (QE). Condition (QE): if Linux CI T1 on the US-163 PR hits
  the failing order, it still BLOCKS (Rule 13 CI green); the minimal
  fix is decided then, not waived.
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

- Legacy scripts/deploy/deploy.sh doesn't ship
  configs/pipewire/05-rt-direct.conf (F-358). Only relevant if that
  path is still used. LOW. (AE N3)
- Board-guard: assert that no other deployed pipewire.conf.d file
  mentions module.rt or rtkit (QE nit (b)). Not done: needs IFD or a
  repo-dir scan that would miss Nix-generated config. LOW. (QE, CM)
- nix/nixos/audio/pipewire.nix copies PW conf.d fragments with
  `cp ${file} dir/`, so they keep the store hash prefix (e.g.
  z7h7hys4...-30-filter-chain-convolver.conf) and load in hash
  order, not NN- order. Pre-existing, harmless today; the ordering is
  accidental. Only 05-rt-direct.conf (F-358) is copied under its
  plain name. Option (A) in the F-358 review. Owner: Architect.
  (worker-1, Architect)
- Bluetooth stays active on the Pi 5 (disable-bt-pi5 not applied; BT
  on serial@7d50c000). No hardware.bluetooth, no bluetoothd. LOW,
  home lab, no owner question now; fix with US-172. (SecSpec, PO)
- ela's PAM loginLimits (nix/nixos/audio/pipewire.nix:83-86; Pi 4 and
  Pi 5) set rtprio 95 and memlock unlimited: every ela process (SSH
  sessions, Mixxx) may go to FIFO 95, above PipeWire's 88, and lock
  all RAM (availability). Existing config, not added by the F-358
  fix. Proposal: rtprio 88 and a bounded memlock, or limits on the PW
  units only. Revisit before gig or amps-on use, with F-291 (#40).
  LOW, not blocking US-163. (SecSpec)
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
  VM/Mac-built paths copy to the Pi 5 as ela unsigned and SecSpec's
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
- Compact or cap the Mac linux-builder qcow2
  (/var/lib/linux-builder/nixos.qcow2): it grows with VM writes and
  never shrinks (19 -> 24 GiB, virtual 30 GiB, in one RT kernel build;
  Mac free 16 -> 4 GiB stopped CM-MAC-BUILD-2 run 2 at 20:58Z on the
  5 GiB line; owner lowered it to 2 GiB for that build). Fix lives in
  the owner's nix-darwin linux-builder config, not mugge.
  Owner-requested, not blocking (CM).
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
- Convolver sink's own audioconvert Props (volume, channelVolumes,
  softVolumes; all 1.0 now) are a second gain stage before the D-063
  Mults: anything raising them above 1.0 bypasses the G9 ceilings
  while the gate is Open. GM should pin them at 1.0 and check them.
  Latent, same class as AE-F6. P3 (AE).
- Compare the Pi 5 host key fingerprint (a5kILUyr) on the HDMI/serial
  console (`ssh-keygen -lf` on the host key). Optional, only if the
  owner is at the Pi anyway (never asked); MANDATORY before any gig or
  amps-on use. LOW (SecSpec).
- Future Pi reinstalls: pre-generate the installed system's host keys
  inside the verified installer session (`ssh-keygen -A -f /mnt`) and
  record the fingerprints before the reboot, removing first-boot TOFU.
  Keys live in /mnt/etc/ssh, never in the store. LOW (Architect;
  SecSpec agrees).
- Add mmc_block to boot.initrd.kernelModules for an explicit load (now
  only via availableKernelModules). Not in this install; may ride with
  the F-366 commit if the Architect agrees. Low (AD).
- Lowest: Pi 5 deploy eval warns that disko's legacy "table" type is
  deprecated (migrate per disko's table-to-gpt guide). Check whether
  MBR is intentional for the Pi 5 FAT/firmware, else migrate before
  upstream removes the legacy type. Predates F-366; the install was
  not affected. (worker-1, re-reported via CM) Update 2026-10-25
  (worker-1): seen on every `nix eval` of BOTH mugge-pi5-deploy and
  mugge-deploy, sometimes with a "read-only, set multiple times"
  error. Not blocking; not US-163 scope. Owner: Architect.
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
