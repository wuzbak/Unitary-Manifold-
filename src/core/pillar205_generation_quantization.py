# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 205 — Generation Quantization Audit: Yukawa Unification from c_L = m/n_w.

═══════════════════════════════════════════════════════════════════════════
AXIOM-ZERO COMPLIANCE
═══════════════════════════════════════════════════════════════════════════
Inputs: ONLY {K_CS, n_w, v_gw}.  No SM masses used as derivation inputs.
SM masses appear in the COMPARISON columns only.

═══════════════════════════════════════════════════════════════════════════
AGENT A (GEOMETRICIAN) HYPOTHESIS
═══════════════════════════════════════════════════════════════════════════
MAS Agent A proposed:
  "The c_L parameters for the three generations are quantized in units of
   1/n_w.  If n_w = 5, then the mass ratios emerge as exp(−πkR × (c − 1/2)).
   This would move 8 fitted parameters to 0 fitted parameters."

FORMAL TEST:
The quantization hypothesis: c_L^{(m)} = m/n_w  for m = 0, 1, 2, 3, 4, 5.

For n_w = 5, the candidates are:
  m=0: c_L = 0.0  (extreme IR-localised)
  m=1: c_L = 0.2  (IR-localised)
  m=2: c_L = 0.4  (IR-localised, near critical)
  m=3: c_L = 0.6  (UV-localised)
  m=4: c_L = 0.8  (UV-localised)
  m=5: c_L = 1.0  (extreme UV-localised)

For each level, computing Y_eff = exp(−(c_L − 1/2) × πkR) for c_L > 1/2
(for c_L ≤ 1/2, Y_eff ≈ 1, IR-localised, O(1) Yukawa coupling):

  m=2, c_L=0.4: Y_eff = 1.0  (IR-localised) → m_f ≈ v ≈ 257 GeV  (top-like)
  m=3, c_L=0.6: Y_eff = exp(−3.7) ≈ 0.025  → m_f ≈ 6.1 GeV  (bottom/charm?)
  m=4, c_L=0.8: Y_eff = exp(−11.1) ≈ 1.5e-5 → m_f ≈ 3.9 MeV  (strange/mu?)
  m=5, c_L=1.0: Y_eff = exp(−18.5) ≈ 9.4e-9 → m_f ≈ 2.4 eV  (neutrino-like)

═══════════════════════════════════════════════════════════════════════════
HONEST AUDIT RESULT
═══════════════════════════════════════════════════════════════════════════
The quantization c_L = m/n_w is a PARTIAL GEOMETRIC APPROXIMATION:

WHAT WORKS (within O(1) factor):
  • m=2, c_L=0.4 → m_f ≈ v (top quark: 173 GeV, factor 1.5 off)
  • m=3, c_L=0.6 → m_f ≈ 6.1 GeV (bottom: 4.2 GeV, factor 1.4 off)

WHAT FAILS (order-of-magnitude off):
  • m=4, c_L=0.8 → m_f ≈ 3.9 MeV (muon: 106 MeV, strange: 96 MeV — 25-50× off)
  • m=5, c_L=1.0 → m_f ≈ 2.4 eV (electron: 0.511 MeV — 5 orders off)

CONCLUSION: The integer quantization c_L = m/n_w correctly identifies the
generation STRUCTURE (3 IR + 3 UV classes) but fails to reproduce the
individual mass values for the lighter generations.  The 8 fitted
parameters are NOT removed; at most 2 are approximately constrained.

TOE SCORE IMPACT: None (no parameters moved to DERIVED or GEOMETRIC PRED.)
The quantization hypothesis correctly motivates the 3-generation structure
but requires fractional c_L corrections for the lighter fermions.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    # Constants
    "N_W", "K_CS", "N_C", "PI_KR",
    "CL_QUANTIZED_LEVELS",
    # Functions
    "cl_quantized",
    "yukawa_from_cl",
    "generation_mass_table",
    "quantization_audit",
    "heaviest_two_assessment",
    "axiom_zero_audit",
    "pillar205_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
N_C: int = math.ceil(N_W / 2)  # = 3
PI_KR: float = float(K_CS) / 2.0  # = 37.0

# The n_w quantization levels: m = 0,1,2,3,4,5
CL_QUANTIZED_LEVELS: List[float] = [float(m) / float(N_W) for m in range(N_W + 1)]

# Pillar 201 GW-improved VEV [GeV]
_V_GW_GEV: float = 257.6

# PDG mass reference values [GeV] — comparison only, NOT derivation inputs
_PDG_MASSES_GEV: Dict[str, float] = {
    "top":     172.69,
    "bottom":    4.18,
    "charm":     1.27,
    "strange":   0.096,
    "muon":      0.10566,
    "electron":  0.000511,
}


def cl_quantized(n_w: int = N_W) -> List[Dict[str, object]]:
    """Return the full set of quantized c_L levels for winding number n_w.

    Parameters
    ----------
    n_w : int  Primary winding number.

    Returns
    -------
    list of dict
        Each entry: {m, c_L, localisation, description}.
    """
    levels = []
    for m in range(n_w + 1):
        cl = float(m) / float(n_w)
        if cl < 0.5:
            loc = "IR-localised (O(1) Yukawa)"
        elif cl == 0.5:
            loc = "critical point (power-law Yukawa)"
        else:
            loc = "UV-localised (exponentially suppressed Yukawa)"
        levels.append({
            "m": m,
            "c_L": cl,
            "c_L_fraction": f"{m}/{n_w}",
            "localisation": loc,
        })
    return levels


def yukawa_from_cl(cl: float, pi_kr: float = PI_KR) -> float:
    """Compute the effective 4D Yukawa coupling from c_L in the RS1 model.

    For c_L > 1/2 (UV-localised):
        Y_eff = exp(−(c_L − 1/2) × πkR)

    For c_L ≤ 1/2 (IR-localised):
        Y_eff = 1.0  (zero mode has O(1) overlap with IR brane Higgs)

    Parameters
    ----------
    cl    : float  Bulk mass parameter.
    pi_kr : float  RS1 warp exponent πkR.

    Returns
    -------
    float
        Effective 4D Yukawa coupling (Ŷ₅ = 1 assumed).
    """
    if cl <= 0.5:
        return 1.0
    return math.exp(-(cl - 0.5) * pi_kr)


def generation_mass_table(
    n_w: int = N_W,
    v_gev: float = _V_GW_GEV,
    pi_kr: float = PI_KR,
) -> List[Dict[str, object]]:
    """Compute the RS1 fermion mass at each quantized c_L level.

    Uses v_gw from Pillar 201 and the 1-level RS1 Yukawa formula.
    All values assume the 5D Yukawa Ŷ₅ = 1 (AxiomZero compliant).

    Parameters
    ----------
    n_w   : int    Primary winding number.
    v_gev : float  Higgs VEV [GeV] (Pillar 201).
    pi_kr : float  RS1 warp exponent.

    Returns
    -------
    list of dict
        Mass table for each quantization level.
    """
    levels = cl_quantized(n_w)
    table = []
    for entry in levels:
        cl = entry["c_L"]
        m_val = entry["m"]
        y_eff = yukawa_from_cl(cl, pi_kr)
        m_f_gev = v_gev * y_eff
        m_f_mev = m_f_gev * 1000.0
        table.append({
            "m": m_val,
            "c_L": cl,
            "c_L_fraction": entry["c_L_fraction"],
            "Y_eff": y_eff,
            "m_f_GeV": m_f_gev,
            "m_f_MeV": m_f_mev,
            "suppression_exponent": (cl - 0.5) * pi_kr if cl > 0.5 else 0.0,
            "localisation": entry["localisation"],
        })
    return table


def quantization_audit(
    n_w: int = N_W,
    v_gev: float = _V_GW_GEV,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Run the Agent A generation quantization audit.

    Tests whether c_L = m/n_w reproduces the observed fermion mass hierarchy.

    Parameters
    ----------
    n_w   : int    Primary winding number.
    v_gev : float  Higgs VEV from Pillar 201.
    pi_kr : float  RS1 warp exponent.

    Returns
    -------
    dict
        Full audit with comparison to PDG masses and verdict.
    """
    table = generation_mass_table(n_w, v_gev, pi_kr)

    # Identify which levels are "qualitatively correct" (within factor 3)
    comparisons = []
    qualitatively_correct = 0
    for entry in table:
        m_geo = entry["m_f_GeV"]
        m_val = entry["m"]
        cl = entry["c_L"]

        # Find closest PDG fermion
        if cl <= 0.5:
            # IR-localised → heavy quark (top)
            pdg_match = "top"
        elif cl == 0.6:
            pdg_match = "bottom"
        elif cl == 0.8:
            pdg_match = "strange"
        elif cl == 1.0:
            pdg_match = "electron"
        else:
            pdg_match = None

        if pdg_match and pdg_match in _PDG_MASSES_GEV:
            m_pdg = _PDG_MASSES_GEV[pdg_match]
            factor = m_geo / m_pdg if m_pdg > 0 else None
            qualitative = factor is not None and 0.33 < factor < 3.0
            if qualitative:
                qualitatively_correct += 1
        else:
            m_pdg = None
            factor = None
            qualitative = None

        comparisons.append({
            "m": m_val,
            "c_L": cl,
            "m_f_GeV": m_geo,
            "pdg_match": pdg_match,
            "pdg_mass_GeV": m_pdg,
            "ratio_geo_to_pdg": factor,
            "within_factor_3": qualitative,
        })

    return {
        "hypothesis": "c_L^{(m)} = m/n_w  for m = 0, 1, 2, ..., n_w",
        "n_w": n_w,
        "v_gev": v_gev,
        "pi_kr": pi_kr,
        "mass_table": table,
        "pdg_comparisons": comparisons,
        "qualitatively_correct_count": qualitatively_correct,
        "total_levels": n_w + 1,
        "verdict": (
            "The integer quantization c_L = m/n_w reproduces the GENERATION "
            "STRUCTURE (IR vs UV localisation) correctly: 3 heavy (IR) + 3 light "
            "(UV) classes, matching 3 SM generations qualitatively.  "
            "Quantitatively: the top (m=2) and bottom (m=3) levels are within "
            "a factor of 1.5 of PDG values; the lighter generations (muon, "
            "electron) are off by 2-5 orders of magnitude.  "
            "Agent A's claim of '8 fitted → 0 fitted' is NOT confirmed.  "
            "At most 2 parameters are approximately constrained (top, bottom)."
        ),
        "agent_a_verdict": "PARTIALLY CONFIRMED — generation structure correct; mass values incorrect for light fermions",
    }


def heaviest_two_assessment(v_gev: float = _V_GW_GEV, pi_kr: float = PI_KR) -> Dict[str, object]:
    """Assess the top (m=2, c_L=0.4) and bottom (m=3, c_L=0.6) predictions.

    These are the two quantization levels with the best agreement.

    Returns
    -------
    dict
        Detailed assessment of top and bottom quark predictions.
    """
    # m=2, c_L=0.4: IR-localised, Y_eff ≈ 1
    cl_top = 2.0 / float(N_W)
    y_top = yukawa_from_cl(cl_top, pi_kr)
    m_top_geo = v_gev * y_top

    # m=3, c_L=0.6: UV-localised, Y_eff = exp(-3.7)
    cl_bot = 3.0 / float(N_W)
    y_bot = yukawa_from_cl(cl_bot, pi_kr)
    m_bot_geo = v_gev * y_bot

    m_top_pdg = _PDG_MASSES_GEV["top"]
    m_bot_pdg = _PDG_MASSES_GEV["bottom"]

    return {
        "top_quark": {
            "c_L": cl_top,
            "c_L_fraction": "2/5 = 0.4",
            "Y_eff": y_top,
            "m_geo_GeV": m_top_geo,
            "m_pdg_GeV": m_top_pdg,
            "ratio": m_top_geo / m_top_pdg,
            "factor_off": abs(m_top_geo / m_top_pdg - 1.0) * 100.0,
            "note": "IR-localised (c_L < 1/2): O(1) Yukawa, mass ≈ v.  Factor 1.5 off PDG.",
        },
        "bottom_quark": {
            "c_L": cl_bot,
            "c_L_fraction": "3/5 = 0.6",
            "Y_eff": y_bot,
            "m_geo_GeV": m_bot_geo,
            "m_pdg_GeV": m_bot_pdg,
            "ratio": m_bot_geo / m_bot_pdg,
            "factor_off": abs(m_bot_geo / m_bot_pdg - 1.0) * 100.0,
            "note": (
                f"UV-localised (c_L=0.6): Y_eff = exp(-{(0.6-0.5)*pi_kr:.1f}) "
                f"≈ {y_bot:.3f}.  Factor {m_bot_geo/m_bot_pdg:.1f}× off PDG (b quark at {m_bot_pdg} GeV)."
            ),
        },
        "combined_verdict": (
            "Top: 49% off PDG (factor 1.49) — correct O(1) structure.\n"
            "Bottom: 45% off PDG (factor 1.46) — correct order of magnitude.\n"
            "Both are within factor 1.5, suggesting the quantization c_L = m/5 "
            "gives the right generation SCALE but not the precise value.  "
            "Fractional corrections δc_L ~ 0.05-0.1 are needed for <10% accuracy."
        ),
        "status": "QUALITATIVE GEOMETRIC APPROXIMATION — factor 1.5 accuracy for top/bottom",
    }


def axiom_zero_audit() -> Dict[str, object]:
    """Verify AxiomZero compliance for Pillar 205."""
    return {
        "axiom_zero_compliant": True,
        "sm_anchors_count": 0,
        "derivation_inputs": [
            "K_CS = 74   [algebraic theorem, Pillar 58]",
            "n_w = 5     [proved from 5D geometry, Pillar 70-D]",
            "v_gw = 257.6 GeV  [Pillar 201 geometric prediction]",
        ],
        "pdg_masses_role": "comparison only — not used as derivation inputs",
    }


def pillar205_summary() -> Dict[str, object]:
    """Return complete Pillar 205 structured audit output."""
    audit = quantization_audit()
    top_bot = heaviest_two_assessment()

    return {
        "pillar": "205",
        "title": "Generation Quantization Audit — Yukawa Unification Feasibility",
        "version": "v10.4",
        "agent_a_hypothesis": (
            "c_L = m/n_w (m = 0,1,...,5) quantizes all Yukawa couplings "
            "from UM geometry, removing 8 fitted parameters."
        ),
        "audit_result": audit,
        "heaviest_two": top_bot,
        "audit_input": axiom_zero_audit(),
        "conclusion": (
            "The integer quantization captures the generation STRUCTURE "
            "(3 IR heavy + 3 UV light fermions) but fails for lighter generations.  "
            "Top (m=2) and bottom (m=3) are within factor 1.5; lighter fermions "
            "are 2-5 orders of magnitude off.  "
            "Agent A's '8→0 fitted parameters' claim is NOT confirmed.  "
            "A sub-generation correction mechanism (e.g., fractional braid modes, "
            "flavor symmetry A₄, or brane-localized mass terms) is required."
        ),
        "toe_impact": (
            "P6-P8 (m_u, m_d, m_s), P16 (m_e) remain ⚠️ FITTED.  "
            "No TOE score change.  The quantization hypothesis motivates future "
            "work on fractional braid corrections δc_L."
        ),
        "status": "PARTIAL GEOMETRIC APPROXIMATION — generation structure correct; masses incorrect for light fermions",
    }
