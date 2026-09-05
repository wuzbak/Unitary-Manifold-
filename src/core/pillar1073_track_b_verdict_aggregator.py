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

Missing derivations or incomplete inventories yield an unestablished verdict,
not a tightening certificate. Packet validity is separate from physical progress.
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
    "EXTENSION_IMPACT_REVIEW_REQUIRED",
    "EXTENSION_INTRODUCES_NEW_FREE_PARAMETER_REJECTED",
    "EXTENSION_UNESTABLISHED",
    "EXTENSION_NO_CLOSURE_EARNED",
}


def _derivation_established(report: Dict[str, Any]) -> bool:
    evidence = report.get("derivation_evidence")
    return bool(
        report.get("valid") is True
        and report.get("derivation_established") is True
        and isinstance(evidence, list) and evidence and all(evidence)
    )


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
        closes = bool(
            r.get("outcome") == "EXTENSION_CLOSES_LANE"
            and r.get("closure_earned") is True
            and _derivation_established(r)
        )
        if not closes:
            all_closed = False
        per_lane.append(
            {
                "pillar": r["pillar"],
                "lane_target": r.get("lane_target"),
                "outcome": r.get("outcome"),
                "closes": closes,
                "derivation_established": _derivation_established(r),
                "scientific_progress": bool(
                    r.get("scientific_progress") is True
                    and _derivation_established(r)
                ),
            }
        )
        residuals.append(
            {
                "pillar": r["pillar"],
                "lane_target": r.get("lane_target"),
                "residual_fraction": r.get("residual_fraction"),
            }
        )

    parameter_free = (
        param_audit.get("parameter_free_extension")
        if param_audit.get("valid") is True
        and param_audit.get("parameter_inventory_complete") is True
        else None
    )
    if parameter_free is not True and parameter_free is not False:
        parameter_free = None
    if parameter_free is True and (
        type(param_audit.get("total_new_free_parameters")) is not int
        or param_audit["total_new_free_parameters"] != 0
    ):
        parameter_free = None
    hardgate_ok = bool(
        hardgate_veto.get("valid") is True
        and hardgate_veto.get("hardgate_non_breakage_verified") is True
        and hardgate_veto.get("hardgate_breakage_detected") is False
        and hardgate_veto.get("extension_retracted") is False
        and hardgate_veto.get("extension_review_required") is not True
        and hardgate_veto.get("all_hardgate_pillars_touched") == []
    )
    derivations_established = all(
        _derivation_established(r) for r in attempts
    )
    scientific_progress = any(
        r.get("scientific_progress") is True and _derivation_established(r)
        for r in attempts
    )

    if hardgate_veto.get("hardgate_breakage_detected") is True:
        verdict = "EXTENSION_BREAKS_HARDGATE_RETRACTED"
    elif (hardgate_veto.get("extension_review_required") is True
          or hardgate_veto.get("extension_retracted") is True):
        verdict = "EXTENSION_IMPACT_REVIEW_REQUIRED"
    elif parameter_free is False:
        verdict = "EXTENSION_INTRODUCES_NEW_FREE_PARAMETER_REJECTED"
    elif not derivations_established or parameter_free is None or not hardgate_ok:
        verdict = "EXTENSION_UNESTABLISHED"
    elif all_closed:
        verdict = "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES"
    elif scientific_progress:
        verdict = "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED"
    else:
        verdict = "EXTENSION_NO_CLOSURE_EARNED"

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
        "all_lanes_closed": verdict == "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES",
        "all_attempts_claim_closure": all_closed,
        "scientific_progress": scientific_progress,
        "derivations_established": derivations_established,
        "verdict": verdict,
        "runtime_labels_changed": any(r.get("runtime_label_changed") is True for r in attempts),
        "closure_earned": verdict == "TRACK_B_CLOSES_ALL_ATTEMPTED_LANES",
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": verdict in VERDICT_ENUM,
        "packet_valid": verdict in VERDICT_ENUM,
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
