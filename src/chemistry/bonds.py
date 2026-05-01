# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/chemistry/bonds.py
======================
Chemistry → Bonds as φ-minima — Pillar 9.

In the Unitary Manifold, chemical bonding is not a separate force layered on
top of quantum mechanics; it is a projection of the 5D entanglement-capacity
scalar φ onto 4D chemistry.  A chemical bond forms wherever φ(r) reaches a
local minimum at a characteristic separation r₀ — the bond length.  The
depth of that minimum determines the bond energy; the width determines the
vibrational frequency.

Theory summary
--------------
Bond potential (Gaussian-well approximation):
    φ(r) = φ_∞ - (φ_∞ - φ_min) · exp(−a²(r − r₀)²)

Bond energy (φ-well depth):
    E_bond = φ_∞ - φ_min

Geometric bond length from KK compactification:
    r₀ = 2π φ_mean / (λ n_w)

Chemical potential (gradient of scalar at equilibrium):
    μ_chem(x) = −∂φ/∂r

Bond order from winding-number ratio:
    b_order = n_w_bond / n_w_ref

Dissociation criterion:
    bond intact  iff  |B_μ| < B_dissociation

Shell capacity from winding quantization:
    C(n) = 2 n²

Public API
----------
phi_bond_well(r, r0, phi_inf, phi_min, a)
    Gaussian-well approximation to the φ-bond potential.

bond_energy(phi_inf, phi_min)
    Depth of the φ-well, E_bond = φ_∞ − φ_min.

bond_length_from_winding(n_w, phi_mean, lam)
    Geometric bond length r₀ = 2π φ_mean / (λ n_w).

chemical_potential(r, phi, dx)
    μ_chem(x) = −∂φ/∂r via np.gradient.

bond_order(n_w_bond, n_w_ref)
    b_order = n_w_bond / n_w_ref.

is_bond_stable(B_strength, B_dissociation)
    True where |B_μ| < B_dissociation.

shell_capacity(n_shell)
    2 n² electron capacity for shell n.
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

_LAM_DEFAULT: float = 1.0
_N_W_REF_DEFAULT: int = 5
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# φ-bond well
# ---------------------------------------------------------------------------

def phi_bond_well(
    r: np.ndarray,
    r0: float,
    phi_inf: float,
    phi_min: float,
    a: float,
) -> np.ndarray:
    """Gaussian-well approximation to the φ-bond potential.

    The entanglement-capacity scalar develops a local minimum at the bond
    length r₀.  Near the minimum the profile is well approximated by a
    Gaussian well:

        φ(r) = φ_∞ − (φ_∞ − φ_min) · exp(−a²(r − r₀)²)

    At r = r₀ the well reaches its minimum φ_min; far from the bond
    (r → ∞) the field recovers its asymptotic value φ_∞.  The width
    parameter a controls the sharpness of the well (larger a → narrower,
    stiffer bond).

    Parameters
    ----------
    r       : ndarray, shape (N,) — radial grid
    r0      : float — equilibrium bond length (well centre)
    phi_inf : float — asymptotic scalar value φ_∞ as r → ∞
    phi_min : float — minimum of φ at the bond centre
    a       : float — well-width parameter (a > 0)

    Returns
    -------
    phi : ndarray, shape (N,) — φ profile across the bond
    """
    r_arr = np.asarray(r, dtype=float)
    depth = phi_inf - phi_min
    return phi_inf - depth * np.exp(-(a ** 2) * (r_arr - r0) ** 2)


# ---------------------------------------------------------------------------
# Bond energy
# ---------------------------------------------------------------------------

def bond_energy(phi_inf: float, phi_min: float) -> float:
    """Bond energy as the depth of the φ-well.

    The chemical bond energy in Planck units equals the depth of the local
    minimum in the entanglement-capacity scalar:

        E_bond = φ_∞ − φ_min

    A deeper well produces a stronger bond.  When φ_inf = φ_min the
    function is flat and E_bond = 0 (no bond formed).

    Parameters
    ----------
    phi_inf : float — asymptotic scalar value φ_∞ (r → ∞)
    phi_min : float — minimum φ at bond centre

    Returns
    -------
    E_bond : float — bond energy in Planck units (≥ 0)

    Raises
    ------
    ValueError
        If phi_inf < phi_min (would imply a negative well depth).
    """
    if phi_inf < phi_min:
        raise ValueError(
            f"phi_inf must be ≥ phi_min; got phi_inf={phi_inf!r}, phi_min={phi_min!r}"
        )
    return float(phi_inf - phi_min)


# ---------------------------------------------------------------------------
# Geometric bond length
# ---------------------------------------------------------------------------

def bond_length_from_winding(
    n_w: int,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Geometric bond length from KK compactification.

    In the Kaluza–Klein reduction the natural orbital radius associated with
    winding number n_w on a compact S¹ of radius ⟨φ⟩ is:

        r₀ = 2π ⟨φ⟩ / (λ n_w)

    This is the bond length predicted purely from the 5D geometry — no
    empirical fitting required.  Higher winding numbers produce shorter,
    stronger bonds (analogous to higher bond orders).

    Parameters
    ----------
    n_w      : int   — winding number (positive integer; n = 1, 2, 3, ...)
    phi_mean : float — mean radion ⟨φ⟩ (compactification radius)
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    r0 : float — geometric bond length in Planck units

    Raises
    ------
    ValueError
        If n_w ≤ 0, phi_mean ≤ 0, or lam ≤ 0.
    """
    if n_w <= 0:
        raise ValueError(f"n_w must be > 0, got {n_w!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if lam <= 0.0:
        raise ValueError(f"lam must be > 0, got {lam!r}")
    return float(2.0 * np.pi * phi_mean / (lam * n_w))


# ---------------------------------------------------------------------------
# Chemical potential
# ---------------------------------------------------------------------------

def chemical_potential(
    r: np.ndarray,
    phi: np.ndarray,
    dx: float = 1.0,
) -> np.ndarray:
    """Chemical potential as the negative gradient of the entanglement scalar.

    The chemical potential at each grid point is defined as the negative
    spatial gradient of the entanglement-capacity scalar:

        μ_chem(x) = −∂φ/∂r

    At the equilibrium bond length the gradient is zero (μ_chem = 0), so
    the bond is in mechanical equilibrium.  Away from equilibrium the
    gradient drives the atoms toward r₀.

    Parameters
    ----------
    r   : ndarray, shape (N,) — radial grid (spacing dx)
    phi : ndarray, shape (N,) — entanglement-capacity scalar
    dx  : float — grid spacing (default 1)

    Returns
    -------
    mu : ndarray, shape (N,) — chemical potential at each grid point
    """
    phi_arr = np.asarray(phi, dtype=float)
    return -np.gradient(phi_arr, dx, edge_order=2)


# ---------------------------------------------------------------------------
# Bond order
# ---------------------------------------------------------------------------

def bond_order(
    n_w_bond: int,
    n_w_ref: int = _N_W_REF_DEFAULT,
) -> float:
    """Bond order from winding-number ratio.

    Chemical bond order (single = 1, double = 2, triple = 3) maps directly
    onto the ratio of the bond winding number to the reference winding number:

        b_order = n_w_bond / n_w_ref

    For n_w_ref = 5 (the Atiyah–Singer canonical winding number), a single
    bond corresponds to n_w_bond = 5 → b_order = 1.0, a double bond to
    n_w_bond = 10 → b_order = 2.0, etc.

    Parameters
    ----------
    n_w_bond : int — winding number of the specific bond
    n_w_ref  : int — reference winding number (default 5)

    Returns
    -------
    b_order : float — bond order

    Raises
    ------
    ValueError
        If n_w_bond < 0 or n_w_ref ≤ 0.
    """
    if n_w_bond < 0:
        raise ValueError(f"n_w_bond must be ≥ 0, got {n_w_bond!r}")
    if n_w_ref <= 0:
        raise ValueError(f"n_w_ref must be > 0, got {n_w_ref!r}")
    return float(n_w_bond) / float(n_w_ref)


# ---------------------------------------------------------------------------
# Bond stability
# ---------------------------------------------------------------------------

def is_bond_stable(
    B_strength: np.ndarray,
    B_dissociation: float,
) -> np.ndarray:
    """Check bond stability against the B_μ field strength threshold.

    A chemical bond remains intact as long as the local irreversibility field
    strength stays below the dissociation threshold:

        bond intact  iff  |B_μ(x)| < B_dissociation

    When the field strength exceeds the threshold the bond is broken — the
    geometric minimum of φ is disrupted by the irreversibility current.

    Parameters
    ----------
    B_strength      : array-like — local |B_μ| field strength at each point
    B_dissociation  : float — dissociation threshold (> 0)

    Returns
    -------
    stable : ndarray of bool — True where bond is intact

    Raises
    ------
    ValueError
        If B_dissociation ≤ 0.
    """
    if B_dissociation <= 0.0:
        raise ValueError(f"B_dissociation must be > 0, got {B_dissociation!r}")
    return np.abs(np.asarray(B_strength, dtype=float)) < B_dissociation


# ---------------------------------------------------------------------------
# Shell capacity
# ---------------------------------------------------------------------------

def shell_capacity(n_shell: int) -> int:
    """Electron shell capacity from winding quantization.

    The Kaluza–Klein quantization condition on S¹/Z₂ allows exactly 2n²
    distinct winding states for the n-th shell.  This reproduces the
    well-known atomic shell capacities:

        C(1) = 2,   C(2) = 8,   C(3) = 18,   C(4) = 32, ...

    Parameters
    ----------
    n_shell : int — principal quantum number (n ≥ 1)

    Returns
    -------
    capacity : int — number of electrons the shell can hold

    Raises
    ------
    ValueError
        If n_shell < 1.
    """
    if n_shell < 1:
        raise ValueError(f"n_shell must be ≥ 1, got {n_shell!r}")
    return 2 * n_shell ** 2
