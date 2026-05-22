# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 343 — 2027 Triple-Observatory Unified Decision Matrix."""
import math
import pytest

from src.core.pillar343_triple_observatory_matrix import (
    N_W, K_CS,
    R_UM, R_UM_SIGMA, WA_UM, MASS_ORDERING_UM,
    WA_CURRENT_SIGMA, R_ACT_UPPER,
    DESI_DR3_SIGMA_WA, DESI_DR3_CENTRAL,
    SO_SIGMA_R, SIGMA_FALSIFIED,
    R_PRIOR_MAX, WA_PRIOR_RANGE,
    separation_guard,
    bayes_factor_r,
    bayes_factor_wa,
    bayes_factor_ordering,
    joint_bayes_factor,
    SCENARIO_VERDICTS,
    classify_so_result,
    classify_desi_result,
    classify_juno_result,
    run_joint_verdict,
    precompute_all_scenarios,
    best_case_scenario,
    worst_case_scenario,
    desi_fails_only_scenario,
    so_fails_only_scenario,
    pillar343_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_r_um(self):
        assert abs(R_UM - 0.0315) < 1e-4

    def test_wa_um_zero(self):
        assert WA_UM == 0.0

    def test_mass_ordering_normal(self):
        assert MASS_ORDERING_UM == "NORMAL"

    def test_desi_current_tension(self):
        assert WA_CURRENT_SIGMA > 2.0

    def test_so_sigma_small(self):
        assert SO_SIGMA_R < 0.01

    def test_sigma_falsified_three(self):
        assert abs(SIGMA_FALSIFIED - 3.0) < 1e-9

    def test_r_prior_max(self):
        assert R_PRIOR_MAX > R_UM

    def test_wa_prior_range_positive(self):
        assert WA_PRIOR_RANGE > 0


class TestSeparationGuard:
    def test_returns_dict(self):
        assert isinstance(separation_guard(), dict)

    def test_pillar_343(self):
        assert separation_guard()["pillar"] == 343

    def test_no_hardgate_promotion(self):
        assert separation_guard()["hardgate_promotion"] is False

    def test_no_toe_score_delta(self):
        assert separation_guard()["toe_score_delta"] == 0


class TestBayesFactors:
    def test_bayes_r_perfect_match_high(self):
        # If SO measures exactly r_UM, Bayes factor should be >> 1
        b = bayes_factor_r(R_UM, SO_SIGMA_R)
        assert b > 1.0

    def test_bayes_r_far_miss_low(self):
        # If SO measures r=0, Bayes factor much lower
        b_match = bayes_factor_r(R_UM, SO_SIGMA_R)
        b_miss = bayes_factor_r(0.0, SO_SIGMA_R)
        assert b_match > b_miss

    def test_bayes_r_positive(self):
        b = bayes_factor_r(0.02, SO_SIGMA_R)
        assert b > 0

    def test_bayes_wa_zero_consistent_high(self):
        # If DESI DR3 measures wₐ=0, B >> 1
        b = bayes_factor_wa(0.0, DESI_DR3_SIGMA_WA)
        assert b > 1.0

    def test_bayes_wa_tension_value_low(self):
        b_zero = bayes_factor_wa(0.0, DESI_DR3_SIGMA_WA)
        b_tension = bayes_factor_wa(DESI_DR3_CENTRAL, DESI_DR3_SIGMA_WA)
        assert b_zero > b_tension

    def test_bayes_wa_positive(self):
        b = bayes_factor_wa(-0.3, 0.2)
        assert b > 0

    def test_bayes_ordering_normal(self):
        b = bayes_factor_ordering("NORMAL")
        assert abs(b - 2.0) < 1e-9

    def test_bayes_ordering_inverted(self):
        b = bayes_factor_ordering("INVERTED")
        assert abs(b - 0.0) < 1e-9

    def test_bayes_ordering_inconclusive(self):
        b = bayes_factor_ordering("inconclusive")
        assert abs(b - 1.0) < 1e-9

    def test_bayes_ordering_pass(self):
        b = bayes_factor_ordering("PASS")
        assert b > 0

    def test_joint_bayes_product(self):
        b_r = bayes_factor_r(R_UM, SO_SIGMA_R)
        b_wa = bayes_factor_wa(0.0, DESI_DR3_SIGMA_WA)
        b_ord = bayes_factor_ordering("NORMAL")
        b_joint = joint_bayes_factor(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL")
        assert abs(b_joint - b_r * b_wa * b_ord) < 1e-9


class TestScenarioVerdicts:
    def test_eight_scenarios(self):
        assert len(SCENARIO_VERDICTS) == 8

    def test_all_pass_gives_standing(self):
        verdict, _ = SCENARIO_VERDICTS[(True, True, True)]
        assert verdict == "STANDING"

    def test_all_fail_gives_falsified(self):
        verdict, _ = SCENARIO_VERDICTS[(False, False, False)]
        assert verdict == "FALSIFIED"

    def test_so_fail_only_gives_high_tension(self):
        verdict, _ = SCENARIO_VERDICTS[(False, True, True)]
        assert "TENSION" in verdict or "FALSIFIED" in verdict

    def test_desi_fail_only_gives_high_tension(self):
        verdict, _ = SCENARIO_VERDICTS[(True, False, True)]
        assert "TENSION" in verdict or "FALSIFIED" in verdict

    def test_juno_fail_only_gives_partially_falsified(self):
        verdict, _ = SCENARIO_VERDICTS[(True, True, False)]
        assert "FALSIFIED" in verdict

    def test_two_fails_gives_substantially_falsified(self):
        for key in [(True, False, False), (False, True, False), (False, False, True)]:
            verdict, _ = SCENARIO_VERDICTS[key]
            assert "FALSIFIED" in verdict


class TestClassifiers:
    def test_so_pass_for_r_um(self):
        pass_, verdict, _, _ = classify_so_result(R_UM, SO_SIGMA_R)
        assert pass_

    def test_so_fail_for_very_low_r(self):
        # r = 0.001 << 0.010 → FALSIFIED
        pass_, verdict, _, _ = classify_so_result(0.001, SO_SIGMA_R)
        assert not pass_

    def test_desi_pass_for_wa_zero(self):
        pass_, verdict, _, _ = classify_desi_result(0.0, DESI_DR3_SIGMA_WA)
        assert pass_

    def test_desi_fail_for_high_tension(self):
        # wₐ = -0.90 with σ = 0.18 → tension > 3σ
        pass_, verdict, _, _ = classify_desi_result(-0.90, 0.18)
        assert not pass_

    def test_juno_pass_for_normal(self):
        pass_, verdict, _, _ = classify_juno_result("NORMAL", 4.0)
        assert pass_

    def test_juno_fail_for_inverted_at_3sigma(self):
        pass_, verdict, _, _ = classify_juno_result("INVERTED", 3.5)
        assert not pass_

    def test_juno_pass_for_inconclusive(self):
        pass_, verdict, _, _ = classify_juno_result("INCONCLUSIVE", 1.0)
        assert pass_


class TestJointVerdict:
    def test_returns_dict(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL", 4.0)
        assert isinstance(result, dict)

    def test_best_case_standing(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL", 4.0)
        assert result["joint_verdict"] == "STANDING"

    def test_worst_case_falsified(self):
        result = run_joint_verdict(0.001, SO_SIGMA_R, -0.90, 0.18, "INVERTED", 3.5)
        assert result["joint_verdict"] == "FALSIFIED"

    def test_bayes_factor_positive(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL", 4.0)
        assert result["bayes_factor_joint"] > 0

    def test_log10_bayes_finite(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL", 4.0)
        assert math.isfinite(result["log10_bayes"])

    def test_has_action(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "NORMAL", 4.0)
        assert "action" in result

    def test_inverted_juno_fails(self):
        result = run_joint_verdict(R_UM, SO_SIGMA_R, 0.0, DESI_DR3_SIGMA_WA, "INVERTED", 3.5)
        assert "FALSIFIED" in result["joint_verdict"]


class TestPrecomputedScenarios:
    def test_eight_scenarios_computed(self):
        scenarios = precompute_all_scenarios()
        assert len(scenarios) == 8

    def test_all_have_joint_verdict(self):
        scenarios = precompute_all_scenarios()
        for s in scenarios:
            assert "joint_verdict" in s

    def test_all_have_log10_bayes(self):
        scenarios = precompute_all_scenarios()
        for s in scenarios:
            assert "log10_bayes" in s

    def test_no_duplicate_keys(self):
        scenarios = precompute_all_scenarios()
        keys = [(s["so_pass"], s["desi_pass"], s["juno_pass"]) for s in scenarios]
        assert len(set(keys)) == 8


class TestNamedScenarios:
    def test_best_case_standing(self):
        result = best_case_scenario()
        assert result["joint_verdict"] == "STANDING"

    def test_worst_case_falsified(self):
        result = worst_case_scenario()
        assert result["joint_verdict"] == "FALSIFIED"

    def test_desi_fails_only_high_tension(self):
        result = desi_fails_only_scenario()
        # DESI fails (wₐ≠0) → HIGH_TENSION or PARTIALLY_FALSIFIED
        assert "TENSION" in result["joint_verdict"] or "FALSIFIED" in result["joint_verdict"]

    def test_so_fails_only_high_tension(self):
        result = so_fails_only_scenario()
        assert "TENSION" in result["joint_verdict"] or "FALSIFIED" in result["joint_verdict"]

    def test_best_case_bayes_high(self):
        best = best_case_scenario()
        worst = worst_case_scenario()
        # Best case (SO confirms r) should have higher Bayes factor
        assert best["log10_bayes"] > worst.get("log10_bayes", float("-inf"))


class TestFullReport:
    def test_returns_dict(self):
        assert isinstance(pillar343_full_report(), dict)

    def test_pillar_343(self):
        assert pillar343_full_report()["pillar"] == 343

    def test_has_experiments(self):
        report = pillar343_full_report()
        assert "experiments" in report

    def test_three_experiments(self):
        report = pillar343_full_report()
        assert len(report["experiments"]) == 3

    def test_experiments_include_so(self):
        report = pillar343_full_report()
        assert "SIMONS_OBSERVATORY" in report["experiments"]

    def test_experiments_include_desi(self):
        report = pillar343_full_report()
        assert "DESI_DR3" in report["experiments"]

    def test_experiments_include_juno(self):
        report = pillar343_full_report()
        assert "JUNO" in report["experiments"]

    def test_eight_scenarios(self):
        report = pillar343_full_report()
        assert report["joint_scenario_count"] == 8

    def test_execution_protocol_present(self):
        report = pillar343_full_report()
        assert "execution_protocol" in report

    def test_scenario_1_standing(self):
        report = pillar343_full_report()
        assert report["scenario_1_all_pass"] == "STANDING"

    def test_scenario_8_falsified(self):
        report = pillar343_full_report()
        assert report["scenario_8_all_fail"] == "FALSIFIED"
