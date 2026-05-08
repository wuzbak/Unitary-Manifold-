# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/delta_cp_hardgate_cert.py — P15 GEOMETRIC_PREDICTION cert."""
from __future__ import annotations

import pytest

from src.core.delta_cp_hardgate_cert import (
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    P15_DELTA_CP_9D_RAD,
    P15_RESIDUAL_PCT,
    P15_UNCERTAINTY_PCT,
    GATE_NOMINAL_PASS,
    GATE_UNCERTAINTY_PASS,
    GATE_ANCHOR_PASS,
    GATE_AXIOMZERO_PASS,
    ALL_GATES_PASS,
    P15_STATUS,
    P15_TOE_SCORE_DELTA,
    p15_nominal_gate,
    p15_uncertainty_gate,
    p15_anchor_gate,
    p15_axiomzero_gate,
    p15_hardgate_certificate,
    p15_upgrade_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_p15_delta_cp_9d_near_pdg():
    """9D δ_CP should be between 1.18 and 1.25 rad."""
    assert 1.18 <= P15_DELTA_CP_9D_RAD <= 1.25


def test_p15_residual_below_5pct():
    """Nominal residual must be < 5%."""
    assert P15_RESIDUAL_PCT < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p15_residual_near_1_2pct():
    """Residual should be around 1.27%."""
    assert 0.5 <= P15_RESIDUAL_PCT <= 3.0


def test_p15_uncertainty_below_5pct():
    """1σ uncertainty must be < 5% of PDG."""
    assert P15_UNCERTAINTY_PCT < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p15_uncertainty_near_3pct():
    """Uncertainty should be around 2.79%."""
    assert 1.0 <= P15_UNCERTAINTY_PCT <= 4.5


# ---------------------------------------------------------------------------
# Gate flags
# ---------------------------------------------------------------------------

def test_gate_nominal_pass():
    assert GATE_NOMINAL_PASS is True


def test_gate_uncertainty_pass():
    assert GATE_UNCERTAINTY_PASS is True


def test_gate_anchor_pass():
    assert GATE_ANCHOR_PASS is True


def test_gate_axiomzero_pass():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_p15_status():
    assert P15_STATUS == "GEOMETRIC_PREDICTION"


def test_p15_toe_score_delta():
    assert abs(P15_TOE_SCORE_DELTA - 0.3) < 1e-10


# ---------------------------------------------------------------------------
# Gate function outputs
# ---------------------------------------------------------------------------

def test_p15_nominal_gate_structure():
    g = p15_nominal_gate()
    assert g["gate"] == "nominal_residual"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0
    assert "delta_cp_9d_rad" in g
    assert "delta_cp_pdg_rad" in g


def test_p15_uncertainty_gate_structure():
    g = p15_uncertainty_gate()
    assert g["gate"] == "propagated_uncertainty"
    assert g["gate_pass"] is True
    assert g["uncertainty_pct"] < 5.0
    assert "uncertainty_rad" in g


def test_p15_anchor_gate_structure():
    g = p15_anchor_gate()
    assert g["gate"] == "anchor_independence"
    assert g["gate_pass"] is True
    assert "scan" in g
    assert g["scan"]["all_points_gate_pass"] is True


def test_p15_axiomzero_gate_structure():
    g = p15_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "derivation_inputs" in g
    assert "pdg_inputs_used" in g


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_p15_certificate_all_keys():
    cert = p15_hardgate_certificate()
    assert "parameter" in cert
    assert "derivation_chain" in cert
    assert "gates" in cert
    assert "gate_details" in cert
    assert "all_gates_pass" in cert
    assert "new_status" in cert
    assert "toe_score_delta" in cert
    assert "verdict" in cert


def test_p15_certificate_all_gates_pass():
    cert = p15_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    for gname, gval in cert["gates"].items():
        assert gval is True, f"Gate '{gname}' did not pass"


def test_p15_certificate_status_upgrade():
    cert = p15_hardgate_certificate()
    assert cert["previous_status"] == "BEST_EVIDENCE_CONSTRAINED"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(cert["toe_score_delta"] - 0.3) < 1e-10


def test_p15_certificate_derivation_chain():
    cert = p15_hardgate_certificate()
    assert len(cert["derivation_chain"]) >= 3
    # First step should mention 7D discrete torsion
    assert "7D" in cert["derivation_chain"][0]


def test_p15_certificate_nominal_baseline():
    cert = p15_hardgate_certificate()
    nb = cert["nominal_baseline"]
    assert nb["residual_7d_pct"] > nb["residual_9d_pct"]
    assert nb["improvement_pct"] > 0


# ---------------------------------------------------------------------------
# Upgrade summary
# ---------------------------------------------------------------------------

def test_p15_upgrade_summary_keys():
    s = p15_upgrade_summary()
    required = [
        "parameter", "name", "pdg_value", "um_prediction", "residual_pct",
        "uncertainty_pct", "all_gates_pass", "previous_status", "new_status",
        "toe_score_delta", "v10_19_deliverable", "derivation_anchor", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}' in upgrade summary"


def test_p15_upgrade_summary_values():
    s = p15_upgrade_summary()
    assert s["parameter"] == "P15"
    assert s["all_gates_pass"] is True
    assert s["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(s["toe_score_delta"] - 0.3) < 1e-10
    assert s["residual_pct"] < 5.0
    assert s["v10_19_deliverable"] == "delta_cp_hardgate_cert.py"
