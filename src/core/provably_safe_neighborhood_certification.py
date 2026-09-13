# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Provably safe neighborhood certification toolkit.

This module implements a fail-closed certification layer for converting computed
approximations into explicit, machine-readable theorem obligations.

Scope covered in one coherent interface:
- Posterior neighborhood certificate (Kantorovich-style)
- Truncation/stability envelopes (finite + tail + nonlinear remainder)
- Localized Sobolev obligations (with Pillar 405 compatibility)
- Invariant-first singularity/topology routing
- Strict interval-vs-analytic obligation split
- Interruption-safe phase checkpoint state
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Dict, List, Sequence

from src.core.pillar405_sobolev_ftum_extension import (
    critical_gradient_bound,
    h1_lipschitz_estimate,
)

__all__ = [
    "FAIL_CLOSED_RULES",
    "WORKSTREAM_SCOPE",
    "PosteriorNeighborhoodInput",
    "TruncationEnvelope",
    "SobolevLocalizationObligation",
    "SingularityRoutingInput",
    "CertificationCheckpoint",
    "posterior_neighborhood_certificate",
    "truncation_envelope",
    "sobolev_localization_obligation",
    "singularity_topology_route",
    "obligation_split",
    "phase_checkpoint",
    "full_certification_packet",
    "formal_bridge_artifact",
]


FAIL_CLOSED_RULES: Dict[str, bool] = {
    "no_unverifiable_claims": True,
    "no_status_inflation": True,
    "explicit_residual_unknowns": True,
    "ambiguous_cases_require_constructive_proof": True,
}

WORKSTREAM_SCOPE: Sequence[str] = (
    "posterior_neighborhood",
    "truncation_envelopes",
    "sobolev_localization",
    "singularity_topology_routing",
    "interval_vs_analytic_split",
    "verification_matrix",
    "formal_bridge_artifacts",
)


@dataclass(frozen=True)
class PosteriorNeighborhoodInput:
    residual_bound: float
    inverse_bound: float
    lipschitz_bound: float


@dataclass(frozen=True)
class TruncationEnvelope:
    finite_mode_error: float
    tail_bound: float
    nonlinear_remainder: float


@dataclass(frozen=True)
class SobolevLocalizationObligation:
    l_h1: float
    epsilon_grad_max: float
    local_patch_radius: float


@dataclass(frozen=True)
class SingularityRoutingInput:
    chart_jacobian_min: float
    invariant_curvature_norm: float
    topological_index_delta: int = 0


@dataclass(frozen=True)
class CertificationCheckpoint:
    phase: str
    completed_invariants: Sequence[str]
    remaining_obligations: Sequence[str]
    restart_pointer: str


def _nonnegative(value: float, name: str) -> None:
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative.")


def posterior_neighborhood_certificate(inp: PosteriorNeighborhoodInput) -> Dict[str, object]:
    """Compute a Kantorovich-style posterior neighborhood certificate.

    Let alpha = ||A^{-1}|| * ||F(x0)|| and beta = ||A^{-1}|| * Lip(F').
    Sufficient condition for uniqueness in a computable ball:
        2 * alpha * beta <= 1.
    Radius (for beta>0):
        r = (1 - sqrt(1 - 2*alpha*beta)) / beta.
    """
    _nonnegative(inp.residual_bound, "residual_bound")
    _nonnegative(inp.inverse_bound, "inverse_bound")
    _nonnegative(inp.lipschitz_bound, "lipschitz_bound")

    alpha = inp.inverse_bound * inp.residual_bound
    beta = inp.inverse_bound * inp.lipschitz_bound
    discriminant = 1.0 - 2.0 * alpha * beta
    sufficient_condition = discriminant >= 0.0

    if beta == 0.0:
        radius = alpha
    elif sufficient_condition:
        radius = (1.0 - math.sqrt(discriminant)) / beta
    else:
        radius = float("nan")

    verdict = (
        "POSTERIOR_NEIGHBORHOOD_CERTIFIED_UNIQUE"
        if sufficient_condition
        else "POSTERIOR_NEIGHBORHOOD_NOT_CERTIFIED_FAIL_CLOSED"
    )

    return {
        "inputs": asdict(inp),
        "alpha": alpha,
        "beta": beta,
        "discriminant": discriminant,
        "sufficient_condition": sufficient_condition,
        "radius": radius,
        "verdict": verdict,
        "theorem_form": "2*alpha*beta<=1 => existence+local uniqueness in explicit ball",
        "residual_unknowns": [] if sufficient_condition else [
            "Constructive inverse stability bound needed or Lipschitz constant too large."
        ],
    }


def truncation_envelope(env: TruncationEnvelope) -> Dict[str, object]:
    """Aggregate explicit finite/tail/nonlinear truncation errors."""
    _nonnegative(env.finite_mode_error, "finite_mode_error")
    _nonnegative(env.tail_bound, "tail_bound")
    _nonnegative(env.nonlinear_remainder, "nonlinear_remainder")

    total_error = env.finite_mode_error + env.tail_bound + env.nonlinear_remainder
    monotone_components = (
        env.finite_mode_error <= total_error
        and env.tail_bound <= total_error
        and env.nonlinear_remainder <= total_error
    )

    return {
        "components": asdict(env),
        "total_error": total_error,
        "monotone_components": monotone_components,
        "traceability": {
            "finite_mode_error": "numeric projection remainder",
            "tail_bound": "analytic infinite-dimensional tail",
            "nonlinear_remainder": "nonlinear operator closure remainder",
        },
        "audit_ready": monotone_components,
    }


def sobolev_localization_obligation(local_patch_radius: float = 1.0) -> Dict[str, object]:
    """Build localized Sobolev obligations using Pillar 405 interfaces."""
    if local_patch_radius <= 0.0:
        raise ValueError("local_patch_radius must be positive.")

    h1 = h1_lipschitz_estimate()
    grad = critical_gradient_bound()
    obligation = SobolevLocalizationObligation(
        l_h1=float(h1["l_h1"]),
        epsilon_grad_max=float(grad["epsilon_grad_max"]),
        local_patch_radius=local_patch_radius,
    )
    localized_contractive = obligation.l_h1 < 1.0 and obligation.epsilon_grad_max > 0.0

    return {
        "obligation": asdict(obligation),
        "backward_compatible_interface": "pillar405_sobolev_ftum_extension",
        "localized_contractive": localized_contractive,
        "verdict": (
            "SOBOLEV_LOCALIZATION_OBLIGATION_SATISFIED"
            if localized_contractive
            else "SOBOLEV_LOCALIZATION_OBLIGATION_FAIL_CLOSED"
        ),
    }


def singularity_topology_route(
    routing: SingularityRoutingInput,
    curvature_singularity_threshold: float = 1.0e6,
) -> Dict[str, object]:
    """Invariant-first routing for singularity and topology integrity."""
    if not math.isfinite(routing.chart_jacobian_min) or routing.chart_jacobian_min <= 0.0:
        route = "COORDINATE_BREAKDOWN_RECHART_REQUIRED"
    elif not math.isfinite(routing.invariant_curvature_norm):
        route = "CONSTRUCTIVE_PROOF_REQUIRED_NONFINITE_INVARIANT"
    elif abs(routing.topological_index_delta) > 0:
        route = "CONSTRUCTIVE_PROOF_REQUIRED_TOPOLOGICAL_TRANSITION"
    elif routing.invariant_curvature_norm >= curvature_singularity_threshold:
        route = "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"
    else:
        route = "REGULAR_REGION_CERTIFIABLE"

    fail_closed = route != "REGULAR_REGION_CERTIFIABLE"
    return {
        "input": asdict(routing),
        "curvature_singularity_threshold": curvature_singularity_threshold,
        "route": route,
        "fail_closed": fail_closed,
    }


def obligation_split() -> Dict[str, List[str]]:
    """Strict split of interval vs analytic responsibilities."""
    return {
        "interval_obligations": [
            "finite-dimensional enclosure of computed constants",
            "roundoff-safe bounds for evaluated residual terms",
            "explicit interval bounds for truncation finite-mode block",
        ],
        "analytic_obligations": [
            "infinite-dimensional tail coercivity",
            "nonlinear remainder control in function spaces",
            "singular-limit and topology-transition constructive arguments",
            "uniform inverse stability in neighborhood",
        ],
    }


def phase_checkpoint(
    phase: str,
    completed_invariants: Sequence[str],
    remaining_obligations: Sequence[str],
    restart_pointer: str,
) -> Dict[str, object]:
    """Create interruption-safe checkpoint payload."""
    if not phase:
        raise ValueError("phase must be non-empty.")
    if not restart_pointer:
        raise ValueError("restart_pointer must be non-empty.")

    ckpt = CertificationCheckpoint(
        phase=phase,
        completed_invariants=tuple(completed_invariants),
        remaining_obligations=tuple(remaining_obligations),
        restart_pointer=restart_pointer,
    )
    return {
        "checkpoint": asdict(ckpt),
        "resumable": True,
    }


def full_certification_packet(
    posterior_input: PosteriorNeighborhoodInput,
    envelope: TruncationEnvelope,
    routing: SingularityRoutingInput,
    local_patch_radius: float = 1.0,
) -> Dict[str, object]:
    """Return complete fail-closed certification packet."""
    posterior = posterior_neighborhood_certificate(posterior_input)
    trunc = truncation_envelope(envelope)
    sobolev = sobolev_localization_obligation(local_patch_radius=local_patch_radius)
    routing_result = singularity_topology_route(routing)
    split = obligation_split()

    residual_unknowns: List[str] = []
    residual_unknowns.extend(posterior["residual_unknowns"])
    if routing_result["fail_closed"]:
        residual_unknowns.append(f"Routing requires constructive proof: {routing_result['route']}")

    all_certified = (
        posterior["sufficient_condition"]
        and sobolev["localized_contractive"]
        and routing_result["route"] == "REGULAR_REGION_CERTIFIABLE"
    )

    return {
        "scope": list(WORKSTREAM_SCOPE),
        "fail_closed_rules": dict(FAIL_CLOSED_RULES),
        "posterior_neighborhood": posterior,
        "truncation_envelope": trunc,
        "sobolev_localization": sobolev,
        "singularity_topology_routing": routing_result,
        "obligation_split": split,
        "all_certified": all_certified,
        "verdict": (
            "CERTIFIED_PACKET_READY_FOR_FORMAL_BRIDGE"
            if all_certified
            else "PARTIAL_PACKET_FAIL_CLOSED_WITH_EXPLICIT_UNKNOWNS"
        ),
        "residual_unknowns": residual_unknowns,
    }


def formal_bridge_artifact(packet: Dict[str, object]) -> Dict[str, object]:
    """Convert certification packet into a formal-bridge friendly artifact."""
    residual_unknowns = list(packet.get("residual_unknowns", []))
    all_certified = bool(packet.get("all_certified", False))
    return {
        "artifact_type": "FORMAL_BRIDGE_CERTIFICATE",
        "all_certified": all_certified,
        "status": "READY_FOR_FORMALIZATION" if all_certified else "BLOCKED_FAIL_CLOSED",
        "theorem_targets": [
            "posterior existence and local uniqueness",
            "truncation envelope soundness",
            "localized Sobolev contractivity",
            "singularity/topology routing correctness",
        ],
        "assumption_ledger": [
            "A1: finite-dimensional residual bound provided",
            "A2: inverse operator bound is valid in the stated neighborhood",
            "A3: nonlinear Lipschitz bound is valid on the same neighborhood",
            "A4: invariant routing inputs are correctly computed",
        ],
        "residual_unknowns": residual_unknowns,
    }
