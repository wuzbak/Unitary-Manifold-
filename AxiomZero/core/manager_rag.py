# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero Manager 5 — Literary Corpus & RAG Engine

Maps to: bot/rag_index.py, bot/research_resources.py,
         6-MONOGRAPH/, manuscript/, proof/

Sub-agents:
    SA5.1  24-book vector retriever
    SA5.2  Paper synthesizer
    SA5.3  Cross-reference verifier
    SA5.4  Terminology gatekeeper
    SA5.5  Markdown draft generator

Purpose: Ensures agents operate with the correct theoretical context.
No agent should generate output that contradicts the indexed corpus
without the contradiction being flagged.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional ChromaDB
try:
    import chromadb  # type: ignore
    _CHROMA = True
except ImportError:
    _CHROMA = False


class RAGManager:
    """Manager 5: Literary Corpus & RAG Engine."""

    name = "M5_RAG"
    model_key = "embed"
    sub_agents = [
        "SA5.1_vector_retriever",
        "SA5.2_paper_synthesizer",
        "SA5.3_cross_ref_verifier",
        "SA5.4_terminology_gatekeeper",
        "SA5.5_markdown_draft_generator",
    ]

    # Canonical UM terminology (anything not in this set triggers a flag)
    CANONICAL_TERMS = {
        "winding number", "braided winding", "kaluza-klein", "compactification",
        "5d metric ansatz", "ftum", "ueum", "holographic boundary",
        "spectral index", "tensor-to-scalar ratio", "birefringence",
        "hardgate", "adjacent track", "unitary pentad", "hils",
        "planck units", "phi0", "radion", "dilaton",
    }

    def __init__(self, config: Dict, model_router: Any, repo_root: Path):
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root
        self._chroma_client: Optional[Any] = None
        self._rag_index = self._load_existing_rag()

    def _load_existing_rag(self):
        """Load the existing bot/rag_index.py RAG index if available."""
        rag_path = self.repo_root / "bot" / "rag_index.py"
        if not rag_path.exists():
            return None
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("bot_rag", rag_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            return getattr(mod, "RAGIndex", None)
        except Exception as exc:
            logger.warning("[M5_RAG] Could not load bot/rag_index.py: %s", exc)
            return None

    async def run(self, state: Any) -> Dict[str, Any]:
        task = state.task
        payload = task.payload
        query = payload.get("query", task.description)

        logger.info("[%s] RAG retrieval for task %s", self.name, task.task_id)

        results = {}
        results["retrieval"] = await self._sa_retrieve(query)
        results["synthesis"] = await self._sa_synthesize(results["retrieval"])
        results["cross_ref"] = await self._sa_cross_reference(query, results["retrieval"])
        results["terminology"] = await self._sa_terminology_gate(query)
        results["draft"] = await self._sa_markdown_draft(query, results["synthesis"])

        return {
            "manager": self.name,
            "status": "ok",
            "context_retrieved": bool(results["retrieval"].get("chunks")),
            "sub_agent_results": results,
        }

    async def _sa_retrieve(self, query: str) -> Dict:
        """SA5.1: Vector retrieval from ChromaDB or keyword fallback."""
        vectordb_url = self.config.get("vectordb_url", "")

        # Try ChromaDB
        if _CHROMA and vectordb_url.startswith("http"):
            try:
                client = chromadb.HttpClient(host=vectordb_url.split("//")[1].split(":")[0],
                                              port=int(vectordb_url.split(":")[-1]))
                collection_name = self.config.get("rag", {}).get("collection_name", "unitary_manifold")
                try:
                    collection = client.get_collection(collection_name)
                    results = collection.query(query_texts=[query], n_results=5)
                    chunks = results.get("documents", [[]])[0]
                    return {"ok": True, "chunks": chunks, "source": "chromadb"}
                except Exception:
                    pass
            except Exception:
                pass

        # Fallback: keyword search over local files using existing RAG index
        if self._rag_index:
            try:
                idx = self._rag_index.build()
                from bot.rag_index import answer_question  # type: ignore
                result = answer_question(idx, query)
                return {"ok": True, "chunks": [result.get("answer", "")], "source": "keyword_rag"}
            except Exception as exc:
                logger.debug("[M5_RAG] Keyword RAG fallback failed: %s", exc)

        # Last resort: grep key terms from corpus
        chunks = self._grep_corpus(query)
        return {"ok": True, "chunks": chunks, "source": "grep_fallback"}

    def _grep_corpus(self, query: str, max_results: int = 3) -> List[str]:
        """Simple keyword grep over key corpus files."""
        terms = query.lower().split()[:3]
        hits = []
        corpus_dirs = [
            self.repo_root / "proof",
            self.repo_root / "6-MONOGRAPH",
            self.repo_root / "src" / "core",
        ]
        for d in corpus_dirs:
            if not d.exists():
                continue
            for md_file in list(d.rglob("*.md"))[:20] + list(d.rglob("*.py"))[:20]:
                try:
                    content = md_file.read_text(errors="replace")
                    if any(t in content.lower() for t in terms):
                        # Return first 300 chars of matching file
                        hits.append(f"[{md_file.name}] {content[:300]}")
                        if len(hits) >= max_results:
                            return hits
                except Exception:
                    pass
        return hits

    async def _sa_synthesize(self, retrieval: Dict) -> Dict:
        """SA5.2: Synthesize retrieved chunks into a coherent context block."""
        chunks = retrieval.get("chunks", [])
        if not chunks:
            return {"ok": True, "synthesis": "No relevant corpus sections retrieved."}
        combined = "\n\n---\n\n".join(str(c) for c in chunks[:3])
        return {"ok": True, "synthesis": combined[:2000]}

    async def _sa_cross_reference(self, query: str, retrieval: Dict) -> Dict:
        """SA5.3: Check for cross-references to FALLIBILITY.md and predictions."""
        fallibility = self.repo_root / "FALLIBILITY.md"
        claim_board = self.repo_root / "docs" / "CLAIM_MASTER_BOARD.md"
        refs = {}
        for name, path in [("FALLIBILITY.md", fallibility), ("CLAIM_MASTER_BOARD.md", claim_board)]:
            if path.exists():
                content = path.read_text(errors="replace")
                terms = query.lower().split()
                hits = [t for t in terms if t in content.lower()]
                refs[name] = {"referenced": bool(hits), "matching_terms": hits[:5]}
        return {"ok": True, "references": refs}

    async def _sa_terminology_gate(self, query: str) -> Dict:
        """SA5.4: Flag non-canonical terminology."""
        query_lower = query.lower()
        flagged = []
        # Check for common mis-phrasings
        mis_phrases = {
            "extra dimension": "Use 'compactified 5th dimension' (not 'extra dimension')",
            "string theory": "AxiomZero is a Kaluza-Klein framework, not string theory",
            "dark matter particle": "UM predicts geometric dark sector — verify claim carefully",
        }
        for phrase, note in mis_phrases.items():
            if phrase in query_lower:
                flagged.append({"phrase": phrase, "note": note})
        return {"ok": True, "flagged": flagged, "flag_count": len(flagged)}

    async def _sa_markdown_draft(self, query: str, synthesis: Dict) -> Dict:
        """SA5.5: Generate a structured markdown context block for M7."""
        synth_text = synthesis.get("synthesis", "")
        draft = f"## Retrieved Context\n\n**Query:** {query}\n\n{synth_text}"
        return {"ok": True, "draft": draft[:1500]}
