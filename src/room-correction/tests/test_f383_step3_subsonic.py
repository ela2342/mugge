"""Tests for the F-383 step-3 subsonic fix (F1-64) and the A1b generator check.

The subsonic now designs on a 64x grid at _LR_LOG_FLOOR (R6d A1). Every
crossover generator fail-closes on its output against the minimum-phase
FIR of its own design magnitude (A r4 A1b), scored by the A2 helper on its
own 16x grid at the generator's design-floor constant (R6d A4), for
filters of at least A1B_MIN_TAPS taps (Q4 bf088723).

Gated on the R6d 22 subsonic cases (A2 limits, grids per Q3 8cf30b4f): the
residual against the reference at 1024x and the generator's floor, the grid
convergence of that reference (1024x vs 2048x), tail, attenuation at hpf/2,
peak at tap 0 and the passband change against today's output. The stage
peak and the corner change are printed, not gated (A3).
"""

import functools
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from room_correction import crossover, dsp_utils, min_phase

SR = dsp_utils.SAMPLE_RATE
N = 16384
HPFS = (20.0, 25.0, 28.0, 35.0, 40.0, 42.0, 55.0, 80.0, 100.0, 200.0, 800.0)
SLOPES = (24.0, 48.0)
CASES = [(hpf, slope) for slope in SLOPES for hpf in HPFS]
CASE_IDS = [f"{hpf:.0f}Hz-{slope:.0f}dB" for hpf, slope in CASES]

M1_LIMIT_DB = -66.0
CONVERGENCE_LIMIT_DB = -100.0
TAIL_LIMIT_DB = -66.0
HALF_HPF_LIMIT_DB = -18.0
PASSBAND_CHANGE_LIMIT_DB = 0.1
GRID = 1 << 17
# Q3: a 256x grid does not resolve the 1e-20 floor of a 24 dB/oct knee
# (reached near hpf * 2^-16.7), so M1 reads the reference at 1024x.
M1_OVERSAMPLE = 1024
CONVERGENCE_OVERSAMPLE = 2048

FLOOR_MESSAGE = "design floor changed: needs an Architect + AE re-ruling of F-383 A1b/M1 (R6d A4)"
MIN_TAPS_MESSAGE = "A1b minimum length changed: needs Architect + AE re-ruling (F-383 Q4)"


def _design_vec(hpf, slope):
    """The legacy highpass knee of _design_crossover_magnitude, vectorised.

    The generator's own loop is too slow for the 1024x and 2048x grids;
    test_vectorised_design_matches pins this copy to it.
    """
    def design(f):
        m = np.ones_like(f, dtype=np.float64)
        sel = (f > 0) & (f < hpf)
        m[sel] = dsp_utils.db_to_linear(-slope * -np.log2(f[sel] / hpf))
        m[f <= 0] = 0.0
        return m
    return design


@functools.lru_cache(maxsize=None)
def _subsonic(hpf, slope):
    return crossover.generate_subsonic_filter(hpf, slope, n_taps=N, sr=SR)


@functools.lru_cache(maxsize=None)
def _legacy_subsonic(hpf, slope):
    """Today's subsonic (4n grid, legacy floor), rebuilt from the generator's pieces."""
    n_fft = dsp_utils.next_power_of_2(N * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / SR)
    magnitude = crossover._design_crossover_magnitude(freqs, hpf, 'highpass', slope)
    fir = crossover._magnitude_to_min_phase_fir(
        magnitude, n_fft, N, floor=crossover._LEGACY_LOG_FLOOR)
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(fir)
    mask = (passband_freqs >= hpf * 2) & (passband_freqs <= SR / 2 * 0.9)
    return fir / np.mean(passband_mag[mask])


def _dtft_db(h, f):
    k = np.arange(len(h))
    return float(20.0 * np.log10(abs(np.sum(h * np.exp(-2j * np.pi * f * k / SR)))))


def _grid_db(h):
    return 20.0 * np.log10(np.maximum(np.abs(np.fft.rfft(h, n=GRID)), 1e-300))


def _reference(h, design, oversample, floor_rel):
    """The A2 helper's minimum-phase reference for h, built from its own pieces."""
    n_fft = dsp_utils.next_power_of_2(oversample * len(h))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / SR)
    h_mag = np.abs(np.fft.rfft(h, n=n_fft))
    mag = min_phase._scaled_design(design, freqs, h_mag)
    return min_phase._cepstral_minimum_phase(
        np.maximum(mag, floor_rel * np.max(mag)), n_fft, len(h))


@functools.lru_cache(maxsize=None)
def _subsonic_reference(hpf, slope, oversample):
    """Each case's reference is built once per grid (Q3)."""
    return _reference(_subsonic(hpf, slope), _design_vec(hpf, slope), oversample,
                      crossover._LR_LOG_FLOOR)


def _residual_db(h, ref):
    """minimum_phase_residual_db()'s score of h against a given reference."""
    error = min(np.sum((h - ref) ** 2), np.sum((h + ref) ** 2))
    return float(10.0 * np.log10(max(error / np.sum(h ** 2), 1e-300)))


class TestFloorPin:
    """C1 (Architect 1a8e02ee): a floor change is a deliberate, reviewed act."""

    def test_floor_constants(self):
        assert crossover._LR_LOG_FLOOR == 1e-20, FLOOR_MESSAGE
        assert crossover._LEGACY_LOG_FLOOR == 1e-10, FLOOR_MESSAGE

    def test_subsonic_designs_and_checks_at_lr_floor(self, monkeypatch):
        synth, checks = [], []
        real_synth = crossover._magnitude_to_min_phase_fir
        real_check = min_phase.check_design_residual

        def spy_synth(magnitude, n_fft, n_taps, floor=crossover._LEGACY_LOG_FLOOR):
            synth.append((n_fft, floor))
            return real_synth(magnitude, n_fft, n_taps, floor=floor)

        def spy_check(h, design_mag, floor_rel, what, sr=SR):
            checks.append(floor_rel)
            return real_check(h, design_mag, floor_rel, what, sr=sr)

        monkeypatch.setattr(crossover, "_magnitude_to_min_phase_fir", spy_synth)
        monkeypatch.setattr(min_phase, "check_design_residual", spy_check)
        crossover.generate_subsonic_filter(40.0, 48.0, n_taps=N, sr=SR)
        assert synth == [(dsp_utils.next_power_of_2(N * crossover.SUBSONIC_DESIGN_OVERSAMPLE),
                          crossover._LR_LOG_FLOOR)], FLOOR_MESSAGE
        assert checks == [crossover._LR_LOG_FLOOR], FLOOR_MESSAGE
        assert crossover.SUBSONIC_DESIGN_OVERSAMPLE == 64


class TestMinTaps:
    """Q4 (Architect bf088723): A1b gates only at n_taps >= A1B_MIN_TAPS."""

    GENERATORS = {
        "subsonic": lambda n: crossover.generate_subsonic_filter(40.0, 48.0, n_taps=n),
        "crossover": lambda n: crossover.generate_crossover_filter('highpass', 80.0, 48.0, n_taps=n),
        "bandpass": lambda n: crossover.generate_bandpass_filter(100.0, 1000.0, n_taps=n),
    }

    @staticmethod
    def _residual_raises(monkeypatch):
        def residual(*args, **kwargs):
            raise RuntimeError("A1b residual computed")
        monkeypatch.setattr(min_phase, "minimum_phase_residual_db", residual)

    def test_min_taps_pin(self):
        assert min_phase.A1B_MIN_TAPS == 16384, MIN_TAPS_MESSAGE

    @pytest.mark.parametrize("n", [4096, 8192])
    @pytest.mark.parametrize("name", list(GENERATORS))
    def test_skipped_below_min(self, monkeypatch, caplog, name, n):
        self._residual_raises(monkeypatch)
        with caplog.at_level("INFO", logger=min_phase.__name__):
            fir = self.GENERATORS[name](n)
        assert len(fir) == n
        assert f"A1b skipped, {n} taps < A1B_MIN_TAPS {min_phase.A1B_MIN_TAPS}" in caplog.text

    @pytest.mark.parametrize("name", list(GENERATORS))
    def test_checked_at_min(self, monkeypatch, name):
        self._residual_raises(monkeypatch)
        with pytest.raises(RuntimeError, match="A1b residual computed"):
            self.GENERATORS[name](min_phase.A1B_MIN_TAPS)


class TestDesignCopy:

    @pytest.mark.parametrize("hpf,slope", CASES, ids=CASE_IDS)
    def test_vectorised_design_matches(self, hpf, slope):
        f = np.fft.rfftfreq(1 << 16, d=1.0 / SR)
        np.testing.assert_allclose(
            _design_vec(hpf, slope)(f),
            crossover._design_crossover_magnitude(f, hpf, 'highpass', slope),
            rtol=1e-12, atol=0)

    def test_legacy_rebuild_matches_phase0b_values(self):
        # r2 p1.out, variant (i): M7 at hpf/2 and A1b at 16x.
        for (hpf, slope), half, a1b in (((20.0, 24.0), -24.051, -61.0), ((40.0, 48.0), -46.606, -39.1)):
            h = _legacy_subsonic(hpf, slope)
            assert _dtft_db(h, hpf / 2) == pytest.approx(half, abs=5e-4)
            assert min_phase.minimum_phase_residual_db(
                h, design_mag=_design_vec(hpf, slope), oversample=16,
                floor_rel=crossover._LR_LOG_FLOOR) == pytest.approx(a1b, abs=0.05)


class TestSubsonicF1:
    """R6d A2 acceptance on the 22 cases."""

    def test_cached_reference_is_the_helpers(self):
        # M1 below scores against the cached reference; pin that to the
        # helper itself at one case, so there is no second implementation.
        h = _subsonic(20.0, 24.0)
        assert _residual_db(h, _subsonic_reference(20.0, 24.0, M1_OVERSAMPLE)) == \
            min_phase.minimum_phase_residual_db(
                h, design_mag=_design_vec(20.0, 24.0), oversample=M1_OVERSAMPLE,
                floor_rel=crossover._LR_LOG_FLOOR)

    @pytest.mark.parametrize("hpf,slope", CASES, ids=CASE_IDS)
    def test_residual_at_1024x(self, hpf, slope):
        # Q3 data: 20/24 is the closest, -69.8 dB at 1024x (-69.7 at 2048x).
        m1 = _residual_db(_subsonic(hpf, slope), _subsonic_reference(hpf, slope, M1_OVERSAMPLE))
        print(f"M1 1024x {hpf:.0f}/{slope:.0f}: {m1:.1f} dB")
        assert m1 <= M1_LIMIT_DB

    @pytest.mark.parametrize("hpf,slope", CASES, ids=CASE_IDS)
    def test_reference_converged(self, hpf, slope):
        ref = _subsonic_reference(hpf, slope, M1_OVERSAMPLE)
        finer = _subsonic_reference(hpf, slope, CONVERGENCE_OVERSAMPLE)
        conv = 10.0 * np.log10(max(np.sum((ref - finer) ** 2) / np.sum(finer ** 2), 1e-300))
        print(f"convergence 1024x vs 2048x {hpf:.0f}/{slope:.0f}: {conv:.1f} dB")
        assert conv <= CONVERGENCE_LIMIT_DB

    @pytest.mark.parametrize("hpf,slope", CASES, ids=CASE_IDS)
    def test_shape(self, hpf, slope):
        h = _subsonic(hpf, slope)
        legacy = _legacy_subsonic(hpf, slope)
        tail = min_phase.tail_peak_db(h)
        half = _dtft_db(h, hpf / 2)
        f = np.fft.rfftfreq(GRID, d=1.0 / SR)
        above = f >= 1.5 * hpf
        change = float(np.max(np.abs(_grid_db(h)[above] - _grid_db(legacy)[above])))
        peak = float(np.max(_grid_db(h)))
        corner = _dtft_db(h, hpf) - _dtft_db(legacy, hpf)
        print(f"{hpf:.0f}/{slope:.0f}: tail {tail:.1f} hpf/2 {half:.3f} max|dH| {change:.5f} "
              f"peak {peak:+.5f} (printed) d corner {corner:+.4f} (printed)")
        assert tail <= TAIL_LIMIT_DB
        assert half <= HALF_HPF_LIMIT_DB
        assert int(np.argmax(np.abs(h))) == 0
        assert change <= PASSBAND_CHANGE_LIMIT_DB


def _legacy_synthesis(monkeypatch):
    """Make generate_subsonic_filter synthesise as today: 4n grid, legacy floor."""
    real = crossover._magnitude_to_min_phase_fir

    def synth(magnitude, n_fft, n_taps, floor=crossover._LEGACY_LOG_FLOOR):
        n_fft4 = dsp_utils.next_power_of_2(n_taps * 4)
        return real(magnitude[::n_fft // n_fft4], n_fft4, n_taps, floor=crossover._LEGACY_LOG_FLOOR)
    monkeypatch.setattr(crossover, "_magnitude_to_min_phase_fir", synth)


class TestDesignCheck:
    """A r4 A1b: the generators fail closed."""

    def test_legacy_subsonic_raises(self, monkeypatch):
        # OBJ-1: today's subsonic at 40 Hz / 48 dB/oct, scored at the
        # subsonic's floor, sits just above the limit (r2: -39.1 dB).
        residual = min_phase.minimum_phase_residual_db(
            _legacy_subsonic(40.0, 48.0), design_mag=_design_vec(40.0, 48.0),
            oversample=min_phase.DESIGN_RESIDUAL_OVERSAMPLE, floor_rel=crossover._LR_LOG_FLOOR)
        print(f"legacy subsonic 40/48 at 16x: {residual:.2f} dB")
        assert residual > min_phase.DESIGN_RESIDUAL_LIMIT_DB
        _legacy_synthesis(monkeypatch)
        with pytest.raises(min_phase.MinimumPhaseError, match="subsonic 40.0 Hz"):
            crossover.generate_subsonic_filter(40.0, 48.0, n_taps=N, sr=SR)

    def test_legacy_synthesis_is_todays_output(self, monkeypatch):
        captured = []
        monkeypatch.setattr(min_phase, "check_design_residual",
                            lambda h, *a, **k: captured.append(h.copy()))
        _legacy_synthesis(monkeypatch)
        crossover.generate_subsonic_filter(40.0, 48.0, n_taps=N, sr=SR)
        np.testing.assert_array_equal(captured[0], _legacy_subsonic(40.0, 48.0))

    @pytest.mark.parametrize("call", [
        lambda: crossover.generate_crossover_filter(
            'lowpass', 80.0, 48.0, n_taps=N, alignment=crossover.LINKWITZ_RILEY),
        lambda: crossover.generate_crossover_filter('highpass', 80.0, 48.0, n_taps=N),
        lambda: crossover.generate_bandpass_filter(100.0, 1000.0, n_taps=N),
        lambda: crossover.generate_subsonic_filter(40.0, 48.0, n_taps=N),
    ], ids=["lr-lowpass", "legacy-highpass", "bandpass", "subsonic"])
    def test_time_reversed_output_raises(self, monkeypatch, call):
        real = crossover._magnitude_to_min_phase_fir
        monkeypatch.setattr(crossover, "_magnitude_to_min_phase_fir",
                            lambda *a, **k: real(*a, **k)[::-1].copy())
        with pytest.raises(min_phase.MinimumPhaseError):
            call()

    def test_floor_rule(self):
        # R6d A4: a legacy leg is scored at its own floor. Legacy LP 80/96
        # passes there (r2: -58.7) and fails at the LR floor.
        h = crossover.generate_crossover_filter('lowpass', 80.0, 96.0, n_taps=N)
        design = lambda f: crossover._design_crossover_magnitude(f, 80.0, 'lowpass', 96.0)
        own = min_phase.check_design_residual(h, design, crossover._log_floor(None), "LP 80/96")
        lr = min_phase.minimum_phase_residual_db(
            h, design_mag=design, oversample=min_phase.DESIGN_RESIDUAL_OVERSAMPLE,
            floor_rel=crossover._LR_LOG_FLOOR)
        print(f"legacy LP 80/96: own floor {own:.1f} dB, LR floor {lr:.1f} dB")
        assert crossover._log_floor(None) == crossover._LEGACY_LOG_FLOOR
        assert lr > min_phase.DESIGN_RESIDUAL_LIMIT_DB


def _legs():
    lr = crossover.LINKWITZ_RILEY
    for slope in (24.0, 48.0):
        for fc in (80.0, 200.0):
            for ft in ('highpass', 'lowpass'):
                yield f"lr{slope:.0f}-{ft}-{fc:.0f}", dict(filter_type=ft, crossover_freq=fc,
                                                           slope_db_per_oct=slope, alignment=lr)
    for slope in (48.0, 96.0):
        for fc in (80.0, 200.0):
            for ft in ('highpass', 'lowpass'):
                yield f"legacy{slope:.0f}-{ft}-{fc:.0f}", dict(filter_type=ft, crossover_freq=fc,
                                                               slope_db_per_oct=slope, alignment=None)


LEGS = list(_legs())
BANDS = [(lo, hi, align) for lo, hi in ((100.0, 1000.0), (300.0, 2000.0))
         for align in (None, crossover.LINKWITZ_RILEY)]


class TestCalibration:
    """Calibration values: every factor passes at its own floor."""

    @pytest.mark.parametrize("kw", [kw for _, kw in LEGS], ids=[name for name, _ in LEGS])
    def test_crossover_leg(self, kw):
        h = crossover.generate_crossover_filter(n_taps=N, **kw)
        design = lambda f: crossover._design_crossover_magnitude(
            f, kw['crossover_freq'], kw['filter_type'], kw['slope_db_per_oct'], kw['alignment'], SR)
        r = min_phase.check_design_residual(h, design, crossover._log_floor(kw['alignment']), "leg")
        print(f"A1b {kw}: {r:.1f} dB")

    @pytest.mark.parametrize("lo,hi,align", BANDS)
    def test_bandpass(self, lo, hi, align):
        slopes = (48.0, 96.0) if align is None else (48.0, 48.0)
        h = crossover.generate_bandpass_filter(lo, hi, *slopes, n_taps=N, alignment=align)
        design = lambda f: (crossover._design_crossover_magnitude(f, lo, 'highpass', slopes[0], align, SR)
                            * crossover._design_crossover_magnitude(f, hi, 'lowpass', slopes[1], align, SR))
        r = min_phase.check_design_residual(h, design, crossover._log_floor(align), "bandpass")
        print(f"A1b bandpass {lo:.0f}-{hi:.0f} {align}: {r:.1f} dB")

    @pytest.mark.parametrize("hpf,slope", CASES, ids=CASE_IDS)
    def test_subsonic(self, hpf, slope):
        r = min_phase.check_design_residual(
            _subsonic(hpf, slope), _design_vec(hpf, slope), crossover._LR_LOG_FLOOR, "subsonic")
        print(f"A1b subsonic {hpf:.0f}/{slope:.0f}: {r:.1f} dB")
