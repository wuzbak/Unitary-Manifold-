# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P15 DERIVED certification (leptonic CP phase δ_CP)."""
from src.core.p15_delta_cp_derived_cert import (
    ALL_GATES_PASS,
    GATE_ANCHOR_INDEPENDENCE_PASS,
    GATE_AXIOMZERO_PASS,
    GATE_NOMINAL_PASS,
    GATE_UNCERTAINTY_PASS,
    P15_PDG_RAD,
    P15_PRED_RAD,
    P15_RESIDUAL,
    p15_derived_gate_report,
    p15_derived_summary,
)


def test_delta_cp_pred_near_pdg():
    assert abs(P15_PRED_RAD - P15_PDG_RAD) / P15_PDG_RAD < 0.05


def test_nominal_residual_gate():
    assert GATE_NOMINAL_PASS is True


def test_uncertainty_gate():
    assert GATE_UNCERTAINTY_PASS is True


def test_anchor_independence_gate():
    assert GATE_ANCHOR_INDEPENDENCE_PASS is True


def test_axiomzero_gate():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_status_after_derived():
    assert p15_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p15_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p15_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p15():
    s = p15_derived_summary()
    assert s["parameter"] == "P15"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
    assert s["axiomzero_pdg_inputs"] == []


def test_residual_value():
    assert P15_RESIDUAL < 2.0  # 1.27% well within 5%
