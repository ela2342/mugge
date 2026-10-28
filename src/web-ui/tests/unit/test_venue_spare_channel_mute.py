"""Spare channel mute of the 200 Hz CHN-50P/UMII18-22 venues (US-173 M2).

Ch 4 (sub 2, AUX3) is unused at these venues. Its mute is the FIR itself.
The convolver always loads /etc/pi4audio/coeffs/combined_sub2_lp.wav
(30-filter-chain-convolver.conf); the venue `coefficients:` field is
metadata only. So two things must hold: the venue names zero.wav, and the
venue WAV set ships combined_sub2_lp.wav as the canonical all-zero bytes.
A dirac.wav here would pass audio through; -120 dB and the D-063 gate are
only the second layer.

zero.wav has no kind in run_venue_checks (AE + Architect, 2026-10-26),
so this file checks it: format and float32 subtype from
room_correction.verify, plus the canonical all-zero bytes.
"""

import hashlib
import pathlib
import struct

import pytest
import yaml

from room_correction.verify import verify_format, verify_wav_subtype

REPO = pathlib.Path(__file__).resolve().parents[4]
VENUES = REPO / "configs/venues"
COEFFS = REPO / "configs/coeffs"
VENUE_SET = COEFFS / "markaudio-ultimax-200hz"
TAPS = 16384

# configs/coeffs/zero.wav is canonical and never regenerated: RIFF,
# 16-byte fmt chunk (IEEE float, mono, 48 kHz, 32 bit), 16384 x 0.0f.
ZERO_SHA256 = (
    "97b9d9db69ae3abc524a3f87206b9a4c8d40a239ff30a98e4ebdcaf462e40c56")


def assert_all_zero_wav(path):
    for result in (verify_format(str(path), TAPS),
                   verify_wav_subtype(str(path))):
        assert result.passed, result
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == ZERO_SHA256, path
    assert data[36:40] == b"data"
    size = struct.unpack_from("<I", data, 40)[0]
    assert size == 4 * TAPS and data[44:44 + size] == bytes(size)


@pytest.mark.parametrize("venue", [
    "markaudio-ultimax-200hz", "home-lab-chn50p-ultimax"])
def test_venue_ch4_resolves_to_all_zero_bytes(venue):
    with open(VENUES / (venue + ".yml")) as f:
        ch4 = yaml.safe_load(f)["channels"]["4_sub2_lp"]
    assert ch4["coefficients"] == "zero.wav"
    assert_all_zero_wav(COEFFS / ch4["coefficients"])
    assert ch4["gain_db"] == -120


def test_venue_set_sub2_file_the_convolver_loads_is_all_zero():
    assert_all_zero_wav(VENUE_SET / "combined_sub2_lp.wav")
