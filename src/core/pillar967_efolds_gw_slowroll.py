# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 967 — N_e Derivation from GW Slow-Roll.

This pillar derives the inflationary e-fold window directly from the Unitary
Manifold predictions for n_s and r. The key result is
N_e = (r/8 + 2)/(1 - n_s), so once n_s = 0.9635 and r = 0.0315 are fixed by the
same geometry, the e-fold count is no longer an independent assumption.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

N_W: int = 5
K_CS: int = 74
PHI0: float = 1.0
N_S_UM: float = 0.9635
R_BRAIDED: float = 0.0315
PI_KR: float = K_CS / 2.0

N_E_DERIVED: float = (R_BRAIDED / 8.0 + 2.0) / (1.0 - N_S_UM)
N_E_WINDOW_LOW: float = 0.9 * N_E_DERIVED
N_E_WINDOW_HIGH: float = 1.1 * N_E_DERIVED
EPSILON_SR: float = 1.0 / (16.0 * PI_KR)
WARP_FACTOR: float = math.exp(-math.pi * K_CS / 2.0)
FIELD_RANGE_REQUIRED: float = math.sqrt(2.0 * EPSILON_SR * N_E_DERIVED)

PILLAR_STATUS: str = "EFOLDS_DERIVED_WINDOW"
PILLAR_VALID: bool = True

__all__ = [
    "K_CS",
    "N_W",
    "PHI0",
    "N_S_UM",
    "R_BRAIDED",
    "N_E_DERIVED",
    "N_E_WINDOW_LOW",
    "N_E_WINDOW_HIGH",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "ns_and_r_values",
    "efolds_from_ns_r",
    "efolds_window",
    "efolds_gw_geometry",
    "fallibility_update",
    "pillar967_summary",
]


def ns_and_r_values() -> Dict[str, object]:
    """Return the UM inflationary observables used in the derivation."""
    return {
        "n_s": N_S_UM,
        "r": R_BRAIDED,
        "source": "UM_geometry",
        "consistency_relation": "N_e = (r/8 + 2)/(1 - n_s)",
    }


def efolds_from_ns_r() -> Dict[str, object]:
    """Derive N_e from the UM n_s and r values."""
    return {
        "formula": "(r/8 + 2)/(1 - n_s)",
        "N_e": N_E_DERIVED,
        "N_e_low": N_E_WINDOW_LOW,
        "N_e_high": N_E_WINDOW_HIGH,
        "window_fraction": 0.10,
        "derived_not_assumed": True,
    }


def efolds_window() -> Dict[str, object]:
    """Return the derived e-fold window and its standard-range check."""
    return {
        "N_e_derived": N_E_DERIVED,
        "N_e_low": N_E_WINDOW_LOW,
        "N_e_high": N_E_WINDOW_HIGH,
        "standard_range": (50.0, 65.0),
        "in_standard_range": 50.0 <= N_E_DERIVED <= 65.0,
        "window_overlaps_standard_range": N_E_WINDOW_HIGH >= 50.0 and N_E_WINDOW_LOW <= 65.0,
    }


def efolds_gw_geometry() -> Dict[str, object]:
    """Return a GW/radion geometry consistency check for the derived window."""
    return {
        "pi_k_R": PI_KR,
        "epsilon_sr": EPSILON_SR,
        "warp_factor": WARP_FACTOR,
        "field_range_required": FIELD_RANGE_REQUIRED,
        "phi0_available": PHI0,
        "field_range_within_phi0": FIELD_RANGE_REQUIRED <= PHI0,
        "geometric_consistency": FIELD_RANGE_REQUIRED <= PHI0 and WARP_FACTOR < 1.0e-40,
        "interpretation": "GW geometry supports the derived 55±5 e-fold window without introducing a new parameter",
    }


def fallibility_update() -> Dict[str, object]:
    """Return the Admission 11 status upgrade."""
    return {
        "section": "Admission 11 (§XIII.1)",
        "previous_status": "STANDARD_ASSUMPTION",
        "new_status": "DERIVED_WINDOW",
        "key_result": (
            f"N_e = (r/8 + 2)/(1-n_s) = {N_E_DERIVED:.6f}, giving "
            f"N_e ∈ [{N_E_WINDOW_LOW:.6f}, {N_E_WINDOW_HIGH:.6f}] from UM-derived n_s and r."
        ),
        "pillar": 967,
        "pillar_status": PILLAR_STATUS,
    }


def pillar967_summary() -> Dict[str, object]:
    """Return the complete Pillar 967 summary."""
    observables = ns_and_r_values()
    derived = efolds_from_ns_r()
    window = efolds_window()
    geometry = efolds_gw_geometry()
    fallibility = fallibility_update()
    return {
        "pillar": 967,
        "title": "N_e Derivation from GW Slow-Roll",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "observables": observables,
        "derived_efolds": derived,
        "window": window,
        "gw_geometry": geometry,
        "fallibility_update": fallibility,
        "derivation_chain": [
            "UM geometry fixes n_s = 0.9635 and r = 0.0315",
            "Slow-roll relation gives N_e = (r/8 + 2)/(1 - n_s)",
            "This yields N_e ≈ 54.9 and a conservative ±10% window",
            "The resulting interval overlaps the standard horizon-solving range",
            "Admission 11 upgrades from assumption to derived window",
        ],
    }
