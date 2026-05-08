# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/cmbs4_monitor.py — CMB-S4 monitoring harness."""
from __future__ import annotations

import math
import pytest

from src.core.cmbs4_monitor import (
    N_S_UM,
    N_S_PDG,
    N_S_PDG_SIGMA,
    R_UM,
    R_UPPER_LIMIT,
    CMBS4_EXPECTED_NS_SIGMA,
    CMBS4_EXPECTED_R_SIGMA,
    CMBS4_LAUNCH_YEAR,
    N_S_FALSIFICATION_WINDOW,
    R_FALSIFICATION_THRESHOLD,
    PLANCK_BASELINE,
    UM_PREDICTION,
    update_with_cmbs4_data,
    falsification_verdict_ns,
    falsification_verdict_r,
    monitoring_report,
    cmbs4_readiness_assessment,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_n_s_um_value():
    assert abs(N_S_UM - 0.9635) < 1e-10


def test_n_s_pdg_value():
    assert abs(N_S_PDG - 0.9649) < 1e-10


def test_n_s_pdg_sigma_value():
    assert abs(N_S_PDG_SIGMA - 0.0042) < 1e-10


def test_r_um_value():
    assert abs(R_UM - 0.0315) < 1e-10


def test_r_upper_limit_value():
    assert abs(R_UPPER_LIMIT - 0.036) < 1e-10


def test_cmbs4_expected_ns_sigma():
    assert abs(CMBS4_EXPECTED_NS_SIGMA - 0.002) < 1e-10


def test_cmbs4_expected_r_sigma():
    assert abs(CMBS4_EXPECTED_R_SIGMA - 0.001) < 1e-10


def test_cmbs4_launch_year():
    assert CMBS4_LAUNCH_YEAR == 2030


def test_ns_falsification_window():
    lo, hi = N_S_FALSIFICATION_WINDOW
    assert abs(lo - 0.955) < 1e-10
    assert abs(hi - 0.972) < 1e-10


def test_r_falsification_threshold():
    assert abs(R_FALSIFICATION_THRESHOLD - 0.010) < 1e-10


# ---------------------------------------------------------------------------
# Baseline dicts
# ---------------------------------------------------------------------------

def test_planck_baseline_structure():
    for key in ("release", "year", "n_s_central", "n_s_sigma", "r_upper_limit_95"):
        assert key in PLANCK_BASELINE


def test_planck_baseline_values():
    assert abs(PLANCK_BASELINE["n_s_central"] - N_S_PDG) < 1e-10
    assert abs(PLANCK_BASELINE["n_s_sigma"] - N_S_PDG_SIGMA) < 1e-10
    assert abs(PLANCK_BASELINE["r_upper_limit_95"] - R_UPPER_LIMIT) < 1e-10


def test_um_prediction_structure():
    for key in ("n_s", "r", "falsification_ns", "falsification_r"):
        assert key in UM_PREDICTION


def test_um_prediction_values():
    assert abs(UM_PREDICTION["n_s"] - N_S_UM) < 1e-10
    assert abs(UM_PREDICTION["r"] - R_UM) < 1e-10


# ---------------------------------------------------------------------------
# update_with_cmbs4_data
# ---------------------------------------------------------------------------

def test_update_returns_dict():
    result = update_with_cmbs4_data(0.9635, 0.002, 0.0315, 0.001, "test")
    assert isinstance(result, dict)


def test_update_required_keys():
    result = update_with_cmbs4_data(0.9635, 0.002, 0.0315, 0.001)
    for key in ("tension_ns_sigma", "tension_r_sigma", "ns_verdict", "r_verdict",
                "overall_consistent", "wording"):
        assert key in result


def test_update_self_consistent():
    """UM prediction vs itself should be zero tension."""
    result = update_with_cmbs4_data(N_S_UM, 0.002, R_UM, 0.001)
    assert result["tension_ns_sigma"] < 1e-10
    assert result["tension_r_sigma"] < 1e-10
    assert result["overall_consistent"] is True


def test_update_extreme_values_inconsistent():
    """Very discrepant values should be flagged as inconsistent."""
    result = update_with_cmbs4_data(0.90, 0.002, 0.001, 0.001)
    assert not result["overall_consistent"]


def test_update_planck_ns_consistent():
    """Planck n_s is only 0.33σ from UM — should be consistent."""
    result = update_with_cmbs4_data(N_S_PDG, N_S_PDG_SIGMA, R_UM, 0.001)
    assert result["ns_verdict"]["level"] == "CONSISTENT"


def test_update_wording_is_string():
    result = update_with_cmbs4_data(0.9635, 0.002, 0.0315, 0.001)
    assert isinstance(result["wording"], str)
    assert len(result["wording"]) > 0


# ---------------------------------------------------------------------------
# falsification_verdict_ns
# ---------------------------------------------------------------------------

def test_ns_verdict_consistent_for_um_prediction():
    """UM should not falsify itself."""
    result = falsification_verdict_ns(N_S_UM, 0.002)
    assert result["level"] == "CONSISTENT"


def test_ns_verdict_consistent_for_planck():
    """Planck n_s is 0.33σ from UM — consistent."""
    result = falsification_verdict_ns(N_S_PDG, N_S_PDG_SIGMA)
    assert result["level"] == "CONSISTENT"


def test_ns_verdict_excluded_far_outside():
    """n_s = 0.90 at σ = 0.0005 is far from UM and outside window."""
    result = falsification_verdict_ns(0.90, 0.0005)
    assert result["level"] == "EXCLUDED"


def test_ns_verdict_excluded_outside_window_high_precision():
    """n_s = 0.940 outside [0.955, 0.972] at σ < 0.001 → EXCLUDED."""
    result = falsification_verdict_ns(0.940, 0.0005)
    assert result["level"] == "EXCLUDED"


def test_ns_verdict_structure():
    result = falsification_verdict_ns(N_S_PDG, N_S_PDG_SIGMA)
    for key in ("parameter", "um_prediction", "observed", "sigma",
                "tension_sigma", "in_falsification_window", "level", "verdict"):
        assert key in result


def test_ns_verdict_zero_sigma_gives_inf():
    result = falsification_verdict_ns(N_S_PDG, 0.0)
    assert result["tension_sigma"] == float("inf")


def test_ns_verdict_in_window():
    result = falsification_verdict_ns(N_S_UM, 0.002)
    assert result["in_falsification_window"] is True


def test_ns_verdict_out_of_window():
    result = falsification_verdict_ns(0.940, 0.002)
    assert result["in_falsification_window"] is False


# ---------------------------------------------------------------------------
# falsification_verdict_r
# ---------------------------------------------------------------------------

def test_r_verdict_consistent_for_um_prediction():
    """UM should not falsify itself."""
    result = falsification_verdict_r(R_UM, 0.001)
    assert result["level"] == "CONSISTENT"


def test_r_verdict_excluded_below_threshold():
    """r = 0.003 ± 0.001 → r < 0.010 well below threshold at > 3σ → EXCLUDED."""
    result = falsification_verdict_r(0.003, 0.001)
    assert result["level"] == "EXCLUDED"
    assert result["falsified_by_threshold"] is True


def test_r_verdict_consistent_above_threshold():
    """r = 0.025 ± 0.005 → not below threshold at > 3σ."""
    result = falsification_verdict_r(0.025, 0.005)
    assert result["level"] == "CONSISTENT"


def test_r_verdict_structure():
    result = falsification_verdict_r(R_UM, 0.001)
    for key in ("parameter", "um_prediction", "observed", "sigma",
                "tension_sigma", "falsification_threshold", "level", "verdict"):
        assert key in result


def test_r_verdict_zero_sigma_gives_inf():
    result = falsification_verdict_r(R_UM, 0.0)
    assert result["tension_sigma"] == float("inf")


def test_r_verdict_not_falsified_by_threshold_when_above():
    """r above threshold should not be falsified by threshold logic."""
    result = falsification_verdict_r(0.020, 0.001)
    assert not result["falsified_by_threshold"]


# ---------------------------------------------------------------------------
# monitoring_report
# ---------------------------------------------------------------------------

def test_monitoring_report_returns_dict():
    report = monitoring_report()
    assert isinstance(report, dict)


def test_monitoring_report_keys():
    report = monitoring_report()
    for key in ("version", "current_baseline", "um_prediction",
                "current_ns_verdict", "next_milestone"):
        assert key in report


def test_monitoring_report_version():
    report = monitoring_report()
    assert report["version"] == "v10.17"


def test_monitoring_report_next_milestone():
    report = monitoring_report()
    assert report["next_milestone"]["experiment"] == "CMB-S4"
    assert report["next_milestone"]["expected_year"] == CMBS4_LAUNCH_YEAR


def test_monitoring_report_has_update_instructions():
    report = monitoring_report()
    assert "update_instructions" in report
    assert "update_with_cmbs4_data" in report["update_instructions"]


# ---------------------------------------------------------------------------
# cmbs4_readiness_assessment
# ---------------------------------------------------------------------------

def test_readiness_assessment_returns_dict():
    result = cmbs4_readiness_assessment()
    assert isinstance(result, dict)


def test_readiness_assessment_keys():
    result = cmbs4_readiness_assessment()
    for key in ("experiment", "launch_year", "um_predictions",
                "falsification_conditions", "expected_outcome"):
        assert key in result


def test_readiness_assessment_experiment():
    result = cmbs4_readiness_assessment()
    assert result["experiment"] == "CMB-S4"
    assert result["launch_year"] == CMBS4_LAUNCH_YEAR


def test_readiness_assessment_um_predictions():
    result = cmbs4_readiness_assessment()
    assert abs(result["um_predictions"]["n_s"] - N_S_UM) < 1e-10
    assert abs(result["um_predictions"]["r"] - R_UM) < 1e-10


def test_readiness_assessment_margin_positive():
    """UM prediction is inside the falsification window, margin must be > 0."""
    result = cmbs4_readiness_assessment()
    assert result["ns_margin_to_falsification_window_sigmas"] > 0
