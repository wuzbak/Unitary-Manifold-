# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/life.py
====================
Life as Negentropy Attractors — Pillar: Biology.

Life as negentropy attractors
-----------------------------
A living system is a local FTUM fixed point that continuously decreases its
internal entropy by exporting entropy to the environment.  This resolves
Schrödinger's 1944 question "What is Life?" in the language of the Unitary
Manifold:

    Life = stable solution to  UΨ* = Ψ*  requiring continuous energy input.

The key insight is that life does not violate the Second Law — it *uses* it.
The organism is an open dissipative system that maintains a high-φ (high
entanglement-capacity) interior by exporting a larger entropy flux to the
external, low-φ environment.

Metabolism
----------
Biochemical reaction networks inside cells are coupled B_μ flows at the
molecular scale.  The Irreversibility Field B_μ is the gauge-field avatar
of biochemical fluxes: each enzymatic reaction is a B_μ gauge transformation
that preserves the topological charge while doing thermodynamic work.

ATP synthesis = irreversibility field doing work
    ATP synthase is topologically equivalent to the B_μ field performing work
    against a φ-gradient (the proton-motive force across the inner
    mitochondrial membrane).  The synthesis rate mirrors:

        Γ_ATP ∝ exp(−Δφ / k_B T)

    where Δφ is the local φ gradient across the membrane (analog of the
    proton electrochemical potential difference).

Negentropy bound
----------------
The rate at which the organism decreases its internal entropy is bounded by
the information current it exports:

    ΔS_int = −J_info = −φ² |∇φ|

Information current conservation
---------------------------------
The information current four-vector is conserved:

    ∇_μ J^μ_inf = 0,   J^μ = φ² u^μ

where u^μ is the four-velocity of the matter flow.  The magnitude

    J_inf = φ² v

quantifies how much biological information (negentropy) the organism
generates and exports per unit time.

Public API
----------
negentropy_rate(phi, phi_env, lam)
    Rate of internal entropy decrease Δ_neg = lam * (phi**2 - phi_env**2).

metabolic_power(phi, B_strength, lam)
    Metabolic power from the B_μ irreversibility field.

atp_synthesis_rate(delta_phi, T, k_B)
    Rate ∝ exp(−delta_phi / (k_B T)).

information_current(phi, v)
    Information current magnitude J_inf = phi**2 * v.

is_living(phi_internal, phi_environment, threshold)
    True iff the negentropy rate exceeds threshold.

cellular_phi_field(n_cells, phi_mean, sigma, seed)
    Spatial distribution of φ across n_cells cells.

homeostasis_defect(phi_field, phi_target)
    Deviation from homeostatic fixed point |mean(φ) − φ_target|.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_K_B_DEFAULT: float = 1.0


# ---------------------------------------------------------------------------
# Negentropy and life condition
# ---------------------------------------------------------------------------

def negentropy_rate(
    phi: float,
    phi_env: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Rate of internal entropy decrease driven by φ contrast.

    A living system maintains φ_internal > φ_environment.  The
    resulting negentropy rate is:

        Δ_neg = λ (φ² − φ_env²)

    Positive Δ_neg means the organism exports entropy to the environment —
    the thermodynamic signature of life.

    Parameters
    ----------
    phi     : float — internal entanglement capacity φ (must be > 0)
    phi_env : float — environmental entanglement capacity φ_env (must be > 0)
    lam     : float — coupling constant λ (default 1)

    Returns
    -------
    delta_neg : float — negentropy rate (positive ↔ alive)

    Raises
    ------
    ValueError
        If phi ≤ 0 or phi_env ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_env <= 0.0:
        raise ValueError(f"phi_env must be > 0, got {phi_env!r}")
    return float(lam * (phi**2 - phi_env**2))


def metabolic_power(
    phi: float,
    B_strength: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Metabolic power from the B_μ irreversibility field.

    The B_μ field doing metabolic work contributes an effective power:

        P_met = λ² φ² |B|² / 2

    This mirrors the dark-matter energy density formula from
    ``src/core/dark_matter_geometry.py``, here applied at the cellular scale.

    Parameters
    ----------
    phi        : float — intracellular entanglement capacity φ (must be > 0)
    B_strength : float — local B_μ field magnitude (must be ≥ 0)
    lam        : float — coupling constant λ (default 1)

    Returns
    -------
    P_met : float — metabolic power (≥ 0)

    Raises
    ------
    ValueError
        If phi ≤ 0 or B_strength < 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if B_strength < 0.0:
        raise ValueError(f"B_strength must be ≥ 0, got {B_strength!r}")
    return float(lam**2 * phi**2 * B_strength**2 / 2.0)


def atp_synthesis_rate(
    delta_phi: float,
    T: float,
    k_B: float = _K_B_DEFAULT,
) -> float:
    """ATP synthesis rate as a Boltzmann factor over the φ-gradient.

    ATP synthase is modelled as the B_μ field doing work against a local
    φ-gradient (the proton-motive force analog):

        Γ_ATP ∝ exp(−Δφ / k_B T)

    A large φ-gradient (steep proton gradient) slows synthesis; a small
    gradient or high temperature accelerates it.

    Parameters
    ----------
    delta_phi : float — local φ gradient across the membrane (Δφ ≥ 0)
    T         : float — temperature (must be > 0)
    k_B       : float — Boltzmann constant (default 1, natural units)

    Returns
    -------
    rate : float — synthesis rate ∈ (0, 1]

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    return float(np.exp(-delta_phi / (k_B * T)))


def information_current(
    phi: float,
    v: float = 1.0,
) -> float:
    """Information current magnitude exported by the organism.

    The conserved information current four-vector J^μ = φ² u^μ has spatial
    magnitude:

        J_inf = φ² v

    where v is the matter-flow velocity magnitude.

    Parameters
    ----------
    phi : float — local entanglement capacity φ (must be > 0)
    v   : float — flow velocity magnitude (default 1)

    Returns
    -------
    J_inf : float — information current magnitude (≥ 0)

    Raises
    ------
    ValueError
        If phi ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    return float(phi**2 * v)


def is_living(
    phi_internal: float,
    phi_environment: float,
    threshold: float = 0.0,
) -> bool:
    """Test whether a system satisfies the thermodynamic life condition.

    A system is "alive" if it actively exports entropy — i.e., if its
    negentropy rate exceeds *threshold*:

        is_living = (negentropy_rate(φ_int, φ_env) > threshold)

    Parameters
    ----------
    phi_internal    : float — internal φ (must be > 0)
    phi_environment : float — environmental φ (must be > 0)
    threshold       : float — minimum negentropy rate to count as alive (default 0)

    Returns
    -------
    bool
    """
    return negentropy_rate(phi_internal, phi_environment) > threshold


def cellular_phi_field(
    n_cells: int,
    phi_mean: float,
    sigma: float = 0.1,
    seed: int = 42,
) -> np.ndarray:
    """Spatial distribution of entanglement capacity across a tissue.

    Models the stochastic variation of φ from cell to cell within a tissue
    by drawing from a Normal distribution:

        φ_i ~ Normal(φ_mean, σ²)   for i = 1, …, n_cells

    Parameters
    ----------
    n_cells  : int   — number of cells (must be ≥ 1)
    phi_mean : float — mean intracellular φ (must be > 0)
    sigma    : float — standard deviation of φ across cells (default 0.1)
    seed     : int   — random seed for reproducibility (default 42)

    Returns
    -------
    phi_field : ndarray, shape (n_cells,)

    Raises
    ------
    ValueError
        If n_cells < 1 or phi_mean ≤ 0.
    """
    if n_cells < 1:
        raise ValueError(f"n_cells must be ≥ 1, got {n_cells!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    rng = np.random.default_rng(seed)
    return rng.normal(loc=phi_mean, scale=sigma, size=n_cells)


def homeostasis_defect(
    phi_field: np.ndarray,
    phi_target: float,
) -> float:
    """Deviation of the tissue-average φ from the homeostatic fixed point.

    A healthy organism keeps ⟨φ⟩ ≈ φ_target.  The homeostasis defect is:

        δ_H = |mean(φ_field) − φ_target|

    δ_H = 0 indicates perfect homeostasis; larger values indicate disease
    or dysregulation.

    Parameters
    ----------
    phi_field  : ndarray — φ values across cells
    phi_target : float   — homeostatic target value of φ

    Returns
    -------
    defect : float — |⟨φ⟩ − φ_target| (≥ 0)
    """
    return float(abs(np.mean(phi_field) - phi_target))
