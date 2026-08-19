"""
DelPhi — Tarot tests (20 tests)
"""
from __future__ import annotations

import pytest

from delphi.app.oracle.tarot import (
    DECK,
    MAJOR_ARCANA,
    MAJOR_ARCANA_DETAILS,
    MINOR_ARCANA,
    SUIT_ELEMENTS,
    build_reading,
    build_seed,
    draw_celtic_cross,
    draw_single_card,
    draw_three_card,
)


def test_deck_has_78_cards():
    assert len(DECK) == 78


def test_major_arcana_count():
    assert len(MAJOR_ARCANA) == 22


def test_minor_arcana_count():
    assert len(MINOR_ARCANA) == 56


def test_all_four_suits_present():
    suits = set()
    for name in MINOR_ARCANA:
        parts = name.split(" of ")
        if len(parts) == 2:
            suits.add(parts[1])
    assert suits == {"Wands", "Cups", "Swords", "Pentacles"}


def test_each_suit_has_14_cards():
    for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
        cards = [n for n in MINOR_ARCANA if n.endswith(f" of {suit}")]
        assert len(cards) == 14, f"{suit} should have 14 cards, got {len(cards)}"


def test_major_arcana_details_has_22_entries():
    assert len(MAJOR_ARCANA_DETAILS) == 22


def test_major_arcana_details_has_upright_and_reversed():
    for name, details in MAJOR_ARCANA_DETAILS.items():
        assert "upright" in details, f"Missing upright for {name}"
        assert "reversed" in details, f"Missing reversed for {name}"


def test_suit_elements_has_four_suits():
    assert set(SUIT_ELEMENTS.keys()) == {"Wands", "Cups", "Swords", "Pentacles"}


def test_build_seed_is_deterministic():
    s1, _ = build_seed("What is my path?", "user1", "2024-01-01")
    s2, _ = build_seed("What is my path?", "user1", "2024-01-01")
    assert s1 == s2


def test_build_seed_differs_by_question():
    s1, _ = build_seed("path?", "user1", "2024-01-01")
    s2, _ = build_seed("love?", "user1", "2024-01-01")
    assert s1 != s2


def test_build_seed_within_uint32():
    s, _ = build_seed("test", "u", "2024-01-01")
    assert 0 <= s < 2**32


def test_draw_single_card_returns_one():
    cards = draw_single_card(42)
    assert len(cards) == 1
    assert "card_name" in cards[0]


def test_draw_three_card_returns_three():
    cards = draw_three_card(42)
    assert len(cards) == 3


def test_draw_three_card_positions():
    cards = draw_three_card(42)
    positions = [c["position_name"] for c in cards]
    assert any("Past" in p for p in positions)
    assert any("Present" in p for p in positions)
    assert any("Future" in p for p in positions)


def test_draw_celtic_cross_returns_ten():
    cards = draw_celtic_cross(42)
    assert len(cards) == 10


def test_draw_celtic_cross_no_duplicates():
    cards = draw_celtic_cross(42)
    names = [c["card_name"] for c in cards]
    assert len(names) == len(set(names))


def test_build_reading_tarot_single(today):
    r = build_reading(question="test", user_id="u", reading_date=today, spread_type="single_card")
    assert r["spread_type"] == "single_card"
    assert len(r["cards"]) == 1
    assert "synthesis" in r


def test_build_reading_three_card(today):
    r = build_reading(question="test", user_id="u", reading_date=today, spread_type="three_card")
    assert len(r["cards"]) == 3


def test_build_reading_celtic_cross(today):
    r = build_reading(question="test", user_id="u", reading_date=today, spread_type="celtic_cross")
    assert len(r["cards"]) == 10


def test_build_reading_synthesis_is_string(today):
    r = build_reading(question="fortune", user_id="u", reading_date=today, spread_type="three_card")
    assert isinstance(r["synthesis"], str)
    assert len(r["synthesis"]) > 0
