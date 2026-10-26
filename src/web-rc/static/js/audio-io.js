// audio-io.js -- Web Audio and media devices for the standalone room
// correction (US-179 AC2, AC4e/f, AC7). Carries out the flow's audio
// commands (flow.js) and reports what the devices do. No decisions: the
// flow decides, this module only plays, meters and records.
//
//   const io = new AudioIO({ onMeter, onOutput, onRecorded, onError });
//   await io.open({ micId, sinkId });   // on a user gesture
//   io.info()                           // -> flow.setAudio()
//   io.execute(cmd)                     // noise-start, gain, output-stop,
//                                       // meter-calibration, sweep-start,
//                                       // record, record-cancel
//
// The context runs only while something plays or records; otherwise it is
// suspended (4e). Both worklet modules load from the same base URL, so they
// share stop-latch.js in the context's one AudioWorkletGlobalScope.

import { checkDspFlags } from "./safety.js";

const METER_URL = new URL("./meter-worklet.js", import.meta.url);
const OUTPUT_URL = new URL("./output-worklet.js", import.meta.url);

/** getUserMedia constraints: every browser DSP flag off (AC2c). */
export function micConstraints(micId) {
  const audio = {
    echoCancellation: false,
    noiseSuppression: false,
    autoGainControl: false,
    channelCount: 1,
  };
  if (micId) audio.deviceId = { exact: micId };
  return { audio, video: false };
}

/** The three DSP flags as the track reports them (missing = undefined). */
export function dspSettings(settings) {
  return {
    echoCancellation: settings.echoCancellation,
    noiseSuppression: settings.noiseSuppression,
    autoGainControl: settings.autoGainControl,
  };
}

/** A device-list fingerprint, to tell a real change from a repeat event. */
export function deviceKey(devices) {
  return devices
    .filter((d) => d.kind === "audioinput" || d.kind === "audiooutput")
    .map((d) => d.kind + ":" + d.deviceId)
    .sort()
    .join("|");
}

export class AudioIO {
  constructor({ onMeter, onOutput, onRecorded, onError } = {}) {
    this.onMeter = onMeter || (() => {});
    this.onOutput = onOutput || (() => {});
    this.onRecorded = onRecorded || (() => {});
    this.onError = onError || (() => {});
    this.ctx = null;
    this.stream = null;
    this.track = null;
    this.meter = null;
    this.out = null;
    this.recording = null;
    this.sinkId = "";
  }

  get isOpen() {
    return this.ctx !== null;
  }

  /** Open the mic and the output device. Rejects with a named error. */
  async open({ micId = "", sinkId = "" } = {}) {
    await this.close();
    const stream = await navigator.mediaDevices.getUserMedia(micConstraints(micId));
    const opts = { latencyHint: "interactive" };
    if (sinkId && "setSinkId" in AudioContext.prototype) opts.sinkId = sinkId;
    let ctx;
    try {
      ctx = new AudioContext(opts);
      await ctx.suspend();
      await ctx.audioWorklet.addModule(METER_URL);
      await ctx.audioWorklet.addModule(OUTPUT_URL);
    } catch (e) {
      for (const t of stream.getTracks()) t.stop();
      if (ctx) await ctx.close().catch(() => {});
      throw e;
    }
    const dest = ctx.destination;
    dest.channelCount = dest.maxChannelCount;
    dest.channelCountMode = "explicit";
    dest.channelInterpretation = "discrete";

    const meter = new AudioWorkletNode(ctx, "webrc-mic-meter", {
      numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
      channelCountMode: "explicit", channelInterpretation: "discrete",
      processorOptions: { splOffsetDb: null },
    });
    meter.port.onmessage = (e) => this._onMeterMessage(e.data);
    ctx.createMediaStreamSource(stream).connect(meter);

    this.ctx = ctx;
    this.stream = stream;
    this.track = stream.getAudioTracks()[0];
    this.meter = meter;
    this.sinkId = opts.sinkId || "";
    this.track.addEventListener("ended", () => this.onError("ended"));
    ctx.addEventListener("statechange", () => {
      if (this.ctx === ctx && ctx.state !== "running" && ctx.state !== "suspended") {
        this.onError("context " + ctx.state);
      }
    });
  }

  async close() {
    this.out = null;
    this.recording = null;
    if (this.stream) for (const t of this.stream.getTracks()) t.stop();
    const ctx = this.ctx;
    this.ctx = this.stream = this.track = this.meter = null;
    if (ctx) await ctx.close().catch(() => {});
  }

  /** What flow.setAudio() needs (AC2a, 2c). */
  info() {
    if (!this.ctx) return null;
    const s = this.track.getSettings();
    return {
      outputRate: this.ctx.sampleRate,
      inputRate: s.sampleRate,
      outputChannels: this.ctx.destination.maxChannelCount,
      dspSettings: dspSettings(s),
      dspOk: checkDspFlags(dspSettings(s)).ok,
      micId: s.deviceId || "",
      micLabel: this.track.label || "",
      sinkId: this.sinkId,
    };
  }

  /** The mic's current rate, for the 2b rate watch. */
  inputRate() {
    return this.track ? this.track.getSettings().sampleRate : undefined;
  }

  execute(cmd) {
    if (!this.ctx) return;
    switch (cmd.type) {
      case "noise-start":
        this._play(cmd.channel, cmd.source, cmd.gain);
        break;
      case "sweep-start":
        this._play(cmd.channel, { kind: "buffer", samples: cmd.samples.slice() }, cmd.gain);
        break;
      case "gain":
        if (this.out) this.out.port.postMessage({ type: "gain", gain: cmd.gain });
        break;
      case "output-stop":
        if (this.out) this.out.port.postMessage({ type: "stop" });
        else this._idle();
        break;
      case "meter-calibration":
        this.meter.port.postMessage({ type: "calibration", splOffsetDb: cmd.splOffsetDb });
        break;
      case "record":
        this.recording = cmd.token;
        this.meter.port.postMessage({ type: "record", id: cmd.token, frames: cmd.frames });
        this._run();
        break;
      case "record-cancel":
        this.recording = null;
        this.meter.port.postMessage({ type: "record-cancel" });
        this._idle();
        break;
      default:
        throw new Error("not an audio command: " + cmd.type);
    }
  }

  // -- internals ----------------------------------------------------------

  _play(channel, source, gain) {
    if (this.out) this.out.port.postMessage({ type: "stop" });
    const node = new AudioWorkletNode(this.ctx, "webrc-output", {
      numberOfInputs: 0, numberOfOutputs: 1,
      outputChannelCount: [this.ctx.destination.channelCount],
      channelInterpretation: "discrete",
      processorOptions: { channel, gain, source },
    });
    node.port.onmessage = (e) => this._onOutputMessage(node, e.data);
    node.connect(this.ctx.destination);
    this.out = node;
    this._run();
  }

  _onOutputMessage(node, msg) {
    const current = node === this.out;
    if (msg.type === "stopped" || msg.type === "error") {
      node.disconnect();
      if (node === this.out) {
        this.out = null;
        this._idle();
      }
    }
    // A replaced output's messages are stale, except an error.
    if (current || msg.type === "error") this.onOutput(msg);
  }

  _onMeterMessage(msg) {
    if (msg.type === "meter") {
      this.onMeter(msg);
    } else if (msg.type === "recorded") {
      if (msg.id !== this.recording) return;
      this.recording = null;
      this.onRecorded(msg.id, msg.samples);
    }
  }

  _run() {
    if (this.ctx.state === "suspended") {
      this.ctx.resume().catch((e) => this.onError(String(e && e.message || e)));
    }
  }

  /** Suspend once nothing plays or records (4e). */
  _idle() {
    if (!this.out && this.recording === null && this.ctx.state === "running") {
      this.ctx.suspend().catch(() => {});
    }
  }
}
