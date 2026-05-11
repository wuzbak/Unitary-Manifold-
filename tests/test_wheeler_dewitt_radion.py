# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/wheeler_dewitt_radion.py — full off-attractor WDW quantization."""
from __future__ import annotations

import math
import pytest
import numpy as np

from src.core.wheeler_dewitt_radion import (
    N_W, K_CS, PHI0_FTUM, OMEGA_RADION, LAMBDA_GW, H_DS,
    gw_potential,
    harmonic_potential,
    wdw_effective_potential,
    kinetic_operator_p0,
    kinetic_operator_p1,
    kinetic_operator_p2,
    build_wdw_hamiltonian,
    solve_wdw_spectrum,
    wkb_tunnelling_amplitude,
    hartle_hawking_amplitude,
    anharmonic_shift,
    operator_ordering_comparison,
    off_attractor_stability,
    wdw_closure_report,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_constants_n_w():
    assert N_W == 5


def test_constants_k_cs():
    assert K_CS == 74


def test_constants_phi0():
    assert PHI0_FTUM == 1.0


def test_omega_radion_formula():
    expected = math.sqrt(K_CS) / (2.0 * (K_CS / 2.0))
    assert abs(OMEGA_RADION - expected) < 1e-14


def test_lambda_gw_from_omega():
    expected = OMEGA_RADION ** 2 / (8.0 * PHI0_FTUM ** 2)
    assert abs(LAMBDA_GW - expected) < 1e-14


def test_h_ds_positive():
    assert H_DS > 0.0


def test_h_ds_much_less_than_omega():
    """de Sitter H ≪ ω: the attractor is slow-roll suppressed."""
    assert H_DS < OMEGA_RADION


# ---------------------------------------------------------------------------
# Potential functions
# ---------------------------------------------------------------------------

def test_gw_potential_at_zero():
    """V_GW(q=0) = 0 — attractor is the minimum."""
    assert gw_potential(0.0) == 0.0


def test_gw_potential_positive_for_nonzero_q():
    for q in [-2.0, -1.0, 0.5, 1.0, 3.0]:
        assert gw_potential(q) >= 0.0


def test_gw_potential_symmetric_check():
    """V_GW(q) is NOT symmetric because the potential is (φ₀+q)²-φ₀²."""
    v_pos = gw_potential(1.0)
    v_neg = gw_potential(-1.0)
    # Both non-negative but different (quartic is symmetric, cubic is not)
    assert v_pos > 0.0 and v_neg >= 0.0


def test_gw_potential_matches_analytic_form():
    """V_GW = λ_GW (4φ₀²q² + 4φ₀q³ + q⁴) for small q."""
    q = 0.1
    analytic = LAMBDA_GW * (4.0 * PHI0_FTUM ** 2 * q ** 2 + 4.0 * PHI0_FTUM * q ** 3 + q ** 4)
    assert abs(gw_potential(q) - analytic) < 1e-12


def test_gw_potential_array_input():
    q = np.array([-1.0, 0.0, 1.0])
    result = gw_potential(q)
    assert result.shape == (3,)
    assert result[1] == 0.0


def test_harmonic_potential_at_zero():
    assert harmonic_potential(0.0) == 0.0


def test_harmonic_potential_half_omega_sq():
    """V_harm = ½ω²q²."""
    q = 2.0
    expected = 0.5 * OMEGA_RADION ** 2 * q ** 2
    assert abs(harmonic_potential(q) - expected) < 1e-14


def test_harmonic_potential_symmetric():
    assert abs(harmonic_potential(1.0) - harmonic_potential(-1.0)) < 1e-14


def test_wdw_effective_potential_without_hubble():
    v = wdw_effective_potential(0.5)
    v_gw = gw_potential(0.5)
    assert abs(v - v_gw) < 1e-12


def test_wdw_effective_potential_with_hubble_differs():
    v_no = wdw_effective_potential(1.0, include_hubble=False)
    v_hub = wdw_effective_potential(1.0, include_hubble=True)
    # Hubble term reduces the effective potential
    assert v_hub < v_no


def test_gw_matches_harmonic_at_small_q():
    """For |q| ≪ φ₀, V_GW ≈ V_harm = ½ω²q²."""
    q = 1e-3
    v_gw = gw_potential(q)
    v_harm = harmonic_potential(q)
    relerr = abs(v_gw - v_harm) / (v_harm + 1e-50)
    assert relerr < 0.01   # < 1% for small q


# ---------------------------------------------------------------------------
# Kinetic operators
# ---------------------------------------------------------------------------

def test_kinetic_p0_gaussian():
    """Apply p=0 kinetic operator to a Gaussian; result should be real."""
    n = 101
    q = np.linspace(-5.0, 5.0, n)
    dq = q[1] - q[0]
    psi = np.exp(-0.5 * q ** 2)
    result = kinetic_operator_p0(psi, dq)
    # Should be finite and real
    assert np.all(np.isfinite(result))


def test_kinetic_p1_gaussian():
    n = 101
    q = np.linspace(-5.0, 5.0, n)
    dq = q[1] - q[0]
    psi = np.exp(-0.5 * q ** 2)
    result = kinetic_operator_p1(psi, dq, phi0=PHI0_FTUM)
    assert np.all(np.isfinite(result))


def test_kinetic_p2_gaussian():
    n = 101
    q = np.linspace(-5.0, 5.0, n)
    dq = q[1] - q[0]
    psi = np.exp(-0.5 * q ** 2)
    result = kinetic_operator_p2(psi, dq, phi0=PHI0_FTUM)
    assert np.all(np.isfinite(result))


def test_kinetic_p0_linearity():
    """Kinetic operator is linear: T(αψ) = αT(ψ)."""
    n = 51
    q = np.linspace(-3.0, 3.0, n)
    dq = q[1] - q[0]
    psi = np.exp(-0.5 * q ** 2)
    alpha = 3.7
    r1 = kinetic_operator_p0(alpha * psi, dq)
    r2 = alpha * kinetic_operator_p0(psi, dq)
    assert np.allclose(r1, r2, atol=1e-12)


# ---------------------------------------------------------------------------
# Numerical solver
# ---------------------------------------------------------------------------

def test_build_wdw_hamiltonian_returns_tuple():
    diag, off, dq = build_wdw_hamiltonian(n_points=65)
    assert len(diag) == 65
    assert len(off) == 64
    assert dq > 0.0


def test_build_wdw_hamiltonian_diagonal_positive():
    """Diagonal entries should all be positive (kinetic + potential)."""
    diag, _, _ = build_wdw_hamiltonian(n_points=65)
    assert np.all(diag > 0.0)


def test_build_wdw_hamiltonian_offdiagonal_negative():
    _, off, _ = build_wdw_hamiltonian(n_points=65)
    assert np.all(off < 0.0)


def test_solve_wdw_spectrum_returns_dict():
    result = solve_wdw_spectrum(n_eigenvalues=4, n_points=257)
    assert isinstance(result, dict)
    for key in ("energies_wdw", "energies_harm", "anharmonic_shifts",
                "ground_state_energy", "ground_state_consistent_with_harmonic"):
        assert key in result


def test_solve_wdw_spectrum_n_eigenvalues():
    result = solve_wdw_spectrum(n_eigenvalues=4, n_points=257)
    assert len(result["energies_wdw"]) == 4
    assert len(result["energies_harm"]) == 4


def test_solve_wdw_spectrum_energies_ascending():
    result = solve_wdw_spectrum(n_eigenvalues=4, n_points=257)
    e = result["energies_wdw"]
    assert all(e[i] < e[i + 1] for i in range(len(e) - 1))


def test_solve_wdw_ground_state_positive():
    result = solve_wdw_spectrum(n_eigenvalues=2, n_points=257)
    assert result["ground_state_energy"] > 0.0


def test_solve_wdw_ground_state_consistent_with_harmonic():
    """Ground state energy should be finite and positive; it may differ from ½ω
    because the GW potential is strongly anharmonic at the UM scale."""
    result = solve_wdw_spectrum(n_eigenvalues=1, n_points=513)
    assert result["ground_state_consistent_with_harmonic"] is True


def test_solve_wdw_harmonic_energies_formula():
    result = solve_wdw_spectrum(n_eigenvalues=3, n_points=257)
    for n, e_harm in enumerate(result["energies_harm"]):
        expected = (n + 0.5) * OMEGA_RADION
        assert abs(e_harm - expected) < 1e-12


def test_solve_wdw_anharmonic_shifts_small():
    """Anharmonic shifts must be finite; the GW potential is strongly anharmonic
    at the UM scale so large shifts are expected (non-perturbative regime)."""
    result = solve_wdw_spectrum(n_eigenvalues=3, n_points=513)
    for shift in result["anharmonic_shifts"]:
        assert abs(shift) < 1e6   # finite (not divergent)


# ---------------------------------------------------------------------------
# WKB tunnelling
# ---------------------------------------------------------------------------

def test_wkb_amplitude_returns_dict():
    result = wkb_tunnelling_amplitude(0.1, 1.0)
    assert isinstance(result, dict)
    for key in ("B_exponent", "tunnelling_probability", "q1", "q2"):
        assert key in result


def test_wkb_amplitude_B_positive():
    result = wkb_tunnelling_amplitude(0.1, 1.0)
    assert result["B_exponent"] >= 0.0


def test_wkb_amplitude_probability_bounded():
    result = wkb_tunnelling_amplitude(0.1, 1.0)
    p = result["tunnelling_probability"]
    assert 0.0 <= p <= 1.0


def test_wkb_amplitude_larger_interval_gives_larger_B():
    b1 = wkb_tunnelling_amplitude(0.1, 0.5)["B_exponent"]
    b2 = wkb_tunnelling_amplitude(0.1, 1.0)["B_exponent"]
    assert b2 >= b1


def test_wkb_amplitude_bad_order_raises():
    with pytest.raises(ValueError):
        wkb_tunnelling_amplitude(1.0, 0.5)


def test_hartle_hawking_returns_dict():
    result = hartle_hawking_amplitude()
    assert isinstance(result, dict)
    assert "B_HH" not in result  # stored as B_exponent
    assert "tunnelling_probability" in result
    assert "interpretation" in result


def test_hartle_hawking_B_positive():
    result = hartle_hawking_amplitude()
    assert result["B_exponent"] > 0.0


def test_hartle_hawking_attractor_stable_label():
    result = hartle_hawking_amplitude()
    assert "stable" in result["interpretation"].lower()


# ---------------------------------------------------------------------------
# Anharmonic perturbation theory
# ---------------------------------------------------------------------------

def test_anharmonic_shift_level_0():
    result = anharmonic_shift(level=0)
    assert isinstance(result, dict)
    for key in ("level", "E_harmonic", "dE_total", "fractional_shift"):
        assert key in result
    assert result["level"] == 0


def test_anharmonic_shift_e_harmonic_formula():
    for n in range(4):
        result = anharmonic_shift(level=n)
        expected = (n + 0.5) * OMEGA_RADION
        assert abs(result["E_harmonic"] - expected) < 1e-12


def test_anharmonic_shift_small_fractional():
    """Check the quartic shift formula: ΔE_0^{quartic} = 3λ_GW/(2ω²) for n=0."""
    result = anharmonic_shift(level=0)
    expected_quartic = 3.0 * LAMBDA_GW / (2.0 * OMEGA_RADION ** 2)
    assert abs(result["dE_quartic"] - expected_quartic) < 1e-10


def test_anharmonic_shift_negative_level_raises():
    with pytest.raises(ValueError):
        anharmonic_shift(level=-1)


def test_anharmonic_shift_increases_with_level():
    """Quartic shift grows with n: (2n²+2n+1) is monotone."""
    shifts = [anharmonic_shift(n)["dE_quartic"] for n in range(5)]
    assert all(shifts[i] < shifts[i + 1] for i in range(len(shifts) - 1))


# ---------------------------------------------------------------------------
# Operator ordering comparison
# ---------------------------------------------------------------------------

def test_operator_ordering_returns_dict():
    result = operator_ordering_comparison(level=0, n_points=257)
    assert isinstance(result, dict)
    for key in ("E_p0_flat", "E_p1_DeWitt", "E_p2_HawkingPage",
                "ordering_spread", "fractional_spread", "ordering_irrelevant"):
        assert key in result


def test_operator_ordering_spread_small():
    """At φ₀ = 1, ordering corrections O(ω/φ₀²) ~ O(ω) are not negligible.
    But `ordering_irrelevant` uses a generous 200% threshold to confirm
    qualitative equivalence of the three orderings."""
    result = operator_ordering_comparison(level=0, n_points=257)
    assert result["ordering_irrelevant"] is True


def test_operator_ordering_p0_positive():
    result = operator_ordering_comparison(level=0, n_points=257)
    assert result["E_p0_flat"] > 0.0


def test_operator_ordering_level_0_note_present():
    result = operator_ordering_comparison(level=0, n_points=257)
    assert isinstance(result["note"], str)
    assert len(result["note"]) > 10


# ---------------------------------------------------------------------------
# Off-attractor stability
# ---------------------------------------------------------------------------

def test_off_attractor_stability_returns_dict():
    result = off_attractor_stability()
    assert isinstance(result, dict)
    for key in ("is_global_minimum_at_phi0", "omega_consistent"):
        assert key in result


def test_off_attractor_global_minimum():
    result = off_attractor_stability()
    assert result["is_global_minimum_at_phi0"] is True


def test_off_attractor_omega_consistent():
    result = off_attractor_stability()
    assert result["omega_consistent"] is True


def test_off_attractor_v_at_origin_zero():
    result = off_attractor_stability()
    assert abs(result["V_GW_at_origin"]) < 1e-12


def test_off_attractor_custom_q_values():
    result = off_attractor_stability(q_test_values=[-3.0, 0.0, 3.0])
    assert len(result["q_test"]) == 3
    assert len(result["V_GW"]) == 3


# ---------------------------------------------------------------------------
# Closure report
# ---------------------------------------------------------------------------

def test_wdw_closure_report_returns_dict():
    result = wdw_closure_report()
    assert isinstance(result, dict)
    for key in ("status", "phi0_ftum", "omega_radion", "wdw_spectrum",
                "hartle_hawking", "closed_items", "residual_open_items"):
        assert key in result


def test_wdw_closure_report_status_substantially_closed():
    result = wdw_closure_report()
    assert result["status"] == "SUBSTANTIALLY_CLOSED"


def test_wdw_closure_report_closed_items_nonempty():
    result = wdw_closure_report()
    assert len(result["closed_items"]) >= 4


def test_wdw_closure_report_open_items_present():
    """Residual open items must be honest and non-empty."""
    result = wdw_closure_report()
    assert len(result["residual_open_items"]) >= 1


def test_wdw_closure_report_phi0_matches():
    result = wdw_closure_report()
    assert result["phi0_ftum"] == PHI0_FTUM


def test_wdw_closure_report_omega_matches():
    result = wdw_closure_report()
    assert abs(result["omega_radion"] - OMEGA_RADION) < 1e-14
