# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Three-sector anomaly inflow scaffold on S¹/Z₂.

This module implements an explicit UV/bulk/IR bookkeeping model for the
candidate three-sector architecture:

    UV sector   : n_w = 5
    Bulk sector : n_parent = 6
    IR sector   : n_shadow = 7

It computes APS η-invariant boundary terms, a linear anomaly-coefficient
candidate (5 + 6 + 7 = 18), and an alternative η-weighted coefficient.
The module is intentionally honest: if multiple anomaly prescriptions produce
different required fermion counts, the result is OPEN_GAP, not DERIVED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.core.aps_spin_structure import eta_bar_from_cs_inflow

N_W_UV: int = 5
N_PARENT_BULK: int = 6
N_SHADOW_IR: int = 7
K_CS: int = N_W_UV**2 + N_SHADOW_IR**2  # 74


@dataclass(frozen=True)
class ThreeSectorAnomalyInput:
    n_uv: int = N_W_UV
    n_bulk: int = N_PARENT_BULK
    n_ir: int = N_SHADOW_IR


def eta_invariants_3sector(model: ThreeSectorAnomalyInput = ThreeSectorAnomalyInput()) -> Dict[str, float]:
    """Return boundary η-invariants at orbifold fixed points and bulk integer."""
    eta_uv = float(eta_bar_from_cs_inflow(model.n_uv))
    eta_ir = float(eta_bar_from_cs_inflow(model.n_ir))
    return {
        "eta_uv_y0": eta_uv,
        "eta_ir_yPiR": eta_ir,
        "bulk_instanton_number": float(model.n_bulk),
    }


def anomaly_coefficients_3sector(model: ThreeSectorAnomalyInput = ThreeSectorAnomalyInput()) -> Dict[str, float]:
    """Return competing anomaly coefficients under explicit assumptions."""
    etas = eta_invariants_3sector(model)
    linear_sum = float(model.n_uv + model.n_bulk + model.n_ir)
    eta_weighted = float(model.n_bulk + 2.0 * etas["eta_uv_y0"] + 2.0 * etas["eta_ir_yPiR"])
    return {
        "linear_sector_sum": linear_sum,          # candidate: 18
        "eta_weighted_sum": eta_weighted,         # alternative candidate
        "k_cs": float(model.n_uv**2 + model.n_ir**2),
    }


def required_weyl_fermions_3sector(model: ThreeSectorAnomalyInput = ThreeSectorAnomalyInput()) -> Dict[str, object]:
    """Assess whether anomaly cancellation uniquely requires 18 Weyl fermions."""
    coeffs = anomaly_coefficients_3sector(model)
    n_linear = int(round(coeffs["linear_sector_sum"]))
    n_eta = int(round(coeffs["eta_weighted_sum"]))
    unique = n_linear == n_eta == 18
    return {
        "required_by_linear_model": n_linear,
        "required_by_eta_weighted_model": n_eta,
        "is_unique_at_18": unique,
        "status": "DERIVED" if unique else "OPEN_GAP",
        "epistemic_note": (
            "OPEN_GAP: competing anomaly prescriptions do not uniquely force N=18."
            if not unique
            else "DERIVED: both anomaly prescriptions force N=18."
        ),
    }


def anomaly_inflow_report_3sector(model: ThreeSectorAnomalyInput = ThreeSectorAnomalyInput()) -> Dict[str, object]:
    """Return machine-readable summary for DERIVATION_STATUS integration."""
    etas = eta_invariants_3sector(model)
    coeffs = anomaly_coefficients_3sector(model)
    req = required_weyl_fermions_3sector(model)
    return {
        "model": {
            "n_uv": model.n_uv,
            "n_bulk": model.n_bulk,
            "n_ir": model.n_ir,
            "k_cs": model.n_uv**2 + model.n_ir**2,
        },
        "eta_invariants": etas,
        "coefficients": coeffs,
        "fermion_requirement": req,
    }

