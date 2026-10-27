"""Unit tests for the mixxx-substitute --tone stimulus (F-394 Q1-5).

The service-integration mute and level tests derive their expected levels
from TONE_FREQ_HZ / TONE_PEAK_DBFS, so the generator itself must be right:
peak level, frequency, phase continuity across process blocks, and the
channel map (ch 1-2 tone, ch 3-8 exactly 0).
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "scripts" / "mixxx-substitute.py"

RATE = 48000


@pytest.fixture(scope="module")
def sub():
    spec = importlib.util.spec_from_file_location("mixxx_substitute", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _blocks(sub, sizes, start=0):
    """Concatenate tone blocks of the given sizes, as the callback would."""
    out, frame = [], start
    for n in sizes:
        out.append(sub.tone_block(frame, n, rate=RATE))
        frame += n
    return np.concatenate(out, axis=1)


def test_constants_match_ae_ruling(sub):
    assert sub.TONE_FREQ_HZ == 1000
    assert sub.TONE_PEAK_DBFS == -20.0


def test_shape_and_dtype(sub):
    block = sub.tone_block(0, 256, rate=RATE)
    assert block.shape == (8, 256)
    assert block.dtype == np.float32


def test_peak_level(sub):
    block = sub.tone_block(0, RATE, rate=RATE)
    peak_db = 20 * np.log10(np.max(np.abs(block[0])))
    # 48 samples per cycle hit the crest exactly (AE Q1 V1: within 0.02 dB).
    assert abs(peak_db - sub.TONE_PEAK_DBFS) < 0.02


def test_frequency(sub):
    block = sub.tone_block(0, RATE, rate=RATE)
    spectrum = np.abs(np.fft.rfft(block[0]))
    freqs = np.fft.rfftfreq(RATE, 1 / RATE)
    assert freqs[np.argmax(spectrum)] == sub.TONE_FREQ_HZ


def test_channel_map(sub):
    block = sub.tone_block(0, 1024, rate=RATE)
    np.testing.assert_array_equal(block[0], block[1])
    assert np.max(np.abs(block[0])) > 0
    assert not block[2:].any(), "ch 3-8 must be exactly 0"


@pytest.mark.parametrize("sizes", [[256] * 8, [1024, 1024], [100, 37, 999, 1]])
def test_phase_continuous_across_blocks(sub, sizes):
    joined = _blocks(sub, sizes)
    whole = sub.tone_block(0, sum(sizes), rate=RATE)
    np.testing.assert_array_equal(joined, whole)


def test_phase_exact_after_long_run(sub):
    # About 12 h of frames: integer phase reduction keeps the waveform
    # identical to the start, so no drift or click builds up.
    start = 12 * 3600 * RATE
    np.testing.assert_array_equal(
        sub.tone_block(start, 480, rate=RATE),
        sub.tone_block(0, 480, rate=RATE),
    )
