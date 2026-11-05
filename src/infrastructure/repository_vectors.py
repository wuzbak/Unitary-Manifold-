# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Explicit, source-verified lexical-vector adapter for the existing RAG bot."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import TYPE_CHECKING

from .vector_index import (
    EmbeddingManifest, ExactVectorIndex, SearchHit, VectorDocument, corpus_content_identity,
)

if TYPE_CHECKING:
    from bot.rag_index import RAGIndex

PREPROCESSING_VERSION = "az_unicode_casefold_word_counts_v1"


class StaleCorpusError(ValueError):
    """Source bytes no longer match the reference generation."""


def _tokens(text: str) -> Counter[str]:
    return Counter(re.findall(r"\w+", text.casefold()))


def _source_path(root: Path, source: str) -> Path:
    if not isinstance(source, str):
        raise ValueError("Source must be a canonical repository-relative path")
    relative = PurePosixPath(source)
    if (
        not source or relative.is_absolute() or ".." in relative.parts
        or "\\" in source or relative.as_posix() != source
    ):
        raise ValueError("Source must be a canonical repository-relative path")
    path = root / source
    if not path.resolve().is_relative_to(root):
        raise ValueError("Source resolves outside the repository")
    return path


@dataclass(frozen=True)
class RepositoryVectorIndex:
    """A pinned word-count baseline, not a learned semantic embedding service."""

    index: ExactVectorIndex
    vocabulary: tuple[str, ...]
    source_identities: tuple[tuple[str, str], ...]
    repository_root: Path

    def search(self, query: str, *, owner_scope: str, top_k: int = 5) -> tuple[SearchHit, ...]:
        if owner_scope != self.index.manifest.owner_scope:
            raise ValueError("Requested owner_scope does not match the repository index")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be nonempty text")
        if type(top_k) is not int or top_k < 0:
            raise ValueError("top_k must be a non-negative integer")
        for source, expected_hash in self.source_identities:
            current = hashlib.sha256(_source_path(self.repository_root, source).read_bytes()).hexdigest()
            if current != expected_hash:
                raise StaleCorpusError(f"Source changed; rebuild a new generation: {source}")
        counts = _tokens(query)
        vector = tuple(float(counts.get(word, 0)) for word in self.vocabulary)
        if not any(vector):
            return ()
        hits = self.index.search(
            vector, query_manifest=self.index.manifest, owner_scope=owner_scope, top_k=top_k,
        )
        return tuple(hit for hit in hits if hit.score > 0)


def build_repository_vectors(
    rag_index: "RAGIndex",
    *,
    repo_root: str | Path,
    owner_scope: str,
    allowed_sources: tuple[str, ...],
    max_chunks: int = 128,
) -> RepositoryVectorIndex:
    """Adapt explicit RAG chunks after checking them against current source bytes.

    Transformed or obsolete chunks are rejected rather than relabeled as fresh
    citations. Only the explicit source allowlist can enter the new generation.
    """
    from bot.rag_index import RAGIndex

    if not isinstance(rag_index, RAGIndex):
        raise ValueError("rag_index must be the existing bot RAGIndex")
    if not isinstance(owner_scope, str) or not owner_scope.strip():
        raise ValueError("owner_scope must be nonempty text")
    if (
        not isinstance(allowed_sources, tuple) or not allowed_sources
        or any(not isinstance(source, str) for source in allowed_sources)
        or len(set(allowed_sources)) != len(allowed_sources)
    ):
        raise ValueError("allowed_sources must be a nonempty tuple of unique source paths")
    if type(max_chunks) is not int or max_chunks < 1:
        raise ValueError("max_chunks must be a positive integer")
    root = Path(repo_root).resolve()
    contents: dict[str, tuple[str, str]] = {}
    for source in allowed_sources:
        raw = _source_path(root, source).read_bytes()
        contents[source] = (raw.decode("utf-8"), hashlib.sha256(raw).hexdigest())
    chunks = [chunk for chunk in rag_index.chunks if chunk.source in contents]
    if not chunks or len(chunks) > max_chunks:
        raise ValueError("Selected RAG chunk count must be between 1 and max_chunks")
    if set(contents) - {chunk.source for chunk in chunks}:
        raise ValueError("Every allowed source must have at least one RAG chunk")
    vocabulary: set[str] = set()
    unique = {}
    for chunk in chunks:
        text, source_hash = contents[chunk.source]
        if not chunk.text or chunk.text not in text:
            raise StaleCorpusError(f"RAG chunk is stale or transformed: {chunk.source}")
        counts = _tokens(chunk.text)
        if not counts:
            raise ValueError("Every selected RAG chunk must contain searchable words")
        vocabulary.update(counts)
        identity = json.dumps(
            [chunk.source, chunk.title, chunk.text, chunk.governance_label],
            ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")
        document_id = hashlib.sha256(identity).hexdigest()
        unique[document_id] = (chunk, source_hash, counts)
    words = tuple(sorted(vocabulary))
    documents = tuple(
        VectorDocument(
            document_id=document_id,
            owner_scope=owner_scope,
            vector=tuple(float(counts.get(word, 0)) for word in words),
            evidence_path=chunk.source,
            source_hash=source_hash,
            citation_metadata={
                "title": chunk.title,
                "chunk_sha256": hashlib.sha256(chunk.text.encode("utf-8")).hexdigest(),
                "governance_label": chunk.governance_label,
                "citation_scope": "file and chunk identity; no entailment or line-number claim",
            },
        )
        for document_id, (chunk, source_hash, counts) in sorted(unique.items())
    )
    vocabulary_hash = hashlib.sha256(
        json.dumps(words, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
    ).hexdigest()
    manifest = EmbeddingManifest(
        model_revision=f"lexical-word-counts:{vocabulary_hash}",
        dimension=len(words),
        normalized=False,
        metric="cosine",
        corpus_snapshot_id=corpus_content_identity(documents),
        preprocessing_version=PREPROCESSING_VERSION,
        owner_scope=owner_scope,
    )
    return RepositoryVectorIndex(
        ExactVectorIndex(manifest, documents), words,
        tuple(sorted((source, identity[1]) for source, identity in contents.items())), root,
    )
