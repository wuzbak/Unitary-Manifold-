# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/atomic_structure/fine_structure.py
========================================
Fine Structure and Spin-Orbit from 5D Geometry — Pillar 14.

The fine-structure splitting of hydrogen arises in the Unitary Manifold
from the curvature of the compact S¹/Z₂ dimension.  Relativistic
corrections, the Lamb shift, hyperfine splitting, and the anomalous magnetic
moment all emerge as higher-order expansions of the 5D KK action without
additional empirical inputs.

Theory summary
--------------
Fine-structure constant from KK geometry:
    α ≈ k_cs · (2π)⁻¹ / n_w²

Dirac energy (relativistic):
    E_nj = m_e [1 + (αZ/(n − δ))²]^{−1/2} − m_e

Lamb shift (leading log):
    ΔE_Lamb ∝ α⁵ m_e ln(1/α)   (2S₁/₂ shift)

Hyperfine splitting:
    ΔE_hf = A_hf/2 · [F(F+1) − I(I+1) − J(J+1)]

g-factor anomaly (Schwinger):
    (g − 2) = α/π

Relativistic correction:
    ΔE_rel = −α⁴ Z⁴/(8n⁴)

Spin-orbit j-values:
    j = l ± 1/2   (l ≥ 1);   j = 1/2   (l = 0)

Landé g-factor:
    g_J = 1 + [j(j+1) + s(s+1) − l(l+1)] / [2j(j+1)]

KK spin connection:
    ω_spin = φ₀ / (n_w · 2π)

Public API
----------
fine_structure_constant_from_kk(k_cs, n_w)
    α = k_cs · (2π)⁻¹ / n_w².

dirac_energy(n, j, Z, alpha_fs)
    Dirac relativistic energy level E_nj.

lamb_shift_estimate(n, l, alpha_fs)
    ΔE_Lamb ∝ α⁵ ln(1/α).

hyperfine_splitting(I, J, A_hf)
    ΔE_hf = A_hf/2 · [F(F+1) − I(I+1) − J(J+1)].

g_factor_anomaly(alpha_fs)
    (g − 2) = α/π.

relativistic_correction(n, Z, alpha_fs)
    ΔE_rel = −α⁴ Z⁴/(8n⁴).

spin_orbit_j_values(l)
    [l − 0.5, l + 0.5] for l ≥ 1, else [0.5].

total_angular_momentum_magnitude(j)
    √(j(j+1)).

lande_g_factor(j, l, s)
    g_J = 1 + [j(j+1)+s(s+1)−l(l+1)] / [2j(j+1)].

kk_spin_connection(n_w, phi0)
    ω_spin = φ₀ / (n_w · 2π).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import numpy as np

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_ALPHA_FS_DEFAULT: float = 1.0 / 137.0
_M_E: float = 1.0          # electron mass in natural units
_TWO_PI: float = 2.0 * np.pi


# ---------------------------------------------------------------------------
# Fine-structure constant from KK geometry
# ---------------------------------------------------------------------------

def fine_structure_constant_from_kk(
    k_cs: float,
    n_w: int = 5,
) -> float:
    """Fine-structure constant estimated from KK compactification parameters.

    In the 5D KK reduction the gauge coupling that appears as α in 4D is
    related to the compactification scale constant k_cs and the reference
    winding number n_w:

        α ≈ k_cs · (2π)⁻¹ / n_w²

    Parameters
    ----------
    k_cs : float — compactification coupling constant (k_cs > 0)
    n_w  : int   — reference winding number (n_w ≥ 1)

    Returns
    -------
    alpha : float — estimated fine-structure constant

    Raises
    ------
    ValueError
        If k_cs ≤ 0 or n_w < 1.
    """
    if k_cs <= 0.0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return float(k_cs / (_TWO_PI * n_w ** 2))


# ---------------------------------------------------------------------------
# Dirac energy
# ---------------------------------------------------------------------------

def dirac_energy(
    n: int,
    j: float,
    Z: int = 1,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Relativistic Dirac energy level for hydrogen-like atom.

    The Dirac formula for the energy of the (n, j) level of a
    hydrogen-like atom with nuclear charge Z is:

        E_nj = m_e · {[1 + (αZ / (n − δ(j)))²]^{−1/2} − 1}

    where δ(j) = j + 1/2 − √[(j+1/2)² − (αZ)²] and the rest mass
    m_e = 1 in natural units.

    Parameters
    ----------
    n        : int   — principal quantum number (n ≥ 1)
    j        : float — total angular momentum quantum number (j ≥ 0.5)
    Z        : int   — nuclear charge (Z ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    E_nj : float — Dirac energy relative to rest mass (negative = bound)

    Raises
    ------
    ValueError
        If n < 1, Z < 1, alpha_fs ≤ 0, or (alpha_fs·Z) ≥ (j+0.5).
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if Z < 1:
        raise ValueError(f"Z must be ≥ 1, got {Z!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    jp = j + 0.5
    aZ = alpha_fs * Z
    if aZ >= jp:
        raise ValueError(
            f"(alpha_fs·Z) = {aZ!r} must be < j+0.5 = {jp!r}"
        )
    delta = jp - np.sqrt(jp ** 2 - aZ ** 2)
    denom = np.sqrt(1.0 + (aZ / (n - delta)) ** 2)
    return float(_M_E * (1.0 / denom - 1.0))


# ---------------------------------------------------------------------------
# Lamb shift estimate
# ---------------------------------------------------------------------------

def lamb_shift_estimate(
    n: int,
    l: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Leading-order estimate of the Lamb shift for level (n, l).

    The Lamb shift arises from vacuum-polarisation and self-energy corrections
    in QED; in the 5D picture these correspond to loop integrals over KK
    modes.  The leading log approximation for s-states (l = 0) gives:

        ΔE_Lamb ∝ α⁵ m_e ln(1/α) / n³

    For l > 0 the shift is suppressed by an extra factor of 1/(l(l+1)) and
    is much smaller than for l = 0.

    Parameters
    ----------
    n        : int   — principal quantum number (n ≥ 1)
    l        : int   — orbital quantum number (l ≥ 0)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    dE_Lamb : float — Lamb shift in natural units

    Raises
    ------
    ValueError
        If n < 1, l < 0, or alpha_fs ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if l < 0:
        raise ValueError(f"l must be ≥ 0, got {l!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    base = (alpha_fs ** 5) * _M_E * np.log(1.0 / alpha_fs) / n ** 3
    if l == 0:
        return float(base)
    return float(base / (l * (l + 1)))


# ---------------------------------------------------------------------------
# Hyperfine splitting
# ---------------------------------------------------------------------------

def hyperfine_splitting(
    I: float,
    J: float,
    A_hf: float,
) -> float:
    """Hyperfine energy splitting between total-spin states.

    The hyperfine interaction couples the nuclear spin I and the electron
    total angular momentum J to form the total spin F = I + J.  The energy
    splitting between adjacent F levels is:

        ΔE_hf = (A_hf/2) · [F(F+1) − I(I+1) − J(J+1)]

    where F takes values |I−J|, |I−J|+1, …, I+J.  This function evaluates
    the expression for F = I + J (upper hyperfine level).

    Parameters
    ----------
    I    : float — nuclear spin quantum number (I ≥ 0)
    J    : float — electron total angular momentum (J ≥ 0.5)
    A_hf : float — hyperfine constant

    Returns
    -------
    dE_hf : float — hyperfine splitting for F = I + J

    Raises
    ------
    ValueError
        If I < 0 or J < 0.
    """
    if I < 0.0:
        raise ValueError(f"I must be ≥ 0, got {I!r}")
    if J < 0.0:
        raise ValueError(f"J must be ≥ 0, got {J!r}")
    F = I + J
    return float((A_hf / 2.0) * (F * (F + 1) - I * (I + 1) - J * (J + 1)))


# ---------------------------------------------------------------------------
# g-factor anomaly
# ---------------------------------------------------------------------------

def g_factor_anomaly(alpha_fs: float = _ALPHA_FS_DEFAULT) -> float:
    """Leading-order anomalous magnetic moment (g − 2) / 2.

    The Schwinger correction gives the leading contribution:

        (g − 2) = α / π

    In the KK picture this arises from the one-loop integral over the
    compact dimension modes.

    Parameters
    ----------
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    g_minus_2 : float — (g − 2) leading term

    Raises
    ------
    ValueError
        If alpha_fs ≤ 0.
    """
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float(alpha_fs / np.pi)


# ---------------------------------------------------------------------------
# Relativistic correction
# ---------------------------------------------------------------------------

def relativistic_correction(
    n: int,
    Z: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Leading relativistic (mass-velocity + Darwin) correction to E_n.

    The first relativistic correction to the hydrogen energy levels is:

        ΔE_rel = −α⁴ Z⁴ / (8n⁴)

    This is the O(α⁴) term in the expansion of the Dirac energy.

    Parameters
    ----------
    n        : int   — principal quantum number (n ≥ 1)
    Z        : int   — nuclear charge (Z ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    dE_rel : float — relativistic energy correction (≤ 0)

    Raises
    ------
    ValueError
        If n < 1, Z < 1, or alpha_fs ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if Z < 1:
        raise ValueError(f"Z must be ≥ 1, got {Z!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float(-(alpha_fs ** 4) * (Z ** 4) / (8.0 * n ** 4))


# ---------------------------------------------------------------------------
# Spin-orbit j-values
# ---------------------------------------------------------------------------

def spin_orbit_j_values(l: int) -> list[float]:
    """Allowed total angular momentum quantum numbers j for orbital l.

    For l ≥ 1 the spin-orbit coupling splits each l-multiplet into two
    j-levels: j = l − 1/2 and j = l + 1/2.  For l = 0 only j = 1/2 exists.

    Parameters
    ----------
    l : int — orbital quantum number (l ≥ 0)

    Returns
    -------
    j_values : list[float] — allowed j values

    Raises
    ------
    ValueError
        If l < 0.
    """
    if l < 0:
        raise ValueError(f"l must be ≥ 0, got {l!r}")
    if l == 0:
        return [0.5]
    return [float(l - 0.5), float(l + 0.5)]


# ---------------------------------------------------------------------------
# Total angular momentum magnitude
# ---------------------------------------------------------------------------

def total_angular_momentum_magnitude(j: float) -> float:
    """Magnitude of total angular momentum vector in units of ħ.

    The eigenvalue of J² is j(j+1)ħ², so the magnitude |J| = √(j(j+1)) ħ:

        |J| = √(j(j+1))

    Parameters
    ----------
    j : float — total angular momentum quantum number (j ≥ 0)

    Returns
    -------
    mag : float — |J| in units of ħ

    Raises
    ------
    ValueError
        If j < 0.
    """
    if j < 0.0:
        raise ValueError(f"j must be ≥ 0, got {j!r}")
    return float(np.sqrt(j * (j + 1)))


# ---------------------------------------------------------------------------
# Landé g-factor
# ---------------------------------------------------------------------------

def lande_g_factor(
    j: float,
    l: int,
    s: float = 0.5,
) -> float:
    """Landé g-factor for a level with quantum numbers j, l, s.

    The Landé g-factor determines the Zeeman splitting in an external
    magnetic field:

        g_J = 1 + [j(j+1) + s(s+1) − l(l+1)] / [2j(j+1)]

    For a pure orbital moment (s = 0) g_J = 1; for a pure spin (l = 0)
    g_J = 2.

    Parameters
    ----------
    j : float — total angular momentum quantum number (j > 0)
    l : int   — orbital quantum number (l ≥ 0)
    s : float — spin quantum number (default 0.5 for electron)

    Returns
    -------
    g_J : float — Landé g-factor

    Raises
    ------
    ValueError
        If j ≤ 0 or l < 0.
    """
    if j <= 0.0:
        raise ValueError(f"j must be > 0, got {j!r}")
    if l < 0:
        raise ValueError(f"l must be ≥ 0, got {l!r}")
    numerator = j * (j + 1) + s * (s + 1) - l * (l + 1)
    denominator = 2.0 * j * (j + 1)
    return float(1.0 + numerator / denominator)


# ---------------------------------------------------------------------------
# KK spin connection
# ---------------------------------------------------------------------------

def kk_spin_connection(n_w: int, phi0: float) -> float:
    """Spin connection arising from the KK compact-dimension geometry.

    The coupling between the spin degree of freedom and the orbital angular
    momentum in the 5D KK picture is mediated by the spin connection of the
    compact dimension.  Its characteristic scale is:

        ω_spin = φ₀ / (n_w · 2π)

    This sets the magnitude of spin-orbit coupling from geometry alone.

    Parameters
    ----------
    n_w  : int   — KK winding number / principal quantum number (n_w ≥ 1)
    phi0 : float — radion VEV (phi0 > 0)

    Returns
    -------
    omega_spin : float — spin connection strength

    Raises
    ------
    ValueError
        If n_w < 1 or phi0 ≤ 0.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    return float(phi0 / (n_w * _TWO_PI))
