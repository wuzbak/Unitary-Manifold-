# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""WS-B Deliverables B1–B3 — c_{Rν_i} Derivation Module for Neutrino Closure.

═══════════════════════════════════════════════════════════════════════════
MAS WORKSTREAM: WS-B  (P19 m_ν₁, P20 Δm²₂₁, P21 Δm²₃₁)
Gate criteria: c_{Rν_i} derived from geometry; residual < 5 %
═══════════════════════════════════════════════════════════════════════════

DERIVATION: c_{Rν_i} FROM S¹/Z₂ ORBIFOLD + BRAID HOLONOMY
------------------------------------------------------------
The right-handed neutrino bulk mass parameter c_{Rν_i} is constrained by
the orbifold structure of S¹/Z₂:

  1. Z₂ ORBIFOLD CONSTRAINT: On S¹/Z₂, the Z₂ parity forces the fermion
     zero-mode to be either UV-localised (c > 1/2) or IR-localised (c < 1/2).
     For active neutrinos: the left-handed ν_L is UV-localised (c_L > 1/2),
     giving a suppressed wavefunction at the IR brane → light neutrino masses.
     For the right-handed ν_R: UV-localisation (c_R > 1/2) also suppresses
     the IR-brane Yukawa coupling.

  2. BRAID HOLONOMY CONDITION: The 5D gauge field winding with (n₁, n₂) = (5, 7)
     imposes a HOLONOMY QUANTIZATION on the bulk fermion profiles.  The
     allowed c_{Rν} values satisfy the winding condition:

         c_{Rν_i} = 1 − i × (n_w / k_CS)    for i ∈ {0, 1, 2}

     This mirrors the left-handed spectrum but with a REFLECTION about c = 1/2:
         c_{Rν}^{(0)} = 1.0000   (most UV-localised right-handed ν)
         c_{Rν}^{(1)} = 0.9324   (intermediate)
         c_{Rν}^{(2)} = 0.8649   (least UV-localised)

     The reflection symmetry c_L + c_R = 3/2 is a consequence of the Dirac
     conjugation on the S¹/Z₂ orbifold (Pillars 75, 81).

  3. DIRAC NEUTRINO MASS ESTIMATE:
     m_νi = Y_ν × v × f₀(c_{Lν_i}) × f₀(c_{Rν_i})

     where f₀(c) = √[(2c−1) × exp(−(c−1/2) × πkR)]   (UV-localised limit)

HONEST GATE REPORT (WS-B Deliverable B3)
-----------------------------------------
The braid holonomy gives c_{Rν_i} analytically.  However:

  • The Yukawa coupling Y_ν is NOT independently derived (open parameter).
  • With Y_ν fixed from one neutrino mass (Δm²₂₁), Δm²₃₁ is predicted at
    ~10 % accuracy (CONSTRAINED — already documented in Pillar 135).
  • The lightest mass m_ν₁ requires Y_ν from the 5D Yukawa mechanism.

VERDICT: P19 (m_ν₁) remains CONSTRAINED; P20/P21 (Δm²) remain
GEOMETRIC ESTIMATE.  The < 5 % gate is NOT met by this derivation.
The c_{Rν_i} formula is newly derived from the orbifold geometry (progress),
but the Yukawa scale Y_ν is still an undetermined free parameter.

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
    "CR_NU_6D",
    "CL_NU_6D",
    "DM2_RATIO_GEO", "DM2_RATIO_PDG",
    "GATE_PASSED",
    "WSB_STATUS",
    # Functions
    "crnu_from_braid_holonomy",
    "clnu_from_6d_geometry",
    "f0_uv_localised",
    "dirac_neutrino_mass_estimate",
    "splitting_ratio_from_crnu",
    "uncertainty_budget",
    "wsb_gate_report",
    "pillar_wsb_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
PI_KR: float = float(K_CS) / 2.0    # = 37.0
N1_BRAID: int = 5
N2_BRAID: int = 7

# Left-handed neutrino bulk mass parameters (from 6D T²/Z₃ fixed points, Pillar 6D-2)
_CL_SPACING: float = float(N_W) / float(K_CS)  # = 5/74
CL_NU_6D: Tuple[float, float, float] = (
    0.5 + 2.0 * _CL_SPACING,    # c_{Lν₃}: most UV-localized (lightest ν left-chiral mode)
    0.5 + _CL_SPACING,          # c_{Lν₂}
    0.5,                         # c_{Lν₁}: IR-critical
)

# Right-handed neutrino bulk mass parameters: c_{Rν}^{(i)} = 1 - i × n_w/k_CS
# Reflection c_L + c_R = 3/2 on the Dirac conjugate orbit
CR_NU_6D: Tuple[float, float, float] = (
    1.0,                          # c_{Rν₃}: most UV-localized right-handed
    1.0 - _CL_SPACING,           # c_{Rν₂}
    1.0 - 2.0 * _CL_SPACING,    # c_{Rν₁}
)

# Splitting ratio (pure geometry from braid pair, Pillar 135)
DM2_RATIO_GEO: float = float(N1_BRAID * N2_BRAID + 1)   # = 36
DM2_RATIO_PDG: float = 2.453e-3 / 7.53e-5                # ≈ 32.6
DM2_RATIO_PCT_ERR: float = abs(DM2_RATIO_GEO - DM2_RATIO_PDG) / DM2_RATIO_PDG * 100.0

# PDG neutrino mass data (comparison only)
_DM2_21_PDG_EV2: float = 7.53e-5
_DM2_31_PDG_EV2: float = 2.453e-3
_SUM_MNU_PLANCK_EV: float = 0.12

GATE_PASSED: bool = False   # < 5 % gate NOT met (Yukawa scale open)
WSB_STATUS: str = "CONSTRAINED/ESTIMATE — c_{Rν_i} derived from geometry; Yukawa scale open"


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def crnu_from_braid_holonomy(n_w: int = N_W, k_cs: int = K_CS) -> Dict[str, object]:
    """Derive c_{Rν_i} from S¹/Z₂ braid holonomy condition.

    The Z₂ orbifold reflection on S¹/Z₂ maps y → −y.  The Dirac conjugate
    of a left-handed zero mode with c_L satisfies c_R = 3/2 − c_L on the
    holomorphically-paired orbit.

    For the 6D fixed-point spectrum c_L^{(i)} = 1/2 + i × n_w/k_CS:

        c_R^{(i)} = 3/2 − c_L^{(i)} = 1 − i × n_w/k_CS

    Parameters
    ----------
    n_w  : int   Winding number.
    k_cs : int   Chern-Simons level.

    Returns
    -------
    dict with c_{Rν_i} values and derivation.
    """
    spacing = float(n_w) / float(k_cs)
    cr_values = [1.0 - i * spacing for i in range(3)]
    cl_values = [0.5 + i * spacing for i in range(3)]
    return {
        "derivation": "c_{Rν_i} = 1 - i × n_w/k_CS (Z₂ Dirac-conjugate orbit)",
        "formula": "c_L + c_R = 3/2  (Z₂ reflection symmetry on S¹/Z₂)",
        "n_w": n_w,
        "k_cs": k_cs,
        "spacing": spacing,
        "c_L_values": cl_values,
        "c_R_values": cr_values,
        "axiomzero_compliant": True,
        "inputs": ["n_w", "k_CS"],
        "note": (
            "The c_L + c_R = 3/2 relation follows from the Z₂ boundary condition "
            "on the 5D Dirac fermion: if Ψ_L has BC c_L, then Ψ_R (the Dirac "
            "conjugate) has BC 3/2 − c_L to preserve the Dirac kinetic term "
            "∫d⁵x √|G| Ψ̄ Γ^M D_M Ψ under y ↦ πR − y."
        ),
    }


def clnu_from_6d_geometry(n_w: int = N_W, k_cs: int = K_CS) -> Dict[str, object]:
    """Return the left-handed neutrino c_L values from 6D T²/Z₃ geometry.

    Parameters
    ----------
    n_w  : int   Winding number.
    k_cs : int   CS level.

    Returns
    -------
    dict with c_{Lν_i} values from 6D fixed-point positions.
    """
    spacing = float(n_w) / float(k_cs)
    cl_nu = [0.5 + i * spacing for i in range(3)]
    return {
        "derivation": "c_{Lν_i} from T²/Z₃ fixed-point positions (Pillar 6D-2)",
        "c_L_nu_gen0": cl_nu[0],
        "c_L_nu_gen1": cl_nu[1],
        "c_L_nu_gen2": cl_nu[2],
        "ordering": "gen0 = heaviest (largest Yukawa), gen2 = lightest",
    }


def f0_uv_localised(c: float, pi_kr: float = PI_KR) -> float:
    """Zero-mode wavefunction profile for UV-localised fermion (c > 1/2).

    f₀(c) ≈ √(2c−1) × exp(−(c−1/2) × πkR)    (UV-localised limit)

    Parameters
    ----------
    c     : float  Bulk mass parameter (must be > 1/2).
    pi_kr : float  πkR.

    Returns
    -------
    float
        Zero-mode profile (positive).

    Raises
    ------
    ValueError if c ≤ 1/2.
    """
    if c <= 0.5:
        raise ValueError(f"c must be > 1/2 for UV-localised mode; got {c}")
    x = (c - 0.5) * pi_kr
    # Protect overflow for very large x
    if x > 300:
        return 0.0
    return math.sqrt(2.0 * c - 1.0) * math.exp(-x)


def dirac_neutrino_mass_estimate(
    yukawa_nu: float = 1.0,
    v_higgs_gev: float = 246.0,
    pi_kr: float = PI_KR,
    n_w: int = N_W,
    k_cs: int = K_CS,
) -> Dict[str, object]:
    """Estimate the three Dirac neutrino masses from c_L + c_R derived values.

    m_νi = Y_ν × v × f₀(c_{Lνi}) × f₀(c_{Rνi})

    The Yukawa coupling Y_ν is NOT derived here (open parameter).  This
    function evaluates the PRODUCT f₀(c_L) × f₀(c_R) for each generation
    to show the geometric suppression structure.

    Parameters
    ----------
    yukawa_nu    : float  Neutrino Yukawa scale Y_ν (default 1.0 as free parameter).
    v_higgs_gev  : float  Higgs VEV in GeV.
    pi_kr        : float  πkR.
    n_w, k_cs    : int    Braid winding / CS level.

    Returns
    -------
    dict with profile products, mass estimates, and status.
    """
    spacing = float(n_w) / float(k_cs)
    cl_nu = [0.5 + i * spacing for i in range(3)]
    cr_nu = [1.0 - i * spacing for i in range(3)]

    profile_products = []
    masses_ev = []

    for i in range(3):
        cl_i = cl_nu[i]
        cr_i = cr_nu[i]
        f_l = f0_uv_localised(cl_i, pi_kr) if cl_i > 0.5 else 1.0
        f_r = f0_uv_localised(cr_i, pi_kr) if cr_i > 0.5 else 1.0
        prod = f_l * f_r
        m_ev = yukawa_nu * v_higgs_gev * 1e9 * prod   # eV
        profile_products.append(prod)
        masses_ev.append(m_ev)

    ratios = []
    for i in range(2):
        r = profile_products[i] / max(profile_products[i + 1], 1e-300)
        ratios.append(r)

    return {
        "yukawa_nu_free_parameter": yukawa_nu,
        "note": (
            "Y_ν is NOT derived from geometry at this level.  "
            "Masses below are ESTIMATES for Y_ν = 1.0."
        ),
        "profile_products": profile_products,
        "masses_eV": masses_ev,
        "mass_ratios": ratios,
        "status": "ESTIMATES ONLY — Y_ν is a free parameter",
    }


def splitting_ratio_from_crnu() -> Dict[str, object]:
    """Return the mass-squared splitting ratio from the braid pair geometry.

    This uses the Pillar 135 result: Δm²₃₁/Δm²₂₁ = n₁n₂ + 1 = 36.
    The c_{Rν_i} derivation does not change this prediction.

    Returns
    -------
    dict with ratio prediction, PDG comparison, and pct_err.
    """
    dm2_31_predicted_ev2 = DM2_RATIO_GEO * _DM2_21_PDG_EV2
    dm2_31_pct_err = abs(dm2_31_predicted_ev2 - _DM2_31_PDG_EV2) / _DM2_31_PDG_EV2 * 100.0
    return {
        "splitting_ratio_geo": DM2_RATIO_GEO,
        "splitting_ratio_pdg": DM2_RATIO_PDG,
        "splitting_ratio_pct_err": DM2_RATIO_PCT_ERR,
        "dm2_31_predicted_ev2": dm2_31_predicted_ev2,
        "dm2_31_pdg_ev2": _DM2_31_PDG_EV2,
        "dm2_31_pct_err": dm2_31_pct_err,
        "gate_lt5pct": dm2_31_pct_err < 5.0,
        "note": (
            "Δm²₃₁/Δm²₂₁ = 36 (geometry) vs 32.6 (PDG) — 10 % accuracy.  "
            "Gate not met.  Status: GEOMETRIC ESTIMATE (P20/P21)."
        ),
    }


def uncertainty_budget() -> Dict[str, object]:
    """Return the WS-B Deliverable B2 uncertainty budget.

    Returns
    -------
    dict with per-source uncertainty contributions.
    """
    return {
        "deliverable": "WS-B / B2 — Uncertainty budget",
        "sources": [
            {
                "source": "Yukawa coupling Y_ν",
                "type": "FREE PARAMETER",
                "impact": "Scales all three neutrino masses → completely open",
                "reduction_path": "Derive Y_ν from GW coupling + 5D Yukawa action",
            },
            {
                "source": "c_{Lν_i} spectrum",
                "type": "DERIVED (6D geometry)",
                "impact": "Sets inter-generation ratios; 6D gives c_L^{(i)} = 1/2+i×5/74",
                "residual_pct": "10 % on Δm² ratio (ratio 36 vs PDG 32.6)",
            },
            {
                "source": "c_{Rν_i} spectrum",
                "type": "DERIVED (Z₂ holonomy, this module)",
                "impact": "Further suppresses all masses uniformly; ratio predictions unchanged",
                "residual_pct": "Same 10 % as c_{Lν_i} alone (equal-spacing approximation)",
            },
            {
                "source": "πkR = 37.0",
                "type": "DERIVED (GW mechanism)",
                "impact": "Exponential sensitivity; ±0.1 in πkR → ±3.7 % in wavefunction",
                "residual_pct": "< 5 % from this source alone",
            },
            {
                "source": "Normal vs inverted hierarchy",
                "type": "UNKNOWN (not yet resolved by UM)",
                "impact": "Changes which generation is lightest",
                "residual_pct": "~factor 2 on Δm²₃₁ if wrong ordering",
            },
        ],
        "dominant_uncertainty": "Y_ν (unmeasured Yukawa scale)",
        "gate_status": "NOT MET — Y_ν must be derived before < 5 % gate is possible",
    }


def wsb_gate_report() -> Dict[str, object]:
    """Consolidated WS-B gate evidence report (B1 + B2 + B3).

    Returns
    -------
    dict for attachment to MAS W1 ledger.
    """
    crnu = crnu_from_braid_holonomy()
    clnu = clnu_from_6d_geometry()
    mass_est = dirac_neutrino_mass_estimate()
    split = splitting_ratio_from_crnu()
    budget = uncertainty_budget()
    return {
        "workstream": "WS-B",
        "parameters": ["P19 (m_ν₁)", "P20 (Δm²₂₁)", "P21 (Δm²₃₁)"],
        "deliverable_B1_crnu_module": crnu,
        "deliverable_B2_uncertainty_budget": budget,
        "deliverable_B3_promotion_rubric": {
            "current_status": "P19 CONSTRAINED; P20/P21 GEOMETRIC ESTIMATE",
            "gate_condition_lt5pct": split["gate_lt5pct"],
            "splitting_ratio_pct_err": split["splitting_ratio_pct_err"],
            "promotion_to_geometric_prediction": (
                "Requires: (1) derive Y_ν from geometry; "
                "(2) improve Δm² ratio accuracy to < 5 %.  "
                "Neither condition is currently met."
            ),
        },
        "clnu_derivation": clnu,
        "mass_estimates": mass_est,
        "splitting_ratio": split,
        "gate_passed": GATE_PASSED,
        "status_change": "NONE — P19 CONSTRAINED, P20/P21 GEOMETRIC ESTIMATE",
        "what_is_newly_achieved": [
            "c_{Rν_i} = 1 − i × n_w/k_CS derived from Z₂ Dirac-conjugate orbit",
            "Both c_L and c_R spectra now have geometric derivations",
            "Yukawa scale Y_ν identified as the remaining free parameter",
            "Uncertainty budget formally documented",
        ],
    }


def pillar_wsb_summary() -> Dict[str, object]:
    """Return a brief WS-B summary for the MAS ledger."""
    split = splitting_ratio_from_crnu()
    return {
        "workstream": "WS-B",
        "parameters": "P19, P20, P21",
        "gate_passed": GATE_PASSED,
        "status": WSB_STATUS,
        "crnu_derived": True,
        "yukawa_nu_derived": False,
        "splitting_ratio_pct_err": split["splitting_ratio_pct_err"],
        "rung_impact": (
            "Both c_L and c_R spectra derived from orbifold geometry.  "
            "Yukawa scale remains open.  "
            "P19 stays CONSTRAINED, P20/P21 stay GEOMETRIC ESTIMATE."
        ),
    }
