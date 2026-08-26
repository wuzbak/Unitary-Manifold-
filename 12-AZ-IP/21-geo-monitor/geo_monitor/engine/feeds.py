# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Live feed parsers for the standalone UM Geophysical Monitor."""

from __future__ import annotations

import json
from typing import Any
from urllib import parse, request

from .physics import GeoEvent, parse_eonet_event, parse_usgs_feature


class USGSFeedParser:
    """Fetch and parse USGS earthquake GeoJSON feeds."""

    USGS_FEED_URL_PAST_DAY = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    )
    USGS_FEED_URL_PAST_HOUR = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
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


def get_combined_events(
    usgs_url: str | None = None,
    eonet_url: str | None = None,
    mock_data: dict[str, Any] | None = None,
) -> list[GeoEvent]:
    """Return a combined list of USGS and EONET GeoEvents.

    When ``mock_data`` is provided, network fetches are skipped. Supported keys are
    ``usgs`` and ``eonet`` with raw payload dictionaries.
    """
    usgs_parser = USGSFeedParser()
    eonet_parser = EONETFeedParser()

    if mock_data is not None:
        usgs_payload = mock_data.get("usgs", {"features": []})
        eonet_payload = mock_data.get("eonet", {"events": []})
    else:
        usgs_payload = usgs_parser.fetch(usgs_url or usgs_parser.USGS_FEED_URL_PAST_DAY)
        if eonet_url:
            with request.urlopen(eonet_url, timeout=20) as response:
                eonet_payload = json.loads(response.read().decode("utf-8"))
        else:
            eonet_payload = eonet_parser.fetch()

    events: list[GeoEvent] = []
    events.extend(usgs_parser.parse_geojson(usgs_payload))
    events.extend(eonet_parser.parse_events(eonet_payload))
    return events
