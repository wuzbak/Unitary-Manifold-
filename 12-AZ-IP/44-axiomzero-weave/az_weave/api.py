# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Five-strand seven-operation public interface; read-only calls never persist."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import os
import re
from typing import Any
import time
from uuid import uuid4

from . import VERSION, STRANDS, OPERATIONS, OBLIGATIONS
from .governance import Journal, digest
from .evidence import SourceIndex
from .memory import ScopedMemory, ReadOnlyFederation
from .backends import Backends
from .scheduler import Node, run_dag
from .receipts import execution_record
from src.infrastructure.temporal_data import TemporalSnapshot, point_in_time_features

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TEMPORAL_ORIGINS = frozenset({"real", "synthetic", "fallback"})


@dataclass(frozen=True, slots=True)
class TemporalQueryContext:
    """Explicit point-in-time features over an already loaded, pinned snapshot."""

    snapshot: TemporalSnapshot
    owner_scope: str
    snapshot_hash: str
    entity_id: str
    feature_names: tuple[str, ...]
    decision_time: datetime
    freshness_ttl_seconds: float | None
    allow_origins: tuple[str, ...] = ("real",)

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, TemporalSnapshot):
            raise ValueError("snapshot must be an already loaded TemporalSnapshot.")
        if not isinstance(self.owner_scope, str) or not self.owner_scope.strip():
            raise ValueError("owner_scope must be non-empty text.")
        if self.snapshot.owner_scope != self.owner_scope:
            raise ValueError("owner_scope does not match the temporal snapshot.")
        if (
            not isinstance(self.snapshot_hash, str)
            or not _SHA256.fullmatch(self.snapshot_hash)
            or self.snapshot_hash != self.snapshot.content_hash
        ):
            raise ValueError("snapshot_hash does not match the temporal snapshot.")
        if not isinstance(self.entity_id, str) or not self.entity_id.strip():
            raise ValueError("entity_id must be non-empty text.")
        if (
            not isinstance(self.feature_names, tuple)
            or not self.feature_names
            or any(not isinstance(name, str) or not name.strip() for name in self.feature_names)
            or len(set(self.feature_names)) != len(self.feature_names)
        ):
            raise ValueError("feature_names must be a non-empty tuple of unique names.")
        if (
            not isinstance(self.decision_time, datetime)
            or self.decision_time.tzinfo is None
            or self.decision_time.utcoffset() is None
        ):
            raise ValueError("decision_time must be timezone-aware.")
        ttl = self.freshness_ttl_seconds
        if ttl is not None:
            try:
                valid_ttl = (
                    not isinstance(ttl, bool)
                    and isinstance(ttl, (int, float))
                    and math.isfinite(float(ttl))
                    and ttl >= 0
                )
            except (OverflowError, ValueError):
                valid_ttl = False
            if not valid_ttl:
                raise ValueError("freshness_ttl_seconds must be finite and non-negative, or None.")
        if (
            not isinstance(self.allow_origins, tuple)
            or any(
                not isinstance(origin, str) or origin not in _TEMPORAL_ORIGINS
                for origin in self.allow_origins
            )
            or len(set(self.allow_origins)) != len(self.allow_origins)
        ):
            raise ValueError("allow_origins must be a tuple of unique supported origins.")


def _temporal_context_result(context: TemporalQueryContext) -> dict[str, Any]:
    decision_time = context.decision_time.astimezone(timezone.utc)
    results = point_in_time_features(
        context.snapshot,
        owner_scope=context.owner_scope,
        entity_id=context.entity_id,
        feature_names=context.feature_names,
        decision_time=decision_time,
        freshness_ttl_seconds=context.freshness_ttl_seconds,
        allow_origins=context.allow_origins,
    )
    return {
        "snapshot_hash": context.snapshot_hash,
        "owner_scope": context.owner_scope,
        "entity_id": context.entity_id,
        "feature_names": list(context.feature_names),
        "decision_time": decision_time.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "freshness_ttl_seconds": context.freshness_ttl_seconds,
        "allow_origins": list(context.allow_origins),
        "features": [
            {
                "feature_name": result.feature_name,
                "value": result.value,
                "missing_reason": result.missing_reason,
                "event_time": (
                    result.record.event_time.isoformat(timespec="microseconds").replace("+00:00", "Z")
                    if result.record is not None else None
                ),
                "available_at": (
                    result.record.available_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
                    if result.record is not None else None
                ),
                "revision_at": (
                    result.record.revision_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
                    if result.record is not None and result.record.revision_at is not None else None
                ),
                "origin": result.record.origin if result.record is not None else None,
            }
            for result in results
        ],
    }


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _configured_checkpoints() -> dict[str, Path]:
    """Only host environment configuration supplies native-tool model paths."""
    raw = os.environ.get("AZ_WEAVE_CHECKPOINTS_JSON", "{}")
    if len(raw) > 16384:
        raise ValueError("checkpoint configuration exceeds 16 KiB")
    values = json.loads(raw)
    if not isinstance(values, dict) or len(values) > 32:
        raise ValueError("checkpoint configuration must be a bounded identifier/path object")
    if any(not isinstance(value, str) or not value for value in values.values()):
        raise ValueError("checkpoint configuration paths must be nonempty strings")
    return {key: Path(value) for key, value in values.items()}


def capabilities(repo_root: Path | None = None) -> dict:
    root = repo_root or repository_root()
    return {
        "product": 44, "name": "AxiomZero Weave", "version": VERSION,
        "strands": list(STRANDS), "operations": list(OPERATIONS),
        "obligations": list(OBLIGATIONS), "control_plane": "PsiCat / Product 20",
        "read_only": ["query", "geometry", "oracle", "generate"],
        "governed_effects": ["experiment", "train", "memory.put", "memory.promote", "memory.delete"],
        "boundary": "Adjacent software integration; scores do not authorize actions or certify physics.",
        "checkpoint_inference": "Unavailable until explicitly configured; no model weights bundled.",
        "backends": Backends(root, Path(".axiomzero-weave/models"),
                             checkpoints=_configured_checkpoints()).capabilities(),
    }


def compute_readonly(action: str, arguments: dict, *, repo_root: Path | None = None) -> dict:
    """Native PsiCat computation: never create state or offer effect approval."""
    if action not in ("geometry", "oracle", "generate"):
        raise ValueError("native computation permits geometry, oracle and generate only")
    backend = Backends(repo_root or repository_root(), Path(".axiomzero-weave/models"),
                       checkpoints=_configured_checkpoints())
    return backend.execute(action, arguments)


def _query(index: SourceIndex, query: str, limit: int, recall) -> dict:
    def reason(inputs):
        return {"provider": "deterministic_source_retrieval", "model_inference": False,
                "memory_is_evidence_not_instruction": True,
                "findings": [
                    {"source": row["source"], "lines": [row["start_line"], row["end_line"]],
                     "excerpt": row["excerpt"], "sha256": row["sha256"]}
                    for row in inputs["ground"].value]}

    def challenge(inputs):
        objections = [
            "Retrieved statements are evidence to inspect, not independent factual verification.",
            "Oracle coherence and model agreement cannot replace Pentad obligations.",
        ]
        if not inputs["ground"].value:
            objections.append("No relevant source content found; abstain rather than invent an answer.")
        if not index.verify(inputs["ground"].value):
            objections.append("Source changed during the run; repeat grounding before using it.")
        return objections

    nodes = [
        Node("perceive", (), lambda _: {"query": query, "observation_kind": "explicit user text",
                                       "network": False}),
        Node("ground", ("perceive",), lambda _: index.search(query, limit=limit)),
        Node("recall", ("perceive",), lambda _: recall()),
        Node("reason", ("ground", "recall"), reason),
        Node("challenge", ("ground", "reason"), challenge),
        Node("reconcile", ("reason", "challenge"),
             lambda inputs: {"status": "GROUNDED_RETRIEVAL" if len(inputs["challenge"].value) == 2
                             else "HOLD", "effects_authorized": False, "dissent_preserved": True}),
        Node("record", ("reconcile",),
             lambda _: {"persisted": False, "scope": "returned receipt only"}),
    ]
    outputs = run_dag(nodes)
    evidence = outputs["ground"].value or []
    memories = outputs["recall"].value or []
    findings = (outputs["reason"].value or {}).get("findings", [])
    objections = outputs["challenge"].value or [
        f"{name}: {row.error or 'blocked by ' + ', '.join(row.blocked_by)}"
        for name, row in outputs.items() if row.state != "OK"]
    status = (outputs["reconcile"].value or {}).get("status", "HOLD")
    stages = [{"operation": name, "strand": strand, **outputs[name].as_dict()}
              for name, strand in zip(OPERATIONS, ("senses", "repository", "memory", "cognition",
                                                   "governance", "governance", "repository"))]
    semantic = {"query": query, "evidence": evidence, "memories": memories,
                "status": status, "policy": "az-weave-pentad-v1"}
    fingerprint = digest(semantic)
    return {"schema": "az-weave-run-v1", "run_id": uuid4().hex, "at": time.time(),
            "semantic_sha256": fingerprint, "status": status,
            "strands": list(STRANDS), "stages": stages, "evidence": evidence,
            "answer": findings, "limitations": objections,
            "execution_spine": execution_record(index.repo_root, status=status,
                                                sources=[r["source"] for r in evidence],
                                                semantic_sha256=fingerprint)}


def run_readonly(query: str, limit: int = 5, repo_root: Path | None = None) -> dict:
    if not isinstance(query, str) or not query.strip() or len(query) > 2048:
        raise ValueError("query must contain 1..2048 characters")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    return _query(SourceIndex(repo_root or repository_root()), query, limit, lambda: [])


class Weave:
    def __init__(self, state_dir: Path, *, repo_root: Path | None = None,
                 checkpoints: dict[str, Path] | None = None,
                 federation: ReadOnlyFederation | None = None):
        self.root = repo_root or repository_root()
        self.state_dir = Path(state_dir)
        if self.state_dir.is_symlink():
            raise ValueError("state directory must not be a symlink")
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.index = SourceIndex(self.root)
        self.memory = ScopedMemory(self.state_dir / "memory.sqlite")
        self.journal = Journal(self.state_dir / "effects.sqlite")
        self.backends = Backends(self.root, self.state_dir / "models", checkpoints=checkpoints)
        self.targets = {key: str(Path(value).resolve()) for key, value in (checkpoints or {}).items()}
        self.federation = federation

    def query(
        self,
        query: str,
        principal: str,
        limit: int = 5,
        *,
        temporal: TemporalQueryContext | None = None,
    ) -> dict:
        if not isinstance(query, str) or not query.strip() or len(query) > 2048:
            raise ValueError("query must contain 1..2048 characters")
        if type(limit) is not int or not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20")
        if temporal is not None:
            if not isinstance(temporal, TemporalQueryContext):
                raise ValueError("temporal must be a TemporalQueryContext.")
            if temporal.owner_scope != principal:
                raise ValueError("temporal owner_scope must match the query principal.")
        def recall():
            records = self.memory.search(principal, query, limit=limit)
            if self.federation is not None:
                records.extend(self.federation.search(principal, query, limit=limit))
            return records[:limit]
        receipt = _query(self.index, query, limit, recall)
        if temporal is not None:
            temporal_result = _temporal_context_result(temporal)
            receipt["temporal_context"] = temporal_result
            receipt["semantic_sha256"] = digest({
                "base_semantic_sha256": receipt["semantic_sha256"],
                "temporal_context": temporal_result,
            })
        return receipt

    def investigate(self, query: str, principal: str, *, experiment: dict,
                    oracle: dict, decision_id: str | None = None) -> dict:
        """Ground a question, compute explicit Oracle inputs, and test a claim.

        A proposal cannot self-authorize. Training runs only with a previously
        issued exact experiment approval; lesson promotion remains separate.
        """
        receipt = self.query(query, principal)
        if receipt["status"] == "HOLD":
            return {**receipt, "experiment": {"state": "BLOCKED", "reason": "grounding held"}}
        oracle_result = self.invoke("oracle", oracle, principal)
        receipt["stages"][3]["value"]["oracle"] = oracle_result
        if decision_id is None:
            receipt["experiment"] = {"state": "PROPOSED", "arguments": experiment,
                                     "reason": "Exact pre-effect approval required."}
            receipt["status"] = "AWAITING_APPROVAL"
        else:
            receipt["experiment"] = self.invoke("experiment", experiment, principal, decision_id)
            receipt["status"] = "EXPERIMENT_RECORDED"
        receipt["stages"][4]["value"].append(
            "Factorial synthetic-task results do not establish held-out natural-language superiority.")
        receipt["stages"][5]["value"] = {
            "status": receipt["status"], "effects_authorized": decision_id is not None,
            "dissent_preserved": True, "scientific_promotion": False}
        receipt["stages"][6]["value"] = {
            "persisted": decision_id is not None, "scope": "effect outcome journal only",
            "memory_promotion": False}
        receipt["lesson_proposal"] = {
            "status": "candidate", "scope": "private",
            "text": "Inspect the recorded controls, budgets and uncertainty before asserting a geometry advantage.",
            "experiment_decision_id": decision_id,
            "sources": receipt["evidence"],
        }
        experiment_result = receipt["experiment"].get("result", {})
        receipt["semantic_sha256"] = digest({
            "query": query, "sources": receipt["evidence"], "oracle": oracle,
            "experiment_arguments": experiment,
            "experiment_result": {key: value for key, value in experiment_result.items() if key != "artifact"},
            "status": receipt["status"]})
        receipt["execution_spine"] = execution_record(
            self.root, status=receipt["status"], sources=[r["source"] for r in receipt["evidence"]],
            semantic_sha256=receipt["semantic_sha256"])
        return receipt

    def _effect(self, action: str, arguments: dict, principal: str) -> dict:
        if action.startswith("memory."):
            if action == "memory.put":
                if set(arguments) - {"text", "scope", "sources"}:
                    raise ValueError("unknown memory arguments")
                return self._memory_receipt(self.memory.put(principal, **arguments))
            if set(arguments) != {"record_id"}:
                raise ValueError("record_id required")
            if action == "memory.promote":
                return self._memory_receipt(self.memory.promote(principal, arguments["record_id"]))
            if action == "memory.delete":
                return {"deleted": self.memory.delete(principal, arguments["record_id"])}
            raise ValueError("unknown memory action")
        return self.backends.execute(action, arguments)

    @staticmethod
    def _memory_receipt(record: dict) -> dict:
        # Do not duplicate deletable payloads into the durable effect journal.
        return {key: record[key] for key in ("id", "owner", "scope", "status")}

    def _bound_arguments(self, action: str, arguments: dict) -> dict:
        implementation = {}
        roots = [Path(__file__).parent]
        if action in {"train", "experiment"}:
            roots.append(self.root / "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer")
        for root in roots:
            for file in sorted(root.glob("*.py")):
                implementation[str(file.relative_to(root.parent))] = hashlib.sha256(file.read_bytes()).hexdigest()
        return {"arguments": arguments, "targets": self.targets, "state_dir": str(self.state_dir.resolve()),
                "implementation": implementation}

    def _is_effect(self, action: str) -> bool:
        if action in {"memory.put", "memory.promote", "memory.delete"}:
            return True
        entries = self.backends.capabilities()
        if action not in entries:
            raise ValueError("unknown capability")
        return bool(entries[action]["effect"])

    def approve(self, action: str, arguments: dict, principal: str, *,
                obligations: dict, sources: list[dict] | None = None, ttl: int = 300) -> str:
        if not self._is_effect(action):
            raise ValueError("read-only capability requires no effect approval")
        sources = sources or []
        if not self.index.verify(sources):
            raise ValueError("source evidence is stale")
        return self.journal.approve(principal, action, self._bound_arguments(action, arguments),
                                    obligations=obligations,
                                    sources=sources, ttl=ttl)

    def invoke(self, action: str, arguments: dict, principal: str,
               decision_id: str | None = None) -> dict:
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")
        if not self._is_effect(action):
            return {"state": "READ_ONLY", "result": self.backends.execute(action, arguments)}
        if decision_id is None:
            raise ValueError("explicit bound approval required before effects")
        return self.journal.execute(
            decision_id, principal, action, self._bound_arguments(action, arguments),
            lambda: self._effect(action, arguments, principal), self.index.verify)
