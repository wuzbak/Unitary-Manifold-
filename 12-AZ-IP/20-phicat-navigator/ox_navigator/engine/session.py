# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""In-memory session history for OX prompts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .constants import MAX_HISTORY


@dataclass(slots=True)
class OxSession:
    """Track recent query/response turns for prompt continuity."""

    turns: list[dict] = field(default_factory=list)

    def add_turn(self, query: str, response: str) -> None:
        self.turns.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        if len(self.turns) > MAX_HISTORY:
            self.turns = self.turns[-MAX_HISTORY:]

    def get_history(self) -> list[dict]:
        return list(self.turns)

    def clear(self) -> None:
        self.turns.clear()

    def to_prompt_context(self) -> str:
        if not self.turns:
            return 'No prior conversation.'
        lines = ['Conversation history:']
        for idx, turn in enumerate(self.turns, start=1):
            lines.append(f"Turn {idx} User: {turn['query']}")
            lines.append(f"Turn {idx} Assistant: {turn['response']}")
        return '\n'.join(lines)
