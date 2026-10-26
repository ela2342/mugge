// meter-core.js -- mic meter for the level check and the sweep (US-179
// AC4b, E1 v2, E3).
//
// Pure: no Web Audio, no DOM. meter-worklet.js feeds it every render
// quantum; the tests feed it directly. From every sample (no decimation, no
// skipped blocks) it computes the per-quantum true sample peak and a 100 ms
// sliding RMS over contiguous samples, updated every quantum. The auto-STOP
// decision (safety.micStopCause) is made on these values, per quantum.

import { linearToDb, micStopCause } from "./safety.js";

export const METER = Object.freeze({
  RMS_WINDOW_MS: 100,  // E3a / AE A3
  REPORT_QUANTA: 4,    // regular report every 4 quanta (~10.7 ms at 48 kHz)
});

/** Per-quantum true peak and 100 ms sliding RMS. */
export class MicMeter {
  constructor(sampleRate) {
    this.n = Math.round(sampleRate * METER.RMS_WINDOW_MS / 1000);
    this.sq = new Float64Array(this.n);
    this.pos = 0;
    this.count = 0;
    this.sum = 0;
  }

  /**
   * One render quantum. Returns { peakDbfs, rmsDbfs }: the true peak of this
   * quantum and the RMS of the last 100 ms ending at its last sample (fewer
   * samples only during the first 100 ms after start). A non-finite sample
   * counts as a clip.
   */
  process(block) {
    let peak = 0;
    for (let i = 0; i < block.length; i++) {
      let v = block[i];
      if (!Number.isFinite(v)) {
        peak = Infinity;
        v = 0;
      } else {
        const a = Math.abs(v);
        if (a > peak) peak = a;
      }
      const q = v * v;
      this.sum += q - this.sq[this.pos];
      this.sq[this.pos] = q;
      if (this.count < this.n) this.count++;
      if (++this.pos === this.n) {
        this.pos = 0;
        // Exact re-sum once per window, so rounding cannot accumulate.
        let s = 0;
        for (let j = 0; j < this.n; j++) s += this.sq[j];
        this.sum = s;
      }
    }
    const rms = this.count ? Math.sqrt(Math.max(this.sum, 0) / this.count) : 0;
    return { peakDbfs: linearToDb(peak), rmsDbfs: linearToDb(rms) };
  }
}

/**
 * Meter plus stop decision and report batching.
 *
 * process(block) returns a report or null. A report carries the maxima of
 * the per-quantum values since the last report, so no quantum's value is
 * lost by batching: { peakDbfs, rmsDbfs, rmsLastDbfs, quanta, cause }.
 * cause is the first stop cause seen in those quanta (or null); a quantum
 * with a stop cause is reported at once.
 */
export class MeterStream {
  constructor(sampleRate, splOffsetDb = null) {
    this.meter = new MicMeter(sampleRate);
    this.setCalibration(splOffsetDb);
    this._resetBatch();
  }

  setCalibration(splOffsetDb) {
    if (!(splOffsetDb === null || Number.isFinite(splOffsetDb))) {
      throw new RangeError("splOffsetDb must be a number or null");
    }
    this.splOffsetDb = splOffsetDb;
  }

  _resetBatch() {
    this.peakMax = -Infinity;
    this.rmsMax = -Infinity;
    this.quanta = 0;
    this.cause = null;
  }

  process(block) {
    const r = this.meter.process(block);
    if (r.peakDbfs > this.peakMax) this.peakMax = r.peakDbfs;
    if (r.rmsDbfs > this.rmsMax) this.rmsMax = r.rmsDbfs;
    this.quanta++;
    const cause = micStopCause(r, this.splOffsetDb);
    if (cause !== null && this.cause === null) this.cause = cause;
    if (cause === null && this.quanta < METER.REPORT_QUANTA) return null;
    const report = {
      peakDbfs: this.peakMax,
      rmsDbfs: this.rmsMax,
      rmsLastDbfs: r.rmsDbfs,
      quanta: this.quanta,
      cause: this.cause,
    };
    this._resetBatch();
    return report;
  }
}
