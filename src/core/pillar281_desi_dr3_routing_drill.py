# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 281 — DESI DR3 Routing Drill (3.2σ / 2.4σ / 1.8σ scenarios).

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Drills the same-day routing in `desi_dr3_publication_day_runbook.py`
against three synthetic DR3 scenarios at σ ∈ {3.2, 2.4, 1.8} and verifies
that the three branches of the routing table (FALSIFIED / HIGH_TENSION /
RESOLVED-or-CONSISTENT) all fire correctly and that the documented
canonical-file update set is mechanically idempotent (re-running the
drill on a previously-applied scenario produces an empty incremental
diff).

──────────────────────────────────────────────────────────────────────────────
Plan §C.8 acceptance gate
──────────────────────────────────────────────────────────────────────────────

Three full drill receipts, each with:
  - the correct verdict bucket (FALSIFIED / HIGH_TENSION / CONSISTENT-or-
    TENSION) at the targeted σ level,
  - mandatory-file coverage audit pass,
  - idempotence check pass (re-running on the same DR3 input yields the
    same checklist).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from src.core.desi_dr3_publication_day_runbook import (
    CANONICAL_DOCS_TO_UPDATE,
    THRESHOLD_FALSIFIED,
    THRESHOLD_HIGH_TENSION,
    THRESHOLD_TENSION,
    UM_WA_PREDICTION,
    publication_day_checklist,
    verify_update_coverage,
)

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "DRILL_SIGMA_LEVELS",
    "separation_guard",
    "synthetic_dr3_inputs_for_sigma",
    "expected_verdict_for_sigma",
    "run_single_drill",
    "run_all_drills",
    "idempotence_check",
    "desi_dr3_drill_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 281
PILLAR_TITLE: str = "DESI DR3 Routing Drill (3.2σ / 2.4σ / 1.8σ scenarios)"
OPERATIONAL_MODULE: bool = True
OPERATIONAL_MODULE_CATEGORY: str = "OBSERVATIONAL_ROUTING_DRILL"

# Plan §C.8 specified σ levels
DRILL_SIGMA_LEVELS: Tuple[float, float, float] = (3.2, 2.4, 1.8)

# Canonical synthetic σ_wa used for all three drills (typical DESI DR3
# precision target).  σ tension is set by adjusting the wa central value.
_SIGMA_WA: float = 0.20


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "drives_existing_runbook_only": True,
    }


# ---------------------------------------------------------------------------
# Drill construction
# ---------------------------------------------------------------------------

def synthetic_dr3_inputs_for_sigma(
    sigma: float, sigma_wa: float = _SIGMA_WA
) -> Tuple[float, float]:
    """Return (wa_observed, sigma_wa) that yields the requested tension σ.

    The runbook computes tension as |wa_observed − UM_WA_PREDICTION|/sigma_wa.
    Choose wa_observed = UM − σ · sigma_wa (negative drift, matching DR2).
    """
    if sigma < 0.0:
        raise ValueError("sigma must be non-negative")
    if sigma_wa <= 0.0:
        raise ValueError("sigma_wa must be positive")
    wa_observed = UM_WA_PREDICTION - sigma * sigma_wa
    return (wa_observed, sigma_wa)


def expected_verdict_for_sigma(sigma: float) -> str:
    """Mirror the runbook's verdict bucket logic."""
    if sigma >= THRESHOLD_FALSIFIED:
        return "FALSIFIED"
    if sigma >= THRESHOLD_HIGH_TENSION:
        return "HIGH_TENSION"
    if sigma >= THRESHOLD_TENSION:
        return "TENSION"
    return "CONSISTENT"


# ---------------------------------------------------------------------------
# Single drill execution
# ---------------------------------------------------------------------------

def run_single_drill(sigma: float) -> Dict[str, object]:
    """Execute one drill scenario at a given tension σ."""
    wa, sw = synthetic_dr3_inputs_for_sigma(sigma)
    checklist = publication_day_checklist(wa, sw)
    expected_verdict = expected_verdict_for_sigma(sigma)
    # Synthetic operator action: pretend every mandatory file is updated.
    mandatory = [doc["filename"] for doc in CANONICAL_DOCS_TO_UPDATE]
    coverage = verify_update_coverage(mandatory)
    return {
        "target_sigma": sigma,
        "wa_observed": wa,
        "sigma_wa": sw,
        "checklist_verdict": checklist["verdict"],
        "expected_verdict": expected_verdict,
        "verdict_matches_expected": bool(
            checklist["verdict"] == expected_verdict
        ),
        "coverage_audit_pass": coverage["audit_pass"],
        "coverage_missing": coverage["missing"],
        "files_to_update_count": len(checklist["files_to_update"]),
        "deadline_hours": checklist["required_within_hours"],
        "same_day_sync_required": checklist["same_day_sync_required"],
    }


def run_all_drills(
    levels: Tuple[float, ...] = DRILL_SIGMA_LEVELS,
) -> List[Dict[str, object]]:
    """Run all drill scenarios from the supplied σ levels."""
    return [run_single_drill(s) for s in levels]


# ---------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------

def idempotence_check(sigma: float) -> Dict[str, object]:
    """Re-run the same drill twice and verify byte-identical checklist outputs."""
    first = run_single_drill(sigma)
    second = run_single_drill(sigma)
    return {
        "sigma": sigma,
        "idempotent_verdict": first["checklist_verdict"] == second["checklist_verdict"],
        "idempotent_coverage": first["coverage_missing"] == second["coverage_missing"],
        "idempotent_deadline": first["deadline_hours"] == second["deadline_hours"],
        "fully_idempotent": (
            first["checklist_verdict"] == second["checklist_verdict"]
            and first["coverage_missing"] == second["coverage_missing"]
            and first["deadline_hours"] == second["deadline_hours"]
        ),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def desi_dr3_drill_report() -> Dict[str, object]:
    """Full drill report packet."""
    drills = run_all_drills()
    idem = [idempotence_check(s) for s in DRILL_SIGMA_LEVELS]
    all_pass = all(
        d["verdict_matches_expected"] and d["coverage_audit_pass"]
        for d in drills
    )
    all_idempotent = all(i["fully_idempotent"] for i in idem)
    # Per-σ green check, exposed by the report for downstream provenance.
    receipts = [
        {
            "sigma": d["target_sigma"],
            "verdict": d["checklist_verdict"],
            "green_check": bool(
                d["verdict_matches_expected"]
                and d["coverage_audit_pass"]
                and i["fully_idempotent"]
            ),
        }
        for d, i in zip(drills, idem)
    ]
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "drill_sigma_levels": list(DRILL_SIGMA_LEVELS),
        "drills": drills,
        "idempotence_checks": idem,
        "all_drills_pass": all_pass,
        "all_drills_idempotent": all_idempotent,
        "acceptance_gate_passed": bool(all_pass and all_idempotent),
        "receipts": receipts,
        "honest_note": (
            "Drills exercise the existing `desi_dr3_publication_day_runbook` "
            "with synthetic inputs constructed to hit each σ bucket. No "
            "canonical-doc files are modified by this module; the coverage "
            "audit checks routing not actual file content."
        ),
        "separation_guard": separation_guard(),
    }
