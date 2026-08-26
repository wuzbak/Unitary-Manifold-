#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Fail CI when tracked directories exceed configured entry-count limits."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check tracked directory entry counts against safety limits to avoid "
            "GitHub UI truncation risk."
        )
    )
    parser.add_argument(
        "--config",
        default="TOOLS/checks/large_directory_limits.json",
        help="Path to JSON config file.",
    )
    return parser.parse_args()


def tracked_paths() -> list[PurePosixPath]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    raw = [p for p in result.stdout.decode("utf-8").split("\x00") if p]
    return [PurePosixPath(path) for path in raw]


def build_directory_entry_counts(paths: list[PurePosixPath]) -> dict[str, int]:
    children_by_dir: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        if len(path.parts) < 2:
            continue
        for idx in range(1, len(path.parts)):
            parent = "/".join(path.parts[:idx])
            child = path.parts[idx]
            children_by_dir[parent].add(child)
    return {directory: len(children) for directory, children in children_by_dir.items()}


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))

    default_limit = int(config["default_max_entries"])
    advisory_threshold = int(config.get("advisory_truncation_threshold", 1000))
    explicit_limits = {
        str(directory).strip("/"): int(limit)
        for directory, limit in config.get("explicit_limits", {}).items()
    }

    counts = build_directory_entry_counts(tracked_paths())

    violations: list[tuple[str, int, int]] = []
    advisories: list[tuple[str, int]] = []

    for directory, count in counts.items():
        limit = explicit_limits.get(directory, default_limit)
        if count > limit:
            violations.append((directory, count, limit))
        if count >= advisory_threshold and directory not in explicit_limits:
            advisories.append((directory, count))

    advisories.sort(key=lambda item: item[1], reverse=True)
    violations.sort(key=lambda item: item[1], reverse=True)

    for directory, count in advisories:
        print(
            "::warning::"
            f"{directory} has {count} tracked entries (>= {advisory_threshold}); "
            "GitHub directory view truncation may hide files."
        )

    if violations:
        for directory, count, limit in violations:
            print(
                "::error::"
                f"{directory} has {count} tracked entries, exceeding limit {limit}. "
                "Shard files into subdirectories before merging."
            )
        return 1

    print("OK: tracked directory entry limits respected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
