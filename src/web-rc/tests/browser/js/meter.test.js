// Mic meter (meter-core.js, meter-worklet.js): US-179 AC4b, E1 v2, E3c.
//
// The E3c trigger cases run on the real AudioWorklet in an
// OfflineAudioContext with synthetic input.

import { assert, close, eq } from "./assert.js";
import { METER, MeterStream, MicMeter, Recorder } from "../../../static/js/meter-core.js";
import { STOP } from "../../../static/js/safety.js";

const SR = 48000;
const Q = 128;
const WIN = SR * METER.RMS_WINDOW_MS / 1000; // 4800
// Example calibration: 0 dBFS = 120 dB SPL (90 dB SPL = -30 dBFS,
// 105 dB SPL = -15 dBFS).
const CAL = 120;
const WORKLET = new URL("../../../static/js/meter-worklet.js", import.meta.url);

function quanta(signal, fn) {
  const out = [];
  for (let i = 0; i < signal.length; i += Q) out.push(fn(signal.subarray(i, i + Q)));
  return out;
}

const db = (x) => 20 * Math.log10(x);

export async function test_peak_sees_every_sample() {
  // One sample anywhere in the quantum sets that quantum's peak.
  for (const at of [0, 1, 63, 127]) {
    const m = new MicMeter(SR);
    const block = new Float32Array(Q);
    block[at] = -0.5;
    close(m.process(block).peakDbfs, db(0.5), 1e-12, "sample " + at);
    eq(m.process(new Float32Array(Q)).peakDbfs, -Infinity, "next quantum");
  }
  const m = new MicMeter(SR);
  const block = new Float32Array(Q);
  block[5] = NaN;
  eq(m.process(block).peakDbfs, Infinity, "NaN counts as clip");
}

export async function test_rms_is_contiguous_100ms() {
  eq(WIN, 4800);
  // 4800 samples at 0.25 then silence: the window ending at the last loud
  // sample is exactly 0.25 RMS, and it drops to silence 100 ms later.
  const sig = new Float32Array(Q * 120); // 120 whole quanta
  // Starts mid-quantum and ends on a quantum boundary (1344 + 4800 = 48 Q).
  sig.fill(0.25, Q * 10 + 64, Q * 10 + 64 + WIN);
  const m = new MicMeter(SR);
  const r = quanta(sig, (b) => m.process(b));
  // WIN is not a multiple of Q (4800 / 128 = 37.5): check by recomputation.
  const ref = [];
  for (let k = 0; k < r.length; k++) {
    const last = (k + 1) * Q;
    let s = 0;
    for (let i = Math.max(0, last - WIN); i < last; i++) s += sig[i] * sig[i];
    ref.push(db(Math.sqrt(s / Math.min(last, WIN))));
  }
  for (let k = 0; k < r.length; k++) {
    if (ref[k] === -Infinity) eq(r[k].rmsDbfs, -Infinity, "silent " + k);
    else close(r[k].rmsDbfs, ref[k], 1e-9, "quantum " + k);
  }
  close(r[47].rmsDbfs, db(0.25), 1e-9, "window = the burst");
  assert(r[46].rmsDbfs < db(0.25) && r[48].rmsDbfs < db(0.25), "neighbours");
}

export async function test_rms_does_not_drift() {
  // 60 s of a full-scale-ish sine then silence: the running sum is re-summed
  // exactly, so silence reads silence.
  const m = new MicMeter(SR);
  const b = new Float32Array(Q);
  for (let k = 0; k < (60 * SR) / Q; k++) {
    for (let i = 0; i < Q; i++) b[i] = 0.9 * Math.sin(2 * Math.PI * 997 * (k * Q + i) / SR);
    m.process(b);
  }
  const z = new Float32Array(Q);
  let r;
  for (let k = 0; k < 40; k++) r = m.process(z);
  eq(r.rmsDbfs, -Infinity, "silence after drift test");
}

export async function test_stream_batches_maxima_and_flushes_on_stop() {
  const s = new MeterStream(SR, null);
  const loud = new Float32Array(Q);
  loud[3] = 0.5;
  const quiet = new Float32Array(Q);
  eq(s.process(loud), null);
  eq(s.process(quiet), null);
  eq(s.process(quiet), null);
  const r = s.process(quiet);
  eq(r.quanta, METER.REPORT_QUANTA);
  close(r.peakDbfs, db(0.5), 1e-12, "peak survives batching");
  eq(r.cause, null);
  const clip = new Float32Array(Q);
  clip[100] = 0.95;
  const c = s.process(clip);
  assert(c !== null, "stop reported at once");
  eq(c.quanta, 1);
  eq(c.cause, STOP.MIC_CLIP);
}

// -- the worklet, offline ----------------------------------------------------

async function runWorklet(signal, splOffsetDb) {
  const ctx = new OfflineAudioContext(1, signal.length, SR);
  await ctx.audioWorklet.addModule(WORKLET);
  const buf = ctx.createBuffer(1, signal.length, SR);
  buf.copyToChannel(signal, 0);
  const src = new AudioBufferSourceNode(ctx, { buffer: buf });
  const node = new AudioWorkletNode(ctx, "webrc-mic-meter", {
    numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
    channelCountMode: "explicit", channelInterpretation: "discrete",
    processorOptions: { splOffsetDb },
  });
  const reports = [];
  node.port.onmessage = (e) => reports.push(e.data);
  src.connect(node);
  src.start();
  await ctx.startRendering();
  // Let queued port messages arrive.
  let n = -1;
  while (n !== reports.length) {
    n = reports.length;
    await new Promise((r) => setTimeout(r, 50));
  }
  const total = reports.reduce((a, r) => a + r.quanta, 0);
  assert(total >= Math.floor(signal.length / Q) - METER.REPORT_QUANTA,
    "worklet metered the whole signal: " + total);
  return reports;
}

const causes = (reports) => reports.map((r) => r.cause).filter((c) => c);

function sine(len, amp, f = 1000) {
  const s = new Float32Array(len);
  for (let i = 0; i < len; i++) s[i] = amp * Math.sin(2 * Math.PI * f * i / SR);
  return s;
}

/** E3c: RMS below 90 dB while the peak crosses 90 dB = no stop. */
export async function test_worklet_peak_over_90_rms_under_90_no_stop() {
  const sig = sine(SR, Math.SQRT2 * 10 ** (-50 / 20)); // -50 dBFS RMS = 70 dB
  for (let i = 1000; i < sig.length; i += 2400) sig[i] = 0.1; // 100 dB SPL peak
  const rep = await runWorklet(sig, CAL);
  eq(causes(rep).length, 0, "no stop: " + causes(rep));
  assert(Math.max(...rep.map((r) => r.peakDbfs)) + CAL > 90, "peak crossed 90");
  assert(Math.max(...rep.map((r) => r.rmsDbfs)) + CAL < 90, "RMS stayed under");
}

/** E3c: RMS crossing 90 dB = stop. */
export async function test_worklet_rms_over_90_stops() {
  const half = SR / 2;
  const sig = new Float32Array(SR);
  sig.set(sine(half, Math.SQRT2 * 10 ** (-40 / 20)), 0);       // 80 dB SPL
  sig.set(sine(half, Math.SQRT2 * 10 ** (-29 / 20)), half);    // 91 dB SPL
  const rep = await runWorklet(sig, CAL);
  const stops = rep.filter((r) => r.cause);
  assert(stops.length > 0, "stopped");
  eq(stops[0].cause, STOP.MIC_SPL);
  assert(stops[0].frame > half, "not before the level rose");
  assert(stops[0].frame < half + WIN, "within one RMS window: " + stops[0].frame);
  // Uncalibrated, the same signal does not stop (AE A1).
  eq(causes(await runWorklet(sig, null)).length, 0, "uncalibrated");
}

/** E3c: a single click above 105 dB SPL peak = stop. */
export async function test_worklet_single_click_over_105_stops() {
  const sig = new Float32Array(SR / 2);
  sig[12345] = 10 ** (-14.9 / 20); // 105.1 dB SPL, one sample
  const rep = await runWorklet(sig, CAL);
  eq(causes(rep)[0], STOP.MIC_SPL_PEAK);
  const quiet = new Float32Array(SR / 2);
  quiet[12345] = 10 ** (-15.1 / 20); // 104.9 dB SPL
  eq(causes(await runWorklet(quiet, CAL)).length, 0, "under 105");
}

/** E3c: peak >= -1 dBFS = stop, with and without calibration. */
export async function test_worklet_clip_stops() {
  const sig = new Float32Array(SR / 2);
  sig[7777] = 10 ** (-0.99 / 20);
  for (const off of [null, CAL]) {
    eq(causes(await runWorklet(sig, off))[0], STOP.MIC_CLIP, "cal " + off);
  }
  const under = new Float32Array(SR / 2);
  under[7777] = 10 ** (-1.01 / 20);
  eq(causes(await runWorklet(under, null)).length, 0, "under -1 dBFS");
}

// -- capture recording (AC2d, AC7) -------------------------------------------

export async function test_recorder_takes_exact_frames_across_blocks() {
  const sig = new Float32Array(1000).map((_, i) => i);
  const rec = new Recorder(300);
  let out = null;
  let pushes = 0;
  for (let i = 0; i < sig.length && !out; i += Q) {
    out = rec.push(sig.subarray(i, i + Q));
    pushes++;
  }
  eq(pushes, 3, "done in the third block");
  eq(out.length, 300);
  for (let i = 0; i < 300; i++) eq(out[i], i, "sample " + i);
  assert(rec.done);
  eq(rec.push(sig.subarray(0, Q)), null, "nothing after done");
}

export async function test_recorder_rejects_bad_frames() {
  for (const f of [0, -1, 1.5, NaN, "10"]) {
    let threw = false;
    try { new Recorder(f); } catch (e) { threw = e instanceof RangeError; }
    assert(threw, "rejects " + f);
  }
}

/** The worklet records contiguous samples from the meter's own input. */
export async function test_worklet_records_bit_exact() {
  const len = SR;
  const sig = new Float32Array(len);
  let x = 12345;
  for (let i = 0; i < len; i++) {
    x = (x * 1103515245 + 12345) >>> 0;
    sig[i] = (x / 2 ** 32 - 0.5) * 0.01;
  }
  const ctx = new OfflineAudioContext(1, len, SR);
  await ctx.audioWorklet.addModule(WORKLET);
  const buf = ctx.createBuffer(1, len, SR);
  buf.copyToChannel(sig, 0);
  const src = new AudioBufferSourceNode(ctx, { buffer: buf });
  const node = new AudioWorkletNode(ctx, "webrc-mic-meter", {
    numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
    channelCountMode: "explicit", channelInterpretation: "discrete",
    processorOptions: { splOffsetDb: null },
  });
  const got = [];
  node.port.onmessage = (e) => { if (e.data.type === "recorded") got.push(e.data); };
  src.connect(node);
  src.start();
  const frames = 20000;
  // Ask at a known point: suspend, post, give the port time, resume.
  ctx.suspend(0.25).then(async () => {
    node.port.postMessage({ type: "record", id: 7, frames });
    await new Promise((r) => setTimeout(r, 100));
    ctx.resume();
  });
  await ctx.startRendering();
  for (let i = 0; i < 20 && !got.length; i++) {
    await new Promise((r) => setTimeout(r, 50));
  }
  eq(got.length, 1, "one recording");
  const r = got[0];
  eq(r.id, 7);
  eq(r.samples.length, frames);
  eq(r.startFrame % Q, 0, "starts on a quantum");
  assert(r.startFrame + frames <= len, "inside the signal");
  for (let i = 0; i < frames; i++) {
    if (r.samples[i] !== sig[r.startFrame + i]) {
      throw new Error("sample " + i + " differs");
    }
  }
}
