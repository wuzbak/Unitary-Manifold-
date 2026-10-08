# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for the PhiCat Protocol golden-ratio braid-strand fusion (ADJACENT TRACK).

Covers: determinism, the golden-ratio strand-weight decay, the non-smooth
per-query strand-order assignment, the toroidal "gravity" weighting,
read-only (zero-network-call) frontier-capability reporting, opt-in
default-OFF non-regression of ``retrieve_context``, the
``evaluate_rankers(include_phicat=True)`` extension, the flag A/B harness,
and the tool/server wiring.
"""

from __future__ import annotations

import math
import sys
from itertools import pairwise
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_rag
from ox_navigator.engine.merlin_phicat_protocol import (
    GRAVITY_SCALE,
    PHI,
    STATUS_LABEL,
    STRAND_NAMES,
    frontier_capability_report,
    gravity_weight,
    phi_strand_weights,
    phicat_protocol_ranking,
    run_phicat_protocol,
    strand_order_for_query,
)
from ox_navigator.engine.merlin_retrieval_eval import (
    LABELLED_QUERIES,
    _pillar_tokens,
    evaluate_rankers,
)
from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool

# --- golden-ratio grounding --------------------------------------------------------------

def test_phi_is_the_golden_ratio() -> None:
    assert math.isclose(PHI, (1.0 + 5.0**0.5) / 2.0, rel_tol=1e-12)
    assert math.isclose(PHI * PHI, PHI + 1.0, rel_tol=1e-9)  # phi^2 = phi + 1, the defining identity


def test_phi_strand_weights_decay_by_golden_ratio_powers() -> None:
    weights = phi_strand_weights(STRAND_NAMES)
    ordered = [weights[name] for name in STRAND_NAMES]
    assert ordered[0] == 1.0
    for a, b in pairwise(ordered):
        assert math.isclose(a / b, PHI, rel_tol=1e-9)


# --- non-smooth, per-query strand ordering -----------------------------------------------

def test_strand_order_is_a_rotation_of_all_strand_names() -> None:
    order = strand_order_for_query([1, 2, 3, 4])
    assert sorted(order) == sorted(STRAND_NAMES)
    assert len(order) == len(STRAND_NAMES)


def test_strand_order_is_deterministic_for_same_code() -> None:
    assert strand_order_for_query([10, 20]) == strand_order_for_query([10, 20])


def test_strand_order_jumps_discontinuously_across_bank_boundary() -> None:
    # braid_bank = (5*a + 7*b) mod 74; crossing a multiple-of-4 residue flips
    # the whole rotation, not a smoothly interpolated weight.
    orders = {strand_order_for_query([a, 0]) for a in range(20)}
    assert len(orders) > 1


def test_strand_order_short_code_falls_back_to_default() -> None:
    assert strand_order_for_query([5]) == STRAND_NAMES
    assert strand_order_for_query([]) == STRAND_NAMES


# --- toroidal "gravity" weighting ---------------------------------------------------------

def test_gravity_weight_is_maximal_at_zero_distance() -> None:
    assert gravity_weight(0) == 1.0


def test_gravity_weight_decays_with_distance() -> None:
    near = gravity_weight(1)
    far = gravity_weight(50)
    assert near > far > 0.0


def test_gravity_weight_handles_zero_scale() -> None:
    assert gravity_weight(0, scale=0.0) == 1.0
    assert gravity_weight(5, scale=0.0) == 0.0


def test_gravity_scale_matches_lattice_quarter_circumference() -> None:
    from ox_navigator.engine.merlin_toroidal_geometry import LATTICE_ORDER

    assert GRAVITY_SCALE == LATTICE_ORDER / 4.0


# --- read-only frontier-capability reporting (no network calls) --------------------------

def test_frontier_capability_report_makes_no_network_calls() -> None:
    report = frontier_capability_report()
    assert report["network_calls_made"] == 0
    assert isinstance(report["frontier_strand_active"], bool)
    assert isinstance(report["available_providers"], list)


def test_frontier_capability_report_default_env_has_no_frontier_provider() -> None:
    report = frontier_capability_report()
    assert report["frontier_strand_active"] is False
    assert report["frontier_providers"] == []


# --- run_phicat_protocol / phicat_protocol_ranking: determinism and structure -------------

def test_run_phicat_protocol_is_deterministic() -> None:
    query = "Why is the winding number five and not seven?"
    first = run_phicat_protocol(query, top_k=5)
    second = run_phicat_protocol(query, top_k=5)
    assert first == second


def test_run_phicat_protocol_structure() -> None:
    report = run_phicat_protocol("Why is the winding number five and not seven?", top_k=5)
    assert report["status"] == STATUS_LABEL
    assert report["method"] == "phicat_protocol_v1"
    assert sorted(report["strand_order"]) == sorted(STRAND_NAMES)
    assert set(report["strand_weights"]) == set(STRAND_NAMES)
    assert 0 < len(report["fused"]) <= 5
    for row in report["fused"]:
        assert set(row["strand_contributions"]) <= set(STRAND_NAMES)
        assert row["toroidal_distance"] >= 0
    assert "frontier_capability" in report


def test_run_phicat_protocol_finds_the_labelled_pillar() -> None:
    report = run_phicat_protocol("Why is the winding number five and not seven?", top_k=5)
    assert any(row["id"] == 67 for row in report["fused"])


def test_phicat_protocol_ranking_covers_full_corpus() -> None:
    ids = [p.get("id") for p in merlin_rag.PILLAR_KNOWLEDGE]
    corpus_tokens = [_pillar_tokens(p) for p in merlin_rag.PILLAR_KNOWLEDGE]
    order = phicat_protocol_ranking("winding number", corpus_tokens, ids)
    assert sorted(order) == sorted(ids)


# --- evaluate_rankers(include_phicat=True) ------------------------------------------------

def test_evaluate_rankers_include_phicat_default_off_is_unchanged() -> None:
    without = evaluate_rankers()
    assert "phicat" not in without["rankers"]
    assert without["best_by_mrr"] == "bm25"


def test_evaluate_rankers_include_phicat_adds_measured_ranker() -> None:
    report = evaluate_rankers(include_phicat=True)
    assert report["query_count"] == len(LABELLED_QUERIES)
    assert "phicat" in report["rankers"]
    assert {"recall@1", "recall@5", "mrr", "ndcg@5"} <= set(report["summary"]["phicat"])
    assert 0.0 <= report["summary"]["phicat"]["mrr"] <= 1.0
    assert report["best_by_mrr"] in report["rankers"]


def test_evaluate_rankers_include_phicat_and_embedder_together() -> None:
    report = evaluate_rankers(include_embedder=True, include_phicat=True)
    assert {"jaccard", "bm25", "rrf", "embedder", "rrf_all", "phicat"} <= set(report["rankers"])


# --- opt-in pillar ranking flag (additive; default OFF) -----------------------------------

def test_phicat_protocol_default_off(monkeypatch) -> None:
    monkeypatch.delenv(merlin_rag.PHICAT_PROTOCOL_FLAG, raising=False)
    assert merlin_rag.phicat_protocol_enabled() is False


def test_phicat_protocol_flag_changes_order_only(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    for flag in (
        merlin_rag.BM25_PILLAR_RANKING_FLAG,
        merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG,
        merlin_rag.PHICAT_PROTOCOL_FLAG,
    ):
        monkeypatch.delenv(flag, raising=False)
    baseline = merlin_rag.retrieve_context(query, max_chunks=5)
    monkeypatch.setenv(merlin_rag.PHICAT_PROTOCOL_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    assert len(ranked["pillars"]) == len(baseline["pillars"]) == 5
    assert {k: v for k, v in ranked.items() if k != "pillars"} == {k: v for k, v in baseline.items() if k != "pillars"}


def test_phicat_protocol_flag_takes_precedence_over_other_flags(monkeypatch) -> None:
    query = "Why are the CMB acoustic peaks suppressed?"
    monkeypatch.setenv(merlin_rag.BM25_PILLAR_RANKING_FLAG, "1")
    monkeypatch.setenv(merlin_rag.SEMANTIC_EMBEDDER_RANKING_FLAG, "1")
    monkeypatch.setenv(merlin_rag.PHICAT_PROTOCOL_FLAG, "1")
    ranked = merlin_rag.retrieve_context(query, max_chunks=5)
    expected = merlin_rag._phicat_protocol_pillars(query, 5)
    assert [p["id"] for p in ranked["pillars"]] == [p["id"] for p in expected]


# --- flag A/B harness includes the new flag -----------------------------------------------

def test_flag_ab_opt_in_flags_include_phicat_protocol() -> None:
    from ox_navigator.engine.merlin_flag_ab import OPT_IN_FLAGS

    assert merlin_rag.PHICAT_PROTOCOL_FLAG in OPT_IN_FLAGS


# --- tool + server surface -----------------------------------------------------------------

def test_phicat_protocol_tool_registered_with_schema() -> None:
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    assert "getMerlinPhiCatProtocol" in names
    assert "args_schema" in names["getMerlinPhiCatProtocol"]


def test_phicat_protocol_tool_routes() -> None:
    result = route_tool("getMerlinPhiCatProtocol", {"query": "winding number five seven", "top_k": 3})
    assert result["ok"] is True
    assert result["result"]["data"]["status"] == STATUS_LABEL


def test_phicat_protocol_tool_requires_query() -> None:
    assert route_tool("getMerlinPhiCatProtocol", {"top_k": 3})["ok"] is False


def test_server_exposes_phicat_protocol_endpoint() -> None:
    import ox_navigator.app.server as server_module

    assert "/api/psicat/phicat-protocol" in Path(server_module.__file__).read_text(encoding="utf-8")
