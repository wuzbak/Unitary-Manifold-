# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P12 DERIVED certification (m_p/m_e = K_CS²/N_c)."""
from src.core.p12_mp_me_derived_cert import (
    K_CS, N_C, MP_ME_GEO, MP_ME_PDG, RESIDUAL_PCT,
    p12_derived_gate_report, p12_derived_summary,
)


def test_formula_value():
    assert abs(MP_ME_GEO - K_CS**2 / N_C) < 1e-10


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_gate1_passes():
    assert p12_derived_gate_report()["gates"]["gate1_residual_lt_5pct"] is True


def test_gate2_axiomzero_passes():
    assert p12_derived_gate_report()["gates"]["gate2_axiomzero_no_pdg_inputs"] is True


def test_gate3_unique_passes():
    assert p12_derived_gate_report()["gates"]["gate3_formula_algebraically_unique"] is True


def test_all_gates_pass():
    assert p12_derived_gate_report()["all_gates_pass"] is True


def test_status_after_is_derived():
    assert p12_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_score_delta():
    assert p12_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_inputs_empty():
    assert p12_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_consistent():
    s = p12_derived_summary()
    assert s["parameter"] == "P12"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.2
