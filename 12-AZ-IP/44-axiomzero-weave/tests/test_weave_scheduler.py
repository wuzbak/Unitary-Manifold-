# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Explicit dataflow, independent parallelism and failure propagation."""

from threading import Barrier
import pytest

from az_weave.scheduler import Node, run_dag


def test_actual_producer_output_reaches_consumer():
    outputs = run_dag([
        Node("repo.read", (), lambda _: {"evidence": "actual file bytes"}),
        Node("provenance", ("repo.read",), lambda rows: rows["repo.read"].value["evidence"]),
    ])
    assert outputs["provenance"].value == "actual file bytes"


def test_independent_nodes_overlap():
    barrier = Barrier(2)
    def worker(_):
        barrier.wait(timeout=5)
        return True
    result = run_dag([Node("one", (), worker), Node("two", (), worker)], max_workers=2)
    assert all(value.state == "OK" for value in result.values())


def test_failed_prerequisite_blocks_descendants():
    def fail(_):
        raise ValueError("unavailable source")
    outputs = run_dag([Node("source", (), fail),
                       Node("reason", ("source",), lambda _: pytest.fail("missing prerequisite")),
                       Node("record", ("reason",), lambda _: pytest.fail("missing reasoning"))])
    assert outputs["source"].state == "FAILED"
    assert outputs["reason"].blocked_by == ("source",)
    assert outputs["record"].blocked_by == ("reason",)
    assert "unavailable source" in outputs["source"].error


def test_consumers_cannot_mutate_another_consumers_evidence():
    def mutate(rows):
        rows["a"].value["text"] = "injected"
    outputs = run_dag([Node("a", (), lambda _: {"text": "source"}),
                       Node("b", ("a",), mutate),
                       Node("c", ("a",), lambda rows: rows["a"].value["text"])])
    assert outputs["c"].value == "source"
    assert outputs["a"].value == {"text": "source"}


@pytest.mark.parametrize("nodes", [
    [Node("a", ("a",), lambda _: None)],
    [Node("a", ("b",), lambda _: None)],
    [Node("a", (), lambda _: None), Node("a", (), lambda _: None)],
])
def test_bad_graph_rejected_before_workers(nodes):
    with pytest.raises(ValueError):
        run_dag(nodes)
