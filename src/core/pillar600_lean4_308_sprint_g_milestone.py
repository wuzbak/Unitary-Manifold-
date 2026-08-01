# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 600 — Lean4 308-theorem Sprint G milestone.

STATUS: LEAN4_308_THEOREM_MILESTONE_CERTIFIED
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "LEAN4_TOTAL",
    "LEAN4_300_BARRIER_CROSSED",
    "SUBSTACK_POST",
    "SPRINT_G_PILLARS",
    "sprint_g_summary",
    "lean4_advancement",
    "milestone_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 600
PILLAR_STATUS: str = "LEAN4_308_THEOREM_MILESTONE_CERTIFIED"
PILLAR_TITLE: str = "Lean4 308-Theorem Sprint G Milestone"
VERSION: str = "v20.3"

LEAN4_TOTAL: int = 308
LEAN4_300_BARRIER_CROSSED: bool = True
SUBSTACK_POST: str = "#279 S03E057"
SPRINT_G_PILLARS: List[int] = [596, 597, 598, 599, 600]


def sprint_g_summary() -> Dict[str, Any]:
    """Return the Sprint G summary."""
    return {
        "sprint": "Sprint G",
        "pillars": SPRINT_G_PILLARS,
        "lean4_before": 274,
        "lean4_after": LEAN4_TOTAL,
        "theorems_added": 34,
        "substack_post": SUBSTACK_POST,
    }



def lean4_advancement() -> Dict[str, Any]:
    """Return the Sprint G Lean4 advancement summary."""
    return {
        "crossed_300_barrier": LEAN4_300_BARRIER_CROSSED,
        "before": 274,
        "after": LEAN4_TOTAL,
        "new_files": [
            "lean4/UnitaryManifold/NPBC5SubgapM.lean",
            "lean4/UnitaryManifold/NPBC5SubgapN.lean",
            "lean4/UnitaryManifold/NPBC5SubgapO.lean",
        ],
        "new_theorems": 34,
    }



def milestone_certificate() -> Dict[str, Any]:
    """Return the 308-theorem milestone certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "lean4_total": LEAN4_TOTAL,
        "barrier_crossed": LEAN4_300_BARRIER_CROSSED,
        "substack_post": SUBSTACK_POST,
        "sprint": "Sprint G",
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 600 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "sprint_g_summary": sprint_g_summary(),
        "lean4_advancement": lean4_advancement(),
        "milestone_certificate": milestone_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
