// The page's view model (view.js): texts and enabled states per flow state.

import { assert, eq } from "./assert.js";
import { FLOW, Flow, STEP } from "../../../static/js/flow.js";
import {
  CAL_GAIN_NOTE, UNCAL_BANNER, UNCAL_RESULT, parseCalibration,
} from "../../../static/js/calibration.js";
import { topStepDbfs } from "../../../static/js/crest.js";
import {
  LIMITS, ROLE, STOP, changeRole, levelNoiseBand, levelNoiseBandLabel,
  stopMessage,
} from "../../../static/js/safety.js";
import {
  REPORT_FILE, TEXT, ackOutputText, capText, channelLabel, micLevelText,
  portConfirmText, predictionText, reportChannels, repeatabilityCaption,
  resultPlots, targetNotReachedText, viewModel,
} from "../../../static/js/view.js";

const SR = 48000;

/** The curve fields of an analysis result (webrc_pipeline.analyze). */
function curves() {
  const freqs = Float64Array.from([20, 40, 80, 160]);
  return {
    measured: { freqs, db: Float64Array.from([-3, 0, 1, -2]) },
    ir: new Float64Array(64), irStartS: -0.1,
    repeatability: { ok: true, band_hz: [30, 200], max_abs_db: 0.4,
      limit_db: 1.0, freqs, diff_db: Float64Array.from([2, 0.4, -0.3, 0.1]) },
  };
}
const OFF = { echoCancellation: false, noiseSuppression: false,
  autoGainControl: false };
const AUDIO = { outputRate: SR, inputRate: SR, outputChannels: 2,
  dspSettings: OFF, micId: "mic-A", micLabel: "UMIK-1" };
const UMIK = parseCalibration('"Sens Factor =-1.378dB, SERNO: 7161942"\n' +
  "20.000\t-0.13\n");

function ready({ cal = false } = {}) {
  const f = new Flow();
  f.setAudio(AUDIO);
  f.setChannel(1);
  f.setDeclaration({ ...changeRole({ enclosure: "closed" }, ROLE.SUBWOOFER),
    limitHz: 40, capabilityConfirmed: true });
  if (cal) f.loadCalibration("7161942.txt", UMIK);
  return f;
}

/**
 * A capture as the page delivers it: the output onset, then the recording,
 * both counted on context clock 1.
 */
function rec(f, token, samples, onset = 0) {
  eq(f.output({ type: "started", frame: 4096 + onset, clock: 1 }).length, 0);
  return f.recorded(token, samples, 4096, 1, null);
}

/** Tick every 4a item, then acknowledge (UX 64c83e3e). */
function ackAll(f) {
  for (let i = 0; i < FLOW.ACK_ITEMS; i++) f.tickAck(i, true);
  return f.acknowledge();
}

export async function test_header_and_first_load() {
  const vm = viewModel(new Flow());
  eq(vm.header, "Standalone — not connected to a mugge Pi");
  eq(vm.step, STEP.SETUP);
  eq(vm.setup.problems.join(), "No audio device yet.");
  eq(vm.setup.canConfirm, false);
  eq(vm.setup.channels.length, 0);
  eq(vm.setup.calStatus, "Uncalibrated: No calibration file loaded.");
  eq(vm.stopVisible, false);
}

export async function test_setup_rates_and_refusal() {
  const f = new Flow();
  f.setAudio({ ...AUDIO, inputRate: 44100 });
  const vm = viewModel(f);
  eq(vm.setup.rateLines.join("|"),
    "Sample rate: 48000 Hz (output)|Sample rate: 44100 Hz (input)");
  assert(vm.setup.rateRefusal.startsWith("Can't measure: this audio device " +
    "runs at 44100 Hz."), vm.setup.rateRefusal);
  eq(vm.setup.channels.join(), "0,1");
}

export async function test_setup_calibration_states() {
  const f = ready();
  let vm = viewModel(f);
  eq(vm.setup.deepBassHint, "Deep-bass correction needs a measurement mic " +
    "with a calibration file.");
  eq(vm.setup.calGainNote, "");
  f.loadCalibration("7161942.txt", UMIK);
  vm = viewModel(f);
  eq(vm.setup.calStatus, "");
  eq(vm.setup.calGainNote, CAL_GAIN_NOTE);
  eq(vm.setup.deepBassHint, "");
  eq(vm.setup.calUnbound, "");
  // E5b D3: after a switch the file is loaded but not bound.
  f.deviceChange({ ...AUDIO, micId: "mic-B", micLabel: "" });
  vm = viewModel(f);
  assert(vm.setup.calUnbound.includes("Confirm that 7161942.txt belongs to " +
    "the selected microphone"), vm.setup.calUnbound);
  eq(vm.setup.calStatus, "Uncalibrated: Calibration not confirmed for this " +
    "microphone.");
  eq(vm.setup.calGainNote, "");
}

/** 4a, UX 64c83e3e verbatim (AE release 17e5fef8). */
export async function test_ack_texts_and_checkboxes() {
  const f = ready();
  f.confirmSetup();
  let vm = viewModel(f, { sinkLabel: "USBStreamer" });
  eq(vm.step, STEP.ACK);
  eq(vm.ack.title, "Before any sound plays");
  eq(vm.ack.intro, "This page plays test signals through your amplifier. " +
    "It can't see your amplifier, volume settings or speakers, so check " +
    "each point:");
  eq(vm.ack.items.join("\n"), [
    "No headphones or in-ear monitors are connected to this output, and " +
      "nobody is wearing any.",
    "The output is not a Bluetooth device.",
    "The amplifier and every volume control after this computer are " +
      "turned down low.",
    'Sound plays on "USBStreamer". It is connected to the speaker I want ' +
      "to measure.",
  ].join("\n"));
  eq(vm.ack.items.length, FLOW.ACK_ITEMS);
  const DEFAULT_OUT = "Sound plays on this browser's default output " +
    "device. I have checked that it is connected to the speaker I want to " +
    "measure.";
  eq(ackOutputText("", ""), DEFAULT_OUT);
  eq(ackOutputText("default", ""), DEFAULT_OUT, "the default device's id");
  // UX 10bc34bf: a chosen output whose label is unknown is not the default.
  const CHOSEN_OUT = "Sound plays on the output device selected in setup " +
    "(the browser does not show its name). I have checked that it is " +
    "connected to the speaker I want to measure.";
  eq(ackOutputText("4f1c9a", ""), CHOSEN_OUT);
  eq(viewModel(f, { sinkId: "4f1c9a", sinkLabel: "" }).ack.items[3], CHOSEN_OUT);
  eq(ackOutputText("4f1c9a", "USBStreamer"),
    'Sound plays on "USBStreamer". It is connected to the speaker I want ' +
    "to measure.");
  eq(vm.ack.button, "I have checked all of this");
  eq(vm.ack.ticked.join(), "false,false,false,false");
  eq(vm.ack.canAcknowledge, false);
  for (let i = 0; i < FLOW.ACK_ITEMS; i++) f.tickAck(i, true);
  vm = viewModel(f);
  eq(vm.ack.ticked.join(), "true,true,true,true");
  eq(vm.ack.canAcknowledge, true);
}

/** 3c, UX 64c83e3e: the label names the values it confirms. */
export async function test_port_confirm_names_the_values() {
  const f = ready();
  f.setDeclaration({ ...f.decl, enclosure: "ported", portTuningHz: 45 });
  const vm = viewModel(f);
  assert(vm.setup.portWarning, "40 Hz is below the 45 Hz port");
  eq(vm.setup.portConfirmText, "I understand the risk: measure down to 40 " +
    "Hz, below the port tuning of 45 Hz.");
  eq(portConfirmText(30, 35.5), "I understand the risk: measure down to 30 " +
    "Hz, below the port tuning of 35.5 Hz.");
  f.setDeclaration({ ...f.decl, enclosure: "closed" });
  eq(viewModel(f).setup.portConfirmText, "", "no port warning, no label");
}

export async function test_level_uncalibrated_banner_and_dbfs() {
  const f = ready();
  f.confirmSetup();
  ackAll(f);
  let vm = viewModel(f);
  eq(vm.level.banner, UNCAL_BANNER);
  eq(vm.level.bannerReason, "No calibration file loaded.");
  eq(vm.level.canStart, true);
  eq(vm.level.canMeasure, false);
  eq(vm.level.bandLabel, levelNoiseBandLabel(ROLE.SUBWOOFER, 40));
  f.startLevel(0);
  vm = viewModel(f);
  eq(vm.stopVisible, true);
  eq(vm.level.canStart, false, "one level check at a time");
  f.hidden();
  eq(viewModel(f).level.canStart, false, "held while hidden (latch r2 A3)");
  eq(viewModel(f).level.holdText, "", "a hidden page has no hold text (E6b)");
  f.visible();
  eq(viewModel(f).level.canStart, true);
  eq(viewModel(f).level.holdText, "");
  f.startLevel(0);
  vm = viewModel(f);
  eq(vm.level.canStepUp, true);
  eq(vm.level.canMeasure, false, "no reading yet");
  const top = topStepDbfs(levelNoiseBand(ROLE.SUBWOOFER, 40));
  eq(vm.level.cap, capText(-60, top));
  eq(vm.level.cap, "Test level: -60 dBFS (highest step " + top + " dBFS)");
  eq(vm.level.safetyLimit, "Safety limit: the output never goes above -20 " +
    "dBFS peak.");
  eq(capText(null, top), "Test level: off");
  eq(vm.level.plusLabel, "+6 dB");
  while (f.canStepUp()) f.stepUp(0);
  eq(viewModel(f).level.canStepUp, false);
  eq(viewModel(f).level.plusLabel, "Highest step reached.");
  eq(viewModel(f).level.cap, "Test level: " + top + " dBFS (highest step " +
    top + " dBFS)");
  f.userStop();
  eq(viewModel(f).level.plusLabel, "+6 dB", "not running");
  f.startLevel(0);
  vm = viewModel(f);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -47.2 });
  vm = viewModel(f);
  eq(vm.level.micLevel, "-47.2 dBFS");
  assert(!vm.level.micLevel.includes("SPL"), "never dB SPL uncalibrated");
  eq(vm.level.canMeasure, true, "UX 436f962f (a): Measure stays enabled");
  eq(vm.level.targetText, "Target level not reached: -48 dBFS (target " +
    "-40 dBFS). The measurement may be rejected as too noisy.");
  f.meter(0, { peakDbfs: -30, rmsDbfs: -39.5 });
  eq(viewModel(f).level.targetText, "", "target reached");
}

export async function test_level_calibrated_spl() {
  const f = ready({ cal: true });
  f.confirmSetup();
  ackAll(f);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -46.778 }); // 74.6 dB SPL
  const vm = viewModel(f);
  eq(vm.level.banner, "");
  eq(vm.level.micLevel, "74.6 dB SPL");
  eq(vm.level.targetText, "Target level not reached: 74 dB SPL (target " +
    "75 dB SPL). The measurement may be rejected as too noisy.");
}

export async function test_target_text_rounds_down() {
  eq(targetNotReachedText(-40.4, null).slice(0, 34),
    "Target level not reached: -41 dBFS");
  eq(micLevelText(NaN, null), "—");
  eq(micLevelText(-50, 120), "70.0 dB SPL");
}

export async function test_measure_progress_and_result() {
  const f = ready();
  f.confirmSetup();
  ackAll(f);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  const m = f.measure(0);
  eq(viewModel(f).measure.progress, TEXT.PREPARING);
  const sweep = new Float32Array(SR);
  for (let i = 0; i < SR; i++) sweep[i] = 0.5 * Math.sin(i / 10);
  eq(f.sweepReady(m[1].token, sweep).length, 0);
  eq(viewModel(f).measure.progress, TEXT.PREPARING, "the room settles");
  f.output({ type: "stopped", frame: 0, clamped: false, cause: null }, 0);
  for (let t = 0; t < 1000 * LIMITS.ROOM_DECAY_S; t += 250) {
    eq(f.tick(t).length, 0);
    eq(viewModel(f).measure.progress, TEXT.PREPARING, "settling at " + t);
  }
  const r = f.tick(1000 * LIMITS.ROOM_DECAY_S);
  eq(viewModel(f).measure.progress, TEXT.PREPARING, "the context resumes");
  const s = f.resumed(r[0].token);
  eq(viewModel(f).measure.progress, "Capture 1 of 2: playing sweep…");
  eq(viewModel(f).stopVisible, true, "STOP during the captures (4e)");
  const s2 = rec(f, s[0].token, new Float32Array(1));
  eq(viewModel(f).measure.progress, "Capture 2 of 2: playing sweep… Keep " +
    "the microphone where it is.");
  const a = rec(f, s2[0].token, new Float32Array(1));
  eq(viewModel(f).measure.progress, "Computing the filter… This can take up " +
    "to a minute the first time.");
  eq(viewModel(f).stopVisible, false, "no sound while computing");
  const c = curves();
  const pf = Float64Array.from([30, 60, 120]);
  f.analysisDone(a[1].token, { fileName: "sub.wav", wavBytes: new Uint8Array(1),
    channel: 1, role: ROLE.SUBWOOFER, delayS: 0.00425, calibrated: false,
    prediction: { passed: true, band_hz: [30, 200], freqs: pf,
      measured_db: Float64Array.from([4, 0, -4]),
      predicted_db: Float64Array.from([1, 0, -1]),
      target_db: Float64Array.from([0, 0, 0]) }, ...c });
  const vm = viewModel(f);
  eq(vm.step, STEP.RESULT);
  eq(vm.result.ready, "Filters ready — download");
  // E2h: the role next to the channel and base_seed; AC5a channel_index.
  eq(vm.result.channel, "Output 2: Subwoofer. Noise base_seed 174 " +
    "(channel_index 1).");
  eq(vm.result.delay, "Delay (audio latency + time of flight): 4.3 ms");
  eq(vm.result.uncalibrated, UNCAL_RESULT);
  eq(vm.result.prediction, "Predicted residual within 3 dB: PASS — " +
    "predicted, not measured, unverified until re-measured (checked over " +
    "30-200 Hz)");
  // AC11 plots: the analysis curves as plot.js takes them.
  const p = vm.result.plots;
  eq(p.measured.freqs, c.measured.freqs);
  eq(p.measured.db, c.measured.db);
  eq(p.measured.caption, TEXT.PLOT_MEASURED);
  eq(p.impulse.ir, c.ir);
  eq(p.impulse.startS, -0.1);
  eq(p.impulse.sampleRate, SR);
  eq(p.repeatability.freqs, c.repeatability.freqs);
  eq(p.repeatability.diffDb, c.repeatability.diff_db);
  eq(p.repeatability.band, c.repeatability.band_hz);
  eq(p.repeatability.limitDb, 1.0);
  eq(p.repeatability.caption, "Repeatability: capture 1 minus capture 2. " +
    "Green: within ±1.0 dB; red: over 1.0 dB (dashed lines: the limit); " +
    "grey: outside the checked band (30-200 Hz).");
  eq(p.impulse.caption, "Impulse response (0 ms = when the sweep was sent " +
    "to the audio output; the peak is at the delay above)");
  eq(p.noPrediction, "", "a curve: no placeholder line");
  eq(p.prediction.freqs, pf);
  eq(p.prediction.measuredDb[0], 4);
  eq(p.prediction.predictedDb[0], 1);
  eq(p.prediction.targetDb[0], 0);
  eq(JSON.stringify(p.prediction.legend), JSON.stringify(
    { target: "Target", measured: "Measured", predicted: "Predicted" }),
    "AC8c: the before curve is the measured one");
  eq(vm.result.downloads.length, 1);
  eq(vm.result.downloads[0].mark, "");
  eq(vm.level.canStart, true, "measure again from the result");
  eq(predictionText({ passed: false }).slice(0, 35),
    "Predicted residual within 3 dB: FAI");
}

/** AC11: no prediction plot without a predicted curve; no plots, no result. */
export async function test_result_plots_without_a_curve() {
  eq(resultPlots(null), null);
  const r = { ...curves(), prediction: { passed: false, freqs: new Float64Array(0) } };
  eq(resultPlots(r).prediction, null);
  eq(resultPlots({ ...r, prediction: null }).prediction, null);
  // UX 866c44ff: a line in its place, not a gap.
  eq(resultPlots(r).noPrediction, "No prediction plot for this channel.");
  eq(resultPlots({ ...r, prediction: null }).noPrediction,
    TEXT.PLOT_NO_PREDICTION);
  assert(resultPlots(r).measured, "the other plots stay");
}

/** Architect Q4: the result step names no phase and no coherence. */
export async function test_result_plots_name_no_phase() {
  const texts = [TEXT.PLOT_MEASURED, TEXT.PLOT_IMPULSE, TEXT.PLOT_PREDICTION,
    TEXT.PLOT_NO_PREDICTION,
    TEXT.LEGEND_TARGET, TEXT.LEGEND_MEASURED, TEXT.LEGEND_PREDICTED,
    repeatabilityCaption(curves().repeatability)];
  for (const t of texts) {
    assert(!/phase|coheren/i.test(t), t);
  }
}

/** AC10/E2h: one report entry per filter, as the downloads name them. */
export async function test_report_channels() {
  const f = new Flow();
  const pred = (passed, band) => ({ passed, band_hz: band });
  f.filters.set(0, { fileName: "combined_ch1-fullrange-browser-generated.wav",
    role: ROLE.FULLRANGE, enclosure: "ported", limitHz: 80, delayS: 0.01,
    calibrated: true, prediction: pred(false, [250, 500]),
    preDeviceChange: false });
  f.filters.set(2, { fileName: "combined_ch3-sub-browser-generated.wav",
    role: ROLE.SUBWOOFER, enclosure: "closed", limitHz: 20, delayS: 0.02,
    calibrated: false, prediction: pred(true, [30, 200]),
    preDeviceChange: true });
  const r = reportChannels(f);
  eq(JSON.stringify(r[0]), JSON.stringify({
    name: "Output 1", channel_index: 0, role: "fullrange", limit_hz: 80,
    enclosure: "ported", delay_s: 0.01,
    filename: "combined_ch1-fullrange-browser-generated.wav",
    prediction_label: "Predicted residual within 3 dB: FAIL — predicted, " +
      "not measured, unverified until re-measured",
    band_hz: [250, 500], calibrated: true,
  }));
  eq(r[1].name, "Output 3");
  eq(r[1].channel_index, 2);
  eq(r[1].role, "subwoofer");
  eq(r[1].filename, "combined_ch3-sub-browser-generated-measured-before-" +
    "device-change.wav", "the name the download uses");
  eq(r[1].calibrated, false);
  eq(r[1].band_hz.join(), "30,200");
  eq(channelLabel(7), "Output 8");
  assert(REPORT_FILE.includes("browser-generated"), "AC10 mark");
  eq(JSON.stringify(reportChannels(new Flow())), "[]");
}

export async function test_notice_detail_after_capture_2_stop() {
  const f = ready();
  f.confirmSetup();
  ackAll(f);
  f.startLevel(0);
  f.meter(0, { peakDbfs: -40, rmsDbfs: -50 });
  const m = f.measure(0);
  const sweep = new Float32Array(SR).fill(0.1);
  f.sweepReady(m[1].token, sweep);
  f.output({ type: "stopped", frame: 0, clamped: false, cause: null }, 0);
  const s = f.resumed(f.tick(1000 * LIMITS.ROOM_DECAY_S)[0].token);
  rec(f, s[0].token, new Float32Array(1));
  f.userStop();
  const vm = viewModel(f);
  eq(vm.notice, "Stopped.");
  assert(vm.noticeDetail.startsWith("Both captures were discarded"));
}

/** E6b: a device hold that came while idle shows next to the disabled Start. */
export async function test_hold_text_next_to_disabled_start() {
  const f = ready();
  f.confirmSetup();
  ackAll(f);
  for (const cause of [STOP.HEARTBEAT, STOP.AUDIO_ERROR]) {
    if (cause === STOP.HEARTBEAT) f.output({ type: "stopped", cause: "heartbeat" });
    else f.audioError();
    const vm = viewModel(f);
    eq(vm.notice, "", "nothing was sounding: no stop box");
    eq(vm.level.canStart, false);
    eq(vm.level.holdText, stopMessage(cause), cause);
    f.setAudio(f.audio);
    eq(viewModel(f).level.holdText, "", "released: " + cause);
    eq(viewModel(f).level.canStart, true);
  }
}
