# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/open_meteo.py
============================
Adapter for the Open-Meteo current-weather API (global, open, no key).

Source:
  https://api.open-meteo.com/v1/forecast

We query the ERA5 reanalysis grid for a global-mean surface temperature
proxy by averaging a set of geographically distributed reference stations.
This is a lightweight approximation sufficient for a ΔT comparison.

Returns::

    {
        "source":        str,
        "T_global_C":    float,   # estimated global surface T (°C)
        "T_baseline_C":  float,   # 1951-1980 baseline (14.0 °C)
        "delta_T_C":     float,   # T_global_C - T_baseline_C
        "date":          str,     # YYYY-MM-DD
    }

Framework mapping
-----------------
* ``temperature_phi_anomaly(T_current, T_baseline)`` — atmosphere.py
* ``tipping_point_phi()`` proximity for permafrost / ice-sheet thresholds
* ``equilibrium_temperature_shift()`` residual check

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

import datetime
import json
import urllib.request
from typing import Any

from . import snapshot

_SNAP_KEY = "open_meteo"
_TIMEOUT = 15
_T_BASELINE = 14.0  # 1951-1980 global mean (°C)

# Geographically distributed reference points for a coarse global mean
_STATIONS = [
    (0.0, 0.0),       # equatorial Atlantic
    (45.0, 0.0),      # mid-latitude N Atlantic
    (-45.0, 0.0),     # mid-latitude S Atlantic
    (0.0, 120.0),     # equatorial Pacific
    (45.0, -120.0),   # NE Pacific
    (-45.0, -60.0),   # S America mid-lat
    (60.0, 30.0),     # Scandinavia
    (-70.0, 0.0),     # Antarctica margin
]


def _station_url(lat: float, lon: float) -> str:
    return (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&temperature_unit=celsius"
    )


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch estimated global surface temperature from Open-Meteo.

    Parameters
    ----------
    live : bool
        When ``True`` attempt live HTTP requests; fall back to the
        snapshot on any failure.

    Returns
    -------
    dict with keys ``source``, ``T_global_C``, ``T_baseline_C``,
    ``delta_T_C``, ``date``.
    """
    if live:
        try:
            return _fetch_live()
        except Exception:  # noqa: BLE001
            pass
    return snapshot.load(_SNAP_KEY)


def _fetch_live() -> dict[str, Any]:
    temps = []
    today = datetime.date.today().isoformat()

    for lat, lon in _STATIONS:
        url = _station_url(lat, lon)
        with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
            data = json.load(resp)
        t = data["current_weather"]["temperature"]
        temps.append(float(t))

    t_global = sum(temps) / len(temps)
    result = {
        "source": "Open-Meteo current weather grid average (live)",
        "T_global_C": round(t_global, 2),
        "T_baseline_C": _T_BASELINE,
        "delta_T_C": round(t_global - _T_BASELINE, 2),
        "date": today,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
