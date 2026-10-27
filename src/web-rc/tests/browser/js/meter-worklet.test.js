// The real meter-worklet.js process(), driven quantum by quantum with chosen
// currentFrame values (Architect 3fb4cd0c B3). The worklet's globals
// (AudioWorkletProcessor, registerProcessor, sampleRate, currentFrame) are
// stand-ins in this page; it shares this page's stop-latch.js instance.

import { assert, eq } from "./assert.js";
import { LATCH, OutputGate, stopLatch } from "../../../static/js/stop-latch.js";

const Q = 128;
const QUIET = new Float32Array(Q);
let Processor = null;

/** The worklet's processor class, loaded once into this page. */
async function meterClass() {
  if (Processor) return Processor;
  globalThis.sampleRate = 48000;
  globalThis.currentFrame = 0;
  globalThis.AudioWorkletProcessor = class {
    constructor() {
      this.posted = [];
      this.port = { postMessage: (m) => this.posted.push(m), onmessage: null };
    }
  };
  globalThis.registerProcessor = (name, cls) => {
    if (name === "webrc-mic-meter") Processor = cls;
  };
  await import("../../../static/js/meter-worklet.js");
  assert(Processor, "registered");
  return Processor;
}

/**
 * A new meter. This page has one stop latch for all its meters, while a real
 * context has one meter per latch: go on from the page's last beat, so a
 * new meter's count does not read as a decreasing beat.
 */
async function newMeter() {
  const P = await meterClass();
  const m = new P({ processorOptions: { splOffsetDb: null } });
  m.beats = stopLatch.beatCount ?? 0;
  return m;
}

/** A fresh meter, `n` clean quanta in, ending before frame `next`. */
async function meterAt(next, n = 30) {
  const m = await newMeter();
  for (let i = n; i > 0; i--) quantum(m, next - i * Q);
  return m;
}

/** Record over the given quanta (one process() call per frame). */
function record(m, quanta, lookback) {
  m.port.onmessage({ data: { type: "record", id: 9, frames: quanta.length * Q,
    lookback } });
  for (const f of quanta) quantum(m, f);
  const done = m.posted.filter((x) => x.type === "recorded");
  eq(done.length, 1, "one recording");
  return done[0];
}

/** Quanta from `from`, +128 each, `n` of them. */
const run = (from, n) => Array.from({ length: n }, (_, i) => from + i * Q);

/** One process() call at `frame`. */
function quantum(meter, frame, block = QUIET) {
  globalThis.currentFrame = frame;
  return meter.process([[block]]);
}

/**
 * The evidence (w6 7edf78aa): Chromium rendered two quanta stamped 627584
 * and never 627712. The beats stay +1 and an armed gate plays on.
 */
export async function test_repeated_and_skipped_frame_keep_the_heartbeat() {
  const m = await newMeter();
  quantum(m, 627328);
  const gate = new OutputGate(stopLatch);
  const beats = [];
  for (const f of [627456, 627584, 627584, 627840, 627968]) {
    quantum(m, f);
    beats.push(stopLatch.beatCount);
    const g = gate.check();
    eq(g.stop, false, "no stop at " + f);
    eq(g.play, true, "plays at " + f);
  }
  eq(stopLatch.beatFault, false);
  for (let i = 1; i < beats.length; i++) eq(beats[i] - beats[i - 1], 1, "+1 at " + i);
  eq(gate.cause, null);

  // The count is still a heartbeat: no process() calls -> stale -> stop.
  let r;
  for (let i = 0; i < LATCH.STALE_QUANTA; i++) r = gate.check();
  eq(r.stop, true);
  eq(gate.cause, LATCH.HEARTBEAT);
}

/**
 * AE 42dada94 G1/G4: a step other than +128 from `lookback` frames before
 * the capture's start to its last sample flags the capture; clean +128
 * quanta, or a glitch older than the lookback, do not.
 */
export async function test_clock_glitch_flags_the_capture() {
  const S = 627456;
  // Clean.
  let m = await meterAt(S);
  let q = run(S, 4);
  eq(record(m, q, 2400).clockGlitch, null, "clean +128");
  // The evidence sequence inside the capture: the latest glitch is named.
  m = await meterAt(S);
  q = [627456, 627584, 627584, 627840];
  const r = record(m, q, 2400);
  eq(JSON.stringify(r.clockGlitch), JSON.stringify({ before: 627584, after: 627840 }));
  eq(r.startFrame, 627456);
  eq(r.samples.length, 4 * Q, "the samples are still delivered");
  // A repeated frame alone.
  m = await meterAt(S);
  q = [S, S + Q, S + Q, S + 2 * Q];
  eq(JSON.stringify(record(m, q, 2400).clockGlitch),
    JSON.stringify({ before: S + Q, after: S + Q }), "repeat");
  // A skip on the capture's last quantum.
  m = await meterAt(S);
  q = [S, S + Q, S + 2 * Q, S + 4 * Q];
  eq(JSON.stringify(record(m, q, 2400).clockGlitch),
    JSON.stringify({ before: S + 2 * Q, after: S + 4 * Q }), "last quantum");
}

/** The lookback edge: 2 quanta back is in, 3 back is out. */
export async function test_clock_glitch_lookback_window() {
  const S = 627456;
  for (const [back, flagged] of [[1, true], [2, true], [3, false]]) {
    // The step into the quantum `back` quanta before the start is bad.
    const m = await newMeter();
    for (let i = 10; i > back; i--) quantum(m, S - i * Q - 1);
    for (let i = back; i > 0; i--) quantum(m, S - i * Q);
    const q = run(S, 2);
    const r = record(m, q, 2 * Q);
    eq(r.clockGlitch !== null, flagged, back + " quanta back");
  }
  // A bad lookback covers the whole context life (fails closed).
  for (const lookback of [undefined, -1, 2.5, NaN, "2400"]) {
    const m = await newMeter();
    quantum(m, 0);
    quantum(m, 7);                       // a glitch long ago
    for (let f = 7 + Q; f < S; f += Q) quantum(m, f);
    const q = run(Math.ceil(S / Q) * Q + 7, 2);
    assert(record(m, q, lookback).clockGlitch !== null, "lookback " + lookback);
  }
}
