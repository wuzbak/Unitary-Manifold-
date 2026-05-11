# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""
Pillar 103 — CMB E-mode polarisation Boltzmann hierarchy + reionisation bump.

NOTE: This is a toy solver for pedagogical purposes.
Sub-percent accuracy requires CAMB/CLASS with full Boltzmann hierarchy.

Cosmological constants match Planck 2018 best-fit ΛCDM.
KK modification (DELTA_KK_REF) encodes the braided-winding correction to C_ℓ.
"""

import numpy as np
from scipy.integrate import solve_ivp

# ---------- cosmological constants ----------
N_S = 0.9649          # scalar spectral index (Planck 2018)
A_S = 2.101e-9        # scalar amplitude
K_PIVOT = 0.05        # pivot scale in Mpc^-1
TAU_REIO = 0.054      # optical depth to reionisation

# ---------- KK modification ----------
DELTA_KK_REF = 8e-4  # fractional KK correction to TT power at ell=ELL_REF
ELL_REF = 100.0

# ---------- recombination parameters ----------
ETA_REC = 280.0       # conformal time at recombination (Mpc)
KAPPA_DOT_REC = -0.05  # peak opacity rate
ETA_0 = 14000.0       # conformal time today (Mpc)

# ---------- r for B-mode upper limit ----------
R_TENSOR = 0.0315     # tensor-to-scalar ratio (Unitary Manifold prediction)

# ---------- reionisation ----------
A_REIO = 4.0 * np.pi * A_S


def _kappa_dot(eta):
    """Simple Gaussian optical depth rate centred on recombination."""
    return KAPPA_DOT_REC * np.exp(-0.5 * ((eta - ETA_REC) / 20.0) ** 2)


def polarisation_boltzmann_rhs(eta, y, k, kappa_dot):
    """RHS of the truncated Boltzmann hierarchy.

    State vector y = [Θ₀, Θ₁, Θ₂, Π₀, Π₁, Π₂] (temperature + polarisation).

    Parameters
    ----------
    eta : float
        Conformal time (Mpc).
    y : array-like, length 6
        [Θ₀, Θ₁, Θ₂, Π₀, Π₁, Π₂].
    k : float
        Comoving wavenumber (Mpc^-1).
    kappa_dot : callable
        kappa_dot(eta) → opacity rate.

    Returns
    -------
    list of 6 derivatives
    """
    Theta0, Theta1, Theta2, Pi0, Pi1, Pi2 = y
    kd = kappa_dot(eta)

    dTheta0 = -k * Theta1
    dTheta1 = (k / 3.0) * (Theta0 - 2.0 * Theta2) + kd * Theta1
    # Theta3 ≈ 0 in truncated hierarchy
    dTheta2 = (2.0 * k / 5.0) * Theta1 - kd * (0.9 * Theta2 - 0.1 * Pi2)
    dPi0 = -k * Pi1 + kd * (Pi0 - 0.5 * Theta2)
    dPi1 = (k / 3.0) * (Pi0 - 2.0 * Pi2) - kd * Pi1
    dPi2 = (2.0 * k / 5.0) * Pi1 - kd * (0.9 * Pi2 - 0.1 * Theta2)

    return [dTheta0, dTheta1, dTheta2, dPi0, dPi1, dPi2]


def solve_polarisation_hierarchy(k_mpc=0.05, eta_max=800.0):
    """Integrate the polarisation Boltzmann hierarchy from η=1 to η=eta_max.

    Parameters
    ----------
    k_mpc : float
        Comoving wavenumber in Mpc^-1.
    eta_max : float
        Final conformal time in Mpc.

    Returns
    -------
    dict with keys: Theta, Pi, eta_arr
    """
    y0 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    eta_span = (1.0, eta_max)
    sol = solve_ivp(
        polarisation_boltzmann_rhs,
        eta_span,
        y0,
        args=(k_mpc, _kappa_dot),
        method="RK45",
        dense_output=False,
        rtol=1e-5,
        atol=1e-8,
        max_step=5.0,
    )
    Theta = sol.y[:3, :]  # rows 0-2
    Pi = sol.y[3:, :]     # rows 3-5
    return {"Theta": Theta, "Pi": Pi, "eta_arr": sol.t}


def _cl_tt_raw(ell_arr):
    """Raw TT power spectrum (with KK modification)."""
    k_ell = ell_arr / ETA_0
    # Avoid log(0) for ell=0
    k_safe = np.where(k_ell > 0, k_ell, K_PIVOT)
    tilt = (k_safe / K_PIVOT) ** (N_S - 1.0)
    kk_mod = 1.0 + DELTA_KK_REF * (ell_arr / ELL_REF) ** 2
    cl = A_S / (ell_arr * (ell_arr + 1.0)) * tilt * kk_mod
    return cl


def cl_ee_spectrum(ell_max=100):
    """E-mode polarisation power spectrum C_ℓ^{EE} for ℓ=2..ell_max.

    Returns
    -------
    ndarray, length (ell_max - 1)
    """
    ell = np.arange(2, ell_max + 1, dtype=float)
    cl_tt = _cl_tt_raw(ell)
    cl_ee = 0.1 * cl_tt * ell ** 2 / (ell ** 2 + 100.0)
    return cl_ee


def cl_te_spectrum(ell_max=100):
    """TE cross-spectrum C_ℓ^{TE} for ℓ=2..ell_max.

    Returns
    -------
    ndarray, length (ell_max - 1)
    """
    ell = np.arange(2, ell_max + 1, dtype=float)
    cl_tt = _cl_tt_raw(ell)
    cl_ee = 0.1 * cl_tt * ell ** 2 / (ell ** 2 + 100.0)
    cl_te = 0.3 * np.sqrt(np.abs(cl_tt * cl_ee))
    return cl_te


def cl_bb_upper_limit(ell_max=100):
    """B-mode upper limit C_ℓ^{BB} for ℓ=2..ell_max (r = 0.0315).

    Returns
    -------
    ndarray, length (ell_max - 1)
    """
    ell = np.arange(2, ell_max + 1, dtype=float)
    cl_tt = _cl_tt_raw(ell)
    cl_bb = R_TENSOR * cl_tt * 0.1
    return cl_bb


def reionisation_bump(ell_arr):
    """Reionisation bump contribution to E-mode power at low ℓ.

    C_reio(ℓ) = A_REIO × τ² × exp(−(ℓ−3)²/8) for ℓ ≤ 10, else 0.

    Parameters
    ----------
    ell_arr : array-like
        Multipole values.

    Returns
    -------
    ndarray, same length as ell_arr
    """
    ell = np.asarray(ell_arr, dtype=float)
    bump = A_REIO * TAU_REIO ** 2 * np.exp(-((ell - 3.0) ** 2) / 8.0)
    bump = np.where(ell <= 10.0, bump, 0.0)
    return bump


def cmb_polarisation_report():
    """Return a status report for Pillar 103."""
    return {
        "status": "OPEN",
        "module": "cmb_polarisation",
        "pillar": 103,
        "description": (
            "Toy CMB E-mode Boltzmann hierarchy + reionisation bump with KK correction. "
            "Sub-percent accuracy requires CAMB/CLASS."
        ),
        "residual_unknowns": [
            "Full hierarchy (>6 multipoles) needed for accurate C_ℓ.",
            "Lensing B-modes not included.",
            "Primordial gravitational waves / tensor modes approximated by r × C_ℓ^{TT}.",
            "Reionisation model is Gaussian; realistic model needs HII fraction history.",
        ],
        "epistemic_label": (
            "OPEN — toy solver; sub-percent accuracy requires CAMB/CLASS"
        ),
    }
