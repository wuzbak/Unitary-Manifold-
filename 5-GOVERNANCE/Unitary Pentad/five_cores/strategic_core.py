# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/strategic_core.py
=============================
Strategic Core — long-horizon goals, doctrine, allocation, and escalation.

The Strategic Core is the doctrine layer of the Five-Cores architecture.  It
holds the mission's long-horizon objectives, allocates resources across time
horizons, and determines when a situation requires escalation to the Human-in-
the-Loop (HIL) steward.

Mathematical Framework
-----------------------
The Strategic Core models each mission objective as a **φ-field** radion whose
value ∈ [0, 1] tracks proximity to the objective.  The doctrine is expressed
as a priority-weighted potential well:

    V_strategic(φ_i) = w_i × (1 − φ_i)²

where w_i is the objective weight (normalised so Σ w_i = 1).

The *strategic coherence* score S ∈ [0, 1] is:

    S = 1 − Σᵢ w_i (1 − φ_i)²

S = 1 means all objectives are at their target; S = 0 means total mission
failure.

Escalation Logic
-----------------
Escalation is triggered when either:
    • S < ESCALATION_THRESHOLD  (strategic coherence too low)
    • any single objective's φ_i < CRITICAL_OBJECTIVE_FLOOR  (objective critical)
    • time since last HIL review > MAX_AUTONOMOUS_STEPS  (mandatory review)

Allocation
-----------
Resources are allocated by the softmax of the negative potential (i.e., the
resource pressure goes to the most-lagging objective):

    pressure_i = w_i × (1 − φ_i)²
    allocation_i = softmax(pressure_i / temperature)

Lower temperature → more concentrated allocation (focus on weakest link).

Public API
----------
MissionObjective
    Dataclass: label, phi, weight, critical_floor.

StrategicState
    Dataclass: objectives dict, phi_trust, step_count, escalation_pending.

StrategicCore
    The strategic core engine.  Methods:
        tick(intent_delta, trust_delta) → StrategicState
        strategic_coherence() → float
        resource_allocation(temperature) → dict[str, float]
        escalation_required() → bool
        add_objective(obj) → None
        doctrine_summary() → str
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Constants (aligned with Pentad braid constants)
# ---------------------------------------------------------------------------

#: Braided sound speed — the stability floor inherited from the (5,7) braid.
C_S: float = 12 / 37  # ≈ 0.3243

#: Below this strategic coherence value, escalation is mandatory.
ESCALATION_THRESHOLD: float = 0.40

#: Any objective below this φ value is declared critical.
CRITICAL_OBJECTIVE_FLOOR: float = C_S  # ≈ 0.324

#: Maximum number of autonomous ticks before a mandatory HIL review.
MAX_AUTONOMOUS_STEPS: int = 74  # = k_cs — the CS resonance level

#: Default allocation temperature (controls focus concentration).
DEFAULT_TEMPERATURE: float = 0.25

#: Default trust floor inherited from Pentad.
TRUST_PHI_MIN: float = C_S

#: Maximum doctrine weight for a single objective (prevents domination).
MAX_SINGLE_WEIGHT: float = 35 / 37  # kinetic mixing depth ρ


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MissionObjective:
    """A single tracked mission objective."""

    label: str
    phi: float = 0.5          # current progress radion ∈ [0, 1]
    weight: float = 1.0       # relative importance
    critical_floor: float = CRITICAL_OBJECTIVE_FLOOR

    def __post_init__(self) -> None:
        self.phi = float(np.clip(self.phi, 0.0, 1.0))
        self.weight = max(0.0, float(self.weight))

    @property
    def potential(self) -> float:
        """Quadratic potential V = w × (1 − φ)²."""
        return self.weight * (1.0 - self.phi) ** 2

    @property
    def is_critical(self) -> bool:
        """True when this objective is below its critical floor."""
        return self.phi < self.critical_floor


@dataclass
class EscalationEvent:
    """Record of a single escalation trigger."""

    step: int
    reason: str
    coherence: float
    critical_objectives: List[str]


@dataclass
class StrategicState:
    """Snapshot of the Strategic Core at a given tick."""

    objectives: Dict[str, MissionObjective]
    phi_trust: float
    step_count: int
    escalation_pending: bool
    last_escalation: Optional[EscalationEvent]
    coherence: float


# ---------------------------------------------------------------------------
# Core Implementation
# ---------------------------------------------------------------------------

class StrategicCore:
    """
    Strategic Core — long-horizon mission doctrine and escalation engine.

    Parameters
    ----------
    objectives : list[MissionObjective] | None
        Initial mission objectives.  If None, a default single-objective
        ``MISSION_INTEGRITY`` is used.
    phi_trust : float
        Initial trust radion (inherited from Pentad, default = 1.0).
    """

    def __init__(
        self,
        objectives: Optional[List[MissionObjective]] = None,
        phi_trust: float = 1.0,
    ) -> None:
        if objectives is None:
            objectives = [
                MissionObjective("MISSION_INTEGRITY", phi=0.9, weight=1.0),
                MissionObjective("RESOURCE_EFFICIENCY", phi=0.7, weight=0.5),
                MissionObjective("CREW_SAFETY", phi=1.0, weight=2.0),
            ]
        self._objectives: Dict[str, MissionObjective] = {
            o.label: o for o in objectives
        }
        self._phi_trust: float = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count: int = 0
        self._escalation_pending: bool = False
        self._last_escalation: Optional[EscalationEvent] = None
        self._steps_since_hil: int = 0

        # Normalize weights
        self._normalize_weights()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_weights(self) -> None:
        total = sum(o.weight for o in self._objectives.values())
        if total > 0:
            for o in self._objectives.values():
                o.weight /= total

    def _clamp_obj(self) -> None:
        for o in self._objectives.values():
            o.phi = float(np.clip(o.phi, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_objective(self, obj: MissionObjective) -> None:
        """Add or replace a mission objective, then re-normalise weights."""
        self._objectives[obj.label] = obj
        self._normalize_weights()

    def strategic_coherence(self) -> float:
        """
        Strategic coherence S ∈ [0, 1].

        S = 1 − Σᵢ wᵢ (1 − φᵢ)²
        """
        if not self._objectives:
            return 1.0
        total_potential = sum(o.potential for o in self._objectives.values())
        return float(np.clip(1.0 - total_potential, 0.0, 1.0))

    def resource_allocation(self, temperature: float = DEFAULT_TEMPERATURE) -> Dict[str, float]:
        """
        Softmax allocation of resources to objectives by pressure.

        Higher pressure (lagging objective) → more resource.

        Returns
        -------
        dict mapping objective label → allocation fraction in [0, 1],
        summing to 1.
        """
        if not self._objectives:
            return {}
        labels = list(self._objectives.keys())
        pressures = np.array([self._objectives[l].potential for l in labels])
        temperature = max(temperature, 1e-8)
        scaled = pressures / temperature
        scaled -= scaled.max()  # numerical stability
        exps = np.exp(scaled)
        alloc = exps / exps.sum()
        return {l: float(a) for l, a in zip(labels, alloc)}

    def critical_objectives(self) -> List[str]:
        """Return labels of objectives currently below their critical floor."""
        return [l for l, o in self._objectives.items() if o.is_critical]

    def escalation_required(self) -> bool:
        """True if any escalation condition is satisfied."""
        if self.strategic_coherence() < ESCALATION_THRESHOLD:
            return True
        if self.critical_objectives():
            return True
        if self._steps_since_hil >= MAX_AUTONOMOUS_STEPS:
            return True
        if self._phi_trust < TRUST_PHI_MIN:
            return True
        return False

    def tick(
        self,
        intent_delta: Optional[Dict[str, float]] = None,
        trust_delta: float = 0.0,
    ) -> StrategicState:
        """
        Advance the Strategic Core by one time step.

        Parameters
        ----------
        intent_delta : dict[label → Δφ] | None
            HIL intent corrections applied to objective radions.
        trust_delta : float
            Change in the trust radion this step.

        Returns
        -------
        StrategicState
            Current state snapshot after the tick.
        """
        self._step_count += 1
        self._steps_since_hil += 1

        # Apply trust update
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        # Apply intent corrections (HIL input)
        if intent_delta:
            for label, delta in intent_delta.items():
                if label in self._objectives:
                    self._objectives[label].phi += delta
        self._clamp_obj()

        # Natural objective drift toward target (exponential relaxation)
        tau = 50.0  # relaxation timescale in steps
        for o in self._objectives.values():
            o.phi += (1.0 - o.phi) / tau
        self._clamp_obj()

        # Escalation check
        needs_esc = self.escalation_required()
        if needs_esc and not self._escalation_pending:
            ev = EscalationEvent(
                step=self._step_count,
                reason="auto",
                coherence=self.strategic_coherence(),
                critical_objectives=self.critical_objectives(),
            )
            self._last_escalation = ev
            self._escalation_pending = True
        elif not needs_esc:
            self._escalation_pending = False

        return StrategicState(
            objectives=dict(self._objectives),
            phi_trust=self._phi_trust,
            step_count=self._step_count,
            escalation_pending=self._escalation_pending,
            last_escalation=self._last_escalation,
            coherence=self.strategic_coherence(),
        )

    def acknowledge_escalation(self) -> None:
        """HIL acknowledgement of the escalation; resets the HIL timer."""
        self._escalation_pending = False
        self._steps_since_hil = 0

    def doctrine_summary(self) -> str:
        """Return a human-readable doctrine summary."""
        lines = [
            "=== Strategic Core Doctrine Summary ===",
            f"Step: {self._step_count}   Trust: {self._phi_trust:.3f}   Coherence: {self.strategic_coherence():.3f}",
            "",
        ]
        alloc = self.resource_allocation()
        for label, obj in self._objectives.items():
            crit = " [CRITICAL]" if obj.is_critical else ""
            lines.append(
                f"  {label}: φ={obj.phi:.3f}  w={obj.weight:.3f}"
                f"  alloc={alloc.get(label, 0):.3f}{crit}"
            )
        if self._escalation_pending:
            lines.append("\n⚠  ESCALATION PENDING — HIL review required")
        return "\n".join(lines)

    @classmethod
    def default(cls) -> "StrategicCore":
        """Factory: canonical 3-objective strategic core."""
        return cls()

    @classmethod
    def mission_profile(cls, labels: List[str], weights: List[float]) -> "StrategicCore":
        """
        Factory: build a Strategic Core from explicit objective names and weights.

        Parameters
        ----------
        labels : list[str]
            Objective labels (e.g. ``['NAVIGATION', 'PROPULSION', 'LIFE_SUPPORT']``).
        weights : list[float]
            Relative importance weights (need not be normalised).
        """
        objs = [
            MissionObjective(label=l, phi=0.8, weight=float(w))
            for l, w in zip(labels, weights)
        ]
        return cls(objectives=objs)
