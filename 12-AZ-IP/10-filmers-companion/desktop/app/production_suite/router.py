"""Unified production-suite router."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/production-suite", tags=["production_suite"])


def _service():
    from ..config import get_config
    from .service import FilmProductionSuiteService

    cfg = get_config()
    return FilmProductionSuiteService(cfg.db_path)


@router.get("/{project_id}/dashboard")
def dashboard(project_id: str):
    """Return the producer / UPM master dashboard."""
    return _service().producer_dashboard(project_id)


@router.get("/{project_id}/script/overview")
def script_overview(project_id: str):
    """Return screenplay and revision overview."""
    return _service().script_overview(project_id)


@router.post("/script/import-text")
def import_script_text(body: dict):
    """Import a plain-text screenplay and build production artifacts."""
    try:
        return _service().import_script_text(
            project_id=body.get("project_id", "imported-project"),
            title=body.get("title", "Untitled Script"),
            content=body.get("content", ""),
            script_format=body.get("format", "feature"),
            revision_name=body.get("revision_name", "White Draft"),
            revision_color=body.get("revision_color", "White"),
            replace_existing=bool(body.get("replace_existing", False)),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/script/import-fountain")
def import_script_fountain(body: dict):
    """Import a Fountain screenplay and build production artifacts."""
    try:
        return _service().import_script_fountain(
            project_id=body.get("project_id", "imported-project"),
            title=body.get("title", "Untitled Script"),
            content=body.get("content", ""),
            revision_name=body.get("revision_name", "Blue Draft"),
            revision_color=body.get("revision_color", "Blue"),
            replace_existing=bool(body.get("replace_existing", False)),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/script/import-fdx")
def import_script_fdx(body: dict):
    """Import a Final Draft XML screenplay and build production artifacts."""
    try:
        return _service().import_script_fdx(
            project_id=body.get("project_id", "imported-project"),
            title=body.get("title", "Untitled Script"),
            content=body.get("content", ""),
            revision_name=body.get("revision_name", "Pink Draft"),
            revision_color=body.get("revision_color", "Pink"),
            replace_existing=bool(body.get("replace_existing", False)),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/script/export-fountain")
def export_script_fountain(project_id: str):
    """Export screenplay in Fountain format."""
    return _service().export_script_fountain(project_id)


@router.get("/{project_id}/script/export-fdx")
def export_script_fdx(project_id: str):
    """Export screenplay in Final Draft XML format."""
    return _service().export_script_fdx(project_id)


@router.post("/script/revision")
def create_script_revision(body: dict):
    """Create a script revision record and update current script content."""
    try:
        return _service().create_script_revision(
            project_id=body.get("project_id", ""),
            revision_name=body.get("revision_name", "Revision"),
            revision_color=body.get("revision_color", "White"),
            change_summary=body.get("change_summary", "Revision update"),
            content=body.get("content"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/script/diagnostics")
def script_diagnostics(project_id: str):
    """Return screenplay diagnostics for quality and continuity checks."""
    return _service().script_diagnostics(project_id)


@router.get("/{project_id}/script/reports")
def screenplay_reports(project_id: str):
    """Return script, scene, location, and character reports."""
    return _service().screenplay_reports(project_id)


@router.get("/{project_id}/script/master-plan")
def script_master_plan(project_id: str, objective: str = "Complete screenwriting upgrade"):
    """Return Merlin-guided screenwriting upgrade master-plan packet."""
    return _service().merlin_screenwriting_master_plan(project_id, objective=objective)


@router.get("/{project_id}/breakdown")
def breakdown(project_id: str):
    """Return breakdown summary across all departments."""
    return _service().breakdown_summary(project_id)


@router.get("/{project_id}/schedule/overview")
def schedule_overview(project_id: str):
    """Return stripboard and schedule health overview."""
    return _service().schedule_overview(project_id)


@router.get("/{project_id}/schedule/dood")
def dood(project_id: str):
    """Return day-out-of-days style chart."""
    return _service().dood_report(project_id)


@router.get("/{project_id}/departments")
def departments(project_id: str):
    """Return all department boards."""
    return _service().all_department_boards(project_id)


@router.get("/{project_id}/departments/{department}")
def department(project_id: str, department: str):
    """Return a single department board."""
    return _service().department_board(project_id, department)


@router.get("/{project_id}/post/overview")
def post_overview(project_id: str):
    """Return dailies, review, and deliverables summary."""
    return _service().post_overview(project_id)


@router.get("/{project_id}/approvals")
def approvals(project_id: str):
    """Return pending and historical approvals."""
    return _service().list_approvals(project_id)


@router.post("/tasks")
def create_task(body: dict):
    """Create or update a cross-department task."""
    return _service().create_task(body)


@router.post("/approvals")
def create_approval(body: dict):
    """Create or update a producer approval request."""
    return _service().create_approval(body)
