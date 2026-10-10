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


def _mapping_service():
    from ...config import get_config
    from .mapping import LocationMappingService

    return LocationMappingService(get_config().db_path)


@router.post("/{location_id}/coordinates")
def set_coordinates(location_id: str, body: dict):
    """Set latitude/longitude (and optional basecamp notes) for a location."""
    from fastapi import HTTPException
    try:
        return _mapping_service().set_coordinates(
            location_id,
            latitude=float(body.get("latitude")),
            longitude=float(body.get("longitude")),
            basecamp_notes=body.get("basecamp_notes", ""),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/map")
def location_map(project_id: str):
    """Return mapped/unmapped locations with geo-coordinates for scouting."""
    return _mapping_service().location_map_summary(project_id)


@router.get("/{project_id}/company-moves")
def company_moves(project_id: str):
    """Return inter-location distances across scheduled shoot days (trailer/basecamp move planning)."""
    return _mapping_service().company_move_plan(project_id)


@router.get("/{project_id}/export.kml")
def export_kml(project_id: str):
    """Export mapped locations as a KML document (Google Earth/Maps, QGIS compatible)."""
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(_mapping_service().export_kml(project_id), media_type="application/vnd.google-earth.kml+xml")
