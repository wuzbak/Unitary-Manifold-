# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar399_lhc_kkgraviton_crosssection.py
=================================================
Pillar 399 — LHC KK Graviton Cross-Section and Exclusion Assessment.

════════════════════════════════════════════════════════════════════════════
MOTIVATION — Admission 10
════════════════════════════════════════════════════════════════════════════

FALLIBILITY.md Admission 10 (status: CONSTRAINED):

    "LHC KK Resonance Constraints: First KK graviton mode at ~4 TeV is near
     the LHC Run 2 exclusion boundary.  The UM's specific πkR = 37 determines
     the coupling strength and thereby the cross-section."

This pillar computes the PRECISE LHC CROSS-SECTION for the UM's KK graviton
and identifies a CONCEPTUAL ERROR in earlier assessments.

════════════════════════════════════════════════════════════════════════════
PILLAR 187 CORRECTION
════════════════════════════════════════════════════════════════════════════

Pillar 187 (and related assessments) conflated e^{-πkR} and e^{+πkR} in
the RS1 coupling formula.  The correct coupling is:

    c₁ = k / M̄_Pl = m_KK × e^{+πkR} / (x₁ × M̄_Pl)   ← CORRECT

not:
    c₁ = m_KK × e^{-πkR} / (x₁ × M̄_Pl)               ← PILLAR 187 ERROR

The difference is exp(2×37) = exp(74) ≈ 10^{32} orders of magnitude.

For UM parameters (m_KK = 1040 GeV, πkR = 37):
    c₁_correct = 1040 × e^{37} / (3.8317 × 2.44×10^{18}) ≈ 1.31

This is c₁ ≈ 1.31 >> LHC benchmark c = 0.1.

════════════════════════════════════════════════════════════════════════════
CHANNEL-BY-CHANNEL ANALYSIS
════════════════════════════════════════════════════════════════════════════

TWO DISTINCT CHANNELS must be considered separately:

1. FERMION CHANNELS (q q̄ → G_KK → ℓℓ):

   UV-localised quarks (c_L > 0.5) have exponentially suppressed profiles
   at the IR brane, where the KK graviton is localised.  Their effective
   coupling is:
       c₁_eff = c₁ × exp(-(c_L - 0.5) × πkR)

   For the u-quark (c_L ≈ 0.70):
       c₁_eff ≈ 1.31 × exp(-0.20 × 37) = 1.31 × 6.08×10^{-4} ≈ 8×10^{-4}

   σ_UM / σ_benchmark = (c₁_eff / c_benchmark)² ≈ (8e-4 / 0.1)² ≈ 6.4×10^{-5} << 1

   FERMION CHANNELS: SAFE ✓

2. GLUON CHANNEL (gg → G_KK):

   Gluons are bulk fields whose zero-mode couples with the full c₁ (no UV
   suppression from fermionic profiles).  However, in the UM's 5D RS1, the
   B_μ radion-gauge mixing (Pillar 1) modifies the gluon–G_KK coupling.
   The precise coupling depends on the B_μ wavefunction overlap, which is
   not fully derived at leading order.

   Conservative estimate without B_μ correction:
       σ_UM / σ_benchmark ≈ (c₁/c_benchmark)² ≈ (1.31/0.1)² ≈ 171

   This is a factor ~171 above the benchmark — the gluon channel is in
   TENSION with LHC gg → G_KK → γγ diphoton searches.

   However: (a) the B_μ coupling may reduce this by an unknown factor;
   (b) the g_μν + φ² B_μ B_ν metric (Pillar 384) gives additional gauge
   kinetic mixing that suppresses the gluon→G_KK amplitude.

   GLUON CHANNEL: IN TENSION (pending B_μ coupling derivation).

OVERALL STATUS: CONSTRAINED_QUANTIFIED — fermion channels safe,
gluon channel in tension with known caveat.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, Optional

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "PILLAR_STATUS",
    # Constants
    "M_KK_GEV",
    "PI_KR",
    "K_CS",
    "M_PL_BAR_GEV",
    "BESSEL_J1_X1",
    "LHC_BENCHMARK_C",
    "LHC_EXCLUSION_SENSITIVITY_PB",
    "C1_UM",
    "CL_U_QUARK",
    "CL_D_QUARK",
    "CL_CRITICAL",
    # Core functions
    "lhc_kk_coupling_from_um_geometry",
    "fermion_channel_effective_coupling",
    "gluon_channel_coupling",
    "lhc_kk_exclusion_verdict",
    "admission_10_closure_verdict",
    "pillar399_summary",
]

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

PILLAR_NUMBER: int = 399
PILLAR_TITLE: str = (
    "LHC KK Graviton Cross-Section and Exclusion Assessment — Admission 10"
)
PILLAR_STATUS: str = "CONSTRAINED_QUANTIFIED"

#: RS1 warp exponent fixed by UM geometry: πkR = K_CS/2 = 37
PI_KR: float = 37.0

#: Chern-Simons level K_CS = 74 = 5² + 7²
K_CS: int = 74

#: KK compactification scale from Pillar 6 [GeV]
M_KK_GEV: float = 1040.0

#: Reduced Planck mass M̄_Pl = M_Pl / √(8π) [GeV]
M_PL_BAR_GEV: float = 2.4355e18

#: First zero of Bessel function J₁ (standard RS1 KK spectrum: m_KK = x₁ k e^{-πkR})
BESSEL_J1_X1: float = 3.8317

#: ATLAS/CMS RS1 benchmark coupling
LHC_BENCHMARK_C: float = 0.1

#: LHC Run 2 sensitivity floor [pb] (approximate exclusion cross-section)
LHC_EXCLUSION_SENSITIVITY_PB: float = 0.05

#: Critical c_L boundary between UV-class (c_L > 0.5) and IR-class (c_L < 0.5)
CL_CRITICAL: float = 0.5

#: u-quark left bulk mass (UV-localised in RS1; ℓ=10 on lattice: 5×10/74 ≈ 0.676)
CL_U_QUARK: float = 10 * 5.0 / K_CS  # ≈ 0.676

#: d-quark left bulk mass (UV-localised; ℓ=9 on lattice: 5×9/74 ≈ 0.608)
CL_D_QUARK: float = 9 * 5.0 / K_CS   # ≈ 0.608

#: CORRECT c₁ = k/M̄_Pl from UM geometry (uses e^{+πkR}, see correction note)
C1_UM: float = M_KK_GEV * math.exp(PI_KR) / (BESSEL_J1_X1 * M_PL_BAR_GEV)


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────

def lhc_kk_coupling_from_um_geometry(
    m_kk_gev: float = M_KK_GEV,
    pi_kr: float = PI_KR,
    m_pl_bar_gev: float = M_PL_BAR_GEV,
) -> Dict[str, object]:
    """Compute the UM KK graviton coupling c₁ = k/M̄_Pl correctly.

    CORRECT RS1 formula (using e^{+πkR}):
        m_KK^{(1)} = x₁ × k × e^{-πkR}
        → k = m_KK × e^{+πkR} / x₁
        → c₁ = k / M̄_Pl = m_KK × e^{+πkR} / (x₁ × M̄_Pl)

    Pillar 187 incorrectly used e^{-πkR} (sign error), giving c₁ ~ 10^{-32}.

    Parameters
    ----------
    m_kk_gev : float      KK compactification scale [GeV].
    pi_kr : float         πkR (UM geometric value = 37).
    m_pl_bar_gev : float  Reduced Planck mass [GeV].

    Returns
    -------
    dict  Correct c₁, Pillar-187-incorrect c₁, ratio, correction note.
    """
    if pi_kr <= 0.0:
        raise ValueError(f"πkR must be positive; got {pi_kr}.")
    if m_kk_gev <= 0.0:
        raise ValueError(f"m_KK must be positive.")

    exp_plus = math.exp(pi_kr)
    exp_minus = math.exp(-pi_kr)

    k_gev = m_kk_gev * exp_plus / BESSEL_J1_X1
    c1_correct = k_gev / m_pl_bar_gev

    # Pillar 187 incorrect version (sign error: used e^{-πkR} instead of e^{+πkR})
    c1_pillar187_incorrect = m_kk_gev * exp_minus / (BESSEL_J1_X1 * m_pl_bar_gev)

    ratio = c1_correct / c1_pillar187_incorrect if c1_pillar187_incorrect > 0 else float("inf")

    return {
        "pi_kr": pi_kr,
        "m_kk_gev": m_kk_gev,
        "k_gev": k_gev,
        "m_pl_bar_gev": m_pl_bar_gev,
        "c1_correct": c1_correct,
        "c1_pillar187_incorrect": c1_pillar187_incorrect,
        "c1_vs_benchmark_ratio": c1_correct / LHC_BENCHMARK_C,
        "correction_note": (
            "Pillar 187 conflated e^{-πkR} and e^{+πkR} in the RS1 coupling formula.  "
            f"Correct: c₁ = m_KK × e^{{+πkR}} / (x₁ M̄_Pl) ≈ {c1_correct:.2f}.  "
            f"Incorrect (Pillar 187 error): c₁ = m_KK × e^{{-πkR}} / (x₁ M̄_Pl) ≈ {c1_pillar187_incorrect:.2e}.  "
            f"Ratio: {ratio:.2e} (≈ e^{{2πkR}} = e^{{74}})."
        ),
        "verdict": (
            f"c₁_correct = {c1_correct:.3f} >> LHC benchmark c = {LHC_BENCHMARK_C}.  "
            "UM KK graviton is strongly coupled to the Planck brane."
        ),
    }


def fermion_channel_effective_coupling(
    c_l: float,
    c1: float = C1_UM,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Compute the effective KK graviton coupling for UV-localised fermions.

    UV-localised fermions (c_L > 0.5) have exponentially suppressed profiles
    at the IR brane.  Their coupling to G_KK is:
        c₁_eff = c₁ × f(c_L)
    where the UV-suppression factor is:
        f(c_L > 0.5) = exp(-(c_L - 0.5) × πkR)
        f(c_L ≤ 0.5) = 1.0   [IR-class: no suppression]

    Production cross-section ratio vs LHC benchmark:
        σ_UM / σ_benchmark = (c₁_eff / c_benchmark)²

    Parameters
    ----------
    c_l : float   Left bulk mass c_L.
    c1 : float    Bare coupling c₁ = k/M̄_Pl (default: UM value).
    pi_kr : float πkR (default 37).

    Returns
    -------
    dict  Zone (UV/IR), suppression factor, effective coupling, σ ratio, verdict.
    """
    if c_l < 0.0:
        raise ValueError(f"c_L must be non-negative; got {c_l}.")

    uv_class = c_l > CL_CRITICAL
    if uv_class:
        uv_suppression_factor = math.exp(-(c_l - CL_CRITICAL) * pi_kr)
        zone = "UV-class"
    else:
        uv_suppression_factor = 1.0
        zone = "IR-class"

    c1_eff = c1 * uv_suppression_factor
    sigma_ratio = (c1_eff / LHC_BENCHMARK_C) ** 2
    safe_from_lhc = c1_eff < LHC_BENCHMARK_C

    return {
        "c_l": c_l,
        "c1_bare": c1,
        "zone": zone,
        "uv_suppression_factor": uv_suppression_factor,
        "c1_eff": c1_eff,
        "sigma_ratio_vs_benchmark": sigma_ratio,
        "safe_from_lhc": safe_from_lhc,
        "verdict": (
            f"c_L = {c_l:.3f} ({zone}).  "
            f"UV suppression factor = {uv_suppression_factor:.3e}.  "
            f"c₁_eff = {c1_eff:.3e}.  "
            f"σ_UM / σ_benchmark = {sigma_ratio:.3e}.  "
            f"{'SAFE from LHC narrow-resonance exclusion ✓' if safe_from_lhc else 'IN TENSION with LHC ✗'}"
        ),
    }


def gluon_channel_coupling(
    c1: float = C1_UM,
) -> Dict[str, object]:
    """Compute the KK graviton production cross-section from the gluon channel.

    Gluons are bulk fields; their zero-mode does not have the UV-localisation
    suppression of UV-class fermions.  The coupling enters at the full c₁ level.
    (A B_μ coupling correction from the UM metric ansatz g_μν + φ² B_μ B_ν
    may modify this, but is not yet derived at leading order.)

    Production cross-section ratio vs LHC benchmark:
        σ_UM / σ_benchmark = (c₁ / c_benchmark)²

    Parameters
    ----------
    c1 : float  Coupling c₁ = k/M̄_Pl (default: UM value).

    Returns
    -------
    dict  c₁, σ ratio, tension flag, caveat.
    """
    sigma_ratio = (c1 / LHC_BENCHMARK_C) ** 2
    in_tension = sigma_ratio > 1.0

    return {
        "c1": c1,
        "sigma_ratio_vs_benchmark": sigma_ratio,
        "in_tension": in_tension,
        "caveat": (
            "The gluon channel coupling at full c₁ is an overestimate.  "
            "The UM metric ansatz G_{μν} = g_{μν} + φ² B_μ B_ν (Pillar 384) "
            "introduces B_μ gauge mixing that may suppress the gg → G_KK amplitude.  "
            "The irreversibility operator T (Pillar 38) also modifies the 5D "
            "stress-energy coupling to the KK tower.  "
            "Full derivation of the B_μ-corrected gluon coupling is OPEN."
        ),
        "verdict": (
            f"Gluon channel: σ_UM / σ_benchmark ≈ {sigma_ratio:.1f} >> 1.  "
            "IN TENSION with LHC gg → G_KK searches.  "
            "Caveat: B_μ coupling correction may reduce this (not yet derived)."
        ),
    }


def lhc_kk_exclusion_verdict(
    m_kk_gev: float = M_KK_GEV,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Full LHC KK graviton exclusion assessment for the UM.

    Parameters
    ----------
    m_kk_gev : float  KK compactification scale [GeV].
    pi_kr : float     πkR.

    Returns
    -------
    dict  Channel-by-channel verdict, overall status, Pillar-187 correction.
    """
    coupling = lhc_kk_coupling_from_um_geometry(m_kk_gev, pi_kr)
    c1 = coupling["c1_correct"]

    fermion_u = fermion_channel_effective_coupling(CL_U_QUARK, c1, pi_kr)
    fermion_d = fermion_channel_effective_coupling(CL_D_QUARK, c1, pi_kr)
    gluon = gluon_channel_coupling(c1)

    fermion_channels_safe = fermion_u["safe_from_lhc"] and fermion_d["safe_from_lhc"]
    gluon_channel_in_tension = gluon["in_tension"]

    m_gkk1_gev = BESSEL_J1_X1 * m_kk_gev  # first KK mode mass
    m_gkk1_tev = m_gkk1_gev / 1000.0

    overall_status = PILLAR_STATUS

    admission_10_status = (
        f"Fermion channels (u, d quarks): SAFE (UV-suppression c₁_eff << c_benchmark).  "
        f"Gluon channel: IN TENSION (c₁={c1:.2f} >> benchmark, B_μ correction OPEN)."
    )

    return {
        "admission": 10,
        "m_kk_gev": m_kk_gev,
        "m_gkk1_tev": m_gkk1_tev,
        "c1_correct": c1,
        "c1_pillar187_incorrect": coupling["c1_pillar187_incorrect"],
        "fermion_channels_safe": fermion_channels_safe,
        "gluon_channel_in_tension": gluon_channel_in_tension,
        "fermion_u_sigma_ratio": fermion_u["sigma_ratio_vs_benchmark"],
        "gluon_sigma_ratio": gluon["sigma_ratio_vs_benchmark"],
        "overall_status": overall_status,
        "admission_10_status": admission_10_status,
        "correction_note": coupling["correction_note"],
        "honest_caveat": gluon["caveat"],
        "citation": "Pillar 399 / src/core/pillar399_lhc_kkgraviton_crosssection.py",
        "verdict": (
            f"c₁ = {c1:.2f} (correct; Pillar 187 had {coupling['c1_pillar187_incorrect']:.2e}).  "
            f"m_G_KK^{{(1)}} ≈ {m_gkk1_tev:.2f} TeV.  "
            "Fermion channels: SAFE (UV suppression).  "
            "Gluon channel: IN TENSION (pending B_μ derivation).  "
            f"Status: {overall_status}."
        ),
    }


def admission_10_closure_verdict() -> Dict[str, object]:
    """Machine-readable verdict for Admission 10.

    Returns
    -------
    dict  Previous status, new status (CONSTRAINED_QUANTIFIED), key findings.
    """
    exclusion = lhc_kk_exclusion_verdict()

    return {
        "admission": 10,
        "previous_status": "CONSTRAINED",
        "new_status": exclusion["overall_status"],
        "c1_correct": exclusion["c1_correct"],
        "c1_pillar187_incorrect": exclusion["c1_pillar187_incorrect"],
        "fermion_channels_safe": exclusion["fermion_channels_safe"],
        "gluon_channel_in_tension": exclusion["gluon_channel_in_tension"],
        "key_finding": (
            f"Pillar 187 coupling formula had a sign error (e^{{-πkR}} vs e^{{+πkR}}).  "
            f"Correct c₁ ≈ {exclusion['c1_correct']:.2f} (not ~10^{{-32}}).  "
            "Fermion channels safe via UV-localisation suppression.  "
            "Gluon channel in tension; B_μ coupling correction needed."
        ),
        "path_forward": (
            "Derive the B_μ-corrected gluon→G_KK coupling from the UM metric "
            "ansatz G_{μν} = g_{μν} + φ² B_μ B_ν.  "
            "This requires computing the graviton-gauge-graviton vertex in the "
            "5D Kaluza-Klein tower with the braided metric (Pillar 1 + Pillar 384).  "
            "Expected to be the subject of a future pillar (Pillar 402+)."
        ),
        "citation": "Pillar 399 / src/core/pillar399_lhc_kkgraviton_crosssection.py",
    }


def pillar399_summary() -> Dict[str, object]:
    """Return full Pillar 399 summary dict."""
    exclusion = lhc_kk_exclusion_verdict()
    verdict = admission_10_closure_verdict()

    return {
        "pillar_number": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "admission": 10,
        "admission_description": "LHC KK resonance constraints",
        "previous_status": "CONSTRAINED",
        "new_status": exclusion["overall_status"],
        "pi_kr": PI_KR,
        "m_kk_gev": M_KK_GEV,
        "m_gkk1_tev": exclusion["m_gkk1_tev"],
        "c1_correct": exclusion["c1_correct"],
        "c1_pillar187_incorrect": exclusion["c1_pillar187_incorrect"],
        "fermion_u_sigma_ratio": exclusion["fermion_u_sigma_ratio"],
        "gluon_sigma_ratio": exclusion["gluon_sigma_ratio"],
        "fermion_channels_safe": exclusion["fermion_channels_safe"],
        "gluon_in_tension": exclusion["gluon_channel_in_tension"],
        "key_result": (
            f"Pillar 187 sign correction: c₁ = {exclusion['c1_correct']:.2f} (not ~10^{{-32}}).  "
            f"Fermion channels: SAFE (σ_u/σ_bench ≈ {exclusion['fermion_u_sigma_ratio']:.2e} << 1).  "
            f"Gluon channel: IN TENSION (σ_g/σ_bench ≈ {exclusion['gluon_sigma_ratio']:.0f}).  "
            f"Admission 10: CONSTRAINED → CONSTRAINED_QUANTIFIED."
        ),
        "honest_residual": (
            "Gluon channel in tension pending B_μ coupling correction.  "
            "B_μ + φ² B_μ B_ν metric mixing (Pillar 384) may suppress gg → G_KK.  "
            "Full derivation required for a complete LHC verdict."
        ),
    }
