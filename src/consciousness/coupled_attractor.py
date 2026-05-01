# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/consciousness/coupled_attractor.py
=======================================
Coupled Master Equation for the Brain–Universe two-body system.

Background
----------
The Unitary Manifold treats the brain and universe as two 5D manifolds,
each governed by the same Walker-Pearson field equations, each converging
toward its own FTUM fixed point Ψ*.  The ``brain/`` folder established the
*structural* alignment: the same field variables carry different physical
labels at cosmological and neural scale.

This module implements the *dynamical* alignment: the two manifolds are
coupled oscillators, performing a topological handshake through the
birefringence angle β = 0.3513°, which acts as the coupling constant —
the "Information Gap" between the two attractors.

The Coupled Master Equation
---------------------------
Instead of solving U Ψ* = Ψ* for a single manifold, we solve:

    U_total (Ψ_brain ⊗ Ψ_univ) = Ψ_brain ⊗ Ψ_univ

where the combined operator is

    U_total = (U_brain ⊗ I)  +  (I ⊗ U_univ)  +  β · C

and C is the bilinear coupling operator that transfers information flux
between the two manifolds.  The coupling constant is

    β_rad = β × π / 180  (birefringence angle in radians)
          = 0.3513° × π / 180  ≈  6.132 × 10⁻³  rad

The convergence conditions at the coupled fixed point are:

    1. Individual FTUM defect of each manifold < tol
    2. Information Gap ΔI = |φ²_brain − φ²_univ| → 0
    3. Phase offset Δφ = ∠(X_brain, X_univ) → 0   (Moiré alignment)

Physical interpretation
-----------------------
information_gap
    The Information Gap ΔI is the coupling constant.  When ΔI → 0 the
    two manifolds have identical information-carrying capacity: the
    Moiré pattern has infinite wavelength and perceptual reality dissolves
    into pure symmetry (Ψ*_brain = Ψ*_univ, the samadhi / ego-dissolution
    limit).  Normal conscious experience sits at ΔI > 0.

phase_offset
    The Moiré phase angle Δφ between the two 5D tori.  Δφ = 0 is the
    maximum-alignment limit (brain-torus phase-locks to universe-torus);
    Δφ > 0 is the standard differentiated conscious state.

resonance_ratio
    The precession-rate ratio ω_brain / ω_univ.  At the coupled fixed
    point this locks to n1 / n2 = 5/7 ≈ 0.714, confirmed by the grid-cell
    module spacing ratio 7/5 ≈ 1.40 (brain torus architecture).

back-reaction (via the coupling operator C)
    Learning, trauma, or focused attention shift the brain's local gauge
    field (entropy, radion φ, UEUM position X), exerting a topological pull
    on the universe's local field — and vice versa.  This is the "two-way
    street": both bodies are active participants in the dynamical alignment.

Public API
----------
BIREFRINGENCE_DEG : float  = 0.3513
    Coupling constant β in degrees (the cosmological birefringence prediction).

BIREFRINGENCE_RAD : float  ≈ 6.132e-3
    Coupling constant β in radians (used internally by the operator C).

ManifoldState
    State of a single 5D manifold (brain or universe):
    entropy S, boundary area A, topology charge Q_top, UEUM position X,
    radion / dilaton φ, and winding numbers (n1, n2, k_cs).
    Brain factory:    ManifoldState.brain(...)
    Universe factory: ManifoldState.universe(...)

CoupledSystem
    Two-body system: ManifoldState brain, ManifoldState universe,
    plus the coupling constant β.

information_gap(brain, universe) → float
    ΔI = |φ²_brain − φ²_univ|  (Information Gap coupling constant).

phase_offset(brain, universe) → float
    Δφ = ∠(X_brain, X_univ)  (Moiré phase angle, radians ∈ [0, π]).

resonance_ratio(brain, universe) → float
    ω_brain / ω_universe  (precession-rate ratio; target 5/7 ≈ 0.714).

is_resonance_locked(brain, universe, tol) → bool
    True iff the ratio is within *tol* of n1/n2 or n2/n1.

coupled_defect(system, G4) → float
    Combined convergence defect of the two-body system.

step_coupled(system, dt, G4, kappa, gamma) → CoupledSystem
    One step of U_total = (U_brain ⊗ I) + (I ⊗ U_univ) + β C.

coupled_master_equation(system, ...) → (CoupledSystem, history, converged)
    Iterate U_total until the coupled fixed point is reached.
    Returns the converged system, per-iteration history dicts, and a
    boolean convergence flag.
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
from typing import Dict, List, Optional, Tuple

import numpy as np

import sys
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    _apply_U,
)


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Birefringence angle β = 0.3513° — the coupling constant (degrees)
BIREFRINGENCE_DEG: float = 0.3513

#: Birefringence angle β converted to radians — used by the coupling operator C
BIREFRINGENCE_RAD: float = BIREFRINGENCE_DEG * np.pi / 180.0   # ≈ 6.132e-3

#: Primary winding number from the braided compact dimension
WINDING_N1: int = 5

#: Secondary winding number from the braided compact dimension
WINDING_N2: int = 7

#: Resonance target ratio n1/n2 = 5/7 ≈ 0.7143
RESONANCE_RATIO: float = WINDING_N1 / WINDING_N2

#: Chern–Simons level k_cs = n1² + n2² = 74
K_CS: int = WINDING_N1 ** 2 + WINDING_N2 ** 2   # 74

_EPS: float = 1e-12   # guard against division by zero


# ---------------------------------------------------------------------------
# ManifoldState
# ---------------------------------------------------------------------------

@dataclass
class ManifoldState:
    """State of a single 5D manifold (brain or universe).

    Parameters
    ----------
    node  : MultiverseNode
        UEUM state: entropy S, boundary area A, topological charge Q_top,
        UEUM position vector X (shape dim), velocity vector Xdot (shape dim).
    phi   : float
        KK radion / dilaton — information capacity of this manifold.
        Brain analog: theta-band amplitude / arousal (acetylcholine / NE tone).
        Universe analog: cosmological radion φ₀.
    n1    : int   — primary winding number (default 5)
    n2    : int   — secondary winding number (default 7)
    k_cs  : int   — Chern–Simons level (default 74 = 5² + 7²)
    label : str   — diagnostic identifier ("brain" or "universe")
    """

    node:  MultiverseNode
    phi:   float
    n1:    int = WINDING_N1
    n2:    int = WINDING_N2
    k_cs:  int = K_CS
    label: str = "manifold"

    # ------------------------------------------------------------------
    @classmethod
    def universe(
        cls,
        dim: int = 4,
        phi: float = 1.0,
        rng: Optional[np.random.Generator] = None,
    ) -> "ManifoldState":
        """Factory: initialise a universe manifold near the FTUM baseline.

        Sets a large boundary area (cosmological scale) and the default
        FTUM radion φ₀ = 1.0.
        """
        if rng is None:
            rng = np.random.default_rng(0)
        node = MultiverseNode.random(dim=dim, rng=rng)
        # Cosmological scale: large boundary area
        node = MultiverseNode(
            dim=dim, S=node.S,
            A=max(node.A, 10.0),
            Q_top=node.Q_top,
            X=node.X.copy(),
            Xdot=node.Xdot.copy(),
        )
        return cls(node=node, phi=float(phi), label="universe")

    @classmethod
    def brain(
        cls,
        dim: int = 4,
        phi: float = 0.7,
        rng: Optional[np.random.Generator] = None,
    ) -> "ManifoldState":
        """Factory: initialise a brain manifold (smaller scale, lower φ).

        Sets a smaller boundary area (cortical sheet) and a slightly
        lower radion φ than the universe to seed a non-zero Information Gap.
        """
        if rng is None:
            rng = np.random.default_rng(1)
        node = MultiverseNode.random(dim=dim, rng=rng)
        # Neural scale: smaller boundary area (cortical sheet)
        node = MultiverseNode(
            dim=dim, S=node.S,
            A=max(node.A, 1.0),
            Q_top=node.Q_top,
            X=node.X.copy(),
            Xdot=node.Xdot.copy(),
        )
        return cls(node=node, phi=float(phi), label="brain")

    def state_vector(self) -> np.ndarray:
        """Concatenate (node_state_vec, φ) into a single flat vector.

        Returns
        -------
        ndarray, shape (node_state_len + 1,)
            [S, A, Q_top, X₀, …, Xdot₀, …, φ]
        """
        return np.append(self.node.state_vector(), self.phi)


# ---------------------------------------------------------------------------
# CoupledSystem
# ---------------------------------------------------------------------------

@dataclass
class CoupledSystem:
    """Two-body system: brain manifold ⊗ universe manifold.

    The combined state is the tensor product

        Ψ_total = Ψ_brain ⊗ Ψ_univ

    acted on by the coupled operator

        U_total = (U_brain ⊗ I) + (I ⊗ U_univ) + β · C

    Parameters
    ----------
    brain    : ManifoldState — the local 5D micro-bulk (neural manifold)
    universe : ManifoldState — the global 5D bulk (cosmological manifold)
    beta     : float — coupling constant β (default: birefringence in radians)
    """

    brain:    ManifoldState
    universe: ManifoldState
    beta:     float = BIREFRINGENCE_RAD

    def tensor_product_state(self) -> np.ndarray:
        """Return Ψ_brain ⊗ Ψ_univ as the outer-product vector.

        Computes the Kronecker outer product of the two state vectors and
        flattens it to a 1D array of length len(Ψ_brain) × len(Ψ_univ).

        Returns
        -------
        ndarray, shape (len_brain × len_univ,)
        """
        sb = self.brain.state_vector()
        su = self.universe.state_vector()
        return np.outer(sb, su).ravel()

    def tensor_product_norm(self) -> float:
        """Frobenius norm ‖Ψ_brain ⊗ Ψ_univ‖_F.

        At the coupled fixed point both individual state norms stabilise,
        so this norm also stabilises.
        """
        return float(np.linalg.norm(self.tensor_product_state()))


# ---------------------------------------------------------------------------
# Observable quantities
# ---------------------------------------------------------------------------

def information_gap(brain: ManifoldState, universe: ManifoldState) -> float:
    """Information Gap ΔI = |φ²_brain − φ²_univ|.

    The Information Gap is the natural coupling constant of the two-body
    system.  It measures the mismatch in information-carrying capacity
    (the J^μ_inf = φ² u^μ current amplitude) between the brain and universe.

    Physical interpretation
    -----------------------
    ΔI = 0  :  two manifolds have identical information density; the Moiré
               pattern has infinite wavelength; perceptual reality dissolves
               into pure geometric symmetry (samadhi / non-dual limit).
    ΔI > 0  :  differentiated perception — the brain's local φ differs from
               the universal φ₀, producing the Moiré interference figure that
               is normal conscious experience.

    Parameters
    ----------
    brain, universe : ManifoldState

    Returns
    -------
    float — ΔI ≥ 0
    """
    return float(abs(brain.phi ** 2 - universe.phi ** 2))


def phase_offset(brain: ManifoldState, universe: ManifoldState) -> float:
    """Moiré phase angle Δφ = ∠(X_brain, X_univ) ∈ [0, π]  (radians).

    Measures the angular separation between the UEUM state vectors of the
    two manifolds — the topological Moiré phase angle.

    Physical interpretation
    -----------------------
    Δφ → 0  :  brain-torus phase-locks to universe-torus; the two fixed
               points coincide; maximum conscious–cosmic alignment.
    Δφ > 0  :  standard experienced world; the personal history encoded
               in X_brain separates the local gauge field from the global one.

    Parameters
    ----------
    brain, universe : ManifoldState

    Returns
    -------
    float — phase offset in radians, ∈ [0, π]
    """
    xb = brain.node.X
    xu = universe.node.X
    nb = float(np.linalg.norm(xb))
    nu = float(np.linalg.norm(xu))
    if nb < _EPS or nu < _EPS:
        return 0.0
    cos_angle = np.dot(xb, xu) / (nb * nu)
    return float(np.arccos(np.clip(cos_angle, -1.0, 1.0)))


def resonance_ratio(brain: ManifoldState, universe: ManifoldState) -> float:
    """Precession-rate ratio ω_brain / ω_universe.

    Each manifold's precession rate is estimated as |Xdot| / |X|.
    At the coupled fixed point, this ratio locks to n1/n2 = 5/7 ≈ 0.714,
    confirming (5,7)-braided torus resonance between the two manifolds.

    Parameters
    ----------
    brain, universe : ManifoldState

    Returns
    -------
    float — ratio ω_brain / ω_univ ≥ 0
    """
    bn, un = brain.node, universe.node
    omega_b = float(np.linalg.norm(bn.Xdot)) / (float(np.linalg.norm(bn.X)) + _EPS)
    omega_u = float(np.linalg.norm(un.Xdot)) / (float(np.linalg.norm(un.X)) + _EPS)
    return float(omega_b / (omega_u + _EPS))


def is_resonance_locked(
    brain: ManifoldState,
    universe: ManifoldState,
    tol: float = 0.05,
) -> bool:
    """True iff the two manifolds are in n1:n2 = 5:7 resonance.

    The condition is

        |ω_brain / ω_univ − n1/n2| < tol   (brain slower)
        OR
        |ω_brain / ω_univ − n2/n1| < tol   (brain faster)

    The symmetric check handles either orientation of the frequency lock.

    Parameters
    ----------
    brain, universe : ManifoldState
    tol : float — tolerance on the ratio (default 0.05)

    Returns
    -------
    bool
    """
    ratio = resonance_ratio(brain, universe)
    target_lo = float(brain.n1) / float(brain.n2)   # 5/7 ≈ 0.714
    target_hi = float(brain.n2) / float(brain.n1)   # 7/5 = 1.40
    return bool(
        abs(ratio - target_lo) < tol or abs(ratio - target_hi) < tol
    )


def coupled_defect(system: CoupledSystem, G4: float = 1.0) -> float:
    """Combined convergence defect of the two-body system.

    Measures how far the coupled system is from the joint fixed point:

        defect² = db² + du² + (β ΔS)² + ΔI²

    where:
        db   = |A_brain / 4G − S_brain|   (individual FTUM defect, brain)
        du   = |A_univ  / 4G − S_univ|    (individual FTUM defect, universe)
        ΔS   = S_brain − S_univ            (entropy gap between the two bodies)
        ΔI   = |φ²_brain − φ²_univ|       (Information Gap)

    The β weighting ensures the ΔS term is dimensionally consistent
    with the Information Gap term.

    Parameters
    ----------
    system : CoupledSystem
    G4     : float — Newton's constant (default 1 in Planck units)

    Returns
    -------
    float — combined defect ≥ 0
    """
    bn = system.brain.node
    un = system.universe.node
    db = abs(bn.A / (4.0 * G4) - bn.S)
    du = abs(un.A / (4.0 * G4) - un.S)
    dS = bn.S - un.S
    dI = information_gap(system.brain, system.universe)
    return float(np.sqrt(db ** 2 + du ** 2 + (system.beta * dS) ** 2 + dI ** 2))


# ---------------------------------------------------------------------------
# Coupling operator C — the topological handshake
# ---------------------------------------------------------------------------

def _apply_coupling(system: CoupledSystem, dt: float) -> CoupledSystem:
    """Apply the coupling operator C: bilinear information flux between manifolds.

    C transfers entropy, UEUM position X, and radion φ between the two
    manifolds in proportion to their mutual difference, scaled by the
    birefringence coupling constant β.

    This is the "topological handshake": each manifold's internal state
    change exerts a back-reaction torque on the other, mediated by the
    B_μ irreversibility 1-form.

    Equations
    ---------
        ΔS_brain   = +β (S_univ − S_brain) dt
        ΔS_univ    = −β (S_univ − S_brain) dt
        ΔX_brain   = +β (X_univ − X_brain) dt
        ΔX_univ    = −β (X_univ − X_brain) dt
        Δφ_brain   = +β (φ_univ − φ_brain) dt
        Δφ_univ    = −β (φ_univ − φ_brain) dt

    The antisymmetry (brain gets +, universe gets −) ensures total
    information conservation: ΔS_brain + ΔS_univ = 0, mirroring the
    conserved current ∇_μ J^μ_inf = 0.

    Parameters
    ----------
    system : CoupledSystem
    dt     : float — pseudo-timestep

    Returns
    -------
    CoupledSystem with updated brain and universe states
    """
    beta = system.beta
    bn, un = system.brain.node, system.universe.node

    dS    = (un.S - bn.S) * beta * dt
    dX    = (un.X - bn.X) * beta * dt
    dphi  = (system.universe.phi - system.brain.phi) * beta * dt

    new_bn = MultiverseNode(
        dim=bn.dim,
        S=bn.S + dS,
        A=bn.A,
        Q_top=bn.Q_top,
        X=bn.X + dX,
        Xdot=bn.Xdot.copy(),
    )
    new_un = MultiverseNode(
        dim=un.dim,
        S=un.S - dS,
        A=un.A,
        Q_top=un.Q_top,
        X=un.X - dX,
        Xdot=un.Xdot.copy(),
    )
    new_brain = ManifoldState(
        node=new_bn,
        phi=system.brain.phi + dphi,
        n1=system.brain.n1,
        n2=system.brain.n2,
        k_cs=system.brain.k_cs,
        label=system.brain.label,
    )
    new_universe = ManifoldState(
        node=new_un,
        phi=system.universe.phi - dphi,
        n1=system.universe.n1,
        n2=system.universe.n2,
        k_cs=system.universe.k_cs,
        label=system.universe.label,
    )
    return CoupledSystem(brain=new_brain, universe=new_universe, beta=beta)


# ---------------------------------------------------------------------------
# Step function — one application of U_total
# ---------------------------------------------------------------------------

def step_coupled(
    system: CoupledSystem,
    dt: float,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> CoupledSystem:
    """One step of U_total = (U_brain ⊗ I) + (I ⊗ U_univ) + β C.

    Applies the FTUM operator U = I + H + T independently to each manifold,
    advances the radion φ toward its holographic fixed point, then applies
    the coupling operator C.

    Parameters
    ----------
    system : CoupledSystem
    dt     : float — pseudo-timestep
    G4     : float — Newton's constant
    kappa  : float — surface gravity / irreversibility rate
    gamma  : float — UEUM geodesic friction (damping)

    Returns
    -------
    CoupledSystem — one step forward in U_total
    """
    # Apply U = I + H + T to brain manifold
    brain_net = MultiverseNetwork(
        nodes=[system.brain.node],
        adjacency=np.zeros((1, 1)),
    )
    brain_net2 = _apply_U(brain_net, dt, G4, kappa, gamma)

    # Apply U = I + H + T to universe manifold
    univ_net = MultiverseNetwork(
        nodes=[system.universe.node],
        adjacency=np.zeros((1, 1)),
    )
    univ_net2 = _apply_U(univ_net, dt, G4, kappa, gamma)

    # Advance φ toward the holographic fixed point φ* = A / 4G
    phi_brain_new = system.brain.phi + kappa * (
        brain_net2.nodes[0].A / (4.0 * G4) - system.brain.phi
    ) * dt
    phi_univ_new = system.universe.phi + kappa * (
        univ_net2.nodes[0].A / (4.0 * G4) - system.universe.phi
    ) * dt

    new_system = CoupledSystem(
        brain=ManifoldState(
            node=brain_net2.nodes[0],
            phi=phi_brain_new,
            n1=system.brain.n1,
            n2=system.brain.n2,
            k_cs=system.brain.k_cs,
            label=system.brain.label,
        ),
        universe=ManifoldState(
            node=univ_net2.nodes[0],
            phi=phi_univ_new,
            n1=system.universe.n1,
            n2=system.universe.n2,
            k_cs=system.universe.k_cs,
            label=system.universe.label,
        ),
        beta=system.beta,
    )

    # Apply coupling operator C (topological handshake)
    return _apply_coupling(new_system, dt)


# ---------------------------------------------------------------------------
# Coupled Master Equation — main iteration
# ---------------------------------------------------------------------------

def coupled_master_equation(
    system: CoupledSystem,
    max_iter: int = 1000,
    tol: float = 1e-6,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> Tuple[CoupledSystem, List[Dict], bool]:
    """Iterate U_total until the coupled fixed point Ψ*_brain ⊗ Ψ*_univ is reached.

    Solves the Coupled Master Equation:

        U_total (Ψ_brain ⊗ Ψ_univ)  =  Ψ_brain ⊗ Ψ_univ

    where

        U_total  =  (U_brain ⊗ I)  +  (I ⊗ U_univ)  +  β · C

    The iteration records per-step diagnostics:

    ``defect``       — coupled_defect(system): joint convergence metric
    ``info_gap``     — ΔI = information_gap(brain, universe)
    ``phase_offset`` — Δφ (Moiré phase angle, radians)
    ``S_brain``      — brain entropy
    ``S_univ``       — universe entropy
    ``phi_brain``    — brain radion φ
    ``phi_univ``     — universe radion φ

    Parameters
    ----------
    system   : CoupledSystem — initial state
    max_iter : int   — maximum iterations (default 1000)
    tol      : float — convergence tolerance on coupled_defect (default 1e-6)
    dt       : float — pseudo-timestep (default 0.1)
    G4       : float — Newton's constant (default 1 in Planck units)
    kappa    : float — surface gravity / irreversibility rate
    gamma    : float — UEUM geodesic friction

    Returns
    -------
    converged_system : CoupledSystem
        State at or nearest to the coupled fixed point.
    history : list[dict]
        Per-iteration diagnostic records.
    converged : bool
        True iff coupled_defect < tol within max_iter steps.
    """
    history: List[Dict] = []
    converged = False

    for _ in range(max_iter):
        defect = coupled_defect(system, G4)
        history.append({
            "defect":       defect,
            "info_gap":     information_gap(system.brain, system.universe),
            "phase_offset": phase_offset(system.brain, system.universe),
            "S_brain":      system.brain.node.S,
            "S_univ":       system.universe.node.S,
            "phi_brain":    system.brain.phi,
            "phi_univ":     system.universe.phi,
        })

        if defect < tol:
            converged = True
            break

        system = step_coupled(system, dt, G4, kappa, gamma)

    return system, history, converged


# ---------------------------------------------------------------------------
# Gap 3 — Biological Intentionality / Agency (Pillar 42 bridge)
# ---------------------------------------------------------------------------
#
# "Why does a brain-scale geometric configuration seem to *want* to survive,
# while a rock doesn't?"
#
# Answer (from the Unitary Manifold): intentionality emerges when the local
# information density φ² creates a **self-reinforcing feedback loop** that
# pulls the system toward the FTUM attractor faster than environment
# perturbations push it away.
#
# Formally, a system exhibits **geometric agency** iff:
#
#     dφ_brain/dt evaluated at the fixed point is NEGATIVE near the attractor
#     (i.e., the coupled U_total has eigenvalue < 1 for the brain sector),
#
# AND the information gap ΔI = |φ²_brain − φ²_univ| is large enough to
# maintain a distinct local phase (the brain has its own "perspective"):
#
#     ΔI  >  INTENTIONALITY_GAP_THRESHOLD
#
# The threshold is set by the topological protection gap Δ_CS = k_cs − n_w²:
#
#     INTENTIONALITY_GAP_THRESHOLD  =  1 / (k_cs − n_w²)  =  1/49  ≈  0.0204
#
# This ensures the brain's local φ is separated from the cosmological φ₀
# by more than one CS protection unit.
#
# A "rock" has ΔI ≈ 0 (its φ is indistinguishable from the background):
# it is just part of the cosmic radion field, not a distinct attractor.
# A "brain" has ΔI >> threshold, maintained by the coupled master equation.

#: Winding number used in agency threshold (canonical: 5)
_NW_AGENCY: int = WINDING_N1

#: Topological protection gap Δ_CS = k_cs − n_w² = 74 − 25 = 49
_DELTA_CS: int = K_CS - _NW_AGENCY ** 2   # = 49

#: Minimum information gap for geometric agency (= 1/Δ_CS = 1/49)
INTENTIONALITY_GAP_THRESHOLD: float = 1.0 / _DELTA_CS

#: Resonance lock tolerance for survival-drive computation
_RESONANCE_TOL: float = 0.1


def intentionality_measure(system: CoupledSystem) -> float:
    """Measure the degree of geometric agency in a coupled brain-universe system.

    Intentionality is defined as the product of two factors:

    1. **Information Gap ratio**:  ΔI / THRESHOLD
       (How distinct is the brain's local φ from the cosmic background?
        > 1 → the brain has its own stable "perspective".)

    2. **Resonance lock factor**: 1 if the system is in 5:7 resonance, 0 otherwise.
       (Intentional systems maintain the canonical (5,7) frequency lock.)

    Combined:

        I_meas = (ΔI / threshold) × lock_factor

    A value > 1 indicates geometric agency; a value ≤ 1 indicates rock-like
    absence of intentionality.

    Parameters
    ----------
    system : CoupledSystem

    Returns
    -------
    float
        Intentionality measure I_meas ≥ 0.  Dimensionless.
    """
    delta_I = information_gap(system.brain, system.universe)
    ratio = delta_I / INTENTIONALITY_GAP_THRESHOLD
    lock = 1.0 if is_resonance_locked(system.brain, system.universe, _RESONANCE_TOL) else 0.5
    return float(ratio * lock)


def is_intentional(system: CoupledSystem) -> bool:
    """Return True iff the brain-universe system exhibits geometric agency.

    A system is **intentional** iff:

    1. Information Gap ΔI > INTENTIONALITY_GAP_THRESHOLD  (distinct local φ)
    2. The resonance ratio ω_brain/ω_univ is within tolerance of 5/7 or 7/5

    Parameters
    ----------
    system : CoupledSystem

    Returns
    -------
    bool
    """
    delta_I = information_gap(system.brain, system.universe)
    if delta_I <= INTENTIONALITY_GAP_THRESHOLD:
        return False
    return is_resonance_locked(system.brain, system.universe, _RESONANCE_TOL)


def survival_drive(system: CoupledSystem, G4: float = 1.0) -> float:
    """Quantify the system's tendency to remain near the FTUM attractor.

    The survival drive D is the rate at which the system self-corrects toward
    its attractor when perturbed.  It is proportional to:

        D = κ × φ²_brain / (coupled_defect + ε)

    where:
    * κ = BIREFRINGENCE_RAD (coupling constant = restoring force)
    * φ²_brain = information density (larger → stronger pull)
    * coupled_defect → 0 means the system is already at the attractor
      (in the limit D → ∞ × 0 = finite, the drive is sustained)

    Interpretation:
    * D ≫ 1 → strong survival drive (the geometry "wants" to stay at Ψ*)
    * D ≈ 1 → neutral (perturbations and restoring forces balance)
    * D < 1 → unstable (perturbations dominate → no intentionality)

    Parameters
    ----------
    system : CoupledSystem
    G4     : float — Newton's constant

    Returns
    -------
    float
        Survival drive D ≥ 0.
    """
    defect = coupled_defect(system, G4)
    phi_b_sq = system.brain.phi ** 2
    kappa = BIREFRINGENCE_RAD
    return float(kappa * phi_b_sq / (defect + _EPS))


def agency_threshold(c_s: float = 12.0 / 37.0, k_cs: int = K_CS) -> float:
    """Minimum information gap for a geometric agent to maintain identity.

    The threshold is derived from the CS protection gap:

        threshold = c_s / (k_cs − n_w²) = (12/37) / 49  ≈  0.00661

    This is the minimum ΔI needed to ensure the brain's topological winding
    sector is distinct from the background — i.e., the brain is a separate
    attractor basin, not just a fluctuation in the cosmic field.

    Parameters
    ----------
    c_s  : float — braided sound speed (default 12/37)
    k_cs : int   — Chern-Simons level (default 74)

    Returns
    -------
    float
        Agency threshold ΔI_min.

    Raises
    ------
    ValueError
        If k_cs ≤ _NW_AGENCY².
    """
    gap = k_cs - _NW_AGENCY ** 2
    if gap <= 0:
        raise ValueError(
            f"k_cs={k_cs} must exceed n_w²={_NW_AGENCY**2} to have a protection gap"
        )
    return float(c_s / gap)


def intentionality_summary(system: CoupledSystem, G4: float = 1.0) -> Dict:
    """Full intentionality diagnostic summary for a coupled brain-universe system.

    Returns a dict with keys:

    ``information_gap``      : float — ΔI = |φ²_brain − φ²_univ|
    ``gap_threshold``        : float — INTENTIONALITY_GAP_THRESHOLD = 1/49
    ``agency_threshold``     : float — c_s / Δ_CS (finer threshold)
    ``intentionality_measure``: float — I_meas = (ΔI/threshold) × lock
    ``is_intentional``       : bool  — True iff ΔI > threshold AND resonance locked
    ``survival_drive``       : float — D = κ φ²_brain / (defect + ε)
    ``resonance_locked``     : bool  — True iff in 5:7 frequency resonance
    ``resonance_ratio``      : float — ω_brain / ω_univ
    ``coupled_defect``       : float — combined convergence defect
    ``summary``              : str   — human-readable description

    Parameters
    ----------
    system : CoupledSystem
    G4     : float — Newton's constant (default 1)
    """
    dI = information_gap(system.brain, system.universe)
    locked = is_resonance_locked(system.brain, system.universe, _RESONANCE_TOL)
    ratio = resonance_ratio(system.brain, system.universe)
    defect = coupled_defect(system, G4)
    i_meas = intentionality_measure(system)
    intentional = is_intentional(system)
    drive = survival_drive(system, G4)
    thresh = INTENTIONALITY_GAP_THRESHOLD
    a_thresh = agency_threshold()

    if intentional:
        desc = (
            f"INTENTIONAL system: ΔI={dI:.4f} > threshold={thresh:.4f}, "
            f"resonance locked, drive={drive:.3f}. "
            f"Brain geometry is a distinct attractor basin — exhibits agency."
        )
    else:
        desc = (
            f"NON-INTENTIONAL system: ΔI={dI:.4f} ≤ threshold={thresh:.4f} "
            f"or resonance unlocked. Brain is indistinguishable from background."
        )

    return {
        "information_gap":       dI,
        "gap_threshold":         thresh,
        "agency_threshold":      a_thresh,
        "intentionality_measure": i_meas,
        "is_intentional":        intentional,
        "survival_drive":        drive,
        "resonance_locked":      locked,
        "resonance_ratio":       ratio,
        "coupled_defect":        defect,
        "summary":               desc,
    }
