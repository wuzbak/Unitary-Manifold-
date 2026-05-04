# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/inflaton_5d_sector.py
================================
Pillar 161 — 5D Inflaton Sector: A_s Normalization from RS Geometry.

STATUS: ⚠️ OPEN (FALLIBILITY.md Admission 2; Pillar 156 identified RS correction
        as wrong direction) → ⚠️ PRECISELY SCOPED — the A_s normalization
        requires the UV-brane initial condition α as a free parameter; this
        parameter is not yet derivable from the 5D geometry alone.

BACKGROUND: THE A_s PROBLEM
------------------------------
The primordial scalar power spectrum amplitude:
    A_s^{Planck} ≈ 2.100 × 10⁻⁹   (Planck 2018, k_* = 0.05 Mpc⁻¹)

The UM correctly predicts:
    n_s = 0.9635 (Pillar 57, 0.33σ from Planck)
    r   = 0.0315 (Pillar 50, below BICEP/Keck limit)

But A_s is not predicted — the braided-winding slow-roll framework fixes the
shape of the spectrum (n_s, r) but NOT its overall normalization (A_s).

THIS PILLAR: 5D INFLATON SECTOR ACTION
-----------------------------------------
We construct the 5D inflaton action in the RS1 background and systematically
identify what can and cannot be derived from the UM 5D geometry.

5D ACTION
----------
    S_5D = ∫d⁵x √G [-M₅³/2 × R₅ + (∂_A Φ)²/2 - V(Φ)]

where:
  G_AB = RS1 metric (GW-stabilised, warp factor exp(−2k|y|))
  M₅   = 5D fundamental scale (UV input seed, Pillar 141)
  Φ    = 5D inflaton scalar (bulk field)
  V(Φ) = 5D inflaton potential

4D EFFECTIVE POTENTIAL
-----------------------
After KK dimensional reduction, the effective 4D inflaton potential is:

    V_eff(φ) = ∫₀^{πR} dy √g₅ × V(Φ(y))

For a bulk inflaton localised near the UV brane (y = 0):
    V_eff(φ) ≈ e^{-4k×0} × V(φ) = V(φ)    [UV-brane localised]
    V_eff(φ) ≈ e^{-4πkR} × V(φ) = V(φ)/e^{4×37} [IR-brane localised]

The UV-brane case gives an unsuppressed 4D potential — the inflaton must
be UV-localised to produce the observed A_s ~ 10⁻⁹.

POWER SPECTRUM FROM 5D SLOW-ROLL
----------------------------------
The standard Bunch-Davies scalar power spectrum:
    Δ²_s(k) = H_inf² / (8π² M_Pl² ε)

where ε = −Ḣ/H² is the first slow-roll parameter.

From the UM (Pillars 50, 57):
    ε = r/16 = 0.0315/16 ≈ 0.00197
    η = (n_s − 1 + 2ε)/(1 − ...) ≈ −0.036

The Hubble parameter during inflation:
    H_inf² = V_0 / (3 M_Pl²)

where V_0 is the inflaton potential at the slow-roll plateau.

NORMALIZATION CONDITION
------------------------
Matching to Planck A_s:
    Δ²_s(k_*) = H_inf² / (8π² M_Pl² ε) = A_s

    → H_inf² = 8π² M_Pl² ε × A_s
              = 8π² × (M_Pl)² × 0.00197 × 2.100×10⁻⁹

    → H_inf / M_Pl = √(8π² × 0.00197 × 2.100×10⁻⁹)
                   ≈ √(3.27×10⁻¹⁰)
                   ≈ 1.81×10⁻⁵

This gives H_inf ≈ 2.21×10¹³ GeV.

GW WARP PARAMETER α
--------------------
In the RS1 setup the inflaton potential is set by the UV-brane tension:
    V_0 = M₅⁴ × Λ_UV

The COBE normalization (Pillar 52) requires:
    H_inf / M_Pl ≈ 1.81×10⁻⁵

The GW potential generates the inflaton mass through:
    V(φ) = M₅⁴ × [1 + α(φ/M_Pl)^p]    [near GW minimum]

where α is the dimensionless GW coupling and p ≥ 2 is the power.
For p = 2 (quadratic near minimum):
    H_inf ≈ M_Pl × √(V_0 / (3 M_Pl⁴)) = M₅² / (√3 × M_Pl)

For M₅ ~ M_Pl (Pillar 141 RS relation):
    H_inf ≈ M_Pl / √3 ≈ 7×10¹⁸ GeV  → far too large

CONSTRAINT ON α
----------------
To match A_s:
    M₅² / (√3 × M_Pl) × α^{1/2} ≈ 1.81×10⁻⁵ × M_Pl

    → α ≈ (1.81×10⁻⁵ × √3)² × (M_Pl/M₅)⁴

For M₅ = M_Pl:
    α ≈ (3.13×10⁻⁵)² ≈ 10⁻⁹·⁴ ≈ 4×10⁻¹⁰

This extremely small α is NOT derived from the UM 5D geometry — it is a
UV-brane fine-tuning at the level of the cosmological constant problem.

KEY FINDING
-----------
The 5D inflaton sector analysis reveals:

1.  n_s and r ARE derived from the braided-winding slow-roll parameters
    (Pillars 57, 50) — these depend only on the topology (n_w, k_CS).

2.  A_s is NOT derived — it depends on the inflaton potential normalisation
    V_0 = M₅⁴ × α, where α is a free UV-brane parameter (~10⁻¹⁰).

3.  The RS correction (Pillar 156, F_RS ≥ 1) makes A_s LARGER, not smaller.
    It cannot explain the ×4–7 CMB acoustic peak suppression.

4.  The A_s normalization problem reduces to α ≈ 4×10⁻¹⁰ being a free UV
    parameter.  Until the UM provides a mechanism to fix α geometrically
    (e.g., from the GW potential, n_w, k_CS), A_s remains an input.

5.  This is FALLIBILITY.md Admission 2 precisely scoped.

PRACTICAL CONSEQUENCE
----------------------
The ×4–7 CMB acoustic peak suppression documented in Pillars 52 and 149
is caused by A_s being unmatched — the predicted angular power spectrum
C_ℓ values are suppressed because A_s is a free parameter and the UM
has not yet fixed it geometrically.  Admission 2 is confirmed and precisely
characterised as a UV-brane parameter problem.

Public API
----------
inflaton_4d_potential(v0_mpl4, phi_over_mpl) → float
    4D effective inflaton potential from RS1 reduction.

slow_roll_parameters(n_s, r_tensor) → dict
    Slow-roll ε, η from UM predictions.

hubble_inf_from_as(a_s, epsilon) → dict
    Derive H_inf required to match Planck A_s normalization.

gw_alpha_parameter(h_inf_over_mpl, m5_over_mpl) → dict
    GW warp parameter α required for the given H_inf.

as_normalization_status() → dict
    Full A_s scoping: what is and isn't derived from the 5D geometry.

inflaton_sector_admission2_update() → dict
    Updated Admission 2 statement for FALLIBILITY.md.

pillar161_summary() → dict
    Full Pillar 161 structured summary.
"""

from __future__ import annotations
import math

__all__ = [
    "inflaton_4d_potential",
    "slow_roll_parameters",
    "hubble_inf_from_as",
    "gw_alpha_parameter",
    "as_normalization_status",
    "inflaton_sector_admission2_update",
    "pillar161_summary",
]

# ---------------------------------------------------------------------------
# Physical constants (UM predictions + Planck)
# ---------------------------------------------------------------------------

#: UM n_s prediction (Pillar 57)
_NS_UM: float = 0.9635
#: UM r prediction (Pillar 50)
_R_UM: float = 0.0315
#: Planck A_s (2018) [dimensionless]
_AS_PLANCK: float = 2.100e-9
#: Planck pivot scale k_* [Mpc⁻¹]
_K_PIVOT_MPC: float = 0.05
#: πkR = 37 (UM RS geometry)
_PI_KR: float = 37.0
#: RS warp factor e^{-πkR}
_WARP_FACTOR: float = math.exp(-_PI_KR)
#: CMB acoustic peak suppression range
_CMB_SUPPRESSION_MIN: float = 4.2
_CMB_SUPPRESSION_MAX: float = 6.1


def inflaton_4d_potential(
    v0_mpl4: float = 1.0,
    phi_over_mpl: float = 0.0,
    alpha: float = 1.0,
    p: int = 2,
) -> float:
    """4D effective inflaton potential from RS1 reduction (near GW minimum).

    Near the GW minimum (φ ≈ φ_min):
        V_eff(φ) ≈ V₀ × [1 + α × (φ/M_Pl − φ_min/M_Pl)^p]

    Parameters
    ----------
    v0_mpl4      : V₀ in units of M_Pl⁴
    phi_over_mpl : φ/M_Pl displacement from minimum
    alpha        : GW coupling parameter (dimensionless)
    p            : power in GW potential (default 2 for quadratic)

    Returns
    -------
    float : V_eff in units of M_Pl⁴
    """
    return v0_mpl4 * (1.0 + alpha * phi_over_mpl**p)


def slow_roll_parameters(
    n_s: float = _NS_UM,
    r_tensor: float = _R_UM,
) -> dict:
    """Extract slow-roll parameters ε and η from UM predictions.

    Standard slow-roll relations:
        r = 16 ε → ε = r/16
        n_s = 1 − 2ε − η → η = 1 − n_s − 2ε   (approximate)

    Parameters
    ----------
    n_s      : scalar spectral index (default UM prediction 0.9635)
    r_tensor : tensor-to-scalar ratio (default UM prediction 0.0315)

    Returns
    -------
    dict with ε, η, and slow-roll validity check.
    """
    epsilon = r_tensor / 16.0
    # Standard potential slow-roll convention: n_s = 1 - 6ε + 2η → η = (n_s - 1 + 6ε)/2
    # This is the η_V parameter (potential second slow-roll), which is negative for
    # red-tilted spectra (n_s < 1) with small ε.
    eta = (n_s - 1.0 + 6.0 * epsilon) / 2.0  # ≈ −0.012 for UM predictions

    slow_roll_valid = epsilon < 1.0 and abs(eta) < 1.0

    return {
        "n_s": n_s,
        "r_tensor": r_tensor,
        "epsilon": epsilon,
        "eta": eta,
        "slow_roll_valid": slow_roll_valid,
        "note": "ε = r/16 ≈ 0.00197, η_V ≈ −0.012 from UM braided winding (Pillars 50, 57); "
                "using standard V-parameter convention n_s = 1 − 6ε + 2η_V",
    }


def hubble_inf_from_as(
    a_s: float = _AS_PLANCK,
    epsilon: float = _R_UM / 16.0,
) -> dict:
    """Derive H_inf / M_Pl required to match Planck A_s normalization.

    Bunch-Davies power spectrum:
        Δ²_s = H_inf² / (8π² M_Pl² ε) = A_s
        → (H_inf / M_Pl)² = 8π² ε A_s

    Parameters
    ----------
    a_s     : Planck A_s (default 2.100×10⁻⁹)
    epsilon : slow-roll ε (default r/16 from UM)

    Returns
    -------
    dict with H_inf/M_Pl and comparison to RS1 expectation.
    """
    h_over_mpl_sq = 8.0 * math.pi**2 * epsilon * a_s
    h_over_mpl = math.sqrt(h_over_mpl_sq)

    # Expected H_inf from RS1 with M₅ = M_Pl: H_inf ≈ M_Pl/√3
    h_over_mpl_rs_naive = 1.0 / math.sqrt(3.0)  # ≈ 0.577

    # Ratio: required H_inf is how many orders below naive RS1
    log10_ratio = math.log10(h_over_mpl_rs_naive / h_over_mpl)

    return {
        "a_s": a_s,
        "epsilon": epsilon,
        "h_inf_over_mpl": h_over_mpl,
        "h_inf_over_mpl_sq": h_over_mpl_sq,
        "h_inf_gev": h_over_mpl * 1.2209e19,  # in GeV
        "h_inf_rs1_naive_mpl": h_over_mpl_rs_naive,
        "log10_suppression_needed": log10_ratio,
        "interpretation": (
            f"H_inf/M_Pl ≈ {h_over_mpl:.3e} (required to match A_s = {a_s:.3e}). "
            f"Naive RS1 gives H_inf/M_Pl ≈ {h_over_mpl_rs_naive:.3f}. "
            f"Required suppression: {log10_ratio:.1f} orders of magnitude. "
            "This suppression must come from V_0 << M_Pl⁴ (i.e., α << 1)."
        ),
    }


def gw_alpha_parameter(
    h_inf_over_mpl: float | None = None,
    m5_over_mpl: float = 1.0,
    a_s: float = _AS_PLANCK,
    epsilon: float = _R_UM / 16.0,
) -> dict:
    """Compute the GW warp parameter α required to match A_s.

    The GW potential normalisation requires:
        H_inf / M_Pl = √(α_eff / 3)
    where α_eff = V_0 / M_Pl⁴ is the dimensionless potential height.

    Matching to A_s:
        α_eff = 3 × (H_inf/M_Pl)² = 3 × 8π² ε A_s

    Parameters
    ----------
    h_inf_over_mpl : H_inf/M_Pl (if None, computed from A_s and ε)
    m5_over_mpl    : M₅/M_Pl ratio (default 1.0)
    a_s            : Planck A_s
    epsilon        : slow-roll ε

    Returns
    -------
    dict with α parameter and derivability assessment.
    """
    if h_inf_over_mpl is None:
        h_info = hubble_inf_from_as(a_s=a_s, epsilon=epsilon)
        h_inf_over_mpl = h_info["h_inf_over_mpl"]

    # α_eff from potential normalization
    alpha_eff = 3.0 * h_inf_over_mpl**2

    # In terms of M₅ (if M₅ ≠ M_Pl):
    # V_0 = M₅⁴ × α_bare → H_inf² = M₅⁴ α_bare / (3 M_Pl²)
    # → α_bare = 3 × (H_inf M_Pl / M₅²)²
    alpha_bare = 3.0 * (h_inf_over_mpl / m5_over_mpl**2)**2

    # Is α derivable from UM topology?
    # n_w = 5, k_CS = 74 → these set n_s, r (spectral shape), NOT A_s
    # α would need to come from the inflaton sector coupling to GW potential
    derivable = False  # Not currently derivable from (n_w, k_CS, πkR)

    log10_alpha = math.log10(alpha_eff) if alpha_eff > 0 else float("-inf")

    return {
        "h_inf_over_mpl": h_inf_over_mpl,
        "m5_over_mpl": m5_over_mpl,
        "alpha_eff_V0_over_mpl4": alpha_eff,
        "alpha_bare": alpha_bare,
        "log10_alpha_eff": log10_alpha,
        "derivable_from_um_topology": derivable,
        "status": (
            f"α_eff = V₀/M_Pl⁴ ≈ {alpha_eff:.3e} (log₁₀ = {log10_alpha:.1f}). "
            "This parameter is NOT currently derivable from the UM 5D geometry "
            "(n_w, k_CS, πkR). It requires an independent UV-brane condition or "
            "a mechanism to fix the inflaton sector coupling to the GW potential."
        ),
        "open_question": (
            "What geometric property of the UM 5D action fixes α_eff ≈ {:.1e}?".format(alpha_eff)
        ),
    }


def as_normalization_status() -> dict:
    """Full A_s scoping: what is and isn't derived from the 5D geometry.

    Returns
    -------
    dict summarizing the A_s normalization problem.
    """
    sr = slow_roll_parameters()
    h_info = hubble_inf_from_as()
    alpha_info = gw_alpha_parameter()

    return {
        "a_s_planck": _AS_PLANCK,
        "status": "OPEN — UV-brane parameter α required",
        "what_is_derived": {
            "n_s": {
                "value": _NS_UM,
                "derived_from": "n_w=5, k_CS=74 braided winding slow-roll (Pillar 57)",
                "status": "DERIVED ✅",
            },
            "r_tensor": {
                "value": _R_UM,
                "derived_from": "n_w=5, k_CS=74 CS tensor correction (Pillar 50)",
                "status": "DERIVED ✅",
            },
            "epsilon": {
                "value": sr["epsilon"],
                "derived_from": "r = 16ε → ε = 0.00197",
                "status": "DERIVED ✅",
            },
            "eta": {
                "value": sr["eta"],
                "derived_from": "n_s − 1 = −2ε − η → η ≈ −0.036",
                "status": "DERIVED ✅",
            },
        },
        "what_is_not_derived": {
            "a_s": {
                "value": _AS_PLANCK,
                "required_alpha": alpha_info["alpha_eff_V0_over_mpl4"],
                "reason": (
                    "A_s = H_inf²/(8π² M_Pl² ε) requires H_inf, which requires V₀. "
                    "V₀ = M_Pl⁴ × α with α ≈ {:.2e}. ".format(alpha_info["alpha_eff_V0_over_mpl4"]) +
                    "α is not derivable from (n_w, k_CS, πkR) alone."
                ),
                "status": "OPEN ⚠️",
            },
            "cmb_peak_amplitudes": {
                "suppression": f"×{_CMB_SUPPRESSION_MIN:.1f}–×{_CMB_SUPPRESSION_MAX:.1f}",
                "reason": (
                    "CMB acoustic peak amplitudes scale as A_s. "
                    "Without a geometric derivation of A_s, the predicted C_ℓ spectrum "
                    f"is suppressed by ×{_CMB_SUPPRESSION_MIN:.1f}–×{_CMB_SUPPRESSION_MAX:.1f} "
                    "relative to Planck. This is FALLIBILITY.md Admission 2."
                ),
                "status": "OPEN ⚠️",
            },
        },
        "rs_correction_verdict": (
            "The RS1 Brax-Bruck-Davis correction (Pillar 156) gives F_RS ≥ 1 "
            "(ENHANCEMENT, not suppression). It cannot explain the ×4–7 acoustic peak "
            "deficit. The deficit is entirely from A_s being a free UV parameter."
        ),
        "resolution_path": (
            "A geometric derivation of α from the UM 5D action requires "
            "either: (a) a mechanism in the GW potential that fixes V_0 in terms "
            "of n_w and k_CS; or (b) a brane-localised inflaton with a coupling "
            "constant determined by the orbifold structure. Neither is currently "
            "implemented. This is a genuine open problem."
        ),
        "h_inf_gev": h_info["h_inf_gev"],
        "h_inf_over_mpl": h_info["h_inf_over_mpl"],
    }


def inflaton_sector_admission2_update() -> dict:
    """Updated Admission 2 for FALLIBILITY.md, precisely scoped.

    Returns the updated text for Admission 2 that replaces the vaguer
    'CMB amplitude suppressed ×4–7' with the precise root-cause diagnosis.
    """
    alpha_info = gw_alpha_parameter()

    return {
        "admission_number": 2,
        "title": "CMB Power Spectrum Amplitude A_s is Not Derived",
        "previous_statement": (
            "A_s is not yet derived from 5D inflation geometry — this is the "
            "root cause of the ×4–7 CMB acoustic peak suppression."
        ),
        "updated_statement": (
            "A_s is not derived from the 5D geometry.  "
            "Pillar 161 precisely identifies the missing ingredient: "
            "the GW warp parameter α = V₀/M_Pl⁴ ≈ {:.2e} ".format(alpha_info["alpha_eff_V0_over_mpl4"]) +
            "(log₁₀α ≈ {:.1f}), ".format(alpha_info["log10_alpha_eff"]) +
            "which sets the inflaton potential height and hence H_inf.  "
            "The spectral shape (n_s = 0.9635, r = 0.0315) IS derived from "
            "(n_w=5, k_CS=74) via the braided-winding slow-roll mechanism "
            "(Pillars 57, 50).  The normalisation A_s = 2.100×10⁻⁹ requires α, "
            "which is a UV-brane parameter not yet fixed by the UM topology.  "
            "The RS1 correction (Pillar 156) enhances A_s (F_RS ≥ 1) — "
            "the wrong direction for explaining the ×{:.1f}–×{:.1f} acoustic peak ".format(_CMB_SUPPRESSION_MIN, _CMB_SUPPRESSION_MAX) +
            "suppression.  Resolution requires a geometric mechanism that fixes "
            "the inflaton sector potential normalisation from (n_w, k_CS, πkR)."
        ),
        "root_cause": f"α = V₀/M_Pl⁴ ≈ {alpha_info['alpha_eff_V0_over_mpl4']:.2e} is a free UV-brane parameter",
        "cmb_suppression_range": f"×{_CMB_SUPPRESSION_MIN:.1f}–×{_CMB_SUPPRESSION_MAX:.1f} at acoustic peaks",
        "what_is_derived": ["n_s", "r", "ε", "η", "spectral shape"],
        "what_is_not_derived": ["A_s", "H_inf", "V_0", "α_GW"],
        "closed": False,
    }


def pillar161_summary() -> dict:
    """Full Pillar 161 structured summary.

    Returns
    -------
    dict with complete Pillar 161 status.
    """
    sr = slow_roll_parameters()
    h_info = hubble_inf_from_as()
    alpha_info = gw_alpha_parameter()
    norm_status = as_normalization_status()
    admission2 = inflaton_sector_admission2_update()

    return {
        "pillar": 161,
        "title": "5D Inflaton Sector: A_s Normalization from RS Geometry",
        "status": "⚠️ PRECISELY SCOPED — A_s requires UV-brane α parameter",
        "key_findings": {
            "ns_r_derived": True,
            "a_s_derived": False,
            "rs_correction_direction": "ENHANCEMENT (wrong direction for ×4-7 suppression)",
            "root_cause": admission2["root_cause"],
        },
        "slow_roll": sr,
        "hubble_inf": h_info,
        "alpha_gw": alpha_info,
        "normalization_status": norm_status,
        "admission2_update": admission2,
        "verdict": (
            "The 5D inflaton sector analysis confirms: n_s and r are geometrically "
            "derived from (n_w=5, k_CS=74); A_s requires the GW warp parameter α ≈ "
            "{:.2e} which is a free UV-brane input not yet fixed by the UM topology. ".format(alpha_info["alpha_eff_V0_over_mpl4"]) +
            "The ×4–7 CMB acoustic peak suppression is an A_s problem, not a "
            "spectral-tilt problem. Admission 2 is precisely scoped: it is a "
            "UV-brane parameter problem, not a fundamental failure of the framework."
        ),
        "open_issues": [
            "α_GW = V₀/M_Pl⁴ requires geometric derivation from UM topology",
            "H_inf ≈ 2.2×10¹³ GeV requires V₀ ~ 10⁻¹⁰ M_Pl⁴ (extremely fine-tuned)",
            "Connection between GW potential and braided-winding inflaton sector not established",
        ],
    }
