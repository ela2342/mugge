#!/usr/bin/env bash
# Real E2E test runner — starts local-demo stack, runs pytest, tears down.
#
# Starts the full local-demo stack (PipeWire + GM + signal-gen + pcm-bridge +
# level-bridge + web UI) with PI_AUDIO_MOCK=0, waits for health, runs the
# service-integration and E2E suites (src/web-ui/tests/service-integration/,
# src/web-ui/tests/e2e/), then restarts the stack for the destructive suite
# (src/web-ui/tests/service-destructive/), and tears down on exit.
#
# Only physical audio hardware is absent — everything else is real.
#
# Usage:
#   nix run .#test-e2e               # preferred (all deps from Nix)
#   ./scripts/test-e2e.sh            # if already in nix develop
#
# Exit codes:
#   0 = all tests passed
#   1 = test failure(s)
#   2 = infrastructure error (stack failed to start)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${LOCAL_DEMO_REPO_DIR:-$(dirname "$SCRIPT_DIR")}"
LOCAL_DEMO="${LOCAL_DEMO_SH:-$REPO_DIR/scripts/local-demo.sh}"
BASH_BIN="${LOCAL_DEMO_BASH:-bash}"
PYTHON="${LOCAL_DEMO_PYTHON:-python}"
E2E_PYTHON="${LOCAL_DEMO_E2E_PYTHON:-$PYTHON}"

# Helper: read a port from the manifest, falling back to a default.
_read_manifest_port() {
    local key="$1" default="$2"
    if [ -n "${LOCAL_DEMO_MANIFEST:-}" ] && [ -f "$LOCAL_DEMO_MANIFEST" ]; then
        "$PYTHON" -c "
import json
m = json.load(open('$LOCAL_DEMO_MANIFEST'))
print(m['ports']['$key'])
" 2>/dev/null && return
    fi
    echo "$default"
}

CLEANUP_DONE=false

log() { echo "[test-e2e] $*"; }
log_err() { echo "[test-e2e] ERROR: $*" >&2; }

cleanup() {
    if $CLEANUP_DONE; then return; fi
    CLEANUP_DONE=true
    log "Tearing down local-demo stack..."
    "$BASH_BIN" "$LOCAL_DEMO" stop 2>/dev/null || true
    rm -f "${START_LOG:-}"
    log "Cleanup complete."
}

trap cleanup EXIT INT TERM

# ---- 1. Start local-demo stack ----

# Steps 1-2 run again before step 5, on a fresh stack.
start_stack() {
START_LOG=$(mktemp /tmp/test-e2e-start-XXXXXX.log)
# Test runs always get the known tone stimulus, never the owner's mp3, so
# every run (CI or dev) measures the same signal (F-394 Q1-1).
export LOCAL_DEMO_MIXXX_SOURCE=tone
log "Starting local-demo stack (PI_AUDIO_MOCK=0)..."
"$BASH_BIN" "$LOCAL_DEMO" start >"$START_LOG" 2>&1 || {
    log_err "local-demo start failed"
    cat "$START_LOG"
    rm -f "$START_LOG"
    exit 2
}
cat "$START_LOG"

# Extract the manifest path from start output. The start command prints:
#   [local-demo] Manifest written to /tmp/local-demo-<PID>.json
# We must set LOCAL_DEMO_MANIFEST before calling env, because env runs in a
# different process (different $$) and would compute a wrong manifest path.
export LOCAL_DEMO_MANIFEST
LOCAL_DEMO_MANIFEST=$(sed -n 's/.*Manifest written to //p' "$START_LOG")
# START_LOG is kept until cleanup: the stack's services (GM, bridges) keep
# writing their logs to it while the tests run (F-394 diagnostics).
if [ -z "$LOCAL_DEMO_MANIFEST" ] || [ ! -f "$LOCAL_DEMO_MANIFEST" ]; then
    log_err "Could not find manifest from start output"
    exit 2
fi
log "Using manifest: $LOCAL_DEMO_MANIFEST"

# Source PW env (includes LOCAL_DEMO_MANIFEST) so pw-cli calls + manifest work
eval "$("$BASH_BIN" "$LOCAL_DEMO" env)"
# The pw-* CLI tools in the tests need the running stack's socket; a wrong
# XDG_RUNTIME_DIR only shows up as "Host is down" skips/errors (F-394).
if [ ! -S "$XDG_RUNTIME_DIR/pipewire-0" ]; then
    log_err "PipeWire socket not found at $XDG_RUNTIME_DIR/pipewire-0"
    exit 2
fi
log "PipeWire socket: $XDG_RUNTIME_DIR/pipewire-0"

# Read all ports from the manifest and export for conftest.py.
# _read_manifest_port uses LOCAL_DEMO_MANIFEST (set by eval above).
export LOCAL_DEMO_URL="http://localhost:$(_read_manifest_port webui 8080)"
export GM_PORT=$(_read_manifest_port gm 4002)
export SIGGEN_PORT=$(_read_manifest_port siggen 4001)
export LEVEL_SW_PORT=$(_read_manifest_port level_sw 9100)
export LEVEL_HW_OUT_PORT=$(_read_manifest_port level_hw_out 9101)
export PCM_PORT=$(_read_manifest_port pcm 9090)

# Read demo_base_dir from manifest for path-based env vars.
_read_manifest_str() {
    local key="$1" default="$2"
    if [ -n "${LOCAL_DEMO_MANIFEST:-}" ] && [ -f "$LOCAL_DEMO_MANIFEST" ]; then
        "$PYTHON" -c "
import json
m = json.load(open('$LOCAL_DEMO_MANIFEST'))
print(m['$key'])
" 2>/dev/null && return
    fi
    echo "$default"
}
DEMO_BASE_DIR=$(_read_manifest_str demo_base_dir "/tmp/pi4audio-demo")
export PI4AUDIO_FILTER_OUTPUT_DIR="$DEMO_BASE_DIR/filters"
export PI4AUDIO_SESSION_DIR="$DEMO_BASE_DIR/sessions"

# ---- 2. Wait for web UI health ----

log "Waiting for web UI at ${LOCAL_DEMO_URL}..."
DEADLINE=$((SECONDS + 30))
while [ $SECONDS -lt $DEADLINE ]; do
    if curl -sf "${LOCAL_DEMO_URL}/" >/dev/null 2>&1; then
        log "Web UI is reachable."
        break
    fi
    sleep 1
done

if ! curl -sf "${LOCAL_DEMO_URL}/" >/dev/null 2>&1; then
    log_err "Web UI not reachable after 30s"
    exit 2
fi

# Allow services to stabilize (GM reconciler, level-bridges)
sleep 2
}

start_stack

# ---- 3. Run service-integration tests (no browser) ----

log "Running service-integration tests..."
cd "$REPO_DIR/src/web-ui"
SI_LOG_START=$(wc -c <"$START_LOG")
SI_EXIT=0
"$E2E_PYTHON" -m pytest tests/service-integration/ -v -rs --tb=short "$@" || SI_EXIT=$?

# F-394: show what the stack logged during the service-integration run
# (GM mode switches, reconciliation, missing endpoints).
log "Stack log during service-integration tests:"
tail -c +"$((SI_LOG_START + 1))" "$START_LOG" | sed 's/^/[stack] /'
log "End of stack log."

# ---- 4. Run browser E2E tests ----

log "Running browser E2E tests..."
E2E_EXIT=0
"$E2E_PYTHON" -m pytest tests/e2e/ -v -rs --tb=short "$@" || E2E_EXIT=$?

# ---- 5. Run destructive service tests on a fresh stack ----

# These remove monitored PipeWire nodes (F-320 D), so they get their own
# stack: stop the one steps 3-4 used, start a new one, stop it on exit.
log "Restarting local-demo stack for destructive service tests..."
cd "$REPO_DIR"
"$BASH_BIN" "$LOCAL_DEMO" stop 2>/dev/null || true
rm -f "$START_LOG"
start_stack

log "Running destructive service tests..."
cd "$REPO_DIR/src/web-ui"
SD_LOG_START=$(wc -c <"$START_LOG")
SD_EXIT=0
"$E2E_PYTHON" -m pytest tests/service-destructive/ -v -rs --tb=short --destructive "$@" || SD_EXIT=$?

log "Stack log during destructive service tests:"
tail -c +"$((SD_LOG_START + 1))" "$START_LOG" | sed 's/^/[stack] /'
log "End of stack log."

# Report all results — fail if any failed.
if [ $SI_EXIT -ne 0 ]; then
    log_err "Service-integration tests failed (exit $SI_EXIT)"
fi
if [ $E2E_EXIT -ne 0 ]; then
    log_err "Browser E2E tests failed (exit $E2E_EXIT)"
fi
if [ $SD_EXIT -ne 0 ]; then
    log_err "Destructive service tests failed (exit $SD_EXIT)"
fi
if [ $SI_EXIT -ne 0 ] || [ $E2E_EXIT -ne 0 ] || [ $SD_EXIT -ne 0 ]; then
    exit 1
fi
