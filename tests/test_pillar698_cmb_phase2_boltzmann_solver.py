# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 698 — CMB Phase 2 Boltzmann solver."""
from __future__ import annotations

import pytest

from src.core.pillar698_cmb_phase2_boltzmann_solver import (
    A_S_LCDM,
    C_S,
    DELTA_KK,
    ELL_MAX,
    H0_KM_S_MPC,
    HIERARCHY_MODE,
    K_CS,
    N_S,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TAU_REC_MPC,
    Z_REC,
    cl_from_hierarchy,
    phase2_amplitude_audit,
    solve_boltzmann_kk,
)

SOLUTION = solve_boltzmann_kk(0.02, n_tau_steps=80)
CL_200 = cl_from_hierarchy(200, n_k=8)
CL_540 = cl_from_hierarchy(540, n_k=8)
AUDIT = phase2_amplitude_audit()


def test_constants_match_task():
    assert PILLAR_NUMBER == 698
    assert N_W == 5
    assert K_CS == 74
    assert C_S == 12.0 / 37.0
    assert DELTA_KK == 8.0e-4


def test_cosmology_constants_match_task():
    assert Z_REC == 1100
    assert TAU_REC_MPC == 282.0
    assert H0_KM_S_MPC == 67.4
    assert A_S_LCDM == 2.10e-9
    assert N_S == 0.9649


def test_status_and_mode_labels():
    assert "PHASE2" in PILLAR_STATUS
    assert HIERARCHY_MODE == "SIMPLIFIED_HIERARCHY"


def test_solver_returns_dict():
    assert isinstance(SOLUTION, dict)


def test_solver_tau_grid_length():
    assert len(SOLUTION["tau_grid"]) == 80


def test_solver_history_length():
    assert len(SOLUTION["theta_history"]) == 80


def test_solver_ell_max():
    assert SOLUTION["ell_max"] == ELL_MAX == 10


def test_solver_final_multipoles_count():
    assert len(SOLUTION["theta_final"]) == ELL_MAX + 1


def test_solver_monopole_starts_nonzero():
    assert SOLUTION["theta_history"][0][0] == 1.0


def test_solver_keeps_finite_values():
    assert all(abs(value) < 1.0e8 for value in SOLUTION["theta_history"][-1])


def test_solver_rejects_nonpositive_k():
    with pytest.raises(ValueError):
        solve_boltzmann_kk(0.0)


def test_solver_rejects_too_few_steps():
    with pytest.raises(ValueError):
        solve_boltzmann_kk(0.02, n_tau_steps=10)


def test_cl_200_positive():
    assert CL_200["c_ell"] > 0.0


def test_cl_540_positive():
    assert CL_540["c_ell"] > 0.0


def test_cl_200_exceeds_cl_540():
    assert CL_200["c_ell"] > CL_540["c_ell"]


def test_cl_reports_peak_window():
    assert CL_200["k_min_mpc"] < CL_200["k_peak_mpc"] < CL_200["k_max_mpc"]


def test_cl_rejects_low_ell():
    with pytest.raises(ValueError):
        cl_from_hierarchy(1)


def test_cl_rejects_too_few_k_samples():
    with pytest.raises(ValueError):
        cl_from_hierarchy(200, n_k=3)


def test_audit_contains_peak_ratio():
    assert AUDIT["peak_ratio_2_to_1"] > 0.0


def test_audit_is_honest_about_approximation():
    assert AUDIT["honesty_label"] == "SIMPLIFIED_HIERARCHY"
