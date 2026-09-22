# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic local repository graph and context-routing helpers."""

from __future__ import annotations

import ast
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[4]
_TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]+")
_DOC_HEADING_RE = re.compile(r"^\s*#+\s+(.*)$")
_PRIORITY_PREFIXES = [
    "src/core/",
    "tests/",
    "proof/",
    "1-THEORY/",
    "docs/",
    "12-AZ-IP/20-psicat-navigator/",
    "src/consciousness/",
]


def _priority_key(path: Path) -> tuple[int, str]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    for index, prefix in enumerate(_PRIORITY_PREFIXES):
        if rel.startswith(prefix):
            return (index, rel)
    return (len(_PRIORITY_PREFIXES), rel)


def _candidate_files(max_files: int) -> List[Path]:
    pool: List[Path] = []
    for pattern in (
        "src/**/*.py",
        "src/**/*.md",
        "tests/**/*.py",
        "proof/**/*.py",
        "1-THEORY/**/*.md",
        "docs/**/*.md",
        "12-AZ-IP/20-psicat-navigator/**/*.py",
        "12-AZ-IP/20-psicat-navigator/**/*.md",
    ):
        pool.extend(REPO_ROOT.glob(pattern))
    unique = sorted({path.resolve() for path in pool if path.is_file()}, key=_priority_key)
    return unique[: max(1, min(int(max_files), 600))]


def _tokenize(*parts: str) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        for token in _TOKEN_RE.findall(part or ""):
            lowered = token.lower()
            tokens.add(lowered)
            tokens.update(piece for piece in re.split(r"[_./-]+", lowered) if piece)
    return tokens


def _python_record(path: Path) -> Dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    symbols: List[str] = []
    imports: List[str] = []
    rel = path.relative_to(REPO_ROOT).as_posix()
    syntax_error: str | None = None
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        syntax_error = f"{exc.msg} @ line {exc.lineno}"
    else:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append(node.name)
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
    return {
        "path": rel,
        "kind": "python",
        "symbols": sorted(set(symbols))[:40],
        "imports": sorted(set(imports))[:40],
        "headings": [],
        "tokens": sorted(_tokenize(rel, " ".join(symbols), " ".join(imports))),
        "parse_status": "syntax_error" if syntax_error else "ok",
        "syntax_error": syntax_error,
    }


def _markdown_record(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    headings = [match.group(1).strip() for match in _DOC_HEADING_RE.finditer(text)]
    rel = path.relative_to(REPO_ROOT).as_posix()
    return {
        "path": rel,
        "kind": "markdown",
        "symbols": [],
        "imports": [],
        "headings": headings[:40],
        "tokens": sorted(_tokenize(rel, " ".join(headings[:40]))),
    }


def _record_for(path: Path) -> Dict[str, Any]:
    if path.suffix == ".py":
        return _python_record(path)
    return _markdown_record(path)


def _edge_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_path = {record["path"]: record for record in records}
    edges: List[Dict[str, Any]] = []
    known_paths = set(by_path)
    for record in by_path.values():
        for imported in list(record.get("imports") or []):
            candidate = imported.replace(".", "/") + ".py"
            if candidate in known_paths:
                edges.append(
                    {
                        "source": record["path"],
                        "target": candidate,
                        "relation": "imports",
                    }
                )
        for other_path, other in by_path.items():
            if other_path == record["path"]:
                continue
            if set(record["symbols"]) & set(other["tokens"]):
                edges.append(
                    {
                        "source": record["path"],
                        "target": other_path,
                        "relation": "symbol_overlap",
                    }
                )
    deduped = {(edge["source"], edge["target"], edge["relation"]): edge for edge in edges}
    return list(deduped.values())


@lru_cache(maxsize=16)
def build_repo_graph(*, max_files: int = 180) -> Dict[str, Any]:
    """Build a bounded deterministic repository graph for routing."""
    files = _candidate_files(max_files=max_files)
    records = [_record_for(path) for path in files]
    edges = _edge_records(records)
    return {
        "ok": True,
        "graph_id": "psicat_local_repo_graph_v1",
        "nodes": records,
        "edges": edges,
        "summary": {
            "file_count": len(records),
            "edge_count": len(edges),
            "local_first": True,
            "deterministic": True,
            "max_files": max_files,
        },
        "guardrail": "Graph output is a routing aid for local repository navigation; it is not an epistemic truth source.",
    }


def route_context_via_repo_graph(query: str, *, max_hits: int = 8, max_files: int = 180) -> Dict[str, Any]:
    """Return deterministic file-routing suggestions before raw file reads."""
    graph = build_repo_graph(max_files=max_files)
    query_tokens = _tokenize(query)
    scored: List[Dict[str, Any]] = []
    for node in list(graph.get("nodes") or []):
        node_tokens = set(node.get("tokens") or [])
        overlap = len(query_tokens & node_tokens)
        if not overlap:
            continue
        score = round(overlap / max(len(query_tokens), 1), 4)
        scored.append(
            {
                "path": str(node["path"]),
                "kind": str(node["kind"]),
                "score": score,
                "matching_tokens": sorted(query_tokens & node_tokens)[:10],
                "symbols": list(node.get("symbols") or [])[:5],
                "headings": list(node.get("headings") or [])[:3],
            }
        )
    scored.sort(key=lambda item: (-float(item["score"]), item["path"]))
    hits = scored[: max(0, min(int(max_hits), 20))]
    return {
        "ok": True,
        "query": query,
        "mode": "deterministic_repo_graph_context_route",
        "graph_summary": dict(graph.get("summary") or {}),
        "suggested_files": hits,
        "next_step_policy": (
            "Prefer graph-guided file selection before broad raw file reads when working inside the local repository."
        ),
    }


__all__ = [
    "build_repo_graph",
    "route_context_via_repo_graph",
]
