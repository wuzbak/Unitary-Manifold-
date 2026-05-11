# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/alpha_gut_su5_complete.py — SU(5) α_GUT derivation."""
from __future__ import annotations

import math
import pytest

from src.core.alpha_gut_su5_complete import (
    N_W, K_CS, N_C, N_GEN, N_F_SU5,
    C_FUND_DYNKIN, C2_FUND_SU5,
    ALPHA_GUT_FORMULA, ALPHA_GUT_NC_KCS, ALPHA_GUT_SU5_PDG,
    PI_KR, M_KK_GEV,
    step1_su_nc_cs_dirac_condition,
    step2_pillar173_discrepancy_resolution,
    step3_su5_embedding_verification,
    residual_discrepancy_budget,
    rge_running_contribution,
    alpha_gut_su5_full_derivation,
    fallibility_status_update_alpha_gut,
    alpha_gut_su5_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_n_c():
    assert N_C == 3


def test_n_gen():
    assert N_GEN == 3


def test_n_f_su5():
    assert N_F_SU5 == 5


def test_c_fund_dynkin():
    """Dynkin index of SU(N) fundamental = 1/2."""
    assert abs(C_FUND_DYNKIN - 0.5) < 1e-14


def test_c2_fund_su5_formula():
    """C₂(SU(5)) = (5²-1)/(2×5) = 24/10 = 12/5 = 2.4."""
    expected = (N_F_SU5 ** 2 - 1) / (2.0 * N_F_SU5)
    assert abs(C2_FUND_SU5 - expected) < 1e-14


def test_alpha_gut_formula_string():
    assert "N_c" in ALPHA_GUT_FORMULA
    assert "K_CS" in ALPHA_GUT_FORMULA


def test_alpha_gut_nc_kcs_value():
    """α_GUT = N_c/K_CS = 3/74."""
    expected = 3.0 / 74.0
    assert abs(ALPHA_GUT_NC_KCS - expected) < 1e-15


def test_alpha_gut_su5_pdg_reasonable():
    """SU(5) GUT coupling ~ 1/24 ~ 0.041."""
    assert 0.03 < ALPHA_GUT_SU5_PDG < 0.06


def test_pi_kr_value():
    assert abs(PI_KR - K_CS / 2.0) < 1e-14


def test_m_kk_gev_positive():
    assert M_KK_GEV > 0.0


def test_m_kk_gev_tev_scale():
    """M_KK should be in the TeV range (10² to 10⁴ GeV)."""
    assert 1e2 < M_KK_GEV < 1e5


# ---------------------------------------------------------------------------
# Step 1 — SU(N_c) CS Dirac condition
# ---------------------------------------------------------------------------

def test_step1_returns_dict():
    result = step1_su_nc_cs_dirac_condition()
    assert isinstance(result, dict)
    for key in ("step", "alpha_gut", "g4_squared", "dirac_check", "dirac_check_ok", "status"):
        assert key in result


def test_step1_step_number():
    result = step1_su_nc_cs_dirac_condition()
    assert result["step"] == 1


def test_step1_alpha_gut_formula():
    """α = N_c/K_CS."""
    result = step1_su_nc_cs_dirac_condition()
    expected = float(N_C) / float(K_CS)
    assert abs(result["alpha_gut"] - expected) < 1e-14


def test_step1_g4_squared_formula():
    """g₄² = 4π N_c / K_CS."""
    result = step1_su_nc_cs_dirac_condition()
    expected = 4.0 * math.pi * N_C / K_CS
    assert abs(result["g4_squared"] - expected) < 1e-12


def test_step1_dirac_check():
    result = step1_su_nc_cs_dirac_condition()
    assert result["dirac_check_ok"] is True


def test_step1_status_contains_derived():
    result = step1_su_nc_cs_dirac_condition()
    assert "DERIVED" in result["status"] or "derived" in result["status"].lower()


def test_step1_custom_n_c():
    """Works for different SU(N_c)."""
    result = step1_su_nc_cs_dirac_condition(n_c=2)
    assert abs(result["alpha_gut"] - 2.0 / K_CS) < 1e-14


# ---------------------------------------------------------------------------
# Step 2 — Pillar 173 discrepancy resolution
# ---------------------------------------------------------------------------

def test_step2_returns_dict():
    result = step2_pillar173_discrepancy_resolution()
    assert isinstance(result, dict)
    for key in ("step", "alpha_pillar173", "alpha_step1", "ratio_step1_to_p173",
                "ratio_matches_expected", "status"):
        assert key in result


def test_step2_step_number():
    result = step2_pillar173_discrepancy_resolution()
    assert result["step"] == 2


def test_step2_alpha_pillar173():
    result = step2_pillar173_discrepancy_resolution()
    expected = 2.0 * math.pi / (N_C * K_CS)
    assert abs(result["alpha_pillar173"] - expected) < 1e-14


def test_step2_alpha_step1():
    result = step2_pillar173_discrepancy_resolution()
    expected = float(N_C) / float(K_CS)
    assert abs(result["alpha_step1"] - expected) < 1e-14


def test_step2_ratio_matches_expected():
    result = step2_pillar173_discrepancy_resolution()
    assert result["ratio_matches_expected"] is True


def test_step2_expected_ratio_formula():
    """Ratio = N_c² / (2π)."""
    result = step2_pillar173_discrepancy_resolution()
    expected_ratio = N_C ** 2 / (2.0 * math.pi)
    assert abs(result["expected_ratio_nc_sq_over_2pi"] - expected_ratio) < 1e-12


def test_step2_status_contains_resolved():
    result = step2_pillar173_discrepancy_resolution()
    assert "RESOLVED" in result["status"] or "convention" in result["status"].lower()


# ---------------------------------------------------------------------------
# Step 3 — SU(5) embedding
# ---------------------------------------------------------------------------

def test_step3_returns_dict():
    result = step3_su5_embedding_verification()
    assert isinstance(result, dict)
    for key in ("step", "alpha_nc_kcs", "alpha_su5_pdg", "pct_error_raw",
                "agrees_at_2pct", "status"):
        assert key in result


def test_step3_step_number():
    result = step3_su5_embedding_verification()
    assert result["step"] == 3


def test_step3_alpha_nc_kcs():
    result = step3_su5_embedding_verification()
    expected = float(N_C) / float(K_CS)
    assert abs(result["alpha_nc_kcs"] - expected) < 1e-14


def test_step3_agrees_at_2pct():
    """N_c/K_CS should agree with SU(5) GUT value at < 2%."""
    result = step3_su5_embedding_verification()
    assert result["agrees_at_2pct"] is True


def test_step3_pct_error_raw_positive():
    result = step3_su5_embedding_verification()
    assert math.isfinite(result["pct_error_raw"])
    assert result["pct_error_raw"] < 5.0   # within 5% of SU(5) GUT


def test_step3_su5_casimir_value():
    result = step3_su5_embedding_verification()
    assert abs(result["c2_su5"] - 2.4) < 1e-10


def test_step3_su3_casimir_formula():
    """C₂(SU(3)) = (N_c²-1)/(2N_c) = 4/3."""
    result = step3_su5_embedding_verification()
    expected = float(N_C ** 2 - 1) / (2.0 * N_C)
    assert abs(result["c2_su3"] - expected) < 1e-12


def test_step3_gamma_su5_close_to_one():
    """SU(5) Casimir correction should be small: γ ≈ 1 ± 5%."""
    result = step3_su5_embedding_verification()
    assert 0.9 < result["gamma_su5_correction"] < 1.1


# ---------------------------------------------------------------------------
# Residual discrepancy budget
# ---------------------------------------------------------------------------

def test_residual_budget_returns_dict():
    result = residual_discrepancy_budget()
    assert isinstance(result, dict)
    for key in ("total_discrepancy_pct", "su5_casimir_correction_pct",
                "rge_running_correction_pct", "residual_unaccounted_pct"):
        assert key in result


def test_residual_budget_total_discrepancy_small():
    result = residual_discrepancy_budget()
    # Total discrepancy ~ 1.7%
    assert abs(result["total_discrepancy_pct"]) < 5.0


def test_residual_budget_su5_correction_positive():
    """SU(5) Casimir correction should be positive (moves α toward SU(5) value)."""
    result = residual_discrepancy_budget()
    assert result["su5_casimir_correction_pct"] > 0.0


def test_residual_budget_dominant_contribution():
    result = residual_discrepancy_budget()
    assert "Casimir" in result["dominant_contribution"] or "SU(5)" in result["dominant_contribution"]


# ---------------------------------------------------------------------------
# RGE running
# ---------------------------------------------------------------------------

def test_rge_running_returns_dict():
    result = rge_running_contribution()
    assert isinstance(result, dict)
    for key in ("b0_1loop", "log_M_GUT_over_M_KK", "alpha_at_M_KK",
                "alpha_at_M_GUT_rge", "pct_change_from_running"):
        assert key in result


def test_rge_running_b0_positive():
    """With N_f=6 and N_c=3: b₀ = (33-12)/(4π) = 21/(4π) > 0."""
    result = rge_running_contribution()
    assert result["b0_1loop"] > 0.0


def test_rge_running_log_ratio_large():
    """ln(M_GUT/M_KK) ≈ ln(2×10¹³) ≈ 30 — large logarithm."""
    result = rge_running_contribution()
    assert result["log_M_GUT_over_M_KK"] > 20.0


def test_rge_running_alpha_at_kk():
    result = rge_running_contribution()
    expected = float(N_C) / float(K_CS)
    assert abs(result["alpha_at_M_KK"] - expected) < 1e-14


def test_rge_running_gut_finite():
    result = rge_running_contribution()
    assert math.isfinite(result["alpha_at_M_GUT_rge"])
    assert result["alpha_at_M_GUT_rge"] > 0.0


# ---------------------------------------------------------------------------
# Full derivation
# ---------------------------------------------------------------------------

def test_full_derivation_returns_dict():
    result = alpha_gut_su5_full_derivation()
    assert isinstance(result, dict)
    for key in ("formula", "alpha_gut", "step1", "step2", "step3",
                "all_steps_ok", "previous_status", "new_status"):
        assert key in result


def test_full_derivation_alpha_gut():
    result = alpha_gut_su5_full_derivation()
    assert abs(result["alpha_gut"] - ALPHA_GUT_NC_KCS) < 1e-15


def test_full_derivation_all_steps_ok():
    result = alpha_gut_su5_full_derivation()
    assert result["all_steps_ok"] is True


def test_full_derivation_previous_status():
    result = alpha_gut_su5_full_derivation()
    assert "POSTULATED" in result["previous_status"]


def test_full_derivation_new_status_constrained():
    result = alpha_gut_su5_full_derivation()
    assert "CONSTRAINED" in result["new_status"]


def test_full_derivation_pct_error_within_2pct():
    result = alpha_gut_su5_full_derivation()
    assert result["pct_error_to_pdg"] < 2.0


# ---------------------------------------------------------------------------
# Fallibility status update
# ---------------------------------------------------------------------------

def test_fallibility_status_update_returns_dict():
    result = fallibility_status_update_alpha_gut()
    assert isinstance(result, dict)
    for key in ("fallibility_section", "old_label", "new_label", "quantity", "module"):
        assert key in result


def test_fallibility_old_label():
    result = fallibility_status_update_alpha_gut()
    assert "POSTULATED" in result["old_label"]


def test_fallibility_new_label_constrained():
    result = fallibility_status_update_alpha_gut()
    assert "CONSTRAINED" in result["new_label"]


def test_fallibility_module_path():
    result = fallibility_status_update_alpha_gut()
    assert "alpha_gut_su5_complete" in result["module"]


def test_fallibility_quantity():
    result = fallibility_status_update_alpha_gut()
    assert "K_CS" in result["quantity"] or "k_CS" in result["quantity"]


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict():
    result = alpha_gut_su5_summary()
    assert isinstance(result, dict)
    for key in ("version", "title", "formula", "alpha_gut", "status",
                "previous_status", "n_steps", "fallibility_update"):
        assert key in result


def test_summary_n_steps():
    result = alpha_gut_su5_summary()
    assert result["n_steps"] == 3


def test_summary_status_constrained():
    result = alpha_gut_su5_summary()
    assert "CONSTRAINED" in result["status"]


def test_summary_pct_error_finite():
    result = alpha_gut_su5_summary()
    assert math.isfinite(result["pct_error"])
    assert result["pct_error"] < 5.0


def test_summary_key_result_present():
    result = alpha_gut_su5_summary()
    assert len(result["key_result"]) > 20
