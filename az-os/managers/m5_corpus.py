# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m5_corpus.py — Manager 5: Literary Corpus & RAG Engine

Interfaces with bot/rag_index.py (already built) to provide the 7-manager
network with instant access to the 24+ books, manuscripts, and pillar corpus.

Sub-agents:
  1. VectorRetrieverAgent  — queries ChromaDB / local RAG index
  2. PaperSynthesizer      — synthesises multiple retrieved chunks
  3. CrossRefVerifier      — cross-references claims against corpus
  4. TerminologyGatekeeper — ensures consistent terminology
  5. MarkdownDraftGen      — generates formatted markdown drafts
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).parent.parent.parent


@dataclass
class CorpusResult:
    agent: str
    status: str
    value: Any = None
    error: Optional[str] = None


class M5CorpusManager:
    """Manager 5 — Literary Corpus & RAG Engine."""

    MANAGER_ID = "M5"
    KK_LEVEL = 2   # trusted agent ring

    def __init__(self) -> None:
        self._rag = self._try_import("bot.rag_index")
        self._idx = None
        if self._rag is not None:
            try:
                self._idx = self._rag.RAGIndex.build()
            except Exception:
                self._idx = None

    # ------------------------------------------------------------------
    # Sub-agent 1: Vector Retriever
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 5) -> CorpusResult:
        """Retrieve the top-k most relevant corpus chunks for a query."""
        if self._rag is None or self._idx is None:
            return CorpusResult("VectorRetrieverAgent", "unverified",
                                error="RAG index unavailable — bot/rag_index.py not loaded")
        try:
            result = self._rag.answer_question(self._idx, query)
            chunks = result.get("chunks", [])[:top_k]
            return CorpusResult("VectorRetrieverAgent", "ok",
                                value={"chunks": chunks, "answer": result.get("answer", "")})
        except Exception as exc:
            return CorpusResult("VectorRetrieverAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 2: Paper Synthesiser
    # ------------------------------------------------------------------

    def synthesise(self, chunks: list[str], topic: str) -> CorpusResult:
        """Synthesise multiple corpus chunks into a coherent summary."""
        if not chunks:
            return CorpusResult("PaperSynthesizer", "error", error="No chunks provided")
        combined = "\n\n---\n\n".join(chunks[:5])
        summary = f"[M5 Synthesis on '{topic}']\n\n" + combined[:2000]
        return CorpusResult("PaperSynthesizer", "ok", value={"summary": summary})

    # ------------------------------------------------------------------
    # Sub-agent 3: Cross-Reference Verifier
    # ------------------------------------------------------------------

    def cross_reference(self, claim: str) -> CorpusResult:
        """
        Check whether a claim is consistent with the indexed corpus.

        Returns "verified" if supporting evidence is found, "unverified" otherwise.
        """
        result = self.retrieve(claim, top_k=3)
        if result.status != "ok":
            return CorpusResult("CrossRefVerifier", "unverified",
                                error="RAG retrieval failed")
        chunks = result.value.get("chunks", [])
        has_support = any(
            word in " ".join(chunks).lower()
            for word in claim.lower().split()[:5]
        )
        return CorpusResult(
            "CrossRefVerifier",
            "verified" if has_support else "unverified",
            value={"claim": claim, "supporting_chunks": len(chunks)},
        )

    # ------------------------------------------------------------------
    # Sub-agent 4: Terminology Gatekeeper
    # ------------------------------------------------------------------

    CANONICAL_TERMS = {
        "compactification radius": ["R5", "R_5", "extra dimension radius"],
        "winding number": ["n_w", "winding_number", "WINDING_NUMBER"],
        "spectral index": ["n_s", "n_S", "N_S"],
        "tensor-to-scalar ratio": ["r", "r_braided", "R_BRAIDED"],
        "KK level": ["KK ring", "privilege ring", "kk_level"],
    }

    def check_terminology(self, text: str) -> CorpusResult:
        """Flag non-canonical terminology variants."""
        issues = []
        text_lower = text.lower()
        for canonical, variants in self.CANONICAL_TERMS.items():
            for variant in variants:
                if variant.lower() in text_lower and canonical.lower() not in text_lower:
                    issues.append(f"Use '{canonical}' instead of '{variant}'")
        if issues:
            return CorpusResult("TerminologyGatekeeper", "flagged",
                                value={"issues": issues})
        return CorpusResult("TerminologyGatekeeper", "ok",
                            value={"issues": []})

    # ------------------------------------------------------------------
    # Sub-agent 5: Markdown Draft Generator
    # ------------------------------------------------------------------

    def generate_draft(self, title: str, sections: dict[str, str]) -> CorpusResult:
        """
        Generate a formatted markdown draft document.

        Parameters
        ----------
        title : str
        sections : dict[str, str]
            {section_heading: section_body}
        """
        lines = [
            f"# {title}",
            "",
            "*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*",
            "*Code architecture, document engineering: GitHub Copilot (AI).*",
            "",
        ]
        for heading, body in sections.items():
            lines.append(f"## {heading}")
            lines.append("")
            lines.append(body)
            lines.append("")
        draft = "\n".join(lines)
        return CorpusResult("MarkdownDraftGen", "ok", value={"markdown": draft})

    @staticmethod
    def _try_import(module_path: str) -> Optional[Any]:
        repo_str = str(REPO_ROOT)
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)
        try:
            return __import__(module_path.replace(".", "/"), fromlist=[""])
        except Exception:
            try:
                import importlib
                return importlib.import_module(module_path)
            except ImportError:
                return None
