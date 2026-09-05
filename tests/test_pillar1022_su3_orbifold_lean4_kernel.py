# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1022 — SU(3) Lean4 kernel certificate."""

from __future__ import annotations

from src.core.pillar1022_su3_orbifold_lean4_kernel import (
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1022_summary,
    su3_orbifold_lean4_kernel_certificate,
)


REPORT = su3_orbifold_lean4_kernel_certificate()
SUMMARY = pillar1022_summary()


def test_constants():
    assert PILLAR_NUMBER == 1022
    assert PILLAR_STATUS == "SU3_ORBIFOLD_LEAN4_KERNEL_CERTIFIED"
    assert PILLAR_VALID is True


def test_lean4_kernel_exists_and_counts_theorems():
    assert REPORT["lean4_kernel"]["file"] == LEAN4_FILE
    assert REPORT["lean4_kernel"]["exists"] is True
    assert REPORT["lean4_kernel"]["theorem_count"] == LEAN4_THEOREM_COUNT == 12


def test_dependency_preserves_residual_open():
    assert REPORT["dependency"]["pillar636_equivalence_established"] is False
    assert REPORT["packet_valid"] is True
    assert REPORT["scientific_progress"] is False
    assert REPORT["physical_theorem_proved"] is False
    assert REPORT["lean4_kernel"]["compilation_verified"] is False
    assert "functional" in REPORT["status_advance"].lower()


def test_summary_echoes_kernel_count():
    assert SUMMARY["lean4_theorem_count"] == 12
