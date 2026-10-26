"""F-262 S3: onset-anchored capture alignment (set A: O1-O4, F1-F5, Q3/Q4).

The capture start is not a time reference. align_capture() finds the direct
sound in the capture itself, cuts [onset - 5 ms, onset + 500 ms], and fails
closed ("capture misaligned") when it can't trust the capture.

Layouts follow the AE/QE Q4 table: the sweep's direct sound is d = 480
samples into the capture, the capture is shifted by L, and the tail after
the sweep is T = 72000 samples. In window iff 240 <= d + L and
d + L + 24000 <= T.
"""

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from room_correction import crossover, deconvolution, dsp_utils
from room_correction.alignment import (
    QUANTUM,
    WINDOW_POST,
    WINDOW_PRE,
    CaptureMisaligned,
    align_capture,
    check_expected_width,
)
from room_correction.sweep import generate_log_sweep, signal_gen_sweep

SR = 48000
D = 480
T = 72000
REPO_ROOT = Path(__file__).resolve().parents[3]
ROOM_SIM = REPO_ROOT / "scripts" / "generate-room-sim-ir.py"


def _session_sweep(duration):
    """The session's sweep: generate_log_sweep at -20 dBFS peak."""
    s = generate_log_sweep(duration, 20.0, 20000.0, SR)
    return s * (dsp_utils.db_to_linear(-20.0) / np.max(np.abs(s)))


def _shifted(response, shift, length):
    """response delayed by shift samples (shift < 0: the capture starts late)."""
    if shift >= 0:
        out = np.concatenate([np.zeros(shift), response, np.zeros(length)])
    else:
        out = np.concatenate([response[-shift:], np.zeros(length)])
    return out[:length]


def _noise(n, level_dbfs, seed):
    return (dsp_utils.db_to_linear(level_dbfs)
            * np.random.default_rng(seed).standard_normal(n))


@pytest.fixture(scope="module")
def room_sim():
    """scripts/generate-room-sim-ir.py, the local-demo room."""
    assert ROOM_SIM.is_file(), f"room sim not found: {ROOM_SIM}"
    spec = importlib.util.spec_from_file_location("room_sim", ROOM_SIM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _room_ir(room_sim, name):
    return np.array(room_sim.generate_room_ir_for_speaker(
        room_sim.CHANNEL_SPEAKERS[name], room_sim.PER_CHANNEL_IR_TAPS,
        room_sim.SUB_MODE_BOOST if name.startswith("sub") else None))


def _direct_sample(room_sim, name):
    d = room_sim.distance(room_sim.CHANNEL_SPEAKERS[name], room_sim.MIC_POS)
    return int(d / room_sim.SPEED_OF_SOUND * SR)


# ---------------------------------------------------------------------------
# Room sim (F1)
# ---------------------------------------------------------------------------

class TestRoomSimCausality:
    """Nothing reaches the mic before the direct sound."""

    @pytest.mark.parametrize("name", ["left", "right", "sub1", "sub2"])
    def test_ir_is_zero_before_direct_arrival(self, room_sim, name):
        ir = _room_ir(room_sim, name)
        direct = _direct_sample(room_sim, name)
        assert np.all(ir[:direct] == 0.0), (
            f"{name}: non-zero before the direct sound at {direct}: first at "
            f"{int(np.nonzero(ir)[0][0])}")
        assert ir[direct] != 0.0


# ---------------------------------------------------------------------------
# Onset rule (O1-O4)
# ---------------------------------------------------------------------------

class TestOnsetOnRoomSim:
    """O4(a), re-pinned by F1: the onset on the port-ref h is the direct sound."""

    @pytest.mark.parametrize("name,onset", [
        ("left", 506), ("right", 506), ("sub1", 465), ("sub2", 465)])
    def test_onset_pin(self, room_sim, name, onset):
        port = signal_gen_sweep(5.0, SR, level_dbfs=-20.0)
        rec = _shifted(np.convolve(port, 0.06 * _room_ir(room_sim, name)),
                       0, len(port) + T)
        aligned = align_capture(rec, _session_sweep(5.0), played=port)
        assert aligned.played_onset == onset
        # The global maximum is a later reflection + modes, not the onset.
        h, zero = deconvolution.deconvolve_lags(rec, port)
        assert int(np.argmax(np.abs(h))) - zero != onset
        # F1: the session-ref onset is checked only under (iii).
        assert abs(aligned.onset - aligned.played_onset) <= QUANTUM

    @pytest.mark.parametrize("onset", [58176, 63552, 63552 + QUANTUM])
    def test_late_direct_sound_passes(self, room_sim, onset):
        """b64aad93 (a): direct sound at 1212 / 1324 ms, production tail.

        F4: the session records 2 s after the sweep (96000 samples).
        """
        port = signal_gen_sweep(5.0, SR, level_dbfs=-20.0)
        sweep = _session_sweep(5.0)
        path = 0.06 * _room_ir(room_sim, "left")
        n = len(port) + 96000
        base = align_capture(_shifted(np.convolve(port, path), 0, n),
                             sweep, played=port)
        aligned = align_capture(_shifted(np.convolve(port, path),
                                         onset - 506, n),
                                sweep, played=port)
        assert aligned.played_onset == onset
        assert aligned.onset == onset
        assert aligned.window_margin >= 0
        assert (np.max(np.abs(aligned.ir - base.ir))
                <= 1e-6 * np.max(np.abs(base.ir)))

    def test_capture_starting_late_trips_i(self, room_sim):
        """F5: -4800 puts the onset at a negative lag; criterion (i)."""
        port = signal_gen_sweep(5.0, SR, level_dbfs=-20.0)
        rec = _shifted(np.convolve(port, 0.06 * _room_ir(room_sim, "left")),
                       -4800, len(port) + T)
        with pytest.raises(CaptureMisaligned) as exc:
            align_capture(rec, _session_sweep(5.0), played=port)
        assert "capture misaligned" in str(exc.value)
        assert "(i)" in str(exc.value)
        assert exc.value.criterion == "i"


class TestOnsetRule:
    """O4(b)-(e) on synthetic paths: direct sound at 480, reflection at 1080."""

    @staticmethod
    def _capture(path, sweep):
        return _shifted(np.convolve(sweep, path), 0, len(sweep) + T)

    @pytest.mark.parametrize("louder_db,onset", [
        (3.0, 480),     # (b) a louder reflection: still the direct sound
        (10.0, 480),    # (c) within 12 dB: the direct sound
        (13.0, 1080),   # (c) direct sound 13 dB down: the reflection
    ])
    def test_reflection_louder_than_direct(self, louder_db, onset):
        sweep = _session_sweep(1.0)
        path = np.zeros(2000)
        path[480] = 0.5
        path[1080] = 0.5 * dsp_utils.db_to_linear(louder_db)
        assert align_capture(self._capture(path, sweep), sweep).onset == onset

    def test_no_arrival_above_floor_trips_ii(self):
        """(d) Noise only: no arrival 30 dB above the pre-onset floor."""
        sweep = _session_sweep(1.0)
        rec = _noise(len(sweep) + T, -40.0, seed=1)
        with pytest.raises(CaptureMisaligned) as exc:
            align_capture(rec, sweep)
        assert exc.value.criterion == "ii"
        assert "capture misaligned: (ii)" in str(exc.value)

    @pytest.mark.parametrize("offset,ok", [
        (QUANTUM, True), (QUANTUM + 1, False), (1000, False)])
    def test_port_and_session_onsets_disagree_trips_iii(self, offset, ok):
        """(e) Session and played-reference onsets more than a quantum apart."""
        sweep = _session_sweep(1.0)
        path = np.zeros(1000)
        path[480] = 1.0
        rec = self._capture(path, sweep)
        played = np.concatenate([np.zeros(offset), sweep])
        if ok:
            aligned = align_capture(rec, sweep, played=played)
            assert aligned.onset - aligned.played_onset == offset
        else:
            with pytest.raises(CaptureMisaligned) as exc:
                align_capture(rec, sweep, played=played)
            assert exc.value.criterion == "iii"


# ---------------------------------------------------------------------------
# Q4 lag / noise matrix, Q3 filter identity
# ---------------------------------------------------------------------------

def _q4_capture(sweep, lag, noise_dbfs=None, seed=0):
    n = len(sweep) + T
    rec = _shifted(sweep, D + lag, n)
    if noise_dbfs is not None:
        rec = rec + _noise(n, noise_dbfs, seed)
    return rec


def _smoothed_db(ir):
    n_fft = 65536
    mag = np.abs(np.fft.rfft(ir, n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / SR)
    band = (freqs >= 20.0) & (freqs <= 20000.0)
    return dsp_utils.linear_to_db(
        dsp_utils.fractional_octave_smooth(mag[band], freqs[band], 6))


@pytest.fixture(scope="module")
def q4_sweep():
    return _session_sweep(5.0)


@pytest.fixture(scope="module")
def q4_base(q4_sweep):
    return align_capture(_q4_capture(q4_sweep, 0), q4_sweep)


PASS_LAGS = [0, -100, 24000, 47000, -WINDOW_PRE, 47520]
FAIL_LAGS = [
    (-241, "before the 240-sample window start"),
    (-300, "before the 240-sample window start"),
    (47521, "window overruns the capture"),
    (60000, "window overruns the capture"),
    (-4800, "onset at lag -4320"),
]


class TestQ4NoiseFree:

    def test_layout_matches_rule(self):
        """The boundary rows sit exactly on the window rule."""
        assert D + (-WINDOW_PRE) == WINDOW_PRE
        assert D + 47520 + WINDOW_POST == T

    @pytest.mark.parametrize("lag", PASS_LAGS)
    def test_pass_rows_match_lag_zero(self, q4_sweep, q4_base, lag):
        """Q3: the IR at any in-window lag equals the IR at lag 0."""
        aligned = align_capture(_q4_capture(q4_sweep, lag), q4_sweep)
        assert aligned.onset == D + lag
        assert len(aligned.ir) == WINDOW_PRE + WINDOW_POST
        assert (np.max(np.abs(aligned.ir - q4_base.ir))
                <= 1e-6 * np.max(np.abs(q4_base.ir)))

    @pytest.mark.parametrize("lag,message", FAIL_LAGS)
    def test_fail_rows(self, q4_sweep, lag, message):
        with pytest.raises(CaptureMisaligned) as exc:
            align_capture(_q4_capture(q4_sweep, lag), q4_sweep)
        assert exc.value.criterion == "i"
        assert str(exc.value).startswith("capture misaligned: (i)")
        assert message in str(exc.value)

    def test_deterministic(self, q4_sweep):
        rec = _q4_capture(q4_sweep, 24000)
        a = align_capture(rec, q4_sweep)
        b = align_capture(rec, q4_sweep)
        assert np.array_equal(a.ir, b.ir)
        assert a.log == b.log


class TestQ4WithNoise:
    """Gross rows plus the +-10 pairs; the +-1 pairs are noise-free only."""

    @pytest.mark.parametrize("noise_dbfs,tol_db", [
        (-90.0, 0.2), (-60.0, 0.5), (-40.0, 1.0)])
    @pytest.mark.parametrize("lag", [-100, 24000, 47000, -230, 47510])
    def test_pass_rows(self, q4_sweep, noise_dbfs, tol_db, lag):
        base = align_capture(_q4_capture(q4_sweep, 0, noise_dbfs, seed=1),
                             q4_sweep)
        aligned = align_capture(_q4_capture(q4_sweep, lag, noise_dbfs, seed=2),
                                q4_sweep)
        assert aligned.onset == D + lag
        diff = np.max(np.abs(_smoothed_db(aligned.ir) - _smoothed_db(base.ir)))
        assert diff <= tol_db, f"1/6-oct response differs by {diff:.3f} dB"

    @pytest.mark.parametrize("noise_dbfs", [-90.0, -60.0, -40.0])
    @pytest.mark.parametrize("lag", [-250, -300, 47530, 60000])
    def test_fail_rows(self, q4_sweep, noise_dbfs, lag):
        with pytest.raises(CaptureMisaligned) as exc:
            align_capture(_q4_capture(q4_sweep, lag, noise_dbfs, seed=2),
                          q4_sweep)
        assert exc.value.criterion == "i"


# ---------------------------------------------------------------------------
# The 1.5x width rule, where the path is known (F3)
# ---------------------------------------------------------------------------

class TestExpectedWidth:

    def test_sub_fir_filtered_capture_passes(self):
        """b64aad93 (b): a capture through a sub lowpass FIR doesn't fire."""
        sweep = _session_sweep(1.0)
        lp = crossover.generate_crossover_filter(
            "lowpass", crossover_freq=80.0, n_taps=16384)
        n = len(sweep) + T
        rec = _shifted(np.convolve(sweep, lp), D, n) + _noise(n, -100.0, 3)
        measured, expected = check_expected_width(rec, sweep, lp)
        assert measured <= 1.5 * expected

    def test_dirac_capture_passes(self):
        sweep = _session_sweep(1.0)
        rec = _shifted(sweep, D, len(sweep) + T)
        measured, expected = check_expected_width(rec, sweep, np.array([1.0]))
        assert measured == pytest.approx(expected, rel=1e-6)

    @pytest.mark.parametrize("smear", ["law", "boxcar"])
    def test_smeared_capture_fails(self, smear):
        """b64aad93 (c): a capture smeared beyond 1.5x is refused."""
        sweep = _session_sweep(1.0)
        if smear == "law":
            played = _session_sweep(1.01)   # a sweep-law mismatch
        else:
            played = np.convolve(sweep, np.ones(48) / 48.0)  # 1 ms smear
        rec = _shifted(played, D, len(sweep) + T)
        with pytest.raises(CaptureMisaligned) as exc:
            check_expected_width(rec, sweep, np.array([1.0]))
        assert exc.value.criterion == "iv"


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

class TestSignalGenSweep:

    def test_length_and_level(self):
        s = signal_gen_sweep(2.0, SR, level_dbfs=-20.0)
        assert len(s) == 2 * SR
        assert np.max(np.abs(s)) == pytest.approx(0.1, rel=1e-3)

    def test_generator_law(self):
        """Phase is the running sum of 2*pi*f_inst/sr, starting at f_start."""
        s = signal_gen_sweep(1.0, SR)
        assert s[0] == pytest.approx(np.sin(2.0 * np.pi * 20.0 / SR))
        rate = np.log(20000.0 / 20.0) / SR
        phase2 = 2.0 * np.pi * 20.0 * (1.0 + np.exp(rate)) / SR
        assert s[1] == pytest.approx(np.sin(phase2))

    def test_differs_from_session_sweep(self):
        """Not generate_log_sweep: no fades, a different phase law."""
        a = signal_gen_sweep(1.0, SR)
        b = generate_log_sweep(1.0, 20.0, 20000.0, SR)
        assert len(a) == len(b)
        assert not np.allclose(a, b / np.max(np.abs(b)), atol=1e-3)


class TestDeconvolveToCaptureEnd:

    def test_none_keeps_every_causal_lag(self):
        sweep = _session_sweep(1.0)
        rec = _shifted(sweep, 60000, len(sweep) + T)
        ir = deconvolution.deconvolve(rec, sweep, ir_duration_s=None)
        assert len(ir) == len(rec)
        assert int(np.argmax(np.abs(ir))) == 60000

    def test_default_still_cuts_at_one_second(self):
        sweep = _session_sweep(1.0)
        rec = _shifted(sweep, 60000, len(sweep) + T)
        assert len(deconvolution.deconvolve(rec, sweep)) == SR

    def test_lags_cover_negative_range(self):
        sweep = _session_sweep(1.0)
        rec = _shifted(sweep, -1000, len(sweep) + T)
        h, zero = deconvolution.deconvolve_lags(rec, sweep)
        assert zero == len(sweep) - 1
        assert len(h) == len(sweep) - 1 + len(rec)
        assert int(np.argmax(np.abs(h))) - zero == -1000
