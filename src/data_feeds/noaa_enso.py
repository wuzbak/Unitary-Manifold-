# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/noaa_enso.py
===========================
Adapter for the NOAA CPC Niño 3.4 SST anomaly index.

Source (open, no key):
  https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices

This is a plain-text monthly file; the most recent row gives the latest
Niño 3.4 anomaly (°C).

Returns::

    {
        "source":             str,
        "nino34_anomaly_C":   float,   # SST anomaly in Niño 3.4 region (°C)
        "phase":              str,     # 'el_nino' | 'la_nina' | 'neutral'
        "date":               str,     # YYYY-MM (year-month of reading)
    }

Framework mapping
-----------------
* ``enso_phase(phi_pacific)`` — oceanography.py
  The Niño 3.4 anomaly is the direct observable that maps to φ_pacific:
  anomaly > +0.5 °C → el_niño, < −0.5 °C → la_niña, else neutral.

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

import urllib.request
from typing import Any

from . import snapshot

_URL = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
_SNAP_KEY = "noaa_enso"
_TIMEOUT = 15

_EL_NINO_THRESHOLD = 0.5   # °C
_LA_NINA_THRESHOLD = -0.5  # °C

# Niño 3.4 column index in the NOAA sstoi.indices file (0-based).
# Columns: YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM
# Niño 3.4 anomaly is column index 7 (0-based).
_NINO34_ANOM_COL = 7


def fetch(live: bool = False) -> dict[str, Any]:
    """Fetch the latest NOAA Niño 3.4 ENSO index.

    Parameters
    ----------
    live : bool
        When ``True`` attempt a live HTTP request; fall back to the
        snapshot on any failure.

    Returns
    -------
    dict with keys ``source``, ``nino34_anomaly_C``, ``phase``, ``date``.
    """
    if live:
        try:
            return _fetch_live()
        except Exception:  # noqa: BLE001
            pass
    return snapshot.load(_SNAP_KEY)


def _classify(anomaly: float) -> str:
    if anomaly > _EL_NINO_THRESHOLD:
        return "el_nino"
    if anomaly < _LA_NINA_THRESHOLD:
        return "la_nina"
    return "neutral"


def _fetch_live() -> dict[str, Any]:
    with urllib.request.urlopen(_URL, timeout=_TIMEOUT) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    anomaly = None
    year_mon = None
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        parts = line.split()
        if len(parts) > _NINO34_ANOM_COL:
            try:
                val = float(parts[_NINO34_ANOM_COL])
                year_mon = f"{parts[0]}-{int(parts[1]):02d}"
                anomaly = val
                break
            except (ValueError, IndexError):
                continue

    if anomaly is None:
        raise ValueError("Could not parse Niño 3.4 anomaly from NOAA feed")

    result = {
        "source": "NOAA CPC Nino 3.4 SST anomaly index (live)",
        "nino34_anomaly_C": anomaly,
        "phase": _classify(anomaly),
        "date": year_mon,
    }
    snapshot.save(_SNAP_KEY, result)
    return result
