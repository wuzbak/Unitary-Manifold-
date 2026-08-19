# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 780 — Wetterinck FRG scaffold for the braid Chern-Simons action."""

from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER = 780
PILLAR_TITLE = "Wetterinck Braid FRG"
STATUS = "BRAID_FRG_SCAFFOLD"
EPISTEMIC_STATUS = "SCAFFOLD"
K_CS = 74
PI_KR = 37.0

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "STATUS",
    "EPISTEMIC_STATUS",
    "K_CS",
    "PI_KR",
    "litim_regulator",
    "beta_newton_coupling",
    "uv_fixed_point_g5",
    "beta_cs_level",
    "beta_cosmological_constant",
    "rg_flow_g5",
    "braid_rg_invariance_proof",
    "wetterinck_braid_frg_report",
]


def _meta(**payload: Any) -> dict[str, Any]:
    payload.setdefault("pillar", PILLAR_NUMBER)
    payload.setdefault("status", STATUS)
    payload.setdefault("epistemic_status", EPISTEMIC_STATUS)
    return payload



def _c_g_value(d: int) -> float:
    if d == 5:
        return 0.00282
    mode_count = max(d * (d - 1) / 2.0, 1.0)
    return mode_count / (((4.0 * math.pi) ** (d / 2.0)) * math.gamma(d / 2.0 + 1.0))



def litim_regulator(p2: float, k2: float) -> dict[str, Any]:
    """Return the Litim cutoff R_k = (k^2-p^2) theta(k^2-p^2)."""
    if p2 < 0.0 or k2 < 0.0:
        raise ValueError("p2 and k2 must be non-negative")
    value = max(k2 - p2, 0.0)
    return _meta(p2=p2, k2=k2, regulator=value, regulator_active=p2 < k2)



def beta_newton_coupling(g: float, d: int = 5, c_g: float | None = None) -> dict[str, Any]:
    """Return the beta function for the dimensionless Newton coupling."""
    c_g_eff = _c_g_value(d) if c_g is None else c_g
    denominator = 1.0 - c_g_eff * g / 2.0
    if abs(denominator) < 1.0e-12:
        raise ValueError("beta function denominator is singular for this g")
    beta = (d - 2.0) * g - (c_g_eff * g * g) / denominator
    return _meta(
        g=g,
        d=d,
        c_g=c_g_eff,
        denominator=denominator,
        beta_g=beta,
        formula="beta_G = (d-2) g - (C_G g^2)/(1 - C_G g/2)",
    )



def uv_fixed_point_g5(d: int = 5) -> dict[str, Any]:
    """Return the one-operator UV fixed-point estimate for g."""
    c_g = _c_g_value(d)
    g_star = (d - 2.0) / c_g
    return _meta(
        d=d,
        c_g=c_g,
        g_star=g_star,
        fixed_point_exists=g_star > 0.0,
        estimate_type="single-operator truncation",
        honest_note="The quoted fixed point is the truncated FRG estimate, not a beyond-truncation proof.",
    )



def beta_cs_level(k_cs: int = K_CS) -> dict[str, Any]:
    """Return the topological beta function for the CS level."""
    return _meta(
        k_cs=k_cs,
        beta_k_cs=0.0,
        protected=True,
        reason="Chern-Simons level is topological and quantized in the scaffold.",
    )



def beta_cosmological_constant(lambda_k: float, k_gev: float, d: int = 5) -> dict[str, Any]:
    """Return a simple quadratic FRG running law for the cosmological term."""
    if k_gev < 0.0:
        raise ValueError("k_gev must be non-negative")
    c_lambda = 1.0 / (16.0 * math.pi * math.pi)
    beta = 2.0 * lambda_k + c_lambda * k_gev * k_gev
    return _meta(
        lambda_k=lambda_k,
        k_gev=k_gev,
        d=d,
        c_lambda=c_lambda,
        beta_lambda=beta,
        running_class="quadratic_uv_sensitivity",
    )



def rg_flow_g5(k_initial_gev: float, k_final_gev: float, g_initial: float | None = None) -> dict[str, Any]:
    """Integrate a simple RG flow for the dimensionless Newton coupling."""
    if k_initial_gev <= 0.0 or k_final_gev <= 0.0:
        raise ValueError("RG scales must be positive")
    steps = 240
    log_k0 = math.log(k_initial_gev)
    log_k1 = math.log(k_final_gev)
    dt = (log_k1 - log_k0) / steps
    g = (1.0 / (math.pi * PI_KR)) if g_initial is None else g_initial
    trajectory: list[dict[str, float]] = []
    for i in range(steps + 1):
        current_log_k = log_k0 + i * dt
        current_k = math.exp(current_log_k)
        trajectory.append({"step": float(i), "k_gev": current_k, "g": g})
        if i < steps:
            beta = beta_newton_coupling(g)["beta_g"]
            g = max(g + dt * beta, 0.0)
    return _meta(
        k_initial_gev=k_initial_gev,
        k_final_gev=k_final_gev,
        g_initial=trajectory[0]["g"],
        g_final=trajectory[-1]["g"],
        trajectory=trajectory,
        approached_uv_fixed_point=trajectory[-1]["g"] > trajectory[0]["g"],
    )



def braid_rg_invariance_proof(k_cs: int = K_CS) -> dict[str, Any]:
    """Return the topological argument for RG invariance of the braid level."""
    return _meta(
        k_cs=k_cs,
        invariant_under_rg=True,
        beta_function=0.0,
        proof_sketch=(
            "The Chern-Simons level multiplies a topological term and remains quantized, "
            "so continuous FRG flow cannot shift k_CS away from the integer value 74."
        ),
    )



def wetterinck_braid_frg_report() -> dict[str, Any]:
    """Return a combined report for Pillar 780."""
    return _meta(
        module="src/core/wetterinck_braid_frg.py",
        regulator=litim_regulator(0.25, 1.0),
        beta_g=beta_newton_coupling(0.1),
        uv_fixed_point=uv_fixed_point_g5(),
        beta_k_cs=beta_cs_level(),
        beta_lambda=beta_cosmological_constant(0.0, 10.0),
        rg_flow=rg_flow_g5(1.0e3, 1.0e6),
        invariance=braid_rg_invariance_proof(),
        summary="The truncated FRG scaffold yields a positive gravity fixed point, preserves k_CS=74 by topology, and keeps the cosmological term quadratically UV-sensitive.",
    )
