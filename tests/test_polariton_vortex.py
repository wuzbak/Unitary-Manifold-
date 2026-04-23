# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_polariton_vortex.py
================================
Unit tests for src/materials/polariton_vortex.py — Pillar 47.

Tests cover:
  - Module constants (c_s, n_w, k_CS, critical angle, topo gap)
  - vortex_speed_ratio / is_superluminal / critical_angle_rad / _deg
  - max_feature_velocity_ratio
  - vortex_topological_charge / merging / annihilation / total charge
  - count_annihilation_pairs
  - topological_protection_gap / kk_winding_to_vortex_charge
  - braided_polariton_speed_um
  - energy_transported_by_vortex / information_transported_by_vortex
  - relativity_violation_check
  - singularity_tracking_resolution / vortex_speed_from_experiment
  - is_experimentally_superluminal
  - um_vortex_summary / VortexSummary
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import pytest

from src.materials.polariton_vortex import (
    # Constants
    N_W_CANONICAL, N1_CANONICAL, N2_CANONICAL, K_CS_CANONICAL,
    C_S_CANONICAL, VORTEX_UNIT_CHARGE,
    HBN_POLARITON_SPEED_NORMALIZED, HBN_SPATIAL_RESOLUTION_NM,
    HBN_TEMPORAL_RESOLUTION_AS,
    # Feature velocity
    vortex_speed_ratio,
    is_superluminal,
    critical_angle_rad,
    critical_angle_deg,
    max_feature_velocity_ratio,
    # Topological charge algebra
    vortex_topological_charge,
    vortex_merging_charge,
    vortex_annihilation_condition,
    total_topological_charge,
    count_annihilation_pairs,
    # UM topology
    topological_protection_gap,
    kk_winding_to_vortex_charge,
    braided_polariton_speed_um,
    # Relativity
    energy_transported_by_vortex,
    information_transported_by_vortex,
    relativity_violation_check,
    # Experimental
    singularity_tracking_resolution,
    vortex_speed_from_experiment,
    is_experimentally_superluminal,
    # Summary
    um_vortex_summary,
    VortexSummary,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS_CANONICAL == N1_CANONICAL ** 2 + N2_CANONICAL ** 2

    def test_c_s_canonical_exact(self):
        assert C_S_CANONICAL == pytest.approx(12.0 / 37.0, rel=1e-12)

    def test_c_s_braid_formula(self):
        expected = (N2_CANONICAL ** 2 - N1_CANONICAL ** 2) / K_CS_CANONICAL
        assert C_S_CANONICAL == pytest.approx(expected, rel=1e-12)

    def test_c_s_less_than_one(self):
        assert C_S_CANONICAL < 1.0

    def test_c_s_positive(self):
        assert C_S_CANONICAL > 0.0

    def test_vortex_unit_charge(self):
        assert VORTEX_UNIT_CHARGE == 1

    def test_hbn_speed_equals_c_s(self):
        assert HBN_POLARITON_SPEED_NORMALIZED == pytest.approx(C_S_CANONICAL, rel=1e-12)

    def test_hbn_spatial_res_positive(self):
        assert HBN_SPATIAL_RESOLUTION_NM > 0.0

    def test_hbn_temporal_res_positive(self):
        assert HBN_TEMPORAL_RESOLUTION_AS > 0.0


# ---------------------------------------------------------------------------
# TestVortexSpeedRatio
# ---------------------------------------------------------------------------

class TestVortexSpeedRatio:
    def test_at_critical_angle_equals_one(self):
        theta_c = critical_angle_rad()
        ratio = vortex_speed_ratio(theta_c)
        assert ratio == pytest.approx(1.0, rel=1e-8)

    def test_below_critical_is_superluminal(self):
        theta_c = critical_angle_rad()
        ratio = vortex_speed_ratio(theta_c * 0.5)
        assert ratio > 1.0

    def test_above_critical_is_subluminal(self):
        theta_c = critical_angle_rad()
        ratio = vortex_speed_ratio(theta_c + 0.1)
        assert ratio < 1.0

    def test_at_90_degrees_equals_c_s(self):
        ratio = vortex_speed_ratio(math.pi / 2.0)
        assert ratio == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_formula_c_s_over_sin_theta(self):
        theta = math.radians(30.0)
        expected = C_S_CANONICAL / math.sin(theta)
        assert vortex_speed_ratio(theta) == pytest.approx(expected, rel=1e-12)

    def test_custom_c_s(self):
        c_s = 0.5
        theta = math.radians(45.0)
        expected = c_s / math.sin(theta)
        assert vortex_speed_ratio(theta, c_s=c_s) == pytest.approx(expected, rel=1e-12)

    def test_raises_zero_theta(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(0.0)

    def test_raises_negative_theta(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(-0.1)

    def test_raises_theta_greater_than_pi_over_2(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(math.pi / 2.0 + 0.01)

    def test_raises_c_s_zero(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(math.radians(30.0), c_s=0.0)

    def test_raises_c_s_one(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(math.radians(30.0), c_s=1.0)

    def test_raises_c_s_greater_than_one(self):
        with pytest.raises(ValueError):
            vortex_speed_ratio(math.radians(30.0), c_s=1.5)

    def test_at_5_deg_superluminal(self):
        ratio = vortex_speed_ratio(math.radians(5.0))
        assert ratio > 1.0

    def test_at_45_deg_subluminal(self):
        ratio = vortex_speed_ratio(math.radians(45.0))
        assert ratio < 1.0

    def test_monotone_decreasing_in_theta(self):
        thetas = [math.radians(a) for a in [5, 10, 20, 45, 89]]
        ratios = [vortex_speed_ratio(t) for t in thetas]
        for i in range(len(ratios) - 1):
            assert ratios[i] > ratios[i + 1]

    def test_positive_for_any_valid_input(self):
        for deg in [1, 5, 20, 45, 89]:
            assert vortex_speed_ratio(math.radians(deg)) > 0.0


# ---------------------------------------------------------------------------
# TestIsSuperluminal
# ---------------------------------------------------------------------------

class TestIsSuperluminal:
    def test_small_angle_is_superluminal(self):
        assert is_superluminal(math.radians(5.0))

    def test_large_angle_not_superluminal(self):
        assert not is_superluminal(math.radians(45.0))

    def test_exactly_at_critical_not_superluminal(self):
        theta_c = critical_angle_rad()
        # At θ_c, ratio == 1.0 exactly; > 1 is False
        assert not is_superluminal(theta_c)

    def test_just_below_critical_is_superluminal(self):
        theta_c = critical_angle_rad()
        assert is_superluminal(theta_c - 1e-6)

    def test_90_degrees_not_superluminal(self):
        assert not is_superluminal(math.pi / 2.0)


# ---------------------------------------------------------------------------
# TestCriticalAngle
# ---------------------------------------------------------------------------

class TestCriticalAngle:
    def test_canonical_critical_angle_rad(self):
        expected = math.asin(C_S_CANONICAL)
        assert critical_angle_rad() == pytest.approx(expected, rel=1e-12)

    def test_canonical_critical_angle_deg(self):
        expected = math.degrees(math.asin(C_S_CANONICAL))
        assert critical_angle_deg() == pytest.approx(expected, rel=1e-10)

    def test_canonical_deg_approx_19(self):
        # arcsin(12/37) ≈ 18.93°
        assert 18.0 < critical_angle_deg() < 20.0

    def test_c_s_half_gives_30_deg(self):
        # arcsin(0.5) = 30°
        assert critical_angle_deg(0.5) == pytest.approx(30.0, rel=1e-8)

    def test_critical_angle_monotone_in_c_s(self):
        a1 = critical_angle_rad(0.2)
        a2 = critical_angle_rad(0.5)
        a3 = critical_angle_rad(0.8)
        assert a1 < a2 < a3

    def test_raises_c_s_zero(self):
        with pytest.raises(ValueError):
            critical_angle_rad(0.0)

    def test_raises_c_s_one(self):
        with pytest.raises(ValueError):
            critical_angle_rad(1.0)

    def test_raises_c_s_negative(self):
        with pytest.raises(ValueError):
            critical_angle_rad(-0.1)


# ---------------------------------------------------------------------------
# TestMaxFeatureVelocity
# ---------------------------------------------------------------------------

class TestMaxFeatureVelocityRatio:
    def test_positive(self):
        assert max_feature_velocity_ratio() > 0.0

    def test_larger_than_one(self):
        # at 1 mrad, c_s/(sin 1e-3) >> 1
        assert max_feature_velocity_ratio(C_S_CANONICAL, theta_min_rad=1e-3) > 1.0

    def test_decreasing_with_larger_theta_min(self):
        v1 = max_feature_velocity_ratio(C_S_CANONICAL, theta_min_rad=0.01)
        v2 = max_feature_velocity_ratio(C_S_CANONICAL, theta_min_rad=0.1)
        assert v1 > v2

    def test_raises_zero_theta_min(self):
        with pytest.raises(ValueError):
            max_feature_velocity_ratio(C_S_CANONICAL, theta_min_rad=0.0)

    def test_raises_negative_theta_min(self):
        with pytest.raises(ValueError):
            max_feature_velocity_ratio(C_S_CANONICAL, theta_min_rad=-0.01)


# ---------------------------------------------------------------------------
# TestVortexTopologicalCharge
# ---------------------------------------------------------------------------

class TestVortexTopologicalCharge:
    def test_unit_positive_charge(self):
        assert vortex_topological_charge(1) == 1

    def test_unit_negative_charge(self):
        assert vortex_topological_charge(-1) == -1

    def test_double_charge(self):
        assert vortex_topological_charge(2) == 2

    def test_zero_charge(self):
        assert vortex_topological_charge(0) == 0

    def test_raises_float_input(self):
        with pytest.raises(TypeError):
            vortex_topological_charge(1.0)


# ---------------------------------------------------------------------------
# TestVortexMergingAndAnnihilation
# ---------------------------------------------------------------------------

class TestVortexMerging:
    def test_merge_plus_plus(self):
        assert vortex_merging_charge(1, 1) == 2

    def test_merge_plus_minus_annihilates(self):
        assert vortex_merging_charge(1, -1) == 0

    def test_merge_zero_neutral(self):
        assert vortex_merging_charge(0, 3) == 3

    def test_commutative(self):
        assert vortex_merging_charge(2, 3) == vortex_merging_charge(3, 2)


class TestVortexAnnihilationCondition:
    def test_plus_minus_annihilates(self):
        assert vortex_annihilation_condition(1, -1)

    def test_plus_plus_no_annihilation(self):
        assert not vortex_annihilation_condition(1, 1)

    def test_two_and_minus_two(self):
        assert vortex_annihilation_condition(2, -2)

    def test_zero_zero(self):
        assert vortex_annihilation_condition(0, 0)

    def test_asymmetric_no_annihilation(self):
        assert not vortex_annihilation_condition(1, -2)


# ---------------------------------------------------------------------------
# TestTotalTopologicalCharge
# ---------------------------------------------------------------------------

class TestTotalTopologicalCharge:
    def test_empty_list(self):
        assert total_topological_charge([]) == 0

    def test_single_charge(self):
        assert total_topological_charge([3]) == 3

    def test_conserved_after_merge(self):
        charges = [1, -1, 2, 1]
        assert total_topological_charge(charges) == 3

    def test_all_annihilate(self):
        assert total_topological_charge([1, -1, 1, -1]) == 0

    def test_canonical_winding(self):
        # Five vortices of charge +1 (n_w = 5)
        assert total_topological_charge([1] * N_W_CANONICAL) == N_W_CANONICAL


# ---------------------------------------------------------------------------
# TestCountAnnihilationPairs
# ---------------------------------------------------------------------------

class TestCountAnnihilationPairs:
    def test_one_pair(self):
        assert count_annihilation_pairs([1, -1]) == 1

    def test_two_pairs(self):
        assert count_annihilation_pairs([1, 1, -1, -1]) == 2

    def test_unbalanced(self):
        assert count_annihilation_pairs([1, 1, -1]) == 1

    def test_no_negatives(self):
        assert count_annihilation_pairs([1, 2, 3]) == 0

    def test_no_positives(self):
        assert count_annihilation_pairs([-1, -2]) == 0

    def test_empty(self):
        assert count_annihilation_pairs([]) == 0


# ---------------------------------------------------------------------------
# TestTopologicalProtectionGap
# ---------------------------------------------------------------------------

class TestTopologicalProtectionGap:
    def test_canonical_value(self):
        expected = N_W_CANONICAL ** 2 / K_CS_CANONICAL
        assert topological_protection_gap() == pytest.approx(expected, rel=1e-12)

    def test_canonical_approx_0_338(self):
        gap = topological_protection_gap()
        assert 0.33 < gap < 0.35

    def test_scales_as_n_w_squared(self):
        g1 = topological_protection_gap(n_w=1, k_cs=74)
        g2 = topological_protection_gap(n_w=2, k_cs=74)
        assert g2 == pytest.approx(4.0 * g1, rel=1e-12)

    def test_raises_n_w_zero(self):
        with pytest.raises(ValueError):
            topological_protection_gap(n_w=0)

    def test_raises_k_cs_zero(self):
        with pytest.raises(ValueError):
            topological_protection_gap(k_cs=0)

    def test_raises_negative_k_cs(self):
        with pytest.raises(ValueError):
            topological_protection_gap(k_cs=-1)


# ---------------------------------------------------------------------------
# TestKkWindingToVortexCharge
# ---------------------------------------------------------------------------

class TestKkWindingToVortexCharge:
    def test_canonical_n_w_5(self):
        assert kk_winding_to_vortex_charge(5) == 5

    def test_n_w_1(self):
        assert kk_winding_to_vortex_charge(1) == 1

    def test_n_w_3(self):
        assert kk_winding_to_vortex_charge(3) == 3

    def test_n_w_7_allowed(self):
        assert kk_winding_to_vortex_charge(7) == 7

    def test_raises_even_n_w(self):
        with pytest.raises(ValueError):
            kk_winding_to_vortex_charge(4)

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            kk_winding_to_vortex_charge(0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            kk_winding_to_vortex_charge(-1)


# ---------------------------------------------------------------------------
# TestBraidedPolaritonSpeedUm
# ---------------------------------------------------------------------------

class TestBraidedPolaritonSpeedUm:
    def test_canonical_value(self):
        assert braided_polariton_speed_um() == pytest.approx(12.0 / 37.0, rel=1e-12)

    def test_canonical_matches_c_s(self):
        assert braided_polariton_speed_um() == pytest.approx(C_S_CANONICAL, rel=1e-12)

    def test_different_braid_pair(self):
        # (3, 5): c_s = (25-9)/(9+25) = 16/34
        c_s = braided_polariton_speed_um(n1=3, n2=5)
        assert c_s == pytest.approx(16.0 / 34.0, rel=1e-12)

    def test_in_zero_one(self):
        c_s = braided_polariton_speed_um()
        assert 0.0 < c_s < 1.0

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            braided_polariton_speed_um(n1=0, n2=7)

    def test_raises_n2_equal_n1(self):
        with pytest.raises(ValueError):
            braided_polariton_speed_um(n1=5, n2=5)

    def test_raises_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            braided_polariton_speed_um(n1=7, n2=5)


# ---------------------------------------------------------------------------
# TestRelativity
# ---------------------------------------------------------------------------

class TestRelativityConsistency:
    def test_energy_transported_zero(self):
        assert energy_transported_by_vortex() == 0.0

    def test_information_transported_zero(self):
        assert information_transported_by_vortex() == 0.0

    def test_no_sr_violation_at_any_speed(self):
        for v in [0.5, 1.0, 2.0, 100.0, 1e10]:
            assert relativity_violation_check(v) is False

    def test_always_false(self):
        assert relativity_violation_check(vortex_speed_ratio(math.radians(5.0))) is False


# ---------------------------------------------------------------------------
# TestSingularityTrackingResolution
# ---------------------------------------------------------------------------

class TestSingularityTrackingResolution:
    def test_returns_dict_with_expected_keys(self):
        d = singularity_tracking_resolution()
        for key in ("spatial_nm", "temporal_as", "spatial_m",
                    "temporal_s", "velocity_resolution_m_per_s"):
            assert key in d

    def test_spatial_conversion(self):
        d = singularity_tracking_resolution(spatial_nm=2.0, temporal_as=100.0)
        assert d["spatial_m"] == pytest.approx(2e-9, rel=1e-12)

    def test_temporal_conversion(self):
        d = singularity_tracking_resolution(spatial_nm=1.0, temporal_as=200.0)
        assert d["temporal_s"] == pytest.approx(200e-18, rel=1e-12)

    def test_velocity_resolution_positive(self):
        d = singularity_tracking_resolution()
        assert d["velocity_resolution_m_per_s"] > 0.0

    def test_velocity_resolution_formula(self):
        d = singularity_tracking_resolution(spatial_nm=1.0, temporal_as=100.0)
        expected = 1e-9 / 100e-18
        assert d["velocity_resolution_m_per_s"] == pytest.approx(expected, rel=1e-10)

    def test_raises_zero_spatial(self):
        with pytest.raises(ValueError):
            singularity_tracking_resolution(spatial_nm=0.0)

    def test_raises_negative_temporal(self):
        with pytest.raises(ValueError):
            singularity_tracking_resolution(temporal_as=-1.0)

    def test_finer_resolution_faster_min_velocity(self):
        d_fine = singularity_tracking_resolution(spatial_nm=0.5, temporal_as=100.0)
        d_coarse = singularity_tracking_resolution(spatial_nm=2.0, temporal_as=100.0)
        assert d_fine["velocity_resolution_m_per_s"] < d_coarse["velocity_resolution_m_per_s"]


# ---------------------------------------------------------------------------
# TestVortexSpeedFromExperiment
# ---------------------------------------------------------------------------

class TestVortexSpeedFromExperiment:
    def test_positive_output(self):
        assert vortex_speed_from_experiment(10.0, 100.0) > 0.0

    def test_formula_exact(self):
        expected = 5e-9 / 200e-18
        assert vortex_speed_from_experiment(5.0, 200.0) == pytest.approx(expected, rel=1e-12)

    def test_larger_displacement_faster(self):
        v1 = vortex_speed_from_experiment(10.0, 100.0)
        v2 = vortex_speed_from_experiment(20.0, 100.0)
        assert v2 > v1

    def test_longer_time_slower(self):
        v1 = vortex_speed_from_experiment(10.0, 50.0)
        v2 = vortex_speed_from_experiment(10.0, 100.0)
        assert v1 > v2

    def test_raises_zero_displacement(self):
        with pytest.raises(ValueError):
            vortex_speed_from_experiment(0.0, 100.0)

    def test_raises_negative_displacement(self):
        with pytest.raises(ValueError):
            vortex_speed_from_experiment(-1.0, 100.0)

    def test_raises_zero_time(self):
        with pytest.raises(ValueError):
            vortex_speed_from_experiment(10.0, 0.0)


# ---------------------------------------------------------------------------
# TestIsExperimentallySuperluminal
# ---------------------------------------------------------------------------

class TestIsExperimentallySuperluminal:
    _C_LIGHT = 2.998e8  # m/s

    def test_superluminal_case(self):
        # v = 1 nm / 1 as = 1e-9 / 1e-18 = 1e9 m/s >> c
        assert is_experimentally_superluminal(1.0, 1.0)

    def test_subluminal_case(self):
        # v = 1 nm / 1e6 as = 1e-9 / 1e-12 = 1e-3 m/s << c
        assert not is_experimentally_superluminal(1.0, 1e6)

    def test_exactly_at_c_not_superluminal(self):
        # delta_x / delta_t == c → not > c
        delta_t_as = (1e-9 / self._C_LIGHT) / 1e-18
        assert not is_experimentally_superluminal(1.0, delta_t_as)


# ---------------------------------------------------------------------------
# TestUmVortexSummary
# ---------------------------------------------------------------------------

class TestUmVortexSummary:
    def setup_method(self):
        self.s = um_vortex_summary()

    def test_returns_vortex_summary_instance(self):
        assert isinstance(self.s, VortexSummary)

    def test_c_s_um_equals_canonical(self):
        assert self.s.c_s_um == pytest.approx(C_S_CANONICAL, rel=1e-12)

    def test_critical_angle_deg_approx_19(self):
        assert 18.0 < self.s.critical_angle_deg < 20.0

    def test_topo_gap_canonical(self):
        expected = N_W_CANONICAL ** 2 / K_CS_CANONICAL
        assert self.s.topo_gap == pytest.approx(expected, rel=1e-12)

    def test_unit_charge_one(self):
        assert self.s.unit_charge == 1

    def test_canonical_winding_five(self):
        assert self.s.canonical_winding == 5

    def test_feature_vel_at_5deg_superluminal(self):
        assert self.s.feature_vel_at_5deg > 1.0

    def test_feature_vel_at_45deg_subluminal(self):
        assert self.s.feature_vel_at_45deg < 1.0

    def test_energy_zero(self):
        assert self.s.energy_transported == 0.0

    def test_info_zero(self):
        assert self.s.info_transported == 0.0

    def test_hbn_spatial_res_positive(self):
        assert self.s.hbn_spatial_res_nm > 0.0

    def test_hbn_temporal_res_positive(self):
        assert self.s.hbn_temporal_res_as > 0.0

    def test_deterministic(self):
        s2 = um_vortex_summary()
        assert self.s.c_s_um == s2.c_s_um
        assert self.s.critical_angle_deg == s2.critical_angle_deg
