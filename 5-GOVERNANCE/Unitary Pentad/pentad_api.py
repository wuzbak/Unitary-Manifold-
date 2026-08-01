# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pentad API Gateway — Public Python interface for the Unitary Pentad.

This module provides a clean REST-style Python API that can be called
from the public website (via Pyodide/WASM or static JSON exports).
"""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from typing import Dict, List

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from consciousness_constant import CONSCIOUSNESS_COUPLING
from pentad_scenarios import (
    detect_collapse_mode,
    harmonic_state_metrics,
    inject_adversarial_intent,
    trust_maintenance_cost,
)
from sentinel_load_balance import SENTINEL_CAPACITY
from unitary_pentad import (
    BRAIDED_SOUND_SPEED,
    PENTAD_LABELS,
    PentadLabel,
    PentadSystem,
    TRUST_PHI_MIN,
    pentad_defect,
    trust_modulation,
)


def _clone_with_body_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    bodies = dict(system.bodies)
    old = bodies[label]
    bodies[label] = type(old)(
        node=old.node,
        phi=float(np.clip(phi, 0.0, 1.0)),
        n1=old.n1,
        n2=old.n2,
        k_cs=old.k_cs,
        label=old.label,
    )
    return PentadSystem(
        bodies=bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )


class PentadAPI:
    """Public REST-style Python API for Pentad simulations and summaries."""

    def run_scenario(self, scenario_name: str) -> dict:
        """Run a named scenario and return a serializable summary."""

        name = scenario_name.strip().lower()
        system = PentadSystem.default()

        if name == "harmonic":
            metrics = harmonic_state_metrics(system)
            return {
                "scenario": name,
                "stability_score": self.get_stability_score(
                    [system.bodies[label].phi for label in PENTAD_LABELS]
                ),
                "trust": float(trust_modulation(system)),
                "metrics": asdict(metrics),
            }
        if name == "collapse":
            system = inject_adversarial_intent(system, 0.0)
            system = _clone_with_body_phi(system, PentadLabel.TRUST, 0.0)
            signature = detect_collapse_mode(system)
            return {
                "scenario": name,
                "stability_score": self.get_stability_score(
                    [system.bodies[label].phi for label in PENTAD_LABELS]
                ),
                "trust": float(trust_modulation(system)),
                "collapse": asdict(signature),
            }
        if name == "wildcard":
            return {
                "scenario": name,
                "trust_maintenance_cost": trust_maintenance_cost(system),
                "trust_floor": TRUST_PHI_MIN,
                "sentinel_capacity": SENTINEL_CAPACITY,
            }
        raise ValueError(f"Unsupported scenario: {scenario_name!r}")

    def get_stability_score(self, body_states: list) -> float:
        """Compute a 0–1 stability score from five normalized body states."""

        if len(body_states) != 5:
            raise ValueError("body_states must contain exactly 5 entries.")
        values = np.clip(np.asarray(body_states, dtype=float), 0.0, 1.0)
        variance = float(np.var(values))
        max_variance = 0.25
        return float(np.clip(1.0 - variance / max_variance, 0.0, 1.0))

    def compute_trust_field(self, trust_params: dict) -> dict:
        """Compute a symmetric trust-field coupling matrix."""

        raw_states = trust_params.get("body_states", {})
        states = {
            label: float(np.clip(raw_states.get(label, 1.0), 0.0, 1.0))
            for label in PENTAD_LABELS
        }
        trust_scalar = float(
            np.clip(
                trust_params.get("trust", np.mean(list(states.values()))),
                0.0,
                1.0,
            )
        )
        matrix = {}
        for left in PENTAD_LABELS:
            matrix[left] = {}
            for right in PENTAD_LABELS:
                if left == right:
                    matrix[left][right] = states[left]
                else:
                    matrix[left][right] = float(
                        np.clip(trust_scalar * 0.5 * (states[left] + states[right]), 0.0, 1.0)
                    )
        return {"labels": list(PENTAD_LABELS), "trust_scalar": trust_scalar, "matrix": matrix}

    def simulate_5body(self, steps: int, initial_state: dict) -> list:
        """Return a simple five-body relaxation trajectory."""

        if steps < 0:
            raise ValueError("steps must be >= 0.")
        state = {
            label: float(np.clip(initial_state.get(label, PentadSystem.default().bodies[label].phi), 0.0, 1.0))
            for label in PENTAD_LABELS
        }
        trajectory: List[Dict[str, float]] = [dict(state)]
        for _ in range(steps):
            mean_phi = float(np.mean(list(state.values())))
            trust = state[PentadLabel.TRUST]
            updated = {}
            for label, phi in state.items():
                damping = BRAIDED_SOUND_SPEED * (0.6 if label == PentadLabel.TRUST else 0.4 + 0.2 * trust)
                updated[label] = float(np.clip(phi + damping * (mean_phi - phi), 0.0, 1.0))
            state = updated
            trajectory.append(dict(state))
        return trajectory

    def get_pillar_summary(self) -> dict:
        """Return a concise summary of key Pentad/UM pillars."""

        return {
            "winding_number": 5,
            "braid_partner": 7,
            "k_cs": 74,
            "xi_c": CONSCIOUSNESS_COUPLING,
            "sentinel_capacity": SENTINEL_CAPACITY,
            "braided_sound_speed": BRAIDED_SOUND_SPEED,
            "trust_floor": TRUST_PHI_MIN,
            "pillars": {
                "pillar_4": "Holographic boundary dynamics",
                "pillar_5": "FTUM fixed-point iteration",
                "pillar_70b": "Ω₀ Holon Zero ground state",
                "pentad": "Five-body HILS governance framework",
            },
        }

    def export_static_json(self) -> dict:
        """Return a static website-friendly Pentad snapshot."""

        baseline = PentadSystem.default()
        return {
            "api_version": "1.0.0",
            "pillar_summary": self.get_pillar_summary(),
            "scenarios": {
                name: self.run_scenario(name)
                for name in ("harmonic", "collapse", "wildcard")
            },
            "baseline_state": {
                label: float(baseline.bodies[label].phi) for label in PENTAD_LABELS
            },
            "baseline_trust": float(trust_modulation(baseline)),
            "baseline_defect": float(pentad_defect(baseline)),
            "sample_trajectory": self.simulate_5body(
                steps=3,
                initial_state={label: float(baseline.bodies[label].phi) for label in PENTAD_LABELS},
            ),
        }


def generate_static_snapshot() -> dict:
    """Generate a complete static snapshot for website export."""

    return PentadAPI().export_static_json()
