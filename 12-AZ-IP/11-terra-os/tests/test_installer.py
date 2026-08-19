"""
TerraOS — Installer Tests (13)
"""
from __future__ import annotations
import pytest
from pathlib import Path


def test_detect_platform_returns_string():
    from terra.deploy.install import _detect_platform
    p = _detect_platform()
    assert isinstance(p, str)


def test_detect_platform_known_value():
    from terra.deploy.install import _detect_platform
    p = _detect_platform()
    assert p in {"linux", "android", "windows", "macos", "unknown"}


def test_is_android_returns_bool():
    from terra.deploy.install import _is_android
    assert isinstance(_is_android(), bool)


def test_check_python_version_true():
    from terra.deploy.install import _check_python_version
    assert _check_python_version() is True


def test_create_directories(tmp_path):
    from terra.deploy.install import _create_directories
    dirs = _create_directories(tmp_path)
    assert len(dirs) >= 1
    for d in dirs:
        assert d.exists()


def test_init_database(tmp_path):
    db = tmp_path / "install_test.db"
    from terra.deploy.install import _init_database
    ok = _init_database(db)
    assert ok is True
    assert db.exists()


def test_seed_database(tmp_path):
    db = tmp_path / "seed_install.db"
    from terra.deploy.install import _init_database, _seed_database
    _init_database(db)
    ok = _seed_database(db)
    assert ok is True


def test_write_env_file(tmp_path):
    from terra.deploy.install import _write_env_file
    env_path = tmp_path / ".env"
    result = _write_env_file(tmp_path / "terra.db", env_path)
    assert result.exists()


def test_env_file_content(tmp_path):
    from terra.deploy.install import _write_env_file
    db = tmp_path / "terra.db"
    env = tmp_path / ".env"
    _write_env_file(db, env)
    content = env.read_text()
    assert "TERRA_DB_PATH" in content


def test_core_requirements_not_empty():
    from terra.deploy.install import CORE_REQUIREMENTS
    assert len(CORE_REQUIREMENTS) >= 4


def test_versions_pinned():
    from terra.deploy.install import CORE_REQUIREMENTS
    for req in CORE_REQUIREMENTS:
        assert ">=" in req or "==" in req or "[" in req, f"Missing version pin: {req}"


def test_run_install_returns_dict(tmp_path):
    db = tmp_path / "run_install.db"
    from terra.deploy.install import run_install
    result = run_install(db_path=db, skip_pip=True)
    assert isinstance(result, dict)
    assert "platform" in result


def test_run_install_steps(tmp_path):
    db = tmp_path / "steps_install.db"
    from terra.deploy.install import run_install
    result = run_install(db_path=db, skip_pip=True)
    assert "steps" in result
    assert result["steps"]["python_version"] is True
