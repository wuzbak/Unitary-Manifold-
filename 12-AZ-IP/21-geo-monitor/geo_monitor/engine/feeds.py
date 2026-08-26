# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Live feed parsers for the standalone UM Geophysical Monitor.

Data sources (all public, no API key required):
  - USGS Earthquake Hazards Feed (GeoJSON)
  - NASA EONET v3 (wildfires, storms, volcanoes, floods)
  - NOAA NWS Alerts API (weather.gov) — severe weather, fire weather, tsunamis
  - NWAC Avalanche Center API — avalanche danger ratings (WA + OR)
"""

from __future__ import annotations

import json
from typing import Any
from urllib import parse, request

from .physics import GeoEvent, parse_eonet_event, parse_usgs_feature


# ---------------------------------------------------------------------------
# USGS Earthquake feed
# ---------------------------------------------------------------------------

class USGSFeedParser:
    """Fetch and parse USGS earthquake GeoJSON feeds."""

    USGS_FEED_URL_PAST_DAY = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    )
    USGS_FEED_URL_PAST_HOUR = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    )
    USGS_FEED_URL_PAST_MONTH_SIG = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
    )

    def parse_geojson(self, data: dict[str, Any]) -> list[GeoEvent]:
        """Parse a USGS GeoJSON FeatureCollection into GeoEvents."""
        events: list[GeoEvent] = []
        for feature in data.get("features", []):
            event = parse_usgs_feature(feature)
            if event is not None:
                events.append(event)
        return events

    def fetch(self, url: str) -> dict[str, Any]:
        """Fetch a JSON payload from a USGS endpoint."""
        with request.urlopen(url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# NASA EONET feed
# ---------------------------------------------------------------------------

class EONETFeedParser:
    """Fetch and parse NASA EONET JSON feeds."""

    EONET_API_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"

    def parse_events(self, data: dict[str, Any]) -> list[GeoEvent]:
        """Parse an EONET payload into GeoEvents."""
        events: list[GeoEvent] = []
        for item in data.get("events", []):
            event = parse_eonet_event(item)
            if event is not None:
                events.append(event)
        return events

    def fetch(self, limit: int = 50, days: int = 7) -> dict[str, Any]:
        """Fetch an EONET payload with simple query parameters."""
        query = parse.urlencode({"status": "open", "limit": limit, "days": days})
        url = f"{self.EONET_API_URL}?{query}"
        with request.urlopen(url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# NOAA NWS Alerts feed
# ---------------------------------------------------------------------------

# Severity → numeric magnitude proxy for UM overlay
_NWS_SEVERITY_MAG: dict[str, float] = {
    "Extreme":  4.0,
    "Severe":   3.0,
    "Moderate": 2.0,
    "Minor":    1.0,
    "Unknown":  1.5,
}

# NWS event type → disaster kind
_NWS_EVENT_KIND: dict[str, str] = {
    "Tsunami Warning": "tsunami",
    "Tsunami Advisory": "tsunami",
    "Tsunami Watch": "tsunami",
    "Tsunami Statement": "tsunami",
    "Red Flag Warning": "wildfire",
    "Fire Weather Watch": "wildfire",
    "Tornado Warning": "tornado",
    "Tornado Watch": "tornado",
    "Severe Thunderstorm Warning": "storm",
    "Severe Thunderstorm Watch": "storm",
    "Flash Flood Warning": "flood",
    "Flood Warning": "flood",
    "Coastal Flood Warning": "flood",
    "Winter Storm Warning": "storm",
    "Blizzard Warning": "storm",
    "High Wind Warning": "storm",
    "Extreme Cold Warning": "storm",
    "Excessive Heat Warning": "storm",
}
_NWS_DEFAULT_KIND = "nws_alert"


def _parse_nws_alert(feature: dict[str, Any]) -> GeoEvent | None:
    """Parse one NWS GeoJSON feature into a GeoEvent."""
    try:
        props = feature.get("properties") or {}
        event_type = str(props.get("event") or "")
        severity = str(props.get("severity") or "Unknown")
        headline = str(props.get("headline") or props.get("areaDesc") or event_type)
        area_desc = str(props.get("areaDesc") or "")

        # Determine kind
        kind = _NWS_DEFAULT_KIND
        for k, v in _NWS_EVENT_KIND.items():
            if k.lower() in event_type.lower():
                kind = v
                break

        mag = _NWS_SEVERITY_MAG.get(severity, 1.5)

        # Prefer a point centroid from geometry; fall back to affectedZones bbox
        geom = feature.get("geometry") or {}
        lat: float | None = None
        lon: float | None = None
        gtype = geom.get("type", "")
        coords = geom.get("coordinates")

        if gtype == "Point" and coords:
            lon, lat = float(coords[0]), float(coords[1])
        elif gtype == "Polygon" and coords and coords[0]:
            # Centroid of first ring
            ring = coords[0]
            lon = sum(c[0] for c in ring) / len(ring)
            lat = sum(c[1] for c in ring) / len(ring)
        elif gtype == "MultiPolygon" and coords and coords[0] and coords[0][0]:
            ring = coords[0][0]
            lon = sum(c[0] for c in ring) / len(ring)
            lat = sum(c[1] for c in ring) / len(ring)

        if lat is None or lon is None:
            return None
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return None

        return GeoEvent(kind=kind, magnitude=mag, lat=lat, lon=lon)
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return None


class NOAAAlertsFeedParser:
    """Fetch and parse NOAA NWS Alerts (api.weather.gov)."""

    NWS_ALERTS_BASE_URL = "https://api.weather.gov/alerts/active"

    def parse_features(self, data: dict[str, Any]) -> list[GeoEvent]:
        """Parse a NWS GeoJSON FeatureCollection into GeoEvents."""
        events: list[GeoEvent] = []
        for feature in data.get("features", []):
            ev = _parse_nws_alert(feature)
            if ev is not None:
                events.append(ev)
        return events

    def fetch(self, area: str | None = None) -> dict[str, Any]:
        """Fetch active NWS alerts, optionally filtered by state code(s).

        ``area`` may be a comma-separated list of US state abbreviations,
        e.g. ``"WA,OR,ID,MT,CA"``.
        """
        params: dict[str, str] = {}
        if area:
            params["area"] = area
        url = self.NWS_ALERTS_BASE_URL
        if params:
            url = f"{url}?{parse.urlencode(params)}"
        req = request.Request(url, headers={"User-Agent": "UM-GeoMonitor/1.0 (open-science)"})
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# NWAC Avalanche Center feed
# ---------------------------------------------------------------------------

# NWAC zone locations (approximate centroids for map placement)
_NWAC_ZONE_COORDS: dict[str, tuple[float, float]] = {
    "olympics":            (47.80, -123.70),
    "west-slopes-south":   (47.22, -121.56),
    "west-slopes-central": (47.70, -121.40),
    "west-slopes-north":   (48.50, -121.20),
    "east-slopes-south":   (46.85, -120.65),
    "east-slopes-central": (47.60, -120.70),
    "east-slopes-north":   (48.40, -120.50),
    "mt-hood":             (45.37, -121.70),
    "central-oregon":      (44.00, -121.60),
    "washington-cascades": (47.50, -121.50),
}

_NWAC_DANGER_MAG: dict[int, float] = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0}


def _parse_nwac_product(product: dict[str, Any]) -> list[GeoEvent]:
    """Parse one NWAC forecast product into GeoEvents (one per zone)."""
    events: list[GeoEvent] = []
    try:
        forecast_zone = str(product.get("forecast_zone") or "").lower()
        danger_list = product.get("danger") or []

        # Use highest danger level across elevation bands
        max_danger = 1
        for band in danger_list:
            lvl = int(band.get("level", 1) or 1)
            if lvl > max_danger:
                max_danger = lvl

        mag = _NWAC_DANGER_MAG.get(max_danger, 1.0)

        # Look up zone coordinates
        lat_lon: tuple[float, float] | None = None
        for key, coords in _NWAC_ZONE_COORDS.items():
            if key in forecast_zone or forecast_zone in key:
                lat_lon = coords
                break

        if lat_lon is None:
            # Generic WA Cascades fallback
            lat_lon = (47.50, -121.50)

        lat, lon = lat_lon
        events.append(GeoEvent(kind="avalanche", magnitude=mag, lat=lat, lon=lon))
    except (KeyError, TypeError, ValueError):
        pass
    return events


class NWACFeedParser:
    """Fetch and parse Northwest Avalanche Center (NWAC) forecast data."""

    NWAC_API_URL = "https://api.avalanche.org/v2/public/products"

    def parse_products(self, data: list[dict[str, Any]] | dict[str, Any]) -> list[GeoEvent]:
        """Parse NWAC product list into GeoEvents."""
        if isinstance(data, dict):
            items: list[dict[str, Any]] = data.get("data", [])
        else:
            items = data
        events: list[GeoEvent] = []
        seen: set[str] = set()
        for product in items:
            zone = str(product.get("forecast_zone") or product.get("zone_name") or "").lower().replace(" ", "-")
            if zone and zone in seen:
                continue
            if zone:
                seen.add(zone)
            events.extend(_parse_nwac_product(product))
        return events

    def fetch(self, center_id: str = "NWAC") -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch NWAC forecast products for the given avalanche center."""
        query = parse.urlencode({"avalanche_center_id": center_id})
        url = f"{self.NWAC_API_URL}?{query}"
        req = request.Request(url, headers={"User-Agent": "UM-GeoMonitor/1.0 (open-science)"})
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Combined event loader
# ---------------------------------------------------------------------------

def get_combined_events(
    usgs_url: str | None = None,
    eonet_url: str | None = None,
    nws_area: str | None = None,
    include_nwac: bool = False,
    mock_data: dict[str, Any] | None = None,
) -> list[GeoEvent]:
    """Return a combined list of GeoEvents from all active feeds.

    Parameters
    ----------
    usgs_url:
        Override USGS feed URL (defaults to the past-day all-events feed).
    eonet_url:
        Override EONET feed URL.
    nws_area:
        Comma-separated NWS state codes, e.g. ``"WA,OR,ID,MT"``.
        Pass ``None`` to skip the NWS feed.
    include_nwac:
        When ``True``, include NWAC avalanche danger forecasts.
    mock_data:
        Inject raw payloads instead of hitting the network.  Supported keys:
        ``usgs``, ``eonet``, ``nws``, ``nwac``.
    """
    usgs_parser   = USGSFeedParser()
    eonet_parser  = EONETFeedParser()
    nws_parser    = NOAAAlertsFeedParser()
    nwac_parser   = NWACFeedParser()

    if mock_data is not None:
        usgs_payload  = mock_data.get("usgs",  {"features": []})
        eonet_payload = mock_data.get("eonet", {"events":   []})
        nws_payload   = mock_data.get("nws",   {"features": []}) if "nws"  in mock_data else None
        nwac_payload  = mock_data.get("nwac",  [])               if "nwac" in mock_data else None
    else:
        usgs_payload  = usgs_parser.fetch(usgs_url or usgs_parser.USGS_FEED_URL_PAST_DAY)
        if eonet_url:
            with request.urlopen(eonet_url, timeout=20) as response:
                eonet_payload = json.loads(response.read().decode("utf-8"))
        else:
            eonet_payload = eonet_parser.fetch()
        nws_payload  = nws_parser.fetch(area=nws_area)  if nws_area    else None
        nwac_payload = nwac_parser.fetch()               if include_nwac else None

    events: list[GeoEvent] = []
    events.extend(usgs_parser.parse_geojson(usgs_payload))
    events.extend(eonet_parser.parse_events(eonet_payload))
    if nws_payload is not None:
        events.extend(nws_parser.parse_features(nws_payload))
    if nwac_payload is not None:
        events.extend(nwac_parser.parse_products(nwac_payload))
    return events
