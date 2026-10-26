"""
Verification suite for generated room correction filters.

This is CRITICAL safety infrastructure. Every generated filter MUST pass all
checks before deployment. The D-009 gain limit check is a HARD FAIL — no
exceptions, no overrides.

Why this matters: psytrance source material at -0.5 LUFS leaves zero headroom.
Any filter gain above -0.5dB risks clipping in the DAC, which causes audible
distortion through the PA system. The -0.5dB safety margin is not conservative —
it is the absolute minimum for safe operation.
"""

import logging

import numpy as np
import soundfile as sf

from . import dsp_utils


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
log = logging.getLogger(__name__)


class VerificationResult:
    """Result of a single verification check."""

    def __init__(self, name, passed, message, details=None):
        self.name = name
        self.passed = bool(passed)
        self.message = message
        self.details = details or {}

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name}: {self.message}"


def load_filter(filter_path):
    """Load a filter WAV file and return (data, sample_rate)."""
    data, sr = sf.read(filter_path, dtype='float64')
    if data.ndim > 1:
        data = data[:, 0]
    return data, sr


def verify_d009(filter_path, margin_db=-0.5):
    """
    D-009 compliance: every frequency bin gain <= margin_db.

    This is a HARD FAIL. No frequency bin in the filter's magnitude spectrum
    may exceed margin_db. This prevents any amplification that could cause
    clipping with hot source material.

    The check examines the filter's magnitude spectrum at full FFT resolution
    and reports the worst-case (maximum) gain found.

    Parameters
    ----------
    filter_path : str
        Path to the filter WAV file.
    margin_db : float
        Maximum allowed gain in dB (default -0.5dB per D-009).

    Returns
    -------
    VerificationResult
    """
    data, sr = load_filter(filter_path)
    freqs, magnitudes = dsp_utils.rfft_magnitude(data)

    # Only check within the audio band (20Hz - 20kHz)
    audio_band = (freqs >= 20) & (freqs <= 20000)
    if not np.any(audio_band):
        return VerificationResult(
            "D-009", False, "No frequency bins in audio band", {}
        )

    gains_db = dsp_utils.linear_to_db(magnitudes[audio_band])
    max_gain_db = float(np.max(gains_db))
    max_gain_freq = float(freqs[audio_band][np.argmax(gains_db)])

    # Use small tolerance for floating point (0.01dB)
    passed = max_gain_db <= margin_db + 0.01
    message = (
        f"Max gain: {max_gain_db:.2f}dB at {max_gain_freq:.1f}Hz "
        f"(limit: {margin_db}dB)"
    )

    return VerificationResult(
        "D-009 Gain Limit",
        passed,
        message,
        {"max_gain_db": max_gain_db, "max_gain_freq": max_gain_freq},
    )


def verify_target_deviation(filter_path, target_curve=None, tolerance_db=8.0):
    """
    Check that the filter's passband matches the target curve within tolerance.

    Identifies the filter's passband (the frequency range where gain is within
    20dB of the maximum) and checks target deviation only within that band.
    Stopband frequencies (where the crossover rolls off) are excluded since
    heavy attenuation there is intentional.

    If no target curve is provided, checks deviation from the filter's own
    passband average level.

    Parameters
    ----------
    filter_path : str
        Path to the filter WAV file.
    target_curve : dict, optional
        Mapping of frequency (Hz) -> target level (dB).
    tolerance_db : float
        Maximum allowed deviation from target in dB.

    Returns
    -------
    VerificationResult
    """
    data, sr = load_filter(filter_path)
    freqs, magnitudes = dsp_utils.rfft_magnitude(data)
    gains_db = dsp_utils.linear_to_db(magnitudes)

    # ISO 1/3 octave center frequencies from 25Hz to 16kHz
    third_octave_centers = [
        25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400,
        500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000,
        6300, 8000, 10000, 12500, 16000,
    ]

    # Determine passband: frequency range where gain is within 10dB of max.
    # This narrower threshold excludes the crossover transition band where
    # large attenuation is intentional (e.g., HP filter below 80Hz).
    audio_mask = (freqs >= 20) & (freqs <= 20000)
    if not np.any(audio_mask):
        return VerificationResult("Target Deviation", False, "No audio band data", {})

    max_gain = np.max(gains_db[audio_mask])
    passband_threshold = max_gain - 10.0

    # Measure level at each 1/3 octave center within the passband
    passband_levels = []
    for fc in third_octave_centers:
        if fc > sr / 2:
            continue
        idx = np.argmin(np.abs(freqs - fc))
        if gains_db[idx] >= passband_threshold:
            passband_levels.append(gains_db[idx])

    if not passband_levels:
        return VerificationResult("Target Deviation", False, "No passband detected", {})

    # Reference level: average passband gain (or use target curve)
    ref_level = np.mean(passband_levels)

    deviations = {}
    max_dev = 0.0
    max_dev_freq = 0.0

    for fc in third_octave_centers:
        if fc > sr / 2:
            continue
        idx = np.argmin(np.abs(freqs - fc))
        measured_db = gains_db[idx]

        # Skip stopband frequencies
        if measured_db < passband_threshold:
            continue

        if target_curve and fc in target_curve:
            target_db = target_curve[fc] + ref_level
        else:
            target_db = ref_level

        dev = abs(measured_db - target_db)
        deviations[fc] = {"measured": measured_db, "target": target_db, "deviation": dev}
        if dev > max_dev:
            max_dev = dev
            max_dev_freq = fc

    passed = max_dev <= tolerance_db
    message = (
        f"Max passband deviation: {max_dev:.1f}dB at {max_dev_freq:.0f}Hz "
        f"(tolerance: {tolerance_db}dB, passband ref: {ref_level:.1f}dB)"
    )

    return VerificationResult(
        "Target Deviation", passed, message, {"deviations": deviations}
    )


def verify_minimum_phase(filter_path):
    """
    Verify that the filter is approximately minimum-phase.

    A minimum-phase filter concentrates its energy at the start of the
    impulse response. We verify this by checking that most of the energy
    (>90%) is in the first half of the filter. This is more robust than
    group delay checking, which is numerically unstable for filters with
    deep stopband nulls.

    Minimum-phase is required for transient fidelity — the entire design
    rationale for this project's FIR approach.

    Parameters
    ----------
    filter_path : str
        Path to the filter WAV file.

    Returns
    -------
    VerificationResult
    """
    data, sr = load_filter(filter_path)
    n = len(data)

    # Energy concentration check: most energy should be in the first half
    total_energy = np.sum(data ** 2)
    if total_energy < 1e-20:
        return VerificationResult(
            "Minimum Phase", False, "Filter has near-zero energy", {}
        )

    first_half_energy = np.sum(data[:n // 2] ** 2)
    energy_ratio = first_half_energy / total_energy

    # Also check that peak is near the start (within first 10% of filter)
    peak_idx = np.argmax(np.abs(data))
    peak_fraction = peak_idx / n

    # Minimum-phase: >90% energy in first half, peak in first 10%
    passed = energy_ratio > 0.90 and peak_fraction < 0.10
    message = (
        f"Energy in first half: {energy_ratio*100:.1f}%, "
        f"peak at sample {peak_idx} ({peak_fraction*100:.1f}% of length)"
    )

    return VerificationResult(
        "Minimum Phase",
        passed,
        message,
        {"energy_ratio": energy_ratio, "peak_index": peak_idx, "peak_fraction": peak_fraction},
    )


import scipy.signal


def verify_format(filter_path, expected_taps=16384, expected_sr=SAMPLE_RATE):
    """
    Verify tap count, sample rate, and WAV format.

    CamillaDSP expects specific filter dimensions. This check ensures the
    exported file matches the expected format.

    Parameters
    ----------
    filter_path : str
        Path to the filter WAV file.
    expected_taps : int
        Expected number of filter taps.
    expected_sr : int
        Expected sample rate.

    Returns
    -------
    VerificationResult
    """
    info = sf.info(filter_path)
    data, sr = load_filter(filter_path)

    issues = []
    if sr != expected_sr:
        issues.append(f"Sample rate {sr} != expected {expected_sr}")
    if len(data) != expected_taps:
        issues.append(f"Tap count {len(data)} != expected {expected_taps}")

    passed = len(issues) == 0
    message = "Format OK" if passed else "; ".join(issues)

    return VerificationResult(
        "Format",
        passed,
        message,
        {"taps": len(data), "sr": sr, "format": info.format, "subtype": info.subtype},
    )


def verify_mandatory_hpf(filter_path, mandatory_hpf_hz, min_attenuation_db=18.0):
    """
    Verify that a filter provides adequate subsonic protection.

    Checks that the magnitude response at half the mandatory HPF frequency
    is at least min_attenuation_db below the passband level. This ensures
    the subsonic protection filter is actually present and effective in the
    combined FIR.

    Parameters
    ----------
    filter_path : str
        Path to the filter WAV file.
    mandatory_hpf_hz : float
        The mandatory highpass frequency declared in the speaker identity.
    min_attenuation_db : float
        Minimum required attenuation at (mandatory_hpf_hz / 2) relative
        to passband. Default 18dB.

    Returns
    -------
    VerificationResult
    """
    data, sr = load_filter(filter_path)
    freqs, magnitudes = dsp_utils.rfft_magnitude(data)
    gains_db = dsp_utils.linear_to_db(magnitudes)

    # Check frequency: half the mandatory HPF
    check_freq = mandatory_hpf_hz / 2.0
    idx_check = np.argmin(np.abs(freqs - check_freq))
    gain_at_check = gains_db[idx_check]

    # Passband reference: average gain between 2x HPF and min(10x HPF, 20kHz)
    passband_low = mandatory_hpf_hz * 2.0
    passband_high = min(mandatory_hpf_hz * 10.0, 20000.0)
    passband_mask = (freqs >= passband_low) & (freqs <= passband_high)

    if not np.any(passband_mask):
        return VerificationResult(
            "Mandatory HPF", False,
            f"No passband bins between {passband_low}Hz and {passband_high}Hz",
            {},
        )

    passband_level = float(np.mean(gains_db[passband_mask]))
    attenuation = passband_level - gain_at_check

    passed = attenuation >= min_attenuation_db
    message = (
        f"Attenuation at {check_freq:.0f}Hz: {attenuation:.1f}dB "
        f"(passband ref: {passband_level:.1f}dB, "
        f"required: >= {min_attenuation_db}dB)"
    )

    return VerificationResult(
        "Mandatory HPF",
        passed,
        message,
        {
            "check_freq_hz": check_freq,
            "attenuation_db": attenuation,
            "passband_level_db": passband_level,
            "gain_at_check_db": gain_at_check,
        },
    )


def verify_crossover_sum(hp_path, lp_path, crossover_freq=80.0, tolerance_db=6.0):
    """
    Verify that HP + LP filters have reasonable energy in the crossover region.

    Note: since the combined filters include per-channel room correction
    (which differs between mains and subs due to different room interaction),
    a perfect flat sum is not expected. This check verifies that the crossover
    region does not have a catastrophic gap or excessive overlap.

    The tolerance is relaxed compared to a pure crossover test because the
    room correction component legitimately alters the magnitude in each band.

    Parameters
    ----------
    hp_path : str
        Path to the highpass (main) combined filter WAV.
    lp_path : str
        Path to the lowpass (sub) combined filter WAV.
    crossover_freq : float
        Crossover frequency in Hz.
    tolerance_db : float
        Maximum allowed deviation from the reference level.

    Returns
    -------
    VerificationResult
    """
    hp_data, hp_sr = load_filter(hp_path)
    lp_data, lp_sr = load_filter(lp_path)

    # Pad to same length
    max_len = max(len(hp_data), len(lp_data))
    n_fft = dsp_utils.next_power_of_2(max_len)

    hp_spec = np.fft.rfft(hp_data, n=n_fft)
    lp_spec = np.fft.rfft(lp_data, n=n_fft)
    sum_spec = hp_spec + lp_spec

    freqs = np.fft.rfftfreq(n_fft, d=1.0 / hp_sr)
    sum_mag_db = dsp_utils.linear_to_db(np.abs(sum_spec))

    # Reference level: average in a broad passband (200Hz-4kHz) where both
    # filters should contribute or the HP dominates cleanly
    ref_band = (freqs >= 200) & (freqs <= 4000)
    if np.any(ref_band):
        ref_level = np.mean(sum_mag_db[ref_band])
    else:
        ref_level = 0.0

    # Check at crossover frequency
    xo_idx = np.argmin(np.abs(freqs - crossover_freq))
    xo_level = sum_mag_db[xo_idx]
    xo_deviation = abs(xo_level - ref_level)

    # Check in a tight band around crossover (0.85 to 1.2x crossover freq).
    # With steep FIR slopes (48dB/oct+), even a small frequency offset from
    # the crossover point produces large attenuation in one filter, so we
    # keep the check band narrow.
    band = (freqs >= crossover_freq * 0.85) & (freqs <= crossover_freq * 1.2)
    if np.any(band):
        band_levels = sum_mag_db[band]
        max_band_dev = float(np.max(np.abs(band_levels - ref_level)))
    else:
        max_band_dev = xo_deviation

    passed = max_band_dev <= tolerance_db
    message = (
        f"Crossover sum at {crossover_freq}Hz: {xo_level:.1f}dB "
        f"(ref: {ref_level:.1f}dB, deviation: {xo_deviation:.1f}dB, "
        f"max band dev: {max_band_dev:.1f}dB, tolerance: {tolerance_db}dB)"
    )

    return VerificationResult(
        "Crossover Sum",
        passed,
        message,
        {"xo_deviation_db": xo_deviation, "max_band_deviation_db": max_band_dev,
         "ref_level_db": ref_level},
    )


def run_all_checks(output_dir, crossover_freq=80.0):
    """
    Run all verification checks on generated filters in output_dir.

    Expects the standard output files:
    - combined_left_hp.wav
    - combined_right_hp.wav
    - combined_sub1_lp.wav
    - combined_sub2_lp.wav

    Returns
    -------
    tuple of (bool, list of VerificationResult)
        (all_passed, results)
    """
    import os

    results = []
    all_passed = True

    filter_files = {
        "left_hp": os.path.join(output_dir, "combined_left_hp.wav"),
        "right_hp": os.path.join(output_dir, "combined_right_hp.wav"),
        "sub1_lp": os.path.join(output_dir, "combined_sub1_lp.wav"),
        "sub2_lp": os.path.join(output_dir, "combined_sub2_lp.wav"),
    }

    for name, path in filter_files.items():
        if not os.path.exists(path):
            result = VerificationResult(
                f"File Exists ({name})", False, f"Missing: {path}"
            )
            results.append(result)
            all_passed = False
            continue

        # D-009 check (HARD FAIL)
        result = verify_d009(path)
        results.append(result)
        if not result.passed:
            all_passed = False

        # Format check
        result = verify_format(path)
        results.append(result)
        if not result.passed:
            all_passed = False

        # Minimum phase check
        result = verify_minimum_phase(path)
        results.append(result)
        if not result.passed:
            all_passed = False

        # Target deviation check
        result = verify_target_deviation(path)
        results.append(result)
        if not result.passed:
            all_passed = False

    # Crossover sum checks
    for hp_name, lp_name, side in [
        ("left_hp", "sub1_lp", "left+sub1"),
        ("right_hp", "sub2_lp", "right+sub2"),
    ]:
        hp_path = filter_files[hp_name]
        lp_path = filter_files[lp_name]
        if os.path.exists(hp_path) and os.path.exists(lp_path):
            result = verify_crossover_sum(hp_path, lp_path, crossover_freq)
            result.name = f"Crossover Sum ({side})"
            results.append(result)
            if not result.passed:
                all_passed = False

    return all_passed, results


def print_report(all_passed, results):
    """Print a human-readable verification report."""
    print("\n" + "=" * 60)
    print("FILTER VERIFICATION REPORT")
    print("=" * 60)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.message}")

    print("-" * 60)
    if all_passed:
        print("RESULT: ALL CHECKS PASSED - filters safe to deploy")
    else:
        print("RESULT: CHECKS FAILED - DO NOT DEPLOY")
    print("=" * 60 + "\n")


# -- Venue checks (US-174b) -------------------------------------------------
#
# run_all_checks() above hard-codes the four-channel 80 Hz layout. The
# functions below check whatever WAV set a venue config expects, with the
# AE's 2026-10-25 gates. run_all_checks() is unchanged.

# AE gate ruling v2 (F-262, 91eca61e). The cepstral residual does not
# converge for filters with high-order unit-circle zeros (subsonic HPF,
# steep LP stopbands): correct 48 dB/oct filters score -5 to -37 dB. It is a
# gross-error gate only (linear phase, time reversal, wrap-around, delay all
# score >= +2 dB) until F-408 replaces the metric.
MIN_PHASE_MAX_RESIDUAL_DB = -3.0
# Tail: wrap-around / truncation, not subsonic decay (verify_mandatory_hpf).
MIN_PHASE_MAX_TAIL_DB = -45.0
# Below this the last 5% is float32 noise; the decay comparison is skipped.
MIN_PHASE_TAIL_DECAY_FLOOR_DB = -100.0
VENUE_D009_MARGIN_DB = -0.5


def _window_energy_db(h, start, stop):
    """Energy of h[start:stop] in dB relative to the energy of h."""
    h = np.asarray(h, dtype=np.float64)
    return float(10.0 * np.log10(max(np.sum(h[start:stop] ** 2) / np.sum(h ** 2), 1e-30)))


def verify_minimum_phase_residual(filter_path,
                                  max_residual_db=MIN_PHASE_MAX_RESIDUAL_DB,
                                  max_tail_db=MIN_PHASE_MAX_TAIL_DB,
                                  decay_floor_db=MIN_PHASE_TAIL_DECAY_FLOOR_DB):
    """
    Minimum-phase gate (AE ruling v2, F-262).

    Passes if all hold:
    - the energy of (h - minphase(|H|)) is at most max_residual_db relative
      to the energy of h (gross-error gate, see MIN_PHASE_MAX_RESIDUAL_DB);
    - the energy in the last 5% of taps is at most max_tail_db;
    - the tail is decaying: unless the last 5% is at or below
      decay_floor_db, its energy is at most that of taps 90-95%.
    Unlike verify_minimum_phase(), this does not use "energy before the
    peak": a correct minimum-phase lowpass can have much of its energy
    before its peak.
    """
    from . import closed_loop

    data, _ = load_filter(filter_path)
    if not np.any(data):
        return VerificationResult(
            "Minimum Phase (residual)", False, "Filter is all zeros", {})
    residual_db = closed_loop.minimum_phase_residual_db(data)
    tail_db = closed_loop.tail_energy_db(data)
    n_tail = max(1, int(round(len(data) * 0.05)))
    prev_db = _window_energy_db(data, len(data) - 2 * n_tail, len(data) - n_tail)
    decaying = tail_db <= decay_floor_db or tail_db <= prev_db
    passed = residual_db <= max_residual_db and tail_db <= max_tail_db and decaying
    message = (
        f"Residual vs min-phase: {residual_db:.1f}dB (limit {max_residual_db}dB), "
        f"last 5% energy: {tail_db:.1f}dB (limit {max_tail_db}dB), "
        f"90-95%: {prev_db:.1f}dB ({'decaying' if decaying else 'RISING'}, "
        f"floor {decay_floor_db}dB)"
    )
    return VerificationResult(
        "Minimum Phase (residual)", passed, message,
        {"residual_db": residual_db, "tail_db": tail_db,
         "tail_prev_db": prev_db, "tail_decaying": decaying},
    )


def verify_wav_subtype(filter_path, expected_subtype="FLOAT"):
    """Check the WAV sample format (float32 = soundfile subtype 'FLOAT')."""
    info = sf.info(filter_path)
    passed = info.subtype == expected_subtype
    return VerificationResult(
        "WAV Subtype", passed,
        f"Subtype {info.subtype} (expected {expected_subtype})",
        {"subtype": info.subtype, "channels": info.channels},
    )


def verify_dirac(filter_path):
    """Check that a passthrough file is an exact unit impulse at tap 0."""
    data, _ = load_filter(filter_path)
    passed = len(data) > 0 and data[0] == 1.0 and not np.any(data[1:])
    return VerificationResult(
        "Dirac", passed,
        "Unit impulse at tap 0" if passed else "Not a unit impulse",
        {"first_tap": float(data[0]) if len(data) else None,
         "rest_energy": float(np.sum(data[1:] ** 2)) if len(data) else None},
    )


def run_venue_checks(output_dir, expected_files, mandatory_hpf_hz=None,
                     expected_taps=16384, expected_sr=SAMPLE_RATE):
    """
    Check the WAV set a venue config expects.

    Parameters
    ----------
    output_dir : str
        Directory holding the exported WAVs.
    expected_files : dict
        Filename -> kind. kind 'fir': a speaker channel's combined FIR
        (D-009, format, float32, minimum-phase residual). kind 'dirac':
        a passthrough file (format, float32, exact unit impulse).
    mandatory_hpf_hz : dict, optional
        Filename -> mandatory HPF frequency (from the speaker identity);
        adds verify_mandatory_hpf() for those files.

    Returns
    -------
    tuple of (bool, list of VerificationResult)
    """
    import os

    mandatory_hpf_hz = mandatory_hpf_hz or {}
    results = []
    for filename, kind in sorted(expected_files.items()):
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            results.append(VerificationResult(
                f"File Exists ({filename})", False, f"Missing: {path}"))
            continue

        checks = [
            verify_format(path, expected_taps=expected_taps, expected_sr=expected_sr),
            verify_wav_subtype(path),
        ]
        if kind == "dirac":
            checks.append(verify_dirac(path))
        elif kind == "fir":
            checks.append(verify_d009(path, margin_db=VENUE_D009_MARGIN_DB))
            checks.append(verify_minimum_phase_residual(path))
            if filename in mandatory_hpf_hz:
                checks.append(verify_mandatory_hpf(path, mandatory_hpf_hz[filename]))
        else:
            raise ValueError(f"unknown kind {kind!r} for {filename}")

        for result in checks:
            result.name = f"{result.name} ({filename})"
            if result.name.startswith("Minimum Phase"):
                log.info("%s: %s", result.name, result.message)
            results.append(result)

    all_passed = bool(results) and all(r.passed for r in results)
    return all_passed, results


# -- Shared correction gate (F-262 S6) --------------------------------------
#
# One gate for every product path (venue pipeline, web-UI filter routes,
# measurement session): run_venue_checks() plus a closed-loop check of
# each correction on the measured IR it was built from.

# The AE's per-driver-role residual bands (US-174b, test_venue_closed_loop).
# The sat band stays clear of a crossover up to 200 Hz and below the region
# where the frequency-dependent window lets reflections through uncorrected.
CLOSED_LOOP_BANDS_HZ = {"highpass": (250.0, 500.0), "lowpass": (30.0, 200.0)}
# AE, F-262 item 1: logged per channel so an HF regression is visible, never
# gated. On the unwindowed IR this band is dominated by reflections the
# frequency-dependent window leaves uncorrected on purpose.
CLOSED_LOOP_LOG_BAND_HZ = (500.0, 4000.0)


def closed_loop_band(speaker):
    """Closed-loop band for a profile speaker dict (by its filter_type)."""
    filter_type = speaker.get("filter_type", "highpass")
    if filter_type not in CLOSED_LOOP_BANDS_HZ:
        raise ValueError(f"no closed-loop band for filter_type {filter_type!r}")
    return CLOSED_LOOP_BANDS_HZ[filter_type]


def verify_closed_loop(measured_ir, correction, band_hz, target_curve="flat",
                       target_phon=None, reference_phon=80.0, sr=SAMPLE_RATE):
    """
    Closed-loop check on the measured IR (AE, F-262 S6).

    Over band_hz, relative to the correction's reference level (1/6
    octave): the corrected max positive deviation from the target must
    not exceed the uncorrected one, and the corrected response must pass
    closed_loop.passes_residual_gate. This catches a filter that applies
    the room instead of correcting it. The same deviations over
    CLOSED_LOOP_LOG_BAND_HZ are logged and returned, but never gate.

    Parameters
    ----------
    measured_ir : np.ndarray
        The IR the correction was built from.
    correction : correction.CorrectionFilter
    band_hz : tuple of (float, float)
        Evaluation band, see closed_loop_band().
    """
    from . import closed_loop
    from . import target_curves as tc

    name = "Closed Loop"
    ir = np.asarray(measured_ir, dtype=np.float64)
    fir = np.asarray(correction.fir, dtype=np.float64)
    if ir.ndim != 1 or not ir.size or not np.all(np.isfinite(ir)) \
            or not np.all(np.isfinite(fir)):
        return VerificationResult(name, False, "Measured IR or FIR is empty or non-finite")

    level = correction.reference_level_db
    system = closed_loop.system_response(ir, fir)

    def responses(lo, hi):
        freqs, uncorrected = closed_loop.smoothed_response_db(ir, lo, hi, sr=sr)
        _, corrected = closed_loop.smoothed_response_db(system, lo, hi, sr=sr)
        target = tc.get_target_curve(
            target_curve, freqs, target_phon=target_phon, reference_phon=reference_phon)
        return corrected - level, uncorrected - level, target

    lo, hi = band_hz
    corrected, uncorrected, target = responses(lo, hi)
    if not all(np.all(np.isfinite(a)) for a in (corrected, uncorrected, target)):
        return VerificationResult(name, False, "Non-finite closed-loop response")
    dev_corrected = closed_loop.max_positive_deviation_db(corrected, target)
    dev_uncorrected = closed_loop.max_positive_deviation_db(uncorrected, target)
    passed = (closed_loop.passes_residual_gate(corrected, target)
              and dev_corrected <= dev_uncorrected)

    log_lo, log_hi = CLOSED_LOOP_LOG_BAND_HZ
    log_corrected, log_uncorrected, log_target = responses(log_lo, log_hi)
    if all(np.all(np.isfinite(a)) for a in (log_corrected, log_uncorrected, log_target)):
        log_dev_corrected = closed_loop.max_positive_deviation_db(log_corrected, log_target)
        log_dev_uncorrected = closed_loop.max_positive_deviation_db(log_uncorrected, log_target)
    else:
        log_dev_corrected = log_dev_uncorrected = float("nan")

    message = (
        f"Max over target {lo:g}-{hi:g} Hz: corrected {dev_corrected:+.2f}dB, "
        f"uncorrected {dev_uncorrected:+.2f}dB "
        f"(limit {closed_loop.MAX_POSITIVE_DEVIATION_DB}dB, corrected <= uncorrected); "
        f"log only {log_lo:g}-{log_hi:g} Hz: corrected {log_dev_corrected:+.2f}dB, "
        f"uncorrected {log_dev_uncorrected:+.2f}dB"
    )
    return VerificationResult(
        name, passed, message,
        {"corrected_max_db": dev_corrected, "uncorrected_max_db": dev_uncorrected,
         "band_hz": (float(lo), float(hi)),
         "log_corrected_max_db": log_dev_corrected,
         "log_uncorrected_max_db": log_dev_uncorrected,
         "log_band_hz": (float(log_lo), float(log_hi))},
    )


def run_correction_gate(output_dir, expected_files, closed_loop_inputs=None,
                        mandatory_hpf_hz=None, expected_taps=16384,
                        expected_sr=SAMPLE_RATE, target_curve="flat",
                        target_phon=None, reference_phon=80.0):
    """
    The shared gate (F-262 S6): run_venue_checks() plus verify_closed_loop().

    Parameters
    ----------
    closed_loop_inputs : dict, optional
        Filename -> (measured IR, CorrectionFilter, profile speaker dict)
        for every 'fir' file that carries a room correction. Files without one (crossover-only)
        get the run_venue_checks() set only.

    Returns
    -------
    tuple of (bool, list of VerificationResult)
    """
    closed_loop_inputs = closed_loop_inputs or {}
    unknown = sorted(f for f in closed_loop_inputs if expected_files.get(f) != "fir")
    if unknown:
        raise ValueError(f"closed-loop inputs for files that are not 'fir': {unknown}")

    _, results = run_venue_checks(
        output_dir, expected_files, mandatory_hpf_hz=mandatory_hpf_hz,
        expected_taps=expected_taps, expected_sr=expected_sr)
    for filename, (measured_ir, correction, speaker) in sorted(closed_loop_inputs.items()):
        result = verify_closed_loop(
            measured_ir, correction, closed_loop_band(speaker), target_curve=target_curve,
            target_phon=target_phon, reference_phon=reference_phon, sr=expected_sr)
        result.name = f"{result.name} ({filename})"
        log.info("%s: %s", result.name, result.message)
        results.append(result)

    all_passed = bool(results) and all(r.passed for r in results)
    return all_passed, results


def mandatory_hpf_by_file(profile, identities, filenames):
    """Filename -> mandatory HPF (Hz), for speakers whose identity has one.

    filenames maps profile speaker key -> exported filename.
    """
    result = {}
    for spk_key, filename in filenames.items():
        identity = identities.get(profile["speakers"][spk_key].get("identity", ""), {})
        hpf = identity.get("mandatory_hpf_hz")
        if hpf is not None:
            result[filename] = float(hpf)
    return result


def gate_summary(filename, results):
    """Per-file pass flags from run_correction_gate() results (for UI payloads)."""
    mine = [r for r in results if r.name.endswith(f"({filename})")]

    def passed(prefix, default=True):
        found = [r.passed for r in mine if r.name.startswith(prefix)]
        return all(found) if found else default

    d009 = [r for r in mine if r.name.startswith("D-009")]
    residual = [r for r in mine if r.name.startswith("Minimum Phase")
                and "residual_db" in r.details]
    return {
        "d009_pass": passed("D-009", default=False),
        "d009_peak_db": float(round(d009[0].details.get("max_gain_db", 0.0), 2))
        if d009 else None,
        "min_phase_pass": passed("Minimum Phase", default=False),
        "min_phase_residual_db": float(round(residual[0].details["residual_db"], 1))
        if residual else None,
        "format_pass": passed("Format", default=False) and passed("WAV Subtype", default=False),
        "hpf_pass": passed("Mandatory HPF"),
        "closed_loop_pass": passed("Closed Loop"),
        "all_pass": bool(mine) and all(r.passed for r in mine),
    }
