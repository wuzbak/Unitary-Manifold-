# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
12-AZ-IP/21-geo-monitor/geo_monitor/engine/wm_feeds.py
=======================================================
UM Geophysical Monitor v3 — Extended Feed Parsers

New data domains added in v3:
  - NOAA SWPC real-time Kp index (space weather / geomagnetic storms)
  - NOAA SWPC 3-day Kp forecast
  - GDACS (Global Disaster Alert and Coordination System — UN OCHA)
    GeoRSS for floods, cyclones, earthquakes not in USGS
  - CISA KEV (Known Exploited Vulnerabilities — cyber incidents)
  - WorldMonitor public REST API (optional; requires WM_API_KEY env var)
    Country Instability Index v8, infrastructure alerts

All sources that require no API key are always active.
WorldMonitor-sourced data is gated behind the WM_API_KEY environment
variable; when absent the parsers return empty lists gracefully.

Licence note:
  We consume WorldMonitor's public REST API and optional SDK; no
  WorldMonitor source code is copied into this repository.  WorldMonitor
  is AGPL v3; this integration is data-attribution-only.  Our own code
  here is LicenseRef-Defensive-Public-Commons-1.0.

Attribution:
  NOAA SWPC — https://www.swpc.noaa.gov/ (public domain, US government)
  GDACS      — https://www.gdacs.org/ (CC BY 4.0, UN OCHA)
  CISA KEV   — https://www.cisa.gov/known-exploited-vulnerabilities-catalog
               (public domain, US government)
  WorldMonitor — https://worldmonitor.app (AGPL v3, koala73/worldmonitor)

🔵 ADJACENT TRACK — feeds augment the UM physics overlay; not hardgate.
"""

from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from typing import Any, Optional
from urllib import request

from .physics import GeoEvent, DISASTER_KINDS_MUTABLE

# ---------------------------------------------------------------------------
# Namespace helpers for GDACS GeoRSS / Atom
# ---------------------------------------------------------------------------
_GDACS_NS = {
    "georss": "http://www.georss.org/georss",
    "gdacs":  "http://www.gdacs.org",
    "atom":   "http://www.w3.org/2005/Atom",
    "cap":    "urn:oasis:names:tc:emergency:cap:1.2",
}

# ---------------------------------------------------------------------------
# Shared HTTP helper (same pattern as feeds.py)
# ---------------------------------------------------------------------------
_HEADERS = {
    "User-Agent": "UM-GeoMonitor/3.0 (open-science; axiomzero.com)",
    "Accept": "application/json, application/geo+json, text/xml, */*",
}


def _fetch_json(url: str, timeout: int = 25) -> Any:
    req = request.Request(url, headers=_HEADERS)
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_text(url: str, timeout: int = 25) -> str:
    req = request.Request(url, headers=_HEADERS)
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


# ===========================================================================
# NOAA SWPC — Space weather / Kp index
# ===========================================================================

SWPC_KP_1MIN_URL = (
    "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
)
SWPC_KP_3DAY_URL = (
    "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
)
SWPC_ALERTS_URL = (
    "https://services.swpc.noaa.gov/products/alerts.json"
)

# Geomagnetic storm thresholds (G-scale)
KP_G_SCALE = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9}   # G1–G5 → Kp threshold


def parse_kp_1min(data: list[dict]) -> Optional[GeoEvent]:
    """
    Parse the NOAA SWPC 1-minute Kp JSON.
    Returns a single GeoEvent of kind 'space_weather' if Kp ≥ 4 (moderate),
    or None if conditions are quiet.

    The event is placed at the geomagnetic north pole (90°N, 0°E) as a
    representative point; the UI renders an auroral oval overlay instead.
    """
    if not data:
        return None
    latest = data[-1]
    try:
        kp = float(latest.get("kp_index", 0))
    except (TypeError, ValueError):
        return None
    if kp < 4.0:
        return None   # quiet — no notable event
    return GeoEvent(
        kind="space_weather",
        magnitude=kp,
        lat=90.0,
        lon=0.0,
        energy_J=_kp_to_energy_j(kp),
    )


def _kp_to_energy_j(kp: float) -> float:
    """
    Approximate joule equivalent for a given Kp level.
    Based on the empirical relationship for ring-current injection energy:
      E ≈ 10^(0.8·Kp + 13)  J  (Dessler-Parker-Sckopke analogue)
    """
    return 10 ** (0.8 * kp + 13.0)


def parse_swpc_alerts(data: list[dict]) -> list[GeoEvent]:
    """
    Parse NOAA SWPC active alerts JSON.
    Converts geomagnetic-storm and radiation-storm alerts into GeoEvents.
    """
    events: list[GeoEvent] = []
    for alert in data:
        msg = alert.get("message", "")
        if not msg:
            continue
        # Detect G-class storm
        for g, kp_thresh in KP_G_SCALE.items():
            if f"G{g}" in msg or f"Kp {kp_thresh}" in msg:
                events.append(GeoEvent(
                    kind="space_weather",
                    magnitude=float(kp_thresh),
                    lat=90.0,
                    lon=0.0,
                    energy_J=_kp_to_energy_j(float(kp_thresh)),
                ))
                break
    return events


class SWPCFeedParser:
    """Fetch and parse NOAA SWPC space-weather feeds (no API key required)."""

    def fetch_kp_1min(self) -> list[dict]:
        return _fetch_json(SWPC_KP_1MIN_URL)

    def fetch_kp_3day(self) -> list[dict]:
        return _fetch_json(SWPC_KP_3DAY_URL)

    def fetch_alerts(self) -> list[dict]:
        return _fetch_json(SWPC_ALERTS_URL)

    def get_current_kp_event(self) -> Optional[GeoEvent]:
        """Return a GeoEvent for current Kp if storm-level (≥4)."""
        data = self.fetch_kp_1min()
        return parse_kp_1min(data)

    def get_current_kp_value(self) -> float:
        """Return latest Kp value (0–9), or 0.0 on error."""
        try:
            data = self.fetch_kp_1min()
            if not data:
                return 0.0
            return float(data[-1].get("kp_index", 0))
        except Exception:
            return 0.0

    def get_alert_events(self) -> list[GeoEvent]:
        """Return GeoEvents from current SWPC alerts."""
        data = self.fetch_alerts()
        return parse_swpc_alerts(data)


# ===========================================================================
# GDACS — Global Disaster Alert and Coordination System (UN OCHA)
# ===========================================================================

GDACS_RSS_URL = "https://www.gdacs.org/xml/rss.xml"

# GDACS alert-level → approximate magnitude proxy
_GDACS_LEVEL_MAG = {"Green": 3.0, "Orange": 6.0, "Red": 8.0}


def parse_gdacs_feed(xml_text: str) -> list[GeoEvent]:
    """
    Parse GDACS GeoRSS/Atom feed into GeoEvents.
    Handles: flood (FL), cyclone (TC), earthquake (EQ), volcano (VO),
             drought (DR), wildfire (WF).
    """
    events: list[GeoEvent] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return events

    # The feed is RSS 2.0 with georss and gdacs extensions
    channel = root.find("channel")
    if channel is None:
        return events

    for item in channel.findall("item"):
        try:
            event = _parse_gdacs_item(item)
            if event is not None:
                events.append(event)
        except Exception:
            continue
    return events


def _parse_gdacs_item(item: ET.Element) -> Optional[GeoEvent]:
    """Parse a single GDACS RSS <item> element."""
    # gdacs:eventtype
    etype_el = item.find("gdacs:eventtype", _GDACS_NS)
    etype = (etype_el.text or "").strip().upper() if etype_el is not None else ""

    kind_map = {
        "EQ": "earthquake",
        "TC": "hurricane",
        "FL": "flood",
        "VO": "volcano",
        "DR": "drought",
        "WF": "wildfire",
        "TS": "tsunami",
    }
    kind = kind_map.get(etype, "storm")

    # gdacs:alertlevel
    level_el = item.find("gdacs:alertlevel", _GDACS_NS)
    level = (level_el.text or "Green").strip().capitalize() if level_el is not None else "Green"
    mag = _GDACS_LEVEL_MAG.get(level, 3.0)

    # gdacs:magnitude (overrides proxy if present)
    mag_el = item.find("gdacs:magnitude", _GDACS_NS)
    if mag_el is not None and mag_el.text:
        try:
            mag = float(mag_el.text.strip())
        except ValueError:
            pass

    # georss:point
    point_el = item.find("georss:point", _GDACS_NS)
    if point_el is None or not point_el.text:
        return None
    parts = point_el.text.strip().split()
    if len(parts) < 2:
        return None
    lat, lon = float(parts[0]), float(parts[1])

    return GeoEvent(kind=kind, magnitude=mag, lat=lat, lon=lon)


class GDACSFeedParser:
    """Fetch and parse GDACS global disaster feed (CC BY 4.0, no API key)."""

    def fetch(self) -> str:
        return _fetch_text(GDACS_RSS_URL)

    def get_events(self) -> list[GeoEvent]:
        xml_text = self.fetch()
        return parse_gdacs_feed(xml_text)


# ===========================================================================
# CISA KEV — Known Exploited Vulnerabilities (cyber incidents)
# ===========================================================================

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
)

# Cyber events are placed at (0, 0) by default — they have no physical location.
# The UI renders them in a separate non-geographic panel.
_CYBER_DEFAULT_LAT = 0.0
_CYBER_DEFAULT_LON = 0.0


def parse_cisa_kev(data: dict, limit: int = 20) -> list[GeoEvent]:
    """
    Parse CISA KEV JSON.  Returns one GeoEvent per recently-added CVE.
    Magnitude is derived from the CVSS severity proxy (1–10 → 0–10 scale).
    Only the most recent `limit` entries are returned.
    """
    events: list[GeoEvent] = []
    vulns = data.get("vulnerabilities", [])
    # Sort by dateAdded descending, take most recent `limit`
    try:
        vulns = sorted(vulns, key=lambda v: v.get("dateAdded", ""), reverse=True)
    except Exception:
        pass
    for vuln in vulns[:limit]:
        try:
            # Use a nominal magnitude of 7.0 (critical exploit) unless we can
            # infer a CVSS score from the description.
            mag = 7.0
            events.append(GeoEvent(
                kind="cyber",
                magnitude=mag,
                lat=_CYBER_DEFAULT_LAT,
                lon=_CYBER_DEFAULT_LON,
            ))
        except Exception:
            continue
    return events


class CISAKEVParser:
    """Fetch and parse CISA KEV feed (public domain, no API key)."""

    def fetch(self) -> dict:
        return _fetch_json(CISA_KEV_URL)

    def get_events(self, limit: int = 20) -> list[GeoEvent]:
        data = self.fetch()
        return parse_cisa_kev(data, limit=limit)


# ===========================================================================
# WorldMonitor public API (optional — requires WM_API_KEY env var)
# ===========================================================================

WM_BASE_URL = "https://api.worldmonitor.app"


def _wm_api_key() -> Optional[str]:
    """Return WM_API_KEY from environment, or None if not set."""
    return os.environ.get("WM_API_KEY") or None


def _wm_headers() -> dict:
    key = _wm_api_key()
    h = dict(_HEADERS)
    if key:
        h["X-WorldMonitor-Key"] = key
    return h


def _fetch_wm_json(path: str, timeout: int = 25) -> Any:
    """Fetch from WorldMonitor REST API with optional auth."""
    url = f"{WM_BASE_URL}{path}"
    req = request.Request(url, headers=_wm_headers())
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wm_api_available() -> bool:
    """Return True only if WM_API_KEY is present in environment."""
    return _wm_api_key() is not None


# ---------------------------------------------------------------------------
# Country Instability Index (CII v8)
# ---------------------------------------------------------------------------

def fetch_cii_scores() -> dict[str, float]:
    """
    Fetch CII v8 country-level stress scores from WorldMonitor.
    Returns {iso2: score} where score ∈ [0, 100].
    Returns empty dict if WM_API_KEY is absent.
    """
    if not wm_api_available():
        return {}
    try:
        data = _fetch_wm_json("/v1/cii")
        scores: dict[str, float] = {}
        for entry in data.get("countries", []):
            iso2 = entry.get("iso2", "")
            score = float(entry.get("score", 0.0))
            if iso2:
                scores[iso2] = score
        return scores
    except Exception:
        return {}


def cii_to_geo_event(iso2: str, score: float, lat: float, lon: float) -> GeoEvent:
    """Convert a CII score to a GeoEvent of kind 'infrastructure'."""
    # Normalise 0–100 CII score to magnitude 0–10
    mag = score / 10.0
    return GeoEvent(kind="infrastructure", magnitude=mag, lat=lat, lon=lon)


# ---------------------------------------------------------------------------
# Infrastructure alerts
# ---------------------------------------------------------------------------

def fetch_infrastructure_alerts() -> list[GeoEvent]:
    """
    Fetch infrastructure alerts from WorldMonitor API.
    Returns empty list if WM_API_KEY is absent.
    """
    if not wm_api_available():
        return []
    try:
        data = _fetch_wm_json("/v1/infrastructure/alerts")
        events: list[GeoEvent] = []
        for alert in data.get("alerts", []):
            lat = float(alert.get("lat", 0.0))
            lon = float(alert.get("lon", 0.0))
            mag = float(alert.get("severity", 5.0))
            events.append(GeoEvent(kind="infrastructure", magnitude=mag, lat=lat, lon=lon))
        return events
    except Exception:
        return []


# ===========================================================================
# Aggregate v3 feed loader
# ===========================================================================

class GeoMonitorV3Feeds:
    """
    Aggregate all v3 feed parsers.

    Usage
    -----
    feeds = GeoMonitorV3Feeds()
    space_events = feeds.space_weather_events()   # always available
    gdacs_events = feeds.gdacs_events()           # always available
    cyber_events = feeds.cyber_events()           # always available
    infra_events = feeds.infrastructure_events()  # WM_API_KEY required
    kp           = feeds.current_kp()             # always available
    """

    def __init__(self) -> None:
        self._swpc = SWPCFeedParser()
        self._gdacs = GDACSFeedParser()
        self._cisa = CISAKEVParser()

    def current_kp(self) -> float:
        """Return current planetary Kp index (0–9)."""
        return self._swpc.get_current_kp_value()

    def space_weather_events(self) -> list[GeoEvent]:
        """Return GeoEvents for active space-weather alerts."""
        events: list[GeoEvent] = []
        ev = self._swpc.get_current_kp_event()
        if ev is not None:
            events.append(ev)
        events.extend(self._swpc.get_alert_events())
        return events

    def gdacs_events(self) -> list[GeoEvent]:
        """Return GeoEvents from GDACS (global floods, cyclones, etc.)."""
        try:
            return self._gdacs.get_events()
        except Exception:
            return []

    def cyber_events(self, limit: int = 20) -> list[GeoEvent]:
        """Return GeoEvents from CISA KEV (cyber incidents)."""
        try:
            return self._cisa.get_events(limit=limit)
        except Exception:
            return []

    def infrastructure_events(self) -> list[GeoEvent]:
        """Return GeoEvents from WorldMonitor infrastructure alerts."""
        return fetch_infrastructure_alerts()

    def cii_scores(self) -> dict[str, float]:
        """Return CII v8 country risk scores (empty if no WM_API_KEY)."""
        return fetch_cii_scores()
