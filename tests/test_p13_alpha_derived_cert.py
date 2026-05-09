# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P13 DERIVED certification (α = 1/137.0 from N_c/K_CS chain)."""
from src.core.p13_alpha_derived_cert import (
    N_C, ALPHA_GUT, ALPHA_INV_GEO, ALPHA_INV_PDG, RESIDUAL_PCT,
    p13_derived_gate_report, p13_derived_summary,
)
from src.sixd.solar_splitting_6dplus import K_CS


def test_alpha_gut_algebraic():
    assert abs(ALPHA_GUT - N_C / K_CS) < 1e-15


def test_alpha_inv_geo():
    assert abs(ALPHA_INV_GEO - 137.0) < 1e-6


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p13_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p13_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p13_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p13_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p13():
    s = p13_derived_summary()
    assert s["parameter"] == "P13"
    assert s["all_gates_pass"] is True
