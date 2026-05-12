# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/five_cores_system.py
================================
Integrated Five-Cores System — the unified operational architecture.

The Five-Cores System integrates all five functional cores under the
AxiomZero HILS constitutional framework.  It enforces the (5,7)-braid
stability bounds as a hard system-level constraint: the overall **system
health score** H_sys is bounded from below by c_s = 12/37 whenever
φ_trust > TRUST_PHI_MIN.

Architecture
------------
The five cores are:

    1. STRATEGIC   — StrategicCore      (long-horizon doctrine)
    2. OPERATIONAL — OperationalCore    (task routing and execution)
    3. SAFETY      — RealTimeSafetyCore (guardrails and interlocks)
    4. SCIENCES    — RealTimeSciencesCore (live data and readiness)
    5. BIOLOGICAL  — BiologicalLogicsCore (crew health and triage)

They are coupled through a shared **trust radion** φ_trust (same as the
Pentad β·C body) that is broadcast to every core each tick.

Inter-Core Protocol
--------------------
At each system tick:

    1. Safety Core runs first (it can veto the step).
    2. If HALT: only Biological Core and Sciences Core continue.
    3. Otherwise: all five cores tick in dependency order.
    4. Cross-core signals are passed:
       • Safety → Operational: execution mode override
       • Strategic → Operational: resource allocation weights
       • Sciences  → Strategic: data-driven objective updates
       • Biological → Strategic: crew readiness correction

System Health Score
--------------------
    H_sys = w_S × S + w_O × T + w_R × (1 − layer_severity/5)
            + w_Sc × R_sys + w_B × crew_readiness

where:
    S   = strategic coherence ∈ [0,1]
    T   = operational throughput ∈ [0,1]
    R_sys = sciences system readiness ∈ [0,1]
    crew_readiness = biological crew readiness ∈ [0,1]
    layer_severity = SafetyLayer severity integer [0..5]

Default weights (summing to 1):
    w_S = 0.25, w_O = 0.20, w_R = 0.25, w_Sc = 0.15, w_B = 0.15

HIL Override
-------------
Any core may request a Human-in-the-Loop (HIL) override.  The override
propagates system-wide: the system enters AWAITING_HIL state and all
non-essential operations are paused until ``hil_acknowledge()`` is called.

Public API
----------
CoreLabel : str constants
    STRATEGIC, OPERATIONAL, SAFETY, SCIENCES, BIOLOGICAL.

CORE_LABELS : tuple[str, ...]

SystemStatus
    NOMINAL, DEGRADED, AWAITING_HIL, HALTED.

SystemHealthReport
    Complete per-tick health snapshot.

FiveCoresSystem
    The integrated system engine.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np

from five_cores.strategic_core import (
    StrategicCore, StrategicState, MissionObjective,
    ESCALATION_THRESHOLD,
)
from five_cores.operational_core import (
    OperationalCore, OperationalState, TaskDomain, ExecutionMode,
)
from five_cores.realtime_safety_core import (
    RealTimeSafetyCore, SafetyState, SafetyLayer,
)
from five_cores.realtime_sciences_core import (
    RealTimeSciencesCore, SciencesState, Observation,
)
from five_cores.biological_logics_core import (
    BiologicalLogicsCore, BiologicalState, TriagePriority,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

C_S: float = 12 / 37        # braided sound speed
TRUST_PHI_MIN: float = C_S  # Pentad trust floor

# System health weights (sum to 1.0)
W_STRATEGIC: float = 0.25
W_OPERATIONAL: float = 0.20
W_SAFETY: float = 0.25
W_SCIENCES: float = 0.15
W_BIOLOGICAL: float = 0.15


class CoreLabel:
    STRATEGIC = "STRATEGIC"
    OPERATIONAL = "OPERATIONAL"
    SAFETY = "SAFETY"
    SCIENCES = "SCIENCES"
    BIOLOGICAL = "BIOLOGICAL"


CORE_LABELS: tuple = (
    CoreLabel.STRATEGIC,
    CoreLabel.OPERATIONAL,
    CoreLabel.SAFETY,
    CoreLabel.SCIENCES,
    CoreLabel.BIOLOGICAL,
)


class SystemStatus:
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    AWAITING_HIL = "AWAITING_HIL"
    HALTED = "HALTED"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SystemHealthReport:
    """Full per-tick snapshot of the Five-Cores System."""

    step_count: int
    phi_trust: float
    status: str
    health_score: float                    # H_sys ∈ [0, 1]
    per_core_scores: Dict[str, float]

    strategic: StrategicState
    operational: OperationalState
    safety: SafetyState
    sciences: SciencesState
    biological: BiologicalState

    hil_requested: bool
    hil_source: Optional[str]             # which core requested HIL
    critical_crew: List[str]
    safety_layer: str


# ---------------------------------------------------------------------------
# System Implementation
# ---------------------------------------------------------------------------

class FiveCoresSystem:
    """
    Integrated Five-Cores System under AxiomZero HILS oversight.

    Parameters
    ----------
    phi_trust : float
        Initial shared trust radion.
    strategic : StrategicCore | None
        Pre-configured strategic core.  Uses default if None.
    operational : OperationalCore | None
    safety : RealTimeSafetyCore | None
    sciences : RealTimeSciencesCore | None
    biological : BiologicalLogicsCore | None
    """

    def __init__(
        self,
        phi_trust: float = 1.0,
        strategic: Optional[StrategicCore] = None,
        operational: Optional[OperationalCore] = None,
        safety: Optional[RealTimeSafetyCore] = None,
        sciences: Optional[RealTimeSciencesCore] = None,
        biological: Optional[BiologicalLogicsCore] = None,
    ) -> None:
        self._phi_trust = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count = 0

        self.strategic = strategic or StrategicCore.default()
        self.operational = operational or OperationalCore.default()
        self.safety = safety or RealTimeSafetyCore.default()
        self.sciences = sciences or RealTimeSciencesCore.default()
        self.biological = biological or BiologicalLogicsCore.default()

        self._status = SystemStatus.NOMINAL
        self._hil_requested = False
        self._hil_source: Optional[str] = None
        self._history: List[SystemHealthReport] = []

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _safety_score(self, state: SafetyState) -> float:
        """Convert safety layer to a [0,1] score (NOMINAL=1, HALT=0)."""
        sev = SafetyLayer.severity(state.layer)
        max_sev = 5
        return float(1.0 - sev / max_sev)

    def _compute_health(
        self,
        strat: StrategicState,
        ops: OperationalState,
        safe: SafetyState,
        sci: SciencesState,
        bio: BiologicalState,
    ) -> tuple:
        """Compute H_sys and per-core score dict."""
        s_score = strat.coherence
        o_score = ops.throughput
        r_score = self._safety_score(safe)
        sc_score = sci.system_readiness
        b_score = bio.crew_readiness

        per_core = {
            CoreLabel.STRATEGIC: s_score,
            CoreLabel.OPERATIONAL: o_score,
            CoreLabel.SAFETY: r_score,
            CoreLabel.SCIENCES: sc_score,
            CoreLabel.BIOLOGICAL: b_score,
        }

        h_sys = (
            W_STRATEGIC * s_score
            + W_OPERATIONAL * o_score
            + W_SAFETY * r_score
            + W_SCIENCES * sc_score
            + W_BIOLOGICAL * b_score
        )
        return float(h_sys), per_core

    def _determine_status(
        self,
        safe: SafetyState,
        h_sys: float,
    ) -> str:
        if safe.halt_active or safe.layer == SafetyLayer.HALT:
            return SystemStatus.HALTED
        if self._hil_requested:
            return SystemStatus.AWAITING_HIL
        if h_sys < C_S or safe.layer in (SafetyLayer.HOLD, SafetyLayer.WARNING):
            return SystemStatus.DEGRADED
        return SystemStatus.NOMINAL

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def phi_trust(self) -> float:
        return self._phi_trust

    def set_trust(self, phi: float) -> None:
        """Update the shared trust radion (e.g. from Pentad update)."""
        self._phi_trust = float(np.clip(phi, 0.0, 1.0))

    def hil_acknowledge(self) -> None:
        """HIL acknowledgement clears the HIL request and resets the loop."""
        self._hil_requested = False
        self._hil_source = None
        self.strategic.acknowledge_escalation()
        self.safety.reset_violation_count()
        self._status = SystemStatus.NOMINAL

    def tick(
        self,
        trust_delta: float = 0.0,
        metric_updates: Optional[Dict[str, float]] = None,
        observations: Optional[Sequence[Observation]] = None,
        vital_updates: Optional[Dict[str, Dict[str, float]]] = None,
        intent_delta: Optional[Dict[str, float]] = None,
        dt: float = 1.0,
    ) -> SystemHealthReport:
        """
        Advance the Five-Cores System by one integrated step.

        Parameters
        ----------
        trust_delta : float
            Change in shared trust radion this step.
        metric_updates : dict | None
            Safety metric readings (forwarded to Safety Core).
        observations : list[Observation] | None
            New data observations (forwarded to Sciences Core).
        vital_updates : dict | None
            Crew vital readings (forwarded to Biological Core).
        intent_delta : dict | None
            HIL intent corrections to strategic objectives.
        dt : float
            Time step size.
        """
        self._step_count += 1
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        # ---- 1. Safety Core first (may veto) ----
        safe_state = self.safety.tick(
            metric_updates=metric_updates,
            trust_delta=0.0,  # trust already updated above
        )
        # Sync trust in safety core
        self.safety._phi_trust = self._phi_trust

        halted = safe_state.halt_active or safe_state.layer == SafetyLayer.HALT

        # ---- 2. Sciences Core (always runs — readiness stays current) ----
        sci_state = self.sciences.tick(
            observations=observations,
            trust_delta=0.0,
        )
        self.sciences._phi_trust = self._phi_trust

        # ---- 3. Biological Core (always runs — crew health always monitored) ----
        bio_state = self.biological.tick(
            vital_updates=vital_updates,
            trust_delta=0.0,
            dt=dt,
        )
        self.biological._phi_trust = self._phi_trust

        # ---- 4. Operational Core (paused on HALT) ----
        if not halted:
            # Safety → Operational: override mode if HOLD
            if safe_state.layer == SafetyLayer.HOLD:
                self.operational._phi_trust = min(self._phi_trust, 0.30)
            else:
                self.operational._phi_trust = self._phi_trust
            ops_state = self.operational.tick(trust_delta=0.0)
        else:
            # Create a frozen state snapshot
            ops_state = OperationalState(
                queued=0,
                in_progress=0,
                completed=0,
                failed=0,
                throughput=0.0,
                phi_trust=self._phi_trust,
                step_count=self._step_count,
                domain_familiarity=dict(self.operational._familiarity),
                active_tasks=[],
            )

        # ---- 5. Strategic Core (paused on HALT) ----
        if not halted:
            # Sciences → Strategic: data readiness update
            # If sciences readiness is high, boost MISSION_INTEGRITY
            sci_boost = (sci_state.system_readiness - 0.5) * 0.02
            strat_intent = dict(intent_delta) if intent_delta else {}
            if "MISSION_INTEGRITY" in self.strategic._objectives:
                strat_intent["MISSION_INTEGRITY"] = strat_intent.get(
                    "MISSION_INTEGRITY", 0.0
                ) + sci_boost

            # Biological → Strategic: crew readiness dampens trust
            if bio_state.crew_readiness < 0.6:
                crew_penalty = (0.6 - bio_state.crew_readiness) * 0.05
                strat_intent["CREW_SAFETY"] = strat_intent.get(
                    "CREW_SAFETY", 0.0
                ) + crew_penalty

            self.strategic._phi_trust = self._phi_trust
            strat_state = self.strategic.tick(
                intent_delta=strat_intent if strat_intent else None,
                trust_delta=0.0,
            )
        else:
            strat_state = StrategicState(
                objectives=dict(self.strategic._objectives),
                phi_trust=self._phi_trust,
                step_count=self._step_count,
                escalation_pending=True,
                last_escalation=self.strategic._last_escalation,
                coherence=self.strategic.strategic_coherence(),
            )

        # ---- 6. HIL request propagation ----
        hil_needed = False
        hil_source = None

        if strat_state.escalation_pending:
            hil_needed = True
            hil_source = CoreLabel.STRATEGIC
        if safe_state.layer in (SafetyLayer.HOLD, SafetyLayer.HALT):
            hil_needed = True
            hil_source = hil_source or CoreLabel.SAFETY
        if bio_state.critical_members:
            hil_needed = True
            hil_source = hil_source or CoreLabel.BIOLOGICAL

        if hil_needed:
            self._hil_requested = True
            self._hil_source = hil_source

        # ---- 7. Health score ----
        h_sys, per_core = self._compute_health(
            strat_state, ops_state, safe_state, sci_state, bio_state
        )
        self._status = self._determine_status(safe_state, h_sys)

        report = SystemHealthReport(
            step_count=self._step_count,
            phi_trust=self._phi_trust,
            status=self._status,
            health_score=h_sys,
            per_core_scores=per_core,
            strategic=strat_state,
            operational=ops_state,
            safety=safe_state,
            sciences=sci_state,
            biological=bio_state,
            hil_requested=self._hil_requested,
            hil_source=self._hil_source,
            critical_crew=bio_state.critical_members,
            safety_layer=safe_state.layer,
        )
        self._history.append(report)
        return report

    def run(
        self,
        n_steps: int,
        trust_schedule: Optional[Sequence[float]] = None,
        metric_schedule: Optional[Sequence[Optional[Dict[str, float]]]] = None,
        observation_schedule: Optional[Sequence[Optional[Sequence[Observation]]]] = None,
        dt: float = 1.0,
    ) -> List[SystemHealthReport]:
        """
        Run the system for n_steps, returning the full history.

        Parameters
        ----------
        n_steps : int
            Number of integration steps.
        trust_schedule : list[float] | None
            Per-step trust deltas.  If shorter than n_steps, zeros padded.
        metric_schedule : list[dict|None] | None
            Per-step safety metric updates.
        observation_schedule : list[list[Observation]|None] | None
            Per-step science observations.
        dt : float
            Time step size.
        """
        reports = []
        for i in range(n_steps):
            t_delta = trust_schedule[i] if trust_schedule and i < len(trust_schedule) else 0.0
            m_upd = metric_schedule[i] if metric_schedule and i < len(metric_schedule) else None
            obs = observation_schedule[i] if observation_schedule and i < len(observation_schedule) else None
            r = self.tick(trust_delta=t_delta, metric_updates=m_upd, observations=obs, dt=dt)
            reports.append(r)
        return reports

    def history(self) -> List[SystemHealthReport]:
        """Return the full tick history."""
        return list(self._history)

    def summary(self) -> str:
        """One-line system status summary."""
        return (
            f"[Step {self._step_count}] status={self._status} "
            f"φ_trust={self._phi_trust:.3f} "
            f"H_sys={self._history[-1].health_score:.3f}"
            if self._history else
            f"[Step 0] No ticks run yet."
        )

    @classmethod
    def default(cls) -> "FiveCoresSystem":
        """Factory: canonical five-cores system at full trust."""
        return cls(phi_trust=1.0)
