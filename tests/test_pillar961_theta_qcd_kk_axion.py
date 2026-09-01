# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 961 — θ_QCD / KK Axion from A₅."""

import math
import pytest
from src.core.pillar961_theta_qcd_kk_axion import (
    PILLAR_STATUS, PILLAR_VALID, K_CS, N_W, N_C, PI_KR, M_KK_GEV, M_PL_GEV,
    ALPHA_GUT_GEO, ALPHA_S_MKK, F_PI_GEV, LAMBDA_QCD_GEV, THETA_QCD_BOUND,
    hosotani_a5_zero_mode, kk_axion_mass, theta_qcd_relaxation,
    kk_axion_experimental_comparison, theta_qcd_status_update,
    pillar961_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "KK_QCD_AXION_MASS_COMPUTED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_C == 3
    assert abs(ALPHA_GUT_GEO - 3.0/74.0) < 1e-12
    assert abs(PI_KR - 37.0) < 1e-10


def test_lambda_qcd():
    assert abs(LAMBDA_QCD_GEV - 0.332) < 0.001


def test_theta_qcd_bound():
    assert THETA_QCD_BOUND == 1e-10


def test_hosotani_a5_zero_mode():
    result = hosotani_a5_zero_mode()
    assert "Hosotani" in result["mechanism"]
    assert "U(1)_PQ" in result["pq_symmetry_source"]
    # f_a should be computed
    assert result["f_a_kk_GeV"] > 0


def test_f_a_derived_from_mpl_and_kcs():
    result = hosotani_a5_zero_mode()
    # f_a^(KK) = M_Pl / (2π √(πkR × K_CS))
    expected = M_PL_GEV / (2 * math.pi * math.sqrt(PI_KR * K_CS))
    assert abs(result["f_a_kk_GeV"] - expected) / expected < 1e-6


def test_f_a_above_stellar_bound():
    result = hosotani_a5_zero_mode()
    assert result["above_astrophysical_bound"] is True
    assert result["f_a_kk_GeV"] > 1e8


def test_kk_axion_mass_computed():
    result = kk_axion_mass()
    assert result["m_a_eV"] > 0
    assert math.isfinite(result["m_a_eV"])


def test_kk_axion_ultra_light():
    result = kk_axion_mass()
    # With f_a ~ M_Pl scale, axion should be ultra-light
    # m_a = m_π × f_π × √(m_u m_d/(m_u+m_d)²) / f_a ~ very small
    assert result["m_a_eV"] < 1.0  # below 1 eV


def test_theta_qcd_relaxation():
    result = theta_qcd_relaxation()
    assert result["theta_relaxed_to"] == "0 (dynamically, by KK axion VEV ⟨a⟩ = −f_a × θ_bare)"
    assert result["m_a_eV"] > 0


def test_pq_quality_instanton_action():
    result = theta_qcd_relaxation()
    # Instanton action S ~ 2π/α_GUT should be large (O(100))
    assert result["pq_quality_instanton_action"] > 50


def test_experimental_consistency():
    result = kk_axion_experimental_comparison()
    assert result["experimental_constraints"]["stellar_cooling_satisfied"] is True
    assert result["experimental_constraints"]["CAST_satisfied"] is True
    assert result["overall_consistent"] is True


def test_cast_bound_satisfied():
    result = kk_axion_experimental_comparison()
    g_agg = result["g_agg_per_GeV"]
    cast_bound = result["experimental_constraints"]["CAST_bound_GeV_inv"]
    assert g_agg < cast_bound


def test_stellar_cooling_satisfied():
    result = kk_axion_experimental_comparison()
    f_a = result["f_a_GeV"]
    assert f_a > result["experimental_constraints"]["stellar_cooling_fa_bound_GeV"]


def test_status_update():
    status = theta_qcd_status_update()
    assert status["parameter"] == "P26 (θ_QCD — strong CP problem)"
    assert "KK_AXION_MECHANISM_IDENTIFIED" in status["new_status"]
    assert status["key_results"]["theta_dynamically_relaxed"] is True


def test_summary():
    s = pillar961_summary()
    assert s["pillar"] == 961
    assert s["valid"] is True
    assert "A₅" in s["key_finding"] or "A5" in s["key_finding"] or "axion" in s["key_finding"].lower()


def test_p26_addressed():
    s = pillar961_summary()
    assert "P26" in s["gap_addressed"]
