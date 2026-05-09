# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/strong_cp_pq_z2_closure.py."""

from src.core.strong_cp_pq_z2_closure import (
    THETA_PDG_BOUND,
    pq_anomaly_coupling,
    strong_cp_closure_summary,
    strong_cp_gate_report,
    theta_effective,
    theta_loop_induced,
    theta_tree_level,
)


def test_theta_tree_level_zero():
    assert theta_tree_level() == 0.0


def test_pq_coupling_positive():
    assert pq_anomaly_coupling() > 0.0


def test_theta_loop_positive_and_tiny():
    theta = theta_loop_induced()
    assert theta > 0.0
    assert theta < THETA_PDG_BOUND


def test_theta_effective_below_bound():
    assert theta_effective() < THETA_PDG_BOUND


def test_gate_report_all_pass():
    gate = strong_cp_gate_report()
    assert gate["all_gates_pass"] is True
    assert gate["status_after"] == "GEOMETRIC_PREDICTION"


def test_gate_report_individual_gates_true():
    gate = strong_cp_gate_report()
    assert all(gate["gates"].values())


def test_summary_matches_gate():
    summary = strong_cp_closure_summary()
    assert summary["parameter"] == "P27"
    assert summary["status_after"] == "GEOMETRIC_PREDICTION"
    assert summary["all_gates_pass"] is True


def test_theta_effective_recorded_in_summary_is_below_bound():
    summary = strong_cp_closure_summary()
    assert summary["theta_effective"] < summary["theta_bound"]
