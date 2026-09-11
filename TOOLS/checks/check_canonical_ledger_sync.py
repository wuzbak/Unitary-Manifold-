#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pre-merge CI check for canonical ledger sync on status-bearing pillar changes."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if not (REPO_ROOT / "src" / "core" / "canonical_ledger_consistency.py").is_file():
    raise SystemExit(f"Repository root not found for ledger sync check: {REPO_ROOT}")
sys.path.insert(0, str(REPO_ROOT))

from src.core.canonical_ledger_consistency import (
    _parse_name_status_line,
    canonical_ledger_sync_requirement,
)


def _git_diff_lines(*, base_sha: str, head_sha: str, name_only: bool) -> list[str]:
    args = ["git", "diff", "--find-renames", "--find-copies", "--name-only" if name_only else "--name-status", base_sha, head_sha]
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _git_full_patch(*, base_sha: str, head_sha: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--find-renames", "--find-copies", "--unified=0", base_sha, head_sha],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
_FILE_MARKER_RE = re.compile(r"^(---|\+\+\+) (a|b)/(.*)$")


def _expanded_changed_files(name_only_lines: list[str], name_status_lines: list[str]) -> list[str]:
    changed_paths = {line.strip() for line in name_only_lines if line.strip()}
    for line in name_status_lines:
        entry = _parse_name_status_line(line)
        if not entry:
            continue
        if entry["path"]:
            changed_paths.add(entry["path"])
        if entry["old_path"]:
            changed_paths.add(entry["old_path"])
    return sorted(changed_paths)


def _split_patch_by_path(full_patch: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_header = ""
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_header, current_lines
        if not current_header:
            return
        block = "\n".join([current_header, *current_lines]).strip()
        paths: set[str] = set()
        match = _DIFF_HEADER_RE.match(current_header)
        if match:
            paths.update({match.group(1), match.group(2)})
        for line in current_lines:
            marker_match = _FILE_MARKER_RE.match(line)
            if not marker_match:
                continue
            marker_path = marker_match.group(3)
            if marker_path != "dev/null":
                paths.add(marker_path)
        for path in paths:
            sections[path] = block
        current_header = ""
        current_lines = []

    for line in full_patch.splitlines():
        if line.startswith("diff --git "):
            _flush()
            current_header = line
            continue
        if current_header:
            current_lines.append(line)
    _flush()
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Check canonical ledger sync requirements for a PR diff.")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    name_status_lines = _git_diff_lines(base_sha=args.base_sha, head_sha=args.head_sha, name_only=False)
    changed_files = _expanded_changed_files(
        _git_diff_lines(base_sha=args.base_sha, head_sha=args.head_sha, name_only=True),
        name_status_lines,
    )
    patch_by_path = _split_patch_by_path(_git_full_patch(base_sha=args.base_sha, head_sha=args.head_sha))
    report = canonical_ledger_sync_requirement(
        changed_files=changed_files,
        name_status_lines=name_status_lines,
        patch_by_path=patch_by_path,
    )

    print("Changed files:")
    for path in changed_files:
        print(path)

    if not report["requires_sync"]:
        print("OK: canonical ledger sync not required for this diff.")
        return 0

    if report["all_required_paths_changed"]:
        print("OK: canonical ledger sync present for status-bearing pillar changes.")
        return 0

    for reason in report["reasons"]:
        print(f"::notice::{reason}")
    for path in report["missing_required_paths"]:
        print(f"::error::Missing required ledger update: {path}")
    print("::error::Wave/pillar changes require canonical ledger + changelog synchronization.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
