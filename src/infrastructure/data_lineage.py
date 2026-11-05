# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded asset-lineage DAGs, not an execution ledger or legal certification.

Source -> temporal_snapshot -> features -> derived_artifact/model/index is the
supported lane. Derived artifacts may also feed models and indexes; models may
feed indexes. Origins propagate as an exact union, including explicit mixtures.
Hashes supplied directly are assertions, not evidence of source authenticity;
``from_payload`` computes a digest of actual bytes and ``verify_payload`` checks
those bytes. Rights and purpose are caller assertions, not verified permissions.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import ClassVar

from .artifact_io import publish_immutable

LINEAGE_SCHEMA_VERSION = "um_data_lineage_v1"
_ORIGINS = frozenset({"real", "synthetic", "fallback"})
_PARENTS = {
    "source": frozenset(),
    "temporal_snapshot": frozenset({"source"}),
    "features": frozenset({"temporal_snapshot"}),
    "derived_artifact": frozenset({"features", "derived_artifact"}),
    "model": frozenset({"features", "derived_artifact"}),
    "index": frozenset({"features", "derived_artifact", "model"}),
}
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value


def _hash(value: object) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("Expected lowercase SHA256")
    return value


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sequence(value: object, name: str) -> tuple:
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{name} must be a tuple or list")
    return tuple(value)


def _fields(value: object, names: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError("Missing or unknown manifest fields")
    return value


@dataclass(frozen=True, slots=True)
class LineageNode:
    """Content-addressed node; optional metadata is deliberately text-only."""

    owner_scope: str
    kind: str
    payload_sha256: str
    origins: tuple[str, ...]
    rights_assertion: str
    purpose_assertion: str
    parent_ids: tuple[str, ...] = ()
    source: str | None = None
    transform: str | None = None
    code_sha256: str | None = None
    config_sha256: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for name in ("owner_scope", "rights_assertion", "purpose_assertion"):
            _text(getattr(self, name), name)
        if not isinstance(self.kind, str) or self.kind not in _PARENTS:
            raise ValueError("Unsupported node kind")
        _hash(self.payload_sha256)
        origins = _sequence(self.origins, "origins")
        if (not origins or any(not isinstance(x, str) or x not in _ORIGINS for x in origins)
                or len(set(origins)) != len(origins)):
            raise ValueError("Explicit unique real/synthetic/fallback origins required")
        parents = _sequence(self.parent_ids, "parent_ids")
        for parent in parents:
            _hash(parent)
        if len(set(parents)) != len(parents):
            raise ValueError("Duplicate parent IDs")
        if self.kind == "source":
            _text(self.source, "source")
            if parents or any(x is not None for x in
                              (self.transform, self.code_sha256, self.config_sha256)):
                raise ValueError("Source cannot have parents or transform identities")
            if len(origins) != 1:
                raise ValueError("Source must assert exactly one origin")
        else:
            if not parents or self.source is not None:
                raise ValueError("Derived nodes require parents, not a source")
            _text(self.transform, "transform")
            _hash(self.code_sha256)
            _hash(self.config_sha256)
        metadata = _sequence(self.metadata, "metadata")
        pairs = []
        for pair in metadata:
            pair = _sequence(pair, "metadata pair")
            if len(pair) != 2:
                raise ValueError("Metadata must contain text pairs")
            pairs.append((_text(pair[0], "metadata key"), _text(pair[1], "metadata value")))
        if len({key for key, _ in pairs}) != len(pairs):
            raise ValueError("Duplicate metadata key")
        object.__setattr__(self, "origins", tuple(sorted(origins)))
        object.__setattr__(self, "parent_ids", tuple(sorted(parents)))
        object.__setattr__(self, "metadata", tuple(sorted(pairs)))

    @classmethod
    def from_payload(cls, payload: bytes, **metadata: object) -> LineageNode:
        """Hash bytes locally; this does not authenticate their provenance."""
        if not isinstance(payload, bytes):
            raise ValueError("payload must be immutable bytes")
        return cls(payload_sha256=hashlib.sha256(payload).hexdigest(), **metadata)

    def verify_payload(self, payload: bytes) -> bool:
        if not isinstance(payload, bytes):
            raise ValueError("payload must be immutable bytes")
        return hashlib.sha256(payload).hexdigest() == self.payload_sha256

    def to_dict(self) -> dict:
        return {
            "owner_scope": self.owner_scope, "kind": self.kind,
            "payload_sha256": self.payload_sha256, "origins": list(self.origins),
            "rights_assertion": self.rights_assertion,
            "purpose_assertion": self.purpose_assertion,
            "parent_ids": list(self.parent_ids), "source": self.source,
            "transform": self.transform, "code_sha256": self.code_sha256,
            "config_sha256": self.config_sha256,
            "metadata": [list(pair) for pair in self.metadata],
        }

    @property
    def node_id(self) -> str:
        return _digest({"schema_version": LINEAGE_SCHEMA_VERSION, **self.to_dict()})


_NODE_FIELDS = {
    "owner_scope", "kind", "payload_sha256", "origins", "rights_assertion",
    "purpose_assertion", "parent_ids", "source", "transform", "code_sha256",
    "config_sha256", "metadata",
}


@dataclass(frozen=True, slots=True)
class RemovalPlan:
    """Advisory closure only: no files deleted and no model unlearning implied."""

    graph_id: str
    requested_ids: tuple[str, ...]
    remove_ids: tuple[str, ...]
    retain_ids: tuple[str, ...]
    deletes_artifacts: ClassVar[bool] = False
    claims_unlearning: ClassVar[bool] = False


@dataclass(frozen=True, slots=True)
class LineageGraph:
    """One owner, closed parent references, immutable canonical asset manifest."""

    owner_scope: str
    nodes: tuple[LineageNode, ...]
    schema_version: str = LINEAGE_SCHEMA_VERSION
    receipt_eligible: ClassVar[bool] = False

    def __post_init__(self) -> None:
        _text(self.owner_scope, "owner_scope")
        if self.schema_version != LINEAGE_SCHEMA_VERSION:
            raise ValueError("Unsupported lineage schema")
        nodes = _sequence(self.nodes, "nodes")
        if any(not isinstance(node, LineageNode) for node in nodes):
            raise ValueError("Expected LineageNode")
        by_id = {node.node_id: node for node in nodes}
        if len(by_id) != len(nodes):
            raise ValueError("Duplicate node IDs")
        for node in nodes:
            if node.owner_scope != self.owner_scope:
                raise ValueError("Node owner_scope mismatch")
            if any(parent not in by_id for parent in node.parent_ids):
                raise ValueError("Unknown parent")
            parents = [by_id[parent] for parent in node.parent_ids]
            if any(parent.kind not in _PARENTS[node.kind] for parent in parents):
                raise ValueError("Unsupported parent kind")
            if parents and set(node.origins) != {
                origin for parent in parents for origin in parent.origins
            }:
                raise ValueError("Derived origin policy must equal explicit parent origin union")
        # Iterative Kahn traversal avoids a recursion limit on long valid chains.
        pending = {key: len(node.parent_ids) for key, node in by_id.items()}
        children: dict[str, list[str]] = {key: [] for key in by_id}
        for key, node in by_id.items():
            for parent in node.parent_ids:
                children[parent].append(key)
        ready = [key for key, count in pending.items() if not count]
        visited = 0
        while ready:
            key = ready.pop()
            visited += 1
            for child in children[key]:
                pending[child] -= 1
                if not pending[child]:
                    ready.append(child)
        if visited != len(nodes):
            raise ValueError("Lineage cycle")
        object.__setattr__(self, "nodes", tuple(sorted(nodes, key=lambda node: node.node_id)))

    def _payload(self) -> dict:
        return {
            "schema_version": self.schema_version, "owner_scope": self.owner_scope,
            "receipt_eligible": False,
            "nodes": [{"node_id": node.node_id, **node.to_dict()} for node in self.nodes],
        }

    @property
    def content_hash(self) -> str:
        return _digest(self._payload())

    def to_json(self) -> str:
        return _canonical({"graph_id": self.content_hash, **self._payload()}).decode("utf-8")

    @classmethod
    def from_json(cls, text: str | bytes) -> LineageGraph:
        def unique(pairs: list) -> dict:
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate JSON key")
                result[key] = value
            return result

        def invalid(value: str) -> None:
            raise ValueError(f"Nonfinite JSON value: {value}")

        data = _fields(json.loads(text, object_pairs_hook=unique, parse_constant=invalid),
                       {"schema_version", "owner_scope", "receipt_eligible", "nodes", "graph_id"})
        if data["receipt_eligible"] is not False:
            raise ValueError("Lineage manifests are not receipt eligible")
        nodes = []
        for entry in _sequence(data["nodes"], "nodes"):
            entry = _fields(entry, _NODE_FIELDS | {"node_id"})
            node = LineageNode(**{key: entry[key] for key in _NODE_FIELDS})
            if _hash(entry["node_id"]) != node.node_id:
                raise ValueError("Node identity mismatch")
            nodes.append(node)
        graph = cls(data["owner_scope"], tuple(nodes), data["schema_version"])
        if _hash(data["graph_id"]) != graph.content_hash:
            raise ValueError("Graph identity mismatch")
        return graph

    def descendants(self, node_id: str) -> tuple[str, ...]:
        """Return transitive children, excluding the requested node."""
        return tuple(key for key in self.affected_by_deletion((node_id,)).remove_ids
                     if key != node_id)

    def affected_by_deletion(self, node_ids: tuple[str, ...]) -> RemovalPlan:
        requested = _sequence(node_ids, "node_ids")
        known = {node.node_id for node in self.nodes}
        if not requested or any(_hash(key) not in known for key in requested):
            raise ValueError("Removal requires known node IDs")
        if len(set(requested)) != len(requested):
            raise ValueError("Duplicate removal node IDs")
        children: dict[str, list[str]] = {key: [] for key in known}
        for node in self.nodes:
            for parent in node.parent_ids:
                children[parent].append(node.node_id)
        removed = set(requested)
        pending = list(requested)
        while pending:
            for child in children[pending.pop()]:
                if child not in removed:
                    removed.add(child)
                    pending.append(child)
        return RemovalPlan(self.content_hash, tuple(sorted(requested)),
                           tuple(sorted(removed)), tuple(sorted(known - removed)))


def save_graph(graph: LineageGraph, directory: str | Path) -> Path:
    """Publish into an existing directory, never overwrite different content."""
    if not isinstance(graph, LineageGraph):
        raise ValueError("Expected LineageGraph")
    return publish_immutable(directory, graph.content_hash, graph.to_json().encode("utf-8"))


def load_graph(path: str | Path) -> LineageGraph:
    """Verify embedded identities; a digest filename must also match its graph."""
    path = Path(path)
    graph = LineageGraph.from_json(path.read_bytes())
    if path.name != graph.content_hash + ".json":
        raise ValueError("Graph filename identity mismatch")
    return graph
