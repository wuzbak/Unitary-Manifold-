# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ew_hierarchy.py
===========================
Test suite for src/core/ew_hierarchy.py (Pillar 50).

Sections
--------
1  Module-level constants
2  Utility — um_ew_scale_planck, hierarchy_gap_log10
3  Mechanism 1: RS1 / GW warp factor
4  Mechanism 2: EC-KK torsion
5  Mechanism 3: AdS₅/CFT₄ tower
6  §4 Higgs quartic (λ problem)
7  §5 Yukawa hierarchy (flavor puzzle)
8  §6 (5,7) braid topology and warp factor
9  HierarchyComparison dataclass
10 compare_hierarchy_mechanisms driver
"""
import math
import pytest

import src.core.ew_hierarchy as ew


# ============================================================================
# 1  Constants
# ============================================================================

class TestConstants:
    def test_n_w_canonical(self):
        assert ew.N_W_CANONICAL == 5

    def test_k_cs_canonical(self):
        assert ew.K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(ew.C_S_CANONICAL - 12.0 / 37.0) < 1e-15

    def test_planck_mass_gev_order(self):
        assert 1.2e19 < ew.PLANCK_MASS_GEV < 1.3e19

    def test_higgs_vev_gev(self):
        assert ew.HIGGS_VEV_GEV == 246.0

    def test_higgs_mass_gev(self):
        assert ew.HIGGS_MASS_GEV == 125.09

    def test_higgs_quartic_value(self):
        lam = 125.09 ** 2 / (2.0 * 246.0 ** 2)
        assert abs(ew.HIGGS_QUARTIC - lam) < 1e-12

    def test_higgs_quartic_around_0p13(self):
        assert 0.12 < ew.HIGGS_QUARTIC < 0.14

    def test_um_ew_scale_planck_value(self):
        expected = math.sqrt((12.0 / 37.0) / 74.0)
        assert abs(ew.UM_EW_SCALE_PLANCK - expected) < 1e-12

    def test_um_ew_scale_planck_order(self):
        assert 0.06 < ew.UM_EW_SCALE_PLANCK < 0.07

    def test_observed_ew_scale_planck(self):
        expected = 246.0 / 1.220890e19
        assert abs(ew.OBSERVED_EW_SCALE_PLANCK - expected) < 1e-30

    def test_hierarchy_gap_log10_positive(self):
        assert ew.HIERARCHY_GAP_LOG10 > 0

    def test_hierarchy_gap_log10_around_15(self):
        assert 15.0 < ew.HIERARCHY_GAP_LOG10 < 16.0

    def test_rs1_kpi_R_canonical(self):
        expected = math.log(1.220890e19 / 246.0)
        assert abs(ew.RS1_KPI_R_CANONICAL - expected) < 1e-10

    def test_rs1_kpi_R_around_38(self):
        assert 38.0 < ew.RS1_KPI_R_CANONICAL < 39.0

    def test_ads5_krs_rc_canonical(self):
        assert abs(ew.ADS5_KRS_RC_CANONICAL - ew.RS1_KPI_R_CANONICAL / math.pi) < 1e-12

    def test_ads5_krs_rc_around_12(self):
        assert 12.0 < ew.ADS5_KRS_RC_CANONICAL < 13.0

    def test_ads5_ir_radius_planck(self):
        expected = 1.220890e19 / 246.0
        assert abs(ew.ADS5_IR_RADIUS_PLANCK - expected) < 1e10

    def test_braid_n1_n2(self):
        assert ew.BRAID_N1 == 5
        assert ew.BRAID_N2 == 7

    def test_braid_crossing_sum(self):
        assert ew.BRAID_CROSSING_SUM == 12

    def test_braid_linking_number_canonical(self):
        assert ew.BRAID_LINKING_NUMBER_CANONICAL == 35


# ============================================================================
# 2  Utilities
# ============================================================================

class TestUMEWScalePlanck:
    def test_canonical(self):
        val = ew.um_ew_scale_planck()
        assert abs(val - math.sqrt((12.0 / 37.0) / 74.0)) < 1e-12

    def test_c_s_1_k_cs_1(self):
        assert abs(ew.um_ew_scale_planck(1.0, 1) - 1.0) < 1e-12

    def test_c_s_4_k_cs_1(self):
        assert abs(ew.um_ew_scale_planck(4.0, 1) - 2.0) < 1e-12

    def test_c_s_small(self):
        assert ew.um_ew_scale_planck(1e-8, 1) < 1e-3

    def test_returns_positive(self):
        assert ew.um_ew_scale_planck() > 0

    def test_invalid_c_s(self):
        with pytest.raises(ValueError):
            ew.um_ew_scale_planck(c_s=0.0)

    def test_invalid_k_cs(self):
        with pytest.raises(ValueError):
            ew.um_ew_scale_planck(k_cs=0)

    def test_scales_with_c_s(self):
        v1 = ew.um_ew_scale_planck(c_s=1.0, k_cs=4)
        v2 = ew.um_ew_scale_planck(c_s=4.0, k_cs=4)
        assert abs(v2 / v1 - 2.0) < 1e-12


class TestHierarchyGapLog10:
    def test_canonical_positive(self):
        assert ew.hierarchy_gap_log10() > 0

    def test_canonical_around_15(self):
        assert 15.0 < ew.hierarchy_gap_log10() < 16.0

    def test_equals_constant(self):
        assert abs(ew.hierarchy_gap_log10() - ew.HIERARCHY_GAP_LOG10) < 1e-12

    def test_larger_vev_smaller_gap(self):
        g1 = ew.hierarchy_gap_log10(higgs_vev_gev=246.0)
        g2 = ew.hierarchy_gap_log10(higgs_vev_gev=1000.0)
        assert g2 < g1

    def test_invalid_higgs_vev(self):
        with pytest.raises(ValueError):
            ew.hierarchy_gap_log10(higgs_vev_gev=0.0)

    def test_invalid_m_planck(self):
        with pytest.raises(ValueError):
            ew.hierarchy_gap_log10(m_planck_gev=-1.0)


# ============================================================================
# 3  Mechanism 1 — RS1 / GW warp factor
# ============================================================================

class TestRS1WarpFactor:
    def test_kpi_R_zero(self):
        assert abs(ew.rs1_warp_factor(0.0) - 1.0) < 1e-15

    def test_kpi_R_1(self):
        assert abs(ew.rs1_warp_factor(1.0) - math.exp(-1.0)) < 1e-15

    def test_canonical(self):
        expected = math.exp(-ew.RS1_KPI_R_CANONICAL)
        assert abs(ew.rs1_warp_factor(ew.RS1_KPI_R_CANONICAL) - expected) < 1e-25

    def test_canonical_equals_observed_ew_scale(self):
        w = ew.rs1_warp_factor(ew.RS1_KPI_R_CANONICAL)
        assert abs(w - ew.OBSERVED_EW_SCALE_PLANCK) < 1e-22

    def test_monotone_decreasing(self):
        v1 = ew.rs1_warp_factor(10.0)
        v2 = ew.rs1_warp_factor(20.0)
        assert v1 > v2

    def test_in_unit_interval(self):
        for kpi in [0.0, 1.0, 10.0, 38.44]:
            assert 0.0 < ew.rs1_warp_factor(kpi) <= 1.0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ew.rs1_warp_factor(-0.1)


class TestRS1EWScaleGev:
    def test_canonical_246(self):
        val = ew.rs1_ew_scale_gev(ew.RS1_KPI_R_CANONICAL)
        assert abs(val - 246.0) < 1e-8

    def test_kpi_R_zero_returns_m_planck(self):
        val = ew.rs1_ew_scale_gev(0.0, m_planck_gev=1e10)
        assert abs(val - 1e10) < 1e-4

    def test_scales_with_m_planck(self):
        v1 = ew.rs1_ew_scale_gev(1.0, m_planck_gev=1e10)
        v2 = ew.rs1_ew_scale_gev(1.0, m_planck_gev=2e10)
        assert abs(v2 / v1 - 2.0) < 1e-12

    def test_invalid_m_planck(self):
        with pytest.raises(ValueError):
            ew.rs1_ew_scale_gev(1.0, m_planck_gev=0.0)


class TestRS1KpiRForEWScale:
    def test_canonical_is_log_ratio(self):
        val = ew.rs1_kpi_R_for_ew_scale()
        expected = math.log(ew.PLANCK_MASS_GEV / 246.0)
        assert abs(val - expected) < 1e-10

    def test_roundtrip(self):
        kpi = ew.rs1_kpi_R_for_ew_scale()
        v = ew.rs1_ew_scale_gev(kpi)
        assert abs(v - 246.0) < 1e-8

    def test_larger_vev_smaller_kpi(self):
        k1 = ew.rs1_kpi_R_for_ew_scale(higgs_vev_gev=246.0)
        k2 = ew.rs1_kpi_R_for_ew_scale(higgs_vev_gev=1000.0)
        assert k2 < k1

    def test_invalid_vev_zero(self):
        with pytest.raises(ValueError):
            ew.rs1_kpi_R_for_ew_scale(higgs_vev_gev=0.0)

    def test_invalid_vev_too_large(self):
        with pytest.raises(ValueError):
            ew.rs1_kpi_R_for_ew_scale(higgs_vev_gev=2e19, m_planck_gev=1e19)

    def test_positive(self):
        assert ew.rs1_kpi_R_for_ew_scale() > 0


class TestGWPhiMin:
    def test_canonical_ratio(self):
        phi_min = ew.gw_phi_min_for_ew_scale()
        expected = 1.0 * (246.0 / ew.PLANCK_MASS_GEV)
        assert abs(phi_min - expected) < 1e-30

    def test_phi0_scaling(self):
        p1 = ew.gw_phi_min_for_ew_scale(phi0=1.0)
        p2 = ew.gw_phi_min_for_ew_scale(phi0=2.0)
        assert abs(p2 / p1 - 2.0) < 1e-12

    def test_vev_scaling(self):
        p1 = ew.gw_phi_min_for_ew_scale(higgs_vev_gev=246.0)
        p2 = ew.gw_phi_min_for_ew_scale(higgs_vev_gev=492.0)
        assert abs(p2 / p1 - 2.0) < 1e-12

    def test_invalid_phi0(self):
        with pytest.raises(ValueError):
            ew.gw_phi_min_for_ew_scale(phi0=0.0)

    def test_less_than_phi0(self):
        phi_min = ew.gw_phi_min_for_ew_scale()
        assert phi_min < 1.0


class TestGWEffectiveKpiR:
    def test_equals_log_ratio(self):
        phi_min = 1e-17
        phi0 = 1.0
        val = ew.gw_effective_kpi_R(phi_min, phi0)
        assert abs(val - math.log(phi0 / phi_min)) < 1e-12

    def test_canonical_ew_roundtrip(self):
        phi_min = ew.gw_phi_min_for_ew_scale()
        kpi = ew.gw_effective_kpi_R(phi_min, phi0=1.0)
        assert abs(kpi - ew.RS1_KPI_R_CANONICAL) < 1e-6

    def test_phi_min_equals_phi0_raises(self):
        with pytest.raises(ValueError):
            ew.gw_effective_kpi_R(phi_min=1.0, phi0=1.0)

    def test_phi_min_larger_raises(self):
        with pytest.raises(ValueError):
            ew.gw_effective_kpi_R(phi_min=2.0, phi0=1.0)

    def test_phi_min_zero_raises(self):
        with pytest.raises(ValueError):
            ew.gw_effective_kpi_R(phi_min=0.0, phi0=1.0)


# ============================================================================
# 4  Mechanism 2 — EC-KK torsion
# ============================================================================

class TestECKKTorsionMassSq:
    def test_zero_kappa(self):
        assert ew.ec_kk_torsion_mass_sq(0.0) == 0.0

    def test_kappa_1_m_kk_1(self):
        val = ew.ec_kk_torsion_mass_sq(1.0, n_w=5, k_cs=74, m_kk=1.0)
        expected = (5.0 / 74.0) ** 2
        assert abs(val - expected) < 1e-15

    def test_scales_linearly_with_kappa(self):
        v1 = ew.ec_kk_torsion_mass_sq(1.0)
        v2 = ew.ec_kk_torsion_mass_sq(2.0)
        assert abs(v2 / v1 - 2.0) < 1e-12

    def test_scales_as_m_kk_squared(self):
        v1 = ew.ec_kk_torsion_mass_sq(1.0, m_kk=1.0)
        v2 = ew.ec_kk_torsion_mass_sq(1.0, m_kk=2.0)
        assert abs(v2 / v1 - 4.0) < 1e-12

    def test_positive(self):
        assert ew.ec_kk_torsion_mass_sq(0.5) > 0

    def test_invalid_kappa(self):
        with pytest.raises(ValueError):
            ew.ec_kk_torsion_mass_sq(-0.1)

    def test_invalid_m_kk(self):
        with pytest.raises(ValueError):
            ew.ec_kk_torsion_mass_sq(1.0, m_kk=0.0)


class TestECKKHiggsVevPlanck:
    def test_zero_kappa(self):
        assert ew.ec_kk_higgs_vev_planck(0.0) == 0.0

    def test_kappa_1_m_kk_1(self):
        val = ew.ec_kk_higgs_vev_planck(1.0)
        mu_sq = ew.ec_kk_torsion_mass_sq(1.0)
        expected = math.sqrt(mu_sq / (2.0 * ew.HIGGS_QUARTIC))
        assert abs(val - expected) < 1e-12

    def test_scales_as_sqrt_kappa(self):
        v1 = ew.ec_kk_higgs_vev_planck(1.0)
        v4 = ew.ec_kk_higgs_vev_planck(4.0)
        assert abs(v4 / v1 - 2.0) < 1e-10

    def test_invalid_lambda_h(self):
        with pytest.raises(ValueError):
            ew.ec_kk_higgs_vev_planck(1.0, lambda_h=0.0)


class TestECKKHiggsVevGev:
    def test_scales_with_m_planck(self):
        v1 = ew.ec_kk_higgs_vev_gev(1.0, m_planck_gev=1e10)
        v2 = ew.ec_kk_higgs_vev_gev(1.0, m_planck_gev=2e10)
        assert abs(v2 / v1 - 2.0) < 1e-10

    def test_invalid_m_planck(self):
        with pytest.raises(ValueError):
            ew.ec_kk_higgs_vev_gev(1.0, m_planck_gev=0.0)


class TestKappaTForEWScale:
    def test_roundtrip(self):
        kappa = ew.kappa_T_for_ew_scale()
        vev = ew.ec_kk_higgs_vev_gev(kappa)
        assert abs(vev - 246.0) < 1e-5

    def test_extremely_small(self):
        kappa = ew.kappa_T_for_ew_scale()
        assert kappa < 1e-30

    def test_scales_as_vev_squared(self):
        k1 = ew.kappa_T_for_ew_scale(higgs_vev_gev=246.0)
        k2 = ew.kappa_T_for_ew_scale(higgs_vev_gev=492.0)
        assert abs(k2 / k1 - 4.0) < 1e-8

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            ew.kappa_T_for_ew_scale(higgs_vev_gev=0.0)

    def test_positive(self):
        assert ew.kappa_T_for_ew_scale() > 0


# ============================================================================
# 5  Mechanism 3 — AdS₅/CFT₄ tower
# ============================================================================

class TestAds5IRCompactificationRadius:
    def test_canonical_value(self):
        R_IR = ew.ads5_ir_compactification_radius()
        expected = ew.PLANCK_MASS_GEV / 246.0
        assert abs(R_IR / expected - 1.0) < 1e-10

    def test_large(self):
        assert ew.ads5_ir_compactification_radius() > 1e16

    def test_inverse_vev_scaling(self):
        r1 = ew.ads5_ir_compactification_radius(higgs_vev_gev=246.0)
        r2 = ew.ads5_ir_compactification_radius(higgs_vev_gev=123.0)
        assert abs(r2 / r1 - 2.0) < 1e-10

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            ew.ads5_ir_compactification_radius(higgs_vev_gev=0.0)


class TestAds5KrsRcForEWScale:
    def test_canonical_value(self):
        val = ew.ads5_krs_rc_for_ew_scale()
        assert abs(val - ew.RS1_KPI_R_CANONICAL / math.pi) < 1e-10

    def test_around_12(self):
        assert 12.0 < ew.ads5_krs_rc_for_ew_scale() < 13.0

    def test_larger_vev_smaller_krs_rc(self):
        k1 = ew.ads5_krs_rc_for_ew_scale(higgs_vev_gev=246.0)
        k2 = ew.ads5_krs_rc_for_ew_scale(higgs_vev_gev=1000.0)
        assert k2 < k1


class TestAds5EWScalePlanck:
    def test_canonical_matches_observed(self):
        val = ew.ads5_ew_scale_planck(1.0, ew.ADS5_KRS_RC_CANONICAL)
        assert abs(val - ew.OBSERVED_EW_SCALE_PLANCK) < 1e-22

    def test_decreases_with_rc(self):
        v1 = ew.ads5_ew_scale_planck(1.0, 1.0)
        v2 = ew.ads5_ew_scale_planck(1.0, 2.0)
        assert v2 < v1

    def test_invalid_k_rs(self):
        with pytest.raises(ValueError):
            ew.ads5_ew_scale_planck(0.0, 1.0)

    def test_invalid_r_c(self):
        with pytest.raises(ValueError):
            ew.ads5_ew_scale_planck(1.0, 0.0)

    def test_in_unit_interval(self):
        val = ew.ads5_ew_scale_planck(1.0, 1.0)
        assert 0 < val < 1


class TestAds5RcForEWScale:
    def test_roundtrip(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        val = ew.ads5_ew_scale_planck(1.0, r_c)
        assert abs(val - ew.OBSERVED_EW_SCALE_PLANCK) < 1e-22

    def test_inverse_scaling_with_k_rs(self):
        r1 = ew.ads5_r_c_for_ew_scale(1.0)
        r2 = ew.ads5_r_c_for_ew_scale(2.0)
        assert abs(r1 / r2 - 2.0) < 1e-10

    def test_invalid_k_rs(self):
        with pytest.raises(ValueError):
            ew.ads5_r_c_for_ew_scale(0.0)


class TestAds5TowerWeightedEWMass:
    def test_canonical_close_to_observed(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        val = ew.ads5_um_tower_weighted_ew_mass(1.0, r_c, R=1.0)
        assert abs(val - ew.OBSERVED_EW_SCALE_PLANCK) / ew.OBSERVED_EW_SCALE_PLANCK < 1e-4

    def test_positive(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        assert ew.ads5_um_tower_weighted_ew_mass(1.0, r_c) > 0

    def test_scales_inverse_with_R(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        v1 = ew.ads5_um_tower_weighted_ew_mass(1.0, r_c, R=1.0)
        v2 = ew.ads5_um_tower_weighted_ew_mass(1.0, r_c, R=2.0)
        assert abs(v1 / v2 - 2.0) < 1e-6

    def test_decreases_with_larger_rc(self):
        v1 = ew.ads5_um_tower_weighted_ew_mass(1.0, 10.0)
        v2 = ew.ads5_um_tower_weighted_ew_mass(1.0, 11.0)
        assert v2 < v1

    def test_invalid_k_rs(self):
        with pytest.raises(ValueError):
            ew.ads5_um_tower_weighted_ew_mass(0.0, 1.0)

    def test_invalid_r_c(self):
        with pytest.raises(ValueError):
            ew.ads5_um_tower_weighted_ew_mass(1.0, 0.0)

    def test_small_kpi_R_higher_modes_contribute(self):
        v_small = ew.ads5_um_tower_weighted_ew_mass(1.0, 0.5, R=1.0, n_max=5)
        v_large = ew.ads5_um_tower_weighted_ew_mass(1.0, 12.23, R=1.0, n_max=5)
        # for small kπR, many modes contribute, giving a larger weighted mass
        assert v_small > v_large


class TestAds5BraidedWarpSuppression:
    def test_canonical_close_to_w1(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        rho = ew.ads5_braided_warp_suppression(1.0, r_c)
        w1 = math.exp(-1.0 / ew.K_CS_CANONICAL)
        assert abs(rho - w1) < 1e-8

    def test_between_0_and_1(self):
        r_c = ew.ads5_r_c_for_ew_scale(1.0)
        rho = ew.ads5_braided_warp_suppression(1.0, r_c)
        assert 0 < rho <= 1.0

    def test_small_kpi_R_differs_from_1(self):
        rho = ew.ads5_braided_warp_suppression(1.0, 0.01)
        assert rho < 0.99

    def test_invalid_k_rs(self):
        with pytest.raises(ValueError):
            ew.ads5_braided_warp_suppression(0.0, 1.0)


class TestAds5ConformalDimensionAtEW:
    def test_at_R_IR_n0(self):
        R_IR = ew.ADS5_IR_RADIUS_PLANCK
        val = ew.ads5_conformal_dimension_at_ew(R_IR, 1.0, 0)
        assert abs(val - 4.0) < 1e-12

    def test_at_R_IR_n1_approximately_4(self):
        R_IR = ew.ADS5_IR_RADIUS_PLANCK
        val = ew.ads5_conformal_dimension_at_ew(R_IR, 1.0, 1)
        assert abs(val - 4.0) < 1e-25

    def test_at_R_IR_n100_approximately_4(self):
        R_IR = ew.ADS5_IR_RADIUS_PLANCK
        val = ew.ads5_conformal_dimension_at_ew(R_IR, 1.0, 100)
        assert abs(val - 4.0) < 1e-20

    def test_small_R_large_delta(self):
        val = ew.ads5_conformal_dimension_at_ew(1.0, 1.0, 10)
        assert val > 10.0

    def test_always_at_least_4(self):
        for n in range(5):
            val = ew.ads5_conformal_dimension_at_ew(2.0, 1.0, n)
            assert val >= 4.0

    def test_invalid_R_IR(self):
        with pytest.raises(ValueError):
            ew.ads5_conformal_dimension_at_ew(0.0, 1.0, 1)

    def test_invalid_L(self):
        with pytest.raises(ValueError):
            ew.ads5_conformal_dimension_at_ew(1.0, 0.0, 1)

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            ew.ads5_conformal_dimension_at_ew(1.0, 1.0, -1)


# ============================================================================
# 6  §4 Higgs quartic (λ problem)
# ============================================================================

class TestKKGeometricQuartic:
    def test_canonical_value(self):
        val = ew.kk_geometric_quartic()
        expected = (12.0 / 37.0) ** 2
        assert abs(val - expected) < 1e-15

    def test_around_0p1(self):
        assert 0.09 < ew.kk_geometric_quartic() < 0.11

    def test_c_s_1(self):
        assert abs(ew.kk_geometric_quartic(c_s=1.0) - 1.0) < 1e-12

    def test_c_s_2(self):
        assert abs(ew.kk_geometric_quartic(c_s=2.0) - 4.0) < 1e-12

    def test_scales_as_c_s_squared(self):
        v1 = ew.kk_geometric_quartic(c_s=1.0)
        v2 = ew.kk_geometric_quartic(c_s=3.0)
        assert abs(v2 / v1 - 9.0) < 1e-12

    def test_independent_of_k_cs(self):
        v1 = ew.kk_geometric_quartic(k_cs=74)
        v2 = ew.kk_geometric_quartic(k_cs=100)
        assert abs(v1 - v2) < 1e-12

    def test_invalid_c_s(self):
        with pytest.raises(ValueError):
            ew.kk_geometric_quartic(c_s=0.0)

    def test_invalid_k_cs(self):
        with pytest.raises(ValueError):
            ew.kk_geometric_quartic(k_cs=0)


class TestQuarticDiscrepancyFactor:
    def test_canonical_around_1p23(self):
        val = ew.quartic_discrepancy_factor()
        assert 1.1 < val < 1.4

    def test_lambda_h_equals_lambda_kk_gives_1(self):
        lam_kk = ew.kk_geometric_quartic()
        val = ew.quartic_discrepancy_factor(lambda_h=lam_kk)
        assert abs(val - 1.0) < 1e-10

    def test_invalid_lambda_h(self):
        with pytest.raises(ValueError):
            ew.quartic_discrepancy_factor(lambda_h=0.0)


class TestHiggsMassFromCsSquared:
    def test_canonical_around_113(self):
        val = ew.higgs_mass_from_cs_squared()
        assert 110.0 < val < 116.0

    def test_formula(self):
        val = ew.higgs_mass_from_cs_squared(246.0, 12.0 / 37.0)
        expected = 246.0 * math.sqrt(2.0) * (12.0 / 37.0)
        assert abs(val - expected) < 1e-10

    def test_below_observed(self):
        assert ew.higgs_mass_from_cs_squared() < ew.HIGGS_MASS_GEV

    def test_scales_with_vev(self):
        v1 = ew.higgs_mass_from_cs_squared(higgs_vev_gev=246.0)
        v2 = ew.higgs_mass_from_cs_squared(higgs_vev_gev=492.0)
        assert abs(v2 / v1 - 2.0) < 1e-12

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            ew.higgs_mass_from_cs_squared(higgs_vev_gev=0.0)

    def test_invalid_c_s(self):
        with pytest.raises(ValueError):
            ew.higgs_mass_from_cs_squared(c_s=0.0)


class TestHiggsMassDiscrepancyGev:
    def test_canonical_around_12(self):
        val = ew.higgs_mass_discrepancy_gev()
        assert 10.0 < val < 15.0

    def test_nonnegative(self):
        assert ew.higgs_mass_discrepancy_gev() >= 0

    def test_zero_when_m_H_equals_geometric(self):
        m_geom = ew.higgs_mass_from_cs_squared()
        val = ew.higgs_mass_discrepancy_gev(higgs_mass_gev=m_geom)
        assert abs(val) < 1e-10

    def test_invalid_m_H(self):
        with pytest.raises(ValueError):
            ew.higgs_mass_discrepancy_gev(higgs_mass_gev=0.0)


class TestHiggsMassFractionalDiscrepancy:
    def test_canonical_negative(self):
        val = ew.higgs_mass_fractional_discrepancy()
        assert val < 0

    def test_canonical_around_minus_10_percent(self):
        val = ew.higgs_mass_fractional_discrepancy()
        assert -0.12 < val < -0.07

    def test_zero_when_m_H_equals_geometric(self):
        m_geom = ew.higgs_mass_from_cs_squared()
        val = ew.higgs_mass_fractional_discrepancy(higgs_mass_gev=m_geom)
        assert abs(val) < 1e-10

    def test_invalid_m_H(self):
        with pytest.raises(ValueError):
            ew.higgs_mass_fractional_discrepancy(higgs_mass_gev=0.0)


class TestVacuumStabilityCondition:
    def test_canonical_stable(self):
        assert ew.vacuum_stability_condition() is True

    def test_positive_lambda_stable(self):
        assert ew.vacuum_stability_condition(0.001) is True

    def test_zero_lambda_unstable(self):
        assert ew.vacuum_stability_condition(0.0) is False

    def test_negative_lambda_unstable(self):
        assert ew.vacuum_stability_condition(-0.01) is False

    def test_type_error(self):
        with pytest.raises(TypeError):
            ew.vacuum_stability_condition("x")


class TestKKVacuumStabilityGeometric:
    def test_canonical_always_true(self):
        assert ew.kk_vacuum_stability_geometric() is True

    def test_any_positive_c_s(self):
        for c_s in [0.01, 0.1, 1.0, 10.0]:
            assert ew.kk_vacuum_stability_geometric(c_s) is True

    def test_invalid_c_s(self):
        with pytest.raises(ValueError):
            ew.kk_vacuum_stability_geometric(c_s=0.0)


# ============================================================================
# 7  §5 Yukawa hierarchy (flavor puzzle)
# ============================================================================

class TestYukawaGeometricMassRatio:
    def test_n0_is_1(self):
        assert abs(ew.yukawa_geometric_mass_ratio(0) - 1.0) < 1e-15

    def test_n1_canonical(self):
        val = ew.yukawa_geometric_mass_ratio(1, n_w=5)
        assert abs(val - math.sqrt(6.0 / 5.0)) < 1e-12

    def test_n2_canonical(self):
        val = ew.yukawa_geometric_mass_ratio(2, n_w=5)
        assert abs(val - math.sqrt(9.0 / 5.0)) < 1e-12

    def test_monotone_increasing(self):
        v0 = ew.yukawa_geometric_mass_ratio(0)
        v1 = ew.yukawa_geometric_mass_ratio(1)
        v2 = ew.yukawa_geometric_mass_ratio(2)
        assert v0 < v1 < v2

    def test_much_less_than_observed(self):
        ratio = ew.yukawa_geometric_mass_ratio(1)
        assert ratio < ew.LEPTON_MASS_RATIO_MU_E / 10

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            ew.yukawa_geometric_mass_ratio(-1)

    def test_invalid_n_w(self):
        with pytest.raises(ValueError):
            ew.yukawa_geometric_mass_ratio(1, n_w=0)


class TestObservedLeptonMassRatio:
    def test_n0_is_1(self):
        assert ew.observed_lepton_mass_ratio(0) == 1.0

    def test_n1_muon_electron(self):
        expected = ew.MUON_MASS_GEV / ew.ELECTRON_MASS_GEV
        assert abs(ew.observed_lepton_mass_ratio(1) - expected) < 1e-10

    def test_n2_tau_electron(self):
        expected = ew.TAU_MASS_GEV / ew.ELECTRON_MASS_GEV
        assert abs(ew.observed_lepton_mass_ratio(2) - expected) < 1e-6

    def test_n1_around_207(self):
        assert 200.0 < ew.observed_lepton_mass_ratio(1) < 210.0

    def test_n2_around_3477(self):
        assert 3400.0 < ew.observed_lepton_mass_ratio(2) < 3550.0

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            ew.observed_lepton_mass_ratio(3)


class TestYukawaDiscrepancyLog10:
    def test_n0_is_zero(self):
        assert ew.yukawa_discrepancy_log10(0) == 0.0

    def test_n1_negative(self):
        assert ew.yukawa_discrepancy_log10(1) < 0

    def test_n2_more_negative_than_n1(self):
        d1 = ew.yukawa_discrepancy_log10(1)
        d2 = ew.yukawa_discrepancy_log10(2)
        assert d2 < d1

    def test_n1_around_minus_2(self):
        d = ew.yukawa_discrepancy_log10(1)
        assert -3.0 < d < -1.0

    def test_n2_around_minus_3(self):
        d = ew.yukawa_discrepancy_log10(2)
        assert -4.0 < d < -2.0


class TestRS1YukawaOverlap:
    def test_n0_is_1(self):
        assert abs(ew.rs1_yukawa_overlap(0) - 1.0) < 1e-15

    def test_decays_with_generation(self):
        v0 = ew.rs1_yukawa_overlap(0)
        v1 = ew.rs1_yukawa_overlap(1)
        v2 = ew.rs1_yukawa_overlap(2)
        assert v0 > v1 > v2

    def test_geometric_progression(self):
        v1 = ew.rs1_yukawa_overlap(1, kpi_R=10.0, delta_c=0.1)
        v2 = ew.rs1_yukawa_overlap(2, kpi_R=10.0, delta_c=0.1)
        assert abs(v2 / v1 - v1) < 1e-10  # ratio is constant (geometric)

    def test_canonical_delta_c_01(self):
        val = ew.rs1_yukawa_overlap(1, kpi_R=ew.RS1_KPI_R_CANONICAL, delta_c=0.1)
        expected = math.exp(-0.1 * ew.RS1_KPI_R_CANONICAL)
        assert abs(val - expected) < 1e-12

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            ew.rs1_yukawa_overlap(-1)

    def test_invalid_kpi_R(self):
        with pytest.raises(ValueError):
            ew.rs1_yukawa_overlap(1, kpi_R=-1.0)

    def test_invalid_delta_c(self):
        with pytest.raises(ValueError):
            ew.rs1_yukawa_overlap(1, delta_c=-0.1)


class TestRS1YukawaMassRatio:
    def test_n0_is_1(self):
        assert abs(ew.rs1_yukawa_mass_ratio(0) - 1.0) < 1e-15

    def test_reciprocal_of_overlap(self):
        r1 = ew.rs1_yukawa_mass_ratio(1)
        o1 = ew.rs1_yukawa_overlap(1)
        assert abs(r1 - 1.0 / o1) < 1e-12

    def test_canonical_n2_around_2000(self):
        val = ew.rs1_yukawa_mass_ratio(2, delta_c=0.1)
        assert val > 1000.0


class TestRS1DeltaCForRatio:
    def test_roundtrip_tau_electron(self):
        tau_e = ew.LEPTON_MASS_RATIO_TAU_E
        delta_c = ew.rs1_delta_c_for_ratio(tau_e, n_gen=2)
        ratio_back = ew.rs1_yukawa_mass_ratio(2, delta_c=delta_c)
        assert abs(ratio_back / tau_e - 1.0) < 1e-6

    def test_canonical_tau_electron_around_0p1(self):
        tau_e = ew.LEPTON_MASS_RATIO_TAU_E
        delta_c = ew.rs1_delta_c_for_ratio(tau_e, n_gen=2)
        assert 0.08 < delta_c < 0.12

    def test_invalid_ratio(self):
        with pytest.raises(ValueError):
            ew.rs1_delta_c_for_ratio(0.5, n_gen=1)

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            ew.rs1_delta_c_for_ratio(10.0, n_gen=0)

    def test_invalid_kpi_R(self):
        with pytest.raises(ValueError):
            ew.rs1_delta_c_for_ratio(10.0, n_gen=1, kpi_R=0.0)


class TestLeptonMassFromGeometry:
    def test_n0_returns_reference(self):
        val = ew.lepton_mass_from_geometry(0, 0.511e-3)
        assert abs(val - 0.511e-3) < 1e-20

    def test_n1_scaled(self):
        val = ew.lepton_mass_from_geometry(1, 0.511e-3)
        expected = 0.511e-3 * math.sqrt(6.0 / 5.0)
        assert abs(val - expected) < 1e-18

    def test_invalid_reference_mass(self):
        with pytest.raises(ValueError):
            ew.lepton_mass_from_geometry(0, -1.0)


# ============================================================================
# 8  §6 (5,7) braid topology and warp factor
# ============================================================================

class TestBraidTopologicalKpiR:
    def test_canonical_12pi(self):
        val = ew.braid_topological_kpi_R()
        assert abs(val - 12.0 * math.pi) < 1e-12

    def test_around_37p7(self):
        val = ew.braid_topological_kpi_R()
        assert 37.5 < val < 38.0

    def test_scales_with_sum(self):
        v1 = ew.braid_topological_kpi_R(n1=1, n2=1)
        v2 = ew.braid_topological_kpi_R(n1=2, n2=2)
        assert abs(v2 / v1 - 2.0) < 1e-12

    def test_equals_constant(self):
        assert abs(ew.braid_topological_kpi_R() - ew.BRAID_KPI_R_TOPOLOGICAL) < 1e-12

    def test_invalid_n1(self):
        with pytest.raises(ValueError):
            ew.braid_topological_kpi_R(n1=0)

    def test_invalid_n2(self):
        with pytest.raises(ValueError):
            ew.braid_topological_kpi_R(n2=0)


class TestBraidEWVevGev:
    def test_canonical_around_531(self):
        val = ew.braid_ew_vev_gev()
        # Should be M_Pl * exp(-12π)
        expected = ew.PLANCK_MASS_GEV * math.exp(-12.0 * math.pi)
        assert abs(val / expected - 1.0) < 1e-10

    def test_larger_than_observed(self):
        # Topological prediction overshoots 246 GeV
        assert ew.braid_ew_vev_gev() > 246.0

    def test_ratio_to_observed_around_2(self):
        ratio = ew.braid_ew_vev_gev() / 246.0
        assert 1.5 < ratio < 3.5

    def test_scales_with_m_planck(self):
        v1 = ew.braid_ew_vev_gev(m_planck_gev=1e10)
        v2 = ew.braid_ew_vev_gev(m_planck_gev=2e10)
        assert abs(v2 / v1 - 2.0) < 1e-10

    def test_equals_constant(self):
        assert abs(ew.braid_ew_vev_gev() - ew.BRAID_EW_VEV_GEV_TOPOLOGICAL) < 1e-5

    def test_invalid_m_planck(self):
        with pytest.raises(ValueError):
            ew.braid_ew_vev_gev(m_planck_gev=0.0)


class TestBraidHierarchyDiscrepancyFraction:
    def test_canonical_small_negative(self):
        val = ew.braid_hierarchy_discrepancy_fraction()
        assert -0.05 < val < 0.0

    def test_canonical_around_minus_2_percent(self):
        val = ew.braid_hierarchy_discrepancy_fraction()
        assert -0.025 < val < -0.015

    def test_sign_is_negative(self):
        # Braid under-predicts kπR → negative fraction
        assert ew.braid_hierarchy_discrepancy_fraction() < 0

    def test_close_to_unity(self):
        # |discrepancy| < 5%
        assert abs(ew.braid_hierarchy_discrepancy_fraction()) < 0.05


class TestBraidLinkingNumber:
    def test_canonical_35(self):
        assert ew.braid_linking_number() == 35

    def test_n1_n2_product(self):
        assert ew.braid_linking_number(3, 7) == 21

    def test_commutative(self):
        assert ew.braid_linking_number(5, 7) == ew.braid_linking_number(7, 5)

    def test_invalid_n1(self):
        with pytest.raises(ValueError):
            ew.braid_linking_number(n1=0)

    def test_invalid_n2(self):
        with pytest.raises(ValueError):
            ew.braid_linking_number(n2=0)


class TestBraidYukawaFromLinking:
    def test_n0_is_1(self):
        assert abs(ew.braid_yukawa_from_linking(0) - 1.0) < 1e-15

    def test_n1_canonical(self):
        val = ew.braid_yukawa_from_linking(1)
        expected = math.exp(-math.pi * 35.0 / 74.0)
        assert abs(val - expected) < 1e-12

    def test_n2_canonical(self):
        val = ew.braid_yukawa_from_linking(2)
        expected = math.exp(-2.0 * math.pi * 35.0 / 74.0)
        assert abs(val - expected) < 1e-12

    def test_decays_with_generation(self):
        v0 = ew.braid_yukawa_from_linking(0)
        v1 = ew.braid_yukawa_from_linking(1)
        v2 = ew.braid_yukawa_from_linking(2)
        assert v0 > v1 > v2

    def test_geometric_progression(self):
        v1 = ew.braid_yukawa_from_linking(1)
        v2 = ew.braid_yukawa_from_linking(2)
        assert abs(v2 / v1 - v1) < 1e-12

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            ew.braid_yukawa_from_linking(-1)

    def test_invalid_n1(self):
        with pytest.raises(ValueError):
            ew.braid_yukawa_from_linking(1, n1=0)

    def test_invalid_k_cs(self):
        with pytest.raises(ValueError):
            ew.braid_yukawa_from_linking(1, k_cs=0)


class TestBraidYukawaMassRatio:
    def test_n0_is_1(self):
        assert abs(ew.braid_yukawa_mass_ratio(0) - 1.0) < 1e-15

    def test_n1_around_4(self):
        val = ew.braid_yukawa_mass_ratio(1)
        assert 3.0 < val < 6.0

    def test_n2_around_19(self):
        val = ew.braid_yukawa_mass_ratio(2)
        assert 10.0 < val < 30.0

    def test_reciprocal_of_overlap(self):
        r1 = ew.braid_yukawa_mass_ratio(1)
        o1 = ew.braid_yukawa_from_linking(1)
        assert abs(r1 * o1 - 1.0) < 1e-12

    def test_greater_than_1(self):
        for n in range(3):
            assert ew.braid_yukawa_mass_ratio(n) >= 1.0


class TestBraidYukawaDiscrepancyLog10:
    def test_n0_is_zero(self):
        assert ew.braid_yukawa_discrepancy_log10(0) == 0.0

    def test_n1_negative_but_better_than_kk(self):
        d_braid = ew.braid_yukawa_discrepancy_log10(1)
        d_kk = ew.yukawa_discrepancy_log10(1)
        assert d_braid < 0
        # Braid should do better (less negative) than pure KK
        assert d_braid > d_kk

    def test_n2_negative(self):
        assert ew.braid_yukawa_discrepancy_log10(2) < 0

    def test_n2_better_than_kk(self):
        d_braid = ew.braid_yukawa_discrepancy_log10(2)
        d_kk = ew.yukawa_discrepancy_log10(2)
        assert d_braid > d_kk  # braid is closer to observed


# ============================================================================
# 9  HierarchyComparison dataclass
# ============================================================================

class TestHierarchyComparison:
    @pytest.fixture
    def hc(self):
        return ew.compare_hierarchy_mechanisms()

    def test_all_gaps_require_fine_tuning(self, hc):
        assert hc.mechanism1_requires_fine_tuning is True
        assert hc.mechanism2_requires_fine_tuning is True
        assert hc.mechanism3_requires_fine_tuning is True

    def test_no_mechanism_closes_gap(self, hc):
        assert hc.any_mechanism_closed_gap is False

    def test_um_ew_scale(self, hc):
        assert abs(hc.um_ew_scale_planck - ew.UM_EW_SCALE_PLANCK) < 1e-12

    def test_observed_ew_scale(self, hc):
        assert abs(hc.observed_ew_scale_planck - ew.OBSERVED_EW_SCALE_PLANCK) < 1e-30

    def test_gap_log10_positive(self, hc):
        assert hc.hierarchy_gap_log10 > 0

    def test_rs1_kpi_R_needed(self, hc):
        assert abs(hc.rs1_kpi_R_needed - ew.RS1_KPI_R_CANONICAL) < 1e-10

    def test_rs1_warp_factor_canonical_equals_observed_ew(self, hc):
        assert abs(hc.rs1_warp_factor_canonical - ew.OBSERVED_EW_SCALE_PLANCK) < 1e-22

    def test_ec_kappa_T_needed_small(self, hc):
        assert hc.ec_kappa_T_needed < 1e-30

    def test_ec_higgs_vev_at_kappa1_large(self, hc):
        assert hc.ec_higgs_vev_gev_at_kappa1 > 1e14

    def test_ads5_conformal_dim_n1_near_4(self, hc):
        assert abs(hc.ads5_conformal_dim_n1_at_ew - 4.0) < 1e-20


# ============================================================================
# 10  compare_hierarchy_mechanisms driver
# ============================================================================

class TestCompareHierarchyMechanisms:
    def test_returns_hierarchy_comparison(self):
        result = ew.compare_hierarchy_mechanisms()
        assert isinstance(result, ew.HierarchyComparison)

    def test_reproducible(self):
        r1 = ew.compare_hierarchy_mechanisms()
        r2 = ew.compare_hierarchy_mechanisms()
        assert r1.hierarchy_gap_log10 == r2.hierarchy_gap_log10

    def test_custom_higgs_vev_changes_gap(self):
        r1 = ew.compare_hierarchy_mechanisms(higgs_vev_gev=246.0)
        r2 = ew.compare_hierarchy_mechanisms(higgs_vev_gev=500.0)
        assert r2.hierarchy_gap_log10 < r1.hierarchy_gap_log10

    def test_custom_k_rs_changes_ads5_fields(self):
        r1 = ew.compare_hierarchy_mechanisms(k_rs=1.0)
        r2 = ew.compare_hierarchy_mechanisms(k_rs=2.0)
        assert abs(r1.ads5_krs_rc_needed - r2.ads5_krs_rc_needed) < 1e-12
        # krs_rc_needed does NOT depend on k_rs (it's kπR/π regardless of k)

    def test_tower_ew_mass_close_to_observed(self):
        r = ew.compare_hierarchy_mechanisms()
        rel_err = abs(r.ads5_tower_ew_mass_planck - ew.OBSERVED_EW_SCALE_PLANCK)
        rel_err /= ew.OBSERVED_EW_SCALE_PLANCK
        assert rel_err < 1e-4

    def test_braid_suppression_in_unit_interval(self):
        r = ew.compare_hierarchy_mechanisms()
        assert 0 < r.ads5_braided_suppression_canonical <= 1.0

    def test_gw_kpi_R_equals_rs1(self):
        r = ew.compare_hierarchy_mechanisms()
        assert abs(r.gw_phi_min_kpi_R - r.rs1_kpi_R_needed) < 1e-6

    def test_n_max_does_not_affect_canonical_result_much(self):
        r1 = ew.compare_hierarchy_mechanisms(n_max=10)
        r2 = ew.compare_hierarchy_mechanisms(n_max=40)
        assert abs(r1.ads5_tower_ew_mass_planck / r2.ads5_tower_ew_mass_planck - 1.0) < 1e-6
