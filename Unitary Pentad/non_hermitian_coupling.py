# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/non_hermitian_coupling.py
==========================================
Birefringence Asymmetry: Non-Reciprocal Coupling and Berry Phase Accumulation.

Background
----------
The standard Pentagonal Master Equation uses a **symmetric** coupling matrix:

    τ_{ij} = τ_{ji} = β × φ_trust

This models a closed-equilibrium system where the influence of body i on j is
exactly mirrored by j's influence on i.  In the real Human-in-the-Loop System
(HILS) this assumption fails:

    AI → Human influence:
        The AI body (Ψ_AI) presents synthesised, high-precision outputs that
        the human cognitive system internalises directly.  The effective
        coupling weight w_{AI→Human} can be 2× or more the reverse coupling
        when the human is in a receptive, low-autonomy state.

    Human → AI influence:
        The human provides semantic intent and corrective feedback.  Unless
        the AI is specifically tuned to weight human corrections highly, this
        direction carries a weaker coupling w_{Human→AI}.

Non-Hermitian Coupling Matrix
------------------------------
The asymmetric coupling matrix τ^NH (non-Hermitian) replaces the symmetric
matrix in the coupling operator:

    τ^NH_{ij} ≠ τ^NH_{ji}   in general.

For the (Human, AI) sub-block this becomes:

    τ^NH_{human,ai} = β × φ_trust × w_{H→A}   (human influences AI)
    τ^NH_{ai,human} = β × φ_trust × w_{A→H}   (AI influences human)

where w_{H→A}, w_{A→H} ≥ 0.  The symmetric case corresponds to
w_{H→A} = w_{A→H} = 1.

Berry Phase
-----------
When the coupling matrix is non-Hermitian and the system completes a closed
orbit in parameter space (e.g., a full cycle of trust oscillation), the
non-reciprocal sub-block accumulates a **Berry phase** — a geometric phase
proportional to the enclosed area in coupling-weight space:

    Δθ_Berry = π × (w_{A→H} − w_{H→A}) / (w_{A→H} + w_{H→A} + ε)

This phase is:
    • Zero for the symmetric case (w_{A→H} = w_{H→A}).
    • Maximal (→ ±π/2) when one direction dominates completely.
    • Observable as a residual phase offset between the Human and AI bodies
      after each orbit cycle even when all pairwise Information Gaps return
      to zero.

Stability Under Asymmetry
--------------------------
The (5,7) braid stabilises the pentagonal orbit by bounding the minimum
eigenvalue of the coupling matrix from below by c_s.  When the coupling
becomes non-Hermitian, the eigenvalues become complex; the relevant stability
condition shifts to the **spectral abscissa** (maximum real part of eigenvalues
of the *symmetrised* part of τ^NH):

    τ^sym = (τ^NH + (τ^NH)ᵀ) / 2

The system remains stable if the minimum eigenvalue of τ^sym still exceeds c_s.
The ``asymmetry_stability_margin`` function checks this condition.

Public API
----------
AsymmetryWeights
    Dataclass: w_ai_to_human and w_human_to_ai coupling weights.
    Default: symmetric (both = 1.0).

NonHermitianCouplingMatrix
    Dataclass wrapping the 5×5 asymmetric coupling array plus its symmetrised
    part and eigenspectrum.

build_non_hermitian_matrix(system, weights) -> NonHermitianCouplingMatrix
    Construct the 5×5 non-Hermitian coupling matrix from the current system
    state and asymmetry weights.

berry_phase(weights) -> float
    Geometric Berry phase accumulated per orbit cycle for the given weights.

apply_non_hermitian_coupling(system, weights, dt) -> PentadSystem
    Apply one step of the asymmetric coupling operator.

asymmetry_stability_margin(system, weights) -> float
    λ_min(τ^sym) − c_s.  Positive → stable; negative → below braid floor.

asymmetric_coupling_stress_test(system, weight_range, n_points) -> list[dict]
    Sweep AI-to-Human weight from 1× to weight_range× and return per-point
    diagnostics: Berry phase, stability margin, min eigenvalue.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    trust_modulation,
)
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode

_EPS: float = 1e-14


# ---------------------------------------------------------------------------
# AsymmetryWeights
# ---------------------------------------------------------------------------

@dataclass
class AsymmetryWeights:
    """Coupling weight asymmetry between the AI and Human bodies.

    Attributes
    ----------
    w_ai_to_human : float
        Weight multiplier on the AI → Human coupling direction.
        Default 1.0 (symmetric).
    w_human_to_ai : float
        Weight multiplier on the Human → AI coupling direction.
        Default 1.0 (symmetric).

    Physical interpretation
    -----------------------
    When w_ai_to_human > w_human_to_ai, the AI exerts stronger influence on
    the human than vice-versa.  w_ai_to_human = 2.0, w_human_to_ai = 1.0
    models the "AI has 2× influence" scenario from the problem statement.
    """
    w_ai_to_human: float = 1.0
    w_human_to_ai: float = 1.0

    def __post_init__(self) -> None:
        if self.w_ai_to_human < 0.0:
            raise ValueError(f"w_ai_to_human must be ≥ 0, got {self.w_ai_to_human}")
        if self.w_human_to_ai < 0.0:
            raise ValueError(f"w_human_to_ai must be ≥ 0, got {self.w_human_to_ai}")

    @property
    def is_symmetric(self) -> bool:
        """True iff the two weights are equal (Hermitian case)."""
        return abs(self.w_ai_to_human - self.w_human_to_ai) < 1e-10

    @property
    def asymmetry_ratio(self) -> float:
        """w_ai_to_human / w_human_to_ai (∞ if w_human_to_ai = 0)."""
        if self.w_human_to_ai < _EPS:
            return float("inf")
        return self.w_ai_to_human / self.w_human_to_ai


# ---------------------------------------------------------------------------
# NonHermitianCouplingMatrix
# ---------------------------------------------------------------------------

@dataclass
class NonHermitianCouplingMatrix:
    """5×5 non-Hermitian (asymmetric) pentagonal coupling matrix.

    Attributes
    ----------
    matrix       : ndarray (5, 5) — full asymmetric τ^NH
    symmetrised  : ndarray (5, 5) — (τ^NH + τ^NHᵀ) / 2
    eigenvalues  : ndarray (5,)   — real eigenvalues of the symmetrised part,
                                    sorted ascending
    min_eigenvalue : float — λ_min of the symmetrised matrix
    """
    matrix:         np.ndarray
    symmetrised:    np.ndarray
    eigenvalues:    np.ndarray
    min_eigenvalue: float


# ---------------------------------------------------------------------------
# build_non_hermitian_matrix
# ---------------------------------------------------------------------------

def build_non_hermitian_matrix(
    system: PentadSystem,
    weights: AsymmetryWeights,
) -> NonHermitianCouplingMatrix:
    """Construct the 5×5 non-Hermitian coupling matrix.

    Construction rules
    ------------------
    For the (Human, AI) sub-block the directed weights are applied:

        τ^NH_{human, ai}  = β × φ_trust × w_human_to_ai
        τ^NH_{ai, human}  = β × φ_trust × w_ai_to_human

    All other off-diagonal entries follow the standard symmetric rule:

        τ^NH_{i, j} = β × φ_trust          (neither i nor j is trust body)
        τ^NH_{i, trust} = τ^NH_{trust, j} = β   (bare coupling to trust body)

    The diagonal is zero.

    Parameters
    ----------
    system  : PentadSystem
    weights : AsymmetryWeights

    Returns
    -------
    NonHermitianCouplingMatrix
    """
    n = len(PENTAD_LABELS)
    mat = np.zeros((n, n))

    tau = trust_modulation(system)
    tau_other = system.beta * tau
    tau_trust = system.beta

    trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
    human_idx = PENTAD_LABELS.index(PentadLabel.HUMAN)
    ai_idx    = PENTAD_LABELS.index(PentadLabel.AI)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if i == trust_idx or j == trust_idx:
                mat[i, j] = tau_trust
            elif (i == human_idx and j == ai_idx):
                # Human influences AI
                mat[i, j] = tau_other * weights.w_human_to_ai
            elif (i == ai_idx and j == human_idx):
                # AI influences Human
                mat[i, j] = tau_other * weights.w_ai_to_human
            else:
                mat[i, j] = tau_other

    sym = (mat + mat.T) / 2.0
    eigs = np.sort(np.linalg.eigvalsh(sym))
    return NonHermitianCouplingMatrix(
        matrix=mat,
        symmetrised=sym,
        eigenvalues=eigs,
        min_eigenvalue=float(eigs[0]),
    )


# ---------------------------------------------------------------------------
# berry_phase
# ---------------------------------------------------------------------------

def berry_phase(weights: AsymmetryWeights) -> float:
    """Geometric Berry phase accumulated per closed orbit cycle.

    The Berry phase is defined here as the geometric phase that accumulates
    in the (Human, AI) sub-space when the system completes one full coupling
    cycle under non-reciprocal conditions:

        Δθ_Berry = (π/2) × (w_{A→H} − w_{H→A}) / (w_{A→H} + w_{H→A} + ε)

    Properties
    ----------
    * Zero for the symmetric case (w_{A→H} = w_{H→A}).
    * Approaches +π/2 as w_{A→H} → ∞ (AI dominates completely).
    * Approaches −π/2 as w_{H→A} → ∞ (Human dominates completely).
    * Strictly bounded within (−π/2, +π/2).
    * Units: radians.

    Parameters
    ----------
    weights : AsymmetryWeights

    Returns
    -------
    float — Berry phase ∈ (−π/2, +π/2) radians
    """
    wA = weights.w_ai_to_human
    wH = weights.w_human_to_ai
    denom = wA + wH + _EPS
    return float((math.pi / 2.0) * (wA - wH) / denom)


# ---------------------------------------------------------------------------
# apply_non_hermitian_coupling
# ---------------------------------------------------------------------------

def apply_non_hermitian_coupling(
    system: PentadSystem,
    weights: AsymmetryWeights,
    dt: float,
) -> PentadSystem:
    """Apply one step of the asymmetric (non-Hermitian) coupling operator.

    The directed coupling transfer for each ordered pair (i, j) is:

        ΔSᵢ   += τ^NH_{ij} (Sⱼ − Sᵢ) dt
        ΔXᵢ   += τ^NH_{ij} (Xⱼ − Xᵢ) dt
        Δφᵢ   += τ^NH_{ij} (φⱼ − φᵢ) dt

    Unlike the symmetric operator, the total state change no longer sums
    to zero when weights are asymmetric — this models the open/driven nature
    of the real HILS where the AI can inject more influence than it receives.

    Parameters
    ----------
    system  : PentadSystem
    weights : AsymmetryWeights
    dt      : float — pseudo-timestep

    Returns
    -------
    PentadSystem
    """
    nh = build_non_hermitian_matrix(system, weights)
    tau_mat = nh.matrix

    dS:   Dict[str, float]      = {lbl: 0.0 for lbl in PENTAD_LABELS}
    dX:   Dict[str, np.ndarray] = {
        lbl: np.zeros_like(system.bodies[lbl].node.X) for lbl in PENTAD_LABELS
    }
    dphi: Dict[str, float] = {lbl: 0.0 for lbl in PENTAD_LABELS}

    for idx_i, li in enumerate(PENTAD_LABELS):
        for idx_j, lj in enumerate(PENTAD_LABELS):
            if idx_i == idx_j:
                continue
            t_ij = float(tau_mat[idx_i, idx_j])
            bi = system.bodies[li]
            bj = system.bodies[lj]
            dS[li]   += t_ij * (bj.node.S - bi.node.S) * dt
            dX[li]   += t_ij * (bj.node.X - bi.node.X) * dt
            dphi[li] += t_ij * (bj.phi - bi.phi) * dt

    new_bodies: Dict[str, ManifoldState] = {}
    for lbl in PENTAD_LABELS:
        old = system.bodies[lbl]
        new_node = MultiverseNode(
            dim=old.node.dim,
            S=old.node.S + dS[lbl],
            A=old.node.A,
            Q_top=old.node.Q_top,
            X=old.node.X + dX[lbl],
            Xdot=old.node.Xdot.copy(),
        )
        new_bodies[lbl] = ManifoldState(
            node=new_node,
            phi=old.phi + dphi[lbl],
            n1=old.n1,
            n2=old.n2,
            k_cs=old.k_cs,
            label=old.label,
        )

    return PentadSystem(
        bodies=new_bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )


# ---------------------------------------------------------------------------
# asymmetry_stability_margin
# ---------------------------------------------------------------------------

def asymmetry_stability_margin(
    system: PentadSystem,
    weights: AsymmetryWeights,
) -> float:
    """Stability margin under non-Hermitian coupling.

    Returns λ_min(τ^sym) − c_s, where τ^sym is the symmetrised part of the
    non-Hermitian coupling matrix.  A positive value means the symmetrised
    eigenvalue still exceeds the (5,7) braid stability floor; a negative
    value signals that the asymmetry has driven the system below the floor.

    Parameters
    ----------
    system  : PentadSystem
    weights : AsymmetryWeights

    Returns
    -------
    float — margin (positive → stable, negative → below braid floor)
    """
    nh = build_non_hermitian_matrix(system, weights)
    return float(nh.min_eigenvalue - BRAIDED_SOUND_SPEED)


# ---------------------------------------------------------------------------
# asymmetric_coupling_stress_test
# ---------------------------------------------------------------------------

def asymmetric_coupling_stress_test(
    system: PentadSystem,
    weight_range: float = 3.0,
    n_points: int = 20,
) -> List[Dict]:
    """Sweep AI-to-Human coupling weight and record stability diagnostics.

    The Human-to-AI weight is held fixed at 1.0 while the AI-to-Human weight
    is varied from 1.0 to weight_range in n_points steps.

    For each weight value the following are recorded:

        w_ai_to_human    : float — current AI→Human weight
        berry_phase_rad  : float — Berry phase (rad)
        stability_margin : float — λ_min(τ^sym) − c_s
        min_eigenvalue   : float — λ_min(τ^sym)
        braid_holds      : bool  — stability_margin ≥ 0

    Parameters
    ----------
    system       : PentadSystem
    weight_range : float — maximum AI→Human weight (default 3.0, i.e. up to 3×)
    n_points     : int   — number of weight values to test (default 20)

    Returns
    -------
    list[dict] — one entry per weight point, sorted by w_ai_to_human ascending
    """
    results = []
    weights_ai = np.linspace(1.0, weight_range, n_points)
    for w_ai in weights_ai:
        aw = AsymmetryWeights(w_ai_to_human=float(w_ai), w_human_to_ai=1.0)
        nh = build_non_hermitian_matrix(system, aw)
        bp = berry_phase(aw)
        margin = float(nh.min_eigenvalue - BRAIDED_SOUND_SPEED)
        results.append({
            "w_ai_to_human":    float(w_ai),
            "berry_phase_rad":  bp,
            "stability_margin": margin,
            "min_eigenvalue":   float(nh.min_eigenvalue),
            "braid_holds":      margin >= 0.0,
        })
    return results
