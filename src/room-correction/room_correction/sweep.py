"""
Logarithmic sine sweep generation for room measurement.

Generates a log sweep from 20Hz to 20kHz at 48kHz sample rate. The log sweep
has the property that its energy is distributed proportionally to 1/f,
matching how we perceive frequency -- each octave gets equal energy.
Deconvolution is handled separately via Wiener deconvolution in the
deconvolution module.

The sweep includes Hann fade-in/fade-out to avoid transients that would
excite all frequencies simultaneously and contaminate the measurement.
"""

import numpy as np
import soundfile as sf

from . import dsp_utils


SAMPLE_RATE = dsp_utils.SAMPLE_RATE


def generate_log_sweep(duration=5.0, f_start=20.0, f_end=20000.0, sr=SAMPLE_RATE):
    """
    Generate a logarithmic sine sweep.

    The instantaneous frequency increases exponentially from f_start to f_end
    over the given duration. This ensures equal energy per octave, which
    matches psychoacoustic frequency perception and produces a clean impulse
    response after deconvolution.

    Parameters
    ----------
    duration : float
        Sweep duration in seconds (5-10s recommended for good SNR).
    f_start : float
        Start frequency in Hz.
    f_end : float
        End frequency in Hz.
    sr : int
        Sample rate in Hz.

    Returns
    -------
    np.ndarray
        The sweep signal, float64, normalized to peak amplitude 0.9.
    """
    n_samples = int(duration * sr)
    t = np.arange(n_samples, dtype=np.float64) / sr

    # Log sweep: instantaneous frequency = f_start * (f_end/f_start)^(t/T)
    # Phase integral of this gives:
    rate = f_end / f_start
    phase = 2.0 * np.pi * f_start * duration / np.log(rate) * (
        np.power(rate, t / duration) - 1.0
    )
    sweep = np.sin(phase)

    # Apply 50ms Hann fade-in/fade-out to avoid transients
    fade_samples = int(0.05 * sr)
    window = dsp_utils.fade_window(n_samples, fade_samples, fade_samples)
    sweep *= window

    # Normalize to 0.9 peak to leave headroom
    sweep *= 0.9 / np.max(np.abs(sweep))

    return sweep


def signal_gen_sweep(duration, sr=SAMPLE_RATE, level_dbfs=0.0, f_start=20.0,
                     f_end=20000.0):
    """
    Port of the signal-gen sweep law (src/signal-gen/src/generator.rs).

    signal-gen plays this law, not generate_log_sweep(): the phase is the
    running sum of 2*pi*f_inst/sr with f_inst = f_start * exp(rate * n),
    there are no fades, and the level is a peak amplitude.

    Use it ONLY as the reference for the capture onset check
    (alignment.align_capture). Until F-403 S2 lets the session deconvolve
    against the array signal-gen actually played, the IR itself is still
    deconvolved against generate_log_sweep().

    Parameters
    ----------
    duration : float
        Sweep duration in seconds.
    sr : int
        Sample rate in Hz.
    level_dbfs : float
        Peak level in dBFS.
    f_start, f_end : float
        Sweep frequency range in Hz.

    Returns
    -------
    np.ndarray
        The sweep signal, float64.
    """
    total = int(duration * sr)
    rate = np.log(f_end / f_start) / total
    f_inst = f_start * np.exp(rate * np.arange(total, dtype=np.float64))
    phase = np.cumsum(2.0 * np.pi * f_inst / sr)
    return np.sin(phase) * dsp_utils.db_to_linear(level_dbfs)


def save_sweep(sweep, path, sr=SAMPLE_RATE):
    """
    Save a sweep signal to a WAV file.

    Output is mono float32 (CamillaDSP-compatible).

    Parameters
    ----------
    sweep : np.ndarray
        The sweep signal.
    path : str
        Output file path.
    sr : int
        Sample rate.
    """
    sf.write(path, sweep.astype(np.float32), sr, subtype='FLOAT')
