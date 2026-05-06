# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_action_minimizer.py
================================
Tests for src/core/action_minimizer.py — Pillar 189-D: Variational Braid Selection.
"""

from __future__ import annotations

import math
import pytest

from src.core.action_minimizer import (
    N_W,
    K_CS,
    N1_CANONICAL,
    N2_CANONICAL,
    ACTION_SCALE,
    cs_action,
    sum_of_squares_decompositions,
    scan_braid_pairs,
    action_landscape,
    canonical_pair_uniqueness,
    action_gap_to_alternatives,
    variational_braid_selection,
    pillar189d_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n1_canonical_is_5(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical_is_7(self):
        assert N2_CANONICAL == 7

    def test_action_scale_is_2pi2(self):
        assert ACTION_SCALE == pytest.approx(2.0 * math.pi**2, rel=1e-9)

    def test_canonical_pair_sum_of_squares_is_k_cs(self):
        # n₁² + n₂² = 5² + 7² = 74 = K_CS
        assert N1_CANONICAL**2 + N2_CANONICAL**2 == K_CS


# ===========================================================================
# cs_action
# ===========================================================================

class TestCsAction:
    def test_canonical_pair(self):
        s = cs_action(5, 7)
        assert s == pytest.approx(ACTION_SCALE * 74, rel=1e-9)

    def test_action_is_2pi2_times_k_eff(self):
        for m, n in [(1, 1), (2, 3), (5, 7), (3, 5), (7, 9)]:
            k_eff = m**2 + n**2
            expected = 2.0 * math.pi**2 * k_eff
            result = cs_action(m, n)
            assert result == pytest.approx(expected, rel=1e-9), \
                f"cs_action({m},{n}) = {result} ≠ {expected}"

    def test_action_is_positive(self):
        for m, n in [(1, 1), (3, 4), (5, 7), (10, 12)]:
            assert cs_action(m, n) > 0.0

    def test_symmetric_in_m_n(self):
        assert cs_action(5, 7) == pytest.approx(cs_action(7, 5), rel=1e-9)

    def test_invalid_m_zero_raises(self):
        with pytest.raises(ValueError):
            cs_action(0, 5)

    def test_invalid_n_zero_raises(self):
        with pytest.raises(ValueError):
            cs_action(5, 0)

    def test_invalid_negative_raises(self):
        with pytest.raises(ValueError):
            cs_action(-1, 5)

    def test_action_increases_with_k_eff(self):
        # cs_action(5,7) < cs_action(7,9) since 74 < 130
        assert cs_action(5, 7) < cs_action(7, 9)


# ===========================================================================
# sum_of_squares_decompositions
# ===========================================================================

class TestSumOfSquaresDecompositions:
    def test_k74_has_one_coprime_decomp(self):
        # 74 = 5² + 7² — unique coprime decomposition
        decomps = sum_of_squares_decompositions(74)
        assert len(decomps) == 1
        assert decomps[0] == (5, 7)

    def test_k74_canonical_pair(self):
        decomps = sum_of_squares_decompositions(74)
        assert (5, 7) in decomps

    def test_k25_has_decomposition(self):
        # 25 = 3² + 4² (coprime) — also 5² (but that's not two distinct)
        decomps = sum_of_squares_decompositions(25)
        assert (3, 4) in decomps

    def test_k50_has_decomposition(self):
        # 50 = 1² + 7² = 49+1, or 5² + 5² (not distinct)
        decomps = sum_of_squares_decompositions(50)
        assert (1, 7) in decomps

    def test_canonical_ordering_m_leq_n(self):
        for k in [5, 10, 25, 50, 74, 85]:
            decomps = sum_of_squares_decompositions(k, require_coprime=False, require_distinct=False)
            for m, n in decomps:
                assert m <= n, f"m={m} > n={n} for k={k}"

    def test_coprime_requirement(self):
        # k=50: 5²+5²=50 (gcd=5) should be excluded when require_coprime=True
        decomps_coprime = sum_of_squares_decompositions(50, require_coprime=True)
        for m, n in decomps_coprime:
            from math import gcd
            assert gcd(m, n) == 1, f"gcd({m},{n}) ≠ 1"

    def test_distinct_requirement(self):
        decomps = sum_of_squares_decompositions(50, require_distinct=True)
        for m, n in decomps:
            assert m != n, f"m={m} == n={n}"

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            sum_of_squares_decompositions(0)

    def test_invalid_m_max_raises(self):
        with pytest.raises(ValueError):
            sum_of_squares_decompositions(74, m_max=0)


# ===========================================================================
# scan_braid_pairs
# ===========================================================================

class TestScanBraidPairs:
    def setup_method(self):
        self.pairs = scan_braid_pairs(m_max=15)

    def test_returns_list(self):
        assert isinstance(self.pairs, list)

    def test_all_pairs_have_required_keys(self):
        for p in self.pairs:
            for key in ["m", "n", "k_eff", "action", "gcd", "coprime", "is_canonical"]:
                assert key in p, f"Missing key '{key}'"

    def test_canonical_pair_present(self):
        canonical = [p for p in self.pairs if p["is_canonical"]]
        assert len(canonical) == 1
        assert canonical[0]["m"] == 5
        assert canonical[0]["n"] == 7

    def test_sorted_by_k_eff(self):
        k_effs = [p["k_eff"] for p in self.pairs]
        assert k_effs == sorted(k_effs)

    def test_all_actions_positive(self):
        for p in self.pairs:
            assert p["action"] > 0.0

    def test_canonical_delta_action_zero(self):
        canonical = next(p for p in self.pairs if p["is_canonical"])
        assert canonical["delta_action"] == pytest.approx(0.0, abs=1e-9)

    def test_pairs_with_k_cs_marked(self):
        k_cs_pairs = [p for p in self.pairs if p["is_k_cs"]]
        assert len(k_cs_pairs) >= 1
        for p in k_cs_pairs:
            assert p["k_eff"] == K_CS

    def test_m_leq_n_convention(self):
        for p in self.pairs:
            assert p["m"] <= p["n"]

    def test_action_equals_2pi2_k_eff(self):
        for p in self.pairs:
            expected = 2.0 * math.pi**2 * p["k_eff"]
            assert p["action"] == pytest.approx(expected, rel=1e-9)

    def test_invalid_m_max_raises(self):
        with pytest.raises(ValueError):
            scan_braid_pairs(m_max=0)


# ===========================================================================
# action_landscape
# ===========================================================================

class TestActionLandscape:
    def setup_method(self):
        self.result = action_landscape()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_k_cs_correct(self):
        assert self.result["k_cs"] == K_CS

    def test_canonical_pair_present(self):
        assert self.result["n1_canonical"] == N1_CANONICAL
        assert self.result["n2_canonical"] == N2_CANONICAL

    def test_s_canonical_is_2pi2_times_74(self):
        expected = 2.0 * math.pi**2 * 74
        assert self.result["s_canonical"] == pytest.approx(expected, rel=1e-9)

    def test_k_cs_decompositions_has_one(self):
        # 74 has unique coprime decomposition (5,7)
        assert self.result["n_k_cs_decompositions"] == 1
        assert self.result["k_cs_decompositions"] == [(5, 7)]

    def test_n_coprime_distinct_pairs_positive(self):
        assert self.result["n_coprime_distinct_pairs_scanned"] > 0

    def test_lower_action_pairs_exist(self):
        assert self.result["n_pairs_with_lower_action"] > 0

    def test_higher_action_pairs_exist(self):
        assert self.result["n_pairs_with_higher_action"] > 0

    def test_nearby_pairs_list(self):
        assert isinstance(self.result["nearby_pairs"], list)


# ===========================================================================
# canonical_pair_uniqueness — THE KEY RESULT OF PILLAR 189-D
# ===========================================================================

class TestCanonicalPairUniqueness:
    def setup_method(self):
        self.result = canonical_pair_uniqueness()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_k_cs_correct(self):
        assert self.result["k_cs"] == K_CS

    def test_n_coprime_decompositions_is_1(self):
        # 74 has EXACTLY ONE coprime decomposition as sum of two distinct positive squares
        assert self.result["n_coprime_decompositions"] == 1

    def test_canonical_pair_is_unique(self):
        assert self.result["canonical_pair_is_unique"] is True

    def test_is_unique_coprime(self):
        assert self.result["is_unique_coprime"] is True

    def test_decompositions_contains_5_7(self):
        assert (5, 7) in self.result["coprime_distinct_decompositions"]

    def test_proof_statement_present(self):
        assert "proof_statement" in self.result
        assert "1" in self.result["proof_statement"]

    def test_number_theory_note_present(self):
        assert "number_theory_note" in self.result

    def test_all_decompositions_list(self):
        assert isinstance(self.result["all_distinct_decompositions"], list)

    def test_74_unique_coprime_in_range_15(self):
        # Only (5,7) satisfies 5²+7²=74 within [1,15]
        assert self.result["coprime_distinct_decompositions"] == [(5, 7)]


# ===========================================================================
# action_gap_to_alternatives
# ===========================================================================

class TestActionGapToAlternatives:
    def setup_method(self):
        self.result = action_gap_to_alternatives()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_canonical_pair_correct(self):
        assert self.result["canonical_pair"] == (N1_CANONICAL, N2_CANONICAL)

    def test_k_cs_correct(self):
        assert self.result["k_cs"] == K_CS

    def test_s_canonical_correct(self):
        assert self.result["s_canonical"] == pytest.approx(
            cs_action(N1_CANONICAL, N2_CANONICAL), rel=1e-9
        )

    def test_lower_pair_exists(self):
        assert self.result["nearest_lower_action_pair"] is not None

    def test_higher_pair_exists(self):
        assert self.result["nearest_higher_action_pair"] is not None

    def test_gap_to_lower_positive(self):
        # S(5,7) - S(lower) > 0 since lower has smaller k_eff
        if self.result["gap_to_lower_mev"] is not None:
            assert self.result["gap_to_lower_mev"] > 0.0

    def test_gap_to_higher_positive(self):
        # S(higher) - S(5,7) > 0 since higher has larger k_eff
        if self.result["gap_to_higher_mev"] is not None:
            assert self.result["gap_to_higher_mev"] > 0.0

    def test_comparisons_present(self):
        assert "comparison_with_alternatives" in self.result

    def test_interpretation_present(self):
        assert "interpretation" in self.result
        assert len(self.result["interpretation"]) > 20

    def test_3_5_comparison(self):
        comps = self.result["comparison_with_alternatives"]
        pairs = [c["pair"] for c in comps]
        assert (3, 5) in pairs

    def test_comparison_delta_action_for_lower_k(self):
        # (3,5) has k=34 < 74 → action gap < 0 (lower action)
        comps = self.result["comparison_with_alternatives"]
        pair_35 = next((c for c in comps if c["pair"] == (3, 5)), None)
        if pair_35:
            assert pair_35["delta_action"] < 0.0  # (3,5) has lower action


# ===========================================================================
# variational_braid_selection
# ===========================================================================

class TestVariationalBraidSelection:
    def setup_method(self):
        self.result = variational_braid_selection()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189d(self):
        assert self.result["pillar"] == "189-D"

    def test_version_is_v10(self):
        assert "v10" in self.result["version"]

    def test_canonical_pair(self):
        assert self.result["canonical_pair"] == (5, 7)

    def test_k_cs_correct(self):
        assert self.result["k_cs"] == K_CS

    def test_key_result_present(self):
        assert "key_result" in self.result
        assert len(self.result["key_result"]) > 20

    def test_honest_status_is_consistency_check(self):
        assert "CONSISTENCY" in self.result["honest_status"].upper()

    def test_honest_framing_mentions_open(self):
        assert "open" in self.result["honest_framing"].lower()

    def test_scaffold_tier_retained(self):
        assert self.result["scaffold_tier"]["retained"] is True

    def test_algebraic_tier_retained(self):
        assert self.result["algebraic_tier"]["retained"] is True

    def test_derivation_tier_is_consistency_check(self):
        assert "CONSISTENCY" in self.result["derivation_tier"]["status"].upper()

    def test_landscape_present(self):
        assert "landscape" in self.result

    def test_uniqueness_present(self):
        assert "uniqueness" in self.result

    def test_action_gap_present(self):
        assert "action_gap" in self.result


# ===========================================================================
# pillar189d_summary
# ===========================================================================

class TestPillar189dSummary:
    def setup_method(self):
        self.result = pillar189d_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189d(self):
        assert self.result["pillar"] == "189-D"

    def test_status_is_consistency_check(self):
        assert "CONSISTENCY" in self.result["status"].upper()

    def test_is_unique_true(self):
        assert self.result["is_unique"] is True

    def test_n_coprime_decompositions_is_1(self):
        assert self.result["n_coprime_decompositions_of_74"] == 1

    def test_honest_framing_present(self):
        assert "honest_framing" in self.result
        assert len(self.result["honest_framing"]) > 30

    def test_prior_modules_retained(self):
        retained = self.result["prior_modules_retained"]
        assert isinstance(retained, list)
        assert len(retained) >= 2
        assert any("95" in r or "braid_uniqueness" in r for r in retained)
        assert any("184" in r or "ckm_braid" in r for r in retained)

    def test_key_result_mentions_74(self):
        assert "74" in self.result["key_result"]

    def test_key_result_mentions_unique(self):
        assert "UNIQUE" in self.result["key_result"].upper()
