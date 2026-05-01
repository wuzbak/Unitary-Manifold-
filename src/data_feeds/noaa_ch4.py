# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/noaa_ch4.py
==========================
Adapter for the NOAA GML global CH₄ annual mean surface concentration.

Source (open, no key):
  https://gml.noaa.gov/webdata/ccgg/trends/ch4/ch4_annmean_gl.txt

Returns::

    {
        "source":   str,
        "ch4_ppb":  float,   # most recent annual mean
        "year":     int,
    }

Framework mapping
-----------------
* ``methane_phi_forcing(ch4_ppb)`` — carbon_cycle.py

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

_URL = "https://gml.noaa.gov/webdata/ccgg/trends/ch4/ch4_annmean_gl.txt"
_SNAP_KEY = "noaa_ch4"
_TIMEOUT = 15


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch the latest NOAA global CH₄ annual mean.

    Parameters
    ----------
    live : bool
        When ``True`` attempt a live HTTP request; fall back to the
        snapshot on any failure.

    Returns
    -------
    dict with keys ``source``, ``ch4_ppb``, ``year``.
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

    ch4_ppb = None
    year = None
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        # Format: year ch4_mean [uncertainty]
        if len(parts) >= 2:
            try:
                yr = int(parts[0])
                val = float(parts[1])
                if val > 0:
                    ch4_ppb = val
                    year = yr
                    break
            except ValueError:
                continue

    if ch4_ppb is None:
        raise ValueError("Could not parse CH4 value from NOAA feed")

    result = {
        "source": "NOAA GML global CH4 annual mean (live)",
        "ch4_ppb": ch4_ppb,
        "year": year,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
