"""Reference Butterworth data for the dsp.js tests (US-179 AC4g/AC5d/E2d).

    python fixtures/butter/generate.py   # rewrites reference.json

scipy.signal.butter(..., output="sos") is the reference design;
sosfilt runs the level-noise chains (full-range 100 Hz-10 kHz, subwoofer
40-200 Hz) over the pink golden for seed 174.
tests/unit/test_butter_fixture.py checks that reference.json is current.
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy import signal

HERE = Path(__file__).resolve().parent
SR = 48000
DESIGNS = [
    # (kind, order, cutoff_hz): the sweep HPF at 0.8 x limit for the
    # declared limit range, and the level-noise band edges.
    ("highpass", 4, 16.0),
    ("highpass", 4, 32.0),
    ("highpass", 4, 400.0),
    ("highpass", 4, 100.0),
    ("lowpass", 4, 10000.0),
    ("highpass", 4, 40.0),
    ("lowpass", 4, 200.0),
    ("highpass", 8, 100.0),
]
PINK_GOLDEN = HERE.parent / "noise" / "pink_seed174_level1.0.f32le"


def sos(kind, order, cutoff):
    return signal.butter(order, cutoff, btype=kind, fs=SR, output="sos")


def reference():
    designs = []
    for kind, order, cutoff in DESIGNS:
        s = sos(kind, order, cutoff)
        impulse = np.zeros(256)
        impulse[0] = 1.0
        designs.append({
            "kind": kind, "order": order, "cutoff_hz": cutoff,
            "sos": s.tolist(),
            "impulse_response": signal.sosfilt(s, impulse).tolist(),
        })
    pink = np.fromfile(PINK_GOLDEN, dtype="<f4").astype(np.float64)

    def chain(low_hz, high_hz):
        sections = np.vstack([sos("highpass", 4, low_hz), sos("lowpass", 4, high_hz)])
        return {
            "seed": 174,
            "band": {"lowHz": low_hz, "highHz": high_hz},
            "source": "noise/" + PINK_GOLDEN.name,
            "output": signal.sosfilt(sections, pink).tolist(),
        }

    return {
        "sample_rate": SR,
        "designs": designs,
        "level_noise": [chain(100.0, 10000.0), chain(40.0, 200.0)],
    }


def render():
    return json.dumps(reference(), indent=1) + "\n"


if __name__ == "__main__":
    (HERE / "reference.json").write_text(render())
    sys.exit(0)
