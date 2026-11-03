#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Research-Debt Tracker (Product 39)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_research_debt_tracker import load_um_gaps_into_tracker


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Research-debt tracker")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    mode.add_argument("--git-repo", type=Path, help="inventory TODO/FIXME debt in a local Git commit")
    parser.add_argument("--revision", default="HEAD", help="Git commit/ref to inventory (default: HEAD)")
    parser.add_argument("--output", type=Path, help="persist Git inventory JSON (also printed)")
    parser.add_argument("--fail-on-debt", action="store_true", help="exit 1 when Git inventory finds debt")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8139)
    args = parser.parse_args(argv)

    if args.git_repo is None and (args.output or args.fail_on_debt or args.revision != "HEAD"):
        parser.error("--output, --fail-on-debt and --revision require --git-repo")
    if args.git_repo is not None:
        from az_research_debt_tracker.git_ingest import ingest_git_debt

        try:
            report = ingest_git_debt(args.git_repo, args.revision)
            payload = json.dumps(report, indent=2) + "\n"
            if args.output:
                args.output.write_text(payload, encoding="utf-8")
        except (ValueError, OSError) as exc:
            print(f"research-debt tracker: {exc}", file=sys.stderr)
            return 2
        print(payload, end="")
        return 1 if args.fail_on_debt and report["items"] else 0

    if args.serve:
        from az_research_debt_tracker.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    tracker = load_um_gaps_into_tracker()
    score = tracker.health_score()
    print(json.dumps(score.__dict__, indent=2))
    for item in tracker.open_items():
        print(f"- [{item.severity}] {item.item_id}: {item.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
