# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 960 — Higgs Mass from GW Potential."""

import math
import pytest
from src.core.pillar960_higgs_mass_gw_potential import (
    PILLAR_STATUS, PILLAR_VALID, N_W, K_CS, N_C, PI_KR, ALPHA_PHI,
    M_KK_GEV, M_HIGGS_EXP_GEV, V_HIGGS_GEV, G_W_MKK,
    gw_radion_mass, hosotani_higgs_mass_estimate, brane_mass_higgs_estimate,
    higgs_mass_geometric_bound, fallibility_update, pillar960_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "HIGGS_MASS_GW_BOUNDED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_m_higgs_exp():
    assert abs(M_HIGGS_EXP_GEV - 125.25) < 0.01


def test_m_kk():
    assert abs(M_KK_GEV - 760.0) < 1.0


def test_alpha_phi():
    expected = math.sqrt(8.0 * N_W / K_CS)
    assert abs(ALPHA_PHI - expected) < 1e-10


def test_pi_kr():
    assert abs(PI_KR - 37.0) < 1e-10


def test_gw_radion_mass():
    result = gw_radion_mass()
    assert result["status"] == "DERIVED_PILLAR_404"
    expected_m_phi = ALPHA_PHI * M_KK_GEV
    assert abs(result["m_phi_GeV"] - expected_m_phi) < 1.0


def test_radion_mass_order_mkk():
    result = gw_radion_mass()
    # Radion mass should be order M_KK
    assert 0.5 * M_KK_GEV < result["m_phi_GeV"] < 2.0 * M_KK_GEV


def test_hosotani_too_light():
    result = hosotani_higgs_mass_estimate()
    assert result["status"] == "TOO_LIGHT_BY_FACTOR"
    assert result["m_H_hosotani_GeV"] < M_HIGGS_EXP_GEV


def test_hosotani_gap_factor():
    result = hosotani_higgs_mass_estimate()
    # Should be much lighter than observed (gap factor >> 1)
    assert result["gap_factor"] > 10


def test_brane_fine_tuning_required():
    result = brane_mass_higgs_estimate()
    assert result["fine_tuning_required"] is True
    assert result["lambda_UV_required"] < 0.1  # lambda_UV << 1


def test_geometric_ratio():
    result = higgs_mass_geometric_bound()
    expected_ratio = math.sqrt(N_C / K_CS)
    assert abs(result["sqrt_alpha_gut"] - expected_ratio) < 1e-6


def test_geometric_prediction_in_window():
    result = higgs_mass_geometric_bound()
    assert result["observed_in_window"] is True
    # Hosotani lower bound < observed < KK upper bound
    assert result["hosotani_lower_GeV"] < M_HIGGS_EXP_GEV < result["kk_upper_GeV"]


def test_geometric_22pct():
    result = higgs_mass_geometric_bound()
    assert result["geometric_estimate_within_30pct"] is True


def test_geometric_prediction_value():
    result = higgs_mass_geometric_bound()
    # Prediction: √(3/74) × 760 ≈ 153 GeV
    expected = math.sqrt(3.0 / 74.0) * M_KK_GEV
    assert abs(result["m_H_geometric_pred_GeV"] - expected) < 1.0


def test_lambda_h_sm():
    result = brane_mass_higgs_estimate()
    # λ_H = 2 m_H²/v_H² ≈ 0.129 (SM tree level)
    expected = 2 * M_HIGGS_EXP_GEV**2 / V_HIGGS_GEV**2
    assert abs(result["lambda_H_SM_tree"] - expected) < 0.01


def test_fallibility_update():
    fb = fallibility_update()
    assert fb["parameter"] == "P5 (m_H = 125.25 GeV)"
    assert "GEOMETRIC" in fb["new_status"]
    assert fb["pillar"] == 960


def test_summary():
    s = pillar960_summary()
    assert s["pillar"] == 960
    assert s["valid"] is True
    assert "22%" in s["key_finding"] or "153" in s["key_finding"]


def test_architecture_limit_honest():
    s = pillar960_summary()
    assert "fine-tuning" in s["honest_architecture_limit"].lower() or "too light" in s["honest_architecture_limit"].lower()
