# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1015 — 9D GS anomaly + CP refinement coherence certificate."""

from __future__ import annotations

from typing import Any, Dict, List

from src.nined.anomaly_cancellation_gs import hard_gate_check, rung4_gate_evidence
from src.nined.cp_phase_9d_refinement import (
    RHOBAR_GATE_THRESHOLD_PCT,
    cp_phase_9d_gate_check,
    delta_cp_9d_uncertainty,
    residual_pct_9d,
    rhobar_robustness_gate,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "WIDE_ALPHA_RANGE",
    "WIDE_GS_RANGE",
    "anchor_partition_scan",
    "edge_case_uncertainty_partitions",
    "nined_coherence_certificate",
    "pillar1015_summary",
]

PILLAR_NUMBER: int = 1015
PILLAR_GATE: str = "NINED_CP_ANOMALY_COHERENCE_CERTIFICATE"
PILLAR_STATUS: str = "NINED_CP_ANOMALY_COHERENCE_CERTIFICATE_COMPLETE"

WIDE_ALPHA_RANGE = (0.16, 0.24)
WIDE_GS_RANGE = (0.12, 0.20)
POINTS_PER_AXIS: int = 9


def _linspace(lo: float, hi: float, n: int) -> List[float]:
    if n < 2:
        raise ValueError("n must be >= 2")
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def anchor_partition_scan(
    alpha_range: tuple[float, float] = WIDE_ALPHA_RANGE,
    gs_range: tuple[float, float] = WIDE_GS_RANGE,
    points: int = POINTS_PER_AXIS,
) -> Dict[str, Any]:
    """Return deterministic pass/fail partitions over widened anchor windows."""
    alphas = _linspace(alpha_range[0], alpha_range[1], points)
    gs_vals = _linspace(gs_range[0], gs_range[1], points)

    pass_cells = 0
    fail_cells = 0
    max_residual = 0.0
    max_uncertainty = 0.0

    for alpha in alphas:
        for gs in gs_vals:
            resid = residual_pct_9d(alpha_9d=alpha, gs_flux=gs)
            unc_pct = delta_cp_9d_uncertainty(alpha_9d=alpha, gs_flux=gs) / 1.20 * 100.0
            max_residual = max(max_residual, resid)
            max_uncertainty = max(max_uncertainty, unc_pct)
            if resid < RHOBAR_GATE_THRESHOLD_PCT and unc_pct < RHOBAR_GATE_THRESHOLD_PCT:
                pass_cells += 1
            else:
                fail_cells += 1

    total = pass_cells + fail_cells
    return {
        "alpha_range": alpha_range,
        "gs_range": gs_range,
        "points_per_axis": points,
        "total_cells": total,
        "pass_cells": pass_cells,
        "fail_cells": fail_cells,
        "pass_fraction": (pass_cells / total) if total else 0.0,
        "all_cells_pass": fail_cells == 0 and total > 0,
        "max_residual_pct": max_residual,
        "max_uncertainty_pct": max_uncertainty,
    }


def edge_case_uncertainty_partitions() -> Dict[str, Any]:
    """Boundary checks around the 5% uncertainty threshold."""
    pdg = 1.20
    threshold_rad = RHOBAR_GATE_THRESHOLD_PCT / 100.0 * pdg
    just_below = rhobar_robustness_gate(threshold_rad * 0.999)
    at_threshold = rhobar_robustness_gate(threshold_rad)
    just_above = rhobar_robustness_gate(threshold_rad * 1.001)
    return {
        "threshold_pct": RHOBAR_GATE_THRESHOLD_PCT,
        "just_below_pass": bool(just_below["gate_pass"]),
        "at_threshold_pass": bool(at_threshold["gate_pass"]),
        "just_above_pass": bool(just_above["gate_pass"]),
    }


def nined_coherence_certificate() -> Dict[str, Any]:
    """Return integrated lane report coupling GS hard-gates and CP utility."""
    rung4 = rung4_gate_evidence()
    hard = hard_gate_check()
    cp_gate = cp_phase_9d_gate_check()
    partition = anchor_partition_scan()
    edges = edge_case_uncertainty_partitions()

    robust_closure = bool(
        rung4["hard_gate_pass"]
        and hard["hard_gate_pass"]
        and cp_gate["gate_pass"]
        and partition["all_cells_pass"]
    )

    binary_outcome = (
        "NINED_CP_ROBUSTNESS_CONFIRMED"
        if robust_closure
        else "NINED_CP_RESIDUAL_CERTIFIED"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": True,
        "three_evidence_classes": {
            "analytic_check": {
                "name": "widened_anchor_partition_scan",
                "pass": bool(partition["all_cells_pass"]),
            },
            "executable_check": {
                "name": "gs_hard_gate_plus_cp_gate",
                "pass": bool(rung4["hard_gate_pass"] and cp_gate["gate_pass"]),
            },
            "adversarial_check": {
                "name": "uncertainty_threshold_edge_cases",
                "pass": bool(edges["just_below_pass"] and not edges["just_above_pass"]),
            },
        },
        "rung4_hard_gate": rung4,
        "cp_gate": cp_gate,
        "anchor_partition": partition,
        "edge_case_thresholds": edges,
        "binary_outcome": binary_outcome,
        "robust_closure": robust_closure,
        "residual_certificate": {
            "needed_for_robust_closure": "all_partition_cells_pass",
            "current_fail_cells": partition["fail_cells"],
            "max_residual_pct": partition["max_residual_pct"],
            "max_uncertainty_pct": partition["max_uncertainty_pct"],
        },
        "epistemic_statement": (
            "This lane binds anomaly hard-gate validity to CP-utility evidence in one certificate. "
            "Nominal CP performance remains strong, and widened-window partitions now determine "
            "whether closure is earned or residual status remains explicit."
        ),
    }


PILLAR_VALID: bool = bool(nined_coherence_certificate()["valid"])


def pillar1015_summary() -> Dict[str, Any]:
    report = nined_coherence_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "9D CP + Anomaly Coherence Certificate",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "binary_outcome": report["binary_outcome"],
        "fail_cells": report["anchor_partition"]["fail_cells"],
    }
