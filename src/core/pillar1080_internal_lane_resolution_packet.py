# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1080 — Internal lane resolution packet for external-critique follow-through.

Executes a deterministic four-lane packet (flavor, UV, CMB, neutrino dependency)
that converts critique pressure into explicit PASS/TENSION/FALSIFIED routing with
named blockers and no unearned closure relabeling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.core.observational_lane_freeze_registry import observational_lane_freeze_registry
from src.core.pillar999_cmb_amplitude_calibration_boundary import pillar999_summary
from src.core.pillar1058_flavor_execution_packet import sprint_cc_flavor_execution_packet
from src.core.pillar1073_track_b_verdict_aggregator import track_b_verdict_report

PILLAR_NUMBER: int = 1080
PILLAR_GATE: str = "CRITIQUE_INTERNAL_LANE_RESOLUTION_PACKET"
PILLAR_STATUS: str = "CRITIQUE_INTERNAL_LANE_RESOLUTION_PACKET_COMPLETE"
VERSION: str = "v36.4"
SPRINT: str = "CH"
NEXT_PILLAR_SLOT: int = 1081

ROUTING_ENUM = {"PASS", "TENSION", "FALSIFIED"}

_ROOT = Path(__file__).resolve().parents[2]
_LIVE_STATUS = _ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"


def _flavor_lane_row() -> Dict[str, Any]:
    packet = sprint_cc_flavor_execution_packet()
    verdict = str(packet.get("deterministic_verdict", "FALSIFIED"))
    lane_verdict = verdict if verdict in ROUTING_ENUM else "FALSIFIED"
    return {
        "lane": "FLAVOR_CL",
        "current_status": "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED / FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED / JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
        "deterministic_verdict": lane_verdict,
        "outcome": packet.get("outcome"),
        "tightened": bool(packet.get("boundary_tightened", False)),
        "runtime_flip_earned": bool(packet.get("runtime_flip_earned", False)),
        "explicit_blocker": "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR and downstream flavor-family unresolved objects",
        "source": "src/core/pillar1058_flavor_execution_packet.py",
    }


def _uv_lane_row() -> Dict[str, Any]:
    report = track_b_verdict_report()
    verdict = "PASS" if report.get("closure_earned", False) else "TENSION"
    return {
        "lane": "UV_SHARED_OBJECT",
        "current_status": "ALPHA_S_TYPE_B_FLOOR / HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
        "deterministic_verdict": verdict,
        "outcome": report.get("verdict"),
        "tightened": report.get("verdict") == "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED",
        "runtime_flip_earned": bool(report.get("closure_earned", False)),
        "explicit_blocker": "Shared compactification object still does not collapse residual floors to closure-grade values.",
        "source": "src/core/pillar1073_track_b_verdict_aggregator.py",
    }


def _cmb_lane_row() -> Dict[str, Any]:
    summary = pillar999_summary()
    ledger = dict(summary.get("evidence_ledger") or {})
    irred = bool(ledger.get("terminal_eft_routes", False))
    verdict = "TENSION" if irred else "FALSIFIED"
    return {
        "lane": "CMB_AMPLITUDE",
        "current_status": "CMB_AMP_CONFIRMED_IRREDUCIBLE",
        "deterministic_verdict": verdict,
        "outcome": summary.get("status"),
        "tightened": irred,
        "runtime_flip_earned": False,
        "explicit_blocker": "Missing nonperturbative amplitude-generation mechanism and global UV transfer-normalization completion.",
        "source": "src/core/pillar999_cmb_amplitude_calibration_boundary.py",
    }


def _neutrino_lane_row() -> Dict[str, Any]:
    payload = json.loads(_LIVE_STATUS.read_text(encoding="utf-8"))
    predictions = list(payload.get("predictions") or [])
    exp3 = next((row for row in predictions if row.get("id") == "EXP-3"), None)
    freeze = observational_lane_freeze_registry()
    if exp3 is None:
        status_text = "MISSING_EXP3_STATUS"
        verdict = "TENSION"
        outcome = "EXP3_MISSING_FAIL_CLOSED"
    else:
        status_text = str(exp3.get("status", ""))
        exp3_status = status_text.upper()
        if any(
            token in exp3_status for token in ("FALSIFIED", "FAIL", "EXCLUDED", "REJECTED")
        ):
            verdict = "FALSIFIED"
        elif any(token in exp3_status for token in ("PASS", "RESOLVED", "CONFIRMED")):
            verdict = "PASS"
        else:
            verdict = "TENSION"
        outcome = exp3.get("verdict")

    tightened = verdict == "PASS"

    if exp3 is None:
        blocker = "EXP-3 lane is missing from live status; fail-closed until JUNO lane is explicitly tracked."
    else:
        blocker = "External JUNO measurement gate not yet complete; no narrative closure allowed ahead of new data."
    return {
        "lane": "NEUTRINO_DEPENDENCY",
        "current_status": status_text,
        "deterministic_verdict": verdict,
        "outcome": outcome,
        "tightened": tightened,
        "runtime_flip_earned": False,
        "explicit_blocker": blocker,
        "source": "9-INFRASTRUCTURE/um_live_status.json (EXP-3) + src/core/observational_lane_freeze_registry.py",
        "freeze_registry_active": bool(freeze.get("freeze_active", False)),
    }


def critique_internal_lane_resolution_packet() -> Dict[str, Any]:
    rows = [
        _flavor_lane_row(),
        _uv_lane_row(),
        _cmb_lane_row(),
        _neutrino_lane_row(),
    ]
    all_routed = all(row["deterministic_verdict"] in ROUTING_ENUM for row in rows)
    tightened_count = sum(1 for row in rows if row.get("tightened"))
    runtime_flip_count = sum(1 for row in rows if row.get("runtime_flip_earned"))
    no_unearned_closure = runtime_flip_count == 0
    unchanged_external_waits = [
        "DESI_DR3_MONITORING",
        "LITEBIRD_BIREFRINGENCE",
    ]
    valid = bool(all_routed and tightened_count >= 1 and no_unearned_closure)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "rows": rows,
        "counts": {
            "pass": sum(1 for row in rows if row["deterministic_verdict"] == "PASS"),
            "tension": sum(
                1 for row in rows if row["deterministic_verdict"] == "TENSION"
            ),
            "falsified": sum(
                1 for row in rows if row["deterministic_verdict"] == "FALSIFIED"
            ),
            "tightened": tightened_count,
            "runtime_flips": runtime_flip_count,
        },
        "outcome": (
            "INTERNAL_LANES_TIGHTENED_WITH_EXPLICIT_BLOCKERS"
            if valid
            else "PACKET_INVALID_OR_UNROUTED"
        ),
        "honesty_boundaries": {
            "no_unearned_closure_labels": no_unearned_closure,
            "external_wait_lanes_unchanged": unchanged_external_waits,
        },
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(critique_internal_lane_resolution_packet()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1080_summary() -> Dict[str, Any]:
    report = critique_internal_lane_resolution_packet()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Critique Internal Lane Resolution Packet",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "outcome": report["outcome"],
        "routing_counts": report["counts"],
    }
