# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1035 — Sprint BX formal residual tightening."""

from src.core.pillar1035_sprint_bx_formal_residual_tightening import (
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1035_summary,
    sprint_bx_formal_residual_tightening,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1035
    assert PILLAR_GATE == "SPRINT_BX_FORMAL_RESIDUAL_TIGHTENING"
    assert PILLAR_STATUS == "SPRINT_BX_FORMAL_RESIDUAL_TIGHTENING_COMPLETE"
    assert PILLAR_VALID is True


def test_lean4_kernel_and_residual_reduction() -> None:
    report = sprint_bx_formal_residual_tightening()
    assert report["lean4_kernel"]["file"] == LEAN4_FILE
    assert report["lean4_kernel"]["exists"] is True
    assert report["lean4_kernel"]["theorem_count"] == LEAN4_THEOREM_COUNT == 12
    assert report["residual_map"]["formal_reduction_earned"] is False
    assert report["residual_map"]["open_steps_after"] == report["residual_map"]["open_steps_before"]
    assert report["residual_map"]["open_steps_before"] == report["dependency"]["residual_map"]["open_steps_after"]
    assert report["scientific_progress"] is False


def test_summary() -> None:
    summary = pillar1035_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
