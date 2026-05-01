# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dissipation_geometry.py
=================================
Pillar 35 — Many-Body Dissipation as 5D Geometric Identity.

Physical context
----------------
In standard statistical mechanics, entropy and dissipation are emergent
statistical concepts: they arise from coarse-graining over many microscopic
degrees of freedom.  The Unitary Manifold replaces this statistical origin
with a **5D geometric identity**: the entropy of any physical system is
encoded in the field-strength tensor H_μν = ∂_μ B_ν − ∂_ν B_μ of the
irreversibility gauge field B_μ.

The irreversibility field B_μ in evolution.py is the gauge field for the
arrow of time.  Its field-strength tensor H_μν satisfies a geometric
Maxwell-like equation whose action functional is

    S_B = −(1/4) ∫ H_μν H^μν √(−g₅) d⁵x                          [1]

The 4D entropy density is then the dimensional reduction of [1]:

    ρ_S(x) = (1/4π) × ⟨H_μν H^μν⟩₄D                               [2]

where the angular brackets denote the zero-mode projection (integration
over the compact S¹/Z₂ dimension).

For a homogeneous background B_μ = (B₀, 0, 0, 0) (only time component):

    H₀ᵢ = ∂₀ Bᵢ − ∂ᵢ B₀ = −∂ᵢ B₀
    H_μν H^μν = 2 |∇B₀|²                                           [3]

This reduces exactly to the Boltzmann entropy density at the FTUM fixed
point φ = φ_star when the radion is at its stabilised value:

    ρ_S(φ_star) = k_B × S_Boltzmann / V                            [4]

(Planck units: k_B = 1.)

Many-body extension
~~~~~~~~~~~~~~~~~~~~
For N non-interacting particles in the 5D geometry, each carrying a
B_μ charge q_i, the total geometric entropy is

    S_N = Σᵢ ρ_S(xᵢ) + S_interaction                              [5]

where the interaction term arises from the braided-winding correlations
between particle pairs.  At the mean-field level:

    S_interaction = −(1/2) Σᵢ≠ⱼ K(xᵢ, xⱼ)                       [6]

with K the two-point function of H_μν in the KK background.

Lindblad dissipator
~~~~~~~~~~~~~~~~~~~~
The irreversibility field B_μ sources a Lindblad-type master equation for
any quantum state ρ coupled to it:

    dρ/dt = −i[H, ρ] + γ (B ρ B† − ½{B†B, ρ})                   [7]

where B here denotes the operator corresponding to the zero mode of B_μ,
and γ is the dissipation rate set by the GW mass:

    γ = m_φ² × c_s² / (2π)                                         [8]

Entropy production rate
~~~~~~~~~~~~~~~~~~~~~~~~
The entropy production rate (second law manifest geometrically) is

    σ = dS/dt = Tr(ρ dH/dt) / T ≥ 0                               [9]

In the UM framework this becomes:

    σ = (1/4π) × ∂_t ⟨H_μν H^μν⟩ = 2γ × S_von_Neumann(ρ)       [10]

The second law (σ ≥ 0) follows from the positive semi-definiteness of the
Lindblad dissipator, which in turn follows from the positivity of the GW
potential.  **Irreversibility is thus a consequence of the 5D metric
topology, not of statistical coarse-graining.**

Connection to Boltzmann entropy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At the FTUM fixed point (φ = φ_star), the geometric entropy density equals
the thermodynamic Boltzmann entropy:

    ρ_S(φ_star) = S_Boltzmann / V

This is the key bridge between the 5D geometric formulation and the
standard thermodynamic description.  Away from the fixed point, the
information current deficit D(φ) = |1 − (φ/φ_star)²| quantifies the
leakage into modes not counted by thermodynamic entropy.

Public API
----------
geometric_entropy_density(H_field_strength_sq)
    ρ_S = H_μν H^μν / (4π) — geometric entropy density from field strength.

entropy_from_B_gradient(grad_B0)
    Entropy density when B_μ = (B₀, 0, 0, 0): ρ_S = |∇B₀|² / (2π).

lindblad_dissipation_rate(m_phi, c_s)
    Dissipation rate γ = m_φ² c_s² / (2π).

many_body_geometric_entropy(single_entropy, N)
    Total geometric entropy for N non-interacting particles:
    S_N = N × single_entropy.

lindblad_entropy_production(gamma, S_von_neumann)
    Entropy production rate σ = 2γ × S_von_neumann.

geometric_equals_boltzmann(phi, phi_star, S_boltzmann, V)
    Return True iff the geometric entropy density equals Boltzmann to within
    tolerance tol (valid exactly at φ = φ_star).

entropy_current_density(phi, u_mu)
    J^μ_S = ρ_S × u^μ — entropy current 4-vector.

information_leakage_fraction(phi, phi_star)
    Fraction of entropy leaking into KK modes: D(φ) = |1 − (φ/φ_star)²|.

second_law_check(sigma)
    Return True iff the entropy production rate σ ≥ 0 (second law).

geometric_entropy_from_state(phi, phi_star, S_boltzmann, V)
    Full geometric entropy including information-leakage correction.

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

import math
from typing import Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_TWO_PI: float = 2.0 * math.pi
_FOUR_PI: float = 4.0 * math.pi

#: Canonical braid pair constants
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74
C_S_CANONICAL: float = 12.0 / 37.0

#: Canonical Goldberger–Wise mass parameter (Planck units)
M_PHI_CANONICAL: float = 1.0

#: Canonical Lindblad dissipation rate γ = m_φ² c_s² / (2π)
GAMMA_CANONICAL: float = M_PHI_CANONICAL ** 2 * C_S_CANONICAL ** 2 / _TWO_PI


# ---------------------------------------------------------------------------
# geometric_entropy_density
# ---------------------------------------------------------------------------

def geometric_entropy_density(H_field_strength_sq: float) -> float:
    """Geometric entropy density from the irreversibility field strength.

    The action of the irreversibility gauge field B_μ in 5D is

        S_B = −(1/4) ∫ H_μν H^μν d⁵x  (√(−g₅) ≈ 1 in Planck units)

    After dimensional reduction the 4D entropy density is

        ρ_S = H_μν H^μν / (4π)

    where H_field_strength_sq = H_μν H^μν (the Lorentz-contracted square
    of the field-strength tensor).

    Parameters
    ----------
    H_field_strength_sq : float
        H_μν H^μν evaluated at a spacetime point (≥ 0 in Euclidean signature).

    Returns
    -------
    rho_S : float
        Geometric entropy density in Planck units (≥ 0).

    Raises
    ------
    ValueError if H_field_strength_sq < 0.
    """
    if H_field_strength_sq < 0.0:
        raise ValueError(
            f"H_field_strength_sq must be ≥ 0 (Euclidean), got {H_field_strength_sq!r}"
        )
    return H_field_strength_sq / _FOUR_PI


# ---------------------------------------------------------------------------
# entropy_from_B_gradient
# ---------------------------------------------------------------------------

def entropy_from_B_gradient(grad_B0: float) -> float:
    """Entropy density when B_μ = (B₀, 0, 0, 0) from its spatial gradient.

    For a time-component-only gauge field:
        H₀ᵢ = −∂ᵢ B₀
        H_μν H^μν = 2 |∇B₀|²

    So the entropy density is:
        ρ_S = 2 |∇B₀|² / (4π) = |∇B₀|² / (2π)

    Parameters
    ----------
    grad_B0 : float
        |∇B₀| — magnitude of the spatial gradient of B₀ (≥ 0).

    Returns
    -------
    rho_S : float
        Geometric entropy density in Planck units (≥ 0).

    Raises
    ------
    ValueError if grad_B0 < 0.
    """
    if grad_B0 < 0.0:
        raise ValueError(f"grad_B0 must be ≥ 0, got {grad_B0!r}")
    return grad_B0 ** 2 / _TWO_PI


# ---------------------------------------------------------------------------
# lindblad_dissipation_rate
# ---------------------------------------------------------------------------

def lindblad_dissipation_rate(m_phi: float, c_s: float) -> float:
    """Lindblad dissipation rate γ from the GW mass and braided sound speed.

    The zero-mode B operator couples to matter with dissipation rate:

        γ = m_φ² c_s² / (2π)

    At the canonical (5,7) values: γ ≈ GAMMA_CANONICAL.

    Parameters
    ----------
    m_phi : float — Goldberger–Wise mass parameter in Planck units (≥ 0)
    c_s   : float — braided sound speed (0 < c_s ≤ 1)

    Returns
    -------
    gamma : float ≥ 0

    Raises
    ------
    ValueError if m_phi < 0 or c_s ≤ 0 or c_s > 1.
    """
    if m_phi < 0.0:
        raise ValueError(f"m_phi must be ≥ 0, got {m_phi!r}")
    if c_s <= 0.0 or c_s > 1.0:
        raise ValueError(f"c_s must be in (0, 1], got {c_s!r}")
    return m_phi ** 2 * c_s ** 2 / _TWO_PI


# ---------------------------------------------------------------------------
# many_body_geometric_entropy
# ---------------------------------------------------------------------------

def many_body_geometric_entropy(single_entropy: float, N: int) -> float:
    """Total geometric entropy for N non-interacting particles.

    For N identical, non-interacting particles in the 5D KK background,
    each carrying geometric entropy single_entropy, the total is

        S_N = N × single_entropy                                     (mean field)

    Interaction corrections are of order O(1/N) and are neglected here.

    Parameters
    ----------
    single_entropy : float — geometric entropy of one particle (≥ 0)
    N              : int   — number of particles (≥ 1)

    Returns
    -------
    S_N : float ≥ 0

    Raises
    ------
    ValueError if single_entropy < 0 or N < 1.
    """
    if single_entropy < 0.0:
        raise ValueError(f"single_entropy must be ≥ 0, got {single_entropy!r}")
    if N < 1:
        raise ValueError(f"N must be ≥ 1, got {N!r}")
    return float(N) * single_entropy


# ---------------------------------------------------------------------------
# lindblad_entropy_production
# ---------------------------------------------------------------------------

def lindblad_entropy_production(gamma: float, S_von_neumann: float) -> float:
    """Entropy production rate from the Lindblad dissipator.

    From the UM Lindblad equation (eq. [7] in module docstring):

        dS/dt = 2γ × S_von_Neumann(ρ)                              [10]

    This is always ≥ 0, reflecting the geometric second law.

    Parameters
    ----------
    gamma         : float — Lindblad dissipation rate (≥ 0)
    S_von_neumann : float — von Neumann entropy of the state ρ (≥ 0)

    Returns
    -------
    sigma : float — entropy production rate (≥ 0)

    Raises
    ------
    ValueError if gamma < 0 or S_von_neumann < 0.
    """
    if gamma < 0.0:
        raise ValueError(f"gamma must be ≥ 0, got {gamma!r}")
    if S_von_neumann < 0.0:
        raise ValueError(f"S_von_neumann must be ≥ 0, got {S_von_neumann!r}")
    return 2.0 * gamma * S_von_neumann


# ---------------------------------------------------------------------------
# geometric_equals_boltzmann
# ---------------------------------------------------------------------------

def geometric_equals_boltzmann(
    phi: float,
    phi_star: float,
    S_boltzmann: float,
    V: float,
    tol: float = 1e-10,
) -> bool:
    """Check whether geometric entropy density equals Boltzmann entropy.

    At the FTUM fixed point φ = φ_star, the 5D geometric entropy density
    equals the thermodynamic Boltzmann entropy:

        ρ_S(φ_star) = S_Boltzmann / V

    This is violated by the information-leakage fraction D(φ) = |1 − (φ/φ_star)²|.

    Parameters
    ----------
    phi         : float — current radion value (> 0)
    phi_star    : float — FTUM fixed-point value (> 0)
    S_boltzmann : float — thermodynamic entropy of the system (≥ 0)
    V           : float — physical volume in Planck units (> 0)
    tol         : float — tolerance on D(φ) (default 1e-10)

    Returns
    -------
    bool — True iff D(φ) < tol (i.e., φ ≈ φ_star)

    Raises
    ------
    ValueError if phi ≤ 0, phi_star ≤ 0, S_boltzmann < 0, or V ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star must be > 0, got {phi_star!r}")
    if S_boltzmann < 0.0:
        raise ValueError(f"S_boltzmann must be ≥ 0, got {S_boltzmann!r}")
    if V <= 0.0:
        raise ValueError(f"V must be > 0, got {V!r}")
    D = abs(1.0 - (phi / phi_star) ** 2)
    return D < tol


# ---------------------------------------------------------------------------
# entropy_current_density
# ---------------------------------------------------------------------------

def entropy_current_density(
    rho_S: float,
    u_mu: Sequence[float],
) -> np.ndarray:
    """Entropy current 4-vector J^μ_S = ρ_S × u^μ.

    In the 4D effective theory the entropy current is

        J^μ_S = ρ_S u^μ

    where ρ_S is the geometric entropy density and u^μ is the 4-velocity
    of the fluid element (normalised: u^μ u_μ = −1 in (−,+,+,+) signature).

    Parameters
    ----------
    rho_S : float        — geometric entropy density (≥ 0)
    u_mu  : sequence[4] — 4-velocity components u^μ (length 4)

    Returns
    -------
    J_S : np.ndarray, shape (4,), float64

    Raises
    ------
    ValueError if rho_S < 0 or u_mu does not have length 4.
    """
    if rho_S < 0.0:
        raise ValueError(f"rho_S must be ≥ 0, got {rho_S!r}")
    u = np.asarray(u_mu, dtype=float).ravel()
    if u.shape != (4,):
        raise ValueError(f"u_mu must have length 4, got shape {u.shape}.")
    return rho_S * u


# ---------------------------------------------------------------------------
# information_leakage_fraction
# ---------------------------------------------------------------------------

def information_leakage_fraction(phi: float, phi_star: float) -> float:
    """Fraction of entropy leaking into KK modes not counted thermodynamically.

    D(φ) = |1 − (φ/φ_star)²|

    D = 0 at φ = φ_star: all entropy is geometric, no leakage.
    D → 1 as φ → 0: all entropy leaks into KK modes (non-thermodynamic).
    D > 1 for φ ≫ φ_star (unphysical: radion runaway prevented by GW potential).

    Parameters
    ----------
    phi      : float — current radion field value (> 0)
    phi_star : float — FTUM fixed-point value (> 0)

    Returns
    -------
    D : float ≥ 0

    Raises
    ------
    ValueError if phi ≤ 0 or phi_star ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star must be > 0, got {phi_star!r}")
    return float(abs(1.0 - (phi / phi_star) ** 2))


# ---------------------------------------------------------------------------
# second_law_check
# ---------------------------------------------------------------------------

def second_law_check(sigma: float) -> bool:
    """Return True iff entropy production rate satisfies the second law.

    The geometric second law (σ ≥ 0) is guaranteed by the positive
    semi-definiteness of the GW potential.  This function validates
    that a computed σ is non-negative (numerical sanity check).

    Parameters
    ----------
    sigma : float — entropy production rate

    Returns
    -------
    bool — True iff sigma ≥ 0

    Raises
    ------
    ValueError if sigma is not a finite number.
    """
    if not math.isfinite(sigma):
        raise ValueError(f"sigma must be finite, got {sigma!r}")
    return sigma >= 0.0


# ---------------------------------------------------------------------------
# geometric_entropy_from_state
# ---------------------------------------------------------------------------

def geometric_entropy_from_state(
    phi: float,
    phi_star: float,
    S_boltzmann: float,
    V: float,
) -> float:
    """Total geometric entropy including information-leakage correction.

    The geometric entropy is related to the thermodynamic Boltzmann entropy by

        S_geo = S_Boltzmann × (1 − D(φ))

    where D(φ) = |1 − (φ/φ_star)²| is the information-leakage fraction.

    At φ = φ_star: S_geo = S_Boltzmann (perfect agreement).
    At φ ≠ φ_star: S_geo < S_Boltzmann (some entropy hidden in KK modes).

    Parameters
    ----------
    phi         : float — current radion value (> 0)
    phi_star    : float — FTUM fixed-point value (> 0)
    S_boltzmann : float — thermodynamic entropy of the system (≥ 0)
    V           : float — physical volume in Planck units (> 0)

    Returns
    -------
    S_geo : float ≥ 0

    Raises
    ------
    ValueError if phi ≤ 0, phi_star ≤ 0, S_boltzmann < 0, or V ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star must be > 0, got {phi_star!r}")
    if S_boltzmann < 0.0:
        raise ValueError(f"S_boltzmann must be ≥ 0, got {S_boltzmann!r}")
    if V <= 0.0:
        raise ValueError(f"V must be > 0, got {V!r}")
    D = information_leakage_fraction(phi, phi_star)
    fraction = max(0.0, 1.0 - D)
    return S_boltzmann * fraction
