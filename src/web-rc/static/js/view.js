// view.js -- what the page shows for a flow state (US-179 AC11).
//
// Pure: no DOM. app.js copies these texts and flags into the page; the
// tests check them without a browser page. Texts are from the story and
// the UX/AE files named at each one.

import { topStepDbfs } from "./crest.js";
import { BASE_SEED, MAX_CHANNELS } from "./crest-plan.js";
import {
  CAL_GAIN_NOTE, UNCAL_BANNER, UNCAL_RESULT, unboundText,
  uncalibratedFieldText, uncalibratedReason,
} from "./calibration.js";
import { FLOW, STEP, markedName } from "./flow.js";
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
  // AC11 result plots. No phase and no "coherence" (Architect Q4).
  PLOT_MEASURED: "Measured response, 1/6-octave smoothed (0 dB = the " +
    "correction's reference level)",
  PLOT_IMPULSE: "Impulse response (0 ms = when the sweep was sent to the " +
    "audio output; the peak is at the delay above)",
  PLOT_PREDICTION: "Predicted response after correction — predicted, not " +
    "measured",
  PLOT_NO_PREDICTION: "No prediction plot for this channel.",
  LEGEND_TARGET: "Target",
  LEGEND_MEASURED: "Measured",
  LEGEND_PREDICTED: "Predicted",
});

/** The role as the setup radios name it (E2a), for the result and report. */
export const ROLE_LABEL = Object.freeze({
  [ROLE.FULLRANGE]: "Full-range speaker",
  [ROLE.SUBWOOFER]: "Subwoofer",
});

/** The report file next to the WAVs (AC10: marked browser-generated). */
export const REPORT_FILE = "room-correction-report-browser-generated.txt";

/** An output channel as the setup list labels it (1-based, UX 1683b0fb). */
export function channelLabel(channel) {
  return "Output " + (channel + 1);
}

/**
 * The 4a output item (UX 64c83e3e, 10bc34bf): the text follows the sinkId
 * in use. The device chosen with setSinkId by its label; a chosen device
 * whose label the browser hides; else the browser's default output device.
 */
export function ackOutputText(sinkId, sinkLabel) {
  if (sinkLabel) {
    return "Sound plays on \"" + sinkLabel + "\". It is connected to the " +
      "speaker I want to measure.";
  }
  if (sinkId && sinkId !== "default") {
    return "Sound plays on the output device selected in setup (the " +
      "browser does not show its name). I have checked that it is " +
      "connected to the speaker I want to measure.";
  }
  return "Sound plays on this browser's default output device. I have " +
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

/** AC8c label, from the analysis result's prediction. */
export function predictionLabel(prediction) {
  if (!prediction) return "";
  return "Predicted residual within 3 dB: " +
    (prediction.passed ? "PASS" : "FAIL") + TEXT.PREDICTED_SUFFIX;
}

/** The result step's AC8c line: the label and its band (E2h). */
export function predictionText(prediction) {
  const band = prediction && prediction.band_hz;
  return predictionLabel(prediction) +
    (band ? " (checked over " + band[0] + "-" + band[1] + " Hz)" : "");
}

/** E2h: the role next to the channel and base_seed (AC5a). */
export function channelLine(channel, role) {
  return channelLabel(channel) + ": " + ROLE_LABEL[role] + ". Noise " +
    "base_seed " + BASE_SEED + " (channel_index " + channel + ").";
}

/** The delay as the report states it. */
export function delayText(delayS) {
  return "Delay (audio latency + time of flight): " +
    (1000 * delayS).toFixed(1) + " ms";
}

/**
 * AC10 report entries, one per filter, for webrc_pipeline.report_text.
 * The filename is the one the download uses (E5b D4 mark included).
 */
export function reportChannels(flow) {
  return [...flow.filters.entries()].map(([channel, f]) => ({
    name: channelLabel(channel),
    channel_index: channel,
    role: f.role,
    limit_hz: f.limitHz,
    enclosure: f.enclosure,
    delay_s: f.delayS,
    filename: f.preDeviceChange ? markedName(f.fileName) : f.fileName,
    prediction_label: predictionLabel(f.prediction),
    band_hz: f.prediction ? f.prediction.band_hz : null,
    calibrated: !!f.calibrated,
  }));
}

/** The AC8a trace's caption: what the colours mean, and its band. */
export function repeatabilityCaption(rep) {
  const limit = rep.limit_db.toFixed(1);
  return "Repeatability: capture 1 minus capture 2. Green: within ±" +
    limit + " dB; red: over " + limit + " dB (dashed lines: the limit); " +
    "grey: outside the checked band (" + rep.band_hz[0] + "-" +
    rep.band_hz[1] + " Hz).";
}

/**
 * The result step's plots (AC11): what plot.js draws, with captions.
 * prediction is null when the analysis has no predicted curve;
 * noPrediction is then the line shown in its place.
 */
export function resultPlots(r) {
  if (!r) return null;
  const rep = r.repeatability, p = r.prediction;
  const curve = !!(p && p.freqs && p.freqs.length > 1);
  return {
    measured: { caption: TEXT.PLOT_MEASURED, freqs: r.measured.freqs,
      db: r.measured.db },
    impulse: { caption: TEXT.PLOT_IMPULSE, ir: r.ir, startS: r.irStartS,
      sampleRate: LIMITS.REQUIRED_RATE },
    repeatability: { caption: repeatabilityCaption(rep), freqs: rep.freqs,
      diffDb: rep.diff_db, band: rep.band_hz, limitDb: rep.limit_db },
    prediction: curve ? {
      caption: TEXT.PLOT_PREDICTION, freqs: p.freqs,
      measuredDb: p.measured_db, predictedDb: p.predicted_db,
      targetDb: p.target_db,
      legend: { target: TEXT.LEGEND_TARGET, measured: TEXT.LEGEND_MEASURED,
        predicted: TEXT.LEGEND_PREDICTED },
    } : null,
    noPrediction: curve ? "" : TEXT.PLOT_NO_PREDICTION,
  };
}

/** The measure step's progress line (W2). */
export function progressText(flow) {
  const p = flow.run.pending;
  if (!p) return "";
  // UX: the wait for the room (settle, resume) shows PREPARING too.
  if (p.kind === "sweep" || p.kind === "settle" || p.kind === "resume") {
    return TEXT.PREPARING;
  }
  if (p.kind === "record") {
    return flow.run.captures.length === 0 ? TEXT.CAPTURE_1 : TEXT.CAPTURE_2;
  }
  if (p.kind === "analyze") return TEXT.COMPUTING;
  return "";
}

/** The whole page state. extras: { sinkId, sinkLabel, pipelineError }. */
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
      items: [...TEXT.ACK_ITEMS, ackOutputText(extras.sinkId || "", extras.sinkLabel || "")],
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
      holdText: flow.canStart ? "" : flow.holdText,
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
    channel: r ? channelLine(r.channel, r.role) : "",
    delay: r ? delayText(r.delayS) : "",
    uncalibrated: r && !r.calibrated ? UNCAL_RESULT : "",
    prediction: r ? predictionText(r.prediction) : "",
    plots: resultPlots(r),
    piNote: TEXT.PI_NOTE,
    downloads: flow.downloads().map((d) => ({
      channel: d.channel,
      name: d.name,
      mark: d.preDeviceChange ? TEXT.PRE_DEVICE_CHANGE : "",
    })),
  };
}
