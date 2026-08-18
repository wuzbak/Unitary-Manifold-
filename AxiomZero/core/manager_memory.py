# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero core/manager_memory.py — Manager 8: Cross-Session Memory Distillation

Responsibilities:
  - Summarise the last-N agent sessions into a compact JSON fact-sheet
  - Feed the fact-sheet into every new session's system prompt
  - Maintain a rolling knowledge base of key physics facts, test results,
    and HILS decisions that have been validated by the human operator
  - Prune stale or superseded facts to keep the fact-sheet lean

Sub-agents:
    SA8.1  Session summariser   (compress raw session log → bullet facts)
    SA8.2  Fact deduplicator    (merge near-duplicate facts)
    SA8.3  Staleness pruner     (remove facts contradicted by newer data)
    SA8.4  System prompt injector (format fact-sheet → LLM system prompt)
    SA8.5  Semantic search      (retrieve relevant facts for a given query)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

FACTSHEET_VERSION = "1.0"
MAX_FACTS_PER_CATEGORY = 50
DEFAULT_FACT_TTL_DAYS = 90
FACT_FILE = Path.home() / ".axiomzero" / "memory" / "factsheet.json"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class MemoryFact:
    """A single validated fact stored in cross-session memory."""
    fact_id: str
    category: str           # e.g. 'physics', 'test_result', 'hils_decision'
    content: str
    confidence: float       # 0.0 – 1.0
    source_task_id: str
    created_at: float
    last_validated_at: float
    validation_count: int = 0
    superseded: bool = False
    tags: List[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        category: str,
        content: str,
        confidence: float,
        source_task_id: str,
        tags: Optional[List[str]] = None,
    ) -> "MemoryFact":
        now = time.time()
        fact_id = hashlib.sha256(
            f"{category}:{content}:{now}".encode()
        ).hexdigest()[:16]
        return cls(
            fact_id=fact_id,
            category=category,
            content=content,
            confidence=confidence,
            source_task_id=source_task_id,
            created_at=now,
            last_validated_at=now,
            tags=tags or [],
        )


@dataclass
class FactSheet:
    """The complete cross-session memory fact-sheet."""
    version: str = FACTSHEET_VERSION
    generated_at: float = field(default_factory=time.time)
    facts: List[MemoryFact] = field(default_factory=list)
    session_count: int = 0

    def to_dict(self) -> Dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> "FactSheet":
        facts = [MemoryFact(**f) for f in data.get("facts", [])]
        return cls(
            version=data.get("version", FACTSHEET_VERSION),
            generated_at=data.get("generated_at", time.time()),
            facts=facts,
            session_count=data.get("session_count", 0),
        )


# ---------------------------------------------------------------------------
# Manager 8
# ---------------------------------------------------------------------------

class MemoryManager:
    """Manager 8: Cross-Session Memory Distillation."""

    name = "M8_Memory"
    model_key = "strategic"
    sub_agents = [
        "SA8.1_session_summariser",
        "SA8.2_fact_deduplicator",
        "SA8.3_staleness_pruner",
        "SA8.4_system_prompt_injector",
        "SA8.5_semantic_search",
    ]

    def __init__(
        self,
        config: Dict,
        model_router: Any,
        repo_root: Path,
        fact_file: Optional[Path] = None,
    ) -> None:
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root
        self.fact_file = fact_file or FACT_FILE
        self._factsheet: Optional[FactSheet] = None
        self._max_facts = config.get("max_facts_per_category", MAX_FACTS_PER_CATEGORY)
        self._ttl_days = config.get("fact_ttl_days", DEFAULT_FACT_TTL_DAYS)

    # ── Persistence ───────────────────────────────────────────────────────

    def load(self) -> FactSheet:
        """Load the fact-sheet from disk; create fresh if absent."""
        if self._factsheet is not None:
            return self._factsheet
        if self.fact_file.exists():
            try:
                data = json.loads(self.fact_file.read_text())
                self._factsheet = FactSheet.from_dict(data)
                logger.info(
                    "Loaded %d facts from %s", len(self._factsheet.facts), self.fact_file
                )
            except Exception as exc:
                logger.warning("Could not load fact-sheet (%s); starting fresh", exc)
                self._factsheet = FactSheet()
        else:
            self._factsheet = FactSheet()
        return self._factsheet

    def save(self) -> None:
        """Persist the current fact-sheet to disk."""
        fs = self.load()
        fs.generated_at = time.time()
        self.fact_file.parent.mkdir(parents=True, exist_ok=True)
        self.fact_file.write_text(json.dumps(fs.to_dict(), indent=2))
        logger.debug("Saved %d facts to %s", len(fs.facts), self.fact_file)

    # ── Core operations ──────────────────────────────────────────────────

    def add_fact(
        self,
        category: str,
        content: str,
        confidence: float,
        source_task_id: str,
        tags: Optional[List[str]] = None,
    ) -> MemoryFact:
        """Add or update a fact; deduplicate by content hash."""
        fs = self.load()
        # Check for near-duplicate (same category + content hash)
        content_hash = hashlib.sha256(f"{category}:{content}".encode()).hexdigest()[:12]
        for existing in fs.facts:
            existing_hash = hashlib.sha256(
                f"{existing.category}:{existing.content}".encode()
            ).hexdigest()[:12]
            if existing_hash == content_hash and not existing.superseded:
                # Update validation metadata
                existing.last_validated_at = time.time()
                existing.validation_count += 1
                existing.confidence = max(existing.confidence, confidence)
                logger.debug("Updated existing fact %s", existing.fact_id)
                self.save()
                return existing

        fact = MemoryFact.create(
            category=category,
            content=content,
            confidence=confidence,
            source_task_id=source_task_id,
            tags=tags,
        )
        fs.facts.append(fact)
        self._prune_category(category)
        self.save()
        logger.info("Added fact [%s] %s…", category, content[:60])
        return fact

    def query_facts(
        self,
        query: str = "",
        category: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 20,
    ) -> List[MemoryFact]:
        """Return relevant facts matching the query."""
        fs = self.load()
        results = [
            f for f in fs.facts
            if not f.superseded
            and f.confidence >= min_confidence
            and (category is None or f.category == category)
        ]
        if query:
            q = query.lower()
            results = [f for f in results if q in f.content.lower() or
                       any(q in tag.lower() for tag in f.tags)]
        # Sort by confidence × recency
        now = time.time()
        results.sort(
            key=lambda f: f.confidence * (1.0 - (now - f.last_validated_at) / (86400 * self._ttl_days)),
            reverse=True,
        )
        return results[:limit]

    def build_system_prompt_injection(self, query: str = "") -> str:
        """
        Return a compact system-prompt section with relevant persistent facts.
        Called by M7 (Executive) at the start of every new session.
        """
        facts = self.query_facts(query=query, min_confidence=0.7, limit=15)
        if not facts:
            return ""
        lines = ["## Persistent Memory — Validated Facts\n"]
        by_cat: Dict[str, List[MemoryFact]] = {}
        for f in facts:
            by_cat.setdefault(f.category, []).append(f)
        for cat, cat_facts in by_cat.items():
            lines.append(f"### {cat.replace('_', ' ').title()}")
            for f in cat_facts:
                lines.append(f"- [{f.confidence:.0%}] {f.content}")
        lines.append("")
        return "\n".join(lines)

    def ingest_session_log(self, session_id: str, log_entries: List[Dict]) -> int:
        """
        Extract facts from raw session log entries and add to the fact-sheet.
        Returns the number of new/updated facts.
        """
        count = 0
        for entry in log_entries:
            event_type = entry.get("event_type", "")
            if event_type == "test_result" and entry.get("passed"):
                self.add_fact(
                    category="test_result",
                    content=f"Test suite {entry.get('suite', 'unknown')}: "
                            f"{entry.get('passed', 0)} passed, {entry.get('failed', 0)} failed",
                    confidence=1.0,
                    source_task_id=session_id,
                    tags=["testing", entry.get("suite", "")],
                )
                count += 1
            elif event_type == "hils_decision":
                self.add_fact(
                    category="hils_decision",
                    content=f"HILS [{entry.get('decision')}]: {entry.get('summary', '')}",
                    confidence=0.95,
                    source_task_id=session_id,
                    tags=["hils", "governance"],
                )
                count += 1
            elif event_type == "paper_found":
                self.add_fact(
                    category="literature",
                    content=f"Paper: {entry.get('title', '')} — {entry.get('verdict', '')}",
                    confidence=entry.get("confidence", 0.8),
                    source_task_id=session_id,
                    tags=["literature", entry.get("verdict", "")],
                )
                count += 1
        return count

    # ── Internal helpers ──────────────────────────────────────────────────

    def _prune_category(self, category: str) -> None:
        """Keep only the top-N highest-confidence, most-recent facts per category."""
        fs = self.load()
        cat_facts = [f for f in fs.facts if f.category == category and not f.superseded]
        if len(cat_facts) <= self._max_facts:
            return
        # Sort: confidence descending, recency descending
        cat_facts.sort(key=lambda f: (f.confidence, f.last_validated_at), reverse=True)
        keep = {f.fact_id for f in cat_facts[: self._max_facts]}
        for fact in fs.facts:
            if fact.category == category and fact.fact_id not in keep:
                fact.superseded = True

    def prune_stale_facts(self) -> int:
        """Mark facts older than TTL as superseded. Returns count pruned."""
        fs = self.load()
        threshold = time.time() - self._ttl_days * 86400
        pruned = 0
        for fact in fs.facts:
            if not fact.superseded and fact.last_validated_at < threshold:
                fact.superseded = True
                pruned += 1
        if pruned:
            self.save()
            logger.info("Pruned %d stale facts", pruned)
        return pruned

    def get_stats(self) -> Dict:
        """Return summary statistics about the current fact-sheet."""
        fs = self.load()
        active = [f for f in fs.facts if not f.superseded]
        by_cat: Dict[str, int] = {}
        for f in active:
            by_cat[f.category] = by_cat.get(f.category, 0) + 1
        return {
            "total_facts": len(fs.facts),
            "active_facts": len(active),
            "superseded_facts": len(fs.facts) - len(active),
            "by_category": by_cat,
            "session_count": fs.session_count,
            "factsheet_version": fs.version,
        }

    async def run(self, task: Any) -> Dict:
        """Execute the memory distillation task (called by agent_core)."""
        action = getattr(task, "action", None) or (task.get("action") if isinstance(task, dict) else None)
        query = getattr(task, "query", "") or (task.get("query", "") if isinstance(task, dict) else "")

        if action == "build_prompt":
            injection = self.build_system_prompt_injection(query)
            return {"status": "ok", "manager": self.name, "prompt_injection": injection}
        elif action == "stats":
            return {"status": "ok", "manager": self.name, "stats": self.get_stats()}
        elif action == "prune":
            count = self.prune_stale_facts()
            return {"status": "ok", "manager": self.name, "pruned": count}
        elif action == "add_fact":
            params = task if isinstance(task, dict) else {}
            fact = self.add_fact(
                category=params.get("category", "general"),
                content=params.get("content", ""),
                confidence=params.get("confidence", 0.8),
                source_task_id=params.get("task_id", "manual"),
                tags=params.get("tags"),
            )
            return {"status": "ok", "manager": self.name, "fact_id": fact.fact_id}
        else:
            return {
                "status": "ok",
                "manager": self.name,
                "prompt_injection": self.build_system_prompt_injection(query),
                "stats": self.get_stats(),
            }
