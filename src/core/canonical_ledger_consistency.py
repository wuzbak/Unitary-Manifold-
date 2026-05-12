# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable consistency checks across the canonical status ledgers.

The regression-count parser is intentionally tolerant of the formatting currently
used in the canonical ledgers: space-separated thousands ("28 560"), comma-
separated thousands ("28,560"), or plain digit strings ("28560").

Two layers of checks are provided:

1. ``canonical_ledger_consistency_report`` — checks that the six core ledgers
   (README, STATUS, FALLIBILITY, DERIVATION_STATUS, WAVE_CHANGELOG,
   mas_tracker) agree on version and regression counts.

2. ``onboarding_docs_consistency_report`` — checks that the user-facing
   onboarding documents (CONTRIBUTING, 2-REPRODUCIBILITY/README,
   9-INFRASTRUCTURE/TEST/README, .github/copilot-instructions,
   wiki/Getting-Started, wiki/Contributing, MCP_INGEST, WHAT_THIS_MEANS)
   each contain the canonical passed-count extracted from STATUS.md, so
   verifiers cannot be directed to a stale test total.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]

LEDGER_PATHS = {
    "readme": ROOT / "README.md",
    "status": ROOT / "STATUS.md",
    "fallibility": ROOT / "FALLIBILITY.md",
    "derivation_status": ROOT / "1-THEORY" / "DERIVATION_STATUS.md",
    "wave_changelog": ROOT / "docs" / "WAVE_CHANGELOG.md",
    "mas_tracker": ROOT / "docs" / "mas_tracker.yml",
}

# Onboarding documents that must contain the canonical full-suite passed count.
# These are the files that direct contributors and verifiers to the test suite.
ONBOARDING_PATHS: Dict[str, Path] = {
    "contributing": ROOT / "CONTRIBUTING.md",
    "reproducibility_readme": ROOT / "2-REPRODUCIBILITY" / "README.md",
    "test_readme": ROOT / "9-INFRASTRUCTURE" / "TEST" / "README.md",
    "copilot_instructions": ROOT / ".github" / "copilot-instructions.md",
    "wiki_getting_started": ROOT / "9-INFRASTRUCTURE" / "wiki" / "Getting-Started.md",
    "wiki_contributing": ROOT / "9-INFRASTRUCTURE" / "wiki" / "Contributing.md",
    "mcp_ingest": ROOT / "6-MONOGRAPH" / "MCP_INGEST.md",
    "what_this_means": ROOT / "4-IMPLICATIONS" / "WHAT_THIS_MEANS.md",
}

VERSION_RE = re.compile(r"v\d+\.\d+")
# Canonical ledgers currently render large counts with space-separated thousands,
# but we also tolerate comma-separated and plain digit formatting for robustness.
REGRESSION_RE = re.compile(r"(\d+(?:[,\s]+\d{3})*) passed\s*[·,]\s*(\d+) skipped\s*[·,]\s*(\d+) deselected", re.IGNORECASE)

__all__ = [
    "LEDGER_PATHS",
    "ONBOARDING_PATHS",
    "canonical_ledger_snapshot",
    "canonical_ledger_consistency_report",
    "onboarding_docs_consistency_report",
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
        "passed": int(match.group(1).replace(" ", "").replace(",", "")),
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
    public_versions = {
        name: snapshot[name]["version"]
        for name in (
            "readme",
            "status",
            "fallibility",
            "derivation_status",
            "wave_changelog",
            "mas_tracker",
        )
    }
    public_version_consistent = len(set(public_versions.values())) == 1
    public_regression_views = {
        name: snapshot[name]["regression"]
        for name in ("readme", "status", "fallibility")
    }
    public_regression_consistent = (
        public_regression_views["readme"] == public_regression_views["status"] == public_regression_views["fallibility"]
        and public_regression_views["status"] is not None
    )

    return {
        "snapshot": snapshot,
        "core_versions": core_versions,
        "public_versions": public_versions,
        "version_consistent": version_consistent,
        "regression_consistent": regression_consistent,
        "public_version_consistent": public_version_consistent,
        "public_regression_views": public_regression_views,
        "public_regression_consistent": public_regression_consistent,
        "status_fallibility_regression": status_regression,
        "all_pass": (
            version_consistent
            and regression_consistent
            and public_version_consistent
            and public_regression_consistent
        ),
    }


def _contains_passed_count(text: str, passed: int) -> bool:
    """Return True if *any* standard rendering of *passed* appears in *text*.

    Accepted formats: space-separated thousands ("29 425"), comma-separated
    ("29,425"), or plain ("29425"), each followed by the word "passed".
    """
    for sep in (" ", ",", ""):
        rendered = f"{passed:,}".replace(",", sep)
        if re.search(re.escape(rendered) + r"\s+passed", text, re.IGNORECASE):
            return True
    return False


def onboarding_docs_consistency_report() -> Dict[str, object]:
    """Check that every onboarding document contains the canonical passed count.

    The canonical count is taken from STATUS.md (the single source of truth).
    Any onboarding document that does *not* contain that count has drifted and
    will direct contributors or verifiers to a stale total.

    Returns a dict with:
      ``canonical``      – the regression dict extracted from STATUS.md
      ``results``        – per-document {path, found, text_present} entries
      ``drifted_docs``   – list of keys whose content does not contain the count
      ``all_pass``       – True if every onboarding doc contains the canonical count
    """
    status_text = _read(LEDGER_PATHS["status"])
    canonical = _extract_regression(status_text)
    if canonical is None:
        return {
            "canonical": None,
            "results": {},
            "drifted_docs": list(ONBOARDING_PATHS),
            "all_pass": False,
            "error": "Could not extract canonical regression count from STATUS.md",
        }

    passed = canonical["passed"]
    results: Dict[str, Dict[str, object]] = {}
    drifted: List[str] = []

    for key, path in ONBOARDING_PATHS.items():
        try:
            text = _read(path)
            found = _contains_passed_count(text, passed)
        except FileNotFoundError:
            found = False
            text = ""
        results[key] = {
            "path": str(path),
            "exists": path.exists(),
            "canonical_count_found": found,
        }
        if not found:
            drifted.append(key)

    return {
        "canonical": canonical,
        "results": results,
        "drifted_docs": drifted,
        "all_pass": len(drifted) == 0,
    }
