"""
DelPhi — Rune tests (15 tests)
"""
from __future__ import annotations

import pytest

from delphi.app.oracle.runes import (
    RUNES,
    RUNE_INDEX,
    build_rune_reading,
    build_seed,
    draw_runic_cross,
    draw_single_rune,
    draw_three_rune,
)


def test_runes_count():
    assert len(RUNES) == 24


def test_rune_index_has_24():
    assert len(RUNE_INDEX) == 24


def test_each_rune_has_symbol():
    for r in RUNES:
        assert r.get("symbol"), f"Rune {r.get('name')} missing symbol"


def test_each_rune_has_upright_and_reversed():
    for r in RUNES:
        assert r.get("upright_meaning"), f"Missing upright for {r.get('name')}"
        assert r.get("reversed_meaning"), f"Missing reversed for {r.get('name')}"


def test_rune_seed_deterministic():
    s1, _ = build_seed("test", "u", "2024-01-01")
    s2, _ = build_seed("test", "u", "2024-01-01")
    assert s1 == s2


def test_draw_single_rune():
    cast = draw_single_rune(99)
    assert len(cast) == 1
    assert "rune" in cast[0]
    assert "name" in cast[0]["rune"]


def test_draw_single_rune_has_reversed():
    cast = draw_single_rune(99)
    assert "is_reversed" in cast[0]["rune"]


def test_draw_three_rune_count():
    cast = draw_three_rune(99)
    assert len(cast) == 3


def test_draw_three_rune_positions():
    cast = draw_three_rune(99)
    position_names = [c["position"]["name"] for c in cast]
    assert any("Past" in p for p in position_names)
    assert any("Present" in p for p in position_names)
    assert any("Future" in p for p in position_names)


def test_draw_runic_cross_count():
    cast = draw_runic_cross(99)
    assert len(cast) == 6


def test_draw_runic_cross_no_duplicates():
    cast = draw_runic_cross(99)
    names = [c["rune"]["name"] for c in cast]
    assert len(names) == len(set(names))


def test_build_rune_reading_single(today):
    r = build_rune_reading("help", user_id="u", reading_date=today, spread_type="single")
    assert len(r["cast"]) == 1
    assert "synthesis" in r


def test_build_rune_reading_three(today):
    r = build_rune_reading("path", user_id="u", reading_date=today, spread_type="three_rune")
    assert len(r["cast"]) == 3


def test_build_rune_reading_cross(today):
    r = build_rune_reading("path", user_id="u", reading_date=today, spread_type="runic_cross")
    assert len(r["cast"]) == 6


def test_build_rune_reading_synthesis_nonempty(today):
    r = build_rune_reading("journey", user_id="u", reading_date=today, spread_type="three_rune")
    assert isinstance(r["synthesis"], str) and len(r["synthesis"]) > 0
