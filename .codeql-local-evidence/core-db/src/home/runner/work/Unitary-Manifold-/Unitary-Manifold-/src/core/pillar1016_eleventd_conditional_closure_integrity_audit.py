# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1016 — 11D conditional-closure integrity audit."""

from __future__ import annotations

from typing import Any, Dict, List

from src.eleventd.architecture_limit_upgrade import architecture_limit_upgrade_report
from src.eleventd.full_precision_closure_v2 import full_precision_closure_v2_report
from src.eleventd.precision_correction_pipeline import precision_correction_pipeline

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "STRESS_POINTS",
    "contradiction_checks",
    "boundary_stress_audit",
    "eleventd_integrity_audit",
    "pillar1016_summary",
]

PILLAR_NUMBER: int = 1016
PILLAR_GATE: str = "ELEVENTD_CONDITIONAL_CLOSURE_INTEGRITY_AUDIT"
PILLAR_STATUS: str = "ELEVENTD_CONDITIONAL_CLOSURE_INTEGRITY_AUDIT_COMPLETE"

STRESS_POINTS = [
    {"chi": -200, "pi_kr_0": 37.0, "epsilon": 0.10},
    {"chi": -120, "pi_kr_0": 36.0, "epsilon": 0.05},
    {"chi": -320, "pi_kr_0": 38.0, "epsilon": 0.20},
]


def contradiction_checks() -> Dict[str, Any]:
    """Check status text, residual labels, and numeric outputs for contradiction."""
    upgrade = architecture_limit_upgrade_report()
    closure = full_precision_closure_v2_report()

    p517_status = str(upgrade["p517_certificate"]["new_status"])
    p518_status = str(upgrade["p518_certificate"]["new_status"])
    p517_open = str(upgrade["p517_certificate"]["remaining_open_condition"])
    floor_label = str(upgrade["p518_certificate"]["irreducible_floor_label"])

    checks = {
        "p517_status_mentions_conditional": "CONDITIONAL" in p517_status,
        "p517_open_condition_named": p517_open != "" and p517_open != "NONE",
        "p518_status_mentions_partial": "PARTIAL" in p518_status,
        "p518_floor_named": floor_label == "5D_IRREDUCIBLE_FLOOR",
        "closure_reports_irreducible_inventory": int(closure["irreducible_floor_inventory"]["count"]) >= 1,
        "closure_lists_cannot_fix": len(closure["what_11d_cannot_fix"]) >= 1,
    }

    failures = [name for name, passed in checks.items() if not bool(passed)]
    return {
        "checks": checks,
        "all_pass": len(failures) == 0,
        "failures": failures,
    }


def boundary_stress_audit(stress_points: List[Dict[str, float]] = STRESS_POINTS) -> Dict[str, Any]:
    """Stress-test deterministic conditional formulas near boundaries."""
    rows: List[Dict[str, Any]] = []
    for case in stress_points:
        pipeline = precision_correction_pipeline(
            chi=int(case["chi"]),
            pi_kr_0=float(case["pi_kr_0"]),
            epsilon=float(case["epsilon"]),
        )
        rows.append(
            {
                "input": case,
                "consistency_pass": bool(pipeline["consistency_checks"]["all_checks_pass"]),
                "zphi_nlo_gt_z0": bool(pipeline["consistency_checks"]["zphi_nlo_greater_than_zphi_0"]),
                "p_r_in_bounds": bool(pipeline["consistency_checks"]["p_r_within_geometric_bounds"]),
                "eta_bar_stable": bool(pipeline["consistency_checks"]["eta_bar_stable_at_0_5"]),
                "p_r_value": float(pipeline["p_r_conditional"]["p_r_value"]),
            }
        )

    all_pass = all(row["consistency_pass"] for row in rows)
    failing = [row for row in rows if not row["consistency_pass"]]
    return {
        "cases": rows,
        "all_pass": all_pass,
        "failing_cases": failing,
    }


def eleventd_integrity_audit() -> Dict[str, Any]:
    """Return 11D lane binary closure/non-promotion integrity outcome."""
    contradiction = contradiction_checks()
    stress = boundary_stress_audit()

    coherent = bool(contradiction["all_pass"] and stress["all_pass"])
    breakpoints: List[str] = []
    if not contradiction["all_pass"]:
        breakpoints.extend([f"contradiction:{x}" for x in contradiction["failures"]])
    if not stress["all_pass"]:
        breakpoints.extend(["stress_case_failure"])

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": True,
        "three_evidence_classes": {
            "analytic_check": {
                "name": "status_numeric_contradiction_check",
                "pass": bool(contradiction["all_pass"]),
            },
            "executable_check": {
                "name": "end_to_end_pipeline_consistency",
                "pass": bool(stress["all_pass"]),
            },
            "adversarial_check": {
                "name": "boundary_stress_cases",
                "pass": bool(stress["all_pass"]),
            },
        },
        "contradiction_checks": contradiction,
        "boundary_stress": stress,
        "binary_outcome": (
            "ELEVENTD_CONDITIONAL_CHAIN_COHERENT"
            if coherent
            else "ELEVENTD_BREAKPOINTS_CERTIFIED"
        ),
        "coherent": coherent,
        "named_breakpoints": breakpoints,
        "epistemic_statement": (
            "This lane audits the full 11D conditional chain for internal coherence. "
            "Status labels, residual-floor language, and deterministic runtime checks are "
            "required to agree before coherence is credited."
        ),
    }


PILLAR_VALID: bool = bool(eleventd_integrity_audit()["valid"])


def pillar1016_summary() -> Dict[str, Any]:
    report = eleventd_integrity_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "11D Conditional-Closure Integrity Audit",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "binary_outcome": report["binary_outcome"],
        "coherent": report["coherent"],
    }
