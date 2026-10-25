# Backlog

Owner directive (2026-10-24): one active priority, US-163 (Pi 5 NixOS
bootstrap; was Raspbian .88, now NixOS at 192.168.178.89). Everything
below is parked. Nobody works on a backlog item unless it blocks US-163.
New findings go to the PM as one-liners and
land here. Maintained by the PM; the CM commits changes.

## Reserved IDs

Taken (not yet filed as records): F-361, F-362, F-363, F-364 (below);
F-365; F-366, F-367, F-369 (US-163 section); F-370 (P2);
F-371 (P3); F-372, F-373 (P1);
D-068 (T57 gate dropped); T65 =
US-159 G16 reconciler test; US-172 (P1, Pi 5
local display). F-368 WITHDRAWN, never to be reused (was a
duplicate of the existing F-358 for AC13).
D-069 (Architect: Pi 5 platform baseline under NixOS, PROPOSED).
Next free: F-374, US-173, D-070, T66.
PROVISIONAL (PO, 2026-10-25, pending the owner via team-lead): the
owner says GPU acceleration is a prerequisite (Wayland doesn't start
without it). PO recommends #50/US-163 scope and acceptance unchanged,
and US-172 raised to HIGH as the next active priority directly after
US-163. Read-only US-172 diagnosis may run in parallel if it doesn't
touch #50. If the owner pulls US-172 into #50, the PO reports back.
When decided: US-172.md priority line + stories index row (B3).

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
  - AC21 (amended, PO ruling (a), verbatim): "the D-022 part
    (hardware V3D GL) is NOT confirmable on the Pi 5 in US-163,
    because there's no DRM device (/dev/dri missing despite
    dtoverlay=vc4-kms-v3d-pi5,noaudio, F-367). It's deferred to
    US-172. Recorded in US-163: 'not confirmable, F-367', with the
    evidence (ls /dev/dri, deploy nkifli3r / boot 45ebdf64). Any
    other parts of AC21 stay as written and are verified as usual."
    Architect concurs; the merge does not depend on D-022 (the audio
    path has no GPU dependency). Record: D-013 re-confirmed on the
    Pi 5 (PREEMPT_RT, AC13 PASS); D-022 NOT re-confirmed on the Pi 5,
    deferred to US-172; the decision record must not say "confirmed"
    for the Pi 5; D-022 on the Pi 4 unchanged (unverified, US-170).
    US-163 PR: known deviation, next to the overlay item (same root
    cause). Status RE-SCOPED (PO).
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
    Re-confirmed on the deploy (QE, T54 step 4, nkifli3r / boot
    45ebdf64): /dev/dri absent despite dtoverlay=vc4-kms-v3d-pi5,
    noaudio; greetd condition-skipped, no labwc, no hardware GL for
    Mixxx (D-022; AC21 re-scoped, see the US-163 text updates).
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
    bbff469e (CM, 2026-10-25). Later: story/US-163 = 976ed8c5
    (lab-note docs commit, pushed; CM). Then story/US-163 = 96b4246c
    (F-369 fix, parent 976ed8c5; pushed, ls-remote verified; CM).
    Then b9e8974e (F-369 review additions, parent 96b4246c). Then
    M = story/US-163 = f0fbefd1 (merge of origin/main 289390bf,
    parents b9e8974e + 289390bf; delta docs/project 132 files +
    .claude/memories 2, 27 commits, no code; pushed, ls-remote
    verified; CM).
  - Recovery (Architect): the firmware partition keeps 2 gens, now
    nkifli3r + x83m7bir; p9mz... was pruned. The PR text and recovery
    notes use gens/x83m7bircd4b7j8wchx9k1mnilzi8kl4/ as the fallback
    generation; drop any p9mz line. Pre-PR batch. Correction (CM,
    Architect + QE): x83 was pruned at AC18a, not AC18b (a no-op
    deploy prunes the FAT to {new, prev, booted}, which collapse to
    one); the recovery line is now gens/nkifli3r.../ and x83 is in the
    store only. See F-369. Update (CM, after CM-DEP-.89-3): the FAT
    holds {2wf21ydg (M = system-4), nkifli3r (N = system-3)}; the
    fallback line stays gens/nkifli3r.../. All x83 recovery text above
    is superseded.
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
    from a clean checkout -> the PR opens at M -> AC17 on M.
    SUPERSEDED ORDER (CM, after F-369; PO + QE): F-369 fix + offline
    test -> review -> merge origin/main -> deploy of the resulting
    head (M) -> AC18b + AC18c in one DEPLOY run -> T54b -> AC17. The FAT
    keeps 2 gens, so AC18b evicts x83m7bir; T54 runs first. (Actual:
    AC18a evicted x83; see F-369, item 7.) Item 1 can
    run at any point. QE conditions: (a) the merge diff stat is
    recorded and empty under nix/, flake.*, configs/ and src/ (CM
    verified: 132 docs/project files + 2 .claude/memories files); (b)
    the AC18b nix-diff against nkifli3r shows ONLY
    configurationRevision; (c) QE ACCEPTS the T54 evidence before
    AC18b (AC18b prunes x83; in fact AC18a pruned it, after T54 was
    accepted, so (c) held); (d) if the head moves: docs-only + diff
    recorded keeps AC18b/AC17 valid; any non-docs change reruns both.
    Status (CM, 2026-10-25): T53 PASS, T54 ACCEPTED, AC18a PASS.
    AC18b NOT GRANTED: held until the F-369 fix is deployed (PO;
    item 7). HELD for worker-1's follow-up commit + QE acceptance;
    then (CM) merge origin/main 289390bf into the branch -> DEPLOY.
    UPDATE (CM, 2026-10-25): reviews closed, merge done (M =
    f0fbefd1). AC18b GRANTED and IN PROGRESS, no longer HELD:
    CM-DEP-.89-3 to worker-1, AC18b + AC18c + T54b in one run, steps
    (a)-(e) (item 7), exact {M, N} criterion, thermal sampler
    condition; three reboots announced to team-lead. Next: AC1a
    re-run on M (separate grant) -> PR opens -> AC17.
    RESULT (CM, 2026-10-25): CM-DEP-.89-3 COMPLETE, every step PASS
    (worker-1; CM spot-checked), lock released. M = f0fbefd1 -> Pi 5
    toplevel 2wf21ydg = system-4; N = nkifli3r = system-3.
    Precondition {N}: PASS. (a) deploy rc=0, 14 paths, Mac profile
    unchanged (system-150), gens {M, N}, os_prefix at M. (b) reboot
    (boot c3a7a23f): booted M, T51 identity OK, check #10 16 gains
    0.0, gate closed. (c) AC18c no-op redeploy: 0 paths, no new link,
    {M, N}; PASS by the CM content ruling ("unchanged" = content; the
    hook rewrites config.txt + MAP.txt with identical content, see
    F-370). (d) T54b rollback: os_prefix at N, boot 80fc4047 booted
    N, {M, N}; N's old hook also kept both. (e) back to M: boot
    eeddb8b6, booted M, T51 OK, check #10 OK. MAP sha 90b081b2
    constant; config.txt 012d89d4 -> 315a13d3 -> 012d89d4 (os_prefix
    only). Thermal valid: 41 samples, 63.9-66.1 C, 2.4 GHz = max,
    rpi_volt 0, no cooling devices (criterion 1 N/A). Deviation: (c)
    attempt 0 failed on a local helper exec bit; nothing ran on the
    Pi (QE: not a finding).
    QE VERDICT: **AC18b PASS, AC18c PASS, T54b PASS**, unconditional.
    QE spot-checked: M (f0fbefd1) contains b9e8974e (merge-base);
    boots 45ebdf64 -> c3a7a23f -> 80fc4047 -> eeddb8b6; final state
    system-4 = M, os_prefix M, {M, N}, gate closed, 16 gains 0.
    NEXT: AC1a re-run (Mac nix-diff 289390bf vs f0fbefd1; Architect
    verdict) -> PR opens -> AC17. QE expectation for AC1a: only F-358
    (05-rt-direct.conf) plus configurationRevision; anything else
    needs a per-item disposition (CM passed to the Architect: the PO
    criterion lists only 05-rt-direct.conf). [SUPERSEDED (CM,
    2026-10-25): the Architect ruled that configurationRevision is set
    only in pi5Modules (flake.nix:827 at f0fbefd1), so it is not in
    the Pi 4 toplevel. The AC1a criterion is exactly
    05-rt-direct.conf; anything else FAILS; no advance PO amendment.
    QE concurs and verified it ("my expectation was wrong").]
    AC1a RE-RUN ON M: **PASS** (Architect, checked the file
    personally). Evidence (worker-1, CM cross-checked):
    ac1a-nixdiff-289390bf-vs-f0fbefd1.txt; Pi 4 toplevel 8nv9psc1
    (289390bf) vs j2ykkiil (f0fbefd1), the same drvPath as at
    bbff469e; kernel hsf3x9wz identical; nix-diff rc=0, only etc ->
    pipewire-configs -> pi4audio-pipewire-configs
    (+05-rt-direct.conf); 0 hits for configurationRevision, revision
    or the SHAs; no other inputs; the raw diff body is identical to
    the bbff469e run. PR: attach
    ac1a-nixdiff-289390bf-vs-f0fbefd1.txt as the raw AC1a evidence.
    Still open: the Pi 4 AC13 A1 precondition before amps-on (Pi 4
    runtime unverified, US-170). NEXT: the PR opens (worker-1 is
    finalising the body; PM status list us163-ac-status-v1.md, sha256
    d291a9ed...) -> AC17.
    HEAD MOVES AFTER f0fbefd1 (joint Architect + QE ruling, sent by
    the Architect at QE's request; via CM, 2026-10-25): condition (d)
    stands, as option (A).
    - Evidence is pinned to f0fbefd1 / 2wf21ydg; AC17 runs on
      2wf21ydg.
    - The PR body carries (1) `git diff --stat f0fbefd1..head`
      showing docs/ only; (2) a nix-diff of the mugge-pi5-deploy
      toplevel f0fbefd1 vs head showing only configurationRevision;
      plus an identical Pi 4 `mugge` drvPath.
    - Any non-docs commit: redeploy the head, re-run T51 identity,
      check #10 (gains/gate) and the >= 2-complete-gens snapshot,
      plus the ACs it touches; AC1a if Pi 4 inputs change.
    - AC17 part (SETTLED, single wording): QE's (d) stands as
      written: any non-docs change re-runs AC18b AND AC17, plus the
      T51 / check #10 / >= 2-gens snapshot, plus AC1a if Pi 4 inputs
      change. Docs-only: no redeploy; the two PR proofs above. A
      narrower AC17 clause (only boot, kernel, firmware, power or
      thermal paths) was proposed and withdrawn (Architect).
    POST-v77 (via CM, 2026-10-25):
    - story/US-163 = afbc04ae: docs-only lab-note fix of the FAT
      section, parent f0fbefd1 (pushed, verified). Docs-only after M,
      so the option (A) PR proofs above apply.
    - QE folds AC2, AC3, AC4 into the AC17 OBSERVE on M; every
      command printed with a label and its rc.
      AC2: `findmnt -no SOURCE / /boot/firmware` plus `lsblk`; root
      and the FAT partition on mmcblk0. disko.nix:40 stays in the PR
      as the design half.
      AC3: /sys/kernel/realtime = 1 (if absent: uname -v plus
      config.gz); PAGESIZE = 4096.
      AC4: trip types and temps side by side; the critical/hot trip
      above 80 C; the 50000 trip is active/passive.
    - usbstreamer-volume-replug: AE chose (a), run inside the AC17
      session. CHANGE step: USBStreamer `authorized` 0 -> 1, with
      BEFORE and AFTER reads (usbmixer, pw Props, the 16 gains,
      links). If usbmixer shows hardware Volume controls: add one
      announced physical replug by the owner. PASS: every value
      after <= before and the gains still 0. FAIL: G16 becomes High,
      an amps-on blocker owned by US-159. Node or links not coming
      back is a recovery finding (amps-on precondition), not an AC
      fail.
    - F-341 AC3 and US-159 T47: FINAL (b), both out of US-163 (PO;
      AE agrees; QE: no US-163 evidence relied on `nc`, the GM gate
      used bash /dev/tcp and AC14 used pw-cli/pw-dump). The PR lists
      both under "not run in US-163", each pointing to the AMPS-ON
      PRECONDITION LIST (Pi 5) in P1. T47 stays with US-159.
    - AC8, AC9a, AC11: Mac-only, worker-1, pending. The CM holds the
      PR until worker-1's two proof files cited by the body are on
      disk.
    PR #50 (2026-10-25, via CM): head afbc04ae -> main 289390bf;
    body sha 8e9cba4a built from PM status list v2 (then v3,
    6ad1e4f8, adds F-362 and F-371). Head-move proofs and the AC1a
    nix-diff posted as a PR comment; the CM proof-file hold is
    lifted. CM rulings: AC8/AC9a/AC11 PASS (Mac-only, worker-1), QE
    review pending; AC11 side finding F-371. AC2 design half done.
    - Verdicts at afbc04ae (all posted verbatim): UX APPROVE
      6398304093 (re-check on any head move); Architect APPROVE
      6398313761 (afbc04ae plus docs-only commits; re-rules only if
      AC17 shows realtime/PAGESIZE/FIFO 88/RTKit/frequency faults);
      SecSpec APPROVE 6398314068 (any non-docs commit voids; CI at
      the final head: no failed job beyond F-363); AE APPROVE
      6398314322 (does not clear amps-on; re-check any push before
      merge; AC17-B FAIL goes to G16 High under US-159); AD APPROVE
      (does not cover CI or AC17; docs-only re-review needs diffstat
      plus nix-diff vs f0fbefd1); TW CHANGES REQUESTED 6398315124;
      QE pending. All lapse at the next head move (strict main
      protection).
    - v79 committed at 91404ac9 (CM; sha 02b54ecd... verified).
    - QE (2026-10-25): AC2, AC3, AC4, AC8, AC9a and AC11 PASS. QE's
      #50 verdict waits for the final head (PO ruling 1).
    - TW routes (CM): B1/B2 on the separate branch
      docs/US-163-ac21-batch (worktree at afbc04ae); TW owns 6 files:
      config.md, CLAUDE.md, rt-audio-stack.md, safety.md,
      SETUP-MANUAL.md, nixos-upgrade.md. The CM merges it into
      story/US-163. S1/N1/N2: worker-1, lab note only.
    - B3 DELIVERED (PM, 2026-10-25): /tmp/pm-b3, base afbc04ae, 25
      files (14 new, 11 modified), MANIFEST.txt with sha256s. The CM
      ACKed 26; the difference: D-069 is the Architect's file (byte
      copy of /tmp/arch-D-069.md), F-368 is withdrawn, and F-328 was
      added (its update was due in this batch). F-037, F-328, F-341
      and F-358 get "Update 2026-10-25" sections; headers and index
      rows unchanged. US-159 G16 AE a-e from the AE's verbatim text;
      T65 lists AE's five cases plus the Architect's two.
    - v80 committed at f075d26d (CM). B3 verified by the CM (all
      files pass shasum -c; D-069 byte-identical; none of the 11
      modified files touched on the branch since afbc04ae).
    - B3 v2 (PM, 2026-10-25): adds defects/F-373.md, the F-373
      defects-index row and the status.md F-373 row (next free
      F-374). 26 files (15 new, 11 modified). New MANIFEST.txt sha
      3fdd2a28...; v1 kept as MANIFEST-v1-superseded.txt. The CM
      commits B3 at the single head move after #49 merges, with the
      TW's 9a7e9562 and the lab notes (82fcf9e8, afd6e065).
    - QE on #50 (6398380045): NOT APPROVED until T1-T3 green with
      counts > 0 and the Nix version in the log on the final head,
      the head-move drvPath proof, and AC17 Session B plus the cycles
      accepted. QE's Nix-pin request on #50 and its `toString ./.`
      one-liner are withdrawn (covered by F-335/#49).
    - AD on #50: T1 cannot pass until #49 merges and #50 merges main.
      That merge touches flake.nix, so the AD M2 proof is the
      mugge-pi5-deploy nix-diff vs f0fbefd1/2wf21ydg showing only
      configurationRevision, plus the Pi 4 drvPath unchanged; else
      AC17 is re-run. A docs-only diffstat is not enough. Merge order:
      #49, then #50.
    - F-362 identity (PM ruling): ONE item. QE's "module-level skip
      reads as 1 skipped" is the same test_filter_routes.py:34-35
      guard. #50 body: F-362 open, pre-existing, NOT a #50 merge
      blocker (settles AD M1 on #50).
    - TW branch docs/US-163-ac21-batch: f2a1ee0c (B1/B2, ACKed),
      head e7086f9e (+ safety.md 5 lines, AD L1); the AE reviews it
      with the rest of safety.md at the re-review. Section 8.7 waits
      on worker-1's commands file (relayed).
    - AC17 Session B (CM-CHG-.89-5): step (a) software
      re-enumeration PASSED on safety (nothing raised); recovery
      finding F-373. Step (b), the owner's physical replug, is
      cleared.
      AE + QE RULING (2026-10-25, to the CM; PO confirmed): step (b)
      is DEFERRED to F-373 and is not a US-163 AC; AC17 (AC16b) is
      satisfied by step (a) plus QE's per-cycle check on the two
      cold cycles. The replug is not on the owner's physical list for
      US-163. The step-(b) timeout at 14:25:31Z happened because the
      owner was never asked; it is not a Pi finding. The hw volume
      and the PW volumes were already at maximum, so a replug can't
      raise them, and WP re-disabled the card. Re-open trigger (AE;
      PO addition): if the
      USBStreamer hw volume is ever set below 0 dB (e.g. by US-159),
      OR the WP rule / link management for the USBStreamer changes
      (disable rule, autoconnect, GraphManager re-adoption), the
      physical replug is a required safety test again.
    - B3 v3 (PM, 2026-10-25): US-163 AC16b amended (text above);
      F-373 status, AC2 (re-test with a physical replug and the
      step-(b) read set), AC3 (AMPS-ON item 8), AC4 (re-open
      trigger). 26 files; MANIFEST.txt sha 7002b0a7...; v2 kept as
      MANIFEST-v2-superseded.txt. Other 24 files unchanged from v2.
    - B3 v4 (PM, 2026-10-25; supersedes v3): F-373 AC2 uses the AE's
      step-(b) read set; AE and QE named as ruling; US-163 AC16b adds
      QE's per-cycle check and "not on the owner's physical list".
      MANIFEST.txt sha 9a5da8ef...; v3 kept as
      MANIFEST-v3-superseded.txt. The CM notes v4 as the frozen batch
      for the #50 head move.
    - AC17-B step (c), PW and bridge restart: PASS (worker-1; CM
      verified; AE ruled PASS after checking the raw files 5aad9083
      and 64fdbcdf). Graph-manager's watchdog re-armed, the 16 gains
      came up at 0, the gate is closed, and the PCM reopened with its
      channel map restored. AE: AC17 is satisfied by (a) and (c), (b)
      deferred to F-373; QE's per-cycle check on the cold cycles
      stays. CM-CHG-.89-5 released after (c), then re-opened
      read-only for cold cycles 1 and 2. Script additions: the
      USB-POWER bmAttributes/bMaxPower read, and an ssh
      ServerAlive option in pi.sh so a poll doesn't hang when the
      power is cut.
    - AE (non-blocking): after each cold boot, a read-only ps -L
      check (PW main and data-loop.0 at FF 88, RTTIME
      200000/200000) confirms F-358 survives a real cold boot.
      worker-1 runs it after each cycle.
    - B3 v5 (PM, 2026-10-25; supersedes v4): F-373.md gets the
      step-(c) recovery data point and AC5 (recovery shape); US-163
      AC16b records step (c) PASS and "AC17 satisfied by (a) and
      (c)"; AC17 adds the AE ps -L check after each cold boot. Index
      rows unchanged. MANIFEST.txt sha e40664ca...; v4 kept as
      MANIFEST-v4-superseded.txt. Other 24 files unchanged from v4.
    - B3 v6 (PM, 2026-10-25; supersedes v5): F-373.md only. AC5 is
      the AE's verbatim safety shape (any recovery route; gains 0
      and gate closed when audio can flow; deliberate ramp; meters
      recover; no abrupt resume), replacing v5's "recovery shape".
      PW + bridge restart is recorded as the current interim
      recovery procedure, not the fix. MANIFEST.txt sha
      ff0687e9...; v5 kept as MANIFEST-v5-superseded.txt. Other 25
      files unchanged from v5.
    - AE: the USBStreamer is bus-powered on root port 1-1. Each cold
      cycle records bmAttributes (expected 0x80) and bMaxPower.
    - AC17 COLD CYCLES 1 AND 2: PASS (CM, 2026-10-25). The owner
      pulled the cable after the CM's GO each time. Boots 7f56af91
      and 8c6239cb, booted == 2wf21ydg. Each cycle: USB
      re-enumeration; USBStreamer bus-powered (1-1, bmAttributes 80,
      500 mA); nothing louder than the step-(a) BEFORE values; gains
      0, gate closed; 24/24 links; one sink running; spa.alsa errors
      0. ps -L: PW main and data-loop.0 at FF 88, RTTIME
      200000/200000, so F-358 survives a real cold boot. Thermal max
      63.9 C. CM-CHG-.89-5 released 15:30Z. The owner is done at the
      Pi; no more physical steps for US-163 (CM). QE ruling on AC17
      pending.
    - Evidence limits (CM, recorded): the USB devnum stays 2 on a
      fresh enumeration, so the proof of a cold cycle is the owner's
      pull plus the down windows. Early-boot journal timestamps come
      before the clock is synced.
    - Lab note d15a1bec (CM, local, on top of 1443401d) joins the #50
      head move.
    - AE: AC17 PASS and CLOSED for US-163. The AFTER amixer dumps
      are byte-identical to the step-(a) BEFORE (29d42498), so the
      USBStreamer powers up at hw 0 dB and re-open trigger (iii)
      stands. Cold boots enumerate before PW, so the F-373 hot-replug
      path is not exercised; that is scope. QE's AC17 verdict is
      pending. B3 v7 (CM: yes) records AC17 PASS in US-163.md once QE
      rules; the lab note alone is not enough.
    - RULED (AE, verbatim): "Current: PW main thread and data-loop.0
      both SCHED_FIFO 88 (main thread via F-020 unit, data loop via
      module-rt / 05-rt-direct.conf), verified on 2 cold boots.
      Backlog P2 (not US-163): return the main thread to SCHED_OTHER
      so only the data loop runs at 88." The Architect owns the P2
      design. Any image-status note listing the main thread as
      SCHED_OTHER misreads P2 as the current state and is corrected
      (the owning author; not in B3, PM checked).
    - Open (PM -> CM -> QE, PO): AC19 says the Pi is redeployed from
      the merged main SHA "and AC17 is re-checked". Two more owner
      cold cycles, or rule (d) (docs-only after M)? CM recommends a
      warm-reboot AC17 read set after the redeploy, with cold cycles
      only if the nix-diff shows a real change. The PM's owner status
      (via team-lead) said two more cycles after the merge; corrected
      once QE and the PO rule.
    - AD APPROVE is comment 6398339160 (CM). AD M2 precise: the
      f0fbefd1 -> final diffstat is docs-only AND the
      mugge-pi5-deploy nix-diff shows only configurationRevision,
      else AC17 is re-run. AD L2 precise: the US-172 check is HDMI
      ALSA devices device.disabled = true in pw-dump, none a sink.
      AD L1 precise: US-170 AC13 A1 += "NRestarts 0, no SIGKILL at
      startup with production 16k-tap coefficients" (in B3 US-170
      AC6); AMPS-ON + safety.md: "an unannounced PW SIGKILL is a
      USBStreamer interruption; follow F2" (CM sent it to the TW).
    - Push gates (CM): (1) #49 lands; (2) Architect docs-only scope:
      CLAUDE.md, .claude/team/config.md and SETUP-MANUAL.md count as
      docs-only; docs-only = no file under src/, nix/, configs/,
      scripts/ (READMEs inside src/ included) and no flake.nix or
      flake.lock change. Per-commit gate: mugge-pi5-deploy nix-diff
      only configurationRevision and the Pi 4 drvPath unchanged,
      else rule (d). #49 at df4a6a9b sets repoSrc=${self} only in
      the app scripts, not in nixosConfigurations, so option (A)
      survives taking main; the Architect re-confirms at b959e5c9;
      the CM runs the empirical nix-diff once after the rebase.
    - Session B ruling (CM/AE): amixer by card ID via a temporary
      alsa-utils copy; software re-enumeration, then the owner's
      physical replug; reads are read-only; PASS when nothing goes
      up. worker-1 is revising the scripts and collects the real
      install commands for the TW's B2 in
      /tmp/us163-install-cmds-for-tw.md.
    - TW blocking: B1 the AC21 .89 docs batch (config.md still .185;
      safety.md lacks the Pi 5 amps-on boundary and the F2 rule); B2
      NEW docs/guide/howto/nixos-upgrade.md is wrong for the Pi 5
      (kexec install, `switch` = live PW restart interrupting the
      USBStreamer, rollback via --rollback/U-Boot; no Pi 5 install,
      rollback or card-reader recovery procedure); B3 the tracking
      batch. S1 = UX note 1: lab note deploy 2 Step 2 recovery line
      names nkifli3r (just deployed); the fallback was x83m7bir.
      N1/N2: lab-note heading levels, a timezone label.
    - AD: M1 F-362 needs a definition and disposition in the PR body
      before the final head; M2 = rule (d).
    - CI run 40198045816: nixos-eval PASS (pi5-prune-gens 13/13 in
      the log, QE's CI item met); test-and-build FAIL = F-335 (`cd
      ...-source/src/web-ui: No such file`), NOT F-363; T1-T3 ran 0
      tests. Under Q2 this blocks #50: #50 DEPENDS ON #49.
    - PO RULINGS: (1) sequence: #49 lands -> ONE head move on #50
      (B1, B2, B3, S1 + the main update) -> ONE re-review round by
      all 7 on the final head. #49 is IN FOCUS, limited to F-335, no
      scope additions. QE and AD may hold until the final head. (2)
      B2: the TW writes it if the role permits and the file isn't
      delegated (L-046), else worker-1 from TW's text; Architect + QE
      verify the commands (darwin nixos-rebuild-ng --no-reexec,
      `boot` plus announced reboot, .89, rollback via pointer and
      generations). (3) Close review not by the TW: Architect the
      factual parts (config.md .185 -> .89, host key + MAC, Pi 5
      references), AE the safety.md parts (veto); same split for B2.
      S1 goes INTO #50 in the same head move, as a traceable
      correction: the line reads x83m7bir..., plus a note "corrected
      in #50: originally said nkifli3r..., which was the generation
      just deployed". worker-1 edits (their file).
    - Branch route for TW (team-lead constraint): share worker-1's
      branch only with strictly disjoint file sets agreed with the CM
      before TW starts; worker-1 keeps the lab note; the CM picks the
      worktree/branch and commits by explicit SHA; docs-only.
    - AC17 Session A (CM-OBS-.89-4, done, released; raw
      ac17-A-observe-20261025T133240Z.txt): AC2/AC3/AC4
      PASS-candidates (QE rules); QE's findmnt form fails as written
      (AC text fix with QE). vcio: CONFIG_BCM_VCIO=y, /dev/vcio
      present, so the libraspberrypi CHANGE branch applies. The
      USBStreamer HAS hardware Volume controls: under AE (a) the
      owner's announced physical replug is needed; the read method is
      with the AE. GENS-dirs script bug (wrong .complete path):
      worker-1; not a FAT finding (config.txt/MAP shas unchanged).
      Session B (CHANGE: libraspberrypi + replug) after CM review.
    - AC3 wording (Architect): /sys/kernel/realtime is absent BY
      DESIGN (it came from the out-of-tree RT patch; since 6.12
      PREEMPT_RT is mainline Kconfig). AC3 PASS = uname -v
      "PREEMPT_RT" + CONFIG_PREEMPT_RT=y, plus PAGESIZE 4096, as the
      PRIMARY check. Amend the AC3 text and the PR body AC table.
    1. PASS (QE + SecSpec; CM-OBS-.89-T53, T53b, T53c): T53-on-deploy,
       ONE read-only OBSERVE on the running deploy. NO external port
       scan (owner directive, see the test-process rule below); the
       running nmap scans were NOT stopped; they ran to completion at
       12:30:10Z, past the directive (CM correction; v66 said
       "stopped"). Checks: host key a5kILUyr + MAC (PASS); `sudo sshd
       -T`: permitrootlogin, passwordauthentication,
       kbdinteractiveauthentication all no (PASS); no root
       authorized_keys; listener clause (QE + SecSpec joint, replaces
       all earlier wording): "Evidence: on-device `sudo ss -ltnup` (bind
       addresses shown) plus `sudo nft list ruleset`. Non-loopback TCP
       listeners are exactly 22 and 8080, each REQUIRED on the v4
       wildcard 0.0.0.0. The v6 wildcard [::] is allowed for either but
       not required. 4001, 4002 and 9100 listen on 127.0.0.1 only.
       Nothing on 5900. Non-loopback UDP is limited to 5353 (avahi) and
       DHCP client sockets. Any other listener, or an expected one on an
       unexpected address, gets a per-line disposition, or T53 FAILS."
       QE amendment for future checks: "Loopback-only listeners from
       known units are benign; list them." AC15 services up, GM gate
       CLOSED; 8080 HTTPS reachable from the Mac. Result: SecSpec
       ACCEPTED all listener dispositions (LLMNR 5355 and avahi
       ephemeral sockets dropped by nft; loopback extras benign).
       SecSpec gap read CM-OBS-.89-T53b: no root entry in
       /etc/ssh/authorized_keys.d, 8080 owner non-root with its unit
       name recorded, host-key pin line logged. The 8080 allowlist
       pos/neg test is moot (QE): AC10/AC15 amendment from the owner
       ruling, F-037 known risk; PO words it. SecSpec's public-IPv6
       point (two global SLAAC addresses on end0, one EUI-64) is
       answered by the on-device bind addresses; the rest goes to
       backlog (P2 router inbound-v6 item). Not an owner question
       (owner). SecSpec reviews the raw output under Rule 13. T54 starts
       once T53 closes.
    2. ACCEPTED (QE): T54 rollback round trip done 12:34-12:41Z; back
       on nkifli3r, boot 45ebdf64, MAP unchanged. AE undervoltage
       condition met by T53c: 0 hits on all 3 boots; rpi_volt =
       hwmon1, in0_lcrit_alarm 0. T54 was mandatory, no re-scope
       (PO). Method
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
    3. AC18a PASS (Architect + QE; corrected expectation: the no-op
       pruned the FAT to one generation, see F-369). AC18b HELD (item
       7). AC18, RE-WORDED to the boot verb (PO, verbatim): "(a)
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
       (Actual: pruned at AC18a; the recovery line is already
       gens/nkifli3r.../.)
    4. OPEN: AC17, two cold power cycles stay (PO). ONE owner request
       for two back-to-back cycles on the FINAL deployed SHA (after
       AC18b; QE; now after T54b, see item 7). The first counts as
       T48 (incl. AE's ps -L). Per boot, no intervention: SSH within
       3 min; new boot_id; readlink
       + configurationRevision; both failed lists empty; kernel log
       scan with per-line disposition; get_throttled 0x0; AC14/#10.
       get_throttled RULED (QE adopts the Architect's tiered
       wording; the sticky since-boot bits 16-19 are the point). No
       vcgencmd on the image. (1) OBSERVE once, before the power
       cycles: /proc/config.gz grep SENSORS_RASPBERRYPI_HWMON and
       BCM_VCIO; `ls -l /dev/vcio`; hwmon names. (2) If /dev/vcio
       exists: ONE CHANGE before the first power cycle copies
       libraspberrypi into the Pi store once (store add only, no
       config or service change, not the audio path). CM tier
       ruling: CHANGE (it modifies state). Conditions: `nix copy --to
       ssh://ela@192.168.178.89` from the Mac with the pinned
       known_hosts; no build or nix shell eval on the Pi; nixpkgs
       revision = the deployed flake.lock; record the store path and
       add a GC root on the Pi (`nix-store --add-root` under the
       user's gcroots) so it survives both cycles; removal after
       AC17 is part of the same CHANGE. The CM schedules (1) and (2)
       after AC18b, right before the owner request, and grants both.
       Each boot runs `sudo vcgencmd get_throttled` from that
       same store path; PASS = 0x0; record the store path and that no
       GC ran between the boots. (3) Else: rpi_volt in0_lcrit_alarm =
       0, no Undervoltage/throttl kernel-log lines (per-line
       disposition), cpuinfo_cur_freq never below max in the sampled
       window; record that short events between samples are not
       visible (not a FAIL). Both branches also record every cpufreq
       cooling_device cur_state = 0 and the SoC temperature. Governor
       is already performance (rt-tuning.nix:33, F-291), so the freq
       check is a valid throttle signal (QE concedes).
    5. AC1a: PASS (Architect) at bbff469e vs origin/main 289390bf:
       the only change is toplevel -> etc -> pipewire-configs ->
       pi4audio-pipewire-configs (+05-rt-direct.conf, store path
       c6ry7vzk...); raw diff ac1a-nixdiff-289390bf-vs-bbff469e.txt
       (worker-1). Pending: re-run on M, same criterion; raw diff
       attached to the PR (QE). DONE: re-run on M PASS (Architect;
       see the AC18b status above). (v59's "DONE at j2ykkiil" was
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
    7. OPEN, US-163 code change: **F-369** High (QE finding; PO
       ruling 2026-10-25 supersedes all earlier positions). The FAT
       keep set {new, prev, booted} collapses to ONE generation after
       any repeat or no-op deploy; after AC18a only nkifli3r is on the
       FAT, x83 is in the store only, so the AC2a one-line SD rollback
       has no second generation. PO: AC2a means ">= 2 complete
       generations on the FAT, always, as soon as >= 2 have ever
       existed" -- it protects operator rollback to an EARLIER
       generation (T54), not only a failed new boot; a booting
       generation can still prove bad later (audio, Mixxx, at the
       gig). QE: no boot risk, but the AC covers more. Fix (PO): the
       prune also keeps the newest other complete generation
       (nix/nixos/boards/pi5/bootloader.nix); the Architect specifies,
       worker-1 implements, usual review. The two earlier Low lines
       (keep the previous profile generation's dir; a bootloader.nix
       header comment on the no-op behaviour) are DROPPED: PO FINAL,
       everything is in US-163, no Low follow-up. AC2a stays ">= 2
       complete generations kept" (PO FINAL, option (B), tie-break;
       Architect + QE voided their earlier positions; objections go
       through the PO). AC2a second clause, PO FINAL wording: "if the
       pointer selects an unbooted generation, the booted one stays
       on the FAT." (Earlier QE wording: "the booted one is always
       among those kept.") QE test-adequacy condition for the fix
       review: an offline check runs the prune step on a fake gens/
       dir plus profile links: (1) the no-op collapse case keeps the
       newest other complete generation; (2) a missing or incomplete
       alt is not recreated; (3) a normal deploy still prunes beyond
       the keep set. SUPERSEDED (CM, 2026-10-25): current fix-review
       conditions. Check file nix/checks/pi5-prune-gens.nix (worker-1,
       in progress). QE accepted worker-1's cases 1-6 and added: (7)
       new=D/prev=C/booted=B -> keeps {B,C,D}; (8) a booted dir with no
       profile link is kept; (9) idempotent re-run; (10) a profiles dir
       with a plain `system` symlink plus a non-matching entry.
       Architect: case A = unbooted pointer (same as QE's 7); explicit
       GNU PATH via lib.makeBinPath in the script (Pi + darwin check);
       an empty prev/booted never matches a stray dir. Evidence: the
       hook and the check use the same prune-gens store path; "N/N
       cases passed"; the check runs in T1/CI; Pi 4 drvPaths unchanged
       and board-guard green. Architect design approval: the MAP.txt
       write moves into the prune-gens script with step 3, accepted
       only if the MAP format and location are unchanged and the test
       asserts MAP content; step 1 (generation build), step 2
       (config.txt pointer write), os_prefix/tryboot handling and the
       gens/<id>/ layout byte-for-byte unchanged in the diff. The
       Architect's review confirms the diff touches
       only prune/retention, not the pointer write, boot selection or
       FAT layout (normal review item; PO).
       F-369 STATUS (CM, 2026-10-25): fix committed at 96b4246c
       (story/US-163). Review record:
       - Architect APPROVE 96b4246c, no changes requested. Item E
         (empty prev/booted) and findutils CLOSED, no action: a
         directory name is never empty; the hook uses only coreutils
         and gnused.
       - QE: cases 1-7, 1b and the negative controls reviewed, fine.
         DROPPED by QE: the same-store-path proof (hook and check both
         import prune-gens.nix) and the non-matching-entry part of
         case 10.
       - Design (unchanged): keep set {new, prev, booted, alt}; alt =
         the highest-numbered system-*-link id != new whose
         gens/<id>/.complete exists; keep only, never recreate
         (Architect). Offline check pi5-prune-gens (pure bash
         runCommand, no VM). Pi 4 drvPaths unchanged, board-guard
         green (Architect item 6); a new Pi 5 toplevel is expected.
       - STILL REQUIRED in worker-1's follow-up commit (via CM): (i) a
         CI step building checks.x86_64-linux.pi5-prune-gens (the
         gating item); (ii) an "N/N cases passed" line; (iii) case 8:
         a booted gen with no profile link is kept; (iv) case 9:
         idempotence (a second run changes nothing), plus a plain
         `system` symlink in setup(). QE accepts on a local log with a
         non-zero count; CI confirms on the PR.
       - DONE in b9e8974e (CM): (i) CI step for
         checks.x86_64-linux.pi5-prune-gens; (ii) "13/13 cases
         passed"; new cases 8 (unlinked booted), 9 (idempotence; plain
         `system` link in every fake profile), 10 (system /
         system-foo / system-foo-link; the MAP loop skips non-numeric
         entries), 11 (empty prev/booted). The check runs the hook's
         exact script (system.build.pi5PruneGens); board-guard
         (107/107) asserts the hook calls that store path.
       - Architect APPROVE b9e8974e, no changes: tested text =
         deployed text; the MAP-loop change touches only non-numeric
         entries, F-369 scope holds. QE ACCEPTED 96b4246c + b9e8974e
         (test adequacy). OPEN for the PR review: the CI log shows
         pi5-prune-gens "13/13 cases passed" (QE).
       AC18b/AC18c/T54b PASS CRITERIA (joint Architect + QE ruling,
       FINAL; N = nkifli3r, M = the deployed head, which must contain
       96b4246c):
       - Precondition: {N} only, pointer at N, x83 pruned (left by
         AC18a under the old hook). This is F-369 as observed: a
         precondition, not a new defect.
       - Steps: (a) deploy M -> {M, N}, pointer at M; (b) reboot ->
         unchanged, booted M; (c) AC18c no-op redeploy -> {M, N}, no
         new profile link; (d) T54b step 1, rollback via
         switch-generation k -> pointer at N, booted N after the
         reboot; (e) T54b step 2, switch-generation k+1 -> pointer at
         M, booted M after the reboot. A fresh deploy of M in (e) also
         PASSES (links k+1 and k+2 both point to M).
       - At every step (a)-(e): exactly 2 complete generations (M and
         N), the booted generation and the os_prefix target among
         them, no gens/*.tmp. 1 generation or a missing .complete =
         FAIL and STOP.
       - Count levels (QE, 2026-10-25: "both, at different levels"):
         in the DEPLOY grant (AC18b/AC18c/T54b, steps (a)-(e)) the
         pass criterion is EXACTLY gens = {M, N}, both .complete; any
         other count or any other id FAILS. AC2a and AC18c as general
         story ACs keep ">= 2, booted among them".
       - (c) is the F-369 regression proof.
       - Restriction: no no-op deploy while N is active (N's old hook
         would collapse the FAT to 1 generation).
       - Evidence at each step (QE; part of the DEPLOY grant):
         ls -la gens/*/; the config.txt os_prefix line; MAP.txt;
         readlink /run/booted-system; ls -l
         /nix/var/nix/profiles/system*.
       - worker-1's item 5 (1 generation after a no-op deploy) is a
         misreading, not a new defect.
       New **AC18c** (PO): "A no-op
       redeploy (boot at the same SHA) leaves >= 2 complete
       generations on the FAT, and the booted generation is among
       them." QE AC18b criteria: (i) MAP shows >= 2 present (M +
       nkifli3r) after the deploy and after the reboot; (ii) AC18c on
       the fixed head still leaves >= 2. [SUPERSEDED by the exact
       {M, N} criterion for this run (QE, 2026-10-25).] Sequence (PO;
       CM sequences):
       fix deploy -> AC18b + AC18c in one run (saves reboots); T54
       runs on the fixed state (PO). RESOLVED as **T54b** (QE; PO
       adopts it, withdrawing "no re-run unless the Architect finds
       X"): AC18c proves presence, not a usable rollback target. On M
       after AC18c, before AC17, same DEPLOY session if practical:
       (1) roll back to nkifli3r (profile switch +
       switch-to-configuration boot), reboot once; PASS booted =
       current = nkifli3r; (2) switch back to M, reboot; PASS T51
       identity = M, #10 (gains), gate closed, MAP/gens/ >= 2 complete
       with M booted. No second "survives reboot" leg. Reboots
       announce-only. T54 (12:34-12:41Z) stays ACCEPTED; T54b is
       additional. bootloader.nix changes, so
       AC18b/AC17 run on the fixed head (QE); the US-163 delta is no
       longer docs-only after the fix (QE condition (d)). Not an owner
       topic (PO). Superseded: Architect "per spec, optional Low" and
       the relayed "PO amends AC2a to except after a no-op deploy".
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
  - THERMAL RULE (AE + Architect; re-worded 2026-10-25, replaces v62's
    "cpu0 scaling_cur_freq" wording) for every Pi 5 load run.
    Precondition (read-only): scaling_governor = performance on all
    cores (production default, rt-tuning.nix:33, F-291); a mismatch is a
    finding, a deploy defect; nobody sets it by hand (AE). Live
    evidence: postboot-T48-50-link-798f2dc7, cpu0 performance
    2400000/2400000 at idle (AE). Sample every 10 s: thermal_zone0, cpu0
    cpuinfo_cur_freq (root; actual clock from firmware, not
    scaling_cur_freq), every cpufreq cooling_device cur_state, the
    rpi_volt undervoltage alarm (path found in T53c:
    /sys/class/hwmon/hwmon1/in0_lcrit_alarm; match on name rpi_volt, the
    hwmon index can change). The sampler runs as root (sudo):
    cpuinfo_cur_freq is root-readable only (worker-1). T54 (AE): T54
    PASS stands, cooling_device recorded as "not sampled" (the sampler
    matched none). Sampler fix is a CONDITION of the AC18b grant:
    cooling_device inventory, rpi_volt by name, labelled fields, the
    cooling_device criterion N/A if no cpufreq-type device exists.
    worker-1 confirms on the Pi that cpuinfo_cur_freq and
    scaling_cur_freq agree at idle. WARN at >= 75 C: report to the owner
    via team-lead, keep running. STOP at >= 80 C (Pi 5 firmware throttle
    onset; full throttle at 85 C). The run's CPU/xrun evidence is
    INVALID, and the run is repeated, if at any sample: any
    cooling_device cur_state != 0; the undervoltage alarm is set; or
    cpuinfo_cur_freq < cpuinfo_max_freq (AE: the firmware can cap the
    clock at the soft limit without a Linux cooling_device showing it).
    Invalidation is a finding, not a STOP (Architect). No builds on the
    Pi; all builds stay on the Mac VM (Architect). Gig cooling: see the
    P1 Pi 5 thermal soak item.
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

- **AMPS-ON PRECONDITION LIST (Pi 5)** (PO, 2026-10-25; the single
  consolidated list). Gates ANY amps, HP or IEM use of the Pi 5. Every
  item must hold; each links to its own entry:
  1. Owner re-confirmation plus the S-012/safety.md pre-flight.
  2. F-341 AC3 PASS on the Pi 5. Until then also NO signal-gen
     measurement session on the Pi 5 (AE, PO).
  3. US-172 condition: HiFiBerry layer (a) restored, or the AE
     re-rules (P1 US-172 GATE; layer deviation accepted only while
     nothing is connected).
  4. US-170 A1 item (QE): the Pi 4 AC13 A1 precondition before
     amps-on (Pi 4 runtime unverified); F-358 runtime verification
     before any Pi 4 audio use (AE), including "no SIGKILL at startup
     with production coefficients" (AD L1).
  5. F2: pcm-bridge/level-bridge PW nodes back after a PW restart
     (P1 below), or the INTERIM RULE (restart both bridges, confirm
     live meters).
  6. F-037/AC20: the open 8080 web UI is accepted only while nothing
     is connected.
  7. F-361 link-audit fix (P1 below: "before any amps-on use").
  8. F-373 fixed and re-tested with a physical replug (AE ruling,
     PO, 2026-10-25; replaces "usbstreamer-volume-replug (AC17-B)
     PASS", which is deferred to F-373). A volume rise after the
     replug makes G16 High and an amps-on blocker (US-159).
  9. The AC20 open blockers for amps-on / gig use: F-317, F-318,
     F-352, F-354, F-355 (F-358 resolved on the Pi 5; Pi 4 US-170).
  10. The 60-min flight-case thermal soak (GIG-READINESS entry, P1)
     PASS (AE: amps-on too, not only gig).
  11. F-372 (P1 below): the S-001 path check fix.
  12. RTTIME soft = hard (AD L1): an overrun SIGKILLs PipeWire with
     no SIGXCPU stage, which interrupts the USBStreamer and needs the
     F2 procedure. Documented in safety.md before amps-on.
  13. F-373 (P1 below): the USBStreamer sink recovery after USB
     re-enumeration, defined under US-159 G16 and tested (AE).
  Related UX item (not a precondition): a persistent web UI banner
  "DEV IMAGE -- not gig-capable. Amps, HP and IEM off." while any
  item here is open, driven by a build or config flag (UX).
  Revisit before amps-on (not blocks): host key on console (P3,
  MANDATORY before gig/amps-on); ela PAM rtprio/memlock (P3); nix
  advisory version (P3); fail-closed allowlist + US-170 parity
  (postponed security, P3).
  Already PASS: AE AC13 A1-A4 on the Pi 5 (RT side lifted).
- **F-341** signal-gen pre-flight #6 replacement. MEDIUM (AE):
  pre-flight #6 only VERIFIES the -20 dBFS signal-gen cap, which stays
  enforced in code and immutable after start; it would be High if an
  unverified substitute were improvised. AC3 (made precise, PO): "AC3
  verifies on the Pi 5 the exact replacement command that goes into
  safety.md (not an equivalent). Until then: don't improvise, don't
  proceed." No improvised netcat variants (AE). Out of US-163 (FINAL
  (b)); a hard gate on the AMPS-ON PRECONDITION LIST (Pi 5).

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
- US-172 AC (AD L2): WirePlumber rule 54 has no on-device effect
  evidence yet; add a positive HDMI-audio-disabled check.
- Pi 4 has no WP card-block rule (54-disable-other-alsa-cards is Pi 5
  only). Pre-existing; Pi 4 follow-up with US-170. (AE)
- APC mini is ALSA card 0 and WP rule 54 disables its WP device:
  fine for audio; at the first Mixxx session confirm the MIDI
  controllers still reach Mixxx (rawmidi/seq). (AE)
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
  - (PO, new AC) "D-022 re-confirmed on the Pi 5: /dev/dri/card*
    present, labwc/greetd running, Mixxx with hardware GL (no
    llvmpipe)."
  - (Architect) /dev/dri root cause: likely F-367 (no overlay applied,
    so the GPU nodes are not okay and the modules have nothing to
    bind), not yet shown on nkifli3r. OBSERVE DROPPED (Architect):
    the 798f2dc7 disabled-node read plus the same symptom on nkifli3r
    (overlay line present, no /dev/dri) put it in the F-367 branch; no
    new F. US-172 re-reads the live DT as its own fix evidence (PO
    condition). Original request: one OBSERVE via the CM: status
    and compatible of the v3d and vc4 (hvs/hdmi/kms) nodes under
    /proc/device-tree, plus lsmod | grep -E 'v3d|vc4'. Disabled or
    absent: covered by F-367. Okay but modules not loaded: a separate
    F-item (autoload/blacklist) under US-172. Filing only, not
    merge-relevant.
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
  SecSpec: security-relevant; fix AC = S-001 and D-009 tests run and
  pass in CI; guard must fail, not skip. The skip silences
  TestDeployPathTraversal (S-001 regression) and the D-009 interlock
  tests on deploy/rollback, which guard an unauthenticated LAN
  endpoint (F-037). Root cause (SecSpec reading): the import asks for
  `_PROFILES_DIR`, which filter_routes.py no longer defines (now
  `_profiles_dir()` at :54), so the ImportError is permanent. Rating
  stays High. Must be defined in the PR #50 body (AD M1).
  AE domain rating (2026-10-25): Medium; fix before the next filter
  deploy via the UI; the guard must fail loudly. The record rating
  stays High (QE, SecSpec). One item (PM ruling): QE's "1 skipped"
  is this guard.
- **F-373** (AE; availability HIGH, safety-relevant; amps-on item
  13; linked US-159 G16): the USBStreamer sink does not recover after
  USB re-enumeration. AC17-B step (a), CM-CHG-.89-5: authorized 0->1
  left sink node id 33 "running" on a dead PCM; spa.alsa
  "hw:USBStreamer,0p: No such device" from 13:46:33Z; no reopen
  after authorized 1 at 13:46:38Z; hw Playback Channel Map all 0.
  Raw: ~/mugge-pi5-prewipe-20261024/
  ac17-B-replug-a-20261025T134631Z.txt (sha 455610c2...). Likely
  cause: a static pipewire.conf.d adapter with no hotplug path; only
  a PW restart recovers it, which also kills the meters (F2). Safety:
  a self-recovery would resume programme at full gain, not Mult 0.
  Required behaviour (G16/US-159): every recovery goes through the
  D-063 gate (gains 0, then a deliberate ramp), or no self-recovery
  and an operator-initiated restart only. Not a US-163 blocker (AC17
  step (a) PASSED). Step (b) shows whether a power-cycled device
  behaves the same way. Record: B3 v2. Step (b) is DEFERRED here
  (AE + QE ruling, PO): the F-373 fix acceptance includes a physical
  replug with the AE's step-(b) read set, before and after: the node
  list (new nodes), the USB devnum, the kernel log, spa.alsa errors,
  the gains, the gate state and the hw mixer. Re-open trigger as in
  the AC17 Session B entry. AMPS-ON items 8 and 13. Current interim
  recovery procedure (AE; verified in AC17-B step (c), 5aad9083): a
  PW restart plus a bridge restart recovers the zombie sink with the
  16 gains at exactly 0 and the gate closed. That is today's manual
  workaround, not the fix. AC (AE, verbatim; the safety shape, not
  the mechanism): "After a USBStreamer re-enumeration (software and
  physical replug), the sink recovers by whatever route the fix
  chooses. At the moment audio can flow again, all 16 gains are
  exactly 0 and the gate is closed (D-063); levels return only
  through a deliberate gate open/ramp. Meters recover (F2). There is
  never an abrupt resume at the previous gain."
- **F-372** (SecSpec, MEDIUM; amps-on/gig blocker class next to
  F-037): the S-001 fix is weak. filter_routes.py:545 tests
  abspath(output_dir).startswith(abspath(DEFAULT_OUTPUT_DIR)), a
  string prefix, so a sibling (<RC>/output-x, <RC>/output2) passes;
  req.profile goes unsanitised into os.path.join for output_dir
  (:244) and session_dir (:226) (partly limited: the profile must
  load first). Impact: integrity; an unauthenticated LAN client could
  deploy combined_*.wav from outside the output tree to
  /etc/pi4audio/coeffs; D-009 verification still caps gain. Fix:
  realpath + os.path.commonpath (or Path.is_relative_to), an
  allowlist pattern for the profile name, and tests that actually run
  (depends on F-362). No owner escalation (home lab rule).
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
  1024, Mixxx + convolver, amps off, production performance
  governor, sampling every 10 s (signals per the thermal rule, US-163
  section). PASS = max < 75 C, none of the three invalidation
  signals (cooling_device cur_state != 0, undervoltage alarm,
  cpuinfo_cur_freq < max), 0 xruns, ambient recorded (margin noted
  for warm venues). FAIL: add active cooling (or a case vent design)
  and re-run. Links to the flight-case ventilation TODO.

## P2

- **F-370** (QE, Low; RULED by the Architect: Low, P2, not a merge
  blocker; not US-163 scope): the Pi 5 hook rewrites config.txt and
  MAP.txt on a no-op deploy with identical content (seen in
  CM-DEP-.89-3 (c)). Fix: skip the rewrite when the content is
  identical (cmp -s before mv). Reason: every rewrite reopens the
  accepted vfat power-loss window (bootloader.nix step 2), not wear.
- Current state (AE ruling 2026-10-25): PW main thread AND
  data-loop.0 run at SCHED_FIFO 88 (verified on 2 cold boots); the
  item below is the proposed change, not the current state.
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
  addresses. Not an owner question; not US-163. Low. CM (T53): no
  stable-privacy addressing in use; options are stable-privacy
  addresses or disabling IPv6.
- Web UI listens on IPv4 only (web-ui.nix `--host 0.0.0.0`), so 8080
  is not reachable over IPv6 (CM, T53). Decide whether IPv6 listening
  is wanted. T53 passes either way ([::] optional). Not US-163. Low.
- .89 docs batch additions (PR #50 review): B2 nixos-upgrade.md Pi 5
  section (TW); "Image status (AC20)" names the thermal soak and the
  P2 "PW main thread back to SCHED_OTHER" among the gig blockers, or
  points to their backlog entries (Architect nit); safety.md gets the
  RTTIME SIGKILL note (AD L1); pi5/default.nix comment .88 -> .89
  (AE; already the worker-1 item above).
- .89 docs batch (CM): the flake.nix comment on mugge-pi5-deploy still
  says "built natively on the Pi ... nixos-rebuild switch"; the real
  route is the Mac `nixos-rebuild boot --no-reexec`. Low.
- **F-363** Purifi Qts test is order-dependent (`iterdir()[:20]`).
  AE rating (2026-10-25): Low while no venue config uses this
  driver; Medium if one does (the T/S data feeds the D-031 design).
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

- development.md, ONE docs item (TW offers to write it; merges UX,
  QE, Arch N2, AD L2, TW F1-F3): run `nix build
  .#checks.<system>.app-source-paths` locally (test-all no longer
  includes the guard; it runs in CI only); the apps run from a store
  snapshot of the tracked tree, so new files must be git-added first;
  the CI section 7.2 pin and guard text; the PytestCacheWarning note.
- Low (QE, #49): `cat` the guard's out path in the CI step so the
  "Checked N app scripts" count shows in the log. (QE follow-up 1 on
  the #49 APPROVE; same item.)
- Low (QE follow-up 2 on #49): dev-howto note: `nix run .#test-*`
  doesn't pick up unstaged new test files, because the apps run on
  the store copy of the tracked files. (TW)
- AD L1 (#49): the lint only catches `toString ./.` and `toString
  self`, and the closure check covers apps only: widen the lint or
  document the limit.
- AD L3 (#49; SecSpec): `cachix watch-exec` pushes the full tracked
  tree (.claude/, the lab notes) into mugge.cachix. Confirm the
  cache's visibility is no wider than the repo's.
- AD L4 / Arch N3 (#49; SecSpec): install-nix-action is pinned to an
  untagged master commit. Move it to the next tag, or decide whether
  the v31.11.2 tag is enough.
- Low (worker-1): nixos-anywhere 1.13.0 puts its own
  `-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no`
  before our --ssh-option values; OpenSSH takes the first value, so
  the host-key pin on the RAM-installer hop was likely not in effect
  (7 "Permanently added" lines in install-fb7d557e.log). That hop was
  TOFU, within the ruling; the final host has been pinned with
  StrictHostKeyChecking=yes since 19:00Z. Untested whether an earlier
  `-o` wins: whoever does the next nixos-anywhere install checks it.
- Low (worker-1): nix/nixos: ela has no per-user GC-root dir on NixOS
  (/nix/var/nix/gcroots/per-user/ela is missing and ela can't create
  it), so `nix-store --add-root` under per-user fails. Ad-hoc tool
  copies are unrooted (CM: accepted deviation for AC17). Fix: create
  the dir via systemd.tmpfiles, or root under ~ with --out-link. Not
  a US-163 blocker.

- **F-371** (worker-1, AC11 side finding; Low): the mugge-pi5-deploy
  closure (2wf21ydg) contains the full nixpkgs source (8ggk1060, rev
  812b3986; presumably via nix.registry/NIX_PATH), which ships 25
  public upstream snakeoil/test private keys (e.g.
  nixos/modules/profiles/keys/ssh_host_ed25519_key). Harmless; adds
  closure size and false positives to every key grep. Option: the
  registry flake by reference, drop the source from the closure.
  Evidence: ~/mugge-pi5-prewipe-20261024/
  ac11-closure-privkey-grep-2wf21ydg.txt.
- Mark the board-guard file-only assertions as file-only (they check
  config files, not on-device effect). (AD L3)
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
  hardware_routes.py:120). Low. (worker-2) Same item as Arch #49 N1
  and the AE local-demo note: the fix is one `chmod -R u+w` line; not
  folded into #49 (a code commit would void the approvals). AD (a):
  most likely pre-existing (the store copy was read-only on Nix 2.34
  and earlier too).
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
  avahi) -- pick one. Seen again in T53 on the deploy: 5355 listens,
  nft drops it (SecSpec accepted the disposition). No new item.
- systemd RebootWatchdogUSec=10min (default) arms the watchdog during
  reboots. Does O-24 cover it? Architect/AE to rule. P3 (worker-1).
- sshd AllowAgentForwarding yes (default) on the Pi 5. LOW, SecSpec to
  decide (worker-1).
- Pi 5 WiFi/BT firmware missing (brcmfmac, BCM4345C0). Note: wlan0 was
  the fallback path during the 20:13 eth0 drop (P2 item), so NixOS
  currently has no wireless fallback. P3 (worker-1).
- No vcgencmd on the Pi 5 image, so no get_throttled evidence for T50
  and gig thermal checks. P3 (worker-1). Fix (Architect): add
  `libraspberrypi` (in pinned nixpkgs, evaluates for aarch64-linux;
  needs /dev/vcio) to the Pi 5 system packages. Not US-163.
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
  fresh round and green T1-T3. QE APPROVES #49 on 3 conditions: CI
  green at 316cc3eb with the guard checking 18 scripts; a local
  revert proof; T3 addressed. NOW ON THE US-163 CRITICAL PATH (PO,
  2026-10-25): #50's test-and-build fails on F-335, so #49 lands
  first, limited to F-335 (no scope additions). CM holds the push
  until worker-2 reports.
  Pushed (CM): head 316cc3eb = b959e5c9 + merge of main 289390bf
  (docs-only, no overlap), up to date with main. All 7 APPROVE at
  316cc3eb: UX 6398401666, AE 6398401922 (no veto), QE 6398402123
  (C1 CI green with "Checked 18 app scripts", C2 local negative
  control, C3 T3 status explicit), SecSpec 6398402382 (no veto), AD
  6398415695, Architect 6398416014, TW 6398427590 (C1). TW C1 and
  AD M1 resolved by body v2 (6398461001, 6398461280). Open: CI run
  40198678554 (QE C1), QE C2 (worker-2), the owner's T3 ruling (QE
  C3, via team-lead), owner acceptance. Next body touch (worker-2):
  AD (a) F-364 "most likely pre-existing"; TW N1 "No other job uses
  GITHUB_TOKEN" is imprecise (actions/checkout uses it by default).
  CI run 40198678554 at 316cc3eb GREEN, counts identical to
  df4a6a9b. QE C1 MET (6399369458): "Checked 18 app scripts" read
  from the signed cachix output of the CI guard derivation (it is in
  $out, not in the log). T3 run 40205694612 (release.yml,
  dispatched by the owner at 316cc3eb) GREEN (CM): artifact
  sd-card-image ~1.04 GB, digest 7a9ae2ce...; verify-ci skipped by
  design (tag-only). QE APPROVED at 316cc3eb, C1/C2/C3 MET (comment
  6399540510). All 7 approvals at the head, CI green, GitHub CLEAN.
  Owner merge consent requested via team-lead.
- #50 US-163: open; see the US-163 section (PR #50 block).
- #43, #45, #44: need #49 on main and real green CI; #45 before #44.
- #36, #40: no Rule 13 review; owner direction needed (#40 IDs clash).
- chore/backlog (this file): no PR yet; docs-only.
