"""
Venue-driven room correction pipeline (US-174b).

Pure orchestration: measured acoustic IRs + venue config + speaker
profile in, the venue's WAV set + delays + a report out. No printing, no
argparse; file I/O only in the explicit load_* / write_* helpers and in
the staged publish (staged_outputs / publish_venue_outputs).

Per speaker channel:

    IR -> correction_from_measurement (normalize_ir_level, median, passband
       -> generate_correction_filter, cut-only, capped) -> generate_profile_filters
       (crossover x correction x subsonic HPF, D-009 clip, min-phase)
       -> uniform D-009 trim across all speaker channels (F-262 S5)
       -> venue coefficient filename

The gate is verify.run_correction_gate() (F-262 S6): run_venue_checks()
plus a closed-loop check of each correction on its measured IR.

Channels whose venue coefficients are dirac.wav (spare, HP, IEM) get an
exact unit impulse.

Channel mapping (Architect, 2026-10-25): a venue channel key starts with
its 1-based channel number ("3_sub1_lp"); a profile speaker's ``channel``
is 0-based. Venue channel N+1 belongs to profile channel N. Any ambiguity
fails closed with ValueError.

Sat/sub level balance is NOT applied (AE, S-012): the correction only
shapes each channel. The measured balance is reported as a recommended
gain delta for the operator.

Output staging (F-399, Architect + AD): outputs are written into a
``.rc-staging-*`` dir inside the output dir, verified there, and published
only on commit. Without a commit (failed gate, exception, interrupt)
the output dir is left as it was. Publish order: SIMULATED marker
(simulated runs) -> old delays.yml removed -> stale combined_*.wav
removed (never dirac.wav) -> WAVs -> delays.yml last -> stale SIMULATED
removed (real runs). Every step is fsynced. A simulated set is refused
if the output dir resolves to deploy.DEFAULT_COEFFS_DIR. So "delays.yml present" means the set next
to it was verified; a crash mid-publish can leave a mixed WAV set, but
never with a delays.yml, and SIMULATED is present whenever any simulated
file may be. The atomic directory swap is US-174d.

Consumers (US-174c/d deploy) treat a set as NOT deployable if SIMULATED
is present, or delays.yml is missing, unparsable, or lacks
``simulated: false``. Deploy copies only the top-level expected files
and never recurses into the output dir (a SIGKILL can leave a
``.rc-staging-*`` dir behind). Concurrent runs on one output dir are not
supported.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import yaml

from . import deploy, dsp_utils
from . import time_align
from .combine import uniform_d009_trim
# REFERENCE_BANDS_HZ, MAX_CUT_DB and reference_band live in correction.py
# since F-262; re-exported here for existing importers.
from .correction import (  # noqa: F401
    MAX_CUT_DB,
    REFERENCE_BANDS_HZ,
    CorrectionFilter,
    correction_from_measurement,
    reference_band,
    require_correctable,
)
from .export import export_filter
from .generate_profile_filters import generate_profile_filters


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
DEFAULT_N_TAPS = 16384
DIRAC_FILENAME = "dirac.wav"
DELAYS_FILENAME = "delays.yml"
SIMULATED_FILENAME = "SIMULATED"
STAGING_PREFIX = ".rc-staging-"
DEFAULT_IDENTITIES_DIR = (
    Path(__file__).resolve().parents[3] / "configs" / "speakers" / "identities"
)


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
    # F-262 S5: uniform trim applied to every speaker filter (0.0 or negative).
    d009_trim_db: float = 0.0
    # F-384 q4: speaker key -> D-009 scalar step 9 applied to its correction.
    d009_scalar_db: Dict[str, float] = field(default_factory=dict)
    # F-262 S6: filename -> (measured IR, CorrectionFilter, speaker dict),
    # for verify.run_correction_gate().
    closed_loop_inputs: Dict[str, Tuple[np.ndarray, CorrectionFilter, dict]] = field(
        default_factory=dict)


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

    require_correctable(speakers)
    target_curve = bundle.profile.get("target_curve", "flat")
    shaped = {
        spk_key: correction_from_measurement(
            acoustic_irs[spk_key], spk_cfg, target_curve=target_curve,
            n_taps=n_taps, sr=sr, max_cut_db=max_cut_db)
        for spk_key, spk_cfg in speakers.items()
    }
    corrections = {k: c.fir for k, c in shaped.items()}
    levels = {k: c.reference_level_db for k, c in shaped.items()}

    combined = generate_profile_filters(
        bundle.profile, bundle.identities, correction_filters=shaped,
        n_taps=n_taps, sr=sr)

    combined, trim_db = uniform_d009_trim(combined)
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
        d009_trim_db=trim_db,
        d009_scalar_db={k: c.d009_scalar_db for k, c in shaped.items()},
        closed_loop_inputs={
            bundle.speaker_files[k]: (np.asarray(acoustic_irs[k], dtype=np.float64),
                                      shaped[k], speakers[k])
            for k in speakers},
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


def write_delays_yaml(result: VenueFilterResult, bundle: VenueBundle, path, *,
                      simulated_scenario) -> dict:
    """
    Write measured delays and level suggestions per venue channel.

    The venue config is not touched; the operator (or 174d) applies the
    values. ``simulated_scenario`` is required: the room scenario name for
    simulated measurements, None for real ones. ``simulated`` is always
    written explicitly (AD, F-399). Returns the written mapping.
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
        "simulated": simulated_scenario is not None,
        "scenario": None if simulated_scenario is None else str(simulated_scenario),
        "note": ("Measured values, NOT applied. recommended_gain_delta_db is a "
                 "suggestion on top of the venue gain_db (S-012)."),
        "channels": channels,
    }
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return data


def is_deployable_name(filename: str) -> bool:
    """Filenames a coeffs dir would load: combined_*.wav and dirac.wav."""
    return filename == DIRAC_FILENAME or _is_combined_name(filename)


def _is_combined_name(filename: str) -> bool:
    return filename.startswith("combined_") and filename.endswith(".wav")


def _refuse_simulated_into_coeffs(output_dir, simulated_scenario):
    # Architect + AD (F-399): a simulated set never goes into the coeffs dir.
    if simulated_scenario is not None and (
            os.path.realpath(output_dir) == os.path.realpath(deploy.DEFAULT_COEFFS_DIR)):
        raise ValueError(
            f"refusing to publish simulated outputs into the coeffs dir {output_dir}")


def _fsync_file(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _remove(path):
    if os.path.lexists(path):
        os.remove(path)


def publish_venue_outputs(staging_dir, output_dir, *, simulated_scenario=None):
    """
    Move a verified staged set into ``output_dir`` (order in the module doc).

    The staged set must be WAVs plus delays.yml, and delays.yml's
    ``simulated`` field must match ``simulated_scenario``; otherwise
    ValueError before anything in ``output_dir`` changes. Returns the
    published WAV filenames.
    """
    _refuse_simulated_into_coeffs(output_dir, simulated_scenario)
    staged = sorted(os.listdir(staging_dir))
    wavs = [n for n in staged if is_deployable_name(n)]
    other = set(staged) - set(wavs) - {DELAYS_FILENAME}
    if DELAYS_FILENAME not in staged or other or not wavs:
        raise ValueError(f"publish: unexpected staged set {staged}")
    with open(os.path.join(staging_dir, DELAYS_FILENAME)) as f:
        staged_delays = yaml.safe_load(f)
    simulated = simulated_scenario is not None
    if not isinstance(staged_delays, dict) or staged_delays.get("simulated") is not simulated:
        raise ValueError("publish: delays.yml 'simulated' does not match this publish")
    for n in staged:
        _fsync_file(os.path.join(staging_dir, n))

    marker = os.path.join(output_dir, SIMULATED_FILENAME)
    if simulated:
        staged_marker = os.path.join(staging_dir, SIMULATED_FILENAME)
        with open(staged_marker, "w") as f:
            f.write(f"simulated room scenario: {simulated_scenario}\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(staged_marker, marker)
    _remove(os.path.join(output_dir, DELAYS_FILENAME))
    # Stale combined_*.wav from a larger earlier set; dirac.wav stays, other
    # channels and the Rule 10 check reference it (AD).
    for n in sorted(os.listdir(output_dir)):
        path = os.path.join(output_dir, n)
        if _is_combined_name(n) and n not in wavs and not os.path.isdir(path):
            os.remove(path)
    _fsync_dir(output_dir)
    for n in wavs:
        os.replace(os.path.join(staging_dir, n), os.path.join(output_dir, n))
    _fsync_dir(output_dir)
    os.replace(os.path.join(staging_dir, DELAYS_FILENAME),
               os.path.join(output_dir, DELAYS_FILENAME))
    _fsync_dir(output_dir)
    if not simulated and os.path.lexists(marker):
        os.remove(marker)
        _fsync_dir(output_dir)
    return wavs


class StagedOutputs:
    """Handle yielded by staged_outputs: write into ``path``, then ``commit()``."""

    def __init__(self, path, output_dir, simulated_scenario):
        self.path = path
        self.output_dir = output_dir
        self.simulated_scenario = simulated_scenario
        self._state = "open"

    def commit(self):
        """Publish the staged set. Only once, and only inside the with block."""
        if self._state != "open":
            raise RuntimeError(f"staged outputs already {self._state}")
        self._state = "committed"
        return publish_venue_outputs(self.path, self.output_dir,
                                     simulated_scenario=self.simulated_scenario)


@contextlib.contextmanager
def staged_outputs(output_dir, *, simulated_scenario=None):
    """
    Staging dir for one run (Architect, F-399). Nothing is published
    unless ``commit()`` is called; the staging dir is always removed.
    """
    _refuse_simulated_into_coeffs(output_dir, simulated_scenario)
    os.makedirs(output_dir, exist_ok=True)
    stage = StagedOutputs(tempfile.mkdtemp(prefix=STAGING_PREFIX, dir=output_dir),
                          output_dir, simulated_scenario)
    try:
        yield stage
    finally:
        if stage._state == "open":
            stage._state = "closed"
        shutil.rmtree(stage.path, ignore_errors=True)
