# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar223_medical_imaging_diagnosis.py
================================================
Pillar 223 — Medical Imaging and Health Diagnosis.

🔵 ADJACENT TRACK — not a hardgate physics claim.

Adjacent applied research track (non-hardgate): imaging physics and diagnostic
inference models for safer, more rigorous decision support.
"""
from __future__ import annotations

import math

__provenance__ = {
    "pillar": 223,
    "title": "Medical Imaging and Health Diagnosis",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — imaging and diagnostic inference",
}

__all__ = [
    "N_W",
    "K_CS",
    "PHI0",
    "BRAIDED_SOUND_SPEED",
    "SOUND_SPEED_SOFT_TISSUE",
    "CT_RISK_PER_MSV_ADULT",
    "ultrasound_axial_resolution",
    "ct_effective_risk",
    "bayes_ppv_npv",
    "fused_diagnostic_probability",
    "diagnostic_triage",
    "cross_pillar_alignment_score",
    "pillar223_summary",
]

N_W: int = 5
K_CS: int = 74
PHI0: float = 0.739085
BRAIDED_SOUND_SPEED: float = 12 / 37

SOUND_SPEED_SOFT_TISSUE: float = 1540.0
CT_RISK_PER_MSV_ADULT: float = 5e-5


def ultrasound_axial_resolution(
    center_frequency_mhz: float,
    fractional_bandwidth: float,
    sound_speed_m_s: float = SOUND_SPEED_SOFT_TISSUE,
) -> dict:
    """Axial resolution approximation: Δz ≈ c / (2 * BW), BW = f0 * frac_bw."""
    if center_frequency_mhz <= 0:
        raise ValueError("center_frequency_mhz must be positive.")
    if not 0 < fractional_bandwidth <= 1.5:
        raise ValueError("fractional_bandwidth must be in (0, 1.5].")
    if sound_speed_m_s <= 0:
        raise ValueError("sound_speed_m_s must be positive.")

    bw_hz = center_frequency_mhz * 1e6 * fractional_bandwidth
    resolution_m = sound_speed_m_s / (2.0 * bw_hz)
    return {
        "center_frequency_mhz": center_frequency_mhz,
        "fractional_bandwidth": fractional_bandwidth,
        "bandwidth_hz": bw_hz,
        "axial_resolution_mm": resolution_m * 1e3,
    }


def ct_effective_risk(dose_msv: float, age_years: float) -> dict:
    """Linearized risk estimate with age modulation."""
    if dose_msv < 0:
        raise ValueError("dose_msv must be non-negative.")
    if age_years <= 0:
        raise ValueError("age_years must be positive.")

    # Higher radiosensitivity in younger cohorts, lower in older cohorts.
    age_factor = max(0.3, min(2.5, 45.0 / age_years))
    excess_risk = dose_msv * CT_RISK_PER_MSV_ADULT * age_factor
    return {
        "dose_msv": dose_msv,
        "age_years": age_years,
        "age_factor": age_factor,
        "estimated_excess_cancer_risk": excess_risk,
        "risk_percent": 100.0 * excess_risk,
    }


def bayes_ppv_npv(prevalence: float, sensitivity: float, specificity: float) -> dict:
    """Compute PPV/NPV from prevalence, sensitivity, specificity."""
    if not 0.0 <= prevalence <= 1.0:
        raise ValueError("prevalence must be in [0, 1].")
    if not 0.0 <= sensitivity <= 1.0:
        raise ValueError("sensitivity must be in [0, 1].")
    if not 0.0 <= specificity <= 1.0:
        raise ValueError("specificity must be in [0, 1].")

    p_pos = sensitivity * prevalence + (1.0 - specificity) * (1.0 - prevalence)
    p_neg = (1.0 - sensitivity) * prevalence + specificity * (1.0 - prevalence)

    ppv = (sensitivity * prevalence / p_pos) if p_pos > 0 else 0.0
    npv = (specificity * (1.0 - prevalence) / p_neg) if p_neg > 0 else 0.0
    return {
        "prevalence": prevalence,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "positive_rate": p_pos,
        "negative_rate": p_neg,
    }


def fused_diagnostic_probability(probabilities: dict[str, float], weights: dict[str, float] | None = None) -> dict:
    """Fuse modality-level probabilities with normalized weighted averaging."""
    if not probabilities:
        raise ValueError("probabilities must be non-empty.")
    if any((p < 0.0 or p > 1.0) for p in probabilities.values()):
        raise ValueError("all probabilities must be in [0, 1].")

    if weights is None:
        weights = {k: 1.0 for k in probabilities}
    if set(weights.keys()) != set(probabilities.keys()):
        raise ValueError("weights keys must match probabilities keys.")
    if any(v < 0 for v in weights.values()):
        raise ValueError("weights must be non-negative.")

    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("sum of weights must be positive.")
    fused = sum(probabilities[k] * weights[k] for k in probabilities) / total_weight
    disagreement = max(probabilities.values()) - min(probabilities.values())
    return {
        "fused_probability": fused,
        "disagreement_index": disagreement,
        "modalities": len(probabilities),
    }


def diagnostic_triage(fused_probability: float, npv: float, critical_symptom_score: float) -> dict:
    """Simple triage policy from fused probability + safety buffers."""
    if not 0.0 <= fused_probability <= 1.0:
        raise ValueError("fused_probability must be in [0, 1].")
    if not 0.0 <= npv <= 1.0:
        raise ValueError("npv must be in [0, 1].")
    if not 0.0 <= critical_symptom_score <= 1.0:
        raise ValueError("critical_symptom_score must be in [0, 1].")

    if critical_symptom_score >= 0.85:
        action = "urgent_imaging_and_specialist_review"
    elif fused_probability >= 0.75:
        action = "confirmatory_test_and_treatment_planning"
    elif fused_probability <= 0.20 and npv >= 0.95:
        action = "watchful_waiting_with_followup"
    else:
        action = "additional_noninvasive_testing"

    return {
        "action": action,
        "fused_probability": fused_probability,
        "npv": npv,
        "critical_symptom_score": critical_symptom_score,
    }


def cross_pillar_alignment_score(
    ultrasound_mechanical_index: float,
    nanosensor_snr_db: float,
    fused_probability: float,
) -> dict:
    """Alignment metric across Pillars 221–223 for coherent end-to-end workflows."""
    if ultrasound_mechanical_index < 0:
        raise ValueError("ultrasound_mechanical_index must be non-negative.")
    if not 0.0 <= fused_probability <= 1.0:
        raise ValueError("fused_probability must be in [0, 1].")

    safety = max(0.0, min(1.0, 1.0 - ultrasound_mechanical_index / 1.9))
    sensing = max(0.0, min(1.0, 1.0 / (1.0 + math.exp(-(nanosensor_snr_db - 20.0) / 5.0))))
    inference = fused_probability
    alignment = 0.35 * safety + 0.30 * sensing + 0.35 * inference
    return {
        "alignment_score": alignment,
        "safety_component": safety,
        "sensing_component": sensing,
        "inference_component": inference,
    }


def pillar223_summary() -> dict:
    """Summary snapshot for Pillar 223."""
    us = ultrasound_axial_resolution(7.5, 0.6)
    bayes = bayes_ppv_npv(prevalence=0.12, sensitivity=0.91, specificity=0.88)
    fused = fused_diagnostic_probability(
        probabilities={"ultrasound": bayes["ppv"], "mri": 0.82, "lab_panel": 0.71},
        weights={"ultrasound": 1.0, "mri": 1.2, "lab_panel": 0.8},
    )
    align = cross_pillar_alignment_score(ultrasound_mechanical_index=0.9, nanosensor_snr_db=34.0, fused_probability=fused["fused_probability"])
    return {
        "pillar": 223,
        "title": "Medical Imaging and Health Diagnosis",
        "status": "ADJACENT RESEARCH TRACK — imaging and diagnostic inference",
        "ultrasound_axial_resolution_mm_example": us["axial_resolution_mm"],
        "bayes_ppv_example": bayes["ppv"],
        "fused_probability_example": fused["fused_probability"],
        "cross_pillar_alignment_score": align["alignment_score"],
        "epistemic_note": (
            "Outputs are decision-support heuristics and do not replace "
            "clinician judgment, regulatory protocols, or patient-specific standards of care."
        ),
    }
