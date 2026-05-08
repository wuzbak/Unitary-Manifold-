# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for desi_y3_joint_routing.py (v10.30)."""
import math
import pytest
from src.core.desi_y3_joint_routing import (
    DOWNSTREAM_UPDATE_TARGETS,
    Y3_SCENARIOS,
    chi2_joint,
    falsification_probability_forecast,
    joint_routing_decision,
    scenario_analysis,
    thirty_day_integration_protocol,
    y3_full_routing_report,
)


class TestChi2Joint:
    def test_zero_tension_gives_zero_chi2(self):
        from src.core.desi_year3_monitor import UM_PREDICTION
        result = chi2_joint(
            UM_PREDICTION["w0"], 0.1,
            UM_PREDICTION["wa"], 0.1,
        )
        assert result["chi2"] < 1e-10
        assert result["sigma_equiv"] < 1e-5

    def test_high_tension_gives_large_chi2(self):
        result = chi2_joint(-0.5, 0.05, 0.5, 0.05)
        assert result["chi2"] > 4.0

    def test_independent_axes_add_in_quadrature(self):
        result = chi2_joint(-0.9, 0.1, 0.3, 0.1)
        dw0 = (-0.9302 - (-0.9)) / 0.1  # ≈ -0.0302
        dwa = (0 - 0.3) / 0.1           # = -3.0
        expected_chi2 = dw0**2 + dwa**2
        assert abs(result["chi2"] - expected_chi2) < 0.01

    def test_sigma_equiv_nonnegative(self):
        result = chi2_joint(-0.838, 0.072, -0.62, 0.30)
        assert result["sigma_equiv"] >= 0.0

    def test_with_nonzero_correlation(self):
        result = chi2_joint(-0.838, 0.072, -0.62, 0.30, rho=0.5)
        result_no_corr = chi2_joint(-0.838, 0.072, -0.62, 0.30, rho=0.0)
        # With positive correlation, chi2 changes
        assert result["chi2"] != result_no_corr["chi2"]


class TestJointRoutingDecision:
    def test_consistent_returns_pass(self):
        from src.core.desi_year3_monitor import UM_PREDICTION
        result = joint_routing_decision(
            UM_PREDICTION["w0"], 0.5,
            UM_PREDICTION["wa"], 0.5,
        )
        assert result["combined_route"] == "PASS"

    def test_wa_3sigma_returns_falsified(self):
        result = joint_routing_decision(
            -0.838, 0.072,
            -0.62, 0.18,   # Y1 central with tighter errors → >3σ
        )
        assert result["combined_route"] in ("FALSIFIED", "TENSION")

    def test_desi_dr2_is_tension(self):
        result = joint_routing_decision(
            -0.838, 0.072,
            -0.62, 0.30,
        )
        assert result["combined_route"] == "TENSION"

    def test_returns_downstream_targets(self):
        result = joint_routing_decision(-0.93, 0.07, -0.10, 0.20)
        assert "downstream_update_targets" in result
        assert len(result["downstream_update_targets"]) > 0

    def test_result_has_1d_and_2d_routing(self):
        result = joint_routing_decision(-0.838, 0.072, -0.62, 0.30)
        assert "1d_routing" in result
        assert "2d_routing" in result
        assert "combined_route" in result


class TestScenarioAnalysis:
    def test_all_scenarios_run(self):
        results = scenario_analysis()
        assert len(results) == len(Y3_SCENARIOS)

    def test_s4_resolved_returns_pass(self):
        results = scenario_analysis()
        s4 = next(r for r in results if "S4" in r["release"])
        assert s4["combined_route"] == "PASS"

    def test_s6_falsification_returns_falsified(self):
        results = scenario_analysis()
        s6 = next(r for r in results if "S6" in r["release"])
        assert s6["combined_route"] in ("FALSIFIED", "TENSION")

    def test_all_results_have_route(self):
        results = scenario_analysis()
        for r in results:
            assert r["combined_route"] in ("PASS", "TENSION", "FALSIFIED")


class TestFalsificationForecast:
    def test_forecast_decreasing_sigma(self):
        forecast = falsification_probability_forecast()
        assert len(forecast) > 0
        # Tension should generally increase as σ decreases
        tensions = [f["wa_tension_sigma"] for f in forecast]
        # First entry (large σ) should have lower tension than last (small σ)
        assert tensions[0] <= tensions[-1]

    def test_all_entries_have_required_keys(self):
        forecast = falsification_probability_forecast()
        for f in forecast:
            assert "sigma_wa" in f
            assert "wa_tension_sigma" in f
            assert "route" in f


class TestThirtyDayProtocol:
    def test_protocol_has_steps(self):
        protocol = thirty_day_integration_protocol()
        assert len(protocol["steps"]) >= 8

    def test_protocol_has_deadline(self):
        protocol = thirty_day_integration_protocol()
        assert "30 days" in protocol["deadline"]

    def test_all_steps_numbered(self):
        protocol = thirty_day_integration_protocol()
        step_nums = [s["step"] for s in protocol["steps"]]
        assert step_nums == list(range(1, len(step_nums) + 1))

    def test_downstream_targets_populated(self):
        assert len(DOWNSTREAM_UPDATE_TARGETS) >= 6
        for target in DOWNSTREAM_UPDATE_TARGETS:
            assert "artifact" in target
            assert "update" in target


class TestFullReport:
    def test_report_has_version(self):
        report = y3_full_routing_report()
        assert report["version"] == "v10.30"

    def test_report_scenarios_covered(self):
        report = y3_full_routing_report()
        assert report["scenarios_covered"] == 9

    def test_report_baseline_is_desi_dr2(self):
        report = y3_full_routing_report()
        assert "DESI DR2" in report["baseline"]["release"]

    def test_report_y3_status_pending(self):
        report = y3_full_routing_report()
        assert "PENDING" in report["y3_status"]
