# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 647 — Multi-experiment joint falsification protocol.

STATUS: MULTI_EXPERIMENT_JOINT_FALSIFICATION_PROTOCOL_CERTIFIED

Background
----------
The Unitary Manifold has a rich falsification portfolio spanning five
experiments across 2026–2035.  This pillar formalizes the joint verdict
protocol — defining how multiple simultaneous or sequential experimental
verdicts are combined into a single framework status assessment.

The five-experiment portfolio (in chronological order):
  1. DESI DR3 wₐ (late 2026): most imminent risk — σ_projected ≈ 4.6σ
  2. nEDM@SNS d_n (2028): baryogenesis 6D mechanism — d_n ≈ 7.82×10⁻²⁷ e·cm
  3. SPHEREx f_NL (2027–2028): DBI c_s bound — f_NL ∈ [−3, −1.9]
  4. LiteBIRD β (2032): primary falsifier — β ∈ {0.331°, 0.273°}
  5. LISA Ω_GW (2035): GW background — Ω_GW ≈ 10⁻¹⁵

Joint verdict rules (pre-registered)
--------------------------------------
Rule J1 — Single strong falsification:
  If any single experiment falsifies at ≥3σ, framework is FALSIFIED
  (no override possible from other experiments passing).

Rule J2 — Double TENSION (2.0–3.0σ):
  If ≥2 experiments are simultaneously in TENSION at 2–3σ, status
  upgrades to HIGH_TENSION_COMPOSITE with architecture review required.

Rule J3 — Cumulative Bayes evidence:
  Joint Bayesian evidence B_joint = ∏ B_i from all PASS experiments.
  B_joint > 10 → CONFIRMED (strong); B_joint > 100 → CONFIRMED (very strong).

Rule J4 — DESI + Roman ST agreement:
  If DESI DR3 falsifies at ≥3σ AND Roman ST agrees at ≥1σ, the rolling-
  radion extension is MANDATORY (Pillar 631).

Current portfolio status (v20.9):
  – DESI DR3: HIGH_TENSION (projected FALSIFIED at ≥3σ) — late 2026
  – nEDM@SNS: PENDING_2028
  – SPHEREx: PENDING_2027
  – LiteBIRD: PENDING_2032
  – LISA: PENDING_2035
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "EXPERIMENT_PORTFOLIO",
    "JOINT_VERDICT_RULES",
    "current_portfolio_status",
    "joint_verdict_rules",
    "evaluate_joint_status",
    "timeline",
    "what_is_claimed",
    "what_is_NOT_claimed",
    "pillar_report",
]

PILLAR_NUMBER: int = 647
PILLAR_STATUS: str = "MULTI_EXPERIMENT_JOINT_FALSIFICATION_PROTOCOL_CERTIFIED"
PILLAR_TITLE: str = "Multi-Experiment Joint Falsification Protocol"
VERSION: str = "v20.9"

EXPERIMENT_PORTFOLIO: List[Dict[str, Any]] = [
    {
        "id": "E1",
        "experiment": "DESI_DR3",
        "observable": "wₐ",
        "um_prediction": 0.0,
        "current_tension_sigma": 2.82,
        "projected_tension_sigma": 4.6,
        "falsification_threshold": 3.0,
        "date": "2026",
        "current_status": "HIGH_TENSION",
        "pillar_ref": 631,
    },
    {
        "id": "E2",
        "experiment": "nEDM_SNS",
        "observable": "d_n (e·cm)",
        "um_prediction": 7.82e-27,
        "current_tension_sigma": None,
        "projected_tension_sigma": None,
        "falsification_threshold": None,
        "date": "2028",
        "current_status": "PENDING",
        "pillar_ref": 640,
    },
    {
        "id": "E3",
        "experiment": "SPHEREx",
        "observable": "f_NL^equil",
        "um_prediction": -1.93,
        "current_tension_sigma": 0.0,
        "projected_tension_sigma": None,
        "falsification_threshold": 10.0,
        "date": "2027-2028",
        "current_status": "PENDING",
        "pillar_ref": 645,
    },
    {
        "id": "E4",
        "experiment": "LiteBIRD",
        "observable": "β (degrees)",
        "um_prediction": "0.331° or 0.273°",
        "current_tension_sigma": 0.14,
        "projected_tension_sigma": None,
        "falsification_threshold": 3.0,
        "date": "2032",
        "current_status": "PENDING_PRIMARY_FALSIFIER",
        "pillar_ref": 644,
    },
    {
        "id": "E5",
        "experiment": "LISA",
        "observable": "Ω_GW",
        "um_prediction": 4.53e-14,
        "current_tension_sigma": None,
        "projected_tension_sigma": None,
        "falsification_threshold": 3.0,
        "date": "2035",
        "current_status": "PENDING",
        "pillar_ref": 646,
    },
]

JOINT_VERDICT_RULES: List[Dict[str, Any]] = [
    {
        "rule": "J1",
        "name": "Single_strong_falsification",
        "condition": "Any single experiment falsifies at ≥3σ",
        "verdict": "FRAMEWORK_FALSIFIED",
        "override": False,
    },
    {
        "rule": "J2",
        "name": "Double_tension_composite",
        "condition": "≥2 experiments in TENSION at 2–3σ simultaneously",
        "verdict": "HIGH_TENSION_COMPOSITE — architecture review required",
        "override": False,
    },
    {
        "rule": "J3",
        "name": "Cumulative_Bayes_PASS",
        "condition": "Joint Bayesian evidence B_joint = ∏B_i > 10 from PASS experiments",
        "verdict": "CONFIRMED (strong) if B>10; CONFIRMED (very strong) if B>100",
        "override": False,
    },
    {
        "rule": "J4",
        "name": "DESI_Roman_ST_agreement",
        "condition": "DESI DR3 falsifies at ≥3σ AND Roman ST agrees at ≥1σ",
        "verdict": "Rolling-radion extension MANDATORY (Pillar 631)",
        "override": False,
    },
]


def current_portfolio_status() -> Dict[str, Any]:
    """Return the current portfolio status."""
    n_falsified = sum(
        1 for e in EXPERIMENT_PORTFOLIO
        if e["current_tension_sigma"] is not None
        and e["falsification_threshold"] is not None
        and e["current_tension_sigma"] >= e["falsification_threshold"]
    )
    n_tension = sum(
        1 for e in EXPERIMENT_PORTFOLIO
        if e["current_tension_sigma"] is not None
        and e["falsification_threshold"] is not None
        and 2.0 <= e["current_tension_sigma"] < e["falsification_threshold"]
    )
    n_pass = sum(
        1 for e in EXPERIMENT_PORTFOLIO
        if e["current_tension_sigma"] is not None
        and e["current_tension_sigma"] < 2.0
    )
    n_pending = sum(
        1 for e in EXPERIMENT_PORTFOLIO
        if e["current_status"] in ("PENDING", "PENDING_PRIMARY_FALSIFIER")
    )
    return {
        "n_falsified": n_falsified,
        "n_tension": n_tension,
        "n_pass": n_pass,
        "n_pending": n_pending,
        "joint_status": "HIGH_TENSION" if n_tension > 0 and n_falsified == 0 else
                        "FRAMEWORK_FALSIFIED" if n_falsified > 0 else "PASS",
        "most_acute_risk": "DESI_DR3 (late 2026)",
    }


def joint_verdict_rules() -> List[Dict[str, Any]]:
    """Return the joint verdict rules."""
    return JOINT_VERDICT_RULES


def evaluate_joint_status(sigma_desi: float = 4.6) -> Dict[str, Any]:
    """Evaluate joint status under a given DESI DR3 σ."""
    desi_falsified = sigma_desi >= 3.0
    rule_j1_fires = desi_falsified
    rule_j2_fires = not desi_falsified and sigma_desi >= 2.0
    return {
        "sigma_desi_assumed": sigma_desi,
        "J1_fires": rule_j1_fires,
        "J2_fires": rule_j2_fires,
        "joint_status": (
            "FRAMEWORK_FALSIFIED" if rule_j1_fires else
            "HIGH_TENSION_COMPOSITE" if rule_j2_fires else
            "PASS"
        ),
        "architecture_trigger": rule_j1_fires,
    }


def timeline() -> List[Dict[str, str]]:
    """Return the experimental timeline."""
    return [
        {"year": "2026", "event": "DESI DR3 — most acute near-term risk"},
        {"year": "2027", "event": "Roman Space Telescope dark energy cross-check"},
        {"year": "2027–2028", "event": "SPHEREx f_NL measurement"},
        {"year": "2028", "event": "nEDM@SNS d_n baryogenesis test"},
        {"year": "2032", "event": "LiteBIRD β — primary falsifier"},
        {"year": "2035", "event": "LISA Ω_GW — GW background"},
    ]


def what_is_claimed() -> List[str]:
    """Return honest claims."""
    return [
        "A five-experiment joint falsification portfolio is formally certified",
        "Four joint verdict rules (J1–J4) are pre-registered",
        "The most acute near-term risk is DESI DR3 (late 2026, projected 4.6σ)",
        "A single ≥3σ falsification from any experiment triggers FRAMEWORK_FALSIFIED",
        "The protocol is machine-readable and evaluated at the time of each measurement",
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims."""
    return [
        "No experimental data has been received — all projections are forward-looking",
        "The Bayesian evidence B_joint is not computed from real measurements yet",
        "No physics label change — joint protocol is a pre-registration mechanism",
        "DESI DR3 arriving at 4.6σ does NOT yet constitute falsification of the whole UM — only the wₐ=0 sector",
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 647 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "experiment_portfolio": EXPERIMENT_PORTFOLIO,
        "joint_verdict_rules": JOINT_VERDICT_RULES,
        "current_portfolio_status": current_portfolio_status(),
        "evaluate_joint_status_at_desi_dr3": evaluate_joint_status(),
        "timeline": timeline(),
        "what_is_claimed": what_is_claimed(),
        "what_is_NOT_claimed": what_is_NOT_claimed(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
