# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/p16_wsiii_plus52_closure.py."""

from src.core.p16_wsiii_plus52_closure import (
    FC_DERIVED,
    PLUS52_DERIVED,
    derive_fc_wsiii,
    derive_plus52_wsiii,
    p16_wsiii_closure_summary,
    p16_wsiii_gate_report,
)


def test_plus52_exact():
    assert PLUS52_DERIVED == 52


def test_fc_exact_fraction():
    assert abs(FC_DERIVED - (7.0 / 126.0)) < 1e-15


def test_derivation_decomposition_values():
    report = derive_plus52_wsiii()
    assert report["decomposition"]["rs_compactification_units"] == 37
    assert report["decomposition"]["torsion_total"] == 15
    assert report["plus52"] == 52
    assert report["is_exact"] is True


def test_no_pdg_inputs_in_plus52_derivation():
    report = derive_plus52_wsiii()
    assert report["axiomzero_pdg_inputs"] == []


def test_fc_report_fields():
    report = derive_fc_wsiii()
    assert report["f_c"] > 0.0
    assert report["f_c_fraction_numerator"] == 7.0
    assert report["f_c_fraction_denominator"] == 126.0
    assert report["corrected_ratio"] > 0.0


def test_gate_report_promotes_p16():
    gate = p16_wsiii_gate_report()
    assert gate["all_gates_pass"] is True
    assert gate["status_after"] == "GEOMETRIC_PREDICTION"
    assert gate["toe_score_delta"] == 0.3


def test_gate_report_all_individual_gates_true():
    gate = p16_wsiii_gate_report()
    assert all(gate["gates"].values())


def test_summary_shape_and_values():
    summary = p16_wsiii_closure_summary()
    assert summary["parameter"] == "P16"
    assert summary["plus52"] == 52
    assert summary["status_after"] == "GEOMETRIC_PREDICTION"
    assert summary["all_gates_pass"] is True
