# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Sealed, local syntactic Python indexes; no execution or semantic resolution."""

from __future__ import annotations

import ast
import hashlib
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from .evidence import (
    EvidenceError,
    contained,
    file_hash,
    fingerprints,
    read_json,
    seal,
    verify_seal,
    write_json,
)

SCHEMA = "um-arts-code-index-v1"
QUERY_CAP = 1000
BOUNDARIES = [
    "Python AST facts only; source code is never imported or executed.",
    "Calls are unresolved syntactic targets, not a resolved cross-file call graph.",
    "No taint analysis, security certification, test-pass evidence or proof claims.",
    "Coverage is limited to fingerprinted canonical Python files and the byte bound.",
    "Declarations are classes and functions; qualified symbols are lexical scope labels.",
]
KINDS = {"files", "imports", "declarations", "calls"}


def _readonly(artifact: Path) -> tuple[sqlite3.Connection, dict]:
    verify_seal(artifact)
    metadata = read_json(contained(artifact, "code_index.json"))
    if not isinstance(metadata, dict) or metadata.get("schema_version") != SCHEMA:
        raise EvidenceError("Unsupported code index schema")
    path = contained(artifact, "code_index.sqlite3")
    db = None
    try:
        db = sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        if db.execute("PRAGMA user_version").fetchone()[0] != 1:
            raise EvidenceError("Unsupported SQLite code index schema")
        for table, columns in {
            "files": ["path", "sha256", "status", "error", "reused"],
            "facts": ["path", "kind", "name", "line", "qualified_symbol", "detail", "resolution"],
        }.items():
            if [row[1] for row in db.execute(f"PRAGMA table_info({table})")] != columns:
                raise EvidenceError("Invalid SQLite code index schema")
        db.row_factory = sqlite3.Row
        return db, metadata
    except sqlite3.Error as exc:
        if db is not None:
            db.close()
        raise EvidenceError(f"Unreadable SQLite code index: {exc}") from exc
    except BaseException:
        if db is not None:
            db.close()
        raise


def _target(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return ".".join([node.id, *reversed(parts)])
    return "<dynamic>"


class _Facts(ast.NodeVisitor):
    def __init__(self, db: sqlite3.Connection, path: str):
        self.db = db
        self.path = path
        self.scope = [path.removesuffix(".py").replace("/", ".")]

    def emit(self, kind, name, node, detail="", resolution="syntactic"):
        self.db.execute("INSERT INTO facts VALUES (?,?,?,?,?,?,?)", (
            self.path, kind, name, node.lineno, ".".join(self.scope), detail, resolution,
        ))

    def declaration(self, node):
        self.scope.append(node.name)
        self.emit("declarations", node.name, node,
                  type(node).__name__)
        self.scope.pop()
        # Decorators, bases and defaults execute in the enclosing scope, not the body.
        for field, value in ast.iter_fields(node):
            if field != "body":
                for child in value if isinstance(value, list) else [value]:
                    if isinstance(child, ast.AST):
                        self.visit(child)
        self.scope.append(node.name)
        for child in node.body:
            self.visit(child)
        self.scope.pop()

    visit_FunctionDef = declaration
    visit_AsyncFunctionDef = declaration
    visit_ClassDef = declaration

    def visit_Import(self, node):
        for item in node.names:
            self.emit("imports", item.name, node, item.asname or "")

    def visit_ImportFrom(self, node):
        module = "." * node.level + (node.module or "")
        for item in node.names:
            self.emit("imports", module + ("" if module.endswith(".") else ".") + item.name,
                      node, item.asname or "")

    def visit_Call(self, node):
        self.emit("calls", _target(node.func), node, type(node.func).__name__, "unresolved")
        self.generic_visit(node)


def _output(root: Path, output: Path) -> tuple[Path, Path]:
    output = output.absolute()
    if any(path.is_symlink() for path in [output, *output.parents]):
        raise EvidenceError("Artifact output may not traverse symlinks")
    output = output.resolve()
    if output.exists() or root.is_relative_to(output):
        raise EvidenceError("Use a new artifact directory, separate from the source root")
    store = root / ".um-arts" if output.is_relative_to(root) else output
    if output.is_relative_to(root) and (
        not output.is_relative_to(store) or output == store
    ):
        raise EvidenceError("In-source artifacts must be under the disclosed .um-arts store")
    return output, store


def build_index(root: Path, output: Path, previous: Path | None = None,
                max_file_bytes: int = 2 * 1024 * 1024) -> dict:
    """Create a new sealed index, streaming one bounded Python AST at a time."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise EvidenceError("Repository root does not exist")
    if isinstance(max_file_bytes, bool) or not isinstance(max_file_bytes, int) \
            or not 1 <= max_file_bytes <= 2 * 1024 * 1024:
        raise EvidenceError("File byte bound must be between 1 and 2 MiB")
    output, store = _output(root, Path(output))
    config = {
        "schema_version": SCHEMA, "max_file_bytes": max_file_bytes,
        "extraction_identity": {
            "code_sha256": file_hash(Path(__file__).resolve()), "python_version": sys.version,
        },
    }
    prior = None
    if previous is not None:
        if output.is_relative_to(Path(previous).resolve()):
            raise EvidenceError("New output may not be nested inside a previous sealed artifact")
        prior, metadata = _readonly(Path(previous).absolute())
        if metadata.get("status") not in {"indexed", "partial"}:
            prior.close()
            raise EvidenceError("Blocked previous indexes cannot supply reusable facts")
        if metadata.get("extraction_identity") != config["extraction_identity"]:
            prior.close()
            prior = None
    result = {
        **config, "root": str(root), "artifact": str(output), "store": str(store),
        "status": "blocked", "errors": [], "before": None, "after": None,
        "counts": {}, "boundaries": BOUNDARIES.copy(),
        "proof_claim": False, "security_certification": False,
    }
    try:
        output.mkdir(parents=True, exist_ok=False)
        with closing(sqlite3.connect(output / "code_index.sqlite3")) as db:
            db.executescript("""
                PRAGMA user_version=1;
                CREATE TABLE files (
                    path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, status TEXT NOT NULL,
                    error TEXT NOT NULL, reused INTEGER NOT NULL
                );
                CREATE TABLE facts (
                    path TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL,
                    line INTEGER NOT NULL, qualified_symbol TEXT NOT NULL,
                    detail TEXT NOT NULL, resolution TEXT NOT NULL
                );
                CREATE INDEX fact_query ON facts(kind, name, path, line);
                CREATE INDEX fact_path ON facts(path);
            """)
            before = None
            try:
                before = fingerprints(root, store, config)
                result["before"] = before["compatibility"]
                for relative, sha in before["source_files"].items():
                    if not relative.endswith(".py"):
                        continue
                    db.execute("INSERT INTO files VALUES (?,?,?,?,0)",
                               (relative, sha, "error", "not parsed"))
                    db.execute("SAVEPOINT file_facts")
                    status, error, reused = "parsed", "", 0
                    try:
                        path = contained(root, relative)
                        with path.open("rb") as stream:
                            data = stream.read(max_file_bytes + 1)
                        if len(data) > max_file_bytes:
                            status, error = "oversize", "file exceeds max_file_bytes"
                        elif hashlib.sha256(data).hexdigest() != sha:
                            status, error = "error", "source changed after fingerprint"
                            result["errors"].append(f"{relative}: source drift")
                        elif prior is not None and prior.execute(
                            "SELECT 1 FROM files WHERE path=? AND sha256=? AND status='parsed'",
                            (relative, sha),
                        ).fetchone():
                            db.executemany("INSERT INTO facts VALUES (?,?,?,?,?,?,?)",
                                           prior.execute("SELECT * FROM facts WHERE path=?",
                                                         (relative,)))
                            reused = 1
                        else:
                            _Facts(db, relative).visit(ast.parse(data, filename=relative))
                    except (OSError, EvidenceError, SyntaxError, UnicodeError, ValueError,
                            RecursionError, MemoryError) as exc:
                        db.execute("ROLLBACK TO file_facts")
                        detail = str(exc)[:512]
                        status = "error"
                        error = type(exc).__name__ + (f": {detail}" if detail else "")
                    db.execute("RELEASE file_facts")
                    db.execute("UPDATE files SET status=?, error=?, reused=? WHERE path=?",
                               (status, error, reused, relative))
                    db.commit()
                after = fingerprints(root, store, config)
                result["after"] = after["compatibility"]
                if before["compatibility"] != after["compatibility"]:
                    result["errors"].append("Source/environment/settings/engine/git drift")
            except (EvidenceError, OSError, RecursionError, MemoryError) as exc:
                result["errors"].append(
                    f"Fingerprint unavailable: {type(exc).__name__}: {str(exc)[:512]}")
            counts = result["counts"]
            counts["files"] = db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            for status in ["parsed", "oversize", "error"]:
                counts[status] = db.execute(
                    "SELECT COUNT(*) FROM files WHERE status=?", (status,)).fetchone()[0]
            counts["reused"] = db.execute(
                "SELECT COUNT(*) FROM files WHERE reused=1").fetchone()[0]
            counts["facts"] = db.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            for kind in ["imports", "declarations", "calls"]:
                counts[kind] = db.execute(
                    "SELECT COUNT(*) FROM facts WHERE kind=?", (kind,)).fetchone()[0]
            if before is not None and not result["errors"]:
                result["status"] = "partial" if counts["error"] or counts["oversize"] else "indexed"
        write_json(output / "code_index.json", result)
        seal(output)
        return result
    except sqlite3.Error as exc:
        raise EvidenceError(f"SQLite code index operation failed: {exc}") from exc
    finally:
        if prior is not None:
            prior.close()


def query_index(artifact: Path, kind: str = "calls", name: str = "",
                limit: int = 100) -> dict:
    """Query an enum-selected table with a parameterized exact-name filter."""
    if not isinstance(kind, str) or kind not in KINDS:
        raise EvidenceError("Unknown code index query kind")
    if not isinstance(name, str) or len(name) > 512:
        raise EvidenceError("Name filter must be at most 512 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise EvidenceError("Query limit must be a positive integer")
    limit = min(limit, QUERY_CAP)
    db, metadata = _readonly(Path(artifact).absolute())
    try:
        with closing(db):
            if metadata.get("status") == "blocked":
                rows = []
            elif kind == "files":
                rows = db.execute(
                    "SELECT * FROM files WHERE (?='' OR path=?) ORDER BY path LIMIT ?",
                    (name, name, limit + 1)).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM facts WHERE kind=? AND (?='' OR name=? OR qualified_symbol=?) "
                    "ORDER BY path,line,name LIMIT ?",
                    (kind, name, name, name, limit + 1)).fetchall()
    except sqlite3.Error as exc:
        raise EvidenceError(f"Unreadable SQLite code index query: {exc}") from exc
    return {
        "schema_version": SCHEMA, "status": metadata["status"], "kind": kind,
        "name": name, "limit": limit, "rows": [dict(row) for row in rows[:limit]],
        "truncated": len(rows) > limit, "counts": metadata["counts"],
        "errors": metadata["errors"], "boundaries": BOUNDARIES.copy(),
        "proof_claim": False, "security_certification": False,
    }
