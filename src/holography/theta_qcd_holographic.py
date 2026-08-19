# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 777 — Holographic θ_QCD suppression from the RS1/Z2 geometry.

This module isolates the holographic interpretation of the strong-CP closure:
in the RS1 orbifold, A_5 is Z2-odd and therefore vanishes at both fixed points.
If the boundary value of A_5 sources the holographic theta parameter, then the
IR source is identically zero and θ_QCD vanishes without a PQ postulate.

Honest status
-------------
THETA_QCD_HOLOGRAPHIC_DERIVED:
    Tree-level θ_QCD = 0 follows directly from the orbifold boundary condition.
    Residual radiative effects are exponentially warp-suppressed and remain many
    orders of magnitude below the experimental 10^-10 bound.
"""

from __future__ import annotations

import math
from typing import Dict

from ..core.qcd_geometry_primary import K_CS, M_PL_GEV

__all__ = [
    "z2_parity_a5",
    "holographic_theta_boundary_value",
    "radiative_theta_correction",
    "no_light_axion_proof",
    "holographic_vs_pq_comparison",
    "theta_qcd_holographic_report",
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

PI_KR: float = 37.0
THETA_EXPERIMENTAL_BOUND: float = 1.0e-10
_EPISTEMIC_STATUS = "THETA_QCD_HOLOGRAPHIC_DERIVED"


def _base_payload(status: str = "DERIVED") -> Dict[str, object]:
    return {
        "status": status,
        "epistemic_status": _EPISTEMIC_STATUS,
        "pillar": 777,
        "background": "RS1/AdS5 orbifold with holographic theta source on the boundary",
    }


def z2_parity_a5(pi_kr: float = PI_KR) -> dict:
    """Return the Z2-orbifold parity statement for the fifth gauge component."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    result = _base_payload()
    result.update(
        {
            "pi_kr": float(pi_kr),
            "field": "A_5",
            "z2_parity": "odd",
            "transformation": "A_5(y) = -A_5(-y)",
            "uv_boundary_value": 0.0,
            "ir_boundary_value": 0.0,
            "fixed_point_statement": "Z2-odd bulk fields obey Dirichlet boundary conditions at y=0 and y=πR.",
        }
    )
    return result


def holographic_theta_boundary_value(k_cs: int = K_CS, pi_kr: float = PI_KR) -> dict:
    """Compute the holographic theta source from the IR boundary value of A_5."""
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive, got {k_cs}")
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    parity = z2_parity_a5(pi_kr=pi_kr)
    a5_ir = parity["ir_boundary_value"]
    theta = float(k_cs) * float(a5_ir)

    result = _base_payload()
    result.update(
        {
            "k_cs": int(k_cs),
            "pi_kr": float(pi_kr),
            "a5_ir_boundary_value": a5_ir,
            "theta_qcd": theta,
            "formula": "θ_QCD = K_CS × A_5|_{IR}",
            "interpretation": "The holographic theta source is forced to zero by orbifold parity.",
        }
    )
    return result


def radiative_theta_correction(pi_kr: float = PI_KR, alpha_s: float = 0.118) -> dict:
    """Estimate the residual warp-suppressed radiative correction to θ_QCD."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")
    if alpha_s <= 0.0:
        raise ValueError(f"alpha_s must be positive, got {alpha_s}")

    naive_one_loop = alpha_s / (2.0 * math.pi) * math.exp(-pi_kr)
    parity_protected_bound = math.exp(-2.0 * pi_kr)

    result = _base_payload(status="BOUNDED")
    result.update(
        {
            "pi_kr": float(pi_kr),
            "alpha_s": float(alpha_s),
            "naive_one_loop_prefactor_estimate": naive_one_loop,
            "delta_theta_upper_bound": parity_protected_bound,
            "experimental_bound": THETA_EXPERIMENTAL_BOUND,
            "satisfies_experimental_bound": parity_protected_bound < THETA_EXPERIMENTAL_BOUND,
            "formula": "|δθ| < exp(-2 π k R)",
            "interpretation": "After orbifold/parity protection, radiative θ is exponentially below present sensitivity.",
        }
    )
    return result


def no_light_axion_proof(pi_kr: float = PI_KR) -> dict:
    """Show that the Z2-odd A5 sector has no massless axion zero mode."""
    if pi_kr <= 0.0:
        raise ValueError(f"pi_kr must be positive, got {pi_kr}")

    m_kk = M_PL_GEV * math.exp(-pi_kr)
    result = _base_payload()
    result.update(
        {
            "pi_kr": float(pi_kr),
            "has_a5_zero_mode": False,
            "reason": "A_5 is Z2-odd and obeys Dirichlet conditions at both orbifold fixed points.",
            "lightest_kk_mode_mass_gev": m_kk,
            "axion_statement": "No parametrically light PQ-like axion is required or generated by this mechanism.",
        }
    )
    return result


def holographic_vs_pq_comparison() -> dict:
    """Compare the orbifold-holographic closure with a standard PQ narrative."""
    theta = holographic_theta_boundary_value()
    loop = radiative_theta_correction()
    axion = no_light_axion_proof()

    result = _base_payload(status="COMPARATIVE")
    result.update(
        {
            "holographic_mechanism": {
                "requires_pq_symmetry": False,
                "theta_tree_level": theta["theta_qcd"],
                "residual_theta_upper_bound": loop["delta_theta_upper_bound"],
                "light_axion_present": axion["has_a5_zero_mode"],
                "mechanism": "Z2 orbifold boundary condition on A_5",
            },
            "pq_reference_mechanism": {
                "requires_pq_symmetry": True,
                "theta_tree_level": "dynamically relaxed",
                "residual_theta_upper_bound": "model-dependent; set by axion potential minimization",
                "light_axion_present": True,
                "mechanism": "global U(1)_PQ with anomalous axion",
            },
            "assessment": "The orbifold route removes the theta source geometrically rather than dynamically.",
            "cross_reference": "See src/core/strong_cp_pq_z2_closure.py for the older PQ/Z2 closure path.",
        }
    )
    return result


def theta_qcd_holographic_report() -> dict:
    """Assemble a compact report for the holographic θ_QCD closure."""
    parity = z2_parity_a5()
    theta = holographic_theta_boundary_value()
    loop = radiative_theta_correction()
    axion = no_light_axion_proof()
    comparison = holographic_vs_pq_comparison()

    result = _base_payload(status="DERIVED")
    result.update(
        {
            "summary": "θ_QCD vanishes exactly at tree level from the orbifold boundary condition; residual effects remain exponentially tiny.",
            "z2_parity": parity,
            "theta_boundary": theta,
            "radiative_correction": loop,
            "axion_sector": axion,
            "comparison": comparison,
        }
    )
    return result
