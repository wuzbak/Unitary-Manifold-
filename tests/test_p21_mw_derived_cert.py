# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P21 DERIVED certification (M_W from EW fit cascade)."""
from src.core.p21_mw_derived_cert import (
    M_W_GEO, M_W_PDG, RESIDUAL_PCT,
    p21_derived_gate_report, p21_derived_summary,
)


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p21_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p21_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p21_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p21_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p21():
    s = p21_derived_summary()
    assert s["parameter"] == "P21"
    assert s["all_gates_pass"] is True
