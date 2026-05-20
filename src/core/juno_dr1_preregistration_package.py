# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""JUNO DR1 Preregistration Package — Δm²₃₁ same-day routing for JUNO Data Release 1 (~2027).

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This module formally preregisters the Unitary Manifold's prediction for the
JUNO neutrino oscillation experiment Data Release 1 (~2027), modeled after
the DESI DR3 publication-day runbook pattern.

JUNO DR1 context:
- JUNO measures Δm²₃₁ to ~0.5% precision (σ ≈ 0.5% × 2.453e-3 eV² ≈ 1.2e-5 eV²)
- Planned data release: ~2027
- This is the key near-term falsifier for P17 (Δm²₃₁ derivation status)

UM Δm²₃₁ prediction chain:
1. Baseline (Pillar 255):                   2.400 × 10⁻³ eV²  (2.16% below PDG)
2. + NLO RGE running (Pillar 274):          closes to 2.452 × 10⁻³ eV² (0.04% residual)
3. + Seesaw texture (Pillar 286):           minimal additional shift; residual < 0.1%

Preregistered UM prediction: Δm²₃₁ = 2.452 × 10⁻³ eV² (NLO-tightened)
PDG 2024 central value:       Δm²₃₁ = 2.453 × 10⁻³ eV²

Routing logic:
  |measured - 2.452e-3| / 2.452e-3 < 1%   → JUNO_CONSISTENT (P17 strengthened)
  |measured - 2.452e-3| / 2.452e-3 ∈ [1%, 3%)  → JUNO_TENSION (log, review)
  |measured - 2.452e-3| / 2.452e-3 ≥ 3%   → JUNO_FALSIFIED (P17 falsified; M_R revision required)
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "UM_DM31_NLO_EV2",
    "UM_DM31_BASELINE_EV2",
    "DM31_PDG_EV2",
    "JUNO_PRECISION_TARGET",
    "TENSION_THRESHOLD_PCT",
    "FALSIFIED_THRESHOLD_PCT",
    "DOCS_TO_UPDATE",
    "separation_guard",
    "um_dm31_prediction",
    "juno_dr1_routing",
    "juno_dr1_readiness_checklist",
    "juno_dr1_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 274   # preregistration augments the JUNO monitoring pillar

# UM predictions
UM_DM31_BASELINE_EV2: float = 2.400e-3   # Pillar 255 baseline (unfitted)
UM_DM31_NLO_EV2: float = 2.452e-3        # Pillar 274 NLO-tightened (preregistered)

# PDG reference
DM31_PDG_EV2: float = 2.453e-3

# JUNO precision
JUNO_PRECISION_TARGET: float = 0.005   # 0.5% fractional uncertainty

# Routing thresholds (fractional)
TENSION_THRESHOLD_PCT: float = 1.0     # 1% fractional → TENSION
FALSIFIED_THRESHOLD_PCT: float = 3.0   # 3% fractional → FALSIFIED

DOCS_TO_UPDATE: List[str] = [
    "docs/CLAIM_MASTER_BOARD.md",
    "FALLIBILITY.md",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "docs/WAVE_CHANGELOG.md",
    "STATUS.md",
]


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for JUNO DR1 preregistration."""
    return {
        "pillar": PILLAR_NUMBER,
        "module": "juno_dr1_preregistration_package",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "preregistration": True,
        "target_experiment": "JUNO",
        "expected_dr1_year": 2027,
    }


def um_dm31_prediction() -> Dict[str, object]:
    """Return the UM Δm²₃₁ prediction chain."""
    baseline_residual_pct = abs(UM_DM31_BASELINE_EV2 - DM31_PDG_EV2) / DM31_PDG_EV2 * 100.0
    nlo_residual_pct = abs(UM_DM31_NLO_EV2 - DM31_PDG_EV2) / DM31_PDG_EV2 * 100.0
    return {
        "baseline_ev2": UM_DM31_BASELINE_EV2,
        "nlo_tightened_ev2": UM_DM31_NLO_EV2,
        "pdg_2024_ev2": DM31_PDG_EV2,
        "baseline_residual_pct": baseline_residual_pct,
        "nlo_residual_pct": nlo_residual_pct,
        "preregistered_prediction_ev2": UM_DM31_NLO_EV2,
        "juno_sigma_ev2": JUNO_PRECISION_TARGET * UM_DM31_NLO_EV2,
        "projected_juno_sigma_pulls": nlo_residual_pct / (JUNO_PRECISION_TARGET * 100.0),
    }


def juno_dr1_routing(
    measured_dm31_ev2: float,
    measured_sigma_ev2: float,
) -> Dict[str, object]:
    """Route a JUNO DR1 Δm²₃₁ measurement to a verdict.

    Parameters
    ----------
    measured_dm31_ev2 : float
        Measured Δm²₃₁ in eV² from JUNO DR1.
    measured_sigma_ev2 : float
        1σ experimental uncertainty in eV².
    """
    if measured_dm31_ev2 <= 0.0:
        raise ValueError("measured_dm31_ev2 must be positive")
    if measured_sigma_ev2 <= 0.0:
        raise ValueError("measured_sigma_ev2 must be positive")

    residual_ev2 = measured_dm31_ev2 - UM_DM31_NLO_EV2
    residual_pct = abs(residual_ev2) / UM_DM31_NLO_EV2 * 100.0
    sigma_pull = abs(residual_ev2) / measured_sigma_ev2

    if residual_pct < TENSION_THRESHOLD_PCT:
        verdict = "JUNO_CONSISTENT"
        action = "P17 CONDITIONAL_DERIVATION strengthened; log to OBSERVATION_TRACKER"
    elif residual_pct < FALSIFIED_THRESHOLD_PCT:
        verdict = "JUNO_TENSION"
        action = "Flag in CLAIM_MASTER_BOARD; review NLO chain; escalate if sigma_pull > 3"
    else:
        verdict = "JUNO_FALSIFIED"
        action = "P17 falsified; M_R revision required; update FALLIBILITY.md immediately"

    return {
        "measured_dm31_ev2": measured_dm31_ev2,
        "measured_sigma_ev2": measured_sigma_ev2,
        "um_prediction_ev2": UM_DM31_NLO_EV2,
        "residual_ev2": residual_ev2,
        "residual_pct": residual_pct,
        "sigma_pull": sigma_pull,
        "verdict": verdict,
        "action_required": action,
        "docs_to_update": DOCS_TO_UPDATE if verdict != "JUNO_CONSISTENT" else DOCS_TO_UPDATE[:3],
    }


def juno_dr1_readiness_checklist() -> List[Dict[str, object]]:
    """Return the same-day readiness checklist for JUNO DR1."""
    nlo_residual = abs(UM_DM31_NLO_EV2 - DM31_PDG_EV2) / DM31_PDG_EV2 * 100.0
    return [
        {
            "item": "UM prediction locked",
            "status": "COMPLETE",
            "value": f"Δm²₃₁ = {UM_DM31_NLO_EV2:.4e} eV² (NLO-tightened)",
            "reference": "pillar274_juno_dm31_tightening.py, pillar286_kk_seesaw_texture_diagonalization.py",
        },
        {
            "item": "Routing thresholds preregistered",
            "status": "COMPLETE",
            "value": f"TENSION at {TENSION_THRESHOLD_PCT}%; FALSIFIED at {FALSIFIED_THRESHOLD_PCT}%",
            "reference": "juno_dr1_preregistration_package.py (this module)",
        },
        {
            "item": "Current NLO residual vs PDG",
            "status": "MONITORED",
            "value": f"{nlo_residual:.4f}% (target: < {TENSION_THRESHOLD_PCT}%)",
            "reference": "pillar274_juno_dm31_tightening.py",
        },
        {
            "item": "Docs-to-update list prepared",
            "status": "COMPLETE",
            "value": str(DOCS_TO_UPDATE),
            "reference": "juno_dr1_preregistration_package.py",
        },
        {
            "item": "Routing function tested",
            "status": "COMPLETE",
            "value": "juno_dr1_routing() tested in test_juno_dr1_preregistration_package.py",
            "reference": "tests/test_juno_dr1_preregistration_package.py",
        },
        {
            "item": "JUNO DR1 expected release",
            "status": "MONITORING",
            "value": "~2027",
            "reference": "JUNO Collaboration public timeline",
        },
    ]


def juno_dr1_preregistration_report() -> Dict[str, object]:
    """Full JUNO DR1 preregistration report."""
    return {
        "module": "juno_dr1_preregistration_package",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "prediction_chain": um_dm31_prediction(),
        "routing_example_consistent": juno_dr1_routing(UM_DM31_NLO_EV2, JUNO_PRECISION_TARGET * UM_DM31_NLO_EV2),
        "routing_example_falsified": juno_dr1_routing(2.525e-3, 1.23e-5),
        "readiness_checklist": juno_dr1_readiness_checklist(),
        "status": "PREREGISTRATION_LOCKED",
    }
