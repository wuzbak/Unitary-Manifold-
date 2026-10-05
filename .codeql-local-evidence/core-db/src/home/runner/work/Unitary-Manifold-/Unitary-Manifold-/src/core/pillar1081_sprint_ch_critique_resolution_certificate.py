# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1081 — Sprint CH critique-resolution certificate.

Integrates:
  - critique-to-proof matrix (P1079),
  - deterministic internal lane packet (P1080),
  - immutable baseline lock and publication packet checks.

This is a non-hardgate execution certificate for rigorous critique handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1079_gemini_critique_proof_matrix import (
    gemini_critique_proof_matrix,
)
from src.core.pillar1080_internal_lane_resolution_packet import (
    critique_internal_lane_resolution_packet,
)

PILLAR_NUMBER: int = 1081
PILLAR_GATE: str = "SPRINT_CH_CRITIQUE_RESOLUTION_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_CH_CRITIQUE_RESOLUTION_CERTIFICATE_COMPLETE"
VERSION: str = "v36.4"
SPRINT: str = "CH"
NEXT_PILLAR_SLOT: int = 1082

_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_PACKET = {
    "execution_report": _ROOT
    / "7-OUTREACH/substack/posts/post-315-s04e018-sprint-ch-execution-report.md",
    "proof_report": _ROOT
    / "7-OUTREACH/substack/posts/post-316-s04e019-sprint-ch-proof-derivation-report.md",
    "unresolved_report": _ROOT
    / "7-OUTREACH/substack/posts/post-317-s04e020-sprint-ch-unresolved-boundaries.md",
    "closeout_report": _ROOT
    / "7-OUTREACH/substack/posts/post-318-s04e021-sprint-ch-final-closeout-verdict.md",
}


def _publication_packet_check() -> Dict[str, Any]:
    exists = {name: path.exists() for name, path in PUBLICATION_PACKET.items()}
    return {"exists": exists, "status": "PASS" if all(exists.values()) else "FAIL"}


def sprint_ch_critique_resolution_certificate() -> Dict[str, Any]:
    matrix = gemini_critique_proof_matrix()
    packet = critique_internal_lane_resolution_packet()
    pubs = _publication_packet_check()

    valid = bool(
        matrix["valid"]
        and packet["valid"]
        and pubs["status"] == "PASS"
        and packet["honesty_boundaries"]["no_unearned_closure_labels"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "dependencies": {
            "pillar1079": matrix,
            "pillar1080": packet,
        },
        "publication_packet": pubs,
        "sprint_success": valid and packet.get("scientific_progress") is True,
        "scientific_progress": packet.get("scientific_progress") is True,
        "packet_valid": valid,
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_ch_critique_resolution_certificate()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1081_summary() -> Dict[str, Any]:
    report = sprint_ch_critique_resolution_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CH Critique Resolution Certificate",
        "status": PILLAR_STATUS,
        "sprint_success": report["sprint_success"],
        "valid": report["valid"],
    }
