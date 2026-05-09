# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P1 DERIVED certification (n_s from inflation geometry)."""
from src.core.p1_ns_derived_cert import (
    NS_GEO, NS_PDG, NS_PDG_SIGMA, RESIDUAL_PCT, NSIGMA_FROM_PDG,
    p1_derived_gate_report, p1_derived_summary,
)


def test_ns_value():
    assert abs(NS_GEO - 0.9635) < 1e-6


def test_residual_below_5pct():
    assert RESIDUAL_PCT < 5.0


def test_within_1sigma_planck():
    assert NSIGMA_FROM_PDG < 1.0


def test_all_gates_pass():
    assert p1_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p1_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p1_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p1_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p1():
    s = p1_derived_summary()
    assert s["parameter"] == "P1"
    assert s["all_gates_pass"] is True
