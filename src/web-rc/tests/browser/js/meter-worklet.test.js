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
  const P = await meterClass();
  const m = new P({ processorOptions: { splOffsetDb: null } });
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
