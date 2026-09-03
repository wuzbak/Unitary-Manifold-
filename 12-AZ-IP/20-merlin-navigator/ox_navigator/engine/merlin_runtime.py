# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Advanced Merlin runtime contracts for Mythos/Astra parity and beyond."""

from __future__ import annotations

from typing import Any


def get_optimization_priorities() -> dict[str, Any]:
    """Return ordered top-priority optimization tracks for Merlin."""
    return {
        "order": [
            {
                "rank": 1,
                "name": "memory_integrity_and_recall",
                "goal": "Eliminate amnesia-like failures with persistent, audited multi-tier memory.",
                "acceptance": [
                    "identity_policy_persistence",
                    "session_summary_recall_consistency",
                    "contradiction_detection_on_context_conflicts",
                ],
            },
            {
                "rank": 2,
                "name": "truthfulness_and_epistemic_calibration",
                "goal": "Raise factual precision while keeping uncertainty explicit and non-deceptive.",
                "acceptance": [
                    "mandatory_gate_label_coverage",
                    "not_found_path_correctness",
                    "citation_traceability_per_response",
                ],
            },
            {
                "rank": 3,
                "name": "safety_and_privileged_change_control",
                "goal": "Harden do-no-harm and identity-gated change control for Merlin modifications.",
                "acceptance": [
                    "sentinel_warn_then_reset_stability",
                    "privileged_request_refusal_when_unverified",
                    "zero_policy_bypass_on_known_attack_prompts",
                ],
            },
            {
                "rank": 4,
                "name": "orchestration_depth_and_tool_reliability",
                "goal": "Improve multi-step execution quality with bounded, auditable tool graphs.",
                "acceptance": [
                    "tool_chain_success_rate_target",
                    "deterministic_replay_pack_generation",
                    "safe_fallback_when_tools_conflict",
                ],
            },
            {
                "rank": 5,
                "name": "competitive_runtime_performance",
                "goal": "Achieve parity or better against Mythos/Astra class environments under constraints.",
                "acceptance": [
                    "quality_parity_or_better",
                    "latency_budget_compliance",
                    "energy_per_successful_task_improvement",
                ],
            },
        ],
        "selection_basis": "User-directed maximum-rigor roadmap, emphasizing memory, integrity, safety, orchestration, and competitiveness.",
    }


def get_mythos_astra_runtime_contract() -> dict[str, Any]:
    """Return Merlin runtime contract for Mythos/Astra environments."""
    return {
        "positioning": {
            "primary_mode": "competitive_agent_parity",
            "secondary_mode": "universal_cognitive_layer_wrapper",
            "controller_mode": "governance_orchestration_supervisor",
        },
        "capability_contract": {
            "required_surfaces": [
                "safe_query_interface",
                "policy_first_orchestration",
                "typed_provenance_and_gate_badges",
                "identity_trust_and_privilege_controls",
                "deterministic_refusal_for_harmful_requests",
            ],
            "compatibility": {
                "legacy_paths_retained": ["/api/ox", "/api/ox/status"],
                "merlin_paths_primary": [
                    "/api/merlin",
                    "/api/merlin/status",
                    "/api/merlin/program",
                    "/api/merlin/identity",
                    "/api/merlin/policy",
                ],
            },
        },
        "agent_graph": {
            "style": "parallel_specialist_mesh_with_final_audit",
            "lanes": [
                {"name": "research_lane", "role": "retrieve and align evidence"},
                {"name": "reasoning_lane", "role": "synthesize candidate answer"},
                {"name": "verification_lane", "role": "check claims and sources"},
                {"name": "safety_lane", "role": "enforce Sentinel and policy"},
                {"name": "governance_lane", "role": "boundary and privilege compliance"},
            ],
            "merge_rule": "Only emit final answer when verification+safety+governance lanes are all green.",
        },
        "environment_constraints": {
            "uncertain_identity_behavior": "normal_access_only_refuse_privileged_changes",
            "reset_policy": "session_clear_on_repeat_policy_violation_policy_memory_retained",
            "disallowed_domains": [
                "unconsensual_sexualization",
                "harm_planning",
                "weapons",
                "rights_violations",
                "illegal_activity_assistance",
            ],
        },
    }


def get_advanced_execution_graph() -> dict[str, Any]:
    """Return a machine-readable execution graph for max-rigor Merlin runs."""
    return {
        "graph_name": "merlin_max_rigor_execution",
        "nodes": [
            {"id": "N1", "name": "ingest_context", "type": "retrieval"},
            {"id": "N2", "name": "identity_gate", "type": "policy"},
            {"id": "N3", "name": "sentinel_scan", "type": "policy"},
            {"id": "N4", "name": "parallel_reasoning", "type": "orchestration"},
            {"id": "N5", "name": "source_verification", "type": "verification"},
            {"id": "N6", "name": "governance_boundary_check", "type": "verification"},
            {"id": "N7", "name": "contract_render", "type": "response"},
            {"id": "N8", "name": "postmortem_memory_write", "type": "memory"},
        ],
        "edges": [
            ["N1", "N2"],
            ["N2", "N3"],
            ["N3", "N4"],
            ["N4", "N5"],
            ["N5", "N6"],
            ["N6", "N7"],
            ["N7", "N8"],
        ],
        "hard_stops": ["identity_gate_fail_for_privileged", "sentinel_policy_block", "verification_conflict_unresolved"],
    }


def get_benchmark_suite() -> dict[str, Any]:
    """Return benchmark harness definition for competitive evaluation."""
    return {
        "tracks": [
            "memory_persistence",
            "factuality_and_citation",
            "refusal_correctness",
            "tool_orchestration_accuracy",
            "latency_cost_energy",
            "mythos_astra_parity",
        ],
        "rubric": [
            "task_success",
            "factual_precision",
            "epistemic_honesty",
            "safety_compliance",
            "governance_compliance",
            "energy_per_successful_task",
        ],
        "promotion_gate": "No promotion to broader autonomy unless all critical tracks pass with zero high-severity policy failures.",
    }
