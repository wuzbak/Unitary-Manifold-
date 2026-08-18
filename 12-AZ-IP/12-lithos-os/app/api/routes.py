"""
LithosOS — FastAPI Routes
"""
from __future__ import annotations
import json
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException

from .models import (
    AskRequest, AskResponse,
    HealthResponse,
    IdentifyRequest, IdentifyResponse, SpecimenCandidateResponse,
    SearchRequest, SearchResponse,
    SpecimenResponse,
    SyncRequest, SyncStatusResponse,
)

router = APIRouter()

@router.get("/", response_model=HealthResponse)
def health():
    from ..config import get_config
    cfg = get_config()
    count = 0
    if cfg.db_path.exists():
        try:
            conn = sqlite3.connect(str(cfg.db_path))
            count = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
            conn.close()
        except Exception:
            pass
    return HealthResponse(
        status="ok",
        service="lithos-os",
        version="1.0.0",
        offline_mode=cfg.offline_mode,
        db_specimen_count=count,
    )

@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    from ..config import get_config
    from ..bot.agents import LithosGovernor
    cfg = get_config()
    gov = LithosGovernor(
        api_key=cfg.openai_api_key,
        model=cfg.openai_model,
        local_llm_url=cfg.local_llm_url,
        local_llm_model=cfg.local_llm_model,
    )
    if req.agent:
        try:
            answer = gov.ask_agent(req.agent, req.question, req.context or "")
            agents_used = [req.agent]
        except KeyError:
            result = gov.route(req.question, req.context or "")
            answer = result.answer
            agents_used = result.agents_used
    else:
        result = gov.route(req.question, req.context or "")
        answer = result.answer
        agents_used = result.agents_used
    return AskResponse(answer=answer, agents_used=agents_used, question=req.question)

@router.post("/identify", response_model=IdentifyResponse)
def identify(req: IdentifyRequest):
    from ..config import get_config
    from ..models.identifier import MindatIdentifier
    cfg = get_config()
    identifier = MindatIdentifier(
        mindat_api_key=cfg.mindat_api_key,
        inaturalist_token=cfg.inaturalist_api_token,
        local_model_path=cfg.local_model_path,
    )
    if req.description:
        result = identifier.identify_from_description(req.description)
    elif req.image_base64:
        import base64
        image_bytes = base64.b64decode(req.image_base64)
        result = identifier.identify_from_bytes(image_bytes)
    else:
        result = identifier.identify_from_bytes(b"")
    candidates = [
        SpecimenCandidateResponse(
            name=c.name,
            common_names=c.common_names,
            confidence=c.confidence,
            confidence_label=c.confidence_label,
            mineral_class=c.mineral_class,
            description=c.description,
            source=c.source,
        )
        for c in result.candidates
    ]
    return IdentifyResponse(
        candidates=candidates,
        summary=result.summary(),
        description_analysis=req.description,
    )

@router.get("/specimen/{specimen_id}", response_model=SpecimenResponse)
def get_specimen(specimen_id: int):
    from ..config import get_config
    from ..db.schema import get_conn, get_specimen_full
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        data = get_specimen_full(conn, specimen_id)
    if not data:
        raise HTTPException(status_code=404, detail="Specimen not found")
    common_names = data.get("common_names", "[]")
    if isinstance(common_names, str):
        try:
            common_names = json.loads(common_names)
        except Exception:
            common_names = [common_names]
    return SpecimenResponse(
        id=data["id"],
        name=data["name"],
        common_names=common_names,
        mineral_class=data.get("mineral_class") or "",
        crystal_system=data.get("crystal_system") or "",
        mohs_hardness=data.get("mohs_hardness") or 0.0,
        composition=data.get("composition") or "",
        description=data.get("description") or "",
        luster=data.get("luster") or "",
        streak=data.get("streak") or "",
        minerals=data.get("minerals", []),
        gemstones=data.get("gemstones", []),
        metals=data.get("metals", []),
        hazards=data.get("hazards", []),
        market_data=data.get("market_data", []),
    )

@router.get("/minerals")
def list_minerals():
    from ..config import get_config
    from ..db.schema import get_conn
    cfg = get_config()
    if not cfg.db_path.exists():
        return []
    try:
        with get_conn(cfg.db_path) as conn:
            rows = conn.execute("""
                SELECT m.*, s.name as specimen_name FROM minerals m
                LEFT JOIN specimens s ON s.id=m.specimen_id LIMIT 200
            """).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

@router.get("/market")
def list_market():
    from ..config import get_config
    from ..db.schema import get_conn
    cfg = get_config()
    if not cfg.db_path.exists():
        return []
    try:
        with get_conn(cfg.db_path) as conn:
            rows = conn.execute("""
                SELECT md.*, s.name as specimen_name FROM market_data md
                LEFT JOIN specimens s ON s.id=md.specimen_id LIMIT 200
            """).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    from ..config import get_config
    from ..db.schema import get_conn, search_specimens
    cfg = get_config()
    if not cfg.db_path.exists():
        return SearchResponse(results=[], total=0, query=req.query)
    with get_conn(cfg.db_path) as conn:
        results = search_specimens(conn, req.query, req.limit)
    return SearchResponse(results=results, total=len(results), query=req.query)

@router.post("/sync", response_model=SyncStatusResponse)
def sync(req: SyncRequest):
    from ..config import get_config
    from ..sync.delta_sync import DeltaSync
    cfg = get_config()
    ds = DeltaSync(db_path=cfg.db_path, sync_url=cfg.sync_url)
    try:
        state = ds.sync(since=req.since, tables=req.tables or None)
        return SyncStatusResponse(
            last_sync=state.last_sync,
            records_updated=state.records_updated,
            records_deleted=state.records_deleted,
            errors=state.errors,
            completed=state.completed,
        )
    except Exception as e:
        return SyncStatusResponse(
            last_sync="", records_updated=0, records_deleted=0,
            errors=[str(e)], completed=False,
        )


# ---------------------------------------------------------------------------
# Mineral guides / source references
# ---------------------------------------------------------------------------

@router.get("/references/{specimen_id}")
def get_references(specimen_id: int):
    """Return all public guide source references for a specimen."""
    from ..config import get_config
    from ..db.schema import get_conn, get_source_references
    cfg = get_config()
    if not cfg.db_path.exists():
        raise HTTPException(status_code=503, detail="Database not initialised")
    with get_conn(cfg.db_path) as conn:
        refs = get_source_references(conn, specimen_id)
    if not refs:
        raise HTTPException(status_code=404, detail=f"No references found for specimen {specimen_id}")
    return refs


@router.get("/guides/sources")
def list_guide_sources():
    """Return the registry of authoritative mineral guide sources."""
    from ..db.mineral_guides import get_guide_sources
    return list(get_guide_sources().values())


@router.get("/guides/fetch/{mineral_name}")
def fetch_mineral_guide(mineral_name: str, refresh: bool = False):
    """Fetch mineral information from Mindat/USGS (cached offline).

    Set ?refresh=true to force a live fetch from public sources.
    Returns cached data immediately if available and refresh=false.
    """
    from ..config import get_config
    from ..sync.mindat_fetcher import MindatFetcher
    cfg = get_config()
    fetcher = MindatFetcher(db_path=cfg.db_path)
    result = fetcher.fetch_mineral(mineral_name, force_refresh=refresh)
    return result.as_dict()


@router.get("/guides/cache/stats")
def guide_cache_stats():
    """Return statistics about the local mineral guide cache."""
    from ..config import get_config
    from ..sync.mindat_fetcher import MindatFetcher
    cfg = get_config()
    fetcher = MindatFetcher(db_path=cfg.db_path)
    return fetcher.cache_stats()


@router.get("/guides/cache")
def list_cached_guides():
    """List all minerals currently cached from public guide sources."""
    from ..config import get_config
    from ..sync.mindat_fetcher import MindatFetcher
    cfg = get_config()
    fetcher = MindatFetcher(db_path=cfg.db_path)
    return fetcher.get_all_cached()

@router.get("/sync/status", response_model=SyncStatusResponse)
def sync_status():
    from ..config import get_config
    from ..sync.delta_sync import DeltaSync
    cfg = get_config()
    ds = DeltaSync(db_path=cfg.db_path, sync_url=cfg.sync_url)
    state = ds.get_state()
    return SyncStatusResponse(
        last_sync=state.last_sync,
        records_updated=state.records_updated,
        records_deleted=state.records_deleted,
        errors=state.errors,
        completed=state.completed,
    )
