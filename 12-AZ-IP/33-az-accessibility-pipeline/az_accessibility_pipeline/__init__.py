# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Accessibility Pipeline — Product 33.

Phase-0/1/2 orchestrator for article-354 direction #6: wires Product 18's
reading layer, Product 17's visualization layer, and Product 19's
fact-check layer together behind one `build_accessibility_report()` call.

Epistemic status: claim recognition is keyword-based and conservative, not
a general NLP claim-extraction model. Every fact-check verdict returned is
whatever Product 19's own, already-tested routing function already
computes — this product introduces no new verdict logic.
"""

from .pipeline import (
    ReadingSegment,
    AccessibilityReport,
    VISUAL_CONCEPTS,
    split_into_reading_segments,
    suggest_visual_concepts,
    route_recognizable_claims,
    build_accessibility_report,
)

__all__ = [
    "ReadingSegment",
    "AccessibilityReport",
    "VISUAL_CONCEPTS",
    "split_into_reading_segments",
    "suggest_visual_concepts",
    "route_recognizable_claims",
    "build_accessibility_report",
]

__version__ = "1.0.0"
