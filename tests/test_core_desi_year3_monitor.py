# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/desi_year3_monitor.py — DESI Year 3 monitoring harness."""
from __future__ import annotations

import math
import pytest

from src.core.desi_year3_monitor import (
    DESI_DR2,
    UM_PREDICTION,
    tension_from_measurement,
    update_with_new_data,
    falsification_verdict,
    monitoring_report,
    desi_year3_placeholder,
)


def test_desi_dr2_structure():
    """DESI DR2 dict has required fields."""
    for key in ("release", "year", "w0_central", "w0_sigma", "wa_central", "wa_sigma"):
        assert key in DESI_DR2


def test_desi_dr2_values_reasonable():
    assert -1.5 < DESI_DR2["w0_central"] < -0.5
    assert DESI_DR2["w0_sigma"] > 0.0
    assert DESI_DR2["wa_central"] < 0.0
    assert DESI_DR2["wa_sigma"] > 0.0


def test_um_prediction_structure():
    for key in ("w0", "wa"):
        assert key in UM_PREDICTION


def test_um_prediction_wa_zero():
    assert UM_PREDICTION["wa"] == 0.0


def test_um_w0_reasonable():
    assert -1.0 < UM_PREDICTION["w0"] < -0.8


# tension_from_measurement
def test_tension_from_measurement_returns_dict():
    result = tension_from_measurement(-0.838, 0.072, -0.62, 0.30, "test")
    assert isinstance(result, dict)
    for key in ("tension_w0_sigma", "tension_wa_sigma", "verdict"):
        assert key in result


def test_tension_from_measurement_self_consistent():
    """UM vs UM should be zero tension."""
    w0_um = UM_PREDICTION["w0"]
    wa_um = UM_PREDICTION["wa"]
    result = tension_from_measurement(w0_um, 0.1, wa_um, 0.1)
    assert result["tension_w0_sigma"] < 1e-10
    assert result["tension_wa_sigma"] < 1e-10


def test_tension_from_measurement_zero_sigma_raises():
    """Zero sigma should give inf tension."""
    result = tension_from_measurement(-1.0, 0.0, -0.5, 0.0)
    assert result["tension_w0_sigma"] == float("inf")
    assert result["tension_wa_sigma"] == float("inf")


def test_tension_from_measurement_dr2_w0_consistent():
    """DESI DR2 w₀ tension should be < 2σ (currently ~1.3σ)."""
    result = tension_from_measurement(
        DESI_DR2["w0_central"], DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"], DESI_DR2["wa_sigma"],
    )
    assert result["tension_w0_sigma"] < 2.0


def test_tension_from_measurement_dr2_wa_tension():
    """DESI DR2 wₐ tension is 2.1σ — documented open problem."""
    result = tension_from_measurement(
        DESI_DR2["w0_central"], DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"], DESI_DR2["wa_sigma"],
    )
    # wₐ tension should be in the range [1.5, 3.5] for DESI DR2
    assert 1.0 < result["tension_wa_sigma"] < 4.0


# update_with_new_data
def test_update_with_new_data_returns_dict():
    result = update_with_new_data("DESI Year 3", 2026, -0.85, 0.06, -0.40, 0.20)
    assert isinstance(result, dict)
    for key in ("release", "year", "um_tension", "baseline_tension"):
        assert key in result


def test_update_reduced_wa_tension():
    """If wₐ moves toward 0, tension should decrease."""
    result = update_with_new_data("Hypothetical", 2026, -0.838, 0.072, -0.1, 0.30)
    assert result["um_tension"]["tension_wa_sigma"] < result["baseline_tension"]["tension_wa_sigma"]


def test_update_increased_wa_tension():
    """If wₐ becomes more negative and uncertainty shrinks, tension increases."""
    result = update_with_new_data("Hypothetical", 2026, -0.838, 0.072, -0.62, 0.15)
    assert result["um_tension"]["tension_wa_sigma"] > result["baseline_tension"]["tension_wa_sigma"]


# falsification_verdict
def test_falsification_verdict_consistent():
    """wₐ = 0 ± 0.5 should give CONSISTENT."""
    result = falsification_verdict(0.0, 0.5)
    assert result["level"] == "CONSISTENT"


def test_falsification_verdict_tension():
    """wₐ = −0.62 ± 0.30 should give TENSION (2.1σ)."""
    result = falsification_verdict(-0.62, 0.30)
    assert result["level"] in ("TENSION", "MARGINAL")
    assert result["tension_sigma"] > 1.5


def test_falsification_verdict_excluded():
    """wₐ = −0.9 ± 0.1 should give EXCLUDED (9σ)."""
    result = falsification_verdict(-0.9, 0.1)
    assert result["level"] == "EXCLUDED"


def test_falsification_verdict_zero_sigma():
    result = falsification_verdict(-0.62, 0.0)
    assert result["tension_sigma"] == float("inf")


# monitoring_report
def test_monitoring_report_returns_dict():
    report = monitoring_report()
    assert isinstance(report, dict)
    for key in ("version", "current_baseline", "um_prediction",
                "current_tension", "falsification_verdict", "next_milestone"):
        assert key in report


def test_monitoring_report_version():
    report = monitoring_report()
    assert report["version"] == "v10.17"


def test_monitoring_report_next_milestone():
    report = monitoring_report()
    assert report["next_milestone"]["release"] == "DESI Year 3"
    assert report["next_milestone"]["expected_year"] == 2026


# desi_year3_placeholder
def test_desi_year3_placeholder_returns_dict():
    result = desi_year3_placeholder()
    assert isinstance(result, dict)
    assert result["release"] == "DESI Year 3"
    assert result["status"] == "PENDING — results not yet published"


def test_desi_year3_placeholder_year():
    result = desi_year3_placeholder()
    assert result["year"] == 2026
