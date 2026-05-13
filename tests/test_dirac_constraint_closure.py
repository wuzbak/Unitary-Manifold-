# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 102-B — Dirac constraint algebra for the 5D minisuperspace."""

import pytest
import numpy as np

from src.core.dirac_constraint_closure import (
    N_W, K_CS, PHI0, PHI_R0, LAMBDA_GW,
    hamiltonian_constraint_5d,
    momentum_constraint_5d,
    poisson_bracket_HH,
    dirac_first_class_audit,
    physical_state_projector,
    lapse_contour_integral,
    dirac_constraint_closure_report,
)


# ---------- constants ---------------------------------------------------------

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_phi0():
    assert PHI0 == 1.0


def test_phi_r0():
    assert PHI_R0 == 1.0


def test_lambda_gw_positive():
    assert LAMBDA_GW > 0.0


# ---------- hamiltonian_constraint_5d ----------------------------------------

def test_H_perp_2d_returns_float():
    val = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=0.0)
    assert isinstance(val, float)


def test_H_perp_2d_finite():
    val = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=0.0)
    assert np.isfinite(val)


def test_H_perp_kinetic_contribution():
    # Increasing p_a should change H_perp
    h0 = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=0.0)
    h1 = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=2.0, p_phi=0.0)
    assert h1 < h0  # kinetic term is negative for p_a momentum


def test_H_perp_phi_kinetic():
    # Increasing p_phi should decrease H_perp
    h0 = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=0.0)
    h1 = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=2.0)
    assert h1 < h0


def test_H_perp_5d_radion():
    # Including radion field changes the result
    h_2d = hamiltonian_constraint_5d(a=1.0, phi=1.0, p_a=0.0, p_phi=0.0)
    h_5d = hamiltonian_constraint_5d(
        a=1.0, phi=1.0, p_a=0.0, p_phi=0.0, phi_r=2.0, p_r=0.0
    )
    assert h_5d != h_2d  # radion potential adds to H_perp


def test_H_perp_5d_radion_kinetic():
    # p_r kinetic term should lower H_perp
    h0 = hamiltonian_constraint_5d(
        a=1.0, phi=1.0, p_a=0.0, p_phi=0.0, phi_r=1.0, p_r=0.0
    )
    h1 = hamiltonian_constraint_5d(
        a=1.0, phi=1.0, p_a=0.0, p_phi=0.0, phi_r=1.0, p_r=2.0
    )
    assert h1 < h0


# ---------- momentum_constraint_5d -------------------------------------------

def test_momentum_constraint_zero():
    # Always 0 in the homogeneous minisuperspace
    val = momentum_constraint_5d(a=1.0, phi=1.0, p_a=1.0, p_phi=1.0)
    assert val == 0.0


def test_momentum_constraint_various():
    for a in [0.5, 1.5, 3.0]:
        for phi in [0.5, 1.0, 1.5]:
            assert momentum_constraint_5d(a=a, phi=phi, p_a=1.0, p_phi=1.0) == 0.0


# ---------- poisson_bracket_HH -----------------------------------------------

def test_pbHH_returns_dict():
    result = poisson_bracket_HH()
    assert isinstance(result, dict)


def test_pbHH_keys():
    result = poisson_bracket_HH()
    for key in ("bracket_value", "is_zero", "a", "phi", "p_a", "p_phi"):
        assert key in result


def test_pbHH_is_zero():
    result = poisson_bracket_HH(a=1.0, phi=1.0)
    assert result["is_zero"]
    assert abs(result["bracket_value"]) < 1e-8


def test_pbHH_grid():
    for a in [0.5, 1.0, 2.0]:
        for phi in [0.7, 1.0, 1.3]:
            res = poisson_bracket_HH(a=a, phi=phi)
            assert abs(res["bracket_value"]) < 1e-8, (
                f"bracket nonzero at a={a}, phi={phi}: {res['bracket_value']}"
            )


def test_pbHH_finite():
    result = poisson_bracket_HH(a=1.5, phi=1.2)
    assert np.isfinite(result["bracket_value"])


# ---------- dirac_first_class_audit ------------------------------------------

def test_audit_returns_dict():
    result = dirac_first_class_audit(n_samples=3)
    assert isinstance(result, dict)


def test_audit_keys():
    result = dirac_first_class_audit(n_samples=3)
    for key in ("all_first_class", "max_bracket_value", "n_checked",
                "bracket_values", "note"):
        assert key in result


def test_audit_all_first_class():
    result = dirac_first_class_audit(n_samples=4)
    assert result["all_first_class"]


def test_audit_max_bracket_small():
    result = dirac_first_class_audit(n_samples=4)
    assert result["max_bracket_value"] < 1e-7


def test_audit_n_checked():
    n = 4
    result = dirac_first_class_audit(n_samples=n)
    assert result["n_checked"] == n * n


def test_audit_bracket_values_list():
    result = dirac_first_class_audit(n_samples=3)
    assert isinstance(result["bracket_values"], list)
    assert len(result["bracket_values"]) == 9


def test_audit_note_string():
    result = dirac_first_class_audit(n_samples=3)
    assert isinstance(result["note"], str) and len(result["note"]) > 0


# ---------- physical_state_projector -----------------------------------------

def test_projector_returns_dict():
    result = physical_state_projector([0.01, 0.5, 1.0, 2.0])
    assert isinstance(result, dict)


def test_projector_keys():
    result = physical_state_projector([0.01, 0.5, 1.0])
    for key in ("physical_indices", "physical_eigenvalues",
                "zero_eigenvalue_count", "gap_to_next", "note"):
        assert key in result


def test_projector_identifies_near_zero():
    eigs = [0.001, 0.5, 1.0, 2.0]
    result = physical_state_projector(eigs)
    assert 0 in result["physical_indices"]


def test_projector_gap_positive():
    eigs = [0.01, 0.5, 1.0, 2.0]
    result = physical_state_projector(eigs)
    assert result["gap_to_next"] >= 0.0


def test_projector_count_positive():
    eigs = [0.001, 0.002, 0.5, 1.0]
    result = physical_state_projector(eigs)
    assert result["zero_eigenvalue_count"] >= 1


def test_projector_note_string():
    result = physical_state_projector([0.01, 1.0])
    assert isinstance(result["note"], str)


# ---------- lapse_contour_integral -------------------------------------------

def test_lapse_contour_returns_dict():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    assert isinstance(result, dict)


def test_lapse_contour_keys():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    for key in ("N_saddle_real", "N_saddle_imag", "action_at_saddle_real",
                "action_at_saddle_imag", "amplitude", "analytic_amplitude",
                "is_suppressed", "saddle_type"):
        assert key in result


def test_lapse_contour_amplitude_nonneg():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    assert result["amplitude"] >= 0.0


def test_lapse_contour_analytic_nonneg():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    assert result["analytic_amplitude"] >= 0.0


def test_lapse_contour_saddle_type():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    assert result["saddle_type"] in ("Euclidean", "Lorentzian")


def test_lapse_contour_is_suppressed_bool():
    result = lapse_contour_integral(a_f=1.5, phi_f=1.1)
    assert isinstance(result["is_suppressed"], bool)


def test_lapse_contour_finite():
    result = lapse_contour_integral(a_f=2.0, phi_f=0.8, a_i=0.0, phi_i=1.0)
    assert np.isfinite(result["amplitude"])


def test_lapse_contour_n_points():
    r64 = lapse_contour_integral(a_f=1.5, phi_f=1.1, n_points=64)
    r128 = lapse_contour_integral(a_f=1.5, phi_f=1.1, n_points=128)
    # Both should be finite and non-negative
    assert np.isfinite(r64["amplitude"]) and np.isfinite(r128["amplitude"])


# ---------- dirac_constraint_closure_report ----------------------------------

def test_report_returns_dict():
    report = dirac_constraint_closure_report()
    assert isinstance(report, dict)


def test_report_status():
    report = dirac_constraint_closure_report()
    assert report["status"] == "SUBSTANTIALLY_CLOSED"


def test_report_keys():
    report = dirac_constraint_closure_report()
    for key in ("status", "first_class_audit", "lapse_contour",
                "closure_evidence", "residual_open_items", "epistemic_label"):
        assert key in report


def test_report_first_class():
    report = dirac_constraint_closure_report()
    assert report["first_class_audit"]["all_first_class"]


def test_report_residual_open_nonempty():
    report = dirac_constraint_closure_report()
    assert len(report["residual_open_items"]) >= 4


def test_report_closure_evidence_nonempty():
    report = dirac_constraint_closure_report()
    assert len(report["closure_evidence"]) >= 3


def test_report_no_full_qg_claim():
    # The status must NOT claim "CLOSED" (only "SUBSTANTIALLY_CLOSED")
    report = dirac_constraint_closure_report()
    assert report["status"] != "CLOSED"
    assert "SUBSTANTIALLY" in report["status"]


def test_report_epistemic_label_honest():
    report = dirac_constraint_closure_report()
    label = report["epistemic_label"]
    # Must mention what remains open
    assert "open" in label.lower() or "remain" in label.lower()
