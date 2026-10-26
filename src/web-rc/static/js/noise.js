// noise.js -- bit-exact port of signal-gen's white and pink noise (US-179 AC5b).
//
// Source of truth: src/signal-gen/src/generator.rs (WhiteNoiseGenerator,
// PinkNoiseGenerator) with rand_xoshiro 0.7.0 / rand_core 0.9.5.
// Goldens: src/web-rc/fixtures/noise/ (AC5c).
//
// The RNG works on 64-bit values held as two uint32 halves, so the per-sample
// path allocates nothing and is safe inside an AudioWorklet. Seeding uses
// BigInt once per generator.

const MASK64 = (1n << 64n) - 1n;
const PHI = 0x9e3779b97f4a7c15n;
const TWO_POW_M53 = 1 / 9007199254740992; // 2^-53
const PINK_NUM_ROWS = 16;

// SplitMix64 as in rand_xoshiro 0.7.0 (seed_from_u64 = from_seed(le bytes)).
function splitmix64(state) {
  let x = state;
  return function next() {
    x = (x + PHI) & MASK64;
    let z = x;
    z = ((z ^ (z >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
    z = ((z ^ (z >> 27n)) * 0x94d049bb133111ebn) & MASK64;
    return z ^ (z >> 31n);
  };
}

/** Normalise a seed (number or BigInt) to an unsigned 64-bit BigInt. */
export function toU64(seed) {
  const s = typeof seed === "bigint" ? seed : BigInt(seed);
  if (s < 0n || s > MASK64) {
    throw new RangeError("seed out of u64 range: " + seed);
  }
  return s;
}

/** AC5a: per-channel seed = base_seed XOR channel_index (0-based). */
export function channelSeed(baseSeed, channelIndex) {
  return toU64(baseSeed) ^ toU64(channelIndex);
}

/** Xoshiro256++ seeded like Xoshiro256PlusPlus::seed_from_u64. */
export class Xoshiro256PlusPlus {
  constructor(seed) {
    const next = splitmix64(toU64(seed));
    // from_rng fills the 32-byte seed with four LE next_u64 values;
    // read_u64_into reads them back as s[0..4].
    this.s = new Uint32Array(8); // [s0h, s0l, s1h, s1l, s2h, s2l, s3h, s3l]
    let allZero = true;
    for (let i = 0; i < 4; i++) {
      const v = next();
      if (v !== 0n) allZero = false;
      this.s[2 * i] = Number(v >> 32n);
      this.s[2 * i + 1] = Number(v & 0xffffffffn);
    }
    if (allZero) {
      // deal_with_zero_seed: unreachable for SplitMix64 output in practice.
      throw new Error("all-zero xoshiro state");
    }
    this.hi = 0;
    this.lo = 0;
  }

  /** Advance once; the 64-bit result is left in this.hi / this.lo. */
  nextU64() {
    const s = this.s;
    const s0h = s[0], s0l = s[1], s1h = s[2], s1l = s[3];
    const s2h = s[4], s2l = s[5], s3h = s[6], s3l = s[7];

    // result = (s0 + s3).rotate_left(23) + s0
    let al = (s0l + s3l) >>> 0;
    let ah = (s0h + s3h + (al < s0l ? 1 : 0)) >>> 0;
    const rh = ((ah << 23) | (al >>> 9)) >>> 0;
    const rl = ((al << 23) | (ah >>> 9)) >>> 0;
    const resl = (rl + s0l) >>> 0;
    this.hi = (rh + s0h + (resl < rl ? 1 : 0)) >>> 0;
    this.lo = resl;

    // t = s1 << 17
    const th = ((s1h << 17) | (s1l >>> 15)) >>> 0;
    const tl = (s1l << 17) >>> 0;

    const n2h = (s2h ^ s0h) >>> 0, n2l = (s2l ^ s0l) >>> 0;
    const n3h = (s3h ^ s1h) >>> 0, n3l = (s3l ^ s1l) >>> 0;
    const n1h = (s1h ^ n2h) >>> 0, n1l = (s1l ^ n2l) >>> 0;
    const n0h = (s0h ^ n3h) >>> 0, n0l = (s0l ^ n3l) >>> 0;

    // s3 = s3.rotate_left(45) = swap halves, then rotate_left(13)
    s[0] = n0h; s[1] = n0l;
    s[2] = n1h; s[3] = n1l;
    s[4] = (n2h ^ th) >>> 0; s[5] = (n2l ^ tl) >>> 0;
    s[6] = ((n3l << 13) | (n3h >>> 19)) >>> 0;
    s[7] = ((n3h << 13) | (n3l >>> 19)) >>> 0;
  }

  /** (next_u64() >> 11) as f64 * 2^-53, mapped to [-1, 1) in f64. */
  nextUnitBipolar() {
    this.nextU64();
    const f = (this.hi * 2097152 + (this.lo >>> 11)) * TWO_POW_M53;
    return f * 2.0 - 1.0;
  }
}

/** WhiteNoiseGenerator: f32 sample, then f32 multiply by the level. */
export class WhiteNoise {
  constructor(seed) {
    this.rng = new Xoshiro256PlusPlus(seed);
  }

  nextSample(level) {
    const sample = Math.fround(this.rng.nextUnitBipolar());
    return Math.fround(sample * Math.fround(level));
  }

  /** Fill a mono Float32Array, like generate(buf, n, 1, 0x01, level). */
  fill(out, level) {
    const lvl = Math.fround(level);
    for (let i = 0; i < out.length; i++) {
      out[i] = Math.fround(Math.fround(this.rng.nextUnitBipolar()) * lvl);
    }
  }
}

/** PinkNoiseGenerator: Voss-McCartney, 16 rows, f64 until the final cast. */
export class PinkNoise {
  constructor(seed) {
    this.rng = new Xoshiro256PlusPlus(seed);
    this.rows = new Float64Array(PINK_NUM_ROWS);
    this.runningSum = 0.0;
    for (let i = 0; i < PINK_NUM_ROWS; i++) {
      this.rows[i] = this.rng.nextUnitBipolar();
      this.runningSum += this.rows[i];
    }
    this.counter = 0; // u32, wraps
    this.norm = 1.0 / PINK_NUM_ROWS;
  }

  nextRaw() {
    this.counter = (this.counter + 1) >>> 0;
    const c = this.counter;
    const rowIdx = c === 0 ? 32 : 31 - Math.clz32(c & -c);
    if (rowIdx < PINK_NUM_ROWS) {
      this.runningSum -= this.rows[rowIdx];
      this.rows[rowIdx] = this.rng.nextUnitBipolar();
      this.runningSum += this.rows[rowIdx];
    }
    return this.runningSum * this.norm;
  }

  nextSample(level) {
    return Math.fround(this.nextRaw() * Math.fround(level));
  }

  fill(out, level) {
    const lvl = Math.fround(level);
    for (let i = 0; i < out.length; i++) {
      out[i] = Math.fround(this.nextRaw() * lvl);
    }
  }
}
