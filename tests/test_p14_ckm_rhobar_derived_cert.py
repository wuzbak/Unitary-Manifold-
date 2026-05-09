# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P14 DERIVED certification (CKM ρ̄)."""
from src.core.p14_ckm_rhobar_derived_cert import (
    ALL_GATES_PASS,
    GATE_AXIOMZERO_PASS,
    GATE_NOMINAL_PASS,
    GATE_ROBUSTNESS_PASS,
    P14_PDG,
    P14_PRED,
    P14_RESIDUAL,
    p14_derived_gate_report,
    p14_derived_summary,
)


def test_rho_bar_pred_near_pdg():
    assert abs(P14_PRED - P14_PDG) / P14_PDG < 0.05


def test_nominal_residual_gate():
    assert GATE_NOMINAL_PASS is True


def test_robustness_gate():
    assert GATE_ROBUSTNESS_PASS is True


def test_axiomzero_gate():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_status_after_derived():
    assert p14_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p14_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p14_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p14():
    s = p14_derived_summary()
    assert s["parameter"] == "P14"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
    assert s["axiomzero_pdg_inputs"] == []


def test_residual_value():
    assert P14_RESIDUAL < 2.0  # 1.22% well within 5%
