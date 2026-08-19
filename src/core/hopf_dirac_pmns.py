# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 778 — Hopf-Dirac PMNS scaffold.

Constrained bridge from the (5,7) Hopf bundle data on S^3 to PMNS mixing
observables. The angle formulas are explicit geometric constructions; the CP
phase is a constrained holonomy estimate; the generation hierarchy remains a
motivated KK-mode scaffold rather than a quantitative derivation.
"""

from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER = 778
PILLAR_TITLE = "Hopf-Dirac PMNS"
STATUS = "HOPF_DIRAC_PMNS_CONSTRAINED"
EPISTEMIC_STATUS = "CONSTRAINED"

N1 = 5
N2 = 7
K_CS = 74
N_C = 3
PI_KR = 37.0
HOPF_LINKING_NUMBER = N1 * N2
HOPF_CHARGE = HOPF_LINKING_NUMBER / K_CS
PDG_DELTA_CP_BEST_FIT_DEG = 222.0

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "STATUS",
    "EPISTEMIC_STATUS",
    "N1",
    "N2",
    "K_CS",
    "N_C",
    "PI_KR",
    "HOPF_LINKING_NUMBER",
    "HOPF_CHARGE",
    "hopf_connection_1form",
    "dirac_eigenvalues_hopf",
    "hopf_winding_pmns_angles",
    "cp_phase_hopf_holonomy",
    "generation_mass_hierarchy_hopf",
    "index_theorem_hopf",
    "hopf_dirac_pmns_report",
]


def _meta(**payload: Any) -> dict[str, Any]:
    payload.setdefault("pillar", PILLAR_NUMBER)
    payload.setdefault("status", STATUS)
    payload.setdefault("epistemic_status", EPISTEMIC_STATUS)
    return payload


def _angle_deg_from_sin2(sin2_value: float) -> float:
    return math.degrees(math.asin(math.sqrt(sin2_value)))



def hopf_connection_1form(n1: int = N1, n2: int = N2) -> dict[str, Any]:
    """Return the normalized Hopf U(1) connection data for the (n1,n2) braid."""
    total = n1 + n2
    linking = n1 * n2
    return _meta(
        connection_form=f"A = ({n1} dphi1 + {n2} dphi2)/{total}",
        coefficients={"dphi1": n1 / total, "dphi2": n2 / total},
        normalization_denominator=total,
        hopf_linking_number=linking,
        hopf_charge=linking / float(n1 * n1 + n2 * n2),
        fiber="S1",
        base="S2",
        total_space="S3",
        honest_note="Connection data are exact at scaffold level; the full spin connection backreaction is not solved here.",
    )



def dirac_eigenvalues_hopf(
    n_modes: int = 5,
    n1: int = N1,
    n2: int = N2,
    k_cs: int = K_CS,
) -> dict[str, Any]:
    """Return the first ``n_modes`` Hopf-shifted Dirac eigenvalues on S^3."""
    if n_modes < 1:
        raise ValueError("n_modes must be >= 1")

    q = (n1 * n2) / float(k_cs)
    modes: list[dict[str, Any]] = []
    for k in range(n_modes):
        standard = k + 1.5
        shifted = standard + q
        modes.append(
            {
                "k": k,
                "standard_abs_eigenvalue": standard,
                "hopf_shift_q": q,
                "modified_positive": shifted,
                "modified_negative": -shifted,
            }
        )

    return _meta(
        charge_q=q,
        eigenvalue_formula="lambda_k^(q) = ±(k + 3/2 + q)",
        modes=modes,
        lightest_abs_eigenvalue=modes[0]["modified_positive"],
        zero_mode_present=False,
        honest_note="The spectrum uses the stated Hopf U(1) shift ansatz; solving the full coupled Dirac operator remains future work.",
    )



def hopf_winding_pmns_angles(
    n1: int = N1,
    n2: int = N2,
    n_c: int = N_C,
    k_cs: int = K_CS,
) -> dict[str, Any]:
    """Derive the three PMNS mixing angles from Hopf winding data."""
    sin2_theta12 = n_c / float(n_c + n2)
    sin2_theta23 = (k_cs + 2 * n_c) / float(2 * k_cs)
    sin2_theta13 = n_c / float((n1 + n2) ** 2)
    return _meta(
        sin2_theta12=sin2_theta12,
        sin2_theta23=sin2_theta23,
        sin2_theta13=sin2_theta13,
        theta12_deg=_angle_deg_from_sin2(sin2_theta12),
        theta23_deg=_angle_deg_from_sin2(sin2_theta23),
        theta13_deg=_angle_deg_from_sin2(sin2_theta13),
        formulas={
            "theta12": "sin^2(theta12) = N_c/(N_c+n2)",
            "theta23": "sin^2(theta23) = (K_CS+2N_c)/(2K_CS)",
            "theta13": "sin^2(theta13) = N_c/(n1+n2)^2",
        },
        exact_fractions={
            "theta12": "3/10",
            "theta23": "20/37",
            "theta13": "1/48",
        },
        honest_note="This module makes the Hopf-to-angle bridge explicit; it does not by itself prove full 6D fermion localization dynamics.",
    )



def cp_phase_hopf_holonomy(n1: int = N1, n2: int = N2, k_cs: int = K_CS) -> dict[str, Any]:
    """Estimate the PMNS CP phase from the Hopf holonomy."""
    linking = n1 * n2
    delta_rad = 2.0 * math.pi * linking / float(k_cs)
    delta_deg = math.degrees(delta_rad)
    residual_pct = abs(delta_deg - PDG_DELTA_CP_BEST_FIT_DEG) / PDG_DELTA_CP_BEST_FIT_DEG * 100.0
    return _meta(
        delta_cp_rad=delta_rad,
        delta_cp_deg=delta_deg,
        holonomy_fraction=linking / float(k_cs),
        linking_number=linking,
        pdg_best_fit_deg=PDG_DELTA_CP_BEST_FIT_DEG,
        residual_pct_vs_best_fit=residual_pct,
        comparison_band="O(30%) agreement target",
        honest_note="The CP phase is a constrained holonomy estimate, not a precision fit; it lands within order-30% of the cited best-fit value.",
    )



def generation_mass_hierarchy_hopf(
    n1: int = N1,
    n2: int = N2,
    k_cs: int = K_CS,
    m_kk_gev: float | None = None,
) -> dict[str, Any]:
    """Return a motivated three-generation KK hierarchy scaffold."""
    linking = n1 * n2
    ratio = linking / float(k_cs)
    normalized_hierarchy = [1.0, 1.0 + ratio, 1.0 + 2.0 * ratio]
    kk_prefactors = [k * 2.0 * math.pi * ratio for k in (1, 2, 3)]
    masses_gev = None
    if m_kk_gev is not None:
        masses_gev = [m_kk_gev * factor for factor in kk_prefactors]

    return _meta(
        hierarchy_formula="m1:m2:m3 ≈ 1 : (1+ℓ/K_CS) : (1+2ℓ/K_CS)",
        normalized_hierarchy=normalized_hierarchy,
        kk_prefactors=kk_prefactors,
        masses_gev=masses_gev,
        linking_number=linking,
        honest_note="The three-lightest-mode identification is motivated by KK suppression and is not yet a quantitative mass fit.",
    )



def index_theorem_hopf(n1: int = N1, n2: int = N2) -> dict[str, Any]:
    """Return the Hopf index-theorem bookkeeping used by this scaffold."""
    linking = n1 * n2
    return _meta(
        dirac_index=linking,
        chiral_zero_modes=linking,
        light_generations_retained=3,
        heavy_modes_decoupled=linking - 3,
        resolution="Most zero modes are assumed to become heavy through KK lifting; the lightest three are identified with the observed generations.",
        honest_note="The index count is explicit, while the decoupling pattern is a constrained interpretation rather than a first-principles diagonalization.",
    )



def hopf_dirac_pmns_report() -> dict[str, Any]:
    """Return a combined report for Pillar 778."""
    connection = hopf_connection_1form()
    spectrum = dirac_eigenvalues_hopf()
    angles = hopf_winding_pmns_angles()
    cp_phase = cp_phase_hopf_holonomy()
    hierarchy = generation_mass_hierarchy_hopf()
    index_data = index_theorem_hopf()
    return _meta(
        module="src/core/hopf_dirac_pmns.py",
        connection=connection,
        spectrum=spectrum,
        angles=angles,
        cp_phase=cp_phase,
        generation_hierarchy=hierarchy,
        index_theorem=index_data,
        summary=(
            "PMNS angles are explicit Hopf-winding derivations, the CP phase is a constrained holonomy estimate, "
            "and the mass hierarchy remains a motivated KK-mode scaffold."
        ),
    )
