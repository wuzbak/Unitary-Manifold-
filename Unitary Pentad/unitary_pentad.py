# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/unitary_pentad.py
=================================
The Unitary Pentad — 5-body HILS Coupled Master Equation.

Background
----------
The 2-body (brain ⊗ universe) system of ``coupled_attractor.py`` is a special
case of a more general *n-body* problem.  The Unitary Manifold architecture
selects **n = 5** on both physical and topological grounds:

    1. The (5, 7)-braid compact dimension has winding number n₁ = 5,
       making pentagonal symmetry the natural "orbit shell" of the theory.

    2. The HILS (Human–Intelligence–Life–System) framework identifies five
       distinct interactive manifolds whose mutual calibration is required
       for a stable operational reality:

          Body 1 — Ψ_univ  : The 5D Physical Manifold
                              Governed by the Walker-Pearson field equations;
                              source of the (5,7) braid irreversibility.

          Body 2 — Ψ_brain  : The Biological Observer
                              Neural integration / predictive coding;
                              implements the grid-cell 7:5 module spacing.

          Body 3 — Ψ_human  : The Intent Layer
                              Semantic direction / judgment / agency;
                              the source of intentional causal structure.

          Body 4 — Ψ_AI     : The Operational Precision
                              The "Truth Machine" / implementation substrate;
                              error-correcting verification and execution.

          Body 5 — β·C      : The Trust / Coupling Field
                              The medium that allows bodies 1–4 to maintain
                              stable co-orbit.  β is the birefringence coupling
                              constant; C is the bilinear coupling operator.

    3. In a pentagonal topology each node must be calibrated to its **four**
       neighbours simultaneously — analogous to the 4-body (n₁ = 4) limit in
       classical mechanics, but now resolved by the (5,7) braid frequency.

The Pentagonal Master Equation
-------------------------------
The 5-body combined state is the 5-fold tensor product:

    Ψ_pentad = Ψ_univ ⊗ Ψ_brain ⊗ Ψ_human ⊗ Ψ_AI ⊗ Ψ_trust

acted on by the Pentagonal Operator:

    U_pentad = Σᵢ (Uᵢ ⊗ I⊗others) + β_eff · C_pentad

where

    C_pentad = Σᵢ Σⱼ≠ᵢ τ_{ij} · C_{ij}

and τ_{ij} is the trust-modulation matrix defined below.

Trust Modulation
----------------
The Trust field (body 5) plays a special mediating role: its radion φ_trust
modulates the effective coupling between every pair of the other four bodies:

    τ_{ij} = β × φ_trust   for bodies i, j ∈ {univ, brain, human, ai}
    τ_{i,trust} = β        for couplings to/from the trust field itself

This ensures that when φ_trust → 0 (total loss of trust), bodies 1–4 decouple
and the pentagonal orbit disintegrates.  When φ_trust → 1 (default), the
coupling reduces to the 2-body birefringence constant β.

Pentagonal Stability — the (5,7) Connection
--------------------------------------------
The braided sound speed c_s = 12/37 ≈ 0.324 from the (5,7) resonance is the
suppression factor that keeps the 5-body tensor-to-scalar ratio within bounds.
By the same token, the 5-way pentagonal coupling matrix has eigenvalues that
are bounded from below by c_s, guaranteeing that no single pairwise coupling
can drive a run-away instability.  This is the topological content of the
statement "n_w = 5 is the magic number."

Convergence conditions at the Pentad fixed point
-------------------------------------------------
    1. Individual FTUM defect of each body < tol
    2. All pairwise Information Gaps ΔI_{ij} → 0
    3. All pairwise phase offsets Δφ_{ij} → 0   (Moiré alignment)
    4. Trust modulation φ_trust > φ_trust_min    (trust floor preserved)

Public API
----------
PentadLabel : str constants
    UNIV = "univ", BRAIN = "brain", HUMAN = "human", AI = "ai",
    TRUST = "trust".

PENTAD_LABELS : tuple[str, ...]
    Ordered tuple of the 5 label strings.

PentadSystem
    5-body system: dict[label → ManifoldState], plus coupling constant β,
    and optional grace-period fields (grace_steps, grace_decay,
    _trust_reservoir, _grace_elapsed) for Trust Hysteresis.
    Factory: PentadSystem.default(dim, rng)

pentad_pairwise_gaps(system) → dict[tuple[str,str], float]
    All C(5,2) = 10 pairwise Information Gaps ΔI_{ij}.

pentad_pairwise_phases(system) → dict[tuple[str,str], float]
    All 10 pairwise Moiré phase angles.

trust_modulation(system) → float
    Effective trust-modulation factor φ_trust ∈ [0, 1].
    When grace_steps > 0, returns max(live_phi, reservoir × exp(-k × elapsed))
    so the coupling field decays slowly rather than collapsing instantly when
    the human element becomes erratic.

tick_grace_period(system) → PentadSystem
    Advance the grace-period state machine by one step.  Called automatically
    by step_pentad.  No-op when grace_steps == 0.

pentad_defect(system, G4) → float
    Combined 5-body convergence defect (RMS of 5 individual FTUM defects
    plus pairwise Information Gap and phase terms).

_apply_pentagonal_coupling(system, dt) → PentadSystem
    Apply the full pentagonal coupling operator C_pentad.

step_pentad(system, dt, G4, kappa, gamma) → PentadSystem
    One step of U_pentad: apply U_i to each body, then C_pentad, then
    tick_grace_period.

pentad_master_equation(system, ...) → (PentadSystem, list[dict], bool)
    Iterate U_pentad until the pentad fixed point is reached.

pentad_eigenspectrum(system) → np.ndarray
    Eigenvalues of the 5×5 pairwise coupling matrix (stability analysis).
    At the braided fixed point the minimum eigenvalue ≥ c_s = 12/37.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Tuple

import numpy as np

import sys
import os

# Ensure the repository root is on the path so src.* imports resolve.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    _apply_U,
)
from src.consciousness.coupled_attractor import (
    BIREFRINGENCE_DEG,
    BIREFRINGENCE_RAD,
    WINDING_N1,
    WINDING_N2,
    K_CS,
    ManifoldState,
)
from src.core.braided_winding import braided_sound_speed


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Braided sound speed c_s = 12/37 — pentagonal stability lower bound.
BRAIDED_SOUND_SPEED: float = braided_sound_speed(WINDING_N1, WINDING_N2, K_CS)

#: Minimum trust modulation (φ_trust floor) — below this the pentad is unstable.
TRUST_PHI_MIN: float = 0.1

_EPS: float = 1e-12


# ---------------------------------------------------------------------------
# Pentad labels
# ---------------------------------------------------------------------------

class PentadLabel:
    """String constants for the 5 HILS manifold bodies."""
    UNIV  = "univ"   #: 5D Physical Manifold — source of (5,7) braid
    BRAIN = "brain"  #: Biological Observer — neural integration
    HUMAN = "human"  #: Intent Layer — semantic direction / judgment
    AI    = "ai"     #: Operational Precision — truth machine / implementation
    TRUST = "trust"  #: Trust / Coupling Field — stabilising medium


#: Canonical ordering of the 5 pentad bodies.
PENTAD_LABELS: Tuple[str, ...] = (
    PentadLabel.UNIV,
    PentadLabel.BRAIN,
    PentadLabel.HUMAN,
    PentadLabel.AI,
    PentadLabel.TRUST,
)


# ---------------------------------------------------------------------------
# Factory helpers — default ManifoldState per body
# ---------------------------------------------------------------------------

def _make_manifold(
    label: str,
    dim: int,
    phi: float,
    area_min: float,
    seed: int,
) -> ManifoldState:
    """Create a ManifoldState for a named pentad body."""
    rng = np.random.default_rng(seed)
    node = MultiverseNode.random(dim=dim, rng=rng)
    node = MultiverseNode(
        dim=dim, S=node.S,
        A=max(node.A, area_min),
        Q_top=node.Q_top,
        X=node.X.copy(),
        Xdot=node.Xdot.copy(),
    )
    return ManifoldState(node=node, phi=float(phi), label=label)


# Body-specific defaults: (phi, area_min, seed)
_BODY_DEFAULTS: Dict[str, Tuple[float, float, int]] = {
    PentadLabel.UNIV:  (1.00, 10.0, 0),   # cosmological scale, φ₀ = 1
    PentadLabel.BRAIN: (0.70,  1.0, 1),   # neural scale, lower φ
    PentadLabel.HUMAN: (0.60,  0.8, 2),   # intent layer, intentional asymmetry
    PentadLabel.AI:    (0.80,  1.5, 3),   # high precision, moderate area
    PentadLabel.TRUST: (0.90,  2.0, 4),   # trust field, near-unity φ
}


# ---------------------------------------------------------------------------
# PentadSystem
# ---------------------------------------------------------------------------

@dataclass
class PentadSystem:
    """5-body Unitary Pentad system.

    Parameters
    ----------
    bodies : dict[str, ManifoldState]
        Mapping from PentadLabel constant → ManifoldState.
        Must contain exactly the 5 keys in PENTAD_LABELS.
    beta   : float
        Base coupling constant β (default: birefringence in radians).
    grace_steps : int
        Number of pseudo-timesteps the Trust Reservoir ("grace period") lasts
        after φ_trust drops below TRUST_PHI_MIN.  0 (default) disables
        hysteresis — trust_modulation reads the live φ_trust directly.
    grace_decay : float
        Exponential decay constant k in the reservoir formula
        ``φ_reservoir × exp(-k × elapsed)``.  Only used when grace_steps > 0.
    _trust_reservoir : float
        Internal — last "good" φ_trust value captured while trust was healthy.
        Automatically maintained by tick_grace_period / step_pentad.
    _grace_elapsed : int
        Internal — number of steps since trust last dropped below TRUST_PHI_MIN.
        Reset to 0 whenever trust recovers.
    """

    bodies: Dict[str, ManifoldState]
    beta:   float = BIREFRINGENCE_RAD
    grace_steps:      int   = 0
    grace_decay:      float = 0.2
    _trust_reservoir: float = field(default=1.0, repr=False)
    _grace_elapsed:   int   = field(default=0,   repr=False)

    def __post_init__(self) -> None:
        missing = set(PENTAD_LABELS) - set(self.bodies)
        if missing:
            raise ValueError(f"PentadSystem missing bodies: {missing}")

    # ------------------------------------------------------------------
    @classmethod
    def default(
        cls,
        dim: int = 4,
        beta: float = BIREFRINGENCE_RAD,
        rng: Optional[np.random.Generator] = None,
    ) -> "PentadSystem":
        """Factory: create a default pentad with canonical initial conditions.

        Each body is seeded at its physically motivated initial φ and
        boundary area, with a small random perturbation from its seed.

        Parameters
        ----------
        dim  : int — UEUM dimension (default 4)
        beta : float — base coupling constant (default: birefringence)
        rng  : optional master RNG (unused; body seeds are deterministic)
        """
        bodies: Dict[str, ManifoldState] = {}
        for label in PENTAD_LABELS:
            phi, area_min, seed = _BODY_DEFAULTS[label]
            bodies[label] = _make_manifold(label, dim, phi, area_min, seed)
        return cls(bodies=bodies, beta=beta)

    def __getitem__(self, label: str) -> ManifoldState:
        return self.bodies[label]

    def state_matrix(self) -> np.ndarray:
        """Stack all 5 state vectors into a (5, state_len) matrix.

        Returns
        -------
        ndarray, shape (5, state_len)
            Row i is the state vector of PENTAD_LABELS[i].
        """
        rows = [self.bodies[lbl].state_vector() for lbl in PENTAD_LABELS]
        return np.vstack(rows)

    def tensor_product_norm(self) -> float:
        """Frobenius norm of the 5-body state matrix."""
        return float(np.linalg.norm(self.state_matrix()))


# ---------------------------------------------------------------------------
# Observable quantities
# ---------------------------------------------------------------------------

def pentad_pairwise_gaps(
    system: PentadSystem,
) -> Dict[Tuple[str, str], float]:
    """All C(5,2) = 10 pairwise Information Gaps ΔI_{ij} = |φᵢ² − φⱼ²|.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    dict mapping (label_i, label_j) → float (ΔI ≥ 0)
    """
    gaps: Dict[Tuple[str, str], float] = {}
    for li, lj in combinations(PENTAD_LABELS, 2):
        phi_i = system.bodies[li].phi
        phi_j = system.bodies[lj].phi
        gaps[(li, lj)] = float(abs(phi_i ** 2 - phi_j ** 2))
    return gaps


def pentad_pairwise_phases(
    system: PentadSystem,
) -> Dict[Tuple[str, str], float]:
    """All 10 pairwise Moiré phase angles Δφ_{ij} = ∠(Xᵢ, Xⱼ) ∈ [0, π].

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    dict mapping (label_i, label_j) → float (radians ∈ [0, π])
    """
    phases: Dict[Tuple[str, str], float] = {}
    for li, lj in combinations(PENTAD_LABELS, 2):
        xi = system.bodies[li].node.X
        xj = system.bodies[lj].node.X
        ni = float(np.linalg.norm(xi))
        nj = float(np.linalg.norm(xj))
        if ni < _EPS or nj < _EPS:
            phases[(li, lj)] = 0.0
        else:
            cos_a = np.dot(xi, xj) / (ni * nj)
            phases[(li, lj)] = float(np.arccos(np.clip(cos_a, -1.0, 1.0)))
    return phases


def trust_modulation(system: PentadSystem) -> float:
    """Effective trust-modulation factor φ_trust ∈ [0, 1].

    The Trust field body acts as a global amplifier / attenuator of all
    inter-body couplings.  Its radion φ_trust scales the effective coupling
    between the four non-trust bodies.

    When ``system.grace_steps == 0`` (default), the live φ_trust is returned
    directly (original stateless behaviour).

    When ``system.grace_steps > 0`` (Trust Reservoir / Hysteresis active),
    the effective trust is::

        φ_effective = max(live_phi, _trust_reservoir × exp(-grace_decay × _grace_elapsed))

    This prevents the coupling field from collapsing instantly when the human
    element becomes erratic.  The reservoir decays over ``grace_steps`` ticks
    until the human signal re-aligns or the grace window closes.

    Returns
    -------
    float — effective φ_trust clamped to [0, 1].
    """
    live = float(np.clip(system.bodies[PentadLabel.TRUST].phi, 0.0, 1.0))
    if system.grace_steps == 0:
        return live
    reservoir_val = system._trust_reservoir * math.exp(
        -system.grace_decay * system._grace_elapsed
    )
    return float(np.clip(max(live, reservoir_val), 0.0, 1.0))


def tick_grace_period(system: PentadSystem) -> PentadSystem:
    """Advance the grace-period (Trust Reservoir) state machine by one step.

    Called automatically at the end of each ``step_pentad``.  When
    ``grace_steps == 0`` the function is a no-op and returns the system
    unchanged.

    State transitions
    -----------------
    * **Trust healthy** (live φ_trust ≥ TRUST_PHI_MIN):
      Refresh the reservoir to the current live value; reset elapsed counter.
    * **Trust erratic, within grace window** (_grace_elapsed < grace_steps):
      Increment the elapsed counter; keep reservoir value for decay calculation.
    * **Grace exhausted** (_grace_elapsed ≥ grace_steps):
      Stop protecting — the reservoir drains to the live (low) value and the
      elapsed counter is held at its current position.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    PentadSystem — same bodies/β, with updated _trust_reservoir / _grace_elapsed.
    """
    if system.grace_steps == 0:
        return system

    live = float(np.clip(system.bodies[PentadLabel.TRUST].phi, 0.0, 1.0))

    if live >= TRUST_PHI_MIN:
        # Trust is healthy — refresh the reservoir and reset the counter.
        new_reservoir = live
        new_elapsed = 0
    elif system._grace_elapsed < system.grace_steps:
        # Still inside the grace window — advance the decay clock.
        new_reservoir = system._trust_reservoir
        new_elapsed = system._grace_elapsed + 1
    else:
        # Grace exhausted — let the reservoir drain to the live value.
        new_reservoir = live
        new_elapsed = system._grace_elapsed

    return PentadSystem(
        bodies=system.bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=new_reservoir,
        _grace_elapsed=new_elapsed,
    )


def pentad_coupling_matrix(system: PentadSystem) -> np.ndarray:
    """5×5 symmetric coupling-strength matrix for the pentagonal network.

    Entry (i, j) for i ≠ j gives the effective coupling strength τ_{ij}:

        τ_{ij} = β × φ_trust   if neither i nor j is the trust body
        τ_{i,trust} = β         (trust body always couples at bare β)

    The diagonal is zero (self-coupling excluded).

    Returns
    -------
    ndarray, shape (5, 5)
    """
    n = len(PENTAD_LABELS)
    mat = np.zeros((n, n))
    tau_trust = system.beta
    tau_other = system.beta * trust_modulation(system)
    trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if i == trust_idx or j == trust_idx:
                mat[i, j] = tau_trust
            else:
                mat[i, j] = tau_other
    return mat


def pentad_eigenspectrum(system: PentadSystem) -> np.ndarray:
    """Eigenvalues of the 5×5 pentagonal coupling matrix (stability analysis).

    At the braided fixed point the minimum non-zero eigenvalue is expected
    to satisfy λ_min ≥ c_s = 12/37 ≈ 0.324 (scaled by β), which is the
    topological stability bound from the (5,7) braid resonance.

    Returns
    -------
    ndarray, shape (5,) — eigenvalues sorted ascending.
    """
    mat = pentad_coupling_matrix(system)
    return np.sort(np.linalg.eigvalsh(mat))


def pentad_defect(system: PentadSystem, G4: float = 1.0) -> float:
    """Combined 5-body convergence defect.

    Measures how far the pentad is from its joint fixed point:

        defect² = (1/5) Σᵢ dᵢ²
                + (1/10) Σ_{i<j} ΔI_{ij}²
                + (β Σ_{i<j} Δφ_{ij})²
                + max(0, φ_trust_min − φ_trust)²

    where dᵢ = |Aᵢ / 4G − Sᵢ| is the individual FTUM defect of body i,
    ΔI_{ij} is the pairwise Information Gap, and Δφ_{ij} is the pairwise
    Moiré phase angle.

    The final term penalises trust collapse below TRUST_PHI_MIN.

    Parameters
    ----------
    system : PentadSystem
    G4     : float — Newton's constant (default 1 in Planck units)

    Returns
    -------
    float — combined defect ≥ 0
    """
    # Individual FTUM defects
    d2 = 0.0
    for lbl in PENTAD_LABELS:
        node = system.bodies[lbl].node
        d2 += (abs(node.A / (4.0 * G4) - node.S)) ** 2
    d2 /= len(PENTAD_LABELS)

    # Pairwise Information Gaps
    gaps = pentad_pairwise_gaps(system)
    gap2 = sum(v ** 2 for v in gaps.values()) / len(gaps)

    # Pairwise phase offsets (weighted by β)
    phases = pentad_pairwise_phases(system)
    phase_sum = sum(phases.values())
    phase2 = (system.beta * phase_sum) ** 2

    # Trust floor penalty
    tau = trust_modulation(system)
    trust_penalty = max(0.0, TRUST_PHI_MIN - tau) ** 2

    return float(np.sqrt(d2 + gap2 + phase2 + trust_penalty))


# ---------------------------------------------------------------------------
# Coupling operator — the pentagonal topological handshake
# ---------------------------------------------------------------------------

def _apply_pentagonal_coupling(
    system: PentadSystem,
    dt: float,
) -> PentadSystem:
    """Apply the pentagonal coupling operator C_pentad.

    For each ordered pair (i, j) with i ≠ j the coupling transfer is:

        ΔSᵢ    += τ_{ij} (Sⱼ − Sᵢ) dt
        ΔXᵢ    += τ_{ij} (Xⱼ − Xᵢ) dt
        Δφᵢ    += τ_{ij} (φⱼ − φᵢ) dt

    where τ_{ij} is the trust-modulated coupling from ``pentad_coupling_matrix``.

    The operator is antisymmetric: the total state change sums to zero,
    conserving total entropy, total X, and total φ across all five bodies.

    Parameters
    ----------
    system : PentadSystem
    dt     : float — pseudo-timestep

    Returns
    -------
    PentadSystem with updated body states
    """
    tau = pentad_coupling_matrix(system)

    # Accumulate increments for each body
    dS:  Dict[str, float]      = {lbl: 0.0 for lbl in PENTAD_LABELS}
    dX:  Dict[str, np.ndarray] = {
        lbl: np.zeros_like(system.bodies[lbl].node.X)
        for lbl in PENTAD_LABELS
    }
    dphi: Dict[str, float] = {lbl: 0.0 for lbl in PENTAD_LABELS}

    for idx_i, li in enumerate(PENTAD_LABELS):
        for idx_j, lj in enumerate(PENTAD_LABELS):
            if idx_i == idx_j:
                continue
            t_ij = tau[idx_i, idx_j]
            bi = system.bodies[li]
            bj = system.bodies[lj]
            dS[li]   += t_ij * (bj.node.S - bi.node.S) * dt
            dX[li]   += t_ij * (bj.node.X - bi.node.X) * dt
            dphi[li] += t_ij * (bj.phi - bi.phi) * dt

    # Build new bodies with increments applied
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
# Step function — one application of U_pentad
# ---------------------------------------------------------------------------

def step_pentad(
    system: PentadSystem,
    dt: float,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> PentadSystem:
    """One step of U_pentad = Σᵢ(Uᵢ ⊗ I⊗others) + β_eff · C_pentad.

    Applies the FTUM operator U = I + H + T independently to each of the
    5 manifold bodies, advances each radion φ toward its holographic fixed
    point, then applies the pentagonal coupling operator C_pentad.

    Parameters
    ----------
    system : PentadSystem
    dt     : float — pseudo-timestep
    G4     : float — Newton's constant
    kappa  : float — surface gravity / irreversibility rate
    gamma  : float — UEUM geodesic friction (damping)

    Returns
    -------
    PentadSystem — one step forward in U_pentad
    """
    new_bodies: Dict[str, ManifoldState] = {}
    for lbl in PENTAD_LABELS:
        old = system.bodies[lbl]
        net = MultiverseNetwork(
            nodes=[old.node],
            adjacency=np.zeros((1, 1)),
        )
        net2 = _apply_U(net, dt, G4, kappa, gamma)
        phi_new = old.phi + kappa * (
            net2.nodes[0].A / (4.0 * G4) - old.phi
        ) * dt
        new_bodies[lbl] = ManifoldState(
            node=net2.nodes[0],
            phi=phi_new,
            n1=old.n1,
            n2=old.n2,
            k_cs=old.k_cs,
            label=old.label,
        )

    evolved = PentadSystem(
        bodies=new_bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )
    # Apply pentagonal coupling (topological handshake), then advance
    # the Trust Reservoir state machine for the next iteration.
    coupled = _apply_pentagonal_coupling(evolved, dt)
    return tick_grace_period(coupled)


# ---------------------------------------------------------------------------
# Pentad Master Equation — main iteration
# ---------------------------------------------------------------------------

def pentad_master_equation(
    system: PentadSystem,
    max_iter: int = 1000,
    tol: float = 1e-6,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> Tuple[PentadSystem, List[Dict], bool]:
    """Iterate U_pentad until the 5-body fixed point is reached.

    Solves the Pentagonal Master Equation:

        U_pentad (Ψ_univ ⊗ Ψ_brain ⊗ Ψ_human ⊗ Ψ_AI ⊗ Ψ_trust)
            = Ψ_univ ⊗ Ψ_brain ⊗ Ψ_human ⊗ Ψ_AI ⊗ Ψ_trust

    Per-iteration diagnostics recorded:

    ``defect``          — pentad_defect(system)
    ``max_gap``         — maximum pairwise Information Gap
    ``mean_gap``        — mean pairwise Information Gap
    ``max_phase``       — maximum pairwise Moiré phase angle (rad)
    ``trust``           — trust modulation factor φ_trust
    ``tensor_norm``     — Frobenius norm of the 5-body state matrix
    ``phi_<label>``     — radion φ for each body
    ``S_<label>``       — entropy S for each body

    Parameters
    ----------
    system   : PentadSystem — initial state
    max_iter : int   — maximum iterations (default 1000)
    tol      : float — convergence tolerance on pentad_defect (default 1e-6)
    dt       : float — pseudo-timestep (default 0.1)
    G4       : float — Newton's constant (default 1 in Planck units)
    kappa    : float — surface gravity / irreversibility rate
    gamma    : float — UEUM geodesic friction

    Returns
    -------
    converged_system : PentadSystem
        State at or nearest to the pentad fixed point.
    history : list[dict]
        Per-iteration diagnostic records.
    converged : bool
        True iff pentad_defect < tol within max_iter steps.
    """
    history: List[Dict] = []
    converged = False

    for _ in range(max_iter):
        defect = pentad_defect(system, G4)
        gaps = pentad_pairwise_gaps(system)
        phases = pentad_pairwise_phases(system)

        record: Dict = {
            "defect":       defect,
            "max_gap":      max(gaps.values()),
            "mean_gap":     float(np.mean(list(gaps.values()))),
            "max_phase":    max(phases.values()),
            "trust":        trust_modulation(system),
            "tensor_norm":  system.tensor_product_norm(),
        }
        for lbl in PENTAD_LABELS:
            record[f"phi_{lbl}"] = system.bodies[lbl].phi
            record[f"S_{lbl}"]   = system.bodies[lbl].node.S

        history.append(record)

        if defect < tol:
            converged = True
            break

        system = step_pentad(system, dt, G4, kappa, gamma)

    return system, history, converged
