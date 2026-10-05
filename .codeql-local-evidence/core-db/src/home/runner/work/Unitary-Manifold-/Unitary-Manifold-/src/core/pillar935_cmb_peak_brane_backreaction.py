# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 935 — CMB Acoustic Peak Amplitude: Brane-Backreaction Estimate.

🔵 ADJACENT TRACK — Non-hardgate.  Does not alter core 5D predictions.

═══════════════════════════════════════════════════════════════════════════
THE GAP THIS ADDRESSES
═══════════════════════════════════════════════════════════════════════════

Admission 2 in FALLIBILITY.md documents that the CMB acoustic peak
amplitude is suppressed by ×4–7 relative to the Planck 2018 spectrum.

Pillar 874 (Sprint BB) confirmed CMB_PEAK_AMPLITUDE_OPEN is an
architecture limit of the 5D zero-mode truncation.

Pillar 928 (Sprint BE) showed the n=1 KK tower contribution is
Boltzmann-negligible.

This pillar estimates whether brane-backreaction provides a correction
that could reduce the suppression factor.

METHOD
──────
In the Randall-Sundrum / KK framework the brane-to-brane propagator
receives a backreaction correction:

  ΔP_s / P_s = β_BR · (H/M_5)²

where:
  H = Hubble parameter during inflation ≈ 10^{-5} M_Pl
  M_5 = 5D Planck mass
  β_BR = brane backreaction coefficient (O(1) in RS models)

In the Unitary Manifold:
  M_5 = M_Pl / (2π R k_cs)^{1/2}
  R = compactification radius = 1/(k_cs · M_Pl)  (natural units)
  k_cs = 74

So M_5 / M_Pl = (2π R k_cs)^{-1/2} = 1 / sqrt(2π * 74 * 1/74)
              = 1 / sqrt(2π) ≈ 0.399

ΔP_s/P_s = β_BR · (H/M_5)² = β_BR · (H/M_Pl)² · (M_Pl/M_5)²
          = β_BR · 10^{-10} · 2π

This is an O(10^{-9}) correction — entirely negligible compared to the
×4–7 suppression.

HONEST RESULT
─────────────
CMB_BRANE_BACKREACTION_NEGLIGIBLE if |ΔP_s/P_s| < 0.01.
CMB_BRANE_BACKREACTION_SIGNIFICANT otherwise.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict

__all__ = [
    "N_W",
    "K_CS",
    "H_OVER_MPL",
    "MPL_OVER_M5_SQ",
    "BETA_BR",
    "DELTA_PS_OVER_PS",
    "BACKREACTION_NEGLIGIBLE",
    "CMB_SUPPRESSION_FACTOR_MIN",
    "CMB_SUPPRESSION_FACTOR_MAX",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "cmb_brane_backreaction",
    "cmb_br_summary",
]

N_W: int = 5
K_CS: int = 74

# Inflationary parameters
H_OVER_MPL: float = 1.0e-5          # H/M_Pl during inflation
BETA_BR: float = 1.0                 # O(1) brane backreaction coefficient (conservative)

# M_Pl / M_5 from 5D geometry
# M_5 / M_Pl = 1/sqrt(2π)  (see derivation above)
MPL_OVER_M5_SQ: float = 2.0 * math.pi   # (M_Pl/M_5)² = 2π

# Fractional correction to scalar power spectrum
DELTA_PS_OVER_PS: float = BETA_BR * (H_OVER_MPL ** 2) * MPL_OVER_M5_SQ
# ≈ 1.0 * 1e-10 * 6.283 ≈ 6.28e-10

BACKREACTION_NEGLIGIBLE: bool = DELTA_PS_OVER_PS < 0.01

# CMB amplitude suppression factor from zero-mode truncation (Admission 2)
CMB_SUPPRESSION_FACTOR_MIN: float = 4.0
CMB_SUPPRESSION_FACTOR_MAX: float = 7.0

PILLAR_NUMBER: int = 935
PILLAR_GATE: str = "CMB_PEAK_BRANE_BACKREACTION"


def cmb_brane_backreaction() -> Dict[str, Any]:
    """
    Estimate brane-backreaction correction to CMB acoustic peak amplitude.
    """
    if BACKREACTION_NEGLIGIBLE:
        status = "CMB_BRANE_BACKREACTION_NEGLIGIBLE"
        note = (
            f"Brane-backreaction correction ΔP_s/P_s ≈ {DELTA_PS_OVER_PS:.2e} "
            f"(O(10⁻¹⁰)) is negligible compared to the zero-mode suppression "
            f"factor ×{CMB_SUPPRESSION_FACTOR_MIN}–{CMB_SUPPRESSION_FACTOR_MAX}. "
            f"CMB_PEAK_AMPLITUDE_OPEN remains an irreducible architecture limit "
            f"of the 5D zero-mode truncation. No mechanism within the framework "
            f"reduces the ×4–7 suppression at the acoustic peaks."
        )
    else:
        status = "CMB_BRANE_BACKREACTION_SIGNIFICANT"
        note = (
            f"Brane-backreaction correction ΔP_s/P_s ≈ {DELTA_PS_OVER_PS:.2e} "
            "is significant — revisit parameter estimates."
        )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": status,
        "delta_ps_over_ps": DELTA_PS_OVER_PS,
        "backreaction_negligible": BACKREACTION_NEGLIGIBLE,
        "h_over_mpl": H_OVER_MPL,
        "mpl_over_m5_sq": MPL_OVER_M5_SQ,
        "beta_br": BETA_BR,
        "suppression_factor_range": (CMB_SUPPRESSION_FACTOR_MIN, CMB_SUPPRESSION_FACTOR_MAX),
        "architecture_limit_confirmed": BACKREACTION_NEGLIGIBLE,
        "note": note,
    }


PILLAR_STATUS: str = cmb_brane_backreaction()["status"]


def cmb_br_summary() -> Dict[str, Any]:
    """Return pillar summary dict."""
    res = cmb_brane_backreaction()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "delta_ps_over_ps": DELTA_PS_OVER_PS,
        "architecture_limit_confirmed": res["architecture_limit_confirmed"],
    }
