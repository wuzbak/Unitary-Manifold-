# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1083 — Sprint CI foundation-first certificate."""

from __future__ import annotations

import json
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
_PUBLICATION_PACKET_PATH = _ROOT / "docs/sprint_publication_packets.json"
_TRACKER_KEY = "v36_5_sprint_ci"
_REQUIRED_PUBLICATION_KEYS = (
    "findings_report",
    "execution_report",
    "findings_post",
    "merlin_handoff_post",
    "closeout_post",
)


def _repo_file_path(raw_path: str | Path) -> Path | None:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = _ROOT / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(_ROOT)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _load_publication_packet() -> Dict[str, Path]:
    try:
        data = json.loads(_PUBLICATION_PACKET_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    packet = data.get(_TRACKER_KEY, {}) if isinstance(data, dict) else {}
    if not isinstance(packet, dict):
        return {}
    normalized: Dict[str, Path] = {}
    for name, path in packet.items():
        if not isinstance(path, str):
            continue
        file_path = _repo_file_path(path)
        if file_path is not None:
            normalized[name] = file_path
    return normalized


def _publication_packet_check() -> Dict[str, Any]:
    packet = _load_publication_packet()
    exists = {
        name: _repo_file_path(packet.get(name, "")) is not None
        for name in _REQUIRED_PUBLICATION_KEYS
    }
    return {
        "exists": exists,
        "status": "PASS" if exists and all(exists.values()) else "FAIL",
    }


def sprint_ci_foundation_certificate() -> Dict[str, Any]:
    packet = foundation_first_photon_action_audit()
    pubs = _publication_packet_check()
    findings_report_ok = pubs["exists"].get("findings_report", False)
    handoff = packet.get("merlin_handoff", {})
    blocker_contraction = packet.get("blocker_contraction", {})
    initial_questions = blocker_contraction.get("initial_questions", [])
    remaining_blockers = blocker_contraction.get("remaining_blockers", [])
    handoff_ok = bool(
        isinstance(handoff, dict)
        and isinstance(blocker_contraction, dict)
        and handoff.get("primary_lane") == PRIMARY_LANE
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
        packet.get("valid")
        and packet.get("scientific_progress")
        and pubs["status"] == "PASS"
        and findings_report_ok
        and handoff_ok
        and packet.get("honesty_boundaries", {}).get("no_unearned_closure_labels")
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
        "findings_report_ok": findings_report_ok,
        "merlin_handoff_ok": handoff_ok,
        "sprint_success": valid,
        "scientific_progress": bool(packet.get("scientific_progress")),
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
