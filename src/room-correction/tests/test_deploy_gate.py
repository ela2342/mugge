"""Deploy gate for venue sets (US-174d, Architect Q3).

check_deployable_set on the simulated home_lab set from the venue runner:
SIMULATED / delays.yml refusal and its override, the production-root
refusal that the override does not lift, top-level regular files only,
and the WAV header checks. The swap itself is in a later slice.
"""

import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mock import venue_sim
from room_correction import deploy
from room_correction import venue_pipeline as vp
from room_correction.deploy import check_deployable_set
from room_correction.export import DEFAULT_TAPS

REPO_ROOT = Path(__file__).resolve().parents[3]
VENUE = REPO_ROOT / "configs" / "venues" / "markaudio-ultimax-200hz.yml"
PROFILE = REPO_ROOT / "configs" / "speakers" / "profiles" / "2way-200hz-markaudio-ultimax.yml"
SR = 48000


@pytest.fixture(scope="module")
def bundle():
    return vp.load_venue_bundle(VENUE, PROFILE)


@pytest.fixture(scope="module")
def home_lab(bundle):
    sim = venue_sim.simulate_venue_measurements(
        bundle.profile, venue_sim.load_scenario("home_lab"), scenario_name="home_lab",
        noise_db=-60.0, noise_color="pink")
    return vp.generate_venue_filters(bundle, sim.measured_irs)


@pytest.fixture(scope="module")
def sets(tmp_path_factory, bundle, home_lab):
    """The same WAVs published once as simulated and once labelled real."""
    root = tmp_path_factory.mktemp("sets")
    for name, scenario in (("sim", "home_lab"), ("real", None)):
        with vp.staged_outputs(str(root / name), simulated_scenario=scenario) as stage:
            vp.write_venue_filters(home_lab, stage.path)
            vp.write_delays_yaml(home_lab, bundle, os.path.join(stage.path, vp.DELAYS_FILENAME),
                                 simulated_scenario=scenario)
            stage.commit()
    return root


@pytest.fixture
def names(bundle):
    return list(bundle.expected_files())


@pytest.fixture
def real_set(tmp_path, sets):
    d = tmp_path / "set"
    shutil.copytree(sets / "real", d)
    return d


@pytest.fixture
def sim_set(tmp_path, sets):
    d = tmp_path / "set"
    shutil.copytree(sets / "sim", d)
    return d


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "coeffs"
    r.mkdir()
    return r


@pytest.fixture
def prod_root(tmp_path, monkeypatch):
    r = tmp_path / "prod-coeffs"
    r.mkdir()
    monkeypatch.setattr(deploy, "PRODUCTION_COEFFS_DIR", str(r))
    return r


class TestSimulated:

    def test_real_labelled_set_is_deployable(self, real_set, names, root):
        assert check_deployable_set(str(real_set), names, str(root)) == []

    def test_simulated_set_refused(self, sim_set, names, root):
        issues = check_deployable_set(str(sim_set), names, str(root))
        assert any("SIMULATED marker" in i for i in issues)
        assert any("simulated: True" in i for i in issues)

    def test_override_lets_a_simulated_set_into_a_non_production_root(
            self, sim_set, names, root, prod_root):
        assert check_deployable_set(str(sim_set), names, str(root), allow_simulated=True) == []

    def test_override_never_reaches_the_production_root(self, sim_set, names, prod_root):
        issues = check_deployable_set(str(sim_set), names, str(prod_root), allow_simulated=True)
        assert any("production coeffs root" in i for i in issues)

    def test_production_root_compared_by_realpath(self, sim_set, names, prod_root, tmp_path):
        alias = tmp_path / "alias"
        alias.symlink_to(prod_root)
        issues = check_deployable_set(str(sim_set), names, str(alias) + "/.", allow_simulated=True)
        assert any("production coeffs root" in i for i in issues)

    def test_default_coeffs_dir_counts_as_production(self, sim_set, names, root, monkeypatch):
        monkeypatch.setattr(deploy, "DEFAULT_COEFFS_DIR", str(root))
        issues = check_deployable_set(str(sim_set), names, str(root), allow_simulated=True)
        assert any("production coeffs root" in i for i in issues)

    def test_marker_alone_refuses(self, real_set, names, root):
        (real_set / vp.SIMULATED_FILENAME).write_text("")
        issues = check_deployable_set(str(real_set), names, str(root))
        assert issues == [f"{vp.SIMULATED_FILENAME} marker present"]

    def test_dangling_marker_symlink_refuses(self, real_set, names, root):
        (real_set / vp.SIMULATED_FILENAME).symlink_to(real_set / "nowhere")
        assert check_deployable_set(str(real_set), names, str(root))

    @pytest.mark.parametrize("content", [
        "simulated: true\n", "simulated: 'false'\n", "simulated: 0\n", "simulated: null\n",
        "simulated:\n", "venue: x\n", "- simulated: false\n", "false\n", "", ": : [\n",
        b"\xff\xfe\x00simulated: false\n",
    ])
    def test_untrusted_delays_yml_refuses(self, real_set, names, root, content):
        p = real_set / vp.DELAYS_FILENAME
        p.write_bytes(content if isinstance(content, bytes) else content.encode())
        issues = check_deployable_set(str(real_set), names, str(root))
        assert issues and all(vp.DELAYS_FILENAME in i for i in issues)
        # ...and the override lifts exactly that, outside production.
        assert check_deployable_set(str(real_set), names, str(root), allow_simulated=True) == []

    @pytest.mark.parametrize("kind", ["missing", "dir", "symlink"])
    def test_delays_yml_not_a_regular_file_refuses(self, real_set, names, root, tmp_path, kind):
        p = real_set / vp.DELAYS_FILENAME
        target = tmp_path / "elsewhere.yml"
        shutil.move(p, target)
        if kind == "dir":
            p.mkdir()
        elif kind == "symlink":
            p.symlink_to(target)
        issues = check_deployable_set(str(real_set), names, str(root))
        assert issues == [f"{vp.DELAYS_FILENAME} missing or not a regular file"]


class TestFiles:

    def test_missing_expected_file(self, real_set, names, root):
        (real_set / "combined_sub1_lp.wav").unlink()
        assert check_deployable_set(str(real_set), names, str(root)) == [
            "combined_sub1_lp.wav: missing or not a regular file"]

    def test_symlinked_file_refused(self, real_set, names, root, tmp_path):
        p = real_set / "combined_left_hp.wav"
        shutil.move(p, tmp_path / "outside.wav")
        p.symlink_to(tmp_path / "outside.wav")
        assert check_deployable_set(str(real_set), names, str(root)) == [
            "combined_left_hp.wav: missing or not a regular file"]

    def test_directory_in_place_of_a_file_refused(self, real_set, names, root):
        p = real_set / "dirac.wav"
        p.unlink()
        p.mkdir()
        (p / "dirac.wav").write_bytes(b"")
        assert check_deployable_set(str(real_set), names, str(root)) == [
            "dirac.wav: missing or not a regular file"]

    @pytest.mark.parametrize("bad", [
        "../combined_left_hp.wav", "sub/combined_left_hp.wav", "/etc/passwd",
        "combined_x/../combined_left_hp.wav",
        "notes.txt", "delays.yml", "combined_left_hp.WAV", "", 3, None])
    def test_bad_expected_name(self, real_set, names, root, bad):
        issues = check_deployable_set(str(real_set), names + [bad], str(root))
        assert issues == [f"{bad!r}: not a deployable file name"]

    @pytest.mark.parametrize("expected", [[], None, {}, 3])
    def test_no_expected_names_refuses(self, real_set, root, expected):
        assert "no expected files" in check_deployable_set(str(real_set), expected, str(root))

    def test_extra_top_level_and_nested_files_are_ignored(self, real_set, names, root):
        (real_set / "notes.txt").write_text("operator notes")
        (real_set / "old").mkdir()
        (real_set / "old" / "combined_left_hp.wav").write_bytes(b"junk")
        assert check_deployable_set(str(real_set), names, str(root)) == []

    @pytest.mark.parametrize("kind", ["missing", "file", "symlink"])
    def test_set_dir_must_be_a_directory(self, real_set, names, root, tmp_path, kind):
        target = {"missing": tmp_path / "nope", "file": tmp_path / "f",
                  "symlink": tmp_path / "link"}[kind]
        if kind == "file":
            target.write_text("x")
        elif kind == "symlink":
            target.symlink_to(real_set)
        issues = check_deployable_set(str(target), names, str(root))
        assert len(issues) == 1 and "is not a plain directory" in issues[0]

    def test_check_does_not_touch_the_set(self, sim_set, names, root):
        def snapshot():
            return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in sim_set.rglob("*")}
        before = snapshot()
        check_deployable_set(str(sim_set), names, str(root))
        check_deployable_set(str(sim_set), names, str(root), allow_simulated=True)
        assert snapshot() == before


class TestHeader:

    def _replace(self, set_dir, name, data, sr=SR, subtype="FLOAT"):
        sf.write(str(set_dir / name), data, sr, subtype=subtype)

    def test_exact_tap_limit_passes(self, real_set, names, root):
        self._replace(real_set, "combined_left_hp.wav", np.zeros(DEFAULT_TAPS, np.float32))
        assert check_deployable_set(str(real_set), names, str(root)) == []

    @pytest.mark.parametrize("data,sr,subtype,fragment", [
        (np.zeros((DEFAULT_TAPS, 2), np.float32), SR, "FLOAT", "2 channels, expected mono"),
        (np.zeros(DEFAULT_TAPS, np.float32), 44100, "FLOAT", "44100 Hz"),
        (np.zeros(DEFAULT_TAPS, np.float32), SR, "PCM_16", "subtype PCM_16"),
        (np.zeros(DEFAULT_TAPS, np.float32), SR, "DOUBLE", "subtype DOUBLE"),
        (np.zeros(DEFAULT_TAPS + 1, np.float32), SR, "FLOAT", f"{DEFAULT_TAPS + 1} taps"),
        (np.zeros(0, np.float32), SR, "FLOAT", "0 taps"),
    ])
    def test_bad_header_refused(self, real_set, names, root, data, sr, subtype, fragment):
        self._replace(real_set, "combined_right_hp.wav", data, sr, subtype)
        issues = check_deployable_set(str(real_set), names, str(root))
        assert len(issues) == 1
        assert issues[0].startswith("combined_right_hp.wav: ") and fragment in issues[0]

    @pytest.mark.parametrize("content", [b"", b"RIFF\x00\x00\x00\x00WAVEfmt ", b"\x00" * 64])
    def test_unreadable_header_fails_closed(self, real_set, names, root, content):
        (real_set / "dirac.wav").write_bytes(content)
        issues = check_deployable_set(str(real_set), names, str(root))
        assert len(issues) == 1 and issues[0].startswith("dirac.wav: unreadable WAV header")

    def test_max_taps_is_a_parameter(self, real_set, names, root):
        issues = check_deployable_set(str(real_set), names, str(root), max_taps=DEFAULT_TAPS - 1)
        assert len(issues) == len(names)
