"""Marketing / distribution router — campaigns, assets, press contacts."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/marketing", tags=["marketing"])


def _service():
    from ..config import get_config
    from .service import MarketingService

    return MarketingService(get_config().db_path)


@router.get("/{project_id}/dashboard")
def dashboard(project_id: str):
    return _service().marketing_dashboard(project_id)


@router.get("/{project_id}/calendar")
def social_calendar(project_id: str):
    return _service().social_calendar(project_id)


@router.post("/campaigns")
def create_campaign(body: dict):
    return _service().create_campaign(
        project_id=body.get("project_id", ""),
        name=body.get("name", ""),
        channel=body.get("channel", ""),
        status=body.get("status", "planned"),
        start_date=body.get("start_date", ""),
        end_date=body.get("end_date", ""),
        budget=float(body.get("budget", 0.0)),
        notes=body.get("notes", ""),
    )


@router.post("/assets")
def create_asset(body: dict):
    return _service().create_asset(
        project_id=body.get("project_id", ""),
        asset_type=body.get("asset_type", "trailer"),
        title=body.get("title", ""),
        campaign_id=body.get("campaign_id", ""),
        status=body.get("status", "pending"),
        due_date=body.get("due_date", ""),
        platform=body.get("platform", ""),
        notes=body.get("notes", ""),
    )


@router.post("/press-contacts")
def create_press_contact(body: dict):
    return _service().create_press_contact(
        project_id=body.get("project_id", ""),
        name=body.get("name", ""),
        outlet=body.get("outlet", ""),
        email=body.get("email", ""),
        beat=body.get("beat", ""),
        notes=body.get("notes", ""),
    )
