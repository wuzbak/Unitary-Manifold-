"""
LithosOS — Installer Tests (13 tests)
"""
from __future__ import annotations
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

class TestPlatformDetection:
    def test_detect_returns_string(self):
        from lithic.deploy.install import _detect_platform
        result = _detect_platform()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_detect_linux_or_known(self):
        from lithic.deploy.install import _detect_platform
        result = _detect_platform()
        assert result in ("linux", "android", "windows", "macos", "unknown")

    def test_is_android_returns_bool(self):
        from lithic.deploy.install import _is_android
        result = _is_android()
        assert isinstance(result, bool)

class TestVersionCheck:
    def test_python_version_ok(self):
        from lithic.deploy.install import check_python
        assert check_python() is True

    def test_python_version_check_logic(self):
        from lithic.deploy.install import _check_python_version
        ok_flag, ver = _check_python_version()
        assert isinstance(ok_flag, bool)
        assert isinstance(ver, str)
        assert "." in ver

class TestCreateDataDir:
    def test_creates_data_dir(self, tmp_path):
        from lithic.deploy.install import _create_data_dir
        target = tmp_path / "data"
        assert not target.exists()
        result = _create_data_dir(target)
        assert result.exists()

    def test_creates_nested_dirs(self, tmp_path):
        from lithic.deploy.install import _create_data_dir
        target = tmp_path / "a" / "b" / "c"
        _create_data_dir(target)
        assert target.exists()

class TestLaunchScripts:
    def test_create_launch_sh(self, tmp_path):
        from lithic.deploy.install import _create_launch_scripts
        scripts = _create_launch_scripts(tmp_path)
        assert scripts["sh"].exists()
        content = scripts["sh"].read_text()
        assert "lithic" in content.lower() or "python" in content.lower()

    def test_create_launch_bat(self, tmp_path):
        from lithic.deploy.install import _create_launch_scripts
        scripts = _create_launch_scripts(tmp_path)
        assert scripts["bat"].exists()

    def test_create_launch_py(self, tmp_path):
        from lithic.deploy.install import _create_launch_scripts
        scripts = _create_launch_scripts(tmp_path)
        assert scripts["py"].exists()

class TestRequirements:
    def test_core_requirements_list(self):
        from lithic.deploy.install import CORE_REQUIREMENTS
        assert isinstance(CORE_REQUIREMENTS, list)
        assert len(CORE_REQUIREMENTS) >= 5

    def test_no_duplicate_requirements(self):
        from lithic.deploy.install import CORE_REQUIREMENTS
        names = [r.split(">=")[0].split("==")[0].strip().lower() for r in CORE_REQUIREMENTS]
        assert len(names) == len(set(names))

    def test_versions_pinned(self):
        from lithic.deploy.install import CORE_REQUIREMENTS
        for req in CORE_REQUIREMENTS:
            assert ">=" in req or "==" in req or "[" in req
