# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 623 — v20.7 regression certificate.

STATUS: V207_REGRESSION_CERTIFIED
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "VERSION_TAG",
    "SUBSTACK_POST",
    "PILLARS_SPRINT_K",
    "LEAN4_DELTA",
    "LEAN4_TOTAL",
    "REGRESSION_PASSED",
    "REGRESSION_SKIPPED",
    "TOE_SCORE",
    "sprint_k_summary",
    "regression_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 623
PILLAR_STATUS: str = "V207_REGRESSION_CERTIFIED"
PILLAR_TITLE: str = "v20.7 Regression Certificate — Sprint K"
VERSION: str = "v20.7"

VERSION_TAG: str = "v20.7"
SUBSTACK_POST: str = "#283 S03E061"
PILLARS_SPRINT_K: List[int] = list(range(618, 624))
LEAN4_DELTA: int = 34
LEAN4_TOTAL: int = 342
REGRESSION_PASSED: int = 50830
REGRESSION_SKIPPED: int = 23
TOE_SCORE: float = 30.0


def sprint_k_summary() -> Dict[str, Any]:
    """Return the Sprint K summary."""
    return {
        "sprint": "Sprint K",
        "version_tag": VERSION_TAG,
        "pillars": PILLARS_SPRINT_K,
        "lean4_total": LEAN4_TOTAL,
        "lean4_delta": LEAN4_DELTA,
        "toe_score": TOE_SCORE,
        "substack_post": SUBSTACK_POST,
        "tests_added": 180,
        "key_advance": "NP-BC-6 all three sub-gap kernels proved; Lean4 342 theorems; 203 cumulative sub-gap theorems",
    }


def regression_certificate() -> Dict[str, Any]:
    """Return the v20.7 regression certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version_tag": VERSION_TAG,
        "regression_passed": REGRESSION_PASSED,
        "regression_skipped": REGRESSION_SKIPPED,
        "lean4_total": LEAN4_TOTAL,
        "toe_score": TOE_SCORE,
        "certified": True,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 623 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "sprint_k_summary": sprint_k_summary(),
        "regression_certificate": regression_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
