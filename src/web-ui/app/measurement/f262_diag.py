"""F-262 diagnostic instrumentation (scratch/F-262-diag ONLY, never merged).

Appends one JSON line per event to $F262_DIAG_DIR/events.jsonl
(default /tmp/f262-diag). The driver test writes the current run index
to $F262_DIAG_DIR/run before each session. Every hook swallows its own
exceptions so instrumentation can never change the session outcome.
"""

import json
import logging
import os
import time

import numpy as np

log = logging.getLogger(__name__)

DIAG_DIR = os.environ.get("F262_DIAG_DIR", "/tmp/f262-diag")
IR_CUTOFF_S = 1.0  # deconvolve(ir_duration_s=1.0) default


def _run_index():
    try:
        with open(os.path.join(DIAG_DIR, "run")) as f:
            return int(f.read().strip())
    except Exception:
        return -1


def _emit(event):
    try:
        os.makedirs(DIAG_DIR, exist_ok=True)
        event = {"run": _run_index(), "t_wall": time.time(), **event}
        with open(os.path.join(DIAG_DIR, "events.jsonl"), "a") as f:
            f.write(json.dumps(event, default=float) + "\n")
    except Exception as exc:  # never affect the session
        log.warning("F-262 diag emit failed: %s", exc)


def siggen_sweep(duration_s, sr, level_dbfs, f_start=20.0, f_end=20000.0):
    """Python port of signal-gen SweepGenerator (generator.rs, 289f1a72).

    signal-gen cannot export the buffer it played (diag note (b)); this
    port reproduces its phase law, phase-after-increment, peak amplitude
    = level_dbfs, and no fades. Ramp handling in main.rs is not modelled.
    """
    total = int(duration_s * sr)
    rate = np.log(f_end / f_start) / total
    f_inst = f_start * np.exp(rate * np.arange(total))
    phase = np.cumsum(2.0 * np.pi * f_inst / sr)
    return np.sin(phase) * 10 ** (level_dbfs / 20.0)


def _xcorr_onset(rec, ref, sr):
    """Lag of ref inside rec (samples), peak uniqueness in dB, -3 dB width.

    Uniqueness = main peak vs the largest correlation value more than
    5 ms away from it (AE S3: within 6 dB means not unique).
    Width = -3 dB width of the main peak in samples, crossings linearly
    interpolated (joint-diag-final addendum: median > 2 samples means the
    AE re-rules the sweep-law assumption).
    """
    from scipy.signal import fftconvolve

    xc = np.abs(fftconvolve(rec, ref[::-1], mode="full"))
    i = int(np.argmax(xc))
    guard = int(0.005 * sr)
    rest = xc.copy()
    rest[max(0, i - guard): i + guard + 1] = 0.0
    second = float(rest.max()) if rest.size else 0.0
    uniq_db = 20 * np.log10(xc[i] / second) if second > 0 else float("inf")
    return i - (len(ref) - 1), float(uniq_db), _width_3db(xc, i)


def _width_3db(xc, i):
    half = xc[i] / np.sqrt(2.0)
    lo = i
    while lo > 0 and xc[lo - 1] >= half:
        lo -= 1
    hi = i
    while hi < len(xc) - 1 and xc[hi + 1] >= half:
        hi += 1
    left = float(lo)
    if lo > 0:
        left = lo - (xc[lo] - half) / (xc[lo] - xc[lo - 1])
    right = float(hi)
    if hi < len(xc) - 1:
        right = hi + (xc[hi] - half) / (xc[hi] - xc[hi + 1])
    return float(right - left)


def _rms_dbfs(x):
    if len(x) == 0:
        return None
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-300))


def capture(key, recording, pre_roll, sweep, ir, sr, timing, level_dbfs):
    """One line per capture: onset, IR peak, noise, wall-clock timing."""
    try:
        pre = np.asarray(pre_roll if pre_roll is not None else [], dtype=float)
        rec = np.asarray(recording, dtype=float)
        full = np.concatenate([pre, rec])
        duration_s = len(sweep) / sr
        out = {"event": "capture", "key": key, "sr": sr,
               "pre_roll_samples": len(pre), "rec_samples": len(rec)}
        for name, ref in (("session_sweep", sweep),
                          ("siggen_port", siggen_sweep(duration_s, sr, level_dbfs))):
            lag_full, uniq, width = _xcorr_onset(full, ref, sr)
            lag = lag_full - len(pre)  # relative to the 0.5 s trim point
            out[f"onset_{name}_samples"] = lag
            out[f"onset_{name}_ms"] = lag / sr * 1e3
            out[f"onset_{name}_uniqueness_db"] = uniq
            out[f"onset_{name}_peak_width_3db_samples"] = width
            # Ideal width for this reference (its own autocorrelation): a log
            # sweep's peak is ~3.3 samples wide even with a perfect law match.
            out[f"onset_{name}_ref_autocorr_width_3db_samples"] = _xcorr_onset(ref, ref, sr)[2]
        ir = np.asarray(ir, dtype=float)
        peak = int(np.argmax(np.abs(ir)))
        out["ir_len"] = len(ir)
        out["ir_peak_idx"] = peak
        out["ir_peak_ms"] = peak / sr * 1e3
        out["ir_peak_to_cutoff_ms"] = (IR_CUTOFF_S * sr - peak) / sr * 1e3
        out["siggen_level_dbfs"] = level_dbfs
        out["session_sweep_peak_dbfs"] = float(
            20 * np.log10(np.max(np.abs(sweep)) + 1e-300))
        out["pre_roll_rms_dbfs"] = _rms_dbfs(pre)
        out["rec_tail_rms_dbfs"] = _rms_dbfs(rec[-int(0.25 * sr):])
        out["rec_peak_dbfs"] = float(20 * np.log10(np.max(np.abs(rec)) + 1e-300)) if len(rec) else None
        out["timing"] = t = dict(timing or {})
        # Architect (3): is the pink warm-up still playing when the sweep
        # starts / during the pre-roll? Positive = overlap in ms.
        if "t_warmup_play" in t and "warmup_duration_s" in t:
            warm_end = t["t_warmup_play"] + t["warmup_duration_s"]
            if "t_sweep_play_call" in t:
                out["warmup_overlap_sweep_ms"] = (warm_end - t["t_sweep_play_call"]) * 1e3
            if "t_capture_returned" in t:
                out["warmup_overlap_preroll_ms"] = (warm_end - t["t_capture_returned"]) * 1e3
        _emit(out)
        # Keep the IR for the driver; it uploads only failing runs' IRs.
        from room_correction.export import export_filter
        d = os.path.join(DIAG_DIR, "ir")
        os.makedirs(d, exist_ok=True)
        export_filter(ir, os.path.join(d, f"run{_run_index()}_ir_{key}.wav"),
                      n_taps=len(ir), sr=sr)
    except Exception as exc:
        log.warning("F-262 diag capture failed: %s", exc)
        _emit({"event": "capture_error", "key": key, "error": repr(exc)})


def delays(delays_s, delay_samples):
    """The session time-alignment lines (session.py:895-917)."""
    _emit({"event": "delays",
           "delays_ms": {k: v * 1000 for k, v in delays_s.items()},
           "delays_samples": {k: int(v) for k, v in delay_samples.items()}})


def verify(name, path, min_phase, d009):
    """verify_minimum_phase result per file, plus residual gate for reference."""
    try:
        from room_correction.verify import verify_minimum_phase_residual
        resid = verify_minimum_phase_residual(path)
        _emit({"event": "verify", "channel": name, "file": os.path.basename(path),
               "min_phase_pass": bool(min_phase.passed),
               "min_phase_message": min_phase.message,
               "min_phase_details": min_phase.details,
               "residual_pass": bool(resid.passed),
               "residual_details": resid.details,
               "d009_pass": bool(d009.passed), "d009_details": d009.details})
    except Exception as exc:
        log.warning("F-262 diag verify failed: %s", exc)
        _emit({"event": "verify_error", "channel": name, "error": repr(exc)})
