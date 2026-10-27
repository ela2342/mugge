"""Tests for the F-383 C4 subsonic corner derivation (Architect 41fd1486,
AE 92386ab9; rule R4 of 62cd5e5c, AE 9973bc8b).

derive_subsonic() is the one derivation for every combine caller (C4.2).
Rule R4: target = fc_hp/5, or max(fc_hp/5, s) if the crossover partner has
a subsonic at s; the corner moves to target iff target < m < fc_hp.  A
moved corner is gated on the product (NB-C4a, L2'); a failing gate raises
(NB-C4b).  No profile or identity data change: mandatory_hpf_hz stays the
protection spec (D3).
"""

import ast
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.signal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config_generator
import generate_bose_filters as gbf
import runner
from room_correction import crossover
from room_correction import generate_profile_filters as gpf
from room_correction.crossover import (
    SubsonicDerivationError,
    derive_subsonic,
    generate_crossover_filter,
    generate_subsonic_filter,
    subsonic_corner,
)

SR = 48000
N_TAPS = 16384
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
PROFILES_DIR = REPO_ROOT / "configs" / "speakers" / "profiles"
UNBUILDABLE = {"2way-80hz-ported", "workshop-xrk10f-fullrange"}
PROFILES = sorted(p.stem for p in PROFILES_DIR.glob("*.yml") if p.stem not in UNBUILDABLE)


def _dirac():
    h = np.zeros(N_TAPS)
    h[0] = 1.0
    return h


# -- rule R4 truth table (m1 of 41fd1486, rows of 62cd5e5c) -----------------

@pytest.mark.parametrize("m, fc_hp, s, corner, moved, reason", [
    (80.0, None, None, 80.0, False, "no HP edge"),
    (200.0, 200.0, None, 200.0, False, "m >= fc_hp"),          # m == fc: not moved
    (250.0, 200.0, 42.0, 250.0, False, "m >= fc_hp"),
    (40.0, 200.0, None, 40.0, False, "target >= m (fc_hp/5 >= m)"),  # target == m
    (25.0, 300.0, None, 25.0, False, "target >= m (fc_hp/5 >= m)"),
    (80.0, 200.0, None, 40.0, True, "moved to fc_hp/5"),       # s none
    (80.0, 200.0, 30.0, 40.0, True, "moved to fc_hp/5"),       # s < fc/5
    (80.0, 200.0, 42.0, 42.0, True, "moved to s"),             # fc/5 < s < m
    (25.0, 80.0, 28.0, 25.0, False, "target >= m (s >= m)"),   # s >= m
    (25.0, 80.0, 25.0, 25.0, False, "target >= m (s >= m)"),   # s == m: target == m
])
def test_r4_truth_table(m, fc_hp, s, corner, moved, reason):
    assert subsonic_corner(m, fc_hp, s) == (corner, moved, reason)


def test_partner_s_is_the_max_over_partners(monkeypatch):
    """s = max over every partner whose LP edge is fc_hp (Architect 3267ecf2 (1), AE a5885b6c).

    meh mid (fc_hp 300) has two partners, bass (s 25) and sub1 (s 20).
    """
    profile, identities, _, calls = _spied_factors(monkeypatch, "meh-3way-template")
    speakers = profile["speakers"]
    freqs = gpf._normalize_crossover_freqs(profile)
    fc_hp = gpf._channel_hp_edge(speakers["mid"], freqs)
    partners = {
        k: identities[c["identity"]].get("mandatory_hpf_hz")
        for k, c in speakers.items() if k != "mid" and gpf._channel_lp_edge(c, freqs) == fc_hp}
    assert partners == {"bass": 25, "sub1": 20}
    assert calls["mid"][2] == 25


def test_none_identity_corner_returns_none():
    assert derive_subsonic(None, 200.0, _dirac()) is None


def test_kept_corner_is_todays_subsonic():
    d = derive_subsonic(42.0, None, None, slope_db_per_oct=48.0, n_taps=N_TAPS, sr=SR)
    assert (d.corner_hz, d.moved, d.reason) == (42.0, False, "no HP edge")
    assert d.c4a_margin_db is None and d.l2_half_db is None
    np.testing.assert_array_equal(d.fir, generate_subsonic_filter(42.0, 48.0, N_TAPS, SR))


def test_moved_corner_is_the_subsonic_at_target():
    xo = generate_crossover_filter("highpass", 200.0, 24, N_TAPS, SR, alignment="linkwitz-riley")
    d = derive_subsonic(80.0, 200.0, xo, n_taps=N_TAPS, sr=SR, channel="sat")
    assert (d.corner_hz, d.moved) == (40.0, True)
    np.testing.assert_array_equal(d.fir, generate_subsonic_filter(40.0, 24.0, N_TAPS, SR))
    assert d.c4a_margin_db >= 0.0
    assert d.l2_half_db >= crossover.L2_MIN_HALF_DB
    assert d.l2_quarter_db >= d.l2_half_db


def test_make_subsonic_is_used_for_every_fir():
    calls = []

    def make(hpf_freq, slope):
        calls.append((hpf_freq, slope))
        return generate_subsonic_filter(hpf_freq, slope, N_TAPS, SR)

    xo = generate_crossover_filter("highpass", 200.0, 24, N_TAPS, SR, alignment="linkwitz-riley")
    derive_subsonic(80.0, 200.0, xo, n_taps=N_TAPS, sr=SR, make_subsonic=make)
    assert sorted(calls) == [(40.0, 24.0), (80.0, 24.0)]


# -- the raises (NB-C4b, m4 message) -----------------------------------------

def test_no_crossover_hp_raises_nb_c4a():
    """hp_filter = dirac: the product is the subsonic at 40 Hz alone."""
    with pytest.raises(SubsonicDerivationError) as exc:
        derive_subsonic(80.0, 200.0, _dirac(), n_taps=N_TAPS, sr=SR, channel="sat_left")
    msg = str(exc.value)
    for part in ("sat_left", "m 80.0 Hz", "40.0 Hz", "NB-C4a", "margin -", "STOP"):
        assert part in msg, msg
    assert isinstance(exc.value, ValueError)


def test_shallow_skirt_raises_l2_half():
    """A flat HP 30 dB down: below the reference everywhere, no skirt at m/2."""
    with pytest.raises(SubsonicDerivationError) as exc:
        derive_subsonic(80.0, 200.0, 0.03 * _dirac(), n_taps=N_TAPS, sr=SR, channel="sat_left")
    msg = str(exc.value)
    for part in ("sat_left", "m 80.0 Hz", "40.0 Hz", "L2'", "at 40.0 Hz", "att(m/2)"):
        assert part in msg, msg


def test_rising_skirt_raises_l2_monotonic():
    """A notch at m/2 on the LR4 HP: att(m/2) ~130 dB, so att(m/4) < att(m/2).

    The product stays below the subsonic at m everywhere, so NB-C4a passes
    and only the L2' monotonic check can fire.  (A bump at m/4 cannot reach
    this branch: NB-C4a catches it first.)
    """
    b, a = scipy.signal.iirnotch(40.0, 5.0, fs=SR)
    xo = generate_crossover_filter("highpass", 200.0, 24, N_TAPS, SR, alignment="linkwitz-riley")
    with pytest.raises(SubsonicDerivationError) as exc:
        derive_subsonic(80.0, 200.0, scipy.signal.lfilter(b, a, xo), n_taps=N_TAPS, sr=SR,
                        channel="sat_left")
    msg = str(exc.value)
    for part in ("sat_left", "L2'", "at 20.0 Hz", "att(m/4)"):
        assert part in msg, msg


def test_moved_corner_needs_the_hp_filter():
    with pytest.raises(ValueError):
        derive_subsonic(80.0, 200.0, None, n_taps=N_TAPS, sr=SR)


# -- every profile: the moved set (R4 re-sweep, 62cd5e5c step a) -------------

# profile -> channel -> (corner, s, NB-C4a min margin in dB from the sweep)
MOVED = {
    "2way-200hz-markaudio-ultimax": {"sat_left": (40.0, None, 31.96), "sat_right": (40.0, None, 31.96)},
    "2way-80hz-sealed": {"sat_left": (20, 20, 80.20), "sat_right": (20, 20, 80.20)},
    "bose-home-chn50p": {"sat_left": (42, 42, 63.53), "sat_right": (42, 42, 63.53)},
    "pa-2way-80hz-lavoce": {"sat_left": (20, 20, 23.52), "sat_right": (20, 20, 23.52)},
    "workshop-c3d-elf-3way": {"hf_left": (200.0, 100, 15.73), "hf_right": (200.0, 100, 15.73)},
}
# Eligible (HP edge and a subsonic) but not moved: profile -> channel -> (s, reason).
KEPT = {
    "pa-2way-80hz-s218": {"sat_left": (28, "target >= m (s >= m)"), "sat_right": (28, "target >= m (s >= m)")},
    "pa-2way-horn-sub": {"sat_left": (40, "target >= m (s >= m)"), "sat_right": (40, "target >= m (s >= m)")},
    "pa-2way-onken": {"sat_left": (35, "target >= m (s >= m)"), "sat_right": (35, "target >= m (s >= m)")},
    "bose-home": {"sat_left": (42, "m >= fc_hp"), "sat_right": (42, "m >= fc_hp")},
    "workshop-c3d-elf-3way": {"mid_left": (28, "m >= fc_hp"), "mid_right": (28, "m >= fc_hp")},
    # Two partners (bass s 25, sub1 s 20): s is their max (3267ecf2 (1)).
    "meh-3way-template": {"mid": (25, "target >= m (s >= m)"), "hf": (25, "target >= m (s >= m)")},
}
MARGIN_PIN_TOL_DB = 0.5


def _spied_factors(monkeypatch, name):
    calls = {}
    real = gpf.derive_subsonic

    def spy(m, fc_hp, hp_filter, **kw):
        result = real(m, fc_hp, hp_filter, **kw)
        calls[kw["channel"]] = (m, fc_hp, kw["partner_subsonic_hz"], kw["slope_db_per_oct"], result)
        return result

    monkeypatch.setattr(gpf, "derive_subsonic", spy)
    profile, identities = config_generator.load_profile_with_identities(name)
    factors = gpf.channel_factors(profile, identities, n_taps=N_TAPS, sr=SR)
    return profile, identities, factors, calls


@pytest.mark.parametrize("name", PROFILES)
def test_profile_moved_set(monkeypatch, name):
    profile, identities, factors, calls = _spied_factors(monkeypatch, name)
    moved, kept = MOVED.get(name, {}), KEPT.get(name, {})
    for key, spk in profile["speakers"].items():
        m = identities[spk["identity"]].get("mandatory_hpf_hz")
        if m is None:
            assert key not in calls or calls[key][4] is None
            assert factors[key].subsonic is None
            continue
        _, fc_hp, s, slope, d = calls[key]
        assert slope == max((profile.get("crossover") or {}).get(
            "slope_db_per_oct", gpf.DEFAULT_SLOPE_DB_PER_OCT), 24.0)
        assert factors[key].subsonic is d.fir
        if key in moved:
            corner, s_exp, margin = moved[key]
            print(f"{name} {key}: {m} -> {d.corner_hz} Hz (s {s}), NB-C4a margin "
                  f"{d.c4a_margin_db:+.2f} dB at {d.c4a_margin_hz:.1f} Hz, L2' "
                  f"{d.l2_half_db:.1f} / {d.l2_quarter_db:.1f} dB")
            assert (d.corner_hz, d.moved, s) == (corner, True, s_exp)
            assert d.c4a_margin_db >= margin - MARGIN_PIN_TOL_DB
        else:
            assert (d.corner_hz, d.moved) == (m, False), (key, d.reason)
            if key in kept:
                assert (s, d.reason) == kept[key]
            else:
                assert fc_hp is None and d.reason == "no HP edge", (key, d.reason)


def test_markaudio_sub_has_no_subsonic():
    """Q-C4d d1 (corner 40.0 exactly) holds only if the sub carries none (62cd5e5c)."""
    profile, identities = config_generator.load_profile_with_identities(
        "2way-200hz-markaudio-ultimax")
    sub = profile["speakers"]["sub1"]
    assert identities[sub["identity"]].get("mandatory_hpf_hz") is None


def test_cascade_channels_never_move(monkeypatch):
    """On today's data no cascade moves, so a3's tail rows are unchanged (5f6b5436)."""
    for name in PROFILES:
        _, _, factors, calls = _spied_factors(monkeypatch, name)
        for key, f in factors.items():
            if gpf.is_cascade(f.filter_type, f.subsonic):
                assert not calls[key][4].moved, (name, key)


# -- the other callers --------------------------------------------------------

def test_runner_goes_through_derive_subsonic(monkeypatch):
    calls = []
    real = crossover.derive_subsonic

    def spy(m, fc_hp, hp_filter, **kw):
        calls.append((kw["channel"], m, fc_hp, kw.get("partner_subsonic_hz")))
        return real(m, fc_hp, hp_filter, **kw)

    monkeypatch.setattr(crossover, "derive_subsonic", spy)
    channels = {
        "main_left": {"type": "highpass", "speaker_identity": {"mandatory_hpf_hz": 80.0}},
        "main_right": {"type": "highpass"},
        "sub1": {"type": "lowpass", "speaker_identity": {"mandatory_hpf_hz": 42.0}},
        "sub2": {"type": "lowpass", "speaker_identity": {"mandatory_hpf_hz": None}},
    }
    xos = {k: generate_crossover_filter(c["type"], 200.0, 48.0, N_TAPS, SR) for k, c in channels.items()}
    result = runner.derive_subsonic_filters(channels, xos, 200.0, N_TAPS, SR)
    assert calls == [
        ("main_left", 80.0, 200.0, 42.0), ("main_right", None, 200.0, 42.0),
        ("sub1", 42.0, None, None), ("sub2", None, None, None),
    ]
    assert sorted(result) == ["main_left", "sub1"]
    assert (result["main_left"].corner_hz, result["main_left"].moved) == (42.0, True)
    np.testing.assert_array_equal(  # m5: the runner's slope stays 24
        result["main_left"].fir, generate_subsonic_filter(42.0, 24.0, N_TAPS, SR))
    np.testing.assert_array_equal(
        result["sub1"].fir, generate_subsonic_filter(42.0, 24.0, N_TAPS, SR))


def test_bose_sub_goes_through_derive_subsonic(monkeypatch, tmp_path):
    calls = []
    real = gbf.derive_subsonic

    def spy(m, fc_hp, hp_filter, **kw):
        result = real(m, fc_hp, hp_filter, **kw)
        calls.append((m, fc_hp, kw["slope_db_per_oct"], result))
        return result

    monkeypatch.setattr(gbf, "derive_subsonic", spy)
    profile_path = PROFILES_DIR / "bose-home.yml"
    gbf.generate_bose_filters(output_dir=str(tmp_path), profile_path=str(profile_path))
    assert len(calls) == 1
    m, fc_hp, slope, d = calls[0]
    assert (m, fc_hp, d.moved, d.corner_hz) == (gbf.SUBSONIC_HPF_HZ, None, False, gbf.SUBSONIC_HPF_HZ)
    np.testing.assert_array_equal(d.fir, generate_subsonic_filter(m, slope, N_TAPS, SR))


def test_only_the_derivation_builds_subsonics():
    """No combine caller generates a subsonic outside derive_subsonic (C4.2)."""
    allowed = {
        ("room-correction/room_correction/crossover.py", "make_subsonic"),
        ("room-correction/room_correction/generate_profile_filters.py", "make_subsonic"),
    }
    found = set()
    for path in sorted(SRC_DIR.rglob("*.py")):
        rel = path.relative_to(SRC_DIR).as_posix()
        if "/tests/" in f"/{rel}":
            continue

        def visit(node, func):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = node.name
            if isinstance(node, ast.Call):
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
                if name == "generate_subsonic_filter":
                    found.add((rel, func))
            for child in ast.iter_child_nodes(node):
                visit(child, func)

        visit(ast.parse(path.read_text(), filename=rel), None)
    assert found == allowed
