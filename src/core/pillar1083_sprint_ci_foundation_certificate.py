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
_TRACKER_PATH = _ROOT / "docs/mas_tracker.yml"
_TRACKER_KEY = "v36_5_sprint_ci"


def _load_publication_packet() -> Dict[str, Path]:
    lines = _TRACKER_PATH.read_text(encoding="utf-8").splitlines()
    in_sprint = False
    in_packet = False
    packet: Dict[str, Path] = {}

    for line in lines:
        if not in_sprint:
            if line == f"{_TRACKER_KEY}:":
                in_sprint = True
            continue

        if line and not line.startswith(" "):
            break

        if not in_packet:
            if line.strip() == "publication_packet:":
                in_packet = True
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent < 4:
            break
        if indent != 4:
            continue

        key, _, raw_value = line.strip().partition(":")
        value = raw_value.strip().strip('"')
        if key and value:
            packet[key] = _ROOT / value

    return packet


PUBLICATION_PACKET = _load_publication_packet()


def _publication_packet_check() -> Dict[str, Any]:
    exists = {name: path.exists() for name, path in PUBLICATION_PACKET.items()}
    return {
        "exists": exists,
        "status": "PASS" if exists and all(exists.values()) else "FAIL",
    }


def sprint_ci_foundation_certificate() -> Dict[str, Any]:
    packet = foundation_first_photon_action_audit()
    pubs = _publication_packet_check()
    handoff = packet["merlin_handoff"]
    initial_questions = packet["blocker_contraction"]["initial_questions"]
    remaining_blockers = packet["blocker_contraction"]["remaining_blockers"]
    handoff_ok = bool(
        handoff.get("primary_lane") == PRIMARY_LANE
        and isinstance(handoff.get("evidence_reviewed"), list)
        and len(handoff["evidence_reviewed"]) > 0
        and "blocker_state_before" in handoff
        and isinstance(handoff["blocker_state_before"], list)
        and handoff["blocker_state_before"] == initial_questions
        and "blocker_state_after" in handoff
        and isinstance(handoff["blocker_state_after"], list)
        and len(handoff["blocker_state_after"]) > 0
        and handoff["blocker_state_after"] == remaining_blockers
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
