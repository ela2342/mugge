"""F-262: one shared correction path, one uniform D-009 trim, one gate.

correction_from_measurement() is the only way to turn a measured IR into a
correction. generate_profile_filters() refuses anything else (TypeError).
uniform_d009_trim() scales all speaker channels by one gain.
run_correction_gate() = run_venue_checks() + a closed loop on the measured IR.
A source scan keeps the production call sites on that path.
"""

import ast
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import venue_sim
from room_correction import combine, verify
from room_correction import venue_pipeline as vp
from room_correction.correction import (
    MAX_CUT_DB,
    CorrectionFilter,
    correction_from_measurement,
    generate_correction_filter,
    normalize_ir_level,
    reference_band,
)
from room_correction.generate_profile_filters import generate_profile_filters

SR = 48000
N_TAPS = 16384
RC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RC_DIR.parents[1]
APP_DIR = REPO_ROOT / "src" / "web-ui" / "app"
VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"

HP = {"filter_type": "highpass"}
LP = {"filter_type": "lowpass"}


@pytest.fixture(scope="module")
def bundle():
    return vp.load_venue_bundle(VENUE, PROFILE)


@pytest.fixture(scope="module")
def sim(bundle):
    return venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"),
        scenario_name="home_lab", noise_db=-60.0, noise_color="pink")


def _correction(ir, speaker):
    return correction_from_measurement(
        ir, speaker, target_curve="flat", n_taps=N_TAPS, sr=SR)


# -- correction_from_measurement -------------------------------------------

class TestCorrectionFromMeasurement:

    @pytest.mark.parametrize("ir, match", [
        (np.zeros((2, 4096)), "1-D"),
        (np.zeros(0), "1-D"),
        (np.full(4096, np.nan), "non-finite"),
        (np.zeros(4096), "silent"),
    ])
    def test_bad_ir_raises(self, ir, match):
        with pytest.raises(ValueError, match=match):
            _correction(ir, HP)

    @pytest.mark.parametrize("filter_type", ["bandpass", "allpass"])
    def test_no_reference_band_raises(self, filter_type, sim):
        with pytest.raises(ValueError, match="reference band"):
            _correction(sim.measured_irs["sat_left"], {"filter_type": filter_type})

    def test_is_normalize_then_capped_correction(self, sim):
        ir = sim.measured_irs["sub1"]
        cf = _correction(ir, LP)
        normalized, level_db = normalize_ir_level(ir, reference_band(LP), sr=SR)
        expected = generate_correction_filter(
            normalized, n_taps=N_TAPS, sr=SR, max_cut_db=MAX_CUT_DB)
        assert isinstance(cf, CorrectionFilter)
        assert len(cf.fir) == N_TAPS
        assert cf.reference_level_db == level_db
        assert cf.ref_band_hz == reference_band(LP)
        np.testing.assert_array_equal(cf.fir, expected)

    def test_level_invariant(self, sim):
        """The measurement's absolute level never reaches the correction."""
        ir = sim.measured_irs["sub1"]
        loud = _correction(ir * 10.0, LP)
        quiet = _correction(ir, LP)
        assert loud.reference_level_db == pytest.approx(quiet.reference_level_db + 20.0)
        np.testing.assert_allclose(loud.fir, quiet.fir, rtol=0, atol=1e-9)

    def test_deterministic(self, sim):
        ir = sim.measured_irs["sat_left"]
        np.testing.assert_array_equal(_correction(ir, HP).fir, _correction(ir, HP).fir)


# -- generate_profile_filters type gate --------------------------------------

class TestTypeGate:

    def test_ndarray_correction_raises(self, bundle, sim):
        with pytest.raises(TypeError, match="correction_from_measurement"):
            generate_profile_filters(
                profile=bundle.profile, identities=bundle.identities,
                correction_filters={"sub1": sim.measured_irs["sub1"]},
                n_taps=N_TAPS, sr=SR)

    def test_correction_filter_accepted(self, bundle, sim):
        filters = generate_profile_filters(
            profile=bundle.profile, identities=bundle.identities,
            correction_filters={"sub1": _correction(sim.measured_irs["sub1"], LP)},
            n_taps=N_TAPS, sr=SR)
        assert set(filters) == set(bundle.profile["speakers"])


# -- uniform D-009 trim (S5) -------------------------------------------------

def _peaking_fir(peak_db):
    fir = np.zeros(4096)
    fir[0] = 10 ** (peak_db / 20.0)
    return fir


class TestUniformTrim:

    def test_below_margin_untouched(self):
        filters = {"a": _peaking_fir(-3.0), "b": _peaking_fir(-6.0)}
        trimmed, trim_db = combine.uniform_d009_trim(filters)
        assert trim_db == 0.0
        for k in filters:
            np.testing.assert_array_equal(trimmed[k], filters[k])

    def test_loudest_lands_on_margin(self):
        trimmed, trim_db = combine.uniform_d009_trim(
            {"a": _peaking_fir(2.0), "b": _peaking_fir(-6.0)})
        assert trim_db == pytest.approx(combine.D009_TRIM_MARGIN_DB - 2.0)
        assert combine.max_gain_db(trimmed["a"]) == pytest.approx(combine.D009_TRIM_MARGIN_DB)

    def test_balance_kept(self):
        """One gain for all: a per-channel re-clip would leave b at -6 dB."""
        filters = {"a": _peaking_fir(2.0), "b": _peaking_fir(-6.0)}
        trimmed, trim_db = combine.uniform_d009_trim(filters)
        assert combine.max_gain_db(trimmed["b"]) == pytest.approx(-6.0 + trim_db)
        assert (combine.max_gain_db(trimmed["a"]) - combine.max_gain_db(trimmed["b"])
                == pytest.approx(8.0))

    def test_non_finite_raises(self):
        with pytest.raises(ValueError, match="non-finite"):
            combine.uniform_d009_trim({"a": np.full(4096, np.inf)})


# -- closed-loop gate (S6) ---------------------------------------------------

class TestClosedLoop:

    @pytest.mark.parametrize("spk", ["sat_left", "sat_right", "sub1"])
    def test_real_correction_passes(self, bundle, sim, spk):
        speaker = bundle.profile["speakers"][spk]
        ir = sim.measured_irs[spk]
        result = verify.verify_closed_loop(
            ir, _correction(ir, speaker), verify.closed_loop_band(speaker))
        assert result.passed, result.message

    @pytest.mark.parametrize("spk", ["sat_left", "sat_right", "sub1"])
    def test_raw_ir_as_correction_fails(self, bundle, sim, spk):
        """The F-262 bug: the measured IR itself used as the correction."""
        speaker = bundle.profile["speakers"][spk]
        ir = sim.measured_irs[spk]
        real = _correction(ir, speaker)
        raw = CorrectionFilter(fir=ir[:N_TAPS].copy(),
                               reference_level_db=real.reference_level_db,
                               ref_band_hz=real.ref_band_hz)
        result = verify.verify_closed_loop(ir, raw, verify.closed_loop_band(speaker))
        assert not result.passed

    def test_non_finite_fails(self, sim):
        ir = sim.measured_irs["sub1"]
        bad = CorrectionFilter(fir=np.full(N_TAPS, np.nan), reference_level_db=0.0,
                               ref_band_hz=reference_band(LP))
        assert not verify.verify_closed_loop(ir, bad, verify.closed_loop_band(LP)).passed

    def test_gate_refuses_closed_loop_on_non_fir(self, tmp_path, sim):
        cf = _correction(sim.measured_irs["sub1"], LP)
        with pytest.raises(ValueError, match="not 'fir'"):
            verify.run_correction_gate(
                str(tmp_path), {"dirac.wav": "dirac"},
                closed_loop_inputs={"dirac.wav": (sim.measured_irs["sub1"], cf, LP)})


# -- venue pipeline parity ---------------------------------------------------

def test_venue_pipeline_uses_shared_function(bundle, sim):
    result = vp.generate_venue_filters(bundle, sim.measured_irs)
    for spk, speaker in bundle.profile["speakers"].items():
        expected = correction_from_measurement(
            sim.measured_irs[spk], speaker,
            target_curve=bundle.profile.get("target_curve", "flat"), n_taps=N_TAPS, sr=SR)
        np.testing.assert_array_equal(result.corrections[spk], expected.fir)
    assert len(result.closed_loop_inputs) == len(bundle.profile["speakers"])


# -- source scan -------------------------------------------------------------

def _production_sources():
    for root in (RC_DIR, APP_DIR):
        for path in sorted(root.rglob("*.py")):
            rel = path.relative_to(root).parts
            if rel[0] in ("tests", "mock") or path.name.startswith("test_"):
                continue
            yield path


def _calls(path):
    """(callee name, enclosing function name) for every call in *path*."""
    tree = ast.parse(path.read_text(), filename=str(path))
    found = []

    def visit(node, func):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node.name
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            found.append((name, func))
        for child in ast.iter_child_nodes(node):
            visit(child, func)

    visit(tree, None)
    return found


# Legacy CLIs outside the venue/session/route paths. Their status is pending
# an AE + Architect ruling (w4-setA-impl-questions); they stay listed, by
# function, so any new caller still fails this scan.
LEGACY_CORRECTION_CALLERS = {
    ("runner.py", "run_full_pipeline"),
    ("runner.py", "run_stage_correct"),
}
LEGACY_MIN_PHASE_CALLERS = {
    ("runner.py", "run_stage_verify"),
    ("verify.py", "run_all_checks"),
    ("generate_bose_filters.py", "verify_all"),
}


def test_source_scan_finds_the_files():
    names = {p.name for p in _production_sources()}
    assert {"correction.py", "venue_pipeline.py", "session.py", "filter_routes.py"} <= names


def test_correction_only_via_shared_function():
    offenders = []
    for path in _production_sources():
        for name, func in _calls(path):
            if name not in ("generate_correction_filter", "normalize_ir_level"):
                continue
            if (path.name, func) == ("correction.py", "correction_from_measurement"):
                continue
            if (path.name, func) in LEGACY_CORRECTION_CALLERS:
                continue
            offenders.append(f"{path.name}:{func} calls {name}")
    assert not offenders, offenders


def test_verify_minimum_phase_is_no_gate():
    offenders = [f"{path.name}:{func}"
                 for path in _production_sources()
                 for name, func in _calls(path)
                 if name == "verify_minimum_phase"
                 and (path.name, func) not in LEGACY_MIN_PHASE_CALLERS]
    assert not offenders, offenders
