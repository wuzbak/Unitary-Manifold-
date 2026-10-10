# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Coverage tests for the opt-in PsiCat editorial retrieval corpus.

These tests assert the corpus loader in ``bot.psicat_literature_corpus``
actually sees every Book/Article/Release markdown file and all three of
PsiCat's self-authored PDF exports, so the literature-ingestion gap this
module closes cannot silently reopen. They do not re-validate the
editorial contract itself (``tests/test_psicat_literature_integrity.py``
already owns that), and they do not re-run PDF extraction (the exports are
reused from the existing gzip cache written for ``merlin_publication_audit``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bot.psicat_literature_corpus import (
    GOVERNANCE_LABEL,
    LITERATURE_ROOT_REL,
    LITERATURE_SUBDIRS,
    PDF_EXPORT_TITLES,
    build_literature_chunks,
    iter_literature_sources,
    load_pdf_export_provenance,
    load_pdf_export_texts,
)
from bot.rag_index import DocumentChunk, PSICAT_EDITORIAL_CORPUS_FLAG, RAGIndex

REPO_ROOT = Path(__file__).resolve().parents[1]
LITERATURE_ROOT = REPO_ROOT / LITERATURE_ROOT_REL


def _actual_markdown_count() -> int:
    total = 0
    for sub in LITERATURE_SUBDIRS:
        directory = LITERATURE_ROOT / sub
        if directory.is_dir():
            total += len(list(directory.glob("*.md")))
    return total


def test_loader_sees_every_markdown_file_in_every_subdirectory() -> None:
    sources = iter_literature_sources()
    markdown_sources = [s for s in sources if s["kind"] == "markdown"]
    assert len(markdown_sources) == _actual_markdown_count()
    assert len(markdown_sources) > 0

    seen_paths = {s["path"] for s in markdown_sources}
    for sub in LITERATURE_SUBDIRS:
        directory = LITERATURE_ROOT / sub
        if not directory.is_dir():
            continue
        for path in directory.glob("*.md"):
            rel = str(path.relative_to(REPO_ROOT))
            assert rel in seen_paths, f"loader did not see {rel}"


def test_loader_covers_all_three_self_authored_pdf_exports() -> None:
    exports = load_pdf_export_texts()
    if not exports:
        pytest.skip("PDF export cache not present in this checkout")
    assert set(exports) == set(PDF_EXPORT_TITLES)
    for key, text in exports.items():
        assert isinstance(text, str) and text, f"export {key} has no extracted text"

    sources = iter_literature_sources()
    pdf_sources = {s["path"] for s in sources if s["kind"] == "pdf_export"}
    assert pdf_sources == {f"psicat-export:{key}" for key in PDF_EXPORT_TITLES}


def test_pdf_export_provenance_matches_declared_three_pdfs() -> None:
    provenance = load_pdf_export_provenance()
    if not provenance:
        pytest.skip("PDF export provenance sidecar not present in this checkout")
    declared = provenance.get("sources") or {}
    assert set(declared) == set(PDF_EXPORT_TITLES)
    # Honest, documented page counts (from the inspection that motivated this module).
    expected_pages = {"publications": 118, "comic_shop": 16, "knowledge_library": 53}
    for key, pages in expected_pages.items():
        assert declared[key]["pages"] == pages


def test_build_literature_chunks_covers_every_markdown_source_and_pdf_export() -> None:
    chunks = build_literature_chunks()
    assert chunks, "literature corpus produced no chunks"
    for chunk in chunks:
        assert chunk.governance_label == GOVERNANCE_LABEL

    sources = iter_literature_sources()
    markdown_paths = {s["path"] for s in sources if s["kind"] == "markdown"}
    chunk_sources = {chunk.source for chunk in chunks}
    missing = markdown_paths - chunk_sources
    assert not missing, f"chunks missing for: {sorted(missing)[:5]} (+{max(0, len(missing) - 5)} more)"

    exports = load_pdf_export_texts()
    for key in PDF_EXPORT_TITLES:
        if key in exports:
            assert f"psicat-export:{key}" in chunk_sources


def test_document_chunk_defaults_to_repository_core_label() -> None:
    chunk = DocumentChunk("README.md", "README", "hello")
    assert chunk.governance_label == "REPOSITORY_CORE"


def test_literature_corpus_is_excluded_by_default() -> None:
    index = RAGIndex.build()
    assert not any(chunk.governance_label == GOVERNANCE_LABEL for chunk in index.chunks)


def test_literature_corpus_included_when_flag_or_kwarg_set(monkeypatch: pytest.MonkeyPatch) -> None:
    index = RAGIndex.build(include_psicat_literature=True)
    assert any(chunk.governance_label == GOVERNANCE_LABEL for chunk in index.chunks)

    monkeypatch.setenv(PSICAT_EDITORIAL_CORPUS_FLAG, "1")
    index_via_env = RAGIndex.build()
    assert any(chunk.governance_label == GOVERNANCE_LABEL for chunk in index_via_env.chunks)
