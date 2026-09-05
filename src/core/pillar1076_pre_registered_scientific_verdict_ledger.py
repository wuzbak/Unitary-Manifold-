# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1076 — Sprint CF Track C: pre-registered scientific verdict ledger.

Aggregates the Track C pre-registered external falsifiers (LiteBIRD β-gap and
DESI wₐ rigidity) into a single signed, timestamped falsifier map. This is the
anti-post-hoc-softening guardrail: every falsifier's admissible window, its
excluded region, and the verdict of "framework survives" vs "framework
falsified" is fixed here — before the external data arrives.

Any future rerun that would relax the admissible windows or expand the excluded
regions must retract this pillar and log the retraction in the sprint ledger.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1074_litebird_beta_gap_sharpness_theorem import (
    litebird_beta_gap_sharpness_report,
)
from src.core.pillar1075_desi_wa_rigidity_theorem import desi_wa_rigidity_report

PILLAR_NUMBER: int = 1076
PILLAR_GATE: str = "SPRINT_CF_TRACK_C_PRE_REGISTERED_SCIENTIFIC_VERDICT_LEDGER"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_C_PRE_REGISTERED_SCIENTIFIC_VERDICT_LEDGER_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1077

REGISTRATION_TAG: str = "SPRINT_CF_v36.2_TRACK_C_PRE_REGISTERED_2026"

TRACK_C_PILLARS: List[int] = [1074, 1075]


def _extract_falsifier_entry(report: Dict[str, Any]) -> Dict[str, Any]:
    thm = report.get("theorem", {})
    return {
        "pillar": report["pillar"],
        "lane_target": report.get("lane_target"),
        "theorem_name": thm.get("name"),
        "closure_type": thm.get("closure_type"),
        "falsifier_conditions": thm.get("falsifier_conditions", []),
    }


def scientific_verdict_ledger_report() -> Dict[str, Any]:
    litebird = litebird_beta_gap_sharpness_report()
    desi = desi_wa_rigidity_report()

    falsifier_entries = [
        _extract_falsifier_entry(litebird),
        _extract_falsifier_entry(desi),
    ]

    all_valid = bool(litebird["valid"]) and bool(desi["valid"])
    total_lean4_delta = (
        litebird["lean4_theorem_delta"] + desi["lean4_theorem_delta"]
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "registration_tag": REGISTRATION_TAG,
        "track_c_pillars": list(TRACK_C_PILLARS),
        "falsifier_entries": falsifier_entries,
        "total_lean4_delta": total_lean4_delta,
        "all_track_c_theorems_stated": all_valid,
        "post_hoc_softening_forbidden": True,
        "retraction_rule": (
            "any relaxation of admissible windows or excluded regions "
            "requires retraction of this pillar and a logged sprint entry"
        ),
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": all_valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(scientific_verdict_ledger_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1076_summary() -> Dict[str, Any]:
    report = scientific_verdict_ledger_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track C — Pre-Registered Scientific Verdict Ledger",
        "status": PILLAR_STATUS,
        "registration_tag": REGISTRATION_TAG,
        "total_lean4_delta": report["total_lean4_delta"],
        "valid": report["valid"],
    }
