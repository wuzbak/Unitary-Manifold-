# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P26 GEOMETRIC_PREDICTION→DERIVED certification."""

from src.core.p26_neutrino_mass_derived_cert import (
    ALL_GATES_PASS,
    GATE_AXIOMZERO_PASS,
    GATE_BOUND_COMPATIBILITY_PASS,
    GATE_NUMERICAL_CONSISTENCY_PASS,
    p26_derived_gate_report,
    p26_derived_summary,
)


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_individual_gate_flags():
    assert GATE_NUMERICAL_CONSISTENCY_PASS is True
    assert GATE_BOUND_COMPATIBILITY_PASS is True
    assert GATE_AXIOMZERO_PASS is True


def test_report_promotes_to_derived():
    report = p26_derived_gate_report()
    assert report["status_before"] == "GEOMETRIC_PREDICTION"
    assert report["status_after"] == "DERIVED"
    assert report["toe_score_delta"] == 0.2
    assert report["all_gates_pass"] is True


def test_axiomzero_is_explicit():
    report = p26_derived_gate_report()
    assert report["axiomzero_pdg_inputs"] == []
    assert len(report["axiomzero_inputs"]) == 4


def test_summary_shape():
    summary = p26_derived_summary()
    assert summary["sprint"] == "P26_DERIVED_CERTIFICATION"
    assert summary["parameter"] == "P26"
    assert summary["status_after"] == "DERIVED"
    assert summary["toe_score_delta"] == 0.2
