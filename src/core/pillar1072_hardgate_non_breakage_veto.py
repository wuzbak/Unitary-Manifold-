# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1072 — Sprint CF Track B: hardgate non-breakage veto.

An empty touched-pillar declaration is not a calculation of non-breakage.
Without evidence-backed comparisons, compatibility remains unestablished.
Declared impacts conservatively block acceptance pending review.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1068_6d_cw_quartic_extension import cw_quartic_extension_report
from src.core.pillar1069_ftheory_spectral_cover_mh import (
    ftheory_spectral_cover_report,
)
from src.core.pillar1070_6d_as_amplitude_mechanism import as_mechanism_report

PILLAR_NUMBER: int = 1072
PILLAR_GATE: str = "SPRINT_CF_TRACK_B_HARDGATE_NON_BREAKAGE_VETO"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_B_HARDGATE_NON_BREAKAGE_VETO_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1073

# The 208 hardgate physics claims are represented by their canonical anchor
# labels. Any Track B pillar that lists an entry in ``hardgate_pillars_touched``
# is treated as a breakage until proven otherwise.
CORE_HARDGATE_ANCHORS: List[str] = [
    "N_W_EQ_5_UNIQUENESS_PILLAR_70D",
    "K_CS_EQ_74_DERIVATION_PILLARS_58_537",
    "PHI_0_SELF_CONSISTENCY_PILLAR_56",
    "N_S_EQ_0P9635_INFLATION_CHAIN",
    "R_BRAIDED_EQ_0P0315_BICEP_KECK_OK",
    "BETA_BIREFRINGENCE_DUAL_SECTOR",
    "ALPHA_GUT_EQ_NC_OVER_KCS_PILLAR_173",
    "LAMBDA_QCD_PATH_C_GEOMETRIC_PILLAR_182",
    "LAMBDA_GW_DERIVED_PILLAR_404",
]


def hardgate_non_breakage_veto() -> Dict[str, Any]:
    reports = [
        cw_quartic_extension_report(),
        ftheory_spectral_cover_report(),
        as_mechanism_report(),
    ]
    all_touched: List[str] = []
    per_pillar = []
    for r in reports:
        touched = list(r.get("hardgate_pillars_touched", []))
        verified = bool(
            r.get("hardgate_non_breakage_verified") is True
            and r.get("hardgate_comparison_evidence")
            and not touched
        )
        per_pillar.append(
            {
                "pillar": r["pillar"],
                "hardgate_pillars_touched": touched,
                "breaks_hardgate": r.get("hardgate_breakage_detected"),
                "non_breakage_verified": verified,
            }
        )
        all_touched.extend(touched)
    non_breakage_verified = all(row["non_breakage_verified"] for row in per_pillar)
    breakage_detected = (
        True if any(row["breaks_hardgate"] is True for row in per_pillar)
        else False if non_breakage_verified else None
    )
    if breakage_detected is True:
        verdict = "HARDGATE_BREAKAGE_DETECTED_RETRACT_EXTENSION"
    elif all_touched:
        verdict = "HARDGATE_IMPACT_REQUIRES_REVIEW"
    elif non_breakage_verified:
        verdict = "NO_HARDGATE_BREAKAGE_DETECTED"
    else:
        verdict = "HARDGATE_NON_BREAKAGE_UNESTABLISHED"
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "per_pillar": per_pillar,
        "all_hardgate_pillars_touched": all_touched,
        "hardgate_breakage_detected": breakage_detected,
        "hardgate_non_breakage_verified": non_breakage_verified,
        "core_hardgate_anchors": list(CORE_HARDGATE_ANCHORS),
        "extension_retracted": breakage_detected is True or bool(all_touched),
        "verdict": verdict,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": True,
        "packet_valid": True,
        "scientific_progress": False,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(hardgate_non_breakage_veto()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1072_summary() -> Dict[str, Any]:
    report = hardgate_non_breakage_veto()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track B — Hardgate Non-Breakage Veto",
        "status": PILLAR_STATUS,
        "verdict": report["verdict"],
        "extension_retracted": report["extension_retracted"],
        "valid": report["valid"],
    }
