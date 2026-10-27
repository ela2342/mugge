"""Tests for the F-383 step-4b composition row (C3, Architect ace87e0d).

channel_factors() is the one source of the factors combine multiplies;
is_cascade() names the channels (crossover LP or bandpass + subsonic)
that get the composition row. verify_minimum_phase_composition() compares
the filter with the exact product of its factors: residual <= -30 dB,
g > 0 (polarity), g <= 1 + 1e-3 (boost), plus the residual row's tail and
decay conditions.

Until the step-4 combine commit, CASCADE_GATE_ROW = "residual": the
residual row still gates every 'fir' file, and on cascade channels it
carries the composition numbers in details["composition"] (log only).
These tests do not depend on the combine: the composition-row inputs are
built from IIR factors (minimum phase by construction).
"""

import os
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.signal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config_generator
from mock import venue_sim
from room_correction import dsp_utils, verify
from room_correction import generate_profile_filters as gpf
from room_correction import venue_pipeline as vp
from room_correction.combine import combine_filters
from room_correction.export import export_filter

SR = 48000
N_TAPS = 16384
REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES_DIR = REPO_ROOT / "configs" / "speakers" / "profiles"
VENUE = REPO_ROOT / "configs" / "venues" / "production.yml"
UNBUILDABLE = {"2way-80hz-ported", "workshop-xrk10f-fullrange"}
PROFILES = sorted(p.stem for p in PROFILES_DIR.glob("*.yml") if p.stem not in UNBUILDABLE)


def _load(name):
    return config_generator.load_profile_with_identities(name)


def _iir(sos):
    h = np.zeros(N_TAPS)
    h[0] = 1.0
    return scipy.signal.sosfilt(sos, h)


def _butter(order, hz, btype):
    return scipy.signal.butter(order, hz, btype, fs=SR, output="sos")


def _cascade_factors(hpf_hz):
    """Dirac correction x BW8 LP80 x BW8 HPF, each minimum phase."""
    dirac = np.zeros(N_TAPS)
    dirac[0] = 1.0
    return (dirac, _iir(_butter(8, 80, "low")), _iir(_butter(8, hpf_hz, "high")))


def _product(factors):
    product = factors[0]
    for factor in factors[1:]:
        product = dsp_utils.convolve_fir(product, factor)
    return product


def _row(tmp_path, fir, factors):
    """verify_minimum_phase_composition() on a float32 WAV round-trip."""
    path = str(tmp_path / "x.wav")
    export_filter(fir, path, n_taps=N_TAPS)
    return verify.verify_minimum_phase_composition(path, factors)


# -- D1: roles and factors ---------------------------------------------------

@pytest.mark.parametrize("filter_type, has_subsonic, expected", [
    ("lowpass", True, True),
    ("bandpass", True, True),
    ("highpass", True, False),
    ("lowpass", False, False),
    ("bandpass", False, False),
    ("highpass", False, False),
])
def test_is_cascade(filter_type, has_subsonic, expected):
    assert gpf.is_cascade(filter_type, np.ones(4) if has_subsonic else None) is expected


class TestChannelFactors:

    @pytest.mark.parametrize("profile_name", PROFILES)
    def test_generator_equals_combined_factors(self, profile_name):
        """m3: generate_profile_filters() is combine_filters() over channel_factors()."""
        profile, identities = _load(profile_name)
        filters = gpf.generate_profile_filters(profile, identities, n_taps=N_TAPS, sr=SR)
        factors = gpf.channel_factors(profile, identities, n_taps=N_TAPS, sr=SR)
        assert list(filters) == list(factors)
        for spk, f in factors.items():
            combined = combine_filters(
                f.correction, f.crossover, n_taps=N_TAPS,
                margin_db=gpf.COMBINE_MARGIN_DB, subsonic_filter=f.subsonic)
            assert np.array_equal(filters[spk], combined), spk

    @pytest.mark.parametrize("profile_name", PROFILES)
    def test_deterministic(self, profile_name):
        """m3: two runs give bit-identical factors."""
        profile, identities = _load(profile_name)
        first = gpf.channel_factors(profile, identities, n_taps=N_TAPS, sr=SR)
        second = gpf.channel_factors(profile, identities, n_taps=N_TAPS, sr=SR)
        assert list(first) == list(second)
        for spk in first:
            a, b = first[spk], second[spk]
            assert a.filter_type == b.filter_type
            assert np.array_equal(a.correction, b.correction), spk
            assert np.array_equal(a.crossover, b.crossover), spk
            assert (a.subsonic is None) == (b.subsonic is None), spk
            if a.subsonic is not None:
                assert np.array_equal(a.subsonic, b.subsonic), spk

    def test_bandpass_with_subsonic_is_cascade(self):
        """Role reading (ace87e0d): the c3d mids (bandpass + subsonic) are cascades."""
        profile, identities = _load("workshop-c3d-elf-3way")
        filenames = {k: f"{k}.wav" for k in profile["speakers"]}
        inputs = gpf.composition_inputs_by_file(
            profile, identities, filenames, n_taps=N_TAPS, sr=SR)
        assert {"mid_left.wav", "mid_right.wav"} <= set(inputs)
        assert "hf_left.wav" not in inputs

    @pytest.mark.parametrize("profile_name", PROFILES)
    def test_inputs_cover_exactly_the_cascades(self, profile_name):
        profile, identities = _load(profile_name)
        filenames = {k: f"{k}.wav" for k in profile["speakers"]}
        factors = gpf.channel_factors(profile, identities, n_taps=N_TAPS, sr=SR)
        inputs = gpf.composition_inputs_by_file(
            profile, identities, filenames, n_taps=N_TAPS, sr=SR)
        assert set(inputs) == {f"{k}.wav" for k, f in factors.items()
                               if gpf.is_cascade(f.filter_type, f.subsonic)}
        for k, f in factors.items():
            if f"{k}.wav" in inputs:
                assert all(np.array_equal(a, b) for a, b in
                           zip(inputs[f"{k}.wav"], (f.correction, f.crossover, f.subsonic)))

    def test_unknown_speaker_raises(self):
        """m4: a typo must not silently drop a channel to the residual row."""
        profile, identities = _load("pa-2way-80hz-lavoce")
        with pytest.raises(ValueError, match="sub9"):
            gpf.composition_inputs_by_file(
                profile, identities, {"sub9": "sub9.wav"}, n_taps=N_TAPS, sr=SR)


# -- D2: the composition row --------------------------------------------------

MUTANTS = {
    "N1-linear-phase": lambda h: np.roll(np.fft.irfft(np.abs(np.fft.rfft(h)), n=N_TAPS),
                                         N_TAPS // 2),
    "N2-time-reversed": lambda h: h[::-1].copy(),
    "N3-shift-n/2": lambda h: np.roll(h, N_TAPS // 2),
    "N5-delay-200": lambda h: np.concatenate([np.zeros(200), h[:-200]]),
}


@pytest.mark.parametrize("hpf_hz", [20, 42], ids=["HP20", "HP42"])
class TestCompositionRow:

    def test_exact_product_passes(self, tmp_path, hpf_hz):
        factors = _cascade_factors(hpf_hz)
        result = _row(tmp_path, 0.5 * _product(factors), factors)
        assert result.passed, result.message
        assert result.name == "Minimum Phase (composition)"
        assert result.details["composition_db"] <= verify.COMPOSITION_MAX_RESIDUAL_DB
        assert result.details["g_db"] == pytest.approx(-6.02, abs=0.01)

    @pytest.mark.parametrize("mutant", list(MUTANTS.values()), ids=list(MUTANTS))
    def test_gross_errors_fail(self, tmp_path, hpf_hz, mutant):
        factors = _cascade_factors(hpf_hz)
        result = _row(tmp_path, mutant(0.5 * _product(factors)[:N_TAPS]), factors)
        assert not result.passed
        assert "residual" in result.details["failed"], result.message
        assert result.details["composition_db"] > verify.COMPOSITION_MAX_RESIDUAL_DB

    def test_factor_shift_10_fails_on_residual(self, tmp_path, hpf_hz):
        """m1: the shipped FIR 10 samples late against its factors."""
        factors = _cascade_factors(hpf_hz)
        late = np.concatenate([np.zeros(10), 0.5 * _product(factors)])
        result = _row(tmp_path, late, factors)
        assert result.details["failed"] == ["residual"], result.message
        assert result.message.startswith("FAIL residual:")

    def test_polarity_flip_fails_on_polarity(self, tmp_path, hpf_hz):
        """m1 / G+: g < 0 fails, it is not absorbed."""
        factors = _cascade_factors(hpf_hz)
        result = _row(tmp_path, -0.5 * _product(factors), factors)
        assert result.details["g"] < 0
        assert result.details["failed"] == ["polarity"], result.message
        assert result.message.startswith("FAIL polarity:")

    def test_boost_fails_on_boost(self, tmp_path, hpf_hz):
        """G<=1 (D-009): the shipped FIR is never louder than its product."""
        factors = _cascade_factors(hpf_hz)
        result = _row(tmp_path, 1.05 * _product(factors), factors)
        assert result.details["g"] > verify.COMPOSITION_MAX_GAIN
        assert result.details["failed"] == ["boost"], result.message
        assert result.message.startswith("FAIL boost:")

    def test_rising_tail_fails(self, tmp_path, hpf_hz):
        """The residual row's decay condition, on the composition row."""
        factors = _cascade_factors(hpf_hz)
        h = 0.5 * _product(factors)[:N_TAPS]
        n_tail = N_TAPS // 20
        h[-n_tail:] += np.sqrt(np.sum(h ** 2) * 10 ** (-60.0 / 10) / n_tail)
        result = _row(tmp_path, h, factors)
        assert not result.details["tail_decaying"]
        assert "rising tail" in result.details["failed"], result.message
        assert not result.passed


def test_composition_limits():
    assert verify.COMPOSITION_MAX_RESIDUAL_DB == -30.0
    assert verify.COMPOSITION_MAX_GAIN == 1.0 + 1e-3
    assert verify.CASCADE_GATE_ROW == "residual"


def test_all_zero_filter_fails(tmp_path):
    factors = _cascade_factors(20)
    result = _row(tmp_path, np.zeros(N_TAPS), factors)
    assert not result.passed


# -- D2/D3: plumbing, residual row still gates (a1) ----------------------------

def _cascade_sub(tmp_path):
    """The TestMandatoryHpfInGate sub (LP200 + 30 Hz subsonic), exported."""
    profile = {
        "crossover": {"frequency_hz": 200, "slope_db_per_oct": 48},
        "speakers": {"sub1": {"identity": "sub-id", "channel": 2,
                              "filter_type": "lowpass"}},
    }
    identities = {"sub-id": {"mandatory_hpf_hz": 30}}
    fir = gpf.generate_profile_filters(profile, identities, n_taps=N_TAPS, sr=SR)["sub1"]
    export_filter(fir, str(tmp_path / "sub1.wav"), n_taps=N_TAPS)
    inputs = gpf.composition_inputs_by_file(
        profile, identities, {"sub1": "sub1.wav"}, n_taps=N_TAPS, sr=SR)
    assert set(inputs) == {"sub1.wav"}
    return inputs


class TestGatePlumbing:

    def test_residual_row_gates_and_logs_composition(self, tmp_path):
        inputs = _cascade_sub(tmp_path)
        files = {"sub1.wav": "fir"}
        hpf = {"sub1.wav": 30.0}
        plain_passed, plain = verify.run_correction_gate(
            str(tmp_path), files, mandatory_hpf_hz=hpf)
        passed, results = verify.run_correction_gate(
            str(tmp_path), files, mandatory_hpf_hz=hpf, composition_inputs=inputs)
        assert passed == plain_passed
        assert [(r.name, r.passed) for r in results] == [(r.name, r.passed) for r in plain]
        assert not any("composition" in r.name for r in results)
        row = next(r for r in results if r.name == "Minimum Phase (residual) (sub1.wav)")
        composition = row.details["composition"]
        assert {"composition_db", "g", "g_db", "residual_db", "tail_db", "tail_prev_db",
                "tail_decaying", "failed", "passed", "message"} <= set(composition)
        assert verify.gate_summary("sub1.wav", results) == verify.gate_summary("sub1.wav", plain)

    def test_non_cascade_file_has_no_composition(self, tmp_path):
        _cascade_sub(tmp_path)
        _, results = verify.run_venue_checks(str(tmp_path), {"sub1.wav": "fir"})
        row = next(r for r in results if r.name.startswith("Minimum Phase"))
        assert "composition" not in row.details

    @pytest.mark.parametrize("gate", [verify.run_venue_checks, verify.run_correction_gate])
    def test_composition_inputs_on_non_fir_raise(self, tmp_path, gate):
        inputs = _cascade_sub(tmp_path)
        with pytest.raises(ValueError, match="not 'fir'"):
            gate(str(tmp_path), {"sub1.wav": "dirac"}, composition_inputs=inputs)
        with pytest.raises(ValueError, match="not 'fir'"):
            gate(str(tmp_path), {}, composition_inputs=inputs)


def test_venue_result_carries_cascade_inputs():
    """D3: generate_venue_filters() fills composition_inputs for runner.py."""
    bundle = vp.load_venue_bundle(VENUE, PROFILES_DIR / "pa-2way-80hz-lavoce.yml")
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"),
        scenario_name="home_lab", noise_db=-60.0, noise_color="pink")
    result = vp.generate_venue_filters(bundle, sim.measured_irs)
    factors = gpf.channel_factors(bundle.profile, bundle.identities, n_taps=N_TAPS, sr=SR)
    cascades = {bundle.speaker_files[k] for k, f in factors.items()
                if gpf.is_cascade(f.filter_type, f.subsonic)}
    assert cascades and set(result.composition_inputs) == cascades
    for filename, inputs in result.composition_inputs.items():
        assert len(inputs) == 3
        assert all(np.all(np.isfinite(a)) for a in inputs)
        assert np.count_nonzero(inputs[0]) > 1, "dirac, not the venue correction"
