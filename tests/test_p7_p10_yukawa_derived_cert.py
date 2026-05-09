# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P7–P10 Yukawa quartet DERIVED certification."""
from src.core.p7_p10_yukawa_derived_cert import (
    ALL_GATES_PASS,
    BRAID_NLO_SUPPRESSION_MAP,
    GATE_AXIOMZERO_PASS,
    GATE_CROSS_GENERATION_PASS,
    GATE_P10_NOMINAL_PASS,
    GATE_P7_NOMINAL_PASS,
    GATE_P8_NOMINAL_PASS,
    GATE_P9_NOMINAL_PASS,
    yukawa_derived_gate_report,
    yukawa_derived_summary,
)


def test_gate_p7_nominal_pass():
    assert GATE_P7_NOMINAL_PASS is True


def test_gate_p8_nominal_pass():
    assert GATE_P8_NOMINAL_PASS is True


def test_gate_p9_nominal_pass():
    assert GATE_P9_NOMINAL_PASS is True


def test_gate_p10_nominal_pass():
    assert GATE_P10_NOMINAL_PASS is True


def test_cross_generation_hierarchy():
    assert GATE_CROSS_GENERATION_PASS is True


def test_axiomzero_gate():
    assert GATE_AXIOMZERO_PASS is True


def test_all_gates_pass():
    assert ALL_GATES_PASS is True


def test_status_after_derived():
    report = yukawa_derived_gate_report()
    assert report["status_after"] == "DERIVED"


def test_toe_score_delta():
    report = yukawa_derived_gate_report()
    assert report["toe_score_delta"] == 0.8


def test_axiomzero_empty():
    report = yukawa_derived_gate_report()
    assert report["axiomzero_pdg_inputs"] == []


def test_all_four_parameters_present():
    report = yukawa_derived_gate_report()
    for pid in ("P7", "P8", "P9", "P10"):
        assert pid in report["per_parameter"]


def test_per_parameter_status():
    report = yukawa_derived_gate_report()
    for pid in ("P7", "P8", "P9", "P10"):
        assert report["per_parameter"][pid]["status_after"] == "DERIVED"


def test_nlo_suppression_map_geometric_fractions():
    """NLO suppression factors are integer/rational braid-sector numbers."""
    assert abs(BRAID_NLO_SUPPRESSION_MAP["top"] - 69.0 / 74.0) < 1e-12
    assert abs(BRAID_NLO_SUPPRESSION_MAP["bottom"] - 2.0 / 37.0) < 1e-12
    assert abs(BRAID_NLO_SUPPRESSION_MAP["tau"] - 1.0 / 31.0) < 1e-12
    assert abs(BRAID_NLO_SUPPRESSION_MAP["electron"] - 1.0 / 3700.0) < 1e-12


def test_summary_yukawa():
    s = yukawa_derived_summary()
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.8
    assert s["axiomzero_pdg_inputs"] == []
    assert set(s["parameters"]) == {"P7", "P8", "P9", "P10"}
