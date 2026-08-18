"""
DelPhi — Image generator tests (9 tests)
"""
from __future__ import annotations

import io

import pytest
from PIL import Image

from delphi.app.images.generator import (
    generate_astrology_wheel,
    generate_chinese_zodiac_card,
    generate_rune_stone,
    generate_tarot_card,
)


def test_tarot_card_returns_bytes():
    data = generate_tarot_card("The Fool", element="Air", arcana="Major", roman_numeral="0")
    assert isinstance(data, bytes) and len(data) > 0


def test_tarot_card_is_valid_png():
    data = generate_tarot_card("The World", element="Earth", arcana="Major")
    img = Image.open(io.BytesIO(data))
    assert img.format == "PNG"


def test_tarot_card_dimensions():
    data = generate_tarot_card("Ace of Wands", element="Fire", arcana="Minor", suit="Wands")
    img = Image.open(io.BytesIO(data))
    assert img.size == (300, 500)


def test_rune_stone_returns_bytes():
    data = generate_rune_stone("Fehu", "ᚠ", "Fire")
    assert isinstance(data, bytes) and len(data) > 0


def test_rune_stone_is_valid_png():
    data = generate_rune_stone("Uruz", "ᚢ", "Earth")
    img = Image.open(io.BytesIO(data))
    assert img.format == "PNG"


def test_astrology_wheel_returns_bytes():
    data = generate_astrology_wheel(signs_highlighted=["Aries"])
    assert isinstance(data, bytes) and len(data) > 0


def test_astrology_wheel_is_valid_png():
    data = generate_astrology_wheel()
    img = Image.open(io.BytesIO(data))
    assert img.format == "PNG"


def test_chinese_zodiac_card_returns_bytes():
    data = generate_chinese_zodiac_card("Dragon", "Wood", 2024, "Yang")
    assert isinstance(data, bytes) and len(data) > 0


def test_chinese_zodiac_card_dimensions():
    data = generate_chinese_zodiac_card("Rabbit", "Water", 2023, "Yin")
    img = Image.open(io.BytesIO(data))
    assert img.size == (300, 400)
