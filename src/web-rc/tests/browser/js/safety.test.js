// AC2-AC4 safety rules (safety.js).

import { assert, close, eq, throws } from "./assert.js";
import {
  LIMITS, LevelCheck, STOP, checkDeclaration, checkDspFlags,
  checkSampleRates, micStopCause, stopMessage, stopReturnsToSetup,
  sweepPlan, sweepStopCause,
} from "../../../static/js/safety.js";

const QUIET = { rmsDbfs: -70, peakDbfs: -60, splDb: null };

function levelCheck(micTarget = { dbfs: -30 }) {
  return new LevelCheck({ maxLevelDbfs: -36, micTarget });
}

export async function test_limits_are_frozen_constants() {
  eq(LIMITS.OUTPUT_PEAK_CAP_DBFS, -20);
  eq(LIMITS.START_DBFS, -60);
  eq(LIMITS.STEP_DB, 6);
  eq(LIMITS.IDLE_TIMEOUT_MS, 30000);
  eq(LIMITS.SWEEP_MAX_S, 10);
  assert(Object.isFrozen(LIMITS));
  try { LIMITS.OUTPUT_PEAK_CAP_DBFS = 0; } catch (e) { /* strict mode */ }
  eq(LIMITS.OUTPUT_PEAK_CAP_DBFS, -20, "cap cannot be raised");
}

export async function test_rate_refusal() {
  eq(checkSampleRates(48000, 48000).ok, true);
  const out = checkSampleRates(44100, 48000);
  eq(out.ok, false);
  eq(out.message, "Can't measure: this audio device runs at 44100 Hz. " +
    "mugge filters need 48 kHz. Set the device to 48 kHz in your system's " +
    "audio settings, then reload this page.");
  const inp = checkSampleRates(48000, 96000);
  eq(inp.ok, false);
  assert(inp.message.includes("96000 Hz"), "names the input rate");
  eq(checkSampleRates(48000, undefined).ok, false, "unknown input rate");
}

export async function test_dsp_flags_must_read_back_off() {
  const off = { echoCancellation: false, noiseSuppression: false,
    autoGainControl: false };
  eq(checkDspFlags(off).ok, true);
  for (const key of Object.keys(off)) {
    const on = { ...off, [key]: true };
    const r = checkDspFlags(on);
    eq(r.ok, false, key + " on");
    eq(r.reasons.length, 1);
    const missing = { ...off };
    delete missing[key];
    eq(checkDspFlags(missing).ok, false, key + " missing");
  }
  eq(checkDspFlags(null).reasons.length, 3);
}

function decl(over) {
  return { limitHz: 20, capabilityConfirmed: true, enclosure: "closed",
    ...over };
}

export async function test_declaration_limit_range() {
  eq(checkDeclaration(decl()).ok, true);
  eq(checkDeclaration(decl({ limitHz: 500 })).ok, true);
  eq(checkDeclaration(decl({ limitHz: 19.9 })).ok, false, "below 20");
  eq(checkDeclaration(decl({ limitHz: 501 })).ok, false, "above 500");
  eq(checkDeclaration(decl({ limitHz: NaN })).ok, false, "NaN");
  eq(checkDeclaration(decl({ limitHz: "20" })).ok, false, "string");
  eq(LIMITS.LIMIT_DEFAULT_HZ, 20);
}

export async function test_declaration_needs_capability_tick() {
  eq(checkDeclaration(decl({ capabilityConfirmed: false })).ok, false);
  eq(checkDeclaration(decl({ capabilityConfirmed: undefined })).ok, false);
  eq(checkDeclaration(decl({ enclosure: undefined })).ok, false);
}

export async function test_declaration_port_below_tuning() {
  const above = checkDeclaration(decl({ limitHz: 40, enclosure: "ported",
    portTuningHz: 35 }));
  eq(above.ok, true);
  eq(above.portWarning, "");
  const below = checkDeclaration(decl({ limitHz: 20, enclosure: "ported",
    portTuningHz: 35 }));
  eq(below.ok, false, "needs second confirmation");
  assert(below.portWarning.includes("cone moves much further"));
  const confirmed = checkDeclaration(decl({ limitHz: 20, enclosure: "ported",
    portTuningHz: 35, portConfirmed: true }));
  eq(confirmed.ok, true);
  assert(confirmed.portWarning !== "", "warning stays visible");
  eq(checkDeclaration(decl({ enclosure: "ported" })).ok, false,
    "tuning required");
}

export async function test_sweep_plan() {
  const p = sweepPlan(20, 8);
  eq(p.fStartHz, 20);
  eq(p.fEndHz, 20000);
  close(p.hpfHz, 16, 1e-12);
  eq(p.seconds, 8);
  eq(p.captureSeconds, 9);
  eq(sweepPlan(20, 30).seconds, 10, "at most 10 s");
  eq(sweepPlan(20, 30).captureSeconds, 11);
}

export async function test_level_check_starts_at_minus_60_and_steps_6() {
  const lc = levelCheck();
  const s = lc.start(0);
  eq(s.gainDbfs, -60);
  eq(s.rampFromZero, true);
  eq(lc.stepUp(1000).gainDbfs, -54);
  eq(lc.stepUp(2000).gainDbfs, -48);
  eq(lc.stepUp(3000).rampFromZero, false);
}

export async function test_level_check_ceiling() {
  const lc = levelCheck(); // max -36: -60, -54, -48, -42, -36
  lc.start(0);
  for (let i = 0; i < 4; i++) assert(lc.stepUp(i) !== null);
  eq(lc.levelDbfs, -36);
  eq(lc.canStepUp(), false);
  eq(lc.stepUp(10), null);
  eq(lc.levelDbfs, -36);
  throws(() => new LevelCheck({ maxLevelDbfs: -20, micTarget: { dbfs: -30 } }));
}

export async function test_level_check_30s_timeout() {
  const lc = levelCheck();
  lc.start(0);
  eq(lc.update(29999, QUIET), null);
  eq(lc.update(30000, QUIET), STOP.TIMEOUT);
  eq(lc.running, false);
  eq(lc.stopCause, STOP.TIMEOUT);
  eq(stopMessage(STOP.TIMEOUT), "Level check stopped after 30 s without " +
    "input. Press Start level check to continue.");
}

export async function test_plus_click_resets_timer_even_at_ceiling() {
  const lc = levelCheck();
  lc.start(0);
  for (let i = 0; i < 4; i++) lc.stepUp(1000);
  lc.stepUp(25000); // at the ceiling: no change, but a user action
  eq(lc.update(54999, QUIET), null);
  eq(lc.update(55000, QUIET), STOP.TIMEOUT);
}

export async function test_clamp_touch_stops_with_cap_message() {
  const lc = levelCheck();
  lc.start(0);
  eq(lc.update(10, { ...QUIET, outputClamped: true }), STOP.CAP);
  eq(stopMessage(STOP.CAP), "Stopped: level cap reached. Lower the amp or " +
    "interface gain, then restart.");
}

export async function test_mic_clip_and_spl_stop() {
  eq(micStopCause({ peakDbfs: -1, splDb: null }), STOP.MIC_CLIP);
  eq(micStopCause({ peakDbfs: -1.01, splDb: null }), null);
  eq(micStopCause({ peakDbfs: -10, splDb: 90 }), null);
  eq(micStopCause({ peakDbfs: -10, splDb: 90.1 }), STOP.MIC_SPL);
  const lc = levelCheck({ splDb: 75 });
  lc.start(0);
  eq(lc.update(10, { rmsDbfs: -20, peakDbfs: -0.5, splDb: 80 }),
    STOP.MIC_CLIP);
}

export async function test_restart_is_fresh_start() {
  const lc = levelCheck();
  lc.start(0);
  lc.stepUp(1);
  lc.stepUp(2);
  lc.update(40000, QUIET);
  eq(lc.running, false);
  eq(lc.stepUp(40001), null, "no step while stopped");
  const s = lc.start(50000);
  eq(s.gainDbfs, -60);
  eq(s.rampFromZero, true);
  eq(lc.stopCause, null);
  eq(lc.update(79999, QUIET), null, "timer restarted");
}

export async function test_target_reached_disables_plus() {
  const cal = levelCheck({ splDb: 75 });
  cal.start(0);
  eq(cal.update(1, { rmsDbfs: -40, peakDbfs: -30, splDb: 74.9 }), null);
  eq(cal.canStepUp(), true);
  eq(cal.update(2, { rmsDbfs: -40, peakDbfs: -30, splDb: 75 }), null);
  eq(cal.canStepUp(), false);
  eq(cal.stepUp(3), null);

  const uncal = levelCheck({ dbfs: -30 });
  eq(uncal.calibrated, false);
  uncal.start(0);
  uncal.update(1, { rmsDbfs: -30, peakDbfs: -20, splDb: null });
  eq(uncal.canStepUp(), false);
}

export async function test_sweep_rise_stop() {
  eq(sweepStopCause(-40, { rmsDbfs: -34, peakDbfs: -25, splDb: null }), null);
  eq(sweepStopCause(-40, { rmsDbfs: -33.9, peakDbfs: -25, splDb: null }),
    STOP.SWEEP_RISE);
  eq(sweepStopCause(-40, { rmsDbfs: -50, peakDbfs: 0, splDb: null }),
    STOP.MIC_CLIP);
}

export async function test_device_and_rate_stops_return_to_setup() {
  eq(stopReturnsToSetup(STOP.DEVICE), true);
  eq(stopReturnsToSetup(STOP.RATE), true);
  eq(stopReturnsToSetup(STOP.TIMEOUT), false);
  eq(stopReturnsToSetup(STOP.CAP), false);
}
