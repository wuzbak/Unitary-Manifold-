# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1083 — Sprint CI foundation-first certificate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1082_foundation_first_photon_action_audit import (
    foundation_first_photon_action_audit,
)

PILLAR_NUMBER: int = 1083
PILLAR_GATE: str = "SPRINT_CI_FOUNDATION_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_CI_FOUNDATION_CERTIFICATE_COMPLETE"
VERSION: str = "v36.5"
SPRINT: str = "CI"
NEXT_PILLAR_SLOT: int = 1084
PRIMARY_LANE: str = "FOUNDATION_PHOTON_ACTION"

_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_PACKET = {
    "findings_report": _ROOT
    / "7-OUTREACH/self-run-reports/FINDINGS_REPORT_2026-09-06_SRR-20260906-P1083-R1.md",
    "execution_report": _ROOT
    / "7-OUTREACH/substack/posts/post-321-s04e024-sprint-ci-foundation-lane-execution.md",
    "findings_post": _ROOT
    / "7-OUTREACH/substack/posts/post-322-s04e025-sprint-ci-photon-action-findings.md",
    "merlin_handoff_post": _ROOT
    / "7-OUTREACH/substack/posts/post-323-s04e026-sprint-ci-merlin-handoff-and-next-sprint-map.md",
    "closeout_post": _ROOT
    / "7-OUTREACH/substack/posts/post-324-s04e027-sprint-ci-closeout-verdict.md",
}


def _publication_packet_check() -> Dict[str, Any]:
    exists = {name: path.exists() for name, path in PUBLICATION_PACKET.items()}
    return {"exists": exists, "status": "PASS" if all(exists.values()) else "FAIL"}


def sprint_ci_foundation_certificate() -> Dict[str, Any]:
    packet = foundation_first_photon_action_audit()
    pubs = _publication_packet_check()
    handoff = packet["merlin_handoff"]
    handoff_ok = bool(
        handoff.get("primary_lane") == PRIMARY_LANE
        and isinstance(handoff.get("evidence_reviewed"), list)
        and len(handoff["evidence_reviewed"]) > 0
        and "blocker_state_before" in handoff
        and isinstance(handoff["blocker_state_before"], list)
        and "blocker_state_after" in handoff
        and isinstance(handoff["blocker_state_after"], list)
        and handoff.get("next_required_action")
    )
    valid = bool(
        packet["valid"]
        and packet["scientific_progress"]
        and pubs["status"] == "PASS"
        and handoff_ok
        and packet["honesty_boundaries"]["no_unearned_closure_labels"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "dependencies": {"pillar1082": packet},
        "publication_packet": pubs,
        "merlin_handoff_ok": handoff_ok,
        "sprint_success": valid,
        "scientific_progress": packet["scientific_progress"],
        "valid": valid,
        "packet_valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_ci_foundation_certificate()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1083_summary() -> Dict[str, Any]:
    report = sprint_ci_foundation_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CI Foundation Certificate",
        "status": PILLAR_STATUS,
        "sprint_success": report["sprint_success"],
        "valid": report["valid"],
    }
