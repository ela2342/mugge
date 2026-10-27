// AudioIO stop order (audio-io.js; latch r2 B4, AE 6f220842, test C1b): an
// output node is disconnected and the context suspended only once the node
// reports zero reached, or ZERO_TIMEOUT_MS after the stop; a new node is
// built only after the old one is disconnected. A fake context and fake
// nodes log every call, in order.

import { assert, eq } from "./assert.js";
import { AudioIO, IO, isSuperseded } from "../../../static/js/audio-io.js";

const NOISE = { kind: "noise", seed: 1, band: null };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** An AudioIO on a fake context; `log` holds every context/node call. */
function rig() {
  const log = [];
  const ctx = {
    state: "suspended",
    destination: { channelCount: 2 },
    suspend() { log.push("suspend"); this.state = "suspended"; return Promise.resolve(); },
    resume() { log.push("resume"); this.state = "running"; return Promise.resolve(); },
    close() { log.push("close"); this.state = "closed"; return Promise.resolve(); },
  };
  const outputs = {}, meterOut = [];
  const msgs = { output: [], meter: [], recorded: [], resumed: [] };
  const io = new AudioIO({
    onOutput: (m) => msgs.output.push(m), onMeter: (m) => msgs.meter.push(m),
    onRecorded: (...args) => msgs.recorded.push(args),
    onResumed: (t) => msgs.resumed.push(t),
  });
  io.ctx = ctx;
  io.meter = { port: { postMessage: (m) => meterOut.push(m) } };
  let n = 0;
  io._newOutput = (opts) => {
    const name = String.fromCharCode(65 + n++);   // A, B, C ...
    log.push("new " + name);
    const node = {
      name, opts, posted: [],
      port: { postMessage: (m) => node.posted.push(m.type) },
      connect: () => log.push("connect " + name),
      disconnect: () => log.push("disconnect " + name),
      // The render thread's messages.
      send: (data) => node.port.onmessage({ data }),
    };
    outputs[name] = node;
    return node;
  };
  const play = () => io.execute({ type: "noise-start", channel: 0, source: NOISE, gain: 0.01 });
  return { io, ctx, log, outputs, msgs, meterOut, play };
}

/** The log entries after `mark`, as one string. */
const since = (log, mark) => log.slice(mark).join(", ");

export async function test_c1b_stop_waits_for_zero_reached() {
  const { io, log, outputs, msgs, play } = rig();
  play();
  eq(since(log, 0), "new A, connect A, resume");
  const mark = log.length;
  io.execute({ type: "output-stop" });
  eq(outputs.A.posted.join(), "stop", "the ramp is started");
  await sleep(IO.ZERO_TIMEOUT_MS / 2);
  eq(since(log, mark), "", "no disconnect, no suspend before zero is reached");
  outputs.A.send({ type: "stopped", frame: 9000, clamped: false, cause: null });
  eq(since(log, mark), "disconnect A, suspend", "zero reached: disconnect, then suspend");
  eq(msgs.output.map((m) => m.type).join(), "stopped");
  eq(io.out, null);
  await sleep(IO.ZERO_TIMEOUT_MS);
  eq(since(log, mark), "disconnect A, suspend", "the deadline is cleared");
}

export async function test_c1b_new_node_only_after_old_disconnect() {
  const { io, log, outputs, msgs, play } = rig();
  play();
  const mark = log.length;
  play();
  eq(outputs.A.posted.join(), "stop");
  eq(since(log, mark), "", "B waits for A");
  await sleep(IO.ZERO_TIMEOUT_MS / 2);
  eq(since(log, mark), "", "B still waits, no suspend in between");
  outputs.A.send({ type: "stopped", frame: 9000, clamped: false, cause: "superseded" });
  await sleep(0);
  eq(since(log, mark), "disconnect A, new B, connect B", "A gone before B exists");
  eq(io.out, outputs.B);
  eq(msgs.output.length, 0, "A's late messages are stale");
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "disconnect A, new B, connect B", "no fallback fires");
}

/** The 100 ms fallback: the "stopped" message is dropped. */
export async function test_c1b_dropped_zero_reached_suspends_by_deadline() {
  const { io, log, play } = rig();
  play();
  let mark = log.length;
  io.execute({ type: "output-stop" });
  await sleep(IO.ZERO_TIMEOUT_MS * 0.8);
  eq(since(log, mark), "", "not before the deadline");
  await sleep(IO.ZERO_TIMEOUT_MS * 0.7);
  eq(since(log, mark), "suspend, disconnect A", "suspended, then treated as stopped");
  eq(io.retiring.size, 0);
  eq(io.out, null);

  // With a replacement waiting: suspend, disconnect, then the new node.
  play();
  mark = log.length;
  play();
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "suspend, disconnect B, new C, connect C, resume");
}

export async function test_c1b_meter_stop_starts_the_deadline() {
  const { io, log, outputs, msgs, play } = rig();
  play();
  const mark = log.length;
  io._onMeterMessage({ type: "meter", cause: "mic_clip", peakDbfs: 0 });
  eq(outputs.A.posted.join(), "stop", "no wait for the flow");
  eq(msgs.meter.length, 1);
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "suspend, disconnect A", "no zero-reached: the deadline");
  io._onMeterMessage({ type: "meter", cause: "mic_clip", peakDbfs: 0 });
  eq(since(log, mark), "suspend, disconnect A", "nothing left to stop");
}

/** A stop from the render thread (stop-latch.js) retires the node too. */
export async function test_c1b_render_thread_stop_retires() {
  const { io, log, outputs, msgs, play } = rig();
  play();
  const mark = log.length;
  outputs.A.send({ type: "stopped", frame: 9000, clamped: false, cause: "heartbeat" });
  eq(since(log, mark), "disconnect A, suspend");
  eq(msgs.output[0].cause, "heartbeat", "the flow hears the cause");
  eq(io.out, null);
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "disconnect A, suspend", "the deadline is cleared");
}

export async function test_c1b_error_retires_with_deadline() {
  const { io, log, outputs, msgs, play } = rig();
  play();
  const mark = log.length;
  outputs.A.send({ type: "error", message: "bad channel" });
  eq(outputs.A.posted.join(), "stop");
  eq(msgs.output[0].type, "error");
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "suspend, disconnect A");
}

export async function test_c1b_stop_cancels_a_waiting_play() {
  const { io, log, outputs, play } = rig();
  play();
  const mark = log.length;
  play();
  io.execute({ type: "output-stop" });
  outputs.A.send({ type: "stopped", frame: 9000, clamped: false, cause: null });
  await sleep(0);
  eq(since(log, mark), "disconnect A, suspend", "B is never built");
  eq(outputs.B, undefined);
}

export async function test_c1b_close_waits_for_zero_reached() {
  const { io, log, outputs, play } = rig();
  play();
  const mark = log.length;
  let closed = false;
  const p = io.close().then(() => { closed = true; });
  eq(outputs.A.posted.join(), "stop");
  await sleep(IO.ZERO_TIMEOUT_MS / 2);
  eq(closed, false);
  eq(since(log, mark), "", "the context is not closed under a sounding node");
  outputs.A.send({ type: "stopped", frame: 9000, clamped: false, cause: null });
  await p;
  eq(since(log, mark), "disconnect A, suspend, close");
  eq(io.isOpen, false);
}

/** A sweep that ended is silent: retire it without a suspend fallback. */
export async function test_c1b_ended_sweep_retires_without_suspend() {
  const { io, log, outputs, msgs, play } = rig();
  io.execute({ type: "record", token: 7, frames: 1000 });
  play();
  const mark = log.length;
  outputs.A.send({ type: "ended", frame: 9000 });
  eq(outputs.A.posted.join(), "stop");
  eq(msgs.output[0].type, "ended");
  await sleep(IO.ZERO_TIMEOUT_MS * 1.5);
  eq(since(log, mark), "disconnect A", "no suspend while recording");
  assert(io.recording === 7, "the recording goes on");
}

/**
 * AE a1736914: the output onset and the capture's first frame reach the
 * flow, each with the clock of the context that counted it.
 */
export async function test_onset_and_start_frame_are_passed_on() {
  const { io, outputs, msgs, play } = rig();
  io.clock = io.meter.clock = 3;
  play();
  outputs.A.send({ type: "started", frame: 1152 });
  eq(JSON.stringify(msgs.output),
    JSON.stringify([{ type: "started", frame: 1152, clock: 3 }]));
  io.execute({ type: "record", token: 5, frames: 10 });
  const samples = new Float32Array(10);
  io.clock = 4;                   // the meter's clock counts, not the latest
  io._onMeterMessage({ type: "recorded", id: 5, startFrame: 1024, samples });
  eq(msgs.recorded.length, 1);
  eq(msgs.recorded[0][0], 5);
  eq(msgs.recorded[0][1], samples);
  eq(msgs.recorded[0][2], 1024, "the capture's first frame");
  eq(msgs.recorded[0][3], 3, "the meter's clock");
}

/** AE 42dada94 G1: the clock check's lookback goes in, its result comes out. */
export async function test_clock_check_is_passed_through() {
  const { io, msgs, meterOut } = rig();
  io.clock = io.meter.clock = 3;
  io.execute({ type: "record", token: 5, frames: 10, lookback: 2400 });
  eq(JSON.stringify(meterOut.at(-1)),
    JSON.stringify({ type: "record", id: 5, frames: 10, lookback: 2400 }));
  const clockGlitch = { before: 1024, after: 1024 };
  io._onMeterMessage({ type: "recorded", id: 5, startFrame: 1024,
    samples: new Float32Array(10), clockGlitch });
  eq(msgs.recorded[0][4], clockGlitch);
}

/** AE d7ffcfb6: a capture arriving with no meter left is dropped, no throw. */
export async function test_recorded_without_a_meter_is_dropped() {
  const { io, msgs } = rig();
  io.clock = io.meter.clock = 3;
  io.execute({ type: "record", token: 5, frames: 10 });
  io.meter = null;
  io._onMeterMessage({ type: "recorded", id: 5, startFrame: 0,
    samples: new Float32Array(10) });
  eq(msgs.recorded.length, 0);
}

/** AE onset clock condition: a node keeps the clock of the context it ran on. */
export async function test_started_carries_the_node_clock() {
  const { io, outputs, msgs, play } = rig();
  io.clock = 3;
  play();
  io.clock = 4;                   // a new context opened meanwhile
  outputs.A.send({ type: "started", frame: 0 });
  eq(msgs.output[0].clock, 3);
}

/**
 * AE 30d2bcef Q3: "resume" is reported once the context runs, so capture 1's
 * pre-roll is never recorded on a still-resuming context.
 */
export async function test_resume_reports_once_running() {
  const { io, ctx, log, meterOut, msgs } = rig();
  io.execute({ type: "resume", token: 7 });
  eq(since(log, 0), "resume");
  eq(msgs.resumed.length, 0, "not before resume() resolves");
  await sleep(0);
  eq(msgs.resumed.join(), "7");
  eq(since(log, 0), "resume, suspend", "nothing started: suspended again");

  // The flow starts the capture on the report: no suspend.
  const b = rig();
  b.io.onResumed = (t) => b.io.execute({ type: "record", token: t, frames: 10 });
  b.io.execute({ type: "resume", token: 8 });
  eq(b.meterOut.length, 0, "no record before the context runs");
  await sleep(0);
  eq(b.meterOut.map((m) => m.type + " " + m.id).join(), "record 8");
  eq(since(b.log, 0), "resume", "running, not suspended");
  assert(b.ctx.state === "running");

  // Closed or reopened meanwhile: no report.
  const c = rig();
  c.io.execute({ type: "resume", token: 9 });
  c.io.ctx = null;
  await sleep(0);
  eq(c.msgs.resumed.length, 0);
}

// -- F-468: overlapping opens --------------------------------------------

/**
 * Runs `fn` with fake media devices and Web Audio behind open(). Each step
 * is named by the call it belongs to: "gum1", "gum2", ... per getUserMedia
 * call; "suspend1", "meter1", "output1", ... per context made. A step in
 * `held` waits for release(name), one in `fail` then rejects; reached(name)
 * resolves once an open is at that step, hit(name) tells whether one was.
 * `log` records "stopN" (stream N's track) and "closeN" (context N) in
 * call order. The order is the test's, not a clock's.
 */
async function withDevices({ held = [], fail = [] }, fn) {
  const steps = new Map();
  const step = (name) => {
    if (!steps.has(name)) {
      const s = {};
      s.reached = new Promise((r) => { s.arrive = r; });
      s.gate = new Promise((r) => { s.go = r; });
      steps.set(name, s);
    }
    return steps.get(name);
  };
  const pass = async (name) => {
    const s = step(name);
    s.hit = true;
    s.arrive();
    if (held.includes(name)) await s.gate;
    if (fail.includes(name)) throw new Error(name + " failed");
  };
  const streams = [], contexts = [], log = [];
  class FakeContext {
    constructor(opts) {
      this.n = contexts.push(this);
      this.opts = opts;
      this.state = "running";
      this.sampleRate = 48000;
      this.destination = { maxChannelCount: 8 };
      this.audioWorklet = {
        addModule: (url) => pass((String(url).includes("meter") ? "meter" : "output") + this.n),
      };
    }
    async suspend() { await pass("suspend" + this.n); this.state = "suspended"; }
    async close() { log.push("close" + this.n); this.state = "closed"; }
    createMediaStreamSource() { return { connect() {} }; }
    addEventListener() {}
    setSinkId() {}
  }
  class FakeNode {
    constructor() { this.port = { postMessage() {} }; }
  }
  const md = navigator.mediaDevices;
  const saved = [md.getUserMedia, window.AudioContext, window.AudioWorkletNode];
  md.getUserMedia = async () => {
    const n = streams.length + 1;
    const track = {
      stopped: false, label: "", stop() { log.push("stop" + n); this.stopped = true; },
      addEventListener() {}, getSettings: () => ({ sampleRate: 48000 }),
    };
    const stream = { track, getTracks: () => [track], getAudioTracks: () => [track] };
    streams.push(stream);
    await pass("gum" + n);
    return stream;
  };
  window.AudioContext = FakeContext;
  window.AudioWorkletNode = FakeNode;
  try {
    await fn({ reached: (name) => step(name).reached, release: (name) => step(name).go(),
      hit: (name) => !!(steps.has(name) && steps.get(name).hit), streams, contexts, log });
  } finally {
    [md.getUserMedia, window.AudioContext, window.AudioWorkletNode] = saved;
  }
}

/** The rejection of `p`, or null if it resolves. */
const rejection = (p) => p.then(() => null, (e) => e);

/** `p`, with its settling logged as `name` (QE 390b9cd8 T4f). */
const logged = (log, name, p) => p.then(
  (v) => { log.push(name); return v; },
  (e) => { log.push(name); throw e; });

/** T4f: the superseded open cleaned up after itself before it rejected. */
function cleanedUpFirst(log, n, at) {
  const settled = log.indexOf(at);
  assert(settled >= 0, at + " settled");
  for (const step of ["stop" + n, "close" + n]) {
    const i = log.indexOf(step);
    assert(i >= 0 && i < settled, step + " before " + at + ": " + log.join());
  }
}

/**
 * Run 11: the older open, held at `at`, finishes after the newer one; it
 * stops there, before its `next` step.
 */
async function olderFinishesLast(at, next) {
  await withDevices({ held: [at] }, async ({ reached, release, hit, streams, contexts, log }) => {
    const io = new AudioIO();
    const first = logged(log, "settled1", io.open({ sinkId: "" }));
    await reached(at);
    await io.open({ sinkId: "room" });
    eq(io.ctx, contexts[1], "the newer open has committed");
    release(at);
    const e = await rejection(first);
    assert(isSuperseded(e), "the older open rejects SupersededError, got " + e);
    eq(hit(next), false, "the older open stops at once, before " + next);
    cleanedUpFirst(log, 1, "settled1");
    eq(io.ctx, contexts[1], "the newer context stays");
    eq(io.sinkId, "room", "the newer choice stays");
    eq(contexts[0].state, "closed", "the older context is closed");
    eq(streams[0].track.stopped, true, "the older mic is stopped");
    eq(contexts[1].state, "suspended");
    eq(streams[1].track.stopped, false);
  });
}

export async function test_f468_older_open_held_at_suspend() {
  await olderFinishesLast("suspend1", "meter1");
}

export async function test_f468_older_open_held_at_the_meter_module() {
  await olderFinishesLast("meter1", "output1");
}

export async function test_f468_older_open_held_at_the_output_module() {
  await olderFinishesLast("output1", "none");
}

export async function test_f468_older_open_finishing_first_does_not_commit() {
  await withDevices({ held: ["meter1", "gum2"] }, async ({ reached, release, contexts }) => {
    const io = new AudioIO();
    const first = io.open({ sinkId: "" });
    await reached("meter1");
    const second = io.open({ sinkId: "room" });
    await reached("gum2");
    release("meter1");
    assert(isSuperseded(await rejection(first)), "the older open is superseded");
    eq(io.ctx, null, "nothing committed in between");
    eq(contexts[0].state, "closed");
    release("gum2");
    await second;
    eq(io.ctx, contexts[1]);
    eq(io.sinkId, "room");
  });
}

export async function test_f468_close_cancels_an_open_in_flight() {
  await withDevices({ held: ["meter1"] }, async ({ reached, release, streams, contexts, log }) => {
    const io = new AudioIO();
    const p = logged(log, "settled1", io.open({ sinkId: "room" }));
    await reached("meter1");
    await io.close();
    release("meter1");
    assert(isSuperseded(await rejection(p)), "the open is superseded");
    cleanedUpFirst(log, 1, "settled1");
    eq(io.ctx, null, "nothing committed after the close");
    eq(io.isOpen, false);
    eq(contexts[0].state, "closed");
    eq(streams[0].track.stopped, true);
  });
}

export async function test_f468_close_during_getusermedia_makes_no_context() {
  await withDevices({ held: ["gum1"] }, async ({ reached, release, streams, contexts }) => {
    const io = new AudioIO();
    const p = io.open({ sinkId: "room" });
    await reached("gum1");
    await io.close();
    release("gum1");
    assert(isSuperseded(await rejection(p)), "the open is superseded");
    eq(contexts.length, 0, "no context for a superseded open");
    eq(streams[0].track.stopped, true, "the granted mic is stopped");
    eq(io.ctx, null);
  });
}

export async function test_f468_close_right_after_open_cancels_it() {
  // No await in between: the open has not yet passed its own close().
  await withDevices({}, async ({ contexts }) => {
    const io = new AudioIO();
    const p = io.open({ sinkId: "room" });
    const c = io.close();
    assert(isSuperseded(await rejection(p)), "the open is superseded");
    await c;
    eq(io.ctx, null);
    eq(contexts.every((x) => x.state === "closed"), true);
  });
}

export async function test_f468_errors_of_a_current_open_pass_through() {
  await withDevices({ fail: ["meter1"] }, async ({ streams, contexts }) => {
    const io = new AudioIO();
    const e = await rejection(io.open({ sinkId: "room" }));
    eq(e && e.message, "meter1 failed", "the original error");
    eq(isSuperseded(e), false);
    eq(io.ctx, null);
    eq(contexts[0].state, "closed");
    eq(streams[0].track.stopped, true);
  });
}

export async function test_f468_errors_of_a_superseded_open_are_superseded() {
  // A newer open owns the outcome: an older one's failure is not reported.
  await withDevices({ held: ["gum1"], fail: ["gum1"] }, async ({ reached, release, contexts }) => {
    const io = new AudioIO();
    const first = io.open({ sinkId: "" });
    await reached("gum1");
    const second = io.open({ sinkId: "room" });
    release("gum1");
    assert(isSuperseded(await rejection(first)), "superseded, not the gum error");
    await second;
    eq(io.ctx, contexts[0], "the newer open's context (the first one made)");
    eq(io.sinkId, "room");
  });
}

export async function test_f468_module_errors_of_a_superseded_open_are_superseded() {
  await withDevices({ held: ["meter1"], fail: ["meter1"] }, async ({ reached, release, contexts }) => {
    const io = new AudioIO();
    const first = io.open({ sinkId: "" });
    await reached("meter1");
    const second = io.open({ sinkId: "room" });
    await second;
    release("meter1");
    const e = await rejection(first);
    assert(isSuperseded(e), "superseded, not the module error: " + e);
    eq(contexts[0].state, "closed");
    eq(io.ctx, contexts[1]);
  });
}

export async function test_f468_three_opens_the_middle_one_finishing_last() {
  // QE 390b9cd8 T4e.
  await withDevices({ held: ["meter1", "meter2"] }, async ({ reached, release, streams, contexts }) => {
    const io = new AudioIO();
    const first = io.open({ sinkId: "a" });
    await reached("meter1");
    const second = io.open({ sinkId: "b" });
    await reached("meter2");
    await io.open({ sinkId: "c" });
    eq(io.ctx, contexts[2], "the newest open has committed");
    release("meter1");
    assert(isSuperseded(await rejection(first)), "the first open is superseded");
    release("meter2");
    assert(isSuperseded(await rejection(second)), "the middle open is superseded");
    eq(io.ctx, contexts[2], "the newest context stays");
    eq(io.sinkId, "c");
    eq(contexts.map((c) => c.state).join(), "closed,closed,suspended");
    eq(streams.map((s) => s.track.stopped).join(), "true,true,false");
  });
}
