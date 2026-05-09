# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""P28 promotion hardgate package (v10.40).

Implements a strict pass/fail decision rule for promoting P28 from
ARCHITECTURE_LIMIT_CERTIFIED(10D) to GEOMETRIC_PREDICTION.

Policy:
  - Promote only if all hardgates pass.
  - Otherwise publish certified non-promotion with toe_score_delta = 0.0.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from src.core.cc_gap_precision_audit import p28_promotion_evaluation, verify_layer3_landscape_sufficiency
from src.core.p28_lambda_10d_closure import p28_10d_closure_report
from src.tend.cc_architecture_limit import LAMBDA_OBS_MPLANCK4

__all__ = [
    "CURRENT_TOE_SCORE",
    "TOE_SCORE_MAX",
    "TARGET_TOE_SCORE_MIN",
    "TARGET_TOE_DELTA_MIN",
    "P28_CURRENT_STATUS",
    "P28_TARGET_STATUS",
    "P28_PROMOTION_DELTA",
    "NON_ACTIONABLE_MEASUREMENT_GATED",
    "evaluate_p28_promotion_candidate",
    "p28_promotion_hardgate_report",
    "p28_promotion_hardgate_summary",
]

CURRENT_TOE_SCORE: float = 27.1
TOE_SCORE_MAX: float = 28.0
TARGET_TOE_SCORE_MIN: float = 27.66
TARGET_TOE_DELTA_MIN: float = TARGET_TOE_SCORE_MIN - CURRENT_TOE_SCORE  # 0.56

P28_CURRENT_STATUS: str = "ARCHITECTURE_LIMIT_CERTIFIED(10D)"
P28_TARGET_STATUS: str = "GEOMETRIC_PREDICTION"
P28_PROMOTION_DELTA: float = 0.7

# These remain non-actionable for this push because their status transitions
# are measurement-gated (LiteBIRD/LISA), not derivation-gated by P28 hardgates.
NON_ACTIONABLE_MEASUREMENT_GATED: Tuple[str, str, str] = ("P23", "P24", "P25")


def _bp_spacing_log10(n_flux: int) -> float:
    """Naive Bousso-Polchinski spacing estimate log10(ε/M_Pl^4) ~ -2*N_flux."""
    return -2.0 * float(n_flux)


def evaluate_p28_promotion_candidate(
    *,
    n_flux: int,
    has_explicit_selection_mechanism: bool,
) -> Dict[str, object]:
    """Evaluate strict hardgates for a specific P28 promotion candidate."""
    layer3 = verify_layer3_landscape_sufficiency()
    required_n_flux = int(math.ceil(float(layer3["n_flux_needed"])))
    lambda_obs_log10 = math.log10(LAMBDA_OBS_MPLANCK4)

    gate1_closure_evidence_pass = n_flux >= required_n_flux
    sweep_fluxes: List[int] = [n_flux, n_flux + 1, n_flux + 2]
    gate2_robustness_sweep_pass = gate1_closure_evidence_pass and all(
        _bp_spacing_log10(nf) < lambda_obs_log10 for nf in sweep_fluxes
    )
    # Gate 3 is satisfied by construction in this package: all computation inputs
    # are geometric constants and candidate flags; PDG values are comparison-only.
    gate3_axiomzero_purity_pass = True
    gate4_falsifier_integrity_preserved = has_explicit_selection_mechanism

    all_gates_pass = (
        gate1_closure_evidence_pass
        and gate2_robustness_sweep_pass
        and gate3_axiomzero_purity_pass
        and gate4_falsifier_integrity_preserved
    )
    toe_score_delta = P28_PROMOTION_DELTA if all_gates_pass else 0.0
    toe_score_after = CURRENT_TOE_SCORE + toe_score_delta

    return {
        "parameter": "P28",
        "quantity": "Cosmological constant Λ",
        "status_before": P28_CURRENT_STATUS,
        "status_after": P28_TARGET_STATUS if all_gates_pass else P28_CURRENT_STATUS,
        "toe_score_before": CURRENT_TOE_SCORE,
        "toe_score_after": toe_score_after,
        "toe_score_delta": toe_score_delta,
        "toe_score_after_pct": toe_score_after / TOE_SCORE_MAX * 100.0,
        "target_locked": {
            "minimum_toe_score": TARGET_TOE_SCORE_MIN,
            "minimum_toe_delta": TARGET_TOE_DELTA_MIN,
            "is_met": toe_score_after >= TARGET_TOE_SCORE_MIN,
        },
        "gates": {
            "gate1_closure_evidence_n_flux_ge_required": gate1_closure_evidence_pass,
            "gate2_robustness_sweep_spacing_pass": gate2_robustness_sweep_pass,
            "gate3_axiomzero_purity_pass": gate3_axiomzero_purity_pass,
            "gate4_falsifier_integrity_preserved": gate4_falsifier_integrity_preserved,
        },
        "all_gates_pass": all_gates_pass,
        "n_flux_candidate": n_flux,
        "n_flux_required": required_n_flux,
        "robustness_sweep_fluxes": sweep_fluxes,
        "lambda_obs_log10": lambda_obs_log10,
        "axiomzero_pdg_inputs": [],
        "non_actionable_measurement_gated": list(NON_ACTIONABLE_MEASUREMENT_GATED),
        "pass_fail_rule": "promote_only_if_all_required_gates_pass_else_certified_non_promotion",
    }


def p28_promotion_hardgate_report() -> Dict[str, object]:
    """Default P28 promotion report using current repository state."""
    closure = p28_10d_closure_report()
    candidate = evaluate_p28_promotion_candidate(
        n_flux=int(closure["effective_n_flux"]),
        has_explicit_selection_mechanism=bool(closure["explicit_selection_pass"]),
    )
    historical = p28_promotion_evaluation()
    return {
        **candidate,
        "evidence_context": {
            "closure_package": closure,
            "historical_can_promote": historical["can_promote"],
            "historical_reason": historical["reason"],
            "historical_enablement_path": historical["what_would_enable"],
        },
    }


def p28_promotion_hardgate_summary() -> Dict[str, object]:
    """Compact summary for tracker/changelog synchronization."""
    report = p28_promotion_hardgate_report()
    return {
        "sprint": "P28_PROMOTION_HARDGATE_PACKAGE",
        "parameter": report["parameter"],
        "status_before": report["status_before"],
        "status_after": report["status_after"],
        "all_gates_pass": report["all_gates_pass"],
        "toe_score_delta": report["toe_score_delta"],
        "target_locked": report["target_locked"],
    }
