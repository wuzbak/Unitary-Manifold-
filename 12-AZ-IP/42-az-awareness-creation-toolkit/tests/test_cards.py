# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import datetime as dt
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_awareness_creation_toolkit.cards import (
    InvalidReviewQualityError,
    create_card_deck,
    due_cards,
    review_card,
)


def test_create_card_deck_basic():
    deck = create_card_deck([
        ("Q1", "A1", "cat-a"),
        ("Q2", "A2", "cat-b"),
    ], created_on=dt.date(2026, 1, 1))
    assert len(deck) == 2
    assert deck[0].card_id == "card-0001"
    assert deck[0].ease_factor == 2.5
    assert deck[0].repetitions == 0
    assert deck[0].due_date == "2026-01-01"


def test_create_card_deck_defaults_category():
    deck = create_card_deck([("Q", "A", "")])
    assert deck[0].category == "general"


def test_create_card_deck_rejects_blank_question_or_answer():
    with pytest.raises(ValueError):
        create_card_deck([("", "A", "cat")])
    with pytest.raises(ValueError):
        create_card_deck([("Q", "   ", "cat")])


def test_review_card_good_recall_advances_interval():
    deck = create_card_deck([("Q", "A", "cat")], created_on=dt.date(2026, 1, 1))
    card = deck[0]

    first = review_card(card, 5, reviewed_on=dt.date(2026, 1, 1))
    assert first.repetitions == 1
    assert first.interval_days == 1
    assert first.due_date == "2026-01-02"

    second = review_card(first, 5, reviewed_on=dt.date(2026, 1, 2))
    assert second.repetitions == 2
    assert second.interval_days == 6
    assert second.due_date == "2026-01-08"

    third = review_card(second, 5, reviewed_on=dt.date(2026, 1, 8))
    assert third.repetitions == 3
    assert third.interval_days > second.interval_days
    assert third.ease_factor >= second.ease_factor


def test_review_card_poor_recall_resets_repetitions():
    deck = create_card_deck([("Q", "A", "cat")], created_on=dt.date(2026, 1, 1))
    advanced = review_card(deck[0], 5, reviewed_on=dt.date(2026, 1, 1))
    advanced = review_card(advanced, 5, reviewed_on=dt.date(2026, 1, 2))
    lapsed = review_card(advanced, 1, reviewed_on=dt.date(2026, 1, 8))
    assert lapsed.repetitions == 0
    assert lapsed.interval_days == 1


def test_review_card_ease_factor_floor():
    deck = create_card_deck([("Q", "A", "cat")])
    card = deck[0]
    for _ in range(20):
        card = review_card(card, 0)
    assert card.ease_factor >= 1.3


def test_review_card_rejects_invalid_quality():
    deck = create_card_deck([("Q", "A", "cat")])
    with pytest.raises(InvalidReviewQualityError):
        review_card(deck[0], 6)
    with pytest.raises(InvalidReviewQualityError):
        review_card(deck[0], -1)


def test_due_cards_filters_by_date():
    deck = create_card_deck([("Q1", "A1", "cat")], created_on=dt.date(2026, 1, 1))
    reviewed = review_card(deck[0], 5, reviewed_on=dt.date(2026, 1, 1))
    assert due_cards([reviewed], as_of=dt.date(2026, 1, 1)) == []
    assert due_cards([reviewed], as_of=dt.date(2026, 1, 2)) == [reviewed]
