# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar404_lambda_gw_derivation.py
============================================
Tests for Pillar 404 — λ_GW Natural Scale Derivation.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar404_lambda_gw_derivation import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    N_W,
    K_CS,
    PI_KR,
    PHI0_BRAID,
    M_KK_GEV,
    M_PL_BAR_GEV,
    NU_GW,
    ALPHA_PHI,
    M_PHI_GEV,
    LAMBDA_GW_NATURAL,
    T_RH_GEV,
    N_E_DERIVED,
    G_STAR_RH,
    H_INF_GEV,
    gw_normalization_condition,
    lambda_gw_from_geometry,
    radion_mass_from_lambda_gw,
    kk_decay_rate,
    reheating_temperature,
    ne_from_chain,
    admission_6_closure_verdict,
    admission_11_closure_verdict,
    pillar404_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 404

    def test_pillar_status(self):
        assert PILLAR_STATUS == "DERIVED_FROM_GW_NORMALIZATION"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_phi0_formula(self):
        assert PHI0_BRAID == pytest.approx(5.0 * math.pi / 74.0, rel=1e-9)

    def test_nu_gw_is_lattice_step(self):
        assert NU_GW == pytest.approx(N_W / K_CS, rel=1e-9)

    def test_alpha_phi_formula(self):
        assert ALPHA_PHI == pytest.approx(math.sqrt(8.0 * NU_GW), rel=1e-9)

    def test_alpha_phi_range(self):
        # Should be O(1) and less than 2
        assert 0.3 < ALPHA_PHI < 2.0

    def test_m_phi_gev_near_mkk(self):
        # m_φ should be O(M_KK) ≈ 764 GeV
        assert 0.1 * M_KK_GEV < M_PHI_GEV < 5.0 * M_KK_GEV

    def test_lambda_gw_natural_positive(self):
        assert LAMBDA_GW_NATURAL > 0.0

    def test_t_rh_positive(self):
        assert T_RH_GEV > 0.0

    def test_g_star_rh(self):
        assert G_STAR_RH == pytest.approx(106.75, rel=1e-6)

    def test_h_inf_positive(self):
        assert H_INF_GEV > 0.0


# ─────────────────────────────────────────────────────────────────────────────
# GW normalization condition
# ─────────────────────────────────────────────────────────────────────────────

class TestGwNormalizationCondition:
    def test_returns_dict(self):
        r = gw_normalization_condition()
        assert isinstance(r, dict)

    def test_nu_gw_in_result(self):
        r = gw_normalization_condition()
        assert r["nu_gw"] == pytest.approx(NU_GW, rel=1e-9)

    def test_alpha_phi_lo_formula(self):
        r = gw_normalization_condition()
        expected = math.sqrt(8.0 * NU_GW)
        assert r["alpha_phi_lo"] == pytest.approx(expected, rel=1e-9)

    def test_alpha_phi_nlo_greater_lo(self):
        r = gw_normalization_condition()
        assert r["alpha_phi_nlo"] > r["alpha_phi_lo"]

    def test_key_identification_present(self):
        r = gw_normalization_condition()
        assert "n_w" in r["key_identification"].lower() or "5" in r["key_identification"]

    def test_invalid_nu_raises(self):
        with pytest.raises(ValueError):
            gw_normalization_condition(nu_gw=-0.1)

    def test_n_warp_factor_near_half(self):
        r = gw_normalization_condition()
        # (1 - e^{-74}) / 2 ≈ 0.5
        assert r["n_warp_factor"] == pytest.approx(0.5, abs=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# Lambda GW from geometry
# ─────────────────────────────────────────────────────────────────────────────

class TestLambdaGwFromGeometry:
    def test_returns_dict(self):
        r = lambda_gw_from_geometry()
        assert isinstance(r, dict)

    def test_alpha_phi_consistent(self):
        r = lambda_gw_from_geometry()
        assert r["alpha_phi"] == pytest.approx(ALPHA_PHI, rel=1e-9)

    def test_m_phi_consistent(self):
        r = lambda_gw_from_geometry()
        assert r["m_phi_gev"] == pytest.approx(M_PHI_GEV, rel=1e-9)

    def test_lambda_gw_natural_units_order_1(self):
        r = lambda_gw_from_geometry()
        # Natural λ_GW should be within order of magnitude of 1
        assert 0.01 < r["lambda_gw_natural_units"] < 1000.0

    def test_is_natural(self):
        r = lambda_gw_from_geometry()
        assert r["is_natural"]

    def test_verdict_contains_closed(self):
        r = lambda_gw_from_geometry()
        assert "DERIVED" in r["verdict"] or "closed" in r["verdict"].lower() or "Admission" in r["verdict"]

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            lambda_gw_from_geometry(phi0=-1.0)

    def test_invalid_mkk_raises(self):
        with pytest.raises(ValueError):
            lambda_gw_from_geometry(m_kk_gev=-100.0)

    def test_m_phi_over_m_kk_near_alpha(self):
        r = lambda_gw_from_geometry()
        assert r["m_phi_over_m_kk"] == pytest.approx(ALPHA_PHI, rel=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# Radion mass from lambda_gw
# ─────────────────────────────────────────────────────────────────────────────

class TestRadionMassFromLambdaGw:
    def test_returns_dict(self):
        r = radion_mass_from_lambda_gw()
        assert isinstance(r, dict)

    def test_m_phi_consistent(self):
        r = radion_mass_from_lambda_gw()
        assert r["m_phi_gev"] == pytest.approx(M_PHI_GEV, rel=1e-4)

    def test_consistent_with_mkk(self):
        r = radion_mass_from_lambda_gw()
        assert r["consistent_with_mkk"]

    def test_m_phi_positive(self):
        r = radion_mass_from_lambda_gw()
        assert r["m_phi_gev"] > 0.0

    def test_verdict_mentions_naturalness(self):
        r = radion_mass_from_lambda_gw()
        assert "natural" in r["verdict"].lower() or "M_KK" in r["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# KK decay rate
# ─────────────────────────────────────────────────────────────────────────────

class TestKkDecayRate:
    def test_returns_dict(self):
        r = kk_decay_rate()
        assert isinstance(r, dict)

    def test_gamma_kk_positive(self):
        r = kk_decay_rate()
        assert r["gamma_kk_gev"] > 0.0

    def test_gamma_kk_formula(self):
        r = kk_decay_rate()
        # Uses RS1 radion coupling Lambda_phi = sqrt(6)*M_KK/(x1*K_OVER_MPl)
        import math
        LAMBDA_PHI = math.sqrt(6.0) * M_KK_GEV / (3.8317 * 0.10)
        expected = M_PHI_GEV ** 3 / (16.0 * math.pi * LAMBDA_PHI ** 2)
        assert r["gamma_kk_gev"] == pytest.approx(expected, rel=0.01)

    def test_gamma_kk_sub_planckian(self):
        r = kk_decay_rate()
        assert r["gamma_kk_gev"] < M_PL_BAR_GEV

    def test_invalid_m_phi_raises(self):
        with pytest.raises(ValueError):
            kk_decay_rate(m_phi_gev=-100.0)


# ─────────────────────────────────────────────────────────────────────────────
# Reheating temperature
# ─────────────────────────────────────────────────────────────────────────────

class TestReheatTemperature:
    def test_returns_dict(self):
        r = reheating_temperature()
        assert isinstance(r, dict)

    def test_t_rh_positive(self):
        r = reheating_temperature()
        assert r["t_rh_gev"] > 0.0

    def test_above_bbn(self):
        r = reheating_temperature()
        assert r["above_bbn"]

    def test_below_inflation(self):
        r = reheating_temperature()
        assert r["below_inflation"]

    def test_t_rh_consistent(self):
        r = reheating_temperature()
        assert r["t_rh_gev"] == pytest.approx(T_RH_GEV, rel=0.1)

    def test_invalid_gamma_raises(self):
        with pytest.raises(ValueError):
            reheating_temperature(gamma_kk_gev=-1.0)


# ─────────────────────────────────────────────────────────────────────────────
# N_e from chain
# ─────────────────────────────────────────────────────────────────────────────

class TestNeFromChain:
    def test_returns_dict(self):
        r = ne_from_chain()
        assert isinstance(r, dict)

    def test_n_e_in_reasonable_range(self):
        r = ne_from_chain()
        assert 40.0 < r["n_e_derived"] < 80.0

    def test_within_planck_range(self):
        r = ne_from_chain()
        assert r["within_planck_range"]

    def test_n_e_pillar346_in_result(self):
        r = ne_from_chain()
        assert r["n_e_pillar346"] == pytest.approx(58.3, rel=0.01)

    def test_sigma_from_p346_reasonable(self):
        r = ne_from_chain()
        # Should be within a few sigma of Pillar 346
        assert r["sigma_from_p346"] < 10.0

    def test_verdict_mentions_closed(self):
        r = ne_from_chain()
        assert "CLOSED" in r["verdict"] or "derived" in r["verdict"].lower()

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError):
            ne_from_chain(t_rh_gev=-1.0)

    def test_invalid_h_inf_raises(self):
        with pytest.raises(ValueError):
            ne_from_chain(h_inf_gev=0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Admission 6 closure verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission6ClosureVerdict:
    def test_returns_dict(self):
        r = admission_6_closure_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_6_closure_verdict()
        assert r["admission"] == 6

    def test_previous_status(self):
        r = admission_6_closure_verdict()
        assert r["previous_status"] == "ARCHITECTURE_LIMIT"

    def test_new_status(self):
        r = admission_6_closure_verdict()
        assert r["new_status"] == "DERIVED_FROM_GW_NORMALIZATION"

    def test_lambda_gw_natural(self):
        r = admission_6_closure_verdict()
        assert r["lambda_gw_is_natural"]

    def test_derivation_chain_present(self):
        r = admission_6_closure_verdict()
        assert "ν" in r["derivation_chain"] or "nu" in r["derivation_chain"].lower()

    def test_nu_gw_derived_value(self):
        r = admission_6_closure_verdict()
        assert r["nu_gw_derived"] == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_citation_present(self):
        r = admission_6_closure_verdict()
        assert "pillar404" in r["citation"].lower() or "Pillar 404" in r["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Admission 11 closure verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission11ClosureVerdict:
    def test_returns_dict(self):
        r = admission_11_closure_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_11_closure_verdict()
        assert r["admission"] == 11

    def test_previous_status(self):
        r = admission_11_closure_verdict()
        assert r["previous_status"] == "CONDITIONALLY_CLOSED"

    def test_new_status(self):
        r = admission_11_closure_verdict()
        assert r["new_status"] == "CLOSED"

    def test_dependency_closed(self):
        r = admission_11_closure_verdict()
        assert "Admission 6" in r["dependency_closed"] or "Adm. 6" in r["dependency_closed"]

    def test_n_e_derived_present(self):
        r = admission_11_closure_verdict()
        assert r["n_e_derived"] > 0.0

    def test_within_planck(self):
        r = admission_11_closure_verdict()
        assert r["within_planck"]

    def test_full_chain_present(self):
        r = admission_11_closure_verdict()
        assert "λ_GW" in r["full_chain"] or "lambda" in r["full_chain"].lower()

    def test_honest_residual_present(self):
        r = admission_11_closure_verdict()
        assert len(r["honest_residual"]) > 50

    def test_citation_present(self):
        r = admission_11_closure_verdict()
        assert "pillar404" in r["citation"].lower() or "Pillar 404" in r["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Full summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar404Summary:
    def test_returns_dict(self):
        r = pillar404_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar404_summary()
        assert r["pillar_number"] == 404

    def test_status(self):
        r = pillar404_summary()
        assert r["status"] == "DERIVED_FROM_GW_NORMALIZATION"

    def test_admissions_closed(self):
        r = pillar404_summary()
        assert 6 in r["admissions_closed"]
        assert 11 in r["admissions_closed"]

    def test_alpha_phi_positive(self):
        r = pillar404_summary()
        assert r["alpha_phi"] > 0.0

    def test_lambda_gw_natural(self):
        r = pillar404_summary()
        assert r["lambda_gw_is_natural"]

    def test_n_e_derived_in_result(self):
        r = pillar404_summary()
        assert 40.0 < r["n_e_derived"] < 80.0

    def test_honest_residual_present(self):
        r = pillar404_summary()
        assert len(r["honest_residual"]) > 50

    def test_key_result_mentions_nu(self):
        r = pillar404_summary()
        assert "ν" in r["key_result"] or "nu" in r["key_result"].lower()

    def test_admission_verdicts_present(self):
        r = pillar404_summary()
        assert "admission_6_verdict" in r
        assert "admission_11_verdict" in r
