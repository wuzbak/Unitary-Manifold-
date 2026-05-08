# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/hyperk_juno_monitor.py — Hyper-K / JUNO Δm²₃₁ monitoring harness."""
from __future__ import annotations

import math
import pytest

from src.core.hyperk_juno_monitor import (
    DM2_31_PDG,
    DM2_31_PDG_SIGMA_FRAC,
    DM2_31_UM_NLO,
    DM2_31_FALSIFICATION_WINDOW,
    HYPERK_EXPECTED_SIGMA_FRAC,
    JUNO_EXPECTED_SIGMA_FRAC,
    HYPERK_FIRST_DATA,
    JUNO_FIRST_DATA,
    NUFIT_BASELINE,
    UM_PREDICTION,
    update_with_measurement,
    falsification_verdict,
    monitoring_report,
    sensitivity_projection,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_dm2_31_pdg_value():
    assert abs(DM2_31_PDG - 2.453e-3) < 1e-15


def test_dm2_31_pdg_sigma_frac():
    assert abs(DM2_31_PDG_SIGMA_FRAC - 0.013) < 1e-10


def test_dm2_31_um_nlo_value():
    expected = 2.453e-3 * (1.0 - 0.0687)
    assert abs(DM2_31_UM_NLO - expected) < 1e-15


def test_dm2_31_um_nlo_below_pdg():
    """Follow-up value should be 6.87% below PDG."""
    assert DM2_31_UM_NLO < DM2_31_PDG
    frac_diff = (DM2_31_PDG - DM2_31_UM_NLO) / DM2_31_PDG
    assert abs(frac_diff - 0.0687) < 1e-10


def test_dm2_31_falsification_window():
    lo, hi = DM2_31_FALSIFICATION_WINDOW
    assert abs(lo - 2.2e-3) < 1e-15
    assert abs(hi - 2.7e-3) < 1e-15


def test_hyperk_expected_sigma_frac():
    assert abs(HYPERK_EXPECTED_SIGMA_FRAC - 0.005) < 1e-10


def test_juno_expected_sigma_frac():
    assert abs(JUNO_EXPECTED_SIGMA_FRAC - 0.005) < 1e-10


def test_hyperk_first_data_year():
    assert HYPERK_FIRST_DATA == 2027


def test_juno_first_data_year():
    assert JUNO_FIRST_DATA == 2026


def test_um_nlo_in_falsification_window():
    """UM NLO value should be inside the falsification window."""
    lo, hi = DM2_31_FALSIFICATION_WINDOW
    assert lo < DM2_31_UM_NLO < hi


# ---------------------------------------------------------------------------
# Baseline dicts
# ---------------------------------------------------------------------------

def test_nufit_baseline_structure():
    for key in ("release", "year", "dm2_31_central", "dm2_31_sigma_frac", "status"):
        assert key in NUFIT_BASELINE


def test_nufit_baseline_values():
    assert abs(NUFIT_BASELINE["dm2_31_central"] - DM2_31_PDG) < 1e-15
    assert abs(NUFIT_BASELINE["dm2_31_sigma_frac"] - DM2_31_PDG_SIGMA_FRAC) < 1e-10


def test_um_prediction_structure():
    for key in ("dm2_31_nlo", "mechanism", "falsification", "current_status"):
        assert key in UM_PREDICTION


def test_um_prediction_nlo_value():
    assert abs(UM_PREDICTION["dm2_31_nlo"] - DM2_31_UM_NLO) < 1e-15


# ---------------------------------------------------------------------------
# update_with_measurement
# ---------------------------------------------------------------------------

def test_update_returns_dict():
    result = update_with_measurement(DM2_31_PDG, DM2_31_PDG_SIGMA_FRAC, "test", 2026)
    assert isinstance(result, dict)


def test_update_required_keys():
    result = update_with_measurement(DM2_31_PDG, DM2_31_PDG_SIGMA_FRAC)
    for key in ("tension_sigma", "baseline_tension_sigma",
                "falsification_verdict", "overall_consistent", "wording"):
        assert key in result


def test_update_self_consistent_nlo():
    """UM NLO vs itself at tiny sigma → zero tension."""
    result = update_with_measurement(DM2_31_UM_NLO, 1e-6, "self_test", 2026)
    assert result["tension_sigma"] < 1e-6
    assert result["overall_consistent"] is True


def test_update_extreme_inconsistent():
    """Δm²₃₁ = 5.0e-3 eV² is far outside window and UM."""
    result = update_with_measurement(5.0e-3, 0.005, "extreme", 2028)
    assert not result["overall_consistent"]


def test_update_wording_is_string():
    result = update_with_measurement(DM2_31_PDG, 0.01, "JUNO Year 1", 2026)
    assert isinstance(result["wording"], str)
    assert len(result["wording"]) > 0


def test_update_sigma_abs_computed_correctly():
    result = update_with_measurement(2.453e-3, 0.01, "test", 2026)
    expected_sigma_abs = 2.453e-3 * 0.01
    assert abs(result["dm2_31_sigma_abs"] - expected_sigma_abs) < 1e-15


def test_update_year_stored():
    result = update_with_measurement(DM2_31_PDG, 0.005, "Hyper-K", 2028)
    assert result["year"] == 2028


# ---------------------------------------------------------------------------
# falsification_verdict
# ---------------------------------------------------------------------------

def test_verdict_consistent_for_nlo_at_small_sigma():
    """UM NLO vs itself at small σ → CONSISTENT."""
    result = falsification_verdict(DM2_31_UM_NLO, 1e-6)
    assert result["level"] == "CONSISTENT"


def test_verdict_excluded_far_outside_window():
    """Δm²₃₁ = 5.0e-3 eV² at 0.1% → far outside [2.2, 2.7]×10⁻³ and > 3σ from UM NLO."""
    result = falsification_verdict(5.0e-3, 0.001)
    assert result["level"] == "EXCLUDED"


def test_verdict_excluded_outside_window_high_precision():
    """Δm²₃₁ = 2.1e-3 eV² (below 2.2e-3 window) at σ < 1% → EXCLUDED."""
    result = falsification_verdict(2.1e-3, 0.005)
    assert result["level"] == "EXCLUDED"


def test_verdict_structure():
    result = falsification_verdict(DM2_31_PDG, DM2_31_PDG_SIGMA_FRAC)
    for key in ("parameter", "um_prediction_nlo", "observed", "sigma_frac",
                "sigma_abs", "tension_sigma", "in_falsification_window",
                "level", "verdict"):
        assert key in result


def test_verdict_zero_sigma_gives_inf():
    result = falsification_verdict(DM2_31_PDG, 0.0)
    assert result["tension_sigma"] == float("inf")


def test_verdict_in_window_for_nlo():
    result = falsification_verdict(DM2_31_UM_NLO, 0.005)
    assert result["in_falsification_window"] is True


def test_verdict_not_in_window_for_extreme():
    result = falsification_verdict(5.0e-3, 0.005)
    assert result["in_falsification_window"] is False


def test_verdict_pdg_central_high_tension():
    """PDG central vs UM NLO at PDG sigma → high tension (documented open problem)."""
    result = falsification_verdict(DM2_31_PDG, DM2_31_PDG_SIGMA_FRAC)
    # 6.87% offset / 1.3% sigma ≈ 5.3σ → EXCLUDED
    assert result["tension_sigma"] > 3.0
    assert result["level"] == "EXCLUDED"


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
    assert report["version"] == "v10.18"


def test_monitoring_report_next_milestone():
    report = monitoring_report()
    ms = report["next_milestone"]
    assert "JUNO" in ms["experiments"]
    assert "Hyper-Kamiokande" in ms["experiments"]
    assert ms["juno_first_data"] == JUNO_FIRST_DATA
    assert ms["hyperk_first_data"] == HYPERK_FIRST_DATA


def test_monitoring_report_has_update_instructions():
    report = monitoring_report()
    assert "update_instructions" in report
    assert "update_with_measurement" in report["update_instructions"]


# ---------------------------------------------------------------------------
# sensitivity_projection
# ---------------------------------------------------------------------------

def test_sensitivity_projection_returns_dict():
    result = sensitivity_projection()
    assert isinstance(result, dict)


def test_sensitivity_projection_keys():
    result = sensitivity_projection()
    for key in ("um_prediction_nlo_eV2", "pdg_central_eV2",
                "falsification_window_eV2", "juno", "hyperk",
                "falsification_condition"):
        assert key in result


def test_sensitivity_projection_juno_structure():
    result = sensitivity_projection()
    juno = result["juno"]
    for key in ("experiment", "first_data_year", "expected_sigma_frac"):
        assert key in juno
    assert juno["experiment"] == "JUNO"
    assert juno["first_data_year"] == JUNO_FIRST_DATA


def test_sensitivity_projection_hyperk_structure():
    result = sensitivity_projection()
    hk = result["hyperk"]
    for key in ("experiment", "first_data_year", "expected_sigma_frac"):
        assert key in hk
    assert hk["experiment"] == "Hyper-Kamiokande"
    assert hk["first_data_year"] == HYPERK_FIRST_DATA


def test_sensitivity_projection_um_value():
    result = sensitivity_projection()
    assert abs(result["um_prediction_nlo_eV2"] - DM2_31_UM_NLO) < 1e-15


def test_sensitivity_projection_margins_positive():
    result = sensitivity_projection()
    for exp_key in ("juno", "hyperk"):
        assert result[exp_key]["margin_to_lower_window_edge_sigma"] > 0
        assert result[exp_key]["margin_to_upper_window_edge_sigma"] > 0
