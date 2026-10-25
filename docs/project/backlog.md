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
US-173 (P1, supervised home-lab first DJ session); D-070
(supervised home-lab first-session exception, ACCEPTED by the owner
2026-10-25, PO; see US-173). US-174 (P1 epic, automated room
correction pipeline; PM checked free across main, origin and all
local/worktree branches, 2026-10-25).
F-374 (P1, LR4 crossover defect); US-175 (P1, F-318 layer 2, GM
link enforcement); F-375, F-376 (P3). F-377 and F-378 WITHDRAWN,
never to be reused: F-377 (Mac disk, worker-2) duplicates the
existing P3 "Mac disk nearly full" item; F-378 (purifi Qts test,
worker-4) duplicates F-363. Both updates are merged into those
items.
F-379 (P2, web-UI correction level defect); F-380 (P2, CI builds no
checks.*); F-381 (P3, driver datasheet_file paths); F-382 (P3,
deploy-src git export ref); F-383 (P1, combine destroys LR8
phase); F-384 (P1, correction.py step 9 re-clip); F-385 (P1, D-031
subsonic vs crossover phase; PM checked free across main, origin
and all worktrees, 2026-10-25); F-386 (P2, gain values read from
pw-dump; PM checked free across main, origin and all worktrees,
2026-10-25); F-387 (Low, web-ui teardown flake; QE N2 on #55; PM
checked free across main, origin and all worktrees, 2026-10-25);
F-388 (P2, Xmax definition in the excursion mask; AE; PM checked
free across main, origin and all worktrees, 2026-10-25); F-389
(US-172 tryboot hang, Architect; PM checked free across main,
origin and all worktrees, 2026-10-25).
Next free: F-390, US-176, D-071, T66.
FINAL (PO, 2026-10-25; supersedes the v87 PROVISIONAL block): the
owner says GPU acceleration is a prerequisite (Wayland doesn't start
without it), and ruled, verbatim: "Separate PR is fine. Just make
sure you keep the momentum going, and don't block asking me for some
minor details." US-172 is HIGH and the active job directly after
US-163; #50 stays headless, scope and acceptance unchanged. One
exception: if the Architect reports a small bug in our own boot hook
BEFORE the #50 head move, that fix rides in the same head move with
the /dev/dri AC. Read-only diagnosis runs now in parallel
(CM-OBS-.89-DRM1, worker-2, for the Architect) as US-172 groundwork.
Recorded in B3 v7/v8 (US-172.md, stories index row).

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
      path is not exercised; that is scope. QE: AC17 ACCEPTED, both
      cold cycles (#50 comment 6399566294). The gate is identical to
      the step-(a) BEFORE (33e73516), which also covers the cold
      re-check of AC12a; amixer byte-identical (29d42498); gens
      snapshot correct (os_prefix 2wf21ydg; MAP 3 nkifli3r and 4
      2wf21ydg present, 1 and 2 pruned). Recorded in B3 v7/v8.
    - RULED (AE, verbatim): "Current: PW main thread and data-loop.0
      both SCHED_FIFO 88 (main thread via F-020 unit, data loop via
      module-rt / 05-rt-direct.conf), verified on 2 cold boots.
      Backlog P2 (not US-163): return the main thread to SCHED_OTHER
      so only the data loop runs at 88." The Architect owns the P2
      design. Any image-status note listing the main thread as
      SCHED_OTHER misreads P2 as the current state and is corrected
      (the owning author; not in B3, PM checked). Arch + AE joint
      image-status line: "PW main thread: FF/88 now (F-020,
      process-wide); target SCHED_OTHER (P2, backlog)". Routed to
      worker-1 for the #50 body (CM). The Architect's AC17 item is
      closed and their #50 approval stands. B3 v7 adds the current
      state to US-163 AC13.
    - AC19 FINAL (PO, RECONCILED; joint QE and PO; AE no veto;
      replaces every earlier AC19 text; verbatim in B3 v8
      US-163.md): after the merge, boot from the merged main SHA,
      an announced warm reboot, then the AC17 read set against the
      step-(a) BEFORE values. Two owner cold cycles only if the
      nix-diff from 2wf21ydg to the main toplevel touches (a) the
      boot chain, (b) the audio device path, (c) audio startup,
      (d) gain defaults or (e) anything that sets the USBStreamer hw
      volume; always if that volume is ever set below 0 dB. QE rules
      from the diff plus the head-move proof. AE sentence: any kernel
      version change, USB/audio driver or firmware change, or
      persisted hw mixer below 0 dB counts under (a)/(b); a Pi 5
      EEPROM/bootloader update is a cold trigger regardless of the
      nix-diff. QE read-set addition (non-blocking): vcgencmd
      bootloader_version and bootloader_config after the redeploy
      (full libraspberrypi store path) vs the baseline the CM takes
      in CM-OBS-.89-DRM1 (output sha to be recorded); identical =
      no EEPROM trigger. Owner line (PO): "No more power-cable pulls
      are needed after the merge; a software restart is enough
      unless the startup or volume code changes." Team-lead has told
      the owner, so no PM owner correction is needed.
    - OPERATIONAL (QE, CM): no EEPROM update on the Pi 5 between the
      AC17 cold cycles and AC19 without telling QE and the AE.
    - B3 v7 (PM, 2026-10-25; supersedes v6): US-163 AC13 current
      state, AC17 PASS, AC19 (interim text); US-172 High; stories
      index US-172 row; status.md. MANIFEST.txt sha 3d733bea...;
      superseded by v8 before commit.
    - B3 v8 (PM, 2026-10-25; supersedes v7): US-163 AC19 = the
      reconciled final text plus the AE sentence and the QE read-set
      addition; US-172 /dev/dri AC is AC1 (former AC1-AC8 now
      AC2-AC9), AC10 desktop with or without HDMI, including
      hot-plug. MANIFEST.txt sha 1dffcaa9...; v7 kept as
      MANIFEST-v7-superseded.txt. Cumulative vs v6: US-163.md,
      US-172.md, stories-index.md, status.md. The CM commits v8 last
      in the head move (worker-1: merge main 45593097 and TW
      9a7e9562, nix-diff proof, then B3 v8 and the lab notes).
    - B3 v9 (PM, 2026-10-25; supersedes v8; v8's US-172 changes
      kept): US-163 AC19 only. QE's EEPROM trigger rule replaces
      "output sha recorded by the CM". Baseline: CM-OBS-.89-DRM1,
      ~/mugge-pi5-prewipe-20261024/drm-observe-20261025T153439Z.txt
      sha256
      4d7b6864071ea88cc8b753a009336593a4f972ba7b310bdfc5af656e42e87cf6
      (section 10; script 4c329c1f). Cold trigger (QE) if the
      bootloader_version hash differs from
      000d3ca289ae790a2e46225eb11b319c67642b1a,
      or the timestamp differs from 1756339608, or the
      bootloader_config sha256 differs from
      916ce18ae8ae88dc5db54cb8cc50f493c51cdd59ae2a7ac2b6259ad9203940e1.
      PM checked all three values against the file (lines 89, 90,
      102). QE accepted the baseline as the AC19
      reference. MANIFEST.txt sha 6bf75232...; v8 kept as
      MANIFEST-v8-superseded.txt. The B3 commit uses v9.
    - Head-move prep (CM): worker-1 done locally at 7e507948,
      nothing pushed yet. nix-diff against 2wf21ydg shows only
      configurationRevision; the Pi 4 is still j2ykkiil.
    - CM-OBS-.89-DRM1 CLOSED 15:36:05Z, read-only. Outputs:
      drm-observe 4d7b6864 (script 4c329c1f), s5 9868a2fc (script
      2d67c46b), s1011 3fd2c3c3 (script ea07e490, identical to the
      pre-approved text). Finding: all display DT nodes disabled;
      the FAT root has no overlays/. Diagnosis with the Architect;
      goes to US-172 (no ride-in, see below).
    - CONDITIONAL ride-in DROPPED (PO, 2026-10-25): the window closed
      with worker-1's B3 v9 commit; the Architect could not confirm
      the config.txt ordering bug without a test boot. Dropped: the
      US-163 /dev/dri AC, greetd explicitly disabled, the AC17 repeat
      (2 owner cold cycles). #50 ships headless as documented; the
      owner line "no more power-cable pulls after the merge" stays
      valid, no note needed. The Architect's #50 approval is
      unaffected. The fix goes to US-172 (starter set there).
    - Review round at df807900 (2026-10-25; ALL LAPSED by the head
      move to 22370317, re-review requested): SecSpec APPROVE
      6399790617; Architect APPROVE 6399796811; AE APPROVE 6399797048
      (AC19: no cold trigger in the nix-diff, warm reboot enough, on
      condition the nix-diff is re-run if main moves past 45593097
      before the merge; AC12a "PASS (2 layers)" accepted; non-blocking
      table cell "while nothing is connected to the HAT; US-172"); UX
      APPROVED with a must-fix 6399797327 (safety.md "Pi 5 Platform
      Status" listed 8 of 13 amps-on items; afbc04ae recovery-line
      note fixed); AD APPROVE 6399805948 (M1, M2, L1, L2, L3 resolved;
      L4 stays backlog; not covered: CI, post-merge AC19, any later
      head); QE verified block 6399806200 (APPROVE pending CI, T3
      proof, line edits); TW CHANGES REQUESTED 6399817933 (one
      safety.md blocker, fixed on the TW branch, 28dcba6e).
    - AD ruling (via CM): AD M3 (CLAUDE.md boot-gain contradiction,
      line 408 vs the 462 quick reference) and L5 (CLAUDE.md "Current
      Mission" still Pi 4 / V3D GL) ride in this docs move (TW text,
      AE confirms wording), plus safety.md 458-459 aligned. PM read
      at 22370317: TW 28dcba6e "Pi 5 CLAUDE.md fixes" changes both
      places; the reviewers judge them.
    - QE T3 (via CM, verbatim): "QE: I've verified the image nix-diff
      myself. sha ab5b35bb… matches. The derivation chain is exactly
      the 6 nodes you listed. The only leaf is the input source "+
      05-rt-direct.conf" in pi4audio-pipewire-configs. I masked the
      store hashes in the --environment part and compared all 9
      changed pairs. None differ. This is consistent with the Pi 4
      toplevel staying j2ykkiil since f0fbefd1: 316cc3eb is from
      before AC1a. T3 plan confirmed. Once the owner's dispatch is
      green with an image artifact, and the final head has
      images.sd-card drvPath == r4hqi43b…, T3 is met for me."
    - B3 v10 (PM; on v9): US-163.md only (057787f1...): QE's AC17
      wording correction (AC12a cold re-check covered by the AFTER
      /proc/asound/cards and PW node reads; module state not read
      cold) and the AC19 read-set addition `lsmod | grep -iE
      'hifiberry|pcm512'` (expect empty). MANIFEST 801336d1...; never
      landed (single head move, CM).
    - B3 v11 (PM; v10 + D-069.md ad218bbe...): TW S1, D-069 "Impact"
      bullet 1 records the Pi 5 sections in rt-audio-stack.md and
      CLAUDE.md as done in #50 (Architect OK; headings at
      rt-audio-stack.md:196/:367, CLAUDE.md:384). MANIFEST
      c8658c6c...; v10 kept as MANIFEST-v10-superseded.txt. CM
      verified 26/26. PM read: both files at 22370317 match v11.
    - Ruling (team-lead, 2026-10-25): the standing merge permission
      covers #50's CLAUDE.md changes (the owner's words have no
      exception; team-lead told the owner that merging #50 adopts
      D-069 and the CLAUDE.md edits and offered to show them; the
      owner did not ask). The Architect's "accepted once the owner
      accepts #50" is met by the CM merge under the standing
      permission; team-lead reports the merge and the CLAUDE.md
      change to the owner afterwards.
    - HEAD MOVE (CM, docs-only, pushed by SHA, ls-remote verified):
      22370317d461a0008f1bc619319d88b77058b548 = db375821 (merge of
      TW 28dcba6e) + 22370317 (B3 v11). Body applied (sha256
      93eee073). Proofs: comment 6399926788; bundle
      /tmp/pr50-review-22370317/ (SHA256SUMS 0120a6b1). Rule (d)
      holds: configurationRevision only, Pi 4 j2ykkiil, sd-card
      r4hqi43b unchanged. Main still 45593097. CI run 40210023435 in
      progress (the df807900 run was cancelled by the push). Owner's
      release.yml run pending via team-lead (release dispatch is the
      owner's, not covered by the standing permission). All 7
      re-review at 22370317.
    - Re-review at 22370317 (posted verbatim by the CM): SecSpec
      APPROVE 6399942686 (conditions: a re-review for any non-docs
      commit after 22370317; no failed CI job beyond the known F-363
      at the final head, run 40210023435 counts; CM: Q2 still
      applies, so an F-363 failure blocks too and gets a rerun); AE
      APPROVE 6399947753 (no veto; re-run condition met, main still
      45593097; after the merge a warm reboot plus QE's EEPROM read
      is enough; assumes CI 40210023435 green, QE's call); UX
      APPROVED 6399948019 (df807900 notes 1 and 2 resolved; note 3
      on the backlog with F-373); Architect APPROVE 6399948245 (#49
      N1-N3 unchanged); TW APPROVED 6399960981 (B1, S1, N1, N3
      resolved; N2 to the backlog, US-172); AD APPROVE 6399961232
      (M3, L5 resolved; L6 with F-373; M4 to the backlog, amps-on
      item 14; not covering CI, AC19 or any later head). Tally 6/7;
      QE open (needs CI and T3).
    - CI and T3 (CM): CI 40210023435 green; the owner's release run
      40226857537 GREEN with the sd-card-image artifact. Only the QE
      verdict is open (6/7).
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
  consolidated list). Gates ANY amps, HP or IEM use of the Pi 5. Each
  item links to its own entry. Lead-in (AE-final, verbatim, safety.md
  1472206a on docs/US-163-postmerge): "The list has 14 rows. On the
  Pi 5, rows 1-3 and 5-14 must ALL hold; row 4 applies to the Pi 4
  only."
  SUPERSEDED by the #51 text (TW, commit 2d22aa7a, AE+AD final;
  Architect R1 / AD L1 / UX (a)), lead-in verbatim: "The list has 14
  rows. On the Pi 5, rows 1-3 and 5-14 must ALL hold; row 4 applies
  to the Pi 4 only. For a defect row, "holds" means the defect is
  closed and its fix verified on the Pi 5, unless the row itself
  names an alternative (row 14)." Gate rule verbatim (AD L2): "Do
  not open it while any Pi 5 row (1-3, 5-14) of the list above is
  open." Re-check both against the pushed #51 head (CM bundle).
  DONE: #51 MERGED (main b0666c02); the PM checked the merged
  safety.md on main: the lead-in, the Gate rule, row 4 and row 14
  match the texts here verbatim. Mirror source is now safety.md on
  main b0666c02.
  1. Owner re-confirmation plus the S-012/safety.md pre-flight.
  2. F-341 AC3 PASS on the Pi 5. Until then also NO signal-gen
     measurement session on the Pi 5 (AE, PO).
  3. US-172 condition: HiFiBerry layer (a) restored, or the AE
     re-rules (P1 US-172 GATE; layer deviation accepted only while
     nothing is connected).
  4. US-170 (AE-final, verbatim, safety.md 1472206a): "Pi 4 only
     (N/A on the Pi 5): the F-358 runtime check on the Pi 4 before
     any Pi 4 audio use". (UX P3. Detail kept: the Pi 4 AC13 A1
     precondition (QE), including "no SIGKILL at startup with
     production coefficients" (AD L1).)
  5. F2: pcm-bridge/level-bridge PW nodes back after a PW restart
     (P1 below), or the INTERIM RULE (restart both bridges, confirm
     live meters).
  6. F-037/AC20: the open 8080 web UI is accepted only while nothing
     is connected.
  7. F-361 link-audit fix (P1 below: "before any amps-on use").
  8. F-373 (AE, verbatim; follows safety.md in #50): "After a USB
     re-enumeration the USBStreamer sink recovers without a PipeWire
     restart. The fix is re-tested with a physical replug:
     afterwards the USBStreamer hardware mixer reads no higher than
     before, all 16 gain values are 0 and the gate is closed (AE)".
     (Replaces "usbstreamer-volume-replug (AC17-B) PASS", deferred
     to F-373; a volume rise after the replug makes G16 High and an
     amps-on blocker, US-159.)
  9. The AC20 open blockers for amps-on / gig use: F-317, F-318,
     F-352, F-354, F-355 (F-358 resolved on the Pi 5; Pi 4 US-170).
  10. The 60-min flight-case thermal soak (GIG-READINESS entry, P1)
     PASS (AE: amps-on too, not only gig).
  11. F-372 (P1 below): the S-001 path check fix.
  12. RTTIME soft = hard (AD L1): an overrun SIGKILLs PipeWire with
     no SIGXCPU stage, which interrupts the USBStreamer and needs the
     F2 procedure. Documented in safety.md before amps-on.
  13. US-159 G16 (F-373) (AE, verbatim; follows safety.md in #50):
     "Any re-adoption of the USBStreamer sink after a re-enumeration
     (by GraphManager or WirePlumber) comes up gated: gains 0, gate
     closed, and audio returns only when the operator re-opens it
     through the D-063 ramp. Tested (AE)".
  14. Gate-authority defects (AD M4). CURRENT (#51 commit 2d22aa7a,
     TW; AE N1 final, AD agrees; supersedes the 1472206a text
     below), verbatim: "F-338, F-339, F-320, F-314, F-325 and F-349
     are closed, or each has an interim operating rule in the
     merged safety.md (planned in PR #45) that is followed. For
     F-314, F-349, F-338 and F-339 the interim rule must be
     AE-accepted. For F-338 and F-339 it must not rely on the web-UI
     Close Gate or on a CloseGate success reply: the emergency stop
     is the amp power switches (including the headphone/IEM amps),
     and after any gate close, mute or GraphManager restart, 'muted'
     is proven only by all 16 gain values reading 0 in pw-dump. That
     interim covers supervised sessions only (a person at those
     switches for the whole time the amps are on, and able to run
     the pw-dump read); before any gig or unattended use, F-338 and
     F-339 are closed. For any own-speaker venue (e.g. CHN-50P),
     F-321 and F-322 are also closed". N1 history: a closed-only
     variant (TW f7f37e87, never pushed) was withdrawn; AD wrote the
     supervised-interim sentence. Consequence: the F-338/F-339 fixes
     are NOT on the US-173 path; they gate any gig or unattended
     use. #45 follow-up (TW): #45's interim rules must carry the
     F-338/F-339 constraints (no Close Gate reliance, 16-gain
     pw-dump proof, supervised only); no "no interim" note on the
     F-338/F-339 records (TW withdrew it).
     Previous text (AE-final, safety.md 1472206a; supersedes AD's
     v92 text): "F-320, F-314, F-325,
     F-338, F-339 and F-349 are closed, or each has an interim
     operating rule in the merged safety.md (planned in PR #45) that
     is followed. For the two Critical ones (F-314, F-349) the
     interim rule must be AE-accepted. For any own-speaker venue
     (e.g. CHN-50P), F-321 and F-322 are also closed". AE reasons:
     "(PR #45)" pointed at an unmerged PR, so the row could not be
     checked against the repo; F-314 and F-349 are Critical and
     F-349 can't be seen by an operator, so their interim rules need
     AE acceptance; F-321/F-322 apply to every own-speaker venue,
     not only CHN-50P. AD's v92 text (superseded): "F-320, F-314,
     F-325, F-338, F-339, F-349 (and F-321/F-322 for CHN-50P) are
     closed, or their interim rules are in safety.md (PR #45) and
     are followed." Why (AD): the interim
     rules (status.md rules 5-7 and 12; safety.md §10 via PR #45) are
     not on main; F-338 (Close Gate disabled in the UI while the gate
     shows CLOSED) and F-339 (CloseGate reports success without
     writing the gains) make the F-320 interim rules impossible to
     carry out or to trust. safety.md mirror: TW, in the first docs
     PR after #50 merges (not #45; in #50 only if its head moves
     again for another reason); AE signs off the diff. Done on
     docs/US-163-postmerge at 1472206a (TW, AE wording); AD sees
     the widened row 14 (PM routed it). In review as PR #51.
  15. US-175 WP-restart re-link (AE, verbatim, 2026-10-25; PENDING
     the matching safety.md text in the TW's F-318 note batch, Part
     C2): "US-175: GraphManager re-link after a WirePlumber restart
     verified to come back gate closed, gains unchanged or 0, no
     automatic resume. Until verified: the operator check in the
     safety.md WirePlumber-restart rule after every WirePlumber
     restart." Under D-070 (supervised home-lab session) the
     operator check is enough; for gig or unattended use the row
     must be closed (AE). Source: /private/tmp/ae-f318-note-review-
     v1.md ADDENDUM. Mirror consequence: the safety.md lead-in ("14
     rows", "rows 1-3 and 5-14") and the Gate rule ("1-3, 5-14")
     change with this row; the TW updates them in the same batch,
     and this list then follows the merged safety.md wording.
     FINAL TEXT (AE ADDENDUM 5, via TW, 2026-10-25; this list takes
     it verbatim once the F-318 batch merges, mirror rule): "US-175:
     GraphManager re-link after a WirePlumber restart verified to
     come back with the gate closed and all 8 gain nodes at Mult and
     Add 0 (GraphManager may hold the venue gains as pending, but not
     live on the nodes), no automatic resume. Until verified: the
     operator check in the safety.md WirePlumber-restart rule after
     every WirePlumber restart." Pending row 14 changes, same batch
     (AE ADDENDUM 5, applied here on merge): "'muted' is proven only
     by all 16 gain values reading 0 in pw-dump" becomes "'muted' is
     proven only by all 16 gain values reading exactly 0.000000 via
     `pw-cli enum-params <pi4audio-convolver id> Props` (see Gains
     at boot)"; "able to run the pw-dump read" becomes "able to run
     that `pw-cli` read".
     Earlier note, superseded by the final text: the AE has since ruled that
     "unchanged" is a FAIL, so "gains unchanged or 0" above is
     superseded; the TW asked the AE for corrected text. Do not act
     on the quoted text; this row is replaced by the TW's final
     wording. The TW's batch carries the lead-in, the Gate rule
     "(1-3, 5-15)" and the table row, plus a D-070 row 15 interim
     entry and a Section 5 pre-flight check #11 (F-318 routing).
     Applied once the CM gives the TW the US-173 head with main/#51
     merged (before that the branch has no row 14).
  NEXT safety.md TOUCH (#51 reviews, non-blocking, fail safe; TW
  drafts, AE owns the wording, this list follows per the mirror
  rule): (1) AD L1 = UX (a): the lead-in "holds" (closed and
  verified) conflicts with row 14's interim-rule option; add
  "unless the row says otherwise (row 14)". (2) AD L2: the Gate
  bullet "while any item of the list above is open" literally
  includes the Pi 4-only row 4; say "any Pi 5 row (1-3, 5-14)".
  (3) UX (b): "(planned in PR #45)" goes stale; once #45 lands,
  name the section instead. AD nit, no change: §8.5 "the Mac" means
  any machine with Nix and the repo.
  UPDATE (CM, #51): (1) and (2) now go INTO #51, superseding "next
  touch" for them. Architect CHANGES REQUESTED at 667b7a8f
  (6402343698): R1 (required) = (1). N1 (non-blocking; AE and AD
  rule): F-338/F-339 must be closed, no interim option. AE APPROVE
  6402349414 crossed the hold; tally at 667b7a8f 6 approve + Arch
  changes requested, all lapse with the TW head move (R1 + L2 + AE
  final wording incl. the N1 ruling); all 7 re-review. (3) stays
  next touch (waits for #45). The lead-in and row 14 here follow
  the new #51 text verbatim once it exists (mirror rule). If N1
  makes F-338/F-339 closed-only, both fixes join the US-173 path
  (~1 day, Architect) and the DJ estimate to the owner is
  corrected (PM asked the AE to name the variant).
  RESOLVED: N1 = (B), the supervised interim (AE confirmed, AD's
  text, AD confirmed in re-review); not closed-only, no estimate
  change (back to 3-5 days, sent to team-lead). (1) AD L1 and (2)
  AD L2 are DONE by #51 (AD: close once #51 merges; merged
  b0666c02). (3) UX (b) "(planned in PR #45)" still waits for #45.
  NEW one-liner for the TW (UX P3, non-blocking, #51 re-review):
  repeat the F-338/F-339 interim as its own bullet under "Until the
  list is closed" (stop = the amp switches incl. HP/IEM; never
  trust the web-UI Close Gate; muted = all 16 pw-dump values 0).
  Mirror rule: this list follows the TW change.
  PENDING ROW H (AE, 2026-10-25; PO agrees; NOT yet numbered here):
  hardware level cap. With the speakers disconnected and a
  true-RMS multimeter on the amp outputs (superseded: the owner's
  oscilloscope, differential, per the AE H procedure in US-173.md;
  owner question on 2 channels + Math or a differential probe via
  team-lead), the amp input knobs are
  set and marked so 0 dBFS reaches at most 5.3 V rms on the sats
  (CHN-50P, 7 W into 4 ohm) and at most 20 V rms (~100 W) on the
  sub (UMII18-22, home lab). Not waivable: without H the AE accepts
  no interim rule. Mirror rule: the TW adds it to safety.md first,
  in the AE's wording, with its own review; this list then follows
  with the safety.md number. AE: row 14 stays the default gate;
  the supervised exception (D-070) needs its own safety.md change.
  MIRROR RULE (AE via TW, 2026-10-25): safety.md "Pi 5 Platform
  Status" carries this full table (13 items in #50; 14 rows on
  docs/US-163-postmerge 1472206a, the first post-merge docs PR) with
  this numbering. Where
  the two differ, this list follows safety.md. Any add, removal or
  renumbering here goes to the TW as a matching safety.md update.
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
  US-172 starter set (Architect, PO, CM; 2026-10-25, from
  CM-OBS-.89-DRM1; supersedes the "candidate causes" above):
  - Diagnosis (Architect; evidence drm-observe 4d7b6864, s5
    9868a2fc, s1011 3fd2c3c3): the firmware applies ZERO overlays
    with our config.txt. disable-bt-pi5 is not applied (BT node has
    no status); every display node stays at the base-DTB "disabled".
    Our artefacts are fine: offline fdtoverlay applies the KMS
    overlay cleanly. So it is our bug in the bootloader.nix
    config.txt layout. Lead cause, NOT yet proven: every
    dtoverlay/dtparam line comes before os_prefix=gens/<id>/, and
    nothing is at the FAT root.
  - First fix candidate: in configTxt emit os_prefix= (with kernel/
    initramfs/cmdline) before the dt lines, ~5 lines reordered. Also
    switch greetd off explicitly until it is ordered after DRM
    (Architect addendum); then greetd ordered after DRM (AC8, PO).
  - Step 1 = one CHANGE test boot (CM): (1) back up config.txt to
    config.txt.pre-drm on the FAT; (2) write the reordered copy via
    write-new + fsync + rename; (3) announced reboot, then read the
    BT status, axi/v3d@2000000 status, /dev/dri, lsmod vc4/v3d;
    (4) restore and check config.txt is byte-identical to the
    backup. PASS = BT disabled + v3d okay (order theory confirmed);
    no change = order theory wrong. The reboot announcement names
    the recovery route: FAT backup, card reader/owner as fallback
    (PO).
  - Fallback if no change: firmware log via vclog.
  - The F-367 guard stays in place until the fix is confirmed (PO).
  - Timing: after #50 merges (focus); the CM schedules the session.
    US-172.md gets this in a later story batch, not in #50 (CM).
    Architect: the starter set goes into the story when US-172 is
    activated.
  - TW N2 (#50 re-review, non-blocking): US-172.md:36 still carries
    the AC1 ride-in exception, which lapsed when the window closed;
    remove or mark it lapsed in the next US-172 story batch.
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
  State (CM, 2026-10-25): head 951d5162 pushed, draft PR #52. The
  Architect REPLACED the Step 1 procedure above (the config.txt
  hand-edit on the FAT is superseded): deploy the branch as a new
  generation (nixos-rebuild boot), announced reboot, pre/post reads,
  rollback per nixos-upgrade.md 8.5; a /dev/mem read counts as
  CHANGE. Test boot after US-163 AC19 closes. Story batch B4b (PM,
  base 951d5162, MANIFEST d646d2c3; US-172.md only, index row
  unchanged): the new Step 1, the branch head and PR #52, and the
  out-of-scope note for F-376. SUPERSEDED (CM held B4b; it carried
  the Architect's FIRST ruling): final test plan (Architect; worker-2
  implements it with pinned scripts), both after AC19. STEP 1 =
  CHANGE: one TRYBOOT of the CURRENT generation; tryboot.txt holds
  the reordered config.txt, config.txt is never written; the tar
  backup of the FAT is deleted after a cmp; announced
  `reboot '0 tryboot'`, TRYBOOT reads, restore, announced normal
  reboot, RESTORED reads; a power cycle recovers. STEP 2 = DEPLOY,
  only after a step 1 PASS: the branch as a new generation
  (nixos-rebuild boot), announced reboot, pre/post reads, 8.5
  rollback. The /dev/mem fallback read is CHANGE with its own CM go.
  B4c (2b92af26) also superseded. Story batch B4d (PM, base
  951d5162, MANIFEST 4474a3fc; US-172.md only, whole-file replace of
  B4b/B4c, index row unchanged).
  B4c was already relayed and committed by worker-2 (07eadd1a) before
  B4d; B4d (verified 4474a3fc) goes on top; both pushed together (CM).
  The tar/cmp wording matches the pinned us172.sh (the tar is deleted
  after cmp plus an identical FAT manifest). Step 1 session
  CM-CHG-.89-US172a granted to worker-2 (CM, after the AC19 PASS).
  B4d relayed to worker-2 as current (CM). The standby owner step
  for a test-boot hang (power cycle) is in team-lead's batch (CM).
  Head 381ef984 (B4c+B4d pushed, CM). The step 1 tryboot reboot
  failed harmlessly: on NixOS (systemd 258) the verb must be
  `systemctl reboot --reboot-argument='0 tryboot'`, not
  `reboot '0 tryboot'` (worker-2). installer.nix:11/34 and
  nixos-upgrade.md:387 are Raspbian contexts and stay as written.
  Step 1 re-granted at us172.sh 78bff43e. Story batch B4e (PM, base
  381ef984, MANIFEST 6df707bf; US-172.md only, whole-file superset
  of B4d, index row unchanged) fixes US-172.md:57; worker-2 commits
  it after their session. Harness gap (worker-2): us172.sh
  tb-reboot should check the transient reboot unit's result after
  the 5 s timer instead of polling for 900 s.
  tb-post (worker-2, CM 2026-10-25): the tryboot itself worked and
  audio/safety passed, but os_prefix order is NOT the cause (the
  tryboot falsified the order theory). Root cause still open,
  pending the firmware log; the CM gave the go for the firmware-log
  read on that boot. B4e verified by the CM (diff vs 381ef984 =
  step-1 lines 57-60 only), held until worker-2's session closes.
  UPDATE (CM, 2026-10-25; supersedes "pending the firmware log",
  "held" and "falsified" above): the firmware-log fallback ABORTED
  at the iomem guard (chosen/log is not in /proc/iomem;
  STRICT_DEVMEM=y); no read happened and this route is CLOSED.
  Restore and the normal reboot PASSED on rcyg67wd.
  CM-CHG-.89-US172a CLOSED. B4e committed as 27e90a0d and pushed.
  QE does NOT accept "falsified": the order theory is "not supported
  by step 1 (no positive control)". The next run needs a
  tryboot-only marker, and the bt oracle is split into
  absent/okay/disabled. Architect: the step-2 reorder is DROPPED;
  greetd-only does not go out either. fdtoverlay is GO, plus Mac
  checks: (a) which file tryboot reads, (b) the overlay path and
  names, (c) which base dtb.
  Marker spec (CM, 2026-10-25): `disable_splash=1` in tryboot.txt
  only, read with vcgencmd get_config. The 3-state bt oracle also
  prints the base-DTB model and compatible. Order: Mac results,
  then the revised step 2 reviewed by the Architect and the QE,
  then the CM's grant.
  H1 RULING (Architect, via CM, 2026-10-25): H1 FIRST and ALONE.
  H1 = a 64-byte firmware overlay path buffer overflows (paths of
  <=62 chars loaded, >=66 failed). Run-2 design: gens/<id>/o/ with
  copies, overlay_prefix=o/ plus disable_splash=1 in tryboot.txt
  only, 4-state oracle (accepted). Verdict confirmed / falsified /
  mixed = STOP. If H1 confirms, the fix (per-generation
  overlay_prefix in bootloader.nix or a shorter gen id, plus a
  path-length assertion in board-guard.nix) gets its own ruling.
  LIBPI option (i) approved: indirect root /home/ela/.us172-libpi
  on frspf350, removed when US-172 closes (CM, 2026-10-25: kept at
  RESTORED, removed only at US-172 close). Run-2 at stable SHAs
  (us172.sh 8706a804, drm-reads d1c52592), under Architect/QE
  review. Run-2 reviews (CM, 2026-10-25): Architect APPROVE at
  8706a804/d1c52592; Architect N1: tryboot.txt stays armed if tb-pre
  fails after the put, so tb-pre now removes it. QE CHANGES
  REQUESTED: R1 FALSIFIED only on the exact base states; R2 an
  oracle self-test before arming; R3 tb-reboot runs once per run
  id. worker-2 is revising. Revised (CM, 2026-10-25): us172.sh
  522e5571, drm-reads 0da219b4, with QE R1-R3 and Architect N1
  implemented; re-review with the QE and Architect. worker-2's Mac
  harness passed the oracle cases; the us172.sh changes were only
  checked with bash -n and shellcheck. QE APPROVE and Architect
  APPROVE at 522e5571/0da219b4 (CM, 2026-10-25). CM-CHG-.89-US172c
  granted to worker-2 (two announced reboots). QE non-blocking:
  US172_CM_GO set per command only; the run report notes that
  disarm is untested. Architect note: a failed first tb-reboot also
  locks the run until the CM releases it (intended). Run 2 (CM,
  2026-10-25, CM-CHG-.89-US172c, run id 20261025T210128Z): tb-pre
  PASS, PRE-base ok, additions only, config.txt untouched, thermal
  65-67.75 °C. GC root /home/ela/.us172-libpi -> frspf350
  (libraspberrypi), REMOVED at US-172 close. tb-reboot (1 of 1) in
  progress. RESULT (CM, 2026-10-25): the Pi did NOT come back from
  tb-reboot: down at 21:03:53Z; at 21:18Z no ping and no ARP from
  the Mac. Likely the H1 tryboot config (vc4-kms-v3d-pi5 +
  disable-bt overlays) hangs the boot; a US-172 finding. The owner
  is asked, via team-lead, for a power cycle; a cold boot uses the
  normal config (tryboot is one-shot). worker-2 is on HOLD with
  the session kept. Once the Pi is back: CM host-key/MAC check,
  worker-2's read-only state record, then the restore path,
  reviewed by the QE and Architect, before tb-restore. The Pi queue
  (US-173 Gate-2, the WP check) waits behind it. STOP confirmed
  (worker-2 via CM): tb-reboot verdict FAIL at 21:18:49Z, not back
  within 900 s (run 1's tryboot took 36 s); tryboot.txt consumed
  (one-shot), config.txt untouched, o/ present. Recovery proposal
  (worker-2), with the Architect and QE for a ruling: a read-only
  state record (boot_id, tryboot flag, gen, journalctl -b -1); skip
  tb-post (marker 0 on a normal boot STOPs by design); tb-restore
  FAT-only; a RESTORED check, with no tb-normal reboot if the boot
  is already normal. The hang is F-389 (Architect, 2026-10-25; was
  "whether ... gets its own F"). QE RULING (via CM, 2026-10-25;
  the Architect's is pending; the CM gives worker-2 the go only
  after both): plan
  accepted. tb-post skipped, recorded as "skipped: normal boot,
  would STOP by design". No tb-normal reboot: (c) is met on the
  power-cycled boot once, after tb-restore, the manifest == PRE
  byte for byte. R3 holds: no tryboot of any kind until the
  Architect rules on a next step. Order on the Pi, before any FAT
  write: (1) the current boot (boot_id, tryboot flag 0, marker 0,
  booted rcyg67wd, overlay_prefix gens/<id>/overlays/); (2)
  journalctl --list-boots: if a kernel boot happened between PRE
  and now, save its journal (-b <id>, -k), timeline from the Mac
  poll times; (3) /sys/fs/pstore, thermal, the rpi_volt alarm,
  vcgencmd get_throttled; (4) a post-hang FAT manifest diffed
  against the armed manifest, which must be 0 lines; (5)
  tb-restore; (6) the RESTORED reads on this boot (audio, drm, the
  (c) checks). Steps 1-4 are read-only OBSERVE; a script change for
  step 6 is a new SHA and a quick QE + Architect re-review. H1
  outcome: "H1 NO-RETURN (inconclusive)", neither CONFIRMED nor
  FALSIFIED. The run report has the timeline, steps 1-4 verbatim
  and the single-variable statement (run 2 = run 1 +
  overlay_prefix=o/ + disable_splash=1 turned a 36 s return into
  no return); no claim on whether the overlays applied; it carries
  the disarm note. Without a console, any rerun needs a design that
  splits the variables (the Architect's call).
  ARCHITECT RULING (via CM, 2026-10-25; adds to the QE's): Safety:
  the power cycle clears the tryboot flag, so a normal boot into
  the base generation; no audio concern (cold USBStreamer at 0 dB
  hw; D-063 Mult 0 and the closed gate apply; nothing connected).
  SD: read-only checks for a FAT dirty bit and ext4 errors before
  tb-restore; any manifest difference besides o/ + tryboot.txt =
  STOP. Reads before tb-restore add `ls /var/log/journal` (is the
  journal persistent?), the hung-boot journal with -o
  short-monotonic and a grep list, and pstore. H1 INCONCLUSIVE, not
  CONFIRMED: "positive control unread; H1 unresolved". NO tryboot
  of any kind until the Architect and QE approve run 3. Run-3
  design: self-recovery via panic=10 and softlockup_panic=1 on a
  tryboot-only cmdline plus RuntimeWatchdogSec on bcm2835; a
  persistent journal; split 3a (o/ with only disable-bt-pi5), then
  3b adds vc4-kms after 3a. Owner-physical, list-only, nothing
  blocks on it: the power cycle and the LED glance (already asked);
  optional an HDMI monitor connected before run 3b; the QE's UART
  item (below). CM DECISION (supersedes the QE's "no tb-normal
  reboot" above): tb-normal runs after tb-restore as a plain reboot
  gated by the CM's logged go, because the tb-normal guard cannot
  trigger with tb-post skipped; a known limitation in the run
  report.
  ARCHITECT ADDENDUM (via CM, 2026-10-25): tb-normal YES after
  tb-restore on the CM's logged go (supersedes the Architect's
  "skip"; QE and Architect agree). Run-3 guard: refuse tb-normal
  when a tb-reboot log with a FAIL exists and there is no tb-post
  log, unless US172_CM_GO=1. Hypothesis B variant: was
  overlay_map.dtb in o/? worker-2 states this; if it was missing,
  3a includes it, sha-checked from KDIR. Discrimination: a
  hung-boot journal rules out B; no journal and no flash code
  points to early kernel; a flash code points to firmware.
  disable_splash stays the marker. F-389 BLOCKS US-172. Console
  repeat not now: HDMI during 3b is offer-only; UART is the last
  fallback, only if 3b hangs AND leaves no journal; any repeat with
  a console goes back to the Architect. get_throttled counts as a
  current-boot reading only. worker-2's recovery script
  us172-recovery.sh (bf33e6e1...) is under Architect + QE review.
  Result (CM, 2026-10-25): CHANGES REQUESTED by both; fixed at
  2832a5c6 and back with both for a re-check. The Pi is still down.
  Architect and QE APPROVED us172-recovery.sh 2832a5c6 (CM,
  2026-10-25). Architect note: a missing "reboot: Restarting
  system" at the end of OLD is recorded as "not seen", not as
  "hung in shutdown". The Pi is still down.
  HDMI and UART stay list-only until run 3 is approved (CM: not to
  team-lead now). H1 may pre-empt
  the Pi
  build queue between derivations once reviewed; US-173 Gate-2
  follows H1.
  /dev/mem firmware-log read: DEFERRED. Eligible only if H1 is
  falsified or mixed AND the Mac check shows the mailbox
  (/dev/vcio) cannot fetch the log; then the Architect and QE rule
  and the guard script gets its own review. BINDING pre-conditions
  (SecSpec, recorded per the Architect): (1) read only the exact
  range chosen/log 0x3ff22000 + 512K, no writes; (2) STRICT_DEVMEM
  stays on; a kernel refusal is the answer; (3) fail-closed guard:
  the range lies inside memreserve/reserved-memory, no overlap with
  a device reg, iomem or a secure/TF-A node; one attempt; (4)
  treated as a possible crash: CHANGE tier, exclusive, announced,
  boot-id/oops/SError check afterwards; (5) dump 0600, sha logged,
  only reviewed excerpts quoted; (6) a one-off diagnostic, not a
  mechanism. Debug-UART capture needs the owner's hands: last
  resort. Owner-physical, CONDITIONAL (QE, 2026-10-25): attach a
  USB-serial adapter to the Pi 5 UART debug header so the team can
  capture the boot console (enable_uart=1 is already set). Only if
  the Architect plans another tryboot run; the Architect decides.
  It goes to team-lead's batched owner list only then.
  Same deferred class (worker-2, via CM, 2026-10-25): a non-/dev/mem
  route to the VC log, mmap of /dev/vc-mem at 0x3ff22000. It maps
  physical memory uncached and bypasses STRICT_DEVMEM, so it needs a
  SecSpec/Architect ruling like the /dev/mem read. NOT in run 2.
  SecSpec (via CM, 2026-10-25): same class as /dev/mem but stricter,
  because it bypasses STRICT_DEVMEM: the same six conditions, plus
  an explicit Architect ruling that the mapping is PROT_READ only.
  Facts: vclog is not in nixpkgs (raspberrypi/utils); the vc-mem
  DMA path returns ENXIO on the Pi 5.
  H1 QE conditions (a)-(d) adopted (CM, 2026-10-25): copy sha256 and
  path length shown before the reboot; DT status is the primary
  oracle, dmesg and /dev/dri secondary; RESTORED = o/ gone +
  manifest == PRE + marker 0; a mixed state or marker 0 = STOP.
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
- **US-173** Supervised home-lab first DJ session (Pi 5) (PO,
  2026-10-25; P1/High; next after US-172). Origin: owner question
  "So how many days until I can use this setup to spin some
  songs?"; PM estimate to team-lead (PO, AE, Architect): 3-5 working
  days, 6-8 if the display or the Hercules surprise, plus fan
  delivery. ACs (PO):
  - H set and marked (pending row H above; owner with multimeter,
    speakers disconnected).
  - Crossover-only minimum-phase WAVs from the US-155 config
    (scripts/generate-crossover-coeffs.py), magnitude response
    verified by the AE (sat HPF clearly down at 80 Hz, sub LP, sane
    sum); no room correction. AD (#55 review, 2026-10-25): after
    #55 merges, regenerate the session WAVs from the merged SHA, the
    AE re-checks them (AC2 was checked on pre-F-374 files), and the
    AC3a SHA256SUMS are committed from that same regeneration.
    AE (via CM, 2026-10-25): the AC2 re-check runs ONLY on WAVs
    regenerated from the #55 merge SHA, with the AC3a SHA256SUMS
    from the same run.
  - F-321 check (AE, NOT waivable): sha256 of the WAVs the convolver
    actually loaded matches the generated files, before amps on.
  - F-341 AC3 (AE, NOT waivable): nc checks #3/#6 verified on the
    Pi 5 in one CM session.
  - F-318 fixed (Architect: small WP rule, 0.5-1 day): non-JACK
    streams never auto-link to the USBStreamer.
  - Home-lab venue file with audible gain_db (AE values; a gain
    increase, so the owner's S-012 confirmation at the session).
  - "DJ routing via GraphManager on the Pi 5: Mixxx -> convolver ->
    gate -> USBStreamer, quantum 1024; no manual pw-link around the
    gate. Verified by link audit." (PO)
  - "The Hercules DJControl Mix Ultra is recognised by Mixxx via
    USB-MIDI (deck/play/crossfader work). If it fails: a separate
    story, and the session may run with mouse/keyboard only if the
    owner wants." (PO)
  - Thermal: the first session is the thermal soak (10 s sampling
    per the AE thermal rule; STOP at 80 C). What STOP means in
    practice (end the session / amps off) is defined beforehand by
    AE and UX as a procedure; owner question only if the team
    cannot specify it (PO).
  - Pre-flight plus owner re-confirmation; session rules (AE): amps
    on last and off first, amp power switch within reach (the
    emergency stop), no USB replugging, fixed USB cable with strain
    relief and no hub, one deployed venue, no web-UI gain edits.
  Parallel start (PO): the sub-items that don't need the display (H,
  F-321 check, F-341 AC3, F-318, venue gains, the AE WAV check) may
  start now, in parallel with US-172 and without blocking it. Only
  the session itself waits for US-172.
  Out of scope (PO): IEM/HP (ch 5-8 gated and muted), room
  correction, second sub and time alignment, Live mode, APCmini.
  Owner physical list (sent to team-lead): remove the HiFiBerry HAT
  (or confirm nothing on it); fit a fan; plug in the Hercules over
  USB; wiring ADA8200 out 1/2/3 -> amp in 1/2/3 (out 4 not
  connected), amp ch1/ch2 -> CHN-50P L/R, ch3 -> UMII18-22 coils in
  series (4 ohm), ch4 nothing, + to + everywhere; ~30 min multimeter
  session for H. Owner questions sent (team-lead): target "home-lab
  test, no room correction"; which speakers/subs; true-RMS
  multimeter and fan on hand; F-037 (web UI without auth) accepted
  for this session. OWNER ANSWERS (2026-10-25, verbatim via
  team-lead): Q1 "As a milestone yes, but I want the room
  correction too." Q2 "correct" (CHN-50P pair plus one UMII18-22).
  Q3 "I have an oscilloscope, that should allow me to measure RMS.
  A fan seems to be easy enough to procure, don't worry about
  that" (team-lead asks the AE whether the oscilloscope suits H;
  the fan is the owner's, no team action). Q4 "acceptable for home
  lab" (F-037 with amps on, home lab). So US-173 is a MILESTONE,
  not the end goal: room correction stays a wanted follow-up;
  placement (next after US-173 or alongside) is with the PO.
  Lanes (CM, 2026-10-25): branch story/US-173-first-dj-session
  from main 07a65f9e, separate PR from US-172. F-318 (WP rule):
  worker-1 on that branch after AC19 closes (superseded: worker-3,
  spawned by team-lead, does F-318 + B5 there); WP files fenced to
  F-318 (worker-2 tells the CM first if US-172 AC7 needs WP).
  US-172 (worker-2) touches only board-guard.nix,
  boards/pi5/bootloader.nix, boards/pi5/default.nix. Pi order:
  AC19 -> US-172 test boot -> US-173 Pi reads (F-341 AC3, H prep).
  AE (advisor/Mac, no worker lane; PM routed): crossover WAVs and
  check, home-lab venue gains, F-321 sha procedure. Story batch B5
  (PM): US-173.md, its stories-index row, D-070.md.
  Estimate note: the +1 day for F-338/F-339 sent to team-lead is
  withdrawn by the N1 final (row 14 above); back to 3-5 working
  days; the PM sends the correction once the CM bundle at the new
  #51 head exists (AE). Architect: the full code fixes (worker-1 GM
  lane F-361 -> F-373/G16 -> GM DJ mode; worker-2 lane F-362 ->
  F-372 -> F-352/F-354/F-355 -> F-338/F-339 -> F2 -> F-318 -> F-317)
  are ~6-9 working days and gate unsupervised or gig use, not this
  session.
  B5 (PM): MANIFEST 40a37a1a (US-173.md, D-070.md, the US-173 and
  D-070 index rows, 1-line diffs vs 07a65f9e); CM verified 4/4,
  handed to worker-3 to commit. US-173.md carries the AE H
  procedure for the owner's oscilloscope. Fan: the owner procures
  one; US-163 AC4 stays "no fan, N/A"; thermals re-checked once
  the fan is fitted (US-173 AC9; PO). F-037: accepted for home-lab
  amps-on use only, NOT for gigs (owner Q4, PO).
  D-070 (ACCEPTED, owner 2026-10-25, PO; was PROPOSED: owner inputs
  answered 2026-10-25: Q1 milestone
  yes, Q4 F-037 acceptable for home lab; team-lead: no longer
  pending owner on these; takes effect only with its own safety.md
  change merged under Rule 13): supervised home-lab
  first-session exception. Interim rules (AE) replace the full fix
  for named amps-on rows. "The exception lists the replaced amps-on
  rows individually with their interim rule; valid only with H set
  and the owner present; expires per row as soon as the full fix is
  merged." F-321 sha and F-341 AC3 are NOT replaced (AE). Pending
  the owner answers (target, F-037 acceptance with amps on). Needs
  its own safety.md change and review (AE). AE interim rules per
  row (2026-10-25, summary): 1 procedure; 3 remove the HAT; 5
  restart bridges, confirm meters; 6 F-037 bounded by H; 7 manual
  `pw-link -l` check before the gate opens (only convolver-out ->
  USBStreamer AUX); 8/13 F-373 rule, amps off before any recovery;
  9 F-317/F-325 amp switch in reach; F-318 fixed (or link check +
  no other apps); F-352/F-354/F-355 no Config gain API, no web-UI
  gain edits, limiter unconfigured; 10 first session = soak; 11
  F-372 one venue, no switching or uploads; 12 existing rule; 14
  F-320 never watchdog_unlatch, latch -> amps off and restart;
  F-314 never switch venue with the gate open; F-338/F-339 amp
  switch as e-stop, gains verified from pw-dump (see N1 above);
  F-349 H + fresh PW start + no NaN sources; F-322 covered by H.
  AE Mac-side items (2026-10-25; generated from a read-only export of
  07a65f9e in /private/tmp/ae-us173/, nothing in the repo yet):
  - Crossover WAVs: NEW DEFECT F-374 (P1 below). A +5.4 dB bump at
    200 Hz; the AE recommends the fix before the first session (else
    an audible boom at 140-280 Hz; not a speaker-safety issue).
    All other WAV checks pass (48 kHz mono float32, 16384 taps,
    causal min-phase, tail decayed, max gain -0.6 dB, L = R, sub DC
    -0.6 dB under the D-031 exception; sat HPF 80 Hz -31.8 dB, US-155
    AC2 OK). Correction (AE): "US-155 is usable" holds for safety
    only; US-155 AC1 (summation) is not signed until F-374 lands.
  - Home-lab venue draft home-lab-chn50p-ultimax.yml: mains -12 dB,
    sub -20 dB, ch 4 -120 dB, HP/IEM -120 dB (muted on purpose, none
    used). With H set: at most ~0.4 W per CHN-50P and ~3.5 W sub at
    full scale incl. the +6 dB L+R sum. Header: valid only with H.
    The owner confirms at the session (S-012) before the gate opens.
  - F-321 loaded-WAV check (before amps on, every session after any
    deploy or reboot; any failure = amps stay off): (a) expected
    hashes from a SHA256SUMS committed next to the WAVs; deploy
    copies exactly those, never regenerates on the Pi (libsndfile
    writes a timestamp into the PEAK chunk, sample data identical);
    (b) OBSERVE sha256 of combined_left_hp, combined_right_hp,
    combined_sub1_lp match, dirac and combined_sub2_lp recorded;
    (c) PW start time later than all three mtimes, else an announced
    PW restart (USBStreamer interruption) and re-check; (d) no
    filter-chain/convolver load error in the journal since PW start;
    (e) GM active venue = home-lab-chn50p-ultimax; (f) recommended
    once per deploy, speakers disconnected (can share the H
    session): same-level 100 Hz and 1 kHz tones, read on the scope,
    ch 1 at 100 Hz >= 20 dB below 1 kHz, ch 3 at 1 kHz >= 40 dB below
    100 Hz, dirac 0 dB; only (f) proves what PW convolves. H also
    caps CHN-50P excursion (~7.5 V peak vs ~8.6 V peak Xmax), so a
    wrong filter under H costs sound quality, not the driver.
  - These go into US-173.md as story batch B5b (PM, pending) for
    worker-3. The AE signs off the H row and D-070 exception drafts
    when the TW has them. DONE: B5b (MANIFEST caebf509, base
    ad478593 = worker-3's B5 commit) verified by the CM and relayed
    to worker-3.
  Lane additions (CM, Architect, 2026-10-25): worker-3 also gets the
  venue YAML, the WAVs in configs/coeffs/venues/home-lab-chn50p-
  ultimax/, test_committed_venue_coeffs.py and the pipewire.nix
  install path (Architect: tmpfiles `C` never replaces the DIRAC
  placeholders), plus one ci.yml T1 step and one development.md line
  (QE DoD); no other lane touches them. AE install requirements for
  the venue WAVs (to worker-3): L+ symlinks preferred, atomic; the
  200 Hz set is home-lab-only per F-321; sub2 stays dirac; the PW
  restart is announced; a Nix sha assertion.
  SecSpec (2026-10-25): F-318 (a), the WP rule, is accepted ALONE as
  the interim for the supervised session; F-318 stays OPEN until
  layer (b), now US-175 (P1 below). The amps call is the AE's.
  F-318 (a) pushed (worker-3, CM 2026-10-25): story/US-173-first-dj-
  session = 695f69af, 8 files; F-318 stays OPEN. aarch64-linux check
  green; Lua 18/18 with 4 mutants killed; integration 17/17; the
  negative control fails 14/17 as required. Implementation reviews
  open: Architect, SecSpec, UX. B5b (caebf509) was relayed but is
  NOT on the branch (only B5 ad478593).
  B5b DONE (CM, 2026-10-25): worker-3 committed it as d588ceb0
  (US-173.md sha 22080732, matches caebf509), pushed. US-173 head
  0e0cbd38 (includes the venue YAML). UX: ACCEPTABLE, PROCEED WITH
  NOTES (fail-closed denial: pw-play and paplay get "no target node
  available" and exit). Architect N1 for F-318: a static nix check
  that the deny hook's `after` names exist in WP's scripts;
  worker-3 does it in-branch if it fits the fence, else a backlog
  item (CM says which). The ci.yml step and the development.md line
  (finding c) go to F-380, not US-173 (CM). Gate-2 on the Pi
  (worker-3) is queued after CM-CHG-.89-F365.
  - UX N1 (MUST land before the US-173 PR merges; TW-owned docs, on
    the US-173 branch, worker-3 commits): an operator note in
    troubleshooting and next to the F-373 rule in safety.md: (1) "no
    target node available" from pw-play, paplay or a browser is
    expected; mugge never auto-routes playback (F-318); (2) make
    sound with the signal-gen web UI, or Mixxx/Reaper via the
    GM-linked JACK path; (3) confirm with `journalctl --user -u
    wireplumber | grep F-318`; (4) never pw-link to the USBStreamer
    by hand.
    Status (TW, 2026-10-25): draft /tmp/tw-f318-note-draft-v3.md:
    a safety.md bullet after the F-373 rule plus a new SETUP-MANUAL
    section 14 subsection "No target node available" (no other
    troubleshooting doc). Part C = the US-175 WP-restart addition:
    C1 in the Section 1 transient list (AE OK); C2 a Pi 5 rule
    bullet, replaced by the AE's verbatim text (marked NOT yet
    verified; operator check after every WP restart), with amps-on
    row 15 added (see the AMPS-ON list). UX OK'd v3. Waiting: AE
    sign-off of the final draft; the CM merging main (#51) into the
    US-173 branch first, so the whole-file batch does not undo
    safety.md row 14. Then a whole-file batch to the CM; worker-3
    commits.
    AE ruling (via TW, 2026-10-25): SETUP-MANUAL section 14 "No
    Sound Output" is fixed IN this batch with AE text (step 6
    opened the gate with no checks; step 7 ran speaker-test
    straight to hw:1,0; step 1 `aplay -l` becomes `cat
    /proc/asound/cards`). Not a backlog item. Team-lead and UX
    concur (steps 6 and 7 replaced); PM asked the AE to confirm
    directly. CONFIRMED (AE, 2026-10-25; text in the AE review file,
    Q2): step 6 checks the gate state read-only (a closed gate is
    the safe default, never opened as a troubleshooting step); step
    7 is read-only `cat /proc/asound/cards`, never playing straight
    to hw:; step 1 merges into or points to step 7 (TW's choice).
    TW has 3 open
    questions to the AE on the C2 bullet; row 15 number and text
    may still change.
  - UX N2 (backlog; not needed for US-173): a dismissible web UI
    information line "Playback from <app> blocked: mugge routes
    audio itself".
  - Backlog (Architect via worker-4, 2026-10-25): the venue YAML
    should name its speaker profile in a machine-readable field
    (today only a comment). worker-3's US-173 lane; until then the
    --venue CLI takes --speaker-profile explicitly.
  - OPEN joint ruling (Architect + AE): "GM links survive a WP
    restart", option (1) or (2).
    RULED (Architect + AE, CM 2026-10-25): the US-173 evidence item
    is reworded to "F-318 never removes GM-created links; after a
    WP restart GM re-links (US-175)". worker-3 makes no change. The
    re-link requirement goes to US-175 (see there).
  - No null sink in F-318 (AE and Architect, 2026-10-25).
  - Gate-2 amps call (AE, for worker-3, 2026-10-25): amps OFF, no
    HP/IEM; restarts are announce-only; D-070 NOT in effect.
    Optional F-321(f) tone check, digital only, gains at or below
    the venue draft (sats -12, sub -20, ch 4 and HP/IEM -120); then
    the gate closed, gains back to 0 and AC14 read back.
  - Gate-2 evidence (AE, via CM, 2026-10-25): raw `pw-link -l`
    captures, to confirm the PW 1.6.2 input marker before the
    operator docs name it, and that AUX0..7 carry only
    convolver-out. Gate-2 follows US-172 H1 on the Pi.
  - Gate-2 scripts ready (worker-3, via CM, 2026-10-25) in
    /tmp/w3-gate2/: gate2.py 806d7ab7, selftest 7de5943a,
    selftest.nix 90258d73; sandbox 26/26 with the policy on, 18/26
    fail with it off. Under QE, AE, Architect and Security review.
    Pi order: US-172 recovery -> deploy 142a3523 -> preflight
    (OBSERVE) -> full run (CHANGE). c7dde808, a9addc52 and 142a3523
    are already pushed.
  - Pushed (CM, 2026-10-25): story/US-173-first-dj-session =
    142a3523 (the F-380 revert of c7dde808, SecSpec fixes and
    Architect N1 in a9addc52, merge of main dfdbbbd6).
  worker-3 findings (not fixed):
  - a) A WirePlumber restart re-creates the ports of nodes it adopts
    and drops their links, even with the policy disabled;
    GraphManager must re-link. Untested; relevant to the Pi Gate-2
    item "GM links 24 unchanged after a WP restart". UX N3: see the
    OUTPUT DEVICE LOST item.
  - b) Stock WP logs "wp_event_dispatcher_unregister_hook: assertion
    failed" 4 times per start; looks harmless.
  - c) Wanted outside worker-3's fence: a CI step for
    checks.aarch64-linux.wireplumber-no-bypass plus a
    development.md line. The CM routes it to the Architect; likely
    part of F-380.
- **US-174** Automated room correction pipeline (Pi 5, home lab
  first) (PO, 2026-10-25; P1 EPIC). Owner, verbatim via team-lead:
  "As a milestone yes, but I want the room correction too.", "I
  would think the room correction is work that could be done
  entirely in parallel." and "We have a full room simulator to
  test the room correction!" So it runs IN PARALLEL with US-172
  and US-173 (supersedes the PO's "next after US-173"); US-173's
  first session does NOT wait for it (PO). Own worker (worker-4,
  team-lead) on story/US-174-room-correction from main b0666c02
  (CM creates it once the first slice and file boundary are set).
  Sub-story cut (PO proposal; Architect + PM split before
  implementation): a) spec/theory (docs/theory: measurement
  procedure, minimum-phase FIR generation, crossover combination,
  16k taps, sub/mains time alignment, measurement safety limits);
  b) offline filter generation (Python, tested against the room
  simulator src/room-correction/mock/room_simulator.py and
  recorded data, no Pi); c) measurement on the Pi 5 (UMIK-1 +
  signal-gen through the gate, calibration file 7161942); d)
  deploy + verification (load filters, re-measure, AE acceptance);
  e) later: the one-button venue workflow (design principle 6).
  c) and d) wait strictly for US-173's H, F-341 AC3 (no signal-gen
  measurement session before it) and D-070 / the amps-on list.
  Pending: the Architect and AE define the first slice and the file
  boundary (expected src/room-correction/ only, disjoint from nix/,
  the GraphManager code and the F-318 WP files); the PM relays it
  to team-lead for worker-4.
  DONE (Architect, 2026-10-25; PO accepted the cut): first slice
  US-174b "Offline filter generation, closed loop against the room
  simulator" (venue markaudio-ultimax-200hz.yml; 3 scenarios + a
  generic home-lab one; ACs 1-8 in US-174.md); AE numbers (X, Y,
  boost cap, pre-ringing threshold, target curve, band) follow as
  AC refinements (174a, day 1). File boundary: WRITE
  src/room-correction/** and new files in configs/room-correction/;
  API freeze on the names src/web-ui imports; deploy.py,
  pw_config_generator.py, recording.py, ws_server.py not edited;
  OUT nix/, flake.*, all Rust, src/web-ui/**, configs/pipewire/,
  configs/wireplumber/, scripts/local-demo.sh; a new Python dep
  means STOP and a separate nix PR; the CM checks the diff names
  on every push. Brief sent to the CM for worker-4 (spawned,
  branch from b0666c02). Sub-story IDs (PO): suffixes US-174a..e;
  US-067 keeps its ID as US-174b2 (optional; after 174b and after
  worker-2's lane). 174c is gated by the FULL amps-on list, H,
  F-341 AC3, D-070 and the S-010 measurement rules; it needs the
  UMIK-1 calibration file (serial 7161942) re-fetched from miniDSP
  (the Pi 4 copy is unreachable). 174e comes after worker-2's
  web-UI lane. Owner list (sent to team-lead, no hurry): the UMIK-1
  calibration file (owner or team fetches); the home-lab room
  dimensions and positions. Story batch B6 (PM, MANIFEST
  a0f9b60c, base b0666c02): US-174.md, 11 old story status lines,
  their index cells, the US-174 index row. Its index row sits next
  to B5's US-173 row: trivial merge conflict expected (CM).
  B6 verified 13/13 (CM), handed to worker-4 to commit; boundary
  check script armed on every push (PM batch paths excepted).
  174a DONE (AE, 2026-10-25), numbers for 174b: boost cap |H| <=
  -0.5 dB absolute; dip-fill sub <= +6 dB 30-200 Hz, 0 dB below
  30 Hz, sats <= +3 dB; nulls narrower than 1/3 octave or deeper
  than 10 dB left alone; min-phase gate = energy of
  (h - minphase(|H|)) <= -40 dB re h (NOT "energy before the peak":
  a correct min-phase lowpass fails it), last 5% of taps <= -60 dB;
  X = +/-3 dB 30-500 Hz on the summed response, 1/6 octave, flat
  target (500 Hz-16 kHz +/-4 dB at 1/3 octave only if simulated);
  Y = corrected RMS <= uncorrected + 1 dB off-position, no 1/3-octave
  band > 3 dB worse; GD <= 3.5 ms 50-300 Hz and <= 1 ms above 500 Hz
  (excl. +/-1/6 octave around corrected modes; "1-2 ms at 200 Hz" is
  not achievable with LR4), sat-sub phase <= 30 deg at 200 Hz,
  modal decay not longer than uncorrected. Precondition: F-374 lands
  before AC3-AC5 are judged. 174c (AE): H also applies to sweeps;
  UMIK-1 file magnitude-only, -1.378 dB; the owner may have a copy,
  else a team member downloads it by serial (no owner needed);
  verify the serial in the header. Story batch B6b (PM, MANIFEST
  a8a7b6c9, on top of B6): US-174.md AC2-AC5 values, the F-374
  precondition, the UMIK-1 wording; sent to the CM for worker-4.
  worker-4 found the purifi Qts test failure on b0666c02: that is
  F-363 (P2), not a new item; it can block a green T1 on the US-174
  PR too, and worker-4 does not fix it there. QE: F-363 is NOT a
  pre-gate for US-174's T1 (see F-363).
  B6 pushed (CM): story/US-174-room-correction = 858fa861 (13 blobs
  = a0f9b60c); B6b verified (a8a7b6c9), with worker-4.
  AE refinement (2026-10-25, after worker-4 found that correction.py
  has no level reference: the cut follows the measurement level 1:1,
  so a +12 dB mode gets about a 29 dB cut). Supersedes the dip-fill,
  X and Y parts of the 174a numbers above: slice 1 is cut-only, NO
  dip-fill; per-bin cut <= the measured excess and <= 18 dB
  (required; if the frozen API blocks the kwarg, it goes to the AE
  and the Architect, not dropped); level reference = per-channel
  median, 1/6 octave, sats 400 Hz-4 kHz, sub 30-150 Hz; new ACs:
  level invariance (IR x0.1/x1/x10 -> same filter within 0.1 dB),
  cut accuracy +/-2 dB of each injected mode's excess, verify
  tolerance default 8 -> 3 dB. Residual one-sided: positive <= +3
  dB, below target unchanged within 0.5 dB; bands sub 30-200 Hz,
  sats 250-500 Hz, system summed 30-500 Hz; metric max positive
  deviation at 1/6 octave. Off-position (Y) DEFERRED, not waived
  (the simulator has the same modes at every position) to
  US-174b-sim; positions B = +0.5 m lateral, C = +1.0 m depth; Y
  unchanged. Sub delay truth = geometric direct path, +/-0.2 ms.
  Min-phase gate and GD unchanged; the Architect accepts the AE's
  3.5 ms GD budget as binding.
  Architect (2026-10-25): slice 1 adds a pure pipeline function
  (runner.py delegates), the correction.py level-normalization fix
  with a level-invariance test, and speaker_sim in
  simulate_measurement. NEW sub-story US-174b-sim, after slice 1: a
  position-dependent modal sum in mock/room_simulator.py (unlocks
  AC4 and spatial averaging). Fence change: crossover.py,
  test_crossover.py and the generate_profile_filters.py type
  pass-through are worker-5's (F-374) until F-374 merges; worker-4
  picks them up by merging main (CM fence script).
  Story batches B6c (MANIFEST ea7c48d5: the refinement, slice-1
  lines, US-174b-sim, the F-374 lane and fence) and B6d (MANIFEST
  946cd203, on top of B6c: AC3 bands, cut-cap rule, AC4 positions,
  AC6 tolerance), each a whole-file replace of US-174.md.
  B6b pushed: story/US-174-room-correction = 0b412fde (CM); B6c
  (ea7c48d5) and B6d (946cd203) verified and relayed. AE alignment
  (2026-10-25; worker-4 builds to it): AC6 = within 1 sample of the
  geometric truth (stricter than +/-0.2 ms; worker-4 tests both;
  supersedes the "+/-0.2 ms" above); AC2 adds "below-target regions
  unchanged within 0.5 dB" as a gate; NEW AC6a: simulated pink noise
  with a fixed seed, at -60 dB re the recording peak it gates (no
  extra cuts below 30 Hz vs the noise-free run, +/-1 dB), at -40 dB
  report-only. Story batch B6e (PM, MANIFEST 1accdb6e, on top of
  B6d, whole-file replace).
  Fence script carve-outs (CM): crossover.py, test_crossover.py,
  generate_profile_filters.py, test_generate_profile_filters.py
  (worker-5, F-374); test_driver_validation.py (F-363, worker-6);
  test_committed_venue_coeffs.py (worker-3).
  Prerequisite (Architect): chore/rc-check-configs (worker-7, off
  b0666c02; F-365 room-correction part) copies configs/ into
  checks.test-room-correction; it lands before the 174b PR and
  before US-173 adds its checks line.
  B6e verified (1accdb6e) and relayed to worker-4, replacing B6d
  (CM). Merge order (Architect, as given): F-363, then
  chore/rc-check-configs, then the 174b PR; US-173 merges main after
  chore/rc-check-configs. F-374 merges first per the earlier ruling.
  Pushed (CM, 2026-10-25, later): story/US-174-room-correction =
  d595613f (US-174b). worker-4 hit one classifier denial (PII Data
  Handling, a read under /tmp/claude-503); team-lead reports it to
  the owner. Pushed (CM, 2026-10-25): f515f99d with per-scenario
  non-vacuity, the large_hall/outdoor_tent exclusions with a
  guard, the rename to test_venue_closed_loop.py and the F-383
  margin comment; 68 passed, e2e 76. Waiting on the QE's verdict.
  Pushed (CM, 2026-10-25): 830b4e20 with the QE's noise-live
  assert; 69 tests; worker-4's mutation check is red with the noise
  branch disabled. QE CHANGES REQUESTED at f515f99d, R1: the guard
  test must also check do-no-harm (max+ <= MAX_POSITIVE_DEVIATION_DB)
  on the excluded large_hall/outdoor_tent; one line, test count
  unchanged. R1 is with worker-4. After R1, worker-4 is cleared to
  run both nix run apps (the dry-run builds only the wrapper drvs):
  df before and after, sequential, abort below 3.0 GiB free. HELD
  (CM, 2026-10-25): Mac disk 2.95 GiB, below the line; pytest in
  the dev shell continues (see the Mac disk item). Pushed (CM,
  2026-10-25): R1 bcc353ed (do-no-harm max+ <= 3 dB on
  large_hall/outdoor_tent; mutation x2 red). The nix runs on
  bcc353ed had finished before the hold: test-room-correction 1
  failed / 1266 passed / 1 skipped (the 1 F is
  test_sample_real_drivers_pass, the F-363 darwin case);
  test-room-sim-e2e 75 passed / 1 skipped, exit 0. Both with the
  QE. QE APPROVED R1 at bcc353ed (CM, 2026-10-25): the test-side
  items are met at branch level; worker-4 is drafting the PR body.
  PR #57 OPEN as DRAFT (CM, 2026-10-25) at bcc353ed, body
  cb31c9bb; CI run 40235962276 in progress. PO RULING (2026-10-25):
  (1) AC2 stays in US-174b, amended in place: "verify tolerance is
  AE-ruled; the default or a per-call argument, as the AE+QE
  decide; the suite impact is handled by the QE". AE RULING on AC2
  (supersedes "verify tolerance default 8 -> 3 dB" above): a
  PER-CALL argument, default stays 8 dB. The existing callers
  (verify.py verify_all l.493, runner.py l.344) check the filter
  WAV against its own passband average, and a correct filter
  departs from flat by the correction depth; only the venue closed
  loop (corrected acoustic response vs target) passes
  tolerance_db=3.0, with tests failing at 3.1 and passing at 2.9;
  any other caller verifying a measured response gets its own AE
  ruling. worker-4 is implementing it. Story batch B6f (PM,
  MANIFEST efcdcb2f, on top of B6e, whole-file replace of
  US-174.md) carries the amended AC2. (2) No split: AC3 and AC5
  stay; #57 stays a draft until #55 merges, then the head is
  updated. Re-open trigger: if #55 stalls (blocked review, or CI
  red with no fix in sight), back to the PO for a split.
  AC2 RE-RULED (AE, via CM, 2026-10-25; supersedes the per-call
  AE ruling above): the AE votes worker-4's option (A). AC2 is met
  by the existing 3 dB residual gate on the corrected response
  (closed_loop.max_positive_deviation_db <=
  MAX_POSITIVE_DEVIATION_DB = 3.0), with boundary tests at 2.9/3.1
  dB and the mutation constant -> 8; verify_target_deviation stays
  at 8.0; no new call site and no CLI exit on simulated data. AE
  audio note: gating only positive deviation at 3 dB is intended;
  dips are bounded by the 174b over-cut criterion. B6f was NOT
  applied (CM) and is VOID; B6g follows once the decision is final
  (the CM says when). Pending: the Architect on (A)/(B), the QE on
  (A) (their per-call conditions crossed with the re-ruling), and
  the PO's final scope call. The QE proposed splitting AC2 out,
  then withdrew it in favour of in-place. worker-4 has not touched
  US-174.md (CM). #57 CI run 40235962276 still in progress.
  New backlog item (AE + Architect, P2; 2026-10-25): option (B), a
  verify_corrected_response gate on REAL post-correction
  measurements, in the venue measurement pipeline story; the
  Architect decides its API shape. No ID yet. DROPPED (AE, via CM,
  2026-10-25): (B) is rejected; the real gate is US-174d's
  re-measurement, with the AE setting its tolerance there. Not
  filed.
  AC2 FINAL (Architect, AE agrees, PO condition met; via CM,
  2026-10-25): "Venue closed-loop residual gate (simulated
  scenarios): closed_loop.max_positive_deviation_db of the 1/6-oct
  smoothed corrected response vs target <= 3.0 dB (AE value)."
  verify_target_deviation is a filter-only sanity check; its 8.0
  default stays. Correction: the v138 wording "only the venue
  closed loop passes tolerance_db=3.0" rested on a wrong premise
  and is superseded. Additions: MAX_POSITIVE_DEVIATION_DB moves into
  closed_loop.py as a named constant (174d revisits it on real
  data); a teeth test (a degraded correction with a residual in
  (3, 8] dB fails; the mutation constant -> 8 goes red). PO: re-word
  in place in #57, no split. worker-4 is implementing (A); the QE's
  conditions for (A) are pending. The CM told the PO the constant
  move is a one-line source change against their "test-only"
  clause; the PO may still ask for the split. Story batch B6g (PM,
  MANIFEST 072fba75, on the B6e base at bcc353ed, whole-file
  replace of US-174.md; supersedes the VOID B6f) carries AC2 and
  the 174d real-gate line. B6g was NOT applied; it is superseded
  by B6h (PM, MANIFEST f78e6296, same B6e base at bcc353ed,
  whole-file replace of US-174.md), which adds the QE's A1-A5 to
  AC2. B6h was NOT applied either; it is superseded by B6i (PM,
  MANIFEST b69ab2f5, same B6e base at bcc353ed, whole-file replace
  of US-174.md), which carries the QE's T1-T6 in place of A1-A5.
  The CM applies B6i on top of worker-4's AC2 commit.
  PO FINAL (via CM, 2026-10-25): the constant move is within
  the "test-only" intent; (A) stands, no split (supersedes "the PO
  may still ask for the split"). QE A1-A5 on (A) (via CM,
  2026-10-25; the QE's C1-C3 lapse): A1 the real chain (1/6-oct
  smoothing -> max_positive_deviation_db); A2 mutations constant
  -> 8 and -> 3.2 plus the REQUIRED np.max -> np.mean product
  mutation; A3 the band stated per assert (subs 30-200, sats
  250-500, system 30-500 Hz); A4 the AC text names the constant and
  the function, "verify_target_deviation default unchanged at 8.0"
  and "verified by tests only, no shipped code enforces it"; A5
  counts against 1268/76. worker-4 is implementing it. Option (B)
  is CLOSED, not filed (AE: it duplicates US-174d).
  QE final conditions T1-T6 on (A) (via CM, 2026-10-25; supersede
  A1-A5): T1 the same chain as the gate, with a deterministic
  one-line degradation for the teeth test; T2 three asserts, values
  to 2 decimals; T3 mutations (a) constant -> 8 REQUIRED, (b)
  constant -> 3.2 optional or the margin stated, (c) np.max ->
  np.mean REQUIRED, (d) tests import the constant only, a grep
  shows zero copies in tests/; T4 the band per assert; T5 the AC
  text, plus "enforced by tests, not a runtime gate", and (B)'s
  closure cites 174d; T6 counts against 1268/76.
  Backlog finding (QE, via CM, 2026-10-25; not US-174b): the
  legacy verify paths run_all_checks (verify.py:493) and
  runner.py:390 `--stage verify` have no test coverage at all. No
  ID yet.
  Measurement SNR check (AE, P2, AE-owned; 2026-10-25): US-174b
  shows the correction raises up to +0.67 dB in below-target
  regions at -40 dB noise re peak, clean at -60. The sweep capture
  must estimate SNR and warn or refuse below 60 dB re peak.
  Pushed (CM, 2026-10-25): US-174 head e071452b = US-174b code
  a3bc538c (55 new tests; local 1252 passed / 1 F-363 fail; sim-e2e
  130 passed) plus B6e. Its sandbox check stays red on the new
  tests until #54 merges.
  Existing assets on main: src/room-correction/ (room_correction/,
  runner.py, analyze_measurement.py, gain_calibration.py,
  thermal_ceiling.py, tests/, mock/ with 3 scenarios),
  scripts/generate-room-sim-ir.py, scripts/test/run-room-sim-e2e.sh,
  configs/local-demo/room-sim-convolver.conf,
  docs/architecture/room-compensation.md.
  OLD ROOM-CORRECTION STORIES (PO): US-174 is the umbrella and
  links them; none is closed in this batch (superseded by the PO
  decisions below, recorded in B6). Linked: US-008,
  US-010, US-012, US-013, US-047, US-048, US-049, US-050, US-061,
  US-067, US-090, US-097, US-098, US-101 (list to be confirmed by
  the Architect's mapping). Status of each until the mapping:
  "linked to US-174, mapping pending"; nobody works on them. Per
  story the Architect proposes reuse (becomes a US-174 sub-story,
  maybe re-scoped), supersede (replaced by a new sub-story, with a
  pointer) or done/obsolete (e.g. CamillaDSP-based, D-040); the PO
  decides the supersede/obsolete calls; the PM records them in the
  batch after. US-090 and US-097 (owner-rejected, session 5) STAY
  rejected; their rejection reasons become explicit US-174
  constraints/ACs (Architect extracts, PO checks the wording).
  PO DECISIONS (2026-10-25) on the Architect's mapping: folded into
  174b: US-010, US-008 (sim part; recording into 174c), US-013 (sim
  half; real-room half into 174d), US-098 P1/P2; into 174c: US-047,
  US-061's abort-restores-state AC (restated against D-063);
  SUPERSEDED: US-050 by 174c (remaining Pi items folded in), US-012
  by 174e; US-067 = US-174b2 (own ID; index "= US-174b2"); US-090
  and US-097 stay "rejected" with "successor: US-174e"; the owner's
  rejection reason quoted verbatim in 174e as a constraint (record:
  local-demo broken by auth middleware redirect, F-223; "exactly
  none of those stories have been end to end tested."); their ACs
  are input only, each checked by the PO before it becomes a 174e
  AC. US-101 separate, off the critical path.
  TW one-liner (PO, no hurry): CLAUDE.md says the room correction
  pipeline is "NOT YET WRITTEN", but src/room-correction/ (incl.
  mock/room_simulator.py) exists on main; the text is stale.
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
  is this guard. AD (#50 review): keep F-362 high on the
  post-US-163 list, because it hides the S-001 and D-009 tests.
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
  AC addition (AD L6, #50 review): the web UI and GraphManager must
  not show a zombie sink as "running" or with live levels.
  UX P1 (amps-on, also US-159 G16): a red web UI state "OUTPUT
  DEVICE LOST — USBStreamer not playing. Amps off before recovery.",
  backend-driven (PCM closed or spa.alsa errors), never inferred
  from meters; recovery offered only through the D-063 gate; U8
  order just below CLOSE FAILED. Design follows from UX.
  UX N3 (2026-10-25): add a "routing lost" indicator here. After a
  WirePlumber restart the links drop until GraphManager re-links
  (seen in the 695f69af test, not caused by F-318; = worker-3
  finding a under US-173); until then output is silent with no
  visible cause.
  UX backlog (2026-10-25, from the AE's F-318 note review; not for
  the US-173 batch): show GraphManager's link_audit result in the
  web UI as "Routing OK / ROUTING VIOLATION", so the pre-amps-on
  `pw-link -l` check stops being an eyeball check. A violation is a
  red banner near CLOSE FAILED in the U8 order. Related: N3 above
  and F-361.
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
- Flaky web-ui unit test (worker-5, 2026-10-25): nondeterministic
  PytestUnraisableExceptionWarning in tests/unit/test_collectors.py
  ::TestPipeWireCollectorRPC::test_backoff_resets_on_connect, an
  asyncio _SelectorTransport.__del__ GC race. Does not touch
  room_correction. Low.
- **F-387** Flaky web-ui test teardown (worker-5, via CM,
  2026-10-25; pre-existing; ID per QE N2 on #55): teardown ERROR in
  test_measurement_integration.py::TestGMFullSessionLifecycle::
  test_gm_mode_transitions_during_happy_path. The mock GM returns
  None at session.py:480, then a starlette CancelledError at
  shutdown. 1 in 15 runs at base b0666c02. Low.
- **F-388** Xmax definition in the excursion-mask derivation (P2;
  AE-owned; 2026-10-25; ID at the AE's request): the
  D-031/excursion-mask derivation must record which Xmax definition
  each driver record carries ("mathematical"/overhang vs measured
  linear, e.g. a 10% THD or 70% BL point) and derate a
  "mathematical" Xmax instead of using it as a linear limit.
  Trigger: F-363 corrects PRV 10MR2000-NDY xmax 5.0 -> 7.15 mm to
  the sheet's printed "mathematical" value. Precondition for F-385
  option (i'); related to the fail-closed T/S follow-up under
  F-363.
- **F-389** Pi 5 tryboot with KMS+BT overlays via overlay_prefix:
  no network, needed an owner power cycle (Architect, no QE
  objection; via CM, 2026-10-25). US-172 run 2: run 1 +
  overlay_prefix=o/ + disable_splash=1 turned a 36 s return into no
  return. Details, recovery and the run-3 design under US-172.
  BLOCKS US-172 (Architect, 2026-10-25). Linked: the watchdog
  reliability TODO (CLAUDE.md open questions; BCM2835 watchdog
  failed Tests 3/5 on the Pi 4) and the RuntimeWatchdogSec check
  under US-163 AC5 below.
- Docs (TW; via CM, 2026-10-25): flake test apps run on a /nix/store
  copy of the git tree, so untracked new test files are invisible
  to `nix run .#test-*` until git-added. On darwin, test-web-ui is
  a check (`nix build .#checks.aarch64-darwin.test-web-ui`), not an
  app. Add to docs/guide/howto/development.md.
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
- **F-374** (AE, Medium, sound quality; 2026-10-25) crossover.py
  ignores the profile's `type: linkwitz-riley`:
  `_design_crossover_magnitude` builds "flat to fc, then 24 dB/oct",
  a 0 dB knee, so sat HP and sub LP are both at -0.6 dB at 200 Hz
  (LR4: -6 dB each). Measured on the US-155 files: sat -12.1 dB at
  141 Hz, -0.6 at 200, -0.6 at 283; sub -0.6, -0.6, -12.0; complex
  sum +1.1 dB at 141 Hz, +5.4 dB at 200 Hz, +1.4 dB at 283 Hz. The
  AE's true-LR4 prototype through the same min-phase code (80 Hz
  subsonic kept): each filter -6.0 dB at 200 Hz, sum -0.68..-0.01
  dB over 20 Hz-20 kHz. Not speaker safety (H caps power; D-031
  met). Blocks the AE's sign-off of US-155 AC1 (summation); a
  precondition for US-174b AC3-AC5; recommended before the US-173
  session (else an audible boom at 140-280 Hz). The file sits inside
  worker-4's US-174b fence (src/room-correction/**). Lane (US-173,
  US-174 or its own small PR): pending the Architect, CM relays.
  RULED (Architect, team-lead, CM; 2026-10-25; option (iii)): its
  own branch fix/F-374-lr-crossover off main b0666c02 (pushed), a
  dedicated worker-5, its own PR merged FIRST; US-173 and US-174
  then merge main. worker-5's files: crossover.py, test_crossover.py
  and the type pass-through in generate_profile_filters.py (carved
  out of worker-4's fence). The Architect's earlier "owned by
  worker-3" is superseded. Legacy callers on the old crossover
  alignment (Architect): runner.py:200 (worker-4, switch in 174b
  after F-374) and generate_bose_filters.py:103/113 (switch, or
  retire if obsolete). AE (#55 review, 2026-10-25; P2): before any
  LR profile goes live, verify that the Pi's filters come from
  generate_profile_filters, not from runner.py or
  generate_bose_filters.py.
  Fence (AE, 2026-10-25): F-374 does NOT change combine.py. The AE's
  earlier D-009-scalar instructions to worker-5 belong to F-383 (CM
  relays). F-374 keeps the crossover-level gate (all 4 cases, exact
  digital LR) plus LR4 post-combine through the UNCHANGED combine;
  LR4 already passes there (4.1/7.4 deg, max|H| -0.499 dB).
  STOPPED (worker-5, CM 2026-10-25): with the real LR4 profile the
  post-combine phase AC fails (68.8 deg max, 29.7 deg at fc). Cause:
  the satellite's mandatory 80 Hz subsonic, not the crossover. With
  the Architect and the AE; a new defect is likely (PM assigns the
  ID on request).
  JOINT RULING FINAL (AE 20:32:02, Architect concurring
  20:31:56-20:32:04, 2026-10-25): worker-5's option (a) accepted.
  The post-combine gate uses an in-test copy without the sat HPF,
  thresholds unchanged. NO phase, sum or max|H| test on the real
  Markaudio profile. Its only test is protection-present (AE
  threshold): on the unmodified markaudio profile the sat
  mandatory_hpf_hz is set, and the exported sat WAV is at least
  18 dB below the HPF-removed copy at mandatory_hpf_hz/2; worker-5
  reports the measured value. WITHDRAWN before it reached worker-5
  (Architect): the pinned real-profile guard (+/-1 dB sum, max|H|
  <= -0.5 dB, fc phase <= 30 deg, 0.3 deg margin); it would have
  locked in the defect. A CM-relayed variant (>= 2.5 dB down AT
  mandatory_hpf_hz) is superseded by the Architect's direct
  18 dB-at-half-corner wording (PM asked the CM to confirm what
  worker-5 has). The baseline numbers go in the F-374 PR body and
  in F-385. Regression rule: see F-385 (review rule, not a test).
  The limitation goes in the PR body, no xfails. Deployable for the
  supervised US-173 session (sound quality, not safety). The
  subsonic interaction is filed as F-385.
  OPEN joint ruling (Architect + AE, CM 2026-10-25): the F-374
  post-combine gate, issue 1 (lifting the combine.py per-bin clip).
  RULED (Architect + AE final, relayed to worker-5 by the CM,
  2026-10-25; closes the open ruling above): the post-combine gate
  runs on the no-HPF copy with combine unchanged.
  - Crossover level, unchanged: sum +/-0.05 dB, legs -6 +/-0.5 dB,
    phase <= 5 deg at fc and <= 10 deg over fc/2..2fc.
  - Post-combine interim, RELATIVE to each WAV's plateau: legs -6
    +/-0.7 dB, sum +/-0.7 dB over fc/2..2fc, phase <= 5 deg at fc
    and <= 10 deg over fc/2..2fc; max|H| <= -0.5 dB absolute.
  - The PR body records the +0.6 dB per-bin-clip lift.
  - Tightening is a new F-383 AC (see F-383).
  PR #55 OPEN (CM, 2026-10-25) at 6e05fd64: 3 commits, tests
  1227/1/1; the only failure is F-363. F-363 merges first; #55's T1
  stays red until then. Merge order (team-lead): the F-363 PR (not
  open yet), then #54 (F-365), then #55. Standing consent applies
  at 7/7 on the final head plus green CI.
  Rule 13 on #55 at 6e05fd64 (bundle /tmp/pr55-review-6e05fd64/;
  requests out 21:5x CET; CM posts verdicts verbatim): AE APPROVE;
  AD APPROVE (not covering CI or a later head). Pending: SecSpec,
  TW, QE, Architect, UX. AD note: updating the branch after F-363
  merges voids all approvals and needs a re-review round.
  TALLY (CM-confirmed, 2026-10-25; supersedes "Pending" above; all 7
  posted verbatim, copies /tmp/pr55-verdicts-6e05fd64/): 5/7.
  APPROVE: AE, AD, SecSpec (no veto), Architect, TW. CHANGES
  REQUESTED: QE (evidence only, in the PR body: R1 the bug
  reproduced on base b0666c02; R2 mutants M1-M3, red then green);
  UX U1 BLOCKING (the speaker editor offers 96 dB/oct,
  speaker-config.js:28, and a free-text Type that the generator now
  rejects (LR only, 24 or 48 dB/oct), with no check on save, so a
  venue session fails only at filter generation (CP-5) after all
  sweeps; fix: the editor and the save or session start reject the
  same values, with a test; if the AE keeps 96, the generator needs
  a non-LR route). The CM asked the AE whether 96 must stay and the
  Architect about scope. Every reviewer re-reviews the merge-main
  head after F-363 merges (strict protection).
  Non-blocking #55 notes: Architect N1 (CM wording): the
  phase-at-fc <= 5 deg check extended to LR4 (24 dB/oct). UX N1:
  slope-error tuple wording; UX N2: release note
  "a crossover section without `type` now means LR" (TW). QE N2:
  the web-ui teardown flake is F-387 (cited in the #55 body). QE
  N3: F-383 cites the #55 post-combine test by name (sum margin 0.1
  dB). AD N2: until runner.py and the bose generator are migrated,
  anything naming "the generated files" (F-321) must say which
  generator produced them.
  TW notes (docs, TW-owned): (1) a user-facing profile crossover
  schema section (`type`, slopes 24/48, missing type = LR);
  speaker-management-requirements.md section 4 still shows an
  older list-style schema (`slope: 96`, `type: HP/LP`). (2) A
  one-line clarification "LR magnitude target as min-phase FIR, not
  LR IIR" in CLAUDE.md Critical Design Decisions 1, D-001,
  design-rationale.md and user-journeys.md. (3) F-374, F-383 and
  F-385 exist only in this backlog: no defect records or
  defects-index rows on main; closing F-374 on merge needs the usual
  tracking batch.
  #55 RULINGS (via CM, 2026-10-25): AE: 96 dB/oct does NOT stay; the
  editor offers 24/48 only, and type is fixed to linkwitz-riley; a
  non-LR alignment would be a new story. Architect: the U1 fix goes
  INTO #55 (worker-5): save-time validation calls the generator's
  own check (single source), plus a JS/Python parity test, a sweep
  of every shipped profile, and no crash or rewrite for stored bad
  values. Architect N1 (LR4 phase-at-fc) and UX N1 go in the same
  head; F-387 cited in the body. Joint AE + Architect (replaces
  "no guard on the real profile"; supersedes AD L1's "loose-bounds"
  test below): a real-profile REGRESSION CEILING of phase <= 35 deg
  at fc and <= 75 deg over fc/2..2fc, sum +/-1.0 dB re plateau, and
  max|H| <= -0.5 dB (hard). Only F-383/F-385 may tighten it;
  relaxing it needs joint AE + Architect approval.
  U1 UX gaps, same head (UX via CM, 2026-10-25): G1 a stored invalid
  slope or type shows as a selected, disabled "(not supported)"
  option with an inline note, never silently 24 or linkwitz-riley;
  save stays 400. G2 the generator check runs at measurement-session
  start, before gain calibration, and refuses to start with its
  message. Nice-to-have: Filters Generate returns 400 instead of
  500. worker-5's fence adds session.py and filter_routes.py
  (disjoint from all open branches, CM checked).
  QE R1/R2 ACCEPTED (via CM, 2026-10-25): R1 on base b0666c02, 3 of
  4 gate tests red with numbers; R2 mutants M1 3 red, M2 7, M3 4;
  post-revert 1227 passed / 1 F-363 / 1 skipped. QE REQUIRED, same
  head: the M1 second net, one assertion through
  generate_profile_filters that the LR output differs from legacy,
  and M1 must turn a TestCrossoverTypePassThrough test red. QE
  non-blocking: N1 the real-profile ceiling (AE + Architect numbers,
  above); N2 the web-ui teardown flake is F-387 (PM, already
  allocated); N3 F-383 cites the +/-0.7 test. worker-5's interim
  aec7b604 (Architect N1 LR4 phase <= 5 deg, UX N1 wording) is not
  pushed; it goes into the complete head.
  FENCE QUESTION (worker-5 stopped; via CM, 2026-10-25): 3 web-ui
  fixtures use LR slope 96; proposal 48, pending the Architect and
  AE. The 422 (save) vs 400 (Generate) split is with the
  Architect. The rest of the head is green and uncommitted on top
  of aec7b604.
  #55 backlog (worker-5, via CM, 2026-10-25; not in #55): (a)
  session/CP-5 load the repo configs while the editor prefers
  /etc/pi4audio; (b) workshop-xrk10f-fullrange has no crossover
  and cannot be saved (unknown filter_type "fullrange";
  pre-existing); (c) /validate, check-mode and activate do not run
  the crossover check yet.
  FENCE ANSWERS (via CM, 2026-10-25): AE: 96 -> 48 is correct (LR8,
  as in meh-3way). Architect: the fence extension is OK for slope
  only; frequencies, delay_ms, enclosure_type and all assertions
  stay unchanged; the commit message says "fixture encoded LR96,
  rejected since F-374 (AE ruling); value incidental to the test".
  REQUIRED in #55: a negative U1 route test, LR 96 on save gives
  422 + error=="validation" + the generator's message verbatim, and
  a non-LR type is rejected too. 422 on save (existing
  speaker_routes contract) and 400 on Generate are OK; detail shows
  verbatim in the editor (UX checks under G1). Aligning the codes
  is out of scope; UX may backlog it. worker-5 is cleared and
  working.
  #55 backlog (AD, 2026-10-25): L1 a loose-bounds regression test
  on the real, unmodified markaudio profile (sum, max|H|, phase),
  tightened with F-385/F-383. L2 default_profile.yml has no
  crossover `type`; with "missing = LR" it changes silently once
  runner.py is migrated: add `type` when runner.py and the bose
  generator are migrated, and document the default in the schema
  docs.
  #55 backlog (AE, 2026-10-25; verdict
  /tmp/pr55-review-6e05fd64/AE-verdict.md): the D-009 max|H| test
  in test_generate_profile_filters covers only 20 Hz..20 kHz;
  extend it to 0..Nyquist and also assert it on the real markaudio
  WAVs, not only the HPF-removed copy. P2, AE-owned.
- **US-175** F-318 layer 2: GraphManager removes any link to the
  USBStreamer that it did not make itself (SecSpec's second
  required layer; team-lead, 2026-10-25). Its own item and its own
  owner: NOT worker-2, whose one mission is US-172. The gig blocker
  that keeps F-318 open (SecSpec accepts layer (a) alone only for
  the supervised home-lab session). File boundary: Rust
  src/graph-manager only, disjoint from worker-4's US-174b fence
  and US-173's F-318 WP files. Owner unassigned. Team-lead pauses new
  workers because of the Mac disk (5.0 GiB free, CM, 2026-10-25).
  NEW requirement (Architect + AE, CM 2026-10-25): GM detects node
  and port re-creation and restores the mode's links. AE safety
  conditions:
  - (a) A WP restart destroys and re-creates the USBStreamer node,
    so it is a USBStreamer interruption: announce it, and the amps
    rule applies as for a PW restart. TW adds this to safety.md
    (PM relayed to the TW).
  - (b) GM's automatic re-link comes back with the D-063 gate
    CLOSED and the gains unchanged or at 0. It never resumes audio
    on its own; reopening is an explicit operator action.
- **F-383** (Architect, AE; 2026-10-25) combine_filters: the D-009
  magnitude clip plus the minimum-phase re-synthesis destroys the
  LR8 crossover phase (76/64 deg HP/LP over fc/2..2fc, sum down to
  -0.94 dB); LR4 is within limits. Blocks deploying any LR8 profile
  (8 in-repo profiles); does NOT block the first DJ session (LR4,
  markaudio-ultimax). Sequenced after F-374. Owner: a new worker
  (team-lead); this entry is their authoritative brief. Causes
  (worker-5): the -200 dB log floors in combine and
  dsp_utils.linear_to_db (about 40 deg); the D-009 per-bin clip
  (another 20-35 deg).
  FINAL mechanism (Architect + AE; supersedes the earlier scope
  note): convolve correction x crossover (x subsonic) directly, then
  truncate and fade as today, then apply ONE scalar D-009 gain (peak
  -0.5 dB at 4x oversampling). No cepstral re-synthesis. Fail closed:
  run the minimum-phase check on the output and raise if it fails;
  a test feeds a non-minimum-phase correction input.
  Min-phase check (Architect + AE): energy of (h - minphase(|H|)) <=
  -40 dB re energy(h), AND the last 5% of taps <= -60 dB re peak
  (the 174b gate thresholds); either failing raises. The reference
  minphase(|H|) is computed cepstrally with a 1e-20 floor and at
  least 4x zero-padding (else it carries the DC-zero/floor error
  that broke LR8 and rejects correct filters). Calibration first: a
  dirac correction x each of the 4 bilinear LR cases (LR4/LR8 x
  80/200 Hz) must PASS the output check with margin; the measured
  values are recorded in the test. Fallback if any calibration case
  is above -46 dB: run the fail-closed min-phase check on the
  CORRECTION input before the product, and make the output
  min-phase check report-only for the LR legs (bilinear LR is
  min-phase by construction). The tail check stays fail-closed on
  the output in every case.
  ACs (AE + Architect): LR8 post-combine HP/LP phase difference <=
  5 deg at fc and <= 10 deg over fc/2..2fc, at 80 and 200 Hz, on
  read-back float32 WAVs; sum +/-1 dB and fc level -6 +/-0.5 dB,
  both relative to the -0.5 dB passband plateau; max|H| <= -0.5 dB;
  the applied scalar logged per channel, with a warning if any
  channel's scalar deviates from -0.5 dB by more than 0.1 dB (AE
  condition, moved here from F-374); tail check as above; full
  room-correction and web-ui runs.
  NEW AC (Architect + AE, 2026-10-25, from F-374; the Architect's
  named OK for the test change): once the scalar gain replaces the
  per-bin clip, tighten the F-374 post-combine gate to legs -6
  +/-0.5 dB relative and sum +/-0.1 dB relative.
- **F-384** (Architect; AE confirms the priority; P1; 2026-10-25)
  correction.py step 9 (main b0666c02,
  src/room-correction/room_correction/correction.py:130-143): the
  post-output D-009 re-clip clips the rfft magnitude per bin and
  keeps the OLD phase, so the output is no longer minimum-phase.
  Live under F-383's mechanism (its fail-closed check would trip on
  it). Fix before or with F-383.
  STAFFING RULED (team-lead, 2026-10-25; supersedes the owner lines
  above and the Architect's options): F-383 and F-384 are ONE
  mission for one new worker, starting after US-174b merges
  (correction.py stays in worker-4's lane until then). Architect:
  keep them as separate items (not merged). F-384 AC (Architect):
  after the overshoot re-clip, the correction output passes the
  same min-phase gate (residual <= -40 dB, tail <= -60 dB), with a
  test that forces the overshoot branch; the web-ui tests pass
  unchanged (frozen function; only this branch's behaviour
  changes).
  Data (worker-4, at the Architect's request, 2026-10-25; US-174b
  closed loop at a3bc538c): after the step-9 re-clip (old phase
  kept) generate_correction_filter overshoots its own -0.5 dB D-009
  margin. Intermediate correction FIR peak: -0.35 dB (home_lab
  sat_left), -0.41 dB (small_club sat_left), up to 0.15 dB over.
  Deployed combined files: -0.57 to -0.60 dB in all 4 scenarios
  (pass D-009). LATENT, not live (Architect; supersedes "live"
  above): both callers (venue_pipeline, web-UI filter_routes) go
  through generate_profile_filters/combine, which re-synthesizes
  min-phase; combined residual vs min-phase -61 dB (sats), -265 dB
  (sub), limit -40. Test impact: the US-174b test asserts the
  intermediate at <= 0 dB, with a TODO to tighten to <= -0.5 dB
  once F-384 lands. Staffing suggestion (Architect): worker-4 fixes
  it as its own commit or small PR; CM and team-lead decide. Until
  they do, the team-lead one-mission ruling above stands.
  DECIDED (team-lead, 2026-10-25): the Architect's suggestion was
  considered and DECLINED. The ruling stands: F-383 and F-384 are
  one mission for a new worker after US-174b merges; worker-4 stays
  on US-174b.
  New AC (AE, #55 review, 2026-10-25; P1 with F-383): an LR8
  post-combine gate on at least one 80 Hz PA profile; today LR8 is
  ungated at 76/64 deg phase. No LR8 profile goes on amps before
  that gate exists.
- **F-385** (P1; AE-owned, Architect co-review; 2026-10-25) "D-031
  subsonic vs crossover phase interaction". Origin: F-374, where
  the sat's mandatory 80 Hz subsonic gives 29.7 deg at fc, the whole
  <= 30 deg sat-sub budget at 200 Hz. D-031 is NOT moved or removed
  for phase reasons alone. Options as the AE finalised them
  (Architect concurring, 2026-10-25):
  - (i') D-031 becomes a per-driver excursion mask |H_sat(f)| <=
    mask(f), derived from Xmax at full amp output (F-363 T/S
    records), asserted fail-closed on every exported sat WAV. A
    subsonic is added only where the crossover HP violates the
    mask, at the lowest order and corner that satisfy it. Preferred.
    Precondition: F-388 (Xmax definition, AE).
  - (ii) A lag allpass on the SAT leg (an allpass can only add lag;
    never the sub). Not min-phase, so it conflicts with F-383 and
    needs the Architect's scoped exception. Low preference.
  - (iii) Documented limitation as the interim state.
  - (iv) A deliberate electrical sat delay (~0.4 ms at fc), which
    needs a defined offset in 174b's +/-0.2 ms delay AC.
  - Rejected: a fixed fc/4 subsonic rule (BW4 at 50 Hz still adds
    about 38 deg at 200 Hz).
  - Sequencing: after F-383. 174b alignment is not judged on this
    profile until (i') lands.
  - The AE derives the mask once the CHN-50P record is final.
  - Baseline (F-374, real markaudio 200 Hz LR4 profile): 29.7 deg at
    fc, 68.8 deg max, sum -0.68..-0.01 dB, max|H| -0.60 dB; also in
    the F-374 PR body.
  - Review rule (Architect + AE, 2026-10-25): if F-383 or any later
    change makes the baseline worse, the AE and the Architect both
    rule before it proceeds (joint STOP). A review rule, not a test
    assertion; no pinned guard exists.
  - Superseded wording: the first relayed direction ("no allpass
    compensation", delay fallback dropped) and the CM's amendment
    without (iv); the Architect's direct message re-lists (iv) as
    the AE's.

## P2

- **Stale HP/IEM routing docs** (AE, docs, P2; AE review; folded per
  team-lead, 2026-10-25). docs/architecture/graph-manager.md section
  5.3/5.4 (0e0cbd38, same on main; lines ~164-195) still documents
  the pre-D-063 "Mixxx HP --> USBStreamer direct" and "Reaper
  HP/IEM --> USBStreamer direct". The code is authoritative
  (src/graph-manager/src/link_audit.rs:21-24): HP/IEM route through
  the convolver (Dirac passthrough); any direct USBStreamer link is
  a violation. Contradicts the F-318 operator rule ("only
  pi4audio-convolver-out may feed the USBStreamer"). Update the
  section 5 routing tables and link counts. Same item: the project
  CLAUDE.md IEM lines (Owner Preferences "IEM signal path ...
  bypasses convolver entirely", ch 6-7; Design Decision 2 "the
  singer's IEM path bypasses the convolver entirely"). AE-verified
  wording: HP/IEM routed through the convolver per D-063, channels
  7-8 to match the channel table. Owner TW: one docs PR, normal
  Rule 13 review. CLAUDE.md is the owner's file: team-lead tells the
  owner; if the owner objects, that part waits. Team-lead has told
  the owner (2026-10-25); nothing more to send. Not urgent. Needs
  AE review (AE, via TW, 2026-10-25).
- **SETUP-MANUAL `aplay -l`** (AE, via TW, 2026-10-25; docs, small):
  SETUP-MANUAL.md:530 and :1845 still use `aplay -l`, which does
  not exist on the image (no alsa-utils). Replace with `cat
  /proc/asound/cards` as in the F-318 batch's section 14 fix. Owner
  TW.
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
- nixos-upgrade.md §8.5 card-reader recovery (UX P3, TW): step 2
  says to pick the newest present generation other than the one
  that just failed; step 3 names where the off-Pi copy of
  config.txt/MAP.txt is kept (save one after each deploy). UX P3
  (#50 re-review): state up front that card-reader recovery step 3
  needs the Mac with the repo checkout. TW: in the first docs PR
  after #50 merges.
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
  fix is decided then, not waived. Re-found by worker-4 (2026-10-25)
  on main b0666c02 in the US-174 worktree before any edits (1
  failed, 1197 passed, 1 skipped); filed as F-378, withdrawn as a
  duplicate. Can block T1 on the US-174 PR as well; not fixed there.
  Routed to QE (classification, owner). QE RULING (2026-10-25):
  Medium, P2; test and data fixed together as ONE item, outside
  US-174. Test (required): (1) deterministic: sorted() iteration and
  ALL records (2346) via validate_all_drivers (check_files=False);
  if runtime is an issue, a fixed named list, never slicing
  directory order; (2) report every failing record. Data
  (required): (3) check Purifi against its datasheet (the record's
  datasheet_file, v0.91) and correct the wrongly scraped field; if
  the datasheet itself is inconsistent (rounding), keep its values,
  note it in ts_measurement_notes with the quote, and add a
  documented per-record exemption mechanism (not a skip); (4) do NOT
  widen the 10% tolerance (validate_driver.py:313); (5) fix any
  other records the full set surfaces under the same rule in the
  same PR (expect more than one; check the other 36386c75 records).
  QE approval evidence: the full-set test passing locally and in CI
  with the validated-record count in the output; a mutation check
  (the bad Purifi triple back -> fails naming the record); a
  datasheet citation per corrected record. Why only Medium: no
  safety or production-path impact (room-correction tooling only),
  but it can fail T1 at random for any PR. It passed in CI on #50
  (1198 passed) only by directory order.
  US-174 T1 (QE): NOT a pre-gate. US-174 changes nothing under
  configs/drivers or the tested code, so CI picks the same sample as
  main. If US-174's T1 is green, no wait; if it goes red on this
  test, the failed job blocks and US-174 waits for the F-363 fix and
  rebases onto it. Never a skip, xfail or tolerance change for this
  test inside US-174. A local failure of this one test does not void
  worker-4's local T1 evidence, if every other test passes and the
  evidence names it as F-363. Owner: someone other than worker-4
  while US-174 runs; disjoint files (test_driver_validation.py +
  driver.yml records), parallel branch OK; the CM checks the shared
  working directory sequencing. CM: urgent for #52 and the F-374 PR
  (a CI failure blocks under Q2). Owner: the CM finds one. OWNER
  (CM, 2026-10-25): worker-6, branch fix/F-363-driver-validation off
  b0666c02 (test_driver_validation.py + configs/drivers/**), briefed
  with the QE ACs above. QE (2026-10-25): worker-6 has the QE's
  approach OK; the full-set scan finds 29 failing records of 2345.
  The US-174 head 0b412fde changes nothing under configs/drivers or
  src/room-correction vs main b0666c02, so the US-174 T1 ruling
  above stands.
  New evidence (QE, 2026-10-25): test_sample_real_drivers_pass is
  red on darwin (Purifi sampled) and green on aarch64-linux CI (run
  40232728057, same drv 909sn50k), so it hid F-363 from Linux CI;
  it only ever covers 20 of ~2345 records. Fix inside the F-363 PR
  (worker-6): delete it in favour of the full-set test, or sort it.
  Medium; closes with the F-363 PR. No new ID (QE): it stays under
  F-363 (same test as the title and AC (1)). F-380 step 1
  follow-up: grep the test suites for other unsorted
  iterdir/glob/listdir slicing.
  QE requests to worker-6 (relayed by the CM, 2026-10-25): R-a
  delete the order-dependent sample test (preferred) or sort it;
  R-b the mutation reds come from the full-set and exemption tests,
  naming the red test per mutation; R-c Linux CI evidence that the
  full-set test is red before the fix.
  PR #56 (CM, 2026-10-25): github.com/ela2342/mugge/pull/56, head
  f4d92a6e, tests only. R-a done: the sample test is deleted in
  favour of the full-set test. R-c: CI run 40234711016 is in
  progress at that head and must come back red (local: 5 failed /
  52 passed). The data fix 4afb8235 is pushed only after the run
  finishes (a push cancels the running job). QE scope: the qms
  comma records sb-acoustics-mt19cp-8 and visaton-paw-46-8 go IN,
  plus a plausibility-bound test (bounds from the AE), as a third
  commit. Then worker-6 merges main dfdbbbd6 on top (base b0666c02
  is 7 commits behind, no file overlap); that is the final review
  head. R-c RESULT (CM, 2026-10-25): run 40234711016 at f4d92a6e is
  RED as required (5 failed / 1203 passed / 1 skipped, only the
  full-set and exemption tests). Data fix 4afb8235 pushed; the
  body links the run. worker-6 is on commit 3 plus the main merge.
  Follow-ups outside worker-6's fence (QE and AE via worker-6,
  2026-10-25; not in the F-363 PR):
  - Re-scrape risk (QE): the driver scrapers would undo the F-363
    datasheet corrections; scrape_loudspeakerdatabase updates
    existing records, scrape_soundimports overwrites them.
  - Two parallel validators (QE): src/room-correction/
    validate_driver.py and scripts/drivers/validate_drivers.py; the
    CLI one still flags records exempted in the F-363 test.
  - Fail closed (AE condition): any code that derives safety
    parameters from driver T/S (D-031 mandatory_hpf_hz, excursion
    mask, alignment, speaker_sim) must fail closed on a record
    marked metadata.ts_consistency: datasheet-inconsistent, unless a
    measured T/S override is present. The F-363 PR only adds a test
    that no profile under configs/ references a marked record
    today. AE-owned; P2 (AE confirmed, 2026-10-25). The F-363
    configs/ assertion is the interim guard. Scope widened (AE,
    2026-10-25; supersedes "datasheet-inconsistent" above): fail
    closed on ANY record with a ts_consistency mark (today
    datasheet-inconsistent and unverifiable), so future mark values
    are covered automatically. Related: F-388 (Xmax definition).
  - Dual-voice-coil Re (AE, P3): Earthquake/Image Dynamics records
    store series Re as if per-coil; the IDMAX10D2 Re 3.44 is in no
    manufacturer document. AE-owned. Detail (worker-6, 2026-10-25):
    the Earthquake DBXi-12D/15D and Image Dynamics V4 records seem
    to hold the series (both-coil, about 2x per-coil) Re. Scope:
    settle the per-coil vs both-coil Re convention for dual-coil
    records, then re-check those Re values and the IDMAX10D2 3.44.
    Kept out of the F-363 PR (AE). No ID yet, like the other
    follow-ups here.
  - Retailer T/S source (AE, P3; via worker-6, 2026-10-25): add a
    retailer value (e.g. "retailer") to the ts_parameter_source enum
    in validate_driver.py and TEMPLATE.yml. accuton-c173-11-191 is
    corrected from a retailer page only, recorded today just in
    ts_measurement_notes; the enum has only manufacturer and
    measured-*. AE-owned; not in the F-363 PR.
  - Decimal-comma parse bug (QE, P2 until worker-6's scan is in):
    datasheet ingestion read European decimal commas wrongly;
    accuton-c173-11-191 stored Qts 34.0 / Qms 527.0 where the
    retailer page prints "0,34" / "5,27". Other records from the
    same source may be affected (worker-6 scanning). AC: a parser
    test with comma decimals plus a Qts/Qms range sanity check in
    the data tests. QE-owned. Update (CM, 2026-10-25): the qms
    comma records sb-acoustics-mt19cp-8 and visaton-paw-46-8 and
    a plausibility-bound test go INTO PR #56 (QE scope, AE
    bounds); see the #56 paragraph above.
  - Coast record (AE + QE final, via CM, 2026-10-25): KEEP, marked
    ts_consistency: unverifiable (a separate value from
    datasheet-inconsistent); stored values unchanged. The QE owns
    the exemption mechanics. Open (AE, PM question): whether the
    fail-closed rule above also covers "unverifiable". ANSWERED
    (AE): yes, see the widened scope above. Addendum (AE + QE, via
    CM): the exemption test still asserts the exact error string,
    and mutation (e) flips unverifiable to datasheet-inconsistent
    and must go red.
- **F-379** (worker-4, Architect ruling; 2026-10-25) Web-UI
  correction level defect: src/web-ui/app/filter_routes.py:231 calls
  correction.generate_correction_filter directly, with no IR level
  normalization, so the cut depth follows the absolute IR level (a
  +12 dB mode is cut 29 dB at x1, 9 dB at x0.1, 49 dB at x10).
  US-174b adds correction.normalize_ir_level(...) and a max_cut_db
  kwarg, but the web-UI path stays unfixed. Related: the step-9
  phase handling in correction.py is F-384 (Architect via
  worker-4). Lane: worker-2 + AE (it
  changes web-UI outputs). Rating: AE (pending). Update (CM,
  2026-10-25): stays in the backlog for a later worker, not
  worker-2.
- **F-380** (worker-7, Architect ruling: its own item; 2026-10-25)
  "CI builds no checks.*. Step 1: audit which checks.* currently
  build red (read-only, eval + build on the Mac/linux-builder).
  Step 2: a ci.yml step building the green ones, with red ones
  tracked as defects." Owner QE, sequencing CM. Known red:
  checks.test-room-correction (red on main since 9643be2a/TK-189,
  yml cp before chmod; fix on chore/rc-check-configs) and
  checks.test-midi (both F-365). Until it lands, the room-correction
  merge gate stays the app variants CI already runs. Note: worker-3's
  ci.yml T1 step (US-173) and step 2 both touch ci.yml; the CM
  sequences them. The Architect approved the QE's audit plan (QE,
  2026-10-25). QE finding: no Rule 13 approval on #49, #50 or #51
  cited an unbuilt checks.* result as CI evidence; the Architect
  waived checking #27-#38. Step 1 HELD (CM decision) until worker-7's
  chore/rc-check-configs PR merges and the Mac has at least 8 GiB
  free; then team-lead spawns worker-8, building from the pinned
  main ref with no worktree.
  Added (CM, 2026-10-25): a CI step for
  checks.aarch64-linux.wireplumber-no-bypass plus a development.md
  line (US-173 worker-3 finding c) belong here, not in US-173; the
  earlier "worker-3's ci.yml T1 step" note is superseded for that
  step. CM, 2026-10-25: worker-3's ci.yml T1 step and the
  development.md command line move from US-173 to F-380 (text to
  follow from worker-3). QE conditions on this move (CM,
  2026-10-25): (1) US-173's evidence is one sandboxed
  aarch64-linux build of the wireplumber-no-bypass check with the
  -L log plus the negative control (Pi route or scratch dispatch);
  (2) F-318 is not closed or amps-on-cleared until F-380 has that
  check gating in CI. Superseded (QE ruling, 2026-10-25): run
  40232728057 IS F-365's Linux leg; step 1 is still required for
  permanent gating (a later Linux failure reopens F-365 at High).
  Step 1 also greps the test suites for other unsorted
  iterdir/glob/listdir slicing (QE, F-363 follow-up).
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
- safety.md pre-flight checklist (QE, AE via team-lead): add "amps
  on last, amps off first". (TW)
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
- PytestCacheWarning "Permission denied" in both nix test apps
  (Low; worker-4 via CM, 2026-10-25): pytest tries to write
  .pytest_cache into the read-only /nix/store source; also in CI
  run 40234711016. Proposed fix: `-p no:cacheprovider` in the
  flake.nix app wrappers.
- Pi 5 WiFi/BT firmware missing (brcmfmac, BCM4345C0). Note: wlan0 was
  the fallback path during the 20:13 eth0 drop (P2 item), so NixOS
  currently has no wireless fallback. P3 (worker-1).
- No vcgencmd on the Pi 5 image, so no get_throttled evidence for T50
  and gig thermal checks. P3 (worker-1). Fix (Architect): add
  `libraspberrypi` (in pinned nixpkgs, evaluates for aarch64-linux;
  needs /dev/vcio) to the Pi 5 system packages. Not US-163.
  Re-raised (Architect, via CM, 2026-10-25): add raspberrypi-utils
  / libraspberrypi to the Pi 5 closure as a diagnostic tool
  (vcgencmd, vclog). Not part of US-172.
- mugge.cachix stays OFF the Pi 5 (SecSpec + Architect, via CM,
  2026-10-25). Adding it would be a substituter config change; not
  done ad hoc. The Pi substitutes from cache.nixos.org only;
  anything else it needs is built there (F-365 fallback rules).
- Nix on the installer is nixpkgs 2.31.2, below the 2026-10-13
  advisory fixes (2.34.9/2.35.3). If the final systems ship it too:
  bump nix.package or nixpkgs. LOW for now (local nix-daemon only, ela
  is root-equivalent); revisit before multi-user or amps-on use.
  (SecSpec)
- Mac disk nearly full (6.0 GiB free on 2026-10-24, falling slowly,
  CM). Clean up Nix store / old worktrees before heavy local builds.
  Also: a failed build grew the Mac store by 16 GiB vs 6.6 GiB
  expected; find out why (CM). Update (worker-2, 2026-10-25): 5.5
  GiB free (the CM brief said ~7.3); builds and caches getting tight.
  Filed as F-377, withdrawn as a duplicate of this item. CM df
  (2026-10-25): 5.1 GiB free, 99% used; later 5.0 GiB. Team-lead
  pauses new workers because of it. CM df later on 2026-10-25: 4.9
  GiB. F-380 step 1 waits for at least 8 GiB free. Later (CM): 4.7
  GiB. Later (CM, 2026-10-25): 4.0 GiB, AT the CM's line: no new
  worktrees or builds (backlog commits continue). Team-lead
  accepted the stop; the owner was asked to free space. Pytest-only
  runs continue; the CM asked the Architect and QE whether queued
  Mac builds can run on the Pi. CM measured 3 GiB free
  (2026-10-25), BELOW the 4 GiB line: still no new worktrees or
  builds; backlog commits continue. Later (CM, 2026-10-25): 3.3
  GiB; later 3.2, 3.4, 3.2, then 3.1 GiB (CM, near the 3.0 GiB
  abort line). Only worker-4's cleared
  US-174b nix runs (abort below 3.0 GiB). Later (CM, 2026-10-25):
  2.95 GiB, BELOW the 3.0 GiB abort line: worker-4's US-174b nix
  run is HELD; pytest in the dev shell continues. Nix GC is banned
  below 4 GiB; freeing space is the owner's call (CM reported it to
  team-lead). Later (CM): 2.9 GiB, still falling with no team job
  running; the hold stays. Later (CM, 2026-10-25): 2.69 GiB. Cause
  (CM, read-only checks): worker-3 ran a `nix build` (US-173 Gate-2
  selftest, 22:27 CET) during the hold (told: no more); the
  linux-builder qcow2 is 29 GiB and grows on the Mac disk;
  softwareupdated has been running ~40 min. With team-lead and the
  owner; the CM has no sudo. Later (CM): 2.5 GiB; worker-3's
  22:27 CET nix build is still running and the CM lets it finish.
  It finished at 22:31:42 CET; disk recovered to 2.8 GiB, still
  below the 3.0 line, so the hold stays (CM). Deviation for the
  record (CM, 2026-10-25): during the hold worker-3 deleted their
  own temporary nix store paths (~430 MiB); the CM asked for
  details and set "no store delete/GC without CM clearance".
- Compact or cap the Mac linux-builder qcow2
  (/var/lib/linux-builder/nixos.qcow2): it grows with VM writes and
  never shrinks (19 -> 24 GiB, virtual 30 GiB, in one RT kernel build;
  Mac free 16 -> 4 GiB stopped CM-MAC-BUILD-2 run 2 at 20:58Z on the
  5 GiB line; owner lowered it to 2 GiB for that build). Fix lives in
  the owner's nix-darwin linux-builder config, not mugge.
  Owner-requested, not blocking (CM). Update (CM, 2026-10-25):
  now 29 GiB. Low gap: the qcow2 grows without bound, so any
  aarch64 build eats Mac disk for good, and nothing in our disk
  rule (abort lines, GC ban below 4 GiB) covers the image itself.
- **F-365** Hermetic nix checks broken in the sandbox (pre-existing; found in
  T57 by worker-1; CI never builds checks.*): checks.<sys>.test-midi
  (../../../configs resolves to /), test-room-correction (cp
  Permission denied on test_camilladsp.yml), test-web-ui (speaker
  YAMLs missing, graph_manager_client not importable). Owner QE;
  filed by worker-1, pending the drvPath-vs-main proof that it is
  pre-existing. Update 2026-10-25: test-room-correction is red on
  main since 9643be2a/TK-189 (yml cp before chmod); worker-7 fixes
  it on chore/rc-check-configs (Architect's flake prerequisite,
  copies configs/ into the check; Architect OK pending; commit 1
  d86451eb pushed, CM 2026-10-25; open as PR #54, head 320c3ae6,
  red on the F-363 test until F-363 merges; needs aarch64-linux
  evidence before merge (QE); CM asked the Architect to choose a CI
  step, a Pi 5 build or a later local build). Pi 5 native build
  approved (Architect, QE) with conditions: sandbox=true, a dry-run
  that builds only the check, the thermal rules, and a rerun on the
  merged head after F-363. Queued behind worker-2's CHANGE session
  (CM). CM-CHG-.89-F365 (worker-7) ABORTED safely at the clone step:
  the Pi has no git. Cleanup verified, session released. worker-7
  prepares a git-archive tarball plus a path: flake run with a
  drvPath equality gate; re-grant pending worker-7's revised scripts
  (CM). Pi fact: mugge.cachix is
  not configured, only cache.nixos.org.
  v2 run (CM, 2026-10-25): drvPath gate PASSED (909sn50k, Mac =
  Pi); STOPPED at the dry-run gate: 40 derivations to build
  (camilladsp Rust + crates, python camilladsp, testPython, the
  test) because mugge.cachix is not on the Pi. Cleanup clean,
  session released. RULING (Architect): option (a), a native Pi
  build of the 40 derivations; amends the earlier "no dependency
  source builds on the Pi". (c) rejected: drvPath identity is not
  a pass on aarch64; adding mugge.cachix to the Pi is a substituter
  config change, not done ad hoc. Conditions: --max-jobs 1 --cores
  2; thermal STOP at 80 C, one resume below 60 C, a second STOP is
  reported; progress to the QE every 30 min; audio stack untouched;
  outputs kept for follow-on builds. QE concurrence pending;
  worker-7 prepares v3.
  SUPERSEDED (CM-confirmed, 2026-10-25; replaces the option (a)
  RULING above): the Architect and QE converged on option (c). The
  PR body records drvPath 909sn50k (the identical build recipe on
  both platforms) and the darwin counts 1/1197/1; CI green at the
  merged head. The Linux leg is deferred to F-380 step 1; a Linux
  failure there reopens F-365 at High. (a), the Pi-native build,
  is a fallback only (its conditions above apply if used). CM
  option: a scratch-branch workflow_dispatch on the ARM runner that
  builds only that check (not release.yml). CM, 2026-10-25: the
  Architect withdrew (a) to fallback-only and took the QE's (c)
  with the QE's conditions (Architect's own words to the QE); the
  "(c) rejected" in the RULING above is void.
  QE fallback conditions for (a), for the record (only if the
  fallback is ever used): (1) sandbox=true recorded; (2) full -L
  log, compared per test with worker-7's darwin state file at
  320c3ae6; (3) a rerun at the merged head after F-363, with GC
  roots removed afterwards; (4) no overlap with US-172 H1; an
  interrupted build restarts at the dry-run gate; (5) WP canary:
  the 16 gains still 0 and the gate closed, besides the pids and
  links; any change = STOP to the QE and Architect.
  Scratch ARM check (CM, 2026-10-25): scratch/f365-arm-check =
  0e56bd4d (ci.yml only, dispatch-only, cachix skipPush), run
  github.com/ela2342/mugge/actions/runs/40232728057, in progress;
  expected red on F-363 alone. The CM deletes the branch after the
  result. worker-7's F-365 v3 Pi scripts are shelved, unhashed
  (fallback only). RESULT (CM, 2026-10-25): GREEN, 1198 passed / 1
  skipped, not the expected red on F-363 (explained by F-363's
  order-dependent sample, see there). The QE is ruling; worker-7
  updates the #54 body; the scratch branch is deleted. QE ruling
  (2026-10-25) for the #54 body: the counts side by side, F-380
  still required, and this run named as F-365's Linux leg. The CM
  updates #54 once worker-7 sends the final sha1. Posted (CM,
  2026-10-25): #54 body at 7cc2890f, QE-confirmed against the
  ruling. Two final edits with worker-7: "first entry" becomes
  "among the first 20 entries", plus the sandbox record "Sandboxed
  build: the build dir is /build (CI log l.1787, 1912), the Linux
  sandbox default". Then the QE text-approves; that approval carries
  into the seven-reviewer re-review after F-363 (update-branch
  voids the approvals anyway). FINAL (CM, 2026-10-25): body posted
  at ac0072af and QE text-APPROVED; posted text matches the file
  (trailing newline aside); head unchanged at 320c3ae6. Correction
  (worker-7, QE checked): the "(CI log l.1787, 1912)" quote above
  is superseded. Those lines are camilladsp dependency builds; the
  check's own line is l.1951 "test-room-correction> rootdir:
  /build/src/room-correction". The bullet now reads "(CI log
  l.1951; also l.1787, 1912 for camilladsp)".
  Pi build queue (Architect, 2026-10-25): F-365, then the F-374
  PR-head suite, then the wireplumber-no-bypass check; each from a
  tarball at the declared SHA with sandbox=true. WP check
  post-condition: live PW/WP pids unchanged, no new USBStreamer
  links. US-172 H1 may pre-empt between derivations.
  Queue update (CM, 2026-10-25; supersedes the order above): F-365
  is REMOVED from the Pi queue (fallback only, see above). The
  queue is the F-374 PR-head suite, expressed as `nix build
  .#checks.*` (never `nix run` apps), then the wireplumber-no-bypass
  check.
  Pi as builder (CM, 2026-10-25): sandboxed `nix build
  .#checks.*` only, with sandbox=true recorded and the thermal rule
  applied; never `nix run .#test-*` on the Pi; GC after the queue
  finishes. test-midi
  (worker-7, QE): NOT a silent skip; flake.nix copies the configs
  flat (midi/, configs/), but src/midi/tests/test_midi_daemon.py:56
  resolves tests/../../../configs, so 6 tests (lines 93, 123, 132,
  142, 536, 594) open <builddir>/../configs/midi/apcmini-mk2.yml,
  hit FileNotFoundError and fail the derivation. Unnoticed because
  CI doesn't run nix flake check (F-380); the app variants see the
  real repo layout. Low (QE). Cheapest fix: mirror the repo layout
  in the derivation (src/midi + configs). Out of
  chore/rc-check-configs.
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
  not affected. (worker-1, re-reported via CM; again by worker-2,
  2026-10-25: every eval of mugge-pi5-deploy) Update 2026-10-25
  (worker-1): seen on every `nix eval` of BOTH mugge-pi5-deploy and
  mugge-deploy, sometimes with a "read-only, set multiple times"
  error. Not blocking; not US-163 scope. Owner: Architect.
- US-170: Pi 4 allowlist and configurationRevision (AC1); Pi 4 WP ALSA
  rule; drvPath pin removal.
- **F-375** (SecSpec, LOW; F-318 follow-up, 2026-10-25) Consider
  PipeWire client permissions that hide or limit the USBStreamer
  playback node for non-GM clients, which is stronger than the WP
  rule. Deferred: it breaks pw-link -l audits and the monitor taps.
  Revisit after US-173 and F-318 layer (b) (US-175).
- **F-376** (worker-2, LOW; 2026-10-25) installer.nix still writes
  tryboot.txt with os_prefix= after the dt lines, the order US-172
  fixes in bootloader.nix. Architect: out of US-172 (the installer
  is used up); backlog only.
- Merge scripts/generate-room-sim-ir.py (used by local-demo) into
  the single room simulator (mock/room_simulator.py) as a thin
  wrapper (Architect, 2026-10-25). Not in 174b: the script is
  read-only for that lane. Also reported by worker-4 (US-174b design
  review): the script re-implements the image-source simulator.
- **F-381** (AE, LOW; 2026-10-25) Driver records give
  metadata.datasheet_file with a "data/" prefix, but validate_driver
  (validate_driver.py:189-190) already resolves it under
  <driver_dir>/data, so the path doubles ("data/data/") and the
  check warns "referenced file not found". Found on
  configs/drivers/dayton-audio-umii18-22 (US-155). PM check on main
  b0666c02: 822 records use the prefix, and only one file exists
  under any configs/drivers/*/data/ (bose-ps28-iii), so most PDFs
  are not committed at all. No audio impact (AE). Same records as
  F-363 (worker-6): the CM decides whether it rides there or later.
  CM ruling (2026-10-25): LATER, its own item with its own worker
  after F-363 merges. F-363 is first in the merge order and must stay
  small; the fix touches validate_driver.py:189, outside worker-6's
  fence; 822 changed records would bury F-363's ~29 data corrections.
  worker-6 does not touch datasheet_file paths; a correction's
  citation may name the real file while the path field stays as is.
- **F-382** (QE, LOW; 2026-10-25; US-163 lab note, AC19 Notes) The
  deploy-src export's eval stderr shows "could not read HEAD ref ...
  using 'master'". Harmless for AC19 (configurationRevision came out
  correct). If future evidence relies on the export's git metadata
  beyond self.rev, the export needs a real ref.
- US-163 AC5 direct read (QE-owned, P3, not a blocker; 2026-10-25):
  on the next OBSERVE session on .89, run `systemctl show -p
  RuntimeWatchdogUSec -p RebootWatchdogUSec -p WatchdogDevice` on
  the booted generation, closing the AC5 inference (QE PASS rests on
  two reads not taken on the final generation plus the config
  default, QE git grep at 798f2dc7 and 07a65f9e) with a direct read.
  Architect (2026-10-25, from F-389): check whether the base
  generation sets RuntimeWatchdogSec at all (the bootstrap read
  showed RuntimeWatchdogUSec=0). The Pi 4 watchdog failed in Tests
  3/5, so this matters for gigs; run 3 also needs it on bcm2835.
  Linked to F-389 and the CLAUDE.md watchdog reliability TODO
  (Architect, 2026-10-25).

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
  MERGED with owner consent ("Yes, merge 49."): merge commit
  45593097 at 15:32:07Z; origin/main = 45593097. CM: F-335 closed by
  #49. PM: the F-335 record (F-335.md, defects index, status.md)
  still says open; F-335 AC4 asks for dispatched T1+T2 green ON MAIN
  with every test-* step run. Close the record after QE confirms
  AC1-AC6 (records follow-up, not in the #50 head move).
- #50 US-163: MERGED 07a65f9e (2026-10-25 19:43:14Z, CM, standing
  owner permission; merge commit pinned to 22370317, tree
  identical). 7/7 at 22370317: SecSpec 6399942686, AE 6399947753,
  UX 6399948019, Architect 6399948245, TW 6399960981, AD
  6399961232, QE APPROVED 6402290391. CI 40210023435 green (counts
  identical to #49 run 40198678554); T3 release run 40226857537
  green (artifact sd-card-image, digest 91b546c4...). US-163 stays
  OPEN until AC19 passes: DEPLOY session CM-DEP-.89-AC19 granted to
  worker-1. A US-163 done-records batch (PM) follows the AC19 PASS.
  AC19 PASSED (CM, 2026-10-25); session closed; evidence with QE for
  the verdict. The done-records batch follows the QE verdict.
  QE ACCEPTED AC19 (warm-reboot redeploy on main 07a65f9e; the full
  verdict is with the CM). main = b0666c02 (#51, docs only); the Pi
  runs #50's 07a65f9e, the same system config. PO status call
  (2026-10-25): DONE (2026-10-25), with the known deviations and
  AC20 (bootstrap/dev image, not gig-capable) kept; "done" is not
  amps-on clearance. Done-records batch B7 (PM): pending the QE's
  per-AC list and the PO's check of the deviation list.
  PO ruling: all 7 "Known deviations" of #50 (final head 22370317)
  verbatim, each with its successor, plus the PR's Backlog IDs list
  unchanged; the earlier "four" is withdrawn. Branch
  docs/US-163-done-records (CM, off b0666c02): TW's AC19 lab-note
  section committed as 8b0c3947; story batch B7b (PM, MANIFEST
  980dd1d2; supersedes B7 db8d2199, never committed) uses the QE's
  authoritative per-AC list: AC5 not ticked (not QE-verified), AC21
  not ticked (amended), the rest ticked. Docs-only (CI-exempt); 7
  approvals still required. The US-172 board-guard note is already
  US-172 AC4 (PO: no new batch).
  PR #53 (CM): B7 (db8d2199) was committed before B7b arrived; head
  ec4508cb, PR opened, 7 reviewers asked. B7b committed on top as a
  whole-file replace: head c1ff5545 (29 ticked; AC5, AC21 not).
  B7 stays in the history as an intermediate commit (no force-push).
  At ec4508cb: UX APPROVED, AD APPROVE (both lapse on the head
  move). AD L1 (status cites D-070 before it is on main): PO adopts
  the AE's corrected sentence as FINAL (B7c 90bed0e0 void, never
  committed; B7d follows). AD L2 (AC6/AC7) fixed by B7b. AD N1
  (down window = Mac-side poll times): TW lab note v3. AC5 evidence
  (CM): two watchdog reads, neither on the final generation; QE
  decides. The CM re-asks all 7 reviewers at the final head (v3 +
  B7d). Team-lead ruling: the TW approves the whole PR and states
  they wrote the section; the QE checks it line by line; the PO acks
  the status wording (not Rule 13).
  B7c (90bed0e0) and B7d (bdf5d904) never committed; B7e (PM,
  MANIFEST bc4dd46d, whole-file superset of B7d) committed on top of
  the TW lab note v3 (943ec13e): head 55ee9dc9 (CM checked the cited
  AC5 evidence lines). B7e: the AE's amps-on status sentence
  (adopted as FINAL by the PO); AC5 ticked (QE PASS, watchdog off by
  default and by config); 30 ticked, AC21 not (amended). All 7
  reviewers and the PO asked at 55ee9dc9 (bundle
  /tmp/pr53-review-55ee9dc9/).
  At 55ee9dc9: UX APPROVED (no concerns; both ec4508cb notes
  resolved); AD APPROVE (not covering CI or later heads; L1, L2, N1
  resolved, no new findings; they were never separate items).
  MERGED (CM, standing owner permission): main = dfdbbbd6, 7/7
  approvals at 55ee9dc9, no failed CI job. US-163 done records are
  on main.
  Follow-ups for the next US-163 docs touch (not blockers):
  - AE: the AC14 verdict should read "16/16 read 0.000000 via pw-cli
    (|x| < 5e-7; exact zero pending the US-159 raw-bits reader)".
  - TW: when D-070 merges, add a short gloss of H to the US-163
    status; lower-case "any" after the colon.
  QE non-blocking (new): the guard count is not echoed in the CI log
  (it is in $out only); add a dev-howto line on unstaged test files
  (Nix flakes ignore them). Already tracked: F-370, F-371, F-373;
  lsmod hifiberry/pcm512 is in the AC19 read set (B3 v10/v11).
- #51 docs/US-163-postmerge (TW: safety.md row 14, row 4 N/A, the
  §8.5 note; nixos-upgrade.md), docs-only: head 667b7a8f (1472206a
  + merge of main 07a65f9e); review bundle /tmp/pr51-review-667b7a8f/
  (SHA256SUMS 2127d70c). PM read: rows 4 and 14 at 667b7a8f match
  this file verbatim. At 667b7a8f: UX APPROVED 6402324487, QE
  APPROVED 6402324704, SecSpec APPROVE 6402324907, TW APPROVED
  6402325121, AD APPROVE 6402325340 (not covering CI or later heads;
  M4 resolved by the AE row 14 wording). 5/7; AE and Architect open.
  CI: changes, nixos-eval, ci-gate success; test-and-build skipped
  (docs-only); GitHub CLEAN. PR numbering (team-lead): #51 is this
  docs PR, not US-172; the US-172 PR gets the next free number.
  Head moved to 2d22aa7ae782148f4f14a72bc1177495b712fae3 (TW: R1 +
  AD L2 + the N1 row 14; the closed-only f7f37e87 was never pushed
  alone); all 667b7a8f verdicts lapsed; bundle
  /tmp/pr51-review-2d22aa7a/ (SHA256SUMS 618dc2ee). At 2d22aa7a:
  UX APPROVED (nit (a) resolved), AD APPROVE (joint N1 text
  confirmed; not CI or later heads), 7/7 (CM), CI green. MERGED
  (CM, standing owner permission): main b0666c02917b4dce969fdc79
  ad242dd799bc1e75.
- New branches at 22370317 (CM, 2026-10-25; owner via team-lead:
  "start the next work now"; disjoint file sets):
  story/US-172-pi5-drm (worker-2: bootloader.nix reorder, greetd
  ordered after DRM, vclog fallback prep; no Pi access; the test
  boot comes after the #50 merge and AC19); docs/US-163-postmerge
  (TW: safety.md row 14, row 4 N/A, the §8.5 note; at 1472206a).
  US-172.md and the backlog stay PM. B4 (PM, US-172 story batch for
  worker-2's branch: US-172.md + the stories-index row; MANIFEST
  eff8d9b1...): status in progress, the starter set, AC1 ride-in
  exception marked LAPSED (TW N2). B4 passed to worker-2 (CM). The
  docs branch is PR #51 (above).
- STANDING OWNER PERMISSION (2026-10-25, verbatim via team-lead):
  "Also, standing permission to merge if the team approves, without
  my additional approval. Let's ensure you can make progress
  autonomously." Once the CM's check is complete (all 7 Rule 13
  approvals at the final head, CI T1-T3 green with real counts, main
  protection respected, no --admin), the CM merges without owner
  acceptance and reports the merge SHA to team-lead. Applies to #50.
  NOT covered: direct pushes to main (including the local 95306f66),
  release or tag dispatch, permission-system blocks. Vetoes and
  safety rules are unchanged.
- #43, #45, #44: need #49 on main and real green CI; #45 before #44.
- #45 dangling citations (TW, 2026-10-25): AC14, F-320, F-338,
  F-339 and F-347 cite "pre-flight #10 (PR #45)". #45
  (docs/safety-d063-gate,
  76b61347) is unmerged, so on main those citations point at
  nothing. Resolve when #45 merges or re-point them. Owner TW.
- #45 gain read method (TW, 2026-10-25; needs an AE ruling before #45
  merges): #45's pre-flight #10 reads gains with `pw-cli
  enum-params` (pw-dump hides NaN), while main's "Gains at boot"
  rule and the F-318 batch's C2 read them from pw-dump. One method
  must be chosen and used consistently. CLOSED (AE ruling,
  2026-10-25): #45 check 10 is correct as written, no change. The
  contradiction was on the main/F-318 side and is fixed in the F-318
  batch ("Gains at boot", C2, amps-on row 14, D-070 row 14 entry;
  AE ADDENDUM 4/5). Follow-ups: F-386.
- **F-386** Gain values read from pw-dump (AE, P2, AE-owned review;
  2026-10-25). AE ruling: gain VALUES are read only with `pw-cli
  enum-params <pi4audio-convolver id> Props`; pw-dump is for
  structure only (node counts and names), because it prints
  NaN/-Inf/subnormal as 0.000000. Review the remaining pw-dump value
  readers outside the F-318 batch, e.g. safety.md's audit polling
  "via pw-dump every 30 s" and audio_mute.py. Node discovery via
  pw-dump is fine; no value check may trust pw-dump for
  NaN/-Inf/subnormal.
- #36, #40: no Rule 13 review; owner direction needed (#40 IDs clash).
- chore/backlog (this file): no PR yet; docs-only.
