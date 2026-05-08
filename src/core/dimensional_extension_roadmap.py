# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
dimensional_extension_roadmap.py — Machine-readable roadmap for the four
post-MAS dimensional-extension research workstreams.

These workstreams address the certified architecture limits identified during
the MAS programme (Waves W0–W14) and further developed in Extension Tracks
ET-1 through ET-4. Each is an independent research programme — none reopens
MAS or creates new MAS waves.

Workstreams:
  WS-I   (6D+)  Close P5 via brane-localized θ_HR derivation
  WS-II  (9D+)  Close P14/P15 via full δ_CP independence from Rung-2
  WS-III (6D+)  Close P19/P20/P21 via simultaneous Δm²₂₁ and Δm²₃₁
  WS-IV  (10D)  Close P3 via complete CY₃ moduli + flux α_s calculation

Usage::

    from src.core.dimensional_extension_roadmap import (
        WORKSTREAM_CATALOGUE,
        get_workstream,
        list_workstreams,
        readiness_check,
        roadmap_summary,
    )
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    # Registry
    "WORKSTREAM_CATALOGUE",
    # Functions
    "get_workstream",
    "list_workstreams",
    "readiness_check",
    "roadmap_summary",
    "execution_freeze_status",
]

# ---------------------------------------------------------------------------
# Workstream Catalogue
# ---------------------------------------------------------------------------
WORKSTREAM_CATALOGUE: Dict[str, Dict] = {
    "WS-I": {
        "title": "6D+ Brane-Localized Higgs-Radion Mixing (P5 Closure)",
        "dimension_target": "6D+",
        "parameter_target": "P5",
        "current_status": "ARCHITECTURE_LIMIT_CERTIFIED(6D+)",
        "current_best_artifact": "src/sixd/higgs_radion_mixing_6d.py",
        "current_residual": "θ_HR established (non-zero, perturbative); exact value unknown",
        "goal": "Compute exact θ_HR from full 6D action with brane-localized kinetic mixing",
        "prerequisites": [
            "Full 6D action on warped background with torus-moduli backreaction",
            "Brane-localized kinetic term ξ H†H R_{6D} derivation from 6D geometry",
            "One-loop effective potential V_CW(φ) with 6D propagators on IR brane",
            "Moduli stabilization to fix R₆ and k/M₆",
        ],
        "key_calculation": (
            "Compute the 6D brane kinetic mixing amplitude M_mix = ξ_{6D} × v × f_radion "
            "where ξ_{6D} is derived from the 6D Dirac-Born-Infeld action on the brane "
            "rather than assumed equal to the 4D conformal value 1/6."
        ),
        "expected_outcome": (
            "Exact θ_HR from geometry → CONSTRAINED or GEOMETRIC_PREDICTION for P5. "
            "If θ_HR matches observed m_H = 125.25 GeV within 5%, P5 → GEOMETRIC_PREDICTION."
        ),
        "readiness_criteria": {
            "ET_1_baseline": True,
            "requires_6d_action": True,
            "requires_moduli_stabilization": True,
            "requires_brane_propagators": True,
        },
        "estimated_dimension_reach": "6D (R-S brane geometry + T²/Z₃ or T²/Z₆ bulk)",
        "falsification_link": (
            "Any θ_HR outside the perturbative range (0, π/4) would require "
            "non-perturbative treatment or rule out the GW-CW mechanism."
        ),
    },

    "WS-II": {
        "title": "9D+ CP Phase Independence for δ_CP and CKM ρ̄ (P14/P15 Robustness)",
        "dimension_target": "9D+",
        "parameter_target": "P14, P15",
        "current_status": "BEST_EVIDENCE_CONSTRAINED(9D)",
        "current_best_artifact": "src/nined/cp_phase_9d_refinement.py",
        "current_residual": "δ_CP ~1.3% nominal; propagated uncertainty <5% (gate pass)",
        "goal": (
            "Derive δ_CP from 9D+ geometry without anchoring to the 7D discrete-torsion "
            "π/3 baseline, achieving full independence from Rung-2 uncertainty"
        ),
        "prerequisites": [
            "9D+ anomaly polynomial decomposition independent of 7D torsion anchor",
            "Full Green-Schwarz counterterm in 9D with moduli-stabilized flux",
            "Rung-4 (8D→9D) KK mode spectrum with resolved CP-violating holonomy",
            "CKM ρ̄ propagation chain from δ_CP(9D) to Wolfenstein parameter",
        ],
        "key_calculation": (
            "Compute the CP-violating holonomy phase from the 9D gauge field background "
            "without the 7D discrete-torsion seed, using the anomaly matching condition "
            "between the 9D Chern-Simons coupling and the boundary GS term."
        ),
        "expected_outcome": (
            "Independent δ_CP prediction → P15 GEOMETRIC_PREDICTION if residual < 5%. "
            "P14 (ρ̄) robustness gate cleared if δ_CP uncertainty < 5% without Rung-2 anchor."
        ),
        "readiness_criteria": {
            "ET_2_baseline": True,
            "rung4_solid": True,
            "requires_9d_holonomy": True,
            "requires_gs_anomaly_matching": True,
        },
        "estimated_dimension_reach": "9D (M-theory reduction on CY₃ × S¹, δ_CP from flux)",
        "falsification_link": (
            "DUNE measurement of δ_CP outside [0.85, 1.30] rad with <3% uncertainty "
            "would falsify all geometric CP predictions in the UM."
        ),
    },

    "WS-III": {
        "title": "6D+ Simultaneous Δm²₂₁ and Δm²₃₁ Prediction (P19/P20/P21 Closure)",
        "dimension_target": "6D+",
        "parameter_target": "P19, P20, P21",
        "current_status": "GEOMETRIC_ESTIMATE_CERTIFIED (NLO improved)",
        "current_best_artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "current_residual": "Δm²₃₁ ~7-8% (NLO); Δm²₂₁ UNCONSTRAINED",
        "goal": (
            "Derive both Δm²₂₁ and Δm²₃₁ simultaneously from 6D+ fixed-point overlap "
            "integrals with exact modular geometry, without solar-sector calibration"
        ),
        "prerequisites": [
            "Full 6D+ modular geometry of T²/Z₃ fixed points (not just Gaussian approximation)",
            "Exact Kähler-moduli-dependent zero-mode profiles for all three generations",
            "RH neutrino c_{Rν} spectrum from 6D Dirac equation with backreaction",
            "Seesaw formula in 6D with both y_D (Dirac) and M_R (Majorana) from geometry",
        ],
        "key_calculation": (
            "Compute the full 3×3 Dirac Yukawa matrix y_D[i,j] from exact T²/Z₃ "
            "fixed-point overlaps including all instanton and curvature corrections, "
            "then run the seesaw formula to get three physical neutrino masses."
        ),
        "expected_outcome": (
            "Simultaneous prediction of Δm²₂₁ and Δm²₃₁ → P20 and P21 → CONSTRAINED "
            "if residuals < 50%; GEOMETRIC_ESTIMATE_CERTIFIED if < 20%."
        ),
        "readiness_criteria": {
            "ET_3_baseline": True,
            "rung1_solid": True,
            "requires_6d_modular_geometry": True,
            "requires_exact_fixed_point_integrals": True,
        },
        "estimated_dimension_reach": "6D (T²/Z₃ modular geometry; possibly 7D for seesaw)",
        "falsification_link": (
            "Hyper-Kamiokande measurement of Δm²₃₁ outside [2.2, 2.7] × 10⁻³ eV² "
            "at <1% would falsify the UM neutrino sector prediction."
        ),
    },

    "WS-IV": {
        "title": "10D CY₃ Complete Moduli/Flux α_s(M_Z) Derivation (P3 Closure)",
        "dimension_target": "10D",
        "parameter_target": "P3",
        "current_status": "ARCHITECTURE_LIMIT_CERTIFIED(10D)",
        "current_best_artifact": "src/tend/cy3_kk_thresholds_alpha_s.py",
        "current_residual": "~20% after CY₃ KK thresholds (quintic estimate)",
        "goal": (
            "Close P3 by computing α_s(M_Z) from the full 10D CY₃ compactification "
            "with all Kähler and complex-structure moduli stabilized and flux quantized"
        ),
        "prerequisites": [
            "Full Kähler moduli stabilization on quintic or mirror CY₃",
            "One-loop threshold corrections from all 101 complex-structure moduli h^{2,1}",
            "Flux lattice sum over all quantized background G-flux values",
            "RGE running from M_KK_CY3 to M_Z including all threshold corrections",
            "4D effective gauge kinetic function from dimensional reduction",
        ],
        "key_calculation": (
            "Compute f_{gauge}(z_i, ψ_j) — the 4D gauge kinetic function as a function "
            "of all Kähler moduli z_i and complex-structure moduli ψ_j — from the 10D "
            "DBI action on the CY₃, then extract α_s = 1/f at the KK threshold."
        ),
        "expected_outcome": (
            "Full α_s prediction within 5% of PDG → P3 GEOMETRIC_PREDICTION. "
            "Intermediate: ~10% residual with moduli-stabilized Kähler + complex structure."
        ),
        "readiness_criteria": {
            "ET_4_baseline": True,
            "rung5_architecture_certified": True,
            "requires_cy3_moduli_stabilization": True,
            "requires_flux_lattice_sum": True,
        },
        "estimated_dimension_reach": "10D type IIB on CY₃ (KKLT or LVS landscape)",
        "falsification_link": (
            "Any CY₃ compactification that gives α_s(M_Z) < 0.08 or > 0.14 "
            "would rule out the 10D extension of the UM direct chain."
        ),
    },
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_workstream(ws_id: str) -> Dict:
    """Return the workstream dict for workstream ID *ws_id*.

    Parameters
    ----------
    ws_id : str
        Workstream ID: 'WS-I', 'WS-II', 'WS-III', or 'WS-IV'.

    Returns
    -------
    dict
        Workstream specification (copy).

    Raises
    ------
    KeyError
        If *ws_id* is not found.
    """
    if ws_id not in WORKSTREAM_CATALOGUE:
        raise KeyError(
            f"Unknown workstream: {ws_id!r}. "
            f"Available: {sorted(WORKSTREAM_CATALOGUE)}"
        )
    return dict(WORKSTREAM_CATALOGUE[ws_id])


def list_workstreams() -> List[str]:
    """Return sorted list of all workstream IDs.

    Returns
    -------
    list[str]
        Sorted workstream IDs.
    """
    return sorted(WORKSTREAM_CATALOGUE.keys())


def readiness_check() -> Dict[str, Dict]:
    """Return readiness status for each workstream.

    For each workstream, computes which readiness criteria are met
    (based on the delivered extension track baseline artifacts).

    Returns
    -------
    dict[str, dict]
        Per-workstream readiness summary with passed/total criteria count.
    """
    # Baseline availability map (ET-1 through ET-4 all delivered)
    baseline_available = {
        "ET_1_baseline": True,
        "ET_2_baseline": True,
        "ET_3_baseline": True,
        "ET_4_baseline": True,
        "rung1_solid": True,
        "rung4_solid": True,
        "rung5_architecture_certified": True,
        # Future prerequisites requiring further research
        "requires_6d_action": False,
        "requires_moduli_stabilization": False,
        "requires_brane_propagators": False,
        "requires_9d_holonomy": False,
        "requires_gs_anomaly_matching": False,
        "requires_6d_modular_geometry": False,
        "requires_exact_fixed_point_integrals": False,
        "requires_cy3_moduli_stabilization": False,
        "requires_flux_lattice_sum": False,
    }

    result = {}
    for ws_id, ws in WORKSTREAM_CATALOGUE.items():
        criteria = ws["readiness_criteria"]
        passed = sum(1 for k, v in criteria.items() if baseline_available.get(k, False) == v)
        total = len(criteria)
        result[ws_id] = {
            "title": ws["title"],
            "criteria_passed": passed,
            "criteria_total": total,
            "readiness_fraction": passed / total if total > 0 else 0.0,
            "baseline_delivered": criteria.get("ET_1_baseline", False)
                or criteria.get("ET_2_baseline", False)
                or criteria.get("ET_3_baseline", False)
                or criteria.get("ET_4_baseline", False),
            "current_status": ws["current_status"],
            "dimension_target": ws["dimension_target"],
        }
    return result


def roadmap_summary() -> Dict:
    """Return a full summary of the dimensional extension roadmap.

    Returns
    -------
    dict
        Summary including workstream count, dimension targets, readiness overview,
        and falsification links.
    """
    readiness = readiness_check()
    dimension_targets = {ws_id: ws["dimension_target"] for ws_id, ws in WORKSTREAM_CATALOGUE.items()}
    parameter_targets = {ws_id: ws["parameter_target"] for ws_id, ws in WORKSTREAM_CATALOGUE.items()}
    falsifiers = {ws_id: ws["falsification_link"] for ws_id, ws in WORKSTREAM_CATALOGUE.items()}

    total_baselines_delivered = sum(
        1 for r in readiness.values() if r["baseline_delivered"]
    )

    return {
        "workstream_count": len(WORKSTREAM_CATALOGUE),
        "workstream_ids": list_workstreams(),
        "dimension_targets": dimension_targets,
        "parameter_targets": parameter_targets,
        "readiness": readiness,
        "total_baselines_delivered": total_baselines_delivered,
        "falsification_links": falsifiers,
        "governance": {
            "mas_reopen_allowed": False,
            "scope_rule": "each workstream is an independent research programme",
            "anti_recycle_rule": "workstream findings are NOT routed back into MAS",
        },
        "note": (
            "All 4 baseline workstreams have extension-track artifacts. "
            "Completing WS-I through WS-IV would advance the architecture-limited "
            "parameters (P3, P5, P14/P15, P19–P21) toward GEOMETRIC_PREDICTION status."
        ),
    }


def execution_freeze_status() -> Dict[str, Dict[str, str]]:
    """Return frozen WS-I..WS-IV execution outcomes from the 2026-05-08 run.

    Returns
    -------
    dict[str, dict[str, str]]
        Workstream execution status and post-freeze action.
    """
    return {
        "WS-II": {
            "status": "PASS_FREEZE",
            "post_freeze_action": "frozen",
        },
        "WS-III": {
            "status": "TARGETED_FOLLOW_UP_FREEZE",
            "post_freeze_action": "open_targeted_workstream_ticket",
        },
        "WS-I": {
            "status": "TARGETED_FOLLOW_UP_FREEZE",
            "post_freeze_action": "open_targeted_workstream_ticket",
        },
        "WS-IV": {
            "status": "TARGETED_FOLLOW_UP_FREEZE",
            "post_freeze_action": "open_targeted_workstream_ticket",
        },
    }
