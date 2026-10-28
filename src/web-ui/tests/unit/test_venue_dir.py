"""F-465: the web UI reads venues from PI4AUDIO_VENUES_DIR, the dir GM uses.

app.venue reads the env var at import, so each test reloads the module and
the fixture reloads it again without the override afterwards.
"""

import importlib

import pytest

import app.venue as venue


@pytest.fixture
def venues_env(monkeypatch, tmp_path):
    monkeypatch.setenv("PI4AUDIO_VENUES_DIR", str(tmp_path))
    importlib.reload(venue)
    yield tmp_path
    monkeypatch.delenv("PI4AUDIO_VENUES_DIR")
    importlib.reload(venue)


def test_env_dir_is_used(venues_env):
    (venues_env / "f465-venue.yml").write_text('name: "F-465 venue"\n')

    assert venue._venues_dir() == venues_env
    assert venue.list_venues() == [
        {"name": "f465-venue", "display_name": "F-465 venue"}]


def test_env_dir_hides_repo_venues(venues_env):
    # An empty env dir is still the venues dir: no silent repo fallback.
    assert venue._venues_dir() == venues_env
    assert venue.list_venues() == []
