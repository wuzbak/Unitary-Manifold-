# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-C++: src/core/ckm_rhobar_8d_wilson_refinement.py"""

from __future__ import annotations

import pytest

from src.core.ckm_rhobar_8d_wilson_refinement import (
    DELTA_CP_8D_REFINED_DEG,
    GATE_PASSED,
    P14_STATUS,
    RHO_BAR_8D_REFINED,
    RHO_BAR_8D_REFINED_PCT_ERR,
    WILSON_BLEND_WEIGHT,
    delta_cp_8d_refined,
    p14_hard_gates,
    rho_bar_8d_refined,
    wscpp_summary,
)


def test_blend_weight_is_unit_interval():
    assert 0.0 < WILSON_BLEND_WEIGHT < 1.0


def test_delta_refined_is_reasonable():
    d = delta_cp_8d_refined()
    assert 60.0 < d["delta_refined_deg"] < 70.0


def test_rho_bar_refined_positive():
    r = rho_bar_8d_refined()
    assert r["rho_bar"] > 0.0


def test_constant_matches_function():
    r = rho_bar_8d_refined()
    assert RHO_BAR_8D_REFINED == pytest.approx(r["rho_bar"])
    assert RHO_BAR_8D_REFINED_PCT_ERR == pytest.approx(r["pct_err_vs_pdg"])


def test_hard_gates_payload_shape():
    g = p14_hard_gates()
    assert "gates" in g
    assert "hard_gate_pass" in g
    assert {"residual_gate", "robustness_gate", "axiomzero_purity_gate"} <= set(g["gates"])


def test_status_matches_gate():
    if GATE_PASSED:
        assert P14_STATUS == "GEOMETRIC PREDICTION"
    else:
        assert P14_STATUS == "CONSTRAINED"


def test_summary_contains_expected_fields():
    s = wscpp_summary()
    assert s["workstream"] == "WS-C++"
    assert s["parameter"].startswith("P14")
    assert isinstance(s["delta_refined_deg"], float)
    assert "hard_gates" in s
    assert "verdict" in s


def test_refined_delta_constant_reasonable():
    assert 60.0 < DELTA_CP_8D_REFINED_DEG < 70.0
