"""F-262 diagnostic driver (scratch/F-262-diag ONLY, never merged).

Runs F262_N (default 20) full measurement sessions against the live
local-demo stack, with the same request body as test_full_session_api,
then joins them with the server-side events from app/measurement/f262_diag.py
into $F262_DIAG_OUT/runs.jsonl and $F262_DIAG_OUT/summary.json.

Never fails on a session error: errors are the data. It fails only if the
instrumentation produced no capture events (diagnostic broken).
"""

import glob
import json
import os
import shutil
import time
import urllib.error
import urllib.request

import pytest

pytestmark = [pytest.mark.service_integration, pytest.mark.slow]

N_RUNS = int(os.environ.get("F262_N", "20"))
DIAG_DIR = os.environ.get("F262_DIAG_DIR", "/tmp/f262-diag")
OUT_DIR = os.environ.get("F262_DIAG_OUT", "/tmp/f262-diag-out")
CUTOFF_MS = 1000.0  # deconvolve ir_duration_s=1.0
NEAR_MS = 50.0
SESSION_TIMEOUT_S = 300

BODY = {
    "profile_name": "2way-80hz-sealed",
    "channels": [{
        "index": 0,
        "name": "Left",
        "target_spl_db": 80.0,
        "thermal_ceiling_dbfs": -20.0,
    }],
    "positions": 1,
    "sweep_duration_s": 2.0,
    "sweep_level_dbfs": -20.0,
    "sample_rate": 48000,
    "umik_sensitivity_dbfs_to_spl": 121.4,
    "hard_limit_spl_db": 95.0,
}


class _HTTPFail(Exception):
    pass


def _get(base, path, timeout=10):
    return json.loads(urllib.request.urlopen(f"{base}{path}", timeout=timeout).read())


def _post(base, path, body=None, timeout=30):
    req = urllib.request.Request(
        f"{base}{path}", data=json.dumps(body).encode() if body else b"",
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except urllib.error.HTTPError as exc:
        # Keep the server's detail: run 40320962929 only showed "400 Bad Request".
        raise _HTTPFail(f"POST {path} -> {exc.code}: {exc.read()[:300]!r}") from None


def _wait_terminal(base, timeout_s):
    deadline = time.monotonic() + timeout_s
    data = {"state": "?"}
    while time.monotonic() < deadline:
        data = _get(base, "/api/v1/measurement/status")
        if data.get("state") in ("idle", "complete", "error", "aborted"):
            return data
        time.sleep(1)
    return {**data, "state": f"timeout({data.get('state')})"}


def _wait_standby(base, timeout_s=60):
    """Terminal session state is reported before the lifecycle has restored
    STANDBY (GM restore on error), so /start would 409 (run 40320962929)."""
    deadline = time.monotonic() + timeout_s
    data = {}
    while time.monotonic() < deadline:
        data = _get(base, "/api/v1/measurement/status")
        if data.get("mode") == "standby":
            return data
        time.sleep(0.5)
    raise _HTTPFail(f"mode not standby after {timeout_s}s: {data.get('mode')}")


def _open_gate(base):
    # An errored session leaves the gate open, and GM refuses a second
    # open_gate ("gate already open" -> 400). Close first: every run then
    # starts from the same closed-gate state as the first one.
    _post(base, "/api/v1/venue/gate/close")
    _post(base, "/api/v1/venue/select", {"venue": "local-demo"})
    return _post(base, "/api/v1/venue/gate/open").get("gate_open")


def _events():
    path = os.path.join(DIAG_DIR, "events.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _spread(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return {"min": min(values), "max": max(values),
            "spread": max(values) - min(values), "n": len(values)}


def _near_or_beyond_cutoff(cap, ref):
    """joint-diag-final Decision: onset >= 950 ms OR IR peak within 50 ms of the cutoff."""
    peak_to_cutoff = cap.get("ir_peak_to_cutoff_ms")
    return (cap[f"onset_{ref}_ms"] >= CUTOFF_MS - NEAR_MS
            or (peak_to_cutoff is not None and abs(peak_to_cutoff) <= NEAR_MS))


def _run_near_or_beyond(row, ref):
    return any(_near_or_beyond_cutoff(c, ref) for c in row["captures"])


def _median(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    m = len(values) // 2
    return values[m] if len(values) % 2 else (values[m - 1] + values[m]) / 2


class TestF262Diag:

    def test_f262_diag_runs(self, local_demo_url):
        os.makedirs(DIAG_DIR, exist_ok=True)
        os.makedirs(OUT_DIR, exist_ok=True)
        for stale in glob.glob(os.path.join(DIAG_DIR, "*")):
            if os.path.isfile(stale):
                os.remove(stale)
        shutil.rmtree(os.path.join(DIAG_DIR, "ir"), ignore_errors=True)

        sessions = []
        for run in range(N_RUNS):
            with open(os.path.join(DIAG_DIR, "run"), "w") as f:
                f.write(str(run))
            row = {"run": run, "t_start": time.time()}
            try:
                _wait_terminal(local_demo_url, 30)
                _wait_standby(local_demo_url)
                row["gate_open"] = _open_gate(local_demo_url)
                row["start"] = _post(
                    local_demo_url, "/api/v1/measurement/start", BODY).get("status")
                data = _wait_terminal(local_demo_url, SESSION_TIMEOUT_S)
                row["state"] = data.get("state")
                row["error_message"] = data.get("error_message")
            except Exception as exc:
                row["state"] = "driver_error"
                row["error_message"] = repr(exc)
            row["t_end"] = time.time()
            sessions.append(row)
            print(f"[f262-diag] run {run}: {row['state']} {row.get('error_message') or ''}",
                  flush=True)

        events = _events()
        by_run = {}
        for ev in events:
            by_run.setdefault(ev.get("run"), []).append(ev)

        rows = []
        for s in sessions:
            evs = by_run.get(s["run"], [])
            caps = [e for e in evs if e.get("event") == "capture"]
            row = {**s,
                   "passed": s["state"] == "complete",
                   "captures": caps,
                   "delays": [e for e in evs if e.get("event") == "delays"],
                   "verify": [e for e in evs if e.get("event") == "verify"],
                   "diag_errors": [e for e in evs if e.get("event", "").endswith("_error")]}
            rows.append(row)
            if not row["passed"]:
                for ir in glob.glob(os.path.join(DIAG_DIR, "ir", f"run{s['run']}_*.wav")):
                    shutil.copy(ir, OUT_DIR)

        with open(os.path.join(OUT_DIR, "runs.jsonl"), "w") as f:
            for row in rows:
                f.write(json.dumps(row, default=float) + "\n")

        def onsets(ref, pred):
            return [c[f"onset_{ref}_ms"] for r in rows if pred(r) for c in r["captures"]]

        summary = {"n_runs": len(rows),
                   "n_passed": sum(r["passed"] for r in rows),
                   "states": {}, "cutoff_ms": CUTOFF_MS, "near_ms": NEAR_MS}
        for r in rows:
            summary["states"][r["state"]] = summary["states"].get(r["state"], 0) + 1
        for ref in ("session_sweep", "siggen_port"):
            all_on = onsets(ref, lambda r: True)
            fail_on = onsets(ref, lambda r: not r["passed"])
            pass_on = onsets(ref, lambda r: r["passed"])
            failing = [r for r in rows if not r["passed"]]
            passing = [r for r in rows if r["passed"]]
            st = _spread(all_on)
            summary[ref] = {
                "onset_ms": st,
                "within_50ms_of_cutoff": sum(abs(o - CUTOFF_MS) <= NEAR_MS for o in all_on),
                "failing_onsets_ms": fail_on,
                "passing_onsets_ms": pass_on,
                # joint-diag-final Decision inputs (lines 22-28):
                "rule_spread_gt_100ms": bool(st and st["spread"] > 100.0),
                "rule_all_failing_near_or_beyond": bool(failing) and all(
                    _run_near_or_beyond(r, ref) for r in failing),
                "rule_no_passing_near_or_beyond": not any(
                    _run_near_or_beyond(r, ref) for r in passing),
                "near_or_beyond_runs": [
                    r["run"] for r in rows if _run_near_or_beyond(r, ref)],
                "peak_width_3db_samples_median": _median(
                    [c.get(f"onset_{ref}_peak_width_3db_samples")
                     for r in rows for c in r["captures"]]),
                "peak_width_3db_samples": _spread(
                    [c.get(f"onset_{ref}_peak_width_3db_samples")
                     for r in rows for c in r["captures"]]),
                "ref_autocorr_width_3db_samples_median": _median(
                    [c.get(f"onset_{ref}_ref_autocorr_width_3db_samples")
                     for r in rows for c in r["captures"]]),
            }
            s2 = summary[ref]
            s2["and_rule_all_three"] = (s2["rule_spread_gt_100ms"]
                                        and s2["rule_all_failing_near_or_beyond"]
                                        and s2["rule_no_passing_near_or_beyond"])
            if s2["and_rule_all_three"]:
                s2["outcome"] = "CONFIRMED"
            elif st and st["spread"] < 5.0 and not failing:
                s2["outcome"] = "REFUTED"
            else:
                s2["outcome"] = "OTHER: report to AE + Architect"
            s2["peak_width_ae_rerule"] = bool(
                s2["peak_width_3db_samples_median"] is not None
                and s2["peak_width_3db_samples_median"] > 2.0)
        summary["ir_peak_ms"] = _spread(
            [c.get("ir_peak_ms") for r in rows for c in r["captures"]])
        summary["verify_min_phase_fail_runs"] = [
            r["run"] for r in rows if any(not v["min_phase_pass"] for v in r["verify"])]
        summary["n_runs_with_captures"] = sum(bool(r["captures"]) for r in rows)
        # Architect (3): per-run warm-up overlap vs pass/fail.
        summary["per_run"] = [{
            "run": r["run"], "state": r["state"], "passed": r["passed"],
            "error_message": r.get("error_message"),
            "captures": [{k: c.get(k) for k in (
                "key", "onset_siggen_port_ms", "onset_session_sweep_ms",
                "onset_siggen_port_peak_width_3db_samples", "ir_peak_ms",
                "ir_peak_to_cutoff_ms", "pre_roll_rms_dbfs", "rec_tail_rms_dbfs",
                "warmup_overlap_sweep_ms", "warmup_overlap_preroll_ms", "timing")}
                for c in r["captures"]],
        } for r in rows]
        summary["n_diag_errors"] = sum(len(r["diag_errors"]) for r in rows)
        with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2, default=float)
        print(json.dumps(summary, indent=2, default=float), flush=True)

        n_captured = sum(bool(r["captures"]) for r in rows)
        assert n_captured == N_RUNS, (
            f"F-262 diag: only {n_captured}/{N_RUNS} runs produced captures; "
            f"states={summary['states']}; the decision rule needs all {N_RUNS}")
