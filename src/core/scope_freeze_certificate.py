# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
scope_freeze_certificate.py — Machine-readable terminal state record for the
entire Unitary Manifold MAS + post-MAS programme.

This module encodes the frozen scope after completion of:
  1. MAS Waves W0–W14 (all parameters gated; programme closed 2026-05-08)
  2. Post-MAS robustness tracks T1–T3 (PASS; T4 optional, not activated)
  3. Post-MAS extension tracks ET-1–ET-6 (all delivered 2026-05-08)

Status: SCOPE_FROZEN
  - MAS: COMPLETE (mas_reopen_allowed: false)
  - Post-MAS robustness: FROZEN (T1–T3 all PASS)
  - Extension tracks: FROZEN (ET-1–ET-4 all DELIVERED)
  - Prediction registry: FROZEN
  - Scope rule: no further MAS waves; any new work is an independent research programme

Usage::

    from src.core.scope_freeze_certificate import (
        SCOPE_STATE,
        get_parameter_status,
        get_dbp_rung_status,
        scope_freeze_summary,
    )
"""
from __future__ import annotations

from typing import Dict

__all__ = [
    # Constants
    "FREEZE_DATE",
    "SCOPE_VERSION",
    "MAS_STATUS",
    "TOE_SCORE",
    "TOE_SCORE_MAX",
    # Frozen state dicts
    "PARAMETER_TERMINAL_STATUS",
    "DBP_LADDER_STATUS",
    "ROBUSTNESS_TRACK_STATUS",
    "EXTENSION_TRACK_STATUS",
    "WS_EXECUTION_PROGRAMME_STATUS",
    "ARCHITECTURE_LIMITS",
    # Functions
    "get_parameter_status",
    "get_dbp_rung_status",
    "list_open_architecture_limits",
    "scope_freeze_summary",
    "is_scope_frozen",
]

# ---------------------------------------------------------------------------
# Programme metadata
# ---------------------------------------------------------------------------
FREEZE_DATE: str = "2026-05-08"
SCOPE_VERSION: str = "v10.14"
MAS_STATUS: str = "COMPLETE"
MAS_REOPEN_ALLOWED: bool = False
TOE_SCORE: float = 14.2         # Raw score over 28 parameters
TOE_SCORE_MAX: float = 28.0     # Maximum possible
TOE_SCORE_PCT: float = TOE_SCORE / TOE_SCORE_MAX  # ≈ 0.507

# ---------------------------------------------------------------------------
# Parameter terminal status table (frozen after W14 + ET-1..ET-6)
# ---------------------------------------------------------------------------
PARAMETER_TERMINAL_STATUS: Dict[str, Dict] = {
    "P3": {
        "name": "α_s(M_Z) strong coupling",
        "terminal_status": "ARCHITECTURE_LIMIT_CERTIFIED(10D)",
        "terminal_wave": "W14",
        "extension_track": "ET-4",
        "residual": "~20% after CY₃ KK thresholds (10D estimate)",
        "artifact": "src/tend/cy3_kk_thresholds_alpha_s.py",
        "score": 0.1,
    },
    "P5": {
        "name": "Higgs mass m_H = 125.25 GeV",
        "terminal_status": "ARCHITECTURE_LIMIT_CERTIFIED(6D+)",
        "terminal_wave": "W14",
        "extension_track": "ET-1",
        "residual": "θ_HR established; exact value requires 6D+ geometry",
        "artifact": "src/sixd/higgs_radion_mixing_6d.py",
        "score": 0.1,
    },
    "P6": {
        "name": "Top Yukawa y_t",
        "terminal_status": "CONSTRAINED",
        "terminal_wave": "W14",
        "residual": "~15% from 6D c_L spectrum",
        "artifact": "src/sixd/yukawa_scale_6d.py",
        "score": 0.5,
    },
    "P7": {
        "name": "Bottom Yukawa y_b",
        "terminal_status": "CONSTRAINED",
        "terminal_wave": "W14",
        "residual": "~20% from 6D c_L spectrum",
        "artifact": "src/sixd/yukawa_scale_6d.py",
        "score": 0.5,
    },
    "P8": {
        "name": "Tau Yukawa y_τ",
        "terminal_status": "CONSTRAINED",
        "terminal_wave": "W14",
        "residual": "~20% from 6D c_L spectrum",
        "artifact": "src/sixd/yukawa_scale_6d.py",
        "score": 0.5,
    },
    "P14": {
        "name": "CKM ρ̄ (quark CP violation)",
        "terminal_status": "BEST_EVIDENCE_CONSTRAINED",
        "terminal_wave": "W14",
        "extension_track": "ET-2",
        "residual": "~1.2% nominal; robustness gate: Rung-2 inherited limit",
        "artifact": "src/core/mas_final_closure.py",
        "score": 0.5,
    },
    "P15": {
        "name": "δ_CP leptonic CP-violation phase",
        "terminal_status": "BEST_EVIDENCE_CONSTRAINED",
        "terminal_wave": "ET-2",
        "extension_track": "ET-2",
        "residual": "~1.3% (9D refined from 12.7% baseline)",
        "artifact": "src/nined/cp_phase_9d_refinement.py",
        "score": 0.5,
    },
    "P16": {
        "name": "Charm Yukawa y_c",
        "terminal_status": "CONSTRAINED",
        "terminal_wave": "W14",
        "residual": "geometric hierarchy from c_L spectrum",
        "artifact": "src/sixd/yukawa_scale_6d.py",
        "score": 0.5,
    },
    "P19": {
        "name": "c_{Rν} right-handed neutrino bulk mass spectrum",
        "terminal_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "terminal_wave": "W14",
        "extension_track": "ET-3",
        "residual": "Δm²₃₁ ~7-8% (NLO improved from ~10.5%)",
        "artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "score": 0.3,
    },
    "P20": {
        "name": "Δm²₂₁ solar neutrino mass splitting",
        "terminal_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "terminal_wave": "W14",
        "extension_track": "ET-3",
        "residual": "UNCONSTRAINED_AT_NLO (6D+ needed for simultaneous prediction)",
        "artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "score": 0.3,
    },
    "P21": {
        "name": "Δm²₃₁ atmospheric neutrino mass splitting",
        "terminal_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "terminal_wave": "W14",
        "extension_track": "ET-3",
        "residual": "~7-8% (NLO improved)",
        "artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "score": 0.3,
    },
    "P26": {
        "name": "θ_QCD strong-CP angle",
        "terminal_status": "ARCHITECTURE_LIMIT_CERTIFIED(7D/8D)",
        "terminal_wave": "W14",
        "residual": "PDG bound < 10⁻¹⁰; torsion mechanism 7D+",
        "artifact": "src/core/open_parameters_p26_p27_certification.py",
        "score": 0.1,
    },
    "P27": {
        "name": "Λ_CC cosmological constant",
        "terminal_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "terminal_wave": "W14",
        "residual": "Flux landscape estimate; Pillar 206",
        "artifact": "src/core/open_parameters_p26_p27_certification.py",
        "score": 0.3,
    },
}

# ---------------------------------------------------------------------------
# DBP ladder frozen state
# ---------------------------------------------------------------------------
DBP_LADDER_STATUS: Dict[str, Dict] = {
    "rung1": {
        "transition": "5D → 6D",
        "anchor": "N_gen = 3",
        "status": "SOLID",
        "module": "src/sixd/generation_count_6d.py",
    },
    "rung2": {
        "transition": "6D → 7D",
        "anchor": "δ_CP",
        "status": "RUNG_SOLID",
        "residual_pct": 12.7,
        "tolerance_pct": 40.0,
        "module": "src/sevend/discrete_torsion_cp.py",
        "kill_switch_pass": True,
    },
    "rung3": {
        "transition": "7D → 8D",
        "anchor": "SU(3)×SU(2)×U(1) gauge group",
        "status": "RUNG_SOLID",
        "module": "src/eightd/wilson_line_gauge.py",
        "kill_switch_pass": True,
    },
    "rung4": {
        "transition": "8D → 9D",
        "anchor": "anomaly cancellation",
        "status": "RUNG_SOLID",
        "module": "src/nined/anomaly_cancellation_gs.py",
        "kill_switch_pass": True,
        "hard_gate_pass": True,
    },
    "rung5": {
        "transition": "9D → 10D",
        "anchor": "Λ_CC (cosmological constant)",
        "status": "ARCHITECTURE_CERTIFIED",
        "module": "src/tend/flux_landscape.py",
        "kill_switch_pass": True,
        "hard_gate_pass": True,
        "architecture_limit": True,
    },
    "rung6": {
        "transition": "10D → 11D",
        "anchor": "M-theory unification",
        "status": "RUNG_SOLID",
        "module": "src/eleventd/horava_witten_hard_gate.py",
        "kill_switch_pass": True,
        "hard_gate_pass": True,
    },
}

# ---------------------------------------------------------------------------
# Post-MAS robustness track status (T1–T3)
# ---------------------------------------------------------------------------
ROBUSTNESS_TRACK_STATUS: Dict[str, Dict] = {
    "T1": {
        "title": "Formal proof hardening",
        "status": "PASS",
        "artifact": "src/core/formal_proof_hardening.py",
    },
    "T2": {
        "title": "Variance-based global sensitivity analysis",
        "status": "PASS",
        "artifact": "src/core/global_sensitivity_analysis.py",
    },
    "T3": {
        "title": "Neural-symbolic drift check",
        "status": "PASS",
        "artifact": "src/core/neural_symbolic_drift_check.py",
    },
    "T4": {
        "title": "Julia structural simplification cross-check",
        "status": "OPTIONAL_NOT_ACTIVATED",
        "activation_rule": "only_if_disputed_or_high_cost_symbolic_blocks",
    },
}

# ---------------------------------------------------------------------------
# Extension track status (ET-1–ET-6)
# ---------------------------------------------------------------------------
EXTENSION_TRACK_STATUS: Dict[str, Dict] = {
    "ET-1": {
        "title": "6D+ Higgs-radion mixing θ_HR",
        "parameter": "P5",
        "artifact": "src/sixd/higgs_radion_mixing_6d.py",
        "status": "DELIVERED",
        "epistemic_outcome": "ARCHITECTURE_LIMIT_CERTIFIED(6D+)",
    },
    "ET-2": {
        "title": "9D+ CP phase refinement for δ_CP and P14 robustness",
        "parameter": "P14, P15",
        "artifact": "src/nined/cp_phase_9d_refinement.py",
        "status": "DELIVERED",
        "epistemic_outcome": "BEST_EVIDENCE_CONSTRAINED(9D)",
    },
    "ET-3": {
        "title": "NLO T²/Z₃ fixed-point overlap integrals for Δm²₃₁",
        "parameter": "P19, P20, P21",
        "artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "status": "DELIVERED",
        "epistemic_outcome": "GEOMETRIC_ESTIMATE_CERTIFIED (NLO improved)",
    },
    "ET-4": {
        "title": "10D CY₃ KK threshold corrections to α_s(M_Z)",
        "parameter": "P3",
        "artifact": "src/tend/cy3_kk_thresholds_alpha_s.py",
        "status": "DELIVERED",
        "epistemic_outcome": "ARCHITECTURE_LIMIT_CERTIFIED(10D)",
    },
    "ET-5": {
        "title": "Prediction registry and ToE score audit",
        "parameter": "all",
        "artifact": "src/core/prediction_registry.py",
        "status": "DELIVERED",
        "epistemic_outcome": "ToE Score ~51%; primary falsifier intact",
    },
    "ET-6": {
        "title": "Scope freeze certificate and dimensional extension roadmap",
        "parameter": "all",
        "artifact": "src/core/scope_freeze_certificate.py",
        "status": "DELIVERED",
        "epistemic_outcome": "SCOPE_FROZEN",
    },
}

# ---------------------------------------------------------------------------
# Independent WS-I..WS-IV execution programme status (post freeze)
# ---------------------------------------------------------------------------
WS_EXECUTION_PROGRAMME_STATUS: Dict[str, Dict] = {
    "WS-II": {
        "status": "PASS_FREEZE",
        "post_freeze_action": "frozen",
        "recycle_into_mas": False,
    },
    "WS-III": {
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
    "WS-I": {
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
    "WS-IV": {
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
}

# ---------------------------------------------------------------------------
# Architecture limits (frozen record)
# ---------------------------------------------------------------------------
ARCHITECTURE_LIMITS: Dict[str, Dict] = {
    "A-P3": {
        "parameter": "P3 (α_s)",
        "dimension_needed": "10D CY₃",
        "description": "Full Calabi-Yau compactification with moduli/flux for direct-chain closure",
        "current_best": "~20% residual with CY₃ KK thresholds (quintic, h11=1, h21=101)",
    },
    "A-P5": {
        "parameter": "P5 (m_H / θ_HR)",
        "dimension_needed": "6D+ brane geometry",
        "description": "Brane-localized kinetic mixing derivation from full 6D action",
        "current_best": "θ_HR non-zero, perturbative; CW mechanism active",
    },
    "A-P14": {
        "parameter": "P14 (ρ̄_CKM robustness)",
        "dimension_needed": "9D+",
        "description": "δ_CP independent of Rung-2 12.7% uncertainty",
        "current_best": "9D correction gives ~1.3% nominal; propagated uncertainty <5%",
    },
    "A-P19-P21": {
        "parameter": "P19/P20/P21 (neutrino mass splittings)",
        "dimension_needed": "6D+ fixed-point overlaps",
        "description": "Simultaneous prediction of Δm²₂₁ and Δm²₃₁ from first principles",
        "current_best": "NLO: Δm²₃₁ ~7-8% residual; Δm²₂₁ UNCONSTRAINED",
    },
    "A-P26": {
        "parameter": "P26 (θ_QCD strong-CP)",
        "dimension_needed": "7D/8D discrete torsion",
        "description": "Geometric derivation of θ_QCD suppression mechanism",
        "current_best": "Axion mechanism identified; exact value architecture-limited",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_parameter_status(pid: str) -> Dict:
    """Return the frozen terminal status for parameter ID *pid*.

    Parameters
    ----------
    pid : str
        Parameter ID (e.g. 'P3', 'P5', 'P14').

    Returns
    -------
    dict
        Frozen status entry.

    Raises
    ------
    KeyError
        If *pid* is not found in the terminal status table.
    """
    if pid not in PARAMETER_TERMINAL_STATUS:
        raise KeyError(
            f"Unknown parameter ID: {pid!r}. "
            f"Available: {sorted(PARAMETER_TERMINAL_STATUS)}"
        )
    return dict(PARAMETER_TERMINAL_STATUS[pid])


def get_dbp_rung_status(rung: str) -> Dict:
    """Return the frozen DBP ladder status for *rung*.

    Parameters
    ----------
    rung : str
        Rung identifier: 'rung1' through 'rung6'.

    Returns
    -------
    dict
        Frozen rung status entry.

    Raises
    ------
    KeyError
        If *rung* is not found.
    """
    if rung not in DBP_LADDER_STATUS:
        raise KeyError(
            f"Unknown rung: {rung!r}. "
            f"Available: {sorted(DBP_LADDER_STATUS)}"
        )
    return dict(DBP_LADDER_STATUS[rung])


def list_open_architecture_limits() -> list:
    """Return list of architecture limit IDs (always frozen, never reopens MAS).

    Returns
    -------
    list[str]
        Sorted architecture limit keys.
    """
    return sorted(ARCHITECTURE_LIMITS.keys())


def is_scope_frozen() -> bool:
    """Return True — scope is always frozen after programme completion.

    Returns
    -------
    bool
        Always True: the programme is complete and scope is frozen.
    """
    return True


def scope_freeze_summary() -> Dict:
    """Return a complete summary of the frozen programme state.

    Returns
    -------
    dict
        Full summary: version, date, MAS status, ToE score, counts by status,
        DBP ladder state, robustness track state, extension track state,
        and architecture limits.
    """
    # Count parameters by terminal status
    status_counts: Dict[str, int] = {}
    for entry in PARAMETER_TERMINAL_STATUS.values():
        st = entry["terminal_status"]
        status_counts[st] = status_counts.get(st, 0) + 1

    # Check all extension tracks delivered
    extension_complete = all(
        v["status"] == "DELIVERED"
        for k, v in EXTENSION_TRACK_STATUS.items()
        if k in ("ET-1", "ET-2", "ET-3", "ET-4")
    )
    # Check all required robustness tracks passed
    robustness_complete = all(
        v["status"] == "PASS"
        for k, v in ROBUSTNESS_TRACK_STATUS.items()
        if k in ("T1", "T2", "T3")
    )
    # All rungs SOLID or CERTIFIED
    dbp_all_solid = all(
        "SOLID" in v["status"] or "CERTIFIED" in v["status"]
        for v in DBP_LADDER_STATUS.values()
    )
    ws_programme_pass_count = sum(
        1 for v in WS_EXECUTION_PROGRAMME_STATUS.values()
        if v["status"] == "PASS_FREEZE"
    )
    ws_programme_targeted_count = sum(
        1 for v in WS_EXECUTION_PROGRAMME_STATUS.values()
        if v["status"] == "TARGETED_FOLLOW_UP_FREEZE"
    )

    return {
        "scope_version": SCOPE_VERSION,
        "freeze_date": FREEZE_DATE,
        "mas_status": MAS_STATUS,
        "mas_reopen_allowed": MAS_REOPEN_ALLOWED,
        "toe_score_raw": TOE_SCORE,
        "toe_score_max": TOE_SCORE_MAX,
        "toe_score_pct": TOE_SCORE_PCT,
        "parameter_count_tracked": len(PARAMETER_TERMINAL_STATUS),
        "parameter_status_counts": status_counts,
        "dbp_ladder_rungs": len(DBP_LADDER_STATUS),
        "dbp_all_solid_or_certified": dbp_all_solid,
        "robustness_tracks_complete": robustness_complete,
        "extension_tracks_complete": extension_complete,
        "ws_execution_programme_count": len(WS_EXECUTION_PROGRAMME_STATUS),
        "ws_execution_pass_freeze_count": ws_programme_pass_count,
        "ws_execution_targeted_follow_up_freeze_count": ws_programme_targeted_count,
        "ws_execution_no_mas_recycle": all(
            not v["recycle_into_mas"] for v in WS_EXECUTION_PROGRAMME_STATUS.values()
        ),
        "architecture_limits_count": len(ARCHITECTURE_LIMITS),
        "scope_frozen": is_scope_frozen(),
        "primary_falsifier": (
            "LiteBIRD β birefringence: β ∈ {0.273°, 0.331°}, "
            "admissible window [0.22°, 0.38°], expected ~2034"
        ),
        "terminal_verdict": (
            "MAS programme complete. Post-MAS robustness tracks T1–T3 all PASS. "
            "Extension tracks ET-1–ET-4 all delivered. Scope is frozen. "
            "No further MAS waves required."
        ),
    }
