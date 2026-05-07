# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""WS-F Deliverables F1–F3 — Higgs Mass Architecture Extension Memo (P5).

═══════════════════════════════════════════════════════════════════════════
MAS WORKSTREAM: WS-F  (P5 m_H)
Gate criteria: extension design memo, go/no-go theorems, selected path
═══════════════════════════════════════════════════════════════════════════

DELIVERABLE F1: EXTENSION DESIGN MEMO
---------------------------------------
The Higgs boson mass m_H = 125.25 GeV requires deriving the Higgs quartic
coupling λ_H from the 5D bulk potential.  In the SM:

    m_H² = 2 λ_H v²   →   λ_H = m_H² / (2v²) ≈ 0.129

Three architectural routes are evaluated:

Option 1: RS1 + Gauge-Higgs Unification (GHU)
    The Higgs is identified with the 5th component of a 5D gauge field.
    The 4D quartic coupling arises from the 5D gauge coupling:
        λ_H = g₅² / (2 × Vol_RS1)
    For g₅² ~ k/(4π) (naive dimensional analysis), this gives:
        λ_H^{GHU} ≈ g₅² × k exp(−4πkR) ≈ tiny (exponentially suppressed)
    STATUS: λ_H too small by many orders — KILLED by NDA estimate.

Option 2: GW Coleman-Weinberg Potential
    The Goldberger-Wise field φ(y) develops a Coleman-Weinberg (CW) potential
    that induces a Higgs quartic coupling via the Higgs-radion mixing angle θ_HR:
        λ_H^{CW} = λ_H^{tree} + θ_HR² × λ_radion^{CW}
    where λ_radion^{CW} = (m_radion / v)² / 2.
    For m_radion ≈ M_KK × exp(−πkR) ≈ TeV (from GW):
        λ_H^{CW} depends on θ_HR — a free mixing angle parameter.
    STATUS: one free parameter (θ_HR) survives; not a zero-parameter derivation.

Option 3: 5D Dilaton Portal
    The bulk dilaton Φ(x,y) develops an IR VEV that couples to the Higgs via:
        L_dilaton = η × Φ × |H|² (IR brane coupling)
    The dilaton mass m_Φ is set by the GW mechanism; the coupling η determines
    the Higgs mass through the dilaton contribution to the vacuum energy.
    STATUS: two free parameters (η, m_Φ mixing); architecture limit remains.

DELIVERABLE F2: GO/NO-GO THEOREMS
-----------------------------------
Theorem WSF-1 (GHU Killing): For the 5D RS1 setup with πkR = 37,
    λ_H^{GHU} = g₅² × k exp(−4πkR) ≪ λ_H^{PDG}.
    → Exponential suppression kills GHU as a standalone mechanism.
    → GO/NO-GO: NO-GO for pure GHU.

Theorem WSF-2 (GW-CW Requirement): The Higgs quartic from GW Coleman-Weinberg
    requires the Higgs-radion mixing angle θ_HR as a free parameter.
    Without an independent derivation of θ_HR, P5 cannot be closed.
    → GO/NO-GO: CONDITIONAL GO — go only if θ_HR is derived from geometry.

Theorem WSF-3 (Dilaton Portal): The dilaton portal coupling η must be O(1)
    to give m_H ≈ 125 GeV.  Natural O(1) values are geometrically allowed
    (GW naturalness), but the EXACT value is not determined.
    → GO/NO-GO: CONDITIONAL GO — same condition as GW-CW.

DELIVERABLE F3: SELECTED EXTENSION BRANCH
-------------------------------------------
The GW-CW route (Option 2) is selected as the most promising.
Kill-switches and stop criteria are defined below.

HONEST VERDICT: P5 remains OPEN (ARCHITECTURE LIMIT) until the
Higgs-radion mixing angle θ_HR is derived from the 5D geometry.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    # Constants
    "N_W", "K_CS", "PI_KR",
    "M_H_PDG_GEV", "V_HIGGS_GEV",
    "LAMBDA_H_PDG",
    "M_KK_GEV",
    "LAMBDA_H_GHU_EST",
    "LAMBDA_H_GHU_PDG_RATIO",
    "WSF_STATUS",
    # Functions
    "higgs_mass_from_quartic",
    "option_ghu",
    "option_gw_cw",
    "option_dilaton_portal",
    "theorem_wsf_1",
    "theorem_wsf_2",
    "theorem_wsf_3",
    "selected_extension_branch",
    "wsf_gate_report",
    "pillar_wsf_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
PI_KR: float = float(K_CS) / 2.0    # = 37.0
M_PL_GEV: float = 1.22e19

M_H_PDG_GEV: float = 125.25
V_HIGGS_GEV: float = 246.22
LAMBDA_H_PDG: float = M_H_PDG_GEV ** 2 / (2.0 * V_HIGGS_GEV ** 2)

M_KK_GEV: float = M_PL_GEV * math.exp(-PI_KR)

# GHU estimate: λ_H^{GHU} = g₅² × k × exp(−4πkR)
# With g₅² ~ k/(4π) (NDA), k ~ M_Pl:
_G5_SQ_NDA: float = M_PL_GEV / (4.0 * math.pi)
LAMBDA_H_GHU_EST: float = _G5_SQ_NDA * M_PL_GEV * math.exp(-4.0 * PI_KR)
LAMBDA_H_GHU_PDG_RATIO: float = LAMBDA_H_GHU_EST / max(LAMBDA_H_PDG, 1e-100)

WSF_STATUS: str = "OPEN (ARCHITECTURE LIMIT) — θ_HR or dilaton coupling not yet derived from geometry"


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def higgs_mass_from_quartic(lambda_h: float = LAMBDA_H_PDG) -> Dict[str, float]:
    """Compute Higgs boson mass from quartic coupling.

    m_H² = 2 λ_H v²

    Parameters
    ----------
    lambda_h : float  Higgs quartic coupling.

    Returns
    -------
    dict with m_H and comparison to PDG.
    """
    m_h = math.sqrt(2.0 * lambda_h) * V_HIGGS_GEV
    pct_err = abs(m_h - M_H_PDG_GEV) / M_H_PDG_GEV * 100.0
    return {
        "lambda_h": lambda_h,
        "m_h_gev": m_h,
        "m_h_pdg_gev": M_H_PDG_GEV,
        "pct_err": pct_err,
    }


def option_ghu(pi_kr: float = PI_KR, m_pl_gev: float = M_PL_GEV) -> Dict[str, object]:
    """Evaluate Option 1: RS1 + Gauge-Higgs Unification.

    Returns
    -------
    dict with λ_H estimate, verdict, and kill-switch check.
    """
    g5_sq = m_pl_gev / (4.0 * math.pi)   # NDA estimate
    lambda_h_ghu = g5_sq * m_pl_gev * math.exp(-4.0 * pi_kr)
    ratio = lambda_h_ghu / max(LAMBDA_H_PDG, 1e-100)
    m_h_ghu = math.sqrt(max(2.0 * lambda_h_ghu, 0.0)) * V_HIGGS_GEV
    return {
        "option": "GHU (Gauge-Higgs Unification)",
        "lambda_h_ghu": lambda_h_ghu,
        "lambda_h_pdg": LAMBDA_H_PDG,
        "ratio": ratio,
        "m_h_gev_estimate": m_h_ghu,
        "verdict": "NO-GO",
        "reason": (
            f"λ_H^{{GHU}} ≈ {lambda_h_ghu:.3e} vs λ_H^{{PDG}} = {LAMBDA_H_PDG:.4f}.  "
            f"Ratio = {ratio:.3e} — exponentially suppressed.  "
            "GHU alone cannot produce the observed Higgs mass."
        ),
        "kill_switch_triggered": True,
    }


def option_gw_cw(
    m_radion_gev: float = None,
    theta_hr: float = 0.1,
) -> Dict[str, object]:
    """Evaluate Option 2: GW Coleman-Weinberg potential.

    Parameters
    ----------
    m_radion_gev : float, optional  Radion mass [GeV] (default: M_KK/10).
    theta_hr     : float            Higgs-radion mixing angle (free parameter).

    Returns
    -------
    dict with λ_H estimate, verdict, and gate check.
    """
    if m_radion_gev is None:
        m_radion_gev = M_KK_GEV / 10.0   # rough estimate
    lambda_radion = (m_radion_gev / V_HIGGS_GEV) ** 2 / 2.0
    lambda_h_cw = theta_hr ** 2 * lambda_radion
    m_h_cw = math.sqrt(max(2.0 * lambda_h_cw, 0.0)) * V_HIGGS_GEV
    pct_err = abs(m_h_cw - M_H_PDG_GEV) / M_H_PDG_GEV * 100.0
    return {
        "option": "GW Coleman-Weinberg",
        "theta_hr_free_parameter": theta_hr,
        "m_radion_gev": m_radion_gev,
        "lambda_radion_cw": lambda_radion,
        "lambda_h_cw": lambda_h_cw,
        "m_h_gev_estimate": m_h_cw,
        "pct_err": pct_err,
        "verdict": "CONDITIONAL GO",
        "condition": "θ_HR must be derived from 5D geometry to close P5",
        "free_parameters_remaining": 1,
        "free_parameter_name": "Higgs-radion mixing angle θ_HR",
        "kill_switch": "If θ_HR is not uniquely determined by 5D geometry → stop",
    }


def option_dilaton_portal(
    eta_coupling: float = 1.0,
    m_dilaton_gev: float = None,
) -> Dict[str, object]:
    """Evaluate Option 3: 5D dilaton portal.

    Parameters
    ----------
    eta_coupling  : float  Dilaton-Higgs coupling on IR brane (free parameter).
    m_dilaton_gev : float, optional  Dilaton mass [GeV].

    Returns
    -------
    dict with estimate, verdict, and gate check.
    """
    if m_dilaton_gev is None:
        m_dilaton_gev = M_KK_GEV / 3.0
    lambda_h_dilaton = eta_coupling * (m_dilaton_gev / V_HIGGS_GEV) ** 2 / 2.0
    m_h_dilaton = math.sqrt(max(2.0 * lambda_h_dilaton, 0.0)) * V_HIGGS_GEV
    pct_err = abs(m_h_dilaton - M_H_PDG_GEV) / M_H_PDG_GEV * 100.0
    return {
        "option": "5D Dilaton Portal",
        "eta_coupling_free_parameter": eta_coupling,
        "m_dilaton_gev": m_dilaton_gev,
        "lambda_h_dilaton": lambda_h_dilaton,
        "m_h_gev_estimate": m_h_dilaton,
        "pct_err": pct_err,
        "verdict": "CONDITIONAL GO",
        "condition": "Both η and m_dilaton must be derived from 5D geometry",
        "free_parameters_remaining": 2,
        "free_parameter_names": ["η (dilaton-Higgs coupling)", "m_dilaton (dilaton mass)"],
        "kill_switch": "If η and m_dilaton not uniquely determined → stop",
    }


def theorem_wsf_1() -> Dict[str, object]:
    """Return Theorem WSF-1: GHU killing theorem.

    Returns
    -------
    dict with statement, proof, and verdict.
    """
    ghu = option_ghu()
    return {
        "theorem_id": "WSF-1",
        "name": "GHU Killing Theorem",
        "statement": (
            "For the RS1 setup with πkR = 37: "
            "λ_H^{GHU} = g₅² × k × exp(−4πkR) ≪ λ_H^{PDG}.  "
            "Gauge-Higgs Unification alone cannot generate the observed Higgs mass."
        ),
        "proof": (
            "By NDA: g₅² ~ k/(4π) ~ M_Pl/(4π).  "
            f"λ_H^{{GHU}} ~ (M_Pl²/(4π)) × exp(−4×37) = {LAMBDA_H_GHU_EST:.3e}.  "
            f"This is smaller than λ_H^{{PDG}} = {LAMBDA_H_PDG:.4f} "
            f"by a factor of {LAMBDA_H_GHU_PDG_RATIO:.3e}.  "
            "The exponential suppression exp(−148) ≈ 10⁻⁶⁴ is irreducible."
        ),
        "verdict": "NO-GO",
        "ghu_estimate": ghu,
    }


def theorem_wsf_2() -> Dict[str, object]:
    """Return Theorem WSF-2: GW-CW requirement theorem."""
    return {
        "theorem_id": "WSF-2",
        "name": "GW-CW Requirement Theorem",
        "statement": (
            "The GW Coleman-Weinberg route to m_H requires the Higgs-radion "
            "mixing angle θ_HR as an independent free parameter.  Without a "
            "geometric derivation of θ_HR, P5 cannot be closed."
        ),
        "proof": (
            "λ_H^{CW} = θ_HR² × (m_radion/v)² / 2.  "
            "m_radion is set by the GW mechanism (derived).  "
            "θ_HR is determined by the Higgs-radion coupling at the IR brane, "
            "which requires knowledge of the brane-localized kinetic mixing term.  "
            "This term is not fixed by the 5D bulk geometry alone."
        ),
        "verdict": "CONDITIONAL GO — requires geometric derivation of θ_HR",
        "gate_condition": "Derive θ_HR from 5D action without free parameters",
    }


def theorem_wsf_3() -> Dict[str, object]:
    """Return Theorem WSF-3: dilaton portal naturalness."""
    return {
        "theorem_id": "WSF-3",
        "name": "Dilaton Portal Naturalness Theorem",
        "statement": (
            "The dilaton portal coupling η = O(1) is consistent with GW "
            "naturalness.  However, the EXACT value needed for m_H = 125 GeV "
            "is not uniquely fixed by the 5D geometry."
        ),
        "proof": (
            "The GW vacuum is at φ₀ = 1 (Pillar 56).  All couplings in the "
            "IR-brane action are O(1) by naturalness.  The coupling η × Φ × |H|² "
            "has η natural in (0.01, 10), but no further constraint restricts η "
            "to the unique value required for m_H = 125.25 GeV."
        ),
        "verdict": "CONDITIONAL GO — same condition as WSF-2",
        "gate_condition": "Derive η from 5D bulk action without free parameters",
    }


def selected_extension_branch() -> Dict[str, object]:
    """Return the WS-F Deliverable F3 selected extension branch.

    The GW-CW route is selected as the most promising.

    Returns
    -------
    dict with selected branch, kill-switches, and stop criteria.
    """
    return {
        "deliverable": "WS-F / F3 — Selected extension branch",
        "selected_option": "Option 2: GW Coleman-Weinberg",
        "rationale": (
            "The GW-CW route is the most natural extension: the GW mechanism "
            "already stabilizes the extra dimension (πkR = 37), and the radion "
            "mass m_radion ~ M_KK is geometrically determined.  The only "
            "additional ingredient is the Higgs-radion mixing angle θ_HR."
        ),
        "open_parameter": "θ_HR (Higgs-radion mixing angle)",
        "derivation_path": (
            "Compute the brane-localized kinetic mixing term from the 5D bulk "
            "Higgs action: S_IR = ∫ d⁴x [c_H × (∂_μ H)² + ...].  The coupling "
            "c_H is fixed by the 5D Yukawa + GW parameters if the Higgs is "
            "bulk-extended (bulk Higgs).  For brane-localized Higgs, θ_HR is "
            "determined by the GW-induced curvature of the Higgs potential."
        ),
        "kill_switches": [
            "θ_HR not derivable from 5D action → stop, archive, keep P5 OPEN",
            "GHU estimate exceeds naturalness bound → discard Option 1 permanently",
            "Dilaton mixing introduces new flat direction → stop dilaton route",
        ],
        "stop_criteria": [
            "If no geometric derivation of θ_HR after exhausting 5D/6D extensions",
            "If loop corrections make λ_H uncontrollable in the IR",
        ],
        "current_status": WSF_STATUS,
        "gate_passed": True,   # F3 memo delivered; P5 status unchanged
    }


def wsf_gate_report() -> Dict[str, object]:
    """Consolidated WS-F gate evidence report (F1 + F2 + F3).

    Returns
    -------
    dict for attachment to MAS W5 ledger.
    """
    f1 = {
        "ghu": option_ghu(),
        "gw_cw": option_gw_cw(),
        "dilaton": option_dilaton_portal(),
    }
    f2 = {
        "theorem_wsf_1": theorem_wsf_1(),
        "theorem_wsf_2": theorem_wsf_2(),
        "theorem_wsf_3": theorem_wsf_3(),
    }
    f3 = selected_extension_branch()
    return {
        "workstream": "WS-F",
        "parameter": "P5 (m_H)",
        "deliverable_F1_extension_design_memo": f1,
        "deliverable_F2_go_no_go_theorems": f2,
        "deliverable_F3_selected_branch": f3,
        "gate_passed": True,   # memos and theorems delivered
        "status_change": "NONE — P5 remains OPEN (ARCHITECTURE LIMIT)",
        "honest_conclusion": (
            "All three routes (GHU, GW-CW, dilaton portal) require at least "
            "one additional free parameter.  GHU is killed by Theorem WSF-1.  "
            "GW-CW and dilaton routes are conditionally viable if θ_HR or η "
            "can be derived from 5D geometry.  P5 stays OPEN."
        ),
    }


def pillar_wsf_summary() -> Dict[str, object]:
    """Return a brief WS-F summary for the MAS ledger."""
    return {
        "workstream": "WS-F",
        "parameter": "P5 (m_H = 125.25 GeV)",
        "gate_passed": True,
        "status": WSF_STATUS,
        "ghu_killed": True,
        "selected_branch": "GW Coleman-Weinberg",
        "open_parameter": "Higgs-radion mixing angle θ_HR",
        "rung_impact": (
            "GHU killed by NDA estimate.  GW-CW selected as extension branch.  "
            "P5 stays OPEN until θ_HR derived."
        ),
    }
