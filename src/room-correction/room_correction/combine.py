"""
Combine correction and crossover filters into a single FIR.

The combined filter performs both room correction and frequency splitting
in a single convolution operation. This is more CPU-efficient than running
two separate convolutions in CamillaDSP, and ensures perfect phase
alignment between the correction and crossover components.

Process (F-383 step 4):
1. Check that the correction input is minimum phase (A1a, fail-closed)
2. Convolve correction, crossover and optional subsonic exactly
3. Truncate to target length with fade-out window
4. One cut-only D-009 scalar on the result (B1)
5. Log the output tail, residual, scalar and peak (A1c, B2)

There is no magnitude clip and no re-synthesis: the product of minimum-phase
factors is minimum phase, and a single gain keeps it so.
"""

import logging

import numpy as np

from . import dsp_utils, min_phase

log = logging.getLogger(__name__)


SAMPLE_RATE = dsp_utils.SAMPLE_RATE


def combine_filters(correction_filter, crossover_filter, n_taps=16384, margin_db=-0.5,
                    subsonic_filter=None):
    """
    Combine a correction filter and crossover filter into one FIR.

    The correction must be minimum phase (A1a). The factors are convolved
    exactly (frequency-domain multiplication on a grid long enough for the
    full linear convolution), truncated to n_taps with a fade-out, and
    scaled once by s_dB = min(0, margin_db - peak), the peak read over the
    full band on an 8x grid (B1, F-383 R3). The scalar only cuts, so a
    product already at or below margin_db is returned as truncated.

    An optional subsonic protection filter can be convolved in as well.
    This is used for ported subwoofers to prevent excursion damage below
    the port tuning frequency. If not provided, behavior is unchanged
    (backward compatible).

    Parameters
    ----------
    correction_filter : np.ndarray
        Room correction FIR filter (minimum phase).
    crossover_filter : np.ndarray
        Crossover FIR filter (highpass or lowpass).
    n_taps : int
        Target output length.
    margin_db : float
        D-009 safety margin.
    subsonic_filter : np.ndarray, optional
        Subsonic protection highpass FIR filter for ported subs.
        If None, no subsonic protection is applied.

    Returns
    -------
    np.ndarray
        Combined minimum-phase FIR filter.

    Raises
    ------
    min_phase.MinimumPhaseError
        A1a: the correction's residual against its own minimum-phase FIR is
        above INPUT_RESIDUAL_LIMIT_DB, or its tail peak is above
        TAIL_LIMIT_DB. The output tail (A1c) is only logged in step 4.
    """
    correction_filter = np.asarray(correction_filter, dtype=np.float64)
    crossover_filter = np.asarray(crossover_filter, dtype=np.float64)
    check_correction_input(correction_filter)

    factors = [correction_filter, crossover_filter]
    if subsonic_filter is not None:
        factors.append(np.asarray(subsonic_filter, dtype=np.float64))

    # The linear convolution of k factors has sum(len) - (k - 1) samples; an
    # rfft grid of at least that size multiplies without wrap-around (F2).
    n_fft = dsp_utils.next_power_of_2(sum(len(f) for f in factors))
    spectrum = np.fft.rfft(factors[0], n=n_fft)
    for factor in factors[1:]:
        spectrum *= np.fft.rfft(factor, n=n_fft)
    product = np.fft.irfft(spectrum, n=n_fft)

    # Truncate with fade-out
    combined_ir = np.zeros(n_taps)
    n = min(n_taps, n_fft)
    combined_ir[:n] = product[:n]
    combined_ir *= dsp_utils.fade_window(n_taps, 0, n_taps // 20)

    combined_ir, scalar_db = d009_scale(combined_ir, margin_db, what="combined filter")

    tail_db, residual_db = output_min_phase_db(combined_ir)
    peak_db = max_gain_db(combined_ir, oversample=D009_SCALAR_OVERSAMPLE, band=None)
    log.info("combined filter: tail %.1f dB (A1c, log only), residual %.1f dB, "
             "scalar %.4f dB, peak %.4f dB", tail_db, residual_db, scalar_db, peak_db)
    if peak_db < margin_db - 0.1:
        log.warning("combined filter: peak %.4f dB is more than 0.1 dB below the "
                    "margin %.2f dB (B2)", peak_db, margin_db)
    return combined_ir


def check_correction_input(correction_filter):
    """
    A1a (F-383): raise MinimumPhaseError unless the correction is minimum
    phase (residual against its own minimum-phase FIR at or below
    INPUT_RESIDUAL_LIMIT_DB) and has decayed (tail peak at or below
    TAIL_LIMIT_DB). The message names each failed condition.
    """
    residual_db = min_phase.minimum_phase_residual_db(correction_filter)
    tail_db = min_phase.tail_peak_db(correction_filter)
    failed = []
    if not residual_db <= min_phase.INPUT_RESIDUAL_LIMIT_DB:
        failed.append(f"residual vs its minimum-phase FIR {residual_db:.1f} dB "
                      f"(limit {min_phase.INPUT_RESIDUAL_LIMIT_DB:.0f} dB)")
    if not tail_db <= min_phase.TAIL_LIMIT_DB:
        failed.append(f"tail peak {tail_db:.1f} dB "
                      f"(limit {min_phase.TAIL_LIMIT_DB:.0f} dB)")
    if failed:
        raise min_phase.MinimumPhaseError(
            "correction input is not minimum phase (A1a): " + ", ".join(failed))


def output_min_phase_db(fir):
    """
    A1c numbers of a combined FIR (F-383): (tail peak in dB re max|h|,
    residual against its own minimum-phase FIR in dB). Step 4 logs them;
    step 5 gates on this same function.
    """
    return min_phase.tail_peak_db(fir), min_phase.minimum_phase_residual_db(fir)


def d009_scale(fir, margin_db, sr=SAMPLE_RATE, what="filter"):
    """
    One cut-only D-009 gain on a finished FIR (F-384 step 9, F-383 B1).

    The peak is read over the full band, 0 Hz to Nyquist, on the
    D009_SCALAR_OVERSAMPLE grid: a sub-20 Hz overshoot plays too (F-384 q2).
    A single scalar keeps the shape, and so the minimum phase, exactly; it
    never boosts (D-009 is a ceiling). An FIR already at or below margin_db
    is returned unchanged. *what* names the filter in the error. Returns
    (fir, scalar in dB).
    """
    peak_db = max_gain_db(fir, sr=sr, oversample=D009_SCALAR_OVERSAMPLE, band=None)
    if not np.isfinite(peak_db):
        raise ValueError(f"{what} has a non-finite peak gain")
    if peak_db <= margin_db:
        return fir, 0.0
    scalar_db = float(margin_db - peak_db)
    return fir * dsp_utils.db_to_linear(scalar_db), scalar_db


# AE, F-262 S5: the venue D-009 limit every combined speaker FIR must meet.
D009_TRIM_MARGIN_DB = -0.5
D009_TRIM_OVERSAMPLE = 4
# F-383/F-384 B3: the D-009 scalar measures the peak on an 8x grid (2^17
# points at 16384 taps), full band. 4x under-reads the inter-bin peak by up to 0.045 dB.
D009_SCALAR_OVERSAMPLE = 8


def max_gain_db(fir, sr=SAMPLE_RATE, oversample=D009_TRIM_OVERSAMPLE, *,
                band=(20.0, 20000.0)):
    """
    Peak magnitude (dB) of an FIR over `band` (Hz, inclusive), oversampled
    in frequency. band=None reads every bin from 0 Hz to Nyquist.
    """
    fir = np.asarray(fir, dtype=np.float64)
    n_fft = dsp_utils.next_power_of_2(len(fir)) * oversample
    mag = np.abs(np.fft.rfft(fir, n=n_fft))
    if band is not None:
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
        mag = mag[(freqs >= band[0]) & (freqs <= band[1])]
    return float(dsp_utils.linear_to_db(np.max(mag)))


def uniform_d009_trim(filters, margin_db=D009_TRIM_MARGIN_DB, sr=SAMPLE_RATE):
    """
    D-009 trim after combine (AE, F-262 S5).

    If any speaker FIR peaks above margin_db, scale ALL of them by one
    gain so the loudest peaks at margin_db. A uniform scale keeps the
    channel balance and the minimum phase; a per-channel re-clip would
    bend the shape. Pass speaker channels only, never dirac passthroughs.

    Returns
    -------
    tuple of (dict, float)
        (trimmed filters, trim in dB: 0.0 or negative).
    """
    if not filters:
        return dict(filters), 0.0
    peak_db = max(max_gain_db(fir, sr=sr) for fir in filters.values())
    if not np.isfinite(peak_db):
        raise ValueError("combined filter has a non-finite peak gain")
    if peak_db <= margin_db:
        return dict(filters), 0.0
    trim_db = margin_db - peak_db
    scale = dsp_utils.db_to_linear(trim_db)
    return {k: np.asarray(fir, dtype=np.float64) * scale
            for k, fir in filters.items()}, float(trim_db)
