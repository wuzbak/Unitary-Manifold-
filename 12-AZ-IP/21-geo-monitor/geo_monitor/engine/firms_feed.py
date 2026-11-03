# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""NASA FIRMS fire-feed helpers for UM Geo Monitor v4."""

from __future__ import annotations

import csv
import io
import os
from urllib import error, request
from dataclasses import dataclass

FIRMS_DATASET = 'VIIRS_SNPP_NRT'
FIRMS_API_TEMPLATE = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{dataset}/{bbox}/{days}'
FIRMS_DEMO_KEY = 'd3efa5f4db12f5f3f61f8ae4e2c0d7c9'
_HEADERS = {'User-Agent': 'UM-GeoMonitor/4.0 (open-science)'}


@dataclass(frozen=True)
class FIRMSFetchResult:
    events: list[dict]
    error: str | None = None


def fetch_firms_active_fires_with_status(
    bbox: tuple = (-180, -90, 180, 90), days: int = 1, *, map_key: str | None = None
) -> FIRMSFetchResult:
    """Fetch active fires while preserving source failures for operator visibility."""
    map_key = map_key or os.environ.get('FIRMS_MAP_KEY', FIRMS_DEMO_KEY)
    bbox_str = ','.join(str(value) for value in bbox)
    url = FIRMS_API_TEMPLATE.format(map_key=map_key, dataset=FIRMS_DATASET, bbox=bbox_str, days=int(days))
    req = request.Request(url, headers=_HEADERS)
    try:
        with request.urlopen(req, timeout=20) as response:
            text = response.read().decode('utf-8')
    except error.HTTPError as exc:
        return FIRMSFetchResult([], f"HTTP {exc.code}: {exc.reason}")
    except Exception as exc:
        return FIRMSFetchResult([], f"{type(exc).__name__}: {exc}".replace(map_key, "[redacted]"))

    try:
        rows = csv.DictReader(io.StringIO(text))
        events: list[dict] = []
        for row in rows:
            if not row:
                continue
            lat_raw = row.get('latitude', row.get('lat'))
            lon_raw = row.get('longitude', row.get('lon'))
            if lat_raw in (None, '') or lon_raw in (None, ''):
                continue
            try:
                events.append(
                    {
                        'lat': float(lat_raw),
                        'lon': float(lon_raw),
                        'frp': float(row.get('frp', 0.0) or 0.0),
                        'acq_date': str(row.get('acq_date', '')),
                        'confidence': row.get('confidence', ''),
                    }
                )
            except (TypeError, ValueError):
                continue
        if rows.fieldnames is None or not {"latitude", "longitude"}.issubset(rows.fieldnames):
            return FIRMSFetchResult([], "invalid CSV header: expected latitude and longitude")
        return FIRMSFetchResult(events)
    except (csv.Error, UnicodeError) as exc:
        return FIRMSFetchResult([], f"invalid CSV payload: {exc}")


def fetch_firms_active_fires(bbox: tuple = (-180, -90, 180, 90), days: int = 1) -> list[dict]:
    """Backward-compatible active-fire fetcher; returns parsed rows only."""
    return fetch_firms_active_fires_with_status(bbox=bbox, days=days).events
