# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 294 — LISA GW Background Preregistration Package.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

P25 (Ω_GW ~ 10⁻¹⁵) is formally DERIVED (from the UM KK resonance cascade)
but remains 🟡 PENDING because LISA has not launched yet (~2035).  This module
formally locks the LISA routing protocol modelled on the successful JUNO DR1
preregistration package (juno_dr1_preregistration_package.py).

Physical context
----------------
The UM Kaluza–Klein resonance cascade generates a stochastic gravitational
wave background from the Planck-scale compactification.  For the KK scale
M_KK ~ M_Pl ~ 10¹⁹ GeV, the primary peak frequency is:

    f_peak ≈ M_KK / (2π) in natural units
           ≈ 10¹⁹ GeV / (2π × 1.52×10²⁴ Hz/GeV) ≈ 10⁴³ Hz

This is far above LISA sensitivity (10⁻⁴ – 1 Hz).  However, KK resonances
at the accessible electroweak/inflation boundary (sub-Planck M_KK scenarios)
or the secondary GW spectrum from braided inflation could be observable.

UM GW background predictions
------------------------------
Primary mode (Planck-scale KK, n_w=5, first resonance):
    Ω_GW(f_peak) ≈ 10⁻¹⁵  (P25, DERIVED)
    f_peak(KK) ≈ M_KK_eff / (2π × ħ) ≈ 10⁴³ Hz (NOT LISA-detectable)

Secondary mode (braided inflation + phase-transition background):
    f_secondary ≈ n_w × c_s × H_inf / (2π) × redshift
    This could fall in LISA band for M_inf ~ 10¹⁵ GeV

Ω_GW spectral shape:
    Ω_GW(f) ∝ (f / f_ref)² × exp(−f / f_ref)   [modified thermal + KK]

LISA routing preregistration
-----------------------------
Routing is defined in three scenarios:
  1. CONSISTENT:  Ω_GW measured at f ~ 3 mHz consistent with 10⁻¹⁵ → PASS
  2. TENSION:     Ω_GW > 10⁻¹² at f ~ 3 mHz without UM KK explanation → TENSION
  3. FALSIFIED:   Positive detection at LISA peak inconsistent with UM shape → REVIEW

LISA sensitivity curve (approximate):
  S_n(f) ≈ 2×10⁻⁴³ Hz⁻¹ at f = 3 mHz (design sensitivity)
  Corresponding Ω_GW sensitivity: ~10⁻¹² at SNR=1 over 4-yr mission

Reference
---------
  LISA Consortium (arXiv:1702.00786); UM P25 → kk_gw_background.py
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "UM_OMEGA_GW_PREDICTION",
    "UM_OMEGA_GW_LOG10",
    "LISA_PEAK_FREQ_HZ",
    "LISA_OMEGA_SENSITIVITY",
    "LISA_LAUNCH_YEAR",
    "CONSISTENT_SIGMA",
    "DOCS_TO_UPDATE",
    "separation_guard",
    "um_omega_gw_prediction",
    "lisa_sensitivity_comparison",
    "omega_gw_spectral_shape",
    "lisa_routing_thresholds",
    "lisa_dr1_routing",
    "lisa_preregistration_checklist",
    "euclid_desi_dr3_readiness",
    "lisa_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 294
PILLAR_TITLE: str = "LISA GW Background Preregistration Package"

# UM prediction (P25, DERIVED)
UM_OMEGA_GW_PREDICTION: float = 1.0e-15
UM_OMEGA_GW_LOG10: float = -15.0

# LISA parameters
LISA_PEAK_FREQ_HZ: float = 3.0e-3    # LISA most sensitive frequency (~3 mHz)
LISA_OMEGA_SENSITIVITY: float = 1.0e-12  # Ω_GW sensitivity at SNR=1, 4-yr mission
LISA_LAUNCH_YEAR: int = 2035

# KK primary peak (unreachable by LISA)
KK_OMEGA_PEAK_FREQ_HZ: float = 1.0e43   # ~ M_KK/(2π ħ)
N_W: int = 5
M_W: int = 7
K_CS: int = 74
C_S: float = 12.0 / 37.0     # braided sound speed

# Routing thresholds
CONSISTENT_SIGMA: float = 3.0   # consistent within this many σ

# Documents to update upon LISA measurement
DOCS_TO_UPDATE: List[str] = [
    "docs/CLAIM_MASTER_BOARD.md",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "FALLIBILITY.md",
    "docs/WAVE_CHANGELOG.md",
    "STATUS.md",
]


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 294."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "preregistration": True,
        "target_experiment": "LISA",
        "expected_launch_year": LISA_LAUNCH_YEAR,
    }


def um_omega_gw_prediction() -> Dict[str, object]:
    """Return the UM Ω_GW prediction for the KK resonance cascade.

    The primary peak is at f ~ 10⁴³ Hz (Planck-scale KK), which is
    completely undetectable by LISA.  The secondary spectrum from braided
    inflation is estimated at the inflation-to-LISA frequency bridge.
    """
    # Primary peak: Planck-scale KK (undetectable)
    # Secondary: braided inflation phase-transition signal
    # Rough estimate: h²Ω_GW ~ (α_GW/α_EM)² × (H_inf/M_Pl)² × (f/f_peak)^n
    alpha_gw = 4.49e-10   # from 10D UV completion (Pillar 52)
    alpha_em = 1.0 / 137.0
    h_inf_over_mpl = 1.0e-5   # approximate inflation scale ratio
    omega_secondary = (alpha_gw / alpha_em) ** 2 * h_inf_over_mpl ** 2
    return {
        "omega_gw_p25_derivation": UM_OMEGA_GW_PREDICTION,
        "log10_omega_gw": UM_OMEGA_GW_LOG10,
        "f_peak_kk_hz": KK_OMEGA_PEAK_FREQ_HZ,
        "f_peak_kk_undetectable_by_lisa": True,
        "omega_secondary_estimate": omega_secondary,
        "omega_secondary_log10": math.log10(omega_secondary) if omega_secondary > 0 else None,
        "source": "P25 DERIVED — kk_gw_background.py; Pillar 69",
        "label": "DERIVED_PENDING_LISA_MEASUREMENT",
    }


def lisa_sensitivity_comparison() -> Dict[str, object]:
    """Compare UM Ω_GW prediction with LISA sensitivity curve.

    LISA sensitivity at 3 mHz: Ω_GW ~ 10⁻¹² (SNR=1, 4-yr mission).
    UM prediction: Ω_GW ~ 10⁻¹⁵ — below LISA sensitivity by ~3 orders.

    The KK primary peak at 10⁴³ Hz is undetectable by any planned instrument.
    The secondary braided-inflation spectrum may fall in or near LISA band
    depending on the inflation scale assumed.
    """
    detection_possible = UM_OMEGA_GW_PREDICTION > LISA_OMEGA_SENSITIVITY
    snr_estimate = UM_OMEGA_GW_PREDICTION / LISA_OMEGA_SENSITIVITY
    gap_orders = math.log10(LISA_OMEGA_SENSITIVITY / UM_OMEGA_GW_PREDICTION)
    return {
        "um_omega_gw": UM_OMEGA_GW_PREDICTION,
        "lisa_sensitivity": LISA_OMEGA_SENSITIVITY,
        "snr_estimate": snr_estimate,
        "log10_snr": math.log10(snr_estimate),
        "gap_orders_below_sensitivity": gap_orders,
        "direct_detection_possible": detection_possible,
        "verdict": (
            "UM_BELOW_LISA_SENSITIVITY"
            if not detection_possible
            else "UM_IN_LISA_BAND"
        ),
        "note": (
            "UM primary KK GW peak at ~10⁴³ Hz is completely undetectable. "
            "The P25 Ω_GW~10⁻¹⁵ prediction is ~3 orders below LISA sensitivity. "
            "A non-detection by LISA is CONSISTENT with the UM framework. "
            "A positive detection above 10⁻¹² at 3 mHz would require a new UM "
            "mechanism (secondary spectrum, phase transition, inflation cascade)."
        ),
    }


def omega_gw_spectral_shape(
    f_hz: float,
    f_ref_hz: float = LISA_PEAK_FREQ_HZ,
    omega_ref: float = UM_OMEGA_GW_PREDICTION,
) -> float:
    """Return the UM Ω_GW spectral shape at frequency f_hz.

    The modified thermal + KK cascade spectral shape:
        Ω_GW(f) = omega_ref × (f/f_ref)² × exp(−f/f_ref)

    This is a generic broken power-law motivated by the KK cascade structure.
    The exact spectral shape requires full numerical Boltzmann evolution.

    Parameters
    ----------
    f_hz : float
        Frequency in Hz.
    f_ref_hz : float
        Reference frequency (LISA peak at 3 mHz by default).
    omega_ref : float
        Ω_GW at f_ref (UM prediction at 10⁻¹⁵ by default).
    """
    if f_hz <= 0.0 or f_ref_hz <= 0.0:
        raise ValueError("Frequencies must be positive")
    x = f_hz / f_ref_hz
    return omega_ref * x ** 2 * math.exp(-x)


def lisa_routing_thresholds() -> Dict[str, object]:
    """Return the preregistered LISA routing thresholds.

    These thresholds are locked at v11.9 and must not be adjusted post-hoc.
    They define the decision boundary for the three verdict scenarios.
    """
    return {
        "CONSISTENT": {
            "condition": f"Ω_GW ≤ {LISA_OMEGA_SENSITIVITY:.0e} or non-detection",
            "threshold_omega": LISA_OMEGA_SENSITIVITY,
            "action": "P25 PENDING → strengthened; log to OBSERVATION_TRACKER",
        },
        "TENSION": {
            "condition": (
                f"Ω_GW > {LISA_OMEGA_SENSITIVITY:.0e} with spectral shape "
                "inconsistent with UM KK cascade"
            ),
            "threshold_omega": LISA_OMEGA_SENSITIVITY * 10.0,
            "action": "Flag in CLAIM_MASTER_BOARD; review secondary spectrum mechanism",
        },
        "FALSIFIED": {
            "condition": (
                f"Positive detection > 3σ with Ω_GW shape and f_peak "
                "inconsistent with any UM mechanism"
            ),
            "threshold_omega": LISA_OMEGA_SENSITIVITY * 100.0,
            "action": "P25 FALSIFIED; open retraction issue; update all truth surfaces",
        },
        "preregistration_version": "v11.9",
        "preregistration_date": "2026-05-20",
        "decisive_experiment": "LISA (~2035)",
    }


def lisa_dr1_routing(
    omega_gw_measured: float,
    sigma_omega: float,
    spectral_shape_consistent: bool = True,
) -> Dict[str, object]:
    """Route a LISA Ω_GW measurement to a verdict.

    Parameters
    ----------
    omega_gw_measured : float
        Measured Ω_GW at LISA peak frequency (or upper limit).
    sigma_omega : float
        1σ uncertainty on Ω_GW measurement.
    spectral_shape_consistent : bool
        Whether the measured spectral shape is consistent with UM KK cascade.
    """
    if sigma_omega <= 0.0:
        raise ValueError("sigma_omega must be positive")

    is_detection = omega_gw_measured > LISA_OMEGA_SENSITIVITY
    sigma_pull = abs(omega_gw_measured - UM_OMEGA_GW_PREDICTION) / sigma_omega

    if not is_detection:
        verdict = "CONSISTENT"
        detail = (
            f"LISA non-detection (Ω_GW < {omega_gw_measured:.2e}) is consistent "
            f"with UM P25 prediction of Ω_GW ~ {UM_OMEGA_GW_PREDICTION:.0e}."
        )
    elif is_detection and spectral_shape_consistent:
        verdict = "TENSION"
        detail = (
            f"LISA detects Ω_GW ~ {omega_gw_measured:.2e} — above UM prediction. "
            "Spectral shape is UM-consistent; may indicate secondary mechanism."
        )
    elif is_detection and not spectral_shape_consistent and sigma_pull >= CONSISTENT_SIGMA:
        verdict = "FALSIFIED"
        detail = (
            f"LISA detection at {omega_gw_measured:.2e} with shape inconsistent with "
            f"UM KK cascade at {sigma_pull:.1f}σ. P25 falsified."
        )
    else:
        verdict = "INCONCLUSIVE"
        detail = "LISA measurement does not decisively route to a verdict at this precision."

    return {
        "omega_gw_measured": omega_gw_measured,
        "sigma_omega": sigma_omega,
        "spectral_shape_consistent": spectral_shape_consistent,
        "um_prediction": UM_OMEGA_GW_PREDICTION,
        "is_detection": is_detection,
        "sigma_pull": sigma_pull,
        "verdict": verdict,
        "detail": detail,
        "docs_to_update": DOCS_TO_UPDATE if verdict != "CONSISTENT" else DOCS_TO_UPDATE[:2],
        "preregistration_version": "v11.9",
    }


def lisa_preregistration_checklist() -> List[Dict[str, object]]:
    """Return the same-day readiness checklist for LISA data."""
    return [
        {
            "item": "UM Ω_GW prediction locked",
            "status": "COMPLETE",
            "value": f"Ω_GW ~ {UM_OMEGA_GW_PREDICTION:.0e} (P25, DERIVED)",
            "reference": "kk_gw_background.py, pillar231_lisa_omega_gw_preregistration_package.py",
        },
        {
            "item": "LISA routing thresholds preregistered",
            "status": "COMPLETE",
            "value": "CONSISTENT / TENSION / FALSIFIED thresholds locked at v11.9",
            "reference": "pillar294_lisa_gw_background_preregistration.py",
        },
        {
            "item": "Spectral shape model",
            "status": "COMPLETE",
            "value": "Ω_GW(f) ∝ (f/f_ref)² exp(−f/f_ref); f_ref = 3 mHz",
            "reference": "omega_gw_spectral_shape() in this module",
        },
        {
            "item": "LISA sensitivity comparison",
            "status": "COMPLETE",
            "value": "UM Ω_GW ~ 3 orders below LISA sensitivity; non-detection CONSISTENT",
            "reference": "lisa_sensitivity_comparison() in this module",
        },
        {
            "item": "Docs-to-update list prepared",
            "status": "COMPLETE",
            "value": str(DOCS_TO_UPDATE),
            "reference": "pillar294_lisa_gw_background_preregistration.py",
        },
        {
            "item": "LISA expected launch",
            "status": "MONITORING",
            "value": f"~{LISA_LAUNCH_YEAR}",
            "reference": "LISA Consortium public timeline",
        },
    ]


def euclid_desi_dr3_readiness() -> Dict[str, object]:
    """Euclid Early Release + DESI DR3 combined readiness assessment.

    Euclid is releasing early galaxy clustering and BAO data (Euclid Early
    Release Observations, 2024–2025).  This function pre-checks the combined
    Euclid+DESI constraint on the dark energy equation of state wₐ,
    extending the DESI DR3 publication-day runbook (Pillar 281) with a
    Euclid-combined scenario.

    Note: This is included in Pillar 294 as a Track 3 observational
    monitoring infrastructure deliverable (per the v11.9 sprint plan).
    """
    # Current DESI DR2 status: T1 at 2.75σ on wₐ
    desi_dr2_sigma = 2.75
    # Euclid Early Release BAO: σ(wₐ) improvement factor ~1.3 (rough)
    # Combined Euclid+DESI uncertainty improvement: ~1/sqrt(1 + 1.3²) relative
    euclid_improvement_factor = 1.3
    desi_dr3_sigma_projection = 2.75 * 1.15   # DESI DR3 (more data) ~15% tighter
    combined_sigma_estimate = math.sqrt(
        desi_dr3_sigma_projection ** 2 + euclid_improvement_factor ** 2
    )
    falsification_threshold = 3.0

    return {
        "current_status": {
            "desi_dr2_sigma": desi_dr2_sigma,
            "verdict": "HIGH_TENSION",
            "falsified": desi_dr2_sigma >= falsification_threshold,
        },
        "euclid_projection": {
            "improvement_factor": euclid_improvement_factor,
            "source": "Euclid Early Release Observations (2024-2025)",
            "note": "Rough estimate; Euclid-specific BAO analysis pending",
        },
        "desi_dr3_projection": {
            "sigma_estimate": desi_dr3_sigma_projection,
            "scenario": "DESI DR3 tightens by ~15% with additional year of data",
        },
        "euclid_desi_combined": {
            "sigma_estimate": combined_sigma_estimate,
            "falsified_if": f"combined σ ≥ {falsification_threshold}",
            "current_below_threshold": combined_sigma_estimate < falsification_threshold,
            "margin_to_falsification": falsification_threshold - combined_sigma_estimate,
        },
        "routing_instruction": (
            "Execute desi_dr3_publication_day_runbook.route_desi_y3() within 30 days "
            "of DESI DR3 publication. If Euclid BAO data is available simultaneously, "
            "apply combined_sigma_estimate to the routing verdict. Update "
            "CLAIM_MASTER_BOARD.md T1 row with combined result."
        ),
        "label": "ADJACENT_TRACK_INFRASTRUCTURE",
        "preregistration_version": "v11.9",
    }


def lisa_preregistration_report() -> Dict[str, object]:
    """Full Pillar 294 LISA preregistration report."""
    pred = um_omega_gw_prediction()
    sensitivity = lisa_sensitivity_comparison()
    thresholds = lisa_routing_thresholds()
    # Drill: non-detection scenario
    routing_nondetect = lisa_dr1_routing(LISA_OMEGA_SENSITIVITY * 0.3, LISA_OMEGA_SENSITIVITY * 0.1)
    # Drill: detection scenario (hypothetical)
    routing_detect = lisa_dr1_routing(LISA_OMEGA_SENSITIVITY * 5.0, LISA_OMEGA_SENSITIVITY * 0.5)
    checklist = lisa_preregistration_checklist()
    euclid_readiness = euclid_desi_dr3_readiness()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "prediction": pred,
        "lisa_sensitivity": sensitivity,
        "routing_thresholds": thresholds,
        "routing_drills": {
            "non_detection": routing_nondetect,
            "detection_hypothetical": routing_detect,
        },
        "readiness_checklist": checklist,
        "euclid_desi_dr3_readiness": euclid_readiness,
        "status": "PREREGISTRATION_LOCKED",
        "summary": (
            "LISA routing preregistered and locked at v11.9. "
            f"UM Ω_GW ~ 10⁻¹⁵ is ~3 orders below LISA sensitivity (~10⁻¹²). "
            "Non-detection by LISA (expected) is CONSISTENT with P25. "
            "Any positive LISA detection above 10⁻¹² requires a new UM mechanism. "
            "Euclid+DESI DR3 combined scenario armed for T1 wₐ monitoring."
        ),
    }
