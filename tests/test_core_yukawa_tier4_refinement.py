# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/yukawa_tier4_refinement.py."""
from __future__ import annotations

from src.core.yukawa_tier4_refinement import (
    BEST_SUPPRESSION_STRENGTH,
    BASELINE_MAX_RESIDUAL_PCT,
    REFINED_MAX_RESIDUAL_PCT,
    BASELINE_MEDIAN_RESIDUAL_PCT,
    REFINED_MEDIAN_RESIDUAL_PCT,
    RESIDUAL_COMPRESSION_PCT,
    tier4_refined_table,
    tier4_yukawa_certificate,
)


def test_best_strength_in_scan_bounds():
    assert 0.0 <= BEST_SUPPRESSION_STRENGTH <= 1.2


def test_refinement_reduces_residuals():
    assert REFINED_MAX_RESIDUAL_PCT < BASELINE_MAX_RESIDUAL_PCT
    assert REFINED_MEDIAN_RESIDUAL_PCT < BASELINE_MEDIAN_RESIDUAL_PCT
    assert RESIDUAL_COMPRESSION_PCT > 90.0


def test_refined_table_shape():
    table = tier4_refined_table()
    assert len(table) == 4
    for row in table:
        assert "suppression_factor" in row
        assert "y_pred_refined" in row
        assert "residual_refined_pct" in row


def test_certificate_no_inflation_policy():
    cert = tier4_yukawa_certificate()
    assert cert["gates"]["residual_compression_pass"] is True
    assert cert["gates"]["cross_generation_consistency_pass"] is True
    assert cert["gates"]["axiomzero_purity_pass"] is False
    assert cert["promotion_allowed"] is False
    assert cert["toe_score_delta"] == 0.0
