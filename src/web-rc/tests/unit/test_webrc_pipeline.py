"""webrc_pipeline on native CPython with the real soundfile (US-179).

Captures are simulated: the sweep goes through a room-simulator IR, then
latency and measurement noise are added. The browser runs the same module
under Pyodide with the soundfile shim (tests/browser).

webrc_pipeline is loaded from its path, so src/web-rc/py (which holds the
soundfile shim) never lands on sys.path here. room_correction is the one
conftest.room_correction_root() names.
"""

import ast
import importlib.util
import io
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile

from .. import conftest

WEB_RC = Path(__file__).resolve().parents[2]
RC = conftest.room_correction_root()
if importlib.util.find_spec("room_correction") is None:
    sys.path.insert(0, str(RC))

from mock import room_simulator  # noqa: E402
from room_correction import verify  # noqa: E402

SR = 48000
LIMIT_HZ = 40.0
SWEEP_S = 3.0
PRE_ROLL_S = 0.5
LATENCY_S = 0.023
SUB = {"filter_type": "lowpass"}
FULL = {"filter_type": "highpass"}


@pytest.fixture(scope="module")
def wp():
    spec = importlib.util.spec_from_file_location(
        "webrc_pipeline", WEB_RC / "py" / "webrc_pipeline.py")
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


@pytest.mark.parametrize("name", [
    "REC_MIN_PEAK_DBFS", "REC_MAX_PEAK_DBFS", "REC_MIN_SNR_DB"])
def test_mirrored_constants_match_native(wp, name):
    assert getattr(wp, name) == _native_constant(RC / "measure_nearfield.py", name)


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
             latency_s=LATENCY_S, onset=0):
    """onset: samples the output started after the scheduled pre-roll."""
    rng = np.random.default_rng(seed)
    pre = int(PRE_ROLL_S * SR)
    lat = int(latency_s * SR) + onset
    total = pre + len(sweep) + SR
    wet = np.convolve(sweep.astype(np.float64) * 10 ** (gain_db / 20), room_ir)
    cap = np.zeros(total)
    end = min(total, pre + lat + len(wet))
    cap[pre + lat:end] = wet[:end - pre - lat]
    cap += rng.standard_normal(total) * 10 ** (noise_dbfs / 20)
    return cap, pre


def _wav(fir, sr=SR):
    buf = io.BytesIO()
    soundfile.write(buf, np.asarray(fir, dtype=np.float32), sr, format="WAV",
                    subtype="FLOAT")
    return buf.getvalue()


@pytest.fixture(scope="module")
def sweep(wp):
    return wp.make_sweep(LIMIT_HZ, SWEEP_S)


@pytest.fixture(scope="module")
def run(wp, sweep):
    """One subwoofer channel through the room with the 63 Hz mode."""
    room = _room_ir()
    cap1, pre = _capture(sweep, room, seed=1)
    cap2, _ = _capture(sweep, room, seed=2)
    ir1, delay1 = wp.ir_from_capture(cap1, sweep, pre)
    ir2, _ = wp.ir_from_capture(cap2, sweep, pre)
    fir, correction = wp.build_filter(ir1, LIMIT_HZ, SUB)
    wav = wp.filter_wav_bytes(fir)
    return {"ir1": ir1, "ir2": ir2, "delay": delay1, "fir": fir, "wav": wav,
            "room": room, "correction": correction}


@pytest.fixture(scope="module")
def run_full(wp, sweep):
    """The same room measured as a full-range channel."""
    cap1, pre = _capture(sweep, _room_ir(), seed=11)
    ir1, _ = wp.ir_from_capture(cap1, sweep, pre)
    fir, correction = wp.build_filter(ir1, LIMIT_HZ, FULL)
    return {"ir1": ir1, "wav": wp.filter_wav_bytes(fir), "correction": correction}


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

    def test_measured_onset_is_removed(self, wp, sweep):
        """AE a1736914: onsets of 0 and 1 quantum give the same IR and delay."""
        room = _room_ir()
        cap0, pre = _capture(sweep, room, seed=6, onset=0)
        cap1, _ = _capture(sweep, room, seed=6, onset=128)
        ir0, d0 = wp.ir_from_capture(cap0, sweep, pre, onset_samples=0)
        ir1, d1 = wp.ir_from_capture(cap1, sweep, pre, onset_samples=128)
        assert abs(int(np.argmax(np.abs(ir0))) - int(np.argmax(np.abs(ir1)))) <= 1
        assert d1 == pytest.approx(d0, abs=1 / SR)
        # Without the measured onset the quantum would land in the delay.
        _, wrong = wp.ir_from_capture(cap1, sweep, pre)
        assert wrong - d0 == pytest.approx(128 / SR, abs=1 / SR)

    def test_onset_outside_the_window_fails_closed(self, wp, sweep):
        cap, pre = _capture(sweep, _room_ir(), seed=6)
        limit = int(wp.MAX_ONSET_S * SR)
        wp.ir_from_capture(cap, sweep, pre, onset_samples=-limit)
        for bad in (limit + 1, -limit - 1):
            with pytest.raises(ValueError, match="onset"):
                wp.ir_from_capture(cap, sweep, pre, onset_samples=bad)


class TestRole:
    """E2e: the declared role picks the speaker dict; E2h: the filename."""

    def test_speaker_dicts(self, wp):
        assert wp.speaker_dict("fullrange") == FULL
        assert wp.speaker_dict("subwoofer") == SUB

    @pytest.mark.parametrize("role", [None, "", "highpass", "sub", "Subwoofer"])
    def test_unknown_role_raises(self, wp, role):
        # Never the shared code's default to "highpass".
        with pytest.raises(ValueError, match="role"):
            wp.speaker_dict(role)

    def test_bands_follow_the_role(self, wp):
        from room_correction.correction import reference_band
        assert verify.closed_loop_band(SUB) == (30, 200)
        assert verify.closed_loop_band(FULL) == (250, 500)
        assert tuple(reference_band(SUB)) == (30, 150)
        assert tuple(reference_band(FULL)) == (400, 4000)

    def test_filenames(self, wp):
        assert wp.filter_filename(0, "fullrange") == \
            "combined_ch1-fullrange-browser-generated.wav"
        assert wp.filter_filename(3, "subwoofer") == \
            "combined_ch4-sub-browser-generated.wav"

    @pytest.mark.parametrize("channel, role", [(-1, "fullrange"), (0, None),
                                               (0, "highpass")])
    def test_filename_refuses_bad_input(self, wp, channel, role):
        with pytest.raises(ValueError):
            wp.filter_filename(channel, role)


class TestFilter:
    @pytest.mark.parametrize("which", ["run", "run_full"])
    def test_gates_pass_on_download_bytes(self, wp, request, which):
        r = request.getfixturevalue(which)
        speaker = SUB if which == "run" else FULL
        name = wp.filter_filename(0, "subwoofer" if which == "run" else "fullrange")
        v = wp.verify_wav_bytes(r["wav"], name, LIMIT_HZ,
                                (r["ir1"], r["correction"], speaker))
        assert v["ok"], [g for g in v["results"] if not g["passed"]]
        names = " ".join(g["name"] for g in v["results"])
        for gate in ("D-009", "Format", "WAV Subtype", "Mandatory HPF",
                     "Minimum Phase", "Closed Loop"):
            assert gate in names, gate

    def test_peak_below_minus_half_db(self, wp, run):
        mag = np.abs(np.fft.rfft(run["fir"], n=1 << 17))
        assert 20 * np.log10(np.max(mag)) <= -0.5

    def test_hpf_gate_uses_0_8_x_limit(self, wp, run):
        name = wp.filter_filename(0, "subwoofer")
        v = wp.verify_wav_bytes(run["wav"], name, LIMIT_HZ,
                                (run["ir1"], run["correction"], SUB))
        hpf = [g for g in v["results"] if g["name"].startswith("Mandatory HPF")]
        assert len(hpf) == 1 and hpf[0]["passed"]

    def test_tampered_bytes_fail_closed(self, wp, run):
        name = wp.filter_filename(0, "subwoofer")
        raw = bytearray(run["wav"])
        # Push one sample far above 0 dB: D-009 must fail.
        data_at = raw.index(b"data") + 8
        raw[data_at:data_at + 4] = np.float32(8.0).tobytes()
        assert not wp.verify_wav_bytes(bytes(raw), name, LIMIT_HZ,
                                       (run["ir1"], run["correction"], SUB))["ok"]

    def test_closed_loop_gate_fails_a_correction_that_applies_the_room(self, wp, run):
        # The shared gate checks the CorrectionFilter on capture 1: the
        # room's own response as the correction doubles the 63 Hz mode.
        from room_correction.correction import CorrectionFilter
        c = run["correction"]
        bad = CorrectionFilter(fir=run["ir1"][:16384], reference_level_db=c.reference_level_db,
                               ref_band_hz=c.ref_band_hz)
        name = wp.filter_filename(0, "subwoofer")
        v = wp.verify_wav_bytes(run["wav"], name, LIMIT_HZ, (run["ir1"], bad, SUB))
        failed = [g["name"] for g in v["results"] if not g["passed"]]
        assert failed == [f"Closed Loop ({name})"], failed
        assert not v["ok"]

    def test_wav_matches_export_filter_layout(self, wp, run):
        info = verify.sf.info(io.BytesIO(run["wav"]))
        assert (info.samplerate, info.channels, info.frames, info.subtype) == \
            (SR, 1, 16384, "FLOAT")

    def test_decode_filter_round_trips(self, wp, run):
        fir = wp.decode_filter(run["wav"])
        assert fir.dtype == np.float64 and len(fir) == 16384
        assert np.max(np.abs(fir - run["fir"].astype(np.float32))) == 0.0


class TestRepeatability:
    def test_repeatable_captures_pass(self, wp, run):
        r = wp.repeatability(run["ir1"], run["ir2"], SUB, LIMIT_HZ)
        assert r["ok"], r["max_abs_db"]
        assert r["band_hz"] == [30.0, 200.0] and r["limit_db"] == 1.0

    def test_trace_covers_the_view_band(self, wp, run):
        r = wp.repeatability(run["ir1"], run["ir2"], SUB, LIMIT_HZ)
        assert r["freqs"][0] == pytest.approx(LIMIT_HZ, rel=0.05)
        assert r["freqs"][-1] == pytest.approx(20000, rel=0.05)
        assert r["diff_db"].shape == r["freqs"].shape

    def test_moved_mic_fails_repeatability(self, wp, sweep, run):
        # Same level, other position: the 63 Hz mode couples less.
        cap, pre = _capture(sweep, _room_ir(mode_gain_db=4.0), seed=6)
        ir_moved, _ = wp.ir_from_capture(cap, sweep, pre)
        r = wp.repeatability(run["ir1"], ir_moved, SUB, LIMIT_HZ)
        assert not r["ok"] and r["max_abs_db"] > 1.0

    @pytest.mark.parametrize("shift_db, ok", [(0.6, True), (1.4, False)])
    def test_limit_is_1_db_without_level_alignment(self, wp, run, shift_db, ok):
        r = wp.repeatability(run["ir1"], run["ir1"] * 10 ** (shift_db / 20), SUB,
                             LIMIT_HZ)
        assert r["ok"] is ok and r["max_abs_db"] == pytest.approx(shift_db, abs=0.05)

    def test_only_the_closed_loop_band_gates(self, wp, sweep, run):
        """A difference above 200 Hz shows in the trace, not the verdict."""
        from scipy import signal
        b, a = signal.butter(2, 2000, "highpass", fs=SR)
        shelf = run["ir2"] + 0.5 * signal.lfilter(b, a, run["ir2"])
        r = wp.repeatability(run["ir1"], shelf, SUB, LIMIT_HZ)
        assert r["ok"], r["max_abs_db"]
        assert np.max(np.abs(r["diff_db"][r["freqs"] > 4000])) > 1.0


class TestPrediction:
    def test_label_and_shapes(self, wp, run):
        p = wp.predict(run["wav"], run["ir2"], SUB)
        assert p["label"] == (
            "Predicted residual within 3 dB: "
            + ("PASS" if p["passed"] else "FAIL")
            + " — predicted, not measured, unverified until re-measured")
        assert p["predicted_db"].shape == p["measured_db"].shape == \
            p["target_db"].shape == p["freqs"].shape
        assert p["band_hz"] == [30.0, 200.0]

    def test_passes_for_a_matching_room(self, wp, run):
        p = wp.predict(run["wav"], run["ir2"], SUB)
        assert p["passed"], p["reason"]
        assert p["corrected_max_db"] <= 3.0 < p["uncorrected_max_db"]

    def test_is_verify_closed_loop(self, wp, run, monkeypatch):
        """P1: the verdict is verify.verify_closed_loop(...).passed."""
        calls = []
        real = verify.verify_closed_loop

        def spy(ir, cf, band, sr=SR):
            res = real(ir, cf, band, sr=sr)
            calls.append((band, res.passed))
            res.passed = not res.passed
            return res

        monkeypatch.setattr(verify, "verify_closed_loop", spy)
        p = wp.predict(run["wav"], run["ir2"], SUB)
        assert calls == [((30, 200), True)] and p["passed"] is False

    def test_fails_for_a_filter_that_applies_the_room(self, wp, run):
        """P1 t1: the room itself as the filter makes it worse: FAIL."""
        p = wp.predict(_wav(run["ir1"][:16384]), run["ir2"], SUB)
        assert not p["passed"], p
        assert p["corrected_max_db"] > p["uncorrected_max_db"]

    def test_filter_level_does_not_change_the_verdict(self, wp, run):
        """P1 t2: the WAV 6 dB down gives the same verdict (V1)."""
        base = wp.predict(run["wav"], run["ir2"], SUB)
        quieter = wp.predict(_wav(wp.decode_filter(run["wav"]) * 10 ** (-6 / 20)),
                             run["ir2"], SUB)
        assert quieter["passed"] == base["passed"]
        assert quieter["corrected_max_db"] == pytest.approx(
            base["corrected_max_db"], abs=0.01)

    def test_capture_level_does_not_change_the_verdict(self, wp, run):
        """P1 t3: capture 2 6 dB up gives the same verdict (V2)."""
        base = wp.predict(run["wav"], run["ir2"], SUB)
        louder = wp.predict(run["wav"], run["ir2"] * 10 ** (6 / 20), SUB)
        assert louder["passed"] == base["passed"]
        assert louder["corrected_max_db"] == pytest.approx(
            base["corrected_max_db"], abs=0.01)

    @pytest.mark.parametrize("bad", ["garbage", "short", "rate", "nan"])
    def test_undecodable_filter_fails_closed(self, wp, run, bad):
        """P1 t4: no verdict without the 16384-tap 48 kHz download."""
        fir = wp.decode_filter(run["wav"])
        wav = {"garbage": b"RIFF\x00\x00not a wav",
               "short": _wav(fir[:8192]),
               "rate": _wav(fir, sr=44100),
               "nan": _wav(np.where(np.arange(16384) == 9, np.nan, fir))}[bad]
        p = wp.predict(wav, run["ir2"], SUB)
        assert p["passed"] is False and p["reason"]
        assert p["corrected_max_db"] is None and p["label"].endswith(
            "FAIL — predicted, not measured, unverified until re-measured")

    def test_non_finite_holdout_fails_closed(self, wp, run):
        ir = run["ir2"].copy()
        ir[5] = np.inf
        p = wp.predict(run["wav"], ir, SUB)
        assert p["passed"] is False and p["reason"]

    def test_fails_for_a_filter_from_another_room(self, wp, sweep, run):
        # Non-vacuous: the 63 Hz filter leaves a 100 Hz mode uncut.
        other = _room_ir(mode_gain_db=0.0) + room_simulator.generate_room_ir(
            [1.0, 1.5, 1.2], [3.5, 2.5, 1.2], [7.0, 5.0, 2.8], wall_absorption=1.0,
            room_modes=[{"frequency": 100.0, "q": 6.0, "gain": 12.0}], sr=SR)
        cap, pre = _capture(sweep, other, seed=7, gain_db=-30.0)
        ir_other, _ = wp.ir_from_capture(cap, sweep, pre)
        assert not wp.predict(run["wav"], ir_other, SUB)["passed"]

    def test_cuts_the_mode(self, wp, run):
        p = wp.predict(run["wav"], run["ir2"], SUB)
        k = np.argmin(np.abs(p["freqs"] - 63.0))
        assert p["predicted_db"][k] < p["measured_db"][k] - 3.0


# -- analyze: one channel end to end -----------------------------------------

UMIK_HF = ('"Sens Factor =-1.378dB, SERNO: 7161942"\n'
           "20.000\t0.00\n7000.000\t0.00\n8000.000\t6.00\n20000.000\t6.00\n")


def _request(sweep, role="subwoofer", rooms=None, onsets=(0, 128), **extra):
    rooms = rooms or (_room_ir(), _room_ir())
    pre = int(PRE_ROLL_S * SR)
    caps = [_capture(sweep, room, seed=20 + i, onset=onset)[0]
            for i, (room, onset) in enumerate(zip(rooms, onsets))]
    req = {"channel": 2, "decl": {"role": role, "limitHz": LIMIT_HZ},
           "played": np.concatenate([np.zeros(pre, np.float32), sweep]),
           "preRollS": PRE_ROLL_S, "captures": caps, "onsets": list(onsets),
           "calibrated": False, "calibrationText": None}
    req.update(extra)
    return req


class TestAnalyze:
    def test_offers_a_verified_download(self, wp, sweep):
        out = wp.analyze(_request(sweep))
        assert out["fileName"] == "combined_ch3-sub-browser-generated.wav"
        assert out["role"] == "subwoofer" and out["channel"] == 2
        assert out["gates"]["ok"]
        assert any(g["name"].startswith("Closed Loop") for g in out["gates"]["results"])
        assert out["repeatability"]["ok"]
        assert out["prediction"]["passed"], out["prediction"]["reason"]
        assert len(wp.decode_filter(out["wavBytes"])) == 16384
        direct_s = np.argmax(np.abs(_room_ir())) / SR
        assert out["delayS"] == pytest.approx(LATENCY_S + direct_s, abs=2 / SR)
        assert out["irStartS"] == -wp.ALIGN_MARGIN_S
        assert out["measured"]["freqs"].shape == out["measured"]["db"].shape

    def test_each_capture_onset_is_removed(self, wp, sweep):
        """AE a1736914: capture 1 started a quantum late, the delay is not."""
        out = wp.analyze(_request(sweep, onsets=(128, 0)))
        direct_s = np.argmax(np.abs(_room_ir())) / SR
        assert out["delayS"] == pytest.approx(LATENCY_S + direct_s, abs=2 / SR)

    def test_prediction_uses_the_hold_out(self, wp, sweep, monkeypatch):
        """AC8b: the filter comes from capture 1, the prediction runs on 2."""
        used = {}
        real_build, real_predict = wp.build_filter, wp.predict
        monkeypatch.setattr(wp, "build_filter", lambda ir, *a, **k: (
            used.setdefault("built", ir), real_build(ir, *a, **k))[1])
        monkeypatch.setattr(wp, "predict", lambda wav, ir, *a, **k: (
            used.setdefault("held", ir), real_predict(wav, ir, *a, **k))[1])
        out = wp.analyze(_request(sweep))
        assert np.array_equal(used["built"], out["ir"])
        assert not np.array_equal(used["held"], used["built"])

    def test_moved_mic_rejects_the_pair(self, wp, sweep):
        req = _request(sweep, rooms=(_room_ir(), _room_ir(mode_gain_db=4.0)))
        with pytest.raises(wp.CaptureRejected, match="differ by .* over 30-200 Hz"):
            wp.analyze(req)

    def test_clipped_second_capture_names_it(self, wp, sweep):
        req = _request(sweep)
        req["captures"][1][int(PRE_ROLL_S * SR) + 4000] = 1.0
        with pytest.raises(wp.CaptureRejected, match=r"clipped.*\(measurement 2 of 2\)"):
            wp.analyze(req)

    @pytest.mark.parametrize("change, match", [
        ({"decl": {"limitHz": LIMIT_HZ}}, "role"),
        ({"decl": {"role": "woofer", "limitHz": LIMIT_HZ}}, "role"),
        ({"calibrated": True}, "calibration"),
        ({"onsets": [0, 127.5]}, "whole sample"),
        ({"onsets": [0]}, "two captures"),
        ({"preRollS": 0.0}, "pre-roll"),
    ])
    def test_bad_requests_fail_closed(self, wp, sweep, change, match):
        req = _request(sweep)
        req.update(change)
        with pytest.raises(ValueError, match=match):
            wp.analyze(req)

    def test_sound_in_the_pre_roll_fails_closed(self, wp, sweep):
        req = _request(sweep)
        req["played"][10] = 0.1
        with pytest.raises(ValueError, match="pre-roll"):
            wp.analyze(req)

    def test_failed_gate_offers_no_download(self, wp, sweep, monkeypatch):
        real = wp.build_filter
        monkeypatch.setattr(wp, "build_filter",
                            lambda *a, **k: (real(*a, **k)[0] * 8, real(*a, **k)[1]))
        with pytest.raises(wp.GateFailed, match="D-009"):
            wp.analyze(_request(sweep))

    def test_one_speaker_dict_everywhere(self, wp, sweep, monkeypatch):
        """E2e / Architect Q3: the same object reaches every shared call."""
        seen = {}

        def spy(name, real, pick):
            def wrapped(*a, **k):
                seen.setdefault(name, set()).add(id(pick(a, k)))
                return real(*a, **k)
            return wrapped

        monkeypatch.setattr(wp, "correction_from_measurement", spy(
            "correction", wp.correction_from_measurement, lambda a, k: a[1]))
        monkeypatch.setattr(verify, "run_correction_gate", spy(
            "gate", verify.run_correction_gate,
            lambda a, k: next(iter(k["closed_loop_inputs"].values()))[2]))
        monkeypatch.setattr(verify, "closed_loop_band", spy(
            "band", verify.closed_loop_band, lambda a, k: a[0]))
        monkeypatch.setattr(wp, "reference_band", spy(
            "reference", wp.reference_band, lambda a, k: a[0]))
        wp.analyze(_request(sweep))
        assert set(seen) == {"correction", "gate", "band", "reference"}
        ids = set().union(*seen.values())
        assert len(ids) == 1, seen

    def test_calibration_feeds_the_correction(self, wp, sweep):
        """K2: a bound session's curve changes the measured response."""
        req = _request(sweep, role="fullrange", onsets=(0, 0))
        plain = wp.analyze(req)
        cal = wp.analyze({**req, "calibrated": True, "calibrationText": UMIK_HF})
        f = plain["measured"]["freqs"]
        diff = cal["measured"]["db"] - plain["measured"]["db"]
        assert np.max(np.abs(diff[(f > 300) & (f < 5000)])) < 0.5
        assert abs(np.median(diff[(f > 10000) & (f < 18000)])) > 4.0
        # Not the bytes: the WAV PEAK chunk carries a timestamp.
        assert not np.array_equal(wp.decode_filter(cal["wavBytes"]),
                                  wp.decode_filter(plain["wavBytes"]))

    def test_uncalibrated_session_ignores_a_stray_curve(self, wp, sweep):
        req = _request(sweep, role="fullrange", onsets=(0, 0))
        plain = wp.analyze(req)
        stray = wp.analyze({**req, "calibrationText": UMIK_HF})
        assert np.array_equal(wp.decode_filter(stray["wavBytes"]),
                              wp.decode_filter(plain["wavBytes"]))


def test_report_text(wp):
    text = wp.report_text([{
        "name": "left", "channel_index": 0, "limit_hz": 20, "enclosure": "closed",
        "delay_s": 0.0123, "filename": wp.filter_filename(0, "fullrange"),
        "prediction_label": "Predicted residual within 3 dB: PASS — x",
        "calibrated": False}], base_seed=174)
    assert "browser-generated" in text
    assert wp.REPORT_TEXT in text
    assert "base_seed: 174" in text and "channel_index 0" in text
    assert "16 Hz" in text and "12.3 ms" in text
