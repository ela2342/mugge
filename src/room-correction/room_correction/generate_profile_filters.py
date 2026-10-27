"""
Topology-agnostic FIR filter generation from speaker profiles.

Replaces the Bose-specific ``generate_bose_filters.py`` with a pipeline
that works for any topology (2-way, 3-way, 4-way, MEH) by reading the
profile's ``crossover.frequency_hz`` (scalar or list) and each speaker's
``filter_type`` (highpass / lowpass / bandpass).

Pipeline per channel:

    correction (dirac placeholder) x crossover x [subsonic HPF] -> D-009 clip -> min-phase FIR

Output: one WAV file per speaker channel, plus optional verification.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional, Tuple

import numpy as np

from . import dsp_utils
from .combine import combine_filters
from .correction import CorrectionFilter
from .crossover import (
    LINKWITZ_RILEY,
    generate_bandpass_filter,
    generate_crossover_filter,
    generate_subsonic_filter,
    validate_crossover_spec,
)
from .export import export_filter

log = logging.getLogger(__name__)

SAMPLE_RATE = dsp_utils.SAMPLE_RATE
DEFAULT_N_TAPS = 16384
COMBINE_MARGIN_DB = -0.6
DEFAULT_SLOPE_DB_PER_OCT = 48.0


# -- Crossover spec check ---------------------------------------------------

def validate_profile_crossover(profile: dict) -> None:
    """Raise CrossoverSpecError if the profile's crossover cannot be generated.

    Shared by the generator, the speaker editor save and the measurement
    session start (F-374).  Checks ``crossover.type`` (missing means
    Linkwitz-Riley), the crossover slope and every bandpass driver's
    ``high_slope_db_per_oct``.  A profile without a crossover section keeps
    the legacy knee and passes.  A list of crossover sections is checked
    section by section.
    """
    crossover_cfg = profile.get("crossover")
    if crossover_cfg is None:
        return
    sections = crossover_cfg if isinstance(crossover_cfg, list) else [crossover_cfg]
    speakers = profile.get("speakers") or {}
    for section in sections:
        slope = section.get("slope_db_per_oct", DEFAULT_SLOPE_DB_PER_OCT)
        high_slopes = [
            spk.get("high_slope_db_per_oct", slope)
            for spk in speakers.values()
            if isinstance(spk, dict) and spk.get("filter_type") == "bandpass"
        ]
        validate_crossover_spec(
            section.get("type", LINKWITZ_RILEY), slope, *high_slopes)


# -- Crossover frequency helpers -------------------------------------------

def _normalize_crossover_freqs(profile: dict) -> List[float]:
    """Return the crossover frequencies as a sorted list.

    Handles both scalar (2-way) and list (N-way) ``frequency_hz`` values.
    """
    raw = profile.get("crossover", {}).get("frequency_hz")
    if raw is None:
        return []
    if isinstance(raw, (int, float)):
        return [float(raw)]
    return sorted(float(f) for f in raw)


def _resolve_bandpass_edges(
    spk_cfg: dict,
    crossover_freqs: List[float],
) -> Tuple[float, float]:
    """Determine the low and high crossover frequencies for a bandpass driver.

    For a 3-way with ``crossover.frequency_hz: [300, 2000]``:
      - The lowpass driver uses the lowest freq (300)
      - The bandpass driver spans [300, 2000]
      - The highpass driver uses the highest freq (2000)

    For a 4-way with ``crossover.frequency_hz: [80, 500, 3000]``:
      - lowpass at 80
      - bandpass [80, 500]
      - bandpass [500, 3000]
      - highpass at 3000

    This function looks at the speaker's ``crossover_index`` if present,
    otherwise infers position from the channel order among bandpass drivers.
    Falls back to using the full crossover range.
    """
    if len(crossover_freqs) < 2:
        raise ValueError(
            f"Bandpass filter requires at least 2 crossover frequencies, "
            f"got {crossover_freqs}"
        )

    # Explicit edge specification in the speaker config
    bp_low = spk_cfg.get("bandpass_low_hz")
    bp_high = spk_cfg.get("bandpass_high_hz")
    if bp_low is not None and bp_high is not None:
        return (float(bp_low), float(bp_high))

    # Infer from crossover_index: index i means the band between
    # crossover_freqs[i] and crossover_freqs[i+1]
    idx = spk_cfg.get("crossover_index")
    if idx is not None:
        if idx < 0 or idx >= len(crossover_freqs) - 1:
            raise ValueError(
                f"crossover_index {idx} out of range for "
                f"{len(crossover_freqs)} crossover frequencies"
            )
        return (crossover_freqs[idx], crossover_freqs[idx + 1])

    # Fallback: use the full crossover range
    return (crossover_freqs[0], crossover_freqs[-1])


# -- Per-channel crossover generation ---------------------------------------

def _generate_channel_crossover(
    spk_cfg: dict,
    crossover_freqs: List[float],
    slope: float,
    n_taps: int,
    sr: int,
    alignment: Optional[str] = None,
) -> np.ndarray:
    """Generate the appropriate crossover FIR for a single speaker channel.

    *alignment* is passed to the crossover generator: None for the legacy
    knee, ``'linkwitz-riley'`` for LR4/LR8 (F-374).
    """
    filter_type = spk_cfg.get("filter_type", "highpass")

    if filter_type == "bandpass":
        low, high = _resolve_bandpass_edges(spk_cfg, crossover_freqs)
        high_slope = spk_cfg.get("high_slope_db_per_oct", slope)
        return generate_bandpass_filter(
            low_freq=low,
            high_freq=high,
            low_slope_db_per_oct=slope,
            high_slope_db_per_oct=high_slope,
            n_taps=n_taps,
            sr=sr,
            alignment=alignment,
        )

    if filter_type == "highpass":
        freq = crossover_freqs[-1] if crossover_freqs else 80.0
    elif filter_type == "lowpass":
        freq = crossover_freqs[0] if crossover_freqs else 80.0
    else:
        raise ValueError(f"Unknown filter_type '{filter_type}'")

    return generate_crossover_filter(
        filter_type=filter_type,
        crossover_freq=freq,
        slope_db_per_oct=slope,
        n_taps=n_taps,
        sr=sr,
        alignment=alignment,
    )


# -- Channel factors (F-383 C3, D1) ----------------------------------------

class ChannelFactors(NamedTuple):
    """The factors combine_filters() multiplies for one speaker channel."""

    correction: np.ndarray
    crossover: np.ndarray
    subsonic: Optional[np.ndarray]
    filter_type: str


def is_cascade(filter_type: str, subsonic) -> bool:
    """True if the channel is a crossover LP cascaded with a subsonic HPF.

    A bandpass contains the crossover LP, so bandpass + subsonic is a cascade
    too (Architect ace87e0d).  The role comes from the profile filter_type
    and the identity subsonic, never from the WAV.
    """
    return filter_type in ("lowpass", "bandpass") and subsonic is not None


def channel_factors(
    profile: dict,
    identities: dict,
    correction_filters: Optional[Dict[str, CorrectionFilter]] = None,
    n_taps: int = DEFAULT_N_TAPS,
    sr: int = SAMPLE_RATE,
) -> Dict[str, ChannelFactors]:
    """Per speaker key, the factors generate_profile_filters() combines.

    The one source of the factors for both the generator and the
    composition gate (verify.verify_minimum_phase_composition).  Arguments
    and exceptions as for generate_profile_filters().
    """
    validate_profile_crossover(profile)
    crossover_freqs = _normalize_crossover_freqs(profile)
    crossover_cfg = profile.get("crossover")
    slope = (crossover_cfg or {}).get(
        "slope_db_per_oct", DEFAULT_SLOPE_DB_PER_OCT)
    alignment = None if crossover_cfg is None else LINKWITZ_RILEY
    speakers = profile.get("speakers", {})

    if correction_filters is None:
        correction_filters = {}
    for spk_key, value in correction_filters.items():
        if not isinstance(value, CorrectionFilter):
            raise TypeError(
                f"correction for {spk_key!r} is {type(value).__name__}, not a "
                f"CorrectionFilter; build it with correction_from_measurement()")

    # Pre-generate subsonic filters (deduplicated by frequency)
    subsonic_cache: Dict[float, np.ndarray] = {}

    dirac = np.zeros(n_taps)
    dirac[0] = 1.0

    factors: Dict[str, ChannelFactors] = {}

    for spk_key, spk_cfg in speakers.items():
        # 1. Crossover
        xo = _generate_channel_crossover(
            spk_cfg, crossover_freqs, slope, n_taps, sr, alignment,
        )

        # 2. Correction (or dirac placeholder)
        correction = correction_filters[spk_key].fir if spk_key in correction_filters else dirac

        # 3. Subsonic HPF (from identity mandatory_hpf_hz)
        id_name = spk_cfg.get("identity", "")
        identity = identities.get(id_name, {})
        hpf_hz = identity.get("mandatory_hpf_hz")
        subsonic = None
        if hpf_hz is not None:
            if hpf_hz not in subsonic_cache:
                subsonic_cache[hpf_hz] = generate_subsonic_filter(
                    hpf_freq=hpf_hz,
                    slope_db_per_oct=max(slope, 24.0),
                    n_taps=n_taps,
                    sr=sr,
                )
            subsonic = subsonic_cache[hpf_hz]

        factors[spk_key] = ChannelFactors(
            correction, xo, subsonic, spk_cfg.get("filter_type", "highpass"))

    return factors


def composition_inputs_by_file(
    profile: dict,
    identities: dict,
    filenames: Dict[str, str],
    correction_filters: Optional[Dict[str, CorrectionFilter]] = None,
    n_taps: int = DEFAULT_N_TAPS,
    sr: int = SAMPLE_RATE,
) -> Dict[str, Tuple[np.ndarray, ...]]:
    """Filename -> factors, for the cascade channels (is_cascade()) only.

    filenames maps profile speaker key -> exported filename.  The factors
    are recomputed with channel_factors() from the same profile, identities
    and corrections the filters were generated from.  Feeds the
    composition_inputs of verify.run_correction_gate().

    Raises
    ------
    ValueError
        If a filename maps to a speaker key the profile does not have.
    """
    speakers = profile.get("speakers") or {}
    unknown = sorted(k for k in filenames if k not in speakers)
    if unknown:
        raise ValueError(f"filenames for speakers the profile does not have: {unknown}")
    factors = channel_factors(profile, identities, correction_filters, n_taps=n_taps, sr=sr)
    return {
        filenames[k]: (f.correction, f.crossover, f.subsonic)
        for k, f in factors.items()
        if k in filenames and is_cascade(f.filter_type, f.subsonic)
    }


# -- Main pipeline ----------------------------------------------------------

def generate_profile_filters(
    profile: dict,
    identities: dict,
    correction_filters: Optional[Dict[str, CorrectionFilter]] = None,
    output_dir: Optional[str] = None,
    n_taps: int = DEFAULT_N_TAPS,
    sr: int = SAMPLE_RATE,
    timestamp: Optional[datetime] = None,
) -> Dict[str, np.ndarray]:
    """Generate combined FIR filters for every speaker in a profile.

    Parameters
    ----------
    profile : dict
        Loaded speaker profile.
    identities : dict
        Mapping of identity names to loaded identity dicts.
    correction_filters : dict, optional
        Per-speaker-key CorrectionFilter from correction_from_measurement().
        If None or a key is missing, a dirac (flat) placeholder is used.
    output_dir : str, optional
        If provided, export WAV files to this directory.
    n_taps : int
        FIR length.
    sr : int
        Sample rate.
    timestamp : datetime, optional
        Embedded in WAV filenames for cache-busting.

    Returns
    -------
    dict
        Mapping of speaker key to combined FIR (np.ndarray).

    Raises
    ------
    TypeError
        If a correction_filters value is not a CorrectionFilter (F-262: a
        bare array, e.g. a raw measured IR, is never a correction).
    CrossoverSpecError
        If ``crossover.type`` is present but not ``'linkwitz-riley'``, or a
        slope is not 24 or 48 dB/oct (see ``validate_profile_crossover``).

    Notes
    -----
    ``crossover.type`` selects the alignment (F-374).  A crossover section
    without ``type`` is Linkwitz-Riley; a profile without a crossover
    section keeps the legacy knee.
    """
    factors = channel_factors(profile, identities, correction_filters, n_taps=n_taps, sr=sr)

    combined_filters: Dict[str, np.ndarray] = {}

    for spk_key, f in factors.items():
        # 4. Combine
        combined = combine_filters(
            correction_filter=f.correction,
            crossover_filter=f.crossover,
            n_taps=n_taps,
            margin_db=COMBINE_MARGIN_DB,
            subsonic_filter=f.subsonic,
        )

        combined_filters[spk_key] = combined

    # 5. Export WAV files if output_dir provided
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        for spk_key, fir in combined_filters.items():
            if timestamp:
                ts = timestamp.strftime("%Y%m%d_%H%M%S")
                filename = f"combined_{spk_key}_{ts}.wav"
            else:
                filename = f"combined_{spk_key}.wav"
            path = os.path.join(output_dir, filename)
            export_filter(fir, path, n_taps=n_taps, sr=sr)

    return combined_filters
