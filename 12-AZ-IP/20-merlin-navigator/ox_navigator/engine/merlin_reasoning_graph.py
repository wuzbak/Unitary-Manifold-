# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Multi-hop pillar reasoning-chain helpers for Merlin."""

from __future__ import annotations

import re
from typing import Any

from .lean4_index import get_theorems_by_pillar
from .merlin_rag import PILLAR_KNOWLEDGE, retrieve_context
from .pillar_graph import find_critical_path

TOKEN_RE = re.compile(r"[a-z0-9_ΔβΩ²³⁴⁵]+", re.IGNORECASE)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text or "")}


def _pillar_lookup() -> dict[int, dict[str, Any]]:
    return {
        int(pillar.get("id", 0)): dict(pillar)
        for pillar in PILLAR_KNOWLEDGE
        if str(pillar.get("id", "")).isdigit()
    }


def _pillar_score(query_tokens: set[str], pillar: dict[str, Any]) -> float:
    haystack = _tokens(
        " ".join(
            [
                str(pillar.get("id", "")),
                str(pillar.get("name", "")),
                str(pillar.get("text", "")),
                str(pillar.get("gate", "")),
            ]
        )
    )
    if not haystack:
        return 0.0
    return round(len(query_tokens & haystack) / max(len(query_tokens | haystack), 1), 4)


def _node_record(pillar: dict[str, Any], query_tokens: set[str]) -> dict[str, Any]:
    pillar_id = int(pillar.get("id", 0))
    lean4_hits = get_theorems_by_pillar(pillar_id)
    return {
        "pillar_id": pillar_id,
        "name": str(pillar.get("name", "")),
        "gate": str(pillar.get("gate", "")),
        "score": _pillar_score(query_tokens, pillar),
        "lean4_hits": lean4_hits,
        "lean4_hit_count": len(lean4_hits),
        "excerpt": str(pillar.get("text", ""))[:220],
    }


def _path_between(start: int, end: int) -> tuple[list[int], str]:
    if start == end:
        return [start], "self"
    forward = find_critical_path(start, end)
    if forward:
        return forward, "dependency_forward"
    reverse = find_critical_path(end, start)
    if reverse:
        return list(reversed(reverse)), "dependency_reverse"
    return [start, end], "semantic_neighbor"


def get_reasoning_chain(query: str, *, max_hops: int = 3) -> dict[str, Any]:
    hop_cap = max(1, min(int(max_hops or 3), 5))
    context = retrieve_context(query, max_chunks=max(hop_cap, 3))
    ranked = list(context.get("pillars") or [])
    if not ranked:
        return {
            "ok": True,
            "query": query,
            "chain": [],
            "edges": [],
            "proof_chain_confidence": 0.0,
            "lean4_total_hits": 0,
        }

    lookup = _pillar_lookup()
    query_tokens = _tokens(query)
    ordered_ids: list[int] = []
    for pillar in ranked[:hop_cap]:
        pillar_id = int(pillar.get("id", 0))
        if pillar_id and pillar_id not in ordered_ids:
            ordered_ids.append(pillar_id)

    path_ids: list[int] = [ordered_ids[0]]
    edges: list[dict[str, Any]] = []
    for target_id in ordered_ids[1:]:
        segment, relation = _path_between(path_ids[-1], target_id)
        for node_id in segment[1:]:
            if node_id not in path_ids:
                path_ids.append(node_id)
        edge_weight = round(
            0.95 if relation.startswith("dependency") else 0.55,
            3,
        )
        edges.append(
            {
                "from_pillar": int(segment[0]),
                "to_pillar": int(segment[-1]),
                "relation": relation,
                "path": segment,
                "edge_weight": edge_weight,
            }
        )

    chain: list[dict[str, Any]] = []
    lean4_total_hits = 0
    for pillar_id in path_ids[: hop_cap + len(edges)]:
        pillar = lookup.get(pillar_id) or {
            "id": pillar_id,
            "name": f"Pillar {pillar_id}",
            "gate": "ARCHITECTURE_LIMIT",
            "text": "No lightweight registry record was available in the embedded pillar index.",
        }
        node = _node_record(pillar, query_tokens)
        lean4_total_hits += int(node["lean4_hit_count"])
        chain.append(node)

    edge_average = (sum(item["edge_weight"] for item in edges) / len(edges)) if edges else 0.0
    coverage = min(len(ordered_ids) / max(hop_cap, 1), 1.0)
    kb_match = context.get("kb_match")
    if kb_match is None:
        kb_match = context.get("match")
    evidence_score = 0.0
    if kb_match:
        evidence_score += 0.1
    evidence_score += 0.35 * edge_average
    evidence_score += min(0.45, 0.09 * lean4_total_hits)
    proof_chain_confidence = round(min(0.99, evidence_score * coverage), 3)
    return {
        "ok": True,
        "query": query,
        "kb_match": kb_match,
        "chain": chain,
        "edges": edges,
        "proof_chain_confidence": proof_chain_confidence,
        "lean4_total_hits": lean4_total_hits,
        "primary_pillar": chain[0] if chain else None,
    }
