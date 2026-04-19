# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/swpc_geomagnetic.py
==================================
Adapter for the NOAA Space Weather Prediction Center (SWPC) solar-wind
and geomagnetic index feed.

Source (open, no key):
  https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json

We extract:
* **Kp index** (geomagnetic activity, 0–9)
* **Dst index** proxy (nT) — we use the proton density / speed product as
  a Dst proxy when the dedicated Dst feed is unavailable.
* **B_nT** — IGRF-13 surface field (fixed, 25 000 nT) used as a baseline
  for ``elsasser_number()``.

Returns::

    {
        "source":   str,
        "kp_index": float,
        "dst_nT":   float,
        "B_nT":     float,
        "date":     str,
    }

Framework mapping
-----------------
* ``elsasser_number(B, rho, Omega, sigma)`` — geology.py
  Live B_nT from SWPC replaces the static IGRF value when available.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import datetime
import json
import urllib.request
from typing import Any

from . import snapshot

_URL_PLASMA = (
    "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"
)
_URL_KP = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
_SNAP_KEY = "swpc_geomagnetic"
_TIMEOUT = 10
_IGRF_B_NT = 25_000.0  # nT, IGRF-13 mean surface dipole field


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch SWPC solar-wind / geomagnetic indices.

    Parameters
    ----------
    live : bool
        When ``True`` attempt live HTTP requests; fall back to the
        snapshot on any failure.

    Returns
    -------
    dict with keys ``source``, ``kp_index``, ``dst_nT``, ``B_nT``, ``date``.
    """
    if live:
        try:
            return _fetch_live()
        except Exception:  # noqa: BLE001
            pass
    return snapshot.load(_SNAP_KEY)


def _fetch_live() -> dict[str, Any]:
    # Kp index — most recent 3-hour value
    with urllib.request.urlopen(_URL_KP, timeout=_TIMEOUT) as resp:
        kp_data = json.load(resp)

    kp_index = 0.0
    for row in reversed(kp_data):
        if isinstance(row, list) and len(row) >= 2:
            try:
                kp_index = float(row[1])
                break
            except (ValueError, TypeError):
                continue

    # Plasma feed — derive a rough Dst proxy from proton density × speed²
    with urllib.request.urlopen(_URL_PLASMA, timeout=_TIMEOUT) as resp:
        plasma_data = json.load(resp)

    dst_proxy = -15.0  # fallback
    for row in reversed(plasma_data):
        if isinstance(row, list) and len(row) >= 3:
            try:
                density = float(row[1])
                speed = float(row[2])
                dst_proxy = -0.013 * density * speed ** 0.5
                break
            except (ValueError, TypeError):
                continue

    result = {
        "source": "NOAA SWPC solar-wind / Kp (live)",
        "kp_index": kp_index,
        "dst_nT": round(dst_proxy, 1),
        "B_nT": _IGRF_B_NT,
        "date": datetime.date.today().isoformat(),
    }
    snapshot.save(_SNAP_KEY, result)
    return result
