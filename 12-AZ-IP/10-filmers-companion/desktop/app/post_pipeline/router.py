"""Post-pipeline router — DaVinci Resolve / OTIO / EDL interchange."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/post-pipeline", tags=["post_pipeline"])


def _bridge():
    from ..config import get_config
    from .service import PostPipelineBridge

    return PostPipelineBridge(get_config().db_path)


@router.get("/resolve/status")
def resolve_status():
    """Report whether a live DaVinci Resolve scripting connection is available."""
    return _bridge().connect_resolve()


@router.get("/{project_id}/exports")
def list_exports(project_id: str):
    return _bridge().list_exports(project_id)


@router.get("/{project_id}/export/edl")
def export_edl(project_id: str):
    return PlainTextResponse(_bridge().export_edl(project_id), media_type="text/plain")


@router.get("/{project_id}/export/shotlist.csv")
def export_shotlist_csv(project_id: str):
    return PlainTextResponse(_bridge().export_shotlist_csv(project_id), media_type="text/csv")


@router.get("/{project_id}/export/otio")
def export_otio(project_id: str):
    return _bridge().export_otio_json(project_id)
