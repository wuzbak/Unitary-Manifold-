# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P5 DERIVED certification (m_H from CW geometry)."""
from src.core.p5_higgs_mass_derived_cert import (
    M_HIGGS_GEO, M_HIGGS_PDG, RESIDUAL_PCT,
    p5_derived_gate_report, p5_derived_summary,
)


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p5_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p5_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p5_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p5_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p5():
    s = p5_derived_summary()
    assert s["parameter"] == "P5"
    assert s["all_gates_pass"] is True
