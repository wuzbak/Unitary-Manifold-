# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Five-strand seven-operation public interface; read-only calls never persist."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
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


def capabilities(repo_root: Path | None = None, *, state_dir: Path | None = None,
                 checkpoints: dict[str, Path] | None = None) -> dict:
    root = repo_root or repository_root()
    return {
        "product": 44, "name": "AxiomZero Weave", "version": VERSION,
        "strands": list(STRANDS), "operations": list(OPERATIONS),
        "obligations": list(OBLIGATIONS), "control_plane": "PsiCat / Product 20",
        "read_only": ["query", "geometry", "oracle", "generate"],
        "governed_effects": ["experiment", "train", "memory.put", "memory.promote", "memory.delete"],
        "boundary": "Adjacent software integration; scores do not authorize actions or certify physics.",
        "checkpoint_inference": "Unavailable until explicitly configured; no model weights bundled.",
        "backends": Backends(root, (state_dir or Path(".axiomzero-weave")) / "models",
                             checkpoints=_configured_checkpoints() if checkpoints is None
                             else checkpoints).capabilities(),
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

    def query(self, query: str, principal: str, limit: int = 5) -> dict:
        if not isinstance(query, str) or not query.strip() or len(query) > 2048:
            raise ValueError("query must contain 1..2048 characters")
        if type(limit) is not int or not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20")
        def recall():
            records = self.memory.search(principal, query, limit=limit)
            if self.federation is not None:
                records.extend(self.federation.search(principal, query, limit=limit))
            return records[:limit]
        return _query(self.index, query, limit, recall)

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

    def _preflight(self, action: str, arguments: dict, principal: str) -> None:
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")
        if action.startswith("memory."):
            self.memory.preflight(action, principal, arguments)
        else:
            self.backends.preflight(action, arguments)

    def approve(self, action: str, arguments: dict, principal: str, *,
                obligations: dict, sources: list[dict] | None = None, ttl: int = 300) -> str:
        if not self._is_effect(action):
            raise ValueError("read-only capability requires no effect approval")
        self._preflight(action, arguments, principal)
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
        # A recorded success is replayed even if its output changed provider
        # availability or the checkpoint digest expected by a resume request.
        if self.journal.get(decision_id, principal)["state"] != "SUCCEEDED":
            self._preflight(action, arguments, principal)
        return self.journal.execute(
            decision_id, principal, action, self._bound_arguments(action, arguments),
            lambda: self._effect(action, arguments, principal), self.index.verify)
