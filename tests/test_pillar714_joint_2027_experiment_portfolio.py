# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 714 — joint 2027 experiment portfolio."""
from __future__ import annotations

import json

import pytest

from src.core.pillar714_joint_2027_experiment_portfolio import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    decision_dashboard_2027,
    experiment_tension_table,
    joint_survival_probability,
    portfolio_2027_verdict,
)

TABLE = experiment_tension_table()
JOINT = joint_survival_probability()
PORTFOLIO = portfolio_2027_verdict()
DASHBOARD = decision_dashboard_2027()


class TestConstants:
    def test_identity(self):
        assert PILLAR_NUMBER == 714
        assert PILLAR_STATUS == "JOINT_2027_PORTFOLIO_CERTIFIED"
        assert PILLAR_TITLE == "Joint 2027 Experiment Portfolio"


class TestTable:
    def test_has_five_experiments(self):
        assert len(TABLE) == 5

    def test_desi_tension(self):
        assert TABLE["DESI_DR3"]["tension_sigma"] == pytest.approx(abs(-0.52) / 0.18)
        assert TABLE["DESI_DR3"]["verdict"] == "TENSION"

    def test_so_is_consistent(self):
        assert TABLE["SO_DR1"]["tension_sigma"] == pytest.approx(abs(0.028 - 0.0315) / 0.006)
        assert TABLE["SO_DR1"]["verdict"] == "CONSISTENT"

    def test_juno_probability_substantial_but_below_half(self):
        assert TABLE["JUNO_PHASE2"]["tension_sigma"] > 3.0
        assert 0.0 < TABLE["JUNO_PHASE2"]["p_survive_3sigma"] < 0.5

    def test_preregistered_channels_centered(self):
        assert TABLE["SPHEREX_FNL"]["tension_sigma"] == pytest.approx(0.0)
        assert TABLE["LITEBIRD_BETA"]["tension_sigma"] == pytest.approx(0.0)


class TestJoint:
    def test_joint_probability_range(self):
        assert 0.0 < JOINT["p_joint_survive_all"] < 1.0

    def test_joint_probability_expected_scale(self):
        assert JOINT["p_joint_survive_all"] == pytest.approx(0.165, rel=0.15)

    def test_timeline(self):
        assert JOINT["timeline"]["2027"] == ["DESI_DR3", "SO_DR1", "JUNO_PHASE2"]


class TestPortfolio:
    def test_portfolio_status(self):
        assert PORTFOLIO["portfolio_status"] == "HIGH_RISK_TENSION"
        assert PORTFOLIO["highest_tension_experiment"] == "JUNO_PHASE2"


class TestDashboard:
    def test_dashboard_json_serializable(self):
        encoded = json.dumps(DASHBOARD)
        assert "DESI_DR3" in encoded

    def test_dashboard_has_five_entries(self):
        assert len(DASHBOARD["experiments"]) == 5
