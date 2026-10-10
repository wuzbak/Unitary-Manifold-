# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Run-sheet generator — Phase 0 of the cold-fusion falsification roadmap.

Reads the existing, already-tested predictions in
``src/physics/lattice_dynamics.py`` and ``src/cold_fusion/excess_heat.py`` and
emits a concrete temperature-ramp schedule and a target loading-ratio curve
that an external electrochemistry lab could run against. This module makes
no new physics claim; it packages existing predictions into a runnable
protocol artifact, per Phase 0 of article-354's roadmap for direction #1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.physics.lattice_dynamics import X_BRAID_CANONICAL, braid_resonance_loading  # noqa: E402
from src.cold_fusion.falsification_protocol import falsification_criteria  # noqa: E402

#: Loading ratio approaches the canonical x = 7/8 = 0.875 resonance target.
LOADING_TARGET = X_BRAID_CANONICAL

#: Default temperature ramp, in degrees Celsius, for a Pd-D electrolytic cell.
DEFAULT_TEMPERATURE_RAMP_C: List[float] = [25.0, 35.0, 45.0, 55.0, 65.0, 75.0, 85.0]

#: COP pass threshold used throughout the cold-fusion falsification protocol.
COP_PASS_THRESHOLD = 1.01


@dataclass(frozen=True)
class RunSheetStep:
    """One scheduled step in a calorimetry run."""

    step_index: int
    temperature_c: float
    target_loading_ratio: float
    hold_minutes: int
    notes: str = ""


@dataclass(frozen=True)
class RunSheet:
    """A complete, lab-executable calorimetry run-sheet."""

    loading_target: float
    cop_pass_threshold: float
    steps: List[RunSheetStep] = field(default_factory=list)
    predicted_cop_range: tuple[float, float] = (1.0, 1.0)

    def to_dict(self) -> dict:
        return {
            "loading_target": self.loading_target,
            "cop_pass_threshold": self.cop_pass_threshold,
            "predicted_cop_range": list(self.predicted_cop_range),
            "steps": [
                {
                    "step_index": s.step_index,
                    "temperature_c": s.temperature_c,
                    "target_loading_ratio": s.target_loading_ratio,
                    "hold_minutes": s.hold_minutes,
                    "notes": s.notes,
                }
                for s in self.steps
            ],
        }


def _loading_curve(n_steps: int, final_loading: float) -> List[float]:
    """Monotonic ramp from a conservative starting loading up to ``final_loading``.

    Loading is deliberately ramped slowly: over-fast deuterium loading is a
    well-known failure mode in electrochemical Pd-D literature independent of
    any claim this framework makes.
    """
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    start = min(0.55, final_loading)
    if n_steps == 1:
        return [final_loading]
    step = (final_loading - start) / (n_steps - 1)
    return [round(start + i * step, 4) for i in range(n_steps)]


def generate_run_sheet(
    temperature_ramp_c: List[float] | None = None,
    loading_target: float = LOADING_TARGET,
    hold_minutes: int = 120,
    cop_pass_threshold: float = COP_PASS_THRESHOLD,
) -> RunSheet:
    """Build a run-sheet pairing a temperature ramp with a loading-ratio curve.

    Parameters
    ----------
    temperature_ramp_c : the electrolytic-cell temperature schedule, Celsius.
    loading_target : target D/Pd loading ratio (defaults to the canonical
        x = 7/8 = 0.875 resonance value from ``lattice_dynamics.py``).
    hold_minutes : dwell time at each step before the next measurement.
    cop_pass_threshold : COP value above which the run counts as a pass,
        per ``falsification_protocol.cold_fusion_falsification_protocol``.
    """
    ramp = list(temperature_ramp_c) if temperature_ramp_c is not None else list(DEFAULT_TEMPERATURE_RAMP_C)
    if not ramp:
        raise ValueError("temperature_ramp_c must not be empty")
    loading_curve = _loading_curve(len(ramp), loading_target)

    resonance = braid_resonance_loading()
    criteria = falsification_criteria()
    f1_required = criteria["criteria"][0]["required_conditions"]["loading_ratio"]

    steps = [
        RunSheetStep(
            step_index=i,
            temperature_c=temp,
            target_loading_ratio=loading,
            hold_minutes=hold_minutes,
            notes=(
                f"F1 calorimetry gate requires {f1_required}; "
                f"braid x_canonical={resonance.get('x_canonical')}"
                if i == len(ramp) - 1
                else ""
            ),
        )
        for i, (temp, loading) in enumerate(zip(ramp, loading_curve))
    ]

    return RunSheet(
        loading_target=loading_target,
        cop_pass_threshold=cop_pass_threshold,
        steps=steps,
        predicted_cop_range=(cop_pass_threshold, cop_pass_threshold + 0.05),
    )
