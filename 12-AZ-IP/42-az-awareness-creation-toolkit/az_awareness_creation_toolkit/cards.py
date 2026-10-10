# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 5: knowledge card deck creation with SM-2 spaced repetition.

Generalizes the fixed, bundled deck in Product 20's
`ox_navigator/engine/flashcard.py` (which only loads one hard-coded
physics deck) into a true creation tool: arbitrary question/answer/
category triples, scheduled with the classic SuperMemo-2 algorithm.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, replace
from typing import Iterable, List, Sequence, Tuple

_DEFAULT_EASE_FACTOR = 2.5
_MIN_EASE_FACTOR = 1.3


class InvalidReviewQualityError(ValueError):
    """Raised when a review quality score is outside the SM-2 range 0-5."""


@dataclass(frozen=True)
class KnowledgeCard:
    card_id: str
    question: str
    answer: str
    category: str
    ease_factor: float
    interval_days: int
    repetitions: int
    due_date: str  # ISO 8601 date

    def as_dict(self) -> dict:
        return {
            "card_id": self.card_id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "ease_factor": round(self.ease_factor, 3),
            "interval_days": self.interval_days,
            "repetitions": self.repetitions,
            "due_date": self.due_date,
        }


def create_card_deck(
    cards: Iterable[Tuple[str, str, str]],
    created_on: _dt.date = None,
) -> List[KnowledgeCard]:
    """Create a fresh deck from (question, answer, category) triples.

    Every new card starts due immediately (``repetitions=0``), matching
    SM-2's convention that an unreviewed card is always due.
    """
    today = created_on or _dt.date.today()
    deck: List[KnowledgeCard] = []
    for index, (question, answer, category) in enumerate(cards):
        if not str(question).strip() or not str(answer).strip():
            raise ValueError("question and answer must both be non-empty")
        deck.append(
            KnowledgeCard(
                card_id=f"card-{index + 1:04d}",
                question=str(question),
                answer=str(answer),
                category=str(category) if category else "general",
                ease_factor=_DEFAULT_EASE_FACTOR,
                interval_days=0,
                repetitions=0,
                due_date=today.isoformat(),
            )
        )
    return deck


def review_card(card: KnowledgeCard, quality: int, reviewed_on: _dt.date = None) -> KnowledgeCard:
    """Apply one SM-2 review step and return the updated card.

    ``quality`` is the standard SM-2 0-5 self-assessed recall grade
    (0 = total blackout, 5 = perfect recall). Grades below 3 reset the
    repetition count and interval, per the original SM-2 specification.
    """
    if not isinstance(quality, int) or not (0 <= quality <= 5):
        raise InvalidReviewQualityError(f"quality must be an int 0-5, got {quality!r}")

    today = reviewed_on or _dt.date.today()
    ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease_factor = max(ease_factor, _MIN_EASE_FACTOR)

    if quality < 3:
        repetitions = 0
        interval_days = 1
    else:
        repetitions = card.repetitions + 1
        if repetitions == 1:
            interval_days = 1
        elif repetitions == 2:
            interval_days = 6
        else:
            interval_days = round(card.interval_days * ease_factor) or 1

    due_date = today + _dt.timedelta(days=interval_days)
    return replace(
        card,
        ease_factor=ease_factor,
        interval_days=interval_days,
        repetitions=repetitions,
        due_date=due_date.isoformat(),
    )


def due_cards(deck: Sequence[KnowledgeCard], as_of: _dt.date = None) -> List[KnowledgeCard]:
    today = as_of or _dt.date.today()
    return [card for card in deck if _dt.date.fromisoformat(card.due_date) <= today]
