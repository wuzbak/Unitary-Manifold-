# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/dark_matter_geometry.py
=================================
Gauge-sector energy and legacy imposed halo profiles — Pillar 8.

The reduced action in ``action_derived_flow`` contains the massless gauge term
−¼ λ² φ³ F_μν F^μν, with F = dB and g_E = φ g.  Its gauge-invariant energy
density in a local orthonormal Einstein frame (signature −+++) is:

    ρ_F = λ² φ³ [Σ_i F_0i² + Σ_{i<j} F_ij²] / 2.

There is no Proca mass term in the current action.  A constant potential has
zero F and zero gauge-sector energy.  Likewise, a static radial one-form
B = B₀ r_s dr/r = d(B₀ r_s ln r) is locally pure gauge away from r = 0;
it does not supply an action-derived isothermal halo.

The existing B² APIs retain their numerical behavior for compatibility.
They impose the phenomenological density λ² φ² |B|²/2, not reduced-action
stress-energy.  Substituting B₀ r_s/r imposes an isothermal density ∝ 1/r²,
an enclosed spherical mass ∝ r, and a flat Newtonian halo rotation curve.
These functions neither solve the field equations nor demonstrate halo
formation or physical-time evolution.

Public API
----------
b_field_dark_density(r, B0, r_scale, phi_mean, lam)
    Legacy imposed isothermal halo density from a B² prescription.

b_field_energy_density(B, phi, lam)
    Legacy gauge-dependent Euclidean B² density λ²φ²|B|²/2.

b_field_strength_energy_density(F, phi, lam)
    Reduced-action gauge energy from orthonormal Einstein-frame F = dB.

b_field_dark_mass_enclosed(r, B0, r_scale, phi_mean, lam)
    Cumulative spherical mass of the imposed isothermal halo.

flat_curve_velocity(B0, r_scale, phi_mean, lam, G4)
    Flat Newtonian rotation speed of the imposed halo.

b_field_rotation_velocity(r, M_baryonic_arr, B0, r_scale, phi_mean, lam, G4)
    Spherical Newtonian circular velocity including the imposed halo.

DarkFieldProfile
    Dataclass summarising the phenomenological halo model.

dark_field_profile(B0, r_scale, phi_mean, r_max, N, lam, G4, M_total, R_disk)
    Build the imposed halo model with spherical exponential baryons.
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
# Legacy B² density and reduced-action gauge-sector energy
# ---------------------------------------------------------------------------

def b_field_energy_density(
    B: np.ndarray,
    phi: np.ndarray,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Legacy phenomenological B² density on the field grid.

        ρ_B(x) = λ² φ²(x) |B(x)|² / 2

    This Euclidean component norm is gauge dependent and is NOT the
    stress-energy of the reduced action.  It is preserved numerically for
    compatibility; use ``b_field_strength_energy_density`` for gauge energy.

    Parameters
    ----------
    B   : ndarray, shape (N, 4) — irreversibility gauge field
    phi : ndarray, shape (N,)   — entanglement-capacity scalar
    lam : float — KK coupling constant λ (default 1)

    Returns
    -------
    rho_B : ndarray, shape (N,)
        Non-negative imposed B² density at each grid point.
    """
    B_sq = np.einsum('ni,ni->n', B, B)          # |B|²  shape (N,)
    return 0.5 * lam**2 * phi**2 * B_sq


def b_field_strength_energy_density(
    F: np.ndarray,
    phi: np.ndarray,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Return the reduced-action gauge-sector energy density T_hat0hat0.

    For −¼ λ²φ³ F², an orthonormal Einstein frame with signature (−,+,+,+)
    gives ρ_F = ½ λ²φ³ (Σ_i F_0i² + Σ_{i<j} F_ij²).  This includes only
    gauge stress, not radion kinetic or potential energy, and is invariant
    under B → B + dχ.  It is not a halo-formation or evolution prescription.

    Parameters
    ----------
    F : ndarray, shape (N, 4, 4)
        Real finite antisymmetric covariant field strength in a local
        orthonormal Einstein frame.  Coordinate components must first be
        transformed to that frame; this function does not perform that step.
    phi : ndarray, shape (N,)
        Real finite positive radion.
    lam : float
        Real finite scalar KK coupling (default 1).

    Returns
    -------
    ndarray, shape (N,)
        Non-negative gauge-sector energy density.

    Notes
    -----
    Evaluation uses ordinary floating-point products, not scaled arithmetic.
    Huge finite inputs can overflow intermediate powers even when the final
    algebraic result would be finite or zero; rescale inputs in that case.

    Raises
    ------
    ValueError
        For invalid shapes, non-real or non-finite inputs, nonpositive phi,
        non-antisymmetric F (absolute tolerance 1e-12), or intermediate
        numerical overflow.
    """
    if any(np.iscomplexobj(value) for value in (F, phi, lam)):
        raise ValueError("F, phi and lam must be real.")
    F_arr = np.asarray(F, dtype=float)
    phi_arr = np.asarray(phi, dtype=float)
    lam_arr = np.asarray(lam, dtype=float)
    if F_arr.ndim != 3 or F_arr.shape[1:] != (4, 4):
        raise ValueError("F must have shape (N, 4, 4).")
    if phi_arr.shape != (F_arr.shape[0],):
        raise ValueError("phi must have shape (N,) matching F.")
    if lam_arr.ndim != 0:
        raise ValueError("lam must be a finite scalar.")
    if not all(np.all(np.isfinite(value)) for value in (F_arr, phi_arr, lam_arr)):
        raise ValueError("F, phi and lam must be finite.")
    if np.any(phi_arr <= 0.0):
        raise ValueError("phi must be > 0 everywhere.")
    if not np.allclose(F_arr, -F_arr.transpose(0, 2, 1), rtol=0.0, atol=1e-12):
        raise ValueError("F must be antisymmetric.")
    with np.errstate(over="ignore", invalid="ignore"):
        electric_sq = np.sum(F_arr[:, 0, 1:] ** 2, axis=1)
        magnetic_sq = (
            F_arr[:, 1, 2] ** 2 + F_arr[:, 1, 3] ** 2 + F_arr[:, 2, 3] ** 2
        )
        rho = 0.5 * lam_arr**2 * phi_arr**3 * (electric_sq + magnetic_sq)
    if not np.all(np.isfinite(rho)):
        raise ValueError("Gauge energy density overflowed; rescale the inputs.")
    return rho


# ---------------------------------------------------------------------------
# Legacy imposed isothermal halo: B² prescription with B amplitude ∝ 1/r
# ---------------------------------------------------------------------------

def b_field_dark_density(
    r: np.ndarray,
    B0: float,
    r_scale: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Impose the legacy isothermal halo density using B(r) = B₀ r_s / r.

    For B_r(r) = B₀ r_s / r (field that falls like 1/r outward from the
    galactic centre), the phenomenological B² prescription is:

        ρ_dark(r) = λ² φ_mean² |B(r)|² / 2
                  = λ² φ_mean² B₀² r_s² / (2 r²)

    This imposed spherical density gives a flat Newtonian halo curve.
    It is not reduced-action stress-energy: the static radial potential
    B_r ∝ 1/r has F = 0 locally away from the origin.

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
    """Cumulative spherical mass of the legacy imposed isothermal halo.

    For the isothermal dark density ρ_dark ∝ 1/r²:

        M_dark(<r) = 4π ∫₀ʳ ρ_dark(r') r'² dr'
                   = 4π ρ₀ r_s² r

    The imposed mass grows linearly with r and gives a flat Newtonian halo
    curve.  This is not a mass derived from the current gauge action.

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
    """Flat Newtonian rotation speed from the legacy imposed halo.

    For the isothermal profile M_dark(<r) = 4π ρ₀ r_s² r:

        v²_flat = G₄ M_dark(<r) / r = 4π G₄ ρ₀ r_s²
                = 2π G₄ λ² φ_mean² B₀² r_s²

    The speed is set by the phenomenological B₀, r_s, and φ_mean parameters,
    not by solving the reduced-action field equations.

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
    """Spherical Newtonian circular velocity including the imposed halo.

    Combines cumulative spherical baryonic mass with legacy imposed halo
    mass.  This is not an exact disk curve or an action-derived prediction:

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
    """Summary of the legacy phenomenological spherical halo model.

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
    """Build an imposed halo profile with spherical exponential baryons.

    Constructs a phenomenological spherical Newtonian rotation curve using:

      1. A baryonic exponential-sphere mass profile M_baryon(<r).
      2. The imposed legacy B² isothermal halo.

    Neither component is derived here from the gauge action; no halo
    formation or physical-time evolution is modeled.

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
    R_disk   : float — spherical exponential scale radius (legacy name; default 1)

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
