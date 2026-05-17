# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""SC4 extended flux-landscape scan with explicit PASS/TENSION/FALSIFIED routing.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

import math

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
N_FLUX_REQUIRED_MIN: int = 61

# Calibrated to the documented canonical point: |log10 residual| ≈ 0.31 at N_flux=37.
_BASE_N_FLUX = 37
_BASE_RESIDUAL = 0.31


def residual_log10_ratio(n_flux: int) -> float:
    """Model residual |log10(Λ_pred/Λ_obs)| as a monotone-decay function of N_flux."""
    if n_flux <= 0:
        raise ValueError("n_flux must be positive")
    return _BASE_RESIDUAL * math.sqrt(_BASE_N_FLUX / float(n_flux))


def classify_sc4_point(n_flux: int, residual_abs_log10: float) -> str:
    """Classify a scan point as PASS/TENSION/FALSIFIED."""
    if n_flux >= N_FLUX_REQUIRED_MIN and residual_abs_log10 <= 0.31:
        return "PASS"
    if residual_abs_log10 <= 0.50:
        return "TENSION"
    return "FALSIFIED"


def scan_flux_landscape(values: list[int] | tuple[int, ...] = N_FLUX_SCAN_VALUES) -> list[dict[str, object]]:
    """Return scan rows for candidate N_flux values."""
    rows: list[dict[str, object]] = []
    for n_flux in values:
        residual = residual_log10_ratio(n_flux)
        verdict = classify_sc4_point(n_flux=n_flux, residual_abs_log10=abs(residual))
        rows.append(
            {
                "n_flux": int(n_flux),
                "residual_abs_log10": abs(residual),
                "meets_naive_threshold": n_flux >= N_FLUX_REQUIRED_MIN,
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
        "rows": rows,
        "first_pass_n_flux": first_pass["n_flux"] if first_pass else None,
        "global_verdict": global_verdict,
        "status": "ARCHITECTURE_LIMIT" if global_verdict != "PASS" else "PASS_CONDITIONAL",
        "closure_blocker": "full_cy3_moduli_and_intersection_data_not_yet_available",
        "blocker_owner": "10D-closure-track",
        "stop_condition": "promote_when_full_cy3_embedding_fixates_flux_degeneracy_and_uv_coefficients",
    }
