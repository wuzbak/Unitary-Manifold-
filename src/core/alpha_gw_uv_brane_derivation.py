# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/alpha_gw_uv_brane_derivation.py
==========================================
RS1 UV-brane geometric derivation attempt for α_GW — Pillar 165 extension.

Context (G2 / T2)
------------------
The CMB acoustic peak amplitude is suppressed ×4.2–6.1 vs ΛCDM (Admission 2 in
FALLIBILITY.md, G2 in OBSERVATION_TRACKER, T2 in TRUTH_LAYER.md).

The Casimir interval [4.2×10⁻¹⁰, 4.8×10⁻¹⁰] bounds α_GW from 5D geometry
(src/core/alpha_gw_casimir_closure.py, v10.28).  This module attempts to derive
α_GW from RS1 UV-brane geometry to answer whether the interval can be tightened
to a point value, or whether UV completion is required.

RS1 Geometry Setup
-------------------
The RS1 metric is

    ds² = e^{−2k|y|} η_{μν} dx^μ dx^ν + dy²

with y ∈ [0, πR].  The warp factor at the IR brane is e^{−2πkR}.

In the Unitary Manifold: πkR = 37 (from cc_architecture_limit.PI_KR).

Derivation Attempt
-------------------
Step 1 — KK mass scale from RS1 geometry:
    M_KK ≈ k × exp(−πkR) = M_Pl × exp(−πkR)   [in units where k ≈ M_Pl]
    M_KK / M_Pl = exp(−πkR) = exp(−37)

Step 2 — Casimir energy coefficient from braided-winding:
    c_cas = K_CS × N_W / (24π²) ≈ 1.562

Step 3 — Naive α_GW from UV-brane kinetic term + Casimir:
    α_GW^{geo} ≈ c_cas × (M_KK / M_Pl)^4 = c_cas × exp(−4πkR) = c_cas × exp(−148)
    α_GW^{geo} ≈ 4.33 × 10⁻⁶⁵

    This is ~55 orders of magnitude below the Casimir bound interval
    [4.2×10⁻¹⁰, 4.8×10⁻¹⁰].

Step 4 — Required UV-brane correction factor to reach the interval:
    c_UV_required = (4.5e-10) / alpha_gw_geo ≈ 1.04 × 10⁵⁵

    This is the coefficient of the UV-brane localized kinetic term that is NOT
    determinable from the 5D UM action alone.  It requires either:
    (a) A 10D string embedding specifying the brane intersection structure, or
    (b) An explicit brane-localized graviton kinetic term with coefficient c_UV
        computed from string-theory compactification data.

Honest Verdict
---------------
    Status: OPEN_NARROWED
    The 5D RS1 geometry places alpha_gw_geo ≈ 4.3×10⁻⁶⁵ — outside and far below
    the Casimir interval.  The interval itself is derived from CMB amplitude
    matching (phenomenological), not from first principles.  Full point-value
    closure of α_GW requires the UV-brane localized kinetic term coefficient
    c_UV, which is not computable from 5D UM inputs alone.

CMB-S4 Observability
---------------------
CMB-S4 will measure A_s to ~0.3% precision.  The Casimir interval spans ~14%
in α_GW, corresponding to suppression factors ×4.2–6.1 — a factor-of-1.5 band
all at the same order of magnitude.  Because the suppression mechanism (acoustic
amplitude problem, Admission 2) is not resolved, no value in the interval can be
individually confirmed or ruled out by CMB-S4 without first fixing the acoustic
amplitude derivation from 5D geometry.

Public API
----------
rs1_uv_brane_alpha_gw_attempt() → dict
    Attempt the RS1 geometric derivation; return status and gap analysis.

casimir_alpha_gw_from_geometry() → dict
    Compute α_GW from Casimir coefficient and RS1 warp factor.

cmbs4_alpha_gw_observability() → dict
    Assess CMB-S4 distinguishability of individual values within the interval.

alpha_gw_gap_closure_verdict() → dict
    Honest verdict: OPEN_NARROWED with explicit missing ingredient.
"""
from __future__ import annotations

import math
from typing import Dict

from src.core.alpha_gw_5d_operator_audit import alpha_gw_5d_operator_assessment

__all__ = [
    # Constants
    "PI_KR",
    "K_CS",
    "N_W",
    "ALPHA_GW_LOWER",
    "ALPHA_GW_UPPER",
    # Functions
    "rs1_uv_brane_alpha_gw_attempt",
    "casimir_alpha_gw_from_geometry",
    "cmbs4_alpha_gw_observability",
    "alpha_gw_gap_closure_verdict",
]

# ---------------------------------------------------------------------------
# Constants (mirrored from cc_architecture_limit for self-containment)
# ---------------------------------------------------------------------------

#: RS1 geometry parameter πkR — from cc_architecture_limit.PI_KR
PI_KR: float = 37.0

#: Chern-Simons level — from cc_architecture_limit.K_CS
K_CS: int = 74

#: Primary winding number — from cc_architecture_limit.N_W
N_W: int = 5

#: Casimir bound interval lower edge (from alpha_gw_casimir_closure.ALPHA_GW_LOWER)
ALPHA_GW_LOWER: float = 4.2e-10

#: Casimir bound interval upper edge (from alpha_gw_casimir_closure.ALPHA_GW_UPPER)
ALPHA_GW_UPPER: float = 4.8e-10

#: CMB-S4 projected relative precision on A_s
CMBS4_AS_PRECISION: float = 0.003  # 0.3%

#: Acoustic peak suppression band from Pillar 149
SUPPRESSION_BAND: tuple = (4.2, 6.1)  # (min, max) ×ΛCDM suppression

# ---------------------------------------------------------------------------
# Derived constants (computed at import)
# ---------------------------------------------------------------------------

#: Casimir coefficient: c_cas = K_CS × N_W / (24π²) ≈ 1.562
_CASIMIR_COEFF: float = float(K_CS * N_W) / (24.0 * math.pi ** 2)

#: M_KK^4 / M_Pl^4 = exp(−4πkR) = exp(−148)
_MKK4_OVER_MPL4: float = math.exp(-4.0 * PI_KR)

#: Naive RS1 geometric α_GW estimate
_ALPHA_GW_GEO: float = _CASIMIR_COEFF * _MKK4_OVER_MPL4

#: Midpoint of the Casimir bound interval
_ALPHA_GW_MID: float = 0.5 * (ALPHA_GW_LOWER + ALPHA_GW_UPPER)


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def rs1_uv_brane_alpha_gw_attempt() -> Dict[str, object]:
    """Attempt the RS1 UV-brane geometric derivation of α_GW.

    Follows the four-step derivation in the module docstring.

    Returns
    -------
    dict with keys:
        pi_kr : float
            RS1 parameter πkR = 37.
        k_cs : int
            Chern-Simons level = 74.
        n_w : int
            Winding number = 5.
        casimir_coefficient : float
            c_cas = K_CS × N_W / (24π²) ≈ 1.562.
        mkk_over_mpl : float
            M_KK / M_Pl = exp(−πkR) = exp(−37).
        mkk4_over_mpl4 : float
            (M_KK / M_Pl)^4 = exp(−148).
        alpha_gw_geometric : float
            Naive geometric estimate ≈ 4.3×10⁻⁶⁵.
        alpha_gw_interval_mid : float
            Midpoint of Casimir bound = 4.5×10⁻¹⁰.
        gap_orders_of_magnitude : float
            log10(interval_mid / alpha_gw_geometric) ≈ 55.
        c_uv_required : float
            UV-brane correction factor needed to reach interval mid (~10⁵⁵).
        derivation_status : str
            'INCOMPLETE' — geometric derivation does not reach the interval.
        missing_ingredient : str
            Exact description of the missing UV-brane physics.
    """
    mkk_over_mpl = math.exp(-PI_KR)
    mkk4_over_mpl4 = _MKK4_OVER_MPL4
    alpha_gw_geo = _ALPHA_GW_GEO
    gap_orders = math.log10(_ALPHA_GW_MID) - math.log10(alpha_gw_geo)
    c_uv_required = _ALPHA_GW_MID / alpha_gw_geo
    operator_audit = alpha_gw_5d_operator_assessment()

    return {
        "pi_kr": PI_KR,
        "k_cs": K_CS,
        "n_w": N_W,
        "casimir_coefficient": _CASIMIR_COEFF,
        "mkk_over_mpl": mkk_over_mpl,
        "mkk4_over_mpl4": mkk4_over_mpl4,
        "alpha_gw_geometric": alpha_gw_geo,
        "alpha_gw_interval_lower": ALPHA_GW_LOWER,
        "alpha_gw_interval_upper": ALPHA_GW_UPPER,
        "alpha_gw_interval_mid": _ALPHA_GW_MID,
        "alpha_gw_geo_inside_interval": bool(ALPHA_GW_LOWER <= alpha_gw_geo <= ALPHA_GW_UPPER),
        "gap_orders_of_magnitude": gap_orders,
        "c_uv_required": c_uv_required,
        "derivation_status": "INCOMPLETE",
        "five_d_operator_audit": operator_audit,
        "transfer_law_bottleneck": operator_audit["transfer_audit"]["bottleneck_statement"],
        "best_candidate_lane": operator_audit["best_candidate_lane"],
        "derivation_note": (
            f"RS1 geometry gives α_GW^{{geo}} ≈ {alpha_gw_geo:.3e}, "
            f"which is {gap_orders:.1f} orders of magnitude below the "
            f"Casimir interval [{ALPHA_GW_LOWER:.1e}, {ALPHA_GW_UPPER:.1e}]. "
            "The UV-brane localized kinetic term coefficient c_UV ≈ "
            f"{c_uv_required:.2e} is not determined by the 5D UM action."
        ),
        "missing_ingredient": (
            "UV-brane localized kinetic term coefficient c_UV requires 10D "
            "string embedding or brane intersection calculation; not computable "
            "from 5D UM inputs alone."
        ),
    }


def casimir_alpha_gw_from_geometry(
    k_cs: int = K_CS,
    n_w: int = N_W,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Compute α_GW from the Casimir coefficient and RS1 warp factor.

    This implements Step 3 of the derivation:

        α_GW^{Casimir} = c_cas × exp(−4πkR)

    where c_cas = K_CS × N_W / (24π²).

    Parameters
    ----------
    k_cs : int   Chern-Simons level (default 74).
    n_w  : int   Winding number (default 5).
    pi_kr: float RS1 parameter πkR (default 37).

    Returns
    -------
    dict with keys:
        casimir_coefficient : float   c_cas ≈ 1.562.
        warp_factor_exp     : float   exp(−4πkR).
        alpha_gw_casimir    : float   c_cas × exp(−4πkR).
        inside_interval     : bool    Whether result falls in [4.2e-10, 4.8e-10].
        interval            : tuple   (ALPHA_GW_LOWER, ALPHA_GW_UPPER).
        gap_to_interval_log10 : float log10(α_GW_mid / α_GW_Casimir).
    """
    coeff = float(k_cs * n_w) / (24.0 * math.pi ** 2)
    warp = math.exp(-4.0 * pi_kr)
    alpha_gw_cas = coeff * warp

    inside = bool(ALPHA_GW_LOWER <= alpha_gw_cas <= ALPHA_GW_UPPER)
    if alpha_gw_cas > 0:
        gap_log10 = math.log10(_ALPHA_GW_MID) - math.log10(alpha_gw_cas)
    else:
        gap_log10 = float("inf")

    return {
        "casimir_coefficient": coeff,
        "warp_factor_exp": warp,
        "alpha_gw_casimir": alpha_gw_cas,
        "inside_interval": inside,
        "interval": (ALPHA_GW_LOWER, ALPHA_GW_UPPER),
        "gap_to_interval_log10": gap_log10,
        "status": (
            "INSIDE_INTERVAL" if inside
            else f"OUTSIDE_INTERVAL — {gap_log10:.1f} orders below midpoint"
        ),
    }


def cmbs4_alpha_gw_observability() -> Dict[str, object]:
    """Assess CMB-S4 distinguishability of individual α_GW values in the interval.

    CMB-S4 will measure A_s to ~0.3% precision.  The Casimir interval
    [4.2×10⁻¹⁰, 4.8×10⁻¹⁰] spans ~14% in α_GW.

    However, any value in the interval produces a suppression in the range
    ×4.2–6.1 — all at the same order of magnitude.  Because the acoustic
    amplitude derivation from 5D geometry is not complete (Admission 2), the
    functional mapping α_GW → A_s^{UM} cannot be derived from first principles.
    Without this mapping, CMB-S4 precision cannot be used to pin α_GW within
    the interval.

    Furthermore, the resolution of Admission 2 (deriving R_b and r_s from 5D
    geometry) is a prerequisite for using any CMB precision measurement to
    constrain α_GW individually.

    Returns
    -------
    dict with keys:
        cmbs4_as_precision          : float  0.003 (0.3%).
        interval_fractional_width   : float  ~0.133 (14% width).
        suppression_band            : tuple  (4.2, 6.1).
        suppression_band_ratio      : float  max/min suppression ≈ 1.45.
        individual_values_distinguishable : bool  False.
        reason                      : str    Why not distinguishable.
        prerequisite_for_cmbs4_use  : str    What must be derived first.
    """
    interval_frac_width = (ALPHA_GW_UPPER - ALPHA_GW_LOWER) / _ALPHA_GW_MID
    supp_min, supp_max = SUPPRESSION_BAND
    suppression_ratio = supp_max / supp_min

    return {
        "cmbs4_as_precision": CMBS4_AS_PRECISION,
        "interval_fractional_width": interval_frac_width,
        "suppression_band": SUPPRESSION_BAND,
        "suppression_band_ratio": suppression_ratio,
        "individual_values_distinguishable": False,
        "reason": (
            "All values in [4.2×10⁻¹⁰, 4.8×10⁻¹⁰] produce acoustic peak "
            f"suppression in the range ×{supp_min:.1f}–×{supp_max:.1f} — a "
            f"factor-of-{suppression_ratio:.2f} band at the same order of "
            "magnitude.  CMB-S4 0.3% precision on A_s cannot distinguish "
            "individual α_GW values within this interval until the 5D "
            "geometric derivation of the acoustic amplitude is complete "
            "(Admission 2, FALLIBILITY.md)."
        ),
        "prerequisite_for_cmbs4_use": (
            "Derivation of the baryon-to-photon ratio R_b and sound horizon r_s "
            "from the 5D geometry is required before CMB-S4 precision can pin "
            "α_GW to a point value within the interval."
        ),
        "cmbs4_can_confirm_suppression_band": True,
        "cmbs4_can_pin_alpha_gw_to_point": False,
    }


def alpha_gw_gap_closure_verdict() -> Dict[str, object]:
    """Honest verdict on G2/T2: can α_GW be pinned to a point value?

    Synthesises the RS1 geometric derivation attempt, Casimir analysis, and
    CMB-S4 observability assessment into a single closure verdict.

    Returns
    -------
    dict with keys:
        status : str
            'OPEN_NARROWED' — the interval [4.2e-10, 4.8e-10] is established
            but α_GW cannot be pinned to a point value from 5D UM inputs.
        derivation_status : str
            'INCOMPLETE' — RS1 geometry gives α_GW^{geo} ≈ 4.3×10⁻⁶⁵,
            ~55 orders below the interval.
        casimir_interval : tuple
            (4.2e-10, 4.8e-10).
        alpha_gw_geometric_estimate : float
            Naive RS1 Casimir estimate.
        gap_to_interval_log10 : float
            Orders of magnitude between geometric estimate and interval midpoint.
        missing_ingredient : str
            EXACT description of the physics needed for full closure.
        cmbs4_distinguishable : bool
            False — interval values not individually distinguishable without
            Admission 2 resolution.
        conclusion : str
            Plain-language summary for TRUTH_LAYER.md / OBSERVATION_TRACKER.
    """
    rs1 = rs1_uv_brane_alpha_gw_attempt()
    cmbs4 = cmbs4_alpha_gw_observability()
    operator_audit = rs1["five_d_operator_audit"]

    return {
        "status": "OPEN_NARROWED",
        "derivation_status": "INCOMPLETE",
        "casimir_interval": (ALPHA_GW_LOWER, ALPHA_GW_UPPER),
        "alpha_gw_geometric_estimate": rs1["alpha_gw_geometric"],
        "gap_to_interval_log10": rs1["gap_orders_of_magnitude"],
        "c_uv_required_to_close": rs1["c_uv_required"],
        "missing_ingredient": (
            "UV-brane localized kinetic term coefficient c_UV requires 10D "
            "string embedding or brane intersection calculation; not computable "
            "from 5D UM inputs alone."
        ),
        "five_d_operator_status": operator_audit["status"],
        "present_transfer_law_survives": operator_audit["present_transfer_law_survives"],
        "best_candidate_lane": operator_audit["best_candidate_lane"],
        "five_d_operator_conclusion": operator_audit["conclusion"],
        "cmbs4_distinguishable": cmbs4["individual_values_distinguishable"],
        "cmbs4_can_pin_alpha_gw": cmbs4["cmbs4_can_pin_alpha_gw_to_point"],
        "string_uv_completion_required": True,
        "conclusion": (
            "The RS1 UV-brane geometric derivation places α_GW^{geo} ≈ "
            f"{rs1['alpha_gw_geometric']:.2e}, which is "
            f"{rs1['gap_orders_of_magnitude']:.1f} orders of magnitude below "
            f"the Casimir interval [{ALPHA_GW_LOWER:.1e}, {ALPHA_GW_UPPER:.1e}]. "
            "The interval is established from CMB amplitude matching "
            "(phenomenological), not from first principles.  "
            f"{operator_audit['transfer_audit']['bottleneck_statement']}  "
            "A point-value derivation still requires c_UV from 10D string embedding.  "
            "Status: OPEN_NARROWED (G2 remains open in OBSERVATION_TRACKER and "
            "T2 remains open in TRUTH_LAYER.md)."
        ),
    }
