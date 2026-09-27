# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Z₂-odd differential coupling audit for scalar/tensor power suppression.

This module tests (does not assume) whether odd-parity B_μ corrections can
explain two architecture tensions with one geometric mechanism.
"""

from __future__ import annotations

from typing import Dict

N_W: int = 5
N_SHADOW: int = 7
K_CS: int = 74
R_FRAMEWORK: float = 0.0315
ACT_DR6_R_UPPER: float = 0.016

# Canonical mismatch marker from framework ledgers for AL-1
AL1_MISMATCH_REFERENCE: float = 0.336  # 33.6%


def z2_odd_scalar_suppression() -> Dict[str, float]:
    """Scalar suppression from odd-sector correction."""
    odd_fraction = (N_W**2) / K_CS          # 25/74
    observed_fraction = 1.0 - odd_fraction  # 49/74
    return {
        "odd_fraction_removed": odd_fraction,
        "observed_fraction_remaining": observed_fraction,
    }


def z2_odd_tensor_suppression() -> Dict[str, float]:
    """Tensor suppression from odd-sector shadow coupling."""
    odd_fraction = (N_SHADOW**2) / K_CS      # 49/74
    observed_fraction = 1.0 - odd_fraction   # 25/74
    return {
        "odd_fraction_removed": odd_fraction,
        "observed_fraction_remaining": observed_fraction,
    }


def corrected_tensor_to_scalar_ratio(r_framework: float = R_FRAMEWORK) -> Dict[str, float]:
    """Compute differential corrected r = r × (25/49)."""
    ratio = (N_W**2) / (N_SHADOW**2)  # 25/49
    r_corrected = r_framework * ratio
    return {"r_framework": r_framework, "ratio_25_over_49": ratio, "r_corrected": r_corrected}


def al1_al2_delta_report() -> Dict[str, object]:
    """Quantify AL-1/AL-2 impact and falsification checks."""
    scalar = z2_odd_scalar_suppression()
    tensor = z2_odd_tensor_suppression()
    rc = corrected_tensor_to_scalar_ratio()

    scalar_removed = scalar["odd_fraction_removed"]
    scalar_error = abs(scalar_removed - AL1_MISMATCH_REFERENCE)
    scalar_within_1pct = scalar_error <= 0.01

    r_corrected = rc["r_corrected"]
    r_distance = abs(r_corrected - ACT_DR6_R_UPPER)
    r_approaches_bound = r_distance <= 5e-4

    status = "FITTED" if (scalar_within_1pct and r_approaches_bound) else "OPEN_GAP"

    return {
        "scalar": scalar,
        "tensor": tensor,
        "r_correction": rc,
        "al1_check": {
            "target_mismatch": AL1_MISMATCH_REFERENCE,
            "predicted_removed_fraction": scalar_removed,
            "abs_error": scalar_error,
            "within_1pct": scalar_within_1pct,
        },
        "al2_check": {
            "target_r_upper": ACT_DR6_R_UPPER,
            "predicted_r_corrected": r_corrected,
            "abs_distance_to_bound": r_distance,
            "approaches_bound": r_approaches_bound,
        },
        "status": status,
        "epistemic_label": (
            "FITTED: numerical consistency with two observables; coupling coefficients "
            "are not yet derived from 5D action-level reduction."
            if status == "FITTED"
            else "OPEN_GAP: one or more falsification checks fail."
        ),
    }

