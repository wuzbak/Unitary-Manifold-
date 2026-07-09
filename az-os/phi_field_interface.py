# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/phi_field_interface.py — φ-Field Interface: Physics Engine ↔ OS Convergence Layer

This module is Pillar 547: the convergence layer that couples the AxiomZero
cognitive OS (az-os/) to the Unitary Manifold physics engine (src/core/).

## Purpose

The physics engine and the OS layer are converging on a shared φ-field
interface.  This interface defines:

1. **φ-Field State** — a shared data structure that both the physics engine
   (FieldState, evolution.py) and the OS (StateDB, phi_ledger) can read/write.

2. **φ-Debt Accounting** — the OS tracks cognitive resource usage via
   φ-debt entries in the phi_ledger table.  This module bridges those entries
   to the physics-layer φ-field evolution.

3. **Radion-OS Coupling** — the radion field φ(x) from the 5D KK reduction
   provides the OS with a coherent measure of "field tension" (how far the
   system is from the FTUM fixed point).  This can trigger HILS alerts when
   the radion deviates significantly from φ₀.

4. **KK Level Ring** — the OS KK privilege levels (0–4) mirror the KK tower
   levels in the physics engine.  Level 0 is the kernel (ground-state radion);
   higher levels correspond to KK excitations.

## Interface Contract

    phi_state = PhiFieldState.from_physics_engine()
    os_tension = phi_state.os_tension()
    phi_state.update_os_phi_debt(agent_id, delta_phi)

## Status

Pillar 547: AZ_OS_PHI_FIELD_INTERFACE_CERTIFIED.
This is an infrastructure/convergence pillar — no new hardgate physics.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = [
    "PHI_FIELD_CONSTANTS",
    "PhiFieldState",
    "PhiDebtEntry",
    "PhiFieldInterface",
    "kk_level_to_radion_mode",
    "radion_tension",
    "phi_debt_to_energy",
]

# ─── Physics constants (shared with physics engine) ──────────────────────────

PHI_FIELD_CONSTANTS: Dict[str, Any] = {
    "phi0": 5 * 2 * math.pi * 1.0,  # φ₀ = 5 × 2π (Pillar 56 closure)
    "n_w": 5,                         # winding number
    "k_cs": 74,                       # Chern-Simons level
    "c_s": 12 / 37,                   # braided sound speed
    "delta_c": 5 / 74,                # fundamental lattice step
    "kk_levels": 5,                   # KK privilege rings: 0–4
    "xi_c": 35 / 74,                  # consciousness coupling Ξ_c
    "sentinel_capacity": 12 / 37,     # per-axiom entropy capacity
}

# Canonical FTUM fixed point (from φ₀ closure, Pillar 56)
PHI0: float = PHI_FIELD_CONSTANTS["phi0"]


@dataclass
class PhiDebtEntry:
    """One φ-debt accounting entry from the OS phi_ledger."""
    agent_id: str
    manager: str      # M1–M7
    kk_level: int     # 0–4
    delta_phi: float  # change in φ-debt
    timestamp: float = field(default_factory=time.time)
    task_id: str = ""
    reason: str = ""

    def energy_cost(self) -> float:
        """Estimate the KK energy cost of this φ-debt entry.

        Energy ∝ (Δφ)² × M_KK² / (2 φ₀²)
        where M_KK sets the scale and φ₀ is the FTUM fixed point.
        """
        return (self.delta_phi ** 2) / (2.0 * PHI0 ** 2)

    def kk_mode_number(self) -> int:
        """Return the KK mode number corresponding to this agent's level."""
        return kk_level_to_radion_mode(self.kk_level)


@dataclass
class PhiFieldState:
    """Shared φ-field state between the physics engine and the OS.

    This bridges:
    - src/core/evolution.py: FieldState (physics layer)
    - az-os/state.py: phi_ledger entries (OS layer)
    """
    phi_value: float         # current radion field value φ
    phi_dot: float = 0.0     # field velocity ∂_t φ
    kk_level: int = 0        # KK level context (0 = ground state)
    step: int = 0            # evolution step
    phi_debt_total: float = 0.0  # accumulated OS φ-debt
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def at_fixed_point(cls) -> "PhiFieldState":
        """Create a PhiFieldState at the FTUM fixed point (φ = φ₀)."""
        return cls(phi_value=PHI0, phi_dot=0.0, kk_level=0)

    def os_tension(self) -> float:
        """Compute OS tension = (φ - φ₀)² / φ₀².

        This measures how far the field is from the FTUM attractor.
        A tension > 0.01 should trigger a HILS alert.
        """
        return (self.phi_value - PHI0) ** 2 / PHI0 ** 2

    def is_near_fixed_point(self, tolerance: float = 0.01) -> bool:
        """True if the field is within tolerance of the FTUM fixed point."""
        return self.os_tension() < tolerance

    def update_phi_debt(self, delta_phi: float) -> "PhiFieldState":
        """Return a new state with updated φ-debt accumulation."""
        return PhiFieldState(
            phi_value=self.phi_value + delta_phi,
            phi_dot=self.phi_dot,
            kk_level=self.kk_level,
            step=self.step + 1,
            phi_debt_total=self.phi_debt_total + abs(delta_phi),
            timestamp=time.time(),
        )

    def kk_excitation_energy(self) -> float:
        """KK excitation energy at the current KK level.

        E_n = n × M_KK where n = kk_mode_number and M_KK is from Pillar 56.
        Uses n_w / k_cs as the KK step in natural units.
        """
        n = kk_level_to_radion_mode(self.kk_level)
        return n * (PHI_FIELD_CONSTANTS["n_w"] / PHI_FIELD_CONSTANTS["k_cs"])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage in StateDB phi_ledger."""
        return {
            "phi_value": self.phi_value,
            "phi_dot": self.phi_dot,
            "kk_level": self.kk_level,
            "step": self.step,
            "phi_debt_total": self.phi_debt_total,
            "os_tension": self.os_tension(),
            "near_fixed_point": self.is_near_fixed_point(),
            "kk_excitation_energy": self.kk_excitation_energy(),
            "timestamp": self.timestamp,
        }


class PhiFieldInterface:
    """Bidirectional interface between the physics engine and the OS.

    Usage:
        interface = PhiFieldInterface()
        state = interface.get_current_state()
        interface.record_phi_debt(agent_id, manager, kk_level, delta_phi)
        tension = interface.aggregate_os_tension()
    """

    def __init__(self) -> None:
        self._state: PhiFieldState = PhiFieldState.at_fixed_point()
        self._debt_log: List[PhiDebtEntry] = []
        self._hils_alerts: List[Dict[str, Any]] = []

    def get_current_state(self) -> PhiFieldState:
        """Return the current φ-field state."""
        return self._state

    def record_phi_debt(
        self,
        agent_id: str,
        manager: str,
        kk_level: int,
        delta_phi: float,
        task_id: str = "",
        reason: str = "",
    ) -> PhiDebtEntry:
        """Record an OS φ-debt entry and update the field state.

        Parameters
        ----------
        agent_id: The agent ID (e.g., 'M1.MetricAgent').
        manager: The manager ID (M1–M7).
        kk_level: KK privilege level (0–4).
        delta_phi: Change in φ caused by this agent's operation.
        task_id: Optional task reference.
        reason: Human-readable description of the operation.
        """
        if kk_level not in range(5):
            raise ValueError(f"kk_level must be 0–4, got {kk_level}")

        entry = PhiDebtEntry(
            agent_id=agent_id,
            manager=manager,
            kk_level=kk_level,
            delta_phi=delta_phi,
            task_id=task_id,
            reason=reason,
        )
        self._debt_log.append(entry)
        self._state = self._state.update_phi_debt(delta_phi)

        # Check for HILS alert
        if self._state.os_tension() > 0.01:
            self._hils_alerts.append({
                "alert_type": "PHI_TENSION_ELEVATED",
                "tension": self._state.os_tension(),
                "agent_id": agent_id,
                "timestamp": time.time(),
                "recommendation": (
                    "OS φ-field tension elevated above threshold. "
                    "Consider invoking HILS approval for further operations."
                ),
            })

        return entry

    def aggregate_os_tension(self) -> Dict[str, Any]:
        """Compute aggregate OS tension statistics."""
        total_debt = sum(abs(e.delta_phi) for e in self._debt_log)
        per_manager: Dict[str, float] = {}
        for entry in self._debt_log:
            per_manager[entry.manager] = per_manager.get(entry.manager, 0.0) + abs(entry.delta_phi)

        return {
            "current_tension": self._state.os_tension(),
            "near_fixed_point": self._state.is_near_fixed_point(),
            "total_phi_debt": total_debt,
            "debt_by_manager": per_manager,
            "hils_alerts_raised": len(self._hils_alerts),
            "phi_value": self._state.phi_value,
            "phi0": PHI0,
            "field_entries": len(self._debt_log),
        }

    def reset_to_fixed_point(self) -> None:
        """Reset the field to the FTUM fixed point (φ = φ₀).

        This is the HILS-governed recovery action for elevated tension.
        """
        self._state = PhiFieldState.at_fixed_point()
        self._hils_alerts.clear()

    def debt_log(self) -> List[PhiDebtEntry]:
        """Return the full φ-debt log."""
        return list(self._debt_log)

    def hils_alerts(self) -> List[Dict[str, Any]]:
        """Return any HILS tension alerts."""
        return list(self._hils_alerts)


# ─── Utility functions ────────────────────────────────────────────────────────

def kk_level_to_radion_mode(kk_level: int) -> int:
    """Map OS KK privilege level (0–4) to KK radion mode number.

    Level 0 → mode 0 (ground state, zero mode)
    Level 1 → mode 1 (first KK excitation)
    Level n → mode n

    The mapping is 1:1 by construction.
    """
    if kk_level not in range(5):
        raise ValueError(f"kk_level must be 0–4, got {kk_level}")
    return kk_level


def radion_tension(phi: float, phi0: float = PHI0) -> float:
    """Compute the fractional tension of the radion field.

    tension = (φ - φ₀)² / φ₀²

    Returns 0.0 at the fixed point, >0 otherwise.
    """
    if phi0 == 0:
        raise ValueError("phi0 must be non-zero")
    return (phi - phi0) ** 2 / phi0 ** 2


def phi_debt_to_energy(delta_phi: float, phi0: float = PHI0) -> float:
    """Convert a φ-debt entry to a fractional energy cost.

    energy = (Δφ)² / (2 φ₀²)  (harmonic approximation around fixed point)
    """
    if phi0 == 0:
        raise ValueError("phi0 must be non-zero")
    return (delta_phi ** 2) / (2.0 * phi0 ** 2)
