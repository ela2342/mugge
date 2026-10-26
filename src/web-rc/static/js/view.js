// view.js -- what the page shows for a flow state (US-179 AC11).
//
// Pure: no DOM. app.js copies these texts and flags into the page; the
// tests check them without a browser page. Texts are from the story and
// the UX/AE files named at each one.

import { topStepDbfs } from "./crest.js";
import { MAX_CHANNELS } from "./crest-plan.js";
import {
  CAL_GAIN_NOTE, UNCAL_BANNER, UNCAL_RESULT, unboundText,
  uncalibratedFieldText, uncalibratedReason,
} from "./calibration.js";
import { FLOW, STEP } from "./flow.js";
import {
  LIMITS, ROLE, capabilityText, checkDeclaration, checkSampleRates,
  levelNoiseBandLabel,
} from "./safety.js";

export const TEXT = Object.freeze({
  HEADER: "Standalone — not connected to a mugge Pi",          // AC11
  DEEP_BASS_HINT: "Deep-bass correction needs a measurement mic " +  // AE N1
    "with a calibration file.",
  // 4a, UX 64c83e3e (AE release 17e5fef8). The output item is last.
  ACK_TITLE: "Before any sound plays",
  ACK_INTRO: "This page plays test signals through your amplifier. It can't " +
    "see your amplifier, volume settings or speakers, so check each point:",
  ACK_ITEMS: Object.freeze([
    "No headphones or in-ear monitors are connected to this output, and " +
      "nobody is wearing any.",
    "The output is not a Bluetooth device.",
    "The amplifier and every volume control after this computer are " +
      "turned down low.",
  ]),
  ACK_BUTTON: "I have checked all of this",
  // 4b, UX 64c83e3e.
  SAFETY_LIMIT: "Safety limit: the output never goes above " +
    LIMITS.OUTPUT_PEAK_CAP_DBFS + " dBFS peak.",
  PLUS: "+6 dB",
  TOP_STEP: "Highest step reached.",
  // AC11 end state, AC10 report text, AC8c label.
  READY: "Filters ready — download",
  PI_NOTE: "Filters for the mugge Pi (48 kHz). Loading onto the Pi is not " +
    "supported yet. Correction not applied or verified acoustically; " +
    "re-measure after loading them.",
  PREDICTED_SUFFIX: " — predicted, not measured, unverified until re-measured",
  // UX 436f962f (a), AE cf32c0a6 (a).
  MAY_BE_REJECTED: "The measurement may be rejected as too noisy.",
  // UX 82b5b616 W2.
  CAPTURE_1: "Capture 1 of 2: playing sweep…",
  CAPTURE_2: "Capture 2 of 2: playing sweep… Keep the microphone where it is.",
  COMPUTING: "Computing the filter… This can take up to a minute the first time.",
  PREPARING: "Preparing the sweep…",
  PRE_DEVICE_CHANGE: "measured before a device change",              // E5b D4
});

/**
 * The 4a output item (UX 64c83e3e): the device chosen with setSinkId, by
 * its label, or the browser's default output device.
 */
export function ackOutputText(sinkLabel) {
  return sinkLabel
    ? "Sound plays on \"" + sinkLabel + "\". It is connected to the " +
      "speaker I want to measure."
    : "Sound plays on this browser's default output device. I have " +
      "checked that it is connected to the speaker I want to measure.";
}

/** The 3c second confirmation, with the values it confirms (UX 64c83e3e). */
export function portConfirmText(limitHz, portTuningHz) {
  return "I understand the risk: measure down to " + limitHz + " Hz, below " +
    "the port tuning of " + portTuningHz + " Hz.";
}

/**
 * The mic level for the meter readout: dB SPL when calibrated, dBFS
 * otherwise, with the unit shown (UX 436f962f: never "dB SPL" uncalibrated).
 */
export function micLevelText(rmsDbfs, splOffsetDb) {
  if (!Number.isFinite(rmsDbfs)) return "—";
  return splOffsetDb === null
    ? rmsDbfs.toFixed(1) + " dBFS"
    : (rmsDbfs + splOffsetDb).toFixed(1) + " dB SPL";
}

/**
 * UX 436f962f (a) with the 82b5b616 W3 format: whole dB, rounded down so
 * the value shown can't equal the target.
 */
export function targetNotReachedText(rmsDbfs, splOffsetDb) {
  const cal = splOffsetDb !== null;
  const x = Math.floor(cal ? rmsDbfs + splOffsetDb : rmsDbfs);
  const unit = cal ? " dB SPL" : " dBFS";
  const target = cal ? LIMITS.MIC_TARGET_SPL_DB : LIMITS.MIC_TARGET_DBFS;
  return "Target level not reached: " + x + unit + " (target " + target +
    unit + "). " + TEXT.MAY_BE_REJECTED;
}

/** 4b "cap shown", first line (UX 64c83e3e); TEXT.SAFETY_LIMIT follows. */
export function capText(levelDbfs, topDbfs) {
  return levelDbfs === null ? "Test level: off"
    : "Test level: " + levelDbfs + " dBFS (highest step " + topDbfs + " dBFS)";
}

export function rateLines(audio) {
  if (!audio) return [];
  return [
    "Sample rate: " + audio.outputRate + " Hz (output)",
    "Sample rate: " + audio.inputRate + " Hz (input)",
  ];
}

/** AC8c, from the analysis result's prediction. */
export function predictionText(prediction) {
  if (!prediction) return "";
  return "Predicted residual within 3 dB: " +
    (prediction.passed ? "PASS" : "FAIL") + TEXT.PREDICTED_SUFFIX;
}

/** The measure step's progress line (W2). */
export function progressText(flow) {
  const p = flow.run.pending;
  if (!p) return "";
  if (p.kind === "sweep") return TEXT.PREPARING;
  if (p.kind === "record") {
    return flow.run.captures.length === 0 ? TEXT.CAPTURE_1 : TEXT.CAPTURE_2;
  }
  if (p.kind === "analyze") return TEXT.COMPUTING;
  return "";
}

/** The whole page state. extras: { sinkLabel, pipelineError }. */
export function viewModel(flow, extras = {}) {
  const audio = flow.audio;
  const decl = flow.decl;
  const unbound = flow.calibrationUnbound;
  const calibrated = flow.calibrated;
  const decision = checkDeclaration(decl);
  const nChannels = Math.min(MAX_CHANNELS, audio ? audio.outputChannels : 0);
  const rates = audio ? checkSampleRates(audio.outputRate, audio.inputRate)
    : { ok: false, message: "" };
  const run = flow.run;
  const lc = run.lc;
  const level = lc && lc.running ? lc.levelDbfs : null;
  const rms = run.micRmsDbfs;

  const vm = {
    step: flow.step,
    header: TEXT.HEADER,
    notice: flow.notice ? flow.notice.text : "",
    noticeDetail: flow.notice && flow.notice.detail ? flow.notice.detail : "",
    sounding: flow.sounding,
    stopVisible: flow.sounding,
    setup: {
      rateLines: rateLines(audio),
      rateRefusal: rates.ok ? "" : rates.message,
      channels: Array.from({ length: nChannels }, (_, i) => i),
      channel: flow.channel,
      role: decl.role,
      limitHz: decl.limitHz,
      capabilityText: decl.role && Number.isInteger(decl.limitHz)
        ? capabilityText(decl.role, decl.limitHz) : "",
      capabilityConfirmed: decl.capabilityConfirmed,
      enclosure: decl.enclosure,
      portTuningHz: decl.portTuningHz,
      portWarning: decision.portWarning,
      portConfirmed: decl.portConfirmed,
      portConfirmText: decision.portWarning
        ? portConfirmText(decl.limitHz, decl.portTuningHz) : "",
      calFile: flow.cal ? flow.cal.fileName : "",
      calUnbound: unbound ? unboundText(flow.cal.fileName,
        audio ? audio.micLabel : "") : "",
      calStatus: uncalibratedFieldText(flow.cal, unbound),
      calGainNote: calibrated ? CAL_GAIN_NOTE : "",
      deepBassHint: decl.role === ROLE.SUBWOOFER && !calibrated
        ? TEXT.DEEP_BASS_HINT : "",
      problems: flow.setupProblems(),
      canConfirm: flow.step === STEP.SETUP && flow.setupProblems().length === 0,
    },
    ack: {
      title: TEXT.ACK_TITLE,
      intro: TEXT.ACK_INTRO,
      items: [...TEXT.ACK_ITEMS, ackOutputText(extras.sinkLabel || "")],
      ticked: Array.from({ length: FLOW.ACK_ITEMS }, (_, i) => flow.ackTicks.has(i)),
      button: TEXT.ACK_BUTTON,
      canAcknowledge: flow.canAcknowledge,
    },
    level: {
      banner: calibrated ? "" : UNCAL_BANNER,
      bannerReason: calibrated ? "" : uncalibratedReason(flow.cal, unbound),
      bandLabel: decl.role && Number.isInteger(decl.limitHz)
        ? levelNoiseBandLabel(decl.role, decl.limitHz) : "",
      micLevel: micLevelText(rms, flow.splOffsetDb),
      cap: run.band ? capText(level, topStepDbfs(run.band)) : "",
      safetyLimit: run.band ? TEXT.SAFETY_LIMIT : "",
      plusLabel: lc && lc.running && !lc.canStepUp() ? TEXT.TOP_STEP : TEXT.PLUS,
      canStart: flow.canStart,
      canStepUp: flow.canStepUp(),
      canMeasure: flow.step === STEP.LEVEL && !!lc && lc.running && rms !== null,
      targetText: lc && lc.running && rms !== null && !lc.targetReached
        ? targetNotReachedText(rms, flow.splOffsetDb) : "",
    },
    measure: { progress: progressText(flow) },
    result: resultView(flow),
    pipelineError: extras.pipelineError || "",
  };
  return vm;
}

function resultView(flow) {
  const r = flow.run.result;
  return {
    ready: flow.filters.size > 0 ? TEXT.READY : "",
    uncalibrated: r && !r.calibrated ? UNCAL_RESULT : "",
    prediction: r ? predictionText(r.prediction) : "",
    piNote: TEXT.PI_NOTE,
    downloads: flow.downloads().map((d) => ({
      channel: d.channel,
      name: d.name,
      mark: d.preDeviceChange ? TEXT.PRE_DEVICE_CHANGE : "",
    })),
  };
}
