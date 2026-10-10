# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Research-Debt Tracker — Product 39.

Phase 1 of article-354 direction #12: a domain-agnostic project-health
library generalized from `src/meta/mas_wave_engine.py`'s `GapItem` /
`FrameworkScore` / `validate_wave_output()` shape.

Epistemic status: this is a generic library that any project can
configure with its own status taxonomy. `um_dogfood.py` loads the
project's own real, live gap list (from `MASWaveEngine().audit_all_gaps()`)
into the generic tracker as a proof the generalization is faithful to at
least one real consumer, not a synthetic-only demonstration.
"""

from .tracker import (
    StatusTaxonomy,
    DEFAULT_TAXONOMY,
    WorkItem,
    ValidationResult,
    HealthScore,
    ResearchDebtTracker,
)
from .um_dogfood import load_um_gaps_into_tracker, UM_GAP_TAXONOMY
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "StatusTaxonomy",
    "DEFAULT_TAXONOMY",
    "WorkItem",
    "ValidationResult",
    "HealthScore",
    "ResearchDebtTracker",
    "load_um_gaps_into_tracker",
    "UM_GAP_TAXONOMY",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
