# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/dune_dcp_monitor.py — DUNE δ_CP monitoring harness."""
from __future__ import annotations

import math
import pytest

from src.core.dune_dcp_monitor import (
    DCP_UM,
    DCP_PI3,
    DCP_PDG,
    DCP_PDG_SIGMA,
    DCP_FALSIFICATION_WINDOW,
    DUNE_EXPECTED_SIGMA,
    DUNE_FIRST_PHYSICS,
    DUNE_FULL_STATISTICS,
    PDG_BASELINE,
    UM_PREDICTION,
    update_with_dune_data,
    falsification_verdict,
    monitoring_report,
    dune_sensitivity_projection,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_dcp_um_value():
    expected = math.pi / 3.0 + (9.0 / 74.0) * 0.05
    assert abs(DCP_UM - expected) < 1e-12


def test_dcp_pi3_value():
    assert abs(DCP_PI3 - math.pi / 3.0) < 1e-12


def test_dcp_pdg_value():
    assert abs(DCP_PDG - 1.20) < 1e-10


def test_dcp_pdg_sigma_value():
    assert abs(DCP_PDG_SIGMA - 0.20) < 1e-10


def test_dcp_falsification_window():
    lo, hi = DCP_FALSIFICATION_WINDOW
    assert abs(lo - 0.85) < 1e-10
    assert abs(hi - 1.30) < 1e-10


def test_dune_expected_sigma():
    assert abs(DUNE_EXPECTED_SIGMA - 0.05) < 1e-10


def test_dune_first_physics():
    assert DUNE_FIRST_PHYSICS == 2028


def test_dune_full_statistics():
    assert DUNE_FULL_STATISTICS == 2032


def test_dcp_um_in_falsification_window():
    lo, hi = DCP_FALSIFICATION_WINDOW
    assert lo < DCP_UM < hi


# ---------------------------------------------------------------------------
# Baseline dicts
# ---------------------------------------------------------------------------

def test_pdg_baseline_structure():
    for key in ("release", "year", "dcp_central", "dcp_sigma", "status"):
        assert key in PDG_BASELINE


def test_pdg_baseline_values():
    assert abs(PDG_BASELINE["dcp_central"] - DCP_PDG) < 1e-10
    assert abs(PDG_BASELINE["dcp_sigma"] - DCP_PDG_SIGMA) < 1e-10


def test_um_prediction_structure():
    for key in ("dcp", "mechanism", "falsification", "current_status"):
        assert key in UM_PREDICTION


def test_um_prediction_dcp_value():
    assert abs(UM_PREDICTION["dcp"] - DCP_UM) < 1e-12


# ---------------------------------------------------------------------------
# update_with_dune_data
# ---------------------------------------------------------------------------

def test_update_returns_dict():
    result = update_with_dune_data(DCP_UM, 0.05, "DUNE Year 1", 2028)
    assert isinstance(result, dict)


def test_update_required_keys():
    result = update_with_dune_data(DCP_UM, 0.05, "test", 2028)
    for key in ("tension_sigma", "baseline_tension_sigma",
                "falsification_verdict", "overall_consistent", "wording"):
        assert key in result


def test_update_self_consistent():
    """UM prediction vs itself should be zero tension and consistent."""
    result = update_with_dune_data(DCP_UM, 0.05)
    assert result["tension_sigma"] < 1e-10
    assert result["overall_consistent"] is True


def test_update_extreme_inconsistent():
    """δ_CP = 3.0 ± 0.05 is far from UM."""
    result = update_with_dune_data(3.0, 0.05, "extreme", 2030)
    assert not result["overall_consistent"]


def test_update_pdg_central_consistent():
    """PDG central 1.20 ± 0.20 rad → UM is 0.08σ away — consistent."""
    result = update_with_dune_data(DCP_PDG, DCP_PDG_SIGMA, "PDG", 2023)
    assert result["overall_consistent"] is True


def test_update_wording_is_string():
    result = update_with_dune_data(1.20, 0.05, "DUNE Year 1", 2028)
    assert isinstance(result["wording"], str)
    assert len(result["wording"]) > 0


def test_update_year_stored():
    result = update_with_dune_data(1.20, 0.05, "DUNE", 2029)
    assert result["year"] == 2029


# ---------------------------------------------------------------------------
# falsification_verdict
# ---------------------------------------------------------------------------

def test_verdict_consistent_for_um_prediction():
    """UM should not falsify itself."""
    result = falsification_verdict(DCP_UM, 0.05)
    assert result["level"] == "CONSISTENT"


def test_verdict_consistent_for_pdg():
    """PDG δ_CP = 1.20 ± 0.20 rad → 0.08σ from UM — consistent."""
    result = falsification_verdict(DCP_PDG, DCP_PDG_SIGMA)
    assert result["level"] == "CONSISTENT"


def test_verdict_excluded_far_outside():
    """δ_CP = 3.0 ± 0.05 rad → far outside window and > 3σ from UM."""
    result = falsification_verdict(3.0, 0.05)
    assert result["level"] == "EXCLUDED"


def test_verdict_excluded_outside_window_high_precision():
    """δ_CP = 0.50 ± 0.01 rad → outside [0.85, 1.30] at σ/μ < 3%."""
    result = falsification_verdict(0.50, 0.005)
    assert result["level"] == "EXCLUDED"


def test_verdict_structure():
    result = falsification_verdict(DCP_PDG, DCP_PDG_SIGMA)
    for key in ("parameter", "um_prediction", "observed", "sigma",
                "tension_sigma", "in_falsification_window", "level", "verdict"):
        assert key in result


def test_verdict_zero_sigma_gives_inf():
    result = falsification_verdict(1.20, 0.0)
    assert result["tension_sigma"] == float("inf")


def test_verdict_in_window_for_um():
    result = falsification_verdict(DCP_UM, 0.05)
    assert result["in_falsification_window"] is True


def test_verdict_not_in_window_for_extreme():
    result = falsification_verdict(0.50, 0.05)
    assert result["in_falsification_window"] is False


def test_verdict_marginal_level():
    """~2σ tension → MARGINAL."""
    result = falsification_verdict(DCP_UM + 2.1 * 0.05, 0.05)
    assert result["level"] in ("MARGINAL", "EXCLUDED")
    assert result["tension_sigma"] > 2.0


# ---------------------------------------------------------------------------
# monitoring_report
# ---------------------------------------------------------------------------

def test_monitoring_report_returns_dict():
    report = monitoring_report()
    assert isinstance(report, dict)


def test_monitoring_report_keys():
    report = monitoring_report()
    for key in ("version", "current_baseline", "um_prediction",
                "current_verdict", "next_milestone"):
        assert key in report


def test_monitoring_report_version():
    report = monitoring_report()
    assert report["version"] == "v10.17"


def test_monitoring_report_next_milestone():
    report = monitoring_report()
    assert report["next_milestone"]["experiment"] == "DUNE"
    assert report["next_milestone"]["first_physics"] == DUNE_FIRST_PHYSICS


def test_monitoring_report_has_update_instructions():
    report = monitoring_report()
    assert "update_instructions" in report
    assert "update_with_dune_data" in report["update_instructions"]


# ---------------------------------------------------------------------------
# dune_sensitivity_projection
# ---------------------------------------------------------------------------

def test_sensitivity_projection_returns_dict():
    result = dune_sensitivity_projection()
    assert isinstance(result, dict)


def test_sensitivity_projection_keys():
    result = dune_sensitivity_projection()
    for key in ("experiment", "um_prediction_rad", "current_pdg",
                "dune_timeline", "falsification_condition"):
        assert key in result


def test_sensitivity_projection_experiment():
    result = dune_sensitivity_projection()
    assert result["experiment"] == "DUNE"


def test_sensitivity_projection_timeline():
    result = dune_sensitivity_projection()
    assert result["dune_timeline"]["expected_sigma_rad"] == DUNE_EXPECTED_SIGMA
    assert result["dune_timeline"]["first_physics"] == DUNE_FIRST_PHYSICS


def test_sensitivity_projection_margins_positive():
    result = dune_sensitivity_projection()
    assert result["falsification_window_margins"]["margin_to_lower_edge_sigma"] > 0
    assert result["falsification_window_margins"]["margin_to_upper_edge_sigma"] > 0


def test_sensitivity_projection_um_prediction():
    result = dune_sensitivity_projection()
    assert abs(result["um_prediction_rad"] - DCP_UM) < 1e-12
