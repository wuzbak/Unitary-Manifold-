# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 290 — Dark Matter Direct Detection Constraints.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Retains the historical expression
    G_N² × m_n² × (m_n / M_KK)⁴ × (N_W / K_CS)² / π
for numerical reproducibility only. In CGS its dimensions are cm⁶/s⁴,
not area. The deprecated ``kk_graviton_si_cross_section`` name therefore
does not denote a physical scattering cross-section.

This module specifies neither a DM particle nor a recoil amplitude. Its
supplied 1 TeV mediator scale is not the 30 GeV DM mass at which the LZ
reference limit is quoted. Physical cross-sections, limit ratios and
consistency assessments consequently fail closed as None / UNSUPPORTED.
Neither a null result nor a positive signal can confirm or refute a missing
UM direct-detection prediction. No replacement scattering model is assumed.
"""
from __future__ import annotations

import math
import warnings
from typing import Dict

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "M_KK_GEV",
    "M_N_GEV",
    "N_W",
    "K_CS",
    "G_N_CGS",
    "GEV_TO_G",
    "LZ_YEAR2_SIGMA_LIMIT_CM2",
    "LZ_YEAR3_PROJECTED_LIMIT_CM2",
    "separation_guard",
    "kk_graviton_si_cross_section",
    "legacy_kk_graviton_dimensional_proxy",
    "LEGACY_PROXY_UNITS",
    "lz_year2_exclusion_limit",
    "consistency_verdict",
    "lz_year3_projection",
    "dm_detection_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 290
PILLAR_TITLE: str = "Dark Matter Direct Detection Constraints"

M_KK_GEV: float = 1.0e3        # supplied mediator scale, not a DM particle mass
M_N_GEV: float = 0.9389        # nucleon mass in GeV
N_W: int = 5                   # winding number
K_CS: int = 74                 # braid resonance anchor

G_N_CGS: float = 6.674e-8      # G_N in cm³ g⁻¹ s⁻²
GEV_TO_G: float = 1.783e-24    # 1 GeV/c² in grams

LZ_YEAR2_SIGMA_LIMIT_CM2: float = 6.6e-48   # at m_chi=30 GeV, 90% CL
LZ_YEAR3_PROJECTED_LIMIT_CM2: float = 2.0e-48
LEGACY_PROXY_UNITS: str = "cm^6/s^4"


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 290."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "experiments": ["LZ", "XENONnT"],
    }


def kk_graviton_si_cross_section(m_kk_tev: float = 1.0) -> float:
    """Deprecated, misnamed legacy proxy in cm⁶/s⁴, NOT a cross-section.

    Numerical behavior is retained for reproducibility. Use
    legacy_kk_graviton_dimensional_proxy for explicitly non-physical output.
    """
    warnings.warn(
        "kk_graviton_si_cross_section is a misnamed dimensional proxy "
        "(cm^6/s^4), not a cross-section; use legacy_kk_graviton_dimensional_proxy",
        DeprecationWarning,
        stacklevel=2,
    )
    return legacy_kk_graviton_dimensional_proxy(m_kk_tev)


def legacy_kk_graviton_dimensional_proxy(m_kk_tev: float = 1.0) -> float:
    """Historical G_CGS² m_n,g² (m_n/M_KK)⁴ (N_W/K_CS)² / π [cm⁶/s⁴]."""
    if m_kk_tev <= 0.0:
        raise ValueError("m_kk_tev must be positive")
    m_kk_gev = m_kk_tev * 1.0e3
    # nucleon mass in grams
    m_n_g = M_N_GEV * GEV_TO_G
    # mass ratio (dimensionless)
    mass_ratio = M_N_GEV / m_kk_gev
    # braid suppression
    braid_suppression = (N_W / K_CS) ** 2
    proxy = G_N_CGS ** 2 * m_n_g ** 2 * mass_ratio ** 4 * braid_suppression / math.pi
    return proxy


def lz_year2_exclusion_limit() -> Dict[str, object]:
    """Return LZ Year 2 exclusion limit parameters."""
    return {
        "sigma_limit_cm2": LZ_YEAR2_SIGMA_LIMIT_CM2,
        "m_chi_gev": 30.0,
        "confidence_level": "90%",
        "reference": "LZ Year 2 (2024)",
    }


def consistency_verdict() -> Dict[str, object]:
    """Fail closed: no physical UM cross-section is available to compare."""
    return {
        "um_sigma_cm2": None,
        "lz_limit_cm2": LZ_YEAR2_SIGMA_LIMIT_CM2,
        "ratio_limit_to_um": None,
        "verdict": "UNSUPPORTED",
        "margin_factors": None,
        "legacy_kk_graviton_proxy_cm6_s4": legacy_kk_graviton_dimensional_proxy(),
        "legacy_proxy_units": LEGACY_PROXY_UNITS,
        "mediator_mass_gev": M_KK_GEV,
        "dm_mass_gev": None,
        "limit_dm_mass_gev": 30.0,
        "unsupported_reason": (
            "Legacy proxy has dimensions cm^6/s^4, not cm^2; no DM identity "
            "or recoil amplitude is specified, and mediator mass is not DM mass."
        ),
    }


def lz_year3_projection() -> Dict[str, object]:
    """Record a supplied detector projection without a UM scattering verdict."""
    return {
        "projected_limit_cm2": LZ_YEAR3_PROJECTED_LIMIT_CM2,
        "um_sigma_cm2": None,
        "ratio_limit_to_um": None,
        "verdict": "UNSUPPORTED",
        "legacy_kk_graviton_proxy_cm6_s4": legacy_kk_graviton_dimensional_proxy(),
        "legacy_proxy_units": LEGACY_PROXY_UNITS,
        "note": (
            "No DM particle or recoil amplitude is specified. The supplied "
            "detector projection cannot be compared with a cm^6/s^4 proxy."
        ),
        "routing": {
            "positive_signal_at_um_mass": (
                "Unsupported: no UM DM mass or scattering prediction is defined; "
                "a positive signal cannot confirm or refute a missing prediction."
            ),
            "null_result": (
                "Unsupported: a null result cannot confirm or refute "
                "a missing UM direct-detection prediction."
            ),
        },
    }


def dm_detection_preregistration_report() -> Dict[str, object]:
    """Full Pillar 290 dark matter detection preregistration report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "kk_graviton_sigma_cm2": None,
        "legacy_kk_graviton_proxy_cm6_s4": legacy_kk_graviton_dimensional_proxy(),
        "legacy_proxy_units": LEGACY_PROXY_UNITS,
        "verdict": "UNSUPPORTED",
        "lz_year2_limit": lz_year2_exclusion_limit(),
        "consistency": consistency_verdict(),
        "lz_year3": lz_year3_projection(),
    }
