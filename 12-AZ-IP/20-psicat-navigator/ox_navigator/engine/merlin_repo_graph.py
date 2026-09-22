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
_DOC_HEADING_RE = re.compile(r"^\s*#+\s+(.*)$", re.MULTILINE)
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


@lru_cache(maxsize=16)
def _candidate_files(max_files: int) -> tuple[Path, ...]:
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
    return tuple(unique[: max(1, min(int(max_files), 600))])


def _state_signature(files: List[Path]) -> tuple[tuple[str, int, int], ...]:
    signature: list[tuple[str, int, int]] = []
    for path in files:
        stat = path.stat()
        signature.append((path.relative_to(REPO_ROOT).as_posix(), int(stat.st_mtime_ns), int(stat.st_size)))
    return tuple(signature)


def _tokenize(*parts: str) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        for token in _TOKEN_RE.findall(part or ""):
            lowered = token.lower()
            tokens.add(lowered)
            tokens.update(piece for piece in re.split(r"[_./-]+", lowered) if piece)
    return tokens


def _python_record(path: Path) -> Dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="replace")
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
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * int(getattr(node, "level", 0) or 0)
                if node.module:
                    imports.append(f"{prefix}{node.module}")
                    imports.extend(
                        f"{prefix}{node.module}.{alias.name}"
                        for alias in node.names
                        if alias.name and alias.name != "*"
                    )
                else:
                    imports.extend(f"{prefix}{alias.name}" for alias in node.names if alias.name)
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
    text = path.read_text(encoding="utf-8", errors="replace")
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
    symbol_sets = {path: set(record.get("symbols") or []) for path, record in by_path.items()}
    token_sets = {path: set(record.get("tokens") or []) for path, record in by_path.items()}
    edges: List[Dict[str, Any]] = []
    known_paths = set(by_path)
    symbol_frequency: dict[str, int] = {}
    for symbols in symbol_sets.values():
        for symbol in symbols:
            symbol_frequency[symbol] = symbol_frequency.get(symbol, 0) + 1
    token_to_paths: dict[str, set[str]] = {}
    for path, tokens in token_sets.items():
        for token in tokens:
            token_to_paths.setdefault(token, set()).add(path)
    for record in by_path.values():
        for imported in list(record.get("imports") or []):
            candidate_targets: set[str] = set()
            if str(imported).startswith("."):
                level = len(str(imported)) - len(str(imported).lstrip("."))
                module = str(imported).lstrip(".")
                base = Path(str(record["path"])).parent
                for _ in range(max(level - 1, 0)):
                    base = base.parent
                if module:
                    module_path = module.replace(".", "/")
                    candidate_targets.add((base / f"{module_path}.py").as_posix())
                    candidate_targets.add((base / module_path / "__init__.py").as_posix())
                else:
                    candidate_targets.add((base / "__init__.py").as_posix())
            else:
                module_path = str(imported).replace(".", "/")
                candidate_targets.update(
                    path
                    for path in known_paths
                    if str(path).endswith(f"{module_path}.py") or str(path).endswith(f"{module_path}/__init__.py")
                )
            for candidate in candidate_targets:
                if candidate in known_paths:
                    edges.append(
                        {
                            "source": record["path"],
                            "target": candidate,
                            "relation": "imports",
                        }
                    )
        overlap_paths: set[str] = set()
        for symbol in symbol_sets[record["path"]]:
            if len(symbol) < 4 or symbol.startswith("__") or symbol_frequency.get(symbol, 0) > 8:
                continue
            overlap_paths.update(token_to_paths.get(symbol, set()))
        for other_path in overlap_paths:
            if other_path == record["path"]:
                continue
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
def _build_repo_graph_cached(max_files: int, state_signature: tuple[tuple[str, int, int], ...]) -> Dict[str, Any]:
    files = [REPO_ROOT / rel_path for rel_path, _mtime_ns, _size in state_signature]
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


def build_repo_graph(*, max_files: int = 180) -> Dict[str, Any]:
    """Build a bounded deterministic repository graph for routing."""
    files = list(_candidate_files(max_files=max_files))
    return _build_repo_graph_cached(max_files, _state_signature(files))


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
