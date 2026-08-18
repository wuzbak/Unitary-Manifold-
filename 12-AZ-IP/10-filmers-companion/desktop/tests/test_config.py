"""Tests for FilmConfig — 10 tests."""
import os
import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset():
    import desktop.app.config as m
    m._config = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_default_port():
    _reset()
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.port == 7864


def test_default_offline_false():
    _reset()
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.offline_mode is False


def test_env_port_override(monkeypatch):
    _reset()
    monkeypatch.setenv("FILM_PORT", "9090")
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.port == 9090


def test_env_offline_override(monkeypatch):
    _reset()
    monkeypatch.setenv("FILM_OFFLINE", "1")
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.offline_mode is True


def test_env_offline_true_string(monkeypatch):
    _reset()
    monkeypatch.setenv("FILM_OFFLINE", "true")
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.offline_mode is True


def test_env_host_override(monkeypatch):
    _reset()
    monkeypatch.setenv("FILM_HOST", "127.0.0.1")
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.host == "127.0.0.1"


def test_singleton_returns_same_instance():
    _reset()
    from desktop.app.config import get_config
    cfg1 = get_config()
    cfg2 = get_config()
    assert cfg1 is cfg2


def test_db_path_is_pathlib(tmp_path, monkeypatch):
    _reset()
    monkeypatch.setenv("FILM_DB_PATH", str(tmp_path / "test.db"))
    from desktop.app.config import get_config
    cfg = get_config()
    assert isinstance(cfg.db_path, Path)


def test_db_parent_created(tmp_path, monkeypatch):
    _reset()
    db_file = tmp_path / "subdir" / "film.db"
    monkeypatch.setenv("FILM_DB_PATH", str(db_file))
    from desktop.app.config import get_config
    cfg = get_config()
    assert cfg.db_path.parent.exists()


def test_llm_url_default():
    _reset()
    from desktop.app.config import get_config
    cfg = get_config()
    assert "11434" in cfg.local_llm_url or "localhost" in cfg.local_llm_url
