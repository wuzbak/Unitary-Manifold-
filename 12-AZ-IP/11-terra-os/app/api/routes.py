"""TerraOS API Routes."""
from fastapi import APIRouter, HTTPException
from terra.app.api.models import (
    AskRequest, AskResponse,
    SoilAnalysisRequest, WaterAnalysisRequest, AnalysisResponse,
    ProfileResponse, AmendmentResponse,
    SearchRequest, SearchResponse, SearchResult,
    SyncRequest, SyncResponse,
    RemediationRequest, RemediationResponse,
    HealthResponse,
)

router = APIRouter()


def _cfg():
    from terra.app.config import get_config
    return get_config()


@router.get("/", response_model=None)
def health():
    from terra.app.db.schema import get_conn
    cfg = _cfg()
    try:
        with get_conn(cfg.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM soil_profiles").fetchone()[0]
    except Exception:
        count = 0
    return HealthResponse(status="ok", app="terra-os", version="0.1.0", db_profile_count=count)


@router.post("/ask", response_model=None)
def ask(req: AskRequest):
    from terra.app.bot.agents import TerraGovernor
    cfg = _cfg()
    governor = TerraGovernor(db_path=cfg.db_path)
    result = governor.respond(req.question)
    return AskResponse(
        agent=result.agent_name,
        answer=result.answer,
        context_chunks=result.context_chunks,
        confidence=result.confidence,
    )


@router.post("/analyze/soil", response_model=None)
def analyze_soil(req: SoilAnalysisRequest):
    from terra.app.models.analyzer import SoilAnalyzer
    analyzer = SoilAnalyzer()
    result = analyzer.analyze(req.model_dump())
    return AnalysisResponse(**result)


@router.post("/analyze/water", response_model=None)
def analyze_water(req: WaterAnalysisRequest):
    from terra.app.models.analyzer import WaterAnalyzer
    analyzer = WaterAnalyzer()
    result = analyzer.analyze(req.model_dump())
    return AnalysisResponse(**result)


@router.get("/profile/{profile_id}", response_model=None)
def get_profile(profile_id: int):
    from terra.app.db.schema import get_conn, get_profile_full
    cfg = _cfg()
    with get_conn(cfg.db_path) as conn:
        data = get_profile_full(conn, profile_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        id=data["id"],
        name=data["name"],
        type=data["type"],
        description=data.get("description"),
        ph_min=data.get("ph_min"),
        ph_max=data.get("ph_max"),
        texture=data.get("texture"),
        organic_matter_pct=data.get("organic_matter_pct"),
        cec=data.get("cec"),
        native_region=data.get("native_region"),
        drainage=data.get("drainage"),
    )


@router.get("/amendments", response_model=None)
def list_amendments():
    from terra.app.db.schema import get_conn
    cfg = _cfg()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, type, description, application_rate, ph_effect FROM amendments LIMIT 100"
        ).fetchall()
    return [AmendmentResponse(**dict(r)) for r in rows]


@router.post("/remediation", response_model=None)
def remediation(req: RemediationRequest):
    from terra.app.db.schema import get_conn
    cfg = _cfg()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT name, method, description, duration_months, effectiveness_pct, cost_estimate FROM remediation_plans LIMIT 10"
        ).fetchall()
    methods = [dict(r) for r in rows]
    urgency = "high" if (req.concentration_ppm or 0) > 100 else "moderate"
    return RemediationResponse(
        contaminant=req.contaminant_name,
        recommended_methods=methods[:3],
        urgency=urgency,
        notes=f"Analysis for {req.medium} medium with {req.contaminant_name}.",
    )


@router.post("/search", response_model=None)
def search(req: SearchRequest):
    from terra.app.db.schema import get_conn, search_profiles
    cfg = _cfg()
    with get_conn(cfg.db_path) as conn:
        rows = search_profiles(conn, req.query, limit=req.limit)
    results = [
        SearchResult(
            id=r["id"],
            name=r["name"],
            profile_type=r.get("profile_type", "soil"),
            description=r.get("description"),
        )
        for r in rows
    ]
    return SearchResponse(results=results, total=len(results))


@router.post("/sync", response_model=None)
def sync(req: SyncRequest):
    from terra.app.sync.delta_sync import DeltaSync
    cfg = _cfg()
    ds = DeltaSync(db_path=cfg.db_path)
    count = ds.sync_table(req.table, since_ts=req.since_ts, batch_size=req.batch_size)
    return SyncResponse(table=req.table, records_synced=count, status="ok")


@router.get("/sync/status", response_model=None)
def sync_status():
    from terra.app.sync.delta_sync import DeltaSync
    cfg = _cfg()
    ds = DeltaSync(db_path=cfg.db_path)
    return ds.status()
