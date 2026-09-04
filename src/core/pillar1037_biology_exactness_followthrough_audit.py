# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1037 — biology exactness follow-through audit."""

from __future__ import annotations

from itertools import product
from typing import Any, Dict

from src.biology.critical_hydration_kernels import (
    critical_hydration_kernel_report,
    critical_water_volume_fraction,
    water_mass_ratio_from_volume_fraction,
)
from src.biology.hox_kk_alignment import hox_report

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "biology_exactness_followthrough_audit",
    "pillar1037_summary",
]

PILLAR_NUMBER: int = 1037
PILLAR_GATE: str = "BIOLOGY_EXACTNESS_FOLLOWTHROUGH_AUDIT"
PILLAR_STATUS: str = "BIOLOGY_EXACTNESS_FOLLOWTHROUGH_AUDIT_COMPLETE"


def _hydration_window() -> Dict[str, float]:
    volume_fractions = []
    mass_ratios = []
    for eps_water, eps_dry, rho_dry in product((78.0, 80.0, 82.0), (4.0, 4.5, 5.0), (1.2, 1.3, 1.4)):
        fraction = critical_water_volume_fraction(eps_water=eps_water, eps_dry=eps_dry)
        volume_fractions.append(fraction)
        mass_ratios.append(water_mass_ratio_from_volume_fraction(fraction, rho_dry=rho_dry))
    return {
        "volume_fraction_min": min(volume_fractions),
        "volume_fraction_max": max(volume_fractions),
        "mass_ratio_min": min(mass_ratios),
        "mass_ratio_max": max(mass_ratios),
    }


def biology_exactness_followthrough_audit() -> Dict[str, Any]:
    """Return Sprint BX follow-through on HOX empirical and hydration lanes."""
    hox = hox_report()
    hydration = critical_hydration_kernel_report()
    hydration_window = _hydration_window()
    volume_spread = hydration_window["volume_fraction_max"] - hydration_window["volume_fraction_min"]
    mass_ratio_spread = hydration_window["mass_ratio_max"] - hydration_window["mass_ratio_min"]
    valid = bool(
        "ADJACENT TRACK" in hox["pillar_classification"]
        and hydration["exact_kernel_status"] == "DERIVED_STRUCTURAL"
        and hydration["model_dependent_prediction_status"] == "FALSIFIABLE_PREDICTION"
        and volume_spread > 0.0
        and mass_ratio_spread > 0.0
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "hox_empirical_lane": {
            "tier1_overall": bool(hox["tier1_overall"]),
            "pillar_classification": hox["pillar_classification"],
            "promotion_condition": hox["promotion_condition"],
        },
        "hydration_exact_kernel": hydration["exact_kernel"],
        "hydration_model_dependence": {
            "status": hydration["model_dependent_prediction_status"],
            "window": hydration_window,
            "volume_fraction_spread": volume_spread,
            "mass_ratio_spread": mass_ratio_spread,
        },
        "non_promotions_retained": [
            "HOX empirical lane remains adjacent-track",
            "Hydration water-fraction and mass-ratio outputs remain model-dependent",
        ],
        "interpretation": (
            "Sprint BX follows through on biology exactness by hardening the HOX empirical "
            "audit packet and by turning hydration medium dependence into an explicit interval "
            "surface instead of a stronger claim."
        ),
    }


_REPORT = biology_exactness_followthrough_audit()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1037_summary() -> Dict[str, Any]:
    """Return concise Pillar 1037 summary."""
    report = biology_exactness_followthrough_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Biology Exactness Follow-Through Audit",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "tier1_overall": report["hox_empirical_lane"]["tier1_overall"],
        "model_dependence_window_reported": report["hydration_model_dependence"]["volume_fraction_spread"] > 0.0,
    }
