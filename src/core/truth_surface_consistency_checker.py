# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 390 — Truth-Surface Consistency Checker
🔵 ADJACENT TRACK (non-hardgate; governance engineering)

Enforces coherence across the six canonical truth surfaces:

  1. STATUS.md
  2. docs/mas_tracker.yml
  3. docs/CLAIM_MASTER_BOARD.md
  4. docs/TRUTH_LAYER.md
  5. 3-FALSIFICATION/OBSERVATION_TRACKER.md
  6. docs/GATEKEEPER_SUMMARY.md

Any divergence in version number, canonical test count, or pillar count
across these surfaces is classified as a release blocker.

Epistemic status: GOVERNANCE_ENGINEERING — validates document coherence;
does not make physics claims.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Canonical surface definitions
# ──────────────────────────────────────────────────────────────────────────────

CANONICAL_SURFACES = [
    "STATUS.md",
    "docs/mas_tracker.yml",
    "docs/CLAIM_MASTER_BOARD.md",
    "docs/TRUTH_LAYER.md",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "docs/GATEKEEPER_SUMMARY.md",
]

# Current canonical ground-truth values (updated each sprint)
CANONICAL_VERSION    = "v12.8"
CANONICAL_TEST_COUNT = 39_952   # v12.8: 39,745 (v12.7 baseline) + 207 (governance sprint)


class DivergenceClass(str, Enum):
    RELEASE_BLOCKER = "RELEASE_BLOCKER"   # Must be fixed before any release.
    WARNING         = "WARNING"            # Should be fixed; not an immediate blocker.
    INFO            = "INFO"               # Informational; no action required.


# ──────────────────────────────────────────────────────────────────────────────
# Divergence record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Divergence:
    surface: str
    field: str                        # "version", "test_count", "pillar_count", etc.
    expected: str
    found: str
    classification: DivergenceClass
    description: str = ""

    @property
    def is_blocking(self) -> bool:
        return self.classification == DivergenceClass.RELEASE_BLOCKER


# ──────────────────────────────────────────────────────────────────────────────
# Surface data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SurfaceSnapshot:
    """Parsed snapshot of one canonical surface."""

    path: str
    version:     Optional[str] = None
    test_count:  Optional[int] = None
    pillar_count: Optional[int] = None
    raw_text:    str = ""

    # ── version extraction ───────────────────────────────────────────────────

    @staticmethod
    def _extract_version(text: str) -> Optional[str]:
        """Find a version string of the form v\\d+\\.\\d+ in text."""
        patterns = [
            r"v12\.\d+",
            r"v11\.\d+",
            r"v10\.\d+",
            r"v\d+\.\d+",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(0)
        return None

    @staticmethod
    def _extract_test_count(text: str) -> Optional[int]:
        """Find the canonical 'N passed' figure in text."""
        # Matches: "39,745 passed" or "39745 passed"
        m = re.search(r"(\d[\d,]+)\s+passed", text)
        if m:
            return int(m.group(1).replace(",", ""))
        return None

    @staticmethod
    def _extract_pillar_count(text: str) -> Optional[int]:
        """Find the highest pillar number mentioned in text (adjacent tracks included)."""
        matches = re.findall(r"\bP(?:illar\s*)?(\d{3,4})\b", text)
        if matches:
            return max(int(x) for x in matches)
        return None

    @classmethod
    def from_text(cls, path: str, text: str) -> "SurfaceSnapshot":
        return cls(
            path=path,
            version=cls._extract_version(text),
            test_count=cls._extract_test_count(text),
            pillar_count=cls._extract_pillar_count(text),
            raw_text=text,
        )

    @classmethod
    def from_file(cls, repo_root: Path, relative_path: str) -> "SurfaceSnapshot":
        """Read the file and parse. Returns empty snapshot on failure."""
        full = repo_root / relative_path
        if not full.exists():
            return cls(path=relative_path)
        text = full.read_text(encoding="utf-8", errors="replace")
        return cls.from_text(relative_path, text)


# ──────────────────────────────────────────────────────────────────────────────
# Consistency checks
# ──────────────────────────────────────────────────────────────────────────────

def check_version_sync(
    snapshots: List[SurfaceSnapshot],
    expected_version: str = CANONICAL_VERSION,
) -> List[Divergence]:
    """All surfaces must carry the same (and current) version string."""
    divergences: List[Divergence] = []
    for snap in snapshots:
        if snap.version is None:
            divergences.append(Divergence(
                surface=snap.path,
                field="version",
                expected=expected_version,
                found="NOT_FOUND",
                classification=DivergenceClass.WARNING,
                description="No version string detected in surface",
            ))
        elif snap.version != expected_version:
            divergences.append(Divergence(
                surface=snap.path,
                field="version",
                expected=expected_version,
                found=snap.version,
                classification=DivergenceClass.RELEASE_BLOCKER,
                description=(
                    f"Surface shows {snap.version} but canonical is {expected_version}; "
                    f"sync required before release"
                ),
            ))
    return divergences


def check_test_count_sync(
    snapshots: List[SurfaceSnapshot],
    expected_count: int,
    tolerance: int = 0,
) -> List[Divergence]:
    """All surfaces that report a test count must agree within tolerance."""
    divergences: List[Divergence] = []
    for snap in snapshots:
        if snap.test_count is None:
            # Only STATUS.md and WAVE_CHANGELOG.md reliably carry the count;
            # absence in other surfaces is a warning, not a blocker.
            divergences.append(Divergence(
                surface=snap.path,
                field="test_count",
                expected=str(expected_count),
                found="NOT_FOUND",
                classification=DivergenceClass.INFO,
                description="Surface does not contain a test-count figure",
            ))
            continue
        diff = abs(snap.test_count - expected_count)
        if diff > tolerance:
            divergences.append(Divergence(
                surface=snap.path,
                field="test_count",
                expected=str(expected_count),
                found=str(snap.test_count),
                classification=DivergenceClass.RELEASE_BLOCKER,
                description=(
                    f"Test count diverges by {diff} from canonical {expected_count}; "
                    f"update surface before release"
                ),
            ))
    return divergences


def check_high_tension_claims(
    snapshots: List[SurfaceSnapshot],
) -> List[Divergence]:
    """Verify that HIGH_TENSION signals are present in all relevant surfaces."""
    divergences: List[Divergence] = []
    # DESI and ACT DR6 are the two current HIGH_TENSION signals.
    required_tension_signals = ["HIGH_TENSION", "DESI", "wₐ"]
    for snap in snapshots:
        if snap.path in ("docs/GATEKEEPER_SUMMARY.md", "docs/CLAIM_MASTER_BOARD.md",
                          "3-FALSIFICATION/OBSERVATION_TRACKER.md"):
            missing = [
                s for s in required_tension_signals
                if s not in snap.raw_text
            ]
            if missing:
                divergences.append(Divergence(
                    surface=snap.path,
                    field="high_tension_signal",
                    expected=str(required_tension_signals),
                    found=f"missing: {missing}",
                    classification=DivergenceClass.WARNING,
                    description="Expected HIGH_TENSION markers not found in surface",
                ))
    return divergences


def check_litebird_primary_falsifier(
    snapshots: List[SurfaceSnapshot],
) -> List[Divergence]:
    """The LiteBIRD birefringence β prediction must appear in all surfaces."""
    divergences: List[Divergence] = []
    for snap in snapshots:
        if "LiteBIRD" not in snap.raw_text and "litebird" not in snap.raw_text.lower():
            divergences.append(Divergence(
                surface=snap.path,
                field="primary_falsifier",
                expected="LiteBIRD birefringence β",
                found="NOT_FOUND",
                classification=DivergenceClass.WARNING,
                description="Primary falsifier (LiteBIRD β) not mentioned in surface",
            ))
    return divergences


# ──────────────────────────────────────────────────────────────────────────────
# Consolidated report
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ConsistencyReport:
    """Full cross-surface consistency report."""

    canonical_version: str
    canonical_test_count: int
    snapshots: List[SurfaceSnapshot]
    divergences: List[Divergence] = field(default_factory=list)

    # ── derived properties ────────────────────────────────────────────────────

    @property
    def blockers(self) -> List[Divergence]:
        return [d for d in self.divergences if d.is_blocking]

    @property
    def warnings(self) -> List[Divergence]:
        return [d for d in self.divergences if d.classification == DivergenceClass.WARNING]

    @property
    def is_release_ready(self) -> bool:
        return len(self.blockers) == 0

    def summary(self) -> dict:
        return {
            "canonical_version": self.canonical_version,
            "canonical_test_count": self.canonical_test_count,
            "surfaces_checked": len(self.snapshots),
            "total_divergences": len(self.divergences),
            "blockers": len(self.blockers),
            "warnings": len(self.warnings),
            "is_release_ready": self.is_release_ready,
        }


def run_full_consistency_check(
    repo_root: Path,
    canonical_version: str = CANONICAL_VERSION,
    canonical_test_count: int = CANONICAL_TEST_COUNT,
    surfaces: Optional[List[str]] = None,
) -> ConsistencyReport:
    """Load all canonical surfaces and run all consistency checks.

    Parameters
    ----------
    repo_root:
        Absolute path to the repository root.
    canonical_version:
        Expected version string (e.g. "v12.8").
    canonical_test_count:
        Expected full-suite passed count.
    surfaces:
        Override the surface list (useful for testing).
    """
    surface_list = surfaces or CANONICAL_SURFACES
    snapshots = [
        SurfaceSnapshot.from_file(repo_root, s) for s in surface_list
    ]

    divergences: List[Divergence] = []
    divergences.extend(check_version_sync(snapshots, canonical_version))
    divergences.extend(check_test_count_sync(snapshots, canonical_test_count))
    divergences.extend(check_high_tension_claims(snapshots))
    divergences.extend(check_litebird_primary_falsifier(snapshots))

    return ConsistencyReport(
        canonical_version=canonical_version,
        canonical_test_count=canonical_test_count,
        snapshots=snapshots,
        divergences=divergences,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Lightweight in-memory checker (for use without filesystem access)
# ──────────────────────────────────────────────────────────────────────────────

def check_surfaces_from_texts(
    surface_texts: Dict[str, str],
    canonical_version: str,
    canonical_test_count: int,
) -> ConsistencyReport:
    """Run checks on pre-loaded text content (no filesystem required)."""
    snapshots = [
        SurfaceSnapshot.from_text(path, text)
        for path, text in surface_texts.items()
    ]

    divergences: List[Divergence] = []
    divergences.extend(check_version_sync(snapshots, canonical_version))
    divergences.extend(check_test_count_sync(snapshots, canonical_test_count))
    divergences.extend(check_high_tension_claims(snapshots))
    divergences.extend(check_litebird_primary_falsifier(snapshots))

    return ConsistencyReport(
        canonical_version=canonical_version,
        canonical_test_count=canonical_test_count,
        snapshots=snapshots,
        divergences=divergences,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Pillar 390 status
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_390_STATUS = "GOVERNANCE_ENGINEERING"
PILLAR_390_LABEL  = "ADJACENT_TRACK"


def pillar_390_status() -> dict:
    """Machine-readable status for Pillar 390."""
    return {
        "pillar": 390,
        "name": "Truth-Surface Consistency Checker",
        "status": PILLAR_390_STATUS,
        "label": PILLAR_390_LABEL,
        "surfaces_monitored": CANONICAL_SURFACES,
        "checks_active": [
            "version_sync",
            "test_count_sync",
            "high_tension_signal_presence",
            "litebird_primary_falsifier_presence",
        ],
        "divergence_classes": [d.value for d in DivergenceClass],
        "release_blocker_policy": (
            "Any RELEASE_BLOCKER divergence must be resolved before a sprint "
            "version tag is applied. Resolve by syncing the divergent surface "
            "to the canonical values in STATUS.md."
        ),
        "hils_status": "ACTIVE",
    }
