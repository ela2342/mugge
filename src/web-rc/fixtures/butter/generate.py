"""Reference Butterworth data for the dsp.js tests (US-179 AC4g/AC5d).

    python fixtures/butter/generate.py   # rewrites reference.json

scipy.signal.butter(..., output="sos") is the reference design;
sosfilt runs the level-noise chain over the pink golden for seed 174.
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
    chain = np.vstack([sos("highpass", 4, 100.0), sos("lowpass", 4, 10000.0)])
    return {
        "sample_rate": SR,
        "designs": designs,
        "level_noise": {
            "seed": 174,
            "source": "noise/" + PINK_GOLDEN.name,
            "output": signal.sosfilt(chain, pink).tolist(),
        },
    }


def render():
    return json.dumps(reference(), indent=1) + "\n"


if __name__ == "__main__":
    (HERE / "reference.json").write_text(render())
    sys.exit(0)
