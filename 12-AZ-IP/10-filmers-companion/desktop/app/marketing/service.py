"""Marketing / distribution service — campaigns, deliverable assets, press.

Covers trailer/poster/EPK tracking, social calendar scheduling, and press
contact management. Designed to interoperate with free/open-source
marketing tooling (Mautic for email/campaign automation, Matomo for
analytics) via the capability packets below, without hard-coding a
dependency on either.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from ..db.schema import get_conn

MAUTIC_CAPABILITY_PACKET = {
    "project": "mautic/mautic",
    "research_basis": ["README.md", "app/bundles/CampaignBundle"],
    "why": "Free, open-source marketing automation (email campaigns, "
    "landing pages, segmentation) — a FOSS alternative to HubSpot/Mailchimp "
    "for festival outreach, audience building, and distributor communication.",
    "integration": "marketing_campaigns rows map 1:1 onto Mautic campaigns; "
    "press_contacts export as a segment list for Mautic contact import.",
}

MATOMO_CAPABILITY_PACKET = {
    "project": "matomo-org/matomo",
    "research_basis": ["README.md", "core/Plugin"],
    "why": "Free, open-source, privacy-respecting web analytics — tracks "
    "trailer/landing-page performance without third-party data sharing, "
    "useful for self-hosted film microsites and EPKs.",
    "integration": "Attach a Matomo site ID per marketing_campaigns row to "
    "correlate on-site engagement with release windows.",
}

ASSET_TYPES = [
    "trailer", "teaser", "poster", "epk", "press-release", "social-clip",
    "one-sheet", "key-art", "behind-the-scenes",
]


class MarketingService:
    """Campaigns, marketing/distribution assets, and press contacts."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def create_campaign(self, project_id: str, name: str, channel: str = "",
                         status: str = "planned", start_date: str = "", end_date: str = "",
                         budget: float = 0.0, notes: str = "") -> dict:
        campaign_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            conn.execute(
                """INSERT INTO marketing_campaigns
                   (id, project_id, name, channel, status, start_date, end_date, budget, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (campaign_id, project_id, name, channel, status, start_date, end_date, budget, notes),
            )
        return {"id": campaign_id, "project_id": project_id, "name": name}

    def create_asset(self, project_id: str, asset_type: str, title: str,
                      campaign_id: str = "", status: str = "pending", due_date: str = "",
                      platform: str = "", notes: str = "") -> dict:
        asset_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            conn.execute(
                """INSERT INTO marketing_assets
                   (id, project_id, campaign_id, asset_type, title, status, due_date, platform, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (asset_id, project_id, campaign_id or None, asset_type, title, status, due_date, platform, notes),
            )
        return {"id": asset_id, "project_id": project_id, "asset_type": asset_type, "title": title}

    def create_press_contact(self, project_id: str, name: str, outlet: str = "",
                              email: str = "", beat: str = "", notes: str = "") -> dict:
        contact_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            conn.execute(
                """INSERT INTO press_contacts (id, project_id, name, outlet, email, beat, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (contact_id, project_id, name, outlet, email, beat, notes),
            )
        return {"id": contact_id, "project_id": project_id, "name": name}

    def marketing_dashboard(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            campaigns = _fetch_all(
                conn, "SELECT * FROM marketing_campaigns WHERE project_id=? ORDER BY start_date",
                (project_id,),
            )
            assets = _fetch_all(
                conn, "SELECT * FROM marketing_assets WHERE project_id=? ORDER BY due_date",
                (project_id,),
            )
            press_contacts = _fetch_all(
                conn, "SELECT * FROM press_contacts WHERE project_id=? ORDER BY name",
                (project_id,),
            )
        assets_by_status: dict[str, int] = {}
        for asset in assets:
            assets_by_status[asset["status"]] = assets_by_status.get(asset["status"], 0) + 1
        return {
            "project_id": project_id,
            "campaigns": campaigns,
            "active_campaigns": [c for c in campaigns if c["status"] == "active"],
            "assets": assets,
            "assets_by_status": assets_by_status,
            "outstanding_assets": [a for a in assets if a["status"] != "delivered"],
            "press_contacts": press_contacts,
            "total_campaign_budget": round(sum(float(c["budget"]) for c in campaigns), 2),
        }

    def social_calendar(self, project_id: str) -> list[dict]:
        """Return marketing assets ordered by due date as a release calendar."""
        with get_conn(self.db_path) as conn:
            return _fetch_all(
                conn,
                """SELECT * FROM marketing_assets
                   WHERE project_id=? AND due_date IS NOT NULL AND due_date != ''
                   ORDER BY due_date""",
                (project_id,),
            )

    def _ensure_project(self, conn, project_id: str) -> None:
        conn.execute(
            """INSERT OR IGNORE INTO projects
               (id, title, format, stage, logline, status, shoot_days, target_day_hours, contingency_pct)
               VALUES (?, ?, 'feature', 'prep', '', 'active', 0, 10.0, 12.0)""",
            (project_id, project_id),
        )


def _fetch_all(conn, query: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(query, params).fetchall()]
