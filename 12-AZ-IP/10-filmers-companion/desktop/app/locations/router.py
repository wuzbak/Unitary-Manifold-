"""Locations router."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/{project_id}")
def list_locations(project_id: str):
    """List all locations for a project."""
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM locations WHERE project_id=?", (project_id,)
        ).fetchall()
    return {"locations": [dict(r) for r in rows]}


@router.post("/")
def create_location(body: dict):
    """Create a new location."""
    import uuid
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    loc_id = body.get("id") or str(uuid.uuid4())
    with get_conn(cfg.db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO locations
               (id,project_id,name,address,int_ext,permit_status,fee,owner_contact,notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                loc_id,
                body.get("project_id", ""),
                body.get("name", ""),
                body.get("address", ""),
                body.get("int_ext", "EXT"),
                body.get("permit_status", "pending"),
                float(body.get("fee", 0)),
                body.get("owner_contact", ""),
                body.get("notes", ""),
            ),
        )
    return {"id": loc_id, "status": "created"}


@router.get("/{location_id}/scout-report")
def scout_report(location_id: str):
    """Generate a scout report for a location."""
    from ...config import get_config
    from ...db.schema import get_conn
    from ...agents.locations import LocationManager
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        row = conn.execute(
            "SELECT * FROM locations WHERE id=?", (location_id,)
        ).fetchone()
    if not row:
        return {"error": "Location not found"}
    mgr = LocationManager()
    report = mgr.generate_scout_report(dict(row))
    return {"report": report}


@router.get("/{project_id}/unconfirmed")
def unconfirmed_locations(project_id: str):
    """List scenes with unconfirmed locations."""
    from ...config import get_config
    from ...db.schema import get_conn
    from ...agents.locations import LocationManager
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        scenes = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM scenes WHERE project_id=?", (project_id,)
            ).fetchall()
        ]
        locations = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM locations WHERE project_id=?", (project_id,)
            ).fetchall()
        ]
    mgr = LocationManager()
    flagged = mgr.check_unconfirmed(scenes, locations)
    return {"flagged_scenes": flagged, "count": len(flagged)}
