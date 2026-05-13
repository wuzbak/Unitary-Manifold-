# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
5D Peccei-Quinn axion mechanism — Gap SC3 closure.

Derives the 5D PQ field profile in the RS1 (Randall-Sundrum) background,
computing the axion decay constant, mass, coupling to photons, and effective
strong-CP angle.

Theory basis:
- RS1 background: ds² = e^{-2k|y|}η_μν dx^μ dx^ν + dy²
- Warp factor suppression: M_Pl_eff = M_Pl × e^{-πkR}
- f_a ~ M_Pl × e^{-πkR}  (UV-brane localized PQ field)
- m_a² ~ Λ_QCD⁴ / f_a²  (QCD instanton potential → m_a * f_a ≈ Λ_QCD²)
- g_{aγγ} = α_EM / (2π f_a)  (generic axion-photon coupling)
- θ_eff ~ e^{-πkR} / N_W  (residual strong-CP angle, warp-suppressed)

Physical context:
  With the canonical PI_KR = 37.0 (from solar_splitting_6dplus), the warp
  factor exp(-37) ≈ 8.5e-17 drives f_a ≈ 208 GeV — well below the classic
  astrophysical axion window [1e9, 1e12] GeV.  The strong-CP closure does
  NOT rely on f_a landing in that window; it relies on θ_eff being
  exponentially suppressed below the PDG bound 1e-10, which IS satisfied:
  θ_eff ≈ 1.7e-17 ≪ 1e-10.  The astrophysical-window flag is therefore False
  at the canonical point but the PDG bound is satisfied by many orders of
  magnitude.  See strong_cp_pq_z2_closure.py for the full gate report.

Constants:
    N_W      = 5            winding number (Planck nₛ-selected)
    K_CS     = 74           CS level = 5² + 7²
    PI_KR    = 37.0         π × k × R (from solar_splitting_6dplus)
    M_PL_GEV = 2.435e18     reduced Planck mass in GeV
    LAMBDA_QCD_GEV = 0.2    QCD scale in GeV
    ALPHA_EM = 1/137.036    fine-structure constant

Export API:
    pq_5d_params(k, R, n_w)  → dict with f_a, m_a, g_agg, theta_eff, …
    canonical_5d_pq_params()  → pq_5d_params at (k=0.1, R=PI_KR/(π·0.1))
"""
from __future__ import annotations

import math
from typing import Dict

from src.sixd.solar_splitting_6dplus import K_CS, N_W, PI_KR

__all__ = [
    "N_W",
    "K_CS",
    "PI_KR",
    "M_PL_GEV",
    "LAMBDA_QCD_GEV",
    "ALPHA_EM",
    "pq_5d_params",
    "canonical_5d_pq_params",
]

M_PL_GEV: float = 2.435e18       # reduced Planck mass [GeV]
LAMBDA_QCD_GEV: float = 0.2       # QCD confinement scale [GeV]
ALPHA_EM: float = 1.0 / 137.036   # fine-structure constant (dimensionless)


def pq_5d_params(k: float, R: float, n_w: int = N_W) -> Dict[str, object]:
    """Compute 5D PQ axion parameters for a given RS1 warp geometry.

    Parameters
    ----------
    k:
        Warping rate [units of M_Pl or 1/length]; determines exp(-πkR).
    R:
        Orbifold radius; together with k sets the warp factor.
    n_w:
        Winding number (PQ charge normalisation).  Defaults to N_W = 5.

    Returns
    -------
    dict with keys
        f_a_GeV                  : axion decay constant [GeV]
        m_a_eV                   : axion mass [eV]
        g_agg_GeV_inv            : axion-photon coupling [GeV⁻¹]
        theta_eff                : effective strong-CP angle (dimensionless)
        pi_kr                    : π k R (dimensionless warp exponent)
        k, R, n_w                : input parameters echoed back
        f_a_in_astrophysical_window : True if 1e9 ≤ f_a ≤ 1e12 GeV
        theta_eff_below_pdg_bound   : True if θ_eff < 1e-10
    """
    pi_kr = math.pi * k * R

    # Warp-suppressed PQ scale (UV-brane localised field)
    f_a = M_PL_GEV * math.exp(-pi_kr)

    # QCD axion mass from instanton potential: m_a · f_a = Λ_QCD²
    m_a_gev = LAMBDA_QCD_GEV**2 / f_a

    # Convert mass to eV (1 GeV = 1e9 eV)
    m_a_ev = m_a_gev * 1e9

    # Axion-photon coupling [GeV⁻¹]
    g_agg = ALPHA_EM / (2.0 * math.pi * f_a)

    # Residual strong-CP angle (warp-exponentially suppressed)
    theta_eff = math.exp(-pi_kr) / float(n_w)

    return {
        "f_a_GeV": f_a,
        "m_a_eV": m_a_ev,
        "g_agg_GeV_inv": g_agg,
        "theta_eff": theta_eff,
        "pi_kr": pi_kr,
        "k": k,
        "R": R,
        "n_w": n_w,
        "f_a_in_astrophysical_window": (1e9 <= f_a <= 1e12),
        "theta_eff_below_pdg_bound": (theta_eff < 1e-10),
    }


def canonical_5d_pq_params() -> Dict[str, object]:
    """PQ parameters at the canonical Unitary Manifold point.

    Uses k = 0.1 and R chosen so that π k R = PI_KR = 37.0.
    """
    k = 0.1
    R = PI_KR / (math.pi * k)
    return pq_5d_params(k=k, R=R, n_w=N_W)
