"""Tests for the Linkwitz-Riley crossover alignment (F-374).

The acceptance criteria are measured on exported float32 WAVs read back
from disk: legs -6 +-0.5 dB at fc, HP+LP complex sum +-1 dB over
20 Hz-20 kHz, |phase(HP) - phase(LP)| <= 10 deg over fc/2..2fc, at
24 and 48 dB/oct and 80 and 200 Hz.  Tighter regression guards: LR4 sum
+-0.05 dB, LR8 sum +-0.1 dB, LR4 and LR8 phase at fc <= 5 deg.

The legacy path (alignment=None) must stay byte-identical; it is checked
against a frozen copy of the pre-F-374 implementation below.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from room_correction import crossover, dsp_utils
from room_correction.export import export_filter
from room_correction.verify import load_filter

LR = crossover.LINKWITZ_RILEY
SR = dsp_utils.SAMPLE_RATE
N_TAPS = 16384
ANALYSIS_FFT = 1 << 17

LEG_DB, LEG_TOL_DB = -6.0, 0.5
SUM_AC_DB = 1.0
PHASE_AC_DEG = 10.0
SUM_GUARD_DB = {24: 0.05, 48: 0.1}
PHASE_AT_FC_DEG = 5.0


def _export_roundtrip(fir, directory, name):
    path = os.path.join(directory, f"{name}.wav")
    export_filter(fir, path, n_taps=len(fir), sr=SR)
    data, _ = load_filter(path)
    return data


def _spectrum(fir):
    freqs = np.fft.rfftfreq(ANALYSIS_FFT, d=1.0 / SR)
    return freqs, np.fft.rfft(fir, n=ANALYSIS_FFT)


def _measure_pair(hp, lp, fc):
    """Return (hp_db_at_fc, lp_db_at_fc, sum_min_db, sum_max_db,
    max_phase_deg over fc/2..2fc, phase_deg_at_fc)."""
    freqs, h = _spectrum(hp)
    _, l = _spectrum(lp)
    i = np.argmin(np.abs(freqs - fc))
    band = (freqs >= 20) & (freqs <= 20000)
    near = (freqs >= fc / 2) & (freqs <= 2 * fc)
    sum_db = 20 * np.log10(np.abs(h + l)[band])
    phase = np.degrees(np.abs(np.angle(h[near] / l[near])))
    return (
        20 * np.log10(np.abs(h[i])),
        20 * np.log10(np.abs(l[i])),
        sum_db.min(),
        sum_db.max(),
        phase.max(),
        np.degrees(np.abs(np.angle(h[i] / l[i]))),
    )


# ---------------------------------------------------------------------------
# Frozen pre-F-374 reference (legacy byte-identity)
# ---------------------------------------------------------------------------

def _ref_magnitude(freqs, crossover_freq, filter_type, slope_db_per_oct):
    magnitude = np.ones_like(freqs, dtype=np.float64)
    for i, f in enumerate(freqs):
        if f <= 0:
            if filter_type == 'highpass':
                magnitude[i] = 0.0
            continue
        ratio = f / crossover_freq
        if filter_type == 'highpass':
            if ratio < 1.0:
                octaves_below = -np.log2(ratio)
                attenuation_db = slope_db_per_oct * octaves_below
                magnitude[i] = dsp_utils.db_to_linear(-attenuation_db)
        elif filter_type == 'lowpass':
            if ratio > 1.0:
                octaves_above = np.log2(ratio)
                attenuation_db = slope_db_per_oct * octaves_above
                magnitude[i] = dsp_utils.db_to_linear(-attenuation_db)
    return magnitude


def _ref_min_phase(magnitude, n_fft, n_taps):
    log_mag_half = np.log(np.maximum(magnitude, 1e-10))
    log_mag_full = np.zeros(n_fft, dtype=np.float64)
    log_mag_full[:len(log_mag_half)] = log_mag_half
    log_mag_full[len(log_mag_half):] = log_mag_half[-2:0:-1]
    cepstrum = np.fft.ifft(log_mag_full).real
    n_half = n_fft // 2
    causal_window = np.zeros(n_fft)
    causal_window[0] = 1.0
    causal_window[1:n_half] = 2.0
    if n_fft % 2 == 0:
        causal_window[n_half] = 1.0
    min_phase_spectrum = np.exp(np.fft.fft(cepstrum * causal_window))
    fir = np.fft.ifft(min_phase_spectrum).real
    fir = fir[:n_taps]
    fir *= dsp_utils.fade_window(n_taps, 0, n_taps // 20)
    return fir


def _ref_normalise(fir, lo, hi):
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(fir)
    mask = (passband_freqs >= lo) & (passband_freqs <= hi)
    if np.any(mask):
        passband_level = np.mean(passband_mag[mask])
        if passband_level > 0:
            fir /= passband_level
    return fir


def _ref_crossover(filter_type, fc, slope, n_taps, sr=SR):
    n_fft = dsp_utils.next_power_of_2(n_taps * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    fir = _ref_min_phase(_ref_magnitude(freqs, fc, filter_type, slope), n_fft, n_taps)
    if filter_type == 'highpass':
        return _ref_normalise(fir, fc * 2, sr / 2 * 0.9)
    return _ref_normalise(fir, 20, fc * 0.5)


def _ref_bandpass(low, high, low_slope, high_slope, n_taps, sr=SR):
    n_fft = dsp_utils.next_power_of_2(n_taps * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    magnitude = (_ref_magnitude(freqs, low, 'highpass', low_slope)
                 * _ref_magnitude(freqs, high, 'lowpass', high_slope))
    fir = _ref_min_phase(magnitude, n_fft, n_taps)
    center = np.sqrt(low * high)
    lo = max(low * 1.5, center * 0.7)
    hi = min(high * 0.67, center * 1.4)
    if lo >= hi:
        lo, hi = low * 1.2, high * 0.8
    return _ref_normalise(fir, lo, hi)


class TestLegacyByteIdentical(unittest.TestCase):
    """alignment=None reproduces the pre-F-374 output exactly."""

    def test_highpass_lowpass(self):
        for filter_type in ('highpass', 'lowpass'):
            for fc in (80.0, 200.0):
                for slope in (24.0, 48.0, 96.0):
                    with self.subTest(filter_type=filter_type, fc=fc, slope=slope):
                        new = crossover.generate_crossover_filter(
                            filter_type, fc, slope, n_taps=4096)
                        ref = _ref_crossover(filter_type, fc, slope, 4096)
                        self.assertTrue(np.array_equal(new, ref))

    def test_production_length(self):
        new = crossover.generate_crossover_filter('highpass', 80.0, 48.0, n_taps=N_TAPS)
        self.assertTrue(np.array_equal(new, _ref_crossover('highpass', 80.0, 48.0, N_TAPS)))

    def test_bandpass(self):
        new = crossover.generate_bandpass_filter(300, 2000, 48.0, 96.0, n_taps=4096)
        ref = _ref_bandpass(300, 2000, 48.0, 96.0, 4096)
        self.assertTrue(np.array_equal(new, ref))

    def test_explicit_none_equals_default(self):
        a = crossover.generate_crossover_filter('lowpass', 80.0, 48.0, n_taps=4096)
        b = crossover.generate_crossover_filter(
            'lowpass', 80.0, 48.0, n_taps=4096, alignment=None)
        self.assertTrue(np.array_equal(a, b))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestAlignmentValidation(unittest.TestCase):

    def test_unknown_alignment_raises(self):
        with self.assertRaises(ValueError):
            crossover.generate_crossover_filter(
                'highpass', 80.0, 48.0, n_taps=1024, alignment='butterworth')

    def test_unsupported_lr_slope_raises(self):
        for slope in (12.0, 36.0, 96.0):
            with self.subTest(slope=slope):
                with self.assertRaisesRegex(ValueError, "24 or 48 dB/oct"):
                    crossover.generate_crossover_filter(
                        'lowpass', 80.0, slope, n_taps=1024, alignment=LR)

    def test_bandpass_checks_both_edges(self):
        with self.assertRaises(ValueError):
            crossover.generate_bandpass_filter(
                300, 2000, 48.0, 96.0, n_taps=1024, alignment=LR)
        with self.assertRaises(ValueError):
            crossover.generate_bandpass_filter(
                300, 2000, 36.0, 48.0, n_taps=1024, alignment=LR)

    def test_bandpass_via_crossover_filter_passes_alignment(self):
        with self.assertRaises(ValueError):
            crossover.generate_crossover_filter(
                'bandpass', 300, 48.0, n_taps=1024, crossover_freq_high=2000,
                high_slope_db_per_oct=96.0, alignment=LR)

    def test_legacy_accepts_any_slope(self):
        fir = crossover.generate_crossover_filter('lowpass', 80.0, 96.0, n_taps=1024)
        self.assertTrue(np.all(np.isfinite(fir)))

    def test_integer_slopes_accepted(self):
        fir = crossover.generate_crossover_filter(
            'highpass', 80, 24, n_taps=1024, alignment=LR)
        self.assertTrue(np.all(np.isfinite(fir)))


# ---------------------------------------------------------------------------
# Acceptance criteria on exported WAVs
# ---------------------------------------------------------------------------

class TestLinkwitzRileyPair(unittest.TestCase):
    """LR4/LR8 HP+LP pairs, exported to float32 WAV and read back."""

    @classmethod
    def setUpClass(cls):
        cls.results = {}
        with tempfile.TemporaryDirectory() as d:
            for slope in (24, 48):
                for fc in (80.0, 200.0):
                    pair = {}
                    for ft in ('highpass', 'lowpass'):
                        fir = crossover.generate_crossover_filter(
                            ft, fc, slope, n_taps=N_TAPS, alignment=LR)
                        pair[ft] = _export_roundtrip(fir, d, f"{ft}_{slope}_{int(fc)}")
                    cls.results[(slope, fc)] = (pair, _measure_pair(
                        pair['highpass'], pair['lowpass'], fc))
        for (slope, fc), (_, m) in sorted(cls.results.items()):
            print(f"LR{slope // 6} {slope} dB/oct fc={fc:.0f}: "
                  f"HP {m[0]:.2f} dB, LP {m[1]:.2f} dB at fc; "
                  f"sum {m[2]:.3f}..{m[3]:.3f} dB; "
                  f"phase max {m[4]:.2f} deg (fc/2..2fc), {m[5]:.2f} deg at fc")

    def _each(self):
        for key, (pair, m) in sorted(self.results.items()):
            with self.subTest(slope=key[0], fc=key[1]):
                yield key, pair, m

    def test_legs_minus_6db_at_fc(self):
        for _, _, m in self._each():
            self.assertAlmostEqual(m[0], LEG_DB, delta=LEG_TOL_DB)
            self.assertAlmostEqual(m[1], LEG_DB, delta=LEG_TOL_DB)

    def test_sum_flat_ac(self):
        for _, _, m in self._each():
            self.assertGreaterEqual(m[2], -SUM_AC_DB)
            self.assertLessEqual(m[3], SUM_AC_DB)

    def test_sum_flat_guard(self):
        for (slope, _), _, m in self._each():
            self.assertGreaterEqual(m[2], -SUM_GUARD_DB[slope])
            self.assertLessEqual(m[3], SUM_GUARD_DB[slope])

    def test_phase_tracking_near_fc(self):
        for _, _, m in self._each():
            self.assertLessEqual(m[4], PHASE_AC_DEG)

    def test_phase_at_fc(self):
        for _, _, m in self._each():
            self.assertLessEqual(m[5], PHASE_AT_FC_DEG)

    def test_finite_and_minimum_phase(self):
        for _, pair, _ in self._each():
            for fir in pair.values():
                self.assertTrue(np.all(np.isfinite(fir)))
                energy = np.cumsum(fir ** 2)
                # Minimum phase: energy is front-loaded.
                self.assertGreater(energy[len(fir) // 10] / energy[-1], 0.99)

    def test_differs_from_legacy(self):
        legacy = crossover.generate_crossover_filter('highpass', 200.0, 24, n_taps=N_TAPS)
        lr = crossover.generate_crossover_filter(
            'highpass', 200.0, 24, n_taps=N_TAPS, alignment=LR)
        self.assertFalse(np.allclose(legacy, lr))


class TestLinkwitzRileyBandpass(unittest.TestCase):
    """Both bandpass edges are LR and sum with the adjacent legs."""

    def test_edges_minus_6db(self):
        low, high = 300.0, 2000.0
        bp = crossover.generate_bandpass_filter(
            low, high, 48, 48, n_taps=N_TAPS, alignment=LR)
        freqs, h = _spectrum(bp)
        for edge in (low, high):
            i = np.argmin(np.abs(freqs - edge))
            self.assertAlmostEqual(20 * np.log10(np.abs(h[i])), LEG_DB, delta=LEG_TOL_DB)


class TestThreeWaySumReport(unittest.TestCase):
    """3-way LP + BP + HP sum, reported only (no gate)."""

    def test_report(self):
        for name, (f1, f2) in (("meh-3way-template", (300.0, 2000.0)),
                               ("workshop-c3d-elf-3way", (100.0, 1000.0))):
            lp = crossover.generate_crossover_filter(
                'lowpass', f1, 48, n_taps=N_TAPS, alignment=LR)
            bp = crossover.generate_bandpass_filter(
                f1, f2, 48, 48, n_taps=N_TAPS, alignment=LR)
            hp = crossover.generate_crossover_filter(
                'highpass', f2, 48, n_taps=N_TAPS, alignment=LR)
            freqs, total = _spectrum(lp + bp + hp)
            band = (freqs >= 20) & (freqs <= 20000)
            sum_db = 20 * np.log10(np.abs(total[band]))
            print(f"3-way {name} [{f1:.0f}, {f2:.0f}] LR8: "
                  f"sum {sum_db.min():.2f}..{sum_db.max():.2f} dB (report only)")
            self.assertTrue(np.all(np.isfinite(sum_db)))


if __name__ == "__main__":
    unittest.main()
