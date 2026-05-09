# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/adm_quantitative_closure.py."""

from src.core.adm_quantitative_closure import (
    DEFAULT_PHI_GRID,
    adm_constraint_audit,
    adm_falsifier_interface,
    adm_quantitative_closure_report,
    lapse_scaling_invariance,
)


def test_default_grid_contains_attractor():
    assert 1.0 in DEFAULT_PHI_GRID


def test_lapse_invariance_passes_default_grid():
    report = lapse_scaling_invariance()
    assert report["positive_lapse"] is True
    assert report["strictly_monotone_decreasing"] is True
    assert report["all_pass"] is True


def test_constraint_audit_passes_vacuum():
    report = adm_constraint_audit()
    assert report["hamiltonian_all_vacuum_satisfied"] is True
    assert report["momentum_all_satisfied"] is True
    assert report["all_pass"] is True


def test_falsifier_interface_pass_at_attractor():
    report = adm_falsifier_interface(phi_0=1.0, sigma_dt_threshold=1e-9)
    assert report["route"] == "PASS"
    assert report["dt_mismatch"] < 1e-9


def test_falsifier_interface_not_pass_off_attractor():
    report = adm_falsifier_interface(phi_0=2.0, sigma_dt_threshold=1e-9)
    assert report["route"] in {"TENSION", "FALSIFIED"}


def test_quantitative_closure_report_is_closed():
    report = adm_quantitative_closure_report()
    assert report["all_gates_pass"] is True
    assert report["status"] == "CLOSED_QUANTITATIVE"


def test_quantitative_report_contains_sections():
    report = adm_quantitative_closure_report()
    assert "lapse_invariance" in report
    assert "constraint_audit" in report
    assert "consistency_check" in report
    assert "falsifier_interface_attractor" in report
