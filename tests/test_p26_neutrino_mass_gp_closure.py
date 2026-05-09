# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P26 CONSTRAINED→GEOMETRIC_PREDICTION closure (neutrino mass)."""
from src.core.p26_neutrino_mass_gp_closure import (
    M_NU_GEO_EV, M_NU_PDG_BOUND_EV, SUM_MNU_GEO_EV,
    p26_gp_gate_report, p26_gp_summary,
)


def test_mass_positive():
    assert M_NU_GEO_EV > 0.0


def test_below_planck_bound():
    assert M_NU_GEO_EV < M_NU_PDG_BOUND_EV


def test_sum_below_planck_bound():
    assert SUM_MNU_GEO_EV < M_NU_PDG_BOUND_EV


def test_all_gates_pass():
    assert p26_gp_gate_report()["all_gates_pass"] is True


def test_status_after_gp():
    assert p26_gp_gate_report()["status_after"] == "GEOMETRIC_PREDICTION"


def test_toe_delta():
    assert p26_gp_gate_report()["toe_score_delta"] == 0.3


def test_axiomzero_empty():
    assert p26_gp_gate_report()["axiomzero_pdg_inputs"] == []


def test_falsification_condition_present():
    s = p26_gp_summary()
    assert "KATRIN" in s["falsification"] or "Planck" in s["falsification"]


def test_summary_p26():
    s = p26_gp_summary()
    assert s["parameter"] == "P26"
    assert s["all_gates_pass"] is True
    assert s["toe_score_delta"] == 0.3
