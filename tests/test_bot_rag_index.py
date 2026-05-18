# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for bot/rag_index.py — RAG Q&A endpoint."""
from __future__ import annotations

import pytest
from pathlib import Path

from bot.rag_index import (
    KNOWLEDGE_BASE,
    DocumentChunk,
    RAGIndex,
    answer_question,
    build_default_index,
    build_runtime_knowledge_base,
    retrieve_intent,
    build_intent_index,
)


# ---------------------------------------------------------------------------
# KNOWLEDGE_BASE
# ---------------------------------------------------------------------------

def test_knowledge_base_non_empty():
    assert len(KNOWLEDGE_BASE) > 0


def test_knowledge_base_structure():
    """Every KB entry must have topic, answer, sources, status."""
    for key, entry in KNOWLEDGE_BASE.items():
        assert "topic" in entry, f"Missing 'topic' in KB entry {key}"
        assert "answer" in entry, f"Missing 'answer' in KB entry {key}"
        assert "sources" in entry, f"Missing 'sources' in KB entry {key}"
        assert "status" in entry, f"Missing 'status' in KB entry {key}"


def test_knowledge_base_birefringence():
    assert "birefringence" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["birefringence"]
    assert "0.273" in entry["answer"] or "0.331" in entry["answer"]
    assert "LiteBIRD" in entry["answer"]


def test_knowledge_base_toe_score():
    assert "toe_score" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["toe_score"]
    assert "51" in entry["answer"] or "54" in entry["answer"] or "%" in entry["answer"]


def test_knowledge_base_alpha_gut():
    assert "alpha_gut" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["alpha_gut"]
    assert "5D SU" in entry["answer"] or "current closure path" in entry["answer"]


def test_knowledge_base_trusted_open_resources():
    assert "trusted_open_resources" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["trusted_open_resources"]
    assert "Pillar 258" in entry["topic"] or "Pillar 258" in entry["answer"]
    assert "100 trusted, free online research resources" in entry["answer"]


def test_runtime_knowledge_base_has_repo_state():
    kb = build_runtime_knowledge_base(Path(__file__).parent.parent)
    assert "repo_state" in kb
    assert "sources" in kb["repo_state"]


# ---------------------------------------------------------------------------
# DocumentChunk
# ---------------------------------------------------------------------------

def test_document_chunk_tokens():
    chunk = DocumentChunk("test.md", "Test", "Hello world physics")
    assert "hello" in chunk.tokens
    assert "world" in chunk.tokens
    assert "physics" in chunk.tokens


def test_document_chunk_score_perfect():
    chunk = DocumentChunk("test.md", "Test", "birefringence litebird prediction")
    query = {"birefringence", "litebird"}
    assert chunk.score(query) == 1.0


def test_document_chunk_score_zero():
    chunk = DocumentChunk("test.md", "Test", "hello world")
    query = {"birefringence", "alpha_s"}
    assert chunk.score(query) == 0.0


def test_document_chunk_score_empty_query():
    chunk = DocumentChunk("test.md", "Test", "some text")
    assert chunk.score(set()) == 0.0


def test_document_chunk_score_partial():
    chunk = DocumentChunk("test.md", "Test", "birefringence alpha_s prediction")
    query = {"birefringence", "litebird"}
    score = chunk.score(query)
    assert 0.0 < score < 1.0


def test_document_chunk_title_bonus_improves_score():
    chunk = DocumentChunk("test.md", "LiteBIRD monitor", "prediction window and launch notes")
    with_title = chunk.score({"litebird"})
    without_match = chunk.score({"desi"})
    assert with_title > without_match


# ---------------------------------------------------------------------------
# RAGIndex
# ---------------------------------------------------------------------------

def test_rag_index_build_no_chunks_kb_only():
    """Build with no repo files — should still have KB entries."""
    idx = RAGIndex(chunks=[], knowledge_base=KNOWLEDGE_BASE)
    assert len(idx.knowledge_base) > 0


def test_rag_index_kb_lookup_birefringence():
    idx = RAGIndex()
    result = idx.lookup_kb("birefringence prediction")
    assert result is not None
    assert "LiteBIRD" in result["answer"]


def test_rag_index_kb_lookup_alpha_gut():
    idx = RAGIndex()
    result = idx.lookup_kb("GUT coupling alpha_gut derivation")
    assert result is not None
    assert "5D" in result["answer"] or "current closure path" in result["answer"]


def test_rag_index_kb_lookup_repo_state():
    idx = RAGIndex()
    result = idx.lookup_kb("current repository wave status")
    assert result is not None
    assert any(src in result["sources"] for src in ["docs/WAVE_CHANGELOG.md", "STATUS.md"])


def test_rag_index_kb_lookup_no_match():
    idx = RAGIndex()
    result = idx.lookup_kb("xyzzy incomprehensible query zzz")
    assert result is None


def test_rag_index_search_empty_returns_empty():
    idx = RAGIndex(chunks=[])
    results = idx.search("birefringence", top_k=5)
    assert results == []


def test_rag_index_search_with_chunks():
    chunks = [
        DocumentChunk("a.md", "A", "birefringence litebird 0.273 0.331 prediction"),
        DocumentChunk("b.md", "B", "unrelated content about cats"),
    ]
    idx = RAGIndex(chunks=chunks)
    results = idx.search("birefringence litebird", top_k=2)
    assert len(results) == 2
    # First result should be the birefringence chunk
    assert results[0][1].source == "a.md"
    assert results[0][0] > results[1][0]


def test_rag_index_search_alias_beta_hits_birefringence():
    chunks = [DocumentChunk("a.md", "A", "birefringence litebird prediction window")]
    idx = RAGIndex(chunks=chunks)
    results = idx.search("beta litebird", top_k=1)
    assert results[0][1].source == "a.md"
    assert results[0][0] > 0.0


def test_rag_index_build_from_repo():
    """Build from the actual repo — should succeed without errors."""
    repo_root = Path(__file__).parent.parent
    idx = RAGIndex.build(repo_root=repo_root)
    # Should have at least the KB entries
    assert len(idx.knowledge_base) > 0


# ---------------------------------------------------------------------------
# answer_question
# ---------------------------------------------------------------------------

def test_answer_question_birefringence():
    idx = RAGIndex()
    result = answer_question(idx, "What is the birefringence prediction?")
    assert isinstance(result, dict)
    assert "answer" in result
    assert "0.273" in result["answer"] or "LiteBIRD" in result["answer"]


def test_answer_question_source_type():
    idx = RAGIndex()
    result = answer_question(idx, "birefringence litebird prediction")
    assert result["source_type"] in ("knowledge_base", "document_retrieval", "no_result")


def test_answer_question_repo_state():
    idx = RAGIndex()
    result = answer_question(idx, "What is the current repository wave?")
    assert "answer" in result
    assert result["source_type"] == "knowledge_base"


def test_answer_question_no_result_graceful():
    idx = RAGIndex(chunks=[])
    result = answer_question(idx, "xyzzy42 incomprehensible nonsense query")
    assert "answer" in result
    assert result["source_type"] == "no_result"


def test_answer_question_litebird():
    idx = RAGIndex()
    result = answer_question(idx, "When is LiteBIRD launching?")
    assert "answer" in result
    assert "2032" in result["answer"] or "LiteBIRD" in result["answer"]


def test_answer_question_toe_score():
    idx = RAGIndex()
    result = answer_question(idx, "What is the current ToE score?")
    assert "answer" in result
    assert len(result["answer"]) > 20


def test_answer_question_desi():
    idx = RAGIndex()
    result = answer_question(idx, "What is the DESI dark energy tension?")
    assert "answer" in result


def test_answer_question_alpha_gut():
    idx = RAGIndex()
    result = answer_question(idx, "How is alpha_gut derived?")
    assert "answer" in result
    assert "DERIVED" in result["answer"] or "CS" in result["answer"]


def test_answer_question_trusted_resources():
    idx = RAGIndex()
    result = answer_question(idx, "trusted datasets and pubmed resources")
    assert result["source_type"] == "knowledge_base"
    assert "100 trusted, free online research resources" in result["answer"]


def test_answer_question_with_doc_chunks():
    """With real document chunks, retrieval should work."""
    chunks = [
        DocumentChunk("FALLIBILITY.md", "Fallibility", "n_w = 5 winding number pure theorem pillar 70-D"),
        DocumentChunk("STATUS.md", "Status", "pillar set closed 217 pillars"),
    ]
    idx = RAGIndex(chunks=chunks)
    result = answer_question(idx, "winding number n_w theorem")
    assert result["source_type"] in ("knowledge_base", "document_retrieval")


# ---------------------------------------------------------------------------
# build_default_index
# ---------------------------------------------------------------------------

def test_build_default_index_returns_rag_index():
    idx = build_default_index()
    assert isinstance(idx, RAGIndex)
    assert len(idx.knowledge_base) > 0


def test_build_intent_index_returns_rag_index():
    idx = build_intent_index()
    assert isinstance(idx, RAGIndex)
    assert len(idx.chunks) > 0


def test_retrieve_intent_latest_uses_snapshot_sources():
    idx = build_intent_index()
    result = retrieve_intent(idx, mode="latest_intent")
    assert result["mode"] == "latest_intent"
    assert result["sources"]
    assert all("score" in src for src in result["sources"])
