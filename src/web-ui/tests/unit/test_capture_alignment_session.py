"""F-262 S3 through the real session path (QE T1/T5; Q4 with the production tail).

The whole mock session runs (gain cal, sweeps, filter gen, deploy, verify).
The only fake is at the capture boundary: measure_nearfield.play_and_record
returns the mock room's capture shifted by a lag, as a late or early
pw-record start would.

Mock room onsets: Left 503, Sub1 463 samples. The session records 2 s after
the 0.5 s sweep (F4), so a capture is len(sweep) + 96000 samples, and a lag
L is in window iff 240 <= onset + L and onset + L + 24000 <= 96000:
L in [-223, 71497] (Sub1 bounds the start, Left the end).
"""

import os
import time

import numpy as np
import pytest
import soundfile as sf

import measure_nearfield
from room_correction import dsp_utils

LAST_EARLY_LAG = -223
LAST_LATE_LAG = 71497

# The 2way-80hz-sealed profile (sat_left on ch 0, sub1 on ch 2).
START_BODY = {
    "channels": [
        {"index": 0, "name": "Left", "target_spl_db": 75.0,
         "thermal_ceiling_dbfs": -20.0, "speaker_key": "sat_left"},
        {"index": 2, "name": "Sub1", "target_spl_db": 75.0,
         "thermal_ceiling_dbfs": -14.0, "speaker_key": "sub1"},
    ],
    "positions": 1,
    "sweep_duration_s": 0.5,
    "sweep_level_dbfs": -20.0,
    "hard_limit_spl_db": 84.0,
    "umik_sensitivity_dbfs_to_spl": 121.4,
    "profile_name": "2way-80hz-sealed",
}


@pytest.fixture
def capture_lag(monkeypatch):
    """Shift every sweep capture by the lag set on the returned dict."""
    lag = {"samples": 0}
    real = measure_nearfield.play_and_record

    def shifted(*args, **kwargs):
        rec, pre_roll = real(*args, **kwargs)
        n, s = len(rec), lag["samples"]
        if s >= 0:
            rec = np.concatenate([np.zeros(s), rec])[:n]
        else:
            rec = np.concatenate([rec[-s:], np.zeros(-s)])
        return rec, pre_roll

    monkeypatch.setattr(measure_nearfield, "play_and_record", shifted)
    return lag


def _run_session(client, output_dir, timeout_s=120.0):
    """Start a session and wait until its lifecycle has finished."""
    from app.main import app
    mm = app.state.mode_manager
    body = dict(START_BODY, output_dir=str(output_dir))
    resp = client.post("/api/v1/measurement/start", json=body)
    assert resp.status_code == 200, resp.text
    session = mm.measurement_session
    assert session is not None
    deadline = time.monotonic() + timeout_s
    while mm.measurement_session is session:
        assert time.monotonic() < deadline, (
            f"session stuck in {session.state.value}")
        time.sleep(0.2)
    final = client.get("/api/v1/measurement/status").json()
    assert mm.last_completed_session is session
    return final, session


def _smoothed_db(path):
    data, sr = sf.read(path, dtype="float64")
    mag = np.abs(np.fft.rfft(data, 65536))
    freqs = np.fft.rfftfreq(65536, 1.0 / sr)
    band = (freqs >= 20.0) & (freqs <= 20000.0)
    return dsp_utils.linear_to_db(
        dsp_utils.fractional_octave_smooth(mag[band] + 1e-30, freqs[band], 6))


def _wavs(directory, prefix):
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory)
                  if f.startswith(prefix) and f.endswith(".wav"))


@pytest.mark.parametrize("lag", [LAST_EARLY_LAG, 24000, LAST_LATE_LAG])
def test_in_window_lag_gives_the_lag_zero_filters(
        client, capture_lag, tmp_path, lag):
    """Q3: same filters, same gate verdict, D-009 within 0.1 dB, same delays."""
    capture_lag["samples"] = 0
    final0, s0 = _run_session(client, tmp_path / "lag0")
    assert final0["state"] == "complete", final0.get("error_message")
    fg0 = s0._filter_gen_result
    delays0 = dict(s0._time_alignment_delays)

    capture_lag["samples"] = lag
    final, s = _run_session(client, tmp_path / "lag")
    assert final["state"] == "complete", final.get("error_message")
    fg = s._filter_gen_result

    for key in ("ch0_pos0", "ch2_pos0"):
        log = s._sweep_results[key]["alignment"]
        log0 = s0._sweep_results[key]["alignment"]
        assert log["onset"] == log0["onset"] + lag
        assert log["window_margin"] >= 0

    assert fg["all_pass"] == fg0["all_pass"]
    assert set(fg["channels"]) == set(fg0["channels"])
    for spk in fg0["channels"]:
        diff = np.max(np.abs(_smoothed_db(fg["channels"][spk])
                             - _smoothed_db(fg0["channels"][spk])))
        assert diff <= 0.2, f"{spk}: corrected response differs {diff:.3f} dB"
    peaks0 = {v["channel"]: v["d009_peak_db"] for v in fg0["verification"]}
    for v in fg["verification"]:
        assert v["d009_peak_db"] == pytest.approx(peaks0[v["channel"]], abs=0.1)
    assert s._time_alignment_delays == delays0


@pytest.mark.parametrize("lag,message", [
    (LAST_EARLY_LAG - 1, "before the 240-sample window start"),
    (-4800, "before the 240-sample window start"),
    (LAST_LATE_LAG + 1, "window overruns the capture"),
])
def test_out_of_window_lag_fails_closed(
        client, capture_lag, tmp_path, lag, message):
    """Q4 FAIL rows: error state, the message, and no WAV written."""
    capture_lag["samples"] = lag
    final, _ = _run_session(client, tmp_path)
    assert final["state"] == "error"
    error = final.get("error_message") or ""
    assert "capture misaligned: (i)" in error
    assert message in error
    assert _wavs(tmp_path / "impulse_responses", "ir_") == []
    assert _wavs(tmp_path, "combined_") == []
