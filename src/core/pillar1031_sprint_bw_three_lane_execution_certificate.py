# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1031 — Sprint BW three-lane execution certificate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1030_sprint_bv_status_coherence_certificate import (
    status_coherence_certificate,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "sprint_bw_three_lane_certificate",
    "pillar1031_summary",
]

PILLAR_NUMBER: int = 1031
PILLAR_GATE: str = "SPRINT_BW_THREE_LANE_EXECUTION_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_BW_THREE_LANE_EXECUTION_CERTIFICATE_COMPLETE"

_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    full = _ROOT / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def sprint_bw_three_lane_certificate() -> Dict[str, Any]:
    """Certify three-lane sprint execution artifacts with explicit binary gates."""
    prior_sync = status_coherence_certificate()
    status_text = _read("STATUS.md")
    plan_text = _read("docs/SPRINT_PLAN.md")
    tracker_text = _read("docs/mas_tracker.yml")
    merlin_tools_text = _read("12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_tools.py")
    merlin_server_text = _read("12-AZ-IP/20-merlin-navigator/ox_navigator/app/server.py")
    merlin_program_text = _read("12-AZ-IP/20-merlin-navigator/MERLIN_PROGRAM.md")
    merlin_readme_text = _read("12-AZ-IP/20-merlin-navigator/README.md")
    outreach_readme_text = _read("7-OUTREACH/substack/README.md")
    article_path = _ROOT / "7-OUTREACH/substack/posts/post-302-s04e005-sprint-bw-three-lane-rigor.md"

    lane1_done = all(
        marker in status_text
        for marker in (
            "v35.3",
            "Sprint BW",
            "1031",
            "CMB_AMP_CONFIRMED_IRREDUCIBLE",
            "ALPHA_S_TYPE_B_FLOOR",
            "LITEBIRD_BIREFRINGENCE",
        )
    ) and all(marker in tracker_text for marker in ("version: \"v35.3\"", "next_pillar_slot: 1032")) and "v35.3" in plan_text

    lane2_done = all(
        marker in merlin_tools_text
        for marker in (
            "evaluateMerlinEmpiricalGate",
            "getMerlinPromotionPacket",
            "authorizeMerlinPrivilege is blocked in orchestration",
        )
    ) and "/api/merlin/promotion-packet" in merlin_server_text and all(
        marker in merlin_program_text
        for marker in ("evaluateMerlinEmpiricalGate", "getMerlinPromotionPacket")
    ) and "/api/merlin/promotion-packet" in merlin_readme_text

    lane3_done = (
        "63,666 passed · 23 skipped · 12 deselected · 0 failed · next pillar slot 1032 (v35.3 Sprint BW)"
        in outreach_readme_text
        and "62,525 passed · 48 skipped · 12 deselected · 0 failed · next pillar slot 993 (v34.0 Sprint BL)"
        not in outreach_readme_text
        and article_path.exists()
    )

    lane_results = {
        "lane1_physics_and_truth_surfaces": lane1_done,
        "lane2_merlin_systems_and_back_room": lane2_done,
        "lane3_integrity_editorial_polish": lane3_done,
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": bool(prior_sync["valid"] and all(lane_results.values())),
        "lane_results": lane_results,
        "prior_dependency": {"pillar1030": prior_sync["valid"]},
        "binary_gate": "all_three_lanes_required",
        "next_pillar_slot": 1032,
    }


PILLAR_VALID: bool = bool(sprint_bw_three_lane_certificate()["valid"])


def pillar1031_summary() -> Dict[str, Any]:
    """Return concise Pillar 1031 summary."""
    report = sprint_bw_three_lane_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "lane_results": report["lane_results"],
        "next_pillar_slot": report["next_pillar_slot"],
    }
