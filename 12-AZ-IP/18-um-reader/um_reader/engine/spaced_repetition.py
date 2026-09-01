# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Spaced-repetition helpers for Sprint BA cards."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FlashCard:
    question: str
    answer: str
    pillar_ref: str
    difficulty: int


SPRINT_BA_FLASHCARDS = [
    FlashCard('What dimensional transition opens Sprint BA?', '4D to 5D via KK compactification.', 'P837', 2),
    FlashCard('Which pillar anchors the first Sprint BA step?', 'P837.', 'P837', 1),
    FlashCard('What is the step-two destination dimension?', '6D.', 'P840', 2),
    FlashCard('Which mechanism defines the 5D→6D lift?', 'Scalar closure lift.', 'P840', 3),
    FlashCard('What dimensional jump follows 6D?', '6D to 7D.', 'P844', 2),
    FlashCard('Which mechanism shapes the 6D→7D move?', 'Torsion-informed flavor extension.', 'P844', 3),
    FlashCard('What dimension follows 7D in Sprint BA?', '8D.', 'P848', 1),
    FlashCard('What routing idea drives the 7D→8D step?', 'Wilson-line gauge routing.', 'P848', 3),
    FlashCard('Which step references anomaly cancellation?', '8D to 9D.', 'P851', 2),
    FlashCard('What is the destination of the anomaly-refinement step?', '9D.', 'P851', 2),
    FlashCard('Which mechanism frames the 9D→10D jump?', 'Flux landscape bookkeeping.', 'P855', 3),
    FlashCard('What is the capstone dimension in Sprint BA?', '11D.', 'P860', 1),
    FlashCard('Which reduction closes the dimensional chain?', 'Horava-Witten capstone reduction.', 'P860', 3),
    FlashCard('How many chapters are defined for Sprint BA?', 'Five chapters.', 'P837-P860', 1),
    FlashCard('How many dimensional chain steps are defined?', 'Seven steps.', 'P837-P860', 1),
    FlashCard('What status labels replace score language?', 'Plain epistemic statuses such as research draft or editorial preview.', 'P857', 2),
    FlashCard('Which chapter covers pillars 852–856?', 'Higher-Dimensional Closure.', 'P852-P856', 2),
    FlashCard('Which chapter ends at P860?', 'Reader Synthesis Window.', 'P857-P860', 2),
    FlashCard('What does Threshold Geometry summarize?', 'The move from readable 4D intuition into compact 5D geometry.', 'P837-P841', 2),
    FlashCard('What does Reader Synthesis Window emphasize?', 'An 11D capstone with explicit epistemic caveats and review prompts.', 'P857-P860', 2),
]


def _interval_days(record: dict, difficulty: int) -> int:
    repetitions = int(record.get('repetitions', 0))
    ease = float(record.get('ease', 2.5))
    if repetitions <= 0:
        return 0
    interval = max(1.0, 6.0 - difficulty)
    for _ in range(1, repetitions):
        interval *= ease
    return max(1, int(round(interval)))


def get_due_cards(deck: list[FlashCard], reviewed: dict) -> list[FlashCard]:
    """Return cards due for review using a lightweight SM-2-style interval."""
    due: list[FlashCard] = []
    for card in deck:
        record = reviewed.get(card.question)
        if not record:
            due.append(card)
            continue
        days_since = float(record.get('days_since', 0))
        if days_since >= _interval_days(record, card.difficulty):
            due.append(card)
    return due
