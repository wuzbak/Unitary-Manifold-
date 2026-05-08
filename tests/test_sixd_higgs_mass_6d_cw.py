# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/higgs_mass_6d_cw.py — WS-V P5 GEOMETRIC_ESTIMATE_CERTIFIED."""
from __future__ import annotations

import pytest

from src.sixd.higgs_mass_6d_cw import (
    K_CS, N_W, PI_KR, Y_T_GEO, M_KK_GEV, M_H_PDG, V_GEO_GEV,
    LAMBDA_H_TREE, M_H_TREE_GEV, M_H_CW_GEV,
    RESIDUAL_TREE_PCT, RESIDUAL_CW_PCT,
    GEC_THRESHOLD_PCT, GATE_PASSED, P5_STATUS, P5_TOE_SCORE_DELTA,
    lambda_h_tree, delta_lambda_cw_top, lambda_h_effective,
    m_h_tree_estimate, m_h_cw_estimate,
    p5_6d_cw_gate, p5_6d_cw_certificate, ws_v_higgs_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_k_cs():
    assert K_CS == 74


def test_n_w():
    assert N_W == 5


def test_lambda_h_tree_value():
    """λ_tree = n_w²/(2K_CS) = 25/148."""
    assert abs(LAMBDA_H_TREE - 25.0 / 148.0) < 1e-10


def test_y_t_geo():
    """y_t = 23/25 from geometric Yukawa hierarchy."""
    assert abs(Y_T_GEO - 23.0 / 25.0) < 1e-10


def test_m_kk_positive():
    assert M_KK_GEV > 0
    # KK scale should be around 1042 GeV
    assert 900 <= M_KK_GEV <= 1200


def test_v_geo_near_pdg():
    """v_geo should be within 1% of 246.22 GeV."""
    assert abs(V_GEO_GEV - 246.22) / 246.22 < 0.01


def test_m_h_pdg():
    assert abs(M_H_PDG - 125.25) < 0.01


def test_gec_threshold():
    assert GEC_THRESHOLD_PCT == 20.0


# ---------------------------------------------------------------------------
# Derived constants
# ---------------------------------------------------------------------------

def test_m_h_tree_range():
    """Tree-level m_H should be between 130 and 160 GeV (10-30% above PDG)."""
    assert 130 <= M_H_TREE_GEV <= 160


def test_m_h_tree_residual_below_20pct():
    """Tree-level residual must be < 20% (GEOMETRIC_ESTIMATE_CERTIFIED threshold)."""
    assert RESIDUAL_TREE_PCT < GEC_THRESHOLD_PCT


def test_m_h_tree_residual_near_14pct():
    """Tree-level residual expected around 14%."""
    assert 10.0 <= RESIDUAL_TREE_PCT <= 18.0


def test_m_h_cw_near_pdg():
    """CW-corrected m_H should be within 2% of PDG."""
    assert RESIDUAL_CW_PCT < 2.0


def test_gate_passed():
    assert GATE_PASSED is True


def test_p5_status():
    assert P5_STATUS == "GEOMETRIC_ESTIMATE_CERTIFIED"


def test_p5_toe_score_delta():
    assert abs(P5_TOE_SCORE_DELTA - 0.2) < 1e-10


# ---------------------------------------------------------------------------
# lambda_h_tree function
# ---------------------------------------------------------------------------

def test_lambda_h_tree_function():
    r = lambda_h_tree()
    assert "lambda_h_tree" in r
    assert abs(r["lambda_h_tree"] - 25.0 / 148.0) < 1e-10
    assert r["axiomzero_pure"] is True
    assert "formula" in r


def test_lambda_h_tree_custom():
    r = lambda_h_tree(n_w=5, k_cs=74)
    assert r["n_w"] == 5
    assert r["k_cs"] == 74


# ---------------------------------------------------------------------------
# delta_lambda_cw_top function
# ---------------------------------------------------------------------------

def test_delta_lambda_cw_negative():
    """CW correction should be negative (top quark reduces quartic)."""
    r = delta_lambda_cw_top()
    assert r["delta_lambda_cw"] < 0


def test_delta_lambda_cw_magnitude():
    """CW correction should be around -0.039."""
    r = delta_lambda_cw_top()
    assert -0.05 <= r["delta_lambda_cw"] <= -0.02


def test_delta_lambda_cw_structure():
    r = delta_lambda_cw_top()
    assert "delta_lambda_cw" in r
    assert "y_t" in r
    assert "m_kk_gev" in r
    assert "log_factor" in r
    assert r["log_factor"] > 0  # M_KK/v > 1


# ---------------------------------------------------------------------------
# lambda_h_effective function
# ---------------------------------------------------------------------------

def test_lambda_h_effective():
    r = lambda_h_effective()
    tree = r["lambda_h_tree"]
    cw = r["delta_lambda_cw"]
    eff = r["lambda_h_effective"]
    assert abs(eff - (tree + cw)) < 1e-12
    assert 0.10 <= eff <= 0.18  # should be positive and reasonable


# ---------------------------------------------------------------------------
# m_h_tree_estimate function
# ---------------------------------------------------------------------------

def test_m_h_tree_estimate_gate_pass():
    r = m_h_tree_estimate()
    assert r["gate_pass"] is True
    assert r["residual_pct"] < 20.0


def test_m_h_tree_estimate_structure():
    r = m_h_tree_estimate()
    assert "m_h_tree_gev" in r
    assert "m_h_pdg_gev" in r
    assert "lambda_h_tree" in r
    assert "v_gev" in r
    assert r["m_h_pdg_gev"] == M_H_PDG


def test_m_h_tree_estimate_formula_consistent():
    """m_H_tree = sqrt(2*lambda) * v."""
    import math
    r = m_h_tree_estimate()
    expected = math.sqrt(2.0 * r["lambda_h_tree"]) * r["v_gev"]
    assert abs(r["m_h_tree_gev"] - expected) < 0.01


# ---------------------------------------------------------------------------
# m_h_cw_estimate function
# ---------------------------------------------------------------------------

def test_m_h_cw_estimate_near_pdg():
    r = m_h_cw_estimate()
    assert r["residual_pct"] < 2.0


def test_m_h_cw_estimate_structure():
    r = m_h_cw_estimate()
    assert "m_h_cw_gev" in r
    assert "lambda_h_effective" in r
    assert "epistemic_note" in r
    assert "y_t_status" in r


def test_m_h_cw_estimate_mentions_constrained():
    """Epistemic note should flag that y_t is CONSTRAINED."""
    r = m_h_cw_estimate()
    assert "CONSTRAINED" in r["y_t_status"]


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

def test_p5_gate_certifying_estimate():
    g = p5_6d_cw_gate()
    assert g["certifying_estimate"] == "tree-level"
    assert g["gate_pass"] is True


def test_p5_gate_structure():
    g = p5_6d_cw_gate()
    assert "m_h_tree_gev" in g
    assert "residual_tree_pct" in g
    assert "m_h_cw_gev" in g
    assert "residual_cw_pct" in g
    assert "path_to_gp" in g


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_p5_certificate_new_status():
    cert = p5_6d_cw_certificate()
    assert cert["new_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert abs(cert["toe_score_delta"] - 0.2) < 1e-10


def test_p5_certificate_derivation_chain():
    cert = p5_6d_cw_certificate()
    assert len(cert["derivation_chain"]) >= 3
    assert any("n_w" in s for s in cert["derivation_chain"])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_ws_v_higgs_summary_keys():
    s = ws_v_higgs_summary()
    required = [
        "workstream", "parameter", "name", "pdg_value_gev",
        "um_tree_level_gev", "um_cw_level_gev",
        "residual_tree_pct", "residual_cw_pct",
        "gate_passed", "previous_status", "new_status",
        "toe_score_delta", "v10_20_deliverable",
        "certifying_estimate", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}'"


def test_ws_v_higgs_summary_values():
    s = ws_v_higgs_summary()
    assert s["workstream"] == "WS-V"
    assert s["parameter"] == "P5"
    assert s["gate_passed"] is True
    assert s["new_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert abs(s["toe_score_delta"] - 0.2) < 1e-10
    assert s["v10_20_deliverable"] == "higgs_mass_6d_cw.py"
    assert s["certifying_estimate"] == "tree-level (λ = n_w²/2K_CS)"
