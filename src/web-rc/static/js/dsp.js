// dsp.js -- small DSP helpers for the web-rc worklets (US-179).
//
// Butterworth sections via the bilinear transform with prewarping, the same
// design scipy.signal.butter(..., output="sos") produces; a direct-form-II
// transposed biquad cascade; and the level-check noise source (AC5d).

import { PinkNoise } from "./noise.js";

/**
 * Butterworth highpass or lowpass of even order as biquad sections.
 * Returns [{b0, b1, b2, a1, a2}, ...] (a0 normalised to 1).
 */
export function butterworth(kind, order, cutoffHz, sampleRate) {
  if (order < 2 || order % 2 !== 0) {
    throw new RangeError("order must be even and >= 2");
  }
  if (!(cutoffHz > 0 && cutoffHz < sampleRate / 2)) {
    throw new RangeError("cutoff must be inside (0, fs/2)");
  }
  const k = Math.tan(Math.PI * cutoffHz / sampleRate);
  const k2 = k * k;
  const sections = [];
  for (let i = 0; i < order / 2; i++) {
    // Analog pole pair angle for a Butterworth of this order.
    const theta = Math.PI * (2 * i + 1) / (2 * order);
    const q2 = 2 * Math.sin(theta); // 1/Q
    const a0 = 1 + q2 * k + k2;
    const a1 = 2 * (k2 - 1) / a0;
    const a2 = (1 - q2 * k + k2) / a0;
    let b0, b1, b2;
    if (kind === "lowpass") {
      b0 = k2 / a0; b1 = 2 * b0; b2 = b0;
    } else if (kind === "highpass") {
      b0 = 1 / a0; b1 = -2 * b0; b2 = b0;
    } else {
      throw new RangeError("kind must be lowpass or highpass");
    }
    sections.push({ b0, b1, b2, a1, a2 });
  }
  return sections;
}

/** Biquad cascade, direct form II transposed, f64 state. */
export class Cascade {
  constructor(sections) {
    this.s = sections.map((c) => ({ ...c }));
    this.z1 = new Float64Array(sections.length);
    this.z2 = new Float64Array(sections.length);
  }

  process(x) {
    let y = x;
    for (let i = 0; i < this.s.length; i++) {
      const c = this.s[i];
      const out = c.b0 * y + this.z1[i];
      this.z1[i] = c.b1 * y - c.a1 * out + this.z2[i];
      this.z2[i] = c.b2 * y - c.a2 * out;
      y = out;
    }
    return y;
  }

  reset() {
    this.z1.fill(0);
    this.z2.fill(0);
  }
}

export const LEVEL_NOISE = Object.freeze({
  LOW_HZ: 100,
  HIGH_HZ: 10000,
  ORDER: 4,
  CREST_SECONDS: 10,
});

/**
 * Level-check noise (AC5d): pink noise at unit level through a 4th-order
 * Butterworth 100 Hz highpass and 10 kHz lowpass. nextSample() returns the
 * band-limited value at unit gain; the caller scales it.
 */
export class LevelNoise {
  constructor(seed, sampleRate) {
    this.pink = new PinkNoise(seed);
    this.filter = new Cascade([
      ...butterworth("highpass", LEVEL_NOISE.ORDER, LEVEL_NOISE.LOW_HZ, sampleRate),
      ...butterworth("lowpass", LEVEL_NOISE.ORDER, LEVEL_NOISE.HIGH_HZ, sampleRate),
    ]);
  }

  nextSample() {
    return this.filter.process(this.pink.nextSample(1.0));
  }
}

/**
 * Crest factor of the band-limited level noise for one seed, measured over
 * the first `seconds` of its deterministic stream (AC5d).
 * Returns { rms, peak, crestDb }.
 */
export function levelNoiseCrest(seed, sampleRate, seconds = LEVEL_NOISE.CREST_SECONDS) {
  const n = Math.round(seconds * sampleRate);
  const src = new LevelNoise(seed, sampleRate);
  let sumSq = 0;
  let peak = 0;
  for (let i = 0; i < n; i++) {
    const v = src.nextSample();
    sumSq += v * v;
    const a = Math.abs(v);
    if (a > peak) peak = a;
  }
  const rms = Math.sqrt(sumSq / n);
  return { rms, peak, crestDb: 20 * Math.log10(peak / rms) };
}
