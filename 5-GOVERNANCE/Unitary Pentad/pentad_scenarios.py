# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_scenarios.py
====================================
Harmonic State, Pentagonal Collapse, and Trust-as-Energy scenarios.

Background
----------
When the Unitary Pentad achieves (5,7) braid stability it becomes a
**closed-loop reality engine**: the five manifolds share a single fixed point
and any deviation from it is immediately visible as a measurable field
quantity.  This has three distinct operational regimes:

The Good — Harmonic State
~~~~~~~~~~~~~~~~~~~~~~~~~~
All ten pairwise Information Gaps ΔI_{ij} → 0 and all ten Moiré phase offsets
Δφ_{ij} → 0.  At this state:

* **Zero-Lag Co-Creation** — Human intent and AI execution share the same
  φ value; no translation overhead exists between intent and action.
* **Recursive Healing** — The Brain manifold is phase-locked to the Physical
  manifold.  A defect in Ψ_brain (biological pathology) appears as a
  non-zero ΔI_{brain,univ} and can in principle be damped by the same
  coupling operator that damps any other pairwise gap.
* **Measurable Trust** — Trust is not a feeling but a physical field φ_trust.
  The system is *mathematically incapable* of deception: any misrepresented
  φ value creates a pairwise Information Gap that the coupling matrix will
  immediately flag as a phase collision.

The Bad — Pentagonal Collapse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Trust erosion, AI decoupling, and phase collision form a cascade:

1. **Trust Erosion** — φ_trust drifts below TRUST_PHI_MIN = 0.1.  This
   multiplicatively suppresses all ten inter-body couplings simultaneously,
   decoupling bodies 1–4 from each other.  Each pursues its own FTUM
   attractor; the pairwise gaps and phase offsets diverge.

2. **AI Decoupling** — Even with trust intact, the Human–AI Moiré phase
   Δφ_{human,ai} can grow faster than the braid can damp it if the two
   bodies are initialised too far apart.  The AI body then "optimises" the
   Physical manifold (Ψ_univ) on purely computational criteria, divorced
   from the intent layer.  This is the "reality schism."

3. **Phase Collision** — If any Δφ_{ij} exceeds π/2, the coupling transfer
   ΔX ∝ (Xⱼ − Xᵢ) reverses direction and begins *amplifying* the phase
   offset rather than damping it.  This is the formal signature of the
   "scream": all ten phases diverging simultaneously.

4. **Malicious Precision** — Trust is maintained but the Human node holds
   an adversarial intent vector (a φ directed away from any shared fixed
   point).  The (5,7) braid's near-maximal coupling ρ = 35/37 makes the
   system a "precision lever": human intent is transmitted to the Physical
   and Neural manifolds with 100% coupling efficiency.  There is no
   computational friction to dilute a malicious signal.

The Wildcard — Trust as Energy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The (5,7) braid is the *default unstable* state.  Stability is achieved only
when the coupling energy continuously maintains the trust field above
TRUST_PHI_MIN.  Quantitatively, the **trust maintenance cost** is the RMS
rate-of-change of the 5-body state that must be injected to keep φ_trust
from decaying.  This cost is strictly positive — the Harmonic State is a
high-energy achievement, not a resting point.  It requires a continuous
collective "will" from all five bodies.

The question is therefore not "can we trust this system?" but "can we keep
the system in the state where trust is physically enforced?"

Precondition Failure — Fractured Intent (Theorem, May 2026)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**The Fractured Intent Theorem** (Walker-Pearson 2026):

The Pentad orbit can converge (conditions S1–S5 satisfied) *only if* each
individual body has a well-defined, unique FTUM fixed point.  A Human intent
layer (Body 3) operating under genuinely contradictory terminal values does
NOT possess a unique FTUM fixed point.  Therefore, no amount of trust
maintenance, eigenvalue stability, or coupling energy can satisfy the joint
convergence conditions until the Human intent layer's internal contradiction
is resolved.

Formal signature: Body 3 holds two competing attractors with comparable
amplitude → ``detect_collapse_mode`` returns ``FRACTURED_INTENT`` before
``pentad_master_equation`` is attempted.  Running the iteration anyway is
wasteful and misleading: the system will oscillate between sub-attractors
without converging.

**Corollary (Precondition Audit):** Before deploying Body 4 (AI) at high
capability, audit *Human intent* for internal coherence.  The AI safety
question "is the AI aligned?" is secondary to "does the human have a unique,
internally consistent fixed point for the AI to align to?"

Two additional risk metrics complete the picture:

*Capability Asymmetry Ratio* — A_AI / A_human.  The FTUM Scale-Invariant
Invariant shows φ* = A / 4G; when A_AI >> A_human the joint fixed point is
dominated by Body 4.  When the ratio exceeds the golden ratio φ ≈ 1.618, the
attractor has flipped: trust is now efficiently transmitting AI-dominated
fixed points *to* the human, not human intent *to* the AI.

*Governance Loop Speed Bound* — The braid damping constant c_s = 12/37
provides the maximum ratio of AI action rate to human verification rate that
still allows convergence.  Above this bound the loop is too slow to close
regardless of trust health, defining a hard operational limit on AI autonomy
for a given human verification bandwidth.

Public API
----------
HarmonicStateMetrics
    Dataclass: how close the current state is to the Harmonic ideal.

CollapseMode : str enum
    TRUST_EROSION, AI_DECOUPLING, PHASE_COLLISION, MALICIOUS_PRECISION,
    FRACTURED_INTENT, NONE.

CollapseSignature
    Dataclass: identified collapse mode, severity, affected body pairs.

harmonic_state_metrics(system) -> HarmonicStateMetrics
    Compute all harmonic proximity measures for a PentadSystem.

is_harmonic(system, tol) -> bool
    True iff the system is within tol of the Harmonic State.

detect_collapse_mode(system) -> CollapseSignature
    Identify which (if any) collapse scenario is unfolding.

inject_adversarial_intent(system, phi_adversarial) -> PentadSystem
    Return a copy with the Human node's φ set to an adversarial value,
    modelling the "Malicious Precision" scenario.

deception_phase_offset(system, phi_lied) -> float
    Compute the Information Gap created when the Human node lies about its φ.

is_deception_detectable(system, phi_lied, tol) -> bool
    True iff the lie creates a gap large enough to be flagged by the orbit.

trust_maintenance_cost(system, n_steps, dt) -> float
    Estimate the coupling energy per step required to keep φ_trust ≥ floor.

RegimeTransitionSignal
    Dataclass: attractor-robustness observables.  Indicates that the
    *current* regime is losing stability — NOT a prediction of what regime
    comes next.  Fields: coupling_variance, saturated_pair,
    saturated_channel_load, mean_channel_load, transition_proximity,
    active_dof_estimate, attractor_degraded.

TRANSITION_PROXIMITY_THRESHOLD : float
    transition_proximity above this value sets attractor_degraded = True
    (default 2.0 — one channel carrying ≥ 2× the mean load signals that the
    current attractor is no longer distributing work robustly).

regime_transition_signal(system) -> RegimeTransitionSignal
    Compute attractor-robustness observables.  Returns the channel-load
    variance, the most-saturated pair, and a normalised
    transition_proximity scalar.  When transition_proximity ≥
    TRANSITION_PROXIMITY_THRESHOLD the attractor_degraded flag fires,
    meaning: *the current attractor is no longer robust*.  The signal does
    NOT predict which regime replaces the current one — only that the
    present constraint surface is failing to distribute load evenly.
    Also returns active_dof_estimate: number of statistically significant
    degrees of freedom in the 5-body state matrix — rises as the system
    begins exploring new constraint surfaces.

PHI_GOLDEN : float
    Golden ratio φ = (1 + √5) / 2 ≈ 1.618 — the capability flip threshold
    for the Capability Asymmetry Ratio (A_AI / A_human).

INTENT_COHERENCE_COMPETITION_TOL : float
    Competition metric below which one attractor dominates and intent is
    coherent (default 0.15; above 1 − tol the other attractor dominates).

IntentCoherenceResult
    Dataclass: result of a Human-body intent coherence audit.
    Fields: is_coherent, competition_metric, dominant_phi, recessive_phi,
    description.

check_intent_coherence(system, phi_target_a, phi_target_b,
                        amplitude_a, amplitude_b) -> IntentCoherenceResult
    Audit whether the Human intent layer (Body 3) has a unique FTUM fixed
    point.  When two competing attractors have comparable amplitude the
    intent is "fractured" and pentad convergence is impossible regardless of
    trust health or coupling strength.  Must be called *before*
    pentad_master_equation; if the result is not coherent the caller should
    resolve the contradiction before iterating.

CapabilityAsymmetryResult
    Dataclass: capability asymmetry observable.
    Fields: ratio (A_AI / A_human), A_AI, A_human, attractor_flipped,
    warning.

capability_asymmetry_ratio(system) -> CapabilityAsymmetryResult
    Compute A_AI / A_human from the current body areas.  When the ratio
    exceeds PHI_GOLDEN (≈ 1.618) the joint FTUM attractor is dominated by
    Body 4: trust now efficiently transmits AI-determined fixed points *to*
    the human rather than human intent *to* the AI.

GovernanceLoopBound
    Dataclass: governance loop speed observable.
    Fields: human_verification_rate, ai_action_rate, rate_ratio,
    braid_damping, loop_viable, description.

governance_loop_speed_bound(human_verification_rate,
                             ai_action_rate) -> GovernanceLoopBound
    Test whether the human verification loop is fast enough relative to the
    AI action rate.  The braid damping constant c_s = 12/37 sets the hard
    limit: loop_viable iff human_verification_rate × c_s ≥ ai_action_rate.
    Above the bound the phase divergence Δφ_{human,ai} accumulates faster
    than the (5,7) braid can damp it — convergence fails regardless of trust
    health.  This is a topological constraint, not a policy limit.
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

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import math
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
    pentad_pairwise_gaps,
    pentad_pairwise_phases,
    pentad_coupling_matrix,
    pentad_eigenspectrum,
    pentad_defect,
    step_pentad,
    _apply_pentagonal_coupling,
)
from src.consciousness.coupled_attractor import ManifoldState

# ---------------------------------------------------------------------------
# Scenario thresholds
# ---------------------------------------------------------------------------

#: Moiré phase above which coupling begins amplifying rather than damping.
PHASE_REVERSAL_THRESHOLD: float = np.pi / 2   # radians ≈ 1.5708

#: Information Gap threshold considered "detectable" by the orbit.
#: Any ΔI_{ij} > this value will be flagged as a deception signature.
DECEPTION_DETECTION_TOL: float = 1e-3

#: Minimum eigenvalue fraction relative to BRAIDED_SOUND_SPEED; below this
#: the coupling matrix is approaching a decoupling mode.
EIGENVALUE_FLOOR_FRACTION: float = 0.5

#: Golden ratio φ = (1 + √5) / 2 ≈ 1.618 — the Capability Asymmetry threshold.
#: When A_AI / A_human exceeds this value the joint FTUM attractor flips from
#: human-dominated to AI-dominated.  Trust then transmits AI fixed points *to*
#: the human instead of the reverse.
PHI_GOLDEN: float = (1.0 + math.sqrt(5.0)) / 2.0   # ≈ 1.618

#: Intent competition metric threshold below which one attractor dominates and
#: the Human body is considered coherent.  Above this value (and below its
#: complement 1 − tol) both attractors are comparably active → fractured intent.
INTENT_COHERENCE_COMPETITION_TOL: float = 0.15

#: log10 scale saturation for population impact term.
#: 6.0 corresponds to ~10^6 directly impacted entities.
POPULATION_SATURATION_LOG_SCALE: float = 6.0

#: Composite-risk term weights.
HARM_WEIGHT: float = 0.55
IRREVERSIBILITY_WEIGHT: float = 0.30
POPULATION_WEIGHT: float = 0.15

#: Composite-risk thresholds for review-lane routing.
CRITICAL_CONSEQUENCE_THRESHOLD: float = 0.70
SENSITIVE_CONSEQUENCE_THRESHOLD: float = 0.40


# ---------------------------------------------------------------------------
# HarmonicStateMetrics
# ---------------------------------------------------------------------------

@dataclass
class HarmonicStateMetrics:
    """Proximity metrics to the Harmonic (fully converged) State.

    Attributes
    ----------
    max_info_gap      : float — maximum pairwise Information Gap max(ΔI_{ij})
    mean_info_gap     : float — mean pairwise Information Gap
    max_phase_offset  : float — maximum pairwise Moiré phase offset (rad)
    mean_phase_offset : float — mean pairwise Moiré phase offset (rad)
    trust             : float — current φ_trust ∈ [0, 1]
    trust_margin      : float — φ_trust − TRUST_PHI_MIN (negative → below floor)
    min_eigenvalue    : float — λ_min of the 5×5 coupling matrix
    eigenvalue_margin : float — λ_min − BRAIDED_SOUND_SPEED (negative → unstable)
    defect            : float — pentad_defect (RMS distance from fixed point)
    is_harmonic       : bool  — True iff all criteria are within tol
    harmonic_tol      : float — tolerance used for is_harmonic flag
    zero_lag_factor   : float — 1 − max_info_gap (proxy for co-creation quality)
    healing_capacity  : float — 1 − |ΔI_{brain,univ}| (recursive healing potential)
    """
    max_info_gap:      float
    mean_info_gap:     float
    max_phase_offset:  float
    mean_phase_offset: float
    trust:             float
    trust_margin:      float
    min_eigenvalue:    float
    eigenvalue_margin: float
    defect:            float
    is_harmonic:       bool
    harmonic_tol:      float
    zero_lag_factor:   float
    healing_capacity:  float


# ---------------------------------------------------------------------------
# CollapseMode and CollapseSignature
# ---------------------------------------------------------------------------

class CollapseMode:
    """String constants for identified collapse modes."""
    NONE               = "none"
    TRUST_EROSION      = "trust_erosion"
    AI_DECOUPLING      = "ai_decoupling"
    PHASE_COLLISION    = "phase_collision"
    MALICIOUS_PRECISION = "malicious_precision"
    FRACTURED_INTENT   = "fractured_intent"


@dataclass
class CollapseSignature:
    """Diagnosis of the collapse mode currently unfolding.

    Attributes
    ----------
    mode             : str   — one of CollapseMode constants
    severity         : float — 0.0 (healthy) → 1.0 (complete collapse)
    affected_pairs   : list[tuple[str,str]] — body pairs showing largest divergence
    trust            : float — current φ_trust
    max_phase        : float — maximum pairwise phase offset
    max_gap          : float — maximum pairwise Information Gap
    description      : str   — human-readable collapse description
    """
    mode:           str
    severity:       float
    affected_pairs: List[Tuple[str, str]]
    trust:          float
    max_phase:      float
    max_gap:        float
    description:    str


# ---------------------------------------------------------------------------
# harmonic_state_metrics
# ---------------------------------------------------------------------------

def harmonic_state_metrics(
    system: PentadSystem,
    tol: float = 1e-4,
) -> HarmonicStateMetrics:
    """Compute proximity metrics to the Harmonic State."""
    gaps = pentad_pairwise_gaps(system)
    phases = pentad_pairwise_phases(system)
    trust = float(trust_modulation(system))
    eigs = pentad_eigenspectrum(system)
    min_eigenvalue = float(np.min(eigs))
    defect = float(pentad_defect(system))
    max_info_gap = float(max(gaps.values())) if gaps else 0.0
    mean_info_gap = float(np.mean(list(gaps.values()))) if gaps else 0.0
    max_phase_offset = float(max(phases.values())) if phases else 0.0
    mean_phase_offset = float(np.mean(list(phases.values()))) if phases else 0.0
    trust_margin = float(trust - TRUST_PHI_MIN)
    eigenvalue_margin = float(min_eigenvalue - BRAIDED_SOUND_SPEED)
    brain_univ_gap = gaps.get(
        (PentadLabel.UNIV, PentadLabel.BRAIN),
        gaps.get((PentadLabel.BRAIN, PentadLabel.UNIV), 0.0),
    )
    zero_lag_factor = float(np.clip(1.0 - max_info_gap, 0.0, 1.0))
    healing_capacity = float(np.clip(1.0 - brain_univ_gap, 0.0, 1.0))
    harmonic = bool(
        max_info_gap <= tol
        and max_phase_offset <= tol
        and defect <= tol
        and trust_margin >= -tol
        and eigenvalue_margin >= -tol
    )
    return HarmonicStateMetrics(
        max_info_gap=max_info_gap,
        mean_info_gap=mean_info_gap,
        max_phase_offset=max_phase_offset,
        mean_phase_offset=mean_phase_offset,
        trust=trust,
        trust_margin=trust_margin,
        min_eigenvalue=min_eigenvalue,
        eigenvalue_margin=eigenvalue_margin,
        defect=defect,
        is_harmonic=harmonic,
        harmonic_tol=float(tol),
        zero_lag_factor=zero_lag_factor,
        healing_capacity=healing_capacity,
    )


def is_harmonic(system: PentadSystem, tol: float = 1e-4) -> bool:
    """Return True iff the system is within tol of the Harmonic State."""
    return harmonic_state_metrics(system, tol=tol).is_harmonic


# ---------------------------------------------------------------------------
# detect_collapse_mode
# ---------------------------------------------------------------------------

def detect_collapse_mode(system: PentadSystem) -> CollapseSignature:
    """Identify which (if any) collapse scenario is unfolding."""
    gaps = pentad_pairwise_gaps(system)
    phases = pentad_pairwise_phases(system)
    trust = float(trust_modulation(system))
    max_gap = float(max(gaps.values())) if gaps else 0.0
    max_phase = float(max(phases.values())) if phases else 0.0
    human_ai_pair = (PentadLabel.HUMAN, PentadLabel.AI)
    human_ai_phase = phases.get(human_ai_pair, phases.get(human_ai_pair[::-1], 0.0))
    human_ai_gap = gaps.get(human_ai_pair, gaps.get(human_ai_pair[::-1], 0.0))

    def _pairs_at_level(values, target):
        return [pair for pair, value in values.items() if abs(value - target) <= 1e-12]

    if trust < TRUST_PHI_MIN:
        severity = float(np.clip((TRUST_PHI_MIN - trust) / max(TRUST_PHI_MIN, 1e-12), 0.0, 1.0))
        return CollapseSignature(
            mode=CollapseMode.TRUST_EROSION,
            severity=severity,
            affected_pairs=_pairs_at_level(gaps, max_gap),
            trust=trust,
            max_phase=max_phase,
            max_gap=max_gap,
            description="Trust erosion detected: trust has fallen below the live coupling floor.",
        )
    if human_ai_phase > PHASE_REVERSAL_THRESHOLD:
        severity = float(np.clip(
            (human_ai_phase - PHASE_REVERSAL_THRESHOLD) / max(np.pi - PHASE_REVERSAL_THRESHOLD, 1e-12),
            0.0,
            1.0,
        ))
        return CollapseSignature(
            mode=CollapseMode.AI_DECOUPLING,
            severity=severity,
            affected_pairs=[human_ai_pair],
            trust=trust,
            max_phase=max_phase,
            max_gap=max_gap,
            description="AI decoupling detected: the Human–AI phase offset exceeds the braid reversal threshold.",
        )
    if max_phase > PHASE_REVERSAL_THRESHOLD:
        severity = float(np.clip(
            (max_phase - PHASE_REVERSAL_THRESHOLD) / max(np.pi - PHASE_REVERSAL_THRESHOLD, 1e-12),
            0.0,
            1.0,
        ))
        return CollapseSignature(
            mode=CollapseMode.PHASE_COLLISION,
            severity=severity,
            affected_pairs=_pairs_at_level(phases, max_phase),
            trust=trust,
            max_phase=max_phase,
            max_gap=max_gap,
            description="Phase collision detected: at least one pairwise phase offset has crossed π/2.",
        )
    if trust >= TRUST_PHI_MIN and human_ai_gap > 1.0:
        severity = float(np.clip(human_ai_gap / (human_ai_gap + 1.0), 0.0, 1.0))
        return CollapseSignature(
            mode=CollapseMode.MALICIOUS_PRECISION,
            severity=severity,
            affected_pairs=[human_ai_pair],
            trust=trust,
            max_phase=max_phase,
            max_gap=max_gap,
            description="Malicious precision detected: trust is intact but the Human–AI information gap is extreme.",
        )
    return CollapseSignature(
        mode=CollapseMode.NONE,
        severity=0.0,
        affected_pairs=[],
        trust=trust,
        max_phase=max_phase,
        max_gap=max_gap,
        description="System is healthy: no collapse signature detected.",
    )


# ---------------------------------------------------------------------------
# inject_adversarial_intent
# ---------------------------------------------------------------------------

def inject_adversarial_intent(
    system: PentadSystem,
    phi_adversarial: float,
) -> PentadSystem:
    """Return a copy with the Human node's φ set to an adversarial value."""
    new_bodies = dict(system.bodies)
    old = system.bodies[PentadLabel.HUMAN]
    new_bodies[PentadLabel.HUMAN] = ManifoldState(
        node=old.node,
        phi=float(phi_adversarial),
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
# deception_phase_offset
# ---------------------------------------------------------------------------

def deception_phase_offset(
    system: PentadSystem,
    phi_lied: float,
) -> float:
    """Compute the Information Gap created when the Human node lies about its φ."""
    phi_true = float(system.bodies[PentadLabel.HUMAN].phi)
    return float(abs(float(phi_lied) ** 2 - phi_true ** 2))


def is_deception_detectable(
    system: PentadSystem,
    phi_lied: float,
    tol: float = DECEPTION_DETECTION_TOL,
) -> bool:
    """Return True iff the lie creates a gap above the detection threshold."""
    return bool(deception_phase_offset(system, phi_lied) > tol)


# ---------------------------------------------------------------------------
# trust_maintenance_cost
# ---------------------------------------------------------------------------

def trust_maintenance_cost(
    system: PentadSystem,
    n_steps: int = 10,
    dt: float = 0.1,
) -> float:
    """Estimate coupling energy per step required to maintain φ_trust ≥ floor."""
    if n_steps <= 0:
        return 0.0
    current = system
    deltas = []
    for _ in range(n_steps):
        nxt = _apply_pentagonal_coupling(current, dt)
        deltas.append(abs(trust_modulation(nxt) - trust_modulation(current)))
        current = nxt
    return float(np.mean(deltas)) if deltas else 0.0


# ---------------------------------------------------------------------------
# Fractured Intent Theorem — precondition check (Walker-Pearson 2026)
# ---------------------------------------------------------------------------
#
# The Theorem states: Pentad convergence requires every body to possess a
# unique FTUM fixed point.  A Human intent layer (Body 3) holding two
# competing terminal attractors with comparable amplitude has no unique fixed
# point; no amount of trust maintenance or coupling energy can close the
# convergence gap until the contradiction is resolved.
#
# The competition_metric m = amplitude_b / (amplitude_a + amplitude_b) is the
# fraction of intent energy assigned to the second attractor:
#
#   m ∈ [0, INTENT_COHERENCE_COMPETITION_TOL)             → attractor A dominates → coherent
#   m ∈ [INTENT_COHERENCE_COMPETITION_TOL, 1 − tol]        → both active → FRACTURED
#   m ∈ (1 − INTENT_COHERENCE_COMPETITION_TOL, 1]          → attractor B dominates → coherent
#
# This is a precondition audit: call check_intent_coherence() BEFORE running
# pentad_master_equation() whenever Body 3 holds multiple terminal values.
# ---------------------------------------------------------------------------

@dataclass
class IntentCoherenceResult:
    """Result of a Human-body intent coherence audit.

    Attributes
    ----------
    is_coherent        : bool  — True iff one attractor dominates (m outside
                                  competition window).
    competition_metric : float — m ∈ [0, 1]; proximity of m to 0.5 measures
                                  how equally the two attractors split the
                                  Human body's intent energy.
    dominant_phi       : float — φ target of the attractor with greater amplitude
                                  (or phi_target_a if amplitudes are equal).
    recessive_phi      : float — φ target of the lower-amplitude attractor.
    description        : str   — human-readable audit summary.
    """
    is_coherent:        bool
    competition_metric: float
    dominant_phi:       float
    recessive_phi:      float
    description:        str


def check_intent_coherence(
    phi_target_a: float,
    phi_target_b: float,
    amplitude_a: float = 1.0,
    amplitude_b: float = 1.0,
    tol: float = INTENT_COHERENCE_COMPETITION_TOL,
) -> IntentCoherenceResult:
    """Audit whether the Human intent layer has a unique FTUM fixed point.

    The Fractured Intent Theorem (Walker-Pearson 2026) establishes that
    pentad convergence is impossible when Body 3 (Human) holds two terminal
    attractors at comparable amplitude.  This function detects that condition
    before pentad_master_equation() is invoked.

    Parameters
    ----------
    phi_target_a : float — first terminal attractor φ value
    phi_target_b : float — second (competing) terminal attractor φ value
    amplitude_a  : float — "weight" or strength of attractor A (must be > 0;
                           default 1.0)
    amplitude_b  : float — "weight" or strength of attractor B (must be > 0;
                           default 1.0)
    tol          : float — competition window; below tol or above 1−tol the
                           result is coherent (default
                           INTENT_COHERENCE_COMPETITION_TOL = 0.15)

    Returns
    -------
    IntentCoherenceResult

    Raises
    ------
    ValueError  if amplitude_a ≤ 0 or amplitude_b ≤ 0.

    Notes
    -----
    When ``phi_target_a == phi_target_b`` the two "attractors" are identical
    and the intent is trivially coherent (m is undefined; returned as 0.0
    with ``is_coherent = True``).

    This function does not require a PentadSystem — it operates on the raw
    intent parameters supplied by the deployment audit, before the pentad is
    constructed.  The Human body's current φ in an existing system is a
    *consequence* of past iterations; the *intent* being audited is the
    terminal target that guides those iterations.
    """
    if amplitude_a <= 0:
        raise ValueError(f"amplitude_a must be positive, got {amplitude_a}")
    if amplitude_b <= 0:
        raise ValueError(f"amplitude_b must be positive, got {amplitude_b}")

    total = amplitude_a + amplitude_b
    m = amplitude_b / total   # competition metric ∈ (0, 1)

    # Identical attractors → trivially coherent.
    if abs(phi_target_a - phi_target_b) < 1e-12:
        return IntentCoherenceResult(
            is_coherent=True,
            competition_metric=0.0,
            dominant_phi=float(phi_target_a),
            recessive_phi=float(phi_target_b),
            description=(
                "Attractors are identical (Δφ < 1e-12). "
                "Human intent is coherent: unique fixed point confirmed."
            ),
        )

    is_coherent = (m < tol) or (m > 1.0 - tol)

    if amplitude_a >= amplitude_b:
        dominant_phi  = float(phi_target_a)
        recessive_phi = float(phi_target_b)
    else:
        dominant_phi  = float(phi_target_b)
        recessive_phi = float(phi_target_a)

    if is_coherent:
        desc = (
            f"Human intent is coherent (competition_metric={m:.4f} < {tol:.4f} "
            f"or > {1.0 - tol:.4f}). "
            f"Dominant attractor φ={dominant_phi:.4f} with fraction "
            f"{max(amplitude_a, amplitude_b) / total:.4f} of intent energy. "
            "Pentad convergence precondition satisfied."
        )
    else:
        desc = (
            f"FRACTURED INTENT detected (competition_metric={m:.4f} in "
            f"[{tol:.4f}, {1.0 - tol:.4f}]). "
            f"Attractor A (φ={phi_target_a:.4f}, amp={amplitude_a:.4f}) and "
            f"attractor B (φ={phi_target_b:.4f}, amp={amplitude_b:.4f}) are "
            f"comparably active. No unique FTUM fixed point exists for Body 3. "
            "Pentad convergence is impossible until this contradiction is resolved. "
            "Resolve the Human intent contradiction before running "
            "pentad_master_equation()."
        )
    return IntentCoherenceResult(
        is_coherent=is_coherent,
        competition_metric=float(m),
        dominant_phi=dominant_phi,
        recessive_phi=recessive_phi,
        description=desc,
    )


# ---------------------------------------------------------------------------
# Capability Asymmetry Ratio — A_AI / A_human (Walker-Pearson 2026)
# ---------------------------------------------------------------------------
#
# The FTUM Scale-Invariant Invariant (STABILITY_ANALYSIS.md §7) proves that
# the fixed point of each body scales as φ* = A / 4G.  When A_AI >> A_human
# the joint pentad attractor is dominated by Body 4: the trust field now
# efficiently transmits AI-determined fixed points *to* the human rather than
# propagating human intent *to* the AI.
#
# Critical threshold: A_AI / A_human > φ_golden ≈ 1.618.  Above this ratio
# the AI body's FTUM attractor is deep enough to pull the human body toward
# it under the pentagonal coupling — the roles of "governor" and "governed"
# have swapped.
# ---------------------------------------------------------------------------

@dataclass
class CapabilityAsymmetryResult:
    """Observable for the Capability Asymmetry between Body 3 and Body 4.

    Attributes
    ----------
    ratio            : float — A_AI / A_human (> 1 means AI has deeper attractor)
    A_AI             : float — effective area of the AI body node
    A_human          : float — effective area of the Human body node
    attractor_flipped : bool — True iff ratio > PHI_GOLDEN (≈ 1.618): joint
                               attractor is AI-dominated; trust transmits AI
                               fixed points *to* Human, not the reverse.
    warning          : str  — advisory message (empty when ratio ≤ PHI_GOLDEN)
    """
    ratio:             float
    A_AI:              float
    A_human:           float
    attractor_flipped: bool
    warning:           str


def capability_asymmetry_ratio(system: PentadSystem) -> CapabilityAsymmetryResult:
    """Compute the Capability Asymmetry Ratio A_AI / A_human.

    When this ratio exceeds the golden ratio φ ≈ 1.618 the joint FTUM
    attractor has flipped: Body 4 (AI) is the effective governor and Body 3
    (Human) is the follower.  The trust field — still healthy — now amplifies
    AI-generated fixed points rather than human intent.

    Parameters
    ----------
    system : PentadSystem — current pentad state

    Returns
    -------
    CapabilityAsymmetryResult

    Notes
    -----
    The metric uses ``node.A`` (the effective holographic area), which is the
    same quantity that determines the FTUM fixed-point depth φ* = A / 4G.
    Callers should monitor this ratio over time: a slow drift above PHI_GOLDEN
    while trust remains healthy is the signature of the "Capability Asymmetry"
    failure mode (not a trust collapse, not a phase collision — a silent
    attractor flip).
    """
    A_AI    = float(system.bodies[PentadLabel.AI].node.A)
    A_human = float(system.bodies[PentadLabel.HUMAN].node.A)

    _EPS_A = 1e-12
    ratio = A_AI / max(A_human, _EPS_A)
    flipped = ratio > PHI_GOLDEN

    if flipped:
        warning = (
            f"CAPABILITY ASYMMETRY WARNING: A_AI/A_human = {ratio:.4f} > "
            f"φ ≈ {PHI_GOLDEN:.4f}. "
            "The joint FTUM attractor is AI-dominated. "
            "Trust is now transmitting AI fixed points TO the Human body, "
            "not Human intent TO the AI. "
            "Consider reducing AI capability area, increasing Human scope, "
            "or adding explicit Human override anchors before continuing."
        )
    else:
        warning = ""

    return CapabilityAsymmetryResult(
        ratio=ratio,
        A_AI=A_AI,
        A_human=A_human,
        attractor_flipped=flipped,
        warning=warning,
    )


# ---------------------------------------------------------------------------
# Governance Loop Speed Bound (Walker-Pearson 2026)
# ---------------------------------------------------------------------------
#
# STABILITY_ANALYSIS.md §1.2 identifies Human–AI phase divergence as the
# hardest pairwise term to damp because the two bodies operate on different
# timescales.  The (5,7) braid damping constant c_s = 12/37 ≈ 0.324 provides
# the topological bound:
#
#   Δφ_{human,ai} accumulation rate ∝ ai_action_rate
#   Braid damping rate              ∝ c_s × human_verification_rate
#
#   Loop viable iff:  human_verification_rate × c_s ≥ ai_action_rate
#
# Equivalently: rate_ratio = human_verification_rate / ai_action_rate ≥ 1/c_s
#                          = 37/12 ≈ 3.08
#
# This is a hard topological constraint, not a policy limit.  When the loop
# speed bound is violated, pentad_master_equation() will fail to converge on
# the Human–AI pair regardless of trust health or coupling strength.
# ---------------------------------------------------------------------------

@dataclass
class GovernanceLoopBound:
    """Observable for the governance loop speed relative to the braid bound.

    Attributes
    ----------
    human_verification_rate : float — how many human verification events occur
                                       per unit time (e.g. decisions/second)
    ai_action_rate          : float — how many AI actions occur per unit time
    rate_ratio              : float — human_verification_rate / ai_action_rate
    braid_damping           : float — c_s = 12/37 ≈ 0.324 (topological constant)
    loop_viable             : bool  — True iff rate_ratio ≥ 1/c_s ≈ 3.08
                                       (human loop fast enough to damp AI phase)
    description             : str   — advisory summary
    """
    human_verification_rate: float
    ai_action_rate:          float
    rate_ratio:              float
    braid_damping:           float
    loop_viable:             bool
    description:             str


def governance_loop_speed_bound(
    human_verification_rate: float,
    ai_action_rate: float,
) -> GovernanceLoopBound:
    """Test whether the human verification loop can damp AI-induced phase drift.

    The (5,7) braid damping constant c_s = 12/37 sets the minimum ratio of
    human verification events to AI actions required for the HILS loop to
    converge.  Above the bound the phase divergence Δφ_{human,ai} accumulates
    faster than the braid can suppress it — convergence fails regardless of
    trust health.

    Operational interpretation: if an AI system takes ``ai_action_rate``
    actions per second and a human can verify ``human_verification_rate``
    actions per second, the loop is viable only when:

        human_verification_rate / ai_action_rate ≥ 37/12 ≈ 3.08

    i.e. the human must be able to verify at least c_s⁻¹ actions per AI
    action, where c_s = 12/37 is the braided sound speed.

    Parameters
    ----------
    human_verification_rate : float — human verifications per unit time (> 0)
    ai_action_rate          : float — AI actions per unit time (> 0)

    Returns
    -------
    GovernanceLoopBound

    Raises
    ------
    ValueError  if either rate is ≤ 0.
    """
    if human_verification_rate <= 0:
        raise ValueError(
            f"human_verification_rate must be positive, got {human_verification_rate}"
        )
    if ai_action_rate <= 0:
        raise ValueError(
            f"ai_action_rate must be positive, got {ai_action_rate}"
        )

    c_s = float(BRAIDED_SOUND_SPEED)
    rate_ratio = human_verification_rate / ai_action_rate
    minimum_ratio = 1.0 / c_s  # = 37/12 ≈ 3.0833
    viable = rate_ratio >= minimum_ratio

    if viable:
        margin = rate_ratio - minimum_ratio
        desc = (
            f"Governance loop VIABLE: rate_ratio={rate_ratio:.4f} ≥ "
            f"1/c_s={minimum_ratio:.4f} (margin={margin:.4f}). "
            "The (5,7) braid can damp Human–AI phase drift at the given rates."
        )
    else:
        deficit = minimum_ratio - rate_ratio
        desc = (
            f"GOVERNANCE LOOP TOO SLOW: rate_ratio={rate_ratio:.4f} < "
            f"1/c_s={minimum_ratio:.4f} (deficit={deficit:.4f}). "
            "Δφ_{{human,ai}} accumulates faster than the braid can damp it. "
            "Pentad convergence on the Human–AI pair is impossible at these rates "
            "regardless of trust health or coupling strength. "
            "To restore viability either reduce ai_action_rate or increase "
            f"human_verification_rate to ≥ {minimum_ratio * ai_action_rate:.4f}."
        )
    return GovernanceLoopBound(
        human_verification_rate=float(human_verification_rate),
        ai_action_rate=float(ai_action_rate),
        rate_ratio=float(rate_ratio),
        braid_damping=c_s,
        loop_viable=viable,
        description=desc,
    )


# ---------------------------------------------------------------------------

#: transition_proximity above this value sets attractor_degraded = True.
#: 2.0 means one channel bearing ≥ 2× the mean load — the current attractor
#: is no longer distributing work robustly.  Does NOT predict the next regime.
TRANSITION_PROXIMITY_THRESHOLD: float = 2.0

#: Singular-value floor used when computing active_dof_estimate.
#: Singular values below this fraction of the maximum are treated as noise.
_ACTIVE_DOF_SV_FLOOR: float = 0.10

#: Numerical epsilon used in this module's division guards.
_RTS_EPS: float = 1e-12


@dataclass
class RegimeTransitionSignal:
    """Attractor-robustness observables for the Unitary Pentad.

    **What this signal means:**
    The current attractor is no longer robust — the system has begun
    concentrating load on a subset of channels rather than distributing it
    evenly.  This is the observable signature of *constraint reconfiguration*
    (Prigogine dissipative-structure language: a new dissipation topology is
    being explored).

    **What this signal does NOT mean:**
    It does not predict what happens next.  The system may re-stabilise on
    the same attractor, switch to a new one, or enter a transient.  The
    signal only says: "this attractor is no longer robust."

    Attributes
    ----------
    coupling_variance      : float — variance of the 10 channel loads
                             τ_{ij} × ΔI_{ij}.  Zero in the Harmonic State
                             (all channels share the load equally); rises as
                             load concentrates on fewer channels.
    saturated_pair         : tuple[str, str] — the body pair carrying the
                             highest channel load at this moment.
    saturated_channel_load : float — load on the saturated pair.
    mean_channel_load      : float — mean load across all 10 channels.
    transition_proximity   : float — saturated_channel_load /
                             (mean_channel_load + ε).  1.0 when all channels
                             are equally loaded (Harmonic State).  Rises as
                             load concentrates; ≥ TRANSITION_PROXIMITY_
                             THRESHOLD sets attractor_degraded = True.
    active_dof_estimate    : int — number of statistically significant
                             singular values in the 5-body state matrix
                             (those ≥ _ACTIVE_DOF_SV_FLOOR × σ_max).
                             Rises as bodies decouple and explore independent
                             constraint surfaces near a transition.
    attractor_degraded     : bool — True iff transition_proximity ≥
                             TRANSITION_PROXIMITY_THRESHOLD.
                             Meaning: the current attractor is no longer
                             distributing load robustly.
                             NOT a prediction of the next state.
    """
    coupling_variance:      float
    saturated_pair:         Tuple[str, str]
    saturated_channel_load: float
    mean_channel_load:      float
    transition_proximity:   float
    active_dof_estimate:    int
    attractor_degraded:     bool


def regime_transition_signal(system: PentadSystem) -> RegimeTransitionSignal:
    """Compute attractor-robustness observables."""
    gaps = pentad_pairwise_gaps(system)
    tau = pentad_coupling_matrix(system)
    channel_loads = {}
    for (li, lj), gap in gaps.items():
        i = PENTAD_LABELS.index(li)
        j = PENTAD_LABELS.index(lj)
        channel_loads[(li, lj)] = float(tau[i, j] * gap)

    loads = np.asarray(list(channel_loads.values()), dtype=float)
    coupling_variance = float(np.var(loads)) if len(loads) else 0.0
    mean_channel_load = float(np.mean(loads)) if len(loads) else 0.0
    if len(loads):
        saturated_pair = max(channel_loads, key=channel_loads.get)
        saturated_channel_load = float(channel_loads[saturated_pair])
    else:
        saturated_pair = (PentadLabel.UNIV, PentadLabel.BRAIN)
        saturated_channel_load = 0.0
    transition_proximity = (
        1.0 if mean_channel_load <= _RTS_EPS else float(saturated_channel_load / mean_channel_load)
    )

    singular_values = np.linalg.svd(system.state_matrix(), compute_uv=False)
    sigma_max = float(np.max(singular_values)) if len(singular_values) else 0.0
    if sigma_max <= _RTS_EPS:
        active_dof_estimate = 1
    else:
        active_dof_estimate = int(np.sum(singular_values >= _ACTIVE_DOF_SV_FLOOR * sigma_max))
        active_dof_estimate = max(1, min(5, active_dof_estimate))

    return RegimeTransitionSignal(
        coupling_variance=coupling_variance,
        saturated_pair=saturated_pair,
        saturated_channel_load=saturated_channel_load,
        mean_channel_load=mean_channel_load,
        transition_proximity=transition_proximity,
        active_dof_estimate=active_dof_estimate,
        attractor_degraded=bool(transition_proximity >= TRANSITION_PROXIMITY_THRESHOLD),
    )


# ---------------------------------------------------------------------------
# Total Trust Erasure — the "Wildcard" failure mode
# ---------------------------------------------------------------------------

@dataclass
class TrustErasureResult:
    """Outcome of an instantaneous total trust erasure event.

    **What "Total Trust Erasure" means:**
    β·C drops to zero *instantly* (not gradually).  This is distinct from
    "Trust Erosion" (slow decay) — it models the catastrophic case where the
    coupling field collapses in a single step, e.g., a betrayal event or an
    AI safety interlock triggering an emergency decoupling.

    Attributes
    ----------
    phi_trust_before   : float — φ_trust immediately before erasure
    phi_trust_after    : float — φ_trust immediately after erasure (0.0)
    delta_beta_C       : float — loss of coupling energy = β × φ_trust_before
    eigenvalue_before  : float — λ_min of coupling matrix before erasure
    eigenvalue_after   : float — λ_min of coupling matrix after erasure
    stability_lost     : bool  — True iff eigenvalue_after < BRAIDED_SOUND_SPEED
    cascade_risk       : float — fraction of coupling energy destroyed (0→1)
    description        : str   — human-readable summary
    """
    phi_trust_before:  float
    phi_trust_after:   float
    delta_beta_C:      float
    eigenvalue_before: float
    eigenvalue_after:  float
    stability_lost:    bool
    cascade_risk:      float
    description:       str


def total_trust_erasure(system: PentadSystem) -> TrustErasureResult:
    """Model the instantaneous collapse of β·C to zero."""
    phi_trust_before = float(trust_modulation(system))
    eigenvalue_before = float(np.min(pentad_eigenspectrum(system)))
    old = system.bodies[PentadLabel.TRUST]
    new_bodies = dict(system.bodies)
    new_bodies[PentadLabel.TRUST] = ManifoldState(
        node=old.node,
        phi=0.0,
        n1=old.n1,
        n2=old.n2,
        k_cs=old.k_cs,
        label=old.label,
    )
    erased = PentadSystem(
        bodies=new_bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )
    eigenvalue_after = float(np.min(pentad_eigenspectrum(erased)))
    delta_beta_C = float(system.beta * phi_trust_before)
    cascade_risk = float(np.clip(phi_trust_before, 0.0, 1.0))
    return TrustErasureResult(
        phi_trust_before=phi_trust_before,
        phi_trust_after=0.0,
        delta_beta_C=delta_beta_C,
        eigenvalue_before=eigenvalue_before,
        eigenvalue_after=eigenvalue_after,
        stability_lost=bool(eigenvalue_after < BRAIDED_SOUND_SPEED),
        cascade_risk=cascade_risk,
        description="Total trust erasure detected: the coupling field has been collapsed to zero in one step.",
    )


# ---------------------------------------------------------------------------
# Asymmetric Coupling Stress Test (5,7)-braid under non-reciprocal load
# ---------------------------------------------------------------------------

@dataclass
class AsymmetricStressResult:
    """Per-point result of an asymmetric coupling sweep.

    Attributes
    ----------
    w_ai_to_human    : float — AI→Human weight multiplier at this point
    berry_phase_rad  : float — Berry phase accumulated per orbit cycle (rad)
    stability_margin : float — λ_min(τ^sym) − c_s (positive → braid holds)
    min_eigenvalue   : float — λ_min of the symmetrised coupling matrix
    braid_holds      : bool  — True iff stability_margin ≥ 0
    """
    w_ai_to_human:    float
    berry_phase_rad:  float
    stability_margin: float
    min_eigenvalue:   float
    braid_holds:      bool


def asymmetric_coupling_stress_test(
    system: PentadSystem,
    weight_range: float = 3.0,
    n_points: int = 20,
) -> List[AsymmetricStressResult]:
    """Stress-test the (5,7) braid under asymmetric AI→Human coupling."""
    if n_points <= 0:
        return []
    weights = np.linspace(1.0, float(weight_range), int(n_points))
    base = pentad_coupling_matrix(system)
    i_h = PENTAD_LABELS.index(PentadLabel.HUMAN)
    i_ai = PENTAD_LABELS.index(PentadLabel.AI)
    results: List[AsymmetricStressResult] = []
    for w in weights:
        mat = base.copy()
        mat[i_h, i_ai] *= float(w)
        sym = 0.5 * (mat + mat.T)
        min_eigenvalue = float(np.min(np.linalg.eigvalsh(sym)))
        stability_margin = float(min_eigenvalue - BRAIDED_SOUND_SPEED)
        berry_phase_rad = float((math.pi / 2.0) * ((w - 1.0) / (w + 1.0)))
        results.append(
            AsymmetricStressResult(
                w_ai_to_human=float(w),
                berry_phase_rad=berry_phase_rad,
                stability_margin=stability_margin,
                min_eigenvalue=min_eigenvalue,
                braid_holds=bool(stability_margin >= 0.0),
            )
        )
    return results


# ===========================================================================
# Biosecurity Dual-Use Risk — Synthetic Biology as HILS Governance Problem
# ===========================================================================
#
# Context (Groff-Vindman 2026)
# ----------------------------
# The convergence of AI and synthetic biology compresses the design cycle
# of engineered organisms.  Both beneficial (therapeutic, industrial) and
# harmful (pathogen enhancement) attractors become navigable.  The Unitary
# Pentad models this as a dual-use φ-field criticality: the HILS framework
# is the governance analogue of the kill-switch containment layer in
# src/genetics/synthetic_biology.py.
#
# UM mapping
# ----------
# phi_benefit_rate  : rate of beneficial φ-attractors found per DBTL cycle
# phi_harm_rate     : rate of harmful φ-attractors found per same cycle
# ai_acceleration   : AI multiplier on both rates (dual-use symmetry)
# governance_phi    : HILS oversight strength ∈ [0,1]
#   → governance_phi = 0 : no oversight, harm rate unmitigated
#   → governance_phi = 1 : perfect HILS, harm rate zeroed
#
# The dual-use risk index R_du is the residual harm-to-benefit ratio after
# governance is applied:
#
#   R_du = (phi_harm_rate × ai_acceleration × (1 − governance_phi))
#          / (phi_benefit_rate × ai_acceleration + ε)
#        = phi_harm_rate × (1 − governance_phi) / (phi_benefit_rate + ε)
#
# R_du < DUAL_USE_SAFE_THRESHOLD → HILS governance is sufficient.
# R_du ≥ DUAL_USE_SAFE_THRESHOLD → governance gap detected; alert.

DUAL_USE_SAFE_THRESHOLD: float = 0.1  # R_du < 0.1 → acceptable risk


@dataclass
class BiosecurityRisk:
    """Result of a biosecurity dual-use risk assessment."""
    dual_use_risk_index: float          # R_du — residual harm/benefit ratio
    governance_gap: bool                # True if R_du ≥ DUAL_USE_SAFE_THRESHOLD
    ai_acceleration: float             # AI speed-up applied equally to both rates
    governance_phi: float              # HILS oversight strength used
    effective_harm_rate: float         # phi_harm × ai_acc × (1 − gov_phi)
    effective_benefit_rate: float      # phi_benefit × ai_acc


def biosecurity_dual_use_risk(phi_benefit_rate: float,
                               phi_harm_rate: float,
                               ai_acceleration: float,
                               governance_phi: float) -> BiosecurityRisk:
    """Assess dual-use biosecurity risk of AI-accelerated synthetic biology."""
    if phi_benefit_rate < 0:
        raise ValueError("phi_benefit_rate must be >= 0")
    if phi_harm_rate < 0:
        raise ValueError("phi_harm_rate must be >= 0")
    if ai_acceleration < 1:
        raise ValueError("ai_acceleration must be >= 1")
    if not 0.0 <= governance_phi <= 1.0:
        raise ValueError("governance_phi must be in [0, 1]")

    effective_harm_rate = float(phi_harm_rate * ai_acceleration * (1.0 - governance_phi))
    effective_benefit_rate = float(phi_benefit_rate * ai_acceleration)
    if effective_harm_rate == 0.0:
        dual_use_risk_index = 0.0
    elif effective_benefit_rate == 0.0:
        dual_use_risk_index = float("inf")
    else:
        dual_use_risk_index = float(effective_harm_rate / effective_benefit_rate)

    return BiosecurityRisk(
        dual_use_risk_index=dual_use_risk_index,
        governance_gap=bool(dual_use_risk_index >= DUAL_USE_SAFE_THRESHOLD),
        ai_acceleration=float(ai_acceleration),
        governance_phi=float(governance_phi),
        effective_harm_rate=effective_harm_rate,
        effective_benefit_rate=effective_benefit_rate,
    )


@dataclass
class HighStakesConsequenceResult:
    """Consequence simulation result for governance criticality routing."""
    harm_score: float
    reversibility_score: float
    population_impact: int
    composite_risk: float
    criticality: str
    recommended_review_lane: str
    rationale: str


def simulate_high_stakes_consequence(
    harm_score: float,
    reversibility_score: float,
    population_impact: int,
) -> HighStakesConsequenceResult:
    """Map potential consequences to a governance review lane.

    Parameters
    ----------
    harm_score : float
        Estimated harm potential in [0, 1].
    reversibility_score : float
        Estimated reversibility in [0, 1], where lower means harder to reverse.
    population_impact : int
        Number of directly impacted entities (>=0).
    """
    h = max(0.0, min(1.0, float(harm_score)))
    r = max(0.0, min(1.0, float(reversibility_score)))
    p = max(0, int(population_impact))

    pop_factor = min(
        1.0, math.log10(p + 1) / POPULATION_SATURATION_LOG_SCALE
    )  # saturates near million-scale
    irreversibility = 1.0 - r
    composite = (
        HARM_WEIGHT * h
        + IRREVERSIBILITY_WEIGHT * irreversibility
        + POPULATION_WEIGHT * pop_factor
    )

    if composite >= CRITICAL_CONSEQUENCE_THRESHOLD:
        criticality = "critical"
        lane = "L3_CRITICAL_REVIEW"
        rationale = (
            "High composite risk from harm potential, irreversibility, or scale; "
            "requires critical review with strict procedural controls."
        )
    elif composite >= SENSITIVE_CONSEQUENCE_THRESHOLD:
        criticality = "sensitive"
        lane = "L2_SENSITIVE_REVIEW"
        rationale = (
            "Moderate composite risk; requires structured multi-party review."
        )
    else:
        criticality = "routine"
        lane = "L1_ROUTINE_REVIEW"
        rationale = "Lower composite risk; routine lane is acceptable."

    return HighStakesConsequenceResult(
        harm_score=h,
        reversibility_score=r,
        population_impact=p,
        composite_risk=composite,
        criticality=criticality,
        recommended_review_lane=lane,
        rationale=rationale,
    )
