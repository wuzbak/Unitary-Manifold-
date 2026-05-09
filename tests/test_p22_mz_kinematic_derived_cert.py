# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P22 DERIVED certification (M_Z kinematic cascade)."""
import math
from src.core.p22_mz_kinematic_derived_cert import (
    M_W_GEO, SIN2_TW_GEO, M_Z_GEO, M_Z_PDG, RESIDUAL_PCT,
    p22_derived_gate_report, p22_derived_summary,
)


def test_formula_value():
    expected = M_W_GEO / math.sqrt(1.0 - SIN2_TW_GEO)
    assert abs(M_Z_GEO - expected) < 1e-6


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p22_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p22_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p22_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p22_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p22():
    s = p22_derived_summary()
    assert s["parameter"] == "P22"
    assert s["all_gates_pass"] is True
