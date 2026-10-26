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
from typing import Tuple

import numpy as np

from . import dsp_utils
from . import target_curves as tc


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
D009_MARGIN_DB = -0.5

# AE, 2026-10-25: level reference per driver role (median of the
# 1/6-octave smoothed magnitude). Sats stay clear of the 200 Hz crossover
# and the box knee; the sub band sits below the crossover.
REFERENCE_BANDS_HZ = {
    "highpass": (400.0, 4000.0),
    "lowpass": (30.0, 150.0),
}
# AE, 2026-10-25: never cut deeper than 18 dB.
MAX_CUT_DB = 18.0


@dataclass(frozen=True)
class CorrectionFilter:
    """A room correction FIR built from a measured IR (F-262).

    generate_profile_filters() accepts only this type, so a raw measured
    IR can no longer be combined as if it were a correction.
    """

    fir: np.ndarray
    reference_level_db: float          # measured level before normalization
    ref_band_hz: Tuple[float, float]   # band the level was taken over


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

    Returns
    -------
    np.ndarray
        Correction filter (minimum-phase FIR, n_taps long).
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
    # spectrum using the cepstral method. This guarantees the output
    # magnitude matches the D-009-compliant design exactly.
    log_mag_half = np.log(np.maximum(correction_linear, 1e-10))
    # Construct full-spectrum log magnitude (conjugate symmetric)
    log_mag_full = np.zeros(n_fft, dtype=np.float64)
    log_mag_full[:len(log_mag_half)] = log_mag_half
    log_mag_full[len(log_mag_half):] = log_mag_half[-2:0:-1]

    cepstrum = np.fft.ifft(log_mag_full).real

    # Causal window for minimum-phase
    n_half = n_fft // 2
    causal_window = np.zeros(n_fft)
    causal_window[0] = 1.0
    causal_window[1:n_half] = 2.0
    if n_fft % 2 == 0:
        causal_window[n_half] = 1.0

    min_phase_cepstrum = cepstrum * causal_window
    min_phase_spectrum = np.exp(np.fft.fft(min_phase_cepstrum))
    correction_filter = np.fft.ifft(min_phase_spectrum).real

    # Step 8: Truncate to desired length with fade-out
    correction_filter = correction_filter[:n_taps]
    fade_out_len = n_taps // 20  # 5% fade-out
    fade = dsp_utils.fade_window(n_taps, 0, fade_out_len)
    correction_filter *= fade

    # Step 9: Post-output D-009 re-clip. Cepstral synthesis and
    # truncation+windowing can push magnitude above the clipped design.
    # Re-clip the final FIR's rfft magnitude while preserving phase.
    margin_linear = dsp_utils.db_to_linear(margin_db)
    out_spectrum = np.fft.rfft(correction_filter)
    out_mag = np.abs(out_spectrum)
    exceed = out_mag > margin_linear
    if np.any(exceed):
        out_phase = np.angle(out_spectrum)
        out_mag[exceed] = margin_linear
        correction_filter = np.fft.irfft(
            out_mag * np.exp(1j * out_phase), n=len(correction_filter),
        )

    return correction_filter


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
    fir = generate_correction_filter(
        normalized, target_curve_name=target_curve, n_taps=n_taps, sr=sr,
        target_phon=target_phon, reference_phon=reference_phon,
        max_cut_db=max_cut_db)
    return CorrectionFilter(fir=fir, reference_level_db=level_db, ref_band_hz=band)
