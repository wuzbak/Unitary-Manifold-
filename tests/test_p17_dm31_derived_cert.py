# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P17 DERIVED certification (Δm²₃₁ from 9D KK+GS)."""
from src.core.p17_dm31_derived_cert import (
    DM2_31_GEO, DM2_31_PDG, RESIDUAL_PCT,
    p17_derived_gate_report, p17_derived_summary,
)


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p17_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p17_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p17_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p17_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p17():
    s = p17_derived_summary()
    assert s["parameter"] == "P17"
    assert s["all_gates_pass"] is True
