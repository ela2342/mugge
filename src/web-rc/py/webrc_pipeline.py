"""Browser-side room correction for one channel (US-179).

Runs inside Pyodide on top of the unchanged shared room_correction
modules (copied byte-identical by build_site.py). This module only wires
them together for the standalone flow:

    make_sweep -> (browser plays and captures) -> check_capture
    -> ir_from_capture -> build_filter -> filter_wav_bytes
    -> verify_wav_bytes -> repeatability / predict -> report_text

Every array goes in and out as plain sequences or numpy arrays; the worker
converts. Nothing here touches the network or a Pi.

Constants that live in modules the browser can't import (venue_pipeline
needs yaml + deploy, measure_nearfield needs the venue tooling) are
mirrored below. tests/unit/test_webrc_pipeline.py reads the native values
with ast and asserts they are equal, so a change upstream fails CI.
"""

import io
import os
import tempfile

import numpy as np
from scipy import signal

import soundfile as sf

from room_correction import closed_loop, dsp_utils, verify
from room_correction.combine import combine_filters
from room_correction.correction import (
    generate_correction_filter,
    normalize_ir_level,
)
from room_correction.crossover import generate_subsonic_filter
from room_correction.deconvolution import deconvolve
from room_correction.export import export_filter
from room_correction.generate_profile_filters import (
    COMBINE_MARGIN_DB,
    DEFAULT_N_TAPS,
    DEFAULT_SLOPE_DB_PER_OCT,
)
from room_correction.recording import apply_umik1_calibration
from room_correction.sweep import generate_log_sweep

SAMPLE_RATE = dsp_utils.SAMPLE_RATE
N_TAPS = DEFAULT_N_TAPS

# Mirrors of venue_pipeline.REFERENCE_BANDS_HZ / MAX_CUT_DB (AE 2026-10-25).
REFERENCE_BANDS_HZ = {
    "highpass": (400.0, 4000.0),
    "lowpass": (30.0, 150.0),
}
MAX_CUT_DB = 18.0

# Mirrors of measure_nearfield's recording integrity thresholds (AC7).
REC_MIN_PEAK_DBFS = -40.0
REC_MAX_PEAK_DBFS = -1.0
REC_MIN_SNR_DB = 20.0
REC_MAX_DC_OFFSET = 0.01

# A standalone channel is one speaker played full range from its declared
# limit up (AC4g). Its level reference is the sat band.
# TODO(US-179): AE to confirm the band choice for a sub-only channel.
CHANNEL_FILTER_TYPE = "highpass"

HPF_RATIO = 0.8               # AC4g/6b, same as safety.js LIMITS.HPF_RATIO
SWEEP_F_END_HZ = 20000.0      # AC4g
# Top of the evaluation band: the 1/6-octave window must stay clear of the
# sweep end, where only noise is left.
# TODO(US-179): AE to confirm the correction band (AC8a).
EVAL_F_HIGH_HZ = 16000.0
# Top of the prediction band. Above 500 Hz the frequency-dependent window
# leaves reflections uncorrected on purpose (F-262: gated band 250-500 Hz
# for sats, 500-4000 Hz logged only), so the unwindowed hold-out IR would
# fail there in any reflective room.
# TODO(US-179): AE to confirm the prediction band (AC8b).
PREDICT_F_HIGH_HZ = 500.0
SWEEP_MAX_S = 10.0            # AC4g
SWEEP_HPF_ORDER = 4           # AC4g, >= 4th order
REPEATABILITY_MAX_DB = 1.0    # AC8a
IR_SECONDS = 1.0              # deconvolve default
ALIGN_MARGIN_S = 0.1          # capture kept before the scheduled sweep onset
MAX_ONSET_S = 0.05            # |measured onset| bound; the flow refuses more

BROWSER_TAG = "browser-generated"
REPORT_TEXT = (
    "Filters for the mugge Pi (48 kHz). Loading onto the Pi is not "
    "supported yet. Correction not applied or verified acoustically; "
    "re-measure after loading them."
)
PREDICTION_LABEL = (
    "Predicted residual within 3 dB: {verdict} — predicted, not measured, "
    "unverified until re-measured"
)


class CaptureRejected(ValueError):
    """A capture failed closed (AC7). The message names the reason."""


def _f64(x):
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
        raise ValueError("expected a non-empty, finite 1-D signal")
    return arr


def subsonic_corner_hz(limit_hz):
    return HPF_RATIO * float(limit_hz)


def correction_band_hz(limit_hz):
    """Band the repeatability check (AC8a) is evaluated over."""
    return (float(limit_hz), EVAL_F_HIGH_HZ)


def prediction_band_hz(limit_hz):
    """Band the predicted residual verdict (AC8b) is evaluated over."""
    return (float(limit_hz), max(PREDICT_F_HIGH_HZ, 2.0 * float(limit_hz)))


# -- sweep (AC4g) -----------------------------------------------------------

def make_sweep(limit_hz, seconds, sr=SAMPLE_RATE):
    """The sweep the browser plays: limit -> 20 kHz, faded, through a
    4th-order Butterworth HPF at 0.8 x limit. float32, peak 0.9 before the
    browser applies its output gain. The same samples are the deconvolution
    reference."""
    seconds = min(float(seconds), SWEEP_MAX_S)
    sweep = generate_log_sweep(seconds, f_start=float(limit_hz),
                               f_end=SWEEP_F_END_HZ, sr=sr)
    sos = signal.butter(SWEEP_HPF_ORDER, subsonic_corner_hz(limit_hz),
                        btype="highpass", fs=sr, output="sos")
    return signal.sosfilt(sos, sweep).astype(np.float32)


# -- capture checks (AC7) ---------------------------------------------------

def check_capture(capture, pre_roll_samples):
    """Integrity of one capture, measure_nearfield's rules and constants.

    capture holds the silent pre-roll followed by the sweep response.
    Returns {ok, issues, peak_dbfs, rms_dbfs, noise_floor_dbfs, snr_db,
    dc_offset}.
    """
    capture = _f64(capture)
    pre_roll_samples = int(pre_roll_samples)
    if not 0 < pre_roll_samples < len(capture):
        raise ValueError("pre-roll must be inside the capture")
    pre_roll = capture[:pre_roll_samples]
    recording = capture[pre_roll_samples:]

    peak_dbfs = 20 * np.log10(max(np.max(np.abs(recording)), 1e-10))
    rms_dbfs = 20 * np.log10(max(np.sqrt(np.mean(recording ** 2)), 1e-10))
    dc_offset = float(abs(np.mean(recording)))
    noise_rms = float(np.sqrt(np.mean(pre_roll ** 2)))
    noise_dbfs = 20 * np.log10(max(noise_rms, 1e-10))
    snr_db = rms_dbfs - noise_dbfs if noise_rms > 0 else float("inf")

    issues = []
    if peak_dbfs < REC_MIN_PEAK_DBFS:
        issues.append(f"Peak too low: {peak_dbfs:.1f} dBFS < "
                      f"{REC_MIN_PEAK_DBFS:g} dBFS (mic not receiving signal?)")
    if peak_dbfs > REC_MAX_PEAK_DBFS:
        issues.append(f"Peak too high: {peak_dbfs:.1f} dBFS > "
                      f"{REC_MAX_PEAK_DBFS:g} dBFS (the mic input clipped)")
    if dc_offset > REC_MAX_DC_OFFSET:
        issues.append(f"DC offset: {dc_offset:.4f} (>{REC_MAX_DC_OFFSET:g}, "
                      f"possible ADC issue)")
    if snr_db < REC_MIN_SNR_DB:
        issues.append(f"SNR too low: {snr_db:.1f} dB < {REC_MIN_SNR_DB:g} dB "
                      f"(noisy room or mic too far)")
    return {
        "ok": not issues,
        "issues": issues,
        "peak_dbfs": float(peak_dbfs),
        "rms_dbfs": float(rms_dbfs),
        "noise_floor_dbfs": float(noise_dbfs),
        "snr_db": float(snr_db),
        "dc_offset": dc_offset,
    }


# -- impulse response -------------------------------------------------------

def ir_from_capture(capture, sweep, pre_roll_samples, calibration_text=None,
                    sr=SAMPLE_RATE, onset_samples=0):
    """Deconvolve one capture into an IR (AC7: alignment by deconvolution).

    onset_samples is the measured output onset for this capture: the frame
    the played buffer's first sample was rendered at, minus the capture's
    first frame (AE a1736914). The output may start a quantum late, so the
    sweep sits at pre_roll_samples + onset_samples in the capture. That
    onset only crops the capture, with ALIGN_MARGIN_S kept before it; the
    arrival is found from the IR peak. Raises CaptureRejected when the
    capture fails check_capture or the peak sits where no acoustic arrival
    can be.

    Returns (ir, delay_s): ir starts ALIGN_MARGIN_S before the measured
    onset; delay_s is the peak position after it (audio latency plus time
    of flight), the same whichever quantum the output started in.
    """
    onset_samples = int(onset_samples)
    if abs(onset_samples) > MAX_ONSET_S * sr:
        raise ValueError("output onset outside the capture window")
    pre_roll_samples = int(pre_roll_samples) + onset_samples
    capture = _f64(capture)
    report = check_capture(capture, pre_roll_samples)
    if not report["ok"]:
        raise CaptureRejected("Capture rejected: " + "; ".join(report["issues"]))

    margin = int(round(ALIGN_MARGIN_S * sr))
    start = pre_roll_samples - margin
    if start < 0:
        raise ValueError("pre-roll shorter than the alignment margin")
    ir = deconvolve(capture[start:], _f64(sweep), sr=sr,
                    ir_duration_s=IR_SECONDS + ALIGN_MARGIN_S)
    peak = int(np.argmax(np.abs(ir)))
    if peak < margin // 2 or peak >= len(ir) - int(0.5 * sr):
        raise CaptureRejected(
            "Capture rejected: no clear arrival found in the impulse response")
    if calibration_text is not None:
        ir = apply_calibration_text(ir, calibration_text, sr=sr)
    return ir, (peak - margin) / sr


def apply_calibration_text(ir, calibration_text, sr=SAMPLE_RATE):
    """apply_umik1_calibration on an uploaded calibration file's text."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "calibration.txt")
        with open(path, "w") as fh:
            fh.write(calibration_text)
        return apply_umik1_calibration(ir, path, sr=sr)


# -- filter (AC6) -----------------------------------------------------------

def build_filter(ir, limit_hz, sr=SAMPLE_RATE):
    """Combined FIR for one channel, the venue pipeline's chain.

    normalize_ir_level -> generate_correction_filter (flat, cut <= 18 dB)
    -> combine_filters with a dirac crossover and the subsonic HPF at
    0.8 x limit (generate_profile_filters' margin and slope rule).
    Returns (fir, reference_level_db).
    """
    ir = _f64(ir)
    normalized, level_db = normalize_ir_level(
        ir, REFERENCE_BANDS_HZ[CHANNEL_FILTER_TYPE], sr=sr)
    correction = generate_correction_filter(
        normalized, target_curve_name="flat", n_taps=N_TAPS, sr=sr,
        max_cut_db=MAX_CUT_DB)
    subsonic = generate_subsonic_filter(
        hpf_freq=subsonic_corner_hz(limit_hz),
        slope_db_per_oct=max(DEFAULT_SLOPE_DB_PER_OCT, 24.0),
        n_taps=N_TAPS, sr=sr)
    dirac = np.zeros(N_TAPS)
    dirac[0] = 1.0
    fir = combine_filters(
        correction_filter=correction, crossover_filter=dirac, n_taps=N_TAPS,
        margin_db=COMBINE_MARGIN_DB, subsonic_filter=subsonic)
    return fir, float(level_db)


def filter_filename(channel_name):
    return f"combined_{channel_name}_{BROWSER_TAG}.wav"


def filter_wav_bytes(fir, sr=SAMPLE_RATE):
    """The WAV bytes the user downloads (export_filter, unchanged)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "filter.wav")
        export_filter(fir, path, n_taps=N_TAPS, sr=sr)
        with open(path, "rb") as fh:
            return fh.read()


def verify_wav_bytes(wav_bytes, filename, limit_hz):
    """AC6c gates on the exact download bytes, written out and re-parsed.

    run_venue_checks (format, subtype, D-009, minimum-phase residual,
    mandatory HPF at 0.8 x limit) plus verify_minimum_phase. Returns
    {ok, results: [{name, passed, message}]}; any fail means no download.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, filename)
        with open(path, "wb") as fh:
            fh.write(bytes(wav_bytes))
        _, results = verify.run_venue_checks(
            tmp, {filename: "fir"},
            mandatory_hpf_hz={filename: subsonic_corner_hz(limit_hz)},
            expected_taps=N_TAPS, expected_sr=SAMPLE_RATE)
        mp = verify.verify_minimum_phase(path)
        mp.name = f"{mp.name} ({filename})"
        results.append(mp)
    out = [{"name": r.name, "passed": bool(r.passed), "message": r.message}
           for r in results]
    return {"ok": bool(out) and all(r["passed"] for r in out), "results": out}


# -- hold-out capture and prediction (AC8) ----------------------------------

def repeatability(ir1, ir2, limit_hz, sr=SAMPLE_RATE):
    """Capture 1 minus capture 2, 1/6-octave smoothed, over the correction
    band (AC8a). Returns {ok, freqs, diff_db, max_abs_db, limit_db}."""
    lo, hi = correction_band_hz(limit_hz)
    freqs, a = closed_loop.smoothed_response_db(_f64(ir1), lo, hi, sr=sr)
    _, b = closed_loop.smoothed_response_db(_f64(ir2), lo, hi, sr=sr)
    diff = a - b
    worst = float(np.max(np.abs(diff)))
    return {
        "ok": bool(np.all(np.isfinite(diff)) and worst <= REPEATABILITY_MAX_DB),
        "freqs": freqs, "diff_db": diff, "max_abs_db": worst,
        "limit_db": REPEATABILITY_MAX_DB,
    }


def predict(wav_bytes, holdout_ir, limit_hz, sr=SAMPLE_RATE):
    """Predicted corrected response on the hold-out capture (AC8b).

    The FIR comes from the download bytes; the verdict is
    closed_loop.passes_residual_gate on the response relative to the
    hold-out IR's reference level, against the flat target.
    Returns {passed, label, freqs, measured_db, predicted_db, target_db}.
    """
    fir, file_sr = sf.read(io.BytesIO(bytes(wav_bytes)), dtype="float64")
    if file_sr != sr:
        raise ValueError(f"filter sample rate {file_sr}, expected {sr}")
    ir = _f64(holdout_ir)
    _, level_db = normalize_ir_level(
        ir, REFERENCE_BANDS_HZ[CHANNEL_FILTER_TYPE], sr=sr)
    lo, hi = prediction_band_hz(limit_hz)
    freqs, measured = closed_loop.smoothed_response_db(ir, lo, hi, sr=sr)
    _, predicted = closed_loop.smoothed_response_db(
        closed_loop.system_response(ir, fir), lo, hi, sr=sr)
    measured = measured - level_db
    predicted = predicted - level_db
    target = closed_loop.channel_target_db(
        freqs, "fullrange", 1.0, DEFAULT_SLOPE_DB_PER_OCT, "flat")
    passed = bool(closed_loop.passes_residual_gate(predicted, target))
    return {
        "passed": passed,
        "label": PREDICTION_LABEL.format(verdict="PASS" if passed else "FAIL"),
        "freqs": freqs, "measured_db": measured,
        "predicted_db": predicted, "target_db": target,
    }


# -- report (AC5a, AC10) ----------------------------------------------------

def report_text(channels, base_seed):
    """Plain-text report shipped next to the WAVs.

    channels: list of {name, channel_index, limit_hz, enclosure, delay_s,
    filename, prediction_label, calibrated}.
    """
    lines = [
        f"mugge standalone room correction ({BROWSER_TAG})",
        "",
        REPORT_TEXT,
        "",
        f"Noise base_seed: {int(base_seed)}",
    ]
    for ch in channels:
        lines += [
            "",
            f"Channel {ch['name']} (channel_index {int(ch['channel_index'])})",
            f"  File: {ch['filename']}",
            f"  Low limit: {float(ch['limit_hz']):g} Hz, subsonic HPF at "
            f"{subsonic_corner_hz(ch['limit_hz']):g} Hz",
            f"  Enclosure: {ch['enclosure']}",
            f"  Mic calibration: {'yes' if ch['calibrated'] else 'no'}",
            f"  Delay (audio latency + time of flight): "
            f"{1000 * float(ch['delay_s']):.1f} ms",
            f"  {ch['prediction_label']}",
        ]
    return "\n".join(lines) + "\n"
