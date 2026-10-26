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


def _get(base, path, timeout=10):
    return json.loads(urllib.request.urlopen(f"{base}{path}", timeout=timeout).read())


def _post(base, path, body=None, timeout=30):
    req = urllib.request.Request(
        f"{base}{path}", data=json.dumps(body).encode() if body else b"",
        headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def _wait_terminal(base, timeout_s):
    deadline = time.monotonic() + timeout_s
    data = {"state": "?"}
    while time.monotonic() < deadline:
        data = _get(base, "/api/v1/measurement/status")
        if data.get("state") in ("idle", "complete", "error", "aborted"):
            return data
        time.sleep(1)
    return {**data, "state": f"timeout({data.get('state')})"}


def _open_gate(base):
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


def _near_or_beyond_cutoff(onset_ms):
    return onset_ms >= CUTOFF_MS - NEAR_MS


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
            st = _spread(all_on)
            summary[ref] = {
                "onset_ms": st,
                "within_50ms_of_cutoff": sum(abs(o - CUTOFF_MS) <= NEAR_MS for o in all_on),
                "failing_onsets_ms": fail_on,
                "passing_onsets_ms": pass_on,
                # AE AND rule inputs (verdict is the AE's/Architect's call):
                "rule_spread_gt_100ms": bool(st and st["spread"] > 100.0),
                "rule_all_failing_near_or_beyond": bool(fail_on) and all(
                    _near_or_beyond_cutoff(o) for o in fail_on),
                "rule_no_passing_near_or_beyond": not any(
                    _near_or_beyond_cutoff(o) for o in pass_on),
            }
            s2 = summary[ref]
            s2["and_rule_all_three"] = (s2["rule_spread_gt_100ms"]
                                        and s2["rule_all_failing_near_or_beyond"]
                                        and s2["rule_no_passing_near_or_beyond"])
        summary["ir_peak_ms"] = _spread(
            [c.get("ir_peak_ms") for r in rows for c in r["captures"]])
        summary["verify_min_phase_fail_runs"] = [
            r["run"] for r in rows if any(not v["min_phase_pass"] for v in r["verify"])]
        summary["n_diag_errors"] = sum(len(r["diag_errors"]) for r in rows)
        with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2, default=float)
        print(json.dumps(summary, indent=2, default=float), flush=True)

        assert any(r["captures"] for r in rows), (
            "F-262 diag: no capture events recorded; instrumentation broken")
