# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
bot/psicat_literature_corpus.py — PsiCat's own editorial literature as an
opt-in retrieval corpus, kept separate from the hardgate physics corpus.

ADJACENT TRACK.  Status label: ``PSICAT_EDITORIAL_CORPUS``.  Default OFF
everywhere it is wired in: ``bot.rag_index.RAGIndex.build()`` only includes
this corpus when ``include_psicat_literature=True`` is passed explicitly or
the ``UM_PSICAT_EDITORIAL_CORPUS`` environment flag is set, and the Navigator
retrieval harness (``merlin_rag.psicat_literature_corpus_enabled``) is the
same opt-in pattern already used for ``MERLIN_BM25_PILLAR_RANKING``,
``MERLIN_SEMANTIC_EMBEDDER_RANKING``, and ``MERLIN_PHICAT_PROTOCOL``.

This module loads two things, and only these two things:

1. Every Book, Article, and Release markdown file under
   ``7-OUTREACH/A Z PsiCat Literature/`` (``Books/``, ``Articles/``,
   ``Releases/``).  These are PsiCat's curated editorial rewrites and
   original commissioned works (see that folder's ``README.md`` for the
   editorial contract); ``tests/test_psicat_literature_integrity.py``
   already enforces their provenance/format contract, separately from
   this module's job of making them retrievable.

2. The already-extracted text of PsiCat's three self-authored PDF exports
   (Publications — 118 pages / 36 articles; Comic Shop — 16 pages / 15
   pieces; the AxiomZero Knowledge Library — 53 pages / 232 sources).
   The text was extracted once, with ``pypdf``, into
   ``12-AZ-IP/20-psicat-navigator/ox_navigator/engine/data/raw/psicat_exports_2026-10-08.json.gz``
   for ``merlin_publication_audit.py`` and ``merlin_webspace_index.py``.
   This module *reuses that same cache* — it does not re-run PDF
   extraction, and it does not duplicate ``merlin_publication_audit.py``'s
   job of auditing the PDFs' claims against the live registry.  That audit
   module remains the authority on whether a claim in these PDFs is
   correct; this module only makes their text retrievable as reference
   material about what PsiCat has published and compiled about himself.

A fourth self-authored PDF exists in the repository
(``12-AZ-IP/20-psicat-navigator/WEBSPACE10_01.pdf``, 2,190 pages — the
webspace machine index) but it is a structured JSON-as-prose export handled
separately by ``merlin_webspace_index.py``'s own reconstruction pipeline; it
is intentionally out of scope here, which only covers the three literature
PDFs named above plus the curated Books/Articles/Releases markdown.

Nothing in this module changes any hardgate physics claim, pillar status, or
promotion decision.  It is read-only reference material, is not
fact-checked here, and must not be cited as a physics authority in place of
``src/core/`` or ``STATUS.md``.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

GOVERNANCE_LABEL = "PSICAT_EDITORIAL_CORPUS"
STATUS_LABEL = "ADJACENT_TRACK"

LITERATURE_ROOT_REL = Path("7-OUTREACH") / "A Z PsiCat Literature"
LITERATURE_SUBDIRS: Tuple[str, ...] = ("Books", "Articles", "Releases")

_EXPORTS_PATH_REL = (
    Path("12-AZ-IP") / "20-psicat-navigator" / "ox_navigator" / "engine" / "data" / "raw"
    / "psicat_exports_2026-10-08.json.gz"
)
_EXPORTS_PROVENANCE_PATH_REL = (
    Path("12-AZ-IP") / "20-psicat-navigator" / "ox_navigator" / "engine" / "data" / "raw"
    / "psicat_exports_2026-10-08.provenance.json"
)

#: Keys in the extracted-text gzip, and the human-readable titles used when
#: they are indexed as chunks.  Keys must match the gzip's top-level keys
#: exactly (``comic_shop``, ``knowledge_library``, ``publications``).
PDF_EXPORT_TITLES: Dict[str, str] = {
    "publications": "PsiCat Publications (self-authored PDF export, 118 pages / 36 articles)",
    "comic_shop": "PsiCat's Comic Shop (self-authored PDF export, 16 pages / 15 pieces)",
    "knowledge_library": (
        "AxiomZero Knowledge Library (self-authored PDF export, 53 pages / 232 sources)"
    ),
}


def _repo_root(repo_root: "Path | None" = None) -> Path:
    return Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent.parent


def _markdown_sources(repo_root: Path) -> List[Tuple[Path, str]]:
    """Every Book/Article/Release markdown file, with a display title."""
    root = repo_root / LITERATURE_ROOT_REL
    out: List[Tuple[Path, str]] = []
    for sub in LITERATURE_SUBDIRS:
        directory = root / sub
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            out.append((path, f"PsiCat Literature / {sub} / {path.stem}"))
    return out


def load_pdf_export_texts(repo_root: "Path | None" = None) -> Dict[str, str]:
    """Return ``{export_key: extracted_text}`` for PsiCat's three self-authored PDFs.

    Reuses the gzip cache already written for ``merlin_publication_audit.py``
    / ``merlin_webspace_index.py``; does not re-run PDF extraction.  Returns
    ``{}`` if the cache is not present (e.g. a checkout that excludes large
    binary/derived artifacts), which callers must treat as "no PDF text
    available this run", not as an integrity failure.
    """
    root = _repo_root(repo_root)
    path = root / _EXPORTS_PATH_REL
    if not path.exists():
        return {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    return {str(key): str(value) for key, value in dict(data).items()}


def load_pdf_export_provenance(repo_root: "Path | None" = None) -> Dict[str, Any]:
    """Return the provenance sidecar (SHA-256s, upload commits, page counts)."""
    root = _repo_root(repo_root)
    path = root / _EXPORTS_PROVENANCE_PATH_REL
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def iter_literature_sources(repo_root: "Path | None" = None) -> List[Dict[str, str]]:
    """Return metadata (no text) for every source this corpus should cover.

    Used by ``tests/test_psicat_literature_corpus.py`` to assert the loader
    sees every Book/Article/Release file and all three self-authored PDF
    exports, so the ingestion gap this module closes cannot silently reopen.
    """
    root = _repo_root(repo_root)
    sources: List[Dict[str, str]] = [
        {
            "kind": "markdown",
            "path": str(path.relative_to(root)),
            "title": title,
        }
        for path, title in _markdown_sources(root)
    ]
    exports = load_pdf_export_texts(root)
    for key, title in PDF_EXPORT_TITLES.items():
        if key in exports:
            sources.append({"kind": "pdf_export", "path": f"psicat-export:{key}", "title": title})
    return sources


def build_literature_chunks(
    repo_root: "Path | None" = None,
    max_chunk_chars: int = 1500,
) -> List[Any]:
    """Build ``bot.rag_index.DocumentChunk``-compatible chunks for this corpus.

    Every chunk is tagged ``governance_label=PSICAT_EDITORIAL_CORPUS`` so
    retrieval callers (and ``bot.rag_index._source_weight``) can tell this
    corpus apart from the hardgate/governance document set indexed by
    default.  Imports ``DocumentChunk`` lazily to avoid an import cycle,
    since ``bot.rag_index`` imports this module back for the opt-in build
    path.
    """
    from bot.rag_index import DocumentChunk

    root = _repo_root(repo_root)
    chunks: List[Any] = []

    for path, title in _markdown_sources(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(root))
        for i in range(0, len(text), max_chunk_chars):
            chunks.append(
                DocumentChunk(
                    rel,
                    title,
                    text[i : i + max_chunk_chars],
                    governance_label=GOVERNANCE_LABEL,
                )
            )

    exports = load_pdf_export_texts(root)
    for key, title in PDF_EXPORT_TITLES.items():
        text = exports.get(key)
        if not text:
            continue
        source = f"psicat-export:{key}"
        for i in range(0, len(text), max_chunk_chars):
            chunks.append(
                DocumentChunk(
                    source,
                    title,
                    text[i : i + max_chunk_chars],
                    governance_label=GOVERNANCE_LABEL,
                )
            )
    return chunks


__all__ = [
    "GOVERNANCE_LABEL",
    "STATUS_LABEL",
    "LITERATURE_ROOT_REL",
    "LITERATURE_SUBDIRS",
    "PDF_EXPORT_TITLES",
    "iter_literature_sources",
    "load_pdf_export_texts",
    "load_pdf_export_provenance",
    "build_literature_chunks",
]
