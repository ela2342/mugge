// flow.js -- the standalone room-correction flow controller (US-179 AC11).
//
// setup -> safety acknowledgement -> level check -> measure (2 captures)
// -> result -> download. One channel at a time (MVP).
//
// Pure: no Web Audio, no DOM, no timers, no Pyodide. Every method takes an
// event (with the time where a rule needs it) and returns the commands the
// page must carry out, in order:
//
//   { type: "noise-start", channel, source, gain }   level-check noise
//   { type: "gain", gain }                           a "+" step (ramped)
//   { type: "output-stop" }                          4e ramp, then suspend
//   { type: "meter-calibration", splOffsetDb }
//   { type: "make-sweep", token, plan }              -> sweepReady()
//   { type: "record", token, frames }                -> recorded()
//   { type: "sweep-start", channel, samples, gain }
//   { type: "record-cancel" }
//   { type: "analyze", token, request }              -> analysisDone/Failed()
//
// Replies carry the token of their command. A reply whose token is not the
// one the flow waits for is dropped: after a stop or a device change, late
// captures and analyses can't be used (E4, E5b D4).
//
// AC references are to US-179 r8 (978c3e1b) with errata E1 v2, E2, E3,
// E4 r2 (f692681c) and E5 (df065993); AE K1-K5 (1318b25c).

import { bandCeilingDbfs, crestEntry, topStepDbfs, unitGain } from "./crest.js";
import { crestSeed, MAX_CHANNELS } from "./crest-plan.js";
import { CAP_LINEAR } from "./output-core.js";
import { LATCH } from "./stop-latch.js";
import {
  LIMITS, LevelCheck, STOP, captureSeconds, checkDeclaration, checkDspFlags,
  checkSampleRates, dbToLinear, emptyDeclaration, levelNoiseBand,
  DEVICE_HOLDS, stopMessage, sweepPlan, sweepStopCause,
} from "./safety.js";

export const STEP = Object.freeze({
  SETUP: "setup",
  ACK: "ack",
  LEVEL: "level",
  MEASURE: "measure",
  RESULT: "result",
});

export const FLOW = Object.freeze({
  PRE_ROLL_S: 0.5,              // AC7 silent pre-capture before the sweep
  SWEEP_S: LIMITS.SWEEP_MAX_S,  // AC4g, at most 10 s per capture
  CAPTURES: 2,                  // AC8a, capture 1 = filter, 2 = hold-out
  ACK_ITEMS: 4,                 // 4a checkboxes (UX 64c83e3e), output last
});

/** The stop texts the flow adds to safety.js's. */
export const FLOW_TEXT = Object.freeze({
  NO_LEVEL_TABLE: "Can't play test noise for this setting.",
  SWEEP_OVER_CAP: "Can't measure: the sweep would exceed the output cap.",
  // UX 82b5b616 W1, AE cf32c0a6 (b): a stop during capture 2.
  BOTH_DISCARDED: "Both captures were discarded: the two captures must be " +
    "taken back to back. Press Start level check to measure again.",
});

/** E5b D4: download name of a filter measured before a device change. */
export function markedName(name) {
  const tag = "-measured-before-device-change";
  return name.endsWith(".wav") ? name.slice(0, -4) + tag + ".wav" : name + tag;
}

function rms(samples) {
  let acc = 0;
  for (let i = 0; i < samples.length; i++) acc += samples[i] * samples[i];
  return Math.sqrt(acc / samples.length);
}

function peak(samples) {
  let p = 0;
  for (let i = 0; i < samples.length; i++) p = Math.max(p, Math.abs(samples[i]));
  return p;
}

export class Flow {
  constructor() {
    this.step = STEP.SETUP;
    this.notice = null;          // { cause, text } for the current step
    this.audio = null;           // setAudio() fields
    this.channel = null;
    this.decl = emptyDeclaration();
    this.ack = false;
    this.ackTicks = new Set();   // ticked 4a items, 0 .. ACK_ITEMS - 1
    this.cal = null;             // { fileName, parsed } (calibration.js)
    this.calBoundMicId = null;
    this.filters = new Map();    // channel -> finished, AC6c-passed result
    this.held = new Set();       // main-thread stop causes still held (r2 A3)
    this._resetRun();
    this._token = 0;
  }

  // -- state queries ------------------------------------------------------

  /** dBFS-to-SPL offset in force, or null: uncalibrated (AE A1, E5b D3). */
  get splOffsetDb() {
    const c = this.cal;
    if (!c || !c.parsed.ok || !this.audio) return null;
    if (this.calBoundMicId === null || this.calBoundMicId !== this.audio.micId) {
      return null;
    }
    return c.parsed.splOffsetDb;
  }

  get calibrated() {
    return this.splOffsetDb !== null;
  }

  /** E5b D3: a loaded file that is not bound to the selected mic. */
  get calibrationUnbound() {
    return this.cal !== null && this.cal.parsed.ok && !this.calibrated;
  }

  get sounding() {
    return this.run.sounding;
  }

  /**
   * Can a level check start? Not while a main-thread stop cause is held
   * (latch r2 A3): the page hidden, or an audio error or heartbeat stop
   * until the devices are opened again (E6). A device change is held by
   * the reset 4a ack.
   */
  get canStart() {
    return !this.run.sounding && this.ack && this.held.size === 0 &&
      this.setupProblems().length === 0 &&
      (this.step === STEP.LEVEL || this.step === STEP.RESULT);
  }

  /** Everything that keeps the setup step from going on (AC2, AC3). */
  setupProblems() {
    const out = [];
    if (!this.audio) return ["No audio device yet."];
    const rates = checkSampleRates(this.audio.outputRate, this.audio.inputRate);
    if (!rates.ok) out.push(rates.message);
    out.push(...checkDspFlags(this.audio.dspSettings).reasons);
    if (!this._channelOk(this.channel)) out.push("Choose the output channel.");
    out.push(...checkDeclaration(this.decl).errors);
    return out;
  }

  /** beforeunload warning (AC11). */
  hasUnsavedWork() {
    if (this.step === STEP.MEASURE || this.run.sounding) return true;
    for (const f of this.filters.values()) if (!f.downloaded) return true;
    return false;
  }

  /** AC11 download, with the E5b D4 per-channel mark. */
  downloads() {
    return [...this.filters.entries()].map(([channel, f]) => ({
      channel,
      name: f.preDeviceChange ? markedName(f.fileName) : f.fileName,
      bytes: f.wavBytes,
      preDeviceChange: f.preDeviceChange,
    }));
  }

  /** One channel's file, or every file without a channel. */
  markDownloaded(channel) {
    for (const [ch, f] of this.filters) {
      if (channel === undefined || ch === channel) f.downloaded = true;
    }
  }

  // -- setup --------------------------------------------------------------

  /**
   * The devices as the page sees them: { outputRate, inputRate,
   * outputChannels, dspSettings, micId, micLabel }.
   */
  setAudio(audio) {
    this.audio = audio ? { ...audio } : null;
    if (audio) this._releaseDeviceHolds();  // opened again
    return [];
  }

  setChannel(channel) {
    if (!this._editable()) return [];
    this.channel = channel;
    return [];
  }

  setDeclaration(decl) {
    if (!this._editable()) return [];
    this.decl = { ...decl };
    return [];
  }

  /** Choosing a file binds it to the selected mic (E5b D3). */
  loadCalibration(fileName, parsed) {
    if (!this._editable()) return [];
    this.cal = { fileName, parsed };
    this.calBoundMicId = this.audio ? this.audio.micId : null;
    return this._meterCal();
  }

  /** E5b D3 [Use <file> for this microphone]. */
  bindCalibration() {
    if (!this._editable() || !this.cal || !this.audio) return [];
    this.calBoundMicId = this.audio.micId;
    return this._meterCal();
  }

  clearCalibration() {
    if (!this._editable()) return [];
    this.cal = null;
    this.calBoundMicId = null;
    return this._meterCal();
  }

  confirmSetup() {
    if (this.step !== STEP.SETUP || this.setupProblems().length) return [];
    this.notice = null;
    this.step = this.ack ? STEP.LEVEL : STEP.ACK;
    return [];
  }

  /** Tick or untick one 4a item (UX 64c83e3e: one checkbox per item). */
  tickAck(item, ticked) {
    if (this.step !== STEP.ACK || !Number.isInteger(item) || item < 0 ||
        item >= FLOW.ACK_ITEMS) {
      return [];
    }
    if (ticked) this.ackTicks.add(item);
    else this.ackTicks.delete(item);
    return [];
  }

  /** The 4a button is enabled only when every item is ticked. */
  get canAcknowledge() {
    return this.step === STEP.ACK && this.ackTicks.size === FLOW.ACK_ITEMS;
  }

  /** 4a, once per session (until a device change, E5b D1). */
  acknowledge() {
    if (!this.canAcknowledge) return [];
    this.ack = true;
    this.step = STEP.LEVEL;
    return [];
  }

  /** Back to setup from the ack, level or result step. Stops any sound. */
  backToSetup() {
    if (this.step === STEP.SETUP) return [];
    const cmds = this._halt();
    this._resetRun();
    this.step = STEP.SETUP;
    this.notice = null;
    return cmds;
  }

  // -- level check (AC4b, 4d, 4h, 4i) -------------------------------------

  startLevel(nowMs) {
    if (!this.canStart) return [];
    const band = levelNoiseBand(this.decl.role, this.decl.limitHz);
    const entry = crestEntry(band, this.channel);
    const top = topStepDbfs(band);
    if (!entry || top === null) {
      this.notice = { cause: "no-level-table", text: FLOW_TEXT.NO_LEVEL_TABLE };
      return [];
    }
    this._resetRun();
    this.step = STEP.LEVEL;
    this.notice = null;
    const lc = new LevelCheck({ maxLevelDbfs: top, splOffsetDb: this.splOffsetDb });
    const r = lc.start(nowMs);
    Object.assign(this.run, { lc, band, entry, sounding: true });
    return [{
      type: "noise-start",
      channel: this.channel,
      source: { kind: "noise", seed: crestSeed(this.channel), band },
      gain: unitGain(entry, r.gainDbfs),
    }];
  }

  stepUp(nowMs) {
    const lc = this.run.lc;
    if (this.step !== STEP.LEVEL || !lc) return [];
    const r = lc.stepUp(nowMs);
    return r ? [{ type: "gain", gain: unitGain(this.run.entry, r.gainDbfs) }] : [];
  }

  /** Is a "+" step left? (the UI disables "+" otherwise). */
  canStepUp() {
    return this.step === STEP.LEVEL && !!this.run.lc && this.run.lc.canStepUp();
  }

  /** "Target not reached at maximum test level" (AE K5). */
  get atTopWithoutTarget() {
    const lc = this.run.lc;
    return !!lc && lc.running && !lc.targetReached && !lc.canStepUp();
  }

  /** The level check's ceiling for the current band, for "cap shown". */
  get levelCeilingDbfs() {
    return this.run.band ? bandCeilingDbfs(this.run.band) : null;
  }

  // -- meter, output and page events --------------------------------------

  /** One meter-worklet report: { peakDbfs, rmsDbfs, ... }. */
  meter(nowMs, reading) {
    if (this.step === STEP.LEVEL && this.run.lc && this.run.lc.running) {
      const cause = this.run.lc.update(nowMs, reading);
      if (cause) return this._stopLevel(cause);
      this.run.micRmsDbfs = reading.rmsDbfs;
      return [];
    }
    if (this.step === STEP.MEASURE && this.run.capturing) {
      const cause = sweepStopCause(this.run.confirmed.micRmsDbfs, reading,
        this.run.confirmed.splOffsetDb);
      if (cause) return this._abortMeasure(cause);
    }
    return [];
  }

  /** Clock tick: the 30 s level-check timeout without meter reports. */
  tick(nowMs) {
    if (this.step === STEP.LEVEL && this.run.lc) {
      const cause = this.run.lc.tick(nowMs);
      if (cause) return this._stopLevel(cause);
    }
    return [];
  }

  /** An output-worklet message: clamped / error / stopped / ended. */
  output(msg) {
    if (msg.type === "error") return this.audioError();
    if (msg.type === "stopped" && msg.cause === LATCH.HEARTBEAT) {
      return this._hold(STOP.HEARTBEAT);
    }
    if (!this.run.sounding) return [];
    if (msg.type === "clamped") return this.autoStop(STOP.CAP);
    // A render-thread stop (stop-latch.js) the meter report has not brought.
    if (msg.type === "stopped" && msg.cause) return this.autoStop(msg.cause);
    return [];
  }

  /** STOP button and Esc (4e). */
  userStop() {
    return this.autoStop(STOP.USER);
  }

  /** visibilitychange/pagehide (4d). */
  hidden() {
    this.held.add(STOP.HIDDEN);
    return this.autoStop(STOP.HIDDEN);
  }

  /** The page is visible again: Start may be pressed again. */
  visible() {
    this.held.delete(STOP.HIDDEN);
    return [];
  }

  /** Held until the devices are opened again (setAudio, deviceChange). */
  audioError() {
    return this._hold(STOP.AUDIO_ERROR);
  }

  /**
   * E6b: the text next to a Start disabled by a device hold, also when the
   * hold came while nothing was sounding; the latest hold names it. A
   * hidden page has no text.
   */
  get holdText() {
    const causes = [...this.held].filter((c) => DEVICE_HOLDS.includes(c));
    return causes.length ? stopMessage(causes[causes.length - 1]) : "";
  }

  _hold(cause) {
    this.held.delete(cause);           // re-added last: the latest names it
    this.held.add(cause);
    return this.autoStop(cause);
  }

  _releaseDeviceHolds() {
    for (const c of DEVICE_HOLDS) this.held.delete(c);
  }

  /** Any stop cause except device and rate changes. */
  autoStop(cause) {
    if (this.step === STEP.MEASURE) return this._abortMeasure(cause);
    if (this.step === STEP.LEVEL && this.run.sounding) return this._stopLevel(cause);
    return [];
  }

  /** E5a/E5b: any device connected, removed or switched. */
  deviceChange(audio) {
    const cmds = this._halt();
    this._resetRun();
    if (audio) {
      this.audio = { ...audio };
      this._releaseDeviceHolds();
    }
    this.ack = false;                   // D1
    this.ackTicks.clear();              // D1: every tick again
    this.channel = null;                // D2
    this.decl = emptyDeclaration();     // D2
    this.calBoundMicId = null;          // D3
    for (const f of this.filters.values()) f.preDeviceChange = true; // D4
    this.step = STEP.SETUP;
    this.notice = { cause: STOP.DEVICE, text: stopMessage(STOP.DEVICE) };
    return [...cmds, ...this._meterCal()];
  }

  /** AC2b: a rate change returns to the 2a refusal. */
  rateChange(audio) {
    const cmds = this._halt();
    this._resetRun();
    this.audio = { ...this.audio, ...audio };
    const rate = [this.audio.outputRate, this.audio.inputRate]
      .find((r) => r !== LIMITS.REQUIRED_RATE) ?? this.audio.outputRate;
    this.step = STEP.SETUP;
    this.notice = { cause: STOP.RATE, text: stopMessage(STOP.RATE, { rate }) };
    return cmds;
  }

  // -- measure (AC4g, 7, 8) -----------------------------------------------

  /** Level confirmed: stop the noise, plan the sweep at the same RMS (A4). */
  measure() {
    const lc = this.run.lc;
    if (this.step !== STEP.LEVEL || !lc || !lc.running ||
        this.run.micRmsDbfs === null) {
      return [];
    }
    const levelDbfs = lc.levelDbfs;
    lc.stop(STOP.USER);
    const plan = { ...sweepPlan(this.decl.limitHz, FLOW.SWEEP_S),
      sampleRate: LIMITS.REQUIRED_RATE };
    this.run.confirmed = {
      levelDbfs,
      micRmsDbfs: this.run.micRmsDbfs,
      targetReached: lc.targetReached,
      splOffsetDb: this.splOffsetDb,
    };
    this.run.plan = plan;
    this.run.sounding = false;
    this.step = STEP.MEASURE;
    this.notice = null;
    const token = this._wait("sweep");
    return [{ type: "output-stop" }, { type: "make-sweep", token, plan }];
  }

  /** The unit-level sweep for the plan (from the pipeline). */
  sweepReady(token, samples) {
    if (!this._is(token, "sweep")) return [];
    const r = rms(samples);
    const gain = r > 0 ? dbToLinear(this.run.confirmed.levelDbfs) / r : 0;
    if (!(gain > 0) || !(peak(samples) * gain < CAP_LINEAR)) {
      return this._abortMeasure("sweep-over-cap", FLOW_TEXT.SWEEP_OVER_CAP);
    }
    const pre = Math.round(FLOW.PRE_ROLL_S * LIMITS.REQUIRED_RATE);
    const played = new Float32Array(pre + samples.length);
    played.set(samples, pre);
    this.run.played = played;
    this.run.gain = gain;
    return this._capture();
  }

  /** The pipeline could not make the sweep: named error, back to the level check. */
  sweepFailed(token, message) {
    if (!this._is(token, "sweep")) return [];
    return this._abortMeasure("rejected", message);
  }

  /** A finished recording from the meter worklet. */
  recorded(token, samples) {
    if (!this._is(token, "record")) return [];
    this.run.captures.push(samples);
    this.run.capturing = false;
    this.run.sounding = false;
    if (this.run.captures.length < FLOW.CAPTURES) return this._capture();
    const t = this._wait("analyze");
    return [{ type: "output-stop" }, {
      type: "analyze",
      token: t,
      request: {
        channel: this.channel,
        decl: { ...this.decl },
        plan: this.run.plan,
        played: this.run.played,
        gain: this.run.gain,
        preRollS: FLOW.PRE_ROLL_S,
        captures: [...this.run.captures],
        levelDbfs: this.run.confirmed.levelDbfs,
        targetReached: this.run.confirmed.targetReached,
        calibrated: this.run.confirmed.splOffsetDb !== null,
        calibrationFile: this.run.confirmed.splOffsetDb !== null
          ? this.cal.fileName : null,
      },
    }];
  }

  /** result: { fileName, wavBytes, ... } that passed every AC6c gate. */
  analysisDone(token, result) {
    if (!this._is(token, "analyze")) return [];
    this.filters.set(this.channel, { ...result, role: this.decl.role,
      preDeviceChange: false, downloaded: false });
    this.run.result = result;
    this.run.pending = null;
    this.step = STEP.RESULT;
    this.notice = null;
    return [];
  }

  /** A capture or a gate failed closed (AC6c, AC7, AC8a): named error. */
  analysisFailed(token, message) {
    if (!this._is(token, "analyze")) return [];
    this._resetRun();
    this.step = STEP.LEVEL;
    this.notice = { cause: "rejected", text: message };
    return [];
  }

  // -- internals ----------------------------------------------------------

  _resetRun() {
    this.run = {
      lc: null, band: null, entry: null, micRmsDbfs: null, confirmed: null,
      plan: null, played: null, gain: 0, captures: [], capturing: false,
      sounding: false, pending: null, result: null,
    };
  }

  _channelOk(ch) {
    const n = Math.min(MAX_CHANNELS, this.audio ? this.audio.outputChannels : 0);
    return Number.isInteger(ch) && ch >= 0 && ch < n;
  }

  _editable() {
    return this.step === STEP.SETUP;
  }

  _meterCal() {
    return [{ type: "meter-calibration", splOffsetDb: this.splOffsetDb }];
  }

  _wait(kind) {
    this._token += 1;
    this.run.pending = { kind, token: this._token };
    return this._token;
  }

  _is(token, kind) {
    const p = this.run.pending;
    return !!p && p.kind === kind && p.token === token;
  }

  _capture() {
    const token = this._wait("record");
    const frames = Math.round((FLOW.PRE_ROLL_S +
      captureSeconds(this.run.plan.seconds)) * LIMITS.REQUIRED_RATE);
    this.run.capturing = true;
    this.run.sounding = true;
    return [
      { type: "record", token, frames },
      { type: "sweep-start", channel: this.channel, samples: this.run.played,
        gain: this.run.gain },
    ];
  }

  /** Stop all sound and recording; pending replies become stale. */
  _halt() {
    const cmds = [];
    if (this.run.sounding) cmds.push({ type: "output-stop" });
    if (this.run.capturing) cmds.push({ type: "record-cancel" });
    if (this.run.lc) this.run.lc.stop(STOP.USER);
    this.run.sounding = false;
    this.run.capturing = false;
    this.run.pending = null;
    return cmds;
  }

  /** 4i: the level-check step stays open and names the cause. */
  _stopLevel(cause) {
    if (this.run.lc) this.run.lc.stop(cause);
    const cmds = this._halt();
    this.notice = { cause, text: stopMessage(cause, { calibrated: this.calibrated }) };
    return cmds;
  }

  /**
   * E4: an auto-STOP during the measure returns to the level check. Every
   * capture is discarded; a stop during capture 2 says so (AE cf32c0a6 b).
   */
  _abortMeasure(cause, text) {
    const both = this.run.capturing && this.run.captures.length > 0;
    const cmds = this._halt();
    this._resetRun();
    this.step = STEP.LEVEL;
    this.notice = { cause,
      text: text || stopMessage(cause, { calibrated: this.calibrated }) };
    if (both) this.notice.detail = FLOW_TEXT.BOTH_DISCARDED;
    return cmds;
  }
}
