# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
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

from ox_navigator.engine import merlin_toroidal_geometry as geo
from ox_navigator.engine.merlin_geometry_memory import _score_overlap
from ox_navigator.engine.merlin_kernel_routing import infer_runtime_kernel_id
from ox_navigator.engine.merlin_rag import KB_MATCH_THRESHOLD, best_kb_match, lookup_kb
from ox_navigator.engine.merlin_retrieval_scoring import (
    BM25Index,
    jaccard_overlap,
    token_list,
)
from ox_navigator.engine.merlin_router import (
    HEAVY_LANE_MIN_LENGTH,
    MEDIUM_LANE_MIN_LENGTH,
    classify_lane,
)
from ox_navigator.engine.merlin_toroidal_router import (
    build_toroidal_navigation_packet,
    evaluate_hybrid_state,
    shortest_graph_path,
    toroidal_rank,
    trace_hybrid_trajectory,
)

# --- lattice constants ------------------------------------------------------

def test_lattice_constants_follow_braid() -> None:
    assert geo.LATTICE_ORDER == 74 == 5 ** 2 + 7 ** 2
    assert geo.HALF_TURN == 37
    assert geo.PHASE_INDEX_BITS == 7
    assert geo.TICK_PHASE_STEP == 24  # 12/37 == 24/74
    assert geo.orbit_period(geo.TICK_PHASE_STEP) == 37
    assert geo.orbit_period(5) == geo.orbit_period(7) == 74


# --- metric and Clarke sets -------------------------------------------------

@pytest.mark.parametrize("a,b,expected", [(0, 0, 0), (0, 1, 1), (0, 73, 1), (0, 37, 37), (10, 50, 34)])
def test_circular_distance(a: int, b: int, expected: int) -> None:
    assert geo.circular_distance(a, b) == expected
    assert geo.circular_distance(b, a) == expected


def test_circular_distance_is_a_metric_on_the_lattice() -> None:
    for a in range(0, 74, 7):
        for b in range(0, 74, 5):
            for c in range(0, 74, 11):
                assert geo.circular_distance(a, c) <= geo.circular_distance(a, b) + geo.circular_distance(b, c)


def test_clarke_subdifferential_kinks() -> None:
    minimum = geo.circular_distance_subdifferential(5, 5)
    assert minimum["kind"] == "coincidence_minimum"
    assert minimum["clarke_gradient"] == [-1, 1] and minimum["is_minimum"]
    assert minimum["descent_directions"] == []
    cut = geo.circular_distance_subdifferential(5 + 37, 5)
    assert cut["kind"] == "cut_locus_maximum"
    assert cut["clarke_stationary"] and not cut["is_minimum"]
    assert cut["descent_directions"] == [-1, 1]
    smooth = geo.circular_distance_subdifferential(8, 5)
    assert smooth["kind"] == "smooth" and smooth["descent_directions"] == [-1]
    assert geo.circular_distance_subdifferential(2, 5)["descent_directions"] == [1]


def test_clarke_descent_direction_reduces_distance() -> None:
    for a in range(74):
        sub = geo.circular_distance_subdifferential(a, 0)
        for direction in sub["descent_directions"]:
            assert geo.circular_distance(a + direction, 0) < geo.circular_distance(a, 0)


def test_toroidal_geodesic_branches_at_cut_locus() -> None:
    result = geo.toroidal_geodesic([0, 0, 0], [37, 3, 70])
    assert result["displacement"] == [37, 3, -4]
    assert result["length"] == geo.toroidal_distance([0, 0, 0], [37, 3, 70]) == 44
    assert result["branch_coordinates"] == [0]
    assert result["geodesic_branch_count"] == 2
    with pytest.raises(ValueError):
        geo.toroidal_distance([0], [0, 1])


def test_braid_bank_is_balanced() -> None:
    counts = [0] * 74
    for a in range(74):
        for b in range(74):
            counts[geo.braid_bank([a, b])] += 1
    assert set(counts) == {74}
    with pytest.raises(ValueError):
        geo.braid_bank([1])


# --- exact unitary lattice operators -----------------------------------------

def test_lattice_operators_are_exactly_unitary() -> None:
    report = geo.verify_lattice_operators()
    assert report["shift_exactly_unitary"]
    assert report["reflection_exactly_unitary"]
    assert report["reflection_involution"]
    assert report["reflection_fixed_points"] == [0, 37]
    assert report["shift_order"] == 74
    assert report["weyl_commutation_residual"] < 1e-12


def test_shift_power_returns_identity_exactly() -> None:
    shift = geo.shift_operator(5)
    power = np.linalg.matrix_power(shift, 74)
    assert np.array_equal(power, np.eye(74, dtype=np.int64))
    assert shift.dtype == np.int64


# --- orbifold impacts and recurrence -----------------------------------------

def test_orbifold_fold_fundamental_domain() -> None:
    assert [geo.orbifold_fold(k) for k in (0, 1, 36, 37, 38, 73, 74, -1)] == [0, 1, 36, 37, 36, 1, 0, 1]


def test_orbifold_bounce_reflects_at_creases() -> None:
    result = geo.orbifold_bounce(30, 5, 10)
    assert result["positions"] == [30, 35, 34, 29, 24, 19, 14, 9, 4, 1, 6]
    assert result["impacts"] == [{"after_step": 2, "crease": 37}, {"after_step": 9, "crease": 0}]
    assert all(0 <= p <= 37 for p in result["positions"])
    backward = geo.orbifold_bounce(5, -5, 3)
    assert backward["impacts"] == [{"after_step": 1, "crease": 0}]
    landing = geo.orbifold_bounce(32, 5, 1)
    assert landing["impacts"] == [{"after_step": 1, "crease": 37}]
    with pytest.raises(ValueError):
        geo.orbifold_bounce(0, 1, -1)


def test_unitary_iteration_never_converges() -> None:
    report = geo.unitary_iteration_report(3, 5)
    assert report["period"] == 74 and report["distinct_states"] == 74
    assert report["converges"] is False
    assert geo.unitary_iteration_report(3, 0)["converges"] is True


def test_first_hitting_time_is_the_exit() -> None:
    hit = geo.first_hitting_time(0, 5, [25])
    assert hit == {"hit": True, "steps": 5, "facet": 25, "period": 74}
    # The 12/37 cadence only visits even phases; odd facets are unreachable.
    miss = geo.first_hitting_time(0, geo.TICK_PHASE_STEP, [1])
    assert miss["hit"] is False and miss["period"] == 37


# --- integer CORDIC ------------------------------------------------------------

def test_cordic_vector_phase_recovers_every_lattice_phase() -> None:
    for k in range(74):
        x = round(1000 * math.cos(2 * math.pi * k / 74))
        y = round(1000 * math.sin(2 * math.pi * k / 74))
        assert geo.cordic_vector_phase(x, y) == k
    assert geo.cordic_vector_phase(0, 0) == 0


def test_cordic_rotate_matches_float_rotation() -> None:
    angle = geo.phase_index_to_angle_fixed(10)
    x, y = geo.cordic_rotate(10000, 0, angle, iterations=20, frac_bits=19)
    theta = 2 * math.pi * 10 / 74
    assert abs(x - 10000 * math.cos(theta)) <= 3
    assert abs(y - 10000 * math.sin(theta)) <= 3


def test_cartesian_fixed_point_drifts_but_phase_lattice_is_exact() -> None:
    table = geo.quantization_error_table((8, 12, 16))
    errors = [row["relative_closure_error"] for row in table["rows"]]
    assert errors[0] > errors[1] > errors[2] > 0
    assert errors[2] < 0.01
    assert all(row["phase_lattice_closure_error"] == 0 for row in table["rows"])
    with pytest.raises(ValueError):
        geo.cordic_closure_drift(bits=3)


# --- phase sketch -----------------------------------------------------------------

def test_phase_sketch_is_deterministic_and_locality_sensitive() -> None:
    a = geo.phase_sketch(["kaluza", "klein", "winding", "number", "five", "birefringence"])
    again = geo.phase_sketch(reversed(["kaluza", "klein", "winding", "number", "five", "birefringence"]))
    near = geo.phase_sketch(["kaluza", "klein", "winding", "number", "seven", "birefringence"])
    far = geo.phase_sketch(["court", "sentencing", "reform", "justice", "equity"])
    assert a == again
    assert len(a["code"]) == geo.DEFAULT_SKETCH_DIMS
    assert all(0 <= c < 74 for c in a["code"])
    assert geo.sketch_similarity(a["code"], near["code"]) > geo.sketch_similarity(a["code"], far["code"])
    assert geo.sketch_similarity(a["code"], a["code"]) == 1.0
    assert geo.phase_sketch([])["empty"] is True
    with pytest.raises(ValueError):
        geo.phase_sketch(["x"], dims=1)


def test_geometry_report_is_labelled_adjacent() -> None:
    report = geo.get_toroidal_geometry_report()
    assert report["status"] == "ADJACENT_TRACK"
    assert "do not imply answer correctness" in report["claims_boundary"]


# --- shared retrieval scoring -----------------------------------------------------

def test_bm25_prefers_rare_matching_terms() -> None:
    docs = [token_list(t) for t in ("the the the winding", "birefringence litebird", "the court", "")]
    index = BM25Index(docs)
    ranked = index.rank(token_list("birefringence the"), top_k=3)
    assert ranked[0][0] == 1
    assert all(score > 0 for _, score in ranked)
    assert index.rank(token_list("absent"), top_k=3) == []


def test_shared_overlap_preserves_geometry_memory_scores() -> None:
    query = {"winding", "number"}
    assert _score_overlap(query, "winding number five") == round(2 / 3, 4)
    assert _score_overlap(set(), "anything") == 0.0
    assert jaccard_overlap(query, set()) == 0.0


def test_lookup_kb_threshold_refactor_is_behaviour_preserving() -> None:
    assert KB_MATCH_THRESHOLD == 0.15
    key, score = best_kb_match("Which pillar closes the Δm²₂₁ tension?")
    match = lookup_kb("Which pillar closes the Δm²₂₁ tension?")
    assert (match is not None) == (key is not None and score > KB_MATCH_THRESHOLD)
    assert best_kb_match("") == (None, 0.0)


# --- hybrid automaton router ------------------------------------------------------

def test_router_thresholds_are_named_and_unchanged() -> None:
    assert (MEDIUM_LANE_MIN_LENGTH, HEAVY_LANE_MIN_LENGTH) == (120, 350)
    assert classify_lane("x" * 120) == "small_fast_router"
    assert classify_lane("x" * 121) == "medium_reasoner_default"
    assert classify_lane("x" * 351) == "heavy_reasoner_exception"


@pytest.mark.parametrize("query", [
    "What is the winding number?",
    "x" * 125,
    "explain the full governance architecture and memory drift audit for proof tools",
    "y" * 360,
    "Resolve two trusted sources disagree on the lean theorem",
])
def test_hybrid_state_preserves_primary_decisions(query: str) -> None:
    state = evaluate_hybrid_state(query)
    lane = classify_lane(query)
    kernel = infer_runtime_kernel_id(lane=lane, query=query, context_source="grounded_retrieval")
    kb = "kb" if lookup_kb(query) else "no_kb"
    assert state["primary_facet"] == f"{lane}|{kernel}|{kb}"
    assert state["primary_facet"] in state["active_facets"]
    assert state["status"] == "ADJACENT_TRACK"


def test_hybrid_state_detects_length_crease() -> None:
    near = evaluate_hybrid_state("x" * 125, include_kb=False)
    assert near["on_crease"] and "lane_length_threshold" in near["creases"]
    assert near["reset_policy"] == "fuse_active_facet_contexts"
    assert set(near["lane"]["active"]) == {"small_fast_router", "medium_reasoner_default"}
    # The off-primary lane carries its own kernel (small lane routes to kernel_r).
    assert "small_fast_router|kernel_r|no_kb" in near["active_facets"]
    far = evaluate_hybrid_state("x" * 60, include_kb=False)
    assert not far["on_crease"] and far["reset_policy"] == "commit_primary_facet"
    assert far["active_facets"] == [far["primary_facet"]]


def test_hybrid_state_heavy_phrase_is_crisp() -> None:
    state = evaluate_hybrid_state("cross-source " + "z" * 340, include_kb=False)
    assert state["lane"]["active"] == ["heavy_reasoner_exception"]


def test_hybrid_state_kernel_tie_crease() -> None:
    query = "governance memory " + "q" * 110
    state = evaluate_hybrid_state(query, include_kb=False)
    assert state["kernel"]["score_driven"] is True
    assert state["kernel"]["tie_broken_by_priority"] is True
    assert "kernel_score_tie" in state["creases"]
    assert set(state["kernel"]["active"]) == {"kernel_a", "kernel_g"}


def test_trajectory_reports_jumps() -> None:
    trace = trace_hybrid_trajectory(["what is the winding number", "x" * 200], include_kb=False)
    assert len(trace["transitions"]) == 1
    assert trace["jump_count"] == 1
    assert trace_hybrid_trajectory(["a"], include_kb=False)["transitions"] == []


def test_toroidal_rank_reports_agreement_with_bm25() -> None:
    result = toroidal_rank(
        "birefringence litebird falsification",
        ["birefringence beta litebird falsifies braided winding", "court sentencing reform",
         "litebird launch 2032 cmb", "tensor ratio bicep"],
        top_k=2,
    )
    assert result["authority"] == "bm25"
    assert result["bm25"][0]["index"] == 0
    assert result["toroidal_sketch"][0]["index"] == 0
    assert 0.0 <= result["top_k_agreement"] <= 1.0


def test_shortest_graph_path_uses_relation_weights() -> None:
    edges = [
        {"source": "a", "target": "d", "relation": "symbol_overlap"},
        {"source": "d", "target": "c", "relation": "symbol_overlap"},
        {"source": "a", "target": "b", "relation": "imports"},
        {"source": "b", "target": "c", "relation": "imports"},
    ]
    result = shortest_graph_path(edges, "a", "c")
    assert result["found"] and result["path"] == ["a", "b", "c"] and result["cost"] == 2.0
    assert result["relations"] == ["imports", "imports"]
    assert shortest_graph_path(edges, "a", "zz")["found"] is False
    isolated = edges + [{"source": "x", "target": "y", "relation": "imports"}]
    assert shortest_graph_path(isolated, "a", "x")["reason"] == "no path"
    assert shortest_graph_path(edges, "a", "a")["cost"] == 0.0


def test_navigation_packet_includes_bm25_pillars() -> None:
    packet = build_toroidal_navigation_packet("Kaluza-Klein metric ansatz", top_k=3)
    assert len(packet["bm25_pillars"]) <= 3
    assert packet["bm25_pillars"]
    assert 0 <= packet["toroidal_address"]["bank"] < 74


# --- server surface -----------------------------------------------------------------

def test_server_exposes_toroidal_endpoints() -> None:
    from ox_navigator.app.server import serve

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=30.0) as client:
            geometry = client.get("/api/psicat/toroidal-geometry")
            assert geometry.status_code == 200
            assert geometry.json()["toroidal_geometry"]["lattice_order"] == 74

            navigation = client.get("/api/psicat/toroidal-navigation?query=winding+number+selection&top_k=3")
            assert navigation.status_code == 200
            assert navigation.json()["toroidal_navigation"]["primary_facet"]

            assert client.get("/api/psicat/toroidal-navigation").status_code == 400
            assert client.get("/api/psicat/toroidal-navigation?query=a&top_k=x").status_code == 400

            geodesic = client.get("/api/psicat/repo-geodesic?source=a.py&target=b.py&max_files=40")
            assert geodesic.status_code == 200
            assert geodesic.json()["repo_geodesic"]["found"] is False
            assert client.get("/api/psicat/repo-geodesic?source=a.py").status_code == 400
    finally:
        httpd.shutdown()
        httpd.server_close()


# --- opt-in crease fusion (additive; default OFF) -----------------------------------

def test_crease_fusion_default_off_leaves_scaffold_unchanged(monkeypatch) -> None:
    from ox_navigator.engine import merlin_rag

    monkeypatch.delenv(merlin_rag.TOROIDAL_CREASE_FUSION_FLAG, raising=False)
    assert merlin_rag.toroidal_crease_fusion_enabled() is False
    scaffold = merlin_rag.build_context_scaffold("x" * 125)
    assert "toroidal_crease" not in scaffold
    assert "[TOROIDAL CREASE]" not in merlin_rag.render_context_scaffold(scaffold)


def test_crease_fusion_flag_is_additive(monkeypatch) -> None:
    from ox_navigator.engine import merlin_rag

    query = "Kaluza-Klein metric ansatz " + "k" * 100  # length 127: lane crease
    monkeypatch.delenv(merlin_rag.TOROIDAL_CREASE_FUSION_FLAG, raising=False)
    baseline = merlin_rag.build_context_scaffold(query)
    monkeypatch.setenv(merlin_rag.TOROIDAL_CREASE_FUSION_FLAG, "1")
    fused = merlin_rag.build_context_scaffold(query)
    crease = fused.pop("toroidal_crease")
    assert fused == baseline  # every pre-existing field is identical
    assert crease["on_crease"] is True
    assert crease["reset_policy"] == "fuse_active_facet_contexts"
    baseline_ids = {str(p["id"]) for p in baseline["retrieval"]["pillars"]}
    fused_ids = [str(p["id"]) for p in crease["fused_pillars"]]
    assert not baseline_ids & set(fused_ids)
    assert len(fused_ids) == len(set(fused_ids))
    fused["toroidal_crease"] = crease
    assert "[TOROIDAL CREASE]" in merlin_rag.render_context_scaffold(fused)


def test_crease_fusion_off_crease_adds_no_pillars(monkeypatch) -> None:
    from ox_navigator.engine import merlin_rag

    monkeypatch.setenv(merlin_rag.TOROIDAL_CREASE_FUSION_FLAG, "true")
    scaffold = merlin_rag.build_context_scaffold("x" * 40)
    assert scaffold["toroidal_crease"]["on_crease"] is False
    assert scaffold["toroidal_crease"]["fused_pillars"] == []


def test_crease_fusion_appends_only_missing_bm25_pillars(monkeypatch) -> None:
    from ox_navigator.engine import merlin_rag, merlin_toroidal_router

    present = [merlin_rag.PILLAR_KNOWLEDGE[0]]
    missing = merlin_rag.PILLAR_KNOWLEDGE[1]
    monkeypatch.setattr(
        merlin_toroidal_router,
        "rank_pillars_bm25",
        lambda query, top_k=5: [{"id": present[0]["id"]}, {"id": missing["id"]}, {"id": "no-such-pillar"}],
    )
    block = merlin_rag._toroidal_crease_block("x" * 125, present, 5)
    assert block["on_crease"] is True
    assert block["fused_pillars"] == [missing]
