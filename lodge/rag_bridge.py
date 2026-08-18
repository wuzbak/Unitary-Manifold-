# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/rag_bridge.py — Knowledge Exchange RAG Bridge (Zone 5)

Wraps the existing ``bot/rag_index.py`` infrastructure to provide a
Lodge-native Knowledge Exchange interface.  Any agent or human can submit
a physics question and receive a grounded answer with citations to specific
files and line numbers in the Unitary Manifold repository.

Additionally tracks question frequency so that recurring gaps surface as
candidates for new pillar entries.

Usage
-----
    from lodge.rag_bridge import KnowledgeExchange
    kx = KnowledgeExchange.build()
    result = kx.ask("What is the braided sound speed?")
    print(result["answer"])
    print(result["citations"])

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

__all__ = ["KnowledgeExchange"]

_HISTORY_FILE = Path(__file__).parent / "ledger" / "exchange_history.jsonl"


class KnowledgeExchange:
    """
    Knowledge Exchange powered by the existing bot/rag_index RAG system.

    Falls back to a minimal keyword search if the RAG index is unavailable.
    """

    def __init__(self, rag_index: Any = None) -> None:
        self._idx = rag_index
        _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def build(cls) -> "KnowledgeExchange":
        """Build the RAG index (lazy import — works without bot deps installed)."""
        try:
            from bot.rag_index import RAGIndex
            idx = RAGIndex.build()
        except Exception:
            idx = None
        return cls(rag_index=idx)

    def ask(
        self,
        question: str,
        agent_label: str = "anonymous",
        agent_class: str = "human",
    ) -> Dict[str, Any]:
        """
        Answer a physics question using the RAG index.

        Returns a dict with keys:
          question, answer, citations, confidence, timestamp, agent_label
        """
        answer = ""
        citations: List[str] = []
        confidence = 0.0

        if self._idx is not None:
            try:
                from bot.rag_index import answer_question
                result = answer_question(self._idx, question)
                answer = result.get("answer", "")
                citations = result.get("sources", [])
                confidence = float(result.get("score", 0.0))
            except Exception as exc:
                answer = f"RAG index error: {exc}"
        else:
            # Fallback: simple keyword lookup against key constants
            answer, citations = self._fallback_answer(question)
            confidence = 0.5

        record = {
            "question": question,
            "answer": answer,
            "citations": citations,
            "confidence": round(confidence, 4),
            "timestamp": _utcnow(),
            "agent_label": agent_label,
            "agent_class": agent_class,
        }

        self._log(record)
        return record

    def top_questions(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Return the *n* most frequently asked questions.

        Useful for surfacing gaps in the theory documentation.
        """
        if not _HISTORY_FILE.exists():
            return []

        counter: Counter = Counter()
        with open(_HISTORY_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                    counter[rec["question"]] += 1
                except (json.JSONDecodeError, KeyError):
                    continue

        return [
            {"question": q, "count": c}
            for q, c in counter.most_common(n)
        ]

    def history(
        self,
        agent_label: Optional[str] = None,
        n: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Return recent question/answer pairs, optionally filtered by agent.
        """
        if not _HISTORY_FILE.exists():
            return []

        rows: List[Dict[str, Any]] = []
        with open(_HISTORY_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                    if agent_label and rec.get("agent_label") != agent_label:
                        continue
                    rows.append(rec)
                except (json.JSONDecodeError, KeyError):
                    continue

        return rows[-n:]

    # ── Internals ─────────────────────────────────────────────────────────────

    def _log(self, record: Dict[str, Any]) -> None:
        """Append one record to the exchange history (JSONL format)."""
        with open(_HISTORY_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _fallback_answer(self, question: str) -> tuple[str, List[str]]:
        """Minimal keyword-based fallback when bot/rag_index is unavailable."""
        q = question.lower()
        answers = {
            "sound speed": (
                "The braided sound speed is c_s = 12/37 ≈ 0.3243, derived from "
                "the (5,7) winding braid resonance with k_CS = 74.",
                ["src/core/braided_winding.py"],
            ),
            "birefringence": (
                "CMB birefringence angle β ∈ {≈0.273°, ≈0.331°} (canonical). "
                "Admissible window [0.22°, 0.38°]. LiteBIRD will test this ~2032.",
                ["src/core/braided_winding.py", "FALLIBILITY.md"],
            ),
            "spectral index": (
                "n_s ≈ 0.9635 (Planck 2018: 0.9649 ± 0.0042, 0.33σ away). "
                "Derived from the braided KK inflaton.",
                ["src/core/inflation.py", "src/core/braided_winding.py"],
            ),
            "tensor": (
                "r_braided ≈ 0.0315, below BICEP/Keck 2021 95% CL bound of 0.036.",
                ["src/core/braided_winding.py"],
            ),
            "alpha": (
                "α_em⁻¹ ≈ 137.0 (PDG: 137.036, residual 0.026%). Derived via "
                "α_GUT = 3/74 and one-loop SU(5)→SM RGE.",
                ["src/core/alpha_em_geometric.py"],
            ),
            "phi0": (
                "φ₀_eff = π · n_w = 5π ≈ 31.42 (n_w = 5). Closure proved by Pillar 56.",
                ["src/core/phi0_closure.py", "src/core/inflation.py"],
            ),
            "winding": (
                "Winding number n_w = 5, selected by Planck n_s data. "
                "k_CS = 5² + 7² = 74 (sum-of-squares resonance).",
                ["src/core/braided_winding.py"],
            ),
            "fixed point": (
                "The FTUM operator is a contraction; the fixed point establishes α ≈ 1/φ₀². "
                "See src/multiverse/fixed_point.py → derive_alpha_from_fixed_point().",
                ["src/multiverse/fixed_point.py"],
            ),
            "entropy": (
                "Entropy-area law S = A/(4G) is an exact geometric consequence of the "
                "5D metric reduction (Pillar 4). See src/holography/boundary.py.",
                ["src/holography/boundary.py"],
            ),
        }

        for keyword, (ans, cites) in answers.items():
            if keyword in q:
                return ans, cites

        return (
            "No direct match found. Try asking about: sound speed, birefringence, "
            "spectral index, tensor ratio, alpha_em, phi0, winding number, "
            "fixed point, or entropy.",
            ["lodge/pillar_registry.py", "src/core/"],
        )


def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
