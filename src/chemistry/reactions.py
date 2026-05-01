# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/chemistry/reactions.py
===========================
Chemical Reactions as B_μ Field Transitions — Pillar 9.

In the Unitary Manifold a chemical reaction is not merely a rearrangement of
atoms; it is a transition between distinct minima of the entanglement-capacity
scalar φ driven by the irreversibility field B_μ.  The activation energy is
the height of the B_μ field barrier between reactant and product φ-minima.
The reaction rate is an Arrhenius exponential in that barrier height.

Theory summary
--------------
Arrhenius rate constant:
    k(T) = A · exp(−E_a / (k_B T))

B_μ activation barrier:
    E_a = λ² φ_mean² H_max² / 2
    where H_max = max|H_μν| = max|∂_μ B_ν − ∂_ν B_μ| (field-strength tensor)

Equilibrium constant from φ difference:
    K_eq = exp(−Δφ / (k_B T))
    where Δφ = φ_products − φ_reactants

Reaction flux (information-current driven):
    J_react = D · φ² · ∇(ln φ)
    = D · φ · ∇φ

Field-strength tensor (1D approximation):
    |H(x)| ≈ |dB/dx|  (antisymmetric finite-difference)

Gibbs free energy analog:
    ΔG_eff = ΔS_U · k_B T

Public API
----------
arrhenius_rate(A, E_a, T, k_B)
    Standard Arrhenius rate constant.

b_field_activation_energy(H_max, phi_mean, lam)
    Activation energy from B_μ field-strength barrier.

equilibrium_constant(delta_phi, T, k_B)
    K_eq = exp(−delta_phi / (k_B T)).

reaction_flux(phi, D, dx)
    Information-current driven reaction flux J_react.

field_strength_tensor(B, dx)
    1D B_μ field-strength magnitude |dB/dx|.

gibbs_analog(delta_S_U, T, k_B)
    Effective Gibbs free energy ΔG_eff = ΔS_U · k_B T.
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
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Arrhenius rate
# ---------------------------------------------------------------------------

def arrhenius_rate(
    A: float,
    E_a: float,
    T: float,
    k_B: float = 1.0,
) -> float:
    """Arrhenius rate constant for a thermally activated B_μ barrier crossing.

    The probability per unit time for the irreversibility field to surmount
    the activation barrier E_a at temperature T follows the familiar
    Arrhenius form:

        k(T) = A · exp(−E_a / (k_B T))

    Here E_a is the height of the B_μ field-strength barrier between the
    reactant and product φ-minima (see b_field_activation_energy).

    Parameters
    ----------
    A   : float — pre-exponential frequency factor (attempt rate)
    E_a : float — activation energy in Planck units (≥ 0)
    T   : float — temperature (must be > 0)
    k_B : float — Boltzmann constant (default 1, Planck units)

    Returns
    -------
    k : float — rate constant

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"Temperature T must be > 0, got {T!r}")
    return float(A * np.exp(-E_a / (k_B * T)))


# ---------------------------------------------------------------------------
# B_μ activation energy
# ---------------------------------------------------------------------------

def b_field_activation_energy(
    H_max: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Activation energy from the B_μ field-strength barrier.

    The B_μ field-strength tensor H_μν = ∂_μ B_ν − ∂_ν B_μ creates a
    potential barrier between reactant and product configurations.  The
    height of this barrier sets the activation energy:

        E_a = λ² φ_mean² H_max² / 2

    Higher field-strength peak (larger H_max) or stronger compactification
    coupling (larger λ, larger φ_mean) increases the activation barrier and
    slows the reaction.

    Parameters
    ----------
    H_max    : float — peak field-strength tensor magnitude max|H_μν|
    phi_mean : float — mean radion ⟨φ⟩
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    E_a : float — activation energy in Planck units (≥ 0)
    """
    return float(0.5 * lam ** 2 * phi_mean ** 2 * H_max ** 2)


# ---------------------------------------------------------------------------
# Equilibrium constant
# ---------------------------------------------------------------------------

def equilibrium_constant(
    delta_phi: float,
    T: float,
    k_B: float = 1.0,
) -> float:
    """Equilibrium constant from the φ-well difference between products and reactants.

    At thermodynamic equilibrium the ratio of product to reactant populations
    is set by the difference in entanglement-capacity scalar values:

        K_eq = exp(−Δφ / (k_B T))
        Δφ = φ_products − φ_reactants

    When Δφ = 0 the two configurations are degenerate and K_eq = 1.  For
    Δφ > 0 (products at higher φ) the reaction is driven toward reactants
    (K_eq < 1); for Δφ < 0 (products at lower φ) the reaction is
    thermodynamically favoured (K_eq > 1).

    Parameters
    ----------
    delta_phi : float — φ_products − φ_reactants
    T         : float — temperature (must be > 0)
    k_B       : float — Boltzmann constant (default 1)

    Returns
    -------
    K_eq : float — dimensionless equilibrium constant

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"Temperature T must be > 0, got {T!r}")
    return float(np.exp(-delta_phi / (k_B * T)))


# ---------------------------------------------------------------------------
# Reaction flux
# ---------------------------------------------------------------------------

def reaction_flux(
    phi: np.ndarray,
    D: float = 1.0,
    dx: float = 1.0,
) -> np.ndarray:
    """Information-current driven reaction flux.

    The irreversibility field drives information (and hence chemical species)
    from regions of high φ to regions of low φ.  The resulting reaction flux
    is:

        J_react = D · φ² · ∇(ln φ)  =  D · φ · ∇φ

    The equality follows because ∇(ln φ) = ∇φ / φ, so the φ² factor
    reduces to φ.  On a uniform grid ∇φ is computed with np.gradient.

    Parameters
    ----------
    phi : ndarray, shape (N,) — entanglement-capacity scalar
    D   : float — diffusion-like transport coefficient (default 1)
    dx  : float — grid spacing (default 1)

    Returns
    -------
    J : ndarray, shape (N,) — reaction flux at each grid point
    """
    phi_arr = np.asarray(phi, dtype=float)
    grad_phi = np.gradient(phi_arr, dx, edge_order=2)
    return D * phi_arr * grad_phi


# ---------------------------------------------------------------------------
# Field-strength tensor (1D)
# ---------------------------------------------------------------------------

def field_strength_tensor(
    B: np.ndarray,
    dx: float = 1.0,
) -> np.ndarray:
    """1D B_μ field-strength magnitude |dB/dx|.

    In the full 5D theory the field-strength tensor is the antisymmetric
    combination H_μν = ∂_μ B_ν − ∂_ν B_μ.  On a 1D grid with a scalar B
    field the only non-trivial component is |dB/dx|, computed via
    np.gradient:

        |H(x)| ≈ |dB/dx|

    Parameters
    ----------
    B  : ndarray, shape (N,) — 1D B_μ field values
    dx : float — grid spacing (default 1)

    Returns
    -------
    H_mag : ndarray, shape (N,) — field-strength magnitude at each point
    """
    B_arr = np.asarray(B, dtype=float)
    return np.abs(np.gradient(B_arr, dx, edge_order=2))


# ---------------------------------------------------------------------------
# Gibbs free energy analog
# ---------------------------------------------------------------------------

def gibbs_analog(
    delta_S_U: float,
    T: float,
    k_B: float = 1.0,
) -> float:
    """Effective Gibbs free energy from the change in the unitary action functional.

    In the Unitary Manifold the role of the Gibbs free energy is played by
    the change in the action functional S_U weighted by thermal energy:

        ΔG_eff = ΔS_U · k_B T

    A positive ΔG_eff corresponds to an action increase (reaction
    thermodynamically disfavoured); negative ΔG_eff means the 5D geometry
    lowers its action — the reaction proceeds spontaneously.

    Parameters
    ----------
    delta_S_U : float — change in unitary action functional ΔS_U
    T         : float — temperature (must be > 0)
    k_B       : float — Boltzmann constant (default 1)

    Returns
    -------
    dG : float — effective Gibbs free energy in Planck units

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"Temperature T must be > 0, got {T!r}")
    return float(delta_S_U * k_B * T)
