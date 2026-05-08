# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/ew_boson_hardgate_cert.py — P21/P22 GEOMETRIC_PREDICTION."""
from __future__ import annotations

import math
import pytest

from src.core.ew_boson_hardgate_cert import (
    SIN2_TW_GEO, ALPHA_0_GEO, V_GEO_GEV,
    DELTA_ALPHA_LEPT, DELTA_ALPHA_HAD5, DELTA_ALPHA_TOTAL, ALPHA_AT_MZ,
    G_F_GEO, M_W_PDG, M_Z_PDG,
    M_W_PRED, M_Z_PRED, RESIDUAL_W_PCT, RESIDUAL_Z_PCT,
    GP_THRESHOLD_PCT, GATE_W_PASS, GATE_Z_PASS, ALL_GATES_PASS,
    P21_STATUS, P22_STATUS, TOE_SCORE_DELTA,
    alpha_running_sm, g_fermi_geometric, ew_boson_masses,
    p21_nominal_gate, p22_nominal_gate,
    p21_p22_robustness_gate, p21_p22_axiomzero_gate,
    p21_p22_hardgate_certificate, ew_bosons_upgrade_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_gp_threshold():
    assert GP_THRESHOLD_PCT == 5.0


def test_m_w_pdg():
    assert abs(M_W_PDG - 80.377) < 0.001


def test_m_z_pdg():
    assert abs(M_Z_PDG - 91.1876) < 0.001


def test_sin2_tw_geo_range():
    """sin²θ_W should be around 0.231."""
    assert 0.228 <= SIN2_TW_GEO <= 0.234


def test_alpha_0_geo():
    """α_0 should be near 1/137.0."""
    assert abs(ALPHA_0_GEO - 1.0 / 137.0) < 1e-6


def test_v_geo_range():
    """v_geo should be within 1% of 246.22 GeV."""
    assert 243 <= V_GEO_GEV <= 249


# ---------------------------------------------------------------------------
# Running α
# ---------------------------------------------------------------------------

def test_delta_alpha_lept_positive():
    assert DELTA_ALPHA_LEPT > 0


def test_delta_alpha_lept_range():
    """Leptonic running should be around 0.035."""
    assert 0.030 <= DELTA_ALPHA_LEPT <= 0.040


def test_delta_alpha_had5():
    assert abs(DELTA_ALPHA_HAD5 - 0.027613) < 1e-6


def test_alpha_at_mz_range():
    """α(M_Z) ≈ 1/128, so about 0.0078."""
    assert 0.0075 <= ALPHA_AT_MZ <= 0.0085


def test_alpha_at_mz_inv():
    """1/α(M_Z) should be around 127-129."""
    assert 126 <= 1.0 / ALPHA_AT_MZ <= 130


# ---------------------------------------------------------------------------
# G_F
# ---------------------------------------------------------------------------

def test_g_fermi_geo_positive():
    assert G_F_GEO > 0


def test_g_fermi_geo_near_pdg():
    """G_F_geo should be within 0.5% of PDG G_F."""
    assert abs(G_F_GEO - 1.1663787e-5) / 1.1663787e-5 < 0.005


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

def test_m_w_pred_range():
    """M_W_pred should be between 78 and 83 GeV."""
    assert 78 <= M_W_PRED <= 83


def test_m_z_pred_range():
    """M_Z_pred should be between 89 and 93 GeV."""
    assert 89 <= M_Z_PRED <= 93


def test_residual_w_below_5pct():
    assert RESIDUAL_W_PCT < GP_THRESHOLD_PCT


def test_residual_z_below_5pct():
    assert RESIDUAL_Z_PCT < GP_THRESHOLD_PCT


def test_residual_w_below_2pct():
    """M_W residual should be below 2%."""
    assert RESIDUAL_W_PCT < 2.0


def test_residual_z_below_1pct():
    """M_Z residual should be below 1%."""
    assert RESIDUAL_Z_PCT < 1.0


def test_m_z_from_m_w_cos():
    """M_Z should equal M_W / cos(θ_W)."""
    cos_tw = math.sqrt(1.0 - SIN2_TW_GEO)
    assert abs(M_Z_PRED - M_W_PRED / cos_tw) < 0.001


# ---------------------------------------------------------------------------
# Gate flags
# ---------------------------------------------------------------------------

def test_gate_w_pass():
    assert GATE_W_PASS is True


def test_gate_z_pass():
    assert GATE_Z_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_p21_status():
    assert P21_STATUS == "GEOMETRIC_PREDICTION"


def test_p22_status():
    assert P22_STATUS == "GEOMETRIC_PREDICTION"


def test_toe_score_delta():
    """P21 + P22 together give +0.6 pts."""
    assert abs(TOE_SCORE_DELTA - 0.6) < 1e-10


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def test_alpha_running_sm_structure():
    r = alpha_running_sm()
    assert "alpha_0" in r
    assert "alpha_mz" in r
    assert "alpha_inv_mz" in r
    assert "delta_alpha_lept" in r
    assert "delta_alpha_had5" in r
    assert "delta_alpha_total" in r


def test_alpha_running_sm_increases():
    """α(M_Z) > α(0) i.e. α runs to larger values (1/α decreases)."""
    r = alpha_running_sm()
    assert r["alpha_mz"] > r["alpha_0"]
    assert r["alpha_inv_mz"] < r["alpha_inv_0"]


def test_g_fermi_geometric_structure():
    r = g_fermi_geometric()
    assert "G_F_geo" in r
    assert "G_F_pdg" in r
    assert "residual_pct" in r
    assert r["residual_pct"] < 0.5   # within 0.5% of PDG


def test_ew_boson_masses_structure():
    r = ew_boson_masses()
    assert "M_W_pred_gev" in r
    assert "M_Z_pred_gev" in r
    assert "residual_W_pct" in r
    assert "residual_Z_pct" in r
    assert "inputs_used" in r


def test_ew_boson_masses_residuals():
    r = ew_boson_masses()
    assert r["residual_W_pct"] < 5.0
    assert r["residual_Z_pct"] < 5.0


# ---------------------------------------------------------------------------
# Gate functions
# ---------------------------------------------------------------------------

def test_p21_gate_structure():
    g = p21_nominal_gate()
    assert g["gate"] == "p21_nominal"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0


def test_p22_gate_structure():
    g = p22_nominal_gate()
    assert g["gate"] == "p22_nominal"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0


def test_robustness_gate_structure():
    g = p21_p22_robustness_gate()
    assert g["gate"] == "robustness"
    assert g["gate_pass"] is True
    assert g["worst_W_pct"] < 5.0
    assert g["worst_Z_pct"] < 5.0


def test_axiomzero_gate_structure():
    g = p21_p22_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "um_prediction_inputs" in g
    assert "sm_inputs_not_free_params" in g


def test_axiomzero_gate_sm_inputs_listed():
    g = p21_p22_axiomzero_gate()
    # Δα_had must be listed as SM (not free parameter)
    sm_note = g["sm_inputs_not_free_params"]["delta_alpha_had5"]
    assert "optical theorem" in sm_note.lower() or "NOT a free" in sm_note


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_certificate_all_gates_pass():
    cert = p21_p22_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    for gname, gval in cert["gates"].items():
        assert gval is True, f"Gate '{gname}' did not pass"


def test_certificate_status_upgrade():
    cert = p21_p22_hardgate_certificate()
    assert cert["previous_status"] == {"P21": "CONSTRAINED", "P22": "CONSTRAINED"}
    assert cert["new_status"]["P21"] == "GEOMETRIC_PREDICTION"
    assert cert["new_status"]["P22"] == "GEOMETRIC_PREDICTION"
    assert abs(cert["toe_score_delta"] - 0.6) < 1e-10


def test_certificate_derivation_chain():
    cert = p21_p22_hardgate_certificate()
    assert len(cert["derivation_chain"]) >= 6
    # Should mention all three UM inputs
    chain_str = " ".join(cert["derivation_chain"])
    assert "sin" in chain_str or "P4" in chain_str
    assert "v_geo" in chain_str or "P6" in chain_str
    assert "α" in chain_str or "alpha" in chain_str or "P13" in chain_str


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_ew_summary_keys():
    s = ew_bosons_upgrade_summary()
    required = [
        "parameters", "names", "pdg_values_gev", "um_predictions_gev",
        "residual_pcts", "all_gates_pass", "previous_status", "new_status",
        "toe_score_delta", "v10_21_deliverable",
        "derivation_anchors", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}'"


def test_ew_summary_values():
    s = ew_bosons_upgrade_summary()
    assert s["parameters"] == ["P21", "P22"]
    assert s["all_gates_pass"] is True
    assert s["new_status"]["P21"] == "GEOMETRIC_PREDICTION"
    assert s["new_status"]["P22"] == "GEOMETRIC_PREDICTION"
    assert abs(s["toe_score_delta"] - 0.6) < 1e-10
    assert s["v10_21_deliverable"] == "ew_boson_hardgate_cert.py"
    assert all(r < 5.0 for r in s["residual_pcts"])
