# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
r"""RS1 fermion nonuniqueness and conditional historical ladder calculations.

On a regular finite interval 0 <= y <= L, take
ds² = exp(-2ky) eta_mu_nu dx^mu dx^nu + dy², k >= 0, L > 0.
The minimally coupled Dirac action is
S = integral d^4x dy sqrt(|g|) bar(Psi) (i Gamma^M D_M - m_5) Psi.
Here sqrt(|g|)=exp(-4ky) and Gamma^mu=exp(ky) gamma^mu, so the
four-dimensional kinetic inner product for the unrescaled profile F is
integral exp(-3ky) F*G dy. With Psi=exp(2ky) psi(x) f(y), it becomes
<f,g>_w = integral exp(ky) f* g dy. The spin-connection term -2k is
removed by that rescaling. Set m_5=ck on the interval; its orbifold extension
is ck sign(y), with the corresponding odd reflection at the other endpoint.
Every real c is compatible with this mass parity.

In a real chiral convention the KK operator is
D_c = exp(-ky) [[0, -d_y+ck], [d_y+ck, 0]] on L²(exp(ky)dy)^2.
Choose domain H¹([0,L], C²) with f_R(0)=f_R(L)=0. Integration by parts gives
<u,Dv>_w - <Du,v>_w = [u_R* v_L - u_L* v_R]_0^L.
The free endpoint values of u_L force v_R=0 in the adjoint domain. Regular
coefficients imply H¹ adjoint regularity, so the domain equals its adjoint
domain: it is self-adjoint, not just symmetric. It is independent of c.
This is a separated chiral boundary condition, NOT an APS spectral condition.
The left zero mode f_L=N exp(-cky), f_R=0 is even on the covering orbifold.
Its kinetic density is N² exp((1-2c)ky). All finite real c are normalisable
on finite L; c>1/2 means UV localisation, not survival. The other domain,
f_L(0)=f_L(L)=0, gives f_R=N exp(+cky), with flat density at c=-1/2
in the SAME signed mass convention. A phenomenological RH parameter with
flat point +1/2 is therefore c_R=-c, not the same signed mass.

The executable counterexample uses fixed k,L, the same chiral domain and a
fixed reference profile. Varying c changes weighted overlaps. It neither
imports masses nor fits CKM targets. It disproves selection by these boundary
conditions alone, not selection by some additional, specified dynamics.
Legacy ladder/seesaw numbers below are retained as conditional ansatze;
the separate historical bisection comparison is explicitly target-dependent.
Lean DiracOrbifoldSpectrum checks arithmetic only, not this analytic argument.
"""
from __future__ import annotations

import math
from typing import Dict, List

from src.core.pillar636_su3_orbifold_equivalence import orbifold_equivalence_theorem

PILLAR_NUMBER = 677
PILLAR_STATUS = "BULK_MASS_UNDERDETERMINED_BY_ORBIFOLD_BC"
PILLAR_TITLE = "Fermion Orbifold Nonuniqueness and Conditional Ladder"
VERSION = "v21.0"
N_W = 5
K_CS = 74
N_C = 3
PI_KR = 37.0
ALPHA_GUT_GEO = N_C / K_CS
CL_TOPO_BASE = 1.0 - ALPHA_GUT_GEO
CL_STEP = 1.0 / (2 * K_CS)
_DELTA_SEESAW = N_C * ALPHA_GUT_GEO / (2.0 * PI_KR)
_CL_BISECT = {1: 0.9610, 2: 0.9550, 3: 0.9340}
_CONDITIONAL = "CONDITIONAL_ANSATZ_NOT_BC_DERIVED"


def _validate_interval(k: float, length: float, *values: float) -> None:
    if not all(math.isfinite(v) for v in (k, length, *values)):
        raise ValueError("parameters must be finite")
    if k < 0 or length <= 0:
        raise ValueError("require k >= 0 and finite length > 0")


def _log_exp_integral(rate: float, length: float) -> float:
    """Log integral_0^L exp(rate*y)dy without exponentiating a large number."""
    z = rate * length
    if z == 0:
        return math.log(length)
    if z > 0:
        return z + math.log(-math.expm1(-z)) - math.log(rate)
    return math.log(-math.expm1(z)) - math.log(-rate)


def rs1_zero_mode(c: float, y: float, k: float = 1.0,
                  length: float = 2.0, chirality: str = "L") -> float:
    """Normalised rescaled profile in the action-derived weight exp(ky)."""
    _validate_interval(k, length, c, y)
    if not 0 <= y <= length or chirality not in ("L", "R"):
        raise ValueError("require 0 <= y <= length and chirality L or R")
    signed_c = c if chirality == "L" else -c
    log_norm = _log_exp_integral((1 - 2 * signed_c) * k, length)
    return math.exp(-signed_c * k * y - 0.5 * log_norm)


def rs1_weighted_overlap(c_a: float, c_b: float, k: float = 1.0,
                         length: float = 2.0) -> float:
    """Overlap of two normalised left zero modes in the SAME weighted space.

    Different c label different admissible operators, not different eigenstates
    of one fixed operator. This overlap is a profile diagnostic, not a Yukawa
    coupling: a physical coupling also requires Higgs and interaction data.
    """
    _validate_interval(k, length, c_a, c_b)
    numerator = _log_exp_integral((1 - c_a - c_b) * k, length)
    norms = (_log_exp_integral((1 - 2 * c_a) * k, length)
             + _log_exp_integral((1 - 2 * c_b) * k, length))
    return math.exp(numerator - 0.5 * norms)


def dirac_boundary_form(u0, uL, v0, vL) -> complex:
    """Endpoint Green form; each endpoint pair is ordered (L, R)."""
    def endpoint(u, v):
        return complex(u[1]).conjugate() * v[0] - complex(u[0]).conjugate() * v[1]
    return endpoint(uL, vL) - endpoint(u0, v0)


def rs1_nonuniqueness_example() -> Dict[str, object]:
    """Fixed geometry/domain, continuum of c; three explicit witnesses."""
    values = (0.0, 0.5, 1.0)
    return {
        "metric": "ds²=exp(-2ky)eta dx dx+dy²",
        "k": 1.0, "length": 2.0,
        "kinetic_weight_unrescaled": "exp(-3ky)",
        "kinetic_weight_rescaled": "exp(ky)",
        "domain": "H¹([0,L],C²), f_R(0)=f_R(L)=0",
        "self_adjoint_reason": "maximal isotropic endpoint data; adjoint has the same domain",
        "parity": "f_L even; f_R odd; m_5 odd on the covering orbifold",
        "admissible_c": "all real c",
        "fixed_reference_c": 0.0,
        "examples": [
            {"c": c, "normalisable": True,
             "overlap_with_fixed_reference": rs1_weighted_overlap(c, 0.0),
             "uv_profile": rs1_zero_mode(c, 0.0),
             "ir_profile": rs1_zero_mode(c, 2.0)}
            for c in values
        ],
        "uses_mass_or_ckm_targets": False,
        "status": PILLAR_STATUS,
    }


def cl_generation(generation: int) -> float:
    """Evaluate the assumed ladder 1-N_c/K_CS-(i-1)/(2K_CS), not a BC result."""
    if generation not in (1, 2, 3):
        raise ValueError("generation must be 1, 2, or 3")
    return CL_TOPO_BASE - (generation - 1) * CL_STEP


def cl_orbifold_spectrum() -> Dict[str, object]:
    return {
        "formula": "c_L^(i) = 1 − N_c/K_CS − (i−1)/(2 K_CS)",
        "derivation_chain": ["assume base 71/74", "assume step 1/148", "evaluate three entries"],
        "generations": {
            i: {"c_L_topo": cl_generation(i), "fraction": fraction}
            for i, fraction in enumerate(("71/74", "141/148", "35/37"), start=1)
        },
        "axiom_zero_compliant": False,
        "sm_inputs": 0,
        "additional_assumptions": ["ladder base", "ladder spacing", "three generations"],
        "status": _CONDITIONAL,
    }


def cl_bisection_comparison() -> Dict[str, object]:
    """Historical target-dependent diagnostic; never used by the counterexample."""
    rows = []
    for i, bisect in _CL_BISECT.items():
        delta = cl_generation(i) - bisect
        percent = abs(delta) / bisect * 100
        rows.append({"generation": i, "c_L_topo": cl_generation(i),
                     "c_L_bisect": bisect, "delta": delta, "delta_pct": percent,
                     "agrees_sub_1p5_pct": percent < 1.5})
    return {
        "comparison": rows,
        "max_delta_pct": max(row["delta_pct"] for row in rows),
        "all_agree_sub_1p5_pct": all(row["agrees_sub_1p5_pct"] for row in rows),
        "status": "HISTORICAL_TARGET_DEPENDENT_COMPARISON",
        "attribution": "No remainder theorem or dynamical explanation of discrepancies.",
        "uses_target_dependent_bisection": True,
    }


def z2_projection_equivalence() -> Dict[str, object]:
    result = orbifold_equivalence_theorem()
    result.update({"status": "INTERNAL_LIFT_UNDERDETERMINED",
                   "advances_pillar_636": False,
                   "level": "EXPLICIT_INEQUIVALENT_INTERNAL_LIFTS"})
    return result


def su3_hilbert_equivalence() -> Dict[str, object]:
    return {
        "kawamura_dependence": "ADDITIONAL_INTERNAL_LIFT_REQUIRED",
        "equivalence_detail": z2_projection_equivalence(),
        "status": "INTERNAL_LIFT_UNDERDETERMINED",
        "sm_gauge_group_derivation": "CONDITIONAL_ON_SU5_AND_CHOSEN_LIFT",
    }


def nu_cl_seesaw_correction() -> Dict[str, object]:
    return {
        "formula": "δ_seesaw = N_c × α_GUT_geo / (2 πkR)",
        "delta_seesaw": _DELTA_SEESAW, "delta_seesaw_pct": _DELTA_SEESAW * 100,
        "physical_meaning": "assumed shift, not derived from a specified Majorana boundary action",
        "planck_sum_mnu_consistent": None, "status": _CONDITIONAL,
    }


def nu_cl_spectrum() -> Dict[str, object]:
    return {
        "spectrum": {i: {"c_L_charged": cl_generation(i),
                         "c_L_nu": cl_generation(i) * (1 + _DELTA_SEESAW),
                         "delta_seesaw": _DELTA_SEESAW} for i in (1, 2, 3)},
        "formula": "c_{Lν_i} = c_L^(i) × (1 + δ_seesaw)",
        "seesaw_correction": nu_cl_seesaw_correction(), "status": _CONDITIONAL,
        "note": "No absolute neutrino mass or splitting prediction follows here.",
    }


def dirac_zero_mode_condition(c_L: float, pi_kR: float = PI_KR) -> Dict[str, object]:
    """Check the finite-interval LH mode at k=1; localisation is not selection."""
    f0 = rs1_zero_mode(c_L, 0.0, length=pi_kR)
    return {
        "c_L": c_L, "uv_localised": c_L > 0.5,
        "zero_mode_profile": "N exp(-c_L k y); kinetic density N² exp((1-2c_L)ky)",
        "z2_odd_bc": "f_L even, f_R odd; f_R(0)=f_R(L)=0",
        "profile_exponent": -c_L, "f0_L_uv_brane": f0,
        "normalisable": True, "z2_bc_selects_uv": False,
        "theorem_677D_a": "All real c_L survive this chiral domain on a finite regular interval.",
        "status": PILLAR_STATUS,
    }


def cl_generation_ladder_derivation(n_w: int = N_W, K_cs: int = K_CS,
                                    N_c: int = N_C, generation=None) -> Dict[str, object]:
    """Legacy API: conditional ladder evaluation, with no asserted CS mass shift."""
    if K_cs <= 0 or n_w <= 0:
        raise ValueError("K_cs and n_w must be positive")
    base, step = 1 - N_c / K_cs, 1 / (2 * K_cs)
    ladder = {i: base - (i - 1) * step for i in (1, 2, 3)}
    result = {
        "c_L_base": base, "step_size": step, "ladder": ladder,
        "derivation_steps": ["assume base", "assume step", "evaluate ladder"],
        "theorem_677D_b": "No specified action implies this ladder; a Wilson line is not a scalar bulk mass.",
        "status": _CONDITIONAL,
    }
    if generation is not None:
        if generation not in (1, 2, 3):
            raise ValueError("generation must be 1, 2, or 3")
        result["c_L_generation"] = ladder[generation]
    return result


def cl_residual_higher_order_bound(K_cs: int = K_CS, N_c: int = N_C) -> Dict[str, object]:
    """Compare residuals to heuristic scales, not a proved perturbative bound."""
    ladder = cl_generation_ladder_derivation(K_cs=K_cs, N_c=N_c)["ladder"]
    nlo, nnlo = (N_c / K_cs)**2, (N_c / K_cs)**3
    rows = {}
    for g, reference in _CL_BISECT.items():
        residual = abs(ladder[g] - reference)
        rows[g] = {"c_L_topo": ladder[g], "c_L_bisect": reference,
                   "abs_residual": residual, "within_NLO": residual <= nlo,
                   "within_NLO_plus_NNLO": residual <= nlo + nnlo,
                   "status": "HEURISTIC_SCALE_COMPARISON"}
    return {
        "K_CS": K_cs, "N_c": N_c, "NLO_bound": nlo, "NNLO_bound": nnlo,
        "combined_bound": nlo + nnlo, "per_generation": rows,
        "all_within_combined_bound": all(r["within_NLO_plus_NNLO"] for r in rows.values()),
        "observed_residuals_within_bound": all(r["within_NLO"] for r in rows.values()),
        "theorem_677D_c": "No remainder estimate has been derived; the legacy bound keys denote heuristic scales.",
        "bound_proved": False, "status": "HEURISTIC_NOT_A_PROVEN_BOUND",
    }


def cr_zero_mode_derivation(n_w: int = N_W, K_cs: int = K_CS) -> Dict[str, object]:
    """Conditional RH ladder, using c_R=-c relative to the signed Dirac mass."""
    if not isinstance(n_w, int) or isinstance(n_w, bool) or n_w <= 0:
        raise ValueError("n_w must be a positive integer")
    return {
        "spectrum": {n: {"c_R": 0.5 - n / (2 * n_w), "ir_localised": n > 0,
                         "flat": n == 0, "z2_even_survives": True,
                         "normalisation": "finite for every real signed mass"}
                     for n in range(n_w + 1)},
        "signed_mass_convention": "c_R=-c for the RH-even domain",
        "theorem_677D_d": "The discrete list is assumed, not selected by parity.",
        "n_w": n_w, "K_cs": K_cs, "status": _CONDITIONAL,
    }


def cr_z2even_survival_check(n_w: int = N_W) -> Dict[str, object]:
    spectrum = cr_zero_mode_derivation(n_w)["spectrum"]
    return {
        "levels": {n: {"c_R": row["c_R"], "c_R >= 0": row["c_R"] >= 0,
                       "normalisable": True} for n, row in spectrum.items()},
        "all_c_R_normalisable": True, "min_c_R": 0.0,
        "theorem_677D_e": "All real c are normalisable on finite L, including negative c; nonnegativity is not required.",
        "status": PILLAR_STATUS,
    }


def g4_bc_spectrum_report(n_w: int = N_W, K_cs: int = K_CS,
                          N_c: int = N_C) -> Dict[str, object]:
    ladder = cl_generation_ladder_derivation(n_w, K_cs, N_c)
    cr = cr_zero_mode_derivation(n_w, K_cs)
    return {
        "gap": "G4 — c_L/c_R from orbifold BC",
        "previous_status": "BC_SPECTRUM_ANALYTICALLY_DERIVED",
        "new_status": PILLAR_STATUS, "c_L_ladder": ladder["ladder"],
        "c_R_spectrum": {n: row["c_R"] for n, row in cr["spectrum"].items()},
        "ladder_status": _CONDITIONAL,
        "NLO_residual_bound": cl_residual_higher_order_bound(K_cs, N_c)["NLO_bound"],
        "all_c_R_normalisable": True,
        "nonuniqueness": rs1_nonuniqueness_example(),
        "lean4_file": "lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean",
        "lean4_scope": "arithmetic proxy only; no Dirac operator or domain is formalised",
        "remaining_open": ["additional dynamics selecting bulk masses, flavor couplings and internal gauge lift"],
    }


def what_is_claimed() -> List[str]:
    return [
        "The finite regular RS1 interval admits a self-adjoint chiral domain for every real c.",
        "Same parity and geometry do not select c; explicit normalised weighted overlaps differ.",
        "The historical ladder is conditional; its third entry is 35/37, not 69/74.",
        "Metric reflection does not select an internal SU(5) involution.",
    ]


def what_is_NOT_claimed() -> List[str]:
    return [
        "No first-principles generation ladder, masses or CKM targets are derived here.",
        "No APS index, Hilbert-space gauge equivalence, or formal Dirac proof is supplied.",
        "Heuristic NLO/NNLO scales and the seesaw shift are not action-derived error bounds.",
    ]


def fermion_closure_report() -> Dict[str, object]:
    return {
        "pillar": PILLAR_NUMBER, "title": PILLAR_TITLE, "version": VERSION,
        "status": PILLAR_STATUS, "theorem_a": cl_orbifold_spectrum(),
        "theorem_a_comparison": cl_bisection_comparison(),
        "theorem_b": su3_hilbert_equivalence(), "theorem_c": nu_cl_spectrum(),
        "nonuniqueness": rs1_nonuniqueness_example(),
        "toe_impact": {"yukawa_c_L_inputs": "not upgraded to derived",
                       "su3_derivation": "conditional internal lift",
                       "nu_spectrum": "conditional ansatz"},
        "claimed": what_is_claimed(), "not_claimed": what_is_NOT_claimed(),
        "residual_open": ["bulk-mass and flavor-coupling selection requires additional dynamics"],
    }
