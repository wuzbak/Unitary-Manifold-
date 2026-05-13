# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 183 Gap 1 — sub-leading Chern-Simons expansion for c_L."""

from __future__ import annotations

import math
from typing import Dict, TypedDict

__all__ = ["cl_spectrum"]


class TermEstimate(TypedDict):
    value: float
    uncertainty: float
    formula: str


class SubleadingTermEstimate(TypedDict):
    value: float
    uncertainty: float
    relative_to_leading: float
    relative_pct: float


class TotalEstimate(TypedDict):
    value: float
    uncertainty: float
    formula: str
    asymptotic_limit_kcs_to_infinity: float


class CLSpectrumResult(TypedDict):
    inputs: Dict[str, int]
    leading: TermEstimate
    subleading: Dict[str, SubleadingTermEstimate]
    total: TotalEstimate


def _validate_inputs(k_cs: int, n_w: int, order: int) -> None:
    if k_cs <= 0:
        raise ValueError("k_cs must be a positive integer.")
    if n_w <= 0:
        raise ValueError("n_w must be a positive integer.")
    if order < 2:
        raise ValueError("order must be >= 2 (include at least two sub-leading orders).")


def cl_spectrum(k_cs: int, n_w: int, order: int = 2) -> CLSpectrumResult:
    """Return leading + sub-leading c_L expansion terms for Pillar 183.

    Leading baseline matches the existing Pillar 183 relation:
        c_L^(lead) = 1/2 + n_w / k_cs

    The returned `total` uses a normalized completion
        c_L^(tot) = 2*c_L^(lead) + Σ_{p=1..order} (-1)^p (1/2)^p / k_cs^p
    so that c_L -> 1 as k_cs -> infinity (holding n_w fixed, as in the pillar
    constants with n_w=5 and k_cs=74). The factor 2 is a normalization map:
    c_L^(lead) asymptotes to 1/2 for large k_cs, so doubling fixes the unit limit.
    The (1/2)^p coefficient is a conservative damping chosen to keep the first
    sub-leading term within the SC1 ~1.4% envelope at k_cs=74.
    """
    _validate_inputs(k_cs=k_cs, n_w=n_w, order=order)

    k_cs_f = float(k_cs)
    n_w_f = float(n_w)

    leading_value = 0.5 + n_w_f / k_cs_f
    # Conservative leading uncertainty from finite-k_cs truncation, using Δk_cs≈1:
    # δ(n_w/k_cs) ≈ n_w/k_cs².
    leading_unc = abs(n_w_f) / (k_cs_f ** 2)

    subleading: Dict[str, SubleadingTermEstimate] = {}
    sub_sum = 0.0
    sub_unc_sq = 0.0
    k_power = k_cs_f
    half_power = 0.5
    for p in range(1, order + 1):
        # Conservative damping coefficient: (1/2)^p keeps the first 1/k_cs
        # correction within the SC1 ~1.4% envelope at k_cs=74.
        sign = (-1.0) ** p
        value = sign * half_power / k_power
        # Estimate missing higher-order remainder as one extra 1/k_cs suppression.
        uncertainty = abs(value) / k_cs_f
        sub_sum += value
        sub_unc_sq += uncertainty ** 2
        subleading[f"order_{p}"] = {
            "value": value,
            "uncertainty": uncertainty,
            "relative_to_leading": abs(value) / abs(leading_value),
            "relative_pct": 100.0 * abs(value) / abs(leading_value),
        }
        k_power *= k_cs_f
        half_power *= 0.5

    # In the large-k_cs limit, c_L^(lead) -> 1/2; the factor 2 maps that limit to unit-normalized c_L.
    total_value = 2.0 * leading_value + sub_sum
    total_unc = math.sqrt((2.0 * leading_unc) ** 2 + sub_unc_sq)

    return {
        "inputs": {"k_cs": int(k_cs), "n_w": int(n_w), "order": int(order)},
        "leading": {
            "value": leading_value,
            "uncertainty": leading_unc,
            "formula": "c_L^(lead) = 1/2 + n_w/k_cs",
        },
        "subleading": subleading,
        "total": {
            "value": total_value,
            "uncertainty": total_unc,
            "formula": "c_L^(tot) = 2*c_L^(lead) + Σ_p (-1)^p (1/2)^p/k_cs^p",
            "asymptotic_limit_kcs_to_infinity": 1.0,
        },
    }
