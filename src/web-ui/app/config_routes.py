"""Config tab REST endpoints.

Endpoints:
    GET  /api/v1/config          Read current gain + quantum + filter info
    POST /api/v1/config/gain     Set gain for one or more channels
    POST /api/v1/config/quantum  Set PipeWire quantum (runtime, via pw-metadata)

Safety:
    - D-009: Mult hard cap at 1.0 (0 dB).  UI soft cap at -20 dB (0.1).
    - G3 (F-352): non-finite, negative, > 1.0 and subnormal Mults are
      rejected (422), never clamped.
    - D-063 (F-344): a non-zero gain is only written while the gate reads
      open (``gain_guard``); otherwise 409 with reason gate_closed or
      gate_unknown.
    - Quantum changes require PipeWire restart awareness (USBStreamer transient
      risk documented in ``docs/operations/safety.md``).
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from typing import Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, field_validator

from .gain_guard import GATE_CLOSED, GATE_UNKNOWN, guarded_set_mult
from .pw_helpers import (
    MULT_HARD_CAP, pw_dump, find_convolver_node, find_gain_node, read_mult,
    find_quantum, find_sample_rate, find_filter_info, validate_mult,
)

log = logging.getLogger(__name__)

MOCK_MODE = os.environ.get("PI_AUDIO_MOCK", "1") == "1"

# Fallback gain node names for the default 2-way stereo topology.
# Used in mock mode and as validator fallback.  On a real Pi, gain nodes
# are discovered dynamically from pw-dump (supports N-way topologies).
DEFAULT_GAIN_NODE_NAMES = [
    "gain_left_hp",   # AUX0 - Left main
    "gain_right_hp",  # AUX1 - Right main
    "gain_sub1_lp",   # AUX2 - Sub 1
    "gain_sub2_lp",   # AUX3 - Sub 2
    "gain_hp_l",      # AUX4 - Headphone L (D-063)
    "gain_hp_r",      # AUX5 - Headphone R (D-063)
    "gain_iem_l",     # AUX6 - IEM L (D-063)
    "gain_iem_r",     # AUX7 - IEM R (D-063)
]

GAIN_LABELS = {
    "gain_left_hp": "Left HP",
    "gain_right_hp": "Right HP",
    "gain_sub1_lp": "Sub 1 LP",
    "gain_sub2_lp": "Sub 2 LP",
    "gain_hp_l": "Headphone L",
    "gain_hp_r": "Headphone R",
    "gain_iem_l": "IEM L",
    "gain_iem_r": "IEM R",
}


def _gain_label(name: str) -> str:
    """Human-readable label for a gain node.  Falls back to the node name."""
    if name in GAIN_LABELS:
        return GAIN_LABELS[name]
    # Auto-generate label from node name: "gain_mid_l_bp" -> "Mid L BP"
    suffix = name.removeprefix("gain_").replace("_", " ").upper()
    return suffix

# Allowed quantum values.
VALID_QUANTUMS = {64, 128, 256, 512, 1024}  # F-141: removed 2048 (no use case, ALSA mismatch)

router = APIRouter(prefix="/api/v1/config", tags=["config"])


# -- Mock state (in-memory, for development) --------------------------------

_mock_gains: Dict[str, float] = {
    "gain_left_hp": 0.001,
    "gain_right_hp": 0.001,
    "gain_sub1_lp": 0.000631,
    "gain_sub2_lp": 0.000631,
    "gain_hp_l": 1.0,
    "gain_hp_r": 1.0,
    "gain_iem_l": 1.0,
    "gain_iem_r": 1.0,
}
_mock_quantum: int = 256


# -- Request models ---------------------------------------------------------

class GainRequest(BaseModel):
    gains: Dict[str, float]

    @field_validator("gains")
    @classmethod
    def validate_gains(cls, v: Dict[str, float]) -> Dict[str, float]:
        for name, mult in v.items():
            if not name.startswith("gain_"):
                raise ValueError(f"Invalid gain node name: {name!r}. "
                                 f"Must start with 'gain_'")
            # G3: refuse, never clamp (F-352 AC1).
            try:
                v[name] = validate_mult(mult)
            except ValueError as exc:
                raise ValueError(f"{name}: {exc}") from None
        return v


class QuantumRequest(BaseModel):
    quantum: int

    @field_validator("quantum")
    @classmethod
    def validate_quantum(cls, v: int) -> int:
        if v not in VALID_QUANTUMS:
            raise ValueError(f"Invalid quantum {v}. "
                             f"Must be one of {sorted(VALID_QUANTUMS)}")
        return v


# -- Endpoints --------------------------------------------------------------

@router.get("")
async def get_config():
    """Read current gain values, quantum, and filter-chain info."""
    if MOCK_MODE:
        return _mock_config_response()

    pw_data = await pw_dump()
    if pw_data is None:
        return JSONResponse(
            status_code=502,
            content={"error": "pw_dump_failed",
                     "detail": "Could not read PipeWire state"},
        )

    # Discover gain nodes dynamically (supports N-way topologies)
    convolver_id, gain_params = find_convolver_node(pw_data)
    gain_names = sorted(k for k in gain_params if k.startswith("gain_"))
    if not gain_names:
        gain_names = list(DEFAULT_GAIN_NODE_NAMES)

    gains = {}
    for name in gain_names:
        node_id, mult = find_gain_node(pw_data, name)
        # F-057: If pw-dump found the convolver but Mult is not in params,
        # fall back to pw-cli enum-params for a live reading.
        if node_id is not None and mult is None:
            live_mult = await read_mult(node_id, name)
            if live_mult is not None:
                mult = live_mult
        gains[name] = {
            "mult": mult if mult is not None else 0.0,
            "label": _gain_label(name),
            "found": mult is not None,
        }

    quantum = find_quantum(pw_data)
    filter_info = find_filter_info(pw_data)

    sample_rate = find_sample_rate(pw_data)

    # F-086: Fall back to production default (256) when pw-metadata has
    # no force-quantum or quantum entry (e.g. fresh PipeWire start).
    if quantum is None:
        quantum = 256

    return {
        "gains": gains,
        "quantum": quantum,
        "sample_rate": sample_rate,
        "filter_chain": filter_info,
    }


def _invalid_gain_request(detail: list) -> JSONResponse:
    """422 without echoing the input: NaN/Infinity are not valid JSON (F-352)."""
    return JSONResponse(status_code=422, content={"detail": detail})


@router.post("/gain")
async def set_gain(request: Request):
    """Set gain Mult values for one or more channels.

    Values are validated by ``GainRequest`` (G3, D-009 cap 1.0).  The body
    is validated here rather than by FastAPI, whose 422 echoes the input
    and cannot encode NaN or Infinity.  Every write goes through
    ``guarded_set_mult``: a non-zero Mult needs the gate open.  The first
    gate refusal stops the batch with 409; values written before it are
    listed in ``applied``.
    """
    try:
        body = GainRequest.model_validate(await request.json())
    except ValueError as exc:  # bad JSON or a ValidationError
        if isinstance(exc, ValidationError):
            return _invalid_gain_request([
                {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                for e in exc.errors()])
        return _invalid_gain_request([{"loc": ["body"], "msg": "invalid JSON",
                                       "type": "json_invalid"}])

    if MOCK_MODE:
        async def write(_node_id: int, name: str, mult: float) -> bool:
            _mock_gains[name] = mult
            return True

        applied = {}
        for name, mult in body.gains.items():
            result = await guarded_set_mult(0, name, mult, write=write)
            if not result.ok:
                return _gate_refused(result.reason, applied)
            applied[name] = mult
        return JSONResponse({"ok": True, "gains": _mock_gains})

    pw_data = await pw_dump()
    if pw_data is None:
        return JSONResponse(
            status_code=502,
            content={"error": "pw_dump_failed",
                     "detail": "Could not read PipeWire state"},
        )

    errors = []
    applied = {}
    for name, mult in body.gains.items():
        node_id, _ = find_gain_node(pw_data, name)
        if node_id is None:
            errors.append(f"node '{name}' not found")
            continue
        result = await guarded_set_mult(node_id, name, mult)
        if result.ok:
            applied[name] = mult
        elif result.reason in (GATE_CLOSED, GATE_UNKNOWN):
            return _gate_refused(result.reason, applied)
        else:
            errors.append(f"pw-cli failed for '{name}'")

    if errors and not applied:
        return JSONResponse(
            status_code=502,
            content={"ok": False, "error": "; ".join(errors)},
        )

    result: dict = {"ok": True, "applied": applied}
    if errors:
        result["warnings"] = errors
    return JSONResponse(result)


def _gate_refused(reason: str | None, applied: dict) -> JSONResponse:
    """409 for a gain write the gate rule refused (UX f05b5f4a, 9c7109b4)."""
    log.info("Gain write refused: %s (applied before refusal: %s)",
             reason, applied)
    return JSONResponse(
        status_code=409,
        content={"ok": False, "error": "gate_not_open", "reason": reason,
                 "applied": applied},
    )


@router.post("/quantum")
async def set_quantum(body: QuantumRequest):
    """Set PipeWire quantum at runtime via pw-metadata.

    This does NOT restart PipeWire.  It changes the clock quantum
    dynamically.  The change takes effect on the next graph cycle.
    """
    global _mock_quantum

    if MOCK_MODE:
        _mock_quantum = body.quantum
        return JSONResponse({"ok": True, "quantum": _mock_quantum})

    def _set_quantum_sync() -> subprocess.CompletedProcess | None:
        try:
            return subprocess.run(
                ["pw-metadata", "-n", "settings", "0",
                 "clock.force-quantum", str(body.quantum)],
                capture_output=True, timeout=5,
            )
        except subprocess.TimeoutExpired:
            return None
        except FileNotFoundError:
            return None

    result = await asyncio.to_thread(_set_quantum_sync)
    if result is None:
        return JSONResponse(
            status_code=504,
            content={"ok": False, "error": "pw-metadata timed out or not found"},
        )
    if result.returncode != 0:
        return JSONResponse(
            status_code=502,
            content={"ok": False,
                     "error": f"pw-metadata failed: {result.stderr.decode().strip()}"},
        )
    log.info("Quantum set to %d via pw-metadata", body.quantum)
    return JSONResponse({"ok": True, "quantum": body.quantum})


# -- Mock helpers -----------------------------------------------------------

def _mock_config_response() -> dict:
    """Build a mock config response for development."""
    gains = {}
    for name in _mock_gains:
        gains[name] = {
            "mult": _mock_gains[name],
            "label": _gain_label(name),
            "found": True,
        }
    return {
        "gains": gains,
        "quantum": _mock_quantum,
        "sample_rate": 48000,
        "filter_chain": {
            "node_name": "filter-chain-convolver",
            "node_id": 42,
            "description": "8-channel FIR convolver (mock)",
        },
    }
