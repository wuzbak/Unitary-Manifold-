# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/biological_logics_core.py
======================================
Biological Logics Core — health and medicine reasoning for crew readiness,
triage, and care pathways.

The Biological Logics Core applies the φ-field radion framework to biological
health states.  Each crew member has a health radion φ_health ∈ [0, 1] that
measures overall physiological coherence; sub-radions track individual vital
categories (cardiovascular, respiratory, neurological, musculoskeletal,
immune).

Mathematical Framework
-----------------------
The biological health state is modelled as a coupled φ-field system:

    φ_health = Σ_k α_k φ_k    (weighted mean over vital categories)

where α_k > 0, Σ α_k = 1 are clinically-derived category weights.

The *triage urgency* U_i for crew member i is:

    U_i = (1 − φ_health_i) × severity_factor_i

where severity_factor encodes known risk multipliers (pre-existing conditions,
mission phase, age, etc.).

Triage Priority Levels
-----------------------
    P1 — IMMEDIATE : φ_health < 0.25  OR  U > 0.75 (life-threatening)
    P2 — URGENT    : 0.25 ≤ φ_health < 0.50  OR  U > 0.50
    P3 — DELAYED   : 0.50 ≤ φ_health < 0.75  (non-urgent, can wait)
    P4 — MINIMAL   : φ_health ≥ 0.75  (minor or self-limiting)

Care Pathways
--------------
Each priority maps to a standardised care pathway:

    P1 → RESUSCITATION: Immediate intervention, all resources, halt non-essential
    P2 → ACTIVE_CARE:   Ongoing monitoring + treatment, alert medical team
    P3 → OBSERVATION:   Scheduled check-in, comfort measures
    P4 → SELF_CARE:     Self-managed, periodic review

Physiological Modelling
------------------------
Vital categories are updated via a damped harmonic oscillator with external
interventions (medications, rest, exercise):

    dφ_k/dt = −γ_k (φ_k − φ_k^eq) + I_k(t)

where:
    γ_k = category recovery rate (inverse timescale)
    φ_k^eq = equilibrium radion (healthy setpoint = 1.0)
    I_k(t) = intervention strength at time t

Public API
----------
VitalCategory
    CARDIOVASCULAR, RESPIRATORY, NEUROLOGICAL, MUSCULOSKELETAL, IMMUNE.

TriagePriority
    P1_IMMEDIATE, P2_URGENT, P3_DELAYED, P4_MINIMAL.

CarePathway
    RESUSCITATION, ACTIVE_CARE, OBSERVATION, SELF_CARE.

CrewMember
    Dataclass: id, name, vital_radions, severity_factor, intervention.

BiologicalState
    Full system state snapshot.

BiologicalLogicsCore
    The health monitoring and triage engine.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

C_S: float = 12 / 37            # braided sound speed ≈ 0.3243

# Vital category labels
class VitalCategory:
    CARDIOVASCULAR = "CARDIOVASCULAR"
    RESPIRATORY = "RESPIRATORY"
    NEUROLOGICAL = "NEUROLOGICAL"
    MUSCULOSKELETAL = "MUSCULOSKELETAL"
    IMMUNE = "IMMUNE"


VITAL_CATEGORIES = [
    VitalCategory.CARDIOVASCULAR,
    VitalCategory.RESPIRATORY,
    VitalCategory.NEUROLOGICAL,
    VitalCategory.MUSCULOSKELETAL,
    VitalCategory.IMMUNE,
]

#: Clinical weights (sum to 1.0)
VITAL_WEIGHTS: Dict[str, float] = {
    VitalCategory.CARDIOVASCULAR: 0.30,
    VitalCategory.RESPIRATORY: 0.25,
    VitalCategory.NEUROLOGICAL: 0.20,
    VitalCategory.MUSCULOSKELETAL: 0.15,
    VitalCategory.IMMUNE: 0.10,
}

#: Recovery rates γ_k (per step)
VITAL_RECOVERY_RATES: Dict[str, float] = {
    VitalCategory.CARDIOVASCULAR: 0.02,
    VitalCategory.RESPIRATORY: 0.03,
    VitalCategory.NEUROLOGICAL: 0.01,
    VitalCategory.MUSCULOSKELETAL: 0.04,
    VitalCategory.IMMUNE: 0.015,
}


class TriagePriority:
    P1_IMMEDIATE = "P1_IMMEDIATE"
    P2_URGENT = "P2_URGENT"
    P3_DELAYED = "P3_DELAYED"
    P4_MINIMAL = "P4_MINIMAL"


class CarePathway:
    RESUSCITATION = "RESUSCITATION"
    ACTIVE_CARE = "ACTIVE_CARE"
    OBSERVATION = "OBSERVATION"
    SELF_CARE = "SELF_CARE"


PRIORITY_TO_PATHWAY: Dict[str, str] = {
    TriagePriority.P1_IMMEDIATE: CarePathway.RESUSCITATION,
    TriagePriority.P2_URGENT: CarePathway.ACTIVE_CARE,
    TriagePriority.P3_DELAYED: CarePathway.OBSERVATION,
    TriagePriority.P4_MINIMAL: CarePathway.SELF_CARE,
}

# Triage thresholds
THRESHOLD_P1: float = 0.25
THRESHOLD_P2: float = 0.50
THRESHOLD_P3: float = 0.75

URGENCY_P1: float = 0.75
URGENCY_P2: float = 0.50


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class CrewMember:
    """A single crew member's biological state."""

    member_id: str
    name: str
    vital_radions: Dict[str, float] = field(default_factory=dict)
    severity_factor: float = 1.0    # clinical risk multiplier ≥ 1
    interventions: Dict[str, float] = field(default_factory=dict)  # category → I_k

    def __post_init__(self) -> None:
        # Ensure all vital categories present
        for vc in VITAL_CATEGORIES:
            if vc not in self.vital_radions:
                self.vital_radions[vc] = 0.95
        # Clamp
        for vc in VITAL_CATEGORIES:
            self.vital_radions[vc] = float(np.clip(self.vital_radions[vc], 0.0, 1.0))
        self.severity_factor = max(1.0, float(self.severity_factor))

    @property
    def phi_health(self) -> float:
        """Weighted mean φ_health ∈ [0, 1]."""
        return float(sum(
            VITAL_WEIGHTS[vc] * self.vital_radions[vc]
            for vc in VITAL_CATEGORIES
        ))

    @property
    def urgency(self) -> float:
        """Triage urgency U = (1 − φ_health) × severity_factor, clamped [0,1]."""
        return float(np.clip((1.0 - self.phi_health) * self.severity_factor, 0.0, 1.0))

    @property
    def triage_priority(self) -> str:
        phi = self.phi_health
        u = self.urgency
        if phi < THRESHOLD_P1 or u > URGENCY_P1:
            return TriagePriority.P1_IMMEDIATE
        if phi < THRESHOLD_P2 or u > URGENCY_P2:
            return TriagePriority.P2_URGENT
        if phi < THRESHOLD_P3:
            return TriagePriority.P3_DELAYED
        return TriagePriority.P4_MINIMAL

    @property
    def care_pathway(self) -> str:
        return PRIORITY_TO_PATHWAY[self.triage_priority]


@dataclass
class BiologicalState:
    """Snapshot of the Biological Logics Core."""

    crew: Dict[str, CrewMember]
    phi_trust: float
    step_count: int
    triage_summary: Dict[str, str]           # member_id → priority
    crew_readiness: float                    # fraction of crew at P3/P4
    critical_members: List[str]              # member_ids at P1
    system_health: float                     # mean φ_health across crew


# ---------------------------------------------------------------------------
# Core Implementation
# ---------------------------------------------------------------------------

class BiologicalLogicsCore:
    """
    Biological Logics Core — crew health monitoring, triage, and care pathways.

    Parameters
    ----------
    crew : list[CrewMember] | None
        Initial crew roster.  Defaults to a 5-member canonical crew.
    phi_trust : float
        Initial trust radion (modulates intervention effectiveness).
    """

    def __init__(
        self,
        crew: Optional[List[CrewMember]] = None,
        phi_trust: float = 1.0,
    ) -> None:
        self._phi_trust = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count = 0

        if crew is None:
            crew = [
                CrewMember("C001", "Commander", severity_factor=1.0),
                CrewMember("C002", "Pilot", severity_factor=1.1),
                CrewMember("C003", "Engineer", severity_factor=1.0),
                CrewMember("C004", "Scientist", severity_factor=1.05),
                CrewMember("C005", "Medical Officer", severity_factor=1.0),
            ]
        self._crew: Dict[str, CrewMember] = {m.member_id: m for m in crew}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evolve_member(self, member: CrewMember, dt: float = 1.0) -> None:
        """Advance one member's vitals by one step via damped relaxation."""
        for vc in VITAL_CATEGORIES:
            phi = member.vital_radions[vc]
            gamma = VITAL_RECOVERY_RATES[vc]
            intervention = member.interventions.get(vc, 0.0) * self._phi_trust
            dphi = -gamma * (phi - 1.0) + intervention   # relax toward 1.0
            phi_new = float(np.clip(phi + dphi * dt, 0.0, 1.0))
            member.vital_radions[vc] = phi_new

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_crew_member(self, member: CrewMember) -> None:
        """Add a crew member to the system."""
        self._crew[member.member_id] = member

    def update_vital(
        self,
        member_id: str,
        category: str,
        value: float,
    ) -> None:
        """
        Direct vital reading update (e.g. from medical sensors).

        Parameters
        ----------
        member_id : str
            Target crew member.
        category : str
            Vital category (use VitalCategory constants).
        value : float
            New radion value ∈ [0, 1].
        """
        if member_id in self._crew:
            self._crew[member_id].vital_radions[category] = float(
                np.clip(value, 0.0, 1.0)
            )

    def apply_intervention(
        self,
        member_id: str,
        category: str,
        strength: float,
    ) -> None:
        """
        Apply a medical intervention to a vital category.

        Parameters
        ----------
        strength : float
            Intervention boost per step ∈ [0, 0.5].
        """
        if member_id in self._crew:
            self._crew[member_id].interventions[category] = float(
                np.clip(strength, 0.0, 0.5)
            )

    def remove_intervention(self, member_id: str, category: str) -> None:
        """Remove an active intervention."""
        if member_id in self._crew:
            self._crew[member_id].interventions.pop(category, None)

    def triage_all(self) -> Dict[str, str]:
        """Return triage priority for each crew member."""
        return {mid: m.triage_priority for mid, m in self._crew.items()}

    def critical_members(self) -> List[str]:
        """Return member IDs at P1_IMMEDIATE triage level."""
        return [
            mid for mid, m in self._crew.items()
            if m.triage_priority == TriagePriority.P1_IMMEDIATE
        ]

    def crew_readiness(self) -> float:
        """
        Fraction of crew not at P1 or P2 (available for full duty).

        Returns
        -------
        float ∈ [0, 1]
        """
        if not self._crew:
            return 1.0
        available = sum(
            1 for m in self._crew.values()
            if m.triage_priority in (TriagePriority.P3_DELAYED, TriagePriority.P4_MINIMAL)
        )
        return float(available / len(self._crew))

    def system_health(self) -> float:
        """Mean φ_health across all crew members."""
        if not self._crew:
            return 1.0
        return float(np.mean([m.phi_health for m in self._crew.values()]))

    def care_plan(self, member_id: str) -> Dict:
        """
        Generate a care plan for a crew member.

        Returns dict with member_id, phi_health, triage_priority,
        care_pathway, vitals, recommended_interventions.
        """
        m = self._crew.get(member_id)
        if m is None:
            return {"error": f"Unknown crew member {member_id!r}"}

        # Recommend interventions for categories below C_S
        recommendations = []
        for vc in VITAL_CATEGORIES:
            phi_v = m.vital_radions[vc]
            if phi_v < C_S:
                rec_strength = float(np.clip((C_S - phi_v) * 0.5, 0.0, 0.5))
                recommendations.append({
                    "category": vc,
                    "current_phi": phi_v,
                    "recommended_intervention": rec_strength,
                    "rationale": f"Below braided stability floor c_s={C_S:.4f}",
                })

        return {
            "member_id": member_id,
            "name": m.name,
            "phi_health": m.phi_health,
            "triage_priority": m.triage_priority,
            "care_pathway": m.care_pathway,
            "vitals": dict(m.vital_radions),
            "recommended_interventions": recommendations,
        }

    def tick(
        self,
        vital_updates: Optional[Dict[str, Dict[str, float]]] = None,
        trust_delta: float = 0.0,
        dt: float = 1.0,
    ) -> BiologicalState:
        """
        Advance the Biological Logics Core by one step.

        Parameters
        ----------
        vital_updates : dict[member_id → dict[category → value]] | None
            Direct sensor readings to apply before evolution.
        trust_delta : float
            Change in trust radion this step.
        dt : float
            Time step size (default 1.0).
        """
        self._step_count += 1
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        # Apply sensor updates
        if vital_updates:
            for mid, categories in vital_updates.items():
                for cat, val in categories.items():
                    self.update_vital(mid, cat, val)

        # Evolve all crew members
        for m in self._crew.values():
            self._evolve_member(m, dt=dt)

        triage = self.triage_all()
        return BiologicalState(
            crew=dict(self._crew),
            phi_trust=self._phi_trust,
            step_count=self._step_count,
            triage_summary=triage,
            crew_readiness=self.crew_readiness(),
            critical_members=self.critical_members(),
            system_health=self.system_health(),
        )

    @classmethod
    def default(cls) -> "BiologicalLogicsCore":
        """Factory: canonical 5-member crew at full health."""
        return cls()
