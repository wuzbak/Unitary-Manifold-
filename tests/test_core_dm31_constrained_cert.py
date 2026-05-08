# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/dm31_constrained_cert.py — P17 CONSTRAINED cert."""
from __future__ import annotations

import pytest

from src.core.dm31_constrained_cert import (
    CONSTRAINED_THRESHOLD_PCT,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    DM2_31_PDG,
    P17_RESIDUAL_2NLO_PCT,
    P17_RESIDUAL_LO_PCT,
    P17_RESIDUAL_NLO_PCT,
    GATE_CONSTRAINED_PASS,
    GATE_ARCHITECTURE_EXPLAINED,
    GATE_AXIOMZERO_PASS,
    ALL_GATES_PASS,
    P17_STATUS,
    P17_TOE_SCORE_DELTA,
    p17_constrained_gate,
    p17_architecture_gate,
    p17_axiomzero_gate,
    p17_constrained_certificate,
    p17_upgrade_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_constrained_threshold():
    assert CONSTRAINED_THRESHOLD_PCT == 50.0


def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_dm2_31_pdg_value():
    """PDG Δm²₃₁ ≈ 2.453×10⁻³ eV²."""
    assert abs(DM2_31_PDG - 2.453e-3) < 1e-6


def test_p17_residual_2nlo_below_50pct():
    """2NLO residual must be < 50% (CONSTRAINED threshold)."""
    assert P17_RESIDUAL_2NLO_PCT < CONSTRAINED_THRESHOLD_PCT


def test_p17_residual_2nlo_near_7pct():
    """2NLO residual should be around 6.87%."""
    assert 4.0 <= P17_RESIDUAL_2NLO_PCT <= 10.0


def test_p17_residual_2nlo_above_5pct():
    """2NLO residual should still be above 5% (not yet GEOMETRIC_PREDICTION)."""
    assert P17_RESIDUAL_2NLO_PCT > GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p17_residual_progression():
    """Residuals should decrease: LO > NLO > 2NLO."""
    assert P17_RESIDUAL_LO_PCT > P17_RESIDUAL_NLO_PCT
    assert P17_RESIDUAL_NLO_PCT > P17_RESIDUAL_2NLO_PCT


# ---------------------------------------------------------------------------
# Gate flags
# ---------------------------------------------------------------------------

def test_gate_constrained_pass():
    assert GATE_CONSTRAINED_PASS is True


def test_gate_architecture_explained():
    assert GATE_ARCHITECTURE_EXPLAINED is True


def test_gate_axiomzero_pass():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_p17_status():
    assert P17_STATUS == "CONSTRAINED"


def test_p17_toe_score_delta():
    assert abs(P17_TOE_SCORE_DELTA - 0.2) < 1e-10


# ---------------------------------------------------------------------------
# Gate function outputs
# ---------------------------------------------------------------------------

def test_p17_constrained_gate_structure():
    g = p17_constrained_gate()
    assert g["gate"] == "constrained_50pct"
    assert g["gate_pass"] is True
    assert g["residual_2nlo_pct"] < 50.0
    assert "threshold_pct" in g
    assert "note_vs_geometric_prediction" in g


def test_p17_constrained_gate_note_mentions_wvs():
    g = p17_constrained_gate()
    assert "WS-V" in g["note_vs_geometric_prediction"]


def test_p17_architecture_gate_structure():
    g = p17_architecture_gate()
    assert g["gate"] == "architecture_explained"
    assert g["gate_pass"] is True
    assert "architecture_limit_module" in g
    assert "explanation" in g
    assert "closure_path" in g


def test_p17_architecture_gate_mentions_wsv():
    g = p17_architecture_gate()
    assert "WS-V" in g["closure_path"]


def test_p17_axiomzero_gate_structure():
    g = p17_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "pdg_inputs_used" in g
    assert "NONE" in g["pdg_inputs_used"]


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_p17_certificate_all_keys():
    cert = p17_constrained_certificate()
    required = [
        "parameter", "residual_progression", "twonlo_summary", "scoring_note",
        "gates", "gate_details", "all_gates_pass", "new_status",
        "toe_score_delta", "verdict",
    ]
    for k in required:
        assert k in cert, f"Missing key '{k}'"


def test_p17_certificate_all_gates_pass():
    cert = p17_constrained_certificate()
    assert cert["all_gates_pass"] is True
    for gname, gval in cert["gates"].items():
        assert gval is True, f"Gate '{gname}' did not pass"


def test_p17_certificate_status_upgrade():
    cert = p17_constrained_certificate()
    assert cert["previous_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert cert["new_status"] == "CONSTRAINED"
    assert abs(cert["toe_score_delta"] - 0.2) < 1e-10


def test_p17_certificate_residual_progression():
    cert = p17_constrained_certificate()
    rp = cert["residual_progression"]
    assert rp["lo_pct"] > rp["nlo_pct"]
    assert rp["nlo_pct"] > rp["2nlo_pct"]
    assert rp["2nlo_pct"] < 50.0


def test_p17_certificate_scoring_note():
    cert = p17_constrained_certificate()
    # Scoring note should explain the 0.5 > 0.3 logic
    assert "0.5" in cert["scoring_note"]
    assert "0.3" in cert["scoring_note"]


# ---------------------------------------------------------------------------
# Upgrade summary
# ---------------------------------------------------------------------------

def test_p17_upgrade_summary_keys():
    s = p17_upgrade_summary()
    required = [
        "parameter", "name", "pdg_value", "residual_pct",
        "residual_lo_pct", "residual_nlo_pct", "all_gates_pass",
        "previous_status", "new_status", "toe_score_delta",
        "v10_19_deliverable", "derivation_anchor", "closure_path", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}' in upgrade summary"


def test_p17_upgrade_summary_values():
    s = p17_upgrade_summary()
    assert s["parameter"] == "P17"
    assert s["all_gates_pass"] is True
    assert s["new_status"] == "CONSTRAINED"
    assert abs(s["toe_score_delta"] - 0.2) < 1e-10
    assert s["residual_pct"] < 50.0
    assert s["residual_pct"] > 5.0
    assert s["v10_19_deliverable"] == "dm31_constrained_cert.py"
    assert "WS-V" in s["closure_path"]
