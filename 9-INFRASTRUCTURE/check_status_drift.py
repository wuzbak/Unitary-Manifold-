# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Cross-surface status drift gate for HF spaces, public-site, and assistant API."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TARGET_FILES = [
    "hf-spaces/README.md",
    "hf-spaces/az-portal/README.md",
    "hf-spaces/oracle-space/README.md",
    "hf-spaces/um-knowledge-dataset/README.md",
    "hf-spaces/az-portal/index.html",
    "hf-spaces/oracle-space/app.py",
    "hf-spaces/axiom-apps/app.py",
    "hf-spaces/az-tools/app.py",
    "hf-spaces/cmb-calc-space/app.py",
    "hf-spaces/az-os/app.py",
    "hf-spaces/az-ip/app.py",
    "hf-spaces/vqe-sandbox/app.py",
    "public-site/README.md",
    "public-site/portal/index.html",
    "public-site/js/assistant.js",
]

REQUIRED_SUBSTRINGS: dict[str, list[str]] = {
    "hf-spaces/README.md": ["um_live_status.json"],
    "hf-spaces/az-portal/README.md": ["um_live_status.json"],
    "hf-spaces/oracle-space/README.md": ["um_live_status.json"],
    "hf-spaces/um-knowledge-dataset/README.md": ["um_live_status.json"],
    "hf-spaces/az-portal/index.html": ["um_live_status.json", 'data-stat="tests"', 'data-stat="lean4"'],
    "hf-spaces/oracle-space/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/axiom-apps/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/az-tools/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/cmb-calc-space/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/az-os/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/az-ip/app.py": ["from space_core.live_status import status_snapshot"],
    "hf-spaces/vqe-sandbox/app.py": ["from space_core.live_status import status_snapshot"],
    "public-site/README.md": ["um_live_status.json"],
    "public-site/portal/index.html": ["um_live_status.json", 'data-stat="tests"', 'data-stat="lean4"'],
    "public-site/js/assistant.js": ["apiEndpoints", "api.axiomzerospc.org"],
}

FORBIDDEN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b56,772\b"),
    re.compile(r"\b57,927\b"),
    re.compile(r"\b59,167\b"),
    re.compile(r"Status snapshot:\s*\*\*v\d+\.\d+"),
    re.compile(r"Current public snapshot:\s*v\d+\.\d+\s*·\s*[\d,]+\s*passing tests"),
]


def run_checks(repo_root: Path | None = None) -> list[str]:
    root = repo_root or REPO_ROOT
    failures: list[str] = []

    for rel in TARGET_FILES:
        path = root / rel
        if not path.exists():
            failures.append(f"{rel}: file missing")
            continue
        text = path.read_text(encoding="utf-8")

        for needle in REQUIRED_SUBSTRINGS.get(rel, []):
            if needle not in text:
                failures.append(f"{rel}: missing required token '{needle}'")

        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                failures.append(f"{rel}: contains stale status pattern '{pattern.pattern}'")

    return failures


def main() -> int:
    failures = run_checks()
    if failures:
        print("STATUS DRIFT CHECK FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("STATUS DRIFT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

