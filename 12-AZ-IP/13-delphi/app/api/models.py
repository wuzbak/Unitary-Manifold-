"""
DelPhi — Pydantic API Models
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReadingRequest(BaseModel):
    oracle_type: str = Field(..., description="tarot | rune | astrology | chinese_zodiac")
    spread_type: Optional[str] = Field(None, description="Spread variant")
    question: Optional[str] = Field(None, description="User's question")
    user_id: str = Field("anonymous", description="User identifier")
    birth_date: Optional[str] = Field(None, description="YYYY-MM-DD for astrology/zodiac")
    birth_time: Optional[str] = Field(None, description="HH:MM for rising sign")
    year: Optional[int] = Field(None, description="Birth year for Chinese zodiac")


class DrawnCard(BaseModel):
    position: str
    name: str
    arcana: str
    reversed: bool
    meaning: str
    element: Optional[str] = None


class DrawnRune(BaseModel):
    position: str
    name: str
    symbol: str
    reversed: bool
    meaning: str
    element: Optional[str] = None


class ReadingResponse(BaseModel):
    reading_id: Optional[int] = None
    oracle_type: str
    spread_type: str
    question: Optional[str] = None
    seed: int
    cards: Optional[list[DrawnCard]] = None
    runes: Optional[list[DrawnRune]] = None
    synthesis: str
    raw: Optional[dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    oracle_type: str = Field("tarot", description="tarot | rune")
    limit: int = Field(10, ge=1, le=50)


class SearchResult(BaseModel):
    id: int
    name: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    oracle_type: str
    results: list[SearchResult]


class HoroscopeRequest(BaseModel):
    sign: str
    date: Optional[str] = Field(None, description="YYYY-MM-DD (defaults to today)")


class HoroscopeResponse(BaseModel):
    sign: str
    date: str
    horoscope: str


class ZodiacRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)


class ZodiacResponse(BaseModel):
    year: int
    animal: str
    element: str
    yin_yang: str
    trine: int
    traits: list[str]
    forecast: str


class HealthResponse(BaseModel):
    status: str
    version: str
    db_ok: bool
    engines: list[str]


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
