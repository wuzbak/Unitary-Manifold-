# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Fail-closed scan for session traces and credentials in training_execution artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_EXECUTION_DIR = PRODUCT_ROOT / "training" / "training_execution"

SENSITIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("OPENROUTER_API_KEY", r"OPENROUTER_API_KEY"),
    ("HF_API_TOKEN", r"HF_API_TOKEN"),
    ("GITHUB_TOKEN", r"GITHUB_TOKEN"),
    ("authorization_header", r"Authorization\s*:\s*Bearer\s+[A-Za-z0-9._\-]+"),
    ("jwt_like_token", r"\beyJ[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{10,}\b"),
    ("private_key_marker", r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    ("session_trace_local_storage", r"merlin_active_session"),
    ("profile_key_reference", r"MERLIN_PROFILE_SHARED_KEY"),
)


def _iter_candidate_paths(explicit_paths: list[str]) -> list[Path]:
    if explicit_paths:
        paths = [Path(item).resolve() for item in explicit_paths]
    else:
        paths = sorted(TRAINING_EXECUTION_DIR.rglob("*"))
    return [path for path in paths if path.is_file()]


def _scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    findings: list[str] = []
    for label, pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text):
            findings.append(label)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan training_execution artifacts for traces/secrets before commit.")
    parser.add_argument("paths", nargs="*", help="Optional file paths to scan.")
    args = parser.parse_args()

    violations: list[tuple[str, list[str]]] = []
    for path in _iter_candidate_paths(args.paths):
        findings = _scan_file(path)
        if findings:
            violations.append((str(path), findings))

    if violations:
        print("training_execution trace scan failed:")
        for path, labels in violations:
            print(f"- {path}: {', '.join(sorted(set(labels)))}")
        return 1

    print("training_execution trace scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
