#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Launcher for the standalone UM Geophysical Monitor product."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from geo_monitor.app.server import serve_ui
from geo_monitor.engine.overlay import compute_overlay, format_result_json, summary_stats
from geo_monitor.engine.physics import DISASTER_KINDS, GeoEvent, UMGeoOverlay


SAMPLE_EVENTS = [
    GeoEvent("earthquake", 7.4, 35.7, 140.1, depth_km=30.0),
    GeoEvent("wildfire", 6.0, 34.0, -118.0, area_ha=5000),
    GeoEvent("hurricane", 4.0, 25.0, -90.0),
    GeoEvent("volcano", 3.0, -8.3, 115.2),
    GeoEvent("storm", 5.0, 20.0, -60.0),
]



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UM Geophysical Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Serve the bundled browser UI")
    serve_parser.add_argument("--port", type=int, default=8021, help="Port for the HTTP server")
    serve_parser.add_argument(
        "--no-open",
        action="store_true",
        help="Accepted for compatibility; the standalone server never auto-opens a browser.",
    )

    analyse_parser = subparsers.add_parser("analyse", help="Analyse a single geophysical event")
    analyse_parser.add_argument("--kind", required=True, choices=sorted(DISASTER_KINDS))
    analyse_parser.add_argument("--magnitude", required=True, type=float)
    analyse_parser.add_argument("--lat", required=True, type=float)
    analyse_parser.add_argument("--lon", required=True, type=float)
    analyse_parser.add_argument("--depth-km", type=float, default=None)
    analyse_parser.add_argument("--area-ha", type=float, default=None)
    analyse_parser.add_argument("--energy-j", type=float, default=None)

    subparsers.add_parser("demo", help="Run a five-event demo analysis")
    return parser



def cmd_serve(args: argparse.Namespace) -> int:
    _ = args.no_open
    serve_ui(port=args.port)
    return 0



def cmd_analyse(args: argparse.Namespace) -> int:
    event = GeoEvent(
        kind=args.kind,
        magnitude=args.magnitude,
        lat=args.lat,
        lon=args.lon,
        depth_km=args.depth_km,
        area_ha=args.area_ha,
        energy_J=args.energy_j,
    )
    result = UMGeoOverlay().analyse(event)
    print(json.dumps(format_result_json(result), indent=2, sort_keys=True))
    return 0



def cmd_demo() -> int:
    results = compute_overlay(SAMPLE_EVENTS)
    payload = {
        "results": results,
        "summary": summary_stats(results),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "serve":
        return cmd_serve(args)
    if args.command == "analyse":
        return cmd_analyse(args)
    if args.command == "demo":
        return cmd_demo()
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
