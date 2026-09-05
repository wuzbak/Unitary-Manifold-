# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1071 — Sprint CF Track B: extension free-parameter audit.

Audits parameter inventories of the 6D/F-theory extension attempts.
Unknown inventories remain unknown, even when their declaration lists are empty.
If an established count > 0, the associated
Type-B floor labels do NOT flip to closed — the parameter cost is published in
the article alongside the outcome.

The pre-registered rule is blunt: closure requires zero new free parameters.
If a parameter is introduced, the extension is honest tightening but not a
closure of the floor. This audit is machine-checkable so no post-hoc softening
can occur.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1068_6d_cw_quartic_extension import cw_quartic_extension_report
from src.core.pillar1069_ftheory_spectral_cover_mh import (
    ftheory_spectral_cover_report,
)
from src.core.pillar1070_6d_as_amplitude_mechanism import as_mechanism_report

PILLAR_NUMBER: int = 1071
PILLAR_GATE: str = "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT"
PILLAR_STATUS: str = "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1072


def extension_free_parameter_audit() -> Dict[str, Any]:
    reports = {
        "pillar_1068_cw_quartic": cw_quartic_extension_report(),
        "pillar_1069_ftheory_mh": ftheory_spectral_cover_report(),
        "pillar_1070_as_mechanism": as_mechanism_report(),
    }
    per_pillar = []
    total_new_params = 0
    inventory_complete = True
    all_params: List[str] = []
    for r in reports.values():
        params = list(r["free_parameters_introduced"])
        count = r.get("free_parameter_count")
        established = bool(
            r.get("valid") is True
            and r.get("parameter_inventory_complete") is True
            and isinstance(r.get("parameter_inventory_evidence"), list)
            and r["parameter_inventory_evidence"]
            and all(r["parameter_inventory_evidence"])
            and isinstance(count, int) and not isinstance(count, bool)
            and count == len(params)
            and all(isinstance(param, str) and param.strip() for param in params)
            and len(set(params)) == len(params)
        )
        inventory_complete = inventory_complete and established
        per_pillar.append(
            {
                "pillar": r["pillar"],
                "lane_target": r["lane_target"],
                "outcome": r["outcome"],
                "closure_earned": bool(
                    r.get("closure_earned") is True and established and count == 0
                    and r.get("outcome") == "EXTENSION_CLOSES_LANE"
                    and r.get("derivation_established") is True
                    and r.get("derivation_evidence")
                    and r.get("hardgate_non_breakage_verified") is True
                    and r.get("hardgate_breakage_detected") is False
                    and r.get("hardgate_comparison_evidence")
                    and not r.get("hardgate_pillars_touched")
                ),
                "free_parameters_introduced": params,
                "free_parameter_count": count if established else None,
                "parameter_inventory_complete": established,
            }
        )
        total_new_params += count if established else 0
        all_params.extend(params)
    parameter_free = total_new_params == 0 if inventory_complete else None
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "per_pillar": per_pillar,
        "total_new_free_parameters": total_new_params if inventory_complete else None,
        "all_new_free_parameters": all_params,
        "parameter_free_extension": parameter_free,
        "parameter_inventory_complete": inventory_complete,
        "audit_status": "ESTABLISHED" if inventory_complete else "UNESTABLISHED",
        "scientific_progress": False,
        "packet_valid": True,
        "audit_rule": (
            "closure requires an evidence-backed complete inventory with zero new free parameters; otherwise Type-B "
            "labels are preserved and the parameter cost is published"
        ),
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": True,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(extension_free_parameter_audit()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1071_summary() -> Dict[str, Any]:
    report = extension_free_parameter_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Track B — Extension Free-Parameter Audit",
        "status": PILLAR_STATUS,
        "total_new_free_parameters": report["total_new_free_parameters"],
        "parameter_free_extension": report["parameter_free_extension"],
        "valid": report["valid"],
    }
