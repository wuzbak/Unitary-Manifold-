"""
DelPhi — Database Seeder
Populates tarot_cards, runes, astrology_signs, chinese_zodiac_animals with
canonical data and generates offline images for each record.
"""
from __future__ import annotations

import json
import logging
import sqlite3

from delphi.app.db.schema import get_connection, init_db
from delphi.app.images.generator import (
    generate_astrology_wheel,
    generate_chinese_zodiac_card,
    generate_rune_stone,
    generate_tarot_card,
)
from delphi.app.oracle.astrology import SIGNS
from delphi.app.oracle.chinese_zodiac import ANIMALS
from delphi.app.oracle.runes import RUNES
from delphi.app.oracle.tarot import (
    DECK,
    MAJOR_ARCANA,
    MAJOR_ARCANA_DETAILS,
    SUIT_ELEMENTS,
    card_element,
    card_keywords,
    card_upright_meaning,
    card_reversed_meaning,
)

log = logging.getLogger(__name__)

_ROMAN = [
    "0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI",
]


def seed_tarot_cards(conn: sqlite3.Connection) -> int:
    """Insert all 78 tarot cards. Returns count inserted."""
    cur = conn.cursor()
    count = 0
    for idx, name in enumerate(DECK):
        arcana = "Major" if idx < 22 else "Minor"
        suit = None
        number = 0
        if arcana == "Major":
            details = MAJOR_ARCANA_DETAILS.get(name, {})
            number = details.get("number", idx)
        else:
            parts = name.split(" of ")
            if len(parts) == 2:
                suit = parts[1]

        element = card_element(name)
        roman = _ROMAN[number] if arcana == "Major" and number < len(_ROMAN) else None
        upright = card_upright_meaning(name)
        reversed_m = card_reversed_meaning(name)
        kw = card_keywords(name)
        keywords_json = json.dumps(kw.split(", ") if kw else [])

        image_blob = generate_tarot_card(
            card_name=name,
            element=element,
            arcana=arcana,
            suit=suit,
            roman_numeral=roman,
        )

        try:
            cur.execute(
                """INSERT OR IGNORE INTO tarot_cards
                   (name, arcana, suit, number, element, roman_numeral,
                    upright_meaning, reversed_meaning, keywords, image_blob)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (name, arcana, suit, number, element, roman,
                 upright, reversed_m, keywords_json, image_blob),
            )
            if cur.rowcount:
                count += 1
        except sqlite3.Error as exc:
            log.warning("tarot_cards insert failed for %s: %s", name, exc)

    conn.commit()
    return count


def seed_runes(conn: sqlite3.Connection) -> int:
    """Insert all 24 Elder Futhark runes. Returns count inserted."""
    cur = conn.cursor()
    count = 0
    for rune in RUNES:
        name: str = rune["name"]
        symbol: str = rune["symbol"]
        phoneme: str = rune.get("phoneme", "")
        element: str = rune.get("element", "Earth")
        upright: str = rune.get("upright_meaning", "")
        reversed_m: str = rune.get("reversed_meaning", "")
        kw = rune.get("keywords", "")
        keywords_json = json.dumps(kw.split(", ") if kw else [])

        image_blob = generate_rune_stone(name, symbol, element)

        try:
            cur.execute(
                """INSERT OR IGNORE INTO runes
                   (name, symbol, phoneme, element,
                    upright_meaning, reversed_meaning, keywords, image_blob)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (name, symbol, phoneme, element, upright, reversed_m, keywords_json, image_blob),
            )
            if cur.rowcount:
                count += 1
        except sqlite3.Error as exc:
            log.warning("runes insert failed for %s: %s", name, exc)

    conn.commit()
    return count


def seed_astrology_signs(conn: sqlite3.Connection) -> int:
    """Insert all 12 Western astrology signs. Returns count inserted."""
    cur = conn.cursor()
    count = 0
    for sign in SIGNS:
        name: str = sign["name"]
        image_blob = generate_astrology_wheel(signs_highlighted=[name])

        try:
            cur.execute(
                """INSERT OR IGNORE INTO astrology_signs
                   (name, symbol, element, modality, ruling_planet,
                    date_range, traits, image_blob)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    name,
                    sign.get("symbol", ""),
                    sign.get("element", ""),
                    sign.get("modality", ""),
                    sign.get("ruler", ""),
                    sign.get("date_range", ""),
                    json.dumps(sign.get("keywords", "").split(", ") if sign.get("keywords") else []),
                    image_blob,
                ),
            )
            if cur.rowcount:
                count += 1
        except sqlite3.Error as exc:
            log.warning("astrology_signs insert failed for %s: %s", name, exc)

    conn.commit()
    return count


def seed_chinese_zodiac_animals(conn: sqlite3.Connection) -> int:
    """Insert all 12 Chinese zodiac animals. Returns count inserted."""
    cur = conn.cursor()
    count = 0
    example_years = {
        "Rat": [1924, 1936, 1948, 1960, 1972, 1984, 1996, 2008, 2020],
        "Ox": [1925, 1937, 1949, 1961, 1973, 1985, 1997, 2009, 2021],
        "Tiger": [1926, 1938, 1950, 1962, 1974, 1986, 1998, 2010, 2022],
        "Rabbit": [1927, 1939, 1951, 1963, 1975, 1987, 1999, 2011, 2023],
        "Dragon": [1928, 1940, 1952, 1964, 1976, 1988, 2000, 2012, 2024],
        "Snake": [1929, 1941, 1953, 1965, 1977, 1989, 2001, 2013, 2025],
        "Horse": [1930, 1942, 1954, 1966, 1978, 1990, 2002, 2014, 2026],
        "Goat": [1931, 1943, 1955, 1967, 1979, 1991, 2003, 2015, 2027],
        "Monkey": [1932, 1944, 1956, 1968, 1980, 1992, 2004, 2016, 2028],
        "Rooster": [1933, 1945, 1957, 1969, 1981, 1993, 2005, 2017, 2029],
        "Dog": [1934, 1946, 1958, 1970, 1982, 1994, 2006, 2018, 2030],
        "Pig": [1935, 1947, 1959, 1971, 1983, 1995, 2007, 2019, 2031],
    }

    for animal in ANIMALS:
        name: str = animal["animal"]
        element: str = animal.get("element_affinity", "Earth")
        yin_yang: str = animal.get("yin_yang", "Yang")
        trine: int = 1  # trine_group is a string; use ordinal
        trine_str: str = animal.get("trine_group", "First Trine")
        trine_map = {"First Trine": 1, "Second Trine": 2, "Third Trine": 3, "Fourth Trine": 4}
        trine = trine_map.get(trine_str, 1)
        traits_str: str = animal.get("strengths", "")
        years: list = example_years.get(name, [])

        year_ex = years[4] if len(years) > 4 else (years[0] if years else 1960)
        image_blob = generate_chinese_zodiac_card(name, element, year_ex, yin_yang)

        try:
            cur.execute(
                """INSERT OR IGNORE INTO chinese_zodiac_animals
                   (name, element, yin_yang, trine, years_example, traits, image_blob)
                   VALUES (?,?,?,?,?,?,?)""",
                (name, element, yin_yang, trine,
                 json.dumps(years), json.dumps(traits_str.split(", ") if traits_str else []),
                 image_blob),
            )
            if cur.rowcount:
                count += 1
        except sqlite3.Error as exc:
            log.warning("chinese_zodiac_animals insert failed for %s: %s", name, exc)

    conn.commit()
    return count


def seed_database(db_path: str | None = None) -> dict[str, int]:
    """Seed all lookup tables. Idempotent (uses INSERT OR IGNORE)."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        results = {
            "tarot_cards": seed_tarot_cards(conn),
            "runes": seed_runes(conn),
            "astrology_signs": seed_astrology_signs(conn),
            "chinese_zodiac_animals": seed_chinese_zodiac_animals(conn),
        }
        log.info("Seeding complete: %s", results)
        return results
    finally:
        conn.close()


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
