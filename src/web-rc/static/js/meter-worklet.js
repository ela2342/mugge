// meter-worklet.js -- AudioWorklet for the mic meter (US-179 AC4b, E1 v2,
// E3). Wraps meter-core.MeterStream; meters input channel 0 only (create
// the node with channelCount 1, channelCountMode "explicit",
// channelInterpretation "discrete"). No outputs.
//
// processorOptions: { splOffsetDb } (null without a calibration file).
// In:  { type: "calibration", splOffsetDb }
// Out: { type: "meter", frame, peakDbfs, rmsDbfs, rmsLastDbfs, quanta, cause }
//      frame = currentFrame at the end of the reported quanta.

import { MeterStream } from "./meter-core.js";

class MicMeterProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const opts = (options && options.processorOptions) || {};
    this.stream = new MeterStream(sampleRate, opts.splOffsetDb ?? null);
    this.silence = null;
    this.port.onmessage = (e) => {
      if (e.data && e.data.type === "calibration") {
        this.stream.setCalibration(e.data.splOffsetDb ?? null);
      }
    };
  }

  process(inputs) {
    let block = inputs[0] && inputs[0][0];
    if (!block) {
      // No input connected this quantum: meter silence, keep the window
      // contiguous.
      if (!this.silence) this.silence = new Float32Array(128);
      block = this.silence;
    }
    const report = this.stream.process(block);
    if (report) {
      this.port.postMessage({
        type: "meter", frame: currentFrame + block.length, ...report,
      });
    }
    return true;
  }
}

registerProcessor("webrc-mic-meter", MicMeterProcessor);
