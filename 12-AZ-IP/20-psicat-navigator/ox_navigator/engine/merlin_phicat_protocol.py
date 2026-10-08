# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""The PhiCat Protocol: golden-ratio-weighted, parallel braid-strand fusion.

ADJACENT TRACK (software emulation of a design idea, not a hardgate physics
claim).

Every ranking Merlin ships today — Jaccard, BM25, the hashed n-gram embedder,
the toroidal phase sketch — is fused the ordinary way: reciprocal-rank fusion
with a single flat constant (``RRF_K = 60`` in ``merlin_retrieval_eval``).
That is a *linear* combination: every strand gets the same weight on every
query, and the strands are folded together sequentially (jaccard, then bm25,
then the rest) rather than evaluated as independent parallel passes.

The PhiCat Protocol is a different, explicitly named fusion rule with two
properties the flat RRF fusion does not have:

1.  **Parallel, not sequential.**  All four strands are evaluated
    independently against the same query and corpus — none depends on
    another's output — and are only combined at the very end.  This module's
    ``_strand_rankings`` makes that independence structural: each ranking
    function receives only the raw query and corpus tokens.

2.  **Non-smooth, golden-ratio weighting, not a flat constant.**  The
    priority order of the four strands is **not** fixed query-to-query.  It
    is read out from the query's own braid-bank residue on the existing
    ``Z_74`` lattice (``merlin_toroidal_geometry.braid_bank``) — the same
    integer invariant the toroidal navigation lane already uses to place a
    query on the lattice.  Two queries whose bank residues differ by one
    step (crossing the mod-4 boundary) land in *entirely different* strand
    priority orders; there is no continuous interpolation between them.
    Within one priority order, weights decay by powers of the golden ratio
    ``φ = (1+√5)/2`` — the same constant already used in this repository's
    hardgate Pillar 208 derivation (``src/core/pillar208_braid_lock_pmns.py``)
    for the braid-lock Berry-phase quantisation
    ``k·π/(n₁·φ)``.  Reusing φ here is a deliberate, disclosed borrowing of
    that constant's role as a *discrete, non-linear* step size, not a new
    physics claim: this module makes no statement about PMNS mixing angles
    or any hardgate pillar, and the φ-weighting below is scored purely by
    the same retrieval benchmarks that scored every other ranker.

On top of the per-strand φ weight, each candidate pillar also receives a
**toroidal "gravity" weight**: its phase-sketch distance to the query's own
phase-sketch code on the ``Z_74`` lattice (``merlin_toroidal_geometry.
phase_sketch`` / ``toroidal_distance``), passed through an inverse-square-like
falloff.  This is the same lattice distance the toroidal navigation lane
already treats as a locality-sensitive similarity signal
(``sketch_similarity``); "gravity" is used here only as a plain-language name
for "nearer points on the lattice pull harder", not a claim that this
software implements gravitation.

What this honestly is:

* a deterministic, offline, reproducible fusion rule over the four rankings
  Merlin already computes — same inputs, same corpus, no new data source;
* a genuine behavioural difference from flat RRF: the strand priority order
  (and therefore which signal dominates) changes discontinuously by query,
  driven by existing lattice arithmetic, not a tunable hyper-parameter;
* benchmarked the same way every other upgrade in this lane is benchmarked —
  against ``merlin_retrieval_eval``'s labelled corpus and
  ``merlin_flag_ab.run_flag_ab``'s promotion gate — and shipped behind a
  default-OFF flag (``MERLIN_PHICAT_PROTOCOL``) until it clears that gate.

What this is not:

* it is not a hardgate physics claim, and it does not touch, modify, or
  depend on any hardgate pillar's status;
* "gravity" here is a named inverse-square-like weighting function over an
  integer lattice distance, not general relativity or Newtonian gravitation;
* it is not guaranteed to beat BM25 or ``rrf_all`` — ``phicat_protocol_report``
  reports its measured rank quality the same honest way
  ``pillar_embedder_report`` does, including when it is weaker;
* it does not call out to, require, or silently depend on any external
  "frontier" model.  ``frontier_capability_report`` below only *reads* the
  existing, already-guarded local-inference provider registry
  (``merlin_local_inference.get_inference_providers``) to report whether a
  stronger local/compatible model is configured; it never issues a network
  request as part of ranking, and ranking results are identical whether or
  not a frontier provider is configured.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .merlin_retrieval_eval import (
    _bm25_ranking,
    _embedder_ranking,
    _jaccard_ranking,
    _pillar_tokens,
)
from .merlin_retrieval_scoring import BM25Index, token_list
from .merlin_toroidal_geometry import (
    LATTICE_ORDER,
    braid_bank,
    phase_sketch,
    toroidal_distance,
)

STATUS_LABEL = "ADJACENT_TRACK"
PHI = (1.0 + 5.0**0.5) / 2.0  # golden ratio; see Pillar 208 Berry-phase quantum k*pi/(n1*phi)
STRAND_NAMES: tuple[str, ...] = ("jaccard", "bm25", "embedder", "toroidal_sketch")
GRAVITY_SCALE = LATTICE_ORDER / 4.0  # == EXPECTED_RANDOM_CIRCULAR_DISTANCE; the lattice's own "far" unit
METHOD = "phicat_protocol_v1"


def _query_code(query: str) -> list[int]:
    return list(phase_sketch(token_list(query))["code"])


def _pillar_codes(corpus_tokens: Sequence[list[str]]) -> list[list[int]]:
    return [list(phase_sketch(tokens)["code"]) for tokens in corpus_tokens]


def _toroidal_sketch_ranking(query_code: Sequence[int], codes: Sequence[Sequence[int]], ids: Sequence[Any]) -> list[Any]:
    """Rank pillars by ascending toroidal distance from the query's phase-sketch code."""
    scored = [(toroidal_distance(query_code, code), ids[i]) for i, code in enumerate(codes)]
    scored.sort(key=lambda item: (item[0], int(item[1])))
    return [pid for _, pid in scored]


def strand_order_for_query(query_code: Sequence[int]) -> tuple[str, ...]:
    """Deterministic, non-smooth per-query rotation of ``STRAND_NAMES``.

    The rotation amount is the query's own braid-bank residue mod the number
    of strands.  Because ``braid_bank`` is a mod-``LATTICE_ORDER`` integer
    computed from the query's two leading phase-sketch coordinates, a query
    whose bank residue crosses a multiple-of-4 boundary jumps to a completely
    different strand order with no intermediate state — a discontinuity by
    construction, not a smoothly varying weight.
    """
    if len(query_code) < 2:
        return STRAND_NAMES
    bank = braid_bank(query_code[:2])
    shift = bank % len(STRAND_NAMES)
    return STRAND_NAMES[shift:] + STRAND_NAMES[:shift]


def phi_strand_weights(order: Sequence[str]) -> dict[str, float]:
    """Golden-ratio discrete decay per strand priority tier: ``w_k = phi ** -k``."""
    return {name: PHI ** (-float(k)) for k, name in enumerate(order)}


def gravity_weight(distance: int, *, scale: float = GRAVITY_SCALE) -> float:
    """Inverse-square-like pull: smaller lattice distance -> larger weight, max 1.0."""
    if scale <= 0:
        return 1.0 if distance == 0 else 0.0
    return 1.0 / (1.0 + (float(distance) / scale) ** 2)


def _strand_rankings(
    query: str, corpus_tokens: Sequence[list[str]], ids: Sequence[Any], query_code: Sequence[int], codes: Sequence[Sequence[int]]
) -> dict[str, list[Any]]:
    from .merlin_semantic_embedder import EmbedderIndex

    bm25_index = BM25Index(corpus_tokens)
    embedder_index = EmbedderIndex(corpus_tokens)
    return {
        "jaccard": _jaccard_ranking(query, corpus_tokens, ids),
        "bm25": _bm25_ranking(query, bm25_index, ids),
        "embedder": _embedder_ranking(query, embedder_index, ids),
        "toroidal_sketch": _toroidal_sketch_ranking(query_code, codes, ids),
    }


def frontier_capability_report() -> dict[str, Any]:
    """Report whether a stronger local/compatible model is configured, read-only.

    This never issues a network call.  It only inspects the existing,
    already-guarded provider registry in ``merlin_local_inference`` so the
    PhiCat Protocol can honestly state whether it *could* incorporate a
    larger external model without ever requiring, or silently calling, one.
    """
    from .merlin_local_inference import get_inference_providers

    providers = get_inference_providers()
    available = [p for p in providers if p.get("available")]
    frontier_capable = [p for p in available if p.get("provider_kind") in {"local_openai_compat", "compatibility"}]
    return {
        "frontier_strand_active": bool(frontier_capable),
        "available_providers": [p["name"] for p in available],
        "frontier_providers": [p["name"] for p in frontier_capable],
        "network_calls_made": 0,
        "note": (
            "Status read-only: configuring MERLIN_LOCAL_SMALL_BASE_URL/MODEL or "
            "MERLIN_LOCAL_MEDIUM_BASE_URL/MODEL (see merlin_local_inference) makes a "
            "stronger local/compatible model available to the rest of Merlin's "
            "reasoning lanes; the PhiCat ranking fusion above never calls it."
        ),
    }


def run_phicat_protocol(
    query: str, pillars: Sequence[dict[str, Any]] | None = None, *, top_k: int = 5
) -> dict[str, Any]:
    """Fuse the four existing rankers with per-query, golden-ratio, lattice-distance weights."""
    if pillars is None:
        from .merlin_rag import PILLAR_KNOWLEDGE

        pillars = PILLAR_KNOWLEDGE
    ids = [p.get("id") for p in pillars]
    corpus_tokens = [_pillar_tokens(p) for p in pillars]
    codes = _pillar_codes(corpus_tokens)
    query_code = _query_code(query)

    rankings = _strand_rankings(query, corpus_tokens, ids, query_code, codes)
    order = strand_order_for_query(query_code)
    weights = phi_strand_weights(order)
    code_by_id = {pid: codes[i] for i, pid in enumerate(ids)}

    scores: dict[Any, float] = {}
    contributions: dict[Any, dict[str, float]] = {pid: {} for pid in ids}
    for name, ranking in rankings.items():
        strand_weight = weights[name]
        for rank, pid in enumerate(ranking, start=1):
            distance = toroidal_distance(query_code, code_by_id[pid])
            pull = strand_weight * (1.0 / rank) * gravity_weight(distance)
            scores[pid] = scores.get(pid, 0.0) + pull
            contributions[pid][name] = round(pull, 6)

    fused_order = sorted(ids, key=lambda pid: (-scores.get(pid, 0.0), int(pid)))
    by_id = {p.get("id"): p for p in pillars}
    top = [
        {
            "id": pid,
            "name": by_id[pid].get("name") if pid in by_id else None,
            "score": round(scores.get(pid, 0.0), 6),
            "strand_contributions": contributions[pid],
            "toroidal_distance": toroidal_distance(query_code, code_by_id[pid]),
        }
        for pid in fused_order[: max(0, int(top_k))]
    ]
    return {
        "status": STATUS_LABEL,
        "method": METHOD,
        "query_toroidal_code": query_code,
        "strand_order": list(order),
        "strand_weights": {name: round(w, 6) for name, w in weights.items()},
        "gravity_scale": GRAVITY_SCALE,
        "fused": top,
        "frontier_capability": frontier_capability_report(),
        "caveat": (
            "Parallel golden-ratio braid-strand fusion over Merlin's existing rankers; "
            "benchmark its rank quality with merlin_flag_ab.run_flag_ab before promoting "
            "MERLIN_PHICAT_PROTOCOL out of default-OFF."
        ),
    }


def phicat_protocol_ranking(query: str, corpus_tokens: Sequence[list[str]], ids: Sequence[Any]) -> list[Any]:
    """Full-corpus id ordering, for wiring into ``merlin_rag.retrieve_context``."""
    codes = _pillar_codes(corpus_tokens)
    query_code = _query_code(query)
    rankings = _strand_rankings(query, corpus_tokens, ids, query_code, codes)
    order = strand_order_for_query(query_code)
    weights = phi_strand_weights(order)
    code_by_id = {pid: codes[i] for i, pid in enumerate(ids)}
    scores: dict[Any, float] = {}
    for name, ranking in rankings.items():
        strand_weight = weights[name]
        for rank, pid in enumerate(ranking, start=1):
            distance = toroidal_distance(query_code, code_by_id[pid])
            scores[pid] = scores.get(pid, 0.0) + strand_weight * (1.0 / rank) * gravity_weight(distance)
    return sorted(ids, key=lambda pid: (-scores.get(pid, 0.0), int(pid)))


__all__ = [
    "GRAVITY_SCALE",
    "METHOD",
    "PHI",
    "STATUS_LABEL",
    "STRAND_NAMES",
    "frontier_capability_report",
    "gravity_weight",
    "phi_strand_weights",
    "phicat_protocol_ranking",
    "run_phicat_protocol",
    "strand_order_for_query",
]
