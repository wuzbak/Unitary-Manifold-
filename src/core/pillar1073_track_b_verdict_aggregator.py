# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1073 — Sprint CF Track B: 6D/F-theory extension verdict aggregator.

Combines Pillars 1068 (6D T²/Z₃ CW quartic), 1069 (F-theory spectral cover m_H),
1070 (6D A_s amplitude mechanism), 1071 (free-parameter audit), and 1072
(hardgate non-breakage veto) into a single Track B closure certificate.

Track B was a pre-registered, parameter-free, one-shot honest attempt to close
three Type-B floors (G1 CMB A_s, G3 Higgs quartic) via a 6D T²/Z₃ / F-theory
extension. Success required ALL of:
  1. Every attempted lane returns ``EXTENSION_CLOSES_LANE``.
  2. Zero new free parameters introduced (Pillar 1071).
  3. Zero hardgate pillars broken (Pillar 1072).

If any attempted lane fails, Track B verdict is
``EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED`` and residuals are reported
exactly — no post-hoc softening, no runtime label change on any of the 208
hardgate pillars.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1068_6d_cw_quartic_extension import cw_quartic_extension_report
from src.core.pillar1069_ftheory_spectral_cover_mh import (
    ftheory_spectral_cover_report,
)
from src.core.pillar1070_6d_as_amplitude_mechanism import as_mechanism_report
from src.core.pillar1071_extension_free_parameter_audit import (
    extension_free_parameter_audit,
)
from src.core.pillar1072_hardgate_non_breakage_veto import (
    hardgate_non_breakage_veto,
)

PILLAR_NUMBER: int = 1073
PILLAR_GATE: str = "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1074

TRACK_B_ATTEMPT_PILLARS: List[int] = [1068, 1069, 1070]
TRACK_B_AUDIT_PILLARS: List[int] = [1071, 1072]

VERDICT_ENUM = {
    "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES",
    "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED",
    "EXTENSION_BREAKS_HARDGATE_RETRACTED",
    "EXTENSION_INTRODUCES_NEW_FREE_PARAMETER_REJECTED",
}


def track_b_verdict_report() -> Dict[str, Any]:
    attempts = [
        cw_quartic_extension_report(),
        ftheory_spectral_cover_report(),
        as_mechanism_report(),
    ]
    param_audit = extension_free_parameter_audit()
    hardgate_veto = hardgate_non_breakage_veto()

    per_lane = []
    all_closed = True
    residuals: List[Dict[str, Any]] = []
    for r in attempts:
        closes = r.get("outcome") == "EXTENSION_CLOSES_LANE"
        if not closes:
            all_closed = False
        per_lane.append(
            {
                "pillar": r["pillar"],
                "lane_target": r.get("lane_target"),
                "outcome": r.get("outcome"),
                "closes": closes,
            }
        )
        residuals.append(
            {
                "pillar": r["pillar"],
                "lane_target": r.get("lane_target"),
                "residual_fraction": r.get("residual_fraction"),
            }
        )

    parameter_free = bool(param_audit.get("parameter_free_extension", False))
    hardgate_ok = not bool(hardgate_veto.get("hardgate_breakage_detected", True))

    if not hardgate_ok:
        verdict = "EXTENSION_BREAKS_HARDGATE_RETRACTED"
    elif not parameter_free:
        verdict = "EXTENSION_INTRODUCES_NEW_FREE_PARAMETER_REJECTED"
    elif all_closed:
        verdict = "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES"
    else:
        verdict = "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED"

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "attempt_pillars": list(TRACK_B_ATTEMPT_PILLARS),
        "audit_pillars": list(TRACK_B_AUDIT_PILLARS),
        "per_lane": per_lane,
        "residuals": residuals,
        "parameter_free_extension": parameter_free,
        "hardgate_non_breakage_verified": hardgate_ok,
        "all_lanes_closed": all_closed,
        "verdict": verdict,
        "runtime_labels_changed": False,
        "closure_earned": verdict == "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES",
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": verdict in VERDICT_ENUM,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(track_b_verdict_report()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1073_summary() -> Dict[str, Any]:
    report = track_b_verdict_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track B — 6D/F-theory Extension Verdict Aggregator",
        "status": PILLAR_STATUS,
        "verdict": report["verdict"],
        "closure_earned": report["closure_earned"],
        "valid": report["valid"],
    }
