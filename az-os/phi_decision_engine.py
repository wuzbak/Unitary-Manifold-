# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/phi_decision_engine.py — φ-Debt Decision Engine (Pillar 553)

This module implements the AxiomZero OS cognitive decision engine that uses
φ-field debt signals from the physics engine (Pillar 547: phi_field_interface.py)
as inputs to OS scheduling and resource allocation decisions.

## Purpose

The φ-debt accounting system (Pillar 547) tracks the energy cost of cognitive
operations as φ-debt entries.  This module reads those signals and uses them
to drive OS-level scheduling decisions:

1. **Priority scheduling**: Agents with high φ-debt are deprioritized.
2. **KK level promotion**: Agents that reduce φ-debt are promoted to higher
   KK privilege levels (0 = ground state, 4 = highest privilege).
3. **HILS alert routing**: When the radion tension σ_φ exceeds 2.0σ, the
   human-in-the-loop is alerted with the specific debt sources.
4. **Equilibrium enforcement**: Agents operating far from the FTUM fixed
   point (|φ - φ₀| > threshold) are throttled until equilibrium is restored.

## Decision categories

Five decision types, mirroring the 5 KK privilege levels:

  Level 0 (KERNEL): physics engine heartbeat, FTUM iteration — always run
  Level 1 (SYSTEM): HILS alert routing, consensus tracking — high priority
  Level 2 (SERVICE): manager dispatch, test routing — normal priority
  Level 3 (USER):   research tasks, corpus search — low priority
  Level 4 (GUEST):  experimental adjacent tracks — throttled if φ-debt high

## φ-debt threshold table

  φ-debt < 0.1 × Ξ_c:  NORMAL — full scheduling
  φ-debt ∈ [0.1, 0.5) Ξ_c: ELEVATED — deprioritize Level 4
  φ-debt ∈ [0.5, 1.0) Ξ_c: HIGH — deprioritize Levels 3–4; alert HILS
  φ-debt ≥ 1.0 × Ξ_c:  CRITICAL — suspend Level 3–4; escalate to Level 1

where Ξ_c = 35/74 (consciousness coupling constant, Unitary Pentad).

## Pillar 553 status: AZ_OS_DECISION_ENGINE_CERTIFIED (adjacent track)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "PHI_DECISION_CONSTANTS",
    "DecisionLevel",
    "SchedulingDecision",
    "PhiDebtSignal",
    "PhiDecisionEngine",
    "kk_level_to_decision_level",
    "phi_debt_to_priority",
    "equilibrium_check",
]

# ─── Constants ────────────────────────────────────────────────────────────────

PHI_DECISION_CONSTANTS: Dict[str, Any] = {
    "xi_c": 35 / 74,           # consciousness coupling Ξ_c
    "phi0": 5 * 2 * math.pi,   # FTUM fixed point φ₀
    "delta_c": 5 / 74,         # lattice step Δc
    "kk_levels": 5,             # privilege levels 0–4
    "hils_alert_sigma": 2.0,    # radion tension alert threshold
    "critical_phi_debt_frac": 1.0,   # φ-debt / Ξ_c → CRITICAL
    "high_phi_debt_frac": 0.5,       # φ-debt / Ξ_c → HIGH
    "elevated_phi_debt_frac": 0.1,   # φ-debt / Ξ_c → ELEVATED
}

XI_C: float = PHI_DECISION_CONSTANTS["xi_c"]
PHI0: float = PHI_DECISION_CONSTANTS["phi0"]


# ─── Decision levels (mirroring KK privilege rings) ─────────────────────────

class DecisionLevel:
    """KK privilege level → scheduling decision category."""
    KERNEL = 0    # physics engine, FTUM — always scheduled
    SYSTEM = 1    # HILS routing, consensus — high priority
    SERVICE = 2   # manager dispatch — normal priority
    USER = 3      # research tasks — low priority
    GUEST = 4     # adjacent tracks — throttled under high φ-debt

    NAMES = {0: "KERNEL", 1: "SYSTEM", 2: "SERVICE", 3: "USER", 4: "GUEST"}

    @classmethod
    def name(cls, level: int) -> str:
        return cls.NAMES.get(level, f"UNKNOWN({level})")


@dataclass
class PhiDebtSignal:
    """A φ-debt signal from the physics engine or agent layer."""
    agent_id: str
    phi_debt: float          # accumulated φ-debt (natural units)
    radion_tension: float    # |φ - φ₀| / σ_φ (z-score from FTUM fixed point)
    kk_level: int            # current KK privilege level (0–4)
    timestamp: float = field(default_factory=time.time)

    def debt_fraction(self) -> float:
        """Return φ-debt as fraction of Ξ_c."""
        return abs(self.phi_debt) / XI_C

    def debt_category(self) -> str:
        """Classify the φ-debt into a scheduling category."""
        frac = self.debt_fraction()
        if frac >= PHI_DECISION_CONSTANTS["critical_phi_debt_frac"]:
            return "CRITICAL"
        elif frac >= PHI_DECISION_CONSTANTS["high_phi_debt_frac"]:
            return "HIGH"
        elif frac >= PHI_DECISION_CONSTANTS["elevated_phi_debt_frac"]:
            return "ELEVATED"
        else:
            return "NORMAL"

    def hils_alert_required(self) -> bool:
        """Return True if the radion tension requires a HILS alert."""
        return self.radion_tension >= PHI_DECISION_CONSTANTS["hils_alert_sigma"]


@dataclass
class SchedulingDecision:
    """A scheduling decision issued by the PhiDecisionEngine."""
    agent_id: str
    decision: str            # SCHEDULE, DEPRIORITIZE, THROTTLE, SUSPEND
    kk_level_current: int
    kk_level_recommended: int
    reason: str
    hils_alert: bool = False
    phi_debt_signal: Optional[PhiDebtSignal] = None

    def is_downgrade(self) -> bool:
        return self.kk_level_recommended > self.kk_level_current

    def is_upgrade(self) -> bool:
        return self.kk_level_recommended < self.kk_level_current


# ─── Core functions ───────────────────────────────────────────────────────────

def kk_level_to_decision_level(kk_level: int) -> int:
    """Map KK privilege level (0–4) to decision level (same: 0=highest).

    KK level 0 = ground state = KERNEL (highest privilege).
    KK level 4 = highest excitation = GUEST (lowest privilege).
    """
    return max(0, min(4, kk_level))


def phi_debt_to_priority(phi_debt: float) -> Tuple[int, str]:
    """Map φ-debt to a scheduling priority integer and category string.

    Returns (priority, category) where lower priority int = higher priority.
    """
    frac = abs(phi_debt) / XI_C
    if frac >= PHI_DECISION_CONSTANTS["critical_phi_debt_frac"]:
        return 100, "CRITICAL"
    elif frac >= PHI_DECISION_CONSTANTS["high_phi_debt_frac"]:
        return 70, "HIGH"
    elif frac >= PHI_DECISION_CONSTANTS["elevated_phi_debt_frac"]:
        return 40, "ELEVATED"
    else:
        return 10, "NORMAL"


def equilibrium_check(phi_value: float, sigma_phi: float = 0.1) -> Dict[str, Any]:
    """Check how far the radion φ is from the FTUM fixed point φ₀.

    Returns:
        tension_sigma: distance from φ₀ in units of σ_φ
        status: EQUILIBRIUM / TENSION / HIGH_TENSION / CRITICAL
        requires_hils: whether HILS alert is needed
    """
    deviation = abs(phi_value - PHI0)
    tension = deviation / max(sigma_phi, 1e-12)
    if tension < 1.0:
        status = "EQUILIBRIUM"
        requires_hils = False
    elif tension < 2.0:
        status = "TENSION"
        requires_hils = False
    elif tension < 3.0:
        status = "HIGH_TENSION"
        requires_hils = True
    else:
        status = "CRITICAL"
        requires_hils = True
    return {
        "phi_value": phi_value,
        "phi0": PHI0,
        "deviation": deviation,
        "tension_sigma": tension,
        "sigma_phi": sigma_phi,
        "status": status,
        "requires_hils": requires_hils,
    }


# ─── Decision Engine ─────────────────────────────────────────────────────────

class PhiDecisionEngine:
    """AxiomZero OS φ-debt decision engine.

    Reads φ-debt signals from the physics interface and issues scheduling
    decisions for the OS agent layer.
    """

    def __init__(self) -> None:
        self._signals: List[PhiDebtSignal] = []
        self._decisions: List[SchedulingDecision] = []

    def ingest_signal(self, signal: PhiDebtSignal) -> None:
        """Ingest a φ-debt signal from an agent."""
        self._signals.append(signal)

    def decide(self, signal: PhiDebtSignal) -> SchedulingDecision:
        """Issue a scheduling decision for the given φ-debt signal."""
        debt_cat = signal.debt_category()
        hils = signal.hils_alert_required()
        kk = signal.kk_level

        # Kernel-level agents are never downgraded
        if kk == DecisionLevel.KERNEL:
            return SchedulingDecision(
                agent_id=signal.agent_id,
                decision="SCHEDULE",
                kk_level_current=kk,
                kk_level_recommended=kk,
                reason="KERNEL agents are always scheduled (physics engine heartbeat).",
                hils_alert=hils,
                phi_debt_signal=signal,
            )

        # Determine decision based on debt category and KK level
        if debt_cat == "NORMAL":
            decision = "SCHEDULE"
            kk_rec = kk
            reason = f"φ-debt NORMAL ({signal.debt_fraction():.3f} Ξ_c). Full scheduling."
        elif debt_cat == "ELEVATED":
            if kk == DecisionLevel.GUEST:
                decision = "DEPRIORITIZE"
                kk_rec = kk   # no level change, but deprioritized
                reason = f"φ-debt ELEVATED ({signal.debt_fraction():.3f} Ξ_c). Deprioritize GUEST."
            else:
                decision = "SCHEDULE"
                kk_rec = kk
                reason = f"φ-debt ELEVATED but level {DecisionLevel.name(kk)} — schedule normally."
        elif debt_cat == "HIGH":
            if kk >= DecisionLevel.USER:
                decision = "THROTTLE"
                kk_rec = min(4, kk + 1)   # downgrade (higher number = lower privilege)
                reason = f"φ-debt HIGH ({signal.debt_fraction():.3f} Ξ_c). Throttle to level {kk_rec}."
            else:
                decision = "DEPRIORITIZE"
                kk_rec = kk
                reason = f"φ-debt HIGH but level {DecisionLevel.name(kk)} — deprioritize."
        else:  # CRITICAL
            if kk >= DecisionLevel.USER:
                decision = "SUSPEND"
                kk_rec = 4   # demote to GUEST until debt cleared
                reason = (
                    f"φ-debt CRITICAL ({signal.debt_fraction():.3f} Ξ_c). "
                    f"Suspend {DecisionLevel.name(kk)} agent until debt < 0.5 Ξ_c."
                )
            elif kk == DecisionLevel.SERVICE:
                decision = "THROTTLE"
                kk_rec = DecisionLevel.USER
                reason = f"φ-debt CRITICAL. Throttle SERVICE to USER level."
            else:
                decision = "DEPRIORITIZE"
                kk_rec = kk
                reason = f"φ-debt CRITICAL but high-privilege level — deprioritize only."

        sched = SchedulingDecision(
            agent_id=signal.agent_id,
            decision=decision,
            kk_level_current=kk,
            kk_level_recommended=kk_rec,
            reason=reason,
            hils_alert=hils,
            phi_debt_signal=signal,
        )
        self._decisions.append(sched)
        return sched

    def decide_all(self) -> List[SchedulingDecision]:
        """Issue decisions for all ingested signals."""
        return [self.decide(s) for s in self._signals]

    def hils_alerts(self) -> List[PhiDebtSignal]:
        """Return all signals that require HILS alerts."""
        return [s for s in self._signals if s.hils_alert_required()]

    def priority_queue(self) -> List[Tuple[int, str]]:
        """Return (priority, agent_id) sorted by scheduling priority."""
        items = []
        for signal in self._signals:
            priority, _ = phi_debt_to_priority(signal.phi_debt)
            items.append((priority + signal.kk_level * 5, signal.agent_id))
        return sorted(items)

    def equilibrium_summary(self) -> Dict[str, Any]:
        """Return a summary of the radion equilibrium status for all agents."""
        if not self._signals:
            return {"agents": 0, "status": "NO_SIGNALS"}
        tensions = [s.radion_tension for s in self._signals]
        max_tension = max(tensions)
        return {
            "agents": len(self._signals),
            "max_tension_sigma": max_tension,
            "mean_tension_sigma": sum(tensions) / len(tensions),
            "hils_alerts_pending": len(self.hils_alerts()),
            "global_status": (
                "CRITICAL" if max_tension >= 3.0
                else "HIGH_TENSION" if max_tension >= 2.0
                else "TENSION" if max_tension >= 1.0
                else "EQUILIBRIUM"
            ),
        }

    def report(self) -> Dict[str, Any]:
        """Return a full decision engine report."""
        return {
            "signals_ingested": len(self._signals),
            "decisions_issued": len(self._decisions),
            "hils_alerts": len(self.hils_alerts()),
            "priority_queue": self.priority_queue(),
            "equilibrium_summary": self.equilibrium_summary(),
        }
