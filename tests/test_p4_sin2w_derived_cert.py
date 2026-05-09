# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P4 DERIVED certification (sin²θ_W from SU(5) 3/8 + RGE)."""
from src.core.p4_sin2w_derived_cert import (
    SIN2_TW_GUT, SIN2_TW_GEO, SIN2_TW_PDG, RESIDUAL_PCT,
    p4_derived_gate_report, p4_derived_summary,
)


def test_gut_bc_exact():
    assert abs(SIN2_TW_GUT - 3.0/8.0) < 1e-15


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p4_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p4_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p4_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p4_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p4():
    s = p4_derived_summary()
    assert s["parameter"] == "P4"
    assert s["all_gates_pass"] is True
