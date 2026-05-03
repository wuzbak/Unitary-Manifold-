# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/nonequilibrium_attractors.py
======================================
Pillar 110 — Non-Equilibrium Attractors of the FTUM Operator.

The FTUM (Fixed-point Topology of the Unitary Manifold) operator admits
not only fixed-point solutions but also periodic (Floquet) orbits —
the dissipative analogue of time crystals in open quantum systems.

This module characterises those periodic attractors:

* Floquet eigenvalue λ_F = exp(2πi φ₀² / (k_cs × τ))
  Norm |λ_F| = 1 — Floquet modes are marginally stable (conservative orbit).

* Time-crystal period T_tc = 2π k_cs / (n_w² φ₀²)  [Planck units]
  Natural period of the FTUM periodic attractor.

* Attractor dimension  d_a = n_w - 1 = 4
  Codimension-1 attractor in the 5D phase space.

* Lyapunov exponent  λ_L = φ₀² / k_cs × (1 - φ₀)
  Negative for φ₀ > 1 (stable), zero at φ₀ = 1 (marginal), positive for φ₀ < 1.
"""

import cmath
import math
from typing import List, Dict, Any

# ── module-level constants ─────────────────────────────────────────────────────
WINDING_NUMBER: int = 5
K_CS: int = 74


# ── public API ────────────────────────────────────────────────────────────────

def ftum_floquet_eigenvalue(period_tau: float,
                            phi0: float = 1.0,
                            k_cs: int = K_CS) -> complex:
    """Return the Floquet eigenvalue for a periodic FTUM orbit of period tau.

    λ_F = exp(2πi × φ₀² / (k_cs × τ))

    Parameters
    ----------
    period_tau : float
        Period of the orbit in Planck units.  Must be positive.
    phi0 : float
        Vacuum field value φ₀.
    k_cs : int
        Chern-Simons level (default K_CS = 74).
    """
    if period_tau <= 0:
        raise ValueError("period_tau must be positive")
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    exponent = 2.0 * math.pi * 1j * phi0**2 / (k_cs * period_tau)
    return cmath.exp(exponent)


def time_crystal_period(n_w: int = WINDING_NUMBER,
                        k_cs: int = K_CS,
                        phi0: float = 1.0) -> float:
    """Return the natural time-crystal period of the FTUM periodic attractor.

    T_tc = 2π × k_cs / (n_w² × φ₀²)   [Planck units]

    For n_w=5, k_cs=74, φ₀=1: T_tc = 2π × 74 / 25 ≈ 18.59.
    """
    if n_w <= 0:
        raise ValueError("n_w must be positive")
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    if phi0 == 0:
        raise ValueError("phi0 must be non-zero")
    return 2.0 * math.pi * k_cs / (n_w**2 * phi0**2)


def dissipative_attractor_dimension(n_w: int = WINDING_NUMBER) -> int:
    """Return the attractor dimension d_a = n_w - 1.

    The compact extra dimension defines a 5D phase space; the FTUM attractor
    lives on a codimension-1 sub-manifold of dimension n_w - 1 = 4.
    """
    if n_w < 1:
        raise ValueError("n_w must be >= 1")
    return n_w - 1


def lyapunov_exponent_periodic(phi0: float = 1.0,
                               k_cs: int = K_CS) -> float:
    """Return the Lyapunov exponent of the periodic FTUM attractor.

    λ_L = φ₀² / k_cs × (1 - φ₀)

    Sign convention
    ---------------
    φ₀ > 1 → λ_L < 0  (stable periodic attractor)
    φ₀ = 1 → λ_L = 0  (marginal, as expected at the FTUM fixed point)
    φ₀ < 1 → λ_L > 0  (repelling from below — orbits grow toward fixed point)
    """
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return phi0**2 / k_cs * (1.0 - phi0)


def attractor_zoo() -> List[Dict[str, Any]]:
    """Return a list of attractor types supported by the FTUM flow.

    Each entry is a dict with keys:
        type      : str  — human-readable attractor type
        period    : float — period in Planck units (0 = fixed point, inf = quasi-periodic)
        dimension : int  — dimension of the attractor manifold
    """
    return [
        {
            "type": "fixed_point",
            "period": 0,
            "dimension": 0,
        },
        {
            "type": "limit_cycle",
            "period": time_crystal_period(),
            "dimension": 1,
        },
        {
            "type": "quasi_periodic",
            "period": float("inf"),
            "dimension": 2,
        },
    ]


def nonequilibrium_summary() -> dict:
    """Return a summary dictionary for Pillar 110.

    Keys
    ----
    time_crystal_period  : T_tc for default parameters
    attractor_dimension  : d_a = n_w - 1 = 4
    lyapunov_at_phi0_1   : λ_L evaluated at φ₀ = 1 (should be 0)
    n_attractor_types    : number of entries in attractor_zoo()
    """
    return {
        "time_crystal_period": time_crystal_period(),
        "attractor_dimension": dissipative_attractor_dimension(),
        "lyapunov_at_phi0_1": lyapunov_exponent_periodic(phi0=1.0),
        "n_attractor_types": len(attractor_zoo()),
    }
