# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Unified machine-readable dashboard for open residuals (SC2, SC4, A3, T3) and monitoring.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
This module is an observational/analytical dashboard that aggregates the four
open framework residuals plus external-measurement monitoring entries.  It does
NOT introduce new hardgate physics claims; the core pillar set (1–208) is frozen.

Residuals tracked:
    SC2  — A_s amplitude closure (CMB power spectrum normalisation)
    SC4  — 10D flux-landscape wrapping count (architecture limit)
    A3   — Higgs mass naturalness (partial closure via KK fixed-point)
    T3   — ADM lapse / BSSN time parameterisation (partially closed)

External monitoring:
    G3   — DESI dark-energy equation-of-state tension
    JUNO — atmospheric Δm²₃₁ prediction vs PDG + JUNO/HyperK risk
"""
from __future__ import annotations

import math

from src.core.as_transfer_normalization_audit import as_transfer_chain_audit
from src.core.flux_landscape_extended_scan import sc4_closure_summary
from src.core.higgs_naturalness_5d_fixedpoint import kk_higgs_naturalness
from src.core.higgs_naturalness_extended import higgs_naturalness_extended_report

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "N_W",
    "K_CS",
    "C_S",
    "residual_sc2_status",
    "residual_sc4_status",
    "residual_a3_status",
    "residual_t3_status",
    "monitoring_g3_desi_status",
    "monitoring_juno_status",
    "separation_guard",
    "full_dashboard",
    "closure_priority_ranking",
    "dashboard_report",
    "v11_5_residual_tightening_overlay",
]

# ---------------------------------------------------------------------------
# Adjacency / separation guard
# ---------------------------------------------------------------------------

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"

# ---------------------------------------------------------------------------
# Core framework constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0

# ---------------------------------------------------------------------------
# SC2 constants: A_s amplitude closure
# ---------------------------------------------------------------------------

_SC2_ALPHA_GW_INTERVAL: tuple[float, float] = (4.2e-10, 4.8e-10)
_SC2_RS1_ESTIMATE: float = 4.33e-65  # naive RS1 estimate without 10D embedding
_SC2_10D_BRIDGE_VALUE: float = 4.49e-10  # 10D bridge result (in-band)
_SC2_CLOSURE_BLOCKER: str = "exact_alpha_gw_point_value_requires_c_UV_from_10D_string_embedding"

# ---------------------------------------------------------------------------
# SC4 constants: 10D flux landscape
# ---------------------------------------------------------------------------

_SC4_N_FLUX_CURRENT: int = 37
_SC4_N_FLUX_REQUIRED: int = 61
_SC4_GAP_FRACTION: float = (_SC4_N_FLUX_REQUIRED - _SC4_N_FLUX_CURRENT) / _SC4_N_FLUX_CURRENT

# ---------------------------------------------------------------------------
# T3 constants: ADM lapse / BSSN
# ---------------------------------------------------------------------------

_T3_LAPSE_DEVIATION_PERCENT: float = 0.6  # slow-roll lapse deviation N=φ from N=1
_T3_LAPSE_IDENTIFICATION: str = "N=phi (radion is lapse in KK ansatz)"

# ---------------------------------------------------------------------------
# G3 constants: DESI tension
# ---------------------------------------------------------------------------

_G3_DESI_TENSION_SIGMA: float = 2.75
_G3_FALSIFICATION_SIGMA: float = 3.0

# ---------------------------------------------------------------------------
# JUNO / HyperK constants
# ---------------------------------------------------------------------------

_JUNO_DM31_UM: float = 2.400e-3  # UM prediction (eV²)
_JUNO_DM31_PDG: float = 2.453e-3  # PDG central value (eV²)
_JUNO_PRECISION_TARGET: float = 0.005  # 0.5% JUNO/HyperK precision
# σ at 0.5% precision on the UM prediction
_JUNO_SIGMA_AT_TARGET: float = _JUNO_PRECISION_TARGET * _JUNO_DM31_UM
_JUNO_TENSION_IF_CONFIRMED: float = (
    (_JUNO_DM31_PDG - _JUNO_DM31_UM) / _JUNO_SIGMA_AT_TARGET
)  # ≈ 4.4σ
_JUNO_FRACTIONAL_DEVIATION: float = (
    (_JUNO_DM31_PDG - _JUNO_DM31_UM) / _JUNO_DM31_PDG
)  # ≈ 2.16%


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def separation_guard() -> bool:
    """Non-hardgate separation guard.

    Returns True unconditionally, asserting that this module is an adjacent-track
    analytical dashboard and does NOT constitute a hardgate physics claim.
    """
    return True


def residual_sc2_status() -> dict[str, object]:
    """Return the current status of residual SC2 (A_s amplitude closure).

    The 10D bridge value 4.49 × 10⁻¹⁰ is in-band with the admissible interval
    [4.2 × 10⁻¹⁰, 4.8 × 10⁻¹⁰].  The exact α_GW point value is blocked
    pending a full 10D string embedding to fix c_UV.
    """
    alpha_lo, alpha_hi = _SC2_ALPHA_GW_INTERVAL
    in_band = alpha_lo <= _SC2_10D_BRIDGE_VALUE <= alpha_hi
    audit = as_transfer_chain_audit()
    fully_closed = audit["chain_verdict"] == "PASS"

    return {
        "residual_id": "SC2",
        "name": "A_s amplitude closure",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "alpha_gw_interval": _SC2_ALPHA_GW_INTERVAL,
        "alpha_gw_interval_low": alpha_lo,
        "alpha_gw_interval_high": alpha_hi,
        "rs1_estimate": _SC2_RS1_ESTIMATE,
        "value_10d_bridge": _SC2_10D_BRIDGE_VALUE,
        "in_band": in_band,
        "closure_blocker": _SC2_CLOSURE_BLOCKER,
        "status": "CLOSED_FULL_POINT_DERIVATION" if fully_closed else "CLOSED_WITH_10D_HARDGATE",
        "framework_level_status": "CLOSED_FULL_POINT_DERIVATION" if fully_closed else "CLOSED_WITH_10D_HARDGATE",
        "full_chain_verdict": audit["chain_verdict"],
        "full_chain_closed": fully_closed,
        "residual_tracked": True,
        "note": (
            "10D bridge gives 4.49e-10 (in-band with Planck A_s).  "
            "Exact point value requires c_UV from 10D string embedding."
        ),
    }


def residual_sc4_status() -> dict[str, object]:
    """Return the current status of residual SC4 (10D flux landscape).

    The current flux wrapping count N_flux = 37 is below the minimum required
    N_flux ≥ 61 for adequate BP landscape coverage.  Gap ≈ 65%.
    """
    gap_fraction = _SC4_GAP_FRACTION
    gap_percent = gap_fraction * 100.0
    summary = sc4_closure_summary()
    closed = summary["global_verdict"] == "PASS"

    return {
        "residual_id": "SC4",
        "name": "10D flux landscape wrapping count",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "n_flux_current": _SC4_N_FLUX_CURRENT,
        "n_flux_required": _SC4_N_FLUX_REQUIRED,
        "gap_fraction": gap_fraction,
        "gap_percent": gap_percent,
        "status": "CLOSED_WITH_EFFECTIVE_FLUX_CHANNELS" if closed else "ARCHITECTURE_LIMIT",
        "effective_flux_scan_status": summary["status"],
        "first_pass_n_flux": summary["first_pass_n_flux"],
        "first_pass_effective_n_flux": summary["first_pass_effective_n_flux"],
        "architecture_limit_type": "10D_EFT_SYSTEMATIC",
        "closure_path": "Extend to full 10D CY₃ flux compactification with ≥61 wrappings.",
        "note": (
            f"Need {_SC4_N_FLUX_REQUIRED - _SC4_N_FLUX_CURRENT} more flux wrappings "
            f"({gap_percent:.0f}% increase from current {_SC4_N_FLUX_CURRENT})."
        ),
    }


def residual_a3_status(
    k: float = 0.1,
    R: float = 37.0 / math.pi / 0.1,
    N_modes: int = 10,
) -> dict[str, object]:
    """Return the current status of residual A3 (Higgs naturalness).

    Calls `kk_higgs_naturalness()` for a live Δ estimate.  Partial closure
    is achieved when Δ < 100 (NATURALNESS_THRESHOLD).

    Parameters
    ----------
    k:
        AdS curvature scale (dimensionless, units of M_PL).
    R:
        Compactification radius.
    N_modes:
        KK modes included in loop sum.
    """
    result = kk_higgs_naturalness(k=k, R=R, N_modes=N_modes)
    extended = higgs_naturalness_extended_report()
    delta = result["tuning_Delta"]
    partial_closure = result["naturalness_partial_closure"]
    status = result["status"]

    return {
        "residual_id": "A3",
        "name": "Higgs mass naturalness (5D KK fixed-point)",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "k": k,
        "R": R,
        "N_modes": N_modes,
        "M_KK_GeV": result["M_KK_GeV"],
        "tuning_Delta": delta,
        "naturalness_threshold": 100.0,
        "partial_closure": partial_closure,
        "status": extended["overall_status"] if isinstance(extended["overall_status"], str) else status,
        "extended_overall_status": extended["overall_status"],
        "convergence_ratio": result["convergence_ratio"],
        "note": (
            f"Δ = {delta:.3g}; {'partial closure achieved' if partial_closure else 'architecture limit — Δ ≥ 100'}. "
            "Full closure requires UV completion in 10D string embedding."
        ),
    }


def residual_t3_status() -> dict[str, object]:
    """Return the current status of residual T3 (ADM lapse / BSSN).

    Kinematic closure: lapse N = φ in KK ansatz; deviation from N = 1 is ~0.6%
    in slow roll.  Full BSSN dynamical evolution remains open.
    """
    from src.core.adm_bssn_closure import t3_closure_assessment

    assessment = t3_closure_assessment()
    final_metric = float(assessment["hamiltonian_proxy"]) + float(assessment["momentum_proxy"])
    return {
        "residual_id": "T3",
        "name": "ADM time parameterisation / BSSN",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "lapse_identification": _T3_LAPSE_IDENTIFICATION,
        "lapse_deviation_percent": _T3_LAPSE_DEVIATION_PERCENT,
        "kinematic_closure": True,
        "bssn_full_evolution": assessment["reduced_sector_complete"],
        "constraint_metric": final_metric,
        "dynamical_verdict": assessment["dynamical_verdict"],
        "status": assessment["status"],
        "closure_blocker": assessment["closure_blocker"],
        "note": (
            "Reduced-sector BSSN execution now runs explicitly. "
            f"Constraint verdict = {assessment['dynamical_verdict']}; "
            f"final proxy metric = {final_metric:.3e}."
        ),
    }


def monitoring_g3_desi_status() -> dict[str, object]:
    """Return the current DESI dark-energy equation-of-state tension status (G3).

    Current tension: 2.75σ (HIGH_TENSION).  Falsification threshold: ≥ 3.0σ.
    UM prediction: w_a = 0 (KK compactification implies static dark energy EoS).
    """
    is_falsified = _G3_DESI_TENSION_SIGMA >= _G3_FALSIFICATION_SIGMA

    return {
        "monitor_id": "G3",
        "name": "DESI dark-energy EoS tension",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "um_prediction_wa": 0.0,
        "desi_tension_sigma": _G3_DESI_TENSION_SIGMA,
        "falsification_threshold_sigma": _G3_FALSIFICATION_SIGMA,
        "is_falsified": is_falsified,
        "status": "HIGH_TENSION" if not is_falsified else "FALSIFIED",
        "note": (
            f"DESI Year 1+2 reports w_a ≠ 0 at {_G3_DESI_TENSION_SIGMA}σ.  "
            f"UM predicts w_a = 0.  Falsification at ≥ {_G3_FALSIFICATION_SIGMA}σ."
        ),
    }


def monitoring_juno_status() -> dict[str, object]:
    """Return the JUNO/HyperK Δm²₃₁ monitoring status.

    UM prediction: Δm²₃₁ = 2.400 × 10⁻³ eV².
    PDG central value: 2.453 × 10⁻³ eV² (2.16% above UM).

    If JUNO/HyperK achieves 0.5% precision, the tension reaches ≈ 4.4σ → FALSIFIED.
    """
    tension_sigma = _JUNO_TENSION_IF_CONFIRMED
    is_falsified_if_confirmed = tension_sigma >= 3.0
    fractional_deviation_percent = _JUNO_FRACTIONAL_DEVIATION * 100.0

    return {
        "monitor_id": "JUNO",
        "name": "JUNO/HyperK Δm²₃₁ neutrino mass splitting",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "um_prediction_dm31_eV2": _JUNO_DM31_UM,
        "pdg_central_dm31_eV2": _JUNO_DM31_PDG,
        "fractional_deviation_percent": fractional_deviation_percent,
        "juno_precision_target": _JUNO_PRECISION_TARGET,
        "juno_sigma_at_target": _JUNO_SIGMA_AT_TARGET,
        "tension_sigma_if_confirmed": tension_sigma,
        "is_falsified_if_confirmed": is_falsified_if_confirmed,
        "status": "RISK_FALSIFICATION_AT_0.5pct_PRECISION",
        "note": (
            f"UM predicts {_JUNO_DM31_UM:.3e} eV²; PDG gives {_JUNO_DM31_PDG:.3e} eV² "
            f"({fractional_deviation_percent:.2f}% above UM). "
            f"At 0.5% JUNO precision → {tension_sigma:.2f}σ tension → FALSIFIED."
        ),
    }


def full_dashboard() -> dict[str, object]:
    """Return all residuals and monitoring entries in a single machine-readable dict."""
    return {
        "dashboard_id": "PILLAR_255_OPEN_GAP_RESIDUAL_DASHBOARD",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "framework_constants": {
            "N_W": N_W,
            "K_CS": K_CS,
            "C_S": C_S,
        },
        "residuals": {
            "SC2": residual_sc2_status(),
            "SC4": residual_sc4_status(),
            "A3": residual_a3_status(),
            "T3": residual_t3_status(),
        },
        "monitoring": {
            "G3": monitoring_g3_desi_status(),
            "JUNO": monitoring_juno_status(),
        },
        "separation_guard_passed": separation_guard(),
    }


def closure_priority_ranking() -> list[str]:
    """Return residual IDs ordered from most-tractable to least-tractable closure.

    Ranking rationale:
    1. T3 — kinematic closure already done; only BSSN dynamics remain (most tractable).
    2. A3 — partial closure achieved when Δ < 100; standard 10D embedding extends it.
    3. SC2 — in-band with 10D bridge; needs c_UV from string embedding to fix point value.
    4. SC4 — architecture limit; requires extending to full CY₃ with ≥61 flux wrappings.
    """
    return ["T3", "A3", "SC2", "SC4"]


def dashboard_report() -> str:
    """Return a human-readable summary of all open residuals and monitoring."""
    d = full_dashboard()
    lines: list[str] = [
        "=" * 72,
        "PILLAR 255 — OPEN GAP RESIDUAL DASHBOARD",
        f"[{ADJACENCY_TRACK_LABEL}]",
        "=" * 72,
        "",
        "RESIDUALS",
        "-" * 40,
    ]

    for rid, res in d["residuals"].items():
        lines.append(f"  {rid}: {res['name']}")
        lines.append(f"      status = {res['status']}")
        lines.append(f"      {res['note']}")
        lines.append("")

    lines += [
        "EXTERNAL MONITORING",
        "-" * 40,
    ]
    for mid, mon in d["monitoring"].items():
        lines.append(f"  {mid}: {mon['name']}")
        lines.append(f"      status = {mon['status']}")
        lines.append(f"      {mon['note']}")
        lines.append("")

    lines += [
        "CLOSURE PRIORITY RANKING (most tractable first)",
        "-" * 40,
        "  " + " → ".join(closure_priority_ranking()),
        "",
        "=" * 72,
    ]
    return "\n".join(lines)


def v11_5_residual_tightening_overlay() -> dict[str, object]:
    """Non-invasive overlay aggregating the v11.5 Residual Tightening Wave.

    🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

    Aggregates the deltas produced by Pillars 274–281 *without* modifying
    any existing residual or monitoring field.  Read-only consumers (CI
    dashboards, paper appendices, audit scripts) can call this to get the
    tightened per-residual numbers for v11.5 with their named modules.
    """
    from src.core.pillar274_juno_dm31_tightening import juno_tightening_report
    from src.core.pillar275_higgs_naturalness_schwinger_convergence import (
        schwinger_convergence_report,
    )
    from src.core.pillar276_t3_momentum_constraint_sector import (
        two_sector_closure_assessment,
    )
    from src.core.pillar277_cmb_peak_three_term_decomposition import (
        peak_suppression_report,
    )
    from src.core.pillar278_sc4_effective_flux_multiplicity_theorem import (
        multiplicity_theorem_report,
    )
    from src.core.pillar279_nw_parity_handedness_obstruction import (
        nw_obstruction_report,
    )
    from src.core.pillar280_sc2_c_uv_independent_interval_narrowing import (
        interval_narrowing_report,
    )
    from src.core.pillar281_desi_dr3_routing_drill import desi_dr3_drill_report

    return {
        "wave_id": "v11.5_RESIDUAL_TIGHTENING_WAVE",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "tightening_modules": {
            "JUNO": juno_tightening_report(),
            "A3": schwinger_convergence_report(),
            "T3": two_sector_closure_assessment(),
            "CMB_PEAK": peak_suppression_report(),
            "SC4": multiplicity_theorem_report(),
            "NW_OBSTRUCTION": nw_obstruction_report(),
            "SC2": interval_narrowing_report(),
            "DESI_DR3_DRILL": desi_dr3_drill_report(),
        },
        "honest_note": (
            "v11.5 overlay only — original residual/monitoring fields are "
            "unchanged. No hardgate label promoted; no falsifier window "
            "weakened. Each tightening module is non-hardgate adjacent."
        ),
    }
