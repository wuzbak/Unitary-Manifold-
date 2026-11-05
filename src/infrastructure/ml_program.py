# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Typed, offline planning inventory; not an ML runtime or execution authority."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from .execution_spine import (
    ExecutionSpineHealthCheck,
    ExecutionSpineRecord,
    build_fail_closed_governance,
)

SCHEMA_VERSION = "az_ml_program_v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "9-INFRASTRUCTURE/az-ml-program/capabilities.json"
STAGES = ("inventory", "baseline", "original", "integration", "validation")
STATUSES = ("planned", "in_progress", "blocked", "completed")
DOMAINS = ("inference", "agents_retrieval", "data", "assurance", "training_interop")
CAPABILITY_NAMES = (
    "Sub-4-bit quantization",
    "Serving with dynamic KV cache",
    "Dynamic batching",
    "Sparse CUDA kernels",
    "Distributed checkpoint storage",
    "Reflective-memory agent",
    "Vector indexing",
    "Self-healing RAG",
    "Safety and alignment evaluation",
    "Lossless tokenizer converter",
    "Serverless real-time feature store",
    "Domain synthetic data",
    "Prediction drift monitoring",
    "Data versioning and lineage",
    "Adversarial defenses",
    "Fairness audit",
    "GPU explainability",
    "Hardware profiler",
    "Modular reinforcement learning",
    "Model format translation",
    "Multimodal vector database",
)
NONCLAIMS = (
    "Inventory validation is not model training, inference, or algorithm delivery.",
    "No physics claim or hardgate promotion follows from this infrastructure.",
    "Dependency-ready means planning order only, not execution or deployment readiness.",
    "Existing source references are reuse candidates, not verified integrations.",
    "Test counts do not establish capability completion or readiness.",
    "Declared capability completion is not production certification.",
)
DEPENDENCY_SEMANTICS = (
    "Capability dependencies are integration/validation gates, not prerequisites for "
    "exploratory inventory or CPU stage work. Stage work may start through the execution "
    "board before full dependency completion. Declared completion is not production certification."
)


class ManifestError(ValueError):
    """Malformed or inconsistent planning inventory."""


@dataclass(frozen=True)
class Capability:
    id: int
    name: str
    domain: str
    stage: str
    status: str
    source_references: tuple[str, ...]
    dependencies: tuple[int, ...]
    external_prerequisites: tuple[str, ...]
    acceptance_gates: tuple[str, ...]
    next_action: str
    owner_role: str
    hardware_requirements: tuple[str, ...]
    baseline_adapters: tuple[str, ...]
    original_algorithm_goal: str
    nonclaim: str
    completion_evidence: tuple[str, ...]


@dataclass(frozen=True)
class Program:
    schema_version: str
    scope: str
    dependency_semantics: str
    nonclaims: tuple[str, ...]
    foundation_commands: tuple[tuple[str, str], ...]
    capabilities: tuple[Capability, ...]

    def status(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scope": self.scope,
            "dependency_semantics": self.dependency_semantics,
            "capability_count": len(self.capabilities),
            "status_counts": dict(sorted(Counter(c.status for c in self.capabilities).items())),
            "stage_counts": dict(sorted(Counter(c.stage for c in self.capabilities).items())),
            "foundation_commands": dict(self.foundation_commands),
            "foundation_command_scope": "Incremental inventory checks only; no capability completion command.",
            "capabilities": [asdict(c) for c in self.capabilities],
            "nonclaims": list(NONCLAIMS) + list(self.nonclaims),
        }

    def next_work(self) -> dict[str, Any]:
        completed = {c.id for c in self.capabilities if c.status == "completed"}
        candidates = []
        blocked = []
        for capability in self.capabilities:
            if capability.status == "completed":
                continue
            missing = sorted(set(capability.dependencies) - completed)
            if missing or capability.status == "blocked":
                blocked.append({
                    "id": capability.id,
                    "unfinished_dependencies": missing,
                    "explicitly_blocked": capability.status == "blocked",
                })
                continue
            candidates.append({
                "id": capability.id,
                "name": capability.name,
                "stage": capability.stage,
                "status": capability.status,
                "dependency_ready": True,
                "dependencies": list(capability.dependencies),
                "dependency_evidence_assessed": False,
                "execution_ready": False,
                "external_prerequisites": list(capability.external_prerequisites),
                "next_action": capability.next_action,
                "owner_role": capability.owner_role,
            })
        return {
            "scope": "dependency-ready capability integration/validation planning only",
            "dependency_semantics": self.dependency_semantics,
            "not_execution_ready": True,
            "candidates": candidates,
            "blocked": blocked,
            "nonclaims": list(NONCLAIMS),
        }

    def receipt(self) -> ExecutionSpineRecord:
        sources = sorted({p for c in self.capabilities for p in c.source_references})
        return ExecutionSpineRecord(
            surface_id="az-ml-program",
            surface_kind="capability_inventory_assessment",
            lane="non-hardgate-ml-infrastructure",
            status="inventory_validated",
            summary="All 21 ambitions inventoried; no model, backend, or deployment certified.",
            generated_at_utc=None,
            canonical_paths=["9-INFRASTRUCTURE/az-ml-program/capabilities.json"],
            sources=sources,
            governance=build_fail_closed_governance(
                epistemic_label="planning inventory, non-model, non-physics",
                promotion_rule="No promotion from inventory checks or test counts.",
                residual_blockers=[
                    "Capability-specific measured acceptance receipts are not assessed.",
                    "External prerequisites, host authority, and governance remain separate.",
                ],
            ),
            compatibility={
                "authority": "planning only; existing execution spine remains authoritative",
                "inventory": self.status(),
                "nonclaims": list(NONCLAIMS),
            },
            health_checks=[ExecutionSpineHealthCheck(
                check_id="az-ml-inventory-schema-and-dag",
                passed=True,
                status="inventory_only",
                summary="Schema, 21 identities, repository paths, and dependency DAG checked.",
                details={"model_evaluation_performed": False, "backend_probe_performed": False},
                sources=sources,
            )],
            promotion={
                "eligible": False,
                "reason": "An inventory assessment is not capability validation.",
                "model_claim": False,
                "physics_claim": False,
            },
        )


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be nonempty text")
    return value


def _texts(value: Any, label: str, *, empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not empty):
        raise ManifestError(f"{label} must be a {'possibly empty' if empty else 'nonempty'} list")
    result = tuple(_text(item, label) for item in value)
    if len(set(result)) != len(result):
        raise ManifestError(f"{label} must not contain duplicates")
    return result


def _paths(value: Any, label: str, root: Path, *, empty: bool = False) -> tuple[str, ...]:
    paths = _texts(value, label, empty=empty)
    for text in paths:
        path = PurePosixPath(text)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != text or "\\" in text:
            raise ManifestError(f"{label}: noncanonical repository path {text!r}")
        candidate = root / text
        if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
            raise ManifestError(f"{label}: missing or outside-repository source {text!r}")
    return paths


def validate_manifest(payload: Any, *, repo_root: Path = REPO_ROOT) -> Program:
    """Validate identities, field types, source paths, and DAG without probing backends."""
    data = _object(payload, "manifest")
    root = Path(repo_root).resolve()
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(f"schema_version must be {SCHEMA_VERSION!r}")
    scope = _text(data.get("scope"), "scope")
    dependency_semantics = _text(data.get("dependency_semantics"), "dependency_semantics")
    if dependency_semantics != DEPENDENCY_SEMANTICS:
        raise ManifestError(f"dependency_semantics must be {DEPENDENCY_SEMANTICS!r}")
    nonclaims = _texts(data.get("nonclaims"), "nonclaims")
    commands = _object(data.get("foundation_commands"), "foundation_commands")
    if not commands:
        raise ManifestError("foundation_commands must not be empty")
    command_pairs = tuple(sorted(
        (_text(key, "command name"), _text(value, "command"))
        for key, value in commands.items()
    ))
    items = data.get("capabilities")
    if not isinstance(items, list) or len(items) != 21:
        raise ManifestError("capabilities must contain exactly IDs 1..21 once")
    capabilities = []
    seen = set()
    for item in items:
        entry = _object(item, "capability")
        identifier = entry.get("id")
        if type(identifier) is not int or identifier not in range(1, 22) or identifier in seen:
            raise ManifestError("capabilities must contain exactly integer IDs 1..21 once")
        seen.add(identifier)
        label = f"capability {identifier}"
        name = _text(entry.get("name"), f"{label}.name")
        if name != CAPABILITY_NAMES[identifier - 1]:
            raise ManifestError(f"{label}.name must be {CAPABILITY_NAMES[identifier - 1]!r}")
        for key, allowed in (("domain", DOMAINS), ("stage", STAGES), ("status", STATUSES)):
            if entry.get(key) not in allowed:
                raise ManifestError(f"{label}.{key} must be one of {allowed}")
        deps = entry.get("dependencies")
        if not isinstance(deps, list) or any(type(d) is not int or d not in range(1, 22) for d in deps):
            raise ManifestError(f"{label}.dependencies must be known integer IDs")
        if identifier in deps or len(set(deps)) != len(deps):
            raise ManifestError(f"{label}.dependencies contains self or duplicate references")
        fields = {
            key: _texts(entry.get(key), f"{label}.{key}")
            for key in ("acceptance_gates", "hardware_requirements", "baseline_adapters")
        }
        fields["external_prerequisites"] = _texts(
            entry.get("external_prerequisites"), f"{label}.external_prerequisites", empty=True,
        )
        for key in ("next_action", "owner_role", "original_algorithm_goal", "nonclaim"):
            fields[key] = _text(entry.get(key), f"{label}.{key}")
        fields["source_references"] = _paths(entry.get("source_references"), f"{label}.source_references", root)
        fields["completion_evidence"] = _paths(
            entry.get("completion_evidence"), f"{label}.completion_evidence", root, empty=True,
        )
        if entry["status"] == "completed" and (entry["stage"] != "validation" or not fields["completion_evidence"]):
            raise ManifestError(f"{label}: completed requires validation stage and explicit evidence")
        capabilities.append(Capability(
            id=identifier, name=name, domain=entry["domain"], stage=entry["stage"],
            status=entry["status"], dependencies=tuple(sorted(deps)), **fields,
        ))
    by_id = {c.id: c for c in capabilities}
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(identifier: int) -> None:
        if identifier in visiting:
            raise ManifestError("dependencies contain a cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in by_id[identifier].dependencies:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in sorted(by_id):
        visit(identifier)
    for capability in capabilities:
        if capability.status == "completed" and any(
            by_id[dependency].status != "completed" for dependency in capability.dependencies
        ):
            raise ManifestError(f"capability {capability.id}: completed has unfinished dependencies")
    return Program(
        SCHEMA_VERSION, scope, dependency_semantics, nonclaims, command_pairs,
        tuple(sorted(capabilities, key=lambda c: c.id)),
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> Any:
    raise ManifestError(f"nonstandard JSON constant {value!r}")


def load_manifest(path: str | Path = DEFAULT_MANIFEST, *, repo_root: Path = REPO_ROOT) -> Program:
    try:
        payload = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object, parse_constant=_invalid_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Cannot load manifest: {exc}") from exc
    return validate_manifest(payload, repo_root=repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("command", choices=("check", "status", "next", "receipt"))
    args = parser.parse_args(argv)
    try:
        program = load_manifest(args.manifest)
    except ManifestError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    if args.command == "check":
        result = {
            "valid": True, "capability_count": 21, "schema_version": program.schema_version,
            "scope": "inventory only", "promotion_eligible": False,
        }
    elif args.command == "status":
        result = program.status()
    elif args.command == "next":
        result = program.next_work()
    else:
        result = program.receipt().to_dict()
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
