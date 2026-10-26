// Meter-to-output auto-STOP on the render thread (stop-latch.js; US-179
// E3/E4, Architect note b): the output stops without the main thread.
// Latch ruling r2 9a6db097 (AE release 6f220842): epochs A1-A5, the stop
// ramp B1-B3, tests C1-C5 (C1b: audio-io.test.js, C6: flow.test.js).

import { assert, eq } from "./assert.js";
import { addBeater } from "./beater.js";
import { LATCH, OutputGate, StopLatch } from "../../../static/js/stop-latch.js";
import { BufferSource, OutputChain, renderPlayed } from "../../../static/js/output-core.js";
import { STOP } from "../../../static/js/safety.js";

const SR = 48000;
const Q = 128;
const RAMP = 480; // 10 ms
const LEVEL = Math.fround(0.5 * 0.1);
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
  l.trip(STOP.MIC_SPL);
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

/** C3: a new epoch never un-trips an old one. */
export async function test_latch_rearm_clears_only_the_new_epoch() {
  const l = new StopLatch();
  const old = l.arm();
  l.trip(STOP.MIC_CLIP);
  const e = l.arm();
  eq(l.tripped(e), false);
  eq(l.cause, null);
  eq(l.tripped(old), true, "the old epoch stays tripped");
}

/** A1: an output older than the current epoch must stop, trip or not. */
export async function test_latch_older_epoch_is_stopped() {
  const l = new StopLatch();
  const old = l.arm();
  eq(l.tripped(old), false);
  const cur = l.arm();
  eq(l.tripped(old), true);
  eq(l.tripped(cur), false);
}

/** A4: a beat that is not finite or not strictly increasing is a fault. */
export async function test_latch_bad_beats_fault() {
  const good = new StopLatch();
  for (const f of [0, 128, 256, 100000]) good.beat(f);
  eq(good.beatFault, false);
  eq(good.beatFrame, 100000);
  for (const [bad, why] of [[NaN, "NaN"], [Infinity, "infinite"], [256, "repeated"],
    [255, "decreasing"], [undefined, "unwritten"]]) {
    const l = new StopLatch();
    l.beat(128);
    l.beat(256);
    l.beat(bad);
    eq(l.beatFault, true, why);
    eq(l.beatFrame, 256, why + ": not stored");
    l.beat(384);
    eq(l.beatFault, true, why + ": the fault holds");
  }
}

// -- the gate, one check per quantum -----------------------------------------

/** Checks the gate n times; one beat per check if `beat` is set. */
function checks(gate, n, beat) {
  const r = [];
  for (let i = 0; i < n; i++) {
    if (beat) gate.latch.beat(beat());
    r.push(gate.check());
  }
  return r;
}

function counter(start = 0) {
  let f = start - Q;
  return () => (f += Q);
}

/** C5: no beat after construction -> zeros; four quiet quanta -> stop. */
export async function test_gate_waits_for_a_fresh_beat() {
  const l = new StopLatch();
  l.beat(1000);                       // before the node: does not count
  const g = new OutputGate(l);
  const r = checks(g, LATCH.STALE_QUANTA, null);
  for (let i = 0; i < LATCH.STALE_QUANTA - 1; i++) {
    eq(r[i].stop, false, "quiet " + i);
    eq(r[i].play, false, "zeros until a fresh beat " + i);
  }
  eq(r[LATCH.STALE_QUANTA - 1].stop, true, "stale after 4 quanta");
  eq(g.cause, LATCH.HEARTBEAT);

  const h = new OutputGate(l);
  l.beat(1128);
  const first = h.check();
  eq(first.stop, false);
  eq(first.play, true, "plays from the first fresh beat");
}

export async function test_gate_never_written_latches() {
  const g = new OutputGate(new StopLatch());
  const r = checks(g, LATCH.STALE_QUANTA, null);
  assert(r.slice(0, -1).every((x) => !x.stop && !x.play));
  eq(r[r.length - 1].stop, true);
  eq(g.cause, LATCH.HEARTBEAT);
}

export async function test_gate_beats_keep_it_playing_and_stale_stops() {
  const l = new StopLatch();
  const g = new OutputGate(l);
  const beat = counter();
  const r = checks(g, 1000, beat);
  assert(r.every((x) => !x.stop && x.play), "1000 quanta with beats");
  // One or two missed quanta (scheduling order) are not stale; four are.
  const quiet = checks(g, LATCH.STALE_QUANTA, null);
  assert(quiet.slice(0, -1).every((x) => !x.stop && x.play), "3 quiet quanta");
  eq(quiet[quiet.length - 1].stop, true, "the 4th quiet quantum stops");
  eq(g.cause, LATCH.HEARTBEAT);
}

export async function test_gate_bad_beat_stops_at_once() {
  for (const bad of [NaN, "repeat", "decrease", "reader"]) {
    const l = new StopLatch();
    const g = new OutputGate(l);
    checks(g, 3, counter());
    const last = l.beatFrame;
    if (bad === "repeat") l.beat(last);
    else if (bad === "decrease") l.beat(last - 1);
    else if (bad === "reader") l.beatFrame = last - Q; // written past beat()
    else l.beat(bad);
    const r = g.check();
    eq(r.stop, true, String(bad));
    eq(g.cause, LATCH.HEARTBEAT, String(bad));
    // A5: the fault stays for the scope; a new node there stops too.
    if (bad !== "reader") eq(new OutputGate(l).check().stop, true, bad + ": new node");
  }
}

/** A4: the meter's stop conditions act on the first fresh beat. */
export async function test_gate_trip_wins_on_the_first_beat() {
  const l = new StopLatch();
  const g = new OutputGate(l);
  l.trip(STOP.MIC_CLIP);
  l.beat(0);
  const r = g.check();
  eq(r.stop, true);
  eq(g.cause, STOP.MIC_CLIP);
}

/** A1, B3, C3: a stop is final; a newer node supersedes an older one. */
export async function test_gate_stop_is_final_and_newer_supersedes() {
  const l = new StopLatch();
  const beat = counter();
  const g1 = new OutputGate(l);
  checks(g1, 3, beat);
  const g2 = new OutputGate(l);
  l.beat(beat());
  eq(g1.check().stop, true);
  eq(g1.cause, LATCH.SUPERSEDED);
  const r2 = g2.check();
  eq(r2.stop, false);
  eq(r2.play, true);
  l.trip(STOP.MIC_CLIP);
  l.beat(beat());
  eq(g2.check().stop, true);
  eq(g2.cause, STOP.MIC_CLIP);
  const g3 = new OutputGate(l);
  l.beat(beat());
  eq(g3.check().stop, false, "the new epoch is clear");
  for (const g of [g1, g2]) {
    const again = checks(g, 10, beat);
    assert(again.every((x) => !x.stop && x.play), "no second stop event");
  }
  eq(g1.cause, LATCH.SUPERSEDED, "C3: old causes stay");
  eq(g2.cause, STOP.MIC_CLIP);
}

// -- B3: nothing reverses the stop ramp ---------------------------------------

/** C1: a second stop or a "+" step during the ramp changes nothing. */
export async function test_stop_ramp_ignores_second_trigger_and_steps() {
  const make = () => new OutputChain({
    sampleRate: SR, source: new BufferSource(new Float32Array(SR).fill(0.5)), gain: 0.1,
  });
  const a = make();
  const b = make();
  const pre = new Float32Array(4 * Q);
  a.render(pre);
  b.render(pre.slice());
  a.stop();
  b.stop();
  const oa = new Float32Array(8 * Q);
  const ob = new Float32Array(8 * Q);
  a.render(oa.subarray(0, Q));
  b.render(ob.subarray(0, Q));
  b.stop();
  b.setGain(1);
  b.setGain(0.2);
  for (let i = Q; i < oa.length; i += Q) {
    a.render(oa.subarray(i, i + Q));
    b.render(ob.subarray(i, i + Q));
    if (i === 2 * Q) b.stop();
  }
  for (let i = 0; i < oa.length; i++) eq(ob[i], oa[i], "unchanged " + i);
  for (let i = 1; i < oa.length; i++) assert(oa[i] <= oa[i - 1], "monotonic " + i);
  for (let i = RAMP - 1; i < oa.length; i++) {
    assert(Object.is(oa[i], 0), "exactly 0 from the end of the ramp " + i);
  }
}

// -- the worklets, offline, no main-thread action ----------------------------

/**
 * Two output channels, each output a constant 0.5 buffer at gain 0.1.
 * meter: "none", "mic" (the real meter worklet on a mic buffer that is
 * silent, then full scale in [clipAt, clipEnd)), or fake-meter options.
 * extraOutputAt: build a second output on channel 1 at that time (s).
 */
async function render({ frames, meter = {}, clipAt = null, clipEnd, extraOutputAt }) {
  const ctx = new OfflineAudioContext(2, frames, SR);
  ctx.destination.channelInterpretation = "discrete";
  await ctx.audioWorklet.addModule(METER);
  await ctx.audioWorklet.addModule(OUTPUT);
  if (meter === "mic") {
    const mic = new Float32Array(frames);
    if (clipAt !== null) mic.fill(1, clipAt, clipEnd ?? frames);
    const micBuf = ctx.createBuffer(1, frames, SR);
    micBuf.copyToChannel(mic, 0);
    const src = new AudioBufferSourceNode(ctx, { buffer: micBuf });
    const node = new AudioWorkletNode(ctx, "webrc-mic-meter", {
      numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
      channelCountMode: "explicit", channelInterpretation: "discrete",
      processorOptions: { splOffsetDb: null },
    });
    src.connect(node);
    src.start();
  } else if (meter !== "none") {
    await addBeater(ctx, meter);
  }
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

/** The ramp-in of a new output, from 0 (4h), as the chain plays it. */
const RAMP_IN = renderPlayed(new Float32Array(4 * RAMP).fill(0.5), 0.1, SR).played;

/** First sample index of the quantum an output starts sounding in. */
function onsetOf(d, from = 0) {
  let i = from;
  while (i < d.length && d[i] === 0) i++;
  return i < d.length ? Math.floor(i / Q) * Q : -1;
}

/** C2: from `at`, the 4h ramp-in from 0, bit for bit. */
function assertRampIn(d, at, why) {
  for (let i = 0; i < 2 * RAMP; i++) eq(d[at + i], RAMP_IN[i], why + ": ramp-in " + i);
}

/**
 * C1 checks for a trip in the quantum that holds frame `at`: full level
 * before it, the ramp starts by the next quantum (B1), never rises, is
 * exactly 0 by one quantum plus 10 ms later (B2) and stays 0.
 */
function assertStopRamp(o, at, why) {
  const k = Math.floor(at / Q) * Q;
  for (let i = RAMP + Q; i < k; i++) eq(o[i], LEVEL, why + ": before the trip " + i);
  assert(o[k + Q] < LEVEL, why + ": falling by the next quantum");
  for (let i = k + 1; i < o.length; i++) assert(o[i] <= o[i - 1], why + ": monotonic " + i);
  for (let i = k + Q + RAMP; i < o.length; i++) {
    assert(Object.is(o[i], 0), why + ": exactly 0 from " + (k + Q + RAMP) + ", at " + i);
  }
}

/**
 * C1: a trip ramps every channel to exactly 0; the ramp needs no meter.
 * The meter and the output run in either order within a quantum, so the
 * ramp starts in the trip quantum or the next one (assertStopRamp).
 */
export async function test_c1_trip_ramps_to_exact_zero_without_the_meter() {
  const at = 4000;
  const k = Math.floor(at / Q) * Q; // the fake meter trips in this quantum
  for (const [name, meter] of [
    ["beats on", { trip: { at: k, cause: STOP.MIC_CLIP, until: k + 1 } }],
    ["meter gone", { trip: { at: k, cause: STOP.MIC_CLIP }, until: k + 1 }],
  ]) {
    const { out, msgs } = await render({ frames: 12000, meter });
    assertStopRamp(out[0], at, name);
    assert(out[1].every((v) => v === 0), name + ": other channel zero");
    const st = msgs.filter((m) => m.type === "stopped");
    eq(st.length, 1, name + ": one zero-reached report");
    eq(st[0].cause, STOP.MIC_CLIP, name);
    assert(st[0].frame <= Math.floor(at / Q) * Q + 2 * Q + RAMP, name + ": reported");
  }
}

export async function test_mic_clip_stops_output_without_main_thread() {
  const clipAt = 4000; // inside quantum 31
  const { out, msgs } = await render({ frames: 12000, meter: "mic", clipAt });
  assertStopRamp(out[0], clipAt, "mic clip");
  const stopped = msgs.find((m) => m.type === "stopped");
  assert(stopped, "the output reports the stop");
  eq(stopped.cause, STOP.MIC_CLIP);
}

/** The real meter's heartbeat keeps the output playing (no false stale). */
export async function test_no_mic_stop_output_plays_on() {
  const { out, msgs } = await render({ frames: 24000, meter: "mic" });
  const at = onsetOf(out[0]);
  assert(at >= 0 && at <= Q, "starts on the first beat: " + at);
  assertRampIn(out[0], at, "real meter");
  for (let i = at + RAMP; i < 24000; i++) eq(out[0][i], LEVEL, "sample " + i);
  eq(msgs.filter((m) => m.type === "stopped").length, 0);
}

/** C5: without any heartbeat the output never sounds and latches. */
export async function test_c5_no_meter_plays_nothing() {
  const { out, msgs } = await render({ frames: 8192, meter: "none" });
  assert(out[0].every((v) => v === 0) && out[1].every((v) => v === 0), "silent");
  const st = msgs.find((m) => m.type === "stopped");
  assert(st, "latched");
  eq(st.cause, LATCH.HEARTBEAT);
  assert(st.frame <= LATCH.STALE_QUANTA * Q + RAMP + Q, "within 4 quanta " + st.frame);
}

/** C5: zeros until the first beat after construction, then the ramp-in. */
export async function test_c5_late_first_beat_starts_from_zero() {
  const from = 8 * Q;
  // Beats only from frame 1024: the output latches stale before that.
  const stale = await render({ frames: 8192, meter: { from } });
  assert(stale.out[0].every((v) => v === 0), "stale before the first beat");
  // A beat in every quantum but the first two: plays from the beat on.
  const { out, msgs } = await render({ frames: 8192, meter: { from: 2 * Q } });
  const at = onsetOf(out[0]);
  assert(at >= 2 * Q && at <= 3 * Q, "starts on the first beat: " + at);
  assertRampIn(out[0], at, "late beat");
  eq(msgs.filter((m) => m.type === "stopped").length, 0);
}

/** C5: beats that stop, or NaN / repeated / decreasing beats, latch. */
export async function test_c5_stale_or_bad_beats_stop() {
  const at = 4000;
  const k = Math.floor(at / Q) * Q;
  const cases = [
    ["stale", { until: at }, k + (LATCH.STALE_QUANTA + 1) * Q],
    ["nan", { bad: { at, kind: "nan" } }, k + 2 * Q],
    ["repeat", { bad: { at, kind: "repeat" } }, k + 2 * Q],
    ["decrease", { bad: { at, kind: "decrease" } }, k + 2 * Q],
  ];
  for (const [why, meter, by] of cases) {
    const { out, msgs } = await render({ frames: 12000, meter });
    const o = out[0];
    for (let i = RAMP + Q; i < k; i++) eq(o[i], LEVEL, why + ": before " + i);
    assert(o[by] < LEVEL, why + ": falling by " + by);
    for (let i = k + 1; i < o.length; i++) assert(o[i] <= o[i - 1], why + ": monotonic " + i);
    for (let i = by + RAMP; i < o.length; i++) assert(Object.is(o[i], 0), why + ": zero " + i);
    const st = msgs.find((m) => m.type === "stopped");
    assert(st, why + ": latched");
    eq(st.cause, LATCH.HEARTBEAT, why);
  }
}

/** C2, C3: after a trip, a new output ramps in from 0; the old stays 0. */
export async function test_c2_output_started_after_a_trip_ramps_in_from_zero() {
  const startAt = 8192;
  const { out } = await render({
    frames: 16384, meter: "mic", clipAt: 2000, clipEnd: 2256, extraOutputAt: startAt / SR,
  });
  for (let i = (Math.floor(2000 / Q) + 1) * Q + RAMP; i < out[0].length; i++) {
    assert(Object.is(out[0][i], 0), "C3: first output stays 0 " + i);
  }
  const at = onsetOf(out[1]);
  assert(at >= startAt && at <= startAt + Q, "second output starts at once: " + at);
  assertRampIn(out[1], at, "C2");
  for (let i = at + RAMP; i < out[1].length; i++) eq(out[1][i], LEVEL, "plays " + i);
}

/** C4: an output built while the mic stays clipped never sounds. */
export async function test_c4_held_clip_new_output_never_sounds() {
  const startAt = 8192;
  const { out, msgs } = await render({
    frames: 16384, meter: "mic", clipAt: 2000, extraOutputAt: startAt / SR,
  });
  assert(out[1].every((v) => v === 0), "not one non-zero sample");
  const st = msgs.find((m) => m.type === "stopped" && m.channel === 1);
  assert(st, "the new output is latched");
  eq(st.cause, STOP.MIC_CLIP);
}

/** A1: building a newer output stops the older one, with the 4e ramp. */
export async function test_a1_newer_output_stops_the_older() {
  const startAt = 8192;
  const { out, msgs } = await render({ frames: 16384, extraOutputAt: startAt / SR });
  assertStopRamp(out[0], startAt, "superseded");
  const st = msgs.find((m) => m.type === "stopped" && m.channel === 0);
  eq(st.cause, LATCH.SUPERSEDED);
  const at = onsetOf(out[1]);
  assertRampIn(out[1], at, "the newer output");
}
