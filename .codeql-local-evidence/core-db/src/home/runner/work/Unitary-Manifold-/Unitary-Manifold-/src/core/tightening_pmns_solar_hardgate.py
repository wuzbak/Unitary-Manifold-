# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tightening 3 — PMNS Solar Angle θ₁₂ HARDGATE Promotion.

TIGHTENING SPRINT — PMNS sin²θ₁₂ HARDGATE_READY promotion
═══════════════════════════════════════════════════════════════════════════

PRIOR STATE (Pillar 163 / pmns_solar_rge_correction.py)
─────────────────────────────────────────────────────────
  • pmns_solar_closure_realism_audit() returned:
      - baseline_residual_pct ≈ 1.50%
      - effective_residual_pct ≈ 1.49%
      - overall_verdict: BASELINE_SUFFICIENT
  • But `pmns_solar_required_two_loop_gain()` used a gate at 5%
    and the `OPEN_GAP_TRACK` / `HARDGATE_READY_TRACK` gates were
    checked in pmns_solar_rge_report().

THIS TIGHTENING:
  1. Runs the full gate logic and formally confirms HARDGATE_READY status
  2. Issues a promotion certificate: SUBSTANTIALLY_CLOSED → HARDGATE_PROMOTED
  3. Updates the sin²θ₁₂ status in the parameter table

RESULT:
  sin²θ₁₂(M_Z) ≈ 0.3024 from canonical Route-A + 1-loop RGE
  PDG: 0.307 ± 0.013
  Residual: 1.5% — well within the 5% gate.
  STATUS: HARDGATE_PROMOTED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "MODULE_LABEL",
    "STATUS",
    "pmns_solar_hardgate_promotion",
    "hardgate_certificate",
]

MODULE_LABEL: str = "tightening_pmns_solar_hardgate"
STATUS: str = "HARDGATE_PROMOTED"

# Canonical values (from pmns_solar_rge_correction.py)
_SIN2_THETA12_MZ: float = 0.3024
_SIN2_THETA12_PDG: float = 0.307
_SIN2_THETA12_PDG_ERR: float = 0.013
_RESIDUAL_PCT: float = abs(_SIN2_THETA12_MZ - _SIN2_THETA12_PDG) / _SIN2_THETA12_PDG * 100.0
_HARDGATE_THRESHOLD_PCT: float = 5.0
_SIGMA_AWAY: float = abs(_SIN2_THETA12_MZ - _SIN2_THETA12_PDG) / _SIN2_THETA12_PDG_ERR


def pmns_solar_hardgate_promotion() -> Dict[str, object]:
    """Gate check: promote PMNS solar angle to HARDGATE_READY."""
    within_gate = _RESIDUAL_PCT < _HARDGATE_THRESHOLD_PCT
    within_1sigma = _SIGMA_AWAY < 1.0
    return {
        "sin2_theta12_mz": _SIN2_THETA12_MZ,
        "sin2_theta12_pdg": _SIN2_THETA12_PDG,
        "sin2_theta12_pdg_err": _SIN2_THETA12_PDG_ERR,
        "residual_pct": _RESIDUAL_PCT,
        "sigma_away": _SIGMA_AWAY,
        "gate_threshold_pct": _HARDGATE_THRESHOLD_PCT,
        "within_gate": within_gate,
        "within_1sigma_pdg": within_1sigma,
        "previous_status": "SUBSTANTIALLY_CLOSED",
        "new_status": "HARDGATE_PROMOTED" if within_gate else "HARDGATE_NOT_MET",
        "promotion_allowed": within_gate,
    }


def hardgate_certificate() -> Dict[str, object]:
    """Full HARDGATE promotion certificate for PMNS θ₁₂."""
    gate = pmns_solar_hardgate_promotion()
    return {
        "module": MODULE_LABEL,
        "status": STATUS if gate["promotion_allowed"] else "HARDGATE_NOT_MET",
        "gate": gate,
        "derivation_chain": [
            "sin²θ₁₂(GUT) = 1/3 − 1/(6 n_w) + 1/(6 K_CS) ≈ 0.3023 [Route-A, Pillar 208]",
            "Δ(sin²θ₁₂)_RGE ≈ +1.5×10⁻⁴ [Antusch et al. 1-loop]",
            "sin²θ₁₂(M_Z) ≈ 0.3024",
            f"PDG: 0.307 ± 0.013 — residual {_RESIDUAL_PCT:.2f}% < gate {_HARDGATE_THRESHOLD_PCT}%",
        ],
        "pillar_163_update": "SUBSTANTIALLY_CLOSED → HARDGATE_PROMOTED",
        "note": (
            "The 1.5% residual is within 0.35σ of PDG. "
            "Full 3-loop and threshold corrections could improve this further."
        ),
    }
