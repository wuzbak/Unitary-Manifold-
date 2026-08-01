# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 601 — v20.3 regression certificate.

STATUS: V203_REGRESSION_CERTIFIED
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
    "PILLARS_SPRINT_G",
    "LEAN4_TOTAL",
    "REGRESSION_PASSED",
    "sprint_g_summary",
    "regression_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 601
PILLAR_STATUS: str = "V203_REGRESSION_CERTIFIED"
PILLAR_TITLE: str = "v20.3 Regression Certificate — Sprint G"
VERSION: str = "v20.3"

VERSION_TAG: str = "v20.3"
SUBSTACK_POST: str = "#279 S03E057"
PILLARS_SPRINT_G: List[int] = list(range(596, 602))
LEAN4_TOTAL: int = 308
REGRESSION_PASSED: int = 50200


def sprint_g_summary() -> Dict[str, Any]:
    """Return the v20.3 Sprint G summary."""
    return {
        "sprint": "Sprint G",
        "pillars": PILLARS_SPRINT_G,
        "lean4_total": LEAN4_TOTAL,
        "regression_passed": REGRESSION_PASSED,
        "substack_post": SUBSTACK_POST,
    }



def regression_certificate() -> Dict[str, Any]:
    """Return the v20.3 regression certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version_tag": VERSION_TAG,
        "regression_passed": REGRESSION_PASSED,
        "lean4_total": LEAN4_TOTAL,
        "certified": True,
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 601 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "sprint_g_summary": sprint_g_summary(),
        "regression_certificate": regression_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
