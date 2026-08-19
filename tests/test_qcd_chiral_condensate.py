# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
from __future__ import annotations

import math

import pytest

from src.core.qcd_chiral_condensate import (
    CONDENSATE_PDG_CUBERT_MEV_HIGH,
    CONDENSATE_PDG_CUBERT_MEV_LOW,
    F_PI_GEV,
    K_CS,
    M5_SQUARED_ADS,
    M_KK_GEV,
    M_PL_GEV,
    N_W,
    PI_K_R,
    PION_PDG_MEV,
    PILLAR,
    PILLAR_STATUS,
    chiral_condensate_um,
    chiral_lagrangian_coefficients,
    gor_pion_mass,
    qcd_chiral_condensate_report,
    soft_wall_kappa_um,
)


def test_constants_match_context():
    assert N_W == 5
    assert K_CS == 74
    assert PI_K_R == pytest.approx(37.0)
    assert M_KK_GEV == pytest.approx(M_PL_GEV * math.exp(-PI_K_R), rel=1e-12)
    assert M5_SQUARED_ADS == -3.0


def test_pillar_metadata():
    assert PILLAR == 774
    assert PILLAR_STATUS == "QCD_CHIRAL_CONDENSATE_DERIVED"


def test_soft_wall_kappa_returns_dict():
    result = soft_wall_kappa_um()
    assert result["status"] == "DERIVED"
    assert result["epistemic_status"] == "DERIVED"


def test_soft_wall_kappa_is_hadronic_scale():
    result = soft_wall_kappa_um()
    assert 0.35 < result["kappa_um_gev"] < 0.40


def test_soft_wall_rho_is_near_pdg():
    result = soft_wall_kappa_um()
    assert 0.70 < result["m_rho_um_gev"] < 0.85


def test_soft_wall_rho_equals_2kappa():
    result = soft_wall_kappa_um()
    assert result["m_rho_um_gev"] == pytest.approx(2.0 * result["kappa_um_gev"], rel=1e-12)


def test_invalid_soft_wall_inputs_raise():
    with pytest.raises(ValueError):
        soft_wall_kappa_um(pi_kr=0.0)
    with pytest.raises(ValueError):
        soft_wall_kappa_um(m_pl_gev=-1.0)


def test_condensate_returns_negative_gev3():
    result = chiral_condensate_um()
    assert result["status"] == "CONSTRAINED"
    assert result["chiral_condensate_gev3"] < 0
    assert result["chiral_condensate_abs_gev3"] > 0


def test_condensate_cuberoot_is_hadronic_scale():
    result = chiral_condensate_um()
    assert 260.0 < result["chiral_condensate_cuberoot_mev"] < 300.0


def test_condensate_within_reasonable_distance_of_pdg_window():
    result = chiral_condensate_um()
    assert result["chiral_condensate_cuberoot_mev"] > CONDENSATE_PDG_CUBERT_MEV_LOW
    assert result["chiral_condensate_cuberoot_mev"] < 1.2 * CONDENSATE_PDG_CUBERT_MEV_HIGH


def test_custom_kappa_changes_condensate():
    default = chiral_condensate_um()["chiral_condensate_abs_gev3"]
    modified = chiral_condensate_um(kappa_gev=0.5)["chiral_condensate_abs_gev3"]
    assert modified > default


def test_invalid_kappa_raises():
    with pytest.raises(ValueError):
        chiral_condensate_um(kappa_gev=0.0)


def test_gor_pion_mass_is_near_physical_value():
    result = gor_pion_mass()
    assert 130.0 < result["pion_mass_gor_mev"] < 140.0


def test_gor_uses_quark_mass_sum():
    result = gor_pion_mass(m_q_mev=3.5)
    assert result["m_q_sum_mev"] == pytest.approx(7.0)


def test_gor_fractional_error_is_small():
    result = gor_pion_mass()
    assert abs(result["fractional_error"]) < 0.05
    assert result["pion_pdg_mev"] == pytest.approx(PION_PDG_MEV, abs=0.1)


def test_custom_condensate_changes_pion_mass():
    default = gor_pion_mass()["pion_mass_gor_mev"]
    modified = gor_pion_mass(condensate_gev3=-0.03)["pion_mass_gor_mev"]
    assert modified > default


def test_invalid_gor_inputs_raise():
    with pytest.raises(ValueError):
        gor_pion_mass(m_q_mev=-1.0)
    with pytest.raises(ValueError):
        gor_pion_mass(f_pi_gev=0.0)


def test_chiral_lagrangian_coefficients_present():
    result = chiral_lagrangian_coefficients()
    assert result["status"] == "CONSTRAINED"
    assert result["B0_gev"] > 0
    assert result["m5_squared_ads"] == -3.0
    assert "X(z)" in result["x_profile"]


def test_report_contains_all_sections():
    report = qcd_chiral_condensate_report()
    assert report["status"] == PILLAR_STATUS
    assert report["epistemic_status"] == "CONSTRAINED"
    for key in ("kappa", "condensate", "pion", "lagrangian"):
        assert key in report


def test_report_value_matches_subreports():
    report = qcd_chiral_condensate_report()
    assert report["value"]["kappa_um_gev"] == pytest.approx(report["kappa"]["kappa_um_gev"], rel=1e-12)
    assert report["value"]["pion_mass_gor_mev"] == pytest.approx(report["pion"]["pion_mass_gor_mev"], rel=1e-12)


def test_f_pi_constant_matches_context():
    assert F_PI_GEV == pytest.approx(0.0924, rel=1e-12)
