"""webrc_pipeline on native CPython with the real soundfile (US-179).

Captures are simulated: the sweep goes through a room-simulator IR, then
latency and measurement noise are added. The browser runs the same module
under Pyodide with the soundfile shim (tests/browser).

webrc_pipeline is loaded from its path, so src/web-rc/py (which holds the
soundfile shim) never lands on sys.path here.
"""

import ast
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3]
RC = SRC / "room-correction"
sys.path.insert(0, str(RC))

from mock import room_simulator  # noqa: E402
from room_correction import verify  # noqa: E402

SR = 48000
LIMIT_HZ = 40.0
SWEEP_S = 3.0
PRE_ROLL_S = 0.5
LATENCY_S = 0.023


@pytest.fixture(scope="module")
def wp():
    spec = importlib.util.spec_from_file_location(
        "webrc_pipeline", SRC / "web-rc" / "py" / "webrc_pipeline.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _native_constant(path, name):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {path}")


@pytest.mark.parametrize("module, name, mirror", [
    ("room_correction/venue_pipeline.py", "REFERENCE_BANDS_HZ", "REFERENCE_BANDS_HZ"),
    ("room_correction/venue_pipeline.py", "MAX_CUT_DB", "MAX_CUT_DB"),
    ("measure_nearfield.py", "REC_MIN_PEAK_DBFS", "REC_MIN_PEAK_DBFS"),
    ("measure_nearfield.py", "REC_MAX_PEAK_DBFS", "REC_MAX_PEAK_DBFS"),
    ("measure_nearfield.py", "REC_MIN_SNR_DB", "REC_MIN_SNR_DB"),
])
def test_mirrored_constants_match_native(wp, module, name, mirror):
    assert getattr(wp, mirror) == _native_constant(RC / module, name)


def test_dc_ceiling_matches_native(wp):
    # measure_nearfield inlines 0.01 in check_recording_integrity.
    src = (RC / "measure_nearfield.py").read_text()
    assert "if dc_offset > 0.01:" in src
    assert wp.REC_MAX_DC_OFFSET == 0.01


def _room_ir(mode_gain_db=9.0):
    return room_simulator.generate_room_ir(
        [1.0, 1.5, 1.2], [3.5, 2.5, 1.2], [7.0, 5.0, 2.8], wall_absorption=0.4,
        room_modes=[{"frequency": 63.0, "q": 6.0, "gain": mode_gain_db}], sr=SR)


def _capture(sweep, room_ir, seed, gain_db=-20.0, noise_dbfs=-75.0,
             latency_s=LATENCY_S):
    rng = np.random.default_rng(seed)
    pre = int(PRE_ROLL_S * SR)
    lat = int(latency_s * SR)
    total = pre + len(sweep) + SR
    wet = np.convolve(sweep.astype(np.float64) * 10 ** (gain_db / 20), room_ir)
    cap = np.zeros(total)
    end = min(total, pre + lat + len(wet))
    cap[pre + lat:end] = wet[:end - pre - lat]
    cap += rng.standard_normal(total) * 10 ** (noise_dbfs / 20)
    return cap, pre


@pytest.fixture(scope="module")
def sweep(wp):
    return wp.make_sweep(LIMIT_HZ, SWEEP_S)


@pytest.fixture(scope="module")
def run(wp, sweep):
    room = _room_ir()
    cap1, pre = _capture(sweep, room, seed=1)
    cap2, _ = _capture(sweep, room, seed=2)
    ir1, delay1 = wp.ir_from_capture(cap1, sweep, pre)
    ir2, _ = wp.ir_from_capture(cap2, sweep, pre)
    fir, level = wp.build_filter(ir1, LIMIT_HZ)
    wav = wp.filter_wav_bytes(fir)
    return {"ir1": ir1, "ir2": ir2, "delay": delay1, "fir": fir, "wav": wav,
            "room": room}


class TestSweep:
    def test_float32_bounded_length(self, wp, sweep):
        assert sweep.dtype == np.float32
        assert len(sweep) == int(SWEEP_S * SR)
        assert np.max(np.abs(sweep)) <= 1.0

    def test_capped_at_10_s(self, wp):
        assert len(wp.make_sweep(LIMIT_HZ, 30.0)) == 10 * SR

    def test_hpf_below_the_limit(self, wp):
        # 4th-order HPF at 32 Hz: well down at 10 Hz relative to 1 kHz.
        s = wp.make_sweep(20.0, 6.0).astype(np.float64)
        spec = np.abs(np.fft.rfft(s, n=1 << 20))
        f = np.fft.rfftfreq(1 << 20, d=1 / SR)
        at = lambda hz: spec[np.argmin(np.abs(f - hz))]
        assert 20 * np.log10(at(6.0) / at(1000.0)) < -20.0

    def test_fades_in_and_out(self, wp, sweep):
        assert abs(sweep[0]) < 1e-3 and abs(sweep[-1]) < 1e-3


class TestCaptureChecks:
    def test_good_capture_passes(self, wp, sweep):
        cap, pre = _capture(sweep, _room_ir(), seed=3)
        assert wp.check_capture(cap, pre)["ok"]

    def test_clip_rejects(self, wp, sweep):
        cap, pre = _capture(sweep, _room_ir(), seed=3)
        cap[pre + 1000] = 1.0
        r = wp.check_capture(cap, pre)
        assert not r["ok"] and "clipped" in r["issues"][0]
        with pytest.raises(wp.CaptureRejected):
            wp.ir_from_capture(cap, sweep, pre)

    def test_low_snr_rejects(self, wp, sweep):
        cap, pre = _capture(sweep, _room_ir(), seed=3, gain_db=-40.0, noise_dbfs=-45.0)
        r = wp.check_capture(cap, pre)
        assert not r["ok"] and any("SNR" in i for i in r["issues"])

    def test_silence_rejects(self, wp):
        cap = np.random.default_rng(0).standard_normal(5 * SR) * 1e-5
        assert not wp.check_capture(cap, SR // 2)["ok"]

    def test_capture_without_arrival_rejects(self, wp, sweep):
        # Loud noise unrelated to the sweep: passes the level checks but
        # deconvolution finds no arrival where one can be.
        rng = np.random.default_rng(4)
        pre = int(PRE_ROLL_S * SR)
        cap = rng.standard_normal(pre + len(sweep) + SR) * 0.01
        cap[:pre] *= 1e-3
        with pytest.raises(wp.CaptureRejected):
            wp.ir_from_capture(cap, sweep, pre)


class TestAlignment:
    def test_delay_from_deconvolution(self, wp, run):
        direct_s = np.argmax(np.abs(run["room"])) / SR
        assert run["delay"] == pytest.approx(LATENCY_S + direct_s, abs=2 / SR)

    @pytest.mark.parametrize("latency_s", [0.0, 0.004, 0.09])
    def test_latency_independent(self, wp, sweep, latency_s):
        cap, pre = _capture(sweep, _room_ir(), seed=5, latency_s=latency_s)
        _, delay = wp.ir_from_capture(cap, sweep, pre)
        direct_s = np.argmax(np.abs(_room_ir())) / SR
        assert delay == pytest.approx(latency_s + direct_s, abs=2 / SR)


class TestFilter:
    def test_gates_pass_on_download_bytes(self, wp, run):
        name = wp.filter_filename("left")
        assert "browser-generated" in name
        v = wp.verify_wav_bytes(run["wav"], name, LIMIT_HZ)
        assert v["ok"], [r for r in v["results"] if not r["passed"]]
        names = " ".join(r["name"] for r in v["results"])
        for gate in ("D-009", "Format", "WAV Subtype", "Mandatory HPF", "Minimum Phase"):
            assert gate in names, gate

    def test_peak_below_minus_half_db(self, wp, run):
        mag = np.abs(np.fft.rfft(run["fir"], n=1 << 17))
        assert 20 * np.log10(np.max(mag)) <= -0.5

    def test_hpf_gate_uses_0_8_x_limit(self, wp, run):
        name = wp.filter_filename("left")
        v = wp.verify_wav_bytes(run["wav"], name, LIMIT_HZ)
        hpf = [r for r in v["results"] if r["name"].startswith("Mandatory HPF")]
        assert len(hpf) == 1 and hpf[0]["passed"]

    def test_tampered_bytes_fail_closed(self, wp, run):
        name = wp.filter_filename("left")
        raw = bytearray(run["wav"])
        # Push one sample far above 0 dB: D-009 must fail.
        data_at = raw.index(b"data") + 8
        raw[data_at:data_at + 4] = np.float32(8.0).tobytes()
        assert not wp.verify_wav_bytes(bytes(raw), name, LIMIT_HZ)["ok"]

    def test_wav_matches_export_filter_layout(self, wp, run):
        info = verify.sf.info(__import__("io").BytesIO(run["wav"]))
        assert (info.samplerate, info.channels, info.frames, info.subtype) == \
            (SR, 1, 16384, "FLOAT")


class TestHoldout:
    def test_repeatable_captures_pass(self, wp, run):
        r = wp.repeatability(run["ir1"], run["ir2"], LIMIT_HZ)
        assert r["ok"], r["max_abs_db"]

    def test_moved_mic_fails_repeatability(self, wp, sweep, run):
        moved = room_simulator.generate_room_ir(
            [1.0, 1.5, 1.2], [5.0, 1.0, 2.0], [7.0, 5.0, 2.8], wall_absorption=0.4,
            room_modes=[{"frequency": 63.0, "q": 6.0, "gain": 9.0}], sr=SR)
        cap, pre = _capture(sweep, moved, seed=6, gain_db=-30.0)
        ir_moved, _ = wp.ir_from_capture(cap, sweep, pre)
        assert not wp.repeatability(run["ir1"], ir_moved, LIMIT_HZ)["ok"]

    def test_prediction_label_and_verdict(self, wp, run):
        p = wp.predict(run["wav"], run["ir2"], LIMIT_HZ)
        assert p["label"] == (
            "Predicted residual within 3 dB: "
            + ("PASS" if p["passed"] else "FAIL")
            + " — predicted, not measured, unverified until re-measured")
        assert p["predicted_db"].shape == p["measured_db"].shape == p["freqs"].shape

    def test_prediction_passes_for_a_matching_room(self, wp, run):
        assert wp.predict(run["wav"], run["ir2"], LIMIT_HZ)["passed"]

    def test_prediction_fails_for_a_filter_from_another_room(self, wp, sweep, run):
        # Non-vacuous: the 63 Hz filter leaves a 100 Hz mode uncut.
        other = _room_ir(mode_gain_db=0.0) + room_simulator.generate_room_ir(
            [1.0, 1.5, 1.2], [3.5, 2.5, 1.2], [7.0, 5.0, 2.8], wall_absorption=1.0,
            room_modes=[{"frequency": 100.0, "q": 6.0, "gain": 12.0}], sr=SR)
        cap, pre = _capture(sweep, other, seed=7, gain_db=-30.0)
        ir_other, _ = wp.ir_from_capture(cap, sweep, pre)
        assert not wp.predict(run["wav"], ir_other, LIMIT_HZ)["passed"]

    def test_prediction_band_never_collapses(self, wp):
        lo, hi = wp.prediction_band_hz(500)
        assert hi >= 2 * lo

    def test_prediction_cuts_the_mode(self, wp, run):
        p = wp.predict(run["wav"], run["ir2"], LIMIT_HZ)
        k = np.argmin(np.abs(p["freqs"] - 63.0))
        assert p["predicted_db"][k] < p["measured_db"][k] - 3.0


def test_report_text(wp):
    text = wp.report_text([{
        "name": "left", "channel_index": 0, "limit_hz": 20, "enclosure": "closed",
        "delay_s": 0.0123, "filename": wp.filter_filename("left"),
        "prediction_label": "Predicted residual within 3 dB: PASS — x",
        "calibrated": False}], base_seed=174)
    assert "browser-generated" in text
    assert wp.REPORT_TEXT in text
    assert "base_seed: 174" in text and "channel_index 0" in text
    assert "16 Hz" in text and "12.3 ms" in text
