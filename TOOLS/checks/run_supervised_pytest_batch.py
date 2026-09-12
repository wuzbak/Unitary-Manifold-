# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Workflow entrypoint for supervised pytest batching."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

from src.core.regression_supervision_plan import (
    DEFAULT_FAST_BATCH_COUNT,
    build_regression_supervision_plan,
    compactified_preflight_command,
    fast_batch_command,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite",
        choices=("tests-fast", "compactified-preflight", "supervisor-check"),
        required=True,
    )
    parser.add_argument("--batch-count", type=int, default=DEFAULT_FAST_BATCH_COUNT)
    parser.add_argument("--batch-index", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    return parser.parse_args()


def _run(command: str, dry_run: bool) -> int:
    print(command)
    if dry_run:
        return 0
    completed = subprocess.run(command, shell=True)
    return completed.returncode


def main() -> int:
    args = _parse_args()
    plan = build_regression_supervision_plan(batch_count=args.batch_count)

    if args.emit_json:
        print(json.dumps(plan, indent=2, sort_keys=True))

    if args.suite == "supervisor-check":
        ok = plan["supervision"]["coverage_matches_discovery"] and plan["supervision"]["all_files_unique"]
        if not ok:
            print("supervised regression coverage check failed", file=sys.stderr)
            return 1
        print("supervised regression coverage check passed")
        return 0

    if args.suite == "compactified-preflight":
        return _run(compactified_preflight_command(), dry_run=args.dry_run)

    if args.batch_index is None:
        print("--batch-index is required for tests-fast", file=sys.stderr)
        return 2
    return _run(
        fast_batch_command(batch_index=args.batch_index, batch_count=args.batch_count),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
