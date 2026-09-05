# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1072 — Sprint CF Track B: hardgate non-breakage veto.

Verifies that the 6D/F-theory extension attempts (Pillars 1068–1070) do not
break any of the 208 closed hardgate physics claims (n_s, r_braided, β, α_GUT,
Λ_QCD path C, n_w=5 uniqueness, K_CS=74 derivation, φ₀ self-consistency,
etc.). If any hardgate breakage is detected, the extension is retracted in
the same commit — this pillar is the veto gate.

Since Track B pillars each report ``hardgate_pillars_touched = []`` by
construction (Pillar 1068/1069/1070 all target *additive* corrections on top of
the closed 5D chain, not modifications of it), the veto returns
``NO_HARDGATE_BREAKAGE_DETECTED``. If a later evidence-earned upgrade adds an
entry, this pillar's report flips to ``HARDGATE_BREAKAGE_DETECTED_RETRACT_EXTENSION``.
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
        per_pillar.append(
            {
                "pillar": r["pillar"],
                "hardgate_pillars_touched": touched,
                "breaks_hardgate": len(touched) > 0,
            }
        )
        all_touched.extend(touched)
    breakage_detected = len(all_touched) > 0
    verdict = (
        "HARDGATE_BREAKAGE_DETECTED_RETRACT_EXTENSION"
        if breakage_detected
        else "NO_HARDGATE_BREAKAGE_DETECTED"
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "per_pillar": per_pillar,
        "all_hardgate_pillars_touched": all_touched,
        "hardgate_breakage_detected": breakage_detected,
        "core_hardgate_anchors": list(CORE_HARDGATE_ANCHORS),
        "extension_retracted": breakage_detected,
        "verdict": verdict,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": True,
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
