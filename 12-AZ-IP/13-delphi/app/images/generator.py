# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Deterministic offline PNG generators for DelPhi assets."""
from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageDraw

_ELEMENT_COLORS: dict[str, tuple[int, int, int]] = {
    'Air': (180, 210, 235),
    'Earth': (115, 145, 80),
    'Fire': (185, 85, 55),
    'Metal': (160, 160, 175),
    'Water': (55, 95, 175),
    'Wood': (65, 135, 85),
}


def _to_png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def _canvas(width: int, height: int, element: str) -> Image.Image:
    color = _ELEMENT_COLORS.get(element, (72, 72, 96))
    return Image.new('RGB', (width, height), color)


def generate_tarot_card(
    card_name: str,
    element: str = 'Air',
    arcana: str = 'Major',
    suit: str | None = None,
    roman_numeral: str | None = None,
) -> bytes:
    """Generate a simple 300x500 tarot card image."""
    image = _canvas(300, 500, element)
    draw = ImageDraw.Draw(image)
    draw.rectangle((15, 15, 285, 485), outline=(250, 250, 250), width=4)
    draw.text((24, 24), card_name, fill=(15, 15, 20))
    draw.text((24, 54), f'{arcana} {suit or ""}'.strip(), fill=(20, 20, 20))
    if roman_numeral:
        draw.text((24, 84), roman_numeral, fill=(20, 20, 20))
    return _to_png_bytes(image)


def generate_rune_stone(name: str, symbol: str, element: str = 'Earth') -> bytes:
    """Generate a simple rune-stone PNG."""
    image = _canvas(256, 256, element)
    draw = ImageDraw.Draw(image)
    draw.ellipse((20, 20, 236, 236), outline=(235, 235, 235), width=5)
    draw.text((112, 92), symbol, fill=(15, 15, 15))
    draw.text((70, 190), name, fill=(15, 15, 15))
    return _to_png_bytes(image)


def generate_astrology_wheel(signs_highlighted: list[str] | None = None) -> bytes:
    """Generate a simple astrology wheel PNG."""
    image = _canvas(320, 320, 'Air')
    draw = ImageDraw.Draw(image)
    draw.ellipse((20, 20, 300, 300), outline=(240, 240, 240), width=4)
    labels = ', '.join(signs_highlighted or ['Zodiac'])
    draw.text((40, 145), labels[:24], fill=(20, 20, 20))
    return _to_png_bytes(image)


def generate_chinese_zodiac_card(animal: str, element: str, year: int, yin_yang: str) -> bytes:
    """Generate a simple 300x400 Chinese-zodiac card PNG."""
    image = _canvas(300, 400, element)
    draw = ImageDraw.Draw(image)
    draw.rectangle((18, 18, 282, 382), outline=(245, 245, 245), width=4)
    draw.text((28, 36), animal, fill=(15, 15, 20))
    draw.text((28, 72), f'{element} · {yin_yang}', fill=(15, 15, 20))
    draw.text((28, 108), str(year), fill=(15, 15, 20))
    return _to_png_bytes(image)
