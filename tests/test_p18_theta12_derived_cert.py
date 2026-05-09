# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P18 DERIVED certification (θ₁₂ Route A geometric)."""
from src.core.p18_theta12_derived_cert import (
    N2, THETA12_GEO_DEG, THETA12_PDG_DEG, RESIDUAL_PCT,
    p18_derived_gate_report, p18_derived_summary,
)
from src.sixd.solar_splitting_6dplus import K_CS, N_W


def test_braid_consistency():
    assert K_CS == N_W**2 + N2**2


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p18_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p18_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p18_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p18_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p18():
    s = p18_derived_summary()
    assert s["parameter"] == "P18"
    assert s["all_gates_pass"] is True
