"""The one web UI Mult writer, guarded by the D-063 gate (F-320 F, F-439).

Every gain write in ``src/web-ui/app`` goes through ``guarded_set_mult``
(PO r3 §3; a unit test fails on any other ``set_mult`` call):

    - The value must pass G3 (``pw_helpers.validate_mult``): finite,
      0 <= Mult <= 1.0, no subnormal.  Invalid values are refused, never
      clamped (F-352).
    - Zero is always allowed.
    - A non-zero write needs a FRESH ``get_gate`` from GraphManager reading
      open.  A closed gate refuses (``gate_closed``); an RPC error or
      timeout refuses too (``gate_unknown``, fail closed).
    - After every non-zero write the gate is read again.  If it is no longer
      open, or the read fails, the Mult is written back to 0 and a WARNING
      is logged (AE 00e6f49a B).

A gate close between the read and the write is still possible (TOCTOU);
the re-read narrows it and GM's own close zeroes the gains.  US-159 D1
(GM as the sole writer) replaces this module.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from . import pw_helpers

log = logging.getLogger(__name__)

# Upper bound for one get_gate round trip (the client's socket timeout is 2 s).
GATE_READ_TIMEOUT_S = 3.0

GATE_CLOSED = "gate_closed"
GATE_UNKNOWN = "gate_unknown"
INVALID_VALUE = "invalid_value"
WRITE_FAILED = "write_failed"

Writer = Callable[[int, str, float], Awaitable[bool]]


@dataclass(frozen=True)
class GuardResult:
    """Outcome of one guarded write.  ``reason`` is None when ``ok``."""
    ok: bool
    reason: Optional[str] = None
    detail: str = ""


def _read_gate_open_sync() -> bool:
    """One get_gate RPC on a fresh connection; True only for gate_open true."""
    # Same client factory as the venue/gate routes (real or MOCK_MODE mock).
    from .venue_routes import _gm_client

    gm = _gm_client()
    try:
        return gm.get_gate().get("gate_open") is True
    finally:
        gm.close()


async def read_gate_open() -> bool:
    """Fresh gate read.  Raises on any RPC error or timeout."""
    return await asyncio.wait_for(
        asyncio.to_thread(_read_gate_open_sync), GATE_READ_TIMEOUT_S)


def _close_gate_sync() -> None:
    """One close_gate RPC on a fresh connection.  Raises on any failure."""
    from .venue_routes import _gm_client

    gm = _gm_client()
    try:
        gm.close_gate()
    finally:
        gm.close()


async def close_gate() -> None:
    """Close the D-063 gate (MUTE, F-439).  Raises on any RPC error/timeout."""
    await asyncio.wait_for(
        asyncio.to_thread(_close_gate_sync), GATE_READ_TIMEOUT_S)


async def read_gate_state() -> str:
    """Fresh gate reading: ``open``, ``closed`` or ``unknown`` (RPC failed)."""
    try:
        return "open" if await read_gate_open() else "closed"
    except Exception as exc:  # noqa: BLE001 — unknown, never "open"
        log.warning("Gate read failed (%s: %s)", type(exc).__name__, exc)
        return "unknown"


async def _gate_refusal() -> Optional[str]:
    """None if the gate reads open now, else the refusal reason."""
    try:
        is_open = await read_gate_open()
    except Exception as exc:  # noqa: BLE001 — every failure fails closed
        log.warning("Gate read failed (%s: %s): refusing gain write",
                    type(exc).__name__, exc)
        return GATE_UNKNOWN
    return None if is_open else GATE_CLOSED


async def guarded_set_mult(node_id: int, node_name: str, mult,
                           *, write: Optional[Writer] = None) -> GuardResult:
    """Write ``<node_name>:Mult`` only if G3 and the gate rule allow it.

    ``write`` replaces the pw-cli writer (MOCK_MODE gain store); the gate
    rule is the same either way.
    """
    if write is None:
        write = pw_helpers.set_mult
    try:
        mult = pw_helpers.validate_mult(mult)
    except ValueError as exc:
        return GuardResult(False, INVALID_VALUE, str(exc))

    if mult == 0.0:
        if await write(node_id, node_name, 0.0):
            return GuardResult(True)
        return GuardResult(False, WRITE_FAILED, f"write failed for '{node_name}'")

    reason = await _gate_refusal()
    if reason is not None:
        return GuardResult(False, reason, f"gate not open: {reason}")

    if not await write(node_id, node_name, mult):
        return GuardResult(False, WRITE_FAILED, f"write failed for '{node_name}'")

    # AE B: the gate may have closed while we wrote.
    reason = await _gate_refusal()
    if reason is None:
        return GuardResult(True)
    log.warning("Gate not open after writing %s Mult=%s (%s): writing 0",
                node_name, pw_helpers.format_mult(mult), reason)
    if not await write(node_id, node_name, 0.0):
        log.error("Could not write %s back to 0 after the gate closed",
                  node_name)
    return GuardResult(False, reason, f"gate not open after write: {reason}")
