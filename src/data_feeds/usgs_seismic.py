# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/usgs_seismic.py
==============================
Adapter for the USGS global earthquake GeoJSON feed.

Source (open, no key):
  https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson

Returns a list of events, each a dict::

    {
        "place":     str,
        "magnitude": float,
        "time_utc":  str,   # ISO-8601
        "lat":       float,
        "lon":       float,
        "depth_km":  float,
    }

Framework mapping
-----------------
* ``rayleigh_number()`` (geology.py) — event depth and magnitude inform the
  local thermal gradient and hence the Ra estimate for the surrounding plate.
* ``phi_rock_regime()`` — magnitude maps to a local φ-stress regime.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import datetime
import json
import urllib.request
from typing import Any

from . import snapshot

_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"
    "4.5_week.geojson"
)
_SNAP_KEY = "usgs_seismic"
_TIMEOUT = 10


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch the USGS M≥4.5 weekly earthquake feed.

    Parameters
    ----------
    live : bool
        When ``True`` attempt a live HTTP request; fall back to the
        snapshot on any failure.  When ``False`` (default) return the
        snapshot immediately — safe for CI / offline use.

    Returns
    -------
    dict with keys:
        ``source`` — human-readable provenance string
        ``events`` — list of event dicts (see module docstring)
    """
    if live:
        try:
            return _fetch_live()
        except Exception:  # noqa: BLE001
            pass
    return snapshot.load(_SNAP_KEY)


def _fetch_live() -> dict[str, Any]:
    with urllib.request.urlopen(_URL, timeout=_TIMEOUT) as resp:
        raw = json.load(resp)

    events = []
    for feat in raw.get("features", []):
        props = feat["properties"]
        coords = feat["geometry"]["coordinates"]
        events.append(
            {
                "place": props.get("place", ""),
                "magnitude": float(props.get("mag") or 0.0),
                "time_utc": datetime.datetime.utcfromtimestamp(
                    props["time"] / 1000.0
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "lat": float(coords[1]),
                "lon": float(coords[0]),
                "depth_km": float(coords[2]),
            }
        )

    result = {
        "source": "USGS GeoJSON M≥4.5 weekly feed (live)",
        "events": events,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
