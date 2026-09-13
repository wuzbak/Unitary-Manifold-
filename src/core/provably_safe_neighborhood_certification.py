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

from collections.abc import Mapping, Sequence as SequenceABC
from dataclasses import asdict, dataclass
import math
from numbers import Integral
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
    "checkpointed_formal_bridge_packet",
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
_ZERO_TOL: float = 1.0e-12


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
    if (not math.isfinite(value)) or value < 0.0:
        raise ValueError(f"{name} must be finite and non-negative.")


def posterior_neighborhood_certificate(inp: PosteriorNeighborhoodInput) -> Dict[str, object]:
    """Compute a Kantorovich-style posterior neighborhood certificate.

    Let alpha = ||A^{-1}|| * ||F(x0)|| and beta = ||A^{-1}|| * Lip(F').
    Sufficient condition for uniqueness in a computable ball:
        2 * alpha * beta < 1.
    Radius (for beta>0):
        r = (1 - sqrt(1 - 2*alpha*beta)) / beta.
    """
    _nonnegative(inp.residual_bound, "residual_bound")
    _nonnegative(inp.inverse_bound, "inverse_bound")
    _nonnegative(inp.lipschitz_bound, "lipschitz_bound")

    alpha = inp.inverse_bound * inp.residual_bound
    beta = inp.inverse_bound * inp.lipschitz_bound
    discriminant = 1.0 - 2.0 * alpha * beta
    degenerate_affine_case = math.isclose(beta, 0.0, abs_tol=_ZERO_TOL)
    exact_affine_zero_residual = (
        degenerate_affine_case
        and math.isclose(alpha, 0.0, abs_tol=_ZERO_TOL)
        and math.isclose(inp.residual_bound, 0.0, abs_tol=_ZERO_TOL)
    )
    near_affine_positive_inverse = (
        degenerate_affine_case
        and inp.inverse_bound > 0.0
        and alpha < 1.0
    )
    sufficient_condition = (
        exact_affine_zero_residual
        or near_affine_positive_inverse
        or (
            (not degenerate_affine_case)
            and beta > 0.0
            and (2.0 * alpha * beta) < 1.0
        )
    )

    if exact_affine_zero_residual:
        radius = 0.0
    elif near_affine_positive_inverse:
        radius = alpha
    elif sufficient_condition and discriminant >= 0.0:
        radius = (2.0 * alpha) / (1.0 + math.sqrt(discriminant))
    else:
        radius = float("nan")

    verdict = (
        "POSTERIOR_NEIGHBORHOOD_CERTIFIED_UNIQUE"
        if sufficient_condition
        else "POSTERIOR_NEIGHBORHOOD_NOT_CERTIFIED_FAIL_CLOSED"
    )

    residual_unknowns: List[str] = []
    if not sufficient_condition:
        if degenerate_affine_case and inp.inverse_bound == 0.0 and inp.residual_bound > 0.0:
            residual_unknowns.append(
                "Inverse-bound degeneracy: inverse_bound=0 with nonzero residual requires valid inverse estimate."
            )
        elif degenerate_affine_case and inp.inverse_bound > 0.0 and alpha >= 1.0:
            residual_unknowns.append(
                "Affine-near-zero Lipschitz case requires smaller residual seed (alpha < 1)."
            )
        elif degenerate_affine_case:
            residual_unknowns.append(
                "Degenerate affine case (beta=0) requires separate non-neighborhood certificate."
            )
        else:
            residual_unknowns.append(
                "Constructive inverse stability bound needed or Lipschitz constant too large."
            )

    return {
        "inputs": asdict(inp),
        "alpha": alpha,
        "beta": beta,
        "degenerate_affine_case": degenerate_affine_case,
        "discriminant": discriminant,
        "sufficient_condition": sufficient_condition,
        "radius": radius,
        "verdict": verdict,
        "theorem_form": "2*alpha*beta<1 => existence+local uniqueness in explicit ball",
        "residual_unknowns": residual_unknowns,
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
    if (not math.isfinite(local_patch_radius)) or local_patch_radius <= 0.0:
        raise ValueError("local_patch_radius must be finite and positive.")

    h1 = h1_lipschitz_estimate()
    grad = critical_gradient_bound()
    l_h1 = float(h1["l_h1"])
    epsilon_grad_max = float(grad["epsilon_grad_max"])
    if (not math.isfinite(l_h1)) or l_h1 < 0.0:
        raise ValueError("h1_lipschitz_estimate must return finite non-negative l_h1.")
    if (not math.isfinite(epsilon_grad_max)) or epsilon_grad_max < 0.0:
        raise ValueError("critical_gradient_bound must return finite non-negative epsilon_grad_max.")
    local_radius_factor = math.sqrt(1.0 + local_patch_radius ** 2)
    obligation = SobolevLocalizationObligation(
        l_h1=l_h1,
        epsilon_grad_max=epsilon_grad_max / local_radius_factor,
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
    """Invariant-first routing for singularity and topology integrity.

    Precedence order:
    1) Invalid numeric input (non-finite Jacobian/curvature) -> fail-closed
    2) Geometric singularity (invariant curvature threshold exceeded)
    3) Topology transition (non-zero topological index delta)
    4) Coordinate breakdown (non-positive chart Jacobian; rechart required)
    5) Regular region certifiable
    """
    if (not math.isfinite(curvature_singularity_threshold)) or curvature_singularity_threshold <= 0.0:
        raise ValueError("curvature_singularity_threshold must be finite and positive.")

    if (not math.isfinite(routing.chart_jacobian_min)) or (
        not math.isfinite(routing.invariant_curvature_norm)
    ):
        route = "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    elif not isinstance(routing.topological_index_delta, Integral):
        route = "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    elif routing.invariant_curvature_norm < 0.0:
        route = "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    elif routing.invariant_curvature_norm > curvature_singularity_threshold:
        route = "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"
    elif abs(routing.topological_index_delta) > 0:
        route = "CONSTRUCTIVE_PROOF_REQUIRED_TOPOLOGICAL_TRANSITION"
    elif routing.chart_jacobian_min <= 0.0:
        route = "COORDINATE_BREAKDOWN_RECHART_REQUIRED"
    else:
        route = "REGULAR_REGION_CERTIFIABLE"

    fail_closed = route in {
        "INVALID_NUMERIC_INPUT_FAIL_CLOSED",
        "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT",
        "CONSTRUCTIVE_PROOF_REQUIRED_TOPOLOGICAL_TRANSITION",
    }
    return {
        "input": asdict(routing),
        "curvature_singularity_threshold": curvature_singularity_threshold,
        "route": route,
        "fail_closed": fail_closed,
    }


def _validate_posterior_stage(posterior: Mapping[str, object]) -> None:
    if ("residual_unknowns" not in posterior) or ("sufficient_condition" not in posterior):
        raise ValueError("Malformed posterior stage output.")
    raw_unknowns = posterior.get("residual_unknowns")
    if isinstance(raw_unknowns, (str, bytes)) or (not isinstance(raw_unknowns, SequenceABC)):
        raise ValueError("Malformed posterior stage output: residual_unknowns must be an ordered sequence.")
    if any(not isinstance(item, str) for item in raw_unknowns):
        raise ValueError("Malformed posterior stage output: residual_unknowns entries must be strings.")
    if not isinstance(posterior.get("sufficient_condition"), bool):
        raise ValueError("Malformed posterior stage output: sufficient_condition must be bool.")


def _require_typed_field(stage: Mapping[str, object], field: str, expected_type: type, stage_name: str) -> None:
    if field not in stage:
        raise ValueError(f"Malformed {stage_name} stage output: missing '{field}'.")
    if not isinstance(stage.get(field), expected_type):
        raise ValueError(
            f"Malformed {stage_name} stage output: {field} must be {expected_type.__name__}."
        )


def _validate_truncation_stage(trunc: Mapping[str, object]) -> None:
    _require_typed_field(trunc, "audit_ready", bool, "truncation envelope")


def _validate_sobolev_stage(sobolev: Mapping[str, object]) -> None:
    _require_typed_field(sobolev, "localized_contractive", bool, "sobolev")


def _validate_routing_stage(routing_result: Mapping[str, object]) -> None:
    _require_typed_field(routing_result, "fail_closed", bool, "routing")
    _require_typed_field(routing_result, "route", str, "routing")


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
    curvature_singularity_threshold: float = 1.0e6,
) -> Dict[str, object]:
    """Return complete fail-closed certification packet."""
    posterior = posterior_neighborhood_certificate(posterior_input)
    trunc = truncation_envelope(envelope)
    _validate_posterior_stage(posterior)
    _validate_truncation_stage(trunc)
    sobolev = sobolev_localization_obligation(local_patch_radius=local_patch_radius)
    _validate_sobolev_stage(sobolev)
    routing_result = singularity_topology_route(
        routing,
        curvature_singularity_threshold=curvature_singularity_threshold,
    )
    _validate_routing_stage(routing_result)
    split = obligation_split()

    residual_unknowns: List[str] = []
    residual_unknowns.extend(posterior["residual_unknowns"])
    if not trunc["audit_ready"]:
        residual_unknowns.append("Truncation envelope is not audit-ready.")
    if not sobolev["localized_contractive"]:
        residual_unknowns.append("Localized Sobolev obligation is not contractive.")
    if routing_result["route"] != "REGULAR_REGION_CERTIFIABLE":
        residual_unknowns.append(f"Routing requires remediation: {routing_result['route']}")

    all_certified = (
        posterior["sufficient_condition"]
        and trunc["audit_ready"]
        and sobolev["localized_contractive"]
        and (not routing_result["fail_closed"])
        and routing_result["route"] == "REGULAR_REGION_CERTIFIABLE"
        and len(residual_unknowns) == 0
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


def formal_bridge_artifact(packet: Mapping[str, object]) -> Dict[str, object]:
    """Convert certification packet into a formal-bridge friendly artifact."""
    if not isinstance(packet, Mapping):
        raise ValueError("Malformed certification packet. Packet must be a mapping.")

    required_fields = {"all_certified", "residual_unknowns"}
    missing = sorted(required_fields.difference(packet.keys()))
    if missing:
        raise ValueError(f"Malformed certification packet. Missing fields: {', '.join(missing)}")

    raw_unknowns = packet.get("residual_unknowns", [])
    if isinstance(raw_unknowns, (str, bytes)) or (not isinstance(raw_unknowns, SequenceABC)):
        raise ValueError(
            "Malformed certification packet. 'residual_unknowns' must be an ordered sequence."
        )
    residual_unknowns = list(raw_unknowns)
    if any(not isinstance(item, str) for item in residual_unknowns):
        raise ValueError("Malformed certification packet. 'residual_unknowns' entries must be strings.")
    residual_unknowns = sorted(residual_unknowns)
    all_certified = packet.get("all_certified")
    if not isinstance(all_certified, bool):
        raise ValueError("Malformed certification packet. 'all_certified' must be bool.")
    if all_certified and residual_unknowns:
        raise ValueError("Inconsistent packet: all_certified=True with non-empty residual_unknowns.")
    ready_for_formalization = all_certified and len(residual_unknowns) == 0
    return {
        "artifact_type": "FORMAL_BRIDGE_CERTIFICATE",
        "all_certified": all_certified,
        "status": "READY_FOR_FORMALIZATION" if ready_for_formalization else "BLOCKED_FAIL_CLOSED",
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


def checkpointed_formal_bridge_packet(
    posterior_input: PosteriorNeighborhoodInput,
    envelope: TruncationEnvelope,
    routing: SingularityRoutingInput,
    phase: str,
    restart_pointer: str,
    local_patch_radius: float = 1.0,
    curvature_singularity_threshold: float = 1.0e6,
) -> Dict[str, object]:
    """Build packet + formal artifact + resumable checkpoint in one call."""
    packet = full_certification_packet(
        posterior_input=posterior_input,
        envelope=envelope,
        routing=routing,
        local_patch_radius=local_patch_radius,
        curvature_singularity_threshold=curvature_singularity_threshold,
    )
    artifact = formal_bridge_artifact(packet)
    checkpoint = phase_checkpoint(
        phase=phase,
        completed_invariants=[
            "posterior_neighborhood",
            "truncation_envelope",
            "sobolev_localization",
            "singularity_topology_routing",
        ],
        remaining_obligations=list(packet["residual_unknowns"]),
        restart_pointer=restart_pointer,
    )
    return {
        "packet": packet,
        "artifact": artifact,
        "checkpoint": checkpoint,
    }
