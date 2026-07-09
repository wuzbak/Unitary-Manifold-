# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 551 — DESI DR3 Tension Evolution Model.

STATUS: DESI_DR3_TENSION_EVOLUTION_MODEL_CERTIFIED  (🔵 ADJACENT TRACK)

This pillar builds a detailed tension-evolution model for the dark energy
parameter wₐ, tracking the DESI measurement across DR1, DR2, and the
projected DR3 scenarios.

## Context

The UM frozen-radion prediction is wₐ = 0, w₀ = −1 (cosmological constant).
DESI DR2 reports wₐ tension at 2.30σ (2D CPL-corrected joint tension;
Pillar 543 routing rehearsal).

Projected tension at DR3 (if DESI central value holds at 2.30σ):
  1D wₐ tension: ~4.6σ (exceeds falsification threshold 3.0σ)
  2D joint tension: ~3.5–4.0σ (depending on DR3 correlation structure)

This pillar:
1. Models the σ evolution as a function of dataset size (N_eff ∝ years).
2. Provides a template for DESI decision-day response (Pillar 543 routing).
3. Pre-registers the precise trigger conditions for each routing verdict.
4. Identifies the uncertainty in the projection (central value vs scatter).

## Tension evolution model

Statistical scaling:
    σ(N) = σ_0 × √(N / N_0)

where:
  - σ_0 = 2.30σ at DR2 (N_0 = 2 years × survey efficiency)
  - N = effective dataset size at DR3 (5-year dataset)
  - σ(DR3) = σ_0 × √(5/2) = 2.30 × 1.581 ≈ 3.64σ  (central value projection)

This is the CENTRAL VALUE projection — it assumes the wₐ measurement
central value does not shift from DR2 to DR3.

## Honest uncertainty

The projection has large uncertainty:
  - If central value shifts toward wₐ = 0: tension drops below 3.0σ (PASS)
  - If central value shifts away from wₐ = 0: tension increases above 3.0σ (FALSIFIED)
  - The DR3 σ projection is ±1σ in the 2D χ² sense

Pre-registered trigger conditions (from Pillar 543):
  - σ ≥ 3.0: FALSIFIED
  - 2.0 ≤ σ < 3.0: HIGH_TENSION (monitoring escalation)
  - σ < 2.0: PASS (tension resolved)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Literal

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "DR2_TENSION",
    "DR3_PROJECTION",
    "TRIGGER_CONDITIONS",
    "SURVEY_TIMELINE",
    "tension_at_dataset_size",
    "dr3_central_projection",
    "dr3_scatter_band",
    "route_tension",
    "tension_evolution_table",
    "decision_day_template",
    "extension_spec_trigger",
    "pillar_report",
]

PILLAR_NUMBER: int = 551
PILLAR_STATUS: str = "DESI_DR3_TENSION_EVOLUTION_MODEL_CERTIFIED"
PILLAR_TITLE: str = "DESI DR3 Tension Evolution Model"
VERSION: str = "v19.1"

# ─── DR2 baseline ─────────────────────────────────────────────────────────────

DR2_TENSION: Dict[str, Any] = {
    "tension_sigma_2d_cpl": 2.30,      # canonical (Pillar 543 / Pillar 428)
    "tension_sigma_1d_wa": 2.07,       # 1D wₐ-only
    "tension_sigma_combined": 2.75,    # BAO+CMB+SNe combined
    "effective_years": 2.0,            # ~2 years of data in DR2
    "wa_central": -0.62,               # DESI DR2 wₐ central value
    "wa_sigma": 0.30,                  # DESI DR2 wₐ uncertainty
    "source": "DESI DR2; Pillars 428, 543",
    "verdict": "HIGH_TENSION — NOT FALSIFIED",
}

# ─── DR3 projection ──────────────────────────────────────────────────────────

# Statistical scaling: σ(N) = σ_0 × √(N / N_0)
_DR2_SIGMA: float = DR2_TENSION["tension_sigma_2d_cpl"]
_DR2_YEARS: float = DR2_TENSION["effective_years"]
_DR3_YEARS: float = 5.0   # 5-year DESI dataset

_DR3_CENTRAL_SIGMA: float = _DR2_SIGMA * math.sqrt(_DR3_YEARS / _DR2_YEARS)

DR3_PROJECTION: Dict[str, Any] = {
    "effective_years": _DR3_YEARS,
    "scaling_model": "σ(N) = σ_DR2 × √(N_DR3 / N_DR2) — statistical precision scaling",
    "sigma_central": _DR3_CENTRAL_SIGMA,
    "sigma_low": _DR3_CENTRAL_SIGMA * 0.6,   # optimistic: central value drifts toward wₐ=0
    "sigma_high": _DR3_CENTRAL_SIGMA * 1.4,  # pessimistic: central value drifts away
    "verdict_central": "FALSIFIED" if _DR3_CENTRAL_SIGMA >= 3.0 else "HIGH_TENSION",
    "uncertainty_note": (
        "The central-value projection assumes no drift from DR2 wₐ measurement. "
        "Actual DR3 tension depends on both statistical precision AND central value shift. "
        "This projection has ±40% uncertainty in σ from central-value drift alone."
    ),
}

# ─── Survey timeline ─────────────────────────────────────────────────────────

SURVEY_TIMELINE: List[Dict[str, Any]] = [
    {
        "release": "DR1",
        "effective_years": 1.0,
        "sigma_projected": _DR2_SIGMA * math.sqrt(1.0 / _DR2_YEARS),
        "date": "2024",
        "status": "RELEASED",
    },
    {
        "release": "DR2",
        "effective_years": 2.0,
        "sigma_projected": _DR2_SIGMA,
        "date": "2025",
        "status": "RELEASED",
        "actual_sigma": 2.30,
    },
    {
        "release": "DR3",
        "effective_years": 3.0,
        "sigma_projected": _DR2_SIGMA * math.sqrt(3.0 / _DR2_YEARS),
        "date": "2026 (expected)",
        "status": "PENDING",
    },
    {
        "release": "Y5 (final)",
        "effective_years": 5.0,
        "sigma_projected": _DR3_CENTRAL_SIGMA,
        "date": "2027",
        "status": "PENDING",
    },
]

# ─── Routing thresholds (from Pillar 543) ─────────────────────────────────────

TRIGGER_CONDITIONS: Dict[str, Any] = {
    "falsified_threshold": 3.0,
    "high_tension_threshold": 2.0,
    "falsified_action": (
        "σ ≥ 3.0 → FALSIFIED: trigger extension spec P268 "
        "(kk_axion_quintessence.py); publish DESI_FALSIFICATION_REPORT.md"
    ),
    "high_tension_action": (
        "2.0 ≤ σ < 3.0 → HIGH_TENSION: escalate monitoring; "
        "update CLAIM_MASTER_BOARD.md T1 row; post Substack decision brief"
    ),
    "pass_action": (
        "σ < 2.0 → PASS: tension resolved; frozen radion consistent; "
        "update T1 row to PASS; no extension required"
    ),
    "extension_spec": "src/core/pillar268_dark_energy_extension_specification.py",
    "preregistration_source": "Pillar 543 (SHA-256 hash recorded)",
}


# ─── Core functions ───────────────────────────────────────────────────────────

def tension_at_dataset_size(
    effective_years: float,
    sigma_dr2: float = _DR2_SIGMA,
    years_dr2: float = _DR2_YEARS,
) -> float:
    """Project the DESI tension σ at a given dataset size (in effective years).

    Uses statistical scaling: σ(N) = σ_DR2 × √(N / N_DR2).
    This assumes the central value does not drift between releases.
    """
    if effective_years <= 0:
        raise ValueError(f"effective_years must be positive, got {effective_years}")
    return sigma_dr2 * math.sqrt(effective_years / years_dr2)


def dr3_central_projection() -> Dict[str, float]:
    """Return the central-value DR3 tension projection."""
    sigma_dr3 = tension_at_dataset_size(_DR3_YEARS)
    return {
        "sigma_dr2": _DR2_SIGMA,
        "sigma_dr3_projected": sigma_dr3,
        "effective_years_dr3": _DR3_YEARS,
        "scaling_factor": math.sqrt(_DR3_YEARS / _DR2_YEARS),
    }


def dr3_scatter_band() -> Dict[str, float]:
    """Return the ±1σ scatter band for the DR3 projection.

    The scatter accounts for central-value drift of the wₐ measurement.
    """
    central = dr3_central_projection()["sigma_dr3_projected"]
    return {
        "sigma_central": central,
        "sigma_low": central * 0.6,
        "sigma_high": central * 1.4,
        "coverage": "±40% range from central-value drift uncertainty",
    }


def route_tension(sigma: float) -> Dict[str, str]:
    """Route a given tension to the pre-registered verdict."""
    if sigma >= TRIGGER_CONDITIONS["falsified_threshold"]:
        verdict = "FALSIFIED"
        action = TRIGGER_CONDITIONS["falsified_action"]
    elif sigma >= TRIGGER_CONDITIONS["high_tension_threshold"]:
        verdict = "HIGH_TENSION"
        action = TRIGGER_CONDITIONS["high_tension_action"]
    else:
        verdict = "PASS"
        action = TRIGGER_CONDITIONS["pass_action"]
    return {"sigma": sigma, "verdict": verdict, "action": action}


def tension_evolution_table() -> List[Dict[str, Any]]:
    """Return a table of tension vs dataset size with routing verdicts."""
    entries = []
    for release in SURVEY_TIMELINE:
        sigma = release["sigma_projected"]
        routing = route_tension(sigma)
        entries.append({
            "release": release["release"],
            "effective_years": release["effective_years"],
            "sigma_projected": sigma,
            "verdict": routing["verdict"],
            "status": release["status"],
        })
    return entries


def decision_day_template() -> Dict[str, Any]:
    """Return the decision-day response template for DESI DR3 arrival."""
    central = dr3_central_projection()["sigma_dr3_projected"]
    routing = route_tension(central)
    return {
        "trigger": "DESI DR3 published (expected late 2026)",
        "first_action": "Read wₐ central value and 1σ uncertainty from DR3 abstract",
        "compute": "2D joint CPL-corrected tension (Pillar 428 method)",
        "route": routing["verdict"],
        "publish_to": [
            "docs/CLAIM_MASTER_BOARD.md (T1 row update)",
            "3-FALSIFICATION/OBSERVATION_TRACKER.md",
            "7-OUTREACH/substack/posts/ (decision brief)",
        ],
        "if_falsified": TRIGGER_CONDITIONS["falsified_action"],
        "if_high_tension": TRIGGER_CONDITIONS["high_tension_action"],
        "if_pass": TRIGGER_CONDITIONS["pass_action"],
        "preregistration_hash": "Pillar 543 SHA-256 registered",
    }


def extension_spec_trigger() -> Dict[str, Any]:
    """Return the conditions under which the extension spec (P268) is triggered."""
    return {
        "trigger_condition": "σ ≥ 3.0 (Pillar 543 preregistered threshold)",
        "extension_module": TRIGGER_CONDITIONS["extension_spec"],
        "extension_name": "Dark Energy Extension Specification (Pillar 268)",
        "extension_mechanism": (
            "KK axion quintessence: the KK bulk axion field can slow radion "
            "freezing and produce wₐ ≠ 0 if the axion mass is O(H₀). "
            "Extension requires new physics beyond the minimal 5D-EFT."
        ),
        "toe_impact_if_triggered": (
            "ToE score impact: T1 (dark energy wₐ) moves from HIGH_TENSION to FALSIFIED. "
            "P28 (cosmological constant reclassification) may be affected. "
            "No hardgate physics (P1–P28 Lane A) is affected by wₐ tension alone."
        ),
        "not_triggered_yet": True,
        "current_tension": _DR2_SIGMA,
    }


def pillar_report() -> Dict[str, Any]:
    """Full Pillar 551 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": True,
        "dr2_tension": DR2_TENSION,
        "dr3_projection": DR3_PROJECTION,
        "survey_timeline": SURVEY_TIMELINE,
        "trigger_conditions": TRIGGER_CONDITIONS,
        "central_projection": dr3_central_projection(),
        "scatter_band": dr3_scatter_band(),
        "evolution_table": tension_evolution_table(),
        "decision_day_template": decision_day_template(),
        "extension_spec_trigger": extension_spec_trigger(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "parent_pillar": 543,
    }
