"""Unit tests for the strict gain read-back oracle (F-439 2(c), no stack).

read_back_gains() / nonzero_gains() in fixtures/backend.py decide every
"all gains 0" assertion in the service and browser tests, so the parser
is pinned here against canned pw-cli enum-params text (QE 544d04b5 3,
AE 1fb3da7c P1/P2, AE 70541687 C2): 16 strict zeros pass; a value line
that is not exactly "Float 0.000000" counts as non-zero; a key whose next
line is not a Float, or a missing, extra or duplicate key, FAILs.
"""

import subprocess
import sys
import types
from pathlib import Path

import pytest

_tests_dir = str(Path(__file__).resolve().parent.parent)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from fixtures import backend  # noqa: E402
from fixtures.backend import (  # noqa: E402
    GAIN_KEYS,
    ZERO_LINE,
    nonzero_gains,
    read_back_gains,
)

ZEROS = dict.fromkeys(GAIN_KEYS, ZERO_LINE)


def _enum_params(values: dict[str, str], tail: list[str] = ()) -> str:
    """pw-cli enum-params <id> Props text for the given key -> value lines."""
    lines = [
        "  Object: size 1234, type Spa:Pod:Object:Param:Props (262146), id Spa:Enum:ParamId:Props (2)",
        "    Prop: key Spa:Pod:Object:Param:Props:params (524289), flags 00000000",
        "      Struct: size 1200",
    ]
    for key, value in values.items():
        lines.append(f'        String "{key}"')
        lines.append(f"        {value}")
    return "\n".join(lines + list(tail)) + "\n"


@pytest.fixture()
def pw_cli(monkeypatch):
    """Serve canned stdout for the pw-cli call; the node id is fixed."""
    def serve(stdout: str) -> None:
        monkeypatch.setattr(backend, "_convolver_id", lambda: 42)
        monkeypatch.setattr(
            backend.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=stdout, stderr=""))
    return serve


def _fails(stdout: str, pw_cli) -> str:
    pw_cli(stdout)
    with pytest.raises(pytest.fail.Exception) as exc:
        read_back_gains()
    return str(exc.value)


def test_sixteen_strict_zeros_pass(pw_cli):
    pw_cli(_enum_params(ZEROS))
    values = read_back_gains()
    assert list(values) == list(GAIN_KEYS)
    assert nonzero_gains(values) == {}


@pytest.mark.parametrize("line", [
    "Float -0.000000", "Float nan", "Float -nan", "Float -inf", "Float inf",
    "Float 0.000001", "Float 0.0", "Float 0.0000000",
])
def test_value_not_exactly_zero_line_is_nonzero(pw_cli, line):
    values = dict(ZEROS, **{"gain_sub1_lp:Mult": line})
    pw_cli(_enum_params(values))
    assert nonzero_gains(read_back_gains()) == {"gain_sub1_lp:Mult": line}


def test_nonzero_add_with_all_mults_zero_is_nonzero(pw_cli):
    values = dict(ZEROS, **{"gain_left_hp:Add": "Float 0.010000"})
    pw_cli(_enum_params(values))
    gains = read_back_gains()
    assert nonzero_gains(gains, "Mult") == {}
    assert nonzero_gains(gains) == {"gain_left_hp:Add": "Float 0.010000"}
    assert nonzero_gains(gains, "Add") == {"gain_left_hp:Add": "Float 0.010000"}


def test_missing_add_fails(pw_cli):
    values = dict(ZEROS)
    del values["gain_iem_r:Add"]
    assert "gain_iem_r:Add" in _fails(_enum_params(values), pw_cli)


def test_extra_gain_key_fails(pw_cli):
    msg = _fails(_enum_params(dict(ZEROS, **{"gain_extra:Mult": ZERO_LINE})), pw_cli)
    assert "gain_extra:Mult" in msg


def test_duplicate_mult_fails(pw_cli):
    tail = ['        String "gain_hp_l:Mult"', "        Float 0.000000"]
    assert "gain_hp_l:Mult" in _fails(_enum_params(ZEROS, tail), pw_cli)


@pytest.mark.parametrize("line", ["Double 0.0", "Int 0", "None", "garbage"])
def test_key_followed_by_non_float_fails_with_raw_line(pw_cli, line):
    msg = _fails(_enum_params(dict(ZEROS, **{"gain_hp_r:Add": line})), pw_cli)
    assert "gain_hp_r:Add" in msg and line in msg


def test_key_followed_by_another_key_fails(pw_cli):
    values = {k: v for k, v in ZEROS.items() if k != "gain_left_hp:Mult"}
    text = _enum_params(values).replace(
        '        String "gain_left_hp:Add"',
        '        String "gain_left_hp:Mult"\n        String "gain_left_hp:Add"', 1)
    msg = _fails(text, pw_cli)
    assert "gain_left_hp:Mult" in msg and 'String "gain_left_hp:Add"' in msg


def test_key_on_last_line_fails(pw_cli):
    text = _enum_params(ZEROS, ['        String "gain_iem_l:Mult"']).rstrip("\n")
    assert "gain_iem_l:Mult" in _fails(text, pw_cli)


def test_pw_cli_error_fails(monkeypatch):
    monkeypatch.setattr(backend, "_convolver_id", lambda: 42)
    monkeypatch.setattr(
        backend.subprocess, "run",
        lambda *a, **k: types.SimpleNamespace(returncode=1, stdout="", stderr="no node"))
    with pytest.raises(pytest.fail.Exception, match="no node"):
        read_back_gains()
