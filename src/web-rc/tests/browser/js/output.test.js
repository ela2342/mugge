// Output chain (output-core.js, output-worklet.js): US-179 AC4c, 4e, 4f,
// 4h, 5d, AE A4.

import { assert, close, eq, throws } from "./assert.js";
import {
  BufferSource, CAP_LINEAR, OutputChain, STATE, renderPlayed,
} from "../../../static/js/output-core.js";
import { crestEntry, levelCeilingDbfs, unitGain } from "../../../static/js/crest.js";
import { crestSeed } from "../../../static/js/crest-plan.js";
import { LevelNoise } from "../../../static/js/dsp.js";
import { LIMITS, ROLE, levelNoiseBand } from "../../../static/js/safety.js";
import { addBeater } from "./beater.js";

const SR = 48000;
const Q = 128;
const RAMP = 480; // 10 ms
const WORKLET = new URL("../../../static/js/output-worklet.js", import.meta.url);

const ones = (n) => new Float32Array(n).fill(1);

function renderAll(chain, n) {
  const out = new Float32Array(Math.ceil(n / Q) * Q);
  const events = [];
  for (let i = 0; i < out.length; i += Q) {
    const ev = chain.render(out.subarray(i, i + Q));
    events.push({ at: i, ...ev });
  }
  return { out, events };
}

export async function test_cap_constant() {
  eq(CAP_LINEAR, Math.fround(0.1), "-20 dBFS as f32");
}

export async function test_ramps_in_from_zero() {
  const g = 0.05;
  const chain = new OutputChain({ sampleRate: SR, source: new BufferSource(ones(2000)), gain: g });
  const { out } = renderAll(chain, 2000);
  close(out[0], Math.fround(g / RAMP), 1e-9, "first sample near 0");
  for (let i = 1; i < RAMP; i++) assert(out[i] > out[i - 1], "rising at " + i);
  eq(out[RAMP - 1], Math.fround(g), "target reached after 10 ms");
  for (let i = RAMP; i < 2000; i++) eq(out[i], Math.fround(g), "steady " + i);
}

export async function test_step_ramps_never_jumps() {
  const g1 = 0.01;
  const g2 = 2 * g1; // +6 dB
  const chain = new OutputChain({ sampleRate: SR, source: new BufferSource(ones(4000)), gain: g1 });
  const a = new Float32Array(1024);
  chain.render(a);
  chain.setGain(g2);
  const b = new Float32Array(1024);
  chain.render(b);
  eq(a[1023], Math.fround(g1));
  let maxStep = Math.abs(b[0] - a[1023]);
  for (let i = 1; i < 1024; i++) maxStep = Math.max(maxStep, Math.abs(b[i] - b[i - 1]));
  assert(maxStep <= (g2 - g1) / RAMP * 1.0001, "largest per-sample step " + maxStep);
  eq(b[RAMP - 1], Math.fround(g2));
  throws(() => chain.setGain(NaN));
  throws(() => chain.setGain(-1));
}

export async function test_stop_ramps_to_zero_then_silence() {
  const src = new BufferSource(ones(10000));
  const chain = new OutputChain({ sampleRate: SR, source: src, gain: 0.05 });
  const a = new Float32Array(1024);
  chain.render(a);
  chain.stop();
  eq(chain.state, STATE.STOPPING);
  const b = new Float32Array(1024);
  const ev = chain.render(b);
  eq(ev.stopped, true);
  eq(chain.state, STATE.STOPPED);
  for (let i = 1; i < RAMP; i++) assert(b[i] < b[i - 1], "falling at " + i);
  for (let i = RAMP - 1; i < 1024; i++) eq(b[i], 0, "silent " + i);
  const posAfter = src.pos;
  chain.render(new Float32Array(Q));
  eq(src.pos, posAfter, "source not advanced once stopped");
  chain.setGain(0.1);
  eq(chain.state, STATE.STOPPED, "no restart by a gain message");
}

export async function test_clamp_stops_never_limits() {
  const s = new Float32Array(5000).fill(0.5);
  s[2000] = 1.0; // at gain 0.1: 0.1 = the cap
  const chain = new OutputChain({ sampleRate: SR, source: new BufferSource(s), gain: 0.1 });
  const { out, events } = renderAll(chain, 5000);
  const ev = events.find((e) => e.clampedAt >= 0);
  eq(ev.at + ev.clampedAt, 2000, "clamped at the sample that reached the cap");
  eq(out[2000], CAP_LINEAR);
  for (let i = 0; i < out.length; i++) assert(Math.abs(out[i]) <= CAP_LINEAR, "cap " + i);
  for (let i = 2001; i < 2000 + RAMP; i++) assert(out[i] < out[i - 1] || out[i] === 0, "ramping down " + i);
  for (let i = 2000 + RAMP; i < out.length; i++) eq(out[i], 0, "stopped " + i);
  assert(events.some((e) => e.stopped), "stopped event");
  eq(chain.clamped, true);
}

export async function test_non_finite_is_a_clamp_and_silent() {
  const s = new Float32Array(1000).fill(0.1);
  s[600] = NaN;
  const chain = new OutputChain({ sampleRate: SR, source: new BufferSource(s), gain: 0.1 });
  const { out, events } = renderAll(chain, 1000);
  eq(out[600], 0, "NaN never reaches the output");
  assert(events.some((e) => e.clampedAt >= 0), "NaN stops like the cap");
}

export async function test_buffer_end_reported() {
  const chain = new OutputChain({ sampleRate: SR, source: new BufferSource(ones(300)), gain: 0.01 });
  const { out, events } = renderAll(chain, 600);
  eq(events[2].ended, true);
  for (let i = 300; i < 600; i++) eq(out[i], 0);
}

/**
 * At the crest-table ceiling the noise never reaches the cap, even past the
 * 10 s the crest was measured over (60 s, every seed, full-range and the
 * lowest subwoofer band).
 */
export async function test_ceiling_level_never_clamps_in_60s() {
  for (const band of [levelNoiseBand(ROLE.FULLRANGE, 80), levelNoiseBand(ROLE.SUBWOOFER, 20)]) {
    for (let ch = 0; ch < 8; ch++) {
      const e = crestEntry(band, ch);
      const gain = unitGain(e, levelCeilingDbfs(e));
      const chain = new OutputChain({
        sampleRate: SR, source: new LevelNoise(crestSeed(ch), SR, band), gain,
      });
      const block = new Float32Array(Q);
      for (let i = 0; i < (60 * SR) / Q; i++) chain.render(block);
      eq(chain.clamped, false, `${band.lowHz}-${band.highHz} ch ${ch}`);
    }
  }
}

export async function test_render_played_matches_chain() {
  const s = new Float32Array(1000);
  for (let i = 0; i < s.length; i++) s[i] = Math.sin(i / 10);
  const { played, clamped } = renderPlayed(s, 0.05, SR);
  eq(played.length, 1000);
  eq(clamped, false);
  const { out } = renderAll(new OutputChain({ sampleRate: SR, source: new BufferSource(s), gain: 0.05 }), 1000);
  for (let i = 0; i < 1000; i++) eq(played[i], out[i], "sample " + i);
}

// -- the worklet, offline ----------------------------------------------------

async function runWorklet({ channels, channel, gain, source, frames, onFrame }) {
  const ctx = new OfflineAudioContext(channels, frames, SR);
  ctx.destination.channelInterpretation = "discrete";
  await ctx.audioWorklet.addModule(WORKLET);
  await addBeater(ctx);  // the meter heartbeat the output waits for (r2 A4)
  const node = new AudioWorkletNode(ctx, "webrc-output", {
    numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [channels],
    channelInterpretation: "discrete",
    processorOptions: { channel, gain, source },
  });
  const msgs = [];
  node.port.onmessage = (e) => msgs.push(e.data);
  node.connect(ctx.destination);
  if (onFrame) {
    for (const [t, fn] of onFrame) ctx.suspend(t).then(() => { fn(node); ctx.resume(); });
  }
  const buf = await ctx.startRendering();
  let n = -1;
  while (n !== msgs.length) {
    n = msgs.length;
    await new Promise((r) => setTimeout(r, 50));
  }
  return { buf, msgs };
}

/**
 * The quantum the output starts in: it plays nothing until its first fresh
 * meter heartbeat (latch r2 A4), which comes in its first or second quantum.
 */
function onsetOf(d) {
  const first = d.findIndex((v) => v !== 0);
  const at = Math.floor(first / Q) * Q;
  assert(first >= 0 && at <= Q, "starts within 2 quanta: " + first);
  for (let i = 0; i < at; i++) eq(d[i], 0, "zero before the first beat " + i);
  return at;
}

export async function test_worklet_mono_to_one_channel_bit_exact() {
  const s = new Float32Array(SR / 4);
  for (let i = 0; i < s.length; i++) s[i] = 0.5 * Math.sin(2 * Math.PI * 440 * i / SR);
  const { buf, msgs } = await runWorklet({
    channels: 4, channel: 2, gain: 0.1, frames: SR / 2,
    source: { kind: "buffer", samples: s },
  });
  for (const ch of [0, 1, 3]) {
    const d = buf.getChannelData(ch);
    assert(d.every((v) => v === 0), "channel " + ch + " is digital zero");
  }
  const got = buf.getChannelData(2);
  const { played } = renderPlayed(s, 0.1, SR);
  const at = onsetOf(got);
  for (let i = 0; i < played.length; i++) eq(got[at + i], played[i], "sample " + i);
  for (let i = at + played.length; i < got.length; i++) eq(got[i], 0, "after end " + i);
  assert(msgs.some((m) => m.type === "ended"), "ended reported");
  eq(msgs.filter((m) => m.type === "error").length, 0);
}

export async function test_worklet_noise_matches_level_noise() {
  const band = levelNoiseBand(ROLE.FULLRANGE, 80);
  const e = crestEntry(band, 1);
  const gain = unitGain(e, -48);
  const { buf } = await runWorklet({
    channels: 2, channel: 1, gain, frames: 4096,
    source: { kind: "noise", seed: crestSeed(1), band },
  });
  const ref = new OutputChain({ sampleRate: SR, source: new LevelNoise(crestSeed(1), SR, band), gain });
  const out = new Float32Array(4096);
  for (let i = 0; i < 4096; i += Q) ref.render(out.subarray(i, i + Q));
  const got = buf.getChannelData(1);
  const at = onsetOf(got);
  for (let i = 0; at + i < 4096; i++) eq(got[at + i], out[i], "sample " + i);
  assert(buf.getChannelData(0).every((v) => v === 0), "other channel zero");
}

export async function test_worklet_clamp_reports_and_stops() {
  const s = new Float32Array(SR / 4).fill(0.5);
  s[5000] = 1.0;
  const { buf, msgs } = await runWorklet({
    channels: 1, channel: 0, gain: 0.1, frames: SR / 4,
    source: { kind: "buffer", samples: s },
  });
  const d = buf.getChannelData(0);
  const at = onsetOf(d);
  const c = msgs.find((m) => m.type === "clamped");
  assert(c, "clamped reported");
  eq(c.frame, at + 5000);
  const st = msgs.find((m) => m.type === "stopped");
  assert(st && st.clamped === true, "stopped after the clamp");
  for (let i = at + 5000 + RAMP; i < d.length; i++) eq(d[i], 0, "silent " + i);
}

export async function test_worklet_stop_message_ramps_down() {
  const { buf, msgs } = await runWorklet({
    channels: 1, channel: 0, gain: 0.05, frames: SR / 2,
    source: { kind: "buffer", samples: new Float32Array(SR).fill(1) },
    onFrame: [[0.25, (node) => node.port.postMessage({ type: "stop" })]],
  });
  const st = msgs.find((m) => m.type === "stopped");
  assert(st && st.clamped === false, "stopped, no clamp");
  const d = buf.getChannelData(0);
  const t = SR / 4;
  eq(d[t - 1], Math.fround(0.05), "full level before the stop");
  for (let i = t + RAMP + Q; i < d.length; i++) eq(d[i], 0, "silent " + i);
}

export async function test_worklet_bad_options_play_nothing() {
  for (const [opts, why] of [
    [{ channel: 5, source: { kind: "buffer", samples: ones(1000) } }, "no such channel"],
    [{ channel: 0, source: { kind: "tone" } }, "unknown source"],
    [{ channel: 0, source: { kind: "noise", seed: 1, band: null } }, "no band"],
    [{ channel: -1, source: { kind: "buffer", samples: ones(1000) } }, "bad channel"],
  ]) {
    const { buf, msgs } = await runWorklet({ channels: 2, gain: 0.05, frames: 2048, ...opts });
    assert(msgs.some((m) => m.type === "error"), why + ": error reported");
    for (let c = 0; c < 2; c++) {
      assert(buf.getChannelData(c).every((v) => v === 0), why + ": silent ch " + c);
    }
  }
}
