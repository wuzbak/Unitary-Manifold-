# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1002 — 6D projection/counting branch rule."""

from __future__ import annotations

from src.core.pillar1002_sixd_projection_branch_rule import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    sixd_projection_branch_rule,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1002
    assert PILLAR_GATE == "SIXD_PROJECTION_BRANCH_RULE"
    assert PILLAR_STATUS == "SIXD_PROJECTION_BRANCH_RULE_COMPLETE"
    assert PILLAR_VALID is True


def test_branch_rule_recovers_lower_pair() -> None:
    report = sixd_projection_branch_rule()
    assert report["branch_pair"] == (5, 6)
    assert report["n_gen_6d"] == 3


def test_branch_rule_gates_pass() -> None:
    report = sixd_projection_branch_rule()
    assert report["valid"] is True
    assert all(report["non_negotiable_consistency_gates"].values())
