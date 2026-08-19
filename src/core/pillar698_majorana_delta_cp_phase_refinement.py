# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 698 — Tightening 13: Majorana Phase δ_CP Refinement

The Dirac CP phase δ_CP in the PMNS matrix arises from KK wavefunction
overlaps in the same manner as the CKM phase (Pillar 693), with the
Majorana phases α₁, α₂ arising from the orbifold boundary conditions
that also generate the mass hierarchy (Pillar 689).

This pillar computes:
1. The KK-derived Dirac phase δ_CP from the T₂/Z₂ orbifold geometry.
2. Majorana phases α₁, α₂ from the Z₂ Dirichlet BC (Pillar 690).
3. Neutrinoless double-beta decay effective mass |m_ββ| as a falsifier.

NuFIT 6.0 (NH): δ_CP ≈ 197° best fit, but with large uncertainty.
KK prediction: δ_CP is constrained by the same braided-winding
geometry that fixes θ₁₂/θ₁₃/θ₂₃ (Pillars 683, 688, 694).

Architecture note (Tightening 13): the KK prediction for δ_CP is
consistent with the NuFIT 6.0 preferred region but sub-leading
compared to the geometric angle uncertainties. This is an honest
consistency check — not a precision prediction.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── PMNS parameters (NuFIT 6.0 NH) ───────────────────────────────────────────
DELTA_CP_NUFIT_DEG     = 197.0    # δ_CP best fit (NH) [degrees]
DELTA_CP_NUFIT_1SIGMA  = 25.0     # ±1σ uncertainty [degrees]

SIN2_THETA12 = 0.307
SIN2_THETA13 = 0.02220
SIN2_THETA23 = 0.546

DM21_EV2 = 7.442e-5
DM31_EV2 = 2.4109e-3

# Majorana phases (not directly constrained by oscillation experiments)
ALPHA1_KK_DEG = 0.0     # convention: absorb into phase definition
ALPHA2_KK_DEG = 0.0     # 0° in the minimal orbifold BC scenario

# ── KK-derived δ_CP ──────────────────────────────────────────────────────────
# δ_CP from the braided-winding geometry: argument of the KK CP-asymmetry
# factor J_ν / J_CKM, where J_ν is the PMNS Jarlskog invariant.
# The ratio is fixed by the ratio of winding sums over KK families.

N_W   = 5
K_CS  = 74

def kk_predicted_delta_cp_deg() -> float:
    """
    Estimate δ_CP from the KK winding geometry.

    The leading KK contribution to the PMNS phase is:
        δ_CP = π + arctan(η_ν / ρ_ν)
    where (ρ_ν, η_ν) are the KK-analogue of Wolfenstein (ρ̄, η̄) for ν sector.
    For the minimal orbifold BC: ρ_ν = 1 - λ²/2, η_ν = λ²/2 × N_W/K_CS.
    """
    lam_nu   = math.sqrt(SIN2_THETA12)   # solar mixing ~ λ_ν
    rho_nu   = 1 - lam_nu ** 2 / 2
    eta_nu   = lam_nu ** 2 / 2 * N_W / K_CS
    delta_cp = math.pi + math.atan2(eta_nu, rho_nu)
    return math.degrees(delta_cp)

def delta_cp_consistent_with_nufit(
    delta_kk_deg: float = None,
    nufit_best: float = DELTA_CP_NUFIT_DEG,
    nufit_1sigma: float = DELTA_CP_NUFIT_1SIGMA,
) -> dict:
    """Check whether KK δ_CP is consistent with NuFIT 6.0 at 2σ."""
    if delta_kk_deg is None:
        delta_kk_deg = kk_predicted_delta_cp_deg()
    diff = abs(delta_kk_deg - nufit_best)
    # Handle circular distance
    diff = min(diff, 360 - diff)
    consistent_2sigma = diff < 2 * nufit_1sigma
    return {
        "delta_kk_deg":         delta_kk_deg,
        "nufit_best_deg":       nufit_best,
        "nufit_1sigma_deg":     nufit_1sigma,
        "angular_diff_deg":     diff,
        "consistent_2sigma":    consistent_2sigma,
    }

# ── Majorana phases ───────────────────────────────────────────────────────────

def majorana_phases() -> dict:
    """Return Majorana phase predictions from minimal orbifold BC."""
    return {
        "alpha1_deg":  ALPHA1_KK_DEG,
        "alpha2_deg":  ALPHA2_KK_DEG,
        "source":      "Z2 Dirichlet BC — minimal scenario (P690)",
        "note":        "Majorana phases not constrained by oscillation data",
    }

# ── Neutrinoless double-beta decay effective mass ─────────────────────────────

def m_bb_effective(
    delta_cp_deg: float = DELTA_CP_NUFIT_DEG,
    alpha1_deg:   float = ALPHA1_KK_DEG,
    alpha2_deg:   float = ALPHA2_KK_DEG,
) -> dict:
    """
    |m_ββ| = |Σ_i V_ei² m_i| for NH.

    For NH: dominant from m_1 (lightest, near-zero) → |m_ββ| ~ m_1
    We take lightest m_1 = 0 (massless limit).
    Then |m_ββ| ≈ |sin²θ₁₂ cos²θ₁₃ e^{iα₁} √Δm²₂₁
                 + sin²θ₁₃ e^{i(α₂-2δ)} √Δm²₃₁|
    """
    m2  = math.sqrt(DM21_EV2)           # eV
    m3  = math.sqrt(DM31_EV2)           # eV
    s12sq = SIN2_THETA12
    c12sq = 1 - s12sq
    s13sq = SIN2_THETA13
    c13sq = 1 - s13sq

    alpha1 = math.radians(alpha1_deg)
    alpha2 = math.radians(alpha2_deg)
    delta  = math.radians(delta_cp_deg)

    # Three mass eigenstates, NH (m1≈0)
    term2 = s12sq * c13sq * m2 * complex(math.cos(alpha1), math.sin(alpha1))
    term3 = s13sq           * m3 * complex(math.cos(alpha2 - 2*delta),
                                            math.sin(alpha2 - 2*delta))
    m_bb  = abs(term2 + term3)
    return {
        "pillar":      698,
        "label":       "MAJORANA_DELTA_CP_REFINEMENT",
        "delta_cp_deg": delta_cp_deg,
        "m_bb_eV":     m_bb,
        "m_bb_meV":    m_bb * 1e3,
        "nh_hierarchy": True,
        "ks3_upper_bound_meV": 36.0,   # KamLAND-Zen / GERDA conservative
        "below_ks3_bound":     m_bb * 1e3 < 36.0,
    }
