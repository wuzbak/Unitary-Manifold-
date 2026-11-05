# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Read and validate the USGS public past-day earthquake GeoJSON feed."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Callable, Mapping
from urllib import request

USGS_FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
STALE_AFTER_SECONDS = 2 * 60 * 60
REQUEST_TIMEOUT_SECONDS = 10
MAX_FEED_BYTES = 8 * 1024 * 1024


class LiveDataError(RuntimeError):
    """A public live feed could not be fetched or validated."""


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _event_summary(feature: Any) -> dict[str, Any]:
    if not isinstance(feature, dict) or not isinstance(feature.get("properties"), dict):
        raise ValueError("feed contains a malformed event")
    properties = feature["properties"]
    event_time = properties.get("time")
    if isinstance(event_time, bool) or not isinstance(event_time, (int, float)) or not math.isfinite(event_time):
        raise ValueError("event time must be milliseconds since Unix epoch")
    return {
        "id": feature.get("id"),
        "time": _iso_utc(datetime.fromtimestamp(event_time / 1000, timezone.utc)),
        "magnitude": properties.get("mag"),
        "place": properties.get("place"),
        "url": properties.get("url"),
    }


def _normalize(payload: Any, fetched_at: datetime) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
        raise ValueError("expected a GeoJSON FeatureCollection")
    metadata = payload.get("metadata")
    features = payload.get("features")
    if not isinstance(metadata, dict) or not isinstance(features, list):
        raise ValueError("feed is missing metadata or features")
    generated_ms = metadata.get("generated")
    if (
        isinstance(generated_ms, bool)
        or not isinstance(generated_ms, (int, float))
        or not math.isfinite(generated_ms)
    ):
        raise ValueError("feed metadata is missing its generated timestamp")

    generated_at = datetime.fromtimestamp(generated_ms / 1000, timezone.utc)
    age_seconds = (fetched_at - generated_at).total_seconds()
    if age_seconds < 0:
        raise ValueError("feed generated timestamp is in the future")
    events = [_event_summary(feature) for feature in features]
    latest = max(events, key=lambda event: event["time"], default=None)
    return {
        "source": "live",
        "source_url": USGS_FEED_URL,
        "feed_title": metadata.get("title"),
        "generated_at": _iso_utc(generated_at),
        "fetched_at": _iso_utc(fetched_at),
        "age_seconds": round(age_seconds, 3),
        "stale_after_seconds": STALE_AFTER_SECONDS,
        "stale": age_seconds > STALE_AFTER_SECONDS,
        "event_count": len(features),
        "latest_event": latest,
    }


def _decode_validated_feed(
    raw: bytes, fetched_at: datetime,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(raw, bytes) or len(raw) > MAX_FEED_BYTES:
        raise ValueError("feed exceeds the supported byte bound or is not bytes")
    if fetched_at.tzinfo is None:
        raise ValueError("fetch time must include a timezone")
    payload = json.loads(raw.decode("utf-8"))
    return payload, _normalize(payload, fetched_at.astimezone(timezone.utc))


def _fetch_validated_feed(
    opener: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    """Share one validated transport response between summary and temporal adapters."""
    open_url = opener or request.urlopen
    try:
        req = request.Request(USGS_FEED_URL, headers={"User-Agent": "AZ-Live-Data-Harness/1.2"})
        with open_url(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_FEED_BYTES + 1)
        fetched_at = now or datetime.now(timezone.utc)
        payload, summary = _decode_validated_feed(raw, fetched_at)
        return payload, summary, raw
    except Exception as exc:
        raise LiveDataError(f"USGS live feed unavailable or invalid: {exc}") from exc


def fetch_earthquake_summary(
    opener: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fetch the public USGS past-day feed; errors are explicit, never fallback data."""
    _, summary, _ = _fetch_validated_feed(opener=opener, now=now)
    return summary
