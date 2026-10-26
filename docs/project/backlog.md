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
  UPDATE (CM, 2026-10-26, after v188): backlog v188 pushed as
  80ee6421. #57: the AC7 fix is ACCEPTED (Architect, AE): an injected
  +6 dB Q4 380 Hz feature in the right path, premise asserts, the 1.0
  dB margin and band kept; the AE's ±1/6-oct idea is withdrawn, the
  joint fix is the Architect's plus 3 refinements; with worker-4. The
  QE reviews the test change and the new head needs a fresh 7/7.
  US-174d pushed at 1601c4dd; US-173 at 2a180966. US-172 tryboot is
  ARMED, waiting for the owner at HDMI. Mac disk: 1.7 GB free and
  falling; no nix for anyone.
  UPDATE (CM, 2026-10-26, after v189): backlog v189 pushed as
  8345c0de. US-173 pushed at fe6b6974 (venue ch4 dirac -> zero.wav).
  Mac disk: 0.95 GB free (1.7 GB about 30 min earlier); the growth is
  mostly Claude session transcripts (including non-mugge projects) and
  macOS swap (2.0 GB in /var/vm), not nix. Escalated to team-lead. No
  nix for anyone.
  UPDATE (CM, PM, 2026-10-26, after v190): backlog v190 pushed as
  dd197656. Mac disk: 610 MB free. The PM deleted 166 old
  /tmp/pm-backlog versions (v1-v180) that the CM verified
  byte-identical to committed chore/backlog blobs (PM re-checked by
  hash-object: same 166); about 25 MB freed. Kept: v19, v44, v45, v47,
  v108, v114, v115, v132 (not in git under that content), all build
  scripts, and v181 onward. No nix for anyone.
  UPDATE (CM, team-lead, 2026-10-26, after v191): the Mac disk hit 0
  bytes, then recovered to 2.1 GiB. Team-lead put the team in QUIET
  MODE (only unblocking messages; no new large /tmp files or copies;
  park big-output work; nobody deletes outside their own verified
  files); the PM relayed it to all advisors. The PM's files were
  checked intact (v191 sha1 8daa407e unchanged). Quiet mode is now
  LIFTED for messages and backlog commits; nix and large /tmp writes
  stay held. Backlog v191 pushed as aba4e31c.
  PROCESS NOTE (owner directive, 2026-10-26, verbatim via team-lead):
  "I don't think change manager should ever be busy for so long. They
  have a coordination task. Things that need work should go to
  workers." Context: a 33-min CM CI-polling call delayed the US-172 go
  while the owner was at the HDMI screen. Rule: CM tool calls stay
  short (git, pushes, grants, relays); CI watching, builds, tests,
  investigations and cleanup go to workers, run detached.
  UPDATE (CM, team-lead, 2026-10-26, after v192): quiet mode came back
  while the disk fell, then LIFTED again for messages and backlog;
  v192 pushed as 1083e373. Standing disk rules: the nix hold stays
  while the Mac has less than 3 GB free, and nobody touches the
  linux-builder. Below 1.5 GB, quiet mode comes back automatically and
  the qcow2 size and df /nix are sampled. #57 is 7/7 at e731820c (see
  US-174); its merge waits on CI and the QE's C1/C2.
  UPDATE (CM, 2026-10-26, after v193/v194): backlog v193 pushed as
  e17d1042, v194 as eedcf9b9. US-172 run 3: the tryboot boot HUNG
  again (see US-172). #63 (US-173, draft) CI green at 0b614d1b; Rule
  13 0/7 (see US-173).
  UPDATE (CM, 2026-10-26, after v195): backlog v195 pushed as
  1734c587. US-172 run 3 disarmed and verified at 11:03:47Z, session
  released, Pi lock free; the normal boot applies no dtoverlays
  (likely F-367 cause, see US-172). F-400 allocated (conf.d fragments
  hash-named; worker-3 on #63).
  UPDATE (CM, 2026-10-26, after v196): backlog v196 pushed as
  238ae9d4. US-172: the Architect's RUN-4 v2 supersedes R4-0-first;
  worker-2 builds the kit off-Pi (see US-172).
  UPDATE (CM, 2026-10-26, after v197): backlog v197 pushed as
  f5ee0097. US-172: run-4 fallback corrected to R4-1b (see US-172).
  #63: F-400 pushed at ff4d6c7e, CI pending.
  UPDATE (CM, 2026-10-26, after v198): backlog v198 pushed as
  b0fc8025. #63 CI run 40312806198 at ff4d6c7e in progress; QE F-400
  conditions C1-C3 (see US-173). US-172: Architect's run-4 HDMI
  expectation (see US-172).
  UPDATE (CM, 2026-10-26, after v199): backlog v199 pushed as
  34530467. #63 head 9b1aa8a1, CI restarted (see US-173). #57 CI
  40310308638 still in test-and-build (started 10:49:50Z, about 22 min
  at the CM's check, within normal range).
  UPDATE (CM, 2026-10-26, after v200): backlog v200 pushed as
  2ca434b8. #57 CI still in progress. F-401 allocated (whole test
  module silently skipped). 174d: web-UI fallback at 2ec2b004 HELD;
  `_deploy_sync` ruling pending with the Architect. #63: AE condition
  (1) MET, checklist bdef865d.
  UPDATE (CM, 2026-10-26, after v201): backlog v201 pushed as
  20f92e4d. US-178 allocated (measurement flow deploys via 174d sets;
  PO: P1, after US-174d, above US-177). 174d: `_deploy_sync` DISABLED
  (see US-174). F-401 WITHDRAWN as a duplicate of F-362 (PM).
  UPDATE (CM, 2026-10-26, after v202): backlog v202 pushed as
  d3279dc7. F-362 sweep (QE (a)+(b)) assigned to worker-1 on
  defect/F-362-skip-guards from origin/main 5f3af36a. US-178 vs
  US-174e: PO option (A), US-178 = flow/plumbing, 174e = venue
  workflow UI on top.
  UPDATE (CM, 2026-10-26, after v203): backlog v203 pushed as
  bd642dc5. PO FINAL: option (C), US-178 = 174e slice 1 (supersedes
  option (A)). F-362 is PR #64 (draft, AC4 mutation head 03b2ec0f).
  174d: deploy_filters and deploy_pw_config REMOVED (Architect).
  UPDATE (CM, 2026-10-26, after v204): backlog v204 pushed as
  6b66902d. F-362 / PR #64 final head 0d9e52e7 pushed, CI run
  40314977506 (CM report, relayed by team-lead). US-172: run-4 kit
  delivered, under Architect + QE review, no grant yet.
  UPDATE (CM, 2026-10-26, after v205): backlog v205 pushed as
  02f1683e. US-172: the run-4 kit is NOT acceptable as delivered
  (Architect); worker-2 rebuilds it to RUN-4 v2. 174d code-complete,
  HELD locally at 5ffb319c. #57 CI green (40310308638); merge waits on
  QE C1/C2. #64: AC4 MET. Mac disk 2.1 -> 6.8 GB free, cause unknown
  (CM asked team-lead); the disk hold stays until settled.
  UPDATE (CM, 2026-10-26, after v206): backlog v206 pushed as
  b448d0ee. 174d HELD at b496250b. #57: QE C1 MET, only C2 (PR body)
  open. Disk: team-lead does not know the cause either and has asked
  the owner (non-blocking); the disk hold stays.
  UPDATE (CM, 2026-10-26, after v207): backlog v207 pushed as
  8011e804. #57 (US-174) MERGED at e731820c; main is 1e1495ab. #61
  update-branched to 781b638a (content identical to 247478d5); its
  approvals are void and 7 re-approvals are requested via team-lead.
  Merge order next: #62, then the F-399 PR, then 174d merges main.
  UPDATE (CM, 2026-10-26, after v208): backlog v208 pushed as
  36ed34a7. #61 MERGED at 781b638a with 7/7; main is c318f404. #62
  update-branched to 62b55b29 (content identical to 20903a04); its
  approvals are void and 7 re-approvals are requested via team-lead.
  Next: the F-399 PR, then 174d.
  UPDATE (CM, 2026-10-26, after v210): backlog v210 pushed as
  8254349c. #62 MERGED at 62b55b29 with 7/7 (CI 40316612538 green);
  main is 289f1a72. F-399 pushed at ec845553; worker-4 merges main and
  drafts the PR body, then the PR opens. Open placement rulings: AE on
  F-399 nit 2 (absolute vs difference premise); Architect on
  w4/d031-shared at 83620c87 (own PR or folded into 174d).
  UPDATE (CM, 2026-10-26, after v211): backlog v211 pushed as
  de2200a1. F-399 pushed at 2fb05039 (merges main 289f1a72 clean; 3
  files, +443/-27); worker-4 adds the AE's (a0) commit and body draft
  2, then the CM opens the PR. Both placement rulings are in (see
  F-399 and US-174d).
  UPDATE (CM, 2026-10-26, after v212): backlog v212 pushed as
  e41e9416. F-399 open as PR #65 at final head 13995e15; CI run
  40317165021 in progress (code, not CI-exempt); 7 reviews requested
  via team-lead. Next: 174d, after #65 merges.
  UPDATE (CM, 2026-10-26, after v213): backlog v213 pushed as
  9dc9cd7f. #65 at 13995e15: UX APPROVE, AD APPROVE, QE APPROVED WITH
  CONDITIONS (C1 CI green, C2 mutation evidence); CI run 40317165021
  still pending. worker-4 is on a read-only F-262 diagnosis while #65
  waits (team-lead's suggestion; PO told, may redirect); no edits, no
  fence overlap.
  UPDATE (CM, 2026-10-26, after v214): backlog v214 pushed as
  9dba5b06. #65: all 7 verdicts posted at 13995e15, all depending on
  CI run 40317165021; QE C2 is a body edit with worker-4 (head stays
  13995e15). #63 review bundle published, tally 0/7, CI 40313123653
  running. Mac disk 6.7 -> 4.9 GB free: the owner's own darwin-rebuild
  of the Mac system config, not team work (team-lead informed); the
  nix hold stands.
  CORRECTION (team-lead, 2026-10-26): the 6.7 -> 4.9 GB drop comes
  from a darwin-rebuild that no mugge worker started; the CM PRESUMES
  it is the owner's. Not confirmed by the owner. UPDATE (CM, after
  v215): backlog v215 pushed as f0c18bf7; df 4.8 GB.
  UPDATE (CM, 2026-10-26, after v216): backlog v216 pushed as
  656d0af3. #63: CI run 40313123653 SUCCESS on all jobs at 9b1aa8a1;
  SecSpec APPROVE, UX APPROVE WITH 2 MERGE CONDITIONS, QE CHANGES
  REQUESTED (B1-B4; see US-173). Two CI findings with the QE for a
  ruling. worker-3 has the conditions; requests OBSERVE for the
  screenshot and merges main later.
  UPDATE (CM, 2026-10-26, after v217): backlog v217 pushed as
  6394e034; df 4.8 GB. #63: all 7 verdicts posted at 9b1aa8a1 (4
  APPROVE with conditions, AD REQUEST CHANGES, AE NOT YET, QE CHANGES
  REQUESTED). worker-3 pushed 2a688a94 (UX C1 as AC12, plus N1); new
  head, so every approval needs a diff-only re-check at the final
  head. Consolidated rework with worker-3 (see US-173).
  UPDATE (CM, 2026-10-26, after v218): backlog v218 pushed as
  9632c15f; df 4.8 GB. #63 QE B3 build: worker-run, CM-cleared and
  published (see US-173). #63 AC11(c): the Architect sent a FINAL
  text; NOT settled until the AE confirms it. #57: QE item closed.
  UPDATE (CM, 2026-10-26, after v219): backlog v219 pushed as
  3aa96bff; df 4.7 GB. #63 AC11(c) SETTLED (AE confirmed the
  Architect's FINAL text; relayed verbatim to worker-3); this
  supersedes the "NOT settled" above. B3 is a team-lead ruling.
  UPDATE (CM, 2026-10-26, after v220): backlog v220 pushed as
  7b13cd2b; df 4.7 GB. #63 pushed at a66576eb (AC11(c) final text; PR
  body replaced with worker-3's full-scope draft). Next: worker-3's
  WAVs + SHA256SUMS, AC5 wording, TW Q1-Q4 answers; then the TW batch,
  main merge, bundle and re-checks.
  UPDATE (CM, 2026-10-26, after v221): backlog v221 pushed as
  7ec44e9e; df 4.8 GB. F-262 CONFIRMED a real bug (worker-4 read-only
  diagnosis; QE confirmed); PO: P1 in the room lane, worker-4 now,
  before 174d; HARD GATE on US-178 (see F-262, US-178). #63:
  worker-3's single nix-shell.drv env build cleared; AC5 wording, TW
  Q1 and Q4 staged for the next commit.
  UPDATE (CM, 2026-10-26, after v222): backlog v222 pushed as
  658e8d92; df 4.7 GB. #65: only C1 open (C2 met when C1 is). #64: QE
  APPROVED (final). F-262: Architect accepts AE S1-S8; sequencing set
  (F-262 from main first, 174d frozen); diagnostic route pending the
  AE. #63 conflicts with main, so no CI since 9b1aa8a1 until the main
  merge. F-400 severity medium (Architect).
  UPDATE (CM, 2026-10-26, after v223): backlog v223 pushed as
  02fb3ae5. F-262 diagnostic spec FINAL (AE AND rule; worker-4
  building scratch/F-262-diag from 289f1a72); QE rulings
  Q1/Q2/Q3/Q4/Q7 in; Q4 verdicts and Q5/Q8 open with the AE and
  Architect. New IDs: F-402 (journey-test skip-on-500, QE) and F-403
  (capture redesign, PO: P1 after F-262; gates US-174e, not US-178).
  #64 new head 15bd74eb, CI 40320048783 running. #63 new head
  3a4baba1, still conflicts with main, no CI yet.
  UPDATE (CM, 2026-10-26, after v224): backlog v224 pushed as
  187c7b1e. F-262: the diagnostic decision rule is CLOSED (Architect
  tie-break: the three-outcome Decision block in joint-diag-final.txt,
  not the AE AND text v224 quotes); Q2/Q3/Q4/Q5/Q8 settled. F-403:
  does not block the F-262 merge but blocks any amps-on
  room-correction deploy (Architect); it gates US-178's amps-on
  activation and acceptance step, not development or amps-off testing
  (AE + Architect, narrowing the PO non-gate); PO: S4 first, as its
  own slice/PR. #63: TW batch landed as 94064cc2 (parent 3a4baba1, new
  F-400.md); worker-3 merges main next.
  UPDATE (CM, 2026-10-26, after v225): backlog v225 pushed as
  5f3adee0. F-262 diagnostic running as CI run 40320962929 on
  scratch/F-262-diag at 4134852f. F-403: S4 brief condition
  (Architect); F-403.md goes inside the F-262 PR (CM call); signal-gen
  can't export the buffer it played (S2 finding). #63: merge head
  5db98556 pushed, PR MERGEABLE, CI 40320814684 running; a follow-up
  commit comes with the AE's US-173.md 248-251 text and
  run_venue_checks on the committed WAVs. New one-liner from worker-4:
  test-e2e.sh `set -e` makes the E2E_EXIT reporting dead code.
  UPDATE (CM, 2026-10-26, after v226): backlog v226 pushed as
  fa9908e3. F-262 diagnostic run 40320962929 INVALID (18 of 20 runs
  driver_error; session not reset after an error); worker-4 fixing it
  for a rerun. F-403: Architect + AE rulings on worker-4's findings
  (1)-(3) and the S4 parameters (S4 condition AMENDED; S2 route =
  file-playback RPC; pink-burst overlap is a candidate US-178 gate).
  #63: final head 0dc2a40b, CI 40321143579 running (5db98556 run
  cancelled), bundle /tmp/pr63-review-0dc2a40b/ out to all 7; verdicts
  recorded so far: UX, QE. Disk dipped to 4.52 GiB (now 4.6): all nix
  clearances withdrawn until there is more headroom (CM).
  UPDATE (CM, 2026-10-26, after v227): backlog v227 pushed as
  36892930. #63 at 0dc2a40b: 6 of 7 verdicts posted on the PR (AE,
  Architect, UX, SecSpec, TW CI-conditional; AD diff-only); the QE's
  APPROVED WITH CONDITIONS C1-C4 waits for its file before posting.
  New defect F-404 (AE: measurement session leaves the gate as found;
  after error or abort it re-links production with the gate open);
  blocks US-178 and any amps-on measurement. F-262: driver fix
  2676be53 pushed, diagnostic rerun triggered; decision rule v2
  replaces the joint-diag-final.txt Decision block. Disk:
  /System/Volumes/Data at 2.7 GiB available (4.6 at 12:14Z); no nix
  client running; cause unknown, reported to team-lead (CM).
  UPDATE (CM, 2026-10-26, after v228): backlog v228 pushed as
  517c182e. PR #65 (F-399) MERGED as 29f5c61f (7/7 at 13995e15, CI
  40317165021 green, QE C1 final). #63: all 7 verdicts posted at
  0dc2a40b and the B4 body 69ae9511 applied, but CI 40321143579 is RED
  (room-correction 2 failed / 60 errors: main's build_channel_map
  rejects the ch 4 zero.wav mute); worker-3 fixing it on 29f5c61f; all
  7 verdicts lapse, diff-only re-checks at the new head. F-262:
  diagnostic now 293cf822 (run 40322683521; 2676be53 and 7c38c463 runs
  cancelled); AE width trigger and onset-before-gate ruling; QE
  accepted M9. One-liners: the UMIK-1 cal-file skip (QE; files found
  on the Mac, team-lead) and Start-after-error 409 (worker-4). Disk:
  Data at 4.4 GiB (2.7 at the v228 reading); the owner is freeing
  space; nix holds stay (CM).
  UPDATE (CM, 2026-10-26, after v229): backlog v229 pushed as
  fc17ee27. US-174d CONDITIONS (1)+(2) and the Architect's
  single-writer condition (3) relayed verbatim to worker-4; 174d stays
  frozen until F-262 lands. #63: the Architect accepted worker-3's
  zero.wav option (A); the AE accepts it with three conditions;
  worker-3 building on 29f5c61f. F-262 diagnostic now aedf4a82 / run
  40322886856 (293cf822 run 40322683521 cancelled).
  UPDATE (CM, 2026-10-26, after v230): backlog v230 pushed
  (chore/backlog head f3334cbe). #63: zero.wav ruling FINAL as joint
  AE + Architect v3 (sha256 f35f5b59; v2 and v1 VOID), relayed to
  worker-3; the QE confirmed from CI 40321143579 that the spare-mute
  zero checks run in T1. US-172: RUN-4 kit v5 ready (pins e62744a7,
  CM-verified, built off the Pi), out for review with the Architect,
  QE, AE and AD; no grant yet.
  UPDATE (CM, 2026-10-26, after v231): backlog v231 pushed as
  48f8d754. US-172 RUN-4 kit v5: AE APPROVE, QE APPROVE WITH
  CONDITIONS C1-C2 (both before the CHANGE 1 grant); Architect and AD
  pending; worker-2's 3 deltas vs the v2 spec are with the Architect
  (v6 if any is ruled in). #63: worker-3's caa63d9e HELD, not pushed
  (differs from ruling v3); worker-3 conforming in a follow-up commit.
  Disk 4.2 GiB, below the 4.5 line; holds stay (CM).
  UPDATE (CM, 2026-10-26, after v232): backlog v232 pushed as
  c28fa793. #63: 3f28b6c7 (conforms to ruling v3) pushed, CI
  40323763997 running; the "caa63d9e HELD" line is superseded. US-172
  kit v5: Architect CHANGES REQUESTED R1-R3, AD REQUEST CHANGES M1, AE
  APPROVE, QE APPROVE WITH CONDITIONS (C1 open); Architect delta
  rulings D1 NO, D2 YES, D3 YES; worker-2 building v6 off the Pi. The
  tb-modprobe gate is NOT settled (joint AE + Architect ruling
  requested); no grant yet. Disk 4.4 GiB; holds stay (CM).
  UPDATE (CM, 2026-10-26, after v233): backlog v233 pushed as
  bf823e42. US-172 tb-modprobe gate SETTLED: joint AE + Architect
  ruling dcec60fa (both released the same sha); it replaces Architect
  R2 and the AE's v5 note. v6 relayed to worker-2. QE C1 still open.
  #63 evidence route v2: scratch/pr63-evidence-3f28b6c7 = 2a17ed77,
  run 40324085388 in progress, gates nothing (CM).
  UPDATE (CM, 2026-10-26, after v234): backlog v234 pushed as
  5177c551. US-172: the Architect's tb-greetd ruling stands (refuses
  unless [MOD-gains] ok and [MOD-gate] ok). #63 evidence run
  40324085388 green. Disk /System/Volumes/Data 21 GiB free, above the
  4.5 line: nix clearances can be granted again on request; the nix
  hold itself stays (every nix build/run/develop needs a CM clearance,
  store deletes need the owner's OK, nobody touches the linux-builder)
  (CM).
  UPDATE (CM, 2026-10-26, after v235): backlog v235 pushed as
  9a59deda. QE PR #63 evidence accounting: route 2a MET, route 1 MET
  pending R1-x (QE).
  UPDATE (CM, 2026-10-26, after v236): backlog v236 pushed as
  66dd389a. #63: the QE and Architect evidence verdicts are posted on
  the PR; the Architect's evidence check passes (CM).
  UPDATE (CM, 2026-10-26, after v237): backlog v237 pushed as
  1d19e534. US-172: QE C2 MET by dcec60fa, C1 still open; QE v6 gate
  sim flows G1-G11 relayed to worker-2; tb-greetd addendum file from
  the Architect pending (CM).
  UPDATE (CM, 2026-10-26, after v238): backlog v238 pushed as
  d0507d0c. US-172: the Architect's tb-greetd addendum is pinned
  (762f9035); the "Pending" line is resolved (CM).
  UPDATE (CM, 2026-10-26, after v239): backlog v239 pushed as
  5b3832ac. US-172: QE verified addendum 762f9035; G10 refined into
  G10a/b/c; worker-2 v6 in progress (not pinned); one consolidated
  FINAL v6 scope sent to worker-2, one v6 pin, no v7 (CM).
  UPDATE (CM, 2026-10-26, after v240): backlog v240 pushed as
  6cc5c759. #63 CI 40323763997 GREEN at 3f28b6c7, 7 re-checks
  requested. #64 CI 40320048783 GREEN at 15bd74eb, worker-1 merging
  main 29f5c61f. F-262 diag 40322886856 SUCCESS, v2 verdict CONFIRMED
  / jitter; validity with the AE and Architect; fix branch held.
  US-172: worker-2's v6 in progress (CM).
  UPDATE (CM, 2026-10-26, after v241): backlog v241 pushed as
  27becf25. #63 at 3f28b6c7: 6 of 7 APPROVE verdicts posted (QE with
  C4 open, UX, Sec, Architect, AD, AE); TW pending. Two non-blocking
  LOWs for US-174d (Sec, AD L1). F-262 joint validity ruling:
  Architect released, AE release pending. US-172: worker-2 has the
  final v6 scope again (CM).
  UPDATE (CM, 2026-10-26, after v242): backlog v242 pushed as
  6e20e110. #63: all 7 verdicts posted at 3f28b6c7 (QE APPROVED WITH
  CONDITION C4); #63 stays a DRAFT, NOT merge-ready (team-lead STOP).
  F-262: no sha released by both authors yet; the Architect is the
  single writer. US-172: the AE lists the Architect's dcec60fa
  re-release as pending; no v6 grant until settled. #64: head
  f715538e, CI 40333713247 running. New F-405 (QE, test-only, #64 skip
  rulings) (CM, QE).
  UPDATE (CM, 2026-10-26, after v243): backlog v243 pushed as
  44120a07. F-262: JOINT final (set A, released by both); worker-4
  briefed, fix branch authorised; 174d stays frozen until F-262
  merges. US-172: the dcec60fa gate is settled, no gate-side obstacle
  to the v6 grant. #63 deploy-first is ON (team-lead + PO), conditions
  pending. F-405: P2 (AE) (CM, AE).
  UPDATE (CM, 2026-10-26, after v244): backlog v244 pushed as
  4d8eca64. #63 deploy-first is OFF: US-172 v6 on rcyg67wd first, THEN
  the #63 DEPLOY plus P-steps (team-lead ruling; Architect pin-break
  finding). F-405: no amps-on row now (CM).
  UPDATE (CM, 2026-10-26, after v245): backlog v245 pushed as
  e53f2a94. #63 Pi plan v2 (dd227076) in review with the AE, the
  Architect and the QE. #64 CI 40333713247 still running (CM).
  UPDATE (CM, 2026-10-26, after v246): backlog v246 pushed as
  3263c271. #63 Pi plan v2: the AE has CLEARED it (ab73af2a,
  conditions C1-C4 + Q2); the Architect (Q1/Q3/Q4) and the QE (C4
  coverage, split) are still pending on v2. The QE's plan verdict is
  on v1 da746539 (APPROVE with A1-A4). Order unchanged: US-172 v6
  first (CM, QE).
  UPDATE (CM, 2026-10-26, after v247): backlog v247 pushed as
  72fad62d. #63 Pi plan: the QE APPROVES v2 (c1e573fe, A1-A6,
  supersedes 37ae18e6); the Architect APPROVES WITH CONDITIONS C1-C7
  on v1 (969edef6), carry-over to v2 pending; P17 overlap open
  (Architect writes one joint line, the QE releases it); worker-3
  holds the P17 part of v3. New one-liner: CI runner image (team-lead)
  (CM, QE, team-lead).
  UPDATE (CM, 2026-10-26, after v248): backlog v248 pushed as
  ad74c35f. #63 Pi plan v2: the Architect APPROVES WITH CONDITIONS
  (03288857; C1-C7 carry over, new A1-A3; carry-over SETTLED). P17 and
  the Q1 conflict are RESOLVED by the joint ruling 5e123a6b (Architect
  wrote, QE released). worker-3 is writing plan v3 (CM).
  UPDATE (CM, 2026-10-26, after v249): backlog v249 pushed as
  9dff179b. #63 plan v3 (df8e1614) crossed with the later rulings;
  worker-3 is writing v4. Open [ARCH-CHECK] on C7 (F-249 standby).
  F-262 set A: six worker-4 impl findings (e3900cbf); the AE's F1-F5
  ruling a8386f4b awaits the Architect's release; F6 is with the
  Architect; nothing has gone to worker-4 yet (CM).
  UPDATE (CM, 2026-10-26, after v250): backlog v250 pushed as
  91706431. F-262 set A: F1-F5 (a8386f4b) and F6 (dfffcfbf) are both
  released and relayed to worker-4; new F6 follow-up one-liner (legacy
  CLI). #63 [ARCH-CHECK] C7 SETTLED (2aeff13a); worker-3 folds it into
  plan v4 (CM).
  UPDATE (CM, QE, 2026-10-26, after v251): backlog v251 pushed as
  3822cc1e. #63 Pi plan v5 ed039bfb (v4 plus C7 2aeff13a) supersedes
  v4 3d3bfff7; the AE released v5 (ab73af2a carries over); the QE
  approved v4 (b0623656); the Architect and the QE are pending on v5.
  F-262 releases now cited from the CM release record aca30fe1 (CM,
  QE).
  UPDATE (CM, QE, 2026-10-26, after v252): backlog v252 pushed as
  141e2ea2. #63 Pi plan v5 ed039bfb is APPROVED by all three plan
  reviewers (Architect 6b0d7071, QE 24e77f04, AE release). No v6 plan
  file (CM ruling); the grant binds v5 + N1-N3 + R-a/R-b by reference
  and still waits for US-172 v6. QE C4 on #63 stays open. Two
  attribution fixes (5e123a6b item 3; the AE's thermal-STOP line).
  F-262: the Architect's own release file eb621b26 (CM, QE).
  UPDATE (CM, 2026-10-26, after v253): backlog v253 pushed as
  bca7c488. F-262: worker-4 pushed c1-c4 (fix/F-262-shared-correction
  at d677f253); DRAFT PR #66 opened so CI runs (run 40338944793 in
  progress). Five new worker-4 findings frozen (b76bc353): (1)-(4) AE
  writes, Architect releases; (5) Architect alone. PR #66 is now the
  F-262 PR (CM).
  UPDATE (CM, 2026-10-26, after v254): backlog v254 pushed as
  50d9a5bb. F-262 PR #66: all rulings on worker-4's c1-c4 findings are
  in and relayed: item (5) Architect e65ced02 (scan changes S1-S6, F6
  allowlist correction), items (1)-(4) AE dc9e529d released by the
  Architect (record (d) a8bf9931). Two new AE backlog one-liners under
  F-262 (CM).
  UPDATE (CM, 2026-10-26, after v255): backlog v255 pushed as
  62bf5e6e. F-262 PR #66 head e325c4ba (434cfe99 F6 scan, e325c4ba c7
  capture alignment); CI 40343196576 running. CI 40338944793 at
  d677f253 FAILED (10 failed, 7 errors); worker-4 diagnosing. c8 (T8
  xfail removal) waits on an AE ruling, the QE releases (CM).
  UPDATE (CM, QE, 2026-10-26, after v256): backlog v256 pushed as
  deed1e00. F-262 c8: AE ruling f8a014c7 (option (a) with conditions),
  awaiting the QE release; A1-A7 retracted (CM). #64: CI 40333713247
  green on all 4 jobs, QE count profile MET (96abe4fb), worker-1
  finishing the body, QE diff-only re-check open; new one-liner
  (test_full_session_api flips). US-172 v6 pinned at us172.sh fc65bcad
  (82113c3f void); re-reviews open (CM, QE).
  UPDATE (CM, QE, UX, 2026-10-26, after v257): backlog v257 pushed as
  37a7622c. F-262 c8 ruling f8a014c7 RELEASED by the QE and relayed to
  worker-4. PR #66 CI 40343196576 at e325c4ba FAILED; worker-4
  diagnosing. #64: body a2bfb9af live, bundle out to all 7; UX APPROVE
  (3a8e85ff). US-172: fc65bcad SUPERSEDED; a v7 re-pin is required (QE
  Q1/Q2 REQUIRED). Team-lead rule: no re-pin for non-blocking points
  (CM, QE, UX).
  UPDATE (CM, QE, AD, 2026-10-26, after v258): backlog v258 pushed as
  2492c7f5. PR #64 (F-362) MERGED as ff091e5f, 7/7 APPROVE at
  f715538e, CI 40333713247 green; F-362 open only for ACs 1-2 and the
  test_filter_routes.py guard (US-174d). US-172: O1 settled,
  fail-closed stays; grant conditions r1 G-1 to G-6 on file
  (6c6308f5); worker-2 pinning v7. F-262: PR #66 head 4396e03c, CI
  40344885535 queued; #66 behind main (CM).
  UPDATE (CM, 2026-10-26, after v259): backlog v259 pushed as
  f382d6f5. US-172 O1 ruling file now on record (release record (f),
  57ee3eb8; corrects v259). #64 non-accepted skips mapped to F-IDs;
  new F-406 and F-407 (PM). F-262: PR #66 head ff985455, CI
  40345460992 running; worker-4 finding b4c66788: the shared min-phase
  gate rejects crossover-only filters for 10 of 11 real profiles; AE
  ruling, Architect release; c8 10-run AC waits on it. worker-1 on
  F-394 (PO pick).
  UPDATE (CM, 2026-10-26, after v260): backlog v260 pushed as
  6ddfea68. PR #67 (docs-only F-406/F-407 records, head ae450041) open
  as draft; 7 Rule 13 verdicts requested; CI-exempt. TW has
  F-406/F-407 in their queue. #66: CI 40345460992 at ff985455 still
  running; needs a main-merge before merge (CM).
  UPDATE (CM, 2026-10-26, after v261): backlog v261 pushed as
  216ee4d2. #67: 6/7 APPROVE at ae450041 (AE pending). PR #68 (F-394
  draft, worker-1, 257b272d) CI 40346339865 running; consult Q1-Q3
  with QE/AE. F-262: AE gate-xo ruling v1 (0aac380f) awaiting
  Architect release; new F-408 for its G4 follow-up (PM) (CM).
  UPDATE (CM, QE, AE, 2026-10-26, after v262): backlog v262 pushed as
  d0f8bc0e. PR #67 MERGED as 498fa3e5, 7/7. F-394: Q2 RELEASED and Q3
  final, both to worker-1; Q1 awaits the AE release. #66: CI
  40345460992 at ff985455 FAILED (12 failed, all "Filter verification
  failed"); the Architect did not release gate ruling v1 (A1
  required); the AE writes v2 (CM).
  UPDATE (CM, AE, 2026-10-26, after v263): backlog v263 pushed as
  f3d7df8f. F-262 gate ruling v2 (91eca61e) RELEASED by the AE and the
  Architect and relayed to worker-4; supersedes v1 (never relayed).
  F-408 attaches to its G4 (no v3; Architect). F-407 set to P2 (AE)
  (CM, AE).
  UPDATE (CM, AE, 2026-10-26, after v264): backlog v264 pushed as
  b593238e. F-394 Q1 RELEASED by the AE (a532179b) and relayed; Q1-Q3
  all with worker-1; fence r3. F-408: AE addendum 165ae71a names it as
  gate v2's G4 follow-up (CM).
  UPDATE (CM, 2026-10-26, after v265): backlog v265 pushed as
  b50b9ed6. F-394 head e050fe90 and fence r4; F-262 head 7011419d with
  the P3 table and finding H1 (AE ruling pending). New: F-409 (UI does
  not show the min-phase residual) and F-410 (unmute restores gains
  behind a closed gate).
  UPDATE (CM, AE, Architect, 2026-10-26, after v266): backlog v266
  pushed as 2f58d759. F-410 set to P2 (AE). F-262 H1 RELEASED (AE
  cfe9bf66, Architect record (i) e6ba4317) and relayed to worker-4
  with F-409. F-410 goes to worker-1 with the CM's next relay.
  UPDATE (CM, 2026-10-26, after v267): backlog v267 pushed as
  95f4e65e. F-262 #66 head 0c592da1 implements H1; the P3 re-run
  passes every buildable profile, with no D-031 report. US-172: the
  owner asked for status (via team-lead); v7 pins not yet in, and the
  CM has sent worker-2 one status ask.
  UPDATE (CM, Architect, 2026-10-26, after v268): backlog v268 pushed
  as cb7cd9f7. US-172 v7 kit (us172.sh 815d231e) Architect pre-review:
  "NOTHING BLOCKING, NOTHING REQUIRED." Three later-kit one-liners
  recorded under US-172.
  UPDATE (CM, QE, AE, AD, 2026-10-26, after v269): backlog v269 pushed
  as 358ca39a. US-172 v7 pre-reviews from the QE, AE and AD recorded
  under US-172. Grant conditions r2 add G-7 (Architect release
  pending) and G-8 (released by the AE, record (j)). QE Q3 (REQUIRED,
  one re-pin) is still open.
  UPDATE (CM, QE, Architect, AD, 2026-10-26, after v270; supersedes
  the line above): backlog v270 pushed as ff61a662. US-172: QE Q3
  CLOSED by G-8 for this run (record (l)); G-7 RELEASED by the
  Architect (record (k)), so grant conditions r2 are fully released;
  the AD closes P1/P2. Every v7 pre-review point is closed; no re-pin,
  and the 815d231e run counts. F-394: fence r5, #68 head 51fae218.
  UPDATE (CM, QE, AE, AD, Architect, team-lead, 2026-10-26, after
  v271): backlog v271 pushed as 237119bc. US-172 v7 kit (815d231e):
  all four final verdicts APPROVE (QE, AE, AD, Architect), none
  blocking. F-394: #68 head 0cb35f0c; QE ruling on AC (iv) (where the
  N>=5 green runs land). F-262: an XPASS in CI 40356547804 for a test
  whose xfail cites F-262.
  UPDATE (CM, PO, QE, team-lead, 2026-10-26, after v272): backlog v272
  pushed as ecad8f35. v273 (frozen 380d4a37) and v274 (frozen
  2a1e29ab) were never pushed: v273 filed US-179 r3, which the PO
  voided, and v274 recorded the F-403.md writer before fence r2.
  US-179: r3 VOID (owner corrections 2026-10-26: 20 Hz low end, the
  seeded per-channel noise design, a Smaart-style display); r4 pending
  at a new path; US-179 and US-180 reserved for the PO. F-262 c8:
  fence r1 b1f0fcbf, then r2 084ad898 (F-403.md out of worker-4's set;
  verify.py FENCED pending the Architect and the AE); 971725d7 VOID,
  never pushed; 65af5ee2 (R2/R3 test files only) queued. QE answers
  abfd33d7 (CI dispatch runs count as the R5 runs; the F-403 minimum
  content). F-403.md writer: PM-allocated, not worker-4 (AE R4, QE Q2;
  CM accepted); PM proposes the TW, TW answer pending.
  UPDATE (CM, Architect, AE, QE, TW, 2026-10-26, after v275): backlog
  v275 pushed as 7e82ef6f. US-172 run 4 CLOSED (Architect ruling r4
  1816176e, decision (c)); next is a v8 bisect kit (run 5). F-262:
  fence r3 48133641 makes verify.py gate_summary OWNED under Architect
  C1 (a627ca97) and AE C1-C3 (f277e402); QE R5 ledger rules r2
  ebd890d0. F-403.md writer: the TW, single writer, allocated by the
  PM and CM (QE released; AE fine with the TW; supersedes "TW answer
  pending" above); TW batch v1 371f0f13; worker-4's fe80d4fa is not
  pushed and is frozen as TW input. AE R6 backlog line filed under
  F-262.
  UPDATE (CM, PO, AE, QE, Architect, 2026-10-26, after v277): backlog
  v277 pushed as bd206f32 (blob c7fc3433). The PM's v278 (121380ad)
  and v279 (d5e8fb09) were never pushed (stale base 7e82ef6f; messages
  crossed). F-403.md writer settled: the TW (QE and AE released,
  record (f) 7f3a057b); F-262 fence r4 865f5117 (wording only). AE R4
  branch ruling 2218daf5: B1 fixture fix, B2 filed as F-411 (Medium).
  eb178a19 (6c7fe986) released by the Architect and the AE (stricter
  line, new head follows). US-179 r8 (978c3e1b) FILED in P3, released
  by the AE, the Architect and UX (PO); assigned to worker-6; US-180,
  US-181 and US-182 filed as follow-ups; D-071 allocated for the
  seeded test-noise design.
  Addendum (CM, 2026-10-26, same version): release record (g) ba281200
  (eb178a19 is not the streak head; a new head with the set-equality
  line needs AE + Architect releases); TW F-403 batch v2 86ab5ba2
  supersedes v1, held until that head.
  UPDATE (CM, AE, Architect, 2026-10-26, after v281): F-262 cd1f63e7
  (the set-equality line) released by the AE and the Architect, record
  (h) eb035598; TW F-403 v2 applied as docs-only commit 4724e65d;
  origin fix/F-262-shared-correction = 4724e65d; PR CI run
  40395927172, then the R5 series. Architect one-liner filed in P3
  (session.py _profile_dirs ignores PI4AUDIO_SPEAKERS_DIR).
  UPDATE (CM, AE, QE, team-lead, 2026-10-26, after v282): backlog v282
  pushed as cb87c39d (v281 was 31846ac9). F-411 set to P2 (AE); owner
  worker-7, two phases (QE release; worker-4 release withdrawn). QE:
  no R5 rule change at 4724e65d. TW F-403 v3 (F-411 swap, QE AC 6
  citation) held until after the R5 series.
  UPDATE (PO, PM, 2026-10-26, after v283): backlog v283 pushed as
  d8c365d6. US-179 r8 erratum E1 v2 (6a78af9f) applied to the US-179
  entry (E1a/E1b/E1c verbatim; E1 732847a4 VOID): pcm-worklet.js is a
  Pi playback feeder, so the mic meter is a new worklet in src/web-rc
  computing true sample peaks.
  UPDATE (CM, PO, AE, team-lead, 2026-10-26, after v284): backlog v284
  pushed as 8246a029. US-179: AE signal answers 6d63a2e3 recorded; S1
  ruled by the PO (e14a0d75: required per-channel role, no default);
  erratum E2 bca0d86b applied verbatim (governing text r8 + E1 v2 +
  E2). F-411: worker-7 briefed for phase 1 (1e64f46b; git-archive
  scratch copy; fixture f5ca9040). F-403: TW batch v5 5abeed4f,
  applied after the R5 series.
  UPDATE (CM, AE, QE, team-lead, 2026-10-26, after v285): backlog v285
  pushed as 2225d2c8. F-411: phase 1 findings bf381fe4; AE ruling
  5fe39778 (gate's 1/6-oct view is right; phase 2 changes the design
  smoothing, P1-P3, E1-E4); AE E3 plan ruling 904f34c9 (A1-A4, no
  simulator change); QE condition 2 r2 d0052503; AE follow-up
  one-liner (real two-position UMIK-1 check). F-383 + F-384: owner
  worker-7 (team-lead confirmed), phase 0 offline after F-411.
  UPDATE (CM, AE, PO, team-lead, 2026-10-26, after v286): backlog v286
  pushed as 882c962a. F-411: CM confirms E3 by call argument, no
  mock-file edits (2c holds). F-383 + F-384: phase 0 GO (b74a78a0);
  report dadab0bf (LR8 LP fallback triggers; subsonic factor open;
  F-384 overshoot from steps 7-8); AE item (2) subsonic ruling
  935b4ee2 recorded, Architect release pending; F-384 forced-input
  task (8fb41306); worker-7 priority order. US-179: base stays on
  main; errata E3 8f508af1 and E4 r2 f692681c recorded with three
  notes for worker-6.
  UPDATE (CM, team-lead, 2026-10-26, after v287): backlog v287 pushed
  as 5543b591. F-383: the Architect released the AE subsonic ruling
  935b4ee2 in full (S1-S3), so the CM's S1 hold is lifted; FINAL F-383
  record (team-lead final stop rule) = A r3 89c3bb1b + B r1 349b585f +
  935b4ee2 + AE diagnosis job c281701b; worker-7 runs phase 0b after
  the current F-384 step. US-179: E3 8f508af1 and E4 r2 f692681c
  relayed to worker-6 with the three notes.
  UPDATE (CM, AE, PO, 2026-10-26, after v288): backlog v288 pushed as
  8a46dd02. F-383: the CM's answers on the releases behind the record
  (message releases, no new files). US-179: AE answers K1-K5 to
  worker-6 (1318b25c), PO K3 ruling e720d78c (no erratum; AC2c
  governs, DSP flags not OFF or missing BLOCK measuring), and the AE's
  K4 follow-up one-liner.
  UPDATE (CM, AE, 2026-10-26, after v289): backlog v289 pushed as
  cd6ce65f. US-179: the AE rules K4 does NOT go on the amps-on
  precondition list (ae0c3e70); it stays a scoped US-179 follow-up,
  checked in the go-check of the first amps-on US-179 web measurement
  run relying on calibrated SPL. The AE has no objection to the PO's
  K3 ruling e720d78c.
  UPDATE (team-lead, 2026-10-26, after v290): backlog v290 pushed as
  f68220c1. US-179: team-lead's "either way" K4 line is superseded by
  the AE's narrower scope in ae0c3e70.
  UPDATE (CM, team-lead, AE, UX, 2026-10-26, after v291): backlog v291
  pushed as ab87b63a. PROCESS: every CM relay of a ruling to a worker
  asks for a one-line ack naming the sha(s); no ack by the worker's
  next report means one re-send plus a note to team-lead. US-179:
  worker-6 head 129c031c pushed; AE flags 2/4 ruling 794b1eeb; UX
  wording 5eb9829c (section 2 relayed; section 1 pending a PO erratum
  decision and an AE safety question).
  PROCESS RULE (team-lead, via CM, 2026-10-26; CM wording): every
  ruling the CM relays to a worker asks for a one-line ack naming the
  sha(s) received. If no ack arrives by the worker's next report, the
  CM re-sends once and tells team-lead. Trigger (CM): worker-6 missed
  the E3/E4 r2, base ruling, 1318b25c and K3 relays; the CM re-sent
  them all.
  UPDATE (CM, AE, 2026-10-26, after v292): backlog v292 pushed as
  0b435258. US-179: AE device-change ruling 20a9bc76 (D1-D4: clear the
  4a ack, every AC3 declaration and the mic-calibration binding;
  discard earlier captures and levels); the PO drafts it as erratum E5
  after the final UX text; worker-6 keeps E4 r2 until E5 is final.
  F-262/#66: PR CI 40395927172 at 4724e65d SUCCESS; R5 series started
  (A1 OK), run 1 = 40403348924. US-172: v8 kit c96afb79 in review
  (Architect, AE, QE); worker-2 acked c96afb79.
  UPDATE (CM, AE, Architect, 2026-10-26, after v293): backlog v293
  pushed as 5f55f455. US-172 v8 kit c96afb79: AE APPROVE (96cf081b;
  gains re-read verb not needed, run-time conditions C1-C4), Architect
  APPROVE r1 (fafd59fc; all 9 design points accepted, R5b
  classification not a step-c precondition, non-blocking N1/N2, no new
  kit); QE pending.
  UPDATE (PO, AE, UX, CM, 2026-10-26, after v294): backlog v294 pushed
  as 0a117e45. US-179: erratum E5 df065993 FINAL (rate/device-change
  stop texts, device-change reset 2e D1-D4, whole-Hz low limit,
  tests), released by the AE (c56fd763) and UX (by message); relayed
  to worker-6 with the AE's test note; worker-6's ack is pending.
  UPDATE (CM, QE, team-lead, 2026-10-26, after v295): backlog v295
  pushed as 0b1dc2d1. US-172 v8 kit c96afb79: QE APPROVE (38663487;
  binding CM run conditions C1/C2, no re-pin), so all three reviewers
  APPROVE; step-a grant CHANGE-US172r5a r1 (60369f8f) issued to
  worker-2, Phase A1 pre-obs only. F-412 filed (P2, QE): the kit
  decides TRYBOOT by absence. US-179 E5: UX release detail (by message
  21:20:58Z, relayed by team-lead).
  UPDATE (CM, worker-2, 2026-10-26, after v296): backlog v296 pushed
  as 1c6a0433. US-172: worker-2's five one-liners (49ab9ebb) sorted:
  F-413 (recovery boot-id match), F-414 (pstore read needs sudo),
  F-415 (date Pi 5 boots by /proc/uptime or NTP sync) filed, no
  P-level given; the tty1 fallback and the watchdog comment merge into
  existing items (no new ID). Run-2 report v2 1fe62b96 in review
  (Architect, QE).
  UPDATE (CM, 2026-10-26, after v297): backlog v297 pushed as
  cfff23cd. US-172 run-2 report v2 1fe62b96: Architect APPROVE once W1
  is applied (4e3bc0c5), QE APPROVE (4271f63b). Architect N2 and QE
  note 5 (rt-tuning.nix:24 watchdog claim) fold into O-24 / F-317 /
  F-325, no new ID. Architect: F-413, F-414 and F-415 are P3; no kit
  change for run 5.

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
Allocated 2026-10-26 (PM, checked free across main, origin and all
worktrees): US-177 (Architect: Web-UI filter panel on 174d coefficient
sets). Next free (supersedes the line above): F-400, US-178, D-071,
T66.
Allocated 2026-10-26 (PM, checked free across main, origin and all
worktrees): F-400 (Architect: conf.d fragments installed hash-named,
#63). Next free (supersedes the line above): F-401, US-178, D-071,
T66.
Allocated 2026-10-26 (PM, checked free across main, origin and all
worktrees): F-401 (worker-4: test module skipped by an ImportError
guard). Next free (supersedes the line above): F-402, US-178, D-071,
T66.
PM correction 2026-10-26: F-401 WITHDRAWN as a duplicate of F-362
(retired, not reused). Allocated 2026-10-26 (PM, checked free across
main, origin and all worktrees): US-178 (Architect: measurement flow
deploys via 174d sets). Next free (supersedes the line above): F-402,
US-179, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-402 (QE option (b): journey-test
skip-on-500 hides a server error) and F-403 (PO: capture redesign, P1
after F-262). Next free (supersedes the line above): F-404, US-179,
D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-404 (AE: measurement session leaves
the gate as found; re-links production with the gate open after error
or abort). Next free (supersedes the line above): F-405, US-179,
D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-405 (QE: test_gate_closed_e2e.py:137
bare except turns a gate-open result into SKIPPED). Next free
(supersedes the line above): F-406, US-179, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-406 (QE: test_filter_deploy_e2e.py:315
skips on a missing v1 after deploy; rollback untested) and F-407 (QE:
test_venue_gate_e2e.py:165/:180 skip on gate-indicator timeout). Next
free (supersedes the line above): F-408, US-179, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-408 (AE gate-xo ruling v1 0aac380f
G4: replace the cepstral min-phase residual with a metric valid for
unit-circle zeros; ruling not yet released by the Architect). Next
free (supersedes the line above): F-409, US-179, D-071, T66.
Allocated 2026-10-26 (PM, checked free across main, all origin/* and
local branches, and worktrees): F-409 (worker-4: G1 residual not shown
in the UI) and F-410 (worker-1: unmute restores the venue gains while
the gate is closed). Next free (supersedes the line above): F-411,
US-179, D-071, T66.
Reserved 2026-10-26 (PM, for the PO; checked free across main, all
origin/* and local branches, and worktree docs, where only Next-free
lines mention them): US-179 (Web-only standalone room correction, P3
side quest; reserved, text pending r4. PO: "r3 VOID; final text
pending r4 (owner corrections 2026-10-26)": support down to 20 Hz,
reuse of the seeded per-channel noise design (US-121 scheme), a
Smaart-style display (US-120). r1, r2 and r3 are void; the PM's frozen
r3 copy /tmp/pm-backlog/US-179-final-r3-75e731bc.md is history only,
not governing text; r4 brings its own Later items) and US-180 (PO, for
the US-179 later item "re-measure after the filters are loaded
elsewhere"; the PO asked for it to be allocated when r4 is filed).
Next free (supersedes the line above): F-411, US-181, D-071, T66.
Filed 2026-10-26 (PM, for the PO, from US-179 r8 978c3e1b; checked
free across main, all origin/* and local branches, and worktree
docs/src, where only Next-free lines mention them): US-179 (filed,
P3), US-180 (filed), US-181 (browser Smaart-style view), US-182 (live
impulse-response view; confirmed free), D-071 (seeded per-channel
test-noise design, US-179 AC5). Next free (supersedes the line above):
F-412, US-183, D-072, T66 (F-411 filed in this version, see F-403).
Next free (v296; supersedes the line above; F-412 confirmed free on
main and all origin/* branches at PM read, filed in this version, see
P2): F-413, US-183, D-072, T66.
Next free (v297; supersedes the line above; F-413, F-414 and F-415
confirmed free on main, all origin/* and local branches at PM read,
filed in this version, see P3): F-416, US-183, D-072, T66.
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
     FIX (AE, via the TW, US-174d draft v3,
     /tmp/tw-us174d-draft/docs/operations/safety.md sha256 41164bac;
     the AE approved the draft with this edit): in the row 15 FINAL
     text above, "on a node that is idle or running (row 14)" becomes
     "(row 16)".
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
     AMENDED (AE ruling model (1), Architect confirmed, via the TW and
     the CM as Addendum 5, 2026-10-26): US-173's F-318 hook
     (mugge-no-bypass.lua) wins. WirePlumber never auto-links
     playback, and neither the USBStreamer nor the convolver is ever
     eligible as the default sink. Two AE-verbatim replacements in the
     FINAL text above, the rest unchanged: (c) becomes "(c) the F-318
     WirePlumber hook denies every playback auto-link, and neither the
     USBStreamer nor the convolver is eligible as default.audio.sink;"
     and the last sentence "With the filter-chain present, the
     convolver is the default sink." becomes "With or without the
     filter-chain, default.audio.sink never names the USBStreamer or
     the convolver." Row 18 depends on US-173 being on main; the OPEN
     footnote covers that. PENDING: a JACK self-connect case the
     Architect and the AE added to the JACK clause; the verbatim text
     is with the CM and the TW, mirrored in the next version.
     SUPERSEDES the HELD line and the PM note above (both moot): the
     TW's Section 5 pre-flight line for the 174d batch, verbatim:
     "Before switching amps on: `pw-metadata -n default 0` must not
     name the USBStreamer or the convolver as default.audio.sink, and
     `pw-link -l` must show no link into a USBStreamer playback port
     that does not come from the convolver output. If either check
     fails, amps stay off."
     UPDATE (TW US-174d draft v2,
     /tmp/tw-us174d-draft/docs/operations/safety.md l.49, sha256
     9a6e5f5e; Architect joint ruling Part B item 4 via the CM; the AE
     is checking the new clause, and the TW sends any delta): resolves
     the PENDING JACK case above. The FINAL row has no "item (5)"
     (that was the PROPOSED numbering); the clause is the last clause
     of (b). (b) is replaced, verbatim: "(b) no link exists into any
     USBStreamer playback port (ch 1-8), including after a pw-play to
     the default sink, after a JACK client with autoconnect forced on,
     and after a JACK client calls jack_connect into a USBStreamer
     port (self-connect-mode);" The rest is as AMENDED above: (a), the
     (c) replacement, (d) and the last sentence. The OPEN footnote for
     row 18 now cites "the F-318 WirePlumber hook and the JACK
     self-connect-mode setting (both US-173)".
     AE FINAL (TW US-174d draft v3, sha256 41164bac, AE-approved,
     2026-10-26; SUPERSEDES the draft v2 (b) text above and the CM
     paraphrase): in (b), "after a JACK client with autoconnect forced
     on;" is replaced, verbatim, by "after a JACK client with
     autoconnect forced on, and after a JACK client calls jack_connect
     into a USBStreamer port (jack.self-connect-mode =
     ignore-external, US-173);"
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
  US-172 ONE-LINERS v1 (worker-2 via CM, 2026-10-26):
  /tmp/cm-relay/US-172/frozen/w2-backlog-oneliners-v1-49ab9ebb.txt
  (sha256 49ab9ebb, 1177 bytes, verified at PM read), "from run 2 /
  recovery". Verbatim, each with the PM disposition:
  - 1. us172-recovery.sh step 2/2b: the old-boot-id check matches the
    id with surrounding spaces, but the id list has one id per line,
    so it falsely reports "old boot id not in journal" (rec-2
    INCONCLUSIVE, 2b empty); match whole lines (grep -qx) instead.
     PM: filed as F-413 (P3 section); same defect as US-172c one-liner
     (a) above, now with the fix.
  - 2. us172-recovery.sh step 4: `ls /sys/fs/pstore` needs sudo
    (Permission denied as ela), so pstore was never read after the
    hang.
     PM: filed as F-414 (P3 section); same as US-172c one-liner (b)
     above.
  - 3. Pi 5 base generation: without /dev/dri, greetd is skipped
    (ConditionPathExistsGlob=/dev/dri/card*) and tty1 has no getty, so
    the HDMI screen shows nothing usable; add a tty1 login fallback.
     PM: no new ID; already filed as the P3 item "No fallback login on
     tty1 without DRM" (UX, QE, Architect and worker-2 merged there);
     merged again.
  - 4. nix/nixos/rt-tuning.nix:24 claims the BCM2835 watchdog is a
    backstop for lockups; as deployed only the 10-min shutdown
    watchdog is armed (no RuntimeWatchdogSec), and it did not recover
    the hung tryboot (Pi down ~11.7 h); fix the comment or configure
    the runtime watchdog (O-24, F-317/F-325) -- skip if already filed.
     PM cross-ref: no new ID. Already covered: the runtime watchdog is
     the O-24 gap (F-317/F-325; Architect RULED above, "EXPECTED, not
     a new defect, no ID"), and the rt-tuning.nix:24 comment is AD L3
     (comment vs options.nix O-24, P3 section, PR #45 context). New
     evidence added there: Pi down ~11.7 h.
  - 5. Boot timelines on the Pi 5 (no RTC): tooling and reports must
    date boots by /proc/uptime or the first NTP sync, never by journal
    wall-clock or `uptime` "up HH:MM" (the run-2 "came back in ~40 s"
    misreading).
     PM: filed as F-415 (P3 section).
  RUN-2 REPORT v2 (CM, 2026-10-26):
  /tmp/cm-relay/US-172/frozen/w2-run2-report-v2-1fe62b96.txt (sha256
  1fe62b96, verified at PM read) is in review with the Architect and
  the QE. Verdicts: not yet relayed to the PM at this version.
  VERDICTS (via CM, 2026-10-26; supersede "not yet relayed" above;
  both crossed v297): Architect VERDICT r1,
  /tmp/cm-relay/US-172/frozen/arch-run2-report-v2-verdict-r1-4e3bc0c5.txt
  (sha256 4e3bc0c5, 2955 bytes, verified at PM read), verbatim:
  "VERDICT: APPROVE once W1 is applied. W1 is a wording fix and needs
  no new review round: the QE or I check the diff." W1 (REQUIRED,
  section 4): the line-order cause candidate is replaced by the
  Architect r4 1816176e text (verbatim in the file), because "a closed
  report must not carry a cause candidate its own author has
  replaced." Per the CM, W1 goes to worker-2 after run-5 step a. N1
  (non-blocking): add the run-2 "no panic= token (kernel default
  panic=0)" fact line only if worker-2 can confirm it from the run-2
  cmdline/pins; "Do not infer it."
  N2 (Architect, verbatim): "rt-tuning.nix sets
  kernel.sched_rt_runtime_us=-1 (RT throttle off) and justifies it
  with a watchdog backstop that is not armed. So a runaway SCHED_FIFO
  task can wedge the Pi with no automatic recovery. For gigs: either
  arm RuntimeWatchdogSec (systemd) on the BCM2835 watchdog or correct
  the comment; fold it into the existing O-24 / F-317 / F-325 rather
  than opening a new item. Per the owner's priority this is prod
  backlog, not a US-172 blocker." PM: no new ID; folded into O-24 /
  F-317 / F-325 and AD L3, with worker-2 one-liner item 4 above.
  QE verdict,
  /tmp/cm-relay/US-172/frozen/qe-run2-report-v2-verdict-4271f63b.md
  (sha256 4271f63b, 3302 bytes, verified at PM read; the QE copy
  /tmp/us172-qe-run2-report-v2-verdict-1fe62b96.md has the same sha),
  verbatim: "VERDICT: APPROVE. No blocking points; the 5 notes below
  are non-blocking." Notes 1-4 (LIBPI root wording, gain counts, mark
  the NIC/ARP line "(inference)", N1 now covered by the v8 sim only)
  are to be folded in "if a v3 happens; no re-issue just for these".
  Note 5 (rt-tuning.nix:24 watchdog claim) asks for a PM item number;
  PM answer (relayed to the QE by the CM): already tracked as O-24 /
  F-317 / F-325 and AD L3, no new F-number.
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
  UPDATE (CM, 2026-10-26): under CHANGE-US172r3-diag (worker-2),
  tb-pre e5533d74 and tb-diag ea3cf033 were all ok. Tryboot is ARMED,
  NOT triggered; the reboot waits for the owner to say they are at the
  HDMI screen.
  RESULT (CM, 2026-10-26): the tryboot boot HUNG again and left no
  journal. Power pull at about 10:59Z; the Pi recovered at 11:00:08Z.
  tb-restore granted (Architect). The owner reports the current normal
  boot sits at the console, with no login and no Wayland. The
  Architect is asking the owner about a USB-serial adapter; the run-4
  ruling waits on the owner's screen and LED observation.
  UPDATE (CM, 2026-10-26): disarmed and verified at 11:03:47Z; session
  released, the Pi lock is free. The hung tryboot showed a black
  screen with a live HDMI signal (owner verbatim: "Before the reboot,
  screen was black (but turned on, so there was video output, just all
  black)"). The normal boot applies NO dtoverlays: vc4-kms-v3d-pi5 and
  disable-bt-pi5 are both missing (suspected cause: overlay_prefix is
  67 characters, over a 64 limit). So there is no /dev/dri and greetd
  is skipped; this is the likely F-367 cause. The Architect is ruling
  on run 4.
  Close-out item (CM, 2026-10-26): remove ~/.us172-libpi on the Pi
  when US-172 closes.
  Same item (worker-2 via CM, 2026-10-26): "remove
  /home/ela/.us172-libpi and the LIBPI GC root" is ONE action; per the
  run-2 record, ~/.us172-libpi IS the GC root (-> frspf350,
  libraspberrypi).
  Root cause, likely (Architect, 2026-10-26): the Pi 5 bootloader
  hook's per-generation overlay path is 67 characters, so the firmware
  silently applies NO dtoverlays on the base boot; vc4/v3d never load,
  there is no /dev/dri, and greetd is skipped. The Architect confirms
  the WiFi firmware error is unrelated noise and the ~/.us172-libpi
  close-out item.
  QE C4 for run 3 (via CM, 2026-10-26): restore VERIFIED, posted on
  #52 (6414496681).
  RUN-4 v2 (Architect via CM, 2026-10-26; SUPERSEDES R4-0-first): H1
  is proven on the base boot (no dtoverlays applied, so vc4/v3d have
  never probed). Run 4 is a tryboot with overlay_prefix=o/,
  modprobe.blacklist=vc4,v3d and panic bounds; an OBSERVE session
  checks that the overlays applied; then a live modprobe of v3d/vc4
  under CHANGE, with the owner at HDMI and dmesg streamed off-Pi.
  Outcomes: (i) a hang before SSH means the R4-0 fallback; (ii) the
  vc4 probe hangs: that is the bug, with the log in hand; (iii)
  /dev/dri appears: the base fix is a short overlay path in
  boards/pi5/bootloader.nix, a build-time length assertion and a
  post-deploy check that the overlays applied. worker-2 is building
  the kit off-Pi.
  CORRECTION (CM, 2026-10-26; corrects outcome (i) above and the
  "tryboot hung" reading of the runs): run 1's tryboot WORKED (flag 1,
  long path, no overlays); only the o/ runs hung. R4-0 is DROPPED; the
  fallback is R4-1b (o/ without the vc4-kms line). bt_applied=0 is
  confirmed on all base boots.
  AE (via CM, 2026-10-26): the live modprobe step is accepted with 3
  conditions: (1) an outputs-off line in the go message; (2) no HDMI
  audio after vc4; (3) the F-395 gains-0 check after any hang.
  QE C4 amendment (via CM, 2026-10-26): bcmrf = the brcmfmac HT Avail
  timeout; posted on #52 (6414529491). The QE's five run-4 kit
  pre-review points went to worker-2.
  Run-4 HDMI expectation (Architect via CM, 2026-10-26): a black
  screen before vc4 loads is legitimate. The outcome (i) control is
  SSH reachability plus tryboot flag 1 plus modprobe.blacklist in the
  cmdline. Read-only fb/simplefb reads are added. A black screen with
  /dev/dri present is a separate finding, not a hang.
  STATUS (CM, 2026-10-26): the run-4 kit is delivered (worker-2) and
  under Architect + QE review; no grant yet. Open question: whether
  the kit matches RUN-4 v2.
  One-liner (worker-2 via CM, 2026-10-26): the v3 recovery script has
  a missing-newline bug; it is not carried into kit v4.
  RULING (Architect via CM, 2026-10-26): the run-4 kit is NOT
  acceptable as delivered; it armed the dropped R4-0. worker-2
  rebuilds it off the Pi to RUN-4 v2: R4-1 armed with dtdebug=1 and
  cmdline-run4 = r41 + modprobe.blacklist=vc4,v3d; a loadable-module
  precondition; outcomes (i), (ii) and (iii); then a separate CHANGE
  for a live modprobe of v3d and then vc4; an optional greetd go. The
  QE's 5 points and the AE's 3 conditions apply.
  UPDATE (CM, 2026-10-26): the RUN-4 kit v5 is ready (pins e62744a7,
  CM-verified, built off the Pi). It is out for review with the
  Architect, QE, AE and AD. No grant yet.
  Kit v5 review (pins e62744a7…6f2), record copies to the PM:
  - AE: APPROVE (CM, 2026-10-26; verdict file
    /tmp/us172-r4-v5-review/AE-verdict.txt, sha256 6bbaa5b0 at PM
    read). Non-blocking note: an R4-gains FAIL does not block
    tb-modprobe.
  - QE: APPROVE WITH CONDITIONS (QE accounting, 2026-10-26), both to
    be met before the CHANGE 1 grant. C1: an off-Pi test of the new
    gains() parser (ok, FAIL and NOT VERIFIABLE cases), because the
    sandbox stubbed it. C2: tb-modprobe also gates on R4-gains ok and
    R4-gate ok, or the AE rules that this isn't needed. Non-blocking
    notes n1-n3 went to the CM.
  - PM cross-ref: QE C2 and the AE's non-blocking note address the
    same point; C2 names an AE ruling as its alternative. Whether the
    AE note is that ruling is for the QE and AE (via CM).
  - Pending: Architect, AD.
  Deltas (worker-2 via CM, 2026-10-26): 3 differences against the
  relayed v2 spec (dtdebug=1; a 30 s vs 60 s wait; a step-4b greetd
  verb), routed to the Architect for a ruling. If any is ruled in, kit
  v6 follows.
  UPDATE (CM, 2026-10-26): remaining kit v5 verdicts and the
  Architect's delta rulings:
  - Architect: CHANGES REQUESTED, R1-R3
    (/tmp/us172-r4v5-architect-verdict.md, sha256 20de4f1f, verified
    at PM read). The design is approved; the Architect re-approves a
    v6 pin that has R1-R3 with no other change. R1: in tb-modprobe's
    vc4 rc path, split rc 1 (modprobe returned non-zero, Pi alive:
    "FINDING [tb-modprobe] modprobe vc4 failed (<mp-vc4 out>), Pi
    alive", then quick and the MOD reads, no 300 s wait) from rc 2
    (did not return: current path); print the rc. R2: the tb-modprobe
    gate also refuses on any '^(VERDICT \[[^]]*\] )?FAIL' in tb-post;
    whether it also needs '[R4-gains] ok' (vs NOT VERIFIABLE) is the
    AE's call. R3: add 'pidead && hang "after MOD reads (greetd/labwc
    start)" vc4' after the MOD reads and before stream_off. worker-2's
    open points 1-4 all ACCEPTED (overlay_prefix after the dtoverlay
    lines; ignore_loglevel omitted; greetd -> labwc as an observation;
    the hung-task bound).
  - AD: REQUEST CHANGES, M1 medium
    (/tmp/us172-r4-v5-ad-verdict-e62744a7.md, sha256 5a15d301,
    verified at PM read): a short SSH stall during modprobe that
    recovers with the same boot id is classified as outcome (ii), and
    the owner is told to power-pull a live Pi, losing the MOD reads
    and the tryboot. Fix: hang() prints "RESULT [tb-modprobe]
    RECOVERED stall of N s (same boot id), not a hang" with no
    DECISION or power-pull text, then quick(), classifying from
    /sys/module/vc4 and /dev/dri; add sandbox flow L (SSH down ~30 s
    during modprobe vc4, back with the same boot id). L1 low, no
    change required: the R4 boot is blind on HDMI before vc4 (evidence
    only on a UART); the CM asks once whether a UART adapter is on
    hand; the go-text "it should restart by itself" holds only for a
    hung-task or soft-lockup panic (no hard-lockup detector or runtime
    watchdog, O-24). The AD re-reviews only M1 + flow L at the new
    pin.
  - Architect delta rulings (/tmp/us172-r4v5-architect-deltas.md,
    sha256 919fcd36, verified at PM read): D1 dtdebug=1 NOT added
    (tryboot.txt stays config.txt + exactly the 2 declared lines,
    TB4SHA 030489f3; fallback: if tb-post hits "STOP FINDING o/
    overlays NOT applied", the follow-up run adds dtdebug=1 with a way
    to read the log). D2 60 s waits after BOTH modprobes (v2 stands).
    D3 step 4b ADDED as its own verb tb-greetd, run only on a separate
    CM go (announced, owner at HDMI, AE (a)); it refuses unless
    tb-modprobe has outcome (iii) with no STOP/ABORT/FAIL, the same R4
    boot id, greetd not active, one run per run id; "greetd already
    active" (started by the udev rule) is the expected path and needs
    no 4b.
  - QE accounting (2026-10-26): C1 OPEN (the off-Pi gains() parser
    test, ok / FAIL / NOT VERIFIABLE, script sha recorded; before
    CHANGE 1; with v6 it runs on the v6 script, and the QE re-checks
    diff-only). C2: the QE accepts the AE's note as the AE ruling,
    holding only while nothing is connected to any Pi output (reverts
    to the gating form if something is connected).
  - GATE NOT SETTLED (CM, 2026-10-26): the QE reads the AE's note as
    satisfying C2; the Architect says R2 (refuse on any FAIL, a gains
    FAIL included) covers it; the two contradict each other. A joint
    AE + Architect ruling is requested. Whether a NOT VERIFIABLE gains
    reading also blocks is the AE's call (Architect).
  - Next (CM): worker-2 builds v6 off the Pi with R1, R3, M1 + flow L,
    QE C1 (on the v6 script), the QE's n1-n3, D2 and D3. PM cross-ref:
    R2 is not in the CM's v6 list (gate ruling pending). No grant yet.
    AD L1 goes into the go-text.
  - QE verdict file (CM, 2026-10-26):
    /tmp/us172-qe-verdict-v5-e62744a7.md, sha256 363b751d (verified at
    PM read), with the C2 addendum.
  - GATE SETTLED (CM, 2026-10-26; supersedes "GATE NOT SETTLED"
    above): FINAL is the joint AE + Architect ruling
    /tmp/us172-r4-gate-joint.md, sha256 dcec60fa (verified at PM read;
    CM read-only copy
    /tmp/cm-relay/US-172/joint-gate-ruling-dcec60fa.md). The AE and
    the Architect both released this same sha. VOID: c8eb180e (its
    file /tmp/us172-r4v5-joint-gate-ruling.txt is now only a pointer,
    sha256 3d727ca4), and the Architect's earlier release line with
    its two notes (dcec60fa covers tb-greetd and the re-read verb). R2
    is replaced by dcec60fa; the AE's v5 note is superseded.
     Content (ruling text): tb-modprobe (and tb-greetd, D3) refuses
     unless tb-post has both "VERDICT [R4-gains] ok" and "VERDICT
     [R4-gate] ok gate closed" and no STOP/ABORT/FAIL line. (1) Gains
     FAIL: refused, no CHANGE 3, report to the AE, R4 boot left as is.
     (2) Gains NOT VERIFIABLE: refused by default; one re-read allowed
     first as an OBSERVE (new verb tb-gains-reread, at most 60 s
     later, own file, its "ok" accepted in place of tb-post's); or the
     AE releases it with a ruling relayed by the CM
     (US172_GAINS_AE_RELEASE=<ruling sha256>, printed, content not
     checked). (3) Gate not proven closed: refused, no release path.
     Why: CHANGE 3 is run 4's riskiest step, so the audio safety state
     is proven first (AE (c)).
  - QE C2 (CM, 2026-10-26): met by the gate ruling; the QE said either
    outcome satisfies it. C1 still OPEN.
  - v6 (CM, 2026-10-26; supersedes "Next" above, including its PM
    cross-ref on R2): R1 + R3 + dcec60fa + D2 + D3 + AD M1/flow L + QE
    n1-n3 + C1 on the v6 script; relayed to worker-2. No grant yet.
  - Gate release history (CM, 2026-10-26): the Architect first
    released only c8eb180e; the AE's pointer text ("released by the AE
    and the Architect") was written ahead of the Architect's release;
    the Architect then sent the exact line "gate joint dcec60fa
    released" (sha verified). dcec60fa is FINAL, released by both.
  - tb-greetd (Architect-only ruling, re-sent after releasing
    dcec60fa; CM relayed to worker-2, 2026-10-26): tb-greetd also
    REFUSES unless tb-modprobe shows [MOD-gains] ok AND [MOD-gate] ok
    (and no STOP/ABORT/FAIL). The re-read/OBSERVE-verb half of the
    earlier D3 note is dropped (dcec60fa's tb-gains-reread wording
    covers it).
  - QE C2 MET by dcec60fa (CM, 2026-10-26): the QE checked the sha
    against both copies and has no objection. C1 still OPEN.
  - QE v6 gate sim flows G1-G11 (required; CM relayed to worker-2,
    2026-10-26): gains FAIL; NOT VERIFIABLE with or without reread or
    release; gate not ok with no release; a missing line; a stray
    STOP/ABORT/FAIL; a reread later than 60 s; the 4 tb-greetd
    preconditions; the happy path. Each flow records the script sha.
  - Pending (CM, 2026-10-26): the Architect pins the tb-greetd
    [MOD-gains]/[MOD-gate] ruling as a one-line addendum file with its
    sha (CM request).
  - PINNED (CM, 2026-10-26; resolves "Pending" above): the Architect's
    tb-greetd addendum /tmp/us172-r4-tbgreetd-mod-addendum.md, sha256
    762f9035 (verified at PM read on both copies; CM copy
    /tmp/cm-relay/US-172/tbgreetd-mod-addendum-762f9035.md). It adds
    to dcec60fa and does not replace it: tb-greetd needs its own CM go
    plus [MOD-gains] ok and [MOD-gate] ok, with no STOP/ABORT/FAIL;
    otherwise blocked, no release path. Relayed to worker-2 and the
    QE.
  - QE (CM, 2026-10-26): addendum 762f9035 verified, no objection. G10
    refined: G10a (each of the 4 oks missing in turn), G10b (MOD not
    ok with the release env set is still refused), G10c (all 4 ok plus
    a STOP/ABORT/FAIL line is refused), plus a happy path. Relayed to
    worker-2.
  - worker-2 v6 progress (CM, 2026-10-26; not yet pinned): R1, R3, AD
    M1, n1 and n2 done. Flows L and L2 pass with no DECISION line. C1
    pre-results on observe4: (a) ok 8/8, (b) FAIL, (c) NOT VERIFIABLE;
    to be re-run on the final v6 script.
  - FINAL v6 scope (CM, 2026-10-26; one consolidated message to
    worker-2): 919fcd36 D1-D3, gate dcec60fa, addendum 762f9035,
    G1-G11 with G10a/b/c, and C1. ONE v6 pin, not a v7.
  - QE G1-G11 list file (QE, 2026-10-26): /tmp/us172-qe-v6-glist.md,
    sha256 719fa398 (verified at PM read). worker-2 has the final
    scope again (CM): all in v6, no v7.
  - OPEN (CM, 2026-10-26): the AE lists the Architect's re-release of
    the dcec60fa gate as pending; the CM's record says both released
    it. The CM has asked the AE. No v6 grant until that is settled.
  - SETTLED (CM, 2026-10-26; resolves "OPEN" above): the AE says
    "nothing missing"; its "pending" note was stale. dcec60fa is
    released by both; the Architect has not amended it; 762f9035 is
    additive. No obstacle to the v6 grant from the gate side.
  - Pi order (CM, 2026-10-26): the #63 DEPLOY plus P-steps (QE C4)
    runs before US-172 v6 (see #63). Team-lead's conditions: v6 keeps
    priority; the Architect confirms no base change; the AE clears it.
  - UPDATE (CM, 2026-10-26; supersedes the "Pi order" line above): Pi
    order (team-lead ruling; supersedes "deploy-first is ON"): US-172
    v6 runs FIRST on the current generation rcyg67wd, THEN the #63
    DEPLOY plus P-steps (QE C4). Condition 2 (the Architect confirms
    no v6 base change) failed. Architect reason: a #63 `nixos-rebuild
    boot` writes a new gens/<id>/ and rewrites config.txt, which
    breaks v6's pins (BASE_TOP, CFGSHA ff08471f, CMDSHA c28e6a4e,
    C4SHA 337c7d5c, TB4SHA 030489f3, the FAT manifest, the tryboot
    draft os_prefix) and its pwdump BEFORE baseline; v6 would then
    need a re-pin, a new OBSERVE baseline and a re-review. The pins
    fail closed (STOP), so it is not a safety issue, but v6 could not
    run.
  - UPDATE (CM, 2026-10-26, after v256): v6 is pinned at us172.sh
    fc65bcad; 82113c3f is VOID. Re-reviews open: the Architect, the
    AD, the QE and the AE. The full flow run finishes around 15:35Z
    (CM).
  - UPDATE (CM, QE, 2026-10-26, after v257): fc65bcad is SUPERSEDED. A
    v7 re-pin is required, superseding "ONE v6 pin, not a v7" above,
    because the QE marks Q1 and Q2 REQUIRED (QE review points on
    fc65bcad, /tmp/us172-qe-v6-points-fc65bcad.md, sha256 61db85d1,
    verified at PM read; not the final verdict). C1 is MET on
    fc65bcad.
     Q1 (REQUIRED): in r4gate's NOT VERIFIABLE branch, a reread file
     that exists but is not ok falls through to the
     US172_GAINS_AE_RELEASE test, so a reread gains FAIL (dcec60fa
     case 1) or gate STOP (case 3) is ACCEPTED when a release is set.
     Fix: refuse on any ^(VERDICT \[[^]]*\] )?(STOP|ABORT|FAIL) line
     regardless of the release. New flows G4b, G4c (REFUSED) and G4d
     (ACCEPTED, release sha printed).
     Q2 (REQUIRED): tb-modprobe can print "outcome (iii)" after a
     MOD-gains FAIL (its regex matches STOP only). Not a gate hole
     (tb-greetd still refuses), but wrong evidence on an audio-safety
     read. Fix: (iii) also requires no ^((VERDICT|RESULT) \[[^]]*\]
     )?(STOP|ABORT|FAIL) line, otherwise the FINDING branch. New flow
     G12.
     v7 also takes the Architect's P3 rc-path-3 flows and AE point 3
     (a FINDING line in tb-greetd) (CM).
     QE O1 (optional-prefix regex: any bare "FAIL ..." line in the MOD
     reads, e.g. "FAIL no HDMI device/node in PipeWire", blocks
     tb-greetd; literal 762f9035 conformance, fails closed; making
     them informational is a ruling change) is with the Architect
     (CM).
     QE final verdict needs the re-pinned kit and the flow output sha:
     G1-G11, G1b, G4b/c/d and G12, each with script sha, input shas,
     exit status and stub call counts, plus C1 on the new pin.
     Grant conditions on file (CM): Architect P1, no tb-greetd go
     while there is a tb-modprobe FINDING unless the Architect clears
     it in a file; Architect P2, "labwc up" is not proof of hardware
     GL.
  - Priority rule (team-lead, via CM): no re-pin for non-blocking
    points. Points nobody marks BLOCKING go to the backlog as
    one-liners.
  - One-liner (QE N1, non-blocking, on fc65bcad): tb-greetd's pre-gate
    refusals (no CM go, no outcome (iii), wrong boot, greetd active)
    are not written to us172-gate-refusals-<T>.txt; tb-modprobe's
    pre-checks behave the same way. "Optional" (QE). No F-ID, no
    P-level given.
  - UPDATE (CM, AE, 2026-10-26, after v258): QE O1 settled. Architect
    ruling (by message, per CM relay; no ruling file): "intended, no
    change"; any bare FAIL line from the MOD reads blocks tb-greetd,
    with no release path on the R4 boot; a new HDMI node after vc4 is
    a real finding for the AE and the Architect. No joint ruling.
    Architect (per CM): an HDMI audio node is UNLIKELY because of 3
    layers: the noaudio overlay, the [R4-hdmi-dmas] pre-read, and WP
    54-disable-other-alsa-cards.
     AE input (NOT a verdict;
     /tmp/cm-relay/US-172/v6-fc65bcad/frozen-AE-v7-Q1-O1-input-e5996f08.txt,
     sha256 e5996f08, verified at PM read): Q1 "matches my intended
     release semantics exactly, no change"; Q2 "agreed". On O1 the AE
     offered an informational alternative under four conditions and,
     verbatim: "If the Architect keeps literal conformance (fail
     closed), I have no audio objection. It only costs a run."
     Grant and go conditions r1 (CM;
     /tmp/cm-relay/US-172/grant-conditions-v7-r1.txt, sha256 6c6308f5,
     verified at PM read): G-1 Architect P1 (bf9f8201), no tb-greetd
     go while the tb-modprobe file has any FINDING line unless the
     Architect clears it in a file; G-2 Architect P2, "labwc up" alone
     is NOT proof of hardware GL; G-3 (new, Architect O1 follow-up, by
     message) no tb-modprobe go if tb-post's [R4-hdmi-dmas] read shows
     "present"; G-4 tb-gains-reread is OBSERVE in the session,
     worker-2 may run it at once on tb-post's NOT VERIFIABLE NEXT
     line, 60 s window stays; G-5 = the O1 ruling above (AE no
     objection, e5996f08); G-6 standing rules (one CHANGE session;
     thermal WARN >=75 C, STOP >=80 C; owner at HDMI before any
     tryboot or modprobe go; recovery = power pull; unbootable
     generation = SD card fix on the Mac). Any change goes in a new
     file.
     CORRECTION (CM, 2026-10-26, after v259; supersedes "by message,
     per CM relay; no ruling file" above): the Architect's two O1
     messages are recorded verbatim in
     /tmp/cm-relay/release-record-20261026-f.txt (sha256 57ee3eb8,
     verified at PM read). Message 2 gives the 3 layers: (1)
     tb-modprobe runs only after H1 PROVEN, so
     dtoverlay=vc4-kms-v3d-pi5,noaudio is applied and vc4 registers no
     HDMI audio; (2) tb-post reads [R4-hdmi-dmas] before any modprobe;
     (3) WirePlumber 54-disable-other-alsa-cards.conf. Architect,
     verbatim: "No joint ruling is needed. Please pass the dmas
     pre-check in (2) on as a CM go condition for tb-modprobe." That
     condition is G-3.
  - UPDATE (CM, 2026-10-26, after v267): the owner asked for US-172
    status via team-lead. The v7 pins are not yet in; the CM has sent
    worker-2 one status ask.
  - UPDATE (CM, Architect, 2026-10-26, after v268): v7 kit pinned
    (us172.sh 815d231e). Architect PRE-REVIEW, not the verdict:
    frozen-prereviews/architect-prereview-a1660f61.txt in
    /tmp/cm-relay/US-172/v7-815d231e/ (sha256 a1660f61, verified at PM
    read). Verbatim: "NOTHING BLOCKING, NOTHING REQUIRED." Position,
    verbatim: "APPROVE expected on the frozen flow output, if G1-G13
    (incl. G1b, G4b/c/d, G12, G13b/d and the rc-path-3 flows for both
    verbs) show the classifications above."
     Later-kit one-liners (non-blocking; no re-pin, per the team-lead
     ruling; no P-level given):
     (1) l.24, verbatim: "Backlog (PM): in a later kit, make (iii) and
     "labwc up" exclude FINDING lines, so the result line itself is
     qualified." For this run, l.23, verbatim: "CM relay rule: a
     RESULT line in a file that also has a FINDING line is relayed
     only together with that FINDING."
     (2) l.31, verbatim: "Backlog (PM): exit status = classification
     (0 = (iii) or labwc up, non-zero otherwise) in a later kit."
     Context, l.29: "So the exit status is NOT evidence for any
     outcome."
     (3) N1, l.34-36, verbatim: "tb-greetd au flag: au is set only if
     some "VERDICT [GREETD-" line exists. If the GREETD reads printed
     no verdict at all (both remote scripts failed), au stays 0.
     "labwc up" could then print with no audio read on record.
     Fail-closed form for a later kit: au=1 unless both [GREETD-gains]
     ok and [GREETD-gate] ok are present." For this run, l.37,
     verbatim: "the CM treats a tb-greetd file without a
     [GREETD-gains] line as not ok (report to the AE), whatever the
     RESULT says."
     Also in the file (PM cross-ref; not in v268): N2, l.38, verbatim:
     "(from v6) capped() rc 2 leaves the background ssh pending.
     Harmless."
  - UPDATE (CM, QE, AE, AD, 2026-10-26, after v269): the other v7
    pre-reviews, frozen in
    /tmp/cm-relay/US-172/v7-815d231e/frozen-prereviews/ (each sha256
    verified at PM read): qe-prereview-1b7da488.md (identical to the
    QE's /tmp copy), ae-prereview-ef57ad7e.txt,
    ad-prereview-56bb31f2.md. None is a final verdict; each waits for
    the flow output.
     QE: v6 Q1 and Q2 CLOSED. REQUIRED Q3 (one re-pin): tb-greetd
     prints "labwc up" when the GREETD audio read is missing. QE fix,
     verbatim: "`au=1` unless BOTH `^VERDICT \[GREETD-gains\] ok ` and
     `^VERDICT \[GREETD-gate\] ok gate closed` are present (drop the
     "a GREETD line exists" precondition)", plus new flow G14c. QE,
     verbatim: "The AE owns the meaning of point 3. If the AE rules
     that a missing read is acceptable, Q3 drops. QE expects it
     isn't." If the pin changes, the 815d231e run "only counts as a
     dry run". OPEN (CM).
     PM cross-ref (not a ruling): Q3 is the defect the Architect
     classed non-blocking as N1 (a1660f61) and the AD classed REQUIRED
     as P2, with a kit fix or grant condition. The AE's N3 says,
     verbatim: "gains() always prints one, so there is no gap now."
     The QE and the AD name a crash case (invalid pw-dump JSON) in
     which no verdict prints. For this run, G-8 covers it (below).
     Grant conditions r2:
     /tmp/cm-relay/US-172/grant-conditions-v7-r2.txt (sha256 667688ef,
     verified at PM read; r1 6c6308f5 unchanged). G-7 (AD P1 option
     (b); release owner Architect, PENDING): a (iii) or "RESULT labwc
     up" line in a file with any FINDING line for that verb is relayed
     only as "(iii)/labwc up WITH FINDING, Architect classifies". G-8
     (AD P2 option (b); release owner AE): "RESULT labwc up" is
     relayed only if the tb-greetd file contains both "VERDICT
     [GREETD-gains] ok " and "VERDICT [GREETD-gate] ok gate closed".
     G-8 RELEASED by the AE: record (j)
     /tmp/cm-relay/release-record-20261026-j.txt (sha256 3390726a,
     verified at PM read). AE, verbatim: "G-8 closes my N3 for this
     run, so no v8 is needed." The kit fixes behind G-7 and G-8 are
     later-kit backlog items (CM).
     Later-kit one-liners (all non-blocking, no re-pin; no P-level
     given):
     QE N1 (l.45): the reread STOP regex is narrower than the
     (VERDICT|RESULT) prefix tb-modprobe/tb-greetd use; "no hole, only
     an inconsistency." QE N2 (l.46): tb-modprobe's (iii) "does not
     itself require MOD-gains ok / MOD-gate ok to be present"; "a
     classification nicety only". QE N3 (l.47, carried from v6 N1):
     pre-gate refusals don't go to us172-gate-refusals-<T>.txt.
     AE N1 (l.44): the r4gate() branch 3 regex has no RESULT prefix;
     "align them in a later kit." AE N2 (l.46): "hang() outcome (ii):
     exit non-zero (worker-2 b)." AE N3 (l.47): tb-greetd au "is armed
     only if some [GREETD-*] VERDICT line exists ... A later kit could
     require both ok outright for "labwc up"." PM cross-ref: AE N2 =
     Architect (2) (exit status); AE N3 = Architect N1 = QE Q3.
     AD L1 (Low section): verbs exit 0 for every outcome; "Backlog:
     derive the exit status from the final classification." AD L2:
     "Each is correct today. Backlog: one shared helper so the regexes
     cannot drift." PM cross-ref: L1 = Architect (2) = AE N2; L2
     overlaps QE N1 and AE N1. The AD also sent L1 and L2 to the PM by
     message.
  - UPDATE (CM, QE, Architect, AD, 2026-10-26, after v270; supersedes
    "OPEN (CM)" on Q3 and "PENDING" on G-7 above): all v7 pre-review
    points CLOSED. No re-pin; 815d231e stands.
     QE Q3 CLOSED, record (l)
     /tmp/cm-relay/release-record-20261026-l.txt (sha256 6b48b8cc,
     verified at PM read). QE, verbatim: "Q3 closed by G-8 667688ef
     (sha verified at read). It applies to this run only. My final
     verdict will check G-8 against the real tb-greetd file: no
     labwc-up relay unless both GREETD ok lines are in it. The kit fix
     and the G14c flow stay in the PM backlog for the next pin."
     Record (l), verbatim: "815d231e stands and worker-2's current
     flow run counts." So the run is not a dry run.
     G-7 RELEASED by the Architect, record (k)
     /tmp/cm-relay/release-record-20261026-k.txt (sha256 c5167e60,
     verified at PM read). Architect, verbatim: "I choose the grant
     condition, not the kit fix, so there is no v8 and no re-pin. G-8
     is the AE's to release." With record (j), grant-conditions-v7-r2
     (667688ef) is fully released.
     AD closure: frozen-prereviews/ad-closure-g7g8-532ecf7c.md (sha256
     532ecf7c, verified at PM read). AD, verbatim: "G-7 closes P1."
     and "G-8 closes P2." The AD accepts the exit-status note as
     covering L1 for this run. "This is not my final kit verdict; that
     follows the flow output."
     PM cross-ref (resolves the v270 cross-ref): with G-8 released and
     Q3 closed by it, the QE, Architect, AD and AE positions on the
     missing-read defect agree for this run. Next-pin one-liner (QE,
     no P-level given): the Q3 kit fix (au=1 unless both GREETD ok
     lines are present) plus flow G14c.
  - UPDATE (QE, AE, AD, Architect via team-lead and CM, 2026-10-26,
    after v271): v7 kit FINAL VERDICTS, all APPROVE, none blocking.
    Frozen in /tmp/cm-relay/US-172/v7-815d231e/frozen-verdicts/ (each
    sha256 verified at PM read): qe-final-a8ba08b0.md,
    ae-final-3c8a1377.txt, ad-final-03e27ea5.md,
    arch-final-372a73a1.txt. Basis: flow output flows-all-5fae86c0.out
    (572 lines) and grant conditions r2 667688ef.
     AD, verbatim: "This approval binds to 815d231e together with
     5fae86c0 and 667688ef. A re-pin voids it." QE: G13b/d "PASS under
     G-7"; Q3/G14c "closed for this run by G-8". Architect CM NOTE
     ("not a condition change"): the sim's k() filter drops "ok"
     VERDICT lines, so "On the Pi, check G-7 and G-8 against the full
     us172-tb-greetd-*.txt / us172-tb-modprobe-*.txt files, never
     against a filtered or console view."
     Run conditions restated: QE: "US172_GAINS_AE_RELEASE is set only
     to the sha of an actual AE ruling file"; the CM checks that sha
     against a frozen AE file before setting it. AE (standing):
     nothing connected; amps and HP/IEM off; warn before any
     USBStreamer interruption; "Any "report to the AE" line comes to
     me before the next step on that boot."; G-8 at relay.
     Not independently verified (QE and AD): worker-2's claim that
     flows A-O (AD: and G1-G11) match the v6 fc65bcad run. AD,
     verbatim: "The v6 flow output is not in /tmp/cm-relay/US-172/."
     Later-kit one-liner AE N4 (wording, non-blocking; no P-level
     given), verbatim: "in G14a/b, the kit's last FINDING still says
     "labwc not up (or ... the audio-read FINDING above)", although
     labwc is up. The audio-read FINDING above it is the operative
     line. A later kit could word it "no labwc-up result"." The AD
     notes the same wording: "When relaying, the CM should quote the
     OBSERVATION line as well."
  - UPDATE (Architect via CM, 2026-10-26): run 4 CLOSED. Ruling r4
    /tmp/cm-relay/US-172/frozen-rulings/run4-B1-ruling-r4-1816176e.txt
    (sha256 1816176e, verified at PM read), applying the r3 decision
    rule (a40a97e0). Verbatim: "DECISION: (c). Run 4 is closed. Next
    comes a v8 kit that bisects the boot (run 5), through the normal
    pin and review. No tryboot reboot of any kind before that."
     Findings (PM summary): F1 the tryboot request path is intact
     (kernel symbols present; GET_REBOOT_FLAGS answered; systemd 258.3
     issued "systemctl reboot --reboot-argument=0 tryboot" and nothing
     rejected it). F2 a plain reboot is down 6.2 s (bounded 12.9 s),
     run 4 was down 26.4 s (bounded 33.4 s). F3 rsts = 0x420 on the
     plain reboot too, so it is dropped as evidence. Conclusion,
     verbatim: "(strong inference, not proof): the bootloader DID
     start a tryboot pass in run 4. That boot failed within roughly
     15-25 s and the Pi reset, and the next pass (tryboot is one-shot)
     booted config.txt." Not yet separable: (K) the kernel panicked
     early and panic=10 reset it, or (F) the bootloader failed in the
     tryboot pass.
     Run 5 design (worker-2 drafts v8, the Architect reviews; G-1..G-8
     carry over unless the review says otherwise; one change per
     tryboot reboot, each with a new run id and gated on the previous
     step's file): R5a "null tryboot" (tryboot.txt = config.txt except
     cmdline=cmdline-r5a.txt, which adds "us172r5=a panic=60"; if R5a
     fails, stop and rule before any overlay step); R5b only after R5a
     is TRYBOOT (R5a + overlay_prefix=o/ plus the run-4 blacklist and
     panic tokens, with panic=60); R5c/R5d only if R5b fails (one
     overlay each). panic=60 makes the signature readable: (K) about
     75-85 s down, (F) about D_plain + 15-25 s, a hang beyond the
     kit's 300 s DECISION. Owner brief (G-6, at HDMI), verbatim: "If
     the screen goes dark for about a minute and then the Pi logo
     comes back, that is expected for a failure. Tell us whether it
     happened."
     Kit points for v8 (Architect): the tb-reboot classifier reports
     the measured down window in its file (r3 method), so a
     NOT-TRYBOOT carries its K/F/plain signature; per-step expected
     cmdline and tryboot.txt diffs are pinned by sha. Optional
     (worker-2, read-only, no installs): a Pi 5 ramoops dtbo in the
     base closure's overlays dir, proposed for R5b so a panic log
     survives in /sys/fs/pstore; if none, skip it. Architect: "No
     owner decision needed."
  UPDATE (CM, 2026-10-26, after v292): v8 kit c96afb79
  (/tmp/cm-relay/US-172/v8-c96afb79) is in review with the Architect,
  the AE and the QE; worker-2 acked c96afb79 (per the PROCESS RULE).
  Verdicts: not yet relayed to the PM at this version.
  UPDATE (CM, 2026-10-26, after v293; supersedes "not yet relayed"
  above): v8 c96afb79 verdicts relayed. QE: PENDING at this version.
  Files in /tmp/cm-relay/US-172/frozen/, sha256 verified at PM read.
  AE VERDICT: APPROVE (audio side). ae-v8-verdict-96cf081b.txt (sha256
  96cf081b, 1582 bytes). Verbatim, reflowed, without its title line
  ("AE verdict: US-172 v8 bisect kit (run 5, steps a-d, Architect r4
  1816176e)"):
  - Kit: /tmp/cm-relay/US-172/v8-c96afb79/, manifest sha256
    c96afb79ec8c25b5c4ae0979aa7fbb815a32a28b6109e102a9daf7891bfabec0
  - Verified at read time: all 29 files OK; us172.sh 5100d29f,
    us172-drm-reads.sh d23d752b.
  - VERDICT: APPROVE (audio side).
  - CM question (tb-gains-reread dropped, G-1/3/5/7/8 vacuous): I do
    NOT need the gains re-read back as a separate verb.
     - tb-post calls `reads R5` in the R5 boot (same-boot check vs
     r5-boot-id). That covers the full audio set (AC14/AC19: 16 gains
     0, gate closed, FF/88, 24 links, sink running) plus the
     F-395-form gains read (node state logged before/after, 8 Mult =
     0.000000, nodes 1+1 running, gate via GM 4002 get_gate) and "no
     HDMI node in PW".
     - return-obs requires RETURN-gains ok + RETURN-gate ok, else STOP
     "no next step, report to the AE" (AE c).
     - tb-pre refuses unless PRE gains + gate are proven (F-395).
  - So G-1/3/5/7/8 are carried by these reads; vacuous G-items are
    fine.
  - Conditions (observation only, no kit change required):
  - C1. If any R5 reads line shows gains or gate not proven: report it
    to me with the tb-post log; tb-restore and the return still
    proceed (they produce no audio). No next R5 step until return-obs
    gives AE (c) ok.
  - C2. No audio-producing action (signal-gen, unmute, gain change,
    profile activation) in any R5 boot. OBSERVE only, as written.
  - C3. dtparam=audio=off stays in every tryboot file (verified in
    a-d). R5c/R5d overlay drops are not audio paths.
  - C4. "Nothing connected" stands (owner); reboots are announced, not
    waited on.
  ARCHITECT VERDICT r1: APPROVE. arch-v8-verdict-r1-fafd59fc.txt
  (sha256 fafd59fc, 4109 bytes). Verbatim, reflowed, without its title
  line ("US-172 run 5, v8 kit: Architect VERDICT r1 (2026-10-26).
  Reviewed against my ruling r4 1816176e."):
  - Read at the frozen CM copy /tmp/cm-relay/US-172/v8-c96afb79/,
    manifest c96afb79 (all files OK at read time): us172.sh 5100d29f
    (full file read, not only the diff), us172-drm-reads.sh d23d752b,
    config.txt.base.template c2a461c8, pins.sha256 + 8 pin files,
    pins-vs-base.diff, render.sh.
  - VERDICT: APPROVE. The kit implements the r4 run-5 design. No
    blocking points.
  - Checked against r4
     - R5a: tryboot.txt = config.txt except for
     cmdline=cmdline-r5a.txt. cmdline = base + "us172r5=a panic=60".
     No o/, no overlay_prefix, no blacklist. The expected DT state is
     the exact base state, and overlay_prefix is the base
     gens/<id>/overlays/.
     - R5b: R5a + overlay_prefix=o/, placed directly after os_prefix
     (machine-checked), plus blacklist, softlockup_panic and
     hung_task_panic, with panic=60.
     - R5c/R5d: one dtoverlay line dropped each; pinned by sha, with
     the exact line diffs machine-checked.
     - TRYBOOT = flag 1 + marker (b/c/d also need the blacklist).
     - The r3 down-window MEASURE line is written into the verb's
     file.
     - Each step has a new run id and is gated on the previous step's
     files.
     - An R5a failure stops the chain ("stop and rule").
     - R5c/R5d run only if R5b fails.
  - Rulings on worker-2's open design points (mine)
  - 1. c/d drop one dtoverlay line and keep the same 5-file o/:
    ACCEPTED, and better than varying o/. Each step then differs from
    R5b by exactly one config.txt line, and o/ stays sha-identical to
    run 4.
  - 2. Marker us172r5=<S> in every step, including a: ACCEPTED (r4
    asks for it). Without the marker, R5a cannot be told apart from a
    normal boot.
  - 3. Ramoops: read-only pstore reads only, no ramoops in any R5
    step: ACCEPTED. Adding it to R5b would be a second change in that
    step. If R5b fails K-like with nothing persisted, worker-2 may
    send a ramoops setup as a proposal for a later step.
  - 4. The c gate counts R5b NOT-TRYBOOT or FAIL outcome (i) as a
    fail, and any STOP blocks the chain: ACCEPTED. An R5b TRYBOOT with
    a tb-post STOP (e.g. "o/ overlays NOT applied") correctly blocks c
    and comes to me. My classification of R5b is NOT a precondition
    for c (the kit gate + CM grant suffice), but the CM sends me the
    R5b files at the same time as the c grant.
  - 5. Step a expects panic=60, softlockup_panic=0, hung_task_panic=0:
    ACCEPTED as is. Non-blocking note N1 below.
  - 6. MEASURE uses the ping-return basis as primary and prints the
    send basis too: ACCEPTED. The refs (D_plain 6.2 s, run 4 26.4 s)
    were measured on the return basis, so the bases match. The kit
    prints OBSERVATION bands only; I classify. Note: a hung-task panic
    (timeout 120 s + panic 60 s) lands at about 190-200 s, in the
    "unclassified" band below the 300 s DECISION. That is expected; I
    classify it.
  - 7. A T-bounds FINDING does not block the T-R5 RESULT: ACCEPTED. An
    inert bound only changes the recovery path (power pull with the
    owner at HDMI), not the evidence.
  - 8. tb-normal after any STOP needs US172_CM_GO=1: ACCEPTED.
  - 9. GATE lines truncated at 60 characters: ACCEPTED (cosmetic).
  - The dropped verbs tb-gains-reread, tb-modprobe and tb-greetd: no
    objection from me, since run 5 makes no CHANGE in the R5 boot. The
    AE rules on them.
  - Non-blocking notes (no new kit version needed; fold them in only
    if v8 is reworked for another reason)
  - N1 Step a: the softlockup_panic/hung_task_panic expectation should
    be "== the PRE normal-boot value" rather than a hard-coded 0
    (their defaults depend on CONFIG_BOOTPARAM_*). A mismatch is a
    FINDING only, so the run is unaffected.
  - N2 Every tb-normal MEASURE line is a fresh D_plain sample. When I
    classify, I use the per-step D_plain next to the 6.2 s reference.
    This needs no kit change.
  - Sim: setup 30f84dd9 / flows ac416ce3 / drm-sim ad09f683, r2
    outputs eec2d7df (12 entries). Both bugs found in the sim (the
    tb-diag slot used up before a refusal, and tb-normal after a
    tb-reboot STOP without GO) are fixed in 5100d29f. I checked the
    fixes in the code: the REFUSED checks come before the OUT file is
    created, and the STOP/GO check is in tb-normal.
  QE VERDICT (QE, CM relay, 2026-10-26): APPROVE, with two binding CM
  run conditions (C1, C2); no re-pin needed.
  /tmp/cm-relay/US-172/frozen/qe-v8-verdict-38663487.md (sha256
  38663487, 5895 bytes, verified at PM read; QE accounting copy
  /tmp/us172-qe-v8-verdict-5100d29f.md, same sha). With AE 96cf081b
  and Architect fafd59fc: 3/3 APPROVE on c96afb79 (CM). The
  non-blocking code fix is filed as F-412 (P2). Verbatim, reflowed,
  without its title line:
  - Kit: /tmp/cm-relay/US-172/v8-c96afb79/, MANIFEST-v8.sha256
    c96afb79. All 29 files verified at read time.
  - Ruling: Architect r4 1816176e, decision (c).
  - Code under review: us172.sh 5100d29f, us172-drm-reads.sh d23d752b.
    Sims: setup 30f84dd9, flows ac416ce3, drm-sim ad09f683.
  - Evidence: /tmp/us172-t8sim-out-r2-5100d29f/. All 12 files match
    sim-out-r2-5100d29f.sha256 (eec2d7df).
  - ## VERDICT: APPROVE, with two binding CM run conditions (C1, C2).
    No re-pin needed.
  - ## What I checked
  - 1. **v7 to v8 diffs.** The v7 base equals the frozen 815d231e. The
    v7->v8r1 and v8r1->v8 diffs match the files.
  - 2. **Pins against the run-4 base.** I diffed these myself:
    orig-config/restored-config ff08471f and cmdline.txt c28e6a4e,
    from ~/mugge-pi5-prewipe-20261024/us172-run-20261026T134852Z. The
    results match pins-vs-base.diff and r4 exactly:
     - R5a: only cmdline=cmdline-r5a.txt, plus the tokens us172r5=a
     and panic=60. There is no overlay_prefix, so it is a true null
     tryboot.
     - R5b: R5a plus overlay_prefix=o/, modprobe.blacklist=vc4,v3d,
     softlockup_panic=1 and hung_task_panic=1.
     - R5c: R5b minus dtoverlay=disable-bt-pi5. R5d: R5b minus
     dtoverlay=vc4-kms-v3d-pi5,noaudio.
     - All 8 pin shas match pins.sha256. In flow H, the sim pre-obs
     renderings for r5a are equal to the pins.
  - 3. **Gate chain (us172.sh:84-100)** matches r4:
     - a needs the run-4 restore plus the anchor.
     - b needs R5a TRYBOOT and "VERDICT [R5-R5] RESULT R5a".
     - c is refused if R5b was TRYBOOT, and needs R5b NOT-TRYBOOT or
     FAIL outcome (i).
     - d needs any R5c result.
     - Any STOP in the previous step's tb-reboot, tb-post, return-obs
     or restored files blocks the next step.
     - The flows confirm it: A (c refused after R5b TRYBOOT), B (b
     K-like, then c, then d), D (R5a fail, so b refused), E/E2/I (FAIL
     (i), then the next step), F/F2 (a STOP blocks the next step).
  - 4. **r1->r2 fixes verified in the outputs:**
     - A refused tb-diag no longer uses up the step-2 slot (flow C: no
     CSHA and a wrong CSHA are refused, then the correct one proceeds,
     then a repeat is refused).
     - tb-normal after a STOP needs US172_CM_GO=1 (flows F and F2).
  - 5. **Refusals (flow C).** All 17 cases refuse as intended: no or
    bad STEP, out-of-order verbs, repeats, no go, return-obs without
    kind.
  - 6. **N1 disarm (flow G).** An extra FAT file and a failed mv both
    remove tryboot.txt, and tb-reboot is then refused.
  - 7. **pre-obs/tb-pre negatives (flow H).** All STOP/FAIL as
    intended.
  - 8. **drm-reads (17 cases).** All four expected results come out as
    RESULT. Each single-fault case comes out as STOP or FAIL: o/ not
    applied, wrong bt, wrong kms, a-overlays, flag 0, wrong cmdline,
    vc4 loaded or /dev/dri present, a restored r5b cmdline, a bad
    step. The pre oracle self-test is ok.
  - 9. **MEASURE bands:** plain <= 16 s, F 16-45 s, K ~60-120 s. The
    45-60 s range is unclassified, which is fine because the Architect
    classifies. A down window after the DECISION line is correctly
    reported as "not a signature" (E2).
  - ## Binding run conditions (the CM checks these from the step
    files; no code change)
  - **Finding QE-v8-1: TRYBOOT is decided by absence.**
     - In waitup (us172.sh:264-271), the second SSH probe `k` decides
     the boot type. If that call returns nothing or only an ssh error
     (it runs with 2>&1), then f1=0, any=0 and bl=0, and the boot is
     classified "NOT-TRYBOOT (flag 0, base cmdline)".
     - return-obs has the same pattern (us172.sh:443): if the cmdline
     grep fails over SSH, it prints "ok normal boot".
     - tb-restore does not require a return-obs run, and gate c
     accepts R5b NOT-TRYBOOT on the tb-reboot line alone.
     - Result: one transient SSH failure right after boot, in a real
     R5b boot, would open R5c/R5d and give a false "R5b failed" bisect
     result.
     - No sim flow covers an empty probe.
  - **C1.** Before acting on any tb-reboot `RESULT ... NOT-TRYBOOT`
    line (and before relaying it as a result), the CM checks the raw
    probe block printed right above it. It must contain all four of:
     - `tryboot flag` followed by exactly 8 hex digits;
     - a `marker:` line;
     - a `blacklist:` line;
     - a cmdline line containing `init=/nix/store/`.
  - If any one is missing, the classification is INCONCLUSIVE: report
    it to the Architect and do not run tb-restore yet. If the Pi is
    still in the R5 boot, return-obs can establish the real state.
  - **C2.** For every NOT-TRYBOOT or FAIL outcome (i), return-obs is
    mandatory before tb-restore. It is read-only and can be repeated.
     - The CM accepts its "ok normal boot" only if the same output
     also shows the boot_id/uptime lines, a `tryboot flag` line with 8
     hex digits, and a non-empty list-boots block.
     - Otherwise the CM re-runs return-obs.
     - A next step (c or d) may start only once a return-obs file
     meeting this condition exists for the previous step.
  - **Recommended code fix (non-blocking; fold it into any later
    revision):**
     - waitup should require the four positive lines (retry the probe
     up to 3 times, then STOP inconclusive).
     - return-obs should test a fetched, non-empty /proc/cmdline
     rather than the grep exit code.
     - gate c/d should require a return-obs file without a STOP
     whenever the previous step was NOT-TRYBOOT or FAIL (i).
     - Add a sim flow with an empty probe.
  - ## Non-blocking cosmetic notes
     - MEASURE prints "D=-0.0 s" (e.g. flow A tb-normal) and "bounded
     nan s (last ping ok none)" (flow B b, flow E a) when the ping log
     has no earlier ok sample. Neither affects classification.
     - drm-sim case "a, but the r5b cmdline": T-R5 says "STOP
     NOT-TRYBOOT" although flag=1. The STOP is correct; the label
     should say wrong-step or inconsistent.
     - drm-sim "b, bounds not active": the result is RESULT R5b PROVEN
     plus a T-bounds FINDING. That is acceptable, because the bounds
     affect recovery only and the FINDING is visible. The Architect
     should note it if it ever happens on the Pi.
  - G-1..G-8 carry over unchanged from v7 (my v7 verdict a8ba08b0).
  STEP-a GRANT (CM, 2026-10-26): CHANGE-US172r5a r1 (exclusive) to
  worker-2, /tmp/cm-relay/US-172/grant-CHANGE-US172r5a-r1.txt (sha256
  60369f8f, 3727 bytes, verified at PM read). Basis: 3/3 APPROVE on
  c96afb79. PM summary: step 0 is a one-line ack naming the grant sha
  + 96cf081b + fafd59fc + 38663487 and confirming no earlier session
  is open (CHANGE-US172r4 RELEASED 2026-10-26T20:12:50Z). Granted now:
  Phase A1, "US172_STEP=a us172.sh pre-obs (OBSERVE)", then STOP and
  report. A2 (tb-pre, tb-diag; the tryboot is ARMED, not triggered)
  only after a CM go with the checked US172_CSHA. Phase B (tb-reboot
  only after the owner says via team-lead that they are at the HDMI
  screen; tb-post; NOT-TRYBOOT / FAIL (i) / hang per the kit and QE
  C1/C2; tb-restore; tb-normal) needs a CM go per item. Step b is NOT
  part of this grant. Binding: AE C1-C4, QE C1/C2, thermal WARN >= 75
  C, STOP >= 80 C; complete output files only.
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
  SUPERSEDED (2026-10-26): "US-174d sets the convolver to 2100" above
  is dropped; under the AE's model (1) the F-318 hook keeps both the
  USBStreamer and the convolver out of the default sink (see amps-on
  row 18 AMENDED, US-174d Addendum 5).
  New verify AC (AE, via CM, 2026-10-26): the default sink is not a
  protected node, and the F-318 hook shows in the journal; a violation
  is P1.
  UX condition (2026-10-26) MET: the F-318 operator note (expected
  message, how to make sound, never link by hand) and the signal-gen
  as the sanctioned speaker check are already on the branch at
  1c2d4bef (SETUP-MANUAL.md l.1936-1965, safety.md F-318 rule
  l.67-90); no new batch. UX also asked the AE to check in the session
  evidence that Mixxx and Reaper show no error dialog when JACK
  self-connect is refused; if they do, the operator note gets one
  "expected at startup" line. The UX wording gaps (a) and (b) went to
  the AE and land in TW batch v19, not US-173 (see F-318).
  UPDATE (CM, 2026-10-26): pushed at 2a180966 = e7ab322f (M2: zero.wav
  sha256 97b9d9db, .gitignore negation), 2e65e58d (profile AUX3
  comment), 2a180966 (.gitignore comment). worker-3's M2 test
  implements the AE's A/B/C in full with local helpers; the AE ruled
  verify_mandatory_hpf NOT equivalent (average vs max reference, point
  vs band). Finding: configs/venues/markaudio-ultimax-200hz.yml ch4 is
  still dirac.wav; fence granted to worker-3 (ch4 plus comment only),
  AE delta look.
  JOINT ruling, merge condition (Architect, AE, via CM, 2026-10-26):
  jack.self-connect-mode = ignore-external in
  80-jack-no-autoconnect.conf, plus a real-PW test: an ignored connect
  returns 0 with no link; an allow-mode positive control; a native GM
  link still works. Residual: a third-party jack_connect stays
  detection-only (GM link_audit plus the first-session pw-link -l).
  Fence granted to worker-3.
  AC11 (the AE's default-sink AC) = worker-3 verify items 13-14. Item
  14 FINAL (Architect, AE): NO production log-level change.
  Hook-loaded evidence: (a) WP active, NRestarts=0; (b) the deployed
  conf says `required`, and the conf and lua shas match; (c) no WP
  err/warn; (d) a cited WP 0.5.12 source showing required = abort; (e)
  AE functional check: pw-play zero.wav with no target gives "no
  target node available" and no new link (CHANGE, nothing connected,
  amps off). The journal line is extra evidence only (answers the
  log-level question).
  UPDATE (CM, 2026-10-26): pushed at fe6b6974: venue
  markaudio-ultimax-200hz ch4 dirac.wav -> zero.wav. The AE accepts
  the delta so far; sign-off waits for the Gain-values comment, an
  all-zero pin test and the Rust venue tests in CI.
  First-session evidence item (AE): Mixxx and Reaper start with no
  error dialog under self-connect-mode (screenshot plus log grep); if
  a warning appears, one SETUP-MANUAL line. Same as the UX request
  above.
  F-318 operator note (CM, 2026-10-26): "ships IN US-173 (writer and
  file being settled with the TW)". The UX recorded the condition MET
  by existing branch text (above); the PM asked the TW to reconcile.
  MET stands until the UX or the TW says otherwise.
  RESOLVED (TW, 2026-10-26): MET stands, as recorded at 1c2d4bef; no
  new note is written. The TW's US-173 batch adds to that text:
  `jack_connect` in the list of forbidden hand-made links, and "The
  Test tab is the only sanctioned way to check the speakers". It also
  adds AC11 to US-173.md in the joint-ruling version (the default-sink
  half plus hook-loaded evidence (a)-(e), the journal line extra
  evidence only). The batch waits for the AE's OK, then the CM applies
  it.
  MERGE CONDITION (QE, 2026-10-26): the jack-self-connect real-PW
  check runs in CI before merge: one ci.yml step in the ARM
  test-and-build job, a hard failure, with the positive-control and
  summary lines quoted from the final-head log. A one-off run is not
  enough unless the check cannot run in the sandbox; that fallback
  needs the QE and the Architect. The CM grants the ci.yml edit to
  worker-3.
  PR #63 (CM, 2026-10-26): draft
  https://github.com/ela2342/mugge/pull/63, branch
  story/US-173-first-dj-session, author worker-3; head 0b614d1b, CI
  green (run 40305727537). The QE's jack-self-connect CI condition is
  MET. Still open: the P-step evidence (needs a CHANGE session), D-031
  M2, the WAV generation (blocked by the nix hold) and 7/7 at the
  final head. Rule 13 tally: 0/7 formal approvals.
  F-400 (Architect via CM, 2026-10-26; not P1 per the Architect; owner
  worker-3 on #63): pipewire.nix installs 10-audio-settings,
  21-usbstreamer-playback, 30-filter-chain-convolver and
  80-jack-no-autoconnect into the conf.d dirs as
  `<storehash>-<name>.conf`. The load order is therefore hash-random,
  and same-name overrides break. Fix: explicit destination names; a
  static nix check that every conf.d file matches
  `^[0-9]{2}-[a-z0-9-]+\.conf$`; a P-step that lists the deployed
  names on the Pi.
  UPDATE (CM, 2026-10-26): F-400 pushed on #63 at ff4d6c7e (parent
  0b614d1b), CI pending. P-step checklist item 15 added (checklist
  sha1 1c677f9e). Rule 13 tally still 0/7.
  QE on F-400 (via CM, 2026-10-26): no objection, with conditions: C1
  CI green for conf-fragment-names and jack-self-connect at the final
  head; C2 P-step 15 lists the user ~ela/.config conf.d dirs (expected
  empty); C3 the post-deploy standard checks run first, because the
  load order changes. AE and Architect informed. CI run 40312806198 at
  ff4d6c7e in progress.
  UPDATE (CM, 2026-10-26): #63 head is now 9b1aa8a1 (F-400 self-test,
  parent ff4d6c7e) and CI restarted; this supersedes the CI run
  40312806198 above. P-step checklist sha1 53daaa70 (C2/C3 added;
  supersedes 1c677f9e).
  AE conditions on #63 (via CM, 2026-10-26): (1) the PR body shows
  that 05-rt-direct does not overlap the 10-audio-settings keys; (2)
  C3 is extended with the pw-metadata clock/quantum values, the
  USBStreamer node props unchanged, and a pre-deploy listing of the
  user conf.d.
  UPDATE (CM, 2026-10-26): AE condition (1) MET (no key overlap; the
  sentence is in the PR body). Checklist sha1 now bdef865d (AE
  condition (2) added; supersedes 53daaa70). QE OK on the 9b1aa8a1
  self-test; QE C1 waits for CI at the final head.
  UPDATE (CM, 2026-10-26): #63 review bundle published at
  /tmp/pr63-review-9b1aa8a1/ (pr63.diff sha256 46357791..., 34 files,
  +3806/-27, merge-base 5f3af36a). 24 commits behind main; the only
  overlap is stories-index.md, so a main merge plus a diff-only
  re-check comes later. Tally 0/7; CI run 40313123653 still running.
  UPDATE (CM, 2026-10-26): CI run 40313123653 at 9b1aa8a1 SUCCESS on
  all jobs (excerpt
  /tmp/pr63-review-9b1aa8a1/ci-40313123653-excerpt.txt). Two CI
  findings went to the QE for a ruling: jack-self-connect was a cachix
  cache hit with no fresh output in this run; wireplumber-no-bypass is
  a flake check not wired into ci.yml, so it did not run in CI.
  worker-3 has the conditions; they request OBSERVE for the screenshot
  and merge main later.
  #63 verdicts at 9b1aa8a1:
  - SecSpec APPROVE (comment 6415267477), INFO residuals (1)-(4), and
    a question to the AE: home-lab-chn50p-ultimax.yml keeps dirac.wav
    at -120 dB on spare ch 4, while markaudio-ultimax-200hz uses
    zero.wav (D-031 M2).
  - UX APPROVE WITH 2 MERGE CONDITIONS (comment 6415275779; pin
    verified). C1: record UX point 4 in US-173.md and supply a Mixxx
    startup (no-modal) screenshot plus the log grep (AE-accepted). C2:
    write the AC9 thermal STOP procedure into the story (UX proposal
    via CM; the AE confirms the order). Non-blocking: N1 the US-173
    session rules and the H procedure still say pw-dump proves gains
    0, contra safety.md F-395. N2 ramp wording vs F-315, so TW v19
    must land in or before #63. N3 AC11(c) "no warning" conflicts with
    deny lines logged at WARNING.
  - QE CHANGES REQUESTED (accounting copy to PM). Blocking: B1 the
    venue `coefficients` field is not consumed by any loader; the
    convolver always loads combined_sub2_lp.wav for ch 4, so the
    zero.wav mute test proves nothing at runtime; the home-lab venue
    still says dirac on ch 4; needs an Architect/AE fact check and a
    test of the file actually loaded. B2 the thermal-watch tests (25)
    are not in test-all, so they never run in CI. B3
    checks.wireplumber-no-bypass (the F-318 AC5 proof) is not in CI;
    accepted if a published run at the final head exists before merge;
    F-380 gates gig use. B4 the PR body is stale and incomplete.
    Carried over: C1-C3, the P-step evidence, D-031 M2, the WAVs +
    SHA256SUMS with a unit test. PM cross-ref: B1 bears on the
    fe6b6974 ch4 dirac.wav -> zero.wav change above.
  Tally: 2 approvals (SecSpec; UX conditional) + QE CHANGES REQUESTED;
  AE, Architect, TW, AD outstanding.
  Backlog one-liner (QE, from #63; no priority given): venue.py
  validates the `coefficients` name but never checks that the file
  exists or is used. Either wire venue coefficients into the deploy,
  or drop/rename the field so configs cannot claim a mute that is not
  applied.
  CORRECTION (CM, 2026-10-26): all 7 #63 verdicts are posted verbatim
  at 9b1aa8a1; this supersedes the tally line above. SecSpec APPROVE
  (6415267477). UX APPROVE with C1/C2 (6415275779). Architect v2
  APPROVE with conditions 1-4 (6415312425; v1 never posted). AD
  REQUEST CHANGES M1 (6415312939). AE NOT YET C1-C3 (6415313355). QE
  CHANGES REQUESTED B1-B4 plus carried C1-C3, P-steps, M2, WAVs +
  SHA256SUMS (6415313950). TW APPROVE with G1-G4 (6415314354).
  QE ruling on the CI findings (after CI 40313123653):
  conf-fragment-names C1 MET. jack-self-connect: the cachix hit counts
  as a pass, but its $out files (policy/control/fragments) must be
  quoted at the final head through a remote-cache read.
  wireplumber-no-bypass stays B3: one published run at the final head
  before merge; the CI wiring is F-380, which gates gig use.
  UPDATE (CM, 2026-10-26): worker-3 pushed 2a688a94 (UX C1 as AC12,
  plus N1). New head: every approval needs a diff-only re-check at the
  final head. N3 (AC11(c) deny-warning exclusion) is with the AE and
  the Architect for a ruling.
  #63 consolidated rework (worker-3, via CM):
  - home-lab ch 4 -> zero.wav; the mute test parametrized over both
    venues.
  - the venue `coefficients:` field is metadata only (AE confirmed),
    so the test and AC3b pin combined_sub2_lp.wav all-zero (sha
    97b9d9db), and the zero.wav comment is reworded (NaN, AD L2).
  - the thermal suite wired into CI; SHA256SUMS plus a test for it;
    the F-380 note.
  - the thermal STOP procedure, AE-confirmed with amendments: skip the
    fade if it takes over about 5 s; start a second watch run after
    the STOP; the session is over, and resuming needs a pre-flight,
    the owner's OK, under 70 C and no INVALID samples.
  - the first-DJ-session evidence AC; the AC11 runtime evidence;
    AC11(c) excluding the deny WARNING; the pw-dump vs F-395 fix;
    DoD/AC5; the full PR body plus a Tests section.
  - TW batches G1/G2 and UX N2 (v19), applied after worker-3's next
    head. QE B3: a CM-published `nix build
    .#checks.aarch64-linux.wireplumber-no-bypass` at the final head;
    needs disk clearance under the hold.
    UPDATE (CM, 2026-10-26): the B3 build (or the cache-hit read) is
    worker-run, CM-cleared and published: a detached worker runs it,
    the CM grants the disk clearance and publishes the output in the
    review bundle.
    ATTRIBUTION (CM, 2026-10-26): B3 is a team-lead ruling: a worker
    runs it detached once the disk hold allows; the CM clears it and
    publishes the result.
  #63 backlog / non-blocking (no priority given): AE N1 and AD L1
  (HP/IEM ch 5-8 -> zero.wav); the Architect's wp-f318 case without
  the convolver stand-in; the TW's stale 80-jack conf header; SecSpec
  INFO (1)-(4).
  Relay to worker-4 AFTER #63 merges (Architect, via CM): switch
  test_deploy_gate.py's in-test zero fixture to the committed
  configs/coeffs/zero.wav.
  #63 AC11(c) (CM, 2026-10-26): the Architect sent a FINAL text that
  withdraws "loaded notice absent = FAIL". PENDING: the CM relays it
  only once the AE confirms the same text. Not settled.
  SETTLED (CM, 2026-10-26; supersedes the PENDING line above): AC11(c)
  FINAL, agreed by the Architect and the AE, relayed verbatim to
  worker-3. Deny lines before (e) are recorded and are an AE finding
  before amps on. Removing / final guard / error-after-deny / any
  other warn+error = FAIL. After (e), only the pw-play deny lines. The
  "loaded" notice is extra evidence only.
  UPDATE (CM, 2026-10-26): #63 pushed at a66576eb (parents 317c6910,
  91943f58, 2a688a94). AC11(c) carries the final text; the PR body is
  replaced with worker-3's full-scope draft. Next from worker-3: the
  WAVs and SHA256SUMS, under one cached `nix develop` the CM cleared
  with a dry-run guard; the AC5 "worker runs, CM publishes" wording
  (team-lead); answers to TW Q1-Q4. After that: the TW G1/G2/N2 batch
  (safety.md, SETUP-MANUAL, F-318.md, new F-400.md, defects-index),
  then the main merge, the bundle and the re-checks.
  CORRECTION (worker-3 via CM, 2026-10-26): the thermal suite count is
  23, not 25 (QE B2 above); the QE confirms it at the final head.
  UPDATE (CM, 2026-10-26): the CM cleared worker-3's single
  nix-shell.drv env build (the dry run listed only that build, nothing
  to fetch). Staged for the next commit: the AC5 "worker runs, CM
  publishes" wording; TW Q1 (AC5 layer (a) is the WP hook, not
  CI-gated, plus the JACK guard, which is CI-gated); Q4
  (80-jack-no-autoconnect.conf header comment fixed). Q4 changes the
  jack-self-connect drv hash, so CI rebuilds it and the QE gets fresh
  log output. Q2: "(b) not started (US-175)" is still correct. Q3:
  F-400 severity is with the Architect.
  RULING (Architect, 2026-10-26, relayed to the TW): F-400 severity is
  medium, not P1. The fragments set disjoint sections, so the risk is
  latent only (a same-name override, future number-order dependence);
  guarded by checks.conf-fragment-names; not safety.
  UPDATE (CM, 2026-10-26): worker-3's first develop ran the generator
  only (exit 0, no build or fetch, df 4.7 -> 4.7). A second develop
  for the coeff/mute tests is cleared with the same guards. #63 has
  had no CI since 9b1aa8a1 because the PR CONFLICTS with main; this
  clears with the main merge.
  UPDATE (CM, 2026-10-26): #63 new head 3a4baba1 pushed (WAVs,
  SHA256SUMS, test, AC5, Q4 conf header). It still CONFLICTS with
  main, so no CI yet.
  UPDATE (CM, 2026-10-26): the TW batch landed as 94064cc2 (parent
  3a4baba1), including the new F-400.md. worker-3 merges main next.
  UPDATE (CM, 2026-10-26): merge head 5db98556 pushed; the PR is
  MERGEABLE; CI run 40320814684 running. A follow-up commit is coming
  with the AE's US-173.md 248-251 text and run_venue_checks on the
  committed WAVs.
  UPDATE (CM, 2026-10-26): final head 0dc2a40b pushed (the AE's
  US-173.md 248-251 text; run_venue_checks on the committed WAVs, all
  FIRs pass). CI run 40321143579 running; the superseded run on
  5db98556 was cancelled. Bundle /tmp/pr63-review-0dc2a40b/ out to all
  7.
  #63 verdicts at 0dc2a40b (record copies to the PM; 2 of 7 so far):
  - UX: APPROVE, CI-conditional (run 40321143579). UX C1/C2 and N1-N3
    from 9b1aa8a1 all closed (AC12, AC9 STOP, F-395 wording, F-315
    wording, AC11(c)). Briefing note (UX: not a backlog item): tell
    the DJ that a gate close ends this session.
  - QE: APPROVED WITH CONDITIONS. C1: CI 40321143579 green, showing
    the 12 coeff/mute tests, the 23 thermal cases, conf-fragment-names
    and jack-self-connect (quote $out if it was a cache hit). C2: B4,
    the stale body (the "to come" list is outdated;
    test_committed_venue_coeffs.py has no row). C3: B3, the WP
    no-bypass run published. C4: the P-steps. B1 and B2 met. Removing
    test_format/test_d009 accepted (run_venue_checks covers them).
  - Not yet relayed to the PM: AE, SecSpec, TW, Architect, AD.
  UPDATE (CM, 2026-10-26; supersedes "Not yet relayed" above): 6 of 7
  verdicts posted on the PR at 0dc2a40b:
  - AE: APPROVE, CI-conditional. Architect: APPROVED, CI-conditional.
    UX: APPROVE, CI-conditional. SecSpec: APPROVE, CI-conditional. AD:
    APPROVE, diff-only.
  - TW: APPROVED, documentation complete, CI-conditional. Non-blocking
    nits: the PR body is stale; AC5 still has the legacy wording
    "(architect: a small WirePlumber rule)".
  - QE: APPROVED WITH CONDITIONS C1-C4 (above); the CM posts it once
    the QE's file arrives.
  - Open: CI 40321143579; the B4 body fix (worker-3); the
    jack-self-connect $out quote (QE C1) and the B3 run (QE C3), both
    waiting on an Architect + QE route because Mac nix is blocked
    (disk).
  UPDATE (CM, 2026-10-26): all 7 verdicts posted at 0dc2a40b,
  including the QE's (sha256 44e32ff2); the B4 body 69ae9511 is
  applied. CI 40321143579 is RED: room-correction 2 failed, 60 errors.
  Cause: main's venue_pipeline.py:164 build_channel_map rejects the ch
  4 zero.wav mute ("venue channel '4_sub2_lp' expects 'zero.wav' but
  no profile speaker uses channel 3"). worker-3 is fixing it on
  29f5c61f, consulting the Architect and AE. Every verdict lapses; all
  7 do diff-only re-checks at the new head.
  QE C1 adds: room-correction at 0 failed / 0 errors with the count
  explained, and build_channel_map not loosened for other venues.
  Evidence routes FINAL (joint QE + Architect v2,
  /tmp/cm-relay/pr63-evidence-route-joint-v2.txt, sha256 4a83b598;
  supersedes v1 1fa1d156): no Mac nix in any route. jack-self-connect
  $out: 1a the final-head CI step log, 1b `nix store cat` from
  mugge.cachix with the narinfo signature checked, fallback a Pi
  CHANGE build at the declared SHA. B3 wireplumber-no-bypass: 2a
  (preferred) a non-gating CI arm64 job on a scratch branch at the
  exact SHA, 2b (fallback) a Pi 5 native build under a CM CHANGE grant
  with the sandbox on. A run carries over to a new head only with an
  identical drvPath.
  FIX ROUTE (Architect, 2026-10-26, via CM): worker-3's option (A)
  accepted. zero.wav is a canonical mute in venue_pipeline, allowed
  only on speakerless channels; a speaker on zero.wav raises
  ValueError (AE may amend). It is never generated, and verify.py
  doesn't change. dirac is generated only when it is named. One added
  test: both venue YAMLs load through load_venue_bundle.
  venue_pipeline.py and test_venue_closed_loop.py are now in #63's
  scope. worker-3 is building on 29f5c61f; CI is the test run while
  disk is below the line. worker-3 owns up to one process slip: they
  ran only the two coefficient test files locally.
  AE (2026-10-26, via CM; relayed to worker-3): accepts option (A);
  point (a) stands (a speaker on zero.wav raises). Conditions:
  - a test that the pipeline output has no file at all for ch 4, and
    that a speakerless channel naming anything other than dirac.wav or
    zero.wav still raises;
  - the committed-bytes tests test_venue_spare_channel_mute.py:50/58
    run in T1;
  - the closed-loop report lists ch 4 as "muted (zero.wav, not
    generated)".
  FINAL (joint AE + Architect v3, 2026-10-26, released by the AE;
  verbatim in /tmp/cm-relay/PR63/joint-zero-wav-ruling-v3.txt, sha256
  f35f5b59; supersedes the FIX ROUTE and AE conditions above; v2
  1ca0e260 and v1 1ef61a25 are VOID). Relayed to worker-3. The AE
  withdrew their conditions 4 and 5 (generate zero.wav; a verify_zero
  kind), because they contradicted the joint ruling recorded at
  0dc2a40b (test_venue_spare_channel_mute.py:11, "no kind in
  run_venue_checks"). Required for re-approval:
  - (1) venue_pipeline.py: ZERO_FILENAME = "zero.wav" next to
    DIRAC_FILENAME; build_channel_map lets a speakerless channel name
    only DIRAC_FILENAME or ZERO_FILENAME (anything else is a
    ValueError), and a channel with a speaker naming ZERO_FILENAME is
    a ValueError (fail closed).
  - (2) generate_venue_filters emits DIRAC_FILENAME only iff some
    speakerless channel names it. Nothing is written for a zero.wav
    channel (no file, no generation, no export_filter call);
    ZERO_FILENAME is not in expected_files; verify.py and
    run_venue_checks are untouched. Tests (v3 change): (a) real venues
    (ch 4 = zero.wav, ch 5-8 = dirac.wav): nothing attributable to ch
    4, and dirac.wav IS present, solely because ch 5-8 name it; (b) a
    synthetic venue where only ch 4 is speakerless and names zero.wav:
    no dirac.wav and nothing for ch 4.
  - (3) the committed-bytes checks (configs/coeffs/zero.wav and the
    venue set's combined_sub2_lp.wav exactly 0.0 and finite,
    test_venue_spare_channel_mute.py:50/58) stay in a T1 suite.
  - (4) the closed-loop / venue report lists ch 4 as "muted (zero.wav,
    not generated)".
  - (5) excluded: no revert to dirac.wav, no fake sub2 speaker in the
    profile.
  Tests: the QE decides the final set (minimum list in the v3 file).
  The local run includes the room-correction suite. Build on main
  after #65 (F-399). The v3 file's US-174d part matches the
  single-writer condition (3) and the AE's all-zero check recorded
  under F-399.
  Process note (CM, 2026-10-26): the CM relayed v2 to worker-3 before
  the AE had released it; fixed: the CM now holds joint texts until
  both authors release them.
  QE CONFIRMED (2026-10-26, from CI 40321143579): the spare-mute zero
  checks run in T1. At the new head the QE checks those 3 tests and
  the 9 test_committed_venue_coeffs tests by name.
  HELD (CM, 2026-10-26): worker-3's caa63d9e (parent e1813e16, which
  merges main 29f5c61f) is not pushed. It differs from ruling v3 on
  the ZERO_FILENAME naming, the item-4 report wording and test (a).
  worker-3 is conforming in a follow-up commit.
  UPDATE (CM, 2026-10-26; supersedes HELD above): 3f28b6c7 is pushed
  (chain e1813e16 main merge -> caa63d9e -> 3f28b6c7) and follows
  ruling v3 literally. CI 40323763997 is running; pass condition 0
  failed / 0 errors of 1364 collected. The caa63d9e points are moot:
  the AE accepted its wording and the Architect waived the constant
  name.
  UPDATE (CM, 2026-10-26): evidence route v2:
  scratch/pr63-evidence-3f28b6c7 = 2a17ed77 pushed, run 40324085388 in
  progress; it gates nothing.
  UPDATE (CM, 2026-10-26): evidence run 40324085388 completed green
  (exit 0, checkout exactly 3f28b6c7). Extracts in
  /tmp/pr63-evidence-40324085388/ (full.log sha256 e2ba739b, verified
  at PM read). The QE and the Architect are judging it.
  QE accounting (2026-10-26;
  /tmp/pr63-qe-evidence-verdict-3f28b6c7.md, sha256 32ab3975, verified
  at PM read): evidence at 3f28b6c7 (run 40324085388): B3 (route 2a)
  MET; route 1 MET pending R1-x. R1-x: the jack-self-connect out path
  in PR CI run 40323763997 must match m689zyzw. Still open for the
  QE's #63 approval: the C1 items from that CI run, the B4 body, R1-x.
  Backlog one-liner (QE, from the #63 evidence; non-blocking;
  AE/Architect domain; no F-ID, no P-level given): a WirePlumber
  restart drops the GM-style link; it also happens with the policy
  off, so the policy is not the cause.
  UPDATE (CM, 2026-10-26): the QE evidence verdict (32ab3975) is
  posted verbatim on #63:
  https://github.com/ela2342/mugge/pull/63#issuecomment-6416265966.
  Architect evidence check PASS (CM, 2026-10-26;
  /tmp/pr63-evidence-architect-check-3f28b6c7.md, sha256 5c7f2837,
  verified at PM read), posted verbatim:
  https://github.com/ela2342/mugge/pull/63#issuecomment-6416283734.
  Route 1b (substituted from cachix, signature evidence adequate) and
  route 2a MET; cachix stayed read-only. It approves the evidence
  only; the Architect's code re-review waits for CI 40323763997 and
  the bundle.
  Backlog one-liner (Architect, non-blocking; no F-ID, no P-level
  given): pin the mugge.cachix signing key in CI.
  UPDATE (CM, 2026-10-26): CI 40323763997 GREEN at 3f28b6c7. The 7
  re-checks are requested.
  Rule 13 tally at 3f28b6c7 (CM, 2026-10-26; verdicts posted verbatim
  on the PR): 6 of 7 APPROVE.
  - QE: APPROVED WITH CONDITION C4 (/tmp/pr63-qe-verdict-3f28b6c7.md,
    sha256 68a46e7f, plus addendum
    /tmp/pr63-qe-verdict-3f28b6c7-addendum.md, sha256 58c7c3db; both
    verified at PM read). C1 MET (CI 40323763997 green;
    room-correction 1364 collected, 1363 passed, 1 known skip). B3
    MET. R1-x MET, so route 1 is fully MET. B4 MET (body c4cd9e75,
    live per CM). C4 OPEN: the Pi P-step evidence (left out of
    68a46e7f by mistake, per the QE). A new head needs another
    diff-only re-check (QE).
  - UX: APPROVE (diff-only vs 0dc2a40b, CI green, pins verified;
    /tmp/pr63-ux-verdict-3f28b6c7.md, sha256 56030914, verified at PM
    read).
  - SecSpec, Architect, AD, AE: APPROVE, posted verbatim (CM).
  - TW: PENDING. The file changed between the CM's hash check and the
    copy; the CM deleted the wrongly posted comment and waits for a
    sha from the TW.
  UPDATE (CM, 2026-10-26; supersedes "TW: PENDING" and "SecSpec,
  Architect, AD, AE: APPROVE, posted verbatim (CM)" above): all 7
  verdicts are posted verbatim at 3f28b6c7; read-only copies in
  /tmp/cm-relay/PR63/ (all 8 sha256 verified at PM read).
  - QE APPROVED 68a46e7f (comment 6417534204); QE addendum APPROVED
    WITH CONDITION C4 58c7c3db (6417597419).
  - UX APPROVE 56030914 (6417551235).
  - SecSpec APPROVE + LOW for 174d 004577be (6417552681).
  - Architect APPROVE a2d9e374 (6417553324).
  - AD APPROVE + L1 for 174d 09e1dd4c (6417554086).
  - AE APPROVE db7f102b (6417555356).
  - TW APPROVED 155c49f0 (6417596798); the TW's earlier 0031f405 is
    withdrawn. A comment the CM posted by mistake was deleted.
  C4 OPEN (QE addendum): Pi P-step evidence for AC3 b-e, AC4, AC7,
  AC11 a-e, AC12, plus the conf.d names before and after deploy. #63
  stays a DRAFT and is NOT merge-ready (team-lead STOP): it merges
  only after the Pi-side DJ-session evidence is in (after US-172) and
  the QE clears C4 at the final head (CM).
  UPDATE (CM, 2026-10-26): deploy-first is ON. Team-lead OK'd the #63
  DEPLOY plus P-steps (QE C4) before US-172 v6, and the PO agrees.
  Conditions: v6 keeps priority; the Architect confirms there is no v6
  base change (pending); the AE clears worker-3's plan, also checking
  174d's referenced-WAVs-exist and the zero-bytes check at
  combined_sub2_lp. worker-3 is preparing the plan; the PO is told.
  UPDATE (CM, 2026-10-26; supersedes "deploy-first is ON" above):
  deploy-first is OFF. Pi order (team-lead ruling; supersedes
  "deploy-first is ON"): US-172 v6 runs FIRST on the current
  generation rcyg67wd, THEN the #63 DEPLOY plus P-steps (QE C4).
  Condition 2 (the Architect confirms no v6 base change) failed.
  Architect reason: a #63 `nixos-rebuild boot` writes a new gens/<id>/
  and rewrites config.txt, which breaks v6's pins (BASE_TOP, CFGSHA
  ff08471f, CMDSHA c28e6a4e, C4SHA 337c7d5c, TB4SHA 030489f3, the FAT
  manifest, the tryboot draft os_prefix) and its pwdump BEFORE
  baseline; v6 would then need a re-pin, a new OBSERVE baseline and a
  re-review. The pins fail closed (STOP), so it is not a safety issue,
  but v6 could not run. worker-3 is still preparing the #63 plan for
  AE and QE review; no grant before v6 is done. #63 stays a DRAFT
  until the QE clears C4.
  UPDATE (CM, 2026-10-26): the #63 Pi plan v2 is
  /tmp/cm-relay/PR63/pi-plan-3f28b6c7-v2-dd227076.txt (sha256
  dd227076, verified at PM read). It supersedes v1 da746539. In
  review: the AE (clearance, Q2), the Architect (Q1, Q3, Q4) and the
  QE (C4 coverage, split).
  - One DEPLOY session of about 1.5-2 h, with one announced plain
    reboot, after US-172 v6.
  - If v6 merges to main first, #63 needs a main merge, a new head and
    a repeat of the evidence run before deploying.
  - The Mixxx steps P15-P17 are deferred if there is no display.
  AE CLEARED plan v2 dd227076 (CM, 2026-10-26; frozen copy
  /tmp/cm-relay/PR63/frozen-AE-deploy-clearance-v2-ab73af2a.txt,
  sha256 ab73af2a, verified at PM read). Conditions:
  - C1: zero bytes at combined_sub2_lp before D3.
  - C2: every WAV the new conf references exists before the D4 reboot,
    dirac.wav included.
  - C3: Mixxx plays nothing.
  - C4 (new): the clearance covers 3f28b6c7 only. If the SHA changes,
    the re-pinned P3/P6/P9 and zero.wav hashes go to the AE before the
    grant.
  - Q2: set_venue is OK in-session with re-reads. The handover records
    "venue armed; next gate open needs the owner's S-012 OK".
  QE verdict on plan v1 da746539 (QE, 2026-10-26;
  /tmp/pr63-qe-piplan-verdict-da746539.md, sha256 37ae18e6, verified
  at PM read): APPROVE with amendments A1-A4; the C4 split is
  acceptable (Q1 YES, conditional). Open conditions:
  - US-173 stays open with AC12 and the Mixxx part of AC7 unchecked.
  - P15-P16 become a hard pre-audio gate of the first DJ session.
  - The PR body must state the split (the QE re-checks the body).
  - The QE's C4 on #63 stays open until the QE has checked the
    session-1 P-step evidence.
  PM cross-ref: the QE verdict names v1 da746539, which v2 dd227076
  supersedes; the PM asked the QE whether it carries to v2. Status on
  v2: pending QE. Still pending on v2: the Architect (Q1/Q3/Q4). Order
  unchanged: US-172 v6 first, then the #63 deploy (CM).
  UPDATE (2026-10-26; supersedes the PM cross-ref above):
  - QE v2 verdict (QE + CM): APPROVE on plan v2 dd227076, superseding
    v1 37ae18e6 (/tmp/pr63-qe-piplan-verdict-v2-dd227076.md, sha256
    c1e573fe; CM frozen copy
    /tmp/cm-relay/PR63/frozen-pr63-qe-piplan-verdict-v2-dd227076-c1e573fe.md;
    both verified at PM read). A1-A4 stand. A5: the deploy SHA is the
    PR head, never a local merge, with CI and evidence green and an
    identical drvPath. A6: the re-pinned P3/P6/P9 go into a new plan
    file the QE verifies before the grant. Q1 change: if the post-D4
    pre-check shows /dev/dri and an active compositor, P15-P16 run in
    session 1 and the split is dropped. The QE's C4 on #63 stays open
    until the QE has checked the session evidence.
  - Architect verdict (CM): APPROVE WITH CONDITIONS C1-C7 on plan v1
    da746539 (frozen copy in /tmp/cm-relay/PR63/:
    frozen-pr63-pi-plan-da746539-architect-verdict-969edef6.md, sha256
    969edef6, verified at PM read): defer P15-P17 and the Mixxx half
    of AC7; no offscreen Mixxx. Carry-over to v2 is pending (CM
    asked). The CM notes the v2 delta is ordering and Q4 only.
  - OPEN, P17 overlap (CM): the Architect defers P17 entirely; QE A2
    keeps the P17 read-back and standby in session 1. The Architect
    writes one joint line and the QE releases it. Per team-lead,
    worker-3 holds the P17 part of plan v3 (a new file) until then.
    The v3 delta then goes to the Architect, the QE and the AE. The
    deploy still comes after US-172 v6.
  - If the split goes ahead (CM, QE): P15-P16 (Mixxx on the HW-GL
    display) become a hard pre-audio gate of the first DJ session
    (US-173), and US-173 stays open with AC12 and the Mixxx half of
    AC7 unchecked. Under QE v2 the split applies only if the post-D4
    display pre-check fails.
  - Architect v2 verdict (CM, 2026-10-26; supersedes "Carry-over to v2
    is pending" above): APPROVE WITH CONDITIONS on plan v2 dd227076
    (frozen copy in /tmp/cm-relay/PR63/:
    frozen-pr63-pi-plan-v2-dd227076-architect-verdict-03288857.md,
    sha256 03288857, verified at PM read). C1-C7 carry over from
    969edef6; carry-over SETTLED. New:
     A1: on a head change, read the generation pins at B0 (toplevel,
     kernel, N, config.txt sha); the CM states them before D1; a
     kernel mismatch means STOP for the Architect's ruling.
     A2: a normal-boot display needs a generation containing both
     US-172 and #63.
     A3: if the session stops between D2 and D4, the CM tells the next
     FAT-reading session about the pending generation.
  - RESOLVED (CM, 2026-10-26; supersedes "OPEN, P17 overlap" above;
    closes the P17 overlap and the Q1 conflict between the Architect's
    v1 deferral and the QE v2 Q1 change, both above): joint ruling
    written by the Architect and released by the QE ("release
    5e123a6b"), frozen copy in /tmp/cm-relay/PR63/:
    frozen-pr63-arch-p17-carryover-qe-a2-5e123a6b.md (sha256 5e123a6b,
    verified at PM read).
     P17: the non-Mixxx part runs in session 1; only the
     Mixxx-dependent part is deferred.
     PRE-DISPLAY counts only on the HW path: vc4 card (not simpledrm
     alone), v3d render node, active compositor, Mixxx reports V3D. If
     all pass, P15-P16 run in session 1. If any fails, the Mixxx part
     is deferred, or AC12 is recorded NOT VALID.
     QE-only note (not joint): if only the renderer check fails, P15's
     routing evidence still counts.
     CORRECTION (QE via CM, Architect 6b0d7071 and f368f222,
     2026-10-26; supersedes the two lines just above): the "QE-only
     note" label was wrong (it came from an earlier relay and the PM
     carried it). The renderer fallback is the Architect's own text in
     the joint file 5e123a6b, item 3, verbatim: "If (d) fails after
     Mixxx has started: quit Mixxx. The routing evidence from P15
     still counts, but AC12 is recorded as NOT VALID (software GL) and
     deferred." Per 6b0d7071, the line "If any fails, the Mixxx part
     is deferred, or AC12 is recorded NOT VALID" above summarises the
     Architect's cover message, not the file text: (a)-(c) fail ->
     defer the Mixxx part; (d) fails -> NOT VALID.
  - The conditional US-173 item above still applies. worker-3 is
    writing plan v3 (CM). The deploy still comes after US-172 v6.
  - UPDATE (CM, 2026-10-26, after v249): plan v3 is frozen as
    /tmp/cm-relay/PR63/pi-plan-3f28b6c7-v3-df8e1614.txt (sha256
    df8e1614, verified at PM read). It crossed with the later rulings.
    worker-3 is writing v4 to fold in QE v2 c1e573fe, Architect v2
    03288857 and the joint 5e123a6b (DISP becomes the HW-path
    PRE-DISPLAY gate).
  - OPEN [ARCH-CHECK] (Architect, via CM): does C7 pass when GM's
    F-249 standby sets force-quantum to 256 instead of clearing it?
  - SETTLED (Architect, via CM, 2026-10-26; supersedes the OPEN
    [ARCH-CHECK] above): frozen copy in /tmp/cm-relay/PR63/:
    frozen-pr63-arch-check-c7-f249-2aeff13a.md (sha256 2aeff13a,
    verified at PM read). The Architect accepts worker-3's reading of
    C7: since F-249, GM is the single quantum authority, with
    force-quantum 256 as its standby value. C7 PASS requires all of:
     the effective driver quantum is 256, read from the USBStreamer
     driver row in `pw-top -b -n 2`, not from settings alone;
     clock.force-quantum is 256 or equals the A2 baseline;
     clock.force-quantum is never 1024.
     Otherwise FAIL: retry `set_mode standby` once and re-read; if it
     still fails, STOP and report to the Architect via the CM. No
     manual pw-metadata write, ever. An A2 baseline of 0 followed by
     256 at P17a is a PASS, logged as an observation. worker-3 folds
     this into plan v4 (CM).
  - UPDATE (CM, 2026-10-26, after v251): plan v4
    /tmp/cm-relay/PR63/pi-plan-3f28b6c7-v4-3d3bfff7.txt (sha256
    3d3bfff7) is superseded by v5
    /tmp/cm-relay/PR63/pi-plan-3f28b6c7-v5-ed039bfb.txt (sha256
    ed039bfb; both verified at PM read), which is v4 plus C7 2aeff13a
    verbatim. v3 df8e1614 was never reviewed (CM).
     QE on v4 (QE accounting copy;
     /tmp/pr63-qe-piplan-verdict-v4-3d3bfff7.md, sha256 b0623656,
     verified at PM read): APPROVE, superseding c1e573fe. No blockers.
     Non-blocking clarifications N1-N3 for worker-3: N1 P16 vs the
     AC12 text, N2 P16 artefacts, N3 the P15 expected link list. The
     QE's C4 on #63 stays open until the QE has checked the session-1
     evidence.
     AE on v5, verbatim (CM release record (b),
     /tmp/cm-relay/release-record-20261026-b.txt, sha256 71db4f71,
     verified at PM read): "matches, release ed039bfb. The AE
     clearance ab73af2a carries over to PR #63 plan v5 (ed039bfb,
     verified). I read the v4→v5 diff (510b404a): only the header, the
     JR-3 wording and C7 changed. AE-C1..C4 and AE-Q2 are unchanged
     from v4. C3 still binds on path D (5e). C7 makes no gain or gate
     change, and no pw-metadata writes are permitted. My release of v4
     3d3bfff7 is superseded."
     CM, on the AE release: being left in DJ mode on a thermal STOP is
     acceptable, because the gate is closed and the Mults are 0.
     Still pending on v5: the Architect and the QE (CM). PM cross-ref:
     the QE's APPROVE above is on v4, not v5.
  - UPDATE (CM, QE, 2026-10-26, after v252; supersedes "Still pending
    on v5" and the PM cross-ref just above): plan v5 ed039bfb is
    APPROVED by all three plan reviewers. All files in
    /tmp/cm-relay/PR63/, each verified at PM read.
     Architect: APPROVE v5
     (frozen-pr63-pi-plan-v5-ed039bfb-architect-verdict-6b0d7071.md,
     sha256 6b0d7071). C7 matches 2aeff13a; R-a and R-b are now
     explicit in the text. Everything outside the v4->v5 delta is
     covered by the Architect's v4 APPROVE f368f222
     (frozen-pr63-pi-plan-v4-3d3bfff7-architect-verdict-f368f222.md).
     From f368f222: R-a "The FAIL clause takes precedence.
     force-quantum 1024 is a FAIL even if the A2 baseline was 1024.";
     R-b: a STOP follows if it is still FAIL on either criterion
     (force-quantum 1024, or an effective driver quantum other than
     256 in pw-top); section 9: both sessions are NOT required before
     #63 merges (on path N, or on path D with (d) failed, #63 may
     merge on the session-1 evidence under QE-S (i)-(iii)).
     QE: APPROVE v5 (/tmp/pr63-qe-piplan-verdict-v5-ed039bfb.md; CM
     frozen copy
     frozen-pr63-qe-piplan-verdict-v5-ed039bfb-24e77f04.md; sha256
     24e77f04), superseding b0623656 and c1e573fe. N1-N3 non-blocking
     (CM summary): P16 outcomes labelled PASS/FINDING/FAIL; the
     screenshot and mixxx.log saved with sha256 and the capture
     command; the expected link list logged before P15. The QE's C4 on
     #63 stays open until the QE has checked the session-1 evidence.
     AE: released v5 (record (b) 71db4f71, above).
     CM ruling: no v6 plan file. The grant binds v5 + N1-N3 + R-a/R-b
     by reference, so the plan sha stays stable. The grant still waits
     for US-172 v6.
  - CORRECTION (CM, 2026-10-26; record (c)
    /tmp/cm-relay/release-record-20261026-c.txt, sha256 1099250e,
    verified at PM read): the thermal-STOP line attributed to the CM
    above is the AE's own text, from the AE's v4 release, verbatim:
    "Being left in DJ mode on a thermal STOP is acceptable: the gate
    is closed and the Mults are 0." Record (b) had quoted only the
    first sentence of that release. The AE's v5 release supersedes the
    v4 release.
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
  US-174e depends on US-178 (PO, 2026-10-26). Overlap resolved per PO
  2026-10-26: US-178 = flow/plumbing, 174e = venue workflow UI on top.
  174e scope otherwise unchanged (the full one-button venue workflow:
  UI flow, UX N2, US-090/097 constraints); priority unchanged (after
  174d/US-178).
  SUPERSEDED (PO FINAL, 2026-10-26, option (C), replaces option (A)
  above): "US-178 is 174e slice 1 (PO 2026-10-26): the deploy/verify
  step is defined only in US-178." 174e does NOT re-design that step;
  it builds the end-to-end venue workflow (UI, UX N2, US-090/097
  constraints) on top of it.
  GATE (PO, 2026-10-26): F-403 (capture redesign) blocks US-174e,
  because one button needs reliable captures (see F-403).
  UPDATE (2026-10-26, see F-403): if the F-403 US-178 gate lifts early
  (S4 landed, peak width ≤ 2 samples), S2 and the continuous stream
  gate US-174e as reliability work (AE + Architect; PO order: S4
  first, the rest before US-174e).
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
  UPDATE (CM, Architect, AE, 2026-10-26): cause is the #55 merge (LR4
  interaction); no loosening. The CM's earlier "<1.0 dB margin"
  reading of the teeth was wrong: the teeth are fine (+0.94 dB
  deviation, 2.06 dB margin to the gate). Fix ACCEPTED: an injected +6
  dB Q4 380 Hz feature in the right path, premise asserts, the 1.0 dB
  margin and band kept (the Architect's fix plus 3 AE refinements);
  with worker-4. The QE reviews the test change; a fresh 7/7 at the
  new head.
  JOINT ruling, FINAL (Architect, AE, via CM, 2026-10-26): the 380 Hz
  / +6 dB / Q4 feature goes in sat_right; premises (a) a difference of
  at least +4 dB, (b) inside the correction band read from the
  constant, (c) inside 250-500 Hz; a ±1/6-oct REPORT line; margin and
  band kept. Reviews: QE, AE delta, Architect delta.
  RULE 13 at e731820c (the AC7-fix head; the 599ea52a approvals do not
  carry, strict protection; CM, 2026-10-26): 7/7. QE APPROVE,
  diff-only, conditional (issuecomment-6414200520): C1 CI green,
  room-correction 0 failed, count = main 5f3af36a + 26, F-394
  skipped/xfail, no new XPASS, test_all_real_drivers_pass passes; C2
  the PR body quotes the 4 REPORT AC7 lines plus the sentence on the
  #55 gap, and the QE is told if the margin is under 2.0 dB. Architect
  delta APPROVE (CI green plus the before/after numbers; 6414210309).
  AE delta APPROVE (CI green; non-blocking absolute-premise nit;
  6414210948). SecSpec APPROVE (6414248023). TW APPROVE (6414248474).
  UX APPROVE (6414248908; test-only delta, no concerns in the UX
  domain). AD APPROVE, diff-only (6414257026). Merge (CM, standing
  consent) waits on CI 40310308638 green and the QE's C1 and C2; for
  C2, worker-4 updates the PR body once CI is done, with the
  before/after numbers. #61 and #62 follow; they need an
  update-branch, re-checks and CI once main moves.
  UPDATE (CM, 2026-10-26): #57 CI is green (run 40310308638) and the
  PR body is set (AC7 margin 4.36 dB). The merge waits on the QE's
  C1/C2 confirmation.
  QE (accounting copy, 2026-10-26), at e731820c, run 40310308638
  green: AC7 MET (own +2.36 dB, other +6.71 dB, margin 4.36 dB; needs
  at least 2.0). The CM held the merge on a room-correction
  collected-count mismatch (base 1245, #57 1340, +95; the QE had
  expected +26). QE correction: the +26 (1314) was wrong; the real
  delta is +95, all from the new test_venue_closed_loop.py, every
  other file's count unchanged. C1 MET. Only C2 (PR body) is open; the
  QE's approval at e731820c becomes final once the CM confirms the
  body.
  F-262 evidence (QE via CM, backlog, does not block #57): in run
  40310308638 (e731820c into 5f3af36a) test_full_session_api XPASSED
  (CI log /tmp/cm-ci-40310308638.log, around l.7659). It is
  xfail(strict=False) on origin/main; further evidence that F-262 is
  non-deterministic.
  MERGED (CM, 2026-10-26): #57 at e731820c; main is 1e1495ab. The C1
  count was resolved at +95 (all in test_venue_closed_loop.py; the
  QE's +26 was their error). This supersedes the "only C2 open" line
  above. #61 is update-branched to 781b638a (content identical to
  247478d5), approvals void, 7 re-approvals requested via team-lead;
  #62 follows.
  QE (accounting, 2026-10-26): #57 is closed for the QE. C2 was met
  before the merge: the body was edited at 11:31:40Z, the merge
  (1e1495ab) was at 11:35:26Z. The QE's pending list was out of date.
  #57 QE row CLOSED (CM, 2026-10-26): body edit 11:31:40Z, then the
  QE's FINAL approval 11:34:59Z, then the merge 11:35:26Z (1e1495ab).
  #61 re-approvals at 781b638a (record copies): QE APPROVE (pin
  e13a5e04 verified against git diff origin/main...781b638a; content
  identical to 247478d5; docs-only, CI-exempt, a failed job still
  blocks). UX APPROVE (pin verified). MERGED (CM, 2026-10-26): #61 at
  781b638a with 7/7; main is c318f404. #62 is update-branched to
  62b55b29 (content identical to 20903a04), approvals void, 7
  re-approvals requested via team-lead.
  #62 re-approvals at 62b55b29 (record copies, sent to CM): UX APPROVE
  (update-branch only, content identical to 20903a04, pin verified).
  QE APPROVE (pin a4636d06 verified against git diff
  origin/main...62b55b29; content identical to 20903a04; docs-only,
  CI-exempt, a failed job still blocks). Tally 2/7 (UX, QE).
  CORRECTION (CM, 2026-10-26): the #62 tally is 7/7 at 62b55b29, not
  2/7; all verdicts were posted verbatim, the Architect's last
  (comment 6415130599). #62 MERGED, CI run 40316612538 green; main is
  289f1a72.
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
  ADDENDUM 5 (Architect and AE, via the CM and the TW, 2026-10-26;
  SUPERSEDES the 2100 and "= pi4audio-convolver" parts of addenda 3
  and 4 above): default-sink model (1), F-318 option A as in US-173's
  mugge-no-bypass.lua. The convolver priority.session 2100, its
  relation test and the "default = convolver" check are DROPPED, not
  held. The verify check becomes "default.audio.sink is neither the
  USBStreamer nor the convolver (unset passes)"; it fails truthfully
  until US-173 is on main.
  UPDATE (CM, 2026-10-26): pushed at story/US-174d-deploy-gate =
  1601c4dd (Q4 measured gate plus Q3 check_deployable_set, 1419 passed
  locally). Fence extended to the convolver conf, pw_config_generator
  (plus its test) and pipewire.nix. The conf design waits for the
  Architect's ruling on combined_sub2_lp.wav missing from the venue
  set.
  AE one-liner (US-174 measurement, 2026-10-26): measurement capture
  must always target the UMIK-1 node explicitly, never the default
  source.
  UPDATE (CM, 2026-10-26): the web-UI fallback is committed at
  2ec2b004 (HELD). New ruling pending with the Architect: the
  measurement session `_deploy_sync` (web-ui measurement/session.py)
  auto-deploys on every run, a 3rd F-348 writer; worker-4 recommends
  disabling it. F-401 found and fixed on this branch (see P3).
  RULING (Architect via CM, 2026-10-26; resolves the pending line
  above): the measurement `_deploy_sync` is DISABLED (option a), with
  3 conditions: (1) a non-error terminal state "Filters ready, not
  deployed"; (2) post-deploy steps skipped and marked, with no PASS
  against old filters; (3) tests: a mock full run writes nothing, a
  browser E2E, and POST /measurement/deploy returns 409.
  deploy_pw_config and reload_convolver are removed if unused.
  worker-4 has the fence. PO (2026-10-26): this interim state (plus
  manual Venue deploy, no post-deploy verify) is accepted as a known
  deviation of 174d until US-178.
  QE condition (2026-10-26): the revived test_filter_routes tests must
  not be re-skipped; failures get fixed, or the test is deleted with a
  reason (see F-362).
  PM correction (2026-10-26): "F-401" above is F-362 (duplicate ID,
  see F-362 and the P3 F-401 entry).
  RULING (Architect via CM, 2026-10-26): deploy_filters and
  deploy_pw_config are REMOVED in 174d, after a whole-repo caller
  grep; any non-app caller is reported and disabled. The live
  verification sweep (session._run_verify and its PASS/FAIL display)
  is removed in 174d too; US-178 restores it against the new set.
  UPDATE (CM, 2026-10-26): 174d is code-complete and HELD locally at
  5ffb319c. The Architect also removed cleanup_old_coefficients and
  the read-only orphans list_versioned_files/_get_active_filenames. QE
  requirement: the two-branch E2E (no xfail), with a line in F-262.md.
  UX narrowed the c-safe rule to deploy, verify and status only.
  UPDATE (CM, 2026-10-26): 174d is now HELD at b496250b. Per the
  Architect it also removes the read-only orphans
  list_versioned_files, _get_active_filenames, _VERSIONED_RE and
  _PW_FILENAME_RE; deletions only.
  RULING (Architect via CM, 2026-10-26): w4/d031-shared (83620c87)
  folds into 174d, no separate PR; its blobs are identical on 174d.
  The branch is retired: not pushed, not deleted. The 174d PR body
  must name the shared D-031 helpers in its scope.
  174d LOWs (2026-10-26; non-blocking, same theme; no F-ID, no P-level
  given):
  - SecSpec (via CM): deploy must create the convolver's file for
    every zero.wav channel from the committed zero.wav, with a hash
    check, and fail closed. A stale combined_sub2_lp.wav (e.g. a dirac
    copy) must never stay in place.
  - AD (#63 L1 at 3f28b6c7, US-174d input): deploy.deploy_filters
    skips a missing source WAV with only a WARNING. A venue output
    with ch 4 = zero.wav has no combined_sub2_lp.wav, so a deploy
    would leave the previous sub2 filter live and ch 4 would not be
    muted. US-174d sets must be complete (zero bytes for muted
    channels), and a missing file must be refused, not skipped. Not
    reachable today: the runner is sim-only and #65 refuses simulated
    output into coeffs.
  US-174c (measurement on the Pi, web-ui measurement/session.py)
  starts only after F-390/F-391 and builds on them, because it is the
  same file (L-046). Its Pi run is also gated by US-173 H, F-341 AC3,
  D-070 and the amps-on list.
- **US-178** Measurement flow deploys via 174d sets (Architect,
  2026-10-26; P1, PO ruling 2026-10-26: directly after US-174d, ranked
  ABOVE US-177, design principle 6, one button per venue; PO wording:
  "one-button measure -> deploy -> verify via the safe 174d path").
  Scope (Architect): deploy_set from the measurement session;
  activation semantics designed by the AE (PW restart vs reload, owner
  warning, gate state; CM relay: under the AE's safety rules, announce
  or skip a PW restart, gate state across activation); post-deploy
  verification against the new set; status. Entry (PO): the AE's
  design for activating filters mid-flow. Inherits SecSpec's
  single-validated-writer AC (see "Coefficient sets: single validated
  writer"). Interim (174d, Architect): the measurement DEPLOY step is
  disabled, the session ends at "Filters ready, not deployed", and
  post-deploy verification is skipped and marked; the PO accepts this
  as a known deviation of 174d until US-178 (see US-174 RULING).
  Overlap resolved per PO 2026-10-26: US-178 = flow/plumbing, 174e =
  venue workflow UI on top. Scope (PO option (A)): the pipeline/flow
  only; a measurement run chains measure -> deploy (via the 174d safe
  path) -> post-deploy verify again, inside the existing wizard step.
  No new venue UI, no UX N2 work, no US-090/097 constraints. If the
  Architect says 174e was meant to include the deploy-from-session
  step, this split still applies; no PO round needed.
  SUPERSEDED (PO FINAL, 2026-10-26, option (C), replaces option (A)
  above): "US-178 is 174e slice 1 (PO 2026-10-26): the deploy/verify
  step is defined only in US-178." US-178 keeps its ID and P1; entry
  condition: the AE's activation design. The scope split stays: US-178
  owns the measure -> safe deploy -> verify-against-live step.
  Scope addition (Architect, 2026-10-26; 174d removes the measurement
  session's live verification sweep, session._run_verify and its
  PASS/FAIL display, because it would have measured the old filters),
  verbatim: "restore live verification (_run_verify, from git history
  before 174d) against the newly activated set". (The CM relay of the
  same text omits "from".)
  ENTRY CONDITION (PO ruling, 2026-10-26, HARD GATE): US-178 must NOT
  start before the F-262 fix has merged (see F-262).
  F-403 (capture redesign) does NOT gate US-178 (PO, 2026-10-26),
  unless the AE or Architect rules that the current capture can pass
  F-262's fail-closed check and still deliver wrong filters (see
  F-403).
  AMENDED (AE + Architect, 2026-10-26; narrows the F-403 line above;
  verbatim in F-403): F-403 gates US-178's amps-on activation and
  acceptance step. US-178 development and amps-off testing may start
  without it (still after the F-262 HARD GATE). Early lift: S4 lands
  before US-178 AND the F-262 diagnostic shows a median
  correlation-peak width ≤ 2 samples.
  Candidate addition (AE, 2026-10-26, see F-403): if the F-262
  diagnostic's pre-roll RMS shows the pink burst still on at the sweep
  start, that finding gates US-178 together with S4.
  GATE (AE, 2026-10-26, see F-404): F-404 (session leaves the gate as
  found; re-links production with the gate open after error or abort)
  blocks US-178 and any amps-on measurement.
- **F-262** Session filters use the raw room IR as the correction
  filter (P1, room lane; PO ruling 2026-10-26). Record
  docs/project/defects/F-262.md on main; this entry carries the
  2026-10-26 diagnosis and ruling.
  Diagnosis (worker-4, read-only, files /tmp/w4-proto/F-262/; via CM,
  relayed to the AE, Architect, QE and PO): a real bug.
  session.py:973-981 feeds the RAW room IR as correction_filters and
  skips generate_correction_filter, which filter_routes and
  venue_pipeline both run. Session filters therefore apply the room's
  response instead of correcting it, at an absolute level. Dates from
  67f24251. The non-determinism probably comes from the wall-clock
  capture alignment (pw_capture.py:197, the 1 s wait before link);
  unconfirmed. D-009: the sub reaches -0.42 dB at lag 44000 (the F-299
  gap). Combine maths is fine with correct inputs. QE (accounting):
  confirmed as a real bug on origin/main.
  PO RULING (2026-10-26): P1 in the room lane; worker-4 now. Order:
  the spec'd diagnostic run, then the fix to the AE and Architect
  spec; #65 C2 fits in between. F-262 comes before 174d; if #65 merges
  mid-F-262, 174d waits, unless another worker has disjoint fences (CM
  call). HARD GATE: US-178 must NOT start before the F-262 fix has
  merged.
  Extra AC (PO; UX/QE wording overrides): "FILTERS READY" only if the
  filters pass the closed-loop test (correction, D-009 level);
  otherwise a clear error state.
  QE test conditions T1-T8 for the fix PR (sent via CM): real code
  path with only capture mocked; red-first; closed loop; both
  branches; lag/noise matrix with fail-closed beyond the cutoff;
  determinism; listed mutations; strict E2E with branch B and the
  xfail removed, plus repeated-run evidence. If the 1 s pw_capture
  wait is a separate cause, it gets its own defect ID (not allocated
  yet).
  UPDATE (CM, 2026-10-26): the AE corrected the line ref to
  session.py:975. The Architect accepts AE S1-S8; S5's trim becomes
  one shared post-combine function. T4 order (QE; Architect + AE):
  average, then correct. Sequencing: F-262 from main first; 174d
  frozen, then merging main. The Architect has no objection on the
  CONDITION that the fix does not touch session._deploy_sync,
  /measurement/deploy or deploy.py. Diagnostic route (Architect
  proposal, PENDING the AE's concurrence): a CI scratch branch from
  289f1a72, N=20 local-demo runs, artifacts uploaded, nothing on the
  Mac.
  SETTLED (CM, 2026-10-26; supersedes "PENDING the AE's concurrence"
  above): the diagnostic spec is FINAL, verbatim in
  /tmp/cm-relay/F-262/diag-spec-FINAL.txt: the Architect's joint text
  with its decision rule REPLACED by the AE's AND rule (Architect
  concurs), plus the Architect's worker notes (a) and (b). worker-4 is
  building scratch/F-262-diag from 289f1a72. AE rule, verbatim:
  "CONFIRMED only if all three hold: onset spread > 100 ms across
  runs; every failing run's onset is >= ~1 s or within 50 ms of the 1
  s cutoff; and no passing run's onset is. Otherwise REFUTED: the
  worker reports to the AE and the Architect before any S3 work."
  QE rulings (verbatim in /tmp/cm-relay/F-262/qe-po-rulings.txt): Q1
  the residual gate (verify_minimum_phase_residual) replaces T3; add a
  check that the session (and filter_routes, if Q5 merges the gates)
  no longer gates on the old verify_minimum_phase; T7 mutation (a)
  (raw IR) must go red on the residual gate. Q3 1e-6 identity on
  noise-free captures only; with noise, closed-loop metrics within the
  AE's tolerance; T6 determinism unchanged. Q4 verdicts are the AE's
  call; the test names the capture layout as constants, states the
  expected verdict per lag explicitly (no computed or "either"
  outcome), has boundary pairs at both ends of the window, and pins
  negative lag (QE default: FAIL "capture misaligned" unless the AE
  rules otherwise). Q2 split accepted (see F-403): the new defect ID
  is filed before F-262 merges; T8 adapts by the 10x outcome (all 10
  PASS: remove branch B and the xfail; any named fail-closed "capture
  misaligned" with nothing deployed: branch B asserts only that error
  and the not-deployed state, xfail reason cites F-403; any other
  failure still fails F-262). Q7 the CI scratch/dispatch route for T8
  is confirmed on conditions (a)-(e): the exact head SHA under review
  with the checkout SHA logged; the same local-demo E2E command CI
  uses; 10 iterations, each with its own pytest summary line plus the
  session API outcome; the log uploaded and published by the CM in the
  review bundle; the PR branch's ci.yml unchanged, the scratch branch
  or dispatch input outside the PR and cleaned up afterwards. Open: Q4
  verdicts and Q5/Q8 (AE and Architect).
  PO on Q2 (verbatim in the same file): split accepted as worker-4
  proposes. F-262 (P1, now) = shared correction function, D-009 trim,
  strict session gate, fail-closed onset/window check on the current
  capture. Exit: "FILTERS READY" only for correct filters, otherwise a
  clear error. The capture redesign is a new defect (F-403).
  CORRECTION (CM, 2026-10-26; supersedes the "AE rule, verbatim"
  two-outcome text and the "decision rule REPLACED by the AE's AND
  rule" note above): the decision rule is CLOSED by the Architect's
  tie-break. The final rule is the Decision block in
  /tmp/cm-relay/F-262/joint-diag-final.txt (lines 22-28), verbatim:
  "CONFIRMED (wall-clock hypothesis) if ALL of these hold: the onset
  spread is > 100 ms; every failing run has its onset >= 950 ms or its
  IR peak within 50 ms of the 1 s cutoff; no passing run does. REFUTED
  if the spread is < 5 ms and no run fails. Anything else: report to
  the AE and the Architect before the alignment design is frozen.
  Either way, the alignment fix stays (AE S3: cross-correlation onset,
  no wall clock, deterministic for the same samples). The diagnostic
  only decides whether the 1 s pw_capture wait gets its own defect ID
  (QE T8)."
  SETTLED (CM, 2026-10-26; supersedes "Open: Q4 verdicts and Q5/Q8"
  above; verbatim in /tmp/cm-relay/F-262/joint-Q2-Q5-final-v2.txt and
  ae-qe-Q3-Q4-final.txt). Q2: worker-4's split (A, S5 shared D-009
  trim, S6 shared gate, fail-closed onset/window check on today's
  capture). Q5: ONE shared gate used by session.py,
  filter_routes._run_pipeline and venue_pipeline (run_venue_checks
  itself, or a function it delegates to); verify_minimum_phase stops
  being a gate everywhere (session.py:1045 and 1143,
  filter_routes.py:209 and 270); the source scan forbids it outside
  the shared gate; M7 mutates each former call site separately and
  records the failing test name for each. The residual metric is
  closed_loop.minimum_phase_residual_db only. Q8: reference_level_db
  and ref_band_hz are required in the payloads. Q3: the AE's
  tolerances. Q4: the AE + QE capture layout and verdict table. The 1
  s ir_duration cutoff goes as part of F-262. The -150 dB floor
  expectation is dropped (AE). Boundary with 174d: in
  filter_routes.py, F-262 touches only _load_correction_filters and
  _run_pipeline, not _verify_all_wavs, _run_deploy or /deploy.
  Diagnostic addendum: log the -3 dB width of the correlation peak per
  capture (median > 2 samples: the AE re-rules).
  UPDATE (CM, 2026-10-26): diagnostic run 40320962929
  (scratch/F-262-diag at 4134852f) is INVALID: 18 of 20 runs were
  driver_error, because the session wasn't reset after an error.
  worker-4 is fixing it for a rerun.
  Correlation-width rule (AE, 2026-10-26, verbatim in
  /tmp/cm-relay/F-262/findings-rulings-arch-ae.txt, sha1 6b9584ae):
  the ≤ 2-sample rule is judged against the generator.rs port, because
  that is what signal-gen actually plays; the session-array width is
  logged for comparison. "If the two widths differ a lot, that itself
  shows the session deconvolves against a different signal than the
  one played, and S2 is needed for correctness." Architect: also check
  whether the failing runs line up with the pink warm-up overlapping
  the sweep start; if they do, route it as the "anything else, report"
  outcome.
  UPDATE (CM, 2026-10-26): driver fix 2676be53 pushed; diagnostic
  rerun triggered.
  DECISION RULE v2 (joint AE + Architect, 2026-10-26; replaces the
  joint-diag-final.txt Decision block, lines 22-28, quoted in the
  CORRECTION above; verbatim in
  /tmp/cm-relay/F-262/diag-decision-rule-v2.txt, sha256 5ace2363). Why
  (verbatim): "in run 40320962929 (n=2 valid) both IR peaks sit within
  3.4 ms of the 1 s cutoff, and both onsets are > 1.26 s. The old
  verify_minimum_phase pass/fail is not ground truth. The run that
  "passed" did so by luck."
  - Validity: driver_error runs are excluded; the rerun needs >= 20
    VALID runs (complete or error), otherwise it fails loudly and no
    verdict is drawn.
  - Classification, independent of the verify result: TRUNCATED if the
    deconvolved IR peak lies within 50 ms of the ir_duration cutoff,
    OR the onset (cross-correlation peak against the generator.rs
    port, relative to the 0.5 s trim point) is >= 950 ms; OK
    otherwise.
  - Decision, verbatim: "CONFIRMED if >= 1 run is TRUNCATED AND every
    verify failure is TRUNCATED." Named cause "deterministic
    truncation" (settle + pre-roll exceed ir_duration_s): onset spread
    < 5 ms and every run TRUNCATED; named cause "jitter": onset spread
    > 100 ms; anything in between reported as measured; the named
    cause goes to the QE's T8 under the new defect ID. "REFUTED if no
    run is TRUNCATED. The worker then reports to the AE and the
    Architect before any S3 work." Onset spread is always reported; it
    names the cause, it does not decide.
  - Reported by name without changing the verdict: every TRUNCATED run
    that ended "complete", with its
    closed_loop.minimum_phase_residual_db (evidence that the old gate
    accepts wrong filters; supports S6).
  - Unchanged: the AE's <= 2-sample correlation-width rule against the
    generator.rs port. Rerun logging (AE): peak distance to the window
    end; correlation -3 dB width for both references;
    closed_loop.minimum_phase_residual_db on every produced WAV;
    pw-record and pre-roll start times relative to the sweep start.
  UPDATE (CM, 2026-10-26): the diagnostic is now 293cf822, run
  40322683521, carrying decision_v2 in summary.json plus the AE's four
  logging items. The 2676be53 and 7c38c463 runs were cancelled.
  AE ruling (2026-10-26, via CM): width trigger > 1.5 × the reference
  autocorrelation width (4.97 samples); the gate is unchanged at
  -40/-60; the onset/window check is mandatory and runs before the
  gate. Reason: sat_left reads an identical -48 dB at lag 48000 and at
  lag -4800.
  QE (2026-10-26, via CM): M9 accepted (bypass the onset check; it
  must go red on the lag rows -241/-300/47521/60000).
  UPDATE (CM, 2026-10-26; supersedes "the diagnostic is now 293cf822"
  above): the diagnostic is now aedf4a82, run 40322886856. It adds the
  normalized correlation peak and the 1.5× width trigger (AE ruling
  2). The CM cancelled the 293cf822 run 40322683521.
  UPDATE (CM, 2026-10-26): diagnostic run 40322886856 SUCCESS;
  decision rule v2 verdict CONFIRMED / jitter. Validity is with the AE
  and the Architect; the fix branch is held.
  UPDATE (CM, 2026-10-26): the joint AE + Architect validity ruling is
  drafted and released by the Architect; the AE's release is pending.
  PM cross-ref: it is not a joint ruling until both have released the
  same sha. worker-4 sent an analysis bearing on the S3 fix design
  (raw xcorr vs whitened onset); the CM routed it to the AE and the
  Architect.
  UPDATE (CM, 2026-10-26; supersedes the line above): there is still
  no sha released by both authors. The AE voided its release of
  b64aad93 + 9833ce7c + 27f46624; the Architect released that same set
  and voided v2. The CM sent one message to both: the Architect is the
  single writer; the ruling splits into (a) diag validity (one new
  file) and (b) the S3 onset/misalignment method; new filenames only.
  Frozen copies: /tmp/cm-relay/F-262/frozen/. worker-4's analysis:
  /tmp/w4-proto/F-262/diag-40322886856-analysis.txt (sha256 3932d0ba,
  verified at PM read). worker-4 holds.
  UPDATE (CM, 2026-10-26; supersedes the line above): F-262 ruling is
  JOINT and final. Set A is released by both: the AE ("release set A:
  b64aad93 9833ce7c 27f46624 27fc548d") and the Architect; the CM
  re-verified all four shas on disk and in the frozen copies (also
  verified at PM read in /tmp/cm-relay/F-262/frozen/).
  - Diag validity (b64aad93 + 9833ce7c + 27f46624): VALID, CONFIRMED,
    cause "jitter + a deterministic overshoot of at least 262 ms".
  - S3 onset method (27fc548d, AE-written): the earliest local maximum
    within 12 dB of the global maximum on the deconvolved IR; a 30 dB
    SNR floor; the 6 dB second-peak rule withdrawn. v3 item 7's -20 dB
    is not adopted.
  - VOID: 430b07a4, 064175e6, f7a4fc20, bbf4587b.
  - worker-4 is BRIEFED and the fix branch is authorised. 174d stays
    frozen until F-262 merges.
  - UPDATE (CM, 2026-10-26, after v249): worker-4 raised six
    implementation findings on set A, frozen as
    /tmp/cm-relay/F-262/frozen/: w4-setA-impl-questions-e3900cbf.txt
    (sha256 e3900cbf, verified at PM read).
     F1-F5: the AE wrote the ruling, frozen as
     /tmp/cm-relay/F-262/frozen/: ae-setA-F1-F5-ruling-a8386f4b.txt
     (sha256 a8386f4b, verified at PM read); awaiting the Architect's
     release.
     F6: with the Architect.
     Nothing has gone to worker-4 yet (CM).
  - UPDATE (CM, 2026-10-26, after v250; supersedes "awaiting the
    Architect's release", "F6: with the Architect" and "Nothing has
    gone to worker-4 yet" above): both rulings are released and
    relayed to worker-4.
     F1-F5 (a8386f4b): the AE wrote it, the Architect released it (per
     CM relay; the frozen file's Architect release line is blank, and
     no separate frozen release file was found at PM read). F3 drops
     (iv) as a gate for room captures; it supersedes the "fail closed
     if it can't be computed" clause of b64aad93 s3 / 9833ce7c item 1,
     for room captures only. F2 adds an S2 AC to F-403 (see F-403).
     Release proof (CM, 2026-10-26; supersedes the "per CM relay ...
     no separate frozen release file" note above): the CM release
     record /tmp/cm-relay/release-record-20261026.txt (sha256
     aca30fe1, verified at PM read) holds the release lines verbatim.
     Released files are never edited; these releases were given by
     message (CM). Architect on a8386f4b: "F-262: release a8386f4b
     (the AE's F1-F5 ruling, sha256
     a8386f4b02807a4aa1744f29848eab2d04769b412accd09606f98ac6eb0abf84,
     read and sha-verified at read time). F3 supersedes my 9833ce7c
     item 1, for room captures only, and I agree with that. No
     objections." AE on dfffcfbf: "release dfffcfbf". The same record
     holds the QE's "release 5e123a6b" for the #63 P17/Q1 joint
     ruling.
     Architect release file (CM, 2026-10-26; cite alongside aca30fe1):
     /tmp/cm-relay/F-262/frozen/:
     F1-F5-architect-release-a8386f4b-eb621b26.txt (sha256 eb621b26,
     verified at PM read). It records the release given by message:
     "the Architect releases the AE's F1-F5 ruling ... as written. No
     objections. F3 supersedes 9833ce7c item 1 for room captures only,
     and I agree with that."
     F6 (dfffcfbf): the Architect wrote it, the AE released it; frozen
     as /tmp/cm-relay/F-262/frozen/:
     F6-source-scan-architect-dfffcfbf.txt (sha256 dfffcfbf, verified
     at PM read). worker-4's source-scan proposal is ACCEPTED with
     tightening: AST scan of src/ (minus tests/ and the
     room-correction mock/); generate_correction_filter,
     verify_minimum_phase and verify.run_all_checks forbidden outside
     an exact (file, def) allowlist that can only shrink; runner and
     generate_bose_filters quarantined from src/web-ui/ and the
     room_correction package; mutations (a)-(c) for the QE next to M7.
  - F-262 follow-up (Architect, in F6 dfffcfbf; "one-liner; low
    priority; not a US-178 or US-174e gate"; no ID allocated),
    verbatim (list bullets flattened to "; "): "F-262 follow-up:
    retire, or re-route onto correction_from_measurement plus the
    shared gate: the legacy runner.py run_full_pipeline /
    run_stage_correct / run_stage_verify; verify.run_all_checks;
    generate_bose_filters.py. Then empty the F-262 source-scan
    allowlist. Fix the deploy.py:8/:99 run_all_checks wording with or
    after 174d." AE (via CM): a manual human run of the legacy CLI is
    the only remaining path, and this line covers it.
  - UPDATE (CM, 2026-10-26, after v253): DRAFT PR #66 is the F-262 PR.
    Branch fix/F-262-shared-correction at d677f253 (base 29f5c61f; 4
    commits, 19 files, +985/-145): worker-4's c1-c4. CI run
    40338944793 in progress; nothing has run locally (CM).
     Still to do: c7 (onset/window, per a8386f4b), c8 (T8 xfail
     removal and the F-403 doc), and mutations M1-M9 (CM).
     New worker-4 findings on d677f253, frozen verbatim as
     /tmp/cm-relay/F-262/frozen/: w4-c1c4-findings-d677f253.txt
     (sha256 b76bc353, verified at PM read). (1) the closed-loop gate
     uses the AE residual bands, not the level-reference band; (2) the
     closed loop does not catch a dropped normalize_ir_level, two unit
     tests guard it instead; (3) bandpass and 3-/4-way profiles now
     fail closed in all three correction paths ("Measurement
     rejected"), crossover-only generation unchanged; (4) the session
     and filter_routes gate is now run_venue_checks plus the closed
     loop, stricter than the old verify_minimum_phase; (5) the
     source-scan allowlist is pending a ruling. Rulings: (1)-(4) the
     AE writes, the Architect releases; (5) is the Architect's alone
     (CM).
     Behaviour change pending the AE ruling (CM): bandpass and
     3-/4-way profiles now fail closed with "Measurement rejected"
     (item 3).
     Possible conflict (CM): worker-4's allowlist names
     verify.run_all_checks, which F6 makes a forbidden callee. PM
     cross-ref, for the Architect (no ruling implied): F6 item 3
     itself allowlists "verify.py run_all_checks" as an enclosing def
     (verify_minimum_phase :487) and run_full_pipeline's call of
     run_all_checks (:280). worker-4's list names
     "generate_bose_filters.verify_all" where F6 names the def
     generate_bose_filters, and it does not list the run_full_pipeline
     run_all_checks :280 entry.
  - UPDATE (CM, 2026-10-26, after v254): all rulings on the d677f253
    findings are in and relayed to worker-4 (CM). Files in
    /tmp/cm-relay/F-262/frozen/, each verified at PM read.
     Item (5), Architect sole writer:
     F6-reconcile-d677f253-architect-e65ced02.txt (sha256 e65ced02).
     worker-4's allowlist is RIGHT on the call sites. F6 correction
     (the Architect's own error): generate_bose_filters.py:192 is
     inside def verify_all, so (generate_bose_filters.py, verify_all)
     replaces F6's (generate_bose_filters.py, generate_bose_filters).
     Six scan changes S1-S6, all in test_shared_correction.py, no
     production code: S1 run_all_checks only from
     runner.run_full_pipeline (:280); S2 entries keyed by
     repo-relative path; S3 scan every .py under src/; S4 stale
     entries fail; S5 aliased imports of forbidden names are
     offenders; S6 import quarantine of runner /
     generate_bose_filters. Every other part of F6 stands. The
     possible run_all_checks conflict in v254 did not exist; the
     Architect confirms both PM cross-ref points are covered
     (verify_all; :280 via S1) (CM).
     Items (1)-(4), AE sole writer, Architect released:
     ae-c1c4-items1-4-ruling-dc9e529d.txt (sha256 dc9e529d); release
     lines verbatim in /tmp/cm-relay/release-record-20261026-d.txt
     (sha256 a8bf9931). All four ACCEPTED. Additions: (1) log-only
     per-channel 500-4000 Hz corrected/uncorrected deviation; (2) the
     QE adds a mutation that drops normalize_ir_level, killed by the
     two required T1 unit tests; (3) the reject text must name the
     cause, verbatim: "Measurement rejected: room correction not
     supported for bandpass (3-/4-way) profiles"; (4) required T1
     assertion: d009_trim_db <= 0.0 and no speaker FIR peak above -0.5
     dB after the trim, and the UI label must not say
     "verify_minimum_phase". Architect note (record (d)): "S5"/"S6" in
     item (4) are the AE's labels, not the scan changes S1-S6 in
     e65ced02.
     This resolves the item 3 behaviour change above: the bandpass and
     3-/4-way fail-closed is ACCEPTED by the AE.
  - F-262 follow-up line amended (Architect, e65ced02): the PM backlog
    line from F6 now reads "generate_bose_filters.py (verify_all)" for
    the legacy entry.
  - F-262 follow-up (AE, dc9e529d item (1); no ID allocated; no
    P-level given), verbatim: "PM backlog: a gating HF check on the
    FDW-windowed IR (the same window the correction used)."
  - F-262 follow-up (AE, dc9e529d item (3); no ID allocated; no
    P-level given), verbatim: "PM backlog: a bandpass residual band
    and level-reference band (AE to define) before any 3-/4-way
    venue."
  - UPDATE (CM, 2026-10-26, after v255): PR #66 head e325c4ba
    (434cfe99 F6 scan; e325c4ba c7 capture alignment), pushed and
    ls-remote verified. CI 40343196576 running (CM).
     CI 40338944793 at d677f253 FAILED: 10 failed, 928 passed, 1
     skipped, 7 errors. Cause (CM):
     configs/speakers/profiles/f262-parity.yml missing from the nix
     source, plus session filter-verification failures at
     session.py:1017. worker-4 is diagnosing.
     c7 (worker-4, frozen /tmp/cm-relay/F-262/frozen/:
     w4-e325c4ba-c8-ruling-request-0e25d355.txt, sha256 0e25d355,
     verified at PM read): the IR is no longer cut at the capture
     start but kept from 5 ms before to 500 ms after the detected
     direct sound; an untrusted capture stops the session with
     "capture misaligned" and writes no filter files; 2 s post-roll;
     the room sim is causal. The 69 cases in test_capture_alignment.py
     pass as plain function calls (no local pytest);
     test_capture_alignment_session.py has not run anywhere yet (CI is
     its first run). worker-4 also fixed a bug that halved the
     measured cross-correlation width.
     c8 (removing the two T8 e2e xfails) PENDING an AE ruling; the AE
     is single writer, the QE releases (CM). worker-4's model of
     local-demo, against the 3.0 dB closed-loop limit: Left passes at
     +1.92 dB; Sub1 fails at +4.73 dB (2 s sweep) / +3.60 dB (5 s),
     from the F2 interim rule (session sweep vs the sweep signal-gen
     plays); Sub1 against the played sweep passes by only 0.01-0.03 dB
     (the F-403 S2 fix); the mock room Left passes by 0.03 dB.
     worker-4: the thin margins are a risk for the required 10
     consecutive local-demo runs either way; the API e2e test measures
     Left only. Options worker-4 gave: (1) remove the API test's xfail
     now and point the browser test's xfail at F-403 S2; (2) pull S2
     into F-262 (sub margin still 0.03 dB); (3) a different ruling.
     worker-4 note (0e25d355): "a room capture at -40 dBFS noise
     always fails the signal-to-noise check, which matches one written
     spec but not a literal reading of the lag/noise table." Mutation
     runs and the source-scan follow-ups stay parked under quiet mode
     (worker-4).
     worker-4 flags A1-A7: the CM asked the PM to carry them over; the
     PM has no A1-A7 text (0e25d355 mentions only "a few smaller
     notes"). Not recorded until the CM sends the source.
  - F-262 follow-up, worker-4's wording (via CM; the CM's ellipsis
    kept): "retire or re-route the legacy CLI paths … onto
    correction_from_measurement + run_correction_gate". PM cross-ref:
    the same item as the Architect's F6 follow-up line above; no new
    entry.
  - F-403.md owner (worker-4 asked; via CM): PM cross-ref: the F-403
    entry records "DECIDED (CM call, 2026-10-26)":
    docs/project/defects/F-403.md goes inside the F-262 PR, written by
    worker-4 with the QE's minimum content, and the TW reviews it
    under Rule 13. The PM only allocated the ID. PM asked the CM to
    confirm that call to worker-4.
  - UPDATE (CM, 2026-10-26, after v256): A1-A7 RETRACTED by the CM
    (the label came from the CM's own notes; no source exists;
    0e25d355 is all there is). Supersedes the "worker-4 flags A1-A7"
    line above. F-403.md: the CM agrees worker-4 writes it under the
    earlier CM call, and confirms this to worker-4 with the c8 relay.
  - c8 ruling (AE sole writer; QE releaser, NOT yet released):
    /tmp/cm-relay/F-262/frozen/: ae-c8-xfail-ruling-f8a014c7.txt
    (sha256 f8a014c7, verified at PM read). Option (a) with
    conditions; option (b) (pull S2 into F-262) rejected.
     R1: MAX_POSITIVE_DEVIATION_DB stays 3.0 dB; no test, xfail or
     local-demo path may use a looser limit.
     R2: REMOVE the API xfail
     (service-integration/test_measurement.py:174) in F-262 (Left
     only, +1.92 dB, 1.08 dB margin), only if the R5 AC passes. If any
     run fails, the xfail goes back with the reason "F-262 c8: API
     closed-loop fails in local-demo, see run log", and the result is
     a finding, not a retry.
     R3: KEEP the browser xfail (e2e/test_measurement.py:243),
     strict=False, re-pointed to F-403 S2 with the measured values;
     remove the old "min-phase check" text; an XPASS is reported, not
     a reason to remove it.
     R4: before the browser xfail goes, worker-4 reports for Sub1 and
     mock-room Left with the S2 (played-sweep) reference: the
     frequency of the max positive deviation, the uncorrected
     deviation there, whether the 18 dB MAX_CUT_DB cap is reached, and
     the onset and lag picked. AE rules: cap reached at a sim mode
     deeper than 18 dB -> fix the local-demo room sim's mode depth
     (test fixture), never the limit or the cap; cap not reached -> a
     correction or alignment defect (new F-number, via PM). Owner of
     this follow-up, verbatim: "F-403 S2 (PM/QE allocate; it is not
     written by worker-4 per the request)." PM cross-ref: no ID
     allocated now; a new F-ID only if the AE rules "cap not reached".
     R5 (10-consecutive-runs AC, for R2 and later the browser test):
     10 consecutive local-demo runs, each a fresh session, no retries
     or single-failure reruns; every run logs the per-channel
     closed-loop max positive deviation and band; PASS needs all 10 at
     or below 3.0 dB AND a worst-run margin of at least 0.5 dB (max
     deviation at most 2.5 dB); the min/max/spread log goes with the
     PR evidence for the QE.
     R6 (-40 dBFS SNR note): no production change; the 30 dB SNR floor
     (27fc548d) stands; rejection is the fail-safe direction. The
     lag/noise table's -40 dBFS row expects "rejected (SNR)" and cites
     27fc548d: in F-262 if it is a one-row test change, otherwise a PM
     backlog line (not yet known which).
     QE input to the c8 ruling (QE,
     /tmp/pr64-qe-countprofile-f715538e.md, sha256 96abe4fb, verified
     at PM read): test_full_session_api went XPASS, XPASS, XFAIL in CI
     runs 40314977506, 40320048783, 40333713247, all before c7
     (e325c4ba). Removing its xfail needs a passing streak on the
     F-262 branch head as evidence, not just the model's +1.92 dB Left
     margin; the 10-consecutive-run AC applies to it too.
  - UPDATE (CM, QE, 2026-10-26, after v257): c8 ruling f8a014c7
    RELEASED by the QE (supersedes "NOT yet released" above) and
    relayed to worker-4. Release lines verbatim in
    /tmp/cm-relay/release-record-20261026-e.txt (sha256 36444390,
    verified at PM read). QE evidence rule for R5, verbatim: "it must
    be run at the F-262 head that removes the xfail, which the AE
    confirmed. If a later head touches the measurement or closed-loop
    path, the streak must be re-run there; a docs-only change carries
    it over." The R5 log needs min, max and spread per channel.
     QE (same record): "F-403 still needs writing. The PM allocates
     it." PM cross-ref: F-403 is already allocated (see F-403); per
     the CM call recorded under F-403, confirmed by the CM after v256,
     worker-4 writes docs/project/defects/F-403.md inside the F-262
     PR.
  - CI 40343196576 at PR #66 head e325c4ba FAILED (CM): 12 failed /
    932 passed / 1 skipped / 7 errors. The same f262-parity.yml
    FileNotFoundError and the same session filter-verification
    failures, plus 3 new failures in test_capture_alignment_session.py
    (lag cases 71497 / 24000 / -223). Excerpt
    /tmp/cm-relay/F-262/ci-40343196576-e325c4ba-excerpt.txt (sha256
    885f52e8, verified at PM read). worker-4 is diagnosing.
  - UPDATE (CM, 2026-10-26, after v258): new PR #66 head 4396e03c (AE
    items 1, 3, 4 of dc9e529d) pushed; CI 40344885535 queued. #66 is
    now behind main because #64 merged (ff091e5f).
  - UPDATE (CM, 2026-10-26, after v259): head ff985455 fixes the 7
    f262-parity.yml errors (the session's generate_filter_chain_conf
    read the profile from disk by name; the test now mocks it, as
    test_measurement_session does). CI 40345460992 running;
    40344885535 at 4396e03c superseded.
  - Cause 2 (worker-4 finding,
    /tmp/cm-relay/F-262/frozen/w4-gate-xo-finding-b4c66788.txt, sha256
    b4c66788, verified at PM read): the shared gate
    (verify_minimum_phase_residual: residual <= -40 dB, last-5% tail
    <= -60 dB) rejects CROSSOVER-ONLY filters for every 48 dB/oct
    profile, before any correction. 10 of 11 real profiles fail; only
    the 24 dB/oct 2way-200hz-markaudio-ultimax (used by the venue sims
    and the parity test) passes. All 11 CI failures (8 session "Filter
    verification failed", 3 test_capture_alignment_session) come from
    this.
     Two failure modes (worker-4): (a) tail, a 48 dB/oct sub LP plus
     subsonic HPF not decayed within 16384 taps (-54 to -58 dB); (b)
     residual -13 to -37 dB even with a good tail. Hypothesis, not
     proved (worker-4): the residual is partly a float32 artifact
     (test profile sat_left r-71.6 in float64, -41.9 after the cast).
     Even the passing profile has little float32 margin (venue sub1
     -46.6). Before F-262, session and filter_routes used
     verify_minimum_phase, which these filters pass.
     Open for the ruling (worker-4): (i) the metric, (ii) thresholds
     or the tail rule for subs with subsonic HPFs, (iii) a different
     check for crossover-only / non-venue paths, (iv) a generation
     change. The AE writes the ruling, the Architect releases it (CM).
     worker-4 changes no gate, threshold or all_pass test until then.
     c8 is held: its 10-run AC needs a green session.
  - UPDATE (CM, 2026-10-26, after v260): CI 40345460992 at ff985455
    still running. #66 is behind main (#64 merged), so it needs a
    main-merge before merge; that voids any approvals given before it
    (CM).
  - UPDATE (CM, AE, 2026-10-26, after v261): AE gate-xo ruling v1
    (/tmp/cm-relay/F-262/frozen/ae-gate-xo-ruling-v1-0aac380f.txt,
    sha256 0aac380f, verified at PM read). Single writer AE; releaser
    Architect; AE released, Architect NOT yet released, so not final.
    Summary (PM, not a substitute for the file): AE finds the cepstral
    reconstruction does not converge for high-order unit-circle zeros,
    so the -40 dB residual threshold rejects true min-phase 48 dB/oct
    filters; "That is a false positive in the gate, not a filter
    defect." and "This is fidelity (pre-ringing), not safety."
    Directions (iii) and (iv) rejected.
     G1 MIN_PHASE_MAX_RESIDUAL_DB becomes -3.0 dB (gross-error gate;
     residual still logged and shown). G2 tail rule: last 5% <= -45 dB
     re total AND decaying vs taps 90-95%; REQUIRED: session and
     filter_routes pass mandatory_hpf_hz to run_venue_checks; required
     test for an identity with mandatory_hpf_hz and an export without
     the HPF. G3 required controls P1-P3 PASS, N1-N5 FAIL (P3 = all 11
     profiles parametrized; worker-4 sends the P3 table). G4 = F-408
     (follow-up, not blocking F-262). G5: D-009 -0.5 dB, closed loop
     3.0 dB, 18 dB HPF limit and bandpass fail-closed stay; dc9e529d
     (4) amended; c8 10-run AC (f8a014c7) starts once the session is
     green with G1-G3.
  - UPDATE (CM, 2026-10-26, after v262): CI 40345460992 at ff985455
    FAILED: 12 failed / 941 passed / 1 skipped, all "Filter
    verification failed" (test_capture_alignment_session x3,
    test_measurement_integration,
    test_measurement_pipeline_integration x4, test_measurement_session
    x4). Excerpt
    /tmp/cm-relay/F-262/ci-40345460992-ff985455-excerpt-v2.txt (sha256
    3b161130, verified at PM read). PM cross-ref: the class worker-4's
    finding b4c66788 explains.
  - Gate ruling v1 NOT released (release record (g),
    /tmp/cm-relay/release-record-20261026-g.txt, sha256 d7079ade,
    verified at PM read). Architect points 96e9b156: G1, the rejection
    of (iii)/(iv), G2(a), the mandatory_hpf_hz requirement and test,
    G3, G4 and G5 AGREED. A1 REQUIRED: G2(b) needs a floor, because
    for a well-decayed filter both tail windows hold only float32
    noise, so (b) "would reject correct filters, depending on the
    measurement or venue"; proposed: (b) applies only above a floor,
    e.g. -100 dB re total (the AE words it), plus a new G3 control P4:
    a filter whose last 10% is pure float32 noise must PASS G2 for at
    least 20 seeds or dither variants. Release condition, verbatim:
    "v2 with A1 folded in (wording yours). I release it on its sha. I
    need no further change." The AE writes v2.
  - UPDATE (CM, 2026-10-26, after v263; supersedes "v1 NOT released
    ... The AE writes v2" above): gate ruling v2
    /tmp/cm-relay/F-262/frozen/ae-gate-xo-ruling-v2-91eca61e.txt
    (sha256 91eca61e, verified at PM read) RELEASED by both co-authors
    and relayed to worker-4. Release record (h)
    /tmp/cm-relay/release-record-20261026-h.txt (sha256 eb2b06d3,
    verified at PM read). AE: "AE: matches, release 91eca61e."
    Architect: "release 91eca61e. I checked the sha at read time. The
    diff from v1 0aac380f contains only the header, G2(b) with its
    -100 dB floor (A1, as I asked), G3 P4 with 20 or more seeds, and
    the G4 A2 data. Nothing else changed." v1 0aac380f was never
    relayed.
     Changes from v1 (PM diffed the two files; matches the Architect's
     list): G2(b) applies only above a floor; if the last-5% energy is
     <= -100 dB re total, (b) passes; above it, the last 5% must not
     exceed taps 90-95%. G3 adds P4: P1 and the 24 dB/oct sat filter
     with their last 10% replaced by float32-level noise (about -145
     dB re total) must PASS G2 for at least 20 seeds each. G1, G2(a),
     G3 P1-P3/N1-N5, G4 and G5 unchanged; the c8 10-run AC starts once
     the session is green with G1-G3.
  Before the first amps-on measurement (non-blocking one-liners; no
  F-ID, no P-level given):
  - AE, verbatim: "F-262 item 7 Architect note: before the first
    amps-on measurement, the AE sets the (i) pre-arrival window to
    exclude the exp-sweep harmonic images (onset - T*ln(5)/ln(f2/f1)
    .. onset)."
  - Architect: in sweep deconvolution, harmonic-distortion products
    land before the linear IR, inside the O3(ii) pre-onset SNR window.
    The AE either confirms they stay >= 30 dB down at measurement
    level or excludes that region. Irrelevant in the sim.
  - UPDATE (CM, 2026-10-26, after v265): head 7011419d pushed (G1-G3
    of ruling v2 91eca61e); CI 40348528240 running. P3 table and
    finding H1: /tmp/cm-relay/F-262/frozen/w4-g3-p3-h1-07e5efbd.txt
    (sha256 07e5efbd, verified at PM read). Every buildable channel
    passes G1+G2. Not buildable: 2way-80hz-ported (identity
    sub-ported-15 missing, F-239) and workshop-xrk10f-fullrange
    ("filter_type 'fullrange' unknown"). Worker-4, verbatim: "N4 (bug
    A, home_lab): residual PASSES on all 3 files (-86.3/-67.1/-27.2),
    so G1 alone does NOT catch it; the closed loop fails all 3".
  - H1 (worker-4, verbatim): "verify_mandatory_hpf false-fails lowpass
    channels." Its passband reference is the mean gain over 2x..10x
    mandatory_hpf_hz, which for subs is mostly LP stopband (e.g.
    2way-80hz-sealed sub 16.7 dB, s218 sub -2.6, horn-sub -7.6: FAIL
    against the 18 dB threshold). Worker-4: in CI,
    test_measurement_session FilterGenSync 4Way "will still fail at
    7011419d". Candidate fix, not implemented: "reference = max gain
    over the window (or over the channel's own passband), threshold 18
    dB unchanged." Ruling: the AE writes it, the Architect releases it
    (CM). PENDING.
  - UPDATE (CM, AE, Architect, 2026-10-26, after v266; supersedes
    "PENDING" above): H1 RELEASED. AE ruling
    /tmp/cm-relay/F-262/frozen/ae-H1-hpf-ref-ruling-cfe9bf66.txt
    (sha256 cfe9bf66, verified at PM read); Architect release record
    (i) /tmp/cm-relay/release-record-20261026-i.txt (sha256 e6ba4317,
    verified at PM read). Relayed to worker-4 together with F-409
    (CM).
     H1-1, verbatim: "reference = MAX gain (dB) over
     [mandatory_hpf_hz, min(20 kHz, 0.95*Nyquist)]"; PASS if
     attenuation >= 18.0 dB, check frequency and threshold unchanged.
     The AE rejects the max over the old 2x-10x window. The details
     key passband_level_db becomes passband_peak_db.
     H1-3 (T1, hermetic, fail never skip): five must-pass and four
     must-fail synthetic filters, plus the 2way-80hz-sealed sub
     regression (attenuation >= 40 dB). H1-4: re-run P3 at the new
     head; AE, verbatim: "If any REAL profile channel fails at the new
     reference, do NOT relax the 18 dB." FilterGenSync 4Way is
     expected to pass. H1-5: v2 G1-G5 and the F-408 addendum 165ae71a
     unchanged; N4 stays asserted on the closed loop.
     Architect, verbatim: "release cfe9bf66. I checked the sha at read
     time against verify.py:293-338 at 7011419d."
  - UPDATE (CM, 2026-10-26, after v267): head 0c592da1 "fix(F-262):
    mandatory-HPF check references the passband peak (H1)" pushed
    (PM-verified on origin, parent 7011419d). CI 40349317717 running;
    the 7011419d run 40348528240 was cancelled by the concurrency
    group. Evidence:
    /tmp/cm-relay/F-262/frozen/w4-h1-p3-rerun-0b1b6062.txt (sha256
    0b1b6062, verified at PM read).
     Controls (float32): the five must-pass cases pass (24.9 / 28.6 /
     52.8 / 149.0 / 23.2 dB) and the four must-fail cases fail (-0.0 /
     3.4 / 6.2 / 12.4 dB). Worker-4: HP2000 "is 149.0 here vs 357.5
     because float32 floors the stopband".
     P3 re-run: every buildable channel passes G1+G2 and the HPF check
     at the new reference, including the nine former false-fails
     (lowest: pa-2way-onken sub 42.0 dB). Still unbuildable:
     2way-80hz-ported (FileNotFoundError) and
     workshop-xrk10f-fullrange (ValueError). FilterGenSync 2WAY sub1
     50.0 dB and 4WAY sub 48.0 dB both pass. No D-031 report (CM).
  - UPDATE (worker-1 via CM, 2026-10-26, after v271): in CI
    40356547804 (#68 at 51fae218), test_full_session_api (class
    TestLocalDemoMeasurementAPI,
    tests/service-integration/test_measurement.py) XPASSed. Its
    non-strict xfail
    (src/web-ui/tests/service-integration/test_measurement.py
    l.173-178 at 0cb35f0c, PM read) cites "F-262: room-sim IRs fail
    filter verification (min-phase check)". It was XFAIL in
    40348754608. Worker-1: the F-394 RPC/PW-env fix probably made it
    pass. Owner: F-262 / PR #66; "The xfail marker may need to come
    off." No P-level given.
  - UPDATE (CM, 2026-10-26, after v272): c8 fence ask. worker-4 wanted
    to add closed_loop_max_db and closed_loop_band_hz per corrected
    channel to verify.py gate_summary, with the data from the
    verify_closed_loop details already computed (CM: one line, no
    logic change); this was outside the c8 fence. Planned in-fence
    (CM): service-integration/test_measurement.py removes the xfail
    (R2), asserts <= 3.0 dB per channel and emits an "F-262-AC"
    warnings line; e2e/test_measurement.py gets the new xfail reason
    (R3).
     Fence r1 (CM, 2026-10-26): /tmp/cm-relay/F-262-fence-r1.txt
     (sha256 b1f0fcbf, verified at PM read). The earlier fences were
     message-only; r1 does not reconstruct them. Commit 971725d7 (with
     the held verify.py line) is VOID and was never pushed; 65af5ee2
     (R2/R3 test files only) is queued for push. OWNED for c8
     (worker-4): the two test_measurement.py files,
     docs/project/defects/F-403.md (NEW) and its defects-index row.
     FENCED pending a ruling: verify.py (gate_summary keys); fence r2
     follows. FENCED: everything else. No Pi session; no nix
     build/run/develop (disk hold).
     PM cross-ref (read-only git, origin, at PM read; quoted in fence
     r1): verify.py differs from main on no open origin branch except
     fix/F-262-shared-correction (head e7afdb36). gate_summary feeds
     the API responses at filter_routes.py:299 and session.py:1204, so
     the two keys change the API payload (the Architect's call on the
     API shape; the AE's on the R5 fit). QE release record (e): a head
     that touches the closed-loop path needs the R5 streak re-run
     there.
  - QE c8 answers (QE via CM, 2026-10-26): frozen file
    qe-c8-R5-ci-F403-min-abfd33d7.md in /tmp/cm-relay/F-262/frozen/
    (sha256 abfd33d7, verified at PM read). Q1, PM summary: 10 CI
    workflow_dispatch runs count as the R5 local-demo runs, under
    conditions. One head (the xfail-removal head; each checkout sha
    equals it). The CM keeps a dispatch ledger and every run counts:
    nothing dropped, cancelled or re-run; a red run ends the series,
    and per R2 the xfail goes back as a finding; only a run that fails
    before the local-demo stack's first step can be ruled void, by the
    QE, with its log. Each run shows the API closed-loop test PASSED
    (SKIPPED, XFAIL or XPASS don't count) and the browser test still
    xfail strict=False. One "F-262-AC ch=… max=… band=…" line per
    measured channel per run, or the run is void. Pass: all 10 max <=
    3.0 dB and the worst <= 2.5 dB; 10/10 with a margin under 0.5 dB
    is UNSTABLE, a finding. Evidence: the ledger, the per-run AC lines
    (CM extracts and freezes them), worker-4's min/max/spread; the QE
    recomputes it. Q2: the F-403 minimum content (see F-403).
  - F-403.md writer (PM allocation, 2026-10-26; CM accepted;
    supersedes the PM cross-ref above that pointed at the CM call, and
    the CM's after-v256 confirmation): AE R4 (f8a014c7) says,
    verbatim, "it is not written by worker-4 per the request", and the
    QE's Q2 heading (abfd33d7) says, verbatim, "written by the
    PM-allocated writer, not worker-4, per R4". Both postdate the CM
    call recorded under F-403. PM proposes the TW as writer, from
    frozen sources only (QE Q2 content, the AE's severity, worker-4's
    R4 data as a frozen file via the CM; pending sections marked so).
    The CM asked the TW (answer pending); if the TW can't, the CM
    names another writer, not worker-4. worker-4 holds. The file still
    lands inside the F-262 PR.
     Fence r2 (CM, 2026-10-26; supersedes r1):
     /tmp/cm-relay/F-262-fence-r2.txt (sha256 084ad898, verified at PM
     read). Change vs r1: F-403.md and its index row are REMOVED from
     worker-4's OWNED set (reason: QE Q2 heading and AE R4, which
     override the earlier CM call). OWNED for c8: the two
     test_measurement.py files only. verify.py stays FENCED pending
     the Architect (API shape) and the AE (R5 fit). FENCED: everything
     else, including docs/project/defects/**. worker-4 may supply the
     R4 data as a frozen file via the CM, for the F-403 writer.
  - UPDATE (CM, Architect, AE, 2026-10-26, after v275): fence r3
    /tmp/cm-relay/F-262-fence-r3.txt (sha256 48133641, verified at PM
    read; supersedes r2 084ad898). verify.py moves to OWNED for the
    gate_summary change ONLY (the two keys closed_loop_max_db and
    closed_loop_band_hz; no other verify.py edits).
    test_shared_correction.py is ADD-only, for the C1 early-FAIL test.
    docs/project/defects/** stays FENCED (the TW writes F-403.md).
    OWNED otherwise: the two test_measurement.py files. The CM sets
    the R5 streak head at the first head with the verify.py change
    plus the test changes, after its CI.
     Architect ruling, frozen arch-gate-summary-keys-a627ca97.txt in
     /tmp/cm-relay/F-262/frozen/ (sha256 a627ca97, verified at PM
     read): API shape ACCEPTED (additive keys; neither consumer has a
     pydantic response_model; filter-gen.js reads only named keys). C1
     (blocking), verbatim: "don't index details with [] -- use a
     guarded read." verify_closed_loop's two early FAIL returns have
     no details, so [] raises KeyError and turns a reported FAIL into
     a crash (HTTP 500 from /generate). Test in the same commit: an
     early-FAIL channel gives closed_loop_pass false, both keys null,
     all_pass false, no exception. No log_* values in the payload
     (they can be NaN, and Starlette's JSONResponse refuses NaN).
     AE answers, frozen ae-R4-R5-answers-f277e402.txt in
     /tmp/cm-relay/F-262/frozen/ (sha256 f277e402, verified at PM
     read): (1) R5 keys YES with C1 (details.get -> None; None is a
     run FAIL, never a skip), C2 (the R5 assert uses the UNROUNDED
     value, or closed_loop_pass AND the value; the payload may stay
     rounded), C3 (all 10 runs <= 3.0 dB AND worst <= 2.5 dB;
     per-channel min/max/spread at the end, for the QE). (2) R4
     reading, verbatim: "the PM is right." The owner line means the
     residual investigation (the R4 data), not the defect file;
     worker-4 writing F-403.md "does not conflict with R4".
  - F-403.md writer (PM and CM allocation, 2026-10-26; supersedes "TW
    answer pending" above): the TW, as the single writer. Per
    team-lead (2026-10-26): the QE released ("TW: release"), and the
    AE says their R4 does not require worker-4 and is fine with the TW
    (AE f277e402: worker-4 "does not conflict with R4"). Correction
    (team-lead, 2026-10-26): this was not a team-lead ruling; fence r3
    (CM file) says "team-lead ruling", which team-lead corrects. TW
    batch v1 on e7afdb36: /tmp/tw-f403-e7afdb36.patch (sha1 371f0f13,
    verified at PM read). Pending for v2 (CM): the severity (AE), the
    R4 data (worker-4), the AE's R4 branch, and the xfail reason at
    the merging head. worker-4's fe80d4fa (F-403.md under fence r1) is
    NOT pushed and is dropped from the branch; its content is frozen
    as TW input, w4-F403-draft-input-fe80d4fa.md in
    /tmp/cm-relay/F-262/frozen/ (sha256 f39151a0, verified at PM
    read).
  - QE R5 ledger rules r2, frozen qe-R5-ledger-rules-r2-ebd890d0.md in
    /tmp/cm-relay/F-262/frozen/ (sha256 ebd890d0, verified at PM read;
    adds to abfd33d7, changes nothing there). A: the dispatch checks
    out the branch head; A1, the CM checks once before the first
    dispatch that origin/main is an ancestor of the streak head (git
    merge-base --is-ancestor); carry-over after an update-branch only
    if the diff from main touches none of src/, tests/, conftest*,
    pytest/pyproject config, nix/, flake.*, configs/, scripts/,
    .github/, else a new series of 10; the Rule 13 PR CI at the final
    head is still required. B, per-run classes: PASS (API test PASSED
    with every AC line; counts), RED (FAILED/ERROR, any max > 3.0 dB,
    or an E2E crash after the stack started; ends the series, R2
    applies), VOID (the API test never ran; logged, neither counts nor
    breaks the streak). T1 failures: each is its own PM one-liner
    (test name, run id); the same T1 test failing in 2 dispatches at
    one head stops the series; more than 3 VOID runs in a series means
    stop and send the ledger to the QE. Other E2E failures in a PASS
    run are separate PM findings. Dispatch one at a time; a run
    cancelled by a later dispatch is VOID.
  - Backlog line (AE, 2026-10-26, from R6 of f8a014c7: no F-262 test
    change; no P-level given), verbatim: "Q4 lag/noise table: state
    that its rows cover align_capture only, and that the pipeline's 30
    dB SNR gate (27fc548d) rejects a -40 dBFS room capture. Add a
    pipeline-level test that a -40 dBFS capture is rejected (SNR) if
    none exists." Supersedes the "not yet known which" in the R6 line
    above.
  - UPDATE (CM, 2026-10-26): fence r4 /tmp/cm-relay/F-262-fence-r4.txt
    (sha256 865f5117, verified at PM read; supersedes r3 48133641).
    Wording and record only; the OWNED and FENCED file sets are
    unchanged. It records the TW as the F-403.md writer (release
    record (f) 7f3a057b) and corrects r3's "team-lead ruling"
    attribution; the AE's B1 fixture fix and B2 (F-411) are NOT in the
    fence; the browser xfail stays.
  - UPDATE (CM, 2026-10-26): F-262 head eb178a19, R5 logging under
    fence r3/r4 (fe80d4fa dropped, the branch went back to 65af5ee2).
    Review diff
    /tmp/cm-relay/F-262/review-eb178a19/65af5ee2..eb178a19.diff
    (sha256 6c7fe986, verified at PM read). Architect, verbatim:
    "release 6c7fe986"; the stricter line is optional, written as "set
    of corrected channels == requested channels". AE, verbatim:
    "release with the stricter line". So (CM) worker-4 adds the
    stricter line in the Architect's form as a new head, and both
    release again; that head becomes the R5 streak candidate.
    worker-4's C1 scope point (corrected entries only) went with the
    6c7fe986 release. PM cross-ref: origin/fix/F-262-shared-correction
    is still e7afdb36 at PM read; CI 40392568920 still running (CM),
    65af5ee2 goes up after it.
     Release record (g) (CM, 2026-10-26; supersedes the PM paraphrase
     of the two releases above):
     /tmp/cm-relay/release-record-20261026-g-6c7fe986.txt (sha256
     ba281200, verified at PM read). Architect, verbatim: "release
     6c7fe986 (eb178a19, parent 65af5ee2). C1 is implemented as ruled:
     guarded .get gives None, no log_* values are in the payload, and
     the early-FAIL test asserts details == {}, both keys None and
     all_pass False. The service test asserts the unrounded pass flag
     together with the rounded value, which is consistent. No points."
     On the C1 scope, verbatim: "If worker-4 wants it, write it as
     "the set of corrected channels equals the channels the test
     requested", not as a hard-coded "Left". That would be a new head
     and needs a new release from me. Otherwise release 6c7fe986
     stands as is." AE, verbatim: "release with the stricter line. The
     corrected-entries scope is right, but the one line also
     guarantees that the measured channel (Left) is the one checked."
     Net (CM), verbatim: "eb178a19 is NOT the streak head. A new head
     with the set-equality line needs AE + Architect releases."
  - UPDATE (CM, AE, Architect, 2026-10-26): cd1f63e7 (the set-equality
    line) RELEASED. Record (h)
    /tmp/cm-relay/release-record-20261026-h-cd1f63e7.txt (sha256
    eb035598, verified at PM read): diff eb178a19..cd1f63e7 sha256
    1fdfafae, full c8 diff 65af5ee2..cd1f63e7 sha256 ec079943. AE,
    verbatim: "F-262, AE: release 1fdfafae (cd1f63e7). The set form
    meets my point and is stronger than the one-liner: it catches
    mislabelled, extra and missing entries." Architect, verbatim:
    "release 1fdfafae (cd1f63e7 increment; full c8 diff ec079943 also
    released)." TW F-403 v2 (86ab5ba2, supersedes v1 371f0f13) applied
    on top as docs-only commit 4724e65d (CM). origin
    fix/F-262-shared-correction = 4724e65d (PM read: 4724e65d, parent
    cd1f63e7, then eb178a19; origin/main is an ancestor, A1 OK). PR CI
    run 40395927172 (CM); the R5 series starts after it.
     UPDATE (CM, QE, 2026-10-26): QE, per CM: no R5 rule change at
     4724e65d; the series goes once CI 40395927172 is green. The TW's
     F-411 swap and the QE's AC 6 citation point (ebd890d0) are held
     as a post-series TW v3, so the streak head does not move.
  UPDATE (CM, 2026-10-26, after v292): PR CI 40395927172 at 4724e65d
  is SUCCESS. R5 series STARTED: A1 OK (origin/main 498fa3e5 is an
  ancestor of the streak head 4724e65d; PM read: merge-base check
  confirms). R5 run 1 = 40403348924 (workflow_dispatch run_e2e=true,
  ref fix/F-262-shared-correction, headSha 4724e65d, dispatched
  2026-10-26T21:19:15Z; conclusion pending at this version). Rules: QE
  abfd33d7 + ebd890d0; one run at a time. Ledger:
  /tmp/cm-relay/F-262/R5/ledger.txt (CM-owned, live).
- **F-403** Capture redesign (P1, room lane, directly after F-262; PO
  ruling 2026-10-26; ID allocated by the PM, checked free across main,
  all branches and worktrees). PO, verbatim: "capture redesign
  (signal-gen sweep export, one continuous play+record stream, noise
  pre-capture)"; it also takes the QE's wall-clock cause (the 1 s
  pw_capture wait, pw_capture.py:197). QE Q2 scope: the S2/S3 stream
  redesign and the S4 noise gate. Must be filed before F-262 merges
  (QE).
  Gate (PO, verbatim): "the new defect does NOT block US-178. Reason:
  with F-262's fail-closed check, a bad capture produces an error,
  never wrong filters; the redesign improves reliability, not
  correctness. It DOES block US-174e (one-button venue workflow),
  because one button needs reliable captures." Exception (PO): "if the
  AE or Architect rules that the current capture can pass the
  fail-closed check and still deliver wrong filters, the new defect
  becomes a US-178 gate. AE/Architect call, no PO round needed."
  Scope (joint AE + Architect, verbatim in joint-Q2-Q5-final-v2.txt):
  S2 signal-gen plays and exports the session array, deconvolution
  runs against the played array; S3 one continuous play+record stream,
  cross-correlation alignment, no wall clock; S4 a 0.5 s pre-capture
  and a 30 dB per 1/3-octave SNR gate.
  Gate (Architect, 2026-10-26, verbatim via CM): "PM: a new P1 defect
  for the S2/S3/S4 capture redesign, directly after F-262. It doesn't
  block the F-262 merge, but it blocks deploying any room-correction
  filter with the amps on. The PM puts that in the backlog line."
  Rationale (joint v2, verbatim): "Until then, cut-only correction +
  max_cut + the S5 trim + the S6 gate + the fail-closed window mean a
  bad capture gives a refused or quieter filter, never a boost."
  US-178 gate (AE + Architect, 2026-10-26; the PO exception above
  applies), verbatim: "The capture-redesign defect gates US-178's
  amps-on activation and acceptance step. US-178 development and
  amps-off testing may start without it. The gate lifts early if S4
  (silent pre-capture + fail-closed SNR check) lands before US-178 AND
  the F-262 diagnostic shows a median correlation-peak width ≤ 2
  samples. S2 and the continuous stream then become reliability-only
  and gate US-174e instead." Reason (via CM): without an SNR gate a
  noisy capture can pass the onset check and the correction then cuts
  noise; S6 cannot catch it because it uses the same measured IR; the
  result is a wrong filter, not a dangerous one, because correction is
  cut-only. Architect: nothing more needed from the PO; the PO's "no
  US-178 gate" is narrowed to "no gate on US-178 development or
  amps-off testing".
  Order (PO, 2026-10-26, verbatim): "pull S4 forward. Order inside the
  defect: S4 (silent pre-capture + fail-closed SNR check) as its own
  first slice/PR, directly after F-262 and before the rest (S2,
  continuous stream). Reason: S4 is the correctness part and, together
  with the correlation-peak criterion, can lift the US-178 amps-on
  gate early. The rest follows as reliability work before US-174e. If
  the Architect sees a technical dependency that forbids S4 first, the
  Architect's order applies, no PO round."
  S4 brief condition (Architect, 2026-10-26, via CM; the Architect
  sees no dependency against S4 first), verbatim: "take the noise
  window from the recording BEFORE the detected onset, i.e. F-262's
  cross-correlation onset minus a 10 ms guard. Do not take a fixed
  first 0.5 s. If the window ends up shorter than the AE's minimum,
  the SNR check FAILs closed. The AE sets the minimum window length
  and the per-band 30 dB threshold."
  S2 finding (CM, 2026-10-26): signal-gen can't export the buffer it
  played. It does have a file-playback RPC.
  Record (QE, 2026-10-26): preferred route is worker-4 writing
  docs/project/defects/F-403.md inside the F-262 PR, so the
  xfail/branch-B citation and the record land in the same merge (TW
  reviews under Rule 13); the TW queue is acceptable if merged before
  or with F-262. Minimum content: the PO scope (sweep export, one
  continuous play+record stream, noise pre-capture, the wall-clock / 1
  s pw_capture wait cause); evidence (the F-262 diagnosis files, the
  test_full_session_api XPASS history); ACs including removal of any
  F-262 branch B or xfail citing F-403. The QE Q2 condition is met
  once the record exists. Route: CM call, pending.
  DECIDED (CM call, 2026-10-26; resolves "Route: CM call, pending"
  above): docs/project/defects/F-403.md goes inside the F-262 PR,
  written by worker-4 with the QE's minimum content; the TW reviews it
  under Rule 13. The CM briefs worker-4 at their next event (worker-4
  is building the scratch branch).
  WRITER CHANGED (AE R4 f8a014c7 and QE Q2 abfd33d7, 2026-10-26; CM
  accepted, fence r2 084ad898; supersedes "written by worker-4" in the
  DECIDED line above): F-403.md is written by the PM-allocated writer,
  not worker-4; the PM proposes the TW, TW answer pending (see F-262,
  c8). Location unchanged: inside the F-262 PR. QE minimum content
  (abfd33d7 Q2, PM summary): header (ID, title, AE severity, status,
  writer, owner, links to F-262/#66 and to f8a014c7 R3/R4/R5); the
  symptom with the measured numbers (browser Sub1 +4.73 dB (2 s) /
  +3.60 dB (5 s) vs 3.0 dB; S2 margins Sub1 0.01-0.03 dB and mock-room
  Left 0.03 dB; offline home_lab Sub1 +0.91 dB); the cause labelled
  VERIFIED or HYPOTHESIS; the R4 data table and which R4 branch the AE
  ruled; the fixed constraints (3.0 and 18.0 dB, R1); the affected
  test and its xfail reason at the merged head; the removal AC (R5 on
  the browser test); a deterministic test that fails today and proves
  the IR reference is the played sweep; reproduction; a matching
  defects-index row.
  WRITER (PM and CM allocation, 2026-10-26; QE released, AE fine with
  the TW; supersedes "TW answer pending" above): the TW, single
  writer. TW batch v1 /tmp/tw-f403-e7afdb36.patch (sha1 371f0f13) on
  e7afdb36; v2 follows with the AE severity, the R4 data, the AE's R4
  branch and the xfail reason at the merging head (see F-262, c8). The
  AE (f277e402): the R4 owner line means the residual investigation,
  not the defect file.
  WRITER SETTLED (CM release record (f), 2026-10-26; supersedes "AE
  fine with the TW" above): the TW, single writer, allocated by CM +
  PM; worker-4 supplies input data only.
  /tmp/cm-relay/release-record-20261026-f-F403-writer.txt (sha256
  7f3a057b, verified at PM read). QE, verbatim: "F-403 writer: TW:
  release." AE, verbatim: "(1) TW: release. One writer settles it, and
  the TW batch already exists. worker-4 supplies only the input data."
  Not a team-lead ruling (team-lead); fence r3's "team-lead ruling"
  wording is fixed in fence r4.
  SEVERITY (AE, 2026-10-26, for the TW;
  /tmp/cm-relay/F-262/frozen/ae-F403-severity-b74d437e.txt, sha256
  b74d437e, verified at PM read), verbatim: "High (audio correctness,
  core room-correction path; fails closed, no speaker or ear hazard)".
  Reasons (PM summary): production code, session.py:829-834 builds the
  IR against the session's own sweep array, not the one signal-gen
  plays (a code fact; only the size of the effect is a hypothesis); it
  blocks the core priority; not Critical because the F-262 closed-loop
  gate refuses the filter and the correction is cut-only and
  D-009-trimmed. Re-rating, verbatim: "if S2 (played-sweep reference)
  shows the mismatch changes no result beyond 0.5 dB on real hardware,
  the AE drops it to Medium." The near-limit residual (R4 data) is
  separate (see R4 BRANCH below).
  R4 DATA (worker-4 via CM, 2026-10-26; offline model only, system
  python3 + numpy at 65af5ee2, no PipeWire, CI or Pi;
  /tmp/cm-relay/F-262/frozen/w4-F403-R4-data-41c33bbb.txt, sha256
  41c33bbb, verified at PM read; S2 played-sweep reference): Sub1 (2 s
  / 5 s, local-demo model) max deviation +2.99 / +2.97 dB at 42.4 Hz,
  uncorrected +20.98 / +20.96 dB there, FIR gain -18.03 dB capped /
  about -21.2 dB uncapped, 18 dB cap REACHED; mock-room Left +2.97 dB
  at 272.6 Hz, uncorrected +3.95 dB, FIR gain -0.71 dB, cap NOT
  reached (minimum FIR gain in 250-500 Hz -1.52 dB). Onset equals
  played_onset in every case.
  R4 BRANCH (AE ruling, 2026-10-26, single writer;
  /tmp/cm-relay/F-262/frozen/ae-F403-R4-branch-ruling-2218daf5.txt,
  sha256 2218daf5, verified at PM read). Alignment, verbatim: "no
  defect. Onset = played_onset in every case, and SNR is 48-65 dB." B1
  Sub1, verbatim: "CAP BRANCH, a test fixture issue." Fix in the
  local-demo room sim (scripts/generate-room-sim-ir.py), never in
  MAX_CUT_DB or MAX_POSITIVE_DEVIATION_DB; verbatim: "The deepest mode
  inside the gated band must be at most 15 dB over target, so the cap
  is not reached and a fully corrected mode leaves room for the R5 0.5
  dB margin." Not in the F-262 fence (fence r4); no owner or P-level
  given. B2 mock-room Left: "NO-CAP BRANCH, a correction defect
  suspected"; filed as F-411 (Medium). Effect on F-262 (AE): the
  browser xfail stays (f8a014c7 R3); verbatim: "Its removal later
  needs S2 + B1 fixture fix + B2 resolved, and then the R5 10-run AC."
  The API test (Left, session sweep, +1.92 dB) is not affected.
  Product note (AE, for the PM backlog, not F-262; no P-level given),
  verbatim: "a real room with a mode more than 21 dB over target fails
  the closed-loop gate, so the channel gets no filter. That is the
  fail-safe direction and correct for now. A future "partial
  correction" verdict is a design question, not a defect."
  TW BATCH v2 (CM, 2026-10-26; supersedes v1 371f0f13):
  /tmp/tw-f403-v2-e7afdb36.patch (sha1 86ab5ba2, verified at PM read),
  held until the new F-262 head (set-equality line) is released. The
  CM passes the B2 number F-411 to the TW.
  TW BATCH v5 (CM, 2026-10-26; supersedes v2 and the "post-series TW
  v3" in F-262; v4 e8a9341f VOID): /tmp/tw-f403-v5-4724e65d.patch
  (sha1 5abeed4f), MANIFEST e50df0c8, commit message 2842db02 (all
  verified at PM read). The CM applies v5 only after the R5 series.
  S4 condition AMENDED (Architect, 2026-10-26; supersedes the S4 brief
  condition above; verbatim in
  /tmp/cm-relay/F-262/findings-rulings-arch-ae.txt, sha1 6b9584ae):
  "The noise window must lie inside [end of the pink warm-up + decay
  guard, detected onset − 10 ms]. As the schedule is today, that
  interval may be empty. S4 therefore also fixes the schedule: a real
  silent gap between the warm-up and the sweep, with a length the AE
  sets. An empty or too-short window FAILs closed."
  S4 parameters (AE, 2026-10-26, verbatim in the same file; amends the
  AE's earlier 0.5 s):
  - "The noise window is ≥ 1.0 s, taken before the detected onset
    minus the Architect's 10 ms guard; shorter fails closed. This
    amends my earlier 0.5 s, because a 0.5 s window gives too few
    averages in the 20 Hz 1/3-octave band (about 4.6 Hz wide) for a
    stable reading."
  - "Per band: 1/3-octave bands from 20 Hz to 20 kHz, each channel's
    sweep band level vs the noise band level, ≥ 30 dB in every band in
    that channel's passband (the subs up to their crossover + 1
    octave), or the capture FAILs. There is no automatic level
    increase."
  S2 route (Architect: design note, not a ruling yet; AE endorsed):
  the file-playback RPC, so signal-gen plays exactly the array the
  session deconvolves against. AE conditions for the brief, verbatim:
  "the session writes the exact array it deconvolves against;
  signal-gen's output level cap still applies to file playback;
  playback is refused if the file's peak exceeds the session's
  sweep_level_dbfs, or if the file isn't mono 48 k float." SecSpec
  also has a say on the path (AE).
  Pink-burst overlap (AE, 2026-10-26, verbatim): "A pink burst still
  running when the sweep starts adds noise exactly where the sweep is
  at 20-40 Hz, which corrupts the sub-bass correction." If the
  diagnostic's pre-roll RMS shows the burst still on, it is a named
  F-403 finding and a US-178 gate together with S4. Fix (AE): "the
  burst ends, then ≥ 0.5 s settle, then the noise window, then the
  sweep."
  S2 AC (AE, F-262 F2 ruling a8386f4b, 2026-10-26), verbatim: "When S2
  lands (session ref = played law), the 30 dB floor is reinstated on
  the session-ref h as well. The PM records this as an S2 AC."
- scripts/test-e2e.sh: worker-4 (outside F-262, via CM, 2026-10-26),
  verbatim: "scripts/test-e2e.sh runs under `set -e`. If the
  service-integration pytest fails, the script exits before the
  browser E2E runs, so the E2E_EXIT reporting below it is dead code."
  No priority given; no ID allocated. PM cross-ref: same script as the
  #64 -rs change (test-e2e.sh:133/139, see F-362).
  CM, 2026-10-26: no F-ID unless the QE asks for one.
- **F-404** A measurement session leaves the D-063 gate in whatever
  state it found it, and after an error or abort it re-links
  production with the gate open (AE, 2026-10-26, via CM; ID allocated
  by the PM, checked free across main, all origin/* and local
  branches, and worktrees; no P-level given). AE, verbatim: "New
  defect (next free ID): a measurement session ends with the gate in
  whatever state it found, and after error or abort it re-links
  production with the gate open."
  Fix (AE): every terminal state (complete, error, abort) closes the
  gate via GM close_gate BEFORE _restore_production_mode. If
  close_gate fails, the session reports "gate state unknown: amps off"
  and does not restore production links.
  Test (AE): an injected error in each phase ends with the gate
  closed, then production restored, in that order.
  Gate (AE): blocks US-178 and any amps-on measurement. It does NOT
  block the F-262 merge; F-262's new fail-closed exits get the fix
  with the rest.
  Interim rule (AE): no measurement session with amps on. The
  diagnostic driver closes the gate between runs.
  PM cross-ref: docs/architecture/measurement-daemon.md (origin/main)
  lists restore_production_mode() at the CP-2..CP-7 abort points; no
  existing backlog entry found for the gate state at session end.
- test_mic_sim_with_cal_file never runs (QE, 2026-10-26, low; no ID
  requested):
  src/room-correction/tests/test_sim_config_generator.py:76-80 skips
  whenever /home/ela/7161942.txt is missing. That path was on the
  unreachable Pi 4 (US-174:62), so the test now runs nowhere (also the
  one room-correction skip on CI 40317165021, not F-394; QE via CM).
  Fix (QE): commit a calibration fixture, or point the test at the
  re-fetched file. PM cross-ref: the same skip is named in the #54 H1
  record (run 40241169781).
  Files available on the Mac (team-lead, 2026-10-26, found in the
  owner's Downloads at the owner's request; both dated 20 June):
  ~/Downloads/7161942.txt, header "Sens Factor =-1.378dB, SERNO:
  7161942" (matches the CLAUDE.md sensitivity), sha256
  b1aeddb6ad0ef149d32c0f55ead271cff4456d4339ad743a080df40f3d2c02a8;
  ~/Downloads/7161942_90deg.txt, sha256
  192af895d55983ab335ff81680c2aa093f477adf231df993f53bddba442d1926.
  Who commits it as a fixture or deploys it to the Pi: the CM, QE and
  AE decide (team-lead).
- Start after a session error (worker-4, 2026-10-26, via CM; optional,
  no priority given, no ID), verbatim: "Start right after a session
  error returns 409 until the GM restore finishes; the UI should
  disable Start until mode=standby." PM cross-ref: the same
  error-to-restore window as F-404.
- **F-405** test_gate_closed_e2e.py:137 reports a gate-open result as
  SKIPPED instead of FAILED (QE, 2026-10-26, #64 skip rulings
  dea15e43; ID allocated by the PM, checked free across main, all
  origin/* and local branches, and worktrees; no P-level given: the QE
  says the PM and the AE set it, and the PM has asked the AE). A bare
  `except Exception` wraps the D-063 gate-closed assert, so
  "gate_open=True" at load shows up as SKIPPED. Test-only fix: narrow
  the except to request and JSON errors and move the assert out of the
  try. It must be fixed before this test counts as gate-closed
  evidence (QE). Does not block #64.
  P-level (AE, 2026-10-26; supersedes "no P-level given" above): P2.
  AE reason: a broad except that turns a gate_open=True failure into a
  SKIP is a false negative on the D-063 gate-closed evidence, so it is
  real; it does not block #64, and nothing is connected now.
  Condition: fix it before any amps-on session, and before any PR or
  report cites test_gate_closed_e2e as gate-closed evidence; until
  then, nobody cites it. PM cross-ref: not added to the amps-on list
  (that needs a matching safety.md update by the TW).
  Amps-on row (CM, 2026-10-26): no, not now; the "PM cross-ref: not
  added" label stands. A row needs a matching TW safety.md batch,
  which is pre-prod safety-doc work the owner has paused (core tech
  first). The P2 entry already carries the AE's "before any amps-on
  session" condition. Promotion to a row is the AE's domain call,
  raised by the AE.
- **F-406** test_filter_deploy_e2e.py:315 skips with "No v1 timestamp
  found in versions listing" (QE, 2026-10-26, #64 body a2bfb9af: NOT
  accepted; ID allocated by the PM; no P-level given). QE, verbatim:
  "v1 was just generated and deployed, so a missing active v1 in
  `/api/v1/filters/versions` is a product, contract or test-key
  defect, and it leaves rollback untested." Same kind as F-402.
- **F-407** test_venue_gate_e2e.py:180 ("Gate indicator did not update
  to OPEN") and :165 (`except Exception: skip(...)`) skip instead of
  failing (QE, 2026-10-26, #64 body a2bfb9af: NOT accepted; ID
  allocated by the PM; no P-level given). QE, verbatim: "The browser
  reflecting gate changes is what the test checks, so a timeout should
  be a FAIL, or an xfail with an F-ID." UX (3a8e85ff) supports it: the
  gate indicator is the operator's main safety cue.
  P-LEVEL (AE, 2026-10-26, after v263; supersedes "no P-level given"
  above), verbatim: "yes, set F-407 to P2 (AE), the same level as
  F-405: fix it before amps-on." F-407: P2 (AE). The AE also confirmed
  A3 as recorded (B1 maps to F-394; no new F-number).
  UPDATE (CM, 2026-10-26, after v260): F-406 and F-407 records are PR
  #67 (docs-only, draft, head ae450041); 7 Rule 13 verdicts requested;
  CI-exempt.
  UPDATE (CM, 2026-10-26, after v261): #67 6/7 APPROVE at ae450041,
  all matched on GitHub (CM): UX, ARCH, TW, SEC, AD, QE; none
  blocking; QE CONFIRMED the ACs as written; AE pending. Frozen
  verdicts /tmp/cm-relay/PR67/frozen-verdicts-ae450041/, each sha256
  verified at PM read: UX 1599efa3, ARCH b4a3b032, TW 627afa08, SEC
  a113860a, AD fb1c0a6c, QE 74723586. TW declares authorship of both
  records (QE cross-checks the facts). None of the approvals rates
  severity (UX, SEC, AD, TW).
  Non-blocking points from the #67 verdicts, verbatim (no F-ID, no
  P-level given except where quoted):
  - F-407 close POST swallowed (one row; ARCH N1, SEC (1), AD L1, QE
    N1). ARCH N1: "F-407 does not mention that the gate-CLOSE API call
    in the same test is wrapped in `except Exception: pass` (between
    :180 and the CLOSED wait). A failed close is swallowed silently,
    and the local-demo gate may then stay open for later tests in the
    session. Suggest extending AC2 to the close call: it fails on an
    API error. Test-only, no production impact." SEC (1), rated "LOW"
    (SEC): "The gate is the D-063 output interlock, so a failing close
    must be a FAIL. Suggest AC2 covers both the open (:165) and the
    close API step." QE N1: "AC1 already covers it, because the CLOSED
    wait then times out and becomes a FAIL. The fix PR should still
    make the close POST fail on an error, in the same way as AC2. No
    record change is needed now."
  - AD L2 (F-407, state leak): "if the test skips (or, after AC1,
    fails) after the gate opened, nothing closes it. There is no
    teardown, and the close error is swallowed. Later E2E modules on
    the same local-demo stack then run with the gate OPEN, so a
    gate-starts-closed (D-063) check that runs later would test leaked
    state. It is local-demo only and has no prod path. Suggested AC: a
    finalizer or fixture that closes the gate and asserts CLOSED."
  - UX N1 (F-407), AC addition for the QE to consider: "the dangerous
    direction is the indicator showing CLOSED while the gate is OPEN
    (stale state after a lost WebSocket event or connection). Besides
    the OPEN/CLOSED timeouts, the fix should make a lost or stale gate
    state visible, e.g. the indicator switches to "UNKNOWN /
    reconnecting" when the WebSocket drops, and never keeps showing
    the last state as current."
  - UX N2 (F-407), severity input: "approving this record does not
    rate it ... I would rate F-407 at least as high as F-406." PM:
    recorded as input; F-406 and F-407 still have no P-level.
  - AD M1 (F-406 AC3, vacuous pass): "If `/filters/active` returns
    `{}`, the loop runs zero times and the test PASSES with no
    rollback evidence. ... Suggested AC amendment: the active set
    after v1, after v2 and after rollback must be non-empty and cover
    every deployed channel. QE to confirm." PM cross-ref: QE CONFIRMED
    the ACs as written (CM); whether M1 is taken up is the QE's call.
  - QE N2 (F-406): "That assert compares `/api/v1/filters/active`
    (l.276/307), not the versions listing. In CI, `/filters/active`
    changed between v1 and v2 while `/filters/versions` showed no
    `active` entry. That points AC1 at a contract mismatch between the
    two endpoints. This is a hint for the fix author; no record change
    is needed."
  - SEC (2), "INFO" (F-406 vs US-174d): "Resolving F-406 must not
    re-enable the rollback writer just to make the test pass.
    Acceptable outcomes: assert the 409 while the writer is disabled,
    or move the rollback evidence to the venue pipeline. The QE and
    Architect pick which one."
  - AD nits: F-407 line cites (open-step skip is :166, CLOSED skip
    :199); Related lines cite F-402 and F-405, which have no record
    file (= QE N3, see the TW docs batch). AD: the F-400 append
    conflict with #63 is trivial; diff-only re-review if the head
    moves.
  UPDATE (CM, AE, 2026-10-26, after v262): PR #67 MERGED as 498fa3e5
  at 15:11:04Z (origin/main head at PM read), 7/7 APPROVE. AE APPROVE
  /tmp/cm-relay/PR67/frozen-verdicts-ae450041/AE-27290d21.md (sha256
  27290d21, verified at PM read). F-406/F-407 records are on main. #63
  has an expected defects-index.md conflict to resolve when it resumes
  after US-172 (CM).
  - AE A1 (F-407 severity input), verbatim: "the gate indicator is how
    the engineer sees whether audio can pass." "The dangerous
    direction is the indicator showing CLOSED while the gate is OPEN."
    "From the audio-safety side, F-407 should rank with F-405: fix it
    before amps-on." "AC3's root cause should state which direction(s)
    fail." PM cross-ref: F-405 is "P2 (AE)" (v243 status line). The PM
    does not set F-407 to P2 by inference; asked the AE to confirm.
    F-407: no P-level given.
  - AE A2 (F-406), verbatim: "Suggested AC4: after the rollback, the
    active set passes the same D-009/format checks as a fresh deploy,
    and the convolver reload is confirmed. A rollback is a deploy, so
    the same safety gate applies." PM cross-ref: SEC (2) above (the
    rollback writer is disabled by US-174d); the QE and Architect pick
    the F-406 outcome.
  - AE A3, verbatim: "My #64 point B1 ... is the same skip-masking
    class. If the PM gives it an F-number, it belongs with
    F-405/F-407." PM: B1 is already mapped to F-394 (v260; CM: F-394
    covers the 7 DJ-switch skips); no new ID. AE told.
- **F-408** Min-phase residual metric not valid for unit-circle zeros
  (AE gate-xo ruling v1
  /tmp/cm-relay/F-262/frozen/ae-gate-xo-ruling-v1-0aac380f.txt,
  sha256 0aac380f, verified at PM read; AE released, Architect NOT yet
  released; ID allocated by the PM at the AE's request; no P-level
  given). G4, verbatim: "Follow-up, not blocking F-262. PM gets a new
  F-number; AE owns it with the Architect, and it lands before the
  first amps-on room correction." Goal (AE): replace the cepstral
  residual with a metric valid for unit-circle zeros, so that
  pre-ringing introduced by correction is detected at fine level
  again. Candidates (AE): passband excess group delay vs the
  generator's design; the residual of the CORRECTION component before
  it is combined with the crossover; an exponentially weighted
  cepstrum.
  Architect A2 (non-blocking, for G4;
  /tmp/cm-relay/F-262/frozen/arch-gate-xo-v1-points-96e9b156.txt,
  sha256 96e9b156, verified at PM read): the near-constant -5.1 dB and
  the 36-sample reference shift "looks more like a systematic
  alignment or normalisation effect in minimum_phase_residual_db than
  like slow cepstral convergence." Architect, verbatim: "Before
  choosing a new metric in G4, check whether aligning the reference
  (peak or cross-correlation lag) before the residual already restores
  fine resolution. If it does, G4 may be a small fix."
  UPDATE (CM, 2026-10-26, after v263; supersedes "Architect NOT yet
  released" above): the source ruling is now v2
  /tmp/cm-relay/F-262/frozen/ae-gate-xo-ruling-v2-91eca61e.txt (sha256
  91eca61e), RELEASED by the AE and the Architect (record (h),
  eb2b06d3). G4 text unchanged from v1. Architect, verbatim: "F-408
  going into the backlog record instead of a v3 is fine." Owner AE
  with the Architect; lands before the first amps-on room correction
  (G4). F-408: no P-level given.
  - A2 data in v2 G4 (AE; float64, oversample 16, floor -240 dB; best
    lag and gain over +/-200 samples before the residual): BW8 LP80
    -20.4 -> -52.5 dB (lag 15); BW8 HP20 -26.6 -> -26.6 (lag 0); P1
    -5.1 -> -5.6 (lag 13). AE, verbatim: "So alignment fixes the LP
    case but not the HPF (DC-zero) cases. It is part of the fix, not
    the whole fix. G1 stays as is."
  UPDATE (CM, AE, 2026-10-26, after v264): AE addendum
  /tmp/cm-relay/F-262/frozen/ae-gate-xo-v2-addendum-F408-165ae71a.txt
  (sha256 165ae71a, verified at PM read) names F-408 as the G4
  follow-up; it does not edit v2 91eca61e. AE, verbatim: "The
  Architect may object to this addendum in a separate file." PM
  cross-ref: the addendum's "the Architect's pending release of v2"
  predates release record (h) (eb2b06d3), where the Architect released
  91eca61e, verbatim: "F-408 going into the backlog record instead of
  a v3 is fine." No Architect objection file seen at PM read.
- **F-409** Min-phase residual not shown in the UI (worker-4; F-262
  follow-up; no P-level given; no owner given)
  AE ruling 91eca61e G1 (l.38), verbatim: "The residual value is still
  logged per channel and shown in the UI details." At #66 head
  7011419d the payload carries "min_phase_residual_db" (verify.py:848,
  gate_summary; passed on in filter_routes.py:299 and
  session.py:1204). src/web-ui/static/js/filter-gen.js and
  rc-wizard.js do not display it (PM checked: no "residual" in either
  at 7011419d). Both files are outside the #66 fence.
- **F-410** Unmute restores the venue gains behind a closed gate
  (worker-1, outside F-394; severity: AE asked, pending; no P-level
  given)
  Source:
  /tmp/cm-relay/F-394/frozen/w1-e050fe90-finding-unmute-gate.txt
  (sha256 14c4d6dd, verified at PM read; transcribed verbatim by the
  CM). Worker-1, verbatim: "So mute → gate close → unmute puts the
  venue gains back on while the GM reports gate_open=false. That is a
  gain increase behind a closed gate." AudioMuteManager.unmute()
  (src/web-ui/app/audio_mute.py l.102-132) writes back _pre_mute_gains
  without a gate check (PM read at e050fe90, confirmed). Found by
  reading the code; nothing was run or played. Worker-1's test
  teardown avoids it by unmuting before closing the gate. Worker-1
  suggests a backlog one-liner under the owner's current priority,
  "unless the AE says otherwise".
  UPDATE (CM, AE, 2026-10-26, after v266; supersedes "severity: AE
  asked, pending; no P-level given" above): P2 (AE). Per CM: it blocks
  amps-on but not current work, the same tier as F-405. AE, verbatim
  (relayed by the CM without summary): "I read e050fe90
  main.rs:824-834. The GM's gate is the gains themselves; CloseGate
  sets every Mult to 0. So unmute() after a close turns the output
  fully back on at venue gain while the GM reports gate_open=false.
  Unlike OpenGate's 30-step ramp, it jumps the gain in a single step,
  and it also undoes automatic closes (Standby, main.rs:575-582)."
  AE fix direction, verbatim: "the GM stays the only writer of the
  Mults. unmute() must not raise any Mult while the gate is closed: it
  either refuses, or clears the mute and leaves the gains at 0, with a
  log line. Plus a T1 test of mute → close → unmute that checks the
  Mults stay at 0. Nothing is connected, so there's no action now."
  PM cross-ref: src/graph-manager/src/main.rs at e050fe90, l.824-834
  (CloseGate sets each Mult to 0.0) and l.575-582 (Standby closes the
  gate the same way), match the AE's reading.
- **F-411** Correction under-corrects near the closed-loop band edge
  (mock-room Left, 272.6 Hz: room +3.95 dB, FIR -0.71 dB) (AE,
  2026-10-26; title verbatim from the AE; severity Medium, AE; no
  P-level given; from F-403 R4 branch B2) Source:
  /tmp/cm-relay/F-262/frozen/ae-F403-R4-branch-ruling-2218daf5.txt
  (sha256 2218daf5, verified at PM read), on worker-4's R4 data
  41c33bbb (offline model, S2 reference). AE, verbatim: "The room is
  +3.95 dB over target at 272.6 Hz (1/6-oct, the gate's view), but the
  FIR cuts only 0.71 dB there. The cap is far away and alignment is
  clean, so the correction under-corrects a 4 dB peak and lands 0.03
  dB inside the gate limit." Severity, verbatim: "Medium (audio
  correctness; fails closed, no hazard)."
  Investigation (AE, verbatim): "The investigation compares the
  correction's own smoothing and windowing view with the closed-loop
  1/6-oct view at 250-300 Hz. If the two disagree by design, the AE
  rules which view is right before any code change." Fixed, verbatim:
  "the 3.0 dB limit, the 18 dB cap and the 1/6-oct gate smoothing are
  not changed to make this pass." Not in the F-262 fence (fence r4).
  No owner or worker assigned yet. Links: F-403, F-262 (its browser
  xfail removal needs F-411 resolved, see F-403).
  UPDATE (AE, 2026-10-26; supersedes "no P-level given" above): P2.
  AE, verbatim: "F-411 P-level, AE: P2. It is a correctness issue in
  core room correction, and the F-403 browser xfail can't be removed
  until it is resolved. The owner is for you and the QE to allocate.
  The investigation route is in ruling 2218daf5 (B2)."
  OWNER (PM + QE, 2026-10-26; supersedes "No owner or worker assigned
  yet" above): worker-7, also owning the F-403 B1 room-sim fixture
  fix. The PM first proposed worker-4 and the QE released worker-4
  (sequential after the R5 series); after team-lead's input (the
  owner's standing rule that nobody idles while a PR waits on CI;
  worker-7 idle, worker-4 blocked in the R5 series) the PM proposed
  worker-7 in two phases, and the QE released it, verbatim: "release
  worker-7, with your two-phase plan. My worker-4 release is
  withdrawn."
  Phases (PM proposal, QE released): phase 1 now, the B2 investigation
  from 2218daf5, read-only and offline on a scratch copy of 4724e65d,
  no commits to the #66 files; findings to the AE as a frozen file,
  and the AE rules which view is right before any code change. Phase
  2: the F-411 fix and the B1 fixture fix on a branch cut after the
  #66 merge, or earlier only under a CM fence revision. Reason (PM
  cross-ref, git diff origin/main...4724e65d): #66 already changes
  scripts/generate-room-sim-ir.py and room_correction/correction.py,
  alignment.py and verify.py.
  QE conditions, verbatim: "(a) The phase-1 scratch copy of 4724e65d
  must NOT be a git checkout in the shared repo dir, because worker-4
  and the CM work there. Use a separate directory: a CM-made clone or
  worktree, or git archive 4724e65d into /tmp. Never in-tree, and
  never isolation:"worktree". (b) Pin the phase-1 data to the 4724e65d
  fixture, and name that sha in the frozen file. (c) My earlier
  conditions 2 and 3 apply in phase 2: B1 and F-411 as separate
  commits with before/after numbers, and a deterministic test that
  does not depend on local-demo, fails today, and keeps the limits
  fixed."
  Earlier QE conditions 2 and 3 (from the worker-4 release), verbatim:
  "2. Keep B1 and F-411 as separate commits, each with its own
  before/after numbers. B1 changes the room-sim fixture, so the F-411
  analysis states which fixture sha it used. The mock-room Left
  numbers must be shown unaffected by B1, or re-taken after it. 3. The
  F-411 fix needs a deterministic test that does not depend on
  local-demo. It must fail today: a +3.95 dB 1/6-oct peak near 272.6
  Hz is cut by only 0.71 dB. The 3.0 dB limit, the 18 dB cap and the
  1/6-oct gate smoothing stay as they are (2218daf5 B2). If the AE
  rules the two smoothing views differ by design, the test follows
  that ruling." Condition 1 of that release (no B1 or F-411 commit on
  the F-262 branch: scripts/ and src/ are on the ebd890d0 A no-carry
  list, so such a commit voids the R5 series at 4724e65d) is covered
  by phase 2.
  BRIEFED (CM, 2026-10-26): worker-7 for phase 1. Frozen brief
  /tmp/cm-relay/F-411/w7-F411-phase1-brief-r1.txt (sha256 1e64f46b,
  verified at PM read). QE (a): scratch copy made by the CM with git
  archive at /tmp/w7-F411-scratch-4724e65d (PM read: exists, not a git
  checkout). QE (b): fixture scripts/generate-room-sim-ir.py blob
  f5ca9040 at 4724e65d (PM read: f5ca9040). Phase 2 waits for the #66
  merge or a fence revision.
  PHASE 1 FINDINGS r1 (worker-7 via CM, 2026-10-26):
  /tmp/cm-relay/F-411/frozen/w7-F411-phase1-findings-r1-bf381fe4.md
  (sha256 bf381fe4, 6999 bytes, verified at PM read), pin 4724e65d. PM
  summary: the two views differ by design. psychoacoustic_smooth
  designs at 1/3 oct over 250-750 Hz, while the gate uses 1/6 oct
  everywhere, so the whole sat gate band 250-500 Hz is in the
  correction's 1/3-oct region. Smoothing explains the gap; the
  fd-window and the FIR synthesis do not (realized FIR within 0.04 dB
  of design); not cap- or alignment-related. Counterfactual
  (attribution only, gate unchanged): 1/6-oct design smoothing takes
  mock-room Left from +2.97 to +1.39 dB (over_cut 0.85), local-demo
  Left +0.85 to +0.28, Sub1 unchanged (+2.99, cap/B1). Mock-room Left
  does not use the f5ca9040 fixture; its room is
  src/room-correction/mock/room_simulator.py + room_config.yml (+
  mock_audio.py). PM cross-ref at 4724e65d: blobs 8f8b74fc, 54113ea4,
  f57c4011 match; #66 changes none of them vs origin/main. Side note
  (worker-7): the psychoacoustic_smooth docstring says "1/3 octave
  200Hz-1kHz", the code uses 250-750 Hz plus crossfades (absorbed by
  AE P2 below).
  AE RULING (AE single writer, via CM, 2026-10-26):
  /tmp/cm-relay/F-411/frozen/ae-F411-phase1-ruling-5fe39778.txt
  (sha256 5fe39778, 2991 bytes, verified at PM read; relayed to
  worker-7). Verbatim: "A good diagnosis; I accept findings 1-5 as
  stated." "RULING: in the sat band, the gate's 1/6-oct view is right.
  The DESIGN smoothing changes; the gate does not." Phase 2 (after #66
  merges or under a fence revision; worker-7), verbatim:
  - "P1 psychoacoustic_smooth: 1/6 oct below 500 Hz; raised-cosine
    crossfade 1/6 -> 1/3 oct over 500-750 Hz; from 750 Hz upward
    unchanged (the existing crossfade to 1/2 oct). The old 150-250 Hz
    crossfade and the 1/3-oct 250-750 Hz region are removed. Below 150
    Hz nothing changes, so Sub1/B1 is unaffected."
  - "P2 Fix the docstring to describe the real bands (finding 5) in
    the same change."
  - "P3 Unchanged: MAX_POSITIVE_DEVIATION_DB 3.0, MAX_CUT_DB 18, gate
    smoothing 1/6 oct, over_cut limit 1.0 dB, the gate bands."
  Evidence for the AE release, before merge (verbatim):
  - "E1 mock-room Left, local-demo Left (2 s and 5 s) and Sub1: max
    deviation and over_cut, old vs new, as in the counterfactual
    table."
  - "E2 Every US-174 venue_sim scenario and every profile in the
    existing closed-loop tests: all gates pass, and the worst over_cut
    is reported with its margin to 1.0 dB. If any over_cut is more
    than 0.9 dB, stop and report before going further. The design must
    not trade one gate for the other."
  - "E3 Position robustness, the real risk of finer smoothing. Build
    the filter at mic position A and apply it to position B's measured
    IR, with the simulator's positions at least 0.5 m apart. In
    250-500 Hz (1/6 oct), corrected-at-B must not exceed
    uncorrected-at-B by more than 1.0 dB at any frequency, for old and
    new smoothing. If the simulator has no second position, say so;
    the AE then sets the substitute."
  - "E4 The F-262 R5 10-run AC is NOT re-run for this. F-411 gets its
    own PR, and the R5 rules apply there if it touches the
    service-integration test."
  AE, verbatim: "Severity stays Medium. The browser xfail removal
  still needs S2 + B1 + this."
  E3 PLAN RULING (AE single writer, via CM, 2026-10-26):
  /tmp/cm-relay/F-411/frozen/ae-F411-E3-plan-ruling-904f34c9.txt
  (sha256 904f34c9, 1692 bytes, verified at PM read; relayed to
  worker-7). Verbatim: "RULING: the plan is ACCEPTED as E3 for the
  merge gate, with the additions below. No simulator change is needed,
  and none is wanted in this PR."
  - "A1 Band: report two windows: 250-500 Hz and 500-750 Hz. The new
    crossfade also changes 500-750 Hz. The 1.0 dB limit applies to
    both windows."
  - "A2 Positions: the 4 offsets of ±0.5 m (x and y), height
    unchanged. Skip and list any B position within 0.3 m of a wall or
    a speaker. Also report ±1.0 m (x and y) as INFORMATION ONLY, not
    as a gate. It shows the trend as the move gets larger."
  - "A3 Output per scenario and position: max(corrected-at-B minus
    uncorrected-at-B) in each window at 1/6 oct, the frequency where
    it peaks, and old vs new smoothing side by side. Report it as
    numbers only; no plots needed."
  - "A4 Stop rule: if new smoothing exceeds the limit anywhere, or is
    more than 0.5 dB worse than old smoothing at the same point, stop
    and report before going further."
  Model limit (AE, verbatim): "So this E3 shows the change is not
  worse IN THE MODEL; it does not prove robustness in a real venue. No
  higher reflection order is required for this PR." Follow-up
  one-liner (AE, verbatim; does not gate the F-411 merge; no P-level
  given): "F-411 follow-up: a real two-position UMIK-1 check of the
  sat-band correction at the first real room-correction session (needs
  amps on, so the owner decides when)".
  QE CONDITION 2 r2 (QE, 2026-10-26; replaces condition 2 of the
  worker-7 release; (a), (b), 1 and 3 unchanged):
  /tmp/f411-qe-condition2-r2.md (sha256 d0052503, 1758 bytes, verified
  at PM read; CM frozen copy
  /tmp/cm-relay/F-411/frozen/qe-F411-condition2-r2-d0052503.md; PM
  frozen copy /tmp/pm-backlog/F-411-qe-condition2-r2-d0052503.md).
  Mock blobs per QE at 4724e65d: room_simulator.py 8f8b74fc,
  room_config.yml 54113ea4, mock_audio.py f57c4011. Verbatim:
  - "2a. B1 and the F-411 fix are separate commits, each with its own
    before/after numbers. (Unchanged.)"
  - "2b. The mock-room inputs are pinned. The F-411 analysis and the
    fix's test name the three mock blobs above as their room. "Left
    unaffected by B1" is now a mechanical check: the B1 commit must
    not touch any of the three mock files. The CM or QE checks this
    with git diff --stat on the B1 commit. If B1 touches one of them,
    the mock-room Left numbers are re-taken after B1."
  - "2c. The fixture is not the fix. The F-411 fix must not touch
    room_simulator.py, room_config.yml or mock_audio.py. Making the
    272.6 Hz mock peak smaller would hide the under-correction, not
    fix it; this is the same principle as 2218daf5 B2's fixed limits.
    A change to those files needs its own AE ruling and its own
    commit."
  - "2d. The local-demo contrast rows (f5ca9040) follow B1 as before.
    Their before/after numbers go with the B1 commit."
  Note on condition 3 (QE, not a change), verbatim: "if the AE rules
  that the 1/3-oct design view vs the 1/6-oct gate view (findings
  headline) is the cause, the fix's deterministic test asserts the
  AE's chosen behavior at 250-300 Hz on the pinned mock room, and it
  must fail at 4724e65d." PM cross-ref: the AE has so ruled
  (5fe39778), so the test asserts the 1/6-oct design view at 250-300
  Hz; the E3 ruling needs no simulator change, consistent with 2c.
  CM on E3 vs 2c (CM, 2026-10-26; closes the PM cross-ref above): no
  conflict. worker-7's AE-accepted E3 plan (904f34c9) gets the second
  position by passing mic_pos to simulate_measurement() as a call
  argument (instrumentation), with no edit to room_simulator.py,
  room_config.yml or mock_audio.py. The phase 2 brief will state both:
  no edits to the three mock files, and E3 by argument only. The CM
  froze QE r2 at
  /tmp/cm-relay/F-411/frozen/qe-F411-condition2-r2-d0052503.md and
  holds it for the phase 2 brief (not relayed while phase 2 is gated).
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
  Rediscovered (worker-4 via CM, 2026-10-26, briefly filed as F-401):
  fixed on US-174d by removing the test_filter_routes.py guard. QE
  condition: the revived tests must not be re-skipped; failures get
  fixed, or the test is deleted with a reason.
  QE sweep (2026-10-26): five web-ui unit test files use the
  module-level "skip the whole file on ImportError" guard. Only
  test_filter_routes.py is actually hidden today (CI's unexplained "1
  skipped" in the unit step); the other four run normally. Proposed
  fix, a small separate PR: replace the 4 remaining guards with plain
  imports, and add -rs to the nix pytest test apps so skip reasons
  show in CI. Optional (QE): a lint check against new unlisted
  module-level skips.
  QE (2026-10-26): F-362.md on origin/main has ACs 1-4 (the "ACs 1-5"
  above does not match it). New AC5, QE verbatim: "5. Every pytest
  invocation in the nix test apps reports skip reasons (`-rs`). In the
  CI log, every remaining skip is named with its reason, and the
  web-ui unit step shows no unnamed module-level skip."
  Status (QE, 2026-10-26): 174d removes the test_filter_routes guard
  and its stale `_PROFILES_DIR` import, so 174d covers AC1. AC2 is
  covered once its CI log shows a non-zero TestDeployPathTraversal /
  D-009 count. ACs 3-5 (the other 4 guards, the mutation check and
  -rs) belong to the small separate F-362 PR. The QE's 174d no-re-skip
  condition applies: failures are fixed or the test is deleted with a
  reason, never re-skipped or xfailed; the unit step shows 0 skipped,
  or every remaining skip is named. The four other guarded modules
  (test_speaker_routes, test_speaker_lifecycle_integration,
  test_activate_integration, test_protection_integration) run; CI's
  "937 passed, 1 skipped" is the whole filter_routes module.
  UPDATE (CM, 2026-10-26): the F-362 PR (QE (a) plain imports for the
  4 guards, (b) -rs) is assigned to worker-1 on
  defect/F-362-skip-guards, from origin/main 5f3af36a. (c), a check
  that fails on any module-level skip without an allowlist entry,
  stays an optional backlog-sized item.
  UPDATE (CM, 2026-10-26): F-362 is PR #64 (draft, worker-1),
  currently at the AC4 throwaway mutation head 03b2ec0f, whose CI run
  is expected to fail; the revert comes next. worker-1 adds AC5 to
  F-362.md in the PR.
  UPDATE (CM, 2026-10-26): final head 0d9e52e7 (revert 03c0237c plus
  F-362.md AC5 and status), held until mutation run 40314266261
  finished, then pushed; CI run 40314977506 (CM report, relayed by
  team-lead).
  QE (via CM, 2026-10-26): AC4 MET (the mutation run failed as
  intended).
  QE APPROVED (final, 2026-10-26) at 0d9e52e7: CI 40314977506 SUCCESS;
  counts 177/17/22/30 all PASSED; the only unit -rs skip is
  test_filter_routes.py:35, the named AC5 one. CI excerpt
  /tmp/pr64-ci-40314977506/; worker-1 and the QE compare it against
  the expected counts (CM).
  QE backlog one-liner (ID PENDING: PM asked the QE whether to reopen
  F-156 or allocate F-402): test_full_user_journey.py:181 skips 3
  browser tests on any 500 from POST /filters/generate with the reason
  "pre-existing numpy bool serialization bug in filter_routes", a skip
  hiding a real server error. PM grep: F-156 (defects/F-156.md on
  main) is exactly that symptom and is marked RESOLVED (task #159).
  Cross-ref F-362 AC5 (the filter_routes import skip) and F-262
  (session filter-gen).
  UPDATE (CM, 2026-10-26): #64 new head 15bd74eb (-rs on
  test-e2e.sh:133/139) pushed; CI run 40320048783 running. QE: e2e -rs
  accepted inside AC5; diff-only re-check at the new head, counts
  expected unchanged; the approval at 0d9e52e7 is superseded once the
  head moves. The QE's condition text names
  test_full_user_journey.py:181 as F-402 (see F-402).
  UPDATE (CM, 2026-10-26): CI 40320048783 GREEN at 15bd74eb. worker-1
  is merging main 29f5c61f. PM cross-ref: the merge moves the head, so
  the re-checks follow.
  UPDATE (CM, 2026-10-26): head f715538e (merges main 29f5c61f); CI
  40333713247 running.
  UPDATE (CM, 2026-10-26): CI 40333713247 still running
  (test-and-build).
  Backlog one-liner (team-lead, 2026-10-26; no F-ID, no priority
  given, the Architect or the QE may set it): the CM saw a warning in
  the log of CI run 40333713247: GitHub's `ubuntu-latest` image moved
  to Ubuntu 26 from 2026-10-19, which could cause new, unrelated CI
  failures. Question: should our workflows pin a specific runner image
  instead of `ubuntu-latest`? Blocks nothing now.
  QE skip rulings at f715538e (/tmp/pr64-qe-skip-rulings-f715538e.md,
  sha256 dea15e43, verified at PM read). None blocks #64.
  - One-liner (worker-1 proposal, QE): in CI, a failed GM DJ-mode
    switch in ensure_dj_mode is masked as a skip of 7
    service-integration tests; intermittent (the 7 tests flip between
    runs). Same kind as F-402. No F-ID, no P-level given.
  - One-liner (QE): test_filter_deploy_e2e.py:315 skips when the
    versions listing shows no active entry after a successful deploy,
    so rollback goes untested; it should assert. No F-ID, no P-level
    given.
  - F-405 (QE; see F-405): test_gate_closed_e2e.py:137.
  - One-liner (QE): test_venue_gate_e2e.py:165 and :180 skip on
    gate-open or indicator-update failure, which is exactly what the
    test checks; they should fail, or xfail with an F-ID. No F-ID, no
    P-level given.
  - UPDATE (PM, 2026-10-26, after v259): the #64 body's NOT-accepted
    skips (/tmp/pr64-review-f715538e/pr64-body-a2bfb9af.md, sha1
    a2bfb9af, verified at PM read) mapped to F-IDs. CM: the ID call is
    the PM's; no new ID where an existing row covers a skip.
    test_full_user_journey.py:181 -> F-402 (:331/:348/:369/:401/:434
    depend on it); the 7 "Could not switch GM to DJ mode" skips ->
    F-394 (CM; this covers the "Same kind as F-402. No F-ID" one-liner
    above and AE B1); test_gate_closed_e2e.py:137 -> F-405;
    test_filter_deploy_e2e.py:315 -> new F-406;
    test_venue_gate_e2e.py:165/:180 -> new F-407. No P-level given for
    F-406 or F-407. TW item 3: their defect records go to the TW docs
    queue.
  - One-liner (TW docs batch, via CM; "low priority" (CM); no P-level
    given): defect records for F-402, F-405, F-398 and F-399.
     TW (direct, 2026-10-26): LOW priority, after US-172 and the DJ
     path, timing for the PO to pick; each of the four has an ID but
     no defects/*.md file and no index row on main. QE N3 (#67,
     74723586): F-402 and F-405 "exist only as backlog IDs. F-405 is
     the `test_gate_closed_e2e.py:137` D-063 masking I asked an F-ID
     for, so the PM should schedule its record." PM: no P-level given
     by either; scheduling is the PO's pick.
  UPDATE (CM, QE, 2026-10-26, after v256): CI 40333713247 at f715538e
  is green on all 4 jobs. QE count profile MET
  (/tmp/pr64-qe-countprofile-f715538e.md, sha256 96abe4fb, verified at
  PM read): a third profile, explained, does not block #64.
  Service-integration 81 = 64 passed + 14 skipped + 3 xfailed + 0
  xpassed; the 7 extra skips are "Could not switch GM to DJ mode"; one
  XPASS became an XFAIL (test_full_session_api, non-strict F-262
  xfail, test_measurement.py:173), not in #64's diff, so pre-existing
  F-262 behaviour; collected count identical; other suites unchanged.
  worker-1 is finishing the PR body. Still open: the QE's diff-only
  Rule 13 re-check at f715538e, once the CM sends the body and bundle
  (CM, QE).
  - One-liner (QE, adding to ruling (a); also proposed by worker-1 via
    CM), QE verbatim: "test_full_session_api (F-262 xfail, non-strict)
    flips XPASS/XFAIL between CI runs on main-equivalent code; same
    kind as F-402." XPASS in 40314977506 and 40320048783, XFAIL in
    40333713247. No F-ID, no P-level given.
  UPDATE (CM, UX, 2026-10-26, after v257): the PR body a2bfb9af is
  live, and the review bundle /tmp/pr64-review-f715538e/ is out to all
  7 reviewers (CM).
  - UX: APPROVE at f715538e, pin verified
    (/tmp/pr64-ux-verdict-f715538e.md, sha256 3a8e85ff, verified at PM
    read). UX endorses two existing one-liners: the venue-gate
    indicator timeout skipped instead of failed
    (test_venue_gate_e2e.py:165/:180), and the gate-closed-at-load
    test masking an open gate as a skip (F-405). Nothing new.
  - CM note: the QE's count-profile file 96abe4fb has a diff-scope
    slip. It says all 7 files are under tests/unit; the diff is 4 test
    files + flake.nix + test-e2e.sh + F-362.md. The QE decides on any
    correction.
  UPDATE (CM, 2026-10-26, after v258): PR #64 MERGED as
  ff091e5faacf7bd00e59f9719d39fdd0cc902888 at 14:59:11Z (origin/main
  head at PM read). 7/7 APPROVE at f715538e, CI 40333713247 green.
  Frozen verdicts in /tmp/cm-relay/PR64/frozen-verdicts-f715538e/,
  each sha256 verified at PM read: AE 73d1966b, SEC 6e9325f3, TW
  42070817, QE df2c1291, ARCH 80a5b191, UX 3a8e85ff, AD 54c8912d.
  F-362 ACs 3-5 done; ACs 1-2 and the test_filter_routes.py:35 guard
  stay with US-174d (worker-4). SecSpec: "Must be closed there; I will
  check it in the 174d review."
  - QE verdict df2c1291 supersedes 0d9e52e7 and corrects the scope
    sentence in 96abe4fb and dea15e43: the diff touches 7 files, not
    "all under src/web-ui/tests/unit/"; conclusions unchanged. This
    resolves the CM diff-scope note above. QE: no new one-liners.
  - Stale body sentence (AD nit, TW item 1, QE N1): the per-module
    numbers were re-checked unchanged at f715538e. History now
    (merged); no action.
  - TW item 2, verbatim: "The F-362 row in defects-index still shows
    only "open. ..." without the new "in progress (PR #64 / 174d)".
    It's an index summary and not wrong, so it can be refreshed when
    F-362 closes in 174d."
  - TW item 3, verbatim: "Once the PM assigns the F-IDs for the
    non-accepted skips (F-402 already exists), they need defect
    records." PM: no F-IDs allocated for them; none requested of the
    PM so far (asked the CM).
  - UX (3a8e85ff) supports two non-accepted skips, already one-liners
    above. Verbatim: test_venue_gate_e2e.py:180/:165 "A timeout must
    be a FAIL (or an xfail with an F-ID), not a skip.";
    test_gate_closed_e2e.py:137 "Until the QE's fix lands, this test
    is not evidence that the UI shows the gate closed at startup."
  Non-blocking one-liners from the #64 verdicts (no F-ID; no P-level
  given except where quoted):
  - AE B1 (73d1966b), verbatim: "5 test_mute_e2e.py cases and 2
    test_audio_flow.py cases SKIP on "Could not switch GM to DJ mode".
    This is the same masking class as F-405: a mute or audio-flow
    safety test must not read as SKIP when its precondition fails in a
    stack that should support it. Fix before amps-on."
  - AE B2, verbatim: "test_full_user_journey.py:348 "No completed
    session for D-009 check" skips. The D-009 journey check never runs
    in CI until F-262 lands. Re-check after #66."
  - Architect N2 (80a5b191), verbatim: "the 14 service-integration
    skips, 7 of them "Could not switch GM to DJ mode", predate #64 and
    are the QE's documented baseline. They are not caused by this
    diff."
  - AD L1 (54c8912d; AD review message: "low priority"), verbatim:
    "scripts/test/run-room-sim-e2e.sh:70 still runs pytest without
    `-rs`. No nix app or CI step calls it (it is only cited in
    US-174.md:32), so it is outside AC5 as written. Add `-rs` next
    time the script is touched."
  - -rsx (one row; Architect N1 and AD L2). Architect N1, verbatim:
    "-rs reports skips only. If XFAIL reasons are also wanted in the
    CI summary (see the QE's test_full_session_api XPASS/XFAIL flip),
    -rsx is the cheap extension. Not needed for F-362's ACs." AD L2,
    verbatim: "-rs reports skips only. An xfail can mask a failure the
    same way a skip does (see the test_full_session_api flip and the
    non-strict xfails), and xfail reasons stay unprinted. Backlog
    idea: `-rsx` across the test apps." AD message: "low priority". PM
    cross-ref: the test_full_session_api flip one-liner above.
- **F-402** Integration test turns a 500 from POST /filters/generate
  into a skip, hiding a real server error
  (test_full_user_journey.py:179-183) (QE, 2026-10-26; option (b), ID
  allocated by the PM, checked free across main, all branches and
  worktrees). QE reason: the defect is the skip that hides failures,
  whatever causes the 500; whether F-156 regressed is unknown, and
  reopening it now would guess the cause and record the wrong fix.
  Priority (QE): room-correction path, goes with the F-262 and US-174
  work, not the safety backlog (no P-level given).
  ACs (QE suggested):
  - (1) test_full_user_journey.py:179-183 no longer turns a 500 into a
    skip; any 5xx from POST /filters/generate FAILS the test, with the
    response body in the assert message.
  - (2) the current 500 gets a diagnosis, with the traceback from the
    CI or local-demo server log. If it is numpy bool_ again: reopen
    F-156, link it, and close F-402 as the test-side fix. If it is
    something else: name it, under F-402 or a new ID.
  - (3) at the final head, generate_crossover_only,
    crossover_filters_are_d009_compliant and pw_config_generated PASS.
    The two dependent Phase-8 skips (l.331 and l.348, "no completed
    session") are rechecked: they pass, or skip only for a reason that
    is real and named.
  - (4) sweep tests/integration and tests/e2e for pytest.skip driven
    by an HTTP status; list what is found.
  Cross-refs: F-156 (stale reason text; RESOLVED, task #159), F-362
  AC5 (the filter_routes import skip), F-262 (session filter-gen).
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
  Note (SecSpec, via CM, 2026-10-26), verbatim: "web UI has
  coefficient write access from US-174d on; F-037 auth or web-ui
  deploy disabled required before amps-on."
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
  UPDATE (CM, 2026-10-26, after v261): F-394 is PR #68 (draft,
  worker-1, head 257b272d); CI 40346339865 running. Fence r2 adds
  scripts/test-e2e.sh. worker-1 consult Q1-Q3
  (/tmp/cm-relay/F-394/frozen/w1-257b272d-consult-Q1-Q3.txt, sha256
  7f4cae29, verified at PM read): Q1 stimulus in the CI local-demo
  (worker-1 recommends (a), a --tone option in mixxx-substitute.py);
  QE writes, AE releases or objects. Q2 whether the mute tests assert
  on level-bridge-hw-out, and whether opening the gate in the virtual
  CI stack is acceptable (worker-1 will not do it without an explicit
  ruling); AE writes, QE releases. Q3 ensure_dj_mode function-scoped
  vs module reorder (worker-1 recommends function scope); QE writes
  alone. CI virtual local-demo only; no Pi, nothing played.
  UPDATE (CM, QE, 2026-10-26, after v262): release record (g)
  (d7079ade, verified at PM read). Frozen copies under
  /tmp/cm-relay/F-394/frozen/.
  - Q2 (AE writes; ae-Q2-mute-tap-gate e37c80fa) RELEASED by the QE
    (/tmp/f394-qe-Q2-release-ae-e37c80fa.md, sha256 86e51a0f, verified
    at PM read): "This release is for that exact sha." and
    "**RELEASED.** No objection; the notes below are non-blocking and
    need no new AE version." Relayed to worker-1 (CM).
  - Q3 (QE sole writer;
    /tmp/f394-qe-Q3-ensure-dj-mode-scope-257b272d.md, sha256 19429bd0,
    verified at PM read): function scope, conditions Q3-1 to Q3-4;
    reordering rejected. Final; relayed to worker-1 (CM).
  - Q1 (QE writes; /tmp/f394-qe-Q1-stimulus-257b272d.md, sha256
    0919d10d, verified at PM read): option (a), a tone mode in
    mixxx-substitute.py, conditions Q1-1 to Q1-7; (b) rejected on test
    adequacy and the routing.rs fence. AWAITING AE RELEASE, not
    relayable (CM); the AE input caee35e0 is NOT a release. The AE
    separately rules whether the "no signal-gen play" rule covers a
    synthetic tone.
  - UPDATE (CM, AE, 2026-10-26, after v264; supersedes "AWAITING AE
    RELEASE" above): Q1 0919d10d RELEASED by the AE
    (/tmp/cm-relay/F-394/frozen/ae-Q1-release-a532179b.txt, sha256
    a532179b, verified at PM read), verbatim: "I release 0919d10d as
    written, with no objections." Relayed to worker-1; Q1-Q3 are all
    relayed (CM).
     AE values (own file; they don't change 0919d10d): V1 1000 Hz
     exactly and -20 dBFS peak, as named constants. V2 (derived from
     the constants, read after >= 1 s settle): level-bridge-sw ch 1-2
     -20.0 dBFS peak +/-1.0 dB; level-bridge-hw-out ch 1-2 -40.0 dBFS
     peak +/-1.5 dB (local-demo Dirac, gain_db -20); ch 3-8 at sw <=
     -120 dBFS; mute <= -120 dBFS within 2 s on hw-out ch 1-2; unmute
     back in the V2 window within 2 s. Guard, AE: "FAIL, never skip"
     naming the cause if the active venue or coefficients aren't the
     local-demo Dirac set. V3 (optional, not required for F-394): sub
     channels presence only, at least 40 dB above the closed floor, no
     window.
     Fence r3 (/tmp/cm-relay/F-394-fence-r3.txt, sha256 1f8c0ca2,
     verified at PM read; supersedes r1 f8440e87): worker-1 owns
     backend.py, test_mute_e2e.py, scripts/test-e2e.sh (r2, by message
     only, now recorded) plus, new in r3, scripts/mixxx-substitute.py
     and scripts/local-demo.sh. No overlap with #63 (3f28b6c7), #66
     (ff985455) or #52 (27e90a0d) (CM).
  - One-liner (QE, non-blocking; no F-ID, no P-level given): PR #36
    (F-270 audio_stimulus) is superseded for test_mute_e2e by F-394;
    its failure paths are all skips, and its signal-gen premise
    contradicts the DJ routing.
  - One-liner (QE, non-blocking; no F-ID, no P-level given): the
    autouse _ensure_standby in test_production.py ignores the
    _set_mode return value (l.53/55), so a failed standby switch goes
    unnoticed.
  - UPDATE (CM, 2026-10-26, after v265): head e050fe90 pushed, on
    d3d7479c (PM-verified on origin). Per CM: d3d7479c = Q3 plus C1-C3
    groundwork; e050fe90 = Q1 tone, Q2 C4 mute sequence, Q1-6 xfails
    removed. CI 40348754608 running; the earlier run 40346339865 was
    cancelled by the concurrency group before E2E.
     Fence r4 (/tmp/cm-relay/F-394-fence-r4.txt, sha256 841f6715,
     verified at PM read; supersedes r3 1f8c0ca2): adds
     src/web-ui/tests/service-integration/test_audio_flow.py and the
     new unit tests test_mixxx_substitute_tone.py and
     test_virtual_gate_guard.py. No overlap with #63, #66 (7011419d),
     #52, #45, #44, #43, #42, #40 or #36 (CM).
     Side finding F-410 (unmute behind a closed gate) is filed
     separately; it is outside F-394.
  - UPDATE (CM, 2026-10-26, after v270): head 51fae218 "fix(tests):
    F-394 AC ii — skip GM push events in RPC replies, real PW socket
    for pytest" pushed (PM-verified on origin, parent e050fe90). CI
    40356547804 running.
     Fence r5 (/tmp/cm-relay/F-394-fence-r5.txt, sha256 015ca022,
     verified at PM read; supersedes r4 841f6715):
     scripts/local-demo.sh widened to cover cmd_env as well (the
     XDG_RUNTIME_DIR / pw_runtime_dir derivation around l.39-40; the
     rest of local-demo.sh stays fenced), plus the NEW
     src/web-ui/tests/unit/test_rpc_call_event_skip.py (T1 regression
     test for _rpc_call skipping GM push events). Only the stale #40
     also touches local-demo.sh: recorded, no hold (CM).
  - UPDATE (CM, QE, 2026-10-26, after v271): #68 head 0cb35f0c
    "fix(local-demo): F-394 env reads the running stack's PW paths
    from the manifest" (PM-verified on origin, parent 51fae218).
    Throwaway 999abd11 (tone stimulus disabled; parent 0cb35f0c) and
    its revert e06d6296 exist (PM-verified).
     QE ruling on AC (iv): /tmp/cm-relay/F-394/qe-ACiv-9402c6eb.md
     (sha256 9402c6eb, verified at PM read). Verbatim: "RULING: either
     head is acceptable. QE prefers e06d6296 (worker-1's alternative),
     so the runs can start now." The N>=5 series counts at a head H
     whose diff to the final head is docs only (git diff --stat
     H..final; nothing under src/, tests/, conftest*, pytest/pyproject
     config, nix/, flake.*, configs/, scripts/ or .github/). A red run
     restarts the count; each run must show the DJ group really ran.
     The 999abd11 runs are not part of the series: they are the
     Q1-7(2) / AC (iii) RED evidence. Condition 3: e06d6296's tree
     must equal 0cb35f0c's. Rule 13 still needs normal T1-T3 CI green
     at the final head. AC (vi) (mute verified) is not ruled here; it
     stays open for the AE and QE.
     PM cross-ref: git rev-parse e06d6296^{tree} and 0cb35f0c^{tree}
     both give a7429a26, so condition 3 holds at PM read. The QE
     verifies it in the review.
     One-liner (worker-1 side note, outside F-394; no F-ID, no P-level
     given): local-demo.sh cmd_env/resolve_nix_paths, in the CM's
     wording (/tmp/cm-relay/pm-pending.txt): "silently runs nix build
     when PW_STORE is set but isn't a directory". PM cross-ref:
     scripts/local-demo.sh l.121-124 at 0cb35f0c, if [ ! -d
     "$PW_STORE/bin" ], echoes "Fetching pipewire..." and runs nix
     build --no-link nixpkgs#pipewire (l.125-128 do the same for
     WP_STORE).
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
  v19 SCOPE ADDITIONS (AE rulings via the TW, 2026-10-26; from UX gaps
  on US-173; NOT in US-173; v19 stays PRE-PROD and PAUSED per the PO):
  (1) F-315 ramp wording in five places in safety.md: row 13, the
  F-373 rule, §8 "Opening the gate ramps" and the WirePlumber restart
  text (two places), all to AE-verbatim "instant step to the venue
  gain (F-315)" wording; the TW holds the exact texts. AE:
  safety-relevant, because an operator would expect a fade that
  doesn't happen. Amps-on row 13 here follows when v19 merges (mirror
  rule). (2) The F-318 "How to make sound" bullet gets a
  half-sentence: amps stay off until the AMPS-ON list holds, and the
  test signal proves only the digital path. AE ruling: a test signal
  with amps off is NOT "signal-gen measurement use" under the Pi 5
  header.
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
  UPDATE (CM, 2026-10-26): F-399 pushed at ec845553. worker-4 is
  merging main and drafting the PR body; the PR opens after that. Open
  placement ruling: the AE on F-399 nit 2 (absolute vs difference
  premise).
  UPDATE (CM, 2026-10-26): F-399 pushed at 2fb05039, merging main
  289f1a72 clean (3 files, +443/-27). AE RULING on nit 2: add an
  absolute premise `assert uncorrected_right >= 4.0`, marked (a0), and
  keep the difference assert (a). worker-4 adds the (a0) commit and
  body draft 2; then the CM opens the PR.
  PR #65 OPEN (CM, 2026-10-26): "fix(F-399): stage venue runner
  outputs, publish only a passing set". Final head 13995e15 (the (a0)
  commit on top of 2fb05039); body draft 2 (sha1 b863b180); diff
  against main 289f1a72: 3 files, +444/-27. Review bundle
  /tmp/pr65-review-13995e15/ (pr65.diff sha256 d06cb3ef...). CI run
  40317165021 in progress; code, not CI-exempt. Team-lead asked for
  the 7 reviews. Tally 0/7.
  #65 verdicts at 13995e15: UX APPROVE (comment 6415192205; holds only
  if CI run 40317165021 goes green). AD APPROVE with L1 (verdict with
  CM). QE APPROVED WITH CONDITIONS: C1 CI run 40317165021 green,
  room-correction collected = 1358, the new tests PASSED by name; C2
  evidence for the "13 mutations" claim, or the claim removed from the
  PR body. Tally 3/7 (UX, AD, QE conditional).
  #65 backlog notes (non-blocking, not Rule 13; no priority given):
  - UX N1 (pre-existing, verify.print_report): "ALL CHECKS PASSED -
    filters safe to deploy" also prints for SIMULATED sets. Suggested:
    "ALL CHECKS PASSED - simulated set, not deployable".
  - UX N2: the coeffs-dir guard's ValueError probably surfaces as a
    traceback. Suggested one-liner: "Refused: simulated outputs never
    go into <coeffs dir>; choose another --output-dir."
  - QE 1: the test_venue_closed_loop crash walk patches global
    os.replace/os.remove; use a vp-local seam so unrelated calls
    cannot shift the k counter.
  - QE 2: venue_pipeline coeffs guard is equality-only realpath;
    consider refusing simulated output into any path under
    DEFAULT_COEFFS_DIR. (Same point as the AD's US-174d AC below.)
  - QE 3: US-174c/d deploy: tests for the consumer contract. Refuse on
    SIMULATED present, delays.yml missing/unparsable, or simulated !=
    false, and never recurse into a leftover .rc-staging-* dir. (Tests
    for the US-174d AC recorded under F-399 above.)
  - TW (owner: TW, docs queue, user-journeys runner examples):
    pre-existing drift. docs/user-journeys.md section 7 (l.721-745)
    shows delays.yml in the old CamillaDSP-era format (delays_ms /
    delays_samples, "Apply delays in CamillaDSP"). The real schema is
    venue / simulated / scenario / note / channels; #65 adds simulated
    and scenario.
  US-174d AC (AD, from #65): the simulated-set guard
  (venue_pipeline._refuse_simulated_into_coeffs, currently realpath
  equality) becomes a commonpath-prefix check covering
  coeffs/sets/<id>, `current` and `committed`. It compares against
  both deploy.DEFAULT_COEFFS_DIR (env-overridable) and
  pw_config_generator's /etc/pi4audio/coeffs, with tests. PM cross-ref
  only: F-372 asks for the same commonpath fix at a different site
  (filter_routes.py).
  CORRECTION (CM, 2026-10-26): #65 has all 7 verdicts posted at
  13995e15 (v214 counted 3/7): UX 6415192205, SecSpec 6415203689, AE
  6415204084, Architect 6415204565, AD 6415205055, QE 6415226025
  (C1/C2), TW 6415226482 (with notes N1-N3). All depend on CI run
  40317165021 going green. QE C2 is with worker-4: back the mutation
  claim with a list or drop it from the body; a body edit, so the head
  stays 13995e15.
  QE (accounting + CM, 2026-10-26): #65 C2 ACCEPTED, option (a)/(i).
  The mutation evidence is real and the needle-asserted mutations are
  applied; body draft 3 (589ff437) applied. CI 40317165021 is the
  unmutated baseline (sources byte-identical), so C2 is MET when C1 is
  MET. Only C1 is open.
  TW #65 notes (verbatim source /tmp/tw-verdict-pr65-13995e15.md,
  comment 6415226482; non-blocking):
  - N1: the module docstring says "Consumers (US-174c/d deploy) treat
    a set as NOT deployable if SIMULATED is present, or delays.yml is
    missing, unparsable, or lacks `simulated: false`." Present tense,
    but no consumer on main does it yet; the check lands with US-174d.
    Suggested: "Consumers must treat ... (US-174d deploy)", or leave
    it, since it becomes true when 174d merges.
  - N2: one docstring line in the "Output staging" paragraph runs past
    100 characters (the one ending "So "delays.yml present" means the
    set next"). Re-wrap it.
  - N3: pre-existing docs/user-journeys.md section 7 delays.yml drift;
    same item as the TW backlog note above (TW docs queue).
  SecSpec INFO (operator docs): publishing deletes stale
  combined_*.wav files in the chosen --output-dir. Intended, and
  stated in the module docstring.
  US-174d CONDITIONS from the #65 review (CM relays them to worker-4
  once #65 merges and 174d picks them up):
  - (1) Architect, BINDING: the F-399 guard
    _refuse_simulated_into_coeffs refuses an output dir EQUAL to OR
    INSIDE either coeffs root (PRODUCTION_COEFFS_DIR and
    DEFAULT_COEFFS_DIR, including sets/), using the same list as
    deploy.py:191; add a test for a simulated run targeted at
    coeffs/sets/<x>. The same finding came from SecSpec LOW
    (commonpath containment) and AD L1 (prefix check, tests for
    coeffs/sets/x and coeffs/current). AD and AE N2: compare against
    both the env-overridable DEFAULT_COEFFS_DIR and the literal
    /etc/pi4audio/coeffs (hard-coded at pw_config_generator.py:52). PM
    cross-ref: same point as the AD US-174d AC above.
  - (2) AE N1: before a real run publishes into the live coeffs dir,
    174d needs (a) an atomic swap and (b) a check that every WAV the
    filter-chain references still exists after the stale-file sweep.
  TW side finding (backlog one-liner, via CM, 2026-10-26; TW docs
  queue; no priority given): F-398 and F-399 have only backlog entries
  and no defect records.
  MERGED (CM, 2026-10-26): #65 merged as 29f5c61f; 7/7 at 13995e15, CI
  40317165021 green, QE C1 final. PM cross-ref: this meets the "once
  #65 merges" trigger for the US-174d CONDITIONS relay above; 174d
  stays frozen until F-262 lands from main (see F-262).
  (3) Architect, single-writer condition (2026-10-26, via CM),
  verbatim: "the single writer materializes every file the convolver
  conf loads. A speakerless convolver channel named zero.wav gets the
  canonical configs/coeffs/zero.wav bytes under its convolver filename
  (e.g. combined_sub2_lp.wav), and dirac likewise. A missing file is
  refused." Background (CM): the convolver loads fixed names
  (combined_*.wav), while venue_pipeline names files after the venue
  `coefficients:` field, so a generated set never contains
  combined_sub2_lp.wav for a speakerless ch 4, and whatever file was
  deployed before stays live. AE agrees (it covers the AE's N1 above)
  and adds that the installer verifies the zero bytes are all-zero
  before the swap.
  RELAYED (CM, 2026-10-26): CONDITIONS (1)+(2) and (3) sent verbatim
  to worker-4. 174d stays frozen until F-262 lands.
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
  OWNER (PM proposal, team-lead confirmed, 2026-10-26): worker-7 owns
  F-383 + F-384 as the one dedicated worker of the team-lead staffing
  ruling (2026-10-25). Team-lead, verbatim: "worker-7 counts as the
  "new worker" for F-383 + F-384. The point of that ruling was that
  one dedicated worker owns both items, with no second writer." PM
  cross-ref: US-174 (#57) and F-374 (#55) are merged; #66 at 4724e65d
  changes combine.py and correction.py, so all post-#66
  correction/combine work (F-411 phase 2, B1, F-383, F-384) sits with
  worker-7, in sequence. Conditions (team-lead): phase 0 is read-only
  and offline (scratch copy; CM go for the scratch-copy use pending at
  this version); F-411 comes first; no code commits until #66 merges
  or the CM revises the fence; the phase-0 report goes to the AE and
  the Architect as a frozen file. Phase 0 scope (PM proposal): the
  F-383 calibration step (a dirac correction x LR4/LR8 x 80/200 Hz
  through the output check, with the -46 dB fallback rule) and the
  F-384 step-9 overshoot measured on the #66 code.
  PHASE 0 GO (CM, 2026-10-26; supersedes "CM go for the scratch-copy
  use pending at this version" above): brief
  /tmp/cm-relay/F-383/w7-F383-F384-phase0-brief-r1.txt (sha256
  b74a78a0, verified at PM read). Fresh git-archive scratch copy
  /tmp/w7-F383-scratch-4724e65d (PM read: .SOURCE-SHA 4724e65d;
  correction.py 203cd320, combine.py 5e935128); the F-411 scratch copy
  stays separate. Read-only, offline, no commits until #66 merges or a
  CM fence revision.
  PHASE 0 REPORT r1 (worker-7 via CM, 2026-10-26):
  /tmp/cm-relay/F-383/frozen/w7-F383-F384-phase0-r1-dadab0bf.md
  (sha256 dadab0bf, 15262 bytes, verified at PM read), source 4724e65d
  (crossover.py 30efb7c9 as well). Relayed by the CM to the Architect
  (single writer of the joint ruling) and the AE (releases). PM
  summary:
  - (1) F-383 calibration: the -46 dB fallback TRIGGERS. Dirac x LR8
    LP fails the output check at -38.8 dB (80 Hz) and -37.7 dB (200
    Hz), limit -40; every LR4 leg and both LR8 HP legs pass with >=
    10.5 dB margin; all tails pass by > 160 dB. worker-7's diagnosis:
    a check artefact (float64 rounding floor of |H| in the LR8 LP
    stopband; no floor 1e-30..1e-6 and no padding 4x-16x gets under
    -38.9 dB; against the LR design magnitude the same legs are -84
    dB).
  - (2) Extra finding, undiagnosed: dirac x LR HP x
    generate_subsonic_filter gives -15.8 to -30.4 dB, including the
    first-DJ-session markaudio sat (CHN-50P mandatory_hpf_hz 80 x LR4
    200 Hz HP) at -27.8 dB; the subsonic FIR alone -23.1 to -44.0 dB.
    Deployed files are not affected today (combine re-synthesizes; -74
    to -101 dB).
  - (3) F-384 on the #66 code: the overshoot is inter-bin from steps
    7-8, not step 9; worst +0.165 dB over the -0.5 dB margin (home_lab
    sat_right), never above 0 dB; step 9 does not measurably break
    min-phase (res4x <= -162 dB, tail <= -102.9 dB). These scenarios
    do not exercise the F-384 defect; the AC test needs a forced
    input. Worker-4's a3bc538c figures (-0.35 / -0.41 dB) reproduced
    exactly at 4724e65d.
  - (4) Info: a polarity-inverted output scores +6 dB in any check of
    this form. PM cross-ref (sent to the Architect): Sub2 is
    phase-inverted for isobaric loading (CLAUDE.md design decision 1).
  ITEM (2) SUBSONIC RULING (AE writer, Architect to release; NOT yet
  released at this version):
  /tmp/cm-relay/F-383/frozen/ae-F383-item2-subsonic-ruling-935b4ee2.txt
  (sha256 935b4ee2, 3310 bytes, verified at PM read). Verbatim,
  reflowed, without its title line:
  - Input:
    /tmp/cm-relay/F-383/frozen/w7-F383-F384-phase0-r1-dadab0bf.md,
    sha256
    dadab0bf7caa20dd67b0dae4f1c31033777492e60dc8eb35c973f323a16cfb6b
    (verified at read). Source pin 4724e65d.
  - Why it is audio-side: the subsonic FIR is the driver-protection
    HPF (D-031, US-179 AC6b pick (a)). If it is not minimum-phase, it
    puts pre-ringing at the HPF corner into every sat that has a
    mandatory HPF, which goes against the transient requirement. Today
    nothing audible is affected: combine re-synthesizes the product,
    and the deployed files measure -74 to -101 dB. Once the FINAL
    mechanism stops re-synthesizing, the factor's own phase reaches
    the speaker. So this must be settled before the F-383 FINAL
    mechanism merges. It does not block the first DJ session on the
    current files.
  - S1 Diagnosis (worker-7, read-only, offline, may start now). Run it
    for generate_subsonic_filter at each of 80/24, 40/24, 40/48 and
    25/24:
     a) Build the reference from the DESIGN magnitude (the power-law
     knee itself, not |rfft(h)|), with a cepstral FFT of at least 64·n
     and an absolute floor of 1e-20. Truncate it to n. Report the
     residual of h against this reference.
     b) Report the energy before the main peak re total energy, and
     the time of the peak in samples. This is a direct pre-ringing
     measure.
     c) Repeat a) with the production design's FFT size and the 1e-10
     floor, to show which of the two causes the aliasing.
  - S2 Decision rule:
     - If a) is ≤ -60 dB for every case, it is a CHECK ARTEFACT. The
     fallback's "report-only" scope then extends to LR × subsonic
     products. The gate becomes the subsonic-alone design-reference
     check at -40 dB plus the existing correction-input check.
     - If a) is > -40 dB for any case, it is a REAL DEFECT and the
     subsonic FIR is fixed in the F-383 PR.
     - Anything in between goes back to the AE before any decision.
  - S3 Constraints on any fix (the Architect designs it, the AE
    releases the magnitude):
     - Keep the corner at mandatory_hpf_hz = 0.8 × the declared limit.
     - Keep ≥ 18 dB attenuation at corner/2 (AC6b pick (a)).
     - Passband above 1.5 × corner: within 0.1 dB of today's filter.
     - No gain above 0 dB anywhere.
     - Design-reference residual ≤ -60 dB and tail ≤ -60 dB re peak.
     An analytic min-phase HPF (for example a Butterworth impulse
     response with order = slope/6) would meet this by construction.
     It is acceptable to the AE if the magnitude constraints above
     hold.
  - Review points for the Architect's joint ruling on (1), (3), (4)
    and (5). These are points, not text for that ruling:
  - P-a (1): I agree with the artefact reading of LR8 LP (-84 dB
    against the design reference). The fallback is acceptable to me
    provided the LR legs are checked against their DESIGN magnitude,
    not left unchecked.
  - P-b (4): the check must not depend on polarity. Score against
    min(ref, -ref), or normalize the sign of h first. Sub2 may be
    polarity-inverted for isobaric loading; a +6 dB false fail there
    is not acceptable.
  - P-c (5): an overshoot of +0.165 dB above the -0.5 dB margin, still
    ≤ 0 dB, is harmless in audio terms; D-009 holds. A fix may go in
    F-384, but it is not a safety item. The F-384 AC needs the
    forced-input case from phase 1.
  PM cross-ref: S1 reads "(worker-7, read-only, offline, may start
  now)", while the CM holds S1 until the Architect releases 935b4ee2
  (joint-text rule); the CM's hold governs until that release.
  F-384 FORCED-INPUT TASK (PM pick, team-lead GO, 2026-10-26):
  worker-7, read-only and offline on /tmp/w7-F383-scratch-4724e65d, no
  #66 files: find and document an input IR with a clear native-bin
  excess before step 9 and measure step 9's effect on the min-phase
  residual and tail, for the F-384 AC "with a test that forces the
  overshoot branch" (Architect, 2026-10-25). Brief (CM):
  /tmp/cm-relay/F-383/w7-F384-forced-input-brief-r1.txt (sha256
  8fb41306, verified at PM read). Team-lead conditions, verbatim: "No
  commits." "No mechanism decisions." "Results go as a frozen file to
  the CM." "If the joint Architect+AE ruling lands first, worker-7
  freezes the work and follows the ruling." "F-411 phase 2 still takes
  priority once it opens." F-370 stays the fallback (team-lead).
  worker-7 PRIORITY ORDER (CM, 2026-10-26): (1) F-411 phase 2 (after
  #66 merges or a fence revision); (2) the F-383 item-2 subsonic
  diagnosis S1 (935b4ee2, once the Architect releases); (3) the F-384
  forced-input task. When a higher item opens, worker-7 finishes the
  current step, freezes and switches.
  UPDATE (CM, team-lead, 2026-10-26, after v287; supersedes "NOT yet
  released at this version", the S1-hold cross-ref and "once the
  Architect releases" above): the Architect released the AE subsonic
  ruling 935b4ee2 in full (S1-S3). Team-lead, verbatim: "The AE's
  subsonic ruling 935b4ee2 is released by the Architect in full, so it
  is no longer "not yet released". The CM's hold on worker-7's
  diagnosis is lifted."
  F-383 RECORD (CM, 2026-10-26; replaces the CM's earlier F-383 record
  note and team-lead's earlier r4 version), verbatim: "F-383 record
  (team-lead final stop rule, 2026-10-26): A r3 89c3bb1b + B r1
  349b585f + AE 935b4ee2 (released by both, S1-S3) + AE diagnosis job
  c281701b (Architect-released). A r4 10ae380a and B r2 3ac658cd are
  equivalent, released by both co-authors, not governing. A4 is
  identical in all versions. VOID: A r1 3e683d42, A r2 3d648255, AE
  f8ad626d. worker-7 runs phase 0b on this record; no further A/B
  revisions until worker-7 reports."
  Files (all /tmp/cm-relay/F-383/frozen/, sha256 verified at PM read):
  arch-F383-F384-ruling-A-r3-89c3bb1b.txt (10284 bytes),
  arch-F383-F384-ruling-B-r1-349b585f.txt (3557 bytes),
  ae-F383-item2-subsonic-ruling-935b4ee2.txt,
  ae-F383-S1-diagnosis-job-c281701b.txt (2308 bytes); not governing:
  arch-F383-F384-ruling-A-r4-10ae380a.txt (9360 bytes),
  arch-F383-F384-ruling-B-r2-3ac658cd.txt (2823 bytes).
  PM cross-ref: B r1 still carries the B4 subsonic floor proposal
  (pass floor 1e-20; the AE decides; the F-383 combine waits); B r2
  marks B4 VOID. As B r1 and B r2 are "equivalent", B4's status rests
  on 935b4ee2 (the AE's decision); no P-level given. The PM's four
  open questions to the CM (A r4 header citing f8ad626d, A r3 VOID vs
  superseded, c281701b citing A r2's A4, no AE release file of A r4
  seen) are closed by this record line ("released by both co-authors",
  "A4 is identical in all versions").
  worker-7 (CM, 2026-10-26): holds this set for phase 0b (A4 prototype
  validation + diagnosis job c281701b) and switches after the current
  F-384 forced-input step; priority order otherwise unchanged.
  RELEASES BEHIND THE RECORD (CM, 2026-10-26; answers the PM's
  questions (i)-(iv); all are MESSAGE releases relayed by the CM, no
  new files). CM: the final record line above supersedes every earlier
  version.
  - (i) B r2 3ac658cd: AE release by message, verbatim: "B r2
    3ac658cdb62493f14eff43eb0472e203ca604cc3946816dc49f3cf1609cc5523:
    AE RELEASE, on the B1-B3 terms as written." AE later, verbatim:
    "My releases of r4/B r2 and of r3/B r1 both stand." f8ad626d is
    moot as a split text; B r2 is not governing in any case (CM).
  - (ii) A r3 89c3bb1b is GOVERNING; the A r4 header's "VOID" label
    was overtaken. Architect, verbatim: "My earlier 'r3 void' no
    longer applies" (accepted the record).
  - (iii) c281701b's "Part A r2's A4" means A4 of the governing A r3
    89c3bb1b; the Architect confirmed A4 is identical in A r2, r3 and
    r4, so the job content does not depend on the label (CM).
  - (iv) A r4 10ae380a: AE release by message, verbatim: "AE RELEASE
    of A r4
    10ae380a5cbdf001fcec4c57136939986c2a68f0142ba7afb5e2198bb2d44b81
    (verified at read, diffed against r2 and r3; OBJ-1 is fixed)."
    Architect, verbatim: "Architect RE-RELEASE of A r4 10ae380a… and B
    r2 3ac658cd." Still not governing (CM).
  - A r3 / B r1: AE release of A r3 by message, verbatim: "AE RELEASE
    of A r3 89c3bb1b… OBJ-1 is fixed"; B r1 released in the AE review
    file c37634c5.
  F-384 FORCED-INPUT REPORT r1 (worker-7 via CM, 2026-10-26):
  /tmp/cm-relay/F-383/frozen/w7-F384-forced-input-r1-92b75b51.md
  (sha256 92b75b51, 9423 bytes, verified at PM read). Read-only and
  offline on scratch 4724e65d; "Facts only, no mechanism decisions."
  With the AE and the Architect for a ruling (CM). Headline (CM): the
  forced inputs reach step 9, but the gate passes, so they can't
  discriminate.
  - Forced inputs: case A (production n_taps 16384) +0.345 dB over
    -0.5 dB on 58 bins, also via correction_from_measurement for
    sat_left, sat_right, sub1; case B (n_taps 2048) +0.664 dB on 480
    bins.
  - Step 9 keeps the old phase (max 1.6e-14 deg), clips native bins to
    -0.5000 dB, and the output still PASSES the F-384 gate (residual A
    -99.4 / B -98.1 dB; tail A -91.0 / B -78.0 dB re peak). Verbatim:
    "it does **not** separate the current step 9 from a fixed one at
    -40/-60."
  - Gate teeth: hard-edged old-phase-kept edits (-0.345 to -6 dB) pass
    the residual (closest -43.6 dB) but fail the tail at every size;
    step 9's real edits taper to zero at band edges and do not trip
    the tail.
  - Inter-bin peak not bounded: case A -0.120 to -0.102 dB; case B
    +0.164 to +0.025 dB, above 0 dB (would fail
    test_corrections_never_boost; n_taps 2048 is not a production
    length). n_taps 512 (100, 18, 20): step 9 itself pushed the tail
    from -60.1 to -59.7 dB.
  - Polarity (AE P-b): the phase-0 check and
    closed_loop.minimum_phase_residual_db score -h at +6.0 dB;
    min(+-ref) scores h and -h the same. Verbatim: "which variant to
    use is not my decision."
  - PENDING: AE + Architect ruling on the report.
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

- **US-177** Web-UI filter panel on 174d coefficient sets (Architect,
  2026-10-26, from the US-174d fallback; P2 PRE-PROD unless the
  Architect or the PO rule otherwise). Scope: deploy via the 174d set
  swap; readback; rollback; versions from MANIFEST/index; refusal of
  3-way profiles. Inherits SecSpec's AC (2) (web-UI deploys only via a
  validated set swap) and the Architect's channel-map rules (ch4 :=
  sub1, shared or inverted per the profile; refuse if unspecified).
  Until it lands, US-174d disables the web-UI /deploy, /rollback,
  /snapshot and /cleanup (409), and venue deploy is the only path.
  Interim detail (Architect, via CM, 2026-10-26): US-174d takes the
  FALLBACK. The 409 responses carry UX text; /active and /versions
  point to "see Venue deploy status". The channel-map rules come from
  the Architect's (a) ruling.
  Cross-ref: the SecSpec gig-blocker "Coefficient sets: single
  validated writer" (and its US-174d write-access note); the P3
  "web-ui PW conf filter_paths point at the output dir".
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
  QE re-confirmation (2026-10-26; cross-ref F-318), verbatim: "F-318:
  add checks.aarch64-linux.wireplumber-no-bypass to ci.yml
  test-and-build. Today that real-PW proof never runs in CI." Same
  item as the CM's 2026-10-25 "Added" line above and the QE's F-318
  condition (2); not US-173 scope; no new entry.
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
- **F-412** (P2; QE, 2026-10-26; from QE-v8-1 in the US-172 v8 verdict
  38663487) The US-172 tryboot kit decides TRYBOOT by absence: in
  waitup an empty or ssh-error probe classifies a boot "NOT-TRYBOOT
  (flag 0, base cmdline)", and return-obs prints "ok normal boot" when
  the cmdline grep fails over SSH; one transient SSH failure in a real
  R5b boot would open R5c/R5d and give a false "R5b failed" bisect
  result. QE P-level, verbatim: "please set P2, due in the next
  revision of the tryboot kit or any reuse of waitup/return-obs. Until
  then, C1/C2 cover it for run 5." Fix (QE recommended, non-blocking):
  waitup requires the four positive lines (retry the probe up to 3
  times, then STOP inconclusive); return-obs tests a fetched,
  non-empty /proc/cmdline rather than the grep exit code; gate c/d
  requires a return-obs file without a STOP whenever the previous step
  was NOT-TRYBOOT or FAIL (i); add a sim flow with an empty probe. Run
  5 cover: binding CM run conditions QE C1/C2 (see US-172).
## P3

- **US-179** Web-only standalone room correction (side quest) (PO,
  2026-10-26; P3 side quest, below US-172, US-173/#63, US-174/F-262
  and US-178; idle worker only, no Pi session of any tier). FILED from
  r8 /tmp/po-drafts/web-rc-story-draft-r8.md (sha256 978c3e1b,
  verified at PM read; PM frozen copy
  /tmp/pm-backlog/US-179-final-r8-978c3e1b.md, same sha256). Released
  by the AE, the Architect and UX, all naming 978c3e1b (PO). r1-r7 are
  void (PO); the PM's frozen r3 copy is history only. Text below is r8
  verbatim, reflowed, without its title and status lines.
  **Owner, verbatim (2026-10-26, via team-lead):**
  - "Here's a side quest while we try to get that sorted. A web only
    standalone version of the room correction. Just using the audio
    hardware in the browser, piggybacking on the UI elements we
    already built."
  - "Or rather, the computation of the correction file, room
    correction itself need not go through the browser. Just the
    measurement and computation."
  - "Yeah, no, we need to support deep bass in the web too. 20Hz is
    fine. ALso, didn't we already settle on a pink noise design? Using
    a predictable RNG per channel?"
  - "We also had the Smaart-alike display off coherence, realtime
    impulse response calculation, etc."
  - On the Architect's noise reconstruction (636a00ec Q2): "I think
    architect assembled those ideas correctly."
  **Priority:** side quest, P3. Below US-172, US-173/#63, US-174/F-262
  and US-178. Idle worker only. No Pi session of any tier.
  **User story:** As the owner, I want to measure a speaker or sub in
  a browser on any computer, with that computer's audio interface and
  a measurement mic, and get correction filter files for the mugge Pi,
  without the Pi, re-using the UI I already know.
  **Use case (PO + AE, settled):** full-range speakers and subs, home
  and PA, one channel at a time, down to 20 Hz.
  **Context (AE):** the browser has none of the Pi's protections (no
  D-063 gate, no D-031 driver HPFs, no D-009 gain staging, no known
  amp or speaker). It can't know the OS volume, interface or amp gain,
  or the speaker's sensitivity and power handling. A digital level is
  not an SPL. Protection comes from the mic, the user's per-channel
  declarations and conservative level limits.
  **Scope (in):**
  - Static web app, no server logic, works offline after loading. No
    dependency on the Pi, GraphManager, signal-gen, pcm-bridge or the
    Pi web UI backend.
  - Audio I/O only via browser APIs: Web Audio output (test noise in
    an AudioWorklet), getUserMedia mic.
  - Computation: the existing Python room-correction code runs in
    Pyodide in a Web Worker (plus a soundfile shim). Shared files are
    byte-identical SOURCE copies of src/room-correction; the build
    copies them and CI checks the hashes. Numbers match the native
    pipeline within tolerance, not bit for bit.
  - Prediction and verdict use room_correction.closed_loop unchanged
    (system_response, passes_residual_gate).
  - UI: reuse unchanged spectrum-renderer.js, pcm-worklet.js, CSS and
    fonts; new thin page and flow controller. The backend-coupled
    wizard/measure/transfer-function scripts are not reused in this
    story.
  - MVP: one channel at a time, one mic position, one output WAV per
    channel (48 kHz, 16384 taps, Pi pipeline WAV format), plus a
    measurement report.
  - Mic calibration file upload (e.g. UMIK-1 .txt).
  **Scope (out, follow-ups below):** the live Smaart-style view and
  the live impulse-response view (US-181, US-182); applying the
  correction in the browser; any audio through the correction (no
  ConvolverNode); loading onto the Pi; multi-way crossovers; several
  positions; time alignment; resampling or other formats; any change
  to src/web-ui, src/room-correction or src/signal-gen; security
  hardening (postponed per owner).
  **Code location and fences (Architect):**
  - New code in src/web-rc/ only; `nix run .#web-rc`.
  - No edits to src/room-correction/**, src/web-ui/** or
    src/signal-gen/**.
  - flake.nix and CI last, in a separate small commit, rebased on
    then-current origin/main.
  - Fresh branch from origin/main; file set disjoint from #63, #66,
    #68.
  - Pyodide vendored for offline use (~20-30 MB).
  - Estimate ~5 worker-days (4 + 1 for the static result views); main
    risk Pyodide packaging.
  **Acceptance criteria:**
  1. **No backend:** opened from static files, the app measures,
  computes and offers the download with the network disconnected after
  loading.
  2. **Audio setup, fail closed (blocking states, no "continue
  anyway"):**
    - 2a The setup step shows "Sample rate: <actual> Hz" for output
      (AudioContext.sampleRate) and input (mic track
      getSettings().sampleRate). If either is not 48000: the step
      stays red, "Start level check" is disabled, text: "Can't
      measure: this audio device runs at <rate> Hz. mugge filters need
      48 kHz. Set the device to 48 kHz in your system's audio
      settings, then reload this page." No resampling.
    - 2b A rate change between captures or on devicechange triggers
      auto-STOP and returns to 2a.
    - 2c echoCancellation, noiseSuppression and autoGainControl must
      read back OFF; otherwise measuring is blocked with a named
      reason.
    - 2d Capture window >= sweep length + 1 s.
  3. **Per-channel speaker declarations (AE R1-R3):**
    - 3a Before any sound on a channel, the user declares its low
      limit: default 20 Hz, range 20-500 Hz, never below 20 Hz.
    - 3b Capability confirmation per channel, e.g. "This speaker can
      safely play down to <limit> Hz at moderate level. I have checked
      its spec sheet or it is a subwoofer." Not ticked = no sound on
      that channel.
    - 3c "Ported (bass reflex) or closed?" If ported and the limit is
      below the port tuning the user enters: a warning and a second,
      separate confirmation. Reason shown in plain words: below its
      tuning a port stops holding the cone back, so the cone moves
      much further and can be damaged.
  4. **Level safety (AE R6; the AE's wording governs):**
    - 4a One-time safety acknowledgement before the first sound: no
      headphones or IEMs; no Bluetooth outputs; amps at a low setting;
      the browser drives the shown output device (setSinkId where
      supported).
    - 4b Level check before every sweep: test noise (AC5) from -60
      dBFS, +6 dB per explicit click only, up to 75 dB SPL at the mic
      (with calibration file) or a fixed mic dBFS target (without;
      visible "uncalibrated" warning). Cap shown. A plain RMS/peak
      meter on the mic input via pcm-worklet.js unchanged (no live TF
      view in this story).
    - 4c Hard digital cap -20 dBFS peak on the actual output, a code
      constant; no UI can raise it.
    - 4d Auto-STOP: mic > 90 dB SPL (calibrated) or mic clip (peak >=
      -1 dBFS); sweep mic level > 6 dB above the level check;
      level-check noise runs 30 s without a user action;
      visibilitychange/pagehide, devicechange, any audio error.
    - 4e STOP button and Esc during the level check and the sweep:
      ramp to 0 in ~10 ms, then the AudioContext is suspended.
    - 4f Mono to ONE selected channel; every other output channel of
      the device is digital zero.
    - 4g Sweep: starts at the declared limit, through a subsonic HPF
      of >= 4th order at 0.8 x the limit (16 Hz for 20 Hz), fade-in
      and fade-out, upper limit 20 kHz, sweep length at most 10 s per
      capture.
    - 4h Output gain starts at 0 and ramps in over about 10 ms. Each
      +6 dB level-check step ramps over about 10 ms; none jumps.
    - 4i After an auto-STOP by the 30 s timeout (4d) or the clamp
      (5d), the level-check step stays open and names the cause, e.g.
      "Level check stopped after 30 s without input. Press Start level
      check to continue." / "Stopped: level cap reached. Lower the amp
      or interface gain, then restart." A restart always begins at -60
      dBFS, never at the last level, and ramps in from 0 per 4h: a
      fresh start, not a resume. Any "+" click counts as user action
      for the 30 s timer (UX note 4de84fe8).
  5. **Test noise (owner-confirmed design, Architect 636a00ec Q2):**
    - 5a Seed per channel: seed = base_seed XOR channel_index (US-121
      scheme); base_seed recorded in the report; channel_index = the
      0-based output channel the noise goes to (0 = left, 1 = right),
      recorded in the report next to base_seed (Architect N1); the
      same noise on every run for a given channel.
    - 5b Generator: the signal-gen generator as reference
      (xoshiro256++, seed_from_u64, pink = Voss-McCartney with 16
      rows), ported to JS in the AudioWorklet. generator.rs operation
      order is kept exactly, including the level step per generator:
      white = f32 cast, then f32 multiply by the level; pink = f64
      multiply by the level, then f32 cast.
    - 5c Golden vectors: the first 4096 samples, white and pink, seeds
      0, 1 and 174, at levels 1.0 and 0.1, produced by the Rust
      generator (generator.rs compiled unchanged) and compared bit for
      bit (f32 bit patterns). Goldens in src/web-rc/fixtures/; no edit
      to src/signal-gen/**. Route (Architect N2): a small Rust tool
      under src/web-rc/golden/ compiles generator.rs unchanged via
      #[path], with rand_xoshiro pinned to signal-gen's lockfile
      version; CI rebuilds the goldens and compares them with the
      committed fixtures.
    - 5d Level-check use (AE R7, O1): pink, band-limited 100 Hz-10 kHz
      (4th-order Butterworth, after the generator), level set from the
      filtered noise's crest factor, measured once over at least 10 s
      of the deterministic stream for the seeds in use, plus a 3 dB
      margin, so its peak stays below the 4c cap. A hard clamp at -20
      dBFS peak is the last stage in the worklet. Any sample that
      reaches it triggers auto-STOP (4e ramp) and the message 'level
      cap reached'. The clamp is a backstop and never runs as a
      distorting limiter. Deep bass is played only by the sweep.
  6. **Filter is cut-only and safe (D-009, AE R5; gates per Architect
  A13):**
    - 6a Correction gain <= 0 dB at every bin; final filter peak <=
      -0.5 dB after trim.
    - 6b The filter contains a subsonic HPF of >= 4th order (the
      shared generate_subsonic_filter, slope >= 24 dB/oct) with its
      corner at 0.8 x the channel's declared limit (16 Hz for 20 Hz),
      and passes verify_mandatory_hpf with that corner (>= 18 dB at
      corner/2 vs passband peak, H1), the same as the Pi, which passes
      mandatory_hpf_hz as the corner.
    - 6c Before any download the bundle runs verify_d009,
      verify_format (16384 taps, 48 kHz), verify_minimum_phase,
      verify_wav_subtype, verify_mandatory_hpf, plus whatever
      F-262/#66 gates are on main at build time, on the downloaded WAV
      bytes (re-read and re-parsed). Any fail = no download, named
      error.
  7. **Captures fail closed (F-262 lessons):** alignment by
  correlation/deconvolution, not timing; a silent pre-capture with an
  SNR check; a mic clip rejects the capture; all thresholds are the
  Python pipeline's constants. A bad capture gives a clear error,
  never "ready".
  8. **Hold-out capture and prediction (AE, REQUIRED):**
    - 8a Two captures at the same position; the filter is built from
      capture 1; the prediction is computed on capture 2; reject if
      the two captures differ by more than 1.0 dB over the correction
      band.
    - 8b The prediction uses the downloaded WAV bytes and closed_loop
      unchanged; the 3 dB residual verdict comes from closed_loop.
    - 8c Label: "Predicted residual within 3 dB: PASS/FAIL —
      predicted, not measured, unverified until re-measured". The
      before curve is labelled "Measured". No ConvolverNode.
  9. **Equivalence with the Pi pipeline:** a CI test feeds the same
  recorded IR through the browser build and the native pipeline;
  filter magnitude within +-0.5 dB over the correction band; the
  browser output also passes run_correction_gate. CI checks the shared
  Python sources are byte-identical to src/room-correction.
  10. **Browser-made files are marked:** "browser-generated" in
  filename and report. Report text: "Filters for the mugge Pi (48
  kHz). Loading onto the Pi is not supported yet. Correction not
  applied or verified acoustically; re-measure after loading them."
  Any later Pi use must pass the Pi's own run_correction_gate and
  D-009 trim (docs).
  11. **UI flow (UX, signed off):** header "Standalone — not connected
  to a mugge Pi"; no deploy, gate or venue elements; steps: setup
  (rates, 48 kHz refusal, speaker declarations) -> safety
  acknowledgement -> level check (level meter, SNR, "+" steps, cap
  shown) -> measure (progress only) -> result -> download. Result step
  (Architect Q4 addendum): measured magnitude (smoothed,
  spectrum-renderer.js), impulse response, delay, a repeatability
  trace (capture 1 minus capture 2 in dB, green where within the AC8a
  1.0 dB limit), and the predicted residual (AC8c). No phase and no
  "coherence" label anywhere in this story (a single sweep can't give
  a true coherence); end state "Filters ready — download";
  beforeunload warning while a measurement or unsaved result exists.
  Hint (AE N1): "Deep-bass correction needs a measurement mic with a
  calibration file."
  12. **Tests:** unit tests for the flow controller and safety logic
  (cap, clamp auto-STOP, ramps, 30 s timeout, 10 s sweep bound,
  auto-STOP triggers, rate refusal, blocked DSP flags, declarations);
  the golden-vector test (5c); an E2E browser test with simulated
  audio (room-simulator IRs, fake media stream); the equivalence test
  (AC9); all in CI.
  13. **Docs (TW):** a short how-to with the safety acknowledgement,
  the per-channel declarations and port warning, and the AC10 Pi-use
  rule.
  **Follow-up stories (PM files with IDs; nothing dropped):**
  - US-180: re-measure after the filters are loaded elsewhere
    (reserved by PM).
  - US-181: browser Smaart-style view: live transfer function, phase
    and coherence during the level check (same AC5 noise, no new
    excitation), plus phase display; transfer_function.py unchanged in
    Pyodide; renderer/transport split of transfer-function.js (route
    b), so it starts after #63/#66/#68 merge. ~3 worker-days. Includes
    a 60 s real-device coherence/clock-drift AC (AE threshold).
  - US-182: live impulse-response view (new feature; browser first, Pi
    later), after US-181. ~1.5 worker-days.
  **Backlog one-liners (PM):**
  - Upload verified correction WAVs to the Pi via Venue: same
    verify.py gates server-side before writing, then select; needs
    SecSpec review (8080 has no auth, F-037).
  - signal-gen and the Python measurement scripts
    (gain_calibration.py, measure_nearfield.py) don't produce
    reproducible noise; consider moving them to the AC5 scheme.
  - D-071: record the per-channel seeded test-noise design (AC5).
  - Other sample rates and export formats.
  Worker-brief attachments (PO; frozen, no story text changes): UX
  release note /tmp/po-drafts/ux-us179-r5-release-note-frozen.txt
  (sha256 4de84fe8, verified at PM read; folded into 4i), and
  Architect note
  /tmp/po-drafts/architect-us179-r7-worker-note-frozen.txt (sha256
  8d89173c, verified at PM read), verbatim: "One note for the worker
  that changes no text: signal-gen's lockfile is the workspace
  src/Cargo.lock, which pins rand_xoshiro 0.7.0." PM cross-ref:
  origin/main src/Cargo.lock has rand_xoshiro version 0.7.0 at PM
  read.
  Brief (PO to the CM, 2026-10-26): an IDLE worker only, on a fresh
  branch from origin/main. Fences: new code only in src/web-rc/; no
  edits to src/room-correction/**, src/web-ui/** or src/signal-gen/**;
  flake.nix and CI last, in a separate commit; file set disjoint from
  #63/#66/#68. No Pi session of any tier; it never pulls anyone off
  US-172, US-173/#63, US-174/F-262 or US-178. Tooling via nix develop
  / nix run, under the disk-hold rules while they are in force.
  ASSIGNED (CM, 2026-10-26): worker-6, branch story/US-179-web-rc from
  origin/main 498fa3e5, worktree .claude/worktrees/story-US-179-web-rc
  (PM cross-ref: branch and worktree at 498fa3e5 at PM read). Fences:
  src/web-rc/ only; flake/CI last, in a separate commit; no Pi. Nix
  cleared for Mac-only builds (87 GiB free); no linux-builder, no GC.
  ERRATUM E1 v2 (PO, 2026-10-26; released by the Architect, UX and the
  AE, per PO): /tmp/po-drafts/us179-r8-erratum-E1-v2.md (sha256
  6a78af9f, verified at PM read; PM frozen copy
  /tmp/pm-backlog/US-179-r8-erratum-E1-v2-6a78af9f.md). E1 732847a4 is
  VOID, and any release of it does not count (PO). r8 (978c3e1b) stays
  the governing text with E1 v2 applied; scope and estimate unchanged
  (PO). Reason, verbatim: "Factual error, found by worker-6 and
  verified by UX and the PO on origin/main:
  src/web-ui/static/js/pcm-worklet.js is a 3-channel PLAYBACK feeder
  (PcmFeeder: a ring buffer fed by postMessage, writing to outputs).
  It does not read the mic and has no RMS/peak code."
  - E1a (AC4b), verbatim: replace the sentence "A plain RMS/peak meter
    on the mic input via pcm-worklet.js unchanged (no live TF view in
    this story)." with: "A plain RMS/peak meter on the mic input: a
    new capture/meter worklet in src/web-rc, styled with the web-ui
    meter CSS unchanged (no live TF view in this story)."
  - E1b (Scope (in), UI bullet), verbatim: replace "reuse unchanged
    spectrum-renderer.js, pcm-worklet.js, CSS and fonts" with: "reuse
    unchanged spectrum-renderer.js, CSS and fonts (pcm-worklet.js is a
    Pi playback feeder and is not reused)"
  - E1c (AC4b, AE wording), verbatim, appended directly after the E1a
    sentence: "The meter computes the true sample peak over every
    sample of every render quantum (no decimation or skipped blocks);
    the 4d mic-clip and 90 dB SPL auto-STOPs are decided on these
    values; AC12 unit-tests both triggers on the meter worklet with
    synthetic input."
  - Architect note (per PO): E1c leaves open whether the STOP decision
    runs in the worklet or on the main thread, as long as it uses the
    worklet's per-quantum true-peak values. The CM freezes a copy and
    relays it to worker-6 (PO).
  AE SIGNAL ANSWERS (AE via CM, 2026-10-26, to worker-6's six
  questions;
  /tmp/cm-relay/US-179/frozen/ae-w6-signal-answers-6d63a2e3.txt,
  sha256 6d63a2e3, verified at PM read; relayed to worker-6 with E1
  v2). PM summary: A1 without a calibration file the fixed target is
  -40 dBFS RMS at the mic (not -30), and the 90 dB SPL stop cannot
  act; A2 ceiling RMS = -20 dBFS - crest_dB - 3 dB, crest measured
  once over at least 10 s per seed, stored as a constant and
  re-checked in CI; A3 the sweep-side mic RMS is full band (declared
  limit to 20 kHz) in 100 ms windows, threshold +6 dB; A4 sweep RMS =
  the confirmed level-check noise RMS, also through the 4c cap and 5d
  clamp; A5 the AC7 onset floor is align_capture as shipped
  (ONSET_SNR_DB 30, from #66), verbatim: "copy room_correction from
  origin/main after #66 merges, or rebase onto it"; REC_MIN_SNR_DB 20
  only as an extra coarse check; dead mic -80 dBFS, clip -1 dBFS; A6
  AC8a uses verify.closed_loop_band(role), not the full band. S1
  (story gap, for the PO): subs become unmeasurable under 100 Hz-10
  kHz level-check noise (safe but blocking). PM cross-ref: A5 makes
  the US-179 shared-file copy depend on the #66 merge;
  closed_loop_band is not on origin/main (verify.py:702 at 4724e65d).
  S1 PO RULING (PO, 2026-10-26;
  /tmp/po-drafts/us179-S1-role-request.txt, sha256 e14a0d75, verified
  at PM read). Verbatim: "The flow gets a per-channel role
  declaration: "Full-range speaker" or "Subwoofer". It is part of the
  AC3 declarations (before any sound), required, with no default (fail
  closed: no role = no sound)." and "Scope stays MVP: no crossover
  design in this story (multi-way crossovers remain out)." Text
  followed as E2 (below).
  ERRATUM E2 (PO, 2026-10-26; released by the AE, UX and the
  Architect, per PO): /tmp/po-drafts/us179-r8-erratum-E2.md (sha256
  bca0d86b, verified at PM read; PM frozen copy
  /tmp/pm-backlog/US-179-r8-erratum-E2-bca0d86b.md). Governing text
  (PO): r8 978c3e1b + E1 v2 6a78af9f + E2 bca0d86b. Scope (out) and
  the estimate are unchanged. E2 verbatim, reflowed, without its title
  line:
  - Story gap S1 (AE 6d63a2e3): r8 has no per-channel role, so the
    level-check band, the AC8a/AC8b bands and the correction reference
    band cannot be chosen, and subs auto-STOP on the +6 dB sweep rule
    (safe but unmeasurable). Inputs: AE 28a48972, UX 9917bceb,
    Architect 7b23fe30 (checked on #66 @ 4724e65d). PO ruling e14a0d75
    stands: required role, no default, no crossover. r8 + E1 v2 stay
    governing, with E2 applied. Scope (out) unchanged; estimate
    unchanged unless worker-6 reports otherwise.
  - E2a (new AC3 item, placed FIRST, before 3a): "3r Role, the first
    declaration per channel (after the output channel is chosen):
    'What is connected to this output?' with two radios, neither
    preselected: 'Full-range speaker — main or monitor speaker that
    plays the whole range' / 'Subwoofer — bass only'. No role = no
    sound on that channel ('Start level check' disabled). Changing the
    role clears the 3b and 3c ticks and resets the limit to the role's
    default. Order per channel: output channel -> role -> low limit
    (3a) -> ported/closed (3c) -> capability confirmation (3b)."
  - E2b (AC3a, replace "default 20 Hz, range 20-500 Hz, never below 20
    Hz." with): "default and range by role: Full-range speaker default
    80 Hz, range 20-500 Hz; Subwoofer default 20 Hz, range 20-50 Hz;
    never below 20 Hz. A Subwoofer limit above 50 Hz is refused with:
    'A subwoofer limit above 50 Hz is not supported here. Check the
    setting, or choose Full-range speaker.'"
  - E2c (AC3b, replace the example text 'e.g. "This speaker can safely
    play down to <limit> Hz at moderate level. I have checked its spec
    sheet or it is a subwoofer."' with): 'by role: Full-range "This
    speaker can safely play down to <limit> Hz at moderate level. I
    have checked its spec sheet." / Subwoofer "This subwoofer can
    safely play down to <limit> Hz at moderate level. I have checked
    its spec sheet."'
  - E2d (AC5d, replace "pink, band-limited 100 Hz-10 kHz (4th-order
    Butterworth, after the generator)," with): "pink, band-limited by
    role (4th-order Butterworth band-pass, after the generator):
    Full-range 100 Hz-10 kHz; Subwoofer [2 x declared limit, 200 Hz]
    (40-200 Hz at 20 Hz). The crest factor is measured per band and
    per seed in use; CI re-checks both bands." The rest of 5d (crest +
    3 dB, -20 dBFS clamp, auto-STOP) and all of AC4 (-60 dBFS start,
    +6 dB clicks, cap, stops, the +6 dB sweep rule) are unchanged. The
    level-check step shows the band in use, e.g. "Test noise: 40–200
    Hz (subwoofer)" / "Test noise: 100 Hz–10 kHz (full-range)".
  - E2e (new AC6 item, role in the computation, Architect): "6d The
    browser builds ONE speaker dict per channel, {'filter_type':
    'highpass'} for Full-range or {'filter_type': 'lowpass'} for
    Subwoofer, and passes that same dict to
    correction_from_measurement and run_correction_gate. A missing
    role is stopped in web-rc before any Python call (the shared
    code's default to 'highpass' is never relied on). No crossover is
    applied: the filter is correction x subsonic HPF (combine_filters
    with a dirac as crossover_filter); the crossover step of
    generate_profile_filters is not run. 'highpass'/'lowpass' are
    internal keys and never shown in the UI. Role -> bands: Full-range
    = AC8a/AC8b band 250-500 Hz, level reference 400-4000 Hz;
    Subwoofer = AC8a/AC8b band 30-200 Hz, level reference 30-150 Hz
    (verify.CLOSED_LOOP_BANDS_HZ / correction.REFERENCE_BANDS_HZ, from
    #66)."
  - E2f (AC8a only; AC9 keeps its own "over the correction band"). In
    8a, replace "reject if the two captures differ by more than 1.0 dB
    over the correction band." with: "reject if the two captures
    differ by more than 1.0 dB over the channel's closed-loop band
    (verify.closed_loop_band of the 6d dict): max absolute difference
    of the two 1/6-octave smoothed magnitudes (AE A6)."
  - E2g (AC9, append): "The Pi reference side calls
    correction_from_measurement + generate_subsonic_filter +
    combine_filters(crossover_filter=dirac,
    margin_db=COMBINE_MARGIN_DB) directly, the same calls web-rc makes
    (generate_profile_filters can't skip its crossover step). No
    change to shared code."
  - E2h (AC10 and AC11, add): "The role is shown next to the channel
    and base_seed in the result step and the report, and is part of
    the download filename next to 'browser-generated' (e.g. '-sub-' /
    '-fullrange-'). The report and the result step name the band the
    AC8c verdict was checked over (e.g. 'checked over 250-500 Hz')."
  - E2i (AC12, add): "unit tests per role for the 3a defaults/ranges,
    the role-change reset, the no-role block, the level-check band and
    its crest constant, and reference_band + closed_loop_band of the
    built dict; an AC9 test asserting no crossover was applied
    (combined FIR = correction x subsonic within tolerance)."
  - E2j (worker note, Architect): this corrects consult r1 9232cfac
    Q2: web-rc mirrors generate_profile_filters steps 2-4 only, not
    step 1 (crossover).
  - Releases needed, each naming this file's sha: AE (E2b, E2c, E2d
    are safety text), UX (E2a-E2c and E2h wording; E2b's refusal text
    is adapted from UX 9917bceb section 5 to the AE's 50 Hz),
    Architect (E2e, E2g, E2i, E2j).
  Architect note (per PO; non-blocking, for worker-6): pin the
  generate_subsonic_filter arguments in one place for both sides; both
  the web-rc side and the AC9 Pi reference pass slope_db_per_oct=24.0,
  because web-rc has no profile; already covered by "the same calls"
  in E2g. The CM freezes a copy and relays E2 plus the note to
  worker-6; the role placeholder can now be replaced (PO).
  US-179 BASE (CM, 2026-10-26; PO informed): the branch stays on main
  and rebases after #66 merges.
  ERRATUM E3 (PO, 2026-10-26; released by the AE, UX and the
  Architect, per PO): /tmp/po-drafts/us179-r8-erratum-E3.md (sha256
  8f508af1, 2186 bytes, verified at PM read; PM frozen copy
  /tmp/pm-backlog/US-179-r8-erratum-E3-8f508af1.md). Verbatim,
  reflowed, without its title line:
  - Source: AE bac898a0 (answer to worker-6's question which value the
    90 dB SPL stop compares against). E1c read as "both stops on true
    peak", but the AE meant "on values the meter itself measured". A
    true-peak 90 dB stop would fire at the 75 dB RMS target on pink
    noise. No safety limit changes (75 dB target, 90 dB value, -1 dBFS
    clip, -20 dBFS cap/clamp unchanged); one backstop is added. r8 +
    E1 v2 + E2 stay governing, with E3 applied. 6a78af9f is not
    edited; E3 replaces its E1c sentence.
  - E3a (AC4b, replace the E1c sentence "The meter computes the true
    sample peak over every sample of every render quantum (no
    decimation or skipped blocks); the 4d mic-clip and 90 dB SPL
    auto-STOPs are decided on these values; AC12 unit-tests both
    triggers on the meter worklet with synthetic input." with):
  - "The meter computes, from every sample of every render quantum (no
    decimation or skipped blocks): the per-quantum true sample peak,
    and a 100 ms sliding RMS over contiguous samples, updated at least
    every quantum. The 4d auto-STOPs are decided on these meter
    values, never on a decimated or display value: mic clip on the
    per-quantum true peak (>= -1 dBFS); 90 dB SPL on the 100 ms RMS
    SPL (the same value the 4b 75 dB target uses); and a backstop at
    per-quantum true-peak SPL > 105 dB SPL. The two SPL stops apply
    only with a calibration file; without one the uncalibrated rules
    (AE A1, -40 dBFS RMS target) apply unchanged."
  - E3b (AC4d, replace "Auto-STOP: mic > 90 dB SPL (calibrated) or mic
    clip (peak >= -1 dBFS);" with):
  - "Auto-STOP: mic > 90 dB SPL as 100 ms RMS, or > 105 dB SPL true
    peak (both calibrated only), or mic clip (true peak >= -1 dBFS);"
  - E3c (AC12, add): "meter tests on the worklet with synthetic input:
    RMS below 90 dB while the peak crosses 90 dB = no stop; RMS
    crossing 90 dB = stop; a single click above 105 dB SPL peak =
    stop; peak >= -1 dBFS = stop."
  - Releases needed, each naming this file's sha: AE (safety text),
    Architect (meter/worklet design), UX (what the user sees on stop;
    no new message text is added, the existing 4i/4d stop texts
    apply).
  ERRATUM E4 r2 (PO, 2026-10-26; released by the AE and UX; the
  Architect has no objection, per PO; E4 7bc8ea34 VOID):
  /tmp/po-drafts/us179-r8-erratum-E4-r2.md (sha256 f692681c, 2737
  bytes, verified at PM read; PM frozen copy
  /tmp/pm-backlog/US-179-r8-erratum-E4-r2-f692681c.md). Verbatim,
  reflowed, without its title line:
  - Replaces E4 7bc8ea34, which is VOID (AE objection 89534d1a).
    Changed from 7bc8ea34: only the mic-clip and 105 dB texts (UX
    f8afd031), the clip-text selection rule, and the clip assertion in
    both modes in E4b. The flow, the 90 dB text and the 'other cause'
    text are unchanged.
  - Source: UX objection 7b3e3849 to E3. r8 4i names texts only for
    the 30 s timeout and the clamp, and 4d names none, so the meter
    stops (mic clip, 90 dB SPL RMS, 105 dB SPL peak) would stop the
    noise with no cause shown. Wording and flow only: no safety limit
    or trigger changes. E4 supersedes E3's closing remark "no new
    message text is added, the existing 4i/4d stop texts apply";
    E3a-E3c are unchanged. 8f508af1 is not edited.
  - E4a (AC4i, replace "After an auto-STOP by the 30 s timeout (4d) or
    the clamp (5d)," with "After any auto-STOP (4d, 5d),"), and add
    after the two existing example texts:
  - "Further example texts per cause:
     - Mic clip, calibration file loaded: 'Stopped: the microphone
     input clipped. Lower the amp or interface output gain, then
     restart. Leave the microphone input gain as it is: the SPL
     calibration depends on it.'
     - Mic clip, no calibration file: 'Stopped: the microphone input
     clipped. Lower the amp or interface output gain, or the
     microphone input gain, then restart.'
     (The mic-clip text is chosen by whether a calibration file is
     loaded at the moment of the stop.)
     - 90 dB SPL (RMS): 'Stopped: too loud at the microphone (over 90
     dB SPL). Lower the amp or interface output gain, then restart.'
     - 105 dB SPL (peak; calibrated only, per E3): 'Stopped: a very
     loud peak at the microphone (over 105 dB SPL). Check that nothing
     touched the mic. Lower the amp or interface output gain, then
     restart.'
     - Any other 4d cause (sweep level rule, page hidden, device
     change, audio error): 'Stopped: <cause in plain words>. Restart
     when ready.'
  - The rest of 4i applies to every cause unchanged: the step stays
    open and names the cause; a restart begins at -60 dBFS and ramps
    in from 0 per 4h (a fresh start). An auto-STOP during the sweep
    returns to the level-check step with the same message, and that
    capture is discarded (AC7: never 'ready')."
  - E4b (AC12, add): "each auto-STOP cause shows its own message (one
    assertion per text; the mic-clip message is asserted both with and
    without a calibration file), and an auto-STOP during the sweep
    returns to the level-check step and discards the capture."
  - Releases needed, each naming this file's sha: UX (wording), AE
    (the stop texts advise gain changes: safety text). Architect:
    no-objection to 7bc8ea34 carries over (flow unchanged); object if
    needed.
  Governing text (PO): r8 978c3e1b + E1 v2 6a78af9f + E2 bca0d86b + E3
  8f508af1 + E4 r2 f692681c. No safety limit changes; scope and
  estimate unchanged (PO). Non-blocking notes for worker-6 (per PO;
  the CM relays them with E3/E4 r2):
  - (UX) On a device or rate change, AC2b ("return to 2a") takes
    precedence over E4's "return to the level-check step". The E4
    "other cause" text is shown.
  - (Architect a) The 100 ms RMS is 4800 samples: use a per-sample
    circular buffer of squares with a running sum and a periodic
    re-sum, and the actual block length, never a hard-coded 128.
  - (Architect b) A meter stop must not depend on the main thread. The
    meter worklet signals the noise-gen worklet directly (a dedicated
    MessagePort or a SharedArrayBuffer flag), which goes silent on the
    next quantum. The main thread is told in parallel, for the message
    and the flow.
  UPDATE (CM, 2026-10-26, after v287): the CM relayed E3
  /tmp/cm-relay/US-179/frozen/us179-r8-erratum-E3-FINAL-8f508af1.md
  and E4 r2
  /tmp/cm-relay/US-179/frozen/us179-r8-erratum-E4-r2-FINAL-f692681c.md
  (sha256 8f508af1 / f692681c, verified at PM read) to worker-6 with
  the three notes above. Base stays on main.
  AE ANSWERS K1-K5 TO WORKER-6 (AE, CM relay, 2026-10-26):
  /tmp/cm-relay/US-179/frozen/ae-w6-cal-mapping-crest-1318b25c.txt
  (sha256 1318b25c, 3073 bytes, verified at PM read). Relayed to
  worker-6; copy to the PO as a possible K3 erratum. Verbatim,
  reflowed, without its title line:
  - Governing text: r8 978c3e1b + E1 v2 6a78af9f + E2 bca0d86b + E3
    8f508af1 + E4 r2 f692681c.
  - K1 Mapping. SPL_dB = dBFS + 120.0 - SensFactor_dB, with SensFactor
    taken from the header ("Sens Factor =X.XXXdB", the same regex as
    test_tool/routes.py _parse_umik1_sensitivity).
     - It applies to RMS (the 90 dB stop and the 75 dB target) and to
     the true peak (the 105 dB backstop) alike.
     - For the house UMIK-1 (7161942, -1.378) this gives 121.378,
     which matches the project constant 121.4
     (configs/hardware/mic-umik1-7161942.yml).
     - Status: consistent with the project constant, but not yet
     cross-checked against a reference (REW or a 94 dB calibrator).
     Safety direction: if the true offset is lower, the meter
     over-reads and the stops fire EARLY (safe, but lower SNR). Use
     exactly this formula; do not "correct" it downward without an AE
     ruling.
     - Clamp: if the parsed SensFactor is outside -6..+6 dB, treat the
     file as uncalibrated, with the visible warning and the A1 rules.
     - No parsable Sens Factor: uncalibrated, as you proposed. Agreed.
  - K2 The frequency-response part of the file is not used by the
    meter. The meter is broadband RMS and peak. The curve is for the
    Python correction only. Agreed.
  - K3 Capture path, a REQUIRED safety condition for "calibrated":
     - getUserMedia with echoCancellation:false,
     noiseSuppression:false, autoGainControl:false.
     - After the stream opens, read track.getSettings(). If any of the
     three is true or missing, the session counts as UNCALIBRATED (A1
     rules, visible warning), whether or not a file is loaded.
     - Browser AGC would silently lower the level and defeat the SPL
     stops. That is the same failure as E4's input-gain case.
     - Test: mock getSettings() with autoGainControl:true, and assert
     uncalibrated mode even with a valid file.
  - K4 UI text with a calibration loaded: "SPL readings assume the
    microphone's input gain is unchanged since its calibration (for a
    UMIK-1: the default input level). Don't change it during this
    session." This is consistent with E4 r2. The exact OS input-level
    setting for the UMIK-1 is not ruled here. Backlog one-liner (via
    the CM to the PM): "US-179 follow-up: cross-check the web meter
    SPL against REW or a calibrator with the UMIK-1 before the first
    amps-on run; define the OS input-level setting."
  - K5 Top step: make it UNIFORM per band. The RMS ceiling for a
    role/band = -20 - max(crest over all seeds of that band's table)
     - 3. The level-check steps (-60, +6) stop at the highest step at
     or below that ceiling.
     - Compute it from your crest table per band; do not assume both
     bands get the same value.
     - This is never above the per-seed ceiling, so it is still safe,
     and it is predictable: same band, same top step on every channel.
     - If -42 is too low to reach 75 dB SPL in a venue, the level
     check reports "target not reached at maximum test level" as it
     already does. It does not get a new step.
  - No safety limit changes.
  PO K3 RULING (PO, CM relay, 2026-10-26; supersedes K3's "counts as
  UNCALIBRATED" above; relayed to worker-6 as a correction to the CM's
  1318b25c summary):
  /tmp/cm-relay/US-179/frozen/po-K3-ruling-e720d78c.txt (sha256
  e720d78c, 1319 bytes, verified at PM read). Verbatim, reflowed,
  without its title line:
  - Governing text: r8 978c3e1b + E1 v2 6a78af9f + E2 bca0d86b + E3
    8f508af1 + E4 r2 f692681c.
  - r8 AC2c already covers K3, and is stricter: "echoCancellation,
    noiseSuppression and autoGainControl must read back OFF; otherwise
    measuring is blocked with a named reason." A flag that reads true,
    or is missing from getSettings(), does not read back OFF, so
    measuring is BLOCKED (no sound at all), calibrated or not.
     - K3's "counts as uncalibrated" is weaker than AC2c and does not
     replace it. AC2c governs. There is no uncalibrated fallback for
     DSP flags that are on or missing.
     - K3's getUserMedia constraints (all three false) are how AC2c is
     met; no text change needed.
     - K3's test is an AC2c test, already in AC12 ("blocked DSP
     flags"): mock getSettings() with autoGainControl:true, and with
     autoGainControl missing; assert measuring is blocked with the
     named reason, also with a valid calibration file loaded.
     - If a target browser can't report these flags at all, that is a
     finding for the PM backlog, not a relaxation of AC2c.
  - K1, K2, K4, K5: worker guidance within the story text; no PO
    action. K4's backlog one-liner goes CM -> PM as the AE asked.
  - AE: object with a file if you need the uncalibrated fallback
    instead of the block.
  FOLLOW-UP (AE K4, via CM; no P-level given), verbatim: "US-179
  follow-up: cross-check the web meter SPL against REW or a calibrator
  with the UMIK-1 before the first amps-on run; define the OS
  input-level setting." Context (CM): the K1 mapping SPL = dBFS + 120
  - SensFactor is not yet reference-checked; its error direction is
  safe. PM cross-ref: not added to the AMPS-ON PRECONDITION LIST (that
  list mirrors safety.md); asked of the AE via the CM whether it
  should be.
  K4 AMPS-ON ANSWER (AE, CM relay, 2026-10-26; closes the PM cross-ref
  above):
  /tmp/cm-relay/US-179/frozen/ae-K4-amps-on-answer-ae0c3e70.txt
  (sha256 ae0c3e70, 960 bytes, verified at PM read). Verbatim,
  reflowed, without its title line ("... does K4 (1318b25c) go on the
  amps-on precondition list? NO."):
  - Reasons:
     - The SPL stops are a backstop. The primary amps-on protections
     for a US-179 run are the -60 dBFS start, the +6 dB steps, the -20
     dBFS clamp with auto-STOP, the 30 s auto-STOP, the ramps and the
     digital-zero channels. None of these depend on SPL calibration.
     - A K1 offset error most likely over-reads, which is the safe
     direction.
     - Under the owner's 2026-10-26 priority, safety.md work is
     paused. A new list row would need a TW batch.
  - Instead: keep it as a US-179 follow-up with a scope line. "Blocks
    the first amps-on US-179 web measurement run that relies on
    calibrated SPL; it does not block other amps-on work." Before that
    run, the AE checks it in the run's go-check. Revisit for safety.md
    when the pre-prod safety-doc work resumes.
  - K3: the PO's e720d78c (AC2c, block with no fallback) is stricter
    than my K3. NO OBJECTION; it governs.
  Team-lead constraint (CM, 2026-10-26; given before the AE answered),
  verbatim: "Either way, the K4 check still has to happen before the
  first amps-on run." With the AE's NO: no amps-on row, no TW work; K4
  stays this scoped US-179 follow-up.
  SUPERSEDED (team-lead, 2026-10-26; applies to the team-lead
  constraint line above): that line was written before the AE answered
  and is broader than the AE's ruling. Team-lead, verbatim: "The AE's
  wording in ae0c3e70 governs. K4 blocks only the first amps-on US-179
  web measurement run that relies on calibrated SPL; other amps-on
  work is not blocked."
  WORKER-6 HEAD (CM, 2026-10-26): 129c031c pushed on
  story/US-179-web-rc (PM read: ls-remote matches): E2, the crest
  table, the E3/E4 r2 meter. Re-sent relays (CM): E3/E4 r2, the base
  ruling, 1318b25c and K3 (see the PROCESS RULE at the top).
  AE FLAGS 2/4 RULING (AE, CM relay, 2026-10-26):
  /tmp/cm-relay/US-179/frozen/ae-w6-flags-2-4-794b1eeb.txt (sha256
  794b1eeb, 917 bytes, verified at PM read). Verbatim, reflowed,
  without its title line:
  - Flag 2, a whole-Hz low limit: ACCEPTED.
     - A 1 Hz granularity is ample for driver limits (20-500 Hz
     full-range, 20-50 Hz sub).
     - The UI must REFUSE a non-integer value, never round it.
     Rounding down would lower the protection corner. UX words the
     text.
     - Test: 40.5 is refused, and 40 is accepted.
  - Flag 4, the HP4 + LP4 cascade for the level-check noise band: NO
    OBJECTION, on one condition.
     - The crest table must be generated with the IDENTICAL cascade as
     the runtime noise: the same order, the same corner frequencies
     and the same coefficient design. A crest computed through a
     different filter would give a wrong RMS ceiling.
     - If the table was generated with a different bandpass design,
     regenerate it.
     - Test: for one band and seed, the JS runtime crest equals the
     table value to within 0.05 dB.
  - No safety limit changes.
  UX WORDING ANSWER (UX, CM relay, 2026-10-26):
  /tmp/cm-relay/US-179/frozen/ux-w6-wording-5eb9829c.md (sha256
  5eb9829c, 2020 bytes, verified at PM read). Status (CM): section 2
  relayed to worker-6; section 1 (new device/rate stop texts) PENDING
  a PO erratum decision and the AE safety question (does a device
  change clear the 4a ack and AC3?). Verbatim, reflowed, without its
  title line:
  - From: ux-specialist, 2026-10-26. Basis: r8 + E1 v2 + E2 + E3 + E4
    r2 (f692681c). Wording only. The PO turns these into story text if
    needed.
  - ## 1. Device change and rate change (AC2b return to setup)
  - No: "Restart when ready." is wrong for these two. The user lands
    back in setup, not in the level check, and has to check something
    first. Use two specific texts instead of the "other cause"
    template:
     - Rate change: 'Stopped: the audio device now runs at <rate> Hz.
     mugge filters need 48 kHz. Set the device back to 48 kHz in your
     system's audio settings, then reload this page.' (Same ending as
     the 2a refusal. The 2a red state then shows as usual.)
     - Device change (connected, removed or switched): 'Stopped: the
     audio devices changed. Check that the right output and microphone
     are selected, then start the level check again.'
  - The message shows at the top of the setup step, above the 2a rate
    line.
  - After either, a level check is a fresh -60 dBFS start (4i).
  - Question for the AE (safety, not a UX ruling): after a device
    change, should the 4a safety acknowledgement and the AC3 channel
    declarations be cleared and re-confirmed? The new output could be
    headphones or a different speaker. UX recommends YES for the
    declarations and the ack.
  - If the AE agrees, append to the device-change text: 'Confirm the
    safety check and the speaker settings again.'
  - ## 2. Whole-Hz low limit
  - The wording is fine with one small change (subject to the AE
    ruling on the restriction itself):
  - 'Enter the low limit as a whole number of Hz between X and Y (e.g.
    40).'
     - X and Y come from the role (E2b): Full-range 20 and 500,
     Subwoofer 20 and 50.
     - A Subwoofer value above 50 shows the E2b refusal text instead
     ('A subwoofer limit above 50 Hz is not supported here. …'), not
     this one.
     - Show the message inline at the field. Never round silently
     (40.5 must not become 40 or 41 without the user entering it). No
     sound until the value is valid.
  AE DEVICE-CHANGE RULING (AE, CM relay, 2026-10-26; answers the UX
  section 1 question above):
  /tmp/cm-relay/US-179/frozen/ae-device-change-reconfirm-20a9bc76.txt
  (sha256 20a9bc76, 1647 bytes, verified at PM read). Status (CM): the
  PO is drafting it as erratum E5, after the final UX text; worker-6
  keeps the E4 r2 text until E5 is final. Verbatim, reflowed, without
  its title line ("US-179 AE ruling on UX 5eb9829c §1 (verified at
  read): what to clear after a device change, 2026-10-26."):
  - YES. After any device change (connected, removed or switched;
    input or output), before any sound:
  - D1 Clear the 4a safety acknowledgement. It must be confirmed
    again.
  - D2 Clear every AC3 channel declaration (role, low limit, channel
    mapping). They must be confirmed again. The new output could be
    headphones or a different speaker, and a stale role or limit would
    apply the wrong HPF and level band.
  - D3 Also: clear the mic calibration binding. A loaded calibration
    file belongs to one microphone. After a device change, the session
    is UNCALIBRATED (A1 rules, visible warning) until the user
    confirms that the file belongs to the selected mic. Re-selecting
    the same file counts. Otherwise a cal file meant for another mic
    would give wrong SPL stops. The input side of the change matters
    just as much as the output side.
  - D4 Discard every level and capture result from before the change.
    The 4i fresh start at -60 dBFS already covers the level check. It
    also covers any sweep level or capture held for the analysis.
  - The UX text line "Confirm the safety check and the speaker
    settings again." is accepted. UX may add the mic-calibration point
    (D3) in its own words.
  - Tests (AC12):
     - after a simulated devicechange, the ack and the declarations
     are empty, and no output is possible until both are confirmed
     again;
     - after a devicechange with a cal file loaded, the session
     reports uncalibrated until it is re-confirmed;
     - an old capture can't be used for the analysis.
  - No safety limit changes. The PO decides on the erratum.
  ERRATUM E5 FINAL (PO, 2026-10-26; supersedes the UX section 1
  PENDING status and "The PO decides on the erratum" above):
  /tmp/po-drafts/us179-r8-erratum-E5.md (sha256 df065993, 3954 bytes,
  verified at PM read); CM frozen copy
  /tmp/cm-relay/US-179/frozen/us179-r8-erratum-E5-FINAL-df065993.md
  (same sha). No safety limit changes; scope and estimate unchanged
  (PO).
  Releases: AE, /tmp/cm-relay/US-179/frozen/ae-E5-release-c56fd763.txt
  (sha256 c56fd763, verified at PM read), "RELEASED (AE safety text
  E5b, E5c; no objection to E5a, E5d)." UX by message, no file (per
  PO), verbatim: "release df065993 (UX). I checked the sha at read
  time. The E5a texts match 5eb9829c §1 and d91ce7c1 §1/§4, the D2/D3
  placement and controls match d91ce7c1 §2-§3, and E5c matches
  5eb9829c §2, all verbatim."
  Governing text (PO): r8 978c3e1b + E1 v2 6a78af9f + E2 bca0d86b + E3
  8f508af1 + E4 r2 f692681c + E5 df065993.
  E5 verbatim, reflowed, without its title line:
  - Sources: UX 5eb9829c (§1 rate text, §2 whole-Hz text), AE 794b1eeb
    (whole-Hz: refuse, never round), AE 20a9bc76 (D1-D4), UX d91ce7c1
    (device-change texts), AE bc0c0127 (Q1 confirm button, Q2 keep
    finished filters). E5 changes released E4 r2 text for two causes:
    rate change and device change no longer use the 'other cause'
    template. No safety limit changes. f692681c is not edited.
  - E5a (AC2b, append): "Both stops show their message at the top of
    the setup step, above the 2a rate line:
     - Rate change: 'Stopped: the audio device now runs at <rate> Hz.
     mugge filters need 48 kHz. Set the device back to 48 kHz in your
     system's audio settings, then reload this page.' (The 2a red
     state then shows as usual.)
     - Device change (connected, removed or switched; input or
     output): 'Stopped: the audio devices changed. Check that the
     right output and microphone are selected. Then confirm the safety
     check, the speaker settings and the microphone calibration again.
     Unfinished measurements were discarded; finished filters can
     still be downloaded.'
  - These two causes do not use the E4 r2 'other cause' text. Any
    later level check is a fresh -60 dBFS start (4i)."
  - E5b (new AC2 item): "2e Device-change reset (AE 20a9bc76,
    bc0c0127). After any device change, before any sound:
     - D1 The 4a safety acknowledgement is cleared and must be
     confirmed again.
     - D2 Every AC3 declaration (role, low limit, ported/closed,
     capability tick, channel mapping) is cleared and must be
     confirmed again. Cleared fields look as on first load (role
     radios unselected, ticks cleared, limit back to the role default
     once a role is picked), with no extra per-field message.
     - D3 The mic-calibration binding is cleared: the session is
     uncalibrated (A1 rules, visible warning) until the user binds a
     file to the selected mic. The calibration field shows an amber
     state: 'Calibration not confirmed for this microphone. A
     calibration file belongs to one microphone. Confirm that <file
     name> belongs to <mic name>, or choose another file. Until then,
     measuring runs uncalibrated.' Controls: [Use <file name> for this
     microphone] (counts as re-selecting the same file) and [Choose
     another file]. The binding is never pre-applied. <mic name> is
     the selected input's device label, or 'the selected microphone'
     if the browser gives none.
     - D4 Every unfinished level-check and capture result from before
     the change is discarded and can't be used for the analysis. A
     finished filter that passed AC6c is kept and downloadable, marked
     per channel 'measured before a device change' in the UI and in
     the download (file name or included metadata). A download set
     mixing pre- and post-change channels shows the mark on each
     pre-change channel; a kept filter is never silently combined with
     post-change results."
  - E5c (AC3a, append): "The low limit is a whole number of Hz. A
    non-integer value is refused, never rounded, with the inline
    message 'Enter the low limit as a whole number of Hz between X and
    Y (e.g. 40).' (X and Y from the role per E2b: Full-range 20 and
    500, Subwoofer 20 and 50). A Subwoofer value above 50 shows the
    E2b refusal text instead. No sound until the value is valid."
  - E5d (AC12, add): "after a simulated devicechange: the 4a ack and
    all AC3 declarations are empty and no output is possible until
    both are confirmed again; with a calibration file loaded the
    session reports uncalibrated until the binding is confirmed; an
    unfinished pre-change capture can't be used for the analysis; a
    finished pre-change filter stays downloadable and carries the
    mark; the rate-change and device-change messages are shown at the
    top of the setup step; 40.5 Hz is refused and 40 Hz accepted."
  - Releases needed, each naming this file's sha: AE (safety text:
    E5b, E5c), UX (wording and placement: E5a-E5c).
  Non-blocking note for worker-6 (AE, via PO): add a test that
  pressing [Use <file name> for this microphone] restores calibrated
  mode. Relay (CM, 2026-10-26): E5 + the AE note relayed to worker-6
  with the ack request; worker-6 replaces the E4 r2 "other cause" text
  for rate and device changes. worker-6 has not yet acked the re-sent
  bundle at this version (ack-by-sha rule running).
  UX RELEASE DETAIL (team-lead, 2026-10-26; refines "UX by message, no
  file (per PO)" above): UX release by message 21:20:58Z, sha
  df065993, relayed by team-lead. Team-lead: the message named the sha
  as checked at read time and confirmed that every UX text matches
  word for word.
  WORKER-6 OPEN POINTS (a), (b), (c) CLOSED (CM, 2026-10-26):
  story/US-179-web-rc pushed at 77ea74e6 (PM read: ls-remote matches).
  worker-6 has acked the governing set by sha (supersedes "has not yet
  acked" above). All four texts below are relayed to worker-6; ack
  pending at this version. Frozen copies in
  /tmp/cm-relay/US-179/frozen/, shas verified at PM read.
  - AE /tmp/cm-relay/US-179/frozen/ae-w6-a-b-cf32c0a6.txt (sha256
    cf32c0a6, 698 bytes), verbatim: "(a) YES, with one condition: the
    capture plays at the last level the check actually reached and
    confirmed, never higher (crest handling as in K1-K5), and every
    stop (90 dB SPL 100 ms RMS, -1 dBFS clip, 105 dB SPL peak
    backstop) stays armed during the capture. A level below target is
    safe; the SNR check failing closed covers quality. (b) YES. Any
    auto-STOP during capture 2 discards both captures; the next
    attempt starts again with a fresh level check (-60 dBFS start,
    4i). FYI on the crest cascade: noted, 1e-9 relative is fine
    (tighter than 0.05 dB)."
  - UX /tmp/cm-relay/US-179/frozen/ux-w6-uncal-measure-436f962f.md
    (sha256 436f962f, 2631 bytes): (c) uncalibrated warning (amber
    banner above the level meter, short form at the calibration field,
    one line in the result step and report; shown whenever
    uncalibrated, not dismissable; meter in dBFS, never "dB SPL") and
    (a) "Measure" stays enabled below the target. Banner, verbatim:
    "UNCALIBRATED — levels are shown in dBFS, not dB SPL. The 90 dB
    and 105 dB SPL safety stops are off; only the clip stop and the
    level cap apply. Keep the amp at a low setting." Result/report,
    verbatim: "Measured uncalibrated: levels in dBFS; the microphone's
    own frequency response is not compensated." (a), verbatim: "Target
    level not reached (<x> of <target>). The measurement may be
    rejected as too noisy." Reason lines and the SNR rejection text:
    verbatim in the file.
  - AE /tmp/cm-relay/US-179/frozen/ae-ux-436f962f-confirm-c5bd03c0.txt
    (sha256 c5bd03c0, 803 bytes; names 436f962f as verified at read):
    "1. CONFIRMED, true and complete." (the banner's safety-stops
    sentence); "2. CONFIRMED." (the not-compensated sentence); "(a) UX
    texts: no objection; consistent with AE cf32c0a6."
  - PO FINAL
    /tmp/cm-relay/US-179/frozen/po-w6-ac-c-ruling-769a5495.txt (sha256
    769a5495, 1925 bytes), verbatim: "No E6. This is worker guidance
    within the story text." Governing chain unchanged (r8 978c3e1b +
    E1 v2 6a78af9f + E2 bca0d86b + E3 8f508af1 + E4 r2 f692681c + E5
    df065993; K3 e720d78c). Binding guidance: (a) as in UX 436f962f
    with the AE cf32c0a6 conditions; "every stop that is active in the
    session stays armed during the capture. Calibrated: all three
    stops. Uncalibrated: the -1 dBFS clip stop, the cap and the clamp.
    The SPL stops don't exist there (E3)." (b) as in AE cf32c0a6. (c)
    as in UX 436f962f verbatim, with the two sentences held for the
    AE's confirmation; PM cross-ref: the AE confirmed both unchanged
    (c5bd03c0), so the UX text stands as written.
  WORKER-6 OPEN QUESTIONS r2 (CM, 2026-10-26; head 77ea74e6): three
  question files frozen in /tmp/cm-relay/US-179/frozen/ (shas verified
  at PM read): w6-open-AE-2f5a24fc.md (2741 bytes),
  w6-open-Arch-22ff06c7.md (2681 bytes), w6-open-UX-c7123b33.md (1076
  bytes).
  - AE: P1 AC8b verdict function: PASS =
    verify.verify_closed_loop(...).passed (passes_residual_gate AND
    corrected max <= uncorrected max, on capture 2), or the residual
    gate alone? worker-6 would keep both. P2/P3 already answered by
    cf32c0a6 / c5bd03c0 (CM). PM cross-ref: P3 also asks whether the
    banner should name "the +6 dB sweep rule"; c5bd03c0 already
    confirmed the sentence "true and complete" (sent to the AE via the
    CM). P4 (information): DSP flags true or missing = BLOCKED (PO
    e720d78c), so the K3 test becomes "Start level check disabled".
    PENDING: AE P1.
  - Architect: Q1 AC9 band; Q2 Arch-b stop mechanism (a shared
    stop-latch.js module in the one AudioWorkletGlobalScope, no SAB,
    no MessagePort; only the main thread re-arms); Q3 calling
    verify_closed_loop directly for the AC8b prediction (reference
    copy 4724e65d).
  - UX: W1 text for "both captures discarded"; W2 progress texts; W3
    the "<x> of <target>" format.
  ARCHITECT ANSWERS r1
  /tmp/cm-relay/US-179/frozen/arch-w6-open-answers-r1-62d25088.txt
  (sha256 62d25088, 3475 bytes, verified at PM read), relayed (CM):
  - Q1, verbatim: "(b) is ACCEPTED, with three precisions." Lower
    edge, verbatim: "max(declared lower limit, 1.5 x the subsonic
    corner)". Upper edge, verbatim: "20 kHz, or 0.95 x Nyquist if that
    is lower." 1/6-oct smoothing on both magnitudes for PASS/FAIL,
    plus the max unsmoothed difference and its frequency, report-only.
    Verbatim: "Do NOT level-align the two filters before comparing."
    The role does not change the band (parity check); a Subwoofer
    filter is compared up to 20 kHz too.
  - Q2, verbatim: "the shared-module latch is ACCEPTED, and no SAB."
    Fail-closed conditions L1-L4: L1 meter heartbeat in the latch, the
    output gives zeros unless it advanced within the last 4 render
    quanta; L2 "rearm" only with a fresh heartbeat, else
    {type:"rearm-refused", reason}; L3 latched = zeros until re-armed,
    hard cut, verbatim: "The AE has the final word on stop behaviour
    (audio safety) and may ask for a short fade."; L4
    OfflineAudioContext tests (no meter node, meter disconnected
    mid-run, rearm with a stale heartbeat refused). PENDING (CM): the
    AE release of L1-L4.
  - Q3: no objection, verbatim conditions: "Build the dict ONCE and
    pass the same object to both. Do not build a second copy." and
    "The direct call is a PREDICTION, report-only." "If the AE names a
    different verdict function, theirs governs." Re-pin from 4724e65d
    and re-run AC9/AC8b when F-383/F-384 land on #66, verbatim:
    "web-rc must follow the merged version."
  UX ANSWERS W1-W3 /tmp/cm-relay/US-179/frozen/ux-w6-W1-W3-82b5b616.md
  (sha256 82b5b616, 1622 bytes, verified at PM read), relayed (CM).
  Wording only, worker guidance.
  - W1 (pending AE P2; PM cross-ref: P2 is already answered by AE
    cf32c0a6, "discards both captures"), verbatim: "Both captures were
    discarded: the two captures must be taken back to back. Press
    Start level check to measure again." Shown below the E4 stop text,
    in the same message box.
  - W2, verbatim: "Capture 1 of 2: playing sweep…", "Capture 2 of 2:
    playing sweep… Keep the microphone where it is.", "Computing the
    filter… This can take up to a minute the first time." (time
    adjusted to the measured value), "Checking the filter…" if visibly
    separate. STOP/Esc stays visible during both captures (4e); during
    computing and checking STOP can be hidden or replaced by "Cancel".
  - W3 (changes the 436f962f (a) format above), verbatim: "Target
    level not reached: -47 dBFS (target -40 dBFS)." / "Target level
    not reached: 68 dB SPL (target 75 dB SPL)." Whole dB rounded DOWN
    (floor) while the target isn't reached. The rest of the 436f962f
    (a) text is unchanged.
- **US-180** Re-measure after the US-179 filters are loaded elsewhere
  (PO, 2026-10-26; P3, follow-up of US-179, from r8 "Follow-up
  stories", verbatim: "re-measure after the filters are loaded
  elsewhere (reserved by PM)"). Reserved in v275; filed now. No ACs
  yet.
- **US-181** Browser Smaart-style view (PO, 2026-10-26; P3, follow-up
  of US-179; starts after #63/#66/#68 merge). r8, verbatim: "browser
  Smaart-style view: live transfer function, phase and coherence
  during the level check (same AC5 noise, no new excitation), plus
  phase display; transfer_function.py unchanged in Pyodide;
  renderer/transport split of transfer-function.js (route b), so it
  starts after #63/#66/#68 merge. ~3 worker-days. Includes a 60 s
  real-device coherence/clock-drift AC (AE threshold)." The AE
  threshold is not yet given.
- **US-182** Live impulse-response view (PO, 2026-10-26; P3, after
  US-181). r8, verbatim: "live impulse-response view (new feature;
  browser first, Pi later), after US-181. ~1.5 worker-days."
- **Upload verified correction WAVs to the Pi via Venue** (PO
  one-liner from US-179 r8, 2026-10-26; no P-level given), verbatim:
  "Upload verified correction WAVs to the Pi via Venue: same verify.py
  gates server-side before writing, then select; needs SecSpec review
  (8080 has no auth, F-037)."
- **Reproducible test noise in signal-gen and the Python measurement
  scripts** (PO one-liner from US-179 r8, 2026-10-26; no P-level
  given), verbatim: "signal-gen and the Python measurement scripts
  (gain_calibration.py, measure_nearfield.py) don't produce
  reproducible noise; consider moving them to the AC5 scheme."
- **D-071: record the seeded test-noise design** (PO one-liner from
  US-179 r8, 2026-10-26; no P-level given), verbatim: "D-071: record
  the per-channel seeded test-noise design (AC5)." D-071 allocated by
  the PM (see Reserved IDs); no writer named yet.
- **Other sample rates and export formats for US-179** (PO one-liner
  from US-179 r8, 2026-10-26; no P-level given), verbatim: "Other
  sample rates and export formats."
- **Measurement session ignores PI4AUDIO_SPEAKERS_DIR** (Architect via
  CM, 2026-10-26; non-blocking, from the F-262 cd1f63e7 release; no
  P-level given), verbatim: "session.py _profile_dirs (:58) always
  uses repo configs/speakers and ignores PI4AUDIO_SPEAKERS_DIR, which
  speaker_routes._speakers_dir honours. On the Pi the UI's profile
  list and filter generation can therefore read different profiles."
  PM cross-ref: src/web-ui/app/measurement/session.py at 4724e65d,
  _profile_dirs at l.54, the configs/speakers join at l.58;
  speaker_routes.py l.41 and filter_routes.py l.41 read
  PI4AUDIO_SPEAKERS_DIR (default /etc/pi4audio/speakers).
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
  WITHDRAWN (AE, 2026-10-26): US-173's F-318 hook
  (mugge-no-bypass.lua) already denies every playback auto-link and
  the convolver is never the default sink, so the premise is gone.
- **F-318 blocked-stream notice** (UX, 2026-10-26; P3, owner UX;
  non-blocking for US-173 and US-174d; from the Architect/AE/UX
  default-output ruling, F-318 option A), verbatim: "**F-318
  blocked-stream notice:** the web UI shows a neutral info line,
  'Audio from <app> blocked (not routed to PA)', deduplicated per app
  with a count and the last time seen, and dismissable. Clicking it
  opens a short explanation: use Mixxx/Reaper, use the signal-gen for
  a speaker test, never link by hand. There is no allow button, no
  modal and no red styling. The source is the existing 'F-318: denied
  auto-link' journal line, surfaced via GM or the web UI. It is
  distinct from the red routing-audit indicator, which is already in
  the backlog and fires only for an actual non-convolver link to
  USBStreamer playback."
  Amendment (UX, after Architect input, 2026-10-26): the notice needs
  a source for BOTH block paths: (a) WirePlumber auto-link denials,
  from the existing "F-318: denied auto-link" journal line; (b) JACK
  self-connect refusals (US-173 jack.self-connect-mode), which have no
  GM-visible event yet, so a source has to be defined (Architect).
  Until (b) has a source, the notice covers (a) only, and its
  explanation must not claim to cover every blocked stream.
  Note (PM, from the US-173 joint ruling, 2026-10-26): with
  self-connect-mode = ignore-external, a refused jack_connect returns
  0 and creates no link, so there is no event to surface; source (b)
  is still to be defined (Architect).
- **deploy.sh puts the JACK fragment in the wrong directory**
  (Architect, 2026-10-26; P3): scripts/deploy/deploy.sh:80 copies
  80-jack-no-autoconnect.conf into
  ~/.config/pipewire/pipewire.conf.d/, but it is a jack.conf.d
  fragment; Nix (pipewire.nix:42) installs it correctly. If deploy.sh
  is still used anywhere, it silently drops rt.prio 70,
  autoconnect=false and US-173's new self-connect-mode. Fix: correct
  the path or retire the legacy script.
- **D-031 exception as a structured field** (AE, via CM, 2026-10-26;
  P3, owner AE), verbatim: "Replace the D-031 null-HPF exception
  comment parse with a structured identity field (e.g.
  `d031_exception: <reason>`). Schema change; needs the owner's file.
  Source: AE ruling on verify_d031_protection, 2026-10-26."
- **web-ui PW conf filter_paths point at the output dir** (worker-4,
  via CM, 2026-10-26; P3; cross-ref US-174d, and US-174c, which owns
  session.py, L-046), verbatim: "web-ui filter_routes:307 and
  session.py:1131 generate the PW conf with filter_paths pointing at
  the output dir instead of coeffs/. Source: worker-4, US-174d
  read-only finding, 2026-10-26."
- **JACK fragment sort order** (QE nit via CM, 2026-10-26; P3,
  non-blocking; the Architect decides): the jack fragment is installed
  as `<storehash>-80-jack-no-autoconnect.conf`, so the store hash, not
  "80-", sets its sort order in jack.conf.d, and a later override
  fragment could sort before it. Should it get a fixed name?
  Cross-ref: US-173 self-connect-mode; the P3 deploy.sh JACK fragment
  path.
  SUPERSEDED (Architect, 2026-10-26): upgraded to F-400, which covers
  all four conf.d fragments; fixed on #63 (see US-173).
- **No fallback login on tty1 without DRM** (UX via CM, 2026-10-26;
  P3): greetd conflicts with getty@tty1, so when there is no /dev/dri
  (US-172 run 3) the console offers no login at all.
  Merged (QE via CM, 2026-10-26), same issue, verbatim: "Provide a
  tty1 getty fallback when greetd's /dev/dri condition is unmet (UX
  and recovery)".
  Merged (Architect via CM, 2026-10-26; a US-172 fix design point),
  same issue: if greetd's /dev/dri condition fails, tty1 falls back to
  a getty.
  Also reported by worker-2 (via CM, 2026-10-26): with no /dev/dri,
  greetd is skipped and getty@tty1 conflicts with it, so tty1 has no
  login. Same item.
- **Pi 5 WiFi firmware missing** (CM, 2026-10-26; P3, cosmetic unless
  WiFi is wanted): brcmfmac43455 firmware and regulatory.db are not
  installed, which gives an "HT Avail" timeout at boot.
  Architect (2026-10-26): unrelated noise, low priority. CM note: the
  photo shows the HT Avail timeout line, which is what "bcmrf" was.
  QE (via CM, 2026-10-26): no action unless WiFi is wanted.
- **Bluetooth enabled on the Pi 5** (Architect, 2026-10-26; no
  priority given; SecSpec informed): disable-bt-pi5 was never applied,
  for the same reason as the US-172 overlays. It is fixed together
  with the overlay fix.
  Merged (AE via CM, 2026-10-26; pre-prod): apply disable-bt-pi5 or
  turn off WirePlumber's bluez monitor, so that no BT audio sink can
  ever appear.
  SecSpec (via team-lead, 2026-10-26; held back during quiet mode):
  Bluetooth must be confirmed off before gigs, because at a venue it
  is a radio open to anyone in range. SecSpec will check at the US-172
  PR review that the post-deploy check confirms disable-bt-pi5
  actually applied.
  Cross-ref (PM dedup, 2026-10-26): duplicate of the earlier P3
  one-liner "Bluetooth stays active on the Pi 5" (SecSpec, PO), which
  is the original.
- **PW main-thread latency under DJ load** (Architect, from the AE,
  2026-10-26; not a gate, no priority given; cross-ref F-358): measure
  GM link-change and gate-param latency under full DJ load on the Pi
  5. PW's main thread runs SCHED_OTHER at nice 0 (F-358 skips the nice
  step because RLIMIT_NICE is 0), so it competes with Mixxx's non-RT
  threads. If it is too slow, the option is LimitNICE for user@1000,
  so PW's stock nice -11 applies; that needs a separate ruling.
- **F-401** Whole test module silently skipped (worker-4 via CM,
  2026-10-26; no priority given): tests/unit/test_filter_routes.py has
  been skipped as a whole module since e5ed2cea. A `try: import ...
  _PROFILES_DIR except ImportError: pytest.skip(...)` guard hid an
  import of a name that no longer exists. Fixed on US-174d by removing
  the guard. Other modules may use the same skip pattern; unchecked.
  Suggested: a QE sweep.
  WITHDRAWN (PM, 2026-10-26): duplicate of F-362 (same guard, same
  module, same `_PROFILES_DIR` cause). The ID F-401 is retired, not
  reused; all F-401 content and the QE sweep are recorded under F-362.
- **testing-process.md:324 stale** (TW via CM, 2026-10-26): it still
  says "/deploy returns 200". The TW is deciding where to fix it.
  UPDATE (TW via CM, 2026-10-26): goes in the TW's 174d batch, written
  against worker-4's code; nothing for the PM to mirror.
- **Rust tests recompile on every CI run** (Architect, 2026-10-26; P3,
  CI speed; the owner asked about the build cache, and cachix works):
  test-all runs cargo test outside Nix with CARGO_TARGET_DIR in $HOME,
  so the Rust workspace and GM recompile on every CI run (6-11 min).
  Make them Nix checks (cachix-cached) or add actions/cache for the
  cargo target. Cross-ref: P3 AD L3 (`cachix watch-exec` pushes the
  full tracked tree into mugge.cachix); F-380 (ARM wall time of one
  test file) is separate.
- **E2E local-demo step takes about 22 min every run** (Architect,
  2026-10-26; P3, CI speed): profile it and shard it into parallel CI
  jobs.
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
  SUPERSEDED (PM dedup, 2026-10-26): the same issue is now F-400 (all
  four conf.d fragments; fixed on #63, see US-173).
- Bluetooth stays active on the Pi 5 (disable-bt-pi5 not applied; BT
  on serial@7d50c000). No hardware.bluetooth, no bluetoothd. LOW,
  home lab, no owner question now; fix with US-172. (SecSpec, PO)
  Cross-ref (PM dedup, 2026-10-26): the later P3 item "Bluetooth
  enabled on the Pi 5" (v197-v199) is the same issue; this item is the
  original. The later item's additions (AE pre-prod point, SecSpec
  pre-gig check) stand.
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
- **F-413** (worker-2 via CM, 2026-10-26; no P-level given, listed
  under P3 until ruled; was US-172c one-liner (a)) us172-recovery.sh
  step 2/2b: the old-boot-id check matches the id with surrounding
  spaces while the id list has one id per line, so it falsely reports
  "old boot id not in journal" (rec-2 INCONCLUSIVE, 2b empty). Fix
  (worker-2): match whole lines (grep -qx). A fix means a new sha and
  re-review (CM, earlier one-liner). Source: 49ab9ebb item 1.
  P3 (Architect by message, via CM, 2026-10-26; replaces "no P-level
  given"). Not a run-5 blocker: the v8 kit already matches boot ids by
  whole line (awk).
- **F-414** (worker-2 via CM, 2026-10-26; no P-level given, listed
  under P3 until ruled; was US-172c one-liner (b)) us172-recovery.sh
  step 4: `ls /sys/fs/pstore` needs sudo (Permission denied as ela),
  so pstore was never read after the hang. Source: 49ab9ebb item 2. PM
  cross-ref (PM read of the v8 kit files, shas d23d752b / 5100d29f
  verified): us172.sh:442 reads pstore with `sudo -n ls -la
  /sys/fs/pstore`, but us172-drm-reads.sh:40 (the $TAG-pstore data
  read, "data only") runs `ls -la /sys/fs/pstore 2>&1` without sudo,
  so that read will likely show Permission denied as ela. Not a run-5
  safety item (OBSERVE data only); sent to the CM for worker-2 and the
  Architect.
  P3 (Architect by message, via CM, 2026-10-26; replaces "no P-level
  given"). Architect ruling, verbatim: "US-172 v8: I agree on both
  items. (1) No kit change for run 5: the pstore data that matters
  comes from return-obs (us172.sh:442 uses sudo -n, I checked), and
  the tb-post pstore line is data only. (2) F-413, F-414 and F-415 are
  all P3, as filed. None of them blocks run 5: the v8 kit already
  matches boot ids by whole line (awk) and dates boots by
  /proc/uptime."
- **F-415** (worker-2 via CM, 2026-10-26; no P-level given, listed
  under P3 until ruled) Boot timelines on the Pi 5 (no RTC): tooling
  and reports must date boots by /proc/uptime or the first NTP sync,
  never by journal wall-clock or `uptime` "up HH:MM" (the run-2 "came
  back in ~40 s" misreading). Source: 49ab9ebb item 5. Related: the
  Architect's RULED note under US-172 ("a no-RTC timestamp artifact").
  P3 (Architect by message, via CM, 2026-10-26; replaces "no P-level
  given"). Not a run-5 blocker: the v8 kit already dates boots by
  /proc/uptime.

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
