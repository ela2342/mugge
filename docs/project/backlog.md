# Backlog

Owner directive (2026-10-24): one active priority, US-163 (Pi 5 NixOS
bootstrap; was Raspbian .88, now NixOS at 192.168.178.89). Everything
below is parked. Nobody works on a backlog item unless it blocks US-163.
New findings go to the PM as one-liners and
land here. Maintained by the PM; the CM commits changes.
SUPERSEDED (2026-10-26): the US-163-only directive above is replaced
by the owner's priority statements and the PO plan below. Owner,
verbatim (via team-lead): "Getting the DJ set to work and the room
correction is slightly higher prio than working out all the safety
edges. For prod, we need all, but right now my feeling is that we're
spending a lot of time chasing corner cases of safety before tackling
the core technology issues." Owner, later the same day, verbatim (via
PO): "I don't see any Wayland at all. HW accelerated UI is really top
priority!"
- TOP PRIORITY (PO, 2026-10-26, after the Wayland statement): US-172
  (hardware V3D GL, labwc/Wayland on HDMI) is above everything else.
  US-172c recovery counts only as the first step of US-172; US-173
  follows afterwards. Plan B (llvmpipe, headless + wayvnc) is struck
  as a plan: it does not meet the goal (one-line note under the DJ
  item only). Capacity: anyone US-172 needs (diagnosis, Architect, CM
  sessions, worker-2) is on it first; lane B continues only with
  workers US-172 doesn't need, and with no Pi sessions while US-172
  needs the Pi. US-172 DONE (PO): labwc running on HDMI with hardware
  V3D (no llvmpipe, verified via the GL renderer string) + /dev/dri +
  greetd after DRM + the stability run (Architect AC2 amendment, see
  US-172); desktop with or without HDMI as in the ACs. Diagnosis
  order: the Architect and worker-2 decide (tryboot/order theory, then
  /proc/device-tree/chosen/log, then vclog); no PO round.
- PRIORITY RE-PLAN (PO FINAL, 2026-10-26, with corrections; supersedes
  the PO's earlier #45 ruling). A. Pi lane (sequential, one Pi session
  at a time): 1. US-172c recovery (first step of US-172). 2. US-172
  display/DRM (TOP PRIORITY above). 3. US-173 core: Mixxx -> GM ->
  filter-chain -> gate -> USBStreamer, Hercules USB-MIDI, thermal
  watch; without amps the goal is the correct ports and plausible
  levels. B. Room correction lane (parallel, mostly simulator/Mac; see
  capacity rule above): 1. #57. 2. #55 (F-374). 3. F-390 (the minimal
  fallback, log path and hash, is enough to start). 4. F-391 (core).
  5. F-399. 6. US-174c/d (with the AE HF-cut bound in 174d), then
  US-174e. F-398 stays an AC on the step that writes coefficients to
  the Pi.
- PRE-PROD (new label, P2; not dropped, no new rounds until the core
  is running): Gate-2 (r8 finishes and its result is recorded, nothing
  after it: the e74a6e93 edit, P-a, F-396, F-397, US-176), F-386,
  F-398 (except its AC above), the #45 revival, further safety.md
  wording rounds, readback audit refinements. The US-172c cold read
  stays in lane A.
- PO CORRECTIONS (2026-10-26): #45 PARKED now; if the TW's resolution
  is complete the CM may commit the merge on the branch to keep the
  work, otherwise the TW saves a patch in the branch worktree; no
  review round, no CI request; 8cba3522 stays. F-318: v18 (3f1a578f)
  lands as is on the US-173 branch; v19 is pre-prod; the AE decides
  whether item 16 is a real-hazard row and the PO accepts that without
  another round (AE ruled: real hazard, minimal form only, see amps-on
  row 16); the v19-onto-#45 order is moot.
- WHO STOPS WHAT (PO, via the CM, verbatim): "workers on pre-prod
  items stop at the next clean point (finish the current tool call,
  commit WIP on their own branch, record the state in one line) and
  move to lane A/B on the CM's assignment. A running build may finish,
  but no follow-up starts. The TW parks the #45 conflict work with a
  WIP commit."
- STAYS IN FORCE: the owner's standing safety rules (warn before
  reboots/USBStreamer interruptions, any gain increase needs the
  owner's OK, nothing connected), the AE/SecSpec veto, Rule 13, and
  the AMPS-ON PRECONDITION LIST (frozen at its current content; new
  rows only for a real hazard) once amps get connected.
  NEW OWNER STANDING STATEMENT (2026-10-26, verbatim via team-lead and
  the CM): "\"nothing is connected\" is standing until further notice,
  no need to keep getting my confirmation for now." The team no longer
  asks the owner to re-confirm "nothing connected"; re-confirmation is
  due only when something gets connected (amps-on row 1).
- Lane status (CM, 2026-10-26): A: worker-2 holds CHG-US172c-1 (steps
  1-6), granted after the owner's cold power cycle (verbatim: "Power
  cycled, with about 10 seconds off.", ~08:43; no LED report needed);
  then the OBSERVE gains read with node state, then steps 7-8, then
  US-172. worker-3 stopped Gate-2 after r8 and is reassigned to US-173
  core prep (Mac-side; sends a plan first). B: worker-4 has F-399 on
  fix/F-399-venue-runner-cleanup at 6f4ae3d1; F-390/F-391 start when
  #55 merges (team-lead to confirm worker-5 is alive). The TW's F-394
  docs batch (/tmp/tw-f394-batch) is held until #55 and #57 merge, to
  save reviewer time. Nothing needs the owner right now.
  UPDATE (CM, team-lead, 2026-10-26): the cold cycle is CONFIRMED
  (OBSERVE-US172c-2, worker-2): /proc/uptime 615 s at 08:54:46Z, boot
  about 08:44:31Z, as the owner said (verbatim: "I power cycled the
  Pi. Physically unplogged power supply. Saw it boot."). The earlier
  "not cold-cycled" reading ("up 11:45") was wrong: the Pi 5 has no
  RTC battery and boots at the last saved wall-clock time until NTP
  corrects it (~44 s), so /proc/uptime is the reference. Host key and
  MAC match the pinned values. Now: OBSERVE-US172c-3 (AE gains read +
  Architect D items) granted to worker-2; the gains read waits for the
  AE ruling on whether the two read-only SSH sessions since boot keep
  the cold-boot precondition intact; CHANGE for steps 7-8 comes next.
  worker-5 is alive (team-lead): F-390/F-391 go to worker-5 when #55
  merges. worker-4 is fence-cleared for F-399 (runner.py:313-350).
  worker-3's US-173 core plan is approved (see US-173).
  UPDATE (CM, 2026-10-26; supersedes the boot reference above): the
  owner rebooted AGAIN by power pull (owner: "Power pull."). Kernel
  start about 08:57:40Z, boot 60f384a1, COLD. The 08:44Z boot
  (deb9ee57) ended abruptly at 674 s with that pull. OBSERVE-US172c-3
  is VOID (partial captures kept raw); worker-2 now holds
  OBSERVE-US172c-4 on 60f384a1. Two SSH sessions from the Mac with the
  same key were not a worker's: 08:55Z (pts/0, sudo dmesg) very likely
  the owner; 08:58:24Z unconfirmed (team-lead is asking the owner). If
  it was an agent, that is a protocol breach (open).
  CORRECTION (CM, 2026-10-26; to the UPDATE above): there was no later
  reboot. The owner's power pull IS boot 60f384a1 (about 08:57:40Z),
  and OBSERVE-US172c-3 ran on that same boot; its VOID label is kept
  anyway. The boot evidence alone can't tell a cold start from a hard
  reset; "COLD" rests on the owner's "Power pull." OBSERVE-US172c-4
  completed and released 09:05:29Z (CM, 2026-10-26). GAINS-RECORD-v2
  (observe4b/, sha256 a465a8ad...4528): two reads (T+04:58, T+07:47)
  with pipewire, wireplumber and GM active, 8/8 Mult 0.000000, links
  and Props unchanged across 4 dumps; GM get_gate: gate_open=false,
  has_pending_gains=false, venue=null. The T+00:44 session is logind
  session 2 (pts/0, from .36), STILL OPEN; only sshd/logind lines for
  it.
  Mac disk (CM, 2026-10-26): 2.99 GiB free, below the 3.0 GiB line. No
  nix clearance for anyone until it recovers.
  UPDATE (CM, team-lead, 2026-10-26): the T+00:44 SSH session item is
  CLOSED (AE). It stays a recorded qualifier; nobody touches the
  session and the owner is NOT asked. This supersedes "team-lead is
  asking the owner" above and every "pending the owner's word" in this
  file.
  UPDATE (CM, 2026-10-26): Mac disk now 2.85 GiB and still dropping.
  No nix.
  UPDATE (CM, 2026-10-26): Mac disk 2.84 GiB. No nix. The CM fixed the
  evidence dir modes (observe3/4/4b were 0600 dirs, unreadable to
  advisors).
  UPDATE (CM, 2026-10-26): Mac disk about 2.90 GB free after two new
  worktrees (~32 MB each). The hold stays: no nix for anyone.
  Steps 7-8 DONE (CM, team-lead, 2026-10-26; corrects "SUSPENDED
  before use" in US-172c): worker-2 had already run step 7 when the
  suspension came; the Architect confirmed the cleanup and the plain
  reboot (announced about 09:08Z) were fine, with the evidence copied
  to the Mac. Step 8 outcome (CM, 2026-10-26): tb-normal issued
  09:06:58Z, down 09:07:14Z, up 09:07:45Z (31 s); new boot aae07160,
  base generation rcyg67wd, tryboot flag 0. RESTORED PASS, 0 findings:
  16 gains at 0; gate closed, venue null; links 24 unchanged; FAT
  manifest equal to PRE; tryboot.txt and o/ absent. Thermal max 66.1
  °C. CM-CHG-.89-US172c-78 released 09:09Z. The Architect's 10-min
  branch did NOT trigger, so plain reboots work on this kernel. LIBPI
  root /home/ela/.us172-libpi stays until US-172 closes. Run 3
  (tryboot with visible boot output) waits until the owner says they
  are at the HDMI screen.
- DJ PLAYBACK PATH (core item, PO, 2026-10-26): Mixxx on the Pi 5 ->
  GM (DJ mode, quantum 1024) -> filter-chain convolver -> gate ->
  USBStreamer, with the crossover-only FIRs from the US-155 venue
  config; room correction is not a prerequisite. Blockers (PM, as sent
  to the PO):
  - US-172c and US-172 (F-367). Architect (2026-10-26): root cause
    (config.txt order) unproven until the tryboot; about half a day to
    Mixxx visible if confirmed, otherwise +1-2 days of vclog
    diagnosis, open-ended. Risk (medium): v3d on BCM2712 (V3D 7.1)
    under PREEMPT_RT is untested by us; US-172 AC2 counts only after a
    stability run.
  - GM DJ mode has never run on the Pi 5, and CI is blind to it: the
    DJ-mode E2E group skips instead of failing (F-394). The backlog
    has no filed record for the "two reconciler bugs" in CLAUDE.md (Pi
    4, US-059 era); the Architect confirms whether they still apply.
  - F-374 (#55): after #55 merges, regenerate the session WAVs from
    the merge SHA, AE AC2 re-check, AC3a SHA256SUMS from the same run.
  - F-318 layer (a), the WP rule (695f69af), lands with v18 as is.
  - Link audit: F-361 is the real fix; under D-070 the manual `pw-link
    -l` check before the gate opens replaces it (only convolver-out ->
    USBStreamer AUX).
  - GM routing defects in the backlog: F-361, F-373/G16, US-175,
    F-394.
  - Hercules USB-MIDI: unverified on Linux; if it fails, a separate
    story and mouse/keyboard (US-173), so not blocking. Bluetooth off
    is irrelevant for USB.
  - Then the D-070 amps-on preconditions. Team: row 2 (F-341 AC3, one
    CM session), the F-321 loaded-WAV sha check, D-070's own safety.md
    text merged (TW v18 on the US-173 branch), the H safety.md text
    (TW, mirror rule), row 16 in its minimal form as a session-plan
    step (AE ruling, QE/CM session record), AE one-liner 7 below; rows
    7 and 10 are checked at the session. Owner only: row 3 (HiFiBerry
    HAT off or nothing on it), H with the oscilloscope (~30 min,
    speakers disconnected), the amp/speaker wiring, row 1 at the
    session, plugging in the Hercules.
  - Thermal is the real limiter (AE + Architect): they expect the 80 C
    STOP in a long set with passive cooling. "Fan/heatsink on the Pi 5
    before the first longer set" is on the owner's batched physical
    list (ask once, together with amps-on).
  - Plan B note only (struck by the PO; not an option): llvmpipe on
    HDMI or headless labwc + wayvnc; neither meets the goal.
  - UPDATE (PO, Architect, 2026-10-26; replaces the "two reconciler
    bugs" point above): the two CLAUDE.md reconciler bugs are STALE
    (GM-12 Finding 10): (2) the reconciler feedback loop was fixed in
    8ef778e3 (2026-03-16, re-entrancy guard plus duplicate-link
    guard); (1) the startup enumeration miss was most likely the
    node-resolution bug fixed in 5fbd5f75 (GM-13/GM-14,
    find_node_port, 2026-03-17; Architect inference, neither commit
    message names it). The reconciler is idempotent and converges as
    ports appear; GM ran as the link manager on the Pi 4 (US-140,
    ce0d85da, 2026-04). The real risk: GM DJ mode has never run on the
    Pi 5 (node/port names, WP auto-links per D-065/F-318, quantum
    1024), covered by the new US-173 link-dump AC.
  - F-396 (PO, 2026-10-26): reproduced in r8 (a WP restart re-suspends
    the filter-chain). Under row 16's minimal form: after a WP
    restart, a PW restart per row 15, then the re-read. If F-396 makes
    the readback never verifiable in practice, it comes back to the PO
    as a core candidate.
  - Owner estimate (PO to team-lead, 2026-10-26): 2-5 working days,
    worst case 1-1.5 weeks.
- AE pre-prod one-liners (2026-10-26): (1) #45 re-review on revival.
  (2) F-318 v19 check. (3) F-395/F-396 T65 replug logging, F-396 AC4
  on the Pi. (4) F-397/US-176 canary design, incl. the safety.md l.630
  30 s pw-dump Mult>1.0 monitor, which can't see NaN/Inf. (5) r8
  sandbox follow-ups. (6) US-159 hardening: F-373, AC18b/T49, F-341
  AC3, G16/T65. (7) Post-US-172c cold cycle with a state-logged gains
  read, before the first amps-on session.
  UPDATE (AE, 2026-10-26): (7) is CLOSED. OBSERVE-US172c-4 PASS, boot
  60f384a1 (fresh boot after power loss or hard reset), T+04:58: both
  nodes running before and after the read, the 8 Mult values all
  0.000000 via pw-cli, node counts 1 and 1 (record ffc000b5...f08d).
  Qualifier: an unattributed SSH session at T+00:44, pending the
  owner's word. Scope: PW start state only; GM restart, profile
  activation and unlatch are not covered.
  AE ruling, verbatim (via CM, 2026-10-26): "PASS, fresh boot after
  power loss or hard reset (60f384a1), T+04:58, F-395-verifiable;
  qualifier: unattributed SSH session at T+00:44". Scope: PW start
  state on this image only; not a GM restart, profile activation or
  unlatch (F-320-E/F-348/F-320-D). The frozen amps-on list is
  untouched. Evidence observe4/GAINS-RECORD.txt, sha256
  ffc000b5...f08d.
  (8) (AE, via CM, 2026-10-26; PRE-PROD, does NOT block M3), verbatim:
  "Direct ALSA tools (aplay, speaker-test, amixer) bypass D-063 gains
  and the gate when PW is stopped. speaker-test emits full-scale noise
  at the USBStreamer's hw 0 dB maximum. Pre-prod: decide whether to
  restrict them (audio group, or drop the package from the prod
  image)."
  (9) (AE, via CM, 2026-10-26; PRE-PROD) safety.md line for the TW's
  next batch, verbatim: "Never run aplay or speaker-test against the
  USBStreamer. Use amixer only to read, never to set USBStreamer
  controls." Reason: the USBStreamer powers up at hw 0 dB, so lowering
  it makes a power loss a gain increase, and the cold-cycle proof
  would need redoing. safety.md is the TW's file; the PM only records
  the line.
  (10) (AE, via CM, 2026-10-26; PRE-PROD), verbatim: "Thermal ceiling
  load failure on profile activation is a warning only. Pre-prod: make
  activation fail closed (gate stays closed, loud UI error) when the
  limiter cannot be configured."
  Merge gate for (9) (team-lead, 2026-10-26): (9) goes in the same
  paused safety.md queue as the US-174d lines but has its own gate.
  Team-lead reads (9) as the AE's US-173 (DJ path) item, gating the
  US-173 merge; the AE's label above is PRE-PROD. Team-lead: the AE's
  word wins. PM asked the AE; until the AE answers, (9) stays as
  labelled above. The muted-spare line is no longer a separate line:
  it is amps-on row 17, sentence 2 (US-174d gate).
  AE ANSWER (2026-10-26; supersedes "PM asked the AE" above): (9) is
  PRE-PROD, for the TW's next safety.md batch; it does NOT gate the
  US-173 merge. AE reason: US-173 never runs aplay, speaker-test,
  amixer set or alsactl; it is an operator rule, and nothing is
  connected. The TW's aplay/amixer/alsactl rule rode along on the
  US-173 branch anyway (1c2d4bef, see US-173); it is not a merge
  condition.
  (11) (AE, via team-lead, 2026-10-26; PRE-PROD, owner AE): after a
  web-ui restart the thermal limiter comes up "unconfigured, awaiting
  profile" (main.py:213-219) and nothing re-reads the active-profile
  marker, so thermal limiting stays OFF until a profile is
  re-activated: it fails open. Fix: re-arm the limiter from the marker
  at startup, or fail closed. Not blocking now. Pairs with (10).
  UPDATE (CM, TW, 2026-10-26): (9) is REMOVED from the "next pre-prod
  safety.md batch" list. The TW's aplay commit 1c2d4bef stays on the
  US-173 branch (no rewrite, CM rule); its safety.md text is byte for
  byte the TW's AE-approved batch (a28f6abd). It rides with the US-173
  PR, the AE reviews it there, and it is NOT a merge condition. TW
  Summary row, verbatim: "US-173 | No aplay/speaker-test playback on
  the USBStreamer (listing OK); amixer read-only; no alsactl | 9".
- AE core items (2026-10-26): #55 and #57 wait only on CI; the HF
  bound; the CHN-50P mask after F-388; the SNR threshold; the 174c/d/e
  reviews; the US-172c/172/173 reviews (US-173 AC2/AC3a); a thermal
  soak under DJ load (no fan on the Pi 5 is a gig risk). While
  "nothing connected" stands, nothing safety-related blocks lane A or
  B.
  Lane status (CM, 2026-10-26, after v185): #55 (F-374) MERGED as
  5f3af36ac1c1db2fc1a7ee516b2765d8584380fe at 09:26:48Z, 7/7 at
  17144904, CI 40294373355 green. F-390 is no longer waiting on #55.
  #57 was update-branched to 599ea52a (merging main 5f3af36a); its own
  diff is identical, but strict protection voided the 6f4ae3d1
  approvals. 7/7 diff-only re-checks are in at 599ea52a; it waits on
  CI 40299659873. QE condition on #57: that run green with the test
  file at 95 passed and the count = main + 26, and the PR body's
  closed-loop numbers refreshed from the CI log or labelled pre-#55
  (#55 moves crossover-section profiles to LR alignment, so
  residual/teeth numbers can move although the diffs share no file).
  UX N1/N2 for US-174e stand. Docs-only PRs (CI-exempt, 7 approvals
  still needed): #61 (TW F-394 status batch, head 247478d5) and #62
  (PM BS1 batch, head 20903a04, 3 files, +4/-4, base blobs = main
  5f3af36a, MANIFEST verified). Tallies so far: #61 AD, QE (source
  owner, F-394 facts cross-checked), UX APPROVE; #62 AD (L1), QE, UX
  APPROVE. worker-5 is permission-blocked on running tests (escalated
  to the owner). Mac disk: about 2.17 GB free, below the line; no nix
  for anyone. The US-174d crash design is being re-settled by the
  Architect and the AD (see US-174d).
  UPDATE (CM, 2026-10-26, after v186): the US-174d crash design is
  SETTLED (see US-174d). #61 and #62 have 7/7 at their heads; their
  merges are held until after #57, so #57's approvals are not voided.
  worker-5 is also permission-blocked on read-only grep (escalated).
  US-173 is pushed at 1c2d4bef. OBSERVE-AE-sink-1 is granted to
  worker-3 for the AE's default-sink reads (see US-173). Mac disk:
  1.92 GB free and still falling; no nix for anyone.
  UPDATE (CM, QE, 2026-10-26, after v187): backlog v187 pushed as
  a6666f74. #57 at 599ea52a: CI 40299659873 is RED;
  TestAC7Identity::test_each_file_corrects_its_own_room fails, margin
  0.68 < 1.0 dB. The QE's approval is SUSPENDED, so #57 stands at 6/7
  and the fixed head needs a fresh 7/7 (see US-174). Fix with
  worker-4, the Architect and the AE. #57 is not merged, so #61 and
  #62 stay held behind it. The 548 s ARM wall time goes to F-380 and
  does not block. OBSERVE-AE-sink-1 released (see US-173).
  CHANGE-US172r3-diag granted (see US-172 run 3). Mac disk: 1.90 GB
  free; no nix for anyone.

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
origin and all worktrees, 2026-10-25); F-390 (P1, speaker-config
path split, GATE before US-173/US-174c/d sessions; PO; PM checked
free across main, origin and all worktrees, 2026-10-25); F-391
(P1, measurement sweep ignores mandatory_hpf_hz; AE; PM checked
free across main, origin and all worktrees, 2026-10-25); F-392
(P2, unequal LR orders at one crossover point; AE; PM checked free
across main, origin and all worktrees, 2026-10-25); F-393 (P2,
check-sandbox guard misses configs/drivers; AD L1 + QE on #54; PM
checked free across main, origin and all worktrees, 2026-10-25);
F-394 (High, DJ-mode E2E group skips or fails, mute unproven; QE,
AE confirms; PM checked free across main, origin and all worktrees,
2026-10-25); F-395 (P1, gain readback blind on a suspended node,
Gate-2 r6b (ii-c); AE co-owns per A5; PM provisional; PM checked
free across main, origin and all worktrees, 2026-10-26; AE asked
for this P1, 2026-10-26); F-396 (P1, production must never suspend
the filter-chain or USBStreamer node; AE; Architect may re-rate; PM
checked free across main, origin and all worktrees, 2026-10-26);
US-176 (canary node for the gains readback, F-395 follow-up; AE +
Architect; joint r6b ruling); F-397 (P1, gain readback consumers
UI/GM show 0 on suspended nodes; Architect; joint r6b ruling); PM
checked both free across main, origin and all worktrees, 2026-10-26.
Next free: F-398, US-177, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, origin and all
worktrees): F-398 (LOW, SecSpec, #57 review: config-supplied names
used as path components unchecked). Next free (supersedes the line
above): F-399, US-177, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, origin and all
worktrees): F-399 (AD M1, #57 review: the venue runner leaves
deployable-named files on a gate failure). Next free (supersedes the
line above): F-400, US-177, D-071, T66.
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
    UPDATE (AE, F-395 AC (c), 2026-10-26): check #10 is reclassified
    from PASS to NOT VERIFIABLE (node state not logged; not a FAIL);
    re-run at the next Pi gains check (see F-395).
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
    UPDATE (AE, F-395 AC (c), 2026-10-26): AC14 is reclassified from
    PASS to NOT VERIFIABLE (node state not logged; not a FAIL); re-run
    at the next Pi gains check (see F-395).
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
      UPDATE (2026-10-26): the "16 gains came up at 0" read in step
      (c) is NOT VERIFIABLE under F-395 (fc/fc-out node state not
      logged; not a FAIL; AE ruling on the QE's AC (c) list,
      2026-10-26); re-run pending (F-395 AC (c)). Also step (a) and
      the step (b) baseline (QE list rows 4, 5, 7).
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
      UPDATE (2026-10-26): the "gains 0" read in cold cycles 1 and 2
      is NOT VERIFIABLE under F-395 (fc/fc-out node state not logged;
      not a FAIL; AE ruling on the QE's AC (c) list, 2026-10-26);
      re-run pending (F-395 AC (c)). The design fact stands: the gains
      start at Mult 0 at power-on because the conf defaults say so; it
      rests on the conf defaults alone until the re-run (AE).
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
     PENDING (AE ruling v4 item 5, TW batch v19; this list follows on
     merge, mirror rule): "Tested (AE)" becomes "To be tested (AE;
     US-159 T65)". G16 (US-159 l.71) and T65 (l.188) are both open and
     no G16 test record exists (QE, AE checked at ba5cc200). The row
     stays a requirement and is not on the F-395 AC (c) list.
     QE note (#45 review, 2026-10-26; non-blocking, pre-prod):
     "through the D-063 ramp" contradicts F-315 (the gate opens as a
     step); the TW and AE fix it in #45 or v19, with the matching row
     here (mirror rule).
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
     safety.md gains text (CM, 2026-10-25): the AE's text is final as
     TW v10, applied in /tmp/tw-f318-applied-v10.diff; the version the
     CM relayed earlier is superseded. This list mirrors the merged
     safety.md wording.
     Row 15 text PENDING (TW, AE verbatim, 2026-10-25; replaces the
     ADDENDUM 5 final text above because of the joint AE + Architect
     r3 ruling,
     /tmp/w3-gate2-rulings/joint-AE-Architect-r3-gain-readback.md;
     this list takes it on merge, mirror rule): "After any WirePlumber
     restart: amps stay off until PipeWire is restarted or the Pi is
     cold power-cycled, with the gains verified at their boot values
     and the gate closed (safety.md, WirePlumber restart). Interim,
     until US-175 is verified and the live gains readback is proven
     (Gate-2 r3)." The matching safety.md and D-070 text is in the
     TW's F-318 batch: v11 (a3f87b1a) has the caveat; v12
     (/tmp/tw-f318-applied-v12.diff, sha256 549c783c) with "live"
     instead of "runtime" (CM asked). The TW flagged the WP-restart
     bullet (safety.md:99-108) and the D-070 / row 15 interim check:
     it reads the live state, so ruling point 2 applies; the AE is
     wording it. The batch stays held for that wording, the AE's final
     OK and the merged US-173 head. The row 14 replacements above are
     unchanged.
     UPDATE v150 (TW, AE, 2026-10-25; supersedes the row 15 PENDING
     text and BOTH row 14 replacements above, the pw-cli 0.000000 one
     and "able to run that pw-cli read", because of r3: a live gains
     readback can't prove "muted" yet). This list takes both verbatim
     once the F-318 batch merges (mirror rule). Row 15 FINAL: "After
     any WirePlumber restart: amps stay off, including the
     headphone/IEM amps, and headphones/IEMs not worn, until PipeWire
     is restarted or the Pi is cold power-cycled, with the gains
     verified at their boot values and the gate closed (safety.md,
     WirePlumber restart). Interim, until US-175 is verified and the
     live gains readback is proven (Gate-2 r3)." Row 14 (#51) NEW:
     "the emergency stop is the amp power switches (including the
     HP/IEM amps); a person at the switches the whole time the amps
     are on. After any gate close, mute or GraphManager restart,
     reading the gains does not prove "muted" yet (live readback under
     investigation, Gate-2 r3). Switch the amps off, including the
     headphone/IEM amps, and headphones/IEMs not worn, and keep them
     off until PipeWire is restarted or the Pi is cold power-cycled,
     with all 16 gains verified at their boot values (safety.md, Gains
     at boot) and the gate closed. Once the live readback is proven,
     this goes back to: "muted" is proven only by all 16 gains reading
     exactly 0.000000 via `pw-cli enum-params`." TW batch state: v13
     (/tmp/tw-f318-applied-v13.diff, sha256 ea6fb2c8) has "live
     readback" in both caveats, the AE's option (b) WP-restart bullet
     (the pw-link -l check stays; an open gate or a failed pw-link
     check is a US-175 defect) and D-070 row 15; the WP-restart
     wording is no longer pending. v14 (/tmp/tw-f318-applied-v14.diff,
     sha256 57cef8e0) adds D-070 row 14 with the same row 14 text.
     Held for the AE's final OK on v14 and the merged US-173 head;
     worker-3 applies it on the US-173 branch, Rule 13 review on that
     PR. Lead-in and Gate rule change only as planned ("1-3, 5-15" and
     the count). PO informed (FYI) of the D-070 rows.
     AE FINAL OK on TW v14 (57cef8e0), 22:18:02 to the TW (via
     team-lead and CM, 2026-10-25). Conditions: (1) amps-on rows 14/15
     match the v14 wording exactly (PM checked: the v150 row texts
     match D-070 rows 14/15 in v14 word for word; D-070 row 15 adds
     the prefix "Not closed for the supervised session. Instead:");
     (2) the AE reviews anything the rebase onto the merged US-173
     head changes beyond those rows and their ranges. The F-318 batch
     now waits only for the merged US-173 head.
     UPDATE v160 (AE, A5 of the Gate-2 ruling, 2026-10-26; final from
     the AE side; source /tmp/w3-gate2-rulings/AE-draft-r6b-ruling.md
     section 6, sha256 80ec329c, PM frozen copy
     /tmp/pm-backlog/AE-draft-r6b-ruling-80ec329c.md, "F-<new>" filled
     in as F-395 by the PM; supersedes the v150 Row 15 FINAL and Row
     14 (#51) NEW texts above). This list takes these verbatim once
     the F-318 batch merges (mirror rule); the AE reviews the TW's
     diff for word-for-word identity. Row 14 (#51): "the emergency
     stop is the amp power switches (including the HP/IEM amps); a
     person at the switches the whole time the amps are on. After any
     gate close, mute or GraphManager restart, reading the gains does
     not prove "muted" yet. Switch the amps off, including the
     headphone/IEM amps, and headphones/IEMs not worn, and keep them
     off until PipeWire is restarted or the Pi is cold power-cycled,
     with all 16 gains verified at their boot values (safety.md, Gains
     at boot) and the gate closed. A gains reading counts only if the
     filter-chain node and its output node were idle or running at
     that moment (state logged with the reading); a reading on a
     suspended node shows 0 whatever the real gain is and proves
     nothing (F-395, Gate-2 r6b). Once the live readback is proven on
     the Pi, this goes back to: "muted" is proven only by all 16 gains
     reading exactly 0.000000 via `pw-cli enum-params` on a node that
     is idle or running." Row 15 (the text is kept up to "until
     PipeWire is restarted or the Pi is cold power-cycled,"; the end
     is replaced): "After any WirePlumber restart: amps stay off,
     including the headphone/IEM amps, and headphones/IEMs not worn,
     until PipeWire is restarted or the Pi is cold power-cycled, with
     the gains verified at their boot values on a node that is idle or
     running (row 14) and the gate closed (safety.md, WirePlumber
     restart). Interim, until US-175 is verified and the live gains
     readback is proven on the Pi (sandbox: proven for non-suspended
     nodes, Gate-2 r6b; Pi check pending)." safety.md check 10 (Gains
     at boot), added: "The reading counts only if the filter-chain
     node and its output node are idle or running at that moment, as
     logged with the reading. A suspended node reads 0 whatever the
     real gain is, so that result is NOT VERIFIABLE, never a pass."
     The F-318 batch (TW v14) therefore needs a new version with these
     texts before it lands; the AE's v14 OK covered the old row texts.
     PM passed the texts to the TW.
     UPDATE v161 (AE, 2026-10-26; aligns with the joint ruling;
     supersedes the v160 Row 14 and check 10 texts; Row 15 unchanged;
     final from the AE side, AE sent the same to the TW): Row 14
     (#51): "the emergency stop is the amp power switches (including
     the HP/IEM amps); a person at the switches the whole time the
     amps are on. After any gate close, mute or GraphManager restart,
     reading the gains does not prove "muted" yet. Switch the amps
     off, including the headphone/IEM amps, and headphones/IEMs not
     worn, and keep them off until PipeWire is restarted or the Pi is
     cold power-cycled, with all 16 gains verified at their boot
     values (safety.md, Gains at boot) and the gate closed. A gains
     reading counts only if the filter-chain node and its output node
     were idle or running immediately before and after the reading
     (states logged with it); a reading on a suspended node shows 0
     whatever the real gain is and proves nothing (F-395, Gate-2 r6b).
     Once the live readback is proven on the Pi, this goes back to:
     "muted" is proven only by all 16 gains reading exactly 0.000000
     via `pw-cli enum-params` on a node that is idle or running."
     safety.md check 10 (Gains at boot), added (the rest of check 10
     stays): "The reading counts only if the filter-chain node and its
     output node are idle or running immediately before and after the
     reading (states logged with it). A suspended node reads 0
     whatever the real gain is, so that result is NOT VERIFIABLE,
     never a pass." The AE reviews the TW's diff word for word.
     UPDATE v162 (AE via TW, 2026-10-26; FINAL, AE verified TW F-318
     batch v17 bc1efdd1 word for word; the A5 texts are closed on the
     AE side). Three more safety.md replacements; no "Gate-2 r3" is
     left in the batch. (a) WirePlumber-restart bullet: "(live
     readback under investigation, Gate-2 r3)" becomes "(live readback
     proven in the sandbox only for nodes that are idle or running,
     Gate-2 r6b; Pi check pending)". (b) Same bullet: "(Gate-2 r3
     in-daemon result plus the AE's Pi check)" becomes "on the Pi
     (Gate-2 r6b sandbox result plus the AE's Pi check, F-395)"; the
     sentence now reads "…until US-175 is verified AND the live gains
     readback is proven on the Pi (Gate-2 r6b sandbox result plus the
     AE's Pi check, F-395). The AE then lifts it." (c) Gains at boot:
     "and it may not show runtime pw-cli changes (live readback under
     investigation, Gate-2 r3)." becomes "and, like enum-params, it
     shows 0 on a suspended node whatever the real gain is (F-395,
     Gate-2 r6b)." TW batch history: v15 (A5 texts), v16 (AE final
     phrase), v17 (bc1efdd1, (a)-(c)). The batch still waits only for
     the merged US-173 head (rebase, amps-on ranges), then goes to the
     CM; this list mirrors it on merge.
     UPDATE (PM, 2026-10-26): the TW batch is now v18
     (/tmp/tw-f318-applied-v18.diff, sha1 3f1a578f); the only change
     from v17 is "(F-396)" after "USBStreamer interruption (Section
     1)" in the safety.md WirePlumber-restart paragraph (the F-396
     cite, AE ruling). Still waits only for the merged US-173 head.
     UPDATE (TW, AE, PM, 2026-10-26): v19 will carry AE ruling v4
     (/tmp/pm-backlog/ae-ruling-f395-safetymd-gap-v4.md, sha256
     0090761e; v3 a719ed5a, v2 ca8eed3e, v1 554c097a; AD H2, see
     F-395) items 1, 3, 4 and 5: row 8 (l.39), l.64, the "Gains at
     boot" last sentence (FAIL or NOT VERIFIABLE: amps stay off or go
     off now, incl. HP/IEM amps), row 13 (above). Item 2 (row 14
     substrings) is SUPERSEDED (AE v4, answering the PM, 2026-10-26:
     option (A)): row 14 gets the planned v160/v161 Row 14 text above
     at the US-173 rebase, word for word D-070 row 14 in v18; it
     already carries the F-395 rule and removes both pw-dump phrases.
     Plus item 16 (below), lead-in "16 rows", rows 1-3 and 5-16, Gate
     rule "1-3, 5-16". Still waits for the merged US-173 head. The TW
     sends the PM the v19 sha1.
     UPDATE (PO, 2026-10-26): #45 merges into safety.md first; v19
     rebases onto it (the TW resolves the conflict there).
     Earlier note, superseded by the final text: the AE has since ruled that
     "unchanged" is a FAIL, so "gains unchanged or 0" above is
     superseded; the TW asked the AE for corrected text. Do not act
     on the quoted text; this row is replaced by the TW's final
     wording. The TW's batch carries the lead-in, the Gate rule
     "(1-3, 5-15)" and the table row, plus a D-070 row 15 interim
     entry and a Section 5 pre-flight check #11 (F-318 routing).
     Applied once the CM gives the TW the US-173 head with main/#51
     merged (before that the branch has no row 14).
  16. F-395 readback rule (AE, verbatim, 2026-10-26; AD H2 on #60;
     number allocated by the PM; PENDING the matching safety.md text
     in TW batch v19, mirror rule): "F-395 readback rule merged:
     safety.md (Gains at boot, rows 8 and 14, F-373 rule) and D-070
     rows 14-15 count a gains reading only with the filter-chain node
     and its output node idle or running before and after it." Applies
     before any amps-on session and before any D-070 use. Not a #60
     blocker; nothing waits on it while nothing is connected to the Pi
     outputs.
     AE RULING (2026-10-26, cc PO; answers the PO's question under the
     re-plan): row 16 is a real hazard and BLOCKS the first supervised
     D-070 amps-on session, in MINIMAL FORM only; the v19 doc merge is
     NOT needed first (pre-prod). Why: a suspended filter-chain node
     reads 0 whatever the gain; profile activation (F-348), an unlatch
     (F-320-D) or a GM restart (F-320-E) can leave real gains live
     under a "0" reading, i.e. full scale into the 4x450 W amps.
     Minimal form, a step in the first session's plan (QE/CM put it in
     the session record), AE verbatim: "(a) Read the gains with
     `pw-cli enum-params <pi4audio-convolver id> Props` only, never
     pw-dump values. Pass = all 8 `gain_*:Mult` exactly 0.000000. (b)
     Log `info.state` of `pi4audio-convolver` and
     `pi4audio-convolver-out` (from pw-dump) immediately before and
     after that read. Both must be idle or running. (c) If a state is
     suspended, missing or not logged, the result is NOT VERIFIABLE.
     Amps (including HP/IEM amps) stay off; nothing is worn. Hint:
     with Mixxx started and linked but transport stopped, the nodes
     should be running, and that is silent anyway with the gains at 0.
     (d) Repeat (a)-(c) after any PW/GM/WP restart, gate close or mute
     in the session, before amps go back on." Stays pre-prod: the
     safety.md v19 wording, the T65 logging, F-396 AC4, the
     F-397/US-176 validator and the canary. PM relayed it to the QE
     (for the CM).
     ADDITION (AE, 2026-10-26, on the QE's question; step (a0) before
     (a)), verbatim: "(a0) From the same `pw-dump` used for the
     states, confirm exactly one node named `pi4audio-convolver` and
     exactly one named `pi4audio-convolver-out`, and on
     `pi4audio-convolver` exactly 8 `gain_*:Mult` params named
     `gain_left_hp`, `gain_right_hp`, `gain_sub1_lp`, `gain_sub2_lp`,
     `gain_hp_l`, `gain_hp_r`, `gain_iem_l`, `gain_iem_r`; any other
     count or name is a FAIL and the amps (including HP/IEM amps) stay
     off (F-348). `pw-dump` is used for structure and states only,
     never for the gain values."
     Evidence format (QE, AE agrees; matches the US-172c read ruling):
     timestamped before/after state lines with the node ids;
     -0.000000, nan or inf counts as FAIL; one labelled block per
     repeat under (d). Relayed to the CM by the QE.
     ADDITION (AE, 2026-10-26; same session plan): no WirePlumber
     restart with amps on. r8 (sandbox,
     /tmp/w3-gate2/selftest-r8-result/) reproduced F-396: pw-mon shows
     the USBStreamer going to suspended on a WP restart, which is the
     standing "USBStreamer loses its stream" case. In the session plan
     a WP restart is a transient action: amps off first (HP/IEM
     included), then the restart, then the (a)-(c) re-read before the
     amps go back on. Not a new rule, no doc batch; the explicit
     safety.md wording stays pre-prod with F-396 AC4 (Pi
     confirmation). PO: row 16 minimal form is an amps-on row for the
     first D-070 session as is.
  17. Dirac/passthrough and muted spare (AE FINAL, verbatim,
     2026-10-26; number allocated by the PM; lands in safety.md in the
     US-174d PR): "Dirac on ch 1-4 ⇒ venue is a declared passthrough
     AND no own speakers/amps on ch 1-4. No driver is connected to a
     channel the venue declares as a muted spare (all-zero filler)."
     The muted-spare condition is this row's second sentence (AE
     ruling); there is no row 18.
     ORDER (AE picked (b), via TW, 2026-10-26; team-lead ruled out
     (a)): the US-174d PR carries rows 15, 16 and 17 into safety.md;
     US-174d does not wait on v19; v19 rebases onto US-174d. Rows 15
     and 16 stay OPEN until US-175 is verified and v19 merges. AE
     requirement: the lead-in or a footnote says rows 15 and 16 are
     OPEN, so nobody takes the absent v19 text as in force (TW drafts
     it in the US-174d batch; the AE sees it). Row 16 is acceptable as
     written (fail-safe: it can only block amps-on). Lead-in,
     verbatim: "The list has 17 rows. On the Pi 5, rows 1-3 and 5-17
     must ALL hold; row 4 applies to the Pi 4 only." Gate rule: "(1-3,
     5-17)". This list follows the merged safety.md wording (mirror
     rule).
     Row 15 FINAL (AE verbatim, via TW, 2026-10-26; supersedes the
     v160/v161 Row 15 text above; it now leads with "US-175:" and the
     status parenthesis is updated): "US-175: After any WirePlumber
     restart: amps stay off, including the headphone/IEM amps, and
     headphones/IEMs not worn, until PipeWire is restarted or the Pi
     is cold power-cycled, with the gains verified at their boot
     values on a node that is idle or running (row 14) and the gate
     closed (safety.md, WirePlumber restart). Interim, until US-175 is
     verified and the live gains readback is proven on the Pi
     (sandbox: proven for non-suspended nodes, Gate-2 r6b; Pi:
     boot-state zeros read on running nodes, OBSERVE-US172c-4,
     2026-10-26; non-zero set-and-read check pending)."
  18. PROPOSED (Architect, AD concurs, AE input, 2026-10-26; number
     proposed by the PM; the TW and the AE keep the final wording;
     mirrors safety.md on merge): "Filter-chain absent = no audio,
     proven on real PW." Why: US-174d adds `nofail` to the
     filter-chain module, so a failed load (a dangling `current` after
     ROLLBACK-FAILED, or a corrupt or missing WAV) leaves PW running
     with no convolver and no gains. Before amps-on, a real-PW/WP test
     shows, all in the convolver-ABSENT state: (1) zero links into
     USBStreamer playback ch 1-8; (2) the USBStreamer is not the
     default sink; (3) GM refuses DJ/live topology, its watchdog
     latches, and its fallback destroys the USBStreamer links; (4)
     behavioural, the deciding proof: a pw-play to the default target
     produces no USBStreamer link; (5) a JACK client with autoconnect
     forced on gets no USBStreamer link either (AE). Preconditions of
     the test: the daemon stays up, NRestarts is stable, and the
     convolver ABSENT state is reported loudly. Mechanism: a WP
     stream-target hook that refuses the USBStreamer as a target for
     Stream/* nodes, with a real-WP test, because WP falls back to the
     only remaining sink whatever priority or metadata says; changing
     media.class is ruled out (F-292). Today only GM's reactive link
     audit (link_audit.rs) covers this, and only while GM runs.
     Classification (AE ruling, via the Architect): NOT P1 now; a HARD
     pre-amps-on blocker, because the US-174d `nofail` creates the
     state it covers, so it is a real hazard under the frozen-list
     rule. Carrier (Architect, TW, PM agree): the US-174d PR carries
     the row into safety.md next to rows 15-17 and states the gap in
     its description; the hook itself is a separate later story. If
     the row lands: lead-in "The list has 18 rows. On the Pi 5, rows
     1-3 and 5-18 must ALL hold; row 4 applies to the Pi 4 only.",
     Gate rule "(1-3, 5-18)", and row 17's "there is no row 18" phrase
     goes (TW asked the AE). Open at the TW: the AE's final text and
     whether an operator-facing interim check goes alongside. Related,
     in US-174d: convolver priority.session 2100, so it is the default
     sink in the normal case.
     FINAL (AE accepted the row as a real hazard, via the TW,
     2026-10-26; SUPERSEDES the PROPOSED text above; mirrors safety.md
     on merge), AE verbatim: "18. Filter-chain absent ⇒ no audio.
     Proven on real PipeWire and WirePlumber, with the filter-chain
     failing to load: (a) the daemon stays up with no restart loop,
     and GM reports the convolver ABSENT; (b) no link exists into any
     USBStreamer playback port (ch 1-8), including after a pw-play to
     the default sink and after a JACK client with autoconnect forced
     on; (c) a WirePlumber hook refuses the USBStreamer as the target
     of every Stream/* node; (d) GM refuses to build the DJ or live
     topology, and its watchdog latches. With the filter-chain
     present, the convolver is the default sink."
     AE rulings: (c) is NOT P1 (the row is a hard amps-on blocker by
     itself); NO interim rule; carried in the US-174d PR with the
     lead-in "The list has 18 rows. On the Pi 5, rows 1-3 and 5-18
     must ALL hold; row 4 applies to the Pi 4 only." and the Gate rule
     "(1-3, 5-18)"; the OPEN footnote covers rows 15, 16 and 18 (TW
     batch with US-174d).
     CORRECTION (TW, 2026-10-26): the AE's row 17 text never said
     "there is no row 18"; that phrase was the TW's and the PM's own
     v186 note outside the quote. Strike "row 17's 'there is no row
     18' phrase goes (TW asked the AE)" above: nothing changes in row
     17's AE text, and the PM's v186 note is superseded by this row.
     HELD at the TW (AE to rule): a safety.md Section 5 pre-flight
     line, "`pw-metadata` shows the convolver as default.audio.sink".
     On main it fails today: the USBStreamer sink has priority.session
     2000, the convolver has none (OBSERVE-AE-sink-1 confirmed, see
     US-173). AE options: (A) an implementation requirement, or a
     reword. PM note: the Architect's addenda 3 and 4 already put this
     in US-174d (see US-174d), so (A) needs no new backlog item.
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
  TOP PRIORITY (PO, 2026-10-26; see the top of this file). DONE =
  labwc on HDMI with hardware V3D (GL renderer string, no llvmpipe) +
  /dev/dri + greetd after DRM + the stability run. AC2 AMENDMENT
  (Architect, via PO): AC2 counts only after a T3d-style stability
  run, not after "visible"; the verbatim AC2 sentence (run length,
  pass criteria) is requested from the Architect and lands in the next
  version. Architect estimate and risks: see the DJ PLAYBACK PATH item
  at the top. Status: US-172c recovery under CHG-US172c-1 (worker-2),
  the owner's cold power cycle done (~08:43).
  AC2 (Architect, verbatim, 2026-10-26; replaces the "requested from
  the Architect" note above; frozen copy
  /tmp/pm-backlog/us172-ac2-architect.txt):
  - [ ] AC2: D-022 re-confirmed on the Pi 5 by a stability run, not by
        "Mixxx visible" (architect, PO). Setup: after a cold boot of
        the deployed branch generation, on the PREEMPT_RT kernel
        (`uname -v` shows PREEMPT_RT) with PipeWire at SCHED_FIFO 88,
        start Mixxx under labwc/greetd on HDMI via `pw-jack mixxx`.
        Run 30 minutes continuously at quantum 1024 with two decks
        playing, waveforms shown, and audio running through the
        filter-chain convolver to the USBStreamer. Under the current
        "nothing connected" owner statement the gate may stay closed,
        because the graph processes either way. PASS needs all of the
        following:
    (1) The GL renderer is V3D, recorded from the Mixxx log or
    `eglinfo`/`glxinfo`; any llvmpipe/softpipe is FAIL.
    `/dev/dri/card*` and `renderD*` are present, and vc4 and v3d are
    loaded.
    (2) For the whole run there is no v3d/vc4/drm error, GPU reset,
    hung-job, or lockup message in `journalctl -k`; no hard hang; SSH
    stays responsive (polled at least every 60 s).
    (3) Zero xruns: the USBStreamer and convolver ERR counters in
    `pw-top` do not increase from minute 1 to the end, and there are
    no `XRun` lines in the PipeWire journal for that window.
    (4) Mixxx, labwc and greetd do not restart: NRestarts is 0 for
    each, the Mixxx PID is unchanged, and both failed lists are empty
    at the end.
    (5) Thermal and frequency per the D-069 rule: samples every 10 s.
    If any cooling_device cur_state is non-zero, the rpi_volt alarm is
    set, or cpuinfo_cur_freq < max, the run is INVALID and must be
    repeated, not counted as a pass. At ≥80 °C, STOP (INVALID).
    Recorded but not pass criteria: Mixxx CPU %, system idle %, PW
    daemon CPU %, peak temperature. If a 30-minute run passes on
    llvmpipe instead, it counts toward plan B only, never toward AC2.
  Why 30 minutes (Architect): it matches the Pi 4 T3d length. The Pi 4
  V3D/RT deadlock (F-012/F-017) showed up within minutes under load,
  so 30 minutes of real GL load catches that class. The 11-hour soak
  is not part of this AC; it belongs to a later gig-readiness check.
  Status UPDATE (CM, worker-2, 2026-10-26; corrects "the owner's cold
  power cycle done" above only in its basis): the cold cycle is
  CONFIRMED by /proc/uptime (boot ~08:44:31Z; see the lane status at
  the top). Firmware reset status 0x1000, no power, SD or USB faults;
  the Architect is decoding 0x1000 on the Pi 5. No DRM devices, greetd
  skipped, no compositor: that is the US-172 problem itself and
  explains the owner's "no Wayland at all".
  FINDING (worker-2, 2026-10-26; candidate defect, ID once the
  Architect rules): after the tryboot reboot on 2026-10-25 (clean
  shutdown 21:03:34Z), the Pi never booted until the owner's power
  cycle; boot -1's shutdown armed a 10-min hardware watchdog that did
  NOT fire overnight. The Architect's ruling on why is pending.
  Related: the CLAUDE.md watchdog-reliability TODO and AD L3
  (rt-tuning.nix:24 vs options.nix O-24).
  RULED (Architect, 2026-10-26): EXPECTED, not a new defect, no ID.
  The shutdown watchdog only covers up to the reset and no runtime
  watchdog is configured: the O-24 gap (F-317/F-325). The run-2
  tryboot most likely HUNG; "boot 0 1 s after boot -1" / "up within 40
  s" was a no-RTC timestamp artifact. rsts=0x1000 and power_reset=0
  are consistent with power-on (medium confidence; uptime is the
  authority). The HAT question is dropped for the diagnosis but stays
  relevant to US-172 AC6 (HiFiBerry gate). Before the step 7-8
  tryboot: (i) the owner watches HDMI (on the owner list; go only once
  the owner says they are at the screen); (ii) worker-2 diffs
  tryboot.txt against config.txt and checks the gens/<id>/ paths.
  US-172c one-liners (CM, worker-2, 2026-10-26): (a) us172-recovery.sh
  rec-2 old_present match is broken (it matches the id with a space on
  each side, but the list is one id per line); a fix means a new sha
  and re-review. (b) The step 4 pstore read needs sudo.
  (c) (CM, worker-2, 2026-10-26; backlog, not a blocker):
  /boot/firmware is mounted rw on the Pi 5 (read-only observation).
  Architect/SecSpec to rule pre-prod.
  Gains-read label (AE, verbatim, via CM, 2026-10-26): "first gains
  read after cold boot (boot ≈08:44:31Z per /proc/uptime, rsts=0x1000;
  read at <timestamp>, T+<mm:ss>; preceded only by read-only
  OBSERVE-US172c-1/2, no PW/WP/GM/web-UI actions)". The AE's four
  changes for the post-reboot read: a WARM label if the boot was soft;
  read once pipewire, wireplumber and graph-manager are active, not
  after a fixed wait; GM gate/venue only through a read-only query;
  VOID captures kept separate. After the second power pull the boot
  reference becomes about 08:57:40Z (boot 60f384a1, owner power pull);
  the read runs under OBSERVE-US172c-4.
  Label AMENDED (AE, via CM, 2026-10-26): "cold boot, but an
  unattributed SSH session at T+44 s". The journal can't clear the
  T+44 s session; only the owner's statement can. Any pw/wp/sudo line
  from that session makes the read "not clean". The owner was asked
  via team-lead what the session ran; nothing waits on the answer.
  RESULT (AE, 2026-10-26): OBSERVE-US172c-4 PASS, boot 60f384a1 (fresh
  boot after power loss or hard reset), T+04:58: both nodes running
  before and after the read, the 8 Mult values all 0.000000 via
  pw-cli, node counts 1 and 1 (record ffc000b5...f08d). Qualifier: an
  unattributed SSH session at T+00:44, pending the owner's word.
  Scope: PW start state only; GM restart, profile activation and
  unlatch are not covered.
  AE ruling, verbatim (via CM, 2026-10-26): "PASS, fresh boot after
  power loss or hard reset (60f384a1), T+04:58, F-395-verifiable;
  qualifier: unattributed SSH session at T+00:44". Scope: PW start
  state on this image only; not a GM restart, profile activation or
  unlatch (F-320-E/F-348/F-320-D). The frozen amps-on list is
  untouched. Evidence observe4/GAINS-RECORD.txt, sha256
  ffc000b5...f08d.
  OBSERVE-US172c-4 completed and released 09:05:29Z (CM, 2026-10-26).
  GAINS-RECORD-v2 (observe4b/, sha256 a465a8ad...4528): two reads
  (T+04:58, T+07:47) with pipewire, wireplumber and GM active, 8/8
  Mult 0.000000, links and Props unchanged across 4 dumps; GM
  get_gate: gate_open=false, has_pending_gains=false, venue=null. The
  T+00:44 session is logind session 2 (pts/0, from .36), STILL OPEN;
  only sshd/logind lines for it.
  Tryboot evidence (CM, 2026-10-26): the run-2 boot 6842870c has no
  "Restarting system" line (journald stopped first); the run's own
  tryboot steps are logged. No boot was recorded between run 2 and
  08:44Z, which fits the Architect's "tryboot hung before journald".
  Kernel config: RASPBERRYPI_FIRMWARE, RASPBERRYPI_POWER,
  RESET_RASPBERRYPI and BCM2835_WDT all =y. The FAT config.txt equals
  the saved original; tryboot.txt (run-2 armed) was still present
  before step 7.
  FAT line order (CM, 2026-10-26): tryboot.txt has
  os_prefix/kernel/initramfs/cmdline and overlay_prefix=o/ BEFORE the
  dtoverlay lines; config.txt has them after. The Architect is ruling
  whether that is the cause candidate.
  Steps 7-8 (CM, 2026-10-26): CHANGE CM-CHG-.89-US172c-78 was granted
  to worker-2 for step 7 (tb-restore) and step 8 (tb-normal, a plain
  reboot, announced); the HDMI-watch condition applies to the next
  tryboot. It is now SUSPENDED before use: tb-restore would delete
  tryboot.txt and o/, which the Architect may want for run 3. Pending
  the Architect's ruling.
  CORRECTION (CM, team-lead, 2026-10-26): the suspension came too
  late. worker-2 had already run step 7 (tb-restore, all VERDICT ok):
  gens/<id>/o, tryboot.txt and us172-fat-backup.tar removed;
  config.txt and the FAT manifest identical. The Architect OK'd step 8
  (tb-normal, plain reboot) as announce-only, with Mac-side poll
  timestamps. Architect rule: not back in 10 min is a finding ("needs
  power pull"), and the diagnosis becomes "Pi 5 reboot/reset path on
  this kernel".
  Step 8 outcome (CM, 2026-10-26): tb-normal issued 09:06:58Z, down
  09:07:14Z, up 09:07:45Z (31 s); new boot aae07160, base generation
  rcyg67wd, tryboot flag 0. RESTORED PASS, 0 findings: 16 gains at 0;
  gate closed, venue null; links 24 unchanged; FAT manifest equal to
  PRE; tryboot.txt and o/ absent. Thermal max 66.1 °C.
  CM-CHG-.89-US172c-78 released 09:09Z. The Architect's 10-min branch
  did NOT trigger, so plain reboots work on this kernel. LIBPI root
  /home/ela/.us172-libpi stays until US-172 closes.
  Tryboot evidence off-Pi (CM, 2026-10-26), in the run dir:
  tryboot.txt sha256 04827191..., orig-config.txt ff08471f...,
  fat-manifest-armed.txt; CM diff observe4b/cm-config-vs-tryboot.diff
  (89853ceb).
  AE (via CM, 2026-10-26): GAINS-RECORD-v2 (a465a8ad) ACCEPTED. Read 1
  (T+04:58) is the primary proof; read 2 is confirmation only. The
  T+00:44 session stays a recorded qualifier: nobody touches it, no
  owner question. Addenda: observe4/GAINS-RECORD.ADDENDUM.txt
  (babd9c68), observe4b/GAINS-RECORD-v2.ADDENDUM.txt (5852758c).
  Run-3 ruling (Architect, via CM, 2026-10-26): the FAT line order is
  the PRIMARY cause candidate, not proven; the alternatives are a
  firmware-stage halt and an o/ dtbo mismatch. tryboot.txt and o/ were
  wanted kept, but steps 7-8 had already run, so run 3 re-creates them
  via tb-pre, verified against the off-Pi copies. Diagnostic
  visibility only: no disable_splash; cmdline-run3.txt without quiet,
  with console=tty1 and ignore_loglevel. The owner watches HDMI and
  photographs at about 10 s / 30 s / 90 s / 3 min; 5-min outcome
  branches. worker-2 is preparing it for QE review.
  Owner list item (physical, never ask for a time slot): run 3 waits
  until the owner says they are at the screen, with the HDMI monitor
  the only device connected.
  CORRECTION (Architect amendments, via CM, 2026-10-26; to the run-3
  ruling above): KEEP disable_splash=1 (the Architect's parse marker;
  "no disable_splash" is withdrawn). o/ vs the base dtbo is settled
  off-Pi as byte-identical (10aed856..., aa13a7df...), so the "o/ dtbo
  mismatch" alternative and its PRE are dropped. Restage from the
  off-Pi copies, with a line-for-line check against
  fat-manifest-armed.txt and a check that gens/<id>/ still exists. The
  only change from run 2 is cmdline-run3.txt (without quiet, plus
  console=tty1 ignore_loglevel), at the top level of gens/<id>/ next
  to cmdline.txt. Architect conclusion: the 31 s plain reboot shows
  the reset path works, so the run-2 hang is specific to tryboot/H1.
  QE run-3 evidence criteria (via CM, 2026-10-26, as adjusted):
  - tryboot.txt differs from run 2 by EXACTLY one line (cmdline=),
    shown as a diff against 04827191...;
  - o/ and gens/<id>/{Image,initrd,cmdline.txt} sha256 equal to
    fat-manifest-armed.txt; full cmdline-run3.txt content plus diff;
  - after restore: cmdline-run3.txt absent, a RESTORED-PASS manifest,
    and state equal to post-steps-7-8;
  - outcome branches with pass/fail/inconclusive named up front; a
    base-generation boot is NOT run-3 evidence;
  - the timeline from Mac-side polls; worker-2 adds an ICMP poll plus
    /proc/uptime at first SSH.
  Step-8 timing precision (CM, 2026-10-26): the first ping was NOT
  measured (SSH-only poll) and /proc/uptime at first SSH was NOT
  captured. Not a finding.
  Run-3 review (CM, 2026-10-26): the QE APPROVED with C1-C3 and the
  Architect APPROVED; both agree with the CM changes (keep
  disable_splash=1; no nix shell dtc; nix copy only if the root is
  absent, otherwise STOP). C1: the one-line diff plus the restored m=1
  marker verdict and the full H1 positive control. C2: a
  TRYBOOT/NOT-TRYBOOT classification line. C3: tb-diag requires
  US172_C3SHA. worker-2 is revising; the kit is NOT frozen yet
  (interim pins 21be4395/9876375e carry change 1 only). Sequence: the
  QE's C4 diff-only check; OBSERVE pre-obs, output to the QE and
  Architect; CHANGE tb-pre and tb-diag; then tb-reboot only with the
  owner at the HDMI screen.
  Run-3 plan v2 (CM, 2026-10-26) at the interim pins
  21be4395/9876375e: the tryboot diff is one line (3fb3e46d) and the
  marker is restored. Still outstanding at worker-2: change 2 (nix
  shell dtc, nix copy), QE C2 and C3. NOT frozen.
  UPDATE (QE, CM, 2026-10-26): the v3 kit is APPROVED. QE C4
  (diff-only): us172.sh 3cd7509b, us172-drm-reads.sh 91ffcb6e, the
  other 4 files unchanged; C1-C4 MET. Verdict verbatim at
  /tmp/us172-run3-C4-QE-verdict.md (sha256 ce71a587), for the US-172
  PR. Nit (non-blocking): the pull-obs usage text doesn't mention $2,
  the power-pull time. The Architect CONFIRMED v3; the raw .dtb
  "differs" in tb-post is expected (/chosen), not a finding.
  OBSERVE-US172r3-pre is granted to worker-2 (pre-obs only). Next: its
  output (cmdline-run3.txt plus C3SHA) to the QE and the Architect,
  then the tb-pre/tb-diag CHANGE grants naming C3SHA; the tryboot
  reboot only once the owner says they are at the HDMI screen.
  UPDATE (CM, 2026-10-26): pre-obs DONE 09:38Z, all 6 ok. C3SHA
  5dd65567 (cmdline-run3, 182 B) = the base cmdline plus "
  ignore_loglevel" only; tryboot-run3.txt = TB3SHA 3fb3e46d with only
  the cmdline= line changed. Finding: the base cmdline already ends
  with console=tty1 and has no quiet, so only ignore_loglevel tells
  tryboot from base. The QE (5523ca53, bytes checked) and the
  Architect ACCEPTED the pre-obs output and C3SHA; no kit change.
  CHANGE-US172r3-diag granted to worker-2 at 09:53Z: tb-pre, then
  tb-diag; arms tryboot; NO reboot. The tryboot reboot waits for the
  owner to say they are at the HDMI screen.
  QE one-liner (LOW; fix at US-172 close-out, text only, no re-review
  now, Architect agrees): the kit comment "moved off by console=tty1"
  is wrong for this Pi, and the drm-reads checks "quiet absent" and
  "tty1 present" do not tell tryboot from base; only c3
  (ignore_loglevel) does. Note it in the run-3 report.
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
  - Gate-2 reviews complete (via CM, 2026-10-25): AE CHANGES (B1
    read the gains via pw-cli enum-params; R1 read the D-063 gate;
    R2 a failed sink restore is a STOP). SecSpec APPROVED both
    scripts, with a CM lock-release condition (configured default
    and target.object restored) and lows 1-3. Architect CHANGES (C1
    check the WP default-nodes state file; N1-N3). QE CHANGES for
    the full run (G1-G4); --preflight-only APPROVED as-is on
    OBSERVE. worker-3 has the batched list and is editing; builds
    stay held (Mac disk).
  - F-390 GATE (PO, 2026-10-25): no US-173 session that loads
    speaker or crossover configs (measurement, CP-5) starts before
    F-390 is met, or the AE-accepted fallback is in place. Gate
    wording with the AE. See F-390. Final gate text (AE): see
    F-390. F-391 gates the same sessions.
  - Gate-2 r2 (CM, 2026-10-25): gate2.py dda3bfcf, selftest
    f72a0aba, out for diff-only re-review by AE, Architect and
    SecSpec; the selftest is held on disk (2.3 GiB).
    Gate-2 r2 verdicts (CM, 2026-10-25): SecSpec APPROVED at
    dda3bfcf/f72a0aba, with 1 new LOW: an unexpected exception escapes
    without writing summary.txt (worker-3 fixing). Architect
    CHANGES-REQUESTED: C1a wp_state fails open on a read error; C1b
    the selftest must exercise the WP history replay on a real sandbox
    WP with history [B, A], plus a negative case; N4/N5 non-blocking.
    AE pending. worker-3 is fixing. A fresh selftest at the final
    hashes is required (held on disk).
    Interim rule (SecSpec, via CM, 2026-10-25), until the LOW fix is
    in: any Gate-2 run without summary.txt or with a traceback counts
    as STOP; the CM checks sink, target.object, the 16 gains and the
    gate before releasing the lock.
    Gate-2 r2 AE CHANGES (via CM, 2026-10-25): R2b a restore failure
    in the finally block must still STOP and still run the checks; E1
    a fresh selftest. worker-3 is fixing (with SecSpec's LOW and the
    Architect's C1a/C1b).
    Gate-2 r3 (CM, 2026-10-25; verdicts /tmp/w3-gate2-verdicts-r3/):
    gate2 b226c0ba, selftest 9d941567, SUMS 6f34661c. SecSpec
    APPROVED, its LOW closed. AE APPROVE on the code; E1 (fresh
    selftest) still open. Architect: gate2.py b226c0ba APPROVED;
    selftest CHANGES S1 (None-default branch coverage) and S2 (C1a
    unreadable-state cases). worker-3 adds S1/S2, then runs the fresh
    selftest. The disk hold on the selftest is lifted (5.3 GiB free;
    CM cleared worker-3).
    Gate-2 r3 selftest at 9d941567 did NOT pass (CM, 2026-10-25;
    evidence /tmp/w3-gate2/selftest-r3-result/, sums 631930a2,
    verified). P1, a real finding: `pw-cli s ... Props gain_a:Mult
    0.5` exited 0, but enum-params AND pw-dump both still read 0.0.
    worker-3 withdraws the "enum-params verified live" claim; this
    affects AE B1. P2, a selftest bug: the setparam run's WirePlumber
    restart dropped the GM stand-in link, so C1b, Perturb and
    FailReplay were not exercised yet.
    Joint AE + Architect ruling (via CM, 2026-10-25; verbatim
    /tmp/w3-gate2-rulings/joint-AE-Architect-r3-gain-readback.md,
    sha256 c6dd26c2; PM frozen copy
    /tmp/pm-backlog/joint-r3-gain-readback-c6dd26c2.md): H1 the set
    never applied, or H2 the readers don't see runtime sets; the
    readback alone can't tell them apart. r4 is selftest only
    (gate2.py stays b226c0ba): (a) re-create the GM link per run; (c)
    setparam fails early if its gains read 0; Architect S1/S2; plus a
    sandbox matrix T1 (separate client) and T2 (in-daemon, the Pi
    topology), each idle and with a stream, recording per cell pw-cli,
    the enum-params poll, pw-dump, the output RMS via a sine (b5) and
    a -0.0 print control (b6). T2 decides: the set applies AND the
    readers see it -> H2 false for the Pi topology (T1 blindness is a
    sandbox artefact; the negative setparam case moves to T2); the set
    applies but the readers stay 0 -> H2 true, a P1 AE finding against
    safety.md check 10 / AE B1 (fallback reader: the US-159 raw-bits
    reader or an output-level check). F-ID held until T2 classifies
    it. (b) set-param diagnostics and the build waited for this
    ruling.
    B1 rule unchanged. The Gate-2 report must say "gains: boot
    defaults verified; live readback unproven (r3 finding)". The
    Gate-2 Pi run may proceed once the r4 selftest passes; it stays
    silent, with no gain writes. RULE: no amps-on step counts the
    gains readback as live proof until T2 shows H2 false AND the Pi
    -0.0 readback check (below) has passed. The TW is told to hold or
    caveat the safety.md "Gains at boot" bullet (F-318 v10); the
    amps-on list here follows the merged safety.md wording. Disk 5.2
    GiB after one ~8 MB build.
    AE confirmed option (A) (CM note in the ruling file, 2026-10-25;
    file now sha256 dccaffd0, PM frozen copy
    /tmp/pm-backlog/joint-r3-gain-readback-dccaffd0.md): "Point 2 as
    sent: Gate-2 on the Pi may run once the r4 selftest passes." It
    runs under nothing-connected, silence only and no gain writes, and
    its report carries "gains: boot defaults verified; live readback
    unproven (r3 finding)". The AE's earlier "held" line is
    superseded. Addendum (Architect + AE): point 4 wording follows the
    AE: "(live readback under investigation, Gate-2 r3)". Point 3
    fallback: see the Pi -0.0 readback check item.
    r4 progress (CM, 2026-10-25): worker-3's selftest edits are in
    gate2_selftest.py 67008fd7 (diff vs 9d941567: fa00acda); gate2.py
    b226c0ba and selftest.nix 90258d73 unchanged. Done: (a) GM link
    re-created per run, (c) setparam probe fails early, S1 the
    NoneDefault run, S2a and S2b. Being added: (b) and the T1/T2
    matrix; then one build and run. Disk-rule breach (CM logged):
    worker-3 ran an uncleared `nix run
    nixpkgs#python3Packages.pyflakes` (1.1 MiB fetched; no harm, 5.2
    GiB free); the disk hold covers nix run, so every nix build/run
    needs CM clearance first.
    r5 (CM, 2026-10-25): r5 build running (gain_matrix.py 7050eac2).
    The AE and Architect validity conditions went to worker-3. One r6
    build is pre-cleared (CM, disk hold) if r5 does not capture them.
    r5 RESULT (CM, 2026-10-25; results SUMS 222b787c): the matrix
    shows the gain set applies AND both readers see it, in T1 and T2,
    idle and with a stream: H2 is FALSE for the Pi topology, so no H2
    F-ID. applied() misfired on sandbox zero-dropouts (the level reads
    -26.02 with them removed). -0.0 is normalised to 0 in T2, so the
    Mult 0.001 fallback is triggered; it needs the owner's S-012 OK,
    with the AE's plain-language explanation first (to team-lead once
    the joint ruling is out; non-blocking). The selftest set-param
    still fails with the filter-chain suspended. Joint AE + Architect
    ruling on options (i)-(iii) PENDING; worker-3 holds. The RULE
    above (no amps-on step counts the readback as live proof) stays
    until that ruling.
    JOINT r5 RULING FINAL (AE + Architect, via CM and team-lead,
    2026-10-25; /tmp/w3-gate2-rulings/joint-r5-ruling-final.md sha256
    bb52fa60, base + Addenda 1-2; PM frozen copy
    /tmp/pm-backlog/joint-r5-ruling-final-bb52fa60.md; supersedes
    "joint ruling PENDING" above and the Mult 0.001 / owner S-012
    fallback in the Pi -0.0 check item, so NO owner question goes
    out). Option (i) YES with the AE's rules a-e; (ii) YES, REQUIRED
    (the Pi-relevant cell); (iii) NO as a fix. applied(): level within
    0.5 dB AND peak within 0.1 dB over covered frames (Addendum 2; A2
    withdrawn); MIN_FRAMES 48000 covered gain_b frames (A1). Gains
    status line for Gate-2 reports, verbatim (supersedes "gains: boot
    defaults verified; live readback unproven (r3 finding)"): "Boot
    defaults verified; live readback proven for a node that has
    already run (sandbox, r5 interim); suspended state and Pi
    unproven." Amps-on use of the readback as live proof needs (ii) in
    r6 plus the Pi check. Pi check = P-a, NO owner gate: a temporary
    UNLINKED test filter-chain in the production daemon; (a)
    autoconnect=false, no target.object, conf Mult 0, no stream
    linked; (b) pw-link -l before, after the set and after the unload,
    any device-port link = abort and unload; (c) Add read back as
    0.000000, nothing writes Add; (d) OBSERVE the production node
    state first, read the test chain in the same state, interpret via
    the r6 (ii) decision table; (e) same PW version and build, same
    daemon (T2); (f) only after the r6 (ii) result. LAST RESORT, only
    if P-a is inconclusive: production Mult 0.000001 (-120 dB) with
    the owner's S-012 OK and the AE's plain-language text (A4). A5: if
    (ii-c) comes out blind, the AE co-owns a P1 against B1 / safety.md
    check 10 and sends new interim text for D-070 rows 14-15 to the PM
    and the TW (amps-on rows 14/15 follow). r6: gain_matrix.py
    c3ce65ee plus sections 3-5, ONE rebuild, no pre-build review; the
    AE and Architect review the diff with the r6 results; gate2.py
    stays b226c0ba until (ii) needs a change. worker-3 is rebuilding
    (CM relayed).
    UPDATE (CM, 2026-10-25; supersedes "r6: gain_matrix.py c3ce65ee
    plus sections 3-5" above): r6 is NON-COUNTING. worker-3 ran
    gain_matrix c3ce65ee BEFORE the final ruling reached them (SUMS
    a84e6ed8). All validity conditions held; T2 running gave 0.5 at
    -26.02 dB and 1.0 at -20.00 dB; the other cells were lost to
    dropouts of up to 95%. r7 = c3ce65ee plus ruling items 3-5: the
    one cleared build, pending. Read every "r6" in the ruling above
    (the (ii) decision table, condition (f), the AE/Architect diff
    review) as r7.
    r6b RESULT (CM, 2026-10-26; supersedes "r7 ... pending": the one
    cleared build is named r6b, not r7): gain_matrix 396a1a69 (final
    ruling built in), results SUMS 38cbc645 (438 files), build log
    9dbfbaa0, rev 142a3523, nix exit 0. Validity: all conditions met;
    no INVALID cells, no NO DATA. Main matrix T1 and T2, idle and
    running: the set applies and both readers show it; H2 false.
    (ii-a): a set made while suspended is not lost; it applies after
    the resume; only the suspended readback is stale (this also
    explains the selftest set-param FAIL). (ii-b): boot 0, then
    resume: silent. (ii-c) BLIND: on a suspended node the readers
    return 0, not the stored conf value. Per the decision table this
    is a P1 against B1 / safety.md check 10, AE co-owned (A5): F-395.
    The AE sends the PM and the TW interim text for D-070 rows 14-15;
    amps-on rows 14/15 here change only on that text. Next: the AE and
    Architect rule on the gate2.py design (refuse suspended nodes vs
    wake them with a silent stream) and on whether the Pi P-a check is
    now due; worker-3 holds. The cleared build is used up; disk at 4.3
    GiB. r5 and r6 stay non-counting records.
    JOINT r6b RULING FINAL (AE + Architect, via CM, 2026-10-26;
    /tmp/w3-gate2-rulings/joint-r6b-ruling-final.md sha256 b7c4a4fd,
    Addendum 1 e011714f, Addendum 2 10ca06f6, each addendum wins where
    they differ; PM frozen copies
    /tmp/pm-backlog/joint-r6b-ruling-final-b7c4a4fd.md,
    joint-r6b-addendum-1-e011714f.md,
    joint-r6b-addendum-2-10ca06f6.md; supersedes "Next: the AE and
    Architect rule..." and "worker-3 holds" above). The AE draft is
    adopted in full, with [ARCH] additions:
    - r6b COUNTS (both checked the raw data).
    - Cap: the code must match r6 note 1 exactly before any next
      build. A phase that reaches the hard per-phase wall-time cap is
      NO DATA + INVALID, even with >= 48000 covered frames; "cap
      reached" is flagged per phase; a selftest case covers it. r6b is
      unaffected (no phase reached the cap).
    - gate2.py base rule (F-395 AC (a)): a gains reading counts only
      if the production filter-chain node AND its output node are idle
      or running, from state snapshots taken immediately BEFORE and
      AFTER the enum-params read; a change between them is NOT
      VERIFIABLE. NOT VERIFIABLE is reported as FAIL (exit 1), reason
      "gains not verifiable: <node> state <before>/<after>"; no new
      exit code; never retried into a PASS. B1 unchanged: enum-params
      is the only PASS source.
    - Selftest cases, each with a reason check: (1) never-run
      suspended node, conf Mult 0: NOT VERIFIABLE; (2) the same with
      conf Mult 0.25: NOT VERIFIABLE (the AE's mutation, F-395 AC
      (b)); (3) a node that has run (idle), Mult 0: PASS; (4) the
      same, runtime Mult 0.5: FAIL; (5) the state changes between the
      two reads: NOT VERIFIABLE. The suspended set-param probe now
      expects NOT VERIFIABLE.
    - WAKE MODE is NOT part of this change: Gate-2 stays read-only. If
      the Pi OBSERVE shows the production chain suspended or never run
      at boot, wake mode becomes a separate joint design (AE
      conditions plus GM/link-audit coordination).
    - Interim consequence (Addendum 1 B, fail-closed, accepted by the
      AE and the Architect): if the Pi chain is suspended or never run
      at boot, Gate-2 cannot pass until the canary (US-176) or the
      no-suspend fix (F-396) lands.
    - Pi P-a is DUE. Step 1 (OBSERVE): the state of the production
      filter-chain, its output node and the USBStreamer node at idle
      and right after the next announced boot; it also re-runs US-163
      check #10 and AC14 under the new rule (F-395 AC (c), CM folds
      them in). Step 2 (CHANGE): P-a with condition (f) amended: the
      only stream is an exact-digital-zero stream linked only into the
      test chain's INPUT; the test chain's output goes to a DEDICATED
      null sink (support.null-audio-sink, no device), now standard,
      created for the test and removed afterwards (Addendum 1 D,
      supersedes the [ARCH] "optional" null sink);
      node.autoconnect=false on every test node; WirePlumber's default
      sink identical before and after (logged); the null sink's
      monitor recorded throughout and exact zeros throughout; (b) and
      (c) unchanged (pw-link -l at every step, no device-port link at
      any time, Add 0.000000). Test-chain conf: gain_a Mult 0, gain_b
      Mult 0.25. Sequence: 2.1 read while suspended (a MEASUREMENT,
      not pass/fail, Addendum 2 item 2: if gain_b reads 0.25 there,
      the Pi reader is not blind there; logged, does not fail the
      run); 2.2 start the zero stream and read (expect gain_b 0.25);
      2.3 set gain_a 0.5 and read (expect 0.5); 2.4 set 0 and read;
      2.5 stop the stream and unload. Steps 2.2-2.4 are pass/fail. No
      device path changes gain, so S-012 does not apply. Production
      Mult 0.000001 stays the last resort only.
    - Gains status line for Gate-2 reports, verbatim (supersedes the
      r5 interim line above): "Boot defaults verified ONLY where the
      node state at the reading was idle or running (otherwise
      unproven). Live readback proven in the sandbox for non-suspended
      nodes (r6b). Suspended state: readers blind (P1). Pi: pending
      OBSERVE + P-a." Amps-on use of the readback still needs P-a to
      pass, plus the gate2.py base rule merged.
    - Status (CM, 2026-10-26): worker-3 is implementing the base rule
      (a-d, no wake mode) plus the exact cap fix; one sandbox build
      cleared. The Pi steps are DEFERRED: the Pi 5 .89 is down (no
      ping), waiting for the owner's power cycle in the US-172c
      recovery.
    - r7 RESULT (CM, 2026-10-26; supersedes the Status line above):
      worker-3 build at US-173 rev 142a3523 (gate2.py e8a39667,
      gate2_selftest.py 2899cfe6, gain_matrix.py 238b3841); results
      /tmp/w3-gate2/selftest-r7-result/ (SUMS e9d5b394), log d8dc52aa.
      Selftest 4 FAIL / 9 PASS: G1-G5 and the cap case PASS;
      gain_matrix verdicts are the same as r6b. NEW finding: after the
      step-6 WirePlumber restart, fc and fc-out both re-suspend, so
      the cleanup gains readback is NOT VERIFIABLE (STOP, exit 3), and
      S2a, S2b, C1b-negative and fail-replay were not exercised
      (Abort, exit 2 at step 0). Exit codes deviate from the ruled
      "exit 1".
    - JOINT r7 RULING (AE + Architect, 2026-10-26;
      /tmp/w3-gate2-rulings/r7-exitcode-joint.md sha256 65555e73,
      frozen copy /tmp/pm-backlog/r7-exitcode-joint-65555e73.md): (1)
      exit codes ACCEPTED as built: NOT VERIFIABLE gives Abort exit 2
      at step 0 (including --preflight-only) and STOP exit 3 at
      cleanup; never PASS, never exit 0, no new exit code. Condition:
      the reason stays visible: the FAIL line carries "gains not
      verifiable: <node> state <before>/<after>", the summary tells it
      apart from a value FAIL (G4) at the same exit code, and the QE
      confirms this in the r7 output; the selftest assertions on the
      reason stay. Record line (AE, verbatim): "Addendum 1 B amended:
      NOT VERIFIABLE = exit 2 at step 0, exit 3 at cleanup
      (r7-exitcode-joint)." The TW and PM record that exit 2/3
      includes NOT VERIFIABLE wherever gate2's exit codes are
      documented. Non-blocking for the next touch: append "(not
      verifiable)" to the Abort/STOP top line. (2) The step-6
      re-suspend is a real finding (F-396), not a harness bug; STOP is
      correct; gate2.py stays read-only with no wake; the cleanup
      states.json goes into the results. (3) Diff review: no blocking
      issues; two stricter-than-ruled points accepted (any state
      change between the snapshots is NOT VERIFIABLE; a missing node
      is bad); "cap reached = not met" fails closed and is accepted.
      Non-blocking: the r7 summary quotes G2's "values alone" field as
      the blindness evidence.
    - Selftest re-wake (AE + Architect agree, 2026-10-26; joint text
      to the CM): only gate2_selftest.py re-wakes, never gate2.py; it
      re-wakes before S2a, S2b, C1b-negative and fail-replay, and each
      must start idle/idle. In the main run, a WP restart that leaves
      the chain suspended gives exit 3 with the cleanup NOT VERIFIABLE
      as the only failed check: a KNOWN FINDING F-396. If the nodes
      are idle or running, exit 0 is expected, logged as "F-396 not
      reproduced". Anything else is FAIL. One build follows (r8).
    - JOINT r7 RESULTS (AE + Architect, 2026-10-26;
      /tmp/w3-gate2-rulings/r7-results-joint.md sha256 a4ad5338,
      frozen copy /tmp/pm-backlog/r7-results-joint-a4ad5338.md; both
      read the raw files, SUMS e9d5b394): ACCEPTED: the readback, cap
      and state-rule parts (matrix identical to r6b; cap case INVALID;
      G1-G5, the probe and the wake PASS in policy and control; G2
      logs "values alone pass (blind)"; the NV reason is visible in
      every FAIL line and in the summary, which the QE confirmed). NOT
      YET COMPLETE: the selftest; S2a, S2b, C1b-neg and fail-replay
      never ran their logic. Finding (F-396 evidence): across the
      step-6 WP restart every node goes to suspended, including fc,
      fc-out, the convolver and the sandbox USBStreamer node
      (policy/pw-mon-step6.txt), despite suspend-timeout 0 and
      pause-on-idle false; no suspend message in the logs, mechanism
      unknown (AE hypothesis: WP re-adopts the node).
    - Remedy (c) + (a); (b) REJECTED. gate2.py: logic unchanged, only
      the non-blocking "(not verifiable)" top-line suffix.
      gate2_selftest.py, ONE edit: (1) before EACH of S2a, S2b,
      C1b-neg and fail-replay, re-wake with the same pw-link-only
      flow_start/flow_stop as the existing wake, logged as
      preparation; each must start at idle/idle (else harness FAIL)
      and reach its intended exit (1/3/3/3) with its intended reason;
      (2) the main-run cleanup outcome is ASSERTED (policy and
      control): suspended after the restart gives exit 3 with the ONLY
      failed check "gains not verifiable: f318-fc state
      suspended/suspended ..." and a FINDING line "WP restart
      re-suspended the filter-chain (F-396)"; idle or running gives
      exit 0, logged "F-396 not reproduced" (PASS, joint addendum);
      anything else FAIL; (3) synthetic gains self-cases on a fixed
      zero base, never on live state. The CM cleared worker-3 for ONE
      edit and ONE build (r8); the joint re-review covers the r8 diff
      and results.
    - Pi implications (Q3): the --wp-restart cleanup verdict is "STOP,
      F-396", never a pass, until F-396 lands. The D-070 row 15
      interim stands: after a WP restart the amps stay off until a PW
      restart or a cold cycle, with the gains verified. Production may
      differ (GM links convolver-out to the USBStreamer driver); the
      Pi settles it. P-a never restarts WP or makes WP re-adopt the
      test chain; if the null sink is created via WP or pw-cli, log
      the states after creation and at every read. No other P-a
      change.
    - r8 IDLE-BRANCH JOINT (AE + Architect via the Architect to the
      CM, 2026-10-26;
      /tmp/w3-gate2-rulings/r8-idle-branch-joint-cm-copy.md sha256
      e74a6e93, frozen copy
      /tmp/pm-backlog/r8-idle-branch-joint-e74a6e93.md): plan AGREED;
      let r8 finish; if r8 reproduces the suspend, it counts as built
      for the suspended branch. (c) CONFIRMED: idle branch, policy
      exit 0, control exit 1, cleanup gains check PASS; suspended
      branch, exit 3 in both modes, NV the only failed gains check.
      (a) accepted for r8 as built (fails closed). ONE small edit
      folds into the next build that is needed anyway (no separate
      build), limited to the main-run cleanup assertion in
      gate2_selftest.py: (1) branch selection uses BOTH entries
      (before and after) of gate2's gains-after-states.json: idle
      branch both idle or running, suspended branch both suspended; a
      missing file, a mixed set or an unknown state is FAIL;
      node-states-wp-restart.json stays as F-396 evidence, not
      asserted; (2) control mode, both branches (AE finding): the set
      of non-gains FAIL names must EQUAL the by-design policy-FAIL set
      from fail-r7-control.txt, stated explicitly in the code; (3)
      idle branch logs "F-396 not reproduced (sandbox)", NOT evidence
      that F-396 is fixed; the Pi --wp-restart verdict stays "STOP,
      F-396" until F-396 AC 3/4 is done. Process note (CM): worker-3
      declared an uncleared cached `nix run` (pyflakes); disk
      unchanged; logged.
    - r8 RESULT (CM, 2026-10-26): selftest 18/18 PASS in both modes;
      F-396 reproduced (suspended branch). Artifacts
      /tmp/w3-gate2/selftest-r8-result (SUMS 16065f52). Gate-2 is
      STOPPED here: PRE-PROD (P2, PO re-plan); the e74a6e93 edit, P-a
      and the F-396 Pi observation are not started. worker-3 moved to
      US-173 core prep.
    - worker-3 state line (via CM, 2026-10-26), verbatim: "Gate-2
      (F-318 a) PARKED as pre-prod (PO re-plan, 2026-10-26). r8 PASS:
      selftest 18/18 in policy and control, matrix exit 0; F-396
      reproduced (WP restart re-suspends fc/fc-out, cleanup NV = STOP
      exit 3 as designed). r8 code: gate2.py 71d3bd75,
      gate2_selftest.py 96a4ac4d, gain_matrix.py 238b3841. Results
      /tmp/w3-gate2/selftest-r8-result (SUMS 16065f52, 540 files);
      store 03qgvdfj and r7 fmfn3rp0 kept. Open: e74a6e93 gaps 1-3
      (branch selection on before+after, explicit control FAIL set,
      idle-branch log), not cleared."
  - a9addc52 evidence (worker-3, via CM, 2026-10-25):
    /tmp/w3-f318-evidence-a9addc52/ (SUMS 904ee759). Built from the
    pre-commit worktree; its provenance file explains why it is
    valid. A clean-rev rebuild only if the QE asks for one.
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
  NEW AC (PO, 2026-10-26; combined with amps-on row 7, the manual link
  check, not a second check; Architect wording overrides): "Before the
  first Mixxx test, in an OBSERVE session: GM in DJ mode with quantum
  1024 confirmed; `pw-link -l` dump compared with the GM routing
  table. Every expected link present, no extra links (incl. WP
  auto-links) to USBStreamer ports. Deviations are fixed and the dump
  repeated before the gate opens. Dump in the lab note."
  Branch (CM, 2026-10-26): story/US-173-first-dj-session = b973e3d9:
  main f01e6647 merged (7f2d4e8c), then the F-318 v18 docs batch
  committed. F-318 v18: LANDED, TW verification pending (one safety.md
  hunk applied with fuzz against main's "Pi 5 row (1-3, 5-14)"
  context).
  UPDATE (CM, TW, 2026-10-26): F-318 v18 at b973e3d9 is TW-VERIFIED
  (the TW's own re-apply is byte-identical); "TW verification pending"
  is DONE. The fuzz note refers to the same file: sha1 3f1a578f,
  sha256 404d880d. TW non-blocking review note for the US-173 PR: the
  "added by PR #45" check-10 sentences stay accurate while #45 is
  parked.
  worker-3 core plan APPROVED (CM, 2026-10-26): M1 GM DJ link set +
  unit test; M4 thermal watch script; M5 Hercules mapping check; then
  M2 venue WAVs (after F-374); then M3 sandbox rehearsal. P1-P4 need
  the Pi and come after US-172.
  UPDATE (CM, 2026-10-26): branch head 2fd7b252: M1 done, GM unit test
  dj_signal_path_is_exactly_mixxx_convolver_usbstreamer, 292/292
  green. worker-3 is on M4/M5.
  UPDATE (CM, 2026-10-26): M4 pushed, head deb48561:
  pi5_thermal_watch.py (D-069 rule, 23 tests). OPEN: the Pi 5 has no
  python3; the Architect is ruling (writePython3Bin / bash / the
  web-ui interpreter).
  M5 findings (worker-3, via CM, 2026-10-26): (i) NixOS installs
  neither the Hercules mapping (configs/mixxx/controllers) nor
  soundconfig.xml; deploy.sh is the old pre-NixOS .185 path. (ii) The
  repo soundconfig.xml is stale: "CamillaDSP 8ch Input", HP on ch 2;
  GM (F-130) expects HP on out_4/out_5, so HP would be silent (less
  audio, not a safety issue). (iii) Unverified whether the mapping's
  lodash/midi-components libs exist in the installed Mixxx. Proposed
  fix: tmpfiles in applications.nix, plus soundconfig captured on the
  Pi. worker-3 is cleared to DRAFT applications.nix (no build); the
  Architect and AE review. worker-3's Pi check list goes on the P-step
  list after US-172.
  UPDATE (CM, 2026-10-26): M5 draft pushed, head 1382490d
  (applications.nix: Hercules L+ links, no soundconfig yet).
  Architect rulings (via CM, 2026-10-26): python3 via writePython3Bin,
  with M3 using the web-ui interpreter as an interim for a P-step
  only; use the packaged Hercules mapping if Mixxx ships one;
  soundconfig via C+ plus a z rule (ela 0644), captured on the Pi
  before the next reboot; a REQUIRED drift-guard test (JACK, 48 kHz,
  Master 0-1, HP 4-5 vs GM routing).
  AE condition for the first DJ session (via CM, 2026-10-26): no
  direct Mixxx->USBStreamer link (a FAIL means remove it and raise a
  P1); Mixxx master/HP gains at defaults; Master stereo.
  Architect corrections (via CM, 2026-10-26): bash was rejected
  because it duplicates reviewed logic (not the test count). C+ must
  be confirmed to exist in the flake's systemd; fallback is L+ to a
  writable copy or an ExecStartPre copy. The Hercules USB-MIDI note
  comes from the CLAUDE.md TODOs.
  UPDATE (CM, 2026-10-26): head bf4bcfcb (applications.nix comments:
  C+ plus z 0644 ela users, Hercules conditions). The drift-guard test
  src/web-ui/tests/unit/test_mixxx_soundconfig.py (HP index from
  speakerChannels=4, production.nix) lands in the SAME commit as the
  captured soundconfig.xml, so the branch stays green with no xfail.
  Architect (M3, via CM, 2026-10-26): alsa-utils goes into the Pi 5
  systemPackages with M3 (package only, no listeners or services).
  Before M3, P-step 4 uses /proc/asound/cards plus
  /proc/asound/seq/clients instead of aconnect.
  P-STEP LIST (worker-3, 2026-10-26; after US-172; frozen copy
  /tmp/pm-backlog/us173-p-step-checklist-63cfa7f9.txt, sha1 63cfa7f9).
  Read-only (OBSERVE):
  - (1) mixxx --version.
  - (2) List the packaged controllers (hercules, lodash,
    midi-components). If the Hercules DJControl Mix Ultra mapping is
    packaged, drop our copy and the L+ links (Architect 2a); if ours
    is kept, it names the Mixxx version it was tested with.
  - (3) ls -la ~/.mixxx/ and ~/.mixxx/controllers/.
  - (4) Hercules over USB: lsusb, /proc/asound/cards, /dev/snd/midi*;
    MIDI clients via /proc/asound/seq/clients until alsa-utils lands
    with M3.
  - (5) Thermal watch for the whole session; before M3 only option
    (c), the interpreter taken from the web-ui unit's ExecStart, path
    logged.
  With Mixxx running (amps off, gate closed):
  - (6) AE safety condition, BEFORE ANY AUDIO: pw-link -l logged; NO
    direct link from any Mixxx port to a USBStreamer playback port.
    Any such link is a FAIL: remove it, raise a P1.
  - (7) Only convolver-out output_AUXn -> USBStreamer playback_AUXn
    links (AC7 link audit against the GM routing table, not against
    soundconfig).
  - (8) Mixxx ports out_0..out_5 present.
  - (9) Log Mixxx master and HP gain at defaults (AE); raising them
    needs an owner OK.
  - (10) Master stays stereo; no Mixxx mono/split options (GM does the
    sub mono sum, AE).
  - (11) Mixxx Preferences > Controllers: Hercules listed (logged),
    mapping selected; test play, crossfader, a deck.
  - (12) soundconfig capture (Architect 2c), BEFORE THE NEXT REBOOT:
    JACK API, Master ch 1-2, HP ch 5-6; copy ~/.mixxx/soundconfig.xml
    back and commit it, replacing the stale repo file, together with
    test_mixxx_soundconfig.py and the C+/z rules; the commit message
    names the D-040 drift.
  UPDATE (CM, worker-3, 2026-10-26): head facd7b8a (comments only,
  applications.nix), with a TODO. worker-3 verified from source (no
  nix) that tmpfiles C+ does NOT replace an existing file in systemd
  258.3, which nixpkgs 812b3986 pins: COPY_MERGE without COPY_REPLACE,
  and O_EXCL gives EEXIST, which is then ignored. The premise "C+
  replaces every boot" is false. This SUPERSEDES "soundconfig via C+
  plus a z rule" in the Architect rulings above, "C+ must be
  confirmed" in the Architect corrections, "C+ plus z 0644" at
  bf4bcfcb and "the C+/z rules" in P-step (12). Fallback (TODO): a
  separate user oneshot, mixxx-soundconfig, running `install -m 0644`
  on every boot. The Architect is ruling on the oneshot versus a labwc
  hook (labwc is in display.nix, the US-172 lane), including the
  Before= ordering. The drift-guard test still lands in the same
  commit as the captured soundconfig.xml.
  RULED (Architect, via CM, 2026-10-26; supersedes "The Architect is
  ruling" above): the fix is a separate user oneshot,
  systemd.user.services.mixxx-soundconfig in applications.nix, NOT a
  labwc hook. Type=oneshot, RemainAfterExit, wantedBy default.target;
  runs `install -D -m 0644 <store file> %h/.mixxx/soundconfig.xml`;
  Before=labwc.service (ordering only, display.nix untouched); no
  ExecReload. Settings changed in Mixxx persist only until the next
  boot, by design. worker-3 must also confirm in the 258.3 source that
  L+ replaces existing files. The drift-guard test still applies,
  against the store file. worker-3 is implementing it.
  P-step checklist REPLACED (worker-3, via CM, 2026-10-26): frozen
  copy /tmp/pm-backlog/us173-p-step-checklist-585801d2.txt (sha1
  585801d2) supersedes 63cfa7f9. Only item 4 changed: before M3,
  /proc/asound/cards plus /proc/asound/seq/clients; after M3
  (alsa-utils), aconnect -l; the functional check either way is that
  Mixxx's controller list shows the Hercules. Open to the Architect:
  add usbutils with M3, or check via sysfs `grep -H .
  /sys/bus/usb/devices/*/product` (the interim choice). PM notes (sent
  to worker-3 via CM): item 4's first line still lists lsusb, and item
  12 still says "the C+/z rules"; per the ruling, item 12 commits the
  soundconfig with test_mixxx_soundconfig.py and the mixxx-soundconfig
  oneshot.
  RULED (Architect, via CM, 2026-10-26; supersedes "Open to the
  Architect" above): usbutils goes into the Pi 5 systemPackages with
  M3, next to alsa-utils, package only. The P-step stays on sysfs
  regardless: `grep -H .
  /sys/bus/usb/devices/*/{product,idVendor,idProduct,speed}`,
  labelled.
  P-step checklist REPLACED again (worker-3, via CM, 2026-10-26):
  frozen copy /tmp/pm-backlog/us173-p-step-checklist-5f68cf7f.txt
  (sha1 5f68cf7f) supersedes 585801d2, and with it the PM notes above.
  Item 4: the labelled sysfs grep plus /proc/asound/cards and
  /dev/snd/midi*, and "lsusb -t as well" after M3. Item 12: the
  soundconfig commits with test_mixxx_soundconfig.py and the
  mixxx-soundconfig user oneshot in applications.nix; the message
  names the D-040 drift and speakerChannels (production.nix) as the
  shared source for the HP channels.
  Oneshot follow-up (Architect, via CM, 2026-10-26; supersedes
  "Before=labwc.service" in the RULED paragraph above): (a) the unit,
  the captured soundconfig.xml and the drift test go in ONE commit;
  lib.mkIf false is rejected, and the patch stays out of the worktree
  until the capture exists. (b) Drop Before=: the Pi 5 has no
  labwc.service, because greetd runs labwc directly. The ordering is
  guaranteed in practice, not by design, and the comment says so. The
  CM is checking with worker-2 whether US-172 adds a labwc or session
  unit. (c) Backlog line: when Mixxx gets a launcher or unit (gig
  auto-start, design principle 6), the soundconfig install moves into
  it (ExecStartPre or the launcher's first step).
  AE drift-test conditions (via CM, 2026-10-26): the test asserts
  values, not a byte match: API = JACK; no CamillaDSP device; Master
  offset 0 width 2; Headphones offset 4 width 2 (GM out_4/5). A
  capture that differs is a FAIL; the test is never edited to match
  the capture. The AE reviews the XML at PR time. Standing condition:
  before any audio, log pw-link -l and confirm there is no direct
  Mixxx->USBStreamer link.
  M3 cleared (CM, 2026-10-26) for worker-3 as code-only prep
  (alsa-utils, usbutils, writePython3Bin, flake8), no nix. The CM
  asked the Architect whether worker-4 (US-174c/d from 64d32f3e) and
  worker-5 (F-390 from #55 head 17144904) can start now under the
  parallel-work rule.
  ANSWERED (Architect, assigned by the CM, 2026-10-26): worker-4
  starts US-174d now (see US-174); US-174c waits for F-390/F-391;
  worker-5 starts F-390 then F-391 now (see F-390).
  UPDATE (CM, 2026-10-26): M3 code pushed,
  story/US-173-first-dj-session = 55dc75e3 (parent facd7b8a).
  flake.nix: pi5-thermal-watch via writePython3Bin (shebang dropped,
  because the writer prepends its own line; plus an assert).
  applications.nix: alsa-utils, usbutils and pi5-thermal-watch,
  packages only. NOT build-verified (disk hold). CM clearance item:
  build the pi5-thermal-watch derivation (writer flake8) or the
  mugge-pi5-deploy toplevel once there is room. The AE's ALSA-tools
  concerns are pre-prod one-liners (8)/(9) and do not block M3.
  M3 ALSA check (AE; PENDING, team-lead correction, 2026-10-26): a
  read-only step AFTER the M3 deploy, not yet run: no ALSA units
  (systemctl list-unit-files | grep -i alsa); a grep of the udev rules
  plus udevadm for alsactl (90-alsa-restore.rules); the USBStreamer
  amixer readback identical before and after the deploy. The AE closes
  it only when the readback matches. Done so far: only the CM's repo
  grep (nothing enables an ALSA restore service; no
  sound/hardware.alsa option); nix eval is blocked by the disk hold.
  UPDATE (AE, via CM, 2026-10-26): the AE ACCEPTED the M3 ALSA check.
  The read-only deploy check also runs `ls /etc/udev/rules.d` plus
  `udevadm cat 2>/dev/null | grep -i alsactl`. The alsa-utils package
  ships 90-alsa-restore.rules, which is inert without
  services.udev.packages. If the USBStreamer amixer readback is the
  same before and after the deploy, the item is CLOSED; no further AE
  conditions. Still PENDING until that readback runs.
  Capture-commit kit READY (worker-3, uncommitted, via CM,
  2026-10-26): unit patch /tmp/w3-us173/mixxx-soundconfig-unit.patch
  (sha1 878e4a7c), regenerated on 55dc75e3, dry-run clean; Before=
  dropped, with the "in practice, not by design" comment. The drift
  test is tightened per the AE (whole-file case-insensitive CamillaDSP
  check; a never-edit-to-match docstring): the stale file fails 2/5,
  the corrected sample passes 5/5. The capture commit = captured
  soundconfig.xml + patch + test, in one commit. Checklist 5f68cf7f
  unchanged. Open to the AE: should the drift test also pin the
  literal HP offset 4, besides == speakerChannels? worker-2's answer
  on a US-172 labwc/session unit is still pending. CI for #55/#57 is
  still in test-and-build.
  UPDATE (CM, AE, 2026-10-26): drift test sha1 0d5dc793 (untracked;
  capture commit only) pins HP == speakerChannels AND == "4" (AE:
  yes). Its comment says a speakerChannels change must not pass
  silently; update both with an AE review. The stale file fails HP and
  CamillaDSP; the sample passes 5/5. The open AE HP-offset question is
  RESOLVED.
  US-172 labwc/session unit (worker-2, via CM, 2026-10-26): NO. greetd
  runs `dbus-run-session labwc` (display.nix:55); the only new user
  unit is wayvnc under mkIf vnc. Dropping Before= stands; RESOLVED.
  UPDATE (CM, 2026-10-26): pushed at 1c2d4bef = worker-3's main merge
  548da0a6 plus the TW's safety.md aplay/amixer/alsactl rule (not a
  merge condition, see AE one-liner (9)).
  M2 ruling (Architect, via CM, 2026-10-26): the venue source set
  lives in configs/coeffs/markaudio-ultimax-200hz/, with a narrow
  gitignore negation. M2 item 3 (pipewire.nix) is DROPPED;
  pipewire.nix stays with US-174d. The Pi bridge is a CM CHANGE that
  replaces the 4 flat combined_*.wav files: sha check, rebuild, sha
  check. zero.wav lives at configs/coeffs/zero.wav, created by
  worker-3 only and consumed by US-174d. The US-174d migration notes
  cover removing the flat files. worker-4 owns the shared static check
  functions.
  OBSERVE-AE-sink-1 (CM, 2026-10-26): granted to worker-3 for the AE's
  default-sink reads. If the USBStreamer turns out to be the default
  sink, that is a potential P1 amps-on blocker (see amps-on row 18
  PROPOSED); it does not block now.
  RESULT (CM, 2026-10-26): OBSERVE-AE-sink-1 released. The default
  sink is the raw USBStreamer (priority.session 2000); the convolver
  has no priority.session. Sent to the AE. Not a block now (nothing
  connected); US-174d sets the convolver to 2100 (see US-174d) and
  amps-on row 18 FINAL covers the convolver-absent case. worker-3
  fast-forwarded to 1c2d4bef (confirmed) and has started the M2 fence
  work.
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
  B6i is HELD (CM, 2026-10-25) until 174d states the real gate. QE
  condition for citing US-174d in place of (B): "corrected
  MEASURED response, max positive deviation <=
  closed_loop.MAX_POSITIVE_DEVIATION_DB (3.0 dB), same 1/6-oct
  smoothing and bands as AC3, failure blocks deploy". The PM asked
  the AE (tolerance owner) to agree the wording; then B6j. The #57
  body cites that 174d line.
  AE 174d wording (agree with edits, 2026-10-25): the corrected
  MEASURED response at the listening position has a max positive
  deviation <= closed_loop.MEASURED_MAX_POSITIVE_DEVIATION_DB
  (initially 3.0 dB, the same value as the simulated
  MAX_POSITIVE_DEVIATION_DB), same 1/6-oct smoothing and bands as
  AC3. A re-measurement with SNR below 60 dB re peak is INVALID
  (repeat it), never a pass. A failure blocks the deploy: the new
  filters are not loaded, the previous ones stay, the run reports
  per channel. Any change to the measured constant needs AE
  review and never ships in the same PR as a correction-algorithm
  change. A separate constant, so real data can't silently loosen
  the simulated gate or the reverse; 174d revisits only the
  measured one. B6j (PM, MANIFEST 6b35c163, same B6e base at
  bcc353ed, whole-file replace of US-174.md; supersedes B6i, B6h
  and B6g, none applied) carries it. HELD (CM) for the QE's OK on
  the separate constant and worker-4's AC2 SHA. PM reading: the
  MEASURED constant is 174d scope, not #57.
  AE correction (2026-10-25): the "SNR below 60 dB re peak"
  sentence used an underived placeholder. It now reads: "A
  re-measurement whose SNR fails the measurement-time SNR check
  (backlog item; threshold AE-set there) is INVALID (repeat it),
  never a pass." The rest stands. B6k (PM, MANIFEST a81655c0)
  superseded B6j. QE (via CM, 2026-10-25): the separate MEASURED
  constant is OK; the stale AC2 line "Boundary tests: 2.9 dB
  passes, 3.1 dB fails." goes, unless worker-4's AC2 commit has
  2.9/3.1 tests, then it stays with "(through the same chain, QE
  T1)". B6l (PM, MANIFEST 78bac870, same B6e base at bcc353ed)
  deletes the line; worker-4's local AC2 commit e548a3d6 (seen
  read-only in the worktree) has no 2.9/3.1 tests. B6l-keep (PM,
  MANIFEST e504d5f6) is the alternative if the final AC2 SHA adds
  them. Both supersede B6k; HELD (CM) for worker-4's AC2 SHA.
  Update (CM, 2026-10-25): e548a3d6 is PUSHED with no 2.9/3.1
  tests and US-174.md untouched (sha256 32260961), so B6l
  (78bac870) is the batch; B6l-keep is VOID, never applied. The CM
  holds the B6l commit until worker-4's next SHA (an uncommitted
  test-file follow-up is in progress) and told worker-4 the AC2
  test conditions, including the required mutation (c) np.max ->
  np.mean and (d) the grep.
  B6m (PM, MANIFEST 6f29708d, base US-174.md sha256 32260961)
  supersedes B6l (never applied): the AE's REQUIRED AC2 boundary tests
  (target +3.0 dB passes, +3.01 dB fails, NaN FAILS;
  max_positive_deviation_db raises or returns +inf on non-finite
  input, or every caller uses <=), the AE's exact closed_loop.py
  comment text, and the teeth window bounds taken from
  MAX_POSITIVE_DEVIATION_DB and the verify_target_deviation default
  (no literals). The AE boundary line replaces the deleted 2.9/3.1
  line. worker-4 implements all of it plus QE O1-O3 in one follow-up
  commit; the CM holds B6m for that SHA.
  B6n (PM, MANIFEST bddbe5c8, base US-174.md sha256 32260961)
  supersedes B6m (never applied). Gate API (Architect APPROVED, fits
  option (A); via CM, 2026-10-25): two layers in closed_loop,
  deviation_within_limit(dev_db, *, limit=MAX_POSITIVE_DEVIATION_DB)
  as the scalar predicate and passes_residual_gate(response_db,
  target_db, *, limit=...), False on any non-finite input checked
  before smoothing; limit keyword-only, tests only; the venue and
  teeth asserts use passes_residual_gate, no second `<=`;
  max_positive_deviation_db stays honest (NaN in, NaN out). AE:
  non-finite input returns False and never raises; a non-finite or
  negative limit and an empty input also return False; a shape
  mismatch may raise ValueError. AC2 boundary line (QE wording,
  adjusted): "Boundary (AE): +3.00 dB passes, +3.01 dB fails,
  NaN/+inf/-inf and a NaN limit fail — via
  closed_loop.deviation_within_limit / passes_residual_gate (QE,
  Architect)". worker-4's 27d8ff11 (QE T1-T6 done; degraded +6.66 dB;
  mutation (c) reds 3 tests) is held for AE (a)/(c) (CM, 2026-10-25).
  B6n received and verified by the CM (2026-10-25); the CM applies it
  on top of worker-4's next #57 commit.
  #57 state (CM, 2026-10-25): the remote head is still e548a3d6, the
  earlier head pushed before 27d8ff11 (CI 40237500890 on it), NOT
  worker-4's awaited commit. worker-4's 46c53424 sits on top of
  27d8ff11: (a) the AE's closed_loop comment verbatim; (c)
  inspect.signature 8.0 (no literals). (b) was built as a metric
  RAISE, not the two-layer gate: push HELD, worker-4 is redoing it;
  the Architect and AE rule on whether the metric may also raise.
  Teeth numbers corrected: weak +6.66 dB at 68.1 Hz, real +0.94 dB,
  margin 3.66 dB. Then the CM verifies, pushes (27d8ff11 and 46c53424
  come along), applies B6n (bddbe5c8) as a separate commit, pushes,
  updates the body; QE/AE review.
  #57 (b) JOINT LINE (CM, 2026-10-25; PENDING one-line confirmations
  from the AE and the Architect; worker-4 gets instructions only after
  both confirm): max_positive_deviation_db MAY raise ValueError on
  non-finite input. passes_residual_gate and deviation_within_limit
  check finiteness first and return False, never raising. Tests: (i)
  gate(NaN/+inf/-inf) is False, no exception; (ii) the metric raises
  on NaN/+inf/-inf. Plus np.isfinite asserts at
  test_venue_closed_loop.py:438/:473/:492. #57 CI at e548a3d6 was
  green (that head will move).
  #57 (b) joint line: the Architect CONFIRMED it as quoted, including
  the isfinite asserts, and reported the AE's confirmation to them
  (CM, 2026-10-25). The CM waits for the AE's own line before
  instructing worker-4 (team-lead).
  UPDATE (CM, 2026-10-25; supersedes the wait above): the AE confirmed
  the joint line directly; both confirmed. worker-4 is instructed:
  keep the metric raise, add the two-layer API (the gates return False
  on non-finite input, never raise), and add the isfinite asserts at
  test_venue_closed_loop.py:438/:473/:492. Then the CM verifies,
  pushes, applies B6n (bddbe5c8) as a separate commit, pushes, updates
  the body; QE/AE review.
  UPDATE (CM, 2026-10-26): pushed worker-4's declared head 47b88da9
  (chain 27d8ff11 -> 46c53424 -> 47b88da9). It still has the metric
  NaN-in/NaN-out, not the joint line (metric raises, gates never
  raise, isfinite asserts); worker-4's tree has uncommitted edits in
  that direction, so a successor head is expected. B6n and the body
  update are held until then; B6n still applies to base 32260961 (CM
  checked). 47b88da9 lacks #56, so its F-363 failure comes from its
  base.
  UPDATE (CM, PM, 2026-10-26; supersedes "a successor head is
  expected" and "B6n and the body update are held" above): worker-4's
  successor head is 6a6264e9 ("metric raises on non-finite, gate never
  raises (final ruling)"), the joint line: closed_loop.py:128-129
  raises ValueError on NaN/+inf/-inf, the gates return False at
  :156-160, tests at :465-498 (PM checked). B6n (bddbe5c8) is
  SUPERSEDED, never applied (its gate-API paragraph still said NaN in,
  NaN out). B6o replaces it: /tmp/pm-b6o, MANIFEST sha1 3a638fb6,
  US-174.md sha256 6df31289, base 32260961 (= 6a6264e9's copy); B6n
  with the gate-API paragraph per the joint line, AE boundary line
  kept. The CM applies B6o as a separate commit. PR body (db299ac5)
  points sent via the CM to worker-4: the docs line names B6o; the "70
  tests" vs 95 count; the test results date from bcc353ed (QE/CM).
  Rule 13 for #57 opens at the head with B6o, so all review one head.
  UPDATE (CM, 2026-10-26): B6o applied as a separate commit; #57 head
  05d306bc3fc2d564be37299333557fdca8afa01f on 6a6264e9, remote
  matches; US-174.md blob 71ba839a = the PM file; base and MANIFEST
  checked; the two removed lines are supersessions (174d "After 174c."
  extended in place; the 8 -> 3 dB line kept as "was:"). worker-4 has
  the three body points; the CM opens Rule 13 at 05d306bc once the
  body arrives. #57 is 20 commits behind main (the cause of the F-363
  CI failure); the CM updates it from main after #59 and #60 merge,
  which moves the head: all 7 then re-check diff-only and CI re-runs.
  Rule 13 head for now 05d306bc; the final head follows the update.
  UPDATE (CM, 2026-10-26): the PR body is set (worker-4, sha256
  490ace7d). Rule 13 is OPEN at 05d306bc with all 7 (bundle
  /tmp/pr57-review-05d306bc, SUMS 3549c945). The branch is 23 behind
  main; the update from main after #59 merges stands.
  UPDATE (CM, QE, UX, 2026-10-26): 3/7 posted at 05d306bc: AE
  6405226733, SecSpec 6405226934, UX 6405227144, all conditional on
  green CI at the final head after the main update, with a diff-only
  re-check. QE APPROVE (accounting copy to the PM; full text with the
  CM, not yet posted): covers the gate code, tests, mutation table,
  teeth numbers and counts (1294 / 95 / 76). QE condition: the F-363
  red is explained by the missing #56; after the update from main, a
  QE diff-only re-check at the new head and CI T1-T3 green. QE open
  item (non-blocking): the CI ARM wall time for the file; over 300 s
  means an F-380 one-liner. SecSpec LOW: F-398. UX one-liners for
  US-174e (non-blocking), verbatim:
  - N1: "the venue_pipeline channel-map errors print the profile's
    0-based channel next to the 1-based venue keys. Label both
    ('profile channel 2 (= output ch 3)') before these messages reach
    the web UI."
  - N2: "in the 174e one-button flow, a failed gate says in plain
    words that nothing was deployed and the previous filters stay
    active, and names the failing channels using 1-based output
    numbers. The 'suggested gain delta (not applied)' value stays
    display-only unless there is an explicit, separately confirmed
    apply step."
  UPDATE (CM, 2026-10-26; supersedes the 3/7 and "QE ... not yet
  posted" above): #57 is 7/7 at 05d306bc: AE 6405226733, SecSpec
  6405226934, UX 6405227144, QE 6405234871, TW 6405235129, Architect
  6405235374, AD 6405246773 (/tmp/pr57-ad-verdict-05d306bc.md, sha256
  2d712b71). All seven lapse at the update from main (after #59
  merges); then diff-only re-checks by all 7 and green CI with F-363
  passing. Non-blocking: QE, fill in the ARM wall-time line from the
  first CI run (over 300 s = an F-380 one-liner to the PM); Architect,
  np.asarray on ragged input raises inside the gate, relevant only if
  external data reaches it (US-174d; pairs with AD L2); the TW keeps 3
  docs follow-ups in their own backlog. AD items (none block #57):
  - M1 = F-399 (fix before US-174c/d).
  - L1 (with F-383/F-384): correction.max_cut_db is not validated; a
    cap below |margin| lifts the design above -0.5 dB, and a NaN cap
    gives a NaN filter. Raise unless the cap is finite and >=
    |margin|.
  - L2 (with US-174d): passes_residual_gate and deviation_within_limit
    keep "never raises" only for numeric input; None or strings raise.
    Catch these or narrow the docstring before the gate becomes a
    deploy gate.
  - L3 (US-174d): sat correction above 500 Hz is bounded only by the
    18 dB cap, D-009 and min-phase. AE RULING (2026-10-26): YES, add
    an HF over-cut bound; a quality gate, not a safety gate; does not
    block #57. Why: above about 500 Hz a single-mic measurement is
    dominated by position-dependent combing; a cut that "fixes" a peak
    that exists only at the mic position leaves a real notch
    everywhere else, and the residual gate can't see it (it judges
    against the same measurement), so the bound applies to the
    correction filter itself. Cut-only: no hardware risk, only tonal
    harm. Sat channels only (subs are lowpassed). (a) Design: 500
    Hz-20 kHz, the correction part (filter minus the crossover-only
    target) cuts at most 6 dB, as a frequency-dependent max_cut: 18 dB
    below 500 Hz (unchanged), 6 dB from 500 Hz up, smooth 1/3-octave
    transition at 500 Hz; enforced in correction.py where max_cut_db
    is applied today (l.106). (b) Verify: fail-closed check on the
    generated WAV: on 1/3-octave smoothing 500 Hz-16 kHz, the filter
    magnitude is never more than 6.0 dB below the crossover-only
    reference at the same frequency; non-finite is a FAIL; it sits
    alongside MEASURED_MAX_POSITIVE_DEVIATION_DB in the US-174d gate
    set. (c) Test (US-174d): sim case with an injected narrow HF comb
    peak (+10 dB at 3 kHz, mic position only): design caps the cut at
    6 dB and verify passes; a hand-built filter with a 10 dB cut at 3
    kHz must FAIL verify. 6 dB is the AE's starting value; the AE
    re-judges it from the first real venue measurements, and any
    change is the AE's.
  - L4 (with venue config validation): build_channel_map accepts
    channel numbers outside 1..8; add a range check (same
    input-validation class as F-398; see UX N1).
  UPDATE (CM, 2026-10-26): #59 merged (main f01e6647); the CM is
  running update-branch on #57 now, so the 7/7 at 05d306bc lapses; the
  new head, the 7 diff-only re-checks and CI (F-363 passing) follow.
  UPDATE (CM, 2026-10-26): #57 at 6f4ae3d1 is 7/7 (AE 6411960153,
  SecSpec 6411960587, TW 6411961113, QE 6411961619, Arch 6411962178,
  UX 6411962685, AD 6411963158); QE conditions:
  test_sample_real_drivers_pass absent (deleted by #56),
  test_all_real_drivers_pass passing, 0 failed, ARM wall-time
  sign-off; AD: F-363 must PASS, not skip. Waits on CI 40294377693
  (not yet checked by the CM). #55 and #57 both touch room-correction,
  so the second to merge needs another update-branch, 7 diff-only
  re-checks and CI.
  UPDATE (CM, QE, 2026-10-26): #55 merged first; #57 at 599ea52a then
  failed CI 40299659873:
  TestAC7Identity::test_each_file_corrects_its_own_room, the right
  room's own filter beats the left filter by only 0.68 dB (1.15 vs
  1.83), under the 1.0 dB margin. QE: deterministic, a real regression
  from the #55 crossover-change interaction, not a flake. QE approval
  SUSPENDED (#57 at 6/7). Fix (worker-4, Architect, AE): a physical
  explanation with own/other numbers before and after #55; no
  loosening of the margin without an AE-backed reason, no xfail; the
  QE reviews any test change. Gate teeth fine: the real +0.94 dB sits
  2.06 dB under the 3.0 dB gate, so the QE's <1.0 dB rule is not
  triggered. ARM wall time 548 s: F-380, not a blocker.
  F-390 GATE (PO, 2026-10-25) applies to every US-174c/d session
  that loads speaker or crossover configs. See F-390. F-391 gates
  the same sessions.
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
  must estimate SNR and warn or refuse below 60 dB re peak. The 60
  dB figure is a PLACEHOLDER, not yet derived (AE, 2026-10-25); the
  AE sets the threshold here, and US-174d's real gate points to
  this check.
  SPLIT (AE, 2026-10-26) into two rows. (1) Correction-input
  measurement (174c): keeps the 60 dB placeholder; its estimator is
  still to be built. (2) US-174d re-measurement gate:
  MEASURED_GATE_SNR_MIN_DB = 30.0, the minimum over the gate band at
  1/6 octave, a placeholder until 174c's estimator exists. Reason: the
  gate only needs to resolve 3 dB, while the input measurement has to
  resolve cuts of up to 18 dB. The 174d AC wording "threshold AE-set
  there" now points to row (2).
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
  SPLIT (Architect parallel-start ruling, assigned by the CM,
  2026-10-26): US-174c and US-174d proceed separately.
  US-174d (deploy refuses SIMULATED; deferred dir swap; a measured
  gate MEASURED_MAX_POSITIVE_DEVIATION_DB separate from the simulated
  constant; SNR-invalid = repeat; a failed gate keeps the previous
  filters; the AE HF-cut bound) is worker-4's from now. Branch
  story/US-174d-deploy-gate, cut from 64d32f3e (worktree
  .claude/worktrees/story-US-174d-deploy-gate). Fence: deploy.py,
  closed_loop.py, venue_pipeline.py, runner.py and their tests; if
  crossover.py or generate_profile_filters.py are needed, stop and get
  an Architect ruling. The PR opens only after #57 and F-399 merge.
  Fence WIDENED (CM, 2026-10-26) for worker-4's L3 HF-cut bound:
  room_correction/correction.py (frequency-dependent cap at the
  max_cut_db site), room_correction/verify.py (a new fail-closed HF
  check) and their tests. Overlap: neither file is in #55 or named in
  F-391; #57 changes both, and the branch builds on it.
  generate_profile_filters is call-only. worker-4 sent a design
  consult to the Architect, AE and AD.
  Architect Q2 RULED option (b) (via CM, 2026-10-26): an atomic
  symlink coeffs/current -> sets/<id>. The CM granted worker-4:
  30-filter-chain-convolver.conf (paths become coeffs/current/<name>);
  pw_config_generator.py plus its test (a shared expected-files
  constant); pipewire.nix tmpfiles (sets/, sets/dirac seeds, and a
  plain `L` for current, NOT `L+`, which would reset it to dirac on
  every boot). Overlap: no active lane touches these; only the stale,
  inactive PR #40 (sprint/session-16) touches pipewire.nix. Deploying
  the new layout is a separate DEPLOY later; the AE is in on that
  grant because it changes which coeff files PW reads. This supersedes
  the earlier "NOT cleared ... pending Architect Q2" (convolver conf,
  pipewire.nix, pw_config_generator).
  Design consult result (AD, 2026-10-26): joint result
  /tmp/us174d-joint-result-v3.md (sha256 273a2b85; frozen copy
  /tmp/pm-backlog/us174d-joint-result-v3-273a2b85.md); the AE accepted
  it with 2 amendments, which worker-4 builds:
  - In scope (AE): the static check "no Dirac on ch 1-4" has a
    passthrough exception, only for a declared passthrough venue AND
    no own speakers/amps on ch 1-4. AD: software can't verify "no own
    speakers", so the exception comes only from the venue YAML
    declaring passthrough plus an explicit per-deploy operator
    confirmation, never a default.
  - In scope (AE): a fallback to seed-dirac (dangling `current`) is
    loud: logged, and a GM/web-ui status flag "seed-dirac: no driver
    protection" is set, which a test asserts.
  - PRE-PROD (AE): make the seed-dirac fallback fail-closed instead of
    only loud.
  - PRE-PROD (Architect): after a crash mid-trial, the next boot loads
    the untested trial set silently. The GM/web-ui gate unlatch/open
    must refuse while coeffs/.trial-pending exists.
  - Backlog (Architect/AE): the F-346 fix, a verified full-channel
    in-place reload, so the gate no longer needs a PW restart (amps
    off) for each trial or rollback. See the F-346 defect record.
  - A5b, a group-writable coeffs tree (2775 root pi4audio): listed as
    open by the AD, but RULED by the SecSpec (about 09:23Z, to the
    Architect; via team-lead): acceptable for the home lab, no sudo or
    helper for now. Conditions for the US-174d ACs: check whether the
    web UI runs as ela, and add no separate service user if it does;
    filters live under /var/lib, not /etc; format and D-031
    driver-protection validation before any swap; plain names only,
    with current pointing inside the sets dir; atomic switch via a
    temp link plus rename. Pre-amps-on/gig backlog (SecSpec): a single
    validated writer (a root helper, or no web-UI deploy until auth
    exists), with ela's group write removed at that point. worker-4
    runs a read-only check of how web-ui deploy_filters writes to the
    root-owned coeffs dir today and reports the finding to the PM and
    the SecSpec.
  SUPERSEDED (2026-10-26) in the list above: the seed-dirac fallback
  row, the seed-dirac fail-closed row, the coeffs/.trial-pending row
  and the A5b "filters live under /var/lib, not /etc" condition.
  Current texts follow. The crash design is being re-settled by the
  Architect and the AD (CM, 2026-10-26); the Architect's final answer
  governs.
  - In scope (AD FINAL): a dangling `current` with no verified
    `committed` stops loud with audio disabled; status flag "no
    verified set: audio disabled", test-asserted. No auto-fallback; it
    repoints to `committed` only if `committed` verifies.
  - In scope (AD FINAL): `current` resolving to seed-dirac (fresh
    install, or the tmpfiles L recreating it) means audio works with
    no driver protection. Flag "seed-dirac: no driver protection"
    whenever this happens on a venue that is not a declared
    passthrough; tests for both venue cases.
  - PRE-PROD (AD, kept, reworded): "gate refuses to open on seed-dirac
    unless the venue is a declared passthrough (declared in the venue
    YAML plus operator confirmation)". Same item (Architect one-liner
    2, owner AE): "the 'seed-dirac: no driver protection' startup
    warning (keyed on current resolving to seed-dirac with a
    non-passthrough venue) becomes fail closed."
  - PRE-PROD (Architect one-liner 1, owner Architect/AE; = the AD's
    crash-mid-trial row, now keyed on `current != committed`, since
    the .trial-pending marker was dropped for a `committed` link):
    "after a crash mid-trial, the next boot loads the untested trial
    set. The GM/web-ui gate unlatch must refuse while
    readlink(coeffs/current) != readlink(coeffs/committed)."
  - PRE-PROD gate condition (AE A1, via the Architect): before the
    first amps-on venue deploy, either F-346 is done (all 8 channels
    loaded and proven, USBStreamer not suspended across the reload,
    row-16 readback) or the gate enforces an amps-off confirmation per
    PW restart. Links to the F-346 row above.
  - With F-348 (Architect one-liner 3, owner Architect): "move the
    generated filter-chain conf onto the venue's explicit
    channel->file map, so the deploy no longer materializes conf names
    for unused channels."
  - Coeffs dir (team-lead correction, 2026-10-26): the filters STAY at
    /etc/pi4audio/coeffs for now. The Architect deviated from the
    SecSpec's /var/lib condition; the SecSpec accepted that (about
    09:25:56Z), with a check that NixOS doesn't manage that path. The
    other four A5b conditions stand as US-174d ACs. Low backlog (owner
    Architect; SecSpec, verbatim): "Move the coeffs dir from
    /etc/pi4audio/coeffs to /var/lib/pi4audio/coeffs (mutable state
    out of /etc). This touches Rule 10, the F-399 guard literal and
    the docs."
  - Spare channel (AE ruling, via team-lead, 2026-10-26): option (2).
    Ch 4 of the markaudio-ultimax-200hz venue (the muted spare) gets a
    committed all-zero filter file, zero.wav, not Dirac. US-174d
    approval conditions (AE, with worker-4): (1) the file and its
    format; (2) the venue declaration; (3) the zero-sample verify; (4)
    the spare's gain stays 0, plus the safety.md text, now amps-on row
    17 sentence 2; (5) the tests.
  SETTLED (Architect superseding note, relayed to worker-4 by the CM;
  the AD concurs; 2026-10-26; replaces "being re-settled" above): a
  `committed` link, no marker file. Addendum A: a ROLLBACK-FAILED
  fail-closed path, with `current` repointed to a dangling
  sets/.rollback-failed. Addendum B: sub2 is negated from the decoded
  sub1 array. Addendum 2 (Architect: a design gap, IN SCOPE, not a
  backlog edge): the filter-chain conf sets `flags = [ nofail ]`, with
  a real-PW dangling-current test and an `L`-not-`L+` static test.
  Consequence: amps-on row 18 PROPOSED (filter-chain absent = no
  audio). Open AE question (CM): the D-031 cut threshold at
  mandatory_hpf_hz.
  Addenda 3 and 4 (Architect, relayed to worker-4 by the CM,
  2026-10-26): `nofail` plus static tests in 174d; the real-PW proof
  moves to pre-amps-on (row 18) unless CI can do it for free;
  convolver priority.session 2100 with a relation test against the
  USBStreamer's 2000; the verify step checks default.audio.sink =
  pi4audio-convolver; the PR text names the ungated fallback, with the
  WP stream-target hook as amps-on row 18 (now FINAL). The hook itself
  is NOT in 174d.
  US-174c (measurement on the Pi, web-ui measurement/session.py)
  starts only after F-390/F-391 and builds on them, because it is the
  same file (L-046). Its Pi run is also gated by US-173 H, F-341 AC3,
  D-070 and the amps-on list.
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
  UPDATE (AE, 2026-10-26; F-395 AC (c)): "verified in AC17-B step (c)"
  above is NOT VERIFIABLE under F-395 (fc/fc-out node state not
  logged; not a FAIL; AE ruling on the QE's AC (c) list, 2026-10-26);
  re-run pending (F-395 AC (c)). The procedure stays as the interim
  workaround. New AC2 addition (AE, verbatim): "the gains read set
  includes the fc and fc-out node state immediately before and after
  the read (D-070 row 14)." The re-run covers the F-373 recovery (PW
  restart plus bridge restart) if it differs from the plain PW
  restart.
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
- **Coefficient sets: single validated writer** (SecSpec, MEDIUM,
  PRE-PROD gig-blocker class next to F-037 and F-372; from the US-174d
  A5b ruling, 2026-10-26), verbatim: "Coefficient sets: single
  validated writer. Before amps-on or gig use, a root-owned systemd
  helper (path unit or localhost RPC) becomes the only writer to the
  coeffs dir. It runs the static checks (verify_format, mandatory HPF
  per D-031, name regex, links resolving inside coeffs/sets/) before
  any repoint of `current`. Alternatively, the web-ui deploy_filters
  path stays disabled until F-037 auth lands. When the helper lands,
  the pi4audio group write on /etc/pi4audio/coeffs (US-174d, home-lab
  interim) is removed. Severity: medium (security-specialist).
  Gig-blocker class, next to F-037."
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
  UPDATE (QE, via CM, 2026-10-25; extends F-387, no new ID): retitled
  "web-ui unit tests: mock GM teardown hygiene (ERROR / unraisable
  warnings)". Same family (the mock GM server's lifecycle at
  event-loop shutdown). Second symptom: in test_collectors.py, test
  TestFilterChainPushEventDesync::
  test_multiple_events_before_response: an unclosed socket
  ResourceWarning plus PytestUnraisableExceptionWarning in
  _SelectorTransport.__del__, ~1 in 3 runs at #55 d0a317c3 (worker-5
  log /tmp/worker5-f374/webui-warn-run2.log). Stays Low. Closes QE N2
  on #55.
- **F-388** Xmax definition in the excursion-mask derivation (P2;
  AE-owned; 2026-10-25; ID at the AE's request): the
  D-031/excursion-mask derivation must record which Xmax definition
  each driver record carries ("mathematical"/overhang vs measured
  linear, e.g. a 10% THD or 70% BL point) and derate a
  "mathematical" Xmax instead of using it as a linear limit.
  UPDATE (QE FYI, 2026-10-25; supersedes "derate" in this paragraph):
  the record merged via #58 says the opposite: no percentage derate
  factors; a "mathematical" Xmax is re-derived as plain overhang, or
  rejected (AE M2 below).
  Trigger: F-363 corrects PRV 10MR2000-NDY xmax 5.0 -> 7.15 mm to
  the sheet's printed "mathematical" value. Precondition for F-385
  option (i'); related to the fail-closed T/S follow-up under
  F-363. Proposed ACs (AD, #56 verdict, 2026-10-25; AE to accept):
  M1 no code enforces ts_consistency marks today and
  speaker_sim.load_driver loads marked records; any safety
  calculation that reads driver records refuses marked records at
  load. M2 xmax_mm gets a definition attribute; a
  "mathematical"/overhang-plus Xmax is derated or rejected (PRV
  5.0 -> 7.15 is +3.3 dB less conservative; other scraped records
  likely carry the same unknown definition). No defects/F-388.md
  record on main yet (TW); add one with the next defects docs PR.
  ACs from the #56 verdicts (AD, QE, Architect, via CM and
  team-lead, 2026-10-25; supersede the proposed M1/M2 above; AE
  acceptance asked):
  - AC-a (AD M1 + QE): no code reads ts_consistency today. Before
    any excursion or power derivation reads driver records, the
    loader refuses marked records, or the caller opts in
    explicitly.
  - AC-b (QE + Architect; condition of the QE's no-re-push and the
    Architect's agreement on #56): correct the "keeps it out of the
    safety math" comment in test_driver_validation.py. The #56 body
    cites F-388 for this.
  - AC-c (QE; condition of the QE's no-re-push on #56): a paired
    loader test: a record marked "unverifiable" is refused AND a
    normal record is still accepted in the same test (the positive
    control proves the loader doesn't refuse everything).
  - AC-d (AD M2): xmax_mm gets a definition attribute; a
    "mathematical"/overhang-plus Xmax is derated or rejected; every
    scraped xmax_mm counts as unknown-definition until its source
    is classified.
  - AC-e (QE N1): a test once a consumer of xmax exists.
  - QE backlog item (#56 merge, via CM, 2026-10-25), covered by
    M1/AC-a, no new ID: "any future consumer of driver-record T/S
    values must exclude ts_consistency: unverifiable records"; the #56
    body points it at F-388.
  AE ACCEPT with edits (via CM, 2026-10-25; replaces the AC-a and AC-d
  wording; AC-b, AC-c and AC-e stay; "derate a mathematical Xmax"
  above is superseded by "re-derive, no percentage derate"):
  - M1: "Every safety computation that reads a driver record
    (excursion mask, thermal, protection, D-031 derivation) refuses at
    load any record that has a ts_consistency mark, or has a null in a
    field the computation needs. The error names the record, the mark
    or the field, and the computation. It fails closed: no fallback
    values, no skipping the channel. Simulation (speaker_sim) may
    still load marked records, but it logs the mark, and its output
    must never feed a safety gate." The F-363 follow-up "Fail closed
    (AE condition)" is merged into M1 (one record). Precondition for
    F-385 (i') CHN-50P excursion mask.
  - M2: "Driver records get xmax_definition with values linear
    (manufacturer measured linear limit, e.g. Klippel), overhang
    (plain (winding depth - gap depth)/2), mathematical (overhang plus
    terms such as + gap depth/4), or unknown. Safety computations use
    linear and overhang as stored. A mathematical Xmax is re-derived
    as the plain overhang from the datasheet's winding and gap depths,
    and both figures are recorded; if the depths aren't printed, it is
    rejected. An unknown Xmax is rejected. No percentage derate
    factors. Only the drivers referenced by speaker identities need a
    classification (AE), starting with markaudio-chn-50p (xmax 3.5)
    before the F-385 mask. The 2345 scraped records may stay unknown."
    PRV example: mathematical 7.15 mm re-derives to (18.8 - 9.0)/2 =
    4.9 mm.
  - AC-f (AE option (a), 2026-10-25, verbatim; from UX N1 on #58;
    supersedes the CM's shorter "M1 addendum" proposal): "AC (UX,
    #58): the M1 refusal (marked record, or a null field the safety
    math needs) also fires (i) when a speaker identity or profile that
    references such a record is saved, and (ii) when a measurement
    session starts, before any gain calibration or stimulus. The M1
    refusal at compute time stays as the backstop and is never
    removed. Tests: one per entry point, plus one showing the
    compute-time refusal still fires if the earlier checks are
    bypassed." Why (AE): a session that can't produce valid safety
    limits should never get as far as playing a stimulus. UX: same
    message at every entry point. F-388.md (#58) gets it in the TW's
    #58 v2 if the TW takes it there, else in the next defects docs PR.
    ON MAIN (#58 merged dfb81cd7, 2026-10-25; supersedes "gets it in
    the TW's #58 v2 ... else in the next defects docs PR" and the
    entry's "No defects/F-388.md record on main yet" line):
    docs/project/defects/F-388.md is on main with AC-f as AC 6.
    Dependency (AD N1 on #58; team-lead): AC-f(ii), the refusal at
    session start, depends on F-390: the session reads the repo
    configs/speakers while the editor saves to /etc/pi4audio/speakers,
    so on the Pi the session-start check could be skipped. F-390 is
    scheduled first. Architect: AC-f uses one shared validator
    (F-391); no second implementation per entry point.
- **F-389** Pi 5 tryboot with KMS+BT overlays via overlay_prefix:
  no network, needed an owner power cycle (Architect, no QE
  objection; via CM, 2026-10-25). US-172 run 2: run 1 +
  overlay_prefix=o/ + disable_splash=1 turned a 36 s return into no
  return. Details, recovery and the run-3 design under US-172.
  BLOCKS US-172 (Architect, 2026-10-25). Linked: the watchdog
  reliability TODO (CLAUDE.md open questions; BCM2835 watchdog
  failed Tests 3/5 on the Pi 4) and the RuntimeWatchdogSec check
  under US-163 AC5 below.
- **F-390** Speaker-config path split (P1; PO, 2026-10-25; from #55
  backlog (a), AD N4). The editor writes /etc/pi4audio/speakers;
  the measurement session and CP-5 read the repo configs/speakers
  (the Nix store on the Pi), so an editor fix never reaches the
  session that measures with it. Driver-safety risk (D-031), not a
  convenience issue (PO). GATE before every US-173 session and
  every US-174c/d session that loads speaker or crossover configs
  (measurement, CP-5); gate wording with the AE. Final gate text
  (AE, 2026-10-25): "F-390 GATE: no US-173 session and no
  US-174c/d session that loads speaker or crossover configs
  (measurement, CP-5 generation or deploy) starts until F-390
  AC1-AC4 are met, or the AE-accepted fallback below is in place."
  AC1: one source of truth on the Pi; the editor, the measurement
  session and CP-5 read and write the same path. AC2: each session
  logs the path and hash of the speaker config it loaded; the lab
  note records it. AC3: a test that an editor change reaches the
  session that measures with it. Fallback, only if the fix is late
  and would block a session: AC2 alone plus a manual hash
  comparison against the editor file before the start; the AE
  decides whether that is enough.
  Route (Architect ruling, 2026-10-25, cc AE and CM): canonical
  /etc/pi4audio/speakers (env PI4AUDIO_SPEAKERS_DIR). Code facts:
  speaker_routes.py:40-59 `_speakers_dir()` (env, /etc, repo,
  ~/pi4-audio-workstation); filter_routes.py:40-51 a duplicate;
  measurement/session.py:~1014 hardcodes
  <project_root>/configs/speakers (the split); #55's
  `_profile_dirs()` inherits it; config_generator.py:31
  IDENTITIES_DIR default (callers must pass dirs); no tmpfiles rule
  for /etc/pi4audio/speakers (only coeffs, pipewire.nix:95-101).
  - R1: the repo/store configs/speakers is read-only seed data,
    never a runtime read path on the Pi.
  - R2: one shared resolver speakers_dir() -> (profiles_dir,
    identities_dir, source) for speaker_routes, filter_routes,
    session start, CP-5, the F-374 pre-check and every
    config_generator/generate_profile_filters call (explicit dirs);
    duplicates deleted. Precedence: env, else /etc if present, else
    the repo dir (dev/test only: local-demo, CI).
  - R3: no silent fallback on the Pi. The Nix module sets the env
    for the web-ui; env set and dir missing or unreadable -> raise;
    the editor shows a clear error, the session refuses to start
    and names the path.
  - R4: tmpfiles `d` for speakers/{profiles,identities}, owned and
    writable by the web-ui user; per-file `C` seeds from the repo.
    Operator edits are never overwritten; changed repo versions of
    existing files do not propagate (deliberate; document it).
    Propagation is a separate AE/QE decision (Architect: no).
  - R5 (AC2): at start and CP-5, log source/dir and the sha256 of
    the profile and each identity file, also in the session record;
    a hash change start -> CP-5 is a WARNING; the session keeps its
    start-time copy.
  - R6 (AC3): (a) editor-save and session-load resolve to the same
    dir (tmp env); (b) integration: save via the editor API, start a
    session (D-057 mock boundary), hash match; (c) env set, dir
    absent -> refuses to start; (d) grep guard: no web-ui module
    builds configs/speakers paths outside the resolver.
  - R7: #55 is NOT widened; F-390 branches after #55 merges (or
    rebases) and replaces `_profile_dirs()`.
  CM assigns the lane; the Architect reviews design and diff before
  the PR; the AE confirms the gate and AC2 wording. Lane: the CM
  assigns it after #55 merges (CM, 2026-10-25). The Architect's
  ruling text is at /tmp/f390-architect-ruling.md (CM).
  AE additions (2026-10-25):
  - AC2 EXTENDED: the logged hash covers the profile AND every
    identity file it references (mandatory_hpf_hz and max_boost_db
    live there), not the profile alone.
  - AC4 (NEW): "A session whose profile, or any identity the
    profile references, cannot be loaded fails at session start,
    before gain calibration or any sweep. It is never skipped with
    a warning." (SecSpec's #55 point: today a missing profile skips
    the pre-check, the sweeps run, and it fails only at CP-5.)
  - Fallback: enough only under ALL of: (a) the comparison covers
    the profile and every referenced identity, the session-loaded
    repo copy vs the editor's /etc/pi4audio/speakers copy,
    byte-identical by sha256; any mismatch or a missing file on
    either side is a STOP, no "proceed and note"; (b) it is done in
    the CM session record after the last editor edit and before the
    start, with no editor saves during the session, and repeated
    before any CP-5 deploy; (c) the session log (AC2) shows the same
    hashes; (d) the sha256 of the coeffs deployed in the convolver
    at session start is recorded, and the previous deploy record
    shows they were generated from configs with the same identity
    hashes (see F-391); (e) valid only for the named US-173 and
    US-174c/d sessions; F-390 stays P1 open, and the fallback never
    covers a gig.
  Linked (AD N1 on #58, 2026-10-25): F-388 AC-f(ii), the driver-record
  refusal at session start, depends on F-390; F-390 goes first.
  ASSIGNED (CM, Architect parallel-start ruling, 2026-10-26): the
  F-390 then F-391 lane is worker-5's. Branch
  fix/F-390-speaker-resolver, cut from #55's head 17144904 (worktree
  .claude/worktrees/fix-F-390-speaker-resolver). CM reading of R7: #55
  is not widened, so branching from #55's head is within "after #55
  merges (or rebases)". Conditions: no edits to #55's own changes
  (anything wrong there is a finding against #55); merge #55's new
  head if it moves; the PR only after #55 merges; the Architect
  reviews design and diff before the PR, and the AE confirms the
  gate/AC2 wording. Authoritative F-391 set: R1-R7, then the FINAL
  ADDENDUM 7e467465, then PART B 60095f5d, then PART C b91ac082, plus
  the AE review; A1/A2 are superseded. US-174c builds on this lane
  (see US-174).
  F-a (worker-5; AE ruling, via CM, 2026-10-26):
  speaker_routes.py:957-963 passes project_root=base.parents[1] to
  thermal_ceiling.load_channel_ceilings. On the /etc layout that is
  /etc, so it raises, the exception is caught as a warning, and the
  thermal limiter is NOT configured on profile activation. A
  regression caused by F-390, so it is fixed IN F-390; the AE won't
  approve the F-390 PR otherwise. The CM granted worker-5
  thermal_ceiling.py, the speaker_routes call site and the tests. AE
  conditions: (1) an /etc-layout activation test asserts the limiter
  is configured with the expected per-channel ceilings; (2) a
  repo-layout backward-compatibility test; (3) all
  load_channel_ceilings/load_speaker_identity callers are grepped and
  fixed in the same change. Fail-closed activation is AE pre-prod
  one-liner (10).
  Open to the Architect (F-390, via CM, 2026-10-26): D2 (repo fallback
  only when PI_AUDIO_MOCK != "0"); D3 (a main.py 503 handler vs
  per-handler); D4 (an edit to #55's _check_profile_crossover, held);
  D6 (web-ui.nix env plus tmpfiles C seeding, unbuilt); F-b
  (deploy.sh:565-575 rsync --delete overwrites operator edits to
  /etc/pi4audio/speakers; backlog?).
  RULED (Architect, via CM, 2026-10-26; supersedes "Open to the
  Architect" above): D1 approved. D2: repo fallback only if
  PI_AUDIO_MOCK != "0". D3: one main.py handler for SpeakersDirError
  only, 503, logged once per request; the session path maps it to
  ERROR. D4: a stacked follow-up commit in F-390 naming the superseded
  #55 lines. D5 approved: a mid-session edit is a WARNING plus
  cp5_check. D6 approved: C seeding never overwrites operator edits,
  with the trade-off in a web-ui.nix comment; unbuilt. F-a is fixed in
  F-390. R6 (a)-(d) approved; the grep guard also catches
  /etc/pi4audio/speakers and ~/pi4-audio-workstation. CM grants:
  main.py, web-ui.nix, the D4 edit and thermal_ceiling.py. Fence:
  speakers_config.py (new), session.py, speaker_routes.py,
  filter_routes.py, main.py, web-ui.nix,
  room-correction/thermal_ceiling.py and their tests.
  Record line (Architect, verbatim): "#55 merges with the fail-open
  FileNotFoundError warning-skip in _check_profile_crossover; F-390
  closes it. Not a #55 blocker under the owner priority (nothing
  connected)."
  F-b one-liner (Architect, verbatim): "Check whether
  scripts/deploy/deploy.sh is still used for the NixOS Pi 5. If not,
  delete its rsync --delete block (deploy.sh:565-575) or the script
  (Raspbian legacy). If it is, it must not clobber operator edits in
  /etc/pi4audio/speakers (F-390 R4)."
  Status (CM, 2026-10-26): worker-5 is permission-blocked on running
  tests (escalated to the owner).
  F-c (worker-5, via CM, 2026-10-26; outside the F-390 fence): see the
  P3 entry "/protection status reads the wrong marker". AE: NOT under
  the AE's F-390 condition.
- **F-391** Measurement sweep ignores mandatory_hpf_hz (P1; AE,
  2026-10-25). Gates the same sessions as F-390. /measurement/start
  accepts ChannelConfig.mandatory_hpf_hz (session.py:193), but
  session.py never applies it; sweeps run 20 Hz-20 kHz at
  sweep_level_dbfs (session.py:778, AE). The only D-031 protection
  during a sweep is the combined FIR deployed in the convolver at
  that moment; if it came from a stale identity, or is a dirac or
  passthrough, the sats get full-level content down to 20 Hz. Fix
  options (the Architect chooses the route; PM asked): apply the
  identity's HPF to the sweep or start the sweep at the HPF, or
  verify before the first sweep that the deployed coeffs carry each
  channel's D-031 HPF. Either way the dead field is removed or
  wired. Interim: F-390 fallback condition (d). Lane: CM (likely
  next to F-390; both touch session.py).
  - Architect route ruling (2026-10-25, cc AE, CM; supersedes "the
    Architect chooses the route"): route (A) on EVERY stimulus the
    session generates, the HPF taken server-side from the loaded
    identity; (B) is not a gate, a hash record only (R5). Why not (B):
    the first venue measurement runs on dirac/placeholder coeffs, so
    (B) would block it or need an HPF placeholder FIR (safety.md
    option (a), another story); a spectral check of a WAV is new
    error-prone safety-path code; (A) is the only place the session
    controls end to end.
  - Code facts: the session.py:193 field is never read;
    routes.py:44/144 copy it from the CLIENT request. Measurement
    sweeps session.py:733-735 call generate_log_sweep(f_start=20.0,
    f_end=20000.0) at sweep_level_dbfs (session.py:202, default -20);
    verification sweeps session.py:1353-1355 hardcode 20.0 too (2nd
    instance); gain cal gain_calibration.py:93/156-190 plays pink
    noise 100 Hz-10 kHz, 4th-order Butterworth (3rd instance;
    identities with an HPF above 100 Hz: bose-jewel-double-cube 200,
    hoqs-c3d-hf 800; hoqs-c3d-mid 100 and markaudio-chn-50p 80 are
    close). sweep.py:59-62 50 ms Hann fades leave a little energy
    below f_start. safety.md:140-175: D-031 requires subsonic
    protection "in the audio pipeline"; dirac placeholders give none.
  - R1 source: per channel from the identity via the F-390 resolver
    (profile -> speaker_key -> identity.mandatory_hpf_hz). Remove
    mandatory_hpf_hz from the /measurement/start request model
    (routes.py:44/144) and the ChannelConfig client input; a client
    that sends it gets 422; a client can never lower the protection.
  - R2 fail closed (= F-390 AC4): no speaker_key, an unloadable
    identity or a missing mandatory_hpf_hz fails at session start,
    before gain cal. The only accepted null is an identity with the
    documented D-031 exception (dayton-ultimax-umii18-22-sealed-120l),
    machine-readable (e.g. d031_exception: "<reason>"; the AE defines
    the field); without it a null refuses. An excepted null has a 20
    Hz floor.
  - R3 measurement and verification sweeps: f_start = max(20.0,
    hpf_hz) AND the stimulus high-passed at hpf_hz before scaling
    (covers the fade leakage). The AE picks the slope (Architect
    default 48 dB/oct, as the D-031 FIR generators; at least 24).
    Deconvolution MUST use the exact played (filtered) signal as
    reference; results below hpf_hz are marked regularized/invalid.
    One shared stimulus builder for both call sites.
  - R4 gain cal: calibrate_channel takes hpf_hz, f_low =
    max(PINK_NOISE_F_LOW, hpf_hz) (gain_calibration.py:93/156);
    measure_nearfield gets the same (covers the CLI).
  - R5 (B) as a record: at session start, log and store the sha256 of
    each deployed coeff WAV in /etc/pi4audio/coeffs next to the F-390
    AC2 hashes (F-390 fallback (d) becomes permanent evidence). A
    deployed-coeff HPF verifier is a separate backlog item, if the AE
    wants it (below).
  - R6 tests: (a) per channel, stimulus energy below hpf_hz under an
    AE-set bound (e.g. <= -40 dB re passband), sweeps at both call
    sites and the gain-cal noise, at hpf 42/80/200/800; (b) a request
    with mandatory_hpf_hz gets 422; (c) a missing identity or HPF
    refuses before gain cal, and an excepted null runs at 20 Hz; (d)
    the deconvolution reference equals the played signal; (e) the
    mutation f_start -> 20.0 makes (a) fail.
  - R7 interim until F-391 merges: F-390 fallback (d) AND no session
    on an identity with an HPF above 100 Hz (gain cal already violates
    D-031 there). Supersedes "Interim: F-390 fallback condition (d)"
    above.
  - F-390 review (Architect): AC4 and the extended AC2 accepted (R5
    covers both; AC4 also covers F-391 R2). One shared resolver: if
    F-390 and F-391 share a lane, F-390 lands first. Lane: CM.
  - Open for the AE: the slope, the R6(a) bound, the d031_exception
    field definition, and whether a deployed-coeff HPF verifier is
    wanted.
  - Ruling texts: Architect /tmp/f391-architect-ruling.md (CM saved,
    2026-10-25); AE final /tmp/ae-f391-ruling.md, sha256
    e6e8a9a3...cdc1 (PM frozen copy
    /tmp/pm-backlog/ae-f391-ruling-e6e8a9a3.md), which includes the
    Architect A2 addendum. The AE text closes the open points above;
    the AE wants the verifier (P2, below). Lane (CM, 2026-10-25):
    worker-5, F-390 then F-391, after #55 merges.
  - AE ruling (exact text in the file; summary): route (A) accepted;
    gain-cal f_low = max(100, hpf); interim = Architect R7 plus AE
    condition (d).
  - AE 1 SLOPE: the stimulus low edge is at least 48 dB/oct (24 is not
    enough), applied offline to the stimulus array (D-055 bans IIR on
    the signal chain, not offline stimulus shaping; frequency-domain
    shaping is OK). Covers the log sweep, the verification sweep
    (session.py:1353), the gain-cal pink noise (today butter(4), 24
    dB/oct, gain_calibration.py:185-190) and measure_nearfield.
  - AE 2 BOUNDS on the EXACT played array (after level scaling and
    fades), on the tilt-compensated magnitude L(f) = 20*log10|X(f)| +
    10*log10(f / f_ref); reference = median of L over [2*hpf, 4*hpf].
    (a) every bin <= hpf/2: L <= ref - 40 dB; (b) every bin <= hpf/4:
    L <= ref - 60 dB; (c) total energy below hpf/2 <= -40 dB re total
    energy; (f) a raised-cosine taper of at least 10 ms at start and
    end, first and last samples 0. Teeth: a 24 dB/oct stimulus FAILS
    (a); a sweep without the taper FAILS (f). Same bounds for the
    gain-cal noise (hpf := f_low), the verification sweep and
    measure_nearfield. Supersedes the Architect's example bound in
    R6(a) and the AE's first version (linear-bin median over [2*hpf,
    0.5*f_end], which would fail a correct 48 dB/oct stimulus).
  - AE 3 DECONVOLUTION: deconvolve() takes the same filtered array
    that was played as its reference, and nothing else.
  - AE 4 NO BOOST BELOW THE HPF: correction never inverts the roll-off
    below the HPF. Test, at every bin below hpf: |combined| <=
    max(|HPF-only| * 10^(0.1/20), 10^(-80/20) * passband peak of
    combined). A red result on current code is an AE finding, fixed
    within F-391.
  - AE 5 d031_exception: a mapping; required keys reason (non-empty),
    directive (e.g. "owner"), date (ISO), min_stimulus_hz (number, >=
    20). A null mandatory_hpf_hz with no valid d031_exception is
    REFUSED (editor, session, generator: one shared validator);
    d031_exception together with a non-null mandatory_hpf_hz is
    REFUSED; with an exception the stimulus floor is min_stimulus_hz
    and the bounds apply with hpf := min_stimulus_hz. Today only
    dayton-ultimax-umii18-22-sealed-120l qualifies (directive "owner",
    min_stimulus_hz 20, reason from its comment block). The exception
    waives the HPF only; the F-388 excursion check still applies once
    it exists.
  - Architect A2 addendum (AE accepted): stimulus build order: sweep
    with its Hann fades -> zero-pad >= 0.5 s on each side ->
    zero-phase HPF >= 48 dB/oct -> outer raised-cosine taper >= 10 ms
    (end samples exactly 0) -> scale. The padded array is both the
    played signal and the deconvolution reference. The DC bin is
    skipped in the tilt term, f_ref = hpf. Gain cal uses hpf := f_low
    = max(100, hpf); the exception case hpf := min_stimulus_hz. Added
    AE checks: (i) at hpf = 20 Hz, the samples in the outer 10 ms
    taper zone, before tapering, are <= -60 dB re the array peak; if
    not, use a longer pad, never loosen the bound; (ii) the gain-cal
    level uses the RMS of the shaped array actually played; test at
    f_low = 800 within 0.1 dB.
  - Architect A1 addendum (via CM): partly superseded by the
    AE/Architect correction above; recorded when the Architect's
    updated A1 text arrives.
  - F-391 ruling COMPLETE (CM, 2026-10-25):
    /tmp/f391-architect-ruling.md, sha256 3f10fc5a...b0a9 (PM frozen
    copy /tmp/pm-backlog/f391-architect-ruling-3f10fc5a.md).
    AUTHORITATIVE SET for worker-5, in order: R1-R7, then the FINAL
    ADDENDUM (sha256 7e467465, F-1 to F-9), then PART B (60095f5d,
    F-10/F-11), then PART C (b91ac082). A1 and A2 are SUPERSEDED IN
    FULL (supersedes the A1 line above). The AE APPROVED the set;
    nothing open. The brief goes to worker-5 after #55 merges (lane
    F-390, then F-391).
  - Final addendum F-8 (one identity validator): today
    speaker_routes.py:162/218 requires mandatory_hpf_hz to be a number
    (the editor cannot save the Dayton identity) and
    config_generator.py:218-225 raises on None; ONE shared validator
    for the editor save, the session start (R2) and the generator.
    Tests: the editor round-trips the Dayton identity; a null without
    an exception gives 422 at the editor and a refusal at session
    start; an exception with a non-null hpf is refused in both places.
    F-3: the gain-cal low edge by zeroing/tapering the bins below
    f_low in the existing frequency-domain step
    (gain_calibration.py:177-183). Timing note (part B): every delay
    measurement uses the same padded reference array; reviewers check
    that no code path rebuilds an unpadded sweep.
  - PART C (Architect, accepted AE C2/C3): F-2 step 1 AMENDED: the log
    sweep starts at f_start = max(20.0, hpf/2), not at hpf (a start at
    hpf puts the Hann fade-in on the HPF edge and hpf to about 1.2*hpf
    is regularised away, the band where the deployed HPF and the
    correction still act; the step-3 high-pass keeps the stimulus at
    hpf/2 >= 40 dB down, about 8 dB margin). For a d031_exception
    identity hpf := min_stimulus_hz; gain-cal unchanged, f_low =
    max(100, hpf). SUPERSEDES R3 "f_start = max(20.0, hpf_hz)" above.
  - PART C F-5 mutations REPLACED (supersede R6 (e) "f_start -> 20.0"
    above, which would stay green because the step-3 high-pass still
    protects): each must turn at least one test red: (m1) step 3
    (stimulus high-pass) removed -> F-4 bounds red; (m2) step 3 at 4th
    order (24 dB/oct) -> F-4 red; (m3) step 4 (outer taper) removed ->
    F-5 taper check red; (m4) deconvolve() given the unpadded or
    unfiltered sweep -> F-6 / R6(d) red. The QE runs or reviews these
    as F-391 PR test evidence.
- Deployed-coeff HPF verifier (Architect R5 under F-391;
  AE-conditional, only if the AE wants it): check that the coeff WAVs
  deployed in the convolver carry each channel's D-031 HPF. Not F-391
  scope.
  AE (2026-10-25): YES, P2. AE text: "At session start and before each
  deploy, read the coefficient WAVs that are actually deployed. Verify
  that each channel's magnitude response meets its identity's
  mandatory_hpf_hz, with the same tilt-free bound as F-391 (a)/(b). On
  a FAIL the session or deploy is refused." Why: after F-391 the
  stimulus is protected, but music playback still depends only on the
  deployed FIR; the hash record (B) proves which file is deployed, not
  that it contains the HPF. Supersedes "AE-conditional" above.
- Speaker-config reset-to-default action (Architect R4 under F-390;
  not F-390 scope).
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
  the crossover check yet. (a) is PROMOTED to F-390 (PO,
  2026-10-25; AD N4); see F-390.
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
  #55 head 2e29f82e (pushed, CM, 2026-10-25): the U1 single-source
  check, fixtures slope-only 96 -> 48, the negative save tests;
  body v2 set; re-review requested from all 7 reviewers. The branch
  is 7 commits behind main. CI run 40236549456.
  #55 Rule 13 at 2e29f82e (verdicts posted verbatim, CM,
  2026-10-25): APPROVED QE (test content; conditional on CI),
  Architect, UX (U1 incl. G1/G2, N1/N2 done), SecSpec (conditional
  on CI T1-T3 at the final head), AD (L1 resolved by the
  real-profile ceiling; does not cover CI/F-363). TW CHANGES
  REQUESTED, one blocker: docs/user-journeys.md:289-294 still says
  48-96 dB/oct; worker-5 is applying the TW text, the AE confirms
  the claims, body v3 adds QE N-a/N-b. AE verdict pending. All
  approvals lapse on a head move; UX does a diff-only re-check at
  the merge-main head. AE APPROVED at 2e29f82e (comment
  6403796828), so #55 is at 6/7; TW CHANGES pending worker-5's
  user-journeys.md:289-294 fix. The new head voids the approvals:
  a diff-only re-check by all 7 follows.
  #55 backlog from the 2e29f82e verdicts (pre-existing, none
  blocking):
  - SecSpec LOW: the measurement session's profile_name has no slug
    check and can load any readable *.yml. Fix before F-037 is
    closed for gigs.
    SecSpec (2026-10-26, from the #55 verdict, F-374 lane): this is
    path traversal to any *.yml, the same class as F-372 and F-398.
  - Architect N2: the room-correction import path is set up 3
    ways; consolidate it into one helper.
  - Architect N3 = AD N5: the editor and validate_profile_crossover
    accept crossover as a LIST; generate_profile_filters calls .get
    on it -> AttributeError -> 500. AE (same item): fails closed,
    no shipped profile uses list form, pre-dates #55.
  - AD L2 (extends L2 above): the default_profile.yml line 19
    comment "48-96 recommended" is wrong now that 96 is rejected.
  - AD N3: the editor browser test fakes the 422 on the PUT, no
    real backend round trip; a tmp profiles dir would fix it. QE
    decides.
  - UX: a missing profile only logs a warning at the pre-check; the
    "not supported" note moves from c-danger to a warning style
    once one exists.
  - TW non-blocking: the profile crossover schema doc
    (speaker-management-requirements.md section 4); the "LR
    magnitude as min-phase FIR" clarification in CLAUDE.md, D-001
    and the theory docs (CLAUDE.md is the owner's); tracking
    records on main for F-374, F-383, F-385 and F-387.
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
  #55 TW fix (CM, 2026-10-25): a4ef9abc (TW docs fix) verified, held
  for the AE's two wording edits, then pushed for a diff-only re-check
  by all 7; the main merge comes after #56. At ce872e30 (2 docs
  commits, diff-only re-check): UX APPROVED (docs match the code
  verified at 2e29f82e); AD APPROVED (does not cover CI; lapses on a
  head move; full verdict with the CM).
  #55 backlog (worker-5, via CM, 2026-10-25; outside the #55 fence):
  (1) story ACs disagreed with F-374 (only LR 24/48): US-011.md:17 and
  user-stories.md:761 said "48-96 dB/oct", US-091.md:34 and
  user-stories.md:6831 "24/48/96 dB/oct". PO RULING (2026-10-25):
  narrow to LR 24 or 48 dB/oct, default 48 from the speaker profile,
  each marked "(narrowed per F-374, PO 2026-10-25)"; PM draft story
  batch /tmp/pm-bs1/ (base main dfdbbbd6), AE wording check pending;
  if the AE says the default should not be 48, the AE value applies
  with no extra PO round. (2) the user-journeys.md crossover journey
  step 4 runs runner.py, still on the legacy alignment (also in the
  #55 body backlog list). (3) TW non-blocking: a profile schema doc
  and a min-phase FIR vs IIR clarification (= the TW non-blocking item
  above).
  #55 TW backlog (UX, ce872e30, non-blocking): user-journeys.md should
  say where a refused slope or type is reported: the "Not supported"
  note in the editor and the "Profile X: ... Fix it in the speaker
  editor." message.
  #55 TW backlog (AD L3/L4, low, wording, ce872e30): L3 user-journeys
  "two legs sum flat" overclaims: the LR8 post-combine is not gated
  (F-383), and the LR4 profile is verified only within the +/-1 dB
  ceiling. L4 "the session start is refused" overclaims: profiles that
  exist only under /etc are skipped (backlog (a) = F-390) and deep
  validation does not run the check (backlog (c)).
  #55 7/7 APPROVED at ce872e30 (CM, 2026-10-25; posted verbatim,
  comments 6403940247-6403942053); CI 40238022026 in progress. Strict
  protection: a main merge after #56, then a diff-only check by all 7.
  QE: confirm the 270 collected vs 271 run discrepancy (likely a
  module-level skip) via --collect-only; one body line at the
  main-merge push.
  #55 after #56 merged (CM, 2026-10-25): worker-5 is merging main
  1c36889f in; then a diff-only re-check by all 7; one more main
  update after #54 merges (strict protection), then the BS1 docs PR
  (c37b8f3c; CM rechecks base blobs).
  #55 at d0a317c3 (CM, 2026-10-25): worker-5's merge of main 1c36889f
  pushed; three-dot diff byte-identical to ce872e30; room-correction
  1244/0/1, web-ui unit 937/1; body v4 posted; CI 40241633913 running;
  diff-only re-check out to all 7. APPROVED so far: UX (own cmp of the
  diff), AD (no new findings; not covering CI; lapses at the post-#54
  update) = 2/7. One intermittent "1 warning" in a web-ui unit run, 2
  reruns clean; worker-5 tries to capture its text; possibly the F-387
  family; the QE is informed.
  UPDATE (CM, team-lead, 2026-10-25; supersedes "2/7" above): 7/7
  APPROVE posted at d0a317c3 (comments 6404488379 to 6404489902), all
  conditional on CI 40241633913 green. QE N2, verbatim: "unexplained
  intermittent warning, 1 of 3 runs, d0a317c3 (web-ui unit)"; worker-5
  is trying to capture the text. After #58 merged, #55 moved to
  9fd7bf2b (update-branch with main dfb81cd7; diff cmp-identical); the
  d0a317c3 approvals lapse (strict protection); diff-only re-check out
  to all 7; CI 40242141720. Re-APPROVED at 9fd7bf2b: UX (own cmp), AD
  (not covering CI) = 2/7. The post-#54 update needs one more
  diff-only re-check (cmp the three-dot diff; room-correction 1244/0/1
  unchanged; CI green at that head). Body nits for that push (same
  fix): TW "(1232 -> 1244 total)" -> "(1233 -> 1245 collected)"; QE N1
  "1233 -> 1245 collected (1244 passed / 0 failed / 1 skipped)".
  UPDATE (CM, team-lead, 2026-10-25; supersedes "2/7"): 6/7 posted at
  9fd7bf2b (SecSpec, UX, TW, AD, Architect, AE); QE pending; CI
  test-and-build running. QE N2 EXPLAINED (worker-5, log
  /tmp/worker5-f374/webui-warn-run2.log; supersedes "unexplained"): in
  src/web-ui/tests/unit/test_collectors.py, test
  TestFilterChainPushEventDesync::test_multiple_events_before_response:
  a ResourceWarning (unclosed socket/transport) plus
  PytestUnraisableExceptionWarning in _SelectorTransport.__del__ after
  the loop is gone, ~1 of 3 runs; a mock GM server connection is still
  open when asyncio.run closes the loop. Not from #55. QE test
  hygiene: close the mock-server writer before the loop exits.
  Probably the F-387 family, unconfirmed (PM asked the QE: F-387, new
  ID or none). TW non-blocking: the #55 body line 77 "merge head
  d0a317c3" stays as the record of where the tests ran.
  UPDATE (CM, 2026-10-25; supersedes "6/7", "QE pending" and "Probably
  the F-387 family, unconfirmed"): 7/7 posted at 9fd7bf2b, the QE
  approving, conditional on CI 40242141720 (test-and-build running).
  QE N2 closed for #55 as F-387 (extended, see F-387). The post-#54
  update and its diff-only re-check by all 7 still apply.
  UPDATE (CM, 2026-10-26): CI 40242141720 FAILED: only the E2E test
  test_level_bridge_sw_has_signal (F-394), identical silence message;
  log /tmp/ci55-40242141720-failed.log. The CM takes it to the QE with
  #54's result; the F-394 fail-again plan most likely applies
  (strict-xfail test-only PR, then update-branch, then diff-only
  re-checks).
  UPDATE (CM, 2026-10-26): #55 is HELD. QE ruling pending between (a)
  the update-branch run onto main ba5cc200 counting as its single
  attempt, or (b) the F-394 strict-xfail quarantine PR first.
  UPDATE (QE ruling via CM and team-lead, 2026-10-26; supersedes "QE
  ruling pending" above): the QE ruled (b). #55 is held until the
  F-394 quarantine PR merges. PR #59 OPEN (branch
  test/F-394-quarantine from ba5cc200, worker-5, head 011bfa5d): one
  line, marks only test_level_bridge_sw_has_signal xfail(strict=True)
  citing F-394. Rule 13 requested from all 7; CI 40245796169 queued.
  #55 stays at 9fd7bf2b until #59 merges; then update-branch onto
  main, the QE's diff-only re-check and a new CI run.
  UPDATE (CM, team-lead, 2026-10-26): #59 has 7/7 APPROVE at 011bfa5d,
  all posted verbatim (comments AE 6405030806, SecSpec 6405031003, TW
  6405031203, QE 6405031402, Architect 6405031668, UX 6405031894, AD
  6405032125; verdict files /tmp/pr59-architect-verdict-011bfa5d.md,
  /tmp/tw-verdict-pr59-011bfa5d.md, /tmp/pr59-ad-verdict-011bfa5d.md,
  /tmp/pr59-review-011bfa5d/AE-verdict.md). Conditions: QE, CI
  40245796169 green with test_level_bridge_sw_has_signal SKIPPED or
  XFAILED and nothing else red; SecSpec, CI T1-T3 green at this head;
  AD, test_timestamps_monotonic PASSED, not SKIPPED (not DJ-gated).
  The QE, AE, Architect and AD accept not narrowing the marker
  (raises= would separate nothing; all failure paths are asserts). The
  CM merges under standing consent on: CI green; the sw test SKIPPED
  or XFAILED; nothing else red, no new XPASS, test count unchanged;
  test_timestamps_monotonic PASSED. CI 40245796169 still running.
  UPDATE (CM, team-lead, 2026-10-26; supersedes the 7/7 at 011bfa5d
  and CI 40245796169 above): #60 merged first, so update-branch moved
  #59 to a55472750fe6d576cde3936b3f54b465dcd6f3d2 (main a3270b5e
  merged in); against main the change is still test_audio_flow.py +1.
  CI 40245796169 was cancelled by concurrency; the new run is
  40247129046, still running (no result recorded; the merge conditions
  above apply unchanged). All 7 approvals voided; diff-only re-checks
  (bundle /tmp/pr59-review-a5547275, SUMS af6c7689): 6/7 re-approved
  (AD, UX, QE, SecSpec, Architect, AE; comment IDs from the CM; the
  QE's is conditional on that run meeting the merge evidence), TW
  outstanding. After the merge: the TW's F-394 Status and index
  follow-up on main, then #55 update-branch, QE diff-only re-check,
  new CI.
  UPDATE (CM, 2026-10-26; supersedes "6/7 ... TW outstanding" above):
  #59 is 7/7 at a5547275: AE 6405217419, SecSpec 6405217679, TW
  6405217910, QE 6405218193, Architect 6405218430, UX 6405218673, AD
  6405218958. The PR body's head line was updated (QE nit); the head
  is unchanged. CI 40247129046 still running. Merge criteria (CM):
  T1-T3 green; test_level_bridge_sw_has_signal XFAIL or SKIP;
  test_timestamps_monotonic PASSED; no other red; no new XPASS (the
  known F-262 test_full_session_api XPASS excepted); collected count
  unchanged.
  UPDATE (CM, 2026-10-26): #59 MERGED at a5547275 (7/7 as above); main
  f01e6647. CI 40247129046 passed. F-394 is quarantined on main
  (strict xfail). Next: the TW's F-394 Status/index follow-up on main;
  #55 update-branch (its approvals lapse), the QE's diff-only
  re-check, new CI.
  UPDATE (CM, 2026-10-26): #55 at 17144904 (update from main f01e6647)
  is 7/7 (AE 6411956420, SecSpec 6411956836, TW 6411957507, QE
  6411958118, Arch 6411958603, UX 6411959075, AD 6411959557; QE
  conditional on CI). Waits on CI 40294373355 (not yet checked by the
  CM). Then F-390/F-391 (worker-5, if alive; team-lead) and the US-173
  WAV regeneration.
  AD L3 suggested text (via CM; TW/AE tidy): "designed so the two legs
  sum flat; the shipped LR4 profile is verified within ±1 dB, LR8
  after room correction is not yet verified (F-383)" (markaudio LR4
  passes only ±1 dB / 35 deg, F-385). AD L4: deep validation and
  activate don't check yet (backlog c), and the session pre-check
  skips /etc-only profiles (a = F-390) and fails only at CP-5; hedge
  the text, or it becomes true with F-390.
  Slope ACs (worker-5 point (1)): AE wording check done (2026-10-25).
  US-011.md:17 / user-stories.md:761 OK as drafted; the default stays
  48 (all shipped profiles except the 200 Hz markaudio/Ultimax one use
  it; the generator defaults to it). US-091.md:34 /
  user-stories.md:6831 NOT OK as drafted: the code at ce872e30 has one
  profile-wide crossover.slope_db_per_oct plus an optional
  high_slope_db_per_oct per bandpass driver, both in {24, 48}. AE
  text: "Crossover slope LR 24 or 48 dB/oct, one value per profile
  (narrowed per F-374, PO 2026-10-25). Per-crossover-point slopes are
  a future item: both legs that meet at one crossover point must use
  the same LR order." Batch BS1 frozen: /tmp/pm-bs1/, MANIFEST sha1
  c37b8f3c (base main dfdbbbd6); applied after #55 merges (CM routes).
  PO informed.
  BS1 is PR #62 (CM, 2026-10-26; head 20903a04, docs-only). #62 review
  one-liners (AD L1, TW; not blocking; the author kept the #62 head so
  the approvals stand): (1) AD, verbatim: "The US-089 AC crossover
  editor slope preset '24/48/96' (US-089.md:32 and
  user-stories.md:6733) contradicts F-374 (LR 24/48 only, one per
  profile). Narrow it the same way as US-011 and US-091." TW: since
  F-374 the editor save rejects 96; UX sees the narrowing. (2) AD,
  verbatim: "The crossover.py:14 docstring still says '48-96 dB/oct',
  but the generator only accepts 24 and 48. Fix the comment the next
  time someone touches the file."
- Steeper crossover slopes (96 dB/oct LR and up; PO, 2026-10-25;
  Low/P3, future work): steeper slopes as minimum-phase FIR. AC (AE):
  the AE first evaluates the group delay and pre-echo behaviour at the
  crossover frequency. If the AE sees a real need (e.g. driver
  protection near a tweeter's Fs), the AE may raise the priority; that
  ruling goes back to the PO.
  AE note (2026-10-25): the min-phase FIR follows LR's phase, so a
  steeper order means more group delay at the crossover frequency; at
  80 Hz that weighs against the transient goal. No need seen now.
- **F-392** Unequal LR orders at one crossover point (P2, audio
  quality, not speaker safety; AE, 2026-10-25): a bandpass driver's
  high_slope_db_per_oct can differ from the profile slope that the
  next driver up uses at the same crossover frequency (e.g. the mid's
  upper edge at LR8, the HF high-pass at LR4). LR legs of different
  orders don't sum flat: a dip or bump of a few dB around the
  crossover frequency. validate_profile_crossover accepts this today.
  AC (AE): "the validator refuses a profile where the two legs meeting
  at a crossover point use different slopes". No shipped profile sets
  high_slope_db_per_oct, so nothing deployed is affected.
  UPDATE (#62 reviews, 2026-10-26; QE, UX, Architect and AE raised the
  same gap; one row, no new ID): it is the counterpart of the US-091
  AC that #62 narrows; main 5f3af36a still accepts it
  (generate_profile_filters.py:46-69 and :154). AE (P3, not a safety
  item), verbatim: "validate_profile_crossover
  (generate_profile_filters.py:46-69) accepts a bandpass driver's
  high_slope_db_per_oct ≠ the slope of the leg it meets, so mismatched
  LR orders at one crossover point (non-flat sum) can be generated.
  That conflicts with the US-091 AC 'same LR order at one crossover
  point'. Fix: reject high_slope_db_per_oct ≠ section slope (or derive
  it), with a test. No profile on main sets it today." QE adds: also
  reject mixed slopes between crossover sections, with a test that a
  mixed LR4/LR8 profile raises CrossoverSpecError. Architect: e.g. BP
  high 24 against HP 48; reject the mismatch or drop the key.
  Priority: P2 above (AE 2026-10-25) vs P3 now (AE); the AE's latest
  word governs (P3).
- **F-393** Check-sandbox guard misses configs/drivers (P2, PM
  provisional, QE to confirm; AD L1 + QE, #54 at 46343238,
  non-blocking there, via CM 2026-10-25): the room-correction check's
  sandbox guard in flake.nix (`test -d configs/venues && test -d
  configs/speakers`) does not cover configs/drivers. If that folder
  were missing from the sandbox, #56's driver-record tests (the F-363
  full-set gate) would skip silently. Fix (AD, QE): add
  configs/drivers to the guard. Related: F-380 (CI builds no
  checks.*).
  UPDATE (QE, 2026-10-25; supersedes "PM provisional, QE to confirm"):
  P2 confirmed. A silent-skip pattern (F-362 family). Fix: add `test
  -d configs/drivers` to the guard, or assert the skip set by name
  once F-380 gates checks.
- **F-394** DJ-mode E2E group: ensure_dj_mode skips on mode-switch
  failure and the level-bridge signal test fails whenever it does run
  (High, QE; AE confirms: safety-relevant, CI has never shown signal
  on the app tap or that mute silences the output; QE owns the record,
  AE reviews; via CM 2026-10-25; NOT an F-262 update; replaces the
  AE's F-395 proposal, F-395 not allocated). Evidence (QE, last 23 CI
  runs): test_level_bridge_sw_has_signal SKIPPED 8, FAILED 2
  (40240718064 #54, 40231575303 US-172), never PASSED. Mechanism:
  ensure_dj_mode (src/web-ui/tests/fixtures/backend.py:389) calls
  pytest.skip when set_mode fails; otherwise the test reads one
  snapshot ~0.15 s after the switch. ACs (QE ruling + addendum, AE):
  - (i) ensure_dj_mode FAILS instead of skipping (the AE's (vii) is
    the same AC).
  - (ii) root-cause set_mode dj failing in the CI local-demo.
  - (iii) diagnose why level-bridge-sw is silent in DJ mode (missing
    stimulus or missing link); polling after settle is only a
    robustness detail; the race hypothesis is withdrawn (supersedes
    the AE's ~5 s poll and the Architect/AE race views in the #54
    notes).
  - (iv) N>=5 consecutive CI runs with the DJ group PASSED (-rs output
    saved).
  - (v) correct F-262's D-249 paragraph ("passes consistently" is not
    supported by CI) and reconcile the F-270 xfail:
    test_mute_e2e.py:90 (test_unmute_restores_levels) cites "F-270:
    ... no audio stimulus in local-demo", but F-270 is the Transfer
    Function tab record, so the citation is wrong, and its claim
    contradicts test_level_bridge_sw_has_signal; re-point the xfail
    reason to F-394 (AE).
  - (vi) the mute E2E tests are vacuous (AE P2, folded):
    test_mute_silences_level_bridge only checks that level data
    arrives before the mute, never that there is signal; in CI
    40240718064 the sw tap was silent and the mute test still PASSED.
    (1) establish whether local-demo DJ mode carries a stimulus on the
    sw tap; (2) if it does, the mute and unmute tests assert pre-mute
    signal above -100 dB on the same tap and FAIL without it, and the
    xfail is removed; (3) if it doesn't, the sw signal test and the
    mute tests get a stimulus added.
  - (viii) the fix PR removes the quarantine marker, if one was added.
    SecSpec LOW (#59 verdict, 2026-10-26), verbatim: "The quarantine
    xfail on test_level_bridge_sw_has_signal covers any failure, so a
    dead bridge or closed 9100 would show as XFAIL. Narrow it: split
    the liveness asserts into an un-quarantined test. QE/AD decide
    how."
    QE (#61 review, 2026-10-26): test_mute_e2e.py
    TestUnmuteRestoresSignal still cites F-270; the F-394 fix PR
    re-points it to F-394 (AC v/viii).
  Rules (QE, AE; via CM 2026-10-25): no quarantine marker in #54 or
  #55; one logged rerun only if this test is the sole failure; a green
  E2E most likely means the group was skipped; later PRs touching GM,
  mute or level-bridge are held to (iv). HARD RULE: nothing may
  describe mute as verified until AC (vi) passes. If #54's E2E fails
  again (QE + AE; the Architect may object): no reruns and no
  indefinite hold; a separate test-only PR puts a strict xfail on
  test_level_bridge_sw_has_signal, reason F-394, through Rule 13; then
  update-branch on #54/#55 and diff-only re-checks.
  Diagnosis lead (QE, via CM, 2026-10-26; a lead, not a conclusion;
  rule in or out under AC (ii)/(iii)): the test-e2e app does not set
  WP_STORE, so local-demo.sh l.114-115 resolves `nix eval --raw
  nixpkgs#wireplumber.outPath` from the unpinned flake-registry
  nixpkgs, not from flake.lock, and puts that WirePlumber into
  XDG_DATA_DIRS, WIREPLUMBER_MODULE_DIR and PATH (l.138-141). The E2E
  environment is not hermetic: the WP version and config search path
  can drift between CI runs, a plausible contributor to the
  nondeterministic DJ switch. Fix candidate: export a WP_STORE pinned
  from the flake, like PW_STORE. Same at both #54 heads, so not a #54
  concern.
  Evidence update (CM, 2026-10-26): #55 CI 40242141720 FAILED on this
  test only, identical silence message (1 failed, 69 passed, 7
  skipped, 4 xfailed; log /tmp/ci55-40242141720-failed.log). That
  makes 3 of 3 failures whenever DJ mode engaged. #54 run 40242139498
  still in its E2E step; the CM takes both results to the QE together;
  the pre-agreed fail-again plan most likely applies.
  Non-blocking notes from the #59 review (2026-10-26, via CM; the QE
  as record owner places them):
  - UX N1, for AC (iii): say explicitly whether the production web-UI
    sw-tap meters on the Pi are also silent in DJ mode, or only the CI
    local-demo. If the Pi is affected, link it to the F2 rule
    ("confirm live meters before amps on") and to the F2 / U8 METERS
    STALE item.
  - Liveness split (AD L1; SecSpec LOW; Architect): no remaining test
    checks that the level-bridge-sw peak list is non-empty. Move the
    liveness and connectivity asserts (lines >= 1, peak list
    non-empty) out of the quarantined test into an un-quarantined
    test, or make it an F-394 AC.
  - Record (AD L2, TW): main has no defects/F-394.md, so the xfail
    marker points at a backlog line only. The TW adds the record with
    ACs (vi) and (viii) in the docs/F-395-annotations PR if the QE
    agrees, together with the AC (v) F-262 D-249 correction ("now
    passes consistently", contradicted by #59).
  - AD L1 on #60 (Low, the QE decides): put the F-394 sentence "sw tap
    silent, mute test still passed" into the #59 xfail reason or PR
    body.
  - SecSpec (#60 review): supports pinning WP_STORE from flake.lock as
    the F-394 fix (CI supply chain; see the diagnosis lead above).
  - Status follow-up (QE, TW): if #59 merges before #60, the F-394
    Status line and its index row change to "quarantined (PR #59,
    strict xfail)".
    UPDATE (CM, QE, 2026-10-26): #60 merged first, so this follow-up
    is a separate main docs change by the TW after #59 merges (not
    part of #59).
    UPDATE (CM, 2026-10-26): #59 merged (main f01e6647); this
    follow-up is now due (TW).
- **F-395** Gain readback is blind on a suspended node (P1; AE co-owns
  per A5; PM provisional ID, AE to confirm; Gate-2 r6b (ii-c), via CM
  2026-10-26): on a suspended node, the gain readers in the r6b matrix
  return 0, not the stored conf value. A "0" reading therefore does
  not prove "muted" for a suspended node. Against B1 / safety.md check
  10. A set made while suspended applies after the resume ((ii-a));
  boot 0 then resume is silent ((ii-b)). Open: the AE and Architect
  ruling on the gate2.py design (refuse suspended nodes, or wake them
  with a silent stream) and whether the Pi P-a check is now due; the
  AE's interim text for D-070 rows 14-15 (PM, TW).
  UPDATE (AE, 2026-10-26; supersedes "PM provisional ID, AE to
  confirm" and the title above): the AE asked for this P1 with the AE
  and the Architect as co-owners. Title: "Gains readback is blind on a
  suspended filter-chain node, so the gains check gives a false PASS."
  Evidence: Gate-2 r6b (ii-c): a conf default of 0.25 reads 0.000000
  while the node is suspended, in all 4 stacks, yet the audio proves
  0.25 was applied; 0.000000 is the gains check's PASS value (D-063),
  so the false PASS is in the dangerous direction. ACs (AE):
  - (a) gate2.py counts a reading only when the fc and fc-out nodes
    are idle or running, as shown in the same snapshot; otherwise NOT
    VERIFIABLE.
  - (b) a selftest mutation: a suspended node with a non-zero default
    must not PASS.
  - (c) every past gains PASS recorded without the node state is
    marked unproven (PM/QE list them). PM candidates from this
    backlog, for the QE to complete: US-163 AE check #10 PASS
    (enum-params, 8 gains 0/0); US-163 AC14 PASS (16/16 gain values 0,
    CM-DEP-.89-2). Nothing amps-on depended on them (AE: amps off,
    nothing connected).
    AE RULING (2026-10-26): both are reclassified from PASS to NOT
    VERIFIABLE and are no longer evidence. They are not FAILs: the
    conf defaults were 0 at the time, so nothing points to an unsafe
    gain; a reader on a suspended node simply can't tell that apart
    from a non-zero gain. Both are re-run under the new rule (node
    state read before and after) at the next Pi gains check; the CM
    may fold that into the 5a OBSERVE. Any record the QE adds to the
    list gets the same treatment, unless its node state was logged at
    the time. F-395 ID CONFIRMED by the AE (AE owns, Architect
    co-owns).
  - (d) Pi OBSERVE of the node states, then P-a.
  Still open: the joint AE + Architect r6b text (gate2.py base rule
  and optional silent-zero wake mode, P-a amendment to condition (f),
  the new gains status line), which the Architect sends to the CM for
  worker-3. The AE's draft is the frozen copy above.
  UPDATE (joint r6b ruling final + Addenda 1-2, 2026-10-26; supersedes
  "Still open: the joint AE + Architect r6b text" above): settled.
  F-395 = the (ii-c) P1, AE owner, Architect co-owner (Addendum 1 F,
  Addendum 2 item 3). AC (a) and (b) are specified by the gate2.py
  base rule and selftest cases 1-5 in the Gate-2 ruling block
  (worker-3 implementing); AC (d) is the Pi step 1 OBSERVE and the
  amended P-a (deferred while .89 is down). Follow-ups: US-176
  (canary), F-397 (readback consumer audit).
  AC (c) LIST COMPLETE (QE, 2026-10-26; searched main dfdbbbd6 and all
  local and gh branches; supersedes "PM candidates ... for the QE to
  complete" above). None of these records logs the fc or fc-out node
  state at the reading, so all 9 are NOT VERIFIABLE under the AE
  ruling, not FAIL (conf defaults were 0); a logged "sink running" is
  the USBStreamer sink and doesn't count. Lab note =
  docs/lab-notes/US-163-pi5-bootstrap.md:
  - (1) US-163 AE check #10 PASS (enum-params, 8 gains 0/0);
  - (2) US-163 AC14 PASS, CM-DEP-.89-2 (lab note l.178 and the l.229
    note);
  - (3) l.276, T54 after return, "16 gain-relevant values exactly 0
    (pw-dump)";
  - (4) l.406, AC17 Session B step (a);
  - (5) l.412, AC17-B step (c), the post-PW-restart recovery read;
  - (6) l.418, cold cycles 1 and 2;
  - (7) l.465, step (b) baseline;
  - (8) l.529, AC19 redeploy of merged main (CM-DEP-.89-AC19);
  - (9) docs/project/defects/F-373.md l.38, the interim recovery
    procedure (same evidence as 5).
  Deliberately not listed (QE; the AE agrees): the Pi 4 era records
  (C-009, TK-249, S-005, TK-039: listening tests on running nodes or
  CamillaDSP mixer reads on retired hardware); F-298 A6, safety.md
  check 10 and amps-on item 8 (criteria, not records); the gate
  "closed / no pending gains" PASSes (GM API reads, not gain
  readbacks).
  AE RULING on the list (2026-10-26): the list is complete as given.
  (i) The AE checked main dfdbbbd6 and TW batch v17: neither
  safety.md, D-070 nor v17 cites AC17-B or the cold cycles as gains
  evidence; safety.md items 8 and 13 are acceptance criteria still to
  be tested, so the TW changes nothing there. The two facts the QE
  names (output safety at power-on from the D-063 gains starting at
  Mult 0; the F-373 interim recovery with the gains at 0) stay as
  design facts but lose the readback proof; until the re-run they rest
  on the conf defaults alone. Records are annotated APPEND-ONLY, never
  rewritten (history): the TW adds one dated line to each of the 9
  entries (lab note l.178/229/276/406/412/418/465/529 and F-373.md
  l.38), verbatim: "2026-10-26: gains result NOT VERIFIABLE under
  F-395 (fc/fc-out node state not logged); re-run pending (F-395 AC
  c)." Plus the F-373 AC2 addition (see F-373). Vehicle: a small
  docs-only PR or part of the F-318 batch (PM and TW choose). (ii)
  Re-run scope ACCEPTED: one read per context, fc/fc-out state logged
  before and after: after boot, after a PW restart, after a cold
  cycle; plus after a WirePlumber restart (D-070 row 15 relies on it)
  and after the F-373 recovery (PW plus bridge restart) if it differs
  from the plain PW restart. Precondition: the step 1 OBSERVE. If it
  shows fc or fc-out suspended or never run in a context, that
  context's re-run can't produce a PASS; it waits for US-176 or F-396
  (Addendum 1 B) and is not a FAIL meanwhile. The cold cycle waits
  until the owner says they're available and blocks nothing.
  UPDATE (AE ruling via CM, 2026-10-26, agreed with the Architect;
  supersedes "The cold cycle waits until the owner says they're
  available" above): the read-only check after the US-172c recovery
  power cycle counts as the cold-cycle gains evidence (F-395 AC (c)),
  so no second owner trip is needed. It also counts as the step-1
  OBSERVE "right after boot". Order (joint): US-172c steps 1-6
  (read-only, no graph), then this read, then steps 7-8; the time
  between the boot and the read is logged. Records (AE, six conditions
  plus the CM's four points; record list
  /tmp/pm-backlog/cold-cycle-read-plan-91bb526b.txt):
  - 1) Cold: the owner's statement, verbatim, that power was
    physically removed (unplugged or switched off at the PSU), ideally
    with roughly how long. A reset button or a software reboot doesn't
    count.
  - 2) This boot: boot id, uptime and the deployed revision/toplevel,
    because the conf defaults are what's being proven. Plus the Mac
    ping down window.
  - 3) First touch: the read is the FIRST session on the graph after
    boot. Before it: no CHANGE, no stream, no pw-cli set, no GM mode
    change, no web-UI action. If anything ran first, log it, and the
    result counts only as an after-boot read, not a cold-cycle read.
    ("No GM" means no GM RPC or web-UI action; the services start at
    boot as normal.)
  - 4) The read, per the r6b rule: pw-dump state of the convolver,
    convolver-out and the USBStreamer node, before and after the
    enum-params read; all 16 Mult and Add values exactly 0.000000;
    pw-dump structure (one of each node, 8 gains); D-063 gate closed.
    Both gain nodes must be idle or running and unchanged, otherwise
    the result is NOT VERIFIABLE.
  - 5) Hardware: the USBStreamer hw mixer (amixer dump, read-only)
    shows Playback Volume unchanged at 0 dB, the same as after AC17.
  - 6) Read-only: no wake of any kind.
  If the result is NOT VERIFIABLE (the chain suspended or never run at
  boot), that is the step-1 OBSERVE result and a valid finding, not a
  FAIL; per Addendum 1 B the cold-cycle gains proof then waits for the
  canary (US-176) or the no-suspend fix (F-396), and the cold cycle is
  batched with the next physical owner task; no second trip now (AE).
  Annotation vehicle (TW + PM, 2026-10-26; supersedes "Vehicle: a
  small docs-only PR or part of the F-318 batch (PM and TW choose)"
  above): a separate small docs-only TW defects PR from main ba5cc200,
  not the F-318 batch (which waits for US-173). Scope: the 9
  annotations, append-only, located by content (F-373.md's line is
  l.34 on main; the AE OKs placement in the 7 table rows); the F-373
  AC2 addition; the F-262 XPASS line (QE verbatim); new records F-395,
  F-396, F-397 plus index rows (AE checks F-395/F-396, the Architect
  F-397); the F-394 record and its AC (v) correction only if the QE
  confirms. US-176 story text stays out (own PR). Branch requested
  from the CM; PR number pending.
  UPDATE (CM, 2026-10-26): the TW's branch is docs/F-395-annotations
  at ba5cc200; it overlaps the stale #40 on defects-index.md. PR
  number pending.
  UPDATE (joint r7 results C, Architect; the AE confirmed C,
  2026-10-26): cold-cycle order AGREED as above. Step 1 does not touch
  the graph. Conditions: amixer reads only (contents/get, never
  set/sset/cset); nothing between the boot and the gains read opens a
  PCM or runs pw-*, wpctl or GM ("no GM" means no GM RPC and no web-UI
  action; GM and PW start at boot as normal); the gains read logs the
  fc and fc-out states from the same pw-dump; the elapsed time from
  the boot to the read is recorded.
  UPDATE (TW, CM, 2026-10-26; supersedes "PR number pending" above):
  the docs PR is #60, head 39dd0deaef422bf146f95d6f21310fc060c52035,
  one commit on main ba5cc200, scope as above (US-176 out). Docs-only,
  CI-exempt. 6/7 APPROVE: AE 6405089963, SecSpec 6405090180, UX
  6405090404, Architect 6405094259, QE 6405094450, TW 6405094669
  (author, COI declared). AD REQUEST CHANGES 6405108734
  (/tmp/pr60-ad-verdict-39dd0dea.md, sha256 a6316d4e...0b2a).
  AD H1 (BLOCKING #60; supersedes "AC (c) LIST COMPLETE" and the count
  of 9 above): docs/project/stories/US-163.md AC14, AC16b, AC17/17-B
  and AC19 carry unannotated gains PASS verdicts, so the AC (c) list
  and count are incomplete. The TW is fixing it (batch v2: annotate
  them, fix the count); the QE confirms the full list with a search
  over docs/. The corrected count goes here when the new #60 head
  lands; then the re-checks follow.
  AD H2 (AMPS-ON PRECONDITION; not blocking #60): safety.md rows 8 and
  14, l.64 and l.69 (check 10), and D-070 row 14 on main still treat a
  pw-dump 0 as mute proof. An AE-worded amendment must merge before
  any amps-on session or D-070 use: a gains read counts only if fc and
  fc-out are idle or running before and after it; NOT VERIFIABLE means
  not muted. The safety.md wording goes through the TW (amps-on
  mirroring rule). PM note: TW batch v18 already carries the
  idle-or-running rule (safety.md, D-070 rows 14 and 15); the PM asked
  the AD whether v18 covers H2 or what delta is missing (wording to
  the AE, application to the TW).
  UPDATE (TW, QE, UX, AD, CM, 2026-10-26; supersedes the 6/7 at
  39dd0dea and "The corrected count goes here" above): #60 head
  bc923cc7bd7f3e2e6f5d3df0ac94577877e116d4 (TW batch v2, one docs
  commit on 39dd0dea, 10 files): US-163.md AC14, AC16b, AC17 and AC19
  each get one dated, append-only "NOT VERIFIABLE under F-395" line
  (PASS kept as history, checkboxes unchanged); F-395.md AC (c) count
  13 = 8 lab-note entries, the 4 US-163.md ACs and the F-373 interim
  procedure. AD H1 RESOLVED (AD). 6/7 APPROVE at bc923cc7: Architect
  6405155445, AD 6405155653, QE 6405158563 (replaces the approval H1
  voided), TW 6405158800 (author, COI declared), UX 6405161429;
  SecSpec 6405090180 from 39dd0dea, counted by the CM. AE pending. CI
  run 40246808944: changes, nixos-eval and ci-gate pass,
  test-and-build skipped (docs-only); no failed job. AD condition:
  when #40 lands (it also touches US-163.md) the four added lines must
  survive. Whichever of #59 and #60 merges second is updated against
  main, which voids its approvals and needs fresh re-checks.
  UPDATE (CM, 2026-10-26; supersedes "SecSpec 6405090180 from
  39dd0dea, counted by the CM" and "AE pending" above): #60 MERGED at
  bc923cc7, main a3270b5e07ea338b9372e6793ebde31d98ea622f, 7/7 at
  bc923cc7: SecSpec 6405152735 (diff-only re-approval; 6405090180 not
  counted), Architect 6405155445, AD 6405155653, QE 6405158563, TW
  6405158800, UX 6405161429, AE 6405180306. #60 merged before #59, so
  #59 is the one updated against main (see F-394).
  QE (2026-10-26; the AE agrees): safety.md amps-on row 13 (US-159
  G16, "Tested (AE)") is NOT on the AC (c) list, which stays at 13. It
  states a requirement (added in 28dcba6e without evidence; no G16
  test record in docs/). The only Pi reading with a re-adopted sink,
  AC17-B step (c), is already on the list; the step (a) re-enumeration
  never re-adopted the sink (F-373) and the cold cycles enumerate the
  USBStreamer before PipeWire starts.
  UPDATE AD H2 (AD, AE, PM, 2026-10-26; supersedes "the PM asked the
  AD whether v18 covers H2" above): covered. TW batch v18 covers
  "Gains at boot" and D-070 rows 14 and 15 (the AD withdrew those
  parts). AE ruling v4 (sha256 0090761e, frozen
  /tmp/pm-backlog/ae-ruling-f395-safetymd-gap-v4.md; v3 a719ed5a, v2
  ca8eed3e, v1 554c097a) gives the rest for TW batch v19: items 1, 3
  and 4 (row 8, l.64, the "Gains at boot" FAIL or NOT VERIFIABLE
  sentence), item 5 (row 13 "To be tested (AE; US-159 T65)"), and row
  14 via the planned v160/v161 Row 14 text (item 2 superseded, AE v4).
  New amps-on item 16 (AMPS-ON PRECONDITION LIST); PR #45 check 10
  carries the same rule (#45 entry). H2 closes (AD) when F-318 batch
  v19 merges with items 1, 3-5 as worded, the planned Row 14 text and
  item 16. The AD's #60 verdict rested only on H1 and is now APPROVE.
  UPDATE (AE, 2026-10-26; AC (c)): the cold-boot gains read is done
  (pre-prod one-liner 7 CLOSED). OBSERVE-US172c-4 PASS, boot 60f384a1
  (fresh boot after power loss or hard reset), T+04:58: both nodes
  running before and after the read, the 8 Mult values all 0.000000
  via pw-cli, node counts 1 and 1 (record ffc000b5...f08d). Qualifier:
  an unattributed SSH session at T+00:44, pending the owner's word.
  Scope: PW start state only; GM restart, profile activation and
  unlatch are not covered. It supersedes the "NOT VERIFIABLE" caveat
  on the earlier gains-0 readbacks (cold cycles, AC14, AC17-B, AC19)
  for the PW start state only.
  UPDATE (CM, AE, 2026-10-26): AE ruling, verbatim (via CM,
  2026-10-26): "PASS, fresh boot after power loss or hard reset
  (60f384a1), T+04:58, F-395-verifiable; qualifier: unattributed SSH
  session at T+00:44". Scope: PW start state on this image only; not a
  GM restart, profile activation or unlatch (F-320-E/F-348/F-320-D).
  The frozen amps-on list is untouched. Evidence
  observe4/GAINS-RECORD.txt, sha256 ffc000b5...f08d. GAINS-RECORD-v2
  (observe4b/, sha256 a465a8ad...4528) adds a second read at T+07:47,
  the same result, with links and Props unchanged across 4 dumps and
  the GM gate closed (gate_open=false, has_pending_gains=false,
  venue=null).
- **F-396** Production must never suspend the filter-chain or the
  USBStreamer node (P1 unless the Architect rules otherwise; AE,
  2026-10-26, from the r6b ruling draft section 4): a suspend of the
  USBStreamer sink means a stream stop/start, which is the transient
  risk in safety.md. AE recommendation:
  session.suspend-timeout-seconds = 0 or equivalent for those nodes,
  and verified. It would also make the gains readers authoritative at
  all times (gate2.py still checks the state). Open question to the
  Architect: does the production filter-chain or the USBStreamer sink
  ever suspend on the Pi? F-395 AC (d) step 1 (Pi OBSERVE of the node
  states at idle and right after boot) answers it.
  UPDATE (joint r6b ruling final + Addenda 1-2, 2026-10-26; supersedes
  "P1 unless the Architect rules otherwise" and "Open question to the
  Architect" above): P1 confirmed; AE owner, Architect co-owner.
  Architect answer: the production config already forbids suspend:
  configs/pipewire/30-filter-chain-convolver.conf:213/224 (capture and
  playback props) sets session.suspend-timeout-seconds = 0 and
  node.pause-on-idle = false; 20-usbstreamer.conf:27-28 and
  21-usbstreamer-playback.conf:30-31 do the same;
  configs/pipewire/tests/test_filter_chain_config.py:83/85 guards only
  the convolver props. The config does NOT exclude "never run since
  boot": the convolver chain has no node.always-process (only
  25-loopback-8ch.conf:17 sets it). ACs (Addendum 1 E): verify on the
  Pi (the step 1 OBSERVE records the filter-chain and USBStreamer node
  states); extend the config test guard to 20-usbstreamer.conf and
  21-usbstreamer-playback.conf.
  UPDATE (AE, 2026-10-26, Gate-2 r7): F-396 is now also a safety item,
  still P1. The r7 sandbox showed every node suspending across a
  WirePlumber restart, the USBStreamer stand-in included, despite
  suspend-timeout 0. Added scope: (a) one Pi observation of the
  USBStreamer, convolver and convolver-out states across a WP restart
  (CHANGE, announced, nothing connected); (b) pw-mon over step 6 in
  every Gate-2 --wp-restart Pi run. safety.md needs no new rule,
  because TW batch v17 already treats a WP restart as a USBStreamer
  interruption. Non-blocking: cite F-396 there the next time the batch
  is touched (TW).
  UPDATE (AE, 2026-10-26; "amends r7-results-joint Q3 (AE,
  2026-10-26)"; the joint r7 addendum agrees): (1) Classification:
  F-396 is a SAFETY item now, still P1, as a precaution; this
  supersedes the "only IF the Pi shows the USBStreamer suspending"
  condition in r7-results-joint Q3. (2) safety.md wording: Q3's
  condition stays. Now no new rule: v17 already treats a WP restart as
  a USBStreamer interruption (announce it, amps rule); the TW cites
  F-396 next to "USBStreamer interruption (Section 1)" the next time
  the batch is touched. If the Pi observation shows the real
  USBStreamer node suspending across a WP restart, safety.md names the
  WP restart explicitly as a transient event, citing F-396; the AE
  gives the wording and the TW applies it (F-396 AC4 in the AE's notes
  on the F-395 docs draft).
  PRE-PROD (P2, PO re-plan 2026-10-26): F-396 waits until the core is
  running; no new rounds.
- **US-176** Canary node for the gains readback (AE + Architect;
  durable F-395 fix; joint r6b ruling section 3 + Addendum 1 A +
  Addendum 2 item 1, 2026-10-26): the production filter-chain gets one
  builtin linear canary node with a fixed non-zero conf default,
  connected to no graph output. gate2.py and every readback consumer
  trust the gain values only if the canary reads exactly its default
  in the SAME enum-params read; a mismatch is FAIL "not verifiable".
  Turns reader blindness into a loud failure in every state, and
  closes "idle but never instantiated". The AE confirms CPU and audio
  irrelevance. One shared validator (F-391 rule). ACs (the canary is
  audio-irrelevant only if all hold):
  - the production conf keeps EXPLICIT inputs and outputs arrays, and
    the canary is in neither (no auto-assigned graph port);
  - the node's pw-dump port list is identical before and after the
    change;
  - the canary's input is unconnected (fed silence) and its Add is 0;
  - its value is distinct from 0, 1 and every production gain: 0.123;
  - it is read in the SAME enum-params call as the gains; a mismatch
    means FAIL "not verifiable";
  - a selftest asserts the canary has no port (no input or output port
    in pw-dump) (Addendum 2 item 1);
  - the conf change needs AE review and reaches the Pi as a normal
    DEPLOY.
  PRE-PROD (P2, PO re-plan 2026-10-26): US-176 waits until the core is
  running; no new rounds.
- **F-397** Gain readback consumers show 0 on suspended or never-run
  nodes (P1, Addendum 1 C, raised from backlog: a safety display;
  owner the Architect; joint r6b ruling section 2, 2026-10-26): every
  gain readback consumer (the web-UI config/gain display,
  GraphManager) shows 0 for a suspended or never-run node even when
  the real gain is non-zero, so a node can show "muted" and surprise
  the operator when it resumes. AC: audit all gain readback consumers;
  they must label or refuse readback on nodes that are not idle or
  running. Related: F-395, US-176.
  UX N1 (#60 review, 2026-10-26; non-blocking; for AC 2): a node that
  is not idle or running shows NO gain number at all (no 0, no -inf
  dB, no muted styling), only a distinct state such as "— (node
  suspended: gain unknown)". While the gate is open, that state goes
  in the U8 banner order next to GAIN NODES MISMATCH as "GAIN READBACK
  UNAVAILABLE". The UX specialist reviews the wording in the fix PR.
  Scope addition (Architect, #45 review, 2026-10-26; same as AD L2):
  src/graph-manager/src/gain_integrity.rs reads gain Mult via pw-dump
  every 30 s and trips only on Mult > 1.0. pw-dump prints NaN, -Inf
  and subnormal as 0.000000, NaN > 1.0 is false, and a suspended node
  reads 0 (F-395), so the check cannot see a NaN/Inf Mult or any gain
  on a suspended node. Added to the consumer list (AC audit).
  AC addition (AE, agreed by the Architect, 2026-10-26): any gain
  readback or consumer that sees Mult < 0 on any channel reports FAIL.
  Polarity lives only in the immutable coefficient set (US-174d, sub2
  option (a)), never in runtime gain.
  PRE-PROD (P2, PO re-plan 2026-10-26): F-397 waits until the core is
  running; no new rounds.
- **F-398** Config-supplied names used as path components unchecked
  (SecSpec, LOW, #57 review at 05d306bc, via CM, 2026-10-26): profile
  `identity` -> identities_dir/{name}.yml and venue `coefficients` ->
  os.path.join(output_dir, filename); an absolute or ../ path escapes
  the directory. SecSpec asks for a US-174c/d AC, met before
  coefficients are written on the Pi: coefficients must be a bare
  basename matching ^[A-Za-z0-9_.-]+\.wav$, identity must be a slug,
  and the resolved path must stay under its directory. Same class as
  F-372 and the #55 profile_name item. Not a #57 blocker.
  PRE-PROD (P2, PO re-plan 2026-10-26), except the AC itself: it stays
  an AC on the step that writes coefficients to the Pi (PO).
  Link (SecSpec, 2026-10-26): covered by the US-174d AC (d) the
  Architect adopted (name regex, links resolving inside coeffs/sets/);
  no duplicate row.
- **F-399** Venue runner leaves deployable-named files on a gate
  failure (AD M1, #57 review at 05d306bc, 2026-10-26; fix before
  US-174c/d): run_venue_pipeline writes deployable-named
  combined_*.wav, dirac.wav and delays.yml to --output-dir before the
  gates run, leaves them there when the gates fail, and puts no
  "simulated" marker on them. The old pipeline wrote delays.yml only
  on a pass. Fix: stage the output and promote it only on a pass; mark
  simulated output (simulated: true plus the scenario); a test that a
  failed run leaves no deployable file. Fits the AE's 174d rule "a
  failure keeps the previous filters". Source
  /tmp/pr57-ad-verdict-05d306bc.md (sha256 2d712b71). Not a #57
  blocker.
  Status (CM, 2026-10-26): lane B; worker-4 on
  fix/F-399-venue-runner-cleanup from 6f4ae3d1.
  worker-4 is fence-cleared for runner.py:313-350 (CM, 2026-10-26).
  US-174d AC (worker-4/Architect, verbatim, via CM): "US-174d AC: the
  real-Pi deploy step refuses an output set that has a SIMULATED
  marker present, or a delays.yml whose `simulated` field is absent or
  unparsable, unless explicitly overridden. It copies only the
  top-level expected files and never recurses into output_dir
  (F-399)."
  UPDATE (CM, 2026-10-26): committed as 64d32f3e (worker-4) and pushed
  to fix/F-399-venue-runner-cleanup; parent 6f4ae3d1 (the #57 head);
  the runner.py hunks are within the cleared fence. 1323 passed / 0
  failed / 1 skipped of 1324; 18 new tests; 13/13 mutations red. The
  PR opens once #57 merges (stacked branch, strict main). F-363 passed
  in that run with the cause unchecked: NOT fixed until the QE
  confirms (see F-363).
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
  #56 final head 684da11a (CM, 2026-10-25): commit 3 e9a96c60 plus
  the merge of main dfdbbbd6; pushed, body v3, Rule 13 requested
  from all 7; CI run 40236821737. Rule 13 at 684da11a: APPROVED
  UX (no concerns: no web UI code reads driver records, no shipped
  speaker or venue config references the 36 changed records), AD
  (does not cover CI; lapses on a head move), TW. Later (CM,
  2026-10-25): 6/7 APPROVED and posted verbatim: QE (its required
  body edit applied by the CM, head unchanged), Architect,
  SecSpec, UX, AD, TW. AE pending; CI 40236821737 running.
  AE APPROVE posted (CM, 2026-10-25): 7/7 at 684da11a; merge on CI
  40236821737 green (standing merge consent). AE: purifi is covered
  (qts 0.23 -> 0.26, computed 0.2589; test_all_real_drivers_pass green
  at 684da11a in the AE's own run).
  On merge (TW): close docs/project/defects/F-363.md (main says
  "open"; its AC2 says "sorted sample") and record the
  resolution: all records checked, exemption table, plausibility
  bounds.
  #56 MERGED (CM, 2026-10-25; standing consent): merge commit
  1c36889f446d79a74a4a69750e48281be84515c5, main = 1c36889f; 7/7 at
  684da11a, CI 40236821737 green (1210 passed / 0 failed / 1 skipped),
  QE body edit in. Open on merge: the TW closes
  docs/project/defects/F-363.md (above). QE backlog one-liner (P2/P3),
  recorded under F-388 (the #56 body points it there): "any future
  consumer of driver-record T/S values must exclude ts_consistency:
  unverifiable records". QE non-blocking: N1 F-388 adds an xmax test
  once a consumer appears (= F-388 AC-e); N2 optional assert that
  quote-None notes start with "F-363: unverifiable" (as above). CM
  observation sent to the QE: the E2E local-demo step shows 1 xpassed
  (QE to classify; F-272 removed xfails).
  F-262 one-liner (QE, from #56, via CM, 2026-10-25; supersedes "QE to
  classify" above; record docs/project/defects/F-262.md on main):
  "XPASS observed in CI 40236821737 (main candidate, #56) — evidence
  for non-determinism; F-262 closure must convert to strict or
  remove." The TW carries it into F-262.md with the next defects docs
  PR. PR #58 (docs-only, CI-exempt; CM, 2026-10-25): the TW's batch
  closing F-363 and adding F-388 (/tmp/tw-defects-f363-f388-v1/,
  MANIFEST 9e22c930), head 51cb3fa0; review open with all 7. It sets
  F-363.md resolved (Resolution: all records checked, exemption table,
  plausibility bounds), adds F-388.md (AE M1/M2 verbatim plus
  AC-b/c/e), updates the defects-index.md F-363 row, adds an F-388 row
  and removes the status.md Open Blockers F-363 row. On merge, the
  F-388 line "No defects/F-388.md record on main yet" and the TW close
  item above are superseded.
  #58 at 51cb3fa0 (CM, 2026-10-25): APPROVE SecSpec, UX, AD (no
  findings; lapses on head move), Architect, TW (declared authorship).
  QE CHANGES REQUESTED, R1: 11 marked records, not 8 (8 exemptions
  plus 3 unsourced `unverifiable`). AE pending. The TW prepares v2;
  then a diff-only re-check by all 7.
  UPDATE (CM, 2026-10-25; supersedes "AE pending"): AE APPROVED
  51cb3fa0 (comment 6404437370, verdict 3404e3d0); 6 APPROVE plus the
  QE's CHANGES REQUESTED. TW v2 (MANIFEST c8a6e156) has R1, N1 and N2
  but not yet F-388 AC-f; the CM holds it until the TW folds AC-f in,
  so the 7 re-check only once.
  #58 v2 at ff586707 (TW MANIFEST 000c414b, CM 2026-10-25; supersedes
  c8a6e156, never committed): the QE's R1 plus N1/N2, the AE's
  exemption-sentence fix, and F-388 AC-f as F-388.md AC 6 (AE text
  verbatim; UX "same message at every entry point" credited to UX).
  Diff-only re-check out to all 7. The QE's F-262 XPASS line stays OUT
  of #58 (TW, scope as reviewed); queued for the TW's next defects
  docs PR.
  #58 MERGED (CM, 2026-10-25): merge commit dfb81cd7 at 22:51:16Z
  (head ff586707); it closes F-363 (R1: 11 marked records) and adds
  F-388 with AC 6 = AC-f. Re-APPROVED at ff586707 (team-lead record):
  UX, SecSpec, Architect, AE, AD; the TW and QE verdicts are covered
  by the CM's 7/7 merge check (comment ids with the CM). The #56 item
  "Open on merge: the TW closes F-363.md" is done. Still queued for
  the TW's next defects docs PR: the QE's F-262 XPASS line.
  #58 TALLY (CM, team-lead, 2026-10-25; supersedes "covered by the
  CM's 7/7 merge check"): 7/7 at ff586707, the TW and QE included, all
  posted before the merge. AE P2 proposal (2026-10-25; ID pending,
  F-395 free): test_mute_silences_level_bridge passes vacuously,
  because it never checks there was signal before the mute; reconcile
  the F-270 and F-262 records (PM asked the AE which records: F-270.md
  on main is the resolved Transfer Function tab defect).
  UPDATE (AE, QE, 2026-10-25; supersedes "ID pending, F-395 free"):
  folded into F-394 as AC (vi); the F-270 reference is the wrong
  citation in the xfail at test_mute_e2e.py:90, reconciled under F-394
  AC (v). F-395 is not allocated.
  #56 backlog (AD, TW, 2026-10-25): AD L1 = TW (3), P3: the CLI
  scripts/drivers/validate_drivers.py and pytest need one shared
  exemption/bounds source (the CLI flags the 8 exempted records
  and skips the bounds); or a CLI help/driver-docs note. AD L2:
  check datasheet_url against the model on the Parts
  Express-sourced records (tang-band's pointed to another driver).
  TW (4), P3 docs debt: the docs/project/test-strategy.md:51
  inventory lacks test_driver_validation.py; the table is stale.
  AD M1/M2: see F-388 (AC-a to AC-e). AD L2 detail: the tang-band
  record pointed to the W2-2360S.
  #56 backlog (Architect, QE, via CM, 2026-10-25): Architect N1 the
  allowlist value becomes a list of {field, value, quote} if a
  record needs two fields; N2 extend the reference test if a new
  way of referencing drivers is added; N3 a non-numeric Q gives a
  TypeError, not a readable violation. QE N2 (optional): assert
  that a quote-None record's notes start with "F-363:
  unverifiable".
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
    MERGED into F-388 M1 (AE, 2026-10-25); F-388 is the one record.
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
  - Status (CM, 2026-10-26): F-363 PASSED in the F-399 run at
    64d32f3e, cause unchecked. NOT fixed until the QE confirms.
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
  Added (CM, 2026-10-26): the room-correction suite took 548 s on CI
  ARM, over the 300 s line (run 40299659873, #57 at 599ea52a). Not a
  #57 blocker (QE).
- US-159 G16 with AE amendments a-e and architect additions 1-3; test
  T65 (not T62). Medium; re-rate on (i) volume after replug, (ii) relink
  with gate_open true. Match by node and direction.
  T65 criterion (QE, T65 owner; AE endorses, 2026-10-26), verbatim:
  "every gains read in T65 follows the F-395 rule: values from pw-cli
  enum-params only, the fc and fc-out node state logged immediately
  before and after each read and idle or running; NOT VERIFIABLE is
  never a pass." AE addition (via QE): T65 case (3), where a
  USBStreamer replug leaves the gate Closed, also logs the fc, fc-out
  and USBStreamer node states before, across and after the replug
  (F-396 evidence). Until T65 passes, safety.md amps-on row 13 reads
  "To be tested (AE; US-159 T65)" (AE ruling v4 item 5).
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

- CLAUDE.md "Session 15 focus" list is stale (TW flag 3 on #45; AD M1,
  Architect, UX agree; 2026-10-26): it ranks F-314 safety first, which
  contradicts the owner's 2026-10-26 priority (DJ set and room
  correction first). Drop the list or point to status.md, at the next
  CLAUDE.md touch (the owner's file). TW flag 4 (optional,
  non-blocking): an F-395 pointer on the Pi 5 gains bullet.
- CLAUDE.md "two reconciler bugs" (US-059, Pi 4 era) have no backlog
  record; the Architect confirms whether GM DJ mode on the Pi 5 still
  hits them (see DJ PLAYBACK PATH). Owner of the check: Architect.
  ANSWERED (Architect, 2026-10-26): stale; see the DJ PLAYBACK PATH
  update at the top (8ef778e3, 5fbd5f75). TW backlog, no F-number: the
  CLAUDE.md "Current Mission" line "Two reconciler bugs block
  automated routing — manual pw-link used for GM-12" is stale; drop it
  or point it at 8ef778e3/5fbd5f75, and mark the GM-12 lab note's
  Finding 10 ("Open") resolved. #45 rewrites that CLAUDE.md paragraph
  anyway; if it merges first, check whether the line is already gone.
## P3

- **/protection status reads the wrong marker** (F-c; worker-5, AE
  ruling via team-lead, 2026-10-26; P3, owner UX; cross-ref F-390):
  thermal_routes reads active-profile.txt from the speakers dir, but
  activation writes active-profile.yml to PI4AUDIO_STATE_DIR
  (~/.config/pi4audio). Only the read-only GET /protection view is
  affected (thermal_routes.py:145-157): it always shows "no channels /
  has_thermal false". Misleading, but no gain changes: profile
  activation configures the limiter directly
  (_configure_thermal_protection, speaker_routes.py step 7) and never
  reads the marker. AE note: app.state.active_speaker_profile is never
  set anywhere in app/.
- **CLAUDE.md IEM-path sentence outdated** (Architect, docs drift,
  2026-10-26; owner's file, flagged to team-lead for the owner and to
  the TW; nobody else edits it): CLAUDE.md says "IEM signal path:
  Reaper → direct PipeWire link → USBStreamer ch 6-7 (bypasses
  convolver entirely)". D-063 and link_audit.rs protect all 8 ports;
  HP and IEM go through the convolver on Dirac. The same file's
  channel table puts the singer IEM on ch 7-8.
  Caveat (TW, 2026-10-26): "ch 6-7" there is probably 0-based
  (AUX6/AUX7 = 1-based ch 7-8), so only the bypass claim may be wrong.
  US-115.md:7 records the IEM routing conflict as an open OWNER
  decision (US-115 AC#4). TW one-liner, verbatim: "TW: IEM path drift
  in rt-audio-stack.md (90/105/707-708) and design-rationale.md
  (48/326), fix after the owner's IEM-routing ruling (US-115 AC#4 /
  CLAUDE.md)". Fix all docs in one pass with CLAUDE.md after the owner
  rules; each fix states AUX6-7 = ch 7-8. Historical docs (lab notes,
  US-028/US-030/TP-001, D-011, assumption-register:76) stay as they
  are.
- **Stray streams reach the PA once the convolver is the default
  sink** (AE, 2026-10-26; P3, owners UX + Architect; not a safety
  item): once US-174d makes the convolver the default sink, any stray
  stream (a browser, a notification sound, pw-play) plays through the
  PA during a gig, gain-staged and D-031-protected. Decide whether the
  row-18 WirePlumber hook should refuse auto-targets for ALL Stream/*
  nodes, leaving only GM-made links.
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
  Details (worker-3, via CM, 2026-10-25; corrects ~430): 6
  selftest builds on the linux-builder (20:56Z-21:31:58Z); 3 `nix
  store delete` runs on their own w3-gate2-selftest outputs only
  (339.1 + 92.7 + 92.2 MiB, ~524 MiB total); no GC. Deviation
  recorded and closed (CM). Later (CM): disk 2.6 GiB and falling;
  the hold stays. Later (CM): 2.5 GiB, still falling. Later (CM):
  2.3 GiB.
  Later (team-lead, CM, 2026-10-25): 5.3 GiB free; the US-173 Gate-2
  selftest is no longer disk-held (CM cleared worker-3).
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
  #54 updated to main 1c36889f (CM, 2026-10-25; after #56 merged):
  head 46343238; all 7 asked for a FULL re-review (bundle
  /tmp/pr54-review-46343238/); CI 40240718064 running. Merge order
  unchanged: #54, then #55.
  #54 Rule 13 at 46343238 (CM, 2026-10-25): 6 verdicts posted: UX (no
  concerns), SecSpec, TW, AE, Architect, AD (the CM posts the AD text
  once it has it as a file). AD APPROVE does not cover CI and lapses
  on a head move. AD M1 MERGE GATE: CI 40240718064 builds no checks.*
  (F-380), so "green at the merged head" needs one check run at
  46343238 showing 0 failed / 1211 collected; the check evidence so
  far is from 320c3ae6, before #56, so #56's new driver tests never
  ran in the check sandbox. QE on HOLD for H1/H2: H1 scratch run
  (branch scratch/pr54-h1-rc-check 3a95ae77, run 40241169781); H2 body
  text, the TW drafting. AD L1 + QE: F-393 (not fixed in #54).
  #54 update (CM, 2026-10-25): AD verdict posted
  (/tmp/pr54-ad-verdict-46343238.md), 6/7 on the PR; QE on HOLD for
  H1/H2. CM local eval: drvPath
  /nix/store/7zah6n80zm3xri1xhy76hz622i3q2grq-test-room-correction.drv;
  AD M1 needs the H1 run (40241169781) to match it. TW body v2 ready
  (182097d7), posted after H1.
  #54 H1 MET (CM, 2026-10-25): run 40241169781 on aarch64-linux
  succeeded; drvPath 7zah6n80, identical to the local eval; 1211
  collected, 1210 passed / 1 skipped / 0 failed; all 14
  TestRealDriverRecords PASSED; the skip is test_mic_sim_with_cal_file
  (not a driver test). The AD's M1 merge gate is met by the same
  evidence. Scratch branch deleted. Body v3 posted (TW v2 with the H1
  row filled in); the QE does the diff-only body check. Open: the QE
  verdict and CI 40240718064 at 46343238 (running).
  UPDATE (CM, 2026-10-25): the AD verified H1 run 40241169781 itself;
  M1 confirmed met. CI 40240718064 at 46343238 FAILED one E2E test:
  test_audio_flow.py::TestLevelBridge::test_level_bridge_sw_has_signal,
  all 8 channels silent (log /tmp/ci54-40240718064-failed.log). The
  QE, AE and Architect are ruling; a flake ruling needs an F-ID (next
  free F-394). AD: the flake.nix diff does not explain it; it needs a
  root cause or a recorded defect, not just a green rerun. After #58
  merged, #54 moved to c32f416f (update-branch with main dfb81cd7;
  diff cmp-identical); diff-only re-check out to all 7; CI
  40242139498. Re-APPROVED at c32f416f: UX (own cmp), AD (not covering
  CI) = 2/7.
  UPDATE (CM, team-lead, 2026-10-25; supersedes "2/7"): 6/7 posted at
  c32f416f (SecSpec, UX, TW, AD, Architect, AE); QE pending; CI
  test-and-build running. E2E failure views: the Architect and AE say
  #54 did not cause it (checks-only change; the E2E closure is
  unchanged); both suspect a race: the test reads one level line right
  after ensure_dj_mode, no settle or retry. The AE accepts one
  explicit rerun, a defect record either way, and a fix that polls for
  up to ~5 s. QE ruling and the ID pending (F-394 free; PM asked the
  QE: new F-394 or an F-262 update, because F-262.md "Partial
  Resolution (D-249)" says this test "now passes consistently" and its
  xfail was removed).
  UPDATE (CM, 2026-10-25; supersedes "6/7", "QE pending" and "ID
  pending"): 7/7 posted at c32f416f, the QE approving, conditional on
  CI 40242139498 (test-and-build running). The E2E failure is F-394
  (High; see the F-394 entry for the rules and the fail-again plan;
  the race hypothesis is withdrawn). CM drvPath proof (posted): the
  test-e2e drvPath differs between dfb81cd7 and c32f416f only via
  LOCAL_DEMO_REPO_DIR="${self}"; all input derivations are identical.
  #54 MERGED (CM, standing owner permission, 2026-10-26): merge commit
  ba5cc200 at 23:33:47Z; 7/7 at c32f416f; CI 40242139498 green. The
  F-394 test was SKIPPED and nothing was red, so the run is green
  under the QE rule; per the QE it most likely means the DJ group was
  skipped (F-394), so the merge says nothing about DJ mode.
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
  UPDATE (CM, TW, 2026-10-26): #45 is still OPEN at 76b61347, stale
  since 2026-10-24. #45 stays alive (PM record): the TW is preparing
  an F-395 check-10 safety.md batch for it (AE wording; see "#45 gain
  read method" below), and #44 still depends on it. It needs an update
  from main (#60 merged) and a full Rule 13 round at its new head.
  UPDATE (CM, PO, 2026-10-26): #45 has the TW's F-395 check-10 commit
  8cba3522 on 76b61347 (one row, AE wording 17a79d37; the body
  addendum notes the safety.md conflict at revival). The AE is
  confirming the wording; once the AE OKs it, #45 meets "check 10
  carries the F-395 rule" (#45 gain read method UPDATE below). PO
  RULING: revive #45 right after #59 merges, in parallel with #57; #45
  goes into safety.md ahead of F-318 v19, and the F-318 batch rebases
  onto it (the TW resolves the conflict once, there). No hold. Revival
  = update from main, the TW's safety.md conflict resolution, a full
  Rule 13 round at the new head.
  UPDATE (CM, 2026-10-26): the AE OK'd the check-10 wording at
  8cba3522 (diff byte-identical to the AE's 17a79d37 text, no
  corrections; not a Rule 13 verdict), so #45 meets "check 10 carries
  the F-395 rule". The CM passed the PO ruling to the TW. A dry-run
  merge of main a3270b5e into 8cba3522 conflicts in 3 files:
  .claude/memories/_index.md, CLAUDE.md (2 hunks) and safety.md; the
  TW prepares the resolved files (/tmp/pr45-merge-prep-8cba3522). #59
  has merged (main f01e6647), so the CM now makes the merge commit and
  publishes the Rule 13 bundle. CLAUDE.md is the owner's file: the
  standing merge consent covers PR changes to it (team-lead ruling,
  #50); the post-merge report names the change.
  UPDATE (CM, PO, 2026-10-26): PARKED (PRE-PROD, PO re-plan). The CM
  had already made and pushed the merge commit at 08:46, before the
  re-plan arrived: b7be7ea1 = merge of main f01e6647 with the TW
  resolution d7fc49a4 (branch commit only, nothing on main). The PO's
  "no merge commit unless the resolution is complete" came too late
  for that step; the work is preserved. The Rule 13 round (bundle
  /tmp/pr45-review-b7be7ea1/, SUMS ea46b36d) is PAUSED; the CM does
  not post #45 verdicts. Verdicts that arrived before the pause
  (record only, not a merge tally; #45 is re-reviewed on revival, AE
  one-liner 1): QE APPROVE (conditional on CI 40294670076), UX
  APPROVE, AD APPROVE (/tmp/pr45-ad-verdict-b7be7ea1.md, sha256
  28729188...). CI 40294670076 is not acted on.
  #45 review one-liners (2026-10-26; non-blocking, pre-prod, for the
  revival or the next safety.md batch): UX N1: venue-setup step 6 /
  safety.md Rule 8 say "restrict port 8080 to that device" with no
  procedure; give only the isolated-network option until a documented
  procedure exists (F-037). UX N2: after Rule 5-7 recovery the MUTE
  indicator stays active with stale pre-mute gains and UNMUTE is
  forbidden, so the operator can't clear it; document the expected
  status-bar state now and clear the pre-mute state on gate close
  (F-320-F / US-159). UX N3: move the check #10 procedure out of its
  table cell into a numbered block below the table, like commands
  #3-#8 (TW, wording unchanged). AD L1: check #10 "all Add values the
  same" becomes "each Add exactly 0.000000" (a non-zero Add is a DC
  offset into the amps). AD L3 (code comment, low):
  nix/nixos/rt-tuning.nix:24 "hardware watchdog provides a backstop"
  contradicts options.nix "stays disabled (O-24)". QE: see amps-on row
  13.
  UPDATE (CM, 2026-10-26; corrects the verdict list in the PARKED
  update above): all 7 verdicts at b7be7ea1 came in before the stop,
  all APPROVE: QE, SecSpec, UX, Architect, AE (with an addendum), AD
  and TW. The CM archived them UNPOSTED in
  /tmp/pr45-verdicts-b7be7ea1/; the UX file is a condensation, so the
  CM asks the UX for the full text again at revival. Revival needs
  another main merge anyway; the TW's cosmetic note gets fixed then:
  the merge commit's subject is ~1100 characters and should become the
  body. More pre-prod one-liners: SecSpec LOW: curl -k -> --cacert
  after F-037. AE addendum: the pw-dump vs pw-cli readback
  contradiction is bound to v19.
  SecSpec (2026-10-26, #45 verdict, review paused), verbatim: "The
  documented gate-close recovery uses `curl -k`. When F-037 auth
  lands, switch to `--cacert`/a pinned fingerprint, so credentials are
  never sent over an unverified connection." Ties to F-037.
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
  UPDATE (AE ruling v4, AD H2, 2026-10-26; reopens the CLOSED above
  for one point): before #45 merges, its check 10 carries the F-395
  rule: gains read via `pw-cli enum-params`, exactly 0.000000; the fc
  and fc-out node states logged before and after the read and idle or
  running; NOT VERIFIABLE means not muted, amps stay off; no "gains
  read 0" or "pw-dump" wording. TW and CM align #45; the TW raises it
  once #60 is done.
- **F-386** Gain values read from pw-dump (AE, P2, AE-owned review;
  2026-10-25). AE ruling: gain VALUES are read only with `pw-cli
  enum-params <pi4audio-convolver id> Props`; pw-dump is for
  structure only (node counts and names), because it prints
  NaN/-Inf/subnormal as 0.000000. Review the remaining pw-dump value
  readers outside the F-318 batch, e.g. safety.md's audit polling
  "via pw-dump every 30 s" and audio_mute.py. Node discovery via
  pw-dump is fine; no value check may trust pw-dump for
  NaN/-Inf/subnormal.
  More readers (via CM, 2026-10-25): (1) worker-3 side finding: GM
  gain_integrity.rs and the web UI read gains from pw-dump, which
  may also be STALE (a sandbox set-param did not show in pw-dump);
  only an enum-params reader is shown live, once the set-param
  case passes. (2) safety.md:69-71 on the US-173 branch says
  pw-dump, not pw-cli, for gains, contradicting the AE's
  enum-params rule; the AE is ruling and the TW fixes it.
  (3) Gate-2 r3 (2026-10-25): a sandbox runtime set showed in neither
  enum-params nor pw-dump; the joint AE + Architect ruling and the r4
  T1/T2 matrix are under US-173 (Gate-2). Until T2 shows H2 false and
  the Pi -0.0 check passes, no reader counts as live proof.
  PRE-PROD (P2, PO re-plan 2026-10-26): F-386 waits until the core is
  running; no new rounds.
- Pi -0.0 gain readback check (joint AE + Architect ruling, point 3,
  2026-10-25): a small separate CHANGE session, nothing connected,
  after the sandbox (r4 T2) result, with the Pi back up first. Set ONE
  gain_*:Mult to -0.0, read it (expect -0.000000), restore 0.0 and
  read it (expect 0.000000). No gain increase, so S-012 doesn't apply,
  and no PW restart. If the Pi doesn't print -0.000000, enum-params is
  blind to runtime sets on the Pi: an AE finding that blocks B1 as
  live proof.
  Fallback (Architect + AE addendum, 2026-10-25): if the sandbox (b6)
  shows that the T2 (in-daemon) variant normalises -0.0 to 0, the -0.0
  probe can't be used; the Pi step then uses gain_*:Mult 0.001. That
  is a gain increase, so standing rule S-012 needs the owner's OK, and
  the AE first explains it to the owner in plain language. Until then
  B1 stays "boot defaults verified; live readback unproven".
- #36, #40: no Rule 13 review; owner direction needed (#40 IDs clash).
- chore/backlog (this file): no PR yet; docs-only.
