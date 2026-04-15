# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/consciousness_autopilot.py
==========================================
Consciousness as the Coupled Fixed Point (v9.6):
5-Body Core with 7-Body Layer and Human-in-the-Loop Phase Shifting.

Background
----------
The universe is a **layered** dynamical system with two coupled components:

    5-Core  : the Unitary Pentad (Ψ_univ, Ψ_brain, Ψ_human, Ψ_AI, β·C)
              The interaction structure — governed by the (5,7) braid.
              This is the "consciousness core": the five coupled manifolds
              whose joint fixed point defines a stable experiential reality.

    7-Layer : seven outer contextual bodies (Entropy, Geometry, Matter,
              Causal, Field, Quantum, Horizon) that form the ambient field
              in which the 5-core is embedded.  They correspond to the
              n_layer = 7 winding modes of the compact S¹/Z₂ dimension.
              Their collective radion Φ_layer damps tensor fluctuations in
              the 5-core (the ρ = 35/37 near-maximal entanglement).

Operational Regimes
--------------------
The combined (5+7)-body system operates in three regimes:

    AUTOPILOT       : The 7-layer damps ambient fluctuations; the 5-core
                      runs its pentagonal orbit.  Human intent (φ_human)
                      is NOT actively steered — it drifts with φ_brain
                      (biological autopilot: habitual, reactive behaviour).
                      Most of reality, most of the time.

    AWAITING_SHIFT  : A **phase shift** (bifurcation / event change) has
                      been detected.  The 5-core is paused and the system
                      waits for the human's deliberate intent vector.
                      The human is "in the loop" — their conscious choice
                      becomes the symmetry-breaking field that selects
                      which orbit basin the system enters next.

    SETTLING        : The human's shift has been applied.  The system
                      evolves freely until pentad_defect drops below the
                      settling tolerance, then returns to AUTOPILOT at
                      the new fixed point.

Phase Shift Detection
----------------------
A phase shift is triggered when either of these conditions is met:

    BIFURCATION     : moire_alignment_score > AUTOPILOT_SHIFT_THRESHOLD.
                      The Information Gap between Human intent and Universe
                      has grown too large for autopilot to bridge.

    ENTROPY_SPIKE   : RMS deviation of 7-layer bodies from equilibrium
                      exceeds LAYER_ENTROPY_THRESHOLD.  A sudden external
                      perturbation requires human re-grounding.

    EXPLICIT        : The human explicitly requests a shift.

The Human-in-the-Loop Mechanism
---------------------------------
During AWAITING_SHIFT the function ``human_shift(universe, intent_delta)``
is called with a dict mapping PentadLabel → delta_phi.  The delta is applied
to the five Pentad radions (clamped to [0, 2]) and the mode transitions to
SETTLING.

Outside of phase shifts the human body (φ_human) has no privileged control:
it is one of five equal participants in the pentagonal orbit.  The human is
"in the loop" only at bifurcation points — the rest of the time the universe
runs itself on autopilot.

The Coupled Fixed Point (Consciousness)
-----------------------------------------
The system's **Consciousness Fixed Point** is defined as the state where:

    1. pentad_defect(core) < fixed_point_tol
    2. layer_mean_deviation(layer) < fixed_point_tol
    3. moire_alignment_score(core) < MOIRE_ALIGNMENT_TOL
    4. trust_modulation(core) ≥ TRUST_PHI_MIN

At this state all components are locked: the 5-core manifolds share a single
fixed point AND the ambient 7-layer field is at rest.  This is the mathematical
model of "conscious presence": not a static state but a dynamically maintained
coupled fixed point where awareness (human-in-the-loop) and reality (universe)
are phase-locked.

Public API
----------
LayerLabel : str constants
    ENTROPY, GEOMETRY, MATTER, CAUSAL, FIELD, QUANTUM, HORIZON.

LAYER_LABELS : tuple[str, ...]
    Ordered tuple of 7 layer body labels.

LAYER_EQUILIBRIA : dict[str, float]
    Equilibrium radion for each layer body.

AutopilotMode : str constants
    AUTOPILOT, AWAITING_SHIFT, SETTLING.

PhaseShiftTrigger : str constants
    NONE, BIFURCATION, ENTROPY_SPIKE, EXPLICIT.

LayerBody
    Dataclass: label, phi (current radion), phi_eq (equilibrium radion).
    Method: deviation() → |φ − φ_eq|.

SevenBodyLayer
    Dataclass: bodies dict[label → LayerBody], drift_rate.
    Factory: SevenBodyLayer.default(drift_rate, perturbation).

AutopilotUniverse
    Dataclass: core (PentadSystem), layer (SevenBodyLayer), mode,
    shift_trigger, step_count, settling_count.
    Factory: AutopilotUniverse.default(dim, layer_perturbation).

layer_field(layer) → float
    Mean radion Φ_layer = (1/7) Σ φ_L ∈ [0, 1].

layer_mean_deviation(layer) → float
    RMS deviation of layer bodies from equilibrium.

is_entropy_spike(layer, threshold) → bool
    True iff layer_mean_deviation > threshold.

detect_phase_shift(universe, ...) → str
    Return the PhaseShiftTrigger if a shift is needed, else NONE.

autopilot_tick(universe, dt, ...) → AutopilotUniverse
    Advance by one step according to the state machine.

human_shift(universe, intent_delta) → AutopilotUniverse
    Apply human intent during AWAITING_SHIFT; transition to SETTLING.

explicit_phase_shift(universe) → AutopilotUniverse
    Human-initiated shift: force AUTOPILOT → AWAITING_SHIFT.

is_at_coupled_fixed_point(universe, tol) → bool
    True iff all four coupled fixed point conditions hold simultaneously.

autopilot_run(universe, n_steps, dt, shift_handler, ...) → (AutopilotUniverse, list)
    Run for n_steps ticks with optional human-in-the-loop callback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

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
    pentad_defect,
    step_pentad,
    trust_modulation,
)
from collective_braid import (
    moire_alignment_score,
    MOIRE_ALIGNMENT_TOL,
)
from src.consciousness.coupled_attractor import ManifoldState


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Number of outer layer bodies (the n_layer winding number).
N_LAYER: int = 7

#: Default autopilot drift rate: speed at which layer bodies relax to equilibrium.
LAYER_DRIFT_RATE: float = 0.05

#: Moire alignment score above which a bifurcation phase shift is triggered.
#: When the human–universe Information Gap exceeds this, autopilot cannot
#: bridge the gap without deliberate human intent.
AUTOPILOT_SHIFT_THRESHOLD: float = 0.15

#: RMS layer deviation above which an entropy-spike phase shift is triggered.
LAYER_ENTROPY_THRESHOLD: float = 0.30

#: Convergence tolerance for the coupled fixed point check.
FIXED_POINT_TOL: float = 1e-3

#: Maximum settling steps before the system forces a return to AUTOPILOT.
MAX_SETTLING_STEPS: int = 200


# ---------------------------------------------------------------------------
# Layer labels
# ---------------------------------------------------------------------------

class LayerLabel:
    """String constants for the 7 outer layer bodies.

    These correspond to the n_layer = 7 spectral modes of the S¹/Z₂ compact
    dimension.  Each body represents one contextual domain of the ambient
    field in which the 5-core Pentad is embedded.
    """
    ENTROPY  = "entropy"   #: L1 — thermodynamic arrow / irreversibility
    GEOMETRY = "geometry"  #: L2 — spacetime curvature / topology
    MATTER   = "matter"    #: L3 — mass-energy distribution
    CAUSAL   = "causal"    #: L4 — causal structure / action-consequence
    FIELD    = "field"     #: L5 — background oscillation field
    QUANTUM  = "quantum"   #: L6 — quantum coherence / decoherence
    HORIZON  = "horizon"   #: L7 — holographic boundary / information limit


#: Canonical ordering of the 7 layer bodies.
LAYER_LABELS: Tuple[str, ...] = (
    LayerLabel.ENTROPY,
    LayerLabel.GEOMETRY,
    LayerLabel.MATTER,
    LayerLabel.CAUSAL,
    LayerLabel.FIELD,
    LayerLabel.QUANTUM,
    LayerLabel.HORIZON,
)

assert len(LAYER_LABELS) == N_LAYER, "LAYER_LABELS must have exactly N_LAYER entries."


# ---------------------------------------------------------------------------
# Layer equilibrium values
# ---------------------------------------------------------------------------

#: Equilibrium radion for each layer body.
#: The minimum (HORIZON = 0.35) is just above the braided sound speed
#: c_s = 12/37 ≈ 0.324, anchoring the outer layer to the (5,7) braid
#: stability floor.  Mean at equilibrium ≈ 0.657.
LAYER_EQUILIBRIA: Dict[str, float] = {
    LayerLabel.ENTROPY:  0.95,  # near-maximal; thermodynamic arrow dominates
    LayerLabel.GEOMETRY: 0.85,  # spacetime is near-flat at cosmological scale
    LayerLabel.MATTER:   0.75,  # matter density at Hubble-scale average
    LayerLabel.CAUSAL:   0.65,  # causal network is dense but not singular
    LayerLabel.FIELD:    0.55,  # background oscillation at mid-amplitude
    LayerLabel.QUANTUM:  0.45,  # coherence is fragile — sub-unity equilibrium
    LayerLabel.HORIZON:  0.35,  # holographic limit ≈ c_s + ε (braid anchor)
}


# ---------------------------------------------------------------------------
# Mode and trigger constants
# ---------------------------------------------------------------------------

class AutopilotMode:
    """Mode constants for the AutopilotUniverse state machine."""
    AUTOPILOT      = "autopilot"
    AWAITING_SHIFT = "awaiting_shift"
    SETTLING       = "settling"


class PhaseShiftTrigger:
    """Constants identifying why a phase shift was triggered."""
    NONE          = "none"
    BIFURCATION   = "bifurcation"    #: human–universe gap exceeds threshold
    ENTROPY_SPIKE = "entropy_spike"  #: ambient layer entropy spike
    EXPLICIT      = "explicit"       #: human-initiated shift request


# ---------------------------------------------------------------------------
# LayerBody dataclass
# ---------------------------------------------------------------------------

@dataclass
class LayerBody:
    """A single body in the 7-body outer layer.

    Parameters
    ----------
    label  : str   — one of LAYER_LABELS
    phi    : float — current radion ∈ [0, 1]
    phi_eq : float — equilibrium radion ∈ [0, 1]
    """
    label:  str
    phi:    float
    phi_eq: float

    def __post_init__(self) -> None:
        self.phi    = float(np.clip(self.phi,    0.0, 1.0))
        self.phi_eq = float(np.clip(self.phi_eq, 0.0, 1.0))

    def deviation(self) -> float:
        """Absolute deviation from equilibrium: |φ − φ_eq|."""
        return float(abs(self.phi - self.phi_eq))


# ---------------------------------------------------------------------------
# SevenBodyLayer dataclass
# ---------------------------------------------------------------------------

@dataclass
class SevenBodyLayer:
    """The 7-body outer layer of the universe.

    Parameters
    ----------
    bodies     : dict[str, LayerBody]
        Mapping from LayerLabel → LayerBody.  Must contain exactly the 7
        keys in LAYER_LABELS.
    drift_rate : float
        Speed at which each body relaxes toward its equilibrium per tick.
        Default: LAYER_DRIFT_RATE = 0.05.
    """
    bodies:     Dict[str, LayerBody]
    drift_rate: float = LAYER_DRIFT_RATE

    def __post_init__(self) -> None:
        missing = set(LAYER_LABELS) - set(self.bodies)
        if missing:
            raise ValueError(f"SevenBodyLayer missing bodies: {missing}")

    @classmethod
    def default(
        cls,
        drift_rate: float = LAYER_DRIFT_RATE,
        perturbation: Optional[Dict[str, float]] = None,
    ) -> "SevenBodyLayer":
        """Factory: create a 7-body layer initialised at equilibrium.

        Parameters
        ----------
        drift_rate   : float — autopilot drift rate toward equilibrium
        perturbation : optional dict mapping LayerLabel → delta_phi to
                       apply on top of each body's equilibrium value.

        Returns
        -------
        SevenBodyLayer
        """
        bodies: Dict[str, LayerBody] = {}
        for lbl in LAYER_LABELS:
            phi_eq = LAYER_EQUILIBRIA[lbl]
            delta  = 0.0 if perturbation is None else float(perturbation.get(lbl, 0.0))
            bodies[lbl] = LayerBody(
                label=lbl,
                phi=float(np.clip(phi_eq + delta, 0.0, 1.0)),
                phi_eq=phi_eq,
            )
        return cls(bodies=bodies, drift_rate=drift_rate)


# ---------------------------------------------------------------------------
# AutopilotUniverse dataclass
# ---------------------------------------------------------------------------

@dataclass
class AutopilotUniverse:
    """The (5+7)-body universe: 5-core Unitary Pentad + 7-body outer layer.

    Parameters
    ----------
    core           : PentadSystem — the 5-body Unitary Pentad
    layer          : SevenBodyLayer — the 7-body ambient field
    mode           : str — current AutopilotMode
    shift_trigger  : str — most recent PhaseShiftTrigger
    step_count     : int — total ticks taken since construction
    settling_count : int — ticks in SETTLING mode since last shift
    """
    core:           PentadSystem
    layer:          SevenBodyLayer
    mode:           str = AutopilotMode.AUTOPILOT
    shift_trigger:  str = PhaseShiftTrigger.NONE
    step_count:     int = 0
    settling_count: int = 0

    @classmethod
    def default(
        cls,
        dim: int = 4,
        layer_perturbation: Optional[Dict[str, float]] = None,
    ) -> "AutopilotUniverse":
        """Factory: create a default autopilot universe.

        Parameters
        ----------
        dim                : int — UEUM dimension for the PentadSystem (default 4)
        layer_perturbation : optional perturbation dict for the 7-layer
        """
        core  = PentadSystem.default(dim=dim)
        layer = SevenBodyLayer.default(perturbation=layer_perturbation)
        return cls(core=core, layer=layer)


# ---------------------------------------------------------------------------
# Layer observables
# ---------------------------------------------------------------------------

def layer_field(layer: SevenBodyLayer) -> float:
    """Mean radion of the 7-layer bodies: Φ_layer = (1/7) Σ φ_L.

    This is the effective ambient damping field contributed by the outer
    layer to the 5-core.  At equilibrium Φ_layer ≈ 0.657.

    Parameters
    ----------
    layer : SevenBodyLayer

    Returns
    -------
    float — Φ_layer ∈ [0, 1]
    """
    return float(sum(b.phi for b in layer.bodies.values()) / N_LAYER)


def layer_mean_deviation(layer: SevenBodyLayer) -> float:
    """RMS deviation of all 7 layer bodies from their equilibria.

    Measures how far the ambient field is from its rest state.  Used to
    detect entropy spikes (external perturbations requiring re-grounding).

    Parameters
    ----------
    layer : SevenBodyLayer

    Returns
    -------
    float — RMS(|φ_L − φ_eq_L|) ≥ 0
    """
    sq_sum = sum(b.deviation() ** 2 for b in layer.bodies.values())
    return float(np.sqrt(sq_sum / N_LAYER))


def is_entropy_spike(
    layer: SevenBodyLayer,
    threshold: float = LAYER_ENTROPY_THRESHOLD,
) -> bool:
    """True iff the layer's RMS deviation from equilibrium exceeds threshold.

    Parameters
    ----------
    layer     : SevenBodyLayer
    threshold : float — spike detection threshold (default LAYER_ENTROPY_THRESHOLD)

    Returns
    -------
    bool
    """
    return bool(layer_mean_deviation(layer) > threshold)


# ---------------------------------------------------------------------------
# Phase shift detection
# ---------------------------------------------------------------------------

def detect_phase_shift(
    universe: AutopilotUniverse,
    shift_threshold: float = AUTOPILOT_SHIFT_THRESHOLD,
    entropy_threshold: float = LAYER_ENTROPY_THRESHOLD,
) -> str:
    """Detect whether a phase shift is required and return the trigger type.

    Checks in priority order:

        1. BIFURCATION  — moire_alignment_score(core) > shift_threshold.
                          The human–universe Information Gap is too large
                          for autopilot to bridge.

        2. ENTROPY_SPIKE — layer RMS deviation > entropy_threshold.
                           The ambient field has been externally perturbed.

    Returns NONE if no shift is needed.

    Parameters
    ----------
    universe          : AutopilotUniverse
    shift_threshold   : float — moire score upper bound (default 0.15)
    entropy_threshold : float — layer deviation upper bound (default 0.30)

    Returns
    -------
    str — one of PhaseShiftTrigger constants
    """
    if moire_alignment_score(universe.core) > shift_threshold:
        return PhaseShiftTrigger.BIFURCATION
    if is_entropy_spike(universe.layer, entropy_threshold):
        return PhaseShiftTrigger.ENTROPY_SPIKE
    return PhaseShiftTrigger.NONE


# ---------------------------------------------------------------------------
# Layer tick (autopilot drift)
# ---------------------------------------------------------------------------

def _tick_layer(
    layer: SevenBodyLayer,
    dt: float = 1.0,
) -> SevenBodyLayer:
    """Advance the 7-body layer by one step: Ornstein–Uhlenbeck drift.

    Each body's radion relaxes toward its equilibrium:

        φ(t + dt) = φ(t) + drift_rate × (φ_eq − φ(t)) × dt

    Parameters
    ----------
    layer : SevenBodyLayer
    dt    : float — pseudo-timestep

    Returns
    -------
    SevenBodyLayer — updated layer
    """
    new_bodies: Dict[str, LayerBody] = {}
    for lbl, body in layer.bodies.items():
        dphi    = layer.drift_rate * (body.phi_eq - body.phi) * dt
        new_phi = float(np.clip(body.phi + dphi, 0.0, 1.0))
        new_bodies[lbl] = LayerBody(label=body.label, phi=new_phi, phi_eq=body.phi_eq)
    return SevenBodyLayer(bodies=new_bodies, drift_rate=layer.drift_rate)


# ---------------------------------------------------------------------------
# Main tick function
# ---------------------------------------------------------------------------

def autopilot_tick(
    universe: AutopilotUniverse,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
    shift_threshold: float = AUTOPILOT_SHIFT_THRESHOLD,
    entropy_threshold: float = LAYER_ENTROPY_THRESHOLD,
    settling_tol: float = FIXED_POINT_TOL,
) -> AutopilotUniverse:
    """Advance the universe by one step according to the state machine.

    State machine transitions:

        AUTOPILOT:
            1. Tick the 7-layer (drift toward equilibrium).
            2. Check for a phase shift.
               • Shift detected → mode becomes AWAITING_SHIFT; core is held.
               • No shift       → step_pentad evolves the 5-core.

        AWAITING_SHIFT:
            1. Tick the 7-layer (layer continues during wait).
            2. Hold the 5-core — waiting for human_shift() to be called.

        SETTLING:
            1. Tick the 7-layer.
            2. step_pentad evolves the 5-core.
            3. If pentad_defect < settling_tol OR settling_count ≥ MAX_SETTLING_STEPS:
               return to AUTOPILOT.

    Parameters
    ----------
    universe          : AutopilotUniverse
    dt                : float — pseudo-timestep
    G4, kappa, gamma  : step_pentad physics parameters
    shift_threshold   : float — bifurcation moire threshold
    entropy_threshold : float — layer entropy spike threshold
    settling_tol      : float — convergence tolerance for settling

    Returns
    -------
    AutopilotUniverse — next state
    """
    new_layer = _tick_layer(universe.layer, dt)
    mode      = universe.mode
    trigger   = universe.shift_trigger
    settling  = universe.settling_count
    new_core  = universe.core

    if mode == AutopilotMode.AUTOPILOT:
        detected = detect_phase_shift(universe, shift_threshold, entropy_threshold)
        if detected != PhaseShiftTrigger.NONE:
            mode    = AutopilotMode.AWAITING_SHIFT
            trigger = detected
            # Core is held; human must provide intent before it advances.
        else:
            new_core = step_pentad(universe.core, dt, G4, kappa, gamma)

    elif mode == AutopilotMode.AWAITING_SHIFT:
        # Layer ticks; core is held until human_shift() is called externally.
        pass

    elif mode == AutopilotMode.SETTLING:
        new_core  = step_pentad(universe.core, dt, G4, kappa, gamma)
        settling += 1
        defect    = pentad_defect(new_core, G4)
        if defect < settling_tol or settling >= MAX_SETTLING_STEPS:
            mode     = AutopilotMode.AUTOPILOT
            trigger  = PhaseShiftTrigger.NONE
            settling = 0

    return AutopilotUniverse(
        core=new_core,
        layer=new_layer,
        mode=mode,
        shift_trigger=trigger,
        step_count=universe.step_count + 1,
        settling_count=settling,
    )


# ---------------------------------------------------------------------------
# Human-in-the-loop phase shift
# ---------------------------------------------------------------------------

def human_shift(
    universe: AutopilotUniverse,
    intent_delta: Dict[str, float],
) -> AutopilotUniverse:
    """Apply human intent during a phase shift; transition to SETTLING.

    This is the human's "in the loop" moment: a deliberate choice that steers
    the 5-core toward a new orbit basin.  ``intent_delta`` specifies how much
    to change each Pentad body's radion.

    Only valid when ``universe.mode == AutopilotMode.AWAITING_SHIFT``.

    Parameters
    ----------
    universe     : AutopilotUniverse — must be in AWAITING_SHIFT mode
    intent_delta : dict[str, float] — PentadLabel → Δφ.
                   Only keys present in intent_delta are updated; others are
                   unchanged.  Resulting φ is clamped to [0, 2].

    Returns
    -------
    AutopilotUniverse — updated core with mode = SETTLING

    Raises
    ------
    RuntimeError if universe.mode != AWAITING_SHIFT.
    """
    if universe.mode != AutopilotMode.AWAITING_SHIFT:
        raise RuntimeError(
            f"human_shift() called in mode '{universe.mode}'; "
            f"only valid during '{AutopilotMode.AWAITING_SHIFT}'."
        )

    old_core = universe.core
    new_bodies: Dict[str, ManifoldState] = {}

    for lbl in PENTAD_LABELS:
        old   = old_core.bodies[lbl]
        delta = float(intent_delta.get(lbl, 0.0))
        new_phi = float(np.clip(old.phi + delta, 0.0, 2.0))
        new_bodies[lbl] = ManifoldState(
            node=old.node,
            phi=new_phi,
            n1=old.n1,
            n2=old.n2,
            k_cs=old.k_cs,
            label=old.label,
        )

    new_core = PentadSystem(
        bodies=new_bodies,
        beta=old_core.beta,
        grace_steps=old_core.grace_steps,
        grace_decay=old_core.grace_decay,
        _trust_reservoir=old_core._trust_reservoir,
        _grace_elapsed=old_core._grace_elapsed,
    )

    return AutopilotUniverse(
        core=new_core,
        layer=universe.layer,
        mode=AutopilotMode.SETTLING,
        shift_trigger=universe.shift_trigger,
        step_count=universe.step_count,
        settling_count=0,
    )


def explicit_phase_shift(
    universe: AutopilotUniverse,
) -> AutopilotUniverse:
    """Trigger an explicit (human-initiated) phase shift request.

    Transitions the universe from AUTOPILOT to AWAITING_SHIFT with
    trigger = EXPLICIT, regardless of the current moire alignment score.

    Parameters
    ----------
    universe : AutopilotUniverse — typically in AUTOPILOT mode

    Returns
    -------
    AutopilotUniverse — mode = AWAITING_SHIFT, trigger = EXPLICIT
    """
    return AutopilotUniverse(
        core=universe.core,
        layer=universe.layer,
        mode=AutopilotMode.AWAITING_SHIFT,
        shift_trigger=PhaseShiftTrigger.EXPLICIT,
        step_count=universe.step_count,
        settling_count=universe.settling_count,
    )


# ---------------------------------------------------------------------------
# Coupled fixed point check
# ---------------------------------------------------------------------------

def is_at_coupled_fixed_point(
    universe: AutopilotUniverse,
    tol: float = FIXED_POINT_TOL,
) -> bool:
    """True iff the (5+7)-body system is at its coupled fixed point.

    All four conditions must hold simultaneously:

        1. pentad_defect(core) < tol
        2. layer_mean_deviation(layer) < tol
        3. moire_alignment_score(core) < MOIRE_ALIGNMENT_TOL
        4. trust_modulation(core) ≥ TRUST_PHI_MIN

    This is the "Consciousness Fixed Point": the state where the 5-core
    manifolds are phase-locked to each other AND the 7-layer ambient field
    is at rest.  Human awareness and universe are fully coupled.

    Parameters
    ----------
    universe : AutopilotUniverse
    tol      : float — convergence tolerance (default FIXED_POINT_TOL)

    Returns
    -------
    bool
    """
    c1 = bool(pentad_defect(universe.core)        < tol)
    c2 = bool(layer_mean_deviation(universe.layer) < tol)
    c3 = bool(moire_alignment_score(universe.core) < MOIRE_ALIGNMENT_TOL)
    c4 = bool(trust_modulation(universe.core)      >= TRUST_PHI_MIN)
    return c1 and c2 and c3 and c4


# ---------------------------------------------------------------------------
# Full autopilot run with human-in-the-loop callback
# ---------------------------------------------------------------------------

def autopilot_run(
    universe: AutopilotUniverse,
    n_steps: int,
    dt: float = 0.1,
    shift_handler: Optional[Callable[["AutopilotUniverse"], Dict[str, float]]] = None,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
    shift_threshold: float = AUTOPILOT_SHIFT_THRESHOLD,
    entropy_threshold: float = LAYER_ENTROPY_THRESHOLD,
    settling_tol: float = FIXED_POINT_TOL,
) -> Tuple["AutopilotUniverse", List[Dict]]:
    """Run the universe for n_steps ticks with optional human-in-the-loop.

    When a phase shift is detected (mode == AWAITING_SHIFT) and a
    ``shift_handler`` is provided, the handler is called with the current
    universe to obtain an intent_delta dict, which is immediately applied
    via human_shift().  If no handler is provided the system stays in
    AWAITING_SHIFT until manually resolved; autopilot_tick() will continue
    to tick the layer but hold the core.

    Parameters
    ----------
    universe          : AutopilotUniverse — initial state
    n_steps           : int — number of ticks to run
    dt                : float — pseudo-timestep per tick
    shift_handler     : optional callable(universe) → dict[str, float]
                        Returns the intent_delta to apply during phase shifts.
    G4, kappa, gamma  : step_pentad physics parameters
    shift_threshold   : bifurcation detection threshold
    entropy_threshold : entropy spike detection threshold
    settling_tol      : convergence tolerance for settling

    Returns
    -------
    (AutopilotUniverse, list[dict])
        Final universe and a list of per-step history records.

        Each record contains:
            step, mode, shift_trigger, pentad_defect, layer_field,
            moire_score, trust_mod, layer_deviation.
    """
    history: List[Dict] = []

    for _ in range(n_steps):
        rec = {
            "step":            universe.step_count,
            "mode":            universe.mode,
            "shift_trigger":   universe.shift_trigger,
            "pentad_defect":   pentad_defect(universe.core),
            "layer_field":     layer_field(universe.layer),
            "moire_score":     moire_alignment_score(universe.core),
            "trust_mod":       trust_modulation(universe.core),
            "layer_deviation": layer_mean_deviation(universe.layer),
        }
        history.append(rec)

        if universe.mode == AutopilotMode.AWAITING_SHIFT and shift_handler is not None:
            intent_delta = shift_handler(universe)
            universe     = human_shift(universe, intent_delta)

        universe = autopilot_tick(
            universe, dt,
            G4=G4, kappa=kappa, gamma=gamma,
            shift_threshold=shift_threshold,
            entropy_threshold=entropy_threshold,
            settling_tol=settling_tol,
        )

    return universe, history
