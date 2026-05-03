# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dark_matter_kk.py
==========================
Pillar 106 — Dark Matter as Kaluza-Klein Graviton Modes.

In the Unitary Manifold the compact S¹/Z₂ extra dimension generates a tower
of KK graviton excitations.  The lightest mode is a natural dark-matter
candidate whose mass is set by the winding geometry.

KK mass spectrum
----------------
The lightest KK graviton mass (in eV) is

    M_KK = φ₀ × (n_w² + √k_CS) × 10⁻³

For φ₀ = 1, n_w = 5, k_CS = 74:

    M_KK = (25 + 8.602) × 10⁻³ ≈ 33.6 meV

Higher harmonics follow M_n = n × M_KK.

Relic density (hot-relic formula)
----------------------------------
    Ω_KK h² = (m_KK / 94 eV) × (g_KK / g*_s)

with g_KK = 2 (spin-2 graviton) and g*_s = 3.91 (entropy dof today).

Viability
---------
The mode is a viable DM candidate when Ω_KK h² < 0.12 (Planck 2018 bound).
"""

from __future__ import annotations

import math
from typing import List, Tuple

# ------------------------------------------------------------------
# Physical constants
# ------------------------------------------------------------------
WINDING_NUMBER: int = 5
K_CS: int = 74

_G_STAR_S: float = 3.91        # entropy dof today
_OMEGA_DM_BOUND: float = 0.12  # Planck 2018 DM upper bound on Ω h²
_HOT_RELIC_SCALE_EV: float = 94.0  # eV — standard hot-relic denominator


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def m_kk_lightest(phi0: float = 1.0,
                  n_w: int = WINDING_NUMBER,
                  k_cs: int = K_CS) -> float:
    """Return the lightest KK graviton mass in eV.

    M_KK = φ₀ × (n_w² + √k_CS) × 10⁻³  [eV]

    Parameters
    ----------
    phi0:
        Mean field amplitude (dimensionless, default 1).
    n_w:
        Winding number (default 5).
    k_cs:
        CS level (default 74).

    Returns
    -------
    float  M_KK in eV.
    """
    return phi0 * (n_w ** 2 + math.sqrt(k_cs)) * 1e-3


def kk_relic_density(m_kk_eV: float, g_kk: float = 2.0) -> float:
    """Return the KK relic density Ω_KK h² (hot-relic formula).

    Ω_KK h² = (m_KK / 94 eV) × (g_KK / g*_s)

    Parameters
    ----------
    m_kk_eV:
        KK mode mass in eV.
    g_kk:
        Internal dof of the KK mode (default 2 for spin-2 graviton).

    Returns
    -------
    float  Ω_KK h² (dimensionless).
    """
    return (m_kk_eV / _HOT_RELIC_SCALE_EV) * (g_kk / _G_STAR_S)


def kk_dark_matter_viable(m_kk_eV: float, g_kk: float = 2.0) -> bool:
    """Return True if the KK mode satisfies the Planck DM bound.

    Viable iff Ω_KK h² < 0.12.

    Parameters
    ----------
    m_kk_eV:
        KK mode mass in eV.
    g_kk:
        Internal dof (default 2).

    Returns
    -------
    bool.
    """
    return kk_relic_density(m_kk_eV, g_kk) < _OMEGA_DM_BOUND


def higher_kk_modes(n_max: int = 5,
                    phi0: float = 1.0,
                    g_kk: float = 2.0) -> List[Tuple[int, float, bool]]:
    """Return KK mass spectrum for modes n = 1 … n_max.

    Parameters
    ----------
    n_max:
        Number of harmonics to compute.
    phi0:
        Mean field amplitude (default 1).
    g_kk:
        Internal dof (default 2).

    Returns
    -------
    List of (n, m_n_eV, viable) tuples.
    """
    m1 = m_kk_lightest(phi0=phi0)
    modes = []
    for n in range(1, n_max + 1):
        m_n = n * m1
        viable = kk_dark_matter_viable(m_n, g_kk)
        modes.append((n, m_n, viable))
    return modes


def dark_matter_kk_summary(phi0: float = 1.0,
                            g_kk: float = 2.0,
                            n_max: int = 5) -> dict:
    """Return a dict summarising the KK dark-matter prediction.

    Keys
    ----
    lightest_mass_eV  : M_KK in eV
    relic_density     : Ω_KK h²
    viable            : bool (Ω < 0.12)
    n_viable_modes    : number of viable modes in n = 1…n_max
    """
    m1 = m_kk_lightest(phi0=phi0)
    omega = kk_relic_density(m1, g_kk)
    modes = higher_kk_modes(n_max=n_max, phi0=phi0, g_kk=g_kk)
    n_viable = sum(1 for _, _, v in modes if v)
    return {
        "lightest_mass_eV": m1,
        "relic_density": omega,
        "viable": omega < _OMEGA_DM_BOUND,
        "n_viable_modes": n_viable,
    }
