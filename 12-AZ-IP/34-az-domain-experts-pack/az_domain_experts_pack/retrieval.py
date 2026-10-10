# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Minimal retrieval index over a directory of Python modules.

Follows the architecture article-354 direction #7 names — "FastAPI plus
retrieval" — but scoped to the retrieval half: a domain-scoped index over a
source directory's module docstrings and top-level function/class
docstrings, with simple keyword-overlap scoring (the same proven, cheap
kind of scoring this repository already uses in several places, e.g.
`bot/rag_index.py`). A thin FastAPI layer following Terra/Lithos's own
pattern can be added on top of this index without changing its API.
"""

from __future__ import annotations

import ast
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


_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_]+")


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)}


def _extract_chunks_from_file(path: Path) -> List[DocChunk]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return []

    chunks: List[DocChunk] = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        chunks.append(DocChunk(source_path=str(path), symbol=path.stem, text=module_doc))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                chunks.append(
                    DocChunk(source_path=str(path), symbol=f"{path.stem}.{node.name}", text=doc)
                )
    return chunks


class DomainExpert:
    """A single-domain retrieval index built from one source directory."""

    def __init__(self, name: str, source_dir: Path) -> None:
        self.name = name
        self.source_dir = source_dir
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
            for path in sorted(self.source_dir.glob("*.py")):
                for chunk in _extract_chunks_from_file(path):
                    self._chunks.append(chunk)
                    self._tokens.append(_tokenize(chunk.text) | _tokenize(chunk.symbol))
        self._built = True
        return len(self._chunks)

    def query(self, question: str, top_k: int = 3) -> List[dict]:
        """Return up to ``top_k`` indexed chunks ranked by keyword overlap
        with ``question``. Returns an empty list if the index has not been
        built or no chunk shares any keyword with the question."""
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
            {"symbol": chunk.symbol, "text": chunk.text, "score": score, "source_path": chunk.source_path}
            for score, chunk in scored[:top_k]
        ]
