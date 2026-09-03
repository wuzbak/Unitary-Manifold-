# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 999 — CMB amplitude calibration/prediction boundary audit.

🔵 ADJACENT TRACK — Non-hardgate.

The slow-roll normalization equation can always choose ``lambda_COBE`` so
that its output equals an input ``A_s`` target.  That algebraic identity must
not be reported as a predicted CMB amplitude.  This pillar makes the boundary
executable and links it to the terminal EFT evidence: KK modes,
brane-backreaction, rolling-radion, and the WZ cross-check do not supply the
missing normalization.

The result is an integrity advance, not a physical closure.  A future UV
candidate can only upgrade this lane by fixing the normalization without an
observational amplitude input and by supplying the missing global UV transfer
data identified in the architecture-limit registry.
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.cmb_amplitude import PLANCK_AS, cobe_normalization_check
from src.core.pillar915_cmb_amp_13d_radion import cmb_amp_13d
from src.core.pillar928_cmb_amp_kk_tower_nlo import cmb_kk_tower_n1
from src.core.pillar935_cmb_peak_brane_backreaction import cmb_brane_backreaction
from src.core.pillar945_cmb_amp_wz_crosscheck import cmb_wz_crosscheck_summary
from src.core.pillar983_residual_budget_pipeline import residual_budget_pipeline

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CMB_AMPLITUDE_TARGET",
    "REQUIRED_RECOVERY_FACTOR",
    "calibration_prediction_boundary",
    "cmb_amplitude_evidence_ledger",
    "pillar998_summary",
]

PILLAR_NUMBER: int = 999
PILLAR_GATE: str = "CMB_AMPLITUDE_CALIBRATION_PREDICTION_BOUNDARY"
PILLAR_STATUS: str = "CMB_AMP_CALIBRATION_BOUNDARY_COMPLETE"
CMB_AMPLITUDE_TARGET: float = PLANCK_AS
REQUIRED_RECOVERY_FACTOR: tuple[float, float] = (4.0, 7.0)


def calibration_prediction_boundary(
    as_target: float = CMB_AMPLITUDE_TARGET,
) -> Dict[str, Any]:
    """Separate an exact target calibration from an independent prediction."""
    if as_target <= 0.0:
        raise ValueError(f"as_target must be positive, got {as_target}")

    calibration = cobe_normalization_check(As_target=as_target)
    doubled_target = cobe_normalization_check(As_target=2.0 * as_target)
    lambda_scaling = doubled_target["lam_cobe"] / calibration["lam_cobe"]
    calibrated_not_predicted = (
        calibration["normalization_is_calibrated"]
        and not calibration["normalization_predicted"]
        and calibration["calibration_parameter_count"] == 1
        and calibration["calibration_input"] == "As_target (external observational datum)"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "as_target": as_target,
        "calibration": calibration,
        "calibration_parameter_count": calibration["calibration_parameter_count"],
        "external_target_used": True,
        "target_doubling_lambda_ratio": lambda_scaling,
        "lambda_scales_with_target": abs(lambda_scaling - 2.0) < 1e-12,
        "pivot_amplitude_calibrated": calibration["normalization_is_calibrated"],
        "pivot_amplitude_predicted": calibration["normalization_predicted"],
        "calibrated_not_predicted": calibrated_not_predicted,
        "closure_claimed": False,
        "upgrade_criterion": (
            "Derive the normalization and transfer response without an observational "
            "A_s target or a fitted equivalent, then test it across acoustic multipoles."
        ),
    }


def cmb_amplitude_evidence_ledger() -> Dict[str, Any]:
    """Return terminal-EFT evidence and the named missing UV objects."""
    kk = cmb_kk_tower_n1()
    brane = cmb_brane_backreaction()
    radion = cmb_amp_13d()
    wz = cmb_wz_crosscheck_summary()
    budget = residual_budget_pipeline()
    cmb_budget = next(row for row in budget["rows"] if row["lane"] == "CMB_AMP")

    mechanisms: List[Dict[str, Any]] = [
        {"mechanism": "KK tower n=1", "status": kk["status"], "terminal": kk["architecture_limit_unchanged"]},
        {"mechanism": "brane backreaction", "status": brane["status"], "terminal": brane["architecture_limit_confirmed"]},
        {"mechanism": "rolling radion", "status": radion["status"], "terminal": radion["status"].endswith("ARCHITECTURE_LIMIT")},
        {"mechanism": "WZ cross-check", "status": wz["status"], "terminal": "ARCHITECTURE_LIMIT_CONFIRMED" in wz["status"]},
    ]
    terminal_eft_routes = all(row["terminal"] for row in mechanisms)

    return {
        "mechanisms": mechanisms,
        "terminal_eft_routes": terminal_eft_routes,
        "recovery_factor_required": REQUIRED_RECOVERY_FACTOR,
        "residual_budget": cmb_budget,
        "named_missing_objects": [
            "nonperturbative amplitude-generation mechanism",
            "global UV completion of transfer normalization",
        ],
        "status": "CONFIRMED_IRREDUCIBLE" if terminal_eft_routes else "EFT_REVIEW_REQUIRED",
    }


def pillar999_summary() -> Dict[str, Any]:
    """Return the calibration boundary and terminal-EFT evidence together."""
    boundary = calibration_prediction_boundary()
    ledger = cmb_amplitude_evidence_ledger()
    valid = (
        boundary["calibrated_not_predicted"]
        and boundary["lambda_scales_with_target"]
        and ledger["terminal_eft_routes"]
        and ledger["residual_budget"]["normalized"]
        and ledger["residual_budget"]["has_registry_row"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "title": "CMB Amplitude Calibration/Prediction Boundary Audit",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "calibration_boundary": boundary,
        "evidence_ledger": ledger,
        "honest_verdict": (
            "The pivot normalization is an external-data calibration, not an A_s "
            "prediction; terminal EFT routes do not close the ×4–7 acoustic deficit."
        ),
    }


PILLAR_VALID: bool = pillar998_summary()["valid"]
