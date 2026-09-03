# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1003 — 7D torsion/shear branch rule."""

from __future__ import annotations

from src.core.pillar1003_sevend_torsion_shear_branch_rule import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    sevend_torsion_shear_branch_rule,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1003
    assert PILLAR_GATE == "SEVEND_TORSION_SHEAR_BRANCH_RULE"
    assert PILLAR_STATUS == "SEVEND_TORSION_SHEAR_BRANCH_RULE_COMPLETE"
    assert PILLAR_VALID is True


def test_branch_pairs_and_shear_alignment() -> None:
    report = sevend_torsion_shear_branch_rule()
    assert report["upper_branch_pair"] == (5, 7)
    assert report["lower_branch_pair"] == (5, 6)
    assert report["shear_summary"]["delta_n2"] == 1


def test_branch_rule_gates_pass() -> None:
    report = sevend_torsion_shear_branch_rule()
    assert report["valid"] is True
    assert all(report["non_negotiable_consistency_gates"].values())
