// crest.js -- level-check output ceiling and gain from the stored crest
// factors (US-179 AE A2, AC4c, E2d).
//
// Levels are the output RMS of the band-limited noise (AE A2). The RMS
// ceiling keeps the peak 3 dB under the -20 dBFS cap:
//   ceiling = OUTPUT_PEAK_CAP_DBFS - crestDb - CREST_MARGIN_DB.
// No table entry for the band and channel means no sound.

import { CREST_TABLE } from "./crest-table.js";
import { bandKey, crestSeed } from "./crest-plan.js";
import { LIMITS, dbToLinear } from "./safety.js";

export const CREST_MARGIN_DB = 3;

/** Stored { rms, peak, crestDb } for a band and output channel, or null. */
export function crestEntry(band, channelIndex) {
  const perSeed = CREST_TABLE[bandKey(band)];
  if (!perSeed) return null;
  return perSeed[String(crestSeed(channelIndex))] || null;
}

/** Highest allowed level-check RMS (dBFS) for this entry. */
export function levelCeilingDbfs(entry) {
  return LIMITS.OUTPUT_PEAK_CAP_DBFS - entry.crestDb - CREST_MARGIN_DB;
}

/**
 * Linear gain that brings the unit-level noise to `levelDbfs` output RMS.
 * Refuses levels above the ceiling.
 */
export function unitGain(entry, levelDbfs) {
  if (!(levelDbfs <= levelCeilingDbfs(entry))) {
    throw new RangeError("level " + levelDbfs + " dBFS above the ceiling");
  }
  return dbToLinear(levelDbfs) / entry.rms;
}
