# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/alpha_s_hardgate_cert.py — P3 GEOMETRIC_PREDICTION cert."""
from __future__ import annotations

from src.core.alpha_s_hardgate_cert import (
    ALL_GATES_PASS,
    ALPHA_S_10D_FULL,
    ALPHA_S_5D,
    ALPHA_S_PDG,
    GATE_AXIOMZERO_PASS,
    GATE_NOMINAL_PASS,
    GATE_ROBUSTNESS_PASS,
    GP_THRESHOLD_PCT,
    P3_RESIDUAL_PCT,
    P3_ROBUSTNESS_WORST_PCT,
    P3_STATUS,
    P3_TOE_SCORE_DELTA,
    ROBUSTNESS_UNCERTAINTY_FRACTION,
    p3_axiomzero_gate,
    p3_hardgate_certificate,
    p3_nominal_gate,
    p3_robustness_gate_kahler_window,
    p3_upgrade_summary,
)


def test_gp_threshold():
    assert GP_THRESHOLD_PCT == 5.0


def test_robustness_uncertainty_fraction():
    assert ROBUSTNESS_UNCERTAINTY_FRACTION == 0.10


def test_alpha_s_nominal_inside_5pct():
    assert abs(ALPHA_S_10D_FULL - ALPHA_S_PDG) / ALPHA_S_PDG < 0.05
    assert P3_RESIDUAL_PCT < GP_THRESHOLD_PCT


def test_alpha_s_improves_vs_5d():
    assert abs(ALPHA_S_10D_FULL - ALPHA_S_PDG) < abs(ALPHA_S_5D - ALPHA_S_PDG)


def test_robustness_worst_inside_5pct():
    assert P3_ROBUSTNESS_WORST_PCT < GP_THRESHOLD_PCT


def test_gate_flags():
    assert GATE_NOMINAL_PASS is True
    assert GATE_ROBUSTNESS_PASS is True
    assert GATE_AXIOMZERO_PASS is True
    assert ALL_GATES_PASS is True


def test_status_upgrade():
    assert P3_STATUS == "GEOMETRIC_PREDICTION"
    assert abs(P3_TOE_SCORE_DELTA - 0.5) < 1e-10


def test_nominal_gate_structure():
    g = p3_nominal_gate()
    assert g["gate"] == "nominal_residual"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0
    assert "alpha_s_pred" in g
    assert "alpha_s_pdg" in g


def test_robustness_gate_structure():
    g = p3_robustness_gate_kahler_window()
    assert g["gate"] == "robustness_kahler_window"
    assert g["gate_pass"] is True
    assert g["worst_case_pct_err"] < 5.0
    assert g["uncertainty_fraction"] == 0.10
    assert len(g["scan_points"]) >= 5


def test_axiomzero_gate_structure():
    g = p3_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "derivation_inputs" in g
    assert "NONE" in g["pdg_inputs_used"]


def test_certificate_keys_and_values():
    cert = p3_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    assert cert["previous_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(cert["toe_score_delta"] - 0.5) < 1e-10
    assert len(cert["derivation_chain"]) >= 4


def test_upgrade_summary():
    s = p3_upgrade_summary()
    assert s["parameter"] == "P3"
    assert s["new_status"] == "GEOMETRIC_PREDICTION"
    assert s["all_gates_pass"] is True
    assert abs(s["toe_score_delta"] - 0.5) < 1e-10
    assert s["v10_24_deliverable"] == "alpha_s_hardgate_cert.py"

