# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 164: c_L Topological Classification
(src/core/cl_topological_classification.py).

Verifies all constants, functions, and the full report for the conditional
theorem c_L = (k_CS - 3)/k_CS = 71/74 ≈ 0.9595.
"""

import math
import pytest

from src.core.cl_topological_classification import (
    N_W,
    K_CS,
    N_FP_R,
    N_FP_L,
    C_R_THEOREM,
    C_L_TOPOLOGICAL,
    C_L_PHYS_NUMERICAL,
    PILLAR144_NUMERICAL_C_L,
    c_r_theorem_recall,
    count_left_chiral_fixed_points,
    c_l_topological_theorem,
    compare_c_l_theorem_vs_numerical,
    c_l_formula_comparison,
    neutrino_mass_consistency_check,
    cl_topological_classification_report,
    pillar164_summary,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_fp_r(self):
        assert N_FP_R == 2

    def test_n_fp_l(self):
        assert N_FP_L == 3

    def test_c_r_theorem_exact(self):
        assert math.isclose(C_R_THEOREM, 23 / 25, rel_tol=1e-14)

    def test_c_l_topological_exact(self):
        assert math.isclose(C_L_TOPOLOGICAL, 71 / 74, rel_tol=1e-14)

    def test_c_l_topological_value(self):
        assert abs(C_L_TOPOLOGICAL - 0.9595) < 1e-3

    def test_c_l_phys_numerical(self):
        assert C_L_PHYS_NUMERICAL == 0.961

    def test_pillar144_numerical_c_l(self):
        assert PILLAR144_NUMERICAL_C_L == 0.961

    def test_c_l_topological_greater_than_half(self):
        assert C_L_TOPOLOGICAL > 0.5


# ---------------------------------------------------------------------------
# c_r_theorem_recall
# ---------------------------------------------------------------------------

class TestCRTheoremRecall:
    def test_c_r_exact(self):
        result = c_r_theorem_recall()
        assert math.isclose(result["c_r"], 23 / 25, rel_tol=1e-14)

    def test_c_r_value(self):
        result = c_r_theorem_recall()
        assert abs(result["c_r"] - 0.920) < 1e-12

    def test_n_w_in_result(self):
        result = c_r_theorem_recall()
        assert result["n_w"] == 5

    def test_n_fp_r_in_result(self):
        result = c_r_theorem_recall()
        assert result["n_fp_r"] == 2

    def test_pillar_is_143(self):
        result = c_r_theorem_recall()
        assert result["pillar"] == 143

    def test_formula_present(self):
        result = c_r_theorem_recall()
        assert "formula" in result
        assert len(result["formula"]) > 0

    def test_custom_n_w(self):
        result = c_r_theorem_recall(n_w=3, n_fp_r=2)
        assert math.isclose(result["c_r"], (9 - 2) / 9, rel_tol=1e-14)


# ---------------------------------------------------------------------------
# count_left_chiral_fixed_points
# ---------------------------------------------------------------------------

class TestCountLeftChiralFixedPoints:
    def test_n_fp_l_equals_3(self):
        result = count_left_chiral_fixed_points()
        assert result["n_fp_l"] == 3

    def test_uv_brane_fixed_equals_1(self):
        result = count_left_chiral_fixed_points()
        assert result["uv_brane_fixed"] == 1

    def test_ir_brane_fixed_equals_1(self):
        result = count_left_chiral_fixed_points()
        assert result["ir_brane_fixed"] == 1

    def test_chiral_midpoint_fixed_equals_1(self):
        result = count_left_chiral_fixed_points()
        assert result["chiral_midpoint_fixed"] == 1

    def test_sum_equals_n_fp_l(self):
        result = count_left_chiral_fixed_points()
        total = result["uv_brane_fixed"] + result["ir_brane_fixed"] + result["chiral_midpoint_fixed"]
        assert total == result["n_fp_l"]

    def test_argument_present(self):
        result = count_left_chiral_fixed_points()
        assert "argument" in result
        assert len(result["argument"]) > 0

    def test_caveat_contains_conditional(self):
        result = count_left_chiral_fixed_points()
        assert "CONDITIONAL" in result["caveat"]

    def test_caveat_mentions_chiral_midpoint(self):
        result = count_left_chiral_fixed_points()
        assert "chiral" in result["caveat"].lower() or "midpoint" in result["caveat"].lower()


# ---------------------------------------------------------------------------
# c_l_topological_theorem
# ---------------------------------------------------------------------------

class TestCLTopologicalTheorem:
    def test_c_l_exact_71_over_74(self):
        result = c_l_topological_theorem()
        assert math.isclose(result["c_l"], 71 / 74, rel_tol=1e-14)

    def test_k_cs_in_result(self):
        result = c_l_topological_theorem()
        assert result["k_cs"] == 74

    def test_n_fp_l_in_result(self):
        result = c_l_topological_theorem()
        assert result["n_fp_l"] == 3

    def test_status_contains_theorem(self):
        result = c_l_topological_theorem()
        assert "THEOREM" in result["status"]

    def test_formula_present(self):
        result = c_l_topological_theorem()
        assert "formula" in result
        assert "k_CS" in result["formula"] or "74" in result["formula"]

    def test_custom_k_cs(self):
        result = c_l_topological_theorem(k_cs=50, n_fp_l=2)
        assert math.isclose(result["c_l"], 48 / 50, rel_tol=1e-14)


# ---------------------------------------------------------------------------
# compare_c_l_theorem_vs_numerical
# ---------------------------------------------------------------------------

class TestCompareCLTheoremVsNumerical:
    def test_c_l_topological_value(self):
        result = compare_c_l_theorem_vs_numerical()
        assert math.isclose(result["c_l_topological"], 71 / 74, rel_tol=1e-14)

    def test_c_l_numerical_value(self):
        result = compare_c_l_theorem_vs_numerical()
        assert result["c_l_numerical"] == 0.961

    def test_absolute_difference_small(self):
        result = compare_c_l_theorem_vs_numerical()
        assert result["absolute_difference"] < 0.005

    def test_fractional_difference_within_1_pct(self):
        result = compare_c_l_theorem_vs_numerical()
        assert result["fractional_difference"] < 0.01

    def test_consistency_is_consistent(self):
        result = compare_c_l_theorem_vs_numerical()
        assert result["consistency"] == "CONSISTENT"

    def test_status_present(self):
        result = compare_c_l_theorem_vs_numerical()
        assert "status" in result

    def test_absolute_difference_positive(self):
        result = compare_c_l_theorem_vs_numerical()
        assert result["absolute_difference"] >= 0.0


# ---------------------------------------------------------------------------
# c_l_formula_comparison
# ---------------------------------------------------------------------------

class TestCLFormulaComparison:
    def test_c_l_topo_nw_approx_0_08(self):
        result = c_l_formula_comparison()
        assert abs(result["c_l_topo_nw"] - 0.08) < 1e-12

    def test_c_l_topo_kcs_approx_0_9595(self):
        result = c_l_formula_comparison()
        assert abs(result["c_l_topo_kcs"] - 71 / 74) < 1e-12

    def test_c_l_numerical_is_0_961(self):
        result = c_l_formula_comparison()
        assert result["c_l_numerical"] == 0.961

    def test_preferred_formula_mentions_kcs(self):
        result = c_l_formula_comparison()
        assert "k_CS" in result["preferred_formula"] or "71/74" in result["preferred_formula"]

    def test_agreement_kcs_vs_numerical_less_than_1_pct(self):
        result = c_l_formula_comparison()
        assert result["agreement_kcs_vs_numerical"] < 0.01

    def test_c_l_topo_nw_less_than_half(self):
        result = c_l_formula_comparison()
        assert result["c_l_topo_nw"] < 0.5

    def test_c_l_topo_kcs_greater_than_half(self):
        result = c_l_formula_comparison()
        assert result["c_l_topo_kcs"] > 0.5


# ---------------------------------------------------------------------------
# neutrino_mass_consistency_check
# ---------------------------------------------------------------------------

class TestNeutrinoMassConsistencyCheck:
    def test_uv_localized_true(self):
        result = neutrino_mass_consistency_check()
        assert result["uv_localized"] is True

    def test_sub_ev_consistent_true(self):
        result = neutrino_mass_consistency_check()
        assert result["sub_ev_consistent"] is True

    def test_f0_c_l_less_than_1e_6(self):
        result = neutrino_mass_consistency_check()
        assert result["f0_c_l"] < 1e-6

    def test_f0_c_l_positive(self):
        result = neutrino_mass_consistency_check()
        assert result["f0_c_l"] > 0.0

    def test_c_l_in_result(self):
        result = neutrino_mass_consistency_check()
        assert math.isclose(result["c_l"], 71 / 74, rel_tol=1e-12)

    def test_estimate_gev_sub_ev(self):
        result = neutrino_mass_consistency_check()
        # sub-eV = < 1e-9 GeV
        assert result["estimate_gev"] < 1e-9

    def test_ir_localized_gives_large_f0(self):
        # c < 0.5 → IR-localized → large wavefunction overlap
        result = neutrino_mass_consistency_check(c_l=0.08)
        assert result["uv_localized"] is False
        assert result["f0_c_l"] > 1.0


# ---------------------------------------------------------------------------
# cl_topological_classification_report
# ---------------------------------------------------------------------------

class TestCLTopologicalClassificationReport:
    def test_pillar_is_164(self):
        result = cl_topological_classification_report()
        assert result["pillar"] == 164

    def test_c_l_theorem_approx_0_9595(self):
        result = cl_topological_classification_report()
        assert math.isclose(result["c_l_theorem"], 71 / 74, rel_tol=1e-14)

    def test_c_l_numerical_is_0_961(self):
        result = cl_topological_classification_report()
        assert result["c_l_numerical"] == 0.961

    def test_agreement_pct_small(self):
        result = cl_topological_classification_report()
        assert result["agreement_pct"] < 1.0

    def test_epistemic_label_is_conditional_theorem(self):
        result = cl_topological_classification_report()
        assert result["epistemic_label"] == "CONDITIONAL_THEOREM"

    def test_open_issues_is_list(self):
        result = cl_topological_classification_report()
        assert isinstance(result["open_issues"], list)
        assert len(result["open_issues"]) >= 2

    def test_open_issues_contains_midpoint(self):
        result = cl_topological_classification_report()
        combined = " ".join(result["open_issues"])
        assert "midpoint" in combined or "chiral" in combined

    def test_status_is_conditional_theorem(self):
        result = cl_topological_classification_report()
        assert result["status"] == "CONDITIONAL_THEOREM"

    def test_theorem_string_present(self):
        result = cl_topological_classification_report()
        assert "theorem" in result
        assert "71" in result["theorem"] or "74" in result["theorem"]


# ---------------------------------------------------------------------------
# pillar164_summary
# ---------------------------------------------------------------------------

class TestPillar164Summary:
    def test_pillar_is_164(self):
        result = pillar164_summary()
        assert result["pillar"] == 164

    def test_c_l_predicted_exact(self):
        result = pillar164_summary()
        assert math.isclose(result["c_l_predicted"], 71 / 74, rel_tol=1e-14)

    def test_c_l_numerical_is_0_961(self):
        result = pillar164_summary()
        assert result["c_l_numerical"] == 0.961

    def test_agreement_pct_is_0_16(self):
        result = pillar164_summary()
        assert abs(result["agreement_pct"] - 0.16) < 0.05

    def test_status_is_conditional_theorem(self):
        result = pillar164_summary()
        assert result["status"] == "CONDITIONAL_THEOREM"

    def test_theorem_string_present(self):
        result = pillar164_summary()
        assert "theorem" in result
        assert "k_CS" in result["theorem"] or "74" in result["theorem"]
