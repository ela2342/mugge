"""
Room correction filter generation.

Takes a measured impulse response and produces a correction filter that
flattens the room response (or shapes it to a target curve). The correction
is CUT-ONLY with a -0.5dB safety margin (D-009).

The algorithm:
1. Compute magnitude spectrum of the measured IR
2. Apply psychoacoustic smoothing (frequency-dependent octave fractions)
3. Apply frequency-dependent windowing (aggressive LF, gentle HF)
4. Compute the inverse: target / measured
5. Enforce D-009: clip all gains to -0.5dB maximum
6. Convert to minimum-phase FIR
7. Scale the finished FIR by one cut-only gain so its true peak stays at or
   below the margin (F-384)

The cut-only constraint means we only attenuate room peaks and apply
subtractive target shaping. Room nulls are left uncorrected — boosting
into a null wastes amplifier power and creates narrow peaks that are
spatially unstable (they help at the mic position but make things worse
everywhere else).

Every product path (venue pipeline, web-UI filter routes, measurement
session) builds its correction through correction_from_measurement()
(F-262). It is the only production caller of normalize_ir_level() and
generate_correction_filter().
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from . import combine
from . import dsp_utils
from . import target_curves as tc


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
D009_MARGIN_DB = -0.5
# F-383/F-384 B3: the D-009 scalar measures the peak on an 8x grid (2^17
# points at 16384 taps), full band. 4x under-reads the inter-bin peak by up to 0.045 dB.
D009_SCALAR_OVERSAMPLE = 8

# AE, 2026-10-25: level reference per driver role (median of the
# 1/6-octave smoothed magnitude). Sats stay clear of the 200 Hz crossover
# and the box knee; the sub band sits below the crossover.
REFERENCE_BANDS_HZ = {
    "highpass": (400.0, 4000.0),
    "lowpass": (30.0, 150.0),
}
# AE, 2026-10-25: never cut deeper than 18 dB.
MAX_CUT_DB = 18.0
# F-383 C1 (Architect f3286c42, AE 6192482b): the step-7 cepstral synthesis
# runs on a grid this many times finer than the design grid. On the design
# grid the cepstrum aliases and the FIR misses A1a (residual -40 / tail -60 dB)
# on some inputs; the design itself (steps 1-6) stays on its own grid.
SYNTH_GRID_FACTOR = 4


@dataclass(frozen=True)
class CorrectionFilter:
    """A room correction FIR built from a measured IR (F-262).

    generate_profile_filters() accepts only this type, so a raw measured
    IR can no longer be combined as if it were a correction.
    """

    fir: np.ndarray
    reference_level_db: float          # measured level before normalization
    ref_band_hz: Tuple[float, float]   # band the level was taken over
    # F-384 q4: D-009 scalar step 9 applied (dB, <= 0); None = not known.
    d009_scalar_db: Optional[float] = None


# AE, F-262 item 3: no residual or level reference band is defined for
# bandpass drivers yet, so 3-/4-way profiles fail closed in every correction
# path. Crossover-only generation is unchanged.
BANDPASS_NOT_SUPPORTED = "room correction not supported for bandpass (3-/4-way) profiles"


def require_correctable(speakers):
    """Raise ValueError if a profile's speakers can't get a room correction."""
    if any(spk.get("filter_type") == "bandpass" for spk in speakers.values()):
        raise ValueError(f"Measurement rejected: {BANDPASS_NOT_SUPPORTED}")


def reference_band(speaker):
    """Level reference band for a profile speaker dict (by its filter_type)."""
    filter_type = speaker.get("filter_type", "highpass")
    if filter_type == "bandpass":
        raise ValueError(f"no level reference band: {BANDPASS_NOT_SUPPORTED}")
    if filter_type not in REFERENCE_BANDS_HZ:
        raise ValueError(f"no level reference band for filter_type {filter_type!r}")
    return REFERENCE_BANDS_HZ[filter_type]


def generate_correction_filter(
    ir,
    target_curve_name='flat',
    n_taps=16384,
    sr=SAMPLE_RATE,
    margin_db=D009_MARGIN_DB,
    target_phon=None,
    reference_phon=80.0,
    max_cut_db=None,
    *,
    return_scalar_db=False,
):
    """
    Generate a room correction filter from a measured impulse response.

    Parameters
    ----------
    ir : np.ndarray
        Measured room impulse response.
    target_curve_name : str
        Target curve name ('flat', 'harman', 'pa').
    n_taps : int
        Desired output filter length.
    sr : int
        Sample rate.
    margin_db : float
        D-009 safety margin. All gains clipped to this value.
    target_phon : float or None
        If provided, apply ISO 226 equal-loudness compensation for this
        playback level (20-90 phon). None = no compensation.
    reference_phon : float
        Loudness level the content was mixed for (default 80 phon).
        Only used when target_phon is not None.
    max_cut_db : float or None
        Upper bound on the cut depth in dB (positive number, e.g. 18.0).
        No gain is driven below -max_cut_db. None = no cap (default,
        unchanged behaviour). The cut is only meaningful relative to the
        target if the IR level has been normalized first, see
        normalize_ir_level().
    return_scalar_db : bool
        If True, also return the D-009 scalar step 9 applied (F-384 q3).

    Returns
    -------
    np.ndarray or tuple of (np.ndarray, float)
        Correction filter (minimum-phase FIR, n_taps long). With
        return_scalar_db, (filter, scalar in dB): <= 0, exactly 0.0 when
        the FIR was already at or below margin_db.
    """
    correction_filter = _unscaled_correction_filter(
        ir, target_curve_name=target_curve_name, n_taps=n_taps, sr=sr,
        margin_db=margin_db, target_phon=target_phon,
        reference_phon=reference_phon, max_cut_db=max_cut_db)
    fir, scalar_db = _d009_scale(correction_filter, margin_db, sr=sr)
    return (fir, scalar_db) if return_scalar_db else fir


def _unscaled_correction_filter(
    ir,
    target_curve_name='flat',
    n_taps=16384,
    sr=SAMPLE_RATE,
    margin_db=D009_MARGIN_DB,
    target_phon=None,
    reference_phon=80.0,
    max_cut_db=None,
    synth_grid_factor=SYNTH_GRID_FACTOR,
):
    """Steps 1-8 of generate_correction_filter(): the FIR before the D-009 scalar.

    synth_grid_factor 1 is the pre-F-383 synthesis on the design grid; kept for
    the regression test only.
    """
    ir = np.asarray(ir, dtype=np.float64)

    # Step 1: Apply frequency-dependent windowing to the IR
    windowed_ir = dsp_utils.frequency_dependent_window(ir, sr=sr)

    # Step 2: Compute magnitude spectrum
    n_fft = dsp_utils.next_power_of_2(max(len(windowed_ir), n_taps * 2))
    spectrum = np.fft.rfft(windowed_ir, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    magnitudes = np.abs(spectrum)

    # Step 3: Apply psychoacoustic smoothing
    smoothed_mag = dsp_utils.psychoacoustic_smooth(magnitudes, freqs)

    # Step 4: Get target curve
    target_db = tc.get_target_curve(
        target_curve_name, freqs,
        target_phon=target_phon, reference_phon=reference_phon,
    )
    target_linear = dsp_utils.db_to_linear(target_db)

    # Step 5: Compute correction = target / measured
    # This is the inverse filter: it cancels the room's effect and applies
    # the desired target shape.
    correction_linear = target_linear / np.maximum(smoothed_mag, 1e-10)

    # Step 6: D-009 enforcement — CUT ONLY with safety margin
    # Convert to dB, clip to margin, convert back
    correction_db = dsp_utils.linear_to_db(correction_linear)
    correction_db = np.minimum(correction_db, margin_db)
    if max_cut_db is not None:
        correction_db = np.maximum(correction_db, -abs(max_cut_db))
    correction_linear = dsp_utils.db_to_linear(correction_db)

    # Step 7: Build minimum-phase FIR directly from the clipped magnitude
    # spectrum using the cepstral method, on a finer grid (F-383 C1).
    log_mag_half = np.log(np.maximum(correction_linear, 1e-10))
    correction_filter = _cepstral_min_phase(log_mag_half, n_fft, synth_grid_factor)

    # Step 8: Truncate to desired length with fade-out
    correction_filter = correction_filter[:n_taps]
    fade_out_len = n_taps // 20  # 5% fade-out
    fade = dsp_utils.fade_window(n_taps, 0, fade_out_len)
    correction_filter *= fade

    return correction_filter


def _cepstral_min_phase(log_mag_half, n_fft, k):
    """
    Minimum-phase impulse response of a log magnitude on an n_fft rfft grid.

    The log magnitude is linearly interpolated onto a grid k times finer
    (DC and Nyquist land on grid points, so they are kept exactly) and the
    cepstrum is taken there (F-383 C1). Returns the full k * n_fft response;
    the caller truncates. k=1 is the synthesis on the design grid itself.
    """
    n_fine = n_fft * k
    if k == 1:
        log_mag_fine = log_mag_half
    else:
        log_mag_fine = np.interp(
            np.arange(n_fine // 2 + 1) / k, np.arange(len(log_mag_half)), log_mag_half)
    # Construct full-spectrum log magnitude (conjugate symmetric)
    log_mag_full = np.zeros(n_fine, dtype=np.float64)
    log_mag_full[:len(log_mag_fine)] = log_mag_fine
    log_mag_full[len(log_mag_fine):] = log_mag_fine[-2:0:-1]

    cepstrum = np.fft.ifft(log_mag_full).real

    # Causal window for minimum-phase
    n_half = n_fine // 2
    causal_window = np.zeros(n_fine)
    causal_window[0] = 1.0
    causal_window[1:n_half] = 2.0
    if n_fine % 2 == 0:
        causal_window[n_half] = 1.0

    min_phase_cepstrum = cepstrum * causal_window
    min_phase_spectrum = np.exp(np.fft.fft(min_phase_cepstrum))
    return np.fft.ifft(min_phase_spectrum).real


def _d009_scale(fir, margin_db, sr=SAMPLE_RATE):
    """
    Step 9: one cut-only D-009 gain on the finished FIR (F-384).

    Cepstral synthesis and truncation+fade can push the magnitude above the
    clipped design, also between FFT bins. A single scalar keeps the shape,
    and so the minimum phase, exactly; it never boosts (D-009 is a ceiling).
    The peak is read over the full band, 0 Hz to Nyquist: a sub-20 Hz
    overshoot plays too (F-384 q2). An FIR already at or below margin_db is
    returned unchanged. Returns (fir, scalar in dB).
    """
    peak_db = combine.max_gain_db(
        fir, sr=sr, oversample=D009_SCALAR_OVERSAMPLE, band=None)
    if not np.isfinite(peak_db):
        raise ValueError("correction filter has a non-finite peak gain")
    if peak_db <= margin_db:
        return fir, 0.0
    scalar_db = float(margin_db - peak_db)
    return fir * dsp_utils.db_to_linear(scalar_db), scalar_db


def normalize_ir_level(ir, ref_band_hz, sr=SAMPLE_RATE, target_db=0.0,
                       fraction=6):
    """
    Scale an impulse response so its passband level sits at target_db.

    generate_correction_filter() divides the target by the measured
    magnitude, so without this step the cut depth follows the absolute
    measurement level (a 10x quieter IR gets 20 dB less cut). The level
    is the MEDIAN of the 1/fraction-octave smoothed log magnitude over
    ref_band_hz. The median ignores modal peaks and nulls, which would
    shift a mean.

    Parameters
    ----------
    ir : np.ndarray
        Measured impulse response.
    ref_band_hz : tuple of (float, float)
        Reference band (low, high) in Hz, inside the driver's passband.
    sr : int
        Sample rate.
    target_db : float
        Level the reference band is moved to (dB re 1.0).
    fraction : float
        Octave fraction of the smoothing (6 = 1/6 octave).

    Returns
    -------
    tuple of (np.ndarray, float)
        (normalized IR, measured reference level in dB before scaling).
    """
    ir = np.asarray(ir, dtype=np.float64)
    f_low, f_high = float(ref_band_hz[0]), float(ref_band_hz[1])
    if not 0 < f_low < f_high < sr / 2:
        raise ValueError(f"invalid reference band {ref_band_hz!r}")

    n_fft = dsp_utils.next_power_of_2(max(len(ir), 65536))
    magnitudes = np.abs(np.fft.rfft(ir, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    # Smooth only around the band (plus half a window each side).
    edge = 2.0 ** (0.5 / fraction)
    region = (freqs >= f_low / edge) & (freqs <= f_high * edge)
    smoothed = dsp_utils.fractional_octave_smooth(
        magnitudes[region], freqs[region], fraction)
    in_band = (freqs[region] >= f_low) & (freqs[region] <= f_high)
    if not np.any(in_band):
        raise ValueError(f"no FFT bins in reference band {ref_band_hz!r}")

    level_db = float(np.median(dsp_utils.linear_to_db(smoothed[in_band])))
    if not np.isfinite(level_db) or level_db <= -199.0:
        raise ValueError("impulse response has no energy in the reference band")

    scale = dsp_utils.db_to_linear(target_db - level_db)
    return ir * scale, level_db


def correction_from_measurement(
    measured_ir,
    speaker,
    *,
    target_curve,
    n_taps,
    sr,
    max_cut_db=MAX_CUT_DB,
    target_phon=None,
    reference_phon=80.0,
):
    """
    Build the correction for one speaker from its measured IR.

    measured IR -> normalize_ir_level (speaker's reference band) ->
    generate_correction_filter (cut-only, capped at max_cut_db).

    Parameters
    ----------
    measured_ir : np.ndarray
        Measured (aligned, windowed, spatially averaged) impulse response.
    speaker : dict
        The profile's speaker dict; its filter_type picks the reference band.

    Returns
    -------
    CorrectionFilter

    Raises
    ------
    ValueError
        If the IR is not a non-empty 1-D array, has non-finite samples, is
        silent, or has no energy in the reference band.
    """
    ir = np.asarray(measured_ir, dtype=np.float64)
    if ir.ndim != 1 or ir.size == 0:
        raise ValueError(f"measured IR must be a non-empty 1-D array, got shape {ir.shape}")
    if not np.all(np.isfinite(ir)):
        raise ValueError("measured IR has non-finite samples")
    if not np.any(ir):
        raise ValueError("measured IR is silent")

    band = reference_band(speaker)
    normalized, level_db = normalize_ir_level(ir, band, sr=sr)
    fir, scalar_db = generate_correction_filter(
        normalized, target_curve_name=target_curve, n_taps=n_taps, sr=sr,
        target_phon=target_phon, reference_phon=reference_phon,
        max_cut_db=max_cut_db, return_scalar_db=True)
    return CorrectionFilter(fir=fir, reference_level_db=level_db, ref_band_hz=band,
                            d009_scalar_db=scalar_db)
