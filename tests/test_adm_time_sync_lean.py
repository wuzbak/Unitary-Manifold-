# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from pathlib import Path
import shutil
import subprocess

import pytest


def _lake_parse_cmd(lake_bin: str) -> list[str]:
    return [lake_bin, "env", "lean", "lean4/UnitaryManifold/ADM_time_sync.lean"]


def _assert_lean_parse_success(lake_bin: str, repo_root: Path) -> None:
    result = subprocess.run(
        _lake_parse_cmd(lake_bin),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_adm_time_sync_lean_artifact_present():
    path = Path("lean4/UnitaryManifold/ADM_time_sync.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "theorem lapse_attractor_one" in text
    assert "Real.rpow" in text


def test_adm_time_sync_lean_parses_when_lean_available():
    lake_bin = shutil.which("lake")
    cmd = _lake_parse_cmd(lake_bin or "lake")
    assert cmd[-1] == "lean4/UnitaryManifold/ADM_time_sync.lean"
    assert cmd[1:3] == ["env", "lean"]
    if lake_bin is None:
        pytest.skip("Lake executable not available in this environment")
    repo_root = Path(__file__).resolve().parents[1]
    _assert_lean_parse_success(lake_bin, repo_root)


def test_adm_time_sync_lean_parse_failure_path(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/lake" if name == "lake" else None)

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr="lean parse error")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    with pytest.raises(AssertionError, match="lean parse error"):
        _assert_lean_parse_success("/usr/bin/lake", Path(__file__).resolve().parents[1])
