# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Source freshness, no-overlap, and existing RAG adapter acceptance tests."""

import hashlib

import pytest

from bot.rag_index import DocumentChunk, RAGIndex
from src.infrastructure.repository_vectors import StaleCorpusError, build_repository_vectors


def build(tmp_path, *, extra=()):
    (tmp_path / "geometry.md").write_text("Metric curvature geometry", encoding="utf-8")
    (tmp_path / "runtime.md").write_text("Serving cache runtime", encoding="utf-8")
    chunks = [
        DocumentChunk("geometry.md", "Geometry", "Metric curvature geometry"),
        DocumentChunk("runtime.md", "Runtime", "Serving cache runtime"),
        *extra,
    ]
    return build_repository_vectors(
        RAGIndex(chunks=chunks, knowledge_base={"fixture": True}), repo_root=tmp_path,
        owner_scope="project", allowed_sources=("geometry.md", "runtime.md"),
    )


def test_real_rag_chunk_contract_is_converted_without_semantic_model_claim(tmp_path):
    adapter = build(tmp_path)
    hits = adapter.search("serving cache", owner_scope="project")
    assert len(hits) == 1
    assert hits[0].document.evidence_path == "runtime.md"
    assert hits[0].document.source_hash == hashlib.sha256((tmp_path / "runtime.md").read_bytes()).hexdigest()
    assert adapter.index.manifest.model_revision.startswith("lexical-word-counts:")
    assert hits[0].document.citation_metadata["citation_scope"].startswith("file and chunk")
    assert adapter.search("unknownvocabulary", owner_scope="project") == ()


def test_changed_source_blocks_results_until_new_generation_is_built(tmp_path):
    adapter = build(tmp_path)
    (tmp_path / "runtime.md").write_text("Changed serving text", encoding="utf-8")
    with pytest.raises(StaleCorpusError, match="rebuild"):
        adapter.search("geometry", owner_scope="project")


def test_wrong_owner_and_invalid_topk_are_rejected_even_for_no_overlap(tmp_path):
    adapter = build(tmp_path)
    with pytest.raises(ValueError, match="owner_scope"):
        adapter.search("unknown", owner_scope="another")
    with pytest.raises(ValueError, match="top_k"):
        adapter.search("unknown", owner_scope="project", top_k=True)
    assert adapter.search("runtime", owner_scope="project", top_k=0) == ()


def test_stale_chunks_cannot_receive_current_source_hashes(tmp_path):
    (tmp_path / "source.md").write_text("new text", encoding="utf-8")
    rag = RAGIndex(
        chunks=[DocumentChunk("source.md", "Source", "old text")],
        knowledge_base={"fixture": True},
    )
    with pytest.raises(StaleCorpusError, match="stale or transformed"):
        build_repository_vectors(
            rag, repo_root=tmp_path, owner_scope="project", allowed_sources=("source.md",),
        )


def test_allowlist_excludes_other_chunks_and_is_not_a_path_escape(tmp_path):
    adapter = build(tmp_path, extra=(DocumentChunk("private.md", "Private", "secret serving"),))
    assert all(doc.evidence_path != "private.md" for doc in adapter.index.documents)
    with pytest.raises(ValueError, match="relative"):
        build_repository_vectors(
            RAGIndex(knowledge_base={"fixture": True}), repo_root=tmp_path,
            owner_scope="project", allowed_sources=("../escape.md",),
        )


def test_order_independent_generation_and_chunk_limit(tmp_path):
    first = build(tmp_path)
    second = build(tmp_path)
    assert first.index.generation_ref == second.index.generation_ref
    rag = RAGIndex(
        chunks=[DocumentChunk("runtime.md", "Runtime", "Serving cache runtime")],
        knowledge_base={"fixture": True},
    )
    with pytest.raises(ValueError, match="Every allowed source"):
        build_repository_vectors(
            rag, repo_root=tmp_path, owner_scope="project",
            allowed_sources=("runtime.md", "geometry.md"),
        )
    with pytest.raises(ValueError, match="max_chunks"):
        build_repository_vectors(
            rag, repo_root=tmp_path, owner_scope="project",
            allowed_sources=("runtime.md",), max_chunks=0,
        )


def test_program_documents_flow_from_real_rag_to_verified_vector_generation(tmp_path):
    source = "9-INFRASTRUCTURE/az-ml-program/README.md"
    path = tmp_path / source
    path.parent.mkdir(parents=True)
    path.write_text(
        "Checkpoint Adam PCG64 restoration remains local; distributed qualification is open.",
        encoding="utf-8",
    )
    rag = RAGIndex.build(repo_root=tmp_path)
    adapter = build_repository_vectors(
        rag, repo_root=tmp_path, owner_scope="ml-program", allowed_sources=(source,),
    )
    hits = adapter.search("checkpoint PCG64", owner_scope="ml-program")
    assert hits
    assert hits[0].document.evidence_path == source
    assert hits[0].document.source_hash == hashlib.sha256(path.read_bytes()).hexdigest()
    path.write_text("Corrected checkpoint evidence; no qualification.", encoding="utf-8")
    with pytest.raises(StaleCorpusError, match="rebuild"):
        adapter.search("checkpoint", owner_scope="ml-program")
    rebuilt = build_repository_vectors(
        RAGIndex.build(repo_root=tmp_path), repo_root=tmp_path, owner_scope="ml-program",
        allowed_sources=(source,),
    )
    assert rebuilt.index.generation_ref != adapter.index.generation_ref
    assert rebuilt.search("checkpoint", owner_scope="ml-program")
