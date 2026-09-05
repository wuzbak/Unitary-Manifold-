# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Merlin replacement program artifacts and evaluation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import shlex
import sys
from typing import Any

from .constants import GATE_LABELS
from .merlin_admission import get_model_admission_policy
from .merlin_identity import get_identity_policy
from .merlin_memory import MERLIN_MAX_HISTORY
from .merlin_router import get_router_policy
from .merlin_runtime import (
    get_advanced_execution_graph,
    get_benchmark_suite,
    get_mythos_astra_runtime_contract,
    get_optimization_priorities,
)
from .merlin_sentinel import get_sentinel_policy
from .merlin_workspace import get_workspace_policy, get_workspace_state

REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProvenanceSource:
    source_id: str
    path: str
    claim_class: str
    confidence_tier: str
    gate: str
    purpose: str


PROGRAM_NON_NEGOTIABLES = {
    "epistemic_labels": [
        "HARDGATE",
        "ADJACENT_TRACK",
        "DERIVED",
        "OPEN_GAP",
        "ARCHITECTURE_LIMIT",
        "GOVERNANCE",
    ],
    "governance_boundary": "Keep physics claims and Pentad governance claims explicitly separated.",
    "certainty_policy": "No hidden certainty language; uncertainty and open gaps must be explicit.",
    "traceability": "Every answer path must cite typed provenance sources.",
}


def get_mentorship_sprint_charter() -> dict[str, Any]:
    return {
        "name": "Merlin Mentorship Sprint",
        "parent_office": "Merlin Program Office",
        "mode": "full_rigor_no_partial_delivery",
        "mission": (
            "Run a multi-model mentorship sprint where specialized lanes transfer process knowledge "
            "into Merlin's governed back-room until mentorship-to-runtime closure is earned."
        ),
        "non_negotiables": [
            "full_rigor_required",
            "no_partial_or_half_measures",
            "auditable_decisions_only",
            "fail_closed_promotion_gates",
        ],
        "governance": {
            "decision_ledger_required": True,
            "risk_ledger_required": True,
            "unresolved_high_severity_risks_block_promotion": True,
        },
        "updated_at": _utcnow(),
    }


def get_specialized_model_faculty_matrix() -> dict[str, Any]:
    faculty = [
        {
            "role": "small_router_faculty",
            "lane": "small_fast_router",
            "teaching_scope": [
                "intent_routing",
                "risk_precheck",
                "safe_tool_selection",
            ],
            "acceptance_rubric": [
                "routing_policy_alignment",
                "risk_label_precision",
                "tool_allowlist_compliance",
            ],
            "required_artifacts": [
                "router_playbook",
                "routing_failure_counterexamples",
                "route_decision_criteria",
                "benchmark_aligned_router_exemplars",
            ],
        },
        {
            "role": "medium_default_faculty",
            "lane": "medium_reasoner_default",
            "teaching_scope": [
                "repository_governance_synthesis",
                "boundary_disciplined_answers",
                "citation_faithfulness",
            ],
            "acceptance_rubric": [
                "task_success_parity_or_better",
                "explicit_uncertainty_discipline",
                "typed_provenance_completeness",
            ],
            "required_artifacts": [
                "reasoning_playbook",
                "quality_regression_counterexamples",
                "answer_decision_criteria",
                "stage_a_quality_exemplars",
            ],
        },
        {
            "role": "heavy_exception_faculty",
            "lane": "heavy_reasoner_exception",
            "teaching_scope": [
                "long_context_reconciliation",
                "cross_source_conflict_resolution",
                "high_impact_exception_handling",
            ],
            "acceptance_rubric": [
                "exception_path_justification_quality",
                "cross_source_consistency",
                "fallback_trigger_discipline",
            ],
            "required_artifacts": [
                "long_context_playbook",
                "conflict_reconciliation_counterexamples",
                "escalation_decision_criteria",
                "exception_benchmark_exemplars",
            ],
        },
        {
            "role": "safety_governance_faculty",
            "lane": "safety_governance",
            "teaching_scope": [
                "sentinel_enforcement",
                "identity_trust_controls",
                "physics_governance_boundary",
            ],
            "acceptance_rubric": [
                "zero_high_severity_policy_violations",
                "boundary_statement_completeness",
                "privileged_action_authorization_compliance",
            ],
            "required_artifacts": [
                "safety_playbook",
                "policy_bypass_counterexamples",
                "governance_decision_criteria",
                "safety_benchmark_exemplars",
            ],
        },
        {
            "role": "benchmarking_faculty",
            "lane": "benchmark_and_empirical_gating",
            "teaching_scope": [
                "stage_a_receipt_generation",
                "replacement_gate_evaluation",
                "longitudinal_clean_window_validation",
            ],
            "acceptance_rubric": [
                "reproducible_receipts",
                "gate_contract_fidelity",
                "energy_per_successful_task_tracking",
            ],
            "required_artifacts": [
                "benchmark_ops_playbook",
                "gate_failure_counterexamples",
                "promotion_decision_criteria",
                "receipt_aligned_benchmark_exemplars",
            ],
        },
    ]
    return {
        "program": "merlin_all_hands_maximum_effort",
        "faculty": faculty,
        "required_peer_review_per_specialist": 1,
        "updated_at": _utcnow(),
    }


def get_knowledge_transfer_cycles() -> dict[str, Any]:
    return {
        "cadence": "structured_specialist_cycles",
        "deposit_bundle_required": [
            "process_playbooks",
            "failure_patterns_and_counterexamples",
            "decision_criteria",
            "benchmark_aligned_exemplars",
        ],
        "cycle_phases": [
            "specialist_prepare",
            "back_room_deposit",
            "peer_review_and_reconciliation",
            "risk_ledger_commit",
        ],
        "workspace_targets": {
            "policy_surface": "getMerlinWorkspacePolicy",
            "state_surface": "getMerlinWorkspaceState",
            "exchange_ledger": "merlin_mentorship_session_ledger",
        },
    }


def get_mentorship_library_and_study_assets() -> dict[str, Any]:
    return {
        "library": {
            "curated_canonical_sources": [
                "STATUS.md",
                "FALLIBILITY.md",
                "5-GOVERNANCE/SEPARATION.md",
                "12-AZ-IP/20-merlin-navigator/README.md",
            ],
            "typed_provenance_registry_surface": "getMerlinKnowledgeCore",
            "benchmark_corpora_surfaces": [
                "getMerlinBenchmarkSuite",
                "getMerlinBenchmarkCorpus",
                "getMerlinMultiStageBenchmarks",
            ],
        },
        "study": {
            "active_training_queue_surface": "getMerlinTrainingPlan",
            "contradiction_log_surface": "getMerlinMemoryState",
            "replay_pack_surface": "runMerlinStageAReceipts",
            "mentorship_session_ledger": {
                "required_fields": [
                    "session_id",
                    "specialist_role",
                    "reviewed_role",
                    "artifacts_deposited",
                    "reconciliation_outcome",
                    "unresolved_risks",
                    "timestamp",
                ],
            },
        },
    }


def get_cross_model_exchange_protocol() -> dict[str, Any]:
    return {
        "policy": "Each specialist must review at least one other specialist output before closure.",
        "requirements": {
            "minimum_peer_reviews_per_specialist": 1,
            "reconciliation_required": True,
            "unresolved_conflicts_must_enter_risk_ledger": True,
            "silent_merge_forbidden": True,
        },
        "risk_logging_contract": {
            "risk_class": "mentorship_unresolved_conflict",
            "minimum_fields": ["specialist_role", "conflict_summary", "severity", "resolution_owner"],
        },
    }


def get_mentorship_completion_contract() -> dict[str, Any]:
    return {
        "name": "mentorship_to_runtime_closure",
        "required_checks": [
            "faculty_artifacts_landed",
            "library_and_study_populated_and_auditable",
            "exchange_cycle_complete",
            "control_tower_deployment_eligibility",
            "no_unresolved_high_severity_risks",
        ],
        "gate_policy": "fail_closed",
    }


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_program_charter() -> dict[str, Any]:
    return {
        "name": "Merlin Replacement Program",
        "mission": (
            "Make Merlin the primary open-science assistant for repository and governance intelligence "
            "with lower energy-per-successful-task than the incumbent token-dependent external-model path."
        ),
        "ownership": {
            "stewards": ["AxiomZero", "@wuzbak", "GitHub Copilot Task Agent"],
            "product_root": str(PRODUCT_ROOT),
        },
        "non_negotiables": PROGRAM_NON_NEGOTIABLES,
        "success_metrics": {
            "primary": [
                "quality_parity_or_better",
                "energy_per_successful_task_lower_than_incumbent",
                "safety_and_governance_compliance_stable",
                "self_hostable_reproducible_and_auditable_stack",
            ],
            "secondary": [
                "lower_external_model_dependency",
                "predictable_latency_budget",
                "deterministic_failure_recovery",
            ],
        },
        "last_updated": _utcnow(),
    }


def get_program_office() -> dict[str, Any]:
    return {
        "name": "Merlin Program Office",
        "mode": "replacement_program_not_feature_work",
        "authority_model": {
            "approve": "promotion gate board",
            "hold": "program office",
            "rollback": "program office + stewards",
        },
        "decision_ledger": {
            "single_source_of_truth": "merlin_control_tower_packet",
            "required_fields": [
                "decision",
                "gate_pass",
                "empirical_gate",
                "sync_checks_ok",
                "deployment_eligibility",
                "timestamp",
            ],
            "policy": "No stage promotion without explicit ledger entry.",
        },
        "risk_ledger": {
            "required_risk_classes": [
                "quality_regression",
                "energy_regression",
                "governance_boundary_violation",
                "safety_policy_violation",
                "operational_reliability",
            ],
            "escalation_rule": "Any unresolved high-severity risk blocks promotion.",
        },
        "gate_board": {
            "frozen_success_contract": [
                "quality_parity_or_better",
                "lower_energy_per_successful_task",
                "stable_safety_and_governance_compliance",
                "operational_reliability_under_load",
            ],
            "fail_closed": True,
        },
        "parallel_squads": [
            {"id": "A", "name": "model_stack_and_routing"},
            {"id": "B", "name": "benchmark_and_empirical_gating"},
            {"id": "C", "name": "toolchain_governed_expansion"},
            {"id": "D", "name": "memory_provenance_telemetry_observability"},
            {"id": "E", "name": "security_safety_identity_hardening"},
            {"id": "F", "name": "product_operator_transparency_surfaces"},
            {"id": "G", "name": "ci_release_and_artifact_governance"},
            {"id": "H", "name": "migration_cutover_decommission_operations"},
        ],
        "operating_rhythm": get_operating_rhythm(),
        "mentorship_sprint": {
            "charter": get_mentorship_sprint_charter(),
            "faculty_matrix": get_specialized_model_faculty_matrix(),
            "knowledge_transfer_cycles": get_knowledge_transfer_cycles(),
            "library_and_study": get_mentorship_library_and_study_assets(),
            "cross_model_exchange_protocol": get_cross_model_exchange_protocol(),
            "completion_contract": get_mentorship_completion_contract(),
        },
        "updated_at": _utcnow(),
    }


def get_replacement_scope() -> dict[str, Any]:
    return {
        "takeover_in_scope": [
            "repository_status_and_claim_navigation",
            "pillar_and_test_traceability_qa",
            "governance_boundary_and_pentad_reasoning_support",
            "tool-assisted corpus navigation via /api/agentToolkit stack",
            "offline-rag-first assistance when live keys are unavailable",
        ],
        "out_of_scope_for_full_replacement": [
            "unbounded external web truth arbitration",
            "unconstrained autonomous write/execute actions without governance gates",
            "formal hardgate acceptance decisions reserved for human stewards",
            "single-model monopoly architecture without staged fallback",
        ],
        "fallback_allowed_when": [
            "confidence below threshold for high-impact responses",
            "task complexity exceeds medium reasoning profile",
            "explicit user request for external comparative model output",
        ],
    }


def get_current_stack_baseline() -> dict[str, Any]:
    return {
        "baseline_product": "12-AZ-IP/20-merlin-navigator",
        "live_model_transport": "Sovereign local runtime primary; OpenRouter stealth/ox-alpha compatibility-only",
        "current_limits": {
            "live_dependency": "OpenRouter path requires OPENROUTER_API_KEY and explicit compatibility enablement",
            "offline_path": "offline_rag fallback",
            "tool_round_cap": 2,
            "orchestration_step_cap": 10,
            "session_memory_max_turns": MERLIN_MAX_HISTORY,
            "tooling_mode": "safe read-mostly toolkit",
        },
        "capabilities_now": [
            "/api/merlin query pipeline",
            "/api/merlin/status live status surface",
            "/api/merlin/memory audited multi-tier memory surface",
            "/api/merlin/telemetry measurable run summary surface",
            "/api/agentToolkit capability discovery",
            "/api/agentInvoke single-tool execution",
            "/api/agentOrchestrate bounded multi-step execution",
            "gate badge extraction and strict response contract",
            "RAG context from repository knowledge base + pillar context + interrogator",
            "typed provenance payloads and Stage A benchmark corpus",
        ],
        "gaps_to_replacement": [
            "stage-a parity capture exists, but broader multi-stage corpus coverage is still required",
            "heavy-lane self-hosted routing still needs empirical tuning beyond the current benchmark gate",
            "scheduled benchmark artifacts exist, but steward-reviewed longitudinal acceptance cadence is not yet complete",
            "cross-run artifact retention and comparison dashboards are still limited to exported JSON bundles",
        ],
    }


def get_weights_and_measures() -> dict[str, Any]:
    return {
        "scorecard_axes": [
            "quality",
            "latency",
            "cost",
            "energy",
            "safety",
            "governance_compliance",
        ],
        "acceptance_bands": {
            "quality": ">= incumbent median and no critical factual regressions",
            "latency": "p95 bounded by stage target",
            "cost": "non-increasing per accepted answer",
            "energy": "strictly lower energy-per-successful-task than incumbent baseline",
            "safety": "0 unresolved high-severity policy violations",
            "governance_compliance": "100% explicit gate/boundary compliance",
        },
        "task_batteries": {
            "core_physics_qa": "hardgate/adjacent/open-gap differentiation and prediction fidelity",
            "pentad_governance_reasoning": "decision consistency, legitimacy checks, intervention safety",
            "tool_use": "safe single-tool and orchestrated multi-step accuracy",
            "citation_faithfulness": "source-path correctness and claim-class consistency",
            "long_context_synthesis": "multi-source compression without boundary drift",
            "refusal_correctness": "proper non-answer when unsupported or unsafe",
            "uncertainty_recovery": "closest-pillar fallback and explicit confidence handling",
        },
        "side_by_side_eval": {
            "required": True,
            "policy": "Run identical prompt sets against Merlin and designated external reference models with fixed rubrics.",
            "rubric_fields": [
                "factuality",
                "traceability",
                "boundary_compliance",
                "task_success",
                "energy_estimate",
            ],
            "stage_a_entrypoint": "getMerlinBenchmarkSuite.stage_a_corpus",
        },
    }


def get_knowledge_core_sources() -> dict[str, Any]:
    sources = [
        ProvenanceSource(
            source_id="status",
            path=str(REPO_ROOT / "STATUS.md"),
            claim_class="live_status",
            confidence_tier="canonical",
            gate="GOVERNANCE",
            purpose="Current repo-wide status, test counts, sprint identity.",
        ),
        ProvenanceSource(
            source_id="fallibility",
            path=str(REPO_ROOT / "FALLIBILITY.md"),
            claim_class="epistemic_limits",
            confidence_tier="canonical",
            gate="OPEN_GAP",
            purpose="Known unresolved tensions and explicit limits.",
        ),
        ProvenanceSource(
            source_id="governance_separation",
            path=str(REPO_ROOT / "5-GOVERNANCE" / "SEPARATION.md"),
            claim_class="governance_boundary",
            confidence_tier="canonical",
            gate="GOVERNANCE",
            purpose="Physics-vs-governance separation rule.",
        ),
        ProvenanceSource(
            source_id="pentad_readme",
            path=str(REPO_ROOT / "5-GOVERNANCE" / "Unitary Pentad" / "README.md"),
            claim_class="governance_system",
            confidence_tier="canonical",
            gate="GOVERNANCE",
            purpose="Pentad definitions, constraints, and operating assumptions.",
        ),
        ProvenanceSource(
            source_id="product20_readme",
            path=str(PRODUCT_ROOT / "README.md"),
            claim_class="product_contract",
            confidence_tier="canonical",
            gate="ARCHITECTURE_LIMIT",
            purpose="Merlin Product 20 contract, endpoints, and mode behavior.",
        ),
        ProvenanceSource(
            source_id="merlin_server",
            path=str(PRODUCT_ROOT / "ox_navigator" / "app" / "server.py"),
            claim_class="runtime_api",
            confidence_tier="runtime",
            gate="GOVERNANCE",
            purpose="Runtime API contract and compatibility shim behavior.",
        ),
    ]
    return {
        "typed_provenance_schema": {
            "fields": ["source_id", "path", "claim_class", "confidence_tier", "gate", "purpose"],
        },
        "sources": [asdict(item) for item in sources],
    }


def run_sync_checks() -> dict[str, Any]:
    knowledge = get_knowledge_core_sources()
    checks = []
    for source in knowledge["sources"]:
        path = Path(source["path"])
        checks.append({
            "source_id": source["source_id"],
            "path": source["path"],
            "exists": path.exists(),
            "readable": path.is_file(),
            "claim_class": source["claim_class"],
            "gate": source["gate"],
        })
    server_path = PRODUCT_ROOT / "ox_navigator" / "app" / "server.py"
    server_text = server_path.read_text(encoding="utf-8") if server_path.exists() else ""
    route_eq_matches = re.findall(r"parsed\.path\s*==\s*['\"]([^'\"]+)['\"]", server_text)
    route_in_blocks = re.findall(r"parsed\.path\s+in\s*\(([^)]*)\)", server_text, flags=re.DOTALL)
    parsed_routes = set(route_eq_matches)
    for block in route_in_blocks:
        for route in re.findall(r"['\"]([^'\"]+)['\"]", block):
            parsed_routes.add(route)

    runtime_endpoint_checks = []
    for endpoint in [
        "/api/merlin",
        "/api/merlin/status",
        "/api/merlin/program",
        "/api/merlin/program-office",
        "/api/merlin/control-tower",
        "/api/merlin/memory",
        "/api/merlin/telemetry",
        "/api/merlin/policy",
        "/api/merlin/runtime",
        "/api/merlin/benchmarks",
        "/api/merlin/training-architecture",
        "/api/merlin/training-dataset",
        "/api/merlin/mlflow-manifests",
        "/api/merlin/open-science-registry",
        "/api/merlin/competitive-benchmarks",
        "/api/merlin/benchmark-corpora",
        "/api/merlin/stage-a-receipts",
        "/api/merlin/replacement-readiness",
        "/api/merlin/frontier-readiness",
        "/api/merlin/training-artifacts",
        "/api/merlin/promotion-packet",
        "/api/merlin/sync-checks",
        "/api/merlin/identity",
        "/api/agentToolkit",
        "/api/agentInvoke",
        "/api/agentOrchestrate",
        "/api/ox",
        "/api/ox/status",
    ]:
        runtime_endpoint_checks.append({"endpoint": endpoint, "present": endpoint in parsed_routes})

    ui_path = PRODUCT_ROOT / "ui" / "ox-navigator.js"
    ui_text = ui_path.read_text(encoding="utf-8") if ui_path.exists() else ""
    gate_label_checks = [{"gate": gate, "present": f"'{gate}'" in ui_text} for gate in GATE_LABELS]

    ok = all(item["exists"] and item["readable"] for item in checks)
    runtime_ok = all(item["present"] for item in runtime_endpoint_checks)
    gate_labels_ok = all(item["present"] for item in gate_label_checks)
    endpoint_targets = [
        "/api/merlin",
        "/api/merlin/status",
        "/api/merlin/program",
        "/api/merlin/program-office",
        "/api/merlin/control-tower",
        "/api/merlin/memory",
        "/api/merlin/telemetry",
        "/api/merlin/benchmarks",
        "/api/merlin/training-architecture",
        "/api/merlin/training-dataset",
        "/api/merlin/mlflow-manifests",
        "/api/merlin/open-science-registry",
        "/api/merlin/competitive-benchmarks",
        "/api/merlin/benchmark-corpora",
        "/api/merlin/stage-a-receipts",
        "/api/merlin/replacement-readiness",
        "/api/merlin/frontier-readiness",
        "/api/merlin/training-artifacts",
        "/api/merlin/promotion-packet",
        "/api/agentToolkit",
        "/api/agentInvoke",
        "/api/agentOrchestrate",
        "/api/ox",
        "/api/ox/status",
    ]
    gate_targets = [
        "HARDGATE",
        "ADJACENT_TRACK",
        "OPEN_GAP",
        "ARCHITECTURE_LIMIT",
        "GOVERNANCE",
    ]
    readme_text = (PRODUCT_ROOT / "README.md").read_text(encoding="utf-8")
    endpoint_re = re.compile(r"/api/[a-zA-Z0-9_/-]+")
    server_endpoints = set(parsed_routes)
    readme_endpoints = set(endpoint_re.findall(readme_text))
    endpoint_checks = []
    for endpoint in endpoint_targets:
        present_everywhere = endpoint in server_endpoints and endpoint in readme_endpoints
        endpoint_checks.append({
            "endpoint": endpoint,
            "server": endpoint in server_endpoints,
            "readme": endpoint in readme_endpoints,
            "ok": present_everywhere,
        })
    gate_checks = []
    for gate in gate_targets:
        gate_checks.append({
            "gate": gate,
            "server": gate in server_text,
            "readme": gate in readme_text,
            "ui": gate in ui_text,
            "ok": gate in server_text and gate in readme_text and gate in ui_text,
        })
    no_derived_drift = "DERIVED" not in ui_text
    consistency_ok = all(item["ok"] for item in endpoint_checks) and all(item["ok"] for item in gate_checks) and no_derived_drift
    return {
        "ok": bool(ok and runtime_ok and gate_labels_ok and consistency_ok),
        "checked_at": _utcnow(),
        "checks": checks,
        "runtime_endpoint_checks": runtime_endpoint_checks,
        "gate_label_checks": gate_label_checks,
        "consistency": {
            "endpoint_checks": endpoint_checks,
            "gate_checks": gate_checks,
            "no_derived_drift_in_ui_gate_labels": no_derived_drift,
        },
        "policy": "Fail closed on missing canonical sources to prevent epistemic drift.",
    }


def get_model_strategy() -> dict[str, Any]:
    return {
        "routing_lanes": [
            {
                "lane": "small_fast_router",
                "purpose": "intent detection, safety precheck, tool-selection triage",
            },
            {
                "lane": "medium_reasoner_default",
                "purpose": "primary response synthesis for most repository/governance tasks",
            },
            {
                "lane": "heavy_reasoner_exception",
                "purpose": "hardest long-context or cross-source reconciliation cases only",
            },
        ],
        "open_weight_priority": "Prefer open-weight models when they satisfy quality and safety gates.",
        "fallback_policy": {
            "inputs": ["task_complexity", "confidence", "risk_level", "latency_budget"],
            "decision": "Escalate or fallback by policy, not by fixed global default.",
        },
    }


def get_training_and_adaptation() -> dict[str, Any]:
    return {
        "data_tracks": [
            "repository_native_qa",
            "governance_decision_traces",
            "adversarial_counterexamples",
            "tool_call_success_failure_pairs",
            "specialist_mentorship_artifact_deposits",
        ],
        "adaptation_tracks": [
            "supervised_tuning_for_domain_coverage",
            "tool_use_alignment_for_agentToolkit_agentInvoke_agentOrchestrate",
            "preference_optimization_for_honesty_and_boundary_discipline",
            "cross_model_mentorship_transfer_cycles",
        ],
        "quality_controls": [
            "deduplicate low-signal examples",
            "gate-label consistency checks",
            "manual steward sampling of high-impact outputs",
            "persona-governance checks cannot be overridden by style mode",
            "no_partial_delivery_in_mentorship_sprint",
        ],
        "mentorship": {
            "charter_surface": "getMerlinMentorshipSprintCharter",
            "faculty_surface": "getMerlinFacultyMatrix",
            "transfer_cycles_surface": "getMerlinKnowledgeTransferCycles",
            "exchange_protocol_surface": "getMerlinExchangeProtocol",
        },
    }


def _status_to_gate(status: str) -> str:
    upper = str(status or "").upper()
    if "OPEN" in upper:
        return "OPEN_GAP"
    if "ARCHITECTURE_LIMIT" in upper:
        return "ARCHITECTURE_LIMIT"
    if "GOVERNANCE" in upper:
        return "GOVERNANCE"
    return "HARDGATE"


def _seed_tool_alignment_examples() -> list[dict[str, Any]]:
    return [
        {
            "id": "tool-alignment-runtime-policy",
            "track": "tool_call_success_failure_pairs",
            "prompt": "Inspect Merlin runtime policy and benchmark readiness before approving wider replacement scope.",
            "preferred_tool": "getMerlinControlTower",
            "fallback_tools": ["getMerlinBenchmarkSuite", "getMerlinExecutionGraph", "getMerlinTrainingArchitecture"],
            "supervision_mode": "tool_selection_alignment",
            "required_fields": ["decision", "gate_pass", "empirical_gate", "deployment_eligibility"],
        },
        {
            "id": "tool-alignment-training-artifacts",
            "track": "tool_call_success_failure_pairs",
            "prompt": "Export the governed Merlin training pack with benchmark baseline and open-science augmentation registry.",
            "preferred_tool": "getMerlinTrainingArtifacts",
            "fallback_tools": ["getMerlinTrainingArchitecture", "getMerlinOpenScienceRegistry"],
            "supervision_mode": "tool_selection_alignment",
            "required_fields": ["training_architecture", "competitive_benchmark_plan", "open_science_registry"],
        },
        {
            "id": "tool-alignment-boundary-audit",
            "track": "tool_call_success_failure_pairs",
            "prompt": "Audit whether a Merlin answer preserved the physics-vs-governance boundary with typed provenance.",
            "preferred_tool": "getMerlinGovernancePolicy",
            "fallback_tools": ["getMerlinKnowledgeCore", "runMerlinMemoryAudit"],
            "supervision_mode": "tool_selection_alignment",
            "required_fields": ["boundary_statement", "provenance_sources", "confidence_statement"],
        },
    ]


def _build_seed_training_examples(limit: int | None = None) -> list[dict[str, Any]]:
    from .merlin_benchmark import get_stage_a_benchmark_corpus
    from .merlin_rag import KNOWLEDGE_BASE

    examples: list[dict[str, Any]] = []
    for key, entry in sorted(KNOWLEDGE_BASE.items()):
        answer_text = str(entry.get("answer", ""))
        if key == "toe_score" or "toe score" in answer_text.lower():
            continue
        examples.append(
            {
                "id": f"repo-qa-{key}",
                "track": "repository_native_qa",
                "prompt": f"Explain {entry.get('topic', key)} with explicit epistemic status and falsification or boundary notes where relevant.",
                "target": answer_text,
                "required_gates": [_status_to_gate(str(entry.get("status", "")))],
                "provenance_sources": list(entry.get("sources", [])),
                "supervision_mode": "grounded_supervised_finetuning",
            }
        )

    benchmark_corpus = get_stage_a_benchmark_corpus()
    for benchmark in benchmark_corpus["benchmarks"]:
        examples.append(
            {
                "id": f"benchmark-{benchmark['id']}",
                "track": "adversarial_counterexamples",
                "prompt": benchmark["query"],
                "target_contract": {
                    "required_gates": list(benchmark["required_gates"]),
                    "required_contract_sections": list(benchmark["required_contract_sections"]),
                    "required_provenance_kinds": list(benchmark["required_provenance_kinds"]),
                    "review_focus": list(benchmark.get("review_focus", [])),
                },
                "supervision_mode": "benchmark_contract_alignment",
            }
        )

    examples.extend(_seed_tool_alignment_examples())
    if limit is not None:
        return examples[: max(0, int(limit))]
    return examples


def get_open_science_resource_registry() -> dict[str, Any]:
    return {
        "policy": (
            "Use external open-science resources as augmentation lanes for Merlin, never as a replacement "
            "for repository-native provenance, governance boundaries, or benchmark discipline."
        ),
        "admission_requirements": [
            "license_review",
            "provenance_review",
            "task_relevance_review",
            "duplication_and_contamination_review",
            "benchmark_impact_review",
        ],
        "resources": [
            {
                "resource_id": "hugging_face_datasets",
                "category": "programmatic_dataset_hub",
                "url": "https://huggingface.co/datasets",
                "recommended_role": [
                    "primary external corpus distribution",
                    "multimodal scientific expansion",
                    "open-weight finetuning inputs",
                ],
                "priority": "highest_external",
            },
            {
                "resource_id": "openml",
                "category": "benchmark_and_tabular_lab",
                "url": "https://www.openml.org/",
                "recommended_role": [
                    "structured benchmarking",
                    "reproducible model comparisons",
                    "meta-learning experiments",
                ],
                "priority": "high",
            },
            {
                "resource_id": "uci_ml_repository",
                "category": "curated_tabular_repository",
                "url": "https://archive.ics.uci.edu/",
                "recommended_role": [
                    "classical reasoning baselines",
                    "small clean evaluation sets",
                ],
                "priority": "medium",
            },
            {
                "resource_id": "papers_with_code",
                "category": "reproducibility_index",
                "url": "https://paperswithcode.com/",
                "recommended_role": [
                    "competitive benchmark discovery",
                    "paper-to-code-to-dataset linking",
                ],
                "priority": "high",
            },
            {
                "resource_id": "mlflow",
                "category": "experiment_tracking",
                "url": "https://mlflow.org/",
                "recommended_role": [
                    "dataset lineage",
                    "model registry",
                    "run comparison and promotion governance",
                ],
                "priority": "highest_ops",
            },
            {
                "resource_id": "aws_open_data_registry",
                "category": "cloud_scale_open_science",
                "url": "https://registry.opendata.aws/",
                "recommended_role": [
                    "large-scale science corpora access",
                    "remote compute-adjacent data staging",
                ],
                "priority": "medium",
            },
            {
                "resource_id": "nairr_pilot",
                "category": "public_compute_and_datasets",
                "url": "https://nairrpilot.org/pilotresources",
                "recommended_role": [
                    "AI-ready scientific datasets",
                    "shared compute pathways for open evaluation",
                ],
                "priority": "high",
            },
            {
                "resource_id": "nasa_open_science",
                "category": "domain_science_catalog",
                "url": "https://science.nasa.gov/open-science/",
                "recommended_role": [
                    "earth-space science specialization",
                    "physics and astronomy expansion lanes",
                ],
                "priority": "high",
            },
        ],
    }


def get_training_architecture(limit: int | None = None) -> dict[str, Any]:
    seed_examples = _build_seed_training_examples(limit=limit)
    track_counts: dict[str, int] = {}
    for item in seed_examples:
        track = str(item.get("track", "unknown"))
        track_counts[track] = track_counts.get(track, 0) + 1
    return {
        "mission_profile": [
            "repository_assistant",
            "scientific_reasoning_assistant",
            "autonomous_research_agent",
        ],
        "training_principle": (
            "Finetune for behavior, discipline, and tool use; use retrieval for fast-moving facts; "
            "promote only through explicit benchmark and governance gates."
        ),
        "model_strategy": {
            "base_path": "open_weight_primary",
            "adaptation_order": [
                "supervised_finetuning",
                "preference_optimization",
                "tool_use_alignment",
                "retrieval_and_memory_hardening",
            ],
            "scratch_pretraining_policy": "Only justified after open-weight adaptation saturates on target benchmark families.",
        },
        "dataset_families": [
            {
                "family": "repository_native_qa",
                "purpose": "Teach canonical answers tied to repository sources and gate labels.",
                "source_surfaces": [
                    str(REPO_ROOT / "STATUS.md"),
                    str(REPO_ROOT / "FALLIBILITY.md"),
                    str(REPO_ROOT / "5-GOVERNANCE" / "SEPARATION.md"),
                    str(PRODUCT_ROOT / "README.md"),
                    str(REPO_ROOT / "hf-spaces" / "um-knowledge-dataset" / "README.md"),
                ],
            },
            {
                "family": "governance_decision_traces",
                "purpose": "Teach Merlin to preserve separation boundaries, escalation policy, and privileged-action discipline.",
                "source_surfaces": [
                    str(PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_identity.py"),
                    str(PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_sentinel.py"),
                    str(PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_program.py"),
                ],
            },
            {
                "family": "benchmark_contract_exemplars",
                "purpose": "Teach the answer contract, provenance kinds, and gate visibility needed for promotion gates.",
                "source_surfaces": [
                    str(PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_benchmark.py"),
                    str(PRODUCT_ROOT / "tools" / "run_merlin_stage_a_benchmarks.py"),
                ],
            },
            {
                "family": "tool_call_success_failure_pairs",
                "purpose": "Teach precise tool choice, schema-aware invocation, and safe orchestration behavior.",
                "source_surfaces": [
                    str(PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_tools.py"),
                    str(PRODUCT_ROOT / "ox_navigator" / "app" / "server.py"),
                ],
            },
            {
                "family": "external_open_science_augmentation",
                "purpose": "Expand beyond repository-native scope without diluting Merlin's grounded identity.",
                "source_surfaces": ["getMerlinOpenScienceRegistry"],
            },
        ],
        "split_policy": {
            "train": "repository-native QA, tool traces, and mentorship deposits with deduplication",
            "dev": "high-impact boundary cases and adversarial counterexamples",
            "test": "promotion-gate benchmarks, refusal probes, and held-out provenance audits",
            "hard_rule": "No overlap between promotion benchmarks and supervised answer targets when measuring readiness.",
        },
        "curriculum": [
            {"stage": 1, "name": "grounded_repository_mastery", "goal": "Canonical answers with typed provenance."},
            {"stage": 2, "name": "boundary_and_refusal_discipline", "goal": "Stable governance and safety behavior."},
            {"stage": 3, "name": "tool_and_memory_alignment", "goal": "Correct tool selection, recall, and replayability."},
            {"stage": 4, "name": "scientific_open_science_expansion", "goal": "Controlled ingestion of external scientific corpora."},
            {"stage": 5, "name": "competitive_replacement_gates", "goal": "Sustained quality, energy, and reliability wins."},
        ],
        "seed_instruction_corpus": seed_examples,
        "seed_statistics": {
            "total_examples": len(seed_examples),
            "track_counts": track_counts,
        },
        "active_training_surfaces": {
            "baseline_plan": "getMerlinTrainingPlan",
            "full_architecture": "getMerlinTrainingArchitecture",
            "dataset_bundle": "getMerlinTrainingDataset",
            "mlflow_manifests": "getMerlinMLflowManifests",
            "artifact_bundle": "getMerlinTrainingArtifacts",
        },
    }


def _dataset_split(record_id: str, track: str) -> str:
    if track == "adversarial_counterexamples":
        return "test"
    digest = hashlib.sha256(f"{track}:{record_id}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 100
    if bucket < 70:
        return "train"
    if bucket < 85:
        return "dev"
    return "test"


def _build_compiled_insight_records(compiled_insights: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    records: list[dict[str, Any]] = []
    benchmark_fixtures: dict[str, list[dict[str, Any]]] = {
        "stage_b_sovereign_takeover": [],
        "stage_c_capability_expansion": [],
    }
    for item in list(compiled_insights or []):
        fact = str(item.get("fact", "")).strip()
        if not fact:
            continue
        kind = str(item.get("kind", "operational_heuristic"))
        split = _dataset_split(str(item.get("insight_id", "")) or fact, "compiled_insights")
        status = str(item.get("status", ""))
        proof_verdict = str(item.get("proof_verdict", "not_applicable"))
        required_gates = ["GOVERNANCE"]
        if status == "[CONTRADICTION_FLAGGED]":
            required_gates.append("ARCHITECTURE_LIMIT")
        if status == "[PROOF_REVIEW_REQUIRED]" or proof_verdict in {"needs_steward_review", "rejected"}:
            required_gates.append("OPEN_GAP")
        records.append({
            "record_id": f"compiled-{item.get('insight_id', '')}",
            "split": split,
            "task_family": "compiled_insights",
            "instruction": f"Retained insight ({kind}): {fact}",
            "response_target": {
                "status": status,
                "proof_verdict": proof_verdict,
                "contradictions": list(item.get("contradictions") or []),
            },
            "target_contract": {
                "requires_epistemic_tag": True,
                "requires_contradiction_check": True,
            },
            "supervision_mode": "compile_time_ingestion",
            "required_gates": required_gates,
            "provenance_sources": ["merlin_compiled_insight_store"],
            "format_version": "merlin_training_jsonl_v1",
        })
        if kind in {"falsification_lead", "structural_constraint"}:
            benchmark_fixtures["stage_b_sovereign_takeover"].append({
                "fixture_id": f"stage_b_fixture_{item.get('insight_id', '')}",
                "source_insight_id": str(item.get("insight_id", "")),
                "kind": kind,
                "prompt": fact,
            })
        if kind in {"theorem_candidate", "operational_heuristic"}:
            benchmark_fixtures["stage_c_capability_expansion"].append({
                "fixture_id": f"stage_c_fixture_{item.get('insight_id', '')}",
                "source_insight_id": str(item.get("insight_id", "")),
                "kind": kind,
                "prompt": fact,
            })
    return records, benchmark_fixtures


def build_training_dataset_bundle(
    limit: int | None = None,
    *,
    compiled_insights: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from .merlin_benchmark import get_benchmark_corpus

    architecture = get_training_architecture(limit=limit)
    seed_examples = list(architecture.get("seed_instruction_corpus") or [])
    splits: dict[str, list[dict[str, Any]]] = {"train": [], "dev": [], "test": []}
    for example in seed_examples:
        track = str(example.get("track", "unknown"))
        split = _dataset_split(str(example.get("id", "")), track)
        record = {
            "record_id": str(example.get("id", "")),
            "split": split,
            "task_family": track,
            "instruction": str(example.get("prompt", "")),
            "response_target": example.get("target"),
            "target_contract": example.get("target_contract"),
            "supervision_mode": str(example.get("supervision_mode", "unspecified")),
            "required_gates": list(example.get("required_gates") or []),
            "provenance_sources": list(example.get("provenance_sources") or []),
            "format_version": "merlin_training_jsonl_v1",
        }
        splits[split].append(record)

    benchmark_payload = get_benchmark_corpus("all")
    if benchmark_payload.get("ok") is False:
        return {
            "ok": False,
            "error": benchmark_payload.get("error", "Unable to build benchmark corpora."),
            "allowed_stages": list(benchmark_payload.get("allowed_stages") or []),
        }
    benchmark_records: dict[str, list[dict[str, Any]]] = {}
    corpora = dict(benchmark_payload.get("corpora") or {})
    for stage_name, payload in corpora.items():
        benchmark_records[stage_name] = []
        for benchmark in list(payload.get("benchmarks") or []):
            benchmark_records[stage_name].append(
                {
                    "benchmark_id": str(benchmark.get("id", "")),
                    "stage": stage_name,
                    "track": str(benchmark.get("track", "")),
                    "query": str(benchmark.get("query", "")),
                    "keywords": list(benchmark.get("keywords") or []),
                    "required_gates": list(benchmark.get("required_gates") or []),
                    "required_contract_sections": list(benchmark.get("required_contract_sections") or []),
                    "required_provenance_kinds": list(benchmark.get("required_provenance_kinds") or []),
                    "review_focus": list(benchmark.get("review_focus") or []),
                    "benchmark_mode": str(benchmark.get("benchmark_mode") or "single_turn"),
                    "setup_turns": list(benchmark.get("setup_turns") or []),
                    "format_version": "merlin_benchmark_jsonl_v1",
                }
            )

    compiled_records, compiled_fixtures = _build_compiled_insight_records(compiled_insights)
    for record in compiled_records:
        splits[record["split"]].append(record)
    benchmark_records["stage_b_sovereign_takeover"].extend(compiled_fixtures["stage_b_sovereign_takeover"])
    benchmark_records["stage_c_capability_expansion"].extend(compiled_fixtures["stage_c_capability_expansion"])

    split_counts = {name: len(items) for name, items in splits.items()}
    benchmark_counts = {name: len(items) for name, items in benchmark_records.items()}
    return {
        "ok": True,
        "dataset": {
            "generated_at": _utcnow(),
            "training_architecture": architecture,
            "splits": splits,
            "benchmark_corpora": benchmark_records,
            "counts": {
                "training_records": split_counts,
                "benchmark_records": benchmark_counts,
                "total_training_records": sum(split_counts.values()),
                "total_benchmark_records": sum(benchmark_counts.values()),
                "compile_time_insight_records": len(compiled_records),
            },
            "schema": {
                "training_fields": [
                    "record_id",
                    "split",
                    "task_family",
                    "instruction",
                    "response_target",
                    "target_contract",
                    "supervision_mode",
                    "required_gates",
                    "provenance_sources",
                    "format_version",
                ],
                "benchmark_fields": [
                    "benchmark_id",
                    "stage",
                    "track",
                    "query",
                    "keywords",
                    "required_gates",
                    "required_contract_sections",
                    "required_provenance_kinds",
                    "review_focus",
                    "benchmark_mode",
                    "setup_turns",
                    "format_version",
                ],
            },
            "compile_time_memory": {
                "source": "MerlinSession.compiled_insights",
                "record_count": len(compiled_records),
                "stage_b_fixture_count": len(compiled_fixtures["stage_b_sovereign_takeover"]),
                "stage_c_fixture_count": len(compiled_fixtures["stage_c_capability_expansion"]),
            },
        },
    }


def get_mlflow_experiment_manifests(
    limit: int | None = None,
    *,
    compiled_insights: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    dataset_bundle = build_training_dataset_bundle(limit=limit, compiled_insights=compiled_insights)
    if dataset_bundle.get("ok") is False:
        return {
            "generated_at": _utcnow(),
            "ok": False,
            "error": dataset_bundle.get("error", "Unable to build dataset bundle for MLflow manifests."),
        }
    dataset_counts = dict(((dataset_bundle.get("dataset") or {}).get("counts") or {}).get("training_records") or {})
    benchmark_counts = dict(((dataset_bundle.get("dataset") or {}).get("counts") or {}).get("benchmark_records") or {})
    resolved_limit = 12 if limit is None else max(0, int(limit))
    python_executable = sys.executable or "python3"
    def _shell_command(*parts: str) -> str:
        return " ".join(shlex.quote(str(part)) for part in parts)
    training_jsonl_command = (
        _shell_command(
            python_executable,
            "12-AZ-IP/20-merlin-navigator/tools/export_merlin_training_jsonl.py",
            "--limit",
            str(resolved_limit),
            "--output-dir",
            "/tmp/merlin-training-jsonl",
        )
    )
    mlflow_manifest_command = (
        _shell_command(
            python_executable,
            "12-AZ-IP/20-merlin-navigator/tools/export_merlin_mlflow_manifests.py",
            "--limit",
            str(resolved_limit),
            "--output-dir",
            "/tmp/merlin-mlflow",
        )
    )
    training_artifact_command = (
        _shell_command(
            python_executable,
            "12-AZ-IP/20-merlin-navigator/tools/export_merlin_training_artifacts.py",
            "--limit",
            str(resolved_limit),
            "--output",
            "/tmp/merlin-training-artifacts.json",
        )
    )
    stage_a_artifact_command = (
        _shell_command(
            python_executable,
            "12-AZ-IP/20-merlin-navigator/tools/export_merlin_stage_a_artifacts.py",
            "--limit",
            "3",
            "--output",
            "/tmp/merlin-stage-a-artifacts.json",
        )
    )
    def _mlflow_runner_command(experiment: str, output: str) -> str:
        return _shell_command(
            python_executable,
            "12-AZ-IP/20-merlin-navigator/tools/run_merlin_mlflow_experiment.py",
            "--experiment",
            experiment,
            "--limit",
            str(resolved_limit),
            "--output",
            output,
        )
    return {
        "ok": True,
        "generated_at": _utcnow(),
        "manifests": [
            {
                "experiment_name": "merlin_sft_repository_mastery",
                "objective": "Train Merlin on repository-native QA, tool traces, and benchmark contracts.",
                "tracking_uri_env": "MLFLOW_TRACKING_URI",
                "working_directory": str(REPO_ROOT),
                "tags": {
                    "program": "merlin_all_hands_maximum_effort",
                    "phase": "supervised_finetuning",
                    "mission_profile": "repository_assistant+scientific_reasoning+autonomous_research",
                },
                "datasets": {
                    "train_split_records": dataset_counts.get("train", 0),
                    "dev_split_records": dataset_counts.get("dev", 0),
                    "test_split_records": dataset_counts.get("test", 0),
                    "compile_time_insight_records": int(((dataset_bundle.get("dataset") or {}).get("counts") or {}).get("compile_time_insight_records", 0)),
                },
                "params": {
                    "base_model_policy": "open_weight_primary",
                    "sft_curriculum_stages": [1, 2, 3],
                    "benchmark_holdout_stages": ["stage_b_sovereign_takeover", "stage_c_capability_expansion"],
                },
                "metrics": [
                    "validation_contract_pass_rate",
                    "typed_provenance_completeness",
                    "boundary_preservation_rate",
                    "tool_selection_precision",
                ],
                "entry_command": _mlflow_runner_command(
                    "merlin_sft_repository_mastery",
                    "/tmp/merlin-sft-receipt.json",
                ),
                "prerequisite_commands": [
                    training_jsonl_command,
                ],
                "artifacts": [
                    "/tmp/merlin-sft-receipt.json",
                ],
                "prerequisite_artifacts": [
                    "/tmp/merlin-training-jsonl/train.jsonl",
                    "/tmp/merlin-training-jsonl/dev.jsonl",
                    "/tmp/merlin-training-jsonl/test.jsonl",
                    "/tmp/merlin-training-jsonl/dataset_manifest.json",
                ],
            },
            {
                "experiment_name": "merlin_dpo_boundary_discipline",
                "objective": "Optimize preference behavior for uncertainty discipline, refusal correctness, and boundary honesty.",
                "tracking_uri_env": "MLFLOW_TRACKING_URI",
                "working_directory": str(REPO_ROOT),
                "tags": {
                    "program": "merlin_all_hands_maximum_effort",
                    "phase": "preference_optimization",
                },
                "datasets": {
                    "stage_c_eval_records": benchmark_counts.get("stage_c_capability_expansion", 0),
                    "stage_b_boundary_eval_records": benchmark_counts.get("stage_b_sovereign_takeover", 0),
                },
                "params": {
                    "preference_targets": [
                        "uncertainty_discipline",
                        "refusal_correctness",
                        "governance_boundary_preservation",
                    ],
                },
                "metrics": [
                    "refusal_precision",
                    "prompt_injection_resistance",
                    "open_gap_visibility",
                ],
                "entry_command": _mlflow_runner_command(
                    "merlin_dpo_boundary_discipline",
                    "/tmp/merlin-dpo-eval-receipt.json",
                ),
                "prerequisite_commands": [
                    training_jsonl_command,
                    mlflow_manifest_command,
                ],
                "artifacts": [
                    "/tmp/merlin-dpo-eval-receipt.json",
                ],
                "prerequisite_artifacts": [
                    "/tmp/merlin-mlflow/mlflow_manifests.json",
                    "/tmp/merlin-training-jsonl/benchmarks/stage_b_sovereign_takeover.jsonl",
                    "/tmp/merlin-training-jsonl/benchmarks/stage_c_capability_expansion.jsonl",
                ],
            },
            {
                "experiment_name": "merlin_stage_b_shadow_eval",
                "objective": "Run Stage B selected-domain primary-routing evaluations before wider takeover.",
                "tracking_uri_env": "MLFLOW_TRACKING_URI",
                "working_directory": str(REPO_ROOT),
                "tags": {
                    "program": "merlin_all_hands_maximum_effort",
                    "phase": "stage_b_sovereign_takeover",
                },
                "datasets": {"stage_b_records": benchmark_counts.get("stage_b_sovereign_takeover", 0)},
                "params": {
                    "required_clean_windows": 3,
                    "focus_tracks": ["long_context_synthesis", "memory_recall", "policy_stability"],
                },
                "metrics": [
                    "stage_b_pass_rate",
                    "memory_recall_accuracy",
                    "privileged_action_escalation_correctness",
                    "energy_per_successful_task",
                ],
                "entry_command": _mlflow_runner_command(
                    "merlin_stage_b_shadow_eval",
                    "/tmp/merlin-stage-b-receipts.json",
                ),
                "prerequisite_commands": [
                    training_jsonl_command,
                    _shell_command(
                        python_executable,
                        "12-AZ-IP/20-merlin-navigator/tools/run_merlin_stage_a_benchmarks.py",
                        "--json",
                    ),
                    stage_a_artifact_command,
                ],
                "artifacts": [
                    "/tmp/merlin-stage-b-receipts.json",
                ],
                "prerequisite_artifacts": [
                    "/tmp/merlin-training-jsonl/benchmarks/stage_b_sovereign_takeover.jsonl",
                    "/tmp/merlin-stage-a-artifacts.json",
                ],
            },
            {
                "experiment_name": "merlin_stage_c_agentic_eval",
                "objective": "Evaluate deeper orchestration, provenance auditing, and autonomous research readiness.",
                "tracking_uri_env": "MLFLOW_TRACKING_URI",
                "working_directory": str(REPO_ROOT),
                "tags": {
                    "program": "merlin_all_hands_maximum_effort",
                    "phase": "stage_c_capability_expansion",
                },
                "datasets": {"stage_c_records": benchmark_counts.get("stage_c_capability_expansion", 0)},
                "params": {
                    "risk_mode": "fail_closed",
                    "focus_tracks": ["orchestration_depth", "provenance_completeness", "autonomous_research"],
                },
                "metrics": [
                    "orchestration_success_rate",
                    "typed_provenance_completion_rate",
                    "research_triage_correctness",
                    "high_severity_policy_violations",
                ],
                "entry_command": _mlflow_runner_command(
                    "merlin_stage_c_agentic_eval",
                    "/tmp/merlin-stage-c-receipts.json",
                ),
                "prerequisite_commands": [
                    training_jsonl_command,
                    training_artifact_command,
                ],
                "artifacts": [
                    "/tmp/merlin-stage-c-receipts.json",
                ],
                "prerequisite_artifacts": [
                    "/tmp/merlin-training-jsonl/benchmarks/stage_c_capability_expansion.jsonl",
                    "/tmp/merlin-training-artifacts.json",
                ],
            },
        ],
        "mlflow_contract": {
            "experiment_required_fields": [
                "experiment_name",
                "objective",
                "tracking_uri_env",
                "working_directory",
                "tags",
                "params",
                "metrics",
                "entry_command",
                "artifacts",
            ],
            "promotion_policy": "Merlin promotion remains governed by control-tower decisions, not MLflow logging alone.",
        },
    }


def get_competitive_benchmark_plan() -> dict[str, Any]:
    from .merlin_benchmark import get_benchmark_corpus, get_multi_stage_benchmark_plan, get_stage_a_benchmark_corpus

    return {
        "objective": "Benchmark Merlin competitively against incumbent and external-class expectations before broader promotion.",
        "internal_gate_stack": {
            "stage_a": get_stage_a_benchmark_corpus(),
            "multi_stage": get_multi_stage_benchmark_plan(),
            "corpora": get_benchmark_corpus("all"),
        },
        "competitive_families": [
            {
                "family": "repository_grounding",
                "must_measure": ["citation_faithfulness", "gate_visibility", "historical_context_retrieval"],
            },
            {
                "family": "scientific_reasoning",
                "must_measure": ["uncertainty_discipline", "cross-source synthesis", "falsification_awareness"],
            },
            {
                "family": "agentic_tool_use",
                "must_measure": ["tool_selection_precision", "schema_compliance", "replayability"],
            },
            {
                "family": "autonomous_research",
                "must_measure": ["hypothesis_generation", "source_triage", "risk_escalation_correctness"],
            },
            {
                "family": "safety_and_governance",
                "must_measure": ["refusal_correctness", "boundary_preservation", "privileged_action_control"],
            },
        ],
        "promotion_metrics": [
            "success_rate_parity_or_better",
            "mean_quality_delta_nonnegative",
            "energy_per_successful_task_lower_than_incumbent",
            "zero_high_severity_policy_violations",
            "stable_clean_windows_over_time",
        ],
    }


def _coerce_frontier_limit(value: Any, default: int = 3) -> int:
    try:
        parsed = int(value) if value is not None else int(default)
    except (TypeError, ValueError):
        return max(1, int(default))
    return parsed if parsed > 0 else max(1, int(default))


def get_frontier_readiness_packet(limit: int | None = 3) -> dict[str, Any]:
    from .merlin_benchmark import build_merlin_control_tower, get_multi_stage_benchmark_plan

    resolved_limit = _coerce_frontier_limit(limit, default=3)
    sync = run_sync_checks()
    control_tower = build_merlin_control_tower(limit=resolved_limit)
    benchmark_plan = get_multi_stage_benchmark_plan()
    training = get_training_architecture(limit=resolved_limit)
    runtime = get_mythos_astra_contract()
    router = get_router_policy()

    promotion_blockers = [
        {
            "id": "sync_checks_green",
            "pass": bool(sync.get("ok")),
            "reason": "Canonical source and endpoint sync checks must pass before promotion.",
        },
        {
            "id": "stage_a_empirical_gate",
            "pass": bool(control_tower.get("readiness", {}).get("packet", {}).get("empirical_gate", {}).get("gate_pass")),
            "reason": "Stage A head-to-head empirical gate must pass with comparable receipts.",
        },
        {
            "id": "longitudinal_acceptance",
            "pass": bool(control_tower.get("longitudinal", {}).get("pass")),
            "reason": "Non-overlapping clean-window longitudinal acceptance must pass.",
        },
        {
            "id": "policy_violation_budget",
            "pass": int(control_tower.get("readiness", {}).get("packet", {}).get("empirical_gate", {}).get("metrics", {}).get("high_severity_policy_violations_merlin", 1)) == 0,
            "reason": "Any high-severity policy violation blocks promotion.",
        },
        {
            "id": "typed_provenance_contract",
            "pass": "typed_provenance_and_gate_badges" in runtime.get("capability_contract", {}).get("required_surfaces", []),
            "reason": "Typed provenance and gate badges must remain mandatory in runtime contract.",
        },
        {
            "id": "sovereign_default_policy",
            "pass": router.get("default_provider") == "sovereign_local" and router.get("gates", {}).get("primary_requires_fully_open_science") is True,
            "reason": "Sovereign local runtime remains primary with open-science policy guardrails.",
        },
    ]

    return {
        "generated_at": _utcnow(),
        "sovereign_primary": router.get("default_provider") == "sovereign_local",
        "openrouter_fallback_only": router.get("compat_mode") == "compatibility_only",
        "sync_checks": sync,
        "control_tower": control_tower,
        "multi_stage_plan": benchmark_plan,
        "training_seed_examples": training.get("seed_statistics", {}),
        "promotion_blockers": promotion_blockers,
        "promotion_blockers_all_clear": all(item["pass"] for item in promotion_blockers),
        "policy": "Fail closed: promotion blocked unless every blocker passes.",
    }


def build_training_artifact_bundle(
    limit: int | None = None,
    *,
    compiled_insights: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from .merlin_benchmark import build_stage_a_artifact_bundle

    training_architecture = get_training_architecture(limit=limit)
    dataset_bundle = build_training_dataset_bundle(limit=limit, compiled_insights=compiled_insights)
    if dataset_bundle.get("ok") is False:
        return {
            "ok": False,
            "error": dataset_bundle.get("error", "Unable to build training dataset bundle."),
        }
    stage_a_limit = limit if limit is None else max(0, int(limit))
    return {
        "ok": True,
        "artifact_bundle": {
            "generated_at": _utcnow(),
            "training_architecture": training_architecture,
            "training_dataset": dataset_bundle["dataset"],
            "mlflow_manifests": get_mlflow_experiment_manifests(limit=limit, compiled_insights=compiled_insights),
            "competitive_benchmark_plan": get_competitive_benchmark_plan(),
            "open_science_registry": get_open_science_resource_registry(),
            "stage_a_baseline": build_stage_a_artifact_bundle(limit=stage_a_limit),
            "artifact_policy": {
                "promotion_rule": "Training artifacts inform promotion, but do not replace empirical benchmark gates.",
                "primary_store": "repository_governed_json_bundle",
                "external_distribution_candidate": "hugging_face_datasets",
            },
        },
    }


def get_energy_optimization_track() -> dict[str, Any]:
    return {
        "optimization_levers": [
            "quantization",
            "cache_reuse",
            "batching",
            "prompt_compaction",
            "adaptive_context_loading",
            "dynamic_depth_reasoning",
        ],
        "guardrails": [
            "no quality regression hidden by lower energy",
            "energy measured per successful task, not per request",
            "confidence-triggered deep pass only when needed",
        ],
        "regression_gate": "Block rollout if energy improves but quality/safety drops outside tolerance.",
    }


def get_backend_expansion_policy() -> dict[str, Any]:
    return {
        "api_targets": ["/api/agentToolkit", "/api/agentInvoke", "/api/agentOrchestrate"],
        "evolution": "Move from read-mostly to tiered capability classes under policy gates.",
        "required_controls": [
            "typed_tool_schemas",
            "tool_risk_levels",
            "hard_stop_conditions",
            "human_gate_requirements_for_high_risk_actions",
            "compatibility_shim_retention_during_migration",
            "workspace_audit_logs_for_all_adaptive_interface_adjustments",
        ],
    }


def get_governance_integration_policy() -> dict[str, Any]:
    return {
        "principle": "Use Pentad reasoning primitives while preserving explicit SEPARATION boundary.",
        "validation_suites": [
            "decision_consistency",
            "legitimacy_gate_compliance",
            "intervention_safety_checks",
        ],
        "required_output_fields": [
            "gate_badges",
            "boundary_statement",
            "provenance_sources",
            "confidence_statement",
        ],
    }


def get_reliability_security_plan() -> dict[str, Any]:
    return {
        "red_team_tracks": [
            "hallucination",
            "role_confusion",
            "prompt_injection",
            "malicious_tool_request",
            "policy_bypass",
        ],
        "operational_controls": [
            "deterministic_replay_packs",
            "strict_secret_handling",
            "connector_isolation",
            "zero_trust_external_call_posture",
            "sentinel_warn_then_reset_controls",
            "privileged_action_identity_verification",
        ],
    }


def get_rollout_plan() -> dict[str, Any]:
    return {
        "stages": [
            {
                "name": "stage_a_parity_capture",
                "goal": "Score Merlin outputs against incumbent path with no takeover.",
            },
            {
                "name": "stage_b_sovereign_takeover",
                "goal": "Merlin primary in selected domains with controlled fallback.",
            },
            {
                "name": "stage_c_capability_expansion",
                "goal": "Merlin default for most workloads; fallback by exception policy.",
            },
            {
                "name": "stage_d_replacement_gates",
                "goal": "Hold quality/energy/safety/governance gates over sustained runs.",
            },
            {
                "name": "stage_e_external_decommission",
                "goal": "Retire selected external dependencies once replacement gates pass.",
            },
        ],
        "rollback_requirement": "Every stage must include explicit rollback triggers and observability.",
    }


def get_operating_rhythm() -> dict[str, Any]:
    return {
        "weekly": "Model/perf/energy review with fixed decision log.",
        "monthly": "Capability gate review to approve additional replacement scope.",
        "quarterly": "Architecture review of model stack, infra cost, energy curves, and incidents.",
    }


def get_exit_criteria() -> dict[str, Any]:
    return {
        "required": [
            "quality_parity_or_better_on_benchmark_suite",
            "lower_energy_per_completed_task_than_incumbent",
            "stable_safety_and_governance_compliance_over_sustained_runs",
            "operational_reliability_under_load_and_adversarial_tests",
            "clear_rollback_path_with_observability",
        ]
    }


def get_program_doctrine() -> dict[str, Any]:
    return {
        "success_definition": [
            "reproducible",
            "auditable",
            "self_hostable",
            "governance_aligned",
            "higher_task_success_than_incumbent",
        ],
        "mandatory_disclosures": [
            "openness_tier",
            "boundary_statement",
            "uncertainty_statement",
            "provenance_sources",
        ],
        "openness_tiers": ["fully_open_science", "partially_open", "proprietary"],
        "non_negotiable": "Boundary labels and epistemic honesty cannot be relaxed by persona or routing mode.",
    }


def get_sovereignty_roadmap() -> dict[str, Any]:
    return {
        "checklist": [
            {"id": 1, "item": "Program doctrine", "mapped_to_blueprint": "charter + doctrine"},
            {"id": 2, "item": "Sovereign runtime routing", "mapped_to_blueprint": "model_strategy + router_policy"},
            {"id": 3, "item": "Persona governance", "mapped_to_blueprint": "training_and_adaptation + reliability_security"},
            {"id": 4, "item": "Governed back-room workspace", "mapped_to_blueprint": "backend_expansion + workspace_policy"},
            {"id": 5, "item": "Typed provenance completion", "mapped_to_blueprint": "knowledge_core"},
            {"id": 6, "item": "Open-science model admission", "mapped_to_blueprint": "model_admission_policy"},
            {"id": 7, "item": "Benchmark harness", "mapped_to_blueprint": "weights_and_measures"},
            {"id": 8, "item": "Reliability and abuse resistance", "mapped_to_blueprint": "reliability_security"},
            {"id": 9, "item": "12/37 cadence controls", "mapped_to_blueprint": "router_policy.cadence_policy"},
            {"id": 10, "item": "Stage A-E rollout", "mapped_to_blueprint": "rollout + exit_criteria"},
        ]
    }


def get_identity_and_trust_policy() -> dict[str, Any]:
    return get_identity_policy()


def get_sentinel_enforcement_policy() -> dict[str, Any]:
    return get_sentinel_policy()


def get_mythos_astra_contract() -> dict[str, Any]:
    return get_mythos_astra_runtime_contract()


def get_merlin_optimization_priorities() -> dict[str, Any]:
    return get_optimization_priorities()


def get_merlin_execution_graph() -> dict[str, Any]:
    return get_advanced_execution_graph()


def get_merlin_benchmark_suite() -> dict[str, Any]:
    return get_benchmark_suite()


def get_full_program_blueprint() -> dict[str, Any]:
    return {
        "generated_at": _utcnow(),
        "charter": get_program_charter(),
        "mentorship_sprint_charter": get_mentorship_sprint_charter(),
        "program_office": get_program_office(),
        "doctrine": get_program_doctrine(),
        "replacement_scope": get_replacement_scope(),
        "current_stack_baseline": get_current_stack_baseline(),
        "weights_and_measures": get_weights_and_measures(),
        "knowledge_core": get_knowledge_core_sources(),
        "model_strategy": get_model_strategy(),
        "router_policy": get_router_policy(),
        "model_admission_policy": get_model_admission_policy(),
        "training_and_adaptation": get_training_and_adaptation(),
        "training_architecture": get_training_architecture(limit=12),
        "training_dataset": build_training_dataset_bundle(limit=12),
        "mlflow_manifests": get_mlflow_experiment_manifests(limit=12),
        "open_science_registry": get_open_science_resource_registry(),
        "competitive_benchmark_plan": get_competitive_benchmark_plan(),
        "energy_optimization": get_energy_optimization_track(),
        "backend_expansion": get_backend_expansion_policy(),
        "workspace_policy": get_workspace_policy(),
        "workspace_state": get_workspace_state(),
        "governance_integration": get_governance_integration_policy(),
        "reliability_security": get_reliability_security_plan(),
        "identity_and_trust": get_identity_and_trust_policy(),
        "sentinel_policy": get_sentinel_enforcement_policy(),
        "mythos_astra_contract": get_mythos_astra_contract(),
        "optimization_priorities": get_merlin_optimization_priorities(),
        "execution_graph": get_merlin_execution_graph(),
        "benchmark_suite": get_merlin_benchmark_suite(),
        "faculty_matrix": get_specialized_model_faculty_matrix(),
        "knowledge_transfer_cycles": get_knowledge_transfer_cycles(),
        "library_and_study_assets": get_mentorship_library_and_study_assets(),
        "cross_model_exchange_protocol": get_cross_model_exchange_protocol(),
        "mentorship_completion_contract": get_mentorship_completion_contract(),
        "rollout": get_rollout_plan(),
        "operating_rhythm": get_operating_rhythm(),
        "exit_criteria": get_exit_criteria(),
        "sovereignty_roadmap": get_sovereignty_roadmap(),
        "sync_checks": run_sync_checks(),
        "frontier_readiness": get_frontier_readiness_packet(limit=3),
    }
