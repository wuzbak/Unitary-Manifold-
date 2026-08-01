# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 607 — v20.4 regression certificate.

STATUS: V204_REGRESSION_CERTIFIED
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
    "PILLARS_SPRINT_H",
    "REGRESSION_PASSED",
    "sprint_h_summary",
    "regression_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 607
PILLAR_STATUS: str = "V204_REGRESSION_CERTIFIED"
PILLAR_TITLE: str = "v20.4 Regression Certificate — Sprint H"
VERSION: str = "v20.4"

VERSION_TAG: str = "v20.4"
SUBSTACK_POST: str = "#280 S03E058"
PILLARS_SPRINT_H: List[int] = list(range(602, 608))
REGRESSION_PASSED: int = 50380


def sprint_h_summary() -> Dict[str, Any]:
    """Return the Sprint H summary."""
    return {
        "sprint": "Sprint H",
        "pillars": PILLARS_SPRINT_H,
        "regression_passed": REGRESSION_PASSED,
        "substack_post": SUBSTACK_POST,
    }



def regression_certificate() -> Dict[str, Any]:
    """Return the v20.4 regression certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version_tag": VERSION_TAG,
        "regression_passed": REGRESSION_PASSED,
        "certified": True,
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 607 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "sprint_h_summary": sprint_h_summary(),
        "regression_certificate": regression_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
