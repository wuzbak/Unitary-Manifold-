# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds
==============
Live ingestion adapters for real-world observational data.

Each adapter module exposes a single ``fetch()`` function that returns a
standardised Python dict.  When the network is unavailable (sandbox, CI,
offline dev) every adapter falls back transparently to the pinned
April 2026 snapshot stored in ``latest_snapshot.json`` via
``snapshot.load(key)``.

Available adapters
------------------
usgs_seismic    — USGS GeoJSON M≥4.5 earthquake feed
pnsn_seismic    — PNSN QuakeML Cascadia earthquake feed
noaa_co2        — NOAA GML Mauna Loa daily CO₂ (ppm)
noaa_ch4        — NOAA GML global CH₄ annual mean (ppb)
open_meteo      — Open-Meteo current surface temperature
swpc_geomagnetic— NOAA SWPC solar-wind / geomagnetic indices
noaa_enso       — NOAA CPC Niño 3.4 ENSO index

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from .snapshot import load as snapshot_load, save as snapshot_save  # noqa: F401
