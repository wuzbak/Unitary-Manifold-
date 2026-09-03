# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Session memory helpers for Merlin."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .gate_parser import extract_gate_badges
from .merlin_persona import compress_context

MERLIN_ACTIVE_SESSION_KEY = "merlin_active_session"
MERLIN_CACHE_KEY = "merlin_sessions_cache"
MERLIN_MAX_HISTORY = 50
MERLIN_MAX_INTENTS = 100


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
    """Track recent Merlin conversation turns."""

    turns: list[dict[str, Any]] = field(default_factory=list)
    intents: list[dict[str, Any]] = field(default_factory=list)
    policy_strikes: int = 0
    reset_events: list[dict[str, Any]] = field(default_factory=list)
    sentinel_mode: str = "MONITOR"
    privileged_attempts: int = 0

    def add_turn(self, query: str, response: str, *, gates: list[str] | None = None) -> None:
        visible_gates = list(gates or extract_gate_badges(response))
        detected_intent = infer_intent(query)
        self.turns.append({
            "query": query,
            "response": response,
            "gates": visible_gates,
            "intent": detected_intent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def set_sentinel_mode(self, mode: str) -> None:
        self.sentinel_mode = mode

    def register_policy_strike(self) -> int:
        self.policy_strikes += 1
        return self.policy_strikes

    def register_privileged_attempt(self) -> int:
        self.privileged_attempts += 1
        return self.privileged_attempts

    def compressed(self) -> dict[str, Any]:
        return compress_context(self.turns)
