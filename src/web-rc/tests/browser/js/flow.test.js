// Flow controller (flow.js): AC11 steps, AC2-AC4 gating, E4 and E5 stops.

import { assert, close, eq } from "./assert.js";
import { FLOW, FLOW_TEXT, Flow, STEP, markedName } from "../../../static/js/flow.js";
import { parseCalibration } from "../../../static/js/calibration.js";
import { crestEntry, topStepDbfs, unitGain } from "../../../static/js/crest.js";
import { crestSeed } from "../../../static/js/crest-plan.js";
import { CAP_LINEAR } from "../../../static/js/output-core.js";
import {
  LIMITS, ROLE, STOP, changeRole, levelNoiseBand, stopMessage,
} from "../../../static/js/safety.js";

const SR = 48000;
const OFF = { echoCancellation: false, noiseSuppression: false,
  autoGainControl: false };
const AUDIO = { outputRate: SR, inputRate: SR, outputChannels: 8,
  dspSettings: OFF, micId: "mic-A", micLabel: "UMIK-1" };
const UMIK = parseCalibration('"Sens Factor =-1.378dB, SERNO: 7161942"\n' +
  "20.000\t-0.13\n");
const QUIET = { peakDbfs: -60, rmsDbfs: -70 };

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
  if (cal) f.loadCalibration("7161942.txt", UMIK);
  f.confirmSetup();
  f.acknowledge();
  eq(f.step, STEP.LEVEL);
  return f;
}

const types = (cmds) => cmds.map((c) => c.type).join(",");

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
  return f.measure();
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
  f.acknowledge();
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
  f.acknowledge();
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -46.5 }); // 74.9 dB SPL
  eq(f.canStepUp(), true, "75 dB SPL not yet reached");
  f.meter(0, { peakDbfs: -40, rmsDbfs: -46.3 }); // 75.1 dB SPL
  eq(f.canStepUp(), false);
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
    const again = f.startLevel(40000);
    close(again[0].gain, unitGain(crestEntry(levelNoiseBand(ROLE.SUBWOOFER, 40),
      2), -60), 1e-15, "fresh start at -60 after " + cause);
  }
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
  eq(f.measure().length, 0, "once");

  const unit = unitSweep();
  const s = f.sweepReady(m[1].token, unit);
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
  const s2 = f.recorded(s[0].token, cap1);
  eq(types(s2), "record,sweep-start", "second capture, same sweep");
  assert(s2[0].token !== s[0].token);
  eq(s2[1].gain, s[1].gain);
  eq(f.recorded(s[0].token, cap1).length, 0, "old token ignored");
  const cap2 = new Float32Array(10);
  const a = f.recorded(s2[0].token, cap2);
  eq(types(a), "analyze");
  const r = a[0].request;
  eq(r.captures.length, 2);
  eq(r.captures[0], cap1, "capture 1 = filter");
  eq(r.captures[1], cap2, "capture 2 = hold-out");
  eq(r.played, s[1].samples, "the exact played buffer");
  eq(r.gain, s[1].gain);
  eq(r.decl.role, ROLE.SUBWOOFER);
  eq(r.calibrated, false);
  eq(r.calibrationFile, null);
  eq(f.step, STEP.MEASURE);
  assert(f.hasUnsavedWork());

  f.analysisDone(a[0].token, { fileName: "sub_ch2.wav", wavBytes: new Uint8Array(4) });
  eq(f.step, STEP.RESULT);
  const d = f.downloads();
  eq(d.length, 1);
  eq(d[0].name, "sub_ch2.wav");
  eq(d[0].preDeviceChange, false);
  assert(f.hasUnsavedWork(), "not downloaded yet");
  f.markDownloaded();
  eq(f.hasUnsavedWork(), false);
}

export async function test_measure_needs_a_running_level_check_with_reading() {
  const f = atLevel();
  eq(f.measure().length, 0, "not started");
  f.startLevel(0);
  eq(f.measure().length, 0, "no reading yet");
  f.meter(0, QUIET);
  f.userStop();
  eq(f.measure().length, 0, "stopped");
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
    const s = f.sweepReady(m[1].token, unitSweep());
    const s2 = f.recorded(s[0].token, new Float32Array(10));
    eq(f.meter(0, { peakDbfs: -30, rmsDbfs: -44.1 }).length, 0, "5.9 dB rise ok");
    eq(types(act(f)), "output-stop,record-cancel", cause);
    eq(f.step, STEP.LEVEL);
    eq(f.notice.cause, cause);
    eq(f.notice.text, stopMessage(cause));
    eq(f.recorded(s2[0].token, new Float32Array(10)).length, 0,
      "late capture discarded: " + cause);
    eq(f.measure().length, 0, "needs a fresh level check");
    eq(types(f.startLevel(0)), "noise-start");
  }
}

export async function test_stop_while_waiting_for_sweep_or_analysis() {
  const f = atLevel();
  const m = toMeasure(f);
  eq(f.userStop().length, 0, "nothing sounding");
  eq(f.step, STEP.LEVEL);
  eq(f.sweepReady(m[1].token, unitSweep()).length, 0, "stale sweep");

  const g = atLevel();
  const gm = toMeasure(g);
  const s = g.sweepReady(gm[1].token, unitSweep());
  const s2 = g.recorded(s[0].token, new Float32Array(1));
  const a = g.recorded(s2[0].token, new Float32Array(1));
  g.hidden();
  eq(g.step, STEP.LEVEL);
  eq(g.analysisDone(a[0].token, { fileName: "x.wav" }).length, 0);
  eq(g.filters.size, 0, "stale analysis not kept");
}

export async function test_sweep_over_cap_is_refused() {
  const f = atLevel();
  const m = toMeasure(f);
  const spike = new Float32Array(SR); // RMS tiny, peak huge after the gain
  spike[100] = 1;
  const cmds = f.sweepReady(m[1].token, spike);
  eq(cmds.length, 0, "no sound");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, FLOW_TEXT.SWEEP_OVER_CAP);
  const g = atLevel();
  const gm = toMeasure(g);
  eq(g.sweepReady(gm[1].token, new Float32Array(SR)).length, 0, "silent sweep");
  assert(CAP_LINEAR > 0);
}

export async function test_analysis_failure_names_the_error() {
  const f = atLevel();
  const m = toMeasure(f);
  const s = f.sweepReady(m[1].token, unitSweep());
  const s2 = f.recorded(s[0].token, new Float32Array(1));
  const a = f.recorded(s2[0].token, new Float32Array(1));
  f.analysisFailed(a[0].token, "Capture rejected: SNR 12 dB below 20 dB.");
  eq(f.step, STEP.LEVEL);
  eq(f.notice.text, "Capture rejected: SNR 12 dB below 20 dB.");
  eq(f.filters.size, 0);
}

export async function test_analyze_request_records_calibration() {
  const f = atLevel({ cal: true });
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  const m = f.measure();
  const s = f.sweepReady(m[1].token, unitSweep());
  const s2 = f.recorded(s[0].token, new Float32Array(1));
  const r = f.recorded(s2[0].token, new Float32Array(1))[0].request;
  eq(r.calibrated, true);
  eq(r.calibrationFile, "7161942.txt");
}

// -- E5: device and rate changes --------------------------------------------

function finishedFilter(f, name) {
  const m = toMeasure(f);
  const s = f.sweepReady(m[1].token, unitSweep());
  const s2 = f.recorded(s[0].token, new Float32Array(1));
  const a = f.recorded(s2[0].token, new Float32Array(1));
  f.analysisDone(a[0].token, { fileName: name, wavBytes: new Uint8Array(1) });
}

/** E5d: everything is cleared, the cal binding too; finished filters marked. */
export async function test_device_change_resets_and_marks() {
  const f = atLevel({ cal: true });
  finishedFilter(f, "sub_ch2_browser-generated.wav");
  const m = toMeasure(f);
  const s = f.sweepReady(m[1].token, unitSweep());
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
  f.acknowledge();
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

export async function test_mixed_download_marks_only_pre_change() {
  const f = atLevel();
  finishedFilter(f, "a_ch2.wav");
  f.deviceChange({ ...AUDIO });
  f.setChannel(3);
  f.setDeclaration(sub40());
  f.confirmSetup();
  f.acknowledge();
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
