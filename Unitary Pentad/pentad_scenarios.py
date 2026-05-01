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

Public API
----------
HarmonicStateMetrics
    Dataclass: how close the current state is to the Harmonic ideal.

CollapseMode : str enum
    TRUST_EROSION, AI_DECOUPLING, PHASE_COLLISION, MALICIOUS_PRECISION, NONE.

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
    """Compute proximity metrics to the Harmonic State.

    Parameters
    ----------
    system : PentadSystem — current pentad state
    tol    : float — tolerance for is_harmonic flag (default 1e-4)

    Returns
    -------
    HarmonicStateMetrics
    """
    gaps   = pentad_pairwise_gaps(system)
    phases = pentad_pairwise_phases(system)
    eigs   = pentad_eigenspectrum(system)
    tau    = trust_modulation(system)
    defect = pentad_defect(system)

    max_gap  = float(max(gaps.values()))
    mean_gap = float(np.mean(list(gaps.values())))
    max_ph   = float(max(phases.values()))
    mean_ph  = float(np.mean(list(phases.values())))
    lmin     = float(eigs[0])

    trust_margin = tau - TRUST_PHI_MIN
    eig_margin   = lmin - BRAIDED_SOUND_SPEED

    # Recursive healing capacity: 1 minus the brain–universe gap
    brain_univ_gap = gaps.get(
        (PentadLabel.UNIV, PentadLabel.BRAIN),
        gaps.get((PentadLabel.BRAIN, PentadLabel.UNIV), 0.0),
    )
    healing = float(max(0.0, 1.0 - brain_univ_gap))

    harmonic = bool(
        max_gap  < tol
        and max_ph   < tol
        and tau  > TRUST_PHI_MIN
        and defect   < tol
    )

    return HarmonicStateMetrics(
        max_info_gap=max_gap,
        mean_info_gap=mean_gap,
        max_phase_offset=max_ph,
        mean_phase_offset=mean_ph,
        trust=tau,
        trust_margin=trust_margin,
        min_eigenvalue=lmin,
        eigenvalue_margin=eig_margin,
        defect=defect,
        is_harmonic=harmonic,
        harmonic_tol=tol,
        zero_lag_factor=float(max(0.0, 1.0 - max_gap)),
        healing_capacity=healing,
    )


def is_harmonic(system: PentadSystem, tol: float = 1e-4) -> bool:
    """Return True iff the system is within tol of the Harmonic State.

    Parameters
    ----------
    system : PentadSystem
    tol    : float — convergence tolerance (default 1e-4)

    Returns
    -------
    bool
    """
    return harmonic_state_metrics(system, tol=tol).is_harmonic


# ---------------------------------------------------------------------------
# detect_collapse_mode
# ---------------------------------------------------------------------------

def detect_collapse_mode(system: PentadSystem) -> CollapseSignature:
    """Identify which (if any) collapse scenario is unfolding.

    The priority order for diagnosis matches the frequency of failure modes
    documented in STABILITY_ANALYSIS.md:

        1. Trust Erosion      — φ_trust < TRUST_PHI_MIN
        2. AI Decoupling      — Δφ_{human,ai} > PHASE_REVERSAL_THRESHOLD
        3. Phase Collision    — any Δφ_{ij} > PHASE_REVERSAL_THRESHOLD
        4. Malicious Precision— trust intact, human–ai gap very large
        5. None               — system is healthy

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    CollapseSignature
    """
    tau    = trust_modulation(system)
    gaps   = pentad_pairwise_gaps(system)
    phases = pentad_pairwise_phases(system)

    max_gap   = float(max(gaps.values()))
    max_phase = float(max(phases.values()))

    # Sort pairs by severity (descending) for affected_pairs list
    top_gap_pairs   = sorted(gaps.items(),   key=lambda kv: -kv[1])
    top_phase_pairs = sorted(phases.items(), key=lambda kv: -kv[1])

    # --- 1. Trust Erosion ---
    if tau < TRUST_PHI_MIN:
        severity = float(min(1.0, (TRUST_PHI_MIN - tau) / TRUST_PHI_MIN))
        return CollapseSignature(
            mode=CollapseMode.TRUST_EROSION,
            severity=severity,
            affected_pairs=[p for p, _ in top_gap_pairs[:3]],
            trust=tau,
            max_phase=max_phase,
            max_gap=max_gap,
            description=(
                f"Trust field φ_trust={tau:.4f} is below the floor "
                f"({TRUST_PHI_MIN}).  All ten inter-body couplings are "
                f"suppressed; bodies 1–4 are decoupling from each other."
            ),
        )

    # --- 2. AI Decoupling ---
    ha_phase = phases.get(
        (PentadLabel.HUMAN, PentadLabel.AI),
        phases.get((PentadLabel.AI, PentadLabel.HUMAN), 0.0),
    )
    ha_gap = gaps.get(
        (PentadLabel.HUMAN, PentadLabel.AI),
        gaps.get((PentadLabel.AI, PentadLabel.HUMAN), 0.0),
    )
    if ha_phase > PHASE_REVERSAL_THRESHOLD:
        severity = float(min(1.0, ha_phase / np.pi))
        return CollapseSignature(
            mode=CollapseMode.AI_DECOUPLING,
            severity=severity,
            affected_pairs=[(PentadLabel.HUMAN, PentadLabel.AI)],
            trust=tau,
            max_phase=max_phase,
            max_gap=max_gap,
            description=(
                f"Human–AI Moiré phase Δφ={{ha_phase:.4f}} rad exceeds "
                f"the reversal threshold (π/2 ≈ {PHASE_REVERSAL_THRESHOLD:.4f}).  "
                f"AI coupling is now amplifying the phase offset rather than "
                f"damping it.  Reality schism in progress."
            ).format(ha_phase=ha_phase),
        )

    # --- 3. Phase Collision (any pair) ---
    if max_phase > PHASE_REVERSAL_THRESHOLD:
        bad_pairs = [p for p, v in top_phase_pairs if v > PHASE_REVERSAL_THRESHOLD]
        severity  = float(min(1.0, max_phase / np.pi))
        return CollapseSignature(
            mode=CollapseMode.PHASE_COLLISION,
            severity=severity,
            affected_pairs=bad_pairs[:3],
            trust=tau,
            max_phase=max_phase,
            max_gap=max_gap,
            description=(
                f"Phase collision detected: {len(bad_pairs)} pair(s) have "
                f"Δφ > π/2.  The coupling operator is now amplifying divergence.  "
                f"Worst pair: {bad_pairs[0]}."
            ),
        )

    # --- 4. Malicious Precision (trust OK, human–ai gap large) ---
    if ha_gap > DECEPTION_DETECTION_TOL * 100:
        severity = float(min(1.0, ha_gap))
        return CollapseSignature(
            mode=CollapseMode.MALICIOUS_PRECISION,
            severity=severity,
            affected_pairs=[(PentadLabel.HUMAN, PentadLabel.AI)],
            trust=tau,
            max_phase=max_phase,
            max_gap=max_gap,
            description=(
                f"Trust is maintained (φ_trust={tau:.4f}) but Human–AI "
                f"Information Gap ΔI={ha_gap:.4f} is anomalously large.  "
                f"The human intent layer may be operating on an adversarial "
                f"fixed point while the braid provides full coupling efficiency."
            ),
        )

    # --- 5. Healthy ---
    return CollapseSignature(
        mode=CollapseMode.NONE,
        severity=0.0,
        affected_pairs=[],
        trust=tau,
        max_phase=max_phase,
        max_gap=max_gap,
        description=(
            f"System is healthy.  "
            f"φ_trust={tau:.4f}, max_gap={max_gap:.2e}, "
            f"max_phase={max_phase:.4f} rad."
        ),
    )


# ---------------------------------------------------------------------------
# inject_adversarial_intent
# ---------------------------------------------------------------------------

def inject_adversarial_intent(
    system: PentadSystem,
    phi_adversarial: float,
) -> PentadSystem:
    """Return a copy with the Human node's φ set to an adversarial value.

    This models the "Malicious Precision" scenario: trust is maintained at
    its default level, but the Human intent layer is directed toward an
    adversarial fixed point.  The (5,7) braid's near-maximal coupling
    ρ = 35/37 transmits this intent to all other bodies with full efficiency.

    Parameters
    ----------
    system          : PentadSystem — baseline state
    phi_adversarial : float — the adversarial φ value to inject

    Returns
    -------
    PentadSystem — copy with Ψ_human.φ = phi_adversarial
    """
    new_bodies = dict(system.bodies)
    old_human  = system.bodies[PentadLabel.HUMAN]
    new_bodies[PentadLabel.HUMAN] = ManifoldState(
        node=old_human.node,
        phi=float(phi_adversarial),
        n1=old_human.n1,
        n2=old_human.n2,
        k_cs=old_human.k_cs,
        label=old_human.label,
    )
    return PentadSystem(bodies=new_bodies, beta=system.beta)


# ---------------------------------------------------------------------------
# deception_phase_offset
# ---------------------------------------------------------------------------

def deception_phase_offset(
    system: PentadSystem,
    phi_lied: float,
) -> float:
    """Compute the Information Gap created when the Human node lies about its φ.

    A "lie" is defined as the Human body reporting φ_lied while its true
    radion value remains at φ_true = system.bodies['human'].phi.

    The detectable gap is:

        ΔI_deception = |φ_lied² − φ_true²|

    This gap appears in the pairwise coupling matrix immediately — there is
    no "delay" between the lie and its detection.

    Parameters
    ----------
    system   : PentadSystem — current state (holds φ_true)
    phi_lied : float — the φ value the human body would report

    Returns
    -------
    float — ΔI_deception ≥ 0
    """
    phi_true = system.bodies[PentadLabel.HUMAN].phi
    return float(abs(phi_lied ** 2 - phi_true ** 2))


def is_deception_detectable(
    system: PentadSystem,
    phi_lied: float,
    tol: float = DECEPTION_DETECTION_TOL,
) -> bool:
    """Return True iff the lie creates a gap above the detection threshold.

    Parameters
    ----------
    system   : PentadSystem
    phi_lied : float — lied φ value
    tol      : float — detection threshold (default DECEPTION_DETECTION_TOL)

    Returns
    -------
    bool
    """
    return deception_phase_offset(system, phi_lied) > tol


# ---------------------------------------------------------------------------
# trust_maintenance_cost
# ---------------------------------------------------------------------------

def trust_maintenance_cost(
    system: PentadSystem,
    n_steps: int = 10,
    dt: float = 0.1,
) -> float:
    """Estimate coupling energy per step required to maintain φ_trust ≥ floor.

    This captures the "Wildcard" scenario: stability is a high-energy
    achievement.  The cost is measured as the mean absolute rate of change
    of the trust body's φ across n_steps of the pentagonal coupling operator.
    A larger value means more "collective will" is required to keep the
    system in the Harmonic State.

    Parameters
    ----------
    system  : PentadSystem — initial state
    n_steps : int   — number of coupling steps to simulate (default 10)
    dt      : float — pseudo-timestep (default 0.1)

    Returns
    -------
    float — mean |Δφ_trust| per step ≥ 0

    Notes
    -----
    This measures only the coupling-operator contribution, not the full
    U_pentad step, to isolate the pure "trust maintenance" signal from
    the FTUM individual-body evolution.
    """
    total_delta = 0.0
    current = system
    for _ in range(n_steps):
        phi_before = trust_modulation(current)
        current    = _apply_pentagonal_coupling(current, dt)
        phi_after  = trust_modulation(current)
        total_delta += abs(phi_after - phi_before)
    return float(total_delta / n_steps)


# ---------------------------------------------------------------------------
# Regime-transition early-warning signal
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
    """Compute attractor-robustness observables.

    Framing
    -------
    Entropy does not reverse — the system changes which degrees of freedom
    are doing the work (Prigogine; dissipative structures).  What looks like
    "entropy changing direction" from inside the system is really constraint
    reconfiguration: one channel saturates, load shifts to adjacent channels,
    and a new dissipation topology is explored.

    This function measures that shift.  The returned ``attractor_degraded``
    flag means exactly: **"the current attractor is no longer robust."**
    It does NOT predict what happens next — only that the present constraint
    surface is no longer distributing work evenly across all channels.

    Observable markers (mapped to Pentad quantities)
    -------------------------------------------------
    1. **Channel load** for pair (i, j):
           load_{ij} = τ_{ij} × ΔI_{ij}
       where τ_{ij} is the coupling strength and ΔI_{ij} is the pairwise
       Information Gap.  This is the actual work the coupling operator is
       doing on that channel right now.

    2. **coupling_variance**: variance of the 10 channel loads.  Zero in the
       Harmonic State (all channels share the load equally).  Rises as load
       concentrates — the primary robustness signal.

    3. **transition_proximity**: saturated_channel_load / mean_channel_load.
       1.0 when perfectly balanced; rises as one channel dominates.  At
       threshold the attractor_degraded flag fires.  This is the observable
       the dissipative-structure framing asks for: "what marks the transition
       between regimes?"

    4. **active_dof_estimate**: effective rank of the 5-body state matrix.
       At the Harmonic fixed point bodies are phase-locked → low rank.
       As the system begins exploring new constraint surfaces, bodies
       decouple → rank rises toward 5.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    RegimeTransitionSignal
    """
    from itertools import combinations as _comb

    # --- Channel loads: τ_{ij} × ΔI_{ij} for all C(5,2) = 10 pairs ---
    gaps    = pentad_pairwise_gaps(system)
    tau_mat = pentad_coupling_matrix(system)

    channel_loads: Dict[Tuple[str, str], float] = {}
    for li, lj in _comb(PENTAD_LABELS, 2):
        idx_i = PENTAD_LABELS.index(li)
        idx_j = PENTAD_LABELS.index(lj)
        tau_ij = float(tau_mat[idx_i, idx_j])
        channel_loads[(li, lj)] = tau_ij * gaps[(li, lj)]

    load_values = list(channel_loads.values())

    coupling_variance      = float(np.var(load_values))
    saturated_pair         = max(channel_loads, key=lambda k: channel_loads[k])
    saturated_channel_load = float(channel_loads[saturated_pair])
    mean_channel_load      = float(np.mean(load_values))
    # When all channel loads are zero (Harmonic State) the system is perfectly
    # balanced.  Define proximity = 1.0 to indicate "no saturation signal".
    if mean_channel_load < _RTS_EPS:
        transition_proximity = 1.0
    else:
        transition_proximity = saturated_channel_load / (mean_channel_load + _RTS_EPS)

    # --- Active degrees of freedom: effective rank of 5-body state matrix ---
    state_mat = system.state_matrix()          # shape (5, state_len)
    sv = np.linalg.svd(state_mat, compute_uv=False)
    sv_max = float(sv[0]) if len(sv) > 0 else 0.0
    floor  = _ACTIVE_DOF_SV_FLOOR * sv_max
    active_dof_estimate = int(np.sum(sv >= floor)) if sv_max > _RTS_EPS else 1

    attractor_degraded = transition_proximity >= TRANSITION_PROXIMITY_THRESHOLD

    return RegimeTransitionSignal(
        coupling_variance=coupling_variance,
        saturated_pair=saturated_pair,
        saturated_channel_load=saturated_channel_load,
        mean_channel_load=mean_channel_load,
        transition_proximity=transition_proximity,
        active_dof_estimate=active_dof_estimate,
        attractor_degraded=attractor_degraded,
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
    """Model the instantaneous collapse of β·C to zero.

    This is the "Wildcard" failure: not a gradual Trust Erosion but a
    sudden, complete zeroing of the coupling field.  The function:

        1. Records the pre-erasure state (eigenvalue, φ_trust, β·C energy).
        2. Constructs the post-erasure system (φ_trust = 0).
        3. Measures the post-erasure eigenvalue of the now-decoupled matrix.
        4. Computes the cascade_risk — the fraction of coupling energy lost.

    The cascade_risk is always 1.0 for a total erasure, but the function
    also exposes delta_beta_C so callers can compare partial vs total events.

    Parameters
    ----------
    system : PentadSystem — pre-erasure state

    Returns
    -------
    TrustErasureResult
    """
    tau_before = trust_modulation(system)
    eigs_before = pentad_eigenspectrum(system)
    lmin_before = float(eigs_before[0])

    # Build post-erasure system: φ_trust → 0
    new_bodies = dict(system.bodies)
    old_trust = system.bodies[PentadLabel.TRUST]
    new_bodies[PentadLabel.TRUST] = ManifoldState(
        node=old_trust.node,
        phi=0.0,
        n1=old_trust.n1,
        n2=old_trust.n2,
        k_cs=old_trust.k_cs,
        label=old_trust.label,
    )
    erased = PentadSystem(bodies=new_bodies, beta=system.beta)

    eigs_after = pentad_eigenspectrum(erased)
    lmin_after = float(eigs_after[0])

    delta_beta_C = system.beta * tau_before
    cascade_risk = float(np.clip(tau_before, 0.0, 1.0))  # fraction of field destroyed

    stability_lost = lmin_after < BRAIDED_SOUND_SPEED

    description = (
        f"Total trust erasure: φ_trust {tau_before:.4f} → 0.  "
        f"Coupling energy lost: β·C = {delta_beta_C:.6f}.  "
        f"λ_min: {lmin_before:.4f} → {lmin_after:.4f}.  "
        + ("STABILITY LOST — all ten inter-body couplings zeroed; "
           "pentagonal orbit disintegrated."
           if stability_lost else
           "Stability margin preserved (residual trust-body coupling).")
    )

    return TrustErasureResult(
        phi_trust_before=tau_before,
        phi_trust_after=0.0,
        delta_beta_C=delta_beta_C,
        eigenvalue_before=lmin_before,
        eigenvalue_after=lmin_after,
        stability_lost=stability_lost,
        cascade_risk=cascade_risk,
        description=description,
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
    """Stress-test the (5,7) braid under asymmetric AI→Human coupling.

    Sweeps the AI-to-Human coupling weight from 1× (symmetric) to
    weight_range× (e.g. 3× = AI exerts 3× the influence it receives) in
    n_points steps.  For each weight the symmetrised eigenvalue is checked
    against the (5,7) braid stability floor c_s.

    The Berry phase per orbit is also computed — this accumulates whenever
    the coupling is non-reciprocal and is observable as a residual phase
    offset between the Human and AI bodies.

    Parameters
    ----------
    system       : PentadSystem — current state
    weight_range : float — maximum AI→Human multiplier (default 3.0)
    n_points     : int   — sweep resolution (default 20)

    Returns
    -------
    list[AsymmetricStressResult]
    """
    import math as _math

    results: List[AsymmetricStressResult] = []
    tau = trust_modulation(system)
    beta = system.beta
    tau_other = beta * tau
    trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
    human_idx = PENTAD_LABELS.index(PentadLabel.HUMAN)
    ai_idx    = PENTAD_LABELS.index(PentadLabel.AI)
    n = len(PENTAD_LABELS)

    for w_ai in np.linspace(1.0, weight_range, n_points):
        # Build the non-Hermitian coupling matrix for this weight
        mat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if i == trust_idx or j == trust_idx:
                    mat[i, j] = beta
                elif i == human_idx and j == ai_idx:
                    mat[i, j] = tau_other * 1.0        # Human → AI stays at 1×
                elif i == ai_idx and j == human_idx:
                    mat[i, j] = tau_other * float(w_ai)  # AI → Human at w_ai×
                else:
                    mat[i, j] = tau_other

        sym_mat = (mat + mat.T) / 2.0
        eigs    = np.sort(np.linalg.eigvalsh(sym_mat))
        lmin    = float(eigs[0])
        margin  = lmin - BRAIDED_SOUND_SPEED

        # Berry phase: π × (w_ai − 1) / (w_ai + 1 + ε)
        berry = (_math.pi / 2.0) * (float(w_ai) - 1.0) / (float(w_ai) + 1.0 + 1e-14)

        results.append(AsymmetricStressResult(
            w_ai_to_human=float(w_ai),
            berry_phase_rad=berry,
            stability_margin=margin,
            min_eigenvalue=lmin,
            braid_holds=margin >= 0.0,
        ))

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

import math as _math_bu  # local alias (pentad_scenarios.py already imports math as _math)

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
    """Assess dual-use biosecurity risk of AI-accelerated synthetic biology.

    Models the Groff-Vindman (2026) concern that AI × SynBio compresses both
    beneficial and harmful design cycles symmetrically.  The Unitary Pentad's
    HILS framework (governance_phi) is the countermeasure.

    Parameters
    ----------
    phi_benefit_rate  : float — base beneficial-attractor discovery rate (must be ≥ 0)
    phi_harm_rate     : float — base harmful-attractor discovery rate (must be ≥ 0)
    ai_acceleration   : float — AI speed-up multiplier applied to both (must be ≥ 1)
    governance_phi    : float — HILS governance effectiveness ∈ [0, 1]
                                0 = no oversight, 1 = perfect containment

    Returns
    -------
    BiosecurityRisk dataclass with:
      dual_use_risk_index   — R_du (lower is safer; < 0.1 is acceptable)
      governance_gap        — True if R_du ≥ DUAL_USE_SAFE_THRESHOLD
      ai_acceleration       — as provided
      governance_phi        — as provided
      effective_harm_rate   — residual harm after oversight
      effective_benefit_rate— benefit rate amplified by AI
    """
    _EPS = 1e-30
    if phi_benefit_rate < 0.0:
        raise ValueError(f"phi_benefit_rate must be ≥ 0, got {phi_benefit_rate!r}")
    if phi_harm_rate < 0.0:
        raise ValueError(f"phi_harm_rate must be ≥ 0, got {phi_harm_rate!r}")
    if ai_acceleration < 1.0:
        raise ValueError(f"ai_acceleration must be ≥ 1, got {ai_acceleration!r}")
    if not (0.0 <= governance_phi <= 1.0):
        raise ValueError(f"governance_phi must be in [0,1], got {governance_phi!r}")

    eff_benefit = phi_benefit_rate * ai_acceleration
    eff_harm    = phi_harm_rate * ai_acceleration * (1.0 - governance_phi)
    r_du        = eff_harm / (eff_benefit + _EPS)

    return BiosecurityRisk(
        dual_use_risk_index=r_du,
        governance_gap=(r_du >= DUAL_USE_SAFE_THRESHOLD),
        ai_acceleration=ai_acceleration,
        governance_phi=governance_phi,
        effective_harm_rate=eff_harm,
        effective_benefit_rate=eff_benefit,
    )
