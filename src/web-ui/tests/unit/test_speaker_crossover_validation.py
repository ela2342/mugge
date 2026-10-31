"""F-374: crossover type/slope are checked by the generator's own validator.

The speaker editor save, the Filters tab Generate and the measurement
session start all run ``validate_profile_crossover`` from
``room_correction.generate_profile_filters`` -- no copied list of supported
values.  Covers:
    - Save rejects an unsupported slope or type with the generator's message;
      a valid profile still saves.
    - A stored unsupported profile loads unchanged; saving it is rejected and
      the file on disk is never rewritten.
    - speaker-config.js VALID_SLOPES / VALID_XOVER_TYPES equal the Python
      constants (parity).
    - Every profile shipped in configs/speakers/profiles passes the validator.
    - Generate returns 400 (not 500) with the same message.
    - A measurement session on an unsupported profile fails before any gain
      calibration or sweep.
"""

import asyncio
import json
import re
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import yaml
from starlette.testclient import TestClient

from app.main import app
from app.measurement.session import (
    ChannelConfig, MeasurementSession, MeasurementState, SessionConfig,
)
from room_correction.crossover import (
    CROSSOVER_TYPES, CrossoverSpecError, LR_SLOPES_DB_PER_OCT,
)
from room_correction.generate_profile_filters import validate_profile_crossover

REPO_ROOT = Path(__file__).resolve().parents[4]
SHIPPED_PROFILES = sorted(
    (REPO_ROOT / "configs" / "speakers" / "profiles").glob("*.yml"))
SHIPPED_IDENTITIES = REPO_ROOT / "configs" / "speakers" / "identities"
SPEAKER_CONFIG_JS = (
    Path(__file__).resolve().parents[2] / "static" / "js" / "speaker-config.js")

SLOPE_96_MESSAGE = "Linkwitz-Riley crossover supports 24 or 48 dB/oct, got 96"
TYPE_LR4_MESSAGE = "Unknown crossover type 'LR4'; expected 'linkwitz-riley'"

_PROFILE = {
    "name": "Crossover Test Profile",
    "topology": "2way",
    "crossover": {"frequency_hz": 80, "slope_db_per_oct": 48,
                  "type": "linkwitz-riley"},
    "speakers": {
        "sat_left": {"identity": "test-spk", "role": "satellite", "channel": 0},
        "sub1": {"identity": "test-sub", "role": "subwoofer", "channel": 2},
    },
}


def _with_crossover(profile, **changes):
    return {**profile, "crossover": {**profile["crossover"], **changes}}


def _generator_message(profile):
    with pytest.raises(CrossoverSpecError) as exc:
        validate_profile_crossover(profile)
    return str(exc.value)


def _run(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


@pytest.fixture
def speakers_dir(tmp_path, monkeypatch):
    """Temp speakers dir with one valid and one stored slope-96 profile."""
    (tmp_path / "identities").mkdir()
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "good.yml").write_text(yaml.dump(_PROFILE, sort_keys=False))
    bad = _with_crossover(_PROFILE, slope_db_per_oct=96, type="LR4")
    (profiles / "bad-96.yml").write_text(yaml.dump(bad, sort_keys=False))
    import app.speaker_routes as mod
    monkeypatch.setattr(mod, "_speakers_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def client(speakers_dir):
    return TestClient(app)


class TestSaveUsesGeneratorCheck:
    """POST/PUT /profiles return the generator's own message."""

    def test_slope_96_rejected_with_generator_message(self, client):
        body = {**_with_crossover(_PROFILE, slope_db_per_oct=96), "slug": "s96"}
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 422
        assert resp.json()["error"] == "validation"
        assert resp.json()["detail"] == SLOPE_96_MESSAGE
        assert resp.json()["detail"] == _generator_message(body)

    def test_unknown_type_rejected_with_generator_message(self, client):
        body = {**_with_crossover(_PROFILE, type="LR4"), "slug": "lr4"}
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 422
        assert resp.json()["error"] == "validation"
        assert resp.json()["detail"] == TYPE_LR4_MESSAGE
        assert resp.json()["detail"] == _generator_message(body)

    def test_bandpass_high_slope_rejected(self, client):
        body = {**_PROFILE, "slug": "bp96", "speakers": {
            **_PROFILE["speakers"],
            "mid": {"identity": "test-spk", "role": "midrange", "channel": 1,
                    "filter_type": "bandpass", "high_slope_db_per_oct": 96},
        }}
        body = _with_crossover(body, frequency_hz=[80, 2000])
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 422
        assert resp.json()["detail"] == SLOPE_96_MESSAGE

    def test_crossover_list_section_checked(self, client):
        body = {**_PROFILE, "slug": "xlist", "crossover": [
            _PROFILE["crossover"],
            {**_PROFILE["crossover"], "slope_db_per_oct": 96},
        ]}
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 422
        assert resp.json()["detail"] == SLOPE_96_MESSAGE

    @pytest.mark.parametrize("slope", [24, 48, 24.0, 48.0])
    def test_valid_profile_saves(self, client, slope):
        slug = f"ok-{int(slope)}-{type(slope).__name__}"
        body = {**_with_crossover(_PROFILE, slope_db_per_oct=slope), "slug": slug}
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 201, resp.json()

    def test_put_slope_96_rejected(self, client, speakers_dir):
        path = speakers_dir / "profiles" / "good.yml"
        before = path.read_bytes()
        resp = client.put("/api/v1/speakers/profiles/good",
                          json=_with_crossover(_PROFILE, slope_db_per_oct=96))
        assert resp.status_code == 422
        assert resp.json()["error"] == "validation"
        assert resp.json()["detail"] == SLOPE_96_MESSAGE
        assert path.read_bytes() == before

    @pytest.mark.parametrize("slope", ["48", None, True])
    def test_non_numeric_slope_rejected(self, client, slope):
        body = {**_with_crossover(_PROFILE, slope_db_per_oct=slope), "slug": "nn"}
        resp = client.post("/api/v1/speakers/profiles", json=body)
        assert resp.status_code == 422
        assert resp.json()["detail"].startswith(
            "Linkwitz-Riley crossover supports 24 or 48 dB/oct, got ")


class TestStoredUnsupportedProfile:
    """A stored slope-96 / type-LR4 profile loads, never gets rewritten."""

    def test_get_returns_stored_values_unchanged(self, client):
        resp = client.get("/api/v1/speakers/profiles/bad-96")
        assert resp.status_code == 200
        xo = resp.json()["crossover"]
        assert xo["slope_db_per_oct"] == 96
        assert xo["type"] == "LR4"

    def test_list_includes_stored_profile(self, client):
        resp = client.get("/api/v1/speakers/profiles")
        assert resp.status_code == 200
        assert "bad-96" in [p["name"] for p in resp.json()["profiles"]]

    def test_save_unchanged_is_rejected_and_file_untouched(self, client,
                                                           speakers_dir):
        path = speakers_dir / "profiles" / "bad-96.yml"
        before = path.read_bytes()
        stored = client.get("/api/v1/speakers/profiles/bad-96").json()
        resp = client.put("/api/v1/speakers/profiles/bad-96", json=stored)
        assert resp.status_code == 422
        # Slope is checked after type; the type error comes first.
        assert resp.json()["detail"] == TYPE_LR4_MESSAGE
        assert path.read_bytes() == before


class TestJsPythonParity:
    """The editor offers exactly what the generator supports."""

    @staticmethod
    def _js_array(name):
        src = SPEAKER_CONFIG_JS.read_text()
        m = re.search(rf"var {name} = (\[[^\]]*\]);", src)
        assert m, f"{name} not found in {SPEAKER_CONFIG_JS}"
        return json.loads(m.group(1))

    def test_slopes_equal_lr_slopes(self):
        js = self._js_array("VALID_SLOPES")
        assert [float(s) for s in js] == list(LR_SLOPES_DB_PER_OCT)

    def test_types_equal_crossover_types(self):
        assert self._js_array("VALID_XOVER_TYPES") == list(CROSSOVER_TYPES)


class TestShippedProfiles:
    """Every shipped profile passes the generator's crossover check.

    A failure is a finding for the Audio Engineer; never edit the profile
    to make this pass.
    """

    def test_profiles_found(self):
        assert len(SHIPPED_PROFILES) >= 10

    @pytest.mark.parametrize("path", SHIPPED_PROFILES, ids=lambda p: p.stem)
    def test_shipped_profile_passes(self, path):
        profile = yaml.safe_load(path.read_text())
        validate_profile_crossover(profile)


def _copy_profile_tree(tmp_path, profile_stem, **crossover_changes):
    """Copy a shipped profile (+ identities) into tmp with crossover changes."""
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    shutil.copytree(SHIPPED_IDENTITIES, tmp_path / "identities")
    profile = yaml.safe_load(
        (REPO_ROOT / "configs" / "speakers" / "profiles"
         / f"{profile_stem}.yml").read_text())
    profile = _with_crossover(profile, **crossover_changes)
    (profiles / f"{profile_stem}.yml").write_text(
        yaml.dump(profile, sort_keys=False))
    return profiles, tmp_path / "identities"


class TestGenerateReturns400:
    """Filters tab Generate: an unsupported stored crossover is a 400."""

    def test_slope_96_is_400_with_generator_message(self, tmp_path,
                                                    monkeypatch):
        import app.filter_routes as fr
        profiles, identities = _copy_profile_tree(
            tmp_path, "2way-80hz-sealed", slope_db_per_oct=96)
        monkeypatch.setattr(fr, "_profiles_dir", lambda: profiles)
        monkeypatch.setattr(fr, "_identities_dir", lambda: identities)
        resp = TestClient(app).post(
            "/api/v1/filters/generate",
            json={"profile": "2way-80hz-sealed"})
        assert resp.status_code == 400, resp.json()
        assert resp.json()["error"] == "invalid_crossover"
        assert resp.json()["detail"] == (
            f"Profile 2way-80hz-sealed: {SLOPE_96_MESSAGE}. "
            f"Fix it in the speaker editor.")


class TestSessionStartRefusesUnsupportedProfile:
    """G2: the session fails before any gain calibration or sweep."""

    def _run_session(self, tmp_path, monkeypatch, **crossover_changes):
        import app.measurement.session as sess
        profiles, identities = _copy_profile_tree(
            tmp_path, "2way-80hz-sealed", **crossover_changes)
        monkeypatch.setattr(sess, "_profile_dirs",
                            lambda: (str(profiles), str(identities)))
        session = MeasurementSession(
            config=SessionConfig(channels=[ChannelConfig(index=0, name="L")],
                                 profile_name="2way-80hz-sealed"),
            ws_broadcast=AsyncMock())
        stages = {name: AsyncMock() for name in (
            "_run_setup", "_run_gain_cal", "_run_measuring",
            "_run_filter_gen", "_run_deploy", "_run_verify")}
        with patch.multiple(MeasurementSession, **stages):
            _run(session.run())
        return session, stages

    def test_slope_96_fails_before_gain_cal(self, tmp_path, monkeypatch):
        session, stages = self._run_session(
            tmp_path, monkeypatch, slope_db_per_oct=96)
        assert session.state == MeasurementState.ERROR
        assert session.to_status_dict()["error_message"] == (
            f"Profile 2way-80hz-sealed: {SLOPE_96_MESSAGE}. "
            f"Fix it in the speaker editor.")
        for name, stage in stages.items():
            assert not stage.called, name

    def test_unknown_type_fails_before_gain_cal(self, tmp_path, monkeypatch):
        session, stages = self._run_session(tmp_path, monkeypatch, type="LR4")
        assert session.state == MeasurementState.ERROR
        assert TYPE_LR4_MESSAGE in session.to_status_dict()["error_message"]
        stages["_run_setup"].assert_not_called()
        stages["_run_gain_cal"].assert_not_called()

    def test_valid_profile_proceeds_to_gain_cal(self, tmp_path, monkeypatch):
        _, stages = self._run_session(tmp_path, monkeypatch)
        stages["_run_setup"].assert_called_once()
        stages["_run_gain_cal"].assert_called_once()
