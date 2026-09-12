# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Shared execution-spine contract for governed artifacts, health checks, and
promotion metadata across repository products and adjacent execution lanes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

EXECUTION_SPINE_SCHEMA_VERSION = "um_execution_spine_v1"
DEFAULT_REPOSITORY = "wuzbak/Unitary-Manifold-"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _string_list(values: list[str] | tuple[str, ...] | None) -> list[str]:
    if values is None:
        return []
    return [str(value) for value in values if str(value).strip()]


def _json_dict(data: dict[str, Any] | None) -> dict[str, Any]:
    return dict(data or {})


def _sanitized_non_repo_marker(original: Path, resolved: Path) -> str:
    raw = original.as_posix() if not original.is_absolute() else resolved.as_posix()
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"NON_REPO_PATH::{original.name or resolved.name}::{digest}"


def _lexical_repo_relative(path: Path) -> str | None:
    collapsed: list[str] = []
    for part in path.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not collapsed:
                return None
            collapsed.pop()
            continue
        collapsed.append(part)
    return "/".join(collapsed)


def _canonicalize_repo_relative(lexical: str, repo_root: Path) -> str:
    candidate = repo_root / lexical
    if candidate.exists() or candidate.is_symlink():
        resolved = candidate.resolve(strict=False)
        try:
            return resolved.relative_to(repo_root).as_posix()
        except ValueError:
            return _sanitized_non_repo_marker(Path(lexical), resolved)
    return lexical


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off", ""}:
            return False
    return bool(value)


def _health_check_list(values: list[ExecutionSpineHealthCheck | dict[str, Any]] | tuple[ExecutionSpineHealthCheck | dict[str, Any], ...] | None) -> list[ExecutionSpineHealthCheck]:
    items: list[ExecutionSpineHealthCheck] = []
    for value in list(values or []):
        if isinstance(value, ExecutionSpineHealthCheck):
            items.append(value)
        elif isinstance(value, dict):
            items.append(ExecutionSpineHealthCheck.from_dict(value))
    return items


def repo_rel(path: str | Path, repo_root: Path, *, base_dir: str | Path | None = None) -> str:
    original = Path(path)
    repo_root_resolved = repo_root.resolve(strict=False)
    if not original.is_absolute():
        if base_dir is not None:
            base_dir_resolved = Path(base_dir).resolve(strict=False)
            try:
                base_dir_resolved.relative_to(repo_root_resolved)
            except ValueError:
                return _sanitized_non_repo_marker(original, base_dir_resolved / original)
            resolved = (base_dir_resolved / original).resolve(strict=False)
            try:
                lexical = resolved.relative_to(repo_root_resolved).as_posix()
                return _canonicalize_repo_relative(lexical, repo_root_resolved)
            except ValueError:
                return _sanitized_non_repo_marker(original, resolved)
        lexical = _lexical_repo_relative(original)
        if lexical is not None:
            return _canonicalize_repo_relative(lexical, repo_root_resolved)
        resolved = (repo_root_resolved / original).resolve(strict=False)
        return _sanitized_non_repo_marker(original, resolved)
    resolved = original.resolve(strict=False)
    try:
        lexical = resolved.relative_to(repo_root_resolved).as_posix()
        return _canonicalize_repo_relative(lexical, repo_root_resolved)
    except ValueError:
        return _sanitized_non_repo_marker(original, resolved)


@dataclass(frozen=True)
class ExecutionSpineHealthCheck:
    check_id: str
    passed: bool
    status: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "passed": _as_bool(self.passed),
            "status": self.status,
            "summary": self.summary,
            "details": _json_dict(self.details),
            "sources": _string_list(self.sources),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExecutionSpineHealthCheck":
        return cls(
            check_id=str(payload.get("check_id", "")),
            passed=_as_bool(payload.get("passed")),
            status=str(payload.get("status", "")),
            summary=str(payload.get("summary", "")),
            details=_json_dict(payload.get("details")),
            sources=_string_list(payload.get("sources")),
        )


@dataclass(frozen=True)
class ExecutionSpineRecord:
    surface_id: str
    surface_kind: str
    lane: str
    status: str
    summary: str
    repository: str = DEFAULT_REPOSITORY
    schema_version: str = EXECUTION_SPINE_SCHEMA_VERSION
    generated_at_utc: str | None = field(default_factory=_utcnow)
    canonical_paths: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    governance: dict[str, Any] = field(default_factory=dict)
    compatibility: dict[str, Any] = field(default_factory=dict)
    health_checks: list[ExecutionSpineHealthCheck] = field(default_factory=list)
    promotion: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "surface_id": self.surface_id,
            "surface_kind": self.surface_kind,
            "lane": self.lane,
            "status": self.status,
            "summary": self.summary,
            "repository": self.repository,
            "generated_at_utc": self.generated_at_utc,
            "canonical_paths": _string_list(self.canonical_paths),
            "sources": _string_list(self.sources),
            "governance": _json_dict(self.governance),
            "compatibility": _json_dict(self.compatibility),
            "health_checks": [item.to_dict() for item in self.health_checks],
            "promotion": _json_dict(self.promotion),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExecutionSpineRecord":
        kwargs: dict[str, Any] = {
            "schema_version": str(payload.get("schema_version", EXECUTION_SPINE_SCHEMA_VERSION)),
            "surface_id": str(payload.get("surface_id", "")),
            "surface_kind": str(payload.get("surface_kind", "")),
            "lane": str(payload.get("lane", "")),
            "status": str(payload.get("status", "")),
            "summary": str(payload.get("summary", "")),
            "repository": str(payload.get("repository", DEFAULT_REPOSITORY)),
            "canonical_paths": _string_list(payload.get("canonical_paths")),
            "sources": _string_list(payload.get("sources")),
            "governance": _json_dict(payload.get("governance")),
            "compatibility": _json_dict(payload.get("compatibility")),
            "health_checks": _health_check_list(payload.get("health_checks")),
            "promotion": _json_dict(payload.get("promotion")),
        }
        if "generated_at_utc" in payload:
            kwargs["generated_at_utc"] = payload.get("generated_at_utc")
        else:
            kwargs["generated_at_utc"] = None
        return cls(**kwargs)


def build_fail_closed_governance(
    *,
    epistemic_label: str,
    promotion_rule: str,
    fail_closed: bool = True,
    optional_backend: bool = False,
    compatibility_only: bool = False,
    residual_blockers: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    return {
        "epistemic_label": epistemic_label,
        "promotion_rule": promotion_rule,
        "fail_closed": bool(fail_closed),
        "optional_backend": bool(optional_backend),
        "compatibility_only": bool(compatibility_only),
        "residual_blockers": _string_list(residual_blockers),
    }
