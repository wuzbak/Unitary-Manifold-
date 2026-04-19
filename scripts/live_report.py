#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
scripts/live_report.py
======================
Thin wrapper — delegates to ``realworld/live_report.py``.

For the full report (prediction impact + framework-vs-observed), prefer::

    python realworld/live_report.py [--live] [--update] [--impact] [--compare]

This script is retained for backwards compatibility with the original
command-line interface.

Command-line driver for the Unitary Manifold real-world comparison.

Usage::

    python scripts/live_report.py           # snapshot (offline-safe)
    python scripts/live_report.py --live    # live API fetch, fall back to snapshot
    python scripts/live_report.py --update  # live fetch + update snapshot cache

The script prints a comparison table of framework-predicted quantities
vs observed real-world values for:

  * CO₂ radiative forcing (NOAA Mauna Loa)
  * CO₂ φ parameter (atmospheric_co2_phi)
  * CH₄ forcing (NOAA GML)
  * Committed equilibrium ΔT
  * Surface temperature anomaly φ (Open-Meteo)
  * ENSO phase (NOAA CPC Niño 3.4)
  * Elsasser number Λ (SWPC + IGRF-13)

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import pathlib
import sys

# Allow running as ``python scripts/live_report.py`` from the repo root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.data_feeds import (  # noqa: E402
    noaa_co2,
    noaa_ch4,
    noaa_enso,
    open_meteo,
    pnsn_seismic,
    swpc_geomagnetic,
    usgs_seismic,
)
from src.data_feeds import snapshot as _snap  # noqa: E402
from src.realworld_comparison import comparison_summary, run_comparison  # noqa: E402


def _print_feed_summary(live: bool) -> None:
    print("\n--- Data Feed Summary ---")
    feeds = [
        ("USGS seismic",   usgs_seismic,    "usgs_seismic"),
        ("PNSN seismic",   pnsn_seismic,    "pnsn_seismic"),
        ("NOAA CO₂",       noaa_co2,        "noaa_co2"),
        ("NOAA CH₄",       noaa_ch4,        "noaa_ch4"),
        ("Open-Meteo T",   open_meteo,      "open_meteo"),
        ("SWPC geomag",    swpc_geomagnetic,"swpc_geomagnetic"),
        ("NOAA ENSO",      noaa_enso,       "noaa_enso"),
    ]
    for label, mod, _key in feeds:
        d = mod.fetch(live=live)
        print(f"  {label:<20} source: {d['source']}")

    print()
    print("  USGS events (M≥4.5 this week):")
    for ev in usgs_seismic.fetch(live=live)["events"][:5]:
        print(f"    M{ev['magnitude']:.1f}  {ev['place']}  depth={ev['depth_km']:.0f} km")

    print()
    print("  PNSN Cascadia events:")
    for ev in pnsn_seismic.fetch(live=live)["events"][:5]:
        print(f"    M{ev['magnitude']:.1f}  {ev['place']}  depth={ev['depth_km']:.0f} km")

    co2 = noaa_co2.fetch(live=live)
    ch4 = noaa_ch4.fetch(live=live)
    met = open_meteo.fetch(live=live)
    enso = noaa_enso.fetch(live=live)
    swpc = swpc_geomagnetic.fetch(live=live)

    print(f"\n  CO₂:  {co2['co2_ppm']:.1f} ppm  ({co2['date']})")
    print(f"  CH₄:  {ch4['ch4_ppb']:.0f} ppb  (year {ch4['year']})")
    print(f"  ΔT:   +{met['delta_T_C']:.2f} °C above baseline")
    print(f"  ENSO: Niño3.4={enso['nino34_anomaly_C']:+.2f} °C → {enso['phase']}")
    print(f"  Kp:   {swpc['kp_index']:.1f}   Dst proxy: {swpc['dst_nT']:.0f} nT")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Unitary Manifold real-world comparison report"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--live",
        action="store_true",
        help="Attempt live API fetch; fall back to snapshot on failure.",
    )
    mode.add_argument(
        "--update",
        action="store_true",
        help="Live fetch AND update the local snapshot cache.",
    )
    args = parser.parse_args(argv)

    live = args.live or args.update

    print("=" * 72)
    print("  Unitary Manifold — Real-World Comparison Report")
    print("  April 2026 | Theory: ThomasCory Walker-Pearson")
    print("=" * 72)

    _print_feed_summary(live=live)

    print("\n--- Framework vs Observed ---")
    report = run_comparison(live=live)
    print(comparison_summary(report))

    n_ok = sum(1 for v in report.values() if v["status"] == "ok")
    n_warn = sum(1 for v in report.values() if v["status"] == "warning")
    print(f"\n  Summary: {n_ok} OK, {n_warn} warning(s) out of {len(report)} metrics\n")

    if args.update:
        print("  (Snapshot updated with live values)")


if __name__ == "__main__":
    main()
