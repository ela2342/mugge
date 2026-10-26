"""Tests for the A2 minimum-phase residual helper (F-383 A2).

The helper's verdicts must come from its own settings: a minimum-phase
FIR scores low, a time-reversed (maximum-phase) one scores high, h and -h
score the same (polarity, ruling r2 R5), and a design magnitude is read
on the helper's own grid.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from room_correction import crossover, dsp_utils, min_phase

SR = dsp_utils.SAMPLE_RATE
PASS_DB = -40.0


def _lr4(filter_type, fc=80.0, n_taps=16384):
    return crossover.generate_crossover_filter(
        filter_type, crossover_freq=fc, slope_db_per_oct=24.0, n_taps=n_taps,
        alignment=crossover.LINKWITZ_RILEY)


def _lr4_design(filter_type, fc=80.0):
    return lambda f: crossover._design_crossover_magnitude(
        f, fc, filter_type, 24.0, crossover.LINKWITZ_RILEY, SR)


def _decaying_min_phase_fir(n=4096):
    """A two-pole resonance: minimum phase, decays far below the floor."""
    pole = 0.97 * np.exp(1j * 2 * np.pi * 1000.0 / SR)
    t = np.arange(n)
    return (pole ** t).real


class TestResidual:

    def test_min_phase_fir_passes(self):
        assert min_phase.minimum_phase_residual_db(_decaying_min_phase_fir()) <= PASS_DB

    def test_time_reversed_fir_fails(self):
        h = _decaying_min_phase_fir()
        assert min_phase.minimum_phase_residual_db(h[::-1]) > PASS_DB

    @pytest.mark.parametrize("filter_type", ["highpass", "lowpass"])
    def test_polarity_inverted_scores_the_same(self, filter_type):
        h = _lr4(filter_type)
        assert min_phase.minimum_phase_residual_db(-h) == \
            min_phase.minimum_phase_residual_db(h)
        design = _lr4_design(filter_type)
        assert min_phase.minimum_phase_residual_db(-h, design_mag=design) == \
            min_phase.minimum_phase_residual_db(h, design_mag=design)

    def test_gain_does_not_change_the_result(self):
        h = _lr4("highpass")
        ref = min_phase.minimum_phase_residual_db(h)
        assert min_phase.minimum_phase_residual_db(h * 1e-3) == pytest.approx(ref, abs=1e-6)
        design = _lr4_design("highpass")
        ref = min_phase.minimum_phase_residual_db(h, design_mag=design)
        assert min_phase.minimum_phase_residual_db(h * 1e-3, design_mag=design) == \
            pytest.approx(ref, abs=1e-6)


class TestDesignMagnitude:

    @pytest.mark.parametrize("filter_type", ["highpass", "lowpass"])
    def test_lr4_leg_matches_its_design(self, filter_type):
        h = _lr4(filter_type)
        assert min_phase.minimum_phase_residual_db(
            h, design_mag=_lr4_design(filter_type), oversample=16) <= PASS_DB

    def test_wrong_design_fails(self):
        h = _lr4("highpass", fc=80.0)
        assert min_phase.minimum_phase_residual_db(
            h, design_mag=_lr4_design("highpass", fc=200.0)) > PASS_DB

    def test_design_is_evaluated_on_the_helper_grid(self):
        h = _lr4("lowpass", n_taps=2048)
        seen = []

        def design(freqs):
            seen.append(freqs)
            return _lr4_design("lowpass")(freqs)

        min_phase.minimum_phase_residual_db(h, design_mag=design, oversample=4)
        assert len(seen) == 1
        n_fft = dsp_utils.next_power_of_2(4 * len(h))
        np.testing.assert_array_equal(seen[0], np.fft.rfftfreq(n_fft, d=1.0 / SR))

    def test_bad_design_shape_raises(self):
        with pytest.raises(ValueError, match="shape"):
            min_phase.minimum_phase_residual_db(
                _lr4("lowpass", n_taps=2048), design_mag=lambda f: np.ones(3))

    def test_design_without_passband_raises(self):
        with pytest.raises(ValueError, match="passband"):
            min_phase.minimum_phase_residual_db(
                _lr4("lowpass", n_taps=2048), design_mag=np.zeros_like)


class TestTail:

    def test_known_tail_level(self):
        h = np.zeros(1000)
        h[0] = -2.0
        h[-10] = 0.002
        assert min_phase.tail_peak_db(h) == pytest.approx(-60.0, abs=1e-9)

    def test_tail_outside_last_five_percent_is_ignored(self):
        h = np.zeros(1000)
        h[0] = 1.0
        h[940] = 0.5
        h[-1] = 1e-4
        assert min_phase.tail_peak_db(h) == pytest.approx(-80.0, abs=1e-9)


@pytest.mark.parametrize("bad", [
    np.zeros(16),
    np.array([1.0, np.nan]),
    np.ones((2, 8)),
    np.array([]),
])
def test_invalid_fir_raises(bad):
    with pytest.raises(ValueError):
        min_phase.minimum_phase_residual_db(bad)
    with pytest.raises(ValueError):
        min_phase.tail_peak_db(bad)
