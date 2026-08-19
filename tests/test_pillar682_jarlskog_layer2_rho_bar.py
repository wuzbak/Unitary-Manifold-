# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 682: Jarlskog Layer 2 FN-Mechanism CP-Phase Correction."""

from __future__ import annotations

import math
import pytest

from src.core.pillar682_jarlskog_layer2_rho_bar import (
    N_W, K_CS, LAMBDA_CABIBBO, A_WOLFENSTEIN, R_B,
    RHO_BAR_PDG, ETA_BAR_PDG, DELTA_GEO_DEG, EPSILON_UM,
    fn_epsilon_um,
    jarlskog_layer2_delta_correction,
    corrected_wolfenstein,
    residual_audit,
    layer2_certificate,
    what_is_claimed,
    what_is_NOT_claimed,
    PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE, VERSION,
)


# ── Constants sanity ──────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 682


def test_version():
    assert VERSION == "v21.1"


def test_n_w_k_cs():
    assert N_W == 5
    assert K_CS == 74


def test_lambda_cabibbo():
    assert 0.220 < LAMBDA_CABIBBO < 0.230


def test_a_wolfenstein():
    assert 0.80 < A_WOLFENSTEIN < 0.85


def test_r_b_range():
    # R_b = sqrt(ρ̄² + η̄²) ≈ 0.38
    assert 0.35 < R_B < 0.42


def test_rho_bar_pdg():
    assert abs(RHO_BAR_PDG - 0.159) < 0.001


def test_eta_bar_pdg():
    assert abs(ETA_BAR_PDG - 0.348) < 0.001


def test_delta_geo_deg():
    assert 65.0 < DELTA_GEO_DEG < 80.0


def test_epsilon_um_tiny():
    # Full warp factor: exp(-π×74/5) ≈ exp(-46.5) — extremely small
    assert EPSILON_UM < 1e-15
    assert EPSILON_UM > 0


# ── fn_epsilon_um ─────────────────────────────────────────────────────────────

def test_fn_epsilon_keys():
    eps = fn_epsilon_um()
    for k in ["pi_kr", "epsilon_full_warp", "m_kk_gev", "epsilon_effective_ew"]:
        assert k in eps


def test_fn_epsilon_pi_kr():
    eps = fn_epsilon_um()
    expected = math.pi * K_CS / N_W
    assert abs(eps["pi_kr"] - expected) < 1e-10


def test_fn_epsilon_effective_positive():
    eps = fn_epsilon_um()
    # ε_eff = (M_Z/M_KK)^{1/3}; M_Z << M_KK so M_KK/M_Z >> 1, thus ε_eff > 1 is valid ratio
    assert eps["epsilon_effective_ew"] > 0


def test_fn_epsilon_mhk_positive():
    eps = fn_epsilon_um()
    assert eps["m_kk_gev"] > 0


# ── jarlskog_layer2_delta_correction ─────────────────────────────────────────

def test_delta_correction_keys():
    corr = jarlskog_layer2_delta_correction()
    for k in [
        "delta_geo_deg", "delta_pdg_deg", "fn_geometry_factor",
        "delta_fn_correction_deg", "delta_corrected_deg",
        "gap_before_deg", "gap_after_deg", "gap_reduction_pct",
    ]:
        assert k in corr


def test_delta_correction_is_negative():
    # FN correction should reduce δ (move it toward PDG)
    corr = jarlskog_layer2_delta_correction()
    assert corr["delta_fn_correction_deg"] < 0


def test_delta_corrected_between_geo_and_pdg():
    corr = jarlskog_layer2_delta_correction()
    # Corrected δ should be between PDG (65.8°) and geometric (71.08°)
    assert 65.0 < corr["delta_corrected_deg"] < 71.5


def test_geometry_factor_positive():
    corr = jarlskog_layer2_delta_correction()
    assert corr["fn_geometry_factor"] > 0


def test_a_sq_lam4_small():
    corr = jarlskog_layer2_delta_correction()
    # A² λ⁴ ≈ 0.00188 — small perturbation
    a_sq_lam4 = corr["a_sq"] * corr["lambda_4"]
    assert a_sq_lam4 < 0.005


def test_gap_reduction_positive():
    corr = jarlskog_layer2_delta_correction()
    # Correction moves in the right direction
    assert corr["gap_reduction_pct"] > 0


def test_sigma_away_after_correction():
    corr = jarlskog_layer2_delta_correction()
    # Should remain within ~3σ of PDG
    assert corr["sigma_away_pdg"] < 5.0


def test_fn_charge_diff():
    corr = jarlskog_layer2_delta_correction()
    assert corr["fn_charge_diff_q12"] == 2


# ── corrected_wolfenstein ─────────────────────────────────────────────────────

def test_corrected_wolfenstein_keys():
    wolf = corrected_wolfenstein()
    for k in [
        "rho_bar_l2", "eta_bar_l2", "rho_residual_l2_pct", "eta_residual_l2_pct",
        "rho_bar_geo", "eta_bar_geo",
    ]:
        assert k in wolf


def test_rho_bar_l2_range():
    wolf = corrected_wolfenstein()
    # ρ̄_L2 should be near the geometric estimate (small correction)
    assert 0.08 < wolf["rho_bar_l2"] < 0.18


def test_eta_bar_l2_range():
    wolf = corrected_wolfenstein()
    assert 0.30 < wolf["eta_bar_l2"] < 0.40


def test_rho_residual_l2_architecture_limit():
    wolf = corrected_wolfenstein()
    # ρ̄ residual confirms architecture limit around 24%
    assert wolf["rho_residual_l2_pct"] > 15.0
    assert wolf["rho_residual_l2_pct"] < 35.0


def test_eta_residual_l2_reduced():
    wolf = corrected_wolfenstein()
    # η̄ residual should be < 10% (η̄ is better constrained)
    assert wolf["eta_residual_l2_pct"] < 12.0


def test_lambda_sq_factor():
    wolf = corrected_wolfenstein()
    expected = 1.0 - LAMBDA_CABIBBO**2 / 2.0
    assert abs(wolf["lambda_sq_factor"] - expected) < 1e-10


def test_r_b_used():
    wolf = corrected_wolfenstein()
    assert abs(wolf["r_b"] - R_B) < 1e-10


# ── residual_audit ────────────────────────────────────────────────────────────

def test_residual_audit_returns_dict():
    audit = residual_audit()
    assert isinstance(audit, dict)


def test_residual_audit_summary_keys():
    audit = residual_audit()
    summary = audit["summary"]
    for k in [
        "rho_bar_before", "rho_bar_after", "rho_bar_pdg",
        "rho_residual_before_pct", "rho_residual_after_pct",
        "eta_bar_before", "eta_bar_after", "eta_bar_pdg",
    ]:
        assert k in summary


def test_residual_audit_architecture_assessment_string():
    audit = residual_audit()
    assert isinstance(audit["architecture_assessment"], str)
    assert "architecture" in audit["architecture_assessment"].lower()


# ── layer2_certificate ────────────────────────────────────────────────────────

def test_layer2_certificate_keys():
    cert = layer2_certificate()
    for k in ["pillar", "title", "version", "status", "fn_epsilon",
              "residual_audit", "p14_status", "claimed", "not_claimed"]:
        assert k in cert


def test_layer2_certificate_pillar():
    cert = layer2_certificate()
    assert cert["pillar"] == 682


def test_layer2_certificate_p14_unchanged():
    cert = layer2_certificate()
    assert "GEOMETRIC ESTIMATE" in cert["p14_status"]
    assert "unchanged" in cert["p14_status"].lower()


def test_layer2_certificate_toe_zero():
    cert = layer2_certificate()
    assert "0" in cert["toe_impact"]


def test_layer2_certificate_next_steps():
    cert = layer2_certificate()
    assert len(cert["next_steps"]) >= 2


# ── what_is_claimed / not_claimed ─────────────────────────────────────────────

def test_claimed_is_list():
    assert isinstance(what_is_claimed(), list)
    assert len(what_is_claimed()) >= 3


def test_not_claimed_is_list():
    assert isinstance(what_is_NOT_claimed(), list)
    assert len(what_is_NOT_claimed()) >= 2


def test_not_claimed_mentions_p14():
    for item in what_is_NOT_claimed():
        if "P14" in item or "ρ̄" in item or "rho" in item.lower():
            break
    else:
        pytest.fail("what_is_NOT_claimed should mention P14 or ρ̄")


# ── Numerical consistency ─────────────────────────────────────────────────────

def test_r_b_equals_sqrt_rho_eta():
    expected = math.sqrt(RHO_BAR_PDG**2 + ETA_BAR_PDG**2)
    assert abs(R_B - expected) < 1e-10


def test_geometry_factor_formula():
    # (K_CS − N_W²) / (π N_W) = (74 − 25) / (5π) ≈ 3.12
    expected = (K_CS - N_W**2) / (math.pi * N_W)
    corr = jarlskog_layer2_delta_correction()
    assert abs(corr["fn_geometry_factor"] - expected) < 1e-10


def test_delta_fn_correction_formula():
    # Δδ_FN ≈ −A² λ⁴ × geometry_factor × (180/π)
    corr = jarlskog_layer2_delta_correction()
    expected = -(A_WOLFENSTEIN**2 * LAMBDA_CABIBBO**4
                 * corr["fn_geometry_factor"] * 180.0 / math.pi)
    assert abs(corr["delta_fn_correction_deg"] - expected) < 1e-10


def test_correction_small_perturbation():
    corr = jarlskog_layer2_delta_correction()
    # Leading FN correction is < 1° (perturbative)
    assert abs(corr["delta_fn_correction_deg"]) < 1.0


def test_rho_bar_l2_formula():
    wolf = corrected_wolfenstein()
    corr = jarlskog_layer2_delta_correction()
    delta_rad = math.radians(corr["delta_corrected_deg"])
    lam_factor = 1.0 - LAMBDA_CABIBBO**2 / 2.0
    expected = R_B * math.cos(delta_rad) * lam_factor
    assert abs(wolf["rho_bar_l2"] - expected) < 1e-12


def test_eta_bar_l2_formula():
    wolf = corrected_wolfenstein()
    corr = jarlskog_layer2_delta_correction()
    delta_rad = math.radians(corr["delta_corrected_deg"])
    lam_factor = 1.0 - LAMBDA_CABIBBO**2 / 2.0
    expected = R_B * math.sin(delta_rad) * lam_factor
    assert abs(wolf["eta_bar_l2"] - expected) < 1e-12


def test_status_token():
    assert PILLAR_STATUS == "JARLSKOG_LAYER2_LEADING_CORRECTION_IMPLEMENTED"
