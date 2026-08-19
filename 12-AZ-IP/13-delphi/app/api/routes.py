"""
DelPhi — FastAPI Routes
"""
from __future__ import annotations

from delphi import __version__
import json
import logging
from datetime import date as _date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from delphi.app.api.models import (
    HealthResponse,
    HoroscopeResponse,
    ReadingRequest,
    ReadingResponse,
    SearchResponse,
    SearchResult,
    ZodiacResponse,
)
from delphi.app.config import get_config
from delphi.app.db.schema import get_connection
from delphi.app.oracle.astrology import (
    build_astrology_reading,
    get_daily_horoscope,
    get_sun_sign,
    SIGN_INDEX,
)
from delphi.app.oracle.chinese_zodiac import build_chinese_zodiac_reading, get_animal
from delphi.app.oracle.runes import build_rune_reading
from delphi.app.oracle.tarot import build_reading as build_tarot_reading

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_ok = False
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        pass
    return HealthResponse(
        status="ok",
        version=__version__,
        db_ok=db_ok,
        engines=["tarot", "rune", "astrology", "chinese_zodiac"],
    )


@router.post("/reading", response_model=ReadingResponse)
def create_reading(req: ReadingRequest) -> ReadingResponse:
    today = _date.today().isoformat()
    oracle = req.oracle_type.lower()

    if oracle == "tarot":
        spread = req.spread_type or "three_card"
        raw = build_tarot_reading(
            question=req.question or "",
            user_id=req.user_id,
            reading_date=today,
            spread_type=spread,
        )
        resp = ReadingResponse(
            oracle_type="tarot",
            spread_type=spread,
            question=req.question,
            seed=raw["seed_int"],
            synthesis=raw["synthesis"],
            raw=raw,
        )

    elif oracle == "rune":
        spread = req.spread_type or "three_rune"
        raw = build_rune_reading(
            question=req.question or "",
            user_id=req.user_id,
            reading_date=today,
            spread_type=spread,
        )
        resp = ReadingResponse(
            oracle_type="rune",
            spread_type=spread,
            question=req.question,
            seed=raw["seed_int"],
            synthesis=raw["synthesis"],
            raw=raw,
        )

    elif oracle == "astrology":
        if not req.birth_date:
            raise HTTPException(status_code=422, detail="birth_date required for astrology reading")
        raw = build_astrology_reading(
            birth_date_str=req.birth_date,
            birth_time_str=req.birth_time,
            user_id=req.user_id,
        )
        resp = ReadingResponse(
            oracle_type="astrology",
            spread_type="natal",
            question=req.question,
            seed=0,
            synthesis=raw.get("natal_summary", ""),
            raw=raw,
        )

    elif oracle == "chinese_zodiac":
        year = req.year
        if year is None and req.birth_date:
            year = int(req.birth_date.split("-")[0])
        if year is None:
            raise HTTPException(status_code=422, detail="year or birth_date required for Chinese zodiac")
        raw = build_chinese_zodiac_reading(birth_year=year, user_id=req.user_id)
        resp = ReadingResponse(
            oracle_type="chinese_zodiac",
            spread_type="annual",
            question=req.question,
            seed=0,
            synthesis=raw.get("summary", ""),
            raw=raw,
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown oracle_type: {oracle!r}")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO readings
               (oracle_type, spread_type, question, user_id, seed, result_json)
               VALUES (?,?,?,?,?,?)""",
            (oracle, resp.spread_type, req.question, req.user_id,
             resp.seed, json.dumps(raw, default=str)),
        )
        resp.reading_id = cur.lastrowid
        conn.commit()
        conn.close()
    except Exception as exc:
        log.warning("Failed to persist reading: %s", exc)

    return resp


@router.get("/horoscope/{sign}", response_model=HoroscopeResponse)
def daily_horoscope(sign: str, date: Optional[str] = Query(None)) -> HoroscopeResponse:
    from datetime import date as dt_date, datetime
    if date:
        try:
            for_date = dt_date.fromisoformat(date)
        except ValueError:
            for_date = dt_date.today()
    else:
        for_date = dt_date.today()
    if sign not in SIGN_INDEX:
        raise HTTPException(status_code=404, detail=f"Unknown sign: {sign!r}")
    horoscope = get_daily_horoscope(sign, for_date)
    return HoroscopeResponse(sign=sign, date=for_date.isoformat(), horoscope=horoscope)


@router.get("/sun-sign", response_model=dict)
def sun_sign(month: int = Query(..., ge=1, le=12), day: int = Query(..., ge=1, le=31)) -> dict:
    from datetime import date as dt_date
    try:
        d = dt_date(2000, month, day)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid month/day combination")
    sign = get_sun_sign(d)
    return {"month": month, "day": day, "sign": sign["name"]}


@router.get("/zodiac/{year}", response_model=ZodiacResponse)
def zodiac(year: int) -> ZodiacResponse:
    raw = build_chinese_zodiac_reading(birth_year=year)
    animal_data = get_animal(year)
    traits = animal_data.get("strengths", "").split(", ")
    return ZodiacResponse(
        year=year,
        animal=raw["animal"],
        element=raw["element"],
        yin_yang=raw["yin_yang"],
        trine=1,
        traits=traits,
        forecast=raw.get("summary", ""),
    )


@router.get("/search/tarot", response_model=SearchResponse)
def search_tarot(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)) -> SearchResponse:
    results: list[SearchResult] = []
    try:
        conn = get_connection()
        rows = conn.execute(
            """SELECT t.id, t.name, t.upright_meaning
               FROM tarot_cards_fts f
               JOIN tarot_cards t ON t.id = f.rowid
               WHERE tarot_cards_fts MATCH ?
               LIMIT ?""",
            (q, limit),
        ).fetchall()
        conn.close()
        for row in rows:
            snippet = row["upright_meaning"][:120] + ("…" if len(row["upright_meaning"]) > 120 else "")
            results.append(SearchResult(id=row["id"], name=row["name"], snippet=snippet))
    except Exception as exc:
        log.warning("Search failed: %s", exc)
    return SearchResponse(query=q, oracle_type="tarot", results=results)


@router.get("/search/rune", response_model=SearchResponse)
def search_rune(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)) -> SearchResponse:
    results: list[SearchResult] = []
    try:
        conn = get_connection()
        rows = conn.execute(
            """SELECT r.id, r.name, r.upright_meaning
               FROM runes_fts f
               JOIN runes r ON r.id = f.rowid
               WHERE runes_fts MATCH ?
               LIMIT ?""",
            (q, limit),
        ).fetchall()
        conn.close()
        for row in rows:
            snippet = row["upright_meaning"][:120] + ("…" if len(row["upright_meaning"]) > 120 else "")
            results.append(SearchResult(id=row["id"], name=row["name"], snippet=snippet))
    except Exception as exc:
        log.warning("Search failed: %s", exc)
    return SearchResponse(query=q, oracle_type="rune", results=results)


@router.get("/readings", response_model=list[dict])
def list_readings(
    user_id: str = Query("anonymous"),
    oracle_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict]:
    try:
        conn = get_connection()
        if oracle_type:
            rows = conn.execute(
                """SELECT id, oracle_type, spread_type, question, created_at
                   FROM readings
                   WHERE user_id=? AND oracle_type=?
                   ORDER BY id DESC LIMIT ?""",
                (user_id, oracle_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, oracle_type, spread_type, question, created_at
                   FROM readings
                   WHERE user_id=?
                   ORDER BY id DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as exc:
        log.warning("list_readings failed: %s", exc)
        return []


@router.get("/readings/{reading_id}", response_model=dict)
def get_reading(reading_id: int) -> dict:
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM readings WHERE id=?", (reading_id,)
        ).fetchone()
        conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Reading {reading_id} not found")
        d = dict(row)
        d["result"] = json.loads(d.pop("result_json", "{}"))
        return d
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
