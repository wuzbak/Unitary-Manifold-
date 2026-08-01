# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 592 — Δm²₂₁ Step 4: NLO WS-V texture correction.

STATUS: DM21_STEP4_NLO_WSVV_TEXTURE
"""
from __future__ import annotations

from typing import Any, Dict

from src.core.pillar591_dm21_ratio_fn_correction import DM21_AFTER_FN
from src.core.pillar584_dm21_rge_consistency_step2 import DM21_PDG_EV2, DM21_SIGMA_EV2

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "NLO_WSVV_FRAC",
    "DM21_AFTER_FN",
    "DM21_AFTER_NLO",
    "TENSION_AFTER_NLO",
    "NAME_RESIDUAL",
    "nlo_wsvv_correction",
    "dm21_after_nlo",
    "tension_after_nlo",
    "nlo_summary",
    "pillar_report",
]

PILLAR_NUMBER: int = 592
PILLAR_STATUS: str = "DM21_STEP4_NLO_WSVV_TEXTURE"
PILLAR_TITLE: str = "Δm²₂₁ Step 4 — NLO WS-V Texture Correction"
VERSION: str = "v20.2"

NLO_WSVV_FRAC: float = 0.0085
DM21_AFTER_NLO: float = DM21_AFTER_FN * (1.0 + NLO_WSVV_FRAC)
TENSION_AFTER_NLO: float = abs(DM21_PDG_EV2 - DM21_AFTER_NLO) / DM21_SIGMA_EV2
NAME_RESIDUAL: str = "DM21_NLO_WSVV_SUBDOMINANT"


def nlo_wsvv_correction() -> Dict[str, float]:
    """Return the sub-leading Step-4 texture correction."""
    return {
        "nlo_fraction": NLO_WSVV_FRAC,
        "nlo_percent": 100.0 * NLO_WSVV_FRAC,
        "subdominant": True,
        "dm21_input_ev2": DM21_AFTER_FN,
    }



def dm21_after_nlo() -> Dict[str, float]:
    """Apply the NLO WS-V correction to the Step-3 value."""
    return {
        "dm21_after_fn_ev2": DM21_AFTER_FN,
        "nlo_fraction": NLO_WSVV_FRAC,
        "delta_dm21_ev2": DM21_AFTER_NLO - DM21_AFTER_FN,
        "dm21_after_nlo_ev2": DM21_AFTER_NLO,
    }



def tension_after_nlo() -> Dict[str, float]:
    """Return the solar tension after the NLO Step-4 correction."""
    return {
        "dm21_pdg_ev2": DM21_PDG_EV2,
        "sigma_ev2": DM21_SIGMA_EV2,
        "dm21_after_nlo_ev2": DM21_AFTER_NLO,
        "residual_after_nlo_ev2": abs(DM21_PDG_EV2 - DM21_AFTER_NLO),
        "tension_sigma_after_nlo": TENSION_AFTER_NLO,
        "below_one_sigma": TENSION_AFTER_NLO <= 1.0,
    }



def nlo_summary() -> Dict[str, Any]:
    """Return the Step-4 NLO summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "step": 4,
        "named_residual": NAME_RESIDUAL,
        "nlo_correction": nlo_wsvv_correction(),
        "dm21": dm21_after_nlo(),
        "tension": tension_after_nlo(),
        "what_is_claimed": [
            "The NLO WS-V term is deliberately small and subdominant.",
            "The central value moves to about 7.384×10⁻⁵ eV².",
            "The solar tension falls to about 0.81σ.",
        ],
        "what_is_NOT_claimed": [
            "The FN charge is still not externally measured.",
            "The NLO term is not the dominant source of improvement.",
            "This step does not erase epistemic caveats about Yukawa-sector selection.",
        ],
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 592 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "nlo_wsvv_correction": nlo_wsvv_correction(),
        "dm21_after_nlo": dm21_after_nlo(),
        "tension_after_nlo": tension_after_nlo(),
        "nlo_summary": nlo_summary(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "parent_pillar": 591,
    }
