# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_branch_catalog.py
==============================
Tests for src/multiverse/branch_catalog.py.

Physical claims under test
---------------------------
1. The canonical (5, 7) branch has loss_function == 0 (lossless).
2. The (5, 6) branch is also lossless (the two-point prediction: both
   triply-viable states from birefringence_scenario_scan).
3. Every other (n₁, n₂) branch in the catalog has loss_function > 0 (lossy).
4. full_branch_catalog(n_max) returns exactly n_max*(n_max-1)/2 entries.
5. Entries are sorted by ascending k_cs.
6. classify_branch raises ValueError for invalid inputs.
7. catalog_summary correctly reports n_lossless, n_lossy, and lossless_pairs.

Test classes
-------------
TestClassifyBranchCanonical
    Detailed checks for the (5, 7) branch: L=0, k_cs=74, c_s=12/37, etc.

TestClassifyBranchOtherPairs
    Loss function is > 0 for all non-viable branches.

TestTwoPointPrediction
    Both lossless states are (5,6) and (5,7) — no other pair in n_max≤12.

TestFullBranchCatalog
    Catalog size, sort order, k_cs values, presence of canonical branch.

TestCatalogSummary
    Summary statistics: counts, lossless list, min/max/mean loss.

TestClassifyBranchEdgeCases
    ValueError on invalid inputs; commutative tests.

"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from src.multiverse.branch_catalog import (
    BranchRecord,
    classify_branch,
    catalog_summary,
    full_branch_catalog,
    lossless_branches,
    LOSSLESS_N1,
    LOSSLESS_N2,
    LOSSLESS_KCS,
    LOSSLESS_CS,
)
from src.core.braided_winding import R_BICEP_KECK_95
from src.core.inflation import PLANCK_NS_CENTRAL, PLANCK_NS_SIGMA


# ---------------------------------------------------------------------------
# Module-level constants matching the canonical branch
# ---------------------------------------------------------------------------

N1 = 5
N2 = 7
K_CS = 74
C_S_CANONICAL = 12.0 / 37.0


# ===========================================================================
# 1. TestClassifyBranchCanonical
# ===========================================================================

class TestClassifyBranchCanonical:
    """The canonical (5, 7) branch is the lossless main branch."""

    @pytest.fixture(scope="class")
    def canonical(self) -> BranchRecord:
        return classify_branch(N1, N2)

    def test_returns_branch_record(self, canonical):
        assert isinstance(canonical, BranchRecord)

    def test_n1_n2(self, canonical):
        assert canonical.n1 == N1
        assert canonical.n2 == N2

    def test_k_cs_is_74(self, canonical):
        assert canonical.k_cs == K_CS

    def test_k_cs_equals_module_constant(self, canonical):
        assert canonical.k_cs == LOSSLESS_KCS

    def test_k_cs_sum_of_squares(self, canonical):
        assert canonical.k_cs == N1**2 + N2**2

    def test_c_s_is_12_over_37(self, canonical):
        assert canonical.c_s == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_c_s_equals_module_constant(self, canonical):
        assert canonical.c_s == pytest.approx(LOSSLESS_CS, rel=1e-10)

    def test_ns_within_planck_1sigma(self, canonical):
        assert abs(canonical.ns - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_r_eff_below_bicep_keck(self, canonical):
        assert canonical.r_eff < R_BICEP_KECK_95

    def test_loss_function_is_zero(self, canonical):
        assert canonical.loss_function == pytest.approx(0.0, abs=1e-12)

    def test_is_lossless_true(self, canonical):
        assert canonical.is_lossless is True

    def test_beta_within_1sigma(self, canonical):
        """β must lie within the 1σ birefringence window."""
        assert abs(canonical.beta_deg - 0.35) < 0.14

    def test_ns_sigma_below_1(self, canonical):
        """(5,7) sits at 0.33σ from Planck — well within 1σ."""
        assert canonical.ns_sigma < 1.0

    def test_lossless_n1_constant(self):
        assert LOSSLESS_N1 == 5

    def test_lossless_n2_constant(self):
        assert LOSSLESS_N2 == 7

    def test_lossless_kcs_constant(self):
        assert LOSSLESS_KCS == 74


# ===========================================================================
# 2. TestClassifyBranchOtherPairs
# ===========================================================================

class TestClassifyBranchOtherPairs:
    """All non-triply-viable branches are lossy (loss_function > 0)."""

    _KNOWN_LOSSY_PAIRS = [(1, 2), (1, 3), (2, 3), (3, 4), (2, 5), (3, 7), (4, 5),
                    (4, 7), (6, 7), (7, 8), (8, 9), (9, 10)]

    @pytest.mark.parametrize("n1,n2", _KNOWN_LOSSY_PAIRS)
    def test_lossy_branch(self, n1, n2):
        b = classify_branch(n1, n2)
        assert b.loss_function > 0.0, (
            f"Branch ({n1},{n2}) should be lossy but L={b.loss_function}"
        )
        assert b.is_lossless is False

    def test_loss_monotone_with_ns_violation(self):
        """A branch with ns far from Planck should have high loss."""
        b_far = classify_branch(1, 2)  # n1=1: ns very far from Planck
        b_near = classify_branch(5, 7)  # canonical
        assert b_far.loss_function > b_near.loss_function

    def test_returns_branch_record_for_arbitrary_pair(self):
        b = classify_branch(3, 11)
        assert isinstance(b, BranchRecord)
        assert b.n1 == 3
        assert b.n2 == 11

    def test_k_cs_equals_sum_of_squares(self):
        """SOS resonance identity holds for all branches."""
        for n1, n2 in [(2, 5), (3, 7), (6, 8)]:
            b = classify_branch(n1, n2)
            assert b.k_cs == n1**2 + n2**2

    def test_c_s_positive_and_sub_unity(self):
        """Sound speed is always in (0, 1)."""
        for n1, n2 in [(1, 3), (4, 6), (7, 9)]:
            b = classify_branch(n1, n2)
            assert 0.0 < b.c_s < 1.0

    def test_r_eff_positive(self):
        for n1, n2 in [(2, 4), (3, 8)]:
            b = classify_branch(n1, n2)
            assert b.r_eff > 0.0

    def test_beta_positive(self):
        for n1, n2 in [(2, 3), (4, 9)]:
            b = classify_branch(n1, n2)
            assert b.beta_deg > 0.0


# ===========================================================================
# 3. TestTwoPointPrediction
# ===========================================================================

class TestTwoPointPrediction:
    """Only two lossless branches exist in the full n_max=12 catalog:
    (5,6) at k_cs=61 and (5,7) at k_cs=74.
    This matches the two-point prediction from birefringence_scenario_scan.
    """

    @pytest.fixture(scope="class")
    def catalog12(self):
        return full_branch_catalog(n_max=12)

    def test_exactly_two_lossless_branches(self, catalog12):
        ll = lossless_branches(catalog12)
        assert len(ll) == 2, (
            f"Expected 2 lossless branches, found {len(ll)}: "
            f"{[(b.n1, b.n2) for b in ll]}"
        )

    def test_canonical_57_is_lossless(self, catalog12):
        ll = lossless_branches(catalog12)
        pairs = {(b.n1, b.n2) for b in ll}
        assert (5, 7) in pairs

    def test_secondary_56_is_lossless(self, catalog12):
        """(5,6) is the second triply-viable state (k_cs=61, β≈0.290°)."""
        ll = lossless_branches(catalog12)
        pairs = {(b.n1, b.n2) for b in ll}
        assert (5, 6) in pairs

    def test_no_other_lossless_branches(self, catalog12):
        ll = lossless_branches(catalog12)
        for b in ll:
            assert (b.n1, b.n2) in {(5, 6), (5, 7)}, (
                f"Unexpected lossless branch ({b.n1},{b.n2})"
            )

    def test_56_k_cs_is_61(self, catalog12):
        ll = lossless_branches(catalog12)
        b56 = next(b for b in ll if b.n1 == 5 and b.n2 == 6)
        assert b56.k_cs == 61

    def test_57_k_cs_is_74(self, catalog12):
        ll = lossless_branches(catalog12)
        b57 = next(b for b in ll if b.n1 == 5 and b.n2 == 7)
        assert b57.k_cs == 74

    def test_56_beta_in_window(self, catalog12):
        """β for (5,6) must be inside the 1σ observational window."""
        ll = lossless_branches(catalog12)
        b56 = next(b for b in ll if b.n1 == 5 and b.n2 == 6)
        assert abs(b56.beta_deg - 0.35) < 0.14

    def test_57_beta_in_window(self, catalog12):
        ll = lossless_branches(catalog12)
        b57 = next(b for b in ll if b.n1 == 5 and b.n2 == 7)
        assert abs(b57.beta_deg - 0.35) < 0.14


# ===========================================================================
# 4. TestFullBranchCatalog
# ===========================================================================

class TestFullBranchCatalog:
    """full_branch_catalog returns the correct number and ordering of records."""

    def test_catalog_size_n4(self):
        # n_max=4: pairs (1,2),(1,3),(1,4),(2,3),(2,4),(3,4) = 6
        cat = full_branch_catalog(n_max=4)
        assert len(cat) == 6

    def test_catalog_size_n5(self):
        # n_max=5: C(5,2) = 10
        cat = full_branch_catalog(n_max=5)
        assert len(cat) == 10

    def test_catalog_size_n10(self):
        # n_max=10: C(10,2) = 45
        cat = full_branch_catalog(n_max=10)
        assert len(cat) == 45

    def test_catalog_size_formula(self):
        for n in range(2, 9):
            cat = full_branch_catalog(n_max=n)
            expected = n * (n - 1) // 2
            assert len(cat) == expected, f"n_max={n}: expected {expected}, got {len(cat)}"

    def test_sorted_by_kcs(self):
        cat = full_branch_catalog(n_max=8)
        kcs_values = [b.k_cs for b in cat]
        assert kcs_values == sorted(kcs_values)

    def test_all_entries_are_branch_record(self):
        cat = full_branch_catalog(n_max=5)
        for b in cat:
            assert isinstance(b, BranchRecord)

    def test_canonical_present_in_large_catalog(self):
        cat = full_branch_catalog(n_max=8)
        pairs = {(b.n1, b.n2) for b in cat}
        assert (5, 7) in pairs

    def test_canonical_absent_in_small_catalog(self):
        cat = full_branch_catalog(n_max=4)
        pairs = {(b.n1, b.n2) for b in cat}
        assert (5, 7) not in pairs

    def test_n1_always_less_than_n2(self):
        cat = full_branch_catalog(n_max=7)
        for b in cat:
            assert b.n1 < b.n2

    def test_k_cs_equals_sum_of_squares_everywhere(self):
        cat = full_branch_catalog(n_max=6)
        for b in cat:
            assert b.k_cs == b.n1**2 + b.n2**2

    def test_raises_for_n_max_less_than_2(self):
        with pytest.raises(ValueError):
            full_branch_catalog(n_max=1)

    def test_raises_for_n_max_zero(self):
        with pytest.raises(ValueError):
            full_branch_catalog(n_max=0)

    def test_loss_function_nonnegative_everywhere(self):
        cat = full_branch_catalog(n_max=8)
        for b in cat:
            assert b.loss_function >= 0.0


# ===========================================================================
# 5. TestCatalogSummary
# ===========================================================================

class TestCatalogSummary:
    """catalog_summary returns the expected aggregate statistics."""

    @pytest.fixture(scope="class")
    def summary8(self):
        return catalog_summary(full_branch_catalog(n_max=8))

    @pytest.fixture(scope="class")
    def summary12(self):
        return catalog_summary(full_branch_catalog(n_max=12))

    def test_returns_dict(self, summary8):
        assert isinstance(summary8, dict)

    def test_n_total_correct(self, summary8):
        # n_max=8: C(8,2)=28
        assert summary8["n_total"] == 28

    def test_n_lossless_plus_n_lossy_equals_n_total(self, summary8):
        assert summary8["n_lossless"] + summary8["n_lossy"] == summary8["n_total"]

    def test_canonical_present_flag(self, summary8):
        assert summary8["canonical_present"] is True

    def test_canonical_absent_flag_small(self):
        s = catalog_summary(full_branch_catalog(n_max=4))
        assert s["canonical_present"] is False

    def test_min_loss_is_zero(self, summary12):
        """The canonical lossless branch keeps the minimum at 0."""
        assert summary12["min_loss"] == pytest.approx(0.0, abs=1e-12)

    def test_max_loss_positive(self, summary8):
        assert summary8["max_loss"] > 0.0

    def test_mean_loss_positive(self, summary8):
        assert summary8["mean_loss"] > 0.0

    def test_lossless_pairs_in_summary12(self, summary12):
        pairs = set(tuple(p) for p in summary12["lossless_pairs"])
        assert (5, 6) in pairs
        assert (5, 7) in pairs

    def test_lossless_pairs_type(self, summary8):
        assert isinstance(summary8["lossless_pairs"], list)

    def test_two_lossless_in_catalog12(self, summary12):
        assert summary12["n_lossless"] == 2


# ===========================================================================
# 6. TestClassifyBranchEdgeCases
# ===========================================================================

class TestClassifyBranchEdgeCases:
    """Edge cases and error handling for classify_branch."""

    def test_raises_on_n1_zero(self):
        with pytest.raises(ValueError):
            classify_branch(0, 5)

    def test_raises_on_n2_equal_n1(self):
        with pytest.raises(ValueError):
            classify_branch(4, 4)

    def test_raises_on_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            classify_branch(7, 3)

    def test_raises_on_negative_n1(self):
        with pytest.raises(ValueError):
            classify_branch(-1, 5)

    def test_n1_1_n2_2_is_valid(self):
        b = classify_branch(1, 2)
        assert isinstance(b, BranchRecord)
        assert b.k_cs == 5  # 1²+2²

    def test_large_pair_does_not_raise(self):
        b = classify_branch(10, 15)
        assert isinstance(b, BranchRecord)
        assert b.loss_function >= 0.0

    def test_branch_record_fields_finite(self):
        for n1, n2 in [(1, 2), (3, 5), (5, 7), (8, 9)]:
            b = classify_branch(n1, n2)
            assert all(isinstance(v, (int, float, bool)) or v is None
                       for v in [b.c_s, b.ns, b.r_eff, b.beta_deg, b.loss_function])
            assert all(not (isinstance(v, float) and (v != v))  # no NaN
                       for v in [b.c_s, b.ns, b.r_eff, b.beta_deg, b.loss_function])
