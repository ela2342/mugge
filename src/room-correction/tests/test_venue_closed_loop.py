"""Closed-loop venue pipeline against the room simulator (US-174b, AC1-AC8).

The real venue config and speaker profile (configs/venues, configs/speakers)
go through venue_sim (speaker_sim -> room -> sweep -> noise -> deconvolution)
and venue_pipeline. The resulting filters are judged against truth taken
from the scenario definition: geometry for delays, the injected mode for
cut depth, the simulated speaker*room path for the residual. None of the
truth comes from the pipeline's own estimators (QE P3).

Measurement noise (AC6a, AE): pink, fixed seed per channel. Every gate
runs at -60 dB re recording peak; -40 dB is run and printed, not gated.

Not covered here, on purpose:
- System (sat+sub summed) response and the crossover region (AC3/AC5
  judgement): blocked on F-374. Per-channel bands below stay clear of the
  200 Hz crossover, so no LR knee behaviour is locked in.
- Off-position robustness (AC4): needs position-dependent modes, slice
  174b-sim.

Acceptance values: AE, 2026-10-25.
"""

import ast
import dataclasses
import inspect
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.signal
import soundfile as sf
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import room_simulator, venue_sim
from room_correction import closed_loop, correction, dsp_utils, verify
from room_correction import venue_pipeline as vp
from room_correction.closed_loop import MAX_POSITIVE_DEVIATION_DB
from room_correction.correction import generate_correction_filter, normalize_ir_level
from room_correction.export import export_filter

SR = 48000
N_TAPS = 16384
RC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RC_DIR.parents[1]
VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
# Both venue configs that use this profile (US-173).
VENUES = [VENUE, REPO_ROOT / "configs" / "venues" / "home-lab-chn50p-ultimax.yml"]
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"

SCENARIOS = ["home_lab", "small_club", "large_hall", "outdoor_tent"]
# QE: the residual bar only counts where it can bite. In large_hall and
# outdoor_tent every channel is already within MAX_POSITIVE_DEVIATION_DB
# uncorrected (worst +2.8 / +2.2 dB, sub), so they add no residual coverage
# and are excluded from it; test_excluded_scenarios_are_vacuous keeps that
# honest if the simulator changes.
RESIDUAL_SCENARIOS = ["home_lab", "small_club"]
VACUOUS_SCENARIOS = [s for s in SCENARIOS if s not in RESIDUAL_SCENARIOS]
NON_VACUOUS_UNCORRECTED_DB = 6.0
# Teeth test degradation (one line, deterministic): the correction's cut depth
# is limited to half the pipeline's cap.
WEAK_CUT_DB = vp.MAX_CUT_DB / 2

# AE: per-channel residual bands (clear of the 200 Hz crossover).
RESIDUAL_BANDS_HZ = {"highpass": (250.0, 500.0), "lowpass": (30.0, 200.0)}
LEVEL_INVARIANCE_DB = 0.1
CUT_ACCURACY_DB = 2.0
AC6_TOLERANCE_S = 0.2e-3
GATED_NOISE_DB = -60.0
REPORT_NOISE_DB = -40.0
# AE below-target ruling, 2026-10-25.
MAX_RAISE_DB = 0.05
MAX_OVER_CUT_DB = 1.0
MAX_FAR_FIELD_DB = 0.1
FAR_OCTAVES = 1.0 / 3.0
# The D-009 margin the correction stage applies everywhere. combine has no
# logged margin scalar yet; when F-383 adds one, read m from there (AE),
# then re-run and report the over-cut to the AE before widening anything.
CORRECTION_MARGIN_DB = correction.D009_MARGIN_DB

EXPECTED_FILES = {
    "combined_left_hp.wav": "fir",
    "combined_right_hp.wav": "fir",
    "combined_sub1_lp.wav": "fir",
    "dirac.wav": "dirac",
}


# -- fixtures ---------------------------------------------------------------

@pytest.fixture(scope="module")
def bundle():
    return vp.load_venue_bundle(VENUE, PROFILE)


def _simulate(bundle, name, noise_db=GATED_NOISE_DB):
    return venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario(name), scenario_name=name,
        noise_db=noise_db, noise_color="pink")


@pytest.fixture(scope="module", params=SCENARIOS)
def run(request, bundle):
    """(scenario name, SimulatedMeasurement, VenueFilterResult) at the gated noise."""
    return _run(bundle, request.param)


@pytest.fixture(scope="module", params=RESIDUAL_SCENARIOS)
def residual_run(request, bundle):
    return _run(bundle, request.param)


_RUNS = {}


def _run(bundle, name):
    # Shared by run and residual_run so each scenario is simulated once.
    if name not in _RUNS:
        sim = _simulate(bundle, name)
        _RUNS[name] = (name, sim, vp.generate_venue_filters(bundle, sim.measured_irs))
    return _RUNS[name]


@pytest.fixture(scope="module")
def home_lab(bundle):
    sim = _simulate(bundle, "home_lab")
    return sim, vp.generate_venue_filters(bundle, sim.measured_irs)


@pytest.fixture(scope="module")
def home_lab_dir(tmp_path_factory, bundle, home_lab):
    _, result = home_lab
    out = tmp_path_factory.mktemp("home_lab_out")
    vp.write_venue_filters(result, str(out))
    vp.write_delays_yaml(result, bundle, str(out / "delays.yml"),
                         simulated_scenario="home_lab")
    return out


# AC7 room feature (Architect + AE ruling, 2026-10-26): a peak injected
# identically into sat_right's true path and its measurement, so the right
# file has something only it corrects. home_lab alone is too benign there.
AC7_FEATURE_HZ = 380.0
AC7_FEATURE_GAIN_DB = 6.0
AC7_FEATURE_Q = 4.0
# Report only: own/other levels this far either side of the feature.
AC7_REPORT_OCTAVES = 1.0 / 6.0


def _peaking_eq(x, f0, gain_db, q, sr=SR):
    """RBJ cookbook peaking biquad applied to x (length preserved)."""
    a = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2.0 * q)
    b = [1.0 + alpha * a, -2.0 * np.cos(w0), 1.0 - alpha * a]
    den = [1.0 + alpha / a, -2.0 * np.cos(w0), 1.0 - alpha / a]
    return scipy.signal.lfilter(b, den, x)


@pytest.fixture(scope="module")
def ac7_home_lab(bundle, home_lab):
    sim, _ = home_lab

    def inject(paths):
        out = dict(paths)
        out["sat_right"] = _peaking_eq(paths["sat_right"], AC7_FEATURE_HZ,
                                       AC7_FEATURE_GAIN_DB, AC7_FEATURE_Q)
        return out
    sim = dataclasses.replace(sim, true_paths=inject(sim.true_paths),
                              measured_irs=inject(sim.measured_irs))
    return sim, vp.generate_venue_filters(bundle, sim.measured_irs)


def _db_at(h, f, lo, hi):
    freqs, db = closed_loop.smoothed_response_db(h, lo, hi)
    return float(np.interp(np.log2(f), np.log2(freqs), db))


def _max_gain_db(fir):
    return float(np.max(dsp_utils.linear_to_db(np.abs(np.fft.rfft(fir, n=1 << 17)))))


# -- AC1: files and format --------------------------------------------------

class TestAC1Outputs:

    def test_channel_map_from_real_configs(self, bundle):
        mapping = {c.number: (c.coefficients, c.speaker_key) for c in bundle.channels}
        assert mapping[1] == ("combined_left_hp.wav", "sat_left")
        assert mapping[2] == ("combined_right_hp.wav", "sat_right")
        assert mapping[3] == ("combined_sub1_lp.wav", "sub1")
        assert mapping[4] == ("zero.wav", None)
        for n in range(5, 9):
            assert mapping[n] == ("dirac.wav", None)
        assert bundle.expected_files() == EXPECTED_FILES

    @pytest.mark.parametrize("venue_path", VENUES, ids=lambda p: p.stem)
    def test_both_venue_configs_load(self, venue_path):
        b = vp.load_venue_bundle(venue_path, PROFILE)
        mapping = {c.number: (c.coefficients, c.speaker_key) for c in b.channels}
        assert mapping[4] == ("zero.wav", None)
        assert b.expected_files() == EXPECTED_FILES

    def test_zero_wav_never_generated(self, home_lab, home_lab_dir, bundle):
        # The mute file is the committed configs/coeffs/zero.wav only.
        _, result = home_lab
        assert "zero.wav" not in result.filters
        assert "zero.wav" not in bundle.expected_files()
        assert not (home_lab_dir / "zero.wav").exists()

    def test_no_dirac_without_dirac_channel(self, bundle, home_lab):
        # dirac.wav is generated only if some channel names it.
        sim, _ = home_lab
        channels = [dataclasses.replace(c, coefficients="zero.wav")
                    if c.coefficients == "dirac.wav" else c for c in bundle.channels]
        muted = dataclasses.replace(bundle, channels=channels)
        assert "dirac.wav" not in muted.expected_files()
        result = vp.generate_venue_filters(muted, sim.measured_irs)
        assert sorted(result.filters) == sorted(
            k for k, v in EXPECTED_FILES.items() if v == "fir")

    def test_every_expected_file_written_float32(self, home_lab_dir):
        assert sorted(p.name for p in home_lab_dir.glob("*.wav")) == sorted(EXPECTED_FILES)
        for name in EXPECTED_FILES:
            info = sf.info(str(home_lab_dir / name))
            assert info.samplerate == SR
            assert info.frames == N_TAPS
            assert info.channels == 1
            assert info.subtype == "FLOAT"

    def test_dirac_is_exact_unit_impulse(self, home_lab_dir):
        data, _ = sf.read(str(home_lab_dir / "dirac.wav"), dtype="float64")
        assert data[0] == 1.0
        assert not np.any(data[1:])

    def test_venue_checks_pass(self, home_lab_dir, bundle):
        passed, results = verify.run_venue_checks(
            str(home_lab_dir), bundle.expected_files(),
            mandatory_hpf_hz=bundle.mandatory_hpf_by_file())
        assert passed, [str(r) for r in results if not r.passed]

    def test_missing_file_fails_venue_checks(self, home_lab_dir, bundle):
        files = dict(bundle.expected_files(), **{"combined_sub2_lp.wav": "fir"})
        passed, results = verify.run_venue_checks(str(home_lab_dir), files)
        assert not passed
        assert any(r.name.startswith("File Exists (combined_sub2_lp.wav)") and not r.passed
                   for r in results)


# -- AC2: D-009 and minimum phase -------------------------------------------

class TestAC2Gates:

    def test_d009_every_speaker_filter(self, run):
        name, _, result = run
        for filename, fir in result.filters.items():
            if filename != vp.DIRAC_FILENAME:
                assert _max_gain_db(fir) <= -0.5, f"{name} {filename}"

    def test_corrections_never_boost(self, run):
        # The intermediate correction FIR overshoots its own -0.5 dB margin by
        # up to 0.15 dB after the step-9 re-clip (F-384); the deployed files
        # are held to D-009 above. Here: no boost at all.
        # TODO(F-384): tighten to <= -0.5 dB once F-384 lands.
        name, _, result = run
        for spk, corr in result.corrections.items():
            assert _max_gain_db(corr) <= 0.0, f"{name} {spk}"

    def test_minimum_phase_every_speaker_filter(self, run):
        name, _, result = run
        for filename, fir in result.filters.items():
            if filename == vp.DIRAC_FILENAME:
                continue
            assert closed_loop.minimum_phase_residual_db(fir) <= verify.MIN_PHASE_MAX_RESIDUAL_DB, \
                f"{name} {filename}"
            assert closed_loop.tail_energy_db(fir) <= verify.MIN_PHASE_MAX_TAIL_DB, \
                f"{name} {filename}"

    def test_gate_accepts_known_minimum_phase(self):
        # One-pole decay a^n: zero at the origin only, minimum phase by construction.
        h = 0.9 ** np.arange(N_TAPS)
        assert closed_loop.minimum_phase_residual_db(h) <= -60.0

    def test_gate_rejects_linear_phase(self, tmp_path, home_lab):
        # Same magnitude as a real sub filter, but symmetric (linear phase).
        _, result = home_lab
        fir = result.filters["combined_sub1_lp.wav"]
        mag = np.abs(np.fft.rfft(fir))
        linear = np.roll(np.fft.irfft(mag, n=N_TAPS), N_TAPS // 2)
        path = str(tmp_path / "linear.wav")
        export_filter(linear, path, n_taps=N_TAPS)
        assert not verify.verify_minimum_phase_residual(path).passed

    def test_gate_rejects_boost(self, tmp_path, home_lab):
        _, result = home_lab
        boosted = result.filters["combined_left_hp.wav"] * dsp_utils.db_to_linear(3.0)
        path = str(tmp_path / "boost.wav")
        export_filter(boosted, path, n_taps=N_TAPS)
        assert not verify.verify_d009(path, margin_db=verify.VENUE_D009_MARGIN_DB).passed


# -- channel map: fail closed -----------------------------------------------

class TestChannelMapFailsClosed:

    @staticmethod
    def _configs(bundle):
        import copy
        return copy.deepcopy(bundle.venue), copy.deepcopy(bundle.profile)

    def test_real_configs_map(self, bundle):
        assert len(vp.build_channel_map(bundle.venue, bundle.profile)) == 8

    def test_key_without_number(self, bundle):
        venue, profile = self._configs(bundle)
        venue["channels"]["sub_extra"] = {"coefficients": "dirac.wav"}
        with pytest.raises(ValueError, match="channel number"):
            vp.build_channel_map(venue, profile)

    def test_speaker_on_dirac_channel(self, bundle):
        venue, profile = self._configs(bundle)
        del venue["channels"]["3_sub1_lp"]              # else ch 3 fails first
        profile["speakers"]["sub1"]["channel"] = 4      # venue ch 5 = dirac
        with pytest.raises(ValueError, match="dirac passthrough"):
            vp.build_channel_map(venue, profile)

    def test_speaker_on_mute_channel(self, bundle):
        venue, profile = self._configs(bundle)
        del venue["channels"]["3_sub1_lp"]              # else ch 3 fails first
        profile["speakers"]["sub1"]["channel"] = 3      # venue ch 4 = zero.wav
        with pytest.raises(ValueError, match="muted"):
            vp.build_channel_map(venue, profile)

    def test_unknown_file_without_speaker(self, bundle):
        # Only dirac.wav and zero.wav may go without a speaker.
        venue, profile = self._configs(bundle)
        venue["channels"]["4_sub2_lp"]["coefficients"] = "combined_sub2_lp.wav"
        with pytest.raises(ValueError, match="no profile speaker"):
            vp.build_channel_map(venue, profile)

    def test_fir_channel_without_speaker(self, bundle):
        venue, profile = self._configs(bundle)
        del profile["speakers"]["sub1"]
        with pytest.raises(ValueError, match="no profile speaker"):
            vp.build_channel_map(venue, profile)

    def test_speaker_without_venue_channel(self, bundle):
        venue, profile = self._configs(bundle)
        profile["speakers"]["sub1"]["channel"] = 11
        with pytest.raises(ValueError, match="matches 0 venue channel keys"):
            vp.build_channel_map(venue, profile)

    def test_two_speakers_one_channel(self, bundle):
        venue, profile = self._configs(bundle)
        profile["speakers"]["sat_right"]["channel"] = 0
        with pytest.raises(ValueError):
            vp.build_channel_map(venue, profile)

    def test_two_venue_keys_one_channel(self, bundle):
        venue, profile = self._configs(bundle)
        venue["channels"]["3_sub1_alt"] = {"coefficients": "combined_sub1_lp.wav"}
        with pytest.raises(ValueError, match="matches 2 venue channel keys"):
            vp.build_channel_map(venue, profile)

    def test_ir_set_must_match_profile(self, bundle, home_lab):
        sim, _ = home_lab
        irs = dict(sim.measured_irs)
        del irs["sub1"]
        with pytest.raises(ValueError, match="missing"):
            vp.generate_venue_filters(bundle, irs)


# -- level invariance and cut accuracy ----------------------------------------

class TestLevelAndCut:

    @pytest.mark.parametrize("scale", [0.1, 10.0])
    def test_filters_invariant_to_measurement_level(self, bundle, home_lab, scale):
        sim, ref = home_lab
        scaled = {k: v * scale for k, v in sim.measured_irs.items()}
        result = vp.generate_venue_filters(bundle, scaled)
        for filename, fir in ref.filters.items():
            _, a = closed_loop.smoothed_response_db(fir, 20.0, 20000.0)
            _, b = closed_loop.smoothed_response_db(result.filters[filename], 20.0, 20000.0)
            assert np.max(np.abs(a - b)) <= LEVEL_INVARIANCE_DB, filename
        for k, level in ref.reference_levels_db.items():
            assert result.reference_levels_db[k] == pytest.approx(
                level + 20.0 * np.log10(scale), abs=0.01)

    @staticmethod
    def _anechoic_mode_cut(gain_db, freq=42.5, q=8.0):
        """Cut (dB, positive) at freq and the injected excess (analytic)."""
        ir = room_simulator.generate_room_ir(
            [1.0, 1.0, 1.0], [3.0, 1.0, 1.0], [8.0, 6.0, 3.0], wall_absorption=1.0,
            room_modes=[{"frequency": freq, "q": q, "gain": gain_db}], sr=SR)
        normalized, _ = normalize_ir_level(ir, vp.REFERENCE_BANDS_HZ["lowpass"], sr=SR)
        corr = generate_correction_filter(normalized, n_taps=N_TAPS, sr=SR,
                                          max_cut_db=vp.MAX_CUT_DB)
        n = 1 << 17
        k = int(round(freq * n / SR))
        cut = -float(dsp_utils.linear_to_db(np.abs(np.fft.rfft(corr, n=n))[k]))
        # The simulator adds g * iirpeak (unity at f0) to the IR: |1 + g| at f0.
        excess = 20.0 * np.log10(1.0 + dsp_utils.db_to_linear(gain_db))
        return cut, excess

    @pytest.mark.parametrize("gain_db", [6.0, 12.0])
    def test_cut_matches_injected_excess(self, gain_db):
        cut, excess = self._anechoic_mode_cut(gain_db)
        assert abs(cut - excess) <= CUT_ACCURACY_DB, (cut, excess)

    def test_cut_capped_at_18_db(self):
        cut, excess = self._anechoic_mode_cut(24.0)
        assert excess > vp.MAX_CUT_DB + 4.0
        assert vp.MAX_CUT_DB - CUT_ACCURACY_DB <= cut <= vp.MAX_CUT_DB + 0.5, cut

    @staticmethod
    def _deep_mode_ir():
        ir = room_simulator.generate_room_ir(
            [1.0, 1.0, 1.0], [3.0, 1.0, 1.0], [8.0, 6.0, 3.0], wall_absorption=1.0,
            room_modes=[{"frequency": 42.5, "q": 8.0, "gain": 24.0}], sr=SR)
        return normalize_ir_level(ir, vp.REFERENCE_BANDS_HZ["lowpass"], sr=SR)[0]

    def test_cap_bounds_the_whole_correction(self):
        # Architect: 18 caps the deepest cut at -18 dB (pre-combine), at every
        # frequency, not just at the mode; the uncapped filter goes deeper.
        ir = self._deep_mode_ir()
        mag_db = lambda h: dsp_utils.linear_to_db(np.abs(np.fft.rfft(h, n=1 << 17)))
        freqs = np.fft.rfftfreq(1 << 17, d=1.0 / SR)
        audible = (freqs >= 20.0) & (freqs <= 20000.0)
        capped = mag_db(generate_correction_filter(ir, n_taps=N_TAPS, sr=SR, max_cut_db=18.0))
        uncapped = mag_db(generate_correction_filter(ir, n_taps=N_TAPS, sr=SR))
        # Non-vacuous: uncapped goes past the capped tolerance (-19.6 dB here).
        assert np.min(uncapped[audible]) < -18.0 - 0.5
        assert np.min(capped[audible]) >= -18.0 - 0.5

    def test_no_cap_is_unchanged_behaviour(self):
        # None (default) must be byte-identical to omitting the kwarg and to
        # a cap no bin reaches. (Byte identity with the pre-US-174b code was
        # checked once against b0666c02; see the PR.)
        ir = self._deep_mode_ir()
        omitted = generate_correction_filter(ir, n_taps=N_TAPS, sr=SR)
        none = generate_correction_filter(ir, n_taps=N_TAPS, sr=SR, max_cut_db=None)
        huge = generate_correction_filter(ir, n_taps=N_TAPS, sr=SR, max_cut_db=1000.0)
        assert omitted.tobytes() == none.tobytes() == huge.tobytes()


# -- residual per channel ---------------------------------------------------

EXT = 2.0 ** FAR_OCTAVES   # judge peaks just outside the band too


def _corrected_and_uncorrected(bundle, sim, result, spk, extend=1.0):
    """1/6-oct responses re the measured reference level, on band (x/÷ extend)."""
    lo, hi = RESIDUAL_BANDS_HZ[bundle.profile["speakers"][spk]["filter_type"]]
    level = result.reference_levels_db[spk]
    path = sim.true_paths[spk]
    freqs, unc = closed_loop.smoothed_response_db(path, lo / extend, hi * extend)
    _, cor = closed_loop.smoothed_response_db(
        closed_loop.system_response(path, result.corrections[spk]), lo / extend, hi * extend)
    return freqs, cor - level, unc - level


def _below_target(bundle, sim, result, spk):
    lo, hi = RESIDUAL_BANDS_HZ[bundle.profile["speakers"][spk]["filter_type"]]
    freqs, cor, unc = _corrected_and_uncorrected(bundle, sim, result, spk, extend=EXT)
    return closed_loop.below_target_report(
        freqs, cor, unc, np.zeros_like(unc), CORRECTION_MARGIN_DB,
        band=(lo, hi), far_octaves=FAR_OCTAVES)


class TestResidualPerChannel:
    """Correction alone vs flat (target at the reference level); crossover excluded (F-374)."""

    def test_max_positive_deviation(self, bundle, residual_run):
        name, sim, result = residual_run
        for spk in result.corrections:
            _, cor, _ = _corrected_and_uncorrected(bundle, sim, result, spk)
            dev = closed_loop.max_positive_deviation_db(cor, np.zeros_like(cor))
            assert np.isfinite(dev), f"{name} {spk}: {dev!r}"
            assert closed_loop.passes_residual_gate(cor, np.zeros_like(cor)), \
                f"{name} {spk}: {dev:+.2f} dB"

    def test_below_target(self, bundle, run, capsys):
        # AE ruling: never raised; over-cut near peaks bounded; far from
        # peaks only the margin. Worst values go to the test output.
        name, sim, result = run
        reports = {spk: _below_target(bundle, sim, result, spk) for spk in result.corrections}
        with capsys.disabled():
            for spk, r in sorted(reports.items()):
                print(f"\n  below-target {name} {spk}: raised {r['raised']:+.2f} dB, "
                      f"over-cut {r['over_cut']:.2f} dB, far-field {r['far_field']:.2f} dB "
                      f"({r['n_far']}/{r['n_below']} bins far)", end="")
        for spk, r in reports.items():
            if r["n_below"] == 0:
                continue
            assert r["raised"] <= MAX_RAISE_DB, f"{name} {spk}: {r}"
            assert r["over_cut"] <= MAX_OVER_CUT_DB, f"{name} {spk}: {r}"
            if r["n_far"]:
                assert r["far_field"] <= MAX_FAR_FIELD_DB, f"{name} {spk}: {r}"

    def test_far_field_guard_is_not_vacuous(self, bundle, home_lab):
        sim, result = home_lab
        assert _below_target(bundle, sim, result, "sub1")["n_far"] > 10

    def test_below_target_report_flags_broadband_over_cut(self):
        # A 1 dB cut everywhere on top of the margin: over-cut stays within
        # 1.0 dB, so only the far-field guard catches it.
        freqs = closed_loop.log_grid(30.0, 200.0)
        unc = np.where(np.abs(np.log2(freqs / 50.0)) < 0.1, 6.0, -1.0)
        cor = unc - 0.5 - 1.0
        r = closed_loop.below_target_report(freqs, cor, unc, np.zeros_like(unc), -0.5)
        assert r["raised"] < 0 and r["over_cut"] <= MAX_OVER_CUT_DB
        assert r["far_field"] > MAX_FAR_FIELD_DB

    def test_scenario_is_not_vacuous(self, bundle, residual_run):
        # QE: in every residual scenario some channel starts well above the
        # bar and the correction brings it under.
        name, sim, result = residual_run
        biting = []
        for spk in result.corrections:
            _, cor, unc = _corrected_and_uncorrected(bundle, sim, result, spk)
            zero = np.zeros_like(unc)
            unc_dev = closed_loop.max_positive_deviation_db(unc, zero)
            assert np.isfinite(unc_dev), f"{name} {spk}: {unc_dev!r}"
            if unc_dev > NON_VACUOUS_UNCORRECTED_DB and closed_loop.passes_residual_gate(cor, zero):
                biting.append(spk)
        assert biting, f"{name}: no channel where the residual bar bites"

    @pytest.mark.parametrize("dev_db, limit, passes", [
        (MAX_POSITIVE_DEVIATION_DB, MAX_POSITIVE_DEVIATION_DB, True),
        (MAX_POSITIVE_DEVIATION_DB + 0.01, MAX_POSITIVE_DEVIATION_DB, False),
        (math.nan, MAX_POSITIVE_DEVIATION_DB, False),
        (math.inf, MAX_POSITIVE_DEVIATION_DB, False),
        (-math.inf, MAX_POSITIVE_DEVIATION_DB, False),
        (0.0, math.nan, False),
        (0.0, math.inf, False),
        (-2 * MAX_POSITIVE_DEVIATION_DB, -MAX_POSITIVE_DEVIATION_DB, False),
    ], ids=["at-limit", "over-0.01", "nan", "+inf", "-inf", "nan-limit", "inf-limit", "negative-limit"])
    def test_deviation_within_limit(self, dev_db, limit, passes):
        # AE (b): the gate's one comparison, at and around its boundary;
        # anything non-finite fails closed.
        assert closed_loop.deviation_within_limit(dev_db, limit=limit) is passes

    def test_deviation_within_limit_default_is_the_gate(self):
        assert closed_loop.deviation_within_limit(MAX_POSITIVE_DEVIATION_DB) is True
        assert closed_loop.deviation_within_limit(MAX_POSITIVE_DEVIATION_DB + 0.01) is False

    @pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf], ids=["nan", "+inf", "-inf"])
    @pytest.mark.parametrize("where", ["response", "target"])
    def test_residual_gate_fails_closed_on_non_finite(self, where, bad):
        # Architect + AE: False, never an exception (a raise here fails the test).
        target = np.zeros(5)
        response = np.zeros(5)
        (response if where == "response" else target)[3] = bad
        assert closed_loop.passes_residual_gate(response, target) is False

    @pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf], ids=["nan", "+inf", "-inf"])
    @pytest.mark.parametrize("where", ["response", "target"])
    def test_metric_raises_on_non_finite(self, where, bad):
        # Architect + AE: the metric itself raises (defence in depth).
        target = np.zeros(5)
        response = np.zeros(5)
        (response if where == "response" else target)[3] = bad
        with pytest.raises(ValueError, match="non-finite"):
            closed_loop.max_positive_deviation_db(response, target)

    def test_residual_gate_fails_closed_on_empty(self):
        assert closed_loop.passes_residual_gate(np.array([]), np.array([])) is False

    def test_residual_gate_fails_closed_on_shape_mismatch(self):
        assert closed_loop.passes_residual_gate(np.zeros(5), np.zeros(4)) is False

    def test_residual_gate_boundary(self):
        target = np.array([-2.0, -0.5, 0.0, 1.0, 2.5])
        at, over = target.copy(), target.copy()
        at[2] += MAX_POSITIVE_DEVIATION_DB
        over[2] += MAX_POSITIVE_DEVIATION_DB + 0.01
        assert closed_loop.passes_residual_gate(at, target) is True
        assert closed_loop.passes_residual_gate(over, target) is False

    def test_no_product_caller_overrides_the_limit(self):
        # Architect: `limit=` is for tests only. Scan every non-test Python
        # file for a call to the gate functions that passes it; the only
        # allowed one is the wrapper forwarding its own `limit`.
        gate_fns = {"passes_residual_gate", "deviation_within_limit"}
        overrides, forwards = [], []
        for path in sorted((REPO_ROOT / "src").rglob("*.py")) + sorted((REPO_ROOT / "scripts").rglob("*.py")):
            if ("tests" in path.parts or path.name.startswith("test_")
                    or path.name == "conftest.py" or "node_modules" in path.parts):
                continue
            for node in ast.walk(ast.parse(path.read_text(), str(path))):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
                if fn not in gate_fns:
                    continue
                for kw in node.keywords:
                    if kw.arg == "limit":
                        if (path.name == "closed_loop.py" and isinstance(kw.value, ast.Name)
                                and kw.value.id == "limit"):
                            forwards.append(path)
                        else:
                            overrides.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
        assert forwards, "scanner did not find the wrapper's own forwarding call"
        assert not overrides, overrides

    def test_gate_has_teeth(self, bundle, home_lab, capsys):
        # Architect/AE/QE: same chain as the venue asserts, only the correction
        # is degraded (cut depth capped at WEAK_CUT_DB). The residual lands
        # between the gate and verify_target_deviation's 8 dB default and
        # must fail the gate; the real correction passes.
        sim, real = home_lab
        weak = vp.generate_venue_filters(bundle, sim.measured_irs, max_cut_db=WEAK_CUT_DB)
        freqs, weak_cor, _ = _corrected_and_uncorrected(bundle, sim, weak, "sub1")
        _, real_cor, _ = _corrected_and_uncorrected(bundle, sim, real, "sub1")
        weak_dev = closed_loop.max_positive_deviation_db(weak_cor, np.zeros_like(weak_cor))
        real_dev = closed_loop.max_positive_deviation_db(real_cor, np.zeros_like(real_cor))
        assert np.isfinite(weak_dev) and np.isfinite(real_dev), (weak_dev, real_dev)
        with capsys.disabled():
            print(f"\n  teeth home_lab sub1 (30-200 Hz): weak {weak_dev:+.2f} dB at "
                  f"{freqs[np.argmax(weak_cor)]:.1f} Hz, real {real_dev:+.2f} dB", end="")
        verify_default = inspect.signature(
            verify.verify_target_deviation).parameters["tolerance_db"].default
        zero = np.zeros_like(weak_cor)
        assert closed_loop.deviation_within_limit(weak_dev, limit=verify_default), \
            f"weak case drifted above verify's default: {weak_dev:+.2f} dB"
        assert not closed_loop.passes_residual_gate(weak_cor, zero), \
            f"weak case passes the gate: {weak_dev:+.2f} dB"
        assert closed_loop.passes_residual_gate(real_cor, zero), f"real: {real_dev:+.2f} dB"

    @pytest.mark.parametrize("name", VACUOUS_SCENARIOS)
    def test_excluded_scenarios_are_vacuous(self, bundle, name):
        # If the uncorrected check fails the scenario now has coverage: add it
        # to RESIDUAL_SCENARIOS. The corrected check is the do-no-harm bar (QE).
        _, sim, result = _run(bundle, name)
        for spk in result.corrections:
            _, cor, unc = _corrected_and_uncorrected(bundle, sim, result, spk)
            dev = closed_loop.max_positive_deviation_db(unc, np.zeros_like(unc))
            harm = closed_loop.max_positive_deviation_db(cor, np.zeros_like(cor))
            assert np.isfinite(dev) and np.isfinite(harm), f"{name} {spk}: {dev!r}, {harm!r}"
            assert closed_loop.passes_residual_gate(unc, np.zeros_like(unc)), \
                f"{name} {spk}: {dev:+.2f} dB"
            assert closed_loop.passes_residual_gate(cor, np.zeros_like(cor)), \
                f"{name} {spk}: {harm:+.2f} dB corrected"


# -- AC6a: noise robustness -------------------------------------------------

def _sub_correction(bundle, sim):
    normalized, _ = normalize_ir_level(
        sim.measured_irs["sub1"], vp.reference_band(bundle, "sub1"), sr=SR)
    return generate_correction_filter(normalized, n_taps=N_TAPS, sr=SR,
                                      max_cut_db=vp.MAX_CUT_DB)


class TestAC6aNoise:

    def test_noise_path_is_live(self, bundle, home_lab):
        # QE: the noise tests must not pass on a silently disabled noise path.
        assert venue_sim.DEFAULT_NOISE_DB is not None
        assert dsp_utils.db_to_linear(GATED_NOISE_DB) > 0.0
        sim, _ = home_lab
        clean = _simulate(bundle, "home_lab", noise_db=None)
        for spk, ir in clean.measured_irs.items():
            assert not np.array_equal(ir, sim.measured_irs[spk]), spk

    def test_noise_adds_no_cuts_below_30_hz(self, bundle, run):
        # AE: at the gated noise, no sub cut below 30 Hz that the noise-free
        # measurement would not make (within 1 dB).
        name, _, result = run
        clean = _sub_correction(bundle, _simulate(bundle, name, noise_db=None))
        _, a = closed_loop.smoothed_response_db(clean, 15.0, 30.0)
        _, b = closed_loop.smoothed_response_db(result.corrections["sub1"], 15.0, 30.0)
        assert np.max(np.abs(a - b)) <= 1.0, name

    @pytest.mark.parametrize("name", SCENARIOS)
    def test_report_at_minus_40_db(self, bundle, name, capsys):
        # Report only (AE): printed for review, not gated.
        sim = _simulate(bundle, name, noise_db=REPORT_NOISE_DB)
        result = vp.generate_venue_filters(bundle, sim.measured_irs)
        truth = venue_sim.true_delays_samples(sim.arrival_samples)
        with capsys.disabled():
            for spk in sorted(result.corrections):
                _, cor, _ = _corrected_and_uncorrected(bundle, sim, result, spk)
                r = _below_target(bundle, sim, result, spk)
                _, cut = closed_loop.smoothed_response_db(result.corrections[spk], 20.0, 500.0)
                print(f"\n  REPORT -40 dB {name} {spk}: max+ {np.max(cor):+.2f} dB, "
                      f"deepest cut {np.min(cut):.1f} dB, raised {r['raised']:+.2f}, "
                      f"over-cut {r['over_cut']:.2f}, far-field {r['far_field']:.2f}, "
                      f"delay err {result.delays_samples[spk] - truth[spk]} samples", end="")
        assert set(result.filters) == set(EXPECTED_FILES)


# -- AC6: time alignment against geometry ----------------------------------

class TestAC6Delays:

    def test_delays_match_geometry(self, run):
        name, sim, result = run
        truth = venue_sim.true_delays_samples(sim.arrival_samples)
        for spk, est in result.delays_samples.items():
            assert abs(est - truth[spk]) <= 1, f"{name} {spk}: {est} vs {truth[spk]}"
            assert abs(result.delays_s[spk] - truth[spk] / SR) <= AC6_TOLERANCE_S

    def test_truth_is_geometry(self, home_lab):
        sim, _ = home_lab
        scenario = venue_sim.load_scenario("home_lab")
        c = venue_sim.speed_of_sound(scenario)
        mic = np.array(scenario["microphone"]["position"])
        for spk, n in sim.arrival_samples.items():
            pos = np.array(venue_sim.speaker_position(scenario, spk))
            assert n == int(np.linalg.norm(pos - mic) / c * SR)

    def test_estimate_follows_a_shifted_ir(self, bundle, home_lab):
        # A sub IR arriving 30 samples later must move every other delay by 30.
        sim, ref = home_lab
        irs = dict(sim.measured_irs)
        irs["sub1"] = np.concatenate([np.zeros(30), irs["sub1"]])[:len(irs["sub1"])]
        from room_correction import time_align
        delays = time_align.delays_to_samples(time_align.compute_delays(irs, sr=SR), sr=SR)
        for spk in ("sat_left", "sat_right"):
            assert delays[spk] == ref.delays_samples[spk] + 30


# -- AC7: channel identity --------------------------------------------------

class TestAC7Identity:

    def test_swapped_measurements_swap_outputs(self, bundle, home_lab):
        sim, ref = home_lab
        irs = dict(sim.measured_irs)
        irs["sat_left"], irs["sat_right"] = irs["sat_right"], irs["sat_left"]
        swapped = vp.generate_venue_filters(bundle, irs)
        np.testing.assert_allclose(swapped.filters["combined_left_hp.wav"],
                                   ref.filters["combined_right_hp.wav"], atol=1e-9)
        np.testing.assert_allclose(swapped.filters["combined_right_hp.wav"],
                                   ref.filters["combined_left_hp.wav"], atol=1e-9)
        assert swapped.delays_samples["sat_left"] == ref.delays_samples["sat_right"]
        assert swapped.delays_samples["sat_right"] == ref.delays_samples["sat_left"]

    def test_each_file_corrects_its_own_room(self, bundle, ac7_home_lab, capsys):
        # Wiring check from physics, not from the mapping code: the right
        # sat's room gets an injected +6 dB, Q 4 peak at 380 Hz (in both the
        # true path and the measurement), so its own file must beat the
        # left file there. (The left room is too benign to tell the two
        # files apart, so only the right side is asserted.)
        sim, ref = ac7_home_lab
        lo, hi = RESIDUAL_BANDS_HZ["highpass"]
        path = sim.true_paths["sat_right"]
        level = ref.reference_levels_db["sat_right"]
        own_fir = ref.filters["combined_right_hp.wav"]
        other_fir = ref.filters["combined_left_hp.wav"]

        # Premises: fail loudly if the fixture stops discriminating.
        f0 = AC7_FEATURE_HZ
        assert lo <= f0 <= hi, (f0, lo, hi)                                   # (c)
        uncorrected_right = _db_at(path, f0, lo, hi) - level
        uncorrected_left = (_db_at(sim.true_paths["sat_left"], f0, lo, hi)
                            - ref.reference_levels_db["sat_left"])
        assert uncorrected_right >= 4.0, (uncorrected_right,)                # (a0)
        assert uncorrected_right - uncorrected_left >= 4.0, (
            uncorrected_right, uncorrected_left)                              # (a)
        own_at_f0 = _db_at(closed_loop.system_response(path, own_fir), f0, lo, hi) - level
        assert own_at_f0 <= uncorrected_right - 3.0, (own_at_f0, uncorrected_right)  # (b)

        def resp(fir):
            return closed_loop.smoothed_response_db(
                closed_loop.system_response(path, fir), lo, hi)[1]

        own_resp, other_resp = resp(own_fir), resp(other_fir)
        target = np.full_like(own_resp, level)
        own = closed_loop.max_positive_deviation_db(own_resp, target)
        other = closed_loop.max_positive_deviation_db(other_resp, target)

        with capsys.disabled():
            for f in (f0 * 2 ** -AC7_REPORT_OCTAVES, f0, f0 * 2 ** AC7_REPORT_OCTAVES):
                o = _db_at(closed_loop.system_response(path, own_fir), f, lo, hi) - level
                x = _db_at(closed_loop.system_response(path, other_fir), f, lo, hi) - level
                print(f"\n  REPORT AC7 sat_right @ {f:.1f} Hz: own {o:+.2f} dB, "
                      f"other {x:+.2f} dB (re level)", end="")
            print(f"\n  REPORT AC7 max+ deviation: own {own:+.4f} dB, "
                  f"other {other:+.4f} dB", end="")

        assert np.isfinite(own) and np.isfinite(other), (own, other)
        assert closed_loop.passes_residual_gate(own_resp, target), f"{own:+.2f} dB"
        assert own < other - 1.0, (own, other)

    def test_left_and_right_differ(self, home_lab):
        # home_lab is asymmetric on purpose; otherwise the swap test proves nothing.
        _, ref = home_lab
        a = ref.filters["combined_left_hp.wav"]
        b = ref.filters["combined_right_hp.wav"]
        assert np.max(np.abs(a - b)) > 1e-3


# -- F-399: staged publish ----------------------------------------------------

def _files(d):
    """Top-level regular files and their bytes."""
    return {p.name: p.read_bytes() for p in Path(d).iterdir() if p.is_file()}


def _staging_dirs(d):
    return [p.name for p in Path(d).iterdir() if p.name.startswith(vp.STAGING_PREFIX)]


def _fill_stage(stage_dir, wavs, scenario, tag):
    for n in wavs:
        (Path(stage_dir) / n).write_bytes(f"{tag} {n}".encode())
    (Path(stage_dir) / vp.DELAYS_FILENAME).write_text(yaml.safe_dump(
        {"venue": tag, "simulated": scenario is not None, "scenario": scenario}))


def _publish(out, wavs, scenario, tag):
    with vp.staged_outputs(str(out), simulated_scenario=scenario) as stage:
        _fill_stage(stage.path, wavs, scenario, tag)
        stage.commit()


OLD_SET = ["combined_left_hp.wav", "combined_right_hp.wav",
           "combined_sub1_lp.wav", "combined_sub2_lp.wav"]
NEW_SET = ["combined_left_hp.wav", "combined_right_hp.wav",
           "combined_sub1_lp.wav", "dirac.wav"]


class TestStagedPublish:

    @pytest.fixture
    def out(self, tmp_path):
        out = tmp_path / "out"
        _publish(out, OLD_SET, None, "old")
        (out / "notes.txt").write_text("operator notes")
        return out

    def test_real_publish(self, out):
        files = _files(out)
        assert sorted(files) == sorted(OLD_SET + ["delays.yml", "notes.txt"])
        assert yaml.safe_load(files["delays.yml"])["simulated"] is False
        assert _staging_dirs(out) == []

    def test_no_commit_publishes_nothing(self, out):
        before = _files(out)
        with vp.staged_outputs(str(out), simulated_scenario="home_lab") as stage:
            _fill_stage(stage.path, NEW_SET, "home_lab", "new")
        assert _files(out) == before
        assert _staging_dirs(out) == []

    def test_exception_in_body_publishes_nothing(self, out):
        before = _files(out)
        with pytest.raises(RuntimeError, match="verify blew up"):
            with vp.staged_outputs(str(out)) as stage:
                _fill_stage(stage.path, NEW_SET, None, "new")
                raise RuntimeError("verify blew up")
        assert _files(out) == before
        assert _staging_dirs(out) == []

    def test_simulated_publish_marks_and_replaces_fewer_files(self, out):
        _publish(out, NEW_SET, "home_lab", "new")
        files = _files(out)
        # combined_sub2_lp.wav from the old set must not survive next to the new set.
        assert sorted(files) == sorted(NEW_SET + ["delays.yml", "SIMULATED", "notes.txt"])
        assert all(files[n] == f"new {n}".encode() for n in NEW_SET)
        delays = yaml.safe_load(files["delays.yml"])
        assert delays["simulated"] is True and delays["scenario"] == "home_lab"
        assert files["notes.txt"] == b"operator notes"

    def test_real_publish_removes_stale_marker(self, out):
        _publish(out, NEW_SET, "home_lab", "sim")
        _publish(out, OLD_SET, None, "real")
        assert "SIMULATED" not in _files(out)
        assert yaml.safe_load(_files(out)["delays.yml"])["simulated"] is False

    def test_commit_only_once_and_only_inside(self, out):
        with vp.staged_outputs(str(out)) as stage:
            _fill_stage(stage.path, NEW_SET, None, "new")
            stage.commit()
            with pytest.raises(RuntimeError):
                stage.commit()
        with vp.staged_outputs(str(out)) as late:
            pass
        with pytest.raises(RuntimeError):
            late.commit()

    @pytest.mark.parametrize("scenario,flag", [(None, True), ("home_lab", False)])
    def test_marker_mismatch_refused_before_any_change(self, out, scenario, flag):
        before = _files(out)
        with pytest.raises(ValueError, match="simulated"):
            with vp.staged_outputs(str(out), simulated_scenario=scenario) as stage:
                _fill_stage(stage.path, NEW_SET, "x" if flag else None, "new")
                stage.commit()
        assert _files(out) == before

    def test_unexpected_staged_file_refused(self, out):
        before = _files(out)
        with pytest.raises(ValueError, match="unexpected"):
            with vp.staged_outputs(str(out)) as stage:
                _fill_stage(stage.path, NEW_SET, None, "new")
                (Path(stage.path) / "stray.txt").write_text("x")
                stage.commit()
        assert _files(out) == before

    def test_sweep_keeps_dirac(self, tmp_path):
        out = tmp_path / "out"
        _publish(out, NEW_SET, None, "old")
        _publish(out, OLD_SET, None, "new")
        # combined_* not in the new set go; dirac.wav is never swept (AD).
        assert sorted(n for n in _files(out) if vp.is_deployable_name(n)) == \
            sorted(OLD_SET + ["dirac.wav"])

    @pytest.mark.parametrize("via_symlink", [False, True])
    def test_simulated_refused_into_coeffs_dir(self, tmp_path, monkeypatch, via_symlink):
        from room_correction import deploy
        coeffs = tmp_path / "coeffs"
        coeffs.mkdir()
        (coeffs / "combined_left_hp.wav").write_bytes(b"prod")
        monkeypatch.setattr(deploy, "DEFAULT_COEFFS_DIR", str(coeffs))
        target = coeffs
        if via_symlink:
            target = tmp_path / "link"
            target.symlink_to(coeffs)
        with pytest.raises(ValueError, match="coeffs dir"):
            with vp.staged_outputs(str(target), simulated_scenario="home_lab"):
                pytest.fail("body must not run")
        assert _files(coeffs) == {"combined_left_hp.wav": b"prod"}
        assert _staging_dirs(coeffs) == []
        with pytest.raises(ValueError, match="coeffs dir"):
            vp.publish_venue_outputs(str(tmp_path), str(target),
                                     simulated_scenario="home_lab")

    @pytest.mark.parametrize("prior,scenario", [(None, "home_lab"), ("home_lab", None),
                                                (None, None)])
    def test_crash_at_every_step_never_leaves_unmarked_mix(self, tmp_path, monkeypatch,
                                                           prior, scenario):
        # Kill the publish at its k-th filesystem change, for every k (Architect C).
        # Afterwards a set with delays.yml must be complete and new, or the old one
        # untouched; anything that may hold simulated files must carry SIMULATED.
        k = 0
        while True:
            k += 1
            out = tmp_path / f"out{k}"
            _publish(out, OLD_SET, prior, "old")
            before = _files(out)
            calls = {"n": 0}
            real_replace, real_remove = os.replace, os.remove

            def crashing(real):
                def f(*a, **kw):
                    calls["n"] += 1
                    if calls["n"] == k:
                        raise OSError("power loss")
                    return real(*a, **kw)
                return f

            monkeypatch.setattr(vp.os, "replace", crashing(real_replace))
            monkeypatch.setattr(vp.os, "remove", crashing(real_remove))
            try:
                _publish(out, NEW_SET, scenario, "new")
                crashed = False
            except OSError:
                crashed = True
            monkeypatch.undo()
            after = _files(out)
            assert _staging_dirs(out) == []
            if not crashed:
                break
            if after == before:
                continue
            if "delays.yml" in after:
                # Either the whole new set, or the old set untouched (a crash right
                # after the marker went in leaves old files marked: fail closed).
                deployable = {n: b for n, b in after.items() if vp.is_deployable_name(n)}
                new = {n: f"new {n}".encode() for n in NEW_SET}
                old = {n: b for n, b in before.items() if vp.is_deployable_name(n)}
                assert deployable in (new, old)
                assert after["delays.yml"] == before["delays.yml"] or deployable == new
            if scenario is not None or prior is not None:
                assert "SIMULATED" in after
        assert k > 6  # the walk reached every step, not just the first


# -- CLI ---------------------------------------------------------------------

def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "runner.py", "--mock", *args],
        cwd=str(RC_DIR), capture_output=True, text=True, timeout=600)


class TestCLI:

    def test_venue_run_passes(self, tmp_path):
        out = tmp_path / "out"
        proc = _run_cli("--venue", str(VENUE), "--speaker-profile", str(PROFILE),
                        "--scenario", "home_lab", "--output-dir", str(out))
        assert proc.returncode == 0, proc.stderr
        assert "ch 3 3_sub1_lp: combined_sub1_lp.wav <- sub1" in proc.stdout
        assert "ch 4 4_sub2_lp: zero.wav <- mute" in proc.stdout
        assert "ch 5 5_eng_l: dirac.wav <- passthrough" in proc.stdout
        assert "RESULT: ALL CHECKS PASSED" in proc.stdout
        assert "Known limit" in proc.stdout
        assert "VERIFY FAILED" not in proc.stderr
        assert sorted(p.name for p in out.glob("*.wav")) == sorted(EXPECTED_FILES)
        delays = yaml.safe_load((out / "delays.yml").read_text())
        assert delays["simulated"] is True and delays["scenario"] == "home_lab"
        assert (out / "SIMULATED").is_file()
        assert _staging_dirs(out) == []

    def test_venue_run_needs_profile(self, tmp_path):
        proc = _run_cli("--venue", str(VENUE), "--scenario", "home_lab",
                        "--output-dir", str(tmp_path))
        assert proc.returncode != 0
        assert "--speaker-profile" in proc.stderr

    def test_venue_run_unknown_scenario(self, tmp_path):
        proc = _run_cli("--venue", str(VENUE), "--speaker-profile", str(PROFILE),
                        "--scenario", "no_such_room", "--output-dir", str(tmp_path))
        assert proc.returncode != 0
        assert "no scenario 'no_such_room'" in proc.stderr

    def test_failed_gate_exits_nonzero(self, tmp_path, monkeypatch, capsys, home_lab):
        # A boosting filter must stop the run: exit 1 and the failed gate on stderr.
        import runner
        sim, ref = home_lab
        boosted = dict(ref.filters)
        boosted["combined_left_hp.wav"] = boosted["combined_left_hp.wav"] * 2.0
        bad = vp.VenueFilterResult(
            boosted, ref.corrections, ref.reference_levels_db,
            ref.recommended_gain_delta_db, ref.delays_s, ref.delays_samples)
        monkeypatch.setattr(venue_sim, "simulate_venue_measurements", lambda *a, **k: sim)
        monkeypatch.setattr(vp, "generate_venue_filters", lambda *a, **k: bad)
        monkeypatch.setattr(sys, "argv", [
            "runner.py", "--mock", "--venue", str(VENUE), "--speaker-profile", str(PROFILE),
            "--scenario", "home_lab", "--output-dir", str(tmp_path)])
        with pytest.raises(SystemExit) as exc:
            runner.main()
        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "VERIFY FAILED" in err
        assert "D-009 Gain Limit (combined_left_hp.wav)" in err
        # F-399 (AD M1): nothing deployable-named is left behind.
        assert sorted(p.name for p in tmp_path.iterdir()) == []

    def _run_main(self, monkeypatch, out):
        import runner
        monkeypatch.setattr(sys, "argv", [
            "runner.py", "--mock", "--venue", str(VENUE), "--speaker-profile", str(PROFILE),
            "--scenario", "home_lab", "--output-dir", str(out)])
        try:
            runner.main()
        except SystemExit as exc:
            return exc.code
        return 0

    def _fake_run(self, monkeypatch, home_lab, filters=None):
        sim, ref = home_lab
        res = ref if filters is None else vp.VenueFilterResult(
            filters, ref.corrections, ref.reference_levels_db,
            ref.recommended_gain_delta_db, ref.delays_s, ref.delays_samples)
        monkeypatch.setattr(venue_sim, "simulate_venue_measurements", lambda *a, **k: sim)
        monkeypatch.setattr(vp, "generate_venue_filters", lambda *a, **k: res)

    def test_failed_run_keeps_previous_passing_set(self, tmp_path, monkeypatch, home_lab):
        out = tmp_path / "out"
        self._fake_run(monkeypatch, home_lab)
        assert self._run_main(monkeypatch, out) == 0
        before = _files(out)
        assert sorted(before) == sorted(list(EXPECTED_FILES) + ["delays.yml", "SIMULATED"])
        boosted = dict(home_lab[1].filters)
        boosted["combined_sub1_lp.wav"] = boosted["combined_sub1_lp.wav"] * 2.0
        self._fake_run(monkeypatch, home_lab, boosted)
        assert self._run_main(monkeypatch, out) == 1
        assert _files(out) == before
        assert _staging_dirs(out) == []

    def test_verify_reads_staged_bytes(self, tmp_path, monkeypatch, home_lab):
        # The gate must judge the files on disk, not the in-memory result (AD).
        out = tmp_path / "out"
        self._fake_run(monkeypatch, home_lab)
        real_write = vp.write_venue_filters

        def write_then_corrupt(result, output_dir, *a, **kw):
            paths = real_write(result, output_dir, *a, **kw)
            p = os.path.join(output_dir, "combined_right_hp.wav")
            data, sr = sf.read(p, dtype="float64")
            sf.write(p, data * 2.0, sr, subtype="FLOAT")
            return paths

        monkeypatch.setattr(vp, "write_venue_filters", write_then_corrupt)
        assert self._run_main(monkeypatch, out) == 1
        assert sorted(p.name for p in out.iterdir()) == []

    def test_exception_in_verify_publishes_nothing(self, tmp_path, monkeypatch, home_lab):
        out = tmp_path / "out"
        self._fake_run(monkeypatch, home_lab)

        def boom(*a, **kw):
            raise RuntimeError("verify crashed")

        monkeypatch.setattr(verify, "run_venue_checks", boom)
        with pytest.raises(RuntimeError, match="verify crashed"):
            self._run_main(monkeypatch, out)
        assert sorted(p.name for p in out.iterdir()) == []
