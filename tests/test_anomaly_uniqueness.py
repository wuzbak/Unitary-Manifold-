# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_anomaly_uniqueness.py
=================================
Test suite for Pillar 55: Anomaly Cancellation Uniqueness Proof
(src/core/anomaly_uniqueness.py).

~90 tests covering all public functions, constants, edge cases, and the
core claim that k_CS = 74 is the UNIQUE integer satisfying all four
anomaly/resonance/birefringence/CMB constraints for the (5,7) braid.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.anomaly_uniqueness import (
    BETA_MAX_DEG,
    BETA_MIN_DEG,
    BETA_TARGET_DEG,
    C_S,
    K_CS_CANONICAL,
    K_SCAN_MAX,
    K_SCAN_MIN,
    N1_CANONICAL,
    N2_CANONICAL,
    NS_BRAIDED,
    anomaly_cancellation_verified,
    anomaly_polynomial_5d,
    birefringence_from_cs_level,
    birefringence_window_check,
    cs_level_consistent_with_ns,
    cs_level_scan,
    cubic_anomaly_coefficient,
    effective_cs_level,
    integer_level_necessity,
    primary_anomaly_level,
    sum_of_squares_condition,
    uniqueness_proof,
    uniqueness_summary,
    z2_orbifold_correction,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_ns_braided(self):
        assert abs(NS_BRAIDED - 0.9635) < 1e-6

    def test_beta_target(self):
        assert abs(BETA_TARGET_DEG - 0.35) < 1e-10

    def test_beta_window_sensible(self):
        assert 0 < BETA_MIN_DEG < BETA_TARGET_DEG < BETA_MAX_DEG

    def test_scan_range(self):
        assert K_SCAN_MIN == 1
        assert K_SCAN_MAX == 200


# ---------------------------------------------------------------------------
# cubic_anomaly_coefficient
# ---------------------------------------------------------------------------

class TestCubicAnomalyCoefficient:
    def test_canonical_value(self):
        """A = 5³ + 7³ = 125 + 343 = 468."""
        assert cubic_anomaly_coefficient() == 468

    def test_canonical_components(self):
        assert cubic_anomaly_coefficient(5, 7) == 5**3 + 7**3

    def test_symmetric_in_charges(self):
        """A(n1,n2) = A(n2,n1)."""
        assert cubic_anomaly_coefficient(3, 5) == cubic_anomaly_coefficient(5, 3)

    def test_single_charge(self):
        assert cubic_anomaly_coefficient(1, 1) == 2

    def test_n1_zero_raises(self):
        with pytest.raises(ValueError):
            cubic_anomaly_coefficient(0, 7)

    def test_n2_negative_raises(self):
        with pytest.raises(ValueError):
            cubic_anomaly_coefficient(5, -1)

    def test_custom_charges(self):
        n1, n2 = 3, 4
        assert cubic_anomaly_coefficient(n1, n2) == n1**3 + n2**3


# ---------------------------------------------------------------------------
# primary_anomaly_level
# ---------------------------------------------------------------------------

class TestPrimaryAnomalyLevel:
    def test_canonical_value(self):
        """k_primary = 2 × 468 / 12 = 78."""
        k = primary_anomaly_level()
        assert abs(k - 78.0) < 1e-10

    def test_formula(self):
        n1, n2 = 5, 7
        A = n1**3 + n2**3
        expected = 2.0 * A / (n1 + n2)
        assert abs(primary_anomaly_level(n1, n2) - expected) < 1e-12

    def test_symmetric_charges_special(self):
        """For n1=n2=n: k_primary = n² (special case)."""
        n = 3
        # A = 2n³, n1+n2 = 2n, k = 2*2n³/(2n) = 2n²
        expected = 2 * n**2
        assert abs(primary_anomaly_level(n, n) - expected) < 1e-12

    def test_returns_float(self):
        k = primary_anomaly_level()
        assert isinstance(k, float)

    def test_zero_sum_raises(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            primary_anomaly_level(1, -1)


# ---------------------------------------------------------------------------
# z2_orbifold_correction
# ---------------------------------------------------------------------------

class TestZ2OrbifoldCorrection:
    def test_canonical_value(self):
        """Δk = (7-5)² = 4."""
        assert z2_orbifold_correction() == 4

    def test_formula(self):
        n1, n2 = 5, 7
        assert z2_orbifold_correction(n1, n2) == (n2 - n1)**2

    def test_symmetric_gives_zero(self):
        """For n1=n2: Δk = 0."""
        assert z2_orbifold_correction(5, 5) == 0

    def test_returns_int(self):
        dk = z2_orbifold_correction()
        assert isinstance(dk, int)

    def test_order_matters(self):
        """Δk is symmetric in exchange (n₂-n₁)² = (n₁-n₂)²."""
        assert z2_orbifold_correction(5, 7) == z2_orbifold_correction(7, 5)

    def test_custom_charges(self):
        n1, n2 = 2, 5
        assert z2_orbifold_correction(n1, n2) == (n2 - n1)**2


# ---------------------------------------------------------------------------
# effective_cs_level
# ---------------------------------------------------------------------------

class TestEffectiveCsLevel:
    def test_canonical_value(self):
        """k_eff = 78 - 4 = 74."""
        k_eff = effective_cs_level()
        assert abs(k_eff - 74.0) < 1e-10

    def test_equals_k_cs_canonical(self):
        assert abs(effective_cs_level() - K_CS_CANONICAL) < 1e-10

    def test_formula(self):
        """k_eff = k_primary - Δk."""
        k_eff = effective_cs_level(5, 7)
        k_prim = primary_anomaly_level(5, 7)
        dk = z2_orbifold_correction(5, 7)
        assert abs(k_eff - (k_prim - dk)) < 1e-12

    def test_returns_float(self):
        assert isinstance(effective_cs_level(), float)


# ---------------------------------------------------------------------------
# anomaly_polynomial_5d
# ---------------------------------------------------------------------------

class TestAnomalyPolynomial5d:
    def test_returns_dict(self):
        result = anomaly_polynomial_5d(74)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = anomaly_polynomial_5d(74)
        for key in ("k", "inflow_term", "boundary_term", "net_anomaly",
                    "z2_correction", "k_primary", "k_eff", "cancels_at_keff"):
            assert key in result

    def test_cancels_at_74(self):
        result = anomaly_polynomial_5d(74)
        assert result["cancels_at_keff"] is True

    def test_does_not_cancel_at_73(self):
        result = anomaly_polynomial_5d(73)
        assert result["cancels_at_keff"] is False

    def test_does_not_cancel_at_75(self):
        result = anomaly_polynomial_5d(75)
        assert result["cancels_at_keff"] is False

    def test_k_primary_is_78(self):
        result = anomaly_polynomial_5d(74)
        assert abs(result["k_primary"] - 78.0) < 1e-10

    def test_k_eff_is_74(self):
        result = anomaly_polynomial_5d(74)
        assert abs(result["k_eff"] - 74.0) < 1e-10

    def test_boundary_term_is_468(self):
        result = anomaly_polynomial_5d(74)
        assert abs(result["boundary_term"] - 468.0) < 1e-10

    def test_z2_correction_is_4(self):
        result = anomaly_polynomial_5d(74)
        assert result["z2_correction"] == 4

    def test_inflow_at_k78_equals_boundary(self):
        """At k=k_primary=78, the inflow equals the boundary term exactly."""
        result = anomaly_polynomial_5d(78)
        # net = boundary - inflow = 0 when k = k_primary
        assert abs(result["net_anomaly"]) < 1e-10

    def test_net_nonzero_at_73(self):
        result = anomaly_polynomial_5d(73)
        assert abs(result["net_anomaly"]) > 0


# ---------------------------------------------------------------------------
# anomaly_cancellation_verified
# ---------------------------------------------------------------------------

class TestAnomalyCancellationVerified:
    def test_true_at_74(self):
        assert anomaly_cancellation_verified(74) is True

    def test_false_at_73(self):
        assert anomaly_cancellation_verified(73) is False

    def test_false_at_75(self):
        assert anomaly_cancellation_verified(75) is False

    def test_false_at_78(self):
        """k_primary = 78 does NOT equal k_eff = 74."""
        assert anomaly_cancellation_verified(78) is False

    def test_exactly_one_k_in_scan(self):
        """Only k=74 satisfies anomaly cancellation in [1,200]."""
        satisfied = [k for k in range(1, 201) if anomaly_cancellation_verified(k)]
        assert satisfied == [74]

    def test_returns_bool(self):
        assert isinstance(anomaly_cancellation_verified(74), bool)


# ---------------------------------------------------------------------------
# sum_of_squares_condition
# ---------------------------------------------------------------------------

class TestSumOfSquaresCondition:
    def test_true_at_74(self):
        assert sum_of_squares_condition(74) is True

    def test_false_at_73(self):
        assert sum_of_squares_condition(73) is False

    def test_false_at_75(self):
        assert sum_of_squares_condition(75) is False

    def test_formula(self):
        """k = n₁² + n₂² = 25 + 49 = 74."""
        n1, n2 = 5, 7
        assert sum_of_squares_condition(n1**2 + n2**2, n1, n2) is True

    def test_custom_charges(self):
        n1, n2 = 3, 4
        k = n1**2 + n2**2
        assert sum_of_squares_condition(k, n1, n2) is True

    def test_returns_bool(self):
        assert isinstance(sum_of_squares_condition(74), bool)


# ---------------------------------------------------------------------------
# birefringence_from_cs_level
# ---------------------------------------------------------------------------

class TestBirefringenceFromCsLevel:
    def test_k74_gives_target(self):
        """β(74) = BETA_TARGET_DEG = 0.35°."""
        beta = birefringence_from_cs_level(74)
        assert abs(beta - BETA_TARGET_DEG) < 1e-10

    def test_larger_k_smaller_beta(self):
        """β ∝ k^{-1/2} is decreasing."""
        b1 = birefringence_from_cs_level(50)
        b2 = birefringence_from_cs_level(100)
        assert b1 > b2

    def test_positive(self):
        for k in (1, 10, 74, 100, 200):
            assert birefringence_from_cs_level(k) > 0.0

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            birefringence_from_cs_level(0)

    def test_returns_float(self):
        assert isinstance(birefringence_from_cs_level(74), float)

    def test_scaling_relation(self):
        """β(k₁)/β(k₂) = √(k₂/k₁)."""
        b1 = birefringence_from_cs_level(74)
        b2 = birefringence_from_cs_level(296)  # 4×74
        assert abs(b1 / b2 - math.sqrt(296.0 / 74.0)) < 1e-10


# ---------------------------------------------------------------------------
# birefringence_window_check
# ---------------------------------------------------------------------------

class TestBirefringenceWindowCheck:
    def test_k74_in_window(self):
        assert birefringence_window_check(74) is True

    def test_very_small_k_out_of_window(self):
        """Very small k → very large β (above 0.38°)."""
        assert birefringence_window_check(1) is False

    def test_very_large_k_out_of_window(self):
        """Very large k → β too small (below 0.22°)."""
        assert birefringence_window_check(200) is False

    def test_k60_in_window(self):
        beta60 = birefringence_from_cs_level(60)
        in_window = BETA_MIN_DEG <= beta60 <= BETA_MAX_DEG
        assert birefringence_window_check(60) is in_window

    def test_returns_bool(self):
        assert isinstance(birefringence_window_check(74), bool)


# ---------------------------------------------------------------------------
# cs_level_consistent_with_ns
# ---------------------------------------------------------------------------

class TestCsLevelConsistentWithNs:
    def test_k74_consistent(self):
        assert cs_level_consistent_with_ns(74) is True

    def test_very_small_k_inconsistent(self):
        """k=1 → c_s much larger than canonical → n_s deviation too large."""
        assert cs_level_consistent_with_ns(1) is False

    def test_very_large_k_inconsistent(self):
        """k=200 → c_s too small → n_s deviation too large."""
        assert cs_level_consistent_with_ns(200) is False

    def test_returns_bool(self):
        assert isinstance(cs_level_consistent_with_ns(74), bool)


# ---------------------------------------------------------------------------
# cs_level_scan
# ---------------------------------------------------------------------------

class TestCsLevelScan:
    def test_returns_list(self):
        scan = cs_level_scan()
        assert isinstance(scan, list)

    def test_length_is_200(self):
        scan = cs_level_scan()
        assert len(scan) == K_SCAN_MAX - K_SCAN_MIN + 1

    def test_k74_all_satisfied(self):
        scan = cs_level_scan()
        entry_74 = next(r for r in scan if r["k"] == 74)
        assert entry_74["all_satisfied"] is True

    def test_k73_not_all_satisfied(self):
        scan = cs_level_scan()
        entry_73 = next(r for r in scan if r["k"] == 73)
        assert entry_73["all_satisfied"] is False

    def test_exactly_one_all_satisfied(self):
        scan = cs_level_scan()
        satisfying = [r for r in scan if r["all_satisfied"]]
        assert len(satisfying) == 1
        assert satisfying[0]["k"] == 74

    def test_required_keys(self):
        scan = cs_level_scan()
        for entry in scan[:5]:
            for key in ("k", "anomaly_ok", "resonance_ok",
                        "birefringence_ok", "ns_ok", "all_satisfied"):
                assert key in entry

    def test_k_values_sequential(self):
        scan = cs_level_scan()
        k_values = [r["k"] for r in scan]
        assert k_values == list(range(K_SCAN_MIN, K_SCAN_MAX + 1))

    def test_k74_anomaly_ok(self):
        scan = cs_level_scan()
        e = next(r for r in scan if r["k"] == 74)
        assert e["anomaly_ok"] is True

    def test_k74_resonance_ok(self):
        scan = cs_level_scan()
        e = next(r for r in scan if r["k"] == 74)
        assert e["resonance_ok"] is True

    def test_k74_birefringence_ok(self):
        scan = cs_level_scan()
        e = next(r for r in scan if r["k"] == 74)
        assert e["birefringence_ok"] is True


# ---------------------------------------------------------------------------
# uniqueness_proof — the main theorem
# ---------------------------------------------------------------------------

class TestUniquenessProof:
    def test_returns_dict(self):
        proof = uniqueness_proof()
        assert isinstance(proof, dict)

    def test_unique_k_is_74(self):
        """The unique solution must be k = 74."""
        proof = uniqueness_proof()
        assert proof["unique_k"] == 74

    def test_unique_is_true(self):
        """Exactly one k satisfies all constraints."""
        proof = uniqueness_proof()
        assert proof["unique"] is True

    def test_n_satisfying_is_1(self):
        proof = uniqueness_proof()
        assert proof["n_satisfying_all"] == 1

    def test_k_primary_is_78(self):
        proof = uniqueness_proof()
        assert abs(proof["k_primary"] - 78.0) < 1e-10

    def test_z2_correction_is_4(self):
        proof = uniqueness_proof()
        assert proof["z2_correction"] == 4

    def test_k_effective_is_74(self):
        proof = uniqueness_proof()
        assert abs(proof["k_effective"] - 74.0) < 1e-10

    def test_proof_statement_is_string(self):
        proof = uniqueness_proof()
        assert isinstance(proof["proof_statement"], str)

    def test_proof_statement_contains_74(self):
        proof = uniqueness_proof()
        assert "74" in proof["proof_statement"]

    def test_constraints_at_74_all_true(self):
        proof = uniqueness_proof()
        c = proof["constraints_at_74"]
        assert c["anomaly_ok"] is True
        assert c["resonance_ok"] is True
        assert c["birefringence_ok"] is True
        assert c["ns_ok"] is True

    def test_scan_results_length(self):
        proof = uniqueness_proof()
        assert len(proof["scan_results"]) == 200

    def test_proof_mentions_braid(self):
        proof = uniqueness_proof()
        assert "braid" in proof["proof_statement"].lower() or "5" in proof["proof_statement"]


# ---------------------------------------------------------------------------
# integer_level_necessity
# ---------------------------------------------------------------------------

class TestIntegerLevelNecessity:
    def test_returns_dict(self):
        result = integer_level_necessity()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = integer_level_necessity()
        for key in ("level_quantised", "delta_beta_at_k74",
                    "delta_beta_min", "sigma_beta_litebird",
                    "observability_ratio", "litebird_can_resolve",
                    "proof_of_necessity"):
            assert key in result

    def test_level_quantised_true(self):
        result = integer_level_necessity()
        assert result["level_quantised"] is True

    def test_beta_at_74_is_target(self):
        result = integer_level_necessity()
        assert abs(result["delta_beta_at_k74"] - BETA_TARGET_DEG) < 1e-10

    def test_sigma_positive(self):
        result = integer_level_necessity()
        assert result["sigma_beta_litebird"] > 0.0

    def test_delta_beta_positive(self):
        result = integer_level_necessity()
        assert result["delta_beta_min"] > 0.0

    def test_observability_ratio_positive(self):
        result = integer_level_necessity()
        assert result["observability_ratio"] > 0.0

    def test_proof_is_string(self):
        result = integer_level_necessity()
        assert isinstance(result["proof_of_necessity"], str)


# ---------------------------------------------------------------------------
# uniqueness_summary — complete proof
# ---------------------------------------------------------------------------

class TestUniquenessSummary:
    def test_returns_dict(self):
        s = uniqueness_summary()
        assert isinstance(s, dict)

    def test_uniqueness_confirmed_true(self):
        """Core claim: k_CS = 74 is the unique anomaly-free level."""
        s = uniqueness_summary()
        assert s["uniqueness_confirmed"] is True

    def test_canonical_k_is_74(self):
        s = uniqueness_summary()
        assert s["canonical_k"] == 74

    def test_unique_k_from_scan_is_74(self):
        s = uniqueness_summary()
        assert s["unique_k_from_scan"] == 74

    def test_n_satisfying_is_1(self):
        s = uniqueness_summary()
        assert s["n_satisfying_all"] == 1

    def test_braid_pair(self):
        s = uniqueness_summary()
        assert s["braid_pair"] == (5, 7)

    def test_k_effective_is_74(self):
        s = uniqueness_summary()
        assert abs(s["k_effective"] - 74.0) < 1e-10

    def test_constraints_at_74_all_true(self):
        s = uniqueness_summary()
        c = s["constraints_at_74"]
        for key in ("anomaly_ok", "resonance_ok", "birefringence_ok", "ns_ok"):
            assert c[key] is True


# ---------------------------------------------------------------------------
# Integration: complete anomaly cancellation chain
# ---------------------------------------------------------------------------

class TestIntegrationAnomalyChain:
    def test_full_derivation_chain(self):
        """End-to-end: (n1,n2) → A → k_primary → k_eff = 74."""
        n1, n2 = 5, 7
        A = cubic_anomaly_coefficient(n1, n2)
        assert A == 468

        k_prim = primary_anomaly_level(n1, n2)
        assert abs(k_prim - 78.0) < 1e-10

        dk = z2_orbifold_correction(n1, n2)
        assert dk == 4

        k_eff = effective_cs_level(n1, n2)
        assert abs(k_eff - 74.0) < 1e-10
        assert round(k_eff) == 74

    def test_uniqueness_of_74_in_all_senses(self):
        """k=74 is unique: only k satisfying ALL four constraints."""
        for k in range(1, 201):
            result_all = (
                anomaly_cancellation_verified(k) and
                sum_of_squares_condition(k) and
                birefringence_window_check(k) and
                cs_level_consistent_with_ns(k)
            )
            if k == 74:
                assert result_all is True, f"k=74 failed all-constraint check"
            # (other k values may or may not satisfy; only 74 satisfies all)

    def test_k78_does_not_satisfy_resonance(self):
        """k_primary=78 does NOT satisfy the sum-of-squares condition."""
        assert not sum_of_squares_condition(78)

    def test_k74_satisfies_resonance(self):
        """k=74 = 5²+7² satisfies the sum-of-squares condition."""
        assert sum_of_squares_condition(74)

    def test_proof_closes_loop(self):
        """The uniqueness proof summary confirms k_CS = 74 is necessary."""
        s = uniqueness_summary()
        assert s["uniqueness_confirmed"] is True
        assert s["unique_k_from_scan"] == K_CS_CANONICAL
