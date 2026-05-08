# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/neutrino_dm31_2nlo.py — 2NLO Δm²₃₁ overlap integrals."""
from __future__ import annotations

import math
import pytest

from src.sixd.neutrino_dm31_2nlo import (
    SIGMA_LO,
    SIGMA_NLO_FACTOR,
    SIGMA_2NLO_FACTOR,
    KK_MASS_RATIO,
    CURVATURE_COEFF,
    Z3_MIX_AMP,
    DM2_31_PDG,
    RESIDUAL_31_LO_PCT,
    RESIDUAL_31_NLO_PCT,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    overlap_integral_lo,
    overlap_integral_nlo,
    overlap_integral_2nlo,
    twonlo_correction_factor,
    effective_2nlo_enhancement_factor,
    dm2_residuals_2nlo,
    twonlo_gate_check,
    neutrino_2nlo_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_sigma_lo():
    assert abs(SIGMA_LO - 1.0 / 3.0) < 1e-15


def test_sigma_nlo_factor():
    assert abs(SIGMA_NLO_FACTOR - 0.15) < 1e-15


def test_sigma_2nlo_factor():
    assert abs(SIGMA_2NLO_FACTOR - 0.03) < 1e-15


def test_kk_mass_ratio():
    assert abs(KK_MASS_RATIO - 0.10) < 1e-15


def test_curvature_coeff():
    assert abs(CURVATURE_COEFF - 0.12) < 1e-15


def test_z3_mix_amp():
    assert abs(Z3_MIX_AMP - 0.05) < 1e-15


def test_dm2_31_pdg_order_of_magnitude():
    """Δm²₃₁ ≈ 2.453e-3 eV²."""
    assert 2.0e-3 < DM2_31_PDG < 3.0e-3


def test_residual_31_lo_pct():
    assert abs(RESIDUAL_31_LO_PCT - 10.5) < 1e-10


def test_residual_31_nlo_pct_range():
    """NLO residual should be between 5% and 10%."""
    assert 5.0 < RESIDUAL_31_NLO_PCT < 10.0


def test_residual_31_nlo_less_than_lo():
    assert RESIDUAL_31_NLO_PCT < RESIDUAL_31_LO_PCT


def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


# ---------------------------------------------------------------------------
# Overlap integrals — LO
# ---------------------------------------------------------------------------

def test_lo_diagonal_is_one():
    """I_LO(i,i) = 1 for all diagonal elements (distance 0)."""
    for i in range(3):
        assert abs(overlap_integral_lo(i, i) - 1.0) < 1e-15


def test_lo_symmetric():
    for i in range(3):
        for j in range(3):
            assert abs(overlap_integral_lo(i, j) - overlap_integral_lo(j, i)) < 1e-14


def test_lo_off_diagonal_less_than_one():
    """Off-diagonal overlaps < 1 (fixed points are separated)."""
    for i in range(3):
        for j in range(3):
            if i != j:
                assert overlap_integral_lo(i, j) < 1.0


def test_lo_off_diagonal_positive():
    for i in range(3):
        for j in range(3):
            assert overlap_integral_lo(i, j) > 0.0


def test_lo_invalid_index():
    with pytest.raises(ValueError):
        overlap_integral_lo(3, 0)
    with pytest.raises(ValueError):
        overlap_integral_lo(0, -1)


# ---------------------------------------------------------------------------
# Overlap integrals — NLO
# ---------------------------------------------------------------------------

def test_nlo_diagonal_greater_than_lo():
    """NLO corrections always increase diagonal overlap (no Z3 mixing there)."""
    for i in range(3):
        assert overlap_integral_nlo(i, i) > overlap_integral_lo(i, i)


def test_nlo_off_diagonal_greater_than_lo():
    """NLO off-diagonal overlaps should also increase."""
    for i in range(3):
        for j in range(3):
            if i != j:
                assert overlap_integral_nlo(i, j) > overlap_integral_lo(i, j)


def test_nlo_diagonal_formula():
    """For diagonal: I_NLO(i,i) = I_LO × (1 + δ_curv + 0) + δ_KK × I_LO = 1 × (1 + 0.012 + 0.10) = 1.112."""
    i_lo = 1.0  # diagonal
    delta_curv = CURVATURE_COEFF * KK_MASS_RATIO
    delta_kk = KK_MASS_RATIO * i_lo
    expected = i_lo * (1.0 + delta_curv) + delta_kk
    for i in range(3):
        assert abs(overlap_integral_nlo(i, i) - expected) < 1e-12


# ---------------------------------------------------------------------------
# Overlap integrals — 2NLO
# ---------------------------------------------------------------------------

def test_2nlo_diagonal_greater_than_nlo():
    """2NLO corrections always increase diagonal overlap."""
    for i in range(3):
        assert overlap_integral_2nlo(i, i) > overlap_integral_nlo(i, i)


def test_2nlo_off_diagonal_greater_than_nlo():
    for i in range(3):
        for j in range(3):
            if i != j:
                assert overlap_integral_2nlo(i, j) > overlap_integral_nlo(i, j)


def test_2nlo_diagonal_formula():
    """I_2NLO(i,i) = I_NLO(i,i) × (1 + δ_curv² + δ_KK²)."""
    delta_curv2 = (CURVATURE_COEFF * KK_MASS_RATIO) ** 2
    delta_kk2 = KK_MASS_RATIO ** 2
    for i in range(3):
        i_nlo = overlap_integral_nlo(i, i)
        expected = i_nlo * (1.0 + delta_curv2 + delta_kk2)
        assert abs(overlap_integral_2nlo(i, i) - expected) < 1e-12


def test_2nlo_all_diagonal_equal():
    """All diagonal fixed points are equivalent on T²/Z₃ (symmetric orbit)."""
    vals = [overlap_integral_2nlo(i, i) for i in range(3)]
    assert abs(vals[0] - vals[1]) < 1e-12
    assert abs(vals[1] - vals[2]) < 1e-12


# ---------------------------------------------------------------------------
# 2NLO correction factor
# ---------------------------------------------------------------------------

def test_twonlo_correction_factor_diagonal_gt_nlo_factor():
    """2NLO/LO ratio should be larger than NLO/LO ratio for diagonal."""
    from src.sixd.neutrino_overlap_integrals_nlo import nlo_correction_factor
    for i in range(3):
        assert twonlo_correction_factor(i, i) > nlo_correction_factor(i, i)


def test_twonlo_correction_factor_diagonal_gt_one():
    for i in range(3):
        assert twonlo_correction_factor(i, i) > 1.0


# ---------------------------------------------------------------------------
# Effective 2NLO enhancement factor
# ---------------------------------------------------------------------------

def test_effective_2nlo_factor_greater_than_one():
    assert effective_2nlo_enhancement_factor() > 1.0


def test_effective_2nlo_factor_greater_than_nlo():
    """2NLO effective factor > NLO effective factor ≈ 1.446."""
    from src.sixd.neutrino_overlap_integrals_nlo import effective_nlo_enhancement_factor
    assert effective_2nlo_enhancement_factor() > effective_nlo_enhancement_factor()


def test_effective_2nlo_factor_value():
    """2NLO effective factor ≈ 1.527 (computed analytically)."""
    f = effective_2nlo_enhancement_factor()
    assert 1.4 < f < 1.7


# ---------------------------------------------------------------------------
# dm2_residuals_2nlo
# ---------------------------------------------------------------------------

def test_dm2_residuals_returns_dict():
    result = dm2_residuals_2nlo()
    assert isinstance(result, dict)


def test_dm2_residuals_required_keys():
    result = dm2_residuals_2nlo()
    for key in ("dm2_31_pred_eV2", "dm2_31_pdg_eV2", "residual_31_2nlo_pct",
                "residual_31_nlo_pct", "residual_31_lo_pct",
                "improvement_over_nlo_pct", "twonlo_effective_factor"):
        assert key in result


def test_dm2_2nlo_residual_less_than_nlo():
    """2NLO residual must be strictly less than NLO residual."""
    result = dm2_residuals_2nlo()
    assert result["residual_31_2nlo_pct"] < result["residual_31_nlo_pct"]


def test_dm2_2nlo_residual_less_than_lo():
    result = dm2_residuals_2nlo()
    assert result["residual_31_2nlo_pct"] < result["residual_31_lo_pct"]


def test_dm2_2nlo_improvement_positive():
    result = dm2_residuals_2nlo()
    assert result["improvement_over_nlo_pct"] > 0.0


def test_dm2_2nlo_residual_range():
    """2NLO residual expected in [5%, 10%]."""
    result = dm2_residuals_2nlo()
    assert 5.0 < result["residual_31_2nlo_pct"] < 10.0


def test_dm2_2nlo_pred_pdg_consistent():
    """Predicted Δm²₃₁ should be close to PDG (within residual%)."""
    result = dm2_residuals_2nlo()
    actual_resid = abs(result["dm2_31_pred_eV2"] - result["dm2_31_pdg_eV2"]) / result["dm2_31_pdg_eV2"] * 100.0
    assert abs(actual_resid - result["residual_31_2nlo_pct"]) < 0.01


# ---------------------------------------------------------------------------
# Gate check
# ---------------------------------------------------------------------------

def test_gate_check_returns_dict():
    gate = twonlo_gate_check()
    assert isinstance(gate, dict)


def test_gate_check_required_keys():
    gate = twonlo_gate_check()
    for key in ("residual_31_2nlo_pct", "residual_31_nlo_pct",
                "gate_threshold_pct", "gate_pass", "status", "honest_note"):
        assert key in gate


def test_gate_check_gate_not_passed():
    """2NLO residual still > 5%, gate NOT passed."""
    gate = twonlo_gate_check()
    assert gate["gate_pass"] is False


def test_gate_check_threshold():
    gate = twonlo_gate_check()
    assert gate["gate_threshold_pct"] == GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_gate_check_2nlo_less_than_nlo():
    gate = twonlo_gate_check()
    assert gate["residual_31_2nlo_pct"] < gate["residual_31_nlo_pct"]


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict():
    summary = neutrino_2nlo_summary()
    assert isinstance(summary, dict)


def test_summary_required_keys():
    summary = neutrino_2nlo_summary()
    for key in ("residual_31_lo_pct", "residual_31_nlo_pct",
                "residual_31_2nlo_pct", "improvement_over_nlo_pct",
                "twonlo_effective_factor", "gate", "overall_status"):
        assert key in summary


def test_summary_status():
    summary = neutrino_2nlo_summary()
    assert "GEOMETRIC_ESTIMATE_CERTIFIED" in summary["overall_status"]


def test_summary_2nlo_residual_less_than_nlo():
    summary = neutrino_2nlo_summary()
    assert summary["residual_31_2nlo_pct"] < summary["residual_31_nlo_pct"]


def test_summary_improvement_positive():
    summary = neutrino_2nlo_summary()
    assert summary["improvement_over_nlo_pct"] > 0.0


def test_summary_correction_factors_dict():
    summary = neutrino_2nlo_summary()
    assert isinstance(summary["twonlo_correction_factors"], dict)
    assert len(summary["twonlo_correction_factors"]) == 9  # 3×3


def test_summary_correction_factors_diagonal_gt_one():
    summary = neutrino_2nlo_summary()
    for key in ("I_2NLO/I_LO[0,0]", "I_2NLO/I_LO[1,1]", "I_2NLO/I_LO[2,2]"):
        assert summary["twonlo_correction_factors"][key] > 1.0
