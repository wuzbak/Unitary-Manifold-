"""Cinematography router."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/cinematography", tags=["cinematography"])


@router.get("/shots/{scene_id}")
def list_shots(scene_id: str):
    """List shot list entries for a scene."""
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM shot_lists WHERE scene_id=?", (scene_id,)
        ).fetchall()
    return {"shots": [dict(r) for r in rows]}


@router.post("/shots")
def create_shot(body: dict):
    """Create a shot list entry."""
    import uuid
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    shot_id = body.get("id") or str(uuid.uuid4())
    with get_conn(cfg.db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO shot_lists
               (id,scene_id,shot_number,coverage_type,lens,movement,frame_rate,notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                shot_id,
                body.get("scene_id", ""),
                body.get("shot_number", 1),
                body.get("coverage_type", ""),
                body.get("lens", ""),
                body.get("movement", ""),
                body.get("frame_rate", "24fps"),
                body.get("notes", ""),
            ),
        )
    return {"id": shot_id, "status": "created"}


@router.post("/suggest-coverage")
def suggest_coverage(body: dict):
    """Suggest coverage for a scene."""
    from ...agents.cinematography import CinematographyAdvisor
    advisor = CinematographyAdvisor()
    synopsis = body.get("synopsis", "")
    scene_type = body.get("scene_type", "drama")
    suggestions = advisor.suggest_coverage(synopsis, scene_type)
    return {"suggestions": suggestions}


@router.post("/calc-lighting")
def calc_lighting(body: dict):
    """Calculate lighting at subject distance."""
    from ...agents.cinematography import CinematographyAdvisor
    advisor = CinematographyAdvisor()
    result = advisor.calc_lighting(
        subject_distance_ft=float(body.get("subject_distance_ft", 10)),
        fixture_power_w=float(body.get("fixture_power_w", 1000)),
    )
    return result
