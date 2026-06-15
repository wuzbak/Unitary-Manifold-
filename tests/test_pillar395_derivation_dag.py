# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 395 — Derivation Graph Acyclicity.

Verifies DAG construction, cycle-detection correctness, topological ordering,
centrality ranking, and the machine-readable pillar status interface.

The critical test is test_derivation_dag_is_acyclic() — this is a hard gate
that must pass at every sprint.
"""

import json
import pytest

from src.core.pillar395_derivation_dag import (
    ClaimNode,
    DerivationDAG,
    _NODES,
    _EDGES,
    build_canonical_dag,
    pillar_395_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# DAG construction
# ──────────────────────────────────────────────────────────────────────────────

class TestDAGConstruction:

    def test_canonical_dag_builds(self):
        dag = build_canonical_dag()
        assert dag is not None

    def test_node_count_reasonable(self):
        dag = build_canonical_dag()
        assert dag.node_count >= 30, "DAG must have ≥30 nodes"

    def test_edge_count_reasonable(self):
        dag = build_canonical_dag()
        assert dag.edge_count >= 40, "DAG must have ≥40 edges"

    def test_all_nodes_present(self):
        dag = build_canonical_dag()
        for node in _NODES:
            assert node.name in dag.node_names, f"Node '{node.name}' missing from DAG"

    def test_edge_endpoints_in_dag(self):
        dag = build_canonical_dag()
        for child, parent in _EDGES:
            assert child in dag.node_names, f"Edge child '{child}' not in DAG"
            assert parent in dag.node_names, f"Edge parent '{parent}' not in DAG"

    def test_parents_of_postulate_empty(self):
        dag = build_canonical_dag()
        # Pure foundational postulates have no upstream dependencies.
        p1_name = "P1: Z₂ orbifold (S¹/Z₂)"
        if p1_name in dag.node_names:
            parents = dag.parents_of(p1_name)
            assert parents == [], f"P1 should have no upstream parents; found {parents}"

    def test_children_of_postulate_nonempty(self):
        dag = build_canonical_dag()
        p1_name = "P1: Z₂ orbifold (S¹/Z₂)"
        if p1_name in dag.node_names:
            children = dag.children_of(p1_name)
            assert len(children) >= 3, "P1 should have many downstream children"


# ──────────────────────────────────────────────────────────────────────────────
# ACYCLICITY — the critical gate
# ──────────────────────────────────────────────────────────────────────────────

class TestDAGAcyclicity:

    def test_derivation_dag_is_acyclic(self):
        """
        CRITICAL GATE — must pass at every sprint.

        Any cycle in the derivation graph is a logical error: it means at least
        one claim is circularly justified.  This test must never be removed.
        """
        dag = build_canonical_dag()
        cycles = dag.find_cycles()
        assert cycles == [], (
            f"Derivation DAG contains CYCLES — logical error: {cycles}"
        )

    def test_is_acyclic_method_returns_true(self):
        dag = build_canonical_dag()
        assert dag.is_acyclic() is True

    def test_topological_order_exists(self):
        dag = build_canonical_dag()
        order = dag.topological_order()
        assert order is not None, "Topological order must exist for an acyclic graph"

    def test_topological_order_length(self):
        dag = build_canonical_dag()
        order = dag.topological_order()
        assert order is not None
        assert len(order) == dag.node_count

    def test_postulates_before_derived_in_topo_order(self):
        dag = build_canonical_dag()
        order = dag.topological_order()
        assert order is not None

        # In topological order, every node's parents must appear before it.
        position = {name: i for i, name in enumerate(order)}
        for child, parent in _EDGES:
            if child in position and parent in position:
                assert position[parent] < position[child], (
                    f"Parent '{parent}' (pos {position[parent]}) appears after "
                    f"child '{child}' (pos {position[child]}) in topological order"
                )

    def test_synthetic_cycle_is_detected(self):
        """Verify the cycle-detection algorithm works on a known cyclic graph."""
        nodes = [
            ClaimNode("A", "DERIVED", "POSTULATED"),
            ClaimNode("B", "DERIVED", "POSTULATED"),
            ClaimNode("C", "DERIVED", "POSTULATED"),
        ]
        # Create cycle A → B → C → A
        edges = [("A", "B"), ("B", "C"), ("C", "A")]
        cyclic_dag = DerivationDAG(nodes=nodes, edges=edges)
        cycles = cyclic_dag.find_cycles()
        assert len(cycles) >= 1, "Cycle detector failed to find a known cycle"

    def test_acyclic_graph_has_no_cycles(self):
        """Verify cycle-detection returns empty list for an acyclic graph."""
        nodes = [
            ClaimNode("Root",   "POSTULATE", "POSTULATED"),
            ClaimNode("Middle", "DERIVED",   "DERIVED"),
            ClaimNode("Leaf",   "DERIVED",   "DERIVED"),
        ]
        edges = [("Middle", "Root"), ("Leaf", "Middle")]
        acyclic = DerivationDAG(nodes=nodes, edges=edges)
        assert acyclic.find_cycles() == []


# ──────────────────────────────────────────────────────────────────────────────
# Downstream and upstream reachability
# ──────────────────────────────────────────────────────────────────────────────

class TestReachability:

    def test_downstream_of_p1_large(self):
        dag = build_canonical_dag()
        p1 = "P1: Z₂ orbifold (S¹/Z₂)"
        if p1 in dag.node_names:
            ds = dag.downstream(p1)
            # P1 is the root postulate — almost everything depends on it.
            assert len(ds) >= 10, f"P1 downstream set too small: {len(ds)}"

    def test_downstream_of_leaf_empty(self):
        dag = build_canonical_dag()
        # A leaf node has no children.  Find one.
        leaf_candidates = [
            n for n in dag.node_names
            if len(dag.children_of(n)) == 0 and len(dag.parents_of(n)) > 0
        ]
        if leaf_candidates:
            leaf = leaf_candidates[0]
            ds = dag.downstream(leaf)
            assert ds == set(), f"Leaf '{leaf}' should have empty downstream set"

    def test_upstream_of_ns(self):
        dag = build_canonical_dag()
        ns_node = "nₛ=0.9635"
        if ns_node in dag.node_names:
            us = dag.upstream(ns_node)
            # nₛ depends on φ₀ bridge which depends on FTUM etc.
            assert len(us) >= 3, "nₛ should have ≥3 upstream ancestors"

    def test_downstream_disjoint_from_upstream(self):
        dag = build_canonical_dag()
        # If the graph is acyclic, downstream and upstream sets are disjoint.
        p1 = "P1: Z₂ orbifold (S¹/Z₂)"
        if p1 in dag.node_names:
            ds = dag.downstream(p1)
            us = dag.upstream(p1)
            overlap = ds & us
            assert overlap == set(), f"Cycle detected via overlap: {overlap}"


# ──────────────────────────────────────────────────────────────────────────────
# Centrality and sensitivity
# ──────────────────────────────────────────────────────────────────────────────

class TestCentrality:

    def test_centrality_ranking_nonempty(self):
        dag = build_canonical_dag()
        ranking = dag.centrality_ranking()
        assert len(ranking) > 0

    def test_centrality_ranking_sorted_descending(self):
        dag = build_canonical_dag()
        ranking = dag.centrality_ranking()
        counts = [count for _, count in ranking]
        assert counts == sorted(counts, reverse=True)

    def test_most_central_node_has_large_downstream(self):
        dag = build_canonical_dag()
        ranking = dag.centrality_ranking()
        top_name, top_count = ranking[0]
        assert top_count >= 5, f"Most central node has only {top_count} descendants"

    def test_postulate_sensitivity_ranking_nonempty(self):
        dag = build_canonical_dag()
        sens = dag.postulate_sensitivity_ranking()
        assert len(sens) >= 4

    def test_postulate_sensitivity_sorted_descending(self):
        dag = build_canonical_dag()
        sens = dag.postulate_sensitivity_ranking()
        counts = [c for _, c in sens]
        assert counts == sorted(counts, reverse=True)

    def test_most_critical_postulate_is_foundational(self):
        dag = build_canonical_dag()
        sens = dag.postulate_sensitivity_ranking()
        top_name, _ = sens[0]
        # The most critical postulate should be one of the foundational ones.
        foundational = ["P1", "P2", "P4", "P5", "Z₂", "orbifold", "FTUM", "Goldberger", "N_e"]
        assert any(f in top_name for f in foundational), (
            f"Expected foundational postulate at top of sensitivity ranking; got '{top_name}'"
        )

    def test_n_efolds_has_downstream_dependents(self):
        dag = build_canonical_dag()
        n_e = "N_e≈60 e-folds"
        if n_e in dag.node_names:
            ds = dag.downstream(n_e)
            assert len(ds) >= 2, "N_e≈60 should have at least nₛ and r as dependents"


# ──────────────────────────────────────────────────────────────────────────────
# JSON export
# ──────────────────────────────────────────────────────────────────────────────

class TestJSONExport:

    def test_json_export_valid(self):
        dag = build_canonical_dag()
        json_str = dag.to_json()
        data = json.loads(json_str)
        assert "node_count" in data
        assert "edge_count" in data
        assert "nodes" in data
        assert "edges" in data

    def test_json_node_count_matches(self):
        dag = build_canonical_dag()
        data = json.loads(dag.to_json())
        assert data["node_count"] == dag.node_count

    def test_json_edge_count_matches(self):
        dag = build_canonical_dag()
        data = json.loads(dag.to_json())
        assert data["edge_count"] == dag.edge_count

    def test_json_nodes_have_required_fields(self):
        dag = build_canonical_dag()
        data = json.loads(dag.to_json())
        for node in data["nodes"]:
            assert "name" in node
            assert "kind" in node
            assert "status" in node

    def test_json_edges_have_child_parent(self):
        dag = build_canonical_dag()
        data = json.loads(dag.to_json())
        for edge in data["edges"]:
            assert "child" in edge
            assert "parent" in edge


# ──────────────────────────────────────────────────────────────────────────────
# Full report
# ──────────────────────────────────────────────────────────────────────────────

class TestFullReport:

    def test_report_structure(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        required_keys = [
            "pillar", "title", "version", "node_count", "edge_count",
            "is_acyclic", "cycles_found", "most_central_node",
            "centrality_top5", "most_critical_postulate",
            "postulate_sensitivity_top5", "acyclicity_verdict",
        ]
        for key in required_keys:
            assert key in report, f"Missing '{key}' in full report"

    def test_report_pillar_number(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert report["pillar"] == 395

    def test_report_version(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert "12.9" in report["version"]

    def test_report_is_acyclic_true(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert report["is_acyclic"] is True

    def test_report_acyclicity_verdict_pass(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert report["acyclicity_verdict"] == "PASS"

    def test_report_no_cycles(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert report["cycles_found"] == []

    def test_report_centrality_top5_length(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert len(report["centrality_top5"]) == 5

    def test_report_topological_order_available(self):
        dag = build_canonical_dag()
        report = dag.full_report()
        assert report["topological_order_available"] is True


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status interface
# ──────────────────────────────────────────────────────────────────────────────

class TestPillarStatus:

    def test_status_returns_dict(self):
        status = pillar_395_status()
        assert isinstance(status, dict)

    def test_status_pillar_field(self):
        status = pillar_395_status()
        assert status["pillar"] == "395"

    def test_status_name_field(self):
        status = pillar_395_status()
        assert "DAG" in status["name"] or "Derivation" in status["name"]

    def test_status_is_acyclic_true(self):
        status = pillar_395_status()
        assert status["is_acyclic"] == "True"

    def test_status_cycles_zero(self):
        status = pillar_395_status()
        assert status["cycles_found"] == "0"

    def test_status_acyclicity_verdict_pass(self):
        status = pillar_395_status()
        assert status["acyclicity_verdict"] == "PASS"

    def test_status_node_count_numeric(self):
        status = pillar_395_status()
        assert int(status["node_count"]) >= 30

    def test_status_edge_count_numeric(self):
        status = pillar_395_status()
        assert int(status["edge_count"]) >= 40
