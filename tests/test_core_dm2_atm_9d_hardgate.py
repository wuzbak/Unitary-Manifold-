# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/dm2_atm_9d_hardgate.py."""
from __future__ import annotations

from src.core.dm2_atm_9d_hardgate import (
    BASE_9D_GS_CORRECTION,
    CYCLE_SENSITIVITY,
    GP_THRESHOLD_PCT,
    P17_STATUS,
    P17_TOE_SCORE_DELTA,
    ROBUSTNESS_FRACTION,
    corrected_dm2_31_prediction,
    p17_hardgate_certificate,
    robustness_scan,
)


def test_constants():
    assert GP_THRESHOLD_PCT == 5.0
    assert ROBUSTNESS_FRACTION == 0.10
    assert BASE_9D_GS_CORRECTION > 0
    assert CYCLE_SENSITIVITY > 0


def test_nominal_prediction_shape():
    result = corrected_dm2_31_prediction(1.0)
    assert result["dm2_31_pred_eV2"] > 0
    assert result["residual_pct"] < GP_THRESHOLD_PCT


def test_robustness_scan_points():
    scan = robustness_scan()
    assert len(scan) == 5


def test_robustness_worst_within_gate():
    cert = p17_hardgate_certificate()
    assert cert["robustness_worst_pct"] < GP_THRESHOLD_PCT


def test_gates_all_pass():
    cert = p17_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    assert all(cert["gates"].values())


def test_status_and_delta():
    assert P17_STATUS == "GEOMETRIC_PREDICTION"
    assert abs(P17_TOE_SCORE_DELTA - 0.3) < 1e-12


def test_certificate_status_change():
    cert = p17_hardgate_certificate()
    assert cert["previous_status"] == "CONSTRAINED"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
