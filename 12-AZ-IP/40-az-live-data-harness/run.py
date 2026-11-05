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
    parser.add_argument("--archive-dir", type=Path, help="existing durable raw-response archive directory")
    parser.add_argument("--replay-archive", help="raw archive SHA-256 to replay without network access")
    args = parser.parse_args(argv)
    if args.replay_archive is not None and not args.replay_archive:
        parser.error("--replay-archive requires a nonempty SHA-256 identifier")
    if args.temporal and (not args.owner_scope or not args.owner_scope.strip()):
        parser.error("--temporal requires --owner-scope")
    if (args.owner_scope or args.snapshot_dir or args.archive_dir or args.replay_archive) and not args.temporal:
        parser.error("--owner-scope, --snapshot-dir and archive options require --temporal")
    if args.replay_archive and not args.archive_dir:
        parser.error("--replay-archive requires --archive-dir")
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
            from az_live_data_harness.capture_archive import load_capture_archive, save_capture_archive

            if args.replay_archive:
                capture = load_capture_archive(
                    args.archive_dir, args.replay_archive, owner_scope=args.owner_scope,
                )
            else:
                capture = fetch_earthquake_snapshot(owner_scope=args.owner_scope)
            result = capture.to_dict()
            result["mode"] = "archive_replay" if args.replay_archive else "live_capture"
            if args.archive_dir:
                result["archive_path"] = str(
                    args.archive_dir / (args.replay_archive + ".json")
                    if args.replay_archive else save_capture_archive(capture, args.archive_dir)
                )
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
