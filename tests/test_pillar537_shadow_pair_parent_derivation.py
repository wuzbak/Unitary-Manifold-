# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 537 — Shadow-Pair Parent Derivation.

Covers all exported functions and constants.  ~42 tests.
"""

from __future__ import annotations

import math
import pytest

from src.core.pillar537_shadow_pair_parent_derivation import (
    # Functions
    parent_integer,
    shadow_pair,
    kcs_from_parent,
    cs_from_parent,
    parent_primality_check,
    verify_step_origin,
    shadow_pair_uniqueness_proof,
    # Constants
    N_BEFORE,
    N_GENERATIONS,
    Z2_REMOVES,
    N_W_OBSERVED,
    N_SHADOW_OBSERVED,
    K_CS_DERIVED,
    C_S_DERIVED,
    PARENT_PRIME,
    PILLAR_STATUS,
    PROOF_METHOD,
    BRAID_STEP_DERIVED,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_generations_is_3(self):
        assert N_GENERATIONS == 3

    def test_n_before_is_6(self):
        assert N_BEFORE == 6

    def test_z2_removes_is_1(self):
        assert Z2_REMOVES == 1

    def test_n_w_observed_is_5(self):
        assert N_W_OBSERVED == 5

    def test_n_shadow_observed_is_7(self):
        assert N_SHADOW_OBSERVED == 7

    def test_k_cs_derived_is_74(self):
        assert K_CS_DERIVED == 74

    def test_c_s_derived_is_12_over_37(self):
        assert abs(C_S_DERIVED - 12 / 37) < 1e-12

    def test_parent_prime_is_37(self):
        assert PARENT_PRIME == 37

    def test_braid_step_derived_is_2(self):
        assert BRAID_STEP_DERIVED == 2

    def test_pillar_status_hardgate(self):
        assert PILLAR_STATUS == "HARDGATE"

    def test_proof_method_label(self):
        assert PROOF_METHOD == "analytic_shadow_parent_derivation"

    def test_k_cs_algebraic_identity(self):
        """K_CS = (N_BEFORE-1)² + (N_BEFORE+1)² = 2(N_BEFORE²+1)."""
        lhs = (N_BEFORE - 1) ** 2 + (N_BEFORE + 1) ** 2
        rhs = 2 * (N_BEFORE ** 2 + 1)
        assert lhs == rhs == K_CS_DERIVED == 74

    def test_c_s_formula_consistency(self):
        """c_s = 2·N_BEFORE / (N_BEFORE²+1) = 12/37."""
        expected = 2 * N_BEFORE / (N_BEFORE ** 2 + 1)
        assert abs(C_S_DERIVED - expected) < 1e-12


# ---------------------------------------------------------------------------
# parent_integer
# ---------------------------------------------------------------------------

class TestParentInteger:
    def test_default_returns_6(self):
        assert parent_integer() == 6

    def test_n_gen_3(self):
        assert parent_integer(3) == 6

    def test_n_gen_1(self):
        assert parent_integer(1) == 2

    def test_n_gen_2(self):
        assert parent_integer(2) == 4

    def test_n_gen_4(self):
        assert parent_integer(4) == 8

    def test_always_even(self):
        for n in range(1, 10):
            assert parent_integer(n) % 2 == 0

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            parent_integer(0)

    def test_invalid_negative_raises(self):
        with pytest.raises(ValueError):
            parent_integer(-1)


# ---------------------------------------------------------------------------
# shadow_pair
# ---------------------------------------------------------------------------

class TestShadowPair:
    def test_default_returns_5_7(self):
        assert shadow_pair() == (5, 7)

    def test_n_before_6_z2_1(self):
        assert shadow_pair(6, 1) == (5, 7)

    def test_n_before_4_z2_1(self):
        assert shadow_pair(4, 1) == (3, 5)

    def test_n_before_8_z2_1(self):
        assert shadow_pair(8, 1) == (7, 9)

    def test_n_before_6_z2_0(self):
        assert shadow_pair(6, 0) == (6, 6)

    def test_symmetric_around_parent(self):
        for n in range(2, 10):
            p, q = shadow_pair(n, 1)
            assert (p + q) // 2 == n

    def test_step_equals_2_z2_removes(self):
        for z in range(0, 4):
            n = 2 * z + 4  # ensure n > z
            if n > z:
                p, q = shadow_pair(n, z)
                assert q - p == 2 * z

    def test_invalid_n_before_too_small(self):
        with pytest.raises(ValueError):
            shadow_pair(1, 1)

    def test_invalid_z2_negative(self):
        with pytest.raises(ValueError):
            shadow_pair(6, -1)

    def test_invalid_n_before_le_z2_removes(self):
        with pytest.raises(ValueError):
            shadow_pair(2, 3)


# ---------------------------------------------------------------------------
# kcs_from_parent
# ---------------------------------------------------------------------------

class TestKcsFromParent:
    def test_default_is_74(self):
        assert kcs_from_parent() == 74

    def test_n6_z1(self):
        assert kcs_from_parent(6, 1) == 74

    def test_matches_direct_formula(self):
        for n in range(2, 10):
            k = kcs_from_parent(n, 1)
            expected = (n - 1) ** 2 + (n + 1) ** 2
            assert k == expected

    def test_algebraic_identity_2n2_plus_2(self):
        """K_CS = 2(n² + z2²)."""
        for n in range(2, 8):
            k = kcs_from_parent(n, 1)
            assert k == 2 * (n ** 2 + 1)

    def test_n4_z1(self):
        assert kcs_from_parent(4, 1) == 3 ** 2 + 5 ** 2  # 9+25=34

    def test_regression_against_k_cs_derived(self):
        assert kcs_from_parent(N_BEFORE, Z2_REMOVES) == K_CS_DERIVED


# ---------------------------------------------------------------------------
# cs_from_parent
# ---------------------------------------------------------------------------

class TestCsFromParent:
    def test_default_is_12_over_37(self):
        assert abs(cs_from_parent() - 12 / 37) < 1e-12

    def test_n6_z1(self):
        assert abs(cs_from_parent(6, 1) - 12 / 37) < 1e-12

    def test_formula_2n_over_n2_plus_1(self):
        for n in range(2, 10):
            c = cs_from_parent(n, 1)
            expected = 2 * n / (n ** 2 + 1)
            assert abs(c - expected) < 1e-12

    def test_regression_against_c_s_derived(self):
        assert abs(cs_from_parent(N_BEFORE, Z2_REMOVES) - C_S_DERIVED) < 1e-12

    def test_matches_pillar267_c_s_observed(self):
        """c_s = 12/37 must match the Pillar 267 C_S_OBSERVED constant."""
        from src.core.pillar267_braid_uniqueness_instanton import C_S_OBSERVED
        assert abs(cs_from_parent() - C_S_OBSERVED) < 1e-12

    def test_matches_phi0_closure_c_s(self):
        """c_s = 12/37 must match phi0_closure.C_S."""
        from src.core.phi0_closure import C_S as C_S_PHI0
        assert abs(cs_from_parent() - C_S_PHI0) < 1e-12


# ---------------------------------------------------------------------------
# parent_primality_check
# ---------------------------------------------------------------------------

class TestParentPrimality:
    def test_default_n6_is_prime(self):
        assert parent_primality_check() is True

    def test_n6_37_is_prime(self):
        assert parent_primality_check(6) is True

    def test_n1_2_is_prime(self):
        assert parent_primality_check(1) is True  # 1²+1=2, prime

    def test_n2_5_is_prime(self):
        assert parent_primality_check(2) is True  # 2²+1=5, prime

    def test_n3_10_not_prime(self):
        assert parent_primality_check(3) is False  # 3²+1=10, not prime

    def test_parent_prime_value(self):
        assert PARENT_PRIME == 37
        assert parent_primality_check(6) is True


# ---------------------------------------------------------------------------
# verify_step_origin
# ---------------------------------------------------------------------------

class TestVerifyStepOrigin:
    def test_default_step_is_2(self):
        result = verify_step_origin()
        assert result["braid_step"] == 2

    def test_step_is_forced(self):
        result = verify_step_origin()
        assert result["is_forced"] is True

    def test_step_formula_string(self):
        result = verify_step_origin(6, 1)
        assert "2 × 1 = 2" in result["braid_step_formula"]

    def test_correct_n_w_and_n_shadow(self):
        result = verify_step_origin(6, 1)
        assert result["n_w"] == 5
        assert result["n_shadow"] == 7

    def test_n_before_in_result(self):
        result = verify_step_origin(6, 1)
        assert result["n_before"] == 6

    def test_matches_braid_step_derived(self):
        result = verify_step_origin(N_BEFORE, Z2_REMOVES)
        assert result["braid_step"] == BRAID_STEP_DERIVED


# ---------------------------------------------------------------------------
# shadow_pair_uniqueness_proof
# ---------------------------------------------------------------------------

class TestShadowPairUniquenessProof:
    @pytest.fixture(scope="class")
    def proof(self):
        return shadow_pair_uniqueness_proof()

    def test_pillar_number(self, proof):
        assert proof["pillar"] == 537

    def test_status_hardgate(self, proof):
        assert proof["status"] == "HARDGATE"

    def test_proof_method(self, proof):
        assert proof["proof_method"] == "analytic_shadow_parent_derivation"

    def test_n_before_is_6(self, proof):
        assert proof["n_before"] == 6

    def test_n_w_is_5(self, proof):
        assert proof["n_w"] == 5

    def test_n_shadow_is_7(self, proof):
        assert proof["n_shadow"] == 7

    def test_k_cs_is_74(self, proof):
        assert proof["K_CS"] == 74

    def test_c_s_is_12_over_37(self, proof):
        assert abs(proof["c_s"] - 12 / 37) < 1e-12

    def test_parent_prime_is_37(self, proof):
        assert proof["parent_prime"] == 37

    def test_parent_prime_is_prime(self, proof):
        assert proof["parent_prime_is_prime"] is True

    def test_identity_holds(self, proof):
        assert proof["K_CS_identity_holds"] is True

    def test_cs_formula_matches(self, proof):
        assert proof["c_s_formula_matches"] is True

    def test_braid_step_forced(self, proof):
        assert proof["braid_step_forced"] is True

    def test_verdict(self, proof):
        assert proof["verdict"] == "ANALYTIC_DERIVATION_COMPLETE"

    def test_closes_gap_reference(self, proof):
        assert "267" in proof["closes_gap_in"]

    def test_summary_contains_74(self, proof):
        assert "74" in proof["summary"]

    def test_summary_contains_37(self, proof):
        assert "37" in proof["summary"]


# ---------------------------------------------------------------------------
# Cross-module consistency regressions
# ---------------------------------------------------------------------------

class TestCrossModuleConsistency:
    def test_k_cs_matches_pillar267_k_cs_observed(self):
        from src.core.pillar267_braid_uniqueness_instanton import K_CS_OBSERVED
        assert K_CS_DERIVED == K_CS_OBSERVED

    def test_k_cs_matches_pillar325_k_cs(self):
        from src.core.pillar325_bbn_neff_kk_consistency import K_CS as K325
        assert K_CS_DERIVED == K325

    def test_n_w_matches_pillar267_n_w_selected(self):
        from src.core.pillar267_braid_uniqueness_instanton import N_W_SELECTED
        assert N_W_OBSERVED == N_W_SELECTED

    def test_shadow_pair_matches_minimum_step_braid(self):
        """shadow_pair(6,1)=(5,7); 7 = 5+2 matches the minimum-step braid formula."""
        p, q = shadow_pair(6, 1)
        # minimum-step: q = p + BRAID_STEP = 5 + 2 = 7
        assert q == p + 2

    def test_braid_step_matches_nw5_braid_step(self):
        from src.core.nw5_pure_theorem import BRAID_STEP
        assert BRAID_STEP_DERIVED == BRAID_STEP
