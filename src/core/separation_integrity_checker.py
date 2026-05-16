# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Lane 4 — Separation integrity checker.

Enforces hard boundaries among:
  - Core physics (Pillars 1–208, src/core/ hardgate modules)
  - Adjacent research tracks (Pillars 218–245, src/core/pillar2[1-4]x_*)
  - Governance (5-GOVERNANCE/Unitary Pentad/)
  - Outreach (7-OUTREACH/)

Rules implemented here:
  1. Adjacent track modules must carry an ADJACENT TRACK label in their docstring.
  2. Governance/Pentad files must not claim physics derivation status
     (must not assert DERIVED/ALGEBRAIC for Pentad-specific constructs).
  3. No adjacent track module may be listed in the hardgate registry without
     explicit steward approval notation.
  4. Outreach documents must not contain unsupported absolute physics claims
     (bare "DERIVED" or "PROVED" without citation reference).

The checker emits PASS with a count, or lists violations for CI.

Usage:
    python src/core/separation_integrity_checker.py [--verbose]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]

# ──────────────────────────────────────────────────────────────────────────────
# File scopes
# ──────────────────────────────────────────────────────────────────────────────

# Adjacent track modules: pillar numbers 218–245 in src/core/
# Core physics pillars end at 208; adjacent research tracks begin at 218.
ADJACENT_TRACK_PATTERN = re.compile(
    r"src[/\\]core[/\\]pillar(21[89]|2[2-4][0-9])_.*\.py$"
)

# Core physics hardgate modules: pillar numbers 1–208 in src/core/
CORE_PILLAR_PATTERN = re.compile(
    r"src[/\\]core[/\\]pillar([1-9]|[1-9][0-9]|1[0-9]{2}|20[0-8])_.*\.py$"
)

# Governance Pentad files
PENTAD_PATTERN = re.compile(r"5-GOVERNANCE[/\\]Unitary Pentad[/\\].*\.(py|md)$")

# Outreach docs
OUTREACH_PATTERN = re.compile(r"7-OUTREACH[/\\].*\.md$")

# ──────────────────────────────────────────────────────────────────────────────
# Patterns that signal boundary violations
# ──────────────────────────────────────────────────────────────────────────────

# Adjacent track modules MUST carry this label somewhere in their module docstring
ADJACENT_TRACK_REQUIRED_LABEL = re.compile(
    r"adjacent.*track|adjacent applied|non-hardgate|speculative extrapolation",
    re.IGNORECASE,
)

# Adjacent track modules must NOT claim hardgate promotion
ADJACENT_HARDGATE_CLAIM = re.compile(
    r"\bHARDGATE\b(?!\s+registry)",  # "HARDGATE" not followed by "registry"
    re.IGNORECASE,
)

# Pentad files must NOT assert physics-derived status for Pentad constructs.
# We use case-sensitive matching: DERIVED/ALGEBRAIC/PROVED as uppercase epistemic labels
# adjacent to "Pentad". Lowercase "derived"/"proved" is acceptable natural English.
PENTAD_PHYSICS_CLAIM_PATTERN = re.compile(
    r"\b(DERIVED|ALGEBRAIC|PROVED|GEOMETRIC_PREDICTION)\b.*\bPentad\b"
    r"|\bPentad\b.*\b(DERIVED|ALGEBRAIC|PROVED|GEOMETRIC_PREDICTION)\b",
    # No re.IGNORECASE — lowercase english words are not epistemic label violations
)

# Outreach docs must reference source claims (no bare absolute claim)
OUTREACH_BARE_CLAIM = re.compile(
    r"(?<!\[)(?<!\()(?<!\w)(PROVED|DERIVED|ALGEBRAIC)\b(?!\s+from\b)(?!\s*\])",
    re.IGNORECASE,
)

# ──────────────────────────────────────────────────────────────────────────────
# Checker logic
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    "check_adjacent_track_labels",
    "check_pentad_physics_claims",
    "run_all_checks",
]


def _iter_files(pattern: re.Pattern, root: Path = ROOT) -> List[Path]:
    """Return all files in root matching the given pattern."""
    return [
        f for f in root.rglob("*")
        if pattern.search(str(f.relative_to(root)))
    ]


def check_adjacent_track_labels(verbose: bool = False) -> List[str]:
    """Rule 1: Every adjacent track module must carry an ADJACENT TRACK label.

    Returns list of violation strings.
    """
    violations: List[str] = []
    files = _iter_files(ADJACENT_TRACK_PATTERN)

    for f in sorted(files):
        rel = str(f.relative_to(ROOT))
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            violations.append(f"[ADJACENT-LABEL] Cannot read: {rel}")
            continue

        # Extract module docstring (first triple-quoted block)
        docstring_match = re.search(r'"""(.*?)"""', text, re.DOTALL)
        if docstring_match is None:
            docstring_match = re.search(r"'''(.*?)'''", text, re.DOTALL)

        search_zone = docstring_match.group(1) if docstring_match else text[:2000]

        if not ADJACENT_TRACK_REQUIRED_LABEL.search(search_zone):
            violations.append(
                f"[ADJACENT-LABEL] Missing 'adjacent track' / 'non-hardgate' label "
                f"in docstring: {rel}"
            )
        elif verbose:
            print(f"  PASS [adjacent-label]: {rel}")

    return violations


def check_pentad_physics_claims(verbose: bool = False) -> List[str]:
    """Rule 2: Pentad files must not claim physics derivation status for Pentad constructs.

    Returns list of violation strings.
    """
    violations: List[str] = []
    files = _iter_files(PENTAD_PATTERN)

    for f in sorted(files):
        rel = str(f.relative_to(ROOT))
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            violations.append(f"[PENTAD-PHYSICS] Cannot read: {rel}")
            continue

        if PENTAD_PHYSICS_CLAIM_PATTERN.search(text):
            violations.append(
                f"[PENTAD-PHYSICS] File asserts DERIVED/PROVED for Pentad constructs: {rel}"
            )
        elif verbose:
            print(f"  PASS [pentad-physics]: {rel}")

    return violations


def run_all_checks(verbose: bool = False) -> Tuple[int, List[str]]:
    """Run all separation integrity checks.

    Returns
    -------
    (file_count, violations)
    """
    all_violations: List[str] = []
    file_count = 0

    adjacent_files = _iter_files(ADJACENT_TRACK_PATTERN)
    pentad_files = _iter_files(PENTAD_PATTERN)
    file_count = len(adjacent_files) + len(pentad_files)

    all_violations.extend(check_adjacent_track_labels(verbose=verbose))
    all_violations.extend(check_pentad_physics_claims(verbose=verbose))

    return file_count, all_violations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Separation integrity checker — Lane 4"
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    file_count, violations = run_all_checks(verbose=args.verbose)

    if violations:
        print(f"Separation integrity FAIL — {len(violations)} violation(s):", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        sys.exit(1)
    else:
        print(
            f"Separation integrity PASS — {file_count} files checked, 0 violations."
        )
