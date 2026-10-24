# Defects Index

Generated from the per-item files in `defects/` (the source of truth). Do NOT run `scripts/split-monoliths.py`: it would overwrite newer per-item files from stale monoliths (F-297).

| ID | Severity | Status | Summary |
|----|----------|--------|--------|
| [ENH-001](defects/ENH-001.md) | Low | Resolved (`ef7a063`, 2026-03-22) | Add sample rate to the persistent status bar (RESOLVED) |
| [ENH-002](defects/ENH-002.md) | Low | Open | Tooltips for all dashboard elements (OPEN) |
| [ENH-003](defects/ENH-003.md) | Medium | Open | Sticky "problems occurred" health indicator with manual clear (OPEN) |
| [ENH-004](defects/ENH-004.md) | Low (enhancement) | OPEN | Channel gain controls need editable text input |
| [F-002](defects/F-002.md) | Medium | Resolved | CamillaDSP websocket API bound to 0.0.0.0 (RESOLVED) |
| [F-011](defects/F-011.md) | Low | Resolved | nfs-blkmap service running unnecessarily (RESOLVED) |
| [F-012](defects/F-012.md) | Critical | Resolved (D-022 -- upstream fix in `6.12.62+rpt-rpi-v8-rt`) | OpenGL/V3D GPU applications cause hard kernel lockup on PREEMPT_RT (RESOLVED -- D-022) |
| [F-013](defects/F-013.md) | Medium | Partially resolved | wayvnc unencrypted session (PARTIALLY RESOLVED) |
| [F-014](defects/F-014.md) | Low | Resolved | RustDesk firewall rules orphaned (RESOLVED) |
| [F-015](defects/F-015.md) | High | Resolved (workaround -- ada8200-in disabled; production f... | CamillaDSP playback stalls during end-to-end testing (RESOLVED -- workaround) |
| [F-016](defects/F-016.md) | Medium | Open | Audible glitches after PipeWire restart with capture active (OPEN) |
| [F-017](defects/F-017.md) | High | Resolved (D-022 -- upstream fix in `6.12.62+rpt-rpi-v8-rt... | Mixxx hard kernel lockup on PREEMPT_RT (RESOLVED -- D-022, same root cause as F-012) |
| [F-018](defects/F-018.md) | High | Resolved | Ephemeral audio configuration not persisted across reboot (RESOLVED) |
| [F-019](defects/F-019.md) | Medium | Open | Headless labwc startup regression after WLR_LIBINPUT_NO_DEVICES removal (OPEN) |
| [F-020](defects/F-020.md) | High | Resolved (workaround -- systemd drop-in deployed) | PipeWire RT module fails to achieve SCHED_FIFO on PREEMPT_RT kernel (RESOLVED -- workaround) |
| [F-021](defects/F-021.md) | High | Resolved (US-062 Boot-to-DJ Mode, 2026-03-21) | Mixxx silently falls back from JACK to ALSA, persists incorrect backend (RESOLVED) |
| [F-022](defects/F-022.md) | High | Resolved (US-062 Boot-to-DJ Mode, 2026-03-21) | Mixxx auto-launches on boot without pw-jack wrapper (RESOLVED) |
| [F-023](defects/F-023.md) | Medium | Open (workaround identified, not yet validated) | Dual V3D GL GPU contention causes system stall on Pi 4B (OPEN) |
| [F-024](defects/F-024.md) | Medium | Open (investigation needed) | PipeWire QUANT=0 / silent audio path after Reaper launch-kill cycles (OPEN) |
| [F-025](defects/F-025.md) | Critical (risk of mechanical damage to speakers) | Resolved (TK-107 + TK-108 done, `a237bc3`) | Config generator missing subsonic driver protection filter (RESOLVED) |
| [F-026](defects/F-026.md) | High (blocks TK-114 spectrum validation) | Resolved (`784c408` — render loop synchronization fix, 20... | Spectrum display unstable on steady tone — PCM worklet ring buffer discontinuities from clock drift (RESOLVED) |
| [F-027](defects/F-027.md) | Medium (visual-only, does not affect audio) | Resolved (`d742fdf`, TK-122) | DSP load bar on dashboard health bar broken (RESOLVED) |
| [F-028](defects/F-028.md) | High (blocks room correction measurement pipeline) | Resolved (`b06d0e5`, TK-120. Validated: 0 errors after 30... | Test tone signal generation glitches via pw-play (RESOLVED) |
| [F-029](defects/F-029.md) | Medium (visual accuracy, does not affect audio) | Resolved (`d742fdf`, TK-122) | Level bar fill height 3dB below numeric readout (RESOLVED) |
| [F-030](defects/F-030.md) | High (audible xruns during DJ sets) | RESOLVED (2026-03-27, worker-2 — committed `c5c20be`, rem... | Web UI monitor JACK client causes xruns under DJ load (RESOLVED) |
| [F-031](defects/F-031.md) | Low (audio unaffected, UI-only) | Open (investigation deferred per owner) | Mixxx UI sluggish at quantum 1024 with PW filter-chain (OPEN) |
| [F-032](defects/F-032.md) | High (MUST-FIX before deployment — SEC-GM-01) | Resolved (code already implements loopback enforcement wi... | GraphManager JSON-RPC loopback binding validation (RESOLVED) |
| [F-033](defects/F-033.md) | High | RESOLVED (2026-03-27, worker-3 — committed `47663a5`, Lim... | PW RT module fails to promote JACK client threads on PREEMPT_RT (RESOLVED) |
| [F-034](defects/F-034.md) | High (service cannot start without workaround) | Resolved (`33b5577` — `=` syntax in service file + `allow... | Signal generator --max-level-dbfs negative value fails clap parsing in systemd service (RESOLVED) |
| [F-035](defects/F-035.md) | High | Resolved (`33b5577` — SEC-PW-CLIENT standardized profile ... | Seccomp SystemCallFilter kills signal generator on PipeWire client init (RESOLVED) |
| [F-036](defects/F-036.md) | Medium (becomes High when US-018 guest devices are deployed) | Open | VNC RFB password auth insufficient for guest device access (OPEN) |
| [F-037](defects/F-037.md) | High | Converted to US-110 (2026-03-29) | Web UI on port 8080 has no authentication (CONVERTED) |
| [F-038](defects/F-038.md) | Medium (UI confusion, no audio impact) | RESOLVED (2026-03-27 — commits `72def21` + `afc8528`, wor... | Dashboard tab has duplicate status bar — not consolidated into persistent bar (RESOLVED) |
| [F-039](defects/F-039.md) | Medium (cosmetic — gauge shows green/0% instead of actual load) | DEFERRED (2026-03-27 — no UI consumer for processing_load... | DSP load gauge shows 0% — FilterChainCollector hardcodes processing_load (DEFERRED) |
| [F-040](defects/F-040.md) | High (safety-related — panic mute button silently fails) | Resolved (committed `4c80c23` 2026-03-21). Backend `audio... | Panic MUTE/UNMUTE backend endpoints missing — button silently fails (RESOLVED) |
| [F-041](defects/F-041.md) | High (blocks E2E test suite reliability) | Resolved (`3a1e6bb` initial fix, `c76b882` subprocess.PIP... | Mock server (uvicorn) crashes mid-E2E Playwright run — 23 cascading timeouts (RESOLVED — pending verification) |
| [F-042](defects/F-042.md) | Medium (test failures indicate possible UI or test regressions) | Resolved (`3a1e6bb` — worker-2 fix committed) | 5 E2E test assertion failures (RESOLVED) |
| [F-043](defects/F-043.md) | Low (cosmetic — misleading color, no functional impact) | Resolved (`ef7a063`, 2026-03-22) | GraphManager SCHED_OTHER shown as red in System tab process list (RESOLVED) |
| [F-044](defects/F-044.md) | Low (cosmetic — confusing label, no functional impact) | Resolved (`ef7a063`, 2026-03-22) | Status bar "Links 100" label and value unclear to operator (RESOLVED) |
| [F-045](defects/F-045.md) | Low (cosmetic — confusing duplicate display) | Resolved (`ef7a063`, 2026-03-22) | "Mode" vs "GM Mode" in System tab — duplicate or unclear (RESOLVED) |
| [F-046](defects/F-046.md) | High (safety-relevant — quantum change during live performance causes audible glitches) | Resolved (`30a25e1`, 2026-03-22) | Config tab quantum buttons fire immediately with no confirmation dialog (RESOLVED) |
| [F-047](defects/F-047.md) | Low (accessibility / usability, no functional impact) | Resolved (`5dad57e`, 2026-03-22) | Web UI has no visible keyboard focus indicators (RESOLVED) |
| [F-048](defects/F-048.md) | Medium (test suite unreliable — cannot gate deployments) | RESOLVED — 41 of 41 fixed. F-049 (measurement wizard stat... | 41 E2E test failures — stale selectors and CSS visibility issues (IN PROGRESS) |
| [F-049](defects/F-049.md) | Medium (test reliability — sequential test runs hang) | RESOLVED (2026-03-27, verified 45/45 consecutive sequenti... | Measurement wizard mock session state isolation in E2E tests (RESOLVED) |
| [F-050](defects/F-050.md) | Medium (usability — operator cannot read dashboard elements at normal viewing distance) | Resolved (`1b527d8`, 2026-03-22) | Dashboard brightness too low — spectrum grid, meter labels, meter outlines barely visible (RESOLVED) |
| [F-051](defects/F-051.md) | Medium (usability regression from F-050 fix) | RESOLVED (committed `774c2ee`, worker-1) | Spectrum background should be black — F-050 accidentally brightened it (RESOLVED) |
| [F-052](defects/F-052.md) | Medium (usability — meters hard to read) | RESOLVED (committed `774c2ee`, worker-1) | Meter contrast still insufficient after F-050 (RESOLVED) |
| [F-053](defects/F-053.md) | Low (usability — feature exists but not discoverable) | RESOLVED (committed `774c2ee`, worker-1) | PHYS IN inactive state too low contrast — 30% opacity invisible (RESOLVED) |
| [F-054](defects/F-054.md) | Low (cosmetic — visual layering issue) | RESOLVED (committed `93567db`, worker-3) | Graph view — HP connection lines render behind Convolver node (RESOLVED) |
| [F-055](defects/F-055.md) | Medium (incomplete visualization — safety-relevant nodes not shown) | RESOLVED (committed `93567db`, worker-3) | Graph view missing four gain nodes (RESOLVED) |
| [F-056](defects/F-056.md) | High (monitoring gap — operator cannot confirm quantum state) | Partially resolved — quantum display fixed, xrun counters... | Quantum change not reflected in status bar or system tab (PARTIAL FIX — xrun portion OPEN) |
| [F-057](defects/F-057.md) | High (non-functional feature — gain controls unusable) | RESOLVED (2026-03-27, worker-3) | Config tab gain controls show -INF and are not editable (RESOLVED) |
| [F-058](defects/F-058.md) | Medium (test infrastructure — causes 6+ false failures in every pure sandbox run) | RESOLVED (2026-03-27 — already fixed, screenshots already... | E2E screenshot tests write to read-only Nix store path (RESOLVED) |
| [F-059](defects/F-059.md) | High (feature fundamentally incorrect — owner directive to rework) | Resolved (`98a95bf` 2026-03-22) — hardcoded SVG replaced,... | Graph view uses hardcoded SVG templates instead of real PipeWire topology (RESOLVED) |
| [F-060](defects/F-060.md) | Medium (process documentation — incorrect gate definitions and role/project coupling) | RESOLVED (2026-03-27 — Correction 1 already fixed. Correc... | L-042 process docs need corrections — nix develop vs nix run, separation of concerns (RESOLVED) |
| [F-061](defects/F-061.md) | High (blocks real-mode Pi operation — all PW introspection endpoints hang) | VERIFIED (2026-03-29, session 4) — all subprocess calls m... | `pw-dump` subprocess hangs under WebSocket load — event loop saturation (VERIFIED) |
| [F-062](defects/F-062.md) | Medium | Resolved (`95aeb0a` 2026-03-22) | 25 tests fail in full suite due to deprecated asyncio.get_event_loop() (RESOLVED) |
| [F-063](defects/F-063.md) | Medium | Open | uvicorn single-worker capacity — WebSocket connections block new TLS handshakes (OPEN) |
| [F-064](defects/F-064.md) | High (web-ui unreachable for owner) | RESOLVED (2026-03-27, worker-1 — system_collector async fix) | Collector timeout cycles block event loop — web-ui unreachable (RESOLVED) |
| [F-066](defects/F-066.md) | Medium (safety-adjacent — gain values protect speakers) | RESOLVED — Mult values are SESSION-ONLY (revert to .conf ... | C-009 Mult persistence claim needs Pi verification (RESOLVED) |
| [F-067](defects/F-067.md) | Medium (documentation quality — blocks US-071 owner acceptance) | Resolved (`c859d80`, 2026-03-23) | SETUP-MANUAL.md writing quality and stale CamillaDSP references (RESOLVED) |
| [F-068](defects/F-068.md) | Low | RESOLVED (2026-03-27, worker-1 — public `get_gm_state()` ... | graph_routes.py accesses private `_state` attribute of FilterChainCollector (RESOLVED) |
| [F-069](defects/F-069.md) | Medium (upgraded — architect MUST-FIX) | RESOLVED (task #166 — ValueError raised for missing requi... | US-045 schema validation uses defaults instead of rejecting missing fields (RESOLVED) |
| [F-070](defects/F-070.md) | Medium | RESOLVED (task #168 — warning added when ceiling > -6 dBF... | US-046 missing -6 dBFS operator warning (RESOLVED) |
| [F-071](defects/F-071.md) | Low | RESOLVED (task #168 — already implemented, existing code ... | US-046 silent fallback when pe_max_watts missing (RESOLVED) |
| [F-072](defects/F-072.md) | Medium | Resolved (`ca52456`, 2026-03-23) | US-044 GM safety alerts not surfaced to web UI status bar (RESOLVED) |
| [F-081](defects/F-081.md) | High | RESOLVED (2026-03-27, worker-3 — committed `fae08ce`) | pcm-bridge file descriptor leak — "Too many open files" after extended runtime (RESOLVED) |
| [F-082](defects/F-082.md) | High | Resolved (S-022, 2026-03-22) | Web-UI deployment directory mismatch — git pull does not update running service (RESOLVED) |
| [F-083](defects/F-083.md) | High | Resolved (`179dafa`, 2026-03-23) | No spectrum display on dashboard (RESOLVED) |
| [F-084](defects/F-084.md) | High | Resolved (`179dafa`, 2026-03-23 — same fix as F-083) | No level meters on dashboard (RESOLVED) |
| [F-085](defects/F-085.md) | High | RESOLVED (committed 2026-03-27) | Graph tab rendering issues — layout, direction, wiring, values, filter types (RESOLVED) |
| [F-086](defects/F-086.md) | Medium | RESOLVED (2026-03-27, worker-1 — quantum fallback to 256 ... | Config tab quantum button not pre-selected (RESOLVED) |
| [F-087](defects/F-087.md) | Low | RESOLVED (2026-03-27, QE approved — held for batch commit) | Config tab latency display missing "Latency" label (RESOLVED) |
| [F-088](defects/F-088.md) | High | Resolved (deployed to Pi S-027) | Xrun display still broken — status bar count not updating (RESOLVED) |
| [F-089](defects/F-089.md) | Medium | Open | journalctl --user returns "No entries" on Pi (OPEN) |
| [F-090](defects/F-090.md) | High | Resolved (deployed and verified on Pi S-027 — 16/16 links) | pcm-bridge auto-connect broken + monitor links session-only (RESOLVED) |
| [F-091](defects/F-091.md) | Medium | Resolved (deployed and verified on Pi S-027) | pcm-bridge violates D-043 — uses PipeWire AUTOCONNECT instead of GM-managed links (RESOLVED) |
| [F-092](defects/F-092.md) | High | Resolved (deployed to Pi S-027 — xrun aggregation working) | Xruns triggered in Mixxx at quantum 256 not visible in web UI (RESOLVED) |
| [F-093](defects/F-093.md) | High | Resolved (deployed to Pi S-027 — 16/16 links, journald re... | GM routing port naming mismatch — 0-based vs 1-based pcm-bridge ports (RESOLVED) |
| [F-094](defects/F-094.md) | Medium | RESOLVED (Option 2: certs relocated to `/etc/pi4audio/cer... | rsync --delete wiped TLS certs from ~/web-ui/ during deployment (RESOLVED) |
| [F-095](defects/F-095.md) | High | RESOLVED (2026-03-27) | journald consuming 62% CPU on Pi — GM pw-cli subprocess flood (RESOLVED) |
| [F-096](defects/F-096.md) | Low (test reliability — intermittent, does not affect production) | RESOLVED (2026-03-27, same root cause as F-049 — verified... | Measurement wizard test_happy_path_completes flaky failure (RESOLVED) |
| [F-097](defects/F-097.md) | Medium (architecture/measurement methodology — incorrect channel count) | RESOLVED (2026-03-26, commit `468533e`). Signal-gen defau... | Signal-gen should output 1 mono channel, not 4 (RESOLVED) |
| [F-098](defects/F-098.md) | High | RESOLVED (all 3 root causes fixed) | Spectrum white flash — TCP framing violation + channel count mismatch |
| [F-099](defects/F-099.md) | Medium (code quality / maintainability) | RESOLVED (2026-03-25 — FFT pipeline deduplicated as part ... | Duplicate FFT pipeline in test.js — refactor to shared module |
| [F-100](defects/F-100.md) | Low | RESOLVED (2026-03-26, commit `af2372f`). Robust preflight... | local-demo.sh leaves orphan processes on PipeWire startup failure |
| [F-101](defects/F-101.md) | High (systemic architecture issue causing repeated bug duplication) | RESOLVED (2026-03-25, verified via CDP screenshots. Root ... | Dashboard spectrum rendering not consolidated with test tab — repeated bug duplication |
| [F-102](defects/F-102.md) | High | RESOLVED (2026-03-25. Root cause: TCP retry cycles — 5s t... | Dashboard spectrum 30-second delay on page load |
| [F-103](defects/F-103.md) | High | RESOLVED (2026-03-25. Root cause: pos=0 messages with -12... | Dashboard meters still flashing despite 4 fix attempts |
| [F-104](defects/F-104.md) | Medium | RESOLVED (2026-03-26, commit `5269fe7`). Play button stat... | Test tab Play button requires manual channel selection |
| [F-105](defects/F-105.md) | Medium | RESOLVED (`151bf48`, 2026-03-25) | Test tab spectrum hiccups returned after F-099 refactoring |
| [F-106](defects/F-106.md) | Medium | RESOLVED (`151bf48`, 2026-03-25) | Test tab has no visual indication of selected signal mode |
| [F-107](defects/F-107.md) | Medium | RESOLVED (2026-03-26. Investigation found sweep end frequ... | Sweep controls — single unlabeled control, no high frequency setting |
| [F-108](defects/F-108.md) | Medium | RESOLVED (2026-03-26) | Sweep never ends — Play button stays animated past duration limit |
| [F-109](defects/F-109.md) | High | RESOLVED (2026-03-26) | Test tab level control does not affect signal-gen output level |
| [F-110](defects/F-110.md) | Medium | BY-DESIGN (2026-03-26. Expected pink-spectrum physics for... | Higher frequencies show lower volume in spectrum display |
| [F-111](defects/F-111.md) | High | RESOLVED (2026-03-26. Investigation found auto-range alre... | Test tab spectrum does not auto-scale (auto-range only on dashboard) |
| [F-112](defects/F-112.md) | High | FIXED (2026-03-26, pending commit. Fix in spectrum-render... | Peak hold drops to bottom instead of decaying to new peak level |
| [F-113](defects/F-113.md) | High | RESOLVED (2026-03-26, commit `dd0bc3a`). US-084 web UI wi... | Levels appear at wrong meters — routing mismatch after US-079 (RESOLVED) |
| [F-114](defects/F-114.md) | Low (downgraded — code path verified correct, likely browser cache per L-054) | CANNOT-REPRODUCE (2026-03-25. Code path correct end-to-en... | Stop button broken after test.js refactor |
| [F-115](defects/F-115.md) | High | RESOLVED (2026-03-25. Root causes F-101 and F-102 fixed i... | Test tab spectrum now shows dashboard bugs (-60dB line, 20s delay) |
| [F-116](defects/F-116.md) | Medium | RESOLVED (2026-03-25. Root cause: test created RingBuffer... | audio-common ring_buffer tests crash with malloc corruption (SIGABRT) |
| [F-117](defects/F-117.md) | High | MITIGATED (2026-03-26, commit `8fdf26a`). Compile-time `s... | graph-manager registry.rs type-punning of pipewire::Registry internals |
| [F-118](defects/F-118.md) | Medium (grouped) | RESOLVED (2026-03-26, commit `8fdf26a`). `checked_mul` wi... | audio-common integer overflow risks in buffer math |
| [F-119](defects/F-119.md) | Low | OPEN | RingBuffer should use UnsafeCell for data buffer (consistency + correctness) |
| [F-120](defects/F-120.md) | Medium | RESOLVED (2026-03-26). Chromium headless_shell crashes on... | E2E test Chromium headless_shell crash on aarch64 `<select>` interaction |
| [F-121](defects/F-121.md) | Low | NOT-A-BUG (2026-03-26). Rust's `TcpListener::bind()` alre... | level-bridge and pcm-bridge TcpListener::bind() lacks SO_REUSEADDR (NOT-A-BUG) |
| [F-122](defects/F-122.md) | Medium | RESOLVED (2026-03-26, commit `5de1e2c`). PPM color thresh... | Dashboard meters lack color threshold indicators |
| [F-123](defects/F-123.md) | High | RESOLVED (2026-03-26, commit `239860b`). Peak hold decay ... | Peak hold line decays to bottom while audio is playing |
| [F-124](defects/F-124.md) | High | RESOLVED (2026-03-26, commit `b032dd2`). level-bridge-sw ... | Phantom levels on A3/A4 (app-to-conv) channels |
| [F-125](defects/F-125.md) | High | RESOLVED (2026-03-26, commit `b032dd2`). Same fix as F-12... | Headphone channels 5/6 not visible in any meter group |
| [F-126](defects/F-126.md) | Medium | RESOLVED (2026-03-26, commit `239860b`). Numeric readout ... | Numeric dB values below meters update too fast — unreadable |
| [F-127](defects/F-127.md) | Medium | OPEN — root cause identified (2026-03-26, worker-1 diagno... | CPU load 75% — significantly higher than previous sessions |
| [F-128](defects/F-128.md) | High | RESOLVED (2026-03-26). Root cause: gap detection threshol... | Spectrum display completely gone |
| [F-129](defects/F-129.md) | Medium | RESOLVED (2026-03-26, commit `239860b`). Clip acknowledge... | Status bar mini meter clip indicator doesn't clear on acknowledge |
| [F-130](defects/F-130.md) | Medium | RESOLVED (2026-03-26, commit `68947e0`). HP port mapping ... | Headphone port mapping incorrect in level-bridge-hw-out |
| [F-131](defects/F-131.md) | High | RESOLVED (2026-03-26, commits `1f2d9ec` + `f842740`, depl... | Dashboard spectrum taps post-gain convolver output — signal below display floor |
| [F-132](defects/F-132.md) | Medium | OPEN | Spectrum display floor DB_MIN -90 dB still clips signal — owner wants -120 dB |
| [F-133](defects/F-133.md) | Medium → **HIGH** (REGRESSED 2026-03-26: grid snap fix broke auto-scaling entirely — nothing scales at all) | RESOLVED (2026-03-27, task #157). 5s release decay + smoo... | Spectrum auto-scaling too hectic — should snap to grid lines |
| [F-134](defects/F-134.md) | High | RESOLVED (committed 2026-03-27) | Spectrum and meters freeze intermittently |
| [F-135](defects/F-135.md) | Medium | OPEN | Status bar mini meters show peak instead of RMS |
| [F-136](defects/F-136.md) | High | RESOLVED (2026-03-27, worker-2) | DSP status bar shows wrong data (multiple sub-issues) |
| [F-137](defects/F-137.md) | Medium | OPEN | Config tab does not pre-select current quantum value |
| [F-138](defects/F-138.md) | Medium | OPEN — bar colors confirmed good (copper/rose), but group... | Status bar mini meter colors ambiguous — warning yellow vs amber default |
| [F-139](defects/F-139.md) | Low | OPEN | Status bar mode label uses unmotivated orange — should use palette color |
| [F-140](defects/F-140.md) | High | RESOLVED (2026-03-26). Root cause: systemd service had `-... | Test tone generation broken — signal-gen not producing output |
| [F-141](defects/F-141.md) | High | RESOLVED (2026-03-27) | Quantum 2048 doesn't work — possible ALSA buffer mismatch |
| [F-142](defects/F-142.md) | High | RESOLVED (2026-03-27, commits `162e9ab` + `99bc7a4`) | Spectrum doesn't render below 30 Hz — sub-bass invisible |
| [F-143](defects/F-143.md) | High | RESOLVED (2026-03-26). Owner confirmed skew appears fixed... | Spectrum frequency skew — higher frequencies show progressively lower energy |
| [F-144](defects/F-144.md) | Medium | OPEN | Test tool page does not auto-switch to measurement mode before playing |
| [F-145](defects/F-145.md) | High | RESOLVED (2026-03-26). Owner confirmed spikes gone. | Spectrum shows weird spikes at regular intervals |
| [F-146](defects/F-146.md) | Medium | CLOSED (not-a-bug, 2026-03-27) | Periodic CPU spikes observed during spectrum display |
| [F-147](defects/F-147.md) | Low (design question) | OPEN — needs D-048 clarification | Auto-range floor question — should -120 dB bottom also adapt? |
| [F-148](defects/F-148.md) | High | RESOLVED (2026-03-27, worker-1) | Spectrum decay drops in segments with spikes between them |
| [F-149](defects/F-149.md) | Low | OPEN | E2E teardown errors from unfiltered /ws/pcm 502 responses |
| [F-150](defects/F-150.md) | Medium | RESOLVED (T-091-4, task #95 — per-driver delay nodes adde... | PW filter-chain config has no delay builtin nodes — time alignment deployment gap (RESOLVED) |
| [F-151](defects/F-151.md) | High | Resolved (AD finding W-3, task #155 completed) | Mock pipeline fallback shows fake green results on backend failure (RESOLVED) |
| [F-152](defects/F-152.md) | High (safety-relevant — operator gets green light when backend is broken) | Resolved (AD finding W-3, task #156 completed) | Silent-pass-on-error in measurement pre-flight profile validation (RESOLVED) |
| [F-153](defects/F-153.md) | Medium | RESOLVED (task #160 completed) | Pre-flight doesn't check PipeWire/convolver/USBStreamer state (RESOLVED) |
| [F-154](defects/F-154.md) | Medium | RESOLVED (task #161 completed — exponential backoff, reco... | Measurement WebSocket has no reconnect logic (RESOLVED) |
| [F-155](defects/F-155.md) | Low (design quality, not demo-blocking) | RESOLVED (task #164 — raised cosine crossfade, taper, IQR... | DSP smoothing issues — windowing transition, psychoacoustic smoothing, spatial averaging (RESOLVED) |
| [F-156](defects/F-156.md) | High (demo-blocking — crossover-only filter generation fails) | RESOLVED (task #159 completed — numpy types converted to ... | POST /api/v1/filters/generate returns 500 — numpy bool_ not JSON serializable (RESOLVED) |
| [F-157](defects/F-157.md) | High (deployment blocker — worker had to improvise during #53 deployment) | RESOLVED (task #162 — full deploy.sh rewrite for D-040, a... | deploy.sh stale — still references CamillaDSP, missing D-040 configs and Rust binaries (RESOLVED) |
| [F-158](defects/F-158.md) | High (deployment blocker) | RESOLVED (task #163 completed — Section 6b added to deplo... | No repeatable Rust binary deployment process (RESOLVED) |
| [F-159](defects/F-159.md) | High (blocks owner demo validation of measurement pipeline) | RESOLVED (2026-03-27) | Measurement session fails to start in local-demo (RESOLVED) |
| [F-160](defects/F-160.md) | High (operational — owner gets stuck in wrong mode with Mixxx still running) | VERIFIED (commits `47feb22` + `4b21c51`, 2026-03-29). QE ... | Mode restore bug — Test/Measure tabs restore Monitoring instead of previous mode (OPEN) |
| [F-161](defects/F-161.md) | Medium (usability — no recovery path without CLI knowledge) | OPEN | No mode switcher in web UI — stuck mode requires CLI workaround (OPEN) |
| [F-162](defects/F-162.md) | Low (cosmetic — confusing but not blocking) | RESOLVED (worker-2, 2026-03-28) | Config tab quantum shows 256 preselected but actual quantum is 1024 (RESOLVED) |
| [F-163](defects/F-163.md) | High (blocks venue workflow on Pi) | RESOLVED (worker-3 deploy.sh path fix, 2026-03-28). Root ... | Speaker/venue config empty — profiles not loaded despite YAML files deployed (RESOLVED) |
| [F-164](defects/F-164.md) | High (BLOCKER for tonight's event — mode switching unusable) | RESOLVED (worker-2, 2026-03-28) | Mode dropdown renders partially off-screen — unusable (RESOLVED) |
| [F-165](defects/F-165.md) | High (BLOCKER for tonight's event — measurement unusable) | RESOLVED (worker-2, 2026-03-28) | Measurement dies with "response exceeds max line length" (RESOLVED) |
| [F-166](defects/F-166.md) | High (BLOCKER — root cause of -134 dB measurement signal on Pi) | RESOLVED (worker-2, committed f4ebaea, 2026-03-28). Await... | UMIK-1 prefix case mismatch — routing.rs and pw_capture.py use wrong case (RESOLVED) |
| [F-167](defects/F-167.md) | Medium (unexpected node in production — should only exist in local-demo) | NOT A DEFECT (owner confirmed browser confusion, 2026-03-28) | Room simulator node visible in Pi Graph tab (NOT A DEFECT) |
| [F-168](defects/F-168.md) | Medium (transient — resolved itself, but could recur at event) | CANNOT REPRODUCE (owner confirmed working now, transient,... | Mode switch stuck in Measurement — cannot return to DJ mode (CANNOT REPRODUCE) |
| [F-169](defects/F-169.md) | Medium (display issue — link counts not populating) | OPEN | Graph tab links shown as 0/0 (OPEN) |
| [F-170](defects/F-170.md) | High (mode switching non-functional despite UI being visible) | RESOLVED — #190 completed (profiles path fix + mode switc... | Mode switch popup visible but cannot switch to DJ mode (RESOLVED) |
| [F-171](defects/F-171.md) | Medium (hardware config incomplete for venue workflow) | RESOLVED — #191 completed (Activate button added), #189 c... | Config tab missing venue amp hardware entry (RESOLVED) |
| [F-172](defects/F-172.md) | Medium (blocks filter generation workflow from UI) | RESOLVED — #190 completed (profiles path fix) | FIR filter generation profile dropdown empty (RESOLVED) |
| [F-173](defects/F-173.md) | Low (display issue — thermal metric not populated) | OPEN | THM value missing in status bar (OPEN) |
| [F-175](defects/F-175.md) | Medium (usability — operator must type curve name instead of selecting) | RESOLVED — #192 completed (dropdown replacing text box) | Target curve selection in speaker edit is a text box instead of dropdown (RESOLVED) |
| [F-176](defects/F-176.md) | Medium (usability — help icons non-functional) | RESOLVED — #193 completed | Tooltip question marks don't show popups (RESOLVED) |
| [F-177](defects/F-177.md) | Medium (measurement display — not broadband as expected) | OPEN — root cause identified as F-181 (UMIK-1 port name m... | UMIK-1 spectrum shows only 0Hz and 20kHz flutter (OPEN — root cause: F-181) |
| [F-178](defects/F-178.md) | Medium (display calibration — curve position misleading) | OPEN | Target curve overlay drawn at 0dB instead of target SPL (OPEN) |
| [F-179](defects/F-179.md) | Medium (misleading status display) | OPEN | DSP status shows "Idle" while music is playing (OPEN) |
| [F-180](defects/F-180.md) | Low (usability enhancement — owner request) | OPEN | Events display should be newest-first with no autoscroll (OPEN) |
| [F-181](defects/F-181.md) | High (blocks UMIK-1 data path — root cause of F-177) | RESOLVED — fix committed `76367d2`, Gate 1 passed (245/24... | UMIK-1 port name mismatch — routing.rs uses capture_MONO, Pi has capture_FL (RESOLVED) |
| [F-182](defects/F-182.md) | Medium (enhancement — owner requirement for FIR generation workflow) | OPEN | Speaker config needs target curve selection + ISO 226 toggle for FIR generation (OPEN) |
| [F-183](defects/F-183.md) | High (design violation — owner directive) | RESOLVED — commit 147 (D-055). IIR biquad HPF removed fro... | Remove IIR HPF biquad nodes from config generator — defeats all-FIR design (RESOLVED) |
| [F-186](defects/F-186.md) | High (blocks 3-way speaker operation at venue) | RESOLVED — commit 146 | 3-way config generator produces only 2 convolvers instead of 6 (RESOLVED) |
| [F-187](defects/F-187.md) | Critical (VENUE BLOCKER — prevents speaker testing) | OPEN — worker-2 diagnosing | Noise on 4 channels + broken spectrum after multiple PW restarts (OPEN) |
| [F-188](defects/F-188.md) | High (breaks web UI monitoring for 3-way speaker configs) | RECLASSIFIED — US-091 test finding (PO directive). Not an... | pcm-bridge 4ch mismatch with 6ch convolver output (RECLASSIFIED) |
| [F-189](defects/F-189.md) | Medium (display incomplete for 3-way topology) | RECLASSIFIED — US-091 test finding (PO directive). Graph ... | Graph tab hardcoded for 4 channels — AUX4-5 not rendered (RECLASSIFIED) |
| [F-190](defects/F-190.md) | High (monitoring incomplete for 3-way topology) | RECLASSIFIED — US-091 test finding (PO directive). Meters... | Web UI meters/spectrum hardcoded for 4 channels (RECLASSIFIED) |
| [F-191](defects/F-191.md) | High (blocks automated routing for 3-way topologies) | RECLASSIFIED — US-091 test finding (PO directive). GM rou... | GM routing.rs hardcoded for 4 channels — cannot manage 3-way (RECLASSIFIED) |
| [F-192](defects/F-192.md) | Medium (wrong signal tapped for spectrum/monitoring) | OPEN — US-084 gap (monitoring architecture tap point). Wo... | pcm-bridge taps convolver output instead of Mixxx stereo (OPEN) |
| [F-193](defects/F-193.md) | Medium (breaks SPL display when channel layout changes) | OPEN | UMIK-1 channel index hardcoded in spl-global.js (OPEN) |
| [F-194](defects/F-194.md) | Medium (operator confusion during diagnostics) | OPEN | No UI distinction between bridge disconnected and channel silent (OPEN) |
| [F-195](defects/F-195.md) | High (wrong gain values for midrange/tweeter in 3-way configs) | RESOLVED — fix committed `6c0ea95`, Gate 1 passed (1151/1... | pw_config_generator gain staging lookup fails for 3-way roles (RESOLVED) |
| [F-196](defects/F-196.md) | High (crashes filter generation for 3-way profiles) | RESOLVED — fix committed `6c0ea95`, Gate 1 passed (1151/1... | generate_bose_filters crashes on frequency_hz list input (RESOLVED) |
| [F-197](defects/F-197.md) | High (wrong ramp-up target gains for 3-way — safety-critical path) | VERIFIED (commit `fa94ee5`, 2026-03-29). QE verified 2026... | speaker_routes.py _compute_target_gains wrong for 3-way profiles (OPEN) |
| [F-198](defects/F-198.md) | Medium (3-way profiles created via UI may be treated as 2-way by pipeline) | OPEN | Profile crossover data model mismatch — UI save vs pipeline load for N-way (OPEN) |
| [F-199](defects/F-199.md) | Low (test coverage gap — no functional regression observed) | OPEN | No E2E test for 3-way (bandpass) filter generation pipeline (OPEN) |
| [F-200](defects/F-200.md) | Low (test coverage gap — no functional regression observed) | OPEN | No E2E test for profile activation (PW config write + target gains) (OPEN) |
| [F-201](defects/F-201.md) | High (core monitoring UI non-functional in local-demo mode) | VERIFIED (2026-03-28 — QE confirmed JS fixes working agai... | Local-demo meters and spectrum broken — same symptoms as prior Pi bugs (VERIFIED) |
| [F-202](defects/F-202.md) | High (architectural gap — owner directive) | CLOSED (2026-03-28) — resolved by removal. Owner directiv... | Local demo (`nix run .#serve`) uses mock PCM bridge instead of real pcm-bridge binary (CLOSED) |
| [F-203](defects/F-203.md) | Medium (resource leak, confuses process inspection, may exhaust PID space on long sessions) | RESOLVED (2026-03-29, commit `0c38e59` — zombie cleanup +... | local-demo.sh zombie process accumulation (~70 zombies per session) (RESOLVED) |
| [F-204](defects/F-204.md) | Medium (gap vs owner intent: "use it like the real thing") | OPEN | Local-demo only supports measurement mode — no DJ/Live mode switching (OPEN) |
| [F-205](defects/F-205.md) | Low (2 test failures, cosmetic) | RESOLVED (pending commit) | test_server.py title assertions outdated after branding rename (OPEN) |
| [F-206](defects/F-206.md) | Medium (2 tests dead in full suite, test-vs-implementation mismatch) | OPEN | test_measurement_integration.py — 2 GM enter-measurement tests fail (OPEN) |
| [F-207](defects/F-207.md) | Low (systemic gap, all 5 service modules affected) | OPEN | No NixOS module integration tests (nixosTest) for any service module (OPEN) |
| [F-208](defects/F-208.md) | Medium (safety-adjacent — headroom validation silently skipped for mid/HF channels in 3-way profiles) | RESOLVED (pending commit) | D-029 gain staging validator maps midrange/tweeter to "satellite" — skips role-specific headroom checks (OPEN) |
| [F-209](defects/F-209.md) | P1 / High (safety-critical — both safety modules silently non-functional) | VERIFIED (2026-03-29, Worker-1) | US-044 watchdog + gain integrity assume gain builtins are separate PW nodes — both non-functional on real hardware (VERIFIED) |
| [F-210](defects/F-210.md) | P1 / High (US-075 local-demo unusable for owner testing) | VERIFIED FIXED (2026-03-29 — QE exploratory: 18/18 pass, ... | PipeWire crashes ~20s after local-demo startup under normal web UI usage (VERIFIED FIXED) |
| [F-211](defects/F-211.md) | High (contributes to F-210 PW crash, excessive log noise, resource waste) | VERIFIED FIXED (2026-03-29 — QE exploratory: 18/18 pass, ... | Reconciler pathological retry storm — 278 warnings in 2 seconds, no backoff (VERIFIED FIXED) |
| [F-212](defects/F-212.md) | Medium (no functional impact observed, but 404 noise pollutes browser console and server logs) | RESOLVED (fa74a8c, 2026-03-29) | 55 JS 404 errors for missing static resources across all web UI tabs (RESOLVED) |
| [F-213](defects/F-213.md) | Medium | Open | Driver protection doesn't engage after profile ACTIVATE (2026-03-29) |
| [F-214](defects/F-214.md) | Low | Open | Missing identity file for ported profile placeholder (2026-03-29) |
| [F-215](defects/F-215.md) | Low | Open | numpy empty-array crash in local-demo measurement (2026-03-29) |
| [F-216](defects/F-216.md) | Medium | Open | Orphaned PipeWire/WirePlumber processes and zombie accumulation from local-demo/test runs (2026-03-29) |
| [F-217](defects/F-217.md) | Medium (test infrastructure — not production code) | Open | E2E conftest console error filter misses /ws/pcm 403 in mock mode (OPEN) |
| [F-218](defects/F-218.md) | Medium (test infrastructure — not production code) | Open | E2E test_capture_spectrum.py — 6 WebSocket timeout failures (OPEN) |
| [F-219](defects/F-219.md) | Medium (test reliability — marginal threshold breach) | Open | test_dashboard_screenshot visual regression — 10.33% pixel diff (OPEN) |
| [F-220](defects/F-220.md) | Medium (development workflow — blocks local-demo E2E filter reload testing) | FIXED — **F-221 fixed** (filter deploy panel now uses `pw... | Local-demo PW reload kills all clients — no reconnect (FIXED — via F-221) |
| [F-221](defects/F-221.md) | Medium (unnecessary destructive reload — causes audio dropout + kills clients) | FIXED (session 5) | Filter deploy panel uses full PW restart instead of convolver node reload (FIXED) |
| [F-222](defects/F-222.md) | High (1392 zombies observed, blocks owner workflow) | Open | Zombie process accumulation in container dev environment (OPEN) |
| [F-223](defects/F-223.md) | High (blocks owner acceptance of 7 stories) | RESOLVED (session 6, commit `adb93d9` — auth middleware n... | Auth middleware intercepts all requests in local-demo despite PI4AUDIO_AUTH_DISABLED=1 (RESOLVED) |
| [F-224](defects/F-224.md) | Low | Open | Mode switch failure in dashboard gives no user-visible error feedback (OPEN) |
| [F-225](defects/F-225.md) | High (core monitoring non-functional in local-demo) | RESOLVED (session 6, commit `c27d880` — level-bridge-hw-o... | No meter bars for 8 output channels in local-demo web UI (RESOLVED) |
| [F-226](defects/F-226.md) | High (measurement pipeline non-functional in local-demo) | RESOLVED (session 6, commit `c27d880` — passthrough Dirac... | No UMIK-1 signal in measurement/test mode in local-demo (RESOLVED) |
| [F-227](defects/F-227.md) | Medium (monitoring/diagnostic display incorrect) | Open — worker-3 investigating | Link counts seem off in local-demo (OPEN) |
| [F-228](defects/F-228.md) | Low | RESOLVED (session 6, commit `00ff2f9` — default mode chan... | Default gm_mode hardcoded to "dj" in fallback paths — should be "standby" (RESOLVED) |
| [F-229](defects/F-229.md) | Low | Open | "camilladsp" key name ghost in ws_monitoring.py (OPEN) |
| [F-230](defects/F-230.md) | Medium | RESOLVED (session 6, commit `00ff2f9` — quantum change ad... | No quantum change on mode switch — DJ should be 1024 (RESOLVED) |
| [F-232](defects/F-232.md) | High (core monitoring data unreliable) | RESOLVED (session 6, commit `8962aab` — skip GM push even... | Topology endpoint returns stale/empty GM data (RESOLVED) |
| [F-233](defects/F-233.md) | High (monitoring data goes stale without warning) | RESOLVED (session 6, commit `8962aab` — skip GM push even... | FilterChainCollector poll loop silently stops updating — push event desync (RESOLVED) |
| [F-234](defects/F-234.md) | Medium | Open | Only 35/39 DJ links coming up in local-demo (OPEN) |
| [F-235](defects/F-235.md) | High (measurement pipeline non-functional locally) | RESOLVED (session 7, commits `94fbf2a`, `1bb85ec`) | Measurement mode still doesn't work in local-demo |
| [F-236](defects/F-236.md) | Medium | RESOLVED | UMIK-1 spectrum in test tab shows frequency-dependent rolloff (RESOLVED) |
| [F-237](defects/F-237.md) | Medium (UX — operator confusion) | Open | Speaker config activation behavior unclear / no venue config management (OPEN) |
| [F-238](defects/F-238.md) | Low | Open | Initial gains (-60/-64 dB) correct for Pi but questionable for simulated setup (OPEN) |
| [F-239](defects/F-239.md) | Medium | Open | Default profile 2way-80hz-ported fails — missing sub-ported-15.yml identity (OPEN) |
| [F-240](defects/F-240.md) | Medium | Open | Unknown filter_type "fullrange" not handled by backend (OPEN) |
| [F-241](defects/F-241.md) | Medium | Open | DRIVER PROTECTION shows "No speaker profile active" after activation (OPEN) |
| [F-242](defects/F-242.md) | Low | Open | Negative sensitivity returns opaque "write_failed" error (OPEN) |
| [F-243](defects/F-243.md) | Low | Open | Negative phon values accepted client-side for ISO 226 (OPEN) |
| [F-244](defects/F-244.md) | High (usability — single-click destructive actions during live show setup) | Open | All entity DELETE buttons in config tab lack confirmation dialogs (OPEN) |
| [F-245](defects/F-245.md) | High (user-facing raw exception, overlaps F-235) | Open | Measurement error UI shows raw Python/NumPy exception to user (OPEN) |
| [F-246](defects/F-246.md) | Medium (affects production Pi and local-demo) | Open | Mixxx invisible in graph viz — classifyNode() drops JACK clients with empty media_class (OPEN) |
| [F-247](defects/F-247.md) | Medium | Open | pcm-bridge 4ch/8ch channel mismatch produces zero audio in local-demo (OPEN) |
| [F-248](defects/F-248.md) | Medium | OPEN — analysis complete, fix postponed per owner | Spectrum display hiccups — event loop jitter in PCM relay (OPEN, POSTPONED) |
| [F-249](defects/F-249.md) | Medium | FIXED | GM does not set force-quantum on initial startup (quantum test failures) |
| [F-250](defects/F-250.md) | Low | RESOLVED (xfail removed — test passes reliably) | Watchdog test flaky teardown — CancelledError during TestClient shutdown |
| [F-251](defects/F-251.md) | High (upgraded from Medium per AD review — entire visual regression gate non-functional in CI) | RESOLVED | Visual regression snapshot mismatches on CI runners |
| [F-252](defects/F-252.md) | High (upgraded from Medium per AD review — entire WebSocket/PCM capture test category non-functional in CI) | RESOLVED | WebSocket/PCM capture timeouts in CI browser tests |
| [F-253](defects/F-253.md) | Low | RESOLVED (fix in CI restructure commit — actions/checkout... | Node.js 20 deprecation in actions/checkout@v4 |
| [F-254](defects/F-254.md) | Low | RESOLVED | Driver YAML Qts consistency check failures |
| [F-255](defects/F-255.md) | Low | RESOLVED | Transient fidelity pre-ringing comparison numerically unstable |
| [F-256](defects/F-256.md) | Low | fixed, awaiting verification — PR #5 merged 2026-04-05 (`... | Rust venue test fails — persist_and_load_venue_name returns None |
| [F-257](defects/F-257.md) | Low | OPEN | CI flake.nix nixConfig warnings — untrusted substituters ignored |
| [F-258](defects/F-258.md) | Medium | OPEN | level-bridge Rust tests missing from CI and worker pre-push |
| [F-259](defects/F-259.md) | Low | OPEN | Measurement Python tests not in CI — no flake app or check target |
| [F-260](defects/F-260.md) | Low | OPEN | 4 stale git stashes need review and cleanup |
| [F-261](defects/F-261.md) | Medium | OPEN | CM protocol gap — destructive operations can lose uncommitted changes |
| [F-262](defects/F-262.md) | Medium | FIX IN PROGRESS — 2 xfails remain (`service-integration/t... | E2E measurement session fails non-deterministically on filter verification |
| [F-263](defects/F-263.md) | Medium | RESOLVED | GM reconciler timing — rapid DJ->live switch link count drops |
| [F-264](defects/F-264.md) | Medium | RESOLVED | Mode badge/switching browser tests fail — WebSocket relay timeout |
| [F-265](defects/F-265.md) | Major (blocks manual testing workflow) | FIX IN PROGRESS (rework per owner feedback) | UMIK-1 sim shows no signal in test tab during measurement mode |
| [F-270](defects/F-270.md) | Medium (feature non-functional in dev/test environment) | Resolved/Fixed (PR #21) | Transfer Function tab broken in local-demo (RESOLVED) |
| [F-271](defects/F-271.md) | High (safety — driver damage risk) | OPEN | Generate D-031 protection filter WAVs for foh-passthrough.yml |
| [F-272](defects/F-272.md) | Medium | RESOLVED — PR #27 (await_settled) + PR #34 (xfail removal... | GM reconciler settlement relies on sleep-based polling |
| [F-273](defects/F-273.md) | Critical | RESOLVED | nixos-rebuild switch fails -- disko.nix and sd-image.nix produce incompatible partition layouts |
| [F-274](defects/F-274.md) | Medium | OPEN | Channel gain UI not updated after audio gate open |
| [F-275](defects/F-275.md) | High (user-visible regression) | RESOLVED | Spectrum display gone after US-131 merge -- PCM bridge monitor connection refused |
| [F-276](defects/F-276.md) | N/A | CLOSED (duplicate) | CLOSED — duplicate of F-275 |
| [F-277](defects/F-277.md) | Low | OPEN | Thermal status should use WebSocket instead of HTTP polling |
| [F-278](defects/F-278.md) | Medium (test infrastructure) | OPEN | test_audio_flow.py mislabeled as E2E -- all 8 tests bypass web UI |
| [F-279](defects/F-279.md) | Medium (test infrastructure) | OPEN | test_config_real.py mislabeled as E2E -- all 9 tests API-only |
| [F-280](defects/F-280.md) | Medium (test infrastructure) | OPEN | test_convolver_reload.py mislabeled as E2E -- all 5 tests are pw-cli subprocess tests |
| [F-281](defects/F-281.md) | Medium (test infrastructure) | OPEN | test_filter_deploy_e2e.py mislabeled as E2E -- all 9 tests API-only |
| [F-282](defects/F-282.md) | Medium (test infrastructure) | OPEN | test_mute_e2e.py partially mislabeled -- 5/8 tests API-only |
| [F-283](defects/F-283.md) | Medium (test infrastructure) | OPEN | test_production.py partially mislabeled -- 14/27 tests API-only |
| [F-284](defects/F-284.md) | Medium (test infrastructure) | RESOLVED | test_measurement_workflow.py mislabeled as E2E -- PI_AUDIO_MOCK=1 scope too large |
| [F-285](defects/F-285.md) | Medium (test infrastructure) | RESOLVED | measurement session E2E -- browser START does not transition from IDLE |
| [F-287](defects/F-287.md) | high | fixed, awaiting verification — PR #32 merged 2026-04-07 (... | Local-demo capture-usb pcm-bridge violates mock boundary (D-057) |
| [F-290](defects/F-290.md) | Low | OPEN — root cause corrected in `01da88fe` but xfail still... | E2E link-count assertion incorrect — DJ has more links than live |
| [F-291](defects/F-291.md) | high (reconstructed — confirm with audio-engineer) | fixed (commit `991ff456`, 2026-04-19, PR status unknown) ... | PipeWire RT thread throttled — xruns under sustained load |
| [F-292](defects/F-292.md) | high (reconstructed — confirm with architect) | fixed (commit `991ff456`, 2026-04-19, via D-065) — Pi ver... | WirePlumber policy.standard=disabled prevents node activation and port creation |
| [F-293](defects/F-293.md) | low (latent — currently harmless per code comment) | fixed (commit `991ff456`, 2026-04-19, PR status unknown) | GraphManager seccomp filter blocks sched_setscheduler |
| [F-295](defects/F-295.md) | medium (reconstructed — confirm with audio-engineer) | fixed (commit `991ff456`, 2026-04-19, PR status unknown) ... | Mixxx audio clicks — JACK client threads not RT; dormant ada8200-in driver node |
| [F-296](defects/F-296.md) | medium | open | Tests that need audio stimulus have no stimulus source in local-demo |
| [F-297](defects/F-297.md) | medium (tracking data loss) | open | scripts/split-monoliths.py would overwrite newer per-item tracking files |
| [F-298](defects/F-298.md) | high (test defect guarding a safety contract; no known safety defect) | open | D-063 gate-closed E2E test cannot fail — gate-open regression would show green |
| [F-299](defects/F-299.md) | medium (D-009 compliance gap; no damage risk today: overshoots are fractions of a dB and the gain nodes attenuate by 60-64 dB downstream) | open | D-009 compliance not guaranteed between bins or below 20 Hz (generator and verifier) |
| [F-300](defects/F-300.md) | low | open | Minimum-phase verifier is a heuristic proxy (90% energy / 10% peak) |
| [F-301](defects/F-301.md) | high | open | test_full_user_journey swallows filter-generation and D-009 failures as skips |
| [F-302](defects/F-302.md) | high | open | Mute browser E2E skips when the mute API is unavailable |
| [F-303](defects/F-303.md) | medium | open | E2E tests skip when GM is not connected (HTTP 502) |
| [F-304](defects/F-304.md) | medium | open | Gain display E2E skips when there are no gain rows; weak count assertion |
| [F-305](defects/F-305.md) | medium | open | Gate/venue E2E skips; gate events possibly not propagated over WebSocket |
| [F-306](defects/F-306.md) | medium | open | Graph E2E skips when the convolver node or internal topology is missing |
| [F-307](defects/F-307.md) | medium | open | Calibration E2E skips on test-isolation conflict and signal-gen 503 |
| [F-308](defects/F-308.md) | medium | open | Measurement service-integration tests are order-dependent and cascade-skip from F-262 |
| [F-309](defects/F-309.md) | medium | open | Filter deploy test skips when the deploy step fails |
| [F-310](defects/F-310.md) | medium | open | Convolver reload test skips when there are no coefficient WAVs |
| [F-311](defects/F-311.md) | medium (X1 is the biggest silent-coverage risk; priority) | open | Dead skip guards can only hide regressions (conditions always false in repo) |
| [F-312](defects/F-312.md) | high (CI gate integrity) | open | No central stack-availability guard — CI can go green with the real stack down |
| [F-313](defects/F-313.md) | high (a test contradicting a safety decision stays silently "green") | open | Orphaned test suites not executed by any runner (one contradicts D-063) |
| [F-314](defects/F-314.md) | CRITICAL (speaker damage risk; audio-engineer) | open — escalated to owner by audio-engineer via team-lead... | Hot venue switch with gate open applies new gains instantly, without confirmation |
| [F-315](defects/F-315.md) | medium (audio-engineer) | open | D-063 gate-open cosine ramp collapses to an instant step |
| [F-316](defects/F-316.md) | low (security-specialist; not blocking) | open | Lab-only static route (US-156) hardcoded into the production image |
| [F-317](defects/F-317.md) | medium (availability; security-specialist). Fix before the next gig. | open | RT throttle disabled (sched_rt_runtime_us=-1) with no configured watchdog backstop |
| [F-318](defects/F-318.md) | high (integrity / audio safety; security-specialist), pending evidence | open — needs Pi evidence | Non-JACK streams may auto-link straight to the USBStreamer since D-065 |
| [F-319](defects/F-319.md) | unknown (suspected, unverified) | open — needs verification (CM OBSERVE session) | level-bridge hw-in still targets ada8200-in, removed by F-295 (suspected) |
