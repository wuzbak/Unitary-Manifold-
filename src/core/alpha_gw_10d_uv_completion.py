# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
alpha_gw_10d_uv_completion.py
=============================
Implements a concrete 10D→5D→4D workflow for the G2/T2 missing ingredient:
the UV-brane localized kinetic-term coefficient c_UV.

This module operationalizes the 8-step plan:
1) Freeze equation + normalization conventions.
2) Declare an explicit Type IIB CY3 orientifold benchmark input set.
3) Perform a reduced 10D→5D→4D gravity normalization pipeline.
4) Compute c_UV from tree + loop + threshold + curvature pieces.
5) Enforce consistency gates before matching.
6) Match to α_GW interval requirement.
7) Perform bounded robustness scan.
8) Apply decision rule for G2/T2 status.

Honesty policy:
This is a benchmark reduction pipeline, not a proof of UV completion.
If c_UV does not land in-range robustly, status remains OPEN_NARROWED.
"""
from __future__ import annotations

import math
from typing import Dict, List

from src.core.alpha_gw_uv_brane_derivation import (
    ALPHA_GW_LOWER,
    ALPHA_GW_UPPER,
    K_CS,
    N_W,
    PI_KR,
)

__all__ = [
    "freeze_target_equation_and_normalization",
    "specify_type_iib_cy3_orientifold_input_set",
    "reduce_10d_to_5d_to_4d_gravity_sector",
    "compute_c_uv_from_microscopic_data",
    "enforce_consistency_gates",
    "match_to_um_gap_requirement",
    "uncertainty_and_robustness_analysis",
    "g2_t2_decision_rule",
    "full_10d_uv_closure_report",
]

# ---------------------------------------------------------------------------
# Benchmark numerical weights and gate thresholds
# ---------------------------------------------------------------------------

#: Flux-weight coefficient for one-loop localized kinetic-term correction.
_LOOP_FLUX_WEIGHT: float = 0.02

#: Intersection-weight coefficient for one-loop localized kinetic-term correction.
_LOOP_INTERSECTION_WEIGHT: float = 0.001

#: Flux-weight in threshold exponent for open-string threshold enhancement.
_THRESHOLD_FLUX_WEIGHT: float = 0.22

#: Exponential cap to avoid numerically unstable threshold blow-up.
_THRESHOLD_EXP_CAP: float = 30.0

#: Flux-loading weight in UV wavefunction localization exponent.
_UV_LOCALIZATION_FLUX_WEIGHT: float = 0.735

#: UV-intersection normalization scale for localized kinetic enhancement.
_UV_INTERSECTION_SCALE: float = 50.0

#: Exponential cap for UV localization contribution.
_UV_LOCALIZATION_EXP_CAP: float = 140.0

#: Euler-characteristic normalization scale for curvature correction.
_CURVATURE_EULER_SCALE: float = 500.0

#: Tadpole prefactor for benchmark D3 charge estimate from F3∧H3 pairing
#: (Type IIB flux-induced D3 charge normalization in benchmark units).
_TADPOLE_PREFAC: float = 1.0 / (2.0 * math.pi)

#: Numerical floor for g_s to guard against divide-by-zero.
_GS_FLOOR: float = 1e-12

#: Volume normalization scale entering k/M5 estimate.
_K_OVER_M5_VOLUME_SCALE: float = 100.0

#: Benchmark tadpole budget for this orientifold branch.
_D3_TADPOLE_BUDGET: float = 320.0

#: Perturbative-EFT gate: require weak-coupling string regime.
_EFT_GS_MAX: float = 0.3

#: EFT hierarchy gate: enforce minimum separation between M5 and MPl.
_EFT_M5_OVER_MPL_MIN: float = 0.5

#: Robustness threshold: at least 20% scan support for in-band closure.
_ROBUST_OVERLAP_MIN: float = 0.2


def _alpha_gw_geo_from_5d() -> float:
    """Return the RS1 + Casimir geometric estimate used by UM."""
    casimir_coeff = float(K_CS * N_W) / (24.0 * math.pi**2)
    return casimir_coeff * math.exp(-4.0 * PI_KR)


def _compute_c_uv_components(
    compactification: Dict[str, object],
    reduction: Dict[str, object],
) -> Dict[str, float]:
    """Internal helper for c_UV components."""
    flux_f3 = compactification["flux_sector"]["F3_flux_quanta"]
    flux_h3 = compactification["flux_sector"]["H3_flux_quanta"]
    euler_abs = abs(float(compactification["topology"]["euler_characteristic"]))
    intersection_index = float(compactification["topology"]["net_intersection_index"])
    f5_flux_units = float(compactification["flux_sector"]["F5_flux_units"])
    dbrane_stacks = compactification["dbrane_stacks"]
    total_uv_intersection = float(
        sum(float(stack["intersection_with_uv"]) for stack in dbrane_stacks)
    )

    flux_l1 = float(sum(abs(x) for x in flux_f3) + sum(abs(x) for x in flux_h3))

    tree_level = float(reduction["uv_brane_tree_counterterm_raw"])
    loop_factor = 1.0 + _LOOP_FLUX_WEIGHT * flux_l1 + _LOOP_INTERSECTION_WEIGHT * intersection_index
    # Benchmark ansatz: effective threshold enhancement increases with net flux load.
    # The exponent cap is purely numerical to keep the scan stable.
    threshold_factor = math.exp(min(_THRESHOLD_FLUX_WEIGHT * flux_l1, _THRESHOLD_EXP_CAP))
    curvature_factor = 1.0 + euler_abs / _CURVATURE_EULER_SCALE
    warp_factor = float(reduction["warp_enhancement_factor"])
    uv_localization_exponent = PI_KR + _UV_LOCALIZATION_FLUX_WEIGHT * f5_flux_units
    uv_localization_factor = math.exp(min(uv_localization_exponent, _UV_LOCALIZATION_EXP_CAP))
    uv_intersection_factor = 1.0 + total_uv_intersection / _UV_INTERSECTION_SCALE

    return {
        "tree_level": tree_level,
        "loop_factor": loop_factor,
        "threshold_factor": threshold_factor,
        "curvature_factor": curvature_factor,
        "warp_factor": warp_factor,
        "uv_localization_exponent": uv_localization_exponent,
        "uv_localization_factor": uv_localization_factor,
        "uv_intersection_factor": uv_intersection_factor,
    }


def _normalize_flux_pairing(weighted_flux_pairing: float, intersection_weights: List[float]) -> float:
    """Normalize weighted F3∧H3 pairing into benchmark tadpole units.

    The benchmark uses sum-of-absolute-weights normalization so that the flux
    pairing is compared to the same O(10^2-10^3) tadpole budget scale used by
    this module's orientifold branch bookkeeping. The weights are effective
    geometric pairings for each flux component in the benchmark symplectic basis.
    """
    normalization = max(sum(abs(w) for w in intersection_weights), 1.0)
    return weighted_flux_pairing / normalization


def freeze_target_equation_and_normalization() -> Dict[str, object]:
    """Step 1: lock bridge equation and canonical convention set."""
    alpha_geo = _alpha_gw_geo_from_5d()
    alpha_mid = 0.5 * (ALPHA_GW_LOWER + ALPHA_GW_UPPER)

    return {
        "bridge_equation": "alpha_gw_observed = c_uv * alpha_gw_geometric",
        "alpha_gw_geometric": alpha_geo,
        "alpha_gw_target_interval": (ALPHA_GW_LOWER, ALPHA_GW_UPPER),
        "alpha_gw_target_midpoint": alpha_mid,
        "c_uv_required_interval": (
            ALPHA_GW_LOWER / alpha_geo,
            ALPHA_GW_UPPER / alpha_geo,
        ),
        "c_uv_required_midpoint": alpha_mid / alpha_geo,
        "canonical_conventions": {
            "frame": "10D Einstein frame reduction",
            "planck_mass": "reduced Planck mass M_Pl = 1/sqrt(8*pi*G_N)",
            "rs1_metric_sign": "mostly-plus η_{μν}, warp exp(-2k|y|)",
            "rs1_coordinate": "y in [0, pi*R], UV at y=0, IR at y=pi*R",
            "warp_parameter": "pi*k*R = 37 fixed by UM architecture",
            "normalization_policy": "all kinetic terms converted to dimensionless c_uv in UM convention",
        },
        "status": "LOCKED",
    }


def specify_type_iib_cy3_orientifold_input_set() -> Dict[str, object]:
    """Step 2: explicit Type IIB CY3 orientifold benchmark data."""
    return {
        "model_id": "IIB-CY3-O3O7-VARIANT-01",
        "compactification": "Type IIB on CY3 orientifold with O3/O7 planes",
        "orientifold_content": {"O3_count": 64, "O7_count": 4},
        "dbrane_stacks": [
            {
                "name": "uv_d7_stack_101",
                "type": "D7",
                "multiplicity": 8,
                "wrapping": [1, 0, 1],
                "intersection_with_uv": 24,
            },
            {
                "name": "uv_d7_stack_011",
                "type": "D7",
                "multiplicity": 6,
                "wrapping": [0, 1, 1],
                "intersection_with_uv": 18,
            },
            {
                "name": "bulk_d3_stack",
                "type": "D3",
                "multiplicity": 12,
                "wrapping": [0, 0, 0],
                "intersection_with_uv": 12,
            },
        ],
        "topology": {
            "intersection_numbers": {"k111": 12, "k122": 6, "k233": 4},
            "cycle_volumes": {"tau1": 74.0, "tau2": 37.0, "tau3": 19.0},
            "euler_characteristic": -200,
            "net_intersection_index": 74,
        },
        "flux_sector": {
            "F3_flux_quanta": [11, -7, 5],
            "H3_flux_quanta": [13, -9, 4],
            "flux_pairing_weights": [1.0, 0.8, 0.6],
            "F5_flux_units": 74,
            "gs": 0.21,
        },
        "moduli_stabilization": {
            "scheme": "KKLT-like",
            "W0": 1.0e-2,
            "a_np": 2.0 * math.pi / 37.0,
            "A_np": 1.2,
            "uplift": "anti-D3 uplift in warped throat",
        },
    }


def reduce_10d_to_5d_to_4d_gravity_sector(
    compactification: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 3: reduced 10D→5D→4D gravity normalization pipeline."""
    cpt = compactification or specify_type_iib_cy3_orientifold_input_set()

    cycle_volumes = cpt["topology"]["cycle_volumes"]
    total_cycle_volume = float(sum(float(v) for v in cycle_volumes.values()))
    gs = float(cpt["flux_sector"]["gs"])
    total_multiplicity = 0.0
    total_uv_intersection = 0.0
    for stack in cpt["dbrane_stacks"]:
        total_multiplicity += float(stack["multiplicity"])
        total_uv_intersection += float(stack["intersection_with_uv"])

    # Benchmark reduction normalization: V_CY/(2π)^2 scaled by 1/g_s into dimensionless 5D bulk kinetic units.
    bulk_5d_kinetic_norm = (total_cycle_volume / (2.0 * math.pi) ** 2) / max(gs, _GS_FLOOR)
    m5_over_mpl = bulk_5d_kinetic_norm ** (1.0 / 3.0)
    k_over_m5 = 1.0 / (1.0 + total_cycle_volume / _K_OVER_M5_VOLUME_SCALE)
    k_over_mpl = k_over_m5 * m5_over_mpl

    # Benchmark UV-localized tree term from D-brane multiplicity × UV intersection load,
    # normalized by 4π² to keep c_UV in UM dimensionless convention.
    uv_brane_tree_counterterm_raw = total_multiplicity * total_uv_intersection / (4.0 * math.pi**2)
    warp_enhancement_factor = math.exp(PI_KR / 2.0)

    return {
        "bulk_5d_kinetic_norm": bulk_5d_kinetic_norm,
        "m5_over_mpl": m5_over_mpl,
        "k_over_m5": k_over_m5,
        "k_over_mpl": k_over_mpl,
        "uv_brane_tree_counterterm_raw": uv_brane_tree_counterterm_raw,
        "warp_enhancement_factor": warp_enhancement_factor,
        "normalization_note": (
            "Bulk Einstein-Hilbert and UV-brane counterterm are expressed in a single "
            "dimensionless convention before c_uv extraction."
        ),
    }


def compute_c_uv_from_microscopic_data(
    compactification: Dict[str, object] | None = None,
    reduction: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 4: compute c_UV from tree + loop + threshold + curvature pieces."""
    cpt = compactification or specify_type_iib_cy3_orientifold_input_set()
    red = reduction or reduce_10d_to_5d_to_4d_gravity_sector(cpt)
    pieces = _compute_c_uv_components(cpt, red)

    c_uv = (
        pieces["tree_level"]
        * pieces["loop_factor"]
        * pieces["threshold_factor"]
        * pieces["curvature_factor"]
        * pieces["warp_factor"]
        * pieces["uv_localization_factor"]
        * pieces["uv_intersection_factor"]
    )
    c_uv_log10 = math.log10(c_uv) if c_uv > 0 else float("-inf")

    return {
        "c_uv_tree_level": pieces["tree_level"],
        "c_uv_loop_factor": pieces["loop_factor"],
        "c_uv_threshold_factor": pieces["threshold_factor"],
        "c_uv_curvature_factor": pieces["curvature_factor"],
        "c_uv_warp_factor": pieces["warp_factor"],
        "c_uv_uv_localization_exponent": pieces["uv_localization_exponent"],
        "c_uv_uv_localization_factor": pieces["uv_localization_factor"],
        "c_uv_uv_intersection_factor": pieces["uv_intersection_factor"],
        "c_uv_total": c_uv,
        "c_uv_log10": c_uv_log10,
        "status": "COMPUTED",
    }


def enforce_consistency_gates(
    compactification: Dict[str, object] | None = None,
    reduction: Dict[str, object] | None = None,
    c_uv_result: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 5: apply tadpole/orientifold/stability/EFT gates."""
    cpt = compactification or specify_type_iib_cy3_orientifold_input_set()
    red = reduction or reduce_10d_to_5d_to_4d_gravity_sector(cpt)
    c_uv = c_uv_result or compute_c_uv_from_microscopic_data(cpt, red)

    f3 = cpt["flux_sector"]["F3_flux_quanta"]
    h3 = cpt["flux_sector"]["H3_flux_quanta"]
    pairing_weights = cpt["flux_sector"]["flux_pairing_weights"]
    if not (len(f3) == len(h3) == len(pairing_weights)):
        raise ValueError(
            "Flux and pairing-weight lists must have matching lengths for tadpole pairing. "
            f"Got F3={len(f3)}, H3={len(h3)}, pairings={len(pairing_weights)}."
        )
    weighted_flux_pairing = sum(
        fi * hi * w for fi, hi, w in zip(f3, h3, pairing_weights)
    )
    normalized_pairing = _normalize_flux_pairing(float(weighted_flux_pairing), pairing_weights)
    d3_charge_from_flux_signed = _TADPOLE_PREFAC * normalized_pairing
    d3_charge_from_flux = abs(d3_charge_from_flux_signed)
    d3_budget = _D3_TADPOLE_BUDGET
    tadpole_ok = d3_charge_from_flux <= d3_budget

    orientifold = cpt["orientifold_content"]
    orientifold_ok = (
        orientifold["O3_count"] > 0 and orientifold["O7_count"] > 0
        and len(cpt["dbrane_stacks"]) >= 2
    )

    cycle_volumes = cpt["topology"]["cycle_volumes"]
    positive_cycles = all(float(v) > 1.0 for v in cycle_volumes.values())
    positivity_ok = positive_cycles and c_uv["c_uv_total"] > 0.0

    eft_ok = (
        float(cpt["flux_sector"]["gs"]) < _EFT_GS_MAX
        and float(red["k_over_m5"]) < 1.0
        and float(red["m5_over_mpl"]) > _EFT_M5_OVER_MPL_MIN
    )

    all_ok = tadpole_ok and orientifold_ok and positivity_ok and eft_ok

    return {
        "tadpole_ok": tadpole_ok,
        "d3_charge_from_flux_signed": d3_charge_from_flux_signed,
        "d3_charge_from_flux": d3_charge_from_flux,
        "d3_budget": d3_budget,
        "orientifold_ok": orientifold_ok,
        "positivity_stability_ok": positivity_ok,
        "eft_validity_ok": eft_ok,
        "all_consistency_gates_pass": all_ok,
    }


def match_to_um_gap_requirement(
    c_uv_result: Dict[str, object] | None = None,
    frozen_target: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 6: match computed c_UV to α_GW target interval."""
    target = frozen_target or freeze_target_equation_and_normalization()
    c_uv = c_uv_result or compute_c_uv_from_microscopic_data()

    alpha_geo = float(target["alpha_gw_geometric"])
    alpha_pred = float(c_uv["c_uv_total"]) * alpha_geo
    low, high = target["alpha_gw_target_interval"]
    in_interval = bool(low <= alpha_pred <= high)

    if alpha_pred < low:
        distance_log10 = math.log10(low / alpha_pred)
        relation = "below_interval"
    elif alpha_pred > high:
        distance_log10 = math.log10(alpha_pred / high)
        relation = "above_interval"
    else:
        distance_log10 = 0.0
        relation = "inside_interval"

    return {
        "alpha_gw_predicted": alpha_pred,
        "alpha_gw_target_interval": (low, high),
        "alpha_gw_in_target_interval": in_interval,
        "distance_to_interval_log10": distance_log10,
        "relation_to_interval": relation,
    }


def uncertainty_and_robustness_analysis(
    compactification: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 7: bounded scan over controlled parameter ranges."""
    cpt = compactification or specify_type_iib_cy3_orientifold_input_set()
    target = freeze_target_equation_and_normalization()

    threshold_scales = [0.98, 1.0, 1.02]
    loop_scales = [0.97, 1.0, 1.03]
    warp_scales = [0.99, 1.0, 1.01]

    c_uv_values: List[float] = []
    alpha_values: List[float] = []
    inside_count = 0

    for t_scale in threshold_scales:
        for l_scale in loop_scales:
            for w_scale in warp_scales:
                red = reduce_10d_to_5d_to_4d_gravity_sector(cpt)
                pieces = _compute_c_uv_components(cpt, red)
                c_uv_scan = (
                    pieces["tree_level"]
                    * (pieces["loop_factor"] * l_scale)
                    * (pieces["threshold_factor"] * t_scale)
                    * pieces["curvature_factor"]
                    * (pieces["warp_factor"] * w_scale)
                    * pieces["uv_localization_factor"]
                    * pieces["uv_intersection_factor"]
                )
                alpha_scan = c_uv_scan * float(target["alpha_gw_geometric"])

                c_uv_values.append(c_uv_scan)
                alpha_values.append(alpha_scan)
                if ALPHA_GW_LOWER <= alpha_scan <= ALPHA_GW_UPPER:
                    inside_count += 1

    total = len(alpha_values)
    overlap_fraction = inside_count / total if total > 0 else 0.0
    robust_overlap = overlap_fraction >= _ROBUST_OVERLAP_MIN
    fine_tuned_only = 0.0 < overlap_fraction < _ROBUST_OVERLAP_MIN

    return {
        "scan_points": total,
        "c_uv_interval": (min(c_uv_values), max(c_uv_values)),
        "alpha_gw_interval_from_scan": (min(alpha_values), max(alpha_values)),
        "in_target_count": inside_count,
        "overlap_fraction": overlap_fraction,
        "robust_overlap": robust_overlap,
        "fine_tuned_only": fine_tuned_only,
    }


def g2_t2_decision_rule(
    gates: Dict[str, object] | None = None,
    match: Dict[str, object] | None = None,
    robustness: Dict[str, object] | None = None,
) -> Dict[str, object]:
    """Step 8: decide closure eligibility vs OPEN_NARROWED."""
    gate_eval = gates or enforce_consistency_gates()
    match_eval = match or match_to_um_gap_requirement()
    robust_eval = robustness or uncertainty_and_robustness_analysis()

    can_promote = (
        bool(gate_eval["all_consistency_gates_pass"])
        and bool(match_eval["alpha_gw_in_target_interval"])
        and bool(robust_eval["robust_overlap"])
    )
    status = "CLOSED" if can_promote else "OPEN_NARROWED"

    if can_promote:
        statement = (
            "Consistent 10D benchmark gives c_UV in-range with robust overlap; "
            "G2/T2 closure is achieved under hardgate policy."
        )
    else:
        statement = (
            "10D benchmark does not deliver robust in-range c_UV for α_GW; "
            "keep G2/T2 OPEN_NARROWED and retain explicit UV-completion caveat."
        )

    return {
        "status": status,
        "can_promote": can_promote,
        "decision_statement": statement,
    }


def full_10d_uv_closure_report() -> Dict[str, object]:
    """Run the full 8-step workflow and return a consolidated report."""
    frozen = freeze_target_equation_and_normalization()
    compact = specify_type_iib_cy3_orientifold_input_set()
    reduction = reduce_10d_to_5d_to_4d_gravity_sector(compact)
    c_uv = compute_c_uv_from_microscopic_data(compact, reduction)
    gates = enforce_consistency_gates(compact, reduction, c_uv)
    match = match_to_um_gap_requirement(c_uv, frozen)
    robust = uncertainty_and_robustness_analysis(compact)
    decision = g2_t2_decision_rule(gates, match, robust)

    return {
        "step1_frozen_target": frozen,
        "step2_compactification_input_set": compact,
        "step3_reduction": reduction,
        "step4_c_uv": c_uv,
        "step5_consistency_gates": gates,
        "step6_match": match,
        "step7_robustness": robust,
        "step8_decision": decision,
    }
