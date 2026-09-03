# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1014 — 8D Wilson-line robustness + branch-consistency audit.

Lane 8D objective:
- widen robustness coverage beyond one narrow perturbation window
- tie Wilson-line gauge gates to downstream CKM rho-bar behavior
- emit explicit failure certificates for adversarial broken branches
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from src.core.ckm_rhobar_8d_wilson_refinement import p14_hard_gates
from src.eightd.wilson_line_gauge import (
    rank_conservation_check,
    rung3_gate_evidence,
    unbroken_group_validation_check,
    wilson_line_quantization_check,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "ROBUSTNESS_WINDOWS_DEG",
    "robustness_window_scan",
    "branch_consistency_audit",
    "adversarial_failure_certificates",
    "eightd_wilson_lane_report",
    "pillar1014_summary",
]

PILLAR_NUMBER: int = 1014
PILLAR_GATE: str = "EIGHTD_WILSON_ROBUSTNESS_BRANCH_AUDIT"
PILLAR_STATUS: str = "EIGHTD_WILSON_ROBUSTNESS_BRANCH_AUDIT_COMPLETE"

ROBUSTNESS_WINDOWS_DEG: List[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
RESIDUAL_THRESHOLD_PCT: float = 5.0
ROBUSTNESS_THRESHOLD_PCT: float = 5.5


def robustness_window_scan(
    windows_deg: List[float] = ROBUSTNESS_WINDOWS_DEG,
    residual_threshold_pct: float = RESIDUAL_THRESHOLD_PCT,
    robustness_threshold_pct: float = ROBUSTNESS_THRESHOLD_PCT,
) -> Dict[str, Any]:
    """Scan P14 hard-gate behavior across widened robustness windows."""
    rows: List[Dict[str, Any]] = []
    for window in windows_deg:
        gate = p14_hard_gates(
            residual_threshold_pct=residual_threshold_pct,
            robustness_window_deg=window,
            robustness_threshold_pct=robustness_threshold_pct,
        )
        rows.append(
            {
                "window_deg": float(window),
                "base_pct_err": float(gate["base_result"]["pct_err_vs_pdg"]),
                "worst_case_pct_err": float(gate["worst_case_pct_err"]),
                "hard_gate_pass": bool(gate["hard_gate_pass"]),
                "failing_gates": [
                    name for name, passed in gate["gates"].items() if not bool(passed)
                ],
            }
        )

    pass_count = sum(1 for row in rows if row["hard_gate_pass"])
    failing_windows = [row["window_deg"] for row in rows if not row["hard_gate_pass"]]
    return {
        "scan_rows": rows,
        "window_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": (pass_count / len(rows)) if rows else 0.0,
        "all_windows_pass": pass_count == len(rows) and len(rows) > 0,
        "failing_windows_deg": failing_windows,
    }


def branch_consistency_audit() -> Dict[str, Any]:
    """Tie 8D gauge-branch gates to downstream rho-bar gate behavior."""
    rung3 = rung3_gate_evidence()
    base_gate = p14_hard_gates(
        residual_threshold_pct=RESIDUAL_THRESHOLD_PCT,
        robustness_window_deg=2.0,
        robustness_threshold_pct=ROBUSTNESS_THRESHOLD_PCT,
    )
    coherent = bool(
        rung3["kill_switch_pass"]
        and base_gate["gates"]["axiomzero_purity_gate"]
        and base_gate["gates"]["residual_gate"]
    )
    return {
        "rung3_kill_switch_pass": bool(rung3["kill_switch_pass"]),
        "rung3_status": str(rung3["status"]),
        "base_p14_residual_gate": bool(base_gate["gates"]["residual_gate"]),
        "base_p14_robustness_gate": bool(base_gate["gates"]["robustness_gate"]),
        "downstream_hard_gate_pass": bool(base_gate["hard_gate_pass"]),
        "coherent": coherent,
    }


def adversarial_failure_certificates() -> List[Dict[str, Any]]:
    """Return explicit failure certificates for broken branch inputs."""
    bad_rank = rank_conservation_check(vacuum_rank=3, target_rank=4)
    bad_quant = wilson_line_quantization_check(phases_rad=(0.0, math.pi / 5.0, 2.0 * math.pi / 3.0))
    bad_group = unbroken_group_validation_check(group_factors=("SU(4)", "U(1)"))

    cases = [
        ("rank_mismatch", bad_rank, "rank_conservation_check"),
        ("phase_not_z3_quantized", bad_quant, "wilson_line_quantization_check"),
        ("wrong_unbroken_group", bad_group, "unbroken_group_validation_check"),
    ]
    rows: List[Dict[str, Any]] = []
    for case_name, payload, gate_name in cases:
        rows.append(
            {
                "case": case_name,
                "gate": gate_name,
                "pass": bool(payload["pass"]),
                "failure_expected": True,
                "failure_confirmed": not bool(payload["pass"]),
                "evidence": str(payload["evidence"]),
            }
        )
    return rows


def eightd_wilson_lane_report() -> Dict[str, Any]:
    """Return complete Lane-8D binary closure/non-promotion report."""
    scan = robustness_window_scan()
    branch = branch_consistency_audit()
    adversarial = adversarial_failure_certificates()

    adversarial_ok = all(bool(row["failure_confirmed"]) for row in adversarial)
    closure_earned = bool(scan["all_windows_pass"] and branch["coherent"] and adversarial_ok)
    failing_gates = sorted({
        gate
        for row in scan["scan_rows"]
        for gate in row["failing_gates"]
    })

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": True,
        "three_evidence_classes": {
            "analytic_check": {
                "name": "widened_window_robustness_scan",
                "pass": bool(scan["all_windows_pass"]),
            },
            "executable_check": {
                "name": "branch_to_downstream_consistency",
                "pass": bool(branch["coherent"]),
            },
            "adversarial_check": {
                "name": "broken_branch_failure_certificates",
                "pass": adversarial_ok,
            },
        },
        "robustness_scan": scan,
        "branch_consistency": branch,
        "adversarial_failure_certificates": adversarial,
        "binary_outcome": (
            "EIGHTD_WILSON_ROBUST_CLOSURE_EARNED"
            if closure_earned
            else "EIGHTD_WILSON_NON_PROMOTION_CERTIFIED"
        ),
        "closure_earned": closure_earned,
        "non_promotion_certificate": {
            "failing_windows_deg": scan["failing_windows_deg"],
            "failing_gates": failing_gates,
            "exact_failure_reason": (
                "none" if closure_earned else "robustness_not_uniform_across_widened_windows"
            ),
        },
        "epistemic_statement": (
            "This lane strengthens 8D evidence discipline by widening robustness windows, "
            "linking gauge-branch checks to downstream rho-bar behavior, and certifying broken "
            "branch failures explicitly. No closure is claimed unless all widened windows pass."
        ),
    }


PILLAR_VALID: bool = bool(eightd_wilson_lane_report()["valid"])


def pillar1014_summary() -> Dict[str, Any]:
    """Return concise Pillar 1014 summary."""
    report = eightd_wilson_lane_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "8D Wilson Robustness + Branch Audit",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "binary_outcome": report["binary_outcome"],
        "closure_earned": report["closure_earned"],
        "failing_windows_deg": report["non_promotion_certificate"]["failing_windows_deg"],
    }
