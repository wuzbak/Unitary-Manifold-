# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 973 — m_ν₁ geometric estimate."""

import math

from src.core.pillar973_mnu1_geometric_estimate import (
    C_R,
    C_S,
    DM21_SQ_EV2,
    DM31_SQ_EV2,
    EXP_BOUND_EV,
    HBAR_C_MEV_FM,
    K_CS,
    METERS_TO_FM,
    M_KK_EV,
    M_NU1_ESTIMATE_EV,
    N_W,
    PILLAR_STATUS,
    PILLAR_VALID,
    R_KK_FM,
    R_KK_METERS,
    SIGMA_M_NU_ANCHOR_EV,
    fallibility_update,
    m_kk_from_r_kk,
    m_nu1_experimental_check,
    m_nu1_seesaw_estimate,
    neutrino_spectrum_check,
    pillar973_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "MNU1_GEOMETRIC_ESTIMATE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_core_constants():
    assert N_W == 5
    assert K_CS == 74


def test_c_r_value():
    assert abs(C_R - 23.0 / 25.0) < 1e-12


def test_r_kk_fm_conversion():
    assert abs(R_KK_FM - R_KK_METERS * METERS_TO_FM) < 1e-3
    assert abs(R_KK_FM - 1.792e9) < 1.0


def test_m_kk_scale_value():
    assert abs(M_KK_EV - 0.11010044642857143) < 1e-12


def test_m_kk_function_formula():
    result = m_kk_from_r_kk()
    assert result["formula"] == "hbar_c/R_KK"


def test_m_kk_function_matches_constant():
    result = m_kk_from_r_kk()
    assert abs(result["M_KK_eV"] - M_KK_EV) < 1e-15


def test_m_kk_manual_formula():
    expected = HBAR_C_MEV_FM / R_KK_FM * 1.0e6
    assert abs(M_KK_EV - expected) < 1e-15


def test_c_s_value():
    assert abs(C_S - 12.0 / 37.0) < 1e-12


def test_c_s_squared_value():
    estimate = m_nu1_seesaw_estimate()
    assert abs(estimate["c_s_sq"] - (12.0 / 37.0) ** 2) < 1e-15


def test_m_nu1_estimate_matches_formula():
    estimate = m_nu1_seesaw_estimate()
    assert abs(estimate["m_nu1_eV"] - M_KK_EV * C_S ** 2) < 1e-15


def test_m_nu1_estimate_value():
    assert abs(M_NU1_ESTIMATE_EV - 0.011581054993217156) < 1e-15


def test_m_nu1_is_below_bound():
    assert M_NU1_ESTIMATE_EV < EXP_BOUND_EV


def test_experimental_check_within_bound():
    check = m_nu1_experimental_check()
    assert check["within_bound"] is True
    assert check["margin_meV"] > 0.0


def test_spectrum_is_normal_hierarchy():
    spectrum = neutrino_spectrum_check()
    assert spectrum["normal_hierarchy_consistent"] is True


def test_spectrum_masses_are_ordered():
    spectrum = neutrino_spectrum_check()
    assert spectrum["m_nu1_eV"] < spectrum["m_nu2_eV"] < spectrum["m_nu3_eV"]


def test_spectrum_reproduces_dm21():
    spectrum = neutrino_spectrum_check()
    assert abs(spectrum["dm21_sq_eV2"] - DM21_SQ_EV2) < 1e-12


def test_spectrum_reproduces_dm31():
    spectrum = neutrino_spectrum_check()
    assert abs(spectrum["dm31_sq_eV2"] - DM31_SQ_EV2) < 1e-12


def test_sum_is_below_sigma_anchor():
    spectrum = neutrino_spectrum_check()
    assert spectrum["sum_m_nu_eV"] < SIGMA_M_NU_ANCHOR_EV
    assert spectrum["within_sigma_anchor"] is True


def test_nh_window_consistency():
    spectrum = neutrino_spectrum_check()
    assert spectrum["nh_window_consistent"] is True


def test_fallibility_update_status():
    update = fallibility_update()
    assert "GEOMETRIC_ESTIMATE" in update["new_status"]
    assert update["pillar"] == 973


def test_summary_keys():
    summary = pillar973_summary()
    assert summary["pillar"] == 973
    assert summary["valid"] is True
    assert len(summary["derivation_chain"]) >= 6


def test_summary_estimate_consistency():
    summary = pillar973_summary()
    assert math.isclose(
        summary["estimate"]["m_nu1_eV"],
        M_NU1_ESTIMATE_EV,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
