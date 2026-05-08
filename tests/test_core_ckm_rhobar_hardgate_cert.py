# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/ckm_rhobar_hardgate_cert.py — P14 GEOMETRIC_PREDICTION cert."""
from __future__ import annotations

import pytest

from src.core.ckm_rhobar_hardgate_cert import (
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    ROBUSTNESS_THRESHOLD_PCT,
    P14_RHO_BAR_PRED,
    P14_RHO_BAR_PDG,
    P14_RESIDUAL_PCT,
    P14_ROBUSTNESS_WINDOW_RAD,
    P14_ROBUSTNESS_WINDOW_DEG,
    P14_ROBUSTNESS_WORST_PCT,
    GATE_NOMINAL_PASS,
    GATE_ROBUSTNESS_PASS,
    GATE_AXIOMZERO_PASS,
    ALL_GATES_PASS,
    P14_STATUS,
    P14_TOE_SCORE_DELTA,
    p14_nominal_gate,
    p14_robustness_gate_9d_window,
    p14_axiomzero_gate,
    p14_hardgate_certificate,
    p14_upgrade_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_robustness_threshold():
    assert ROBUSTNESS_THRESHOLD_PCT == 5.0


def test_p14_rho_bar_pdg_value():
    """PDG ρ̄ should be around 0.159."""
    assert 0.14 <= P14_RHO_BAR_PDG <= 0.18


def test_p14_rho_bar_pred_near_pdg():
    """ρ̄ prediction should be within 5% of PDG."""
    assert abs(P14_RHO_BAR_PRED - P14_RHO_BAR_PDG) / P14_RHO_BAR_PDG < 0.05


def test_p14_residual_below_5pct():
    """Nominal residual must be < 5%."""
    assert P14_RESIDUAL_PCT < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p14_residual_near_1_2pct():
    """Residual should be around 1.22%."""
    assert 0.5 <= P14_RESIDUAL_PCT <= 3.0


def test_p14_robustness_window_reasonable():
    """9D-propagated window should be between 0.5° and 1.5°."""
    assert 0.5 <= P14_ROBUSTNESS_WINDOW_DEG <= 1.5


def test_p14_robustness_worst_below_5pct():
    """Worst-case ρ̄ error at ±1σ window must be < 5%."""
    assert P14_ROBUSTNESS_WORST_PCT < ROBUSTNESS_THRESHOLD_PCT


# ---------------------------------------------------------------------------
# Gate flags
# ---------------------------------------------------------------------------

def test_gate_nominal_pass():
    assert GATE_NOMINAL_PASS is True


def test_gate_robustness_pass():
    assert GATE_ROBUSTNESS_PASS is True


def test_gate_axiomzero_pass():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_p14_status():
    assert P14_STATUS == "GEOMETRIC_PREDICTION"


def test_p14_toe_score_delta():
    assert abs(P14_TOE_SCORE_DELTA - 0.3) < 1e-10


# ---------------------------------------------------------------------------
# Gate function outputs
# ---------------------------------------------------------------------------

def test_p14_nominal_gate_structure():
    g = p14_nominal_gate()
    assert g["gate"] == "nominal_residual"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0
    assert "rho_bar_pred" in g
    assert "rho_bar_pdg" in g


def test_p14_nominal_gate_values():
    g = p14_nominal_gate()
    assert g["rho_bar_pred"] > 0
    assert g["rho_bar_pdg"] > 0
    assert g["rho_bar_pdg"] == pytest.approx(P14_RHO_BAR_PDG)


def test_p14_robustness_gate_structure():
    g = p14_robustness_gate_9d_window()
    assert g["gate"] == "robustness_9d_window"
    assert g["gate_pass"] is True
    assert g["worst_case_pct_err"] < 5.0
    assert "robustness_window_rad" in g
    assert "robustness_window_deg" in g
    assert "rho_plus_pct_err" in g
    assert "rho_minus_pct_err" in g


def test_p14_robustness_gate_window_positive():
    g = p14_robustness_gate_9d_window()
    assert g["robustness_window_rad"] > 0
    assert g["robustness_window_deg"] > 0


def test_p14_axiomzero_gate_structure():
    g = p14_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "rung3_evidence" in g


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_p14_certificate_all_keys():
    cert = p14_hardgate_certificate()
    required_keys = [
        "parameter", "derivation_chain", "robustness_key", "gates",
        "gate_details", "all_gates_pass", "new_status", "toe_score_delta", "verdict",
    ]
    for k in required_keys:
        assert k in cert, f"Missing key '{k}'"


def test_p14_certificate_all_gates_pass():
    cert = p14_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    for gname, gval in cert["gates"].items():
        assert gval is True, f"Gate '{gname}' did not pass"


def test_p14_certificate_status_upgrade():
    cert = p14_hardgate_certificate()
    assert cert["previous_status"] == "BEST_EVIDENCE_CONSTRAINED"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(cert["toe_score_delta"] - 0.3) < 1e-10


def test_p14_certificate_derivation_chain():
    cert = p14_hardgate_certificate()
    assert len(cert["derivation_chain"]) >= 3
    # Chain should include 8D step
    assert any("8D" in step for step in cert["derivation_chain"])


def test_p14_certificate_robustness_key_mentions_9d():
    cert = p14_hardgate_certificate()
    assert "9D" in cert["robustness_key"]


# ---------------------------------------------------------------------------
# Upgrade summary
# ---------------------------------------------------------------------------

def test_p14_upgrade_summary_keys():
    s = p14_upgrade_summary()
    required = [
        "parameter", "name", "pdg_value", "um_prediction", "residual_pct",
        "robustness_window_deg", "robustness_worst_pct", "all_gates_pass",
        "previous_status", "new_status", "toe_score_delta",
        "v10_19_deliverable", "derivation_anchor", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}' in upgrade summary"


def test_p14_upgrade_summary_values():
    s = p14_upgrade_summary()
    assert s["parameter"] == "P14"
    assert s["all_gates_pass"] is True
    assert s["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(s["toe_score_delta"] - 0.3) < 1e-10
    assert s["residual_pct"] < 5.0
    assert s["robustness_worst_pct"] < 5.0
    assert s["v10_19_deliverable"] == "ckm_rhobar_hardgate_cert.py"
