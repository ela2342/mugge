"""
Venue-driven room correction pipeline (US-174b).

Pure orchestration: measured acoustic IRs + venue config + speaker
profile in, the venue's WAV set + delays + a report out. No printing, no
argparse; file I/O only in the explicit load_* / write_* helpers.

Per speaker channel:

    IR -> normalize_ir_level (median, passband) -> generate_correction_filter
       (cut-only, capped) -> generate_profile_filters (crossover x correction
       x subsonic HPF, D-009 clip, min-phase) -> venue coefficient filename

Channels whose venue coefficients are dirac.wav (spare, HP, IEM) get an
exact unit impulse.

Channel mapping (Architect, 2026-10-25): a venue channel key starts with
its 1-based channel number ("3_sub1_lp"); a profile speaker's ``channel``
is 0-based. Venue channel N+1 belongs to profile channel N. Any ambiguity
fails closed with ValueError.

Sat/sub level balance is NOT applied (AE, S-012): the correction only
shapes each channel. The measured balance is reported as a recommended
gain delta for the operator.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import yaml

from . import dsp_utils
from . import time_align
from .correction import generate_correction_filter, normalize_ir_level
from .export import export_filter
from .generate_profile_filters import generate_profile_filters


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
DEFAULT_N_TAPS = 16384
DIRAC_FILENAME = "dirac.wav"
DEFAULT_IDENTITIES_DIR = (
    Path(__file__).resolve().parents[3] / "configs" / "speakers" / "identities"
)

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
class ChannelAssignment:
    """One venue output channel and where its coefficients come from."""

    number: int                   # 1-based venue channel number
    venue_key: str                # e.g. "3_sub1_lp"
    coefficients: str             # WAV filename from the venue config
    speaker_key: Optional[str]    # profile speaker, None for dirac channels


@dataclass
class VenueBundle:
    """A venue config plus the speaker profile and identities it uses."""

    name: str
    venue: dict
    profile: dict
    identities: Dict[str, dict]
    channels: List[ChannelAssignment]

    @property
    def speaker_files(self) -> Dict[str, str]:
        """Profile speaker key -> coefficient filename."""
        return {c.speaker_key: c.coefficients for c in self.channels
                if c.speaker_key is not None}

    def expected_files(self) -> Dict[str, str]:
        """Filename -> kind ('fir' or 'dirac'), for verify.run_venue_checks."""
        files = {c.coefficients: "fir" for c in self.channels if c.speaker_key}
        if any(c.speaker_key is None for c in self.channels):
            files[DIRAC_FILENAME] = "dirac"
        return files

    def mandatory_hpf_by_file(self) -> Dict[str, float]:
        """Filename -> mandatory HPF (Hz) for channels whose identity has one."""
        result = {}
        for spk_key, filename in self.speaker_files.items():
            identity = self.identities.get(self.profile["speakers"][spk_key]["identity"], {})
            hpf = identity.get("mandatory_hpf_hz")
            if hpf is not None:
                result[filename] = float(hpf)
        return result


@dataclass
class VenueFilterResult:
    """Output of generate_venue_filters()."""

    filters: Dict[str, np.ndarray]                 # filename -> FIR
    corrections: Dict[str, np.ndarray]             # speaker key -> correction FIR
    reference_levels_db: Dict[str, float]          # speaker key -> measured level
    recommended_gain_delta_db: Dict[str, float]    # speaker key -> suggestion, never applied
    delays_s: Dict[str, float]                     # speaker key -> delay compensation
    delays_samples: Dict[str, int]
    notes: List[str] = field(default_factory=list)


def _channel_number(venue_key: str) -> int:
    prefix = venue_key.split("_", 1)[0]
    if not prefix.isdigit():
        raise ValueError(
            f"venue channel key {venue_key!r} does not start with a channel number")
    return int(prefix)


def build_channel_map(venue: dict, profile: dict) -> List[ChannelAssignment]:
    """
    Map venue output channels to profile speakers.

    Raises ValueError if a profile channel matches zero or several venue
    keys, if a profile speaker would get dirac.wav, or if a venue key with
    a non-dirac coefficients file has no profile speaker.
    """
    venue_channels = venue.get("channels") or {}
    by_number: Dict[int, List[str]] = {}
    for key in venue_channels:
        by_number.setdefault(_channel_number(key), []).append(key)

    speaker_by_number: Dict[int, str] = {}
    for spk_key, spk_cfg in (profile.get("speakers") or {}).items():
        if "channel" not in spk_cfg:
            raise ValueError(f"profile speaker {spk_key!r} has no channel")
        number = int(spk_cfg["channel"]) + 1
        keys = by_number.get(number, [])
        if len(keys) != 1:
            raise ValueError(
                f"profile speaker {spk_key!r} (channel {number - 1}) matches "
                f"{len(keys)} venue channel keys: {keys}")
        if number in speaker_by_number:
            raise ValueError(
                f"profile speakers {speaker_by_number[number]!r} and {spk_key!r} "
                f"share channel {number - 1}")
        speaker_by_number[number] = spk_key

    assignments = []
    for key, cfg in sorted(venue_channels.items(), key=lambda kv: _channel_number(kv[0])):
        number = _channel_number(key)
        coeffs = (cfg or {}).get("coefficients")
        if not coeffs:
            raise ValueError(f"venue channel {key!r} has no coefficients file")
        spk_key = speaker_by_number.get(number)
        if spk_key is None and coeffs != DIRAC_FILENAME:
            raise ValueError(
                f"venue channel {key!r} expects {coeffs!r} but no profile "
                f"speaker uses channel {number - 1}")
        if spk_key is not None and coeffs == DIRAC_FILENAME:
            raise ValueError(
                f"profile speaker {spk_key!r} maps to venue channel {key!r}, "
                f"which is a dirac passthrough")
        assignments.append(ChannelAssignment(number, key, coeffs, spk_key))

    filenames = [a.coefficients for a in assignments if a.speaker_key]
    if len(set(filenames)) != len(filenames):
        raise ValueError(f"two speaker channels share a coefficients file: {filenames}")
    return assignments


def load_venue_bundle(venue_path, speaker_profile_path, identities_dir=None) -> VenueBundle:
    """Load a venue config, its speaker profile and the identities it names."""
    identities_dir = Path(identities_dir) if identities_dir else DEFAULT_IDENTITIES_DIR
    with open(venue_path) as f:
        venue = yaml.safe_load(f)
    with open(speaker_profile_path) as f:
        profile = yaml.safe_load(f)

    identities = {}
    for spk_key, spk_cfg in (profile.get("speakers") or {}).items():
        name = spk_cfg.get("identity")
        if not name:
            raise ValueError(f"profile speaker {spk_key!r} has no identity")
        if name not in identities:
            with open(identities_dir / f"{name}.yml") as f:
                identities[name] = yaml.safe_load(f)

    return VenueBundle(
        name=venue.get("name") or Path(venue_path).stem,
        venue=venue,
        profile=profile,
        identities=identities,
        channels=build_channel_map(venue, profile),
    )


def reference_band(bundle: VenueBundle, speaker_key: str):
    """Level reference band for a speaker (by its filter_type)."""
    filter_type = bundle.profile["speakers"][speaker_key].get("filter_type", "highpass")
    if filter_type not in REFERENCE_BANDS_HZ:
        raise ValueError(
            f"no level reference band for filter_type {filter_type!r} ({speaker_key})")
    return REFERENCE_BANDS_HZ[filter_type]


def generate_venue_filters(
    bundle: VenueBundle,
    acoustic_irs: Dict[str, np.ndarray],
    n_taps: int = DEFAULT_N_TAPS,
    sr: int = SAMPLE_RATE,
    max_cut_db: float = MAX_CUT_DB,
) -> VenueFilterResult:
    """
    Generate every coefficient file a venue expects.

    Parameters
    ----------
    acoustic_irs : dict
        Profile speaker key -> measured IR at the listening position
        (one sweep per channel, AE: per-channel sequencing is mandatory).
    """
    speakers = bundle.profile.get("speakers") or {}
    missing = sorted(set(speakers) - set(acoustic_irs))
    extra = sorted(set(acoustic_irs) - set(speakers))
    if missing or extra:
        raise ValueError(f"IRs do not match profile speakers: missing {missing}, extra {extra}")

    target_curve = bundle.profile.get("target_curve", "flat")
    corrections, levels = {}, {}
    for spk_key in speakers:
        normalized, levels[spk_key] = normalize_ir_level(
            acoustic_irs[spk_key], reference_band(bundle, spk_key), sr=sr)
        corrections[spk_key] = generate_correction_filter(
            normalized, target_curve_name=target_curve, n_taps=n_taps, sr=sr,
            max_cut_db=max_cut_db)

    combined = generate_profile_filters(
        bundle.profile, bundle.identities, correction_filters=corrections,
        n_taps=n_taps, sr=sr)

    filters = {bundle.speaker_files[k]: fir for k, fir in combined.items()}
    if any(c.speaker_key is None for c in bundle.channels):
        dirac = np.zeros(n_taps)
        dirac[0] = 1.0
        filters[DIRAC_FILENAME] = dirac

    delays_s = time_align.compute_delays(acoustic_irs, sr=sr)
    quietest = min(levels.values())
    return VenueFilterResult(
        filters=filters,
        corrections=corrections,
        reference_levels_db=levels,
        recommended_gain_delta_db={k: quietest - v for k, v in levels.items()},
        delays_s=delays_s,
        delays_samples=time_align.delays_to_samples(delays_s, sr=sr),
    )


def write_venue_filters(result: VenueFilterResult, output_dir, n_taps=DEFAULT_N_TAPS,
                        sr=SAMPLE_RATE) -> Dict[str, str]:
    """Export every filter under its venue filename. Returns filename -> path."""
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    for filename, fir in sorted(result.filters.items()):
        path = os.path.join(output_dir, filename)
        export_filter(fir, path, n_taps=n_taps, sr=sr)
        paths[filename] = path
    return paths


def write_delays_yaml(result: VenueFilterResult, bundle: VenueBundle, path) -> dict:
    """
    Write measured delays and level suggestions per venue channel.

    The venue config is not touched; the operator (or 174d) applies the
    values. Returns the written mapping.
    """
    channels = {}
    for c in bundle.channels:
        if c.speaker_key is None:
            continue
        k = c.speaker_key
        channels[c.venue_key] = {
            "speaker": k,
            "delay_ms": round(float(result.delays_s[k]) * 1000.0, 4),
            "delay_samples": int(result.delays_samples[k]),
            "reference_level_db": round(float(result.reference_levels_db[k]), 2),
            "recommended_gain_delta_db": round(float(result.recommended_gain_delta_db[k]), 2),
        }
    data = {
        "venue": bundle.name,
        "note": ("Measured values, NOT applied. recommended_gain_delta_db is a "
                 "suggestion on top of the venue gain_db (S-012)."),
        "channels": channels,
    }
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return data
