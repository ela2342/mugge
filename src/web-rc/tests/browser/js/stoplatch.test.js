// Meter-to-output auto-STOP on the render thread (stop-latch.js; US-179
// E3/E4, Architect note b): the output stops without the main thread.

import { assert, eq } from "./assert.js";
import { StopLatch } from "../../../static/js/stop-latch.js";
import { STOP } from "../../../static/js/safety.js";

const SR = 48000;
const Q = 128;
const RAMP = 480; // 10 ms
const METER = new URL("../../../static/js/meter-worklet.js", import.meta.url);
const OUTPUT = new URL("../../../static/js/output-worklet.js", import.meta.url);

// -- the latch ---------------------------------------------------------------

export async function test_latch_unarmed_never_trips() {
  const l = new StopLatch();
  l.trip(STOP.MIC_CLIP);
  eq(l.tripped(0), false);
  const e = l.arm();
  eq(l.tripped(e), false, "a trip before arming does not stop a new output");
}

export async function test_latch_trip_stops_armed_output() {
  const l = new StopLatch();
  const e = l.arm();
  eq(l.tripped(e), false);
  l.trip(STOP.MIC_CLIP);
  eq(l.tripped(e), true);
  eq(l.cause, STOP.MIC_CLIP);
  l.trip(STOP.SPL);
  eq(l.cause, STOP.MIC_CLIP, "the first cause is kept");
}

export async function test_latch_trip_stops_older_outputs_too() {
  const l = new StopLatch();
  const old = l.arm();
  const cur = l.arm();
  l.trip(STOP.MIC_CLIP);
  eq(l.tripped(old), true);
  eq(l.tripped(cur), true);
}

export async function test_latch_rearm_clears() {
  const l = new StopLatch();
  l.arm();
  l.trip(STOP.MIC_CLIP);
  const e = l.arm();
  eq(l.tripped(e), false);
  eq(l.cause, null);
}

// -- both worklets, offline, no main-thread action ------------------------------

/**
 * Output: a constant 0.5 buffer at gain 0.1 on channel 0. Mic: silence, then
 * full scale from sample clipAt (or never). The main thread does nothing
 * while rendering. extraOutputAt: start a second output at that time.
 */
async function runBoth({ frames, clipAt, clipEnd, extraOutputAt }) {
  const ctx = new OfflineAudioContext(2, frames, SR);
  ctx.destination.channelInterpretation = "discrete";
  await ctx.audioWorklet.addModule(METER);
  await ctx.audioWorklet.addModule(OUTPUT);
  const mic = new Float32Array(frames);
  if (clipAt !== null) mic.fill(1, clipAt, clipEnd ?? frames);
  const micBuf = ctx.createBuffer(1, frames, SR);
  micBuf.copyToChannel(mic, 0);
  const src = new AudioBufferSourceNode(ctx, { buffer: micBuf });
  const meter = new AudioWorkletNode(ctx, "webrc-mic-meter", {
    numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
    channelCountMode: "explicit", channelInterpretation: "discrete",
    processorOptions: { splOffsetDb: null },
  });
  src.connect(meter);
  src.start();
  const msgs = [];
  const makeOutput = (channel) => {
    const node = new AudioWorkletNode(ctx, "webrc-output", {
      numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [2],
      channelInterpretation: "discrete",
      processorOptions: {
        channel, gain: 0.1,
        source: { kind: "buffer", samples: new Float32Array(frames).fill(0.5) },
      },
    });
    node.port.onmessage = (e) => msgs.push({ channel, ...e.data });
    node.connect(ctx.destination);
  };
  makeOutput(0);
  if (extraOutputAt !== undefined) {
    ctx.suspend(extraOutputAt).then(() => { makeOutput(1); ctx.resume(); });
  }
  const buf = await ctx.startRendering();
  let n = -1;
  while (n !== msgs.length) {
    n = msgs.length;
    await new Promise((r) => setTimeout(r, 50));
  }
  return { out: [buf.getChannelData(0), buf.getChannelData(1)], msgs };
}

export async function test_mic_clip_stops_output_without_main_thread() {
  const clipAt = 4000; // inside quantum 31
  const { out, msgs } = await runBoth({ frames: 12000, clipAt });
  const o = out[0];
  // Playing at full gain before the clip.
  for (let i = RAMP; i < Math.floor(clipAt / Q) * Q; i++) {
    eq(o[i], Math.fround(0.5 * 0.1), "before the clip " + i);
  }
  // The ramp starts by the next quantum at the latest: silent from the end of
  // the clip's quantum + one quantum + the ramp on.
  const silentFrom = (Math.floor(clipAt / Q) + 2) * Q + RAMP;
  for (let i = silentFrom; i < o.length; i++) eq(o[i], 0, "after the stop " + i);
  // A ramp, never a jump (4e).
  let jump = 0;
  for (let i = 1; i < o.length; i++) jump = Math.max(jump, Math.abs(o[i] - o[i - 1]));
  assert(jump <= 0.05 / RAMP + 1e-6, "ramped stop, max step " + jump);
  const stopped = msgs.find((m) => m.type === "stopped");
  assert(stopped, "the output reports the stop");
  eq(stopped.cause, STOP.MIC_CLIP);
}

export async function test_no_mic_stop_output_plays_on() {
  const { out, msgs } = await runBoth({ frames: 12000, clipAt: null });
  for (let i = RAMP; i < 12000; i++) eq(out[0][i], Math.fround(0.05), "sample " + i);
  eq(msgs.filter((m) => m.type === "stopped").length, 0);
}

export async function test_output_started_after_a_trip_plays() {
  // A short clip burst trips the latch; the output started later arms a new
  // epoch and plays.
  const startAt = 8192;
  const { out } = await runBoth({
    frames: 16384, clipAt: 2000, clipEnd: 2256, extraOutputAt: startAt / SR,
  });
  for (let i = (Math.floor(2000 / Q) + 2) * Q + RAMP; i < out[0].length; i++) {
    eq(out[0][i], 0, "first output stopped " + i);
  }
  for (let i = startAt + Q + RAMP; i < out[1].length; i++) {
    eq(out[1][i], Math.fround(0.05), "second output plays " + i);
  }
}

export async function test_held_clip_stops_a_later_output() {
  // The mic stays clipped: the meter reports the cause every quantum, so the
  // new epoch trips as well.
  const startAt = 8192;
  const { out } = await runBoth({ frames: 16384, clipAt: 2000, extraOutputAt: startAt / SR });
  for (let i = startAt + 2 * Q + RAMP; i < out[1].length; i++) eq(out[1][i], 0, "stopped " + i);
}
