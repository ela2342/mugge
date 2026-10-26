// AC5a-5c: the JS noise port against the Rust goldens, bit for bit.

import { eq, throws } from "./assert.js";
import {
  PinkNoise, WhiteNoise, channelSeed, toU64,
} from "../../../static/js/noise.js";

const N = 4096;
const SEEDS = [0, 1, 174];
const LEVELS = [[1.0, "1.0"], [0.1, "0.1"]];
const SIGNALS = [["white", WhiteNoise], ["pink", PinkNoise]];

async function golden(name) {
  const resp = await fetch("/fixtures/noise/" + name);
  if (!resp.ok) throw new Error("missing golden " + name);
  const bits = new Uint32Array(await resp.arrayBuffer());
  eq(bits.length, N, name + " length");
  return bits;
}

function firstMismatch(got, want) {
  for (let i = 0; i < want.length; i++) {
    if (got[i] !== want[i]) return i;
  }
  return -1;
}

export async function test_goldens_bit_exact_fill() {
  for (const seed of SEEDS) {
    for (const [level, levelName] of LEVELS) {
      for (const [sig, Gen] of SIGNALS) {
        const name = `${sig}_seed${seed}_level${levelName}.f32le`;
        const want = await golden(name);
        const out = new Float32Array(N);
        new Gen(seed).fill(out, level);
        eq(firstMismatch(new Uint32Array(out.buffer), want), -1, name);
      }
    }
  }
}

export async function test_goldens_bit_exact_next_sample() {
  for (const seed of SEEDS) {
    for (const [level, levelName] of LEVELS) {
      for (const [sig, Gen] of SIGNALS) {
        const name = `${sig}_seed${seed}_level${levelName}.f32le`;
        const want = await golden(name);
        const gen = new Gen(seed);
        const out = new Float32Array(N);
        for (let i = 0; i < N; i++) out[i] = gen.nextSample(level);
        eq(firstMismatch(new Uint32Array(out.buffer), want), -1, name);
      }
    }
  }
}

export async function test_seed_as_bigint_equals_number() {
  const a = new Float32Array(64);
  const b = new Float32Array(64);
  new PinkNoise(174).fill(a, 1.0);
  new PinkNoise(174n).fill(b, 1.0);
  eq(firstMismatch(new Uint32Array(a.buffer), new Uint32Array(b.buffer)), -1);
}

export async function test_channel_seed_is_xor() {
  eq(channelSeed(174, 0), 174n);
  eq(channelSeed(174, 1), 175n);
  eq(channelSeed(175, 1), 174n);
  eq(channelSeed(0xffffffffffffffffn, 1), 0xfffffffffffffffen);
}

export async function test_seed_range_checked() {
  throws(() => toU64(-1), "negative seed");
  throws(() => toU64(1n << 64n), "seed above u64");
}

export async function test_pink_counter_wrap_skips_row_update() {
  // u32::MAX + 1 wraps to 0; trailing_zeros(0) = 32 >= 16, so no row
  // changes and the RNG is not drawn (generator.rs next_sample).
  const pink = new PinkNoise(1);
  pink.counter = 0xffffffff;
  const rows = Float64Array.from(pink.rows);
  const state = Uint32Array.from(pink.rng.s);
  pink.nextRaw();
  eq(pink.counter, 0);
  eq(firstMismatch(pink.rows, rows), -1, "rows unchanged");
  eq(firstMismatch(pink.rng.s, state), -1, "rng not advanced");
}

export async function test_pink_row_index_is_trailing_zeros() {
  // counter 8 -> row 3 updates, every other row stays.
  const pink = new PinkNoise(1);
  pink.counter = 7;
  const rows = Float64Array.from(pink.rows);
  pink.nextRaw();
  for (let i = 0; i < 16; i++) {
    if (i === 3) {
      eq(pink.rows[i] !== rows[i], true, "row 3 updated");
    } else {
      eq(pink.rows[i], rows[i], "row " + i);
    }
  }
}
