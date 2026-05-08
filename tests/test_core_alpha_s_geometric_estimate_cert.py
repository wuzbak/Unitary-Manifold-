# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/alpha_s_geometric_estimate_cert.py — WS-VI P3."""
from __future__ import annotations

import pytest

from src.core.alpha_s_geometric_estimate_cert import (
    K_CS, N_FLUX, H11, H21,
    GEC_THRESHOLD_PCT, ALPHA_S_PDG, ALPHA_S_5D, ALPHA_S_10D_FULL,
    RESIDUAL_5D_PCT, RESIDUAL_10D_PCT,
    GATE_GEC_PASS, GATE_ARCHITECTURE_EXPLAINED, GATE_AXIOMZERO_PASS,
    ALL_GATES_PASS, P3_STATUS, P3_TOE_SCORE_DELTA,
    p3_gec_residual_gate, p3_architecture_gate, p3_axiomzero_gate,
    p3_hardgate_certificate, ws_vi_alpha_s_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_k_cs():
    assert K_CS == 74


def test_n_flux():
    assert N_FLUX == 37  # = K_CS / 2


def test_cy3_moduli():
    assert H11 == 1
    assert H21 == 101


def test_gec_threshold():
    assert GEC_THRESHOLD_PCT == 20.0


def test_alpha_s_pdg():
    assert abs(ALPHA_S_PDG - 0.1179) < 1e-6


def test_alpha_s_5d():
    """5D chain gives alpha_s ≈ 0.0673."""
    assert abs(ALPHA_S_5D - 0.0673) < 0.001


def test_alpha_s_10d_range():
    """Full 10D result should be between 0.10 and 0.12."""
    assert 0.10 <= ALPHA_S_10D_FULL <= 0.12


# ---------------------------------------------------------------------------
# Residuals
# ---------------------------------------------------------------------------

def test_residual_5d_large():
    """5D residual should be > 30%."""
    assert RESIDUAL_5D_PCT > 30.0


def test_residual_10d_below_20pct():
    """10D residual must be < 20% (GEC threshold)."""
    assert RESIDUAL_10D_PCT < GEC_THRESHOLD_PCT


def test_residual_10d_near_4pct():
    """10D residual expected around 4.1%."""
    assert 2.0 <= RESIDUAL_10D_PCT <= 8.0


def test_improvement_from_5d_to_10d():
    """10D should improve significantly over 5D."""
    assert RESIDUAL_10D_PCT < RESIDUAL_5D_PCT / 2


# ---------------------------------------------------------------------------
# Gate flags
# ---------------------------------------------------------------------------

def test_gate_gec_pass():
    assert GATE_GEC_PASS is True


def test_gate_architecture_explained():
    assert GATE_ARCHITECTURE_EXPLAINED is True


def test_gate_axiomzero_pass():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_p3_status():
    assert P3_STATUS == "GEOMETRIC_ESTIMATE_CERTIFIED"


def test_p3_toe_score_delta():
    assert abs(P3_TOE_SCORE_DELTA - 0.2) < 1e-10


# ---------------------------------------------------------------------------
# Gate functions
# ---------------------------------------------------------------------------

def test_p3_gec_gate_structure():
    g = p3_gec_residual_gate()
    assert g["gate"] == "gec_20pct"
    assert g["gate_pass"] is True
    assert g["residual_10d_pct"] < 20.0
    assert "kahler_shift" in g
    assert "cs_shift" in g
    assert "flux_shift" in g
    assert "note" in g


def test_p3_gec_gate_improvements():
    g = p3_gec_residual_gate()
    assert g["residual_5d_pct"] > g["residual_10d_pct"]
    assert g["total_shift"] > 0


def test_p3_gec_gate_note_mentions_5pct():
    g = p3_gec_residual_gate()
    assert "5%" in g["note"]


def test_p3_architecture_gate_structure():
    g = p3_architecture_gate()
    assert g["gate"] == "architecture_explained"
    assert g["gate_pass"] is True
    assert "explanation" in g
    assert "path_to_gp" in g
    assert "architecture_module" in g


def test_p3_axiomzero_gate_structure():
    g = p3_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "derivation_inputs" in g
    assert "NONE" in g["pdg_inputs_used"]


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_p3_certificate_keys():
    cert = p3_hardgate_certificate()
    required = [
        "parameter", "derivation_chain", "ws_iv_full_gate",
        "gates", "gate_details", "all_gates_pass",
        "new_status", "toe_score_delta", "verdict",
    ]
    for k in required:
        assert k in cert, f"Missing key '{k}'"


def test_p3_certificate_all_gates_pass():
    cert = p3_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    for gname, gval in cert["gates"].items():
        assert gval is True, f"Gate '{gname}' did not pass"


def test_p3_certificate_status():
    cert = p3_hardgate_certificate()
    assert cert["previous_status"] == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert cert["new_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert abs(cert["toe_score_delta"] - 0.2) < 1e-10


def test_p3_certificate_derivation_chain():
    cert = p3_hardgate_certificate()
    assert len(cert["derivation_chain"]) >= 4
    # Should mention 5D baseline and improvements
    assert any("5D" in s for s in cert["derivation_chain"])
    assert any("10D" in s for s in cert["derivation_chain"])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_ws_vi_alpha_s_summary_keys():
    s = ws_vi_alpha_s_summary()
    required = [
        "workstream", "parameter", "name", "pdg_value",
        "um_5d_prediction", "um_10d_prediction",
        "residual_5d_pct", "residual_10d_pct",
        "all_gates_pass", "previous_status", "new_status",
        "toe_score_delta", "v10_20_deliverable",
        "derivation_anchor", "verdict",
    ]
    for k in required:
        assert k in s, f"Missing key '{k}'"


def test_ws_vi_alpha_s_summary_values():
    s = ws_vi_alpha_s_summary()
    assert s["workstream"] == "WS-VI"
    assert s["parameter"] == "P3"
    assert s["all_gates_pass"] is True
    assert s["new_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert abs(s["toe_score_delta"] - 0.2) < 1e-10
    assert s["v10_20_deliverable"] == "alpha_s_geometric_estimate_cert.py"
    assert s["residual_10d_pct"] < 20.0
