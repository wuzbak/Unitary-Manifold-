#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Fail CI when newly tracked files exceed size safety limits."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 5 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check tracked file sizes against anti-bloat limit.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help="Maximum allowed size for any tracked file.",
    )
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        help="Exact repo-relative path to allow above threshold; repeatable.",
    )
    parser.add_argument(
        "--base-sha",
        default="",
        help="Optional git base SHA; when provided with --head-sha checks only changed files.",
    )
    parser.add_argument(
        "--head-sha",
        default="",
        help="Optional git head SHA; when provided with --base-sha checks only changed files.",
    )
    return parser.parse_args()


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=False,
    )
    raw = [p for p in result.stdout.decode("utf-8").split("\x00") if p]
    return [Path(p) for p in raw]


def changed_paths(base_sha: str, head_sha: str) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=AMRT",
            f"{base_sha}...{head_sha}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    raw = [p.strip() for p in result.stdout.splitlines() if p.strip()]
    return [Path(p) for p in raw]


def main() -> int:
    args = parse_args()
    max_bytes = int(args.max_bytes)
    allow = set(args.allow)
    base_sha = args.base_sha.strip()
    head_sha = args.head_sha.strip()

    violations: list[tuple[str, int]] = []
    candidate_paths = (
        changed_paths(base_sha=base_sha, head_sha=head_sha)
        if base_sha and head_sha
        else tracked_paths()
    )
    for path in candidate_paths:
        rel = path.as_posix()
        if rel in allow:
            continue
        if not path.exists() or path.is_dir():
            continue
        size = os.path.getsize(path)
        if size > max_bytes:
            violations.append((rel, size))

    if violations:
        for rel, size in sorted(violations, key=lambda item: item[1], reverse=True):
            print(
                "::error::"
                f"{rel} is {size} bytes, above limit {max_bytes}. "
                "Move heavy artifacts to DVC/LFS or add an explicit allowlist entry."
            )
        return 1

    print(f"OK: tracked files are <= {max_bytes} bytes (excluding allowlist).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
