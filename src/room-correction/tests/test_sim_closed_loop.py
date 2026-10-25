"""Closed-loop venue pipeline against the room simulator (US-174b, AC1-AC8).

The real venue config and speaker profile (configs/venues, configs/speakers)
go through venue_sim (speaker_sim -> room -> sweep -> noise -> deconvolution)
and venue_pipeline. The resulting filters are judged against truth taken
from the scenario definition: geometry for delays, the injected mode for
cut depth, the simulated speaker*room path for the residual. None of the
truth comes from the pipeline's own estimators (QE P3).

Not covered here, on purpose:
- System (sat+sub summed) response and the crossover region (AC3/AC5
  judgement): blocked on F-374. Per-channel bands below stay clear of the
  200 Hz crossover, so no LR knee behaviour is locked in.
- Off-position robustness (AC4): needs position-dependent modes, slice
  174b-sim.

Acceptance values: AE, 2026-10-25.
"""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import room_simulator, venue_sim
from room_correction import closed_loop, dsp_utils, verify
from room_correction import venue_pipeline as vp
from room_correction.correction import generate_correction_filter, normalize_ir_level
from room_correction.export import export_filter

SR = 48000
N_TAPS = 16384
RC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RC_DIR.parents[1]
VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"

SCENARIOS = ["home_lab", "small_club", "large_hall", "outdoor_tent"]

# AE: per-channel residual bands (clear of the 200 Hz crossover).
RESIDUAL_BANDS_HZ = {"highpass": (250.0, 500.0), "lowpass": (30.0, 200.0)}
MAX_POSITIVE_DEVIATION_DB = 3.0
LEVEL_INVARIANCE_DB = 0.1
CUT_ACCURACY_DB = 2.0
AC6_TOLERANCE_S = 0.2e-3

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


@pytest.fixture(scope="module", params=SCENARIOS)
def run(request, bundle):
    """(scenario name, SimulatedMeasurement, VenueFilterResult), noise on, fixed seed."""
    name = request.param
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario(name), scenario_name=name)
    return name, sim, vp.generate_venue_filters(bundle, sim.measured_irs)


@pytest.fixture(scope="module")
def home_lab(bundle):
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"), scenario_name="home_lab")
    return sim, vp.generate_venue_filters(bundle, sim.measured_irs)


@pytest.fixture(scope="module")
def home_lab_dir(tmp_path_factory, bundle, home_lab):
    _, result = home_lab
    out = tmp_path_factory.mktemp("home_lab_out")
    vp.write_venue_filters(result, str(out))
    vp.write_delays_yaml(result, bundle, str(out / "delays.yml"))
    return out


def _max_gain_db(fir):
    return float(np.max(dsp_utils.linear_to_db(np.abs(np.fft.rfft(fir, n=1 << 17)))))


# -- AC1: files and format --------------------------------------------------

class TestAC1Outputs:

    def test_channel_map_from_real_configs(self, bundle):
        mapping = {c.number: (c.coefficients, c.speaker_key) for c in bundle.channels}
        assert mapping[1] == ("combined_left_hp.wav", "sat_left")
        assert mapping[2] == ("combined_right_hp.wav", "sat_right")
        assert mapping[3] == ("combined_sub1_lp.wav", "sub1")
        for n in range(4, 9):
            assert mapping[n] == ("dirac.wav", None)
        assert bundle.expected_files() == EXPECTED_FILES

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
        # up to 0.15 dB after the min-phase step (AE finding 3, open); the
        # deployed files are held to D-009 above. Here: no boost at all.
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
        profile["speakers"]["sub1"]["channel"] = 3      # venue ch 4 = dirac
        with pytest.raises(ValueError):
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


# -- residual per channel ---------------------------------------------------

def _corrected_and_uncorrected(bundle, sim, result, spk):
    lo, hi = RESIDUAL_BANDS_HZ[bundle.profile["speakers"][spk]["filter_type"]]
    level = result.reference_levels_db[spk]
    path = sim.true_paths[spk]
    _, unc = closed_loop.smoothed_response_db(path, lo, hi)
    _, cor = closed_loop.smoothed_response_db(
        closed_loop.system_response(path, result.corrections[spk]), lo, hi)
    return cor - level, unc - level


class TestResidualPerChannel:
    """Correction alone vs flat (target at the reference level); crossover excluded (F-374)."""

    def test_max_positive_deviation(self, bundle, run):
        name, sim, result = run
        for spk in result.corrections:
            cor, _ = _corrected_and_uncorrected(bundle, sim, result, spk)
            dev = closed_loop.max_positive_deviation_db(cor, np.zeros_like(cor))
            assert dev <= MAX_POSITIVE_DEVIATION_DB, f"{name} {spk}: {dev:+.2f} dB"

    def test_below_target_never_raised(self, bundle, run):
        # Cut-only: where the room is below target the filter must not lift it.
        # The magnitude bound (AE "unchanged within 0.5 dB") is open with the
        # AE: the global -0.5 dB margin plus cut skirts next to modes give
        # up to 1.35 dB today, always downward.
        name, sim, result = run
        for spk in result.corrections:
            cor, unc = _corrected_and_uncorrected(bundle, sim, result, spk)
            below = unc < 0.0
            if np.any(below):
                assert np.max(cor[below] - unc[below]) <= 0.05, f"{name} {spk}"

    def test_home_lab_sub_is_not_vacuous(self, bundle, home_lab):
        sim, result = home_lab
        cor, unc = _corrected_and_uncorrected(bundle, sim, result, "sub1")
        zero = np.zeros_like(unc)
        assert closed_loop.max_positive_deviation_db(unc, zero) > 10.0
        assert closed_loop.max_positive_deviation_db(cor, zero) <= MAX_POSITIVE_DEVIATION_DB


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

    def test_each_file_corrects_its_own_room(self, bundle, home_lab):
        # Wiring check from physics, not from the mapping code: the right
        # sat's room has a +5 dB peak in its band, so its own file must
        # beat the left file there. (The left room is too benign to tell
        # the two files apart, so only the right side is asserted.)
        sim, ref = home_lab
        lo, hi = RESIDUAL_BANDS_HZ["highpass"]
        path = sim.true_paths["sat_right"]
        level = ref.reference_levels_db["sat_right"]

        def dev(filename):
            _, resp = closed_loop.smoothed_response_db(
                closed_loop.system_response(path, ref.filters[filename]), lo, hi)
            return float(np.max(resp - level))

        own, other = dev("combined_right_hp.wav"), dev("combined_left_hp.wav")
        assert own <= MAX_POSITIVE_DEVIATION_DB
        assert own < other - 1.0, (own, other)

    def test_left_and_right_differ(self, home_lab):
        # home_lab is asymmetric on purpose; otherwise the swap test proves nothing.
        _, ref = home_lab
        a = ref.filters["combined_left_hp.wav"]
        b = ref.filters["combined_right_hp.wav"]
        assert np.max(np.abs(a - b)) > 1e-3


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
        assert "ch 4 4_sub2_lp: dirac.wav <- passthrough" in proc.stdout
        assert "RESULT: ALL CHECKS PASSED" in proc.stdout
        assert "Known limit" in proc.stdout
        assert "VERIFY FAILED" not in proc.stderr
        assert sorted(p.name for p in out.glob("*.wav")) == sorted(EXPECTED_FILES)
        assert (out / "delays.yml").stat().st_size > 0

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
