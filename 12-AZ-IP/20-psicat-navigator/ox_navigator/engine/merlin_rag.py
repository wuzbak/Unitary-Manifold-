# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""RAG helpers for Merlin, seeded from the canonical repository sources."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

from .interrogator import load_kb, search_kb

REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / "ui"
INTERROGATOR_KB_PATH = UI_ROOT / "interrogator-kb.json"


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


def build_rag_context(query: str) -> str:
    """Build the Merlin prompt context blocks."""
    context = retrieve_context(query)
    blocks = []
    if context["kb_match"]:
        kb = context["kb_match"]
        blocks.append(
            "[KNOWLEDGE BASE MATCH]\n"
            f"Topic: {kb['topic']}\n"
            f"Status: {kb['status']}\n"
            f"Answer: {kb['answer']}\n"
            f"Sources: {', '.join(kb.get('sources', []))}"
        )
    pillar_lines = []
    for pillar in context["pillars"]:
        pillar_lines.append(
            f"Pillar {pillar['id']} | {pillar['gate']} | {pillar['name']} | {pillar['text']}"
        )
    if pillar_lines:
        blocks.append("[RETRIEVED PILLAR CONTEXT]\n" + "\n".join(pillar_lines))
    if context["interrogator_hits"]:
        hit_lines = []
        for hit in context["interrogator_hits"]:
            hit_lines.append(
                f"{hit.get('id', 'unknown')} | {hit.get('gate', hit.get('status', 'UNKNOWN'))} | "
                f"{hit.get('claim', hit.get('prediction', ''))}"
            )
        blocks.append("[INTERROGATOR MATCHES]\n" + "\n".join(hit_lines))
    blocks.append("[PREDICTIONS]\n" + context["predictions"].strip())
    blocks.append("[FALLIBILITY]\n" + context["fallibility"].strip())
    return "\n\n".join(blocks)


def closest_pillar(query: str) -> dict[str, Any] | None:
    """Return the closest pillar match for a query."""
    return retrieve_context(query, max_chunks=1)["pillars"][0] if retrieve_context(query, max_chunks=1)["pillars"] else None
