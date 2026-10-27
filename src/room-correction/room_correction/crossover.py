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

import numbers
from typing import NamedTuple, Optional

import numpy as np
import scipy.signal

from . import dsp_utils, min_phase


SAMPLE_RATE = dsp_utils.SAMPLE_RATE

LINKWITZ_RILEY = 'linkwitz-riley'

# Profile ``crossover.type`` values the generator supports (F-374).
CROSSOVER_TYPES = (LINKWITZ_RILEY,)

# LR orders that sum in phase without a polarity flip (LR4, LR8).
LR_SLOPES_DB_PER_OCT = (24.0, 48.0)

# The LR8 HP leg reaches 1e-10 at ~0.056*fc; clipping the log magnitude
# there corrupts the Hilbert-derived phase, so the LR path floors at 1e-20.
_LR_LOG_FLOOR = 1e-20
_LEGACY_LOG_FLOOR = 1e-10

# The subsonic designs on a 64x grid at _LR_LOG_FLOOR (F-383 R6d A1, F1-64):
# its steep knee is not minimum phase on the shared 4x grid at 1e-10.
SUBSONIC_DESIGN_OVERSAMPLE = 64


class CrossoverSpecError(ValueError):
    """A crossover type or slope the generator cannot design (F-374)."""


def _is_lr_slope(slope):
    if isinstance(slope, bool) or not isinstance(slope, numbers.Real):
        return False
    return float(slope) in LR_SLOPES_DB_PER_OCT


def _validate_alignment(alignment, *slopes_db_per_oct):
    """Raise CrossoverSpecError on an unknown alignment or a non-LR slope."""
    if alignment is None:
        return
    if alignment != LINKWITZ_RILEY:
        raise CrossoverSpecError(
            f"Unknown crossover alignment '{alignment}'; expected "
            f"None or '{LINKWITZ_RILEY}'"
        )
    for slope in slopes_db_per_oct:
        if not _is_lr_slope(slope):
            shown = slope if isinstance(slope, numbers.Real) else repr(slope)
            raise CrossoverSpecError(
                f"Linkwitz-Riley crossover supports 24 or 48 dB/oct, "
                f"got {shown}"
            )


def validate_crossover_spec(crossover_type, *slopes_db_per_oct):
    """Raise CrossoverSpecError unless a profile crossover can be generated.

    The single check behind the generator, the speaker editor save and the
    measurement session start (F-374).  *crossover_type* is the profile's
    ``crossover.type``; *slopes_db_per_oct* are every slope the generator
    will design with it.
    """
    if crossover_type not in CROSSOVER_TYPES:
        raise CrossoverSpecError(
            f"Unknown crossover type '{crossover_type}'; expected "
            f"'{LINKWITZ_RILEY}'"
        )
    _validate_alignment(crossover_type, *slopes_db_per_oct)


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
    with the rest of the FIR pipeline. It is synthesised on an FFT grid of
    SUBSONIC_DESIGN_OVERSAMPLE x n_taps with the log floor _LR_LOG_FLOOR.

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
    min_phase.MinimumPhaseError
        If the filter is not the minimum-phase FIR of its design (F-383 A1b;
        checked when n_taps >= min_phase.A1B_MIN_TAPS).
    """
    if slope_db_per_oct < 24.0:
        raise ValueError(
            f"Subsonic filter slope must be >= 24 dB/oct for adequate "
            f"excursion protection, got {slope_db_per_oct}"
        )

    n_fft = dsp_utils.next_power_of_2(n_taps * SUBSONIC_DESIGN_OVERSAMPLE)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    def design(f):
        return _design_crossover_magnitude(f, hpf_freq, 'highpass', slope_db_per_oct)

    # Design target magnitude: highpass at hpf_freq
    magnitude = design(freqs)

    subsonic_filter = _magnitude_to_min_phase_fir(
        magnitude, n_fft, n_taps, floor=_LR_LOG_FLOOR)

    # Normalize: passband (above hpf_freq) should be at unity
    passband_freqs, passband_mag = dsp_utils.rfft_magnitude(subsonic_filter)
    mask = (passband_freqs >= hpf_freq * 2) & (passband_freqs <= sr / 2 * 0.9)
    if np.any(mask):
        passband_level = np.mean(passband_mag[mask])
        if passband_level > 0:
            subsonic_filter /= passband_level

    min_phase.check_design_residual(
        subsonic_filter, design, _LR_LOG_FLOOR,
        f"subsonic {hpf_freq} Hz {slope_db_per_oct} dB/oct", sr=sr)
    return subsonic_filter


# -- Subsonic corner derivation (F-383 C4) ----------------------------------

# C4.1: on a channel with a crossover HP the subsonic corner may sit at
# <= fc_hp / 5; the protection is judged on the product (D-031 unchanged).
SUBSONIC_CORNER_RATIO = 5.0

# NB-C4a grid: 1/12 octave from 10 Hz up to m (AE a2 of 41fd1486).
NB_C4A_LOW_HZ = 10.0
NB_C4A_STEPS_PER_OCT = 12

# L2' (Part B 9e5eb913): att(m/2) re the H1 peak, and att(m/4) >= att(m/2).
L2_MIN_HALF_DB = 18.0

_DERIVE_N_FFT = 1 << 17
_DERIVE_DB_FLOOR = 1e-30


class SubsonicDerivationError(ValueError):
    """A moved subsonic corner fails NB-C4a or L2' (NB-C4b: a STOP)."""


class SubsonicDerivation(NamedTuple):
    """The subsonic factor derive_subsonic() chose for one channel.

    The gate fields are None when the corner was not moved.
    """

    corner_hz: float
    fir: np.ndarray
    moved: bool
    reason: str
    c4a_margin_db: Optional[float]
    c4a_margin_hz: Optional[float]
    l2_half_db: Optional[float]
    l2_quarter_db: Optional[float]


def subsonic_corner(mandatory_hpf_hz, hp_edge_hz, partner_subsonic_hz=None):
    """Rule R4 (Architect 62cd5e5c, AE 9973bc8b): (corner_hz, moved, reason).

    m is the identity's mandatory_hpf_hz, fc_hp the channel's crossover HP
    edge (None for lowpass and fullrange channels) and s the subsonic corner
    of its crossover partner, the leg whose LP edge is fc_hp (None if the
    partner has no subsonic).  target = fc_hp/5 if s is None, else
    max(fc_hp/5, s).  The corner moves to target iff target < m < fc_hp.
    """
    m = mandatory_hpf_hz
    if hp_edge_hz is None:
        return m, False, "no HP edge"
    if m >= hp_edge_hz:
        return m, False, "m >= fc_hp"
    target = hp_edge_hz / SUBSONIC_CORNER_RATIO
    if partner_subsonic_hz is not None:
        target = max(target, partner_subsonic_hz)
    if target >= m:
        if partner_subsonic_hz is not None and partner_subsonic_hz >= m:
            return m, False, "target >= m (s >= m)"
        return m, False, "target >= m (fc_hp/5 >= m)"
    if partner_subsonic_hz is not None and partner_subsonic_hz == target:
        return target, True, "moved to s"
    return target, True, "moved to fc_hp/5"


def _db(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), _DERIVE_DB_FLOOR))


def _response(b, freqs, sr):
    return scipy.signal.freqz(b, worN=np.atleast_1d(np.asarray(freqs, float)), fs=sr)[1]


def derive_subsonic(
    mandatory_hpf_hz,
    hp_edge_hz,
    hp_filter,
    slope_db_per_oct=24.0,
    partner_subsonic_hz=None,
    n_taps=16384,
    sr=SAMPLE_RATE,
    channel="",
    make_subsonic=None,
):
    """
    Derive a channel's subsonic factor from its identity corner (F-383 C4).

    The one derivation for every combine caller (C4.2).  The corner follows
    subsonic_corner() (rule R4).  A moved corner is gated on the product
    P = hp_filter * subsonic(corner), evaluated exactly with freqz:

    - NB-C4a: |ref| - |P| >= 0 dB on the 1/12-octave grid from 10 Hz to m,
      where ref is the subsonic at m with the same slope;
    - L2': att_P(m/2) >= 18 dB re P's H1 peak, and att_P(m/4) >= att_P(m/2).

    A failing gate raises; no other corner is tried and fc is never touched
    (NB-C4b).  The function is pure; make_subsonic(hpf_freq, slope) lets a
    caller cache the subsonic FIRs (default: generate_subsonic_filter).

    Parameters
    ----------
    mandatory_hpf_hz : float or None
        The identity's protection corner m.  None returns None.
    hp_edge_hz : float or None
        The channel's crossover HP edge fc_hp; None if it has none.
    hp_filter : np.ndarray or None
        The channel's crossover FIR; needed only if the corner moves.
    slope_db_per_oct : float
        Subsonic slope, as for generate_subsonic_filter().
    partner_subsonic_hz : float or None
        The crossover partner's subsonic corner s (R4).
    channel : str
        Channel name for the raise message.

    Returns
    -------
    SubsonicDerivation or None

    Raises
    ------
    SubsonicDerivationError
        If a moved corner fails NB-C4a or L2'.  The message names the
        channel, m, the corner, the check, the frequency and the margin.
    """
    if mandatory_hpf_hz is None:
        return None
    if make_subsonic is None:
        def make_subsonic(hpf_freq, slope):
            return generate_subsonic_filter(
                hpf_freq=hpf_freq, slope_db_per_oct=slope, n_taps=n_taps, sr=sr)

    m = mandatory_hpf_hz
    corner, moved, reason = subsonic_corner(m, hp_edge_hz, partner_subsonic_hz)
    fir = make_subsonic(corner, slope_db_per_oct)
    if not moved:
        return SubsonicDerivation(corner, fir, False, reason, None, None, None, None)
    if hp_filter is None:
        raise ValueError(f"{channel}: a moved subsonic corner needs the channel's HP filter")

    def stop(check, freq, margin, detail):
        raise SubsonicDerivationError(
            f"{channel}: subsonic corner moved from m {m} Hz to {corner} Hz fails "
            f"{check} at {freq:.1f} Hz, margin {margin:+.2f} dB ({detail}). "
            f"STOP (NB-C4b): no other corner is tried.")

    ref = make_subsonic(m, slope_db_per_oct)
    steps = np.arange(0, int(np.floor(NB_C4A_STEPS_PER_OCT * np.log2(m / NB_C4A_LOW_HZ))) + 1)
    grid = np.unique(np.append(NB_C4A_LOW_HZ * 2.0 ** (steps / NB_C4A_STEPS_PER_OCT), m))
    margins = _db(_response(ref, grid, sr)) - _db(
        _response(hp_filter, grid, sr) * _response(fir, grid, sr))
    i = int(np.argmin(margins))
    c4a_margin_db, c4a_margin_hz = float(margins[i]), float(grid[i])
    if c4a_margin_db < 0.0:
        stop("NB-C4a", c4a_margin_hz, c4a_margin_db,
             f"product above the subsonic at m, {slope_db_per_oct} dB/oct")

    product = np.fft.rfft(hp_filter, _DERIVE_N_FFT) * np.fft.rfft(fir, _DERIVE_N_FFT)
    freqs = np.fft.rfftfreq(_DERIVE_N_FFT, d=1.0 / sr)
    peak_db, _, _ = dsp_utils.h1_passband_peak_db(freqs, _db(product), m, sr=sr)
    if peak_db is None:
        raise ValueError(f"{channel}: no H1 passband bins above m {m} Hz")

    def att(freq):
        return peak_db - float(_db(_response(hp_filter, freq, sr) * _response(fir, freq, sr))[0])

    l2_half_db, l2_quarter_db = att(m / 2.0), att(m / 4.0)
    if l2_half_db < L2_MIN_HALF_DB:
        stop("L2'", m / 2.0, l2_half_db - L2_MIN_HALF_DB,
             f"att(m/2) {l2_half_db:.1f} dB re the H1 peak, required >= {L2_MIN_HALF_DB} dB")
    if l2_quarter_db < l2_half_db:
        stop("L2'", m / 4.0, l2_quarter_db - l2_half_db,
             f"att(m/4) {l2_quarter_db:.1f} dB < att(m/2) {l2_half_db:.1f} dB")
    return SubsonicDerivation(corner, fir, True, reason, c4a_margin_db, c4a_margin_hz,
                              l2_half_db, l2_quarter_db)


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
    min_phase.MinimumPhaseError
        If the filter is not the minimum-phase FIR of its design (F-383 A1b;
        checked when n_taps >= min_phase.A1B_MIN_TAPS).
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
        fir = _normalise_to_target(fir, band_magnitude, lo, hi, sr)
    else:
        mask = (passband_freqs >= lo) & (passband_freqs <= hi)
        if np.any(mask):
            passband_level = np.mean(passband_mag[mask])
            if passband_level > 0:
                fir /= passband_level

    min_phase.check_design_residual(
        fir, band_magnitude, _log_floor(alignment),
        f"bandpass {low_freq}-{high_freq} Hz", sr=sr)
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
    min_phase.MinimumPhaseError
        If the filter is not the minimum-phase FIR of its design (F-383 A1b;
        checked when n_taps >= min_phase.A1B_MIN_TAPS).
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

    def design(f):
        return _design_crossover_magnitude(
            f, crossover_freq, filter_type, slope_db_per_oct, alignment, sr)

    # Design target magnitude
    magnitude = design(freqs)

    fir = _magnitude_to_min_phase_fir(
        magnitude, n_fft, n_taps, floor=_log_floor(alignment))

    if filter_type == 'highpass':
        lo, hi = crossover_freq * 2, sr / 2 * 0.9
    else:
        lo, hi = 20, crossover_freq * 0.5

    if alignment is not None:
        fir = _normalise_to_target(fir, design, lo, hi, sr)
    else:
        # Normalize: passband should be at 0dB (unity gain)
        passband_freqs, passband_mag = dsp_utils.rfft_magnitude(fir)
        mask = (passband_freqs >= lo) & (passband_freqs <= hi)

        if np.any(mask):
            passband_level = np.mean(passband_mag[mask])
            if passband_level > 0:
                fir /= passband_level

    min_phase.check_design_residual(
        fir, design, _log_floor(alignment),
        f"{filter_type} {crossover_freq} Hz {slope_db_per_oct} dB/oct", sr=sr)
    return fir
