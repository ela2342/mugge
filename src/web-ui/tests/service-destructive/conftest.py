"""Destructive service test fixtures — real stack, no browser.

Tests in this directory break the local-demo stack on purpose (e.g. they
remove a monitored PipeWire node), so they never share a stack with
tests/service-integration/ or tests/e2e/.  scripts/test-e2e.sh runs them
in their own step, on a freshly started stack that is stopped afterwards.

Backend fixtures are shared via tests/fixtures/backend.py.
"""

import sys
from pathlib import Path

import pytest

# Add the tests/ directory to sys.path so shared fixtures are importable.
_tests_dir = str(Path(__file__).resolve().parent.parent)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from fixtures.backend import (  # noqa: F401, E402
    apply_backend_skips,
    register_markers,
    add_backend_options,
    backend_type,
    base_url,
    local_demo_url,
    gm_port,
    siggen_port,
    level_sw_port,
    level_hw_out_port,
    pcm_port,
    api_get,
    api_post,
    rpc_call,
    read_levels,
    read_pcm_header,
    ensure_dj_mode,
)


# ---------------------------------------------------------------------------
# Hooks — delegate to shared backend
# ---------------------------------------------------------------------------

def pytest_configure(config):
    register_markers(config)


def pytest_addoption(parser):
    add_backend_options(parser)


def pytest_collection_modifyitems(config, items):
    apply_backend_skips(config, items)
