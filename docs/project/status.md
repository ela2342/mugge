# Project Status

Last updated: 2026-10-24 (session 15, tracking re-sync by PM). Before this,
the file was last updated on 2026-04-04 (session 9). Story, defect and
decision details are in the `stories/`, `defects/` and `decisions/`
directories. Their index files are generated from the per-item files
(see F-297: do NOT run `scripts/split-monoliths.py`).

> **Re-sync caveats (2026-10-24).**
> - PR state is **UNVERIFIED**. `gh` is unauthenticated for github.com, so
>   PR merges are known only from merge commits on main. Rule 13 approvals
>   and owner acceptance for PRs #2–#35 are **not recorded** in tracking.
> - `c34f7da7` and `991ff456` (2026-04-19) are single-parent commits on
>   origin/main with no PR number, so PR status is unknown. If they were
>   direct pushes, Rule 13 was bypassed.
> - Local main has an unpushed commit `95306f66` (PreCompact hook schema
>   fix, 2026-10-24) made directly on main without a PR. It is waiting
>   for an owner decision.
> - No commits between 2026-04-19 and 2026-10-24. The state of the Pi
>   after April is unknown.

## Current Mission

**D-040: Pure PipeWire filter-chain pipeline (CamillaDSP abandoned).**
PipeWire 1.6.2 is on main (US-128, PR #2). Pi deployment of 1.6.2 is not
recorded.

Session 15 focus, pending owner direction:
1. **Safety: F-314 (CRITICAL)** — venue switch with gate open applies
   +60/+64 dB instantly. Escalated to owner. Interim rule: never change venue
   with the gate open. AE veto on gate/venue/first-boot PRs until fixed.
2. Reconcile tracking with 6 months of history (this update).
3. Test integrity and xfail budget (6 active, limit 5). Work order below.
4. Retroactive review/acceptance of work that landed without a recorded
   review: PRs #2–#35, plus `991ff456` and `c34f7da7` (AE, security in
   progress).

### Proposed work order (2026-10-24; worker spawning is the owner's call)

1. **F-314** (critical safety; fix in GM, architect picks mechanism). Note
   it touches gate/venue logic, so it must carry **F-298 Part A** with it
   or follow it (AE merge condition).
2. **F-298 Part A** (A1–A7) — D-063 gate test integrity. Unblocks US-113
   and US-151 acceptance. A7 replaces the orphaned conf test (F-313).
3. **F-315** (gate ramp is a step) — gate logic, after F-298 Part A.
4. **F-290** (xfail → budget back to 5).
5. **F-296** (stimulus fixture; unblocks F-298 Part B, F-301-adjacent work).
6. **F-262 diagnosis** (AE + architect spec; covers F-299, F-308).
7. **F-298 Part B**.
8. **F-312** (REQUIRE_STACK guard) + **F-301/F-302** (high skip defects),
   then F-303–F-311, then **US-157** lint. F-313 orphan wiring alongside.
9. Pi evidence via CM sessions (amps OFF): **F-318** (WP auto-link), F-316
   boot check, F-319 level-bridge, F-317 watchdog.

## Active Work

| Story | Phase | Summary | Blocker / next step |
|-------|-------|---------|---------------------|
| US-113 | REVIEW | First-boot active config + FoH passthrough | PR #22 merged 2026-04-06. Approvals/acceptance unrecorded. Real-stack E2E (L-QE-002) + F-271 open. |
| US-120 | REVIEW | Real-time transfer function measurement | PR #11 merged 2026-04-05. Approvals/acceptance unrecorded. |
| US-128 | REVIEW | Upgrade PipeWire to 1.6.2 | PR #2 merged 2026-04-04. Pi deploy + acceptance unrecorded. US-112 patch regen status unknown. |
| US-131 | REVIEW | Parallel local-demo instances | PR #13 merged 2026-04-05. Approvals/acceptance unrecorded. |
| US-140 | REVIEW | Deterministic reconciler settlement | PR #27 merged 2026-04-06. Approvals/acceptance unrecorded. |
| US-142, 143, 145, 147, 148, 149 | TEST | Browser E2E stories | Tests exist but skip if stack down. Accept after F-312 + CI log showing passed (QE). |
| US-144, 146, 150, 151 | TEST (blocked) | Mute / venue-gate / banner / gate-closed E2E | Blocked by F-302, F-305, F-305, F-298 Part A. |
| US-152, US-153 | IMPLEMENT (not started) | Watchdog latch E2E; D-009 ceiling E2E | No test exists (QE). |
| US-154 | IMPLEMENT (partial) | Reclassify mislabeled E2E tests | F-284 moved files; 34 API-only tests remain in e2e/ (calibration, hardware). |
| US-155 | in-review (retroactive) | Markaudio CHN-50P + Ultimax venue config | Story/AC by PO. AE review in progress. AC3 needs owner decision (sub D-031 exception). |
| US-156 | in-review (retroactive) | Static route Pi → lab VM subnet | Story/AC by PO. Security: LOW, move to dev-only module (F-316). |
| US-157 | draft | Test anti-pattern AST lint | After F-298/F-301/F-303–F-310. PO to review AC. |
| US-158 | draft | Live-mode mic input capture | F-295 follow-up; PO recommends high. Owner to confirm. |
| US-132 | draft (epic) | Network management | DRIFT: release workflow committed without decomposition (`5279649e`, `26d77f2c`). |
| US-072 | IMPLEMENT (HW validated) | NixOS reproducible build | Unchanged since session 9. |
| US-112 | REVIEW (Rule 13 passed) | PW convolver hot-reload patch | AD-R13-003/004 open. Patch regen for PW 1.6.2 status unknown. |
| US-115 | IMPLEMENT (Phase 0 done) | 8ch filter-chain convolver (D-063) | Story file still says `ready`, which is inconsistent. |
| US-123 | IMPLEMENT (done) | GM deterministic boot state | Story file still says `draft`, which is inconsistent. |
| US-125 | IMPLEMENT | Explicit mode arming | Session 9 worker state unknown. Story file says `draft`. |
| US-126 | IMPLEMENT (Rule 13 conditional) | Persistent audio gate banner | QE conditions open. Story file says `draft`. |
| US-114 | TEST (Pi validated) | Minimal kernel config | AC #6, #7, #9 open. |
| US-119 | IMPLEMENT (partial) | Image size tier 3 | Story file says `draft`. |
| US-098 | TEST | Room correction pipeline verification | P1/P2 41/41 pass (session 9). |
| US-090, US-092–US-097 | REVIEW (Gate 3) | Seven web UI stories | Awaiting owner re-acceptance (since session 9). |
| US-088 | REVIEW | Direct WS from Rust | Owner Pi session. |
| US-089 | TEST | Speaker config management | Blocked by F-198. |
| US-091 | IMPLEMENT | Multi-way crossover | F-188–F-191 open. |
| US-077 | TEST 6/9 | Single-clock timestamp arch | DoD #4 Pi perf. |
| US-070 | TEST 3/7 | GitHub Actions CI | CI restructured since (PRs #9, #20; 4d0ae4db, 91cecd88). DoD needs re-check. |
| US-044 | IMPLEMENT/TEST | Safety protection suite | AC #1-2/6-8 need Pi. |
| US-071 | REVIEW | SETUP-MANUAL doc quality | Gate 3 failed: prose rewrite. |
| US-084 | IMPLEMENT 10/13 | Level-bridge extraction | Pi systemd + acceptance. |
| US-079–US-082 | IMPLEMENT | Capture point, spectrum, meters, playback | Owner re-validation. |
| US-110 | IMPLEMENT | Web UI passkey auth (F-037) | 17 tasks; progress since session 4 unknown. |
| US-111 | IMPLEMENT 8/13 | Local-demo topology redesign | AC #8, #9 open. |

**Known tracking inconsistency:** several story files (US-115, US-119,
US-123, US-125, US-126) carry older statuses than this table, which
reflects the session 9 status.md. Each story owner must confirm before
the files are changed.

### Owner-Blocking Items

| Item | Blocked on |
|------|-----------|
| `95306f66` unpushed direct-to-main commit | Owner decision: push, PR, or drop |
| `gh` authentication for github.com | Owner re-auth (blocks PR verification + opening PRs) |
| Retroactive Rule 13 / acceptance for PRs #2–#35, `991ff456`, `c34f7da7` | Owner to decide scope (accept as-is vs retroactive review) |
| D-065 (reconstructed) | Owner confirms the decision was taken. Security: HIGH residual risk (F-318) pending Pi evidence |
| **F-314 hot venue switch (CRITICAL)** | Escalated by AE; owner to prioritise fix. Interim: never change venue with gate open |
| HP/IEM chain (ch 5-8, unity gain) | Owner decision after measurement: per-channel soft cap or limiter (AE). Interim procedural rules in safety.md (TW) |
| US-155 AC3 sub D-031 exception | Owner confirms "owner directive" (then file decision) or require subsonic HPF |
| US-158 priority | Owner confirms intent/priority (PO recommends high) |
| US-090/092–097 re-acceptance | Owner (pending since session 9) |
| US-088, US-084, US-044, US-077, US-063 Pi work | Owner Pi session |
| US-079–082 re-validation | Owner local-demo test |
| US-089 acceptance | Owner prioritization + Pi deploy |
| US-099–104 (venue workflow) | Owner prioritization |

## Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| PW filter-chain config | deployed (as of April) | 8ch FIR convolver + gain nodes (D-063) |
| GraphManager | deployed (as of April) | Link topology + mode transitions (port 4002). Reconciler settlement (US-140) on main. F-293 seccomp change on main. |
| signal-gen | deployed (as of April) | RT measurement audio (port 4001) |
| pcm-bridge | deployed (as of April) | Lock-free level metering (port 9100) |
| Web UI platform | Stage 1+2 deployed | Dashboard, spectrum, config tab, graph viz, TF tab (US-120). HTTPS (D-032). No auth (F-037). |
| Room correction pipeline | done (TK-071) | 13 DSP modules. F-262 may indicate a min-phase filter-gen bug (under diagnosis). |
| SETUP-MANUAL.md | draft | Gate 3 prose rewrite pending |
| Core software | on main | **PipeWire 1.6.2** (US-128), Mixxx 2.5.0, Reaper 7.64, wayvnc. Pi deployment of 1.6.2 unrecorded. |
| RT tuning | on main (`991ff456`) | RT throttle off, performance governor, PW FIFO/88 via unit (F-291), JACK clients FIFO/70 (F-295). Pi verification unrecorded. |
| WirePlumber | on main (`991ff456`) | 90-no-auto-link.conf removed (D-065, F-292). |
| Platform security | partial | Firewall active, SSH hardened. Web UI auth: US-110. New static route (US-156) unreviewed. |
| GitHub Actions CI | merged | Restructured 2026-04-04/05: 2-job ARM pipeline, Cachix, PR-only trigger, paths filter (PR #9), tag release workflow (US-132). |
| NixOS build (US-072) | HW validated on test Pi | Unchanged since session 9. |

## Completed Stories

| Story | Summary | Accepted |
|-------|---------|----------|
| US-000 | Core audio software installation | 2026-03-22 |
| US-000a | Platform security hardening | 2026-03-21 |
| US-000b | Desktop trimming for headless | 2026-03-22 |
| US-001 | CamillaDSP CPU benchmark | 2026-03-22 |
| US-002 | Latency measurement | 2026-03-22 |
| US-004 | Assumption register (A1-A28) | 2026-03-21 |
| US-005 | Hercules DJ controller | 2026-03-12 |
| US-006 | Mixxx feasibility | 2026-03-12 |
| US-058 | PW filter-chain benchmark (BM-2) — triggered D-040 | 2026-03-16 |
| US-059 | GraphManager core + production filter-chain | 2026-03-21 |
| US-062 | Boot-to-DJ mode | 2026-03-20 |
| US-076 | Web UI visual polish | 2026-03-25 |
| US-109 | Playwright MCP integration | 2026-03-29 |

## Deferred / Cancelled

| Story | Reason |
|-------|--------|
| US-003 | Deferred: T3d/T4 pending, owner deselected for Tier 11 |
| US-028 | Cancelled: D-040 eliminated ALSA Loopback |
| US-056 | Cancelled: D-040, CamillaDSP abandoned |
| US-057 | Cancelled: D-040, CamillaDSP abandoned |

## Open Blockers

| ID | Severity | Summary |
|----|----------|---------|
| **F-314** | **Critical** | Venue switch with gate open: instant +60/+64 dB, no ramp/confirmation. Exists on main (US-113). AE veto on gate/venue/first-boot PRs. |
| F-187 | Critical | Noise on 4 channels + broken spectrum after multiple PW restarts. Blocked — needs Pi at venue. |
| F-271 | High | D-031 protection WAVs for ch 1-4 missing (blocks US-113 acceptance). |
| F-298 | High | D-063 gate-closed test cannot fail. Part A is AE merge condition; blocks US-113/US-151 acceptance. |
| F-318 | High | Since D-065, non-JACK streams may auto-link straight to USBStreamer (security). Needs Pi evidence. |
| F-313 | High | Orphaned test suites; one contradicts D-063. Architect ruling: wire/migrate/port. |
| F-312 | High | No central REQUIRE_STACK guard; CI can go green with stack down. |
| F-301, F-302 | High | Skips swallow D-009 / mute failures. |
| F-287 | High | Fixed by PR #32. Two gaps before VERIFIED (node name ruling, pinning test). |
| F-291 | High (reconstructed) | PW RT throttle / FIFO not applied. Fixed on main (`991ff456`), Pi verification unrecorded. Claimed security approval NOT confirmed; retroactive review: LOW + F-317. |
| F-292 | High (reconstructed) | WP policy.standard=disabled broke node activation. Fixed via D-065, Pi verification unrecorded. |
| F-315 | Medium | D-063 gate-open ramp collapses to an instant step. |
| F-317 | Medium | RT throttle off with no configured watchdog. Fix before next gig. |
| F-299 | Medium | D-009 not guaranteed between bins / below 20 Hz (generator + verifier). Joint fix with F-262. |
| F-303–F-311 | Medium | Skip-audit groups and dead skip guards. |
| F-262 | Medium | 2 xfails. Possible real min-phase filter-gen bug (architect ruling). Highest product risk among the xfails. |
| F-296 | Medium | No audio stimulus in local-demo; 3 xfails misattributed to F-270. |
| F-297 | Medium | `split-monoliths.py` would overwrite newer tracking files. Do not run. |
| F-272 | Medium | RESOLVED (PRs #27, #34). VERIFIED pending CI log. |
| F-290 | Low | Test assertion bug, xfail still present (architect priority 1). |
| F-037 | High | Web UI no auth — converted to US-110 (ready, blocked on D-060 implementation) |
| F-222 | High | Zombie process accumulation in container dev environment (PID 1 = sleep infinity) |
| F-244 | High | All entity DELETE buttons in config tab lack confirmation dialogs. Cross-cutting UX (US-089/US-093). |
| F-245 | High | Measurement error UI shows raw Python/NumPy exception. Overlaps F-235. |
| F-234 | Medium | Only 35/39 DJ links in local-demo (4 missing). Investigation needed. |
| F-237 | Medium | Speaker config activation UX unclear / no venue config management (relates to US-113/D-062). |
| F-016 | Medium | Audible glitches after PW restart with capture adapter |
| F-013 | Medium | wayvnc TLS needed before US-018 guest devices |
| F-239 | Medium | Default profile 2way-80hz-ported fails: missing sub-ported-15.yml (US-090). |
| F-240 | Medium | Unknown filter_type "fullrange" not handled by backend (US-090). |
| F-241 | Medium | DRIVER PROTECTION stale state after profile activation (US-092). |
| F-246 | Medium | Mixxx invisible in graph viz — classifyNode() drops JACK clients with empty media_class (US-095). Affects production. |
| F-247 | Medium | pcm-bridge 4ch/8ch channel mismatch — zero audio in local-demo spectrum (US-115 regression). |
| F-039 | Medium | DSP load gauge 0% — needs pw-top BUSY parsing |
| F-242 | Low | Negative sensitivity returns opaque "write_failed" (US-093). |
| F-243 | Low | Negative phon values accepted client-side (US-094). |

### Test health (2026-10-24)

- **xfail budget exceeded: 6 active, limit 5.** F-290 ×1
  (`service-integration/test_production.py:219`), F-262 ×2
  (`service-integration/test_measurement.py:173`, `e2e/test_measurement.py:243`),
  F-270 ×3, which are misattributed and now F-296
  (`service-integration/test_mute_e2e.py:89`,
  `service-integration/test_tf_backend_integration.py:165`,
  `e2e/test_transfer_function.py:136`).
- Architect ruling: fix F-290 first (brings the count to 5), then F-296
  (opt-in signal-gen stimulus fixture), then the F-262 diagnosis with AE
  review. Deterministic xfails must be `strict=True`.
- Skip audit done by QE (2026-10-24): F-298, F-301–F-312 filed. Orphaned
  test suites with no runner: F-313. Mechanical lint: US-157.

## Key Metrics

| Metric | Value |
|--------|-------|
| Commits on main since 2026-04-04 | 185 (first-parent: 27 PR merges, 10 direct commits 2026-04-04, 2 single-parent commits 2026-04-19, 1 unpushed local) |
| Total stories filed | 158 (US-155/156 written retroactively, US-157/158 new, 2026-10-24) |
| Total defects filed | F-319 highest. Gaps with no record: F-266–F-269, F-286, F-288, F-289, F-294 (plus older historical gaps) |
| Total decisions | D-065 highest (D-065 reconstructed, needs owner confirmation; D-064 DRAFT) |
| Active xfails | 6 (limit 5) |
| PW convolver CPU (q1024 / q256) | 1.70% / 3.47% (PW 1.4.9 measurements; not re-measured on 1.6.2) |
| PA path latency (q256) | ~5.3ms |
| Longest stable run | 13h 39m, zero xruns (O-018) |

## External Dependencies

| Dependency | Status |
|------------|--------|
| Pi 4B hardware | Production Pi `192.168.178.185`; test Pi `192.168.178.35`. Current state unknown (no activity since April). |
| GitHub CLI auth | **Broken.** `gh` returns HTTP 401 for github.com. Owner must re-authenticate. |
| Core software | PW 1.6.2 on main, Mixxx 2.5.0, Reaper 7.64 |
| Hercules USB-MIDI | Enumeration confirmed, full test pending |
| APCmini mk2 mapping | Research needed |

## Key Decisions

See `decisions/` directory and `decisions-index.md` for all decisions (D-001
through D-065). Most significant recent decisions:

- **D-040** (2026-03-16): Abandon CamillaDSP — pure PipeWire filter-chain pipeline
- **D-043** (2026-03-20): WirePlumber retained for device management, linking disabled
- **D-060** (2026-03-29): Local CA for TLS — replaces D-032 self-signed (unblocks US-110 passkeys)
- **D-061** (2026-03-30): GM manages PW/WP lifecycle — amends D-058
- **D-062** (2026-03-30): First-boot / active config — FoH passthrough baseline, mute-default safety
- **D-063** (2026-03-30): 8ch filter-chain convolver + universal audio gate
- **D-064** (2026-04-04): NixOS VM test framework for CI smoke testing (DRAFT)
- **D-065** (2026-04-19, reconstructed): Remove WP 90-no-auto-link.conf, amends D-043. **Owner confirmation required.**

## Session 15 Re-sync (2026-10-24)

### What landed on main since session 9 (from CM log)

| Date | Commit / PR | Content |
|------|-------------|---------|
| 2026-04-04 | 10 direct commits (`4d0ae4db`..`86550b11`) | CI restructure, PR-based workflow docs, worktree enforcement v2, defects F-256–F-262, F-265, US-131 docs |
| 2026-04-04 | PR #2 | US-128 PipeWire 1.6.2 |
| 2026-04-05 | PRs #3, #5, #6, #9, #11, #13 | xfail-tracking cleanup, F-256, F-266, CI paths filter, US-120, US-131 |
| 2026-04-06 | PRs #10, #12, #14, #15, #16, #17, #19, #20, #21, #22, #24, #25, #26, #27, #28 | UMIK-sim measurement mode (F-262/F-265 work), F-249, E2E for US-090/091/093/096, F-250–255 xfail fixes, L-054 mock-policy prompts, parallel T2 port propagation, F-270, US-113, deployment/NixOS docs, F-273, US-140, test-expectations docs |
| 2026-04-07 | PRs #30, #31, #32, #33, #34, #35 | F-275 port-propagation E2E overhaul (incl. US-142–153 tests, F-284), testing principles, F-287, session-14 stories/defects docs, F-272, F-285 |
| 2026-04-19 | `991ff456` (PR unknown) | F-291, F-293, F-295 fixes, D-065, US-156 |
| 2026-04-19 | `c34f7da7` (PR unknown) | US-155 venue config |
| 2026-10-24 | `95306f66` (local, unpushed, no PR) | PreCompact hook schema fix |

### Tracking changes made in this re-sync

- Index files regenerated from the per-item files. The header warns
  against `split-monoliths.py` (F-297).
- Reconstructed records filed from commits and code comments: F-291,
  F-292, F-293, F-295, US-155, US-156, D-065. Each is marked
  "reconstructed" and needs confirmation from the named role.
- New defects: F-296 (QE/architect xfail audit) and F-297 (PM).
- Second commit: F-298–F-319 (test integrity, D-009, gate safety,
  retroactive security review), US-155/156 rewritten by PO, US-157, US-158.
  F-262/F-290/F-296/US-113 updated with review conditions and AC. US-142–154,
  F-256, F-272, F-287 updated from QE confirmations. Security review recorded
  on F-291, F-292, F-293, D-065: claimed F-291/F-293 approvals are NOT
  confirmed (F-293 approved retroactively today).
- ID gap F-294 confirmed: no record anywhere.
- Status lines updated with merge evidence: US-113, US-120, US-128,
  US-131, US-140, US-142–US-154, US-132, F-256, F-262, F-272, F-287,
  F-290.
- PipeWire version corrected to 1.6.2 in the component table.

### Open follow-ups

- PO: review US-157 AC.
- AE: retroactive reviews of US-155 (first), F-291, F-295, D-065; F-318
  assessment.
- Architect: decide the F-297 fix. Confirm whether F-295 is one defect or
  two. Rule on F-287 node name (D-057). Pick the F-314 mechanism.
- QE: CI-log evidence for US-142–149, F-256, F-272 (needs CM).
- CM (Pi OBSERVE/CHANGE, amps OFF): F-318 evidence, F-316 boot check, F-319.
- Owner: `gh` re-auth, `95306f66`, retroactive review scope, D-065.

## Session 9 Summary (2026-04-02)

### Commits (~45, session ongoing)

| SHA | Description |
|-----|-------------|
| 6ef8f93 | US-123: GM deterministic boot state (F-249 fix, venue persistence, enhanced get_state) |
| 1b9b7b9 | US-127 story: runtime coefficient switching (D-053) |
| b391c98 | US-123/124/125/126 boot state stories |
| a168309 | Session 9 progress update |
| 86d9c26 | US-120/121/122 AE refinements + post-convolver-only design/verify workflow |
| 68c9654 | Theory: post-convolver-only reference — remove pre-convolver tap per owner directive |
| 8fbf6ce | Theory: AE review + owner design/verify workflow clarification |
| b5e49e3 | Theory: incorporate AE review — reference taps, coherence, program material, safety |
| cf0dd1c | Stories: US-120/121/122 real-time measurement stories |
| 3425946 | Theory: real-time transfer function and multichannel delay measurement |
| 438a8a2 | Theory: phase correction analysis — minimum-phase optimal for PA transient fidelity |
| bb71a86 | Tests: mark measurement tests needs_usb_audio, xfail flaky link test |
| 38ac9e0 | Fix: mock-mode quantum default 256, sync on mode switch |
| 5b3880a | Tests: E2E fixes — DJ mode fixture, config key paths, link count ranges, pw-dump retry |
| e8d722e | Tests: Playwright crash fix — full chrome binary + sandbox/shm flags |
| 01f6039 | Docs: F-248 spectrum hiccup root cause analysis (postponed) |
| eea6e48 | Tests: E2E wrapper — LOCAL_DEMO path resolution, pw-jack/curl in PATH |
| bc9adac | Tests: Phase 1b — E2E backend detection, safety fixtures, audio flow tests |
| 32de7e6 | Tests: correct parent path depth after unit/ move |
| 7c2e56d | Docs: session 9 progress update |
| 2d78d23 | Docs: test infrastructure design — 4-tier backend model |
| 197f5b1 | Tests: Phase 1a — move unit tests to tests/unit/, E2E to tests/e2e/ |
| 5ca4735 | E2E endpoint path corrections |
| d669d3f | web UI PATH for pw-dump/pw-cli |
| 0d7cdee | tmpfiles Group=users |
| be8d682 | cert service Group=users |
| 1f3e865 | US-119 libcamera disable |
| 6297a4f | CM role prompt fix: remove git reset HEAD from commit protocol (L-020) |
| 308c0b8 | labwc autostart — executable mode + start wayvnc directly |
| c4d9823 | labwc autostart — activate graphical-session.target for wayvnc |
| 972ad72 | WLR_LIBINPUT_NO_DEVICES for headless Pi |
| ed38be1 | greetd labwc launch — writeShellScript + dbus-run-session |
| f0479b6 | greetd XDG_RUNTIME_DIR for labwc auto-login (superseded by ed38be1) |
| e657e1a | blacklist brcmfmac (WiFi unused, eliminates boot WARNING) |
| 6c50b0b | greetd TTYPath + logind seat assignment for labwc |
| cce3e23 | VC4 DVP clock + HDMI nodes in device tree overlay |
| 3d77388 | udev GROUP=audio instead of OWNER=ela for NixOS compat |
| 72cdd83 | WirePlumber config via configPackages (fix script search path) |
| 9735c5b | dtoverlay=disable-bt in config.txt (D-019) |
| bc9ab7c | V3D/VC4 + disable-bt device tree overlays for Pi 4B |
| c791ada | US-072 architect-reviewed initrd module list |
| 4c17ebb | US-072 strip initrd modules for minimal kernel (SD card build fix) |
| c3b8c7a | US-113 Phase 5: venue selection and audio gate E2E tests |
| 7976ee0 | US-114 SND_SOC/DRM_VC4 dep, parent-level virt/media, NVMe disable |
| 6653c5f | US-113 Phase 4: venue selection and audio gate Web UI controls |
| 29da641 | docs: S8-dup team duplication incident in CLAUDE.md |
| e56cbd6 | docs: session 8 status, F-235/F-236 resolved, SETUP-MANUAL D-063/US-113 |

### Accomplishments

1. **US-072 hardware validation complete** — NixOS SD card image flashed to test Pi
   (192.168.178.35). 11 iterative fix commits resolved: V3D/VC4 device tree overlay
   (19 fragments), greetd + labwc + wayvnc display stack, WirePlumber config path,
   udev audio group, brcmfmac blacklist. Result: PREEMPT_RT 6.12.62 kernel, VC4
   hardware GPU, full Wayland desktop, PipeWire + WirePlumber running, zero kernel
   WARNINGs, clean boot.
2. **US-113 all 5 phases committed** — Phase 4 (Web UI venue selection + audio gate
   controls, `6653c5f`) and Phase 5 (E2E tests, `c3b8c7a`) completed. QE approved
   34/34 E2E. Story ready for owner acceptance.
3. **US-114 kernel config fixes** — SND_SOC/DRM_VC4 dependency resolution, initrd
   module stripping, NVMe disable. Kernel validated on test Pi hardware.
4. **S8-dup incident documented** — CLAUDE.md updated with session 8 team duplication
   incident (ninth occurrence).
5. **Gate 2 PASSED** — Full audio workstation stack running on test Pi. All 11 checks
   pass: PREEMPT_RT, V3D HW GPU, PipeWire FIFO/88, WirePlumber, GraphManager,
   signal-gen, pcm-bridge (both instances), Web UI HTTPS with auto-generated SSL certs,
   all API endpoints 200.
6. **US-119 libcamera disable** committed (`1f3e865`).
7. **Test infrastructure design doc finalized** — `docs/architecture/test-infrastructure.md`,
   architect + QE approved.
8. **US-098 P1/P2 verified** — 41/41 pass.
9. **Worker-4 fixes** — cert service Group=users (`be8d682`), tmpfiles Group=users
   (`0d7cdee`), web UI PATH for pw-dump/pw-cli (`d669d3f`), E2E endpoint corrections
   (`5ca4735`).
10. **CM role prompt fix** (`6297a4f`) — git reset HEAD removed from commit protocol
    (L-020 root cause).
11. **Nix store cleanup** — 45.6 GB freed on builder.
12. **Spectrum hiccup analysis** — single-clock event loop jitter root cause identified.
    Owner rejected decimation/batching fix. Approach TBD.
13. **Test infrastructure Phase 1a+1b complete** — unit tests moved to `tests/unit/`,
    E2E tests to `tests/e2e/` (`197f5b1`). Phase 1b: E2E backend detection, safety
    fixtures, audio flow tests (`bc9adac`). Playwright crash fix (`e8d722e`).
14. **E2E baseline established** — 60 pass, 4 fail (F-249 GM quantum), 12 skip, 1 xfail.
    US-090/092-097 re-verification unblocked.
15. **Theory docs committed** — Real-time transfer function measurement, multichannel
    delay measurement, phase correction analysis. AE reviewed. 6 commits.
16. **US-120/121/122 stories filed** (`cf0dd1c`) — real-time measurement stories derived
    from theory docs. Pre-convolver references removed per owner directive (`68c9654`).
17. **F-249 filed and RESOLVED** — GM quantum not changing on mode switch. Fixed by
    US-123 (`6ef8f93`). 277 tests pass.
18. **US-123 implemented** (`6ef8f93`) — GM deterministic boot state: F-249 fix (quantum
    on startup), NixOS default standby mode, venue name persistence across reboots
    (owner directive: crash recovery one-tap restore), enhanced get_state RPC.
19. **8 new stories filed** — US-123/124/125/126 (boot state: deterministic boot,
    first-boot UX, mode arming, gate banner) + US-127 (runtime coefficient switching,
    D-053 formalized).
20. **D-053 architectural finding** — coefficient switching requires destroy-and-recreate
    (C-011 confirmed: PW filter-chain convolver does NOT support hot-reload). Watchdog
    does NOT auto-unlatch after node recreation. Owner elevated D-053 as critical.

### Test Pi Validation Results

All components verified on 192.168.178.35:
- PREEMPT_RT 6.12.62+rpt-rpi-v8-rt kernel
- VC4 hardware GPU (V3D DRM active)
- greetd auto-login → labwc Wayland compositor → wayvnc (port 5900)
- PipeWire + WirePlumber running as user services
- Zero kernel WARNINGs in dmesg
- Clean boot sequence

### In Progress

- **Worker-1:** US-126 (persistent audio gate banner on all tabs)
- **Worker-2:** SD card image build running on remote builder
- **Worker-4:** US-125 (explicit mode arming — verifying existing behavior)

### Blocked/Pending

- **US-113 real-stack E2E:** blocked on Phase 1b test infra completion
- **US-127 (D-053):** owner elevated as critical, blocks venue switching + measurement. Not yet started.
- **Spectrum hiccup fix:** analysis done (F-248), approach TBD (owner rejected decimation/batching)

### Pending Owner Decisions

1. **US-090/092-097 formal re-acceptance** — E2E baseline clean, ready for owner
2. **US-113 acceptance review** — all phases committed, real-stack E2E still pending
3. **US-127 (D-053) prioritization** — runtime coefficient switching. Owner elevated as critical.

### Team State

- Worker-1: US-126 gate banner (active)
- Worker-2: SD card image build (active)
- Worker-4: US-125 mode arming (active)
- Worker-3, Worker-5: status unknown
- CM: idle
- Architect, QE, AD, UX, TW: idle

### Uncommitted

- status.md update (this file)
- Worker-1 US-126 in progress
- Worker-4 US-125 in progress

## Session 8 Summary (2026-04-01)

### Commits (5 pushed)

| SHA | Description |
|-----|-------------|
| 03903c4 | D-063 watchdog mute closes audio gate (architect must-fix) |
| d6b462e | US-113 Phase 3: D-063 audio gate integration |
| b1375ce | Fix: use python3 default instead of python in local-demo |
| c61ea84 | US-114 minimal kernel config for Pi 4B audio workstation |
| 9be9269 | US-114 minimal kernel config (initial) |

### Accomplishments

1. **US-113 Phase 3 complete** — D-063 audio gate integrated into GraphManager.
   Gate starts closed (all Mult=0.0). `open_gate` RPC applies venue gains with
   cosine ramp-up. Watchdog mute now also closes the gate for consistency.
2. **US-114 committed** — Minimal kernel config targeting only required modules
   (USB audio, HID, V3D, WiFi/Ethernet, SD, ALSA, watchdog, ext4/vfat).
3. **F-235 RESOLVED** — Measurement mode fix verified (committed session 7,
   confirmed session 8). 36/36 tests pass, E2E pw-record capture working.
4. **python3 fix** — local-demo scripts now use `python3` instead of `python`.
5. **SETUP-MANUAL update in progress** — D-063 8ch convolver and US-113 venue
   config documentation.

## Session 7 Summary (2026-03-31)

### Commits (5 pushed)

| SHA | Description |
|-----|-------------|
| 8f42b8c | US-115 Phase 0: 8ch convolver (configs, dirac.wav, gain nodes, routing) |
| a06dd18 | F-236 fix: stale 48-byte coefficient stubs replaced with 16384-sample coefficients |
| 085cc0b | F-247: pcm-bridge 4ch/8ch channel mismatch documentation |
| 7247bf3 | US-113 Phase 1: venue config data model + YAML schema |
| 146a390 | US-113 Phase 2: GM venue RPC commands (venue.rs, serde_yaml, tests) |

### Accomplishments

1. **US-115 Phase 0 complete** — 8ch filter-chain convolver implemented: production
   and local-demo configs extended to 8 channels, dirac.wav (16384-sample identity
   impulse) generated, 8 gain nodes (AUX0-7), HP/IEM routed through convolver with
   Dirac passthrough.
2. **US-113 Phases 1+2 committed** — Venue config data model (YAML schema, Python
   module) and GM RPC commands (venue.rs, serde_yaml dependency, full test coverage).
3. **F-236 RESOLVED** (`a06dd18`) — Root cause: stale 48-byte coefficient stubs caused
   convolver to fail silently. 4 Playwright screenshots verify: flat monitor, correct
   room-sim, perfectly flat Dirac-everywhere UMIK-1 20Hz-20kHz (end-to-end transparent).
4. **F-247 filed and documented** — pcm-bridge 4ch/8ch channel mismatch from US-115
   8ch extension.
5. **9 defects filed** (F-239 through F-247) from QE exploratory testing and UX review.
6. **2 stories filed** — US-115 (8ch convolver, critical path) and US-116 (time delay
   measurement and compensation).
7. **7 OWNER REJECTED stories** (US-090, US-092-097) fully re-verified: QE exploratory
   Playwright pass + UX screenshot review pass. Ready for owner re-acceptance.
8. **US-072 kernel build** failed twice (disk full — 30GB builder insufficient for -dev
   output). US-114 (minimal kernel config) is next priority for reducing build size.

### Session ended

**VM bricked by unauthorized nix garbage collection (L-043).** Worker-2 ran
`nix-collect-garbage` without owner permission, removing nix store paths that
running programs (bash, coreutils) depend on. VM completely unresponsive — no
SSH, no shell. Owner will restore from snapshot. All 5 commits safely pushed
to remote. Home directory intact.

### Priorities for next session

1. **US-090/092-097 owner re-acceptance** — all 7 stories have full Gate 1 evidence.
2. **US-115 remaining phases** — Phase 0 done, integration testing needed.
3. **US-113 completion** — Phases 1+2 committed, UI and E2E integration remain.
4. **US-072 SD card build** — -dev kernel output exclusion (or US-114 minimal config).
5. **F-235 (HIGH)** — measurement mode broken in local-demo, blocks US-097/US-098.
6. **F-244 (HIGH)** — DELETE confirmation dialogs across config tab.

## Session 6 Summary (2026-03-31)

### Commits (15 pushed)

| SHA | Description |
|-----|-------------|
| 3e79abf | Consolidate PW lifecycle, start/stop, US-075 bugs |
| 4d11657 | Mixxx substitute + dirac removal |
| 62105d8 | Monitoring → standby rename (48 files) |
| 0104d30 | Room-sim IR 1024→16384 |
| 25b9595 | US-075 bugs #5, #8, #10 |
| e42cd61 | Docs D-062, D-063, F-224, US-113 |
| 180a4a8 | Fix stale measurement link count assertions |
| c27d880 | F-225/F-226/F-227 convolver metering, passthrough coeffs, dead links |
| 8962aab | F-233/F-232 skip GM push events in RPC response reads |
| 47b66fd | Defect docs F-225 through F-233 |
| 00ff2f9 | F-230 quantum change on mode switch, F-228 default mode standby |
| 3da77d6 | US-114 minimal kernel config story (draft) |
| adb93d9 | F-223 disable auth middleware by default (login page not implemented) |
| 7b43222 | US-075 E2E production-replica validation tests (35 new) |
| b9e4be0 | F-234 through F-238 filed, 7 defects RESOLVED |

### Accomplishments

1. **F-223 RESOLVED** — auth middleware now opt-in via `PI4AUDIO_AUTH_ENABLED=1` (`adb93d9`). Unblocks 7 OWNER REJECTED stories (US-090, US-092-097) for E2E re-verification.
2. **9 defects resolved** — F-223, F-225, F-226, F-228, F-230, F-232, F-233, F-238, plus multiple US-075 audit bugs.
3. **35 new E2E production-replica tests** committed (`7b43222`) for US-075 — mode switching, quantum, topology, meters.
4. **5 new defects filed** from owner morning testing — F-234 (4 missing DJ links), F-235 (measurement mode broken), F-236 (UMIK spectrum rolloff), F-237 (config activation UX), F-238 (sim gains trade-off).
5. **Monitoring → standby rename** across 48 files (`62105d8`).
6. **Room-sim IR length corrected** from 1024 to 16384 (`0104d30`).
7. **US-114** (minimal kernel config) filed as draft story.

### Pending for Session 7

1. **E2E re-verification of US-090, US-092-097** — F-223 fixed, stories unblocked.
2. **F-235 (HIGH)** — measurement mode broken in local-demo. Blocks US-098 P1/P2.
3. **F-234** — 4 missing DJ links. Investigation needed.
4. **F-236** — UMIK spectrum rolloff in test tab. Likely code duplication fix.
5. **US-072** — SD card build blocked on -dev kernel output exclusion.
6. **Status.md update** — this file was stale (session 5).

## Session 4/5 Summary (2026-03-30)

(See git history. Key: F-061/F-209 verified, 7 stories advanced to REVIEW, US-111
scope revised (WP required on PW 1.6.x), US-110/US-111 moved to IMPLEMENT, F-217
filed, nixos-upgrade.md written, US-098 P1/P2 deferral REJECTED by owner.)

## Session 3 Summary (2026-03-29)

(See git history for session 3 details. Key: D-060 filed, US-110/US-111 created,
NixOS closure trim, F-181/F-195/F-196 resolved, test Pi SSH access established.)
