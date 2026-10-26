// Calibration file parsing (calibration.js, AE K1/K4, E5b D3).

import { assert, close, eq } from "./assert.js";
import {
  CAL_GAIN_NOTE, UNCAL_BANNER, UNCAL_RESULT, parseCalibration,
  parseSensFactor, unboundText, uncalibratedFieldText, uncalibratedReason,
} from "../../../static/js/calibration.js";

const UMIK = '"Sens Factor =-1.378dB, SERNO: 7161942"\n* Freq(Hz)  dB\n' +
  "20.000\t-0.13\n1000.000\t0.00\n";

export async function test_house_umik_maps_to_121_378() {
  const c = parseCalibration(UMIK);
  eq(c.ok, true);
  eq(c.sensFactorDb, -1.378);
  close(c.splOffsetDb, 121.378, 1e-12);
  // CRLF and a BOM parse the same.
  close(parseCalibration("\uFEFF" + UMIK.replace(/\n/g, "\r\n")).splOffsetDb,
    121.378, 1e-12);
}

export async function test_sens_factor_forms() {
  eq(parseSensFactor('"Sens Factor =2.5dB, SERNO: 123"\n20.0\t0.0\n'), 2.5);
  eq(parseSensFactor('"Sens Factor = +3dB"\n'), 3);
  eq(parseSensFactor("20.000\t-0.13\n1000.000\t0.00\n"), null, "no header");
  eq(parseSensFactor('* comment\n"Sens Factor =-1.0dB"\n'), -1, "after *");
  eq(parseSensFactor('20.0\t0.0\n"Sens Factor =-1.0dB"\n'), null,
    "past the headers");
  eq(parseSensFactor('"Sens Factor =abcdB"\n'), null, "not a number");
  eq(parseSensFactor(""), null);
}

/** K1 clamp: outside -6..+6 dB, or unparsable, is uncalibrated. */
export async function test_out_of_range_is_uncalibrated() {
  for (const v of ["6.001", "-6.001", "12"]) {
    const c = parseCalibration('"Sens Factor =' + v + 'dB"\n20.0\t0.0\n');
    eq(c.ok, false, v);
    eq(c.splOffsetDb, null, v);
  }
  for (const v of ["6", "-6", "0"]) {
    const c = parseCalibration('"Sens Factor =' + v + 'dB"\n20.0\t0.0\n');
    eq(c.ok, true, v);
    close(c.splOffsetDb, 120 - Number(v), 1e-12);
  }
  const none = parseCalibration("20.0\t0.0\n");
  eq(none.ok, false);
  eq(none.splOffsetDb, null);
}

export async function test_texts() {
  eq(CAL_GAIN_NOTE, "SPL readings assume the microphone's input gain is " +
    "unchanged since its calibration (for a UMIK-1: the default input " +
    "level). Don't change it during this session.");
  eq(unboundText("7161942.txt", "UMIK-1"), "Calibration not confirmed for " +
    "this microphone. A calibration file belongs to one microphone. Confirm " +
    "that 7161942.txt belongs to UMIK-1, or choose another file. Until then, " +
    "measuring runs uncalibrated.");
  assert(unboundText("a.txt", "").includes("belongs to the selected microphone"));
}

/** UX 436f962f (c), AE c5bd03c0: the uncalibrated texts, one reason each. */
export async function test_uncalibrated_texts() {
  eq(UNCAL_BANNER, "UNCALIBRATED — levels are shown in dBFS, not dB SPL. " +
    "The 90 dB and 105 dB SPL safety stops are off; only the clip stop and " +
    "the level cap apply. Keep the amp at a low setting.");
  eq(UNCAL_RESULT, "Measured uncalibrated: levels in dBFS; the microphone's " +
    "own frequency response is not compensated.");
  const file = (text) => ({ fileName: "x.txt", parsed: parseCalibration(text) });
  eq(uncalibratedReason(null, false), "No calibration file loaded.");
  eq(uncalibratedReason(file("20.0\t0.0\n"), false),
    'The calibration file has no "Sens Factor" line.');
  eq(uncalibratedReason(file('"Sens Factor =7.5dB"\n'), false),
    "The calibration file's Sens Factor (7.5 dB) is outside -6 to +6 dB, " +
    "so it is not used.");
  eq(uncalibratedReason(file(UMIK), true),
    "Calibration not confirmed for this microphone.");
  eq(uncalibratedReason(file(UMIK), false), "", "calibrated");
  eq(uncalibratedFieldText(null, false),
    "Uncalibrated: No calibration file loaded.");
  eq(uncalibratedFieldText(file(UMIK), false), "");
}
