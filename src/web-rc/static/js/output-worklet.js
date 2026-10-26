// output-worklet.js -- AudioWorklet for the test noise and the sweep
// (US-179 AC4c, 4e, 4f, 4h, 5). Wraps output-core.OutputChain.
//
// One output with outputChannelCount [device channels]. Mono to ONE
// channel; every other channel is digital zero (4f).
//
// processorOptions:
//   { channel, gain, source: { kind: "noise", seed, band }       (AC5d)
//                         | { kind: "buffer", samples } }        (sweep)
// In:  { type: "gain", gain }   level-check step, ramped (4h)
//      { type: "stop" }         STOP / Esc / auto-STOP, ramped (4e)
// A meter auto-STOP (stop-latch.js) starts the same STOP ramp from the next
// process() call, without the main thread (Architect note b). So do a stale
// meter heartbeat and a newer output (latch r2 A1, A4). Until the first
// fresh heartbeat the node outputs zeros and its ramp-in waits. The STOP
// ramp is computed here, so it runs without the meter and the main thread
// (r2 B2); nothing reverses it (B3).
//
// Out: { type: "clamped", frame }   the cap was reached (5d)
//      { type: "stopped", frame, clamped, cause }   zero reached (r2 B4);
//        cause: the meter's, "heartbeat", "superseded", or null
//      { type: "ended", frame }      buffer source finished
//      { type: "error", message }    nothing is played

import { LevelNoise } from "./dsp.js";
import { BufferSource, OutputChain } from "./output-core.js";
import { OutputGate, stopLatch } from "./stop-latch.js";

class OutputProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const o = (options && options.processorOptions) || {};
    this.channel = o.channel;
    this.chain = null;
    this.endedSent = false;
    this.gate = new OutputGate(stopLatch);
    try {
      const src = o.source || {};
      let source;
      if (src.kind === "noise") {
        source = new LevelNoise(src.seed, sampleRate, src.band);
      } else if (src.kind === "buffer" && src.samples instanceof Float32Array) {
        source = new BufferSource(src.samples);
      } else {
        throw new Error("unknown source");
      }
      if (!Number.isInteger(this.channel) || this.channel < 0) {
        throw new Error("bad channel");
      }
      this.chain = new OutputChain({ sampleRate, source, gain: o.gain });
    } catch (e) {
      this.port.postMessage({ type: "error", message: String(e && e.message || e) });
    }
    this.port.onmessage = (e) => {
      if (!this.chain || !e.data) return;
      if (e.data.type === "gain") {
        try {
          this.chain.setGain(e.data.gain);
        } catch (err) {
          this.chain.stop();
          this.port.postMessage({ type: "error", message: String(err.message) });
        }
      } else if (e.data.type === "stop") {
        this.chain.stop();
      }
    };
  }

  process(inputs, outputs) {
    const out = outputs[0];
    for (const ch of out) ch.fill(0);
    if (!this.chain) return false;
    const target = out[this.channel];
    if (!target) {
      this.chain = null;
      this.port.postMessage({ type: "error", message: "no such output channel" });
      return false;
    }
    const g = this.gate.check();
    if (g.stop) this.chain.stop();
    if (!g.play) return true;
    const ev = this.chain.render(target);
    const frame = currentFrame;
    if (ev.clampedAt >= 0) {
      this.port.postMessage({ type: "clamped", frame: frame + ev.clampedAt });
    }
    if (ev.ended && !this.endedSent) {
      this.endedSent = true;
      this.port.postMessage({ type: "ended", frame: frame + target.length });
    }
    if (ev.stopped) {
      this.port.postMessage({
        type: "stopped", frame: frame + target.length, clamped: this.chain.clamped,
        cause: this.gate.cause,
      });
    }
    return true;
  }
}

registerProcessor("webrc-output", OutputProcessor);
