"""Gating tests for the F-383 step-4 combine (fence 99de4381 D4, Architect ace87e0d a3).

The composition row gates every cascade channel, the residual row every
other 'fir' file. On the shipped filters:
- c) the gross mutants N1, N2, N3, N5 and a rising tail fail the
  composition row of a cascade sub; m1: a 10-sample shift fails on
  residual, a polarity flip on polarity;
- C3.3: a cascade sub gated without composition_inputs gets the residual
  row (fail-closed);
- d) every channel of every buildable profile passes run_correction_gate()
  with composition_inputs, on the dirac path and, for the two PA profiles,
  on the venue path in the four scenarios. Closed Loop per the AE's Q1
  ruling (ebf8fad5): corrected <= uncorrected everywhere (R2), a full pass
  in home_lab and outdoor_tent (R3), print-only in small_club and
  large_hall (R4, F-489).
"""

import dataclasses
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config_generator
from mock import venue_sim
from room_correction import combine, verify
from room_correction import generate_profile_filters as gpf
from room_correction import venue_pipeline as vp
from room_correction.export import export_filter

SR = 48000
N_TAPS = 16384
REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILES_DIR = REPO_ROOT / "configs" / "speakers" / "profiles"
VENUE = REPO_ROOT / "configs" / "venues" / "production.yml"
UNBUILDABLE = {"2way-80hz-ported", "workshop-xrk10f-fullrange"}
PROFILES = sorted(p.stem for p in PROFILES_DIR.glob("*.yml") if p.stem not in UNBUILDABLE)
PA_PROFILES = ["2way-80hz-sealed", "pa-2way-80hz-lavoce"]
SCENARIOS = ["home_lab", "small_club", "large_hall", "outdoor_tent"]
# Q1 R3/R4 (ebf8fad5): the HP mains miss the 3 dB limit in the larger rooms (F-489).
CLOSED_LOOP_FULL_PASS = {"home_lab", "outdoor_tent"}

MUTANTS = {
    "N1-linear-phase": lambda h: np.roll(np.fft.irfft(np.abs(np.fft.rfft(h)), n=len(h)),
                                         len(h) // 2),
    "N2-time-reversed": lambda h: h[::-1].copy(),
    "N3-shift-n/2": lambda h: np.roll(h, len(h) // 2),
    "N5-delay-200": lambda h: np.concatenate([np.zeros(200), h[:-200]]),
}


def _shipped(profile_name):
    """Uniform-trimmed dirac-path filters, filename -> FIR, plus the gate inputs."""
    profile, identities = config_generator.load_profile_with_identities(profile_name)
    filters, _ = combine.uniform_d009_trim(
        gpf.generate_profile_filters(profile, identities, n_taps=N_TAPS, sr=SR))
    filenames = {spk: f"{spk}.wav" for spk in filters}
    inputs = gpf.composition_inputs_by_file(
        profile, identities, filenames, n_taps=N_TAPS, sr=SR)
    hpf = verify.mandatory_hpf_by_file(profile, identities, filenames)
    return {filenames[spk]: fir for spk, fir in filters.items()}, inputs, hpf


def _row(tmp_path, fir, factors):
    path = str(tmp_path / "x.wav")
    export_filter(fir, path, n_taps=N_TAPS)
    return verify.verify_minimum_phase_composition(path, factors)


def _min_phase_rows(results):
    return [r for r in results if r.name.startswith("Minimum Phase")]


def _print_rows(label, results):
    for r in _min_phase_rows(results):
        d = r.details
        cres = f"{d['composition_db']:7.1f}" if "composition_db" in d else "      -"
        print(f"{label}: {r.name}: cres {cres} dB, residual {d['residual_db']:6.1f} dB, "
              f"tail {d['tail_db']:7.1f} dB")


# -- c) and m1: mutants of the shipped cascade sub fail --------------------------

@pytest.mark.parametrize("profile_name", PA_PROFILES)
class TestShippedCascadeMutants:

    @pytest.mark.parametrize("mutant", list(MUTANTS.values()), ids=list(MUTANTS))
    def test_gross_mutant_fails_on_residual(self, tmp_path, profile_name, mutant):
        filters, inputs, _ = _shipped(profile_name)
        result = _row(tmp_path, mutant(filters["sub1.wav"]), inputs["sub1.wav"])
        assert not result.passed
        assert "residual" in result.details["failed"], result.message
        assert result.details["composition_db"] > verify.COMPOSITION_MAX_RESIDUAL_DB

    def test_rising_tail_fails_on_decay(self, tmp_path, profile_name):
        filters, inputs, _ = _shipped(profile_name)
        h = filters["sub1.wav"].astype(np.float64)
        n_tail = N_TAPS // 20
        # The shipped tail decays slowly: give the last 5% twice the energy of taps 90-95%.
        prev = np.sum(h[-2 * n_tail:-n_tail] ** 2)
        h[-n_tail:] += np.sqrt(2.0 * prev / n_tail)
        result = _row(tmp_path, h, inputs["sub1.wav"])
        assert not result.passed
        assert "rising tail" in result.details["failed"], result.message

    def test_shift_10_fails_on_residual(self, tmp_path, profile_name):
        filters, inputs, _ = _shipped(profile_name)
        late = np.concatenate([np.zeros(10), filters["sub1.wav"][:-10]])
        result = _row(tmp_path, late, inputs["sub1.wav"])
        assert result.details["failed"] == ["residual"], result.message

    def test_polarity_flip_fails_on_polarity(self, tmp_path, profile_name):
        filters, inputs, _ = _shipped(profile_name)
        result = _row(tmp_path, -filters["sub1.wav"], inputs["sub1.wav"])
        assert result.details["failed"] == ["polarity"], result.message


# -- C3.3: no composition_inputs, the residual row, fail-closed -------------------

@pytest.mark.parametrize("profile_name", PA_PROFILES)
def test_cascade_without_inputs_gets_residual_row(tmp_path, profile_name):
    """A cascade sub gated without its factors is not waved through."""
    filters, inputs, hpf = _shipped(profile_name)
    assert "sub1.wav" in inputs
    export_filter(filters["sub1.wav"], str(tmp_path / "sub1.wav"), n_taps=N_TAPS)
    passed, results = verify.run_correction_gate(
        str(tmp_path), {"sub1.wav": "fir"},
        mandatory_hpf_hz={k: v for k, v in hpf.items() if k == "sub1.wav"})
    _print_rows(f"C3.3 {profile_name}", results)
    rows = _min_phase_rows(results)
    assert [r.name for r in rows] == ["Minimum Phase (residual) (sub1.wav)"]
    assert not rows[0].passed and not passed, rows[0].message


# -- d) every channel passes the gate --------------------------------------------

@pytest.mark.parametrize("profile_name", PROFILES)
def test_dirac_path_passes_gate(tmp_path, profile_name):
    filters, inputs, hpf = _shipped(profile_name)
    for filename, fir in filters.items():
        export_filter(fir, str(tmp_path / filename), n_taps=N_TAPS)
    passed, results = verify.run_correction_gate(
        str(tmp_path), {f: "fir" for f in filters}, mandatory_hpf_hz=hpf,
        composition_inputs=inputs)
    _print_rows(f"dirac {profile_name}", results)
    assert passed, [r.message for r in results if not r.passed]
    for filename in filters:
        row = "composition" if filename in inputs else "residual"
        assert [r.name for r in _min_phase_rows(results) if r.name.endswith(f"({filename})")] \
            == [f"Minimum Phase ({row}) ({filename})"]


def _venue_gate(tmp_path, profile_name, scenario, mutate=None):
    bundle = vp.load_venue_bundle(VENUE, PROFILES_DIR / f"{profile_name}.yml")
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario(scenario),
        scenario_name=scenario, noise_db=-60.0, noise_color="pink")
    result = vp.generate_venue_filters(bundle, sim.measured_irs)
    vp.write_venue_filters(result, str(tmp_path))
    closed_loop_inputs = dict(result.closed_loop_inputs)
    if mutate:
        closed_loop_inputs = mutate(closed_loop_inputs)
    passed, results = verify.run_correction_gate(
        str(tmp_path), bundle.expected_files(),
        closed_loop_inputs=closed_loop_inputs,
        mandatory_hpf_hz=bundle.mandatory_hpf_by_file(),
        target_curve=bundle.profile.get("target_curve", "flat"),
        composition_inputs=result.composition_inputs)
    return bundle, result, closed_loop_inputs, passed, results


def _closed_loop_harm(results, closed_loop_inputs):
    """Q1 R2: files whose Closed Loop row is missing, empty, non-finite or worse than uncorrected."""
    harm = []
    for filename in sorted(closed_loop_inputs):
        rows = [r for r in results if r.name == f"Closed Loop ({filename})"]
        d = rows[0].details if len(rows) == 1 else {}
        corrected, uncorrected = d.get("corrected_max_db"), d.get("uncorrected_max_db")
        if corrected is None or uncorrected is None \
                or not np.isfinite(corrected) or not np.isfinite(uncorrected) \
                or not corrected <= uncorrected:
            harm.append(filename)
    return harm


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("profile_name", PA_PROFILES)
def test_venue_path_passes_gate(tmp_path, profile_name, scenario):
    bundle, result, closed_loop_inputs, passed, results = _venue_gate(
        tmp_path, profile_name, scenario)
    _print_rows(f"venue {profile_name} {scenario}", results)
    for r in results:
        if r.name.startswith("Closed Loop"):
            print(f"venue {profile_name} {scenario}: {r.name}: "
                  f"{'PASS' if r.passed else 'FAIL'} {r.message}")
    # R1: every row but Closed Loop passes.
    assert all(r.passed for r in results if not r.name.startswith("Closed Loop")), \
        [r.message for r in results if not r.passed]
    # R2: the Closed Loop row never makes things worse, in every scenario.
    assert closed_loop_inputs
    assert _closed_loop_harm(results, closed_loop_inputs) == []
    # R3: a full pass where the HP mains meet the limit; R4 (F-489): print only elsewhere.
    if scenario in CLOSED_LOOP_FULL_PASS:
        assert passed, [r.message for r in results if not r.passed]
        for filename in bundle.expected_files():
            assert verify.gate_summary(filename, results)["all_pass"], filename
    assert result.composition_inputs
    for filename, kind in bundle.expected_files().items():
        if kind != "fir":
            continue
        row = "composition" if filename in result.composition_inputs else "residual"
        assert [r.name for r in _min_phase_rows(results) if r.name.endswith(f"({filename})")] \
            == [f"Minimum Phase ({row}) ({filename})"]


def _inverted(correction):
    """A filter that applies the room: the correction's inverse, peak-normalised."""
    n = len(correction.fir)
    spectrum = np.fft.rfft(correction.fir, 4 * n)
    floor = 1e-3 * np.max(np.abs(spectrum))
    spectrum = np.where(np.abs(spectrum) < floor, floor * np.exp(1j * np.angle(spectrum)), spectrum)
    fir = np.fft.irfft(1.0 / spectrum, 4 * n)[:n]
    return dataclasses.replace(correction, fir=fir / np.max(np.abs(fir)))


def test_closed_loop_harm_mutant_fails(tmp_path):
    """Q1 R6: an inverted correction on every channel in home_lab trips the R2 check."""
    def mutate(inputs):
        return {f: (ir, _inverted(c), spk) for f, (ir, c, spk) in inputs.items()}

    _, _, inputs, passed, results = _venue_gate(
        tmp_path, "2way-80hz-sealed", "home_lab", mutate=mutate)
    for r in results:
        if r.name.startswith("Closed Loop"):
            print(f"R6 mutant: {r.name}: {r.message}")
    assert not passed
    assert _closed_loop_harm(results, inputs) == sorted(inputs)
