# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Claim-recognition + routing pipeline — the three supporting pieces named
in article-354 direction #6 wired into one orchestrator: a reading-layer
text chunker (Phase 0), a visualization-layer concept mapper (Phase 1), and
a fact-check-layer router into Product 19's existing verdict functions
(Phase 2's narrow, buildable slice — full automatic claim recognition is
not attempted here; recognition is keyword-based and conservative).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from falsification_observatory.engine.routing import (  # noqa: E402
    route_act,
    route_desi,
    route_hllhc,
    route_juno,
    route_litebird,
    route_nedm,
    route_xenon,
)

#: The eight visual concepts Product 17 (UM Image Generator) already
#: renders, transcribed as short metadata (not the rendering code itself).
VISUAL_CONCEPTS = {
    "cmb": {"label": "CMB n_s / r Plane", "keywords": ("spectral index", "n_s", "tensor-to-scalar", "cmb")},
    "birefringence": {"label": "Birefringence β Window", "keywords": ("birefringence", "litebird", "β")},
    "kkTower": {"label": "KK Mass Tower", "keywords": ("kaluza-klein", "kk tower", "kk mode")},
    "braid": {"label": "(5,7) Braid Topology", "keywords": ("braid", "winding number", "(5,7)")},
    "metric": {"label": "5D Metric Structure", "keywords": ("5d metric", "radion", "compact dimension")},
    "dm21": {"label": "Δm²₂₁ Tension Timeline", "keywords": ("juno", "neutrino mass", "δm²", "dm21")},
    "domains": {"label": "Hardgate Domain Pie Chart", "keywords": ("hardgate", "208 pillars", "pillar")},
    "calendar": {"label": "Falsification Calendar", "keywords": ("falsification", "desi", "cmb-s4")},
}

#: Maps a recognizable claim keyword to the matching Product 19 routing
#: function. Each router is called with no observation, which yields the
#: existing, already-tested AWAITING_DATA verdict shape when no value is
#: supplied — exactly the same honest placeholder Product 19 itself uses.
_CLAIM_ROUTERS = {
    "birefringence": route_litebird,
    "dark energy": route_desi,
    "w_a": route_desi,
    "neutrino mass": route_juno,
    "delta m21": route_juno,
    "spectral index": route_act,
    "n_s": route_act,
    "kk gluon": route_hllhc,
    "electric dipole moment": route_nedm,
    "edm": route_nedm,
    "dark matter": route_xenon,
    "xenon": route_xenon,
}


@dataclass(frozen=True)
class ReadingSegment:
    """One sentence-level chunk, ready for a TTS engine."""

    index: int
    text: str


@dataclass(frozen=True)
class AccessibilityReport:
    """Combined reading + visualization + fact-check report for one passage."""

    segments: List[ReadingSegment]
    suggested_visuals: List[str]
    claim_verdicts: List[dict] = field(default_factory=list)


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_into_reading_segments(text: str) -> List[ReadingSegment]:
    """Phase 0 — the reading layer. Splits text into sentence-level chunks
    suitable for a TTS engine to read aloud one at a time."""
    if not text.strip():
        return []
    raw_sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return [ReadingSegment(index=i, text=s) for i, s in enumerate(raw_sentences)]


def suggest_visual_concepts(text: str) -> List[str]:
    """Phase 1 — the visualization layer. Recognizes mentions of any of
    Product 17's eight visual concepts by keyword and returns the matching
    concept keys, in the order they first appear in the text."""
    lowered = text.lower()
    found: List[str] = []
    for key, meta in VISUAL_CONCEPTS.items():
        if any(keyword in lowered for keyword in meta["keywords"]):
            found.append(key)
    return found


def route_recognizable_claims(text: str) -> List[dict]:
    """Phase 2 — the fact-check layer (narrow slice). Recognizes keyword
    mentions of any of Product 19's seven falsification fronts and routes
    them through the existing, already-tested routing functions. No new
    verdict logic is introduced here — every verdict returned is whatever
    Product 19's own router already computes."""
    lowered = text.lower()
    seen_experiments: set[str] = set()
    results: List[dict] = []
    for keyword, router in _CLAIM_ROUTERS.items():
        if keyword in lowered:
            verdict = router()
            if verdict.exp_id in seen_experiments:
                continue
            seen_experiments.add(verdict.exp_id)
            results.append(
                {
                    "matched_keyword": keyword,
                    "exp_id": verdict.exp_id,
                    "name": verdict.name,
                    "verdict": verdict.verdict,
                    "prediction": verdict.prediction,
                }
            )
    return results


def build_accessibility_report(text: str) -> AccessibilityReport:
    """Run all three phases and return a combined report."""
    return AccessibilityReport(
        segments=split_into_reading_segments(text),
        suggested_visuals=suggest_visual_concepts(text),
        claim_verdicts=route_recognizable_claims(text),
    )
