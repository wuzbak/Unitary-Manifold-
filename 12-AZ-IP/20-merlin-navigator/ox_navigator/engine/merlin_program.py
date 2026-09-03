# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Merlin replacement program artifacts and evaluation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
            "staged model-router exists but requires empirical benchmark tuning",
            "no formal benchmark corpus with side-by-side external comparisons",
            "sync drift checks are not enforced as recurring quality gates",
            "fully automated incumbent-vs-merlin batch runner is not yet attached to CI",
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
    ok = all(item["exists"] and item["readable"] for item in checks)
    endpoint_targets = [
        "/api/merlin",
        "/api/merlin/status",
        "/api/merlin/program",
        "/api/merlin/memory",
        "/api/merlin/telemetry",
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
    server_text = (PRODUCT_ROOT / "ox_navigator" / "app" / "server.py").read_text(encoding="utf-8")
    readme_text = (PRODUCT_ROOT / "README.md").read_text(encoding="utf-8")
    ui_text = (PRODUCT_ROOT / "ui" / "ox-navigator.js").read_text(encoding="utf-8")
    endpoint_checks = []
    for endpoint in endpoint_targets:
        present_everywhere = endpoint in server_text and endpoint in readme_text
        endpoint_checks.append({
            "endpoint": endpoint,
            "server": endpoint in server_text,
            "readme": endpoint in readme_text,
            "ok": present_everywhere,
        })
    gate_checks = []
    for gate in gate_targets:
        gate_checks.append({
            "gate": gate,
            "server": gate in server_text,
            "readme": gate in readme_text,
            "ui": gate in ui_text,
            "ok": gate in readme_text and gate in ui_text,
        })
    no_derived_drift = "DERIVED" not in ui_text
    consistency_ok = all(item["ok"] for item in endpoint_checks) and all(item["ok"] for item in gate_checks) and no_derived_drift
    return {
        "ok": bool(ok and consistency_ok),
        "checked_at": _utcnow(),
        "checks": checks,
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
        ],
        "adaptation_tracks": [
            "supervised_tuning_for_domain_coverage",
            "tool_use_alignment_for_agentToolkit_agentInvoke_agentOrchestrate",
            "preference_optimization_for_honesty_and_boundary_discipline",
        ],
        "quality_controls": [
            "deduplicate low-signal examples",
            "gate-label consistency checks",
            "manual steward sampling of high-impact outputs",
            "persona-governance checks cannot be overridden by style mode",
        ],
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
        "doctrine": get_program_doctrine(),
        "replacement_scope": get_replacement_scope(),
        "current_stack_baseline": get_current_stack_baseline(),
        "weights_and_measures": get_weights_and_measures(),
        "knowledge_core": get_knowledge_core_sources(),
        "model_strategy": get_model_strategy(),
        "router_policy": get_router_policy(),
        "model_admission_policy": get_model_admission_policy(),
        "training_and_adaptation": get_training_and_adaptation(),
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
        "rollout": get_rollout_plan(),
        "operating_rhythm": get_operating_rhythm(),
        "exit_criteria": get_exit_criteria(),
        "sovereignty_roadmap": get_sovereignty_roadmap(),
        "sync_checks": run_sync_checks(),
    }
