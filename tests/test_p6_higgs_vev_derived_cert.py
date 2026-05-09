# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P6 DERIVED certification (v from CW geometry)."""
from src.core.p6_higgs_vev_derived_cert import (
    V_GEO, V_PDG, RESIDUAL_PCT,
    p6_derived_gate_report, p6_derived_summary,
)


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p6_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p6_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p6_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p6_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p6():
    s = p6_derived_summary()
    assert s["parameter"] == "P6"
    assert s["all_gates_pass"] is True
