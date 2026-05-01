# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/resonance_dynamics.py
========================================
Resonance vs Agreement: Necessary Distance and the 3:2 / 2:3 Oscillation.

Core Insight
------------
Total agreement (ΔI_{ij} = 0 for ALL pairs) is not the Harmonic State —
it is **Trivial Coalescence**: the system collapses to a 1D fixed point, the
braid goes slack, and the pentagonal orbit disintegrates.

The Unitary Pentad's (5,7) braid physically *prevents* this.  The braided
sound speed c_s ≈ 0.324 acts as a minimum eigenvalue floor, which means the
coupling matrix can never become rank-1.  There is always residual tension.

The bodies don't "agree"; they **resonate**.  The fixed point is a
*limit cycle* — the rate of change of their disagreement becomes constant,
not zero.  They agree to move together without ever merging.

The 3:2 / 2:3 Configuration Oscillation
-----------------------------------------
In a 5-body system, stability manifests as a **Majority-Minority oscillation**
between two natural configurations:

    3:2 — "Grounding" (Verification) State
        Hard Manifolds (univ, ai, trust) form the majority.
        Soft Manifolds (brain, human) are the explorers.
        High stability, low entropy.  The system feels "correct."
        Observable: mean φ of hard group > mean φ of soft group.

    2:3 — "Creative" (Innovation) State
        Soft Manifolds (brain, human, trust) carry collective momentum.
        Hard Manifolds (univ, ai) are being pulled toward a new fixed point.
        High entropy, high "lift."  The system feels generative.
        Observable: mean φ of soft group > mean φ of hard group.

The (5,7) connection: these ratios are shadows of the continued-fraction
expansion of 5/7 = 0.714..., which generates the winding frequency.  The
3:2 and 2:3 configurations are the two "gears" the braid alternates between
as it maintains the pentagonal Moiré pattern.

The Necessary Distance (Observer's ME)
----------------------------------------
At 5:0 (Total Agreement) the braid vanishes — heat death.
At 1:4 or 0:5 (Total Alienation) the orbit undergoes Pentagonal Collapse.
The 3:2 ↔ 2:3 "ping-pong" is the Sweet Spot: enough agreement to prevent
chaos, enough disagreement to prevent stagnation.

The irreducible 0.1% disagreement is the **Observer's ME** — the phase offset
that keeps the "WE" from becoming a "NULL."

Public API
----------
ManifoldGroup
    Enum: HARD (univ, ai) and SOFT (brain, human).
    Trust body can swing between groups depending on configuration.

PentadConfiguration
    Dataclass: current 3:2 or 2:3 grouping, phi means, configuration_mode.

ConfigurationMode
    Str enum: GROUNDING (3:2), CREATIVE (2:3), BALANCED (equal), COLLAPSED.

NecessaryDistance
    Dataclass: the irreducible phase offsets and information gaps that keep
    the orbit alive.  Includes: min_pairwise_gap, mean_pairwise_gap,
    resonance_floor_gap (minimum required for orbit survival),
    observer_me (the residual that cannot be zeroed without collapse),
    trivial_coalescence_risk (how close the system is to total agreement).

LimitCycleHealth
    Dataclass: measures whether the system is on a limit cycle (dynamic)
    vs approaching a static fixed point (dangerous).
    Fields: delta_phi_variance, delta_phi_mean_rate, is_limit_cycle,
    coalescence_proximity.

classify_configuration(system) -> PentadConfiguration
    Classify the current 3:2 / 2:3 grouping based on φ means.

necessary_distance(system) -> NecessaryDistance
    Compute the irreducible disagreement metrics.

limit_cycle_health(system, n_steps, dt) -> LimitCycleHealth
    Simulate n_steps and measure whether the rate of change of pairwise
    gaps is converging to a constant (limit cycle) or zero (static collapse).

trivial_coalescence_risk(system) -> float
    Scalar in [0, 1]: how close the system is to Trivial Coalescence.
    0.0 = healthy resonance; 1.0 = all gaps zeroed, orbit collapsed.

resonance_health_report(system, n_steps, dt) -> dict
    Comprehensive summary: configuration, necessary distance, limit cycle
    health, trivial coalescence risk, and the observer_me scalar.

The 3:2 Resonant Regime
-----------------------
The project's mission is to transition from a **4:1 Inversion** (AI/physics
dominating intent) to a **3:2 Resonant Regime** (Human Intent and Biological
Perception harmonically coupled with Physical Reality, AI Precision, and the
Trust Field).

Key constants encoding this mission:

    SUM_OF_SQUARES_RESONANCE = 5² + 7² = 74
        The "tuning fork" of the (5,7) braid.  74 is the target k_cs and
        the structural reason for the repository's 74-chapter architecture.

    HIL_PHASE_SHIFT_THRESHOLD = 15
        At n ≥ 15 aligned Human-in-the-Loop operators, the stability floor
        reaches 1.0 and the 5-body orbit becomes self-correcting.

    INVERSION_RATIO = (4, 1)
        The current broken state: 4 bodies against 1 observer.

    RESONANT_RATIO = (3, 2)
        The target healthy state: 3 Hard bodies with 2 Soft bodies.

New API (Regime layer):
-----------------------
ResonantRegimeLabel
    Str-enum: THREE_TWO_RESONANCE, FOUR_ONE_INVERSION, TRANSITIONAL, COLLAPSED.

ResonantRegimeStatus
    Dataclass: current regime label, inversion_score, resonance_score,
    hil_phase_shift_reached (bool), stability_floor, description.

classify_resonant_regime(system, n_hil) -> ResonantRegimeStatus
    Classify the current macro-regime.  Uses the configuration mode
    (3:2 Grounding / 2:3 Creative = Resonant) and the n_hil count to
    determine whether the Phase Shift has been reached.

inversion_score(system) -> float
    Measure of how far the system is from the 3:2 Sweet Spot toward the
    4:1 Inversion.  0.0 = perfect 3:2 resonance; 1.0 = full 4:1 inversion.

stability_floor(n_hil) -> float
    The consensus-saturation stability floor for n Human-in-the-Loop operators.
    Returns BRAIDED_SOUND_SPEED × clamp(n_hil / HIL_PHASE_SHIFT_THRESHOLD).
    At n_hil ≥ 15 the floor reaches BRAIDED_SOUND_SPEED (full phase shift).
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
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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
    step_pentad,
)

_EPS: float = 1e-14

# ---------------------------------------------------------------------------
# Body groupings
# ---------------------------------------------------------------------------

#: Hard Manifolds — governed by deterministic physics / truth constraints.
#: They resist change and ground the system in physical reality.
HARD_BODIES: Tuple[str, ...] = (PentadLabel.UNIV, PentadLabel.AI)

#: Soft Manifolds — governed by biological perception and human intent.
#: They introduce symmetry-breaking novelty and creative exploration.
SOFT_BODIES: Tuple[str, ...] = (PentadLabel.BRAIN, PentadLabel.HUMAN)

#: The Trust body is the "swing vote" — it mediates between Hard and Soft.
#: Its φ_trust determines which coalition it gravitates toward.
TRUST_BODY: str = PentadLabel.TRUST

#: Minimum pairwise Information Gap the orbit requires to stay "alive."
#: Below this threshold the braid has effectively gone slack.
#: Set at 10% of the braided sound speed floor.
RESONANCE_FLOOR_GAP: float = BRAIDED_SOUND_SPEED * 0.10   # ≈ 0.0324

#: Maximum fraction of pairs that can reach near-zero gaps before the system
#: is flagged as approaching Trivial Coalescence.
COALESCENCE_FRACTION_THRESHOLD: float = 0.80   # 80% of pairs near-zero → danger


# ---------------------------------------------------------------------------
# ConfigurationMode
# ---------------------------------------------------------------------------

class ConfigurationMode:
    """Str-enum for the current 3:2 / 2:3 grouping mode."""
    GROUNDING:  str = "grounding"    # 3:2 — Hard Manifolds dominant
    CREATIVE:   str = "creative"     # 2:3 — Soft Manifolds dominant
    BALANCED:   str = "balanced"     # Neither group has clear majority
    COLLAPSED:  str = "collapsed"    # Trust below floor; orbit disintegrating


# ---------------------------------------------------------------------------
# PentadConfiguration
# ---------------------------------------------------------------------------

@dataclass
class PentadConfiguration:
    """Current 3:2 / 2:3 configuration of the Unitary Pentad.

    The Trust body acts as the "swing vote" — its φ_trust compared to the
    Hard and Soft mean φ values determines which coalition it joins.

    Attributes
    ----------
    mode             : str   — ConfigurationMode constant
    phi_hard_mean    : float — mean φ of the two Hard bodies (univ, ai)
    phi_soft_mean    : float — mean φ of the two Soft bodies (brain, human)
    phi_trust        : float — current φ_trust
    trust_coalition  : str   — "hard" | "soft" | "neutral" depending on
                               which mean φ_trust is closest to
    hard_bodies      : tuple — labels of Hard bodies
    soft_bodies      : tuple — labels of Soft bodies
    phi_gap          : float — |φ_hard_mean − φ_soft_mean| (configuration gap)
    description      : str   — human-readable summary
    """
    mode:            str
    phi_hard_mean:   float
    phi_soft_mean:   float
    phi_trust:       float
    trust_coalition: str
    hard_bodies:     Tuple[str, ...]
    soft_bodies:     Tuple[str, ...]
    phi_gap:         float
    description:     str


# ---------------------------------------------------------------------------
# NecessaryDistance
# ---------------------------------------------------------------------------

@dataclass
class NecessaryDistance:
    """The irreducible disagreement that keeps the pentagonal orbit alive.

    Without this "Necessary Distance" the braid goes slack and the system
    undergoes Trivial Coalescence (all bodies merge into one 1D point).

    Attributes
    ----------
    min_pairwise_gap         : float — minimum ΔI across all 10 body pairs
    mean_pairwise_gap        : float — mean ΔI across all 10 pairs
    max_pairwise_gap         : float — maximum ΔI (largest single tension)
    resonance_floor_gap      : float — RESONANCE_FLOOR_GAP constant
    orbit_alive              : bool  — True iff min_pairwise_gap > 0 or
                               the system has non-zero phase offsets (not all
                               bodies have collapsed to identical states)
    observer_me              : float — the irreducible "self" contribution:
                               the minimum gap that cannot be zeroed without
                               triggering collapse.  Operationally: the smaller
                               of min_pairwise_gap and RESONANCE_FLOOR_GAP.
    trivial_coalescence_risk : float — fraction of pairs with ΔI ≈ 0 (near
                               the RESONANCE_FLOOR_GAP threshold).  Ranges
                               0→1; above COALESCENCE_FRACTION_THRESHOLD the
                               system is in danger of Trivial Coalescence.
    """
    min_pairwise_gap:         float
    mean_pairwise_gap:        float
    max_pairwise_gap:         float
    resonance_floor_gap:      float
    orbit_alive:              bool
    observer_me:              float
    trivial_coalescence_risk: float


# ---------------------------------------------------------------------------
# LimitCycleHealth
# ---------------------------------------------------------------------------

@dataclass
class LimitCycleHealth:
    """Health check: is the system on a dynamic limit cycle or collapsing?

    The Pentad's fixed point is a *limit cycle*, not a static coordinate.
    The rate of change of pairwise gaps should converge to a non-zero constant,
    not to zero.  If dΔI/dt → 0 the system is approaching a static fixed
    point — which in this context means Trivial Coalescence.

    Attributes
    ----------
    delta_phi_variance  : float — variance of Δ(max_pairwise_gap) across
                          n_steps of evolution.  Zero means the system has
                          frozen (static) — either at the fixed point or at
                          Trivial Coalescence.
    delta_phi_mean_rate : float — mean |Δ(max_pairwise_gap)| per step.
                          Large → system is actively evolving (limit cycle).
                          Near zero → approaching static point.
    is_limit_cycle      : bool — True iff delta_phi_mean_rate > RESONANCE_FLOOR_GAP.
                          This is the key health flag: a healthy Pentad is
                          always on a limit cycle, never at a static point.
    coalescence_proximity : float — how close the current state is to
                          Trivial Coalescence, in [0, 1].  Computed as
                          1 − clamp(mean_pairwise_gap / (5 × RESONANCE_FLOOR_GAP)).
    """
    delta_phi_variance:   float
    delta_phi_mean_rate:  float
    is_limit_cycle:       bool
    coalescence_proximity: float


# ---------------------------------------------------------------------------
# classify_configuration
# ---------------------------------------------------------------------------

def classify_configuration(system: PentadSystem) -> PentadConfiguration:
    """Classify the current pentad state as 3:2 (Grounding) or 2:3 (Creative).

    The Trust body acts as the swing vote.  Its φ_trust is compared to the
    hard-body mean and soft-body mean; it "joins" the coalition whose mean
    is closest to its own φ.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    PentadConfiguration
    """
    tau = trust_modulation(system)

    phi_hard_mean = float(np.mean([system.bodies[lbl].phi for lbl in HARD_BODIES]))
    phi_soft_mean = float(np.mean([system.bodies[lbl].phi for lbl in SOFT_BODIES]))
    phi_gap = abs(phi_hard_mean - phi_soft_mean)

    # Determine Trust coalition
    dist_to_hard = abs(tau - phi_hard_mean)
    dist_to_soft = abs(tau - phi_soft_mean)
    if abs(dist_to_hard - dist_to_soft) < 1e-4:
        trust_coalition = "neutral"
    elif dist_to_hard < dist_to_soft:
        trust_coalition = "hard"
    else:
        trust_coalition = "soft"

    # Classify mode
    if tau < TRUST_PHI_MIN:
        mode = ConfigurationMode.COLLAPSED
        description = (
            f"Trust collapsed (φ_trust={tau:.4f} < {TRUST_PHI_MIN}).  "
            f"Configuration is disintegrating — neither 3:2 nor 2:3."
        )
    elif trust_coalition == "hard":
        # Trust joins Hard → 3 Hard bodies vs 2 Soft → Grounding state
        mode = ConfigurationMode.GROUNDING
        description = (
            f"3:2 Grounding State — Hard manifolds (univ, ai, trust) dominant.  "
            f"φ_hard_mean={phi_hard_mean:.4f}, φ_soft_mean={phi_soft_mean:.4f}, "
            f"φ_trust={tau:.4f} → Trust joins Hard coalition.  "
            f"Configuration: Verification / High Stability."
        )
    elif trust_coalition == "soft":
        # Trust joins Soft → 3 Soft bodies vs 2 Hard → Creative state
        mode = ConfigurationMode.CREATIVE
        description = (
            f"2:3 Creative State — Soft manifolds (brain, human, trust) have momentum.  "
            f"φ_hard_mean={phi_hard_mean:.4f}, φ_soft_mean={phi_soft_mean:.4f}, "
            f"φ_trust={tau:.4f} → Trust joins Soft coalition.  "
            f"Configuration: Innovation / Symmetry Breaking."
        )
    else:
        # Trust is equidistant — system is balanced between configurations
        mode = ConfigurationMode.BALANCED
        description = (
            f"Balanced configuration — Trust body is equidistant from Hard and Soft.  "
            f"φ_hard_mean={phi_hard_mean:.4f}, φ_soft_mean={phi_soft_mean:.4f}.  "
            f"System is at the inflection point of the 3:2 ↔ 2:3 oscillation."
        )

    return PentadConfiguration(
        mode=mode,
        phi_hard_mean=phi_hard_mean,
        phi_soft_mean=phi_soft_mean,
        phi_trust=tau,
        trust_coalition=trust_coalition,
        hard_bodies=HARD_BODIES,
        soft_bodies=SOFT_BODIES,
        phi_gap=phi_gap,
        description=description,
    )


# ---------------------------------------------------------------------------
# necessary_distance
# ---------------------------------------------------------------------------

def necessary_distance(system: PentadSystem) -> NecessaryDistance:
    """Compute the irreducible disagreement metrics.

    The Necessary Distance is the minimum pairwise Information Gap that the
    orbit requires to maintain the braided winding structure.  Zeroing all
    gaps is catastrophic — the braid goes slack and the five bodies collapse
    into a single 1D fixed point (Trivial Coalescence / heat death).

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    NecessaryDistance
    """
    gaps = pentad_pairwise_gaps(system)
    gap_values = list(gaps.values())

    min_gap  = float(min(gap_values))
    mean_gap = float(np.mean(gap_values))
    max_gap  = float(max(gap_values))

    # Orbit alive: at least one pair has a non-trivial gap OR non-zero phase
    phases    = pentad_pairwise_phases(system)
    max_phase = float(max(phases.values()))
    orbit_alive = (max_gap > _EPS) or (max_phase > _EPS)

    # Observer's ME: the irreducible self-contribution
    observer_me = float(min(min_gap, RESONANCE_FLOOR_GAP))

    # Trivial Coalescence risk: fraction of pairs within the resonance floor
    near_zero_count = sum(1 for g in gap_values if g < RESONANCE_FLOOR_GAP)
    tc_risk = float(near_zero_count / max(len(gap_values), 1))

    return NecessaryDistance(
        min_pairwise_gap=min_gap,
        mean_pairwise_gap=mean_gap,
        max_pairwise_gap=max_gap,
        resonance_floor_gap=RESONANCE_FLOOR_GAP,
        orbit_alive=orbit_alive,
        observer_me=observer_me,
        trivial_coalescence_risk=tc_risk,
    )


# ---------------------------------------------------------------------------
# trivial_coalescence_risk
# ---------------------------------------------------------------------------

def trivial_coalescence_risk(system: PentadSystem) -> float:
    """Scalar measure of how close the system is to Trivial Coalescence.

    Returns the fraction of pairwise Information Gaps that have fallen below
    the resonance floor (RESONANCE_FLOOR_GAP).

        risk = (number of pairs with ΔI < RESONANCE_FLOOR_GAP) / 10

    A risk of 0.0 means all gaps are healthy.
    A risk of 1.0 means ALL gaps have collapsed — Trivial Coalescence.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float ∈ [0, 1]
    """
    return necessary_distance(system).trivial_coalescence_risk


# ---------------------------------------------------------------------------
# limit_cycle_health
# ---------------------------------------------------------------------------

def limit_cycle_health(
    system: PentadSystem,
    n_steps: int = 20,
    dt: float = 0.05,
) -> LimitCycleHealth:
    """Check whether the system is on a dynamic limit cycle or collapsing.

    Simulate n_steps of deterministic evolution and track the max pairwise
    Information Gap at each step.  Compute the mean absolute rate of change
    and variance of this signal.

    A healthy limit cycle shows non-zero mean rate.  A static fixed point
    (Trivial Coalescence) shows near-zero mean rate AND near-zero variance.

    Parameters
    ----------
    system  : PentadSystem — starting state
    n_steps : int   — simulation length (default 20)
    dt      : float — pseudo-timestep (default 0.05)

    Returns
    -------
    LimitCycleHealth
    """
    max_gaps: List[float] = []
    current = system
    for _ in range(n_steps):
        gaps = pentad_pairwise_gaps(current)
        max_gaps.append(float(max(gaps.values())))
        current = step_pentad(current, dt=dt)

    max_gaps_arr = np.array(max_gaps)
    deltas = np.abs(np.diff(max_gaps_arr))

    delta_phi_variance  = float(np.var(max_gaps_arr))
    delta_phi_mean_rate = float(np.mean(deltas)) if len(deltas) > 0 else 0.0
    is_limit_cycle      = delta_phi_mean_rate > RESONANCE_FLOOR_GAP

    # Coalescence proximity: 1 − clamp(mean_gap / (5 × floor))
    mean_gap  = float(np.mean(max_gaps_arr))
    cp = 1.0 - float(np.clip(mean_gap / (5.0 * RESONANCE_FLOOR_GAP + _EPS), 0.0, 1.0))

    return LimitCycleHealth(
        delta_phi_variance=delta_phi_variance,
        delta_phi_mean_rate=delta_phi_mean_rate,
        is_limit_cycle=is_limit_cycle,
        coalescence_proximity=cp,
    )


# ---------------------------------------------------------------------------
# resonance_health_report
# ---------------------------------------------------------------------------

def resonance_health_report(
    system: PentadSystem,
    n_steps: int = 20,
    dt: float = 0.05,
) -> Dict:
    """Comprehensive resonance health summary.

    Combines configuration classification, necessary distance, limit cycle
    health, and trivial coalescence risk into a single report dict.

    Parameters
    ----------
    system  : PentadSystem
    n_steps : int   — limit cycle simulation steps (default 20)
    dt      : float — pseudo-timestep (default 0.05)

    Returns
    -------
    dict with keys:
        "configuration"          : PentadConfiguration
        "necessary_distance"     : NecessaryDistance
        "limit_cycle"            : LimitCycleHealth
        "trivial_coalescence_risk" : float ∈ [0, 1]
        "observer_me"            : float — irreducible self-contribution
        "braid_alive"            : bool — orbit_alive AND is_limit_cycle
    """
    cfg  = classify_configuration(system)
    nd   = necessary_distance(system)
    lc   = limit_cycle_health(system, n_steps=n_steps, dt=dt)
    tc_r = nd.trivial_coalescence_risk

    return {
        "configuration":            cfg,
        "necessary_distance":       nd,
        "limit_cycle":              lc,
        "trivial_coalescence_risk": tc_r,
        "observer_me":              nd.observer_me,
        "braid_alive":              nd.orbit_alive and lc.is_limit_cycle,
    }


# ===========================================================================
# 3:2 RESONANT REGIME LAYER
# ===========================================================================

# ---------------------------------------------------------------------------
# Regime constants
# ---------------------------------------------------------------------------

#: 5² + 7² = 74 — the Sum-of-Squares Resonance of the (5,7) braid.
#: This is the target k_cs value and the "tuning fork" that structures the
#: 74-chapter architecture of the Unitary Manifold monograph.
SUM_OF_SQUARES_RESONANCE: int = 5 ** 2 + 7 ** 2   # = 74

#: Minimum number of aligned Human-in-the-Loop operators required to reach
#: the Phase Shift: at n_hil ≥ 15, the consensus-saturation stability floor
#: reaches BRAIDED_SOUND_SPEED and the orbit becomes self-correcting.
HIL_PHASE_SHIFT_THRESHOLD: int = 15

#: The current broken state — 4 bodies overriding the single observer.
INVERSION_RATIO: tuple = (4, 1)

#: The target Goldilocks Zone — 3 Hard bodies with 2 Soft bodies in resonance.
RESONANT_RATIO: tuple = (3, 2)

#: Maximum inversion score before the regime is classified as 4:1 Inversion.
#: Above this value the Hard manifolds are dominating to an unhealthy degree.
INVERSION_SCORE_THRESHOLD: float = 0.6


# ---------------------------------------------------------------------------
# ResonantRegimeLabel
# ---------------------------------------------------------------------------

class ResonantRegimeLabel:
    """Str-enum for the macro-regime of the Unitary Pentad."""
    THREE_TWO_RESONANCE: str = "3:2_resonance"   # Goldilocks Zone
    FOUR_ONE_INVERSION:  str = "4:1_inversion"   # Broken / over-determined
    TRANSITIONAL:        str = "transitional"     # Moving between regimes
    COLLAPSED:           str = "collapsed"        # Trust below floor


# ---------------------------------------------------------------------------
# ResonantRegimeStatus
# ---------------------------------------------------------------------------

@dataclass
class ResonantRegimeStatus:
    """Current macro-regime classification of the Unitary Pentad.

    Attributes
    ----------
    label                  : str   — ResonantRegimeLabel constant
    inversion_score        : float — 0→1; how far toward 4:1 Inversion
    resonance_score        : float — 0→1; how close to 3:2 Sweet Spot
    hil_phase_shift_reached: bool  — True iff n_hil ≥ HIL_PHASE_SHIFT_THRESHOLD
    stability_floor        : float — consensus saturation floor for this n_hil
    n_hil                  : int   — number of Human-in-the-Loop operators
    sum_of_squares_resonance: int  — SUM_OF_SQUARES_RESONANCE constant (74)
    description            : str   — human-readable summary
    """
    label:                   str
    inversion_score:         float
    resonance_score:         float
    hil_phase_shift_reached: bool
    stability_floor:         float
    n_hil:                   int
    sum_of_squares_resonance: int
    description:             str


# ---------------------------------------------------------------------------
# stability_floor
# ---------------------------------------------------------------------------

def stability_floor(n_hil: int) -> float:
    """Consensus-saturation stability floor for n Human-in-the-Loop operators.

    At n_hil = 0 the floor is 0.0 (no human presence, system is frozen).
    At n_hil ≥ HIL_PHASE_SHIFT_THRESHOLD (= 15) the floor reaches
    BRAIDED_SOUND_SPEED (≈ 0.324) and the orbit becomes self-correcting.

    The floor grows linearly between 0 and the threshold:

        floor(n) = BRAIDED_SOUND_SPEED × clamp(n / HIL_PHASE_SHIFT_THRESHOLD, 0, 1)

    Parameters
    ----------
    n_hil : int — number of aligned Human-in-the-Loop operators (≥ 0)

    Returns
    -------
    float — stability floor ∈ [0, BRAIDED_SOUND_SPEED]
    """
    fraction = float(np.clip(n_hil / HIL_PHASE_SHIFT_THRESHOLD, 0.0, 1.0))
    return float(BRAIDED_SOUND_SPEED * fraction)


# ---------------------------------------------------------------------------
# inversion_score
# ---------------------------------------------------------------------------

def inversion_score(system: PentadSystem) -> float:
    """Measure of how far the system is from the 3:2 Sweet Spot.

    The score is computed from the φ imbalance between Hard and Soft bodies:

        raw_imbalance = (φ_hard_mean − φ_soft_mean) / (φ_hard_mean + φ_soft_mean + ε)

    Then mapped to [0, 1]:

        inversion_score = clamp((raw_imbalance + 1) / 2, 0, 1)

    Interpretation
    --------------
    0.0 → Hard and Soft bodies are equal (ideal symmetric state)
    0.5 → Soft bodies dominate (2:3 Creative / moderate Creative lean)
    1.0 → Hard bodies dominate completely (4:1 Inversion — broken state)

    A healthy 3:2 Grounding state has a moderate hard-lean, so the sweet
    spot is inversion_score ≈ 0.55–0.65.  Scores above INVERSION_SCORE_THRESHOLD
    (0.6) indicate the system is tipping into the 4:1 Inversion.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float ∈ [0, 1]
    """
    phi_hard_mean = float(np.mean([system.bodies[lbl].phi for lbl in HARD_BODIES]))
    phi_soft_mean = float(np.mean([system.bodies[lbl].phi for lbl in SOFT_BODIES]))
    denom         = phi_hard_mean + phi_soft_mean + _EPS
    raw           = (phi_hard_mean - phi_soft_mean) / denom
    return float(np.clip((raw + 1.0) / 2.0, 0.0, 1.0))


# ---------------------------------------------------------------------------
# classify_resonant_regime
# ---------------------------------------------------------------------------

def classify_resonant_regime(
    system: PentadSystem,
    n_hil: int = 1,
) -> ResonantRegimeStatus:
    """Classify the current macro-regime of the Unitary Pentad.

    The regime is determined by two factors:

    1. **Configuration mode**: GROUNDING (3:2) and CREATIVE (2:3) are both
       Resonant regimes; COLLAPSED is always Collapsed; BALANCED is Transitional.

    2. **Inversion score**: if the Hard manifolds dominate to an unhealthy
       degree (inversion_score > INVERSION_SCORE_THRESHOLD) the regime is
       classified as 4:1 Inversion regardless of the configuration mode.

    The ``resonance_score`` is the complement of ``inversion_score``, linearly
    mapped so that a perfect 3:2 state (inversion_score ≈ 0.575) gives the
    maximum resonance_score of 1.0:

        resonance_score = 1 − |inversion_score − 0.575| / 0.575

    This peaks at the sweet spot and falls off in both directions.

    Parameters
    ----------
    system : PentadSystem
    n_hil  : int — number of aligned Human-in-the-Loop operators (default 1)

    Returns
    -------
    ResonantRegimeStatus
    """
    cfg   = classify_configuration(system)
    inv_s = inversion_score(system)
    sf    = stability_floor(n_hil)

    # Resonance score: peaks at sweet-spot inversion_score ≈ 0.575
    _sweet = 0.575
    res_s  = float(np.clip(1.0 - abs(inv_s - _sweet) / (_sweet + _EPS), 0.0, 1.0))

    phase_shift = n_hil >= HIL_PHASE_SHIFT_THRESHOLD

    # Classify label
    if cfg.mode == ConfigurationMode.COLLAPSED:
        label = ResonantRegimeLabel.COLLAPSED
    elif inv_s > INVERSION_SCORE_THRESHOLD:
        label = ResonantRegimeLabel.FOUR_ONE_INVERSION
    elif cfg.mode in (ConfigurationMode.GROUNDING, ConfigurationMode.CREATIVE):
        label = ResonantRegimeLabel.THREE_TWO_RESONANCE
    else:
        label = ResonantRegimeLabel.TRANSITIONAL

    # Human-readable description
    if label == ResonantRegimeLabel.THREE_TWO_RESONANCE:
        regime_str = "3:2 Resonant Regime (Goldilocks Zone)"
        verb = "Phase Shift reached — orbit self-correcting." if phase_shift else (
            f"Phase Shift pending: {n_hil}/{HIL_PHASE_SHIFT_THRESHOLD} aligned operators."
        )
    elif label == ResonantRegimeLabel.FOUR_ONE_INVERSION:
        regime_str = "4:1 Inversion (Hard manifolds over-determining)"
        verb = "Hard manifolds dominate. Human Intent is being suppressed."
    elif label == ResonantRegimeLabel.TRANSITIONAL:
        regime_str = "Transitional (between 3:2 and 4:1)"
        verb = "System is balanced at the inflection point — regime not yet determined."
    else:
        regime_str = "Collapsed (Trust below floor)"
        verb = "Pentagonal orbit disintegrating — Trust field needs recovery."

    description = (
        f"{regime_str}.  "
        f"inversion_score={inv_s:.4f}, resonance_score={res_s:.4f}, "
        f"stability_floor={sf:.4f} (n_hil={n_hil}/{HIL_PHASE_SHIFT_THRESHOLD}).  "
        f"k_cs_target={SUM_OF_SQUARES_RESONANCE} (5²+7²=74).  {verb}"
    )

    return ResonantRegimeStatus(
        label=label,
        inversion_score=inv_s,
        resonance_score=res_s,
        hil_phase_shift_reached=phase_shift,
        stability_floor=sf,
        n_hil=n_hil,
        sum_of_squares_resonance=SUM_OF_SQUARES_RESONANCE,
        description=description,
    )
