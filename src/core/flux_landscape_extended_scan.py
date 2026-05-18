# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""SC4 flux-landscape closure scan with explicit 10D dependency routing.

�� ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

import math

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.p28_lambda_10d_closure import DUAL_FLUX_MULTIPLICITY, REQUIRED_N_FLUX_MIN, effective_flux_sufficiency
from src.tend.cc_architecture_limit import K_CS, LAMBDA_OBS_MPLANCK4, N_W, PI_KR

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "N_FLUX_SCAN_VALUES",
    "N_FLUX_REQUIRED_MIN",
    "residual_log10_ratio",
    "classify_sc4_point",
    "scan_flux_landscape",
    "sc4_closure_summary",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
N_FLUX_SCAN_VALUES: tuple[int, ...] = (37, 48, 61, 74, 100, 150, 200, 500, 1000)
N_FLUX_REQUIRED_MIN: int = REQUIRED_N_FLUX_MIN
SC4_PASS_RESIDUAL_THRESHOLD: float = 0.31
SC4_TENSION_RESIDUAL_THRESHOLD: float = 0.50


def _lambda_pred_for_base_flux(n_flux: int, c_uv_total: float) -> float:
    """Compute Λ prediction for a candidate base flux count."""
    if n_flux <= 0:
        raise ValueError("n_flux must be positive")
    if c_uv_total <= 0.0:
        raise ValueError("c_uv_total must be positive")

    casimir_coeff = float(K_CS * N_W) / (24.0 * math.pi**2)
    rs1_warp_factor = math.exp(-4.0 * PI_KR)
    effective_flux_channels = n_flux * DUAL_FLUX_MULTIPLICITY
    topological_partition = float(effective_flux_channels * (N_W + 2))
    return casimir_coeff * rs1_warp_factor / (c_uv_total * topological_partition)


def residual_log10_ratio(n_flux: int) -> float:
    """Return |log10(Λ_pred/Λ_obs)| using explicit 10D UV closure data."""
    uv_report = full_10d_uv_closure_report()
    c_uv_total = float(uv_report["step4_c_uv"]["c_uv_total"])
    lambda_pred = _lambda_pred_for_base_flux(n_flux=n_flux, c_uv_total=c_uv_total)
    return abs(math.log10(lambda_pred / LAMBDA_OBS_MPLANCK4))


def classify_sc4_point(n_flux: int, residual_abs_log10: float) -> str:
    """Classify a scan point as PASS/TENSION/FALSIFIED."""
    effective = effective_flux_sufficiency(base_n_flux=n_flux)
    if effective["meets_bp_threshold"] and residual_abs_log10 <= SC4_PASS_RESIDUAL_THRESHOLD:
        return "PASS"
    if residual_abs_log10 <= SC4_TENSION_RESIDUAL_THRESHOLD:
        return "TENSION"
    return "FALSIFIED"


def scan_flux_landscape(values: list[int] | tuple[int, ...] = N_FLUX_SCAN_VALUES) -> list[dict[str, object]]:
    """Return full scan rows for candidate N_flux values."""
    rows: list[dict[str, object]] = []
    uv_report = full_10d_uv_closure_report()
    c_uv_total = float(uv_report["step4_c_uv"]["c_uv_total"])

    for n_flux in values:
        residual = residual_log10_ratio(n_flux)
        eff = effective_flux_sufficiency(base_n_flux=n_flux)
        lambda_pred = _lambda_pred_for_base_flux(n_flux=n_flux, c_uv_total=c_uv_total)
        verdict = classify_sc4_point(n_flux=n_flux, residual_abs_log10=residual)
        rows.append(
            {
                "n_flux": int(n_flux),
                "effective_n_flux": int(eff["effective_n_flux"]),
                "residual_abs_log10": residual,
                "lambda_pred_mplanck4": lambda_pred,
                "meets_naive_threshold": bool(eff["meets_bp_threshold"]),
                "spacing_below_lambda_obs": bool(eff["spacing_below_lambda_obs"]),
                "verdict": verdict,
            }
        )
    return rows


def sc4_closure_summary() -> dict[str, object]:
    """Return SC4 closure packet with explicit blocker/owner/stop-condition."""
    rows = scan_flux_landscape()
    pass_rows = [r for r in rows if r["verdict"] == "PASS"]
    first_pass = min(pass_rows, key=lambda r: r["n_flux"]) if pass_rows else None

    global_verdict = "PASS" if first_pass is not None else "TENSION"

    return {
        "scan_id": "SC4_FLUX_LANDSCAPE_EXTENDED_SCAN",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "required_n_flux_min": N_FLUX_REQUIRED_MIN,
        "dual_flux_multiplicity": DUAL_FLUX_MULTIPLICITY,
        "rows": rows,
        "first_pass_n_flux": first_pass["n_flux"] if first_pass else None,
        "first_pass_effective_n_flux": first_pass["effective_n_flux"] if first_pass else None,
        "global_verdict": global_verdict,
        "status": "CLOSED_WITH_EFFECTIVE_FLUX_CHANNELS" if global_verdict == "PASS" else "ARCHITECTURE_LIMIT",
        "closure_blocker": (
            "none"
            if global_verdict == "PASS"
            else "full_cy3_moduli_and_intersection_data_not_yet_available"
        ),
        "blocker_owner": "10D-closure-track",
        "stop_condition": "promote_when_effective_flux_channels_and_lambda_residual_gates_pass",
    }
