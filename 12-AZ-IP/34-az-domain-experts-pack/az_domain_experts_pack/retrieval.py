# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Recursive, source-cited keyword retrieval over Python docstrings.

Source citations identify indexed repository text, not scientific validation.
"""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class DocChunk:
    """One retrievable unit: a module, function, or class docstring."""

    source_path: str
    symbol: str
    text: str
    relative_path: str
    start_line: int
    end_line: int
    source_sha256: str


_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_]+")


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)}


def _extract_chunks_from_file(path: Path, source_dir: Path) -> List[DocChunk]:
    try:
        source = path.read_bytes()
        tree = ast.parse(source.decode("utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return []

    relative_path = path.relative_to(source_dir).as_posix()
    module = ".".join(Path(relative_path).with_suffix("").parts)
    digest = hashlib.sha256(source).hexdigest()
    chunks: List[DocChunk] = []

    def visit(node: ast.AST, symbol: str) -> None:
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                expression = node.body[0]
                chunks.append(DocChunk(
                    source_path=str(path), symbol=symbol, text=doc,
                    relative_path=relative_path, start_line=expression.lineno,
                    end_line=expression.end_lineno, source_sha256=digest,
                ))
        for child in ast.iter_child_nodes(node):
            child_symbol = symbol
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                child_symbol = f"{symbol}.{child.name}"
            visit(child, child_symbol)

    visit(tree, module)
    return chunks


class DomainExpert:
    """A single-domain retrieval index built from one source directory."""

    def __init__(self, name: str, source_dir: Path) -> None:
        self.name = name
        self.source_dir = Path(source_dir).resolve()
        self._chunks: List[DocChunk] = []
        self._tokens: List[set[str]] = []
        self._built = False

    def build(self) -> int:
        """Index every ``*.py`` file under ``source_dir``. Returns the
        number of indexed chunks. Safe to call more than once (idempotent:
        re-running clears and rebuilds)."""
        self._chunks = []
        self._tokens = []
        if self.source_dir.is_dir():
            for path in sorted(self.source_dir.rglob("*.py")):
                if not path.resolve().is_relative_to(self.source_dir):
                    continue
                for chunk in _extract_chunks_from_file(path, self.source_dir):
                    self._chunks.append(chunk)
                    self._tokens.append(_tokenize(chunk.text) | _tokenize(chunk.symbol))
        self._built = True
        return len(self._chunks)

    def query(self, question: str, top_k: int = 3) -> List[dict]:
        """Return 1–50 source-cited chunks ranked by keyword overlap.

        Build lazily if needed; return no results when no keywords match.
        Citations refer to the file snapshot at the last build.
        """
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 50:
            raise ValueError("top_k must be an integer between 1 and 50")
        if not self._built:
            self.build()
        if not question.strip() or not self._chunks:
            return []
        q_tokens = _tokenize(question)
        if not q_tokens:
            return []

        scored = []
        for chunk, tokens in zip(self._chunks, self._tokens):
            overlap = len(q_tokens & tokens)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {
                "symbol": chunk.symbol, "text": chunk.text, "score": score,
                "source_path": chunk.source_path,
                "citation": {
                    "relative_path": chunk.relative_path,
                    "start_line": chunk.start_line, "end_line": chunk.end_line,
                    "source_sha256": chunk.source_sha256,
                },
            }
            for score, chunk in scored[:top_k]
        ]
