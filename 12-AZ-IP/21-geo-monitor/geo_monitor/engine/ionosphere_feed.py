# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""NOAA ionosphere / Kp helpers for UM Geo Monitor v4."""

from __future__ import annotations

import json
from urllib import request

KP_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
_HEADERS = {'User-Agent': 'UM-GeoMonitor/4.0 (open-science)'}
_OFFLINE = {'kp': 0, 'storm_level': 'quiet', 'space_weather_alert': False}


def fetch_kp_index() -> dict:
    """Fetch the latest NOAA planetary Kp index row."""
    req = request.Request(KP_URL, headers=_HEADERS)
    try:
        with request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception:
        return {'kp': 0, 'observed_time': None, 'source': KP_URL}

    try:
        if isinstance(payload, list):
            rows = [row for row in payload if isinstance(row, list) and len(row) >= 2 and row[0] != 'time_tag']
            last = rows[-1]
            return {'kp': float(last[1]), 'observed_time': last[0], 'source': KP_URL}
        if isinstance(payload, dict):
            return {'kp': float(payload.get('kp', 0.0) or 0.0), 'observed_time': payload.get('observed_time'), 'source': KP_URL}
    except Exception:
        pass
    return {'kp': 0, 'observed_time': None, 'source': KP_URL}


def get_ionospheric_status() -> dict:
    """Return a coarse ionospheric-status summary with offline fallback."""
    payload = fetch_kp_index()
    try:
        kp = float(payload.get('kp', 0.0) or 0.0)
    except (TypeError, ValueError):
        return dict(_OFFLINE)
    if kp >= 7:
        storm_level = 'severe'
    elif kp >= 5:
        storm_level = 'storm'
    elif kp >= 4:
        storm_level = 'active'
    else:
        storm_level = 'quiet'
    return {
        'kp': kp,
        'storm_level': storm_level,
        'space_weather_alert': kp >= 5,
        'observed_time': payload.get('observed_time'),
    }
