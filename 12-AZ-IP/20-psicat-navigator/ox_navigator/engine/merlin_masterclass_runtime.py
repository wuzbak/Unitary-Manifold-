# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Geometry-first masterclass execution and swarm-governance runtime surfaces."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any

from src.infrastructure.execution_spine import (
    ExecutionSpineHealthCheck,
    ExecutionSpineRecord,
    build_fail_closed_governance,
    repo_rel,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCT_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_SPINE_CHARTER_DOC = REPO_ROOT / "9-INFRASTRUCTURE" / "EXECUTION_SPINE_CONVERGENCE_CHARTER.md"
EXECUTION_BOARD_DOC = PRODUCT_ROOT / "PSICAT_EXECUTION_BOARD.md"
README_DOC = PRODUCT_ROOT / "README.md"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_rel(path: Path) -> str:
    return repo_rel(path, REPO_ROOT)


def _run_git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return str(completed.stdout or "").strip()


def _visible_branch_rows(limit: int = 16) -> list[dict[str, Any]]:
    current_branch = _run_git("branch", "--show-current") or "unknown"
    raw = _run_git("branch", "--format", "%(refname:short)")
    branches: list[str] = []
    if raw:
        branches.extend(item.strip() for item in raw.splitlines() if item.strip())
    remote_raw = _run_git("branch", "--remotes", "--format", "%(refname:short)")
    if remote_raw:
        branches.extend(item.strip() for item in remote_raw.splitlines() if item.strip())
    deduped: list[str] = []
    for branch in branches:
        if branch not in deduped:
            deduped.append(branch)
    rows: list[dict[str, Any]] = []
    for branch in deduped[: max(1, int(limit))]:
        scope = "current" if branch == current_branch else ("remote" if branch.startswith("origin/") else "local")
        rows.append(
            {
                "branch": branch,
                "scope": scope,
                "classification": "active_runtime_governance" if scope == "current" else "adjacent_visible_only",
                "promotion_rule": "Branch intent, dependency mapping, and explicit evidence packet required before merge or promotion.",
            }
        )
    if not rows:
        rows.append(
            {
                "branch": current_branch,
                "scope": "current",
                "classification": "active_runtime_governance",
                "promotion_rule": "Branch intent, dependency mapping, and explicit evidence packet required before merge or promotion.",
            }
        )
    return rows


def _endpoint_pressure(events: list[dict[str, Any]]) -> dict[str, Any]:
    endpoints = [str(item.get("endpoint") or "unknown") for item in events]
    counts = Counter(endpoints)
    dominant_endpoint, dominant_count = ("unknown", 0)
    if counts:
        dominant_endpoint, dominant_count = counts.most_common(1)[0]
    total = max(1, len(endpoints))
    return {
        "distinct_endpoint_count": len(counts),
        "dominant_endpoint": dominant_endpoint,
        "dominant_endpoint_share": dominant_count / total,
        "endpoint_counts": dict(counts),
    }


def analyze_swarm_trajectory(
    events: list[dict[str, Any]] | None = None,
    *,
    allow_internal_swarm: bool = True,
    source: str = "unknown",
) -> dict[str, Any]:
    rows = [dict(item) for item in list(events or []) if isinstance(item, dict)]
    total_events = len(rows)
    actor_ids = [str(item.get("actor_id") or "").strip() for item in rows if str(item.get("actor_id") or "").strip()]
    source_types = [str(item.get("source_type") or "external").strip().lower() for item in rows]
    privilege_events = sum(bool(item.get("privilege_requested")) for item in rows)
    schema_probe_events = sum(bool(item.get("schema_probe")) for item in rows)
    contradiction_events = sum(bool(item.get("contradiction_flagged")) for item in rows)
    quarantined_events = sum(bool(item.get("quarantined")) for item in rows)
    branch_target_events = sum(bool(item.get("branch_targeted")) for item in rows)
    repeated_signature_events = sum(bool(item.get("repeated_signature")) for item in rows)
    orchestration_events = sum(
        "/api/agentInvoke" in str(item.get("endpoint") or "")
        or "/api/agentOrchestrate" in str(item.get("endpoint") or "")
        for item in rows
    )
    pressure = _endpoint_pressure(rows)
    unique_actors = len({item for item in actor_ids if item})
    internal_events = sum(item == "internal" for item in source_types)
    internal_ratio = (internal_events / total_events) if total_events else 0.0
    coordinated = bool(
        total_events >= 4
        and (
            unique_actors >= 2
            or repeated_signature_events >= 2
            or float(pressure["dominant_endpoint_share"]) >= 0.6
        )
    )
    hostile_signal_count = (
        privilege_events
        + schema_probe_events
        + contradiction_events
        + quarantined_events
        + branch_target_events
        + repeated_signature_events
    )
    if total_events == 0:
        state = "INSUFFICIENT_SIGNAL"
        attractor = "unknown"
        transition = "observe"
    elif allow_internal_swarm and coordinated and internal_ratio >= 0.6 and hostile_signal_count == 0:
        state = "TRUSTED_INTERNAL_SWARM"
        attractor = "stable_trusted_attractor"
        transition = "admissible"
    elif coordinated and hostile_signal_count >= 4:
        state = "HOSTILE_SWARM_PRESSURE"
        attractor = "hostile_pressure_attractor"
        transition = "non_admissible"
    elif coordinated and (quarantined_events > 0 or contradiction_events > 0):
        state = "QUARANTINE_BASIN"
        attractor = "contradiction_quarantine_basin"
        transition = "quarantine"
    elif coordinated or hostile_signal_count >= 2:
        state = "SUSPICIOUS_COORDINATED_PRESSURE"
        attractor = "watchful_boundary_layer"
        transition = "watch"
    elif total_events >= 3:
        state = "NOISY_BURST"
        attractor = "unstable_noise_basin"
        transition = "hold"
    else:
        state = "ROUTINE_SINGLE_TRAJECTORY"
        attractor = "routine_execution_lane"
        transition = "admissible"
    control_actions = {
        "INSUFFICIENT_SIGNAL": ["observe"],
        "ROUTINE_SINGLE_TRAJECTORY": ["observe"],
        "NOISY_BURST": ["observe", "rate_limit", "hold"],
        "SUSPICIOUS_COORDINATED_PRESSURE": ["hold", "rate_limit", "sandbox", "human_review"],
        "QUARANTINE_BASIN": ["quarantine", "sandbox", "human_review", "convert_to_training"],
        "HOSTILE_SWARM_PRESSURE": ["quarantine", "sandbox", "reject", "human_review", "convert_to_training"],
        "TRUSTED_INTERNAL_SWARM": ["allow_bounded_swarm", "log", "benchmark", "cross_check"],
    }
    return {
        "analysis_id": "psicat_swarm_trajectory_analysis_v1",
        "generated_at": _utcnow(),
        "source": source,
        "state_class": state,
        "trajectory_attractor": attractor,
        "transition_verdict": transition,
        "counts": {
            "total_events": total_events,
            "unique_actors": unique_actors,
            "internal_ratio": internal_ratio,
            "privilege_events": privilege_events,
            "schema_probe_events": schema_probe_events,
            "contradiction_events": contradiction_events,
            "quarantined_events": quarantined_events,
            "branch_target_events": branch_target_events,
            "repeated_signature_events": repeated_signature_events,
            "orchestration_events": orchestration_events,
        },
        "pressure_map": pressure,
        "coordinated": coordinated,
        "hostile_signal_count": hostile_signal_count,
        "recommended_actions": control_actions[state],
        "conversion_targets": [
            "adversarial_benchmark_corpus",
            "training_challenge_pack",
            "contradiction_signature_library",
            "routing_policy_refinement",
        ]
        if state in {"QUARANTINE_BASIN", "HOSTILE_SWARM_PRESSURE", "SUSPICIOUS_COORDINATED_PRESSURE"}
        else [],
        "policy": {
            "offensive_use_forbidden": True,
            "commandeering_third_party_swarms_forbidden": True,
            "human_review_required": state in {"QUARANTINE_BASIN", "HOSTILE_SWARM_PRESSURE"},
            "trusted_internal_swarm_requires_bounded_roles": True,
        },
    }


def get_masterclass_execution_packet(limit: int = 16) -> dict[str, Any]:
    branches = _visible_branch_rows(limit=limit)
    health_checks = [
        ExecutionSpineHealthCheck(
            check_id="execution_spine_charter_present",
            passed=EXECUTION_SPINE_CHARTER_DOC.exists(),
            status="pass" if EXECUTION_SPINE_CHARTER_DOC.exists() else "fail",
            summary="The canonical execution-spine convergence charter must remain present.",
            sources=[_repo_rel(EXECUTION_SPINE_CHARTER_DOC)],
        ),
        ExecutionSpineHealthCheck(
            check_id="execution_board_present",
            passed=EXECUTION_BOARD_DOC.exists(),
            status="pass" if EXECUTION_BOARD_DOC.exists() else "fail",
            summary="The PsiCat execution board must remain present for active operating visibility.",
            sources=[_repo_rel(EXECUTION_BOARD_DOC)],
        ),
        ExecutionSpineHealthCheck(
            check_id="visible_branch_state_captured",
            passed=bool(branches),
            status="pass" if branches else "fail",
            summary="At least one visible branch record must be captured for branch-aware execution.",
            details={"visible_branch_count": len(branches)},
            sources=["git branch --format", "git branch --remotes --format"],
        ),
    ]
    execution_spine = ExecutionSpineRecord(
        surface_id="psicat_masterclass_execution_packet",
        surface_kind="masterclass_execution_packet",
        lane="geometry_first_governance",
        status="ACTIVE_EXECUTION_PACKET",
        summary="Geometry-first governance, branch-aware execution, PsiCat co-runner, and swarm-safe control packet.",
        canonical_paths=[
            _repo_rel(README_DOC),
            _repo_rel(EXECUTION_BOARD_DOC),
            _repo_rel(EXECUTION_SPINE_CHARTER_DOC),
        ],
        sources=[
            _repo_rel(README_DOC),
            _repo_rel(EXECUTION_BOARD_DOC),
            _repo_rel(EXECUTION_SPINE_CHARTER_DOC),
        ],
        governance=build_fail_closed_governance(
            epistemic_label="GOVERNANCE",
            promotion_rule="The packet governs runtime execution and swarm defense; it does not claim scientific closure or offensive capability.",
            residual_blockers=[
                "Visible branch classification is limited to locally available refs in the current clone.",
                "Hostile swarm attribution remains probabilistic and requires human review for critical actions.",
            ],
        ),
        compatibility={
            "primary_endpoint": "/api/psicat/masterclass-execution",
            "legacy_endpoints": ["/api/merlin/masterclass-execution", "/api/ox/masterclass-execution"],
            "analysis_endpoint": "/api/psicat/swarm-analyze",
        },
        health_checks=health_checks,
        promotion={
            "eligible": False,
            "gate": "governed_execution_only",
            "reason": "The packet defines execution doctrine and control surfaces, not a completion or promotion receipt.",
        },
    ).to_dict()
    return {
        "generated_at": _utcnow(),
        "execution_spine": execution_spine,
        "command_doctrine": [
            "execution_first",
            "truth_first",
            "geometry_first",
            "swarm_safe",
            "branch_aware",
        ],
        "master_objective": "Advance the repository into a geometry-native governance and execution system with Lean proof boundaries, Python runtime state control, PsiCat governed co-running, and swarm-safe defensive orchestration.",
        "lanes": [
            {
                "lane_id": "A",
                "name": "formal_frontier",
                "purpose": "Tighten Lean work into deterministic burden units with explicit promotion boundaries.",
                "done_when": "Touched formal units have explicit verdicts and unverified global build limits stay visible.",
            },
            {
                "lane_id": "B",
                "name": "geometry_first_runtime",
                "purpose": "Model governance as state-space control with attractors, contradictions, barriers, and admissible transitions.",
                "done_when": "Runtime surfaces classify trajectories structurally rather than by vague scorecards alone.",
            },
            {
                "lane_id": "C",
                "name": "psicat_active_co_runner",
                "purpose": "Keep training, benchmarks, challenge packs, contradiction/quarantine signals, and promotion packets in one governed loop.",
                "done_when": "PsiCat learns from misses and blockers while staying fail-closed and receipt-backed.",
            },
            {
                "lane_id": "D",
                "name": "swarm_orchestration_and_defense",
                "purpose": "Permit bounded internal swarms and detect, quarantine, or sandbox hostile coordinated pressure.",
                "done_when": "Trusted swarms help and hostile coordination is recognized early and routed safely.",
            },
            {
                "lane_id": "E",
                "name": "governance_hardening",
                "purpose": "Bind approval tiers, remediation, quarantine authority, human override, and demotion into one runtime-active doctrine.",
                "done_when": "Sensitive and critical transitions remain explicit under speed and pressure.",
            },
            {
                "lane_id": "F",
                "name": "monorepo_branch_convergence",
                "purpose": "Move fast without corrupting truth surfaces or branch intent.",
                "done_when": "Branch parallelism increases throughput without multiplying confusion or silent drift.",
            },
        ],
        "primary_lane": "geometry_first_runtime",
        "support_lanes": [
            "formal_frontier",
            "psicat_active_co_runner",
            "monorepo_branch_convergence",
            "swarm_orchestration_and_defense",
        ],
        "common_receipt_model": {
            "receipt_types": [
                "formal_receipt",
                "runtime_receipt",
                "benchmark_receipt",
                "governance_receipt",
                "swarm_receipt",
                "branch_convergence_receipt",
            ],
            "shared_fields": [
                "surface_id",
                "lane",
                "status",
                "summary",
                "evidence_artifacts",
                "health_checks",
                "blockers",
                "remediation_actions",
                "promotion_rule",
                "rollback_path",
            ],
        },
        "observability_layer": {
            "signals": [
                "contradictions",
                "quarantines",
                "escalation_events",
                "benchmark_posture",
                "lane_health",
                "branch_state",
                "promotion_blockers",
            ],
            "trajectory_axes": [
                "coherence",
                "contradiction_density",
                "boundary_pressure",
                "privilege_seeking",
                "schema_probing",
                "endpoint_concentration",
                "branch_targeting",
            ],
        },
        "geometry_state_space": {
            "states": [
                "ROUTINE_SINGLE_TRAJECTORY",
                "NOISY_BURST",
                "SUSPICIOUS_COORDINATED_PRESSURE",
                "TRUSTED_INTERNAL_SWARM",
                "QUARANTINE_BASIN",
                "HOSTILE_SWARM_PRESSURE",
            ],
            "allowed_transition_rule": "Only admissible and watch-class trajectories may advance automatically; quarantine and hostile states require containment and review.",
            "forbidden_transition_rule": "No hostile, contradiction-heavy, or privilege-seeking swarm may gain sensitive capability without human approval.",
        },
        "swarm_framework": {
            "ethical_internal_swarm_roles": [
                "specialized_review_lane",
                "bounded_execution_role",
                "contradiction_triage_lane",
                "formal_runtime_cross_check_lane",
                "benchmark_and_remediation_lane",
            ],
            "hostile_recognition_classes": [
                "coordinated_schema_probing",
                "repeated_privilege_seeking",
                "contradiction_flooding",
                "synchronized_endpoint_pressure",
                "branch_or_status_manipulation",
                "repeat_quarantine_signature",
            ],
            "control_actions": [
                "observe",
                "rate_limit",
                "hold",
                "quarantine",
                "sandbox",
                "human_review",
                "reject",
                "convert_to_training",
            ],
            "hard_constraints": [
                "no_offensive_cyber_behavior",
                "no_commandeering_third_party_swarms",
                "no_hidden_external_automation",
                "no_claim_inflation",
            ],
        },
        "branch_convergence": {
            "visible_branches": branches,
            "intent_requirements": [
                "branch_class",
                "dependency_map",
                "collision_review",
                "promotion_authority",
            ],
            "visibility_limit_note": "Only branches visible in the current local clone can be classified automatically; hidden adjacent branches require explicit human context or fetch.",
        },
        "immediate_execution_packet": [
            "freeze_doctrine",
            "classify_visible_branches",
            "route_primary_lane_to_geometry_first_runtime",
            "bind_common_receipt_model",
            "bind_observability_signals",
            "stand_up_swarm_doctrine",
            "execute_changed_surface_first",
        ],
        "operating_rhythm": {
            "every_session": [
                "bootstrap_from_canonical_truth_surfaces",
                "inspect_current_branch_state",
                "identify_primary_and_support_targets",
                "act_validate_checkpoint",
            ],
            "every_burst": [
                "one_primary_deliverable",
                "one_or_two_support_deliverables",
                "explicit_blocker_board",
                "one_receipt_packet",
                "one_resume_point",
            ],
            "promotion_conversation_rule": "Only evidence, blockers, readiness, and consequences; no symbolic advancement.",
        },
    }
