// safety.js -- level-safety rules for the standalone room correction (US-179).
//
// Pure logic: no Web Audio, no DOM, no timers. The caller passes the time
// (ms) and the meter readings in; the functions return decisions. The audio
// code only ever applies what this module returns, so every rule here is
// unit-testable without sound.
//
// AC references are to US-179 r8 (978c3e1b) with errata E1 v2 (6a78af9f)
// and E2 (bca0d86b).

/** Code constants. No UI can change them (AC4c). */
export const LIMITS = Object.freeze({
  REQUIRED_RATE: 48000,          // AC2a
  LIMIT_MIN_HZ: 20,              // AC3a, never below 20 Hz for any role
  START_DBFS: -60,               // AC4b, level-check start
  STEP_DB: 6,                    // AC4b, one "+" click
  OUTPUT_PEAK_CAP_DBFS: -20,     // AC4c, hard cap on the actual output
  MIC_TARGET_SPL_DB: 75,         // AC4b, calibrated mic
  MIC_TARGET_DBFS: -40,          // AC4b, uncalibrated mic, RMS (AE A1)
  MIC_MAX_SPL_DB: 90,            // AC4d, calibrated mic
  MIC_CLIP_DBFS: -1,             // AC4d, mic clip (peak >= this)
  SWEEP_MAX_RISE_DB: 6,          // AC4d, sweep vs level check at the mic
  IDLE_TIMEOUT_MS: 30000,        // AC4d, level check without user action
  RAMP_MS: 10,                   // AC4e/4h
  HPF_RATIO: 0.8,                // AC4g/6b, subsonic corner = 0.8 x limit
  SWEEP_F_MAX_HZ: 20000,         // AC4g
  SWEEP_MAX_S: 10,               // AC4g
  CAPTURE_TAIL_S: 1,             // AC2d, capture >= sweep + 1 s
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
  return sweepSeconds + LIMITS.CAPTURE_TAIL_S;
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
    errors.push("Low limit must be a whole number of Hz between " +
      range.minHz + " and " + range.maxHz + " Hz.");
  } else if (limit > range.maxHz) {
    errors.push(decl.role === ROLE.SUBWOOFER ? SUB_LIMIT_REFUSAL
      : "Low limit must be a whole number of Hz between " + range.minHz +
        " and " + range.maxHz + " Hz.");
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
  MIC_CLIP: "mic-clip",
  SWEEP_RISE: "sweep-rise",
  HIDDEN: "hidden",
  DEVICE: "device",
  RATE: "rate",
  AUDIO_ERROR: "audio-error",
});

const STOP_MESSAGES = Object.freeze({
  [STOP.USER]: "Stopped.",
  [STOP.TIMEOUT]: "Level check stopped after 30 s without input. Press " +
    "Start level check to continue.",
  [STOP.CAP]: "Stopped: level cap reached. Lower the amp or interface " +
    "gain, then restart.",
  [STOP.MIC_SPL]: "Stopped: more than 90 dB SPL at the mic. Lower the amp " +
    "or interface gain, then restart.",
  [STOP.MIC_CLIP]: "Stopped: the mic input clipped. Lower the mic gain or " +
    "the amp, then restart.",
  [STOP.SWEEP_RISE]: "Stopped: the sweep was more than 6 dB louder at the " +
    "mic than the level check. Lower the amp, then restart.",
  [STOP.HIDDEN]: "Stopped: the page was hidden. Restart when you are back.",
  [STOP.DEVICE]: "Stopped: an audio device changed. Check the setup again.",
  [STOP.RATE]: "Stopped: the sample rate changed. Check the setup again.",
  [STOP.AUDIO_ERROR]: "Stopped: audio error.",
});

export function stopMessage(cause) {
  return STOP_MESSAGES[cause] || STOP_MESSAGES[STOP.AUDIO_ERROR];
}

/** Causes that send the user back to the setup step (AC2b). */
export function stopReturnsToSetup(cause) {
  return cause === STOP.DEVICE || cause === STOP.RATE;
}

/**
 * Mic-side auto-STOP rules shared by the level check and the sweep (AC4d).
 * reading = { peakDbfs, splDb } (splDb null when uncalibrated).
 */
export function micStopCause(reading) {
  if (reading.peakDbfs >= LIMITS.MIC_CLIP_DBFS) return STOP.MIC_CLIP;
  if (reading.splDb != null && reading.splDb > LIMITS.MIC_MAX_SPL_DB) {
    return STOP.MIC_SPL;
  }
  return null;
}

/**
 * Level-check state machine (AC4b, 4d, 4h, 4i).
 *
 * maxLevelDbfs is the highest noise level the "+" steps may reach, derived
 * from the noise's crest factor (AC5d); it must leave the output peak below
 * the AC4c cap. micTarget is { splDb } (calibrated) or { dbfs } (not).
 */
export class LevelCheck {
  constructor({ maxLevelDbfs, micTarget }) {
    if (!(maxLevelDbfs < LIMITS.OUTPUT_PEAK_CAP_DBFS)) {
      throw new RangeError("maxLevelDbfs must stay below the output cap");
    }
    this.maxLevelDbfs = maxLevelDbfs;
    this.micTarget = micTarget;
    this.running = false;
    this.levelDbfs = null;
    this.lastActionMs = 0;
    this.stopCause = null;
    this.targetReached = false;
  }

  get calibrated() {
    return this.micTarget.splDb != null;
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
   * reading = { rmsDbfs, peakDbfs, splDb } at the mic, plus outputClamped
   * when the worklet's last-stage clamp was touched (AC5d).
   */
  update(nowMs, reading) {
    if (!this.running) return null;
    let cause = null;
    if (reading.outputClamped) {
      cause = STOP.CAP;
    } else {
      cause = micStopCause(reading);
    }
    if (cause === null && nowMs - this.lastActionMs >= LIMITS.IDLE_TIMEOUT_MS) {
      cause = STOP.TIMEOUT;
    }
    if (cause !== null) {
      this.stop(cause);
      return cause;
    }
    if (this.calibrated) {
      if (reading.splDb != null && reading.splDb >= this.micTarget.splDb) {
        this.targetReached = true;
      }
    } else if (reading.rmsDbfs >= this.micTarget.dbfs) {
      this.targetReached = true;
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
export function sweepStopCause(levelCheckMicRmsDbfs, reading) {
  const mic = micStopCause(reading);
  if (mic !== null) return mic;
  if (reading.rmsDbfs > levelCheckMicRmsDbfs + LIMITS.SWEEP_MAX_RISE_DB) {
    return STOP.SWEEP_RISE;
  }
  return null;
}
