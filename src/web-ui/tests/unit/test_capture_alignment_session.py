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
from config_generator import load_profile
from room_correction import dsp_utils

LAST_EARLY_LAG = -223
LAST_LATE_LAG = 71497

# F-383 step 4 ruling 82b91d68: the response diff is taken over bins above
# peak0 - 120 dB only.  The exact-product sub stopband reaches the float64
# noise floor (~-185 dB re peak), where a 5e-6 capture difference moves the
# noise by dB; it carries no signal.
DIFF_FLOOR_DB = 120.0
SUB_PASSBAND_HZ = (20.0, 200.0)
BAND_TOP_HZ = 20000.0
MAIN_MIN_KEPT_SHARE = 0.5

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


def _band_freqs(path):
    """The bin frequencies of _smoothed_db(path)."""
    sr = sf.info(path).samplerate
    freqs = np.fft.rfftfreq(65536, 1.0 / sr)
    return freqs[(freqs >= 20.0) & (freqs <= 20000.0)]


def _passbands(fg):
    """Per channel: the band the kept bins must cover (ruling 82b91d68 R3).

    Subs (lowpass) 20-200 Hz; mains (highpass) from the session profile's
    crossover frequency (fg["crossover_freq_hz"]) to 20 kHz.
    """
    from app.measurement.session import _profile_dirs
    profiles_dir, _ = _profile_dirs()
    profile = load_profile(fg["profile"], profiles_dir=profiles_dir)
    crossover = float(fg["crossover_freq_hz"])
    bands = {}
    for spk in fg["channels"]:
        ftype = profile["speakers"][spk]["filter_type"]
        assert ftype in ("lowpass", "highpass"), (spk, ftype)
        bands[spk] = (SUB_PASSBAND_HZ if ftype == "lowpass"
                      else (crossover, BAND_TOP_HZ))
    return bands


def _response_diff(spk, path, path0, passband):
    """Max |dB diff| over the bins above the floor, with the R3 guards."""
    db, db0 = _smoothed_db(path), _smoothed_db(path0)
    freqs = _band_freqs(path0)
    data0, _ = sf.read(path0, dtype="float64")
    peak0 = float(np.max(db0))
    assert np.max(np.abs(data0)) > 0 and np.isfinite(peak0), (
        f"{spk}: lag-0 peak not finite/positive")
    floor = peak0 - DIFF_FLOOR_DB
    keep = (db0 > floor) | (db > floor)
    lo, hi = passband
    in_pass = (freqs >= lo) & (freqs <= hi)
    missing = in_pass & ~keep
    assert not missing.any(), (
        f"{spk}: passband bin at {freqs[missing][0]:.1f} Hz below the "
        f"{DIFF_FLOOR_DB:.0f} dB floor")
    if passband != SUB_PASSBAND_HZ:
        share = keep.mean()
        assert share >= MAIN_MIN_KEPT_SHARE, (
            f"{spk}: only {share:.0%} of band bins above the floor")
    return float(np.max(np.abs(db[keep] - db0[keep])))


def _wavs(directory, prefix):
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory)
                  if f.startswith(prefix) and f.endswith(".wav"))


@pytest.mark.parametrize("lag", [LAST_EARLY_LAG, 24000, LAST_LATE_LAG])
def test_in_window_lag_gives_the_lag_zero_filters(
        client, capture_lag, tmp_path, lag):
    """Q3: same filters, same gate verdict, D-009 within 0.1 dB, same delays.

    The response diff skips bins at the numerical floor (ruling 82b91d68).
    """
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
    passbands = _passbands(fg0)
    for spk in fg0["channels"]:
        diff = _response_diff(spk, fg["channels"][spk],
                              fg0["channels"][spk], passbands[spk])
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
