# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from pathlib import Path
import shutil
import subprocess

import pytest


def test_adm_time_sync_lean_artifact_present():
    path = Path("lean4/UnitaryManifold/ADM_time_sync.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "theorem lapse_attractor_one" in text
    assert "Real.rpow" in text


def test_adm_time_sync_lean_parses_when_lean_available():
    lean_bin = shutil.which("lean")
    if lean_bin is None:
        pytest.skip("Lean executable not available in this environment")
    result = subprocess.run(
        [lean_bin, "lean4/UnitaryManifold/ADM_time_sync.lean"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
