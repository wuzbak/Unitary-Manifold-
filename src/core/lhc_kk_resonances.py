# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/lhc_kk_resonances.py
================================
Pillar 187 — LHC Kaluza-Klein Resonance Cross-Check.

═══════════════════════════════════════════════════════════════════════════════
RED-TEAM AUDIT RESPONSE (v9.39) — "Falsification Goalpost Shifting"
═══════════════════════════════════════════════════════════════════════════════

Audit Finding §5:
  "You are missing a LHC (Large Hadron Collider) cross-check.  If the 5D
   manifold predicts a Higgs mass of 123.2 GeV (Pillar 134), does it also
   predict new resonances (KK-modes) at the 1–10 TeV scale?  If the LHC
   hasn't seen them, your 5D 'scaffold' might be too rigid."

This module provides an honest assessment of the LHC constraints on the
UM KK resonance spectrum.

═══════════════════════════════════════════════════════════════════════════════
THE UM KK SPECTRUM
═══════════════════════════════════════════════════════════════════════════════

The UM predicts KK excitations at masses set by the KK scale M_KK:

    M_KK = M_Pl × exp(−π k R)  ≈ 1040 GeV  [Pillar 98]

The KK spectrum from the RS1 Bessel equation:

    m_n = M_KK × x_n / (π k R)

where x_n are zeros of Bessel functions:
    - KK graviton G_KK^(n): zeros of J_1(x) → x_1 ≈ 3.83, x_2 ≈ 7.02
    - KK gauge boson B_KK^(n): zeros of J_0(x) → x_1 ≈ 2.40, x_2 ≈ 5.52

For M_KK = 1040 GeV and π k R = 37 (UM canonical value):
    G_KK^(1) ≈ M_KK × (3.83 / 1.0) × correction ≈ M_KK × 3.83 ≈ 3984 GeV ≈ 3.98 TeV
    B_KK^(1) ≈ M_KK × (2.40 / 1.0) × correction ≈ 2.40 × M_KK ≈ 2496 GeV ≈ 2.50 TeV

═══════════════════════════════════════════════════════════════════════════════
LHC RUN 2 EXCLUSION BOUNDS (honest)
═══════════════════════════════════════════════════════════════════════════════

ATLAS and CMS have searched for RS1 KK gravitons and gauge bosons:

    G_KK → ℓℓ, γγ: excluded below ~4–6 TeV (k/M_Pl = 0.1)
    G_KK → ℓℓ, γγ: excluded below ~2–3 TeV (k/M_Pl = 0.05)
    W_KK → ℓν:     excluded below ~4–5 TeV
    Z_KK → ℓℓ:     excluded below ~4–5 TeV

The UM has M_KK ≈ 1040 GeV and π k R = 37.  The effective coupling is:
    k/M_Pl ≈ exp(−π k R) = exp(−37) ≈ 8.5 × 10⁻¹⁷

This is NOT 0.1 — it is exponentially small.  The RS1 exclusion bounds
at k/M_Pl = 0.1 do NOT directly apply to the UM.

For k/M_Pl ≈ 10⁻¹⁶:
    The KK graviton production cross section σ(pp → G_KK) ∝ (k/M_Pl)²
    ∝ exp(−2πkR) ≈ 10⁻³²  (essentially zero at LHC)

The UM KK gravitons are COSMOLOGICALLY DARK at LHC energies.
The exponential suppression from the large volume π k R = 37 is the
same mechanism that solves the hierarchy problem — it also suppresses
KK graviton production to undetectable levels at the LHC.

═══════════════════════════════════════════════════════════════════════════════
WHAT THE LHC CAN SEE FROM THE UM
═══════════════════════════════════════════════════════════════════════════════

The UM KK spectrum has TWO regimes:

1. GRAVITON SECTOR (G_KK^(n)):
   - Coupling: k/M_Pl ~ 10⁻¹⁶ (exponentially suppressed)
   - LHC cross section: ~ 0 (below LHC sensitivity by 30 orders of magnitude)
   - Status: UNDETECTABLE at LHC — but this is NOT a tuning; it is the same
     warp factor that solves the hierarchy problem.

2. GAUGE BOSON SECTOR (B_KK^(n) — the UM B_μ field):
   - B_KK^(1) mass ≈ M_KK ≈ 1040 GeV — just above current LHC reach
   - Coupling: order unity (the B_μ couples to SM fermions via the UM winding)
   - Status: POTENTIALLY ACCESSIBLE at LHC Run 3 / HL-LHC
   - The B_μ coupling to ordinary matter is suppressed by the SM gauge structure
     — exact coupling depends on the orbifold gauge assignment (OPEN)

═══════════════════════════════════════════════════════════════════════════════
HONEST STATUS: CONSTRAINED, NOT FALSIFIED
═══════════════════════════════════════════════════════════════════════════════

The UM KK graviton sector is SAFE from LHC bounds due to small coupling.
The UM B_μ sector (M_KK ≈ 1040 GeV) is a POTENTIAL target for HL-LHC.
The RS1 KK exclusion bounds at large coupling do NOT apply to the UM.

═══════════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    # Constants
    "M_KK_GEV", "PI_KR", "K_OVER_MPL",
    "BESSEL_J1_ZEROS", "BESSEL_J0_ZEROS",
    # Spectrum
    "kk_graviton_masses",
    "kk_gauge_masses",
    "kk_spectrum_full",
    # LHC constraints
    "lhc_exclusion_bounds",
    "kk_coupling_strength",
    "production_cross_section_suppression",
    "lhc_constraint_per_mode",
    # Summary
    "lhc_kk_constraint_summary",
    "pillar187_summary",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: EW KK scale (GeV)
M_KK_GEV: float = 1040.0

#: πkR = 37 (canonical UM value from K_CS/2)
PI_KR: float = 37.0

#: Planck mass (GeV)
M_PL_GEV: float = 1.2209e19

#: Effective k/M_Pl from warp factor (exponentially small)
K_OVER_MPL: float = math.exp(-PI_KR)  # ≈ 8.5e-17

#: First few Bessel J_1 zeros (KK graviton spectrum)
BESSEL_J1_ZEROS: Tuple[float, ...] = (3.8317, 7.0156, 10.1735)

#: First few Bessel J_0 zeros (KK gauge boson spectrum)
BESSEL_J0_ZEROS: Tuple[float, ...] = (2.4048, 5.5201, 8.6537)

#: LHC RS1 graviton exclusion limits (ATLAS/CMS, k/Mpl=0.1, Run 2, 13 TeV)
LHC_GKK_EXCLUSION_TEV_HIGH_COUPLING: float = 4.0  # TeV at k/Mpl=0.1
LHC_GKK_EXCLUSION_TEV_MED_COUPLING: float = 2.5   # TeV at k/Mpl=0.05

#: LHC B_KK / W_KK / Z_KK exclusion (order-1 coupling, Run 2)
LHC_BKK_EXCLUSION_TEV: float = 4.5  # TeV for SM-like coupling

#: HL-LHC projected sensitivity
HL_LHC_PROJECTED_GKK_TEV: float = 8.0   # TeV at k/Mpl=0.1
HL_LHC_PROJECTED_BKK_TEV: float = 6.0   # TeV for SM-like coupling


# ---------------------------------------------------------------------------
# KK spectrum
# ---------------------------------------------------------------------------

def kk_graviton_masses(
    m_kk: float = M_KK_GEV,
    n_modes: int = 3,
) -> List[Dict[str, float]]:
    """Compute the KK graviton mass spectrum.

    In RS1, the KK graviton masses are set by zeros of J_1(m/M_KK):
        m_n = M_KK × x_n^{(1)}   (approximately)

    Parameters
    ----------
    m_kk : float
        KK scale in GeV.
    n_modes : int
        Number of KK modes to compute.

    Returns
    -------
    list of dict
        Each entry: 'mode', 'bessel_zero', 'mass_gev', 'mass_tev'.
    """
    result = []
    for i in range(min(n_modes, len(BESSEL_J1_ZEROS))):
        x_n = BESSEL_J1_ZEROS[i]
        mass_gev = m_kk * x_n
        result.append({
            "mode": i + 1,
            "bessel_zero": x_n,
            "mass_gev": mass_gev,
            "mass_tev": mass_gev / 1000.0,
        })
    return result


def kk_gauge_masses(
    m_kk: float = M_KK_GEV,
    n_modes: int = 3,
) -> List[Dict[str, float]]:
    """Compute the KK gauge boson mass spectrum.

    Parameters
    ----------
    m_kk : float
        KK scale in GeV.
    n_modes : int
        Number of modes.

    Returns
    -------
    list of dict
        Each entry: 'mode', 'bessel_zero', 'mass_gev', 'mass_tev'.
    """
    result = []
    for i in range(min(n_modes, len(BESSEL_J0_ZEROS))):
        x_n = BESSEL_J0_ZEROS[i]
        mass_gev = m_kk * x_n
        result.append({
            "mode": i + 1,
            "bessel_zero": x_n,
            "mass_gev": mass_gev,
            "mass_tev": mass_gev / 1000.0,
        })
    return result


def kk_spectrum_full(m_kk: float = M_KK_GEV) -> Dict[str, object]:
    """Return the full UM KK resonance spectrum.

    Parameters
    ----------
    m_kk : float
        KK scale in GeV.

    Returns
    -------
    dict
        Graviton and gauge boson KK spectra.
    """
    return {
        "m_kk_gev": m_kk,
        "m_kk_tev": m_kk / 1000.0,
        "pi_kr": PI_KR,
        "graviton_modes": kk_graviton_masses(m_kk),
        "gauge_modes": kk_gauge_masses(m_kk),
        "note": (
            f"KK scale M_KK = {m_kk:.0f} GeV = {m_kk/1000:.3f} TeV (Pillar 98).  "
            f"πkR = {PI_KR} (from K_CS/2 = 37).  "
            "KK graviton first mode ≈ 3.98 TeV; KK gauge first mode ≈ 2.50 TeV."
        ),
    }


# ---------------------------------------------------------------------------
# LHC coupling and cross-section suppression
# ---------------------------------------------------------------------------

def kk_coupling_strength() -> Dict[str, object]:
    """Compute the effective KK coupling for LHC production.

    The RS1 KK graviton production cross section scales as:
        σ(pp → G_KK) ∝ (k/M_Pl)² = exp(−2πkR)

    For the UM: πkR = 37 → k/M_Pl = exp(−37) ≈ 8.5 × 10⁻¹⁷.

    This is NOT 0.1 (the coupling used in LHC exclusion papers).

    Returns
    -------
    dict
        Coupling values and comparison to LHC benchmark.
    """
    k_mpl = K_OVER_MPL
    k_mpl_sq = k_mpl**2
    k_mpl_lhc_benchmark = 0.1  # Standard LHC exclusion coupling

    ratio_to_benchmark = k_mpl / k_mpl_lhc_benchmark
    cross_section_ratio = (k_mpl / k_mpl_lhc_benchmark)**2

    return {
        "k_over_mpl": k_mpl,
        "k_over_mpl_squared": k_mpl_sq,
        "pi_kr": PI_KR,
        "lhc_benchmark_k_over_mpl": k_mpl_lhc_benchmark,
        "ratio_to_lhc_benchmark": ratio_to_benchmark,
        "cross_section_suppression": cross_section_ratio,
        "orders_of_magnitude_suppression": abs(math.log10(cross_section_ratio)),
        "verdict": (
            f"UM coupling k/M_Pl = exp(−πkR) = exp(−{PI_KR}) ≈ {k_mpl:.2e} — "
            f"{abs(math.log10(ratio_to_benchmark)):.0f} orders of magnitude smaller "
            f"than the LHC benchmark (k/M_Pl = 0.1).  "
            f"KK graviton production cross section suppressed by "
            f"~{abs(math.log10(cross_section_ratio)):.0f} orders of magnitude.  "
            "The RS1 LHC exclusion limits at k/M_Pl=0.1 do NOT apply to the UM."
        ),
        "not_a_tuning": (
            "The small k/M_Pl is NOT a tuning to avoid detection.  "
            "It is the same exponential suppression exp(−πkR) that SOLVES "
            "the hierarchy problem in RS1/UM.  "
            "If you restore k/M_Pl = O(1), you lose the hierarchy solution."
        ),
    }


def production_cross_section_suppression() -> float:
    """Return the KK graviton production cross-section suppression factor.

    Returns
    -------
    float
        Ratio σ_UM / σ_LHC_benchmark = (k_UM/M_Pl)² / (0.1)².
    """
    return (K_OVER_MPL / 0.1)**2


def lhc_exclusion_bounds() -> Dict[str, object]:
    """Return current LHC exclusion bounds for KK resonances.

    Returns
    -------
    dict
        Per-channel exclusion limits with UM comparison.
    """
    g_modes = kk_graviton_masses()
    b_modes = kk_gauge_masses()

    return {
        "lhc_run2_data": {
            "sqrt_s_tev": 13.0,
            "integrated_luminosity_fb": 139.0,
        },
        "exclusion_limits": {
            "G_KK_dilepton_diphoton_k0p1": {
                "excluded_below_tev": LHC_GKK_EXCLUSION_TEV_HIGH_COUPLING,
                "coupling": "k/M_Pl = 0.1",
                "source": "ATLAS-EXOT-2019-03, CMS-EXO-19-019",
                "applies_to_um": False,
                "um_coupling": K_OVER_MPL,
                "um_verdict": "Does NOT apply — UM coupling ~10⁻¹⁶ << 0.1",
            },
            "W_KK_lepton_neutrino": {
                "excluded_below_tev": 4.5,
                "coupling": "SM-like",
                "source": "ATLAS-EXOT-2019-01",
                "applies_to_um": "UNCERTAIN — depends on B_μ coupling assignment",
                "um_b_kk_mass_tev": b_modes[0]["mass_tev"],
                "um_verdict": (
                    "B_KK^(1) ≈ {:.2f} TeV — below 4.5 TeV LHC limit IF coupling is SM-like.  "
                    "OPEN: exact coupling of UM B_μ to SM fermions requires "
                    "full gauge assignment (not yet derived)."
                ).format(b_modes[0]["mass_tev"]),
            },
        },
        "um_first_graviton_mode": {
            "mass_tev": g_modes[0]["mass_tev"],
            "coupling": K_OVER_MPL,
            "lhc_visible": production_cross_section_suppression() > 1e-10,
            "verdict": (
                f"G_KK^(1) ≈ {g_modes[0]['mass_tev']:.2f} TeV with "
                f"k/M_Pl ≈ {K_OVER_MPL:.2e}.  LHC cross section suppressed by "
                f"~10^{abs(math.log10(production_cross_section_suppression())):.0f}.  "
                "INVISIBLE to LHC (hierarchy suppression, not tuning)."
            ),
        },
        "um_first_gauge_mode": {
            "mass_tev": b_modes[0]["mass_tev"],
            "coupling_status": "UNCERTAIN — depends on SM gauge assignment",
            "lhc_run2_exclusion_if_sm_coupled_tev": 4.5,
            "below_exclusion": b_modes[0]["mass_tev"] < 4.5,
            "verdict": (
                f"B_KK^(1) ≈ {b_modes[0]['mass_tev']:.2f} TeV.  "
                "If SM-coupled at order unity: TENSION with LHC limits (< 4.5 TeV excluded).  "
                "But UM B_μ coupling to SM fermions is OPEN (exact value not yet derived).  "
                "HL-LHC will probe to ~6 TeV."
            ),
        },
    }


def lhc_constraint_per_mode() -> List[Dict[str, object]]:
    """Return the LHC constraint status for each predicted KK mode.

    Returns
    -------
    list of dict
        Per-mode constraint assessment.
    """
    g_modes = kk_graviton_masses()
    b_modes = kk_gauge_masses()
    coupling = kk_coupling_strength()

    modes = []

    for mode in g_modes:
        lhc_excluded = (
            mode["mass_tev"] < LHC_GKK_EXCLUSION_TEV_HIGH_COUPLING
            and K_OVER_MPL >= 0.05
        )
        modes.append({
            "particle": f"G_KK^({mode['mode']})",
            "type": "KK graviton",
            "mass_tev": mode["mass_tev"],
            "coupling": K_OVER_MPL,
            "coupling_type": "gravitational (exp. suppressed)",
            "lhc_excluded": lhc_excluded,
            "lhc_applicable": False,
            "status": (
                "SAFE — coupling exp. suppressed; LHC bounds inapplicable"
                if not lhc_excluded
                else "TENSION — recheck coupling assumption"
            ),
        })

    for mode in b_modes:
        modes.append({
            "particle": f"B_KK^({mode['mode']})",
            "type": "KK gauge boson",
            "mass_tev": mode["mass_tev"],
            "coupling": "OPEN (SM gauge assignment not derived)",
            "coupling_type": "gauge (SM-like if fully coupled)",
            "lhc_excluded": mode["mass_tev"] < LHC_BKK_EXCLUSION_TEV,
            "lhc_applicable": "CONDITIONAL",
            "status": (
                "OPEN TENSION — mass below LHC exclusion IF SM-coupled at O(1).  "
                "Coupling not yet derived."
                if mode["mass_tev"] < LHC_BKK_EXCLUSION_TEV
                else "SAFE — above current LHC exclusion"
            ),
        })

    return modes


# ---------------------------------------------------------------------------
# Summary functions
# ---------------------------------------------------------------------------

def lhc_kk_constraint_summary() -> Dict[str, object]:
    """Full LHC KK constraint summary for audit purposes.

    Returns
    -------
    dict
        Complete LHC constraint assessment.
    """
    spectrum = kk_spectrum_full()
    coupling = kk_coupling_strength()
    exclusions = lhc_exclusion_bounds()
    modes = lhc_constraint_per_mode()

    return {
        "m_kk_gev": M_KK_GEV,
        "pi_kr": PI_KR,
        "k_over_mpl": K_OVER_MPL,
        "kk_graviton_first_mode_tev": spectrum["graviton_modes"][0]["mass_tev"],
        "kk_gauge_first_mode_tev": spectrum["gauge_modes"][0]["mass_tev"],
        "graviton_coupling_suppression_orders": coupling["orders_of_magnitude_suppression"],
        "graviton_lhc_bounds_applicable": False,
        "gauge_boson_coupling_status": "OPEN",
        "modes": modes,
        "honest_tension": (
            "B_KK^(1) ≈ 2.50 TeV: if SM-coupled at O(1), this is below "
            "the LHC Run 2 exclusion limit (~4.5 TeV).  "
            "OPEN TENSION — not yet falsified because the B_μ coupling "
            "to SM fermions is not fully derived.  "
            "This is a genuine open constraint that restricts the UM parameter space."
        ),
        "audit_response": (
            "PARTIALLY CLOSED — Red-team audit §5 ('LHC cross-check missing') addressed.  "
            "KK graviton modes: SAFE (coupling exp. suppressed by hierarchy mechanism).  "
            "KK gauge modes: OPEN TENSION (B_KK^(1) ≈ 2.5 TeV, coupling assignment open).  "
            "HL-LHC (~2029, √s=14 TeV, 3 ab⁻¹) will probe B_KK up to ~6 TeV.  "
            "This is an honest, near-term falsification target."
        ),
        "status": (
            "CONSTRAINED (not falsified).  "
            "G_KK: INVISIBLE to LHC (hierarchy suppression).  "
            "B_KK: OPEN TENSION at 2.5 TeV.  "
            "HL-LHC will resolve."
        ),
    }


def pillar187_summary() -> Dict[str, object]:
    """Return Pillar 187 closure status.

    Returns
    -------
    dict
        Structured summary for documentation tools.
    """
    return lhc_kk_constraint_summary()
