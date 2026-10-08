# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for the local hashed n-gram semantic embedder (ADJACENT TRACK).

Covers: determinism, normalization, opt-in default-OFF non-regression of
``retrieve_context``, the ``evaluate_rankers(include_embedder=True)``
extension, the flag A/B harness, and the tool/server wiring.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_rag
from ox_navigator.engine.merlin_retrieval_eval import LABELLED_QUERIES, evaluate_rankers
from ox_navigator.engine.merlin_semantic_embedder import (
    DEFAULT_EMBED_DIMS,
    STATUS_LABEL,
    EmbedderIndex,
    cosine_similarity,
    embed_text,
    embedder_similarity_report,
    pillar_embedder_report,
)
from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool

# --- core embedding properties ----------------------------------------------------------

def test_embed_text_is_deterministic() -> None:
    a = embed_text("orbifold compactification and winding number")
    b = embed_text("orbifold compactification and winding number")
    assert np.array_equal(a, b)


def test_embed_text_is_l2_normalised() -> None:
    vector = embed_text("braided Chern-Simons level five seven")
    assert vector.shape == (DEFAULT_EMBED_DIMS,)
    assert abs(float(np.linalg.norm(vector)) - 1.0) < 1e-9


def test_embed_text_empty_string_is_zero_vector() -> None:
    vector = embed_text("")
    assert float(np.linalg.norm(vector)) == 0.0


def test_cosine_similarity_identical_text_is_one() -> None:
    vector = embed_text("holographic boundary entropy")
    assert cosine_similarity(vector, vector) == pytest.approx(1.0, abs=1e-9)


def test_cosine_similarity_unrelated_text_is_low() -> None:
    a = embed_text("holographic boundary entropy area")
    b = embed_text("zzyx qqpp wwvv mmnn")
    assert cosine_similarity(a, b) < 0.2


def test_embed_tokens_rejects_out_of_range_dims() -> None:
    with pytest.raises(ValueError):
        embed_text("anything", dims=4)
    with pytest.raises(ValueError):
        embed_text("anything", dims=100_000)


def test_shared_morphology_scores_higher_than_unrelated() -> None:
    """Character n-grams give partial credit that whole-token matching misses."""
    query = embed_text("neutrino mass splitting")
    morphological = embed_text("neutrinos mass-splittings")
    unrelated = embed_text("justice sentencing reform courts")
    assert cosine_similarity(query, morphological) > cosine_similarity(query, unrelated)


# --- EmbedderIndex / similarity report --------------------------------------------------

def test_embedder_index_ranks_best_match_first() -> None:
    docs = ["the quick brown fox", "orbifold fold winding number five", "unrelated text about ferries"]
    report = embedder_similarity_report("winding number orbifold", docs, top_k=3)
    assert report["status"] == STATUS_LABEL
    assert report["results"]
    assert report["results"][0]["index"] == 1


def test_embedder_index_len() -> None:
    index = EmbedderIndex([["a", "b"], ["c"]])
    assert len(index) == 2


# --- pillar ranking report vs BM25 -------------------------------------------------------

def test_pillar_embedder_report_structure() -> None:
    report = pillar_embedder_report("Why is the winding number five and not seven?", top_k=5)
    assert report["status"] == STATUS_LABEL
    assert report["authority"] == "bm25"
    assert 0 <= len(report["embedder"]) <= 5
    assert 0.0 <= report["bm25_top_k_agreement"] <= 1.0
    assert report["pillar_count"] == len(merlin_rag.PILLAR_KNOWLEDGE)


# --- evaluate_rankers(include_embedder=True) ---------------------------------------------

def test_evaluate_rankers_include_embedder_default_off_is_unchanged() -> None:
    without = evaluate_rankers()
    assert "embedder" not in without["rankers"]
    assert "rrf_all" not in without["rankers"]
    assert without["best_by_mrr"] == "bm25"


def test_evaluate_rankers_include_embedder_adds_measured_rankers() -> None:
    report = evaluate_rankers(include_embedder=True)
    assert report["query_count"] == len(LABELLED_QUERIES)
    assert {"jaccard", "bm25", "rrf", "embedder", "rrf_all"} <= set(report["rankers"])
    for ranker in ("embedder", "rrf_all"):
        assert {"recall@1", "recall@5", "mrr", "ndcg@5"} <= set(report["summary"][ranker])
        assert 0.0 <= report["summary"][ranker]["mrr"] <= 1.0
    assert report["best_by_mrr"] in report["rankers"]


# --- opt-in pillar ranking flag (additive; default OFF) ---------------------------------

def test_semantic_embedder_ranking_default_off(monkeypatch) -> None:
    monkeypatch.delenv(merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG, raising=False)
    assert merlin_rag.semantic_embedder_ranking_enabled() is False


def test_semantic_embedder_ranking_flag_changes_order_only(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    monkeypatch.delenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, raising=False)
    monkeypatch.delenv(merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG, raising=False)
    baseline = merlin_rag.retrieve_context(query, max_chunks=5)
    monkeypatch.setenv(merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    assert len(ranked["pillars"]) == len(baseline["pillars"]) == 5
    assert {k: v for k, v in ranked.items() if k != "pillars"} == {k: v for k, v in baseline.items() if k != "pillars"}


def test_semantic_embedder_flag_takes_precedence_over_bm25_flag(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    monkeypatch.setenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, "1")
    monkeypatch.setenv(merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    expected = merlin_rag._semantic_embedder_pillars(query, 5)
    assert [p["id"] for p in ranked["pillars"]] == [p["id"] for p in expected]


# --- flag A/B harness includes the new flag ----------------------------------------------

def test_flag_ab_opt_in_flags_include_semantic_embedder() -> None:
    from ox_navigator.engine.merlin_flag_ab import OPT_IN_FLAGS

    assert merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG in OPT_IN_FLAGS


# --- tool + server surface ---------------------------------------------------------------

def test_semantic_embedder_tool_registered_with_schema() -> None:
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    assert "getMerlinSemanticEmbedder" in names
    assert "args_schema" in names["getMerlinSemanticEmbedder"]


def test_semantic_embedder_tool_routes() -> None:
    result = route_tool("getMerlinSemanticEmbedder", {"query": "winding number five seven", "top_k": 3})
    assert result["ok"] is True
    assert result["result"]["data"]["status"] == STATUS_LABEL
    assert result["result"]["data"]["authority"] == "bm25"


def test_semantic_embedder_tool_requires_query() -> None:
    assert route_tool("getMerlinSemanticEmbedder", {"top_k": 3})["ok"] is False


def test_server_exposes_semantic_embedder_endpoint() -> None:
    import ox_navigator.app.server as server_module

    assert "/api/psicat/semantic-embedder" in Path(server_module.__file__).read_text(encoding="utf-8")
