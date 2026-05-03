# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/proton_decay.py
========================
Pillar 107 — Proton Decay Rate from SU(5) × Orbifold Geometry.

The Unitary Manifold predicts the proton partial lifetime for the dominant
channel p → e⁺π⁰ from the SU(5) GUT scale and an orbifold-geometry
suppression factor derived from the winding number n_w = 5.

GUT scale
---------
    M_GUT = φ₀ × 2 × 10¹⁶  GeV

Orbifold suppression
--------------------
The Z₂ orbifold boundary condition on the extra dimension introduces a
geometrical suppression of the X/Y boson propagator:

    f_orb = (1 / n_w) × cos²(π / n_w)

For n_w = 5:

    f_orb = 0.2 × cos²(36°) = 0.2 × (0.809)² ≈ 0.1309

Proton decay rate
-----------------
    Γ_p = f_orb² × α_GUT² × m_p⁵ / M_GUT⁴

with α_GUT = 1/25 and m_p = 0.938 GeV.  Result in GeV (ħ = 1).

Proton lifetime
---------------
    τ_p = ħ / Γ_p

converted to years using ħ = 6.582 × 10⁻²⁵ GeV·s and 1 yr = 3.156 × 10⁷ s.

The Super-Kamiokande lower bound is τ(p → e⁺π⁰) > 1.6 × 10³⁴ yr.
"""

from __future__ import annotations

import math

# ------------------------------------------------------------------
# Physical constants
# ------------------------------------------------------------------
WINDING_NUMBER: int = 5
_ALPHA_GUT: float = 1.0 / 25.0      # GUT coupling
_M_PROTON_GEV: float = 0.938        # proton mass in GeV
_HBAR_GEV_S: float = 6.582e-25      # ħ in GeV·s
_SECONDS_PER_YEAR: float = 3.156e7  # s yr⁻¹

# Super-Kamiokande lower bound (years)
SK_BOUND_YEARS: float = 1.6e34


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def gut_scale_mass(phi0: float = 1.0) -> float:
    """Return the GUT scale in GeV.

    M_GUT = φ₀ × 2 × 10¹⁶  GeV

    Parameters
    ----------
    phi0:
        Mean field amplitude (default 1).

    Returns
    -------
    float  M_GUT in GeV.
    """
    return phi0 * 2e16


def orbifold_suppression(n_w: int = WINDING_NUMBER) -> float:
    """Return the orbifold suppression factor f_orb.

    f_orb = (1 / n_w) × cos²(π / n_w)

    Parameters
    ----------
    n_w:
        Winding number (default 5).

    Returns
    -------
    float in (0, 1).
    """
    return (1.0 / n_w) * math.cos(math.pi / n_w) ** 2


def proton_decay_rate(phi0: float = 1.0,
                      n_w: int = WINDING_NUMBER) -> float:
    """Return the proton decay rate Γ_p in GeV (natural units).

    Γ_p = f_orb² × α_GUT² × m_p⁵ / M_GUT⁴

    Parameters
    ----------
    phi0:
        Mean field amplitude (default 1).
    n_w:
        Winding number (default 5).

    Returns
    -------
    float  Γ_p in GeV.
    """
    f_orb = orbifold_suppression(n_w)
    m_gut = gut_scale_mass(phi0)
    return (f_orb ** 2) * (_ALPHA_GUT ** 2) * (_M_PROTON_GEV ** 5) / (m_gut ** 4)


def proton_lifetime_years(phi0: float = 1.0,
                           n_w: int = WINDING_NUMBER) -> float:
    """Return the proton partial lifetime in years.

    τ_p = ħ / Γ_p  [converted from GeV·s to years]

    Parameters
    ----------
    phi0:
        Mean field amplitude (default 1).
    n_w:
        Winding number (default 5).

    Returns
    -------
    float  τ_p in years.
    """
    gamma = proton_decay_rate(phi0, n_w)
    tau_s = _HBAR_GEV_S / gamma
    return tau_s / _SECONDS_PER_YEAR


def proton_decay_summary(phi0: float = 1.0,
                          n_w: int = WINDING_NUMBER) -> dict:
    """Return a dict summarising the proton decay prediction.

    Keys
    ----
    gut_scale       : M_GUT in GeV
    orbifold_factor : f_orb
    lifetime_years  : τ_p in years
    sk_bound        : 1.6e34 yr (Super-Kamiokande lower bound)
    viable          : lifetime > sk_bound
    """
    m_gut = gut_scale_mass(phi0)
    f_orb = orbifold_suppression(n_w)
    tau = proton_lifetime_years(phi0, n_w)
    return {
        "gut_scale": m_gut,
        "orbifold_factor": f_orb,
        "lifetime_years": tau,
        "sk_bound": SK_BOUND_YEARS,
        "viable": tau > SK_BOUND_YEARS,
    }
