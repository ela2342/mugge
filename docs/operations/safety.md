# Safety Operations Manual

This document is the single authoritative reference for all safety constraints
on the Pi audio workstation (the Raspberry Pi 5 since 2026-10-24; sections
written for the Pi 4B still apply unless the Pi 5 section below says
otherwise). Every team member -- human and automated --
must follow these rules. CLAUDE.md points here; architecture docs cross-reference
here.

**Scope:** Physical safety of speakers, amplifiers, and human hearing. This is
not about data loss or software correctness -- it is about preventing hardware
damage and hearing injury.

---

## Pi 5 Platform Status (US-163)

The Pi 5 (`ela@192.168.178.89`) runs a **bootstrap/dev image. It is NOT
gig-capable.** Evidence: `docs/lab-notes/US-163-pi5-bootstrap.md`.

**No amps, headphones or IEM, and no signal-gen measurement use,** until
every Pi 5 row of the AMPS-ON PRECONDITION LIST (Pi 5) below holds. The
PM keeps the list in the backlog, using the same item numbers; if the
backlog adds an item, this table must be updated too. The list has 17
rows: 1-14 and 19-21 (rows 15-18 are reserved for the US-174d PR, not
merged yet). On the Pi 5, rows 1-3, 5-14 and 19-21 must ALL hold; row 4
applies to the Pi 4 only. For a defect row, "holds" means the defect is
closed and its fix verified on the Pi 5, unless the row itself names an
alternative (rows 14 and 21).

| # | Item | What must hold, and why |
|---|------|-------------------------|
| 1 | Owner | The owner re-confirms amps-on, and the Section 5 pre-flight (with S-012, Section 7) passes |
| 2 | F-341 AC3 | The pre-flight `nc` commands (Section 5, checks #3 and #6) are verified on the Pi 5 NixOS image. Until then, no signal-gen measurement session on the Pi 5 |
| 3 | US-172 | The HiFiBerry block is back to three working layers: layer (a) (`force_eeprom_read=0`) is verified to take effect, or the AE re-rules. The two-layer state is accepted only while nothing is connected to the HAT output (see "Outputs" below) |
| 4 | US-170 | Pi 4 only (N/A on the Pi 5): the F-358 runtime check on the Pi 4 before any Pi 4 audio use |
| 5 | F2 | Metering bridge nodes come back after a PipeWire restart. Until then, the F2 rule below |
| 6 | F-037 | Web UI on 8080 has no authentication. It is open on the LAN by owner ruling, accepted only while nothing is connected to any Pi output |
| 7 | F-361 | The link audit protects only ports named `playback_AUX0..7` |
| 8 | F-373 | After a USB re-enumeration the USBStreamer sink recovers without a PipeWire restart. The fix is re-tested with a physical replug: afterwards the USBStreamer hardware mixer reads no higher than before, all 16 gain values are 0, read as in "Gains at boot" (node state logged, F-395) and the gate is closed (AE) |
| 9 | F-317, F-318, F-352, F-354, F-355 | RT throttle off with no watchdog backstop (F-317); non-JACK streams may auto-link to the USBStreamer (F-318); the gain API can pass a NaN Mult (F-352) or splice a name into a command (F-354); the thermal limiter can latch a NaN level (F-355) |
| 10 | Thermal soak | A 60-minute flight-case thermal soak passes (passive cooling only, see "Thermal" below) |
| 11 | F-372 | The S-001 path check is a string-prefix test, and the profile name is not sanitised |
| 12 | RTTIME | A PipeWire RT overrun is SIGKILLed with no warning first (see "Unannounced PipeWire kill" below) |
| 13 | US-159 G16 (F-373) | Any re-adoption of the USBStreamer sink after a re-enumeration (by GraphManager or WirePlumber) comes up gated: gains 0, gate closed, and audio returns only when the operator re-opens the gate (an instant step to the venue gain, F-315; there is no ramp). To be tested (AE; US-159 T65) |
| 14 | Gate-authority defects (AD M4) | F-338, F-339, F-320, F-314, F-325 and F-349 are closed, or each has an interim operating rule in the merged safety.md (planned in PR #45, paused since 2026-10-26; until it merges, the rules in this row and in the Pi 5 rules below apply) that is followed. For F-314, F-349, F-338 and F-339 the interim rule must be AE-accepted. For F-338 and F-339 it must not rely on the web-UI Close Gate or on a CloseGate success reply: the emergency stop is the amp power switches (including the HP/IEM amps); a person at the switches the whole time the amps are on. After any gate close, mute or GraphManager restart, reading the gains does not prove "muted" yet. Switch the amps off, including the headphone/IEM amps, and headphones/IEMs not worn, and keep them off until PipeWire is restarted or the Pi is cold power-cycled, with all 16 gains verified at their boot values (safety.md, Gains at boot) and the gate closed. A gains reading counts only if the filter-chain node and its output node were idle or running immediately before and after the reading (states logged with it); a reading on a suspended node shows 0 whatever the real gain is and proves nothing (F-395, Gate-2 r6b). Once the live readback is proven on the Pi, this goes back to: "muted" is proven only by all 16 gains reading exactly 0.000000 via `pw-cli enum-params` on a node that is idle or running. That interim covers supervised sessions only; before any gig or unattended use, F-338 and F-339 are closed. For any own-speaker venue (e.g. CHN-50P), F-321 and F-322 are also closed |
| 19 | F-465 | F-465 fixed and AC3 b-e passed on that generation; see F-465 rule |
| 20 | F-410, F-320 D | While the D-063 gate is closed, no action other than Open Gate raises any Mult: the web UI unmute never restores gains behind a closed gate (F-410, closes with the F-439 / F-320 F PR), and the GM watchdog unlatch writes no Mult (F-320 D). Both must be fixed; no interim operating rule counts; AE acceptance required |
| 21 | F-348 | No generated filter-chain conf can bring the gains up behind a closed gate. A generated conf writes the venue gains as its Mult defaults, and they take effect at the next PipeWire restart (F-348). Holds when F-348 is closed, or when the F-348 rule below is followed. Row 14's interim alternative does not cover F-348 |

Until the list is closed, these rules apply on the Pi 5:

- **F2 rule:** after any PipeWire restart, restart pcm-bridge and
  level-bridge and confirm live meters before any amp goes on.
- **Unannounced PipeWire kill:** `RLIMIT_RTTIME` is 200 ms soft and hard
  (F-358), so a runaway RT loop gets PipeWire SIGKILLed with no SIGXCPU
  warning first. An unannounced PipeWire SIGKILL or restart is a
  USBStreamer interruption (Section 1). Follow the F2 procedure (restart
  pcm-bridge and level-bridge, confirm live meters) before amps on.
- **F-373 rule (USB glitch = silent output):** if the USBStreamer drops
  off the USB bus and comes back (a cable bump, a replug, a hub or power
  glitch), PipeWire does not reopen it. The output stays silent, the sink
  still shows "running", and nothing else signals a fault. Do NOT raise
  any gain to compensate: not in the software, not on the USBStreamer
  mixer, and not on the amplifier knobs. Recovery is a PipeWire restart,
  which is itself a USBStreamer interruption (Section 1): amps off first,
  and headphones/IEM off and not worn, then the F2 procedure. Before amps
  on, check all gains as in "Gains at boot" below (a reading on a
  suspended node proves nothing, F-395), check that the gate is closed,
  and that the amp knobs are back at their staged positions; then re-open
  the gate the normal way (an instant step to the venue gain, F-315).
- **F-318 rule (no auto-routing, no hand-made links):**
  - *Expected message.* WirePlumber never links a playback stream to any
    output. `pw-play` and `paplay` get "no target node available" and
    exit; a browser plays nothing. This is expected, not a fault. To
    confirm, run `journalctl --user -u wireplumber | grep F-318` and look
    for `F-318: denied auto-link of stream`.
  - *How to make sound.* Use the web UI Test tab (signal-gen), Mixxx in
    DJ mode or Reaper in Live mode. GraphManager makes their links. The
    Test tab is the only sanctioned way to check the speakers (amps stay
    off until the AMPS-ON list holds; until then the test signal proves
    the digital path only, not the speakers).
  - *Never create or remove links by hand.* Not with `pw-link <out> <in>`,
    not with `pw-link -d`, not with `jack_connect`, not with a patchbay
    (qpwgraph, Helvum).
    GraphManager owns every link. On all 8 USBStreamer playback ports
    (`playback_AUX0..7`: speakers AND headphones/IEM, D-063) the only
    allowed source is `pi4audio-convolver-out`. Any other link into the
    USBStreamer bypasses the crossover, the D-063 gains and the gate.
    Full-scale audio then goes straight to the amplifiers or the in-ear
    monitors, with no protection against speaker damage or hearing
    damage.
  - *Apps cannot change their own links (US-173).* Mixxx, Reaper and
    every other JACK app run with `jack.self-connect-mode =
    ignore-external`. When an app connects one of its ports to another
    app's or device's port, the call does nothing and still reports
    success, so the app cannot route itself around the crossover.
    GraphManager makes all links instead. On PipeWire 1.6.2 the same
    holds when an app removes a link: changing the sound hardware or
    the outputs in Mixxx or Reaper does not silence the output: audio
    keeps flowing through the GraphManager links, or resumes as soon as
    GraphManager re-links the app. Never use an app's audio settings
    to silence the output: use the app's own volume or master fader,
    and in an emergency the amp power switches (row 14). This does not
    stop `jack_connect` or a patchbay, which act on other apps' ports;
    see the rule above.
  - *Required check before amps on.* After starting Mixxx, Reaper or any
    other audio app, and before amps on, run `pw-link -l` (listing only,
    safe). Under every USBStreamer `playback_AUX` port, the only source
    listed must be `pi4audio-convolver-out`.
  - *If any other source appears:* amps off (or keep them off),
    headphones/IEM off and not worn, then report it. Do not delete the
    link by hand.
- **ALSA tools (US-173):** the Pi 5 image ships alsa-utils for
  diagnosis. **Never run aplay or speaker-test against the USBStreamer;
  listing devices (`aplay -l`, `aplay -L`, `arecord -l`, `arecord -L`) is
  allowed. Use amixer only to read, never to set USBStreamer controls, and
  never run alsactl.** See Section 9, "Operator Rule: ALSA Command-Line
  Tools".
- **WirePlumber restart:** a WirePlumber restart, planned or after a
  crash, destroys and re-creates the USBStreamer node, so it is a
  USBStreamer interruption (Section 1) (F-396). Announce a planned restart, and
  the amps rule applies exactly as for a PipeWire restart. The gain nodes
  live in PipeWire, not in WirePlumber, so they keep their values through
  a WirePlumber restart. Without GraphManager acting, audio would resume
  at the old gains as soon as the USBStreamer is re-linked. The required
  behaviour (US-175) is: when GraphManager re-links after the restart, the
  D-063 gate comes back closed and all 8 gain nodes read 0 (GraphManager
  may keep the venue gains as pending values for the next gate
  opening), audio never resumes by itself, and re-opening the gate is an
  explicit operator action through the normal gate opening (an instant
  step, F-315). **This is NOT yet verified. Do not rely on it.** After every WirePlumber restart, the amps stay off. Before
  switching them on again, restart PipeWire or cold power-cycle the Pi.
  Either one interrupts the USBStreamer: announce it; amps off, including
  the headphone/IEM amps, and headphones/IEMs not worn.
  Afterwards the gains are back at their boot values; verify them as in
  "Gains at boot" below, and check that the D-063 gate is closed. Reading
  the gains live after a WirePlumber restart does not count as proof yet
  (live readback proven in the sandbox only for nodes that are idle or
  running, Gate-2 r6b; Pi check pending). This interim rule applies
  until US-175 is verified AND the live gains readback is proven on the
  Pi (Gate-2 r6b sandbox result plus the AE's Pi check, F-395). The AE
  then lifts it. Also do the `pw-link -l` check from the F-318 rule. An open gate or
  a failed `pw-link -l` check after a WirePlumber restart is a defect
  against US-175: report it. An unplanned restart shows in
  `journalctl --user -u wireplumber`; treat it the same way.
- **F-341 rule:** do not rely on pre-flight checks #3 and #6 as written on
  the Pi 5; treat their result as unverified.
- **Gains at boot:** all 8 linear gains boot with Mult and Add 0 (16
  values). Read the gain VALUES with `pw-cli enum-params <id> Props`,
  where <id> is the pi4audio-convolver node id taken from pw-dump. PASS
  only if every gain_*:Mult and gain_*:Add of the 8 named gains prints
  exactly `0.000000`. `nan`, `inf`, `-0.000000`, any other value, a
  missing gain or an extra gain_* name is a FAIL. The reading counts
  only if the filter-chain node and its output node are idle or running
  immediately before and after the reading (states logged with it). A
  suspended node reads 0 whatever the real gain is, so that result is
  NOT VERIFIABLE, never a pass. pw-dump is for
  structure only: exactly one pi4audio-convolver node, one
  pi4audio-convolver-out node and the 8 named gains. Never pass a gain on
  its pw-dump value: pw-dump prints NaN, -Inf and subnormal values as 0,
  and, like enum-params, it shows 0 on a suspended node whatever the
  real gain is (F-395, Gate-2 r6b). A script may additionally
  check the pw-dump values as an extra FAIL condition (any non-zero or -0
  value fails), never as a pass. Known limit of both readers: a magnitude
  below 5e-7 (below -126 dB) prints as 0.000000. The AE accepts this: a
  gain that small is inaudible, below the noise floor of the chain. On a
  FAIL or a NOT VERIFIABLE result, the gains are not proven muted: amps
  stay off or go off now, including the headphone/IEM amps,
  headphones/IEMs not worn; report. (Section 5 check 10 is added by PR #45,
  paused; until then this paragraph is the rule.)
- **Gate:** the GraphManager gate boots closed. Do not open it while any
  Pi 5 row (1-3, 5-14, 19-21) of the list above is open.
- **F-465 rule (no venue armed):** the GraphManager service has no venues
  directory, so it cannot arm a venue. Without a venue the gate cannot
  open and the gains stay 0: the gap blocks audio, it does not make
  audio unsafe. Do not open the gate, start a DJ session or turn amps on,
  on any generation, until the F-465 fix has deployed and AC3 (b-e) has
  passed on the Pi 5 on that generation. AC3 is the US-173 coefficient
  check: (b) the coefficient WAVs match their committed sha256, (c)
  PipeWire started after those files were written, (d) the journal shows
  no filter-chain load error, (e) GraphManager's active venue is the
  expected one.
- **Watchdog latch (F-320 D):** until F-320 D lands, `watchdog_unlatch`
  writes a fixed gain table back (0.001 on the mains and ch 5-8, 0.000631
  on the subs), not the venue gains, while the gate still reads closed.
  So a closed gate is not silent after an unlatch. If the watchdog
  latches: unlatch, then `close_gate`, then confirm all 8 Mults read 0
  (read as in "Gains at boot") before anything else.
- **F-348 rule (generated convolver conf):** until F-348 is fixed, a
  generated `~/.config/pipewire/pipewire.conf.d/30-filter-chain-convolver.conf`
  comes up at the next PipeWire restart with the venue gains as its
  defaults, while the gate reads closed. "Gains at boot" catches this
  only at boot, not after a mid-session restart. So: (1) do not activate
  a speaker profile, run a filter rollback, deploy filters, or run the
  measurement DEPLOY step from the web UI, and do not call
  room_correction's `deploy_pw_config` by hand; all of these write that
  file. (2) Before any PipeWire restart, confirm that the file either
  does not exist, or that it is the shipped conf and all 8 gain Mult
  defaults in it read 0.0. If not, do not restart, keep the amps off,
  and have it removed in a CM CHANGE session. (3) After the restart,
  pass the "Gains at boot" read, and confirm in pw-dump that there is
  exactly one pi4audio-convolver node, before the amps go on and before
  headphones or IEM go back in.
- **Outputs:** the WirePlumber allowlist disables every ALSA card except the
  USBStreamer (and the UMIK-1 capture). The HiFiBerry DAC+ HAT is blocked on
  2 layers (allowlist and module blacklist). The third layer
  (`force_eeprom_read=0`) has no effect, because the firmware merges no
  `config.txt` overlays (US-172). Accepted only while nothing is connected
  to the HAT.
- **Reboots:** Section 1 applies unchanged. While the owner's standing
  statement that nothing is connected to any Pi output holds, announce
  every reboot, power cycle, tryboot or PipeWire restart; if anything has
  been connected since, wait for the owner's go.
- **Thermal:** passive cooling only (metal case, no fan). During load runs,
  sample the SoC temperature every 10 s. At 75 °C or more, warn the owner
  and keep running. At 80 °C or more, STOP (the firmware starts throttling
  there). Sustained DJ load is expected to cross 80 °C without a fan.
- **RT (Section 6):** D-013 is re-confirmed on the Pi 5 (D-069): PREEMPT_RT
  6.12.62, PipeWire at SCHED_FIFO 88 without RTKit (F-358 fix).

---

## 1. USBStreamer Transient Risk

**The USBStreamer produces full-scale transients when its audio stream is
interrupted.** These transients pass through the 4x450W amplifier chain and can
damage speakers and risk hearing.

### Actions That Cause Transients

- Rebooting the Pi
- `systemctl --user restart pipewire.service`
- `systemctl --user restart wireplumber.service` (it destroys and
  re-creates the USBStreamer node)
- Any action that causes PipeWire to drop the USBStreamer playback stream
- USB bus resets affecting the USBStreamer

**Note (D-040):** CamillaDSP is no longer in the audio path. The previous
risk from `systemctl restart camilladsp` no longer applies. All audio
processing is now within PipeWire's filter-chain — the only transient risk
is from PipeWire restarts or USB interruptions.

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

### Subsonic Corner on Channels With a Crossover HP (F-383)

The identity's `mandatory_hpf_hz` stays the protection spec; no profile or
identity data changes. What F-383 changes is where the separate subsonic
filter's corner sits on a channel that also has a crossover highpass:

- **Protection is judged on the product.** On a channel with a crossover HP,
  the D-031 protection is judged on the product of the crossover HP and the
  subsonic, not on the subsonic alone. Lowpass and full-range channels keep
  the subsonic at `mandatory_hpf_hz`.
- **One derivation.** `derive_subsonic()` in
  `src/room-correction/room_correction/crossover.py` derives the corner for
  every combine caller (profile filters, the runner, the Bose generator). No
  caller keeps the old corner.
- **Rule R4.** Let m be `mandatory_hpf_hz`, fc_hp the channel's crossover HP
  edge, and s the highest subsonic corner among its crossover partners (the
  legs whose LP edge is fc_hp), or none if no partner has a subsonic. The
  target is fc_hp/5 if s is none, otherwise max(fc_hp/5, s). The corner moves
  to the target only if target < m < fc_hp; otherwise it stays at m. Below
  the partner's own subsonic, a lower corner gains nothing at the crossover
  and costs phase alignment between the two legs.
- **Gates on a moved corner.** A moved corner must pass both checks on the
  product, or filter generation stops with `SubsonicDerivationError`:
  - NB-C4a: at every 1/12-octave point from 10 Hz to m, the product
    attenuates at least as much as the subsonic at m with the same slope;
  - L2': the attenuation at m/2 is at least 18 dB re the passband peak above
    m, and the attenuation at m/4 is at least the attenuation at m/2.

  On a failure no other corner is tried and the crossover frequency is never
  changed. A crossover-frequency change is an audible tonal change and goes
  to the owner.
- `verify_mandatory_hpf` still checks every channel at m on the shipped
  product.

Moved set at C4 (`94f14fcc`); all other channels keep m:

| Profile | Channels | m -> corner | Partner s | fc_hp |
|---------|----------|-------------|-----------|-------|
| 2way-200hz-markaudio-ultimax | sat_left/right | 80 -> 40 Hz | none | 200 Hz |
| 2way-80hz-sealed | sat_left/right | 25 -> 20 Hz | 20 Hz | 80 Hz |
| bose-home-chn50p | sat_left/right | 80 -> 42 Hz | 42 Hz | 200 Hz |
| pa-2way-80hz-lavoce | sat_left/right | 55 -> 20 Hz | 20 Hz | 80 Hz |
| workshop-c3d-elf-3way | hf_left/right | 800 -> 200 Hz | 100 Hz | 1000 Hz |

**Pending step 4 (not a result): composition tail.** At C4 the composition
row is log only; the tail does not gate yet. With step 4, the shipped
combined filter on every cascade channel is gated on tail and decay (the
last 5% at or below -45 dB, and decaying). The step-4 PR must report that
tail/decay for every profile it ships. A buildable, shipped profile without
that data, or any tail/decay failure, is a STOP to the audio engineer and
the architect, with no workaround. Only a profile that does not build today
(2way-80hz-ported, workshop-xrk10f-fullrange) may be reported as "cannot be
generated", named as such.

This changes driver protection, so it carries the audio engineer's veto in
the PR. Until F-383 step 5 has landed, the CM hold F-383-AMPS stays: the
new filters are not cleared for amps-on use.

Rulings: C4.1 (Architect NOTE `1f1c1f05`, AE FINAL `80801402`); C4 fence
`41fd1486` (AE `92386ab9`); R4 `62cd5e5c` (AE `9973bc8b`); s = max over
partners `3267ecf2` (AE `a5885b6c`).

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
- F-383: subsonic corner derivation on channels with a crossover HP (rule R4)

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
| 3 | Signal generator running and reachable | `echo '{"cmd":"status"}' \| nc -q1 127.0.0.1 4001` **Pi 5:** the nc -q1 form is invalid on the Pi 5 image (libressl nc); status has no max_level_dbfs; see F-341. Do not run a measurement session until F-341 lands. | Measurement audio I/O unavailable. Signal-gen is the sole measurement output path (D-040). |
| 4 | PipeWire running at FIFO/88 | `chrt -p $(pgrep -x pipewire)` | Graph clock not real-time (F-020) |
| 5 | Correct PipeWire quantum for measurement mode | `pw-metadata -n settings \| grep quantum` | Quantum affects convolver processing latency and CPU load. Measurement typically uses quantum 256 (live mode). |
| 6 | Signal-gen hard cap is -20 dBFS | `echo '{"cmd":"status"}' \| nc -q1 127.0.0.1 4001` -- check `max_level_dbfs` in response. **Pi 5:** the nc -q1 form is invalid on the Pi 5 image (libressl nc); status has no max_level_dbfs; see F-341. Do not run a measurement session until F-341 lands. | Safety cap incorrect or missing. The -20 dBFS cap is immutable after startup but verify at pre-flight to confirm correct startup flag. |
| 7 | Signal-gen ports visible in PipeWire graph | `pw-cli ls Node \| grep signal-gen` | Signal-gen not registered as PW node. In managed mode, GraphManager creates links -- if ports are missing, no audio can flow. |
| 8 | ADA8200 capture adapter stopped (if not needed) | `pw-cli ls \| grep ada8200` | F-015: USB bandwidth contention between capture and playback streams on USBStreamer |
| 9 | Owner confirmed amp level safe | Verbal/written confirmation | Transient/excursion damage risk |
| 11 | Routing: the USBStreamer is fed only from the convolver (F-318) | `pw-link -l` (listing only): under every USBStreamer `playback_AUX0..7` port, the only source listed is `pi4audio-convolver-out` | A bypass link sends full-scale audio to the amplifiers or IEM with no crossover, gains or gate. Amps off (or keep off), headphones/IEM off and not worn, report it; do not delete the link by hand. See the F-318 rule (Pi 5 rules). |

Check 10 (the gains read as in "Gains at boot", F-395) is added by PR #45,
paused; until then the "Gains at boot" rule in the Pi 5 rules applies.

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
| 11 | F-318; `src/graph-manager/src/link_audit.rs` (only `pi4audio-convolver-out` may feed USBStreamer ports, D-063) |

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

The Config tab provides per-channel gain sliders controlling the four PipeWire
filter-chain `linear` builtin gain nodes. These are the same gain nodes used
by the panic MUTE button (Section 7, F-040) and the measurement pipeline.

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

The MUTE button (always visible in the status bar) sets all four gain node
Mult values to 0.0. Pre-mute values are stored in memory by
`AudioMuteManager`. UNMUTE restores the stored values. The MUTE operation
does NOT drop the PipeWire stream — this is critical for USBStreamer transient
safety (Section 1). The audio path remains connected; only the gain is zeroed.

### PROHIBITED: Setting Gains to Unity for Spectrum Viewing (owner directive 2026-03-25)

**Never set gain nodes to Mult = 1.0 (unity) to get a "full-scale" spectrum
display.** This was proposed as a workaround to see the true signal level at
post-gain tap points in the spectrum analyzer (US-080 Tap 2). The owner
explicitly rejected it as a safety risk.

**Why it is dangerous:**

All 8 gain nodes boot at Mult 0 (D-063 universal gate). Opening the gate is an
instant step to the venue gain (F-315); there is no ramp. The venue gain is the
active venue profile's `gain_db` (D-009 hard cap 0 dB).
Own-speaker profiles attenuate the speaker channels heavily (for example
`configs/venues/markaudio-ultimax-200hz.yml`: -60 dB mains, -64 dB sub 1, -120
dB sub 2). In `production.yml` and `markaudio-ultimax-200hz.yml` the headphone
and IEM channels are at 0 dB, so their level is set only by the headphone/IEM
amplifiers: turn those down before opening the gate. `foh-passthrough.yml` is
0 dB on all 8 channels with Dirac coefficients, so there is no crossover and
no subsonic protection (D-031). It is only for feeding a venue FoH system that
does its own gain staging, never our own 4x450W amps. The old fixed defaults
0.001 (-60 dB mains) and 0.000631 (-64 dB subs) are pre-D-063; they survive
only in the watchdog unlatch restore table (defect F-320). Setting a
speaker-channel gain node to unity while our speakers are connected, whether
by `pw-cli` or by opening the gate on the wrong profile, sends full-scale
audio through the 4x450W amplifier chain. Even momentarily, this can damage
drivers and ears.

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

PipeWire's static adapters (`20-usbstreamer.conf`, `21-usbstreamer-playback.conf`)
hold the USBStreamer ALSA device open continuously. Any other process attempting
`open()` on the ALSA device node receives `EBUSY`. This is the primary defense
and blocks all bypass attempts while PipeWire is running.

**Residual risk:** When PipeWire is stopped or restarting, the ALSA device is
momentarily available. Layer 2 covers this gap.

### Layer 2: udev Device Permissions

The udev rule `99-usbstreamer-lockout.rules` restricts USBStreamer ALSA device
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

### Layer 4: Filter-Chain Watchdog (T-044-4)

The GraphManager's watchdog (`src/graph-manager/src/watchdog.rs`) continuously
monitors 6 critical nodes in the PipeWire graph:

| Node | Role |
|------|------|
| `pi4audio-convolver` | Filter-chain capture side |
| `pi4audio-convolver-out` | Filter-chain playback side |
| `gain_left_hp` | Left main gain node |
| `gain_right_hp` | Right main gain node |
| `gain_sub1_lp` | Sub 1 gain node |
| `gain_sub2_lp` | Sub 2 gain node |

If ANY monitored node disappears from the PipeWire graph, the watchdog
triggers a **latched safety mute**:

**Primary mute mechanism:** Set `Mult=0.0` on all 4 gain nodes via native
PipeWire API (`pw_node_set_param` via `pipewire-rs` FFI). Target response
time: <1ms per node, <5ms total.

**Fallback mechanism:** If the gain nodes themselves have disappeared (can't
set Mult on a nonexistent node), the watchdog destroys ALL links to the
USBStreamer input ports using `pw_registry::destroy_global()`.

**Latch behavior:** Once triggered, the mute is LATCHED -- it stays active
even after the missing nodes return. Unlatching requires an explicit RPC
command (`watchdog_unlatch`). This prevents transient audio during graph
recovery. Pre-mute gain values are stored and restored on unlatch.

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
| 1 | PipeWire exclusive ALSA hold | All non-PW processes | No | `20/21-usbstreamer.conf` |
| 2 | udev OWNER/MODE | Other users, system services | Yes | `99-usbstreamer-lockout.rules` |
| 3 | WirePlumber node deny | Rogue PW client nodes | N/A (WP requires PW) | `53-deny-usbstreamer-alsa.conf` |
| 4 | GraphManager watchdog | Convolver/gain node loss | N/A (GM requires PW) | `src/graph-manager/src/watchdog.rs` |

### Operator Rule: ALSA Command-Line Tools (US-173)

Since US-173 the Pi image installs alsa-utils (`aplay`, `arecord`,
`amixer`, `aconnect`, `alsactl`) for gig-day diagnosis.

**Never run aplay or speaker-test against the USBStreamer; listing devices
(`aplay -l`, `aplay -L`, `arecord -l`, `arecord -L`) is allowed. Use amixer
only to read, never to set USBStreamer controls, and never run alsactl.**

Why: audio played straight to the USBStreamer ALSA device bypasses the
convolver, the D-063 gains and the gate, so it reaches the amplifiers
unfiltered and unattenuated. Layer 1 blocks this only while PipeWire
holds the playback device; while PipeWire is stopped or restarting,
Layer 2 still lets the `ela` user open it (S-010 was the same class of
DSP bypass, via a different ALSA device). The mixer controls are
different: no layer blocks `ela` from changing them, even while PipeWire
is running, because an ALSA control device can be opened alongside
PipeWire. The USBStreamer hardware Playback Volume powers up at 0 dB, its
maximum, and the output safety rests on the D-063 gains and the gate
alone. Setting a USBStreamer control changes the gain staging underneath
them. Lowering it is no safer: the next power loss resets it to 0 dB,
which is then a silent gain increase.

### Cross-References

- US-044: ALSA device lockout user story
- T-044-1: udev rules + PipeWire exclusive hold
- T-044-2: WirePlumber deny policy
- T-044-3: GraphManager link audit
- T-044-4: Filter-chain watchdog
- `configs/udev/99-usbstreamer-lockout.rules`
- `configs/wireplumber/53-deny-usbstreamer-alsa.conf`
- `configs/wireplumber/scripts/deny-usbstreamer-alsa.lua`
- `src/graph-manager/src/watchdog.rs`

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
| US-173 | No aplay/speaker-test playback on the USBStreamer (listing OK); amixer read-only; no alsactl | 9 |

## Safety Incident Register

| Date | Session | Summary | Outcome | Lab Note |
|------|---------|---------|---------|----------|
| 2026-03-13 | S-010 | Sweep bypassed CamillaDSP via sysdefault ALSA device | No damage (sysdefault not routed to physical output) | `change-S-010-measurement-test-failed.md` |
| 2026-03-17 | S-012 | +30 dB gain increase on live path while owner monitoring on headphones | No injury. New rule: never increase gain without owner confirmation | `change-C-005-live-mode-investigation.md` |
