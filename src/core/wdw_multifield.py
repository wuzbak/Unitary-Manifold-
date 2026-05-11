# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""
Pillar 102 — 2D minisuperspace Wheeler-DeWitt equation with fields (a, φ).

DeWitt supermetric: G^{AB} = diag(−a, 1/a) in (a, φ) space.
WDW equation: [a ∂²/∂a² − (1/a) ∂²/∂φ² + 2a⁴ V_eff(a,φ)] Ψ = 0
V_eff(a,φ) = (1/2)(φ−1)² − (3/8)a²  (Goldberger-Wise radion + curvature)
"""

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import brentq

# ---------- repository constants ----------
N_W = 5
K_CS = 74
PHI0 = 1.0
PI_KR = 37.0
C_S_BRAID = 12.0 / 37.0


def _v_eff(a, phi):
    """Effective potential V_eff(a,φ) = (1/2)(φ−1)² − (3/8)a²."""
    return 0.5 * (phi - 1.0) ** 2 - (3.0 / 8.0) * a ** 2


def build_2d_wdw_hamiltonian(n_a=20, n_phi=20):
    """Build the 2D WDW Hamiltonian as a dense matrix using 2nd-order finite differences.

    Grid: a ∈ [0.1, 5], φ ∈ [0.5, 1.5].
    DeWitt ordering:  H = a ∂²/∂a² − (1/a) ∂²/∂φ² + 2a⁴ V_eff

    Returns
    -------
    H : ndarray, shape (n_a*n_phi, n_a*n_phi)
    """
    a_arr = np.linspace(0.1, 5.0, n_a)
    phi_arr = np.linspace(0.5, 1.5, n_phi)
    da = a_arr[1] - a_arr[0]
    dphi = phi_arr[1] - phi_arr[0]
    N = n_a * n_phi

    def idx(ia, iphi):
        return ia * n_phi + iphi

    H = np.zeros((N, N))

    for ia, a in enumerate(a_arr):
        for iphi, phi in enumerate(phi_arr):
            i = idx(ia, iphi)
            # DeWitt a-kinetic term: +a ∂²/∂a²
            coeff_a = a / da ** 2
            if 0 < ia < n_a - 1:
                H[i, idx(ia - 1, iphi)] += coeff_a
                H[i, i] -= 2.0 * coeff_a
                H[i, idx(ia + 1, iphi)] += coeff_a
            # DeWitt φ-kinetic term: −(1/a) ∂²/∂φ²
            coeff_phi = (1.0 / a) / dphi ** 2
            if 0 < iphi < n_phi - 1:
                H[i, idx(ia, iphi - 1)] += coeff_phi
                H[i, i] -= 2.0 * coeff_phi
                H[i, idx(ia, iphi + 1)] += coeff_phi
            # Potential term: +2a⁴ V_eff
            H[i, i] += 2.0 * a ** 4 * _v_eff(a, phi)

    # Symmetrize to enforce standard matrix symmetry (H → (H+H^T)/2).
    # Note: the DeWitt inner product in the continuum includes a measure √|det G|
    # where G is the supermetric; on the discrete grid we approximate self-adjointness
    # by explicit symmetrization.  This is an approximation adequate for the coarse
    # eigenspectrum; full self-adjointness under the weighted inner product requires
    # inclusion of the supermetric Jacobian in the finite-difference stencil.
    H = (H + H.T) / 2.0
    return H


def solve_2d_wdw_spectrum(n_a=20, n_phi=20, n_eigvals=6):
    """Solve the 2D WDW equation and return the lowest eigenvalues/eigenfunctions.

    Returns
    -------
    dict with keys: eigenvalues, lowest_psi, grid_a, grid_phi
    """
    a_arr = np.linspace(0.1, 5.0, n_a)
    phi_arr = np.linspace(0.5, 1.5, n_phi)
    H = build_2d_wdw_hamiltonian(n_a=n_a, n_phi=n_phi)
    k = min(n_eigvals, H.shape[0] - 1)
    vals, vecs = eigh(H, subset_by_index=[0, k - 1])
    lowest_psi = vecs[:, 0].reshape(n_a, n_phi)
    return {
        "eigenvalues": vals,
        "lowest_psi": lowest_psi,
        "grid_a": a_arr,
        "grid_phi": phi_arr,
    }


def lapse_saddle_point(a_val=1.0, v_eff=0.5, t_total=1.0):
    """Compute the lapse saddle-point for the Hartle-Hawking minisuperspace amplitude.

    Simple minisuperspace action for constant a:
      S[N] = T × [−ȧ²/(2N) + N × V(a)]
    Saddle: dS/dN=0 → N_saddle = ȧ / sqrt(2 V(a))

    Here we approximate ȧ ≈ a/t_total (scale of motion).

    Returns
    -------
    dict with keys: N_saddle, action, amplitude
    """
    a_dot = a_val / t_total  # characteristic velocity
    if v_eff <= 0.0:
        # Lorentzian region — no real saddle; return tunneling amplitude = 0
        n_saddle = 0.0
        action = 0.0
        amplitude = 0.0
    else:
        n_saddle = a_dot / np.sqrt(2.0 * v_eff)
        action = t_total * (-a_dot ** 2 / (2.0 * n_saddle) + n_saddle * v_eff)
        amplitude = float(np.exp(-abs(action)))
    return {"N_saddle": n_saddle, "action": action, "amplitude": amplitude}


def operator_ordering_2d_comparison(n_a=15, n_phi=15):
    """Compare DeWitt vs flat operator ordering eigenvalues.

    Flat ordering: −∂²/∂a² − ∂²/∂φ² + potential (ignores supermetric).

    Returns
    -------
    dict with keys: dewitt_eigenvalues, flat_eigenvalues, difference, note
    """
    a_arr = np.linspace(0.1, 5.0, n_a)
    phi_arr = np.linspace(0.5, 1.5, n_phi)
    da = a_arr[1] - a_arr[0]
    dphi = phi_arr[1] - phi_arr[0]
    N = n_a * n_phi

    def idx(ia, iphi):
        return ia * n_phi + iphi

    H_flat = np.zeros((N, N))
    for ia, a in enumerate(a_arr):
        for iphi, phi in enumerate(phi_arr):
            i = idx(ia, iphi)
            coeff_a = 1.0 / da ** 2
            if 0 < ia < n_a - 1:
                H_flat[i, idx(ia - 1, iphi)] -= coeff_a
                H_flat[i, i] += 2.0 * coeff_a
                H_flat[i, idx(ia + 1, iphi)] -= coeff_a
            coeff_phi = 1.0 / dphi ** 2
            if 0 < iphi < n_phi - 1:
                H_flat[i, idx(ia, iphi - 1)] -= coeff_phi
                H_flat[i, i] += 2.0 * coeff_phi
                H_flat[i, idx(ia, iphi + 1)] -= coeff_phi
            H_flat[i, i] += 2.0 * a ** 4 * _v_eff(a, phi)

    H_flat = (H_flat + H_flat.T) / 2.0
    H_dw = build_2d_wdw_hamiltonian(n_a=n_a, n_phi=n_phi)

    k = 6
    vals_dw, _ = eigh(H_dw, subset_by_index=[0, k - 1])
    vals_flat, _ = eigh(H_flat, subset_by_index=[0, k - 1])

    return {
        "dewitt_eigenvalues": vals_dw,
        "flat_eigenvalues": vals_flat,
        "difference": vals_dw - vals_flat,
        "note": (
            "DeWitt ordering uses the supermetric G^{AB}; "
            "flat ordering ignores G. Differences encode quantum gravity ambiguity."
        ),
    }


def wdw_multifield_report():
    """Return a human-readable status report for Pillar 102."""
    return {
        "status": "OPEN",
        "module": "wdw_multifield",
        "pillar": 102,
        "description": (
            "2D minisuperspace WDW equation with (a,φ) fields, "
            "DeWitt supermetric, Hartle-Hawking lapse saddle, operator ordering comparison."
        ),
        "residual_unknowns": [
            "Contour prescription for Lorentzian path integral (no-boundary vs tunneling).",
            "Operator ordering ambiguity is physical, not merely numerical.",
            "Connection to full superspace (minisuperspace is a drastic truncation).",
        ],
        "epistemic_label": "OPEN — minisuperspace truncation; full quantum gravity unknown",
    }
