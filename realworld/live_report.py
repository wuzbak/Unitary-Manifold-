#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
realworld/live_report.py
=========================
Unified command-line driver for the Unitary Manifold real-world comparison
and prediction-impact analysis.

Usage::

    python realworld/live_report.py            # full report (snapshot, offline-safe)
    python realworld/live_report.py --live     # live API fetch, fallback to snapshot
    python realworld/live_report.py --update   # live fetch + update snapshot cache
    python realworld/live_report.py --impact   # prediction-impact table only
    python realworld/live_report.py --compare  # framework-vs-observed table only

The report contains two sections:

Section A — Prediction Impact
  Shows how substituting April 2026 real-world values shifts the framework's
  outputs relative to the pre-industrial reference baseline.  Answers the
  question: *do the real numbers change the initial prediction?*

Section B — Framework vs Observed
  Shows the residual between what the framework predicts (given live inputs)
  and what is independently observed by NOAA / USGS / SWPC.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import pathlib
import sys

# Allow running from any directory
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
from src.realworld_comparison import comparison_summary, run_comparison  # noqa: E402
from realworld.prediction_impact import impact_report, impact_summary  # noqa: E402


def _print_header(mode_label: str) -> None:
    print("=" * 80)
    print("  Unitary Manifold — Real-World Report")
    print(f"  April 2026  |  Mode: {mode_label}")
    print("  Theory: ThomasCory Walker-Pearson  |  Code: GitHub Copilot (AI)")
    print("=" * 80)


def _print_feed_summary(live: bool) -> None:
    print("\n─── Observational Data Feeds ───────────────────────────────────────────")
    feeds = [
        ("USGS global seismic",   usgs_seismic),
        ("PNSN Cascadia seismic", pnsn_seismic),
        ("NOAA CO₂ (Mauna Loa)", noaa_co2),
        ("NOAA CH₄ (GML)",       noaa_ch4),
        ("Open-Meteo surface T",  open_meteo),
        ("NOAA SWPC geomagnetic", swpc_geomagnetic),
        ("NOAA ENSO (Niño 3.4)", noaa_enso),
    ]
    for label, mod in feeds:
        d = mod.fetch(live=live)
        src = d["source"]
        print(f"  {label:<28} {src}")

    co2_d = noaa_co2.fetch(live=live)
    ch4_d = noaa_ch4.fetch(live=live)
    met_d = open_meteo.fetch(live=live)
    enso_d = noaa_enso.fetch(live=live)
    swpc_d = swpc_geomagnetic.fetch(live=live)

    print()
    print(f"  CO₂:   {co2_d['co2_ppm']:.1f} ppm  ({co2_d['date']})")
    print(f"  CH₄:   {ch4_d['ch4_ppb']:.0f} ppb  (year {ch4_d['year']})")
    print(f"  ΔT:    +{met_d['delta_T_C']:.2f} °C above baseline")
    print(f"  ENSO:  Niño3.4={enso_d['nino34_anomaly_C']:+.2f} °C → {enso_d['phase']}")
    print(f"  Kp:    {swpc_d['kp_index']:.1f}   Dst≈{swpc_d['dst_nT']:.0f} nT")

    print("\n  USGS events (M≥4.5, most recent 5):")
    for ev in usgs_seismic.fetch(live=live)["events"][:5]:
        print(f"    M{ev['magnitude']:.1f}  {ev['place']}  depth={ev['depth_km']:.0f} km")

    print("\n  PNSN Cascadia events (most recent 5):")
    pnsn_events = pnsn_seismic.fetch(live=live)["events"][:5]
    if pnsn_events:
        for ev in pnsn_events:
            print(f"    M{ev['magnitude']:.1f}  {ev['place']}  depth={ev['depth_km']:.0f} km")
    else:
        print("    (none in current feed window)")


def _print_impact(live: bool) -> None:
    print("\n─── Section A: Prediction Impact ───────────────────────────────────────")
    print("  Question: do real-world April 2026 values change the initial prediction?")
    print()
    entries = impact_report(live=live)
    print(impact_summary(entries))


def _print_comparison(live: bool) -> None:
    print("\n─── Section B: Framework vs Observed ───────────────────────────────────")
    print("  Residual between framework prediction (given live inputs)")
    print("  and independently observed values from NOAA / USGS / SWPC.")
    print()
    report = run_comparison(live=live)
    print(comparison_summary(report))
    n_ok = sum(1 for v in report.values() if v["status"] == "ok")
    n_warn = sum(1 for v in report.values() if v["status"] == "warning")
    print(f"\n  Summary: {n_ok} OK, {n_warn} warning(s) out of {len(report)} metrics")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Unitary Manifold real-world comparison report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true",
                      help="Attempt live API fetch; fall back to snapshot.")
    mode.add_argument("--update", action="store_true",
                      help="Live fetch AND update the local snapshot cache.")

    section = parser.add_mutually_exclusive_group()
    section.add_argument("--impact", action="store_true",
                         help="Print prediction-impact table only (Section A).")
    section.add_argument("--compare", action="store_true",
                         help="Print framework-vs-observed table only (Section B).")

    args = parser.parse_args(argv)
    live = args.live or args.update

    mode_label = "snapshot" if not live else ("live+update" if args.update else "live")
    _print_header(mode_label)

    if not (args.impact or args.compare):
        _print_feed_summary(live=live)

    if not args.compare:
        _print_impact(live=live)

    if not args.impact:
        _print_comparison(live=live)

    if args.update:
        print("\n  (Snapshot cache updated with live values)")


if __name__ == "__main__":
    main()
