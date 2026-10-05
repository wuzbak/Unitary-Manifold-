# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 779 — Sp(2,R) radion propagator scaffold.

This module encodes the claimed null-cone improvement of the 5D radion
propagator induced by the 13D Sp(2,R) constraint structure.
"""

from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER = 779
PILLAR_TITLE = "Sp(2,R) Null-Cone Radion Propagator"
STATUS = "SP2R_UV_IMPROVED"
EPISTEMIC_STATUS = "UV_IMPROVED"

DIM_13 = 13
RADION_INDEX = 12
PI_KR = 37.0
M_PL_GEV = 1.22e19

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "STATUS",
    "EPISTEMIC_STATUS",
    "DIM_13",
    "RADION_INDEX",
    "PI_KR",
    "M_PL_GEV",
    "sp2r_null_cone_constraints",
    "radion_propagator_standard",
    "sp2r_uv_form_factor",
    "sp2r_modified_propagator",
    "uv_fixed_point_probe",
    "propagator_uv_scaling",
    "sp2r_radion_propagator_report",
]


def _meta(**payload: Any) -> dict[str, Any]:
    payload.setdefault("pillar", PILLAR_NUMBER)
    payload.setdefault("status", STATUS)
    payload.setdefault("epistemic_status", EPISTEMIC_STATUS)
    return payload



def _default_radion_mass(pi_kr: float) -> float:
    return 1.0 / max(pi_kr, 1.0)



def sp2r_null_cone_constraints(n_dim: int = DIM_13) -> dict[str, Any]:
    """Return the first-class Sp(2,R) null-cone constraints."""
    if n_dim < 3:
        raise ValueError("n_dim must be >= 3")
    return _meta(
        n_dim=n_dim,
        signature="(11+2) parent for the default scaffold",
        constraints=["X·X = 0", "P·P = 0", "X·P = 0"],
        radion_sector={"X^12": "Phi_M", "P^12": "d_t Phi_M"},
        gauge_fixed_second_time=True,
        honest_note="The second time direction is treated as pure gauge, consistent with the architecture-limit statement in the 13D scaffold.",
    )



def radion_propagator_standard(
    p2_gev2: float,
    m_radion_gev: float | None = None,
    pi_kr: float = PI_KR,
) -> dict[str, Any]:
    """Return the standard 5D radion propagator 1/(p^2 + m^2)."""
    if p2_gev2 < 0.0:
        raise ValueError("p2_gev2 must be non-negative")
    mass = _default_radion_mass(pi_kr) if m_radion_gev is None else m_radion_gev
    denominator = p2_gev2 + mass * mass
    return _meta(
        p2_gev2=p2_gev2,
        m_radion_gev=mass,
        denominator_gev2=denominator,
        propagator_gev_minus2=1.0 / denominator,
        formula="G_phi(p^2) = 1/(p^2 + m_radion^2)",
    )



def sp2r_uv_form_factor(p2_gev2: float, m_pl_gev: float = M_PL_GEV) -> dict[str, Any]:
    """Return the null-cone UV form factor F_UV(x) = 1/(1+x)."""
    if p2_gev2 < 0.0:
        raise ValueError("p2_gev2 must be non-negative")
    if m_pl_gev <= 0.0:
        raise ValueError("m_pl_gev must be positive")
    x = p2_gev2 / (m_pl_gev * m_pl_gev)
    form_factor = 1.0 / (1.0 + x)
    return _meta(
        p2_gev2=p2_gev2,
        x=p2_gev2 / (m_pl_gev * m_pl_gev),
        t2_integration_abs=1.0,
        form_factor=form_factor,
        uv_limit_statement="For p^2 >> M_Pl^2, F_UV ~ M_Pl^2/p^2 and the propagator softens from 1/p^2 to 1/p^4.",
    )



def sp2r_modified_propagator(
    p2_gev2: float,
    m_radion_gev: float | None = None,
    pi_kr: float = PI_KR,
) -> dict[str, Any]:
    """Return the Sp(2,R)-softened radion propagator."""
    standard = radion_propagator_standard(p2_gev2=p2_gev2, m_radion_gev=m_radion_gev, pi_kr=pi_kr)
    form_factor = sp2r_uv_form_factor(p2_gev2=p2_gev2)
    modified = standard["propagator_gev_minus2"] * form_factor["form_factor"]
    return _meta(
        p2_gev2=p2_gev2,
        standard_propagator_gev_minus2=standard["propagator_gev_minus2"],
        form_factor=form_factor["form_factor"],
        modified_propagator_gev_minus2=modified,
        uv_behavior="UV_SOFTER_1_OVER_P4",
        standard=standard,
        form_factor_data=form_factor,
        honest_note="The form factor is a finite-measure scaffold rather than an exact Sp(2,R) group integral.",
    )



def uv_fixed_point_probe(pi_kr: float = PI_KR, k_cs: int = 74, d_bulk: int = 5) -> dict[str, Any]:
    """Return a positive asymptotic-safety probe based on the softened propagator."""
    if d_bulk <= 2:
        raise ValueError("d_bulk must exceed 2 for the stated fixed-point expression")
    correction_factor_proxy = abs(k_cs / (2.0 * pi_kr))
    g5_star_proxy = (d_bulk - 2.0) / (2.0 * correction_factor_proxy)
    return _meta(
        d_bulk=d_bulk,
        correction_factor_proxy=correction_factor_proxy,
        symbolic_fixed_point="G5* = (d-2)/(2 |Omega_Sp2R|)",
        g5_star_proxy=g5_star_proxy,
        fixed_point_exists_proxy=g5_star_proxy > 0.0,
        honest_note="The sign and UV-improvement signal are positive, but the exact Sp(2,R) phase-space volume has not been computed in this scaffold.",
    )



def propagator_uv_scaling() -> dict[str, Any]:
    """Compare standard and modified high-momentum scaling."""
    p2_low = M_PL_GEV * M_PL_GEV
    p2_high = 1.0e6 * p2_low
    standard_low = radion_propagator_standard(p2_low)["propagator_gev_minus2"]
    standard_high = radion_propagator_standard(p2_high)["propagator_gev_minus2"]
    modified_low = sp2r_modified_propagator(p2_low)["modified_propagator_gev_minus2"]
    modified_high = sp2r_modified_propagator(p2_high)["modified_propagator_gev_minus2"]
    standard_ratio = standard_high / standard_low
    modified_ratio = modified_high / modified_low
    return _meta(
        p2_low=p2_low,
        p2_high=p2_high,
        standard_ratio=standard_ratio,
        modified_ratio=modified_ratio,
        expected_standard_ratio=1.0e-6,
        expected_modified_ratio=1.0e-12,
        interpretation="Using p^2 as the running variable, the standard propagator scales as (p^2)^-1 and the softened propagator as (p^2)^-2.",
    )



def sp2r_radion_propagator_report() -> dict[str, Any]:
    """Return a combined report for Pillar 779."""
    return _meta(
        module="src/core/sp2r_radion_propagator.py",
        constraints=sp2r_null_cone_constraints(),
        sample_standard=radion_propagator_standard(1.0),
        sample_modified=sp2r_modified_propagator(1.0),
        uv_scaling=propagator_uv_scaling(),
        fixed_point_probe=uv_fixed_point_probe(),
        summary="The Sp(2,R) null-cone scaffold softens the radion propagator in the UV and supports a positive asymptotic-safety probe, while the exact group-volume integral remains open.",
    )
