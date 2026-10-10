"""Tests for the marketing / distribution module."""
from __future__ import annotations

import pytest

from desktop.app.marketing.service import MarketingService
from desktop.app.config import get_config


@pytest.fixture
def svc():
    from desktop.app.db.schema import init_db
    cfg = get_config()
    init_db(cfg.db_path)
    return MarketingService(cfg.db_path)


def test_create_campaign_and_asset(svc):
    campaign = svc.create_campaign(
        "proj-1", "Festival Launch", channel="social", status="active", budget=25000.0
    )
    asset = svc.create_asset(
        "proj-1", asset_type="trailer", title="Teaser Trailer v1",
        campaign_id=campaign["id"], due_date="2026-11-15",
    )
    assert asset["asset_type"] == "trailer"

    dashboard = svc.marketing_dashboard("proj-1")
    assert dashboard["total_campaign_budget"] == 25000.0
    assert len(dashboard["active_campaigns"]) == 1
    assert len(dashboard["outstanding_assets"]) == 1
    assert dashboard["assets_by_status"]["pending"] == 1


def test_press_contacts_and_calendar(svc):
    svc.create_press_contact("proj-1", "Jane Critic", outlet="IndieWire", beat="Festivals")
    svc.create_asset("proj-1", "poster", "Key Art Poster", due_date="2026-10-01")
    svc.create_asset("proj-1", "epk", "Electronic Press Kit", due_date="2026-10-15")

    dashboard = svc.marketing_dashboard("proj-1")
    assert len(dashboard["press_contacts"]) == 1

    calendar = svc.social_calendar("proj-1")
    assert [item["title"] for item in calendar] == ["Key Art Poster", "Electronic Press Kit"]
