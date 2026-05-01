# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_solitonic_charge.py — Test suite for Pillar 39: solitonic topological
charge quantization (src/core/solitonic_charge.py).

~105 tests covering all public functions, constants, edge cases, and
cross-module physics consistency.

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.solitonic_charge import (
    K_CS_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    NS_PLANCK,
    NS_SIGMA,
    NS_TARGET,
    PHI_0_BARE,
    Z2_ORDER,
    cs_level_from_soliton_pair,
    derive_canonical_parameters,
    effective_phi0,
    minimum_winding_for_planck,
    orbifold_allowed_windings,
    orbifold_uniqueness,
    resonance_identity_verified,
    soliton_energy,
    soliton_pair_energy,
    soliton_stability_criterion,
    spectral_index_from_phi0eff,
    topological_protection_gap,
    winding_number_from_cs_level,
)

_TWO_PI = 2.0 * math.pi


# ---------------------------------------------------------------------------
# TestSolitonEnergy
# ---------------------------------------------------------------------------
class TestSolitonEnergy:
    def test_n0_gives_zero(self):
        assert soliton_energy(0, 1.0) == 0.0

    def test_n1_R1(self):
        assert math.isclose(soliton_energy(1, 1.0), math.pi, rel_tol=1e-12)

    def test_n5_R1(self):
        expected = math.pi * 25
        assert math.isclose(soliton_energy(5, 1.0), expected, rel_tol=1e-12)

    def test_scales_inversely_with_R(self):
        e1 = soliton_energy(3, 1.0)
        e2 = soliton_energy(3, 2.0)
        assert math.isclose(e1 / e2, 2.0, rel_tol=1e-12)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            soliton_energy(-1, 1.0)

    def test_zero_R_raises(self):
        with pytest.raises(ValueError):
            soliton_energy(1, 0.0)

    def test_negative_R_raises(self):
        with pytest.raises(ValueError):
            soliton_energy(1, -0.5)


# ---------------------------------------------------------------------------
# TestOrbifoldAllowedWindings
# ---------------------------------------------------------------------------
class TestOrbifoldAllowedWindings:
    def test_max_n_10_returns_odd_only(self):
        result = orbifold_allowed_windings(10)
        assert result == [1, 3, 5, 7, 9]

    def test_max_n_1(self):
        assert orbifold_allowed_windings(1) == [1]

    def test_max_n_0_returns_empty(self):
        assert orbifold_allowed_windings(0) == []

    def test_max_n_negative_returns_empty(self):
        assert orbifold_allowed_windings(-5) == []

    def test_result_contains_5_and_7(self):
        result = orbifold_allowed_windings(20)
        assert 5 in result
        assert 7 in result

    def test_no_even_numbers(self):
        result = orbifold_allowed_windings(20)
        assert all(n % 2 == 1 for n in result)

    def test_sorted_ascending(self):
        result = orbifold_allowed_windings(15)
        assert result == sorted(result)


# ---------------------------------------------------------------------------
# TestEffectivePhi0
# ---------------------------------------------------------------------------
class TestEffectivePhi0:
    def test_n1_phi0_bare_1(self):
        assert math.isclose(effective_phi0(1, 1.0), _TWO_PI, rel_tol=1e-12)

    def test_n5_phi0_bare_1(self):
        expected = 5 * _TWO_PI
        assert math.isclose(effective_phi0(5, 1.0), expected, rel_tol=1e-12)

    def test_scales_linearly_with_n(self):
        phi3 = effective_phi0(3, 1.0)
        phi6 = effective_phi0(6, 1.0)
        assert math.isclose(phi6 / phi3, 2.0, rel_tol=1e-12)

    def test_scales_linearly_with_phi0_bare(self):
        phi_a = effective_phi0(5, 1.0)
        phi_b = effective_phi0(5, 2.0)
        assert math.isclose(phi_b / phi_a, 2.0, rel_tol=1e-12)

    def test_zero_n_raises(self):
        with pytest.raises(ValueError):
            effective_phi0(0, 1.0)

    def test_negative_phi0_raises(self):
        with pytest.raises(ValueError):
            effective_phi0(5, -1.0)

    def test_zero_phi0_raises(self):
        with pytest.raises(ValueError):
            effective_phi0(5, 0.0)


# ---------------------------------------------------------------------------
# TestSpectralIndexFromPhi0eff
# ---------------------------------------------------------------------------
class TestSpectralIndexFromPhi0eff:
    def test_large_phi0_approaches_1(self):
        ns = spectral_index_from_phi0eff(1e6)
        assert math.isclose(ns, 1.0, rel_tol=1e-9)

    def test_n5_gives_target(self):
        phi_eff = effective_phi0(5, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        # NS_TARGET = 0.9635; allow small floating-point margin
        assert math.isclose(ns, NS_TARGET, rel_tol=1e-4)

    def test_formula_correctness(self):
        phi = 10.0
        expected = 1.0 - 36.0 / (phi * phi)
        assert math.isclose(spectral_index_from_phi0eff(phi), expected, rel_tol=1e-12)

    def test_zero_phi_raises(self):
        with pytest.raises(ValueError):
            spectral_index_from_phi0eff(0.0)

    def test_negative_phi_raises(self):
        with pytest.raises(ValueError):
            spectral_index_from_phi0eff(-5.0)

    def test_n1_far_from_planck(self):
        phi_eff = effective_phi0(1, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        # n_w=1 → ns ≈ 0.088, far from Planck
        assert ns < 0.5


# ---------------------------------------------------------------------------
# TestMinimumWindingForPlanck
# ---------------------------------------------------------------------------
class TestMinimumWindingForPlanck:
    def test_canonical_returns_5(self):
        assert minimum_winding_for_planck() == 5

    def test_result_is_odd(self):
        result = minimum_winding_for_planck()
        assert result % 2 == 1

    def test_n3_not_within_2sigma(self):
        phi_eff = effective_phi0(3, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        assert abs(ns - NS_PLANCK) > 2.0 * NS_SIGMA

    def test_n1_not_within_2sigma(self):
        phi_eff = effective_phi0(1, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        assert abs(ns - NS_PLANCK) > 2.0 * NS_SIGMA

    def test_n5_within_2sigma(self):
        phi_eff = effective_phi0(5, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        assert abs(ns - NS_PLANCK) <= 2.0 * NS_SIGMA

    def test_n7_outside_2sigma(self):
        phi_eff = effective_phi0(7, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        assert abs(ns - NS_PLANCK) > 2.0 * NS_SIGMA

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            minimum_winding_for_planck(phi0_bare=0.0)

    def test_tight_tolerance_still_returns_5(self):
        # 1σ window: [0.9607, 0.9691]; n_w=5 → ns≈0.9635, within 1σ
        result = minimum_winding_for_planck(sigma_tolerance=1.0)
        assert result == 5


# ---------------------------------------------------------------------------
# TestCsLevelFromSolitonPair
# ---------------------------------------------------------------------------
class TestCsLevelFromSolitonPair:
    def test_canonical_5_7(self):
        assert cs_level_from_soliton_pair(5, 7) == 74

    def test_1_1(self):
        assert cs_level_from_soliton_pair(1, 1) == 2

    def test_3_4(self):
        assert cs_level_from_soliton_pair(3, 4) == 25

    def test_symmetry_order_matters(self):
        # n2 must be >= n1; (7,5) should raise
        with pytest.raises(ValueError):
            cs_level_from_soliton_pair(7, 5)

    def test_n1_zero_raises(self):
        with pytest.raises(ValueError):
            cs_level_from_soliton_pair(0, 5)

    def test_n1_negative_raises(self):
        with pytest.raises(ValueError):
            cs_level_from_soliton_pair(-1, 5)

    def test_equal_charges_allowed(self):
        # n1==n2 is allowed (n2 >= n1)
        assert cs_level_from_soliton_pair(3, 3) == 18


# ---------------------------------------------------------------------------
# TestResonanceIdentityVerified
# ---------------------------------------------------------------------------
class TestResonanceIdentityVerified:
    def test_canonical_true(self):
        assert resonance_identity_verified(5, 7, 74) is True

    def test_wrong_k_false(self):
        assert resonance_identity_verified(5, 7, 75) is False

    def test_1_1_2(self):
        assert resonance_identity_verified(1, 1, 2) is True

    def test_3_4_25(self):
        assert resonance_identity_verified(3, 4, 25) is True

    def test_3_4_26_false(self):
        assert resonance_identity_verified(3, 4, 26) is False


# ---------------------------------------------------------------------------
# TestSolitonPairEnergy
# ---------------------------------------------------------------------------
class TestSolitonPairEnergy:
    def test_canonical_5_7_R1(self):
        expected = math.pi * 74
        assert math.isclose(soliton_pair_energy(5, 7, 1.0), expected, rel_tol=1e-12)

    def test_equals_sum_of_individuals(self):
        n1, n2, R = 3, 5, 2.0
        pair = soliton_pair_energy(n1, n2, R)
        individual = soliton_energy(n1, R) + soliton_energy(n2, R)
        assert math.isclose(pair, individual, rel_tol=1e-12)

    def test_scales_inversely_R(self):
        e1 = soliton_pair_energy(5, 7, 1.0)
        e2 = soliton_pair_energy(5, 7, 2.0)
        assert math.isclose(e1 / e2, 2.0, rel_tol=1e-12)

    def test_invalid_R_raises(self):
        with pytest.raises(ValueError):
            soliton_pair_energy(5, 7, 0.0)

    def test_n2_less_than_n1_raises(self):
        with pytest.raises(ValueError):
            soliton_pair_energy(7, 5, 1.0)

    def test_n1_zero_raises(self):
        with pytest.raises(ValueError):
            soliton_pair_energy(0, 5, 1.0)


# ---------------------------------------------------------------------------
# TestTopologicalProtectionGap
# ---------------------------------------------------------------------------
class TestTopologicalProtectionGap:
    def test_canonical_n1_5(self):
        # ΔE = π(4·5−4)/R = π·16/R
        expected = math.pi * 16 / 1.0
        assert math.isclose(topological_protection_gap(5, 7, 1.0), expected, rel_tol=1e-12)

    def test_n1_1_uses_soliton_energy(self):
        # For n1=1, gap = π·1/R
        expected = math.pi / 1.0
        assert math.isclose(topological_protection_gap(1, 3, 1.0), expected, rel_tol=1e-12)

    def test_gap_positive(self):
        assert topological_protection_gap(5, 7, 1.0) > 0

    def test_scales_inversely_R(self):
        g1 = topological_protection_gap(5, 7, 1.0)
        g2 = topological_protection_gap(5, 7, 2.0)
        assert math.isclose(g1 / g2, 2.0, rel_tol=1e-12)

    def test_invalid_R_raises(self):
        with pytest.raises(ValueError):
            topological_protection_gap(5, 7, 0.0)

    def test_n2_less_than_n1_raises(self):
        with pytest.raises(ValueError):
            topological_protection_gap(7, 5, 1.0)


# ---------------------------------------------------------------------------
# TestOrbifoldUniqueness
# ---------------------------------------------------------------------------
class TestOrbifoldUniqueness:
    def test_n_w_derived_is_5(self):
        result = orbifold_uniqueness()
        assert result["n_w_derived"] == 5

    def test_k_cs_derived_is_74(self):
        result = orbifold_uniqueness()
        assert result["k_cs_derived"] == 74

    def test_ns_predicted_close_to_target(self):
        result = orbifold_uniqueness()
        assert math.isclose(result["ns_predicted"], NS_TARGET, rel_tol=1e-4)

    def test_planck_sigma_below_2(self):
        result = orbifold_uniqueness()
        assert result["planck_sigma"] <= 2.0

    def test_candidates_contains_only_5_in_range_1_21(self):
        result = orbifold_uniqueness()
        # Within 1..21 only n_w=5 is in 2σ
        assert result["candidates"] == [5]

    def test_candidates_are_odd(self):
        result = orbifold_uniqueness()
        assert all(c % 2 == 1 for c in result["candidates"])


# ---------------------------------------------------------------------------
# TestDeriveCanonicalParameters
# ---------------------------------------------------------------------------
class TestDeriveCanonicalParameters:
    def test_n_w_is_5(self):
        result = derive_canonical_parameters()
        assert result["n_w"] == 5

    def test_k_cs_is_74(self):
        result = derive_canonical_parameters()
        assert result["k_cs"] == 74

    def test_ns_close_to_target(self):
        result = derive_canonical_parameters()
        assert math.isclose(result["ns"], NS_TARGET, rel_tol=1e-4)

    def test_phi0_eff_correct(self):
        result = derive_canonical_parameters()
        expected = 5 * _TWO_PI
        assert math.isclose(result["phi0_eff"], expected, rel_tol=1e-12)

    def test_resonance_ok_true(self):
        result = derive_canonical_parameters()
        assert result["resonance_ok"] is True

    def test_n1_n2_values(self):
        result = derive_canonical_parameters()
        assert result["n1"] == 5
        assert result["n2"] == 7

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            derive_canonical_parameters(phi0_bare=0.0)


# ---------------------------------------------------------------------------
# TestSolitonStabilityCriterion
# ---------------------------------------------------------------------------
class TestSolitonStabilityCriterion:
    def test_zero_temp_always_stable(self):
        assert soliton_stability_criterion(5, 1.0, 0.0) is True

    def test_high_temp_unstable(self):
        # gap for n=5, R=1 → π·16; T=1000 > gap
        assert soliton_stability_criterion(5, 1.0, 1000.0) is False

    def test_n1_uses_soliton_energy(self):
        gap = math.pi / 1.0
        assert soliton_stability_criterion(1, 1.0, gap - 1e-10) is True
        assert soliton_stability_criterion(1, 1.0, gap + 1e-10) is False

    def test_n5_boundary(self):
        gap = math.pi * 16  # 4*5-4=16
        assert soliton_stability_criterion(5, 1.0, gap - 1e-10) is True
        assert soliton_stability_criterion(5, 1.0, gap + 1e-10) is False

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            soliton_stability_criterion(0, 1.0, 0.1)

    def test_invalid_R_raises(self):
        with pytest.raises(ValueError):
            soliton_stability_criterion(5, 0.0, 0.1)


# ---------------------------------------------------------------------------
# TestWindingNumberFromCsLevel
# ---------------------------------------------------------------------------
class TestWindingNumberFromCsLevel:
    def test_k74_returns_5_7(self):
        assert winding_number_from_cs_level(74) == (5, 7)

    def test_result_n1_less_than_n2(self):
        n1, n2 = winding_number_from_cs_level(74)
        assert n1 < n2

    def test_result_both_odd(self):
        n1, n2 = winding_number_from_cs_level(74)
        assert n1 % 2 == 1
        assert n2 % 2 == 1

    def test_sum_of_squares_matches(self):
        k = 74
        n1, n2 = winding_number_from_cs_level(k)
        assert n1 * n1 + n2 * n2 == k

    def test_invalid_k_raises(self):
        # k=3 cannot be expressed as sum of two odd squares
        with pytest.raises(ValueError):
            winding_number_from_cs_level(3)


# ---------------------------------------------------------------------------
# TestModuleConstants
# ---------------------------------------------------------------------------
class TestModuleConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_equals_sum_of_squares(self):
        assert K_CS_CANONICAL == N1_CANONICAL ** 2 + N2_CANONICAL ** 2

    def test_z2_order(self):
        assert Z2_ORDER == 2

    def test_phi0_bare(self):
        assert PHI_0_BARE == 1.0

    def test_ns_planck_range(self):
        # Planck 2018: 0.9649 ± 0.0042
        assert 0.96 < NS_PLANCK < 0.97

    def test_ns_sigma_positive(self):
        assert NS_SIGMA > 0

    def test_ns_target_in_planck_2sigma(self):
        assert abs(NS_TARGET - NS_PLANCK) <= 2.0 * NS_SIGMA


# ---------------------------------------------------------------------------
# TestPhysicsConsistency  (cross-function checks)
# ---------------------------------------------------------------------------
class TestPhysicsConsistency:
    def test_pair_energy_equals_k_cs_times_pi_over_R(self):
        R = 1.5
        e = soliton_pair_energy(N1_CANONICAL, N2_CANONICAL, R)
        expected = math.pi * K_CS_CANONICAL / R
        assert math.isclose(e, expected, rel_tol=1e-12)

    def test_orbifold_excludes_n2_and_n4(self):
        allowed = orbifold_allowed_windings(10)
        assert 2 not in allowed
        assert 4 not in allowed

    def test_minimum_winding_consistent_with_uniqueness(self):
        uniq = orbifold_uniqueness()
        min_w = minimum_winding_for_planck()
        assert uniq["n_w_derived"] == min_w

    def test_derive_consistent_with_individual_functions(self):
        params = derive_canonical_parameters()
        assert params["n_w"] == minimum_winding_for_planck()
        assert params["k_cs"] == cs_level_from_soliton_pair(params["n1"], params["n2"])
        assert math.isclose(
            params["ns"],
            spectral_index_from_phi0eff(effective_phi0(params["n_w"])),
            rel_tol=1e-12,
        )

    def test_n5_soliton_stable_at_low_T(self):
        assert soliton_stability_criterion(5, 1.0, 1.0) is True

    def test_winding_from_cs_inverts_cs_level(self):
        n1, n2 = winding_number_from_cs_level(K_CS_CANONICAL)
        assert cs_level_from_soliton_pair(n1, n2) == K_CS_CANONICAL

    def test_resonance_identity_for_all_odd_pairs_up_to_9(self):
        for n1 in range(1, 10, 2):
            for n2 in range(n1, 10, 2):
                k = cs_level_from_soliton_pair(n1, n2)
                assert resonance_identity_verified(n1, n2, k)

    def test_protection_gap_increases_with_n(self):
        R = 1.0
        gaps = [topological_protection_gap(n, n + 2, R) for n in range(3, 12, 2)]
        assert all(gaps[i] < gaps[i + 1] for i in range(len(gaps) - 1))

    def test_spectral_index_monotone_in_n(self):
        # ns should increase with n_w (as phi_eff grows, ns → 1)
        ns_vals = [
            spectral_index_from_phi0eff(effective_phi0(n, 1.0))
            for n in orbifold_allowed_windings(15)
        ]
        assert all(ns_vals[i] < ns_vals[i + 1] for i in range(len(ns_vals) - 1))

    def test_soliton_energy_additive(self):
        R = 2.0
        e5 = soliton_energy(5, R)
        e7 = soliton_energy(7, R)
        pair = soliton_pair_energy(5, 7, R)
        assert math.isclose(e5 + e7, pair, rel_tol=1e-12)

    def test_ns_n5_within_1sigma_of_target(self):
        phi_eff = effective_phi0(5, 1.0)
        ns = spectral_index_from_phi0eff(phi_eff)
        assert abs(ns - NS_TARGET) < NS_SIGMA
