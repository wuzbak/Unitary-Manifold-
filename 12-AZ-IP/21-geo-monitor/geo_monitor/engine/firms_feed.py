# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""NASA FIRMS fire-feed helpers for UM Geo Monitor v4."""

from __future__ import annotations

import csv
import io
import os
from urllib import error, request

FIRMS_DATASET = 'VIIRS_SNPP_NRT'
FIRMS_API_TEMPLATE = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{dataset}/{bbox}/{days}'
FIRMS_DEMO_KEY = 'd3efa5f4db12f5f3f61f8ae4e2c0d7c9'
_HEADERS = {'User-Agent': 'UM-GeoMonitor/4.0 (open-science)'}


def fetch_firms_active_fires(bbox: tuple = (-180, -90, 180, 90), days: int = 1) -> list[dict]:
    """Fetch FIRMS active fires, returning an empty list on API failure."""
    map_key = os.environ.get('FIRMS_MAP_KEY', FIRMS_DEMO_KEY)
    bbox_str = ','.join(str(value) for value in bbox)
    url = FIRMS_API_TEMPLATE.format(map_key=map_key, dataset=FIRMS_DATASET, bbox=bbox_str, days=int(days))
    req = request.Request(url, headers=_HEADERS)
    try:
        with request.urlopen(req, timeout=20) as response:
            text = response.read().decode('utf-8')
    except error.HTTPError as exc:
        if exc.code in {403, 429}:
            return []
        return []
    except Exception:
        return []

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
        return events
    except Exception:
        return []
