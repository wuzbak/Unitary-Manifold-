# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Toroidal situational awareness for a Merlin session (read-only).

ADJACENT TRACK.  Merlin's conversation is replayed as a hybrid trajectory on
the Z_74 torus: each turn has a discrete facet (lane | kernel | kb), a toroidal
address (phase sketch) and a lead pillar (BM25).  From that trajectory Merlin
can see where the conversation has been, which creases it has crossed, where
it jumped topic, and whether the current query is new ground or a return.

The report is computed from ``session.turns`` and never writes to the session.
The address similarity is a locality-sensitive approximation; topic labels are
heuristics for orientation, not semantic judgements.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any

from .merlin_retrieval_scoring import jaccard_overlap, token_set
from .merlin_toroidal_geometry import STATUS_LABEL, phase_sketch, sketch_similarity
from .merlin_toroidal_router import evaluate_hybrid_state, rank_pillars_bm25

# Topic decisions use exact content-token Jaccard; the toroidal address is a
# compact sketch of the same content tokens, reported alongside for navigation.
REVISIT_OVERLAP = 0.25
TOPIC_JUMP_OVERLAP = 0.1
FUNCTION_WORDS = frozenset(
    ["a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from", "how", "i", "in", "is", "it", "me", "of", "on", "or", "so", "that", "the", "this", "to", "was", "we", "what", "when", "where", "which", "who", "why", "will", "with", "you", "your", "about", "tell", "explain"]
)
MAX_AWARENESS_TURNS = 40
MAX_QUERY_CHARS = 4000


def _turn_queries(session: Any) -> list[str]:
    turns = list(getattr(session, "turns", None) or [])
    queries = [str(turn.get("query") or "") for turn in turns if isinstance(turn, dict)]
    return [q[:MAX_QUERY_CHARS] for q in queries if q.strip()][-MAX_AWARENESS_TURNS:]


def content_tokens(query: str) -> set[str]:
    return {token for token in token_set(query) if token not in FUNCTION_WORDS}


def _lead_pillar(query: str) -> int | None:
    ranked = rank_pillars_bm25(query, top_k=1)
    return ranked[0]["id"] if ranked else None


def build_awareness_from_queries(history: Sequence[str], current_query: str = "") -> dict[str, Any]:
    queries = [str(q)[:MAX_QUERY_CHARS] for q in history if str(q).strip()][-MAX_AWARENESS_TURNS:]
    current = str(current_query or "")[:MAX_QUERY_CHARS].strip()
    states = [evaluate_hybrid_state(q) for q in queries]
    contents = [content_tokens(q) for q in queries]
    codes = [phase_sketch(sorted(c))["code"] for c in contents]
    leads = [_lead_pillar(q) for q in queries]

    topic_jumps = []
    for i in range(1, len(states)):
        overlap = jaccard_overlap(contents[i - 1], contents[i])
        facet_jump = states[i - 1]["primary_facet"] != states[i]["primary_facet"]
        if overlap < TOPIC_JUMP_OVERLAP or facet_jump:
            topic_jumps.append({
                "turn": i,
                "content_overlap": round(overlap, 4),
                "address_similarity": sketch_similarity(codes[i - 1], codes[i]),
                "facet_jump": facet_jump,
                "lead_pillar_change": leads[i - 1] != leads[i],
            })

    position: dict[str, Any] = {"present": False}
    if current:
        state = evaluate_hybrid_state(current)
        current_content = content_tokens(current)
        code = phase_sketch(sorted(current_content))["code"]
        overlaps = [jaccard_overlap(current_content, prior) for prior in contents]
        nearest = max(range(len(overlaps)), key=lambda i: (overlaps[i], i)) if overlaps else None
        best = round(overlaps[nearest], 4) if nearest is not None else 0.0
        position = {
            "present": True,
            "primary_facet": state["primary_facet"],
            "on_crease": state["on_crease"],
            "creases": state["creases"],
            "reset_policy": state["reset_policy"],
            "lead_pillar": _lead_pillar(current),
            "nearest_turn": nearest,
            "nearest_content_overlap": best,
            "nearest_address_similarity": sketch_similarity(code, codes[nearest]) if nearest is not None else 0.0,
            "orientation": "revisiting" if nearest is not None and best >= REVISIT_OVERLAP else "new_territory",
        }

    occupancy = Counter(state["primary_facet"] for state in states)
    crease_counts = Counter(crease for state in states for crease in state["creases"])
    return {
        "status": STATUS_LABEL,
        "turns_observed": len(queries),
        "facet_occupancy": dict(sorted(occupancy.items())),
        "crease_visits": sum(1 for state in states if state["on_crease"]),
        "crease_types": dict(sorted(crease_counts.items())),
        "lead_pillars": leads,
        "pillar_dwell": dict(sorted(Counter(p for p in leads if p is not None).items())),
        "topic_jumps": topic_jumps,
        "current_position": position,
        "thresholds": {"revisit_overlap": REVISIT_OVERLAP, "topic_jump_overlap": TOPIC_JUMP_OVERLAP},
        "read_only": True,
        "caveat": "Topic labels use lexical overlap; the address is a locality-sensitive sketch. They orient, they do not judge meaning.",
    }


def build_session_awareness(session: Any, current_query: str = "") -> dict[str, Any]:
    report = build_awareness_from_queries(_turn_queries(session), current_query)
    report["contradiction_events"] = len(list(getattr(session, "contradiction_events", None) or []))
    return report


__all__ = [
    "REVISIT_OVERLAP",
    "TOPIC_JUMP_OVERLAP",
    "build_awareness_from_queries",
    "build_session_awareness",
    "content_tokens",
]
