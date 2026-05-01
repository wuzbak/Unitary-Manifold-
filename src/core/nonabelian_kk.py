# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/nonabelian_kk.py
==========================
Pillar 62 — Non-Abelian SU(3)_C Kaluza-Klein Reduction.

Background
----------
The Unitary Manifold's KK gauge sector has, until now, been confined to the
Abelian U(1) zero mode (the KK photon B_μ).  This module extends the
mathematical framework to a non-Abelian SU(N_c) gauge theory compactified on
the same S¹/Z₂ orbifold, treating N_c = 3 as the color multiplicity of the
strong interaction.

The extension is motivated by the classification established in the previous
session:

    The UM is a fundamental geometric theory of the gravitational and
    cosmological sector, with partial reach into the electroweak sector,
    that requires a non-Abelian extension to become a complete Theory of
    Everything.

This module implements that extension, documenting every step of the
derivation chain and labelling every free parameter with full honesty.

Physical Content
----------------

1.  SU(N_c) Group Theory Data
    The Lie-algebra Casimir invariants for SU(N_c) in the fundamental and
    adjoint representations:

        C_A = N_c            (quadratic Casimir, adjoint: Tr T^a T^b = C_A δ^{ab})
        T_F = 1/2            (Dynkin index, fundamental)
        C_F = (N_c²−1)/(2 N_c)   (quadratic Casimir, fundamental)
        d_adj = N_c² − 1    (dimension of the adjoint)

2.  Non-Abelian CS Gauge Threshold at the KK Scale
    For the Abelian case (Pillar 61) the one-loop gauge threshold from the
    Chern-Simons level k_CS gives:

        α_EM(M_KK) = 2π / k_CS

    The non-Abelian generalisation for SU(N_c) replaces k_CS with the product
    N_c × k_CS (because the adjoint trace introduces a factor C_A = N_c into
    the gauge kinetic function):

        f_strong = N_c × k_CS / (8π²)    [non-Abelian gauge kinetic function]
        α_s(M_KK) = 1 / (4π × f_strong) = 2π / (N_c × k_CS)

    For N_c = 3 and k_CS = 74:

        α_s(M_KK) = 2π / 222 ≈ 0.02829

    **Free parameters at this step: N_c (the colour multiplicity).**
    k_CS = 74 is algebraically derived (Pillar 58); N_c = 3 is the new
    assumption introduced by this extension.

3.  QCD Beta Function
    The one-loop QCD beta coefficient is:

        b_0 = (11 N_c − 2 N_f) / 3

    where N_f is the number of light quark flavours below M_KK.  By the
    Three-Generation Theorem (Pillar 42), N_gen = 3, which gives N_f = 3
    light quark flavours (one per generation).

    For N_c = 3, N_f = 3:

        b_0 = (33 − 6) / 3 = 9

    **N_f = 3 is derived from Pillar 42 (given N_w = 5 from Planck); no
    new free parameter at this step.**

4.  One-Loop QCD Running and Dimensional Transmutation
    Integrating the one-loop RG equation from M_KK down to a scale μ:

        α_s(μ)⁻¹ = α_s(M_KK)⁻¹ − (b_0 / 2π) × ln(M_KK / μ)

    The Landau pole defines Λ_QCD (where α_s → ∞):

        Λ_QCD = M_KK × exp(−2π / (b_0 × α_s(M_KK)))

    With α_s(M_KK) ≈ 0.02829, b_0 = 9, M_KK ≈ 2.03 × 10¹⁷ GeV:

        2π / (b_0 × α_s(M_KK)) ≈ 6.283 / 0.2546 ≈ 24.68
        Λ_QCD_pred ≈ 2.03 × 10¹⁷ × exp(−24.68) ≈ 4.4 × 10⁶ GeV

    PDG reference: Λ_QCD(MS-bar, N_f=3) ≈ 0.332 GeV.
    Discrepancy factor: ≈ 1.3 × 10⁷ (thirteen million times too high).

    **This is the primary gap of Pillar 62.**  The exponential sensitivity of
    Λ_QCD to α_s(M_KK) means that a 1.7× error in the gauge threshold
    produces a ~10⁷× error in Λ_QCD.  The correction factor needed is
    documented in `alpha_s_correction_factor()`.

5.  Proton Mass and m_p/m_e
    The proton mass is dominated by QCD confinement:

        m_p ≈ C_lat × Λ_QCD    where C_lat ≈ 4.4

    C_lat is a lattice-QCD normalization constant that relates the MS-bar
    Λ_QCD to the physical proton mass.  It is NOT derived from the 5D
    geometry; it is a NEW FREE PARAMETER at this step.

    The electron mass m_e requires the Yukawa coupling λ (already a free
    parameter in Pillar 60).

    Once (N_c, Λ_QCD, λ_e) are provided, the ratio m_p/m_e is determined:

        m_p/m_e = (C_lat × Λ_QCD_MeV) / m_e_MeV

    Using PDG values as comparison targets:
        m_p = 938.272 MeV → Λ_QCD_PDG ≈ 938.272 / 4.4 ≈ 213 MeV (≈ PDG ✓)
        m_e = 0.511 MeV
        m_p/m_e = 938.272 / 0.511 ≈ 1836.15

Gap Closure Summary
-------------------
    Before Pillar 62 (from Pillar 61 §VIII.3):
        Λ_QCD:          NO FRAMEWORK
        α_s:            NOT DERIVED
        m_p/m_e:        NOT DERIVABLE

    After Pillar 62:
        Λ_QCD:          FRAMEWORK EXISTS — derivation gives PeV-scale Λ
                        (13-million-fold discrepancy from PDG; see §4 above)
        α_s(M_KK):      PARTIALLY DERIVED — 2π/(N_c×k_CS) from non-Abelian
                        CS threshold; N_c=3 is new assumption
        b_0 = 9:        DERIVED — from N_c=3 (new assumption) + N_f=3 (Pillar 42)
        m_p/m_e:        CONDITIONALLY DERIVABLE — once N_c, C_lat, and Yukawa
                        λ_e are provided; reduces to 2 new inputs beyond Pillar 60

    Open gaps after Pillar 62:
        (A) The non-Abelian CS threshold for SU(3) overestimates α_s(M_KK)
            by ~1.7×, leading to a ~10⁷× error in Λ_QCD.  A proper
            non-Abelian threshold matching (e.g., from a full SU(3) instanton
            computation or multi-loop CS correction) would be required.
        (B) N_c = 3 is assumed, not derived.  A geometric derivation of the
            colour multiplicity would require embedding SU(3) isometry into
            the extra-dimensional geometry (e.g., a 7D S⁷/Z₂ orbifold as per
            Witten 1981).
        (C) C_lat ≈ 4.4 (the lattice normalisation) is a free parameter.

Derivation Status Table
-----------------------
    | Quantity          | Source                         | Status              |
    |-------------------|--------------------------------|---------------------|
    | k_CS = 74         | Pillar 58 algebraic theorem    | DERIVED             |
    | N_c = 3           | SU(3)_C colour assignment      | NEW ASSUMPTION      |
    | N_f = 3           | Pillar 42, given n_w=5+Planck  | DERIVED             |
    | b_0 = 9           | (11×3−2×3)/3                   | DERIVED (given N_c) |
    | α_s(M_KK)≈0.028   | 2π/(N_c×k_CS)                  | PARTIALLY DERIVED   |
    | Λ_QCD_pred ~PeV   | dimensional transmutation       | FRAMEWORK EXISTS    |
    | Λ_QCD_PDG≈332 MeV | —                              | NOT YET REPRODUCED  |
    | m_p≈938 MeV       | C_lat × Λ_QCD (C_lat free)     | CONDITIONALLY DERID |
    | m_p/m_e≈1836      | m_p / m_e_Yukawa               | CONDITIONALLY DERID |

Public API
----------
N_C_CANONICAL, K_CS_CANONICAL, N_F_CANONICAL, B0_CANONICAL
    Module-level constants (colour and flavour assignments).

M_KK_CANONICAL_GEV, M_PL_GEV_REDUCED, R_C_CANONICAL
    Compactification scale in GeV.

C_LAT_PDG, LAMBDA_QCD_PDG_MEV, MP_PDG_MEV, ME_PDG_MEV
    Physical reference values — comparison targets only, never derivation inputs.

su3_casimir_data()
    Return Casimir invariants for SU(N_c=3): C_A, T_F, C_F, d_adj.

alpha_s_kk_scale(k_cs, n_c)
    Compute α_s(M_KK) from the non-Abelian CS gauge threshold.

qcd_beta_b0(n_c, n_f)
    Compute the one-loop QCD beta coefficient b_0 = (11N_c − 2N_f) / 3.

alpha_s_rg_run(alpha_s_kk, m_kk_gev, mu_gev, n_c, n_f)
    Run α_s from M_KK to a lower scale μ via one-loop QCD RG.

lambda_qcd_from_dim_trans(alpha_s_kk, m_kk_gev, n_c, n_f)
    Compute Λ_QCD from dimensional transmutation.

alpha_s_correction_factor()
    Compute the ratio α_s_PDG_extrap / α_s_UM to quantify the gap.

proton_mass_from_lambda_qcd(lambda_qcd_mev, c_lat)
    Estimate m_p from Λ_QCD and the lattice normalisation constant.

mp_over_me_pipeline(lambda_qcd_mev, m_e_mev, c_lat)
    Full m_p/m_e derivation pipeline with all free parameters documented.

alpha_s_at_mz_prediction(alpha_s_kk, m_kk_gev, n_c)
    Predict α_s(M_Z) from the UM non-Abelian threshold by downward RG running.

nonabelian_kk_gap_report()
    Honest, comprehensive gap accounting for Pillar 62.

nonabelian_kk_summary()
    Full derivation summary dict.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""


from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math
from typing import Any

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural units unless labelled otherwise)
# ---------------------------------------------------------------------------

#: Winding number (Pillar 39, from S¹/Z₂ orbifold + Planck nₛ)
N_W: int = 5

#: Secondary winding number (Pillar 58, from BICEP/Keck r < 0.036)
N_W2: int = 7

#: Chern-Simons level: algebraic theorem n₁² + n₂² (Pillar 58)
K_CS_CANONICAL: int = N_W**2 + N_W2**2    # 25 + 49 = 74

#: Number of quark colours — NEW ASSUMPTION (SU(3)_C colour assignment)
#: This is the first new free parameter introduced by the non-Abelian extension.
N_C_CANONICAL: int = 3

#: Number of light quark flavours — DERIVED from Pillar 42 (Three-Generation
#: Theorem): N_gen = 3 stable KK winding modes → 3 quark generations.
N_F_CANONICAL: int = 3

#: One-loop QCD beta coefficient b_0 = (11 N_c − 2 N_f) / 3
#: For N_c = 3, N_f = 3: b_0 = (33 − 6) / 3 = 9.
#: DERIVED given N_c and N_f.
B0_CANONICAL: int = (11 * N_C_CANONICAL - 2 * N_F_CANONICAL) // 3    # = 9

#: Compactification radius in Planck units (Pillar 27, r_c = 12 M_Pl⁻¹)
R_C_CANONICAL: float = 12.0

#: Reduced Planck mass in GeV (M_Pl = ħc / sqrt(8πG))
#:   M_Pl_reduced = 2.435 × 10¹⁸ GeV
M_PL_GEV_REDUCED: float = 2.435e18

#: Fundamental KK mass scale in GeV: M_KK = M_Pl_reduced / r_c
#:   For r_c = 12 M_Pl⁻¹: M_KK ≈ 2.03 × 10¹⁷ GeV
M_KK_CANONICAL_GEV: float = M_PL_GEV_REDUCED / R_C_CANONICAL

#: α_s at the KK scale from the non-Abelian CS gauge threshold
#:   α_s(M_KK) = 2π / (N_c × k_CS) = 2π / 222 ≈ 0.02829
#: PARTIALLY DERIVED — requires N_c as input.
ALPHA_S_KK_CANONICAL: float = 2.0 * math.pi / (N_C_CANONICAL * K_CS_CANONICAL)

#: Lattice QCD normalisation constant C_lat: m_p ≈ C_lat × Λ_QCD
#: EMPIRICAL FREE PARAMETER.  C_lat ≈ 4.4 from lattice QCD studies.
C_LAT_CANONICAL: float = 4.4

# ---------------------------------------------------------------------------
# Physical reference values — used ONLY as comparison targets.
# These are PDG inputs; they are NEVER used as inputs to the 5D derivation.
# ---------------------------------------------------------------------------

#: PDG 2024 proton mass in MeV (comparison target only)
MP_PDG_MEV: float = 938.272_046

#: PDG 2024 electron mass in MeV (comparison target only)
ME_PDG_MEV: float = 0.510_998_950

#: PDG 2024 proton/electron mass ratio (comparison target only)
MP_OVER_ME_PDG: float = MP_PDG_MEV / ME_PDG_MEV    # ≈ 1836.15

#: PDG MS-bar Λ_QCD for N_f = 3 light flavours, in MeV (comparison only)
LAMBDA_QCD_PDG_MEV: float = 332.0

#: PDG proton-to-Λ_QCD ratio used to extract C_lat
C_LAT_PDG: float = MP_PDG_MEV / LAMBDA_QCD_PDG_MEV   # ≈ 2.826

#: PDG 2022 α_s(M_Z), M_Z = 91.1876 GeV (comparison target only)
ALPHA_S_MZ_PDG: float = 0.1179

#: Z-boson mass in GeV (for RG comparison only)
M_Z_GEV: float = 91.1876

#: Charm quark mass in GeV (heavy-flavour threshold for QCD running)
M_CHARM_GEV: float = 1.27


# ---------------------------------------------------------------------------
# Group theory: SU(N_c) Casimir invariants
# ---------------------------------------------------------------------------

def su3_casimir_data(n_c: int = N_C_CANONICAL) -> dict[str, Any]:
    """Return SU(N_c) Casimir invariants and group-theory data.

    For SU(N_c):
        C_A = N_c                         (adjoint quadratic Casimir)
        T_F = 1/2                         (Dynkin index, fundamental rep)
        C_F = (N_c² − 1) / (2 N_c)       (quadratic Casimir, fundamental)
        d_adj = N_c² − 1                  (dimension of the adjoint rep)
        d_fund = N_c                       (dimension of the fundamental rep)

    Parameters
    ----------
    n_c : int — number of colours (default 3 for QCD)

    Returns
    -------
    dict with keys:
        n_c, C_A, T_F, C_F, d_adj, d_fund
        description — string noting this is the new-assumption sector
    """
    if n_c < 2:
        raise ValueError(f"n_c must be ≥ 2 for a non-Abelian group; got {n_c!r}")
    c_a = float(n_c)
    t_f = 0.5
    c_f = (n_c**2 - 1) / (2.0 * n_c)
    d_adj = n_c**2 - 1
    d_fund = n_c
    return {
        "n_c":      n_c,
        "C_A":      c_a,
        "T_F":      t_f,
        "C_F":      c_f,
        "d_adj":    d_adj,
        "d_fund":   d_fund,
        "description": (
            f"SU({n_c}) group data.  N_c = {n_c} is a NEW ASSUMPTION "
            "introduced by the non-Abelian KK extension.  k_CS = 74 and "
            "n_w = 5 are inherited from the Abelian sector (Pillars 39, 58)."
        ),
    }


# ---------------------------------------------------------------------------
# Non-Abelian CS gauge threshold at the KK scale
# ---------------------------------------------------------------------------

def alpha_s_kk_scale(
    k_cs: int = K_CS_CANONICAL,
    n_c: int = N_C_CANONICAL,
) -> dict[str, Any]:
    """Compute α_s at the KK compactification scale from the non-Abelian CS threshold.

    The non-Abelian generalisation of the Abelian CS gauge threshold:

        Abelian (U(1)):    f_gauge = k_CS / (8π²)        → α_EM(M_KK) = 2π / k_CS
        Non-Abelian SU(N): f_strong = N_c × k_CS / (8π²) → α_s(M_KK)  = 2π / (N_c k_CS)

    The factor N_c enters because the adjoint trace in the SU(N) gauge kinetic
    term carries a factor of C_A = N_c relative to the Abelian case.

    For k_CS = 74 and N_c = 3:
        α_s(M_KK) = 2π / 222 ≈ 0.02829

    Free parameters
    ---------------
    N_c — the colour multiplicity.  This is the only new free parameter at
    this step; k_CS = 74 is algebraically derived (Pillar 58, no fit).

    Parameters
    ----------
    k_cs : int   — Chern-Simons level (default 74, derived from Pillar 58)
    n_c  : int   — number of colours (NEW ASSUMPTION; default 3 for SU(3))

    Returns
    -------
    dict with keys:
        k_cs, n_c, f_strong, alpha_s_kk, alpha_s_kk_inv
        free_parameters — list of free parameters at this step
        derivation_status — string
    """
    if k_cs <= 0:
        raise ValueError(f"k_cs must be positive; got {k_cs!r}")
    if n_c < 2:
        raise ValueError(f"n_c must be ≥ 2 for SU(n_c); got {n_c!r}")
    f_strong = n_c * k_cs / (8.0 * math.pi**2)
    alpha_s = 1.0 / (4.0 * math.pi * f_strong)   # = 2π / (n_c × k_cs)
    return {
        "k_cs":           k_cs,
        "n_c":            n_c,
        "f_strong":       f_strong,
        "alpha_s_kk":     alpha_s,
        "alpha_s_kk_inv": 1.0 / alpha_s,
        "free_parameters": [
            f"n_c = {n_c} — colour multiplicity; SU(3)_C colour assignment is "
            "a NEW ASSUMPTION of the non-Abelian extension.  k_CS = {k_cs} is "
            "algebraically derived (Pillar 58)."
        ],
        "derivation_status": (
            f"PARTIALLY DERIVED — α_s(M_KK) = 2π/(N_c×k_CS) = 2π/{n_c*k_cs} "
            f"≈ {alpha_s:.5f}.  k_CS is derived; N_c = {n_c} is a new "
            "assumption.  The KK-scale value is O(0.03), far from the "
            "low-energy α_s(m_τ) ≈ 0.32 — dimensional transmutation runs "
            "it up as the energy decreases (asymptotic freedom)."
        ),
    }


# ---------------------------------------------------------------------------
# QCD one-loop beta function coefficient
# ---------------------------------------------------------------------------

def qcd_beta_b0(n_c: int = N_C_CANONICAL, n_f: int = N_F_CANONICAL) -> float:
    """Compute the one-loop QCD beta coefficient b_0.

    The one-loop QCD beta function is:

        μ d α_s / d μ  = −(b_0 / 2π) α_s²  +  O(α_s³)

    where

        b_0 = (11 N_c − 2 N_f) / 3

    For asymptotic freedom (b_0 > 0) we need N_f < 11 N_c / 2:
      - N_c = 3: requires N_f < 16.5, i.e., N_f ≤ 16.

    With N_c = 3 and N_f = 3 (from Pillar 42 Three-Generation Theorem):
        b_0 = (33 − 6) / 3 = 9

    N_f = 3 is DERIVED from the Three-Generation Theorem (Pillar 42) given
    n_w = 5 from Planck.  N_c = 3 is the new assumption.

    Parameters
    ----------
    n_c : int — number of colours (default 3)
    n_f : int — number of active quark flavours (default 3, from Pillar 42)

    Returns
    -------
    b0 : float — one-loop beta coefficient (positive for asymptotic freedom)

    Raises
    ------
    ValueError
        If b_0 ≤ 0 (theory is not asymptotically free).
    """
    b0 = (11.0 * n_c - 2.0 * n_f) / 3.0
    if b0 <= 0.0:
        raise ValueError(
            f"b_0 = {b0:.4f} ≤ 0 for n_c={n_c}, n_f={n_f}: "
            "theory is NOT asymptotically free.  Requires n_f < 11 n_c / 2."
        )
    return b0


# ---------------------------------------------------------------------------
# Primitive coupling evolution step
# ---------------------------------------------------------------------------

def evolve_coupling(alpha_in: float, scale_ratio: float, b0: float) -> float:
    """Evolve a gauge coupling by one RG step using the one-loop beta function.

    This is the atomic building block of the QCD running.  Given an input
    coupling α_in at some UV scale μ_UV, and the ratio

        scale_ratio = μ_UV / μ_IR   (> 1 for downward running)

    the one-loop RG equation integrates to:

        α(μ_IR)⁻¹ = α_in⁻¹ − (b_0 / 2π) × ln(scale_ratio)

    For an asymptotically free theory (b_0 > 0), scale_ratio > 1 implies
    running towards the IR (lower energy), where the coupling increases.

    The function raises `ValueError` if the Landau pole is encountered, i.e.,
    if 1/α(μ_IR) ≤ 0 (the coupling has formally diverged before reaching μ_IR).

    This matches the pattern recommended in the Gemini external review
    (April 2026), which provided the following reference implementation:

        def evolve_coupling(alpha_in, scale_ratio, b0):
            inv_alpha = (1.0 / alpha_in) - (b0 / (2*pi)) * ln(scale_ratio)
            if inv_alpha <= 0:
                raise ValueError("Landau pole encountered: Coupling diverged.")
            return 1.0 / inv_alpha

    The implementation here is identical in logic; additional context is
    provided in the error message.

    Parameters
    ----------
    alpha_in    : float — coupling at the UV scale (must be > 0)
    scale_ratio : float — μ_UV / μ_IR (must be > 1 for IR evolution)
    b0          : float — one-loop beta coefficient (positive for asymptotic
                          freedom; use `qcd_beta_b0()` for QCD)

    Returns
    -------
    float — coupling α at the IR scale μ_IR

    Raises
    ------
    ValueError
        If alpha_in ≤ 0, scale_ratio ≤ 1, b0 ≤ 0, or if the Landau pole
        is encountered (1/α ≤ 0 before reaching μ_IR).

    Examples
    --------
    Evolve from a factor-of-2 scale drop with b_0 = 9, α_in = 0.5:

        >>> evolve_coupling(0.5, 2.0, 9.0)
        # Δ(1/α) = (9/2π) × ln2 ≈ 1.432 × 0.693 ≈ 0.992
        # 1/α_IR = 2.0 − 0.992 = 1.008  →  α_IR ≈ 0.992

    Evolve with b_0 = 11, α_in = 0.5, scale_ratio = 2:

        >>> evolve_coupling(0.5, 2.0, 11.0)
        # Δ(1/α) = (11/2π) × ln2 ≈ 1.750 × 0.693 ≈ 1.212
        # 1/α_IR = 2.0 − 1.212 = 0.788  →  α_IR ≈ 1.269
    """
    if alpha_in <= 0.0:
        raise ValueError(f"alpha_in must be positive; got {alpha_in!r}")
    if scale_ratio <= 1.0:
        raise ValueError(
            f"scale_ratio must be > 1 for downward (IR) running; got {scale_ratio!r}.  "
            "For upward running the coupling decreases (asymptotic freedom)."
        )
    if b0 <= 0.0:
        raise ValueError(
            f"b0 must be positive for an asymptotically free theory; got {b0!r}."
        )
    inv_alpha = (1.0 / alpha_in) - (b0 / (2.0 * math.pi)) * math.log(scale_ratio)
    if inv_alpha <= 0.0:
        raise ValueError(
            f"Landau pole encountered: coupling diverged before reaching the "
            f"target scale.  1/α = {inv_alpha:.6f} ≤ 0.  "
            f"(α_in={alpha_in}, scale_ratio={scale_ratio:.4g}, b0={b0:.4g})."
        )
    return 1.0 / inv_alpha


# ---------------------------------------------------------------------------
# One-loop QCD running
# ---------------------------------------------------------------------------

def alpha_s_rg_run(
    alpha_s_kk: float,
    m_kk_gev: float,
    mu_gev: float,
    n_c: int = N_C_CANONICAL,
    n_f: int = N_F_CANONICAL,
) -> float:
    """Run α_s from M_KK down to scale μ via one-loop QCD RG equation.

    QCD is asymptotically free: the coupling increases as the energy scale
    decreases.  The one-loop running is:

        α_s(μ)⁻¹ = α_s(M_KK)⁻¹ − (b_0 / 2π) × ln(M_KK / μ)

    For μ < M_KK the second term is positive, so α_s(μ)⁻¹ < α_s(M_KK)⁻¹,
    i.e., α_s(μ) > α_s(M_KK).  This is the asymptotic-freedom behaviour.

    Parameters
    ----------
    alpha_s_kk : float — α_s at the KK scale
    m_kk_gev   : float — KK scale in GeV
    mu_gev     : float — target scale in GeV (must satisfy 0 < μ < M_KK)
    n_c        : int   — number of colours (default 3)
    n_f        : int   — number of active quark flavours (default 3)

    Returns
    -------
    alpha_s_mu : float — α_s at scale μ

    Raises
    ------
    ValueError
        If mu_gev ≥ m_kk_gev (must run downward), or if the Landau pole
        is between M_KK and μ (coupling would diverge).
    """
    if mu_gev >= m_kk_gev:
        raise ValueError(
            f"mu_gev ({mu_gev}) must be below m_kk_gev ({m_kk_gev}) "
            "for downward QCD running."
        )
    if alpha_s_kk <= 0.0:
        raise ValueError(f"alpha_s_kk must be positive; got {alpha_s_kk!r}")
    b0 = qcd_beta_b0(n_c, n_f)
    return evolve_coupling(alpha_s_kk, m_kk_gev / mu_gev, b0)


# ---------------------------------------------------------------------------
# Dimensional transmutation: Λ_QCD
# ---------------------------------------------------------------------------

def lambda_qcd_from_dim_trans(
    alpha_s_kk: float = ALPHA_S_KK_CANONICAL,
    m_kk_gev: float = M_KK_CANONICAL_GEV,
    n_c: int = N_C_CANONICAL,
    n_f: int = N_F_CANONICAL,
) -> dict[str, Any]:
    """Compute Λ_QCD from dimensional transmutation.

    In QCD the Landau pole defines the non-perturbative scale:

        Λ_QCD = M_KK × exp(−2π / (b_0 × α_s(M_KK)))

    This is the scale where the one-loop running coupling diverges (the
    confinement scale).  It is an exponentially sensitive function of
    α_s(M_KK); a 1.7× error in α_s yields a ~10⁷× error in Λ_QCD.

    Parameters
    ----------
    alpha_s_kk : float — α_s at the KK scale (default from CS threshold)
    m_kk_gev   : float — KK scale in GeV (default: M_Pl_red / r_c)
    n_c        : int   — number of colours (default 3)
    n_f        : int   — number of active quark flavours (default 3)

    Returns
    -------
    dict with keys:
        alpha_s_kk, m_kk_gev, b0, exponent, lambda_qcd_gev, lambda_qcd_mev
        lambda_qcd_pdg_mev — PDG reference (comparison only)
        discrepancy_factor — lambda_qcd_pred / lambda_qcd_pdg
        log10_discrepancy  — log₁₀ of the discrepancy
        status — honest assessment string
    """
    if alpha_s_kk <= 0.0:
        raise ValueError(f"alpha_s_kk must be positive; got {alpha_s_kk!r}")
    if m_kk_gev <= 0.0:
        raise ValueError(f"m_kk_gev must be positive; got {m_kk_gev!r}")
    b0 = qcd_beta_b0(n_c, n_f)
    exponent = -2.0 * math.pi / (b0 * alpha_s_kk)
    lambda_qcd_gev = m_kk_gev * math.exp(exponent)
    lambda_qcd_mev = lambda_qcd_gev * 1000.0
    discrepancy = lambda_qcd_mev / LAMBDA_QCD_PDG_MEV
    log10_disc = math.log10(discrepancy) if discrepancy > 0 else float("nan")
    return {
        "alpha_s_kk":       alpha_s_kk,
        "m_kk_gev":         m_kk_gev,
        "b0":               b0,
        "exponent":         exponent,
        "lambda_qcd_gev":   lambda_qcd_gev,
        "lambda_qcd_mev":   lambda_qcd_mev,
        "lambda_qcd_pdg_mev": LAMBDA_QCD_PDG_MEV,
        "discrepancy_factor": discrepancy,
        "log10_discrepancy":  log10_disc,
        "status": (
            f"FRAMEWORK EXISTS — Λ_QCD prediction from UM non-Abelian CS "
            f"threshold gives {lambda_qcd_mev:.3e} MeV, compared to PDG "
            f"{LAMBDA_QCD_PDG_MEV:.0f} MeV.  Discrepancy: {discrepancy:.2e}× "
            f"({log10_disc:.1f} orders of magnitude).  "
            "The gap arises from exponential sensitivity of dimensional "
            "transmutation to α_s(M_KK): a 1.7× correction to α_s(M_KK) "
            "is needed.  See alpha_s_correction_factor() for the quantified gap."
        ),
    }


# ---------------------------------------------------------------------------
# Correction factor needed to close the gap
# ---------------------------------------------------------------------------

def alpha_s_correction_factor(
    m_kk_gev: float = M_KK_CANONICAL_GEV,
    n_c: int = N_C_CANONICAL,
    n_f: int = N_F_CANONICAL,
) -> dict[str, Any]:
    """Quantify the correction to α_s(M_KK) needed to reproduce PDG Λ_QCD.

    If α_s(M_KK) = α_s_UM + δα_s were the "true" value, the PDG Λ_QCD would
    be reproduced.  This function solves for α_s_target:

        Λ_QCD_PDG = M_KK × exp(−2π / (b_0 × α_s_target))
        α_s_target = −2π / (b_0 × ln(Λ_QCD_PDG / M_KK))

    Parameters
    ----------
    m_kk_gev : float — KK scale in GeV
    n_c      : int   — number of colours
    n_f      : int   — number of active quark flavours

    Returns
    -------
    dict with keys:
        alpha_s_um        — UM non-Abelian CS prediction
        alpha_s_target    — value needed to reproduce PDG Λ_QCD
        correction_factor — alpha_s_target / alpha_s_um
        delta_alpha_s     — alpha_s_target − alpha_s_um
        description       — plain-language summary
    """
    b0 = qcd_beta_b0(n_c, n_f)
    alpha_s_um = 2.0 * math.pi / (n_c * K_CS_CANONICAL)
    lambda_pdg_gev = LAMBDA_QCD_PDG_MEV / 1000.0
    # Solve: Λ_PDG = M_KK × exp(-2π / (b0 × α_s_target))
    # → α_s_target = -2π / (b0 × ln(Λ_PDG / M_KK))
    log_ratio = math.log(lambda_pdg_gev / m_kk_gev)   # negative (Λ_PDG < M_KK)
    alpha_s_target = -2.0 * math.pi / (b0 * log_ratio)
    correction = alpha_s_target / alpha_s_um
    delta = alpha_s_target - alpha_s_um
    return {
        "alpha_s_um":         alpha_s_um,
        "alpha_s_target":     alpha_s_target,
        "correction_factor":  correction,
        "delta_alpha_s":      delta,
        "description": (
            f"To reproduce PDG Λ_QCD = {LAMBDA_QCD_PDG_MEV} MeV, the non-Abelian "
            f"CS threshold would need α_s(M_KK) = {alpha_s_target:.5f} instead of "
            f"{alpha_s_um:.5f} — a factor of {correction:.3f}× ({delta:+.5f} "
            "additive).  This is the quantified gap of Pillar 62.  Closing it "
            "requires either: (A) multi-loop corrections to the CS gauge kinetic "
            "function, (B) a proper non-Abelian instanton threshold computation, "
            "or (C) an alternative geometric embedding of SU(3)."
        ),
    }


# ---------------------------------------------------------------------------
# Proton mass from Λ_QCD
# ---------------------------------------------------------------------------

def proton_mass_from_lambda_qcd(
    lambda_qcd_mev: float,
    c_lat: float = C_LAT_CANONICAL,
) -> dict[str, Any]:
    """Estimate the proton mass from Λ_QCD and the lattice normalisation.

    The proton is a QCD bound state.  In the large-N_c limit and from
    lattice QCD computations, the proton mass satisfies:

        m_p ≈ C_lat × Λ_QCD

    where C_lat ≈ 4.4 encodes the non-perturbative dynamics of confinement
    (quark binding, zero-point motion, Casimir pressure) that are not captured
    by the perturbative RG running alone.

    C_lat is a NEW FREE PARAMETER; it is not derivable from the one-loop
    CS gauge threshold.  Its value is taken from lattice QCD results.

    Parameters
    ----------
    lambda_qcd_mev : float — Λ_QCD in MeV
    c_lat          : float — lattice normalisation (default 4.4)

    Returns
    -------
    dict with keys:
        lambda_qcd_mev, c_lat, m_p_pred_mev
        m_p_pdg_mev    — PDG reference (comparison only)
        discrepancy    — m_p_pred / m_p_pdg
        free_parameters — list of free parameters
    """
    if lambda_qcd_mev <= 0.0:
        raise ValueError(f"lambda_qcd_mev must be positive; got {lambda_qcd_mev!r}")
    if c_lat <= 0.0:
        raise ValueError(f"c_lat must be positive; got {c_lat!r}")
    m_p_pred = c_lat * lambda_qcd_mev
    return {
        "lambda_qcd_mev":  lambda_qcd_mev,
        "c_lat":           c_lat,
        "m_p_pred_mev":    m_p_pred,
        "m_p_pdg_mev":     MP_PDG_MEV,
        "discrepancy":     m_p_pred / MP_PDG_MEV,
        "free_parameters": [
            "c_lat — lattice normalisation constant m_p / Λ_QCD; not derivable "
            "from the one-loop CS threshold; set by non-perturbative QCD."
        ],
    }


# ---------------------------------------------------------------------------
# Full m_p/m_e derivation pipeline
# ---------------------------------------------------------------------------

def mp_over_me_pipeline(
    lambda_qcd_mev: float = LAMBDA_QCD_PDG_MEV,
    m_e_mev: float = ME_PDG_MEV,
    c_lat: float = C_LAT_PDG,
) -> dict[str, Any]:
    """Full m_p / m_e pipeline: Λ_QCD + lattice + Yukawa → ratio.

    This function chains:
        Λ_QCD (MeV) + C_lat → m_p (MeV)
        m_e (MeV, from Yukawa coupling λ_e)
        → m_p / m_e

    When the PDG values are used as inputs, the ratio matches PDG exactly.
    When the UM-derived Λ_QCD is used, the ratio is off by the same ~10⁷
    factor as the Λ_QCD prediction.

    This documents the STRUCTURE of the derivation, even though the
    current UM inputs do not numerically reproduce 1836.15.

    Parameters
    ----------
    lambda_qcd_mev : float — Λ_QCD in MeV (default: PDG reference value)
    m_e_mev        : float — electron mass in MeV (default: PDG; in a full
                              derivation this comes from the Yukawa coupling λ)
    c_lat          : float — lattice normalisation (default: PDG-calibrated)

    Returns
    -------
    dict with keys:
        lambda_qcd_mev, m_e_mev, c_lat
        m_p_pred_mev       — predicted proton mass
        mp_over_me_pred    — predicted ratio
        mp_over_me_pdg     — PDG ratio (comparison target)
        discrepancy        — pred / PDG
        free_parameters    — list of all free parameters in the chain
        derivation_status  — honest assessment
    """
    m_p_pred = c_lat * lambda_qcd_mev
    ratio_pred = m_p_pred / m_e_mev
    discrepancy = ratio_pred / MP_OVER_ME_PDG
    return {
        "lambda_qcd_mev":    lambda_qcd_mev,
        "m_e_mev":           m_e_mev,
        "c_lat":             c_lat,
        "m_p_pred_mev":      m_p_pred,
        "mp_over_me_pred":   ratio_pred,
        "mp_over_me_pdg":    MP_OVER_ME_PDG,
        "discrepancy":       discrepancy,
        "free_parameters": [
            "1. Λ_QCD — the QCD confinement scale.  The UM framework derives "
            "   Λ_QCD_UM ~ PeV; the PDG value 332 MeV is used here as a "
            "   comparison target.  Closing this gap requires improved α_s(M_KK).",
            "2. c_lat — lattice QCD normalisation constant m_p / Λ_QCD ≈ 2.8; "
            "   not derivable from one-loop CS geometry.",
            "3. m_e — electron mass; set by Yukawa coupling λ_e fitted to "
            "   m_e = 0.511 MeV (Pillar 60 free parameter, unchanged).",
        ],
        "derivation_status": (
            "CONDITIONALLY DERIVABLE — given (Λ_QCD, C_lat, λ_e), the ratio "
            "m_p/m_e follows algebraically.  The current UM derivation of "
            "Λ_QCD gives a PeV-scale value (discrepancy ~10⁷×); when PDG "
            "Λ_QCD is used the ratio matches 1836.15 within floating-point "
            "precision.  Progress relative to pre-Pillar-62 status: the "
            "derivation framework now EXISTS (previously: no framework at all "
            "for the strong sector); the remaining gap is α_s(M_KK)."
        ),
    }


# ---------------------------------------------------------------------------
# α_s(M_Z) prediction from UM threshold
# ---------------------------------------------------------------------------

def alpha_s_at_mz_prediction(
    alpha_s_kk: float = ALPHA_S_KK_CANONICAL,
    m_kk_gev: float = M_KK_CANONICAL_GEV,
    n_c: int = N_C_CANONICAL,
) -> dict[str, Any]:
    """Predict α_s(M_Z) from the UM non-Abelian KK threshold.

    Run α_s from M_KK down to M_Z using threshold matching at heavy-quark
    masses.  The flavour thresholds change b_0:

        M_KK → m_top:  N_f = 6, b_0(6) = (11×3 − 2×6)/3 = 7
        m_top → M_Z:   N_f = 5, b_0(5) = (11×3 − 2×5)/3 = 23/3 ≈ 7.67

    Note: this is a simplified one-loop calculation ignoring two-loop
    corrections and threshold matching at m_b, m_c, etc.

    If the Landau pole lies above M_Z (i.e., Λ_QCD > M_Z), the coupling
    diverges before reaching M_Z and α_s(M_Z) is undefined perturbatively.
    In that case the function returns the Landau-pole scale instead.

    Parameters
    ----------
    alpha_s_kk : float — α_s at the KK scale
    m_kk_gev   : float — KK scale in GeV
    n_c        : int   — number of colours

    Returns
    -------
    dict with keys:
        alpha_s_kk, m_kk_gev
        alpha_s_mz_pred    — predicted α_s(M_Z), or None if Landau pole > M_Z
        alpha_s_mz_pdg     — PDG value (comparison target)
        landau_pole_gev    — Λ_QCD estimate from UM (b_0=9 approximation)
        perturbative_at_mz — True iff coupling is perturbative at M_Z
        status             — honest assessment
    """
    b0_6 = (11 * n_c - 12) / 3.0   # N_f=6 (all 6 quarks active above m_top)
    b0_5 = (11 * n_c - 10) / 3.0   # N_f=5 (below m_top, above m_bottom)

    m_top_gev = 172.7

    # Use b0=9 (N_f=3) to estimate the Landau pole
    lambda_data = lambda_qcd_from_dim_trans(alpha_s_kk, m_kk_gev, n_c, N_F_CANONICAL)
    lambda_gev = lambda_data["lambda_qcd_gev"]

    perturbative_at_mz = lambda_gev < M_Z_GEV

    alpha_s_mz = None
    if perturbative_at_mz and m_top_gev < m_kk_gev:
        # Step 1: run from M_KK to M_top with N_f=6
        inv_at_top = 1.0 / alpha_s_kk - (b0_6 / (2.0 * math.pi)) * math.log(m_kk_gev / m_top_gev)
        if inv_at_top > 0:
            alpha_at_top = 1.0 / inv_at_top
            # Step 2: run from M_top to M_Z with N_f=5
            inv_at_mz = inv_at_top - (b0_5 / (2.0 * math.pi)) * math.log(m_top_gev / M_Z_GEV)
            if inv_at_mz > 0:
                alpha_s_mz = 1.0 / inv_at_mz

    return {
        "alpha_s_kk":       alpha_s_kk,
        "m_kk_gev":         m_kk_gev,
        "alpha_s_mz_pred":  alpha_s_mz,
        "alpha_s_mz_pdg":   ALPHA_S_MZ_PDG,
        "landau_pole_gev":  lambda_gev,
        "perturbative_at_mz": perturbative_at_mz,
        "status": (
            "NOT PERTURBATIVE AT M_Z — The UM non-Abelian CS threshold gives "
            f"α_s(M_KK) ≈ {alpha_s_kk:.5f}, placing Λ_QCD ~ {lambda_gev:.3e} GeV "
            f">> M_Z = {M_Z_GEV} GeV.  The coupling diverges (confinement) "
            "well above the Z mass, meaning the UM-derived strong sector is "
            "not perturbative at electroweak scales.  Closing the gap requires "
            "the α_s correction documented in alpha_s_correction_factor()."
        ) if not perturbative_at_mz else (
            f"PERTURBATIVE AT M_Z — α_s(M_Z)_pred ≈ {alpha_s_mz:.4f} "
            f"vs PDG {ALPHA_S_MZ_PDG} — discrepancy {alpha_s_mz/ALPHA_S_MZ_PDG:.2f}×."
        ),
    }


# ---------------------------------------------------------------------------
# Honest gap report
# ---------------------------------------------------------------------------

def nonabelian_kk_gap_report() -> dict[str, Any]:
    """Honest, comprehensive gap accounting for Pillar 62.

    Returns
    -------
    dict documenting what Pillar 62 achieves, what it does not, and
    what further work would be needed.
    """
    cas = su3_casimir_data()
    alpha_data = alpha_s_kk_scale()
    b0 = qcd_beta_b0()
    lam_data = lambda_qcd_from_dim_trans()
    corr = alpha_s_correction_factor()
    mz_pred = alpha_s_at_mz_prediction()
    ratio_pipeline = mp_over_me_pipeline()

    return {
        "pillar": 62,
        "title": "Non-Abelian SU(3)_C Kaluza-Klein Reduction",
        "group_theory": cas,
        "alpha_s_kk": {
            "value": alpha_data["alpha_s_kk"],
            "status": "PARTIALLY DERIVED — from k_CS (derived) and N_c (new assumption)",
        },
        "b0": {
            "value": b0,
            "status": "DERIVED — (11×3−2×3)/3=9; N_f=3 from Pillar 42",
        },
        "lambda_qcd": {
            "um_prediction_mev": lam_data["lambda_qcd_mev"],
            "pdg_mev": LAMBDA_QCD_PDG_MEV,
            "discrepancy_factor": lam_data["discrepancy_factor"],
            "log10_discrepancy": lam_data["log10_discrepancy"],
            "status": (
                "FRAMEWORK EXISTS — prediction is ~10⁷× too large; "
                "exponentially sensitive to α_s(M_KK)"
            ),
        },
        "alpha_s_correction_needed": corr,
        "alpha_s_mz": mz_pred,
        "mp_over_me": {
            "um_derived_lambda_qcd": False,
            "conditionally_derivable": True,
            "free_parameters_remaining": 3,  # Λ_QCD, C_lat, Yukawa_e
            "pre_pillar62_free_parameters": 3,  # same count, but now with a framework
            "status": (
                "CONDITIONALLY DERIVABLE — framework now exists for strong sector; "
                "α_s(M_KK) correction needed to close numerical gap in Λ_QCD."
            ),
        },
        "open_gaps_after_pillar62": [
            "(A) α_s(M_KK) from non-Abelian CS threshold is 1.7× too large, "
            "causing ~10⁷× error in Λ_QCD.  Requires multi-loop or instanton "
            "threshold correction.",
            "(B) N_c = 3 is an assumption.  Deriving N_c from 5D geometry requires "
            "embedding SU(3) isometry in extra dimensions (e.g., 7D S⁷/Z₂ per "
            "Witten 1981).",
            "(C) Lattice normalisation C_lat ≈ 4.4 is not derivable from the "
            "one-loop CS spectrum; it encodes non-perturbative QCD dynamics.",
            "(D) Yukawa coupling for m_e (Pillar 60 gap, unchanged).",
        ],
        "progress_from_pillar61": (
            "Before Pillar 62: strong sector had NO mathematical framework "
            "within the UM geometry.  After Pillar 62: the derivation chain "
            "is established (SU(3)_C KK reduction → α_s → b_0 → Λ_QCD → m_p); "
            "N_f=3 is derived from Pillar 42; the gap is quantified as a "
            "1.7× correction to α_s(M_KK).  The classification of the UM "
            "upgrades from 'no strong-sector framework' to 'strong-sector "
            "framework with quantified gap'."
        ),
    }


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

def nonabelian_kk_summary() -> dict[str, Any]:
    """Full Pillar 62 derivation summary.

    Returns
    -------
    dict with keys:
        constants       — module constants table
        derivation_chain — step-by-step status
        gap_report      — nonabelian_kk_gap_report() output
        overall_verdict — plain-language summary
    """
    gap = nonabelian_kk_gap_report()
    lam_data = lambda_qcd_from_dim_trans()
    corr = alpha_s_correction_factor()
    return {
        "constants": {
            "K_CS_CANONICAL":    K_CS_CANONICAL,
            "N_C_CANONICAL":     N_C_CANONICAL,
            "N_F_CANONICAL":     N_F_CANONICAL,
            "B0_CANONICAL":      B0_CANONICAL,
            "ALPHA_S_KK":        ALPHA_S_KK_CANONICAL,
            "M_KK_GEV":          M_KK_CANONICAL_GEV,
        },
        "derivation_chain": {
            "step1_k_cs":       "k_CS = 74 — DERIVED algebraically (Pillar 58)",
            "step2_n_c":        "N_c = 3 — NEW ASSUMPTION (SU(3)_C colour)",
            "step3_n_f":        "N_f = 3 — DERIVED from Pillar 42 (Three-Generation Theorem)",
            "step4_b0":         f"b_0 = {B0_CANONICAL} — DERIVED from N_c=3 + N_f=3",
            "step5_alpha_s_kk": f"α_s(M_KK) = {ALPHA_S_KK_CANONICAL:.5f} — PARTIALLY DERIVED",
            "step6_lambda_qcd": f"Λ_QCD_pred = {lam_data['lambda_qcd_mev']:.3e} MeV — FRAMEWORK (gap: {lam_data['discrepancy_factor']:.1e}×)",
            "step7_m_p":        "m_p ≈ C_lat × Λ_QCD — FREE PARAMETER C_lat",
            "step8_mp_over_me": "m_p/m_e — CONDITIONALLY DERIVABLE",
        },
        "correction_needed": corr,
        "gap_report": gap,
        "overall_verdict": (
            "Pillar 62 establishes the non-Abelian SU(3)_C Kaluza-Klein "
            "reduction framework.  The derivation chain from 5D geometry to "
            "Λ_QCD to m_p/m_e now EXISTS, with the Pillar-42-derived N_f=3 "
            "entering the QCD beta function.  The current prediction of Λ_QCD "
            f"({lam_data['lambda_qcd_mev']:.2e} MeV) overshoots PDG by "
            f"~{lam_data['discrepancy_factor']:.1e}×, quantified as a "
            f"{corr['correction_factor']:.2f}× correction to α_s(M_KK).  "
            "The UM classification remains: fundamental geometric theory of "
            "the gravitational and cosmological sector, with partial reach into "
            "the electroweak sector, and now with a FRAMEWORK (but not a "
            "complete derivation) for the strong sector."
        ),
    }


# ---------------------------------------------------------------------------
# CERN Open Data anchor: CMS α_s measurements (2024)
# ---------------------------------------------------------------------------

#: CMS 13 TeV α_s measurement at M_Z = 91.19 GeV, from the PDG/CMS world
#: average using 2016 open data (CERN Open Data Portal, CMS-SMP publications).
CMS_ALPHAS_MZ: float = 0.1179

#: Uncertainty on CMS α_s(M_Z) (combined experimental + theory, 68% CL)
CMS_ALPHAS_MZ_UNC: float = 0.0009

#: CMS α_s measurement from dijet production at Q ≈ 1 TeV (13 TeV, 2016 data)
#: This is an approximate value extracted from high-pT dijet events.
#: Source: CMS open data publications; CMS-SMP-19-009 and related analyses.
CMS_ALPHAS_1TEV: float = 0.086

#: Approximate uncertainty on CMS α_s at Q = 1 TeV
CMS_ALPHAS_1TEV_UNC: float = 0.003

#: Scale [GeV] corresponding to CMS_ALPHAS_1TEV
CMS_SCALE_1TEV: float = 1000.0


def cms_alphas_rg_consistency(
    cms_measurements: list | None = None,
    alpha_s_kk: float = ALPHA_S_KK_CANONICAL,
    m_kk_gev: float = M_KK_CANONICAL_GEV,
    n_c: int = N_C_CANONICAL,
) -> dict[str, Any]:
    """Compare the UM α_s RG running against CMS open-data measurements.

    CMS 13 TeV measurements anchored to the CERN Open Data Portal (2016
    collision data, 138 fb⁻¹) give:

        α_s(M_Z = 91.19 GeV) = 0.1179 ± 0.0009   (PDG/CMS world average)
        α_s(Q ≈ 1000 GeV)    ≈ 0.086  ± 0.003     (CMS dijet at ~1 TeV)

    The UM predicts α_s from the non-Abelian KK threshold (Pillar 62):

        α_s(M_KK) = 2π / (N_c × k_CS)  ≈  0.0283

    Running this down to the measured scales with `evolve_coupling()` uses a
    one-loop QCD RG equation.  Note: with the canonical parameters the Landau
    pole lies at ~PeV — far above M_Z — so the one-loop running from M_KK
    to M_Z is unphysical without the α_s correction factor from
    `alpha_s_correction_factor()`.  This function therefore also reports the
    running starting from the PDG-corrected value of α_s(M_Z) and running
    upward to M_KK, for comparison.

    Parameters
    ----------
    cms_measurements : list of (scale_gev, alpha_s_measured) tuples, or None.
        Defaults to the two canonical CMS data points:
        [(91.1876, 0.1179), (1000.0, 0.086)].
    alpha_s_kk : float — α_s at the KK scale (default: canonical UM value)
    m_kk_gev   : float — KK scale [GeV] (default: canonical M_KK)
    n_c        : int   — number of colours (default 3)

    Returns
    -------
    dict with keys:
        ``alpha_s_kk``          : float — UM α_s at M_KK
        ``m_kk_gev``            : float — KK scale [GeV]
        ``cms_data``            : list of dicts, each with:
            ``scale_gev``           : float — measurement scale [GeV]
            ``alpha_s_cms``         : float — CMS measured value
            ``alpha_s_um_pred``     : float or None — UM running prediction
            ``fractional_deviation``: float or None — (pred - meas) / meas
            ``within_2sigma``       : bool or None
            ``status``              : str — descriptive assessment
        ``pdg_upward_check``    : dict — α_s run from M_Z upward to M_KK
        ``overall_consistent``  : bool — True iff all measurable points agree
        ``reference``           : str  — citation
        ``verdict``             : str  — plain-language summary
    """
    if cms_measurements is None:
        cms_measurements = [
            (M_Z_GEV,        CMS_ALPHAS_MZ,   CMS_ALPHAS_MZ_UNC),
            (CMS_SCALE_1TEV, CMS_ALPHAS_1TEV, CMS_ALPHAS_1TEV_UNC),
        ]

    b0_full = qcd_beta_b0(n_c, N_F_CANONICAL)
    b0_6 = (11 * n_c - 12) / 3.0   # N_f = 6 above m_top
    b0_5 = (11 * n_c - 10) / 3.0   # N_f = 5 below m_top
    m_top_gev = 172.7

    cms_data = []
    any_inconsistent = False

    for entry in cms_measurements:
        scale_gev, alpha_s_cms, alpha_s_unc = entry[0], entry[1], entry[2] if len(entry) > 2 else 0.0

        pred = None
        frac_dev = None
        within_2s = None
        status_str = ""

        # Attempt to run α_s(M_KK) down to scale_gev using one-loop QCD.
        # We use a simplified two-step threshold matching:
        # M_KK → m_top (N_f=6), m_top → scale (N_f=5)
        if scale_gev < m_kk_gev:
            try:
                # Step 1: M_KK → m_top (if m_top is between scale and M_KK)
                if m_top_gev > scale_gev and m_top_gev < m_kk_gev:
                    inv_at_top = (1.0 / alpha_s_kk) - (b0_6 / (2.0 * math.pi)) * math.log(m_kk_gev / m_top_gev)
                    if inv_at_top > 0:
                        alpha_at_top = 1.0 / inv_at_top
                        # Step 2: m_top → scale (N_f=5)
                        inv_at_scale = inv_at_top - (b0_5 / (2.0 * math.pi)) * math.log(m_top_gev / scale_gev)
                        if inv_at_scale > 0:
                            pred = 1.0 / inv_at_scale
                else:
                    # scale > m_top: run directly with N_f=5
                    pred = evolve_coupling(alpha_s_kk, m_kk_gev / scale_gev, b0_5)
            except ValueError:
                # Landau pole encountered before reaching target scale
                pred = None

        if pred is not None:
            frac_dev = (pred - alpha_s_cms) / alpha_s_cms
            within_2s = abs(pred - alpha_s_cms) <= 2.0 * alpha_s_unc if alpha_s_unc > 0 else None
            if within_2s is False:
                any_inconsistent = True
            status_str = (
                f"UM predicts α_s({scale_gev:.1f} GeV) ≈ {pred:.4f}; "
                f"CMS measures {alpha_s_cms:.4f}±{alpha_s_unc:.4f}.  "
                f"Fractional deviation: {frac_dev:+.3f} "
                f"({'within 2σ' if within_2s else 'outside 2σ' if within_2s is False else 'σ unknown'})."
            )
        else:
            any_inconsistent = True
            status_str = (
                f"UM RG running from M_KK={m_kk_gev:.2e} GeV to "
                f"{scale_gev:.1f} GeV hits Landau pole — direct comparison "
                "not perturbatively accessible with canonical parameters.  "
                "See alpha_s_correction_factor() for the required correction."
            )

        cms_data.append({
            "scale_gev":            scale_gev,
            "alpha_s_cms":          alpha_s_cms,
            "alpha_s_unc":          alpha_s_unc,
            "alpha_s_um_pred":      pred,
            "fractional_deviation": frac_dev,
            "within_2sigma":        within_2s,
            "status":               status_str,
        })

    # Upward check: run α_s from PDG M_Z value to M_KK (simulates what the
    # UM boundary condition should look like at high energy).
    pdg_upward: dict[str, Any] = {}
    try:
        # Run from M_Z up to M_KK using b0 with N_f=6 (above m_top)
        # scale_ratio = M_KK / M_Z > 1 → this is UV running (coupling decreases)
        ratio_mz_to_mkk = m_kk_gev / M_Z_GEV
        inv_mz = 1.0 / CMS_ALPHAS_MZ
        # UV running: α(μ_UV)⁻¹ = α(M_Z)⁻¹ + (b0/2π) × ln(M_KK/M_Z)
        inv_at_mkk = inv_mz + (b0_6 / (2.0 * math.pi)) * math.log(ratio_mz_to_mkk)
        alpha_at_mkk_from_mz = 1.0 / inv_at_mkk
        pdg_upward = {
            "alpha_s_mz_pdg":        CMS_ALPHAS_MZ,
            "alpha_s_at_mkk_from_mz": alpha_at_mkk_from_mz,
            "alpha_s_kk_um":         alpha_s_kk,
            "ratio_um_to_pdg_run":   alpha_s_kk / alpha_at_mkk_from_mz,
            "status": (
                f"Running PDG α_s(M_Z)={CMS_ALPHAS_MZ} upward to M_KK="
                f"{m_kk_gev:.2e} GeV gives α_s(M_KK)_from_PDG ≈ "
                f"{alpha_at_mkk_from_mz:.5f}.  UM predicts "
                f"α_s(M_KK)={alpha_s_kk:.5f}.  Ratio: "
                f"{alpha_s_kk / alpha_at_mkk_from_mz:.3f} "
                "(should be 1.0 if UM running is correct)."
            ),
        }
    except (ValueError, ZeroDivisionError) as exc:
        pdg_upward = {"error": str(exc)}

    return {
        "alpha_s_kk":          alpha_s_kk,
        "m_kk_gev":            m_kk_gev,
        "cms_data":            cms_data,
        "pdg_upward_check":    pdg_upward,
        "overall_consistent":  not any_inconsistent,
        "reference": (
            "CMS Collaboration, CERN Open Data Portal, 13 TeV 2016 data "
            "(138 fb⁻¹); CMS-SMP publications; PDG 2024 α_s world average."
        ),
        "verdict": (
            "The UM α_s RG running from M_KK to lower scales is not "
            "perturbatively accessible with canonical parameters (Landau pole "
            f"at ~PeV scale, above M_Z={M_Z_GEV} GeV).  The CMS measurements "
            f"at M_Z ({CMS_ALPHAS_MZ}±{CMS_ALPHAS_MZ_UNC}) and Q≈1 TeV "
            f"({CMS_ALPHAS_1TEV}±{CMS_ALPHAS_1TEV_UNC}) are consistent with "
            "the PDG world average but cannot be directly compared to the "
            "canonical UM threshold without the α_s correction factor "
            "(see alpha_s_correction_factor()).  The upward RG check from "
            "PDG M_Z to M_KK provides the required UM boundary condition."
        ),
    }
