# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""WS-A Deliverable A1–A3 — 6D c_L Spectrum Audit for Absolute Fermion Masses.

═══════════════════════════════════════════════════════════════════════════
MAS WORKSTREAM: WS-A  (P6 m_u, P7 m_d, P8 m_s, P16 m_e)
Gate criteria: residual < 5 % without anchor
═══════════════════════════════════════════════════════════════════════════

DERIVATION: 6D T²/Z₃ FIXED-POINT c_L SPECTRUM
-----------------------------------------------
The 6D orbifold (Track B Rung 1, Pillar 6D-2) derives the left-handed
bulk mass parameters from fixed-point positions on T²/Z₃:

    c_L^{(i)} = 1/2 + i × (n_w / k_CS),   i ∈ {0, 1, 2}

For (n_w, k_CS) = (5, 74):

    c_L^{(0)} = 0.5000   (IR-critical, Yukawa = 1.0)    → top/tau generation
    c_L^{(1)} = 0.5676   → charm/muon generation
    c_L^{(2)} = 0.6351   → up/electron generation

Yukawa coupling:

    Y^{(i)} = exp(−(c_L^{(i)} − 1/2) × πkR) = exp(−i × 5/74 × 37)

Mass ratios (pure geometry):

    m_gen0 / m_gen1 = exp(5/74 × 37) = exp(2.500) ≈ 12.18
    m_gen0 / m_gen2 = exp(10/74 × 37) = exp(5.000) ≈ 148.41

HONEST GATE REPORT (WS-A Deliverable A3)
-----------------------------------------
PDG ratios (ordering t, c, u in up-type sector):

    m_t / m_c = 172 760 / 1 273 ≈ 135.7   → 6D predicts 12.2   → 1 014 % gap
    m_t / m_u = 172 760 / 2.16 ≈ 79 981   → 6D predicts 148.4  → 53 800 % gap

PDG ratios (ordering τ, μ, e in lepton sector):

    m_τ / m_μ  =  1 776.9 / 105.7 ≈ 16.8  → 6D predicts 12.2   → 38 % gap
    m_τ / m_e  =  1 776.9 / 0.511 ≈ 3 477 → 6D predicts 148.4  → 2 243 % gap

VERDICT: P6, P7, P8, P16 REMAIN FITTED.
  The 6D c_L spectrum with c_L^{(i)} = 1/2 + i × 5/74 provides a
  geometric derivation of the QUALITATIVE hierarchy (exponential suppression
  per generation step, 3 distinct generations) but does NOT achieve < 5 %
  residuals for the absolute fermion masses.

  The < 5 % gate is NOT met.  No status promotion is warranted.

WHAT IS NEWLY DERIVED (genuine progress):
  ✅  The GENERATION STRUCTURE (3 generations, exponential hierarchy) is now
      derived from T²/Z₃ fixed-point geometry rather than ad-hoc c_L fits.
  ✅  The QUALITATIVE ORDERING (heavy → light across fixed points) is
      geometrically predicted.
  ✅  The ANCHOR ELIMINATION shows that c_L itself is no longer a free
      parameter per fermion species; a single geometric formula governs all
      three values per sector.
  ✅  The FAILURE MODE is documented: the simple equally-spaced c_L spectrum
      under-predicts the top/up mass hierarchy by ~5 orders of magnitude.

NEXT STEPS TO CLOSE P6/P7/P8/P16:
  • Include c_R contributions from the same T²/Z₃ fixed-point positions.
  • Include off-diagonal Yukawa corrections from Z₃-breaking perturbations.
  • Derive GW coupling λ_GW from the 5D bulk action (currently open).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    # Constants
    "N_W", "K_CS", "PI_KR",
    "CL_6D",
    "YUKAWA_6D",
    "MASS_RATIO_01", "MASS_RATIO_02", "MASS_RATIO_12",
    "GATE_PASSED",
    "WS_A_STATUS",
    # Functions
    "cl_spectrum_6d",
    "yukawa_6d",
    "mass_ratios_6d",
    "pdg_ratio_comparison",
    "residual_table",
    "anchor_elimination_proof",
    "wsa_gate_report",
    "pillar_wsa_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS  (AxiomZero: derived from {M_Pl, n_w, k_CS} only)
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
PI_KR: float = float(K_CS) / 2.0     # = 37.0

# 6D c_L spectrum: c_L^{(i)} = 1/2 + i × n_w/k_CS
_SPACING: float = float(N_W) / float(K_CS)
CL_6D: Tuple[float, float, float] = (
    0.5,
    0.5 + _SPACING,
    0.5 + 2.0 * _SPACING,
)

# Yukawa couplings from 6D geometry
YUKAWA_6D: Tuple[float, float, float] = tuple(
    1.0 if c <= 0.5 else math.exp(-(c - 0.5) * PI_KR)
    for c in CL_6D
)

# Mass ratios (pure 6D prediction)
MASS_RATIO_01: float = YUKAWA_6D[0] / max(YUKAWA_6D[1], 1e-300)   # m_0 / m_1
MASS_RATIO_02: float = YUKAWA_6D[0] / max(YUKAWA_6D[2], 1e-300)   # m_0 / m_2
MASS_RATIO_12: float = YUKAWA_6D[1] / max(YUKAWA_6D[2], 1e-300)   # m_1 / m_2

# PDG comparison values (comparison only — not inputs)
_M_TOP_MEV: float = 172760.0
_M_CHARM_MEV: float = 1273.0
_M_UP_MEV: float = 2.16
_M_TAU_MEV: float = 1776.9
_M_MUON_MEV: float = 105.7
_M_ELECTRON_MEV: float = 0.511
_M_DOWN_MEV: float = 4.67
_M_STRANGE_MEV: float = 93.4
_M_BOTTOM_MEV: float = 4180.0

# Gate result
GATE_PASSED: bool = False   # < 5 % gate NOT met at this level of derivation
WS_A_STATUS: str = "GEOMETRIC ESTIMATE (large residuals) — P6/P7/P8/P16 remain FITTED"


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def cl_spectrum_6d(n_w: int = N_W, k_cs: int = K_CS) -> Dict[str, object]:
    """Return the 6D c_L spectrum derived from T²/Z₃ fixed-point positions.

    Parameters
    ----------
    n_w : int   Winding number (default 5).
    k_cs : int  Chern-Simons level (default 74).

    Returns
    -------
    dict with c_L values, spacing, and derivation note.
    """
    spacing = float(n_w) / float(k_cs)
    cl_values = [0.5 + i * spacing for i in range(3)]
    return {
        "n_w": n_w,
        "k_cs": k_cs,
        "spacing": spacing,
        "c_L_gen0": cl_values[0],
        "c_L_gen1": cl_values[1],
        "c_L_gen2": cl_values[2],
        "formula": "c_L^{(i)} = 1/2 + i × n_w/k_CS",
        "derivation": (
            "Fixed-point position on T² maps to c_L via the T²/Z₃ lattice metric. "
            "The three fixed points of Z₃ on T² are at z₀=0, z₁=(1+τ)/3, z₂=(2+τ)/3. "
            "The spacing n_w/k_CS = 5/74 comes from the braid winding condition."
        ),
        "axiomzero_compliant": True,
        "inputs": ["M_Pl (through k, R)", "n_w", "k_CS"],
    }


def yukawa_6d(pi_kr: float = PI_KR, n_w: int = N_W, k_cs: int = K_CS) -> Dict[str, object]:
    """Compute the 6D Yukawa couplings from the c_L spectrum.

    Y^{(i)} = exp(-(c_L^{(i)} - 1/2) × πkR)  for c_L > 1/2
    Y^{(0)} = 1.0  (IR-critical generation)

    Parameters
    ----------
    pi_kr : float   πkR compactification parameter.
    n_w   : int     Winding number.
    k_cs  : int     Chern-Simons level.

    Returns
    -------
    dict with Yukawa values and mass ratios.
    """
    spacing = float(n_w) / float(k_cs)
    cl = [0.5 + i * spacing for i in range(3)]
    yukawas = [1.0 if c <= 0.5 else math.exp(-(c - 0.5) * pi_kr) for c in cl]
    r01 = yukawas[0] / max(yukawas[1], 1e-300)
    r02 = yukawas[0] / max(yukawas[2], 1e-300)
    r12 = yukawas[1] / max(yukawas[2], 1e-300)
    return {
        "pi_kr": pi_kr,
        "yukawa_gen0": yukawas[0],
        "yukawa_gen1": yukawas[1],
        "yukawa_gen2": yukawas[2],
        "mass_ratio_01": r01,
        "mass_ratio_02": r02,
        "mass_ratio_12": r12,
        "formula": "Y^{(i)} = exp(-(c_L^{(i)} - 1/2) × πkR)",
        "analytic_01": f"exp({n_w}/{k_cs} × {pi_kr}) = exp({n_w * pi_kr / k_cs:.3f})",
    }


def mass_ratios_6d() -> Dict[str, float]:
    """Return the three mass ratios from 6D geometry.

    Returns
    -------
    dict: ratio_gen0_gen1, ratio_gen0_gen2, ratio_gen1_gen2.
    """
    return {
        "ratio_gen0_gen1": MASS_RATIO_01,
        "ratio_gen0_gen2": MASS_RATIO_02,
        "ratio_gen1_gen2": MASS_RATIO_12,
        "analytic": {
            "01": f"exp(5/74 × 37) = exp(2.5) ≈ {MASS_RATIO_01:.3f}",
            "02": f"exp(10/74 × 37) = exp(5.0) ≈ {MASS_RATIO_02:.3f}",
            "12": f"same as 01 (equal spacing)",
        },
    }


def pdg_ratio_comparison() -> List[Dict[str, object]]:
    """Compare 6D mass ratios to PDG observations.

    Returns
    -------
    list of dicts with PDG sector, ratio, 6D prediction, and pct_err.
    """
    entries = [
        {
            "sector": "up-type quarks (t/c)",
            "heavy": "m_t",
            "light": "m_c",
            "pdg_ratio": _M_TOP_MEV / _M_CHARM_MEV,
            "six_d_prediction": MASS_RATIO_01,
            "pct_err": abs(_M_TOP_MEV / _M_CHARM_MEV - MASS_RATIO_01)
                       / (_M_TOP_MEV / _M_CHARM_MEV) * 100.0,
        },
        {
            "sector": "up-type quarks (t/u)",
            "heavy": "m_t",
            "light": "m_u",
            "pdg_ratio": _M_TOP_MEV / _M_UP_MEV,
            "six_d_prediction": MASS_RATIO_02,
            "pct_err": abs(_M_TOP_MEV / _M_UP_MEV - MASS_RATIO_02)
                       / (_M_TOP_MEV / _M_UP_MEV) * 100.0,
        },
        {
            "sector": "charged leptons (τ/μ)",
            "heavy": "m_τ",
            "light": "m_μ",
            "pdg_ratio": _M_TAU_MEV / _M_MUON_MEV,
            "six_d_prediction": MASS_RATIO_01,
            "pct_err": abs(_M_TAU_MEV / _M_MUON_MEV - MASS_RATIO_01)
                       / (_M_TAU_MEV / _M_MUON_MEV) * 100.0,
        },
        {
            "sector": "charged leptons (τ/e)",
            "heavy": "m_τ",
            "light": "m_e",
            "pdg_ratio": _M_TAU_MEV / _M_ELECTRON_MEV,
            "six_d_prediction": MASS_RATIO_02,
            "pct_err": abs(_M_TAU_MEV / _M_ELECTRON_MEV - MASS_RATIO_02)
                       / (_M_TAU_MEV / _M_ELECTRON_MEV) * 100.0,
        },
        {
            "sector": "down-type quarks (b/s)",
            "heavy": "m_b",
            "light": "m_s",
            "pdg_ratio": _M_BOTTOM_MEV / _M_STRANGE_MEV,
            "six_d_prediction": MASS_RATIO_01,
            "pct_err": abs(_M_BOTTOM_MEV / _M_STRANGE_MEV - MASS_RATIO_01)
                       / (_M_BOTTOM_MEV / _M_STRANGE_MEV) * 100.0,
        },
        {
            "sector": "down-type quarks (b/d)",
            "heavy": "m_b",
            "light": "m_d",
            "pdg_ratio": _M_BOTTOM_MEV / _M_DOWN_MEV,
            "six_d_prediction": MASS_RATIO_02,
            "pct_err": abs(_M_BOTTOM_MEV / _M_DOWN_MEV - MASS_RATIO_02)
                       / (_M_BOTTOM_MEV / _M_DOWN_MEV) * 100.0,
        },
    ]
    return entries


def residual_table() -> Dict[str, object]:
    """Return the WS-A Deliverable A3 residual table.

    This is the hard-gate evidence artifact for the MAS W1 ledger.

    Returns
    -------
    dict with per-sector residuals, gate_passed flag, and verdict.
    """
    rows = pdg_ratio_comparison()
    all_lt5 = all(row["pct_err"] < 5.0 for row in rows)
    max_err = max(row["pct_err"] for row in rows)
    min_err = min(row["pct_err"] for row in rows)
    return {
        "deliverable": "WS-A / A3 — PDG residual table",
        "rows": rows,
        "gate_target_pct": 5.0,
        "gate_passed": all_lt5,
        "max_residual_pct": max_err,
        "min_residual_pct": min_err,
        "verdict": (
            "GATE FAILED — large residuals in all sectors.  "
            "6D c_L = 1/2 + i×5/74 gives inter-generation ratio "
            f"= exp(2.5) ≈ {MASS_RATIO_01:.1f}, "
            "but PDG values require per-sector ratios of O(10²–10⁵).  "
            "P6/P7/P8/P16 remain FITTED.  "
            "No status promotion warranted from this artifact alone."
        ),
        "what_is_newly_achieved": [
            "c_L spectrum derived from 6D geometry (not fitted per species)",
            "Qualitative 3-generation hierarchy confirmed geometrically",
            "Anchor-elimination theorem: one overall Yukawa scale per sector",
            "Failure mode documented: simple fixed-point c_L under-predicts hierarchy",
        ],
    }


def anchor_elimination_proof() -> Dict[str, object]:
    """Return the anchor-elimination proof for WS-A Deliverable A2.

    Shows that the 6D c_L spectrum reduces the number of free parameters
    from 9 (one c_L per fermion species) to 2 (one Yukawa scale per sector)
    plus the overall 6D-derived c_L formula.

    Returns
    -------
    dict with before/after free parameter count and epistemic assessment.
    """
    return {
        "deliverable": "WS-A / A2 — Anchor-elimination proof",
        "before_6d": {
            "free_params": 9,
            "description": (
                "Before 6D: each of the 9 fermion species "
                "(u, d, s, c, b, t, e, μ, τ) had an independent c_L value.  "
                "These 9 values were fitted to PDG mass data — no derivation."
            ),
        },
        "after_6d": {
            "free_params": 2,
            "description": (
                "After 6D: c_L^{(i)} = 1/2 + i × n_w/k_CS — single formula.  "
                "Remaining free parameters: (1) overall Yukawa scale for the "
                "quark sector Y_q, (2) overall Yukawa scale for the lepton "
                "sector Y_l.  Both are fixed by ONE reference mass per sector "
                "(e.g. m_t fixes Y_q, m_τ fixes Y_l)."
            ),
        },
        "reduction": 9 - 2,
        "epistemic_status": (
            "PARTIAL ANCHOR ELIMINATION: free parameters 9 → 2 within a sector.  "
            "However, the surviving 2 free parameters (Y_q, Y_l) introduce a "
            "hidden anchor per sector.  For FULL closure, Y_q and Y_l must be "
            "derived from the GW potential + 5D bulk geometry.  "
            "This remains open at the 5D level."
        ),
        "gate_verdict": (
            "Deliverable A2 PARTIALLY SATISFIED: the c_L spectrum is derived.  "
            "Full anchor elimination requires Y_q and Y_l from GW geometry — "
            "not yet achieved.  No status promotion for P6/P7/P8/P16."
        ),
    }


def wsa_gate_report() -> Dict[str, object]:
    """Consolidated WS-A gate evidence report (A1 + A2 + A3).

    Returns
    -------
    dict for attachment to MAS W1 ledger.
    """
    cl_spec = cl_spectrum_6d()
    yuk = yukawa_6d()
    elim = anchor_elimination_proof()
    resid = residual_table()
    return {
        "workstream": "WS-A",
        "parameters": ["P6 (m_u)", "P7 (m_d)", "P8 (m_s)", "P16 (m_e)"],
        "deliverable_A1_cl_spectrum": cl_spec,
        "deliverable_A2_anchor_elimination": elim,
        "deliverable_A3_residual_table": resid,
        "yukawa_summary": yuk,
        "gate_passed": resid["gate_passed"],
        "status_change": "NONE — P6/P7/P8/P16 remain FITTED",
        "honest_status_after_wsa": "FITTED (partial geometric derivation; c_L from 6D but Yukawa scale open)",
        "next_step": (
            "Derive overall Yukawa scale Y_q, Y_l from GW bulk coupling λ_GW + "
            "M_Pl.  Until then, one anchor per sector persists."
        ),
    }


def pillar_wsa_summary() -> Dict[str, object]:
    """Return a brief WS-A summary for the MAS ledger."""
    return {
        "workstream": "WS-A",
        "pillar": "6D-2 (extension)",
        "parameters": "P6, P7, P8, P16",
        "gate_passed": GATE_PASSED,
        "status": WS_A_STATUS,
        "c_L_spectrum_derived": True,
        "yukawa_scale_derived": False,
        "mass_ratios_match_pdg": False,
        "max_residual_pct": max(row["pct_err"] for row in pdg_ratio_comparison()),
        "rung_impact": (
            "6D geometry derives the generation structure and c_L spectrum.  "
            "Yukawa scale remains open.  Parameters stay FITTED."
        ),
    }
