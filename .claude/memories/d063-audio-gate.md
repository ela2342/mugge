# D-063 Universal Audio Gate — Implementation Facts

## Topic: Watchdog monitors 2 nodes; gain builtins are params (2026-10-24)

**Context:** safety.md §9 claimed the watchdog monitors 6 nodes, 4 of them gain nodes.
**Learning:** `MONITORED_NODES` is only `pi4audio-convolver` and `pi4audio-convolver-out`. The 8 `linear` gain builtins are not PipeWire graph nodes; they are prefixed params on `pi4audio-convolver` (`gain_left_hp:Mult`). They cannot vanish independently, so they are the mute target, not part of the monitored set. `gain_integrity.rs` separately polls for Mult > 1.0 every 30 s.
**Source:** technical-writer code reading (`watchdog.rs`), confirmed by audio-engineer.
**Tags:** watchdog, gain, filter-chain, D-063, safety, US-044

## Topic: Gate state is GraphManager memory, not the actual gains (2026-10-24)

**Context:** Drafting safety.md Section 10.
**Learning:** `gate_open` is an in-memory flag in GraphManager. Several paths change the real Mult values without updating it, so the indicator can read CLOSED while audio is live: watchdog unlatch restores gains and leaves the gate closed; GM restart starts closed but never writes Mult; web UI MUTE/UNMUTE (`audio_mute.py`) never talks to GM. Opening the gate is an instant step (F-315: the 30-step ramp runs in one main-loop iteration). A venue switch with the gate open applies gains instantly (F-314, CRITICAL). D-063's `active.yml` `audio_enabled` field does not exist in code.
Tracking: F-320 "gate state not authoritative" (High) with sub-items F-320-D (unlatch), F-320-E (GM restart), F-320-F (MUTE/UNMUTE), F-320-G (`audio_enabled` missing). F-037 (no web UI auth) is rated Critical because anyone on the network can open the gate.
**Source:** technical-writer code reading; all confirmed by audio-engineer, filed by PM.
**Tags:** gate, D-063, F-314, F-315, mute, unmute, watchdog, unlatch, graph-manager

## Topic: First-boot default venue is foh-passthrough (2026-10-24)

**Learning:** `venue.rs` `DEFAULT_VENUE_NAME = "foh-passthrough"` (override: `PI4AUDIO_DEFAULT_VENUE`, not set in nix/). It is unity gain on all 8 channels with `dirac.wav` on ch 1-4, so there is no D-031 protection (F-271). HP/IEM ch 5-8 are unity in `production.yml` too.
**Source:** technical-writer code reading.
**Tags:** venue, first-boot, foh-passthrough, D-031, F-271, IEM, hearing safety
