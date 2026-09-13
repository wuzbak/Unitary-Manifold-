# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Provably safe neighborhood certification primitives.

This module encodes a fail-closed intermediate certification layer for moving
from computed approximations to explicit neighborhood theorems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Literal

ObligationClass = Literal["interval", "analytic"]


@dataclass(frozen=True)
class TruncationEnvelope:
    """Explicit error envelope attached to a computed approximation."""

    truncation_tail_bound: float
    operator_remainder_bound: float
    interval_roundoff_bound: float
    analytic_tail_bound: float

    def total_bound(self) -> float:
        """Return total additive envelope error."""
        return (
            self.truncation_tail_bound
            + self.operator_remainder_bound
            + self.interval_roundoff_bound
            + self.analytic_tail_bound
        )


@dataclass(frozen=True)
class PosteriorInputs:
    """Inputs needed for a posterior neighborhood certificate."""

    residual_bound: float
    inverse_bound: float
    lipschitz_bound: float
    envelope: TruncationEnvelope


def _nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")


def classify_obligation(obligation_name: str) -> ObligationClass:
    """Classify obligations into interval-safe vs analytic-required classes."""
    normalized = obligation_name.strip().lower()
    exact_policy = {
        "interval_roundoff_bound": "interval",
        "interval_roundoff_tail_bound": "interval",
        "truncation_tail_bound": "analytic",
        "operator_remainder_bound": "analytic",
        "analytic_tail_bound": "analytic",
    }
    if normalized in exact_policy:
        return exact_policy[normalized]  # type: ignore[return-value]
    analytic_markers = (
        "tail",
        "operator",
        "remainder",
        "coerc",
        "compact",
        "sobolev",
        "singular",
        "topolog",
        "infinite",
    )
    if any(marker in normalized for marker in analytic_markers):
        return "analytic"
    interval_markers = (
        "interval",
        "roundoff",
        "finite_mode",
    )
    if any(marker in normalized for marker in interval_markers):
        return "interval"
    return "interval"


def posterior_neighborhood_certificate(inputs: PosteriorInputs) -> Dict[str, object]:
    """Compute fail-closed posterior neighborhood certificate.

    The certificate is accepted only when all contractivity and positivity
    conditions are satisfied.
    """
    _nonnegative("residual_bound", inputs.residual_bound)
    _nonnegative("inverse_bound", inputs.inverse_bound)
    _nonnegative("lipschitz_bound", inputs.lipschitz_bound)
    _nonnegative("truncation_tail_bound", inputs.envelope.truncation_tail_bound)
    _nonnegative("operator_remainder_bound", inputs.envelope.operator_remainder_bound)
    _nonnegative("interval_roundoff_bound", inputs.envelope.interval_roundoff_bound)
    _nonnegative("analytic_tail_bound", inputs.envelope.analytic_tail_bound)

    envelope_total = inputs.envelope.total_bound()
    seed_radius = inputs.inverse_bound * (inputs.residual_bound + envelope_total)
    contraction_margin = 1.0 - (inputs.inverse_bound * inputs.lipschitz_bound)
    total_seed_residual = inputs.residual_bound + envelope_total

    fail_reasons = []
    if contraction_margin <= 0.0:
        fail_reasons.append("non_contractive_linearization")

    if seed_radius == 0.0 and contraction_margin > 0.0:
        if total_seed_residual == 0.0:
            radius = 0.0
            uniqueness_gate = 0.0
            unique_local_solution = True
        else:
            fail_reasons.append("degenerate_radius_seed")
            radius = float("inf")
            uniqueness_gate = float("inf")
            unique_local_solution = False
    else:
        radius = seed_radius / contraction_margin if contraction_margin > 0.0 else float("inf")
        # Contraction-theorem uniqueness gate.
        uniqueness_gate = inputs.inverse_bound * inputs.lipschitz_bound
        unique_local_solution = uniqueness_gate < 1.0
        if not unique_local_solution:
            fail_reasons.append("uniqueness_gate_failed")

    certified = not fail_reasons
    return {
        "certified": certified,
        "radius": radius,
        "beta": seed_radius,
        "contraction_margin": contraction_margin,
        "uniqueness_gate": uniqueness_gate,
        "envelope_total": envelope_total,
        "fail_reasons": fail_reasons,
        "obligation_split": {
            "interval": [
                "residual_bound",
                "inverse_bound",
                "interval_roundoff_bound",
            ],
            "analytic": [
                "truncation_tail_bound",
                "operator_remainder_bound",
                "analytic_tail_bound",
                "lipschitz_bound",
            ],
        },
    }


def singularity_routing_gate(
    coordinate_singularity_detected: bool,
    invariant_curvature_blowup: bool,
    topology_reaction_detected: bool,
) -> Dict[str, str]:
    """Route singularity outcomes with fail-closed policy."""
    if invariant_curvature_blowup:
        return {
            "route": "geometric_singularity",
            "status": "fail_closed",
            "reason": "invariant_blowup_requires_constructive_argument",
        }
    if topology_reaction_detected:
        return {
            "route": "topology_transition",
            "status": "fail_closed",
            "reason": "topology_reaction_requires_constructive_argument",
        }
    if coordinate_singularity_detected:
        return {
            "route": "coordinate_artifact",
            "status": "rechart_required",
            "reason": "invariants_bounded_but_coordinates_break",
        }
    return {
        "route": "regular",
        "status": "pass",
        "reason": "no_singularity_indicators",
    }
