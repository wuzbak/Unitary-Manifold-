# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Safe, read-mostly tool registry and orchestration helpers for Merlin."""

from __future__ import annotations

import os
import time
from typing import Any

from .flashcard import get_categories, load_flashcards
from .interrogator import get_tension_map_data, search_kb
from .merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY
from .merlin_program import (
    get_backend_expansion_policy,
    get_current_stack_baseline,
    get_energy_optimization_track,
    get_exit_criteria,
    get_full_program_blueprint,
    get_governance_integration_policy,
    get_knowledge_core_sources,
    get_model_strategy,
    get_operating_rhythm,
    get_program_charter,
    get_reliability_security_plan,
    get_replacement_scope,
    get_rollout_plan,
    get_training_and_adaptation,
    get_weights_and_measures,
    run_sync_checks,
)
from .merlin_rag import (
    INTERROGATOR_ENTRIES,
    PILLAR_KNOWLEDGE,
    build_rag_context,
    build_status_response,
    lookup_kb,
)

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


def _tool_manifest() -> dict[str, Any]:
    return {
        "functions": [
            {"name": "fetchRepoContext", "summary": "Return canonical live repo status", "domain": "functions"},
            {"name": "listPillars", "summary": "List representative pillar records", "domain": "functions"},
            {"name": "getPillar", "summary": "Return one pillar by id", "domain": "functions"},
            {"name": "searchKnowledgeBase", "summary": "Search canonical Merlin KB", "domain": "functions"},
            {"name": "searchInterrogator", "summary": "Search bundled interrogator KB", "domain": "functions"},
            {"name": "getTensionMap", "summary": "Return interrogator sigma/confidence points", "domain": "functions"},
            {"name": "loadFlashcards", "summary": "Return Merlin flashcard deck", "domain": "functions"},
            {"name": "getFlashcardCategories", "summary": "Return flashcard categories", "domain": "functions"},
            {"name": "getMerlinProgramCharter", "summary": "Return Merlin replacement program charter", "domain": "functions"},
            {"name": "getMerlinReplacementScope", "summary": "Return in-scope and fallback policy boundaries", "domain": "functions"},
            {"name": "getMerlinStackBaseline", "summary": "Return baseline capabilities and replacement gaps", "domain": "functions"},
            {"name": "getMerlinWeightsAndMeasures", "summary": "Return scorecard axes and benchmark battery", "domain": "functions"},
            {"name": "getMerlinKnowledgeCore", "summary": "Return typed provenance source registry", "domain": "functions"},
            {"name": "runMerlinSyncChecks", "summary": "Run canonical source sync checks", "domain": "functions"},
            {"name": "getMerlinModelStrategy", "summary": "Return staged small/medium/heavy strategy", "domain": "functions"},
            {"name": "getMerlinTrainingPlan", "summary": "Return adaptation and training tracks", "domain": "functions"},
            {"name": "getMerlinEnergyPlan", "summary": "Return energy-first optimization controls", "domain": "functions"},
            {"name": "getMerlinBackendPolicy", "summary": "Return backend expansion policy controls", "domain": "functions"},
            {"name": "getMerlinGovernancePolicy", "summary": "Return Pentad governance integration policy", "domain": "functions"},
            {"name": "getMerlinReliabilityPlan", "summary": "Return reliability and abuse-resistance controls", "domain": "functions"},
            {"name": "getMerlinRolloutPlan", "summary": "Return staged rollout and rollback policy", "domain": "functions"},
            {"name": "getMerlinOperatingRhythm", "summary": "Return weekly/monthly/quarterly cadence", "domain": "functions"},
            {"name": "getMerlinExitCriteria", "summary": "Return hard replacement exit criteria", "domain": "functions"},
            {"name": "getMerlinProgramBlueprint", "summary": "Return full integrated Merlin replacement blueprint", "domain": "functions"},
        ],
        "integrations": [],
        "entities": [
            {
                "name": "MerlinSession",
                "summary": "Planned saved-session library. Standalone Product 20 currently exposes schema only.",
                "domain": "entities",
                "operations": ["schema"],
            },
        ],
        "connectors": [
            {
                "name": "github",
                "summary": "Standalone compatibility summary only; no token exposure.",
                "domain": "connectors",
            },
        ],
        "secrets": [
            {"name": "OPENROUTER_API_KEY", "domain": "secrets"},
            {"name": "BRAVE_API_KEY", "domain": "secrets"},
            {"name": "HF_API_TOKEN", "domain": "secrets"},
        ],
    }


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
    "getMerlinReplacementScope": lambda **args: {"data": get_replacement_scope()},
    "getMerlinStackBaseline": lambda **args: {"data": get_current_stack_baseline()},
    "getMerlinWeightsAndMeasures": lambda **args: {"data": get_weights_and_measures()},
    "getMerlinKnowledgeCore": lambda **args: {"data": get_knowledge_core_sources()},
    "runMerlinSyncChecks": lambda **args: {"data": run_sync_checks()},
    "getMerlinModelStrategy": lambda **args: {"data": get_model_strategy()},
    "getMerlinTrainingPlan": lambda **args: {"data": get_training_and_adaptation()},
    "getMerlinEnergyPlan": lambda **args: {"data": get_energy_optimization_track()},
    "getMerlinBackendPolicy": lambda **args: {"data": get_backend_expansion_policy()},
    "getMerlinGovernancePolicy": lambda **args: {"data": get_governance_integration_policy()},
    "getMerlinReliabilityPlan": lambda **args: {"data": get_reliability_security_plan()},
    "getMerlinRolloutPlan": lambda **args: {"data": get_rollout_plan()},
    "getMerlinOperatingRhythm": lambda **args: {"data": get_operating_rhythm()},
    "getMerlinExitCriteria": lambda **args: {"data": get_exit_criteria()},
    "getMerlinProgramBlueprint": lambda **args: {"data": get_full_program_blueprint()},
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
                    "description": "OpenRouter access for live Merlin/OpenRouter path.",
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
            "entities": {
                "MerlinSession": {
                    "summary": "Planned cross-device saved-session library; schema only in standalone Product 20.",
                    "schema": MERLIN_SESSION_SCHEMA,
                    "sample_count": 0,
                    "samples": [],
                    "storage_keys": [MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY],
                },
            },
        }
    return {"view": view, "error": "unsupported view"}


def route_tool(tool: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    """Route a Merlin tool call to a safe local capability."""
    args = dict(args or {})
    started = time.perf_counter()
    tool_type = "unknown"
    ok = True
    error = ""
    result: Any = None
    try:
        if tool in _FUNCTIONS:
            tool_type = "function"
            result = _FUNCTIONS[tool](**args)
        elif tool.startswith("entity.MerlinSession."):
            tool_type = "entity"
            op = tool.split(".")[-1]
            if op == "schema":
                result = {"data": MERLIN_SESSION_SCHEMA}
            else:
                ok = False
                error = "MerlinSession library operations are not yet implemented in standalone Product 20."
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
    return {
        "ok": ok,
        "tool": tool,
        "type": tool_type,
        "result": result,
        "error": error,
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


def orchestrate_steps(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute a bounded sequential Merlin tool chain."""
    if len(steps) > 10:
        raise ValueError("step cap exceeded (max 10)")
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
        result = route_tool(tool, args)
        result["step"] = index
        results.append(result)
    total_duration_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "ok": all(step.get("ok") for step in results),
        "steps": results,
        "total_duration_ms": total_duration_ms,
    }
