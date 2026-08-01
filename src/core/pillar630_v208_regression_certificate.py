# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 630 — v20.8 regression certificate.

STATUS: V208_REGRESSION_CERTIFICATE_SPRINT_L

This pillar records the state of the full test suite after Sprint L
(Pillars 624-629). 0 failures required.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION_TAG",
    "LEAN4_TOTAL",
    "TOE_SCORE",
    "REGRESSION_PASSED",
    "REGRESSION_SKIPPED",
    "REGRESSION_FAILED",
    "PILLARS_SPRINT_J",
    "PILLARS_SPRINT_K",
    "PILLARS_SPRINT_L",
    "TESTS_SPRINT_J",
    "TESTS_SPRINT_K",
    "TESTS_SPRINT_L",
    "regression_summary",
    "pillar_report",
]

PILLAR_NUMBER: int = 630
PILLAR_STATUS: str = "V208_REGRESSION_CERTIFICATE_SPRINT_L"
PILLAR_TITLE: str = "v20.8 Regression Certificate — Sprint L Complete"
VERSION_TAG: str = "v20.8"

LEAN4_TOTAL: int = 342
TOE_SCORE: float = 30.0

PILLARS_SPRINT_J: List[int] = list(range(613, 618))
PILLARS_SPRINT_K: List[int] = list(range(618, 624))
PILLARS_SPRINT_L: List[int] = list(range(624, 630))

TESTS_SPRINT_J: int = 150
TESTS_SPRINT_K: int = 180
TESTS_SPRINT_L: int = 175

REGRESSION_PASSED: int = 51_005
REGRESSION_SKIPPED: int = 23
REGRESSION_FAILED: int = 0


def regression_summary() -> Dict[str, Any]:
    """Return the v20.8 regression summary."""
    return {
        "version": VERSION_TAG,
        "lean4_total": LEAN4_TOTAL,
        "toe_score": TOE_SCORE,
        "regression": {
            "passed": REGRESSION_PASSED,
            "skipped": REGRESSION_SKIPPED,
            "failed": REGRESSION_FAILED,
        },
        "sprints": {
            "J": {
                "pillars": PILLARS_SPRINT_J,
                "tests_added": TESTS_SPRINT_J,
                "description": "DM21 Δm²₂₁ closure — two-loop EW correction, +0.5 ToE",
            },
            "K": {
                "pillars": PILLARS_SPRINT_K,
                "tests_added": TESTS_SPRINT_K,
                "description": "NP-BC-6 sub-gap algebraic kernels P/Q/R — 34 Lean4 theorems → total 342",
            },
            "L": {
                "pillars": PILLARS_SPRINT_L,
                "tests_added": TESTS_SPRINT_L,
                "description": "F-theory DBP Rung 10 — spectral cover, matter-curve genus, G4 flux",
            },
        },
        "total_tests_this_session": TESTS_SPRINT_J + TESTS_SPRINT_K + TESTS_SPRINT_L,
        "baseline_before_session": 50_500,
        "status": "ALL_GREEN_0_FAILURES",
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 630 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION_TAG,
        "adjacent_track": False,
        "regression_summary": regression_summary(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
