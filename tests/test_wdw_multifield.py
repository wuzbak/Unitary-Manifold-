# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 102 — 2D minisuperspace Wheeler-DeWitt equation."""

import pytest
import numpy as np

from src.core.wdw_multifield import (
    N_W, K_CS, PHI0, PI_KR, C_S_BRAID,
    build_2d_wdw_hamiltonian,
    solve_2d_wdw_spectrum,
    lapse_saddle_point,
    operator_ordering_2d_comparison,
    wdw_multifield_report,
)

# Use small grids throughout for speed
N_A_TEST = 10
N_PHI_TEST = 10


# ---------- constant sanity checks ----------

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_phi0():
    assert PHI0 == 1.0


def test_pi_kr():
    assert PI_KR == 37.0


def test_c_s_braid():
    assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-12


# ---------- Hamiltonian ----------

def test_build_hamiltonian_shape():
    H = build_2d_wdw_hamiltonian(n_a=N_A_TEST, n_phi=N_PHI_TEST)
    expected = N_A_TEST * N_PHI_TEST
    assert H.shape == (expected, expected)


def test_hamiltonian_symmetric():
    H = build_2d_wdw_hamiltonian(n_a=N_A_TEST, n_phi=N_PHI_TEST)
    assert np.allclose(H, H.T, atol=1e-12)


def test_hamiltonian_finite():
    H = build_2d_wdw_hamiltonian(n_a=N_A_TEST, n_phi=N_PHI_TEST)
    assert np.all(np.isfinite(H))


def test_hamiltonian_dtype():
    H = build_2d_wdw_hamiltonian(n_a=N_A_TEST, n_phi=N_PHI_TEST)
    assert np.issubdtype(H.dtype, np.floating)


# ---------- spectrum ----------

def test_spectrum_returns_dict():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    assert isinstance(result, dict)


def test_spectrum_keys():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    for key in ("eigenvalues", "lowest_psi", "grid_a", "grid_phi"):
        assert key in result


def test_spectrum_eigenvalues_finite():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    assert np.all(np.isfinite(result["eigenvalues"]))


def test_spectrum_eigenvalues_ordered():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    vals = result["eigenvalues"]
    assert np.all(np.diff(vals) >= 0)


def test_spectrum_n_eigvals():
    n_eig = 4
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=n_eig)
    assert len(result["eigenvalues"]) == n_eig


def test_spectrum_lowest_psi_shape():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    assert result["lowest_psi"].shape == (N_A_TEST, N_PHI_TEST)


def test_spectrum_grid_lengths():
    result = solve_2d_wdw_spectrum(n_a=N_A_TEST, n_phi=N_PHI_TEST, n_eigvals=4)
    assert len(result["grid_a"]) == N_A_TEST
    assert len(result["grid_phi"]) == N_PHI_TEST


# ---------- lapse saddle-point ----------

def test_lapse_saddle_returns_dict():
    result = lapse_saddle_point(a_val=1.0, v_eff=0.5, t_total=1.0)
    assert isinstance(result, dict)


def test_lapse_saddle_keys():
    result = lapse_saddle_point(a_val=1.0, v_eff=0.5, t_total=1.0)
    for key in ("N_saddle", "action", "amplitude"):
        assert key in result


def test_lapse_amplitude_positive():
    result = lapse_saddle_point(a_val=1.0, v_eff=0.5, t_total=1.0)
    assert result["amplitude"] >= 0.0


def test_lapse_amplitude_le_one():
    result = lapse_saddle_point(a_val=1.0, v_eff=0.5, t_total=1.0)
    assert result["amplitude"] <= 1.0


def test_lapse_saddle_lorentzian():
    # v_eff <= 0 → Lorentzian region; amplitude should be 0
    result = lapse_saddle_point(a_val=2.0, v_eff=-0.1, t_total=1.0)
    assert result["amplitude"] == 0.0


def test_lapse_n_saddle_positive_for_real_potential():
    result = lapse_saddle_point(a_val=1.0, v_eff=1.0, t_total=1.0)
    assert result["N_saddle"] >= 0.0


# ---------- operator ordering comparison ----------

def test_operator_ordering_comparison_returns_dict():
    result = operator_ordering_2d_comparison(n_a=8, n_phi=8)
    assert isinstance(result, dict)


def test_operator_ordering_keys():
    result = operator_ordering_2d_comparison(n_a=8, n_phi=8)
    for key in ("dewitt_eigenvalues", "flat_eigenvalues", "difference", "note"):
        assert key in result


def test_operator_ordering_eigenvalues_finite():
    result = operator_ordering_2d_comparison(n_a=8, n_phi=8)
    assert np.all(np.isfinite(result["dewitt_eigenvalues"]))
    assert np.all(np.isfinite(result["flat_eigenvalues"]))


def test_operator_ordering_difference_finite():
    result = operator_ordering_2d_comparison(n_a=8, n_phi=8)
    assert np.all(np.isfinite(result["difference"]))


# ---------- report ----------

def test_wdw_report_keys():
    report = wdw_multifield_report()
    for key in ("status", "module", "residual_unknowns", "epistemic_label"):
        assert key in report


def test_wdw_report_status():
    report = wdw_multifield_report()
    assert report["status"] == "OPEN"


def test_wdw_report_module():
    report = wdw_multifield_report()
    assert report["module"] == "wdw_multifield"


def test_wdw_report_residual_unknowns_nonempty():
    report = wdw_multifield_report()
    assert len(report["residual_unknowns"]) > 0
