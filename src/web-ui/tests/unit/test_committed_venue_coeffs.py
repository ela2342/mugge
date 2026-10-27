"""Committed venue FIR coefficients (US-173 M2, D-009, D-031).

configs/coeffs/markaudio-ultimax-200hz/ is a venue SOURCE set: the
crossover-only WAVs are generated once on the Mac and committed; the Pi
gets these exact bytes (no regeneration: the libsndfile PEAK chunk
differs per run, so hashes cover the committed bytes). Convolver ch 4
(sub 2) gets combined_sub2_lp.wav, a byte copy of the canonical
configs/coeffs/zero.wav (test_venue_spare_channel_mute.py).

The committed files pass the same file gate as a generated set: every
venue that uses this set goes through run_venue_checks (AE + Architect,
2026-10-26), speaker FIRs as 'fir' and dirac.wav as 'dirac'. zero.wav has
no kind there; test_venue_spare_channel_mute.py checks it.

D-031 thresholds are the AE's ruling for M2. check_d031_floor and
check_no_boost are local until the shared US-174d versions exist; keep
them in step with those (TODO 174d: import the shared functions).
"""

import hashlib
import importlib.util
import pathlib
import struct

import numpy as np
import pytest
import soundfile as sf
import yaml

from room_correction.verify import run_venue_checks

REPO = pathlib.Path(__file__).resolve().parents[4]
COEFF_DIR = REPO / "configs/coeffs/markaudio-ultimax-200hz"
COEFFS = REPO / "configs/coeffs"
ZERO = COEFFS / "zero.wav"
VENUES = REPO / "configs/venues"
# Venues whose speaker channels load this set.
SET_VENUES = ("markaudio-ultimax-200hz", "home-lab-chn50p-ultimax")
DIRAC = "dirac.wav"
PROFILE = REPO / "configs/speakers/profiles/2way-200hz-markaudio-ultimax.yml"
IDENTITIES = REPO / "configs/speakers/identities"
GENERATOR = REPO / "scripts/generate-crossover-coeffs.py"

TAPS = 16384
RATE = 48000
N_FFT = 65536  # AE: at least 65536 points
PASSBAND_TOP_HZ = 16000.0
FLOOR_LOW_HZ = 10.0
# M2-only regression (crossover-only): mains at f_h. Analytic LR4 HP at
# 200 Hz gives -32.0 dB at 80 Hz.
M2_MAINS_AT_HPF_MAX_DB = -30.0
# Tolerance above max_boost_db for the no-boost check.
NO_BOOST_TOLERANCE_DB = 0.5

# zero.wav is canonical and never regenerated: RIFF, 16-byte fmt chunk
# (IEEE float, mono, 48 kHz, 32 bit), data chunk of 16384 x 0.0f. Same
# layout as dirac.wav. The set's combined_sub2_lp.wav is a copy of it.
ZERO_SHA256 = (
    "97b9d9db69ae3abc524a3f87206b9a4c8d40a239ff30a98e4ebdcaf462e40c56")
SUB2 = "combined_sub2_lp.wav"


def deploy_filenames():
    spec = importlib.util.spec_from_file_location("gen_coeffs", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DEPLOY_FILENAMES


def load_profile():
    with open(PROFILE) as f:
        return yaml.safe_load(f)


def load_identity(name):
    text = (IDENTITIES / (name + ".yml")).read_text()
    return yaml.safe_load(text), text


def channels():
    """file name -> (speaker profile entry, identity, identity text)."""
    names = deploy_filenames()
    result = {}
    for key, speaker in load_profile()["speakers"].items():
        identity, text = load_identity(speaker["identity"])
        result[names[key]] = (speaker, identity, text)
    return result


CHANNELS = channels()
CROSSOVER_HZ = float(load_profile()["crossover"]["frequency_hz"])


def magnitude_db(path):
    fir, rate = sf.read(str(path), dtype="float64")
    assert rate == RATE, path
    spectrum = np.abs(np.fft.rfft(fir, n=N_FFT))
    freqs = np.fft.rfftfreq(N_FFT, 1.0 / RATE)
    with np.errstate(divide="ignore"):
        return freqs, 20 * np.log10(spectrum)


def passband_ref_db(freqs, mag_db, crossover_hz, filter_type):
    """AE: for a highpass, ref = max |H| over [f_xo, 16 kHz]."""
    assert filter_type == "highpass", filter_type  # only ruled case
    band = (freqs >= crossover_hz) & (freqs <= PASSBAND_TOP_HZ)
    return float(mag_db[band].max())


def check_d031_floor(freqs, rel_db, mandatory_hpf_hz):
    """D-031 floor, relative to the passband reference. Violations."""
    violations = []
    for top_hz, limit_db in ((mandatory_hpf_hz, -6.0),
                             (mandatory_hpf_hz / 2.0, -18.0)):
        band = (freqs >= FLOOR_LOW_HZ) & (freqs <= top_hz)
        worst = float(rel_db[band].max())
        if worst > limit_db:
            violations.append((FLOOR_LOW_HZ, top_hz, worst, limit_db))
    return violations


def check_no_boost(freqs, mag_db, crossover_hz, max_boost_db):
    """Null-HPF channels: absolute |H| <= max_boost_db + 0.5 dB on
    [10 Hz, f_xo]. Violation or None."""
    limit_db = max_boost_db + NO_BOOST_TOLERANCE_DB
    band = (freqs >= FLOOR_LOW_HZ) & (freqs <= crossover_hz)
    worst = float(mag_db[band].max())
    return (worst, limit_db) if worst > limit_db else None


def is_d031_exception(identity, text):
    """Keyed on the identity: null HPF, sealed, exception documented."""
    return (identity.get("mandatory_hpf_hz") is None
            and identity.get("type") == "sealed"
            and "D-031 EXCEPTION" in text)


def venue_coefficients(venue):
    with open(VENUES / (venue + ".yml")) as f:
        channels = yaml.safe_load(f)["channels"]
    return {c["coefficients"] for c in channels.values()}


def assert_venue_gate(output_dir, expected_files, mandatory_hpf_hz=None):
    passed, results = run_venue_checks(
        str(output_dir), expected_files, mandatory_hpf_hz=mandatory_hpf_hz)
    assert passed, [r for r in results if not r.passed] or results


def read_sums():
    sums = {}
    for line in (COEFF_DIR / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        sums[name.lstrip("*")] = digest
    return sums


def test_sha256sums_cover_exactly_the_committed_wavs():
    sums = read_sums()
    wavs = {p.name for p in COEFF_DIR.glob("*.wav")}
    assert set(sums) == wavs == set(CHANNELS) | {SUB2}
    assert sums[SUB2] == ZERO_SHA256
    for name, digest in sums.items():
        got = hashlib.sha256((COEFF_DIR / name).read_bytes()).hexdigest()
        assert got == digest, name


def test_zero_wav_is_canonical():
    data = ZERO.read_bytes()
    assert hashlib.sha256(data).hexdigest() == ZERO_SHA256
    assert len(data) == 44 + 4 * TAPS
    assert data[:4] == b"RIFF" and data[8:16] == b"WAVEfmt "
    assert struct.unpack_from("<I", data, 4)[0] == len(data) - 8
    assert struct.unpack_from("<IHHIIHH", data, 16) == (
        16, 3, 1, RATE, RATE * 4, 4, 32)
    assert data[36:40] == b"data"
    assert struct.unpack_from("<I", data, 40)[0] == 4 * TAPS
    assert data[44:] == bytes(4 * TAPS)


@pytest.mark.parametrize("venue", SET_VENUES)
def test_venue_files_pass_the_venue_gate(venue):
    """Format, float32, D-009 at -0.5 dB, minimum-phase residual and the
    D-031 mandatory HPF (from the speaker identity) for the FIRs; format,
    float32 and an exact unit impulse for dirac.wav. No overrides."""
    names = venue_coefficients(venue)
    firs = names & set(CHANNELS)
    assert firs == set(CHANNELS), venue
    assert names - firs <= {DIRAC, ZERO.name}, venue
    hpf = {name: float(CHANNELS[name][1]["mandatory_hpf_hz"])
           for name in firs
           if CHANNELS[name][1].get("mandatory_hpf_hz") is not None}
    assert_venue_gate(COEFF_DIR, dict.fromkeys(firs, "fir"), hpf)
    if DIRAC in names:
        assert_venue_gate(COEFFS, {DIRAC: "dirac"})


@pytest.mark.parametrize("name", sorted(CHANNELS))
def test_d031(name):
    speaker, identity, text = CHANNELS[name]
    freqs, mag_db = magnitude_db(COEFF_DIR / name)
    hpf = identity.get("mandatory_hpf_hz")
    if hpf is None:
        assert is_d031_exception(identity, text), speaker["identity"]
        violation = check_no_boost(
            freqs, mag_db, CROSSOVER_HZ, identity["max_boost_db"])
        assert violation is None, (name, violation)
        return
    ref = passband_ref_db(
        freqs, mag_db, CROSSOVER_HZ, speaker["filter_type"])
    rel_db = mag_db - ref
    assert check_d031_floor(freqs, rel_db, float(hpf)) == [], name


@pytest.mark.parametrize("name", sorted(
    n for n, (s, _, _) in CHANNELS.items() if s["role"] == "satellite"))
def test_m2_mains_regression_at_hpf(name):
    speaker, identity, _ = CHANNELS[name]
    hpf = float(identity["mandatory_hpf_hz"])
    freqs, mag_db = magnitude_db(COEFF_DIR / name)
    ref = passband_ref_db(
        freqs, mag_db, CROSSOVER_HZ, speaker["filter_type"])
    at_hpf = float(mag_db[np.argmin(np.abs(freqs - hpf))]) - ref
    assert at_hpf <= M2_MAINS_AT_HPF_MAX_DB, (name, at_hpf)
