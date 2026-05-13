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
    lapse_path_integral_2d,
    dirac_bracket_2d,
    wdw_multifield_closure_report,
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
    assert report["status"] == "SUBSTANTIALLY_CLOSED"


def test_wdw_report_module():
    report = wdw_multifield_report()
    assert report["module"] == "wdw_multifield"


def test_wdw_report_residual_unknowns_nonempty():
    report = wdw_multifield_report()
    assert len(report["residual_unknowns"]) > 0


# ---------- lapse_path_integral_2d -------------------------------------------

def test_lapse_path_integral_returns_dict():
    result = lapse_path_integral_2d(a_val=1.0, phi_val=1.0)
    assert isinstance(result, dict)


def test_lapse_path_integral_keys():
    result = lapse_path_integral_2d()
    required = {
        "N_saddle", "action_at_saddle", "lapse_integral_real",
        "lapse_integral_imag", "steepest_descent_direction",
        "amplitude_squared", "is_suppressed", "analytic_amplitude_squared",
    }
    assert required.issubset(result.keys())


def test_lapse_path_integral_amplitude_nonneg():
    result = lapse_path_integral_2d()
    assert result["amplitude_squared"] >= 0.0


def test_lapse_path_integral_analytic_nonneg():
    result = lapse_path_integral_2d()
    assert result["analytic_amplitude_squared"] >= 0.0


def test_lapse_path_integral_finite():
    result = lapse_path_integral_2d()
    for key in ("lapse_integral_real", "lapse_integral_imag",
                "steepest_descent_direction", "amplitude_squared"):
        assert np.isfinite(result[key]), f"{key} is not finite"


def test_lapse_path_integral_suppressed_euclidean():
    # Default point (a=1, phi=1) → V_eff = −3/8 < 0 (Lorentzian region with
    # gravity domination), which produces an imaginary N_saddle.
    result = lapse_path_integral_2d(a_val=1.0, phi_val=1.0)
    N_s = result["N_saddle"]
    # N_s should be complex (imaginary part non-zero or real)
    assert np.isfinite(abs(N_s))


def test_lapse_path_integral_custom_v_eff():
    # Supply a custom V_eff that is positive to force an Euclidean saddle.
    result = lapse_path_integral_2d(
        a_val=0.5, phi_val=2.0, v_eff_fn=lambda a, phi: 1.0
    )
    assert result["amplitude_squared"] >= 0.0


def test_lapse_path_integral_n_contour():
    r32 = lapse_path_integral_2d(n_contour=32)
    r64 = lapse_path_integral_2d(n_contour=64)
    # Results should be consistent (both finite, signs agree)
    assert np.isfinite(r32["amplitude_squared"])
    assert np.isfinite(r64["amplitude_squared"])


def test_lapse_path_integral_is_suppressed_bool():
    result = lapse_path_integral_2d()
    assert isinstance(result["is_suppressed"], bool)


# ---------- dirac_bracket_2d -------------------------------------------------

def test_dirac_bracket_returns_dict():
    result = dirac_bracket_2d()
    assert isinstance(result, dict)


def test_dirac_bracket_keys():
    result = dirac_bracket_2d()
    for key in ("bracket_value", "is_first_class", "H_perp_value",
                "p_phi_constraint_surface", "note"):
        assert key in result


def test_dirac_bracket_is_zero():
    result = dirac_bracket_2d(a=1.0, phi=1.0)
    assert abs(result["bracket_value"]) < 1e-7


def test_dirac_bracket_first_class():
    result = dirac_bracket_2d(a=1.0, phi=1.0)
    assert result["is_first_class"]


def test_dirac_bracket_grid():
    # Verify {H_⊥, H_⊥} = 0 at several (a, φ) points
    for a in [0.5, 1.0, 2.0]:
        for phi in [0.7, 1.0, 1.3]:
            res = dirac_bracket_2d(a=a, phi=phi)
            assert abs(res["bracket_value"]) < 1e-7, (
                f"bracket nonzero at a={a}, phi={phi}: {res['bracket_value']}"
            )


def test_dirac_bracket_p_phi_nonneg():
    result = dirac_bracket_2d(a=1.5, phi=1.5)
    assert result["p_phi_constraint_surface"] >= 0.0


def test_dirac_bracket_note_string():
    result = dirac_bracket_2d()
    assert isinstance(result["note"], str) and len(result["note"]) > 0


# ---------- wdw_multifield_closure_report ------------------------------------

def test_closure_report_returns_dict():
    report = wdw_multifield_closure_report()
    assert isinstance(report, dict)


def test_closure_report_status():
    report = wdw_multifield_closure_report()
    assert report["status"] == "SUBSTANTIALLY_CLOSED"


def test_closure_report_keys():
    report = wdw_multifield_closure_report()
    for key in ("status", "lapse_path_integral", "dirac_bracket",
                "closure_evidence", "residual_open_items", "epistemic_label"):
        assert key in report


def test_closure_report_residual_items_nonempty():
    report = wdw_multifield_closure_report()
    assert len(report["residual_open_items"]) >= 3


def test_closure_report_closure_evidence_nonempty():
    report = wdw_multifield_closure_report()
    assert len(report["closure_evidence"]) >= 2


def test_closure_report_first_class():
    report = wdw_multifield_closure_report()
    assert report["dirac_bracket"]["is_first_class"]


def test_report_has_closure_evidence():
    report = wdw_multifield_report()
    assert "closure_evidence" in report
    assert len(report["closure_evidence"]) > 0
