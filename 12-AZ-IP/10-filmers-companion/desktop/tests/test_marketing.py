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


def test_create_campaign_rejects_blank_name(svc):
    with pytest.raises(ValueError):
        svc.create_campaign("proj-1", "   ")


def test_create_campaign_rejects_unknown_status(svc):
    with pytest.raises(ValueError):
        svc.create_campaign("proj-1", "Launch", status="rogue")


def test_create_campaign_rejects_negative_budget(svc):
    with pytest.raises(ValueError):
        svc.create_campaign("proj-1", "Launch", budget=-100.0)


def test_create_asset_rejects_unknown_asset_type(svc):
    with pytest.raises(ValueError):
        svc.create_asset("proj-1", asset_type="billboard", title="Mystery Asset")


def test_create_asset_rejects_unknown_status(svc):
    with pytest.raises(ValueError):
        svc.create_asset("proj-1", asset_type="poster", title="Poster", status="lost")


def test_create_asset_rejects_unknown_campaign(svc):
    with pytest.raises(ValueError):
        svc.create_asset("proj-1", asset_type="poster", title="Poster", campaign_id="does-not-exist")


def test_create_press_contact_rejects_blank_name(svc):
    with pytest.raises(ValueError):
        svc.create_press_contact("proj-1", "")


def test_list_campaigns_and_assets(svc):
    svc.create_campaign("proj-1", "Festival Launch")
    svc.create_asset("proj-1", "trailer", "Teaser Trailer v1")
    assert len(svc.list_campaigns("proj-1")) == 1
    assert len(svc.list_assets("proj-1")) == 1


def test_marketing_dashboard_flags_overdue_assets(svc):
    svc.create_asset("proj-1", "trailer", "Overdue Trailer", due_date="2020-01-01")
    svc.create_asset("proj-1", "poster", "Future Poster", due_date="2999-01-01")

    dashboard = svc.marketing_dashboard("proj-1", as_of="2026-01-01")
    assert [a["title"] for a in dashboard["overdue_assets"]] == ["Overdue Trailer"]
