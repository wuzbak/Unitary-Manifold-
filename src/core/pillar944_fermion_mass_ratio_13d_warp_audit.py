# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 944 — Fermion Mass Ratio 13D Orbifold Warp Audit (Sprint BG).

🔵 ADJACENT TRACK — Non-hardgate.

═══════════════════════════════════════════════════════════════════════════
THE GAP THIS ADDRESSES
═══════════════════════════════════════════════════════════════════════════

Sprint BC (P898–P899) registered FERMION_MASS_RATIO_OPEN:
  - Quark mass ratios from FN+warp: severe overshoot (O(10²) off for lighter quarks)
  - Charged lepton ratios: tension retained
  - Root cause: 7D warp factor ε = exp(-2.5) ≈ 0.082 is too large to generate
    the observed m_e/m_τ ≈ 2.9×10⁻⁴ suppression without additional structure.

This pillar attempts the 13D orbifold extension:
  - In 13D, each generation gets a separate T²/Z₂ fixed-point sector
  - The warp factor is generation-indexed: ε_i = exp(-π n_w R_i / R₀)
  - With n_w=5 and R_i/R₀ ∈ {1, 2, 3} for the three generations,
    the generation-indexed warp produces: ε₁, ε₂ = ε₁², ε₃ = ε₁³

HONEST OUTCOME
──────────────
  FERMION_MASS_RATIO_13D_PARTIAL  — generation-indexed warp partially
    improves quark hierarchy; lepton hierarchy tension remains.
  FERMION_MASS_RATIO_13D_IRREDUCIBLE  — warp alone insufficient; additional
    mechanism (e.g. mixing with KK modes, higher-dimensional operators) needed.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "WARP_FACTORS",
    "QUARK_MASS_RATIOS_PDG",
    "QUARK_MASS_RATIOS_13D",
    "LEPTON_MASS_RATIOS_PDG",
    "LEPTON_MASS_RATIOS_13D",
    "QUARK_RATIO_RESIDUALS",
    "LEPTON_RATIO_RESIDUALS",
    "fermion_mass_ratio_13d_summary",
]

PILLAR_NUMBER: int = 944
PILLAR_GATE: str = "FERMION_MASS_RATIO_13D_ORBIFOLD_WARP_AUDIT"

# ── 13D generation-indexed warp factors ──────────────────────────────────────
_N_W: int = 5
_PI: float = math.pi
# R_i / R_0 = i for i = 1, 2, 3 (three generations at distinct fixed points)
# ε_i = exp(-π n_w R_i / R_0) = exp(-π * 5 * i) for winding geometry
# This is an ansatz for the 13D inter-generation hierarchy; the precise radii
# are architecture-dependent but n_w=5 is fixed.
WARP_FACTORS: Dict[str, float] = {
    "gen1": math.exp(-_PI * _N_W * 1),   # ε₁ ≈ 7.1e-8
    "gen2": math.exp(-_PI * _N_W * 2),   # ε₂ ≈ 5.1e-15
    "gen3": math.exp(-_PI * _N_W * 3),   # ε₃ ≈ 3.6e-22
}

# ── Observed PDG mass ratios (dimensionless) ─────────────────────────────────
# Quarks: m_u/m_t, m_d/m_b, m_s/m_b (running masses at M_Z, approximate)
QUARK_MASS_RATIOS_PDG: Dict[str, float] = {
    "m_u_over_m_t": 2.2e-3 / 172.5,       # ≈ 1.28e-5
    "m_d_over_m_b": 4.7e-3 / 4.18,        # ≈ 1.12e-3
    "m_s_over_m_b": 96e-3 / 4.18,         # ≈ 2.30e-2
}

# Leptons: m_e/m_tau, m_mu/m_tau
LEPTON_MASS_RATIOS_PDG: Dict[str, float] = {
    "m_e_over_m_tau":  0.511e-3 / 1776.86e-3,    # ≈ 2.88e-4
    "m_mu_over_m_tau": 105.66e-3 / 1776.86e-3,   # ≈ 5.95e-2
}

# ── 13D prediction: mass ratios from generation-indexed warp ─────────────────
# Yukawa coupling y_i ∝ ε_i (overlap of zero-mode wavefunctions at fixed points)
# Mass ratio m_i / m_j = y_i / y_j = ε_i / ε_j = exp(-π n_w (R_i - R_j) / R_0)
# Quark mass ratios (up-type):
#   m_u / m_t ≈ ε₁ / ε₃ factor times t-quark mass normalization
# Honest comparison: take m_top ∼ ε₃ normalized to 1, m_charm ∼ ε₂, m_up ∼ ε₁
_eps1: float = WARP_FACTORS["gen1"]
_eps2: float = WARP_FACTORS["gen2"]
_eps3: float = WARP_FACTORS["gen3"]

QUARK_MASS_RATIOS_13D: Dict[str, float] = {
    "m_u_over_m_t": _eps1 / _eps3,   # = exp(+π*5*2) = exp(10π) ≈ huge — INVERTED
    "m_d_over_m_b": _eps1 / _eps3,   # same structure for down-type
    "m_s_over_m_b": _eps2 / _eps3,   # = exp(+π*5*1) = exp(5π)
}
# Note: ε₁ / ε₃ = exp(-π*5*(1-3)) = exp(+10π) >> 1 — this is WRONG because
# the 3rd generation is the HEAVIEST and should have the LARGEST warp.
# The correct assignment is: m_top ∼ ε₁ (gen1 is heaviest at smallest R),
# m_charm ∼ ε₂, m_up ∼ ε₃.  Ratio m_u/m_t = ε₃/ε₁ = exp(-10π) ≈ 1.4e-14.
QUARK_MASS_RATIOS_13D = {
    "m_u_over_m_t": _eps3 / _eps1,   # = exp(-π*5*2) ≈ 5.1e-15 / 7.1e-8 ≈ 7.2e-8
    "m_d_over_m_b": _eps3 / _eps1,
    "m_s_over_m_b": _eps2 / _eps1,   # = exp(-π*5*1) ≈ 5.1e-15 / 7.1e-8 ≈ 7.2e-8
}
# Recompute with correct ratio:
_ratio_eps31: float = _eps3 / _eps1   # exp(-10π) ≈ 7.2e-8 ... but exp(-10π) = exp(-31.4) ≈ 2.4e-14
_ratio_eps21: float = _eps2 / _eps1   # exp(-5π) ≈ exp(-15.7) ≈ 1.5e-7
QUARK_MASS_RATIOS_13D = {
    "m_u_over_m_t": _ratio_eps31,   # 13D prediction ≈ 2.4e-14 vs PDG 1.28e-5
    "m_d_over_m_b": _ratio_eps31,
    "m_s_over_m_b": _ratio_eps21,   # 13D prediction ≈ 1.5e-7 vs PDG 2.30e-2
}

LEPTON_MASS_RATIOS_13D: Dict[str, float] = {
    "m_e_over_m_tau":  _ratio_eps31,  # same warp hierarchy
    "m_mu_over_m_tau": _ratio_eps21,
}

# ── Fractional residuals (log-ratio scale for mass hierarchies) ───────────────
def _log_residual(pred: float, obs: float) -> float:
    """Log-ratio residual |log10(pred/obs)|."""
    if pred <= 0 or obs <= 0:
        return float("inf")
    return abs(math.log10(pred / obs))

QUARK_RATIO_RESIDUALS: Dict[str, float] = {
    k: _log_residual(QUARK_MASS_RATIOS_13D[k], QUARK_MASS_RATIOS_PDG[k])
    for k in QUARK_MASS_RATIOS_PDG
}

LEPTON_RATIO_RESIDUALS: Dict[str, float] = {
    k: _log_residual(LEPTON_MASS_RATIOS_13D[k], LEPTON_MASS_RATIOS_PDG[k])
    for k in LEPTON_MASS_RATIOS_PDG
}

# ── Honest verdict ──────────────────────────────────────────────────────────
# "within 2 decades" as the pass threshold (log residual < 2)
_Q_PASS: int = sum(1 for v in QUARK_RATIO_RESIDUALS.values() if v < 2.0)
_L_PASS: int = sum(1 for v in LEPTON_RATIO_RESIDUALS.values() if v < 2.0)
_TOTAL_PASS: int = _Q_PASS + _L_PASS
_TOTAL: int = len(QUARK_RATIO_RESIDUALS) + len(LEPTON_RATIO_RESIDUALS)

if _TOTAL_PASS == _TOTAL:
    PILLAR_STATUS: str = "FERMION_MASS_RATIO_13D_CLOSED"
elif _TOTAL_PASS >= _TOTAL // 2:
    PILLAR_STATUS = "FERMION_MASS_RATIO_13D_PARTIAL"
else:
    PILLAR_STATUS = "FERMION_MASS_RATIO_13D_IRREDUCIBLE"

PILLAR_VALID: bool = True

_REMAINING: str = (
    f"13D generation-indexed warp: {_TOTAL_PASS}/{_TOTAL} ratios within 2 decades of PDG. "
    f"Quark: {_Q_PASS}/{len(QUARK_RATIO_RESIDUALS)} pass. "
    f"Lepton: {_L_PASS}/{len(LEPTON_RATIO_RESIDUALS)} pass. "
    "The warp ansatz generates inter-generation suppression exp(-π n_w ΔR/R₀); "
    "the precise R_i values are architecture-dependent (not uniquely fixed by n_w=5). "
    "FERMION_MASS_RATIO remains open as an architecture residual requiring UV completion."
)


def fermion_mass_ratio_13d_summary() -> Dict[str, Any]:
    """Return the Sprint BG fermion mass ratio 13D audit summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "warp_factors": WARP_FACTORS,
        "quark_ratios_pdg": QUARK_MASS_RATIOS_PDG,
        "quark_ratios_13d": QUARK_MASS_RATIOS_13D,
        "lepton_ratios_pdg": LEPTON_MASS_RATIOS_PDG,
        "lepton_ratios_13d": LEPTON_MASS_RATIOS_13D,
        "quark_log_residuals": QUARK_RATIO_RESIDUALS,
        "lepton_log_residuals": LEPTON_RATIO_RESIDUALS,
        "n_pass": _TOTAL_PASS,
        "n_total": _TOTAL,
        "remaining": _REMAINING,
    }
