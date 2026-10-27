"""F-383 C1: the correction's cepstral synthesis runs on a 4x finer grid.

On the design grid (n_fft = next_pow2(max(len, 2 n_taps))) the cepstrum
aliases, and some corrections miss A1a (residual -40 / tail -60 dB): 2 of 1000
white-noise seeds at 16384 taps uncapped (40, 578). The log floor is inert.
Steps 1-6 (smoothing, target, cut cap, design) stay on the design grid, bit
for bit; only step 7 interpolates the log magnitude onto a grid
SYNTH_GRID_FACTOR times finer for the cepstrum.

Ruling: Architect C1 r1 (f3286c42), AE release 6192482b; data worker-7 C1
report r1 (e2f9c7a6), variant D2c.

    R3a  synth_grid_factor 1 is f3c84c74's step 7, bit for bit.
    R3b  A1a passes at 16384, seeds 0..49 plus 578, uncapped and capped 18
         (ruling a1d2672f P3; the 1000-seed run is a PR attachment).
    R3c  the design is still met: |realised - design| p99 <= 0.02 dB.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from room_correction import correction, dsp_utils, min_phase
from room_correction import target_curves as tc
from room_correction.correction import (
    D009_MARGIN_DB,
    MAX_CUT_DB,
    SYNTH_GRID_FACTOR,
    generate_correction_filter,
)

SR = 48000
N_TAPS = 16384
# A1a limits on a correction (F-383 fence 041646b7).
A1A_MAX_RESIDUAL_DB = -40.0
A1A_MAX_TAIL_DB = -60.0
R3C_MAX_P99_DB = 0.02
R3C_BAND_HZ = (20.0, 20000.0)
# The two D1 fails before C1 (16384 uncapped); 40 is also inside 0..49.
R3B_REGRESSION_SEEDS = (40, 578)
R3B_SEEDS = sorted(set(range(50)) | set(R3B_REGRESSION_SEEDS))


def _random_ir(seed, n=N_TAPS):
    """test_d009_property._random_ir(np.random.RandomState(seed), n)."""
    ir = np.random.RandomState(seed).randn(n)
    return ir / np.max(np.abs(ir))


def _f3c84c74_unscaled(ir, n_taps, max_cut_db, margin_db=D009_MARGIN_DB, sr=SR):
    """Frozen copy of _unscaled_correction_filter at f3c84c74 (flat target).

    Returns (fir, design rfft freqs, design correction in dB).
    """
    ir = np.asarray(ir, dtype=np.float64)
    windowed_ir = dsp_utils.frequency_dependent_window(ir, sr=sr)
    n_fft = dsp_utils.next_power_of_2(max(len(windowed_ir), n_taps * 2))
    spectrum = np.fft.rfft(windowed_ir, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    smoothed_mag = dsp_utils.psychoacoustic_smooth(np.abs(spectrum), freqs)
    target_db = tc.get_target_curve('flat', freqs, target_phon=None, reference_phon=80.0)
    target_linear = dsp_utils.db_to_linear(target_db)
    correction_linear = target_linear / np.maximum(smoothed_mag, 1e-10)
    correction_db = dsp_utils.linear_to_db(correction_linear)
    correction_db = np.minimum(correction_db, margin_db)
    if max_cut_db is not None:
        correction_db = np.maximum(correction_db, -abs(max_cut_db))
    correction_linear = dsp_utils.db_to_linear(correction_db)
    log_mag_half = np.log(np.maximum(correction_linear, 1e-10))
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
    fir = np.fft.ifft(np.exp(np.fft.fft(cepstrum * causal_window))).real
    fir = fir[:n_taps]
    fir *= dsp_utils.fade_window(n_taps, 0, n_taps // 20)
    return fir, freqs, correction_db


def test_synth_grid_factor_is_4():
    assert SYNTH_GRID_FACTOR == 4


@pytest.mark.parametrize("seed", [0, 40, 578])
@pytest.mark.parametrize("max_cut_db", [None, MAX_CUT_DB])
def test_factor_1_is_f3c84c74_bit_for_bit(seed, max_cut_db):
    """R3a: k=1 reproduces the pre-C1 synthesis exactly."""
    ir = _random_ir(seed)
    old, _, _ = _f3c84c74_unscaled(ir, N_TAPS, max_cut_db)
    new = correction._unscaled_correction_filter(
        ir, n_taps=N_TAPS, max_cut_db=max_cut_db, synth_grid_factor=1)
    assert np.array_equal(new, old)


@pytest.mark.parametrize("seed", R3B_SEEDS)
@pytest.mark.parametrize("max_cut_db", [None, MAX_CUT_DB])
def test_correction_passes_a1a(seed, max_cut_db):
    """R3b: seeds 40 and 578 uncapped failed A1a before C1."""
    fir = generate_correction_filter(_random_ir(seed), n_taps=N_TAPS, max_cut_db=max_cut_db)
    assert min_phase.minimum_phase_residual_db(fir) <= A1A_MAX_RESIDUAL_DB
    assert min_phase.tail_peak_db(fir) <= A1A_MAX_TAIL_DB


@pytest.mark.parametrize("seed", range(20))
def test_design_magnitude_is_met(seed):
    """R3c: the FIR before the D-009 scalar realises the design on its grid."""
    ir = _random_ir(seed)
    _, freqs, design_db = _f3c84c74_unscaled(ir, N_TAPS, MAX_CUT_DB)
    fir = correction._unscaled_correction_filter(ir, n_taps=N_TAPS, max_cut_db=MAX_CUT_DB)
    realised_db = dsp_utils.linear_to_db(np.abs(np.fft.rfft(fir, n=2 * (len(freqs) - 1))))
    band = (freqs >= R3C_BAND_HZ[0]) & (freqs <= R3C_BAND_HZ[1])
    assert np.percentile(np.abs(realised_db - design_db)[band], 99) <= R3C_MAX_P99_DB
