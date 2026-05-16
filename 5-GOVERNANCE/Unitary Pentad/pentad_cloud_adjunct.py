# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_cloud_adjunct.py
======================================
Pentad-native contract for cloud compute without introducing a sixth body.

Background
----------
The Unitary Pentad is closed at five active bodies:

    Ψ_univ, Ψ_brain, Ψ_human, Ψ_AI, β·C

This module formalises the boundary condition for using cloud services without
breaking that closure.  The cloud is treated as an **adjunct reservoir**:

1. **Archive / persistence** — snapshots, logs, restoration metadata.
2. **Batch compute** — throughput-heavy simulations and offline analysis.
3. **Truth query** — external datasets, retrieval, cross-checks.
4. **Model host** — large remote inference endpoints serving Ψ_AI.

It is *not*:
- a sixth manifold,
- a sixth voting body,
- a participant in phase-locking,
- or a direct actuator of the live orbit.

Any result returning from the cloud must re-enter through the existing five-body
governance path: the local Ψ_AI body under Ψ_human + β·C supervision.

Public API
----------
CloudAdjunctRole
    String constants for supported cloud reservoir roles.

CLOUD_ADJUNCT_ROLES : tuple[str, ...]
    Canonical set of supported roles.

CloudAdjunctRequest
    One cloud request: role, latency class, criticality, and requested powers.

CloudAdjunctPolicy
    Contract boundary: what the cloud may and may not do.

CloudAdjunctDecision
    Routing result describing whether the task stays local, mirrors to archive,
    or runs asynchronously in the cloud.

default_cloud_adjunct_policy() -> CloudAdjunctPolicy
    Canonical policy preserving five-body closure.

evaluate_cloud_adjunct(system, request, policy=None) -> CloudAdjunctDecision
    Main entry point.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass
from typing import Tuple

from unitary_pentad import PENTAD_LABELS, PentadSystem, trust_modulation


class CloudAdjunctRole:
    """Supported adjunct roles for remote cloud services."""

    ARCHIVE = "archive"
    BATCH_COMPUTE = "batch_compute"
    TRUTH_QUERY = "truth_query"
    MODEL_HOST = "model_host"


CLOUD_ADJUNCT_ROLES: Tuple[str, ...] = (
    CloudAdjunctRole.ARCHIVE,
    CloudAdjunctRole.BATCH_COMPUTE,
    CloudAdjunctRole.TRUTH_QUERY,
    CloudAdjunctRole.MODEL_HOST,
)

_ASYNC_ROLES: Tuple[str, ...] = (
    CloudAdjunctRole.BATCH_COMPUTE,
    CloudAdjunctRole.TRUTH_QUERY,
    CloudAdjunctRole.MODEL_HOST,
)


@dataclass(frozen=True)
class CloudAdjunctRequest:
    """One request to the cloud adjunct reservoir."""

    request_id: str
    role: str
    estimated_roundtrip_ms: float
    criticality: float = 0.5
    phase_lock_required: bool = False
    control_write_requested: bool = False
    state_mutation: str = "none"

    def __post_init__(self) -> None:
        if self.role not in CLOUD_ADJUNCT_ROLES:
            raise ValueError(f"Unsupported role={self.role!r}.")
        if self.estimated_roundtrip_ms < 0.0:
            raise ValueError("estimated_roundtrip_ms must be >= 0.")
        if not (0.0 <= self.criticality <= 1.0):
            raise ValueError("criticality must be in [0,1].")
        if self.state_mutation not in {"none", "snapshot", "advisory", "actuation"}:
            raise ValueError(
                "state_mutation must be one of {'none', 'snapshot', 'advisory', 'actuation'}."
            )


@dataclass(frozen=True)
class CloudAdjunctPolicy:
    """Boundary rules for cloud participation around the five-body orbit."""

    active_orbit_bodies: Tuple[str, ...] = PENTAD_LABELS
    phase_lock_latency_budget_ms: float = 5.0
    truth_confirmation_threshold: float = 0.6
    min_trust_for_autonomous_truth: float = 0.25
    allow_archive_snapshots: bool = True
    allow_async_batch_compute: bool = True
    allow_truth_queries: bool = True
    allow_remote_model_hosts: bool = True

    def __post_init__(self) -> None:
        if self.active_orbit_bodies != PENTAD_LABELS:
            raise ValueError("active_orbit_bodies must remain exactly the five Pentad labels.")
        if self.phase_lock_latency_budget_ms <= 0.0:
            raise ValueError("phase_lock_latency_budget_ms must be > 0.")
        if not (0.0 <= self.truth_confirmation_threshold <= 1.0):
            raise ValueError("truth_confirmation_threshold must be in [0,1].")
        if not (0.0 <= self.min_trust_for_autonomous_truth <= 1.0):
            raise ValueError("min_trust_for_autonomous_truth must be in [0,1].")


@dataclass(frozen=True)
class CloudAdjunctDecision:
    """Routing decision for one cloud request."""

    execution_path: str
    cloud_enabled: bool
    can_join_active_orbit: bool
    active_orbit_bodies: Tuple[str, ...]
    requires_human_confirmation: bool
    requires_local_verification: bool
    allowed_operations: Tuple[str, ...]
    failover_mode: str
    rationale: str


def default_cloud_adjunct_policy() -> CloudAdjunctPolicy:
    """Return the canonical cloud adjunct contract."""

    return CloudAdjunctPolicy()


def _cloud_role_enabled(role: str, policy: CloudAdjunctPolicy) -> bool:
    if role == CloudAdjunctRole.ARCHIVE:
        return policy.allow_archive_snapshots
    if role == CloudAdjunctRole.BATCH_COMPUTE:
        return policy.allow_async_batch_compute
    if role == CloudAdjunctRole.TRUTH_QUERY:
        return policy.allow_truth_queries
    if role == CloudAdjunctRole.MODEL_HOST:
        return policy.allow_remote_model_hosts
    return False


def _role_operations(role: str) -> Tuple[str, ...]:
    if role == CloudAdjunctRole.ARCHIVE:
        return ("snapshot", "restore_metadata", "diff")
    if role == CloudAdjunctRole.BATCH_COMPUTE:
        return ("simulate", "analyze", "return_result")
    if role == CloudAdjunctRole.TRUTH_QUERY:
        return ("retrieve", "cross_check", "summarize")
    return ("infer", "rank", "summarize")


def _role_failover(role: str) -> str:
    if role == CloudAdjunctRole.ARCHIVE:
        return "queue_snapshot_locally"
    if role == CloudAdjunctRole.TRUTH_QUERY:
        return "degrade_to_local_truth_and_cached_sources"
    return "continue_local_without_cloud"


def evaluate_cloud_adjunct(
    system: PentadSystem,
    request: CloudAdjunctRequest,
    policy: CloudAdjunctPolicy | None = None,
) -> CloudAdjunctDecision:
    """Evaluate whether and how a request may use the cloud adjunct."""

    policy = default_cloud_adjunct_policy() if policy is None else policy
    trust = trust_modulation(system)

    if not _cloud_role_enabled(request.role, policy):
        return CloudAdjunctDecision(
            execution_path="local_only",
            cloud_enabled=False,
            can_join_active_orbit=False,
            active_orbit_bodies=policy.active_orbit_bodies,
            requires_human_confirmation=True,
            requires_local_verification=True,
            allowed_operations=(),
            failover_mode="continue_local_without_cloud",
            rationale="Requested cloud role is disabled by policy; retain the closed local Pentad.",
        )

    if request.phase_lock_required or request.control_write_requested:
        return CloudAdjunctDecision(
            execution_path="local_only",
            cloud_enabled=False,
            can_join_active_orbit=False,
            active_orbit_bodies=policy.active_orbit_bodies,
            requires_human_confirmation=True,
            requires_local_verification=True,
            allowed_operations=(),
            failover_mode="continue_local_without_cloud",
            rationale=(
                "Cloud cannot participate in phase-locking or direct control writes; "
                "the live orbit must remain a five-body local loop."
            ),
        )

    if request.state_mutation == "actuation":
        return CloudAdjunctDecision(
            execution_path="local_only",
            cloud_enabled=False,
            can_join_active_orbit=False,
            active_orbit_bodies=policy.active_orbit_bodies,
            requires_human_confirmation=True,
            requires_local_verification=True,
            allowed_operations=(),
            failover_mode="continue_local_without_cloud",
            rationale="Cloud outputs may advise or persist state, but may not actuate the live orbit.",
        )

    if request.role == CloudAdjunctRole.ARCHIVE:
        return CloudAdjunctDecision(
            execution_path="adjunct_mirror",
            cloud_enabled=True,
            can_join_active_orbit=False,
            active_orbit_bodies=policy.active_orbit_bodies,
            requires_human_confirmation=False,
            requires_local_verification=False,
            allowed_operations=_role_operations(request.role),
            failover_mode=_role_failover(request.role),
            rationale="Cloud is admitted only as an external archive mirror; the active orbit remains local.",
        )

    requires_confirmation = (
        request.criticality >= policy.truth_confirmation_threshold
        or trust < policy.min_trust_for_autonomous_truth
        or request.estimated_roundtrip_ms > policy.phase_lock_latency_budget_ms
    )

    if request.role in _ASYNC_ROLES:
        return CloudAdjunctDecision(
            execution_path="adjunct_async",
            cloud_enabled=True,
            can_join_active_orbit=False,
            active_orbit_bodies=policy.active_orbit_bodies,
            requires_human_confirmation=requires_confirmation,
            requires_local_verification=True,
            allowed_operations=_role_operations(request.role),
            failover_mode=_role_failover(request.role),
            rationale=(
                "Cloud is admitted as an asynchronous reservoir; all returned results must "
                "be locally verified before they influence the five-body loop."
            ),
        )

    return CloudAdjunctDecision(
        execution_path="local_only",
        cloud_enabled=False,
        can_join_active_orbit=False,
        active_orbit_bodies=policy.active_orbit_bodies,
        requires_human_confirmation=True,
        requires_local_verification=True,
        allowed_operations=(),
        failover_mode="continue_local_without_cloud",
        rationale="Unsupported adjunct request; preserve the closed Pentad orbit.",
    )
