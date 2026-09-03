# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Session and durable memory helpers for Merlin."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .gate_parser import extract_gate_badges
from .merlin_persona import compress_context
from .merlin_telemetry import summarize_runs

MERLIN_ACTIVE_SESSION_KEY = "merlin_active_session"
MERLIN_CACHE_KEY = "merlin_sessions_cache"
MERLIN_MAX_HISTORY = 50
MERLIN_MAX_INTENTS = 100
MERLIN_MAX_TELEMETRY = 100
MERLIN_MAX_AUDITS = 100

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")

DEFAULT_DURABLE_MEMORIES = [
    {
        "scope": "repository",
        "fact": "Merlin is local/offline-first and OpenRouter is compatibility-only fallback.",
        "source": "product_policy",
        "tags": ["runtime", "router", "fallback", "openrouter"],
    },
    {
        "scope": "repository",
        "fact": "Merlin must keep epistemic labels, boundary statements, and uncertainty visible.",
        "source": "program_doctrine",
        "tags": ["governance", "epistemic", "labels", "uncertainty"],
    },
    {
        "scope": "repository",
        "fact": "Privileged Merlin modifications require identity verification and otherwise must be refused.",
        "source": "identity_policy",
        "tags": ["identity", "privilege", "safety"],
    },
]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str) -> str:
    return _NORMALIZE_RE.sub(" ", str(text or "").lower()).strip()


def infer_intent(query: str) -> str:
    sample = (query or "").lower()
    if any(item in sample for item in {"plan", "roadmap", "strategy"}):
        return "planning"
    if any(item in sample for item in {"test", "verify", "check"}):
        return "verification"
    if any(item in sample for item in {"governance", "policy", "boundary"}):
        return "governance"
    if any(item in sample for item in {"pillar", "hardgate", "open_gap", "adjacent"}):
        return "physics_navigation"
    return "general_qa"


@dataclass(slots=True)
class MerlinSession:
    """Track recent Merlin conversation turns, durable memory, and telemetry."""

    turns: list[dict[str, Any]] = field(default_factory=list)
    intents: list[dict[str, Any]] = field(default_factory=list)
    policy_strikes: int = 0
    reset_events: list[dict[str, Any]] = field(default_factory=list)
    sentinel_mode: str = "MONITOR"
    privileged_attempts: int = 0
    durable_memory: list[dict[str, Any]] = field(default_factory=list)
    contradiction_events: list[dict[str, Any]] = field(default_factory=list)
    memory_audits: list[dict[str, Any]] = field(default_factory=list)
    telemetry: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.turns = list(self.turns)[-MERLIN_MAX_HISTORY:] if isinstance(self.turns, list) else []
        self.intents = list(self.intents)[-MERLIN_MAX_INTENTS:] if isinstance(self.intents, list) else []
        self.telemetry = list(self.telemetry)[-MERLIN_MAX_TELEMETRY:] if isinstance(self.telemetry, list) else []
        self.memory_audits = list(self.memory_audits)[-MERLIN_MAX_AUDITS:] if isinstance(self.memory_audits, list) else []
        self.contradiction_events = (
            list(self.contradiction_events)[-MERLIN_MAX_AUDITS:] if isinstance(self.contradiction_events, list) else []
        )
        self.reset_events = list(self.reset_events)[-MERLIN_MAX_AUDITS:] if isinstance(self.reset_events, list) else []
        self.durable_memory = list(self.durable_memory) if isinstance(self.durable_memory, list) else []
        if not self.durable_memory:
            for item in DEFAULT_DURABLE_MEMORIES:
                self.remember(item["fact"], scope=item["scope"], source=item["source"], tags=item["tags"])
        self.turns = list(self.turns)[-MERLIN_MAX_HISTORY:]
        self.intents = list(self.intents)[-MERLIN_MAX_INTENTS:]
        self.telemetry = list(self.telemetry)[-MERLIN_MAX_TELEMETRY:]
        self.memory_audits = list(self.memory_audits)[-MERLIN_MAX_AUDITS:]
        self.contradiction_events = list(self.contradiction_events)[-MERLIN_MAX_AUDITS:]

    def remember(
        self,
        fact: str,
        *,
        scope: str = "session",
        source: str = "runtime",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        clean_fact = str(fact or "").strip()
        if not clean_fact:
            raise ValueError("fact is required")
        normalized = _normalize(clean_fact)
        for entry in self.durable_memory:
            if entry["normalized_fact"] == normalized and entry["scope"] == scope:
                entry["retrieval_count"] = int(entry.get("retrieval_count", 0))
                entry["last_seen_at"] = _utcnow()
                return dict(entry)
        record = {
            "fact": clean_fact,
            "normalized_fact": normalized,
            "scope": scope,
            "source": source,
            "tags": list(tags or []),
            "created_at": _utcnow(),
            "last_seen_at": _utcnow(),
            "retrieval_count": 0,
        }
        self.durable_memory.append(record)
        return dict(record)

    def retrieve_memory(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        query_tokens = set(_normalize(query).split())
        if not query_tokens:
            return []
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in self.durable_memory:
            haystack = set(entry["normalized_fact"].split()) | {str(tag).lower() for tag in entry.get("tags", [])}
            overlap = len(query_tokens & haystack)
            if overlap:
                scored.append((overlap, entry))
        scored.sort(key=lambda item: (-item[0], item[1]["created_at"]))
        selected = [entry for _, entry in scored[:limit]]
        for entry in selected:
            entry["retrieval_count"] += 1
            entry["last_seen_at"] = _utcnow()
        return [dict(entry) for entry in selected]

    def audit_memory(self, query: str) -> dict[str, Any]:
        matched = self.retrieve_memory(query)
        audit = {
            "query": query,
            "timestamp": _utcnow(),
            "matched_memory_count": len(matched),
            "matched_scopes": sorted({item["scope"] for item in matched}),
            "matched_facts": [item["fact"] for item in matched],
            "matched_memory": matched,
        }
        self.memory_audits.append(audit)
        if len(self.memory_audits) > MERLIN_MAX_AUDITS:
            self.memory_audits = self.memory_audits[-MERLIN_MAX_AUDITS:]
        return audit

    def _record_contradiction(self, query: str, response: str) -> None:
        normalized_query = _normalize(query)
        current_gates = set(extract_gate_badges(response))
        for prior in reversed(self.turns):
            if _normalize(prior.get("query", "")) != normalized_query:
                continue
            prior_gates = set(prior.get("gates") or extract_gate_badges(str(prior.get("response", ""))))
            if prior_gates and current_gates and prior_gates != current_gates:
                self.contradiction_events.append({
                    "query": query,
                    "prior_response": str(prior.get("response", ""))[:240],
                    "new_response": str(response or "")[:240],
                    "prior_timestamp": prior.get("timestamp"),
                    "detected_at": _utcnow(),
                })
                if len(self.contradiction_events) > MERLIN_MAX_AUDITS:
                    self.contradiction_events = self.contradiction_events[-MERLIN_MAX_AUDITS:]
                return

    def add_turn(self, query: str, response: str, *, gates: list[str] | None = None) -> None:
        visible_gates = list(gates or extract_gate_badges(response))
        detected_intent = infer_intent(query)
        self._record_contradiction(query, response)
        self.turns.append({
            "query": query,
            "response": response,
            "gates": visible_gates,
            "intent": detected_intent,
            "timestamp": _utcnow(),
        })
        self.add_intent(
            query=query,
            intent=detected_intent,
            scope="session",
            provenance_sources=["query_text", "gate_badges"],
        )
        if len(self.turns) > MERLIN_MAX_HISTORY:
            self.turns = self.turns[-MERLIN_MAX_HISTORY:]

    def add_intent(
        self,
        *,
        query: str,
        intent: str,
        scope: str = "session",
        provenance_sources: list[str] | None = None,
    ) -> None:
        self.intents.append({
            "query": query,
            "intent": intent,
            "scope": scope,
            "provenance_sources": list(provenance_sources or []),
            "timestamp": _utcnow(),
        })
        if len(self.intents) > MERLIN_MAX_INTENTS:
            self.intents = self.intents[-MERLIN_MAX_INTENTS:]

    def get_history(self) -> list[dict[str, Any]]:
        return list(self.turns)

    def get_intents(self) -> list[dict[str, Any]]:
        return list(self.intents)

    def clear(self, *, reason: str = "manual") -> None:
        self.turns.clear()
        self.intents.clear()
        self.reset_events.append({
            "reason": reason,
            "timestamp": _utcnow(),
        })

    def set_sentinel_mode(self, mode: str) -> None:
        self.sentinel_mode = mode

    def register_policy_strike(self) -> int:
        self.policy_strikes += 1
        return self.policy_strikes

    def register_privileged_attempt(self) -> int:
        self.privileged_attempts += 1
        return self.privileged_attempts

    def record_run(self, run: dict[str, Any]) -> None:
        self.telemetry.append(dict(run))
        if len(self.telemetry) > MERLIN_MAX_TELEMETRY:
            self.telemetry = self.telemetry[-MERLIN_MAX_TELEMETRY:]

    def get_memory_state(self) -> dict[str, Any]:
        scopes: dict[str, int] = {}
        for entry in self.durable_memory:
            scopes[entry["scope"]] = scopes.get(entry["scope"], 0) + 1
        return {
            "tiers": ["session", "user", "repository"],
            "durable_memory_count": len(self.durable_memory),
            "durable_memory_by_scope": scopes,
            "contradiction_event_count": len(self.contradiction_events),
            "audit_count": len(self.memory_audits),
            "recent_memory_audits": self.memory_audits[-5:],
            "recent_contradictions": self.contradiction_events[-5:],
            "durable_memory": [
                {
                    "fact": item["fact"],
                    "scope": item["scope"],
                    "source": item["source"],
                    "tags": item["tags"],
                    "retrieval_count": item["retrieval_count"],
                }
                for item in self.durable_memory[-10:]
            ],
        }

    def get_public_memory_state(self) -> dict[str, Any]:
        state = self.get_memory_state()
        return {
            "tiers": state["tiers"],
            "durable_memory_count": state["durable_memory_count"],
            "durable_memory_by_scope": state["durable_memory_by_scope"],
            "contradiction_event_count": state["contradiction_event_count"],
            "audit_count": state["audit_count"],
        }

    def get_telemetry_summary(self, *, public: bool = False) -> dict[str, Any]:
        summary = summarize_runs(self.telemetry)
        if public:
            return {
                "count": summary["count"],
                "providers": summary["providers"],
                "average_latency_ms": summary["average_latency_ms"],
                "average_energy_joules": summary["average_energy_joules"],
                "average_provenance_sources": summary["average_provenance_sources"],
            }
        return summary

    def compressed(self, query: str = "", *, matched_memory: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        base = compress_context(self.turns)
        matched = list(matched_memory or [])
        if query and not matched:
            matched = self.retrieve_memory(query)
        memory_summary = " | ".join(f"[{item['scope']}] {item['fact']}" for item in matched[:3])
        contradiction_summary = (
            f" contradictions={len(self.contradiction_events)}"
            if self.contradiction_events else
            ""
        )
        summary = str(base.get("summary", "")).strip()
        if memory_summary:
            summary = f"{summary}\n[Durable Memory]\n{memory_summary}".strip()
        if contradiction_summary:
            summary = f"{summary}\n[Memory Audit]{contradiction_summary}".strip()
        base["summary"] = summary
        base["memory_hits"] = len(matched)
        base["matched_memory"] = matched
        return base

    def to_dict(self) -> dict[str, Any]:
        return {
            "turns": list(self.turns),
            "intents": list(self.intents),
            "policy_strikes": int(self.policy_strikes),
            "reset_events": list(self.reset_events),
            "sentinel_mode": str(self.sentinel_mode),
            "privileged_attempts": int(self.privileged_attempts),
            "durable_memory": list(self.durable_memory),
            "contradiction_events": list(self.contradiction_events),
            "memory_audits": list(self.memory_audits),
            "telemetry": list(self.telemetry),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MerlinSession":
        data = dict(payload or {})
        return cls(
            turns=list(data.get("turns") or []),
            intents=list(data.get("intents") or []),
            policy_strikes=int(data.get("policy_strikes", 0) or 0),
            reset_events=list(data.get("reset_events") or []),
            sentinel_mode=str(data.get("sentinel_mode") or "MONITOR"),
            privileged_attempts=int(data.get("privileged_attempts", 0) or 0),
            durable_memory=list(data.get("durable_memory") or []),
            contradiction_events=list(data.get("contradiction_events") or []),
            memory_audits=list(data.get("memory_audits") or []),
            telemetry=list(data.get("telemetry") or []),
        )
