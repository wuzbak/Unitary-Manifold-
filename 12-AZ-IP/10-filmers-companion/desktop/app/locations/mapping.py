"""Location + trailer/basecamp mapping — geo-coordinates, distance planning,
and KML export for scouting, company moves, and unit base-camp logistics.

Pure standard-library implementation (haversine great-circle distance — no
external geocoding/mapping dependency). KML (Keyhole Markup Language) is an
open, OGC-standardized format readable by Google Earth/Maps, free GIS tools
(QGIS), and most location-scouting apps, so exports here are usable without
any paid mapping service.
"""
from __future__ import annotations

import math
from pathlib import Path

from ..db.schema import get_conn

_EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return _EARTH_RADIUS_KM * c


class LocationMappingService:
    """Geo-mapping, company-move distance planning, and KML export."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def set_coordinates(self, location_id: str, latitude: float, longitude: float,
                         basecamp_notes: str = "") -> dict:
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"latitude out of range: {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"longitude out of range: {longitude}")
        with get_conn(self.db_path) as conn:
            row = conn.execute("SELECT id FROM locations WHERE id=?", (location_id,)).fetchone()
            if row is None:
                raise ValueError(f"Unknown location: {location_id}")
            conn.execute(
                "UPDATE locations SET latitude=?, longitude=?, basecamp_notes=? WHERE id=?",
                (latitude, longitude, basecamp_notes, location_id),
            )
        return {"id": location_id, "latitude": latitude, "longitude": longitude}

    def location_map_summary(self, project_id: str) -> dict:
        """Return all project locations with coordinates, flagging unmapped ones."""
        with get_conn(self.db_path) as conn:
            rows = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM locations WHERE project_id=? ORDER BY name", (project_id,)
                ).fetchall()
            ]
        mapped = [r for r in rows if r.get("latitude") is not None and r.get("longitude") is not None]
        mapped_ids = {r["id"] for r in mapped}
        unmapped = [r for r in rows if r["id"] not in mapped_ids]
        return {
            "project_id": project_id,
            "total_locations": len(rows),
            "mapped": mapped,
            "unmapped": unmapped,
            "coverage_pct": round(100.0 * len(mapped) / len(rows), 1) if rows else 0.0,
        }

    def company_move_plan(self, project_id: str) -> dict:
        """Compute inter-location distances across consecutive scheduled shoot
        days — the "trailer/basecamp mapping" view used by the 1st AD and
        transport department to plan company moves between unit bases.
        """
        with get_conn(self.db_path) as conn:
            days = [
                dict(r)
                for r in conn.execute(
                    """SELECT sd.shoot_date, sd.location_id, l.name AS location_name,
                              l.latitude, l.longitude
                       FROM schedule_days sd
                       LEFT JOIN locations l ON l.id = sd.location_id
                       WHERE sd.project_id=?
                       ORDER BY sd.shoot_date""",
                    (project_id,),
                ).fetchall()
            ]
        moves = []
        total_km = 0.0
        for previous, current in zip(days, days[1:]):
            if (
                previous.get("latitude") is None or previous.get("longitude") is None
                or current.get("latitude") is None or current.get("longitude") is None
            ):
                moves.append({
                    "from_date": previous["shoot_date"],
                    "to_date": current["shoot_date"],
                    "from_location": previous.get("location_name"),
                    "to_location": current.get("location_name"),
                    "distance_km": None,
                    "company_move": previous.get("location_id") != current.get("location_id"),
                    "note": "Coordinates missing — distance not computed.",
                })
                continue
            distance = haversine_km(
                previous["latitude"], previous["longitude"],
                current["latitude"], current["longitude"],
            )
            total_km += distance
            moves.append({
                "from_date": previous["shoot_date"],
                "to_date": current["shoot_date"],
                "from_location": previous.get("location_name"),
                "to_location": current.get("location_name"),
                "distance_km": round(distance, 2),
                "company_move": previous.get("location_id") != current.get("location_id"),
            })
        return {
            "project_id": project_id,
            "shoot_days": len(days),
            "moves": moves,
            "total_company_move_km": round(total_km, 2),
            "company_move_count": sum(1 for m in moves if m["company_move"]),
        }

    def export_kml(self, project_id: str) -> str:
        """Export mapped locations as a KML placemark document."""
        with get_conn(self.db_path) as conn:
            project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
            rows = [
                dict(r)
                for r in conn.execute(
                    """SELECT * FROM locations
                       WHERE project_id=? AND latitude IS NOT NULL AND longitude IS NOT NULL
                       ORDER BY name""",
                    (project_id,),
                ).fetchall()
            ]
        title = (project["title"] if project else project_id) or project_id
        placemarks = []
        for loc in rows:
            description = _xml_escape(
                f"{loc.get('address') or ''} | Permit: {loc.get('permit_status') or 'pending'} | "
                f"Fee: ${float(loc.get('fee') or 0.0):,.2f}"
            )
            placemarks.append(
                "    <Placemark>\n"
                f"      <name>{_xml_escape(loc['name'])}</name>\n"
                f"      <description>{description}</description>\n"
                "      <Point>\n"
                f"        <coordinates>{loc['longitude']},{loc['latitude']},0</coordinates>\n"
                "      </Point>\n"
                "    </Placemark>"
            )
        kml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
            "  <Document>\n"
            f"    <name>{_xml_escape(title)} — Locations</name>\n"
            + "\n".join(placemarks)
            + "\n  </Document>\n</kml>\n"
        )
        return kml


def _xml_escape(value: str) -> str:
    return (
        (value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
