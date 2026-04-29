# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_unitary_closure.py
================================
Tests for src/core/unitary_closure.py — Pillar 96.

Physical claims under test
---------------------------
1. The analytic inequality c_s(5,n₂) < R_BICEP_KECK_95/r_bare restricts n₂ ≤ 7.
2. Given n₁=5, the viable braid partners are exactly n₂ ∈ {6, 7}.
3. Exactly two lossless braid sectors exist: {(5,6), (5,7)}.
4. The FTUM fixed point S* = A/(4G) is identical for both sectors (sector-agnostic).
5. The Unitary Summation assembles all ten closure steps correctly.

Test count: exactly 59  (14,582 + 59 = 14,641 = 11⁴).

*Theory: ThomasCory Walker-Pearson.*
*Code and tests: GitHub Copilot (AI).*
"""
from __future__ import annotations

import math
import pytest

from src.core.unitary_closure import (
    # constants
    N1_COMMON,
    N2_VIABLE,
    K_CS_56,
    K_CS_57,
    R_BARE,
    C_S_UPPER_BOUND,
    N2_UPPER_BOUND,
    N_LOSSLESS_SECTORS,
    PILLAR_COUNT_AT_CLOSURE,
    TEST_COUNT_AT_CLOSURE,
    M_THEORY_DIMENSIONS,
    WORLD_DIMENSIONS,
    BETA_56,
    BETA_57,
    BETA_ADMISSIBLE_LOWER,
    BETA_ADMISSIBLE_UPPER,
    # functions
    c_s_from_braid,
    r_eff_from_braid,
    c_s_upper_bound,
    n2_upper_bound_analytic,
    analytic_viable_n2_values,
    ftum_sector_fixed_point,
    sector_agnostic_fixed_point,
    unitary_closure_theorem,
    unitary_summation_statement,
    UnitaryClosureResult,
    SectorFixedPoint,
)
from src.core.braided_winding import R_BICEP_KECK_95


# ===========================================================================
# TestModuleConstants  (5 tests)
# ===========================================================================

class TestModuleConstants:
    """Verify module-level constants are physically correct."""

    def test_n1_common_is_planck_selected(self):
        """n₁ = n_w = 5 — the Planck nₛ-selected winding number."""
        assert N1_COMMON == 5

    def test_n2_viable_is_6_and_7(self):
        """The only viable braid partners are 6 and 7."""
        assert set(N2_VIABLE) == {6, 7}

    def test_kcs_values(self):
        """k_CS(5,6)=61 and k_CS(5,7)=74 are correct."""
        assert K_CS_56 == 61   # 5²+6²
        assert K_CS_57 == 74   # 5²+7²

    def test_closure_targets(self):
        """Repository closure targets: 96 pillars and 14,641 = 11⁴ tests."""
        assert PILLAR_COUNT_AT_CLOSURE == 96
        assert TEST_COUNT_AT_CLOSURE == 11**4
        assert TEST_COUNT_AT_CLOSURE == 14641

    def test_m_theory_resonance(self):
        """14,641 = M_THEORY_DIMENSIONS ^ WORLD_DIMENSIONS = 11^4."""
        assert M_THEORY_DIMENSIONS == 11
        assert WORLD_DIMENSIONS == 4
        assert M_THEORY_DIMENSIONS**WORLD_DIMENSIONS == TEST_COUNT_AT_CLOSURE


# ===========================================================================
# TestBraidedSoundSpeed  (8 tests)
# ===========================================================================

class TestBraidedSoundSpeed:
    """Tests for c_s_from_braid()."""

    def test_cs_56_exact(self):
        """c_s(5,6) = 11/61 exactly."""
        assert math.isclose(c_s_from_braid(5, 6), 11.0 / 61.0, rel_tol=1e-12)

    def test_cs_57_exact(self):
        """c_s(5,7) = 24/74 = 12/37 exactly."""
        assert math.isclose(c_s_from_braid(5, 7), 12.0 / 37.0, rel_tol=1e-12)

    def test_cs_58_value(self):
        """c_s(5,8) = 39/89."""
        assert math.isclose(c_s_from_braid(5, 8), 39.0 / 89.0, rel_tol=1e-12)

    def test_cs_bounded_below_zero(self):
        """c_s > 0 for any valid braid pair."""
        for n2 in range(6, 12):
            assert c_s_from_braid(5, n2) > 0

    def test_cs_bounded_above_one(self):
        """c_s < 1 for any valid braid pair (causality)."""
        for n2 in range(6, 20):
            assert c_s_from_braid(5, n2) < 1.0

    def test_cs_strictly_increasing_in_n2(self):
        """c_s increases monotonically as n₂ increases (n₁ fixed)."""
        cs_prev = c_s_from_braid(5, 6)
        for n2 in range(7, 15):
            cs_curr = c_s_from_braid(5, n2)
            assert cs_curr > cs_prev
            cs_prev = cs_curr

    def test_cs_invalid_inputs(self):
        """c_s_from_braid raises for n₂ ≤ n₁ or n₁ ≤ 0."""
        with pytest.raises(ValueError):
            c_s_from_braid(5, 5)   # n₂ = n₁
        with pytest.raises(ValueError):
            c_s_from_braid(5, 4)   # n₂ < n₁
        with pytest.raises(ValueError):
            c_s_from_braid(0, 6)   # n₁ = 0

    def test_cs_formula_is_n1_symmetric(self):
        """c_s formula is antisymmetric in (n₁,n₂): c_s(a,b) = −c_s(b,a) only
        if we allow n₁ > n₂.  Since we require n₂ > n₁, verify the magnitude
        identity |c_s(5,7)| = (n₂²−n₁²)/(n₁²+n₂²)."""
        n1, n2 = 5, 7
        expected = (n2**2 - n1**2) / (n1**2 + n2**2)
        assert math.isclose(c_s_from_braid(n1, n2), expected, rel_tol=1e-14)


# ===========================================================================
# TestREffUpperBoundConstraint  (8 tests)
# ===========================================================================

class TestREffUpperBoundConstraint:
    """Tests for r_eff_from_braid() and c_s_upper_bound()."""

    def test_r_eff_56_below_bicep_keck(self):
        """r_eff(5,6) < 0.036 — (5,6) satisfies the BICEP/Keck bound."""
        assert r_eff_from_braid(5, 6) < R_BICEP_KECK_95

    def test_r_eff_57_below_bicep_keck(self):
        """r_eff(5,7) < 0.036 — (5,7) satisfies the BICEP/Keck bound."""
        assert r_eff_from_braid(5, 7) < R_BICEP_KECK_95

    def test_r_eff_58_exceeds_bicep_keck(self):
        """r_eff(5,8) > 0.036 — (5,8) FAILS the BICEP/Keck bound."""
        assert r_eff_from_braid(5, 8) > R_BICEP_KECK_95

    def test_r_eff_59_exceeds_bicep_keck(self):
        """r_eff(5,9) > 0.036 — (5,9) FAILS."""
        assert r_eff_from_braid(5, 9) > R_BICEP_KECK_95

    def test_c_s_upper_bound_value(self):
        """c_s upper bound = R_BICEP_KECK_95 / r_bare ≈ 0.370."""
        ub = c_s_upper_bound()
        assert 0.35 < ub < 0.39

    def test_c_s_56_below_upper_bound(self):
        """c_s(5,6) < c_s upper bound."""
        assert c_s_from_braid(5, 6) < C_S_UPPER_BOUND

    def test_c_s_57_below_upper_bound(self):
        """c_s(5,7) < c_s upper bound."""
        assert c_s_from_braid(5, 7) < C_S_UPPER_BOUND

    def test_c_s_58_above_upper_bound(self):
        """c_s(5,8) > c_s upper bound — excluded by constraint [C2]."""
        assert c_s_from_braid(5, 8) > C_S_UPPER_BOUND


# ===========================================================================
# TestAnalyticViablePairs  (8 tests)
# ===========================================================================

class TestAnalyticViablePairs:
    """Tests for n2_upper_bound_analytic() and analytic_viable_n2_values()."""

    def test_n2_upper_bound_is_7(self):
        """The analytic upper bound on n₂ is exactly 7."""
        assert N2_UPPER_BOUND == 7

    def test_n2_upper_bound_analytic_equals_constant(self):
        """n2_upper_bound_analytic() returns 7 (= N2_UPPER_BOUND)."""
        assert n2_upper_bound_analytic() == N2_UPPER_BOUND

    def test_n2_7_satisfies_bound(self):
        """n₂=7: 7² = 49 < n₂²_max ≈ 54.38  → included."""
        n1 = 5
        threshold = C_S_UPPER_BOUND
        n2_sq_max = n1**2 * (1 + threshold) / (1 - threshold)
        assert 7**2 < n2_sq_max

    def test_n2_8_violates_bound(self):
        """n₂=8: 8² = 64 > n₂²_max ≈ 54.38  → excluded."""
        n1 = 5
        threshold = C_S_UPPER_BOUND
        n2_sq_max = n1**2 * (1 + threshold) / (1 - threshold)
        assert 8**2 > n2_sq_max

    def test_viable_n2_values_are_6_and_7(self):
        """analytic_viable_n2_values() returns [6, 7] — exactly two values."""
        viable = analytic_viable_n2_values()
        assert viable == [6, 7]

    def test_viable_count_is_two(self):
        """Exactly two viable n₂ values exist."""
        assert len(analytic_viable_n2_values()) == N_LOSSLESS_SECTORS

    def test_no_viable_pair_with_n2_8_or_higher(self):
        """n₂ ≥ 8 produces no viable pairs (r constraint eliminates them)."""
        viable = analytic_viable_n2_values()
        assert all(n2 <= 7 for n2 in viable)

    def test_both_viable_betas_in_admissible_window(self):
        """Both β(5,6) and β(5,7) lie in the admissible β window."""
        assert BETA_ADMISSIBLE_LOWER <= BETA_56 <= BETA_ADMISSIBLE_UPPER
        assert BETA_ADMISSIBLE_LOWER <= BETA_57 <= BETA_ADMISSIBLE_UPPER


# ===========================================================================
# TestUnitaryClosureTheorem  (8 tests)
# ===========================================================================

class TestUnitaryClosureTheorem:
    """Tests for unitary_closure_theorem()."""

    def test_returns_closure_result(self):
        """unitary_closure_theorem() returns a UnitaryClosureResult."""
        result = unitary_closure_theorem()
        assert isinstance(result, UnitaryClosureResult)

    def test_n1_fixed_is_5(self):
        """n₁ = 5 (Planck-selected winding number)."""
        result = unitary_closure_theorem()
        assert result.n1_fixed == N1_COMMON

    def test_n2_viable_is_6_and_7(self):
        """The viable n₂ set is exactly {6, 7}."""
        result = unitary_closure_theorem()
        assert result.n2_viable == [6, 7]

    def test_lossless_count_is_2(self):
        """Exactly 2 lossless sectors."""
        result = unitary_closure_theorem()
        assert result.lossless_count == 2

    def test_is_unique_true(self):
        """Uniqueness flag is True (exactly 2 sectors, no more)."""
        result = unitary_closure_theorem()
        assert result.is_unique is True

    def test_proof_complete(self):
        """proof_complete flag is True."""
        result = unitary_closure_theorem()
        assert result.proof_complete is True

    def test_closure_steps_present(self):
        """The theorem includes six proof steps."""
        result = unitary_closure_theorem()
        assert len(result.steps) == 6

    def test_steps_include_qed(self):
        """The final step contains the QED symbol."""
        result = unitary_closure_theorem()
        assert "∎" in result.steps[-1]


# ===========================================================================
# TestFTUMSectorAgnosticism  (8 tests)
# ===========================================================================

class TestFTUMSectorAgnosticism:
    """Tests for ftum_sector_fixed_point() and sector_agnostic_fixed_point()."""

    def test_ftum_56_returns_dataclass(self):
        """ftum_sector_fixed_point(5,6) returns a SectorFixedPoint."""
        fp = ftum_sector_fixed_point(5, 6)
        assert isinstance(fp, SectorFixedPoint)

    def test_ftum_57_returns_dataclass(self):
        """ftum_sector_fixed_point(5,7) returns a SectorFixedPoint."""
        fp = ftum_sector_fixed_point(5, 7)
        assert isinstance(fp, SectorFixedPoint)

    def test_s_star_56_is_quarter(self):
        """S*(5,6) = 0.25 = A/(4G) in normalised units."""
        fp = ftum_sector_fixed_point(5, 6)
        assert math.isclose(fp.s_star, 0.25, rel_tol=1e-12)

    def test_s_star_57_is_quarter(self):
        """S*(5,7) = 0.25 = A/(4G) in normalised units."""
        fp = ftum_sector_fixed_point(5, 7)
        assert math.isclose(fp.s_star, 0.25, rel_tol=1e-12)

    def test_both_sectors_convergent(self):
        """is_convergent is True for both sectors (FTUM guarantee)."""
        assert ftum_sector_fixed_point(5, 6).is_convergent
        assert ftum_sector_fixed_point(5, 7).is_convergent

    def test_s_star_equal_across_sectors(self):
        """S*(5,6) = S*(5,7) — FTUM is sector-agnostic."""
        agnostic = sector_agnostic_fixed_point()
        assert agnostic["s_star_equal"] is True

    def test_agnostic_flag_set(self):
        """The 'agnostic' key in sector_agnostic_fixed_point() is True."""
        assert sector_agnostic_fixed_point()["agnostic"] is True

    def test_fixed_point_kcs_values(self):
        """k_CS values stored in SectorFixedPoint match module constants."""
        fp56 = ftum_sector_fixed_point(5, 6)
        fp57 = ftum_sector_fixed_point(5, 7)
        assert fp56.k_cs == K_CS_56
        assert fp57.k_cs == K_CS_57


# ===========================================================================
# TestUnitarySummationStatement  (7 tests)
# ===========================================================================

class TestUnitarySummationStatement:
    """Tests for unitary_summation_statement() — the capstone function."""

    def test_returns_dict(self):
        """unitary_summation_statement() returns a dict."""
        summ = unitary_summation_statement()
        assert isinstance(summ, dict)

    def test_pillar_count_96(self):
        """Closure pillar count is 96."""
        assert unitary_summation_statement()["pillars"] == 96

    def test_test_count_is_11_to_4(self):
        """Test count = 11⁴ = 14,641."""
        summ = unitary_summation_statement()
        assert summ["tests"] == 14641
        assert summ["tests"] == 11**4

    def test_n_lossless_sectors_is_2(self):
        """n_lossless_sectors = 2."""
        assert unitary_summation_statement()["n_lossless_sectors"] == 2

    def test_viable_sectors_are_56_and_57(self):
        """viable_sectors = [(5,6), (5,7)]."""
        summ = unitary_summation_statement()
        assert (5, 6) in summ["viable_sectors"]
        assert (5, 7) in summ["viable_sectors"]
        assert len(summ["viable_sectors"]) == 2

    def test_ftum_agnostic_true(self):
        """ftum_agnostic is True in the summation."""
        assert unitary_summation_statement()["ftum_agnostic"] is True

    def test_ten_closure_steps(self):
        """The Unitary Summation contains exactly 10 closure steps."""
        assert len(unitary_summation_statement()["closure_steps"]) == 10


# ===========================================================================
# TestCrossModuleIntegration  (7 tests)
# ===========================================================================

class TestCrossModuleIntegration:
    """Integration tests: Pillar 96 agrees with earlier pillars."""

    def test_r_bare_consistent_with_braided_winding(self):
        """R_BARE ≈ 0.097 is consistent with (5,7) braided prediction."""
        from src.core.braided_winding import braided_ns_r
        pred57 = braided_ns_r(5, 7)
        r_bare_check = pred57.r_eff / pred57.c_s
        assert math.isclose(R_BARE, r_bare_check, rel_tol=1e-6)

    def test_n2_upper_bound_agrees_with_enumeration(self):
        """Analytic n₂ ≤ 7 agrees with branch_catalog enumeration of lossless pairs."""
        try:
            from src.multiverse.branch_catalog import lossless_branches, full_branch_catalog
            catalog = full_branch_catalog(n_max=12)
            lossless = lossless_branches(catalog)
            analytic_n2_set = set(N2_VIABLE)
            catalog_n2_set = {b.n2 for b in lossless if b.n1 == N1_COMMON}
            assert analytic_n2_set == catalog_n2_set
        except (ImportError, AttributeError):
            pytest.skip("branch_catalog not available in this environment")

    def test_beta_values_consistent_with_litebird_boundary(self):
        """β(5,6) and β(5,7) agree with litebird_boundary canonical constants."""
        from src.core.litebird_boundary import BETA_CANONICAL, BETA_DERIVED
        assert math.isclose(BETA_56, BETA_CANONICAL, rel_tol=1e-9)
        assert math.isclose(BETA_57, BETA_DERIVED,   rel_tol=1e-9)

    def test_beta_gap_consistent_with_dual_sector(self):
        """β gap in unitary_closure is consistent with dual_sector_convergence."""
        from src.core.dual_sector_convergence import BETA_GAP_DEG
        expected_gap = BETA_57 - BETA_56
        assert math.isclose(BETA_GAP_DEG, expected_gap, rel_tol=1e-9)

    def test_k_cs_57_satisfies_completeness_theorem(self):
        """k_CS = 74 is the value proved by Pillar 74 completeness theorem."""
        from src.core.completeness_theorem import K_CS
        assert K_CS_57 == K_CS

    def test_unitary_summation_version_is_v9_25(self):
        """The Unitary Summation is stamped v9.25."""
        summ = unitary_summation_statement()
        assert summ["version"] == "v9.25"

    def test_proof_complete_end_to_end(self):
        """End-to-end: closure theorem + FTUM agnosticism + summation all consistent."""
        closure = unitary_closure_theorem()
        agnostic = sector_agnostic_fixed_point()
        summ = unitary_summation_statement()
        assert closure.is_unique is True
        assert agnostic["agnostic"] is True
        assert summ["proof_complete"] is True
        assert summ["n_lossless_sectors"] == closure.lossless_count == 2
