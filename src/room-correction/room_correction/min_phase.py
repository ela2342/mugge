"""
Minimum-phase checks for correction inputs, designed factors and combined
FIRs (F-383 A2).

minimum_phase_residual_db() compares an FIR with the minimum-phase FIR of a
reference magnitude: its own |H| by default, or a design magnitude. Its FFT
grid is fixed here, never taken from the generator under test, so a
generator's own grid cannot make it pass by construction. For a design
reference the floor is the generator's own design-floor constant (F-383 R6d
A4): a reference below the floor the generator can realise is float noise.

check_design_residual() is the fail-closed check each crossover generator
runs on its output against its own design magnitude (F-383 A1b), for
filters of at least A1B_MIN_TAPS taps (F-383 Q4).

This is not the deployed venue gate. closed_loop.minimum_phase_residual_db()
and verify.verify_minimum_phase_residual() keep their own settings.
"""

import logging

import numpy as np

from . import dsp_utils

log = logging.getLogger(__name__)


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
TAIL_FRACTION = 0.05
# A design magnitude is scaled to h's passband: the bins in 20 Hz-20 kHz
# within 1 dB of the design's maximum there.
PASSBAND_BAND_HZ = (20.0, 20000.0)
PASSBAND_WITHIN_DB = 1.0
# A1b: a generated factor must match the minimum-phase FIR of its design
# magnitude to this residual, on a grid of this oversample.
DESIGN_RESIDUAL_LIMIT_DB = -40.0
DESIGN_RESIDUAL_OVERSAMPLE = 16
# A1b is calibrated at the production length (F-383 Q4). Below it the design
# IR outlasts n and the fade dominates the residual, so A1b does not apply.
A1B_MIN_TAPS = 16384


class MinimumPhaseError(ValueError):
    """A generated FIR is not the minimum-phase FIR of its design (F-383 A1b)."""


def _as_fir(h):
    h = np.asarray(h, dtype=np.float64)
    if h.ndim != 1 or h.size == 0:
        raise ValueError(f"FIR must be a non-empty 1-D array, got shape {h.shape}")
    if not np.all(np.isfinite(h)):
        raise ValueError("FIR has non-finite samples")
    if not np.any(h):
        raise ValueError("FIR is silent")
    return h


def _cepstral_minimum_phase(mag, n_fft, n):
    """Minimum-phase FIR (n taps) of a positive rfft magnitude on an n_fft grid."""
    log_mag = np.log(mag)
    cepstrum = np.fft.ifft(np.concatenate([log_mag, log_mag[-2:0:-1]])).real
    causal_window = np.zeros(n_fft)
    causal_window[0] = 1.0
    causal_window[1:n_fft // 2] = 2.0
    causal_window[n_fft // 2] = 1.0
    return np.fft.ifft(np.exp(np.fft.fft(cepstrum * causal_window))).real[:n]


def _scaled_design(design_mag, freqs, h_mag):
    design = np.asarray(design_mag(freqs), dtype=np.float64)
    if design.shape != freqs.shape:
        raise ValueError(f"design_mag returned shape {design.shape}, expected {freqs.shape}")
    if not np.all(np.isfinite(design)) or np.any(design < 0):
        raise ValueError("design_mag must be finite and non-negative")
    lo, hi = PASSBAND_BAND_HZ
    band = (freqs >= lo) & (freqs <= hi)
    if not np.any(design[band] > 0):
        raise ValueError("design_mag has no passband in 20 Hz-20 kHz")
    passband = band & (design >= np.max(design[band]) * dsp_utils.db_to_linear(-PASSBAND_WITHIN_DB))
    return design * float(np.median(h_mag[passband] / design[passband]))


def minimum_phase_residual_db(h, design_mag=None, oversample=4, floor_rel=1e-20,
                              sr=SAMPLE_RATE):
    """
    Residual of h against a minimum-phase reference, dB re energy(h).

    Parameters
    ----------
    h : np.ndarray
        FIR under test.
    design_mag : callable or None
        freqs (Hz) -> linear magnitude, evaluated on this function's own
        grid and scaled to h's passband by the median of |H|/design. None
        uses |rfft(h)| itself.
    oversample : int
        FFT grid n_fft = next_power_of_2(oversample * len(h)).
    floor_rel : float
        Magnitude floor relative to the reference's maximum, so a gain on h
        never changes the result.
    sr : int
        Sample rate.

    Returns
    -------
    float
        10*log10(energy(h - ref) / energy(h)), with ref the minimum-phase FIR
        of the reference magnitude truncated to len(h). The lower of the
        values against +ref and -ref is returned, so a polarity-inverted
        filter scores the same as the original.
    """
    h = _as_fir(h)
    if int(oversample) < 1:
        raise ValueError(f"oversample must be >= 1, got {oversample!r}")
    n_fft = dsp_utils.next_power_of_2(max(2, int(oversample) * len(h)))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    h_mag = np.abs(np.fft.rfft(h, n=n_fft))
    mag = h_mag if design_mag is None else _scaled_design(design_mag, freqs, h_mag)
    ref = _cepstral_minimum_phase(np.maximum(mag, floor_rel * np.max(mag)), n_fft, len(h))
    error = min(np.sum((h - ref) ** 2), np.sum((h + ref) ** 2))
    return float(10.0 * np.log10(max(error / np.sum(h ** 2), 1e-300)))


def tail_peak_db(h, fraction=TAIL_FRACTION):
    """Largest |h| in the last `fraction` of the taps, dB re max|h| (amplitude)."""
    h = _as_fir(h)
    n_tail = max(1, int(round(len(h) * fraction)))
    tail = np.max(np.abs(h[-n_tail:]))
    return float(20.0 * np.log10(max(tail / np.max(np.abs(h)), 1e-300)))


def check_design_residual(h, design_mag, floor_rel, what, sr=SAMPLE_RATE):
    """
    Raise MinimumPhaseError unless h matches its design's minimum-phase FIR.

    The residual is minimum_phase_residual_db() against *design_mag* on the
    DESIGN_RESIDUAL_OVERSAMPLE grid, with *floor_rel* the generator's own
    design-floor constant. *what* names the filter in the error. A filter
    shorter than A1B_MIN_TAPS is not checked.

    Returns
    -------
    float or None
        The residual in dB, when it is <= DESIGN_RESIDUAL_LIMIT_DB; None
        when the check was skipped.
    """
    if len(h) < A1B_MIN_TAPS:
        log.info("%s: A1b skipped, %d taps < A1B_MIN_TAPS %d", what, len(h), A1B_MIN_TAPS)
        return None
    residual = minimum_phase_residual_db(
        h, design_mag=design_mag, oversample=DESIGN_RESIDUAL_OVERSAMPLE,
        floor_rel=floor_rel, sr=sr)
    if not residual <= DESIGN_RESIDUAL_LIMIT_DB:
        raise MinimumPhaseError(
            f"{what}: residual vs the minimum-phase FIR of its design is "
            f"{residual:.1f} dB, above the {DESIGN_RESIDUAL_LIMIT_DB:.0f} dB limit"
        )
    return residual
