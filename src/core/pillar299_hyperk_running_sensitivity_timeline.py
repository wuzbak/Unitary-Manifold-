# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 299 — Hyper-Kamiokande Running Sensitivity Timeline.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Pillar 293 derived the UM proton lifetime predictions (τ(p→e⁺π⁰) and
τ(p→ν̄K⁺)) and preregistered the final Hyper-Kamiokande routing thresholds
for the 10-year exposure.  This module extends Pillar 293 by mapping the
UM predictions against the Hyper-K year-by-year exposure curve, providing:

  1. The year-by-year sensitivity timeline: at what year does Hyper-K first
     reach the UM prediction, and at what year does it definitively exclude it
     if not seen?
  2. A GUT model comparison table: UM vs. non-SUSY SU(5), SUSY SU(5), and
     SO(10), so that experimental context is clear.
  3. The nuclear matrix element sensitivity scan: bounding the UM lifetime
     range when the hadronic matrix element carries its ~30% lattice QCD
     uncertainty.
  4. Formal preregistration of year-by-year routing thresholds (locked at v11.10).

Hyper-Kamiokande exposure model
----------------------------------
Reference: Hyper-Kamiokande Design Report, arXiv:1805.04163 (Abe et al. 2018)

  Detector fiducial volume:  187 kton (initial configuration)
  Per-year exposure:         ~187 kton·yr
  Efficiency (p→e⁺π⁰):      ~85%  (estimate from published Monte Carlo)
  Efficiency (p→ν̄K⁺):       ~50%  (estimate)

  Year-by-year sensitivity (90% CL limit at 0 background events):
    τ/B(p→e⁺π⁰) > 2.3 × number_of_events_needed × exposure_ratio × M_GUT_factor

  The published Hyper-K design report gives:
    Year 1:   τ/B(p→e⁺π⁰) > ~5 × 10³⁴ yr  (design report Fig. 7.4)
    Year 5:   τ/B(p→e⁺π⁰) > ~1.5 × 10³⁵ yr
    Year 10:  τ/B(p→e⁺π⁰) > ~2 × 10³⁵ yr  (design report 90% CL sensitivity)

  The sensitivity grows approximately linearly with exposure (in the zero-
  background Poisson limit, τ_sens ∝ exposure = M × T × efficiency):
    τ_sens(t) = τ_sens_1yr × t   [for integer years t]

GUT model comparison for p → e⁺π⁰
-------------------------------------
  Theory                  | τ prediction           | Status (2026)
  ----------------------- | ---------------------- | -----------------
  Non-SUSY SU(5)          | ~(1–2) × 10³³ yr      | Super-K excluded
  SUSY SU(5) (minimal)    | ~(2–10) × 10³⁴ yr     | Hyper-K window
  SO(10) (non-SUSY)       | ~(3–8) × 10³⁴ yr      | Hyper-K window
  Unitary Manifold (UM)   | see Pillar 293         | Hyper-K window
  Flipped SU(5)           | ~(1–4) × 10³⁵ yr      | Hyper-K 5-10 yr

  Note: non-SUSY minimal SU(5) is already experimentally excluded by Super-K.
  The UM uses α_GUT = 3/74 ≈ 0.0405 (not the conventional 1/25 = 0.04), which
  shifts M_GUT by <1% from the standard SU(5) value, placing the UM in the
  same decade as SUSY SU(5) and SO(10).

Nuclear matrix element sensitivity
--------------------------------------
The hadronic matrix element |⟨π⁰|O|p⟩|² carries ~30% uncertainty from
lattice QCD calculations (see Aoki et al. 2017, Phys.Rev.D 96, 014506).
This enters τ as:

    τ ∝ M_GUT⁴ / (α_GUT² × |matrix_element|²)

A ±30% matrix element uncertainty → ±56% lifetime uncertainty
(since τ ∝ |ME|⁻², a 30% shift in ME → (1.3)² - 1 = 69% shift in τ).

Operationally:
    τ_upper = τ_central × (1 + 0.30)² ≈ τ_central × 1.69
    τ_lower = τ_central × (1 - 0.30)² ≈ τ_central × 0.49

This is incorporated into the year-by-year routing as a sensitivity band.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "HK_FIDUCIAL_KTON",
    "HK_EFFICIENCY_EPLUS_PI0",
    "HK_EFFICIENCY_NUBAR_KPLUS",
    "HK_START_YEAR",
    "HK_SENSITIVITY_1YR_EPLUS_PI0_YR",
    "HK_SENSITIVITY_10YR_EPLUS_PI0_YR",
    "SK_LIMIT_EPLUS_PI0_YR",
    "MATRIX_ELEMENT_UNCERTAINTY",
    "separation_guard",
    "hk_year_sensitivity",
    "hk_timeline",
    "matrix_element_sensitivity_band",
    "gut_model_comparison",
    "hk_yearly_routing",
    "proton_decay_timeline_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 299
PILLAR_TITLE: str = "Hyper-Kamiokande Running Sensitivity Timeline"

# Hyper-K detector parameters (arXiv:1805.04163)
HK_FIDUCIAL_KTON: float = 187.0          # fiducial volume in kton
HK_EFFICIENCY_EPLUS_PI0: float = 0.85    # detection efficiency p→e⁺π⁰
HK_EFFICIENCY_NUBAR_KPLUS: float = 0.50  # detection efficiency p→ν̄K⁺
HK_START_YEAR: int = 2024                # Hyper-K first beam (approximate)

# Hyper-K published sensitivities (arXiv:1805.04163, Table 7.1)
HK_SENSITIVITY_1YR_EPLUS_PI0_YR: float = 5.0e34   # τ/B 90%CL Year-1
HK_SENSITIVITY_10YR_EPLUS_PI0_YR: float = 1.0e35  # τ/B 90%CL Year-10

# Super-K current limit
SK_LIMIT_EPLUS_PI0_YR: float = 2.4e34   # Super-K 90%CL (2020)

# Nuclear matrix element uncertainty (lattice QCD, ±30%)
MATRIX_ELEMENT_UNCERTAINTY: float = 0.30


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 299."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "extends_pillar": 293,
        "experiment": "Hyper-Kamiokande",
        "analysis_type": "RUNNING_SENSITIVITY_TIMELINE",
    }


def hk_year_sensitivity(
    year: int,
    mode: str = "eplus_pi0",
) -> float:
    """Return the Hyper-K 90%CL lifetime sensitivity at a given year.

    The sensitivity grows linearly with exposure (zero-background Poisson
    regime): τ_sens(t) ≈ τ_sens_1yr × t.

    Parameters
    ----------
    year : int
        Year of operation (1-indexed, i.e., Year 1 = first year of data).
    mode : str
        Decay mode: "eplus_pi0" (p→e⁺π⁰) or "nubar_kplus" (p→ν̄K⁺).

    Returns
    -------
    float
        90%CL sensitivity in years.
    """
    if year < 1:
        raise ValueError("year must be ≥ 1")
    if mode == "eplus_pi0":
        return HK_SENSITIVITY_1YR_EPLUS_PI0_YR * year
    elif mode == "nubar_kplus":
        # Year-10 sensitivity is ~3.2e34 yr (design report); Year-1 = 3.2e33
        hk_1yr_nubar = 3.2e34 / 10.0
        return hk_1yr_nubar * year
    else:
        raise ValueError(f"Unknown mode: {mode!r}; use 'eplus_pi0' or 'nubar_kplus'")


def hk_timeline(
    tau_um_central: float,
    years: int = 10,
    mode: str = "eplus_pi0",
) -> List[Dict[str, object]]:
    """Map UM proton lifetime prediction against the Hyper-K year-by-year timeline.

    Parameters
    ----------
    tau_um_central : float
        UM central proton lifetime prediction (years).
    years : int
        Number of Hyper-K operational years to tabulate (default 10).
    mode : str
        Decay mode: "eplus_pi0" or "nubar_kplus".

    Returns
    -------
    List[Dict]
        Per-year routing table with sensitivity, UM status, and action.
    """
    timeline = []
    for yr in range(1, years + 1):
        sens = hk_year_sensitivity(yr, mode=mode)
        calendar_year = HK_START_YEAR + yr - 1
        # UM prediction relative to sensitivity
        if tau_um_central > sens:
            status = "UM_ABOVE_LIMIT"
            routing = "CONSISTENT"
            action = "No signal expected yet at current sensitivity; continue running."
        elif tau_um_central > SK_LIMIT_EPLUS_PI0_YR and mode == "eplus_pi0":
            # Between SK and HK year-N sensitivity
            status = "UM_AT_THRESHOLD"
            routing = "WATCH"
            action = f"UM prediction enters HK sensitivity window in Year {yr}."
        else:
            status = "UM_WITHIN_SENSITIVITY"
            routing = "OBSERVABLE_OR_EXCLUDED"
            action = (
                f"UM prediction τ={tau_um_central:.2e} yr within HK Year-{yr} "
                f"sensitivity {sens:.2e} yr. Signal expected or exclusion imminent."
            )
        timeline.append({
            "hk_year": yr,
            "calendar_year": calendar_year,
            "sensitivity_yr": sens,
            "tau_um_yr": tau_um_central,
            "um_above_sensitivity": tau_um_central > sens,
            "status": status,
            "routing": routing,
            "action": action,
        })
    return timeline


def matrix_element_sensitivity_band(tau_central: float) -> Dict[str, object]:
    """Compute the UM lifetime prediction band from nuclear matrix element uncertainty.

    The hadronic matrix element carries ±30% uncertainty (lattice QCD).
    Since τ ∝ |ME|⁻², the lifetime band is:
        τ_upper = τ_central × (1 + δ_ME)² = τ_central × 1.69
        τ_lower = τ_central × (1 - δ_ME)² = τ_central × 0.49

    Parameters
    ----------
    tau_central : float
        Central UM lifetime prediction (years).
    """
    delta = MATRIX_ELEMENT_UNCERTAINTY
    tau_upper = tau_central * (1.0 + delta) ** 2
    tau_lower = tau_central * (1.0 - delta) ** 2
    band_factor = tau_upper / tau_lower
    return {
        "tau_central_yr": tau_central,
        "matrix_element_uncertainty_pct": delta * 100.0,
        "tau_upper_yr": tau_upper,
        "tau_lower_yr": tau_lower,
        "band_factor": band_factor,
        "log10_tau_central": math.log10(tau_central),
        "log10_tau_upper": math.log10(tau_upper),
        "log10_tau_lower": math.log10(tau_lower),
        "note": (
            f"±{delta*100:.0f}% matrix element uncertainty → "
            f"lifetime band [{tau_lower:.2e}, {tau_upper:.2e}] yr "
            f"(factor of {band_factor:.2f})."
        ),
    }


def gut_model_comparison(tau_um: float) -> List[Dict[str, object]]:
    """Return the GUT model comparison table for p → e⁺π⁰ lifetime.

    Parameters
    ----------
    tau_um : float
        UM central proton lifetime prediction in years.
    """
    return [
        {
            "theory": "Non-SUSY SU(5) (minimal Georgi-Glashow)",
            "tau_range_yr": [1e33, 2e33],
            "tau_log10_range": [33.0, 33.3],
            "status_vs_sk": "EXCLUDED",
            "status_vs_hk": "EXCLUDED",
            "note": "SK 2020 limit 2.4×10³⁴ yr excludes this range.",
        },
        {
            "theory": "SUSY SU(5) (minimal)",
            "tau_range_yr": [2e34, 1e35],
            "tau_log10_range": [34.3, 35.0],
            "status_vs_sk": "VIABLE",
            "status_vs_hk": "IN_HK_WINDOW",
            "note": "Dominant mode in SUSY theories; HK Year 1–10 sensitive.",
        },
        {
            "theory": "SO(10) (non-SUSY)",
            "tau_range_yr": [3e34, 8e34],
            "tau_log10_range": [34.5, 34.9],
            "status_vs_sk": "VIABLE",
            "status_vs_hk": "IN_HK_WINDOW",
            "note": "Broad range; overlaps with UM in some parameter choices.",
        },
        {
            "theory": "Unitary Manifold (UM, this work)",
            "tau_range_yr": [tau_um * (1 - MATRIX_ELEMENT_UNCERTAINTY) ** 2,
                             tau_um * (1 + MATRIX_ELEMENT_UNCERTAINTY) ** 2],
            "tau_log10_range": [math.log10(tau_um * (1 - MATRIX_ELEMENT_UNCERTAINTY) ** 2),
                                math.log10(tau_um * (1 + MATRIX_ELEMENT_UNCERTAINTY) ** 2)],
            "tau_central_yr": tau_um,
            "status_vs_sk": "VIABLE" if tau_um > SK_LIMIT_EPLUS_PI0_YR else "SK_EXCLUDED",
            "status_vs_hk": "IN_HK_WINDOW" if tau_um < HK_SENSITIVITY_10YR_EPLUS_PI0_YR else "ABOVE_HK_10YR",
            "alpha_gut": 3.0 / 74.0,
            "alpha_gut_conventional": 1.0 / 25.0,
            "note": (
                "α_GUT = N_c/K_CS = 3/74 (CS-quantized, Pillar 148). "
                f"Central τ = {tau_um:.2e} yr. "
                "Band from ±30% lattice QCD matrix element uncertainty."
            ),
        },
        {
            "theory": "Flipped SU(5)",
            "tau_range_yr": [1e35, 4e35],
            "tau_log10_range": [35.0, 35.6],
            "status_vs_sk": "VIABLE",
            "status_vs_hk": "PARTIAL — upper range beyond HK 10-yr",
            "note": "HK Year 5–10 may probe the lower part of this range.",
        },
    ]


def hk_yearly_routing(
    tau_um: float,
    mode: str = "eplus_pi0",
) -> Dict[str, object]:
    """Preregistered year-by-year Hyper-K routing for the UM proton decay prediction.

    Returns the first year at which:
      (a) The UM prediction enters the HK sensitivity window (should see a signal)
      (b) A non-observation would constitute strong evidence against the UM

    Parameters
    ----------
    tau_um : float
        UM proton lifetime central value (years).
    mode : str
        Decay mode: "eplus_pi0" or "nubar_kplus".
    """
    first_year_in_window = None
    first_year_excluded = None
    for yr in range(1, 21):  # up to 20 years
        sens = hk_year_sensitivity(yr, mode=mode)
        if first_year_in_window is None and tau_um <= sens * 2.0:
            # UM prediction within 2× of sensitivity → entering window
            first_year_in_window = yr
        if first_year_excluded is None and tau_um <= sens:
            # HK sensitivity exceeds UM prediction → non-observation is tension
            first_year_excluded = yr

    sensitivity_band = matrix_element_sensitivity_band(tau_um)
    timeline = hk_timeline(tau_um, years=10, mode=mode)

    return {
        "tau_um_central_yr": tau_um,
        "mode": mode,
        "sk_limit_yr": SK_LIMIT_EPLUS_PI0_YR,
        "hk_1yr_sensitivity": HK_SENSITIVITY_1YR_EPLUS_PI0_YR,
        "hk_10yr_sensitivity": HK_SENSITIVITY_10YR_EPLUS_PI0_YR,
        "first_year_entering_window": first_year_in_window,
        "first_year_non_observation_tension": first_year_excluded,
        "matrix_element_band": sensitivity_band,
        "timeline": timeline,
        "preregistration_version": "v11.10",
        "preregistration_date": "2026-05-20",
        "routing_summary": (
            f"UM τ = {tau_um:.2e} yr ({mode}). "
            f"HK enters UM sensitivity window in Year {first_year_in_window}. "
            f"Non-observation becomes P-DECAY tension in Year {first_year_excluded}. "
            "P_DECAY_FALSIFIED if measured τ < current SK limit at ≥3σ."
        ),
    }


def proton_decay_timeline_report(tau_um_central: float = 5.0e34) -> Dict[str, object]:
    """Generate the complete Hyper-K running sensitivity timeline report.

    Parameters
    ----------
    tau_um_central : float
        UM central proton lifetime (years). Default is 5×10³⁴ yr, consistent
        with Pillar 293 derivation. The exact value depends on the hadronic
        matrix element; the band is captured by matrix_element_sensitivity_band().
    """
    guard = separation_guard()
    yearly = hk_yearly_routing(tau_um=tau_um_central, mode="eplus_pi0")
    nubar_routing = hk_yearly_routing(tau_um=tau_um_central * 11.8, mode="nubar_kplus")
    # τ(ν̄K⁺) ≈ τ(e⁺π⁰) × (1/|V_us|²) × f_kaon ≈ τ × (1/0.225²) × 0.60 ≈ τ × 11.85
    guts = gut_model_comparison(tau_um=tau_um_central)

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_guard": guard,
        "tau_um_central_yr": tau_um_central,
        "eplus_pi0_routing": yearly,
        "nubar_kplus_routing": nubar_routing,
        "gut_model_comparison": guts,
        "sk_current_limit_yr": SK_LIMIT_EPLUS_PI0_YR,
        "hk_1yr_sensitivity_yr": HK_SENSITIVITY_1YR_EPLUS_PI0_YR,
        "hk_10yr_sensitivity_yr": HK_SENSITIVITY_10YR_EPLUS_PI0_YR,
        "hk_start_year": HK_START_YEAR,
        "matrix_element_uncertainty_pct": MATRIX_ELEMENT_UNCERTAINTY * 100,
        "summary": (
            f"Hyper-K will probe UM τ(p→e⁺π⁰) = {tau_um_central:.2e} yr starting "
            f"Year {yearly['first_year_entering_window']} (calendar ~"
            f"{HK_START_YEAR + (yearly['first_year_entering_window'] or 5) - 1}). "
            "A non-observation by Year 10 would require M_GUT or α_GUT revision. "
            "Signal observation at correct lifetime would strongly support UM GUT sector."
        ),
        "status": "TIMELINE_PREREGISTERED",
        "label": "ADJACENT_TRACK",
    }
