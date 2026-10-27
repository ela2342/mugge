// plot.js -- the result-step plots (US-179 AC11, Architect Q4 addendum).
//
// Geometry is pure and tested without a page; the draw functions take a
// 2D context and colours, so app.js only finds the canvases. The measured
// magnitude goes through web-ui's spectrum-renderer.js (curveToBins feeds
// it); the impulse response, the repeatability trace and the predicted
// residual are plain line plots. No phase and no "coherence" anywhere.

/** Frequency labels of the log axes; each plot shows those in its range. */
export const FREQ_TICKS = Object.freeze([[20, "20"], [30, "30"], [50, "50"],
  [100, "100"], [200, "200"], [500, "500"], [1000, "1k"], [2000, "2k"],
  [5000, "5k"], [10000, "10k"], [20000, "20k"]]);
/** The measured magnitude's fixed dB range and renderer FFT size (2.9 Hz). */
export const MEASURED_DB = Object.freeze([-36, 12]);
export const MEASURED_FFT = 16384;
/** Impulse-response window shown, seconds from the scheduled sweep onset. */
export const IR_WINDOW_S = Object.freeze([-0.02, 0.3]);

/**
 * A curve on log-spaced points onto the renderer's linear FFT bins
 * (bin k at k * sampleRate / fftSize). Interpolated linearly in log
 * frequency; bins outside the curve, or on a segment with a non-finite
 * end, get floorDb.
 */
export function curveToBins(freqs, db, fftSize, sampleRate, floorDb) {
  const out = new Float32Array(fftSize / 2).fill(floorDb);
  const n = freqs.length;
  if (n < 2) return out;
  let j = 0;
  for (let k = 1; k < out.length; k++) {
    const f = k * sampleRate / fftSize;
    if (f < freqs[0] || f > freqs[n - 1]) continue;
    while (j < n - 2 && freqs[j + 1] < f) j++;
    const a = Math.log(freqs[j]), b = Math.log(freqs[j + 1]);
    const t = b > a ? (Math.log(f) - a) / (b - a) : 0;
    // A bin on a point takes that point alone, whatever its neighbour.
    const v = t <= 0 ? db[j] : t >= 1 ? db[j + 1] : db[j] + t * (db[j + 1] - db[j]);
    if (Number.isFinite(v)) out[k] = v;
  }
  return out;
}

/** x of frequency f on a log axis [lo, hi] spanning [x0, x0 + w]. */
export function logX(f, lo, hi, x0, w) {
  return x0 + w * (Math.log(f / lo) / Math.log(hi / lo));
}

/** y of value v on a linear axis [lo, hi] spanning [y0 + h, y0] (clamped). */
export function linY(v, lo, hi, y0, h) {
  const c = Math.min(hi, Math.max(lo, v));
  return y0 + h - h * (c - lo) / (hi - lo);
}

/**
 * The AC8a trace's colour class per point: "ok" (inside the checked band
 * and within the limit, green), "over" (inside, above the limit) or
 * "unchecked" (outside the band the verdict uses, AE 6d63a2e3).
 */
export function repeatabilityClasses(freqs, diffDb, band, limitDb) {
  return Array.from(freqs, (f, i) => {
    if (f < band[0] || f > band[1]) return "unchecked";
    return Math.abs(diffDb[i]) <= limitDb ? "ok" : "over";
  });
}

/**
 * Min/max of the IR per column over the window [t0, t1] (s); ir[0] is at
 * startS. Columns with no sample are NaN.
 */
export function irEnvelope(ir, startS, sampleRate, t0, t1, columns) {
  const min = new Float32Array(columns).fill(NaN);
  const max = new Float32Array(columns).fill(NaN);
  const i0 = Math.max(0, Math.ceil((t0 - startS) * sampleRate));
  const i1 = Math.min(ir.length - 1, Math.floor((t1 - startS) * sampleRate));
  for (let i = i0; i <= i1; i++) {
    const t = startS + i / sampleRate;
    const c = Math.min(columns - 1, Math.floor((t - t0) / (t1 - t0) * columns));
    const v = ir[i];
    if (Number.isNaN(min[c]) || v < min[c]) min[c] = v;
    if (Number.isNaN(max[c]) || v > max[c]) max[c] = v;
  }
  return { min, max };
}

/** Peak magnitude of the IR inside the window, for its y scale. */
export function irPeak(env) {
  let p = 0;
  for (let c = 0; c < env.min.length; c++) {
    if (Number.isFinite(env.min[c])) p = Math.max(p, -env.min[c], env.max[c]);
  }
  return p;
}

// -- drawing (2D context) ---------------------------------------------------

export const PAD = Object.freeze({ left: 36, right: 8, top: 6, bottom: 16 });

/** Background and plot box; the caption is the page's, not the canvas's. */
function frame(ctx, w, h, colors) {
  ctx.fillStyle = colors.bg;
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = colors.grid;
  ctx.lineWidth = 1;
  ctx.strokeRect(PAD.left, PAD.top, w - PAD.left - PAD.right,
    h - PAD.top - PAD.bottom);
  return { x0: PAD.left, y0: PAD.top, pw: w - PAD.left - PAD.right,
    ph: h - PAD.top - PAD.bottom };
}

/** The log axis of a curve: its first to its last frequency. */
function freqAxis(box, freqs) {
  return { ...box, fLo: freqs[0], fHi: freqs[freqs.length - 1] };
}

function fx(box, f) {
  return logX(f, box.fLo, box.fHi, box.x0, box.pw);
}

function freqTicks(ctx, box, colors) {
  ctx.fillStyle = colors.label;
  ctx.font = "9px monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (const [f, t] of FREQ_TICKS) {
    if (f >= box.fLo && f <= box.fHi) ctx.fillText(t, fx(box, f), box.y0 + box.ph + 2);
  }
}

function dbTicks(ctx, box, lo, hi, step, colors) {
  ctx.fillStyle = colors.label;
  ctx.font = "9px monospace";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) {
    const y = linY(v, lo, hi, box.y0, box.ph);
    ctx.fillText(String(v), box.x0 - 3, y);
    ctx.strokeStyle = colors.grid;
    ctx.beginPath();
    ctx.moveTo(box.x0, y);
    ctx.lineTo(box.x0 + box.pw, y);
    ctx.stroke();
  }
}

function freqLine(ctx, box, freqs, db, lo, hi, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  let pen = false;
  for (let i = 0; i < freqs.length; i++) {
    if (!Number.isFinite(db[i])) { pen = false; continue; }
    const x = fx(box, freqs[i]);
    const y = linY(db[i], lo, hi, box.y0, box.ph);
    if (pen) ctx.lineTo(x, y); else ctx.moveTo(x, y);
    pen = true;
  }
  ctx.stroke();
}

/** The impulse response: min/max envelope per pixel column. */
export function drawImpulse(ctx, w, h, plot, colors) {
  const box = frame(ctx, w, h, colors);
  const [t0, t1] = IR_WINDOW_S;
  const env = irEnvelope(plot.ir, plot.startS, plot.sampleRate, t0, t1,
    Math.max(1, Math.floor(box.pw)));
  const peak = irPeak(env) || 1;
  ctx.strokeStyle = colors.line;
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let c = 0; c < env.min.length; c++) {
    if (!Number.isFinite(env.min[c])) continue;
    ctx.moveTo(box.x0 + c + 0.5, linY(env.max[c], -peak, peak, box.y0, box.ph));
    ctx.lineTo(box.x0 + c + 0.5, linY(env.min[c], -peak, peak, box.y0, box.ph) + 0.5);
  }
  ctx.stroke();
  ctx.fillStyle = colors.label;
  ctx.font = "9px monospace";
  ctx.textBaseline = "top";
  for (const ms of [0, 100, 200, 300]) {
    const x = box.x0 + box.pw * (ms / 1000 - t0) / (t1 - t0);
    // The last label ends at the box edge instead of running off the canvas.
    ctx.textAlign = ms === 300 ? "right" : "center";
    ctx.fillText(ms + " ms", x, box.y0 + box.ph + 2);
  }
}

/** The AC8a trace, coloured per point by repeatabilityClasses, and the limit. */
export function drawRepeatability(ctx, w, h, plot, colors) {
  const box = freqAxis(frame(ctx, w, h, colors), plot.freqs);
  const lo = -3 * plot.limitDb, hi = 3 * plot.limitDb;
  dbTicks(ctx, box, lo, hi, plot.limitDb, colors);
  freqTicks(ctx, box, colors);
  // The limit as dashed lines over the checked band, so "over" shows
  // without the colours (UX 866c44ff).
  const xa = fx(box, Math.max(plot.band[0], box.fLo));
  const xb = fx(box, Math.min(plot.band[1], box.fHi));
  ctx.strokeStyle = colors.line;
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 3]);
  for (const v of [plot.limitDb, -plot.limitDb]) {
    const y = Math.round(linY(v, lo, hi, box.y0, box.ph)) + 0.5;
    ctx.beginPath();
    ctx.moveTo(xa, y);
    ctx.lineTo(xb, y);
    ctx.stroke();
  }
  ctx.setLineDash([]);
  const cls = repeatabilityClasses(plot.freqs, plot.diffDb, plot.band,
    plot.limitDb);
  ctx.lineWidth = 1.5;
  for (let i = 1; i < plot.freqs.length; i++) {
    const a = plot.diffDb[i - 1], b = plot.diffDb[i];
    if (!Number.isFinite(a) || !Number.isFinite(b)) continue;
    ctx.strokeStyle = colors[cls[i]];
    ctx.beginPath();
    ctx.moveTo(fx(box, plot.freqs[i - 1]), linY(a, lo, hi, box.y0, box.ph));
    ctx.lineTo(fx(box, plot.freqs[i]), linY(b, lo, hi, box.y0, box.ph));
    ctx.stroke();
  }
}

/** The AC8c curves: measured, predicted and the target, with a legend. */
export function drawPrediction(ctx, w, h, plot, colors) {
  const box = freqAxis(frame(ctx, w, h, colors), plot.freqs);
  const lo = -18, hi = 18;
  dbTicks(ctx, box, lo, hi, 6, colors);
  freqTicks(ctx, box, colors);
  const curves = [
    [plot.targetDb, colors.target, plot.legend.target],
    [plot.measuredDb, colors.measured, plot.legend.measured],
    [plot.predictedDb, colors.predicted, plot.legend.predicted],
  ];
  ctx.font = "9px monospace";
  ctx.textAlign = "right";
  ctx.textBaseline = "top";
  curves.forEach(([db, color, label], k) => {
    freqLine(ctx, box, plot.freqs, db, lo, hi, color);
    ctx.fillStyle = color;
    ctx.fillText(label, box.x0 + box.pw - 4, box.y0 + 4 + 11 * k);
  });
}
