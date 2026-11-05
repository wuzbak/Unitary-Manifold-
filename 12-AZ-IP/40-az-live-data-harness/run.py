#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Live-Data Harness (Product 40)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from az_live_data_harness import LiveDataError, fetch_earthquake_summary


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="AZ Live-Data Harness")
    parser.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8140)
    parser.add_argument("--temporal", action="store_true", help="capture availability-aware magnitudes")
    parser.add_argument("--owner-scope", help="explicit project scope required for temporal capture")
    parser.add_argument("--snapshot-dir", type=Path, help="existing durable directory for temporal snapshots")
    args = parser.parse_args(argv)
    if args.temporal and (not args.owner_scope or not args.owner_scope.strip()):
        parser.error("--temporal requires --owner-scope")
    if (args.owner_scope or args.snapshot_dir) and not args.temporal:
        parser.error("--owner-scope and --snapshot-dir require --temporal")
    if args.serve and args.temporal:
        parser.error("--serve and --temporal are separate modes")

    if args.serve:
        from az_live_data_harness.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    import json

    try:
        if args.temporal:
            from az_live_data_harness.temporal_adapter import fetch_earthquake_snapshot
            from src.infrastructure.temporal_data import save_snapshot
            from src.infrastructure.data_lineage import save_graph

            capture = fetch_earthquake_snapshot(owner_scope=args.owner_scope)
            result = capture.to_dict()
            if args.snapshot_dir:
                result["snapshot_path"] = str(save_snapshot(
                    capture.snapshot, args.snapshot_dir, owner_scope=args.owner_scope,
                ))
                result["lineage_path"] = str(save_graph(capture.lineage(), args.snapshot_dir))
            print(json.dumps(result, indent=2))
            return 2 if capture.stale else 0
        result = fetch_earthquake_summary()
    except (LiveDataError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 2 if result["stale"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
