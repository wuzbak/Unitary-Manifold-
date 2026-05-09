# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P3 DERIVED certification (α_s from 10D CY₃ moduli+flux closure)."""
from src.core.p3_alpha_s_derived_cert import (
    ALL_GATES_PASS,
    GATE_AXIOMZERO_PASS,
    GATE_NOMINAL_PASS,
    GATE_ROBUSTNESS_PASS,
    P3_PDG,
    P3_PRED,
    P3_RESIDUAL,
    p3_derived_gate_report,
    p3_derived_summary,
)


def test_alpha_s_pred_near_pdg():
    assert abs(P3_PRED - P3_PDG) / P3_PDG < 0.05


def test_nominal_residual_gate():
    assert GATE_NOMINAL_PASS is True


def test_robustness_gate():
    assert GATE_ROBUSTNESS_PASS is True


def test_axiomzero_gate():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_status_after_derived():
    assert p3_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p3_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p3_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p3():
    s = p3_derived_summary()
    assert s["parameter"] == "P3"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
    assert s["axiomzero_pdg_inputs"] == []


def test_residual_value():
    assert P3_RESIDUAL < 5.0
