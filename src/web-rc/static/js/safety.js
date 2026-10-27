// safety.js -- level-safety rules for the standalone room correction (US-179).
//
// Pure logic: no Web Audio, no DOM, no timers. The caller passes the time
// (ms) and the meter readings in; the functions return decisions. The audio
// code only ever applies what this module returns, so every rule here is
// unit-testable without sound.
//
// AC references are to US-179 r8 (978c3e1b) with errata E1 v2 (6a78af9f),
// E2 (bca0d86b), E3 (8f508af1), E4 r2 (f692681c) and E5 (df065993).

/** Code constants. No UI can change them (AC4c). */
export const LIMITS = Object.freeze({
  REQUIRED_RATE: 48000,          // AC2a
  LIMIT_MIN_HZ: 20,              // AC3a, never below 20 Hz for any role
  START_DBFS: -60,               // AC4b, level-check start
  STEP_DB: 6,                    // AC4b, one "+" click
  OUTPUT_PEAK_CAP_DBFS: -20,     // AC4c, hard cap on the actual output
  MIC_TARGET_SPL_DB: 75,         // AC4b, calibrated mic
  MIC_TARGET_DBFS: -40,          // AC4b, uncalibrated mic, RMS (AE A1)
  MIC_MAX_SPL_DB: 90,            // AC4d/E3, calibrated mic, 100 ms RMS
  MIC_MAX_PEAK_SPL_DB: 105,      // E3, calibrated mic, true-peak backstop
  MIC_CLIP_DBFS: -1,             // AC4d, mic clip (peak >= this)
  SWEEP_MAX_RISE_DB: 6,          // AC4d, sweep vs level check at the mic
  IDLE_TIMEOUT_MS: 30000,        // AC4d, level check without user action
  RAMP_MS: 10,                   // AC4e/4h
  HPF_RATIO: 0.8,                // AC4g/6b, subsonic corner = 0.8 x limit
  SWEEP_F_MAX_HZ: 20000,         // AC4g
  SWEEP_MAX_S: 10,               // AC4g
  // AE d1f133da Q1: the room's decay after a stimulus stops. The AC2d
  // capture tail (capture >= sweep + 1 s) and the wait between the level
  // noise and capture 1 (flow.js) both read it.
  ROOM_DECAY_S: 1,
});

export function dbToLinear(db) {
  return Math.pow(10, db / 20);
}

export function linearToDb(x) {
  return x > 0 ? 20 * Math.log10(x) : -Infinity;
}

// -- AC2: audio setup -------------------------------------------------------

/** AC2a: both rates must be exactly 48 kHz. No resampling. */
export function checkSampleRates(outputRate, inputRate) {
  for (const rate of [outputRate, inputRate]) {
    if (rate !== LIMITS.REQUIRED_RATE) {
      return {
        ok: false,
        message:
          "Can't measure: this audio device runs at " + rate + " Hz. " +
          "mugge filters need 48 kHz. Set the device to 48 kHz in your " +
          "system's audio settings, then reload this page.",
      };
    }
  }
  return { ok: true, message: "" };
}

const DSP_FLAGS = Object.freeze([
  ["echoCancellation", "echo cancellation"],
  ["noiseSuppression", "noise suppression"],
  ["autoGainControl", "automatic gain control"],
]);

/**
 * AC2c: the mic track's getSettings() must read every browser DSP flag back
 * as false. A missing flag counts as not off: the browser didn't confirm it.
 */
export function checkDspFlags(settings) {
  const reasons = [];
  for (const [key, label] of DSP_FLAGS) {
    if (settings == null || settings[key] !== false) {
      reasons.push("Can't measure: the browser's " + label +
        " is still on for this mic.");
    }
  }
  return { ok: reasons.length === 0, reasons };
}

/** AC2d: capture length for a sweep, in seconds. */
export function captureSeconds(sweepSeconds) {
  return sweepSeconds + LIMITS.ROOM_DECAY_S;
}

// -- AC3: per-channel declarations -----------------------------------------

/** E2a: what is connected to an output. There is no default. */
export const ROLE = Object.freeze({
  FULLRANGE: "fullrange",
  SUBWOOFER: "subwoofer",
});

/** E2b: low-limit default and range per role (Hz, whole numbers). */
export const ROLE_LIMITS = Object.freeze({
  [ROLE.FULLRANGE]: Object.freeze({ defaultHz: 80, minHz: 20, maxHz: 500 }),
  [ROLE.SUBWOOFER]: Object.freeze({ defaultHz: 20, minHz: 20, maxHz: 50 }),
});

export const SUB_LIMIT_REFUSAL =
  "A subwoofer limit above 50 Hz is not supported here. Check the " +
  "setting, or choose Full-range speaker.";

/** E5c: the inline whole-Hz refusal for a role's range. */
export function limitRangeText(role) {
  const range = ROLE_LIMITS[role];
  return "Enter the low limit as a whole number of Hz between " +
    range.minHz + " and " + range.maxHz + " (e.g. 40).";
}

/**
 * E5c: the low-limit field's text as a number, or NaN. Only plain digits
 * count; "40.5" is refused, never rounded.
 */
export function parseLimitHz(text) {
  const t = String(text ?? "").trim();
  return /^[0-9]+$/.test(t) ? Number(t) : NaN;
}

/** E5b D2: a declaration as on first load (no role, nothing confirmed). */
export function emptyDeclaration() {
  return {
    role: null, limitHz: null, capabilityConfirmed: false,
    enclosure: null, portTuningHz: null, portConfirmed: false,
  };
}

export function isRole(role) {
  return role === ROLE.FULLRANGE || role === ROLE.SUBWOOFER;
}

/** E2c: the 3b confirmation text for a role and limit. */
export function capabilityText(role, limitHz) {
  if (role === ROLE.SUBWOOFER) {
    return "This subwoofer can safely play down to " + limitHz +
      " Hz at moderate level. I have checked its spec sheet.";
  }
  if (role === ROLE.FULLRANGE) {
    return "This speaker can safely play down to " + limitHz +
      " Hz at moderate level. I have checked its spec sheet.";
  }
  throw new RangeError("no role");
}

/**
 * E2a: a role change clears the 3b and 3c confirmations and resets the
 * limit to the new role's default. Enclosure and port tuning stay.
 */
export function changeRole(decl, role) {
  if (!isRole(role)) throw new RangeError("unknown role " + role);
  return {
    ...decl,
    role,
    limitHz: ROLE_LIMITS[role].defaultHz,
    capabilityConfirmed: false,
    portConfirmed: false,
  };
}

/**
 * A new low limit clears the 3b and 3c confirmations: they name or depend
 * on the limit, so a tick for another limit never carries over.
 */
export function changeLimit(decl, limitHz) {
  return { ...decl, limitHz, capabilityConfirmed: false, portConfirmed: false };
}

/** A new enclosure or port tuning clears the separate 3c confirmation. */
export function changeEnclosure(decl, enclosure, portTuningHz) {
  return { ...decl, enclosure, portTuningHz, portConfirmed: false };
}

/**
 * E2e: the one speaker dict a channel passes to the shared Python code.
 * The filter_type keys are internal and never shown. Throws without a
 * role, so the shared default ("highpass") is never relied on.
 */
export function speakerDict(role) {
  if (role === ROLE.FULLRANGE) return { filter_type: "highpass" };
  if (role === ROLE.SUBWOOFER) return { filter_type: "lowpass" };
  throw new RangeError("no role: no Python call for this channel");
}

/** E2h: role tag in the download filename. */
export function roleFileTag(role) {
  if (role === ROLE.FULLRANGE) return "fullrange";
  if (role === ROLE.SUBWOOFER) return "sub";
  throw new RangeError("no role");
}

/** E2d: level-check noise band per role (4th-order Butterworth edges). */
export function levelNoiseBand(role, limitHz) {
  if (role === ROLE.FULLRANGE) return { lowHz: 100, highHz: 10000 };
  if (role === ROLE.SUBWOOFER) return { lowHz: 2 * limitHz, highHz: 200 };
  throw new RangeError("no role: no sound on this channel");
}

/** E2d: the band as the level-check step shows it. */
export function levelNoiseBandLabel(role, limitHz) {
  const { lowHz, highHz } = levelNoiseBand(role, limitHz);
  const hz = (f) => (f >= 1000 ? f / 1000 + " kHz" : f + " Hz");
  const name = role === ROLE.SUBWOOFER ? "subwoofer" : "full-range";
  return "Test noise: " + (role === ROLE.SUBWOOFER
    ? lowHz + "\u2013" + hz(highHz)
    : hz(lowHz) + "\u2013" + hz(highHz)) + " (" + name + ")";
}

/**
 * AC3: no sound on a channel until this returns ok.
 *
 * decl = { role, limitHz, capabilityConfirmed, enclosure: "ported" | "closed",
 *          portTuningHz, portConfirmed }
 *
 * The role comes first (E2a): without it nothing else is checked and the
 * channel stays silent.
 */
export function checkDeclaration(decl) {
  if (!isRole(decl.role)) {
    return { ok: false, errors: ["Choose what is connected to this output."],
      portWarning: "" };
  }
  const errors = [];
  let portWarning = "";
  const range = ROLE_LIMITS[decl.role];
  const limit = decl.limitHz;
  if (typeof limit !== "number" || !Number.isInteger(limit) ||
      limit < range.minHz) {
    errors.push(limitRangeText(decl.role));
  } else if (limit > range.maxHz) {
    errors.push(decl.role === ROLE.SUBWOOFER ? SUB_LIMIT_REFUSAL
      : limitRangeText(decl.role));
  }
  if (decl.capabilityConfirmed !== true) {
    errors.push("Confirm that this speaker can safely play down to the limit.");
  }
  if (decl.enclosure !== "ported" && decl.enclosure !== "closed") {
    errors.push("Choose ported (bass reflex) or closed.");
  } else if (decl.enclosure === "ported") {
    const tuning = decl.portTuningHz;
    if (typeof tuning !== "number" || !Number.isFinite(tuning) || tuning <= 0) {
      errors.push("Enter the port tuning frequency.");
    } else if (limit < tuning) {
      portWarning =
        "The low limit is below the port tuning (" + tuning + " Hz). Below " +
        "its tuning a port stops holding the cone back, so the cone moves " +
        "much further and can be damaged.";
      if (decl.portConfirmed !== true) {
        errors.push("Confirm the low limit below the port tuning separately.");
      }
    }
  }
  return { ok: errors.length === 0, errors, portWarning };
}

// -- AC4g: sweep plan -------------------------------------------------------

export function sweepPlan(limitHz, seconds) {
  const s = Math.min(seconds, LIMITS.SWEEP_MAX_S);
  return {
    fStartHz: limitHz,
    fEndHz: LIMITS.SWEEP_F_MAX_HZ,
    hpfHz: LIMITS.HPF_RATIO * limitHz,
    seconds: s,
    captureSeconds: captureSeconds(s),
  };
}

// -- AC4b/4d/4i: level check -----------------------------------------------

export const STOP = Object.freeze({
  USER: "user",
  TIMEOUT: "timeout",
  CAP: "cap",
  MIC_SPL: "mic-spl",
  MIC_SPL_PEAK: "mic-spl-peak",
  MIC_CLIP: "mic-clip",
  SWEEP_RISE: "sweep-rise",
  HIDDEN: "hidden",
  DEVICE: "device",
  RATE: "rate",
  AUDIO_ERROR: "audio-error",
  HEARTBEAT: "heartbeat",       // the meter's heartbeat stopped (latch r2 A4)
});

const STOP_MESSAGES = Object.freeze({
  [STOP.USER]: "Stopped.",
  [STOP.TIMEOUT]: "Level check stopped after 30 s without input. Press " +
    "Start level check to continue.",
  [STOP.CAP]: "Stopped: level cap reached. Lower the amp or interface " +
    "gain, then restart.",
  // E4a texts.
  [STOP.MIC_SPL]: "Stopped: too loud at the microphone (over 90 dB SPL). " +
    "Lower the amp or interface output gain, then restart.",
  [STOP.MIC_SPL_PEAK]: "Stopped: a very loud peak at the microphone (over " +
    "105 dB SPL). Check that nothing touched the mic. Lower the amp or " +
    "interface output gain, then restart.",
  [STOP.SWEEP_RISE]: "Stopped: the sweep was more than 6 dB louder at the " +
    "microphone than the level check. Restart when ready.",
  [STOP.HIDDEN]: "Stopped: the page was hidden. Restart when ready.",
  // E5a: shown at the top of the setup step.
  [STOP.DEVICE]: "Stopped: the audio devices changed. Check that the right " +
    "output and microphone are selected. Then confirm the safety check, the " +
    "speaker settings and the microphone calibration again. Unfinished " +
    "measurements were discarded; finished filters can still be downloaded.",
  // E6 (UX a62af4b1): held causes name the step that releases the hold.
  [STOP.AUDIO_ERROR]: "Stopped: an audio error occurred. Go back to setup, " +
    "press Use these devices, then start the level check again.",
  [STOP.HEARTBEAT]: "Stopped for safety: the microphone level monitor " +
    "stopped responding, so the sound was stopped. This can happen when the " +
    "computer is busy. Go back to setup, press Use these devices, then start " +
    "the level check again.",
});

// E4a: the mic-clip text depends on whether a calibration file is loaded at
// the moment of the stop (its SPL mapping depends on the mic input gain).
const MIC_CLIP_CALIBRATED = "Stopped: the microphone input clipped. Lower " +
  "the amp or interface output gain, then restart. Leave the microphone " +
  "input gain as it is: the SPL calibration depends on it.";
const MIC_CLIP_UNCALIBRATED = "Stopped: the microphone input clipped. " +
  "Lower the amp or interface output gain, or the microphone input gain, " +
  "then restart.";

/**
 * The text for an auto-STOP. calibrated: a calibration file is in use at
 * the moment of the stop (E4a). rate: the device's new rate, for
 * STOP.RATE (E5a).
 */
export function stopMessage(cause, { calibrated = false, rate } = {}) {
  if (cause === STOP.MIC_CLIP) {
    return calibrated ? MIC_CLIP_CALIBRATED : MIC_CLIP_UNCALIBRATED;
  }
  if (cause === STOP.RATE) {
    return "Stopped: the audio device now runs at " + rate + " Hz. mugge " +
      "filters need 48 kHz. Set the device back to 48 kHz in your system's " +
      "audio settings, then reload this page.";
  }
  return STOP_MESSAGES[cause] || STOP_MESSAGES[STOP.AUDIO_ERROR];
}

/** Causes that hold Start until the devices are opened again (E6). */
export const DEVICE_HOLDS = Object.freeze([STOP.AUDIO_ERROR, STOP.HEARTBEAT]);

/** Causes that send the user back to the setup step (AC2b). */
export function stopReturnsToSetup(cause) {
  return cause === STOP.DEVICE || cause === STOP.RATE;
}

/**
 * Mic-side auto-STOP rules shared by the meter worklet, the level check and
 * the sweep (AC4d, E3a/b).
 *
 * reading = { peakDbfs, rmsDbfs }: the per-quantum true peak and the 100 ms
 * sliding RMS from the meter (meter-core.js), never a display value.
 * splOffsetDb maps mic dBFS to dB SPL; null without a calibration file, and
 * then neither SPL stop can act (AE A1).
 */
export function micStopCause(reading, splOffsetDb) {
  if (reading.peakDbfs >= LIMITS.MIC_CLIP_DBFS) return STOP.MIC_CLIP;
  if (splOffsetDb != null) {
    if (reading.rmsDbfs + splOffsetDb > LIMITS.MIC_MAX_SPL_DB) {
      return STOP.MIC_SPL;
    }
    if (reading.peakDbfs + splOffsetDb > LIMITS.MIC_MAX_PEAK_SPL_DB) {
      return STOP.MIC_SPL_PEAK;
    }
  }
  return null;
}

/**
 * Level-check state machine (AC4b, 4d, 4h, 4i).
 *
 * maxLevelDbfs is the highest noise level the "+" steps may reach, from the
 * noise's crest factor (crest.js levelCeilingDbfs); it must leave the output
 * peak below the AC4c cap. splOffsetDb is the calibration's dBFS-to-SPL
 * offset, or null without a calibration file. The mic target follows from
 * it: 75 dB SPL, or -40 dBFS RMS uncalibrated (AE A1). Both are constants.
 */
export class LevelCheck {
  constructor({ maxLevelDbfs, splOffsetDb = null }) {
    if (!(maxLevelDbfs < LIMITS.OUTPUT_PEAK_CAP_DBFS)) {
      throw new RangeError("maxLevelDbfs must stay below the output cap");
    }
    if (!(splOffsetDb === null || Number.isFinite(splOffsetDb))) {
      throw new RangeError("splOffsetDb must be a number or null");
    }
    this.maxLevelDbfs = maxLevelDbfs;
    this.splOffsetDb = splOffsetDb;
    this.running = false;
    this.levelDbfs = null;
    this.lastActionMs = 0;
    this.stopCause = null;
    this.targetReached = false;
  }

  get calibrated() {
    return this.splOffsetDb !== null;
  }

  /** The mic RMS (dBFS) that counts as "target reached". */
  get micTargetRmsDbfs() {
    return this.calibrated
      ? LIMITS.MIC_TARGET_SPL_DB - this.splOffsetDb
      : LIMITS.MIC_TARGET_DBFS;
  }

  /** Fresh start at -60 dBFS, never a resume (AC4i). */
  start(nowMs) {
    this.running = true;
    this.levelDbfs = LIMITS.START_DBFS;
    this.lastActionMs = nowMs;
    this.stopCause = null;
    this.targetReached = false;
    return { gainDbfs: this.levelDbfs, rampFromZero: true };
  }

  /** "+" is allowed only while running, below the ceiling and the target. */
  canStepUp() {
    return this.running && !this.targetReached &&
      this.levelDbfs + LIMITS.STEP_DB <= this.maxLevelDbfs;
  }

  /** One explicit click: +6 dB, and it counts as a user action (AC4i). */
  stepUp(nowMs) {
    if (!this.running) return null;
    this.lastActionMs = nowMs;
    if (!this.canStepUp()) return null;
    this.levelDbfs += LIMITS.STEP_DB;
    return { gainDbfs: this.levelDbfs, rampFromZero: false };
  }

  /**
   * Feed one meter reading. Returns a stop cause, or null.
   * reading = { rmsDbfs, peakDbfs } at the mic (see micStopCause), plus
   * outputClamped when the worklet's last-stage clamp was touched (AC5d).
   */
  update(nowMs, reading) {
    if (!this.running) return null;
    let cause = null;
    if (reading.outputClamped) {
      cause = STOP.CAP;
    } else {
      cause = micStopCause(reading, this.splOffsetDb);
    }
    if (cause === null && nowMs - this.lastActionMs >= LIMITS.IDLE_TIMEOUT_MS) {
      cause = STOP.TIMEOUT;
    }
    if (cause !== null) {
      this.stop(cause);
      return cause;
    }
    if (reading.rmsDbfs >= this.micTargetRmsDbfs) this.targetReached = true;
    return null;
  }

  /**
   * The 30 s timer without a meter reading (AC4d): the timeout must not
   * depend on the meter worklet still reporting. Returns a cause or null.
   */
  tick(nowMs) {
    if (!this.running) return null;
    if (nowMs - this.lastActionMs >= LIMITS.IDLE_TIMEOUT_MS) {
      this.stop(STOP.TIMEOUT);
      return STOP.TIMEOUT;
    }
    return null;
  }

  stop(cause) {
    if (this.running) {
      this.running = false;
      this.stopCause = cause;
    }
  }
}

/**
 * Sweep-time mic rule (AC4d): the mic level during the sweep may not rise
 * more than 6 dB above the confirmed level-check reading.
 */
export function sweepStopCause(levelCheckMicRmsDbfs, reading, splOffsetDb) {
  const mic = micStopCause(reading, splOffsetDb);
  if (mic !== null) return mic;
  if (reading.rmsDbfs > levelCheckMicRmsDbfs + LIMITS.SWEEP_MAX_RISE_DB) {
    return STOP.SWEEP_RISE;
  }
  return null;
}
