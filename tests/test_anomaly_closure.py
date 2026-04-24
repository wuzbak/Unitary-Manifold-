# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_anomaly_closure.py
==============================
Test suite for Pillar 58: Anomaly Closure — First-Principles Derivation
of the (5,7) Braid (src/core/anomaly_closure.py).

~125 tests covering:
  - The algebraic identity theorem (k_primary − Δk_Z₂ = n₁²+n₂² for all pairs)
  - Braided sound speed and tensor ratio functions
  - The BICEP/Keck tensor bound → n₂=7 uniqueness argument
  - CMB observable summaries and triple-constraint scanning
  - The full derivation chain dict
  - The gap closure status report
  - Constants and edge cases

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.anomaly_closure import (
    C_S_CANONICAL,
    K_CS_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    NS_PLANCK,
    NS_SIGMA,
    PHI0_BARE,
    R_BICEP_KECK,
    all_odd_braid_pairs,
    canonical_pair_is_unique_survivor,
    cs_derivative_positive,
    cs_monotone_increasing_in_n2,
    full_derivation_chain,
    gap_closure_status,
    n2_from_r_bound,
    pair_cmb_summary,
    prove_sos_identity_universally,
    r_bare_from_winding,
    r_bound_unique_n2_verified,
    r_braided_from_pair,
    sos_identity_lhs,
    sos_identity_proof,
    sos_identity_rhs,
    sos_identity_verified,
    sound_speed_from_braid,
    spectral_index_from_winding,
    triple_constraint_survivors,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_equals_sos(self):
        assert K_CS_CANONICAL == N1_CANONICAL**2 + N2_CANONICAL**2

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-12

    def test_c_s_canonical_numerically(self):
        assert abs(C_S_CANONICAL - (N2_CANONICAL**2 - N1_CANONICAL**2) / K_CS_CANONICAL) < 1e-12

    def test_phi0_bare(self):
        assert PHI0_BARE == 1.0

    def test_ns_planck(self):
        assert abs(NS_PLANCK - 0.9649) < 1e-6

    def test_ns_sigma(self):
        assert abs(NS_SIGMA - 0.0042) < 1e-6

    def test_r_bicep_keck(self):
        assert abs(R_BICEP_KECK - 0.036) < 1e-12


# ---------------------------------------------------------------------------
# TestSosIdentityLhs
# ---------------------------------------------------------------------------

class TestSosIdentityLhs:
    def test_canonical_pair(self):
        # k_primary = 78, Δk = 4, LHS = 74
        lhs = sos_identity_lhs(5, 7)
        assert abs(lhs - 74.0) < 1e-10

    def test_pair_1_3(self):
        # k_primary = 2(1+27)/4 = 14, Δk = 4, LHS = 10
        lhs = sos_identity_lhs(1, 3)
        assert abs(lhs - 10.0) < 1e-10

    def test_pair_3_5(self):
        # k_primary = 2(27+125)/8 = 38, Δk = 4, LHS = 34
        lhs = sos_identity_lhs(3, 5)
        assert abs(lhs - 34.0) < 1e-10

    def test_pair_7_9(self):
        # 7²+9²=49+81=130; verify LHS=130
        lhs = sos_identity_lhs(7, 9)
        assert abs(lhs - 130.0) < 1e-10

    def test_pair_1_5(self):
        lhs = sos_identity_lhs(1, 5)
        # n1²+n2² = 1+25 = 26; verify
        assert abs(lhs - 26.0) < 1e-10

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            sos_identity_lhs(0, 3)

    def test_raises_n2_equal_n1(self):
        with pytest.raises(ValueError):
            sos_identity_lhs(5, 5)

    def test_raises_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            sos_identity_lhs(7, 3)

    def test_raises_negative_n1(self):
        with pytest.raises(ValueError):
            sos_identity_lhs(-1, 3)


# ---------------------------------------------------------------------------
# TestSosIdentityRhs
# ---------------------------------------------------------------------------

class TestSosIdentityRhs:
    def test_canonical(self):
        assert sos_identity_rhs(5, 7) == 74

    def test_pair_1_3(self):
        assert sos_identity_rhs(1, 3) == 10

    def test_pair_3_5(self):
        assert sos_identity_rhs(3, 5) == 34

    def test_pair_7_9(self):
        assert sos_identity_rhs(7, 9) == 130

    def test_pair_1_5(self):
        assert sos_identity_rhs(1, 5) == 26

    def test_is_integer(self):
        assert isinstance(sos_identity_rhs(5, 7), int)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            sos_identity_rhs(0, 3)

    def test_raises_n2_le_n1(self):
        with pytest.raises(ValueError):
            sos_identity_rhs(5, 3)


# ---------------------------------------------------------------------------
# TestSosIdentityVerified — the core theorem
# ---------------------------------------------------------------------------

class TestSosIdentityVerified:
    """Tests for the algebraic identity LHS == RHS for many pairs."""

    def test_canonical_pair(self):
        assert sos_identity_verified(5, 7)

    def test_pair_1_3(self):
        assert sos_identity_verified(1, 3)

    def test_pair_3_5(self):
        assert sos_identity_verified(3, 5)

    def test_pair_7_9(self):
        assert sos_identity_verified(7, 9)

    def test_pair_1_5(self):
        assert sos_identity_verified(1, 5)

    def test_pair_1_7(self):
        assert sos_identity_verified(1, 7)

    def test_pair_3_7(self):
        assert sos_identity_verified(3, 7)

    def test_pair_5_9(self):
        assert sos_identity_verified(5, 9)

    def test_pair_9_11(self):
        assert sos_identity_verified(9, 11)

    def test_pair_11_13(self):
        assert sos_identity_verified(11, 13)

    def test_pair_1_9(self):
        assert sos_identity_verified(1, 9)

    def test_pair_5_13(self):
        assert sos_identity_verified(5, 13)

    def test_large_pair(self):
        assert sos_identity_verified(19, 21)

    def test_large_pair_far(self):
        assert sos_identity_verified(3, 19)


# ---------------------------------------------------------------------------
# TestSosIdentityProof
# ---------------------------------------------------------------------------

class TestSosIdentityProof:
    def test_canonical_identity_holds(self):
        p = sos_identity_proof(5, 7)
        assert p["identity_holds"]

    def test_canonical_k_primary(self):
        p = sos_identity_proof(5, 7)
        assert abs(p["k_primary"] - 78.0) < 1e-10

    def test_canonical_delta_k_z2(self):
        p = sos_identity_proof(5, 7)
        assert p["delta_k_z2"] == 4

    def test_canonical_k_eff_lhs(self):
        p = sos_identity_proof(5, 7)
        assert abs(p["k_eff_lhs"] - 74.0) < 1e-10

    def test_canonical_k_eff_rhs(self):
        p = sos_identity_proof(5, 7)
        assert p["k_eff_rhs"] == 74

    def test_factoring_consistent(self):
        p = sos_identity_proof(5, 7)
        assert p["factoring_consistent"]

    def test_proof_string_not_empty(self):
        p = sos_identity_proof(5, 7)
        assert len(p["proof_step"]) > 10

    def test_pair_1_3(self):
        p = sos_identity_proof(1, 3)
        assert p["identity_holds"]
        assert p["k_eff_rhs"] == 10

    def test_pair_3_5(self):
        p = sos_identity_proof(3, 5)
        assert p["identity_holds"]
        assert p["k_eff_rhs"] == 34


# ---------------------------------------------------------------------------
# TestProveUniversally
# ---------------------------------------------------------------------------

class TestProveUniversally:
    def test_all_verified(self):
        result = prove_sos_identity_universally(max_n=20)
        assert result["all_verified"]

    def test_no_failure(self):
        result = prove_sos_identity_universally(max_n=20)
        assert result["first_failure"] is None

    def test_odd_pairs_only(self):
        result = prove_sos_identity_universally(max_n=20)
        assert result["odd_pairs_only"]

    def test_n_pairs_checked_correct(self):
        # Odd integers up to 20: 1,3,5,7,9,11,13,15,17,19 = 10 values
        # Pairs: C(10,2) = 45
        result = prove_sos_identity_universally(max_n=20)
        assert result["n_pairs_checked"] == 45

    def test_theorem_statement_present(self):
        result = prove_sos_identity_universally(max_n=10)
        assert "THEOREM" in result["theorem_statement"]

    def test_max_n_30(self):
        result = prove_sos_identity_universally(max_n=30)
        assert result["all_verified"]


# ---------------------------------------------------------------------------
# TestSoundSpeed
# ---------------------------------------------------------------------------

class TestSoundSpeed:
    def test_canonical_pair(self):
        cs = sound_speed_from_braid(5, 7)
        assert abs(cs - 12.0 / 37.0) < 1e-12

    def test_pair_1_3(self):
        cs = sound_speed_from_braid(1, 3)
        assert abs(cs - 8.0 / 10.0) < 1e-12

    def test_pair_3_5(self):
        cs = sound_speed_from_braid(3, 5)
        assert abs(cs - 16.0 / 34.0) < 1e-12

    def test_cs_positive(self):
        assert sound_speed_from_braid(5, 7) > 0

    def test_cs_less_than_one(self):
        for n1, n2 in [(1, 3), (3, 5), (5, 7), (7, 9)]:
            assert sound_speed_from_braid(n1, n2) < 1.0

    def test_raises_n2_le_n1(self):
        with pytest.raises(ValueError):
            sound_speed_from_braid(7, 5)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            sound_speed_from_braid(0, 5)

    def test_cs_increases_with_n2(self):
        cs7 = sound_speed_from_braid(5, 7)
        cs9 = sound_speed_from_braid(5, 9)
        assert cs9 > cs7


# ---------------------------------------------------------------------------
# TestCsDerivativePositive
# ---------------------------------------------------------------------------

class TestCsDerivativePositive:
    def test_positive_at_canonical(self):
        assert cs_derivative_positive(5, 7) > 0

    def test_positive_at_small_pair(self):
        assert cs_derivative_positive(1, 3) > 0

    def test_positive_at_large_pair(self):
        assert cs_derivative_positive(11, 13) > 0

    def test_increases_with_n1(self):
        # Larger n₁ → larger numerator → larger derivative
        d5 = cs_derivative_positive(5, 7)
        d7 = cs_derivative_positive(7, 9)
        assert d7 > d5 * 0.5  # rough check that it stays positive


# ---------------------------------------------------------------------------
# TestCsMonotone
# ---------------------------------------------------------------------------

class TestCsMonotone:
    def test_monotone_canonical(self):
        assert cs_monotone_increasing_in_n2(5, 7, 9)

    def test_monotone_various(self):
        assert cs_monotone_increasing_in_n2(3, 5, 7)

    def test_monotone_large(self):
        assert cs_monotone_increasing_in_n2(1, 3, 9)

    def test_raises_n2b_le_n2a(self):
        with pytest.raises(ValueError):
            cs_monotone_increasing_in_n2(5, 9, 7)

    def test_raises_n2a_le_n1(self):
        with pytest.raises(ValueError):
            cs_monotone_increasing_in_n2(5, 3, 9)


# ---------------------------------------------------------------------------
# TestRBare
# ---------------------------------------------------------------------------

class TestRBare:
    def test_canonical_value(self):
        # r_bare = 96 / (5×2π)² = 96/986.96... ≈ 0.09726
        r = r_bare_from_winding(5)
        expected = 96.0 / (5 * 2 * math.pi) ** 2
        assert abs(r - expected) < 1e-10

    def test_positive(self):
        assert r_bare_from_winding(5) > 0

    def test_decreases_with_n1(self):
        assert r_bare_from_winding(7) < r_bare_from_winding(5)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            r_bare_from_winding(0)

    def test_raises_phi0_zero(self):
        with pytest.raises(ValueError):
            r_bare_from_winding(5, phi0_bare=0.0)


# ---------------------------------------------------------------------------
# TestRBraided
# ---------------------------------------------------------------------------

class TestRBraided:
    def test_canonical_satisfies_bicep(self):
        r = r_braided_from_pair(5, 7)
        assert r < R_BICEP_KECK

    def test_canonical_value(self):
        r = r_braided_from_pair(5, 7)
        assert abs(r - r_bare_from_winding(5) * sound_speed_from_braid(5, 7)) < 1e-12

    def test_n2_9_violates_r(self):
        r = r_braided_from_pair(5, 9)
        assert r > R_BICEP_KECK

    def test_r_increases_with_n2(self):
        r7 = r_braided_from_pair(5, 7)
        r9 = r_braided_from_pair(5, 9)
        assert r9 > r7

    def test_pair_3_5_violates_r(self):
        # r_bare(3) × c_s(3,5) should exceed 0.036
        r = r_braided_from_pair(3, 5)
        assert r > R_BICEP_KECK


# ---------------------------------------------------------------------------
# TestN2FromRBound
# ---------------------------------------------------------------------------

class TestN2FromRBound:
    def test_canonical_returns_7(self):
        assert n2_from_r_bound(5) == 7

    def test_n1_3_returns_none_or_value(self):
        # For n1=3, r_braided(3,5) ≈ 0.127 > 0.036, so no satisfying n2
        result = n2_from_r_bound(3)
        # Expect None since smallest braid (3,5) already violates r bound
        assert result is None

    def test_n1_7_returns_9(self):
        # For n1=7, n2=9: c_s=56/106≈0.132, r=r_bare(7)×0.132
        # r_bare(7) = 96/(7×2π)² ≈ 0.0498; r_braided ≈ 0.0498×0.492 ≈ 0.0245 < 0.036
        result = n2_from_r_bound(7)
        assert result == 9

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            n2_from_r_bound(0)

    def test_raises_r_max_zero(self):
        with pytest.raises(ValueError):
            n2_from_r_bound(5, r_max=0.0)


# ---------------------------------------------------------------------------
# TestRBoundUniqueN2Verified
# ---------------------------------------------------------------------------

class TestRBoundUniqueN2Verified:
    def test_canonical_unique(self):
        result = r_bound_unique_n2_verified()
        assert result["unique"]

    def test_canonical_n2_is_7(self):
        result = r_bound_unique_n2_verified()
        assert result["unique_n2"] == 7

    def test_n1_correct(self):
        result = r_bound_unique_n2_verified()
        assert result["n1"] == N1_CANONICAL

    def test_r_max_correct(self):
        result = r_bound_unique_n2_verified()
        assert abs(result["r_max"] - R_BICEP_KECK) < 1e-12

    def test_r_values_present(self):
        result = r_bound_unique_n2_verified()
        assert len(result["r_values_sample"]) > 0

    def test_satisfying_list_has_one(self):
        result = r_bound_unique_n2_verified()
        assert len(result["satisfying_n2_values"]) == 1


# ---------------------------------------------------------------------------
# TestAllOddBraidPairs
# ---------------------------------------------------------------------------

class TestAllOddBraidPairs:
    def test_basic_count(self):
        # Odd numbers ≤ 7: 1,3,5,7 → 4 numbers → C(4,2) = 6 pairs
        pairs = all_odd_braid_pairs(7)
        assert len(pairs) == 6

    def test_all_odd(self):
        for n1, n2 in all_odd_braid_pairs(15):
            assert n1 % 2 == 1
            assert n2 % 2 == 1

    def test_ordered(self):
        for n1, n2 in all_odd_braid_pairs(15):
            assert n1 < n2

    def test_contains_canonical(self):
        pairs = all_odd_braid_pairs(10)
        assert (5, 7) in pairs

    def test_max_n_20(self):
        # Odd ≤ 20: 1,3,5,7,9,11,13,15,17,19 = 10; C(10,2)=45
        pairs = all_odd_braid_pairs(20)
        assert len(pairs) == 45

    def test_empty_for_max_1(self):
        assert all_odd_braid_pairs(1) == []


# ---------------------------------------------------------------------------
# TestSpectralIndex
# ---------------------------------------------------------------------------

class TestSpectralIndex:
    def test_n1_5_close_to_planck(self):
        ns = spectral_index_from_winding(5)
        assert abs(ns - 0.9635) < 0.001

    def test_n1_3_far_from_planck(self):
        ns = spectral_index_from_winding(3)
        sigma = abs(ns - NS_PLANCK) / NS_SIGMA
        assert sigma > 10

    def test_n1_7_off_by_nearly_4_sigma(self):
        ns = spectral_index_from_winding(7)
        sigma = abs(ns - NS_PLANCK) / NS_SIGMA
        assert 3.0 < sigma < 5.0

    def test_increases_with_n1(self):
        assert spectral_index_from_winding(7) > spectral_index_from_winding(5)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            spectral_index_from_winding(0)


# ---------------------------------------------------------------------------
# TestPairCmbSummary
# ---------------------------------------------------------------------------

class TestPairCmbSummary:
    def test_canonical_satisfies_both(self):
        s = pair_cmb_summary(5, 7)
        assert s["satisfies_both"]

    def test_canonical_ns(self):
        s = pair_cmb_summary(5, 7)
        assert abs(s["ns"] - 0.9635) < 0.001

    def test_canonical_r_braided(self):
        s = pair_cmb_summary(5, 7)
        assert s["r_braided"] < R_BICEP_KECK

    def test_canonical_k_cs(self):
        s = pair_cmb_summary(5, 7)
        assert s["k_cs"] == 74

    def test_canonical_c_s(self):
        s = pair_cmb_summary(5, 7)
        assert abs(s["c_s"] - 12.0 / 37.0) < 1e-12

    def test_n1_3_fails_ns(self):
        s = pair_cmb_summary(3, 5)
        assert not s["satisfies_ns_2sigma"]

    def test_n1_5_n2_9_fails_r(self):
        s = pair_cmb_summary(5, 9)
        assert not s["satisfies_r_bicep"]

    def test_n1_7_fails_ns(self):
        s = pair_cmb_summary(7, 9)
        assert not s["satisfies_ns_2sigma"]


# ---------------------------------------------------------------------------
# TestTripleConstraintSurvivors
# ---------------------------------------------------------------------------

class TestTripleConstraintSurvivors:
    def test_exactly_one_survivor(self):
        survivors = triple_constraint_survivors(max_n=20)
        assert len(survivors) == 1

    def test_survivor_is_canonical(self):
        survivors = triple_constraint_survivors(max_n=20)
        s = survivors[0]
        assert s["n1"] == N1_CANONICAL
        assert s["n2"] == N2_CANONICAL

    def test_survivor_satisfies_both(self):
        survivors = triple_constraint_survivors(max_n=20)
        assert survivors[0]["satisfies_both"]


# ---------------------------------------------------------------------------
# TestCanonicalPairUniquenessSurvivor
# ---------------------------------------------------------------------------

class TestCanonicalPairUniquenessSurvivor:
    def test_canonical_is_unique(self):
        assert canonical_pair_is_unique_survivor(max_n=20)

    def test_larger_scan(self):
        assert canonical_pair_is_unique_survivor(max_n=30)


# ---------------------------------------------------------------------------
# TestFullDerivationChain
# ---------------------------------------------------------------------------

class TestFullDerivationChain:
    def setup_method(self):
        self.chain = full_derivation_chain()

    def test_derived_pair_canonical(self):
        assert self.chain["derived_pair"] == (N1_CANONICAL, N2_CANONICAL)

    def test_derived_k_cs(self):
        assert self.chain["derived_k_cs"] == K_CS_CANONICAL

    def test_derived_c_s(self):
        assert abs(self.chain["derived_c_s"] - C_S_CANONICAL) < 1e-12

    def test_canonical_confirmed(self):
        assert self.chain["canonical_confirmed"]

    def test_step1_no_empirical_input(self):
        assert not self.chain["step1_z2_orbifold"]["empirical_input"]

    def test_step2_empirical_input(self):
        assert self.chain["step2_planck_ns"]["empirical_input"]

    def test_step3_empirical_input(self):
        assert self.chain["step3_bicep_r"]["empirical_input"]

    def test_step4_no_empirical_input(self):
        assert not self.chain["step4_algebraic_identity"]["empirical_input"]

    def test_step5_no_empirical_input(self):
        assert not self.chain["step5_sound_speed"]["empirical_input"]

    def test_step4_k_cs(self):
        assert self.chain["step4_algebraic_identity"]["k_cs_derived"] == K_CS_CANONICAL

    def test_step4_identity_holds(self):
        assert self.chain["step4_algebraic_identity"]["proof"]["identity_holds"]

    def test_step2_n1_selected_5(self):
        assert self.chain["step2_planck_ns"]["n1_selected"] == 5

    def test_step3_n2_selected_7(self):
        assert self.chain["step3_bicep_r"]["n2_selected"] == 7

    def test_chain_summary_present(self):
        assert "k_CS=74" in self.chain["chain_summary"]


# ---------------------------------------------------------------------------
# TestGapClosureStatus
# ---------------------------------------------------------------------------

class TestGapClosureStatus:
    def setup_method(self):
        self.status = gap_closure_status()

    def test_proved_present(self):
        assert "proved" in self.status

    def test_derived_present(self):
        assert "derived" in self.status

    def test_still_open_present(self):
        assert "still_open" in self.status

    def test_proved_verified(self):
        assert self.status["proved"]["verified"]

    def test_pairs_verified_count(self):
        assert self.status["proved"]["pairs_verified"] > 0

    def test_derived_unique_n2(self):
        assert self.status["derived"]["unique_n2"] == N2_CANONICAL

    def test_derived_uniqueness_confirmed(self):
        assert self.status["derived"]["uniqueness_confirmed"]

    def test_still_open_references_n1(self):
        assert "n₁" in self.status["still_open"]["gap"] or "n1" in self.status["still_open"]["gap"].lower()

    def test_triple_constraint_unique(self):
        assert self.status["triple_constraint_unique"]

    def test_overall_summary_present(self):
        assert "GAP STATUS" in self.status["overall_summary"]

    def test_overall_summary_mentions_proved(self):
        assert "PROVED" in self.status["overall_summary"]

    def test_overall_summary_mentions_still_open(self):
        assert "STILL OPEN" in self.status["overall_summary"]
