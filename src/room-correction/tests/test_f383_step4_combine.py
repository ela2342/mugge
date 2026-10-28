"""Tests for the F-383 step-4 combine (fence c49a1500, AE 34348be3).

combine_filters() checks the correction input (A1a, fail-closed),
convolves the factors exactly, truncates with the fade, scales once by
s_dB = min(0, margin - peak) (B1, full band 8x per R3), and logs the
output tail, residual, scalar and peak (A1c log only per Q1, B2).
"""

import ast
import inspect
import logging
import os
import re
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import venue_sim
from room_correction import combine, correction, dsp_utils, min_phase
from room_correction import venue_pipeline as vp
from room_correction.combine import combine_filters
from room_correction.crossover import LINKWITZ_RILEY, generate_crossover_filter
from room_correction.generate_profile_filters import COMBINE_MARGIN_DB
from room_correction.min_phase import MinimumPhaseError

SR = 48000
N_TAPS = 16384
N_GRID = 1 << 17
REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES_DIR = REPO_ROOT / "configs" / "speakers" / "profiles"
MARKAUDIO_VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
MARKAUDIO = PROFILES_DIR / "2way-200hz-markaudio-ultimax.yml"
SCENARIOS = ["home_lab", "small_club", "large_hall", "outdoor_tent"]
LOG_LINE = re.compile(
    r"combined filter: tail (\S+) dB \(A1c, log only\), residual (\S+) dB, "
    r"scalar (\S+) dB, peak (\S+) dB")


def _dirac(n=N_TAPS):
    h = np.zeros(n)
    h[0] = 1.0
    return h


def _lr8(filter_type, fc):
    return generate_crossover_filter(filter_type, crossover_freq=fc, slope_db_per_oct=48.0,
                                     n_taps=N_TAPS, sr=SR, alignment=LINKWITZ_RILEY)


def _truncate_fade(product):
    h = np.zeros(N_TAPS)
    n = min(N_TAPS, len(product))
    h[:n] = product[:n]
    return h * dsp_utils.fade_window(N_TAPS, 0, N_TAPS // 20)


def _dtft(h, f):
    return complex(np.sum(h * np.exp(-2j * np.pi * f * np.arange(len(h)) / SR)))


def _db(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-300))


def _logged(caplog):
    return [tuple(float(v) for v in LOG_LINE.fullmatch(r.getMessage()).groups())
            for r in caplog.records
            if r.name == combine.__name__ and r.levelno == logging.INFO]


def _warnings(caplog):
    return [r for r in caplog.records
            if r.name == combine.__name__ and r.levelno == logging.WARNING]


def _home_lab_correction(speaker):
    bundle = vp.load_venue_bundle(MARKAUDIO_VENUE, MARKAUDIO)
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"),
        scenario_name="home_lab", noise_db=-60.0, noise_color="pink")
    return vp.generate_venue_filters(bundle, sim.measured_irs).corrections[speaker]


# -- Mechanism (R1, A4) -------------------------------------------------------

@pytest.mark.parametrize("fc", [80.0, 200.0])
def test_lr8_legs_sum_flat_in_phase(fc):
    """dirac x LR8: legs -6.02 dB at fc, in phase within 2.5 deg, sum flat."""
    hp = combine_filters(_dirac(), _lr8("highpass", fc), n_taps=N_TAPS,
                         margin_db=COMBINE_MARGIN_DB).astype(np.float32).astype(np.float64)
    lp = combine_filters(_dirac(), _lr8("lowpass", fc), n_taps=N_TAPS,
                         margin_db=COMBINE_MARGIN_DB).astype(np.float32).astype(np.float64)
    phase = abs(np.degrees(np.angle(_dtft(hp, fc) / _dtft(lp, fc))))
    freqs = np.fft.rfftfreq(N_GRID, d=1.0 / SR)
    hp_spec, lp_spec = np.fft.rfft(hp, N_GRID), np.fft.rfft(lp, N_GRID)
    hp_plat = np.mean(_db(hp_spec[(freqs >= 2 * fc) & (freqs <= 20000)]))
    lp_plat = np.mean(_db(lp_spec[(freqs >= 20) & (freqs <= fc / 2)]))
    band = (freqs >= fc / 2) & (freqs <= 2 * fc)
    sum_re_plat = _db(hp_spec[band] + lp_spec[band]) - (hp_plat + lp_plat) / 2
    print(f"LR8 {fc:g}: phase at fc {phase:.3f} deg, HP {_db(_dtft(hp, fc)) - hp_plat:.3f} dB, "
          f"LP {_db(_dtft(lp, fc)) - lp_plat:.3f} dB, sum {sum_re_plat.min():+.4f}.."
          f"{sum_re_plat.max():+.4f} dB, max|H| HP {_db(hp_spec).max():.4f} "
          f"LP {_db(lp_spec).max():.4f} dB")
    assert phase <= 2.5
    assert _db(_dtft(hp, fc)) - hp_plat == pytest.approx(-6.02, abs=0.02)
    assert _db(_dtft(lp, fc)) - lp_plat == pytest.approx(-6.02, abs=0.02)
    assert np.max(np.abs(sum_re_plat)) <= 0.01
    assert _db(hp_spec).max() == pytest.approx(COMBINE_MARGIN_DB, abs=1e-3)
    assert _db(lp_spec).max() == pytest.approx(COMBINE_MARGIN_DB, abs=1e-3)


def test_r3_full_band_peak_at_margin():
    """R3: dirac x LR8 80 LP at margin -0.5 peaks <= -0.5 dB, full band, 2^17 points."""
    h = combine_filters(_dirac(), _lr8("lowpass", 80.0), n_taps=N_TAPS, margin_db=-0.5)
    # 1e-9: the scalar lands the peak on the margin to the last ulp.
    assert _db(np.fft.rfft(h, N_GRID)).max() <= -0.5 + 1e-9


# -- B1: one cut-only scalar ---------------------------------------------------

def test_never_boosts(caplog):
    """A product below the margin comes back as the truncated, faded product."""
    xo = _lr8("lowpass", 80.0)
    c = 0.5 * _dirac()
    caplog.set_level(logging.INFO, logger=combine.__name__)
    h = combine_filters(c, xo, n_taps=N_TAPS, margin_db=COMBINE_MARGIN_DB)
    np.testing.assert_array_equal(h, _truncate_fade(dsp_utils.convolve_fir(c, xo)))
    assert _logged(caplog)[0][2] == 0.0


def test_overshoot_scaled_once(caplog):
    """An overshooting product is scaled by one gain: the shape is exact."""
    xo = _lr8("lowpass", 80.0)
    c = 2.0 * _dirac()
    caplog.set_level(logging.INFO, logger=combine.__name__)
    h = combine_filters(c, xo, n_taps=N_TAPS, margin_db=COMBINE_MARGIN_DB)
    ref = _truncate_fade(dsp_utils.convolve_fir(c, xo))
    scalar_db = COMBINE_MARGIN_DB - combine.max_gain_db(
        ref, oversample=combine.D009_SCALAR_OVERSAMPLE, band=None)
    assert scalar_db < -6.0
    np.testing.assert_allclose(h, ref * dsp_utils.db_to_linear(scalar_db), rtol=1e-12, atol=0)
    assert combine.max_gain_db(h, oversample=combine.D009_SCALAR_OVERSAMPLE,
                               band=None) == pytest.approx(COMBINE_MARGIN_DB, abs=1e-9)
    # Not bit-equal: the LR8 stopband reaches ~-325 dB, where rounding of
    # the scaled taps moves the cepstral reference by a few hundredths of a dB.
    assert min_phase.minimum_phase_residual_db(h) == pytest.approx(
        min_phase.minimum_phase_residual_db(ref), abs=0.1)
    assert _logged(caplog)[0][2] == pytest.approx(scalar_db, abs=1e-4)


def test_d009_scale_shared_with_correction():
    """F1: correction._d009_scale is combine.d009_scale, with the same error text."""
    fir = 3.0 * _lr8("lowpass", 80.0)
    assert correction.D009_SCALAR_OVERSAMPLE == combine.D009_SCALAR_OVERSAMPLE == 8
    a, a_db = correction._d009_scale(fir, -0.5)
    b, b_db = combine.d009_scale(fir, -0.5, what="correction filter")
    assert a_db == b_db < 0
    np.testing.assert_array_equal(a, b)
    below = 0.1 * fir
    same, zero = correction._d009_scale(below, -0.5)
    assert same is below and zero == 0.0
    with pytest.raises(ValueError, match="^correction filter has a non-finite peak gain$"):
        correction._d009_scale(np.full(16, np.inf), -0.5)


def test_min_phase_does_not_import_combine():
    """F1: import direction combine -> min_phase -> dsp_utils, never back."""
    tree = ast.parse(Path(min_phase.__file__).read_text())
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names}
    assert "combine" not in imported and "correction" not in imported


# -- B2: one INFO line per call, WARN when lossy --------------------------------

def test_b2_info_line_silent_on_lr(caplog):
    caplog.set_level(logging.INFO, logger=combine.__name__)
    combine_filters(_dirac(), _lr8("highpass", 80.0), n_taps=N_TAPS,
                    margin_db=COMBINE_MARGIN_DB)
    assert len(_logged(caplog)) == 1
    assert not _warnings(caplog)


def test_b2_warns_when_lossy(caplog):
    """The final peak more than 0.1 dB below the margin is a WARN."""
    caplog.set_level(logging.INFO, logger=combine.__name__)
    combine_filters(0.5 * _dirac(), _lr8("highpass", 80.0), n_taps=N_TAPS,
                    margin_db=COMBINE_MARGIN_DB)
    (tail, residual, scalar, peak), = _logged(caplog)
    assert scalar == 0.0 and peak == pytest.approx(-6.02, abs=0.01)
    assert len(_warnings(caplog)) == 1
    assert "below the margin" in _warnings(caplog)[0].getMessage()


# -- A1a: the correction input, fail-closed -------------------------------------

def _min_phase_correction():
    """A minimum-phase correction: geometric decay, zero at |z| = 0.99."""
    return 0.99 ** np.arange(N_TAPS)


@pytest.mark.parametrize("bad", [
    lambda: np.roll(_dirac(), 100),
    lambda: _min_phase_correction()[:2048][::-1].copy(),
], ids=["delayed-dirac", "time-reversed"])
def test_a1a_non_minimum_phase_raises(bad):
    with pytest.raises(MinimumPhaseError, match="residual"):
        combine_filters(bad(), _lr8("lowpass", 80.0), n_taps=N_TAPS)


def test_a1a_tail_raises_on_tail():
    """F4: truncated a^k with a^N = 1e-2 is minimum phase; its tail is ~-40 dB."""
    a = 1e-2 ** (1.0 / N_TAPS)
    c = a ** np.arange(N_TAPS)
    assert min_phase.minimum_phase_residual_db(c) <= min_phase.INPUT_RESIDUAL_LIMIT_DB
    with pytest.raises(MinimumPhaseError) as raised:
        combine_filters(c, _lr8("lowpass", 80.0), n_taps=N_TAPS)
    message = str(raised.value)
    assert "tail" in message and "residual" not in message
    assert "correction" in message and "-60" in message


@pytest.mark.parametrize("make", [_dirac, lambda: _home_lab_correction("sub1")],
                         ids=["dirac", "home_lab-sub1"])
def test_a1a_passes(make):
    c = make()
    assert min_phase.minimum_phase_residual_db(c) <= min_phase.INPUT_RESIDUAL_LIMIT_DB
    assert min_phase.tail_peak_db(c) <= min_phase.TAIL_LIMIT_DB
    combine_filters(c, _lr8("lowpass", 80.0), n_taps=N_TAPS)


def test_a1a_limits():
    assert min_phase.INPUT_RESIDUAL_LIMIT_DB == -40.0
    assert min_phase.TAIL_LIMIT_DB == -60.0


# -- A1c: output tail and residual, logged only (Q1) ----------------------------

def test_a1c_synthetic_tail_logged(caplog):
    """A correction that passes A1a at its length, combined to a quarter of it."""
    c = (1e-4 ** (1.0 / N_TAPS)) ** np.arange(N_TAPS)
    caplog.set_level(logging.INFO, logger=combine.__name__)
    h = combine_filters(c, _dirac(), n_taps=N_TAPS // 4, margin_db=COMBINE_MARGIN_DB)
    (tail, residual, _, _), = _logged(caplog)
    assert tail > min_phase.TAIL_LIMIT_DB
    assert tail == pytest.approx(combine.output_min_phase_db(h)[0], abs=0.05)
    assert residual == pytest.approx(combine.output_min_phase_db(h)[1], abs=0.05)


def test_a1c_natural_tail_logged(caplog):
    """R4: LR8 80 LP x home_lab sub1 correction; the product outlasts n (info)."""
    correction_fir = _home_lab_correction("sub1")
    caplog.set_level(logging.INFO, logger=combine.__name__)
    h = combine_filters(correction_fir, _lr8("lowpass", 80.0), n_taps=N_TAPS,
                        margin_db=COMBINE_MARGIN_DB)
    (tail, residual, scalar, peak), = _logged(caplog)
    print(f"R4 natural A1c: tail {tail} dB, residual {residual} dB, scalar {scalar} dB, "
          f"peak {peak} dB")
    assert tail == pytest.approx(combine.output_min_phase_db(h)[0], abs=0.05)


def test_output_residual_logged_not_gated(caplog):
    """The dirac x LR8 80 LP output residual is far above -40 dB; it never raises."""
    caplog.set_level(logging.INFO, logger=combine.__name__)
    combine_filters(_dirac(), _lr8("lowpass", 80.0), n_taps=N_TAPS, margin_db=COMBINE_MARGIN_DB)
    (_, residual, _, _), = _logged(caplog)
    assert residual > min_phase.INPUT_RESIDUAL_LIMIT_DB


# -- Signature, A4 calibration ---------------------------------------------------

def test_signature_pinned():
    params = inspect.signature(combine_filters).parameters
    assert [(p.name, p.default) for p in params.values()] == [
        ("correction_filter", inspect.Parameter.empty),
        ("crossover_filter", inspect.Parameter.empty),
        ("n_taps", 16384), ("margin_db", -0.5), ("subsonic_filter", None)]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_a4_markaudio_calibration(caplog, scenario):
    """A4 (report only): markaudio LR4 x the four scenarios, one line per channel."""
    bundle = vp.load_venue_bundle(MARKAUDIO_VENUE, MARKAUDIO)
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario(scenario),
        scenario_name=scenario, noise_db=-60.0, noise_color="pink")
    caplog.set_level(logging.INFO, logger=combine.__name__)
    vp.generate_venue_filters(bundle, sim.measured_irs)
    logged = _logged(caplog)
    assert len(logged) == len(bundle.profile["speakers"])
    for spk, (tail, residual, scalar, peak) in zip(bundle.profile["speakers"], logged):
        print(f"A4 markaudio {scenario} {spk}: scalar {scalar:+.4f} dB, peak {peak:.4f} dB, "
              f"tail {tail:.1f} dB, residual {residual:.1f} dB")
