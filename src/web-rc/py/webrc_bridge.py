"""Call boundary between rc-worker.js and webrc_pipeline (US-179).

call() converts the JS argument array with JsProxy.to_py(), so typed
arrays arrive as memoryviews and plain objects as dicts. Results go back with plain types only: numpy
arrays as float64 memoryviews (Float64Array in JS), tuples as lists,
numpy scalars as Python numbers. Only the functions in CALLS are
reachable from JS.
"""

import numpy as np

import webrc_pipeline as wp

CALLS = {
    "make_sweep": wp.make_sweep,
    "analyze": wp.analyze,
    "report_text": wp.report_text,
}


def _arg(value):
    if isinstance(value, memoryview):
        return np.asarray(value)
    if isinstance(value, list):
        return [_arg(v) for v in value]
    if isinstance(value, dict):
        return {k: _arg(v) for k, v in value.items()}
    return value


def _result(value):
    if isinstance(value, np.ndarray):
        if value.dtype.kind in "fiu":
            return memoryview(np.ascontiguousarray(value, dtype=np.float64))
        raise TypeError(f"unsupported array dtype {value.dtype}")
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, (list, tuple)):
        return [_result(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _result(v) for k, v in value.items()}
    return value


def call(name, args):
    """Run CALLS[name](*args). Returns {ok, result} or {ok: False, kind,
    message}; kind is "rejected" for wp.Rejected (a user-facing fail
    closed), "error" otherwise."""
    if hasattr(args, "to_py"):  # JsProxy of a JS array
        args = args.to_py()
    fn = CALLS.get(name)
    if fn is None:
        return {"ok": False, "kind": "error", "message": f"unknown call {name!r}"}
    try:
        return {"ok": True, "result": _result(fn(*_arg(list(args))))}
    except wp.Rejected as exc:
        return {"ok": False, "kind": "rejected", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001 - reported to the UI, never swallowed
        return {"ok": False, "kind": "error",
                "message": f"{type(exc).__name__}: {exc}"}
