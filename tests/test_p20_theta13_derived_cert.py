# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P20 DERIVED certification (sin²θ₁₃ = 3/138 purely algebraic)."""
from src.core.p20_theta13_derived_cert import (
    N_C, N_W, N2, SIN2_THETA13_DERIVED, RESIDUAL_PCT,
    p20_derived_gate_report, p20_derived_summary,
)
from src.sixd.solar_splitting_6dplus import K_CS


def test_formula_value():
    assert abs(SIN2_THETA13_DERIVED - 3/138) < 1e-10


def test_braid_pair_consistency():
    assert K_CS == N_W**2 + N2**2  # 74 = 25 + 49


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_gate1_passes():
    assert p20_derived_gate_report()["gates"]["gate1_residual_lt_5pct"] is True


def test_gate2_axiomzero_passes():
    assert p20_derived_gate_report()["gates"]["gate2_axiomzero_no_pdg_inputs"] is True


def test_gate3_integers_consistent():
    assert p20_derived_gate_report()["gates"]["gate3_braid_integers_self_consistent"] is True


def test_all_gates_pass():
    assert p20_derived_gate_report()["all_gates_pass"] is True


def test_status_after_is_derived():
    assert p20_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_score_delta():
    assert p20_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_inputs_empty():
    assert p20_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_consistent():
    s = p20_derived_summary()
    assert s["parameter"] == "P20"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
