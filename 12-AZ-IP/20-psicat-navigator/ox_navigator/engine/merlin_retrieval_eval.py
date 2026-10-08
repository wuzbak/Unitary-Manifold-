# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Labelled retrieval evaluation for Merlin pillar context.

ADJACENT TRACK.  Measures, rather than asserts, how well each ranking finds
the right pillars:

* ``jaccard``  — the current ``retrieve_context`` ranking (unchanged);
* ``bm25``     — Okapi BM25 over the same fields;
* ``rrf``      — reciprocal-rank fusion of the two (k = 60).

The query set is hand-labelled against ``PILLAR_KNOWLEDGE`` and deliberately
paraphrased so that exact-name matching is not enough.  It is small (a few
dozen queries); results are indicative, not a benchmark of record.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from .merlin_retrieval_scoring import BM25Index, jaccard_overlap, token_list, token_set

RRF_K = 60
DEFAULT_CUTOFFS = (1, 3, 5)
RANKERS = ("jaccard", "bm25", "rrf")

# (query, relevant pillar ids). Labels reference bot/assistant_api.PILLAR_KNOWLEDGE.
LABELLED_QUERIES: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("What is the five-dimensional metric with the radion field?", (1,)),
    ("Show me the line element ds² with the scalar φ and gauge potential", (1,)),
    ("How do the 5D Einstein equations reduce to 4D gravity plus electromagnetism?", (2,)),
    ("Which equations give gravity, EM and a scalar after reduction?", (2,)),
    ("How is the extra dimension folded by y → −y?", (3,)),
    ("orbifold compactification and the projection of Kaluza-Klein modes", (3,)),
    ("Where does Bekenstein-Hawking entropy come from in the framework?", (4,)),
    ("holographic boundary entropy proportional to area", (4,)),
    ("Does the fixed-point iteration of the multiverse operator converge?", (5,)),
    ("FTUM convergence", (5,)),
    ("Why is the winding number five and not seven?", (67,)),
    ("How does Planck's spectral index pick n_w?", (67,)),
    ("Is the brain-universe attractor a physics claim?", (9,)),
    ("What is Xi_c = 35/74 used for?", (9,)),
    ("Is the LENR excess-heat prediction a confirmation that cold fusion occurs?", (15,)),
    ("tunneling coefficient of performance prediction", (15,)),
    ("Why are the CMB acoustic peaks too low by a factor of four to seven?", (57,)),
    ("amplitude suppression admission and eta(k)", (57,)),
    ("What is the origin holon Ω₀?", (70,)),
    ("master convergence attractor and its sub-pillars", (70,)),
    ("Which pillar closes the core set and where do adjacent tracks begin?", (208,)),
    ("How many hardgate pillars are there before the research tracks?", (208,)),
    ("Lean4 theorems for the APS index", (700,)),
    ("NPW5APS formal proof file", (700,)),
    ("lepton CP violation Jarlskog invariant from the lattice", (772,)),
    ("How was the solar mass-splitting tension reduced from 2.98σ?", (772, 773)),
    ("next-to-leading-order corrections to Δm²₂₁", (773,)),
    ("Is the neutrino mass-squared difference below one sigma yet?", (773,)),
    ("Where do the winding numbers 5 and 7 enter k_cs = 74?", (67, 3)),
    ("Which pillars are adjacent tracks rather than hardgate claims?", (9, 15, 208)),
)


def _pillar_tokens(pillar: dict[str, Any]) -> list[str]:
    return token_list(" ".join(str(pillar.get(field, "")) for field in ("id", "name", "text", "gate")))


def _jaccard_ranking(query: str, corpus_tokens: Sequence[list[str]], ids: Sequence[Any]) -> list[Any]:
    """Mirror of ``merlin_rag.retrieve_context`` ordering (score desc, then id asc)."""
    query_set = token_set(query)
    scored = [(jaccard_overlap(query_set, set(tokens)), ids[i]) for i, tokens in enumerate(corpus_tokens)]
    scored.sort(key=lambda item: (-item[0], int(item[1])))
    return [pid for score, pid in scored if score > 0.0]


def _bm25_ranking(query: str, index: BM25Index, ids: Sequence[Any]) -> list[Any]:
    return [ids[i] for i, _ in index.rank(token_list(query), top_k=len(ids))]


def reciprocal_rank_fusion(rankings: Sequence[Sequence[Any]], *, k: int = RRF_K) -> list[Any]:
    scores: dict[Any, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return [item for item, _ in sorted(scores.items(), key=lambda kv: (-kv[1], int(kv[0])))]


def _metrics(ranking: Sequence[Any], relevant: set[Any], cutoffs: Sequence[int]) -> dict[str, float]:
    out: dict[str, float] = {}
    for c in cutoffs:
        out[f"recall@{c}"] = len(set(ranking[:c]) & relevant) / len(relevant)
    reciprocal = 0.0
    for rank, item in enumerate(ranking, start=1):
        if item in relevant:
            reciprocal = 1.0 / rank
            break
    out["mrr"] = reciprocal
    depth = max(cutoffs)
    dcg = sum(1.0 / math.log2(rank + 1) for rank, item in enumerate(ranking[:depth], start=1) if item in relevant)
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, min(len(relevant), depth) + 1))
    out[f"ndcg@{depth}"] = dcg / ideal if ideal else 0.0
    return out


def evaluate_rankers(
    pillars: Sequence[dict[str, Any]] | None = None,
    queries: Sequence[tuple[str, Sequence[int]]] | None = None,
    *,
    cutoffs: Sequence[int] = DEFAULT_CUTOFFS,
) -> dict[str, Any]:
    if pillars is None:
        from .merlin_rag import PILLAR_KNOWLEDGE

        pillars = PILLAR_KNOWLEDGE
    labelled = list(queries if queries is not None else LABELLED_QUERIES)
    ids = [p.get("id") for p in pillars]
    known = set(ids)
    corpus_tokens = [_pillar_tokens(p) for p in pillars]
    index = BM25Index(corpus_tokens)
    totals = {name: {} for name in RANKERS}
    per_query = []
    skipped = []
    for query, relevant_ids in labelled:
        relevant = {pid for pid in relevant_ids if pid in known}
        if not relevant:
            skipped.append(query)
            continue
        jaccard = _jaccard_ranking(query, corpus_tokens, ids)
        bm25 = _bm25_ranking(query, index, ids)
        rankings = {"jaccard": jaccard, "bm25": bm25, "rrf": reciprocal_rank_fusion([jaccard, bm25])}
        row = {"query": query, "relevant": sorted(relevant)}
        for name, ranking in rankings.items():
            metrics = _metrics(ranking, relevant, cutoffs)
            row[name] = {"top3": ranking[:3], **{k: round(v, 4) for k, v in metrics.items()}}
            for key, value in metrics.items():
                totals[name][key] = totals[name].get(key, 0.0) + value
        per_query.append(row)
    n = len(per_query)
    summary = {
        name: {key: round(value / n, 4) for key, value in metrics.items()} if n else {}
        for name, metrics in totals.items()
    }
    best = max(RANKERS, key=lambda name: (summary[name].get("mrr", 0.0), summary[name].get("recall@5", 0.0))) if n else None
    return {
        "status": "ADJACENT_TRACK",
        "query_count": n,
        "corpus_size": len(ids),
        "skipped_queries": skipped,
        "summary": summary,
        "best_by_mrr": best,
        "per_query": per_query,
        "caveat": "Small hand-labelled set over a 14-entry corpus; indicative only.",
    }


__all__ = ["LABELLED_QUERIES", "RRF_K", "evaluate_rankers", "reciprocal_rank_fusion"]
