"""Measured gate for the post-deploy re-measurement (US-174d).

Unit tests on closed_loop.measured_gate: verdicts, SNR -> INVALID,
fail-closed input handling, precedence, constant separation. The
end-to-end use on simulated corrections is in test_venue_closed_loop.py.
"""

import dataclasses
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from room_correction import closed_loop
from room_correction.closed_loop import (
    MAX_POSITIVE_DEVIATION_DB,
    MEASURED_MAX_POSITIVE_DEVIATION_DB,
    MEASUREMENT_SNR_MIN_DB,
    Verdict,
    measured_band_result,
    measured_gate,
)

GOOD_SNR = MEASUREMENT_SNR_MIN_DB + 20.0
TARGET = np.zeros(32)


def _curve(peak_db):
    r = np.full(32, -1.0)
    r[7] = peak_db
    return r


PASSING = (_curve(MEASURED_MAX_POSITIVE_DEVIATION_DB), TARGET, GOOD_SNR)
FAILING = (_curve(MEASURED_MAX_POSITIVE_DEVIATION_DB + 0.01), TARGET, GOOD_SNR)
INVALID = (_curve(0.0), TARGET, MEASUREMENT_SNR_MIN_DB - 0.01)


class TestBand:

    def test_at_limit_passes_just_over_fails(self):
        assert measured_band_result("sat", *PASSING[:2], snr_db=GOOD_SNR).verdict is Verdict.PASS
        r = measured_band_result("sat", *FAILING[:2], snr_db=GOOD_SNR)
        assert r.verdict is Verdict.FAIL
        assert r.deviation_db == pytest.approx(MEASURED_MAX_POSITIVE_DEVIATION_DB + 0.01)

    def test_snr_at_minimum_is_judged(self):
        r = measured_band_result("sat", *PASSING[:2], snr_db=MEASUREMENT_SNR_MIN_DB)
        assert r.verdict is Verdict.PASS

    @pytest.mark.parametrize("snr", [
        MEASUREMENT_SNR_MIN_DB - 0.01, None, float("nan"), float("inf"), float("-inf"),
        "80", True, [80.0], np.array([80.0])])
    def test_untrusted_snr_is_invalid_even_if_response_passes(self, snr):
        r = measured_band_result("sat", *PASSING[:2], snr_db=snr)
        assert r.verdict is Verdict.INVALID

    def test_low_snr_wins_over_a_failing_response(self):
        # A measurement below the SNR line says nothing: repeat, don't judge.
        r = measured_band_result("sat", *FAILING[:2], snr_db=MEASUREMENT_SNR_MIN_DB - 1)
        assert r.verdict is Verdict.INVALID

    @pytest.mark.parametrize("response", [
        None, "abc", b"abc", [1.0, [2.0, 3.0]], np.zeros((4, 8)), np.array([]),
        np.array([0.0, np.nan, 0.0]), np.array([0.0, np.inf]), np.zeros(31), 0.0])
    def test_malformed_response_fails_closed(self, response):
        r = measured_band_result("sat", response, TARGET, snr_db=GOOD_SNR)
        assert r.verdict is Verdict.FAIL
        r = measured_band_result("sat", TARGET, response, snr_db=GOOD_SNR)
        assert r.verdict is Verdict.FAIL

    def test_two_dimensional_curves_fail_even_if_shapes_match(self):
        flat = np.zeros((4, 8))
        assert measured_band_result("sat", flat, flat, snr_db=GOOD_SNR).verdict is Verdict.FAIL

    def test_uses_its_own_constant(self, monkeypatch):
        # The two constants are separate (AE): loosening the simulated one
        # must not loosen the measured gate, and the reverse.
        monkeypatch.setattr(closed_loop, "MAX_POSITIVE_DEVIATION_DB", 100.0)
        assert measured_band_result("sat", *FAILING[:2], snr_db=GOOD_SNR).verdict is Verdict.FAIL
        monkeypatch.setattr(closed_loop, "MEASURED_MAX_POSITIVE_DEVIATION_DB", 0.0)
        assert measured_band_result("sat", *PASSING[:2], snr_db=GOOD_SNR).verdict is Verdict.FAIL
        monkeypatch.undo()
        monkeypatch.setattr(closed_loop, "MEASURED_MAX_POSITIVE_DEVIATION_DB", 100.0)
        assert closed_loop.passes_residual_gate(*FAILING[:2]) is False

    def test_initial_values(self):
        # AE, 2026-10-25: initially the same 3.0 dB as the simulated gate.
        assert MEASURED_MAX_POSITIVE_DEVIATION_DB == MAX_POSITIVE_DEVIATION_DB == 3.0


class TestGate:

    def test_all_pass(self):
        r = measured_gate({"sat_left": PASSING, "sub1": PASSING}, PASSING)
        assert r.verdict is Verdict.PASS and r.passed
        assert [b.name for b in r.channels] == ["sat_left", "sub1"]
        assert r.system.name == "system"

    @pytest.mark.parametrize("channels,system,expected", [
        ({"a": PASSING, "b": FAILING}, PASSING, Verdict.FAIL),
        ({"a": PASSING, "b": PASSING}, FAILING, Verdict.FAIL),
        ({"a": FAILING, "b": INVALID}, PASSING, Verdict.INVALID),
        ({"a": FAILING, "b": FAILING}, INVALID, Verdict.INVALID),
        ({"a": PASSING}, INVALID, Verdict.INVALID),
    ])
    def test_precedence_invalid_then_fail(self, channels, system, expected):
        r = measured_gate(channels, system)
        assert r.verdict is expected
        assert not r.passed

    @pytest.mark.parametrize("channels,system", [
        ({}, PASSING), (None, PASSING), ([PASSING], PASSING), ("sat", PASSING),
        ({"a": PASSING}, None), ({"a": PASSING}, (TARGET, TARGET)),
        ({"a": None}, PASSING), ({"a": 3.0}, PASSING),
    ])
    def test_missing_or_malformed_parts_fail_closed(self, channels, system):
        r = measured_gate(channels, system)
        assert r.verdict is Verdict.FAIL

    def test_result_is_frozen(self):
        r = measured_gate({"a": PASSING}, PASSING)
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.verdict = Verdict.FAIL
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.system.verdict = Verdict.PASS
