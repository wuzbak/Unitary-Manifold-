# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Hybrid-automaton (non-smooth) routing over Merlin's toroidal facets.

ADJACENT TRACK.  Merlin's existing lane, kernel, and knowledge-base decisions
are hard thresholds — step functions of the query.  This module makes that
non-smoothness explicit without changing any primary decision:

* each decision is a guard with a numeric value, a threshold, and a margin;
* queries inside a margin sit on a *crease*; the set of facets reachable from
  there is the active set (the discrete analogue of a Clarke generalised
  gradient) and the reset policy is to fuse context across that set;
* each query receives a toroidal address (integer phase sketch + braid bank);
* query sequences are traced as hybrid trajectories with explicit jumps;
* repository routing uses weighted Dijkstra geodesics on the repo graph.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable, Sequence
from itertools import product
from typing import Any

from .merlin_kernel_routing import KERNEL_RULES, _rule_score, infer_runtime_kernel_id
from .merlin_repo_graph import build_repo_graph
from .merlin_retrieval_scoring import BM25Index, jaccard_overlap, token_list, token_set
from .merlin_router import (
    HEAVY_LANE_MIN_LENGTH,
    HEAVY_LANE_PHRASES,
    LARGE_CONTEXT_KEYWORDS,
    MEDIUM_LANE_MIN_LENGTH,
    classify_lane,
)
from .merlin_toroidal_geometry import (
    STATUS_LABEL,
    phase_sketch,
    sketch_similarity,
)

LANE_ORDER = ("small_fast_router", "medium_reasoner_default", "heavy_reasoner_exception")
DEFAULT_LENGTH_MARGIN = 16
DEFAULT_KB_MARGIN = 0.05
RELATION_WEIGHTS = {"imports": 1.0, "symbol_overlap": 2.0}
MAX_ACTIVE_FACETS = 12


def _lane_guards(query: str, margin: int) -> dict[str, Any]:
    sample = (query or "").lower()
    length = len(sample)
    heavy_hits = sum(1 for phrase in HEAVY_LANE_PHRASES if phrase in sample)
    keyword_hit = any(key in sample for key in LARGE_CONTEXT_KEYWORDS)
    primary = classify_lane(query)
    guards = [
        {"guard": "length>medium", "value": length, "threshold": MEDIUM_LANE_MIN_LENGTH,
         "distance": length - MEDIUM_LANE_MIN_LENGTH},
        {"guard": "length>heavy", "value": length, "threshold": HEAVY_LANE_MIN_LENGTH,
         "distance": length - HEAVY_LANE_MIN_LENGTH},
        {"guard": "heavy_phrase", "value": heavy_hits, "threshold": 1, "distance": heavy_hits - 1},
        {"guard": "large_context_keyword", "value": int(keyword_hit), "threshold": 1,
         "distance": int(keyword_hit) - 1},
    ]
    active = {primary}
    # Length guards are the only continuous ones; discrete keyword guards are crisp.
    if heavy_hits == 0:
        if abs(length - HEAVY_LANE_MIN_LENGTH) <= margin:
            active.update({"heavy_reasoner_exception", "medium_reasoner_default"})
        if not keyword_hit and abs(length - MEDIUM_LANE_MIN_LENGTH) <= margin:
            active.update({"medium_reasoner_default", "small_fast_router"})
    for guard in guards:
        guard["on_crease"] = guard["guard"].startswith("length") and abs(guard["distance"]) <= margin
    return {
        "primary": primary,
        "active": [lane for lane in LANE_ORDER if lane in active],
        "guards": guards,
    }


def _kernel_guards(query: str, lane: str, context_source: str) -> dict[str, Any]:
    sample = f"{lane} {query} None".lower()
    scores = {str(rule["kernel_id"]): _rule_score(sample, tuple(rule["keywords"])) for rule in KERNEL_RULES}
    primary = infer_runtime_kernel_id(lane=lane, query=query, context_source=context_source)
    # Lane and policy overrides decide the kernel outright; only the keyword-scored
    # path (medium lane, ordinary context) can sit on a tie crease.
    score_driven = lane == "medium_reasoner_default" and context_source not in {"policy_block", "privilege_block"}
    top = max(scores.values()) if scores else 0
    tied = sorted(kernel for kernel, score in scores.items() if score == top and top > 0) if score_driven else []
    active = sorted(set(tied) | {primary})
    return {
        "primary": primary,
        "active": active,
        "rule_scores": scores,
        "score_driven": score_driven,
        "tie_broken_by_priority": len(tied) > 1,
    }


def _kb_guard(query: str, margin: float) -> dict[str, Any]:
    from .merlin_rag import KB_MATCH_THRESHOLD, best_kb_match

    key, score = best_kb_match(query)
    matched = bool(key) and score > KB_MATCH_THRESHOLD
    return {
        "best_key": key,
        "score": round(score, 4),
        "threshold": KB_MATCH_THRESHOLD,
        "distance": round(score - KB_MATCH_THRESHOLD, 4),
        "matched": matched,
        "on_crease": bool(key) and abs(score - KB_MATCH_THRESHOLD) <= margin,
        "active": ["kb", "no_kb"] if bool(key) and abs(score - KB_MATCH_THRESHOLD) <= margin else (
            ["kb"] if matched else ["no_kb"]
        ),
    }


def evaluate_hybrid_state(
    query: str,
    *,
    context_source: str = "grounded_retrieval",
    length_margin: int = DEFAULT_LENGTH_MARGIN,
    kb_margin: float = DEFAULT_KB_MARGIN,
    include_kb: bool = True,
) -> dict[str, Any]:
    """Return the primary facet, the active facet set, and the reset policy for a query."""
    lane = _lane_guards(query, int(length_margin))
    kernel = _kernel_guards(query, lane["primary"], context_source)
    kb = _kb_guard(query, float(kb_margin)) if include_kb else {
        "matched": False, "on_crease": False, "active": ["no_kb"], "skipped": True,
    }
    kb_primary = "kb" if kb["matched"] else "no_kb"
    primary_facet = f"{lane['primary']}|{kernel['primary']}|{kb_primary}"
    # The kernel guard depends on the lane, so each reachable lane carries its own kernel set.
    combos = []
    for active_lane in lane["active"]:
        lane_kernel = kernel if active_lane == lane["primary"] else _kernel_guards(query, active_lane, context_source)
        combos.extend(product([active_lane], lane_kernel["active"], kb["active"]))
    active_facets = ["|".join(combo) for combo in combos][:MAX_ACTIVE_FACETS]
    creases = []
    if len(lane["active"]) > 1:
        creases.append("lane_length_threshold")
    if len(kernel["active"]) > 1:
        creases.append("kernel_score_tie")
    if kb.get("on_crease"):
        creases.append("kb_match_threshold")
    sketch = phase_sketch(token_list(query))
    return {
        "status": STATUS_LABEL,
        "query": query,
        "primary_facet": primary_facet,
        "active_facets": active_facets,
        "active_facet_count": len(combos),
        "on_crease": bool(creases),
        "creases": creases,
        "reset_policy": "fuse_active_facet_contexts" if creases else "commit_primary_facet",
        "lane": lane,
        "kernel": kernel,
        "kb": kb,
        "toroidal_address": sketch,
        "decision_preserved": "primary facet equals the existing classify_lane / kernel / lookup_kb decisions",
    }


def trace_hybrid_trajectory(queries: Sequence[str], **kwargs: Any) -> dict[str, Any]:
    """Trace a sequence of queries as a hybrid trajectory with discrete jumps."""
    states = [evaluate_hybrid_state(q, **kwargs) for q in queries]
    transitions = []
    for i in range(1, len(states)):
        before, after = states[i - 1], states[i]
        jumped = before["primary_facet"] != after["primary_facet"]
        transitions.append({
            "index": i,
            "from": before["primary_facet"],
            "to": after["primary_facet"],
            "jump": jumped,
            "address_similarity": sketch_similarity(
                before["toroidal_address"]["code"], after["toroidal_address"]["code"]
            ),
        })
    return {
        "status": STATUS_LABEL,
        "facets": [state["primary_facet"] for state in states],
        "transitions": transitions,
        "jump_count": sum(1 for t in transitions if t["jump"]),
        "crease_visits": sum(1 for state in states if state["on_crease"]),
    }


def toroidal_rank(query: str, documents: Sequence[str], *, top_k: int = 5) -> dict[str, Any]:
    """Rank documents by exact BM25 and by integer toroidal sketch; report their agreement.

    BM25 is authoritative.  The sketch ranking is the integer-only candidate
    for static bank routing; the overlap measures how faithful it is.
    """
    doc_tokens = [token_list(doc) for doc in documents]
    query_tokens = token_list(query)
    index = BM25Index(doc_tokens)
    bm25 = index.rank(query_tokens, top_k=top_k)
    query_code = phase_sketch(query_tokens)["code"]
    sketched = []
    for i, tokens in enumerate(doc_tokens):
        if not tokens:
            continue
        sketched.append((i, sketch_similarity(query_code, phase_sketch(tokens)["code"])))
    sketched.sort(key=lambda item: (-item[1], item[0]))
    sketched = sketched[: max(0, int(top_k))]
    bm25_ids = {i for i, _ in bm25}
    sketch_ids = {i for i, _ in sketched}
    return {
        "bm25": [{"index": i, "score": round(s, 4)} for i, s in bm25],
        "toroidal_sketch": [{"index": i, "similarity": s} for i, s in sketched],
        "top_k_agreement": round(len(bm25_ids & sketch_ids) / max(len(bm25_ids), 1), 4) if bm25_ids else 0.0,
        "authority": "bm25",
    }


def rank_pillars_bm25(query: str, *, top_k: int = 5) -> list[dict[str, Any]]:
    from .merlin_rag import PILLAR_KNOWLEDGE

    corpus = [
        token_list(" ".join(str(p.get(field, "")) for field in ("id", "name", "text", "gate")))
        for p in PILLAR_KNOWLEDGE
    ]
    index = BM25Index(corpus)
    query_tokens = token_list(query)
    query_set = set(query_tokens)
    ranked = index.rank(query_tokens, top_k=top_k)
    return [
        {
            "id": PILLAR_KNOWLEDGE[i].get("id"),
            "name": PILLAR_KNOWLEDGE[i].get("name"),
            "bm25": round(score, 4),
            "jaccard": round(jaccard_overlap(query_set, set(corpus[i])), 4),
        }
        for i, score in ranked
    ]


def _weighted_adjacency(edges: Iterable[dict[str, Any]]) -> dict[str, list[tuple[str, float, str]]]:
    adjacency: dict[str, list[tuple[str, float, str]]] = {}
    for edge in edges:
        weight = RELATION_WEIGHTS.get(str(edge.get("relation")), 3.0)
        source, target, relation = str(edge["source"]), str(edge["target"]), str(edge.get("relation"))
        adjacency.setdefault(source, []).append((target, weight, relation))
        adjacency.setdefault(target, []).append((source, weight, relation))
    return adjacency


def shortest_graph_path(edges: Iterable[dict[str, Any]], source: str, target: str) -> dict[str, Any]:
    """Weighted Dijkstra over an undirected relation graph (deterministic tie-breaks)."""
    adjacency = _weighted_adjacency(edges)
    if source not in adjacency or target not in adjacency:
        return {"found": False, "reason": "source or target not in graph", "path": [], "cost": None}
    best = {source: 0.0}
    previous: dict[str, tuple[str, str]] = {}
    heap: list[tuple[float, str]] = [(0.0, source)]
    visited: set[str] = set()
    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        if node == target:
            break
        for neighbour, weight, relation in sorted(adjacency.get(node, [])):
            candidate = cost + weight
            if candidate < best.get(neighbour, float("inf")):
                best[neighbour] = candidate
                previous[neighbour] = (node, relation)
                heapq.heappush(heap, (candidate, neighbour))
    if target not in best:
        return {"found": False, "reason": "no path", "path": [], "cost": None}
    path, relations = [target], []
    while path[-1] != source:
        node, relation = previous[path[-1]]
        path.append(node)
        relations.append(relation)
    path.reverse()
    relations.reverse()
    return {"found": True, "path": path, "relations": relations, "cost": best[target], "hops": len(path) - 1}


def route_repo_geodesic(source: str, target: str, *, max_files: int = 180) -> dict[str, Any]:
    graph = build_repo_graph(max_files=max_files)
    result = shortest_graph_path(graph.get("edges") or [], source, target)
    result.update({"source": source, "target": target, "relation_weights": dict(RELATION_WEIGHTS)})
    return result


def build_toroidal_navigation_packet(query: str, *, top_k: int = 5) -> dict[str, Any]:
    state = evaluate_hybrid_state(query)
    state["bm25_pillars"] = rank_pillars_bm25(query, top_k=top_k)
    state["query_token_count"] = len(token_set(query))
    return state


__all__ = [
    "RELATION_WEIGHTS",
    "build_toroidal_navigation_packet",
    "evaluate_hybrid_state",
    "rank_pillars_bm25",
    "route_repo_geodesic",
    "shortest_graph_path",
    "toroidal_rank",
    "trace_hybrid_trajectory",
]
