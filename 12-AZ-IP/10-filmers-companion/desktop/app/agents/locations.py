"""
FilmersCompanion — Location Manager Agent
"""
from __future__ import annotations

from .base import BaseAgent


class LocationManager(BaseAgent):
    """Handles location scouting, permits, and scene-location grouping."""

    def generate_scout_report(self, location: dict) -> str:
        """Generate a scout report for a location."""
        name = location.get("name", "Unknown Location")
        address = location.get("address", "No address provided")
        int_ext = location.get("int_ext", "?")
        permit_status = location.get("permit_status", "unknown")
        fee = location.get("fee", 0.0)
        notes = location.get("notes", "")
        owner = location.get("owner_contact", "Not provided")

        status_flag = {
            "confirmed": "✅ CONFIRMED",
            "pending": "⏳ PENDING",
            "rejected": "❌ REJECTED",
            "expired": "⚠️ EXPIRED",
        }.get(permit_status.lower(), f"❓ {permit_status.upper()}")

        report = (
            f"LOCATION SCOUT REPORT\n"
            f"{'='*50}\n"
            f"Name:           {name}\n"
            f"Address:        {address}\n"
            f"Type:           {int_ext}\n"
            f"Permit Status:  {status_flag}\n"
            f"Location Fee:   ${fee:,.2f}\n"
            f"Owner/Contact:  {owner}\n"
            f"Notes:          {notes or 'None'}\n"
            f"{'='*50}\n"
        )

        if permit_status.lower() == "rejected":
            report += "⚠️  ACTION REQUIRED: Permit rejected — identify alternative location.\n"
        elif permit_status.lower() == "pending":
            report += "📋  Follow up with permitting authority. Build 2-week buffer.\n"
        elif permit_status.lower() == "confirmed":
            report += "✅  Location secured. Confirm tech scout with HODs.\n"

        return report

    def check_unconfirmed(self, scenes: list[dict], locations: list[dict]) -> list[dict]:
        """
        Return scenes whose location does not have permit_status == 'confirmed'.
        """
        loc_map = {loc["id"]: loc for loc in locations}
        flagged = []
        for scene in scenes:
            lid = scene.get("location_id")
            if lid is None:
                flagged.append({**scene, "_issue": "No location assigned"})
                continue
            loc = loc_map.get(lid)
            if loc is None:
                flagged.append({**scene, "_issue": f"Location {lid} not found"})
                continue
            if loc.get("permit_status", "").lower() != "confirmed":
                flagged.append({
                    **scene,
                    "_issue": f"Location '{loc.get('name')}' status: {loc.get('permit_status')}",
                })
        return flagged

    def group_by_location(self, scenes: list[dict]) -> dict[str, list[str]]:
        """Group scene IDs by location_id."""
        groups: dict[str, list[str]] = {}
        for scene in scenes:
            lid = scene.get("location_id") or "unassigned"
            groups.setdefault(lid, [])
            groups[lid].append(scene.get("id", scene.get("scene_number", "?")))
        return groups
