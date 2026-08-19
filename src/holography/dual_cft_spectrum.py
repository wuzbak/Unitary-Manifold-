# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 775 — UM RS1 geometry to dual 4D CFT operator spectrum.

This module packages the leading holographic dictionary implied by the
Randall-Sundrum / AdS5 background already used in the Unitary Manifold.
It identifies the boundary operators sourced by the main 5D bulk fields,
estimates the CFT central charge, and records the Chern-Simons anomaly data.

Honest status
-------------
DUAL_CFT_SPECTRUM_SCAFFOLD:
    The operator assignments follow the standard AdS/CFT dictionary, the
    anomaly coefficient is fixed by K_CS, and the central charge is estimated
    at order-of-magnitude level. A full non-perturbative definition of the
    dual CFT still requires external algebraic input.
"""

from __future__ import annotations

import math
from typing import Dict, List

from ..core.qcd_geometry_primary import M_PL_GEV, m_kk_geometric

__all__ = [
    "graviton_to_cft_stresstensor",
    "kk_tower_to_cft_operators",
    "radion_to_cft_lagrangian_density",
    "cs_field_to_cft_current",
    "gauge_field_to_cft_currents",
    "cft_central_charge",
    "cs_anomaly_coefficient",
    "dual_cft_spectrum_report",
]

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

N_W: int = 5
K_CS: int = 74
PI_KR: float = 37.0
M_KK_GEV: float = m_kk_geometric(N_W, K_CS)
STRESS_TENSOR_DELTA: float = 4.0
CURRENT_DELTA: float = 3.0
FERMION_DELTA_LIGHT: float = 2.5
FERMION_DELTA_TOP: float = 2.0
_EPISTEMIC_STATUS = "DUAL_CFT_SPECTRUM_SCAFFOLD"


def _base_payload(status: str = "DERIVED") -> Dict[str, object]:
    return {
        "status": status,
        "epistemic_status": _EPISTEMIC_STATUS,
        "background": "RS1/AdS5 with holographic 4D CFT dual",
        "pillar": 775,
    }


def graviton_to_cft_stresstensor(k_cs: int = K_CS, pi_kr: float = PI_KR) -> dict:
    """Map the massless 5D graviton to the 4D CFT stress tensor."""
    result = _base_payload()
    result.update(
        {
            "bulk_field": "5D massless graviton h_{MN}",
            "bulk_mass_squared_l2": 0.0,
            "spin": 2,
            "cft_operator": "stress tensor T_{mu nu}",
            "conformal_dimension": STRESS_TENSOR_DELTA,
            "boundary_coupling": "∫ d^4x h_{mu nu} T^{mu nu}",
            "k_cs": int(k_cs),
            "pi_kr": float(pi_kr),
            "operator_role": "universal conserved energy-momentum tensor",
        }
    )
    return result


def kk_tower_to_cft_operators(n_max: int = 5, pi_kr: float = PI_KR) -> dict:
    """Map the RS1 KK graviton tower to approximate spin-2 CFT operators."""
    if n_max < 1:
        raise ValueError(f"n_max must be >= 1, got {n_max}")
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    levels: List[Dict[str, float]] = []
    m_kk = M_PL_GEV * math.exp(-pi_kr)
    for n in range(1, n_max + 1):
        levels.append(
            {
                "n": n,
                "bulk_mass_gev": n * m_kk,
                "bulk_mass_squared_gev2": (n * m_kk) ** 2,
                "cft_operator": f"O_{{{n}}}^(2)",
                "conformal_dimension": 4.0 + 2.0 * n,
            }
        )

    result = _base_payload(status="APPROXIMATE")
    result.update(
        {
            "tower_type": "KK graviton / glueball-like spin-2 operators",
            "n_max": int(n_max),
            "pi_kr": float(pi_kr),
            "m_kk_gev": m_kk,
            "operator_levels": levels,
            "dimension_formula": "Delta_n ≈ 4 + 2 n",
            "interpretation": "Massive spin-2 boundary operators dual to KK gravitons.",
        }
    )
    return result


def radion_to_cft_lagrangian_density(pi_kr: float = PI_KR) -> dict:
    """Map the radion/dilaton sector to the CFT gauge kinetic operator."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    c_rad_reference = 1.0
    m_kk = M_PL_GEV * math.exp(-pi_kr)
    radion_mass = c_rad_reference * m_kk
    result = _base_payload(status="CONSTRAINED")
    result.update(
        {
            "bulk_field": "radion / dilaton phi",
            "bulk_mass_squared_l2_zero_mode": 0.0,
            "cft_operator": "Tr F^2",
            "conformal_dimension": 4.0,
            "radion_mass_formula": "m_radion = c_rad * M_KK with c_rad = O(1) from Goldberger-Wise stabilization",
            "c_rad_reference": c_rad_reference,
            "m_kk_gev": m_kk,
            "radion_mass_reference_gev": radion_mass,
            "operator_role": "source for conformal-symmetry breaking / gauge-kinetic deformation",
            "pi_kr": float(pi_kr),
        }
    )
    return result


def cs_field_to_cft_current(k_cs: int = K_CS) -> dict:
    """Map the 5D Chern-Simons gauge field to a U(1) current in the CFT."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")

    anomaly_current_coeff = float(k_cs) / (2.0 * math.pi**2)
    result = _base_payload()
    result.update(
        {
            "bulk_field": "5D Chern-Simons gauge field A_M",
            "p_form_degree": 1,
            "cft_operator": "U(1) current j^mu",
            "conformal_dimension": CURRENT_DELTA,
            "anomaly_coefficient_current_normalization": anomaly_current_coeff,
            "ward_identity": "∂_mu j_A^mu = (K_CS / 16π^2) F∧F",
            "k_cs": int(k_cs),
        }
    )
    return result


def gauge_field_to_cft_currents(k_cs: int = K_CS) -> dict:
    """Map the bulk gauge sector to conserved SM currents in the dual CFT."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")

    currents = [
        {"group": "SU(3)_c", "operator": "J^a_mu (color current)", "conformal_dimension": CURRENT_DELTA},
        {"group": "SU(2)_L", "operator": "J^i_mu (weak current)", "conformal_dimension": CURRENT_DELTA},
        {"group": "U(1)_Y", "operator": "J^Y_mu (hypercharge current)", "conformal_dimension": CURRENT_DELTA},
    ]
    fermion_sector = {
        "light_quark_bulk_c": 0.5,
        "light_quark_conformal_dimension": FERMION_DELTA_LIGHT,
        "top_quark_bulk_c": 0.0,
        "top_quark_conformal_dimension": FERMION_DELTA_TOP,
    }

    result = _base_payload()
    result.update(
        {
            "bulk_field": "5D SU(5) gauge sector reduced to SM gauge group by Wilson lines",
            "currents": currents,
            "fermionic_operator_sector": fermion_sector,
            "k_cs": int(k_cs),
            "interpretation": "Conserved boundary currents plus fermionic operator dimensions controlled by bulk localization.",
        }
    )
    return result


def cft_central_charge(
    k_cs: int = K_CS,
    pi_kr: float = PI_KR,
    m_pl_gev: float = M_PL_GEV,
) -> dict:
    """Estimate the CFT central charge from the AdS5 gravity dual."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")
    if m_pl_gev <= 0.0:
        raise ValueError(f"m_pl_gev must be positive, got {m_pl_gev}")

    k_gev = m_pl_gev
    radius_gev_inv = pi_kr / k_gev
    g5 = 1.0 / (m_pl_gev**2 * math.pi * radius_gev_inv)
    c_direct = m_pl_gev**2 / (2.0 * k_gev**3 * radius_gev_inv)
    c_reduced = m_pl_gev**2 / (2.0 * k_gev**3 * radius_gev_inv)
    inverse_kcs = 1.0 / float(k_cs)

    result = _base_payload(status="ESTIMATED")
    result.update(
        {
            "formula": "UM reduction: c_CFT ≈ M_Pl^2 / (2 k^3 R), equivalent here to 1 / (2 πkR)",
            "k_gev": k_gev,
            "radius_gev_inverse": radius_gev_inv,
            "g5_inverse_gev3": 1.0 / g5,
            "c_cft_direct": c_direct,
            "c_cft_reduced": c_reduced,
            "inverse_k_cs": inverse_kcs,
            "relative_difference_to_1_over_kcs": abs(c_reduced - inverse_kcs) / inverse_kcs,
            "interpretation": "The dual is strongly coupled; the normalization suggests coupling strength controlled by 1/K_CS.",
            "normalization_caveat": "Large-N extraction is model-dependent, so N_CFT should not be over-interpreted from this scalar estimate alone.",
        }
    )
    return result


def cs_anomaly_coefficient(k_cs: int = K_CS) -> dict:
    """Return the Chern-Simons induced anomaly coefficients in the dual CFT."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")

    result = _base_payload()
    result.update(
        {
            "k_cs": int(k_cs),
            "axial_ward_identity_coefficient": float(k_cs) / (16.0 * math.pi**2),
            "current_normalization_coefficient": float(k_cs) / (2.0 * math.pi**2),
            "ward_identity": "∂_mu j_A^mu = (K_CS / 16π^2) F∧F",
            "interpretation": "K_CS acts as the holographic 't Hooft anomaly coefficient.",
        }
    )
    return result


def dual_cft_spectrum_report() -> dict:
    """Assemble a compact report of the holographic UM→CFT dictionary."""
    graviton = graviton_to_cft_stresstensor()
    kk = kk_tower_to_cft_operators()
    radion = radion_to_cft_lagrangian_density()
    cs_current = cs_field_to_cft_current()
    gauge = gauge_field_to_cft_currents()
    central = cft_central_charge()
    anomaly = cs_anomaly_coefficient()

    result = _base_payload(status="SCAFFOLD")
    result.update(
        {
            "summary": "Operator assignments fixed at leading holographic level; full non-perturbative CFT construction remains open.",
            "graviton_sector": graviton,
            "kk_sector": kk,
            "radion_sector": radion,
            "cs_sector": cs_current,
            "gauge_sector": gauge,
            "central_charge": central,
            "anomaly": anomaly,
        }
    )
    return result
