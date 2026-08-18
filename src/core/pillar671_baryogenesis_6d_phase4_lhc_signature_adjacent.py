# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 671 — Baryogenesis 6D Phase 4 LHC signature.

STATUS: BARYOGENESIS_PHASE4_LHC_SIGNATURE_PREREGISTERED

Background
----------
This adjacent-track pillar preregisters the collider-facing consequence of the
6D baryogenesis lane.  It records the Drell-Yan production benchmark, the
HL-LHC event estimate, and the trigger rule that promotes the search to Tier 1
priority if the nEDM@SNS signal exceeds the stated threshold.
"""
from __future__ import annotations

from typing import Any, Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "M_SIGMA_GEV",
    "SQRT_S_TEV",
    "SIGMA_DRELL_YAN_FB",
    "LUMINOSITY_HLLHC_AB",
    "N_EVENTS_HLLHC",
    "M_SIGMA_WINDOW_LOW",
    "M_SIGMA_WINDOW_HIGH",
    "D_N_TRIGGER_ECM",
    "D_N_NLO_ECM",
    "LHC_PRIORITY",
    "PYTHIA8_REQUIRED",
    "SIGNAL",
    "drell_yan_production",
    "lhc_priority_preregistration",
    "pillar_report",
]

PILLAR_NUMBER: int = 671
PILLAR_STATUS: str = "BARYOGENESIS_PHASE4_LHC_SIGNATURE_PREREGISTERED"
PILLAR_TITLE: str = "Baryogenesis 6D Phase 4 — LHC Signature"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = True

M_SIGMA_GEV: float = 650.0
SQRT_S_TEV: float = 13.6
SIGMA_DRELL_YAN_FB: float = 0.4
LUMINOSITY_HLLHC_AB: float = 3.0
N_EVENTS_HLLHC: float = SIGMA_DRELL_YAN_FB * LUMINOSITY_HLLHC_AB * 1000.0
M_SIGMA_WINDOW_LOW: float = 310.0
M_SIGMA_WINDOW_HIGH: float = 780.0
D_N_TRIGGER_ECM: float = 5e-27
D_N_NLO_ECM: float = 7.82e-27
LHC_PRIORITY: str = (
    "TIER_1_PRIORITY" if D_N_NLO_ECM >= D_N_TRIGGER_ECM else "MONITOR"
)
PYTHIA8_REQUIRED: bool = True
SIGNAL: str = "prompt_charged_tracks_plus_missing_ET"
SNS_DATE: str = "2028"
HLLHC_TIMELINE: str = "HL-LHC_Run"


def drell_yan_production() -> Dict[str, Any]:
    """Return the benchmark Drell-Yan production summary."""
    return {
        "m_sigma_gev": M_SIGMA_GEV,
        "sqrt_s_tev": SQRT_S_TEV,
        "sigma_drell_yan_fb": SIGMA_DRELL_YAN_FB,
        "coupling_mechanism": "electroweak_drell_yan_pair_production",
        "n_events_hllhc": N_EVENTS_HLLHC,
        "signal": SIGNAL,
        "pythia8_required": PYTHIA8_REQUIRED,
        "honest_residual": (
            "Full detector-level acceptance and background estimation still "
            "require Pythia8 / experimental simulation outside CI."
        ),
    }


def lhc_priority_preregistration() -> Dict[str, Any]:
    """Return the pre-registered LHC-priority trigger condition."""
    return {
        "d_n_trigger_ecm": D_N_TRIGGER_ECM,
        "d_n_nlo_ecm": D_N_NLO_ECM,
        "d_n_exceeds_trigger": D_N_NLO_ECM >= D_N_TRIGGER_ECM,
        "lhc_priority": LHC_PRIORITY,
        "sns_date": SNS_DATE,
        "hllhc_timeline": HLLHC_TIMELINE,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 671 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "drell_yan_production": drell_yan_production(),
        "lhc_priority_preregistration": lhc_priority_preregistration(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
