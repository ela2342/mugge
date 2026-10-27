// The result-step plots (plot.js): geometry, and what lands on a canvas.

import { assert, close, eq } from "./assert.js";
import {
  IR_WINDOW_S, PAD, curveToBins, drawImpulse, drawPrediction,
  drawRepeatability, irEnvelope, irPeak, linY, logX, repeatabilityClasses,
} from "../../../static/js/plot.js";

const COLORS = {
  bg: "rgb(0, 0, 0)", grid: "rgb(0, 0, 0)", label: "rgb(0, 0, 0)",
  line: "rgb(255, 255, 255)", ok: "rgb(0, 255, 0)", over: "rgb(255, 0, 0)",
  unchecked: "rgb(0, 0, 255)", target: "rgb(0, 0, 255)",
  measured: "rgb(255, 0, 0)", predicted: "rgb(0, 255, 0)",
};

function canvas(w, h) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return c.getContext("2d", { willReadFrequently: true });
}

/** Does column x (plot box rows only) hold a pixel of this pure colour? */
function columnHas(ctx, x, h, channel) {
  const px = ctx.getImageData(x, PAD.top, 1, h - PAD.top - PAD.bottom).data;
  for (let i = 0; i < px.length; i += 4) {
    const rgb = [px[i], px[i + 1], px[i + 2]];
    if (rgb[channel] > 150 && rgb.every((v, k) => k === channel || v < 90)) {
      return true;
    }
  }
  return false;
}

/** The rows of column x holding this pure colour (plot box only). */
function rowsOf(ctx, x, h, channel) {
  const top = PAD.top, ph = h - PAD.top - PAD.bottom;
  const px = ctx.getImageData(x, top, 1, ph).data;
  const rows = [];
  for (let i = 0; i < px.length; i += 4) {
    const rgb = [px[i], px[i + 1], px[i + 2]];
    if (rgb[channel] > 150 && rgb.every((v, k) => k === channel || v < 90)) {
      rows.push(top + i / 4);
    }
  }
  return rows;
}

/** The trace's value sits at its row on the axis the plot labels. */
function atRow(ctx, x, h, channel, v, lo, hi, msg) {
  const rows = rowsOf(ctx, x, h, channel);
  const y = linY(v, lo, hi, PAD.top, h - PAD.top - PAD.bottom);
  assert(rows.length > 0 && rows.every((r) => Math.abs(r - y) <= 2),
    msg + ": rows " + rows + ", expected about " + y);
}

/** Bins inside the curve interpolate in log f; outside, the floor. */
export async function test_curve_to_bins() {
  // sampleRate 1000, fftSize 10: bins at 0, 100, 200, 300, 400 Hz.
  const out = curveToBins([100, 200, 400], [0, 6, 0], 10, 1000, -99);
  eq(out.length, 5);
  eq(out[0], -99, "DC is never drawn");
  eq(out[1], 0);
  eq(out[2], 6);
  close(out[3], 6 - 6 * Math.log(1.5) / Math.log(2), 1e-5, "log-f interpolation");
  eq(out[4], 0, "the last point is inside");
  const wide = curveToBins([100, 1000], [0, 10], 1024, 48000, -99);
  eq(wide[2], -99, "below the curve");
  close(wide[3], 10 * Math.log(1.40625) / Math.log(10), 1e-5);
  close(wide[21], 10 * Math.log(9.84375) / Math.log(10), 1e-5);
  eq(wide[22], -99, "above the curve");
  // sampleRate 1600, fftSize 16: bins every 100 Hz up to 700 Hz.
  const gap = curveToBins([100, 200, 400, 800], [0, NaN, 0, 3], 16, 1600, -99);
  eq(gap[1], 0, "a bin on a finite point takes it");
  eq(gap[2], -99, "a non-finite point is not drawn");
  eq(gap[3], -99, "nor a segment ending at one");
  eq(gap[4], 0, "the finite segment after it is");
  close(gap[6], 3 * Math.log(1.5) / Math.log(2), 1e-5);
  eq(curveToBins([100], [0], 10, 1000, -99)[1], -99, "one point is no curve");
}

export async function test_axes() {
  close(logX(100, 10, 1000, 0, 200), 100, 1e-9);
  close(logX(10, 10, 1000, 5, 200), 5, 1e-9);
  close(linY(0, -10, 10, 0, 100), 50, 1e-9);
  close(linY(10, -10, 10, 0, 100), 0, 1e-9);
  eq(linY(20, -10, 10, 0, 100), 0, "clamped at the top");
  eq(linY(-20, -10, 10, 0, 100), 100, "clamped at the bottom");
}

/** AC8a: green within the limit, red over it, grey outside the band. */
export async function test_repeatability_classes() {
  const cls = repeatabilityClasses([20, 30, 100, 200, 300],
    [5, 1.0, -1.01, -0.5, 9], [30, 200], 1.0);
  eq(cls.join(), "unchecked,ok,over,ok,unchecked");
}

/** The IR envelope: min/max per column, NaN where no sample falls. */
export async function test_ir_envelope() {
  const ir = Float32Array.from([1, -2, 3, 0, 0, 0, 0, 0, 0, -5]);
  const env = irEnvelope(ir, 0, 10, 0, 1, 5);
  eq(env.min[0], -2);
  eq(env.max[0], 1);
  eq(env.min[1], 0);
  eq(env.max[1], 3);
  eq(env.min[4], -5);
  eq(env.max[4], 0, "samples 8 and 9 share the last column");
  eq(irPeak(env), 5);
  const early = irEnvelope(ir, 0, 10, -0.5, 0.5, 2);
  assert(Number.isNaN(early.min[0]), "no sample before the IR starts");
  eq(early.max[1], 3, "samples 0..5 land in the second column");
  eq(early.min[1], -2);
  eq(irPeak(early), 3, "only the window counts, NaN skipped");
  // The IR starts before the window (irStartS -0.1): the start is cut.
  const late = irEnvelope(ir, -0.3, 10, 0, 0.6, 3);
  eq(late.max[0], 0, "samples before t0 are not shown");
  eq(irPeak(late), 5);
}

/** The trace lands on the canvas in the colour its class names. */
export async function test_draw_repeatability_colours() {
  const w = 300, h = 120;
  const ctx = canvas(w, h);
  const freqs = [20, 40, 80, 160, 320, 640];
  drawRepeatability(ctx, w, h, { freqs, diffDb: [0.5, 0.5, 2, 2, 0.5, 0.5],
    band: [40, 320], limitDb: 1.0 }, COLORS);
  const x = (a, b) => Math.round(logX(Math.sqrt(a * b), 20, 640, PAD.left,
    w - PAD.left - PAD.right));
  assert(columnHas(ctx, x(80, 160), h, 0), "over the limit: red");
  assert(!columnHas(ctx, x(80, 160), h, 1), "not green there");
  assert(columnHas(ctx, x(320, 640), h, 2), "outside the band: grey");
  // The axis spans three times the limit either way.
  atRow(ctx, x(80, 160), h, 0, 2, -3, 3, "2 dB on a +-3 dB axis");
  const ok = canvas(w, h);
  drawRepeatability(ok, w, h, { freqs, diffDb: freqs.map(() => 0.2),
    band: [40, 320], limitDb: 1.0 }, COLORS);
  assert(columnHas(ok, x(80, 160), h, 1), "within the limit: green");
  assert(!columnHas(ok, x(80, 160), h, 0), "and not red");
}

/** How many columns x0..x1 of row y are white (the limit lines). */
function whiteIn(ctx, y, x0, x1) {
  const px = ctx.getImageData(x0, y, x1 - x0, 1).data;
  let k = 0;
  for (let i = 0; i < px.length; i += 4) {
    if (px[i] > 150 && px[i + 1] > 150 && px[i + 2] > 150) k++;
  }
  return k;
}

/** UX 866c44ff: the limit as dashed lines at +-limit, over the band only. */
export async function test_draw_repeatability_limit_lines() {
  const w = 300, h = 120;
  const ctx = canvas(w, h);
  const freqs = [20, 40, 80, 160, 320, 640];
  drawRepeatability(ctx, w, h, { freqs, diffDb: freqs.map(() => 0.2),
    band: [40, 320], limitDb: 1.0 }, COLORS);
  const pw = w - PAD.left - PAD.right, ph = h - PAD.top - PAD.bottom;
  const x = (f) => Math.round(logX(f, 20, 640, PAD.left, pw));
  for (const v of [1, -1]) {
    const y = Math.round(linY(v, -3, 3, PAD.top, ph));
    const inside = whiteIn(ctx, y, x(40) + 2, x(320) - 2);
    const span = x(320) - x(40) - 4;
    assert(inside > span / 3 && inside < span * 0.9,
      v + " dB: dashed over the band, " + inside + " of " + span);
    eq(whiteIn(ctx, y, PAD.left + 1, x(40) - 2), 0, "not below the band");
    eq(whiteIn(ctx, y, x(320) + 2, PAD.left + pw - 1), 0,
      "not above the band");
  }
  // Nothing white elsewhere: the trace stays in its class colour.
  eq(whiteIn(ctx, Math.round(linY(0.2, -3, 3, PAD.top, ph)), x(40) + 2,
    x(320) - 2), 0);
}

/** AC8c: target, measured and predicted each drawn at its own level. */
export async function test_draw_prediction_curves() {
  const w = 300, h = 160;
  const ctx = canvas(w, h);
  const freqs = [30, 100, 300, 1000];
  drawPrediction(ctx, w, h, { freqs, measuredDb: freqs.map(() => 9),
    predictedDb: freqs.map(() => -6), targetDb: freqs.map(() => 0),
    legend: { target: "", measured: "", predicted: "" } }, COLORS);
  const x = Math.round(logX(170, 30, 1000, PAD.left, w - PAD.left - PAD.right));
  atRow(ctx, x, h, 0, 9, -18, 18, "measured");
  atRow(ctx, x, h, 1, -6, -18, 18, "predicted");
  atRow(ctx, x, h, 2, 0, -18, 18, "target");
}

/** A spike in the IR is drawn at its time, and nothing elsewhere. */
export async function test_draw_impulse_spike() {
  const w = 336, h = 120, sr = 48000, startS = -0.1;
  const ir = new Float32Array(Math.round(0.5 * sr));
  const at = 0.15;
  ir[Math.round((at - startS) * sr)] = 0.8;
  const ctx = canvas(w, h);
  drawImpulse(ctx, w, h, { ir, startS, sampleRate: sr }, COLORS);
  const [t0, t1] = IR_WINDOW_S;
  const pw = w - PAD.left - PAD.right;
  const col = PAD.left + Math.floor((at - t0) / (t1 - t0) * pw);
  const white = (x) => {
    const px = ctx.getImageData(x, PAD.top, 1, h - PAD.top - PAD.bottom).data;
    let n = 0;
    for (let i = 0; i < px.length; i += 4) if (px[i] > 150 && px[i + 1] > 150) n++;
    return n;
  };
  assert(white(col) > (h - PAD.top - PAD.bottom) / 3, "the spike's column");
  assert(white(col - 20) <= 2, "a quiet column is only the zero line");
}
