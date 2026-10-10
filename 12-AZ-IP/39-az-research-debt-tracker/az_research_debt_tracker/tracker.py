# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Domain-agnostic research/project-debt tracker — Phase 1 of article-354
direction #12 ("MAS Wave Engine -> generic research-debt tracker").

`src/meta/mas_wave_engine.py`'s `GapItem` / `FrameworkScore` /
`validate_wave_output()` already implement a working gap-tracking and
closure-scoring model for Unitary Manifold pillars. This module strips
the UM-specific vocabulary (pillars, falsifiers, epistemic labels tied
to physics) and generalizes the same shape into a configurable
project-health tracker any research or engineering project can use:
named work items with a status drawn from a configurable status set,
severity, and an owner-defined "closed" bucket vs "open" bucket, plus
aggregate closure-fraction scoring and a validation routine for
declaring an item closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional


@dataclass(frozen=True)
class StatusTaxonomy:
    """A project's configurable status vocabulary: which status names
    count as 'closed' vs 'open' for closure-fraction scoring."""

    closed_statuses: FrozenSet[str]
    open_statuses: FrozenSet[str]

    def classify(self, status: str) -> str:
        if status in self.closed_statuses:
            return "closed"
        if status in self.open_statuses:
            return "open"
        raise ValueError(
            f"status {status!r} is not declared in either closed_statuses "
            f"or open_statuses for this taxonomy"
        )


#: A default taxonomy mirroring the shape of `src/meta/mas_wave_engine.py`'s
#: VALID_STATUSES / OPEN_TRACKING_STATUSES split, but with domain-neutral names.
DEFAULT_TAXONOMY = StatusTaxonomy(
    closed_statuses=frozenset({
        "DERIVED", "CONSTRAINED", "CONDITIONAL_THEOREM", "SUBSTANTIALLY_CLOSED",
        "NATURALLY_BOUNDED", "GEOMETRIC_PREDICTION", "BEST_EVIDENCE_CONSTRAINED",
        "FITTED", "PARAMETERIZED", "SELF_CONSISTENT", "META_CLOSED",
    }),
    open_statuses=frozenset({
        "OPEN", "PARTIALLY_CLOSED", "HONEST_OPEN_PROBLEM", "ARCHITECTURE_LIMIT_CERTIFIED",
    }),
)


@dataclass
class WorkItem:
    """A tracked unit of research/project debt — generalizes `GapItem`."""

    item_id: str
    description: str
    status: str
    severity: str
    owner_ref: Optional[str] = None


@dataclass
class ValidationResult:
    """Generalizes `WaveValidationResult`: did a candidate closure of a
    WorkItem satisfy the project's own honesty requirements?"""

    item_id: str
    tests_passed: int
    tests_failed: int
    has_status_label: bool
    has_documentation_entry: bool
    overall_valid: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class HealthScore:
    """Generalizes `FrameworkScore`: aggregate closure accounting."""

    n_closed: int
    n_open: int
    total_items: int
    closed_fraction: float
    open_fraction: float
    by_status: Dict[str, int]


class ResearchDebtTracker:
    """A domain-agnostic tracker for research/engineering debt items."""

    def __init__(self, taxonomy: StatusTaxonomy = DEFAULT_TAXONOMY):
        self.taxonomy = taxonomy
        self._items: Dict[str, WorkItem] = {}

    def add_item(self, item: WorkItem) -> None:
        if item.status not in self.taxonomy.closed_statuses | self.taxonomy.open_statuses:
            raise ValueError(f"unknown status {item.status!r} for item {item.item_id!r}")
        self._items[item.item_id] = item

    def get_item(self, item_id: str) -> Optional[WorkItem]:
        return self._items.get(item_id)

    def open_items(self) -> List[WorkItem]:
        return [i for i in self._items.values() if self.taxonomy.classify(i.status) == "open"]

    def closed_items(self) -> List[WorkItem]:
        return [i for i in self._items.values() if self.taxonomy.classify(i.status) == "closed"]

    def all_items(self) -> List[WorkItem]:
        return list(self._items.values())

    def validate_closure(
        self,
        item_id: str,
        tests_passed: int,
        tests_failed: int,
        has_documentation_entry: bool,
    ) -> ValidationResult:
        """Validate a claimed closure of a WorkItem: require the status
        to resolve to 'closed' under this tracker's taxonomy, all tests
        passing, zero failures, and a documentation entry — mirroring
        `mas_wave_engine.validate_wave_output()`'s own honesty gate."""
        item = self.get_item(item_id)
        issues: List[str] = []
        if item is None:
            issues.append(f"unknown item_id {item_id!r}")
            return ValidationResult(item_id, tests_passed, tests_failed, False, has_documentation_entry, False, issues)

        has_status_label = self.taxonomy.classify(item.status) == "closed"
        if not has_status_label:
            issues.append(f"status {item.status!r} does not resolve to 'closed'")
        if tests_failed != 0:
            issues.append(f"{tests_failed} failing tests")
        if tests_passed <= 0:
            issues.append("no passing tests recorded")
        if not has_documentation_entry:
            issues.append("no documentation entry recorded for this closure")

        overall_valid = len(issues) == 0
        return ValidationResult(
            item_id=item_id,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            has_status_label=has_status_label,
            has_documentation_entry=has_documentation_entry,
            overall_valid=overall_valid,
            issues=issues,
        )

    def health_score(self) -> HealthScore:
        """Generalizes `compute_framework_score()`."""
        by_status: Dict[str, int] = {}
        for item in self._items.values():
            by_status[item.status] = by_status.get(item.status, 0) + 1

        n_closed = len(self.closed_items())
        n_open = len(self.open_items())
        total = n_closed + n_open
        closed_fraction = (n_closed / total) if total else 0.0
        open_fraction = (n_open / total) if total else 0.0
        return HealthScore(
            n_closed=n_closed,
            n_open=n_open,
            total_items=total,
            closed_fraction=closed_fraction,
            open_fraction=open_fraction,
            by_status=by_status,
        )
