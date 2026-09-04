# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Safe, tiered tool registry and orchestration helpers for Merlin."""

from __future__ import annotations

import os
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from .flashcard import get_categories, load_flashcards
from .interrogator import get_tension_map_data, search_kb
from .merlin_admission import evaluate_model_admission, get_model_admission_policy
from .merlin_benchmark import (
    build_merlin_control_tower,
    build_stage_a_artifact_bundle,
    build_stage_a_replacement_readiness,
    build_promotion_packet,
    evaluate_longitudinal_acceptance,
    evaluate_benchmark_response,
    evaluate_empirical_gate,
    get_multi_stage_benchmark_plan,
    get_stage_a_benchmark_corpus,
    run_stage_a_head_to_head_receipts_sync,
)
from .merlin_identity import authorize_privileged_request, verify_identity_signals
from .merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY, MerlinSession
from .merlin_program import (
    get_backend_expansion_policy,
    get_current_stack_baseline,
    get_energy_optimization_track,
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_exit_criteria,
    get_full_program_blueprint,
    get_governance_integration_policy,
    get_identity_and_trust_policy,
    get_knowledge_core_sources,
    get_mythos_astra_contract,
    get_model_strategy,
    get_operating_rhythm,
    get_program_office,
    get_program_charter,
    get_program_doctrine,
    get_reliability_security_plan,
    get_replacement_scope,
    get_rollout_plan,
    get_sovereignty_roadmap,
    get_sentinel_enforcement_policy,
    get_training_and_adaptation,
    get_weights_and_measures,
    run_sync_checks,
)
from .merlin_router import choose_runtime, get_router_policy
from .merlin_rag import (
    INTERROGATOR_ENTRIES,
    PILLAR_KNOWLEDGE,
    build_rag_context,
    build_status_response,
    lookup_kb,
)
from .merlin_workspace import get_workspace_policy, get_workspace_state

_LIMIT_SYNC_ARGS_SCHEMA = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer"},
        "sync_checks_ok": {"type": "boolean"},
    },
    "additionalProperties": False,
}

MERLIN_SESSION_SCHEMA = {
    "title": "MerlinSession",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "context_type": {
            "type": "string",
            "enum": ["chat", "interrogation", "flashcards", "geo-interpretation", "falsification"],
        },
        "messages_json": {"type": "array"},
        "deck_json": {"type": ["array", "null"]},
    },
    "required": ["title", "context_type", "messages_json"],
}


def _matches_schema_type(value: Any, schema_type: Any) -> bool:
    if isinstance(schema_type, list):
        return any(_matches_schema_type(value, item) for item in schema_type)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "null":
        return value is None
    return True


def _validate_args_schema(schema: dict[str, Any] | None, args: dict[str, Any]) -> str | None:
    if not schema:
        return None
    reserved_keys = {"human_gate_approved"}
    required = list(schema.get("required") or [])
    for key in required:
        if key not in args:
            return f"Missing required argument: {key}"
    props = dict(schema.get("properties") or {})
    for key, value in args.items():
        if key in reserved_keys:
            continue
        if key in props:
            expected = props[key].get("type")
            if expected and not _matches_schema_type(value, expected):
                return f"Invalid argument type for '{key}': expected {expected}"
        elif schema.get("additionalProperties") is False:
            return f"Unexpected argument: {key}"
    return None


def _tool_manifest() -> dict[str, Any]:
    functions = [
            {"name": "fetchRepoContext", "summary": "Return canonical live repo status", "domain": "functions"},
            {"name": "listPillars", "summary": "List representative pillar records", "domain": "functions"},
            {"name": "getPillar", "summary": "Return one pillar by id", "domain": "functions"},
            {"name": "searchKnowledgeBase", "summary": "Search canonical Merlin KB", "domain": "functions"},
            {"name": "searchInterrogator", "summary": "Search bundled interrogator KB", "domain": "functions"},
            {"name": "getTensionMap", "summary": "Return interrogator sigma/confidence points", "domain": "functions"},
            {"name": "loadFlashcards", "summary": "Return Merlin flashcard deck", "domain": "functions"},
            {"name": "getFlashcardCategories", "summary": "Return flashcard categories", "domain": "functions"},
            {"name": "getMerlinProgramCharter", "summary": "Return Merlin replacement program charter", "domain": "functions"},
            {"name": "getMerlinProgramDoctrine", "summary": "Return hard doctrine and success definition", "domain": "functions"},
            {"name": "getMerlinProgramOffice", "summary": "Return Merlin Program Office command structure and gate authority", "domain": "functions"},
            {"name": "getMerlinSovereigntyRoadmap", "summary": "Return implementation checklist mapped to blueprint", "domain": "functions"},
            {"name": "getMerlinReplacementScope", "summary": "Return in-scope and fallback policy boundaries", "domain": "functions"},
            {"name": "getMerlinStackBaseline", "summary": "Return baseline capabilities and replacement gaps", "domain": "functions"},
            {"name": "getMerlinWeightsAndMeasures", "summary": "Return scorecard axes and benchmark battery", "domain": "functions"},
            {"name": "getMerlinKnowledgeCore", "summary": "Return typed provenance source registry", "domain": "functions"},
            {"name": "runMerlinSyncChecks", "summary": "Run canonical source sync checks", "domain": "functions"},
            {"name": "getMerlinModelStrategy", "summary": "Return staged small/medium/heavy strategy", "domain": "functions"},
            {"name": "getMerlinRouterPolicy", "summary": "Return sovereign router and 12/37 cadence policy", "domain": "functions"},
            {"name": "previewMerlinRoute", "summary": "Preview lane/provider decision for a query", "domain": "functions"},
            {"name": "getMerlinModelAdmissionPolicy", "summary": "Return open-science model admission policy", "domain": "functions"},
            {"name": "evaluateMerlinModelAdmission", "summary": "Evaluate one model against admission policy", "domain": "functions"},
            {"name": "getMerlinTrainingPlan", "summary": "Return adaptation and training tracks", "domain": "functions"},
            {"name": "getMerlinEnergyPlan", "summary": "Return energy-first optimization controls", "domain": "functions"},
            {"name": "getMerlinBackendPolicy", "summary": "Return backend expansion policy controls", "domain": "functions"},
            {"name": "getMerlinWorkspacePolicy", "summary": "Return governed back-room workspace policy", "domain": "functions"},
            {"name": "getMerlinWorkspaceState", "summary": "Return back-room workspace state summary", "domain": "functions"},
            {"name": "getMerlinGovernancePolicy", "summary": "Return Pentad governance integration policy", "domain": "functions"},
            {"name": "getMerlinReliabilityPlan", "summary": "Return reliability and abuse-resistance controls", "domain": "functions"},
            {"name": "getMerlinRolloutPlan", "summary": "Return staged rollout and rollback policy", "domain": "functions"},
            {"name": "getMerlinOperatingRhythm", "summary": "Return weekly/monthly/quarterly cadence", "domain": "functions"},
            {"name": "getMerlinExitCriteria", "summary": "Return hard replacement exit criteria", "domain": "functions"},
            {"name": "getMerlinProgramBlueprint", "summary": "Return full integrated Merlin replacement blueprint", "domain": "functions"},
            {"name": "getMerlinIdentityPolicy", "summary": "Return canonical identity and trust policy", "domain": "functions"},
            {"name": "verifyMerlinIdentity", "summary": "Verify identity signals for privileged actions", "domain": "functions"},
            {"name": "authorizeMerlinPrivilege", "summary": "Authorize privileged Merlin modification requests", "domain": "functions"},
            {"name": "getMerlinSentinelPolicy", "summary": "Return Sentinel safety enforcement policy", "domain": "functions"},
            {"name": "getMerlinMythosAstraContract", "summary": "Return Merlin runtime contract for Mythos/Astra parity", "domain": "functions"},
            {"name": "getMerlinOptimizationPriorities", "summary": "Return ordered top optimization priorities", "domain": "functions"},
            {"name": "getMerlinExecutionGraph", "summary": "Return max-rigor execution graph", "domain": "functions"},
            {"name": "getMerlinBenchmarkSuite", "summary": "Return benchmark harness definition", "domain": "functions"},
            {"name": "getMerlinBenchmarkCorpus", "summary": "Return Stage A benchmark prompt corpus", "domain": "functions"},
            {"name": "getMerlinMultiStageBenchmarks", "summary": "Return multi-stage benchmark batteries and acceptance cadence", "domain": "functions"},
            {"name": "evaluateMerlinBenchmarkResponse", "summary": "Score one response against a Stage A benchmark", "domain": "functions"},
            {"name": "runMerlinStageAReceipts", "summary": "Run self-hosted Stage A receipt set", "domain": "functions"},
            {"name": "evaluateMerlinEmpiricalGate", "summary": "Evaluate sustained Merlin-vs-incumbent replacement gate", "domain": "functions"},
            {"name": "evaluateMerlinLongitudinalAcceptance", "summary": "Evaluate sustained clean-window promotion cadence over gate history", "domain": "functions"},
            {"name": "getMerlinPromotionPacket", "summary": "Return explicit replacement promotion packet", "domain": "functions"},
            {"name": "getMerlinReplacementReadiness", "summary": "Return concrete self-hosted replacement readiness packet", "domain": "functions"},
            {"name": "getMerlinStageAArtifacts", "summary": "Return exportable Stage A artifact bundle", "domain": "functions"},
            {"name": "getMerlinControlTower", "summary": "Return control tower readiness, drift alerts, trendlines, and deployment eligibility", "domain": "functions"},
            {"name": "getMerlinMemoryState", "summary": "Return Merlin multi-tier memory state", "domain": "functions"},
            {"name": "runMerlinMemoryAudit", "summary": "Audit which durable memories match a query", "domain": "functions"},
            {"name": "getMerlinTelemetrySummary", "summary": "Return measurable run summary for recent Merlin turns", "domain": "functions"},
        ]
    policy_overrides = {
        "getPillar": {
            "args_schema": {
                "type": "object",
                "properties": {"pillar_id": {"type": "integer"}},
                "required": ["pillar_id"],
                "additionalProperties": True,
            },
        },
        "searchKnowledgeBase": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
        "searchInterrogator": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
        "previewMerlinRoute": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["query"],
            },
        },
        "evaluateMerlinModelAdmission": {
            "args_schema": {"type": "object", "properties": {"model": {"type": "object"}}, "required": ["model"]},
            "risk_level": "medium",
        },
        "verifyMerlinIdentity": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "user_context": {"type": "string"},
                    "page_context": {"type": "string"},
                },
            },
            "risk_level": "medium",
        },
        "authorizeMerlinPrivilege": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "user_context": {"type": "string"},
                    "page_context": {"type": "string"},
                },
            },
            "risk_level": "high",
            "requires_human_gate": True,
        },
        "evaluateMerlinBenchmarkResponse": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "benchmark_id": {"type": "string"},
                    "response": {"type": "object"},
                },
                "required": ["benchmark_id", "response"],
            },
        },
        "evaluateMerlinLongitudinalAcceptance": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "gate_history": {"type": "array"},
                    "window_size": {"type": "integer"},
                    "min_clean_windows": {"type": "integer"},
                },
                "required": ["gate_history"],
            },
            "risk_level": "medium",
        },
        "runMerlinStageAReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
        },
        "evaluateMerlinEmpiricalGate": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "head_to_head_runs": {"type": "array"},
                    "min_runs": {"type": "integer"},
                    "max_quality_regressions": {"type": "integer"},
                },
                "required": ["head_to_head_runs"],
            },
            "risk_level": "medium",
        },
        "getMerlinPromotionPacket": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "head_to_head_runs": {"type": "array"},
                    "sync_checks_ok": {"type": "boolean"},
                },
                "additionalProperties": True,
            },
            "risk_level": "medium",
        },
        "getMerlinReplacementReadiness": {
            "args_schema": _LIMIT_SYNC_ARGS_SCHEMA,
            "risk_level": "medium",
        },
        "getMerlinStageAArtifacts": {
            "args_schema": _LIMIT_SYNC_ARGS_SCHEMA,
            "risk_level": "medium",
        },
        "getMerlinControlTower": {
            "args_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer"}},
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinMemoryAudit": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            "capability_class": "state_read",
        },
        "getMerlinMemoryState": {"capability_class": "state_read"},
        "getMerlinTelemetrySummary": {"capability_class": "state_read"},
    }
    enriched_functions = []
    for item in functions:
        enriched = {
            "capability_class": "read",
            "risk_level": "low",
            "requires_human_gate": False,
            "args_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            **item,
            **policy_overrides.get(item["name"], {}),
        }
        enriched_functions.append(enriched)
    return {
        "functions": enriched_functions,
        "integrations": [],
        "entities": [
            {
                "name": "MerlinSession",
                "summary": "Audited Merlin session with durable memory, contradictions, and telemetry.",
                "domain": "entities",
                "operations": ["schema", "state", "audit"],
            },
        ],
        "connectors": [
            {
                "name": "github",
                "summary": "Standalone compatibility summary only; no token exposure.",
                "domain": "connectors",
                "risk_level": "low",
            },
        ],
        "secrets": [
            {"name": "OPENROUTER_API_KEY", "domain": "secrets"},
            {"name": "BRAVE_API_KEY", "domain": "secrets"},
            {"name": "HF_API_TOKEN", "domain": "secrets"},
        ],
    }


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_limit(value: Any, default: int = 3) -> int:
    if value is None:
        return int(default)
    return int(value)


def _validate_args_schema(args: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, str]:
    properties = dict(schema.get("properties") or {})
    required = list(schema.get("required") or [])
    allow_extra = bool(schema.get("additionalProperties", False))
    reserved_keys = {"human_gate_approved"}
    filtered_args = {k: v for k, v in args.items() if k not in reserved_keys}
    for key in required:
        if key not in filtered_args:
            return False, f"Missing required argument: {key}"
    if not allow_extra:
        extra = sorted(set(filtered_args.keys()) - set(properties.keys()))
        if extra:
            return False, f"Unknown argument(s): {', '.join(extra)}"
    type_map = {
        "string": str,
        "boolean": bool,
        "object": dict,
        "array": list,
    }

    def _matches(expected_type: str, value: Any) -> bool:
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        py_type = type_map.get(expected_type)
        return isinstance(value, py_type) if py_type else True
    for key, spec in properties.items():
        if key not in filtered_args:
            continue
        expected = spec.get("type")
        if isinstance(expected, list):
            valid = any(_matches(str(t), filtered_args[key]) for t in expected)
        else:
            valid = _matches(str(expected), filtered_args[key]) if expected else True
        if not valid:
            return False, f"Invalid type for '{key}', expected {expected}"
    return True, ""


def _build_replay_artifact(*, tool: str, args: dict[str, Any], result: Any, ok: bool) -> dict[str, Any]:
    secret_markers = ("token", "secret", "key", "password", "credential")
    safe_args = {}
    for key, value in dict(args or {}).items():
        lower = str(key).lower()
        safe_args[key] = "***REDACTED***" if any(marker in lower for marker in secret_markers) else value
    replay = {
        "generated_at": _utcnow(),
        "tool": tool,
        "args": safe_args,
        "ok": ok,
        "result_excerpt": json.dumps(result, ensure_ascii=False)[:800] if result is not None else "",
    }
    replay_payload = json.dumps(replay, ensure_ascii=False, sort_keys=True)
    replay["digest_sha256"] = hashlib.sha256(replay_payload.encode("utf-8")).hexdigest()
    return replay


def fetch_repo_context() -> dict[str, Any]:
    return {"data": build_status_response()}


def list_pillars() -> dict[str, Any]:
    return {"data": {"pillars": PILLAR_KNOWLEDGE, "total": len(PILLAR_KNOWLEDGE)}}


def get_pillar(pillar_id: int) -> dict[str, Any]:
    for pillar in PILLAR_KNOWLEDGE:
        if int(pillar["id"]) == int(pillar_id):
            return {"data": pillar}
    return {"data": None, "error": f"Pillar {pillar_id} not found"}


def search_knowledge_base(query: str) -> dict[str, Any]:
    return {"data": {"match": lookup_kb(query), "context": build_rag_context(query)}}


def search_interrogator(query: str) -> dict[str, Any]:
    return {"data": {"results": search_kb(INTERROGATOR_ENTRIES, query)[:5]}}


def get_tension_map() -> dict[str, Any]:
    return {"data": {"points": get_tension_map_data(INTERROGATOR_ENTRIES)}}


def load_flashcards_tool() -> dict[str, Any]:
    cards = load_flashcards()
    return {"data": {"count": len(cards), "cards": cards}}


def get_flashcard_categories() -> dict[str, Any]:
    return {"data": {"categories": get_categories(load_flashcards())}}


_FUNCTIONS = {
    "fetchRepoContext": fetch_repo_context,
    "listPillars": list_pillars,
    "getPillar": lambda **args: get_pillar(int(args.get("pillar_id", args.get("id", 0)))),
    "searchKnowledgeBase": lambda **args: search_knowledge_base(str(args.get("query", ""))),
    "searchInterrogator": lambda **args: search_interrogator(str(args.get("query", ""))),
    "getTensionMap": lambda **args: get_tension_map(),
    "loadFlashcards": lambda **args: load_flashcards_tool(),
    "getFlashcardCategories": lambda **args: get_flashcard_categories(),
    "getMerlinProgramCharter": lambda **args: {"data": get_program_charter()},
    "getMerlinProgramDoctrine": lambda **args: {"data": get_program_doctrine()},
    "getMerlinProgramOffice": lambda **args: {"data": get_program_office()},
    "getMerlinSovereigntyRoadmap": lambda **args: {"data": get_sovereignty_roadmap()},
    "getMerlinReplacementScope": lambda **args: {"data": get_replacement_scope()},
    "getMerlinStackBaseline": lambda **args: {"data": get_current_stack_baseline()},
    "getMerlinWeightsAndMeasures": lambda **args: {"data": get_weights_and_measures()},
    "getMerlinKnowledgeCore": lambda **args: {"data": get_knowledge_core_sources()},
    "runMerlinSyncChecks": lambda **args: {"data": run_sync_checks()},
    "getMerlinModelStrategy": lambda **args: {"data": get_model_strategy()},
    "getMerlinRouterPolicy": lambda **args: {"data": get_router_policy()},
    "previewMerlinRoute": lambda **args: {"data": choose_runtime(str(args.get("query", "")), confidence=float(args.get("confidence", 0.7)))},
    "getMerlinModelAdmissionPolicy": lambda **args: {"data": get_model_admission_policy()},
    "evaluateMerlinModelAdmission": lambda **args: {"data": evaluate_model_admission(dict(args.get("model") or {}))},
    "getMerlinTrainingPlan": lambda **args: {"data": get_training_and_adaptation()},
    "getMerlinEnergyPlan": lambda **args: {"data": get_energy_optimization_track()},
    "getMerlinBackendPolicy": lambda **args: {"data": get_backend_expansion_policy()},
    "getMerlinWorkspacePolicy": lambda **args: {"data": get_workspace_policy()},
    "getMerlinWorkspaceState": lambda **args: {"data": get_workspace_state()},
    "getMerlinGovernancePolicy": lambda **args: {"data": get_governance_integration_policy()},
    "getMerlinReliabilityPlan": lambda **args: {"data": get_reliability_security_plan()},
    "getMerlinRolloutPlan": lambda **args: {"data": get_rollout_plan()},
    "getMerlinOperatingRhythm": lambda **args: {"data": get_operating_rhythm()},
    "getMerlinExitCriteria": lambda **args: {"data": get_exit_criteria()},
    "getMerlinProgramBlueprint": lambda **args: {"data": get_full_program_blueprint()},
    "getMerlinIdentityPolicy": lambda **args: {"data": get_identity_and_trust_policy()},
    "verifyMerlinIdentity": lambda **args: {"data": verify_identity_signals(
        str(args.get("query", "")),
        str(args.get("user_context", "")),
        str(args.get("page_context", "")),
    )},
    "authorizeMerlinPrivilege": lambda **args: {"data": authorize_privileged_request(
        str(args.get("query", "")),
        page_context=str(args.get("page_context", "")),
        user_context=str(args.get("user_context", "")),
    )},
    "getMerlinSentinelPolicy": lambda **args: {"data": get_sentinel_enforcement_policy()},
    "getMerlinMythosAstraContract": lambda **args: {"data": get_mythos_astra_contract()},
    "getMerlinOptimizationPriorities": lambda **args: {"data": get_merlin_optimization_priorities()},
    "getMerlinExecutionGraph": lambda **args: {"data": get_merlin_execution_graph()},
    "getMerlinBenchmarkSuite": lambda **args: {"data": get_merlin_benchmark_suite()},
    "getMerlinMultiStageBenchmarks": lambda **args: {"data": get_multi_stage_benchmark_plan()},
    "runMerlinStageAReceipts": lambda **args: {"data": run_stage_a_head_to_head_receipts_sync(limit=args.get("limit"))},
    "getMerlinReplacementReadiness": lambda **args: {"data": build_stage_a_replacement_readiness(
        limit=args.get("limit"),
        sync_checks_ok=args.get("sync_checks_ok"),
    )},
    "getMerlinStageAArtifacts": lambda **args: {"data": build_stage_a_artifact_bundle(
        limit=args.get("limit"),
        sync_checks_ok=args.get("sync_checks_ok"),
    )},
    "getMerlinControlTower": lambda **args: {"data": build_merlin_control_tower(limit=_coerce_limit(args.get("limit"), default=3))},
}


def get_toolkit_view(view: str = "index", *, domain: str | None = None, tool: str | None = None) -> dict[str, Any]:
    """Return one of the Merlin toolkit discovery views."""
    manifest = _tool_manifest()
    if view == "index":
        return {
            "view": "index",
            "functions": [f"{item['name']} — {item['summary']}" for item in manifest["functions"]],
            "integrations": [],
            "entities": [f"{item['name']} — {item['summary']}" for item in manifest["entities"]],
            "connectors": [f"{item['name']} — {item['summary']}" for item in manifest["connectors"]],
            "secrets": [item["name"] for item in manifest["secrets"]],
        }
    if view == "domain":
        selected = manifest.get(domain or "", [])
        return {"view": "domain", "domain": domain, "items": selected}
    if view == "tool":
        for group_name, items in manifest.items():
            for item in items:
                if item["name"] == tool:
                    return {"view": "tool", "tool": tool, "type": group_name[:-1], "detail": item}
        return {"view": "tool", "tool": tool, "error": "not found"}
    if view == "full":
        return {"view": "full", **manifest}
    if view == "state":
        state_session = MerlinSession()
        return {
            "view": "state",
            "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "repo": build_status_response(),
            "connectors": {
                "github": {
                    "authorized": bool(os.environ.get("GITHUB_TOKEN")),
                    "summary": "Standalone compatibility view only; no token is ever exposed.",
                },
            },
            "secrets": {
                "OPENROUTER_API_KEY": {
                    "available": bool(os.environ.get("OPENROUTER_API_KEY")),
                    "description": "OpenRouter access for compatibility-only fallback path.",
                },
                "BRAVE_API_KEY": {
                    "available": bool(os.environ.get("BRAVE_API_KEY")),
                    "description": "External literature alignment search.",
                },
                "HF_API_TOKEN": {
                    "available": bool(os.environ.get("HF_API_TOKEN")),
                    "description": "HF inference compatibility token.",
                },
            },
            "router": {
                "policy": get_router_policy(),
                "openrouter_compat_enabled": bool(os.environ.get("MERLIN_ENABLE_OPENROUTER_COMPAT")),
            },
            "memory": state_session.get_public_memory_state(),
            "telemetry": state_session.get_telemetry_summary(public=True),
            "entities": {
                "MerlinSession": {
                    "summary": "Audited multi-tier session memory with contradiction tracking and measurable run telemetry.",
                    "schema": MERLIN_SESSION_SCHEMA,
                    "sample_count": 0,
                    "samples": [],
                    "storage_keys": [MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY],
                },
            },
        }
    return {"view": view, "error": "unsupported view"}


def route_tool(tool: str, args: dict[str, Any] | None = None, *, session: MerlinSession | None = None) -> dict[str, Any]:
    """Route a Merlin tool call to a safe local capability."""
    args = dict(args or {})
    active_session = session if session is not None else MerlinSession()
    manifest = _tool_manifest()
    policy = next((item for item in manifest["functions"] if item["name"] == tool), None)
    if policy is None and tool.startswith("entity.MerlinSession."):
        op = tool.split(".")[-1]
        if op == "audit":
            policy = {"args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "additionalProperties": False}}
        elif op in {"schema", "state"}:
            policy = {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}}
    if policy is None and tool == "connector.github":
        policy = {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}}
    allowed_tools = {
        *(item["name"] for item in manifest["functions"]),
        "getMerlinBenchmarkCorpus",
        "evaluateMerlinBenchmarkResponse",
        "getMerlinMemoryState",
        "runMerlinMemoryAudit",
        "getMerlinTelemetrySummary",
        "connector.github",
    }
    started = time.perf_counter()
    tool_type = "unknown"
    ok = True
    error = ""
    result: Any = None
    try:
        if not (tool in allowed_tools or tool.startswith("entity.MerlinSession.")):
            ok = False
            error = f"Tool not allowlisted: {tool}"
            raise ValueError(error)
        if policy:
            schema_ok, schema_error = _validate_args_schema(args, dict(policy.get("args_schema") or {}))
            if not schema_ok:
                ok = False
                error = schema_error
                raise ValueError(schema_error)
            if bool(policy.get("requires_human_gate")) and not bool(args.get("human_gate_approved")):
                ok = False
                error = "Human gate approval required for this tool."
                raise ValueError(error)
        if tool in _FUNCTIONS:
            tool_type = "function"
            result = _FUNCTIONS[tool](**args)
        elif tool == "getMerlinBenchmarkCorpus":
            tool_type = "function"
            result = {"data": get_stage_a_benchmark_corpus()}
        elif tool == "evaluateMerlinBenchmarkResponse":
            tool_type = "function"
            result = {"data": evaluate_benchmark_response(str(args.get("benchmark_id", "")), dict(args.get("response") or {}))}
        elif tool == "evaluateMerlinEmpiricalGate":
            tool_type = "function"
            result = {"data": evaluate_empirical_gate(
                list(args.get("head_to_head_runs") or []),
                min_runs=int(args.get("min_runs", 12)),
                max_quality_regressions=int(args.get("max_quality_regressions", 0)),
            )}
        elif tool == "evaluateMerlinLongitudinalAcceptance":
            tool_type = "function"
            result = {"data": evaluate_longitudinal_acceptance(
                list(args.get("gate_history") or []),
                window_size=int(args.get("window_size", 4)),
                min_clean_windows=int(args.get("min_clean_windows", 3)),
            )}
        elif tool == "getMerlinPromotionPacket":
            tool_type = "function"
            sync_checks_ok = (
                bool(args.get("sync_checks_ok"))
                if "sync_checks_ok" in args
                else bool(run_sync_checks().get("ok"))
            )
            result = {"data": build_promotion_packet(
                head_to_head_runs=list(args.get("head_to_head_runs") or []),
                telemetry_summary=active_session.get_telemetry_summary(public=True),
                sync_checks_ok=sync_checks_ok,
            )}
        elif tool == "getMerlinMemoryState":
            tool_type = "function"
            result = {"data": active_session.get_public_memory_state()}
        elif tool == "runMerlinMemoryAudit":
            tool_type = "function"
            audit = active_session.audit_memory(str(args.get("query", "")))
            result = {"data": {
                "query": audit["query"],
                "matched_memory_count": audit["matched_memory_count"],
                "matched_scopes": audit["matched_scopes"],
            }}
        elif tool == "getMerlinTelemetrySummary":
            tool_type = "function"
            result = {"data": active_session.get_telemetry_summary(public=True)}
        elif tool.startswith("entity.MerlinSession."):
            tool_type = "entity"
            op = tool.split(".")[-1]
            if op == "schema":
                result = {"data": MERLIN_SESSION_SCHEMA}
            elif op == "state":
                result = {"data": active_session.get_public_memory_state()}
            elif op == "audit":
                query = str(args.get("query", "")).strip()
                if query:
                    audit = active_session.audit_memory(query)
                    result = {"data": {
                        "query": query,
                        "matched_memory_count": audit["matched_memory_count"],
                        "matched_scopes": audit["matched_scopes"],
                    }}
                else:
                    result = {
                        "data": {
                            "recent_memory_audits": active_session.get_memory_state()["recent_memory_audits"],
                            "contradiction_event_count": active_session.get_memory_state()["contradiction_event_count"],
                        },
                    }
            else:
                ok = False
                error = "Unsupported MerlinSession operation."
        elif tool == "connector.github":
            tool_type = "connector"
            result = {
                "authorized": bool(os.environ.get("GITHUB_TOKEN")),
                "type": "github",
                "connectionConfig": {"mode": "compatibility-summary-only"},
            }
        else:
            ok = False
            error = f"Unknown tool: {tool}"
    except Exception as exc:  # pragma: no cover
        ok = False
        error = str(exc)
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    replay = _build_replay_artifact(tool=tool, args=args, result=result, ok=ok)
    return {
        "ok": ok,
        "tool": tool,
        "type": tool_type,
        "result": result,
        "error": error,
        "policy": {
            "capability_class": (policy or {}).get("capability_class", "unknown"),
            "risk_level": (policy or {}).get("risk_level", "unknown"),
            "requires_human_gate": bool((policy or {}).get("requires_human_gate", False)),
        },
        "audit": {
            "args_keys": sorted(args.keys()),
            "duration_ms": duration_ms,
        },
        "replay_artifact": replay,
        "duration_ms": duration_ms,
    }


def get_path(obj: Any, path: str | None):
    """Resolve a dotted path into an object."""
    if not path:
        return obj
    current = obj
    for key in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(key)]
            except Exception:
                return None
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def orchestrate_steps(steps: list[dict[str, Any]], *, session: MerlinSession | None = None) -> dict[str, Any]:
    """Execute a bounded sequential Merlin tool chain."""
    if len(steps) > 10:
        raise ValueError("step cap exceeded (max 10)")
    if any(str(step.get("tool", "")).strip() == "authorizeMerlinPrivilege" for step in steps):
        raise ValueError("authorizeMerlinPrivilege is blocked in orchestration; use single-step invocation with explicit human gate.")
    started = time.perf_counter()
    results = []
    for index, step in enumerate(steps):
        tool = str(step.get("tool", ""))
        args = dict(step.get("args") or {})
        threading = step.get("input_from") or {}
        if threading:
            from_step = int(threading.get("step", -1))
            prior = results[from_step] if 0 <= from_step < len(results) else None
            if prior and prior.get("ok"):
                threaded = get_path(prior.get("result"), threading.get("path"))
                into = threading.get("into")
                template = threading.get("template")
                if into and template is not None:
                    args[into] = str(template).replace("{value}", "" if threaded is None else str(threaded))
                elif into:
                    args[into] = threaded
                elif isinstance(threaded, dict):
                    args.update(threaded)
                else:
                    args["_threaded"] = threaded
        result = route_tool(tool, args, session=session)
        result["step"] = index
        result["threading"] = threading
        results.append(result)
    total_duration_ms = round((time.perf_counter() - started) * 1000, 3)
    high_risk_steps = sum(1 for step in results if str((step.get("policy") or {}).get("risk_level")) == "high")
    replay = {
        "generated_at": _utcnow(),
        "step_count": len(results),
        "steps": [
            {
                "step": step.get("step"),
                "tool": step.get("tool"),
                "ok": step.get("ok"),
                "policy": step.get("policy"),
                "args_keys": (step.get("audit") or {}).get("args_keys", []),
                "threading": step.get("threading", {}),
                "duration_ms": step.get("duration_ms"),
                "replay_digest": ((step.get("replay_artifact") or {}).get("digest_sha256", "")),
            }
            for step in results
        ],
    }
    replay_payload = json.dumps(replay, ensure_ascii=False, sort_keys=True)
    replay["digest_sha256"] = hashlib.sha256(replay_payload.encode("utf-8")).hexdigest()
    return {
        "ok": all(step.get("ok") for step in results),
        "steps": results,
        "total_duration_ms": total_duration_ms,
        "audit_log_mode": "required",
        "human_gate_required": any((step.get("policy") or {}).get("requires_human_gate") for step in results),
        "policy_summary": {
            "high_risk_steps": high_risk_steps,
            "blocked_tools_in_orchestration": ["authorizeMerlinPrivilege"],
        },
        "replay_artifact": replay,
    }
