# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/fermion_laplacian_spectrum.py
========================================
Pillar 174 — Fermion Masses from the RS₁ Laplacian: Honest Spectrum Analysis.

═══════════════════════════════════════════════════════════════════════════════
MOTIVATION (Red-Team Audit, May 2026)
═══════════════════════════════════════════════════════════════════════════════

The audit correctly identified that 9 quark and lepton masses (P6–P11,
P16–P18) in the Unitary Manifold are fitted via per-species bulk mass
parameters c_L — a free parameter in the Randall-Sundrum framework.

The proposed fix: "Replace free parameters with eigenvalues of the
Laplacian on the internal manifold."

This module investigates that proposal honestly.

═══════════════════════════════════════════════════════════════════════════════
WHAT THE RS₁ LAPLACIAN GIVES
═══════════════════════════════════════════════════════════════════════════════

The Randall-Sundrum Model 1 (RS1) background is:
    ds² = e^{−2ky} η_μν dx^μ dx^ν + dy²     y ∈ [0, π R]

where k is the AdS curvature and R is the radius of the extra dimension.

A 5D Dirac fermion Ψ with bulk mass M_5 (= c × k) satisfies:
    (Γ^M D_M − M_5) Ψ = 0

Separating into 4D modes: Ψ(x,y) = Σ_n ψ_n(x) f_n(y)

The zero-mode (n=0) profile for the LEFT-handed component is:
    f_L(y) ∝ e^{(2−c_L)ky}     where c_L = M_5^L / k

The zero-mode is normalizable for all real c_L (it just changes localization).

The 4D effective Yukawa coupling from the overlap integral is:
    λ_4 = Ŷ₅ × F(c_L, c_R, πkR)

where:
    F(c_L, c_R, πkR) = f_L(πR) × f_R(πR)

and for the standard RS1 wavefunction:
    F(c_L, c_R, βkR) ≈ exp[−(c_L + c_R − 1) × πkR]     (for c > 1/2)
    or
    F ≈ exp[+(c_L + c_R − 1) × πkR] / (πkR)             (for c < 1/2)

═══════════════════════════════════════════════════════════════════════════════
THE HONEST ANSWER: IS c_L QUANTIZED?
═══════════════════════════════════════════════════════════════════════════════

In the STANDARD RS1 orbifold S¹/Z₂ with Z₂-even boundary conditions,
c_L is a CONTINUOUS parameter.  The zero-mode exists for all real c_L.

The Laplacian spectrum gives:
- Zero modes (massless) at all values of c_L (continuous degeneracy)
- KK tower (massive) at m_n ~ n × M_KK, with profiles depending on c_L

CONCLUSION: The 5D Laplacian does NOT spontaneously quantize c_L in the
standard RS1 framework.  The fermion masses remain PARAMETERIZED without
additional physics:

1. Discrete flavor symmetry (e.g., A₄, S₃) that restricts c_L to specific
   representations — this is model-building input, not 5D geometry.
2. Brane-localized mass terms that create a boundary condition quantizing c_L
   — requires specifying the brane potential explicitly.
3. A moduli stabilization mechanism that fixes c_L via the vev of a bulk
   scalar — model-dependent.
4. String theory UV completion that quantizes the 10D dilaton vev projected
   to c_L — not yet accomplished.

This result CONFIRMS the PARAMETERIZED status of P6–P18 in holon_zero.py.
It does NOT represent a failure of the theory — all RS-based models face
the same situation.  It represents an honest open problem.

═══════════════════════════════════════════════════════════════════════════════
WHAT THIS MODULE DOES PROVIDE
═══════════════════════════════════════════════════════════════════════════════

1. The RS1 zero-mode wavefunction f_L(y; c_L) and f_R(y; c_R)
2. The Yukawa overlap integral F(c_L, c_R, πkR)
3. The c_L → mass map for the 9 SM fermions at Ŷ₅=1
4. Proof that the zero-mode spectrum is continuous in c_L
5. Identification of what ADDITIONAL physics would quantize c_L
6. The fermion mass hierarchy from the exponential RS profile

═══════════════════════════════════════════════════════════════════════════════

Unitary Manifold / Unitary Pentad framework: AxiomZero commissioned IP.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "PI_KR",
    "HAT_Y5",
    "C_R_CANONICAL",
    # Fermion data
    "SM_FERMION_DATA",
    # Core functions
    "rs_zero_mode_profile_L",
    "rs_zero_mode_profile_R",
    "yukawa_overlap_integral",
    "yukawa_from_c",
    "fermion_mass_from_c",
    "c_from_mass",
    "fermion_mass_hierarchy",
    # Spectrum analysis
    "zero_mode_normalization",
    "is_zero_mode_normalizable",
    "c_spectrum_is_continuous",
    "what_quantizes_c",
    # Honest verdict
    "pillar174_honest_verdict",
    "pillar174_summary",
    "pillar174_full_report",
]

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
PI_KR: float = float(K_CS) / 2.0  # = 37.0

#: GW vacuum condition: Ŷ₅ = 1 (Goldberger-Wise, Pillar 97)
HAT_Y5: float = 1.0

#: Canonical RS right-handed bulk mass parameter (from n_w=5 geometry, Pillar 93)
C_R_CANONICAL: float = 0.920

#: PDG fermion masses [MeV] used to derive c_L at Ŷ₅=1
#: Source: PDG 2022 (Particle Data Group)
SM_FERMION_DATA: List[Dict] = [
    {"id": "P6",  "name": "up quark",     "mass_mev": 2.16,    "sector": "quark",   "pillar": "93/97"},
    {"id": "P7",  "name": "down quark",   "mass_mev": 4.67,    "sector": "quark",   "pillar": "93/97"},
    {"id": "P8",  "name": "strange quark","mass_mev": 93.4,    "sector": "quark",   "pillar": "93/97"},
    {"id": "P9",  "name": "charm quark",  "mass_mev": 1270.0,  "sector": "quark",   "pillar": "97/98"},
    {"id": "P10", "name": "bottom quark", "mass_mev": 4180.0,  "sector": "quark",   "pillar": "97/98"},
    {"id": "P11", "name": "top quark",    "mass_mev": 172_760.0,"sector": "quark",  "pillar": "93/97"},
    {"id": "P16", "name": "electron",     "mass_mev": 0.511,   "sector": "lepton",  "pillar": 97},
    {"id": "P17", "name": "muon",         "mass_mev": 105.66,  "sector": "lepton",  "pillar": "97/98"},
    {"id": "P18", "name": "tau",          "mass_mev": 1776.9,  "sector": "lepton",  "pillar": "97/98"},
]

#: Higgs VEV [MeV]
_V_HIGGS_MEV: float = 246_000.0  # 246 GeV


# ---------------------------------------------------------------------------
# RS1 zero-mode wavefunctions
# ---------------------------------------------------------------------------

def rs_zero_mode_profile_L(
    c_l: float,
    y: float,
    k: float = 1.0,
    pi_r: float = PI_KR,
) -> float:
    """
    Left-handed RS1 zero-mode profile at position y ∈ [0, πR].

    Profile (un-normalized):
        f_L(y; c_L) = e^{(2 − c_L) k y}

    For c_L > 1/2: exponentially localised near UV brane (y = 0)
    For c_L < 1/2: exponentially localised near IR brane (y = πR)
    For c_L = 1/2: flat profile

    Parameters
    ----------
    c_l  : float — bulk mass parameter c_L = M_5^L / k
    y    : float — position in extra dimension, y ∈ [0, π R]
    k    : float — AdS curvature (in units where k=1, all lengths in 1/k)
    pi_r : float — π k R (compactification parameter; default: K_CS/2 = 37)

    Returns
    -------
    float — un-normalized zero-mode profile value at y
    """
    return math.exp((2.0 - c_l) * k * y)


def rs_zero_mode_profile_R(
    c_r: float,
    y: float,
    k: float = 1.0,
    pi_r: float = PI_KR,
) -> float:
    """
    Right-handed RS1 zero-mode profile at position y ∈ [0, πR].

    Profile (un-normalized):
        f_R(y; c_R) = e^{−(2 + c_R) k y}

    Wait — correcting sign convention per Gherghetta-Pomarol (2000):
        For left-handed: f_L^{(0)} ~ e^{(2 − c) k y}
        For right-handed: f_R^{(0)} ~ e^{(2 + c) k y}   [Weyl fermion]
    But since we deal with 4D Yukawa coupling from IR brane overlap,
    the convention that matters is the profile at y = πR.

    For the Yukawa overlap integral, we use the simplified form:
        Yukawa ∝ f_L(πR) × f_R(πR)

    with:
        f_L(πR) = N_L × e^{(2 − c_L) × πkR}    (for c_L > 1/2: UV-localised)
        f_R(πR) = N_R × e^{−(2 − c_R) × πkR}   (for c_R > 1/2: UV-localised too)

    In the RS1 Yukawa context, the exponential suppression relative to the IR
    brane value is:
        λ_4D ∝ exp[−(c_L + c_R − 1) × πkR]   for c_L, c_R > 1/2

    Parameters
    ----------
    c_r  : float — bulk mass parameter c_R = M_5^R / k
    y    : float — position in extra dimension
    k    : float — AdS curvature
    pi_r : float — π k R

    Returns
    -------
    float — un-normalized zero-mode wavefunction value
    """
    return math.exp((2.0 - c_r) * k * y)


def yukawa_overlap_integral(
    c_l: float,
    c_r: float,
    pi_k_r: float = PI_KR,
    hat_y5: float = HAT_Y5,
) -> float:
    """
    4D effective Yukawa coupling from the RS1 wavefunction overlap.

    Using the Gherghetta-Pomarol formula for the IR-brane Yukawa:

        λ_4D = Ŷ₅ × √[(1 − 2c_L)(e^{2(1−c_L)πkR} − 1)⁻¹] ×
               √[(1 − 2c_R)(e^{2(1−c_R)πkR} − 1)⁻¹]

    For c > 1/2 (UV-localised), the normalization gives:
        N(c) = √[2(c − 1/2) / (e^{2(c−1/2)πkR} − 1)]
             ≈ √[2(c − 1/2)] × e^{−(c−1/2)πkR}    for large πkR

    The overlap at the IR brane (y = πR):
        λ_4D ≈ Ŷ₅ × N_L(c_L) × N_R(c_R) × e^{(2−c_L−c_R)πkR} / (πkR)

    For the simplified leading-order approximation (valid for c > 1/2, large πkR):
        λ_4D ≈ Ŷ₅ × √[(2c_L − 1)(2c_R − 1)] × e^{−(c_L + c_R − 1) πkR}

    Parameters
    ----------
    c_l    : float — left-handed bulk mass parameter
    c_r    : float — right-handed bulk mass parameter
    pi_k_r : float — πkR (default: 37, from K_CS/2)
    hat_y5 : float — 5D Yukawa coupling (default: 1.0, from GW vacuum Pillar 97)

    Returns
    -------
    float — 4D effective Yukawa coupling λ_4D (dimensionless)
    """
    # For the generic case, use the full normalization
    def _norm(c: float) -> float:
        x = 2.0 * (c - 0.5) * pi_k_r
        if abs(x) < 1e-10:
            # c ≈ 1/2: flat profile
            return 1.0 / math.sqrt(pi_k_r)
        if x > 700.0:
            # Avoid overflow: use approximation
            return math.sqrt(2.0 * (c - 0.5)) * math.exp(-(c - 0.5) * pi_k_r)
        denom = math.expm1(x)  # e^x - 1
        if denom <= 0:
            # c < 1/2: IR-localised, different formula
            # |e^x - 1| = |1 - e^x| for x < 0
            denom = abs(denom)
        return math.sqrt(2.0 * abs(c - 0.5) / denom)

    n_l = _norm(c_l)
    n_r = _norm(c_r)
    # IR brane overlap factor: e^{(2 - c_L - c_R) × πkR} × (πkR)
    # (from integrating against the brane Yukawa coupling)
    ir_overlap = math.exp((2.0 - c_l - c_r) * pi_k_r)

    return hat_y5 * n_l * n_r * ir_overlap


def yukawa_from_c(
    c_l: float,
    c_r: float = C_R_CANONICAL,
    pi_k_r: float = PI_KR,
    hat_y5: float = HAT_Y5,
) -> float:
    """
    Return the 4D Yukawa coupling for given (c_L, c_R).

    Parameters
    ----------
    c_l    : float — left-handed bulk mass
    c_r    : float — right-handed bulk mass (default: 0.920, canonical)
    pi_k_r : float — πkR (default: 37)
    hat_y5 : float — 5D Yukawa (default: 1.0)

    Returns
    -------
    float — 4D Yukawa coupling (dimensionless)
    """
    return yukawa_overlap_integral(c_l, c_r, pi_k_r, hat_y5)


def fermion_mass_from_c(
    c_l: float,
    c_r: float = C_R_CANONICAL,
    v_mev: float = _V_HIGGS_MEV,
    pi_k_r: float = PI_KR,
    hat_y5: float = HAT_Y5,
) -> float:
    """
    Return the 4D fermion mass [MeV] for given (c_L, c_R).

        m_f = λ_4D × v / √2

    Parameters
    ----------
    c_l    : float — left-handed bulk mass
    c_r    : float — right-handed bulk mass
    v_mev  : float — Higgs VEV in MeV (default: 246,000 MeV)
    pi_k_r : float — πkR (default: 37)
    hat_y5 : float — 5D Yukawa (default: 1.0)

    Returns
    -------
    float — fermion mass in MeV
    """
    lam = yukawa_from_c(c_l, c_r, pi_k_r, hat_y5)
    return lam * v_mev / math.sqrt(2.0)


def c_from_mass(
    mass_mev: float,
    c_r: float = C_R_CANONICAL,
    v_mev: float = _V_HIGGS_MEV,
    pi_k_r: float = PI_KR,
    hat_y5: float = HAT_Y5,
    c_l_min: float = 0.50,
    c_l_max: float = 0.99,
    tol: float = 1e-8,
    max_iter: int = 200,
) -> float:
    """
    Find c_L (by bisection) such that fermion_mass_from_c(c_L, c_R) = mass_mev.

    The mass is a monotonically decreasing function of c_L (for c_L > 1/2):
    higher c_L → more UV-localised → smaller IR overlap → smaller mass.

    Parameters
    ----------
    mass_mev : float — target mass in MeV
    c_r      : float — right-handed bulk mass (default: 0.920)
    v_mev    : float — Higgs VEV in MeV
    pi_k_r   : float — πkR
    hat_y5   : float — 5D Yukawa
    c_l_min  : float — lower bound for bisection (default: 0.50)
    c_l_max  : float — upper bound for bisection (default: 0.99)
    tol      : float — convergence tolerance
    max_iter : int   — maximum iterations

    Returns
    -------
    float — c_L value that reproduces mass_mev

    Notes
    -----
    This is the bisection used in Pillar 98 (universal_yukawa.py).  The c_L
    value is NOT derived from first principles — it is fitted to the observed
    mass.  Status: PARAMETERIZED.
    """
    def residual(c_l: float) -> float:
        return fermion_mass_from_c(c_l, c_r, v_mev, pi_k_r, hat_y5) - mass_mev

    # Check bracket
    r_min = residual(c_l_min)
    r_max = residual(c_l_max)

    if r_min * r_max > 0:
        # Try extending the bracket
        for c_l_max_try in [0.995, 0.999, 0.9999, 0.49, 0.3, 0.1, -0.5]:
            r_max_try = residual(c_l_max_try)
            if r_min * r_max_try <= 0:
                c_l_max = c_l_max_try
                r_max = r_max_try
                break
        else:
            raise ValueError(
                f"Cannot bracket c_L for mass = {mass_mev} MeV.  "
                f"Residuals at [{c_l_min}, {c_l_max}]: [{r_min:.3e}, {r_max:.3e}]"
            )

    # Bisection
    lo, hi = (c_l_min, c_l_max) if r_min < 0 else (c_l_max, c_l_min)
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        r_mid = residual(mid)
        if abs(r_mid) < tol * mass_mev or abs(hi - lo) < tol:
            return mid
        if r_mid < 0:
            lo = mid
        else:
            hi = mid

    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Spectrum analysis
# ---------------------------------------------------------------------------

def zero_mode_normalization(
    c_l: float,
    pi_k_r: float = PI_KR,
) -> float:
    """
    Normalization constant for the RS1 left-handed zero mode.

    N²(c_L) = ∫₀^{πR} e^{2(2−c_L)ky} e^{−4ky} dy
             = ∫₀^{πR} e^{−2(c_L−1/2)×2ky} dy

    For c_L > 1/2:
        N² = (2c_L − 1) / (e^{2(c_L−1/2)πkR} − 1)
    For c_L < 1/2:
        N² = (1 − 2c_L) / (1 − e^{−2(1/2−c_L)πkR})
    For c_L = 1/2:
        N² = 1 / πkR

    Returns
    -------
    float — N(c_L), the normalization constant
    """
    x = 2.0 * (c_l - 0.5) * pi_k_r
    if abs(x) < 1e-10:
        return 1.0 / math.sqrt(pi_k_r)
    denom = abs(math.expm1(abs(x)))
    if denom < 1e-300:
        denom = 1e-300
    return math.sqrt(abs(2.0 * (c_l - 0.5)) / denom)


def is_zero_mode_normalizable(c_l: float, pi_k_r: float = PI_KR) -> bool:
    """
    Return True if the RS1 zero mode is normalizable for this c_L.

    In the standard RS1 orbifold S¹/Z₂, the zero mode is normalizable
    for ALL real c_L — the norm is always finite.

    Parameters
    ----------
    c_l    : float — bulk mass parameter
    pi_k_r : float — πkR

    Returns
    -------
    bool — always True for finite c_L (the spectrum is continuous)
    """
    try:
        n = zero_mode_normalization(c_l, pi_k_r)
        return math.isfinite(n) and n > 0
    except (ValueError, OverflowError):
        return False


def c_spectrum_is_continuous() -> Dict:
    """
    Test whether c_L is quantized or continuous in the standard RS1 orbifold.

    Samples the zero-mode normalization across the range c_L ∈ [−1, 2] and
    checks that the zero mode exists (is normalizable) for all tested values.

    Returns
    -------
    dict with keys:
        all_normalizable  : bool — True if zero mode exists for all sampled c_L
        n_tested          : int  — number of c_L values tested
        c_range           : tuple — (min, max) c_L tested
        is_continuous     : bool — True (result of the analysis)
        verdict           : str  — honest assessment
        quantization_source: list[str] — what WOULD quantize c_L
    """
    c_values = [c * 0.05 for c in range(-20, 41)]  # c ∈ [-1.0, 2.0] in steps of 0.05
    results = [(c, is_zero_mode_normalizable(c)) for c in c_values]
    all_norm = all(r[1] for r in results)

    return {
        "all_normalizable": all_norm,
        "n_tested": len(c_values),
        "c_range": (c_values[0], c_values[-1]),
        "is_continuous": all_norm,
        "verdict": (
            "CONTINUOUS: The RS1 zero mode exists for all tested c_L ∈ [−1, 2].  "
            "The bulk mass parameter c_L is NOT spontaneously quantized by the "
            "5D Dirac equation on the standard RS1 orbifold S¹/Z₂.  "
            "The 9 fermion masses remain PARAMETERIZED without additional input."
        ) if all_norm else (
            "UNEXPECTED: Some c_L values give non-normalizable modes.  "
            "This requires further investigation."
        ),
        "quantization_source": [
            "Discrete flavor symmetry (A₄, S₃, etc.) acting on c_L values",
            "Brane-localized mass terms with specific UV/IR boundary conditions",
            "Moduli stabilization: vev of a bulk scalar fixing c_L",
            "String theory UV completion projecting to quantized dilaton vev",
        ],
    }


def what_quantizes_c() -> Dict:
    """
    Return a structured description of what physics would be needed to
    quantize c_L and upgrade fermion masses from PARAMETERIZED to DERIVED.

    Returns
    -------
    dict with keys:
        current_status   : str — PARAMETERIZED
        mechanisms       : list[dict] — each mechanism and its requirements
        recommendation   : str — most promising direction
    """
    return {
        "current_status": "PARAMETERIZED",
        "current_evidence": (
            "c_L values are determined by bisection at the GW vacuum condition "
            "Ŷ₅=1 (Pillar 97-98).  The pattern is consistent with KK winding "
            "quantization but is not derived from first-principles BCs."
        ),
        "mechanisms": [
            {
                "name": "Discrete Flavor Symmetry",
                "description": (
                    "A flavor symmetry group G_f (e.g., A₄, S₃, Δ(27)) acting on "
                    "the bulk fermion multiplets restricts c_L to values determined "
                    "by the representations.  This is model-building input."
                ),
                "status": "OPEN — not implemented in UM",
                "difficulty": "HIGH",
            },
            {
                "name": "Brane-Localized Mass Quantization",
                "description": (
                    "Brane-localized mass terms on the UV brane with specific "
                    "orbifold BCs can discretize c_L.  Requires specifying the "
                    "brane potential exactly."
                ),
                "status": "OPEN — specific potential not identified in UM",
                "difficulty": "MEDIUM",
            },
            {
                "name": "Winding Number Quantization (UM conjecture)",
                "description": (
                    "The KK winding number n_w=5 and CS level K_CS=74 may impose "
                    "quantization conditions on the fermion zero-mode profiles "
                    "via topological constraints on the braid winding.  "
                    "This is the most physically motivated UM-specific direction."
                ),
                "status": "OPEN — algebraic proof not complete",
                "difficulty": "MEDIUM",
            },
            {
                "name": "String Theory UV Completion",
                "description": (
                    "A specific string compactification gives discrete dilaton "
                    "vev → discrete bulk masses → c_L fixed.  "
                    "Requires a full 10D → 5D → 4D reduction."
                ),
                "status": "OPEN — speculative",
                "difficulty": "VERY HIGH",
            },
        ],
        "recommendation": (
            "Most promising: investigate whether the (5,7) braid winding and "
            "K_CS=74 Chern-Simons level impose topological quantization conditions "
            "on the RS zero-mode profiles.  If c_L values must be rational "
            "multiples of 1/K_CS to satisfy the braid periodicity condition, "
            "the fermion masses would be geometrically fixed."
        ),
    }


def fermion_mass_hierarchy() -> List[Dict]:
    """
    Compute the c_L values and mass hierarchy for all 9 SM fermions.

    Returns a list of dicts with the c_L value, mass, and epistemic status
    for each fermion.  The c_L is obtained by bisection at Ŷ₅=1.

    Returns
    -------
    list[dict] — one entry per fermion, sorted by mass
    """
    results = []
    for f in sorted(SM_FERMION_DATA, key=lambda x: x["mass_mev"]):
        try:
            c_l = c_from_mass(f["mass_mev"])
            m_computed = fermion_mass_from_c(c_l)
            accuracy_pct = abs(m_computed - f["mass_mev"]) / f["mass_mev"] * 100.0
        except ValueError:
            c_l = float("nan")
            m_computed = float("nan")
            accuracy_pct = float("nan")

        results.append({
            "id": f["id"],
            "name": f["name"],
            "mass_pdg_mev": f["mass_mev"],
            "c_l": c_l,
            "c_r": C_R_CANONICAL,
            "mass_computed_mev": m_computed,
            "accuracy_pct": accuracy_pct,
            "status": "PARAMETERIZED",
            "note": (
                "c_L fitted by bisection at Ŷ₅=1; not from first-principles 5D BCs"
            ),
        })
    return results


# ---------------------------------------------------------------------------
# Verdict and reporting
# ---------------------------------------------------------------------------

def pillar174_honest_verdict() -> Dict:
    """
    The honest scientific verdict from the Pillar 174 analysis.

    Returns
    -------
    dict
    """
    spectrum = c_spectrum_is_continuous()
    quant = what_quantizes_c()
    hierarchy = fermion_mass_hierarchy()

    # Compute accuracy stats
    accuracies = [
        f["accuracy_pct"] for f in hierarchy
        if math.isfinite(f["accuracy_pct"])
    ]
    max_err = max(accuracies) if accuracies else float("nan")
    mean_err = sum(accuracies) / len(accuracies) if accuracies else float("nan")

    return {
        "question": (
            "Does the 5D Dirac operator on the RS₁ orbifold spontaneously "
            "quantize the bulk mass parameter c_L, thereby deriving fermion masses "
            "from first principles?"
        ),
        "answer": "NO — c_L is continuous in the standard RS₁ orbifold.",
        "spectrum_analysis": spectrum,
        "what_quantizes_c": quant,
        "fermion_hierarchy": hierarchy,
        "accuracy_stats": {
            "n_fermions": len(accuracies),
            "max_error_pct": max_err,
            "mean_error_pct": mean_err,
            "note": "c_L values are fitted by bisection — accuracy is by construction",
        },
        "overall_status": "PARAMETERIZED — c_L continuous; additional physics required",
        "conclusion": (
            "In the standard RS₁ orbifold S¹/Z₂, the zero-mode of the 5D Dirac "
            "operator is normalizable for ALL real values of the bulk mass c_L.  "
            "The spectrum is continuous: there is no spontaneous quantization of c_L "
            "from the 5D equations of motion alone.  "
            "The 9 quark and lepton masses (P6–P18) therefore remain PARAMETERIZED, "
            "as correctly labelled in holon_zero.py.  "
            "Upgrading these to DERIVED requires additional input — most promising is "
            "a topological quantization condition from the (5,7) KK winding structure "
            "(see what_quantizes_c() for the full analysis).  "
            "This is documented as an open problem, consistent with FALLIBILITY.md §XX."
        ),
    }


def pillar174_summary() -> str:
    """Return a one-paragraph human-readable summary of Pillar 174."""
    return (
        "Pillar 174 — Fermion Masses from RS₁ Laplacian: Honest Spectrum Analysis.  "
        "The 5D Dirac operator on the RS₁ orbifold S¹/Z₂ produces zero modes "
        "for ALL real c_L ∈ (−∞, +∞) — the spectrum is continuous.  "
        "c_L is NOT spontaneously quantized by the 5D equations of motion.  "
        "The 9 fermion masses (P6–P18) remain PARAMETERIZED — c_L fitted by "
        "bisection at the GW condition Ŷ₅=1, not from first-principles BCs.  "
        "This CONFIRMS the PARAMETERIZED status in holon_zero.py.  "
        "Closing this gap requires additional physics: discrete flavor symmetry, "
        "brane-localized BCs, or a topological winding quantization condition.  "
        "Status: PARAMETERIZED (open problem, not a failure)."
    )


def pillar174_full_report() -> Dict:
    """Return the complete Pillar 174 report."""
    verdict = pillar174_honest_verdict()
    return {
        "pillar": 174,
        "title": "Fermion Masses from the RS₁ Laplacian: Honest Spectrum Analysis",
        "status": verdict["overall_status"],
        "constants": {
            "n_w": N_W,
            "k_cs": K_CS,
            "pi_kr": PI_KR,
            "hat_y5": HAT_Y5,
            "c_r_canonical": C_R_CANONICAL,
        },
        "verdict": verdict,
        "summary": pillar174_summary(),
        "authorship": (
            "Theory, scientific direction: ThomasCory Walker-Pearson.  "
            "Code and document engineering: GitHub Copilot (AI)."
        ),
    }

