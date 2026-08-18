# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar691_ckm_jarlskog_hardgate_assessment.py
==========================
Pillar 691 — CKM Jarlskog Hardgate Assessment

Applies a 5% hardgate criterion to the Sprint Y CKM observables.  Eta-bar and
J_CP pass comfortably, but rho-bar fails decisively for the implemented Layer 2
FN ansatz, so the overall verdict remains architecture-limited.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
from typing import Any, Dict

__all__ = [
    "N_W",
    "K_CS",
    "W_RHOBAR_PDG",
    "W_ETABAR_PDG",
    "W_J_PDG",
    "ckm_hardgate_assessment",
    "jarlskog_hardgate_verdict",
    "sprint_y_summary",
]

N_W = 5
K_CS = 74
N1 = 5
N2 = 7
W_RHOBAR_PDG = 0.159
W_ETABAR_PDG = 0.348
W_J_PDG = 3.08e-5
W_LAMBDA_PDG = 0.225
W_A_PDG = 0.826
EPSILON_FN = N_W / K_CS
M_U_MEV = 2.16
M_T_MEV = 172760.0


def _r_b() -> float:
    vub_geo = math.sqrt(M_U_MEV / M_T_MEV)
    a_geo = math.sqrt(N1 / N2)
    return vub_geo / (a_geo * W_LAMBDA_PDG**3)


def _rho_eta_j() -> Dict[str, float]:
    delta_sub = 2.0 * math.atan2(N1, N2)
    harmonic = 2.0 * math.pi / N_W
    delta_fn = math.atan2(EPSILON_FN * math.sin(harmonic), 1.0 - EPSILON_FN * math.cos(harmonic))
    rho_bar = _r_b() * math.cos(delta_sub + delta_fn)
    eta_bar = math.sqrt(max(_r_b() * _r_b() - rho_bar * rho_bar, 0.0))
    c_lambda = 1.0 / K_CS
    c_a = 2.5 / K_CS
    lambda_fn = W_LAMBDA_PDG * (1.0 + EPSILON_FN * c_lambda)
    a_fn = W_A_PDG * (1.0 + EPSILON_FN * c_a)
    j_cp = lambda_fn**6 * a_fn**2 * eta_bar
    return {"rho_bar": rho_bar, "eta_bar": eta_bar, "J_CP": j_cp}


def _observable_assessment(name: str, predicted: float, pdg: float) -> Dict[str, Any]:
    gap = abs(predicted - pdg) / pdg * 100.0
    return {
        "observable": name,
        "predicted": predicted,
        "pdg": pdg,
        "gap_percent": gap,
        "passes_5_percent": gap < 5.0,
        "verdict": "HARDGATE" if gap < 5.0 else "ARCHITECTURE_LIMIT",
    }


def ckm_hardgate_assessment() -> Dict[str, Any]:
    """Assess rho-bar, eta-bar, and J_CP against the 5% hardgate rule."""
    values = _rho_eta_j()
    rho = _observable_assessment("rho_bar", values["rho_bar"], W_RHOBAR_PDG)
    eta = _observable_assessment("eta_bar", values["eta_bar"], W_ETABAR_PDG)
    jcp = _observable_assessment("J_CP", values["J_CP"], W_J_PDG)
    return {
        "pillar": 691,
        "status": "CKM_HARDGATE_ASSESSED",
        "rho_bar": rho,
        "eta_bar": eta,
        "J_CP": jcp,
        "overall_pass": all(item["passes_5_percent"] for item in (rho, eta, jcp)),
    }


def jarlskog_hardgate_verdict() -> Dict[str, Any]:
    """Return the overall Sprint Y hardgate verdict."""
    assessment = ckm_hardgate_assessment()
    overall = "HARDGATE" if assessment["overall_pass"] else "ARCHITECTURE_LIMIT"
    failing = [name for name in ("rho_bar", "eta_bar", "J_CP") if not assessment[name]["passes_5_percent"]]
    return {
        "pillar": 691,
        "overall_verdict": overall,
        "failing_observables": failing,
        "passing_observables": [name for name in ("rho_bar", "eta_bar", "J_CP") if assessment[name]["passes_5_percent"]],
        "hardgate_rule_percent": 5.0,
    }


def sprint_y_summary() -> Dict[str, Any]:
    """Return a concise Sprint Y status summary."""
    assessment = ckm_hardgate_assessment()
    verdict = jarlskog_hardgate_verdict()
    return {
        "pillar": 691,
        "sprint": "Sprint Y",
        "status": verdict["overall_verdict"],
        "assessment": assessment,
        "verdict": verdict,
        "honest_note": (
            "Eta-bar and J_CP are within 5%, but rho-bar is not. Sprint Y therefore "
            "lands at architecture-limit status rather than hardgate closure."
        ),
    }
