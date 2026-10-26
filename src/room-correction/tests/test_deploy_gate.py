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


# -- set swap (Architect Q1/Q2) ----------------------------------------------

from datetime import datetime, timezone

from room_correction.closed_loop import MEASUREMENT_SNR_MIN_DB, Verdict
from room_correction.deploy import (
    CURRENT_LINK, KEEP_EXTRA_SETS, PREVIOUS_LINK, SETS_DIRNAME,
    DeployRefused, RollbackFailed, deploy_venue_set, prune_sets, trial_deploy,
)

T0 = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


class FakeReload:
    """Records what ``current`` points at on each Reload; scripted results."""

    def __init__(self, root, results=()):
        self.root, self.results, self.seen = root, list(results), []

    def __call__(self):
        self.seen.append(os.readlink(self.root / CURRENT_LINK))
        return self.results.pop(0) if self.results else True


@pytest.fixture
def live(tmp_path, names):
    """A coeffs root as tmpfiles seeds it: sets/dirac and current -> sets/dirac."""
    r = tmp_path / "live"
    seed = r / SETS_DIRNAME / "dirac"
    seed.mkdir(parents=True)
    for n in names:
        sf.write(str(seed / n), np.r_[1.0, np.zeros(DEFAULT_TAPS - 1)].astype(np.float32),
                 SR, subtype="FLOAT")
    (r / CURRENT_LINK).symlink_to(os.path.join(SETS_DIRNAME, "dirac"))
    return r


def _links(root):
    return {k: (os.readlink(root / k) if (root / k).is_symlink() else None)
            for k in (CURRENT_LINK, PREVIOUS_LINK)}


def _litter(root):
    sets = root / SETS_DIRNAME
    return sorted(p.name for p in list(sets.iterdir()) + list(root.iterdir())
                  if p.name.startswith("."))


class TestTrialDeploy:

    def test_commit_swaps_in_the_set(self, real_set, names, live):
        reload = FakeReload(live)
        with trial_deploy(str(real_set), names, str(live), reload=reload, now=T0) as t:
            assert _links(live)[CURRENT_LINK] == f"sets/{t.set_id}"
            t.commit()
        links = _links(live)
        assert links == {CURRENT_LINK: f"sets/{t.set_id}", PREVIOUS_LINK: "sets/dirac"}
        assert t.set_id.startswith("20261026T120000Z-")
        assert reload.seen == [f"sets/{t.set_id}"]
        for n in names:
            assert (live / CURRENT_LINK / n).read_bytes() == (real_set / n).read_bytes()
        assert sorted(p.name for p in (live / CURRENT_LINK).iterdir()) == sorted(names)
        assert _litter(live) == []

    @pytest.mark.parametrize("exc", [None, ValueError, KeyboardInterrupt])
    def test_no_commit_rolls_back(self, real_set, names, live, exc):
        reload = FakeReload(live)
        try:
            with trial_deploy(str(real_set), names, str(live), reload=reload, now=T0) as t:
                if exc:
                    raise exc("measurement crashed")
        except BaseException as e:
            assert exc is not None and isinstance(e, exc)
        else:
            assert exc is None
        assert _links(live) == {CURRENT_LINK: "sets/dirac", PREVIOUS_LINK: None}
        assert reload.seen == [f"sets/{t.set_id}", "sets/dirac"]
        # The tried set is not pruned during a trial; it stays immutable.
        assert (live / SETS_DIRNAME / t.set_id).is_dir()

    def test_rollback_restores_the_old_previous(self, real_set, names, live):
        older = live / SETS_DIRNAME / "20261025T000000Z-000000000000"
        older.mkdir()
        (live / PREVIOUS_LINK).symlink_to(f"sets/{older.name}")
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live), now=T0):
            assert _links(live)[PREVIOUS_LINK] == "sets/dirac"
        assert _links(live) == {CURRENT_LINK: "sets/dirac",
                                PREVIOUS_LINK: f"sets/{older.name}"}

    def test_failed_reload_on_swap_rolls_back(self, real_set, names, live):
        reload = FakeReload(live, [False, True])
        with pytest.raises(RuntimeError, match="reload failed after swapping in"):
            with trial_deploy(str(real_set), names, str(live), reload=reload, now=T0):
                pytest.fail("body must not run after a failed reload")
        assert _links(live)[CURRENT_LINK] == "sets/dirac"
        assert len(reload.seen) == 2 and reload.seen[1] == "sets/dirac"

    @pytest.mark.parametrize("second", [False, OSError("pw-cli gone")])
    def test_failed_rollback_is_loud_and_raised(self, real_set, names, live, capsys, second):
        def reload():
            if not hasattr(reload, "n"):
                reload.n = 1
                return True
            if isinstance(second, Exception):
                raise second
            return second
        with pytest.raises(RollbackFailed):
            with trial_deploy(str(real_set), names, str(live), reload=reload, now=T0):
                pass
        assert "ROLLBACK FAILED" in capsys.readouterr().err

    def test_double_commit_raises_and_stays_committed(self, real_set, names, live):
        with pytest.raises(RuntimeError, match="already committed"):
            with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live),
                              now=T0) as t:
                t.commit()
                t.commit()
        assert _links(live)[CURRENT_LINK] == f"sets/{t.set_id}"

    def test_refused_set_touches_nothing(self, sim_set, names, live):
        before = sorted(p.name for p in (live / SETS_DIRNAME).iterdir())
        reload = FakeReload(live)
        with pytest.raises(DeployRefused, match="SIMULATED"):
            with trial_deploy(str(sim_set), names, str(live), reload=reload):
                pytest.fail("refused set entered")
        assert reload.seen == []
        assert _links(live) == {CURRENT_LINK: "sets/dirac", PREVIOUS_LINK: None}
        assert sorted(p.name for p in (live / SETS_DIRNAME).iterdir()) == before

    def test_simulated_override_never_into_production(self, sim_set, names, live, monkeypatch):
        monkeypatch.setattr(deploy, "PRODUCTION_COEFFS_DIR", str(live))
        with pytest.raises(DeployRefused, match="production coeffs root"):
            with trial_deploy(str(sim_set), names, str(live), reload=FakeReload(live),
                              allow_simulated=True):
                pytest.fail("refused set entered")

    def test_no_current_link_refuses(self, real_set, names, live):
        (live / CURRENT_LINK).unlink()
        with pytest.raises(DeployRefused, match="no current set"):
            with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live)):
                pytest.fail("entered without a rollback target")

    def test_staged_bytes_are_checked_again(self, real_set, names, live, monkeypatch):
        # A file swapped after the check (TOCTOU) is caught on the staged copy.
        monkeypatch.setattr(deploy, "check_deployable_set", lambda *a, **k: [])
        sf.write(str(real_set / "combined_left_hp.wav"),
                 np.zeros((8, 2), np.float32), SR, subtype="FLOAT")
        with pytest.raises(DeployRefused, match="combined_left_hp.wav: 2 channels"):
            with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live)):
                pytest.fail("bad staged set entered")
        assert sorted(p.name for p in (live / SETS_DIRNAME).iterdir()) == ["dirac"]
        assert _links(live)[CURRENT_LINK] == "sets/dirac"

    def test_set_id_never_reused(self, real_set, names, live):
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live), now=T0) as t:
            t.commit()
        with pytest.raises(DeployRefused, match="already exists"):
            with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live), now=T0):
                pytest.fail("reused id")
        assert _links(live)[CURRENT_LINK] == f"sets/{t.set_id}"
        assert _litter(live) == []

    def test_set_id_hashes_content(self, real_set, names, live):
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live), now=T0) as a:
            a.commit()
        sf.write(str(real_set / "dirac.wav"),
                 np.r_[0.5, np.zeros(DEFAULT_TAPS - 1)].astype(np.float32), SR, subtype="FLOAT")
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live), now=T0) as b:
            b.commit()
        assert a.set_id[:17] == b.set_id[:17] and a.set_id != b.set_id

    def test_crash_between_links_restores_both(self, real_set, names, live, monkeypatch):
        real_point = deploy._point

        def point(root, link, target):
            if link == CURRENT_LINK and target != "sets/dirac":
                raise OSError("power cut")
            return real_point(root, link, target)
        monkeypatch.setattr(deploy, "_point", point)
        reload = FakeReload(live)
        with pytest.raises(OSError, match="power cut"):
            with trial_deploy(str(real_set), names, str(live), reload=reload, now=T0):
                pytest.fail("entered")
        assert _links(live) == {CURRENT_LINK: "sets/dirac", PREVIOUS_LINK: None}


def _measure(verdict):
    good = MEASUREMENT_SNR_MIN_DB + 20
    curve = {Verdict.PASS: np.zeros(8), Verdict.FAIL: np.full(8, 9.0),
             Verdict.INVALID: np.zeros(8)}[verdict]
    snr = good if verdict is not Verdict.INVALID else MEASUREMENT_SNR_MIN_DB - 1
    band = (curve, np.zeros(8), snr)
    return lambda: ({"sat_left": band}, band)


class TestDeployVenueSet:

    def test_pass_commits(self, real_set, names, live):
        r = deploy_venue_set(str(real_set), names, str(live), measure=_measure(Verdict.PASS),
                             reload=FakeReload(live), now=T0)
        assert r.verdict is Verdict.PASS
        links = _links(live)
        assert links[PREVIOUS_LINK] == "sets/dirac"
        assert links[CURRENT_LINK].startswith("sets/20261026T120000Z-")

    @pytest.mark.parametrize("verdict", [Verdict.FAIL, Verdict.INVALID])
    def test_fail_and_invalid_keep_the_previous_filters(self, real_set, names, live, verdict):
        reload = FakeReload(live)
        r = deploy_venue_set(str(real_set), names, str(live), measure=_measure(verdict),
                             reload=reload, now=T0)
        assert r.verdict is verdict
        assert _links(live) == {CURRENT_LINK: "sets/dirac", PREVIOUS_LINK: None}
        assert reload.seen[-1] == "sets/dirac"

    @pytest.mark.parametrize("measure", [
        lambda: (_ for _ in ()).throw(RuntimeError("mic unplugged")),
        lambda: None,
        lambda: ({"sat_left": None}, None),
    ])
    def test_broken_measurement_keeps_the_previous_filters(self, real_set, names, live, measure):
        try:
            r = deploy_venue_set(str(real_set), names, str(live), measure=measure,
                                 reload=FakeReload(live), now=T0)
        except Exception:
            pass
        else:
            assert r.verdict is Verdict.FAIL
        assert _links(live)[CURRENT_LINK] == "sets/dirac"


    def test_simulated_set_refused_before_measuring(self, sim_set, names, live):
        def measure():
            pytest.fail("measured a refused set")
        with pytest.raises(DeployRefused, match="SIMULATED"):
            deploy_venue_set(str(sim_set), names, str(live), measure=measure,
                             reload=FakeReload(live))
        assert _links(live)[CURRENT_LINK] == "sets/dirac"

class TestPrune:

    def _commit(self, real_set, names, live, i):
        sf.write(str(real_set / "dirac.wav"),
                 np.r_[1.0 - i / 100, np.zeros(DEFAULT_TAPS - 1)].astype(np.float32),
                 SR, subtype="FLOAT")
        now = T0.replace(minute=i)
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live),
                          now=now) as t:
            t.commit()
        return t.set_id

    def test_keeps_current_previous_and_n_newest(self, real_set, names, live):
        ids = [self._commit(real_set, names, live, i) for i in range(KEEP_EXTRA_SETS + 4)]
        kept = sorted(p.name for p in (live / SETS_DIRNAME).iterdir())
        assert kept == sorted(["dirac"] + ids[-(KEEP_EXTRA_SETS + 2):])
        assert _links(live) == {CURRENT_LINK: f"sets/{ids[-1]}",
                                PREVIOUS_LINK: f"sets/{ids[-2]}"}

    def test_never_removes_a_linked_set_even_if_old(self, real_set, names, live):
        ids = [self._commit(real_set, names, live, i) for i in range(KEEP_EXTRA_SETS + 3)]
        # previous re-pointed at a set that is already pruned-eligible by age.
        (live / PREVIOUS_LINK).unlink()
        (live / PREVIOUS_LINK).symlink_to(f"sets/{ids[1]}")
        removed = prune_sets(str(live), keep=0)
        assert sorted(os.path.basename(p) for p in removed) == ids[2:-1]
        assert sorted(p.name for p in (live / SETS_DIRNAME).iterdir()) == sorted(
            ["dirac", ids[1], ids[-1]])

    def test_removes_leftover_staging_but_not_foreign_dirs(self, real_set, names, live):
        (live / SETS_DIRNAME / ".staging-deadbeef0000").mkdir()
        (live / SETS_DIRNAME / "operator-backup").mkdir()
        self._commit(real_set, names, live, 0)
        names_left = sorted(p.name for p in (live / SETS_DIRNAME).iterdir())
        assert ".staging-deadbeef0000" not in names_left
        assert "operator-backup" in names_left and "dirac" in names_left

    def test_rollback_does_not_prune(self, real_set, names, live):
        ids = [self._commit(real_set, names, live, i) for i in range(KEEP_EXTRA_SETS + 2)]
        before = sorted(p.name for p in (live / SETS_DIRNAME).iterdir())
        sf.write(str(real_set / "dirac.wav"),
                 np.r_[0.25, np.zeros(DEFAULT_TAPS - 1)].astype(np.float32), SR, subtype="FLOAT")
        with trial_deploy(str(real_set), names, str(live), reload=FakeReload(live),
                          now=T0.replace(hour=13)) as t:
            pass
        after = sorted(p.name for p in (live / SETS_DIRNAME).iterdir())
        assert after == sorted(before + [t.set_id])
        assert _links(live)[CURRENT_LINK] == f"sets/{ids[-1]}"

