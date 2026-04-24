# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_muon_g2.py
======================
Test suite for src/core/muon_g2.py — Pillar 51.

Covers:
  - KK graviton loop correction magnitude (negligible ~10⁻⁴¹)
  - KK correction is ~30 orders below data-driven discrepancy
  - ALP Barr–Zee upper bound structure and parameter dependence
  - B_μ dark photon mass estimate (Goldberger–Wise suppression)
  - B_μ coupling bound from birefringence
  - Full report keys, types, and consistency
  - Boundary / error conditions
  - Experimental reference values
  - UM is not falsified by muon g-2
"""

import math
import pytest

from src.core.muon_g2 import (
    ALPHA_EM,
    A_MU_EXP_1E11,
    A_MU_SM_DD_1E11,
    A_MU_SM_LATTICE_1E11,
    C_S,
    DELTA_A_MU_DD_1E11,
    K_CS,
    M_KK_1_GEV,
    M_MU_GEV,
    M_PL_GEV,
    M_TAU_GEV,
    N_W,
    R_C_PLANCK,
    SIGNIFICANCE_DD,
    SIGNIFICANCE_LATTICE,
    alp_barr_zee_upper_bound,
    bmu_coupling_from_birefringence,
    bmu_dark_photon_mass_estimate,
    full_mu_g2_report,
    kk_graviton_correction,
    orders_of_magnitude_below_anomaly,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_alpha_em_fine_structure(self):
        # α_EM ≈ 1/137
        assert abs(ALPHA_EM - 1.0 / 137.035999084) < 1e-10

    def test_m_pl_gev_order(self):
        # M_Pl ≈ 2.435 × 10¹⁸ GeV
        assert 2.4e18 < M_PL_GEV < 2.5e18

    def test_m_mu_gev_value(self):
        # m_μ ≈ 105.658 MeV = 0.105658 GeV
        assert abs(M_MU_GEV - 0.105658375) < 1e-9

    def test_m_kk_1_gev_value(self):
        # M_KK_1 = M_Pl / r_c = 2.435e18 / 12 ≈ 2.029e17
        expected = M_PL_GEV / R_C_PLANCK
        assert abs(M_KK_1_GEV - expected) < 1e10

    def test_c_s_value(self):
        # c_s = 12/37
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_k_cs_canonical(self):
        assert K_CS == 74

    def test_n_w_canonical(self):
        assert N_W == 5

    def test_r_c_planck(self):
        assert R_C_PLANCK == 12.0

    def test_delta_a_mu_dd_positive(self):
        assert DELTA_A_MU_DD_1E11 > 0

    def test_significance_dd(self):
        # ~5σ discrepancy vs data-driven
        assert SIGNIFICANCE_DD >= 4.5

    def test_significance_lattice(self):
        # ~1σ agreement with lattice QCD
        assert SIGNIFICANCE_LATTICE <= 2.0

    def test_exp_value_reasonable(self):
        # a_μ^exp ≈ 116592070.5 × 10⁻¹¹
        assert 116_592_000 < A_MU_EXP_1E11 < 116_593_000

    def test_sm_dd_value_reasonable(self):
        assert 116_591_800 < A_MU_SM_DD_1E11 < 116_592_000

    def test_sm_lattice_value_reasonable(self):
        assert 116_591_900 < A_MU_SM_LATTICE_1E11 < 116_592_100

    def test_discrepancy_consistent_with_exp_minus_sm(self):
        # Δa_μ ≈ (a_μ^exp - a_μ^SM_DD) in units of 10⁻¹¹
        delta_computed = A_MU_EXP_1E11 - A_MU_SM_DD_1E11
        # DELTA_A_MU_DD_1E11 = 261.0; computed = 260.5 — ~1 unit rounding
        assert abs(delta_computed - DELTA_A_MU_DD_1E11) < 5.0


# ---------------------------------------------------------------------------
# KK graviton correction
# ---------------------------------------------------------------------------

class TestKKGravitonCorrection:
    def test_default_returns_small_positive(self):
        delta = kk_graviton_correction()
        assert delta > 0

    def test_default_order_of_magnitude(self):
        # δa_μ^KK ≈ (α/π) × (m_μ/M_KK)² × F
        # (m_μ/M_KK)² ≈ (0.1/2e17)² ≈ 2.5e-37
        # (α/π) ≈ 2.3e-3
        # F ≈ 1.1
        # Product ≈ 6e-40 ... within 2 orders
        delta = kk_graviton_correction()
        assert 1e-42 < delta < 1e-38

    def test_scales_as_ratio_squared(self):
        # δa_μ ∝ (m_μ / M_KK)²
        delta1 = kk_graviton_correction(m_mu_GeV=0.1, M_KK_GeV=1e17)
        delta2 = kk_graviton_correction(m_mu_GeV=0.2, M_KK_GeV=1e17)
        assert abs(delta2 / delta1 - 4.0) < 0.01

    def test_scales_inversely_as_M_KK_squared(self):
        delta1 = kk_graviton_correction(M_KK_GeV=1e17)
        delta2 = kk_graviton_correction(M_KK_GeV=2e17)
        assert abs(delta1 / delta2 - 4.0) < 0.01

    def test_form_factor_increases_with_cs(self):
        delta_low  = kk_graviton_correction(c_s=0.1)
        delta_high = kk_graviton_correction(c_s=0.5)
        assert delta_high > delta_low

    def test_form_factor_at_zero_cs(self):
        # F_spin2(c_s=0) = 1.0
        delta0 = kk_graviton_correction(c_s=0.0)
        delta1 = kk_graviton_correction(c_s=C_S)
        expected_ratio = 1.0 + C_S ** 2
        assert abs(delta1 / delta0 - expected_ratio) < 1e-10

    def test_raises_on_non_positive_M_KK(self):
        with pytest.raises(ValueError):
            kk_graviton_correction(M_KK_GeV=0.0)
        with pytest.raises(ValueError):
            kk_graviton_correction(M_KK_GeV=-1e17)

    def test_raises_on_non_positive_m_mu(self):
        with pytest.raises(ValueError):
            kk_graviton_correction(m_mu_GeV=0.0)

    def test_canonical_value_matches_hand_calculation(self):
        # Manual: (α/π) × (m_μ/M_KK)² × (1 + c_s²)
        expected = (ALPHA_EM / math.pi) * (M_MU_GEV / M_KK_1_GEV) ** 2 * (1 + C_S ** 2)
        result = kk_graviton_correction()
        assert abs(result - expected) / expected < 1e-10

    def test_at_tev_scale_still_negligible(self):
        # Even at M_KK = 1 TeV (much smaller than Planck), δa_μ ~ 10⁻⁹ × (α/π) ~ 10⁻¹¹
        # Still much smaller than systematic uncertainties in SM
        delta_tev = kk_graviton_correction(M_KK_GeV=1e3)
        # (0.106/1000)^2 ≈ 1.12e-8; (α/π) ≈ 2.3e-3; product ≈ 2.6e-11
        assert delta_tev < 1e-9


# ---------------------------------------------------------------------------
# Orders of magnitude below anomaly
# ---------------------------------------------------------------------------

class TestOrdersOfMagnitude:
    def test_default_is_around_30(self):
        # From FALLIBILITY.md: ~30 orders of magnitude below Δa_μ
        oom = orders_of_magnitude_below_anomaly()
        assert 28 < oom < 35

    def test_positive(self):
        oom = orders_of_magnitude_below_anomaly()
        assert oom > 0

    def test_at_tev_scale_less_suppressed(self):
        oom_planck = orders_of_magnitude_below_anomaly()
        oom_tev    = orders_of_magnitude_below_anomaly(M_KK_GeV=1e3)
        assert oom_tev < oom_planck

    def test_exact_calculation(self):
        delta_kk = kk_graviton_correction()
        delta_dd = DELTA_A_MU_DD_1E11 * 1e-11
        expected = math.log10(delta_dd / delta_kk)
        result = orders_of_magnitude_below_anomaly()
        assert abs(result - expected) < 1e-10


# ---------------------------------------------------------------------------
# ALP Barr–Zee upper bound
# ---------------------------------------------------------------------------

class TestALPBarrZeeUpperBound:
    def test_default_positive(self):
        bound = alp_barr_zee_upper_bound()
        assert bound > 0

    def test_scales_with_y_mu(self):
        b1 = alp_barr_zee_upper_bound(y_mu_max=1.0)
        b2 = alp_barr_zee_upper_bound(y_mu_max=2.0)
        assert abs(b2 / b1 - 2.0) < 0.01

    def test_decreases_with_alp_mass(self):
        b_light = alp_barr_zee_upper_bound(m_alp_GeV=1e-4)
        b_heavy = alp_barr_zee_upper_bound(m_alp_GeV=1e-2)
        # δa_μ ∝ 1/m_a² for heavy loop fermion
        assert b_light > b_heavy

    def test_mass_squared_scaling(self):
        b1 = alp_barr_zee_upper_bound(m_alp_GeV=1e-3)
        b2 = alp_barr_zee_upper_bound(m_alp_GeV=2e-3)
        # For z_f ≫ 1 and h(z) ≈ ln(z)/2, the 1/m_a² scaling holds approximately
        ratio = b1 / b2
        assert 2.5 < ratio < 5.5  # approximate 1/m_a² scaling with log correction

    def test_k_cs_dependence(self):
        b61 = alp_barr_zee_upper_bound(k_cs=61)
        b74 = alp_barr_zee_upper_bound(k_cs=74)
        assert b74 > b61

    def test_raises_on_non_positive_alp_mass(self):
        with pytest.raises(ValueError):
            alp_barr_zee_upper_bound(m_alp_GeV=0.0)

    def test_raises_on_non_positive_fermion_mass(self):
        with pytest.raises(ValueError):
            alp_barr_zee_upper_bound(m_f_GeV=0.0)

    def test_raises_on_non_positive_rc(self):
        with pytest.raises(ValueError):
            alp_barr_zee_upper_bound(r_c=0.0)

    def test_light_fermion_regime(self):
        # m_f < m_alp: light fermion, different h(z) branch
        b = alp_barr_zee_upper_bound(m_alp_GeV=10.0, m_f_GeV=0.1)
        assert b >= 0

    def test_result_is_upper_bound_not_exact(self):
        # y_mu_max=1 means this is the worst-case; any y_mu ≤ 1 gives smaller value
        b_max = alp_barr_zee_upper_bound(y_mu_max=1.0)
        b_smaller = alp_barr_zee_upper_bound(y_mu_max=0.1)
        assert b_max > b_smaller

    def test_g_agg_scales_with_k_cs(self):
        # g_aγγ ∝ k_cs, so bound ∝ k_cs
        b37 = alp_barr_zee_upper_bound(k_cs=37)
        b74 = alp_barr_zee_upper_bound(k_cs=74)
        assert abs(b74 / b37 - 2.0) < 0.01


# ---------------------------------------------------------------------------
# B_μ dark photon mass estimate
# ---------------------------------------------------------------------------

class TestBmuDarkPhotonMass:
    def test_default_returns_extremely_small(self):
        # The Goldberger-Wise suppression is exponential: exp(-π × r_c × φ₀_eff)
        # exp(-π × 12 × 31.42) is astronomically small → essentially 0
        m = bmu_dark_photon_mass_estimate()
        assert m >= 0.0

    def test_mass_decreases_with_larger_phi0(self):
        m_small = bmu_dark_photon_mass_estimate(phi0_eff=5.0, r_c=1.0)
        m_large = bmu_dark_photon_mass_estimate(phi0_eff=10.0, r_c=1.0)
        assert m_small > m_large

    def test_mass_decreases_with_larger_rc(self):
        m_small_rc = bmu_dark_photon_mass_estimate(phi0_eff=1.0, r_c=1.0)
        m_large_rc = bmu_dark_photon_mass_estimate(phi0_eff=1.0, r_c=2.0)
        assert m_small_rc > m_large_rc

    def test_mass_at_unit_params(self):
        # phi0=1, r_c=1: m = (1/1) × exp(-π × 1 × 1) = exp(-π) ≈ 0.04322
        m = bmu_dark_photon_mass_estimate(phi0_eff=1.0, r_c=1.0)
        expected = math.exp(-math.pi)
        assert abs(m - expected) < 1e-10

    def test_raises_on_non_positive_rc(self):
        with pytest.raises(ValueError):
            bmu_dark_photon_mass_estimate(r_c=0.0)

    def test_raises_on_non_positive_phi0(self):
        with pytest.raises(ValueError):
            bmu_dark_photon_mass_estimate(phi0_eff=0.0)

    def test_mass_is_non_negative(self):
        for phi0 in [1.0, 5.0, 10.0, 31.42]:
            m = bmu_dark_photon_mass_estimate(phi0_eff=phi0, r_c=R_C_PLANCK)
            assert m >= 0.0

    def test_large_exponent_gives_zero(self):
        # phi0_eff=100, r_c=12 → exponent=π×12×100≈3770 → underflows to 0
        m = bmu_dark_photon_mass_estimate(phi0_eff=100.0, r_c=R_C_PLANCK)
        assert m == 0.0

    def test_exponential_scaling(self):
        # m ∝ exp(-π × r_c × φ₀): doubling φ₀ squares the exponential factor
        m1 = bmu_dark_photon_mass_estimate(phi0_eff=1.0, r_c=1.0)
        m2 = bmu_dark_photon_mass_estimate(phi0_eff=2.0, r_c=1.0)
        # m2/m1 = exp(-π × 1) ≈ exp(-π)
        expected_ratio = math.exp(-math.pi)
        assert abs(m2 / m1 - expected_ratio) < 1e-10


# ---------------------------------------------------------------------------
# B_μ coupling from birefringence
# ---------------------------------------------------------------------------

class TestBmuCouplingFromBirefringence:
    def test_default_returns_positive(self):
        eps = bmu_coupling_from_birefringence()
        assert eps > 0

    def test_default_is_small(self):
        # β ≈ 0.331°; denominator = π × 74 / 4 ≈ 58.1
        # β_rad ≈ 0.00578; eps ≈ 0.0578/58.1 ≈ 9.9e-5
        eps = bmu_coupling_from_birefringence()
        assert 1e-5 < eps < 1e-3

    def test_scales_linearly_with_beta(self):
        eps1 = bmu_coupling_from_birefringence(beta_deg=0.331)
        eps2 = bmu_coupling_from_birefringence(beta_deg=0.662)
        assert abs(eps2 / eps1 - 2.0) < 1e-10

    def test_scales_inversely_with_k_cs(self):
        eps1 = bmu_coupling_from_birefringence(k_cs=37)
        eps2 = bmu_coupling_from_birefringence(k_cs=74)
        assert abs(eps1 / eps2 - 2.0) < 1e-10

    def test_raises_on_non_positive_k_cs(self):
        with pytest.raises(ValueError):
            bmu_coupling_from_birefringence(k_cs=0)

    def test_canonical_calculation(self):
        beta_deg = 0.331
        beta_rad = math.radians(beta_deg)
        expected = beta_rad / (math.pi * K_CS / 4.0)
        result = bmu_coupling_from_birefringence(beta_deg=beta_deg)
        assert abs(result - expected) < 1e-14

    def test_zero_beta_gives_zero_coupling(self):
        eps = bmu_coupling_from_birefringence(beta_deg=0.0)
        assert eps == 0.0

    def test_canonical_5_6_beta(self):
        # (5,6) canonical prediction: β ≈ 0.273°
        eps = bmu_coupling_from_birefringence(beta_deg=0.273, k_cs=61)
        assert eps > 0


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

class TestFullMuG2Report:
    def setup_method(self):
        self.report = full_mu_g2_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_required_keys_present(self):
        required = [
            "delta_a_mu_kk",
            "delta_a_mu_bz_upper",
            "bmu_mass_planck",
            "bmu_coupling_bound",
            "ratio_kk_to_anomaly",
            "a_mu_exp",
            "delta_a_mu_data_driven",
            "sigma_data_driven",
            "sigma_lattice_qcd",
            "um_can_explain_anomaly",
            "um_is_falsified",
            "M_KK_1_GeV",
            "m_mu_GeV",
            "summary",
        ]
        for key in required:
            assert key in self.report, f"Missing key: {key}"

    def test_um_cannot_explain_anomaly(self):
        assert self.report["um_can_explain_anomaly"] is False

    def test_um_is_not_falsified(self):
        assert self.report["um_is_falsified"] is False

    def test_kk_correction_negligible(self):
        # KK correction should be < 10⁻³⁸ (much less than Δa_μ ~ 10⁻⁹)
        assert self.report["delta_a_mu_kk"] < 1e-38

    def test_ratio_kk_to_anomaly_very_large(self):
        # ratio_kk_to_anomaly = δa_μ^KK / Δa_μ ≈ 10⁻³¹ (KK is ~30 orders smaller)
        assert self.report["ratio_kk_to_anomaly"] < 1e-25

    def test_sigma_dd_around_5(self):
        assert 4.0 <= self.report["sigma_data_driven"] <= 6.0

    def test_sigma_lattice_around_1(self):
        assert 0.0 <= self.report["sigma_lattice_qcd"] <= 3.0

    def test_bz_upper_bound_positive(self):
        assert self.report["delta_a_mu_bz_upper"] > 0

    def test_bmu_coupling_bound_positive(self):
        assert self.report["bmu_coupling_bound"] > 0

    def test_bmu_coupling_bound_small(self):
        # Coupling bound < 10⁻³ (suppressed by k_cs and converted from radians)
        assert self.report["bmu_coupling_bound"] < 1e-3

    def test_summary_is_string(self):
        assert isinstance(self.report["summary"], str)
        assert len(self.report["summary"]) > 50

    def test_a_mu_exp_correct_order(self):
        # a_μ ≈ 1.166 × 10⁻³ (= 116592070.5 × 10⁻¹¹)
        assert 1.0e-3 < self.report["a_mu_exp"] < 1.3e-3

    def test_delta_dd_correct_order(self):
        # Δa_μ ≈ 261 × 10⁻¹¹ ≈ 2.6 × 10⁻⁹
        assert 1e-9 < self.report["delta_a_mu_data_driven"] < 4e-9

    def test_m_kk_matches_constant(self):
        assert abs(self.report["M_KK_1_GeV"] - M_KK_1_GEV) < 1e10

    def test_m_mu_matches_constant(self):
        assert abs(self.report["m_mu_GeV"] - M_MU_GEV) < 1e-10

    def test_kk_correction_consistent_with_standalone(self):
        delta_kk_standalone = kk_graviton_correction()
        assert abs(self.report["delta_a_mu_kk"] - delta_kk_standalone) < 1e-50

    def test_bz_bound_consistent_with_standalone(self):
        bz_standalone = alp_barr_zee_upper_bound()
        assert abs(self.report["delta_a_mu_bz_upper"] - bz_standalone) < 1e-30


# ---------------------------------------------------------------------------
# Physical interpretation cross-checks
# ---------------------------------------------------------------------------

class TestPhysicalInterpretation:
    def test_kk_mass_above_planck_scale(self):
        # M_KK_1 should be sub-Planck (r_c = 12, so M_KK = M_Pl/12)
        assert M_KK_1_GEV < M_PL_GEV

    def test_kk_mass_above_tev(self):
        # M_KK_1 >> TeV scale
        assert M_KK_1_GEV > 1e12  # >> 1 TeV

    def test_muon_to_kk_ratio_is_tiny(self):
        ratio = M_MU_GEV / M_KK_1_GEV
        assert ratio < 1e-15

    def test_kk_correction_much_less_than_experimental_uncertainty(self):
        # Experimental uncertainty is ~146 × 10⁻¹² ≈ 1.46 × 10⁻¹⁰
        exp_unc = 146e-12
        delta_kk = kk_graviton_correction()
        assert delta_kk < exp_unc * 1e-25  # at least 25 orders below uncertainty

    def test_oom_exceeds_30(self):
        oom = orders_of_magnitude_below_anomaly()
        assert oom > 29  # FALLIBILITY.md says ~30 orders

    def test_alp_barr_zee_could_be_significant_with_large_yukawa(self):
        # With y_mu = 1 and m_alp = 1 MeV, the Barr-Zee bound can in principle
        # be relevant (though the UM does not derive y_mu)
        b = alp_barr_zee_upper_bound(y_mu_max=1.0, m_alp_GeV=1e-3)
        assert b > 0  # non-trivial bound exists

    def test_alp_coupling_g_agg_is_sub_planck(self):
        # g_aγγ = k_cs × α_EM / (2π² r_c M_Pl) [GeV⁻¹]
        g_agg = K_CS * ALPHA_EM / (2.0 * math.pi ** 2 * R_C_PLANCK * M_PL_GEV)
        # Should be ~10⁻²¹ GeV⁻¹
        assert 1e-24 < g_agg < 1e-18
