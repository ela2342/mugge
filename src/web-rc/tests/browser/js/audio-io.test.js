// AudioIO stop order (audio-io.js; latch r2 B4, AE 6f220842, test C1b): an
// output node is disconnected and the context suspended only once the node
// reports zero reached, or ZERO_TIMEOUT_MS after the stop; a new node is
// built only after the old one is disconnected. A fake context and fake
// nodes log every call, in order.

import { assert, eq } from "./assert.js";
import { AudioIO, IO } from "../../../static/js/audio-io.js";

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
  const msgs = { output: [], meter: [] };
  const io = new AudioIO({
    onOutput: (m) => msgs.output.push(m), onMeter: (m) => msgs.meter.push(m),
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
