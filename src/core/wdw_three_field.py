# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""
Pillar 109 — 3D minisuperspace Wheeler-DeWitt extension.

Extends the (a, φ) two-field truncation by adding a radion-like third degree of
freedom χ, yielding a three-field minisuperspace lane:
    (a, φ, χ)
with DeWitt-like supermetric signature:
    G^{AB} = diag(-a, 1/a, 1/a)
"""

from __future__ import annotations

from typing import Dict

import numpy as np
from scipy.linalg import eigh

N_W = 5
K_CS = 74
PI_KR = 37.0
PHI0 = 1.0
CHI0 = 1.0


def _v_eff_3d(a: float, phi: float, chi: float) -> float:
    """Three-field effective potential with radion-inflaton coupling."""
    v_phi = 0.5 * (phi - PHI0) ** 2
    v_chi = 0.5 * (chi - CHI0) ** 2
    v_coupling = 0.12 * (phi - PHI0) * (chi - CHI0)
    v_curvature = -(3.0 / 8.0) * a**2
    return v_phi + v_chi + v_coupling + v_curvature


def build_3d_wdw_hamiltonian(n_a: int = 8, n_phi: int = 8, n_chi: int = 8) -> np.ndarray:
    """Build dense 3D minisuperspace WDW Hamiltonian with 2nd-order finite differences."""
    if min(n_a, n_phi, n_chi) < 3:
        raise ValueError("n_a, n_phi, n_chi must each be >= 3.")

    a_arr = np.linspace(0.1, 5.0, n_a)
    phi_arr = np.linspace(0.5, 1.5, n_phi)
    chi_arr = np.linspace(0.5, 1.5, n_chi)
    da = a_arr[1] - a_arr[0]
    dphi = phi_arr[1] - phi_arr[0]
    dchi = chi_arr[1] - chi_arr[0]

    n_tot = n_a * n_phi * n_chi
    h = np.zeros((n_tot, n_tot), dtype=float)

    def idx(ia: int, iphi: int, ichi: int) -> int:
        return (ia * n_phi + iphi) * n_chi + ichi

    for ia, a in enumerate(a_arr):
        for iphi, phi in enumerate(phi_arr):
            for ichi, chi in enumerate(chi_arr):
                i = idx(ia, iphi, ichi)

                coeff_a = a / da**2
                if 0 < ia < n_a - 1:
                    h[i, idx(ia - 1, iphi, ichi)] += coeff_a
                    h[i, i] -= 2.0 * coeff_a
                    h[i, idx(ia + 1, iphi, ichi)] += coeff_a

                coeff_phi = (1.0 / a) / dphi**2
                if 0 < iphi < n_phi - 1:
                    h[i, idx(ia, iphi - 1, ichi)] += coeff_phi
                    h[i, i] -= 2.0 * coeff_phi
                    h[i, idx(ia, iphi + 1, ichi)] += coeff_phi

                coeff_chi = (1.0 / a) / dchi**2
                if 0 < ichi < n_chi - 1:
                    h[i, idx(ia, iphi, ichi - 1)] += coeff_chi
                    h[i, i] -= 2.0 * coeff_chi
                    h[i, idx(ia, iphi, ichi + 1)] += coeff_chi

                h[i, i] += 2.0 * a**4 * _v_eff_3d(a, phi, chi)

    return 0.5 * (h + h.T)


def solve_3d_wdw_spectrum(
    n_a: int = 8,
    n_phi: int = 8,
    n_chi: int = 8,
    n_eigvals: int = 6,
) -> Dict[str, object]:
    """Solve lowest eigenmodes of the 3D minisuperspace Hamiltonian."""
    h = build_3d_wdw_hamiltonian(n_a=n_a, n_phi=n_phi, n_chi=n_chi)
    k = min(max(n_eigvals, 1), h.shape[0] - 1)
    vals, vecs = eigh(h, subset_by_index=[0, k - 1])
    psi0 = vecs[:, 0].reshape(n_a, n_phi, n_chi)
    return {
        "eigenvalues": vals,
        "ground_state_wavefunction": psi0,
        "grid_shape": (n_a, n_phi, n_chi),
    }


def wdw_three_field_report() -> Dict[str, object]:
    """Structured status report for the 3D minisuperspace extension."""
    return {
        "pillar": 109,
        "module": "wdw_three_field",
        "status": "SUBSTANTIALLY_CLOSED",
        "description": (
            "3D minisuperspace WDW with fields (a, φ, χ), DeWitt-like supermetric, "
            "and coupled radion-inflaton potential."
        ),
        "residual_unknowns": [
            "Contour prescription for Lorentzian path integral remains open.",
            "Full non-minisuperspace 5D Wheeler-DeWitt closure remains open.",
            "Operator-ordering and measure-choice ambiguity beyond symmetric discretization remains open.",
        ],
        "epistemic_label": "SUBSTANTIALLY_CLOSED — 3-field minisuperspace extension implemented.",
    }

