// crest.js -- level-check output ceiling and gain from the stored crest
// factors (US-179 AE A2, AC4c, E2d, AE K5 1318b25c).
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
 * AE K5: the level-check ceiling is uniform per band, from the largest
 * crest over all seeds of that band, so every channel of a band gets the
 * same top step. Null if the band is not in the table (no sound).
 */
export function bandCeilingDbfs(band) {
  const perSeed = CREST_TABLE[bandKey(band)];
  if (!perSeed) return null;
  const crests = Object.values(perSeed).map((e) => e.crestDb);
  if (crests.length === 0) return null;
  return LIMITS.OUTPUT_PEAK_CAP_DBFS - Math.max(...crests) - CREST_MARGIN_DB;
}

/**
 * AE K5: the highest level-check step (START_DBFS + n * STEP_DB) at or
 * below the band ceiling. Null if no step fits or the band is unknown.
 */
export function topStepDbfs(band) {
  const ceiling = bandCeilingDbfs(band);
  if (ceiling === null || ceiling < LIMITS.START_DBFS) return null;
  const n = Math.floor((ceiling - LIMITS.START_DBFS) / LIMITS.STEP_DB);
  return LIMITS.START_DBFS + n * LIMITS.STEP_DB;
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
