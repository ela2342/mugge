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
//
// Stop order (latch r2 B4, AE 6f220842): a stopping output node ramps to 0
// on the render thread and reports "stopped" (zero reached). Only then is it
// disconnected and the context suspended, and only then is a new output
// node built and connected: an old ramp-down never overlaps a new ramp-in.
//
// Clock (AE onset condition): every open() is a new context with its own
// currentFrame clock and number. Output "started" messages and recordings
// carry the number of the context whose worklet stamped their frame, so
// the flow only compares frames from one clock.
// If "stopped" does not come within ZERO_TIMEOUT_MS, the context is
// suspended anyway and the node is treated as stopped.

import { checkDspFlags } from "./safety.js";

export const IO = Object.freeze({
  ZERO_TIMEOUT_MS: 100,   // AE 6f220842: "zero reached" deadline
});

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

let clockSeq = 0;

export class AudioIO {
  constructor({ onMeter, onOutput, onRecorded, onError } = {}) {
    this.onMeter = onMeter || (() => {});
    this.onOutput = onOutput || (() => {});
    this.onRecorded = onRecorded || (() => {});
    this.onError = onError || (() => {});
    this.ctx = null;
    this.clock = null;            // the open context's clock number
    this.stream = null;
    this.track = null;
    this.meter = null;
    this.out = null;              // the output node that may sound
    this.retiring = new Set();    // nodes stopping, until zero is reached
    this.recording = null;
    this.sinkId = "";
    this._playSeq = 0;
    this._waiting = 0;
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
    this.clock = ++clockSeq;
    meter.clock = this.clock;
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
    // Closing cuts the output: first let every ramp reach 0 (r2 B4).
    this._playSeq += 1;
    if (this.out) this._retire(this.out, true);
    await this._retired();
    this.out = null;
    this.recording = null;
    if (this.stream) for (const t of this.stream.getTracks()) t.stop();
    const ctx = this.ctx;
    this.ctx = this.clock = this.stream = this.track = this.meter = null;
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
        this._playSeq += 1;       // a play still waiting is cancelled
        if (this.out) this._retire(this.out, true);
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

  /** Start an output once every older output has reached 0 (r2 B4). */
  _play(channel, source, gain) {
    const seq = ++this._playSeq;
    if (this.out) {
      this._retire(this.out, true);
      this.out = null;            // its late messages are stale
    }
    const ctx = this.ctx;
    const go = () => {
      if (seq !== this._playSeq || this.ctx !== ctx) {
        this._idle();
        return;
      }
      const node = this._newOutput({ channel, gain, source });
      node.clock = this.clock;
      node.port.onmessage = (e) => this._onOutputMessage(node, e.data);
      node.connect(ctx.destination);
      this.out = node;
      this._run();
    };
    if (!this.retiring.size) {
      go();
      return;
    }
    this._waiting += 1;           // no suspend between the two nodes
    this._retired().then(() => {
      this._waiting -= 1;
      go();
    });
  }

  _newOutput(processorOptions) {
    return new AudioWorkletNode(this.ctx, "webrc-output", {
      numberOfInputs: 0, numberOfOutputs: 1,
      outputChannelCount: [this.ctx.destination.channelCount],
      channelInterpretation: "discrete",
      processorOptions,
    });
  }

  /** Resolves once no node is retiring. */
  async _retired() {
    while (this.retiring.size) {
      await Promise.all([...this.retiring].map((n) => n.retired));
    }
  }

  /**
   * Stop `node`: it ramps to 0 and reports "stopped". stopTrigger: a stop
   * (not just a finished sweep), so a missing report suspends the context.
   * A second call is a no-op (r2 B3).
   */
  _retire(node, stopTrigger) {
    if (node.retired) return;
    let done;
    node.retired = new Promise((r) => { done = r; });
    this.retiring.add(node);
    const ctx = this.ctx;
    const finish = () => {
      if (!this.retiring.has(node)) return;
      clearTimeout(timer);
      node.disconnect();
      this.retiring.delete(node);
      if (this.out === node) this.out = null;
      done();
      this._idle();
    };
    node.finish = finish;
    const timer = setTimeout(async () => {
      if (stopTrigger && this.ctx === ctx) await ctx.suspend().catch(() => {});
      finish();
    }, IO.ZERO_TIMEOUT_MS);
    node.port.postMessage({ type: "stop" });
  }

  _onOutputMessage(node, msg) {
    const current = node === this.out;
    if (msg.type === "stopped") {
      // Zero reached: a stop from the render thread retires the node too.
      if (!node.retired) this._retire(node, true);
      node.finish();
    } else if (msg.type === "error") {
      this._retire(node, true);
    } else if (msg.type === "ended" && current) {
      // The sweep has played: its output is silent from here on.
      this._retire(node, false);
    }
    // A replaced output's messages are stale, except an error.
    if (msg.type === "started") msg = { ...msg, clock: node.clock };
    if (current || msg.type === "error") this.onOutput(msg);
  }

  _onMeterMessage(msg) {
    if (msg.type === "meter") {
      // The render thread is stopping the output (stop-latch.js): start
      // the zero-reached deadline now, not when the flow reacts.
      if (msg.cause && this.out) this._retire(this.out, true);
      this.onMeter(msg);
    } else if (msg.type === "recorded") {
      if (msg.id !== this.recording) return;
      this.recording = null;
      this.onRecorded(msg.id, msg.samples, msg.startFrame, this.meter.clock);
    }
  }

  _run() {
    if (this.ctx.state === "suspended") {
      this.ctx.resume().catch((e) => this.onError(String(e && e.message || e)));
    }
  }

  /** Suspend once nothing plays or records (4e). */
  _idle() {
    if (!this.ctx || this.out || this.retiring.size || this._waiting ||
        this.recording !== null) {
      return;
    }
    if (this.ctx.state === "running") {
      this.ctx.suspend().catch(() => {});
    }
  }
}
