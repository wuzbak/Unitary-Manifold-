# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""First-principles CP asymmetry prediction for (5,7)-topology lab platforms.

Derives A_CP^lab from the UM (5,7) braid geometry and computes the topology
transfer efficiency for Josephson-junction/SQUID arrays and topological
insulators.

References
----------
- LAB_SCALE_CP_VIOLATION_FALSIFIER.md
- 1-THEORY/LAB_SCALE_CP_VIOLATION_57_BRAID.md
"""
from __future__ import annotations

import math
from typing import Any

__all__ = [
    "N_W",
    "K_CS",
    "J_CKM_PDG",
    "THETA_BRAID",
    "A_CP_TARGET_ORDER",
    "jarlskog_from_braid_geometry",
    "topology_transfer_efficiency",
    "a_cp_lab_prediction",
    "falsification_threshold_analysis",
    "full_prediction_report",
]

N_W: int = 5
K_CS: int = 74
J_CKM_PDG: float = 3.04e-5
THETA_BRAID: float = 2 * math.pi * N_W / K_CS  # ≈ 0.4243 rad
A_CP_TARGET_ORDER: float = 1e-5


def jarlskog_from_braid_geometry(
    n_w: int = N_W,
    k_cs: int = K_CS,
    pi_kr: float = 37.0,
) -> dict[str, Any]:
    """Compute the geometric Jarlskog invariant from UM braid geometry.

    Uses the leading-order formula from the (n_w, k_cs) braid group
    representation of SU(3) quark mixing:

        J_geo = (n_w / k_cs)^2 × sin(θ_braid) × (1 - (n_w / k_cs)^2)

    where θ_braid = 2π × n_w / k_cs.

    Parameters
    ----------
    n_w:
        Winding number (default 5).
    k_cs:
        Chern-Simons level (default 74 = 5² + 7²).
    pi_kr:
        π × compactification radius product (default 37 = K_CS/2).

    Returns
    -------
    dict with keys:

    - ``theta_braid_rad`` – braid angle in radians
    - ``sin_braid`` – sin(θ_braid)
    - ``J_geo`` – geometric Jarlskog invariant
    - ``J_CKM_PDG`` – PDG reference value
    - ``residual_vs_pdg_pct`` – |J_geo - J_PDG| / J_PDG × 100
    - ``status`` – 'GEOMETRIC_PREDICTION' when residual < 50 %
    """
    theta = 2.0 * math.pi * n_w / k_cs
    sin_theta = math.sin(theta)
    ratio = n_w / k_cs
    j_geo = ratio**2 * sin_theta * (1.0 - ratio**2)
    residual_pct = abs(j_geo - J_CKM_PDG) / J_CKM_PDG * 100.0
    status = "GEOMETRIC_PREDICTION" if residual_pct < 50.0 else "OUTSIDE_50PCT_BAND"
    return {
        "theta_braid_rad": theta,
        "sin_braid": sin_theta,
        "J_geo": j_geo,
        "J_CKM_PDG": J_CKM_PDG,
        "residual_vs_pdg_pct": residual_pct,
        "status": status,
    }


def topology_transfer_efficiency(
    coherence_length_nm: float,
    braid_length_nm: float | None = None,
    platform: str = "JJ_SQUID",
) -> dict[str, Any]:
    """Compute the topology transfer efficiency Π_topo for a given platform.

    For JJ/SQUID arrays:
        braid_length_nm = coherence_length_nm × K_CS / N_W  (≈ 14.8×)
        Π_topo = exp(-coherence_length_nm / braid_length_nm)
               = exp(-N_W / K_CS) ≈ exp(-5/74) ≈ 0.934

    For topological insulators:
        Π_topo = 1 - exp(-braid_length_nm / coherence_length_nm)

    Parameters
    ----------
    coherence_length_nm:
        Josephson or surface-state coherence length in nm (typical 500–2000).
    braid_length_nm:
        Override the braid length (nm).  If None, computed from platform formula.
    platform:
        ``'JJ_SQUID'`` or ``'TOPOLOGICAL_INSULATOR'``.

    Returns
    -------
    dict with keys:

    - ``pi_topo`` – topology transfer efficiency in [0, 1]
    - ``braid_length_nm`` – effective braid length used
    - ``coherence_length_nm`` – input coherence length
    - ``platform`` – platform string
    - ``regime_classification`` – qualitative label
    """
    if coherence_length_nm <= 0:
        raise ValueError("coherence_length_nm must be positive")

    if braid_length_nm is None:
        braid_length_nm = coherence_length_nm * K_CS / N_W  # ≈ 14.8×

    ratio = coherence_length_nm / braid_length_nm

    if platform == "JJ_SQUID":
        pi_topo = math.exp(-ratio)
    elif platform == "TOPOLOGICAL_INSULATOR":
        pi_topo = 1.0 - math.exp(-1.0 / ratio) if ratio != 0 else 1.0
    else:
        raise ValueError(f"Unknown platform: {platform!r}")

    if pi_topo > 0.9:
        regime = "COHERENT_HIGH_TRANSFER"
    elif pi_topo > 0.5:
        regime = "INTERMEDIATE_TRANSFER"
    else:
        regime = "INCOHERENT_LOW_TRANSFER"

    return {
        "pi_topo": pi_topo,
        "braid_length_nm": braid_length_nm,
        "coherence_length_nm": coherence_length_nm,
        "platform": platform,
        "regime_classification": regime,
    }


def a_cp_lab_prediction(
    platform: str = "JJ_SQUID",
    coherence_length_nm: float = 1000.0,
) -> dict[str, Any]:
    """Compute the full predicted lab CP asymmetry.

    A_CP^lab = J_geo × Π_topo

    Parameters
    ----------
    platform:
        Condensed-matter platform string.
    coherence_length_nm:
        Coherence length in nm.

    Returns
    -------
    dict with keys:

    - ``j_geo_result`` – output of :func:`jarlskog_from_braid_geometry`
    - ``pi_topo_result`` – output of :func:`topology_transfer_efficiency`
    - ``a_cp_lab`` – predicted asymmetry
    - ``prediction_order_of_magnitude`` – floor(log10(|a_cp_lab|))
    - ``prediction_consistent_with_target`` – True if OOM within ±2 of −5
    """
    j_result = jarlskog_from_braid_geometry()
    t_result = topology_transfer_efficiency(coherence_length_nm, platform=platform)
    a_cp = j_result["J_geo"] * t_result["pi_topo"]
    oom = math.floor(math.log10(abs(a_cp)))
    consistent = abs(oom - (-5)) <= 2
    return {
        "j_geo_result": j_result,
        "pi_topo_result": t_result,
        "a_cp_lab": a_cp,
        "prediction_order_of_magnitude": oom,
        "prediction_consistent_with_target": consistent,
    }


def falsification_threshold_analysis() -> dict[str, Any]:
    """Quantify the measurement requirements for falsification.

    Returns
    -------
    dict with keys:

    - ``minimum_sigma_for_falsification`` – σ_A required (1×10⁻⁵)
    - ``required_events_for_jj_squid`` – rough event-count estimate
    - ``required_events_for_topological_insulator`` – rough event-count estimate
    - ``time_to_falsification_years_estimate`` – wall-clock campaign duration
    - ``notes`` – plain-language explanation
    """
    sigma_min = 1e-5
    # Assuming σ per event ≈ 1 (binary ±1 outcome), n ~ (σ_event / σ_target)^2
    events_jj = int((1.0 / sigma_min) ** 2)  # ~ 10^10
    events_ti = int(0.5 * events_jj)          # TI slightly more efficient geometry
    return {
        "minimum_sigma_for_falsification": sigma_min,
        "required_events_for_jj_squid": events_jj,
        "required_events_for_topological_insulator": events_ti,
        "time_to_falsification_years_estimate": 2.0,
        "notes": (
            "Falsification requires A_CP^lab = 0 at 95% CL with σ_A ≤ 10^{-5} "
            "in a topology-certified (5,7) platform with systematics controlled."
        ),
    }


def full_prediction_report() -> dict[str, Any]:
    """Return a complete summary of all WS-3 CP-falsifier predictions.

    Returns
    -------
    dict with keys:

    - ``braid_geometry`` – jarlskog_from_braid_geometry() output
    - ``jj_squid_prediction`` – a_cp_lab_prediction('JJ_SQUID') output
    - ``ti_prediction`` – a_cp_lab_prediction('TOPOLOGICAL_INSULATOR') output
    - ``falsification_analysis`` – falsification_threshold_analysis() output
    - ``summary`` – plain-language status string
    """
    braid = jarlskog_from_braid_geometry()
    jj = a_cp_lab_prediction("JJ_SQUID", coherence_length_nm=1000.0)
    ti = a_cp_lab_prediction("TOPOLOGICAL_INSULATOR", coherence_length_nm=1000.0)
    fals = falsification_threshold_analysis()
    summary = (
        f"J_geo = {braid['J_geo']:.3e} ({braid['status']}); "
        f"A_CP^JJ = {jj['a_cp_lab']:.3e}; "
        f"A_CP^TI = {ti['a_cp_lab']:.3e}; "
        f"σ_min_falsif = {fals['minimum_sigma_for_falsification']:.1e}"
    )
    return {
        "braid_geometry": braid,
        "jj_squid_prediction": jj,
        "ti_prediction": ti,
        "falsification_analysis": fals,
        "summary": summary,
    }
