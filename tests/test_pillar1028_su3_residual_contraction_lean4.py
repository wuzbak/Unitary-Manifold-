# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1028 — SU(3) residual contraction Lean4."""

from src.core.pillar1028_su3_residual_contraction_lean4 import (
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1028_summary,
    su3_residual_contraction_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1028
    assert PILLAR_GATE == "SU3_RESIDUAL_CONTRACTION_LEAN4"
    assert PILLAR_STATUS == "SU3_RESIDUAL_CONTRACTION_LEAN4_COMPLETE"
    assert PILLAR_VALID is True


def test_lean4_kernel_and_residual_reduction() -> None:
    report = su3_residual_contraction_report()
    assert report["lean4_kernel"]["file"] == LEAN4_FILE
    assert report["lean4_kernel"]["exists"] is True
    assert report["lean4_kernel"]["theorem_count"] == LEAN4_THEOREM_COUNT == 16
    assert report["residual_map"]["formal_reduction_earned"] is True
    assert report["residual_map"]["after_count"] < report["residual_map"]["before_count"]


def test_summary() -> None:
    summary = pillar1028_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
