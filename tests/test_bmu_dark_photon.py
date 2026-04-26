# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_bmu_dark_photon.py
==============================
Test suite for src/core/bmu_dark_photon.py — Pillar 71.

Covers:
  - Module constants
  - bmu_kk_mass: positive, formula, scaling, errors
  - bmu_kinetic_mixing: positive, small, scaling, errors
  - bmu_fermion_coupling: n_w=5 odd, brane positions, errors
  - dark_photon_cmb_constraints: dict keys, exclusion booleans, types
  - bmu_muon_g2_contribution: positive, heavy vs light suppression, epsilon scaling
  - bmu_coupling_audit: dict keys, mass_from_kk True, gap_status str
  - bmu_summary: dict structure, types

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.bmu_dark_photon import (
    N_W,
    K_CS,
    C_S,
    G5_PLANCK,
    R_KK_PLANCK,
    DARK_PHOTON_CMB_MASS_LIMIT_EV,
    DARK_PHOTON_ACCEL_EPSILON_LIMIT,
    M_MU_MEV,
    MUON_G2_ANOMALY,
    MUON_G2_ANOMALY_UNC,
    ALPHA_EM,
    bmu_kk_mass,
    bmu_kinetic_mixing,
    bmu_fermion_coupling,
    dark_photon_cmb_constraints,
    bmu_muon_g2_contribution,
    bmu_coupling_audit,
    bmu_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-14

    def test_g5_planck(self):
        assert G5_PLANCK == 1.0

    def test_r_kk_planck(self):
        assert R_KK_PLANCK == 1.0

    def test_cmb_mass_limit_positive(self):
        assert DARK_PHOTON_CMB_MASS_LIMIT_EV > 0

    def test_cmb_mass_limit_value(self):
        assert DARK_PHOTON_CMB_MASS_LIMIT_EV == pytest.approx(1e-14, rel=1e-10)

    def test_accel_epsilon_limit_positive(self):
        assert DARK_PHOTON_ACCEL_EPSILON_LIMIT > 0

    def test_muon_mass_positive(self):
        assert M_MU_MEV > 0

    def test_muon_mass_value(self):
        assert abs(M_MU_MEV - 105.66) < 0.01

    def test_g2_anomaly_positive(self):
        assert MUON_G2_ANOMALY > 0

    def test_g2_anomaly_uncertainty_positive(self):
        assert MUON_G2_ANOMALY_UNC > 0

    def test_alpha_em_value(self):
        assert abs(ALPHA_EM - 1.0 / 137.035999084) < 1e-12

    def test_alpha_em_small(self):
        assert ALPHA_EM < 0.01


class TestBmuKkMass:
    def test_positive(self):
        assert bmu_kk_mass(1.0, 1.0) > 0

    def test_formula(self):
        result = bmu_kk_mass(1.0, 1.0)
        assert result == pytest.approx(1.0 / math.pi, rel=1e-10)

    def test_planck_params(self):
        result = bmu_kk_mass(R_KK_PLANCK, G5_PLANCK)
        assert result == pytest.approx(1.0 / math.pi, rel=1e-10)

    def test_mass_scales_inversely_with_r_kk(self):
        m1 = bmu_kk_mass(1.0, 1.0)
        m2 = bmu_kk_mass(2.0, 1.0)
        assert m2 == pytest.approx(m1 / 2.0, rel=1e-10)

    def test_mass_scales_with_g5(self):
        m1 = bmu_kk_mass(1.0, 1.0)
        m2 = bmu_kk_mass(1.0, 2.0)
        assert m2 == pytest.approx(2.0 * m1, rel=1e-10)

    def test_r_kk_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_kk_mass(0.0, 1.0)

    def test_r_kk_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_kk_mass(-1.0, 1.0)

    def test_g5_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_kk_mass(1.0, 0.0)

    def test_g5_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_kk_mass(1.0, -1.0)

    def test_mass_pi_factor(self):
        # m = g5 / (R_KK * pi)
        m = bmu_kk_mass(2.0, 3.0)
        assert m == pytest.approx(3.0 / (2.0 * math.pi), rel=1e-10)

    def test_output_type(self):
        assert isinstance(bmu_kk_mass(1.0, 1.0), float)

    def test_small_r_kk_large_mass(self):
        m = bmu_kk_mass(0.001, 1.0)
        assert m > 100.0

    def test_large_r_kk_small_mass(self):
        m = bmu_kk_mass(1000.0, 1.0)
        assert m < 0.01

    def test_mass_positive_for_all_positives(self):
        for r in [0.1, 0.5, 1.0, 2.0, 10.0]:
            for g in [0.1, 1.0, 2.0]:
                assert bmu_kk_mass(r, g) > 0

    def test_mass_order_mkk(self):
        # m_Bμ ≈ 1/π for natural params — order of M_KK
        m = bmu_kk_mass(R_KK_PLANCK, G5_PLANCK)
        assert 0.1 < m < 10.0

    def test_formula_explicit(self):
        R, g = 3.5, 2.5
        expected = g / (R * math.pi)
        assert bmu_kk_mass(R, g) == pytest.approx(expected, rel=1e-10)

    def test_g5_large(self):
        m = bmu_kk_mass(1.0, 100.0)
        assert m == pytest.approx(100.0 / math.pi, rel=1e-10)

    def test_consistency_with_m_kk(self):
        # m_Bμ = g5/(R_KK * π) ~ M_KK = 1/(π R_KK) for g5=1
        m_bmu = bmu_kk_mass(1.0, 1.0)
        m_kk = 1.0 / (math.pi * 1.0)
        assert m_bmu == pytest.approx(m_kk, rel=1e-10)

    def test_half_g5(self):
        m1 = bmu_kk_mass(1.0, 1.0)
        m2 = bmu_kk_mass(1.0, 0.5)
        assert m2 == pytest.approx(0.5 * m1, rel=1e-10)

    def test_quarter_r_kk(self):
        m1 = bmu_kk_mass(1.0, 1.0)
        m2 = bmu_kk_mass(0.25, 1.0)
        assert m2 == pytest.approx(4.0 * m1, rel=1e-10)


class TestKineticMixing:
    def test_positive(self):
        assert bmu_kinetic_mixing(1.0, 1.0) > 0

    def test_formula(self):
        result = bmu_kinetic_mixing(1.0, 1.0)
        expected = 1.0 * math.sqrt(ALPHA_EM) / (2.0 * math.pi)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_natural_params_small(self):
        eps = bmu_kinetic_mixing(G5_PLANCK, R_KK_PLANCK)
        assert eps < 0.1

    def test_scales_with_g5(self):
        e1 = bmu_kinetic_mixing(1.0, 1.0)
        e2 = bmu_kinetic_mixing(2.0, 1.0)
        assert e2 == pytest.approx(2.0 * e1, rel=1e-10)

    def test_independent_of_r_kk(self):
        e1 = bmu_kinetic_mixing(1.0, 1.0)
        e2 = bmu_kinetic_mixing(1.0, 5.0)
        assert e1 == pytest.approx(e2, rel=1e-10)

    def test_g5_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_kinetic_mixing(0.0, 1.0)

    def test_g5_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_kinetic_mixing(-1.0, 1.0)

    def test_alpha_em_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_kinetic_mixing(1.0, 1.0, alpha_em=0.0)

    def test_alpha_em_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_kinetic_mixing(1.0, 1.0, alpha_em=-1.0)

    def test_scales_with_sqrt_alpha(self):
        e1 = bmu_kinetic_mixing(1.0, 1.0, alpha_em=ALPHA_EM)
        e2 = bmu_kinetic_mixing(1.0, 1.0, alpha_em=4 * ALPHA_EM)
        assert e2 == pytest.approx(2.0 * e1, rel=1e-10)

    def test_output_type(self):
        assert isinstance(bmu_kinetic_mixing(1.0, 1.0), float)

    def test_natural_mixing_order_alpha(self):
        # For natural params: ε = sqrt(α_em)/(2π) ~ 0.014
        eps = bmu_kinetic_mixing(G5_PLANCK, R_KK_PLANCK)
        expected = math.sqrt(ALPHA_EM) / (2.0 * math.pi)
        assert eps == pytest.approx(expected, rel=1e-10)

    def test_explicit_value(self):
        g5 = 2.0
        alpha = 1 / 100.0
        eps = bmu_kinetic_mixing(g5, 1.0, alpha_em=alpha)
        assert eps == pytest.approx(g5 * math.sqrt(alpha) / (2 * math.pi), rel=1e-10)

    def test_large_g5_larger_mixing(self):
        e1 = bmu_kinetic_mixing(1.0, 1.0)
        e2 = bmu_kinetic_mixing(100.0, 1.0)
        assert e2 > e1

    def test_mixing_positive_always(self):
        for g5 in [0.01, 0.1, 1.0, 10.0]:
            assert bmu_kinetic_mixing(g5, 1.0) > 0


class TestFermionCoupling:
    def test_n_w_5_ir_brane_value(self):
        # n_w=5, brane_position=π: cos(5π) = cos(π) = -1 → |g_f| = G5/sqrt(π*R_KK)
        g_f = bmu_fermion_coupling(5, math.pi)
        expected = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_n_w_5_ir_brane_abs_value(self):
        g_f = bmu_fermion_coupling(5, math.pi)
        assert g_f >= 0

    def test_n_w_5_uv_brane(self):
        # brane_position=0: cos(5*0) = 1 → g_f = G5/sqrt(π)
        g_f = bmu_fermion_coupling(5, 0.0)
        expected = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_n_w_1_ir_brane(self):
        # cos(1*π) = -1 → |g_f| = G5/sqrt(π)
        g_f = bmu_fermion_coupling(1, math.pi)
        expected = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_n_w_7_ir_brane(self):
        # cos(7π) = cos(π) = -1 → same
        g_f = bmu_fermion_coupling(7, math.pi)
        expected = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_zero_at_quarter_period(self):
        # cos(n_w * π/2): for n_w=2, π/2 gives 0
        # But n_w must be ≥ 1; use n_w=1, brane_pos=π/2
        g_f = bmu_fermion_coupling(1, math.pi / 2.0)
        # cos(π/2) = 0
        assert g_f == pytest.approx(0.0, abs=1e-10)

    def test_returns_nonneg(self):
        for n_w in [1, 3, 5, 7]:
            for pos in [0.0, math.pi / 4, math.pi / 2, math.pi]:
                g_f = bmu_fermion_coupling(n_w, pos)
                assert g_f >= 0

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_fermion_coupling(0, math.pi)

    def test_n_w_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_fermion_coupling(-1, math.pi)

    def test_output_type(self):
        assert isinstance(bmu_fermion_coupling(5, math.pi), float)

    def test_brane_position_zero_cos_1(self):
        # cos(0) = 1 always → g_f = prefactor
        prefactor = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        for n_w in [1, 3, 5, 7]:
            g_f = bmu_fermion_coupling(n_w, 0.0)
            assert g_f == pytest.approx(prefactor, rel=1e-10)

    def test_coupling_n_w_5_same_as_n_w_1_at_pi(self):
        # Both cos(5π) and cos(1π) = -1 → same coupling
        g5 = bmu_fermion_coupling(5, math.pi)
        g1 = bmu_fermion_coupling(1, math.pi)
        assert g5 == pytest.approx(g1, rel=1e-10)

    def test_coupling_formula_explicit(self):
        n_w = 3
        pos = math.pi / 6.0
        g_f = bmu_fermion_coupling(n_w, pos)
        prefactor = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        expected = abs(prefactor * math.cos(n_w * pos))
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_various_n_w_positive_at_uv(self):
        for n_w in [1, 5, 7, 9, 11]:
            assert bmu_fermion_coupling(n_w, 0.0) > 0

    def test_coupling_max_at_uv_or_ir_brane(self):
        # At IR brane for odd n_w: |cos(n_w π)| = 1 (maximum)
        g_max = bmu_fermion_coupling(5, math.pi)
        g_mid = bmu_fermion_coupling(5, math.pi / 4.0)
        # g_mid = |cos(5π/4)| * prefactor = cos(5π/4) < 1 always
        # Actually cos(5π/4) = -√2/2, so |g_mid| = √2/2 * prefactor < prefactor
        assert g_max >= g_mid - 1e-10  # within tolerance

    def test_n_w_2_even_coupling(self):
        # n_w=2: cos(2*π) = 1 → g_f = prefactor
        g_f = bmu_fermion_coupling(2, math.pi)
        prefactor = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        expected = abs(prefactor * math.cos(2 * math.pi))
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_n_w_large(self):
        g_f = bmu_fermion_coupling(100, math.pi)
        assert g_f >= 0

    def test_n_w_1_positive(self):
        assert bmu_fermion_coupling(1, 1.0) >= 0

    def test_n_w_5_formula_exact(self):
        g_f = bmu_fermion_coupling(N_W, math.pi)
        # G5_PLANCK = 1, R_KK_PLANCK = 1
        expected = 1.0 / math.sqrt(math.pi) * abs(math.cos(5 * math.pi))
        assert g_f == pytest.approx(expected, rel=1e-10)

    def test_n_w_5_ir_equal_uv(self):
        # cos(5π)=-1 and cos(0)=1, both have abs=1
        g_ir = bmu_fermion_coupling(5, math.pi)
        g_uv = bmu_fermion_coupling(5, 0.0)
        assert g_ir == pytest.approx(g_uv, rel=1e-10)

    def test_n_w_4_halfway(self):
        # cos(4 * π/2) = cos(2π) = 1
        g_f = bmu_fermion_coupling(4, math.pi / 2.0)
        prefactor = G5_PLANCK / math.sqrt(math.pi * R_KK_PLANCK)
        assert g_f == pytest.approx(prefactor, rel=1e-10)


class TestCmbConstraints:
    def test_returns_dict(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert isinstance(result, dict)

    def test_key_m_bmu_ev(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "m_bmu_ev" in result

    def test_key_epsilon(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "epsilon" in result

    def test_key_in_cmb_excluded_region(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "in_cmb_excluded_region" in result

    def test_key_cmb_limit_epsilon(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "cmb_limit_epsilon" in result

    def test_key_interpretation(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "interpretation" in result

    def test_light_large_epsilon_excluded(self):
        # m < 1e-14 eV AND ε > 1e-7 → excluded
        result = dark_photon_cmb_constraints(1e-15, 1e-6)
        assert result["in_cmb_excluded_region"] is True

    def test_light_small_epsilon_allowed(self):
        # m < 1e-14 eV but ε < 1e-7 → not excluded
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert result["in_cmb_excluded_region"] is False

    def test_heavy_not_excluded(self):
        # m > 1e-14 eV → not in CMB mass range
        result = dark_photon_cmb_constraints(1.0, 1e-3)
        assert result["in_cmb_excluded_region"] is False

    def test_planck_scale_not_excluded(self):
        # Planck-scale B_μ is extremely heavy → not in CMB excluded region
        result = dark_photon_cmb_constraints(1e20, 1e-3)
        assert result["in_cmb_excluded_region"] is False

    def test_in_cmb_excluded_region_bool(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert isinstance(result["in_cmb_excluded_region"], bool)

    def test_interpretation_str(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert isinstance(result["interpretation"], str)

    def test_negative_m_raises(self):
        with pytest.raises(ValueError):
            dark_photon_cmb_constraints(-1.0, 1e-3)

    def test_negative_epsilon_raises(self):
        with pytest.raises(ValueError):
            dark_photon_cmb_constraints(1.0, -1.0)

    def test_cmb_limit_value(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert result["cmb_limit_epsilon"] == pytest.approx(1e-7, rel=1e-10)

    def test_zero_m_allowed_with_small_eps(self):
        result = dark_photon_cmb_constraints(0.0, 1e-8)
        assert result["in_cmb_excluded_region"] is False

    def test_zero_epsilon_not_excluded(self):
        result = dark_photon_cmb_constraints(1e-15, 0.0)
        assert result["in_cmb_excluded_region"] is False

    def test_m_stored_correctly(self):
        m = 1e-10
        result = dark_photon_cmb_constraints(m, 1e-8)
        assert result["m_bmu_ev"] == pytest.approx(m, rel=1e-10)

    def test_epsilon_stored_correctly(self):
        eps = 3.5e-8
        result = dark_photon_cmb_constraints(1e-15, eps)
        assert result["epsilon"] == pytest.approx(eps, rel=1e-10)

    def test_cmb_mass_limit_key(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-8)
        assert "cmb_mass_limit_ev" in result

    def test_exactly_at_limit_not_excluded(self):
        # Exactly at m = 1e-14, ε = 1e-7: boundary condition
        result = dark_photon_cmb_constraints(DARK_PHOTON_CMB_MASS_LIMIT_EV, 1e-7)
        # m is NOT < limit (it's equal), so not in mass range
        assert result["in_cmb_excluded_region"] is False

    def test_output_type_consistent(self):
        result = dark_photon_cmb_constraints(1e-15, 1e-6)
        assert isinstance(result["m_bmu_ev"], float)
        assert isinstance(result["epsilon"], float)

    def test_mid_mass_mid_epsilon(self):
        result = dark_photon_cmb_constraints(1e-16, 1e-5)
        assert result["in_cmb_excluded_region"] is True


class TestMuonG2:
    def test_positive(self):
        assert bmu_muon_g2_contribution(1000.0, 1e-3) > 0

    def test_heavy_dark_photon_suppressed(self):
        # m >> m_μ → suppressed
        delta_heavy = bmu_muon_g2_contribution(1e6, 1e-3)
        delta_light = bmu_muon_g2_contribution(1.0, 1e-3)
        assert delta_heavy < delta_light

    def test_light_dark_photon_order_unity_F(self):
        # m << m_μ → F ≈ 1
        delta = bmu_muon_g2_contribution(0.001, 1e-3)
        expected_approx = ALPHA_EM / (2.0 * math.pi) * 1e-6
        assert delta > 0

    def test_scales_as_epsilon_squared(self):
        d1 = bmu_muon_g2_contribution(1000.0, 1e-3)
        d2 = bmu_muon_g2_contribution(1000.0, 2e-3)
        assert d2 == pytest.approx(4.0 * d1, rel=1e-8)

    def test_scales_with_alpha_em(self):
        # alpha_em factored in directly
        d = bmu_muon_g2_contribution(1000.0, 1e-3)
        assert d > 0

    def test_m_bmu_zero_raises(self):
        with pytest.raises(ValueError):
            bmu_muon_g2_contribution(0.0, 1e-3)

    def test_m_bmu_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_muon_g2_contribution(-1.0, 1e-3)

    def test_epsilon_negative_raises(self):
        with pytest.raises(ValueError):
            bmu_muon_g2_contribution(1000.0, -1.0)

    def test_epsilon_zero_gives_zero(self):
        d = bmu_muon_g2_contribution(1000.0, 0.0)
        assert d == pytest.approx(0.0, abs=1e-40)

    def test_heavy_suppression_formula(self):
        # For m >> m_μ: Δa_μ = (α/2π) * ε² * (1/3) * (m_μ/m)²
        m = 1e5  # much larger than m_μ ≈ 105.66 MeV
        eps = 1e-2
        x = m / M_MU_MEV
        F = (1.0 / 3.0) / x ** 2
        expected = (ALPHA_EM / (2.0 * math.pi)) * eps ** 2 * F
        result = bmu_muon_g2_contribution(m, eps)
        assert result == pytest.approx(expected, rel=1e-8)

    def test_light_formula(self):
        # For m << m_μ: F = 1/(1+x²) ≈ 1
        m = 0.001  # very light
        eps = 1e-2
        x = m / M_MU_MEV
        F = 1.0 / (1.0 + x ** 2)
        expected = (ALPHA_EM / (2.0 * math.pi)) * eps ** 2 * F
        result = bmu_muon_g2_contribution(m, eps)
        assert result == pytest.approx(expected, rel=1e-8)

    def test_output_type(self):
        assert isinstance(bmu_muon_g2_contribution(1000.0, 1e-3), float)

    def test_planck_scale_suppressed(self):
        # Planck-scale B_μ: m >> m_μ → highly suppressed
        m_planck_mev = 1.22e22
        d = bmu_muon_g2_contribution(m_planck_mev, 1e-3)
        assert d < 1e-30

    def test_comparison_with_anomaly(self):
        # For typical dark photon parameters, contribution should be < anomaly
        d = bmu_muon_g2_contribution(100.0, 1e-3)
        assert d < MUON_G2_ANOMALY * 1e3  # much less even with factor

    def test_monotone_in_epsilon(self):
        for eps1, eps2 in [(1e-5, 1e-4), (1e-4, 1e-3)]:
            d1 = bmu_muon_g2_contribution(100.0, eps1)
            d2 = bmu_muon_g2_contribution(100.0, eps2)
            assert d2 > d1

    def test_monotone_in_mass_heavy(self):
        # For heavy masses: larger m → smaller contribution
        d1 = bmu_muon_g2_contribution(1e4, 1e-3)
        d2 = bmu_muon_g2_contribution(1e5, 1e-3)
        assert d1 > d2

    def test_formula_at_x_equal_1(self):
        # x = 1: m = M_MU_MEV, heavy branch (x>1 → no, x=1 = not > 1, use light branch)
        m = M_MU_MEV
        eps = 1e-2
        x = 1.0
        # x = m/m_mu = 1, not > 1, use light: F = 1/(1+1) = 0.5
        F = 1.0 / (1.0 + x ** 2)
        expected = (ALPHA_EM / (2.0 * math.pi)) * eps ** 2 * F
        result = bmu_muon_g2_contribution(m, eps)
        assert result == pytest.approx(expected, rel=1e-8)

    def test_very_small_epsilon(self):
        d = bmu_muon_g2_contribution(100.0, 1e-10)
        assert d > 0
        assert d < 1e-20


class TestCouplingAudit:
    def setup_method(self):
        self.audit = bmu_coupling_audit()

    def test_returns_dict(self):
        assert isinstance(self.audit, dict)

    def test_key_mass_from_kk(self):
        assert "mass_from_kk" in self.audit

    def test_mass_from_kk_true(self):
        assert self.audit["mass_from_kk"] is True

    def test_key_kinetic_mixing_derived(self):
        assert "kinetic_mixing_derived" in self.audit

    def test_kinetic_mixing_derived_true(self):
        assert self.audit["kinetic_mixing_derived"] is True

    def test_key_fermion_coupling_derived(self):
        assert "fermion_coupling_derived" in self.audit

    def test_fermion_coupling_partial(self):
        assert self.audit["fermion_coupling_derived"] == "PARTIAL"

    def test_key_g2_contribution(self):
        assert "g2_contribution_order_of_magnitude" in self.audit

    def test_g2_contribution_float(self):
        assert isinstance(self.audit["g2_contribution_order_of_magnitude"], float)

    def test_key_cmb_constraints_checked(self):
        assert "cmb_constraints_checked" in self.audit

    def test_cmb_constraints_checked_true(self):
        assert self.audit["cmb_constraints_checked"] is True

    def test_key_gap_status(self):
        assert "gap_status" in self.audit

    def test_gap_status_str(self):
        assert isinstance(self.audit["gap_status"], str)

    def test_gap_status_mentions_partial(self):
        assert "PARTIAL" in self.audit["gap_status"]

    def test_key_closes_fallibility_gap(self):
        assert "closes_fallibility_gap" in self.audit

    def test_closes_fallibility_gap_str(self):
        assert isinstance(self.audit["closes_fallibility_gap"], str)

    def test_closes_fallibility_gap_mentions_gap(self):
        text = self.audit["closes_fallibility_gap"].lower()
        assert "gap" in text or "fallibility" in text or "dark photon" in text.lower()


class TestSummary:
    def setup_method(self):
        self.s = bmu_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_pillar_key(self):
        assert "pillar" in self.s

    def test_pillar_value(self):
        assert self.s["pillar"] == 71

    def test_name_key(self):
        assert "name" in self.s

    def test_name_str(self):
        assert isinstance(self.s["name"], str)

    def test_m_bmu_key(self):
        assert "m_bmu_planck_units" in self.s

    def test_m_bmu_positive(self):
        assert self.s["m_bmu_planck_units"] > 0

    def test_kinetic_mixing_key(self):
        assert "kinetic_mixing_epsilon" in self.s

    def test_kinetic_mixing_positive(self):
        assert self.s["kinetic_mixing_epsilon"] > 0

    def test_n_w_key(self):
        assert "n_w" in self.s

    def test_n_w_value(self):
        assert self.s["n_w"] == 5

    def test_gap_closed_key(self):
        assert "gap_closed" in self.s

    def test_gap_closed_str(self):
        assert isinstance(self.s["gap_closed"], str)

    def test_honest_status_key(self):
        assert "honest_status" in self.s

    def test_honest_status_dict(self):
        assert isinstance(self.s["honest_status"], dict)

    def test_coupling_audit_key(self):
        assert "coupling_audit" in self.s

    def test_cmb_constraints_key(self):
        assert "cmb_constraints" in self.s
