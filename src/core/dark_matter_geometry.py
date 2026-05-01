# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dark_matter_geometry.py
=================================
Dark Matter as the Irreversibility Field B_μ — Pillar 8.

In the Unitary Manifold "dark matter" is not an invisible particle; it is
the geometric pressure of the Irreversibility Field B_μ.  The B_μ field
contributes an effective energy density that, for a galactic-scale profile
B_r(r) ∝ 1/r, produces the isothermal-sphere dark-matter density:

    ρ_dark(r) = λ² φ_mean² |B(r)|² / 2  ∝  1/r²

This is the only dark-matter profile that gives a flat rotation curve:

    M_dark(<r) = 4π ∫₀ʳ ρ_dark r'² dr'  ∝  r   (for ρ ∝ 1/r²)
    v²_flat = G M_dark(<r) / r = 4π G ρ₀  =  const

The field thus acts as "geometric dark matter" — extra gravity sourced by
the Irreversibility Field rather than by new particles.

Theory summary
--------------
B_μ dark density (isothermal profile):
    ρ_dark(r) = ρ₀ r_s² / r²
    where ρ₀ = λ² φ_mean² B₀² / 2  and  B(r) = B₀ r_s / r

Dark mass enclosed:
    M_dark(<r) = 4π ρ₀ r_s² r

Flat curve velocity:
    v_flat = sqrt(4π G ρ₀ r_s²) = sqrt(2π G λ² φ_mean² B₀² r_s²)

B_μ field energy density (general):
    ρ_B(x) = λ² φ²(x) |B(x)|² / 2

Total rotation curve:
    v_total(r) = sqrt(G [M_baryon(<r) + M_dark(<r)] / r)

Public API
----------
b_field_dark_density(r, B0, r_scale, phi_mean, lam)
    Isothermal dark density from a B_μ ∝ 1/r profile.

b_field_energy_density(B, phi, lam)
    Local B_μ energy density ρ_B = λ²φ²|B|²/2 on the field grid.

b_field_dark_mass_enclosed(r, B0, r_scale, phi_mean, lam)
    Cumulative dark mass M_dark(<r) for a 1/r B_μ profile.

flat_curve_velocity(B0, r_scale, phi_mean, lam, G4)
    Asymptotic flat rotation speed v_flat from B_μ dark pressure.

b_field_rotation_velocity(r, M_baryonic_arr, B0, r_scale, phi_mean, lam, G4)
    Total circular velocity including B_μ dark contribution.

DarkFieldProfile
    Dataclass summarising the B_μ dark-matter prediction for a galaxy.

dark_field_profile(B0, r_scale, phi_mean, r_max, N, lam, G4, M_total, R_disk)
    Build a DarkFieldProfile for a galaxy with given parameters.
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

from dataclasses import dataclass
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_G4_DEFAULT: float = 1.0
_NUMERICAL_EPSILON: float = 1e-30
#: Minimum-radius fraction used by dark_field_profile: r_min = _MIN_RADIUS_FRACTION × r_scale.
#: Keeps r > 0 to avoid the 1/r singularity at the galactic centre.
_MIN_RADIUS_FRACTION: float = 0.05


# ---------------------------------------------------------------------------
# B_μ energy density (general, on field grid)
# ---------------------------------------------------------------------------

def b_field_energy_density(
    B: np.ndarray,
    phi: np.ndarray,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Local B_μ energy density on the field grid.

    The stress-energy tensor of the Irreversibility Field contributes an
    effective energy density:

        ρ_B(x) = λ² φ²(x) |B(x)|² / 2

    This is the "dark" energy density seen by 4D observers: real gravity is
    sourced by it, but there is no corresponding particle to detect.

    Parameters
    ----------
    B   : ndarray, shape (N, 4) — irreversibility gauge field
    phi : ndarray, shape (N,)   — entanglement-capacity scalar
    lam : float — KK coupling constant λ (default 1)

    Returns
    -------
    rho_B : ndarray, shape (N,)
        Non-negative B_μ energy density at each grid point.
    """
    B_sq = np.einsum('ni,ni->n', B, B)          # |B|²  shape (N,)
    return 0.5 * lam**2 * phi**2 * B_sq


# ---------------------------------------------------------------------------
# Galactic dark-matter model: isothermal profile from B_μ ∝ 1/r
# ---------------------------------------------------------------------------

def b_field_dark_density(
    r: np.ndarray,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Isothermal dark-matter density from a B_μ(r) = B₀ r_s / r profile.

    For B_r(r) = B₀ r_s / r (field that falls like 1/r outward from the
    galactic centre), the dark density is:

        ρ_dark(r) = λ² φ_mean² |B(r)|² / 2
                  = λ² φ_mean² B₀² r_s² / (2 r²)

    This is the isothermal-sphere profile ρ ∝ 1/r² — the only profile that
    produces a truly flat rotation curve.  The B_μ field thus geometrically
    mimics the role historically assigned to dark matter.

    Parameters
    ----------
    r        : ndarray, shape (N,) — radial grid (must be > 0)
    B0       : float — B-field amplitude at r = r_scale
    r_scale  : float — reference scale radius (Planck units)
    phi_mean : float — mean radion ⟨φ⟩ (compactification radius)
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    rho_dark : ndarray, shape (N,)  — dark density at each radius (≥ 0)
    """
    r_arr = np.asarray(r, dtype=float)
    rho0 = 0.5 * lam**2 * phi_mean**2 * B0**2 * r_scale**2
    return rho0 / (r_arr**2 + _NUMERICAL_EPSILON)


def b_field_dark_mass_enclosed(
    r: np.ndarray,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Cumulative dark mass M_dark(<r) for a B_μ ∝ 1/r profile.

    For the isothermal dark density ρ_dark ∝ 1/r²:

        M_dark(<r) = 4π ∫₀ʳ ρ_dark(r') r'² dr'
                   = 4π ρ₀ r_s² r

    The enclosed dark mass grows linearly with r — this is the mathematical
    origin of flat rotation curves.

    Parameters
    ----------
    r        : ndarray, shape (N,) — radial grid (must be > 0)
    B0       : float — B-field amplitude at r = r_scale
    r_scale  : float — reference scale radius
    phi_mean : float — mean radion ⟨φ⟩
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    M_dark : ndarray, shape (N,)  — enclosed dark mass at each radius
    """
    r_arr = np.asarray(r, dtype=float)
    rho0 = 0.5 * lam**2 * phi_mean**2 * B0**2 * r_scale**2
    return 4.0 * np.pi * rho0 * r_arr


def flat_curve_velocity(
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
    G4: float = _G4_DEFAULT,
) -> float:
    """Asymptotic flat rotation speed from B_μ dark pressure.

    For the isothermal profile M_dark(<r) = 4π ρ₀ r_s² r:

        v²_flat = G₄ M_dark(<r) / r = 4π G₄ ρ₀ r_s²
                = 2π G₄ λ² φ_mean² B₀² r_s²

    This is the universal constant that the rotation curve asymptotes to at
    large r — set entirely by the B₀, r_s, and φ_mean parameters, with no
    free dark-matter mass parameter.

    Parameters
    ----------
    B0       : float — B-field amplitude at r = r_scale
    r_scale  : float — reference scale radius
    phi_mean : float — mean radion ⟨φ⟩
    lam      : float — KK coupling λ (default 1)
    G4       : float — Newton's constant in 4D (default 1, Planck units)

    Returns
    -------
    v_flat : float — flat rotation speed (> 0)

    Raises
    ------
    ValueError
        If B0 ≤ 0, r_scale ≤ 0, or phi_mean ≤ 0.
    """
    if B0 <= 0.0:
        raise ValueError(f"B0 must be > 0, got {B0!r}")
    if r_scale <= 0.0:
        raise ValueError(f"r_scale must be > 0, got {r_scale!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    v_sq = 2.0 * np.pi * G4 * lam**2 * phi_mean**2 * B0**2 * r_scale**2
    return float(np.sqrt(max(v_sq, 0.0)))


def b_field_rotation_velocity(
    r: np.ndarray,
    M_baryonic_arr: np.ndarray,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
    G4: float = _G4_DEFAULT,
) -> np.ndarray:
    """Total circular velocity including B_μ dark contribution.

    Combines the baryonic (stars + gas) mass with the B_μ dark-matter mass
    to give the total rotation curve:

        v²_total(r) = G₄ [M_baryon(<r) + M_dark(<r)] / r

    Parameters
    ----------
    r               : ndarray, shape (N,) — radial grid
    M_baryonic_arr  : ndarray, shape (N,) — cumulative baryonic mass M(<r)
    B0              : float — B-field amplitude at r = r_scale
    r_scale         : float — reference scale radius
    phi_mean        : float — mean radion ⟨φ⟩
    lam             : float — KK coupling λ (default 1)
    G4              : float — Newton's constant (default 1)

    Returns
    -------
    v_total : ndarray, shape (N,) — total circular speed at each r
    """
    r_arr = np.asarray(r, dtype=float)
    M_dark = b_field_dark_mass_enclosed(r_arr, B0, r_scale, phi_mean, lam)
    M_total = np.asarray(M_baryonic_arr, dtype=float) + M_dark
    v_sq = G4 * M_total / (r_arr + _NUMERICAL_EPSILON)
    return np.sqrt(np.clip(v_sq, 0.0, None))


# ---------------------------------------------------------------------------
# DarkFieldProfile
# ---------------------------------------------------------------------------

@dataclass
class DarkFieldProfile:
    """Summary of the B_μ dark-matter prediction for a galaxy.

    Attributes
    ----------
    r           : ndarray — radial grid in Planck units
    rho_dark    : ndarray — dark density profile ρ_dark(r)
    M_dark      : ndarray — cumulative dark mass M_dark(<r)
    v_baryonic  : ndarray — baryonic-only rotation curve v_baryon(r)
    v_total     : ndarray — total rotation curve v_total(r) with dark field
    v_flat      : float   — asymptotic flat curve speed
    B0          : float   — B-field amplitude used
    r_scale     : float   — B-field scale radius used
    phi_mean    : float   — mean radion ⟨φ⟩
    lam         : float   — KK coupling λ
    """

    r: np.ndarray
    rho_dark: np.ndarray
    M_dark: np.ndarray
    v_baryonic: np.ndarray
    v_total: np.ndarray
    v_flat: float
    B0: float
    r_scale: float
    phi_mean: float
    lam: float


def dark_field_profile(
    B0: float,
    r_scale: float,
    phi_mean: float,
    r_max: float = 20.0,
    N: int = 200,
    lam: float = _LAM_DEFAULT,
    G4: float = _G4_DEFAULT,
    M_total: float = 1.0,
    R_disk: float = 1.0,
) -> DarkFieldProfile:
    """Build a DarkFieldProfile for a galaxy with exponential baryonic disk.

    Constructs the full rotation curve prediction by combining:

      1. A baryonic exponential-sphere mass profile M_baryon(<r).
      2. A B_μ dark-matter profile from B_r(r) = B₀ r_s / r.

    Parameters
    ----------
    B0       : float — B-field amplitude at r = r_scale
    r_scale  : float — reference scale radius
    phi_mean : float — mean radion ⟨φ⟩
    r_max    : float — maximum radius of the grid (default 20)
    N        : int   — number of grid points (default 200)
    lam      : float — KK coupling λ (default 1)
    G4       : float — Newton's constant (default 1)
    M_total  : float — total baryonic mass (default 1)
    R_disk   : float — baryonic disk scale radius (default 1)

    Returns
    -------
    DarkFieldProfile
    """
    r = np.linspace(_MIN_RADIUS_FRACTION * r_scale, r_max, N)   # avoid r = 0
    x = r / R_disk
    M_baryon = M_total * (1.0 - (1.0 + x + 0.5 * x**2) * np.exp(-x))
    v_baryon = np.sqrt(np.clip(G4 * M_baryon / (r + _NUMERICAL_EPSILON), 0.0, None))

    rho_dark = b_field_dark_density(r, B0, r_scale, phi_mean, lam)
    M_dark = b_field_dark_mass_enclosed(r, B0, r_scale, phi_mean, lam)
    v_total = b_field_rotation_velocity(r, M_baryon, B0, r_scale, phi_mean, lam, G4)
    v_flat_val = flat_curve_velocity(B0, r_scale, phi_mean, lam, G4)

    return DarkFieldProfile(
        r=r, rho_dark=rho_dark, M_dark=M_dark,
        v_baryonic=v_baryon, v_total=v_total,
        v_flat=v_flat_val,
        B0=B0, r_scale=r_scale, phi_mean=phi_mean, lam=lam,
    )
