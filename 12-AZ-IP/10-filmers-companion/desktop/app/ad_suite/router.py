"""AD Suite router."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/ad-suite", tags=["ad_suite"])


@router.get("/{project_id}/call-sheets")
def list_call_sheets(project_id: str):
    """List all call sheets for a project."""
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM call_sheets WHERE project_id=?", (project_id,)
        ).fetchall()
    return {"call_sheets": [dict(r) for r in rows]}


@router.post("/generate-call-sheet")
def generate_call_sheet(body: dict):
    """Generate a formatted call sheet."""
    from ...agents.ad_suite import ADChief
    ad = ADChief()
    scenes = body.get("scenes", [])
    location = body.get("location", {})
    shoot_date = body.get("shoot_date", "TBD")
    result = ad.generate_call_sheet(scenes, location, shoot_date)
    return {"call_sheet": result}


@router.post("/check-turnaround")
def check_turnaround(body: dict):
    """Check turnaround compliance between wrap and call times."""
    from ...agents.ad_suite import ADChief
    ad = ADChief()
    result = ad.check_turnaround(
        wrap_time=body.get("wrap_time", "22:00"),
        call_time=body.get("call_time", "07:00"),
    )
    return result


@router.post("/one-liner")
def one_liner(body: dict):
    """Generate a one-liner scene list."""
    from ...agents.ad_suite import ADChief
    ad = ADChief()
    scenes = body.get("scenes", [])
    result = ad.generate_one_liner(scenes)
    return {"one_liner": result}


@router.post("/dept-note")
def add_dept_note(body: dict):
    """Add a department note."""
    import uuid
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    note_id = body.get("id") or str(uuid.uuid4())
    with get_conn(cfg.db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO dept_notes
               (id, project_id, dept, note, created_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (
                note_id,
                body.get("project_id", ""),
                body.get("dept", ""),
                body.get("note", ""),
            ),
        )
    return {"id": note_id, "status": "created"}
