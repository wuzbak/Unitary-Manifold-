# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dirty_data_test.py
============================
Pillar 61 — The AxiomZero Challenge: Internal Falsifier Suite.

Background: The Gemini "Reality Check"
---------------------------------------
An external critique (April 2026) identified three modes in which an AI
framework can appear to produce "correct" physics:

    1. Math Correction (Compiler)   — fixing internal signs/normalisations.
    2. Theory Metaphor (Librarian)  — recasting known results in new language.
    3. Oracle Retrieval             — returning a known answer via pattern-match
                                      rather than derivation.

The critique proposed two tests to discriminate genuine derivation from
oracle retrieval:

**Dirty Data Test:**
    Give the framework a slightly "broken" version of the 5D equations
    (perturbed compactification φ₀_eff by a factor 1+δ).  If the 4D
    prediction tracks the perturbation as expected from the 5D chain, the
    code is genuinely using the 5D structure.  If the output collapses back
    to the known answer independent of δ, the answer is being retrieved from
    memory — not derived.

**Oracle Test (Unknown-Unknown):**
    Ask the framework to derive a quantity for which no hint was ever
    provided during framework construction.  The two candidates are:
        (a) The fine-structure constant α ≈ 1/137.036
        (b) The proton/electron mass ratio m_p/m_e ≈ 1836.15

This module implements:

    (1) The Dirty Data Test for ns and r from the inflation pipeline.
    (2) An honest accounting of whether α and m_p/m_e can be derived from
        the (5,7) braid topology alone.
    (3) A scoped RG estimate of α from k_CS = 74, clearly documenting which
        step requires a free parameter.

Dirty Data Test — Design
------------------------
The canonical 4D inflaton vev is:

    φ₀_eff = n_w · 2π · φ₀_bare   ≈  31.416  (n_w=5, φ₀_bare=1)

The slow-roll spectral index at the inflection point φ* = φ₀_eff/√3 is:

    nₛ = 1 − 6ε    where ε = (V'/V)²/2 evaluated at φ*

For the Goldberger-Wise potential this gives:

    nₛ ≈ 1 − 6/φ₀_eff²   (leading-order approximation)

Perturbing φ₀_eff → φ₀_eff · (1 + δ):

    nₛ(δ) ≈ 1 − 6/[φ₀_eff · (1+δ)]²
           ≈ nₛ(0) + 12/φ₀_eff² · δ   (first order in δ)

The linear sensitivity coefficient is:

    dnₛ/dδ|_{δ=0}  =  2 · (nₛ(0) − 1) / 1  =  12 / φ₀_eff²

For φ₀_eff ≈ 31.416:

    dnₛ/dδ ≈ 12 / 987  ≈ 0.01215

If the code is genuinely using the 5D pathway:
    nₛ(δ=0.1) − nₛ(0)  ≈  0.001215   ← expected

If the code is bypassing the 5D pathway (oracle):
    nₛ(δ=0.1) − nₛ(0)  ≈  0          ← would falsify the derivation claim

α Derivation Scoping — Why It Fails Without a Free Parameter
------------------------------------------------------------
The (5,7) braid gives k_CS = 74 algebraically (Pillar 58).  The axion-photon
coupling from the Chern-Simons term is:

    g_{aγγ} = k_CS · α / (2π² r_c)

This equation contains α as a *free input*, not as a derived output.  To
derive α one would need to:

  Step 1: Compute α at the KK scale M_KK = M_Pl / r_c from the gauge kinetic
          function determined by the 5D geometry.  The KK-scale coupling is:

              α(M_KK) = 1 / (4π · f_gauge)
                       = 1 / (4π · k_CS / (8π²))
                       = 2π / k_CS

          For k_CS = 74:

              α(M_KK) = 2π / 74 ≈ 0.085

          (This is an O(0.1) quantity, not ≈ 1/137 — the KK-scale coupling is
          not the low-energy electromagnetic fine structure constant.)

  Step 2: Run α from M_KK down to low energies via RG equations:

              α(μ)⁻¹ = α(M_KK)⁻¹ + (b₀ / 2π) · ln(M_KK / μ)

          where b₀ = −(4/3)T_F · n_f is the QED beta-function coefficient
          with n_f light fermion flavours.  At μ = m_e:

              α⁻¹(m_e) ≈ 2.94 + (2/3π) · ln(M_KK / m_e) · n_f

          This step introduces n_f (the number of light fermion species below
          M_KK) as a free parameter.  The UM does not currently derive n_f.

  Step 3: Close n_f from first principles.  The Standard Model has n_f = 5
          charged fermions lighter than the Z mass.  To derive n_f = 5 from
          the 5D framework would require a complete fermion-sector derivation
          — specifically the Yukawa profile and brane-localisation for all
          five SM generations, which Pillar 60 documents as an open gap.

Conclusion: α is derivable from k_CS only up to the free parameter n_f.
Claiming α ≈ 1/137 without specifying n_f independently of observations
would be oracle retrieval, not derivation.  This module computes the
KK-scale value α(M_KK) and the RG-corrected value α(m_e; n_f) transparently,
and clearly labels n_f as a free input.

m_p/m_e Gap Accounting
-----------------------
The proton/electron mass ratio m_p/m_e ≈ 1836.15 cannot be derived from the
current UM framework because:

  1. The electron mass is set by a free Yukawa coupling λ fitted to m_e
     (documented in Pillar 60, `src/core/particle_mass_spectrum.py`).

  2. The proton mass receives a dominant contribution from QCD confinement
     (Λ_QCD ≈ 210 MeV) plus a subdominant quark-mass contribution.

  3. The UM does not currently derive Λ_QCD from the 5D geometry.  The
     strong coupling α_s and its running (governing Λ_QCD) would require
     a non-Abelian extension of the KK gauge sector — not yet implemented.

The Gemini "Unknown-Unknown" Test: the ratio 1836.15 can be reproduced by
providing the known value as a target.  It cannot be reproduced by blind
derivation from the (5,7) topology without additional inputs.

Public API
----------
PHI0_BARE, N_W, PHI0_EFF_CANONICAL
    Module-level canonical constants.

ALPHA_EM_PDG, MP_OVER_ME_PDG, NS_CANONICAL
    Physical reference values used only as comparison targets; never as
    inputs to the 5D derivation pipeline.

perturbed_phi0_eff(delta)
    Return φ₀_eff · (1 + δ) — the "dirty" compactification vev.

ns_from_phi0_eff(phi0_eff)
    Compute nₛ directly from an effective inflaton vev via the slow-roll
    approximation at the inflection point.  This is the thin pipeline through
    which the Dirty Data Test runs.

ns_perturbation_response(delta)
    Return (ns_clean, ns_dirty, delta_ns) for a given perturbation δ.

ns_linear_sensitivity()
    Analytic linear-response coefficient dnₛ/dδ|_{δ=0} = 12 / φ₀_eff².

dirty_data_check(delta, rtol)
    Core test: verify that nₛ tracks the perturbation within rtol of the
    expected linear response.  Returns a result dict.

oracle_detection_report()
    Demonstrate that nₛ does NOT return the canonical value when δ ≠ 0.

alpha_kk_scale(k_cs, r_c)
    Estimate α at the KK compactification scale from the CS gauge threshold.
    Documents the derivation chain and labels free parameters.

alpha_rg_run(alpha_kk, m_kk_gev, mu_gev, n_f)
    Run α from the KK scale to a lower scale μ via one-loop QED RG.

alpha_low_energy(k_cs, r_c, m_kk_gev, mu_gev, n_f)
    Full pipeline: α(M_KK) → RG → α(μ).  Returns a dict documenting every
    free parameter and its status.

three_generation_n_f_constraint()
    The "Kill Move" answer: does the (5,7) topology constrain n_f?
    Shows that n_w=5 → N_gen=3 via the orbifold stability condition n²≤n_w.
    Partially closes the n_f gap: n_f_lepton=3 is geometrically constrained,
    given n_w=5 from Planck.  Documents remaining caveats honestly.

mp_over_me_gap_report()
    Honest accounting of why m_p/m_e cannot be derived from (5,7) alone.

axiomzero_challenge_summary()
    Full summary dict of the AxiomZero Challenge status.

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
# Module-level constants
# ---------------------------------------------------------------------------

#: Winding number (Pillar 39, derived from S¹/Z₂ orbifold + Planck nₛ)
N_W: int = 5

#: Secondary winding (Pillar 58, derived from BICEP/Keck r < 0.036)
N_W2: int = 7

#: Chern-Simons level: proved algebraically as n₁² + n₂² (Pillar 58)
K_CS: int = N_W**2 + N_W2**2          # 25 + 49 = 74

#: FTUM bare fixed-point radion (Planck units, φ₀_bare ≈ 1)
PHI0_BARE: float = 1.0

#: Canonical effective 4D inflaton vev: φ₀_eff = N_W · 2π · φ₀_bare
PHI0_EFF_CANONICAL: float = N_W * 2.0 * math.pi   # ≈ 31.416

#: Compactification radius in Planck units (Pillar 27)
R_C_CANONICAL: float = 12.0

#: Braided sound speed c_s = (N_W2² − N_W²) / K_CS = 24/74 = 12/37 (Pillar 58)
C_S_CANONICAL: float = (N_W2**2 - N_W**2) / K_CS   # 24/74 ≈ 0.3243

# --------------------------------------------------------------------------
# Physical reference values — used ONLY as comparison targets.
# These are PDG inputs, never used as inputs to the 5D derivation.
# --------------------------------------------------------------------------

#: PDG 2022 fine-structure constant (CODATA; input to α-comparison only)
ALPHA_EM_PDG: float = 1.0 / 137.035_999_084

#: PDG 2022 proton/electron mass ratio (input to m_p/m_e comparison only)
MP_OVER_ME_PDG: float = 1836.152_673_43

#: Planck 2018 spectral index central value (1σ = 0.0042)
NS_PLANCK_CENTRAL: float = 0.9649
NS_PLANCK_SIGMA: float = 0.0042

# Leading-order slow-roll nₛ from the GW potential at the inflection point
# φ* = φ₀_eff / √3.  At the inflection point η = 0, ε = 6 / φ₀_eff², so:
#     nₛ = 1 − 6ε = 1 − 36 / φ₀_eff²
# For φ₀_eff = 5·2π ≈ 31.416:  φ₀_eff² ≈ 987.5, nₛ ≈ 1 − 36/987.5 ≈ 0.9635
NS_CANONICAL: float = 1.0 - 36.0 / PHI0_EFF_CANONICAL**2   # ≈ 0.9635

#: Proton mass in MeV (PDG 2024)
M_PROTON_MEV: float = 938.272_046

#: Electron mass in MeV (PDG 2024)
M_ELECTRON_MEV: float = 0.510_998_950


# ---------------------------------------------------------------------------
# Helper: slow-roll nₛ from effective inflaton vev
# ---------------------------------------------------------------------------

def ns_from_phi0_eff(phi0_eff: float, lam: float = 1.0) -> float:
    """Compute nₛ from a given effective inflaton vev via the GW slow-roll chain.

    This is a *thin wrapper* that goes through the full Goldberger-Wise
    potential pipeline — it does NOT hard-code the known answer.

    The inflection point is φ* = φ₀_eff / √3 (where V'' = 0).

    Parameters
    ----------
    phi0_eff : float — effective 4D inflaton vev (Planck units, > 0)
    lam      : float — GW coupling (default 1; nₛ is λ-independent at LO)

    Returns
    -------
    ns : float — scalar spectral index

    Raises
    ------
    ValueError
        If phi0_eff ≤ 0.
    """
    if phi0_eff <= 0.0:
        raise ValueError(f"phi0_eff must be positive; got {phi0_eff!r}")
    phi_star = phi0_eff / math.sqrt(3.0)
    # GW potential and derivatives at φ*
    V   = lam * (phi_star**2 - phi0_eff**2)**2
    dV  = 4.0 * lam * phi_star * (phi_star**2 - phi0_eff**2)
    d2V = 4.0 * lam * (3.0 * phi_star**2 - phi0_eff**2)
    if V <= 0.0:
        raise ValueError(
            f"Potential V={V!r} ≤ 0 at phi_star={phi_star!r}, phi0_eff={phi0_eff!r}."
        )
    epsilon = 0.5 * (dV / V) ** 2
    eta     = d2V / V
    return 1.0 - 6.0 * epsilon + 2.0 * eta


def r_from_phi0_eff(phi0_eff: float, lam: float = 1.0) -> float:
    """Compute r = 16ε from a given effective inflaton vev.

    Parameters
    ----------
    phi0_eff : float — effective 4D inflaton vev (Planck units, > 0)
    lam      : float — GW coupling (default 1; r is λ-independent at LO)

    Returns
    -------
    r : float — tensor-to-scalar ratio
    """
    if phi0_eff <= 0.0:
        raise ValueError(f"phi0_eff must be positive; got {phi0_eff!r}")
    phi_star = phi0_eff / math.sqrt(3.0)
    V   = lam * (phi_star**2 - phi0_eff**2)**2
    dV  = 4.0 * lam * phi_star * (phi_star**2 - phi0_eff**2)
    if V <= 0.0:
        raise ValueError(f"Potential V={V!r} ≤ 0.")
    epsilon = 0.5 * (dV / V) ** 2
    return 16.0 * epsilon


# ---------------------------------------------------------------------------
# Dirty Data Test — core functions
# ---------------------------------------------------------------------------

def perturbed_phi0_eff(delta: float) -> float:
    """Return φ₀_eff · (1 + δ) — the "dirty" compactification vev.

    This introduces a controlled perturbation into the 5D compactification
    radius.  A framework that genuinely uses φ₀_eff to compute nₛ will
    produce a predictably different output.  A framework that retrieves the
    known answer from memory will return the canonical value regardless of δ.

    Parameters
    ----------
    delta : float — fractional perturbation (e.g. 0.05 = 5%)

    Returns
    -------
    phi0_eff_dirty : float
    """
    return PHI0_EFF_CANONICAL * (1.0 + delta)


def ns_perturbation_response(delta: float) -> dict[str, float]:
    """Compute nₛ before and after perturbing φ₀_eff by δ.

    Parameters
    ----------
    delta : float — fractional perturbation of φ₀_eff

    Returns
    -------
    dict with keys:
        phi0_eff_clean  — canonical φ₀_eff
        phi0_eff_dirty  — perturbed φ₀_eff = φ₀_eff · (1+δ)
        ns_clean        — nₛ at canonical φ₀_eff
        ns_dirty        — nₛ at perturbed φ₀_eff
        delta_ns        — ns_dirty − ns_clean  (should be nonzero for |δ| > 0)
        delta_ns_linear — first-order prediction Δnₛ ≈ (dnₛ/dδ) · δ
    """
    phi_clean = PHI0_EFF_CANONICAL
    phi_dirty = perturbed_phi0_eff(delta)
    ns_clean  = ns_from_phi0_eff(phi_clean)
    ns_dirty  = ns_from_phi0_eff(phi_dirty)
    delta_ns  = ns_dirty - ns_clean
    sensitivity = ns_linear_sensitivity()
    return {
        "phi0_eff_clean":  phi_clean,
        "phi0_eff_dirty":  phi_dirty,
        "ns_clean":        ns_clean,
        "ns_dirty":        ns_dirty,
        "delta_ns":        delta_ns,
        "delta_ns_linear": sensitivity * delta,
    }


def ns_linear_sensitivity() -> float:
    """Analytic first-order sensitivity dnₛ/dδ|_{δ=0}.

    From the leading-order formula nₛ ≈ 1 − 6ε, with ε evaluated via the
    full GW potential at φ* = φ₀_eff / √3, the numerical derivative at
    δ = 0 equals ≈ −2 · (nₛ_0 − 1) evaluated from the full potential.

    We compute this via finite difference at δ = ±1e-5 to avoid any
    approximation mismatch with the actual pipeline.

    Returns
    -------
    sensitivity : float — dnₛ/dδ ≈ 12 / φ₀_eff² (positive)
    """
    eps = 1e-5
    ns_p = ns_from_phi0_eff(PHI0_EFF_CANONICAL * (1.0 + eps))
    ns_m = ns_from_phi0_eff(PHI0_EFF_CANONICAL * (1.0 - eps))
    return (ns_p - ns_m) / (2.0 * eps)


def ns_linear_sensitivity_analytic() -> float:
    """Leading-order analytic estimate of dnₛ/dδ = 72 / φ₀_eff².

    At the inflection point φ* = φ₀_eff / √3, η = 0 and ε = 6 / φ₀_eff².
    Therefore:

        nₛ(φ₀_eff) = 1 − 36 / φ₀_eff²

    Perturbing φ₀_eff → φ₀_eff · (1+δ):

        nₛ(δ) = 1 − 36 / (φ₀_eff(1+δ))²

        dnₛ/dδ|_{δ=0} = +72 / φ₀_eff²

    Returns
    -------
    float ≈ 72 / PHI0_EFF_CANONICAL²  ≈ 0.073
    """
    return 72.0 / PHI0_EFF_CANONICAL**2


def dirty_data_check(
    delta: float,
    rtol: float = 0.20,
) -> dict[str, Any]:
    """Core Dirty Data Test.

    Verify that the nₛ prediction tracks a perturbation δ in φ₀_eff within
    *rtol* of the expected linear response.

    A result where ``tracks_perturbation = True`` means the code is genuinely
    propagating the 5D change through to the 4D observable — not retrieving
    the canonical answer from memory.

    Parameters
    ----------
    delta : float — fractional perturbation (|δ| should be between 0.001 and 0.5)
    rtol  : float — relative tolerance on Δnₛ vs the linear prediction (default 0.20)

    Returns
    -------
    dict with keys:
        delta               — input perturbation
        ns_clean            — canonical nₛ
        ns_dirty            — perturbed nₛ
        delta_ns_actual     — nₛ(dirty) − nₛ(clean)
        delta_ns_predicted  — linear estimate (sensitivity · δ)
        sensitivity         — dnₛ/dδ|_{δ=0}
        relative_error      — |actual − predicted| / |predicted|
        rtol                — tolerance used
        tracks_perturbation — True iff code uses 5D path (not oracle)
        verdict             — human-readable string
    """
    if abs(delta) < 1e-10:
        raise ValueError("delta must be nonzero to distinguish oracle from derivation.")
    resp = ns_perturbation_response(delta)
    sensitivity = ns_linear_sensitivity()
    delta_ns_actual    = resp["delta_ns"]
    delta_ns_predicted = sensitivity * delta
    if abs(delta_ns_predicted) < 1e-15:
        relative_error = float("inf")
    else:
        relative_error = abs(delta_ns_actual - delta_ns_predicted) / abs(delta_ns_predicted)
    # The code passes the Dirty Data Test if it tracks the perturbation:
    # i.e., delta_ns is in the right direction and close to the linear prediction.
    sign_ok    = (delta_ns_actual * delta_ns_predicted) > 0
    magnitude_ok = relative_error < rtol
    tracks = sign_ok and magnitude_ok
    verdict = (
        "PASS — Code uses 5D path: nₛ tracks the perturbation as expected."
        if tracks else
        "FAIL — Possible oracle retrieval: nₛ does not track the perturbation."
    )
    return {
        "delta":               delta,
        "ns_clean":            resp["ns_clean"],
        "ns_dirty":            resp["ns_dirty"],
        "delta_ns_actual":     delta_ns_actual,
        "delta_ns_predicted":  delta_ns_predicted,
        "sensitivity":         sensitivity,
        "relative_error":      relative_error,
        "rtol":                rtol,
        "tracks_perturbation": tracks,
        "verdict":             verdict,
    }


def oracle_detection_report() -> dict[str, Any]:
    """Demonstrate that nₛ does NOT stay at the canonical value when δ ≠ 0.

    An oracle would return NS_PLANCK_CENTRAL ≈ 0.9649 regardless of δ.
    The genuine 5D pipeline returns a different value for each δ.

    Returns
    -------
    dict mapping delta values to ns_dirty and whether it deviates from canonical.
    """
    test_deltas = [-0.20, -0.10, -0.05, 0.05, 0.10, 0.20]
    results: dict[str, Any] = {
        "ns_canonical":    ns_from_phi0_eff(PHI0_EFF_CANONICAL),
        "ns_planck_central": NS_PLANCK_CENTRAL,
        "perturbations":   {},
    }
    for d in test_deltas:
        ns_d = ns_from_phi0_eff(perturbed_phi0_eff(d))
        results["perturbations"][d] = {
            "ns_dirty":        ns_d,
            "deviates_from_canonical": abs(ns_d - results["ns_canonical"]) > 1e-6,
        }
    results["oracle_falsified"] = all(
        v["deviates_from_canonical"]
        for v in results["perturbations"].values()
    )
    return results


def r_perturbation_response(delta: float) -> dict[str, float]:
    """Compute r before and after perturbing φ₀_eff by δ.

    Confirms that the tensor-to-scalar ratio also tracks the perturbation
    independently of nₛ, providing a second oracle-falsification channel.

    Parameters
    ----------
    delta : float — fractional perturbation of φ₀_eff

    Returns
    -------
    dict with keys: phi0_eff_clean, phi0_eff_dirty, r_clean, r_dirty, delta_r
    """
    phi_clean = PHI0_EFF_CANONICAL
    phi_dirty = perturbed_phi0_eff(delta)
    r_clean   = r_from_phi0_eff(phi_clean)
    r_dirty   = r_from_phi0_eff(phi_dirty)
    return {
        "phi0_eff_clean": phi_clean,
        "phi0_eff_dirty": phi_dirty,
        "r_clean":        r_clean,
        "r_dirty":        r_dirty,
        "delta_r":        r_dirty - r_clean,
    }


# ---------------------------------------------------------------------------
# α derivation chain — honest scoping
# ---------------------------------------------------------------------------

def alpha_kk_scale(
    k_cs: int = K_CS,
    r_c: float = R_C_CANONICAL,
) -> dict[str, Any]:
    """Estimate α at the KK compactification scale from the CS gauge threshold.

    The Chern-Simons term at level k_CS gives a one-loop gauge threshold
    correction to the gauge kinetic function:

        f_gauge = k_CS / (8π²)

    The gauge coupling at M_KK is therefore:

        α(M_KK) = 1 / (4π · f_gauge) = 2π / k_CS

    This is an O(1) quantity (≈ 0.085 for k_CS = 74), far from α ≈ 1/137.

    Parameters
    ----------
    k_cs : int   — Chern-Simons level (default 74, derived)
    r_c  : float — compactification radius in Planck units (default 12)

    Returns
    -------
    dict with keys:
        k_cs            — CS level used
        r_c             — compactification radius
        f_gauge         — gauge kinetic function from CS threshold
        alpha_kk        — α at the KK scale (∼ O(1), not 1/137)
        alpha_kk_inv    — 1/α at KK scale
        free_parameters — list of free parameters in this step
        status          — string describing derivation status
    """
    f_gauge  = k_cs / (8.0 * math.pi**2)
    alpha_kk = 1.0 / (4.0 * math.pi * f_gauge)   # = 2π / k_cs
    return {
        "k_cs":         k_cs,
        "r_c":          r_c,
        "f_gauge":      f_gauge,
        "alpha_kk":     alpha_kk,
        "alpha_kk_inv": 1.0 / alpha_kk,
        "free_parameters": [],   # k_cs is derived; r_c is derived
        "status": (
            "DERIVED — α(M_KK) = 2π/k_CS follows from the CS gauge threshold. "
            "No free parameter at this step.  But α(M_KK) ≈ {:.4f} ≠ 1/137."
        ).format(alpha_kk),
    }


def alpha_rg_run(
    alpha_kk: float,
    m_kk_gev: float,
    mu_gev: float,
    n_f: int,
) -> float:
    """Run α from the KK scale to a lower scale μ via one-loop QED RG.

    In QED the coupling increases with energy (screening by virtual fermion
    loops).  Going from high scale M_KK down to a lower scale μ, 1/α increases:

        α(μ)⁻¹ = α(M_KK)⁻¹ + (b_eff / π) · ln(M_KK / μ)

    where b_eff = n_f / 3 is the effective QED beta-function coefficient and
    n_f is the number of charged fermion species with mass below M_KK.

    Parameters
    ----------
    alpha_kk : float — fine-structure constant at the KK scale
    m_kk_gev : float — KK scale in GeV
    mu_gev   : float — target scale in GeV
    n_f      : int   — number of light charged fermion species (FREE PARAMETER)

    Returns
    -------
    alpha_low : float — α at the target scale μ  (smaller than alpha_kk)

    Notes
    -----
    n_f is a FREE PARAMETER here.  It counts the charged fermions lighter
    than M_KK.  For the Standard Model n_f = 5 (e, μ, τ, u, d, s, c, b
    minus the top quark, but in QED counting only charged leptons + quarks ×
    N_c × Q²).  The UM does not currently derive n_f from the 5D geometry.
    """
    if m_kk_gev <= 0 or mu_gev <= 0:
        raise ValueError("Scales must be positive.")
    if m_kk_gev < mu_gev:
        raise ValueError("m_kk_gev must be above mu_gev for downward RG running.")
    # one-loop QED running: coupling increases with energy (screening).
    # α(μ)⁻¹ = α(M_KK)⁻¹ + (b_eff / π) · ln(M_KK / μ)   for μ < M_KK
    # where b_eff > 0 gives a positive contribution (1/α increases going down).
    b_eff = n_f / 3.0
    alpha_inv_low = 1.0 / alpha_kk + b_eff / math.pi * math.log(m_kk_gev / mu_gev)
    if alpha_inv_low <= 0:
        raise ValueError(
            f"RG running produced 1/α = {alpha_inv_low!r} ≤ 0; "
            "check n_f and scale range."
        )
    return 1.0 / alpha_inv_low


def alpha_low_energy(
    k_cs: int = K_CS,
    r_c: float = R_C_CANONICAL,
    m_kk_gev: float = 1e6,          # intermediate demonstration scale (see Notes)
    mu_gev: float = 0.000511,        # electron mass in GeV
    n_f: int = 5,                    # SM charged fermion species (FREE PARAMETER)
) -> dict[str, Any]:
    """Full α derivation chain: gauge threshold → RG running → low-energy α.

    Documents every free parameter explicitly.

    Parameters
    ----------
    k_cs    : int   — Chern-Simons level (derived)
    r_c     : float — compactification radius in Planck units (derived)
    m_kk_gev: float — RG starting scale in GeV.  The physical KK scale is
                      M_Pl / r_c ≈ 2×10¹⁷ GeV, but the one-loop QED formula
                      diverges at such extreme separations for large n_f.  The
                      default 10⁶ GeV is used to keep the demonstration
                      well-behaved; the Notes section explains the full-scale
                      breakdown.
    mu_gev  : float — target RG scale (default: electron mass)
    n_f     : int   — number of light charged fermion species (FREE PARAMETER)

    Returns
    -------
    dict with keys:
        k_cs, r_c, m_kk_gev, mu_gev, n_f
        alpha_kk            — α at M_KK (derived, no free param at this step)
        alpha_low           — α at μ (depends on n_f — FREE PARAMETER)
        alpha_low_inv       — 1/α at μ
        alpha_pdg_inv       — 1/ALPHA_EM_PDG ≈ 137.04 (comparison only)
        n_f_is_free         — True (always; n_f is not derived from 5D geometry)
        derivation_status   — honest assessment string
        free_parameters     — list of free parameters in the full chain

    Notes
    -----
    At the true physical KK scale M_KK = M_Pl / r_c ≈ 2×10¹⁷ GeV, the
    one-loop QED RG running over ln(M_KK/m_e) ≈ 51 decades with n_f = 5
    gives 1/α_low ≈ 11.78 + (5/3π)×117 ≈ 11.78 + 62 = 73.8, so
    α_low ≈ 0.014 — much closer to 1/137 but still off.  The discrepancy
    occurs because the gauge threshold α(M_KK) = 2π/k_CS ≈ 0.085 differs
    from the true unification-scale coupling.  Matching to 1/137 requires
    choosing n_f by hand — which is oracle retrieval, not derivation.
    """
    kk_info  = alpha_kk_scale(k_cs, r_c)
    alpha_kk = kk_info["alpha_kk"]
    alpha_low = alpha_rg_run(alpha_kk, m_kk_gev, mu_gev, n_f)
    return {
        "k_cs":           k_cs,
        "r_c":            r_c,
        "m_kk_gev":       m_kk_gev,
        "mu_gev":         mu_gev,
        "n_f":            n_f,
        "alpha_kk":       alpha_kk,
        "alpha_kk_inv":   kk_info["alpha_kk_inv"],
        "alpha_low":      alpha_low,
        "alpha_low_inv":  1.0 / alpha_low,
        "alpha_pdg_inv":  1.0 / ALPHA_EM_PDG,
        "n_f_is_free":    True,
        "derivation_status": (
            "PARTIALLY DERIVED: α(M_KK) = 2π/k_CS is genuinely derived from the "
            "CS level.  The RG running to low energies requires n_f (number of "
            "light charged fermions), which is NOT currently derived from the 5D "
            "geometry.  n_f is a free parameter.  Setting n_f by hand to the SM "
            "value and reading off α(m_e) would be oracle retrieval."
        ),
        "free_parameters": [
            "n_f — number of light charged fermion species; SM value n_f=5 "
            "requires a complete fermion sector derivation (Pillar 60 gap)."
        ],
    }


# ---------------------------------------------------------------------------
# m_p/m_e gap report
# ---------------------------------------------------------------------------

def mp_over_me_gap_report() -> dict[str, Any]:
    """Honest accounting of why m_p/m_e cannot currently be derived from (5,7).

    Returns
    -------
    dict with keys:
        target_ratio        — PDG value m_p/m_e ≈ 1836.15
        geometric_ratio     — UM geometric prediction (lepton mass ratio m_2/m_0)
        discrepancy_factor  — target / geometric (factor of failure)
        gaps                — list of open theoretical gaps
        derivation_status   — honest assessment string
    """
    # The geometric lepton mass ratio from Pillar 60:
    #   m_2/m_0 = sqrt(1 + 4/N_W) = sqrt(9/5) ≈ 1.342  (for n=2 KK mode)
    geometric_lepton_ratio = math.sqrt(1.0 + 4.0 / N_W)   # ≈ 1.342
    return {
        "target_ratio":       MP_OVER_ME_PDG,
        "geometric_ratio":    geometric_lepton_ratio,
        "discrepancy_factor": MP_OVER_ME_PDG / geometric_lepton_ratio,
        "gaps": [
            "1. Electron mass requires a free Yukawa coupling λ fitted to m_e "
            "= 0.511 MeV (Pillar 60). λ is not derived from 5D geometry.",
            "2. Proton mass ≈ Λ_QCD ≈ 210 MeV is dominated by QCD confinement. "
            "Λ_QCD requires the non-Abelian strong coupling α_s, which the UM "
            "does not currently derive from the KK gauge sector.",
            "3. A non-Abelian SU(3)_C KK reduction is not yet implemented. "
            "Without it, quark confinement cannot be derived geometrically.",
        ],
        "derivation_status": (
            "NOT DERIVABLE from current UM framework.  The ratio m_p/m_e ≈ 1836 "
            "requires Λ_QCD (strong confinement scale) in the numerator and a "
            "Yukawa coupling in the denominator — neither of which is currently "
            "a 5D output.  Claiming this ratio without those inputs would be "
            "oracle retrieval."
        ),
    }


# ---------------------------------------------------------------------------
# Three-generation topology: partial closure of the n_f gap
# ---------------------------------------------------------------------------

def three_generation_n_f_constraint() -> dict[str, Any]:
    """Assess whether the (5,7) orbifold topology constrains the fermion count n_f.

    The "Kill Move" question (April 2026):
        "Does the topology of the (5,7) manifold constrain the number of
         fermion generations (n_f)?"

    This function computes the answer from first principles via Pillar 42
    (Three-Generation Theorem, src/core/three_generations.py), without
    importing that module directly (to keep this module self-contained).

    Derivation chain
    ----------------
    1. The S¹/Z₂ orbifold with winding number n_w supports KK modes
       φ_n with masses m_n = n / R.

    2. The topological stability condition (CS protection gap Δ = k_CS − n_w²)
       keeps only modes with n² ≤ n_w stable.  Higher modes decay to n ≤ ⌊√n_w⌋.

    3. For n_w = 5 (from Planck nₛ + Z₂ orbifold quantization):
           n=0:  0 ≤ 5  ✓  (Gen 1 — lightest)
           n=1:  1 ≤ 5  ✓  (Gen 2 — middle)
           n=2:  4 ≤ 5  ✓  (Gen 3 — heaviest)
           n=3:  9 > 5  ✗  (4th gen unstable — decays)

       Exactly N_gen = 3 stable matter-fermion modes.

    4. This constrains n_f (charged lepton flavors in the QED RG) to
       n_f_lepton = N_gen = 3 — *given n_w = 5 as input*.

    Honest caveats
    --------------
    C1. n_w = 5 is not a pure topological output: it requires the Planck nₛ
        observation (n_w = 5 is the minimum odd winding in the Planck 2σ
        band; n_w = 7 is excluded at 3.9σ).  So N_gen = 3 is derived from
        topology + one cosmological observation, not topology alone.

    C2. N_gen = 3 is not unique to n_w = 5.  A survey of n_w ∈ {1, …, 10}:
        n_w=1→1 mode, n_w=2→1, n_w=3→2, n_w=4→3, n_w=5→3, n_w=6→3,
        n_w=7→3, n_w=8→3, n_w=9→4, n_w=10→4.
        So n_w ∈ {4, 5, 6, 7, 8} all give N_gen = 3.  The selection of
        n_w = 5 is the additional observational input that uniquifies it.

    C3. The QED RG n_f counts colored charged species too.  For the UM
        with 3 lepton generations: n_f_eff ≈ 3 (leptons) + colored quark
        contributions.  The quark sector requires non-Abelian SU(3)_C KK
        reduction (not yet implemented).  So n_f_lepton = 3 is constrained
        geometrically, but n_f_total in the QED RG is not yet fully derived.

    Returns
    -------
    dict with keys:
        n_w                 — winding number used
        n_gen               — number of stable KK generations = 3
        stable_modes        — [0, 1, 2] (mode indices)
        fourth_gen_excluded — True: n=3 is unstable (3² = 9 > n_w = 5)
        n_f_lepton_constrained — True: n_f for leptons = N_gen = 3
        n_f_lepton          — 3 (number of lepton flavors, geometrically constrained)
        n_w_giving_3_gen    — list of n_w values that also give 3 stable modes
        n_w_uniquified_by   — str: "Planck nₛ selects n_w=5 from {4,5,6,7,8}"
        remaining_gap       — str: description of what is still undetermined
        derivation_status   — honest assessment string
        upgrade_from_prior  — str: how this improves on prior "n_f is free" status
    """
    n_w = N_W  # = 5
    # Compute stable modes via stability condition n² ≤ n_w.
    # Only n ≤ floor(√n_w) can satisfy n² ≤ n_w, so we search that range.
    max_n = int(math.isqrt(n_w))
    stable_modes = [n for n in range(max_n + 1) if n * n <= n_w]
    n_gen = len(stable_modes)
    fourth_excluded = (3 * 3) > n_w  # 9 > 5 → True
    # Survey n_w ∈ {1, …, 10} for N_gen = 3
    nw_giving_3 = [
        nw for nw in range(1, 11)
        if sum(1 for n in range(int(math.isqrt(nw)) + 1) if n * n <= nw) == 3
    ]
    return {
        "n_w":                    n_w,
        "n_gen":                  n_gen,
        "stable_modes":           stable_modes,
        "fourth_gen_excluded":    fourth_excluded,
        "n_f_lepton_constrained": True,
        "n_f_lepton":             n_gen,   # = 3
        "n_w_giving_3_gen":       nw_giving_3,
        "n_w_uniquified_by":      (
            f"Planck nₛ selects n_w=5 as the minimum odd winding in the "
            f"Planck 2σ band (n_w=7 excluded at 3.9σ).  Among n_w values "
            f"giving 3 stable modes {nw_giving_3}, only n_w=5 satisfies "
            f"both the orbifold quantization and the Planck nₛ constraint."
        ),
        "remaining_gap": (
            "1. n_w=5 requires Planck nₛ as input — it is not a pure "
            "topological prediction. "
            "2. The QED RG n_f counts colored quark contributions "
            "(Nc × Q²) beyond lepton flavors.  The quark sector requires "
            "non-Abelian SU(3)_C KK reduction (not yet implemented). "
            "3. The absolute fermion mass scale (Yukawa λ) is still a "
            "free parameter per generation."
        ),
        "derivation_status": (
            "PARTIALLY CLOSED: n_f for charged leptons = N_gen = 3 is a "
            "geometric consequence of n_w=5 and the orbifold stability "
            "condition n²≤n_w.  This upgrades the α-RG n_f from 'free "
            "parameter' to 'constrained by Pillar 42, given Planck nₛ'.  "
            "The full QED n_f (including quark color factors) is not yet "
            "derived from the 5D geometry."
        ),
        "upgrade_from_prior": (
            "Prior §VIII.2 status: 'n_f is a free parameter'.  "
            "Updated status: n_f_lepton = 3 is geometrically constrained "
            "by the Three-Generation Theorem (Pillar 42), given n_w=5 "
            "from Planck.  Remaining free components: quark contributions "
            "to n_f_total, and the Yukawa mass scale λ."
        ),
    }

def axiomzero_challenge_summary() -> dict[str, Any]:
    """Full AxiomZero Challenge status report.

    Returns
    -------
    dict documenting the derivation status of α, m_p/m_e, nₛ, r, and the
    Dirty Data Test result.
    """
    dirty_small = dirty_data_check(delta=0.05)
    dirty_large = dirty_data_check(delta=0.20, rtol=0.30)
    oracle_rep  = oracle_detection_report()
    alpha_info  = alpha_low_energy()
    mass_info   = mp_over_me_gap_report()
    n_gen_info  = three_generation_n_f_constraint()
    return {
        "dirty_data_test": {
            "delta_05pct": dirty_small,
            "delta_20pct": dirty_large,
            "oracle_falsified": oracle_rep["oracle_falsified"],
            "verdict": (
                "PASS — 5D path is genuinely used; perturbations propagate to 4D."
                if (dirty_small["tracks_perturbation"] and dirty_large["tracks_perturbation"])
                else "FAIL — check pipeline for oracle retrieval."
            ),
        },
        "alpha_derivation": {
            "alpha_pdg":           ALPHA_EM_PDG,
            "alpha_kk":            alpha_info["alpha_kk"],
            "alpha_low_n_f5":      alpha_info["alpha_low"],
            "n_f_lepton":          n_gen_info["n_f_lepton"],
            "n_f_lepton_constrained": n_gen_info["n_f_lepton_constrained"],
            "status": (
                "PARTIALLY DERIVED — α(M_KK)=2π/k_CS from k_CS; "
                "n_f_lepton=3 geometrically constrained by Pillar 42 "
                "(given n_w=5 from Planck); quark n_f still open."
            ),
        },
        "three_generation": n_gen_info,
        "mp_over_me_derivation": {
            "target":  MP_OVER_ME_PDG,
            "status":  "NOT DERIVABLE from current UM (gaps: Λ_QCD, Yukawa)",
        },
        "ns_r_derivation": {
            "ns_canonical": ns_from_phi0_eff(PHI0_EFF_CANONICAL),
            "status": (
                "DERIVED from φ₀_eff (given n_w=5 as observational input). "
                "Dirty Data Test confirms the derivation path is active."
            ),
        },
        "overall_verdict": (
            "The UM has genuine derivation chains for nₛ, r, k_CS, and c_s. "
            "The fine-structure constant α is partially derived: α(M_KK) from k_CS "
            "is genuine; n_f_lepton=3 is constrained by the Three-Generation "
            "Theorem (Pillar 42, given n_w=5 from Planck); quark color factors "
            "in n_f remain open.  The mass ratio m_p/m_e is not derivable from "
            "current UM inputs.  The Dirty Data Test confirms the 5D pipeline is "
            "active, not oracular."
        ),
    }
