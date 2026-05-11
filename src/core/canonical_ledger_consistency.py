# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable consistency checks across the canonical status ledgers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[2]

LEDGER_PATHS = {
    "status": ROOT / "STATUS.md",
    "fallibility": ROOT / "FALLIBILITY.md",
    "derivation_status": ROOT / "1-THEORY" / "DERIVATION_STATUS.md",
    "wave_changelog": ROOT / "docs" / "WAVE_CHANGELOG.md",
    "mas_tracker": ROOT / "docs" / "mas_tracker.yml",
}

VERSION_RE = re.compile(r"v\d+\.\d+")
REGRESSION_RE = re.compile(r"(\d+(?:\s\d{3})*) passed\s*[·,]\s*(\d+) skipped\s*[·,]\s*(\d+) deselected", re.IGNORECASE)

__all__ = [
    "LEDGER_PATHS",
    "canonical_ledger_snapshot",
    "canonical_ledger_consistency_report",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_version(text: str) -> str | None:
    match = VERSION_RE.search(text)
    return match.group(0) if match else None


def _extract_regression(text: str) -> Dict[str, int] | None:
    match = REGRESSION_RE.search(text)
    if not match:
        return None
    return {
        "passed": int(match.group(1).replace(" ", "")),
        "skipped": int(match.group(2)),
        "deselected": int(match.group(3)),
    }


def canonical_ledger_snapshot() -> Dict[str, Dict[str, object]]:
    """Return extracted versions and regression tuples from the canonical ledgers."""
    snapshot: Dict[str, Dict[str, object]] = {}
    for key, path in LEDGER_PATHS.items():
        text = _read(path)
        snapshot[key] = {
            "path": str(path),
            "version": _extract_version(text),
            "regression": _extract_regression(text),
        }
    return snapshot


def canonical_ledger_consistency_report() -> Dict[str, object]:
    """Check whether the core ledgers are synchronized on version/regression state."""
    snapshot = canonical_ledger_snapshot()
    core_versions = {
        name: snapshot[name]["version"]
        for name in ("status", "fallibility", "derivation_status")
    }
    version_consistent = len(set(core_versions.values())) == 1

    status_regression = snapshot["status"]["regression"]
    fallibility_regression = snapshot["fallibility"]["regression"]
    regression_consistent = status_regression == fallibility_regression and status_regression is not None

    return {
        "snapshot": snapshot,
        "core_versions": core_versions,
        "version_consistent": version_consistent,
        "regression_consistent": regression_consistent,
        "status_fallibility_regression": status_regression,
        "all_pass": version_consistent and regression_consistent,
    }
