# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from um_reader.engine.spaced_repetition import FlashCard, SPRINT_BA_FLASHCARDS, get_due_cards
from um_reader.engine.sprint_ba_content import (
    SPRINT_BA_CHAPTERS,
    SPRINT_BA_DIMENSIONAL_CHAIN,
    export_chapter_latex,
    get_chapter,
)


def test_sprint_ba_chapters_has_five_entries():
    assert len(SPRINT_BA_CHAPTERS) == 5


def test_sprint_ba_chapters_cover_expected_start_and_end():
    assert SPRINT_BA_CHAPTERS[0]['pillar_range'][0] == 837
    assert SPRINT_BA_CHAPTERS[-1]['pillar_range'][-1] == 860


def test_sprint_ba_chapters_have_plain_status_strings():
    assert all('score' not in chapter['status'].lower() for chapter in SPRINT_BA_CHAPTERS)


def test_sprint_ba_dimensional_chain_has_seven_steps():
    assert len(SPRINT_BA_DIMENSIONAL_CHAIN) == 7


def test_sprint_ba_dimensional_chain_is_contiguous():
    assert SPRINT_BA_DIMENSIONAL_CHAIN[0]['from_dim'] == 4
    assert SPRINT_BA_DIMENSIONAL_CHAIN[-1]['to_dim'] == 11


def test_get_chapter_returns_requested_chapter():
    assert get_chapter(3)['title'] == 'Gauge Memory and Phase'


def test_get_chapter_raises_for_missing_chapter():
    with pytest.raises(KeyError):
        get_chapter(99)


def test_export_chapter_latex_contains_cc_by_header():
    latex = export_chapter_latex(get_chapter(1))
    assert '% CC-BY 4.0' in latex


def test_export_chapter_latex_contains_title_and_range():
    latex = export_chapter_latex(get_chapter(2))
    assert 'Recursive Field Ladders' in latex
    assert 'P842--P846' in latex


def test_flashcard_dataclass_fields_round_trip():
    card = FlashCard('Q', 'A', 'P001', 2)
    assert card.question == 'Q'
    assert card.difficulty == 2


def test_sprint_ba_flashcards_minimum_count():
    assert len(SPRINT_BA_FLASHCARDS) >= 20


def test_sprint_ba_flashcards_reference_pillars():
    assert all(card.pillar_ref for card in SPRINT_BA_FLASHCARDS)


def test_get_due_cards_returns_all_unreviewed_cards():
    due = get_due_cards(SPRINT_BA_FLASHCARDS[:3], {})
    assert len(due) == 3


def test_get_due_cards_respects_interval_not_due():
    card = SPRINT_BA_FLASHCARDS[0]
    reviewed = {card.question: {'days_since': 1, 'repetitions': 2, 'ease': 2.5}}
    assert get_due_cards([card], reviewed) == []


def test_get_due_cards_marks_card_due_when_interval_elapsed():
    card = SPRINT_BA_FLASHCARDS[0]
    reviewed = {card.question: {'days_since': 20, 'repetitions': 2, 'ease': 2.5}}
    assert get_due_cards([card], reviewed) == [card]


def test_get_due_cards_mixes_due_and_not_due_cards():
    cards = SPRINT_BA_FLASHCARDS[:2]
    reviewed = {
        cards[0].question: {'days_since': 20, 'repetitions': 2, 'ease': 2.5},
        cards[1].question: {'days_since': 1, 'repetitions': 3, 'ease': 2.5},
    }
    due = get_due_cards(cards, reviewed)
    assert due == [cards[0]]
