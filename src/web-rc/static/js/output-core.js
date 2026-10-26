// output-core.js -- the output chain for the level check and the sweep
// (US-179 AC4c, 4e, 4f, 4h, 5d; AE A4).
//
// Pure: no Web Audio, no DOM. output-worklet.js runs it per render quantum;
// the controller runs the same code offline to get the exact played signal
// for deconvolution (Architect Q2); the tests run it directly.
//
// Per sample: source -> gain (linear ramps of RAMP_MS, starting from 0) ->
// clamp at the -20 dBFS cap, the last stage. A sample that reaches the cap
// (or is not finite) is held at the cap, reported, and starts the stop ramp:
// a backstop, never a limiter that keeps playing.

import { LIMITS, dbToLinear } from "./safety.js";

/** The cap as the f32 output sees it. */
export const CAP_LINEAR = Math.fround(dbToLinear(LIMITS.OUTPUT_PEAK_CAP_DBFS));

/** Plays a Float32Array once, then silence. */
export class BufferSource {
  constructor(samples) {
    this.samples = samples;
    this.pos = 0;
  }

  get ended() {
    return this.pos >= this.samples.length;
  }

  nextSample() {
    return this.pos < this.samples.length ? this.samples[this.pos++] : 0;
  }
}

export const STATE = Object.freeze({
  RUNNING: "running",
  STOPPING: "stopping",
  STOPPED: "stopped",
});

/**
 * source: anything with nextSample() (dsp.LevelNoise, BufferSource).
 * gain: the linear target gain; output ramps in from 0 (4h).
 */
export class OutputChain {
  constructor({ sampleRate, source, gain }) {
    this.source = source;
    this.rampLen = Math.round(sampleRate * LIMITS.RAMP_MS / 1000);
    this.g = 0;
    this.state = STATE.RUNNING;
    this.clamped = false;
    this._ramp(gain);
  }

  _ramp(target) {
    if (!(Number.isFinite(target) && target >= 0)) {
      throw new RangeError("gain must be a finite number >= 0");
    }
    this.target = target;
    this.step = (target - this.g) / this.rampLen;
    this.left = this.rampLen;
  }

  /** A level-check step (4h): ramp to the new gain, never jump. */
  setGain(gain) {
    if (this.state === STATE.RUNNING) this._ramp(gain);
  }

  /** STOP (4e): ramp to 0, then silence. */
  stop() {
    if (this.state === STATE.RUNNING) {
      this.state = STATE.STOPPING;
      this._ramp(0);
    }
  }

  /**
   * Fill `out` (Float32Array). Returns the events of this block:
   * { clampedAt: index | -1, stopped: bool, ended: bool }.
   */
  render(out) {
    const ev = { clampedAt: -1, stopped: false, ended: false };
    if (this.state === STATE.STOPPED) {
      out.fill(0);
      return ev;
    }
    for (let i = 0; i < out.length; i++) {
      if (this.state === STATE.STOPPED) {
        out[i] = 0;
        continue;
      }
      if (this.left > 0) {
        this.left--;
        this.g = this.left === 0 ? this.target : this.g + this.step;
      }
      const y = Math.fround(this.source.nextSample() * this.g);
      if (Number.isFinite(y) && Math.abs(y) < CAP_LINEAR) {
        out[i] = y;
      } else {
        out[i] = Number.isFinite(y) ? Math.sign(y) * CAP_LINEAR : 0;
        if (!this.clamped) {
          this.clamped = true;
          ev.clampedAt = i;
        }
        this.stop();
      }
      if (this.state === STATE.STOPPING && this.left === 0) {
        this.state = STATE.STOPPED;
        ev.stopped = true;
      }
    }
    if (this.source.ended) ev.ended = true;
    return ev;
  }
}

/**
 * The exact signal the chain plays for a buffer source at a fixed gain,
 * rendered in `quantum`-sized blocks like the worklet (for deconvolution).
 */
export function renderPlayed(samples, gain, sampleRate, quantum = 128) {
  const chain = new OutputChain({
    sampleRate, source: new BufferSource(samples), gain,
  });
  const out = new Float32Array(Math.ceil(samples.length / quantum) * quantum);
  for (let i = 0; i < out.length; i += quantum) {
    chain.render(out.subarray(i, i + quantum));
  }
  return { played: out.subarray(0, samples.length), clamped: chain.clamped };
}
