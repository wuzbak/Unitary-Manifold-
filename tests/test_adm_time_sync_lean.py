# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from pathlib import Path


def test_adm_time_sync_lean_artifact_present():
    path = Path("lean4/UnitaryManifold/ADM_time_sync.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "theorem lapse_attractor_one" in text
    assert "Real.rpow" in text

