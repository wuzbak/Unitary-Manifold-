# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 3: structural awareness of repository documents.

Parses Markdown / YAML / TOML / JSON / CSV files already present in this
monorepo into a compact structural summary (headings, front-matter keys,
top-level keys, row/column counts) using only already-installed
dependencies (stdlib `tomllib`/`csv`/`json`, already-used `PyYAML`).

All paths are resolved and confined to the repository root -- this module
will never read a file outside the clone, which matters because PsiCat
calls this with caller-supplied path strings.
"""

from __future__ import annotations

import csv
import io
import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ._repo import repo_root

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only without PyYAML installed
    yaml = None  # type: ignore

_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

_SUPPORTED_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".toml", ".json", ".csv"}


class UnsupportedDocumentFormatError(ValueError):
    """Raised when a path is outside the repo, missing, or an unsupported type."""


@dataclass(frozen=True)
class DocumentInspection:
    path: str
    kind: str
    summary: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"path": self.path, "kind": self.kind, "summary": self.summary}


def _resolve_safe_repo_path(relative_path: str) -> Path:
    root = repo_root().resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise UnsupportedDocumentFormatError(
            f"path escapes the repository root: {relative_path!r}"
        ) from exc
    if not candidate.is_file():
        raise UnsupportedDocumentFormatError(f"not a file: {relative_path!r}")
    return candidate


def _inspect_markdown(text: str) -> Dict[str, Any]:
    front_matter: Optional[Dict[str, Any]] = None
    body = text
    match = _FRONT_MATTER_PATTERN.match(text)
    if match:
        body = text[match.end():]
        if yaml is not None:
            try:
                parsed = yaml.safe_load(match.group(1))
                if isinstance(parsed, dict):
                    front_matter = parsed
            except Exception:  # noqa: BLE001 - front matter may be non-YAML; degrade gracefully
                front_matter = None
    headings = []
    for line in body.splitlines():
        heading_match = _HEADING_PATTERN.match(line)
        if heading_match:
            headings.append({"level": len(heading_match.group(1)), "text": heading_match.group(2)})
    words = len(body.split())
    return {
        "headings": headings,
        "heading_count": len(headings),
        "front_matter_keys": sorted(front_matter.keys()) if front_matter else [],
        "word_count": words,
        "line_count": len(text.splitlines()),
    }


def _summarize_value(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {"type": "object", "top_level_keys": sorted(str(key) for key in value.keys())}
    if isinstance(value, list):
        return {"type": "array", "item_count": len(value)}
    return {"type": type(value).__name__}


def _inspect_yaml(text: str) -> Dict[str, Any]:
    if yaml is None:
        return {"error": "PyYAML is not installed in this environment", "line_count": len(text.splitlines())}
    documents = list(yaml.safe_load_all(text))
    if len(documents) == 1:
        return {"document_count": 1, **_summarize_value(documents[0])}
    return {"document_count": len(documents), "documents": [_summarize_value(doc) for doc in documents]}


def _inspect_toml(data: bytes) -> Dict[str, Any]:
    parsed = tomllib.loads(data.decode("utf-8"))
    return _summarize_value(parsed)


def _inspect_json(text: str) -> Dict[str, Any]:
    parsed = json.loads(text)
    return _summarize_value(parsed)


def _inspect_csv(text: str) -> Dict[str, Any]:
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    header = rows[0] if rows else []
    return {
        "header": header,
        "column_count": len(header),
        "row_count": max(len(rows) - 1, 0),
    }


def inspect_repository_document(relative_path: str) -> DocumentInspection:
    """Inspect one repository-relative document path and return its structure."""
    path = _resolve_safe_repo_path(relative_path)
    suffix = path.suffix.lower()
    if suffix not in _SUPPORTED_SUFFIXES:
        raise UnsupportedDocumentFormatError(f"unsupported document type: {suffix!r}")

    if suffix == ".toml":
        summary = _inspect_toml(path.read_bytes())
        kind = "toml"
    else:
        text = path.read_text(encoding="utf-8")
        if suffix in (".md", ".markdown"):
            summary = _inspect_markdown(text)
            kind = "markdown"
        elif suffix in (".yaml", ".yml"):
            summary = _inspect_yaml(text)
            kind = "yaml"
        elif suffix == ".json":
            summary = _inspect_json(text)
            kind = "json"
        else:
            summary = _inspect_csv(text)
            kind = "csv"

    return DocumentInspection(path=str(path.relative_to(repo_root().resolve())), kind=kind, summary=summary)
