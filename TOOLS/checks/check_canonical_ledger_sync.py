#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pre-merge CI check for canonical ledger sync on status-bearing pillar changes."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.canonical_ledger_consistency import canonical_ledger_sync_requirement


def _git_diff_lines(*, base_sha: str, head_sha: str, name_only: bool) -> list[str]:
    args = ["git", "diff", "--name-only" if name_only else "--name-status", base_sha, head_sha]
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _git_patch_for_path(*, base_sha: str, head_sha: str, path: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--unified=0", base_sha, head_sha, "--", path],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Check canonical ledger sync requirements for a PR diff.")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    changed_files = _git_diff_lines(base_sha=args.base_sha, head_sha=args.head_sha, name_only=True)
    name_status_lines = _git_diff_lines(base_sha=args.base_sha, head_sha=args.head_sha, name_only=False)
    patch_by_path = {
        path: _git_patch_for_path(base_sha=args.base_sha, head_sha=args.head_sha, path=path)
        for path in changed_files
        if path.startswith("src/core/pillar") or path == "src/core/sm_free_parameters.py"
    }
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
