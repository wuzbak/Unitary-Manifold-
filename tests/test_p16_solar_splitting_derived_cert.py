# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P16 DERIVED certification (f_c = 7/126 purely algebraic)."""
from src.core.p16_solar_splitting_derived_cert import (
    FC_DERIVED, RESIDUAL_RATIO_PCT, PI_KR_ALGEBRAIC,
    p16_derived_gate_report, p16_derived_summary,
)


def test_fc_value():
    assert abs(FC_DERIVED - 7/126) < 1e-10


def test_pi_kr_algebraic_equals_37():
    assert PI_KR_ALGEBRAIC == 37


def test_residual_below_5pct():
    assert RESIDUAL_RATIO_PCT < 5.0


def test_gate1_passes():
    assert p16_derived_gate_report()["gates"]["gate1_residual_lt_5pct"] is True


def test_gate2_axiomzero_passes():
    assert p16_derived_gate_report()["gates"]["gate2_axiomzero_no_pdg_inputs"] is True


def test_gate3_algebraic_match():
    assert p16_derived_gate_report()["gates"]["gate3_pi_kr_algebraic_matches"] is True


def test_all_gates_pass():
    assert p16_derived_gate_report()["all_gates_pass"] is True


def test_status_after_is_derived():
    assert p16_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_score_delta():
    assert p16_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_inputs_empty():
    assert p16_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_consistent():
    s = p16_derived_summary()
    assert s["parameter"] == "P16"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
