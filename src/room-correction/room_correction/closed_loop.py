"""
Closed-loop evaluation of correction filters (US-174b).

Given an acoustic path IR (speaker * room at the mic) and the FIR that
will run on that channel, compute the corrected system response and
compare it with the target. Used by the simulator closed-loop tests now,
and by the re-measurement check after deploy later (US-174d), so the
metrics live here rather than in a test file.

Metrics (values: AE, 2026-10-25):
- Smoothed response: 1/6-octave, log-domain average (same averaging as
  dsp_utils.fractional_octave_smooth), evaluated on a log frequency grid.
- Max positive deviation from target, one-sided (the cut-only pipeline
  must remove peaks; it is not allowed to fill dips).
- Below-target regions: never raised, over-cut bounded near peaks, only
  the D-009 margin far from peaks (below_target_report, AE ruling).
- Minimum phase: energy of (h - minphase(|H|)) relative to energy of h.
- Causality / wrap-around: energy in the last 5% of taps.

Known limit (Architect, 2026-10-25): the room simulator has a single mic
position and position-independent room modes, so off-position robustness
(AC4) cannot be evaluated yet; that is slice 174b-sim.
"""

import numpy as np

from . import dsp_utils
from . import target_curves as tc


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
EVAL_N_FFT = 1 << 17          # 0.37 Hz bins at 48 kHz, fine enough for Q~10 modes
POINTS_PER_OCTAVE = 48
# Residual gate (AE, 2026-10-25): max positive deviation of the corrected
# response from the target, 1/6 octave, per channel, simulated scenarios.
# US-174d gets its own MEASURED_MAX_POSITIVE_DEVIATION_DB for real
# measurements; this value is not changed by 174d. Changing or loosening it
# needs AE review.
MAX_POSITIVE_DEVIATION_DB = 3.0


def log_grid(f_low, f_high, points_per_octave=POINTS_PER_OCTAVE):
    """Log-spaced frequency grid from f_low to f_high inclusive."""
    n_oct = np.log2(f_high / f_low)
    n = int(np.ceil(n_oct * points_per_octave)) + 1
    return f_low * 2.0 ** (np.linspace(0.0, n_oct, n))


def smoothed_response_db(h, f_low, f_high, sr=SAMPLE_RATE, fraction=6,
                         n_fft=EVAL_N_FFT, points_per_octave=POINTS_PER_OCTAVE):
    """
    Fractional-octave smoothed magnitude of an FIR / IR on a log grid.

    Each grid point is the mean of the log magnitude over bins within
    +/- half of 1/fraction octave, which matches
    dsp_utils.fractional_octave_smooth() at that frequency.

    Returns
    -------
    tuple of (np.ndarray, np.ndarray)
        (grid frequencies in Hz, smoothed magnitude in dB).
    """
    h = np.asarray(h, dtype=np.float64)
    n_fft = max(n_fft, dsp_utils.next_power_of_2(len(h)))
    mag = np.abs(np.fft.rfft(h, n=n_fft))
    log_mag = np.log10(np.maximum(mag, 1e-10))
    bin_hz = sr / n_fft

    grid = log_grid(f_low, f_high, points_per_octave)
    ratio = 2.0 ** (0.5 / fraction)
    lo = np.ceil(grid / ratio / bin_hz).astype(int)
    hi = np.floor(grid * ratio / bin_hz).astype(int)
    lo = np.clip(lo, 1, len(mag) - 1)
    hi = np.clip(np.maximum(hi, lo), 1, len(mag) - 1)

    csum = np.concatenate([[0.0], np.cumsum(log_mag)])
    mean_log = (csum[hi + 1] - csum[lo]) / (hi - lo + 1)
    return grid, 20.0 * mean_log


def crossover_target_db(freqs, filter_type, crossover_freq, slope_db_per_oct):
    """
    Ideal Linkwitz-Riley magnitude in dB (the crossover part of the target).

    LR of order 2N is a squared Butterworth of order N, N = slope / 12:
    lowpass 1 / (1 + x^2N), highpass x^2N / (1 + x^2N), x = f / fc.
    This is the textbook shape (-6 dB at fc), not whatever crossover.py
    produces today (F-374), so it cannot lock in that defect.
    """
    freqs = np.asarray(freqs, dtype=np.float64)
    order = 2.0 * slope_db_per_oct / 12.0
    x = np.maximum(freqs, 1e-6) / float(crossover_freq)
    if filter_type == 'lowpass':
        mag = 1.0 / (1.0 + x ** order)
    elif filter_type == 'highpass':
        mag = x ** order / (1.0 + x ** order)
    elif filter_type == 'fullrange':
        mag = np.ones_like(x)
    else:
        raise ValueError(f"unsupported filter_type {filter_type!r}")
    return dsp_utils.linear_to_db(mag)


def channel_target_db(freqs, filter_type, crossover_freq, slope_db_per_oct,
                      target_curve_name='flat'):
    """Crossover target times the profile's target curve, in dB."""
    curve = tc.get_target_curve(target_curve_name, np.asarray(freqs, dtype=np.float64))
    return crossover_target_db(freqs, filter_type, crossover_freq,
                               slope_db_per_oct) + curve


def system_response(acoustic_ir, fir):
    """Corrected system: the FIR feeding the acoustic path (time domain)."""
    return dsp_utils.convolve_fir(acoustic_ir, fir)


def max_positive_deviation_db(response_db, target_db):
    """
    Largest amount (dB) by which the response exceeds the target.

    Fails closed (AE): non-finite input raises ValueError. A NaN result
    compares False both ways, so a ``dev > limit`` check would let it pass.
    """
    diff = np.asarray(response_db, dtype=float) - np.asarray(target_db, dtype=float)
    if not np.all(np.isfinite(diff)):
        raise ValueError("max_positive_deviation_db: non-finite response or target")
    return float(np.max(diff))


def below_target_report(freqs, corrected_db, uncorrected_db, target_db, margin_db,
                        band=None, far_octaves=1.0 / 3.0):
    """
    Below-target criteria for cut-only correction (AE ruling, 2026-10-25).

    In bins where the uncorrected response is below target:

    - ``raised``: max (corrected - uncorrected). Cut-only must never lift
      a dip (gate: <= +0.05 dB).
    - ``over_cut``: max |corrected - uncorrected + m|, m = |margin_db| the
      D-009 margin the correction applied everywhere. Cut skirts next to
      a peak spill into neighbouring dips (gate: <= 1.0 dB).
    - ``far_field``: the same as over_cut, restricted to bins more than
      far_octaves from any above-target bin, where only the margin may
      act (gate: <= 0.1 dB). Separates skirt spill from a broadband
      over-cut. NaN if there are no such bins (``n_far`` = 0).

    Evaluate on a grid that extends past the band by at least far_octaves,
    so peaks just outside the band count; ``band`` = (f_low, f_high)
    limits which bins are judged. Returns a dict of floats.
    """
    freqs = np.asarray(freqs, dtype=np.float64)
    delta = np.asarray(corrected_db) - np.asarray(uncorrected_db)
    excess = np.asarray(uncorrected_db) - np.asarray(target_db)
    in_band = np.ones(len(freqs), dtype=bool)
    if band is not None:
        in_band = (freqs >= band[0]) & (freqs <= band[1])
    below = in_band & (excess < 0)
    above = excess > 0

    log_f = np.log2(freqs)
    if np.any(above):
        distance = np.min(np.abs(log_f[:, None] - log_f[above][None, :]), axis=1)
    else:
        distance = np.full(len(freqs), np.inf)
    far = below & (distance > far_octaves)

    m = abs(margin_db)
    nan = float("nan")
    return {
        "raised": float(np.max(delta[below])) if np.any(below) else nan,
        "over_cut": float(np.max(np.abs(delta[below] + m))) if np.any(below) else nan,
        "far_field": float(np.max(np.abs(delta[far] + m))) if np.any(far) else nan,
        "n_below": int(np.sum(below)),
        "n_far": int(np.sum(far)),
    }


def minimum_phase_reference(h, oversample=8):
    """Minimum-phase FIR with the same magnitude as h (cepstral method)."""
    h = np.asarray(h, dtype=np.float64)
    n = len(h)
    n_fft = dsp_utils.next_power_of_2(n * oversample)
    mag = np.abs(np.fft.rfft(h, n=n_fft))
    floor = max(np.max(mag), 1e-30) * 1e-12
    log_mag = np.log(np.maximum(mag, floor))
    full = np.concatenate([log_mag, log_mag[-2:0:-1]])
    cepstrum = np.fft.ifft(full).real
    window = np.zeros(n_fft)
    window[0] = 1.0
    window[1:n_fft // 2] = 2.0
    window[n_fft // 2] = 1.0
    return np.fft.ifft(np.exp(np.fft.fft(cepstrum * window))).real[:n]


def minimum_phase_residual_db(h):
    """Energy of (h - minphase(|H|)) in dB relative to the energy of h."""
    h = np.asarray(h, dtype=np.float64)
    energy = np.sum(h ** 2)
    if energy == 0:
        raise ValueError("filter has no energy")
    residual = np.sum((h - minimum_phase_reference(h)) ** 2)
    return float(10.0 * np.log10(max(residual / energy, 1e-30)))


def tail_energy_db(h, tail_fraction=0.05):
    """Energy in the last tail_fraction of taps, dB relative to total."""
    h = np.asarray(h, dtype=np.float64)
    energy = np.sum(h ** 2)
    if energy == 0:
        raise ValueError("filter has no energy")
    n_tail = max(1, int(round(len(h) * tail_fraction)))
    return float(10.0 * np.log10(max(np.sum(h[-n_tail:] ** 2) / energy, 1e-30)))


def summed_response(acoustic_irs, firs, delays_samples=None):
    """
    Sum of several corrected channels at the listening position.

    Parameters
    ----------
    acoustic_irs, firs : dict
        Keyed by channel/speaker; same keys.
    delays_samples : dict, optional
        Integer delay compensation per key (applied to the FIR output).
    """
    delays_samples = delays_samples or {}
    parts = []
    for key, ir in acoustic_irs.items():
        y = system_response(ir, firs[key])
        d = int(delays_samples.get(key, 0))
        if d < 0:
            raise ValueError(f"negative delay for {key}: {d}")
        parts.append(np.concatenate([np.zeros(d), y]))
    n = max(len(p) for p in parts)
    total = np.zeros(n)
    for p in parts:
        total[:len(p)] += p
    return total
