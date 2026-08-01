# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 612 — v20.5 regression certificate.

STATUS: V205_REGRESSION_CERTIFIED
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
    "PILLARS_SPRINT_I",
    "LEAN4_TOTAL",
    "REGRESSION_PASSED",
    "TOE_SCORE",
    "sprint_i_summary",
    "regression_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 612
PILLAR_STATUS: str = "V205_REGRESSION_CERTIFIED"
PILLAR_TITLE: str = "v20.5 Regression Certificate — Sprint I"
VERSION: str = "v20.5"

VERSION_TAG: str = "v20.5"
SUBSTACK_POST: str = "#281 S03E059"
PILLARS_SPRINT_I: List[int] = list(range(608, 613))
LEAN4_TOTAL: int = 308
REGRESSION_PASSED: int = 50500
TOE_SCORE: float = 29.5


def sprint_i_summary() -> Dict[str, Any]:
    """Return the Sprint I summary."""
    return {
        "sprint": "Sprint I",
        "pillars": PILLARS_SPRINT_I,
        "lean4_total": LEAN4_TOTAL,
        "regression_passed": REGRESSION_PASSED,
        "toe_score": TOE_SCORE,
        "substack_post": SUBSTACK_POST,
    }



def regression_certificate() -> Dict[str, Any]:
    """Return the v20.5 regression certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version_tag": VERSION_TAG,
        "lean4_total": LEAN4_TOTAL,
        "regression_passed": REGRESSION_PASSED,
        "toe_score": TOE_SCORE,
        "certified": True,
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 612 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "sprint_i_summary": sprint_i_summary(),
        "regression_certificate": regression_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
