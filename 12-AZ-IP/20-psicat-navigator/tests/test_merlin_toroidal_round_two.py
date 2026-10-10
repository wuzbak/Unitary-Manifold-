# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

import httpx
import numpy as np
import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_rag
from ox_navigator.engine import merlin_toroidal_geometry as geo
from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_retrieval_eval import (
    LABELLED_QUERIES,
    _jaccard_ranking,
    _pillar_tokens,
    evaluate_rankers,
    reciprocal_rank_fusion,
)
from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool
from ox_navigator.engine.merlin_toroidal_awareness import (
    build_awareness_from_queries,
    build_session_awareness,
    content_tokens,
)
from ox_navigator.engine.merlin_unitary_lab import (
    cayley_step,
    l1_clarke_subgradient,
    procrustes_fit,
    random_unitary,
    run_unitary_lab,
    run_unitary_lab_sweep,
    unitarity_residual,
)

GOLDEN_SHA256 = "3aec49f2d748482657164ec8081157421b68e64397304107f99c8b5d34f2055d"
ROUND_TWO_TOOLS = (
    "getMerlinToroidalGeometry",
    "getMerlinToroidalNavigation",
    "getMerlinToroidalAwareness",
    "getMerlinRetrievalEval",
    "getMerlinUnitaryLab",
    "getMerlinPhaseIsaVectors",
)


# --- retrieval evaluation -------------------------------------------------------------

def test_reciprocal_rank_fusion_on_toy_rankings() -> None:
    fused = reciprocal_rank_fusion([[1, 2, 3], [2, 1, 3]], k=60)
    assert fused[:2] == [1, 2]  # tie broken by id
    assert reciprocal_rank_fusion([[3, 2], [3, 1]])[0] == 3


def test_jaccard_ranking_mirrors_retrieve_context(monkeypatch) -> None:
    monkeypatch.delenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, raising=False)
    pillars = merlin_rag.PILLAR_KNOWLEDGE
    ids = [p.get("id") for p in pillars]
    tokens = [_pillar_tokens(p) for p in pillars]
    for query, _ in LABELLED_QUERIES:
        live = [p.get("id") for p in merlin_rag.retrieve_context(query, max_chunks=5)["pillars"]]
        assert live == _jaccard_ranking(query, tokens, ids)[:5]


def test_evaluate_rankers_reports_measured_result() -> None:
    report = evaluate_rankers()
    assert report["query_count"] == len(LABELLED_QUERIES)
    for ranker in ("jaccard", "bm25", "rrf"):
        assert {"recall@1", "recall@5", "mrr", "ndcg@5"} <= set(report["summary"][ranker])
        assert 0.0 <= report["summary"][ranker]["mrr"] <= 1.0
    assert report["summary"]["bm25"]["mrr"] >= report["summary"]["jaccard"]["mrr"]
    assert report["best_by_mrr"] == "bm25"


def test_evaluate_rankers_metrics_on_tiny_corpus() -> None:
    pillars = [{"id": 1, "name": "alpha", "text": "orbifold fold"}, {"id": 2, "name": "beta", "text": "neutrino mass"}]
    report = evaluate_rankers(pillars, [("orbifold", (1,)), ("neutrino mass", (2,)), ("unknown", (99,))])
    assert report["query_count"] == 2
    assert report["skipped_queries"] == ["unknown"]
    assert report["summary"]["bm25"]["recall@1"] == 1.0


# --- opt-in BM25 pillar ranking (additive; default OFF) -------------------------------

def test_bm25_pillar_ranking_default_off(monkeypatch) -> None:
    monkeypatch.delenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, raising=False)
    assert merlin_rag.bm25_pillar_ranking_enabled() is False


def test_bm25_pillar_ranking_flag_changes_order_only(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    monkeypatch.delenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, raising=False)
    baseline = merlin_rag.retrieve_context(query, max_chunks=5)
    monkeypatch.setenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    assert len(ranked["pillars"]) == len(baseline["pillars"]) == 5
    assert ranked["pillars"][0]["id"] == 57
    assert {k: v for k, v in ranked.items() if k != "pillars"} == {k: v for k, v in baseline.items() if k != "pillars"}


# --- opt-in production RRF fusion ranking (additive; default OFF) ---------------------

def test_rrf_fusion_ranking_default_off(monkeypatch) -> None:
    monkeypatch.delenv(merlin_rag.RRF_FUSION_RANKING_FLAG, raising=False)
    assert merlin_rag.rrf_fusion_ranking_enabled() is False


def test_rrf_fusion_ranking_flag_changes_order_only(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    monkeypatch.delenv(merlin_rag.RRF_FUSION_RANKING_FLAG, raising=False)
    baseline = merlin_rag.retrieve_context(query, max_chunks=5)
    monkeypatch.setenv(merlin_rag.RRF_FUSION_RANKING_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    assert len(ranked["pillars"]) == len(baseline["pillars"]) == 5
    assert ranked["pillars"][0]["id"] == 57
    assert {k: v for k, v in ranked.items() if k != "pillars"} == {k: v for k, v in baseline.items() if k != "pillars"}


def test_rrf_fusion_ranking_matches_offline_rrf_all(monkeypatch) -> None:
    """The production flag must reproduce evaluate_rankers' already-measured rrf_all order."""
    from ox_navigator.engine.merlin_retrieval_eval import (
        _bm25_ranking,
        _embedder_ranking,
        _jaccard_ranking,
        _pillar_tokens,
        reciprocal_rank_fusion,
    )
    from ox_navigator.engine.merlin_retrieval_scoring import BM25Index
    from ox_navigator.engine.merlin_semantic_embedder import EmbedderIndex

    query = "Why are the CMB acoustic peaks suppressed?"
    pillars = merlin_rag.PILLAR_KNOWLEDGE
    ids = [p.get("id") for p in pillars]
    tokens = [_pillar_tokens(p) for p in pillars]
    expected = reciprocal_rank_fusion([
        _jaccard_ranking(query, tokens, ids),
        _bm25_ranking(query, BM25Index(tokens), ids),
        _embedder_ranking(query, EmbedderIndex(tokens), ids),
    ])[:5]

    monkeypatch.setenv(merlin_rag.RRF_FUSION_RANKING_FLAG, "1")
    live = [p.get("id") for p in merlin_rag.retrieve_context(query, max_chunks=5)["pillars"]]
    assert live == expected


# --- flag A/B harness -----------------------------------------------------------------

def test_flag_ab_restores_environment_and_reports(monkeypatch) -> None:
    from ox_navigator.engine.merlin_flag_ab import OPT_IN_FLAGS, run_flag_ab

    for flag in OPT_IN_FLAGS:
        monkeypatch.delenv(flag, raising=False)
    report = run_flag_ab(stages=["stage_a_parity_capture"], limit_per_stage=2)
    assert report["ok"] is True
    assert report["benchmark_count"] == 2
    assert set(report["summary"]) == {
        "baseline", "crease_fusion", "bm25_pillars", "both", "semantic_embedder", "phicat_protocol",
        "rrf_fusion", "psicat_literature_corpus", "hosting_retention_guard", "all_flags",
    }
    assert report["summary"]["baseline"]["answers_changed"] == []
    for flag in OPT_IN_FLAGS:
        assert flag not in os.environ


def test_flag_ab_rejects_unknown_inputs() -> None:
    from ox_navigator.engine.merlin_flag_ab import run_flag_ab

    assert run_flag_ab(stages=["no_such_stage"])["ok"] is False
    assert run_flag_ab(stages=["stage_a_parity_capture"], limit_per_stage=0, variants={"x": ("NOT_A_FLAG",)})["ok"] is False


@pytest.mark.slow
def test_flag_ab_full_corpus_has_no_regressions() -> None:
    from ox_navigator.engine.merlin_flag_ab import run_flag_ab

    report = run_flag_ab()
    assert report["benchmark_count"] >= 30
    for variant in report["summary"].values():
        assert variant["regressions"] == []


# --- toroidal awareness ---------------------------------------------------------------

HISTORY = [
    "What is the CMB birefringence prediction from the braided winding?",
    "How does LiteBIRD test the birefringence angle beta?",
    "Explain cold fusion COP prediction in palladium",
]


def test_content_tokens_drop_function_words() -> None:
    assert content_tokens("What is the orbifold?") == {"orbifold"}


def test_awareness_orientation_and_jumps() -> None:
    revisit = build_awareness_from_queries(HISTORY, "birefringence braided winding CMB prediction")
    assert revisit["current_position"]["orientation"] == "revisiting"
    assert revisit["current_position"]["nearest_turn"] == 0
    fresh = build_awareness_from_queries(HISTORY, "Tell me about governance and the pentad")
    assert fresh["current_position"]["orientation"] == "new_territory"
    assert [jump["turn"] for jump in fresh["topic_jumps"]] == [2]
    assert fresh["turns_observed"] == 3
    assert sum(fresh["facet_occupancy"].values()) == 3


def test_awareness_empty_history_and_no_query() -> None:
    report = build_awareness_from_queries([], "")
    assert report["turns_observed"] == 0
    assert report["current_position"] == {"present": False}
    lone = build_awareness_from_queries([], "orbifold")
    assert lone["current_position"]["orientation"] == "new_territory"
    assert lone["current_position"]["nearest_turn"] is None


def test_session_awareness_is_read_only() -> None:
    session = MerlinSession()
    for query in HISTORY:
        session.turns.append({"query": query, "response": "r", "timestamp": "t"})
    before = repr(session.to_dict()) if hasattr(session, "to_dict") else repr(session.turns)
    report = build_session_awareness(session, "LiteBIRD birefringence angle")
    after = repr(session.to_dict()) if hasattr(session, "to_dict") else repr(session.turns)
    assert before == after
    assert report["read_only"] is True
    assert report["turns_observed"] == 3


# --- unitary lab ----------------------------------------------------------------------

def test_cayley_step_preserves_unitarity_along_subgradients() -> None:
    rng = np.random.default_rng(0)
    u = random_unitary(5, rng)
    a = rng.standard_normal((5, 9)) + 1j * rng.standard_normal((5, 9))
    b = rng.standard_normal((5, 9)) + 1j * rng.standard_normal((5, 9))
    for k in range(50):
        u = cayley_step(u, l1_clarke_subgradient(u, a, b), 0.5 / (k + 1))
    assert unitarity_residual(u) < 1e-12


def test_subgradient_is_zero_at_exact_fit() -> None:
    rng = np.random.default_rng(1)
    u = random_unitary(3, rng)
    a = rng.standard_normal((3, 4)) + 0j
    assert np.allclose(l1_clarke_subgradient(u, a, u @ a), 0.0)
    assert unitarity_residual(procrustes_fit(a, u @ a)) < 1e-12


def test_unitary_lab_l1_beats_procrustes_under_outliers() -> None:
    clean = run_unitary_lab(seed=0, outlier_fraction=0.0)
    assert clean["frobenius_procrustes"]["recovery_error"] < 0.05
    assert clean["l1_riemannian_subgradient"]["recovery_error"] < 0.05
    dirty = run_unitary_lab(seed=0, outlier_fraction=0.1)
    assert dirty["frobenius_procrustes"]["recovery_error"] > 0.5
    assert dirty["l1_riemannian_subgradient"]["recovery_error"] < 0.05
    assert dirty["l1_riemannian_subgradient"]["max_unitarity_residual_over_iterates"] < 1e-12
    assert dirty["eigenvalue_moduli_max_deviation"] < 1e-12


def test_unitary_lab_validates_and_sweeps() -> None:
    assert run_unitary_lab(n=1)["ok"] is False
    assert run_unitary_lab(n=4, samples=2)["ok"] is False
    assert run_unitary_lab(iterations=0)["ok"] is False
    sweep = run_unitary_lab_sweep(seeds=3, outlier_fractions=(0.1,), iterations=300)
    assert sweep["ok"] is True
    assert sweep["rows"][0]["frobenius_recovered"] == 0
    assert sweep["worst_unitarity_residual"] < 1e-12


# --- phase ISA golden vectors ---------------------------------------------------------

def test_golden_vectors_are_pinned() -> None:
    golden = geo.export_golden_vectors()
    assert golden["sha256"] == GOLDEN_SHA256
    assert golden["vector_count"] == 420
    assert golden["operand_bits"] == 7


def test_isa_semantics_match_geometry() -> None:
    assert geo.isa_phrot(73, 1) == 0
    assert geo.isa_phneg(5) == 69
    assert geo.isa_phneg(37) == 37
    assert geo.isa_phsub_mask(0, 0) == 0
    assert geo.isa_phsub_mask(0, 37) == 3
    assert geo.isa_phsub_mask(1, 0) == 1
    assert geo.isa_phsub_mask(0, 1) == 2
    for a in range(geo.LATTICE_ORDER):
        assert geo.isa_phrot(a, geo.isa_phneg(a)) == 0
        assert geo.isa_phneg(geo.isa_phneg(a)) == a


# --- tool + server surface ------------------------------------------------------------

def test_round_two_tools_registered_with_schemas() -> None:
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    for tool in ROUND_TWO_TOOLS:
        assert tool in names
        assert "args_schema" in names[tool]


def test_round_two_tools_route() -> None:
    session = MerlinSession()
    session.turns.append({"query": HISTORY[0]})
    awareness = route_tool("getMerlinToroidalAwareness", {"query": "birefringence braided winding"}, session=session)
    assert awareness["ok"] is True
    assert awareness["result"]["data"]["turns_observed"] == 1
    lab = route_tool("getMerlinUnitaryLab", {"n": 999, "iterations": 50}, session=session)
    assert lab["ok"] is True
    assert lab["result"]["data"]["config"]["n"] == 16
    assert route_tool("getMerlinPhaseIsaVectors", {})["result"]["data"]["sha256"] == GOLDEN_SHA256
    assert route_tool("getMerlinToroidalNavigation", {"top_k": 3})["ok"] is False


def test_server_exposes_round_two_endpoints() -> None:
    from ox_navigator.app.server import serve

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60.0) as client:
            awareness = client.get("/api/psicat/toroidal-awareness?query=orbifold+fold")
            assert awareness.status_code == 200
            assert awareness.json()["toroidal_awareness"]["read_only"] is True

            evaluation = client.get("/api/psicat/retrieval-eval")
            assert evaluation.status_code == 200
            assert evaluation.json()["retrieval_eval"]["best_by_mrr"] == "bm25"

            lab = client.get("/api/psicat/unitary-lab?n=3&iterations=100&seed=2&outlier_percent=0")
            assert lab.status_code == 200
            assert lab.json()["unitary_lab"]["config"]["n"] == 3
            assert client.get("/api/psicat/unitary-lab?n=x").status_code == 400

            isa = client.get("/api/psicat/phase-isa")
            assert isa.status_code == 200
            assert isa.json()["phase_isa"]["sha256"] == GOLDEN_SHA256
    finally:
        httpd.shutdown()
        httpd.server_close()
