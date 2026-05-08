# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-B++: src/core/neutrino_absolute_scale_closure_attempt.py"""

from __future__ import annotations

import pytest

from src.core.neutrino_absolute_scale_closure_attempt import (
    DM2_21_PDG_EV2,
    DM2_31_PCT_ERR,
    DM2_31_PDG_EV2,
    DM2_31_PRED_EV2,
    GATE_PASSED,
    M1_FLOOR_EV,
    P19_STATUS,
    P20_STATUS,
    P21_STATUS,
    SUM_MNU_PDG_BOUND_EV,
    absolute_scale_predictions,
    calibrate_neutrino_scale,
    promotion_rubric,
    uncertainty_budget,
    wsbpp_summary,
)


def test_calibration_matches_dm2_21_target():
    c = calibrate_neutrino_scale()
    assert c["dm2_21_target_ev2"] == pytest.approx(DM2_21_PDG_EV2)
    assert c["scale_ev2"] == pytest.approx(DM2_21_PDG_EV2)


def test_absolute_predictions_are_physical():
    p = absolute_scale_predictions()
    assert p["m1_ev"] >= 0.0
    assert p["m2_ev"] > p["m1_ev"]
    assert p["m3_ev"] > p["m2_ev"]
    assert p["sum_mnu_ev"] <= SUM_MNU_PDG_BOUND_EV


def test_dm2_31_constants_consistent():
    p = absolute_scale_predictions()
    assert DM2_31_PRED_EV2 == pytest.approx(p["dm2_31_pred_ev2"])
    assert DM2_31_PCT_ERR == pytest.approx(p["dm2_31_pct_err"])
    assert DM2_31_PDG_EV2 > 0.0


def test_promotion_rubric_has_all_gates():
    r = promotion_rubric()
    assert {"dm2_21_gate", "dm2_31_gate", "sum_mnu_gate", "axiomzero_purity_gate"} <= set(r["gates"])
    assert isinstance(r["hard_gate_pass"], bool)


def test_statuses_are_honest():
    assert P19_STATUS == "CONSTRAINED"
    assert P20_STATUS == "GEOMETRIC ESTIMATE"
    assert P21_STATUS == "GEOMETRIC ESTIMATE"
    assert GATE_PASSED is False


def test_uncertainty_budget_has_blocker():
    b = uncertainty_budget()
    assert "promotion_blocker" in b
    assert "Δm²31" in b["promotion_blocker"] or "residual" in b["promotion_blocker"]


def test_summary_shape():
    s = wsbpp_summary()
    assert s["workstream"] == "WS-B++"
    assert s["parameters"] == ["P19", "P20", "P21"]
    assert "predictions" in s
    assert "promotion_rubric" in s
    assert isinstance(M1_FLOOR_EV, float)
