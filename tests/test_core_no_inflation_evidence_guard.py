# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/no_inflation_evidence_guard.py."""
from __future__ import annotations

from src.core.no_inflation_evidence_guard import (
    REQUIRED_PROMOTION_GATES,
    evaluate_promotion_guard,
)


def test_required_gate_list():
    assert list(REQUIRED_PROMOTION_GATES) == [
        "nominal_residual",
        "robustness",
        "axiomzero_purity",
    ]


def test_guard_all_pass():
    result = evaluate_promotion_guard(
        {
            "nominal_residual": True,
            "robustness": True,
            "axiomzero_purity": True,
        }
    )
    assert result["allow_promotion"] is True
    assert result["missing_required_gates"] == []
    assert result["failing_required_gates"] == []


def test_guard_blocks_missing_or_failing():
    result = evaluate_promotion_guard(
        {
            "nominal_residual": True,
            "robustness": False,
        }
    )
    assert result["allow_promotion"] is False
    assert "axiomzero_purity" in result["missing_required_gates"]
    assert "robustness" in result["failing_required_gates"]
