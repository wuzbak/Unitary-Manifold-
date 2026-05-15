# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Statistical experimental design for the WS-3 Lab-Scale CP falsifier.

Covers power analysis, systematic budget, platform specifications,
campaign timeline, and blinding protocol — all calibrated to the
10^{-5} decision-grade sensitivity target for (5,7)-topology platforms.
"""
from __future__ import annotations

import math
from typing import Any

__all__ = [
    "SIGMA_A_DECISION_GRADE",
    "CONFIDENCE_LEVEL",
    "N_REPLICATIONS_REQUIRED",
    "statistical_power_analysis",
    "systematic_budget_allocation",
    "jj_squid_platform_spec",
    "topological_insulator_platform_spec",
    "campaign_timeline_and_milestones",
    "blinding_protocol_spec",
]

SIGMA_A_DECISION_GRADE: float = 1e-5
CONFIDENCE_LEVEL: float = 0.95
N_REPLICATIONS_REQUIRED: int = 2


def statistical_power_analysis(
    signal_a_cp: float,
    sigma_per_measurement: float,
    n_measurements: int,
) -> dict[str, Any]:
    """Compute statistical power for detecting A_CP at the given sensitivity.

    The combined uncertainty after n_measurements is:

        σ_A = σ_per_measurement / √n_measurements

    SNR = |signal_a_cp| / σ_A.
    Power to detect at 3σ: Φ(SNR − 3) where Φ is the normal CDF approximation.

    Parameters
    ----------
    signal_a_cp:
        Expected signal asymmetry.
    sigma_per_measurement:
        Noise per individual measurement.
    n_measurements:
        Number of measurements.

    Returns
    -------
    dict with keys:

    - ``n_measurements``
    - ``sigma_combined`` – combined σ after n_measurements
    - ``SNR`` – signal / σ_combined
    - ``power_to_detect_signal_at_3sigma`` – approximate power in [0, 1]
    - ``time_estimate_hours_at_1ms_integration`` – wall-clock hours estimate
    """
    if n_measurements <= 0:
        raise ValueError("n_measurements must be positive")
    if sigma_per_measurement <= 0:
        raise ValueError("sigma_per_measurement must be positive")

    sigma_combined = sigma_per_measurement / math.sqrt(n_measurements)
    snr = abs(signal_a_cp) / sigma_combined if sigma_combined > 0 else 0.0

    # Approximate Φ(x) via logistic surrogate accurate to ~0.001
    def phi(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-1.7 * x))

    power = phi(snr - 3.0)

    ms_per_measurement = 1.0
    time_hours = n_measurements * ms_per_measurement / 1e3 / 3600.0

    return {
        "n_measurements": n_measurements,
        "sigma_combined": sigma_combined,
        "SNR": snr,
        "power_to_detect_signal_at_3sigma": power,
        "time_estimate_hours_at_1ms_integration": time_hours,
    }


def systematic_budget_allocation() -> dict[str, Any]:
    """Break down the 10^{-5} total systematic uncertainty budget.

    Budget fractions:
    - Electronic noise floor  30 %  → σ_elec    = 3×10^{-6}
    - Thermal drift           20 %  → σ_thermal  = 2×10^{-6}
    - Cross-talk / EMI        20 %  → σ_xtalk    = 2×10^{-6}
    - Calibration             20 %  → σ_cal      = 2×10^{-6}
    - Statistical             10 %  → σ_stat     = 1×10^{-6}

    Quadrature total: √(9 + 4 + 4 + 4 + 1) × 10^{-6} = √22 × 10^{-6} ≈ 4.69×10^{-6}

    Returns
    -------
    dict with keys:

    - ``budget_table`` – list of (source, fraction, sigma) tuples
    - ``total_sigma`` – quadrature sum
    - ``budget_headroom_factor`` – SIGMA_A_DECISION_GRADE / total_sigma
    - ``notes``
    """
    budget_table = [
        ("electronic_noise_floor", 0.30, 3e-6),
        ("thermal_drift",          0.20, 2e-6),
        ("cross_talk_EMI",         0.20, 2e-6),
        ("calibration",            0.20, 2e-6),
        ("statistical",            0.10, 1e-6),
    ]
    total_sigma = math.sqrt(sum(s**2 for _, _, s in budget_table))
    headroom = SIGMA_A_DECISION_GRADE / total_sigma
    return {
        "budget_table": budget_table,
        "total_sigma": total_sigma,
        "budget_headroom_factor": headroom,
        "notes": (
            "Quadrature sum of all systematic contributions must stay below "
            f"SIGMA_A_DECISION_GRADE = {SIGMA_A_DECISION_GRADE:.0e}. "
            f"Current budget leaves headroom factor {headroom:.2f}."
        ),
    }


def jj_squid_platform_spec() -> dict[str, Any]:
    """Return design specification for the JJ/SQUID array platform.

    Returns
    -------
    dict with design constants and protocol fields.
    """
    return {
        "temperature_mk": 20,
        "junction_critical_current_ua": 1.0,
        "loop_inductance_ph": 50,
        "squid_mutual_inductance_ph": 10,
        "estimated_phase_noise_rad_per_sqrtHz": 1e-6,
        "required_integration_time_hours_per_measurement": 1.0,
        "topology_certification_method": "Andreev_reflection_spectroscopy",
        "control_platform_description": "identical_array_with_trivial_winding",
        "blinding_protocol": "signal_randomized_by_crypto_key_until_unblinding",
        "winding_numbers_certified": (5, 7),
        "notes": (
            "Operating temperature 20 mK suppresses quasiparticle poisoning. "
            "Topology certified via Andreev reflection spectroscopy prior to "
            "any CP-odd measurement. Control array has identical geometry but "
            "trivial (1,1) winding."
        ),
    }


def topological_insulator_platform_spec() -> dict[str, Any]:
    """Return design specification for the topological insulator platform.

    Returns
    -------
    dict with material candidates and protocol fields.
    """
    return {
        "material_candidates": ["Bi2Se3", "Bi2Te3", "(Bi,Sb)2Te3"],
        "operating_temperature_k": 4.0,
        "helical_surface_state_gap_mev": 300,
        "winding_encoding_method": "magnetic_domain_engineering",
        "required_film_thickness_nm": 10,
        "transport_observable": "Hall_resistance_asymmetry",
        "conjugate_protocol": "time_reversal_partner_with_B_field_sign_inversion",
        "winding_numbers_certified": (5, 7),
        "notes": (
            "Helical surface states encode (5,7) winding via ferromagnetic "
            "domain patterns. Conjugate protocol inverts B-field to generate "
            "time-reversal partner. Asymmetry measured via Hall resistance."
        ),
    }


def campaign_timeline_and_milestones() -> dict[str, Any]:
    """Return the full multi-year campaign timeline.

    Returns
    -------
    dict with phase keys and milestone descriptions.
    """
    return {
        "Phase_1": {
            "months": "1-6",
            "name": "Platform fabrication and topology certification",
            "deliverables": [
                "Fabricate JJ/SQUID arrays with (5,7)-certified winding",
                "Andreev reflection spectroscopy certification report",
                "Fabricate TI thin films with magnetic domain encoding",
                "Baseline noise characterization at operating temperature",
            ],
        },
        "Phase_2": {
            "months": "7-12",
            "name": "Blinded sensitivity commissioning",
            "deliverables": [
                "Blind CP-odd channel commissioning with randomized signal injection",
                "Systematic budget verification against design targets",
                "First sensitivity demonstration: σ_A ≤ 5×10^{-5}",
                "Pre-registration of analysis code and unblinding conditions",
            ],
        },
        "Phase_3": {
            "months": "13-18",
            "name": "Decision-grade measurement campaign",
            "deliverables": [
                "Full decision-grade run: σ_A ≤ 10^{-5}",
                "Systematic controls verification and sign-reversal tests",
                "Unblinding at independent statistician review",
                "Publication of A_CP^lab measurement",
            ],
        },
        "Phase_4": {
            "months": "19-24",
            "name": "Replication at second independent laboratory",
            "deliverables": [
                "Independent lab replicates Phase 3 with independent platform",
                "Joint analysis of both datasets",
                "Falsification verdict if null at 95% CL in both labs",
            ],
        },
        "falsification_possible_after_month": 24,
        "notes": (
            "Falsification verdict requires null result at σ_A ≤ 10^{-5} "
            "in N ≥ 2 independent (5,7)-certified platforms."
        ),
    }


def blinding_protocol_spec() -> dict[str, Any]:
    """Return the technical blinding specification for the CP campaign.

    Returns
    -------
    dict with blinding protocol fields.
    """
    return {
        "randomization_seed_custodian": "independent_statistician",
        "unblinding_condition": (
            "all_systematic_checks_complete_and_published"
        ),
        "pre_registration_required": True,
        "analysis_code_frozen_before_unblinding": True,
        "randomization_method": "AES-256 encrypted offset added to raw asymmetry",
        "blinding_audit_trail": "immutable_git_commit_hash_of_code_and_data",
        "partial_unblinding_policy": "prohibited_except_for_safety_stop_rules",
        "safety_stop_criteria": (
            "Campaign halted if σ_A > 10× design target after Phase 2"
        ),
        "notes": (
            "Full blinding until all systematics are published prevents "
            "experimenter bias in deciding when to stop data collection."
        ),
    }
