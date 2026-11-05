# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Independent regression checks for bounded asset-lineage manifests."""

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import shutil
import uuid

import pytest

from src.infrastructure.data_lineage import (
    LINEAGE_SCHEMA_VERSION, LineageGraph, LineageNode, load_graph, save_graph,
)


def source(origin="real", **kwargs):
    return LineageNode.from_payload(
        b"source bytes", owner_scope="tenant", kind="source", origins=(origin,),
        rights_assertion="Caller asserts research rights",
        purpose_assertion="Research only", source="dataset:one", **kwargs,
    )


def derive(kind, *parents, origins=None):
    return LineageNode.from_payload(
        kind.encode(), owner_scope="tenant", kind=kind,
        origins=origins or tuple(sorted({o for p in parents for o in p.origins})),
        rights_assertion="Caller asserts derived use", purpose_assertion="Research",
        parent_ids=tuple(p.node_id for p in parents), transform="pipeline:v1",
        code_sha256=hashlib.sha256(b"code").hexdigest(),
        config_sha256=hashlib.sha256(b"config").hexdigest(),
    )


def lane():
    root = source()
    snapshot = derive("temporal_snapshot", root)
    features = derive("features", snapshot)
    artifact = derive("derived_artifact", features)
    model = derive("model", artifact)
    index = derive("index", model)
    return root, snapshot, features, artifact, model, index


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def test_independent_hashes_and_node_order():
    nodes = lane()
    graph = LineageGraph("tenant", nodes)
    for node in nodes:
        expected = hashlib.sha256(canonical({
            "schema_version": LINEAGE_SCHEMA_VERSION, **node.to_dict(),
        })).hexdigest()
        assert node.node_id == expected
    payload = json.loads(graph.to_json())
    graph_id = payload.pop("graph_id")
    assert graph_id == hashlib.sha256(canonical(payload)).hexdigest()
    assert graph.to_json() == LineageGraph("tenant", nodes[::-1]).to_json()
    assert source().payload_sha256 == hashlib.sha256(b"source bytes").hexdigest()
    assert source().verify_payload(b"source bytes")
    assert not source().verify_payload(b"other")


def test_immutable_and_metadata_identity():
    root = source()
    with pytest.raises(FrozenInstanceError):
        root.source = "changed"
    assert replace(root, rights_assertion="Different assertion").node_id != root.node_id
    assert replace(root, metadata=(("version", "1"),)).node_id != root.node_id
    assert replace(root, origins=("synthetic",)).node_id != root.node_id
    assert replace(root, owner_scope="other").node_id != root.node_id
    assert replace(root, purpose_assertion="Other purpose").node_id != root.node_id
    assert replace(root, source="other").node_id != root.node_id
    node = lane()[1]
    for field in ("code_sha256", "config_sha256", "payload_sha256"):
        assert replace(node, **{field: "0" * 64}).node_id != node.node_id


@pytest.mark.parametrize("change", [
    {"origins": ()}, {"origins": ("mixed",)}, {"origins": (True,)},
    {"origins": ("real", "real")}, {"rights_assertion": ""},
    {"purpose_assertion": " "}, {"source": ""}, {"payload_sha256": True},
    {"metadata": (("number", 1),)}, {"metadata": (("bool", True),)},
    {"metadata": (("nan", float("nan")),)}, {"metadata": (("inf", float("inf")),)},
    {"metadata": (("x", "1"), ("x", "2"))}, {"parent_ids": ("a" * 64,)},
    {"transform": "not a source"}, {"origins": ("real", "synthetic")},
])
def test_invalid_source_metadata(change):
    with pytest.raises(ValueError):
        replace(source(), **change)


def test_parent_scope_and_kind_checks():
    root, snapshot, features, *_ = lane()
    for nodes in ((root, root), (snapshot,), (root, features)):
        with pytest.raises(ValueError):
            LineageGraph("tenant", nodes)
    with pytest.raises(ValueError, match="owner_scope"):
        LineageGraph("other", (root,))
    with pytest.raises(ValueError, match="parent kind"):
        LineageGraph("tenant", (root, derive("model", root)))
    for change in ({"parent_ids": ()}, {"code_sha256": None},
                   {"config_sha256": None}, {"source": "claimed"},
                   {"parent_ids": (root.node_id, root.node_id)}):
        with pytest.raises(ValueError):
            replace(snapshot, **change)
    # A content-addressed cycle cannot normally be constructed without a hash
    # fixed point; dangling attempted backreferences still fail closed.
    with pytest.raises(ValueError, match="Unknown parent"):
        LineageGraph("tenant", (replace(features, parent_ids=("0" * 64,)),))


def test_origin_policy_and_explicit_mixture():
    real, synthetic = source(), source("synthetic")
    mislabeled = derive("temporal_snapshot", synthetic, origins=("real",))
    with pytest.raises(ValueError, match="origin policy"):
        LineageGraph("tenant", (synthetic, mislabeled))
    mixed = derive("temporal_snapshot", real, synthetic)
    features = derive("features", mixed)
    graph = LineageGraph("tenant", (real, synthetic, mixed, features))
    assert features.origins == ("real", "synthetic")
    assert not graph.receipt_eligible


def test_parent_and_metadata_order_are_canonical():
    first, second = source(), source("fallback")
    mixed = derive("temporal_snapshot", first, second)
    reordered = replace(
        mixed, parent_ids=tuple(reversed(mixed.parent_ids)),
        origins=tuple(reversed(mixed.origins)),
        metadata=(("z", "last"), ("a", "first")),
    )
    canonical_node = replace(mixed, metadata=(("a", "first"), ("z", "last")))
    assert reordered == canonical_node
    assert reordered.node_id == canonical_node.node_id
    assert LineageGraph("tenant", (first, second, mixed))


def test_cycle_detector_independently_of_sha_fixed_point(monkeypatch):
    # Inject deterministic IDs solely to exercise the cycle detector without
    # needing to solve a cryptographic fixed-point problem.
    left_id = hashlib.sha256(b"left").hexdigest()
    right_id = hashlib.sha256(b"right").hexdigest()
    base = derive("derived_artifact", lane()[2])
    left = replace(base, payload_sha256=left_id, parent_ids=(right_id,))
    right = replace(base, payload_sha256=right_id, parent_ids=(left_id,))
    monkeypatch.setattr(LineageNode, "node_id", property(lambda node: node.payload_sha256))
    with pytest.raises(ValueError, match="cycle"):
        LineageGraph("tenant", (left, right))


def test_direct_hash_is_only_an_assertion():
    claimed = replace(source(), payload_sha256="0" * 64)
    assert not claimed.verify_payload(b"source bytes")


def test_deletion_closure_is_advisory_and_branch_safe():
    nodes = lane()
    independent = replace(source(), source="dataset:independent")
    graph = LineageGraph("tenant", (*nodes, independent))
    plan = graph.affected_by_deletion((nodes[2].node_id,))
    assert set(plan.remove_ids) == {node.node_id for node in nodes[2:]}
    assert set(plan.retain_ids) == {node.node_id for node in (*nodes[:2], independent)}
    assert set(graph.descendants(nodes[0].node_id)) == {node.node_id for node in nodes[1:]}
    assert not plan.deletes_artifacts and not plan.claims_unlearning
    assert len(graph.nodes) == 7
    assert plan.graph_id == graph.content_hash
    with pytest.raises(ValueError):
        graph.affected_by_deletion(("0" * 64,))


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(schema_version="other"),
    lambda p: p.update(schema_version=True),
    lambda p: p.update(schema=LINEAGE_SCHEMA_VERSION),
    lambda p: p.update(unknown="field"),
    lambda p: p.update(receipt_eligible=True),
    lambda p: p.update(receipt_eligible=0),
    lambda p: p.update(graph_id="0" * 64),
    lambda p: p["nodes"][0].update(node_id="0" * 64),
    lambda p: p["nodes"][0].update(purpose_assertion="tampered"),
    lambda p: p["nodes"][0].update(unknown="field"),
])
def test_tampering_and_schema_rejected(mutation):
    payload = json.loads(LineageGraph("tenant", lane()).to_json())
    mutation(payload)
    with pytest.raises(ValueError):
        LineageGraph.from_json(json.dumps(payload))


def test_duplicate_json_and_nonfinite_rejected():
    text = LineageGraph("tenant", lane()).to_json()
    for damaged in (
        text.replace('{"graph_id":', '{"graph_id":"duplicate","graph_id":', 1),
        text.replace('"kind":"source"', '"kind":"source","kind":"source"'),
        text.replace('"metadata":[]', '"metadata":[["x",NaN]]', 1),
        text.replace('"metadata":[]', '"metadata":[["x",Infinity]]', 1),
    ):
        with pytest.raises(ValueError):
            LineageGraph.from_json(damaged)


def test_canonical_persistence_existing_directory_and_no_overwrite():
    directory = Path(__file__).parent / (".lineage-test-" + uuid.uuid4().hex)
    directory.mkdir()
    try:
        graph = LineageGraph("tenant", lane())
        path = save_graph(graph, directory)
        assert path.read_text() == graph.to_json()
        assert load_graph(path) == graph
        assert save_graph(graph, directory) == path
        path.write_text("tampered")
        with pytest.raises(ValueError):
            save_graph(graph, directory)
        with pytest.raises(ValueError):
            load_graph(path)
        with pytest.raises(FileNotFoundError):
            save_graph(graph, directory / "absent")
    finally:
        shutil.rmtree(directory)
