# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P19 DERIVED certification (θ₂₃ Tier-3 geometric)."""
from src.core.p19_theta23_derived_cert import (
    N2, THETA23_GEO_DEG, THETA23_PDG_DEG, RESIDUAL_PCT,
    p19_derived_gate_report, p19_derived_summary,
)
from src.sixd.solar_splitting_6dplus import K_CS, N_W


def test_braid_consistency():
    assert K_CS == N_W**2 + N2**2


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_all_gates_pass():
    assert p19_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p19_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p19_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p19_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p19():
    s = p19_derived_summary()
    assert s["parameter"] == "P19"
    assert s["all_gates_pass"] is True
