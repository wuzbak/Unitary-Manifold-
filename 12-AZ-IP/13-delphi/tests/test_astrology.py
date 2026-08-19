"""
DelPhi — Astrology tests (20 tests)
"""
from __future__ import annotations

from datetime import date

import pytest

from delphi.app.oracle.astrology import (
    SIGNS,
    SIGN_INDEX,
    build_astrology_reading,
    get_daily_horoscope,
    get_moon_sign,
    get_rising_sign,
    get_sun_sign,
)


def test_signs_count():
    assert len(SIGNS) == 12


def test_sign_index_count():
    assert len(SIGN_INDEX) == 12


def test_each_sign_has_element():
    for s in SIGNS:
        assert s.get("element") in {"Fire", "Earth", "Air", "Water"}


def test_each_sign_has_modality():
    for s in SIGNS:
        assert s.get("modality") in {"Cardinal", "Fixed", "Mutable"}


def test_each_sign_has_horoscopes():
    from delphi.app.oracle.astrology import HOROSCOPE_TEMPLATES
    for s in SIGNS:
        assert len(HOROSCOPE_TEMPLATES.get(s["name"], [])) >= 5


# Sun sign correctness
def test_sun_sign_aries():
    assert get_sun_sign(date(2024, 3, 25))["name"] == "Aries"


def test_sun_sign_leo():
    assert get_sun_sign(date(2024, 8, 10))["name"] == "Leo"


def test_sun_sign_capricorn_december():
    assert get_sun_sign(date(2024, 12, 25))["name"] == "Capricorn"


def test_sun_sign_capricorn_january():
    assert get_sun_sign(date(2024, 1, 10))["name"] == "Capricorn"


def test_sun_sign_pisces():
    assert get_sun_sign(date(2024, 3, 1))["name"] == "Pisces"


def test_sun_sign_scorpio():
    assert get_sun_sign(date(2024, 11, 5))["name"] == "Scorpio"


def test_moon_sign_returns_valid():
    sign = get_moon_sign(date(1990, 6, 15))
    assert sign["name"] in SIGN_INDEX


def test_rising_sign_returns_valid():
    sign = get_rising_sign(date(1990, 6, 15), birth_hour=14, birth_minute=30)
    assert sign["name"] in SIGN_INDEX


def test_rising_sign_no_time():
    sign = get_rising_sign(date(1990, 6, 15))
    assert sign["name"] in SIGN_INDEX


def test_daily_horoscope_returns_string():
    h = get_daily_horoscope("Aries", date(2024, 1, 1))
    assert isinstance(h, str) and len(h) > 0


def test_daily_horoscope_deterministic():
    h1 = get_daily_horoscope("Leo", date(2024, 6, 15))
    h2 = get_daily_horoscope("Leo", date(2024, 6, 15))
    assert h1 == h2


def test_daily_horoscope_unknown_sign_returns_fallback():
    # Unknown signs return a fallback string (not None)
    h = get_daily_horoscope("Xenon", date(2024, 1, 1))
    assert isinstance(h, str)


def test_build_astrology_reading_sun_sign(today):
    r = build_astrology_reading(birth_date_str="1985-04-10")
    assert r.get("sun_sign", {}).get("name") == "Aries"


def test_build_astrology_reading_has_moon_sign(today):
    r = build_astrology_reading(birth_date_str="1990-07-20")
    assert "moon_sign" in r
    assert isinstance(r["moon_sign"], dict)


def test_build_astrology_reading_has_rising_sign(today):
    r = build_astrology_reading(birth_date_str="1990-07-20", birth_time_str="14:30")
    assert "rising_sign" in r
    assert isinstance(r["rising_sign"], dict)
