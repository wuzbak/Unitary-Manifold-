# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 103 — CMB E-mode polarisation Boltzmann hierarchy."""

import pytest
import numpy as np

from src.core.cmb_polarisation import (
    N_S, A_S, K_PIVOT, TAU_REIO, DELTA_KK_REF, ELL_REF,
    polarisation_boltzmann_rhs,
    solve_polarisation_hierarchy,
    cl_ee_spectrum,
    cl_te_spectrum,
    cl_bb_upper_limit,
    reionisation_bump,
    cmb_polarisation_report,
    _kappa_dot,
)


# ---------- constant sanity checks ----------

def test_tau_reio():
    assert abs(TAU_REIO - 0.054) < 1e-10


def test_n_s():
    assert abs(N_S - 0.9649) < 1e-10


def test_a_s():
    assert abs(A_S - 2.101e-9) < 1e-15


def test_k_pivot():
    assert abs(K_PIVOT - 0.05) < 1e-10


def test_delta_kk_ref():
    assert DELTA_KK_REF > 0.0


def test_ell_ref():
    assert ELL_REF == 100.0


# ---------- Boltzmann RHS ----------

def test_polarisation_rhs_length():
    y0 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    rhs = polarisation_boltzmann_rhs(100.0, y0, k=0.05, kappa_dot=_kappa_dot)
    assert len(rhs) == 6


def test_polarisation_rhs_finite():
    y0 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    rhs = polarisation_boltzmann_rhs(100.0, y0, k=0.05, kappa_dot=_kappa_dot)
    assert all(np.isfinite(v) for v in rhs)


def test_polarisation_rhs_theta0_depends_on_theta1():
    # dΘ₀/dη = -k Θ₁, so with Θ₁=0 → dΘ₀=0
    y0 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    rhs = polarisation_boltzmann_rhs(100.0, y0, k=0.1, kappa_dot=_kappa_dot)
    assert rhs[0] == 0.0


def test_polarisation_rhs_zero_state():
    y0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    rhs = polarisation_boltzmann_rhs(100.0, y0, k=0.05, kappa_dot=_kappa_dot)
    assert all(v == 0.0 for v in rhs)


# ---------- solve hierarchy ----------

def test_solve_polarisation_dict():
    result = solve_polarisation_hierarchy(k_mpc=0.05, eta_max=200.0)
    assert isinstance(result, dict)


def test_solve_polarisation_keys():
    result = solve_polarisation_hierarchy(k_mpc=0.05, eta_max=200.0)
    for key in ("Theta", "Pi", "eta_arr"):
        assert key in result


def test_solve_polarisation_shapes():
    result = solve_polarisation_hierarchy(k_mpc=0.05, eta_max=200.0)
    assert result["Theta"].shape[0] == 3
    assert result["Pi"].shape[0] == 3


def test_solve_polarisation_eta_increasing():
    result = solve_polarisation_hierarchy(k_mpc=0.05, eta_max=200.0)
    assert np.all(np.diff(result["eta_arr"]) > 0)


# ---------- power spectra ----------

def test_cl_ee_positive():
    cl = cl_ee_spectrum(ell_max=50)
    assert np.all(cl > 0)


def test_ee_spectrum_length():
    ell_max = 50
    cl = cl_ee_spectrum(ell_max=ell_max)
    assert len(cl) == ell_max - 1  # ell = 2..ell_max


def test_cl_ee_finite():
    cl = cl_ee_spectrum(ell_max=100)
    assert np.all(np.isfinite(cl))


def test_cl_te_finite():
    cl = cl_te_spectrum(ell_max=100)
    assert np.all(np.isfinite(cl))


def test_cl_te_positive():
    cl = cl_te_spectrum(ell_max=100)
    assert np.all(cl >= 0.0)


def test_cl_te_spectrum_length():
    ell_max = 60
    cl = cl_te_spectrum(ell_max=ell_max)
    assert len(cl) == ell_max - 1


def test_cl_bb_upper_limit_positive():
    cl = cl_bb_upper_limit(ell_max=100)
    assert np.all(cl > 0)


def test_cl_bb_upper_limit_length():
    ell_max = 80
    cl = cl_bb_upper_limit(ell_max=ell_max)
    assert len(cl) == ell_max - 1


def test_cl_bb_less_than_tt():
    # B-mode should be < TT at all ell
    from src.core.cmb_polarisation import _cl_tt_raw
    ell = np.arange(2, 51, dtype=float)
    cl_bb = cl_bb_upper_limit(ell_max=50)
    cl_tt = _cl_tt_raw(ell)
    assert np.all(cl_bb < cl_tt)


# ---------- reionisation bump ----------

def test_reionisation_bump_positive():
    ell = np.array([2.0, 3.0, 4.0, 5.0])
    bump = reionisation_bump(ell)
    assert np.all(bump >= 0.0)


def test_reionisation_bump_zero_for_large_ell():
    ell = np.array([11.0, 20.0, 50.0])
    bump = reionisation_bump(ell)
    assert np.all(bump == 0.0)


def test_reionisation_bump_peak_at_ell3():
    ell = np.array([2.0, 3.0, 4.0, 5.0])
    bump = reionisation_bump(ell)
    # ℓ=3 should be the peak (Gaussian centred at 3)
    assert bump[1] >= bump[0]
    assert bump[1] >= bump[2]


def test_reionisation_bump_length():
    ell = np.arange(2, 12, dtype=float)
    bump = reionisation_bump(ell)
    assert len(bump) == len(ell)


# ---------- report ----------

def test_report_keys():
    report = cmb_polarisation_report()
    for key in ("status", "module", "residual_unknowns", "epistemic_label"):
        assert key in report


def test_report_status():
    report = cmb_polarisation_report()
    assert report["status"] == "OPEN"


def test_report_module():
    report = cmb_polarisation_report()
    assert report["module"] == "cmb_polarisation"


def test_report_residual_unknowns_nonempty():
    report = cmb_polarisation_report()
    assert len(report["residual_unknowns"]) > 0
