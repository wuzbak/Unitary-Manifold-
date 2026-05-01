# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/noaa_co2.py
==========================
Adapter for the NOAA GML Mauna Loa daily CO₂ concentration feed.

Source (open, no key):
  https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt

Returns::

    {
        "source":   str,
        "co2_ppm":  float,   # most recent daily reading
        "date":     str,     # YYYY-MM-DD
    }

Framework mapping
-----------------
* ``greenhouse_forcing_phi(co2_ppm)``  — atmosphere.py
* ``co2_forcing(delta_CO2_ppm)``       — meteorology.py
* ``atmospheric_co2_phi(co2_ppm)``     — carbon_cycle.py

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

import urllib.request
from typing import Any

from . import snapshot

_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt"
_SNAP_KEY = "noaa_co2"
_TIMEOUT = 15


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch the latest Mauna Loa daily CO₂ reading.

    Parameters
    ----------
    live : bool
        When ``True`` attempt a live HTTP request; fall back to the
        snapshot on any failure.

    Returns
    -------
    dict with keys ``source``, ``co2_ppm``, ``date``.
    """
    if live:
        try:
            return _fetch_live()
        except Exception:  # noqa: BLE001
            pass
    return snapshot.load(_SNAP_KEY)


def _fetch_live() -> dict[str, Any]:
    with urllib.request.urlopen(_URL, timeout=_TIMEOUT) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    co2_ppm = None
    date_str = None
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        # Format: year month day co2_ppm [...]
        if len(parts) >= 4:
            try:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                val = float(parts[3])
                if val > 0:
                    co2_ppm = val
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    break
            except ValueError:
                continue

    if co2_ppm is None:
        raise ValueError("Could not parse CO2 value from NOAA feed")

    result = {
        "source": "NOAA GML Mauna Loa daily CO2 (live)",
        "co2_ppm": co2_ppm,
        "date": date_str,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
