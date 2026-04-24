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


# ===========================================================================
# §4 extension — Braid-Warp Correspondence
# ===========================================================================

class TestBraidGWResidualTension:
    """braid_gw_residual_tension: T_GW = kπR_obs − kπR_topo ≈ 0.744."""

    def test_canonical_positive(self):
        assert ew.braid_gw_residual_tension() > 0.0

    def test_canonical_value(self):
        t = ew.braid_gw_residual_tension()
        assert abs(t - 0.7443) < 1e-3

    def test_equals_kpiR_diff(self):
        obs  = ew.rs1_kpi_R_for_ew_scale()
        topo = ew.braid_topological_kpi_R()
        assert abs(ew.braid_gw_residual_tension() - (obs - topo)) < 1e-10

    def test_smaller_for_larger_winding_sum(self):
        # Larger n1+n2 → topo closer to obs → smaller residual
        t57  = ew.braid_gw_residual_tension(5, 7)
        t610 = ew.braid_gw_residual_tension(6, 10)   # sum=16 > 12 → smaller gap
        assert t610 < t57

    def test_raises_on_zero_n(self):
        with pytest.raises(ValueError):
            ew.braid_gw_residual_tension(0, 7)

    def test_custom_planck(self):
        t = ew.braid_gw_residual_tension(m_planck_gev=1.0e19)
        assert t > 0.0


class TestBraidGWTensionFraction:
    """braid_gw_tension_fraction ≈ 0.0194 (1.94%)."""

    def test_canonical_fraction(self):
        f = ew.braid_gw_tension_fraction()
        assert abs(f - 0.0194) < 5e-4

    def test_between_zero_and_one(self):
        f = ew.braid_gw_tension_fraction()
        assert 0.0 < f < 1.0

    def test_complement_of_topological_coverage(self):
        cov = ew.braid_topological_kpi_R() / ew.rs1_kpi_R_for_ew_scale()
        frac = ew.braid_gw_tension_fraction()
        assert abs(cov + frac - 1.0) < 1e-10


class TestBraidTwistDensity:
    """braid_twist_density: k_rs = (n1+n2)/r_c."""

    def test_canonical_close_to_one(self):
        # k_rs = 12 / ADS5_KRS_RC_CANONICAL ≈ 0.98
        k = ew.braid_twist_density()
        assert 0.97 < k < 1.00

    def test_proportional_to_crossing_sum(self):
        k1 = ew.braid_twist_density(5, 7, r_c=10.0)
        k2 = ew.braid_twist_density(6, 7, r_c=10.0)   # sum=13 vs 12
        assert abs(k2 / k1 - 13 / 12) < 1e-10

    def test_inversely_proportional_to_rc(self):
        k1 = ew.braid_twist_density(5, 7, r_c=5.0)
        k2 = ew.braid_twist_density(5, 7, r_c=10.0)
        assert abs(k1 / k2 - 2.0) < 1e-10

    def test_raises_on_nonpositive_rc(self):
        with pytest.raises(ValueError):
            ew.braid_twist_density(5, 7, r_c=0.0)

    def test_raises_on_zero_n(self):
        with pytest.raises(ValueError):
            ew.braid_twist_density(0, 7)


class TestBraidEquilibriumRadius:
    """braid_equilibrium_radius: R_topo = π(n1+n2)/sqrt(-λ5d/6)."""

    def test_canonical_equals_12pi(self):
        # λ5d=-6 → k_rs=1 → R_topo=12π
        r = ew.braid_equilibrium_radius(5, 7, lambda5d=-6.0)
        assert abs(r - 12.0 * math.pi) < 1e-8

    def test_positive(self):
        assert ew.braid_equilibrium_radius() > 0.0

    def test_scales_with_crossing_sum(self):
        r57 = ew.braid_equilibrium_radius(5, 7, lambda5d=-6.0)
        r69 = ew.braid_equilibrium_radius(6, 9, lambda5d=-6.0)   # sum=15
        assert abs(r69 / r57 - 15.0 / 12.0) < 1e-10

    def test_raises_on_nonnegative_lambda(self):
        with pytest.raises(ValueError):
            ew.braid_equilibrium_radius(lambda5d=0.0)
        with pytest.raises(ValueError):
            ew.braid_equilibrium_radius(lambda5d=1.0)

    def test_stronger_ads_gives_smaller_radius(self):
        r1 = ew.braid_equilibrium_radius(lambda5d=-6.0)
        r2 = ew.braid_equilibrium_radius(lambda5d=-24.0)  # k_rs doubles
        assert abs(r2 / r1 - 0.5) < 1e-10


# ===========================================================================
# §5 extension — Strand Localisation Yukawa
# ===========================================================================

class TestBraidStrandYukawa:
    """braid_strand_yukawa: y_n = exp(-n × n2 × kπR / k_cs)."""

    def test_generation0_is_one(self):
        assert ew.braid_strand_yukawa(0) == 1.0

    def test_decreasing_with_generation(self):
        y0 = ew.braid_strand_yukawa(0)
        y1 = ew.braid_strand_yukawa(1)
        y2 = ew.braid_strand_yukawa(2)
        assert y0 > y1 > y2 > 0.0

    def test_canonical_gen1_value(self):
        # exp(-7 × 38.443 / 74) = exp(-3.634)
        expected = math.exp(-7 * ew.RS1_KPI_R_CANONICAL / ew.K_CS_CANONICAL)
        assert abs(ew.braid_strand_yukawa(1) - expected) < 1e-12

    def test_canonical_gen1_approx(self):
        assert abs(ew.braid_strand_yukawa(1) - 0.0263) < 5e-4

    def test_exponential_in_n_gen(self):
        y1 = ew.braid_strand_yukawa(1)
        y2 = ew.braid_strand_yukawa(2)
        assert abs(y2 - y1 ** 2) < 1e-15   # geometric sequence

    def test_raises_negative_n_gen(self):
        with pytest.raises(ValueError):
            ew.braid_strand_yukawa(-1)

    def test_zero_kpiR_gives_one(self):
        assert ew.braid_strand_yukawa(2, kpi_R=0.0) == 1.0

    def test_larger_n2_gives_smaller_yukawa(self):
        y_n2_7 = ew.braid_strand_yukawa(1, n2=7)
        y_n2_9 = ew.braid_strand_yukawa(1, n2=9)
        assert y_n2_9 < y_n2_7


class TestBraidStrandMassRatio:
    """braid_strand_mass_ratio = 1 / braid_strand_yukawa."""

    def test_generation0_is_one(self):
        assert ew.braid_strand_mass_ratio(0) == 1.0

    def test_canonical_gen1(self):
        assert abs(ew.braid_strand_mass_ratio(1) - 37.96) < 0.5

    def test_canonical_gen2(self):
        assert abs(ew.braid_strand_mass_ratio(2) - 1441) < 5

    def test_ratio_is_reciprocal_of_yukawa(self):
        for n in range(3):
            y = ew.braid_strand_yukawa(n)
            r = ew.braid_strand_mass_ratio(n)
            assert abs(r * y - 1.0) < 1e-10

    def test_increasing_with_generation(self):
        r0 = ew.braid_strand_mass_ratio(0)
        r1 = ew.braid_strand_mass_ratio(1)
        r2 = ew.braid_strand_mass_ratio(2)
        assert r0 < r1 < r2


class TestBraidStrandDiscrepancyLog10:
    """braid_strand_discrepancy_log10: log10(strand_ratio/observed)."""

    def test_generation0_zero(self):
        assert ew.braid_strand_discrepancy_log10(0) == 0.0

    def test_gen1_smaller_than_basic_linking(self):
        # Strand model is better (smaller absolute discrepancy) than basic model
        disc_strand = abs(ew.braid_strand_discrepancy_log10(1))
        disc_basic  = abs(ew.braid_yukawa_discrepancy_log10(1))
        assert disc_strand < disc_basic

    def test_gen2_smaller_than_basic_linking(self):
        disc_strand = abs(ew.braid_strand_discrepancy_log10(2))
        disc_basic  = abs(ew.braid_yukawa_discrepancy_log10(2))
        assert disc_strand < disc_basic

    def test_canonical_gen1_within_one_order(self):
        # |log10 discrepancy| < 1 for gen 1 in strand model
        assert abs(ew.braid_strand_discrepancy_log10(1)) < 1.0

    def test_canonical_gen2_within_one_order(self):
        assert abs(ew.braid_strand_discrepancy_log10(2)) < 1.0


class TestBraidAlexanderPolynomial:
    """braid_alexander_polynomial: Δ_{n1,n2}(t)."""

    def test_at_t_equals_one(self):
        assert ew.braid_alexander_polynomial(1.0) == 1.0

    def test_at_t_near_one(self):
        assert abs(ew.braid_alexander_polynomial(1.0 + 1e-12) - 1.0) < 1e-6

    def test_canonical_at_0743(self):
        assert abs(ew.braid_alexander_polynomial(0.743) - 0.3797) < 1e-3

    def test_positive_for_real_t(self):
        for t in [0.1, 0.5, 0.9, 1.5, 2.0]:
            val = ew.braid_alexander_polynomial(t)
            assert isinstance(val, float)

    def test_raises_nonpositive_t(self):
        with pytest.raises(ValueError):
            ew.braid_alexander_polynomial(0.0)
        with pytest.raises(ValueError):
            ew.braid_alexander_polynomial(-1.0)

    def test_different_knots(self):
        # T(3,5) and T(5,7) should give different values at same t
        v57 = ew.braid_alexander_polynomial(0.8, n1=5, n2=7)
        v35 = ew.braid_alexander_polynomial(0.8, n1=3, n2=5)
        assert abs(v57 - v35) > 1e-4

    def test_symmetric_formula(self):
        # Δ_{p,q} = Δ_{q,p} (knot is the same)
        v57 = ew.braid_alexander_polynomial(0.6, n1=5, n2=7)
        v75 = ew.braid_alexander_polynomial(0.6, n1=7, n2=5)
        assert abs(v57 - v75) < 1e-10


# ===========================================================================
# §6 extension — Higgs Sector: Geometric Quartic and Top-Loop Correction
# ===========================================================================

class TestBraidQuarticFromWindingRatio:
    """braid_quartic_from_winding_ratio: λ = (n1/n2)² / (2π)."""

    def test_canonical_value(self):
        expected = (5 / 7) ** 2 / (2 * math.pi)
        assert abs(ew.braid_quartic_from_winding_ratio() - expected) < 1e-12

    def test_canonical_approx(self):
        assert abs(ew.braid_quartic_from_winding_ratio() - 0.0812) < 1e-4

    def test_positive(self):
        assert ew.braid_quartic_from_winding_ratio() > 0.0

    def test_less_than_cs_squared(self):
        # λ_winding < c_s² — worse prediction
        assert ew.braid_quartic_from_winding_ratio() < ew.C_S_CANONICAL ** 2

    def test_raises_zero_n(self):
        with pytest.raises(ValueError):
            ew.braid_quartic_from_winding_ratio(n1=0, n2=7)

    def test_scaling_with_n1(self):
        lam5 = ew.braid_quartic_from_winding_ratio(n1=5, n2=7)
        lam6 = ew.braid_quartic_from_winding_ratio(n1=6, n2=7)
        assert abs(lam6 / lam5 - (6 / 5) ** 2) < 1e-10


class TestBraidHiggsMassFromWindingRatio:
    """braid_higgs_mass_from_winding_ratio: correct SM convention √(2λ)."""

    def test_canonical_value(self):
        m = ew.braid_higgs_mass_from_winding_ratio()
        assert abs(m - 99.14) < 0.1

    def test_correct_convention(self):
        lam = ew.braid_quartic_from_winding_ratio()
        expected = ew.HIGGS_VEV_GEV * math.sqrt(2.0 * lam)
        assert abs(ew.braid_higgs_mass_from_winding_ratio() - expected) < 1e-10

    def test_wrong_gemini_convention_different(self):
        lam = ew.braid_quartic_from_winding_ratio()
        gemini_wrong = ew.HIGGS_VEV_GEV * math.sqrt(lam / 2.0)  # ≈ 49.6 GeV
        correct = ew.braid_higgs_mass_from_winding_ratio()
        # correct is 2× larger than Gemini's wrong formula
        assert abs(correct / gemini_wrong - 2.0) < 1e-8

    def test_less_accurate_than_cs_sq(self):
        obs = ew.HIGGS_MASS_GEV
        err_winding = abs(ew.braid_higgs_mass_from_winding_ratio() - obs)
        err_cs = abs(ew.higgs_mass_from_cs_squared() - obs)
        assert err_winding > err_cs

    def test_positive(self):
        assert ew.braid_higgs_mass_from_winding_ratio() > 0.0


class TestBraidQuarticFromStiffness:
    """braid_quartic_from_stiffness: λ_stiff = c_s²(1 + n1n2/k_cs²)."""

    def test_canonical_value(self):
        lam = ew.braid_quartic_from_stiffness()
        assert abs(lam - 0.10586) < 1e-4

    def test_greater_than_cs_squared(self):
        assert ew.braid_quartic_from_stiffness() > ew.C_S_CANONICAL ** 2

    def test_cross_link_correction_positive(self):
        lam_base = ew.C_S_CANONICAL ** 2
        lam_stiff = ew.braid_quartic_from_stiffness()
        assert lam_stiff > lam_base

    def test_correction_small(self):
        # Cross-link correction < 1% (n1n2/k_cs² = 35/5476 ≈ 0.64%)
        ratio = ew.braid_quartic_from_stiffness() / ew.C_S_CANONICAL ** 2
        assert 1.0 < ratio < 1.01

    def test_raises_zero_kcs(self):
        with pytest.raises(ValueError):
            ew.braid_quartic_from_stiffness(k_cs=0)


class TestBraidHiggsMassVibrational:
    """braid_higgs_mass_vibrational ≈ 113.2 GeV."""

    def test_canonical_value(self):
        m = ew.braid_higgs_mass_vibrational()
        assert abs(m - 113.19) < 0.1

    def test_greater_than_winding_ratio_mass(self):
        assert ew.braid_higgs_mass_vibrational() > ew.braid_higgs_mass_from_winding_ratio()

    def test_greater_than_cs_sq_mass(self):
        assert ew.braid_higgs_mass_vibrational() > ew.higgs_mass_from_cs_squared()

    def test_still_below_observed(self):
        assert ew.braid_higgs_mass_vibrational() < ew.HIGGS_MASS_GEV

    def test_positive(self):
        assert ew.braid_higgs_mass_vibrational() > 0.0

    def test_consistent_with_stiffness_lambda(self):
        m_expected = ew.HIGGS_VEV_GEV * math.sqrt(2.0 * ew.braid_quartic_from_stiffness())
        assert abs(ew.braid_higgs_mass_vibrational() - m_expected) < 1e-8


class TestBraidHiggsMassTopCorrected:
    """braid_higgs_mass_top_corrected: one-loop top-quark fix."""

    def test_310_gev_cutoff(self):
        m = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=310.0)
        assert abs(m - 123.88) < 0.2

    def test_greater_than_tree_level(self):
        m_tree = ew.higgs_mass_from_cs_squared()
        m_1loop = ew.braid_higgs_mass_top_corrected()
        assert m_1loop > m_tree

    def test_increases_with_cutoff(self):
        m1 = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=250.0)
        m2 = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=400.0)
        assert m2 > m1

    def test_at_canonical_cutoff_near_125(self):
        # Λ_KK = braid_kk_cutoff_for_higgs_mass() → m_H = 125.09
        cutoff = ew.braid_kk_cutoff_for_higgs_mass()
        m = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=cutoff)
        assert abs(m - ew.HIGGS_MASS_GEV) < 0.01

    def test_raises_cutoff_below_top(self):
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=100.0)

    def test_raises_nonpositive_vev(self):
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_top_corrected(higgs_vev_gev=0.0)

    def test_physical_range(self):
        # Mass must exceed tree-level for any Λ > m_top;
        # upper bound grows with Λ (no hard cap beyond tree-level)
        for cutoff in [210.0, 310.0, 500.0, 1000.0]:
            m = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=cutoff)
            assert m > ew.higgs_mass_from_cs_squared()   # always above tree-level
        # Specifically: Λ=310 GeV gives < 125 GeV; Λ=exact cutoff gives =125.09 GeV
        assert ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=310.0) < 125.5


class TestBraidKKCutoffForHiggsMass:
    """braid_kk_cutoff_for_higgs_mass ≈ 332 GeV — falsifiable prediction."""

    def test_canonical_value(self):
        cutoff = ew.braid_kk_cutoff_for_higgs_mass()
        assert abs(cutoff - 331.5) < 1.0

    def test_above_top_mass(self):
        assert ew.braid_kk_cutoff_for_higgs_mass() > ew.TOP_MASS_GEV

    def test_below_tev(self):
        assert ew.braid_kk_cutoff_for_higgs_mass() < 1000.0

    def test_round_trip(self):
        """Using the predicted cutoff must reproduce the observed Higgs mass."""
        cutoff = ew.braid_kk_cutoff_for_higgs_mass()
        m_back = ew.braid_higgs_mass_top_corrected(lambda_cutoff_gev=cutoff)
        assert abs(m_back - ew.HIGGS_MASS_GEV) < 0.01

    def test_raises_on_tree_exceeds_observed(self):
        """If tree-level m_H ≥ observed m_H, top correction cannot close gap."""
        # Make c_s very large so tree-level overshoots
        with pytest.raises(ValueError):
            ew.braid_kk_cutoff_for_higgs_mass(c_s=1.0)   # m_H_tree > 125.09

    def test_raises_nonpositive_inputs(self):
        with pytest.raises(ValueError):
            ew.braid_kk_cutoff_for_higgs_mass(higgs_vev_gev=0.0)


class TestBraidQuarticComparison:
    """braid_quartic_comparison: complete hierarchy summary dict."""

    def setup_method(self):
        self.cmp = ew.braid_quartic_comparison()

    def test_returns_dict(self):
        assert isinstance(self.cmp, dict)

    def test_all_keys_present(self):
        required = {
            "lambda_observed", "lambda_winding_ratio", "lambda_cs_sq",
            "lambda_stiffness", "m_H_observed", "m_H_winding_ratio",
            "m_H_gemini_wrong", "m_H_tree_cs_sq", "m_H_vibrational",
            "m_H_top_corrected", "lambda_kk_cutoff_gev", "best_error_pct",
        }
        assert required.issubset(self.cmp.keys())

    def test_lambda_ordering(self):
        assert (self.cmp["lambda_winding_ratio"]
                < self.cmp["lambda_cs_sq"]
                < self.cmp["lambda_stiffness"]
                < self.cmp["lambda_observed"])

    def test_mass_ordering(self):
        assert (self.cmp["m_H_gemini_wrong"]         # wrong formula: ~49.6
                < self.cmp["m_H_winding_ratio"]       # correct: ~99.1
                < self.cmp["m_H_tree_cs_sq"]          # ~112.8
                < self.cmp["m_H_vibrational"]          # ~113.2
                < self.cmp["m_H_top_corrected"]        # ~123.9
                < self.cmp["m_H_observed"])            # 125.09

    def test_gemini_wrong_is_half_correct(self):
        # Gemini's wrong formula uses √(λ/2) instead of √(2λ) — factor of 2
        ratio = self.cmp["m_H_winding_ratio"] / self.cmp["m_H_gemini_wrong"]
        assert abs(ratio - 2.0) < 1e-8

    def test_best_error_pct_small(self):
        # Top-corrected should be within 1% of 125.09 GeV
        assert abs(self.cmp["best_error_pct"]) < 1.5

    def test_kk_cutoff_below_tev(self):
        assert self.cmp["lambda_kk_cutoff_gev"] < 1000.0

    def test_kk_cutoff_above_top_mass(self):
        assert self.cmp["lambda_kk_cutoff_gev"] > ew.TOP_MASS_GEV

    def test_top_corrected_close_to_observed(self):
        err = abs(self.cmp["m_H_top_corrected"] - self.cmp["m_H_observed"])
        assert err < 2.0    # within 2 GeV at Λ=310 GeV


# ===========================================================================
# Cross-mechanism consistency checks
# ===========================================================================

class TestCrossMechanismConsistency:
    """Verify the three mechanisms are self-consistent and correctly ordered."""

    def test_strand_better_than_basic_linking_gen1(self):
        disc_strand = abs(ew.braid_strand_discrepancy_log10(1))
        disc_basic  = abs(ew.braid_yukawa_discrepancy_log10(1))
        assert disc_strand < disc_basic

    def test_strand_better_than_basic_linking_gen2(self):
        disc_strand = abs(ew.braid_strand_discrepancy_log10(2))
        disc_basic  = abs(ew.braid_yukawa_discrepancy_log10(2))
        assert disc_strand < disc_basic

    def test_vibrational_lambda_greater_than_cs_sq(self):
        assert ew.braid_quartic_from_stiffness() > ew.kk_geometric_quartic()

    def test_top_corrected_better_than_tree(self):
        obs = ew.HIGGS_MASS_GEV
        err_tree   = abs(ew.higgs_mass_from_cs_squared() - obs)
        err_1loop  = abs(ew.braid_higgs_mass_top_corrected() - obs)
        assert err_1loop < err_tree

    def test_gw_tension_plus_topo_equals_obs(self):
        kpi_obs  = ew.rs1_kpi_R_for_ew_scale()
        kpi_topo = ew.braid_topological_kpi_R()
        gw_gap   = ew.braid_gw_residual_tension()
        assert abs(kpi_topo + gw_gap - kpi_obs) < 1e-10

    def test_equilibrium_radius_matches_topological_kpiR(self):
        # λ5d=-6 → R_eq = 12π = braid_topological_kpi_R
        R_eq = ew.braid_equilibrium_radius(lambda5d=-6.0)
        assert abs(R_eq - ew.braid_topological_kpi_R()) < 1e-8

    def test_alexander_at_strand_yukawa_t(self):
        # Evaluate Alexander polynomial at t matching strand Yukawa for gen 1
        t1 = math.exp(-1 * ew.BRAID_N2 * ew.RS1_KPI_R_CANONICAL / ew.K_CS_CANONICAL)
        val = ew.braid_alexander_polynomial(t1)
        # Should return a well-defined float in (0, 2)
        assert 0.0 < val < 2.0

    def test_all_lambdas_positive(self):
        assert ew.braid_quartic_from_winding_ratio() > 0.0
        assert ew.kk_geometric_quartic() > 0.0
        assert ew.braid_quartic_from_stiffness() > 0.0


# ===========================================================================
# §11  Hard-cutoff Higgs mass additions (Pillar 50 extension)
# ===========================================================================

class TestBraidHardCutoffDeltaMhSq:
    """braid_hard_cutoff_delta_mh_sq: top-loop δm_H² in hard-cutoff scheme."""

    def test_canonical_value(self):
        """At Λ = 332 GeV δm_H² ≈ −5 339 GeV²."""
        delta = ew.braid_hard_cutoff_delta_mh_sq()
        assert abs(delta - (-5339.23)) < 1.0

    def test_always_negative(self):
        """Hard-cutoff correction is negative for all physical Λ."""
        for lam in [50.0, 172.0, 200.0, 285.0, 332.0, 480.0, 1000.0]:
            assert ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=lam) < 0.0

    def test_monotonically_more_negative_with_cutoff(self):
        """Larger Λ gives a more negative correction."""
        d200 = ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=200.0)
        d332 = ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=332.0)
        d600 = ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=600.0)
        assert d200 > d332 > d600

    def test_at_200_gev(self):
        delta = ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=200.0)
        assert abs(delta - (-2343.15)) < 1.0

    def test_scales_quadratically_for_large_cutoff(self):
        """For large Λ the −Λ² term dominates; doubling Λ roughly quadruples |δm_H²|."""
        d500 = abs(ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=500.0))
        d1000 = abs(ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=1000.0))
        ratio = d1000 / d500
        # Exact quadratic scaling gives ratio 4; log correction makes it slightly < 4
        assert 3.0 < ratio < 5.0

    def test_nondefault_top_mass(self):
        """Varying top mass changes δm_H²; result is still negative."""
        d_heavy = ew.braid_hard_cutoff_delta_mh_sq(m_top_gev=200.0)
        assert d_heavy < 0.0

    def test_nondefault_yukawa(self):
        """Larger Yukawa gives larger |δm_H²|."""
        d1 = ew.braid_hard_cutoff_delta_mh_sq(y_top=1.0)
        d2 = ew.braid_hard_cutoff_delta_mh_sq(y_top=1.5)
        assert d2 < d1

    def test_raises_nonpositive_cutoff(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=0.0)

    def test_raises_negative_cutoff(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=-100.0)

    def test_raises_nonpositive_top_mass(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_delta_mh_sq(m_top_gev=0.0)

    def test_raises_nonpositive_yukawa(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_delta_mh_sq(y_top=0.0)

    def test_returns_float(self):
        assert isinstance(ew.braid_hard_cutoff_delta_mh_sq(), float)


class TestBraidHiggsMassHardCutoff:
    """braid_higgs_mass_hard_cutoff: physical Higgs mass in hard-cutoff scheme."""

    def test_canonical_value_at_200_gev(self):
        """At Λ = 200 GeV (below tachyonic threshold) m_H ≈ 101.9 GeV."""
        m = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=200.0)
        assert abs(m - 101.92) < 0.1

    def test_canonical_value_at_332_gev(self):
        """At Λ = 332 GeV m_H ≈ 85.97 GeV (hard-cutoff scheme)."""
        m = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=332.0)
        assert abs(m - 85.97) < 0.1

    def test_below_tree_level(self):
        """Hard-cutoff mass is below tree-level (negative correction dominates)."""
        m_tree = ew.higgs_mass_from_cs_squared()
        m_hard = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=200.0)
        assert m_hard < m_tree

    def test_decreases_with_cutoff(self):
        """Higher Λ → more negative correction → lower hard-cutoff m_H."""
        m200 = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=200.0)
        m300 = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=300.0)
        assert m200 > m300

    def test_raises_tachyonic(self):
        """Above the tachyonic threshold (≈ 480 GeV) a ValueError is raised."""
        lam_tach = ew.braid_tachyon_kk_scale()
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=lam_tach + 50.0)

    def test_raises_nonpositive_vev(self):
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_hard_cutoff(higgs_vev_gev=0.0)

    def test_raises_nonpositive_cs(self):
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_hard_cutoff(c_s=0.0)

    def test_positive(self):
        assert ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=200.0) > 0.0


class TestBraidHardCutoffFinetuning:
    """braid_hard_cutoff_finetuning: Δ_FT = |δm_H²(hard)| / m_H_obs²."""

    def test_canonical_value(self):
        """At Λ = 332 GeV Δ_FT ≈ 0.341 (34% fine-tuning)."""
        ft = ew.braid_hard_cutoff_finetuning()
        assert abs(ft - 0.341) < 0.005

    def test_below_one_at_canonical_cutoff(self):
        """At Λ = 332 GeV model is mildly unnatural but Δ_FT < 1."""
        assert ew.braid_hard_cutoff_finetuning() < 1.0

    def test_below_one_at_200_gev(self):
        """At Λ = 200 GeV Δ_FT ≈ 0.15 < 1."""
        ft = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=200.0)
        assert ft < 1.0

    def test_above_one_at_600_gev(self):
        """At Λ = 600 GeV correction exceeds m_H_obs² — model is unnatural."""
        ft = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=600.0)
        assert ft > 1.0

    def test_monotonically_increases_with_cutoff(self):
        """Fine-tuning grows with cutoff because |δm_H²| ∝ Λ²."""
        ft200 = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=200.0)
        ft332 = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=332.0)
        ft600 = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=600.0)
        assert ft200 < ft332 < ft600

    def test_equals_one_at_lambda_nat(self):
        """By construction Δ_FT = 1 exactly at the naturalness bound Λ_nat."""
        lam_nat = ew.braid_natural_kk_scale()
        ft = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=lam_nat)
        assert abs(ft - 1.0) < 1e-4

    def test_positive(self):
        assert ew.braid_hard_cutoff_finetuning() > 0.0

    def test_larger_higgs_mass_reduces_finetuning(self):
        """If m_H_obs² is larger the denominator grows and Δ_FT decreases."""
        ft1 = ew.braid_hard_cutoff_finetuning(higgs_mass_gev=125.09)
        ft2 = ew.braid_hard_cutoff_finetuning(higgs_mass_gev=200.0)
        assert ft2 < ft1

    def test_raises_nonpositive_higgs_mass(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_finetuning(higgs_mass_gev=0.0)

    def test_raises_nonpositive_cutoff(self):
        with pytest.raises(ValueError):
            ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=0.0)

    def test_returns_float(self):
        assert isinstance(ew.braid_hard_cutoff_finetuning(), float)


class TestBraidNaturalKKScale:
    """braid_natural_kk_scale: bisection root Λ_nat where |δm_H²| = m_H_obs²."""

    def test_canonical_value(self):
        """Λ_nat ≈ 524 GeV."""
        lam = ew.braid_natural_kk_scale()
        assert abs(lam - 524.4) < 1.0

    def test_above_top_mass(self):
        assert ew.braid_natural_kk_scale() > ew.TOP_MASS_GEV

    def test_below_tev(self):
        assert ew.braid_natural_kk_scale() < 1000.0

    def test_above_tachyon_scale(self):
        """Λ_nat > Λ_tach: naturalness bound lies beyond the tachyonic threshold."""
        assert ew.braid_natural_kk_scale() > ew.braid_tachyon_kk_scale()

    def test_round_trip_finetuning_equals_one(self):
        """Finetuning at Λ_nat must equal 1 to within numerical precision."""
        lam_nat = ew.braid_natural_kk_scale()
        ft = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=lam_nat)
        assert abs(ft - 1.0) < 1e-4

    def test_increases_with_higgs_mass(self):
        """Larger observed m_H_obs → correction can be larger → higher Λ_nat."""
        lam1 = ew.braid_natural_kk_scale(higgs_mass_gev=125.09)
        lam2 = ew.braid_natural_kk_scale(higgs_mass_gev=200.0)
        assert lam2 > lam1

    def test_varies_with_top_mass(self):
        """Varying top mass changes Λ_nat; heavier top → higher Λ_nat at fixed y_top."""
        lam_light = ew.braid_natural_kk_scale(m_top_gev=150.0)
        lam_heavy = ew.braid_natural_kk_scale(m_top_gev=200.0)
        # At fixed Yukawa, heavier top raises the log term → Λ_nat moves higher
        assert lam_light > ew.TOP_MASS_GEV
        assert lam_heavy > ew.TOP_MASS_GEV
        assert lam_heavy > lam_light

    def test_returns_float(self):
        assert isinstance(ew.braid_natural_kk_scale(), float)

    def test_finetuning_below_one_before_nat(self):
        """Below Λ_nat the fine-tuning is < 1 (model is natural)."""
        lam_nat = ew.braid_natural_kk_scale()
        ft_below = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=lam_nat - 50.0)
        assert ft_below < 1.0

    def test_finetuning_above_one_after_nat(self):
        """Above Λ_nat the fine-tuning exceeds 1 (model becomes unnatural)."""
        lam_nat = ew.braid_natural_kk_scale()
        ft_above = ew.braid_hard_cutoff_finetuning(lambda_cutoff_gev=lam_nat + 50.0)
        assert ft_above > 1.0


class TestBraidTachyonKKScale:
    """braid_tachyon_kk_scale: Λ_tach where m_H²(hard) → 0."""

    def test_canonical_value(self):
        """Λ_tach ≈ 480 GeV."""
        lam = ew.braid_tachyon_kk_scale()
        assert abs(lam - 480.5) < 1.0

    def test_above_top_mass(self):
        assert ew.braid_tachyon_kk_scale() > ew.TOP_MASS_GEV

    def test_below_tev(self):
        assert ew.braid_tachyon_kk_scale() < 1000.0

    def test_below_natural_scale(self):
        """Λ_tach < Λ_nat: tachyonic breakdown precedes the naturalness scale."""
        assert ew.braid_tachyon_kk_scale() < ew.braid_natural_kk_scale()

    def test_round_trip_delta_equals_neg_tree(self):
        """At Λ_tach the hard-cutoff correction exactly cancels the tree mass²."""
        lam_tach = ew.braid_tachyon_kk_scale()
        delta = ew.braid_hard_cutoff_delta_mh_sq(lambda_cutoff_gev=lam_tach)
        tree_sq = 2.0 * ew.C_S_CANONICAL ** 2 * ew.HIGGS_VEV_GEV ** 2
        assert abs(delta + tree_sq) < 1e-6

    def test_hard_cutoff_raises_above_tachyon(self):
        """braid_higgs_mass_hard_cutoff raises ValueError above Λ_tach."""
        lam_tach = ew.braid_tachyon_kk_scale()
        with pytest.raises(ValueError):
            ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=lam_tach + 10.0)

    def test_hard_cutoff_ok_below_tachyon(self):
        """braid_higgs_mass_hard_cutoff succeeds below Λ_tach."""
        lam_tach = ew.braid_tachyon_kk_scale()
        m = ew.braid_higgs_mass_hard_cutoff(lambda_cutoff_gev=lam_tach - 50.0)
        assert m > 0.0

    def test_increases_with_vev(self):
        """Larger tree-level mass (via larger vev) raises the tachyonic threshold."""
        lam1 = ew.braid_tachyon_kk_scale(higgs_vev_gev=246.0)
        lam2 = ew.braid_tachyon_kk_scale(higgs_vev_gev=300.0)
        assert lam2 > lam1

    def test_increases_with_cs(self):
        """Larger c_s → larger tree-level m_H² → harder to go tachyonic → higher Λ_tach."""
        lam1 = ew.braid_tachyon_kk_scale(c_s=ew.C_S_CANONICAL)
        lam2 = ew.braid_tachyon_kk_scale(c_s=0.5)
        assert lam2 > lam1

    def test_raises_nonpositive_vev(self):
        with pytest.raises(ValueError):
            ew.braid_tachyon_kk_scale(higgs_vev_gev=0.0)

    def test_raises_nonpositive_cs(self):
        with pytest.raises(ValueError):
            ew.braid_tachyon_kk_scale(c_s=0.0)

    def test_returns_float(self):
        assert isinstance(ew.braid_tachyon_kk_scale(), float)


class TestBraidHiggsMassSchemeComparison:
    """braid_higgs_mass_scheme_comparison: dim-reg vs hard-cutoff dict."""

    def setup_method(self):
        self.cmp = ew.braid_higgs_mass_scheme_comparison()

    def test_returns_dict(self):
        assert isinstance(self.cmp, dict)

    def test_all_keys_present(self):
        required = {
            "m_H_observed", "m_H_tree", "m_H_dim_reg", "m_H_hard_cutoff",
            "delta_mh_sq_dim_reg", "delta_mh_sq_hard", "finetuning_hard",
            "lambda_nat_gev", "lambda_tach_gev", "scheme_gap_gev",
            "dim_reg_error_pct", "honest_assessment",
        }
        assert required.issubset(self.cmp.keys())

    def test_m_H_observed_matches_constant(self):
        assert self.cmp["m_H_observed"] == ew.HIGGS_MASS_GEV

    def test_m_H_tree_near_113_gev(self):
        assert abs(self.cmp["m_H_tree"] - 112.83) < 0.1

    def test_m_H_dim_reg_near_125_gev(self):
        assert abs(self.cmp["m_H_dim_reg"] - 125.11) < 0.1

    def test_m_H_hard_cutoff_near_86_gev(self):
        assert abs(self.cmp["m_H_hard_cutoff"] - 85.97) < 0.1

    def test_dim_reg_above_tree(self):
        assert self.cmp["m_H_dim_reg"] > self.cmp["m_H_tree"]

    def test_hard_cutoff_below_tree(self):
        assert self.cmp["m_H_hard_cutoff"] < self.cmp["m_H_tree"]

    def test_dim_reg_error_pct_tiny(self):
        """Dim-reg reproduces observed Higgs mass to < 0.1%."""
        assert abs(self.cmp["dim_reg_error_pct"]) < 0.1

    def test_delta_dim_reg_positive(self):
        """Dim-reg (MS-bar log) correction is positive."""
        assert self.cmp["delta_mh_sq_dim_reg"] > 0.0

    def test_delta_hard_negative(self):
        """Hard-cutoff correction is negative (quadratic term dominates)."""
        assert self.cmp["delta_mh_sq_hard"] < 0.0

    def test_finetuning_matches_standalone(self):
        """finetuning_hard in dict equals braid_hard_cutoff_finetuning()."""
        ft_standalone = ew.braid_hard_cutoff_finetuning()
        assert abs(self.cmp["finetuning_hard"] - ft_standalone) < 1e-10

    def test_lambda_nat_matches_standalone(self):
        lam_nat = ew.braid_natural_kk_scale()
        assert abs(self.cmp["lambda_nat_gev"] - lam_nat) < 1e-6

    def test_lambda_tach_matches_standalone(self):
        lam_tach = ew.braid_tachyon_kk_scale()
        assert abs(self.cmp["lambda_tach_gev"] - lam_tach) < 1e-6

    def test_lambda_nat_above_lambda_tach(self):
        assert self.cmp["lambda_nat_gev"] > self.cmp["lambda_tach_gev"]

    def test_scheme_gap_positive(self):
        """dim-reg gives higher m_H than hard-cutoff at Λ=332 GeV."""
        assert self.cmp["scheme_gap_gev"] > 0.0

    def test_scheme_gap_near_39_gev(self):
        assert abs(self.cmp["scheme_gap_gev"] - 39.14) < 0.5

    def test_hard_cutoff_none_above_tachyon(self):
        """When Λ > Λ_tach the hard-cutoff result is None (tachyonic)."""
        cmp_tach = ew.braid_higgs_mass_scheme_comparison(lambda_cutoff_gev=600.0)
        assert cmp_tach["m_H_hard_cutoff"] is None
        assert cmp_tach["scheme_gap_gev"] is None

    def test_scheme_gap_none_implies_tachyonic(self):
        """scheme_gap_gev is None iff m_H_hard_cutoff is None."""
        cmp_tach = ew.braid_higgs_mass_scheme_comparison(lambda_cutoff_gev=600.0)
        assert (cmp_tach["m_H_hard_cutoff"] is None) == (cmp_tach["scheme_gap_gev"] is None)

    def test_honest_assessment_is_string(self):
        assert isinstance(self.cmp["honest_assessment"], str)

    def test_honest_assessment_mentions_scheme(self):
        assert "scheme" in self.cmp["honest_assessment"].lower()

    def test_custom_cutoff_consistent(self):
        """With a custom Λ=200 GeV all derived values remain consistent."""
        cmp200 = ew.braid_higgs_mass_scheme_comparison(lambda_cutoff_gev=200.0)
        # dim-reg mass at 200 GeV is lower than at 332 GeV
        assert cmp200["m_H_dim_reg"] < self.cmp["m_H_dim_reg"]
        # hard-cutoff mass is higher (less correction) at 200 GeV
        assert cmp200["m_H_hard_cutoff"] > self.cmp["m_H_hard_cutoff"]
