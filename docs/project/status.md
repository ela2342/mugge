# Project Status

Last updated: 2026-10-24 (session 15, tracking re-sync by PM). Before this,
the file was last updated on 2026-04-04 (session 9). Story, defect and
decision details are in the `stories/`, `defects/` and `decisions/`
directories. Their index files are generated from the per-item files
(see F-297: do NOT run `scripts/split-monoliths.py`).

> **Re-sync caveats (2026-10-24).**
> - PR state: `gh` works again (2026-10-24, change-manager). PRs #13 and
>   #22 are confirmed MERGED on GitHub (2026-04-05 `07313172`, 2026-04-06
>   `4bd79a7e`). Other PR states are still taken from merge commits on main.
>   Open on GitHub and untracked until now: #40 (sprint/session-16, CI
>   24689960850 green) and #36 (F-270 audio-stimulus fixture); see O-21. Rule 13 approvals
>   and owner acceptance for PRs #2–#35 are **not recorded** in tracking.
> - `c34f7da7` and `991ff456` (2026-04-19) are single-parent commits on
>   origin/main with no PR merge (change-manager, GitHub): direct pushes,
>   Rule 13 bypassed (O-21).
> - April CI logs have expired (HTTP 410). Items verified only by CI logs
>   stay "awaiting verification" until a fresh Gate 1 run on main (F-329).
> - Local main has an unpushed commit `95306f66` (PreCompact hook schema
>   fix, 2026-10-24) made directly on main without a PR. It is waiting
>   for an owner decision.
> - Main's T1/T2 are not runnable (F-335). Branch `docs/safety-d063-gate`
>   (technical-writer) is PR #45, head `76b61347` when written (CM;
>   `e0056596` -> `7faee7b0` -> `0c55d806` -> `76b61347`; it moves as TW
>   folds fixes in, so see the PR). `76b61347` carries the architect's C1
>   (pre-flight #10 reads the gains with pw-cli, as pw-dump prints NaN,
>   subnormal and -Inf as 0.000000), AE's "only 0.000000 passes" rule,
>   SecSpec's F-037 text, AD L2 and UX note 2. At `76b61347` all six content
>   reviewers approve (AE, architect, TW, UX, AD, QE content); SecSpec has
>   no concerns and withholds until CI is green; all earlier verdicts are
>   superseded (CM, issuecomment-6386005093). CI at `76b61347` (run
>   40106812306) failed with F-335. Still
>   blocking: CI (F-335; runs 40101792484 and 40101792756 ran zero tests;
>   T3 waits on O-26) and owner acceptance, including explicit acceptance
>   of the CLAUDE.md change in #45 (CM).
>   Non-blocking follow-ups: F-343.
>   Both #44 and #45 edit venue-setup.md (merge-conflict risk, CM aware).
>   The `nc -q1` commands are still unverified on the Pi (F-341; O-2 moot,
>   now post-bootstrap verification on the Pi 5). Merge order (CM,
>   2026-10-24): the F-335 fix PR (worker-2), #41, #46 (follow-up
>   tracking, `chore/tracking-followup`, head `9e9dce9b`, stacked on
>   #41, retargeted to main after it; O-34 resolved, round restarted),
>   #45, #44 (rebased over #45 for venue-setup.md), #42, #43. #40 and
>   #36 wait for owner direction; #40 overlaps #41/#46 and #42, and
>   its US-160..162 may collide with ours (CM checking). Every rebase
>   voids approvals (range-diff re-confirmation).
> - No commits between 2026-04-19 and 2026-10-24. The state of the Pi
>   after April is unknown.

## Current Mission

**New mission (owner, 2026-10-24): bootstrap NixOS on a Pi 5 with
nixos-anywhere.** Owner: "There is multiple, and none of the historical
ones is currently reachable. Working with the NixOS one is correct. Ok.
We currently have a Pi 5 running Raspbian, reachable using ssh
ela@192.168.178.88. Use this to bootstrap a new NixOS system using
nixos-anywhere. This is hooked up to the USBStreamer and the ADA8200.
Amps are off, so the system is safe."

- Analysis basis: the team's analysis of the NixOS build stands, so
  F-348 and F-349 stand as analysed. None of the historical Pis
  (`192.168.178.185`, `192.168.178.35`) is reachable.
- Target: Pi 5, Raspbian today, USBStreamer and ADA8200 attached, amps
  off (owner). All access goes through the CM (tiers as before); warn
  the owner before any reboot or audio-stack restart (CLAUDE.md safety
  rule), which the install will cause.
- Story: US-163 (draft, product-owner). Worker: `worker-1`
  (team-lead). F-335 (CI) has its own worker, `worker-2` (O-8
  resolved).
- Owner: "For now, you have free hand to use the Pi on the .88"
  (O-37 resolved). Still open: O-36 (the owner confirms the wipe
  after worker-1's inventory and backup).
- Docs assume a Pi 4B throughout: F-353.

Previous mission:

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

0. **F-338** (CLOSE GATE always enabled). AE + architect: ships ahead of
   US-159 as a small standalone fix, UX tier A. PO: bundle with US-160
   (interim UNMUTE, high).
1. **F-314 via US-159** (critical; GM gate module, design agreed by architect, AE, UX). It
   touches gate/venue logic, so it must carry **F-298 Part A** with it or
   follow it (AE merge condition). Part B must not delay it.
2. **F-298 Part A** (A1–A7): D-063 gate test integrity. Unblocks US-113 and
   US-151 acceptance. A7 absorbs the orphaned conf test (F-313).
3. **F-320** (gate state not authoritative). Architect designs it. Sub-item
   E needs the owner's restart decision.
4. **F-315** (gate ramp is a step).
5. **F-321 + F-322** (venue coefficients and per-speaker limits not
   enforced). Before any CHN-50P use.
6. **F-290** (xfail; brings the budget back to 5).
7. **F-296** (stimulus fixture; unblocks F-298 Part B).
8. **F-262 diagnosis** (AE + architect spec; covers F-299, F-308).
9. **F-298 Part B**.
10. Test integrity: **F-312**, **F-301/F-302**, **F-324**, F-313 wiring,
    F-303–F-311, then **US-157** lint.
11. Pi evidence via CM sessions (amps OFF): **F-318** (WP default sink),
    F-321 (which coefficient files are on the Pi), F-316 boot check,
    F-319 level-bridge, **F-325/F-317** watchdog configuration and lockup
    test.
12. **F-323 / US-158** (Live-mode mic). Needed before any Live gig.
- **Gig blockers, independent of the order above:** F-037/US-110 (on
  any shared network), F-314, F-320, F-325, F-321/F-322 (CHN-50P rig) and
  F-349 (interim rule 12 until fixed).
- **Owner action:** F-326 (invalid GITHUB_TOKEN).

### Interim operating rules (2026-10-24; pending owner acceptance)

These apply while the amps are on, until the referenced defects are fixed.
safety.md §10 carries the canonical wording (technical-writer, branch
`docs/safety-d063-gate`, PR #45, `76b61347`). Its rule
numbers are given in brackets. Where a status.md rule is stricter or not
yet in safety.md (rules 9-12), the stricter rule applies (AD).

1. Close the gate before switching venues (F-314) [Rule 3].
2. Play nothing on the Pi except Mixxx, Reaper and the signal generator,
   and keep the amps off during any GraphManager restart (F-318) [Rule 9].
3. Don't open the gate on `foh-passthrough` (F-271, F-314) [Rule 2].
4. Before opening the gate, verify on the Pi (CM session, not the web UI)
   that the deployed filter files match the active venue, using the
   sha256sum check in safety.md §10 Rule 10. Until that check passes, the
   CHN-50P amp channels stay OFF. This rule relies on rule 1 (gate closed
   before any venue switch). The CHN-50P rig needs its 200 Hz filter files
   verified (F-321, F-322; AE) [Rule 10].
5. A watchdog unlatch restores fixed gains instantly, even if the gate
   was closed (F-320 D). Order: amps off, headphones off and IEMs out,
   then unlatch (GM RPC `watchdog_unlatch` via SSH or a CM CHANGE
   session; the web UI has no unlatch control until US-159 U2), then Close
   Gate and check the venue, then pre-flight #10, then amps on, then Open
   Gate (F-320) [Rule 5].
   After any GraphManager restart, treat every output as live and press
   Close Gate before assuming silence (F-320) [Rule 6].
6. Never use UNMUTE: it also goes live instantly. To recover from MUTE,
   press Close Gate, then Open Gate (F-320) [Rule 7].
7. **Hard rule:** nothing else may reach the Pi. Keep it off shared or
   venue WiFi, or block port 8080 to every device except the engineer's
   (F-037) [Rule 8].
   Proposed tightening (security, AE agrees; owner to adopt, O-32),
   until F-352 and F-354 are fixed: for every amps-on session the
   preferred control is an nftables rule that restricts 8080 to the
   engineer's device, verified from a second host on the same LAN
   (connection refused or dropped). An isolated network is acceptable
   only if it really is engineer-only (a dedicated AP or a direct
   cable); a home LAN with phones, smart devices or guests counts as
   shared. AE's proposed rule 13 is withdrawn, so it is not an owner
   decision: 13(a) is covered by Rule 8 as worded in #45 (security),
   with a wording fix queued for TW ("people or devices"; applies to
   the current target Pi); 13(b) is covered by rule 11.
8. With a 3-way speaker profile active: no Live mode, and nothing
   connected to ADA8200 outputs 7-8 except engineer headphones (F-342; AE)
   [HP/IEM Rule 3].
9. (Proposed by AE and architect, owner to adopt, O-32.) Until F-346 is
   fixed: no convolver reload at all (not the web UI filter reload, not
   POST /reload-pw). Activate new filters by a PipeWire restart: warn the
   owner first (transient risk); amps off, headphones off, IEM earpieces
   out or the pack at minimum. After the restart, run §10 Rules 1 and 10
   and pre-flight #10 before the amps go on and before headphones or IEM
   go back in (F-346; AE).
10. (Proposed by architect and AE, owner to adopt, O-32.) Until F-348 is
    fixed: (a) do not activate any speaker profile from the web UI
    (profile activation writes an unsafe PipeWire config that takes effect
    at the next PipeWire restart); (b) no 3-way or other non-2-way speaker
    profile with the amps on, in any mode. (b) supersedes rule 8's DJ
    allowance. (c) Around any PipeWire restart (including the rule 9
    procedure): (1) before the restart, confirm that
    ~/.config/pipewire/pipewire.conf.d/30-filter-chain-convolver.conf does
    not exist; if it exists, do not restart, and keep the amps off until it
    has been removed in a CM CHANGE session with the owner's agreement;
    (2) after the restart, pass pre-flight #10 before the amps go on and
    before headphones or IEM go back in, and confirm that exactly one
    pi4audio-convolver node is present (AE: #10 can pass on one clean
    convolver while a second exists) (F-348).
    (a) is not lifted until F-348 and F-355 are both fixed and tested:
    lifting it configures the web UI thermal limiter (AE).
11. (Proposed by AE, owner to adopt, O-32.) Until US-159 makes GM the sole
    Mult writer (F-344, F-345): the gate showing CLOSED does not guarantee
    silence. Besides UNMUTE (rule 6), Config tab gain Apply and the web UI
    thermal limiter write Mult without GM. Never use Config tab gain
    Apply. To make the outputs safe, turn the amps off, take headphones
    off and IEMs out, and turn the headphone/IEM amps off; do not rely
    on Close Gate alone. After any gate close, pass pre-flight #10 before the
    amps go on, whatever the gate indicator shows [Rule 11].
    If gains behave erratically: amps and HP/IEM off first; MUTE and
    Close Gate can be overwritten by the web UI limiter (F-355; AE).
12. (Proposed by AE, owner to adopt, O-32.) Until F-349 is fixed:
    (a) no Reaper plugin chain on the live path that the owner has not
    vetted, and no LV2 effects in Mixxx unless the owner has vetted them
    (Mixxx built-in effects are acceptable); (b) after any suspected
    non-finite event (plugin glitch, application crash mid-stream,
    signal-gen anomaly), first turn the amps off, take headphones off
    and IEMs out, even while the gate is Open; do not reopen the gate;
    then clear the convolvers by a PipeWire restart per Rule 9 (warn
    the owner first), then Rules 1 and 10 and pre-flight check #10.
    Nothing visible detects the event (F-349), so (a) is the only real
    interim protection (AD);
    (c) the gate fade-in is not a guarantee: a NaN or Inf stored in
    a convolver may come out as a full-scale step the instant the gate
    opens, on any channel including headphones and IEM (F-349) [AE].

"Amps off" (AE, 2026-10-24; applies everywhere): for any USBStreamer
interruption (reboot, kexec, PW restart, USB replug, an install) it
also means no headphones or IEM worn and the HP/IEM amps off or
disconnected. Transients reach ch 5-8 whatever the speaker amps do.
To go into safety.md §1 with the F-343 follow-up.

Where these rules say "press Close Gate": the button is disabled while
the indicator reads CLOSED (F-338). Then: amps off, panic MUTE, REST
`POST /api/v1/venue/gate/close`, then pre-flight #10 (AE). GM can also
report closed without zeroing anything if the convolver is missing
(F-339), so pre-flight #10 is the only proof.

Also in safety.md (AE, for HP/IEM, until a level limit exists): before the
gate opens in Live mode, the singer's earpieces are out or the IEM pack is
at minimum. Levels come up only with the singer's agreement. No gain
increase on ch 5-8 without owner confirmation (S-012).

safety.md §5 pre-flight #10 (as in #45 `76b61347`): after every boot or
PW/GM restart, before amps on: pw-dump shows exactly one
`pi4audio-convolver` and one `pi4audio-convolver-out` node; that node
has exactly the 8 named `gain_*:Mult`, each exactly `0.000000`, and all
`Add` the same, read with `pw-cli enum-params` only (pw-dump prints
NaN, -Inf and subnormals as 0.000000). Any `nan`, `inf`, `-0.000000`,
other name, missing value or second node: amps stay off. Never the UI
indicator (F-298, F-313, F-348).

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
| US-115 | IMPLEMENT (Phase 0 done) | 8ch filter-chain convolver (D-063) | Story file updated 2026-10-24. Integration testing, review and acceptance not recorded. IEM routing conflict needs an owner decision. |
| US-123 | IMPLEMENT (done) | GM deterministic boot state | Story file updated 2026-10-24. Rule 13/acceptance not recorded. Related: F-320 E. |
| US-125 | IMPLEMENT | Explicit mode arming | Session 9 verification outcome not recorded. Story file updated 2026-10-24. |
| US-126 | IMPLEMENT (Rule 13 conditional) | Persistent audio gate banner | QE conditions open. E2E blocked by F-305. The banner can show a wrong state (F-320). |
| US-114 | TEST (Pi validated) | Minimal kernel config | AC #6, #7, #9 open. |
| US-119 | IMPLEMENT (partial) | Image size tier 3 | libcamera disabled. Mesa override present, AC check pending. Story file updated 2026-10-24. |
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

Story files US-115, US-119, US-123, US-125 and US-126 were brought in
line with this table on 2026-10-24 (owner directive).

### Owner Decisions Pending (recorded 2026-10-24 so they survive the session)

Standing permissions (owner, 2026-10-24): "You do not need my
permission for read access ever, or for spawning workers. Pushes to
PRs are always fine." Branch commits need no owner go either ("commit
away"). For now the team has a free hand on the Pi 5 at `.88`. Still
the owner's: merges to main, pushes to main, release dispatch, and
any Pi CHANGE/DEPLOY outside that free hand (always warn before a
reboot or USBStreamer interruption, and re-confirm once the amps are
connected).

| # | Decision | Context / recommendation |
|---|----------|--------------------------|
| O-1 | Accept interim operating rules 1–8 (above; rule 8 added 2026-10-24, F-342) | AE/security. Canonical text in safety.md (TW branch `docs/safety-d063-gate`). Rules 9-12 and the rule 7 tightening are under O-32 (AD). |
| O-2 | ~~Approve read-only Pi check (CM OBSERVE, amps OFF)~~ | **MOOT 2026-10-24:** the old Pis are unreachable (owner). The pending checks are re-scoped to post-bootstrap verification on the Pi 5, or dropped, as their owners decide (F-348 AC7, F-341 AC3, F-346 AC7, F-316, F-318, F-319, F-321, F-328). Was to cover: which gate/venue code is deployed, the WP default sink (F-318), the hw-in level-bridge (F-319), which coefficient files are on the Pi (F-321), the route boot behaviour (F-316), and whether the safety.md `nc -q1` commands work (F-341). F-318 needs GM stopped plus a test stream, so it needs a CHANGE session. |
| O-3 | GitHub auth route (F-326) | `gh` works again for change-manager (2026-10-24; PRs #41-#43 opened). Agent sessions still get 401 from the invalid `GITHUB_TOKEN` (AE, AD). Owner: remove/refresh the variable, or accept CM-supplied diffs as the review route. |
| O-4 | `95306f66` (unpushed direct commit to main) | A one-line fix to the PreCompact hook in `.claude/settings.json`, committed straight onto local main. Moving it to a branch and opening a PR needs no owner go (standing permissions); the owner only needs to say if it should be dropped instead. PM recommends the branch + PR. |
| O-5 | Retroactive review of `991ff456` and `c34f7da7` | AE and security reviews done 2026-10-24 (F-316–F-318, F-320–F-325). The full Rule 13 set is not done. |
| O-6 | The 27 PRs merged without recorded reviews (#2–#35) | Review now, or accept as-is. |
| O-7 | D-065: confirm the decision was taken | Joint AE + security: HIGH, CRITICAL if the USBStreamer is the default sink (F-318). |
| O-8 | ~~Worker spawning~~ | **RESOLVED 2026-10-24:** spawning workers never needs the owner (standing permissions). `worker-2` is on F-335, `worker-1` on US-163. Items marked "needs a worker (O-8)" now just need one assigned; next in the work order: F-314 via US-159 with F-298 Part A, and QE's fresh Gate 1 run. |
| O-9 | ~~Scope of the playwright MCP removal (PR #43, AD-43-1)~~ **RESOLVED 2026-10-24:** owner: "playwright: just the broken one in this project". `.mcp.json` only; the settings.json entry, wrapper and devShell package stay (US-109 kept). | #43 removes the `.mcp.json` entry only. `.claude/settings.json` `mcpServers.playwright`, `scripts/playwright-mcp.sh` and the `flake.nix:287` devShell package remain. Remove those too, or keep? Confirm the user-level playwright MCP as US-109's replacement. (The owner's local `.mcp.json` edit was moved onto #43 as `e7a728af` at team-lead's request; disclosed to the owner by change-manager. Main is clean.) |
| O-10 | IEM routing: confirm D-063 supersedes the CLAUDE.md IEM-bypass note | Confirm that D-063 (IEM/HP through convolver and gate) supersedes the 2026-03-08 CLAUDE.md IEM-bypass note. If confirmed, correct CLAUDE.md (owner-approved edit) (architect). D-063 (2026-03-30) is an explicit owner decision ("8 channels passthrough from app to output"), implemented in `routing.rs` l.602-616; US-115 AC #4 agrees. The CLAUDE.md line predates it. `docs/safety-d063-gate` (TW) and PR #44 already describe IEM through the gate; CLAUDE.md sync follows the owner's answer (UX). AC on closing (TW): `docs/safety-d063-gate` (`93237884`) carries "owner reconfirmation pending, O-10"; when the owner closes O-10, that clause comes out of CLAUDE.md, safety.md §10, README, design-rationale and venue-setup. |
| O-11 | HP/IEM level limit (ch 5-8, unity gain) | Measure the ADA8200 → IEM transmitter → earpieces chain first, then decide on a per-channel soft cap or limiter (AE). |
| O-12 | GM restart behaviour (F-320 E) | Zero gains on start (safe, but a crash silences the show), or adopt state (read back the Mults and report OPEN if any is above 0). The agreed US-159 design (G5/G5a, architect + AE + UX) zeroes on start. Architect: zero on start (adopting a previous Open state after a crash restores audio with no operator action). AE position (2026-10-24, corrects the earlier "adopt" recommendation): under either option the gate never reads CLOSED while any Mult is above 0. AE recommends zero on start (simpler, fully verifiable; matches US-159 G5/T5). Adopt is an acceptable owner option for show continuity only if the adopted values pass G3 validation (finite, at most 1.0, at most the per-speaker ceiling) and the graph passes the G4 health check; otherwise GM falls back to zero. If the owner chooses adopt, T5 asserts the invariant plus that validation. Owner to decide. |
| O-13 | PO Q1: Ultimax sub D-031 exception (US-155 AC3) | AE checked it numerically: ~12 mm against 28 mm Xmax at full PA4504 output. If confirmed, file a D-031 amendment. Otherwise add a subsonic HPF. |
| O-14 | PO Q2: is the CHN-50P + Ultimax rig a real gig setup, and should it get full Rule 13 now? | PO recommends yes (7 W driver). |
| O-15 | PO Q3: purpose and consumers of the US-156 route; production or dev-only? | PO and security recommend dev-only (F-316). |
| O-16 | PO Q4: US-158 Live-mode mic, story and priority | PO and AE recommend high (F-323 blocks Live gigs). |
| O-17 | F-037 / US-110 as a gig blocker | Security + AE: CRITICAL. Auth is off in the production image. Unblock by ANY of: auth enforced and verified on the Pi, 8080 firewalled to the engineer device, or never on a shared network. |
| O-18 | US-090/092–097 re-acceptance | Pending since session 9. |
| O-19 | US-088, US-084, US-044, US-077, US-063 Pi work | Owner Pi session; now on the Pi 5 after US-163 (old Pis unreachable). |
| O-20 | US-079–082 re-validation; US-089 acceptance; US-099–104 prioritization | Unchanged since session 9. |
| O-21 | Direct pushes and untracked PRs | `c34f7da7` and `991ff456` reached main without a PR (Rule 13 bypass). PRs #40 (sprint/session-16) and #36 (F-270) are open and untracked: review, merge path, or close? |
| O-22 | ~~Does a CI paths-filter skip count as Rule 13 green?~~ **RESOLVED 2026-10-24:** owner: "Reviews as per team orchestration protocol". A skip is NOT green; T1-T3 must actually run on each PR head (CM + QE arranging runs). No author exemption: the TW gives an explicit verdict on their own PR #42. | T1-T3 were skipped on PRs #41-#43. QE: yes, only if QE confirms per PR (with grep evidence) that no changed file is a build or test input. AD: prefers the real fix, F-330 (denylist). If accepted, update CLAUDE.md Rule 13 and testing-process.md. |
| O-23 | Dev disk full | **RESOLVED 2026-10-24:** owner cleared caches, ~6.1 GB free. |
| O-24 | Hardware watchdog (F-325, F-317) | AE: not a speaker-safety backstop; a watchdog reboot resets USB and causes a transient with amps on. Worth it for availability (gate closed on boot). Owner to accept the tradeoff knowingly. |
| O-25 | Authoritative state-format spec | `.claude/team/protocol/state-format.md` dropped the Phase column from the story table (l.91-93); the canonical `team-protocol/project-state/format.md` has it, and status.md uses it. TW recommends re-syncing the local copy. |
| O-26 | T3 not in PR CI (F-333) | (a) manual T3 dispatch per PR; (b) T3 back in PR CI for `nix/`, `flake.*`, `configs/` PRs; (c) reword Rule 13 so T3 is a release gate. QE recommends (b), with (a) as the interim. Until decided, no PR can meet T1+T2+T3 green. |
| O-27 | Gate ramp curve (F-315, D-063 amendment) | AE's 30 dB/s dB-linear slew (2 s full open) vs D-063's 3 s cosine implemented over real time. AE accepts either; minimum: wall-clock rate limit, per-tick cap, generation check, >= 2 s. |
| O-28 | F-037 disclosure (security, low) | If the repo is public, F-037 documents an exploit path for a still-open vulnerability. Security: acceptable, but the owner should know. |
| O-29 | Split US-159 (PO proposal) | US-159 core (G1-G11 incl. G8b, T1-T5, T7, T8, T10, T11), US-159b WP default-sink bypass (B1, B2, T6; different files, needs a Pi CHANGE session, can run in parallel), US-159c web UI (U1-U7, T9, DOC1; depends on the core gate-state API). The AE veto lift then requires core + 159b. Owner decides. |
| O-30 | First boot under US-159 G8b (AE ruling; PO to route) | G8b refuses `open()` on `foh-passthrough.yml` until F-271 protection WAVs exist (no passthrough exemption; AE, architect agree). Q1: accept no first-boot audio until F-271 ships, with F-271 prioritised alongside US-159 (AE: yes; PO: make F-271 a US-159 dependency). Q2: is a real FoH-feed use case wanted (ch 1-4 as line level into a house processor)? If so, an explicit "external processing / line-out" output type in the speaker profile: G8b (i) still applies, (ii) skipped only for channels declared external; never the first-boot default; operator confirmation on every open; UI shows the unprotected state while open (AE conditions). Q3 (UX): a deliberate "monitors only" open (ch 5-8, ch 1-4 held at 0 and verified by G11 read-back)? AE: no safety objection. Architect: a per-channel-group gate is out of US-159 scope. |
| O-31 | Thermal limiter heartbeat loss mid-show (US-159 L2/R1) | AE recommends a time-bounded hold: at once GM holds the last factor, refuses any raise and the UI shows "THERMAL PROTECTION LOST"; if the heartbeat is not back within 60 s, GM ramps down (at the G2 rate or faster) to -6 dB relative to the held value and keeps that cap until the limiter returns or the operator closes the gate; on return, normal control resumes with slewed raises (L1). Reason: fail closed at once is a show failure; an unbounded hold leaves voice-coil heating unprotected (time constants of seconds to tens of seconds). Pure fail-closed is also safe; AE refuses only an unbounded hold. Architect preferred hold plus alarm. Owner to choose. |
| O-32 | Adopt the proposed interim safety rules 9-12 and the rule 7 tightening (above) | Until the fixes land, these keep the amps-on risk down: no convolver reload, use a PipeWire restart instead (rule 9, F-346); no speaker-profile activation from the web UI and only 2-way profiles with the amps on (rule 10, F-348; also keeps the F-355 limiter unconfigured); never use Config tab gain Apply or the web UI thermal limiter, and turn the amps off rather than trust Close Gate (rule 11, F-344, F-345); no unvetted plugins and no gate reopen after a suspected NaN (rule 12, F-349); and restrict port 8080 to the engineer's device with a firewall rule, or use a truly engineer-only network (rule 7 tightening, security, F-352, F-354). AE's proposed rule 13 is withdrawn (covered by Rule 8 and rule 11), so it is not part of this decision. If rule 11 is not adopted before the next amps-on session, F-345 becomes Critical; F-346 becomes Critical if the room-correction pipeline runs with the amps on before its fix (AE). Owner: adopt all, or say which not. |
| O-33 | Coefficient reload while the gate is Open (US-159 G8c, F-346) | Architect ruling R-b, AE (RF4) and AD: reload only while the gate is confirmed Closed. Not a policy preference but a correctness requirement with the current patch: each swap is a hard discontinuity with no crossfade, and the 8 channels swap in different cycles. Reload while Open could only be reconsidered once the patch provides a synchronized, crossfaded all-channel swap. Owner to confirm. |
| O-34 | ~~PR #46 pushed and opened without owner approval~~ | **RESOLVED 2026-10-24:** owner: "Pushes to PRs are always fine." #46 stays open; CM pushes the held fixes (batches 8-12) and a fresh 7-reviewer round runs on the new head (verdicts at `0161e41a` are void). |
| O-35 | New Critical F-349: corrupted audio (NaN or Inf) can come out at full scale when the gate opens | Rare, but a single bad sample from a plugin or app can be stored in the filters and released as a full-scale step on any channel, including headphones and IEM (AE: Critical). It blocks nothing new (AE's veto on gate code already covers US-159). Owner: acknowledge, adopt interim rule 12 (O-32), and choose whether the fix goes into US-159 or a sibling story (architect and PM to propose). |
| O-36 | Confirm the Raspbian wipe on the Pi 5 | Install path (architect, PO; US-163 AC6): a NixOS RAM installer booted once via tryboot, then nixos-anywhere erases the SD card and installs. Staging and the tryboot boot are reversible (a power cycle brings Raspbian back); the erase is the wipe, irreversible. Done first (worker-1, US-163 P1/P3): inventory; backup at `mugge-backups/pi5-raspbian-88-2026-10-24`. There is no UMIK-1 calibration and no measurement data on this Pi. The Wi-Fi PSK and ela's password hash in cloud-init were not copied and are destroyed by the wipe. Owner: anything else to keep? Then confirm the wipe (PO and security: the "free hand" does not replace this confirmation). |
| O-37 | ~~Install from the story branch before the Rule 13 merge~~ | **RESOLVED 2026-10-24:** owner: "For now, you have free hand to use the Pi on the .88." Installing from the US-163 branch is allowed; after the merge the Pi is redeployed from main (US-163 AC19). Warn the owner before every reboot. |
| O-38 | Three new Criticals that let the web UI set any output to up to +20 dB, past the gate (F-352, F-354, F-355) | (1) A hand-made request with a NaN gain, which an upstream PipeWire bug turns into a random gain (F-352). (2) A hand-made request with a crafted gain name, a fixed gain up to +20 dB, still possible once login exists (F-354). (3) The web UI thermal limiter, after one bad audio sample, keeps sending random gains every 0.5 s and overrides Close Gate and MUTE (F-355; today blocked because rule 10(a) leaves the limiter unconfigured). Rated Critical by AE, the architect and security. The interim rule 7 tightening is under O-32. Owner: (a) acknowledge; (b) may the architect report the PipeWire `filter-graph.c:671` bug upstream? That is outward-facing (AE and security support it). |
| O-39 | Pi 5 hardware and network questions from the US-163 inventory | worker-1's inventory of `.88` (relayed by team-lead): (a) a HiFiBerry DAC+ HAT is fitted. US-163 keeps it disabled (AE); is anything wired to its outputs? (b) There is no fan or cooler. The no-audio bootstrap can go ahead, but US-164 (load and RT tests) needs an active cooler fitted first (PO, architect). (c) Wi-Fi is up on `.87` as well as Ethernet on `.88`: keep Wi-Fi in the NixOS image, or Ethernet only? (d) The IPs of the dev machine and the engineer's device, for the 8080 allowlist (US-163 AC10). (e) Confirm that no headphones or IEM are attached to ch 5-8 during the install (AC7). |

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
| **F-320** | High | Gate can read CLOSED while audio is live (watchdog unlatch, GM restart, UI UNMUTE). D amended: unlatch writes a hardcoded gain table past the gate (architect, AE High). |
| **F-321** | High | Venue coefficients not enforced; dirac on a fresh image; shared filenames across venues. |
| **F-322** | High | No per-speaker power/excursion limit on runtime gain (7 W CHN-50P can get 450 W). |
| **F-323** | High (readiness) | No vocal-mic capture in Live mode. Fix: US-158. |
| **F-324** | High | `graph_manager_client.py` has zero tests. |
| **F-328** | High (Live readiness) | ada8200-in no longer deployed; how Live mode gets ADA8200 ch 1/2 is unanswered (architect). Split from F-295. |
| **F-314** | **Critical** | Venue switch with gate open: instant +60/+64 dB, no ramp/confirmation. Exists on main (US-113). AE veto on gate/venue/first-boot PRs. |
| F-187 | Critical | Noise on 4 channels + broken spectrum after multiple PW restarts. Blocked — needs Pi at venue. |
| F-271 | High | D-031 protection WAVs for ch 1-4 missing (blocks US-113 acceptance). |
| F-298 | High | D-063 gate-closed test cannot fail. Part A is AE merge condition; blocks US-113/US-151 acceptance. |
| F-318 | High → Critical if confirmed | Since D-065, non-JACK streams may auto-link straight to USBStreamer (joint AE + security). Needs Pi evidence. Non-reactive layer required. |
| F-313 | Medium | Orphaned test suites; one contradicts D-063. Architect ruling + QE AC: wire/migrate/port. |
| F-312 | High | No central REQUIRE_STACK guard; CI can go green with stack down. |
| F-301, F-302 | High | Skips swallow D-009 / mute failures. |
| F-287 | High | Fixed by PR #32. Two gaps before VERIFIED (node name ruling, pinning test). |
| F-291 | Medium (AE ruling) | PW RT throttle / FIFO not applied. Fixed on main (`991ff456`), Pi verification unrecorded. Conditional on throttle/xrun evidence + configured watchdog. Claimed security approval NOT confirmed; retroactive review: LOW + F-317. |
| F-292 | High (reconstructed) | WP policy.standard=disabled broke node activation. Fixed via D-065, Pi verification unrecorded. |
| F-315 | Medium | D-063 gate-open ramp collapses to an instant step. |
| F-317 | Medium | RT throttle off with no configured watchdog. Revert to bounded value; blocks next release image (architect + security). |
| F-325 | Medium | Hardware watchdog not configured (BCM2835 failed 2/11). Fix + lockup test before next gig. |
| F-326 | Medium | Invalid `GITHUB_TOKEN` blocks all PRs (owner action, O-3). |
| F-327 | Low | Defect IDs with no record: F-267–269, F-286, F-288, F-289, F-294. |
| F-329 | Medium | CI keeps no durable test evidence (junit / -rs artifacts). |
| F-330 | Medium | CI paths filter is an allowlist; unknown paths skip T1-T3 (O-22: a skip is not green). |
| F-333 | High | T3 (SD image) not in PR CI; no PR can meet T1+T2+T3 green (O-26). |
| **F-335** | **Critical** | CI T1 fails on main before any test runs (`src/web-ui` not found in flake source). Blocks every merge, incl. #41-#43 (O-22). |
| F-357 | High (QE) | A skipped `test-and-build` counts as CI green: every green run since 2026-04-20 was docs-only, so main has had no real T1 since. Either a skip satisfies branch protection or the job is not required (worker-2 to state). |
| F-334 | Medium | local-demo still disables WP policy.standard; diverges from production (D-065), F-318 untestable locally. |
| F-331 | Low | 16k-tap dirac on ch 5-8 ~doubles convolver load; BM-2 rerun at 8ch first (architect). |
| F-332 | Low | `audio_mute.py:46` misleading log message. |
| F-348 | High (AE, architect; Critical if a generated conf or a non-D-063 node is active on the Pi) | Every web-UI profile activation (2-way too) writes a generated conf under the D-063 conf's filename, with profile-gain Mult defaults and no ch 5-8: after a PW restart the outputs come up live while GM shows CLOSED. GM's fixed list can't close N-way gains, close returns Ok (F-339), and integrity misses > 0 dB. Fix: US-159 G12/G13, G8c R-g4, T32-T37; interim rule 10; OBSERVE AC7 on hold (O-2). |
| F-349 | **Critical** (AE; likelihood low) | Non-finite audio drives full-scale output: a NaN latched in the convolver while Closed fires as a full-scale step at gate open, bypassing the fade-in, HP/IEM included; sink mapping undefined (`-Ofast` converter), worst case rated. Fix: post-gain bit-pattern finite check plus a confirmed convolver reset before every open (AE). Interim rule 12; O-35. |
| F-351 | High (AE; architect: confirmed statically) | GM gain integrity and the web UI (mute, thermal limiter, Config tab) read gains from pw-dump text, which prints NaN and -Inf as 0, and `NaN > 1.0` is false, so a NaN gain passes; the pw-cli fallback maps unparseable to 0.0. Fix: one native raw-f32 Props reader in GM shared with US-159 G11 (f); web UI takes gain state from GM. |
| F-352 | **Critical** (AE, architect) | `POST /api/v1/config/gain` passes NaN to pw-cli as text; an upstream PW bug (`filter-graph.c:671`) then applies an uninitialised value, up to +20 dB, past the gate; no auth today (F-037). Fix: finite and range check, reject not clamp, re-check in every writer. Interim: rules 7 and 11 [Rules 8, 11]; rule 7 tightening proposed (O-32). |
| F-354 | **Critical** (security, AE; architect confirmed) | The same endpoint splices the gain name into the pw-cli params: a crafted name sets any Mult up to 10.0 (+20 dB), past the gate, deterministic, still reachable with auth (US-110). Fix: exact 8-name allowlist, structural params. Interim: as F-352. |
| F-355 | **Critical** (AE; blocked today by rules 10(a), 11) | A NaN level latches the web UI thermal limiter, which then sends `nan` every 0.5 s: a persistent random gain up to +20 dB that overrides gate close and MUTE. Do not lift rule 10(a) until fixed. |
| F-347 | Medium (AE) | Config tab iterates a fixed 2-way `GAIN_NODES` list with a 0.001 fallback: under a generated N-way config it shows phantom enabled -60 dB sliders and hides the real gains (QE, static evidence). |
| F-346 | High (AE, architect; Critical if room correction runs with amps on before the fix) | `POST /reload-pw` hot-swaps coefficients with no gate check, G8b or auth; probably reloads only `conv_left_hp` and reports success silently; no crossfade; unlocked fallback swap; stalls the PW main loop. No test checks the param names (QE). Fix: US-159 G8c, T22-T26, patch changes, AC13 tests; interim rule 9. |
| F-345 | High (AE; Critical if the interim rule is not adopted before the next amps-on session) | Thermal limiter (`thermal_limiter.py:356-437`) writes `base_mult * factor` via pw-cli with no gate check, so recovery or an override restores Mult while Closed. Its tests are mock-only. Fix in US-159 (T13). |
| F-344 | High (QE, AE) | Config tab gain Apply (`POST /api/v1/config/gain`, `config_routes.py:176-215`) writes Mult via pw-cli with no gate check, so the channel is live while the indicator reads CLOSED. Fix in US-159 (T12). |
| F-343 | Low | PR #45 non-blocking follow-ups. AC2 (§1 hedge), AC3 (2-way scope) and AC7 present in #45 `d605b5c1`; AC1 (Rule 8 step 1 vs REST close) partly, no shell-on-Pi fallback yet (TW, AD). |
| F-342 | Medium (AE; High once a 3-way profile is used at a gig/rehearsal or with an IEM) | GM does not enforce D-054 `mode_constraints` on set_mode; Live on a 3-way profile puts the HP feed on IEM ch 7-8 (AD; architect confirmed: GM must refuse). |
| F-341 | Medium | safety.md pre-flight `nc -q1` commands unverified on NixOS (no netcat in `nix/`; `-q` is Debian-only). AC3 on the Pi 5 after US-163 T52 (QE). AE to rate. |
| F-340 | Low | PR #44 non-blocking docs follow-ups (architect 1-3, UX, AD L1-L5); later docs pass (TW). |
| F-338 | High | Web UI CLOSE GATE disabled while the gate reads CLOSED; interim rules 5-7 not performable from the UI (AE confirmed High). Standalone fix ahead of US-159. |
| F-339 | High | GM CloseGate returns Ok when the convolver is missing and nothing was zeroed (AE; architect confirmed in code). Likelier trigger: gain param name mismatch (AE). Fix: US-159 G11/T10. |
| F-336 | Medium | Real-Pi browser tests unusable: wizard T4 ignores PI_AUDIO_URL; monitor suite always skipped in CI (severity confirmed by QE). |
| F-337 | Low | development.md Gate 2/3 contradict testing-process.md §8 (authoritative, QE); `test-drivers` is not an app. Fixed in PR #44 (`docs/test-strategy-drift`), head `8318e930` (CM). At `8318e930`: TW (author conflict of interest declared), UX, AD, AE, architect and QE (content only) approved; SecSpec no concerns, withheld until CI is green. Still blocking: CI (F-335: runs 40101792484 and 40101792756 ran zero tests; T1+T2 must really run after the fix and a rebase; T3 waits on O-26) and owner acceptance (CM). Non-blocking follow-ups: F-340 (AC16 is must-fix, UX). |
| F-299 | Medium | D-009 not guaranteed between bins / below 20 Hz (generator + verifier). Joint fix with F-262. |
| F-303–F-311 | Medium | Skip-audit groups and dead skip guards. |
| F-262 | Medium | 2 xfails. Possible real min-phase filter-gen bug (architect ruling). Highest product risk among the xfails. |
| F-296 | Medium | No audio stimulus in local-demo; 3 xfails misattributed to F-270. |
| F-297 | Medium | `split-monoliths.py` would overwrite newer tracking files. Do not run. |
| F-272 | Medium | RESOLVED (PRs #27, #34). VERIFIED pending CI log. |
| F-290 | Low | Test assertion bug, xfail still present (architect priority 1). |
| F-037 | **Critical** (security + AE) | Web UI no auth (auth off in production image) — US-110. **Gig blocker** on any shared network: remote unauthenticated driver damage via F-314/F-320/F-322. Interim rule 7, O-17. |
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
| Total defects filed | F-348 highest. Gaps with no record: F-267–F-269, F-286, F-288, F-289, F-294, tracked as F-327 (plus older historical gaps). F-266 reconstructed from `32da863d` |
| Total decisions | D-065 highest (D-065 reconstructed, needs owner confirmation; D-064 DRAFT) |
| Active xfails | 6 (limit 5) |
| PW convolver CPU (q1024 / q256) | 1.70% / 3.47% (PW 1.4.9 measurements; not re-measured on 1.6.2) |
| PA path latency (q256) | ~5.3ms |
| Longest stable run | 13h 39m, zero xruns (O-018) |

## External Dependencies

| Dependency | Status |
|------------|--------|
| Pi hardware | New target (owner, 2026-10-24): Pi 5 at `ela@192.168.178.88`, Raspbian until the NixOS bootstrap, USBStreamer and ADA8200 attached. Old Pi 4B production (`192.168.178.185`) and test (`192.168.178.35`) Pis unreachable (owner). |
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
- Third commit (owner directive "update any outdated documentation or
  project state; track all issues"): F-266 reconstructed; F-320–F-327
  filed; AE retroactive reviews recorded (US-155, F-291, F-295, D-065/F-318);
  F-313 detailed with QE AC; F-037 marked as a gig blocker; stale story
  files US-115/119/123/125/126 updated; interim operating rules 1–7 and all
  owner-pending decisions (O-1–O-27) recorded in this file. Review input
  from the Rule 13 round on PRs #41-#43 recorded: F-037 CRITICAL, F-297
  ruling and D-032 restore, F-295 split (F-328), F-317 analysis, US-157 AC
  rewrite, US-159 gate-module story (architect + AE + UX design), F-328–F-332
  filed, US-109 kept (O-9), CI-evidence gap (F-329/F-330), T3 gap (F-333),
  local-demo WP divergence (F-334); owner rulings O-9, O-22, O-23 recorded;
  AE severity rulings F-291 (medium), F-295 (low), F-299 rationale.
- Fourth commit: interim rules 2, 4, 5, 6 aligned with the AE safety.md
  verdict; F-335 filed (T1 broken on main); F-319 scope extended; US-158
  AC9 (QE Gate 2 soak); F-298/F-313 linked to the safety.md change; O-28.
- Fifth commit: AE nits (F-315 heading, O-12/F-320 E position, US-159 T2),
  F-335 root cause and full ACs (architect + QE), US-158 AC3 cross-reference (QE).
- Follow-up PR (after the #41 freeze): F-322 AE severity rationale and
  summed-sub ceiling (G9/T7); US-159 T9 browser E2E (UX + QE), T8 invariant
  restated, B2 reuses link_audit.rs; architect O-12 position; AD leftovers
  (D-049 date, F-323 link, F-112 status, F-319 links, Gate 1 scope,
  F-335 "probable"); F-335 SHA-pin security note; US-159 GM-restart close
  reason (UX); F-336, F-337 filed. Second batch: interim rules cite safety.md
  §10 numbers, rule 4 tightened (AE), rule 5 names the unlatch route (UX),
  pre-flight #10; F-335 AC4 E2E stack; F-336 widened; F-337 QE ruling.
  Third batch: AE rule 4 text; F-338 (CLOSE GATE disabled, UX) and F-339
  (CloseGate false success, AE) filed with the interim close procedure;
  PO review of US-159 applied; US-160 (interim UNMUTE), US-161 (chain
  calibration), US-162 (dynamic limiter) filed; A35 registered; O-29.
  Fourth batch: US-159 G11 confirmed close with CloseFailed (architect,
  AE A1-A4), U4 state list and U6 CLOSE FAILED (UX), T10; G8b
  coefficient validation with T11 (AE); B2 bound and fail-closed rule, T6
  under DJ load (AE); F-338 standalone ahead of US-159 (AE + architect);
  F-339 confirmed (architect); F-337 fixed on branch; PO priorities on
  US-160-162; safety branch now `a85473df`; O-10 note (TW).
  Fifth batch: final G8b text (AE + architect, a-d, +0.1 dB, load-time
  record) and T11 cases; first-boot ruling recorded in G8b and F-271,
  O-30 filed, F-271 added to US-159 Depends on; AE veto-lift wording;
  F-338/F-339 ratings confirmed, F-339 name-mismatch trigger; US-161 ACs
  (AE); safety branch `1616dd61` approved; PR #44 (`76c897a5`) AE + UX
  approved with merge-order condition; O-10 CLAUDE.md sync note (UX).
  Sixth batch: PR #44 AD changes requested (B1, B2) recorded; F-340 (#44
  non-blocking follow-ups) and F-341 (`nc -q1` unverified on NixOS) filed;
  #44 verdict tally per CM; merge order recorded; O-10 reworded (architect).
  Seventh batch: F-344 (Config gain Apply bypasses the gate) and F-345
  (thermal limiter restores Mult while Closed; AE), US-159 write-site list
  and T12-T20 (QE), sole-writer design D1-D3 (architect) and limiter
  rules L1-L4 with R1-R3 (AE, architect); O-31, O-32; AE ratings (F-344
  High, F-345 High with a Critical trigger); F-346 (`/reload-pw`, AE High;
  partial reload and silent success per architect; interim rule 9; US-159
  G8c R-a to R-e with ReloadCount and ReloadFailed (RF1-RF4), T22-T24;
  AD patch findings; O-33); F-347 (Config tab fixed gain list, QE; AE
  Medium); F-348 (generated confs drop the boot gate, N-way gains not
  closable; AE and architect, merged; High), US-159 G12/G13, interim rule
  10; G8c R-f (content known, `object.serial`), R-h (re-arm value) and
  R-g1 to R-g4 (architect, AD, AE), T24-T37; F-346 AC13 (QE test gaps)
  and AC14; final-head tallies and CI runs;
  F-342 (D-054 mode_constraints not enforced on set_mode;
  AD, architect confirmed); F-340 progress (#44 `4e70c481`) and AC10; F-341
  AC4 (remove "not yet verified" labels); F-335 #44 CI evidence and QE
  fix-review AC6 (cachix / nix.conf warning). F-342 rated Medium by AE
  (re-rate trigger); proposed interim rule 8 (3-way: no Live, nothing on
  outputs 7-8 but HP); O-1 now covers rules 1-8; O-10 closing AC (TW);
  safety branch is PR #45 (`93237884`); #44/#45 verdicts per CM; F-341
  QE verification plan; F-340 AC10/11; F-338 AC4 and US-159 DOC2 (safety.md
  rules 5-7 update, UX); F-343 (#45 follow-ups); F-342 3-way DJ scope note
  and HP-output logging AC (AD); PR heads per CM (#44 `8318e930`,
  #45 `d605b5c1`); O-31 AE recommendation.
  Eighth batch: PR #46 (tracking follow-up) and O-34; #46 review notes:
  interim rule 11 and rule 5 #10 step (AE), pre-flight #10 `Add`, US-159
  G8b (a)/G11 (c)/G12 wording and F-346 status (architect), US-159 U6
  wording and U8, F-347 AC1/2, US-160 AC2 (UX); #46 round complete (AE,
  TW, AD changes requested; O-34 review paused); rule 11 in AE's text;
  precedence clause (AD M1); F-337, F-336, F-343, F-345, F-340, F-271,
  F-335, F-347 and US-159 R-g1/T18/T19/T22/T32/T33/T35 (TW, AD, QE);
  US-159 R-i and N1/N2 (architect, AE), G14, U8 (UX), T38-T45, DOC3;
  F-346 AC15; F-343 AC13; F-349 filed (architect, AE to rate); #45 head
  `e0056596` (CM); O-1 points to O-32 for rules 9-12 (AD). #45 round at
  `e0056596` (QE changes requested; TW fix `98ffb751` held); F-349 rated
  High (AE) and interim rule 12; US-159 G13 duplicate nodes and T46
  (architect), T38-T45 confirmed (QE); F-348 AC7 shadowing, AC10
  rollback, AC11; F-346 AC16; F-343 AC14-AC18 (SecSpec, architect, AD, UX);
  F-349 scope and ACs (AE) with the PW 1.6.2 source facts (architect); #45
  head `98ffb751`.
  Ninth batch: F-349 re-rated Critical (AE) and rewritten: AE's required
  fixes, bit-pattern finite check, the architect's `-Ofast` and pw-dump
  findings, QE's T47 plan; interim rule 12 (a)-(c) (AE); O-35; F-349 in
  the gig blockers; #45 head `76b61347` (CM; TW and UX approve);
  F-348 AC12 deploy paths (TW, architect; wizard claim withdrawn);
  F-343 AC13, AC19 and AC21 in #45, AC22-24 (QE, UX); F-346 AC17; US-159
  G11 (f) raw-float read-back and R-i N1 (a) bit test (AE); F-350
  filed (stale reload comments); F-351 filed (pw-dump gain readers,
  TW, unverified).
  Tenth batch: value oracles read Mult/Add with pw-cli or a raw pod read,
  pw-dump for topology only (QE; US-159 test criteria and T8-T22, F-338,
  F-339, F-344, F-345, F-348); T47 case (5) NaN Mult (QE); F-343 AC19
  residual clause (AD L2) and AE #10 note; F-341 AC3 (c) (QE); F-348
  AC12 deploy ban accepted (AE); F-351 confirmed and rewritten with
  ACs, status row (architect); interim strict pw-cli oracle; #45 at
  `76b61347`: all six content reviewers approve, SecSpec withheld (CM).
  Eleventh batch: F-351 rated High with AE's ACs; F-352 filed (Config
  API accepts NaN Mult; Critical if PW parses `nan`, AE); US-159 G11 (f)
  -0.0 split (QE); local commits `cac75d44`, `0ced44e5` (CM).
  Twelfth batch: owner answer on the Pi identity and the new mission
  (Pi 5 at `192.168.178.88`, NixOS bootstrap with nixos-anywhere,
  `worker-1`); O-2 moot and its checks re-scoped (F-341, F-346 AC7,
  F-348 AC7); O-8 note; O-36, O-37; F-353 filed (Pi 4B references);
  local commit `78b436a3` (CM).
  Thirteenth batch: F-352 unconditionally Critical (NaN path, PW
  parse bug); F-354 (gain-name injection) and F-355 (thermal limiter
  NaN latch) filed Critical; F-356 (CLAUDE.md boot gains); F-320 D
  amended (unlatch writes a hardcoded table); F-349 Props note; US-159
  T47 case (5), Pi 5 authority, G11 (f) warning log; US-163 (PO
  consolidated, T48-T57), US-164, US-165 filed; rule 7 tightening
  proposed (AE's rule 13 withdrawn), rule 10(a) lift condition, HP/IEM
  in "amps off"; F-341 AC3, F-346 AC7, F-348 AC7 re-scoped; owner
  standing permissions; O-8, O-34, O-37 resolved; O-38 new; O-4, O-32,
  O-35, O-36 reworded; merge order (CM); local commit `9e9dce9b` (CM).
  Fourteenth batch (#46 must-fixes at `9e9dce9b`): rule 11 HP/IEM
  wording (AE B3); pw-cli value oracles in US-159 U4, T38-T45 and
  F-298 (QE M1, M3; architect N1), raw-bits reader for `== 0` (AE
  N1), T46 alarm (QE N2); rule 13 withdrawal recorded; rule 12(b)
  immediate action (AD L2); F-353 AC5 (AD L3); pre-flight #10
  summary and F-343 to #45 `76b61347` (TW); F-348 AC7 split
  (architect); F-335 37 sites; F-357 filed (QE); US-163 AC1a, AC2,
  AC2a, AC4, AC6, AC12a, P1/P3 results; US-164 cooler prerequisite;
  O-36, O-38 reworded, O-39 new; local commit `d0065a54` (CM).
- Status lines updated with merge evidence: US-113, US-120, US-128,
  US-131, US-140, US-142–US-154, US-132, F-256, F-262, F-272, F-287,
  F-290.
- PipeWire version corrected to 1.6.2 in the component table.

### Open follow-ups

- Done 2026-10-24: US-157 AC review (PO, architect, QE); F-297 ruling;
  F-295 split (F-328); F-314 mechanism (US-159).
- Architect: rule on F-287 node name (D-057); F-321 vs F-271 relation;
  answer the F-328 Live-input question; F-331 analysis.
- QE: fresh Gate 1 run on current main with `-rs -rx` output (F-256, F-272,
  US-142–153); needs a worker (O-8).
- F-335 fix (`${self}` + Nix pin/log, architect): `worker-2`. Pin and
  log in the same PR, a separate commit (CM). T3 is a local aarch64
  sd-card build, not a release dispatch; without a builder it is NOT
  RUN, a merge blocker (O-26). QE's Gate 1 run waits on it.
- Pi checks after the US-163 bootstrap: F-341 AC3 and US-159 T47 on
  the Pi 5 after T52 (QE); F-348 AC7 is US-163 AC14 (AE); F-346 AC7
  dropped (AE). Still to re-scope by their owners: F-318, F-316,
  F-319; F-321 and F-328 to AE (architect's view: drop F-321's
  historic part, as US-159 G8/G8b fix the code path, and add a
  post-bootstrap OBSERVE inventory of `/etc/pi4audio/coeffs` with
  hashes against the repo).
- Pi 4B references in CLAUDE.md, config.md and the benchmarks (F-353);
  CLAUDE.md boot-gain text (F-356).
- safety.md follow-up branch (TW, not #45): after-Apply slider
  display; #10 missing/duplicate `-out` FAIL case; §10 Rule 8 text
  (security + AE: devices too, any deployment target, 8080 allowlist
  preferred); §1 "amps off" includes HP/IEM (AE, F-343).
- AE to rate UX's note: rule 11's "turn the amps off" does not
  silence HP/IEM; must-fix only if AE says so.
- UX follow-up after O-35: US-159 U8 states for the F-349 alarm, G13
  duplicate nodes, G14 codes, the F-351 UNKNOWN display.
- AE F-355 (g): is the `levels_sw` tap before or after the gain?
  Needed before the fix PR.
- Story IDs on #46 collide with #40 (CM, 2026-10-24: US-157..163,
  F-292, F-296; US-164/165 too). PO ruled that #46 renumbers from
  US-169 / F-358; PM sent PO the cost (about 300 references on #46,
  84 on #41, 7 in #45's safety.md, the US-163 branch) and is waiting.
  D-066 (on #40 only) must reach main: main's US-155 venue config
  depends on it (PO).
- CM: confirm that worker-1's kexec and page-size readings come from
  a CM-logged OBSERVE session; otherwise mark them unverified (AD).
- Owner: decisions in "Owner Decisions Pending" above.

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
