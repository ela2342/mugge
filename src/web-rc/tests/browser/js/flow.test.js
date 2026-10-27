// Flow controller (flow.js): AC11 steps, AC2-AC4 gating, E4 and E5 stops.

import { assert, close, eq } from "./assert.js";
import { FLOW, FLOW_TEXT, Flow, STEP, markedName } from "../../../static/js/flow.js";
import { parseCalibration } from "../../../static/js/calibration.js";
import { crestEntry, topStepDbfs, unitGain } from "../../../static/js/crest.js";
import { crestSeed } from "../../../static/js/crest-plan.js";
import { CAP_LINEAR } from "../../../static/js/output-core.js";
import { LATCH } from "../../../static/js/stop-latch.js";
import {
  LIMITS, ROLE, STOP, changeRole, levelNoiseBand, stopMessage,
} from "../../../static/js/safety.js";

const SR = 48000;
const OFF = { echoCancellation: false, noiseSuppression: false,
  autoGainControl: false };
const AUDIO = { outputRate: SR, inputRate: SR, outputChannels: 8,
  dspSettings: OFF, micId: "mic-A", micLabel: "UMIK-1" };
const UMIK_TEXT = '"Sens Factor =-1.378dB, SERNO: 7161942"\n' +
  "20.000\t-0.13\n";
const UMIK = parseCalibration(UMIK_TEXT);
const QUIET = { peakDbfs: -60, rmsDbfs: -70 };
/** The output worklet's zero-reached for a commanded stop. */
const STOPPED = { type: "stopped", frame: 0, clamped: false, cause: null };

function sub40() {
  return { ...changeRole({ enclosure: "closed" }, ROLE.SUBWOOFER), limitHz: 40,
    capabilityConfirmed: true };
}

/** A flow at the level step, channel 2, Subwoofer 40 Hz closed. */
function atLevel({ cal = false } = {}) {
  const f = new Flow();
  f.setAudio(AUDIO);
  f.setChannel(2);
  f.setDeclaration(sub40());
  if (cal) f.loadCalibration("7161942.txt", UMIK, UMIK_TEXT);
  f.confirmSetup();
  ackAll(f);
  eq(f.step, STEP.LEVEL);
  return f;
}

/** Tick every 4a item, then acknowledge (UX 64c83e3e). */
function ackAll(f) {
  for (let i = 0; i < FLOW.ACK_ITEMS; i++) f.tickAck(i, true);
  return f.acknowledge();
}

const types = (cmds) => cmds.map((c) => c.type).join(",");

/**
 * A capture as the page delivers it: the output onset, then the recording,
 * both counted on context clock 1.
 */
function rec(f, token, samples, onset = 0) {
  eq(f.output({ type: "started", frame: 4096 + onset, clock: 1 }).length, 0);
  return f.recorded(token, samples, 4096, 1, null);
}

/** A unit sweep stand-in: a sine with fades, RMS about -3 dBFS. */
function unitSweep(seconds = 1) {
  const n = seconds * SR;
  const s = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const fade = Math.min(1, i / 480, (n - 1 - i) / 480);
    s[i] = fade * Math.sin(2 * Math.PI * 100 * i / SR);
  }
  return s;
}

function rmsOf(x) {
  let a = 0;
  for (const v of x) a += v * v;
  return Math.sqrt(a / x.length);
}

/** Level check to the top step with a reading, then measure. */
function toMeasure(f, now = 0) {
  f.startLevel(now);
  while (f.canStepUp()) f.stepUp(now);
  f.meter(now, { peakDbfs: -40, rmsDbfs: -50 });
  return f.measure(now);
}

/**
 * The sweep is ready, the level noise reaches zero at `now`, the room has
 * decayed and the context runs: capture 1's commands.
 */
function settled(f, token, samples, now = 0) {
  const cmds = f.sweepReady(token, samples);
  if (cmds.length) return cmds;
  f.output(STOPPED, now);
  const r = f.tick(now + 1000 * LIMITS.ROOM_DECAY_S);
  return types(r) === "resume" ? f.resumed(r[0].token) : r;
}

// -- setup gating (AC2, AC3, 4a) --------------------------------------------

export async function test_setup_blocks_until_everything_is_valid() {
  const f = new Flow();
  eq(f.setupProblems().length, 1, "no audio yet");
  f.setAudio(AUDIO);
  assert(f.setupProblems().includes("Choose the output channel."));
  f.setChannel(2);
  eq(f.setupProblems()[0], "Choose what is connected to this output.");
  eq(types(f.confirmSetup()), "");
  eq(f.step, STEP.SETUP, "stays in setup");
  f.setDeclaration(sub40());
  eq(f.setupProblems().length, 0);
  f.confirmSetup();
  eq(f.step, STEP.ACK, "4a before the first sound");
  eq(f.startLevel(0).length, 0, "no sound before the ack");
  // Defence in depth: the ack guard holds even if the step were wrong.
  f.step = STEP.LEVEL;
  eq(f.startLevel(0).length, 0, "no sound without the ack at any step");
  f.step = STEP.ACK;
  ackAll(f);
  eq(f.step, STEP.LEVEL);
}

export async function test_channel_must_exist_on_the_device() {
  const f = new Flow();
  f.setAudio({ ...AUDIO, outputChannels: 2 });
  f.setDeclaration(sub40());
  for (const ch of [2, -1, 1.5, null, "0", 8]) {
    f.setChannel(ch);
    assert(f.setupProblems().includes("Choose the output channel."), String(ch));
  }
  f.setChannel(1);
  eq(f.setupProblems().length, 0);
}

export async function test_wrong_rate_blocks() {
  for (const audio of [{ ...AUDIO, outputRate: 44100 },
    { ...AUDIO, inputRate: 44100 }]) {
    const f = new Flow();
    f.setAudio(audio);
    f.setChannel(0);
    f.setDeclaration(sub40());
    assert(f.setupProblems()[0].startsWith("Can't measure: this audio device " +
      "runs at 44100 Hz."));
    f.confirmSetup();
    eq(f.step, STEP.SETUP);
  }
}

/** PO e720d78c: a DSP flag that is on or missing blocks, calibrated or not. */
export async function test_dsp_flags_block_even_with_calibration() {
  for (const dspSettings of [{ ...OFF, autoGainControl: true },
    { echoCancellation: false, noiseSuppression: false }]) {
    const f = new Flow();
    f.setAudio({ ...AUDIO, dspSettings });
    f.setChannel(0);
    f.setDeclaration(sub40());
    f.loadCalibration("7161942.txt", UMIK);
    assert(f.setupProblems().includes("Can't measure: the browser's " +
      "automatic gain control is still on for this mic."));
    f.confirmSetup();
    eq(f.step, STEP.SETUP, "blocked");
  }
}

// -- level check ------------------------------------------------------------

export async function test_level_check_starts_at_minus_60_on_one_channel() {
  const f = atLevel();
  const cmds = f.startLevel(1000);
  eq(types(cmds), "noise-start");
  const band = levelNoiseBand(ROLE.SUBWOOFER, 40);
  const c = cmds[0];
  eq(c.channel, 2);
  eq(c.source.kind, "noise");
  eq(c.source.seed, crestSeed(2));
  eq(c.source.band.lowHz, 80);
  eq(c.source.band.highHz, 200);
  close(c.gain, unitGain(crestEntry(band, 2), -60), 1e-15);
  eq(f.startLevel(1000).length, 0, "no second start while sounding");
}

/** AE K5: "+" stops at the band's top step; each step is one gain command. */
export async function test_steps_stop_at_band_top_step() {
  const f = atLevel();
  f.startLevel(0);
  const band = levelNoiseBand(ROLE.SUBWOOFER, 40);
  const top = topStepDbfs(band);
  const entry = crestEntry(band, 2);
  let level = -60;
  while (f.canStepUp()) {
    const cmds = f.stepUp(0);
    level += 6;
    eq(types(cmds), "gain");
    close(cmds[0].gain, unitGain(entry, level), 1e-15);
  }
  eq(level, top);
  eq(f.stepUp(0).length, 0, "no step above the top");
  f.meter(0, { peakDbfs: -45, rmsDbfs: -55 });
  eq(f.atTopWithoutTarget, true, "target not reached at maximum test level");
}

export async function test_target_reached_disables_plus() {
  const f = atLevel();
  f.startLevel(0);
  f.meter(0, { peakDbfs: -30, rmsDbfs: -40 }); // uncalibrated target -40
  eq(f.canStepUp(), false);
  eq(f.stepUp(0).length, 0);
}

export async function test_calibrated_target_and_meter_message() {
  const f = new Flow();
  f.setAudio(AUDIO);
  const cmds = f.loadCalibration("7161942.txt", UMIK);
  eq(types(cmds), "meter-calibration");
  close(cmds[0].splOffsetDb, 121.378, 1e-12);
  eq(f.calibrated, true);
  f.setChannel(2);
  f.setDeclaration(sub40());
  f.confirmSetup();
  ackAll(f);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -46.5 }); // 74.9 dB SPL
  eq(f.canStepUp(), true, "75 dB SPL not yet reached");
  f.meter(0, { peakDbfs: -40, rmsDbfs: -46.3 }); // 75.1 dB SPL
  eq(f.canStepUp(), false);
}

/**
 * Release a held main-thread cause (latch r2 A3): Start is refused until
 * the page is visible again / the devices are opened again.
 */
function release(f, cause) {
  if (cause === STOP.HIDDEN) {
    eq(f.canStart, false, "held: hidden");
    eq(f.startLevel(40000).length, 0, "no Start while hidden");
    eq(f.holdText, "", "a hidden page has no hold text (E6b)");
    f.visible();
  } else if (cause === STOP.AUDIO_ERROR || cause === STOP.HEARTBEAT) {
    eq(f.canStart, false, "held: " + cause);
    eq(f.startLevel(40000).length, 0, "no Start after " + cause);
    eq(f.holdText, stopMessage(cause), "E6b: the hold names itself");
    f.setAudio(AUDIO);
  }
  eq(f.canStart, true, "released: " + cause);
  eq(f.holdText, "", "released: no hold text");
}

/** 4d/4i/E4: each auto-STOP names its cause; a restart is fresh at -60. */
export async function test_level_auto_stops() {
  const cases = [
    [(f) => f.meter(5, { peakDbfs: -0.5, rmsDbfs: -20 }), STOP.MIC_CLIP],
    [(f) => f.output({ type: "clamped" }), STOP.CAP],
    [(f) => f.output({ type: "error" }), STOP.AUDIO_ERROR],
    [(f) => f.tick(30020), STOP.TIMEOUT],
    [(f) => f.meter(30020, QUIET), STOP.TIMEOUT],
    [(f) => f.hidden(), STOP.HIDDEN],
    [(f) => f.userStop(), STOP.USER],
    [(f) => f.audioError(), STOP.AUDIO_ERROR],
    [(f) => f.output({ type: "stopped", cause: LATCH.HEARTBEAT }), STOP.HEARTBEAT],
  ];
  // The last user action is the "+" at 20 ms: 30 s later, not before.
  const early = atLevel();
  early.startLevel(0);
  early.stepUp(20);
  eq(early.tick(30019).length, 0, "29.999 s");
  eq(early.meter(30019, QUIET).length, 0);
  for (const [act, cause] of cases) {
    const f = atLevel();
    f.startLevel(0);
    f.stepUp(10);
    f.stepUp(20);
    eq(types(act(f)), "output-stop", cause);
    eq(f.step, STEP.LEVEL, "level step stays open: " + cause);
    eq(f.notice.cause, cause);
    eq(f.notice.text, stopMessage(cause, { calibrated: false }));
    eq(f.sounding, false);
    eq(f.stepUp(25).length, 0, "no + after a stop");
    release(f, cause);
    const again = f.startLevel(40000);
    close(again[0].gain, unitGain(crestEntry(levelNoiseBand(ROLE.SUBWOOFER, 40),
      2), -60), 1e-15, "fresh start at -60 after " + cause);
  }
}

/** Latch r2 A3: a render-thread stop the meter report has not brought. */
export async function test_render_thread_stop_reaches_the_flow() {
  const f = atLevel();
  f.startLevel(0);
  eq(types(f.output({ type: "stopped", cause: STOP.MIC_CLIP })), "output-stop");
  eq(f.notice.cause, STOP.MIC_CLIP);
  eq(f.canStart, true, "a meter cause is not held here: the meter re-trips");
  eq(f.output({ type: "stopped", cause: STOP.MIC_CLIP }).length, 0, "once");
  eq(f.output({ type: "stopped", cause: null }).length, 0, "a plain zero-reached");
}

/** A4, E6: a heartbeat stop is held until the devices reopen, with its text. */
export async function test_heartbeat_stop_is_a_held_audio_error() {
  const f = atLevel();
  f.startLevel(0);
  eq(types(f.output({ type: "stopped", cause: LATCH.HEARTBEAT })), "output-stop");
  eq(f.notice.cause, STOP.HEARTBEAT);
  eq(f.notice.text, stopMessage(STOP.HEARTBEAT));
  release(f, STOP.HEARTBEAT);
  // E6b: not sounding: still held, and the text shows without a stop box.
  f.notice = null;
  eq(f.output({ type: "stopped", cause: LATCH.HEARTBEAT }).length, 0);
  eq(f.notice, null, "nothing was sounding");
  eq(f.canStart, false, "held while idle too");
  eq(f.holdText, stopMessage(STOP.HEARTBEAT));
  // The latest hold names it; opening the devices releases both.
  f.audioError();
  eq(f.holdText, stopMessage(STOP.AUDIO_ERROR));
  f.output({ type: "stopped", cause: LATCH.HEARTBEAT });
  eq(f.holdText, stopMessage(STOP.HEARTBEAT), "re-held: latest again");
  f.hidden();
  eq(f.holdText, stopMessage(STOP.HEARTBEAT), "hidden adds no text");
  f.setAudio(AUDIO);
  eq(f.canStart, false, "still hidden");
  eq(f.holdText, "");
  f.visible();
  eq(f.canStart, true);
}

/** A3: hidden holds while idle; a device change keeps it, frees an error. */
export async function test_held_causes_and_device_change() {
  const f = atLevel();
  f.hidden();
  eq(f.canStart, false, "hidden while idle");
  f.audioError();
  f.output({ type: "stopped", cause: LATCH.HEARTBEAT });
  f.deviceChange({ ...AUDIO });
  f.setChannel(2);
  f.setDeclaration(sub40());
  f.confirmSetup();
  ackAll(f);
  eq(f.held.has(STOP.AUDIO_ERROR), false, "the devices were opened again");
  eq(f.held.has(STOP.HEARTBEAT), false, "the heartbeat hold too");
  eq(f.canStart, false, "still hidden");
  eq(f.startLevel(0).length, 0);
  f.visible();
  eq(f.canStart, true);
  f.audioError();
  f.deviceChange(null);
  eq(f.held.has(STOP.AUDIO_ERROR), true, "no device: still held");
}

/** C6: after a stop, no sweep without a new level check with its own reading. */
export async function test_c6_sweep_needs_a_new_passed_level_check() {
  const f = atLevel();
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  f.output({ type: "stopped", cause: STOP.MIC_CLIP });
  eq(f.measure(0).length, 0, "stopped: no sweep");
  f.startLevel(1000);
  eq(f.measure(0).length, 0, "the old reading does not count");
  f.meter(1000, { peakDbfs: -0.5, rmsDbfs: -20 });
  eq(f.measure(0).length, 0, "the new check did not pass");
  f.startLevel(2000);
  f.meter(2000, { peakDbfs: -40, rmsDbfs: -50 });
  eq(types(f.measure(0)), "output-stop,make-sweep", "a new passed check");
}

/** UX 64c83e3e: one checkbox per item; all ticked, or no acknowledgement. */
export async function test_ack_needs_every_tick() {
  const f = new Flow();
  f.setAudio(AUDIO);
  f.setChannel(2);
  f.setDeclaration(sub40());
  eq(f.tickAck(0, true).length, 0);
  eq(f.ackTicks.size, 0, "no ticks outside the 4a step");
  f.confirmSetup();
  eq(f.step, STEP.ACK);
  for (let i = 0; i < FLOW.ACK_ITEMS - 1; i++) f.tickAck(i, true);
  eq(f.canAcknowledge, false, "one item unticked");
  f.acknowledge();
  eq(f.step, STEP.ACK, "refused");
  f.tickAck(FLOW.ACK_ITEMS, true);
  f.tickAck(-1, true);
  eq(f.canAcknowledge, false, "no such item");
  f.tickAck(FLOW.ACK_ITEMS - 1, true);
  f.tickAck(0, false);
  eq(f.canAcknowledge, false, "unticked again");
  f.tickAck(0, true);
  eq(f.canAcknowledge, true);
  f.acknowledge();
  eq(f.step, STEP.LEVEL);
  eq(f.canAcknowledge, false, "only in the 4a step");
  // E5 D1: a device change clears every tick.
  f.deviceChange({ ...AUDIO });
  eq(f.ackTicks.size, 0);
  f.setChannel(2);
  f.setDeclaration(sub40());
  f.confirmSetup();
  eq(f.step, STEP.ACK);
  eq(f.canAcknowledge, false, "ticks again after a device change");
}

export async function test_mic_clip_text_follows_calibration() {
  const f = atLevel({ cal: true });
  f.startLevel(0);
  f.meter(0, { peakDbfs: -0.5, rmsDbfs: -40 });
  eq(f.notice.text, stopMessage(STOP.MIC_CLIP, { calibrated: true }));
  // Calibrated SPL stops act; uncalibrated they can't (AE A1).
  f.startLevel(0);
  f.meter(0, { peakDbfs: -20, rmsDbfs: -30 }); // 91.4 dB SPL RMS
  eq(f.notice.cause, STOP.MIC_SPL);
  const u = atLevel();
  u.startLevel(0);
  eq(u.meter(0, { peakDbfs: -20, rmsDbfs: -30 }).length, 0);
}

export async function test_stops_outside_sound_do_nothing() {
  const f = atLevel();
  eq(f.hidden().length, 0);
  eq(f.output({ type: "clamped" }).length, 0);
  eq(f.tick(1e9).length, 0);
  eq(f.notice, null);
}

export async function test_setup_is_frozen_after_setup() {
  const f = atLevel();
  f.setChannel(3);
  f.setDeclaration({ ...sub40(), limitHz: 20 });
  f.loadCalibration("x.txt", UMIK);
  eq(f.channel, 2);
  eq(f.decl.limitHz, 40);
  eq(f.cal, null);
  f.startLevel(0);
  eq(types(f.backToSetup()), "output-stop");
  eq(f.step, STEP.SETUP);
  f.setChannel(3);
  eq(f.channel, 3);
  f.confirmSetup();
  eq(f.step, STEP.LEVEL, "ack stays within a device session");
}

// -- measure (AC4g, AC7, AC8, A4, E4) ---------------------------------------

export async function test_measure_two_captures_then_analyze() {
  const f = atLevel();
  const m = toMeasure(f);
  eq(types(m), "output-stop,make-sweep");
  eq(f.step, STEP.MEASURE);
  const plan = m[1].plan;
  eq(plan.fStartHz, 40);
  eq(plan.fEndHz, 20000);
  eq(plan.seconds, 10, "AC4g: at most 10 s");
  close(plan.hpfHz, 32, 1e-12);
  eq(plan.sampleRate, SR);
  eq(f.measure(0).length, 0, "once");

  const unit = unitSweep();
  const s = settled(f, m[1].token, unit);
  eq(types(s), "record,sweep-start");
  const pre = FLOW.PRE_ROLL_S * SR;
  eq(s[0].frames, Math.round((FLOW.PRE_ROLL_S + 10 + 1) * SR), "AC2d window");
  eq(s[1].channel, 2);
  eq(s[1].samples.length, pre + unit.length);
  for (let i = 0; i < pre; i++) eq(s[1].samples[i], 0, "silent pre-roll");
  const top = topStepDbfs(levelNoiseBand(ROLE.SUBWOOFER, 40));
  close(20 * Math.log10(rmsOf(unit) * s[1].gain), top, 1e-9,
    "A4: sweep RMS = level-check RMS");

  const cap1 = new Float32Array(10);
  const s2 = rec(f, s[0].token, cap1);
  eq(types(s2), "record,sweep-start", "second capture, same sweep");
  assert(s2[0].token !== s[0].token);
  eq(s2[1].gain, s[1].gain);
  eq(f.recorded(s[0].token, cap1).length, 0, "old token ignored");
  const cap2 = new Float32Array(10);
  const a = rec(f, s2[0].token, cap2);
  eq(types(a), "output-stop,analyze", "the sweep output stops before the analysis");
  const r = a[1].request;
  eq(r.captures.length, 2);
  eq(r.captures[0], cap1, "capture 1 = filter");
  eq(r.captures[1], cap2, "capture 2 = hold-out");
  eq(r.played, s[1].samples, "the exact played buffer");
  eq(r.gain, s[1].gain);
  eq(r.decl.role, ROLE.SUBWOOFER);
  eq(r.calibrated, false);
  eq(r.calibrationFile, null);
  eq(r.calibrationText, null, "no curve without a calibrated session");
  eq(f.step, STEP.MEASURE);
  assert(f.hasUnsavedWork());

  f.analysisDone(a[1].token, { fileName: "sub_ch2.wav", wavBytes: new Uint8Array(4) });
  eq(f.step, STEP.RESULT);
  const d = f.downloads();
  eq(d.length, 1);
  eq(d[0].name, "sub_ch2.wav");
  eq(d[0].preDeviceChange, false);
  eq(f.filters.get(f.channel).role, ROLE.SUBWOOFER, "for the report");
  eq(f.filters.get(f.channel).enclosure, "closed", "for the report");
  assert(f.hasUnsavedWork(), "not downloaded yet");
  f.markDownloaded();
  eq(f.hasUnsavedWork(), false);
}

/**
 * AE d1f133da, 30d2bcef: capture 1 starts no sooner than ROOM_DECAY_S of
 * wall-clock time after the level noise's "stopped" (not after the click),
 * and only once the context runs again.
 */
export async function test_capture_1_waits_for_the_room_to_settle() {
  eq(LIMITS.ROOM_DECAY_S, 1, "the AC2d tail's constant");
  const f = atLevel();
  const m = toMeasure(f, 5000);
  eq(types(m), "output-stop,make-sweep");
  eq(f.sweepReady(m[1].token, unitSweep()).length, 0, "no capture yet");
  eq(f.tick(5900).length, 0, "no stopped yet");
  eq(f.output(STOPPED, 5900).length, 0);
  eq(f.tick(6000).length, 0, "1 s after the click: the room still decays");
  eq(f.tick(6899).length, 0);
  eq(f.output(STOPPED, 6800).length, 0, "a second stopped");
  const r = f.tick(6900);
  eq(types(r), "resume", "1 s after stopped");
  eq(f.tick(7150).length, 0, "once");
  eq(f.resumed(r[0].token + 1).length, 0, "not this resume");
  eq(types(f.resumed(r[0].token)), "record,sweep-start", "running: capture 1");
  eq(f.resumed(r[0].token).length, 0, "once");

  // On the page's 250 ms tick: the first record is ROOM_DECAY_S to
  // ROOM_DECAY_S + 250 ms after stopped.
  for (const stoppedAt of [100, 101, 237, 349]) {
    const g = atLevel();
    const gm = toMeasure(g, 0);
    g.sweepReady(gm[1].token, unitSweep());
    g.output(STOPPED, stoppedAt);
    let t = 0, cmds = [];
    for (; t < 5000 && !cmds.length; t += 250) cmds = g.tick(t);
    t -= 250;
    eq(types(cmds), "resume", "at " + stoppedAt);
    assert(t - stoppedAt >= 1000 * LIMITS.ROOM_DECAY_S, "waited " + (t - stoppedAt));
    assert(t - stoppedAt < 1000 * LIMITS.ROOM_DECAY_S + 250, "late " + t);
  }

  // The room settled before the sweep was ready: the next tick goes on.
  const h = atLevel();
  const hm = toMeasure(h, 0);
  h.output(STOPPED, 20);
  eq(h.tick(3000).length, 0, "no sweep yet");
  eq(h.sweepReady(hm[1].token, unitSweep()).length, 0);
  eq(types(h.tick(3250)), "resume");
}

/** AE d1f133da Q2: no "stopped": fail closed as an output fault, never the click. */
export async function test_no_stopped_fails_closed() {
  const f = atLevel();
  const m = toMeasure(f, 1000);
  f.sweepReady(m[1].token, unitSweep());
  eq(f.tick(1000 + 1000 * FLOW.STOPPED_TIMEOUT_S - 1).length, 0, "not yet");
  eq(f.tick(1000 + 1000 * FLOW.STOPPED_TIMEOUT_S).length, 0, "nothing sounds");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.cause, STOP.AUDIO_ERROR);
  eq(f.holdText, stopMessage(STOP.AUDIO_ERROR), "held until the devices reopen");
  eq(f.output(STOPPED, 2500).length, 0, "a late stopped");
  eq(f.tick(1e9).length, 0, "no capture later");

  // Also while the sweep is still being made.
  const g = atLevel();
  toMeasure(g, 0);
  g.tick(1000 * FLOW.STOPPED_TIMEOUT_S);
  eq(g.notice.cause, STOP.AUDIO_ERROR);

  // A "stopped" without a time can't start the wait.
  for (const t of [undefined, NaN, Infinity]) {
    const h = atLevel();
    const hm = toMeasure(h, 0);
    h.sweepReady(hm[1].token, unitSweep());
    h.output(STOPPED, t);
    eq(h.notice.cause, STOP.AUDIO_ERROR, String(t));
    eq(h.tick(1e9).length, 0, String(t));
  }
}

/**
 * AE d1f133da Q3: in the wait nothing sounds and no gain changes; a stop
 * aborts it; mic checks still apply; a retry starts a fresh wait.
 */
export async function test_the_settle_wait_aborts_and_restarts() {
  const NO_SOUND = ["noise-start", "sweep-start", "gain", "record"];
  const silent = (cmds, why) => {
    for (const c of cmds) assert(!NO_SOUND.includes(c.type), why + ": " + c.type);
  };
  const stops = [
    [(h) => h.userStop(), STOP.USER],
    [(h) => h.hidden(), STOP.HIDDEN],
    [(h) => h.deviceChange({ ...AUDIO }), STOP.DEVICE],
    [(h) => h.output({ ...STOPPED, cause: STOP.MIC_CLIP }, 10), STOP.MIC_CLIP],
    [(h) => h.meter(10, { peakDbfs: -0.5, rmsDbfs: -20 }), STOP.MIC_CLIP],
  ];
  for (const phase of ["sweep", "settle", "resume"]) {
    for (const [act, cause] of stops) {
      // After the plain "stopped" the noise node is gone: no second one.
      if (phase === "resume" && act === stops[3][0]) continue;
      const why = phase + " " + cause;
      const h = atLevel();
      const hm = toMeasure(h, 0);
      let r = [];
      if (phase !== "sweep") h.sweepReady(hm[1].token, unitSweep());
      if (phase === "resume") {
        h.output(STOPPED, 0);
        r = h.tick(1000);
        eq(types(r), "resume", why);
      }
          silent(act(h), why);
      assert(h.step !== STEP.MEASURE, why);
      eq(h.notice.cause, cause, why);
      if (r.length) eq(h.resumed(r[0].token).length, 0, why + ": late resume");
      silent(h.tick(5000), why + ": later tick");
      eq(settled(h, hm[1].token, unitSweep(), 6000).length, 0, why + ": stale");
    }
  }
  // A retry waits again from its own "stopped".
  const f = atLevel();
  const fm = toMeasure(f, 0);
  f.sweepReady(fm[1].token, unitSweep());
  f.output(STOPPED, 0);
  f.userStop();
  const m = toMeasure(f, 10000);
  f.sweepReady(m[1].token, unitSweep());
  eq(f.tick(10900).length, 0, "the old stopped does not count");
  f.output(STOPPED, 10500);
  eq(f.tick(11250).length, 0);
  eq(types(f.tick(11500)), "resume");
  // In the wait the mic may fall freely: the room decays.
  const g = atLevel();
  toMeasure(g, 0);
  eq(g.meter(10, { peakDbfs: -90, rmsDbfs: -100 }).length, 0);
  eq(g.step, STEP.MEASURE);
}

export async function test_measure_needs_a_running_level_check_with_reading() {
  const f = atLevel();
  eq(f.measure(0).length, 0, "not started");
  f.startLevel(0);
  eq(f.measure(0).length, 0, "no reading yet");
  f.meter(0, QUIET);
  f.userStop();
  eq(f.measure(0).length, 0, "stopped");
}

/** AE a1736914: each capture's measured output onset goes to the analysis. */
export async function test_onset_reaches_the_analysis() {
  const f = atLevel();
  const m = toMeasure(f);
  eq(f.output({ type: "started", frame: 7 }).length, 0, "level-check noise");
  eq(f.run.onsetFrame, null, "not a capture's onset");
  const s = settled(f, m[1].token, unitSweep());
  f.output({ type: "started", frame: 1000 + 128, clock: 5 });
  f.output({ type: "started", frame: 5000, clock: 5 });
  const s2 = f.recorded(s[0].token, new Float32Array(1), 1000, 5, null);
  eq(types(s2), "record,sweep-start");
  eq(f.run.onsetFrame, null, "reset for capture 2");
  f.output({ type: "started", frame: 9999, clock: 5 });
  const a = f.recorded(s2[0].token, new Float32Array(1), 9999, 5, null);
  eq(a[1].request.onsets.join(), "128,0", "one quantum late, then on time");
  eq(a[1].request.captures.length, 2);
}

/** AE a1736914: an unknown or implausible onset fails closed (audio error). */
export async function test_unknown_onset_is_an_audio_error() {
  const limit = FLOW.MAX_ONSET_S * SR;
  eq(limit, 2400, "the same bound as webrc_pipeline.MAX_ONSET_S");
  for (const onset of [-limit, limit]) {
    const f = atLevel();
    const s = settled(f, toMeasure(f)[1].token, unitSweep());
    eq(types(rec(f, s[0].token, new Float32Array(1), onset)),
      "record,sweep-start", "in bounds: " + onset);
  }
  const bad = [
    ["no started", (f, t) => f.recorded(t, new Float32Array(1), 4096, 1, null)],
    ["no started, frame 0", (f, t) => f.recorded(t, new Float32Array(1), 0, 1, null)],
    ["late", (f, t) => rec(f, t, new Float32Array(1), limit + 1)],
    ["early", (f, t) => rec(f, t, new Float32Array(1), -limit - 1)],
    ["no start frame", (f, t) => {
      f.output({ type: "started", frame: 4096, clock: 1 });
      return f.recorded(t, new Float32Array(1), undefined, 1, null);
    }],
    ["bad frame", (f, t) => {
      f.output({ type: "started", frame: 4096.5, clock: 1 });
      return f.recorded(t, new Float32Array(1), 4096, 1, null);
    }],
    // AE onset clock condition: frames from two contexts don't compare.
    ["other clock", (f, t) => {
      f.output({ type: "started", frame: 4096, clock: 1 });
      return f.recorded(t, new Float32Array(1), 4096, 2, null);
    }],
    ["no recording clock", (f, t) => {
      f.output({ type: "started", frame: 4096, clock: 1 });
      return f.recorded(t, new Float32Array(1), 4096, undefined, null);
    }],
    ["no onset clock", (f, t) => {
      f.output({ type: "started", frame: 4096 });
      return f.recorded(t, new Float32Array(1), 4096, undefined, null);
    }],
  ];
  for (const [why, act] of bad) {
    const f = atLevel();
    const s = settled(f, toMeasure(f)[1].token, unitSweep());
    eq(types(act(f, s[0].token)), "output-stop,record-cancel", why);
    eq(f.step, STEP.LEVEL, why);
    eq(f.notice.cause, STOP.AUDIO_ERROR, why);
    eq(f.canStart, false, "held: " + why);
  }
  // Capture 2 needs its own onset.
  const f = atLevel();
  const s = settled(f, toMeasure(f)[1].token, unitSweep());
  const s2 = rec(f, s[0].token, new Float32Array(1));
  eq(types(f.recorded(s2[0].token, new Float32Array(1), 4096, 1, null)),
    "output-stop,record-cancel", "no onset for capture 2");
}

/**
 * AE 42dada94 G2-G4: a capture the meter flagged for a render clock glitch
 * is never used. It is rejected (not an audio error) with the UX 7b893ef9
 * text, in either capture, before the onset check; no silent re-capture.
 * A capture with no clock check fails closed the same way.
 */
export async function test_a_clock_glitch_capture_is_not_used() {
  const TEXT = "Measurement not used: the audio recording skipped for a " +
    "moment, so it can't be trusted. This can happen when the computer is " +
    "busy. Close other apps or browser tabs, then restart.";
  const GLITCH = { before: 627584, after: 627584 };
  const cases = [
    ["capture 1", 0, GLITCH, 0],
    ["capture 2", 1, GLITCH, 0],
    ["capture 1, bad onset too", 0, GLITCH, 1e6],
    ["no clock check", 0, undefined, 0],
  ];
  for (const [why, before, glitch, onset] of cases) {
    const f = atLevel();
    let s = settled(f, toMeasure(f)[1].token, unitSweep());
    eq(s[0].lookback, FLOW.MAX_ONSET_S * SR, "the check covers the onset bound");
    for (let i = 0; i < before; i++) s = rec(f, s[0].token, new Float32Array(1));
    f.output({ type: "started", frame: 4096 + onset, clock: 1 });
    eq(types(f.recorded(s[0].token, new Float32Array(1), 4096, 1, glitch)),
      "output-stop", why);
    eq(f.step, STEP.LEVEL, why);
    eq(f.notice.cause, "rejected", why);
    eq(f.notice.text, TEXT, why);
    eq(FLOW_TEXT.CLOCK_GLITCH, TEXT);
    eq(f.notice.detail, undefined, why);
    eq(f.run.captures.length, 0, "discarded: " + why);
    eq(f.run.pending, null, "no re-capture: " + why);
    eq(f.canStart, true, "not held: " + why);
    eq(types(f.startLevel(0)), "noise-start", why);
  }
}

/** E4: an auto-STOP during the sweep returns to the level check, discards. */
export async function test_sweep_auto_stop_discards_captures() {
  const stops = [
    [(f) => f.meter(0, { peakDbfs: -30, rmsDbfs: -43.9 }), STOP.SWEEP_RISE],
    [(f) => f.meter(0, { peakDbfs: -0.9, rmsDbfs: -50 }), STOP.MIC_CLIP],
    [(f) => f.output({ type: "clamped" }), STOP.CAP],
    [(f) => f.hidden(), STOP.HIDDEN],
    [(f) => f.userStop(), STOP.USER],
  ];
  for (const [act, cause] of stops) {
    const f = atLevel();
    const m = toMeasure(f); // level-check mic RMS -50
    const s = settled(f, m[1].token, unitSweep());
    const s2 = rec(f, s[0].token, new Float32Array(10));
    eq(f.meter(0, { peakDbfs: -30, rmsDbfs: -44.1 }).length, 0, "5.9 dB rise ok");
    eq(types(act(f)), "output-stop,record-cancel", cause);
    eq(f.step, STEP.LEVEL);
    eq(f.notice.cause, cause);
    eq(f.notice.text, stopMessage(cause));
    eq(f.notice.detail, FLOW_TEXT.BOTH_DISCARDED, "stop in capture 2: " + cause);
    eq(f.recorded(s2[0].token, new Float32Array(10)).length, 0,
      "late capture discarded: " + cause);
    eq(f.measure(0).length, 0, "needs a fresh level check");
    release(f, cause);
    eq(types(f.startLevel(0)), "noise-start");
  }
}

/** A stop in capture 1 has nothing more to discard: no W1 line. */
export async function test_stop_in_capture_1_has_no_both_discarded_line() {
  const f = atLevel();
  const m = toMeasure(f);
  settled(f, m[1].token, unitSweep());
  f.userStop();
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, stopMessage(STOP.USER));
  eq(f.notice.detail, undefined);
  eq(FLOW_TEXT.BOTH_DISCARDED, "Both captures were discarded: the two " +
    "captures must be taken back to back. Press Start level check to " +
    "measure again.");
}

export async function test_sweep_failure_names_the_error() {
  const f = atLevel();
  const m = toMeasure(f);
  eq(f.sweepFailed(m[1].token + 1, "x").length, 0, "other token");
  eq(f.step, STEP.MEASURE);
  eq(f.sweepFailed(m[1].token, "ValueError: bad limit").length, 0, "no sound");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, "ValueError: bad limit");
  eq(settled(f, m[1].token, unitSweep()).length, 0, "late sweep dropped");
}

export async function test_stop_while_waiting_for_sweep_or_analysis() {
  const f = atLevel();
  const m = toMeasure(f);
  eq(f.userStop().length, 0, "nothing sounding");
  eq(f.step, STEP.LEVEL);
  eq(settled(f, m[1].token, unitSweep()).length, 0, "stale sweep");

  const g = atLevel();
  const gm = toMeasure(g);
  const s = settled(g, gm[1].token, unitSweep());
  const s2 = rec(g, s[0].token, new Float32Array(1));
  const a = rec(g, s2[0].token, new Float32Array(1));
  g.hidden();
  eq(g.step, STEP.LEVEL);
  eq(g.analysisDone(a[1].token, { fileName: "x.wav" }).length, 0);
  eq(g.filters.size, 0, "stale analysis not kept");
}

export async function test_sweep_over_cap_is_refused() {
  const f = atLevel();
  const m = toMeasure(f);
  const spike = new Float32Array(SR); // RMS tiny, peak huge after the gain
  spike[100] = 1;
  const cmds = settled(f, m[1].token, spike);
  eq(cmds.length, 0, "no sound");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, FLOW_TEXT.SWEEP_OVER_CAP);
  const g = atLevel();
  const gm = toMeasure(g);
  eq(settled(g, gm[1].token, new Float32Array(SR)).length, 0, "silent sweep");
  assert(CAP_LINEAR > 0);
}

export async function test_analysis_failure_names_the_error() {
  const f = atLevel();
  const m = toMeasure(f);
  const s = settled(f, m[1].token, unitSweep());
  const s2 = rec(f, s[0].token, new Float32Array(1));
  const a = rec(f, s2[0].token, new Float32Array(1));
  f.analysisFailed(a[1].token, "Capture rejected: SNR 12 dB below 20 dB.");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, "Capture rejected: SNR 12 dB below 20 dB.");
  eq(f.filters.size, 0);
  // UX 09da95d8 Q1: the notice stays until Start level check, no timer.
  f.tick(10 * 60 * 1000);
  f.meter(10 * 60 * 1000, { peakDbfs: -40, rmsDbfs: -50 });
  eq(f.notice && f.notice.text, "Capture rejected: SNR 12 dB below 20 dB.");
  f.startLevel(10 * 60 * 1000);
  eq(f.notice, null, "Start level check clears it");
}

export async function test_analyze_request_records_calibration() {
  const f = atLevel({ cal: true });
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  const m = f.measure(0);
  const s = settled(f, m[1].token, unitSweep());
  const s2 = rec(f, s[0].token, new Float32Array(1));
  const r = rec(f, s2[0].token, new Float32Array(1))[1].request;
  eq(r.calibrated, true);
  eq(r.calibrationFile, "7161942.txt");
  eq(r.calibrationText, UMIK_TEXT, "the curve goes to the analysis (K2)");
}

/** E5b D3: a file not bound to the mic is uncalibrated, its curve stays out. */
export async function test_unbound_calibration_sends_no_curve() {
  const f = new Flow();
  f.loadCalibration("7161942.txt", UMIK, UMIK_TEXT);  // no mic yet: unbound
  f.setAudio(AUDIO);
  f.setChannel(2);
  f.setDeclaration(sub40());
  f.confirmSetup();
  ackAll(f);
  assert(f.calibrationUnbound);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  const m = f.measure(0);
  const s = settled(f, m[1].token, unitSweep());
  const s2 = rec(f, s[0].token, new Float32Array(1));
  const r = rec(f, s2[0].token, new Float32Array(1))[1].request;
  eq(r.calibrated, false);
  eq(r.calibrationText, null);
}

// -- E5: device and rate changes --------------------------------------------

function finishedFilter(f, name) {
  const m = toMeasure(f);
  const s = settled(f, m[1].token, unitSweep());
  const s2 = rec(f, s[0].token, new Float32Array(1));
  const a = rec(f, s2[0].token, new Float32Array(1));
  f.analysisDone(a[1].token, { fileName: name, wavBytes: new Uint8Array(1) });
}

/** E5d: everything is cleared, the cal binding too; finished filters marked. */
export async function test_device_change_resets_and_marks() {
  const f = atLevel({ cal: true });
  finishedFilter(f, "sub_ch2_browser-generated.wav");
  const m = toMeasure(f);
  const s = settled(f, m[1].token, unitSweep());
  const cmds = f.deviceChange({ ...AUDIO });
  eq(types(cmds), "output-stop,record-cancel,meter-calibration");
  eq(cmds[2].splOffsetDb, null, "meter uncalibrated");
  eq(f.step, STEP.SETUP);
  eq(f.notice.text, stopMessage(STOP.DEVICE));
  eq(f.ack, false, "D1");
  eq(f.channel, null, "D2");
  eq(f.decl.role, null, "D2");
  eq(f.decl.capabilityConfirmed, false, "D2");
  eq(f.calibrated, false, "D3: same mic, still unbound");
  eq(f.calibrationUnbound, true);
  eq(f.recorded(s[0].token, new Float32Array(1)).length, 0, "D4 capture");
  const d = f.downloads();
  eq(d.length, 1, "D4: finished filter kept");
  eq(d[0].name, "sub_ch2_browser-generated-measured-before-device-change.wav");
  eq(d[0].preDeviceChange, true);

  // No sound until ack and declarations are confirmed again.
  eq(f.startLevel(0).length, 0);
  f.setChannel(2);
  f.setDeclaration(sub40());
  f.confirmSetup();
  eq(f.step, STEP.ACK, "ack again");
  eq(f.startLevel(0).length, 0);
  ackAll(f);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -20, rmsDbfs: -30 }); // 91 dB SPL if calibrated
  eq(f.notice, null, "uncalibrated until rebound");
}

export async function test_device_change_rebind_restores_calibration() {
  const f = atLevel({ cal: true });
  f.deviceChange({ ...AUDIO, micId: "mic-B", micLabel: "" });
  eq(f.calibrated, false);
  const cmds = f.bindCalibration();
  eq(types(cmds), "meter-calibration");
  close(cmds[0].splOffsetDb, 121.378, 1e-12);
  eq(f.calibrated, true);
  // A different mic id later unbinds it again.
  f.setAudio({ ...AUDIO, micId: "mic-C" });
  eq(f.calibrated, false);
}

export async function test_mark_downloaded_per_channel() {
  const f = atLevel();
  finishedFilter(f, "a_ch2.wav");
  f.backToSetup();
  f.setChannel(3);
  f.confirmSetup();
  finishedFilter(f, "b_ch3.wav");
  f.markDownloaded(2);
  assert(f.hasUnsavedWork(), "channel 3 not downloaded");
  f.markDownloaded(3);
  eq(f.hasUnsavedWork(), false);
}

export async function test_mixed_download_marks_only_pre_change() {
  const f = atLevel();
  finishedFilter(f, "a_ch2.wav");
  f.deviceChange({ ...AUDIO });
  f.setChannel(3);
  f.setDeclaration(sub40());
  f.confirmSetup();
  ackAll(f);
  finishedFilter(f, "b_ch3.wav");
  const names = f.downloads().map((d) => d.name).sort();
  eq(names.join(), "a_ch2-measured-before-device-change.wav,b_ch3.wav");
}

export async function test_rate_change_returns_to_setup() {
  const f = atLevel();
  f.startLevel(0);
  const cmds = f.rateChange({ outputRate: 44100 });
  eq(types(cmds), "output-stop");
  eq(f.step, STEP.SETUP);
  eq(f.notice.text, stopMessage(STOP.RATE, { rate: 44100 }));
  assert(f.setupProblems()[0].includes("44100 Hz"));
  f.confirmSetup();
  eq(f.step, STEP.SETUP, "2a red state");
}

export async function test_marked_name() {
  eq(markedName("x.wav"), "x-measured-before-device-change.wav");
  eq(markedName("x"), "x-measured-before-device-change");
  eq(LIMITS.REQUIRED_RATE, SR);
}
