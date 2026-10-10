# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 7: cross-product "home health" dashboard.

Composes three already-tested subsystems into one snapshot call, adding
no new verdict or scoring logic of its own (same non-duplication pattern
Product 33's accessibility pipeline uses for Product 19):

* this toolkit's own live product-registry count (feature 1),
* Product 39's `ResearchDebtTracker.health_score()` over the project's
  real, live MAS Wave Engine gaps, and
* Product 19's `route_all({})` falsification-observatory verdicts across
  all seven tracked experimental fronts.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ._repo import ensure_repo_on_path
from .registry import load_product_registry


@dataclass(frozen=True)
class HomeHealthSnapshot:
    generated_at: str
    product_count: int
    research_debt: Dict[str, Any]
    falsification_fronts: Dict[str, int]
    falsification_detail: List[Dict[str, Any]]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "product_count": self.product_count,
            "research_debt": self.research_debt,
            "falsification_fronts": self.falsification_fronts,
            "falsification_detail": self.falsification_detail,
        }


def _research_debt_summary() -> Dict[str, Any]:
    from az_research_debt_tracker.um_dogfood import load_um_gaps_into_tracker

    tracker = load_um_gaps_into_tracker()
    score = tracker.health_score()
    return {
        "n_open": score.n_open,
        "n_closed": score.n_closed,
        "total_items": score.total_items,
        "open_fraction": round(score.open_fraction, 4),
        "closed_fraction": round(score.closed_fraction, 4),
        "by_status": dict(score.by_status),
    }


def _falsification_summary() -> Dict[str, Any]:
    from dataclasses import asdict

    from falsification_observatory.engine.routing import route_all

    verdicts = route_all({})
    tally: Dict[str, int] = {}
    for verdict in verdicts:
        tally[verdict.verdict] = tally.get(verdict.verdict, 0) + 1
    return tally, [asdict(verdict) for verdict in verdicts]


def build_home_health_snapshot() -> HomeHealthSnapshot:
    """Build one aggregate snapshot of the monorepo's current state.

    Each composed call is independently tested in its own product; this
    function only aggregates their already-validated outputs.
    """
    ensure_repo_on_path()
    product_count = len(load_product_registry())
    research_debt = _research_debt_summary()
    falsification_fronts, falsification_detail = _falsification_summary()
    return HomeHealthSnapshot(
        generated_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
        product_count=product_count,
        research_debt=research_debt,
        falsification_fronts=falsification_fronts,
        falsification_detail=falsification_detail,
    )
