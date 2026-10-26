// Unit tests for crest-plan.js / crest.js / crest-table.js (US-179 AE A2, E2d).

import { assert, eq } from "./assert.js";
import { CREST_TABLE } from "../../../static/js/crest-table.js";
import {
  BASE_SEED, MAX_CHANNELS, bandKey, computeCrestTable, crestBands, crestSeed,
} from "../../../static/js/crest-plan.js";
import {
  CREST_MARGIN_DB, bandCeilingDbfs, crestEntry, levelCeilingDbfs, topStepDbfs,
  unitGain,
} from "../../../static/js/crest.js";
import { LevelNoise, LEVEL_NOISE } from "../../../static/js/dsp.js";
import { LIMITS, ROLE, levelNoiseBand } from "../../../static/js/safety.js";

const FULLRANGE = levelNoiseBand(ROLE.FULLRANGE, 80);

/** AE A2 CI re-check: every stored constant matches a fresh computation. */
export async function test_table_matches_recomputation() {
  const fresh = computeCrestTable();
  const keys = (o) => Object.keys(o).sort().join();
  eq(keys(CREST_TABLE), keys(fresh), "bands");
  for (const [band, perSeed] of Object.entries(fresh)) {
    eq(keys(CREST_TABLE[band]), keys(perSeed), band + " seeds");
    for (const [seed, e] of Object.entries(perSeed)) {
      const s = CREST_TABLE[band][seed];
      for (const k of ["rms", "peak", "crestDb"]) {
        const tol = 1e-9 * Math.max(1, Math.abs(e[k]));
        assert(Math.abs(s[k] - e[k]) <= tol,
          `${band} seed ${seed} ${k}: stored ${s[k]} vs ${e[k]}`);
      }
    }
  }
}

export async function test_plan_covers_every_role_band() {
  const keys = crestBands().map(bandKey);
  eq(keys.length, 32, "full-range + 31 subwoofer limits");
  assert(keys.includes("100-10000"), "full-range band");
  for (let hz = 20; hz <= 50; hz++) {
    assert(keys.includes(2 * hz + "-200"), "sub band for " + hz + " Hz");
  }
  eq(crestSeed(0), BASE_SEED, "channel 0 seed");
  eq(crestSeed(7), BASE_SEED ^ 7, "channel 7 seed");
  for (const bad of [-1, MAX_CHANNELS, 1.5, NaN]) {
    let threw = false;
    try { crestSeed(bad); } catch (e) { threw = true; }
    assert(threw, "channel " + bad + " rejected");
  }
  eq(LEVEL_NOISE.CREST_SECONDS >= 10, true, "crest over >= 10 s");
}

export async function test_missing_entry_means_no_sound() {
  eq(crestEntry({ lowHz: 41, highHz: 200 }, 0), null, "odd band");
  eq(crestEntry({ lowHz: 100, highHz: 20000 }, 0), null, "unknown band");
  assert(crestEntry(FULLRANGE, 0) !== null, "full-range ch 0");
  assert(crestEntry(levelNoiseBand(ROLE.SUBWOOFER, 50), 7) !== null, "sub ch 7");
}

export async function test_table_is_frozen() {
  assert(Object.isFrozen(CREST_TABLE), "table frozen");
  const e = crestEntry(FULLRANGE, 0);
  assert(Object.isFrozen(e), "entry frozen");
}

export async function test_ceiling_keeps_peak_under_cap() {
  eq(CREST_MARGIN_DB, 3, "margin");
  for (const band of crestBands()) {
    for (let ch = 0; ch < MAX_CHANNELS; ch++) {
      const e = crestEntry(band, ch);
      const ceiling = levelCeilingDbfs(e);
      eq(ceiling, LIMITS.OUTPUT_PEAK_CAP_DBFS - e.crestDb - 3, "formula");
      // RMS at the ceiling puts the measured peak 3 dB under the cap.
      const peakDb = 20 * Math.log10(unitGain(e, ceiling) * e.peak);
      assert(Math.abs(peakDb - (LIMITS.OUTPUT_PEAK_CAP_DBFS - 3)) < 1e-9,
        `${bandKey(band)} ch ${ch} peak ${peakDb}`);
    }
  }
}

export async function test_unit_gain_sets_output_rms() {
  const e = crestEntry(FULLRANGE, 0);
  const g = unitGain(e, -48);
  const src = new LevelNoise(crestSeed(0), LIMITS.REQUIRED_RATE, FULLRANGE);
  const n = LEVEL_NOISE.CREST_SECONDS * LIMITS.REQUIRED_RATE;
  let sumSq = 0;
  for (let i = 0; i < n; i++) {
    const v = g * src.nextSample();
    sumSq += v * v;
  }
  const rmsDb = 10 * Math.log10(sumSq / n);
  assert(Math.abs(rmsDb + 48) < 1e-9, "output RMS " + rmsDb);
}

export async function test_unit_gain_refuses_above_ceiling() {
  const e = crestEntry(FULLRANGE, 0);
  for (const lvl of [levelCeilingDbfs(e) + 0.01, -20, NaN]) {
    let threw = false;
    try { unitGain(e, lvl); } catch (err) { threw = true; }
    assert(threw, "level " + lvl + " refused");
  }
}

/** AE K5: one top step per band, from the band's largest crest. */
export async function test_top_step_uniform_per_band() {
  for (const band of crestBands()) {
    const perSeed = CREST_TABLE[bandKey(band)];
    const maxCrest = Math.max(...Object.values(perSeed).map((e) => e.crestDb));
    eq(bandCeilingDbfs(band), -20 - maxCrest - 3, bandKey(band));
    const top = topStepDbfs(band);
    eq((top - LIMITS.START_DBFS) % LIMITS.STEP_DB, 0, "on the step grid");
    assert(top <= bandCeilingDbfs(band), "at or below the band ceiling");
    assert(top + LIMITS.STEP_DB > bandCeilingDbfs(band), "highest such step");
    for (let ch = 0; ch < MAX_CHANNELS; ch++) {
      const e = crestEntry(band, ch);
      assert(top <= levelCeilingDbfs(e), "never above the per-seed ceiling");
      unitGain(e, top); // does not throw
    }
  }
  // With the current table (crest 10.77..13.23 dB) the full-range band
  // tops at -42.
  eq(topStepDbfs(FULLRANGE), -42);
  eq(bandCeilingDbfs({ lowHz: 1, highHz: 2 }), null, "unknown band");
  eq(topStepDbfs({ lowHz: 1, highHz: 2 }), null, "unknown band");
}
