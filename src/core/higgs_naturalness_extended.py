# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""A3 Higgs naturalness multiloop + UV-completion extension with explicit closure routing.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

import math

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.higgs_naturalness_5d_fixedpoint import M_PL_GEV, kk_higgs_naturalness

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "K_SWEEP",
    "two_loop_qcd_factor",
    "three_loop_mixed_factor",
    "uv_counterterm_factor",
    "higgs_naturalness_point",
    "higgs_naturalness_sweep",
    "higgs_naturalness_extended_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
K_SWEEP: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20)
# Renormalized Δ routing thresholds for adjacent-track A3 closure packets.
_A3_PASS_DELTA_THRESHOLD: float = 1.0
_A3_TENSION_DELTA_THRESHOLD: float = 3.0
# Maximum relative spread across canonical scheme points for closure stability.
_SCHEME_SPREAD_MAX: float = 0.2


def two_loop_qcd_factor(alpha_s_mz: float = 0.113) -> float:
    """Deterministic 2-loop QCD factor."""
    return 1.0 + 0.30 * alpha_s_mz


def three_loop_mixed_factor(alpha_s_mz: float = 0.113, y_t: float = 0.935) -> float:
    """Deterministic 3-loop mixed QCD-Yukawa factor."""
    return 1.0 + 0.05 * alpha_s_mz * y_t


def uv_counterterm_factor(c_uv_total: float) -> float:
    """UV counterterm suppression factor inferred from the 10D closure coefficient.

    The benchmark c_UV is translated into an effective finite renormalized fraction
    using a stable logarithmic normalization.
    """
    if c_uv_total <= 0.0:
        raise ValueError("c_uv_total must be positive")
    return 1.0 / (1.0 + abs(math.log10(c_uv_total)))


def _verdict_from_delta(delta_total: float) -> str:
    if delta_total < _A3_PASS_DELTA_THRESHOLD:
        return "PASS"
    if delta_total < _A3_TENSION_DELTA_THRESHOLD:
        return "TENSION"
    return "FALSIFIED"


def _status_from_verdict(verdict: str) -> str:
    if verdict == "PASS":
        return "DERIVED_COMPLETE"
    if verdict == "TENSION":
        return "DERIVED_WITH_TENSION"
    return "ARCHITECTURE_LIMIT_FAILED"


def higgs_naturalness_point(k: float, n_modes: int = 10) -> dict[str, object]:
    """Evaluate one k-point in the UV-complete A3 naturalness lane."""
    r = 37.0 / math.pi / k
    base = kk_higgs_naturalness(k=k, R=r, N_modes=n_modes)
    uv_report = full_10d_uv_closure_report()

    factor_2 = two_loop_qcd_factor()
    factor_3 = three_loop_mixed_factor()
    uv_factor = uv_counterterm_factor(float(uv_report["step4_c_uv"]["c_uv_total"]))

    delta_multiloop = float(base["tuning_Delta"]) * factor_2 * factor_3
    delta_renormalized = delta_multiloop * uv_factor

    m_kk = float(base["M_KK_GeV"])
    is_uv_cutoff = (m_kk / M_PL_GEV) < 1e-12
    uv_closed = uv_report["step8_decision"]["status"] == "CLOSED"
    verdict = _verdict_from_delta(delta_renormalized)

    return {
        "k": k,
        "R": r,
        "N_modes": n_modes,
        "delta_base": float(base["tuning_Delta"]),
        "two_loop_factor": factor_2,
        "three_loop_factor": factor_3,
        "delta_multiloop": delta_multiloop,
        "uv_counterterm_factor": uv_factor,
        "delta_renormalized": delta_renormalized,
        "M_KK_GeV": m_kk,
        "kk_tower_acts_as_uv_cutoff": is_uv_cutoff,
        "uv_completion_closed": uv_closed,
        "verdict": verdict,
        "status": _status_from_verdict(verdict),
    }


def higgs_naturalness_sweep() -> list[dict[str, object]]:
    """Evaluate the canonical k sweep for the A3 lane."""
    return [higgs_naturalness_point(k=k) for k in K_SWEEP]


def higgs_naturalness_extended_report() -> dict[str, object]:
    """Return integrated A3 UV-complete extension report."""
    rows = higgs_naturalness_sweep()
    canonical = higgs_naturalness_point(k=0.10)
    uv_report = full_10d_uv_closure_report()

    verdicts = {r["verdict"] for r in rows}
    max_delta = max(float(r["delta_renormalized"]) for r in rows)
    min_delta = min(float(r["delta_renormalized"]) for r in rows)
    scheme_spread = (max_delta - min_delta) / max_delta if max_delta > 0 else 0.0

    uv_closed = uv_report["step8_decision"]["status"] == "CLOSED"
    kk_cutoff_all = all(bool(r["kk_tower_acts_as_uv_cutoff"]) for r in rows)

    if "FALSIFIED" in verdicts:
        overall_verdict = "FALSIFIED"
    elif "TENSION" in verdicts:
        overall_verdict = "TENSION"
    else:
        overall_verdict = "PASS"

    full_complete = (
        overall_verdict == "PASS"
        and uv_closed
        and kk_cutoff_all
        and scheme_spread < _SCHEME_SPREAD_MAX
    )

    return {
        "report_id": "A3_HIGGS_NATURALNESS_EXTENDED",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "rows": rows,
        "canonical_k_point": canonical,
        "overall_verdict": overall_verdict,
        "overall_status": "DERIVED_COMPLETE" if full_complete else "DERIVED_WITH_RESIDUAL",
        "uv_completion_status": uv_report["step8_decision"]["status"],
        "scheme_spread": scheme_spread,
        "kk_cutoff_all_points": kk_cutoff_all,
        "closure_blocker": (
            "none"
            if full_complete
            else "full_uv_complete_multiloop_scheme_stability_not_yet_uniform"
        ),
        "blocker_owner": "A3-naturalness-track",
        "stop_condition": "promote_when_multiloop_renormalized_delta_stays_subunit_and_uv_closed",
    }
