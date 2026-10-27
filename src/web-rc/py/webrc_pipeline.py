"""Browser-side room correction for one channel (US-179).

Runs inside Pyodide on top of the unchanged shared room_correction
modules (copied byte-identical by build_site.py). This module only wires
them together for the standalone flow:

    make_sweep -> (browser plays and captures) -> analyze:
    ir_from_capture x 2 -> repeatability -> build_filter -> filter_wav_bytes
    -> verify_wav_bytes -> predict;  report_text

Every array goes in and out as plain sequences or numpy arrays; the worker
converts. Nothing here touches the network or a Pi.

One speaker dict per channel ({"filter_type": "highpass"} for a full-range
speaker, "lowpass" for a subwoofer, E2e) picks every band: the level
reference (correction.reference_band), the repeatability and prediction
band (verify.closed_loop_band). analyze builds it once and passes the same
object to every call.

Constants that live in a module the browser can't import
(measure_nearfield needs the venue tooling) are mirrored below.
tests/unit/test_webrc_pipeline.py reads the native values with ast and
asserts they are equal, so a change upstream fails CI.
"""

import io
import math
import os
import tempfile

import numpy as np
from scipy import signal

import soundfile as sf

from room_correction import closed_loop, dsp_utils, verify
from room_correction.combine import combine_filters
from room_correction.correction import (
    MAX_CUT_DB,
    CorrectionFilter,
    correction_from_measurement,
    normalize_ir_level,
    reference_band,
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
from room_correction.target_curves import get_target_curve

SAMPLE_RATE = dsp_utils.SAMPLE_RATE
N_TAPS = DEFAULT_N_TAPS

# Mirrors of measure_nearfield's recording integrity thresholds (AC7).
REC_MIN_PEAK_DBFS = -40.0
REC_MAX_PEAK_DBFS = -1.0
REC_MIN_SNR_DB = 20.0
REC_MAX_DC_OFFSET = 0.01

# The role the user declares (safety.js ROLE) -> the shared code's
# filter_type key (E2e) and the filename tag (E2h). Never shown in the UI.
ROLE_FILTER_TYPES = {"fullrange": "highpass", "subwoofer": "lowpass"}
ROLE_FILE_TAGS = {"fullrange": "fullrange", "subwoofer": "sub"}
ROLE_LABELS = {"fullrange": "Full-range speaker", "subwoofer": "Subwoofer"}

HPF_RATIO = 0.8               # AC4g/6b, same as safety.js LIMITS.HPF_RATIO
SWEEP_F_END_HZ = 20000.0      # AC4g
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
# UX 436f962f, second half confirmed by the AE (c5bd03c0); calibration.js
# UNCAL_RESULT shows the same line in the result step.
UNCAL_REPORT_TEXT = (
    "Measured uncalibrated: levels in dBFS; the microphone's own frequency "
    "response is not compensated."
)
PREDICTION_LABEL = (
    "Predicted residual within 3 dB: {verdict} — predicted, not measured, "
    "unverified until re-measured"
)


class Rejected(ValueError):
    """A measurement failed closed. The message names the reason and is
    shown to the user as it is."""


class CaptureRejected(Rejected):
    """A capture failed closed (AC7, AC8a)."""


class GateFailed(Rejected):
    """The filter failed an AC6c gate: no download."""


def _f64(x):
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
        raise ValueError("expected a non-empty, finite 1-D signal")
    return arr


def subsonic_corner_hz(limit_hz):
    return HPF_RATIO * float(limit_hz)


def speaker_dict(role):
    """The channel's speaker dict (E2e). A missing or unknown role raises:
    the shared code's default to "highpass" is never relied on."""
    if role not in ROLE_FILTER_TYPES:
        raise ValueError(f"no speaker role for this channel ({role!r})")
    return {"filter_type": ROLE_FILTER_TYPES[role]}


def view_band_hz(limit_hz, sr=SAMPLE_RATE):
    """Band the measured magnitude is shown over: limit .. 20 kHz."""
    return (float(limit_hz), min(SWEEP_F_END_HZ, 0.95 * sr / 2))


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

def build_filter(ir, limit_hz, speaker, sr=SAMPLE_RATE):
    """Combined FIR for one channel: generate_profile_filters steps 2-4,
    without the crossover (E2e, E2j).

    correction_from_measurement (the speaker's reference band, flat,
    cut <= 18 dB) -> combine_filters with a dirac crossover and the
    subsonic HPF at 0.8 x limit (generate_profile_filters' margin and
    slope rule). Returns (fir, CorrectionFilter).
    """
    correction = correction_from_measurement(
        _f64(ir), speaker, target_curve="flat", n_taps=N_TAPS, sr=sr,
        max_cut_db=MAX_CUT_DB)
    subsonic = generate_subsonic_filter(
        hpf_freq=subsonic_corner_hz(limit_hz),
        slope_db_per_oct=max(DEFAULT_SLOPE_DB_PER_OCT, 24.0),
        n_taps=N_TAPS, sr=sr)
    dirac = np.zeros(N_TAPS)
    dirac[0] = 1.0
    fir = combine_filters(
        correction_filter=correction.fir, crossover_filter=dirac, n_taps=N_TAPS,
        margin_db=COMBINE_MARGIN_DB, subsonic_filter=subsonic)
    return fir, correction


def filter_filename(channel_index, role):
    """E2h: the 1-based output channel, the role tag, then BROWSER_TAG."""
    channel_index = int(channel_index)
    if channel_index < 0 or role not in ROLE_FILE_TAGS:
        raise ValueError(f"no filename for channel {channel_index}, role {role!r}")
    return f"combined_ch{channel_index + 1}-{ROLE_FILE_TAGS[role]}-{BROWSER_TAG}.wav"


def filter_wav_bytes(fir, sr=SAMPLE_RATE):
    """The WAV bytes the user downloads (export_filter, unchanged)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "filter.wav")
        export_filter(fir, path, n_taps=N_TAPS, sr=sr)
        with open(path, "rb") as fh:
            return fh.read()


def decode_filter(wav_bytes, sr=SAMPLE_RATE):
    """The download bytes as the float64 FIR that runs (AE b0d0c499 V1).
    Anything but N_TAPS finite taps at sr raises ValueError."""
    fir, file_sr = sf.read(io.BytesIO(bytes(wav_bytes)), dtype="float64")
    fir = np.asarray(fir, dtype=np.float64)
    if file_sr != sr:
        raise ValueError(f"filter sample rate {file_sr}, expected {sr}")
    if fir.ndim != 1 or len(fir) != N_TAPS:
        raise ValueError(f"filter has shape {fir.shape}, expected {N_TAPS} taps")
    if not np.all(np.isfinite(fir)):
        raise ValueError("filter has non-finite taps")
    return fir


def verify_wav_bytes(wav_bytes, filename, limit_hz, closed_loop_input,
                     sr=SAMPLE_RATE):
    """AC6c gates on the exact download bytes, written out and re-parsed.

    run_correction_gate (format, subtype, D-009, minimum-phase residual,
    mandatory HPF at 0.8 x limit, closed loop on capture 1) plus
    verify_minimum_phase. closed_loop_input is (capture-1 IR,
    CorrectionFilter, speaker dict). Returns {ok, results: [{name, passed,
    message}]}; any fail means no download.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, filename)
        with open(path, "wb") as fh:
            fh.write(bytes(wav_bytes))
        _, results = verify.run_correction_gate(
            tmp, {filename: "fir"},
            closed_loop_inputs={filename: closed_loop_input},
            mandatory_hpf_hz={filename: subsonic_corner_hz(limit_hz)},
            expected_taps=N_TAPS, expected_sr=sr)
        mp = verify.verify_minimum_phase(path)
        mp.name = f"{mp.name} ({filename})"
        results.append(mp)
    out = [{"name": r.name, "passed": bool(r.passed), "message": r.message}
           for r in results]
    return {"ok": bool(out) and all(r["passed"] for r in out), "results": out}


# -- hold-out capture and prediction (AC8) ----------------------------------

def repeatability(ir1, ir2, speaker, limit_hz, sr=SAMPLE_RATE):
    """Capture 1 minus capture 2, 1/6-octave smoothed (AC8a, E2f).

    The verdict is the max abs difference over the speaker's closed-loop
    band. The trace for the result view covers view_band_hz; only its
    points inside band_hz are gated (AE 6d63a2e3).
    Returns {ok, band_hz, max_abs_db, limit_db, freqs, diff_db}.
    """
    ir1, ir2 = _f64(ir1), _f64(ir2)
    lo, hi = verify.closed_loop_band(speaker)
    _, a = closed_loop.smoothed_response_db(ir1, lo, hi, sr=sr)
    _, b = closed_loop.smoothed_response_db(ir2, lo, hi, sr=sr)
    gated = a - b
    worst = float(np.max(np.abs(gated)))
    vlo, vhi = view_band_hz(limit_hz, sr=sr)
    freqs, ta = closed_loop.smoothed_response_db(ir1, vlo, vhi, sr=sr)
    _, tb = closed_loop.smoothed_response_db(ir2, vlo, vhi, sr=sr)
    return {
        "ok": bool(np.all(np.isfinite(gated)) and worst <= REPEATABILITY_MAX_DB),
        "band_hz": [float(lo), float(hi)], "max_abs_db": worst,
        "limit_db": REPEATABILITY_MAX_DB, "freqs": freqs, "diff_db": ta - tb,
    }


def repeatability_text(rep):
    """The AC8a rejection, worded as UX 1683b0fb with 09da95d8.

    X is the worst difference rounded UP to 0.1 dB, so a reject never
    reads as within the limit; lo/hi are the band the check used. A
    difference that can't be computed gets the 09da95d8 Q2 text, which
    names no speaker or level (nothing to turn up).
    """
    lo, hi = rep["band_hz"]
    worst, limit = rep["max_abs_db"], rep["limit_db"]
    if not np.isfinite(worst):
        return (f"Measurement not used: the two sweeps could not be compared "
                f"between {lo:g} and {hi:g} Hz. Restart; if this happens "
                f"again, check the microphone connection.")
    shown = max(math.ceil(round(worst * 10, 6)) / 10, round(limit + 0.1, 1))
    return (f"Measurement not used: the two sweeps differ by up to {shown:.1f} "
            f"dB between {lo:g} and {hi:g} Hz (limit {limit:.1f} dB). Keep "
            f"the microphone still and the room quiet, then restart.")


def predict(wav_bytes, holdout_ir, speaker, sr=SAMPLE_RATE):
    """Predicted residual on the hold-out capture (AC8b, AE b0d0c499 P1).

    verify.verify_closed_loop on capture 2 with the FIR decoded from the
    download bytes, its uniform level removed over the speaker's reference
    band (V1), and capture 2's own reference level (V2). Report-only: it
    never gates the download. Fails closed: any error or non-finite value
    is FAIL with the reason.

    Returns {passed, label, reason, band_hz, corrected_max_db,
    uncorrected_max_db, freqs, measured_db, predicted_db, target_db}; the
    curves are for the result view.
    """
    band = verify.closed_loop_band(speaker)
    out = {"passed": False, "reason": "", "band_hz": [float(band[0]), float(band[1])],
           "corrected_max_db": None, "uncorrected_max_db": None,
           "freqs": np.zeros(0), "measured_db": np.zeros(0),
           "predicted_db": np.zeros(0), "target_db": np.zeros(0)}
    try:
        fir = decode_filter(wav_bytes, sr=sr)
        ref_band = reference_band(speaker)
        fir_eval, _ = normalize_ir_level(fir, ref_band, sr=sr)
        ir = _f64(holdout_ir)
        _, level_db = normalize_ir_level(ir, ref_band, sr=sr)
        cf = CorrectionFilter(fir=fir_eval, reference_level_db=level_db,
                              ref_band_hz=ref_band)
        result = verify.verify_closed_loop(ir, cf, band, sr=sr)
        corrected = result.details.get("corrected_max_db")
        uncorrected = result.details.get("uncorrected_max_db")
        if corrected is None or uncorrected is None or not (
                np.isfinite(corrected) and np.isfinite(uncorrected)):
            out["reason"] = result.message
            return _labelled(out)
        out["corrected_max_db"] = float(corrected)
        out["uncorrected_max_db"] = float(uncorrected)
        out["passed"] = bool(result.passed)
        out["reason"] = result.message
        lo, hi = band
        freqs, measured = closed_loop.smoothed_response_db(ir, lo, hi, sr=sr)
        _, predicted = closed_loop.smoothed_response_db(
            closed_loop.system_response(ir, fir_eval), lo, hi, sr=sr)
        out.update(freqs=freqs, measured_db=measured - level_db,
                   predicted_db=predicted - level_db,
                   target_db=get_target_curve("flat", freqs))
    except Exception as exc:  # noqa: BLE001 - a FAIL with the reason, never PASS
        out["passed"] = False
        out["reason"] = f"{type(exc).__name__}: {exc}"
    return _labelled(out)


def _labelled(prediction):
    prediction["label"] = PREDICTION_LABEL.format(
        verdict="PASS" if prediction["passed"] else "FAIL")
    return prediction


# -- one channel, end to end (the page's "analyze") --------------------------

def analyze(request, sr=SAMPLE_RATE):
    """Both captures of one channel -> the verified download (flow.js).

    request: {channel, decl: {role, limitHz, ...}, played, preRollS,
    captures: [c1, c2], onsets: [o1, o2], calibrated, calibrationText, ...}.
    played is the buffer the output played: the silent pre-roll, then the
    sweep, which is the deconvolution reference. onsets[i] is capture i's
    measured output onset in samples (AE a1736914).

    The speaker dict is built once and the same object goes to the
    correction, the gate and the prediction (E2e, Architect Q3).

    Raises CaptureRejected (a capture, or the two differ, AC7/AC8a) or
    GateFailed (AC6c); the flow shows the message and starts over.
    Returns {fileName, wavBytes, role, limitHz, channel, delayS, gates,
    repeatability, prediction, measured: {freqs, db}, ir, irStartS}.
    """
    decl = request["decl"]
    role = decl.get("role")
    speaker = speaker_dict(role)
    limit_hz = float(decl["limitHz"])
    channel = int(request["channel"])
    captures, onsets = list(request["captures"]), list(request["onsets"])
    if len(captures) != 2 or len(onsets) != 2:
        raise ValueError("expected two captures, each with its onset")
    for onset in onsets:
        if not float(onset).is_integer():
            raise ValueError(f"onset {onset!r} is not a whole sample")
    pre = int(round(float(request["preRollS"]) * sr))
    played = _f64(request["played"])
    if not 0 < pre < len(played) or np.any(played[:pre]):
        raise ValueError("played buffer has no silent pre-roll")
    sweep = played[pre:]
    calibration_text = None
    if request.get("calibrated"):
        calibration_text = request.get("calibrationText")
        if not calibration_text:
            raise ValueError("calibrated session without the calibration file")

    irs, delays = [], []
    for i, (capture, onset) in enumerate(zip(captures, onsets)):
        try:
            ir, delay = ir_from_capture(capture, sweep, pre, calibration_text,
                                        sr=sr, onset_samples=int(onset))
        except CaptureRejected as exc:
            raise CaptureRejected(f"{exc} (measurement {i + 1} of 2)") from exc
        irs.append(ir)
        delays.append(delay)

    rep = repeatability(irs[0], irs[1], speaker, limit_hz, sr=sr)
    if not rep["ok"]:
        raise CaptureRejected(repeatability_text(rep))

    fir, correction = build_filter(irs[0], limit_hz, speaker, sr=sr)
    wav = filter_wav_bytes(fir, sr=sr)
    name = filter_filename(channel, role)
    gates = verify_wav_bytes(wav, name, limit_hz, (irs[0], correction, speaker),
                             sr=sr)
    if not gates["ok"]:
        failed = [f"{r['name']}: {r['message']}" for r in gates["results"]
                  if not r["passed"]]
        raise GateFailed("Filter not offered for download, a check failed: "
                         + "; ".join(failed))

    vlo, vhi = view_band_hz(limit_hz, sr=sr)
    freqs, measured = closed_loop.smoothed_response_db(irs[0], vlo, vhi, sr=sr)
    return {
        "fileName": name, "wavBytes": wav, "role": role, "limitHz": limit_hz,
        "channel": channel, "delayS": delays[0], "gates": gates,
        "repeatability": rep,
        "prediction": predict(wav, irs[1], speaker, sr=sr),
        "measured": {"freqs": freqs,
                     "db": measured - correction.reference_level_db},
        "ir": irs[0], "irStartS": -ALIGN_MARGIN_S,
    }


# -- report (AC5a, AC10) ----------------------------------------------------

def report_text(channels, base_seed):
    """Plain-text report shipped next to the WAVs.

    channels: list of {name, channel_index, role, limit_hz, enclosure,
    delay_s, filename, prediction_label, band_hz, calibrated}; band_hz is
    the band the AC8c verdict was checked over (E2h).
    """
    lines = [
        f"mugge standalone room correction ({BROWSER_TAG})",
        "",
        REPORT_TEXT,
        "",
        f"Noise base_seed: {int(base_seed)}",
    ]
    for ch in channels:
        if ch["role"] not in ROLE_LABELS:
            raise ValueError(f"no speaker role for channel {ch['name']!r}")
        lo, hi = ch["band_hz"]
        lines += [
            "",
            f"Channel {ch['name']} (channel_index {int(ch['channel_index'])})",
            f"  Role: {ROLE_LABELS[ch['role']]}",
            f"  File: {ch['filename']}",
            f"  Low limit: {float(ch['limit_hz']):g} Hz, subsonic HPF at "
            f"{subsonic_corner_hz(ch['limit_hz']):g} Hz",
            f"  Enclosure: {ch['enclosure']}",
            f"  Mic calibration: {'yes' if ch['calibrated'] else 'no'}",
            f"  Delay (audio latency + time of flight): "
            f"{1000 * float(ch['delay_s']):.1f} ms",
            f"  {ch['prediction_label']} (checked over {float(lo):g}-"
            f"{float(hi):g} Hz)",
        ]
        if not ch["calibrated"]:
            lines.append(f"  {UNCAL_REPORT_TEXT}")
    return "\n".join(lines) + "\n"
