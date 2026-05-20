# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 291 — Planetary Defense / Taurid Risk UM Intersection.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Applies the CROS entropy sector framework (Pillar 237) and the φ₀/ξ_c
information-capacity ratio to the Taurid meteor complex risk assessment,
closing the loop between the `book-taurid-density-risk-2030s.md` document
and the live computational framework.

Taurid complex context:
- The Taurid meteor complex contains ~100–400 m objects (the "Taurid swarm")
  with encounter windows near the Halloween–Bonfire Night period every 2–7 yr.
- `book-taurid-density-risk-2030s.md` estimates the encounter probability.

UM frame contributions (adjacent track only):
- φ₀/ξ_c ≈ 1.618/(35/74) ≈ 3.42 serves as a dimensionless information-
  amplification capacity index.  In the CROS framework, this ratio bounds
  the effective early-warning enhancement from geometric information flow.
- The planetary-defense readiness index is scored against DART (2022
  validated), Hera (2026), and NEO Surveyor (2028) milestones.

IMPORTANT: The UM makes no hardgate physics claim about planetary defense.
This is an adjacent-track qualitative application of the CROS geometry to
real-world early-warning planning.  All risk numbers are based on standard
planetary science estimates, not derived from the 5D geometry.
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PHI_0",
    "XI_C",
    "TAURID_ANNUAL_RISK_PER_100M",
    "DART_SUCCESS_YEAR",
    "HERA_LAUNCH_YEAR",
    "NEO_SURVEYOR_LAUNCH",
    "TAURID_SWARM_DENSITY_PER_KM3",
    "separation_guard",
    "taurid_encounter_risk_score",
    "planetary_defense_readiness_index",
    "um_phi_entropy_warning_capacity",
    "cros_integration_with_taurid",
    "taurid_risk_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 291
PILLAR_TITLE: str = "Planetary Defense / Taurid Risk UM Intersection"

PHI_0: float = (1.0 + math.sqrt(5.0)) / 2.0   # golden ratio ≈ 1.618
XI_C: float = 35.0 / 74.0                     # Ξ_c ≈ 0.473

TAURID_ANNUAL_RISK_PER_100M: float = 1.0e-3   # P(Tunguska-scale) per yr per 100 m object
DART_SUCCESS_YEAR: int = 2022
HERA_LAUNCH_YEAR: int = 2026
NEO_SURVEYOR_LAUNCH: int = 2028
TAURID_SWARM_DENSITY_PER_KM3: float = 1.0e-8  # objects/km³ at 1 AU encounter


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 291."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "integrates_cros_pillar237": True,
        "real_world_application": True,
    }


def taurid_encounter_risk_score(
    object_diameter_m: float = 150.0,
    encounter_year: int = 2032,
) -> Dict[str, object]:
    """Compute a risk score for a Taurid encounter.

    Scales base annual risk by (diameter/100m)² and adjusts for available
    warning time from 2026 (current baseline).
    """
    if object_diameter_m <= 0.0:
        raise ValueError("object_diameter_m must be positive")
    base_risk = TAURID_ANNUAL_RISK_PER_100M * (object_diameter_m / 100.0) ** 2
    years_warning = max(0, encounter_year - 2026)
    detection_factor = min(1.0, years_warning / 10.0)
    residual_risk = base_risk * (1.0 - detection_factor)
    return {
        "object_diameter_m": object_diameter_m,
        "base_annual_risk": base_risk,
        "years_warning": years_warning,
        "detection_factor": detection_factor,
        "residual_risk": residual_risk,
        "verdict": "HIGH_RISK" if base_risk >= 0.01 else "MANAGEABLE",
    }


def planetary_defense_readiness_index() -> Dict[str, object]:
    """Score current planetary defense readiness (0–1 scale)."""
    detection_score = 0.70    # NEO Surveyor (2028) + existing surveys
    deflection_score = 0.60   # DART validated; Hera (2026) follow-up
    warning_score = 0.80      # International Asteroid Warning Network active
    readiness = (detection_score + deflection_score + warning_score) / 3.0
    return {
        "detection_score": detection_score,
        "deflection_score": deflection_score,
        "warning_score": warning_score,
        "readiness_index": readiness,
        "dart_validated": True,
        "hera_launch_year": HERA_LAUNCH_YEAR,
        "neo_surveyor_launch": NEO_SURVEYOR_LAUNCH,
        "assessment": "OPERATIONAL_WITH_GAPS" if readiness > 0.5 else "INSUFFICIENT",
    }


def um_phi_entropy_warning_capacity() -> Dict[str, object]:
    """Return the φ₀/ξ_c information-amplification capacity ratio."""
    capacity = PHI_0 / XI_C
    return {
        "phi_0": PHI_0,
        "xi_c": XI_C,
        "capacity_ratio": capacity,
        "interpretation": (
            "Information amplification capacity ∝ φ₀/ξ_c ≈ {:.3f} > 1.0: "
            "UM frame predicts non-trivial early-warning enhancement from "
            "geometric information flow in the CROS sector."
        ).format(capacity),
        "caveat": "Adjacent track only; no hardgate claim on planetary defense.",
    }


def cros_integration_with_taurid(sector_weight: float = 0.15) -> Dict[str, object]:
    """Integrate CROS entropy capacity with Taurid warning enhancement.

    sector_weight: fraction of CROS capacity allocated to the planetary
    early-warning sector (arbitrary; represents qualitative weighting).
    """
    if not (0.0 < sector_weight <= 1.0):
        raise ValueError("sector_weight must be in (0, 1]")
    capacity = um_phi_entropy_warning_capacity()["capacity_ratio"]
    effective_warning = capacity * sector_weight
    return {
        "sector_weight": sector_weight,
        "um_capacity_ratio": capacity,
        "effective_taurid_warning_enhancement": effective_warning,
        "status": "QUALITATIVE_ADJACENT_TRACK_ONLY",
    }


def taurid_risk_preregistration_report() -> Dict[str, object]:
    """Full Pillar 291 preregistration report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "encounter_risk_150m_2032": taurid_encounter_risk_score(150.0, 2032),
        "readiness_index": planetary_defense_readiness_index(),
        "um_capacity": um_phi_entropy_warning_capacity(),
        "cros_integration": cros_integration_with_taurid(),
    }
