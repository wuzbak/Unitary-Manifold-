# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Decision-grade execution report for the F-LAB-CP-1..4 protocol.

Operationalizes the dual-track (Track A: JJ/SQUID, Track B: topological insulator)
lab CP-asymmetry campaign.  All verdicts reference `evaluate_lab_cp_campaign` from
the canonical `lab_litebird_substitute` module; this module adds execution-layer
wrapping, gap analysis, and progress tracking.
"""
from __future__ import annotations

from src.core.lab_litebird_substitute import (
    LAB_TRACKS,
    SIGMA_TARGET as _SIGMA_TARGET_BASE,
    LabCPCampaignInput,
    evaluate_lab_cp_campaign,
    lab_protocol_checklist,
)

__all__ = [
    "SIGMA_TARGET",
    "N_REPLICATIONS_REQUIRED",
    "TOPOLOGY_CERTIFICATION_CONFIDENCE",
    "SYSTEMATIC_SUPPRESSION_REQUIRED",
    "CURRENT_SIGMA_A_ESTIMATE",
    "baseline_execution_report",
    "execute_campaign_verdict",
    "decision_grade_threshold_check",
    "track_progress_report",
    "full_execution_report",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

SIGMA_TARGET: float = 1.0e-5
N_REPLICATIONS_REQUIRED: int = 3
TOPOLOGY_CERTIFICATION_CONFIDENCE: float = 0.95
SYSTEMATIC_SUPPRESSION_REQUIRED: float = 10.0  # factor over current noise floor

# Best published JJ/SQUID sensitivity — current experimental state (NOT the target)
CURRENT_SIGMA_A_ESTIMATE: float = 1.0e-4

# Derived summary constants
_GAP_FACTOR: float = CURRENT_SIGMA_A_ESTIMATE / SIGMA_TARGET  # 10.0×
_TIMELINE_YEARS: int = 2  # representative estimate to close sensitivity gap


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def baseline_execution_report() -> dict[str, object]:
    """Return a machine-readable summary of the *current* F-LAB-CP campaign status.

    Reflects the state of the art as of publication — NOT the target.  The target
    σ_A ≤ 1 × 10⁻⁵ has not yet been achieved; the gap is clearly stated.
    """
    return {
        "lane_id": "F14/P8",
        "execution_status": "PROTOCOL_READY_AWAITING_DATA",
        "sigma_target": SIGMA_TARGET,
        "n_replications_required": N_REPLICATIONS_REQUIRED,
        "topology_certification_confidence": TOPOLOGY_CERTIFICATION_CONFIDENCE,
        "systematic_suppression_required": SYSTEMATIC_SUPPRESSION_REQUIRED,
        "tracks": {
            "A": {
                "track_id": "A",
                "platform": LAB_TRACKS["A"]["platform"],
                "current_sigma_estimate": CURRENT_SIGMA_A_ESTIMATE,
                "gap_to_target_factor": _GAP_FACTOR,
                "status": "PRE_DECISION_GRADE",
            },
            "B": {
                "track_id": "B",
                "platform": LAB_TRACKS["B"]["platform"],
                "current_sigma_estimate": None,
                "gap_to_target_factor": None,
                "status": "PLATFORM_DEVELOPMENT",
            },
        },
        "current_sigma_a_estimate": CURRENT_SIGMA_A_ESTIMATE,
        "gap_to_target_factor": _GAP_FACTOR,
        "timeline_estimate_years": _TIMELINE_YEARS,
        "protocol_checklist": lab_protocol_checklist(),
    }


def execute_campaign_verdict(
    a_cp_lab: float,
    sigma_a: float,
    n_replications: int,
    topology_certified: bool,
    systematics_passed: bool,
) -> dict[str, object]:
    """Wrap `evaluate_lab_cp_campaign` with richer execution-layer output.

    Parameters
    ----------
    a_cp_lab:
        Measured CP asymmetry (dimensionless).
    sigma_a:
        Total uncertainty on a_cp_lab (must be > 0).
    n_replications:
        Number of independent replications completed.
    topology_certified:
        Whether (5,7) topology certification has been independently verified.
    systematics_passed:
        Whether the systematics decomposition and control criteria are satisfied.

    Returns
    -------
    dict containing:
        verdict, sigma_significance, signal_significant_2sigma,
        action_required, and the full underlying campaign evaluation.
    """
    inputs = LabCPCampaignInput(
        a_cp_lab=a_cp_lab,
        sigma_a=sigma_a,
        topology_certified=topology_certified,
        independent_replications=n_replications,
        systematics_controls_passed=systematics_passed,
        # Conservative defaults for the richer wrapper: these flags are not
        # routinely available without a full blinded-analysis packet.
        topology_independent_asymmetry=False,
        sign_reversal_inverts_cp_odd=True,
        cp_even_baseline_stable=True,
        signal_explained_by_systematics=False,
    )
    base = evaluate_lab_cp_campaign(inputs)

    sigma_significance = abs(a_cp_lab) / sigma_a
    signal_significant_2sigma = sigma_significance > 2.0

    action_required: list[str] = []
    verdict = base["verdict"]
    if verdict == "INCONCLUSIVE":
        if not topology_certified:
            action_required.append("Obtain independent (5,7) topology certification.")
        if not base["decision_grade"]:
            action_required.append(
                f"Improve sensitivity: need σ_A ≤ {SIGMA_TARGET:.1e} "
                f"(current gap ×{sigma_a / SIGMA_TARGET:.1f})."
            )
        if n_replications < N_REPLICATIONS_REQUIRED:
            action_required.append(
                f"Complete {N_REPLICATIONS_REQUIRED - n_replications} more "
                f"independent replication(s) (have {n_replications}, need {N_REPLICATIONS_REQUIRED})."
            )
        if not systematics_passed:
            action_required.append("Pass full systematics decomposition controls.")
        if not action_required:
            action_required.append(
                "Decision-grade sensitivity reached; increase statistics to resolve signal."
            )
    elif verdict == "SUPPORTED":
        action_required.append(
            "Submit for peer review and request independent Track-B replication."
        )
    elif verdict == "FALSIFIED":
        action_required.append(
            "Declare falsification event; notify governance board immediately."
        )

    return {
        "verdict": verdict,
        "sigma_significance": sigma_significance,
        "signal_significant_2sigma": signal_significant_2sigma,
        "decision_grade": base["decision_grade"],
        "triggered_conditions": base["triggered_conditions"],
        "reason": base["reason"],
        "action_required": action_required,
        "inputs_summary": {
            "a_cp_lab": a_cp_lab,
            "sigma_a": sigma_a,
            "n_replications": n_replications,
            "topology_certified": topology_certified,
            "systematics_passed": systematics_passed,
        },
    }


def decision_grade_threshold_check(sigma_a: float) -> bool:
    """Return True when *sigma_a* meets the decision-grade sensitivity threshold.

    Decision-grade is defined as σ_A ≤ 1 × 10⁻⁵.
    """
    return sigma_a <= SIGMA_TARGET


def track_progress_report(track_id: str, current_sigma: float) -> dict[str, object]:
    """Return a progress-toward-target summary for a single lab track.

    Parameters
    ----------
    track_id:
        "A" (JJ/SQUID) or "B" (topological insulator).
    current_sigma:
        Latest measured sensitivity for this track (must be > 0).

    Returns
    -------
    dict with progress fraction, gap factor, and status label.
    """
    if track_id not in LAB_TRACKS:
        raise ValueError(
            f"Unknown track_id {track_id!r}; expected one of {sorted(LAB_TRACKS)}."
        )
    if current_sigma <= 0.0:
        raise ValueError("current_sigma must be positive.")

    gap_factor = current_sigma / SIGMA_TARGET
    decision_grade = decision_grade_threshold_check(current_sigma)
    # Progress fraction: 1.0 when gap_factor = 1 (at target); 0.0 if infinitely away.
    # Use logarithmic scale relative to starting point.
    import math
    if CURRENT_SIGMA_A_ESTIMATE > SIGMA_TARGET:
        log_range = math.log10(CURRENT_SIGMA_A_ESTIMATE / SIGMA_TARGET)
        log_gap = math.log10(max(current_sigma, SIGMA_TARGET) / SIGMA_TARGET)
        progress_fraction = max(0.0, min(1.0, 1.0 - log_gap / log_range))
    else:
        progress_fraction = 1.0

    return {
        "track_id": track_id,
        "platform": LAB_TRACKS[track_id]["platform"],
        "current_sigma": current_sigma,
        "sigma_target": SIGMA_TARGET,
        "gap_factor": gap_factor,
        "decision_grade": decision_grade,
        "progress_fraction": progress_fraction,
        "status": "DECISION_GRADE" if decision_grade else "PRE_DECISION_GRADE",
    }


def full_execution_report() -> dict[str, object]:
    """Return the combined execution report for both tracks plus threshold status.

    Combines `baseline_execution_report()` with per-track progress reports and
    a decision-grade threshold summary.
    """
    baseline = baseline_execution_report()
    track_a = track_progress_report("A", CURRENT_SIGMA_A_ESTIMATE)
    track_b_sigma = SIGMA_TARGET * 5.0  # illustrative Track B placeholder (5× target)
    track_b = track_progress_report("B", track_b_sigma)
    threshold_met = decision_grade_threshold_check(CURRENT_SIGMA_A_ESTIMATE)

    return {
        "baseline": baseline,
        "track_progress": {
            "A": track_a,
            "B": track_b,
        },
        "decision_grade_threshold_met": threshold_met,
        "overall_execution_status": baseline["execution_status"],
    }
