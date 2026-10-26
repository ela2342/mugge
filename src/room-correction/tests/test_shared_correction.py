"""F-262: one shared correction path, one uniform D-009 trim, one gate.

correction_from_measurement() is the only way to turn a measured IR into a
correction. generate_profile_filters() refuses anything else (TypeError).
uniform_d009_trim() scales all speaker channels by one gain.
run_correction_gate() = run_venue_checks() + a closed loop on the measured IR.
A source scan keeps the production call sites on that path.
"""

import ast
import copy
import dataclasses
import os
import re
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import venue_sim
from room_correction import closed_loop, combine, verify
from room_correction import venue_pipeline as vp
from room_correction.correction import (
    BANDPASS_NOT_SUPPORTED,
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
SRC_DIR = REPO_ROOT / "src"
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

    def test_bandpass_names_the_cause(self, sim):
        with pytest.raises(ValueError, match=re.escape(BANDPASS_NOT_SUPPORTED)):
            _correction(sim.measured_irs["sat_left"], {"filter_type": "bandpass"})


# -- bandpass profiles fail closed (AE item 3) -------------------------------

BANDPASS_REJECTED = ("Measurement rejected: room correction not supported for "
                     "bandpass (3-/4-way) profiles")


def _with_bandpass(bundle, spk="sat_left"):
    profile = copy.deepcopy(bundle.profile)
    profile["speakers"][spk]["filter_type"] = "bandpass"
    return dataclasses.replace(bundle, profile=profile)


class TestBandpassRejected:

    def test_text(self):
        with pytest.raises(ValueError, match=re.escape(BANDPASS_REJECTED)):
            vp.require_correctable({"mid": {"filter_type": "bandpass"}, "sub": LP})

    def test_two_way_accepted(self, bundle):
        vp.require_correctable(bundle.profile["speakers"])

    def test_venue_pipeline_rejects(self, bundle, sim):
        with pytest.raises(ValueError, match=re.escape(BANDPASS_REJECTED)):
            vp.generate_venue_filters(_with_bandpass(bundle), sim.measured_irs)


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

    @pytest.mark.parametrize("peaks_db", [
        (-6.0, -12.0), (-0.5, -3.0), (-0.49, -3.0), (0.0, -1.0), (2.0, -6.0), (20.0, 19.0)])
    def test_trim_never_raises_gain(self, peaks_db):
        """AE item 4: the trim is 0 or negative, and no peak ends above -0.5 dB."""
        filters = {f"s{i}": _peaking_fir(p) for i, p in enumerate(peaks_db)}
        trimmed, trim_db = combine.uniform_d009_trim(filters)
        assert trim_db <= 0.0
        for fir in trimmed.values():
            assert combine.max_gain_db(fir) <= combine.D009_TRIM_MARGIN_DB + 1e-9

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
        # AE item 1: the 500-4000 Hz deviations are logged, not gated.
        assert result.details["log_band_hz"] == (500.0, 4000.0)
        assert np.isfinite(result.details["log_corrected_max_db"])
        assert np.isfinite(result.details["log_uncorrected_max_db"])
        assert "log only 500-4000 Hz" in result.message

    def test_log_band_never_gates(self, bundle, sim, monkeypatch):
        """A huge HF deviation changes the log, not the verdict."""
        speaker = bundle.profile["speakers"]["sat_left"]
        ir = sim.measured_irs["sat_left"]
        cf = _correction(ir, speaker)
        band = verify.closed_loop_band(speaker)
        before = verify.verify_closed_loop(ir, cf, band)
        real = closed_loop.max_positive_deviation_db
        lo, hi = verify.CLOSED_LOOP_LOG_BAND_HZ

        def inflated(response, target):
            dev = real(response, target)
            return dev + 40.0 if len(response) == n_log else dev
        n_log = len(closed_loop.smoothed_response_db(ir, lo, hi)[0])
        assert n_log != len(closed_loop.smoothed_response_db(ir, *band)[0])
        monkeypatch.setattr(closed_loop, "max_positive_deviation_db", inflated)
        after = verify.verify_closed_loop(ir, cf, band)
        assert after.passed == before.passed is True
        assert after.details["log_corrected_max_db"] == pytest.approx(
            before.details["log_corrected_max_db"] + 40.0)

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


# -- source scan (F6, Architect ruling dfffcfbf) -------------------------------

# Only the shared function may build a correction.
SHARED = ("room-correction/room_correction/correction.py", "correction_from_measurement")
SHARED_ONLY = {"generate_correction_filter", "normalize_ir_level"}
# The old heuristic gate, directly or through run_all_checks (verify.py:487).
FORBIDDEN = SHARED_ONLY | {"verify_minimum_phase", "run_all_checks"}
# Legacy CLIs: exact (file, def) -> callees. Every callee must still be
# called there (a stale entry fails), so this list can only shrink. PM
# backlog: retire or re-route them, then empty it.
LEGACY_ALLOWLIST = {
    ("room-correction/runner.py", "run_full_pipeline"):
        {"generate_correction_filter", "run_all_checks"},
    ("room-correction/runner.py", "run_stage_correct"): {"generate_correction_filter"},
    ("room-correction/runner.py", "run_stage_verify"): {"verify_minimum_phase"},
    ("room-correction/room_correction/verify.py", "run_all_checks"): {"verify_minimum_phase"},
    ("room-correction/generate_bose_filters.py", "verify_all"): {"verify_minimum_phase"},
}
# Quarantine: deployed code never imports the legacy CLIs.
QUARANTINED_MODULES = {"runner", "generate_bose_filters"}
QUARANTINED_FROM = ("web-ui/", "room-correction/room_correction/")


def _production_sources(src_dir=SRC_DIR):
    for path in sorted(src_dir.rglob("*.py")):
        rel = path.relative_to(src_dir).as_posix()
        if "/tests/" in f"/{rel}" or rel.startswith("room-correction/mock/"):
            continue
        yield rel, path


def _scan(rel, source):
    """Calls and imports in one file.

    Returns (uses, modules): uses is a list of (name, enclosing def, kind)
    for every name(...), module.name(...) and ``from x import name``;
    modules is every imported module name (each dotted part).
    """
    uses, modules = [], []

    def visit(node, func):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node.name
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            uses.append((name, func, "call"))
        elif isinstance(node, ast.ImportFrom):
            modules.extend((node.module or "").split("."))
            for alias in node.names:
                uses.append((alias.name, func, "import"))
                modules.append(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.extend(alias.name.split("."))
        for child in ast.iter_child_nodes(node):
            visit(child, func)

    visit(ast.parse(source, filename=rel), None)
    return uses, modules


def _violations(sources):
    """Scan (rel, source) pairs; return the list of F6 violations."""
    offenders, seen = [], set()
    for rel, source in sources:
        uses, modules = _scan(rel, source)
        allowed_here = set().union(*[c for (f, _), c in LEGACY_ALLOWLIST.items() if f == rel])
        for name, func, kind in uses:
            if name not in FORBIDDEN:
                continue
            if (rel, func) == SHARED and name in SHARED_ONLY:
                continue
            if rel == SHARED[0] and kind == "import":
                continue
            if kind == "call" and name in LEGACY_ALLOWLIST.get((rel, func), ()):
                seen.add((rel, func, name))
                continue
            if kind == "import" and name in allowed_here:
                continue
            offenders.append(f"{rel}:{func} {kind}s {name}")
        if rel.startswith(QUARANTINED_FROM):
            for module in QUARANTINED_MODULES.intersection(modules):
                offenders.append(f"{rel} imports quarantined {module}")
    for (rel, func), callees in sorted(LEGACY_ALLOWLIST.items()):
        for name in sorted(callees):
            if (rel, func, name) not in seen:
                offenders.append(f"stale allowlist entry: {rel}:{func} {name}")
    return offenders


def _sources():
    return [(rel, path.read_text()) for rel, path in _production_sources()]


def test_source_scan_finds_the_files():
    names = {rel for rel, _ in _production_sources()}
    assert {SHARED[0], "room-correction/room_correction/venue_pipeline.py",
            "room-correction/runner.py", "web-ui/app/measurement/session.py",
            "web-ui/app/filter_routes.py"} <= names
    assert not any("/tests/" in f"/{rel}" or rel.startswith("room-correction/mock/")
                   for rel in names)


def test_source_scan_clean():
    offenders = _violations(_sources())
    assert not offenders, offenders


def _mutated(rel, old, new):
    sources = dict(_sources())
    assert sources[rel].count(old) == 1, (rel, old)
    sources[rel] = sources[rel].replace(old, new)
    return list(sources.items())


class TestSourceScanTeeth:
    """The Architect's F6 mutations (a)-(c), plus the shared-function rule."""

    def test_min_phase_in_venue_runner_fails(self):
        offenders = _violations(_mutated(
            "room-correction/runner.py", "def run_venue_pipeline(args):\n",
            "def run_venue_pipeline(args):\n    verify.verify_minimum_phase(None)\n"))
        assert "room-correction/runner.py:run_venue_pipeline calls verify_minimum_phase" in offenders

    def test_web_ui_importing_runner_fails(self):
        rel = "web-ui/app/filter_routes.py"
        offenders = _violations(_mutated(
            rel, "import asyncio\n", "import asyncio\nfrom runner import run_stage_correct\n"))
        assert f"{rel} imports quarantined runner" in offenders

    def test_stale_allowlist_entry_fails(self):
        offenders = _violations(_mutated(
            "room-correction/runner.py",
            "    results.append(verify.verify_minimum_phase(args.filter))\n", ""))
        assert offenders == [
            "stale allowlist entry: room-correction/runner.py:run_stage_verify verify_minimum_phase"]

    def test_correction_outside_shared_function_fails(self):
        rel = "web-ui/app/measurement/session.py"
        offenders = _violations(_mutated(
            rel, "        measured_irs = self._measured_irs(profile)\n",
            "        measured_irs = self._measured_irs(profile)\n"
            "        generate_correction_filter(None)\n"))
        assert f"{rel}:_filter_gen_sync calls generate_correction_filter" in offenders
