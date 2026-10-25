"""
Simulated per-channel measurements for a venue profile (US-174b).

For each speaker in a profile: speaker response (speaker_sim, from the
identity) -> room (room_simulator, scenario geometry) -> log sweep ->
recording + measurement noise -> Wiener deconvolution. One sweep per
channel, as on the real system (AE: per-channel sequencing is mandatory).

Ground truth (direct-path distance and arrival sample) comes from the
scenario geometry, NOT from the pipeline's estimators, so tests can
compare the two (QE, P3).

Known limits (Architect, 2026-10-25): one mic position; the room modes
are position-independent biquads. Off-position robustness needs the
position-dependent model of slice 174b-sim.
"""

import os
from dataclasses import dataclass
from typing import Dict

import numpy as np
import yaml

from room_correction import deconvolution, dsp_utils, speaker_sim
from room_correction.sweep import generate_log_sweep

from . import room_simulator


SAMPLE_RATE = dsp_utils.SAMPLE_RATE
SCENARIOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")

# Profile speaker keys -> scenario speaker keys. The scenarios predate the
# profile naming (sat_left/sat_right); they use main_left/main_right.
SCENARIO_SPEAKER_ALIASES = {
    "sat_left": "main_left",
    "sat_right": "main_right",
    "sub1": "sub1",
    "sub2": "sub2",
}

# Measurement noise added to each recorded sweep: RMS in dB re recording
# peak. AE, 2026-10-25: pink (1/f, real rooms are noisy in the bass);
# -60 dB gates every slice-1 AC, -40 dB is run for the report only.
# Fixed seed per channel keeps runs deterministic (QE).
DEFAULT_NOISE_DB = -60.0
DEFAULT_NOISE_COLOR = "pink"
NOISE_COLORS = ("white", "pink")
DEFAULT_SEED = 174
SWEEP_DURATION_S = 3.0
SPEAKER_IR_TAPS = 4096


@dataclass
class SimulatedMeasurement:
    """Simulated measurement of every profile speaker in one scenario."""

    scenario_name: str
    measured_irs: Dict[str, np.ndarray]      # deconvolved from the noisy sweep
    true_paths: Dict[str, np.ndarray]        # speaker * room, as simulated
    distances_m: Dict[str, float]            # direct path, from geometry
    arrival_samples: Dict[str, int]          # direct-path arrival, from geometry


def scenario_path(name_or_path):
    """Resolve a scenario name ('small_club') or a path to a YAML file."""
    if os.path.isfile(name_or_path):
        return name_or_path
    path = os.path.join(SCENARIOS_DIR, f"{name_or_path}.yml")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"no scenario {name_or_path!r} (looked in {SCENARIOS_DIR})")
    return path


def load_scenario(name_or_path):
    with open(scenario_path(name_or_path)) as f:
        return yaml.safe_load(f)


def speed_of_sound(scenario):
    """Same temperature model as room_simulator.generate_room_ir()."""
    return 331.3 + 0.606 * scenario.get("room", {}).get("temperature", 22.0)


def speaker_position(scenario, speaker_key):
    scenario_key = SCENARIO_SPEAKER_ALIASES.get(speaker_key, speaker_key)
    speakers = scenario.get("speakers") or {}
    if scenario_key not in speakers:
        raise KeyError(f"scenario has no speaker {scenario_key!r} (profile key {speaker_key!r})")
    return speakers[scenario_key]["position"]


def measurement_noise(n, color, rng, sr=SAMPLE_RATE):
    """Unit-RMS noise. 'pink' has a 1/f power spectrum (flat below 1 Hz)."""
    if color not in NOISE_COLORS:
        raise ValueError(f"unknown noise color {color!r}, expected one of {NOISE_COLORS}")
    white = rng.randn(n)
    if color == "white":
        return white / np.sqrt(np.mean(white ** 2))
    spectrum = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    spectrum /= np.sqrt(np.maximum(freqs, 1.0))
    pink = np.fft.irfft(spectrum, n=n)
    return pink / np.sqrt(np.mean(pink ** 2))


def true_delays_samples(arrival_samples):
    """Delay compensation implied by the geometry: latest arrival = 0."""
    latest = max(arrival_samples.values())
    return {k: latest - v for k, v in arrival_samples.items()}


def simulate_venue_measurements(profile, scenario, scenario_name="scenario",
                                sr=SAMPLE_RATE, noise_db=DEFAULT_NOISE_DB,
                                seed=DEFAULT_SEED,
                                sweep_duration_s=SWEEP_DURATION_S,
                                noise_color=DEFAULT_NOISE_COLOR):
    """
    Measure every speaker of a profile in a simulated scenario.

    Parameters
    ----------
    profile : dict
        Speaker profile (``speakers`` with ``identity``).
    scenario : dict
        Loaded scenario YAML.
    noise_db : float or None
        Measurement noise RMS, dB re recording peak. None = noiseless.
    noise_color : str
        'pink' (default) or 'white'.
    """
    sweep = generate_log_sweep(duration=sweep_duration_s, sr=sr)
    mic = scenario["microphone"]["position"]
    speed = speed_of_sound(scenario)

    measured, paths, distances, arrivals = {}, {}, {}, {}
    for index, (spk_key, spk_cfg) in enumerate(sorted(profile["speakers"].items())):
        pos = speaker_position(scenario, spk_key)
        spk_ir = speaker_sim.generate_fir_from_identity(
            spk_cfg["identity"], n_taps=SPEAKER_IR_TAPS, sr=sr)
        recording, path_ir = room_simulator.simulate_measurement(
            sweep, pos, mic, scenario, sr=sr, speaker_ir=spk_ir)
        if noise_db is not None:
            rng = np.random.RandomState(seed + index)
            level = dsp_utils.db_to_linear(noise_db) * np.max(np.abs(recording))
            recording = recording + level * measurement_noise(
                len(recording), noise_color, rng, sr=sr)
        measured[spk_key] = deconvolution.deconvolve(recording, sweep, sr=sr)
        paths[spk_key] = path_ir
        distances[spk_key] = float(room_simulator.distance(pos, mic))
        arrivals[spk_key] = int(distances[spk_key] / speed * sr)

    return SimulatedMeasurement(scenario_name, measured, paths, distances, arrivals)
