"""F-384: the D-009 step of generate_correction_filter is one cut-only scalar.

The old step 9 re-clipped the FIR's native rfft bins and kept their phase.
That bounds the native bins only, not the true (inter-bin) peak. Step 9 is now
one gain, sized on the B3 grid (full band 0 Hz - Nyquist, 8x), that never
boosts. A scalar keeps the FIR's shape, and so its minimum phase, exactly.
The full band matters: case A's unscaled FIR peaks at 9.5 Hz (-0.20 dB;
-0.12 dB before the F-383 C1 synthesis on the 4x grid), above its
20 Hz - 20 kHz peak (F-384 q2).

Ruling: Architect r2 (0221e6ed), AE release d5c4b28d, T5 note c70fccae;
full band per the q2 answer (7c6c86c3, AE a2946e74, fence r4 e016eb0b).
The tests check the property directly, not through a residual gate: the
residual gate passes the old step 9 at -98/-99 dB, so it cannot tell old from
new (worker-7 forced-input report r1, 92b75b51).

Fixed inputs (analytic, no randomness): a unit dirac of 48000 samples
through RBJ peaking biquads, flat target, margin -0.5 dB, max_cut_db 18.

    case A: (12, 18, 40), (20, 18, 40), (31, 18, 40)  (f0 Hz, +dB, Q), n_taps 16384
    case B: (40, 18, 20), n_taps 2048

Pre-fix numbers (worker-7 measure.out, source 4724e65d). pkNat = peak on the
native rfft grid, pk4x = combine.max_gain_db at 4x, pk2^17 = peak at 2^17
points, res4x / tail = phase-0 residual and tail (amplitude re peak), dB:

    case  stage        pkNat   pk4x    pk2^17  res4x  tail
    A     before st.9  -0.155  -0.258  -0.120  -98.5  -91.9
    A     old st.9     -0.500  -0.337  -0.102  -99.4  -91.0
    B     before st.9  +0.164  +0.164  +0.164  -90.7  -73.1
    B     old st.9     -0.500  +0.013  +0.025  -98.1  -78.0

The old step 9 fails T1 (it changes the shape) and T3 on both cases.
"""

import os
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.signal
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from room_correction import combine, correction, dsp_utils, min_phase
from room_correction.correction import (
    D009_MARGIN_DB,
    D009_SCALAR_OVERSAMPLE,
    MAX_CUT_DB,
    correction_from_measurement,
    generate_correction_filter,
    normalize_ir_level,
    reference_band,
)

SR = 48000
N_IR = 48000
REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"

CASES = {
    "A": dict(peaks=[(12, 18, 40), (20, 18, 40), (31, 18, 40)], n_taps=16384),
    "B": dict(peaks=[(40, 18, 20)], n_taps=2048),
}
# T5 (c70fccae): a no-op input sits at least 0.05 dB under the margin. A
# dirac at +6 dB gives a flat -6 dB correction (unscaled 8x peak -6.02 dB).
NO_OP_IR_GAIN = 2.0
NO_OP_MAX_PEAK_DB = D009_MARGIN_DB - 0.05
# T3b: the scaled FIR stays minimum phase on the A2 helper's own settings.
T3B_MAX_RESIDUAL_DB = -40.0
T3B_MAX_TAIL_DB = -60.0


def _peaking_eq(x, f0, gain_db, q, sr=SR):
    """RBJ cookbook peaking biquad applied to x (length preserved)."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2.0 * q)
    b = [1.0 + alpha * a, -2.0 * np.cos(w0), 1.0 - alpha * a]
    den = [1.0 + alpha / a, -2.0 * np.cos(w0), 1.0 - alpha / a]
    return scipy.signal.lfilter(b, den, x)


def _case_ir(name):
    x = np.zeros(N_IR)
    x[0] = 1.0
    for f0, gain_db, q in CASES[name]["peaks"]:
        x = _peaking_eq(x, f0, gain_db, q)
    return x


def _grid_peak_db(fir):
    return combine.max_gain_db(fir, sr=SR, oversample=D009_SCALAR_OVERSAMPLE, band=None)


def _fine_peak_db(fir):
    """Peak at 2^17 points, full band."""
    return float(dsp_utils.linear_to_db(np.max(np.abs(np.fft.rfft(fir, n=1 << 17)))))


def _scale_factor(out, unscaled):
    """k with out == k * unscaled, and the worst deviation re peak."""
    k = float(np.dot(out, unscaled) / np.dot(unscaled, unscaled))
    dev = float(np.max(np.abs(out - k * unscaled)) / np.max(np.abs(out)))
    return k, dev


def _assert_t1_t3(out, unscaled):
    k, dev = _scale_factor(out, unscaled)
    assert 0.0 < k <= 1.0, k                                  # T1: cut only
    assert dev <= 1e-12, dev                                  # T1: same shape
    assert _grid_peak_db(out) <= D009_MARGIN_DB + 1e-9        # T2
    assert _fine_peak_db(out) <= D009_MARGIN_DB + 0.01        # T3
    return k


def _speakers():
    with open(PROFILE) as f:
        return yaml.safe_load(f)["speakers"]


def test_scalar_grid_is_8x():
    assert D009_SCALAR_OVERSAMPLE == 8


@pytest.mark.parametrize("name", sorted(CASES))
class TestForcedOvershoot:
    """T1-T3 on the fixed inputs, through generate_correction_filter."""

    def test_unscaled_fir_overshoots(self, name):
        # The fixture still forces the branch: the FIR before step 9 peaks
        # above the margin on the scalar grid.
        unscaled = correction._unscaled_correction_filter(
            _case_ir(name), n_taps=CASES[name]["n_taps"], max_cut_db=MAX_CUT_DB)
        assert _grid_peak_db(unscaled) > D009_MARGIN_DB

    def test_output_is_scaled_unscaled_fir(self, name):
        ir = _case_ir(name)
        kw = dict(n_taps=CASES[name]["n_taps"], max_cut_db=MAX_CUT_DB)
        out = generate_correction_filter(ir, **kw)
        unscaled = correction._unscaled_correction_filter(ir, **kw)
        assert out.shape == (CASES[name]["n_taps"],)
        k = _assert_t1_t3(out, unscaled)
        assert k < 1.0

    def test_output_stays_minimum_phase(self, name):
        # T3b: A2 helper, own |H| as reference, A2 defaults.
        out = generate_correction_filter(
            _case_ir(name), n_taps=CASES[name]["n_taps"], max_cut_db=MAX_CUT_DB)
        assert min_phase.minimum_phase_residual_db(out, design_mag=None) <= T3B_MAX_RESIDUAL_DB
        assert min_phase.tail_peak_db(out) <= T3B_MAX_TAIL_DB


@pytest.mark.parametrize("spk", ["sat_left", "sub1"])
def test_public_path_scales_case_a(spk):
    """T4: case A through correction_from_measurement, Markaudio speaker dicts."""
    speaker = _speakers()[spk]
    ir = _case_ir("A")
    n_taps = CASES["A"]["n_taps"]
    out = correction_from_measurement(
        ir, speaker, target_curve="flat", n_taps=n_taps, sr=SR).fir
    normalized, _ = normalize_ir_level(ir, reference_band(speaker), sr=SR)
    unscaled = correction._unscaled_correction_filter(
        normalized, target_curve_name="flat", n_taps=n_taps, sr=SR,
        max_cut_db=MAX_CUT_DB)
    k = _assert_t1_t3(out, unscaled)
    assert k < 1.0


def test_no_op_is_bit_identical():
    """T5: an FIR already under the margin is returned unchanged (k == 1)."""
    ir = np.zeros(N_IR)
    ir[0] = NO_OP_IR_GAIN
    kw = dict(n_taps=16384, max_cut_db=MAX_CUT_DB)
    unscaled = correction._unscaled_correction_filter(ir, **kw)
    assert _grid_peak_db(unscaled) <= NO_OP_MAX_PEAK_DB
    out = generate_correction_filter(ir, **kw)
    assert np.array_equal(out, unscaled)


@pytest.mark.parametrize("name", sorted(CASES))
def test_return_scalar_db_reports_the_applied_cut(name):
    """S1 (1d3626b1): return_scalar_db gives the same FIR plus the applied scalar."""
    ir = _case_ir(name)
    kw = dict(n_taps=CASES[name]["n_taps"], max_cut_db=MAX_CUT_DB)
    fir, scalar_db = generate_correction_filter(ir, return_scalar_db=True, **kw)
    assert np.array_equal(fir, generate_correction_filter(ir, **kw))
    unscaled = correction._unscaled_correction_filter(ir, **kw)
    assert scalar_db < 0.0
    np.testing.assert_allclose(fir, unscaled * dsp_utils.db_to_linear(scalar_db), rtol=0, atol=0)


def test_return_scalar_db_is_zero_for_no_op():
    ir = np.zeros(N_IR)
    ir[0] = NO_OP_IR_GAIN
    _, scalar_db = generate_correction_filter(
        ir, n_taps=16384, max_cut_db=MAX_CUT_DB, return_scalar_db=True)
    assert scalar_db == 0.0


def test_correction_from_measurement_records_the_scalar():
    """S1b (q4, d0bd84c0): the public path stores the applied scalar."""
    speaker = _speakers()["sat_left"]
    ir = _case_ir("A")
    n_taps = CASES["A"]["n_taps"]
    shaped = correction_from_measurement(ir, speaker, target_curve="flat", n_taps=n_taps, sr=SR)
    normalized, _ = normalize_ir_level(ir, reference_band(speaker), sr=SR)
    fir, scalar_db = generate_correction_filter(
        normalized, target_curve_name="flat", n_taps=n_taps, sr=SR,
        max_cut_db=MAX_CUT_DB, return_scalar_db=True)
    assert np.array_equal(shaped.fir, fir)
    assert isinstance(shaped.d009_scalar_db, float)
    assert shaped.d009_scalar_db == scalar_db < 0.0


def test_hand_built_correction_has_no_scalar():
    # None, not 0.0: a hand-built filter does not know its scalar (d0bd84c0).
    c = correction.CorrectionFilter(fir=np.ones(4), reference_level_db=0.0,
                                    ref_band_hz=(400.0, 4000.0))
    assert c.d009_scalar_db is None


def test_non_finite_peak_raises():
    fir = np.zeros(1024)
    fir[3] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        correction._d009_scale(fir, D009_MARGIN_DB)


def _old_max_gain_db(fir, sr=SR, oversample=combine.D009_TRIM_OVERSAMPLE):
    """Frozen copy of combine.max_gain_db before the band parameter."""
    fir = np.asarray(fir, dtype=np.float64)
    n_fft = dsp_utils.next_power_of_2(len(fir)) * oversample
    mag = np.abs(np.fft.rfft(fir, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    band = (freqs >= 20) & (freqs <= 20000)
    return float(dsp_utils.linear_to_db(np.max(mag[band])))


@pytest.mark.parametrize("name", sorted(CASES))
@pytest.mark.parametrize("oversample", [combine.D009_TRIM_OVERSAMPLE, D009_SCALAR_OVERSAMPLE])
def test_max_gain_db_default_band_is_unchanged(name, oversample):
    """Band test (i): the default band gives the old value bit-identically."""
    unscaled = correction._unscaled_correction_filter(
        _case_ir(name), n_taps=CASES[name]["n_taps"], max_cut_db=MAX_CUT_DB)
    old = _old_max_gain_db(unscaled, oversample=oversample)
    assert combine.max_gain_db(unscaled, sr=SR, oversample=oversample) == old
    assert combine.max_gain_db(
        unscaled, sr=SR, oversample=oversample, band=(20.0, 20000.0)) == old


def test_max_gain_db_full_band_reads_sub_20_hz_peak():
    """Band test (ii): band=None on case A returns the 9.5 Hz peak (-0.20 dB).

    The level is -0.20 dB since F-383 C1 (synthesis on the 4x grid, ruling
    a1d2672f); it was -0.12 dB on the design grid.
    """
    unscaled = correction._unscaled_correction_filter(
        _case_ir("A"), n_taps=CASES["A"]["n_taps"], max_cut_db=MAX_CUT_DB)
    n_fft = dsp_utils.next_power_of_2(len(unscaled)) * combine.D009_TRIM_OVERSAMPLE
    mag = np.abs(np.fft.rfft(unscaled, n=n_fft))
    peak_hz = np.fft.rfftfreq(n_fft, d=1.0 / SR)[np.argmax(mag)]
    full = combine.max_gain_db(unscaled, sr=SR, band=None)
    assert peak_hz < 20.0
    assert full == float(dsp_utils.linear_to_db(np.max(mag)))
    assert full == pytest.approx(-0.20, abs=0.01)
    assert full >= combine.max_gain_db(unscaled, sr=SR)
    assert full > combine.max_gain_db(unscaled, sr=SR, band=(20.0, 20000.0))
    assert full > D009_MARGIN_DB  # the step-9 scalar still fires
