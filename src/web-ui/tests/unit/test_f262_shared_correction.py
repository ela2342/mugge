"""F-262: the measurement session and filter_routes build the same filters.

The session used the measured IR itself as the correction (F-262), and
filter_routes skipped the level normalization and the cut cap. Both now go
through correction_from_measurement(), uniform_d009_trim() and
run_correction_gate(). These tests drive both entry points with the same
simulated venue measurement and check:

- the session's closed loop passes on every channel and is reported;
- a bad measurement fails closed;
- session, filter_routes and the venue pipeline write the same samples.
"""

import contextlib
import copy
import dataclasses
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch

# Mock mode must be set before any app imports.
os.environ["PI_AUDIO_MOCK"] = "1"

_RC_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "room-correction"))
if _RC_DIR not in sys.path:
    sys.path.insert(0, _RC_DIR)

import numpy as np
import pytest
import soundfile as sf

from app import filter_routes
from app.measurement.session import ChannelConfig, MeasurementSession, SessionConfig
from mock import venue_sim
from room_correction import venue_pipeline as vp

REPO_ROOT = Path(_RC_DIR).parents[1]
VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"
PROFILE_NAME = "f262-parity"


@pytest.fixture(scope="module")
def bundle():
    return vp.load_venue_bundle(VENUE, PROFILE)


@pytest.fixture(scope="module")
def measured_irs(bundle):
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"),
        scenario_name="home_lab", noise_db=-60.0, noise_color="pink")
    # float32-exact, so the session's ir_*.wav export round-trips bit for
    # bit into filter_routes.
    return {k: ir.astype(np.float32).astype(np.float64)
            for k, ir in sim.measured_irs.items()}


@contextlib.contextmanager
def _patched_profile(bundle):
    """Serve bundle's profile by name; the .conf generator would read it from disk."""
    def load(name, profiles_dir=None, identities_dir=None):
        return bundle.profile, bundle.identities
    with patch("config_generator.load_profile_with_identities", side_effect=load), \
            patch("config_generator.validate_and_raise"), \
            patch("room_correction.pw_config_generator.generate_filter_chain_conf",
                  return_value="# mock PW conf"):
        yield


def _run_session(bundle, irs, output_dir):
    channels = [ChannelConfig(index=spk["channel"], name=k, speaker_key=k)
                for k, spk in bundle.profile["speakers"].items()]
    config = SessionConfig(channels=channels, output_dir=output_dir, positions=1,
                           profile_name=PROFILE_NAME)

    async def _noop(msg):
        pass

    session = MeasurementSession(config=config, ws_broadcast=_noop)
    for k, spk in bundle.profile["speakers"].items():
        if k in irs:
            session._impulse_responses[f"ch{spk['channel']}_pos0"] = irs[k]
    with _patched_profile(bundle):
        return session._filter_gen_sync()


def _samples(path):
    data, _ = sf.read(path, dtype="float32")
    return data


@pytest.fixture(scope="module")
def session_run(bundle, measured_irs, tmp_path_factory):
    root = tmp_path_factory.mktemp("f262")
    result = _run_session(bundle, measured_irs, str(root / "session" / PROFILE_NAME))
    return root, result


class TestSessionClosedLoop:

    def test_all_pass(self, session_run):
        assert session_run[1]["all_pass"] is True

    def test_every_channel_closed_loop_checked(self, session_run, bundle):
        verification = session_run[1]["verification"]
        assert {v["channel"] for v in verification} == set(bundle.profile["speakers"])
        for v in verification:
            assert v["closed_loop_pass"] is True, v
            assert v["d009_pass"] is True, v

    def test_reference_level_reported(self, session_run, bundle):
        for v in session_run[1]["verification"]:
            assert np.isfinite(v["reference_level_db"])
            assert tuple(v["ref_band_hz"]) == vp.reference_band(
                bundle.profile["speakers"][v["channel"]])

    def test_trim_reported(self, session_run):
        # AE F-262 item 4: the trim never raises gain, and every speaker FIR
        # peaks at or below -0.5 dB after it.
        assert session_run[1]["d009_trim_db"] <= 0.0
        for v in session_run[1]["verification"]:
            assert v["d009_peak_db"] <= -0.5, v


BANDPASS_REJECTED = ("Measurement rejected: room correction not supported for "
                     "bandpass (3-/4-way) profiles")


def _with_bandpass(bundle):
    profile = copy.deepcopy(bundle.profile)
    profile["speakers"]["sat_left"]["filter_type"] = "bandpass"
    return dataclasses.replace(bundle, profile=profile)


class TestSessionFailsClosed:

    def test_silent_measurement_rejected(self, bundle, measured_irs, tmp_path):
        irs = dict(measured_irs, sat_left=np.zeros_like(measured_irs["sat_left"]))
        with pytest.raises(RuntimeError, match="Measurement rejected for sat_left"):
            _run_session(bundle, irs, str(tmp_path))

    def test_bandpass_profile_rejected(self, bundle, measured_irs, tmp_path):
        """AE F-262 item 3: the text names the cause; nothing is written."""
        out = tmp_path / "out"
        with pytest.raises(RuntimeError, match=re.escape(BANDPASS_REJECTED)):
            _run_session(_with_bandpass(bundle), measured_irs, str(out))
        assert not out.exists() or not list(out.rglob("*.wav"))


class TestRoutesFailClosed:

    def test_bandpass_profile_rejected(self, bundle, tmp_path):
        req = filter_routes.FilterGenerateRequest(
            profile=PROFILE_NAME, mode="crossover_plus_correction",
            generate_pw_conf=False)
        with _patched_profile(_with_bandpass(bundle)), \
                patch.object(filter_routes, "DEFAULT_SESSION_DIR", str(tmp_path / "session")), \
                patch.object(filter_routes, "DEFAULT_OUTPUT_DIR", str(tmp_path / "routes")):
            with pytest.raises(ValueError, match=re.escape(BANDPASS_REJECTED)):
                filter_routes._run_pipeline(req)
        assert not (tmp_path / "routes").exists()


class TestParity:
    """Same measurement in, same samples out, on all three entry points."""

    @pytest.fixture(scope="class")
    def routes_result(self, session_run, bundle):
        root, _ = session_run
        req = filter_routes.FilterGenerateRequest(
            profile=PROFILE_NAME, mode="crossover_plus_correction",
            generate_pw_conf=False)
        with _patched_profile(bundle), \
                patch.object(filter_routes, "DEFAULT_SESSION_DIR", str(root / "session")), \
                patch.object(filter_routes, "DEFAULT_OUTPUT_DIR", str(root / "routes")):
            return filter_routes._run_pipeline(req)

    def test_routes_pass(self, routes_result):
        assert routes_result["all_pass"] is True
        assert all(v["closed_loop_pass"] for v in routes_result["verification"])

    def test_session_matches_filter_routes(self, session_run, routes_result):
        session = session_run[1]
        assert set(session["channels"]) == set(routes_result["channels"])
        for spk, path in session["channels"].items():
            np.testing.assert_array_equal(
                _samples(path), _samples(routes_result["channels"][spk]), err_msg=spk)
        assert session["d009_trim_db"] == routes_result["d009_trim_db"]

    def test_session_matches_venue_pipeline(self, session_run, bundle, measured_irs):
        result = vp.generate_venue_filters(bundle, measured_irs)
        assert set(bundle.speaker_files) == set(session_run[1]["channels"])
        for spk, path in session_run[1]["channels"].items():
            np.testing.assert_array_equal(
                _samples(path),
                result.filters[bundle.speaker_files[spk]].astype(np.float32),
                err_msg=spk)
