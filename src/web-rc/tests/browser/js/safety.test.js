// AC2-AC4 safety rules (safety.js).

import { assert, close, eq, throws } from "./assert.js";
import {
  LIMITS, LevelCheck, ROLE, ROLE_LIMITS, STOP, SUB_LIMIT_REFUSAL,
  capabilityText, changeRole, checkDeclaration, checkDspFlags,
  checkSampleRates, levelNoiseBand, levelNoiseBandLabel, micStopCause,
  roleFileTag, speakerDict, stopMessage, stopReturnsToSetup, sweepPlan,
  sweepStopCause,
} from "../../../static/js/safety.js";

const QUIET = { rmsDbfs: -70, peakDbfs: -60 };
// Example calibration: 0 dBFS = 120 dB SPL, so 75 dB SPL = -45 dBFS.
const CAL = 120;

function levelCheck(splOffsetDb = null) {
  return new LevelCheck({ maxLevelDbfs: -36, splOffsetDb });
}

export async function test_limits_are_frozen_constants() {
  eq(LIMITS.OUTPUT_PEAK_CAP_DBFS, -20);
  eq(LIMITS.START_DBFS, -60);
  eq(LIMITS.STEP_DB, 6);
  eq(LIMITS.IDLE_TIMEOUT_MS, 30000);
  eq(LIMITS.SWEEP_MAX_S, 10);
  eq(LIMITS.MIC_CLIP_DBFS, -1);
  eq(LIMITS.MIC_MAX_SPL_DB, 90);
  eq(LIMITS.MIC_MAX_PEAK_SPL_DB, 105);
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
  return { role: ROLE.FULLRANGE, limitHz: 20, capabilityConfirmed: true,
    enclosure: "closed", ...over };
}

export async function test_declaration_limit_range_fullrange() {
  eq(checkDeclaration(decl()).ok, true);
  eq(checkDeclaration(decl({ limitHz: 500 })).ok, true);
  eq(checkDeclaration(decl({ limitHz: 19 })).ok, false, "below 20");
  eq(checkDeclaration(decl({ limitHz: 501 })).ok, false, "above 500");
  eq(checkDeclaration(decl({ limitHz: 40.5 })).ok, false, "whole Hz");
  eq(checkDeclaration(decl({ limitHz: NaN })).ok, false, "NaN");
  eq(checkDeclaration(decl({ limitHz: "20" })).ok, false, "string");
  eq(LIMITS.LIMIT_MIN_HZ, 20);
}

export async function test_declaration_limit_range_subwoofer() {
  const sub = (limitHz) => decl({ role: ROLE.SUBWOOFER, limitHz });
  eq(checkDeclaration(sub(20)).ok, true);
  eq(checkDeclaration(sub(50)).ok, true);
  eq(checkDeclaration(sub(19)).ok, false, "below 20");
  const above = checkDeclaration(sub(51));
  eq(above.ok, false, "above 50");
  eq(above.errors[0], SUB_LIMIT_REFUSAL);
  eq(SUB_LIMIT_REFUSAL, "A subwoofer limit above 50 Hz is not supported " +
    "here. Check the setting, or choose Full-range speaker.");
}

export async function test_role_defaults_and_ranges() {
  eq(ROLE_LIMITS[ROLE.FULLRANGE].defaultHz, 80);
  eq(ROLE_LIMITS[ROLE.FULLRANGE].minHz, 20);
  eq(ROLE_LIMITS[ROLE.FULLRANGE].maxHz, 500);
  eq(ROLE_LIMITS[ROLE.SUBWOOFER].defaultHz, 20);
  eq(ROLE_LIMITS[ROLE.SUBWOOFER].minHz, 20);
  eq(ROLE_LIMITS[ROLE.SUBWOOFER].maxHz, 50);
  assert(Object.isFrozen(ROLE_LIMITS[ROLE.SUBWOOFER]));
  for (const role of Object.values(ROLE)) {
    const d = changeRole(decl(), role);
    eq(checkDeclaration({ ...d, capabilityConfirmed: true }).ok, true,
      role + " default is inside its range");
  }
}

export async function test_no_role_blocks_sound() {
  for (const role of [undefined, null, "", "highpass", "lowpass"]) {
    const r = checkDeclaration(decl({ role }));
    eq(r.ok, false, String(role));
    eq(r.errors[0], "Choose what is connected to this output.");
    throws(() => speakerDict(role), "speaker dict " + role);
    throws(() => levelNoiseBand(role, 20), "noise band " + role);
    throws(() => roleFileTag(role), "file tag " + role);
  }
}

export async function test_role_change_resets() {
  const before = decl({ limitHz: 40, enclosure: "ported", portTuningHz: 45,
    portConfirmed: true });
  eq(checkDeclaration(before).ok, true);
  const after = changeRole(before, ROLE.SUBWOOFER);
  eq(after.role, ROLE.SUBWOOFER);
  eq(after.limitHz, 20, "subwoofer default");
  eq(after.capabilityConfirmed, false, "3b tick cleared");
  eq(after.portConfirmed, false, "3c tick cleared");
  eq(after.enclosure, "ported");
  eq(after.portTuningHz, 45);
  eq(checkDeclaration(after).ok, false);
  eq(changeRole(after, ROLE.FULLRANGE).limitHz, 80, "full-range default");
  throws(() => changeRole(before, "lowpass"));
}

export async function test_capability_text_follows_role() {
  eq(capabilityText(ROLE.FULLRANGE, 80), "This speaker can safely play " +
    "down to 80 Hz at moderate level. I have checked its spec sheet.");
  eq(capabilityText(ROLE.SUBWOOFER, 25), "This subwoofer can safely play " +
    "down to 25 Hz at moderate level. I have checked its spec sheet.");
  throws(() => capabilityText(undefined, 20));
}

export async function test_speaker_dict_and_file_tag() {
  eq(JSON.stringify(speakerDict(ROLE.FULLRANGE)), '{"filter_type":"highpass"}');
  eq(JSON.stringify(speakerDict(ROLE.SUBWOOFER)), '{"filter_type":"lowpass"}');
  eq(roleFileTag(ROLE.FULLRANGE), "fullrange");
  eq(roleFileTag(ROLE.SUBWOOFER), "sub");
}

export async function test_level_noise_band_per_role() {
  eq(JSON.stringify(levelNoiseBand(ROLE.FULLRANGE, 80)),
    '{"lowHz":100,"highHz":10000}');
  eq(JSON.stringify(levelNoiseBand(ROLE.SUBWOOFER, 20)),
    '{"lowHz":40,"highHz":200}');
  eq(JSON.stringify(levelNoiseBand(ROLE.SUBWOOFER, 50)),
    '{"lowHz":100,"highHz":200}');
  eq(levelNoiseBandLabel(ROLE.SUBWOOFER, 20),
    "Test noise: 40\u2013200 Hz (subwoofer)");
  eq(levelNoiseBandLabel(ROLE.FULLRANGE, 20),
    "Test noise: 100 Hz\u201310 kHz (full-range)");
}

export async function test_uncalibrated_target_is_minus_40_dbfs() {
  eq(LIMITS.MIC_TARGET_DBFS, -40);
  eq(LIMITS.MIC_TARGET_SPL_DB, 75);
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
  throws(() => new LevelCheck({ maxLevelDbfs: -20 }));
  throws(() => new LevelCheck({ maxLevelDbfs: -36, splOffsetDb: NaN }));
  throws(() => new LevelCheck({ maxLevelDbfs: -36, splOffsetDb: "120" }));
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

export async function test_mic_clip_stop_both_modes() {
  for (const off of [null, CAL]) {
    eq(micStopCause({ rmsDbfs: -60, peakDbfs: -1 }, off), STOP.MIC_CLIP);
  }
  eq(micStopCause({ rmsDbfs: -60, peakDbfs: -1.01 }, null), null);
  // Calibrated, a peak just under clip is far over 105 dB SPL: backstop.
  eq(micStopCause({ rmsDbfs: -60, peakDbfs: -1.01 }, CAL), STOP.MIC_SPL_PEAK);
  const lc = levelCheck(CAL);
  lc.start(0);
  eq(lc.update(10, { rmsDbfs: -40, peakDbfs: -0.5 }), STOP.MIC_CLIP);
}

/** E3: 90 dB SPL on the 100 ms RMS, 105 dB SPL on the true peak. */
export async function test_spl_stops_rms_and_peak() {
  // RMS below 90 dB while the peak crosses 90 dB: no stop.
  eq(micStopCause({ rmsDbfs: 89.9 - CAL, peakDbfs: 100 - CAL }, CAL), null);
  // RMS at 90 dB is not over 90; just over is.
  eq(micStopCause({ rmsDbfs: 90 - CAL, peakDbfs: 100 - CAL }, CAL), null);
  eq(micStopCause({ rmsDbfs: 90.01 - CAL, peakDbfs: 100 - CAL }, CAL),
    STOP.MIC_SPL);
  // A single click above 105 dB SPL peak with quiet RMS: stop.
  eq(micStopCause({ rmsDbfs: 60 - CAL, peakDbfs: 105 - CAL }, CAL), null);
  eq(micStopCause({ rmsDbfs: 60 - CAL, peakDbfs: 105.01 - CAL }, CAL),
    STOP.MIC_SPL_PEAK);
  // Uncalibrated: neither SPL stop can act (AE A1), only the clip.
  eq(micStopCause({ rmsDbfs: -2, peakDbfs: -1.01 }, null), null);
}

/** E4a/E4b: every auto-STOP cause has its own text. */
export async function test_stop_messages_per_cause() {
  eq(stopMessage(STOP.MIC_CLIP, { calibrated: true }),
    "Stopped: the microphone input clipped. Lower the amp or interface " +
    "output gain, then restart. Leave the microphone input gain as it is: " +
    "the SPL calibration depends on it.");
  eq(stopMessage(STOP.MIC_CLIP, { calibrated: false }),
    "Stopped: the microphone input clipped. Lower the amp or interface " +
    "output gain, or the microphone input gain, then restart.");
  eq(stopMessage(STOP.MIC_CLIP), stopMessage(STOP.MIC_CLIP,
    { calibrated: false }), "default is uncalibrated");
  eq(stopMessage(STOP.MIC_SPL), "Stopped: too loud at the microphone (over " +
    "90 dB SPL). Lower the amp or interface output gain, then restart.");
  eq(stopMessage(STOP.MIC_SPL_PEAK), "Stopped: a very loud peak at the " +
    "microphone (over 105 dB SPL). Check that nothing touched the mic. " +
    "Lower the amp or interface output gain, then restart.");
  eq(stopMessage(STOP.SWEEP_RISE), "Stopped: the sweep was more than 6 dB " +
    "louder at the microphone than the level check. Restart when ready.");
  eq(stopMessage(STOP.HIDDEN),
    "Stopped: the page was hidden. Restart when ready.");
  eq(stopMessage(STOP.DEVICE),
    "Stopped: an audio device changed. Restart when ready.");
  eq(stopMessage(STOP.RATE),
    "Stopped: the sample rate changed. Restart when ready.");
  eq(stopMessage(STOP.AUDIO_ERROR),
    "Stopped: an audio error occurred. Restart when ready.");
  eq(stopMessage("no-such-cause"), stopMessage(STOP.AUDIO_ERROR));
  const texts = Object.values(STOP).map((c) => stopMessage(c));
  eq(new Set(texts).size, texts.length, "one distinct text per cause");
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
  const cal = levelCheck(CAL);
  eq(cal.calibrated, true);
  eq(cal.micTargetRmsDbfs, 75 - CAL);
  cal.start(0);
  eq(cal.update(1, { rmsDbfs: 74.9 - CAL, peakDbfs: -30 }), null);
  eq(cal.canStepUp(), true);
  eq(cal.update(2, { rmsDbfs: 75 - CAL, peakDbfs: -30 }), null);
  eq(cal.canStepUp(), false);
  eq(cal.stepUp(3), null);

  const uncal = levelCheck(null);
  eq(uncal.calibrated, false);
  eq(uncal.micTargetRmsDbfs, -40);
  uncal.start(0);
  uncal.update(1, { rmsDbfs: -40.1, peakDbfs: -20 });
  eq(uncal.canStepUp(), true);
  uncal.update(2, { rmsDbfs: -40, peakDbfs: -20 });
  eq(uncal.canStepUp(), false);
}

export async function test_sweep_rise_stop() {
  eq(sweepStopCause(-40, { rmsDbfs: -34, peakDbfs: -25 }, null), null);
  eq(sweepStopCause(-40, { rmsDbfs: -33.9, peakDbfs: -25 }, null),
    STOP.SWEEP_RISE);
  eq(sweepStopCause(-40, { rmsDbfs: -50, peakDbfs: 0 }, null),
    STOP.MIC_CLIP);
  eq(sweepStopCause(-40, { rmsDbfs: 90.5 - CAL, peakDbfs: -25 }, CAL),
    STOP.MIC_SPL, "SPL stops apply during the sweep");
}

export async function test_device_and_rate_stops_return_to_setup() {
  eq(stopReturnsToSetup(STOP.DEVICE), true);
  eq(stopReturnsToSetup(STOP.RATE), true);
  eq(stopReturnsToSetup(STOP.TIMEOUT), false);
  eq(stopReturnsToSetup(STOP.CAP), false);
}
