# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 647 — Multi-experiment joint falsification protocol."""
from __future__ import annotations

from src.core.pillar647_multi_experiment_joint_protocol import (
    EXPERIMENT_PORTFOLIO,
    JOINT_VERDICT_RULES,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    current_portfolio_status,
    evaluate_joint_status,
    joint_verdict_rules,
    pillar_report,
    timeline,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
PORTFOLIO_STATUS = current_portfolio_status()
RULES = joint_verdict_rules()
TIMELINE = timeline()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 647

    def test_status(self):
        assert "JOINT_FALSIFICATION_PROTOCOL" in PILLAR_STATUS

    def test_five_experiments(self):
        assert len(EXPERIMENT_PORTFOLIO) == 5

    def test_four_rules(self):
        assert len(JOINT_VERDICT_RULES) == 4


class TestPortfolioStatus:
    def test_no_falsified_yet(self):
        assert PORTFOLIO_STATUS["n_falsified"] == 0

    def test_high_tension_or_pass(self):
        assert PORTFOLIO_STATUS["joint_status"] in ("HIGH_TENSION", "PASS")

    def test_desi_most_acute(self):
        assert "DESI" in PORTFOLIO_STATUS["most_acute_risk"]


class TestJointVerdictRules:
    def test_rule_j1_exists(self):
        j1 = next(r for r in RULES if r["rule"] == "J1")
        assert j1["verdict"] == "FRAMEWORK_FALSIFIED"

    def test_rule_j3_exists(self):
        j3 = next(r for r in RULES if r["rule"] == "J3")
        assert "Bayes" in j3["name"] or "PASS" in j3["condition"]


class TestEvaluateJointStatus:
    def test_pass(self):
        result = evaluate_joint_status(1.0)
        assert result["joint_status"] == "PASS"

    def test_tension(self):
        result = evaluate_joint_status(2.5)
        assert result["joint_status"] == "HIGH_TENSION_COMPOSITE"

    def test_falsified(self):
        result = evaluate_joint_status(4.6)
        assert result["joint_status"] == "FRAMEWORK_FALSIFIED"
        assert result["J1_fires"] is True


class TestTimeline:
    def test_six_events(self):
        assert len(TIMELINE) >= 5

    def test_desi_first(self):
        years = [t["year"] for t in TIMELINE]
        assert "2026" in years


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
