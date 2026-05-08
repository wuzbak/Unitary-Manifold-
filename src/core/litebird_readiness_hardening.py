# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Strict LiteBIRD publication-readiness path for immediate falsifier execution."""
from __future__ import annotations

from typing import Dict, List

from src.core.falsification_check import check_falsification
from src.core.litebird_boundary import fail_zone_report

__all__ = [
    "CHECKLIST_VERSION",
    "PUBLICATION_CHECKLIST",
    "RECORD_TARGETS",
    "litebird_publication_checklist",
    "litebird_prepublication_packet",
    "record_litebird_measurement",
]

CHECKLIST_VERSION: str = "v10.26"

PUBLICATION_CHECKLIST: List[str] = [
    "confirm_measurement_source_and_sigma",
    "run_falsification_check_cli",
    "capture_window_and_gap_verdict",
    "update_observation_tracker_same_day",
    "sync_canonical_falsifier_feed_same_commit",
]

RECORD_TARGETS: List[str] = [
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "src/core/canonical_falsifier_evidence_feed.py",
    "git history / release note",
]


def litebird_publication_checklist() -> List[Dict[str, object]]:
    """Return the strict checklist required before recording a LiteBIRD result."""
    return [
        {
            "step": idx + 1,
            "item": item,
            "required": True,
        }
        for idx, item in enumerate(PUBLICATION_CHECKLIST)
    ]


def litebird_prepublication_packet() -> Dict[str, object]:
    """Return the execution packet that must be ready before publication day."""
    return {
        "version": CHECKLIST_VERSION,
        "primary_event": "LiteBIRD β publication",
        "checklist": litebird_publication_checklist(),
        "command": "python src/core/falsification_check.py --beta VALUE --sigma UNCERTAINTY",
        "record_targets": list(RECORD_TARGETS),
        "policy": "no_delay_between_measurement_and_recording",
    }


def record_litebird_measurement(
    beta: float,
    sigma: float,
    release_reference: str,
    checklist_complete: bool = True,
) -> Dict[str, object]:
    """Execute the β falsifier and package the exact recording payload."""
    if not checklist_complete:
        return {
            "ready_to_record": False,
            "policy": "blocked_until_checklist_complete",
            "missing_requirement": "publication_checklist_incomplete",
            "record_targets": list(RECORD_TARGETS),
        }

    verdict = check_falsification(beta, sigma)
    boundary = fail_zone_report(beta, sigma)
    return {
        "ready_to_record": True,
        "beta": beta,
        "sigma": sigma,
        "release_reference": release_reference,
        "verdict": verdict.verdict,
        "detail": verdict.message,
        "sector": verdict.sector,
        "boundary_report": boundary,
        "record_targets": list(RECORD_TARGETS),
        "command": f"python src/core/falsification_check.py --beta {beta} --sigma {sigma}",
    }
