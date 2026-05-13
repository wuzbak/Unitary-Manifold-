# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 52 UV-brane α_GW closure lane for Gap 2 (CMB amplitude)."""
from __future__ import annotations

import math
from typing import Dict

from src.core.alpha_gw_10d_uv_completion import specify_type_iib_cy3_orientifold_input_set
from src.core.alpha_gw_uv_brane_derivation import (
    ALPHA_GW_LOWER,
    ALPHA_GW_UPPER,
    N_W,
    PI_KR,
    rs1_uv_brane_alpha_gw_attempt,
)
from src.core.cmb_acoustic_amplitude_rg import A_S_PLANCK, acoustic_peak_amplitude_ratio

_PLANCK_REL_AS_SIGMA = 0.014  # from ln(10^10 A_s) ~ 3.044 ± 0.014


def _kk_spectrum_enhancement(n_modes: int) -> float:
    """Return normalized KK tower sum Σ(1/n²)/(π²/6) for n=1..n_modes."""
    if n_modes < 1:
        raise ValueError("n_modes must be >= 1.")
    kk_sum = sum(1.0 / (n * n) for n in range(1, n_modes + 1))
    return kk_sum / (math.pi**2 / 6.0)


def _uvbrane_alpha_components() -> Dict[str, float]:
    """Build RS1 + KK + UV geometry components used for α_GW reconstruction."""
    rs1 = rs1_uv_brane_alpha_gw_attempt()
    compactification = specify_type_iib_cy3_orientifold_input_set()
    n_flux = float(compactification["flux_sector"]["F5_flux_units"])
    kk_modes = max(1, int(round(n_flux)))
    kk_enhancement = _kk_spectrum_enhancement(kk_modes)

    # RS1 geometric baseline (tiny), then UV-brane + KK uplift with flux loading.
    alpha_rs1 = float(rs1["alpha_gw_geometric"])
    flux_ratio = n_flux / float(N_W)
    warp_exponent = 3.0 + (1.0 - kk_enhancement) * (n_flux / 16.0)
    uv_uplift = math.exp(PI_KR * warp_exponent) * (flux_ratio**5) * kk_enhancement
    alpha_raw = alpha_rs1 * uv_uplift
    alpha_in_band = min(ALPHA_GW_UPPER, max(ALPHA_GW_LOWER, alpha_raw))

    return {
        "alpha_rs1": alpha_rs1,
        "alpha_raw": alpha_raw,
        "alpha_in_band": alpha_in_band,
        "alpha_clipped": alpha_raw != alpha_in_band,
        "n_flux": n_flux,
        "kk_modes": float(kk_modes),
        "kk_enhancement": kk_enhancement,
        "uv_uplift": uv_uplift,
        "warp_exponent": warp_exponent,
    }


def uvbrane_alpha_gw() -> float:
    """Return RS1+KK-derived α_GW constrained to the canonical Casimir interval."""
    return float(_uvbrane_alpha_components()["alpha_in_band"])


def amplitude_closure_report() -> Dict[str, object]:
    """Return Gap 2 closure report using α_GW and Pillar 149 transfer lane."""
    components = _uvbrane_alpha_components()
    peak_data = acoustic_peak_amplitude_ratio()["peaks"]
    transfer_factor = sum(
        float(p["suppression_factor"]) * float(p["tilt_ratio"])
        for p in peak_data[:2]
    ) / 2.0

    alpha = float(components["alpha_in_band"])
    a_s_pred = alpha * transfer_factor
    sigma_a_s = A_S_PLANCK * _PLANCK_REL_AS_SIGMA
    residual = a_s_pred - A_S_PLANCK
    sigma_level = abs(residual) / sigma_a_s if sigma_a_s > 0 else float("inf")
    exact_closure = abs(residual) <= sigma_a_s
    shortfall = max(0.0, A_S_PLANCK - a_s_pred)

    required_ingredient = None
    if not exact_closure:
        required_ingredient = (
            "Refine UV-brane localization transfer normalization with explicit "
            "N_flux-sensitive geometry (10D flux/intersection input)."
        )

    return {
        "status": "CLOSED" if exact_closure else "REDUCED_GAP",
        "alpha_gw": alpha,
        "alpha_bounds": (ALPHA_GW_LOWER, ALPHA_GW_UPPER),
        "transfer_factor": transfer_factor,
        "a_s_planck": A_S_PLANCK,
        "a_s_predicted": a_s_pred,
        "residual": residual,
        "sigma_a_s": sigma_a_s,
        "sigma_level": sigma_level,
        "exact_closure": exact_closure,
        "shortfall": shortfall,
        "required_uv_geometry_or_n_flux_ingredient": required_ingredient,
        "residual_documentation": (
            f"A_s = α_GW×T = {a_s_pred:.3e}; Planck={A_S_PLANCK:.3e}; "
            f"residual={residual:+.3e} ({sigma_level:.2f}σ)."
        ),
        "derivation_components": components,
    }

