# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/climate/feedback.py
========================
Climate Feedbacks as φ-Field Amplification — Pillar 22.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30


def climate_sensitivity_phi(delta_F: float, delta_T: float) -> float:
    """Equilibrium climate sensitivity: ΔT per unit forcing.

    ECS = ΔT / ΔF   K (W m⁻²)⁻¹

    Parameters
    ----------
    delta_F : float — radiative forcing W m⁻² (must be ≠ 0)
    delta_T : float — equilibrium temperature change K

    Returns
    -------
    ECS : float — climate sensitivity
    """
    if abs(delta_F) < _EPS:
        raise ValueError(f"delta_F must be non-zero, got {delta_F!r}")
    return float(delta_T / delta_F)


def ice_albedo_feedback_phi(delta_T: float, alpha_ice: float = 0.6,
                             alpha_ocean: float = 0.06,
                             ice_fraction: float = 0.1) -> float:
    """Ice-albedo feedback forcing from ice loss.

    ΔF_ice = ice_fraction × (α_ocean − α_ice) × S / 4   W m⁻²
    (simplified, S = 1361 W m⁻²)

    Parameters
    ----------
    delta_T      : float — temperature change (K; controls ice fraction loss)
    alpha_ice    : float — ice albedo (default 0.6)
    alpha_ocean  : float — open ocean albedo (default 0.06)
    ice_fraction : float — initial ice fraction (default 0.1, ∈ [0,1])

    Returns
    -------
    delta_F : float — additional forcing W m⁻²
    """
    if not (0.0 <= ice_fraction <= 1.0):
        raise ValueError(f"ice_fraction must be in [0,1], got {ice_fraction!r}")
    S = 1361.0
    loss_fraction = min(ice_fraction, max(0.0, 0.05 * delta_T))
    return float(loss_fraction * (alpha_ocean - alpha_ice) * S / 4.0)


def water_vapor_phi(delta_T: float, wv_feedback: float = 1.8) -> float:
    """Water-vapour feedback additional forcing per degree of warming.

    ΔF_WV = wv_feedback × ΔT   W m⁻²

    Parameters
    ----------
    delta_T     : float — temperature change K
    wv_feedback : float — water-vapour feedback factor W m⁻² K⁻¹ (default 1.8)

    Returns
    -------
    delta_F_WV : float — water-vapour forcing W m⁻²
    """
    return float(wv_feedback * delta_T)


def permafrost_feedback_phi(phi_permafrost: float, delta_T: float,
                             thaw_rate: float = 0.03) -> float:
    """Permafrost carbon feedback forcing.

    ΔF_pf = thaw_rate × phi_permafrost × max(0, delta_T)

    Parameters
    ----------
    phi_permafrost : float — permafrost C store (GtC, must be ≥ 0)
    delta_T        : float — warming (K)
    thaw_rate      : float — fraction thawed per K (default 0.03, must be ≥ 0)

    Returns
    -------
    delta_F : float — feedback forcing W m⁻²
    """
    if phi_permafrost < 0.0:
        raise ValueError(f"phi_permafrost must be ≥ 0, got {phi_permafrost!r}")
    if thaw_rate < 0.0:
        raise ValueError(f"thaw_rate must be ≥ 0, got {thaw_rate!r}")
    return float(thaw_rate * phi_permafrost * max(0.0, delta_T))


def cloud_phi_feedback(delta_T: float, cloud_feedback: float = -0.42) -> float:
    """Net cloud φ feedback (slightly negative overall).

    ΔF_cloud = cloud_feedback × ΔT   W m⁻²

    Parameters
    ----------
    delta_T       : float — warming (K)
    cloud_feedback: float — feedback parameter W m⁻² K⁻¹ (default -0.42)

    Returns
    -------
    delta_F : float — cloud feedback forcing
    """
    return float(cloud_feedback * delta_T)


def tipping_point_phi(phi_current: float, phi_tipping: float,
                       B_noise: float) -> float:
    """Proximity to tipping point as noise-normalised distance.

    proximity = (phi_tipping − phi_current) / (B_noise + ε)

    proximity < 0 → tipping point has been crossed.

    Parameters
    ----------
    phi_current : float — current system φ
    phi_tipping : float — critical tipping-point φ
    B_noise     : float — system noise (must be ≥ 0)

    Returns
    -------
    proximity : float — distance to tipping (negative = tipped)
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float((phi_tipping - phi_current) / (B_noise + _EPS))


def feedback_amplification_phi(forcing_direct: float,
                                 total_feedback: float) -> float:
    """Total temperature response including feedback amplification.

    ΔT_total = ΔF_direct / (1 − total_feedback)

    Parameters
    ----------
    forcing_direct : float — direct radiative forcing K
    total_feedback : float — net feedback factor (must be < 1 for stability)

    Returns
    -------
    delta_T_total : float — amplified warming
    """
    if total_feedback >= 1.0:
        raise ValueError(f"total_feedback must be < 1 for stability, got {total_feedback!r}")
    return float(forcing_direct / (1.0 - total_feedback))


def radiative_forcing_phi(delta_C: float, alpha: float = 5.35) -> float:
    """Radiative forcing from an incremental CO₂ change.

    ΔF = alpha × ln(1 + delta_C / C_ref)   (linearised for small delta_C)

    Parameters
    ----------
    delta_C : float — CO₂ change in ppm
    alpha   : float — forcing coefficient (default 5.35 W m⁻²)

    Returns
    -------
    delta_F : float — radiative forcing W m⁻²
    """
    return float(alpha * math.log1p(abs(delta_C) / (280.0 + _EPS)) * (1 if delta_C >= 0 else -1))


def climate_phi_memory(phi_ocean: float, phi_atmosphere: float,
                        coupling: float) -> float:
    """Ocean heat uptake as long-memory φ buffer.

    phi_mem = coupling × phi_ocean + (1 − coupling) × phi_atmosphere

    Parameters
    ----------
    phi_ocean      : float — ocean heat content φ
    phi_atmosphere : float — atmospheric temperature φ
    coupling       : float — ocean-atmosphere coupling ∈ [0, 1]

    Returns
    -------
    phi_mem : float — effective system memory φ
    """
    if not (0.0 <= coupling <= 1.0):
        raise ValueError(f"coupling must be in [0,1], got {coupling!r}")
    return float(coupling * phi_ocean + (1.0 - coupling) * phi_atmosphere)


def equilibrium_phi_temperature(phi_forcing: float,
                                  lambda_feedback: float = 0.8) -> float:
    """Equilibrium surface temperature response to forcing.

    ΔT_eq = phi_forcing / lambda_feedback

    Parameters
    ----------
    phi_forcing    : float — net radiative forcing W m⁻²
    lambda_feedback: float — climate feedback parameter W m⁻² K⁻¹ (must be > 0)

    Returns
    -------
    delta_T_eq : float — equilibrium warming K
    """
    if lambda_feedback <= 0.0:
        raise ValueError(f"lambda_feedback must be > 0, got {lambda_feedback!r}")
    return float(phi_forcing / lambda_feedback)
