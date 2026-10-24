# Safety Operations Manual

This document is the single authoritative reference for all safety constraints
on the Pi 4B audio workstation. Every team member -- human and automated --
must follow these rules. CLAUDE.md points here; architecture docs cross-reference
here.

**Scope:** Physical safety of speakers, amplifiers, and human hearing. This is
not about data loss or software correctness -- it is about preventing hardware
damage and hearing injury.

---

## 1. USBStreamer Transient Risk

**The USBStreamer produces full-scale transients when its audio stream is
interrupted.** These transients pass through the 4x450W amplifier chain and can
damage speakers and risk hearing.

### Actions That Cause Transients

- Rebooting the Pi, including an automatic reboot by the hardware watchdog
  (see below)
- `systemctl --user restart pipewire.service`
- Any action that causes PipeWire to drop the USBStreamer playback stream
- USB bus resets affecting the USBStreamer

**Note (D-040):** CamillaDSP is no longer in the audio path. The previous
risk from `systemctl restart camilladsp` no longer applies. All audio
processing is now within PipeWire's filter-chain — the only transient risk
is from PipeWire restarts or USB interruptions.

**Hardware watchdog reboot:** The BCM2835 hardware watchdog is not
configured in the NixOS image (F-317, F-325; from the Nix config, not
verified on the Pi). If it is configured, a watchdog reboot after a lockup
is an unannounced reboot: the USBStreamer stream drops with no chance to
warn the owner or turn off the amps. By design, after the reboot all gains
load as `Mult = 0.0` and the gate is closed (D-063, Section 10), so the
reboot transient would be the only acoustic risk and nothing would play
until the operator reopens the gate. Gate-closed-at-boot is not verified by
any test (F-298, F-313), and after any web UI speaker-profile activation
the next PipeWire start (boot or restart) may load non-zero gains (F-348,
Section 10 Known Gaps): run pre-flight check #10 (Section 5) before the
amps go back on. Whether to enable the watchdog (automatic recovery vs an
unannounced transient) is an owner decision (O-24).

### Required Procedure

**Before performing any of these actions:**

1. **Warn the owner.** Explicitly state: "This will interrupt the audio stream
   and may produce transients through the amplifier chain."
2. **Wait for owner confirmation.** The owner decides when it is safe to
   proceed (e.g., after turning off amplifiers or lowering volume to zero).
3. **There are no exceptions.** Not for "quick restarts," not for "it should be
   fine," not for emergencies. The owner decides.

This applies to all team members: workers, Change Manager, everyone.

### Cross-References

- CLAUDE.md "Safety Rules (2026-03-10)"
- S-014 lab note: CamillaDSP restart during DJ mode prep (owner confirmed amps
  safe beforehand)

---

## 2. Driver Protection Filters (D-031)

**All production audio pipeline configs MUST include driver protection filters
for every speaker channel.** This is a safety requirement to prevent mechanical
damage from out-of-band content. Post-D-040, the filter-chain convolver
(PipeWire native) provides FIR-based crossover and HPF protection; the IIR
safety-net concept from D-031 applies to any future config generation.

### Why This Matters

The critical scenario is **dirac placeholder FIR filters** (used before room
measurement). A dirac filter passes all frequencies with unity gain -- no
crossover, no subsonic protection. Sub drivers receive full-bandwidth signal
including subsonic content that can cause over-excursion damage.

**The Bose PS28 III deployment exposed this gap:** The 5.25" sealed isobaric
sub drivers (`mandatory_hpf_hz: 42`) were receiving unfiltered signal through
dirac placeholders. The room correction pipeline only generated subsonic
protection for ported enclosures, not sealed ones -- but small sealed drivers
need protection too.

### The Rule

Any speaker identity declaring `mandatory_hpf_hz` MUST have subsonic
protection in the audio pipeline, regardless of enclosure type:

- **Subwoofers (all types):** HPF below the driver's usable bandwidth. The
  `mandatory_hpf_hz` field in the speaker identity schema declares the cutoff.
- **Ported subwoofers:** HPF below the port tuning frequency. Without it, the
  driver is mechanically unloaded below tuning and excursion increases rapidly.
- **Sealed subwoofers with small drivers:** HPF below the driver's mechanical
  resonance. Small sealed drivers have limited Xmax; subsonic content causes
  over-excursion.
- **Satellites:** HPF at or above the crossover frequency to prevent
  bass-induced damage to small drivers.

**Post-D-040 implementation:** The PipeWire filter-chain convolver loads
combined FIR coefficient WAV files that embed both the crossover slope and
room correction. When dirac placeholder filters are in use (before room
measurement), subsonic protection must come from either: (a) the FIR
coefficient itself (a highpass FIR placeholder instead of a dirac), or
(b) a future `bq_highpass` IIR stage in the filter-chain config. The room
correction pipeline generates combined filters that embed the HPF into the
crossover shape, making the protection permanent once measurements are done.

**Historical note:** Under the pre-D-040 CamillaDSP architecture, this was
implemented as an IIR Butterworth HPF in the CamillaDSP YAML pipeline.

### Known Gap: Signal-Gen Measurement Path (D-040)

Post-D-040, the RT signal generator replaces CamillaDSP for measurement I/O.
The signal-gen does NOT include a subsonic HPF. Safety analysis:

- **Log sweeps (20-20kHz):** Safe. No subsonic content.
- **Pink noise (gain calibration):** The Voss-McCartney generator produces
  energy to near-DC. At the -20 dBFS hard cap (SEC-D037-04), this delivers
  approximately 0.14W into 4 ohms -- negligible for all drivers in inventory.
- **Risk scenario:** If `--max-level-dbfs` is increased above -20 dBFS in a
  future configuration change, subsonic pink noise could damage small-excursion
  sub drivers (e.g., Bose PS28 III, `mandatory_hpf_hz: 42`).

**Status:** Known gap, safe under current -20 dBFS cap. If the measurement
level cap is ever raised, a digital HPF in the signal-gen (before the hard
clip) is required. Tracked as a D-031 future safety item.

### Cross-References

- D-031: Formal decision mandating IIR protection filters
- D-029: Per-speaker-identity boost budget + mandatory HPF framework
- `docs/theory/design-rationale.md` "Driver Protection Filters: A Safety
  Requirement"
- `configs/speakers/identities/` -- `mandatory_hpf_hz` field in each identity
- S-007 lab note: CHN-50P config deployment with HPF verification

---

## 3. Measurement Safety

Near-field and room measurements send audio signals through the amplifier chain
to the speakers. The RT signal generator (`pi4audio-signal-gen`) provides all
measurement safety attenuation. CamillaDSP is no longer in the measurement
signal path (D-040).

### The S-010 Safety Incident (Historical)

On 2026-03-13, under the pre-D-040 architecture, a measurement test sent a
-20 dBFS sweep to the ALSA `sysdefault` device (128-channel fallback),
bypassing CamillaDSP entirely. The -40 dB safety attenuation was NOT in the
signal path. No speaker damage occurred because `sysdefault` did not route to
a physical output -- but the safety model was violated.

**Root cause:** The `sounddevice` library resolved the device name "default" to
`sysdefault` (ALSA) instead of the PipeWire default sink.

**Structural resolution (D-040):** This class of failure is eliminated. The
signal-gen is a native PipeWire stream -- there is no `sounddevice` library and
no ALSA device name ambiguity. The lesson still applies conceptually: verify
the signal reaches the intended destination.

**Full details:** `docs/lab-notes/change-S-010-measurement-test-failed.md`

### Measurement Safety Rules

1. **The RT signal generator must be the sole audio output path.** Measurement
   audio is produced by `pi4audio-signal-gen`, which enforces an immutable hard
   cap (`--max-level-dbfs`, default -20.0 dBFS) and per-sample `active_channels`
   isolation in the RT callback. Any measurement audio that bypasses the
   signal-gen bypasses all safety attenuation.

2. **Pre-flight checks must not be skipped for audio-producing measurements.**
   Verify that `pi4audio-signal-gen` is running and reachable on
   `127.0.0.1:4001` via `SignalGenClient.status()`. Verify PipeWire is at
   FIFO/88.

3. **Owner go-ahead required before each audio-producing command.** The owner
   must confirm that amplifiers are at a safe level and that the measurement
   microphone is positioned before any sweep or noise signal is played.

4. **Verify signal-gen hard cap at startup.** Confirm the signal-gen's
   `--max-level-dbfs` value via the RPC `status` response. The hard cap is
   immutable after startup (set from CLI flag, no runtime setter), so this is a
   startup verification rather than a per-measurement check.

### Measurement Attenuation Budget

The RT signal generator enforces safety attenuation at the source:

| Parameter | Value | Mechanism | Notes |
|-----------|-------|-----------|-------|
| Hard amplitude cap | -20 dBFS (immutable) | `safety.rs` `hard_clip()`, set via `--max-level-dbfs` CLI flag | Every sample clamped to 0.1 linear. Cannot be changed at runtime. |
| Active channel isolation | 0.0 on inactive channels | `generator.rs` `active_channels` bitmask in RT callback | Only the specified channel(s) receive signal; all others are silence. |
| Subsonic HPF | **Not present** | Known gap (D-031) | Safe at -20 dBFS (0.14W). Required if cap is ever raised. See Section 2 known gap. |

With a -20 dBFS sweep, the signal-gen output goes through GraphManager links
directly to the USBStreamer. The signal at the amplifier input is -20 dBFS,
delivering approximately 1.4W into a 4-ohm load (safe for all drivers in the
inventory).

**Power comparison with pre-D-040 architecture:** The old pipeline applied -20
dB in CamillaDSP on top of the -20 dBFS source signal, yielding -40 dBFS at
the amplifier (0.014W). The current pipeline delivers -20 dBFS directly to the
amplifier (1.4W) -- 100x more power. This is still safe: 1.4W into a typical
87 dB/W/m speaker produces approximately 88.5 dB SPL at 1 meter (moderate
conversation level). Operators should be aware that measurement SPL is higher
than under the previous architecture.

### Cross-References

- `src/signal-gen/src/safety.rs` -- hard amplitude cap implementation
- `src/measurement/signal_gen_client.py` -- SignalGenClient RPC interface
- `docs/architecture/rt-signal-generator.md` -- signal generator architecture
- `docs/lab-notes/change-S-010-measurement-test-failed.md` -- historical safety
  incident (pre-D-040, structurally resolved)
- `docs/lab-notes/change-S-013-chn50p-nearfield-measurement.md` -- first
  successful measurement (pre-D-040 architecture)

---

## 4. Gain Staging Limits (D-009)

**All correction filters must have gain <= -0.5 dB at every frequency.**

Room peaks are attenuated; nulls are left uncorrected. Target curves are
applied as relative attenuation (cut mid/treble relative to bass), not as
boost. Every generated filter is programmatically verified before deployment.

### Rationale

Psytrance source material at -0.5 LUFS leaves zero headroom for boost. Any
boost in the correction filter risks digital clipping at PA power levels.
The -0.5 dB safety margin ensures no frequency bin exceeds unity gain even
with measurement uncertainty.

### Cross-References

- D-009: Cut-only correction with -0.5dB safety margin
- `docs/theory/design-rationale.md` "Regularization" section

---

## 5. Measurement Pre-Flight Checklist

Before running any measurement that produces audio output, verify all of the
following. This checklist was compiled from lab notes documenting reliability
constraints discovered during system testing, updated for D-040 architecture
(AE sign-off 2026-03-21).

### Mandatory Checks (must pass before audio plays)

| # | Check | How to verify | Failure consequence |
|---|-------|---------------|---------------------|
| 1 | Web UI monitor service stopped (if using JACK backend) | `systemctl --user status pi4audio-webui-monitor` | F-030: SCHED_OTHER JACK client causes xruns under load. US-060 replaces JACK monitoring with PW-native data sources -- retire this check after US-060 validation. |
| 2 | Mixxx not running | `pgrep -x mixxx` | CPU competition, PipeWire resource contention |
| 3 | Signal generator running and reachable | Command #3 below the table | Measurement audio I/O unavailable. Signal-gen is the sole measurement output path (D-040). |
| 4 | PipeWire running at FIFO/88 | `chrt -p $(pgrep -x pipewire)` | Graph clock not real-time (F-020) |
| 5 | Correct PipeWire quantum for measurement mode | Command #5 below the table | Quantum affects convolver processing latency and CPU load. Measurement typically uses quantum 256 (live mode). |
| 6 | Signal-gen hard cap is -20 dBFS | Command #3 below the table -- check `max_level_dbfs` in response | Safety cap incorrect or missing. The -20 dBFS cap is immutable after startup but verify at pre-flight to confirm correct startup flag. |
| 7 | Signal-gen ports visible in PipeWire graph | Command #7 below the table | Signal-gen not registered as PW node. In managed mode, GraphManager creates links -- if ports are missing, no audio can flow. |
| 8 | No USBStreamer capture stream active (unless needed) | Command #8 below the table returns nothing (no output = pass). See the notes on check #8 | F-015: USB bandwidth contention between capture and playback streams on the USBStreamer. This applies to any capture on the USBStreamer, not only the `ada8200-in` adapter. No capture-plus-playback stability run has been done since D-040. |
| 9 | Owner confirmed amp level safe | Verbal/written confirmation | Transient/excursion damage risk |
| 10 | All 8 gains read 0.0 in PipeWire before amps on | After every boot and after any PipeWire or GraphManager restart: read the gain params from PipeWire itself (`pw-cli enum-params <pi4audio-convolver id> Props`, or `pw-dump`). Pass: `pw-dump` shows exactly one `pi4audio-convolver` node and exactly one `pi4audio-convolver-out` node, and that convolver node has exactly the 8 `gain_*:Mult` params `gain_left_hp`, `gain_right_hp`, `gain_sub1_lp`, `gain_sub2_lp`, `gain_hp_l`, `gain_hp_r`, `gain_iem_l`, `gain_iem_r`, all exactly 0.0, and all `Add` values 0.0. Do NOT use the web UI gate indicator (F-320) | Gains live with the gate showing CLOSED. No automated test covers gate-closed-at-boot (F-298, F-313). A second convolver node can be live while this node reads 0.0 (F-348). Any duplicate node, any missing or extra `gain_*` name, or any non-zero value: FAIL, amps stay off |

**Commands for checks #3, #5, #7 and #8.** These contain a shell pipe, so
they are kept out of the table: inside a Markdown table the pipe has to be
written as `\|`, and a command copied from the raw file with the backslash
still in it does not run as intended. For check #8 that would print nothing
and look like a pass. Copy the commands from this block:

```sh
# 3 and 6: signal generator status (6: check max_level_dbfs)
# Not yet verified on the NixOS image: nc may be missing, and -q1 is a
# Debian netcat option. If it fails, use:
#   bash -c 'exec 3<>/dev/tcp/127.0.0.1/4001; echo "{\"cmd\":\"status\"}" >&3; head -n1 <&3'
echo '{"cmd":"status"}' | nc -q1 127.0.0.1 4001

# 5: PipeWire quantum
pw-metadata -n settings | grep quantum

# 7: signal-gen node present
pw-cli ls Node | grep signal-gen

# 8: no capture node on the USBStreamer or ADA8200 (no output = pass)
pw-cli ls Node | grep -i -e ada8200 -e 'USBStreamer.*input'
```

**Notes on check #8:** The pcm-bridge and level-bridge captures attach to
PipeWire capture nodes (`ada8200-in` or the USBStreamer's ALSA input node),
so if command #8 finds no such node, no capture can be attached either. The
check is conservative: an idle capture node with no active stream also
fails it. That is intended (it fails safe). If it fails, find out what
created the node before going on. The NixOS image no longer deploys the ADA8200
capture adapter (`20-usbstreamer.conf`, F-295), so `ada8200-in` should be
absent unless someone started it by hand. As a result, Live-mode mic input
on the ADA8200 is currently not configured (F-323). The image does define a
`capture-usb` pcm-bridge that targets
`alsa_input.usb-MiniDSP_USBStreamer-00.pro-input-0` directly
(`production.nix`). It is suspected dead, but that is not verified (F-319).

**Check #10 applies beyond measurement:** run it before powering the amps
for any session, not only measurements (Section 10).

**Note:** The old check #9 (ALSA Loopback buffer adequate, F-028) has been
removed. D-040 eliminates the ALSA Loopback from the signal path -- PipeWire
native graph handles all audio routing. F-028 cannot recur.

### Source Lab Notes for Each Constraint

| # | Source |
|---|--------|
| 1 | `docs/lab-notes/change-S-005-stop-webui-xruns.md`, F-030. Retirement: after US-060 validation. |
| 2 | `docs/lab-notes/change-S-013-chn50p-nearfield-measurement.md` (attempt 1) |
| 3 | D-040 architecture. `src/signal-gen/src/safety.rs`, `docs/architecture/rt-signal-generator.md` |
| 4 | `docs/lab-notes/TK-039-T3d-dj-stability.md` (Phase 0), F-020 |
| 5 | D-040 (quantum is sole latency parameter). `docs/lab-notes/change-S-003-dj-mode-quantum.md` (historical) |
| 6 | D-040, D-009. `src/signal-gen/src/safety.rs` (hard cap implementation) |
| 7 | D-040. S-010 structural resolution. `src/signal-gen/src/main.rs` (PW stream registration) |
| 8 | F-015: `docs/lab-notes/F-015-playback-stalls.md` |
| 9 | CLAUDE.md "Safety Rules", Section 1 of this document |

---

## 6. PREEMPT_RT as a Safety Requirement

The system drives a PA capable of dangerous SPL through 4x450W amplifiers.
PREEMPT_RT is classified as a **hard real-time system with human safety
implications** (D-013).

A scheduling delay on a stock PREEMPT kernel has no formal worst-case bound. If
the audio processing thread misses its deadline, the result is a buffer
underrun -- a full-scale transient through the amplifier chain and a hearing
damage risk to anyone near the speakers.

PREEMPT_RT converts the Linux kernel to a fully preemptible architecture with
bounded worst-case scheduling latency. This transforms the system from
"empirically adequate" to "provably adequate" for hard real-time audio at PA
power levels.

### Cross-References

- D-013: PREEMPT_RT mandatory for production
- `docs/architecture/rt-audio-stack.md` Section 1: full PREEMPT_RT configuration

---

## 7. Runtime Gain Increase Safety (S-012)

**Never increase gain on any node in the live audio path without explicit
owner confirmation.** This applies whether the owner is monitoring on
headphones, in-ear monitors, or PA speakers.

### The S-012 Safety Incident

On 2026-03-17, during a Reaper live-mode investigation (CHANGE session C-005),
a worker changed the PW `linear` gain node Mult parameter from 0.001 (-60 dB)
to 0.0316 (-30 dB) — a +30 dB increase — without warning the owner. The
owner was actively monitoring on headphones at the time. No injury occurred,
but the incident demonstrated a gap in the safety rules: gain changes to live
audio paths were not explicitly listed as triggering actions requiring owner
confirmation.

**Full details:** `docs/lab-notes/change-C-005-live-mode-investigation.md`
(Finding 1)

### Runtime Gain Safety Rules

1. **Owner confirmation required before any gain increase.** Before increasing
   gain on any node in the audio path (volume, Mult, channelVolumes, or any
   parameter that increases signal level), explicitly inform the owner and wait
   for confirmation. This applies even for small increases (e.g., +3 dB).

2. **Gain decreases are safe.** Reducing gain (attenuation) does not require
   owner confirmation — it can only make the signal quieter, never louder.

3. **Applies to all gain mechanisms.** Including but not limited to:
   - `pw-cli s <node> Props '{ volume: ... }'`
   - `pw-cli s <node> Props '{ params: [ "Mult", ... ] }'`
   - `pw-cli s <node> Props '{ channelVolumes: [ ... ] }'`
   - Any PipeWire filter-chain parameter change that affects signal level

4. **No exceptions for "small" increases.** The safety margin depends on the
   current listening level, speaker thermal limits, and amplifier gain — none
   of which the worker can reliably assess remotely.

### Cross-References

- S-012 / TK-242: Safety incident
- `docs/lab-notes/change-C-005-live-mode-investigation.md` Finding 1
- CLAUDE.md "Safety Rules": Updated with gain-increase rule
- S-010: Prior near-miss (measurement bypass, different mechanism, same principle)

---

## 8. Web UI Gain Controls (US-065, Config Tab)

The Config tab shows per-channel gain sliders for the eight PipeWire
filter-chain `linear` builtin gain nodes (D-063: one per USBStreamer output,
channels 1-8). These are the same gain nodes used by the panic MUTE button
(F-040, below), the universal audio gate (Section 10), and the measurement
pipeline.

The sliders show the gain values read from PipeWire when the Config tab was
opened; they do not update on their own (reopen the tab to re-read). A
slider reading -INF does not prove silence: the value may be stale, or the
parameter may be missing (shown as a greyed-out row). A non-zero slider
while the gate shows CLOSED means the outputs were live when the tab was
opened: keep the amps off. Pre-flight check #10 (Section 5) is the
authoritative check.

**Interim (until US-159): the Config tab gain sliders are read-only in
practice.** Do not use Config tab gain Apply. It writes the gain nodes
directly, bypasses the D-063 gate, and the gate indicator keeps showing
CLOSED (Section 10, Rule 11; F-344).

| Ch | Gain node | Output |
|----|-----------|--------|
| 1 | `gain_left_hp` | Left main |
| 2 | `gain_right_hp` | Right main |
| 3 | `gain_sub1_lp` | Sub 1 |
| 4 | `gain_sub2_lp` | Sub 2 |
| 5 | `gain_hp_l` | Engineer headphone L |
| 6 | `gain_hp_r` | Engineer headphone R |
| 7 | `gain_iem_l` | Singer IEM L |
| 8 | `gain_iem_r` | Singer IEM R |

The "Output" column is the 2-way layout, the only one with IEM outputs. On
3-way profiles, ch 5-6 are speaker channels, ch 7-8 carry the engineer
headphones, and there is no IEM output (Section 10, "Headphone and IEM
Channels", Rule 3; F-342).

The gain nodes are builtins inside the filter-chain module. They are not
separate PipeWire graph nodes; they appear as prefixed parameters on the
`pi4audio-convolver` node (e.g. `gain_left_hp:Mult`). All eight default to
`Mult = 0.0` in `configs/pipewire/30-filter-chain-convolver.conf` (D-063 gate
closed at startup; by design, see Known Gaps in Section 10, F-298, F-348).
Operating values come from the active venue config and
are applied when the gate opens (Section 10).

### Two-Layer Gain Cap

| Layer | Cap | Mechanism | Bypass possible? |
|-------|-----|-----------|------------------|
| **Server hard cap** | Mult <= 1.0 (0 dB) | `config_routes.py` `GainRequest` validator + `min(mult, MULT_HARD_CAP)` before every `pw-cli` call | No — enforced on every API call regardless of client |
| **UI soft cap** | Mult <= 0.1 (-20 dB) | `config.js` slider max = 0.1 | Yes — a crafted API call can set Mult up to 1.0. This is by design: the hard cap at 0 dB prevents boost, the soft cap prevents accidental high-level output from the UI |

The server hard cap enforces D-009: no gain node in the pipeline may produce
net gain. Mult = 1.0 is unity (0 dB). Values above 1.0 are silently clamped
to 1.0. Values below 0.0 are rejected by the validator.

### Gain Increase Safety (S-012 Interaction)

The S-012 safety rule ("never increase gain without owner confirmation")
applies to **automated and SSH-based gain changes** — not to the owner using
the Config tab UI directly. When the owner adjusts a slider and presses Apply,
they are explicitly choosing to change the gain. However:

- The UI soft cap at -20 dB means casual slider adjustment cannot produce
  dangerous levels through the current amplifier chain
- The Apply/Reset workflow (dirty state tracking, explicit Apply button)
  prevents accidental gain changes from slider touches
- Workers and automated scripts MUST still follow S-012 for any `pw-cli`
  gain changes outside the owner's direct UI interaction

### Quantum Changes and Transient Risk

The Config tab allows runtime quantum changes via `pw-metadata`. Quantum
changes do NOT restart PipeWire and do NOT cause USBStreamer transients
(Section 1). The change takes effect on the next PipeWire graph cycle. The
UI shows a latency indicator (ms) for each quantum value so the operator
understands the impact.

### Panic MUTE Integration (F-040)

The MUTE button (always visible in the status bar) sets the Mult value of
every `gain_*` parameter on the convolver node to 0.0 (all eight channels;
`audio_mute.py` discovers them from `pw-dump`). Pre-mute values are stored in memory by
`AudioMuteManager`. UNMUTE restores the stored values. The MUTE operation
does NOT drop the PipeWire stream — this is critical for USBStreamer transient
safety (Section 1). The audio path remains connected; only the gain is zeroed.

### PROHIBITED: Setting Gains to Unity for Spectrum Viewing (owner directive 2026-03-25)

**Never set gain nodes to Mult = 1.0 (unity) to get a "full-scale" spectrum
display.** This was proposed as a workaround to see the true signal level at
post-gain tap points in the spectrum analyzer (US-080 Tap 2). The owner
explicitly rejected it as a safety risk.

**Why it is dangerous:**

Production venue operating gains (`configs/venues/production.yml`) attenuate
the speaker channels by 60-64 dB (Mult 0.001 = -60 dB mains, Mult 0.000631 =
-64 dB subs). Setting these to unity while speakers are connected would send
full-scale audio through the 4x450W amplifier chain. Even momentarily, this
can damage drivers and ears.

Headphone and IEM channels (5-8) already run at unity in the production
venue configs. Their hearing-safety rules are in Section 10.

**The safe alternative:** Display-side compensation. The spectrum analyzer
uses an auto-ranging Y axis (D-048) that adapts to the signal level at any
tap point. No gain changes are needed to see meaningful spectrum data at any
point in the signal chain. If absolute level reference is needed, the display
can add a computed offset (`20*log10(1/Mult)` dB) without touching the actual
gain. This was originally proposed as Option A (AE recommendation) and is
superseded by auto-ranging, but remains available as a future enhancement.

**Rule:** Gain values are set for speaker protection and system calibration.
They are NEVER adjusted for diagnostic or display convenience. If the
spectrum display is hard to read at a given tap point, fix the display — not
the gain.

### Cross-References

- D-009: Cut-only correction, -0.5 dB safety margin (hard cap basis)
- D-048: Auto-ranging Y axis supersedes gain compensation
- S-012: No gain increase without owner confirmation
- F-040: Panic MUTE/UNMUTE endpoint implementation
- US-065: Configuration Tab story
- US-080: Multi-Point Spectrum Analyzer (tap point selection)
- `src/web-ui/app/config_routes.py`: Server-side gain cap enforcement
- `src/web-ui/app/audio_mute.py`: MUTE/UNMUTE logic
- `src/web-ui/app/pw_helpers.py`: Shared PipeWire subprocess helpers

---

## 9. ALSA Device Lockout and Filter-Chain Watchdog (US-044)

**Threat model:** A process bypasses the PipeWire filter-chain convolver and
sends audio directly to the USBStreamer ALSA device. The audio reaches the
4x450W amplifier chain without crossover filtering, gain attenuation, or
driver protection -- risking speaker damage and hearing injury.

This threat is addressed by a four-layer defense-in-depth architecture.

### Layer 1: PipeWire Exclusive ALSA Hold

PipeWire's static playback adapter (`21-usbstreamer-playback.conf`) holds
the USBStreamer ALSA playback device open continuously. Any other process attempting
`open()` on the ALSA device node receives `EBUSY`. This is the primary defense
and blocks all bypass attempts while PipeWire is running.

The capture adapter (`20-usbstreamer.conf`, `ada8200-in`) is no longer
deployed by the NixOS image (F-295). Capture is not a bypass risk.

**Residual risk:** When PipeWire is stopped or restarting, the ALSA device is
momentarily available. Layer 2 covers this gap.

### Layer 2: udev Device Permissions

The udev rule `90-usbstreamer-lockout.rules` restricts USBStreamer ALSA device
nodes to `OWNER=ela MODE=0600`:

- **Locked:** `pcmC{X}D0p` (playback) and `controlC{X}` (mixer control)
- **Not locked:** `pcmC{X}D0c` (capture -- needed for measurement, no safety risk)

This ensures that even when PipeWire is down, only the `ela` user (who runs
PipeWire) can open the playback device. Other users and system services receive
`EACCES`.

**Residual risk:** A process running as `ela` can still open the device when
PipeWire is down. This is an accepted risk -- the `ela` user is the operator.

### Layer 3: WirePlumber Node Deny Policy

The Lua policy script `deny-usbstreamer-alsa.lua` (loaded by
`53-deny-usbstreamer-alsa.conf`) monitors all PipeWire node creation events.
Any node targeting the USBStreamer ALSA device that is not a whitelisted static
adapter (`ada8200-in`, `alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0`)
is immediately destroyed via `node:request_destroy()`.

This catches edge cases where a PipeWire client (e.g., `pw-cli`, a misbehaving
application) creates an unauthorized node targeting the USBStreamer within the
PipeWire graph.

**Residual risk (D-065):** Layer 3 destroys rogue *nodes*; it does not stop
WirePlumber from creating *links*. D-065 removed `90-no-auto-link.conf`, so
WirePlumber's standard linking policy is active again. The remaining
anti-link measures are `node.autoconnect = false` and GraphManager's
reconciler cleanup. `node.autoconnect = false` on a sink only stops that
node from linking itself: if a sink is the default sink, WirePlumber's
default policy is expected to auto-link other streams to it. That is
expected from WirePlumber's default policy but not yet confirmed on the Pi
(F-318, amps-off test pending). Such a link bypasses the filter-chain and
the gate. Interim operator rule: Section 10, Rule 9.

### Layer 4: Filter-Chain Watchdog (T-044-4)

The GraphManager's watchdog (`src/graph-manager/src/watchdog.rs`) continuously
monitors 2 critical nodes in the PipeWire graph (`MONITORED_NODES`):

| Node | Role |
|------|------|
| `pi4audio-convolver` | Filter-chain capture side |
| `pi4audio-convolver-out` | Filter-chain playback side |

The eight gain builtins (Section 8) are not monitored separately. They are
parameters on `pi4audio-convolver`, so they cannot disappear independently
of it. They are the watchdog's mute target, not part of its monitored set.

If ANY monitored node disappears from the PipeWire graph, the watchdog
triggers a **latched safety mute**:

**Primary mute mechanism:** Set `Mult=0.0` on all 8 gain parameters
(`GAIN_PARAM_NAMES`) on the convolver node via native PipeWire API
(`pw_node_set_param` via `pipewire-rs` FFI). Target response time: <1ms per
param, <8ms total.

**Fallback mechanism:** If the convolver node itself is gone (no node to set
params on), the watchdog destroys ALL links to the USBStreamer input ports
using `pw_registry::destroy_global()`.

**Gate interaction (D-063):** Both the primary and the fallback mute close
the universal audio gate (Section 10).

**Latch behavior:** Once triggered, the mute is LATCHED -- it stays active
even after the missing nodes return. Unlatching requires an explicit RPC
command (`watchdog_unlatch`). This prevents transient audio during graph
recovery. Pre-mute gain values are stored and restored on unlatch.
**Caution:** unlatch restores those gains immediately, without a ramp, and
leaves the gate state CLOSED, so audio is live while the gate reads closed
(F-320-D). Unlatch is not a safe recovery path; see Section 10, rule 5.

**Gain integrity check (T-044-5):** `src/graph-manager/src/gain_integrity.rs`
polls the gain parameters via `pw-dump` every 30 s. If any Mult is above 1.0
(amplification), it triggers the same safety mute and closes the gate. This
is a control-plane check (30 s interval), not part of the <21ms watchdog
path.

**Response time budget:** <21ms (1 PipeWire graph cycle at quantum 1024).
Registry events are push-based (not polled), so the watchdog fires within
the same PW main loop iteration that processes the node removal event.

**RT scheduling:** The GraphManager runs at SCHED_FIFO priority 80 (set via
systemd `CPUSchedulingPolicy=fifo` / `CPUSchedulingPriority=80`). This is
below PipeWire (FIFO/88) but above all non-audio processes, guaranteeing the
watchdog's mute path meets its <21ms deadline even under CPU contention.

### Defense Layer Summary

| Layer | Mechanism | Blocks | When PW down? | Config |
|-------|-----------|--------|---------------|--------|
| 1 | PipeWire exclusive ALSA hold | All non-PW processes | No | `21-usbstreamer-playback.conf` |
| 2 | udev OWNER/MODE | Other users, system services | Yes | `90-usbstreamer-lockout.rules` |
| 3 | WirePlumber node deny | Rogue PW client nodes | N/A (WP requires PW) | `53-deny-usbstreamer-alsa.conf` |
| 4 | GraphManager watchdog | Convolver node loss; gain Mult > 1.0 (integrity check) | N/A (GM requires PW) | `src/graph-manager/src/watchdog.rs`, `gain_integrity.rs` |

### Cross-References

- US-044: ALSA device lockout user story
- T-044-1: udev rules + PipeWire exclusive hold
- T-044-2: WirePlumber deny policy
- T-044-3: GraphManager link audit
- T-044-4: Filter-chain watchdog
- T-044-5: Gain integrity check
- D-065: WirePlumber `90-no-auto-link.conf` removed; F-318: WirePlumber auto-link
- `configs/udev/90-usbstreamer-lockout.rules`
- `configs/wireplumber/53-deny-usbstreamer-alsa.conf`
- `configs/wireplumber/scripts/deny-usbstreamer-alsa.lua`
- `src/graph-manager/src/watchdog.rs`
- `src/graph-manager/src/gain_integrity.rs`

---

## 10. Universal Audio Gate (D-063, US-113)

**No signal reaches any USBStreamer output until the operator explicitly
opens the audio gate** (by design; see Known Gaps, F-298, F-348). This
applies to every venue and every mode. Since D-063 (owner decision
2026-03-30; owner reconfirmation pending, O-10), all eight output channels
(mains, subs, engineer headphones, singer IEM) pass through the
filter-chain convolver and its eight gain nodes (Section 8). Channels 5-8
use Dirac (identity) coefficients. The gate controls all eight.

### How the Gate Works

| State or event | What happens | Source |
|----------------|--------------|--------|
| PipeWire start (boot, PW restart) | All 8 gain nodes load `Mult = 0.0` from `30-filter-chain-convolver.conf` (by design; see Known Gaps, F-298, F-348) | `configs/pipewire/30-filter-chain-convolver.conf` |
| GraphManager start | Gate state is CLOSED. The persisted or default venue is loaded as *pending* gains only | `src/graph-manager/src/main.rs` |
| Venue selected (gate closed) | New gains become pending. Nothing is applied to PipeWire | `set_venue` RPC |
| Gate opened | Pending venue gains are written to the 8 gain nodes. Refused if no venue is loaded | `open_gate` RPC, `POST /api/v1/venue/gate/open` |
| Gate closed | All 8 gain nodes set to `Mult = 0.0` | `close_gate` RPC, `POST /api/v1/venue/gate/close` |
| Automatic close | Standby transition, watchdog mute (Section 9), gain integrity violation (Section 9) | `main.rs`, `registry.rs` |

**Gate opening is currently a step, not a ramp.** D-063 specifies a 3 s,
30-step cosine ramp-up. The current implementation computes all 30 steps
within a single PipeWire main-loop iteration, so PipeWire applies only the
final value: in practice the gains jump straight to the venue values in one
graph cycle. Tracked as F-315. Until it is fixed, treat gate open as an
instant step to full venue gain.

**The gate indicator shows GraphManager's state, not the actual gains.**
Until F-320-D, F-320-E and F-320-F are fixed, the indicator can read CLOSED
while audio is live:

- after a watchdog unlatch (F-320-D): unlatch restores the stored gains
  immediately, without a ramp, and leaves the gate state CLOSED;
- after a GraphManager restart (F-320-E): GraphManager starts with the gate
  CLOSED but does not write the gains, so PipeWire keeps whatever values it
  had (GraphManager restarts automatically on failure);
- after UNMUTE (F-320-F): see "MUTE is not the gate" below.

**MUTE is not the gate.** The panic MUTE button (Section 8) zeroes the gains
but does not change the gate state, and it is not latched against the gate.
Opening the gate or changing venue re-applies gains even while MUTE shows
active. UNMUTE restores the pre-mute gains regardless of gate state, with no
ramp (F-320-F).

### Rules for Opening the Gate

1. **Check the venue before opening.** Confirm the active venue name and its
   per-channel gains in the web UI before pressing open. The gate applies
   whatever venue is pending.
2. **First boot: foh-passthrough has no driver protection.** On first boot
   the default venue is `foh-passthrough`: unity gain on all 8 channels and
   no driver protection on channels 1-4 (`dirac.wav`). Until F-271 is
   resolved, do not open the gate with `foh-passthrough` loaded while the PA
   amps are on. Select a venue with protection filters first, or keep the
   amps off.
3. **Never change venue while the gate is open (interim, F-314).**
   A venue change with the gate open applies the new gains immediately, with
   no ramp and no confirmation. Switching from `production` to
   `foh-passthrough` is a +60/+64 dB jump into the 4x450W amplifiers with
   Dirac on channels 1-4. Procedure: close the gate, apply the venue, verify
   the venue detail, then reopen.
4. **Live mode: IEM at minimum before opening.** Before opening the gate in
   Live mode, the singer's earpieces must be out or the IEM pack volume must
   be at minimum. Bring the IEM level up from minimum with the singer
   present and agreeing.
5. **Watchdog unlatch: amps off first** (interim, F-320-D). Unlatch
   restores the venue gains instantly, so the outputs are live at full venue
   level from that moment, even though the indicator still reads CLOSED.
   Closing the gate afterwards is too late. Order:
   1. Amps off (or amp gains down), and IEM earpieces out or the IEM pack at
      minimum.
   2. Unlatch the watchdog. There is no web UI control for this yet
      (CLEAR WATCHDOG arrives with US-159). It is the GraphManager RPC
      `watchdog_unlatch` on `127.0.0.1:4002`, so it needs a shell on the Pi:
      the owner over SSH, or a team member in a CHANGE session granted by the
      Change Manager. Not yet verified on the NixOS image (`nc` may be
      missing, and `-q1` is a Debian netcat option): try
      `echo '{"cmd":"watchdog_unlatch"}' | nc -q1 127.0.0.1 4002`, and if
      that fails, the bash-only form (same caveat)
      `bash -c 'exec 3<>/dev/tcp/127.0.0.1/4002; echo "{\"cmd\":\"watchdog_unlatch\"}" >&3; head -n1 <&3'`.
      Success is a reply containing `"ok":true`. If both fail, the
      watchdog stays latched and the outputs stay muted. That is the safe
      state: do not improvise, leave the amps off and fix it later.
   3. Close the gate. The web UI CLOSE GATE button does not work here: it is
      greyed out while the indicator reads CLOSED, which is the case after an
      unlatch (F-338). Press panic MUTE in the status bar, then close the gate with
      `POST /api/v1/venue/gate/close` from the engineer's device
      (`curl -k -X POST https://<pi>:8080/api/v1/venue/gate/close`). This
      is the primary path. In a shell on the Pi, the GraphManager RPC
      `echo '{"cmd":"close_gate"}' | nc -q1 127.0.0.1 4002` also works if
      `nc` is present (not yet verified on the NixOS image); if it fails,
      use the curl command. MUTE stores the live gains as "pre-mute", so a later UNMUTE
      brings them back (Rule 7).
   4. Verify the venue (Rule 1) and run pre-flight check #10 (Section 5).
   5. Amps back on, then open the gate per Rules 1-4.
6. **After any GraphManager restart** (crash, redeploy, service restart),
   **treat every output as live** (interim, F-320-E). Keep the amps off
   during the restart (Rule 9), close the gate as in Rule 5 step 3 (panic
   MUTE, then the REST or RPC close; the CLOSE GATE button is greyed out
   while the indicator reads CLOSED), and run pre-flight check #10
   (Section 5) before assuming the outputs are silent.
7. **Never use UNMUTE** (interim, F-320-F). UNMUTE restores the pre-mute
   gains instantly, whatever the gate state. To recover from MUTE: amps off,
   close the gate as in Rule 5 step 3 (if the indicator reads CLOSED, the
   CLOSE GATE button is greyed out, so use the REST or RPC close), run
   pre-flight check #10, then amps on and open the gate per Rules 1-4. If
   someone has already pressed UNMUTE, treat the outputs as live
   immediately.
8. **No shared network at any time (interim, F-037).** The web UI has no
   authentication: anyone on the network can open the gate, select
   `foh-passthrough` and raise gains. This works while the amps are off
   too: the state persists, and the outputs go live when the amps come on.
   Until F-037 is fixed, do not connect the Pi to a network other people
   can join at any time during setup or the show; use a network only the
   engineer's device is on, or restrict port 8080 to that device. If the Pi
   has been on such a network, treat every output as live and recover in
   this order:
   1. Disconnect the Pi from that network, or apply the port 8080
      restriction. Otherwise someone can undo the recovery right after it.
   2. Amps off, then close the gate as in Rule 5 step 3.
   3. Verify the venue (Rule 1) and run the coefficient check (Rule 10). A
      venue switch survives closing the gate, and the next open applies it.
   4. Check that no measurement or signal-gen playback is running or
      queued (signal-gen status, command #3 in Section 5: not playing). It
      would play into the amps when they come on; the -20 dBFS cap still
      allows a loud signal on 450 W amps.
   5. Run pre-flight check #10, then amps on, then open the gate per
      Rules 1-4.

   Never press UNMUTE during this recovery (Rule 7): if someone pressed
   MUTE at raised gains, those gains are stored as pre-mute.
9. **With amps on, run no other audio on the Pi** (interim, F-318). Only
   Mixxx or Reaper via `pw-jack`, the signal generator and the measurement
   tools. No browser audio, no desktop sounds, no PulseAudio or ALSA-plugin
   applications. WirePlumber may link such a stream straight to the
   USBStreamer, with no crossover, no D-031 protection, no gate and no gain
   stage (Section 9, Layer 3). Keep the amps off while GraphManager restarts,
   because its link audit is not running then.
10. **Confirm the coefficient files match the venue before opening the gate
    with amps on** (interim, F-321). GraphManager does not load a venue's
    `coefficients` on a venue switch; it changes gains only. Several venues
    use the same filenames (`combined_*.wav`), and the image seeds those
    files as Dirac copies when no venue-specific files are present. So the FIR filters actually running may not be
    the ones the venue was designed for. For example,
    `markaudio-ultimax-200hz` on the wrong filters puts bass into the 7 W
    CHN-50P: on 80 Hz crossover files the driver is inside the D-031
    floor, but gets far more power below the 157 Hz box Fc than it was
    budgeted for; on Dirac files it has no highpass at all. The check needs a shell on the Pi (the owner over SSH, or a
    team member in an OBSERVE session granted by the Change Manager):
    - Compare `sha256sum /etc/pi4audio/coeffs/*.wav`. If any
      `combined_*.wav` matches `dirac.wav`, there is no crossover or driver
      protection on that channel: amps stay off.
    - Otherwise, compare the checksums against those recorded when the
      venue's filter set was generated (for the Markaudio rig, US-155 AC4).
    - No such record exists yet. If you cannot confirm the set, keep the
      amps off.
11. **Gate bypass** (interim, until GraphManager is the sole Mult writer,
    US-159; F-344, F-345). CLOSED does not guarantee silence. Besides
    UNMUTE (Rule 7), two web UI paths write non-zero Mult without
    GraphManager: Config tab gain Apply, and the thermal limiter, which
    restores gain toward the profile gain as the coil cools if it was
    limiting when the gate closed.
    - Never use Config tab gain Apply.
    - To make the outputs safe, turn the amps off; do not rely on CLOSE
      GATE alone.
    - Until US-159, after any gate close, pass pre-flight check #10
      (Section 5) before the amps go on, whatever the gate indicator shows
      and whether or not you used Config tab gain Apply or saw the thermal
      limiter active (dashboard LIMIT, WARN or a LIM x.x dB badge).

Watchdog mute, gain-integrity mute, and the standby transition all close the
gate. Watchdog unlatch and UNMUTE are **not** safe recovery paths.

### Headphone and IEM Channels (5-8)

This section describes the 2-way layout. On 3-way profiles, ch 5-6 are
speaker channels and ch 7-8 carry the engineer headphones (Rule 3 below).

The engineer headphone (5-6) and singer IEM (7-8) channels run at unity
gain (Mult 1.0, 0 dB) in the `production` and `markaudio-ultimax-200hz`
venue configs. A full-scale digital signal reaches those outputs without
attenuation. The level at the ear is set only by:

- the source fader (Reaper or Mixxx), and
- the headphone amplifier or IEM transmitter gain.

The server hard cap (Mult <= 1.0, Section 8) does not protect these
channels: unity is within the cap.

**Rules:**

1. S-012 (Section 7) covers channels 5-8: no gain increase on headphone or
   IEM channels (venue gain, Mult, or source-side routing changes) without
   owner confirmation, and for IEM also the singer's confirmation.
2. The IEM-at-minimum rule in "Rules for Opening the Gate" applies every
   time the gate is opened in Live mode.
3. **With a 3-way speaker profile active: no Live mode, and nothing
   connected to ADA8200 outputs 7-8 except engineer headphones** (interim,
   F-342). 3-way profiles use six speaker channels, so the 8-channel
   convolver has no room for IEM channels. On 3-way, DJ mode routes the
   headphone feed to outputs 7-8 by design, and in Live mode the headphone
   feed would land on the IEM outputs. The profiles allow DJ and standby
   only (D-054 `mode_constraints`), but GraphManager does not enforce this.

**Open item:** The headphone and IEM chain (ADA8200 output → IEM
transmitter → earpieces) has not been measured. No SPL or dBFS limit can be
stated yet. Measuring the chain and deciding on a per-channel soft cap or
limiter for channels 5-8 is owner decision O-11 ("Owner Decisions Pending"
in `docs/project/status.md`).

### Known Gaps

| Gap | Effect | Interim rule | Tracking |
|-----|--------|--------------|----------|
| Ramp not temporal | Gate open is an instant step to venue gain | Treat gate open as a step | F-315 |
| Hot venue switch | Venue change with gate open applies new gains instantly | Rule 3: close gate before venue change | F-314 |
| No D-031 protection in `foh-passthrough` | Full-range signal on mains and subs once gate is open | Rule 2: amps off or protected venue | F-271 |
| Unlatch leaves gate CLOSED with gains live | Indicator reads CLOSED while audio flows | Rule 5 | F-320-D |
| GraphManager restart does not write gains | Indicator reads CLOSED while PipeWire keeps venue gains | Rule 6 | F-320-E (no automated test, F-313) |
| MUTE/UNMUTE independent of the gate | Gains re-applied while MUTE shows active; UNMUTE bypasses gate | Rule 7 | F-320-F |
| CLOSE GATE button disabled while the gate reads CLOSED | The UI cannot close the gate in the F-320 states, where it matters most | Rules 5-7: panic MUTE, then REST or RPC close | F-338 |
| Live mode not refused on 3-way profiles | Headphone feed on the IEM outputs ch 7-8 | HP/IEM Rule 3: never select Live mode on a 3-way profile; only engineer headphones on outputs 7-8 | F-342 |
| Gate bypass by web UI Mult writers | Config tab gain Apply and the web UI thermal limiter write Mult bypassing the gate; GraphManager gain integrity checks only > 1.0 and never re-zeroes | Rule 11 | US-159 (sole writer, reduce-only limiter); F-344, F-345 |
| Profile activation writes an unsafe PipeWire config | Speaker-profile ACTIVATE (2-way included), DEPLOY TO PI and the room-correction wizard's "Install PW config" step write a generated config to `~/.config/pipewire/pipewire.conf.d/30-filter-chain-convolver.conf` with profile-gain Mult defaults and no ch 5-8 (from the code, not verified on the Pi); after the next PipeWire restart the outputs are live while the gate shows CLOSED, and the wizard's own "Reload filter-chain" step may make this happen at once; on non-2-way profiles close cannot reach the gains | Do not use ACTIVATE, DEPLOY TO PI or the wizard deploy; no non-2-way profile with the amps on; before any PipeWire restart, check that `~/.config/pipewire/pipewire.conf.d/30-filter-chain-convolver.conf` does not exist (if it does, the amps stay off after the restart); pre-flight check #10 before amps on after every PipeWire restart | F-348; US-159 G12/G13 |
| Coefficient reload bypasses the gate | RELOAD FILTERS, the room-correction wizard's "Reload filter-chain" step and `POST /reload-pw` swap coefficients in place with no gate check and no validation, probably on one channel only, and report success | Do not use RELOAD FILTERS, the wizard reload or `POST /reload-pw`; activate new filters by a PipeWire restart (Section 1: warn the owner first) with amps off, headphones off and IEM out or at minimum, then Rules 1 and 10 and pre-flight check #10 before anything goes back on | F-346; US-159 G8c |
| Close reports success without proof | `close_gate` returns ok without verifying, even if no gains were written (convolver node missing) | Rules 5-7 end with pre-flight check #10 | F-339 |
| No persisted gate state | D-063's `active.yml` `audio_enabled` field is not implemented; the gate exists only in GraphManager memory | Rules 5-6 | F-320-G |
| Web UI has no authentication | Anyone on the network can open the gate, change venue and raise gains | Rule 8 | F-037 (Critical) |
| HP/IEM chain not measured | No SPL limit can be stated for channels 5-8 | HP/IEM rules above | O-11 |
| Gate-closed-at-boot not verified by automated tests | A conf change or first-boot regression that leaves gains non-zero would pass CI | Pre-flight check #10 (Section 5) after every boot, before amps on | F-298, F-313 |
| WirePlumber may auto-link non-JACK streams to the USBStreamer (D-065) | Unfiltered, ungated full-scale signal into the amps | Rule 9 | F-318 |
| Venue coefficients not loaded on venue switch | Running FIR may not match the venue (e.g. no crossover into the CHN-50P) | Rule 10 | F-321 |
| Per-speaker thermal and excursion ceilings not enforced | Nothing stops a venue gain above a speaker's safe limit (the CHN-50P is rated 7 W, -18.1 dB re 450 W) | With the CHN-50P, use only AE-reviewed venues and never `foh-passthrough` (Rule 2) | F-322 |

### Cross-References

- D-063: 8-channel convolver with universal audio gate
- US-113: Venue config, first-boot active config, gate implementation
- D-031: Mandatory driver protection filters (Section 2)
- D-009: Gain hard cap (Section 8)
- S-012: No gain increase without owner confirmation (Section 7)
- F-271: D-031 protection filters for `foh-passthrough`
- F-314: Hot venue switch with gate open applies gains instantly
- F-315: Gate-open cosine ramp collapses to an instant step
- F-320: Gate state not authoritative (D: unlatch, E: GM restart, F: MUTE/UNMUTE, G: `audio_enabled`)
- F-037: Web UI has no authentication
- F-298: D-063 gate test integrity (gate-closed E2E test swallows its assertion)
- F-313: Orphaned gate conf test and unwired GraphManager restart test
- F-318: WirePlumber default-sink auto-linking (D-065)
- F-321: Venue coefficients not loaded on venue switch
- F-322: Per-speaker thermal and excursion limits not enforced
- F-338: CLOSE GATE button disabled while the gate reads CLOSED
- F-339: Gate close reports success without verifying the gains
- F-342: GraphManager does not enforce D-054 `mode_constraints` on `set_mode`
- F-344: Config tab gain Apply writes Mult directly, bypassing the gate
- F-345: Thermal limiter restores Mult while the gate is closed
- F-346: Coefficient reload (`POST /reload-pw`) bypasses the gate
- F-348: Generated filter-chain configs remove the D-063 boot gate
- `src/web-ui/app/audio_mute.py`: MUTE/UNMUTE (independent of the gate)
- `configs/venues/`: Venue gain configs
- `src/graph-manager/src/main.rs`: Gate open/close and venue handling
- `src/web-ui/app/venue_routes.py`: Gate REST endpoints

---

## Summary of Safety Decisions

| Decision | Summary | Section |
|----------|---------|---------|
| D-009 | Cut-only correction, -0.5 dB safety margin | 4, 8 |
| D-013 | PREEMPT_RT mandatory for production | 6 |
| D-029 | Per-speaker boost budget + mandatory HPF framework | 2 |
| D-031 | IIR Butterworth HPF in all production configs | 2 |
| S-012 | No gain increase without owner confirmation | 7, 8 |
| F-040 | Panic MUTE sets gain to 0.0 without dropping PW stream | 8 |
| US-044 | Four-layer ALSA lockout + watchdog defense | 9 |
| D-063 | 8ch convolver; universal audio gate, all outputs muted at boot (by design; see Known Gaps, F-298, F-348) | 8, 9, 10 |

## Safety Incident Register

| Date | Session | Summary | Outcome | Lab Note |
|------|---------|---------|---------|----------|
| 2026-03-13 | S-010 | Sweep bypassed CamillaDSP via sysdefault ALSA device | No damage (sysdefault not routed to physical output) | `change-S-010-measurement-test-failed.md` |
| 2026-03-17 | S-012 | +30 dB gain increase on live path while owner monitoring on headphones | No injury. New rule: never increase gain without owner confirmation | `change-C-005-live-mode-investigation.md` |
