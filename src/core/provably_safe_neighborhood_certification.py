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

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
import math
from numbers import Integral, Real
from typing import Dict, List

from src.core.pillar405_sobolev_ftum_extension import (
    critical_gradient_bound,
    h1_lipschitz_estimate,
)

# Fail-closed resource policy: bound normalization of unknown-ledger iterables
# to keep packet validation predictable and interruption-safe.
RESIDUAL_UNKNOWNS_MAX_ITEMS = 10_000

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

INTERVAL_OBLIGATION_ITEMS: Sequence[str] = (
    "finite-dimensional enclosure of computed constants",
    "roundoff-safe bounds for evaluated residual terms",
    "explicit interval bounds for truncation finite-mode block",
)

ANALYTIC_OBLIGATION_ITEMS: Sequence[str] = (
    "infinite-dimensional tail coercivity",
    "nonlinear remainder control in function spaces",
    "singular-limit and topology-transition constructive arguments",
    "uniform inverse stability in neighborhood",
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
        r = (2*alpha) / (1 + sqrt(1 - 2*alpha*beta)).
    (Equivalent to (1 - sqrt(1 - 2*alpha*beta)) / beta for beta>0.)
    """
    _nonnegative(inp.residual_bound, "residual_bound")
    _nonnegative(inp.inverse_bound, "inverse_bound")
    _nonnegative(inp.lipschitz_bound, "lipschitz_bound")

    alpha = inp.inverse_bound * inp.residual_bound
    beta = inp.inverse_bound * inp.lipschitz_bound
    discriminant = 1.0 - 2.0 * alpha * beta
    beta_effectively_zero = math.isclose(beta, 0.0, abs_tol=_ZERO_TOL)
    degenerate_affine_case = beta == 0.0
    exact_affine_zero_residual = (
        beta_effectively_zero
        and math.isclose(alpha, 0.0, abs_tol=_ZERO_TOL)
        and math.isclose(inp.residual_bound, 0.0, abs_tol=_ZERO_TOL)
    )
    near_affine_positive_inverse = (
        beta_effectively_zero
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
                "Nonlinear gate failed: requires 2*alpha*beta < 1; "
                f"computed alpha={alpha:.6g}, beta={beta:.6g}, product={2.0 * alpha * beta:.6g}."
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
    if not isinstance(h1, Mapping) or "l_h1" not in h1:
        raise ValueError("h1_lipschitz_estimate must return mapping with 'l_h1'.")
    if not isinstance(grad, Mapping) or "epsilon_grad_max" not in grad:
        raise ValueError("critical_gradient_bound must return mapping with 'epsilon_grad_max'.")
    raw_l_h1 = h1["l_h1"]
    raw_epsilon_grad_max = grad["epsilon_grad_max"]
    if isinstance(raw_l_h1, bool) or (not isinstance(raw_l_h1, Real)):
        raise ValueError("h1_lipschitz_estimate must return finite non-negative l_h1.")
    if isinstance(raw_epsilon_grad_max, bool) or (not isinstance(raw_epsilon_grad_max, Real)):
        raise ValueError("critical_gradient_bound must return finite non-negative epsilon_grad_max.")
    l_h1 = float(raw_l_h1)
    epsilon_grad_max = float(raw_epsilon_grad_max)
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
    if isinstance(curvature_singularity_threshold, bool):
        raise ValueError("curvature_singularity_threshold must be finite and non-negative.")
    if (not math.isfinite(curvature_singularity_threshold)) or curvature_singularity_threshold < 0.0:
        raise ValueError("curvature_singularity_threshold must be finite and non-negative.")

    if isinstance(routing.chart_jacobian_min, bool) or isinstance(routing.invariant_curvature_norm, bool):
        route = "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    elif (not math.isfinite(routing.chart_jacobian_min)) or (
        not math.isfinite(routing.invariant_curvature_norm)
    ):
        route = "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    elif isinstance(routing.topological_index_delta, bool) or (
        not isinstance(routing.topological_index_delta, Integral)
    ):
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
    regular_region_gate = route == "REGULAR_REGION_CERTIFIABLE"
    return {
        "input": asdict(routing),
        "curvature_singularity_threshold": curvature_singularity_threshold,
        "route": route,
        "fail_closed": fail_closed,
        "regular_region_gate": regular_region_gate,
    }


def _validated_string_sequence_base(
    raw_values: object,
    field_name: str,
    error_prefix: str,
    max_items: int | None = None,
) -> List[str]:
    if isinstance(raw_values, (str, bytes, bytearray, set, frozenset)) or isinstance(raw_values, Mapping):
        raise ValueError(f"{error_prefix}: {field_name} must be an ordered sequence.")
    if not isinstance(raw_values, Sequence):
        raise ValueError(f"{error_prefix}: {field_name} must be an ordered sequence.")
    if max_items is not None and len(raw_values) > max_items:
        raise ValueError(f"{error_prefix}: {field_name} must be a finite bounded sequence.")

    normalized_values: List[str] = []
    for item in raw_values:
        if not isinstance(item, str):
            raise ValueError(f"{error_prefix}: {field_name} entries must be strings.")
        normalized_values.append(item)
    return normalized_values


def _validated_unknown_sequence(raw_unknowns: object, error_prefix: str) -> List[str]:
    """Normalize residual unknown ledger from concrete ordered sequences."""
    return _validated_string_sequence_base(
        raw_values=raw_unknowns,
        field_name="residual_unknowns",
        error_prefix=error_prefix,
        max_items=RESIDUAL_UNKNOWNS_MAX_ITEMS,
    )


def _validated_string_sequence(
    raw_values: object,
    field_name: str,
    error_prefix: str,
) -> List[str]:
    return _validated_string_sequence_base(
        raw_values=raw_values,
        field_name=field_name,
        error_prefix=error_prefix,
    )


def _validate_posterior_stage(posterior: Mapping[str, object]) -> List[str]:
    if ("residual_unknowns" not in posterior) or ("sufficient_condition" not in posterior):
        raise ValueError("Malformed posterior stage output.")
    normalized_unknowns = _validated_unknown_sequence(
        posterior.get("residual_unknowns"),
        "Malformed posterior stage output",
    )
    if type(posterior.get("sufficient_condition")) is not bool:
        raise ValueError("Malformed packet stage: posterior_neighborhood.sufficient_condition must be bool.")
    if posterior.get("sufficient_condition") and normalized_unknowns:
        raise ValueError(
            "Malformed posterior stage output: sufficient_condition=True requires empty residual_unknowns."
        )
    return normalized_unknowns


def _require_typed_field(stage: Mapping[str, object], field: str, expected_type: type, stage_name: str) -> None:
    if field not in stage:
        raise ValueError(f"Malformed {stage_name} stage output: missing '{field}'.")
    value = stage.get(field)
    if expected_type is bool:
        if type(value) is not bool:
            raise ValueError(f"Malformed {stage_name} stage output: {field} must be bool.")
        return
    if not isinstance(value, expected_type):
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
    _require_typed_field(routing_result, "regular_region_gate", bool, "routing")


def _validated_residual_unknowns(packet: Mapping[str, object]) -> List[str]:
    return _validated_unknown_sequence(
        packet.get("residual_unknowns", []),
        "Malformed certification packet",
    )


def _validate_packet_consistency_from_stage_gates(
    packet: Mapping[str, object],
    posterior_ok: bool,
    truncation_ok: bool,
    sobolev_ok: bool,
    routing_stage_passed: bool,
) -> List[str]:
    residual_unknowns = _validated_residual_unknowns(packet)

    all_certified = packet.get("all_certified")
    if type(all_certified) is not bool:
        raise ValueError("Malformed certification packet. 'all_certified' must be bool.")

    expected_all_certified = (
        posterior_ok and truncation_ok and sobolev_ok and routing_stage_passed
    )
    if all_certified != expected_all_certified:
        raise ValueError(
            "Malformed certification packet: all_certified inconsistent with validated stage gates."
        )

    if expected_all_certified and residual_unknowns:
        raise ValueError("Inconsistent packet: all_certified=True with non-empty residual_unknowns.")
    if (not expected_all_certified) and (not residual_unknowns):
        raise ValueError(
            "Malformed certification packet: blocked stage gates require non-empty residual_unknowns."
        )
    return residual_unknowns


def _remaining_obligations_from_stage_gates(
    posterior_ok: bool,
    truncation_ok: bool,
    sobolev_ok: bool,
    routing_stage_passed: bool,
    routing_route: str,
) -> List[str]:
    obligations: List[str] = []
    if not posterior_ok:
        obligations.append("Posterior neighborhood obligation unresolved.")
    if not truncation_ok:
        obligations.append("Truncation envelope obligation unresolved.")
    if not sobolev_ok:
        obligations.append("Sobolev localization obligation unresolved.")
    if not routing_stage_passed:
        obligations.append(f"Routing obligation unresolved: route={routing_route}.")
    return obligations


def obligation_split() -> Dict[str, List[str]]:
    """Strict split of interval vs analytic responsibilities."""
    return {
        "interval_obligations": list(INTERVAL_OBLIGATION_ITEMS),
        "analytic_obligations": list(ANALYTIC_OBLIGATION_ITEMS),
    }


def phase_checkpoint(
    phase: str,
    completed_invariants: Sequence[str],
    remaining_obligations: Sequence[str],
    restart_pointer: str,
) -> Dict[str, object]:
    """Create interruption-safe checkpoint payload."""
    if not isinstance(phase, str) or not phase.strip():
        raise ValueError("phase must be non-empty.")
    if not isinstance(restart_pointer, str) or not restart_pointer.strip():
        raise ValueError("restart_pointer must be non-empty.")
    completed = _validated_string_sequence(
        completed_invariants,
        "completed_invariants",
        "Malformed checkpoint payload",
    )
    remaining = _validated_string_sequence(
        remaining_obligations,
        "remaining_obligations",
        "Malformed checkpoint payload",
    )

    ckpt = CertificationCheckpoint(
        phase=phase.strip(),
        completed_invariants=tuple(completed),
        remaining_obligations=tuple(remaining),
        restart_pointer=restart_pointer.strip(),
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
    posterior_unknowns = _validate_posterior_stage(posterior)
    _validate_truncation_stage(trunc)
    sobolev = sobolev_localization_obligation(local_patch_radius=local_patch_radius)
    _validate_sobolev_stage(sobolev)
    routing_result = singularity_topology_route(
        routing,
        curvature_singularity_threshold=curvature_singularity_threshold,
    )
    _validate_routing_stage(routing_result)
    split = obligation_split()
    posterior_ok = posterior["sufficient_condition"]
    trunc_ok = trunc["audit_ready"]
    sobolev_ok = sobolev["localized_contractive"]
    routing_regular_region = routing_result["regular_region_gate"]
    routing_fail_closed = routing_result["fail_closed"]
    residual_unknowns: List[str] = []
    residual_unknowns.extend(posterior_unknowns)
    if not trunc_ok:
        residual_unknowns.append("Truncation envelope is not audit-ready.")
    if not sobolev_ok:
        residual_unknowns.append("Localized Sobolev obligation is not contractive.")
    routing_stage_passed = routing_regular_region and (not routing_fail_closed)
    if not routing_stage_passed:
        residual_unknowns.append(f"Routing requires remediation: {routing_result['route']}")

    all_certified = (
        posterior_ok
        and trunc_ok
        and sobolev_ok
        and routing_stage_passed
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

    residual_unknowns = _validated_residual_unknowns(packet)
    all_certified = packet.get("all_certified")
    if type(all_certified) is not bool:
        raise ValueError("Malformed certification packet. 'all_certified' must be bool.")
    if all_certified and residual_unknowns:
        raise ValueError("Inconsistent packet: all_certified=True with non-empty residual_unknowns.")
    if (not all_certified) and (not residual_unknowns):
        raise ValueError("Inconsistent packet: all_certified=False requires non-empty residual_unknowns.")
    ready_for_formalization = all_certified and len(residual_unknowns) == 0
    return _build_formal_bridge_artifact(
        all_certified=all_certified,
        residual_unknowns=residual_unknowns,
        ready_for_formalization=ready_for_formalization,
    )


def _build_formal_bridge_artifact(
    all_certified: bool,
    residual_unknowns: Sequence[str],
    ready_for_formalization: bool,
) -> Dict[str, object]:
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
        "residual_unknowns": list(residual_unknowns),
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

    posterior_stage = packet.get("posterior_neighborhood")
    truncation_stage = packet.get("truncation_envelope")
    sobolev_stage = packet.get("sobolev_localization")
    routing_stage = packet.get("singularity_topology_routing")
    if not isinstance(posterior_stage, Mapping):
        raise ValueError("Malformed packet stage: posterior_neighborhood must be a mapping.")
    if not isinstance(truncation_stage, Mapping):
        raise ValueError("Malformed packet stage: truncation_envelope must be a mapping.")
    if not isinstance(sobolev_stage, Mapping):
        raise ValueError("Malformed packet stage: sobolev_localization must be a mapping.")
    if not isinstance(routing_stage, Mapping):
        raise ValueError("Malformed packet stage: singularity_topology_routing must be a mapping.")

    _validate_posterior_stage(posterior_stage)
    _validate_truncation_stage(truncation_stage)
    _validate_sobolev_stage(sobolev_stage)
    _validate_routing_stage(routing_stage)

    posterior_ok = posterior_stage["sufficient_condition"]
    truncation_ok = truncation_stage["audit_ready"]
    sobolev_ok = sobolev_stage["localized_contractive"]
    routing_regular_region = routing_stage["regular_region_gate"]
    routing_fail_closed = routing_stage["fail_closed"]
    routing_stage_passed = routing_regular_region and (not routing_fail_closed)

    completed_invariants: List[str] = []
    if posterior_ok:
        completed_invariants.append("posterior_neighborhood")
    if truncation_ok:
        completed_invariants.append("truncation_envelope")
    if sobolev_ok:
        completed_invariants.append("sobolev_localization")
    if routing_stage_passed:
        completed_invariants.append("singularity_topology_routing")
    stage_remaining_obligations = _remaining_obligations_from_stage_gates(
        posterior_ok=posterior_ok,
        truncation_ok=truncation_ok,
        sobolev_ok=sobolev_ok,
        routing_stage_passed=routing_stage_passed,
        routing_route=routing_stage["route"],
    )

    consistency_error: str | None = None
    try:
        _validate_packet_consistency_from_stage_gates(
            packet=packet,
            posterior_ok=posterior_ok,
            truncation_ok=truncation_ok,
            sobolev_ok=sobolev_ok,
            routing_stage_passed=routing_stage_passed,
        )
    except ValueError as exc:
        message = str(exc)
        consistency_only = (
            "all_certified inconsistent with validated stage gates" in message
            or "all_certified=True with non-empty residual_unknowns" in message
            or "blocked stage gates require non-empty residual_unknowns" in message
        )
        if not consistency_only:
            raise
        consistency_error = message
        remaining_obligations = list(stage_remaining_obligations)
        if not remaining_obligations:
            remaining_obligations = ["Packet consistency reconciliation required."]
        if consistency_error not in remaining_obligations:
            remaining_obligations.append(consistency_error)
    else:
        remaining_obligations = list(stage_remaining_obligations)

    if consistency_error is None:
        artifact = formal_bridge_artifact(packet)
    else:
        artifact = _build_formal_bridge_artifact(
            all_certified=False,
            residual_unknowns=remaining_obligations,
            ready_for_formalization=False,
        )

    checkpoint = phase_checkpoint(
        phase=phase,
        completed_invariants=completed_invariants,
        remaining_obligations=remaining_obligations,
        restart_pointer=restart_pointer,
    )
    return {
        "packet": packet,
        "artifact": artifact,
        "checkpoint": checkpoint,
    }
