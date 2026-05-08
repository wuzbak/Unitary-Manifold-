# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/higgs_mass_hardgate_cert.py — P5 GEOMETRIC_PREDICTION cert."""
from __future__ import annotations

from src.sixd.higgs_mass_hardgate_cert import (
    ALL_GATES_PASS,
    CW_MIXING_EXPONENT,
    GATE_AXIOMZERO_PASS,
    GATE_NOMINAL_PASS,
    GATE_ROBUSTNESS_PASS,
    GP_THRESHOLD_PCT,
    M_H_CW_FROM_YB_GEV,
    OVERLAP_UNCERTAINTY_FRACTION,
    P5_RESIDUAL_PCT,
    P5_ROBUSTNESS_WORST_PCT,
    P5_STATUS,
    P5_TOE_SCORE_DELTA,
    Y_B_OVERLAP_WS_VII,
    Y_T_EFFECTIVE_FROM_YB,
    cw_yukawa_from_yb,
    p5_axiomzero_gate,
    p5_hardgate_certificate,
    p5_nominal_gate,
    p5_robustness_gate_overlap_window,
    p5_upgrade_summary,
)


def test_gp_threshold():
    assert GP_THRESHOLD_PCT == 5.0


def test_overlap_uncertainty_fraction():
    assert OVERLAP_UNCERTAINTY_FRACTION == 0.15


def test_cw_mixing_exponent():
    assert abs(CW_MIXING_EXPONENT - 0.2) < 1e-12


def test_nominal_bottom_overlap_positive():
    assert Y_B_OVERLAP_WS_VII > 0.0


def test_nominal_effective_yukawa_reasonable():
    assert 0.85 <= Y_T_EFFECTIVE_FROM_YB <= 0.95


def test_cw_mass_near_pdg():
    assert 120.0 <= M_H_CW_FROM_YB_GEV <= 130.0
    assert P5_RESIDUAL_PCT < GP_THRESHOLD_PCT


def test_robustness_worst_inside_5pct():
    assert P5_ROBUSTNESS_WORST_PCT < GP_THRESHOLD_PCT


def test_gate_flags():
    assert GATE_NOMINAL_PASS is True
    assert GATE_ROBUSTNESS_PASS is True
    assert GATE_AXIOMZERO_PASS is True
    assert ALL_GATES_PASS is True


def test_status_upgrade():
    assert P5_STATUS == "GEOMETRIC_PREDICTION"
    assert abs(P5_TOE_SCORE_DELTA - 0.5) < 1e-10


def test_cw_yukawa_from_yb_anchor():
    assert abs(cw_yukawa_from_yb(Y_B_OVERLAP_WS_VII) - Y_T_EFFECTIVE_FROM_YB) < 1e-12


def test_nominal_gate_structure():
    g = p5_nominal_gate()
    assert g["gate"] == "nominal_residual"
    assert g["gate_pass"] is True
    assert g["residual_pct"] < 5.0
    assert "y_b_overlap_ws_vii" in g
    assert "y_t_effective" in g


def test_robustness_gate_structure():
    g = p5_robustness_gate_overlap_window()
    assert g["gate"] == "robustness_overlap_window"
    assert g["gate_pass"] is True
    assert g["worst_case_pct_err"] < 5.0
    assert g["uncertainty_fraction"] == 0.15
    assert len(g["scan_points"]) >= 7


def test_axiomzero_gate_structure():
    g = p5_axiomzero_gate()
    assert g["gate"] == "axiomzero_purity"
    assert g["gate_pass"] is True
    assert "derivation_inputs" in g
    assert "NONE" in g["pdg_inputs_used"]
    assert "anchors" in g


def test_certificate_keys_and_values():
    cert = p5_hardgate_certificate()
    assert cert["all_gates_pass"] is True
    assert cert["previous_status"] == "GEOMETRIC_ESTIMATE_CERTIFIED"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert abs(cert["toe_score_delta"] - 0.5) < 1e-10
    assert len(cert["derivation_chain"]) >= 4


def test_upgrade_summary():
    s = p5_upgrade_summary()
    assert s["parameter"] == "P5"
    assert s["new_status"] == "GEOMETRIC_PREDICTION"
    assert s["all_gates_pass"] is True
    assert abs(s["toe_score_delta"] - 0.5) < 1e-10
    assert s["v10_24_deliverable"] == "higgs_mass_hardgate_cert.py"

