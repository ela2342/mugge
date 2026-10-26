// dsp.js against scipy.signal.butter / sosfilt (fixtures/butter).

import { assert, close, eq, throws } from "./assert.js";
import {
  Cascade, LEVEL_NOISE, LevelNoise, butterworth, levelNoiseCrest,
} from "../../../static/js/dsp.js";

const FULLRANGE_BAND = { lowHz: 100, highHz: 10000 };

async function reference() {
  const resp = await fetch("/fixtures/butter/reference.json");
  assert(resp.ok, "reference.json " + resp.status);
  return resp.json();
}

function maxAbsDiff(a, b) {
  eq(a.length, b.length, "length");
  let worst = 0;
  for (let i = 0; i < a.length; i++) {
    worst = Math.max(worst, Math.abs(a[i] - b[i]));
  }
  return worst;
}

// scipy distributes the gain across sections differently, so the cascade
// is compared by its impulse response, not section by section.
export async function test_impulse_response_matches_scipy() {
  const ref = await reference();
  for (const d of ref.designs) {
    const sections = butterworth(d.kind, d.order, d.cutoff_hz, ref.sample_rate);
    eq(sections.length, d.order / 2, "sections");
    const c = new Cascade(sections);
    const out = d.impulse_response.map((_, i) => c.process(i === 0 ? 1 : 0));
    const err = maxAbsDiff(out, d.impulse_response);
    assert(err < 1e-12, `${d.kind} ${d.order} ${d.cutoff_hz} Hz: ${err}`);
  }
}

export async function test_level_noise_matches_scipy_on_the_pink_golden() {
  const ref = await reference();
  eq(ref.level_noise.length, 2, "full-range and subwoofer bands");
  for (const ln of ref.level_noise) {
    const src = new LevelNoise(ln.seed, ref.sample_rate, ln.band);
    const out = ln.output.map(() => src.nextSample());
    const err = maxAbsDiff(out, ln.output);
    assert(err < 1e-12, `level noise ${ln.band.lowHz}-${ln.band.highHz} Hz ` +
      "vs sosfilt: " + err);
  }
}

export async function test_reset_restores_initial_state() {
  const c = new Cascade(butterworth("highpass", 4, 100, 48000));
  const first = [1, 0, 0, 0].map((x) => c.process(x));
  c.reset();
  const again = [1, 0, 0, 0].map((x) => c.process(x));
  for (let i = 0; i < 4; i++) eq(again[i], first[i]);
}

export async function test_rejects_bad_designs() {
  throws(() => butterworth("highpass", 3, 100, 48000), "odd order");
  throws(() => butterworth("highpass", 0, 100, 48000), "order 0");
  throws(() => butterworth("highpass", 4, 0, 48000), "0 Hz");
  throws(() => butterworth("highpass", 4, 24000, 48000), "Nyquist");
  throws(() => butterworth("bandpass", 4, 100, 48000), "kind");
}

export async function test_level_noise_constants() {
  eq(LEVEL_NOISE.ORDER, 4);
  eq(LEVEL_NOISE.CREST_SECONDS, 10);
  assert(Object.isFrozen(LEVEL_NOISE));
  throws(() => new LevelNoise(174, 48000), "no band");
  throws(() => new LevelNoise(174, 48000, { lowHz: 200, highHz: 200 }));
}

export async function test_crest_is_deterministic_and_plausible() {
  const a = levelNoiseCrest(174, 48000, FULLRANGE_BAND, 1);
  const b = levelNoiseCrest(174, 48000, FULLRANGE_BAND, 1);
  eq(a.crestDb, b.crestDb, "same seed, same crest");
  close(a.peak / a.rms, 10 ** (a.crestDb / 20), 1e-9);
  // Gaussian-like band-limited noise over 48k samples: roughly 11-15 dB.
  assert(a.crestDb > 9 && a.crestDb < 18, "crest " + a.crestDb);
  assert(levelNoiseCrest(175, 48000, FULLRANGE_BAND, 1).crestDb !== a.crestDb,
    "seed matters");
}
