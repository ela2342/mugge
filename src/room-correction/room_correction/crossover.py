"""
Minimum-phase FIR crossover filter generation.

Generates steep crossover slopes as minimum-phase FIR filters. Unlike IIR
crossovers (Linkwitz-Riley), FIR crossovers can achieve arbitrarily steep
slopes without phase distortion problems, and the minimum-phase design
avoids pre-ringing while keeping group delay minimal.

The approach:
1. Design the ideal (brick-wall) magnitude response
2. Window to make it realizable as an FIR filter
3. Convert to minimum-phase using Hilbert transform of log magnitude

The steep slopes (48-96 dB/oct) are much steeper than practical IIR designs
and provide excellent separation between mains and subs, reducing distortion
in the crossover region.

With ``alignment='linkwitz-riley'`` the magnitude is an LR4 or LR8 target
instead (F-374): each leg is -6 dB at fc and the minimum-phase HP and LP
legs sum flat and in phase.  The default (None) keeps the legacy knee
byte-identical.
"""

import numpy as np
import scipy.signal

from . import dsp_utils


SAMPLE_RATE = dsp_utils.SAMPLE_RATE

LINKWITZ_RILEY = 'linkwitz-riley'

# LR orders that sum in phase without a polarity flip (LR4, LR8).
LR_SLOPES_DB_PER_OCT = (24.0, 48.0)

# The LR8 HP leg reaches 1e-10 at ~0.056*fc; clipping the log magnitude
# there corrupts the Hilbert-derived phase, so the LR path floors at 1e-20.
_LR_LOG_FLOOR = 1e-20
_LEGACY_LOG_FLOOR = 1e-10


def _validate_alignment(alignment, *slopes_db_per_oct):
    """Raise ValueError for an unknown alignment or an unsupported LR slope."""
    if alignment is None:
        return
    if alignment != LINKWITZ_RILEY:
        raise ValueError(
            f"Unknown crossover alignment '{alignment}'; expected "
            f"None or '{LINKWITZ_RILEY}'"
        )
    for slope in slopes_db_per_oct:
        if float(slope) not in LR_SLOPES_DB_PER_OCT:
            raise ValueError(
                f"Linkwitz-Riley crossover supports 24 or 48 dB/oct, "
                f"got {slope}"
            )


def _log_floor(alignment):
    return _LEGACY_LOG_FLOOR if alignment is None else _LR_LOG_FLOOR


def _lr_magnitude(freqs, crossover_freq, filter_type, slope_db_per_oct, sr):
    """Linkwitz-Riley magnitude: LP = 1/(1+x), HP = x/(1+x).

    x = (w/wc)^(S/6) on the bilinear-warped frequency w = tan(pi*f/sr):
    this is the exact digital LR magnitude, whose min-phase legs stay in
    phase (ln(f) has a Nyquist kink that skews the Hilbert phase).
    """
    nyquist = sr / 2.0
    warped = np.tan(np.pi * np.clip(freqs, 0.0, nyquist) / sr)
    ratio = warped / np.tan(np.pi * crossover_freq / sr)
    order = slope_db_per_oct / 6.0
    with np.errstate(divide='ignore', over='ignore'):
        if filter_type == 'highpass':
            return 1.0 / (1.0 + ratio ** -order)
        return 1.0 / (1.0 + ratio ** order)


def _design_crossover_magnitude(freqs, crossover_freq, filter_type, slope_db_per_oct,
                                alignment=None, sr=SAMPLE_RATE):
    """
    Design the target magnitude response for a crossover filter.

    With ``alignment=None`` (legacy) this creates a smooth rolloff shape
    rather than a true brick-wall to avoid Gibbs phenomenon ringing. The
    rolloff follows a power law that matches the specified slope in
    dB/octave, with a 0 dB knee at the crossover frequency.

    With ``alignment='linkwitz-riley'`` the shape is a Linkwitz-Riley
    magnitude (-6 dB at the crossover frequency), so complementary
    highpass and lowpass legs sum flat.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency array in Hz.
    crossover_freq : float
        Crossover frequency in Hz.
    filter_type : str
        'highpass' or 'lowpass'.
    slope_db_per_oct : float
        Rolloff slope in dB per octave.
    alignment : str or None
        None (legacy knee) or 'linkwitz-riley'.
    sr : int
        Sample rate (used by the Linkwitz-Riley frequency warping).

    Returns
    -------
    np.ndarray
        Target magnitude response (linear scale).

    Raises
    ------
    ValueError
        If alignment is unknown or the slope is not a supported LR order.
    """
    _validate_alignment(alignment, slope_db_per_oct)
    if alignment == LINKWITZ_RILEY:
        return _lr_magnitude(freqs, crossover_freq, filter_type, slope_db_per_oct, sr)

    magnitude = np.ones_like(freqs, dtype=np.float64)

    for i, f in enumerate(freqs):
        if f <= 0:
            if filter_type == 'highpass':
                magnitude[i] = 0.0
            continue

        ratio = f / crossover_freq
        if filter_type == 'highpass':
            if ratio < 1.0:
                # Below crossover: attenuate
                octaves_below = -np.log2(ratio)
                attenuation_db = slope_db_per_oct * octaves_below
                magnitude[i] = dsp_utils.db_to_linear(-attenuation_db)
            # Above crossover: passband (1.0)
        elif filter_type == 'lowpass':
            if ratio > 1.0:
                # Above crossover: attenuate
                octaves_above = np.log2(ratio)
                attenuation_db = slope_db_per_oct * octaves_above
                magnitude[i] = dsp_utils.db_to_linear(-attenuation_db)
            # Below crossover: passband (1.0)

    return magnitude


def generate_subsonic_filter(
    hpf_freq,
    slope_db_per_oct=24.0,
    n_taps=16384,
    sr=SAMPLE_RATE,
):
    """
    Generate a minimum-phase FIR subsonic protection highpass filter.

    Ported subwoofers have sharply rising cone excursion below their tuning
    frequency. Without a subsonic filter, room correction could boost
    sub-bass energy that pushes the driver past its Xmax limit. This filter
    provides a steep highpass rolloff below the specified frequency.

    The filter uses a minimum-phase design to avoid pre-ringing, consistent
    with the rest of the FIR pipeline.

    Parameters
    ----------
    hpf_freq : float
        Highpass cutoff frequency in Hz (typically the port tuning frequency
        or a safety margin above it).
    slope_db_per_oct : float
        Rolloff steepness in dB/octave. Must be >= 24 for adequate
        excursion protection. Default 24 dB/oct.
    n_taps : int
        Output filter length.
    sr : int
        Sample rate.

    Returns
    -------
    np.ndarray
        Minimum-phase FIR subsonic protection filter.

    Raises
    ------
    ValueError
        If slope_db_per_oct < 24 (insufficient protection).
    """
    if slope_db_per_oct < 24.0:
        raise ValueError(
            f"Subsonic filter slope must be >= 24 dB/oct for adequate "
            f"excursion protection, got {slope_db_per_oct}"
        )

    n_fft = dsp_utils.next_power_of_2(n_taps * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    # Design target magnitude: highpass at hpf_freq
    magnitude = _design_crossover_magnitude(freqs, hpf_freq, 'highpass', slope_db_per_oct)

    subsonic_filter = _magnitude_to_min_phase_fir(magnitude, n_fft, n_taps)

    # Normalize: passband (above hpf_freq) should be at unity
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(subsonic_filter)
    mask = (passband_freqs >= hpf_freq * 2) & (passband_freqs <= sr / 2 * 0.9)
    if np.any(mask):
        passband_level = np.mean(passband_mag[mask])
        if passband_level > 0:
            subsonic_filter /= passband_level

    return subsonic_filter


def _normalise_to_target(fir, target_fn, lo, hi, sr):
    """Scale *fir* so its magnitude matches *target_fn* over [lo, hi] Hz.

    Linkwitz-Riley path only.  The gain is the mean dB difference between
    measured and target magnitude, so the legs stay at -6 dB at fc instead
    of being pulled to unity by a passband that has not fully settled.
    """
    n_fft = dsp_utils.next_power_of_2(len(fir))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return fir
    measured = np.abs(np.fft.rfft(fir, n=n_fft))[mask]
    target = target_fn(freqs[mask])
    log_offset = np.mean(np.log(np.maximum(measured, _LR_LOG_FLOOR))
                         - np.log(np.maximum(target, _LR_LOG_FLOOR)))
    return fir / np.exp(log_offset)


def _magnitude_to_min_phase_fir(magnitude, n_fft, n_taps, floor=_LEGACY_LOG_FLOOR):
    """Synthesise a minimum-phase FIR from a half-spectrum magnitude.

    Shared helper for all crossover filter types.

    Parameters
    ----------
    magnitude : np.ndarray
        Target magnitude (rfft bins, linear scale).
    n_fft : int
        FFT size used for synthesis.
    n_taps : int
        Desired output FIR length.
    floor : float
        Magnitude floor before the log.  The LR8 HP leg reaches 1e-10 at
        about 0.056*fc, and clipping there corrupts the Hilbert phase, so
        the LR path passes 1e-20.

    Returns
    -------
    np.ndarray
        Minimum-phase FIR of length *n_taps*, with fade-out window applied.
    """
    log_mag_half = np.log(np.maximum(magnitude, floor))
    log_mag_full = np.zeros(n_fft, dtype=np.float64)
    log_mag_full[:len(log_mag_half)] = log_mag_half
    log_mag_full[len(log_mag_half):] = log_mag_half[-2:0:-1]

    cepstrum = np.fft.ifft(log_mag_full).real

    n_half = n_fft // 2
    causal_window = np.zeros(n_fft)
    causal_window[0] = 1.0
    causal_window[1:n_half] = 2.0
    if n_fft % 2 == 0:
        causal_window[n_half] = 1.0

    min_phase_cepstrum = cepstrum * causal_window
    min_phase_spectrum = np.exp(np.fft.fft(min_phase_cepstrum))
    fir = np.fft.ifft(min_phase_spectrum).real

    # Truncate with fade-out
    fir = fir[:n_taps]
    fade_out_len = n_taps // 20
    fade = dsp_utils.fade_window(n_taps, 0, fade_out_len)
    fir *= fade
    return fir


def generate_bandpass_filter(
    low_freq,
    high_freq,
    low_slope_db_per_oct=48.0,
    high_slope_db_per_oct=96.0,
    n_taps=16384,
    sr=SAMPLE_RATE,
    alignment=None,
):
    """Generate a minimum-phase FIR bandpass crossover filter.

    Creates a bandpass by multiplying a highpass magnitude response (at
    *low_freq*) with a lowpass magnitude response (at *high_freq*) and
    synthesising a minimum-phase FIR via the cepstral method.  Independent
    slopes per edge allow different rolloff rates (e.g. gentle low-end
    rolloff but steep high-end cutoff).

    Parameters
    ----------
    low_freq : float
        Lower crossover frequency in Hz (highpass edge).
    high_freq : float
        Upper crossover frequency in Hz (lowpass edge).
    low_slope_db_per_oct : float
        Rolloff steepness at the low edge in dB/octave.
    high_slope_db_per_oct : float
        Rolloff steepness at the high edge in dB/octave.
    n_taps : int
        Output filter length.
    sr : int
        Sample rate.
    alignment : str, optional
        None for the legacy knee, or ``'linkwitz-riley'`` for LR edges
        (both edges must then be 24 or 48 dB/oct).

    Returns
    -------
    np.ndarray
        Minimum-phase FIR bandpass crossover filter.  Legacy: unity gain in
        the passband centre.  LR: matched to the LR target there.

    Raises
    ------
    ValueError
        If *low_freq* >= *high_freq*, or the alignment or an LR slope is
        unsupported.
    """
    if low_freq >= high_freq:
        raise ValueError(
            f"low_freq ({low_freq}) must be less than high_freq ({high_freq})"
        )
    _validate_alignment(alignment, low_slope_db_per_oct, high_slope_db_per_oct)

    n_fft = dsp_utils.next_power_of_2(n_taps * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    def band_magnitude(f):
        hp = _design_crossover_magnitude(
            f, low_freq, 'highpass', low_slope_db_per_oct, alignment, sr)
        lp = _design_crossover_magnitude(
            f, high_freq, 'lowpass', high_slope_db_per_oct, alignment, sr)
        return hp * lp

    fir = _magnitude_to_min_phase_fir(
        band_magnitude(freqs), n_fft, n_taps, floor=_log_floor(alignment))

    # Normalise: unity gain at passband centre (geometric mean of edges)
    center_freq = np.sqrt(low_freq * high_freq)
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(fir)
    lo = max(low_freq * 1.5, center_freq * 0.7)
    hi = min(high_freq * 0.67, center_freq * 1.4)
    if lo >= hi:
        lo, hi = low_freq * 1.2, high_freq * 0.8
    if alignment is not None:
        return _normalise_to_target(fir, band_magnitude, lo, hi, sr)
    mask = (passband_freqs >= lo) & (passband_freqs <= hi)
    if np.any(mask):
        passband_level = np.mean(passband_mag[mask])
        if passband_level > 0:
            fir /= passband_level

    return fir


def generate_crossover_filter(
    filter_type,
    crossover_freq=80.0,
    slope_db_per_oct=48.0,
    n_taps=16384,
    sr=SAMPLE_RATE,
    crossover_freq_high=None,
    high_slope_db_per_oct=None,
    alignment=None,
):
    """
    Generate a minimum-phase FIR crossover filter.

    Parameters
    ----------
    filter_type : str
        'highpass' for mains, 'lowpass' for subs, 'bandpass' for mid-range
        drivers in 3-way or 4-way topologies.
    crossover_freq : float
        Crossover frequency in Hz.  For bandpass this is the *lower* edge.
    slope_db_per_oct : float
        Rolloff steepness (48-96 dB/oct recommended).  For bandpass this
        applies to the lower edge.
    n_taps : int
        Output filter length.
    sr : int
        Sample rate.
    crossover_freq_high : float, optional
        Upper crossover frequency (required for bandpass).
    high_slope_db_per_oct : float, optional
        Rolloff steepness at the upper edge (bandpass only).  Defaults to
        *slope_db_per_oct* if not provided.
    alignment : str, optional
        None (default) for the legacy knee.  ``'linkwitz-riley'`` gives an
        LR4 (24 dB/oct) or LR8 (48 dB/oct) leg: -6 dB at fc, summing flat
        and in phase with the complementary leg.

    Returns
    -------
    np.ndarray
        Minimum-phase FIR crossover filter.

    Raises
    ------
    ValueError
        If filter_type is unknown, bandpass parameters are invalid, or the
        alignment or an LR slope is unsupported.
    """
    if filter_type == 'bandpass':
        if crossover_freq_high is None:
            raise ValueError(
                "crossover_freq_high is required for bandpass filter_type"
            )
        return generate_bandpass_filter(
            low_freq=crossover_freq,
            high_freq=crossover_freq_high,
            low_slope_db_per_oct=slope_db_per_oct,
            high_slope_db_per_oct=(
                high_slope_db_per_oct if high_slope_db_per_oct is not None
                else slope_db_per_oct
            ),
            n_taps=n_taps,
            sr=sr,
            alignment=alignment,
        )

    if filter_type not in ('highpass', 'lowpass'):
        raise ValueError(
            f"Unknown filter_type '{filter_type}'; expected "
            f"'highpass', 'lowpass', or 'bandpass'"
        )
    _validate_alignment(alignment, slope_db_per_oct)

    n_fft = dsp_utils.next_power_of_2(n_taps * 4)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    # Design target magnitude
    magnitude = _design_crossover_magnitude(
        freqs, crossover_freq, filter_type, slope_db_per_oct, alignment, sr)

    fir = _magnitude_to_min_phase_fir(
        magnitude, n_fft, n_taps, floor=_log_floor(alignment))

    if filter_type == 'highpass':
        lo, hi = crossover_freq * 2, sr / 2 * 0.9
    else:
        lo, hi = 20, crossover_freq * 0.5

    if alignment is not None:
        return _normalise_to_target(
            fir,
            lambda f: _design_crossover_magnitude(
                f, crossover_freq, filter_type, slope_db_per_oct, alignment, sr),
            lo, hi, sr,
        )

    # Normalize: passband should be at 0dB (unity gain)
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(fir)
    mask = (passband_freqs >= lo) & (passband_freqs <= hi)

    if np.any(mask):
        passband_level = np.mean(passband_mag[mask])
        if passband_level > 0:
            fir /= passband_level

    return fir
