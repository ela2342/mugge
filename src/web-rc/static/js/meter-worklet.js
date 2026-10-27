// meter-worklet.js -- the capture/meter AudioWorklet for the mic (US-179
// AC2d, AC4b, AC7, E1 v2, E3). Meters every quantum (meter-core.MeterStream)
// and records captures from the same samples. Input channel 0 only (create
// the node with channelCount 1, channelCountMode "explicit",
// channelInterpretation "discrete"). No outputs.
//
// processorOptions: { splOffsetDb } (null without a calibration file).
// In:  { type: "calibration", splOffsetDb }
//      { type: "record", id, frames, lookback }   start at the next quantum;
//      lookback = frames before the start that the clock check covers
//      { type: "record-cancel" }
// A report with a stop cause also trips stop-latch.js, which stops the output
// worklet without the main thread (Architect note b). Every process() then
// writes the heartbeat (latch r2 A4), after the stop conditions: a count of
// process() calls (Architect 3fb4cd0c B1), not currentFrame.
//
// Out: { type: "meter", frame, peakDbfs, rmsDbfs, rmsLastDbfs, quanta, cause }
//      frame = currentFrame at the end of the reported quanta.
//      { type: "recorded", id, startFrame, samples, clockGlitch }
//      (samples transferred). clockGlitch = { before, after }: a currentFrame
//      step other than +128 from `lookback` frames before startFrame to the
//      last sample (AE 42dada94 G1), else null.

import { FrameClock, MeterStream, Recorder } from "./meter-core.js";
import { stopLatch } from "./stop-latch.js";

class MicMeterProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const opts = (options && options.processorOptions) || {};
    this.stream = new MeterStream(sampleRate, opts.splOffsetDb ?? null);
    this.silence = null;
    this.rec = null;
    this.clock = new FrameClock();
    // The heartbeat count, +1 per process() call. One meter node per
    // AudioContext (audio-io.js builds it with the context; a new context
    // is a new latch scope). A second meter per context would need one
    // counter per scope in stop-latch.js, never one per node.
    this.beats = 0;
    this.port.onmessage = (e) => {
      const d = e.data || {};
      if (d.type === "calibration") {
        this.stream.setCalibration(d.splOffsetDb ?? null);
      } else if (d.type === "record") {
        // A bad lookback checks the context's whole life (fails closed).
        const back = Number.isInteger(d.lookback) && d.lookback >= 0
          ? Math.ceil(d.lookback / 128) : Infinity;
        this.rec = { id: d.id, startFrame: null, from: null, back,
          recorder: new Recorder(d.frames) };
      } else if (d.type === "record-cancel") {
        this.rec = null;
      }
    };
  }

  process(inputs) {
    this.clock.step(currentFrame);
    let block = inputs[0] && inputs[0][0];
    if (!block) {
      // No input connected this quantum: meter silence, keep the window
      // contiguous.
      if (!this.silence) this.silence = new Float32Array(128);
      block = this.silence;
    }
    if (this.rec) {
      if (this.rec.startFrame === null) {
        this.rec.startFrame = currentFrame;
        this.rec.from = this.clock.n - this.rec.back;
      }
      const done = this.rec.recorder.push(block);
      if (done) {
        const { id, startFrame, from } = this.rec;
        this.rec = null;
        this.port.postMessage({ type: "recorded", id, startFrame, samples: done,
          clockGlitch: this.clock.since(from) }, [done.buffer]);
      }
    }
    const report = this.stream.process(block);
    if (report) {
      if (report.cause) stopLatch.trip(report.cause);
      this.port.postMessage({
        type: "meter", frame: currentFrame + block.length, ...report,
      });
    }
    this.beats += 1;
    stopLatch.beat(this.beats);
    return true;
  }
}

registerProcessor("webrc-mic-meter", MicMeterProcessor);
