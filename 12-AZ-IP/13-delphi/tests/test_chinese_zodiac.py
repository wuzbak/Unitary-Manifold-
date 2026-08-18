"""
DelPhi — Chinese Zodiac tests (15 tests)
"""
from __future__ import annotations

import pytest

from delphi.app.oracle.chinese_zodiac import (
    ANIMALS,
    ANIMAL_INDEX,
    build_chinese_zodiac_reading,
    get_animal,
    get_compatibility,
    get_element,
    get_yin_yang,
)


def test_animals_count():
    assert len(ANIMALS) == 12


def test_animal_index_count():
    assert len(ANIMAL_INDEX) == 12


def test_get_animal_2024_dragon():
    assert get_animal(2024)["animal"] == "Dragon"


def test_get_animal_2023_rabbit():
    assert get_animal(2023)["animal"] == "Rabbit"


def test_get_animal_2020_rat():
    assert get_animal(2020)["animal"] == "Rat"


def test_get_element_by_last_digit():
    assert get_element(2024) in {"Wood", "Fire", "Earth", "Metal", "Water"}


def test_get_element_water_year():
    assert get_element(2023) == "Water"


def test_get_element_wood_year():
    assert get_element(2024) == "Wood"


def test_yin_yang_even_year():
    assert get_yin_yang(2024) == "Yang"


def test_yin_yang_odd_year():
    assert get_yin_yang(2023) == "Yin"


def test_each_animal_has_strengths():
    for a in ANIMALS:
        assert a.get("strengths"), f"Missing strengths for {a.get('animal')}"


def test_get_compatibility_returns_dict():
    result = get_compatibility("Dragon", "Rat")
    assert isinstance(result, dict) and "score" in result


def test_build_zodiac_reading_has_summary(today):
    r = build_chinese_zodiac_reading(birth_year=1990)
    assert isinstance(r.get("summary"), str) and len(r["summary"]) > 0


def test_build_zodiac_reading_animal_name(today):
    r = build_chinese_zodiac_reading(birth_year=2024)
    assert r["animal"] == "Dragon"


def test_build_zodiac_reading_has_element(today):
    r = build_chinese_zodiac_reading(birth_year=2024)
    assert r.get("element") in {"Wood", "Fire", "Earth", "Metal", "Water"}
