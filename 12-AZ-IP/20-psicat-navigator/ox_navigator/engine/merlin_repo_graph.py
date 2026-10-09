# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic local repository graph and context-routing helpers."""

from __future__ import annotations

import ast
import os
import re
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[4]
_TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]+")
_DOC_HEADING_RE = re.compile(r"^\s*#+\s+(.*)$", re.MULTILINE)
_REQUEST_DISCOVERY: ContextVar[dict[str, Any] | None] = ContextVar("repo_graph_discovery", default=None)
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
    return _priority_key_cached(path, str(REPO_ROOT))


@lru_cache(maxsize=8192)
def _priority_key_cached(path: Path, root: str) -> tuple[int, str]:
    rel = path.relative_to(Path(root)).as_posix()
    for index, prefix in enumerate(_PRIORITY_PREFIXES):
        if rel.startswith(prefix):
            return (index, rel)
    return (len(_PRIORITY_PREFIXES), rel)


@contextmanager
def repo_graph_request():
    """Reuse discovery within a request, while checking directory and file freshness."""
    token = _REQUEST_DISCOVERY.set({})
    try:
        yield
    finally:
        _REQUEST_DISCOVERY.reset(token)


def _directory_signature(path: str) -> tuple[int, int, int]:
    stat = os.stat(path)
    return stat.st_ino, stat.st_mtime_ns, stat.st_ctime_ns


def _discover_files() -> tuple[Path, ...]:
    request = _REQUEST_DISCOVERY.get()
    if request and request.get("root") == str(REPO_ROOT):
        try:
            if all(_directory_signature(path) == signature for path, signature in request["directories"]):
                return request["files"]
        except OSError:
            pass
    pool: List[str] = []
    signatures = []
    reusable = True
    for relative, suffixes in (
        ("src", (".py", ".md")),
        ("tests", (".py",)),
        ("proof", (".py", ".md")),
        ("1-THEORY", (".md",)),
        ("docs", (".md",)),
        ("12-AZ-IP/20-psicat-navigator", (".py", ".md")),
    ):
        directories = [str(REPO_ROOT / relative)]
        while directories:
            directory = directories.pop()
            try:
                signature = _directory_signature(directory)
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if entry.is_symlink():
                            reusable = False
                        if entry.is_dir(follow_symlinks=False):
                            directories.append(entry.path)
                        elif entry.name.endswith(suffixes) and entry.is_file():
                            pool.append(str(Path(entry.path).resolve()) if entry.is_symlink() else entry.path)
                signatures.append((directory, signature))
            except OSError:
                reusable = False
                continue
    files = _discovery_layout_cached(tuple(sorted(set(pool))), str(REPO_ROOT))
    if request is not None:
        request.clear()
        if reusable:
            request.update(root=str(REPO_ROOT), directories=signatures, files=files)
    return files


@lru_cache(maxsize=4)
def _discovery_layout_cached(files: tuple[str, ...], root: str) -> tuple[Path, ...]:
    # Only immutable path metadata is reused; discovery and source stats stay fresh.
    return tuple(sorted((Path(path) for path in files), key=lambda path: _priority_key_cached(path, root)))


@lru_cache(maxsize=4)
def _file_layout_cached(
    files: tuple[Path, ...], root: str,
) -> tuple[tuple[Path, frozenset[str]], ...]:
    repo_root = Path(root)
    areas: dict[str, list[Path]] = {}
    relative_paths: dict[Path, str] = {}
    for path in files:
        rel = path.relative_to(repo_root).as_posix()
        relative_paths[path] = rel
        area = next((prefix for prefix in _PRIORITY_PREFIXES if rel.startswith(prefix)), None)
        if area is None:
            parts = Path(rel).parts
            area = "/".join(parts[:2] if parts[0] == "src" else parts[:1])
        areas.setdefault(area, []).append(path)
    def priority(path: Path) -> tuple[int, str]:
        rel = relative_paths[path]
        index = next(
            (index for index, prefix in enumerate(_PRIORITY_PREFIXES) if rel.startswith(prefix)),
            len(_PRIORITY_PREFIXES),
        )
        return index, rel

    groups = [sorted(group, key=priority) for group in areas.values()]
    groups.sort(key=lambda group: priority(group[0]))
    # Interleave areas before applying the cap, including within equal query scores.
    representative = [
        group[index]
        for index in range(max((len(group) for group in groups), default=0))
        for group in groups
        if index < len(group)
    ]
    return tuple((path, frozenset(_tokenize(relative_paths[path]))) for path in representative)


def _select_files(files: Iterable[Path], max_files: int, query: str = "") -> tuple[Path, ...]:
    # Discovery remains fresh; reuse only path metadata for an identical file set.
    representative = _file_layout_cached(tuple(files), str(REPO_ROOT))
    query_tokens = _tokenize(query)
    if query_tokens:
        representative = sorted(
            representative, key=lambda item: -len(query_tokens & item[1])
        )
    return tuple(path for path, _ in representative[: max(1, min(int(max_files), 600))])


def _candidate_files(max_files: int, query: str = "") -> tuple[Path, ...]:
    return _select_files(_discover_files(), max_files, query)


def _state_signature(files: List[Path]) -> tuple[tuple[str, int, int], ...]:
    signature: list[tuple[str, int, int]] = []
    for path in files:
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
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


def _python_record(path: Path) -> Dict[str, Any] | None:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None
    symbols: List[str] = []
    imports: List[str] = []
    rel = path.relative_to(REPO_ROOT).as_posix()
    syntax_error: str | None = None
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        syntax_error = f"{exc.msg} @ line {exc.lineno}"
    else:
        nodes = [tree]
        while nodes:
            node = nodes.pop()
            # Expressions cannot contain definition/import statements. Skipping
            # their literal data retains nested statement blocks without walking
            # every element of large embedded benchmark datasets.
            if isinstance(node, ast.expr):
                continue
            nodes.extend(ast.iter_child_nodes(node))
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


def _markdown_record(path: Path) -> Dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None
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


def _record_for(path: Path) -> Dict[str, Any] | None:
    if path.suffix == ".py":
        return _python_record(path)
    return _markdown_record(path)


@lru_cache(maxsize=1200)
def _record_for_cached(
    resolved_path: str, mtime_ns: int, size: int, root: str
) -> Dict[str, Any] | None:
    """Reuse records across subsets, with file identity and freshness in the key."""
    return _record_for(Path(resolved_path))


def _relative_import_candidates(source_path: str, imported: str) -> set[str]:
    level = len(str(imported)) - len(str(imported).lstrip("."))
    module = str(imported).lstrip(".")
    package_dir = Path(str(source_path)).parent
    for _ in range(max(level - 1, 0)):
        package_dir = package_dir.parent
    if not module:
        return {(package_dir / "__init__.py").as_posix()}
    module_path = module.replace(".", "/")
    return {
        (package_dir / f"{module_path}.py").as_posix(),
        (package_dir / module_path / "__init__.py").as_posix(),
    }


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
    module_to_paths: dict[str, set[str]] = {}
    for path in known_paths:
        if not path.endswith(".py"):
            continue
        module_paths = [path[:-3]]
        if path.endswith("/__init__.py"):
            module_paths.append(path[:-len("/__init__.py")])
        for module_path in module_paths:
            # Preserve suffix matching, including imports without a package prefix.
            for offset in range(len(module_path)):
                module_to_paths.setdefault(module_path[offset:], set()).add(path)
    for record in by_path.values():
        for imported in list(record.get("imports") or []):
            candidate_targets: set[str] = set()
            if str(imported).startswith("."):
                candidate_targets.update(_relative_import_candidates(str(record["path"]), str(imported)))
            else:
                module_path = str(imported).replace(".", "/")
                candidate_targets.update(module_to_paths.get(module_path, ()))
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
    return [deduped[key] for key in sorted(deduped)]


@lru_cache(maxsize=32)
def _build_repo_graph_cached(
    max_files: int, state_signature: tuple[tuple[str, int, int], ...], root: str
) -> Dict[str, Any]:
    records = [
        record
        for rel_path, mtime_ns, size in state_signature
        if (record := _record_for_cached(
            str((Path(root) / rel_path).resolve()), mtime_ns, size, root
        )) is not None
    ]
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
    return deepcopy(_build_repo_graph(max_files))


def _build_repo_graph(max_files: int, query: str = "") -> Dict[str, Any]:
    discovered = _discover_files()
    cap = max(1, min(int(max_files), 600))
    files = list(_select_files(discovered, cap, query))
    graph = _build_repo_graph_cached(cap, _state_signature(files), str(REPO_ROOT))
    return {
        **graph,
        "summary": {
            **graph["summary"],
            "total_discovered": len(discovered),
            "truncated": len(discovered) > len(files),
            "truncated_count": len(discovered) - len(files),
            "selection_mode": "query_path_priority" if query else "representative_area_sampling",
        },
    }


def route_context_via_repo_graph(query: str, *, max_hits: int = 8, max_files: int = 180) -> Dict[str, Any]:
    """Return deterministic file-routing suggestions before raw file reads."""
    graph = _build_repo_graph(max_files, query)
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
