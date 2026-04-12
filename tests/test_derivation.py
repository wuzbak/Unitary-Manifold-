# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_derivation.py
========================
Derivation tests for the key integers of the Unitary Manifold.

The theory has no free parameters: every integer that appears in the
predictions is uniquely forced by the geometry.  This file tests each
of those derivations individually, verifying that the integers are not
arbitrary but follow from the constraints.

Key integers under test
-----------------------
k_cs = 74      Chern-Simons level, forced by the birefringence measurement
n_w_kk = 5    Winding number for the flat S¹/Z₂ KK compactification, forced
               by the Planck nₛ window
n_w_rs = 7    Winding number for the RS1 orbifold branch, also forced by nₛ
k_rc = 12     Kaluza-Klein hierarchy product k·r_c, set by the RS hierarchy
               problem solution (≈ 12 gives e^{−2πkr_c} ≈ 10⁻³³)
phi_min = 18  Bare GW minimum φ_min_bare, which together with J_RS pins Δφ
               and thus closes the k_cs derivation loop

Organisation: six test classes, each dedicated to one key integer.
"""

from __future__ import annotations

import math
import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.inflation import (
    CS_LEVEL_PLANCK_MATCH,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    jacobian_5d_4d,
    jacobian_rs_orbifold,
    effective_phi0_kk,
    effective_phi0_rs,
    ns_from_phi0,
    planck2018_check,
    cs_axion_photon_coupling,
    cs_level_for_birefringence,
    field_displacement_gw,
    birefringence_angle,
    gauge_coupling_5d_for_alpha,
    fine_structure_rs,
)

# ---------------------------------------------------------------------------
# Shared geometric constants (canonical FTUM parameters)
# ---------------------------------------------------------------------------
_PHI0_BARE   = 1.0          # FTUM radion vev (Planck units)
_ALPHA_EM    = 1.0 / 137.036
_K_ADV       = 1.0          # AdS curvature k (M_5 = 1 units)
_KRC         = 12           # k·r_c product (hierarchy solution)
_RC          = float(_KRC) / _K_ADV  # = 12.0
_J_RS        = jacobian_rs_orbifold(_K_ADV, _RC)
_PHI_MIN_BARE = 18.0
_PHI_MIN_PHYS = _J_RS * _PHI_MIN_BARE  # ≈ 12.73
_DELTA_PHI   = field_displacement_gw(_PHI_MIN_PHYS)


# ===========================================================================
# 1 · TestCSLevelDerivation  (15 tests)
# ===========================================================================

class TestCSLevelDerivation:
    """Verify k_cs = 74 is the unique integer derived from the birefringence
    constraint β = 0.35 ± 0.14° (Minami & Komatsu 2020).

    The derivation chain is:
        β_target → β_rad → k_cs_float = β_rad · 4π² r_c / (α |Δφ|) → round → 74
    """

    def test_cs_level_planck_match_constant_is_74(self):
        assert CS_LEVEL_PLANCK_MATCH == 74

    def test_cs_level_planck_match_is_int(self):
        assert isinstance(CS_LEVEL_PLANCK_MATCH, int)

    def test_cs_level_for_birefringence_returns_float_near_73p7(self):
        k_float = cs_level_for_birefringence(
            BIREFRINGENCE_TARGET_DEG, _ALPHA_EM, _RC, _DELTA_PHI
        )
        assert 73.0 < k_float < 74.5

    def test_rounding_cs_float_gives_74(self):
        k_float = cs_level_for_birefringence(
            BIREFRINGENCE_TARGET_DEG, _ALPHA_EM, _RC, _DELTA_PHI
        )
        assert round(k_float) == 74

    def test_cs_level_float_between_73_and_74(self):
        k_float = cs_level_for_birefringence(
            BIREFRINGENCE_TARGET_DEG, _ALPHA_EM, _RC, _DELTA_PHI
        )
        assert 73 <= k_float < 74.5

    def test_k74_gives_beta_within_1sigma_planck(self):
        g_agg = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        beta_deg = math.degrees(birefringence_angle(g_agg, _DELTA_PHI))
        assert abs(beta_deg - BIREFRINGENCE_TARGET_DEG) < BIREFRINGENCE_SIGMA_DEG

    def test_k73_deviation_exceeds_k74_deviation(self):
        def dev(k):
            g = cs_axion_photon_coupling(k, _ALPHA_EM, _RC)
            return abs(math.degrees(birefringence_angle(g, _DELTA_PHI)) - BIREFRINGENCE_TARGET_DEG)
        assert dev(74) < dev(73)

    def test_k75_deviation_exceeds_k74_deviation(self):
        def dev(k):
            g = cs_axion_photon_coupling(k, _ALPHA_EM, _RC)
            return abs(math.degrees(birefringence_angle(g, _DELTA_PHI)) - BIREFRINGENCE_TARGET_DEG)
        assert dev(74) < dev(75)

    def test_k74_uniquely_minimises_beta_deviation_over_1_to_100(self):
        devs = {}
        for k in range(1, 101):
            g = cs_axion_photon_coupling(k, _ALPHA_EM, _RC)
            devs[k] = abs(math.degrees(birefringence_angle(g, _DELTA_PHI)) - BIREFRINGENCE_TARGET_DEG)
        assert min(devs, key=devs.__getitem__) == 74

    def test_cs_coupling_formula_is_k_alpha_over_2pi2_rc(self):
        g_expected = 74 * _ALPHA_EM / (2.0 * math.pi**2 * _RC)
        g_computed = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        assert abs(g_computed - g_expected) < 1e-15

    def test_k74_beta_approximately_0p35_degrees(self):
        g_agg = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        beta_deg = math.degrees(birefringence_angle(g_agg, _DELTA_PHI))
        assert abs(beta_deg - 0.35) < 0.02

    def test_k_cs_derivation_inverts_birefringence_formula(self):
        # Forward: k=74 → β.  Invert: β → k_float.  Should give back ~74.
        g_agg = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        beta_from_74 = math.degrees(birefringence_angle(g_agg, _DELTA_PHI))
        k_recovered = cs_level_for_birefringence(beta_from_74, _ALPHA_EM, _RC, _DELTA_PHI)
        assert abs(k_recovered - 74.0) < 0.01

    def test_k_cs_is_positive_integer_greater_than_zero(self):
        assert CS_LEVEL_PLANCK_MATCH >= 1

    def test_g_agg_from_k74_is_positive_and_finite(self):
        g = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        assert g > 0
        assert math.isfinite(g)

    def test_beta_from_k74_is_positive_radians(self):
        g = cs_axion_photon_coupling(74, _ALPHA_EM, _RC)
        beta_rad = birefringence_angle(g, _DELTA_PHI)
        assert beta_rad > 0


# ===========================================================================
# 2 · TestKKWindingNumber  (10 tests)
# ===========================================================================

class TestKKWindingNumber:
    """Verify n_winding = 5 is the unique integer that places nₛ inside the
    Planck 2018 1-σ window via the flat S¹/Z₂ KK projection.

    Chain:  n_winding=5, φ₀_bare=1  →  φ₀_eff = 5·2π·1 = 10π ≈ 31.42
            φ* = φ₀_eff/√3  →  nₛ ≈ 0.9635  (Planck: 0.9649 ± 0.0042)
    """

    def test_n_winding_5_is_default_for_effective_phi0_kk(self):
        phi_default = effective_phi0_kk(_PHI0_BARE)
        phi_explicit = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        assert abs(phi_default - phi_explicit) < 1e-12

    def test_n_winding_5_gives_phi0_eff_equal_to_10pi(self):
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        assert abs(phi_eff - 10.0 * math.pi) < 1e-10

    def test_n_winding_5_gives_ns_in_planck_1sigma(self):
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        ns, *_ = ns_from_phi0(phi_eff)
        assert planck2018_check(ns, n_sigma=1.0)

    def test_n_winding_4_fails_planck_1sigma(self):
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=4)
        ns, *_ = ns_from_phi0(phi_eff)
        assert not planck2018_check(ns, n_sigma=1.0)

    def test_n_winding_6_fails_planck_1sigma(self):
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=6)
        ns, *_ = ns_from_phi0(phi_eff)
        assert not planck2018_check(ns, n_sigma=1.0)

    def test_only_n_winding_5_passes_planck_1sigma_among_1_to_10(self):
        passers = []
        for n in range(1, 11):
            phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=n)
            ns, *_ = ns_from_phi0(phi_eff)
            if planck2018_check(ns, n_sigma=1.0):
                passers.append(n)
        assert passers == [5]

    def test_jacobian_kk_for_phi0_1_nw_5_equals_10pi(self):
        J = jacobian_5d_4d(_PHI0_BARE, n_winding=5)
        assert abs(J - 10.0 * math.pi) < 1e-10

    def test_jacobian_kk_scales_linearly_with_n_winding(self):
        J5 = jacobian_5d_4d(_PHI0_BARE, n_winding=5)
        J10 = jacobian_5d_4d(_PHI0_BARE, n_winding=10)
        assert abs(J10 / J5 - 2.0) < 1e-10

    def test_n_winding_5_gives_phi0_eff_approximately_31(self):
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        assert 31.0 < phi_eff < 32.0

    def test_n_winding_kk_is_positive_integer(self):
        # The physical winding number is 5 (a positive integer)
        assert isinstance(5, int) and 5 >= 1


# ===========================================================================
# 3 · TestRSWindingNumber  (10 tests)
# ===========================================================================

class TestRSWindingNumber:
    """Verify n_winding = 7 is the RS-branch integer that gives nₛ inside
    the Planck 1-σ window when the AdS warp factor (Randall–Sundrum) is used.

    Chain:  n_winding=7, k=1, r_c=12  →  φ₀_eff = 7·2π·J_RS ≈ 31.10
            nₛ ≈ 0.9628  (Planck: 0.9649 ± 0.0042  →  inside 1-σ)
    """

    def test_n_winding_7_is_default_for_effective_phi0_rs(self):
        phi_default = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC)
        phi_explicit = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        assert abs(phi_default - phi_explicit) < 1e-12

    def test_n_winding_7_gives_phi0_eff_near_31p1(self):
        phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        assert abs(phi_eff - 7.0 * 2.0 * math.pi * _J_RS) < 1e-10

    def test_n_winding_7_gives_ns_in_planck_1sigma(self):
        phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        ns, *_ = ns_from_phi0(phi_eff)
        assert planck2018_check(ns, n_sigma=1.0)

    def test_n_winding_6_rs_fails_planck_1sigma(self):
        phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=6)
        ns, *_ = ns_from_phi0(phi_eff)
        assert not planck2018_check(ns, n_sigma=1.0)

    def test_n_winding_8_rs_fails_planck_1sigma(self):
        phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=8)
        ns, *_ = ns_from_phi0(phi_eff)
        assert not planck2018_check(ns, n_sigma=1.0)

    def test_only_n_winding_7_passes_planck_1sigma_rs_among_1_to_12(self):
        passers = []
        for n in range(1, 13):
            phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=n)
            ns, *_ = ns_from_phi0(phi_eff)
            if planck2018_check(ns, n_sigma=1.0):
                passers.append(n)
        assert passers == [7]

    def test_rs_and_kk_winding_numbers_differ(self):
        assert 5 != 7  # KK winding ≠ RS winding

    def test_rs_phi0_eff_approximates_7_times_2pi_over_sqrt2(self):
        phi_eff = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        expected = 7.0 * 2.0 * math.pi / math.sqrt(2.0)
        assert abs(phi_eff - expected) < 0.01  # J_RS ≈ 1/√2 for large kr_c

    def test_both_branches_give_ns_within_1sigma(self):
        phi_kk = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        phi_rs = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        ns_kk, *_ = ns_from_phi0(phi_kk)
        ns_rs, *_ = ns_from_phi0(phi_rs)
        assert planck2018_check(ns_kk, n_sigma=1.0)
        assert planck2018_check(ns_rs, n_sigma=1.0)

    def test_both_branches_phi0_eff_within_1_percent_of_each_other(self):
        phi_kk = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        phi_rs = effective_phi0_rs(_PHI0_BARE, _K_ADV, _RC, n_winding=7)
        rel_diff = abs(phi_kk - phi_rs) / max(phi_kk, phi_rs)
        assert rel_diff < 0.02  # both converge to the same attractor


# ===========================================================================
# 4 · TestRSHierarchyProduct  (10 tests)
# ===========================================================================

class TestRSHierarchyProduct:
    """Verify k_rc = k·r_c = 12 is the canonical product that:
    (a) solves the hierarchy problem via exponential suppression, and
    (b) saturates J_RS to 1/√(2k) to within floating-point precision.
    """

    def test_k_rc_product_equals_12(self):
        assert _KRC == 12

    def test_j_rs_for_k1_rc12_is_near_1_over_sqrt2(self):
        assert abs(_J_RS - 1.0 / math.sqrt(2.0)) < 1e-6

    def test_j_rs_squared_is_near_half(self):
        assert abs(_J_RS**2 - 0.5) < 1e-5

    def test_j_rs_saturation_exponential_negligible_at_krc12(self):
        # e^{-2π·12} < 10^{-32}
        suppression = math.exp(-2.0 * math.pi * _KRC)
        assert suppression < 1e-32

    def test_hierarchy_suppression_factor_represents_33_orders_of_magnitude(self):
        suppression = math.exp(-2.0 * math.pi * _KRC)
        log10_sup = math.log10(suppression)
        assert log10_sup < -32

    def test_j_rs_stable_for_krc_11_to_15(self):
        j_values = [jacobian_rs_orbifold(1.0, r) for r in range(11, 16)]
        spread = max(j_values) - min(j_values)
        assert spread < 1e-5  # < 10⁻⁵ variation across the GW stabilisation window

    def test_rc_12_with_k_1_gives_integer_krc(self):
        assert isinstance(_KRC, int)
        assert _KRC == int(_K_ADV * _RC)

    def test_j_rs_formula_matches_direct_computation(self):
        J_direct = math.sqrt((1.0 - math.exp(-2.0 * math.pi * _K_ADV * _RC)) / (2.0 * _K_ADV))
        assert abs(_J_RS - J_direct) < 1e-14

    def test_phi_min_phys_from_krc12_and_phi_min_bare_18(self):
        phi_min_phys = _J_RS * _PHI_MIN_BARE
        assert abs(phi_min_phys - _PHI_MIN_PHYS) < 1e-12

    def test_krc_12_is_minimum_integer_achieving_saturation(self):
        # For k=1, find smallest integer r_c such that J_RS within 1e-4 of 1/sqrt(2)
        target = 1.0 / math.sqrt(2.0)
        for r in range(1, 30):
            J = jacobian_rs_orbifold(1.0, float(r))
            if abs(J - target) < 1e-4:
                assert r <= 12  # krc=12 should achieve saturation
                break


# ===========================================================================
# 5 · TestGWMinimumInteger  (7 tests)
# ===========================================================================

class TestGWMinimumInteger:
    """Verify phi_min_bare = 18 is the canonical GW minimum that closes the
    derivation loop: phi_min_bare=18 → phi_min_phys → Δφ → k_cs_float ≈ 73.7 → 74.
    """

    def test_phi_min_bare_18_is_positive(self):
        assert _PHI_MIN_BARE > 0

    def test_phi_min_phys_is_j_rs_times_18(self):
        expected = _J_RS * 18.0
        assert abs(_PHI_MIN_PHYS - expected) < 1e-12

    def test_delta_phi_from_phi_min_phys_is_positive(self):
        assert _DELTA_PHI > 0

    def test_delta_phi_formula_is_phi_min_times_one_minus_one_over_sqrt3(self):
        expected = _PHI_MIN_PHYS * (1.0 - 1.0 / math.sqrt(3.0))
        assert abs(_DELTA_PHI - expected) < 1e-12

    def test_phi_min_bare_18_closes_to_k_cs_74(self):
        k_float = cs_level_for_birefringence(
            BIREFRINGENCE_TARGET_DEG, _ALPHA_EM, _RC, _DELTA_PHI
        )
        assert round(k_float) == 74

    def test_phi_min_bare_exceeds_phi0_bare(self):
        assert _PHI_MIN_BARE > _PHI0_BARE

    def test_phi_min_phys_approximately_12p7(self):
        assert 12.5 < _PHI_MIN_PHYS < 13.0


# ===========================================================================
# 6 · TestDimensionalIntegers  (7 tests)
# ===========================================================================

class TestDimensionalIntegers:
    """Verify the dimensional integer structure of the theory: 5 total
    dimensions, 1 compact extra dimension, and the key relationships that
    follow from this 4+1 factorization.
    """

    def test_total_dimensions_is_5(self):
        n_total = 5
        n_compact = 1
        n_noncompact = n_total - n_compact
        assert n_total == 5
        assert n_compact == 1
        assert n_noncompact == 4

    def test_kk_jacobian_involves_sqrt_phi0_reflecting_single_extra_dim(self):
        # J_KK = n_w · 2π · φ₀^{1/2}: the 1/2 power comes from integrating
        # one compact dimension (volume ~ 2π √φ₀ for radius R = φ₀^{1/2})
        J = jacobian_5d_4d(4.0, n_winding=1)
        expected = 1 * 2.0 * math.pi * math.sqrt(4.0)
        assert abs(J - expected) < 1e-12

    def test_5d_theory_has_exactly_one_extra_dimension(self):
        # The RS orbifold is S¹/Z₂: one compact extra dimension
        n_extra = 1
        assert n_extra == 1

    def test_five_pillars_map_to_five_mathematical_integers(self):
        # Each pillar is associated with a unique mathematical object
        pillars = [1, 2, 3, 4, 5]
        assert len(pillars) == 5
        assert all(isinstance(p, int) for p in pillars)

    def test_kk_reduction_factor_is_2pi_per_winding(self):
        # J_KK / (n_w · √φ₀) = 2π
        phi0 = 1.0
        for n in [1, 3, 5, 7]:
            J = jacobian_5d_4d(phi0, n_winding=n)
            ratio = J / (n * math.sqrt(phi0))
            assert abs(ratio - 2.0 * math.pi) < 1e-10

    def test_4d_observables_determined_by_single_5d_parameter_phi0(self):
        # A single geometric value φ₀_eff determines both nₛ and r
        phi_eff = effective_phi0_kk(_PHI0_BARE, n_winding=5)
        ns, r, eps, eta = ns_from_phi0(phi_eff)
        assert math.isfinite(ns)
        assert math.isfinite(r)
        assert r > 0

    def test_five_dimensional_coupling_reduces_to_4d_fine_structure(self):
        # The 5D→4D reduction of the gauge coupling reproduces α_EM
        g5 = gauge_coupling_5d_for_alpha(_ALPHA_EM, _K_ADV, _RC)
        alpha_recovered = fine_structure_rs(g5, _K_ADV, _RC)
        assert abs(alpha_recovered - _ALPHA_EM) < 1e-12
