# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/hils_thermalization.py
========================================
Sentinel Handover — Cold-Start Thermalization Protocol.

Background
----------
The Consciousness Autopilot operates in three regimes (AUTOPILOT,
AWAITING_SHIFT, SETTLING).  When the system has zero Human-in-the-Loop (HIL)
operators (n_hil = 0) it enters **AWAITING_SHIFT** and freezes — waiting for
the first conscious agent to inject an intent vector.

The "Cold Start" Problem
-------------------------
When the first operator (n_hil: 0 → 1) enters a frozen system they carry a
**fresh intent layer** — a φ_human value that has not yet been calibrated to
the frozen pentad state.  This creates an **Information Shock (ΔI_shock)**:

    ΔI_shock = |φ_incoming² − φ_frozen²|

If this shock is large enough, the sudden φ jump can:

    1. Drive the trust field φ_trust into sub-floor territory (< TRUST_PHI_MIN),
       triggering a false Trust Erosion collapse detection.
    2. Cause the Autopilot Sentinel to misread the initial delta as a
       "Deception" event (because ΔI > DECEPTION_DETECTION_TOL).
    3. Transiently violate the c_s stability bound by pushing the coupling
       matrix eigenvalue below BRAIDED_SOUND_SPEED before the orbit can adjust.

The Thermalization Protocol
----------------------------
The solution is a "waiting room": the new operator's φ is not applied directly
to the live system.  Instead it is passed through a **thermalization filter**
that gradually walks the incoming φ toward its target over a warm-up window:

    φ_warm(k) = φ_frozen + (φ_incoming − φ_frozen) × ramp(k / n_warmup)

where ramp(t) = t² × (3 − 2t)   (smooth-step, zero first derivative at endpoints)

This ensures:
    • dφ/dk = 0 at k = 0  (zero initial shock)
    • φ_warm(n_warmup) = φ_incoming  (full integration at the end)

The Deception Guard
--------------------
During thermalization the trust field is held at a **protected floor**
``phi_trust_guard`` (default = TRUST_PHI_MIN + 0.1) to prevent the Sentinel
from interpreting the initial intent-delta as a deception event.  Once warm-up
completes the guard is released and the live trust field resumes.

Public API
----------
ThermalState
    Dataclass tracking the handover warm-up.
    Fields: phi_incoming, phi_frozen, n_warmup, step, complete, phi_trust_guard.

ThermalReport
    Dataclass: summary of a completed thermalization run.
    Fields: n_warmup, phi_frozen, phi_incoming, delta_shock, max_transient_gap,
    deception_guard_triggered, final_stability_margin.

ThermalState.default(phi_incoming, phi_frozen, n_warmup) -> ThermalState
    Factory: create a fresh thermal state.

smooth_ramp(t) -> float
    Smooth-step function: t² × (3 − 2t).  Zero derivative at t=0 and t=1.

warmed_phi(state) -> float
    Current warmed φ for the incoming operator given the thermal state.

tick_thermalization(state) -> ThermalState
    Advance the thermal state by one step.

apply_thermalization_step(system, state) -> (PentadSystem, ThermalState)
    Apply the current warmed φ to the system's Human body, then tick.
    Returns (updated_system, updated_state).

thermalize_handover(system, phi_incoming, n_warmup, dt, seed) -> ThermalReport
    Run the full thermalization protocol from n_hil=0 to n_hil=1.
    Returns a ThermalReport summarising the handover.

information_shock(phi_incoming, phi_frozen) -> float
    Compute the raw Information Shock |φ_incoming² − φ_frozen²|.

deception_risk(phi_incoming, phi_frozen) -> bool
    True iff the shock exceeds DECEPTION_DETECTION_TOL — i.e., the raw
    application would trigger a false deception alarm.
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
from dataclasses import dataclass, field
from typing import List, Tuple

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
    pentad_coupling_matrix,
    step_pentad,
)
from pentad_scenarios import DECEPTION_DETECTION_TOL
from src.consciousness.coupled_attractor import ManifoldState

_EPS: float = 1e-14

#: Trust guard floor during thermalization (above TRUST_PHI_MIN to prevent
#: false deception detection during the warm-up window).
THERMAL_TRUST_GUARD: float = TRUST_PHI_MIN + 0.1

#: Default number of warm-up steps.
DEFAULT_N_WARMUP: int = 20


# ---------------------------------------------------------------------------
# Helper: Information Shock
# ---------------------------------------------------------------------------

def information_shock(phi_incoming: float, phi_frozen: float) -> float:
    """Raw Information Shock when an operator enters a frozen system.

    ΔI_shock = |φ_incoming² − φ_frozen²|

    Parameters
    ----------
    phi_incoming : float — radion of the entering operator
    phi_frozen   : float — radion of the frozen (AWAITING_SHIFT) human body

    Returns
    -------
    float — ΔI_shock ≥ 0
    """
    return float(abs(phi_incoming ** 2 - phi_frozen ** 2))


def deception_risk(phi_incoming: float, phi_frozen: float) -> bool:
    """True iff a direct (unthermalized) handover would trigger a deception alarm.

    The Pentad orbit flags any pairwise Information Gap above
    DECEPTION_DETECTION_TOL as a potential deception event.

    Parameters
    ----------
    phi_incoming : float
    phi_frozen   : float

    Returns
    -------
    bool
    """
    return information_shock(phi_incoming, phi_frozen) > DECEPTION_DETECTION_TOL


# ---------------------------------------------------------------------------
# smooth_ramp
# ---------------------------------------------------------------------------

def smooth_ramp(t: float) -> float:
    """Smooth-step ramp: t² (3 − 2t), clipped to [0, 1].

    Properties:
        ramp(0) = 0,  ramp(1) = 1
        ramp'(0) = 0, ramp'(1) = 0   (zero velocity at both ends)

    Parameters
    ----------
    t : float — normalised time ∈ [0, 1]

    Returns
    -------
    float ∈ [0, 1]
    """
    t_c = float(np.clip(t, 0.0, 1.0))
    return t_c * t_c * (3.0 - 2.0 * t_c)


# ---------------------------------------------------------------------------
# ThermalState
# ---------------------------------------------------------------------------

@dataclass
class ThermalState:
    """Tracks the warm-up state for a single HIL handover.

    Attributes
    ----------
    phi_incoming     : float — target φ of the entering operator
    phi_frozen       : float — φ of the frozen human body in the system
    n_warmup         : int   — total warm-up steps
    step             : int   — current step (0 … n_warmup)
    complete         : bool  — True once step ≥ n_warmup
    phi_trust_guard  : float — minimum trust φ enforced during warm-up
    """
    phi_incoming:    float
    phi_frozen:      float
    n_warmup:        int
    step:            int   = 0
    complete:        bool  = False
    phi_trust_guard: float = THERMAL_TRUST_GUARD

    @classmethod
    def default(
        cls,
        phi_incoming: float,
        phi_frozen: float,
        n_warmup: int = DEFAULT_N_WARMUP,
    ) -> "ThermalState":
        """Factory: create a fresh (step=0) thermal state.

        Parameters
        ----------
        phi_incoming : float — incoming operator's radion
        phi_frozen   : float — frozen system's human-body radion
        n_warmup     : int   — warm-up duration in steps (default 20)
        """
        return cls(
            phi_incoming=float(phi_incoming),
            phi_frozen=float(phi_frozen),
            n_warmup=max(1, int(n_warmup)),
            step=0,
            complete=False,
            phi_trust_guard=THERMAL_TRUST_GUARD,
        )


# ---------------------------------------------------------------------------
# warmed_phi
# ---------------------------------------------------------------------------

def warmed_phi(state: ThermalState) -> float:
    """Current warmed φ for the incoming operator.

    φ_warm(k) = φ_frozen + (φ_incoming − φ_frozen) × smooth_ramp(k / n_warmup)

    Parameters
    ----------
    state : ThermalState

    Returns
    -------
    float — interpolated radion value
    """
    if state.complete:
        return float(state.phi_incoming)
    t = state.step / max(state.n_warmup, 1)
    return float(state.phi_frozen + (state.phi_incoming - state.phi_frozen) * smooth_ramp(t))


# ---------------------------------------------------------------------------
# tick_thermalization
# ---------------------------------------------------------------------------

def tick_thermalization(state: ThermalState) -> ThermalState:
    """Advance the thermal state by one step.

    Parameters
    ----------
    state : ThermalState

    Returns
    -------
    ThermalState — updated state
    """
    new_step = state.step + 1
    complete = new_step >= state.n_warmup
    return ThermalState(
        phi_incoming=state.phi_incoming,
        phi_frozen=state.phi_frozen,
        n_warmup=state.n_warmup,
        step=new_step,
        complete=complete,
        phi_trust_guard=state.phi_trust_guard,
    )


# ---------------------------------------------------------------------------
# _set_body_phi  (internal helper)
# ---------------------------------------------------------------------------

def _set_body_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    """Return a copy of system with a single body's φ replaced."""
    new_bodies = dict(system.bodies)
    old = system.bodies[label]
    new_bodies[label] = ManifoldState(
        node=old.node,
        phi=float(phi),
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
# apply_thermalization_step
# ---------------------------------------------------------------------------

def apply_thermalization_step(
    system: PentadSystem,
    state: ThermalState,
) -> Tuple[PentadSystem, ThermalState]:
    """Apply the current warmed φ to the system's Human body, then tick.

    During warm-up the trust body's φ is also guarded: if the live φ_trust
    would drop below phi_trust_guard it is clamped to phi_trust_guard.  This
    prevents the Sentinel from misreading the initial delta as deception.

    Parameters
    ----------
    system : PentadSystem — current system state
    state  : ThermalState — current thermal state

    Returns
    -------
    (PentadSystem, ThermalState) — updated system and updated thermal state
    """
    phi_w = warmed_phi(state)
    sys2  = _set_body_phi(system, PentadLabel.HUMAN, phi_w)

    # Trust guard: prevent sub-floor collapse during warm-up.
    if not state.complete:
        live_trust = sys2.bodies[PentadLabel.TRUST].phi
        if live_trust < state.phi_trust_guard:
            sys2 = _set_body_phi(sys2, PentadLabel.TRUST, state.phi_trust_guard)

    new_state = tick_thermalization(state)
    return sys2, new_state


# ---------------------------------------------------------------------------
# ThermalReport
# ---------------------------------------------------------------------------

@dataclass
class ThermalReport:
    """Summary of a completed thermalization run.

    Attributes
    ----------
    n_warmup                : int   — warm-up steps used
    phi_frozen              : float — frozen human φ at handover start
    phi_incoming            : float — incoming operator's target φ
    delta_shock             : float — raw Information Shock (unthermalized)
    max_transient_gap       : float — maximum ΔI_{human, any} observed during warm-up
    deception_guard_triggered : bool — True if trust guard was clamped at any step
    final_stability_margin  : float — λ_min(τ^sym) − c_s at end of warm-up
    """
    n_warmup:                   int
    phi_frozen:                 float
    phi_incoming:               float
    delta_shock:                float
    max_transient_gap:          float
    deception_guard_triggered:  bool
    final_stability_margin:     float


# ---------------------------------------------------------------------------
# thermalize_handover
# ---------------------------------------------------------------------------

def thermalize_handover(
    system: PentadSystem,
    phi_incoming: float,
    n_warmup: int = DEFAULT_N_WARMUP,
    dt: float = 0.05,
) -> ThermalReport:
    """Run the full thermalization protocol for an n=0 → n=1 HIL handover.

    Steps
    -----
    1. Record the frozen human φ and compute the raw Information Shock.
    2. Create a ThermalState for the warm-up window.
    3. For each warm-up step: apply_thermalization_step + one deterministic
       pentad step.
    4. After warm-up completes, record final diagnostics.

    Parameters
    ----------
    system       : PentadSystem — frozen system (n_hil = 0, AWAITING_SHIFT)
    phi_incoming : float — radion of the entering operator
    n_warmup     : int   — warm-up duration in steps (default 20)
    dt           : float — pseudo-timestep for pentad evolution (default 0.05)

    Returns
    -------
    ThermalReport
    """
    phi_frozen = system.bodies[PentadLabel.HUMAN].phi
    shock = information_shock(phi_incoming, phi_frozen)
    state = ThermalState.default(phi_incoming, phi_frozen, n_warmup)

    max_gap = 0.0
    guard_triggered = False
    current = system

    for _ in range(n_warmup):
        # Check trust guard before applying step
        prev_trust = current.bodies[PentadLabel.TRUST].phi
        current, state = apply_thermalization_step(current, state)
        new_trust  = current.bodies[PentadLabel.TRUST].phi
        if new_trust != prev_trust and new_trust == state.phi_trust_guard:
            guard_triggered = True

        # Advance the pentad dynamics
        current = step_pentad(current, dt=dt)

        # Record the peak Human-body Information Gap
        gaps = pentad_pairwise_gaps(current)
        human_gaps = [v for (a, b), v in gaps.items()
                      if PentadLabel.HUMAN in (a, b)]
        if human_gaps:
            max_gap = max(max_gap, max(human_gaps))

    # Final stability margin (symmetric coupling, post warm-up)
    tau_mat = pentad_coupling_matrix(current)
    sym_mat = (tau_mat + tau_mat.T) / 2.0
    eigs    = np.linalg.eigvalsh(sym_mat)
    final_margin = float(np.min(eigs) - BRAIDED_SOUND_SPEED)

    return ThermalReport(
        n_warmup=n_warmup,
        phi_frozen=phi_frozen,
        phi_incoming=phi_incoming,
        delta_shock=shock,
        max_transient_gap=max_gap,
        deception_guard_triggered=guard_triggered,
        final_stability_margin=final_margin,
    )
