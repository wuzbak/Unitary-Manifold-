# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""A3 Higgs naturalness multi-loop extension with explicit verdict routing.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

import math

from src.core.higgs_naturalness_5d_fixedpoint import M_PL_GEV, kk_higgs_naturalness

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "K_SWEEP",
    "two_loop_qcd_factor",
    "higgs_naturalness_point",
    "higgs_naturalness_sweep",
    "higgs_naturalness_extended_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
K_SWEEP: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20)


def two_loop_qcd_factor(alpha_s_mz: float = 0.113) -> float:
    """Simple 2-loop correction factor used for the adjacent-track extension."""
    return 1.0 + 0.30 * alpha_s_mz


def _verdict_from_delta(delta_total: float) -> str:
    if delta_total < 100.0:
        return "PASS"
    if delta_total < 200.0:
        return "TENSION"
    return "FALSIFIED"


def _status_from_verdict(verdict: str) -> str:
    if verdict == "PASS":
        return "DERIVED_PARTIAL"
    if verdict == "TENSION":
        return "ARCHITECTURE_LIMIT_TENSION"
    return "ARCHITECTURE_LIMIT_FAILED"


def higgs_naturalness_point(k: float, n_modes: int = 10) -> dict[str, object]:
    """Evaluate one k-point in the extended A3 naturalness lane."""
    r = 37.0 / math.pi / k
    base = kk_higgs_naturalness(k=k, R=r, N_modes=n_modes)
    factor = two_loop_qcd_factor()

    delta_total = float(base["tuning_Delta"]) * factor
    m_kk = float(base["M_KK_GeV"])
    is_uv_cutoff = (m_kk / M_PL_GEV) < 1e-12
    verdict = _verdict_from_delta(delta_total)

    return {
        "k": k,
        "R": r,
        "N_modes": n_modes,
        "delta_base": float(base["tuning_Delta"]),
        "two_loop_factor": factor,
        "delta_total": delta_total,
        "M_KK_GeV": m_kk,
        "kk_tower_acts_as_uv_cutoff": is_uv_cutoff,
        "verdict": verdict,
        "status": _status_from_verdict(verdict),
    }


def higgs_naturalness_sweep() -> list[dict[str, object]]:
    """Evaluate the canonical k sweep for the A3 lane."""
    return [higgs_naturalness_point(k=k) for k in K_SWEEP]


def higgs_naturalness_extended_report() -> dict[str, object]:
    """Return integrated A3 extension report."""
    rows = higgs_naturalness_sweep()
    canonical = higgs_naturalness_point(k=0.10)
    verdicts = {r["verdict"] for r in rows}

    if "FALSIFIED" in verdicts:
        overall = "FALSIFIED"
    elif "TENSION" in verdicts:
        overall = "TENSION"
    else:
        overall = "PASS"

    return {
        "report_id": "A3_HIGGS_NATURALNESS_EXTENDED",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "rows": rows,
        "canonical_k_point": canonical,
        "overall_verdict": overall,
        "closure_blocker": "full_uv_completion_beyond_effective_kk_tower",
        "blocker_owner": "A3-naturalness-track",
        "stop_condition": "promote_when_uv_complete_multiloop_proof_is_derived",
    }
