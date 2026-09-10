# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""RAG helpers for Merlin, seeded from the canonical repository sources."""

from __future__ import annotations

import importlib.util
import os
import re
import sys
import threading
from pathlib import Path
from typing import Any

from .merlin_counterexample import build_counterexample_digest
from .merlin_training_execution import get_merlin_lane_e_runtime_profiles
from .interrogator import load_kb, search_kb

REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / "ui"
INTERROGATOR_KB_PATH = UI_ROOT / "interrogator-kb.json"
_RAG_INDEX_CACHE = None
_RAG_INDEX_LOCK = threading.Lock()


def _load_module(name: str, path: Path):
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


_assistant_api = _load_module("merlin_assistant_api", REPO_ROOT / "bot" / "assistant_api.py")
_rag_index = _load_module("merlin_rag_index", REPO_ROOT / "bot" / "rag_index.py")

KNOWLEDGE_BASE: dict[str, dict[str, Any]] = dict(_rag_index.KNOWLEDGE_BASE)
PILLAR_KNOWLEDGE: list[dict[str, Any]] = list(_assistant_api.PILLAR_KNOWLEDGE)
PREDICTIONS_TEXT: str = _assistant_api.PREDICTIONS_TEXT
FALLIBILITY_TEXT: str = _assistant_api.FALLIBILITY_TEXT
build_status_response = _assistant_api.build_status_response
INTERROGATOR_ENTRIES = load_kb(INTERROGATOR_KB_PATH)
TOKEN_RE = re.compile(r"[a-z0-9_ΔβΩ²³⁴⁵]+", re.IGNORECASE)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text or "")}


def _default_index():
    global _RAG_INDEX_CACHE
    if _RAG_INDEX_CACHE is None:
        with _RAG_INDEX_LOCK:
            if _RAG_INDEX_CACHE is None:
                _RAG_INDEX_CACHE = _rag_index.RAGIndex.build(repo_root=REPO_ROOT)
    return _RAG_INDEX_CACHE


def lookup_kb(query: str) -> dict[str, Any] | None:
    """Return the best knowledge-base match if overlap clears the threshold."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return None
    best_key = None
    best_score = 0.0
    for key, entry in KNOWLEDGE_BASE.items():
        haystack = _tokens(" ".join([
            key,
            str(entry.get("topic", "")),
            str(entry.get("answer", "")),
            str(entry.get("status", "")),
            " ".join(entry.get("sources", [])),
        ]))
        if not haystack:
            continue
        score = len(query_tokens & haystack) / max(len(query_tokens), 1)
        if score > best_score:
            best_score = score
            best_key = key
    if best_key and best_score > 0.15:
        entry = dict(KNOWLEDGE_BASE[best_key])
        entry["key"] = best_key
        entry["score"] = round(best_score, 4)
        return entry
    return None


def retrieve_context(query: str, max_chunks: int = 5) -> dict[str, Any]:
    """Return pillar, prediction, fallibility, and interrogator context."""
    query_tokens = _tokens(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for pillar in PILLAR_KNOWLEDGE:
        haystack = _tokens(" ".join([
            str(pillar.get("id", "")),
            str(pillar.get("name", "")),
            str(pillar.get("text", "")),
            str(pillar.get("gate", "")),
        ]))
        score = len(query_tokens & haystack) / max(len(query_tokens | haystack), 1)
        scored.append((score, pillar))
    scored.sort(key=lambda item: (-item[0], int(item[1].get("id", 0))))
    pillars = [pillar for _, pillar in scored[:max_chunks]]
    interrogator_hits = search_kb(INTERROGATOR_ENTRIES, query)[:3]
    return {
        "pillars": pillars,
        "predictions": PREDICTIONS_TEXT,
        "fallibility": FALLIBILITY_TEXT,
        "interrogator_hits": interrogator_hits,
        "kb_match": lookup_kb(query),
    }


def build_context_scaffold(
    query: str,
    *,
    session: Any | None = None,
    max_chunks: int = 5,
    ast_file_limit: int = 5,
) -> dict[str, Any]:
    """Build the typed Merlin/PsiCat context scaffold."""
    try:
        normalized_ast_file_limit = max(1, int(5 if ast_file_limit is None else ast_file_limit))
    except (TypeError, ValueError):
        normalized_ast_file_limit = 5
    generic = _rag_index.build_context_scaffold(
        _default_index(),
        query,
        repo_root=REPO_ROOT,
        top_k=max_chunks,
        ast_file_limit=normalized_ast_file_limit,
    )
    context = retrieve_context(query, max_chunks=max_chunks)
    contradiction_digest = (
        build_counterexample_digest(session=session, limit=8)
        if session is not None
        else {"ok": True, "total_events": 0, "quarantined_insight_count": 0, "kind_counts": {}, "items": []}
    )
    memory_geometry = (
        session.get_geometric_memory_map(query, limit=6)
        if session is not None
        else {"ok": True, "model": "merlin_geometric_memory_map_v1", "landmark_count": 0, "frames": {}}
    )
    runtime_alignment = {
        "local_first": True,
        "openrouter_compat_enabled": bool(os.environ.get("MERLIN_ENABLE_OPENROUTER_COMPAT")),
        "suggested_agent_endpoints": list(generic.get("tooling", {}).get("suggested_endpoints", [])),
        "agent_toolkit_path": "/api/agentToolkit",
        "invoke_path": "/api/agentInvoke",
        "orchestrate_path": "/api/agentOrchestrate",
    }
    if generic.get("lane", {}).get("lane_id") == "runtime_performance":
        lane_e_payload = get_merlin_lane_e_runtime_profiles(refresh=False)
        runtime_alignment["lane_e_runtime_profiles"] = {
            "artifact_path": lane_e_payload.get("artifact_path"),
            "artifact_exists": lane_e_payload.get("artifact_exists"),
            "profile_keys": lane_e_payload.get("profile_keys", []),
        }
    return {
        **generic,
        "schema_version": "merlin_context_scaffold_v1",
        "retrieval": {
            **dict(generic.get("retrieval") or {}),
            "pillars": list(context.get("pillars") or []),
            "interrogator_hits": list(context.get("interrogator_hits") or []),
            "predictions": PREDICTIONS_TEXT,
            "fallibility": FALLIBILITY_TEXT,
        },
        "contradiction_ledger": {
            "digest": contradiction_digest,
            "memory_geometry_model": str(memory_geometry.get("model") or "unknown"),
            "contradiction_pressure": float(
                ((memory_geometry.get("frames") or {}).get("topological_persistence") or {}).get("contradiction_pressure", 0.0)
            ),
            "landmark_count": int(memory_geometry.get("landmark_count", 0) or 0),
        },
        "runtime_alignment": runtime_alignment,
    }


def render_context_scaffold(scaffold: dict[str, Any]) -> str:
    """Render the Merlin scaffold without appending the larger prediction/fallibility packs."""
    retrieval = dict(scaffold.get("retrieval") or {})
    blocks = [_rag_index.render_context_scaffold(scaffold)]
    pillar_lines = []
    for pillar in list(retrieval.get("pillars") or [])[:5]:
        pillar_lines.append(
            f"Pillar {pillar['id']} | {pillar['gate']} | {pillar['name']} | {pillar['text']}"
        )
    if pillar_lines:
        blocks.append("[RETRIEVED PILLAR CONTEXT]\n" + "\n".join(pillar_lines))
    interrogator_hits = list(retrieval.get("interrogator_hits") or [])
    if interrogator_hits:
        hit_lines = []
        for hit in interrogator_hits[:3]:
            hit_lines.append(
                f"{hit.get('id', 'unknown')} | {hit.get('gate', hit.get('status', 'UNKNOWN'))} | "
                f"{hit.get('claim', hit.get('prediction', ''))}"
            )
        blocks.append("[INTERROGATOR MATCHES]\n" + "\n".join(hit_lines))
    contradiction = dict(scaffold.get("contradiction_ledger") or {})
    digest = dict(contradiction.get("digest") or {})
    blocks.append(
        "[CONTRADICTION LEDGER]\n"
        f"events={int(digest.get('total_events', 0) or 0)} | "
        f"quarantined={int(digest.get('quarantined_insight_count', 0) or 0)} | "
        f"pressure={float(contradiction.get('contradiction_pressure', 0.0)):.3f}"
    )
    runtime = dict(scaffold.get("runtime_alignment") or {})
    blocks.append(
        "[RUNTIME ALIGNMENT]\n"
        f"local_first={bool(runtime.get('local_first'))} | "
        f"openrouter_compat_enabled={bool(runtime.get('openrouter_compat_enabled'))} | "
        f"agent_paths={runtime.get('agent_toolkit_path')}, {runtime.get('invoke_path')}, {runtime.get('orchestrate_path')}"
    )
    return "\n\n".join(blocks)


def build_rag_context(
    query: str,
    *,
    session: Any | None = None,
    ast_file_limit: int = 5,
    max_chunks: int = 5,
) -> str:
    """Build the Merlin prompt context blocks."""
    scaffold = build_context_scaffold(
        query,
        session=session,
        ast_file_limit=ast_file_limit,
        max_chunks=max_chunks,
    )
    context = retrieve_context(query, max_chunks=max_chunks)
    retrieval = dict(scaffold.get("retrieval") or {})
    blocks = [render_context_scaffold(scaffold)]
    blocks.append("[PREDICTIONS]\n" + str(retrieval.get("predictions") or context["predictions"]).strip())
    blocks.append("[FALLIBILITY]\n" + str(retrieval.get("fallibility") or context["fallibility"]).strip())
    return "\n\n".join(blocks)


def closest_pillar(query: str) -> dict[str, Any] | None:
    """Return the closest pillar match for a query."""
    return retrieve_context(query, max_chunks=1)["pillars"][0] if retrieve_context(query, max_chunks=1)["pillars"] else None
