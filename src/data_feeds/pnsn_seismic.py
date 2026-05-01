# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/pnsn_seismic.py
==============================
Adapter for the Pacific Northwest Seismic Network (PNSN) recent-earthquake
feed, filtered to Cascadia / Pacific Northwest events.

Source (open, no key):
  https://pnsn.org/api/v1/earthquakes/recent

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
* Cascadia subduction-zone moment deficit — event rate and magnitude
  distribution inform the seismic-moment accumulation model.
* ``rayleigh_number()`` for the Pacific NW mantle wedge.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import json
import urllib.request
from typing import Any

from . import snapshot

_URL = "https://pnsn.org/api/v1/earthquakes/recent"
_SNAP_KEY = "pnsn_seismic"
_TIMEOUT = 10

# Approximate bounding box for Cascadia / Pacific Northwest
_LAT_MIN, _LAT_MAX = 40.0, 52.0
_LON_MIN, _LON_MAX = -130.0, -116.0


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch recent PNSN Cascadia earthquakes.

    Parameters
    ----------
    live : bool
        When ``True`` attempt a live HTTP request; fall back to the
        snapshot on any failure.  When ``False`` (default) return the
        snapshot immediately.

    Returns
    -------
    dict with keys:
        ``source`` — provenance string
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
    items = raw if isinstance(raw, list) else raw.get("earthquakes", [])
    for item in items:
        lat = float(item.get("lat", 0.0))
        lon = float(item.get("lon", 0.0))
        if not (_LAT_MIN <= lat <= _LAT_MAX and _LON_MIN <= lon <= _LON_MAX):
            continue
        events.append(
            {
                "place": item.get("place", item.get("location", "")),
                "magnitude": float(item.get("mag", item.get("magnitude", 0.0))),
                "time_utc": item.get("time", item.get("origin_time", "")),
                "lat": lat,
                "lon": lon,
                "depth_km": float(item.get("depth", 0.0)),
            }
        )

    result = {
        "source": "PNSN Cascadia recent earthquakes (live)",
        "events": events,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
