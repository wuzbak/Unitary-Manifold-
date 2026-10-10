# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Dogfood example: load `src/meta/mas_wave_engine.py`'s real 6 open gaps
into a generic `ResearchDebtTracker`, proving the generalized tracker can
represent the project's own actual tracked debt, not just synthetic
examples."""

from __future__ import annotations

from typing import List

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

from src.meta.mas_wave_engine import MASWaveEngine

from .tracker import ResearchDebtTracker, StatusTaxonomy, WorkItem

#: Taxonomy matching `mas_wave_engine`'s own OPEN_TRACKING_STATUSES split
#: (all of its tracked gaps use open-bucket statuses by construction).
UM_GAP_TAXONOMY = StatusTaxonomy(
    closed_statuses=frozenset(),
    open_statuses=frozenset({
        "OPEN", "PARTIALLY_CLOSED", "HONEST_OPEN_PROBLEM",
        "ARCHITECTURE_LIMIT_CERTIFIED", "SUBSTANTIALLY_CLOSED",
    }),
)


def load_um_gaps_into_tracker() -> ResearchDebtTracker:
    """Build a ResearchDebtTracker populated with the real, live gap list
    from `MASWaveEngine().audit_all_gaps()` — not a synthetic example."""
    engine = MASWaveEngine()
    gaps = engine.audit_all_gaps()
    tracker = ResearchDebtTracker(taxonomy=UM_GAP_TAXONOMY)
    for gap in gaps:
        tracker.add_item(
            WorkItem(
                item_id=gap.gap_id,
                description=gap.description,
                status=gap.epistemic_status,
                severity=gap.severity,
                owner_ref=f"pillar_{gap.pillar_number}" if gap.pillar_number else None,
            )
        )
    return tracker
