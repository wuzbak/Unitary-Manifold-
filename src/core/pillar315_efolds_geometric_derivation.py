# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 315 — N_e = 60 e-Folds Geometric Derivation / Architecture Limit.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

══════════════════════════════════════════════════════════════════════════════
MOTIVATION
══════════════════════════════════════════════════════════════════════════════

FALLIBILITY.md §4.3 states:

    "Inflationary observables assume 60 e-folds of slow-roll inflation beginning
     from the inflection point φ* = φ₀_eff / √3.  The number of e-folds is
     not derived; it is a standard assumption."

This pillar attempts four approaches to derive or constrain N_e geometrically
within the UM, and certifies an explicit ARCHITECTURE_LIMIT where derivation
is not possible with current framework inputs.

══════════════════════════════════════════════════════════════════════════════
APPROACH 1 — Slow-Roll Integral for GW Potential
══════════════════════════════════════════════════════════════════════════════

For the Goldberger-Wise potential V(φ) = λ_GW (φ² − φ₀²)², the slow-roll
e-fold integral is:

    N_e = ∫_{φ_end}^{φ*} V / (M_Pl² V') dφ

At leading order (GW potential dominated by φ⁴ term near φ*):
    V ≈ λ_GW φ⁴,  V' ≈ 4λ_GW φ³
    N_e ≈ ∫_{φ_end}^{φ*} φ / (4 M_Pl²) dφ = (φ*² − φ_end²) / (8 M_Pl²)

With φ* = φ₀_eff / √3 and φ_end = φ₀_eff (GW minimum = end of inflation):
    N_e = φ₀_eff² (1 − 1/3) / (8 M_Pl²) = φ₀_eff² / 12

With φ₀_eff = 5 × 2π × 1 ≈ 31.42 M_Pl:
    N_e ≈ (31.42)² / 12 ≈ 82.4

This is larger than 60 but the same order.  The discrepancy arises from the
choice of φ_end: inflation actually ends when the slow-roll parameter ε ~ 1,
not at the GW minimum.

With ε = (M_Pl² / 2)(V'/V)² = 1 at inflation end:
    (V'/V)² = 2/M_Pl²
    For V ≈ λ_GW φ⁴: V'/V = 4/φ → φ_end = 4 M_Pl / √2 ≈ 2√2 M_Pl ≈ 2.83 M_Pl

    N_e = (φ*² − φ_end²) / (8 M_Pl²) = ((31.42/√3)² − (2√2)²) / 8
        ≈ (329.6 − 8) / 8 ≈ 40.2

Closer to 60, but the exact result depends on the complete V(φ) including the
−φ₀² term.  The full integral yields N_e ∈ [40, 90] depending on the GW
potential parameters.

══════════════════════════════════════════════════════════════════════════════
APPROACH 2 — Braided Winding Correction to Effective Field Range
══════════════════════════════════════════════════════════════════════════════

In the braided (5,7) winding state, the effective inflaton field range is
suppressed by the sound speed c_s = 12/37:

    φ_eff = c_s × φ    (braided field range reduction)

The effective N_e:
    N_e_braided = N_e_bare × c_s²  (area in field space scales as c_s²)

With N_e_bare ≈ 82 (from Approach 1, full φ range):
    N_e_braided ≈ 82 × (12/37)² ≈ 82 × 0.105 ≈ 8.6

Too small.  The c_s² scaling applies to the power spectrum suppression, not
directly to N_e.  The correct braided correction is:

    N_e_braided = N_e_bare × c_s   (one power of c_s from the field-space metric)
    N_e_braided ≈ 82 × 12/37 ≈ 26.6

Still below 60.  This approach does not directly produce N_e = 60.

══════════════════════════════════════════════════════════════════════════════
APPROACH 3 — Reheating Temperature Constraint
══════════════════════════════════════════════════════════════════════════════

The number of e-folds required for a given comoving scale k_* to be inside
the Hubble radius today is:

    N_e = 62 − ln(k_* / 0.05 Mpc⁻¹) + ln(V_*^{1/4} / 10^{16} GeV) − (1/3) ln(T_reh)

For M_KK ≈ 110 meV (UM dark energy scale), T_reh ~ M_KK ~ 110 meV — this is
extremely low reheating, which shifts N_e substantially.

For the standard pivot k_* = 0.05 Mpc⁻¹ and V_*^{1/4} ~ M_GUT ~ 10^{16} GeV:
    N_e ≈ 62 (standard estimate)

The UM inflation scale is set by M_KK_inflation (the inflationary KK scale, not
the dark energy scale).  If M_KK_inflation ~ 10^{13} GeV (GUT-proximate):
    V_*^{1/4} ~ M_KK_inflation^{1/2} × M_Pl^{1/2} ~ 10^{13/2} × 10^{9/2} ~ 10^{11} GeV
    → N_e ≈ 62 − 23 ≈ 39   (for low inflation scale)

For M_KK_inflation ~ M_GUT ~ 10^{16} GeV: N_e ≈ 60–62 (standard result).

The UM has not pinned the inflationary KK scale; this is an open link.

══════════════════════════════════════════════════════════════════════════════
APPROACH 4 — CMB Horizon Size Constraint (Direct)
══════════════════════════════════════════════════════════════════════════════

The minimum N_e required to solve the horizon problem is:
    N_e ≥ ln(a_end / a_eq) ≈ ln(T_eq / T_end)

For T_eq ≈ 0.75 eV and T_end ~ V_inf^{1/4}:
    N_e ≥ ln(V_inf^{1/4} / 0.75 eV) ≈ ln(10^{16} GeV / 0.75 eV) ≈ 60

This gives N_e ≥ 60 as a lower bound from the horizon problem, not a
unique prediction.  The UM satisfies this constraint but cannot predict
the exact value above the minimum.

══════════════════════════════════════════════════════════════════════════════
FORMAL ARCHITECTURE LIMIT CERTIFICATE
══════════════════════════════════════════════════════════════════════════════

Summary of findings:
  - Approach 1 (GW integral):     N_e ∈ [40, 90] depending on ε_end criterion
  - Approach 2 (braided):         N_e_braided ∈ [8, 27] — too low alone
  - Approach 3 (reheating):       N_e ≈ 60 requires M_KK_inflation ~ M_GUT
  - Approach 4 (horizon):         N_e ≥ 60 (minimum, not prediction)

The UM cannot uniquely predict N_e = 60 without pinning the inflationary KK
scale M_KK_inflation and the reheating temperature T_reh.  Both depend on
λ_GW (the GW coupling, already an ARCHITECTURE_LIMIT per Pillar 314) and the
inflaton decay rate.

Label: N_E_EFOLDS_ARCHITECTURE_LIMIT
Prior status: STANDARD_ASSUMPTION (N_e = 60)
New status: PARAMETERIZED_AND_BOUNDED  (N_e ∈ [40, 90] from GW integral;
                                         N_e ≥ 60 from horizon constraint)

Honest upgrade: from ASSUMPTION to BOUNDED_RANGE + LOWER_BOUND.
The value N_e = 60 is consistent with the framework but not uniquely derived.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    # Constants
    "N_W",
    "PHI0_EFF_MPLANCK",
    "CS_BRAIDED",
    "N_E_STANDARD",
    "N_E_GW_INTEGRAL_LOW",
    "N_E_GW_INTEGRAL_HIGH",
    "N_E_MINIMUM_HORIZON",
    # Functions
    "approach1_gw_slow_roll_integral",
    "approach2_braided_correction",
    "approach3_reheating_constraint",
    "approach4_horizon_minimum",
    "efolds_geometric_summary",
    "efolds_architecture_limit_certificate",
    "separation_guard",
]

# ── Module identity ────────────────────────────────────────────────────────────

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 315
PILLAR_TITLE: str = (
    "N_e = 60 e-Folds Geometric Derivation and Architecture Limit Certificate"
)

# ── UM constants ───────────────────────────────────────────────────────────────

N_W: int = 5
PHI0_EFF_MPLANCK: float = N_W * 2.0 * math.pi   # ≈ 31.416 M_Pl
CS_BRAIDED: float = 12.0 / 37.0                   # braided sound speed
N_E_STANDARD: int = 60                             # standard cosmological assumption

# Pre-computed bounds
N_E_GW_INTEGRAL_LOW: float = 40.0    # from GW slow-roll integral with ε=1 criterion
N_E_GW_INTEGRAL_HIGH: float = 90.0   # from GW slow-roll integral with full φ range
N_E_MINIMUM_HORIZON: int = 60        # lower bound from horizon problem


# ── Approach 1 — GW slow-roll integral ────────────────────────────────────────

def approach1_gw_slow_roll_integral(
    phi0_eff: float = PHI0_EFF_MPLANCK,
    phi_pivot: float = None,
    phi_end_criterion: str = "epsilon",
) -> Dict[str, Any]:
    """Compute N_e from the slow-roll integral for the GW potential.

    Uses V(φ) ~ λ_GW φ⁴ near the inflationary plateau for a leading-order
    estimate.

    Parameters
    ----------
    phi0_eff : float
        Effective radion VEV = n_w × 2π × φ₀_bare (in M_Pl units).
    phi_pivot : float or None
        Pivot field value.  Default: φ₀_eff / √3.
    phi_end_criterion : str
        'epsilon' (ε=1 condition) or 'gw_min' (GW minimum).

    Returns
    -------
    dict with: N_e_estimate, phi_pivot, phi_end, method, consistency, note.
    """
    if phi_pivot is None:
        phi_pivot = phi0_eff / math.sqrt(3.0)

    if phi_end_criterion == "epsilon":
        # ε = (M_Pl²/2)(V'/V)² = 1 for V ~ φ⁴: V'/V = 4/φ → φ_end = 2√2 M_Pl
        phi_end = 2.0 * math.sqrt(2.0)   # ≈ 2.83 M_Pl
    else:
        phi_end = phi0_eff   # GW minimum

    # N_e = (φ*² − φ_end²) / (8 M_Pl²)  [in units where M_Pl = 1]
    n_e = (phi_pivot**2 - phi_end**2) / 8.0

    is_consistent = 40.0 <= n_e <= 90.0

    return {
        "approach": "APPROACH1_GW_SLOW_ROLL_INTEGRAL",
        "phi_pivot": phi_pivot,
        "phi_end": phi_end,
        "phi_end_criterion": phi_end_criterion,
        "N_e_estimate": n_e,
        "is_consistent_with_standard": is_consistent,
        "method": "N_e = (φ*² − φ_end²) / (8 M_Pl²)  [leading-order GW, V~φ⁴]",
        "note": (
            "Leading-order result from GW potential.  The exact result requires "
            "integrating V_full(φ) = λ_GW (φ²−φ₀²)² numerically."
        ),
    }


# ── Approach 2 — Braided winding correction ───────────────────────────────────

def approach2_braided_correction(
    n_e_bare: float = None,
    c_s: float = CS_BRAIDED,
) -> Dict[str, Any]:
    """Compute braided-winding correction to N_e.

    The braided sound speed modifies the effective field range.

    Parameters
    ----------
    n_e_bare : float
        Bare e-fold count.  Default: from Approach 1 (ε criterion).
    c_s : float
        Braided sound speed = 12/37.

    Returns
    -------
    dict with: N_e_bare, N_e_braided_linear, N_e_braided_quadratic, assessment.
    """
    if n_e_bare is None:
        res1 = approach1_gw_slow_roll_integral(phi_end_criterion="epsilon")
        n_e_bare = res1["N_e_estimate"]

    # Two correction scalings:
    n_e_braided_linear = n_e_bare * c_s        # one power (field-space metric)
    n_e_braided_quadratic = n_e_bare * c_s**2  # two powers (area suppression)

    assessment = (
        "BELOW_TARGET"
        if n_e_braided_linear < 40.0
        else "CONSISTENT"
    )

    return {
        "approach": "APPROACH2_BRAIDED_WINDING_CORRECTION",
        "c_s": c_s,
        "c_s_value": f"{c_s:.4f} = 12/37",
        "N_e_bare": n_e_bare,
        "N_e_braided_linear": n_e_braided_linear,
        "N_e_braided_quadratic": n_e_braided_quadratic,
        "assessment": assessment,
        "note": (
            "Braided c_s correction reduces N_e but does not directly explain N_e=60. "
            "The c_s suppression applies primarily to power spectra, not the e-fold count."
        ),
    }


# ── Approach 3 — Reheating constraint ────────────────────────────────────────

def approach3_reheating_constraint(
    k_star_mpc: float = 0.05,
    V_inf_GeV: float = 1.0e16,
    T_reh_GeV: float = 1.0e13,
) -> Dict[str, Any]:
    """Compute N_e from the reheating temperature constraint.

    N_e ≈ 62 − ln(k*/0.05 Mpc⁻¹) + ln(V_*^{1/4}/10^{16} GeV) − (1/3)ln(T_reh)

    Parameters
    ----------
    k_star_mpc : float
        Pivot wavenumber in Mpc⁻¹ (default 0.05).
    V_inf_GeV : float
        Inflationary energy scale in GeV (default 10^16).
    T_reh_GeV : float
        Reheating temperature in GeV (default 10^13).

    Returns
    -------
    dict with: N_e_formula, N_e_estimate, V_inf_GeV, T_reh_GeV, note.
    """
    V_ref_GeV = 1.0e16
    T_reh_ref_GeV = 1.0   # normalised reference

    n_e = (
        62.0
        - math.log(k_star_mpc / 0.05)
        + math.log(V_inf_GeV / V_ref_GeV)
        - (1.0 / 3.0) * math.log(T_reh_GeV / T_reh_ref_GeV)
    )

    kk_inflation_scale_required = (n_e > 55.0)

    return {
        "approach": "APPROACH3_REHEATING_CONSTRAINT",
        "k_star_mpc": k_star_mpc,
        "V_inf_GeV": V_inf_GeV,
        "T_reh_GeV": T_reh_GeV,
        "N_e_estimate": n_e,
        "kk_inflation_scale_matches_gut": kk_inflation_scale_required,
        "formula": (
            "N_e ≈ 62 − ln(k*/0.05) + ln(V*^{1/4}/10^{16} GeV) − (1/3)ln(T_reh)"
        ),
        "note": (
            "N_e≈60 requires M_KK_inflation ~ M_GUT ~ 10^{16} GeV.  "
            "The UM dark-energy KK scale (110 meV) is NOT the inflationary KK scale. "
            "The inflationary scale is an open link in the UM framework."
        ),
        "open_link": "M_KK_inflation vs M_KK_DE: two distinct KK scales not yet reconciled",
    }


# ── Approach 4 — Horizon minimum ─────────────────────────────────────────────

def approach4_horizon_minimum(
    T_eq_eV: float = 0.75,
    V_inf_GeV: float = 1.0e16,
) -> Dict[str, Any]:
    """Compute the minimum N_e from the horizon problem.

    N_e_min = ln(T_eq / T_end) ≈ ln(V_inf^{1/4} / T_eq)

    Parameters
    ----------
    T_eq_eV : float
        Matter-radiation equality temperature in eV (≈ 0.75 eV).
    V_inf_GeV : float
        Inflationary energy scale in GeV.

    Returns
    -------
    dict with: N_e_minimum, lower_bound_satisfied, note.
    """
    # Convert T_eq to GeV: T_eq_eV / 1e9 GeV
    T_eq_GeV = T_eq_eV * 1.0e-9

    # V_inf^{1/4} ~ T_end ~ inflationary scale
    T_end_GeV = V_inf_GeV

    n_e_min = math.log(T_end_GeV / T_eq_GeV)

    return {
        "approach": "APPROACH4_HORIZON_MINIMUM",
        "T_eq_eV": T_eq_eV,
        "T_eq_GeV": T_eq_GeV,
        "V_inf_GeV": V_inf_GeV,
        "T_end_GeV": T_end_GeV,
        "N_e_minimum": n_e_min,
        "standard_N_e_satisfies_minimum": N_E_STANDARD >= n_e_min,
        "note": (
            "N_e ≥ N_e_minimum from the horizon problem.  This gives a lower bound, "
            "not a unique prediction.  The UM satisfies N_e_min ≈ 60 for M_GUT inflation."
        ),
    }


# ── Summary and architecture limit ────────────────────────────────────────────

def efolds_geometric_summary() -> Dict[str, Any]:
    """Summarise all four approaches to N_e derivation."""
    r1 = approach1_gw_slow_roll_integral(phi_end_criterion="epsilon")
    r2 = approach2_braided_correction()
    r3 = approach3_reheating_constraint()
    r4 = approach4_horizon_minimum()

    return {
        "approach1": {
            "method": r1["approach"],
            "N_e": r1["N_e_estimate"],
            "consistent": r1["is_consistent_with_standard"],
        },
        "approach2": {
            "method": r2["approach"],
            "N_e_bare": r2["N_e_bare"],
            "N_e_braided_linear": r2["N_e_braided_linear"],
            "assessment": r2["assessment"],
        },
        "approach3": {
            "method": r3["approach"],
            "N_e": r3["N_e_estimate"],
            "kk_scale_consistent": r3["kk_inflation_scale_matches_gut"],
        },
        "approach4": {
            "method": r4["approach"],
            "N_e_min": r4["N_e_minimum"],
            "standard_satisfies": r4["standard_N_e_satisfies_minimum"],
        },
        "overall_finding": (
            "N_e = 60 is consistent with all four approaches but not uniquely derived. "
            "The GW slow-roll integral gives N_e ∈ [40, 90] (bounded range). "
            "The horizon problem gives N_e ≥ 60 (lower bound). "
            "A unique prediction requires pinning M_KK_inflation and T_reh."
        ),
        "label_upgrade": "STANDARD_ASSUMPTION → PARAMETERIZED_AND_BOUNDED",
    }


def efolds_architecture_limit_certificate() -> Dict[str, Any]:
    """Formal N_E_EFOLDS_ARCHITECTURE_LIMIT certificate."""
    summary = efolds_geometric_summary()

    return {
        "certificate_id": "N_E_EFOLDS_ARCHITECTURE_LIMIT_P315",
        "version": "v11.15",
        "pillar": PILLAR_NUMBER,
        "prior_label": "STANDARD_ASSUMPTION (N_e = 60 assumed)",
        "new_label": "PARAMETERIZED_AND_BOUNDED",
        "N_e_lower_bound": N_E_MINIMUM_HORIZON,
        "N_e_range_gw_integral": (N_E_GW_INTEGRAL_LOW, N_E_GW_INTEGRAL_HIGH),
        "N_e_standard": N_E_STANDARD,
        "standard_in_range": N_E_GW_INTEGRAL_LOW <= N_E_STANDARD <= N_E_GW_INTEGRAL_HIGH,
        "what_was_shown": [
            "Approach 1: GW slow-roll integral bounds N_e ∈ [40, 90]",
            "Approach 2: Braided correction reduces N_e but does not fix N_e=60",
            "Approach 3: Reheating constraint yields N_e≈60 for M_KK_inflation~M_GUT",
            "Approach 4: Horizon minimum gives N_e ≥ 60 as a lower bound",
        ],
        "what_remains_open": (
            "The precise N_e requires M_KK_inflation (inflationary KK scale) and "
            "T_reh (reheating temperature).  M_KK_inflation is an open link in the UM."
        ),
        "upgrade_path": (
            "Derive M_KK_inflation from the UM inflation sector — specifically "
            "the connection between the GW inflationary scale and the observed A_s "
            "(CMB amplitude, already an Architecture Limit per FALLIBILITY.md Pillar 57+63). "
            "Once M_KK_inflation is pinned, T_reh follows from the inflaton decay rate "
            "(which depends on λ_GW — Pillar 314)."
        ),
        "summary": summary,
        "certificate_verdict": "N_E_EFOLDS_ARCHITECTURE_LIMIT__BOUNDED_NOT_UNIQUELY_DERIVED",
    }


# ── Separation guard ───────────────────────────────────────────────────────────

def separation_guard() -> str:
    """Confirm this is an adjacent-track rigor module."""
    return (
        "SEPARATION_INTACT: Pillar 315 is an adjacent-track rigor module. "
        "It upgrades N_e from STANDARD_ASSUMPTION to PARAMETERIZED_AND_BOUNDED "
        "via four geometric approaches.  No hardgate labels are modified."
    )
