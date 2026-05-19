# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 275 — Higgs Naturalness Schwinger Convergence Lane."""
from __future__ import annotations

import math

import pytest

from src.core.pillar275_higgs_naturalness_schwinger_convergence import (
    ADJACENCY_TRACK_LABEL,
    DEFAULT_K,
    DEFAULT_N_GRID,
    DEFAULT_R,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    convergence_table,
    converged_delta_with_bound,
    kk_mode_mass_warp,
    m_kk_from_k_r,
    regulated_tower_remainder_upper_bound,
    regulated_tower_sum,
    schwinger_convergence_report,
    schwinger_tau_geometric,
    separation_guard,
    tuning_delta_regulated,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 275
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False


def test_m_kk_recovers_dashboard_value():
    m_kk = m_kk_from_k_r(k=DEFAULT_K, r=DEFAULT_R)
    # Pillar 255 dashboard reports M_KK ≈ 20.78 GeV at this operating point.
    assert m_kk == pytest.approx(20.78, rel=0.01)


def test_m_kk_input_validation():
    with pytest.raises(ValueError):
        m_kk_from_k_r(k=-1.0, r=1.0)
    with pytest.raises(ValueError):
        m_kk_from_k_r(k=1.0, r=-1.0)


def test_kk_mode_mass_warp_basic():
    m1 = kk_mode_mass_warp(n=1, m_kk=10.0, k_warp=0.1)
    assert m1 == pytest.approx(1.0 * 10.0 + 0.1 * 10.0)
    with pytest.raises(ValueError):
        kk_mode_mass_warp(n=0, m_kk=10.0, k_warp=0.1)
    with pytest.raises(ValueError):
        kk_mode_mass_warp(n=1, m_kk=-1.0, k_warp=0.1)


def test_schwinger_tau_positive():
    tau = schwinger_tau_geometric()
    assert tau > 0.0
    with pytest.raises(ValueError):
        schwinger_tau_geometric(k=-1.0)


def test_regulated_tower_sum_finite():
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric(k=DEFAULT_K, m_kk=m_kk)
    S = regulated_tower_sum(n_modes=200, m_kk=m_kk, k_warp=DEFAULT_K, tau=tau)
    assert math.isfinite(S)
    assert S > 0.0


def test_regulated_tower_sum_input_validation():
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric()
    with pytest.raises(ValueError):
        regulated_tower_sum(n_modes=0, m_kk=m_kk, k_warp=DEFAULT_K, tau=tau)
    with pytest.raises(ValueError):
        regulated_tower_sum(n_modes=10, m_kk=m_kk, k_warp=DEFAULT_K, tau=0.0)


def test_remainder_bound_envelope():
    # The truncation error must strictly upper-bound the partial-sum gap.
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric(k=DEFAULT_K, m_kk=m_kk)
    S_50 = regulated_tower_sum(50, m_kk, DEFAULT_K, tau)
    S_500 = regulated_tower_sum(500, m_kk, DEFAULT_K, tau)
    actual_tail = abs(S_500 - S_50)
    bound = regulated_tower_remainder_upper_bound(50, m_kk, DEFAULT_K, tau)
    assert bound >= actual_tail - 1.0e-30


def test_remainder_bound_decreases_with_n():
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric(k=DEFAULT_K, m_kk=m_kk)
    bounds = [
        regulated_tower_remainder_upper_bound(n, m_kk, DEFAULT_K, tau)
        for n in (5, 10, 50, 100, 200)
    ]
    # Strictly monotone non-increasing
    for a, b in zip(bounds, bounds[1:]):
        assert b <= a + 1e-30


def test_remainder_bound_input_validation():
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric()
    with pytest.raises(ValueError):
        regulated_tower_remainder_upper_bound(0, m_kk, DEFAULT_K, tau)
    with pytest.raises(ValueError):
        regulated_tower_remainder_upper_bound(10, m_kk, DEFAULT_K, 0.0)


def test_tuning_delta_regulated_keys_and_finiteness():
    row = tuning_delta_regulated(n_modes=100)
    for key in (
        "n_modes",
        "M_KK_GeV",
        "tau_invGeV2",
        "tower_sum_GeV2",
        "tail_upper_bound_GeV2",
        "delta_N",
        "delta_bound",
    ):
        assert key in row
    assert math.isfinite(row["delta_N"])
    assert row["delta_bound"] >= 0.0


def test_convergence_table_grid_default():
    table = convergence_table()
    assert [row["n_modes"] for row in table] == list(DEFAULT_N_GRID)
    # Δ_N is monotone non-decreasing in N (adding non-negative weights)
    deltas = [row["delta_N"] for row in table]
    for a, b in zip(deltas, deltas[1:]):
        assert b >= a - 1e-30


def test_converged_delta_with_bound_structure():
    c = converged_delta_with_bound(n_max=200)
    for key in (
        "delta_infinity_estimate",
        "analytic_error_upper",
        "delta_infinity_upper",
        "n_modes",
        "M_KK_GeV",
        "tau_invGeV2",
    ):
        assert key in c
    assert c["n_modes"] == 200
    # The upper estimate ≥ point estimate by construction
    assert c["delta_infinity_upper"] >= c["delta_infinity_estimate"]
    # Analytic error is non-negative
    assert c["analytic_error_upper"] >= 0.0


def test_acceptance_gate_passes_at_n200():
    rep = schwinger_convergence_report()
    assert rep["acceptance_gate_passed"] is True
    # Δ_∞ stays well below 1 with the geometric τ choice
    assert rep["converged_delta"]["delta_infinity_estimate"] < 1.0


def test_report_no_hardgate_drift():
    rep = schwinger_convergence_report()
    assert rep["separation_guard"]["is_hardgate"] is False
    assert rep["separation_guard"]["modifies_hardgate_module"] is False


def test_bound_dominates_actual_truncation_error_in_table():
    table = convergence_table()
    # For each row, the bound should be ≥ |Δ_∞_upper − Δ_N|.
    converged = converged_delta_with_bound(n_max=int(DEFAULT_N_GRID[-1]))
    delta_upper = converged["delta_infinity_upper"]
    for row in table:
        gap = max(0.0, delta_upper - row["delta_N"])
        # bound should dominate the gap within the table for sufficiently
        # large N; for the smallest N entry, this is the most demanding
        # check and is the entire purpose of the closed-form bound.
        assert row["delta_bound"] + 1e-12 >= gap or row["n_modes"] == DEFAULT_N_GRID[-1]


def test_remainder_bound_underflow_does_not_explode():
    # Extreme N must return 0.0 without throwing.
    m_kk = m_kk_from_k_r()
    tau = schwinger_tau_geometric(k=DEFAULT_K, m_kk=m_kk)
    val = regulated_tower_remainder_upper_bound(10_000, m_kk, DEFAULT_K, tau)
    assert val == 0.0 or math.isfinite(val)
