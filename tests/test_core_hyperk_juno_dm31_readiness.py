# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for hyperk_juno_dm31_readiness.py (v10.30)."""
import math
import pytest
from src.core.hyperk_juno_dm31_readiness import (
    COMBINED_SIGMA_PCT,
    DM2_31_PDG,
    DM2_31_RESIDUAL_PCT,
    DM2_31_UM,
    HYPERK_EXPECTED_SIGMA_PCT,
    JUNO_EXPECTED_SIGMA_PCT,
    hyperk_juno_falsifier_routing,
    hyperk_juno_readiness_report,
    p17_tension_at_precision,
    precision_milestone_analysis,
)


class TestConstants:
    def test_dm2_31_um_lt_pdg(self):
        # UM is 2.18% below PDG
        assert DM2_31_UM < DM2_31_PDG

    def test_residual_is_2_18(self):
        assert abs(DM2_31_RESIDUAL_PCT - 2.18) < 0.01

    def test_um_consistent_with_residual(self):
        assert abs((DM2_31_PDG - DM2_31_UM) / DM2_31_PDG * 100.0 - DM2_31_RESIDUAL_PCT) < 0.01

    def test_combined_sigma_lt_hyperk_and_juno(self):
        assert COMBINED_SIGMA_PCT < HYPERK_EXPECTED_SIGMA_PCT
        assert COMBINED_SIGMA_PCT < JUNO_EXPECTED_SIGMA_PCT


class TestTensionAtPrecision:
    def test_tension_increases_as_sigma_decreases(self):
        t_large = p17_tension_at_precision(5.0)
        t_small = p17_tension_at_precision(1.0)
        assert t_small["tension_sigma"] > t_large["tension_sigma"]

    def test_tension_at_2pct_is_about_1sigma(self):
        # sigma = 2.18% is exactly the residual → tension = 1.0σ
        t = p17_tension_at_precision(DM2_31_RESIDUAL_PCT)
        assert abs(t["tension_sigma"] - 1.0) < 0.05

    def test_um_in_falsification_window(self):
        t = p17_tension_at_precision(1.0)
        assert t["in_falsification_window"] is True

    def test_routing_at_tight_precision(self):
        # At 0.5% precision: tension = 2.18/0.5 = 4.36σ → FALSIFIED
        t = p17_tension_at_precision(0.5)
        assert t["routing"] == "FALSIFIED"

    def test_routing_at_loose_precision(self):
        # At 5% precision: tension = 2.18/5 = 0.44σ → CONSISTENT
        t = p17_tension_at_precision(5.0)
        assert t["routing"] == "CONSISTENT"


class TestPrecisionMilestones:
    def test_returns_list_of_milestones(self):
        milestones = precision_milestone_analysis()
        assert len(milestones) > 5

    def test_all_have_routing(self):
        milestones = precision_milestone_analysis()
        for m in milestones:
            assert m["routing"] in ("CONSISTENT", "TENSION", "FALSIFIED")

    def test_tightest_precision_falsifies(self):
        milestones = precision_milestone_analysis()
        tightest = milestones[-1]  # 0.1% precision
        assert tightest["routing"] == "FALSIFIED"

    def test_loosest_precision_consistent(self):
        milestones = precision_milestone_analysis()
        loosest = milestones[0]  # 5% precision
        assert loosest["routing"] == "CONSISTENT"


class TestHyperkJunoRouting:
    def test_pdg_value_at_hyperk_precision_is_tension(self):
        result = hyperk_juno_falsifier_routing(DM2_31_PDG, HYPERK_EXPECTED_SIGMA_PCT, "Hyper-K", 2028)
        # Tension = 2.18% / 1% = 2.18σ → TENSION
        assert result["route"] == "TENSION"

    def test_um_exact_at_hyperk_is_pass(self):
        result = hyperk_juno_falsifier_routing(DM2_31_UM, HYPERK_EXPECTED_SIGMA_PCT, "Hyper-K", 2028)
        assert result["route"] == "PASS"

    def test_pdg_value_at_juno_precision(self):
        result = hyperk_juno_falsifier_routing(DM2_31_PDG, JUNO_EXPECTED_SIGMA_PCT, "JUNO", 2027)
        # Tension = 2.18% / 0.5% = 4.36σ → FALSIFIED
        assert result["route"] == "FALSIFIED"

    def test_result_has_action(self):
        result = hyperk_juno_falsifier_routing(DM2_31_PDG, 1.0, "Hyper-K", 2028)
        assert "action" in result
        assert len(result["action"]) > 10

    def test_outside_window_falsifies(self):
        # DM2_31 = 2.0e-3 is outside the falsification window [2.2e-3, 2.7e-3]
        result = hyperk_juno_falsifier_routing(2.0e-3, 0.5, "future", 2030)
        assert result["route"] == "FALSIFIED"


class TestReadinessReport:
    def test_report_version(self):
        report = hyperk_juno_readiness_report()
        assert report["version"] == "v10.30"

    def test_p17_status(self):
        report = hyperk_juno_readiness_report()
        assert report["p17_status"] == "GEOMETRIC_PREDICTION"

    def test_report_has_experiments(self):
        report = hyperk_juno_readiness_report()
        assert "JUNO" in report["experiments"]
        assert "Hyper-K" in report["experiments"]
        assert "combined" in report["experiments"]

    def test_report_has_scenarios(self):
        report = hyperk_juno_readiness_report()
        assert len(report["hyperk_scenarios"]) >= 3
        assert len(report["juno_scenarios"]) >= 1

    def test_tension_thresholds_monotone(self):
        report = hyperk_juno_readiness_report()
        t2 = report["tension_2sigma_at_precision_pct"]
        t3 = report["tension_3sigma_at_precision_pct"]
        # 3σ requires tighter precision than 2σ
        if t2 > 0 and t3 > 0:
            assert t3 <= t2
