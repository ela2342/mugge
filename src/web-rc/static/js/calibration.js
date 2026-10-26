// calibration.js -- mic calibration file -> dBFS-to-SPL offset (US-179
// AC4b, AE K1/K2/K4 1318b25c, E5b D3 df065993).
//
// SPL_dB = dBFS + 120.0 - SensFactor_dB (AE K1), for the RMS and the true
// peak alike. SensFactor comes from the "Sens Factor =X.XXXdB" header line,
// parsed as web-ui test_tool/routes.py _parse_umik1_sensitivity does. The
// frequency-response lines are not used by the meter (K2). Anything that
// does not give a usable SensFactor leaves the session uncalibrated (AE A1
// rules), which is the safe default.

export const CAL = Object.freeze({
  FULL_SCALE_SPL_DB: 120.0,
  SENS_MIN_DB: -6,
  SENS_MAX_DB: 6,
});

/** AE K4: shown while a calibration is in use. */
export const CAL_GAIN_NOTE = "SPL readings assume the microphone's input " +
  "gain is unchanged since its calibration (for a UMIK-1: the default input " +
  "level). Don't change it during this session.";

const SENS_RE = /Sens Factor\s*=\s*([+-]?\d+\.?\d*)\s*dB/;

/** The header's SensFactor in dB, or null (same rules as routes.py). */
export function parseSensFactor(text) {
  const lines = String(text).replace(/^\uFEFF/, "").split("\n");
  for (const raw of lines) {
    const line = raw.trim();
    if (line.startsWith('"') && line.includes("Sens Factor")) {
      const m = SENS_RE.exec(line);
      if (m) return Number(m[1]);
    }
    if (!line.startsWith('"') && !line.startsWith("*")) break;
  }
  return null;
}

/**
 * { ok, sensFactorDb, splOffsetDb, reason }. ok is false without a
 * parsable SensFactor or with one outside -6..+6 dB (K1 clamp); the file
 * then counts as uncalibrated.
 */
export function parseCalibration(text) {
  const sens = parseSensFactor(text);
  if (sens === null || !Number.isFinite(sens)) {
    return { ok: false, sensFactorDb: null, splOffsetDb: null,
      reason: "no Sens Factor in the file header" };
  }
  if (sens < CAL.SENS_MIN_DB || sens > CAL.SENS_MAX_DB) {
    return { ok: false, sensFactorDb: sens, splOffsetDb: null,
      reason: "Sens Factor " + sens + " dB is outside -6..+6 dB" };
  }
  return { ok: true, sensFactorDb: sens,
    splOffsetDb: CAL.FULL_SCALE_SPL_DB - sens, reason: "" };
}

/** E5b D3: the amber state while a file is not bound to the selected mic. */
export function unboundText(fileName, micLabel) {
  const mic = micLabel ? micLabel : "the selected microphone";
  return "Calibration not confirmed for this microphone. A calibration " +
    "file belongs to one microphone. Confirm that " + fileName +
    " belongs to " + mic + ", or choose another file. Until then, " +
    "measuring runs uncalibrated.";
}

// UX 436f962f (c): the uncalibrated warning. The banner's safety sentence
// is pending the AE's check (worker-6 AE file P3).
export const UNCAL_BANNER = "UNCALIBRATED — levels are shown in dBFS, not " +
  "dB SPL. The 90 dB and 105 dB SPL safety stops are off; only the clip " +
  "stop and the level cap apply. Keep the amp at a low setting.";

export const UNCAL_RESULT = "Measured uncalibrated: levels in dBFS; the " +
  "microphone's own frequency response is not compensated.";

/**
 * The one reason line under the banner, or "" when calibrated.
 * cal: { fileName, parsed } or null; unbound: E5b D3 (file not confirmed
 * for the selected mic).
 */
export function uncalibratedReason(cal, unbound) {
  if (!cal) return "No calibration file loaded.";
  if (!cal.parsed.ok) {
    if (cal.parsed.sensFactorDb === null) {
      return "The calibration file has no \"Sens Factor\" line.";
    }
    return "The calibration file's Sens Factor (" + cal.parsed.sensFactorDb +
      " dB) is outside -6 to +6 dB, so it is not used.";
  }
  if (unbound) return "Calibration not confirmed for this microphone.";
  return "";
}

/** The short form at the calibration field in setup. */
export function uncalibratedFieldText(cal, unbound) {
  const reason = uncalibratedReason(cal, unbound);
  return reason ? "Uncalibrated: " + reason.replace(/\.$/, "") + "." : "";
}
