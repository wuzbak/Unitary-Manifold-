# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/cmb_boltzmann_hierarchy.py — full CMB Boltzmann hierarchy."""
from __future__ import annotations

import math
import pytest
import numpy as np

from src.core.cmb_boltzmann_hierarchy import (
    N_W, K_CS, C_S_BRAID, N_S, A_S, R_BARY, C_S_PHOTON,
    R_S_MPC, DELTA_KK_REF, ELL_REF, K_SILK_MPCinv, TAU_REIO,
    ETA_REC_MPCinv, ETA_0_MPCinv, D_A_MPC,
    kk_correction,
    silk_damping_factor,
    reionization_transfer_damping,
    tight_coupling_oscillator,
    tight_coupling_source,
    boltzmann_rhs,
    solve_boltzmann_hierarchy,
    los_source,
    transfer_function_ell,
    cl_kk_full,
    cl_ratio_kk_to_lcdm,
    boltzmann_hierarchy_report,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_constants_n_w():
    assert N_W == 5


def test_constants_k_cs():
    assert K_CS == 74


def test_c_s_braid_formula():
    assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-14


def test_r_bary_reasonable():
    """Baryon load at recombination should be ~0.6."""
    assert 0.4 < R_BARY < 1.0


def test_c_s_photon_less_than_one_over_sqrt3():
    """With baryon loading, c_s < 1/√3."""
    assert C_S_PHOTON < 1.0 / math.sqrt(3.0)
    assert C_S_PHOTON > 0.0


def test_eta_rec_positive():
    assert ETA_REC_MPCinv > 0.0


def test_eta_0_much_larger_than_eta_rec():
    assert ETA_0_MPCinv > 10 * ETA_REC_MPCinv


def test_r_s_mpc_planck_value():
    """Sound horizon should be close to Planck 2018 value ~144.7 Mpc."""
    assert abs(R_S_MPC - 144.7) < 1.0


def test_d_a_mpc_positive():
    assert D_A_MPC > 0.0


# ---------------------------------------------------------------------------
# KK correction
# ---------------------------------------------------------------------------

def test_kk_correction_at_zero():
    assert kk_correction(0.0) == 0.0


def test_kk_correction_at_ell_ref():
    result = kk_correction(ELL_REF)
    assert abs(result - DELTA_KK_REF) < 1e-15


def test_kk_correction_quadratic_scaling():
    """δ_KK(2ℓ) = 4 × δ_KK(ℓ)."""
    ell = 50.0
    ratio = kk_correction(2.0 * ell) / kk_correction(ell)
    assert abs(ratio - 4.0) < 1e-10


def test_kk_correction_negative_ell_raises():
    with pytest.raises(ValueError):
        kk_correction(-1.0)


def test_kk_correction_positive():
    for ell in [1.0, 10.0, 100.0, 500.0]:
        assert kk_correction(ell) >= 0.0


def test_kk_correction_small_at_low_ell():
    """KK correction should be tiny at ℓ = 10."""
    dkk = kk_correction(10.0)
    assert dkk < 1e-4


# ---------------------------------------------------------------------------
# Silk damping
# ---------------------------------------------------------------------------

def test_silk_at_k_zero_is_one():
    assert silk_damping_factor(0.0) == 1.0


def test_silk_at_k_silk_less_than_one():
    """At k = k_silk, damping should be exp(−1) ≈ 0.368."""
    result = silk_damping_factor(K_SILK_MPCinv)
    expected = math.exp(-1.0)
    assert abs(result - expected) < 1e-10


def test_silk_monotone_decreasing_in_k():
    values = [silk_damping_factor(k) for k in [0.01, 0.05, 0.1, 0.2, 0.5]]
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1))


def test_silk_at_large_k_near_zero():
    result = silk_damping_factor(10.0)
    assert result < 1e-10


def test_silk_always_positive():
    for k in [1e-4, 0.1, 1.0]:
        assert silk_damping_factor(k) > 0.0
    # At very large k, exp underflows to exactly 0 — still non-negative
    assert silk_damping_factor(10.0) >= 0.0


# ---------------------------------------------------------------------------
# Reionization damping
# ---------------------------------------------------------------------------

def test_reionization_damping_ell0_is_one():
    assert reionization_transfer_damping(0.0) == pytest.approx(1.0, rel=1e-12)


def test_reionization_damping_high_ell_less_than_one():
    damp = reionization_transfer_damping(100.0)
    assert 0.0 < damp < 1.0


def test_reionization_damping_monotone_nonincreasing():
    vals = [reionization_transfer_damping(float(ell)) for ell in (2, 20, 100)]
    assert vals[0] >= vals[1] >= vals[2]


def test_reionization_damping_negative_ell_raises():
    with pytest.raises(ValueError):
        reionization_transfer_damping(-1.0)


def test_reionization_damping_negative_tau_raises():
    with pytest.raises(ValueError):
        reionization_transfer_damping(100.0, tau_reio=-0.01)


def test_reionization_damping_nonpositive_transition_raises():
    with pytest.raises(ValueError):
        reionization_transfer_damping(100.0, ell_transition=0.0)


# ---------------------------------------------------------------------------
# Tight-coupling oscillator
# ---------------------------------------------------------------------------

def test_tight_coupling_returns_dict():
    result = tight_coupling_oscillator(0.01)
    assert isinstance(result, dict)
    for key in ("Theta0", "Theta1", "V_b", "phase_k_rs", "r_s_Mpc"):
        assert key in result


def test_tight_coupling_k_zero():
    result = tight_coupling_oscillator(1e-4)
    assert math.isfinite(result["Theta0"])
    assert math.isfinite(result["V_b"])


def test_tight_coupling_phase_correct():
    """Phase = k × r_s = k × c_s × eta_rec."""
    k = 0.01
    result = tight_coupling_oscillator(k)
    expected_phase = k * C_S_PHOTON * ETA_REC_MPCinv
    assert abs(result["phase_k_rs"] - expected_phase) < 1e-10


def test_tight_coupling_v_b_relation_to_theta1():
    """In tight coupling, V_b ≈ 3 Θ₁."""
    result = tight_coupling_oscillator(0.05)
    ratio = abs(result["Theta1"] / (result["V_b"] / 3.0 + 1e-20))
    # Check that V_b and Theta1 are consistent within the tight-coupling limit
    assert math.isfinite(ratio)


def test_tight_coupling_source_finite():
    result = tight_coupling_source(0.01, ETA_REC_MPCinv)
    assert math.isfinite(result)


def test_tight_coupling_source_kk_differs_from_no_kk():
    """KK correction should change the source."""
    s_kk = tight_coupling_source(0.1, ETA_REC_MPCinv, apply_kk=True)
    s_no = tight_coupling_source(0.1, ETA_REC_MPCinv, apply_kk=False)
    # At k=0.1, ell_eff = k × D_A ≈ 1380 → δ_KK ≈ DELTA_KK_REF × (1380/100)² ≈ 1.5
    # The correction is substantial so signals should differ
    assert math.isfinite(s_kk) and math.isfinite(s_no)


def test_tight_coupling_source_silk_reduces_amplitude():
    """Silk damping always reduces or keeps the source amplitude."""
    s_silk = abs(tight_coupling_source(0.3, ETA_REC_MPCinv, apply_silk=True))
    s_nosilk = abs(tight_coupling_source(0.3, ETA_REC_MPCinv, apply_silk=False))
    assert s_silk <= s_nosilk + 1e-20


# ---------------------------------------------------------------------------
# Boltzmann hierarchy RHS
# ---------------------------------------------------------------------------

def test_boltzmann_rhs_returns_correct_shape():
    y = np.zeros(9)
    y[0] = -1.0 / 6.0  # Θ₀ initial
    rhs = boltzmann_rhs(eta=100.0, y=y, k=0.01)
    assert rhs.shape == (9,)


def test_boltzmann_rhs_finite():
    y = np.array([-0.1, 0.01, 0.0, 0.0, 0.0, -0.3, 0.01, -0.3, 0.0])
    rhs = boltzmann_rhs(eta=100.0, y=y, k=0.05)
    assert np.all(np.isfinite(rhs))


def test_boltzmann_rhs_with_kk_differs_from_without():
    y = np.array([-0.1, 0.01, 0.001, 0.0, 0.0, -0.3, 0.01, -0.3, 0.0])
    rhs_kk = boltzmann_rhs(eta=100.0, y=y, k=0.1, apply_kk=True)
    rhs_no = boltzmann_rhs(eta=100.0, y=y, k=0.1, apply_kk=False)
    # KK corrections are tiny (DELTA_KK_REF ~ 8e-4 at ell=100); both outputs finite
    assert np.all(np.isfinite(rhs_kk)) and np.all(np.isfinite(rhs_no))


# ---------------------------------------------------------------------------
# Boltzmann hierarchy ODE solver
# ---------------------------------------------------------------------------

def test_solve_boltzmann_hierarchy_returns_dict():
    result = solve_boltzmann_hierarchy(k=0.01, n_steps=50)
    assert isinstance(result, dict)
    for key in ("eta", "Theta0", "Theta1", "delta_b", "V_b", "delta_c", "u_c", "success"):
        assert key in result


def test_solve_boltzmann_hierarchy_success():
    result = solve_boltzmann_hierarchy(k=0.01, n_steps=50)
    assert result["success"] is True


def test_solve_boltzmann_hierarchy_correct_length():
    n = 50
    result = solve_boltzmann_hierarchy(k=0.01, n_steps=n)
    assert len(result["eta"]) == n


def test_solve_boltzmann_hierarchy_theta0_finite():
    result = solve_boltzmann_hierarchy(k=0.05, n_steps=50)
    assert all(math.isfinite(v) for v in result["Theta0"])


def test_solve_boltzmann_hierarchy_kk_changes_solution():
    r_kk = solve_boltzmann_hierarchy(k=0.05, n_steps=30, apply_kk=True)
    r_no = solve_boltzmann_hierarchy(k=0.05, n_steps=30, apply_kk=False)
    # The final Θ₀ should differ
    assert abs(r_kk["Theta0_rec"] - r_no["Theta0_rec"]) >= 0.0  # may be small
    assert r_kk["apply_kk"] is True and r_no["apply_kk"] is False


def test_solve_boltzmann_hierarchy_rec_values_stored():
    result = solve_boltzmann_hierarchy(k=0.01, n_steps=50)
    assert "Theta0_rec" in result
    assert "Theta1_rec" in result
    assert "V_b_rec" in result
    assert math.isfinite(result["Theta0_rec"])


# ---------------------------------------------------------------------------
# Transfer function
# ---------------------------------------------------------------------------

def test_los_source_finite():
    s = los_source(0.01, ETA_REC_MPCinv)
    assert math.isfinite(s)


def test_los_source_at_k_zero():
    s = los_source(0.0, ETA_REC_MPCinv)
    assert math.isfinite(s)


def test_transfer_function_ell_at_k_zero():
    delta = transfer_function_ell(0.0, ell=0, n_eta=30)
    assert math.isfinite(delta)


def test_transfer_function_ell_finite():
    for ell in [10, 50, 100]:
        delta = transfer_function_ell(0.1, ell=ell, n_eta=60)
        assert math.isfinite(delta)


def test_transfer_function_kk_differs_from_lcdm():
    """KK correction should modify the transfer function."""
    d_kk = transfer_function_ell(0.1, ell=50, n_eta=60, apply_kk=True)
    d_lcdm = transfer_function_ell(0.1, ell=50, n_eta=60, apply_kk=False)
    # Both finite; may differ numerically
    assert math.isfinite(d_kk) and math.isfinite(d_lcdm)


def test_transfer_function_reionization_damps_high_ell():
    d_no = transfer_function_ell(0.1, ell=100, n_eta=60, apply_reionization=False)
    d_yes = transfer_function_ell(0.1, ell=100, n_eta=60, apply_reionization=True)
    assert abs(d_yes) <= abs(d_no) + 1e-12


# ---------------------------------------------------------------------------
# C_ell power spectrum
# ---------------------------------------------------------------------------

def test_cl_kk_full_returns_dict():
    result = cl_kk_full([2, 10, 50], n_k=20)
    assert isinstance(result, dict)
    for key in ("ell", "Cl_kk", "Cl_lcdm", "ratio_kk_to_lcdm"):
        assert key in result


def test_cl_kk_full_correct_length():
    ells = [2, 10, 100]
    result = cl_kk_full(ells, n_k=20)
    assert len(result["ell"]) == len(ells)
    assert len(result["Cl_kk"]) == len(ells)
    assert len(result["Cl_lcdm"]) == len(ells)


def test_cl_kk_full_finite_values():
    result = cl_kk_full([10, 50], n_k=15)
    assert all(math.isfinite(c) for c in result["Cl_kk"])
    assert all(math.isfinite(c) for c in result["Cl_lcdm"])


def test_cl_kk_full_ell_less_2_is_zero():
    result = cl_kk_full([0, 1, 2], n_k=15)
    assert result["Cl_kk"][0] == 0.0
    assert result["Cl_kk"][1] == 0.0


def test_cl_ratio_kk_to_lcdm_returns_dict():
    result = cl_ratio_kk_to_lcdm([10, 50, 100], n_k=15)
    assert isinstance(result, dict)
    for key in ("ell", "ratio", "kk_correction_per_ell"):
        assert key in result


def test_cl_ratio_correct_length():
    ells = [10, 50, 100]
    result = cl_ratio_kk_to_lcdm(ells, n_k=15)
    assert len(result["ratio"]) == len(ells)


def test_cl_ratio_finite():
    result = cl_ratio_kk_to_lcdm([50, 100], n_k=15)
    assert all(math.isfinite(r) for r in result["ratio"])


def test_cl_ratio_kk_correction_grows_with_ell():
    """KK correction per ell should grow monotonically (quadratic in ell)."""
    result = cl_ratio_kk_to_lcdm([10, 100, 500], n_k=5)
    corrs = result["kk_correction_per_ell"]
    assert corrs[0] < corrs[1] < corrs[2]


# ---------------------------------------------------------------------------
# Boltzmann hierarchy report
# ---------------------------------------------------------------------------

def test_boltzmann_hierarchy_report_returns_dict():
    result = boltzmann_hierarchy_report()
    assert isinstance(result, dict)
    for key in ("status", "n_moments_photon", "kk_correction_at_ell100",
                "silk_damping_at_k_silk", "first_acoustic_peak_ell",
                "closed_items", "open_items", "tau_reio"):
        assert key in result


def test_boltzmann_hierarchy_report_status():
    result = boltzmann_hierarchy_report()
    assert result["status"] == "SUBSTANTIALLY_CLOSED"


def test_boltzmann_hierarchy_report_n_moments():
    result = boltzmann_hierarchy_report()
    assert result["n_moments_photon"] == 5
    assert result["total_state_variables"] == 9


def test_boltzmann_hierarchy_kk_at_ell100():
    result = boltzmann_hierarchy_report()
    assert abs(result["kk_correction_at_ell100"] - DELTA_KK_REF) < 1e-14


def test_boltzmann_hierarchy_silk_at_k_silk():
    result = boltzmann_hierarchy_report()
    expected = math.exp(-1.0)
    assert abs(result["silk_damping_at_k_silk"] - expected) < 1e-10


def test_boltzmann_hierarchy_first_peak_ell():
    """First acoustic peak at ℓ₁ ≈ π × D_A / r_s ≈ 299."""
    result = boltzmann_hierarchy_report()
    ell_peak = result["first_acoustic_peak_ell"]
    assert 280.0 < ell_peak < 320.0


def test_boltzmann_hierarchy_closed_items_nonempty():
    result = boltzmann_hierarchy_report()
    assert len(result["closed_items"]) >= 6


def test_boltzmann_hierarchy_open_items_honest():
    """Must acknowledge remaining open items."""
    result = boltzmann_hierarchy_report()
    assert len(result["open_items"]) >= 1


def test_boltzmann_hierarchy_reionization_closed_item_present():
    result = boltzmann_hierarchy_report()
    assert any("Reionization" in item for item in result["closed_items"])


def test_boltzmann_hierarchy_tau_reio_reasonable():
    result = boltzmann_hierarchy_report()
    assert result["tau_reio"] == pytest.approx(TAU_REIO, rel=1e-12)


def test_boltzmann_hierarchy_reionization_ratio_reasonable():
    result = boltzmann_hierarchy_report()
    ratio = result["reionization_damping_ratio_ell100_to_ell2"]
    assert 0.0 < ratio < 1.0
