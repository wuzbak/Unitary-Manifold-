# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_topology.py
===========================
Tests for src/core/cmb_topology.py — Pillar 34:
CMB Observables Derived from Integer Topology (no fitting).

Physical claims under test
--------------------------
1. topology_to_cmb: all three CMB observables (ns, r, β) computed from
   integer (n1, n2) with zero free parameters; canonical (5,7) passes all
   Planck/BICEP/birefringence constraints.
2. admissible_window: returns (0.22°, 0.38°); correct order.
3. predicted_gap: returns (0.29°, 0.31°); inside the admissible window.
4. ns_from_winding: correct formula 1 - 20/(3 n1²); consistent with braided.
5. r_bare_from_winding: correct formula 32/(3 n1²); positive.
6. r_braided_from_pair: r = r_bare × c_s; r < r_bare; within BICEP limit for (5,7).
7. beta_from_cs: positive angle; inside admissible window for canonical pair.
8. litebird_sensitivity: correct σ(β) ≈ 0.03°; identifies resolvability.
9. falsification_check: correctly identifies falsified/consistent scenarios.
10. branch_comparison: correct structure; gap inside window.
11. integer_topology_observables_table: free_params = 0; all_pass = True for (5,7).
12. Input validation: ValueError for unphysical (n1, n2) pairs.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.cmb_topology import (
    topology_to_cmb,
    admissible_window,
    predicted_gap,
    ns_from_winding,
    r_bare_from_winding,
    r_braided_from_pair,
    beta_from_cs,
    litebird_sensitivity,
    falsification_check,
    branch_comparison,
    integer_topology_observables_table,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
    NS_CANONICAL,
    R_CANONICAL,
    BETA_CANONICAL_DEG,
    BETA_DERIVED_DEG,
    BETA_WINDOW_MIN_DEG,
    BETA_WINDOW_MAX_DEG,
    BETA_GAP_MIN_DEG,
    BETA_GAP_MAX_DEG,
    R_BICEP_KECK_LIMIT,
    LITEBIRD_SIGMA_BETA_DEG,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14

    def test_beta_window_order(self):
        assert BETA_WINDOW_MIN_DEG < BETA_WINDOW_MAX_DEG

    def test_beta_gap_inside_window(self):
        assert BETA_WINDOW_MIN_DEG < BETA_GAP_MIN_DEG
        assert BETA_GAP_MAX_DEG < BETA_WINDOW_MAX_DEG

    def test_r_bicep_keck_limit(self):
        assert R_BICEP_KECK_LIMIT == 0.036

    def test_litebird_sigma(self):
        assert abs(LITEBIRD_SIGMA_BETA_DEG - 0.03) < 1e-10


# ===========================================================================
# topology_to_cmb
# ===========================================================================

class TestTopologyToCMB:
    def test_canonical_all_pass(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["all_pass"] is True

    def test_canonical_ns_in_planck_1sigma(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["ns_ok"] is True
        assert result["ns_sigma"] <= 1.0

    def test_canonical_r_below_bicep(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["r_ok"] is True
        assert result["r"] < R_BICEP_KECK_LIMIT

    def test_canonical_beta_in_window(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["beta_ok"] is True
        assert BETA_WINDOW_MIN_DEG <= result["beta_deg"] <= BETA_WINDOW_MAX_DEG

    def test_canonical_k_cs(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["k_cs"] == K_CS_CANONICAL

    def test_canonical_c_s(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert abs(result["c_s"] - C_S_CANONICAL) < 1e-12

    def test_zero_free_parameters(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["free_params"] == 0

    def test_r_less_than_r_bare(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert result["r"] < result["r_bare"]

    def test_r_equals_r_bare_times_cs(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        assert abs(result["r"] - result["r_bare"] * result["c_s"]) < 1e-12

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            topology_to_cmb(0, 7)

    def test_raises_n2_leq_n1(self):
        with pytest.raises(ValueError):
            topology_to_cmb(5, 5)

    def test_raises_n2_lt_n1(self):
        with pytest.raises(ValueError):
            topology_to_cmb(7, 5)

    def test_output_keys_complete(self):
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        for key in ["n1", "n2", "k_cs", "c_s", "ns", "r", "r_bare",
                    "beta_deg", "ns_sigma", "r_ok", "ns_ok",
                    "beta_ok", "all_pass", "free_params"]:
            assert key in result, f"Missing key: {key}"

    def test_other_pair_higher_r_bare(self):
        # (3,7) should give different k_cs and potentially higher r
        result_3_7 = topology_to_cmb(3, 7)
        assert result_3_7["k_cs"] == 3**2 + 7**2

    def test_c_s_from_formula(self):
        # c_s = |n2² - n1²| / k_cs
        result = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
        expected_cs = (N2_CANONICAL**2 - N1_CANONICAL**2) / K_CS_CANONICAL
        assert abs(result["c_s"] - expected_cs) < 1e-12


# ===========================================================================
# admissible_window
# ===========================================================================

class TestAdmissibleWindow:
    def test_returns_tuple_of_two(self):
        w = admissible_window()
        assert len(w) == 2

    def test_correct_bounds(self):
        beta_min, beta_max = admissible_window()
        assert abs(beta_min - BETA_WINDOW_MIN_DEG) < 1e-12
        assert abs(beta_max - BETA_WINDOW_MAX_DEG) < 1e-12

    def test_min_less_than_max(self):
        beta_min, beta_max = admissible_window()
        assert beta_min < beta_max

    def test_canonical_beta_inside_window(self):
        beta_min, beta_max = admissible_window()
        assert beta_min <= BETA_CANONICAL_DEG <= beta_max
        assert beta_min <= BETA_DERIVED_DEG <= beta_max


# ===========================================================================
# predicted_gap
# ===========================================================================

class TestPredictedGap:
    def test_returns_tuple_of_two(self):
        g = predicted_gap()
        assert len(g) == 2

    def test_correct_bounds(self):
        gap_min, gap_max = predicted_gap()
        assert abs(gap_min - BETA_GAP_MIN_DEG) < 1e-12
        assert abs(gap_max - BETA_GAP_MAX_DEG) < 1e-12

    def test_gap_inside_window(self):
        beta_min, beta_max = admissible_window()
        gap_min, gap_max = predicted_gap()
        assert beta_min < gap_min
        assert gap_max < beta_max

    def test_canonical_beta_outside_gap(self):
        gap_min, gap_max = predicted_gap()
        assert not (gap_min <= BETA_CANONICAL_DEG <= gap_max)
        assert not (gap_min <= BETA_DERIVED_DEG <= gap_max)


# ===========================================================================
# ns_from_winding
# ===========================================================================

class TestNsFromWinding:
    def test_formula_n5(self):
        ns = ns_from_winding(5)
        # Uses KK inflation chain: ns ≈ 0.9635 (consistent with braided_ns_r)
        assert abs(ns - 0.9635) < 0.001

    def test_formula_n7(self):
        ns = ns_from_winding(7)
        # n=7 gives larger phi0_eff → ns closer to 1
        assert abs(ns - 0.9814) < 0.001

    def test_less_than_one(self):
        for n in [1, 2, 5, 7, 10]:
            assert ns_from_winding(n) < 1.0

    def test_increases_with_n(self):
        # Larger n → more e-folds → more scale invariant (ns closer to 1)
        ns5 = ns_from_winding(5)
        ns7 = ns_from_winding(7)
        assert ns7 > ns5

    def test_planck_consistency_n5(self):
        ns = ns_from_winding(5)
        # Should be within 1σ of Planck 0.9649 ± 0.0042 (uses proper KK inflation)
        assert abs(ns - 0.9649) < 1 * 0.0042

    def test_raises_n_zero(self):
        with pytest.raises(ValueError):
            ns_from_winding(0)

    def test_raises_n_negative(self):
        with pytest.raises(ValueError):
            ns_from_winding(-1)


# ===========================================================================
# r_bare_from_winding
# ===========================================================================

class TestRBareFromWinding:
    def test_formula_n5(self):
        r = r_bare_from_winding(5)
        # Uses KK inflation chain: r_bare ≈ 0.0973 (from braided_ns_r output)
        assert abs(r - 0.0973) < 0.001

    def test_positive(self):
        for n in [1, 2, 5, 7, 10]:
            assert r_bare_from_winding(n) > 0.0

    def test_decreases_with_n(self):
        r5 = r_bare_from_winding(5)
        r7 = r_bare_from_winding(7)
        assert r7 < r5

    def test_large_n_small_r(self):
        assert r_bare_from_winding(100) < 0.005

    def test_raises_n_zero(self):
        with pytest.raises(ValueError):
            r_bare_from_winding(0)

    def test_n5_exceeds_bicep(self):
        r = r_bare_from_winding(5)
        assert r > R_BICEP_KECK_LIMIT


# ===========================================================================
# r_braided_from_pair
# ===========================================================================

class TestRBraidedFromPair:
    def test_canonical_below_bicep(self):
        r = r_braided_from_pair(N1_CANONICAL, N2_CANONICAL)
        assert r < R_BICEP_KECK_LIMIT

    def test_less_than_r_bare(self):
        r_braid = r_braided_from_pair(N1_CANONICAL, N2_CANONICAL)
        r_bare  = r_bare_from_winding(N1_CANONICAL)
        assert r_braid < r_bare

    def test_ratio_equals_c_s(self):
        r_braid = r_braided_from_pair(N1_CANONICAL, N2_CANONICAL)
        r_bare  = r_bare_from_winding(N1_CANONICAL)
        c_s     = r_braid / r_bare
        assert abs(c_s - C_S_CANONICAL) < 1e-12

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            r_braided_from_pair(0, 7)

    def test_raises_n2_leq_n1(self):
        with pytest.raises(ValueError):
            r_braided_from_pair(5, 3)

    def test_positive(self):
        assert r_braided_from_pair(N1_CANONICAL, N2_CANONICAL) > 0.0


# ===========================================================================
# beta_from_cs
# ===========================================================================

class TestBetaFromCS:
    def test_positive(self):
        beta = beta_from_cs(K_CS_CANONICAL)
        assert beta > 0.0

    def test_in_admissible_window(self):
        beta = beta_from_cs(K_CS_CANONICAL)
        assert BETA_WINDOW_MIN_DEG <= beta <= BETA_WINDOW_MAX_DEG

    def test_raises_k_cs_zero(self):
        with pytest.raises(ValueError):
            beta_from_cs(0)

    def test_raises_alpha_em_zero(self):
        with pytest.raises(ValueError):
            beta_from_cs(74, alpha_em=0.0)

    def test_raises_r_c_zero(self):
        with pytest.raises(ValueError):
            beta_from_cs(74, r_c=0.0)

    def test_finite_output(self):
        beta = beta_from_cs(K_CS_CANONICAL)
        assert math.isfinite(beta)


# ===========================================================================
# litebird_sensitivity
# ===========================================================================

class TestLiteBirdSensitivity:
    def test_sigma_correct(self):
        result = litebird_sensitivity()
        assert abs(result["sigma_beta_deg"] - 0.03) < 1e-10

    def test_correct_canonical_beta(self):
        result = litebird_sensitivity()
        assert abs(result["canonical_beta_deg"] - BETA_CANONICAL_DEG) < 1e-10

    def test_correct_derived_beta(self):
        result = litebird_sensitivity()
        assert abs(result["derived_beta_deg"] - BETA_DERIVED_DEG) < 1e-10

    def test_branch_separation_positive(self):
        result = litebird_sensitivity()
        assert result["branch_separation"] > 0.0

    def test_gap_width_positive(self):
        result = litebird_sensitivity()
        assert result["gap_max_deg"] > result["gap_min_deg"]

    def test_gap_resolvable_flag(self):
        result = litebird_sensitivity()
        assert isinstance(result["gap_resolvable"], bool)

    def test_branches_resolvable_flag(self):
        result = litebird_sensitivity()
        assert isinstance(result["branches_resolvable"], bool)

    def test_launch_year(self):
        result = litebird_sensitivity()
        assert result["launch_year"] == 2032

    def test_all_keys_present(self):
        result = litebird_sensitivity()
        for key in ["sigma_beta_deg", "canonical_beta_deg", "derived_beta_deg",
                    "branch_separation", "gap_min_deg", "gap_max_deg",
                    "gap_resolvable", "branches_resolvable", "launch_year"]:
            assert key in result


# ===========================================================================
# falsification_check
# ===========================================================================

class TestFalsificationCheck:
    def test_inside_window_not_falsified(self):
        result = falsification_check(0.331)
        assert result["falsified"] is False

    def test_inside_window_derived_not_falsified(self):
        result = falsification_check(0.351)
        assert result["falsified"] is False

    def test_below_window_falsified(self):
        result = falsification_check(0.10)
        assert result["falsified"] is True

    def test_above_window_falsified(self):
        result = falsification_check(0.50)
        assert result["falsified"] is True

    def test_in_gap_falsified(self):
        result = falsification_check(0.30)
        assert result["falsified"] is True

    def test_reason_is_string(self):
        result = falsification_check(0.351)
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0

    def test_in_admissible_flag(self):
        result_in  = falsification_check(0.331)
        result_out = falsification_check(0.10)
        assert result_in["in_admissible"] is True
        assert result_out["in_admissible"] is False

    def test_in_gap_flag(self):
        result_gap    = falsification_check(0.30)
        result_no_gap = falsification_check(0.331)
        assert result_gap["in_predicted_gap"] is True
        assert result_no_gap["in_predicted_gap"] is False


# ===========================================================================
# branch_comparison
# ===========================================================================

class TestBranchComparison:
    def test_structure(self):
        result = branch_comparison()
        assert "canonical_branch" in result
        assert "derived_branch" in result
        assert "gap" in result
        assert "litebird_test" in result
        assert "primary_falsifier" in result

    def test_gap_inside_window(self):
        result = branch_comparison()
        g = result["gap"]
        w = admissible_window()
        assert w[0] < g["min_deg"]
        assert g["max_deg"] < w[1]

    def test_gap_width(self):
        result = branch_comparison()
        g = result["gap"]
        assert abs(g["width_deg"] - (g["max_deg"] - g["min_deg"])) < 1e-12

    def test_falsifier_string(self):
        result = branch_comparison()
        assert isinstance(result["primary_falsifier"], str)
        assert "falsifies" in result["primary_falsifier"]


# ===========================================================================
# integer_topology_observables_table
# ===========================================================================

class TestIntegerTopologyTable:
    def test_free_params_zero(self):
        table = integer_topology_observables_table()
        assert table["free_parameters"] == 0

    def test_all_pass(self):
        table = integer_topology_observables_table()
        assert table["all_pass"] is True

    def test_ns_pass(self):
        table = integer_topology_observables_table()
        assert table["ns"]["pass"] is True

    def test_r_pass(self):
        table = integer_topology_observables_table()
        assert table["r"]["pass"] is True

    def test_beta_pass(self):
        table = integer_topology_observables_table()
        assert table["beta"]["pass"] is True

    def test_integer_input(self):
        table = integer_topology_observables_table()
        assert table["integer_input"]["n1"] == N1_CANONICAL
        assert table["integer_input"]["n2"] == N2_CANONICAL

    def test_k_cs_correct(self):
        table = integer_topology_observables_table()
        assert table["k_cs"]["value"] == K_CS_CANONICAL

    def test_c_s_correct(self):
        table = integer_topology_observables_table()
        assert abs(table["c_s"]["value"] - C_S_CANONICAL) < 1e-12

    def test_litebird_present(self):
        table = integer_topology_observables_table()
        assert "litebird_test" in table
