"""pytest configuration — add desktop/ to sys.path so imports work."""
import sys
from pathlib import Path

import pytest

# Allow `from desktop.app.xxx import yyy` style imports in tests
DESKTOP_PARENT = Path(__file__).parent.parent.parent  # apps/filmmakers-companion/
if str(DESKTOP_PARENT) not in sys.path:
    sys.path.insert(0, str(DESKTOP_PARENT))


@pytest.fixture(autouse=True)
def isolate_default_database(tmp_path, monkeypatch):
    from desktop.app import config

    monkeypatch.setattr(config, "FILM_DIR", tmp_path / "filmers")
    config._config = None
    yield
    config._config = None
