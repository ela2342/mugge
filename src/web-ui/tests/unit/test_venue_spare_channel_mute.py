"""Spare channel mute of the markaudio-ultimax-200hz venue (US-173 M2).

Ch 4 (sub 2, AUX3) is unused at this venue. Its mute is the FIR itself:
the coefficients must resolve to the canonical all-zero zero.wav. A
dirac.wav here would pass audio through; -120 dB and the D-063 gate are
only the second layer.
"""

import hashlib
import pathlib
import struct

import yaml

REPO = pathlib.Path(__file__).resolve().parents[4]
VENUE = REPO / "configs/venues/markaudio-ultimax-200hz.yml"
COEFFS = REPO / "configs/coeffs"
TAPS = 16384

# configs/coeffs/zero.wav is canonical and never regenerated: RIFF,
# 16-byte fmt chunk (IEEE float, mono, 48 kHz, 32 bit), 16384 x 0.0f.
ZERO_SHA256 = (
    "97b9d9db69ae3abc524a3f87206b9a4c8d40a239ff30a98e4ebdcaf462e40c56")


def test_venue_ch4_resolves_to_all_zero_bytes():
    with open(VENUE) as f:
        ch4 = yaml.safe_load(f)["channels"]["4_sub2_lp"]
    path = COEFFS / ch4["coefficients"]
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == ZERO_SHA256, path
    assert data[36:40] == b"data"
    size = struct.unpack_from("<I", data, 40)[0]
    assert size == 4 * TAPS and data[44:44 + size] == bytes(size)
    assert ch4["gain_db"] == -120
