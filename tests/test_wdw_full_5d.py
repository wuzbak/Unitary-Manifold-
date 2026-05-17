# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 102-C — Full 5D Wheeler-DeWitt: Perturbative Closure."""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.wdw_full_5d import (
    N_W,
    K_CS,
    PHI0,
    C_S_BRAID,
    PI_KR,
    _ODD_KK_LEVELS,
    kk_mode_dispersion,
    bunch_davies_wavefunction,
    bunch_davies_variance,
    mode_wdw_residual_check,
    kk_vacuum_energy_zeta_reg,
    kk_correction_to_spectrum,
    tensor_power_spectrum,
    scalar_power_spectrum,
    tensor_to_scalar_ratio,
    ordering_laplace_beltrami_uniqueness,
    factorization_consistency_check,
    wdw_full_5d_closure_report,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_phi0():
    assert PHI0 == 1.0


def test_c_s_braid():
    assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-12


def test_pi_kr():
    assert PI_KR == 37.0


def test_odd_kk_levels_all_odd():
    for n in _ODD_KK_LEVELS:
        assert n % 2 == 1, f"KK level {n} is not odd"


def test_odd_kk_levels_nonempty():
    assert len(_ODD_KK_LEVELS) > 0


# ---------------------------------------------------------------------------
# KK dispersion relation
# ---------------------------------------------------------------------------

def test_dispersion_massless_n0():
    # n=0: ω² = k²/a²
    omega2 = kk_mode_dispersion(k=1.0, n_kk=0, a=2.0)
    assert abs(omega2 - (1.0 / 2.0) ** 2) < 1e-12


def test_dispersion_kk1_at_attractor():
    # n=1, φ=φ₀=1: ω² = k²/a² + 1
    omega2 = kk_mode_dispersion(k=1.0, n_kk=1, a=1.0, phi=1.0, phi0=1.0)
    assert abs(omega2 - 2.0) < 1e-12


def test_dispersion_always_nonnegative():
    for k in [0.1, 1.0, 5.0]:
        for n in [0, 1, 3]:
            for a in [0.5, 1.0, 3.0]:
                assert kk_mode_dispersion(k, n, a) >= 0.0


def test_dispersion_increases_with_kk_level():
    k, a = 1.0, 1.0
    omega2_n1 = kk_mode_dispersion(k, 1, a)
    omega2_n3 = kk_mode_dispersion(k, 3, a)
    assert omega2_n3 > omega2_n1


def test_dispersion_scale_factor_dependence():
    # Larger a → smaller 4D gradient term k²/a²; KK mass term unchanged
    k, n = 1.0, 1
    omega2_small_a = kk_mode_dispersion(k, n, a=0.5)
    omega2_large_a = kk_mode_dispersion(k, n, a=5.0)
    assert omega2_small_a > omega2_large_a


def test_dispersion_phi_dependence():
    # Larger φ → smaller KK mass m_n = n·φ₀/φ
    k, n, a = 1.0, 1, 1.0
    omega2_phi1 = kk_mode_dispersion(k, n, a, phi=1.0)
    omega2_phi2 = kk_mode_dispersion(k, n, a, phi=2.0)
    assert omega2_phi2 < omega2_phi1


# ---------------------------------------------------------------------------
# Bunch-Davies wave function
# ---------------------------------------------------------------------------

def test_bd_wavefunction_positive_at_origin():
    psi = bunch_davies_wavefunction(0.0, k=1.0, n_kk=1, a=1.0)
    assert psi > 0.0


def test_bd_wavefunction_decays():
    psi0 = bunch_davies_wavefunction(0.0, k=1.0, n_kk=1, a=1.0)
    psi1 = bunch_davies_wavefunction(2.0, k=1.0, n_kk=1, a=1.0)
    assert psi1 < psi0


def test_bd_wavefunction_symmetric():
    k, n, a = 1.0, 1, 1.0
    psi_pos = bunch_davies_wavefunction(+1.0, k, n, a)
    psi_neg = bunch_davies_wavefunction(-1.0, k, n, a)
    assert abs(psi_pos - psi_neg) < 1e-12


def test_bd_wavefunction_normalisation():
    """∫ ψ²(q) dq ≈ 1 (numerical quadrature)."""
    k, n_kk, a = 1.0, 1, 1.0
    omega = math.sqrt(kk_mode_dispersion(k, n_kk, a))
    sigma = 1.0 / math.sqrt(omega)
    q_arr = np.linspace(-6 * sigma, 6 * sigma, 2000)
    dq = q_arr[1] - q_arr[0]
    psi_arr = np.array([bunch_davies_wavefunction(q, k, n_kk, a) for q in q_arr])
    norm = np.sum(psi_arr ** 2) * dq
    assert abs(norm - 1.0) < 0.01


def test_bd_variance_positive():
    var = bunch_davies_variance(k=1.0, n_kk=1, a=1.0)
    assert var > 0.0


def test_bd_variance_formula():
    """⟨q²⟩ = 1/(2ω)."""
    k, n_kk, a = 1.0, 1, 1.0
    omega = math.sqrt(kk_mode_dispersion(k, n_kk, a))
    expected = 1.0 / (2.0 * omega)
    assert abs(bunch_davies_variance(k, n_kk, a) - expected) < 1e-12


def test_bd_variance_decreases_with_frequency():
    # Higher frequency → smaller variance (tighter wavepacket)
    var_k1 = bunch_davies_variance(k=1.0, n_kk=1, a=1.0)
    var_k5 = bunch_davies_variance(k=5.0, n_kk=1, a=1.0)
    assert var_k5 < var_k1


# ---------------------------------------------------------------------------
# Mode WDW residual check
# ---------------------------------------------------------------------------

def test_mode_wdw_residual_dict_keys():
    result = mode_wdw_residual_check(k=1.0, n_kk=1, a=1.0)
    for key in ("omega", "max_residual", "is_satisfied", "note"):
        assert key in result


def test_mode_wdw_residual_satisfied_n1():
    result = mode_wdw_residual_check(k=1.0, n_kk=1, a=1.0)
    assert result["is_satisfied"], (
        f"BD vacuum residual {result['max_residual']:.3e} exceeds 1% for mode (k=1, n=1, a=1)"
    )


def test_mode_wdw_residual_satisfied_massless():
    result = mode_wdw_residual_check(k=2.0, n_kk=0, a=1.0)
    assert result["is_satisfied"]


def test_mode_wdw_residual_satisfied_n3():
    result = mode_wdw_residual_check(k=0.5, n_kk=3, a=1.0)
    assert result["is_satisfied"]


def test_mode_wdw_omega_matches_dispersion():
    k, n, a = 1.0, 1, 1.0
    result = mode_wdw_residual_check(k=k, n_kk=n, a=a)
    expected_omega = math.sqrt(kk_mode_dispersion(k, n, a))
    assert abs(result["omega"] - expected_omega) < 1e-10


# ---------------------------------------------------------------------------
# Vacuum energy
# ---------------------------------------------------------------------------

def test_vacuum_energy_dict_keys():
    result = kk_vacuum_energy_zeta_reg(a=1.0)
    for key in ("raw_sum", "subtracted_sum", "kk_effective_lambda", "is_planck_suppressed"):
        assert key in result


def test_vacuum_energy_raw_positive():
    result = kk_vacuum_energy_zeta_reg(a=1.0)
    assert result["raw_sum"] > 0.0


def test_vacuum_energy_planck_suppressed():
    result = kk_vacuum_energy_zeta_reg(a=1.0)
    assert result["is_planck_suppressed"]


def test_vacuum_energy_finite():
    result = kk_vacuum_energy_zeta_reg(a=1.0)
    assert math.isfinite(result["raw_sum"])
    assert math.isfinite(result["kk_effective_lambda"])


# ---------------------------------------------------------------------------
# KK correction to spectrum
# ---------------------------------------------------------------------------

def test_kk_correction_nonnegative():
    delta = kk_correction_to_spectrum(k=0.1, H_dS=1e-5)
    assert delta >= 0.0


def test_kk_correction_exponentially_small_for_um_params():
    # For UM: m_1 = 1, H_dS ~ 1e-5 → exp(-2π/1e-5) ~ 0
    delta = kk_correction_to_spectrum(k=0.05, H_dS=1e-5)
    assert delta < 1e-100  # utterly negligible


def test_kk_correction_increases_with_H():
    # Larger H_dS → smaller Boltzmann suppression → larger correction
    delta_small_H = kk_correction_to_spectrum(k=1.0, H_dS=0.01)
    delta_large_H = kk_correction_to_spectrum(k=1.0, H_dS=0.5)
    assert delta_large_H >= delta_small_H


# ---------------------------------------------------------------------------
# Tensor power spectrum
# ---------------------------------------------------------------------------

def test_tensor_spectrum_dict_keys():
    result = tensor_power_spectrum([0.05, 0.1], H_dS=1e-5)
    for key in ("k_values", "P_T", "delta_KK", "P_T_massless", "n_T"):
        assert key in result


def test_tensor_spectrum_positive():
    result = tensor_power_spectrum([0.05, 0.1, 0.5], H_dS=1e-5)
    assert np.all(result["P_T"] > 0)


def test_tensor_spectrum_formula():
    # P_T(k) = (2/π²) H² (massless part)
    H = 1e-5
    result = tensor_power_spectrum([0.1], H_dS=H)
    expected = 2.0 / math.pi ** 2 * H ** 2
    assert abs(result["P_T_massless"] - expected) < 1e-20


def test_tensor_spectrum_shape():
    k_arr = [0.01, 0.05, 0.1, 0.5]
    result = tensor_power_spectrum(k_arr, H_dS=1e-5)
    assert len(result["P_T"]) == len(k_arr)


# ---------------------------------------------------------------------------
# Scalar power spectrum
# ---------------------------------------------------------------------------

def test_scalar_spectrum_dict_keys():
    result = scalar_power_spectrum([0.05, 0.1], H_dS=1e-5, epsilon_sr=0.006)
    for key in ("k_values", "P_zeta", "delta_KK", "P_zeta_0", "r_check"):
        assert key in result


def test_scalar_spectrum_positive():
    result = scalar_power_spectrum([0.05, 0.1], H_dS=1e-5, epsilon_sr=0.006)
    assert np.all(result["P_zeta"] > 0)


def test_scalar_spectrum_formula():
    # P_ζ = H² / (8π² ε c_s)
    H, eps, cs = 1e-5, 0.006, 12.0 / 37.0
    result = scalar_power_spectrum([0.1], H_dS=H, epsilon_sr=eps, cs=cs)
    expected = H ** 2 / (8.0 * math.pi ** 2 * eps * cs)
    assert abs(result["P_zeta_0"] - expected) / expected < 1e-10


# ---------------------------------------------------------------------------
# Tensor-to-scalar ratio
# ---------------------------------------------------------------------------

def test_r_consistency_with_braided_prediction():
    """r = P_T / P_ζ ≈ 16ε c_s; with ε=0.006, c_s=12/37: r ≈ 0.0315."""
    r = tensor_to_scalar_ratio(H_dS=1e-5, epsilon_sr=0.006)
    # Allow generous tolerance — this is a consistency check, not a derivation
    assert 0.01 < r < 0.10


def test_r_positive():
    r = tensor_to_scalar_ratio(H_dS=1e-5, epsilon_sr=0.006)
    assert r > 0.0


def test_r_increases_with_epsilon():
    r_small = tensor_to_scalar_ratio(H_dS=1e-5, epsilon_sr=0.001)
    r_large = tensor_to_scalar_ratio(H_dS=1e-5, epsilon_sr=0.01)
    assert r_large > r_small


# ---------------------------------------------------------------------------
# Operator ordering — Laplace-Beltrami uniqueness
# ---------------------------------------------------------------------------

def test_lb_ordering_dict_keys():
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8, n_eigvals=3)
    for key in ("lb_eigenvalues", "flat_eigenvalues", "difference",
                "sqrt_det_G", "connection_term", "lb_is_unique"):
        assert key in result


def test_sqrt_det_G_is_one():
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8)
    assert abs(result["sqrt_det_G"] - 1.0) < 1e-12


def test_connection_term_value():
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8)
    assert abs(result["connection_term"] - (-0.5)) < 1e-12


def test_lb_is_unique():
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8)
    assert result["lb_is_unique"] is True


def test_lb_and_flat_eigenvalues_differ():
    """LB adds first-derivative term → different eigenvalues than flat."""
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8, n_eigvals=3)
    # The two orderings must give different spectra (confirming LB is distinct)
    diff = result["difference"]
    assert np.any(np.abs(diff) > 1e-8)


def test_lb_eigenvalues_finite():
    result = ordering_laplace_beltrami_uniqueness(n_a=8, n_phi=8, n_eigvals=3)
    assert np.all(np.isfinite(result["lb_eigenvalues"]))
    assert np.all(np.isfinite(result["flat_eigenvalues"]))


# ---------------------------------------------------------------------------
# Factorisation consistency
# ---------------------------------------------------------------------------

def test_factorisation_dict_keys():
    result = factorization_consistency_check(n_a=8, n_phi=8, n_modes=2)
    for key in ("mode_zero_point_energies", "consistency_check",
                "background_lowest_eigen", "factorisation_consistent"):
        assert key in result


def test_factorisation_consistent():
    result = factorization_consistency_check(n_a=8, n_phi=8, n_modes=2)
    assert result["factorisation_consistent"] is True


def test_factorisation_zpe_positive():
    result = factorization_consistency_check(n_a=8, n_phi=8, n_modes=2)
    for zpe in result["mode_zero_point_energies"]:
        assert zpe > 0.0


def test_factorisation_background_eigen_finite():
    result = factorization_consistency_check(n_a=8, n_phi=8, n_modes=2)
    assert math.isfinite(result["background_lowest_eigen"])


# ---------------------------------------------------------------------------
# Closure report
# ---------------------------------------------------------------------------

def test_closure_report_status():
    report = wdw_full_5d_closure_report()
    assert report["status"] == "CLOSED"


def test_closure_report_pillar():
    report = wdw_full_5d_closure_report()
    assert report["pillar"] == "102-C"


def test_closure_report_keys():
    report = wdw_full_5d_closure_report()
    for key in ("status", "pillar", "closure_evidence", "closed_items",
                "residual_open_items", "epistemic_label"):
        assert key in report


def test_closure_report_evidence_nonempty():
    report = wdw_full_5d_closure_report()
    assert len(report["closure_evidence"]) >= 5


def test_closure_report_closed_items():
    report = wdw_full_5d_closure_report()
    assert len(report["closed_items"]) >= 4


def test_closure_report_residual_honest():
    """Report must still acknowledge non-perturbative and UV residuals."""
    report = wdw_full_5d_closure_report()
    text = " ".join(report["residual_open_items"]).lower()
    assert "non-perturbative" in text or "uv" in text.lower()


def test_closure_report_epistemic_label_contains_closed():
    report = wdw_full_5d_closure_report()
    assert "CLOSED" in report["epistemic_label"]
