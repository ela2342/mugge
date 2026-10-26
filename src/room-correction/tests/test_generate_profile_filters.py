"""Tests for topology-agnostic FIR filter generation pipeline.

Covers _normalize_crossover_freqs, _resolve_bandpass_edges,
_generate_channel_crossover, and generate_profile_filters for
2-way (regression), 3-way, and 4-way topologies.
"""

import copy
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from room_correction import dsp_utils
from room_correction.combine import combine_filters
from room_correction.verify import load_filter
from room_correction.generate_profile_filters import (
    COMBINE_MARGIN_DB,
    _generate_channel_crossover,
    _normalize_crossover_freqs,
    _resolve_bandpass_edges,
    generate_profile_filters,
)


# ---------------------------------------------------------------------------
# Test profiles
# ---------------------------------------------------------------------------

PROFILE_2WAY = {
    "name": "2-way test",
    "topology": "2way",
    "crossover": {"frequency_hz": 200, "slope_db_per_oct": 48},
    "speakers": {
        "sat_left": {
            "identity": "sat-id",
            "role": "satellite",
            "channel": 0,
            "filter_type": "highpass",
        },
        "sub1": {
            "identity": "sub-id",
            "role": "subwoofer",
            "channel": 2,
            "filter_type": "lowpass",
        },
    },
}

IDENTITIES_2WAY = {
    "sat-id": {"mandatory_hpf_hz": 200},
    "sub-id": {"mandatory_hpf_hz": 42},
}

PROFILE_3WAY = {
    "name": "3-way test",
    "topology": "3way",
    "crossover": {"frequency_hz": [300, 2000], "slope_db_per_oct": 48},
    "speakers": {
        "bass": {
            "identity": "bass-id",
            "role": "fullrange",
            "channel": 0,
            "filter_type": "lowpass",
        },
        "mid": {
            "identity": "mid-id",
            "role": "midrange",
            "channel": 1,
            "filter_type": "bandpass",
        },
        "hf": {
            "identity": "hf-id",
            "role": "tweeter",
            "channel": 2,
            "filter_type": "highpass",
        },
    },
}

IDENTITIES_3WAY = {
    "bass-id": {},
    "mid-id": {},
    "hf-id": {},
}

PROFILE_4WAY = {
    "name": "4-way test",
    "topology": "4way",
    "crossover": {"frequency_hz": [80, 500, 3000], "slope_db_per_oct": 48},
    "speakers": {
        "sub": {
            "identity": "sub-id",
            "role": "subwoofer",
            "channel": 0,
            "filter_type": "lowpass",
        },
        "low_mid": {
            "identity": "lowmid-id",
            "role": "midrange",
            "channel": 1,
            "filter_type": "bandpass",
            "crossover_index": 0,
        },
        "high_mid": {
            "identity": "highmid-id",
            "role": "midrange",
            "channel": 2,
            "filter_type": "bandpass",
            "crossover_index": 1,
        },
        "hf": {
            "identity": "hf-id",
            "role": "tweeter",
            "channel": 3,
            "filter_type": "highpass",
        },
    },
}

IDENTITIES_4WAY = {
    "sub-id": {"mandatory_hpf_hz": 30},
    "lowmid-id": {},
    "highmid-id": {},
    "hf-id": {},
}

N_TAPS = 4096  # Smaller for fast tests


# ---------------------------------------------------------------------------
# _normalize_crossover_freqs
# ---------------------------------------------------------------------------

class TestNormalizeCrossoverFreqs(unittest.TestCase):

    def test_scalar_returns_single_element_list(self):
        profile = {"crossover": {"frequency_hz": 200}}
        self.assertEqual(_normalize_crossover_freqs(profile), [200.0])

    def test_list_returns_sorted(self):
        profile = {"crossover": {"frequency_hz": [2000, 300]}}
        self.assertEqual(_normalize_crossover_freqs(profile), [300.0, 2000.0])

    def test_missing_crossover_returns_empty(self):
        self.assertEqual(_normalize_crossover_freqs({}), [])

    def test_none_frequency_returns_empty(self):
        profile = {"crossover": {"frequency_hz": None}}
        self.assertEqual(_normalize_crossover_freqs(profile), [])

    def test_integer_values_become_float(self):
        profile = {"crossover": {"frequency_hz": [80, 500, 3000]}}
        result = _normalize_crossover_freqs(profile)
        self.assertEqual(result, [80.0, 500.0, 3000.0])
        for v in result:
            self.assertIsInstance(v, float)


# ---------------------------------------------------------------------------
# _resolve_bandpass_edges
# ---------------------------------------------------------------------------

class TestResolveBandpassEdges(unittest.TestCase):

    def test_explicit_edges(self):
        spk = {"bandpass_low_hz": 250, "bandpass_high_hz": 1800}
        low, high = _resolve_bandpass_edges(spk, [300, 2000])
        self.assertEqual(low, 250.0)
        self.assertEqual(high, 1800.0)

    def test_crossover_index_0(self):
        spk = {"crossover_index": 0}
        low, high = _resolve_bandpass_edges(spk, [80, 500, 3000])
        self.assertEqual(low, 80.0)
        self.assertEqual(high, 500.0)

    def test_crossover_index_1(self):
        spk = {"crossover_index": 1}
        low, high = _resolve_bandpass_edges(spk, [80, 500, 3000])
        self.assertEqual(low, 500.0)
        self.assertEqual(high, 3000.0)

    def test_fallback_uses_full_range(self):
        spk = {}
        low, high = _resolve_bandpass_edges(spk, [300, 2000])
        self.assertEqual(low, 300.0)
        self.assertEqual(high, 2000.0)

    def test_single_freq_raises(self):
        with self.assertRaises(ValueError):
            _resolve_bandpass_edges({}, [200])

    def test_empty_freqs_raises(self):
        with self.assertRaises(ValueError):
            _resolve_bandpass_edges({}, [])

    def test_crossover_index_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            _resolve_bandpass_edges({"crossover_index": 2}, [80, 500, 3000])

    def test_negative_crossover_index_raises(self):
        with self.assertRaises(ValueError):
            _resolve_bandpass_edges({"crossover_index": -1}, [80, 500, 3000])


# ---------------------------------------------------------------------------
# _generate_channel_crossover
# ---------------------------------------------------------------------------

class TestGenerateChannelCrossover(unittest.TestCase):

    def test_highpass_output_length(self):
        spk = {"filter_type": "highpass"}
        fir = _generate_channel_crossover(spk, [200.0], 48.0, N_TAPS, 48000)
        self.assertEqual(len(fir), N_TAPS)

    def test_lowpass_output_length(self):
        spk = {"filter_type": "lowpass"}
        fir = _generate_channel_crossover(spk, [200.0], 48.0, N_TAPS, 48000)
        self.assertEqual(len(fir), N_TAPS)

    def test_bandpass_output_length(self):
        spk = {"filter_type": "bandpass"}
        fir = _generate_channel_crossover(spk, [300.0, 2000.0], 48.0, N_TAPS, 48000)
        self.assertEqual(len(fir), N_TAPS)

    def test_unknown_type_raises(self):
        spk = {"filter_type": "notch"}
        with self.assertRaises(ValueError):
            _generate_channel_crossover(spk, [200.0], 48.0, N_TAPS, 48000)

    def test_highpass_uses_last_freq(self):
        """Highpass should use the highest crossover frequency."""
        spk = {"filter_type": "highpass"}
        fir = _generate_channel_crossover(spk, [300.0, 2000.0], 48.0, N_TAPS, 48000)
        # Verify it's a highpass at 2000 Hz — check attenuation at 100 Hz
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_100 = np.argmin(np.abs(freqs - 100))
        idx_10k = np.argmin(np.abs(freqs - 10000))
        # At 100 Hz (well below 2000 Hz crossover) should be heavily attenuated
        self.assertLess(mag_db[idx_100], -40)
        # At 10 kHz (above crossover) should be near 0 dB
        self.assertGreater(mag_db[idx_10k], -3)

    def test_lowpass_uses_first_freq(self):
        """Lowpass should use the lowest crossover frequency."""
        spk = {"filter_type": "lowpass"}
        fir = _generate_channel_crossover(spk, [300.0, 2000.0], 48.0, N_TAPS, 48000)
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_100 = np.argmin(np.abs(freqs - 100))
        idx_5k = np.argmin(np.abs(freqs - 5000))
        # At 100 Hz (below 300 Hz crossover) should be near 0 dB
        self.assertGreater(mag_db[idx_100], -3)
        # At 5 kHz (well above crossover) should be heavily attenuated
        self.assertLess(mag_db[idx_5k], -40)

    def test_default_type_is_highpass(self):
        spk = {}  # No filter_type specified
        fir = _generate_channel_crossover(spk, [200.0], 48.0, N_TAPS, 48000)
        # Should work (defaults to highpass)
        self.assertEqual(len(fir), N_TAPS)

    def test_empty_freqs_highpass_defaults_80(self):
        """With no crossover frequencies, highpass defaults to 80 Hz."""
        spk = {"filter_type": "highpass"}
        fir = _generate_channel_crossover(spk, [], 48.0, N_TAPS, 48000)
        self.assertEqual(len(fir), N_TAPS)


# ---------------------------------------------------------------------------
# generate_profile_filters — 2-way (regression)
# ---------------------------------------------------------------------------

class TestGenerateProfileFilters2Way(unittest.TestCase):
    """2-way profile should produce one HP and one LP filter, matching
    the behaviour of the old Bose-specific generator."""

    def setUp(self):
        self.result = generate_profile_filters(
            PROFILE_2WAY, IDENTITIES_2WAY, n_taps=N_TAPS,
        )

    def test_returns_both_channels(self):
        self.assertIn("sat_left", self.result)
        self.assertIn("sub1", self.result)
        self.assertEqual(len(self.result), 2)

    def test_filter_lengths(self):
        for key, fir in self.result.items():
            self.assertEqual(len(fir), N_TAPS, f"{key} length mismatch")

    def test_d009_compliance(self):
        """Every filter must have gain <= 0 dB (D-009 safety: target -0.5 dB).

        The combine module clips to COMBINE_MARGIN_DB (-0.6 dB) but cepstral
        reconstruction introduces small deviations, especially at lower tap
        counts.  We allow up to -0.1 dB which is still well within safety.
        """
        for key, fir in self.result.items():
            spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
            mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
            max_gain = np.max(mag_db)
            self.assertLessEqual(
                max_gain, -0.1,
                f"{key}: max gain {max_gain:.2f} dB exceeds D-009 safety"
            )

    def test_satellite_is_highpass(self):
        """Satellite channel should attenuate below crossover (200 Hz)."""
        fir = self.result["sat_left"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_50 = np.argmin(np.abs(freqs - 50))
        idx_1k = np.argmin(np.abs(freqs - 1000))
        # Well below crossover should be heavily attenuated
        self.assertLess(mag_db[idx_50], -20)
        # Well above crossover should be near margin
        self.assertGreater(mag_db[idx_1k], COMBINE_MARGIN_DB - 3)

    def test_subwoofer_is_lowpass(self):
        """Subwoofer channel should attenuate above crossover (200 Hz)."""
        fir = self.result["sub1"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_50 = np.argmin(np.abs(freqs - 50))
        idx_2k = np.argmin(np.abs(freqs - 2000))
        # Below crossover passband (after subsonic HPF ~42 Hz)
        self.assertGreater(mag_db[idx_50], COMBINE_MARGIN_DB - 6)
        # Well above crossover should be heavily attenuated
        self.assertLess(mag_db[idx_2k], -20)

    def test_subwoofer_has_subsonic_hpf(self):
        """Sub with mandatory_hpf_hz=42 should have subsonic protection."""
        fir = self.result["sub1"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        # At 10 Hz (well below 42 Hz HPF) should be very attenuated
        idx_10 = np.argmin(np.abs(freqs - 10))
        idx_80 = np.argmin(np.abs(freqs - 80))
        self.assertLess(mag_db[idx_10], mag_db[idx_80] - 10,
                        "Subsonic HPF should attenuate below 42 Hz")


# ---------------------------------------------------------------------------
# generate_profile_filters — 3-way
# ---------------------------------------------------------------------------

class TestGenerateProfileFilters3Way(unittest.TestCase):
    """3-way profile: LP bass, BP mid, HP tweeter."""

    def setUp(self):
        self.result = generate_profile_filters(
            PROFILE_3WAY, IDENTITIES_3WAY, n_taps=N_TAPS,
        )

    def test_returns_all_three_channels(self):
        self.assertIn("bass", self.result)
        self.assertIn("mid", self.result)
        self.assertIn("hf", self.result)
        self.assertEqual(len(self.result), 3)

    def test_filter_lengths(self):
        for key, fir in self.result.items():
            self.assertEqual(len(fir), N_TAPS, f"{key} length mismatch")

    def test_d009_compliance(self):
        for key, fir in self.result.items():
            spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
            mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
            max_gain = np.max(mag_db)
            self.assertLessEqual(
                max_gain, -0.1,
                f"{key}: max gain {max_gain:.2f} dB exceeds D-009 safety"
            )

    def test_bass_is_lowpass_at_300(self):
        """Bass channel lowpass at 300 Hz."""
        fir = self.result["bass"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_100 = np.argmin(np.abs(freqs - 100))
        idx_3k = np.argmin(np.abs(freqs - 3000))
        self.assertGreater(mag_db[idx_100], COMBINE_MARGIN_DB - 3)
        self.assertLess(mag_db[idx_3k], -20)

    def test_mid_is_bandpass_300_to_2000(self):
        """Mid channel bandpass 300-2000 Hz."""
        fir = self.result["mid"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        # Passband center ~775 Hz (geometric mean of 300 and 2000)
        idx_800 = np.argmin(np.abs(freqs - 800))
        idx_30 = np.argmin(np.abs(freqs - 30))
        idx_10k = np.argmin(np.abs(freqs - 10000))
        self.assertGreater(mag_db[idx_800], COMBINE_MARGIN_DB - 3,
                           "Bandpass mid should pass ~800 Hz")
        self.assertLess(mag_db[idx_30], -20,
                        "Bandpass mid should attenuate 30 Hz")
        self.assertLess(mag_db[idx_10k], -20,
                        "Bandpass mid should attenuate 10 kHz")

    def test_hf_is_highpass_at_2000(self):
        """HF channel highpass at 2000 Hz."""
        fir = self.result["hf"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_500 = np.argmin(np.abs(freqs - 500))
        idx_10k = np.argmin(np.abs(freqs - 10000))
        self.assertLess(mag_db[idx_500], -20)
        self.assertGreater(mag_db[idx_10k], COMBINE_MARGIN_DB - 3)


# ---------------------------------------------------------------------------
# generate_profile_filters — 4-way
# ---------------------------------------------------------------------------

class TestGenerateProfileFilters4Way(unittest.TestCase):
    """4-way profile: LP sub, BP low-mid [80-500], BP high-mid [500-3000], HP tweeter."""

    def setUp(self):
        self.result = generate_profile_filters(
            PROFILE_4WAY, IDENTITIES_4WAY, n_taps=N_TAPS,
        )

    def test_returns_all_four_channels(self):
        self.assertIn("sub", self.result)
        self.assertIn("low_mid", self.result)
        self.assertIn("high_mid", self.result)
        self.assertIn("hf", self.result)
        self.assertEqual(len(self.result), 4)

    def test_filter_lengths(self):
        for key, fir in self.result.items():
            self.assertEqual(len(fir), N_TAPS, f"{key} length mismatch")

    def test_d009_compliance(self):
        for key, fir in self.result.items():
            spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
            mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
            max_gain = np.max(mag_db)
            self.assertLessEqual(
                max_gain, -0.1,
                f"{key}: max gain {max_gain:.2f} dB exceeds D-009 safety"
            )

    def test_sub_is_lowpass_at_80(self):
        fir = self.result["sub"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_40 = np.argmin(np.abs(freqs - 40))
        idx_500 = np.argmin(np.abs(freqs - 500))
        self.assertGreater(mag_db[idx_40], COMBINE_MARGIN_DB - 6)
        self.assertLess(mag_db[idx_500], -20)

    def test_sub_has_subsonic_hpf(self):
        """Sub with mandatory_hpf_hz=30 should have subsonic protection."""
        fir = self.result["sub"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_5 = np.argmin(np.abs(freqs - 5))
        idx_50 = np.argmin(np.abs(freqs - 50))
        self.assertLess(mag_db[idx_5], mag_db[idx_50] - 10)

    def test_low_mid_bandpass_80_500(self):
        fir = self.result["low_mid"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        # Center ~200 Hz (geometric mean of 80 and 500)
        idx_200 = np.argmin(np.abs(freqs - 200))
        idx_10 = np.argmin(np.abs(freqs - 10))
        idx_5k = np.argmin(np.abs(freqs - 5000))
        self.assertGreater(mag_db[idx_200], COMBINE_MARGIN_DB - 3)
        self.assertLess(mag_db[idx_10], -20)
        self.assertLess(mag_db[idx_5k], -20)

    def test_high_mid_bandpass_500_3000(self):
        fir = self.result["high_mid"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        # Center ~1225 Hz (geometric mean of 500 and 3000)
        idx_1200 = np.argmin(np.abs(freqs - 1200))
        idx_50 = np.argmin(np.abs(freqs - 50))
        idx_15k = np.argmin(np.abs(freqs - 15000))
        self.assertGreater(mag_db[idx_1200], COMBINE_MARGIN_DB - 3)
        self.assertLess(mag_db[idx_50], -20)
        self.assertLess(mag_db[idx_15k], -20)

    def test_hf_is_highpass_at_3000(self):
        fir = self.result["hf"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_500 = np.argmin(np.abs(freqs - 500))
        idx_10k = np.argmin(np.abs(freqs - 10000))
        self.assertLess(mag_db[idx_500], -20)
        self.assertGreater(mag_db[idx_10k], COMBINE_MARGIN_DB - 3)


# ---------------------------------------------------------------------------
# WAV export
# ---------------------------------------------------------------------------

class TestGenerateProfileFiltersExport(unittest.TestCase):
    """Test WAV file export via output_dir."""

    def test_exports_wav_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_profile_filters(
                PROFILE_2WAY, IDENTITIES_2WAY,
                output_dir=tmpdir, n_taps=N_TAPS,
            )
            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 2)
            for f in files:
                self.assertTrue(f.endswith(".wav"))
                self.assertTrue(f.startswith("combined_"))

    def test_exports_with_timestamp(self):
        from datetime import datetime
        ts = datetime(2026, 3, 27, 12, 0, 0)
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_profile_filters(
                PROFILE_2WAY, IDENTITIES_2WAY,
                output_dir=tmpdir, n_taps=N_TAPS, timestamp=ts,
            )
            files = os.listdir(tmpdir)
            for f in files:
                self.assertIn("20260327_120000", f)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestGenerateProfileFiltersEdgeCases(unittest.TestCase):

    def test_custom_correction_filter_used(self):
        """When correction_filters are provided, they should be used."""
        # Create a correction filter that heavily attenuates everything
        n = N_TAPS
        attenuation = np.zeros(n)
        attenuation[0] = 0.01  # -40 dB dirac
        corrections = {"sat_left": attenuation, "sub1": attenuation}
        result = generate_profile_filters(
            PROFILE_2WAY, IDENTITIES_2WAY,
            correction_filters=corrections, n_taps=N_TAPS,
        )
        # Both filters should be much quieter than without correction
        for key, fir in result.items():
            spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
            mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
            # With -40 dB correction, max gain should be well below -20 dB
            self.assertLess(np.max(mag_db), -20,
                            f"{key}: correction filter not applied")

    def test_missing_identity_no_subsonic(self):
        """Speaker with identity not in identities dict gets no subsonic HPF."""
        identities = {"sat-id": {}}  # sub-id missing
        result = generate_profile_filters(
            PROFILE_2WAY, identities, n_taps=N_TAPS,
        )
        self.assertIn("sub1", result)
        # Should still produce a valid filter (lowpass without subsonic)
        self.assertEqual(len(result["sub1"]), N_TAPS)

    def test_no_mandatory_hpf_no_subsonic(self):
        """Identity without mandatory_hpf_hz gets no subsonic filter."""
        identities = {
            "sat-id": {},
            "sub-id": {},  # No mandatory_hpf_hz
        }
        result = generate_profile_filters(
            PROFILE_2WAY, identities, n_taps=N_TAPS,
        )
        # Sub should still work, just without subsonic protection
        fir = result["sub1"]
        spectrum = np.fft.rfft(fir, n=N_TAPS * 4)
        freqs = np.fft.rfftfreq(N_TAPS * 4, 1.0 / 48000)
        mag_db = dsp_utils.linear_to_db(np.abs(spectrum))
        idx_10 = np.argmin(np.abs(freqs - 10))
        idx_100 = np.argmin(np.abs(freqs - 100))
        # Without subsonic HPF, 10 Hz should be closer to 100 Hz level
        # (both are in the lowpass passband)
        self.assertGreater(mag_db[idx_10], mag_db[idx_100] - 10)

    def test_empty_speakers_returns_empty(self):
        profile = {
            "crossover": {"frequency_hz": 200, "slope_db_per_oct": 48},
            "speakers": {},
        }
        result = generate_profile_filters(profile, {}, n_taps=N_TAPS)
        self.assertEqual(result, {})



# ---------------------------------------------------------------------------
# crossover.type pass-through (F-374)
# ---------------------------------------------------------------------------

def _profile_2way_lr4(crossover):
    profile = {
        "speakers": {
            "sat_left": {"identity": "sat", "filter_type": "highpass"},
            "sub1": {"identity": "sub", "filter_type": "lowpass"},
        },
    }
    if crossover is not None:
        profile["crossover"] = crossover
    return profile


class TestCrossoverTypePassThrough(unittest.TestCase):
    """crossover.type selects the alignment; missing type means LR."""

    XO = {"frequency_hz": 200, "slope_db_per_oct": 24}

    def _run(self, crossover):
        return generate_profile_filters(
            _profile_2way_lr4(crossover), {}, n_taps=N_TAPS)

    def test_missing_type_defaults_to_linkwitz_riley(self):
        implicit = self._run(dict(self.XO))
        explicit = self._run(dict(self.XO, type="linkwitz-riley"))
        for key in implicit:
            self.assertTrue(np.array_equal(implicit[key], explicit[key]), key)

    def test_linkwitz_riley_differs_from_legacy(self):
        lr = _generate_channel_crossover(
            {"filter_type": "highpass"}, [200.0], 24, N_TAPS, 48000,
            "linkwitz-riley")
        legacy = _generate_channel_crossover(
            {"filter_type": "highpass"}, [200.0], 24, N_TAPS, 48000)
        self.assertFalse(np.allclose(lr, legacy))

    def test_profile_output_differs_from_legacy(self):
        """Through generate_profile_filters: the LR alignment is handed on."""
        result = self._run(dict(self.XO, type="linkwitz-riley"))
        dirac = np.zeros(N_TAPS)
        dirac[0] = 1.0
        for key, filter_type in (("sat_left", "highpass"), ("sub1", "lowpass")):
            xo = _generate_channel_crossover(
                {"filter_type": filter_type}, [200.0], 24, N_TAPS, 48000)
            legacy = combine_filters(
                dirac, xo, N_TAPS, margin_db=COMBINE_MARGIN_DB)
            self.assertFalse(np.allclose(result[key], legacy), key)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            self._run(dict(self.XO, type="butterworth"))

    def test_unknown_type_raises_without_speakers(self):
        with self.assertRaises(ValueError):
            generate_profile_filters(
                {"crossover": dict(self.XO, type="bessel"), "speakers": {}}, {},
                n_taps=N_TAPS)

    def test_no_crossover_section_keeps_legacy(self):
        result = self._run(None)
        dirac = np.zeros(N_TAPS)
        dirac[0] = 1.0
        for key, filter_type in (("sat_left", "highpass"), ("sub1", "lowpass")):
            xo = _generate_channel_crossover(
                {"filter_type": filter_type}, [], 48.0, N_TAPS, 48000)
            expected = combine_filters(
                dirac, xo, N_TAPS, margin_db=COMBINE_MARGIN_DB)
            self.assertTrue(np.array_equal(result[key], expected), key)

    def test_bandpass_edges_are_linkwitz_riley(self):
        bp = _generate_channel_crossover(
            {"filter_type": "bandpass"}, [300.0, 2000.0], 48, 16384, 48000,
            "linkwitz-riley")
        freqs, mag = dsp_utils.rfft_magnitude(bp, n_fft=1 << 17)
        for edge in (300.0, 2000.0):
            level = 20 * np.log10(mag[np.argmin(np.abs(freqs - edge))])
            self.assertAlmostEqual(level, -6.0, delta=0.5)



# ---------------------------------------------------------------------------
# Real markaudio-ultimax profile: D-031 protection present (F-374 / F-385)
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MARKAUDIO_PROFILE = os.path.join(
    REPO_ROOT, "configs", "speakers", "profiles", "2way-200hz-markaudio-ultimax.yml")
PROTECTION_MIN_CUT_DB = 18.0


def _load_profile_with_identities(path):
    import yaml
    from room_correction.speaker_sim import load_identity

    with open(path) as f:
        profile = yaml.safe_load(f)
    identities = {
        spk["identity"]: load_identity(spk["identity"])
        for spk in profile["speakers"].values()
    }
    return profile, identities


def _exported_sat(profile, identities, directory):
    generate_profile_filters(profile, identities, output_dir=directory)
    data, _ = load_filter(os.path.join(directory, "combined_sat_left.wav"))
    return data


class TestMarkaudioProtectionPresent(unittest.TestCase):
    """The sat leg keeps its mandatory subsonic HPF (D-031).

    The HPF costs crossover phase at 200 Hz (F-385).  This test guards
    against "fixing" that by dropping the protection; it deliberately
    asserts nothing about phase or sum.
    """

    def test_sat_subsonic_cuts_one_octave_below_corner(self):
        profile, identities = _load_profile_with_identities(MARKAUDIO_PROFILE)
        sat_identity = profile["speakers"]["sat_left"]["identity"]
        hpf_hz = identities[sat_identity].get("mandatory_hpf_hz")
        self.assertIsNotNone(hpf_hz)

        unprotected = copy.deepcopy(identities)
        unprotected[sat_identity]["mandatory_hpf_hz"] = None
        with tempfile.TemporaryDirectory() as d:
            protected_sat = _exported_sat(profile, identities, d)
        with tempfile.TemporaryDirectory() as d:
            unprotected_sat = _exported_sat(profile, unprotected, d)

        n_fft = 1 << 17
        freqs, protected_mag = dsp_utils.rfft_magnitude(protected_sat, n_fft=n_fft)
        _, unprotected_mag = dsp_utils.rfft_magnitude(unprotected_sat, n_fft=n_fft)
        i = np.argmin(np.abs(freqs - hpf_hz / 2))
        cut_db = 20 * np.log10(unprotected_mag[i] / protected_mag[i])
        print(f"markaudio sat protection at {freqs[i]:.1f} Hz: {cut_db:.2f} dB cut")
        self.assertGreaterEqual(cut_db, PROTECTION_MIN_CUT_DB)



class TestMarkaudioLr4PostCombine(unittest.TestCase):
    """LR4 200 Hz post-combine gate on the markaudio profile, sat HPF removed.

    The sat's D-031 subsonic is removed in-test only: its minimum-phase
    lead at 200 Hz is tracked as F-385.  Levels are relative to each WAV's
    own passband plateau.  The +-0.7 dB tolerances are interim: combine.py's
    per-bin D-009 clip lifts the crossover region ~0.6 dB above the plateau.
    F-383 (scalar D-009) tightens them to legs -6 +-0.5 dB and sum +-0.1 dB.
    """

    FC = 200.0
    LEG_DB, LEG_TOL_DB = -6.0, 0.7
    SUM_TOL_DB = 0.7
    PHASE_AT_FC_DEG = 5.0
    PHASE_NEAR_FC_DEG = 10.0
    D009_MAX_DB = -0.5

    @classmethod
    def setUpClass(cls):
        profile, identities = _load_profile_with_identities(MARKAUDIO_PROFILE)
        sat_identity = profile["speakers"]["sat_left"]["identity"]
        identities = copy.deepcopy(identities)
        identities[sat_identity]["mandatory_hpf_hz"] = None
        with tempfile.TemporaryDirectory() as d:
            generate_profile_filters(profile, identities, output_dir=d)
            cls.wavs = {
                key: load_filter(os.path.join(d, f"combined_{key}.wav"))[0]
                for key in profile["speakers"]
            }
        n_fft = 1 << 17
        cls.freqs = np.fft.rfftfreq(n_fft, d=1.0 / 48000)
        cls.hp = np.fft.rfft(cls.wavs["sat_left"], n=n_fft)
        cls.lp = np.fft.rfft(cls.wavs["sub1"], n=n_fft)
        f = cls.freqs
        cls.i_fc = np.argmin(np.abs(f - cls.FC))
        cls.near = (f >= cls.FC / 2) & (f <= 2 * cls.FC)
        cls.hp_plateau = np.mean(
            20 * np.log10(np.abs(cls.hp[(f >= 2 * cls.FC) & (f <= 20000)])))
        cls.lp_plateau = np.mean(
            20 * np.log10(np.abs(cls.lp[(f >= 20) & (f <= cls.FC / 2)])))

    def test_legs_minus_6db_relative_at_fc(self):
        hp_db = 20 * np.log10(np.abs(self.hp[self.i_fc])) - self.hp_plateau
        lp_db = 20 * np.log10(np.abs(self.lp[self.i_fc])) - self.lp_plateau
        print(f"markaudio LR4 post-combine legs at fc: HP {hp_db:.2f}, "
              f"LP {lp_db:.2f} dB re plateau")
        self.assertAlmostEqual(hp_db, self.LEG_DB, delta=self.LEG_TOL_DB)
        self.assertAlmostEqual(lp_db, self.LEG_DB, delta=self.LEG_TOL_DB)

    def test_sum_relative_near_fc(self):
        plateau = (self.hp_plateau + self.lp_plateau) / 2
        sum_db = 20 * np.log10(np.abs(self.hp + self.lp)[self.near]) - plateau
        print(f"markaudio LR4 post-combine sum fc/2..2fc: "
              f"{sum_db.min():.3f}..{sum_db.max():.3f} dB re plateau")
        self.assertGreaterEqual(sum_db.min(), -self.SUM_TOL_DB)
        self.assertLessEqual(sum_db.max(), self.SUM_TOL_DB)

    def test_phase_tracking(self):
        at_fc = np.degrees(np.abs(np.angle(self.hp[self.i_fc] / self.lp[self.i_fc])))
        near = np.degrees(np.abs(np.angle(self.hp[self.near] / self.lp[self.near])))
        print(f"markaudio LR4 post-combine phase: {at_fc:.2f} deg at fc, "
              f"{near.max():.2f} deg max fc/2..2fc")
        self.assertLessEqual(at_fc, self.PHASE_AT_FC_DEG)
        self.assertLessEqual(near.max(), self.PHASE_NEAR_FC_DEG)

    def test_d009_absolute(self):
        n_fft = 4 * len(self.wavs["sat_left"])
        for key, fir in self.wavs.items():
            freqs, mag = dsp_utils.rfft_magnitude(fir, n_fft=n_fft)
            band = (freqs >= 20) & (freqs <= 20000)
            max_db = 20 * np.log10(mag[band].max())
            with self.subTest(key=key):
                self.assertLessEqual(max_db, self.D009_MAX_DB)


# Regression ceiling only, not a target; tightening or replacing it is
# F-383/F-385; relaxing it needs joint Architect+AE approval.
REAL_PROFILE_REGRESSION_CEILING = {
    "phase_at_fc_deg": 35.0,
    "phase_near_fc_deg": 75.0,   # fc/2..2fc
    "sum_tol_db": 1.0,           # re plateau, fc/2..2fc
    "d009_max_db": -0.5,         # absolute (D-009, hard)
}
_CEILING_STOP = "joint Architect+AE STOP (F-374 rule)"


class TestMarkaudioRealProfileCeiling(unittest.TestCase):
    """Real, unmodified markaudio profile (sat D-031 HPF kept).

    Same method as TestMarkaudioLr4PostCombine.  The sat subsonic's phase
    lead (F-385) and combine.py's per-bin clip (F-383) are why this is a
    ceiling, not the LR4 target.
    """

    FC = 200.0

    @classmethod
    def setUpClass(cls):
        profile, identities = _load_profile_with_identities(MARKAUDIO_PROFILE)
        with tempfile.TemporaryDirectory() as d:
            generate_profile_filters(profile, identities, output_dir=d)
            cls.wavs = {
                key: load_filter(os.path.join(d, f"combined_{key}.wav"))[0]
                for key in profile["speakers"]
            }
        n_fft = 1 << 17
        cls.freqs = np.fft.rfftfreq(n_fft, d=1.0 / 48000)
        cls.hp = np.fft.rfft(cls.wavs["sat_left"], n=n_fft)
        cls.lp = np.fft.rfft(cls.wavs["sub1"], n=n_fft)
        f = cls.freqs
        cls.i_fc = np.argmin(np.abs(f - cls.FC))
        cls.near = (f >= cls.FC / 2) & (f <= 2 * cls.FC)
        cls.hp_plateau = np.mean(
            20 * np.log10(np.abs(cls.hp[(f >= 2 * cls.FC) & (f <= 20000)])))
        cls.lp_plateau = np.mean(
            20 * np.log10(np.abs(cls.lp[(f >= 20) & (f <= cls.FC / 2)])))

    def test_phase_within_ceiling(self):
        c = REAL_PROFILE_REGRESSION_CEILING
        at_fc = np.degrees(np.abs(np.angle(self.hp[self.i_fc] / self.lp[self.i_fc])))
        near = np.degrees(np.abs(np.angle(self.hp[self.near] / self.lp[self.near])))
        print(f"markaudio real profile phase: {at_fc:.2f} deg at fc, "
              f"{near.max():.2f} deg max fc/2..2fc")
        self.assertLessEqual(at_fc, c["phase_at_fc_deg"], _CEILING_STOP)
        self.assertLessEqual(near.max(), c["phase_near_fc_deg"], _CEILING_STOP)

    def test_sum_within_ceiling(self):
        tol = REAL_PROFILE_REGRESSION_CEILING["sum_tol_db"]
        plateau = (self.hp_plateau + self.lp_plateau) / 2
        sum_db = 20 * np.log10(np.abs(self.hp + self.lp)[self.near]) - plateau
        print(f"markaudio real profile sum fc/2..2fc: "
              f"{sum_db.min():.3f}..{sum_db.max():.3f} dB re plateau")
        self.assertGreaterEqual(sum_db.min(), -tol, _CEILING_STOP)
        self.assertLessEqual(sum_db.max(), tol, _CEILING_STOP)

    def test_d009_absolute(self):
        limit = REAL_PROFILE_REGRESSION_CEILING["d009_max_db"]
        band = (self.freqs >= 20) & (self.freqs <= 20000)
        for key, fir in self.wavs.items():
            max_db = 20 * np.log10(
                np.abs(np.fft.rfft(fir, n=len(self.freqs) * 2 - 2)[band]).max())
            print(f"markaudio real profile max|H| {key}: {max_db:.3f} dB")
            with self.subTest(key=key):
                self.assertLessEqual(max_db, limit, _CEILING_STOP)


if __name__ == "__main__":
    unittest.main()
