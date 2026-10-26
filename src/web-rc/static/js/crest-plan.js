// crest-plan.js -- which level-noise crest factors exist, and how they are
// computed (US-179 AE A2, E2d).
//
// The level check plays band-limited pink noise; its start, steps and target
// are the output RMS (AE A2). The peak follows from the crest factor, which
// is measured once over >= 10 s per (band, seed) and stored as a constant in
// crest-table.js (tools/gen_crest_table.py). CI recomputes every entry
// (crest.test.js). This module does not import the table, so the generator
// can run before the table exists.

import { LEVEL_NOISE, levelNoiseCrest } from "./dsp.js";
import { channelSeed } from "./noise.js";
import { LIMITS, ROLE, ROLE_LIMITS, levelNoiseBand } from "./safety.js";

/** Fixed base seed: the level noise is the same on every run. */
export const BASE_SEED = 174;
/** USBStreamer outputs; channel index 0..7 picks the per-channel seed. */
export const MAX_CHANNELS = 8;

export function bandKey(band) {
  return band.lowHz + "-" + band.highHz;
}

/** Seed for an output channel (AC5a): BASE_SEED XOR channel index. */
export function crestSeed(channelIndex) {
  if (!(Number.isInteger(channelIndex) && channelIndex >= 0 &&
        channelIndex < MAX_CHANNELS)) {
    throw new RangeError("channel index out of range: " + channelIndex);
  }
  return Number(channelSeed(BASE_SEED, channelIndex));
}

/**
 * Every band the level check can play: the full-range band, and one
 * subwoofer band per whole-Hz limit (checkDeclaration only accepts whole Hz).
 */
export function crestBands() {
  const bands = [levelNoiseBand(ROLE.FULLRANGE, ROLE_LIMITS.fullrange.defaultHz)];
  const sub = ROLE_LIMITS.subwoofer;
  for (let hz = sub.minHz; hz <= sub.maxHz; hz++) {
    bands.push(levelNoiseBand(ROLE.SUBWOOFER, hz));
  }
  return bands;
}

/** { "<low>-<high>": { "<seed>": { rms, peak, crestDb } } } at 48 kHz. */
export function computeCrestTable() {
  const table = {};
  for (const band of crestBands()) {
    const perSeed = {};
    for (let ch = 0; ch < MAX_CHANNELS; ch++) {
      const seed = crestSeed(ch);
      perSeed[String(seed)] = levelNoiseCrest(
        seed, LIMITS.REQUIRED_RATE, band, LEVEL_NOISE.CREST_SECONDS);
    }
    table[bandKey(band)] = perSeed;
  }
  return table;
}
