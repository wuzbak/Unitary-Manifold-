# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/litebird_proof_alternative.py
========================================
Pillar 45-E -- LiteBIRD Proof-Alternative Lab Campaign Engine.

The LiteBIRD satellite launches ~2032 and publishes birefringence results
~2034.  This module operationalises the complete set of laboratory-accessible
falsification and proof-alternative lanes available *now*, before that date.

Background
----------
The Unitary Manifold predicts a CMB birefringence angle

    beta in {0.273 deg, 0.290 deg, 0.331 deg, 0.351 deg}

with a forbidden gap at (0.29 deg, 0.31 deg) and admissible window
[0.22 deg, 0.38 deg].  Because LiteBIRD is 8 years away, three
complementary proof-alternative lanes are defined here:

Lane A -- CP-Asymmetry Table-Top (F14/P8)
    Topology-certified (5,7) braid photonic/atomic platforms measure
    a CP-violation asymmetry A_CP^lab.  The UM predicts a nonzero
    A_CP^lab proportional to sin(2 * pi * 5/74).  Decision-grade
    sensitivity requires sigma_A < 1e-5.

Lane B -- Polarisation Rotation in Analogue Braid Systems
    Microwave-photonic or cold-atom waveguide experiments that can
    emulate the 5D (5,7) braid geometry measure a rotation angle
    phi_rot = phi_0 * c_s / pi, where phi_0 is derived from the UM
    constants.  If phi_rot falls in the predicted gap interval
    [phi_gap_lower, phi_gap_upper] the framework is falsified at lab scale.

Lane C -- B-Mode Polarisation Analogue
    Cryogenic CMB-testbed cameras (CLASS, SPIDER ground deployments, etc.)
    measuring effective B-mode rotation on known calibration sources.
    The predicted rotation is beta_lab ~ beta_CMB / alpha_scale, where
    alpha_scale is the lab-to-cosmological frequency ratio.

For each lane this module provides:
  * Predicted signal
  * Decision thresholds (pass / fail / inconclusive)
  * Uncertainty budget
  * Evidence strength metric
  * Scoring contribution to the ToE score (if decision-grade positive)
  * Composite verdict aggregating all three lanes

Public API
----------
Predicted signals::
    A_CP_PREDICTED       -- Lane A CP asymmetry (dimensionless)
    PHI_ROT_PREDICTED    -- Lane B rotation angle (degrees)
    BETA_LAB_PREDICTED   -- Lane C effective B-mode rotation (degrees)

Decision thresholds::
    SIGMA_A_THRESHOLD    -- Lane A decision-grade sensitivity
    PHI_ROT_GAP_LOWER    -- Lane B gap lower bound (degrees)
    PHI_ROT_GAP_UPPER    -- Lane B gap upper bound (degrees)
    BETA_LAB_WINDOW_LOW  -- Lane C admissible window lower bound
    BETA_LAB_WINDOW_HIGH -- Lane C admissible window upper bound

Functions::
    lane_a_cp_asymmetry_verdict(a_cp, sigma_a, replications, controls_passed)
    lane_b_rotation_verdict(phi_rot, sigma_phi, replication_count)
    lane_c_bmode_verdict(beta_lab, sigma_beta, calibration_confirmed)
    composite_proof_alternative(lane_a_in, lane_b_in, lane_c_in)
    proof_alternative_status_snapshot()
    evidence_strength_score(lane_a_result, lane_b_result, lane_c_result)

"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "C_S",
    "A_CP_PREDICTED",
    "PHI_ROT_PRIMARY",
    "PHI_ROT_SHADOW",
    "PHI_ROT_PREDICTED",
    "BETA_LAB_PREDICTED",
    "SIGMA_A_THRESHOLD",
    "PHI_ROT_GAP_LOWER",
    "PHI_ROT_GAP_UPPER",
    "BETA_LAB_WINDOW_LOW",
    "BETA_LAB_WINDOW_HIGH",
    "PHI_ROT_WINDOW_LOW",
    "PHI_ROT_WINDOW_HIGH",
    "LANE_A_TOE_CONTRIBUTION",
    "LANE_B_TOE_CONTRIBUTION",
    "LANE_C_TOE_CONTRIBUTION",
    # Dataclasses
    "LaneAInput",
    "LaneBInput",
    "LaneCInput",
    # Functions
    "lane_a_cp_asymmetry_verdict",
    "lane_b_rotation_verdict",
    "lane_c_bmode_verdict",
    "composite_proof_alternative",
    "proof_alternative_status_snapshot",
    "evidence_strength_score",
    "uncertainty_budget_lane_a",
    "uncertainty_budget_lane_b",
    "uncertainty_budget_lane_c",
]

# ---------------------------------------------------------------------------
# UM physical constants
# ---------------------------------------------------------------------------

#: Winding number (selected by Planck n_s = 0.9649)
N_W: int = 5

#: Chern-Simons charge = n_w^2 + n_2^2 = 5^2 + 7^2
K_CS: int = 74

#: Braided sound speed c_s = (n_2^2 - n_1^2) / (n_1^2 + n_2^2) = (49 - 25) / 74
C_S: float = 24.0 / 74.0

#: phi_0 from 5D geometry: phi_0 = sqrt(8 * N_W / (1 - n_s)) with n_s = 0.9635
_N_S: float = 0.9635
PHI_0: float = math.sqrt(8.0 * N_W / (1.0 - _N_S))

# ---------------------------------------------------------------------------
# Lane A -- CP-Asymmetry predictions
# ---------------------------------------------------------------------------

#: Predicted CP asymmetry A_CP^lab = sin(2 * pi * N_W / K_CS)
#: This is the topology-locked signal from the (5,7) braid sector
A_CP_PREDICTED: float = math.sin(2.0 * math.pi * N_W / K_CS)

#: Decision-grade sensitivity for Lane A (1 sigma)
SIGMA_A_THRESHOLD: float = 1.0e-5

#: Minimum independent replications for decision-grade verdict
LANE_A_MIN_REPLICATIONS: int = 2

#: ToE score contribution if Lane A supports at decision-grade (pts)
LANE_A_TOE_CONTRIBUTION: float = 0.4

# ---------------------------------------------------------------------------
# Lane B -- Polarisation rotation in analogue braid systems
# ---------------------------------------------------------------------------

#: (5,7) primary sector rotation
PHI_ROT_PRIMARY: float = (PHI_0 * (24.0 / 74.0) / math.pi) % 360.0

#: (5,6) shadow sector rotation: c_s_56 = (36-25)/61 = 11/61
PHI_ROT_SHADOW: float = (PHI_0 * (11.0 / 61.0) / math.pi) % 360.0

#: Main predicted value is the primary (5,7) sector
PHI_ROT_PREDICTED: float = PHI_ROT_PRIMARY

#: The forbidden gap is BETWEEN the two sector predictions
_PHI_GAP_CENTRE: float = (PHI_ROT_PRIMARY + PHI_ROT_SHADOW) / 2.0
_GAP_HALF_WIDTH_DEG: float = min(0.2, abs(PHI_ROT_PRIMARY - PHI_ROT_SHADOW) * 0.2)
PHI_ROT_GAP_LOWER: float = _PHI_GAP_CENTRE - _GAP_HALF_WIDTH_DEG
PHI_ROT_GAP_UPPER: float = _PHI_GAP_CENTRE + _GAP_HALF_WIDTH_DEG

#: Admissible window spans both sector predictions with 3-sigma margin
_PHI_SIGMA_THEORY: float = 0.2  # degrees theoretical uncertainty
PHI_ROT_WINDOW_LOW: float = min(PHI_ROT_PRIMARY, PHI_ROT_SHADOW) - 5.0 * _PHI_SIGMA_THEORY
PHI_ROT_WINDOW_HIGH: float = max(PHI_ROT_PRIMARY, PHI_ROT_SHADOW) + 5.0 * _PHI_SIGMA_THEORY

#: ToE score contribution if Lane B confirms at decision grade (pts)
LANE_B_TOE_CONTRIBUTION: float = 0.3

# ---------------------------------------------------------------------------
# Lane C -- B-mode polarisation analogue (cryogenic testbeds)
# ---------------------------------------------------------------------------

#: Scale factor from cosmological to lab frequency (GHz ratio)
_ALPHA_SCALE: float = 1.0e-9  # cosmological / lab frequency ratio

#: Predicted effective lab B-mode rotation (degrees)
#: beta_lab = beta_CMB / alpha_scale, but clamped to testbed-accessible range
#: For calibration-source campaigns: effective predicted rotation delta
BETA_CMB_PRIMARY: float = 0.273  # degrees, primary UM prediction
BETA_LAB_PREDICTED: float = BETA_CMB_PRIMARY  # for lab campaigns at matched cal source

#: Admissible window for Lane C (same physics, same bounds)
BETA_LAB_WINDOW_LOW: float = 0.22   # degrees
BETA_LAB_WINDOW_HIGH: float = 0.38  # degrees

#: Forbidden gap (same as CMB)
BETA_LAB_GAP_LOWER: float = 0.29   # degrees
BETA_LAB_GAP_UPPER: float = 0.31   # degrees

#: ToE score contribution if Lane C confirms at decision grade (pts)
LANE_C_TOE_CONTRIBUTION: float = 0.3


# ---------------------------------------------------------------------------
# Input dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LaneAInput:
    """Input bundle for a Lane A CP-asymmetry campaign."""
    a_cp_measured: float
    sigma_a: float
    replications: int
    systematics_controls_passed: bool
    topology_certified: bool


@dataclass(frozen=True)
class LaneBInput:
    """Input bundle for a Lane B analogue rotation campaign."""
    phi_rot_measured: float
    sigma_phi: float
    replication_count: int
    calibration_confirmed: bool


@dataclass(frozen=True)
class LaneCInput:
    """Input bundle for a Lane C cryogenic B-mode campaign."""
    beta_lab_measured: float
    sigma_beta: float
    calibration_confirmed: bool
    foreground_subtracted: bool


# ---------------------------------------------------------------------------
# Lane A verdict
# ---------------------------------------------------------------------------

def lane_a_cp_asymmetry_verdict(
    inp: LaneAInput,
) -> dict:
    """Apply the Lane A CP-asymmetry decision logic.

    Verdict ladder:
      INCONCLUSIVE   -- topology not certified OR sensitivity not decision-grade
      FALSIFIED      -- zero-consistent at 95 CL with decision-grade sensitivity
      SUPPORTED      -- nonzero at >=3 sigma with topology lock and controls
      CONSISTENT     -- decision-grade, non-zero, but <3 sigma

    Parameters
    ----------
    inp : LaneAInput

    Returns
    -------
    dict with keys:
        verdict, falsified, supported, evidence_strength_sigma,
        a_cp_predicted, sigma_a_threshold, decision_grade, reason,
        toe_score_contribution
    """
    if inp.sigma_a <= 0.0:
        raise ValueError(f"sigma_a must be positive, got {inp.sigma_a}")

    if not inp.topology_certified:
        return _lane_a_inconclusive("Topology not independently certified as (5,7).", inp)

    if inp.sigma_a > SIGMA_A_THRESHOLD:
        return _lane_a_inconclusive(
            f"sigma_a = {inp.sigma_a:.2e} > threshold {SIGMA_A_THRESHOLD:.1e};"
            " sensitivity not decision-grade.",
            inp,
        )

    if not inp.systematics_controls_passed:
        return _lane_a_inconclusive("Systematics controls not passed.", inp)

    if inp.replications < LANE_A_MIN_REPLICATIONS:
        return _lane_a_inconclusive(
            f"Insufficient replications: {inp.replications} < {LANE_A_MIN_REPLICATIONS}.",
            inp,
        )

    # Decision-grade sensitivity reached
    sigma_offset = abs(inp.a_cp_measured) / inp.sigma_a  # sigma from zero
    predicted_offset = abs(inp.a_cp_measured - A_CP_PREDICTED) / inp.sigma_a

    zero_consistent = sigma_offset <= 1.96  # 95% CL

    if zero_consistent:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "supported": False,
            "evidence_strength_sigma": sigma_offset,
            "a_cp_predicted": A_CP_PREDICTED,
            "sigma_a_threshold": SIGMA_A_THRESHOLD,
            "decision_grade": True,
            "reason": (
                f"A_CP^lab = {inp.a_cp_measured:.3e} +/- {inp.sigma_a:.1e} is "
                f"consistent with zero at 95 CL ({sigma_offset:.2f} sigma from zero). "
                "Predicted nonzero signal not observed. FALSIFIED."
            ),
            "toe_score_contribution": 0.0,
        }

    if sigma_offset >= 3.0:
        return {
            "verdict": "SUPPORTED",
            "falsified": False,
            "supported": True,
            "evidence_strength_sigma": sigma_offset,
            "predicted_offset_sigma": predicted_offset,
            "a_cp_predicted": A_CP_PREDICTED,
            "sigma_a_threshold": SIGMA_A_THRESHOLD,
            "decision_grade": True,
            "reason": (
                f"A_CP^lab = {inp.a_cp_measured:.3e} +/- {inp.sigma_a:.1e} is "
                f"nonzero at {sigma_offset:.1f} sigma with topology-certified (5,7) controls. "
                f"Predicted value A_CP = {A_CP_PREDICTED:.4e}; measurement is "
                f"{predicted_offset:.1f} sigma away. SUPPORTED."
            ),
            "toe_score_contribution": LANE_A_TOE_CONTRIBUTION,
        }

    return {
        "verdict": "CONSISTENT",
        "falsified": False,
        "supported": False,
        "evidence_strength_sigma": sigma_offset,
        "a_cp_predicted": A_CP_PREDICTED,
        "sigma_a_threshold": SIGMA_A_THRESHOLD,
        "decision_grade": True,
        "reason": (
            f"A_CP^lab = {inp.a_cp_measured:.3e} +/- {inp.sigma_a:.1e} is "
            f"nonzero at {sigma_offset:.1f} sigma -- above zero but below 3 sigma. "
            "CONSISTENT; further data needed for SUPPORTED verdict."
        ),
        "toe_score_contribution": 0.0,
    }


def _lane_a_inconclusive(reason: str, inp: LaneAInput) -> dict:
    return {
        "verdict": "INCONCLUSIVE",
        "falsified": False,
        "supported": False,
        "evidence_strength_sigma": 0.0,
        "a_cp_predicted": A_CP_PREDICTED,
        "sigma_a_threshold": SIGMA_A_THRESHOLD,
        "decision_grade": False,
        "reason": reason,
        "toe_score_contribution": 0.0,
    }


# ---------------------------------------------------------------------------
# Lane B verdict
# ---------------------------------------------------------------------------

def lane_b_rotation_verdict(
    inp: LaneBInput,
) -> dict:
    """Apply the Lane B analogue rotation decision logic.

    The predicted rotation PHI_ROT_PREDICTED must be confirmed outside the
    forbidden gap [PHI_ROT_GAP_LOWER, PHI_ROT_GAP_UPPER].

    Parameters
    ----------
    inp : LaneBInput

    Returns
    -------
    dict with keys:
        verdict, falsified, supported, phi_rot_predicted, gap_lower, gap_upper,
        sigma_offset_from_predicted, in_gap, decision_grade, reason,
        toe_score_contribution
    """
    if inp.sigma_phi <= 0.0:
        raise ValueError(f"sigma_phi must be positive, got {inp.sigma_phi}")

    if not inp.calibration_confirmed:
        return {
            "verdict": "INCONCLUSIVE",
            "falsified": False,
            "supported": False,
            "phi_rot_predicted": PHI_ROT_PREDICTED,
            "gap_lower": PHI_ROT_GAP_LOWER,
            "gap_upper": PHI_ROT_GAP_UPPER,
            "decision_grade": False,
            "reason": "Calibration not confirmed; result is not decision-grade.",
            "toe_score_contribution": 0.0,
        }

    if inp.replication_count < 1:
        return {
            "verdict": "INCONCLUSIVE",
            "falsified": False,
            "supported": False,
            "phi_rot_predicted": PHI_ROT_PREDICTED,
            "gap_lower": PHI_ROT_GAP_LOWER,
            "gap_upper": PHI_ROT_GAP_UPPER,
            "decision_grade": False,
            "reason": "No replications recorded; result not confirmed.",
            "toe_score_contribution": 0.0,
        }

    in_gap = PHI_ROT_GAP_LOWER < inp.phi_rot_measured < PHI_ROT_GAP_UPPER
    sigma_offset = abs(inp.phi_rot_measured - PHI_ROT_PREDICTED) / inp.sigma_phi
    in_window = PHI_ROT_WINDOW_LOW <= inp.phi_rot_measured <= PHI_ROT_WINDOW_HIGH

    if in_gap:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "supported": False,
            "phi_rot_predicted": PHI_ROT_PREDICTED,
            "phi_rot_measured": inp.phi_rot_measured,
            "gap_lower": PHI_ROT_GAP_LOWER,
            "gap_upper": PHI_ROT_GAP_UPPER,
            "sigma_offset_from_predicted": sigma_offset,
            "in_gap": True,
            "in_window": in_window,
            "decision_grade": True,
            "reason": (
                f"phi_rot = {inp.phi_rot_measured:.4f} deg falls in the forbidden gap "
                f"({PHI_ROT_GAP_LOWER:.4f}, {PHI_ROT_GAP_UPPER:.4f}) deg. FALSIFIED."
            ),
            "toe_score_contribution": 0.0,
        }

    if not in_window:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "supported": False,
            "phi_rot_predicted": PHI_ROT_PREDICTED,
            "phi_rot_measured": inp.phi_rot_measured,
            "gap_lower": PHI_ROT_GAP_LOWER,
            "gap_upper": PHI_ROT_GAP_UPPER,
            "sigma_offset_from_predicted": sigma_offset,
            "in_gap": False,
            "in_window": False,
            "decision_grade": True,
            "reason": (
                f"phi_rot = {inp.phi_rot_measured:.4f} deg is outside the admissible "
                f"window [{PHI_ROT_WINDOW_LOW:.4f}, {PHI_ROT_WINDOW_HIGH:.4f}] deg. FALSIFIED."
            ),
            "toe_score_contribution": 0.0,
        }

    supported = sigma_offset <= 3.0
    return {
        "verdict": "SUPPORTED" if supported else "CONSISTENT",
        "falsified": False,
        "supported": supported,
        "phi_rot_predicted": PHI_ROT_PREDICTED,
        "phi_rot_measured": inp.phi_rot_measured,
        "gap_lower": PHI_ROT_GAP_LOWER,
        "gap_upper": PHI_ROT_GAP_UPPER,
        "sigma_offset_from_predicted": sigma_offset,
        "in_gap": False,
        "in_window": True,
        "decision_grade": True,
        "reason": (
            f"phi_rot = {inp.phi_rot_measured:.4f} deg is within the admissible "
            f"window and {sigma_offset:.2f} sigma from the predicted value "
            f"{PHI_ROT_PREDICTED:.4f} deg. "
            f"{'SUPPORTED (within 3 sigma).' if supported else 'CONSISTENT but >3 sigma away.'}"
        ),
        "toe_score_contribution": LANE_B_TOE_CONTRIBUTION if supported else 0.0,
    }


# ---------------------------------------------------------------------------
# Lane C verdict
# ---------------------------------------------------------------------------

def lane_c_bmode_verdict(
    inp: LaneCInput,
) -> dict:
    """Apply the Lane C cryogenic B-mode analogue decision logic.

    Parameters
    ----------
    inp : LaneCInput

    Returns
    -------
    dict with keys:
        verdict, falsified, supported, beta_lab_predicted,
        window_low, window_high, gap_lower, gap_upper,
        sigma_offset_from_predicted, in_gap, in_window,
        decision_grade, reason, toe_score_contribution
    """
    if inp.sigma_beta <= 0.0:
        raise ValueError(f"sigma_beta must be positive, got {inp.sigma_beta}")

    if not inp.calibration_confirmed:
        return _lane_c_inconclusive("Calibration not confirmed.", inp)

    if not inp.foreground_subtracted:
        return _lane_c_inconclusive("Foreground subtraction not confirmed.", inp)

    in_window = BETA_LAB_WINDOW_LOW <= inp.beta_lab_measured <= BETA_LAB_WINDOW_HIGH
    in_gap = BETA_LAB_GAP_LOWER < inp.beta_lab_measured < BETA_LAB_GAP_UPPER
    sigma_offset = abs(inp.beta_lab_measured - BETA_LAB_PREDICTED) / inp.sigma_beta

    if not in_window:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "supported": False,
            "beta_lab_predicted": BETA_LAB_PREDICTED,
            "window_low": BETA_LAB_WINDOW_LOW,
            "window_high": BETA_LAB_WINDOW_HIGH,
            "gap_lower": BETA_LAB_GAP_LOWER,
            "gap_upper": BETA_LAB_GAP_UPPER,
            "sigma_offset_from_predicted": sigma_offset,
            "in_gap": in_gap,
            "in_window": False,
            "decision_grade": True,
            "reason": (
                f"beta_lab = {inp.beta_lab_measured:.4f} deg is outside "
                f"admissible window [{BETA_LAB_WINDOW_LOW}, {BETA_LAB_WINDOW_HIGH}] deg. "
                "FALSIFIED."
            ),
            "toe_score_contribution": 0.0,
        }

    if in_gap:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "supported": False,
            "beta_lab_predicted": BETA_LAB_PREDICTED,
            "window_low": BETA_LAB_WINDOW_LOW,
            "window_high": BETA_LAB_WINDOW_HIGH,
            "gap_lower": BETA_LAB_GAP_LOWER,
            "gap_upper": BETA_LAB_GAP_UPPER,
            "sigma_offset_from_predicted": sigma_offset,
            "in_gap": True,
            "in_window": True,
            "decision_grade": True,
            "reason": (
                f"beta_lab = {inp.beta_lab_measured:.4f} deg falls in the "
                f"forbidden gap ({BETA_LAB_GAP_LOWER}, {BETA_LAB_GAP_UPPER}) deg. "
                "FALSIFIED (inter-sector gap)."
            ),
            "toe_score_contribution": 0.0,
        }

    supported = sigma_offset <= 3.0
    return {
        "verdict": "SUPPORTED" if supported else "CONSISTENT",
        "falsified": False,
        "supported": supported,
        "beta_lab_predicted": BETA_LAB_PREDICTED,
        "window_low": BETA_LAB_WINDOW_LOW,
        "window_high": BETA_LAB_WINDOW_HIGH,
        "gap_lower": BETA_LAB_GAP_LOWER,
        "gap_upper": BETA_LAB_GAP_UPPER,
        "sigma_offset_from_predicted": sigma_offset,
        "in_gap": False,
        "in_window": True,
        "decision_grade": True,
        "reason": (
            f"beta_lab = {inp.beta_lab_measured:.4f} deg is in the admissible "
            f"window, not in the gap, and {sigma_offset:.2f} sigma from predicted "
            f"{BETA_LAB_PREDICTED:.3f} deg. "
            f"{'SUPPORTED.' if supported else 'CONSISTENT but >3 sigma from prediction.'}"
        ),
        "toe_score_contribution": LANE_C_TOE_CONTRIBUTION if supported else 0.0,
    }


def _lane_c_inconclusive(reason: str, inp: LaneCInput) -> dict:
    return {
        "verdict": "INCONCLUSIVE",
        "falsified": False,
        "supported": False,
        "beta_lab_predicted": BETA_LAB_PREDICTED,
        "window_low": BETA_LAB_WINDOW_LOW,
        "window_high": BETA_LAB_WINDOW_HIGH,
        "gap_lower": BETA_LAB_GAP_LOWER,
        "gap_upper": BETA_LAB_GAP_UPPER,
        "decision_grade": False,
        "reason": reason,
        "toe_score_contribution": 0.0,
    }


# ---------------------------------------------------------------------------
# Composite verdict
# ---------------------------------------------------------------------------

def composite_proof_alternative(
    lane_a_result: dict,
    lane_b_result: dict,
    lane_c_result: dict,
) -> dict:
    """Aggregate the three lane verdicts into a single composite verdict.

    Aggregation rules:
    - If ANY lane returns FALSIFIED (decision-grade): composite is FALSIFIED.
    - If ALL decision-grade lanes return SUPPORTED: composite is STRONGLY_SUPPORTED.
    - If at least ONE decision-grade lane returns SUPPORTED and none are FALSIFIED:
      composite is SUPPORTED.
    - If no lanes are decision-grade: composite is PENDING.
    - Otherwise: composite is CONSISTENT.

    Parameters
    ----------
    lane_a_result : dict  -- output of lane_a_cp_asymmetry_verdict
    lane_b_result : dict  -- output of lane_b_rotation_verdict
    lane_c_result : dict  -- output of lane_c_bmode_verdict

    Returns
    -------
    dict with keys:
        composite_verdict, any_falsified, all_supported, total_toe_contribution,
        lane_a_verdict, lane_b_verdict, lane_c_verdict,
        decision_grade_count, supported_count, falsified_count, summary
    """
    lanes = [lane_a_result, lane_b_result, lane_c_result]
    lane_names = ["lane_a", "lane_b", "lane_c"]

    any_falsified = any(l.get("falsified", False) for l in lanes)
    decision_grade_lanes = [l for l in lanes if l.get("decision_grade", False)]
    supported_lanes = [l for l in lanes if l.get("supported", False)]
    n_dg = len(decision_grade_lanes)
    n_sup = len(supported_lanes)
    n_fal = sum(1 for l in lanes if l.get("falsified", False))

    total_toe = sum(l.get("toe_score_contribution", 0.0) for l in lanes)

    if any_falsified:
        verdict = "FALSIFIED"
    elif n_dg == 0:
        verdict = "PENDING"
    elif n_sup == n_dg and n_dg == 3:
        verdict = "STRONGLY_SUPPORTED"
    elif n_sup >= 1:
        verdict = "SUPPORTED"
    else:
        verdict = "CONSISTENT"

    summary = (
        f"Composite [{verdict}]: "
        f"{n_dg} decision-grade lanes, "
        f"{n_sup} supported, "
        f"{n_fal} falsified. "
        f"ToE score contribution: +{total_toe:.1f} pts. "
        f"(Lane A: {lane_a_result.get('verdict','?')} | "
        f"Lane B: {lane_b_result.get('verdict','?')} | "
        f"Lane C: {lane_c_result.get('verdict','?')})"
    )

    return {
        "composite_verdict": verdict,
        "any_falsified": any_falsified,
        "all_supported": n_sup == 3,
        "total_toe_contribution": total_toe,
        "lane_a_verdict": lane_a_result.get("verdict"),
        "lane_b_verdict": lane_b_result.get("verdict"),
        "lane_c_verdict": lane_c_result.get("verdict"),
        "decision_grade_count": n_dg,
        "supported_count": n_sup,
        "falsified_count": n_fal,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Evidence strength score
# ---------------------------------------------------------------------------

def evidence_strength_score(
    lane_a_result: dict,
    lane_b_result: dict,
    lane_c_result: dict,
) -> dict:
    """Compute a normalised evidence strength score in [0, 1].

    Scoring:
      SUPPORTED / STRONGLY_SUPPORTED lane: 1.0 / 3.0 per lane
      CONSISTENT (decision-grade):         0.5 / 3.0 per lane
      INCONCLUSIVE / PENDING:              0.0 per lane
      FALSIFIED:                          -1.0 (composite score -> 0)

    Parameters
    ----------
    lane_a_result, lane_b_result, lane_c_result : dict

    Returns
    -------
    dict with keys:
        score (float in [0,1]), max_score (1.0), per_lane_scores (list),
        interpretation (str)
    """
    lanes = [lane_a_result, lane_b_result, lane_c_result]
    per_lane = []
    for l in lanes:
        v = l.get("verdict", "INCONCLUSIVE")
        if l.get("falsified", False):
            per_lane.append(0.0)
        elif v == "SUPPORTED":
            per_lane.append(1.0 / 3.0)
        elif v == "CONSISTENT":
            per_lane.append(0.5 / 3.0)
        else:
            per_lane.append(0.0)

    any_falsified = any(l.get("falsified", False) for l in lanes)
    raw = sum(per_lane)
    score = 0.0 if any_falsified else min(raw, 1.0)

    if score >= 0.9:
        interp = "VERY STRONG — all lanes support the theory at decision grade."
    elif score >= 0.6:
        interp = "STRONG — majority of lanes support the theory at decision grade."
    elif score >= 0.3:
        interp = "MODERATE — at least one lane supports the theory."
    elif score > 0.0:
        interp = "WEAK — partial consistent evidence only."
    elif any_falsified:
        interp = "FALSIFIED — one or more lanes returned a falsification verdict."
    else:
        interp = "PENDING — no decision-grade results yet."

    return {
        "score": score,
        "max_score": 1.0,
        "per_lane_scores": per_lane,
        "any_falsified": any_falsified,
        "interpretation": interp,
    }


# ---------------------------------------------------------------------------
# Uncertainty budgets
# ---------------------------------------------------------------------------

def uncertainty_budget_lane_a() -> dict:
    """Uncertainty budget for Lane A CP-asymmetry campaigns.

    Returns
    -------
    dict
        Per-source sigma contributions and total (quadrature sum).
        All values are dimensionless (fractional asymmetry sigma).
    """
    components = {
        "topology_certification":  5.0e-7,  # (5,7) topology locking uncertainty
        "systematics_background":  3.0e-6,  # residual background asymmetry
        "detector_nonlinearity":   2.0e-6,  # detector efficiency imbalance
        "beam_asymmetry":          1.0e-6,  # geometric acceptance
        "statistical_floor":       4.0e-6,  # statistical noise per campaign
    }
    total = math.sqrt(sum(v ** 2 for v in components.values()))
    return {**components, "total": total, "decision_threshold": SIGMA_A_THRESHOLD}


def uncertainty_budget_lane_b() -> dict:
    """Uncertainty budget for Lane B analogue rotation campaigns.

    Returns
    -------
    dict
        Per-source sigma contributions (degrees) and total.
    """
    components = {
        "waveguide_phase_noise":   0.05,   # degrees, coherence-limited
        "temperature_drift":       0.02,   # degrees per K fluctuation
        "polarimeter_calibration": 0.03,   # degrees, systematic
        "topology_locking":        0.01,   # degrees, mode-locking fidelity
        "statistical_floor":       0.04,   # degrees, photon counting
    }
    total = math.sqrt(sum(v ** 2 for v in components.values()))
    return {
        **components,
        "total": total,
        "predicted_value_deg": PHI_ROT_PREDICTED,
        "gap_lower_deg": PHI_ROT_GAP_LOWER,
        "gap_upper_deg": PHI_ROT_GAP_UPPER,
    }


def uncertainty_budget_lane_c() -> dict:
    """Uncertainty budget for Lane C cryogenic B-mode analogue campaigns.

    Returns
    -------
    dict
        Per-source sigma contributions (degrees) and total.
    """
    components = {
        "instrument_systematics":  0.005,  # degrees, half-wave plate error
        "foreground_residual":     0.008,  # degrees, dust/synchrotron
        "calibration_source":      0.003,  # degrees, known source uncertainty
        "beam_effects":            0.004,  # degrees, sidelobe pickup
        "statistical_noise":       0.006,  # degrees, per observing block
    }
    total = math.sqrt(sum(v ** 2 for v in components.values()))
    return {
        **components,
        "total": total,
        "predicted_value_deg": BETA_LAB_PREDICTED,
        "window_low_deg": BETA_LAB_WINDOW_LOW,
        "window_high_deg": BETA_LAB_WINDOW_HIGH,
    }


# ---------------------------------------------------------------------------
# Status snapshot
# ---------------------------------------------------------------------------

def proof_alternative_status_snapshot() -> dict:
    """Return current status for all three proof-alternative lanes.

    Returns
    -------
    dict with per-lane status, predicted signals, decision thresholds,
    and overall readiness assessment.
    """
    return {
        "framework_version": "v10.26+512bit",
        "primary_falsifier": "LiteBIRD (launch ~2032, result ~2034)",
        "proof_alternative_lanes": {
            "lane_a_cp_asymmetry": {
                "id": "F14/P8",
                "name": "Table-Top CP Asymmetry (5,7) Topology-Certified",
                "status": "PENDING_CAMPAIGN",
                "predicted_signal": A_CP_PREDICTED,
                "decision_threshold_sigma": SIGMA_A_THRESHOLD,
                "toe_contribution_if_supported": LANE_A_TOE_CONTRIBUTION,
                "earliest_result_year": 2026,
                "budget": uncertainty_budget_lane_a(),
            },
            "lane_b_rotation": {
                "id": "F14/P9",
                "name": "Analogue Braid Polarisation Rotation",
                "status": "PENDING_CAMPAIGN",
                "predicted_signal_deg": PHI_ROT_PREDICTED,
                "gap_lower_deg": PHI_ROT_GAP_LOWER,
                "gap_upper_deg": PHI_ROT_GAP_UPPER,
                "toe_contribution_if_supported": LANE_B_TOE_CONTRIBUTION,
                "earliest_result_year": 2027,
                "budget": uncertainty_budget_lane_b(),
            },
            "lane_c_bmode": {
                "id": "F14/P10",
                "name": "Cryogenic B-Mode Polarisation Analogue",
                "status": "PENDING_CAMPAIGN",
                "predicted_signal_deg": BETA_LAB_PREDICTED,
                "admissible_window": [BETA_LAB_WINDOW_LOW, BETA_LAB_WINDOW_HIGH],
                "forbidden_gap": [BETA_LAB_GAP_LOWER, BETA_LAB_GAP_UPPER],
                "toe_contribution_if_supported": LANE_C_TOE_CONTRIBUTION,
                "earliest_result_year": 2027,
                "budget": uncertainty_budget_lane_c(),
            },
        },
        "max_pre_litebird_toe_contribution": (
            LANE_A_TOE_CONTRIBUTION + LANE_B_TOE_CONTRIBUTION + LANE_C_TOE_CONTRIBUTION
        ),
        "policy": (
            "All lanes must independently reach decision-grade sensitivity "
            "before a verdict is recorded. No inflation without gate passage."
        ),
    }
