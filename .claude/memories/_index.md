# Project Memory Index — mugge

| File | Description |
|------|-------------|
| playwright-usage.md | Playwright browser testing rules: screenshot vs DOM snapshot, web UI connection details, hidden element cleanup |
| d040-architecture-transition.md | D-040 architecture knowledge: FilterChainCollector, pcm-bridge metering, GraphManagerClient, D-043 bypass defense, SETUP-MANUAL.md stale references, Python deployment gap (S-002), _MEAS_DIR path resolution, deploy.py stale coeffs path, signal-gen subsonic HPF gap (D-031 safety), C-011 convolver no hot-reload (D-061 GM lifecycle) |
| security-findings.md | Security defects: F-036 VNC 8-char password limit (DES/RFB), F-037 (CRITICAL since 2026-10-24, gate exposure) web UI no authentication on port 8080 |
| coding-principles.md | Core architectural principle: temporal/spatial memory safety — all safety-relevant invariant checks (bounds, channel count, etc.) must be runtime assert, never debug_assert. F-116 precedent. |
| pipewire-rt-promotion.md | PipeWire RT promotion model: JACK clients need LimitRTPRIO/LimitMEMLOCK (not CPUSchedulingPolicy=fifo). PW promotes callback threads; client process stays SCHED_OTHER. F-033/F-020 distinction. |
| orchestrator-discipline.md | Orchestrator Rule 2 violations: must not do technical analysis of failures or prescribe HOW (implementation steps, specific function calls). Relay WHAT, worker figures out HOW. |
| change-management-git.md | CM git hazards: `git reset HEAD` unsafe with parallel workers sharing a working tree — must check for other modifications before clearing staging. Data loss incident (pipewire.nix). |
| pipewire-port-activation.md | PipeWire 1.6.x port activation requires WirePlumber for all node types (adapter, filter-chain, spa-node-factory) except loopback. Permanent architectural constraint. policy.standard=disabled is local-demo only; production removed it (D-065, F-292). |
| nixos-kernel-config.md | NixOS kernel config pipeline (bcm2711_defconfig -> common-config.nix -> structuredExtraConfig), ZFS as -dev output blocker, autoModules=true on aarch64, SND_SOC must stay enabled (DRM_VC4 depends on it — CORRECTED), cross-arch nix eval performance, lib.kernel type selection guide |
| d063-audio-gate.md | D-063 gate implementation facts: watchdog monitors 2 nodes (gains are convolver params), gate state vs actual gains (unlatch/GM restart/UNMUTE bypass), F-314 hot switch, F-315 step ramp, foh-passthrough first-boot default |
| rt-scheduling-and-watchdog.md | PREEMPT_RT IRQ threads at FIFO-50 can be starved (sched_rt_runtime_us=-1), BCM2835 hardware watchdog not fed (no systemd.watchdog.runtimeTime), WP autoconnect=false does not protect a default sink |
| tracking-data-integrity.md | split-monoliths.py keeps only the last section per ID (lost the original D-032), state-format.md Phase column drift vs canonical (O-25) |
