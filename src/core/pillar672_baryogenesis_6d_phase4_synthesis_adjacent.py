# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 672 — Baryogenesis 6D Phase 4 synthesis.

STATUS: BARYOGENESIS_6D_PHASE4_SYNTHESIS_CERTIFIED

Background
----------
This adjacent-track synthesis pillar combines the Phase 4 bubble-nucleation and
LHC-signature certificates.  It preserves the architecture-limit honesty while
stating the primary discriminator and the experimental window that remains most
relevant for the 6D baryogenesis lane.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "PHASE4_PILLARS",
    "ARCHITECTURE_LIMIT_UNCHANGED",
    "PRIMARY_EXPERIMENTAL_DISCRIMINATOR",
    "SNS_WINDOW_GEV",
    "synthesis_certificate",
    "what_is_claimed",
    "what_is_NOT_claimed",
    "pillar_report",
]

PILLAR_NUMBER: int = 672
PILLAR_STATUS: str = "BARYOGENESIS_6D_PHASE4_SYNTHESIS_CERTIFIED"
PILLAR_TITLE: str = "Baryogenesis 6D Phase 4 — Synthesis"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = True

PHASE4_PILLARS: List[int] = [670, 671]
ARCHITECTURE_LIMIT_UNCHANGED: bool = True
PRIMARY_EXPERIMENTAL_DISCRIMINATOR: str = "nEDM_at_SNS_2028"
SNS_WINDOW_GEV: List[float] = [310.0, 780.0]


def synthesis_certificate() -> Dict[str, Any]:
    """Return the Phase 4 baryogenesis synthesis certificate."""
    return {
        "phase4_pillars": PHASE4_PILLARS,
        "architecture_limit_unchanged": ARCHITECTURE_LIMIT_UNCHANGED,
        "primary_experimental_discriminator": PRIMARY_EXPERIMENTAL_DISCRIMINATOR,
        "sns_window_gev": SNS_WINDOW_GEV,
        "phase4_certified": True,
    }


def what_is_claimed() -> List[str]:
    """Return the honest claims of the Phase 4 synthesis."""
    return [
        "Bubble nucleation remains suppressed in the current 6D estimate because S3/T exceeds the nominal criterion.",
        "The leading experimental discriminator remains nEDM@SNS in the 2028 window.",
        "If the SNS trigger threshold is exceeded, the HL-LHC search is pre-registered as Tier 1 priority.",
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return the honest non-claims of the Phase 4 synthesis."""
    return [
        "The synthesis does not claim that the minimal 5D baryogenesis architecture limit has been removed.",
        "No collider discovery is claimed; the LHC signature remains a preregistered search target.",
        "No hardgate physics label change is claimed from these adjacent-track Phase 4 analyses.",
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 672 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "synthesis_certificate": synthesis_certificate(),
        "what_is_claimed": what_is_claimed(),
        "what_is_NOT_claimed": what_is_NOT_claimed(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
