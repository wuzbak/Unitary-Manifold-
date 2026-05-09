# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P2 DERIVED certification (r from inflation geometry)."""
from src.core.p2_r_derived_cert import (
    R_GEO, R_PDG_BOUND, p2_derived_gate_report, p2_derived_summary,
)


def test_r_below_bound():
    assert R_GEO < R_PDG_BOUND


def test_all_gates_pass():
    assert p2_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p2_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p2_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p2_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p2():
    s = p2_derived_summary()
    assert s["parameter"] == "P2"
    assert s["all_gates_pass"] is True
