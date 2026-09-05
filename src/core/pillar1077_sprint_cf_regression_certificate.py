# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1077 — Sprint CF regression certificate.

Aggregates Sprint CF (v36.2) Track A (Pillars 1062–1067), Track B (Pillars
1068–1073), and Track C (Pillars 1074–1076) into a single sprint-level
closure certificate.

Meaningful progress rule (same as Sprint CE): Sprint CF succeeds iff
  1. Track A: all five Type-B floor theorems are stated and their
     justification classes are upgraded to LEAN4_..._THEOREM_STATED.
  2. Track B: the 6D/F-theory extension attempt returns a binary verdict
     (either TRACK_B_CLOSES_ALL_ATTEMPTED_LANES or
     EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED) with zero hardgate breakage
     and zero new free parameters.
  3. Track C: two external falsifier sharpness theorems are stated and
     registered under the anti-post-hoc-softening ledger.
  4. No runtime label on any of the 208 closed hardgate pillars changes.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1067_track_a_floor_theorems_aggregator import (
    track_a_floor_theorems_aggregator,
)
from src.core.pillar1073_track_b_verdict_aggregator import track_b_verdict_report
from src.core.pillar1076_pre_registered_scientific_verdict_ledger import (
    scientific_verdict_ledger_report,
)

PILLAR_NUMBER: int = 1077
PILLAR_GATE: str = "SPRINT_CF_REGRESSION_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_CF_REGRESSION_CERTIFICATE_COMPLETE"
VERSION: str = "v36.2"
SPRINT_NAME: str = "CF"
NEXT_PILLAR_SLOT: int = 1078

SPRINT_TRACK_PILLARS: Dict[str, List[int]] = {
    "track_a_floor_theorems": [1062, 1063, 1064, 1065, 1066, 1067],
    "track_b_extension_attempt": [1068, 1069, 1070, 1071, 1072, 1073],
    "track_c_falsifier_sharpening": [1074, 1075, 1076],
}


def sprint_cf_regression_certificate() -> Dict[str, Any]:
    track_a = track_a_floor_theorems_aggregator()
    track_b = track_b_verdict_report()
    track_c = scientific_verdict_ledger_report()

    track_a_ok = bool(track_a.get("valid", False))
    track_b_ok = bool(track_b.get("valid", False))
    track_c_ok = bool(track_c.get("valid", False))

    hardgate_untouched = (
        track_b.get("hardgate_non_breakage_verified", False)
        and not track_b.get("runtime_labels_changed", True)
    )
    parameter_free = bool(track_b.get("parameter_free_extension", False))

    meaningful_progress = track_a_ok and track_b_ok and track_c_ok
    sprint_success = meaningful_progress and hardgate_untouched and parameter_free

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "sprint_track_pillars": {k: list(v) for k, v in SPRINT_TRACK_PILLARS.items()},
        "track_a_valid": track_a_ok,
        "track_b_valid": track_b_ok,
        "track_c_valid": track_c_ok,
        "track_b_verdict": track_b.get("verdict"),
        "hardgate_untouched": hardgate_untouched,
        "parameter_free_extension": parameter_free,
        "meaningful_progress": meaningful_progress,
        "sprint_success": sprint_success,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": sprint_success,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cf_regression_certificate()["valid"])
    except (KeyError, TypeError, ValueError):
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1077_summary() -> Dict[str, Any]:
    report = sprint_cf_regression_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CF Regression Certificate",
        "status": PILLAR_STATUS,
        "sprint_success": report["sprint_success"],
        "track_b_verdict": report["track_b_verdict"],
        "valid": report["valid"],
    }
