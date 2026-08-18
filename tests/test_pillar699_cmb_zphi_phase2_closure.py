# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 699 — CMB Z_phi Phase 2 closure."""
from __future__ import annotations

import math

from src.core.pillar699_cmb_zphi_phase2_closure import (
    C_S,
    N_W,
    OBSERVED_SUPPRESSION_CENTRAL,
    PILLAR_NUMBER,
    Z_PHI_PHASE1,
    suppression_coverage,
    zphi_closure_status,
    zphi_phase2_total,
)

TOTALS = zphi_phase2_total()
COVERAGE = suppression_coverage()
STATUS = zphi_closure_status()


def test_pillar_number():
    assert PILLAR_NUMBER == 699


def test_phase2_formula_matches_task():
    expected = 1.0 + N_W * C_S ** 2 / (4.0 * math.pi ** 2)
    assert math.isclose(TOTALS["z_phi_phase2"], expected, rel_tol=0.0, abs_tol=1e-15)


def test_total_is_product():
    assert math.isclose(TOTALS["z_phi_total"], Z_PHI_PHASE1 * TOTALS["z_phi_phase2"], rel_tol=0.0, abs_tol=1e-15)


def test_phase2_factor_gt_one():
    assert TOTALS["z_phi_phase2"] > 1.0


def test_total_gt_phase1():
    assert TOTALS["z_phi_total"] > Z_PHI_PHASE1


def test_predicted_factor_near_central_gap():
    assert 5.0 < COVERAGE["predicted_suppression_factor"] < 6.0


def test_observed_factor_central_value():
    assert COVERAGE["observed_suppression_factor"] == OBSERVED_SUPPRESSION_CENTRAL


def test_predicted_ratio_positive():
    assert COVERAGE["predicted_amplitude_ratio"] > 0.0


def test_observed_ratio_positive():
    assert COVERAGE["observed_amplitude_ratio"] > 0.0


def test_coverage_fraction_bounded():
    assert 0.0 < COVERAGE["coverage_fraction"] <= 1.0


def test_coverage_high():
    assert COVERAGE["coverage_fraction"] > 0.8


def test_normalization_residual_small():
    assert abs(COVERAGE["normalization_residual"]) < 0.02


def test_status_closed():
    assert STATUS["status"] == "PHASE2_CLOSED"


def test_status_contains_totals():
    assert "z_phi_total" in STATUS["z_phi"]


def test_status_contains_coverage():
    assert "coverage_fraction" in STATUS["coverage"]


def test_honesty_label_present():
    assert STATUS["honesty_label"] == "CENTRAL_SUPPRESSION_5P5_USED"
