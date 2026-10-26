"""fixtures/butter/reference.json is what generate.py produces (US-179)."""

import importlib.util
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "butter"


def test_reference_is_current():
    spec = importlib.util.spec_from_file_location("gen_butter", FIXTURE / "generate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert (FIXTURE / "reference.json").read_text() == mod.render()
