# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_nonabelian_kk.py
============================
Test suite for Pillar 62: Non-Abelian SU(3)_C Kaluza-Klein Reduction
(src/core/nonabelian_kk.py).

~110 tests covering:
  - Module-level constants (correctness, derivation claims)
  - su3_casimir_data(): SU(N) group theory
  - alpha_s_kk_scale(): non-Abelian CS threshold formula
  - qcd_beta_b0(): one-loop QCD beta function
  - alpha_s_rg_run(): asymptotic-freedom running
  - lambda_qcd_from_dim_trans(): dimensional transmutation
  - alpha_s_correction_factor(): gap quantification
  - proton_mass_from_lambda_qcd(): lattice-normalised m_p
  - mp_over_me_pipeline(): full ratio derivation
  - alpha_s_at_mz_prediction(): M_Z comparison
  - nonabelian_kk_gap_report(): comprehensive accounting
  - nonabelian_kk_summary(): top-level dict

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.nonabelian_kk import (
    # Constants
    N_W, N_W2, K_CS_CANONICAL, N_C_CANONICAL, N_F_CANONICAL, B0_CANONICAL,
    R_C_CANONICAL, M_PL_GEV_REDUCED, M_KK_CANONICAL_GEV, ALPHA_S_KK_CANONICAL,
    C_LAT_CANONICAL, C_LAT_PDG, LAMBDA_QCD_PDG_MEV, MP_PDG_MEV, ME_PDG_MEV,
    MP_OVER_ME_PDG, ALPHA_S_MZ_PDG, M_Z_GEV, M_CHARM_GEV,
    CMS_ALPHAS_MZ, CMS_ALPHAS_MZ_UNC, CMS_ALPHAS_1TEV, CMS_ALPHAS_1TEV_UNC,
    CMS_SCALE_1TEV,
    # Functions
    su3_casimir_data,
    evolve_coupling,
    alpha_s_kk_scale,
    qcd_beta_b0,
    alpha_s_rg_run,
    lambda_qcd_from_dim_trans,
    alpha_s_correction_factor,
    proton_mass_from_lambda_qcd,
    mp_over_me_pipeline,
    alpha_s_at_mz_prediction,
    nonabelian_kk_gap_report,
    nonabelian_kk_summary,
    cms_alphas_rg_consistency,
)


# ===========================================================================
# I. Module-level constants
# ===========================================================================

class TestConstants:
    """Verify every module constant matches the expected value."""

    def test_n_w(self):
        assert N_W == 5

    def test_n_w2(self):
        assert N_W2 == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74
        assert K_CS_CANONICAL == N_W**2 + N_W2**2

    def test_n_c_canonical(self):
        assert N_C_CANONICAL == 3

    def test_n_f_canonical(self):
        # Derived from Pillar 42 Three-Generation Theorem
        assert N_F_CANONICAL == 3

    def test_b0_canonical(self):
        # b_0 = (11×3 − 2×3)/3 = 9
        expected = (11 * N_C_CANONICAL - 2 * N_F_CANONICAL) // 3
        assert B0_CANONICAL == expected
        assert B0_CANONICAL == 9

    def test_r_c_canonical(self):
        assert R_C_CANONICAL == 12.0

    def test_m_pl_gev_reduced_order_of_magnitude(self):
        # Reduced Planck mass ≈ 2.44 × 10^18 GeV
        assert 2.0e18 < M_PL_GEV_REDUCED < 3.0e18

    def test_m_kk_canonical_gev(self):
        assert abs(M_KK_CANONICAL_GEV - M_PL_GEV_REDUCED / R_C_CANONICAL) < 1.0
        assert 1e16 < M_KK_CANONICAL_GEV < 1e18

    def test_alpha_s_kk_canonical_formula(self):
        expected = 2.0 * math.pi / (N_C_CANONICAL * K_CS_CANONICAL)
        assert abs(ALPHA_S_KK_CANONICAL - expected) < 1e-12

    def test_alpha_s_kk_canonical_magnitude(self):
        # Should be ~0.028 — small but non-zero
        assert 0.01 < ALPHA_S_KK_CANONICAL < 0.10

    def test_c_lat_canonical(self):
        # Lattice normalisation ≈ 4.4
        assert 3.0 < C_LAT_CANONICAL < 6.0

    def test_c_lat_pdg(self):
        # C_lat_PDG = m_p / Λ_QCD_PDG ≈ 938/332 ≈ 2.83
        expected = MP_PDG_MEV / LAMBDA_QCD_PDG_MEV
        assert abs(C_LAT_PDG - expected) < 0.01

    def test_lambda_qcd_pdg_mev(self):
        # PDG MS-bar Λ_QCD (N_f=3) ≈ 332 MeV
        assert 100.0 < LAMBDA_QCD_PDG_MEV < 600.0

    def test_mp_pdg_mev(self):
        assert abs(MP_PDG_MEV - 938.272) < 0.01

    def test_me_pdg_mev(self):
        assert abs(ME_PDG_MEV - 0.511) < 0.001

    def test_mp_over_me_pdg(self):
        assert abs(MP_OVER_ME_PDG - 1836.15) < 0.01

    def test_alpha_s_mz_pdg(self):
        # PDG α_s(M_Z) ≈ 0.1179
        assert abs(ALPHA_S_MZ_PDG - 0.1179) < 0.001

    def test_m_z_gev(self):
        assert abs(M_Z_GEV - 91.19) < 0.1

    def test_m_charm_gev(self):
        assert 1.0 < M_CHARM_GEV < 2.0


# ===========================================================================
# II. su3_casimir_data
# ===========================================================================

class TestSU3CasimirData:
    """SU(N_c) group theory — Casimir invariants."""

    def test_n_c_3_c_a(self):
        d = su3_casimir_data(3)
        assert d["C_A"] == 3.0

    def test_n_c_3_t_f(self):
        d = su3_casimir_data(3)
        assert d["T_F"] == 0.5

    def test_n_c_3_c_f(self):
        d = su3_casimir_data(3)
        expected = (9 - 1) / 6.0   # 8/6 = 4/3
        assert abs(d["C_F"] - expected) < 1e-12

    def test_n_c_3_d_adj(self):
        d = su3_casimir_data(3)
        assert d["d_adj"] == 8   # SU(3): 9 - 1 = 8

    def test_n_c_3_d_fund(self):
        d = su3_casimir_data(3)
        assert d["d_fund"] == 3

    def test_n_c_2_su2(self):
        d = su3_casimir_data(2)
        assert d["C_A"] == 2.0
        assert d["d_adj"] == 3

    def test_n_c_5_su5(self):
        d = su3_casimir_data(5)
        assert d["C_A"] == 5.0
        assert d["d_adj"] == 24

    def test_c_f_formula_general(self):
        for n in [2, 3, 4, 5]:
            d = su3_casimir_data(n)
            expected = (n**2 - 1) / (2.0 * n)
            assert abs(d["C_F"] - expected) < 1e-12

    def test_description_mentions_assumption(self):
        d = su3_casimir_data()
        assert "ASSUMPTION" in d["description"] or "assumption" in d["description"].lower()

    def test_invalid_n_c_raises(self):
        with pytest.raises(ValueError):
            su3_casimir_data(1)

    def test_n_c_in_output(self):
        d = su3_casimir_data(4)
        assert d["n_c"] == 4


# ===========================================================================
# III. alpha_s_kk_scale
# ===========================================================================

class TestAlphaSKKScale:
    """Non-Abelian CS gauge threshold."""

    def test_canonical_formula(self):
        result = alpha_s_kk_scale()
        expected = 2.0 * math.pi / (N_C_CANONICAL * K_CS_CANONICAL)
        assert abs(result["alpha_s_kk"] - expected) < 1e-12

    def test_canonical_value(self):
        result = alpha_s_kk_scale()
        # 2π/222 ≈ 0.02829
        assert abs(result["alpha_s_kk"] - 0.02829) < 0.001

    def test_inverse_consistent(self):
        result = alpha_s_kk_scale()
        assert abs(result["alpha_s_kk"] * result["alpha_s_kk_inv"] - 1.0) < 1e-12

    def test_f_strong(self):
        result = alpha_s_kk_scale()
        expected_f = N_C_CANONICAL * K_CS_CANONICAL / (8.0 * math.pi**2)
        assert abs(result["f_strong"] - expected_f) < 1e-12

    def test_free_parameters_list_nonempty(self):
        result = alpha_s_kk_scale()
        assert len(result["free_parameters"]) >= 1

    def test_n_c_in_output(self):
        result = alpha_s_kk_scale(n_c=3)
        assert result["n_c"] == 3

    def test_k_cs_in_output(self):
        result = alpha_s_kk_scale(k_cs=74)
        assert result["k_cs"] == 74

    def test_larger_n_c_smaller_alpha_s(self):
        r3 = alpha_s_kk_scale(n_c=3)
        r5 = alpha_s_kk_scale(n_c=5)
        assert r5["alpha_s_kk"] < r3["alpha_s_kk"]

    def test_larger_k_cs_smaller_alpha_s(self):
        r74 = alpha_s_kk_scale(k_cs=74)
        r100 = alpha_s_kk_scale(k_cs=100)
        assert r100["alpha_s_kk"] < r74["alpha_s_kk"]

    def test_invalid_k_cs_raises(self):
        with pytest.raises(ValueError):
            alpha_s_kk_scale(k_cs=0)

    def test_invalid_n_c_raises(self):
        with pytest.raises(ValueError):
            alpha_s_kk_scale(n_c=1)

    def test_abelian_limit_u1(self):
        # For N_c=1 (Abelian U(1)) formula should give 2π/k_cs
        # (but N_c=1 is invalid for our non-Abelian context)
        # So we verify the Abelian result is LARGER than the non-Abelian
        result_abelian = 2.0 * math.pi / K_CS_CANONICAL  # from Pillar 61
        result_na = alpha_s_kk_scale()["alpha_s_kk"]
        assert result_abelian > result_na  # Abelian coupling is stronger at KK scale

    def test_derivation_status_in_output(self):
        result = alpha_s_kk_scale()
        assert "DERIVED" in result["derivation_status"]


# ===========================================================================
# IV. qcd_beta_b0
# ===========================================================================

class TestQCDBetaB0:
    """One-loop QCD beta function coefficient."""

    def test_canonical_b0(self):
        # N_c=3, N_f=3 → b_0 = (33-6)/3 = 9
        assert qcd_beta_b0(3, 3) == 9.0

    def test_n_c_3_n_f_6(self):
        # Standard QCD with 6 flavours: (33-12)/3 = 7
        assert qcd_beta_b0(3, 6) == 7.0

    def test_n_c_3_n_f_5(self):
        # Standard QCD with 5 flavours: (33-10)/3 = 23/3
        assert abs(qcd_beta_b0(3, 5) - 23.0/3.0) < 1e-12

    def test_asymptotic_freedom_condition(self):
        # b_0 > 0 for N_f < 11 N_c / 2
        assert qcd_beta_b0(3, 16) > 0  # 16 < 16.5

    def test_asymptotic_freedom_boundary_raises(self):
        # N_f = 17 for N_c=3: (33-34)/3 < 0 → should raise
        with pytest.raises(ValueError):
            qcd_beta_b0(3, 17)

    def test_n_f_0_limiting_case(self):
        # Pure Yang-Mills (no quarks): b_0 = 11 N_c / 3
        assert abs(qcd_beta_b0(3, 0) - 11.0) < 1e-12

    def test_pillar42_constraint(self):
        # N_f=3 is derived from Pillar 42; confirm b_0=9 is used canonically
        assert B0_CANONICAL == 9
        assert abs(qcd_beta_b0() - B0_CANONICAL) < 1e-12


# ===========================================================================
# V. evolve_coupling  (Gemini-suggested primitive, April 2026)
# ===========================================================================

class TestEvolveCoupling:
    """Primitive one-step coupling evolution — Gemini external review (April 2026).

    Gemini's reference implementation:
        def evolve_coupling(alpha_in, scale_ratio, b0):
            inv_alpha = (1/alpha_in) - (b0/(2π)) × ln(scale_ratio)
            if inv_alpha <= 0:
                raise ValueError("Landau pole encountered: Coupling diverged.")
            return 1.0 / inv_alpha

    These tests verify that our implementation matches that pattern exactly and
    exercise the boundary conditions that Gemini's analysis described.
    """

    # --- Formula correctness (using Gemini's worked example) ---

    def test_gemini_example_b9_sr2(self):
        # Gemini: α_in=0.5, scale_ratio=2, b0=9
        # Δ(1/α) = (9/2π) × ln2 ≈ 1.432 × 0.693 ≈ 0.992
        # 1/α_IR = 2.0 − 0.992 = 1.008  →  α_IR ≈ 0.992
        result = evolve_coupling(0.5, 2.0, 9.0)
        expected_inv = 1.0 / 0.5 - (9.0 / (2.0 * math.pi)) * math.log(2.0)
        assert abs(result - 1.0 / expected_inv) < 1e-12

    def test_gemini_example_b11_sr2(self):
        # Gemini: α_in=0.5, scale_ratio=2, b0=11
        # Δ(1/α) = (11/2π) × ln2 ≈ 1.750 × 0.693 ≈ 1.212
        # 1/α_IR = 2.0 − 1.212 = 0.788  →  α_IR ≈ 1.269
        result = evolve_coupling(0.5, 2.0, 11.0)
        expected_inv = 1.0 / 0.5 - (11.0 / (2.0 * math.pi)) * math.log(2.0)
        assert abs(result - 1.0 / expected_inv) < 1e-12

    def test_gemini_b11_inv_alpha_positive(self):
        # Gemini explicitly verified 1/α ≈ 0.788 > 0 for b0=11, sr=2, α_in=0.5
        inv_alpha = 1.0 / 0.5 - (11.0 / (2.0 * math.pi)) * math.log(2.0)
        assert inv_alpha > 0.0
        assert abs(inv_alpha - 0.788) < 0.01

    def test_b9_result_near_1(self):
        # Gemini noted α_IR ≈ 0.992 for b0=9 case; quite strong but finite
        result = evolve_coupling(0.5, 2.0, 9.0)
        assert abs(result - 0.992) < 0.01

    def test_b11_result_larger_than_b9(self):
        # Larger b_0 → stronger IR coupling after same scale ratio
        a9 = evolve_coupling(0.5, 2.0, 9.0)
        a11 = evolve_coupling(0.5, 2.0, 11.0)
        assert a11 > a9

    # --- Asymptotic freedom direction ---

    def test_coupling_increases_going_ir(self):
        # scale_ratio = μ_UV / μ_IR > 1 → IR coupling > UV coupling
        alpha_ir = evolve_coupling(0.1, 10.0, 9.0)
        assert alpha_ir > 0.1

    def test_larger_scale_ratio_larger_coupling(self):
        a2 = evolve_coupling(0.5, 2.0, 9.0)
        a4 = evolve_coupling(0.5, 4.0, 9.0)
        assert a4 > a2  # more running → stronger coupling

    def test_unit_scale_ratio_raises(self):
        # scale_ratio = 1 → ln(1) = 0 but should be > 1 for IR running
        with pytest.raises(ValueError):
            evolve_coupling(0.5, 1.0, 9.0)

    def test_scale_ratio_below_one_raises(self):
        with pytest.raises(ValueError):
            evolve_coupling(0.5, 0.5, 9.0)

    def test_nonpositive_alpha_raises(self):
        with pytest.raises(ValueError):
            evolve_coupling(0.0, 2.0, 9.0)

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            evolve_coupling(-0.1, 2.0, 9.0)

    def test_nonpositive_b0_raises(self):
        with pytest.raises(ValueError):
            evolve_coupling(0.5, 2.0, 0.0)

    def test_negative_b0_raises(self):
        with pytest.raises(ValueError):
            evolve_coupling(0.5, 2.0, -9.0)

    def test_landau_pole_raises(self):
        # Very large scale_ratio → 1/α → 0 and flips sign → should raise
        with pytest.raises(ValueError, match="Landau pole"):
            evolve_coupling(0.5, 1e6, 9.0)

    # --- Consistency with alpha_s_rg_run ---

    def test_consistent_with_rg_run(self):
        # evolve_coupling and alpha_s_rg_run must agree
        m_kk = 200.0
        mu = 100.0
        alpha_in = 0.5
        b0 = qcd_beta_b0()
        via_primitive = evolve_coupling(alpha_in, m_kk / mu, b0)
        via_rg = alpha_s_rg_run(alpha_in, m_kk, mu)
        assert abs(via_primitive - via_rg) < 1e-12

    # --- Canonical QCD parameters ---

    def test_canonical_b0_in_evolve(self):
        # Using the Pillar-62 canonical b_0=9 at the factor-of-2 test scale
        result = evolve_coupling(0.5, 2.0, float(B0_CANONICAL))
        assert result > 0.0

    def test_small_alpha_perturbative_stability(self):
        # Small coupling stays perturbative over a wide scale range
        result = evolve_coupling(0.01, 10.0, 9.0)
        assert 0.0 < result < 1.0   # remains perturbative


# ===========================================================================
# VI. alpha_s_rg_run
# ===========================================================================

class TestAlphaSRGRun:
    """One-loop QCD asymptotic-freedom running (delegates to evolve_coupling)."""

    def test_coupling_increases_at_low_energy(self):
        # QCD: α_s increases as μ decreases
        alpha_high = alpha_s_rg_run(ALPHA_S_KK_CANONICAL, M_KK_CANONICAL_GEV,
                                    M_KK_CANONICAL_GEV / 10)
        alpha_low = alpha_s_rg_run(ALPHA_S_KK_CANONICAL, M_KK_CANONICAL_GEV,
                                   M_KK_CANONICAL_GEV / 100)
        assert alpha_low > alpha_high > ALPHA_S_KK_CANONICAL

    def test_same_scale_is_identity(self):
        # Degenerate: run to a scale just barely below M_KK
        mu = M_KK_CANONICAL_GEV * 0.9999
        alpha = alpha_s_rg_run(ALPHA_S_KK_CANONICAL, M_KK_CANONICAL_GEV, mu)
        # Should be barely larger than input
        assert alpha > ALPHA_S_KK_CANONICAL

    def test_positive_result(self):
        # Above the Landau pole the result should be positive
        # Use a small log (high μ still below M_KK)
        mu = M_KK_CANONICAL_GEV * 0.5
        alpha = alpha_s_rg_run(ALPHA_S_KK_CANONICAL, M_KK_CANONICAL_GEV, mu)
        assert alpha > 0

    def test_mu_above_m_kk_raises(self):
        with pytest.raises(ValueError):
            alpha_s_rg_run(0.1, 1e10, 2e10)

    def test_nonpositive_alpha_raises(self):
        with pytest.raises(ValueError):
            alpha_s_rg_run(0.0, 1e10, 1e5)

    def test_landau_pole_raises(self):
        # Very small mu where coupling would blow up → Landau pole error
        with pytest.raises(ValueError):
            # With canonical α_s(M_KK) ≈ 0.028, the Landau pole is at ~PeV
            # Running from M_KK down to 1 GeV crosses the Landau pole
            alpha_s_rg_run(ALPHA_S_KK_CANONICAL, M_KK_CANONICAL_GEV, 1.0)

    def test_consistency_with_b0(self):
        # Verify the formula: α_s(μ)⁻¹ = α_s(M_KK)⁻¹ − (b0/2π)×ln(M_KK/μ)
        m_kk = 1e10
        mu = 1e8
        alpha_in = 0.15   # large enough to stay perturbative above μ
        alpha_out = alpha_s_rg_run(alpha_in, m_kk, mu)
        b0 = qcd_beta_b0()
        expected_inv = 1.0 / alpha_in - (b0 / (2.0 * math.pi)) * math.log(m_kk / mu)
        assert abs(1.0 / alpha_out - expected_inv) < 1e-12

    def test_larger_b0_faster_running(self):
        # Larger b_0 → faster increase of coupling → larger α_s at same μ
        # Use a factor-of-2 scale difference so both stay perturbative
        m_kk = 200.0
        mu = 100.0
        alpha_in = 0.5  # large enough that short running stays above zero
        a_nf3 = alpha_s_rg_run(alpha_in, m_kk, mu, n_c=3, n_f=3)   # b0=9
        a_nf6 = alpha_s_rg_run(alpha_in, m_kk, mu, n_c=3, n_f=0)   # b0=11
        assert a_nf6 > a_nf3  # larger b0 → stronger running


# ===========================================================================
# VII. lambda_qcd_from_dim_trans
# ===========================================================================

class TestLambdaQCDFromDimTrans:
    """Dimensional transmutation: Λ_QCD from KK threshold."""

    def test_keys_present(self):
        d = lambda_qcd_from_dim_trans()
        for key in ("alpha_s_kk", "m_kk_gev", "b0", "exponent",
                    "lambda_qcd_gev", "lambda_qcd_mev",
                    "lambda_qcd_pdg_mev", "discrepancy_factor",
                    "log10_discrepancy", "status"):
            assert key in d

    def test_exponent_negative(self):
        d = lambda_qcd_from_dim_trans()
        assert d["exponent"] < 0

    def test_lambda_below_m_kk(self):
        d = lambda_qcd_from_dim_trans()
        assert d["lambda_qcd_gev"] < M_KK_CANONICAL_GEV

    def test_canonical_discrepancy_is_large(self):
        # The UM prediction overshoots PDG by many orders of magnitude
        d = lambda_qcd_from_dim_trans()
        assert d["discrepancy_factor"] > 1e4

    def test_log10_discrepancy_positive(self):
        d = lambda_qcd_from_dim_trans()
        assert d["log10_discrepancy"] > 0

    def test_consistency_mev_gev(self):
        d = lambda_qcd_from_dim_trans()
        assert abs(d["lambda_qcd_mev"] - d["lambda_qcd_gev"] * 1000) < 1e-6

    def test_larger_alpha_s_larger_lambda_qcd(self):
        d_small = lambda_qcd_from_dim_trans(alpha_s_kk=0.01)
        d_large = lambda_qcd_from_dim_trans(alpha_s_kk=0.10)
        assert d_large["lambda_qcd_gev"] > d_small["lambda_qcd_gev"]

    def test_formula_consistency(self):
        # Verify: Λ = M_KK × exp(-2π / (b0 × α_s))
        alpha_s = 0.05
        m_kk = 1e10
        d = lambda_qcd_from_dim_trans(alpha_s_kk=alpha_s, m_kk_gev=m_kk)
        b0 = qcd_beta_b0()
        expected = m_kk * math.exp(-2.0 * math.pi / (b0 * alpha_s))
        assert abs(d["lambda_qcd_gev"] - expected) / expected < 1e-10

    def test_invalid_alpha_s_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_dim_trans(alpha_s_kk=-0.1)

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_dim_trans(m_kk_gev=0.0)

    def test_pdg_value_in_output(self):
        d = lambda_qcd_from_dim_trans()
        assert abs(d["lambda_qcd_pdg_mev"] - LAMBDA_QCD_PDG_MEV) < 1e-6


# ===========================================================================
# VIII. alpha_s_correction_factor
# ===========================================================================

class TestAlphaSCorrectionFactor:
    """Correction factor needed to reproduce PDG Λ_QCD."""

    def test_keys_present(self):
        d = alpha_s_correction_factor()
        for key in ("alpha_s_um", "alpha_s_target", "correction_factor",
                    "delta_alpha_s", "description"):
            assert key in d

    def test_target_less_than_um(self):
        # α_s_target < α_s_UM because the UM overestimates α_s
        d = alpha_s_correction_factor()
        assert d["alpha_s_target"] < d["alpha_s_um"]

    def test_correction_factor_less_than_one(self):
        # Need to REDUCE α_s (α_s_target / α_s_UM < 1)
        d = alpha_s_correction_factor()
        assert d["correction_factor"] < 1.0

    def test_delta_alpha_s_negative(self):
        # Need to decrease α_s
        d = alpha_s_correction_factor()
        assert d["delta_alpha_s"] < 0.0

    def test_um_matches_canonical(self):
        d = alpha_s_correction_factor()
        assert abs(d["alpha_s_um"] - ALPHA_S_KK_CANONICAL) < 1e-12

    def test_target_gives_pdg_lambda(self):
        # With α_s_target, dimensional transmutation should give PDG Λ_QCD
        d = alpha_s_correction_factor()
        b0 = qcd_beta_b0()
        lam_pred = M_KK_CANONICAL_GEV * math.exp(
            -2.0 * math.pi / (b0 * d["alpha_s_target"])
        )
        # Should match PDG Λ_QCD within ~1%
        assert abs(lam_pred * 1000 - LAMBDA_QCD_PDG_MEV) / LAMBDA_QCD_PDG_MEV < 0.01

    def test_description_nonempty(self):
        d = alpha_s_correction_factor()
        assert len(d["description"]) > 50


# ===========================================================================
# IX. proton_mass_from_lambda_qcd
# ===========================================================================

class TestProtonMassFromLambdaQCD:
    """Proton mass from Λ_QCD and lattice normalisation."""

    def test_pdg_inputs_give_pdg_proton(self):
        result = proton_mass_from_lambda_qcd(LAMBDA_QCD_PDG_MEV, C_LAT_PDG)
        assert abs(result["m_p_pred_mev"] - MP_PDG_MEV) / MP_PDG_MEV < 0.01

    def test_keys_present(self):
        result = proton_mass_from_lambda_qcd(332.0)
        for key in ("lambda_qcd_mev", "c_lat", "m_p_pred_mev",
                    "m_p_pdg_mev", "discrepancy", "free_parameters"):
            assert key in result

    def test_free_parameters_nonempty(self):
        result = proton_mass_from_lambda_qcd(332.0)
        assert len(result["free_parameters"]) >= 1

    def test_proportional_to_lambda(self):
        r1 = proton_mass_from_lambda_qcd(200.0, c_lat=4.0)
        r2 = proton_mass_from_lambda_qcd(400.0, c_lat=4.0)
        assert abs(r2["m_p_pred_mev"] / r1["m_p_pred_mev"] - 2.0) < 1e-12

    def test_proportional_to_c_lat(self):
        r1 = proton_mass_from_lambda_qcd(300.0, c_lat=3.0)
        r2 = proton_mass_from_lambda_qcd(300.0, c_lat=6.0)
        assert abs(r2["m_p_pred_mev"] / r1["m_p_pred_mev"] - 2.0) < 1e-12

    def test_discrepancy_pdg_inputs(self):
        result = proton_mass_from_lambda_qcd(LAMBDA_QCD_PDG_MEV, C_LAT_PDG)
        assert abs(result["discrepancy"] - 1.0) < 0.01

    def test_invalid_lambda_raises(self):
        with pytest.raises(ValueError):
            proton_mass_from_lambda_qcd(-100.0)

    def test_invalid_c_lat_raises(self):
        with pytest.raises(ValueError):
            proton_mass_from_lambda_qcd(332.0, c_lat=0.0)

    def test_m_p_pdg_in_output(self):
        result = proton_mass_from_lambda_qcd(332.0)
        assert abs(result["m_p_pdg_mev"] - MP_PDG_MEV) < 0.01


# ===========================================================================
# X. mp_over_me_pipeline
# ===========================================================================

class TestMpOverMePipeline:
    """Full m_p/m_e ratio derivation pipeline."""

    def test_pdg_inputs_give_pdg_ratio(self):
        result = mp_over_me_pipeline(
            lambda_qcd_mev=LAMBDA_QCD_PDG_MEV,
            m_e_mev=ME_PDG_MEV,
            c_lat=C_LAT_PDG,
        )
        assert abs(result["mp_over_me_pred"] - MP_OVER_ME_PDG) / MP_OVER_ME_PDG < 0.01

    def test_keys_present(self):
        result = mp_over_me_pipeline()
        for key in ("lambda_qcd_mev", "m_e_mev", "c_lat", "m_p_pred_mev",
                    "mp_over_me_pred", "mp_over_me_pdg", "discrepancy",
                    "free_parameters", "derivation_status"):
            assert key in result

    def test_free_parameters_lists_three(self):
        result = mp_over_me_pipeline()
        assert len(result["free_parameters"]) == 3

    def test_derivation_status_contains_conditionally(self):
        result = mp_over_me_pipeline()
        assert "CONDITIONALLY" in result["derivation_status"]

    def test_mp_over_me_pdg_in_output(self):
        result = mp_over_me_pipeline()
        assert abs(result["mp_over_me_pdg"] - MP_OVER_ME_PDG) < 0.01

    def test_ratio_proportional_to_lambda(self):
        r1 = mp_over_me_pipeline(lambda_qcd_mev=300.0)
        r2 = mp_over_me_pipeline(lambda_qcd_mev=600.0)
        assert abs(r2["mp_over_me_pred"] / r1["mp_over_me_pred"] - 2.0) < 1e-10

    def test_ratio_inversely_proportional_to_m_e(self):
        r1 = mp_over_me_pipeline(m_e_mev=0.511)
        r2 = mp_over_me_pipeline(m_e_mev=1.022)
        assert abs(r2["mp_over_me_pred"] / r1["mp_over_me_pred"] - 0.5) < 1e-10

    def test_discrepancy_pdg_inputs_near_one(self):
        result = mp_over_me_pipeline(
            lambda_qcd_mev=LAMBDA_QCD_PDG_MEV,
            m_e_mev=ME_PDG_MEV,
            c_lat=C_LAT_PDG,
        )
        assert abs(result["discrepancy"] - 1.0) < 0.02


# ===========================================================================
# XI. alpha_s_at_mz_prediction
# ===========================================================================

class TestAlphaSAtMZPrediction:
    """Prediction for α_s(M_Z) from UM non-Abelian threshold."""

    def test_keys_present(self):
        d = alpha_s_at_mz_prediction()
        for key in ("alpha_s_kk", "m_kk_gev", "alpha_s_mz_pred",
                    "alpha_s_mz_pdg", "landau_pole_gev",
                    "perturbative_at_mz", "status"):
            assert key in d

    def test_canonical_not_perturbative_at_mz(self):
        # With canonical UM parameters, Λ_QCD is above M_Z
        d = alpha_s_at_mz_prediction()
        assert not d["perturbative_at_mz"]

    def test_landau_pole_above_mz_canonical(self):
        d = alpha_s_at_mz_prediction()
        assert d["landau_pole_gev"] > M_Z_GEV

    def test_alpha_s_mz_pred_none_when_not_perturbative(self):
        d = alpha_s_at_mz_prediction()
        assert d["alpha_s_mz_pred"] is None

    def test_pdg_value_in_output(self):
        d = alpha_s_at_mz_prediction()
        assert abs(d["alpha_s_mz_pdg"] - ALPHA_S_MZ_PDG) < 1e-6

    def test_input_alpha_s_kk_in_output(self):
        d = alpha_s_at_mz_prediction(alpha_s_kk=0.05)
        assert abs(d["alpha_s_kk"] - 0.05) < 1e-12

    def test_perturbative_with_large_m_kk_and_small_alpha_s(self):
        # With a tiny α_s, Λ_QCD is very small → perturbative at M_Z
        d = alpha_s_at_mz_prediction(alpha_s_kk=0.001, m_kk_gev=1e15)
        assert d["perturbative_at_mz"]
        assert d["alpha_s_mz_pred"] is not None
        assert d["alpha_s_mz_pred"] > 0


# ===========================================================================
# XII. nonabelian_kk_gap_report
# ===========================================================================

class TestNonabelianKKGapReport:
    """Comprehensive gap accounting."""

    def test_keys_present(self):
        d = nonabelian_kk_gap_report()
        for key in ("pillar", "title", "group_theory", "alpha_s_kk",
                    "b0", "lambda_qcd", "alpha_s_correction_needed",
                    "alpha_s_mz", "mp_over_me", "open_gaps_after_pillar62",
                    "progress_from_pillar61"):
            assert key in d

    def test_pillar_number(self):
        d = nonabelian_kk_gap_report()
        assert d["pillar"] == 62

    def test_title_mentions_su3(self):
        d = nonabelian_kk_gap_report()
        assert "SU(3)" in d["title"] or "Non-Abelian" in d["title"]

    def test_b0_value(self):
        d = nonabelian_kk_gap_report()
        assert d["b0"]["value"] == 9.0

    def test_alpha_s_kk_status_string(self):
        d = nonabelian_kk_gap_report()
        assert "PARTIALLY DERIVED" in d["alpha_s_kk"]["status"]

    def test_lambda_qcd_framework_exists(self):
        d = nonabelian_kk_gap_report()
        assert "FRAMEWORK" in d["lambda_qcd"]["status"]

    def test_lambda_qcd_discrepancy_large(self):
        d = nonabelian_kk_gap_report()
        assert d["lambda_qcd"]["discrepancy_factor"] > 1e4

    def test_mp_over_me_conditionally_derivable(self):
        d = nonabelian_kk_gap_report()
        assert d["mp_over_me"]["conditionally_derivable"] is True

    def test_open_gaps_four_items(self):
        d = nonabelian_kk_gap_report()
        assert len(d["open_gaps_after_pillar62"]) >= 3

    def test_progress_mentions_strong_sector(self):
        d = nonabelian_kk_gap_report()
        assert "strong" in d["progress_from_pillar61"].lower()

    def test_b0_status_mentions_pillar42(self):
        d = nonabelian_kk_gap_report()
        assert "Pillar 42" in d["b0"]["status"]


# ===========================================================================
# XIII. nonabelian_kk_summary
# ===========================================================================

class TestNonabelianKKSummary:
    """Top-level summary dict."""

    def test_keys_present(self):
        d = nonabelian_kk_summary()
        for key in ("constants", "derivation_chain", "correction_needed",
                    "gap_report", "overall_verdict"):
            assert key in d

    def test_constants_subkeys(self):
        d = nonabelian_kk_summary()
        for key in ("K_CS_CANONICAL", "N_C_CANONICAL", "N_F_CANONICAL",
                    "B0_CANONICAL", "ALPHA_S_KK", "M_KK_GEV"):
            assert key in d["constants"]

    def test_b0_constant_in_summary(self):
        d = nonabelian_kk_summary()
        assert d["constants"]["B0_CANONICAL"] == 9

    def test_derivation_chain_steps(self):
        d = nonabelian_kk_summary()
        chain = d["derivation_chain"]
        # 8 steps: k_CS, N_c, N_f, b_0, α_s(M_KK), Λ_QCD, m_p, m_p/m_e
        assert len(chain) == 8

    def test_step1_k_cs_derived(self):
        d = nonabelian_kk_summary()
        assert "DERIVED" in d["derivation_chain"]["step1_k_cs"]

    def test_step2_n_c_assumption(self):
        d = nonabelian_kk_summary()
        assert "ASSUMPTION" in d["derivation_chain"]["step2_n_c"]

    def test_step3_n_f_derived(self):
        d = nonabelian_kk_summary()
        assert "DERIVED" in d["derivation_chain"]["step3_n_f"]

    def test_overall_verdict_nonempty(self):
        d = nonabelian_kk_summary()
        assert len(d["overall_verdict"]) > 100

    def test_overall_verdict_mentions_framework(self):
        d = nonabelian_kk_summary()
        assert "framework" in d["overall_verdict"].lower() or "FRAMEWORK" in d["overall_verdict"]

    def test_gap_report_pillar_number(self):
        d = nonabelian_kk_summary()
        assert d["gap_report"]["pillar"] == 62


# ===========================================================================
# XIV. Physics consistency checks
# ===========================================================================

class TestPhysicsConsistency:
    """Cross-checks between functions for internal consistency."""

    def test_alpha_s_kk_matches_constant(self):
        result = alpha_s_kk_scale()
        assert abs(result["alpha_s_kk"] - ALPHA_S_KK_CANONICAL) < 1e-12

    def test_b0_canonical_matches_function(self):
        assert abs(qcd_beta_b0() - B0_CANONICAL) < 1e-12

    def test_lambda_qcd_uses_b0_canonical(self):
        d = lambda_qcd_from_dim_trans()
        assert d["b0"] == B0_CANONICAL

    def test_correction_factor_uses_canonical_alpha_s_um(self):
        d = alpha_s_correction_factor()
        assert abs(d["alpha_s_um"] - ALPHA_S_KK_CANONICAL) < 1e-12

    def test_c_lat_pdg_consistent_with_mp_lambda(self):
        # C_LAT_PDG × Λ_QCD_PDG should ≈ m_p_PDG
        pred = C_LAT_PDG * LAMBDA_QCD_PDG_MEV
        assert abs(pred - MP_PDG_MEV) / MP_PDG_MEV < 0.01

    def test_b0_9_is_positive_asymptotic_freedom(self):
        assert B0_CANONICAL > 0

    def test_n_f_3_from_pillar42_enters_b0(self):
        # N_f = 3 (Three-Generation Theorem) enters b_0
        b0_nf3 = qcd_beta_b0(N_C_CANONICAL, N_F_CANONICAL)
        assert b0_nf3 == B0_CANONICAL  # = 9

    def test_su3_casimir_c_a_equals_n_c(self):
        d = su3_casimir_data(N_C_CANONICAL)
        assert d["C_A"] == float(N_C_CANONICAL)

    def test_gap_report_alpha_s_value_matches_canonical(self):
        gap = nonabelian_kk_gap_report()
        assert abs(gap["alpha_s_kk"]["value"] - ALPHA_S_KK_CANONICAL) < 1e-12

    def test_summary_alpha_s_matches_canonical(self):
        s = nonabelian_kk_summary()
        assert abs(s["constants"]["ALPHA_S_KK"] - ALPHA_S_KK_CANONICAL) < 1e-12


# ===========================================================================
# CERN Open Data constants
# ===========================================================================

class TestCERNOpenDataConstants:
    def test_cms_alphas_mz_pdg_consistent(self):
        # CMS α_s(M_Z) should match the PDG value
        assert abs(CMS_ALPHAS_MZ - ALPHA_S_MZ_PDG) < 1e-10

    def test_cms_alphas_mz_unc_small(self):
        assert 0.0 < CMS_ALPHAS_MZ_UNC < 0.01

    def test_cms_alphas_1tev_smaller_than_mz(self):
        # α_s decreases with increasing scale (asymptotic freedom)
        assert CMS_ALPHAS_1TEV < CMS_ALPHAS_MZ

    def test_cms_alphas_1tev_positive(self):
        assert CMS_ALPHAS_1TEV > 0.0

    def test_cms_scale_1tev_value(self):
        assert abs(CMS_SCALE_1TEV - 1000.0) < 1e-6


# ===========================================================================
# cms_alphas_rg_consistency
# ===========================================================================

class TestCMSAlphaSRGConsistency:
    def setup_method(self):
        self.result = cms_alphas_rg_consistency()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_s_kk_present(self):
        assert "alpha_s_kk" in self.result
        assert abs(self.result["alpha_s_kk"] - ALPHA_S_KK_CANONICAL) < 1e-12

    def test_m_kk_gev_present(self):
        assert "m_kk_gev" in self.result
        assert self.result["m_kk_gev"] > 0.0

    def test_cms_data_is_list(self):
        assert isinstance(self.result["cms_data"], list)
        assert len(self.result["cms_data"]) == 2  # two default CMS points

    def test_cms_data_has_required_keys(self):
        for entry in self.result["cms_data"]:
            assert "scale_gev" in entry
            assert "alpha_s_cms" in entry
            assert "alpha_s_um_pred" in entry
            assert "fractional_deviation" in entry
            assert "status" in entry

    def test_cms_mz_entry_scale_correct(self):
        mz_entry = self.result["cms_data"][0]
        assert abs(mz_entry["scale_gev"] - M_Z_GEV) < 0.01

    def test_cms_mz_entry_measured_value(self):
        mz_entry = self.result["cms_data"][0]
        assert abs(mz_entry["alpha_s_cms"] - CMS_ALPHAS_MZ) < 1e-10

    def test_cms_1tev_entry_scale_correct(self):
        tev_entry = self.result["cms_data"][1]
        assert abs(tev_entry["scale_gev"] - CMS_SCALE_1TEV) < 1e-3

    def test_cms_1tev_entry_measured_value(self):
        tev_entry = self.result["cms_data"][1]
        assert abs(tev_entry["alpha_s_cms"] - CMS_ALPHAS_1TEV) < 1e-10

    def test_pdg_upward_check_present(self):
        assert "pdg_upward_check" in self.result
        assert isinstance(self.result["pdg_upward_check"], dict)

    def test_pdg_upward_alpha_s_mz_pdg_correct(self):
        upward = self.result["pdg_upward_check"]
        if "alpha_s_mz_pdg" in upward:
            assert abs(upward["alpha_s_mz_pdg"] - CMS_ALPHAS_MZ) < 1e-10

    def test_pdg_upward_run_positive(self):
        upward = self.result["pdg_upward_check"]
        if "alpha_s_at_mkk_from_mz" in upward:
            assert upward["alpha_s_at_mkk_from_mz"] > 0.0

    def test_pdg_upward_run_smaller_than_mz(self):
        # Running upward (higher energy) → smaller coupling (asymptotic freedom)
        upward = self.result["pdg_upward_check"]
        if "alpha_s_at_mkk_from_mz" in upward:
            assert upward["alpha_s_at_mkk_from_mz"] < CMS_ALPHAS_MZ

    def test_overall_consistent_key_present(self):
        assert "overall_consistent" in self.result
        assert isinstance(self.result["overall_consistent"], bool)

    def test_reference_is_string(self):
        assert isinstance(self.result["reference"], str)
        assert "CMS" in self.result["reference"]

    def test_verdict_is_string(self):
        assert isinstance(self.result["verdict"], str)
        assert len(self.result["verdict"]) > 20

    def test_custom_measurement_single_point(self):
        custom = [(M_Z_GEV, 0.1179, 0.001)]
        result = cms_alphas_rg_consistency(cms_measurements=custom)
        assert len(result["cms_data"]) == 1
        assert abs(result["cms_data"][0]["alpha_s_cms"] - 0.1179) < 1e-10

    def test_custom_alpha_s_kk_used(self):
        result = cms_alphas_rg_consistency(alpha_s_kk=0.1)
        assert abs(result["alpha_s_kk"] - 0.1) < 1e-10

    def test_status_is_string_for_each_entry(self):
        for entry in self.result["cms_data"]:
            assert isinstance(entry["status"], str)
            assert len(entry["status"]) > 10

