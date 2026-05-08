# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for cmbs4_ns_r_joint_falsifier.py (v10.30)."""
import math
import pytest
from src.core.cmbs4_ns_r_joint_falsifier import (
    NS_FALSIFICATION_WINDOW,
    NS_SIGMA_CMBS4,
    NS_SIGMA_PLANCK,
    R_BICEP_UPPER,
    R_FALSIFICATION_LOWER,
    R_SIGMA_CMBS4,
    UM_NS,
    UM_R,
    cmbs4_readiness_report,
    cmbs4_signal_ellipse,
    joint_ns_r_verdict,
    ns_tension,
    r_tension,
)


class TestNsTension:
    def test_um_vs_planck_lt_1sigma(self):
        result = ns_tension(0.9649, 0.0042)
        assert result["tension_sigma"] < 1.0

    def test_far_ns_gives_high_tension(self):
        result = ns_tension(0.9900, 0.0042)
        assert result["tension_sigma"] > 1.0

    def test_in_window(self):
        result = ns_tension(0.9635, 0.0042)
        assert result["in_falsification_window"] is True

    def test_outside_window_below(self):
        result = ns_tension(0.950, 0.001)
        assert result["in_falsification_window"] is False

    def test_outside_window_above(self):
        result = ns_tension(0.975, 0.001)
        assert result["in_falsification_window"] is False

    def test_falsified_only_when_precision_sufficient(self):
        # Outside window but big sigma → not falsified
        result = ns_tension(0.950, 0.010)
        assert result["falsified"] is False
        # Outside window + small sigma → falsified
        result2 = ns_tension(0.950, 0.0005)
        assert result2["falsified"] is True


class TestRTension:
    def test_r_bicep_consistent(self):
        # r < 0.036 (BICEP/Keck) → should be consistent
        result = r_tension(0.018, 0.012)
        assert not result["falsified_too_high"]

    def test_r_too_low_falsified(self):
        # r = 0.005 ± 0.001 → upper 3σ = 0.008 < 0.010 → falsified
        result = r_tension(0.005, 0.001)
        assert result["falsified_too_low"] is True

    def test_r_too_high_falsified(self):
        # r = 0.050 ± 0.003 → lower 3σ = 0.041 > 0.036 → falsified
        result = r_tension(0.050, 0.003)
        assert result["falsified_too_high"] is True

    def test_um_r_not_falsified(self):
        result = r_tension(UM_R, 0.002)
        assert result["falsified"] is False

    def test_r_tension_zero_at_um(self):
        result = r_tension(UM_R, 0.002)
        assert result["tension_sigma"] < 0.1


class TestJointNsRVerdict:
    def test_um_prediction_gives_pass(self):
        verdict = joint_ns_r_verdict(UM_NS, 0.002, UM_R, 0.001, "test", 2030)
        assert verdict["route"] == "PASS"

    def test_planck_current_gives_pass(self):
        verdict = joint_ns_r_verdict(0.9649, 0.0042, 0.020, 0.012, "Planck", 2024)
        assert verdict["route"] == "PASS"

    def test_falsification_below_r(self):
        verdict = joint_ns_r_verdict(0.9635, 0.002, 0.005, 0.001, "CMB-S4", 2030)
        assert verdict["route"] == "FALSIFIED"
        assert "r" in " ".join(verdict["reason"]).lower() or "falsified" in verdict["status"].lower()

    def test_ns_outside_window_at_precision_falsifies(self):
        verdict = joint_ns_r_verdict(0.950, 0.0005, UM_R, 0.001, "Future", 2032)
        assert verdict["route"] == "FALSIFIED"

    def test_result_has_required_keys(self):
        verdict = joint_ns_r_verdict(UM_NS, 0.002, UM_R, 0.001, "test", 2030)
        for key in ["experiment", "measurement", "ns_result", "r_result", "route", "action"]:
            assert key in verdict


class TestSignalEllipse:
    def test_centre_matches_um(self):
        ellipse = cmbs4_signal_ellipse()
        assert ellipse["centre_ns"] == UM_NS
        assert ellipse["centre_r"] == UM_R

    def test_1sigma_band_contains_centre(self):
        ellipse = cmbs4_signal_ellipse()
        ns_low, ns_high = ellipse["ns_1sigma_band"]
        assert ns_low <= UM_NS <= ns_high

    def test_cmbs4_sigma_matches_constants(self):
        ellipse = cmbs4_signal_ellipse()
        assert ellipse["cmbs4_ns_sigma"] == NS_SIGMA_CMBS4
        assert ellipse["cmbs4_r_sigma"] == R_SIGMA_CMBS4


class TestReadinessReport:
    def test_report_version(self):
        report = cmbs4_readiness_report()
        assert report["version"] == "v10.30"

    def test_report_has_scenarios(self):
        report = cmbs4_readiness_report()
        assert len(report["projection_scenarios"]) == 3

    def test_report_has_falsification_conditions(self):
        report = cmbs4_readiness_report()
        assert len(report["falsification_conditions"]) >= 3

    def test_current_status_is_pass(self):
        report = cmbs4_readiness_report()
        assert report["current_status"]["route"] == "PASS"

    def test_worst_case_scenario_not_pass(self):
        # Scenario 3: n_s high, r low → should be tension or falsified
        report = cmbs4_readiness_report()
        worst = report["projection_scenarios"][2]
        assert worst["route"] in ("TENSION", "FALSIFIED")
