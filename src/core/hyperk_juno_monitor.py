# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
hyperk_juno_monitor.py — Hyper-K / JUNO Δm²₃₁ mass-splitting monitoring harness.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
Hyper-Kamiokande and JUNO will measure the atmospheric mass-squared
splitting Δm²₃₁ with ~0.5% precision (~2026–2030).

UM prediction (Pillar 17):
  Δm²₃₁ ≈ PDG × (1 − 0.075) ≈ 2.27 × 10⁻³ eV²
  (NLO T²/Z₃ geometric estimate — GEOMETRIC_ESTIMATE_CERTIFIED, ~7.5% below PDG)
  PDG 2023: Δm²₃₁ = 2.453 × 10⁻³ eV²

═══════════════════════════════════════════════════════════════════════════
FALSIFICATION CONDITIONS
═══════════════════════════════════════════════════════════════════════════
  • Δm²₃₁ ∉ [2.2, 2.7] × 10⁻³ eV² at σ < 1% → UM geometric estimate excluded

CURRENT STATUS:
  UM NLO value ≈ 2.27 × 10⁻³ eV² is ~7.5% below PDG centre.
  Within current ±1.3% PDG precision, this is a ~5.8σ discrepancy —
  documented as GEOMETRIC_ESTIMATE_CERTIFIED pending NLO refinement.

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Constants
    "DM2_31_PDG",
    "DM2_31_PDG_SIGMA_FRAC",
    "DM2_31_UM_NLO",
    "DM2_31_FALSIFICATION_WINDOW",
    "HYPERK_EXPECTED_SIGMA_FRAC",
    "JUNO_EXPECTED_SIGMA_FRAC",
    "HYPERK_FIRST_DATA",
    "JUNO_FIRST_DATA",
    # Baseline dicts
    "NUFIT_BASELINE",
    "UM_PREDICTION",
    # Functions
    "update_with_measurement",
    "falsification_verdict",
    "monitoring_report",
    "sensitivity_projection",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DM2_31_PDG: float = 2.453e-3           # eV², PDG 2023
DM2_31_PDG_SIGMA_FRAC: float = 0.013   # ~1.3% (current precision)
DM2_31_UM_NLO: float = 2.453e-3 * (1.0 - 0.075)   # NLO estimate, 7.5% below PDG

DM2_31_FALSIFICATION_WINDOW: tuple = (2.2e-3, 2.7e-3)  # eV²

HYPERK_EXPECTED_SIGMA_FRAC: float = 0.005  # 0.5% precision ~2030
JUNO_EXPECTED_SIGMA_FRAC: float = 0.005    # 0.5% precision ~2027

HYPERK_FIRST_DATA: int = 2027
JUNO_FIRST_DATA: int = 2026

# ---------------------------------------------------------------------------
# Baseline observational data
# ---------------------------------------------------------------------------

#: NuFIT / PDG 2023 baseline for Δm²₃₁
NUFIT_BASELINE: Dict = {
    "release": "PDG 2023 / NuFIT 5.3",
    "year": 2023,
    "reference": (
        "Particle Data Group (2023), Prog. Theor. Exp. Phys. 2022, 083C01; "
        "Esteban et al. (2020), NuFIT 5.3, JHEP 09 178"
    ),
    "dm2_31_central": DM2_31_PDG,
    "dm2_31_sigma_frac": DM2_31_PDG_SIGMA_FRAC,
    "dm2_31_sigma_abs": DM2_31_PDG * DM2_31_PDG_SIGMA_FRAC,
    "status": "CURRENT_BASELINE",
    "note": "Normal ordering (NH), Δm²₃₁ = Δm²₃₂ + Δm²₂₁ in NH",
}

#: UM prediction for Δm²₃₁
UM_PREDICTION: Dict = {
    "dm2_31_nlo": DM2_31_UM_NLO,
    "residual_fraction": -0.075,
    "mechanism": (
        "Δm²₃₁ from NLO T²/Z₃ geometric calculation (Pillar 17); "
        "LO contribution from 5D mass spectrum; "
        "NLO correction −7.5% from radion-neutrino mixing"
    ),
    "falsification": (
        "Δm²₃₁ ∉ [2.2, 2.7] × 10⁻³ eV² at σ < 1% → UM geometric estimate excluded"
    ),
    "current_residual_eV2": DM2_31_UM_NLO - DM2_31_PDG,
    "current_tension_sigma": abs(DM2_31_UM_NLO - DM2_31_PDG) / (DM2_31_PDG * DM2_31_PDG_SIGMA_FRAC),
    "current_status": "GEOMETRIC_ESTIMATE_CERTIFIED (~7.5% below PDG, NLO refinement pending)",
    "module": "src/ (Pillar 17 — neutrino_overlap_integrals_nlo.py)",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def _tension_frac(predicted: float, observed: float, sigma_frac: float) -> float:
    """Tension in σ using fractional uncertainty; inf if sigma_frac == 0."""
    sigma_abs = observed * sigma_frac if sigma_frac > 0 else 0.0
    return abs(predicted - observed) / sigma_abs if sigma_abs > 0 else float("inf")


def _tension_abs(predicted: float, observed: float, sigma_abs: float) -> float:
    """Tension in σ using absolute uncertainty; inf if sigma_abs == 0."""
    return abs(predicted - observed) / sigma_abs if sigma_abs > 0 else float("inf")


def update_with_measurement(
    dm2_31_obs: float,
    dm2_31_sigma_frac: float,
    experiment: str = "",
    year: int = 0,
) -> Dict:
    """Process a new Δm²₃₁ measurement and compare with UM prediction.

    Parameters
    ----------
    dm2_31_obs : float       Observed Δm²₃₁ central value [eV²].
    dm2_31_sigma_frac : float Fractional 1σ uncertainty (e.g. 0.01 for 1%).
    experiment : str         Experiment name (e.g. "Hyper-K Year 1").
    year : int               Year of the result.

    Returns
    -------
    dict with tension analysis and falsification verdict.
    """
    dm2_31_sigma_abs = dm2_31_obs * dm2_31_sigma_frac

    t_um = _tension_abs(DM2_31_UM_NLO, dm2_31_obs, dm2_31_sigma_abs)
    t_baseline_abs = DM2_31_PDG * DM2_31_PDG_SIGMA_FRAC
    t_baseline = _tension_abs(DM2_31_UM_NLO, DM2_31_PDG, t_baseline_abs)

    verdict = falsification_verdict(dm2_31_obs, dm2_31_sigma_frac)

    return {
        "experiment": experiment,
        "year": year,
        "dm2_31_obs": dm2_31_obs,
        "dm2_31_sigma_frac": dm2_31_sigma_frac,
        "dm2_31_sigma_abs": dm2_31_sigma_abs,
        "um_dm2_31_nlo": DM2_31_UM_NLO,
        "tension_sigma": t_um,
        "baseline_tension_sigma": t_baseline,
        "tension_improvement_sigma": t_baseline - t_um,
        "falsification_verdict": verdict,
        "overall_consistent": verdict["level"] == "CONSISTENT",
        "wording": (
            f"{experiment} ({year}): Δm²₃₁ = {dm2_31_obs:.4e} ± {dm2_31_sigma_frac*100:.1f}% eV². "
            f"UM NLO: {DM2_31_UM_NLO:.4e} eV² — tension {t_um:.2f}σ "
            f"(baseline: {t_baseline:.2f}σ from NuFIT). "
            f"{'Tension reduced ✅' if t_um < t_baseline else 'Tension increased ⚠️'}."
        ),
    }


def falsification_verdict(dm2_31_obs: float, dm2_31_sigma_frac: float) -> Dict:
    """Return falsification verdict for UM Δm²₃₁ NLO prediction.

    Parameters
    ----------
    dm2_31_obs : float        Observed Δm²₃₁ [eV²].
    dm2_31_sigma_frac : float Fractional 1σ uncertainty (e.g. 0.01 for 1%).

    Returns
    -------
    dict with falsification assessment.
    """
    dm2_31_sigma_abs = dm2_31_obs * dm2_31_sigma_frac
    tension = _tension_abs(DM2_31_UM_NLO, dm2_31_obs, dm2_31_sigma_abs)
    lo, hi = DM2_31_FALSIFICATION_WINDOW
    in_window = lo <= dm2_31_obs <= hi

    if tension < 1.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM Δm²₃₁ (NLO) within 1σ ✅"
    elif tension < 2.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM Δm²₃₁ (NLO) at {tension:.2f}σ ✅"
    elif tension < 3.0:
        level = "MARGINAL"
        verdict = f"MARGINAL — UM Δm²₃₁ (NLO) at {tension:.2f}σ ⚠️"
    else:
        level = "EXCLUDED"
        verdict = f"EXCLUDED — UM Δm²₃₁ (NLO) at {tension:.2f}σ 🔴"

    # Override: outside falsification window at high precision
    if not in_window and dm2_31_sigma_frac < 0.01 and level not in ("EXCLUDED",):
        level = "EXCLUDED"
        verdict = (
            f"EXCLUDED — Δm²₃₁={dm2_31_obs:.4e} eV² outside UM window "
            f"[{lo:.2e}, {hi:.2e}] eV² at σ={dm2_31_sigma_frac*100:.1f}% 🔴"
        )

    return {
        "parameter": "delta_m2_31",
        "um_prediction_nlo": DM2_31_UM_NLO,
        "observed": dm2_31_obs,
        "sigma_frac": dm2_31_sigma_frac,
        "sigma_abs": dm2_31_sigma_abs,
        "tension_sigma": tension,
        "in_falsification_window": in_window,
        "falsification_window": DM2_31_FALSIFICATION_WINDOW,
        "level": level,
        "verdict": verdict,
        "action_required": (
            "Document as HONEST_OPEN_PROBLEM in FALLIBILITY.md"
            if level in ("MARGINAL", "EXCLUDED")
            else "No action — within observational uncertainty"
        ),
    }


def monitoring_report() -> Dict:
    """Generate current monitoring report vs NuFIT baseline.

    Returns
    -------
    dict with full monitoring state.
    """
    verdict = falsification_verdict(DM2_31_PDG, DM2_31_PDG_SIGMA_FRAC)

    return {
        "version": "v10.17",
        "current_baseline": NUFIT_BASELINE,
        "um_prediction": UM_PREDICTION,
        "current_verdict": verdict,
        "falsification_summary": (
            f"UM Δm²₃₁ (NLO) = {DM2_31_UM_NLO:.4e} eV² vs PDG "
            f"{DM2_31_PDG:.4e} ± {DM2_31_PDG_SIGMA_FRAC*100:.1f}% eV² "
            f"({verdict['tension_sigma']:.2f}σ)"
        ),
        "next_milestone": {
            "experiments": ["JUNO", "Hyper-Kamiokande"],
            "juno_first_data": JUNO_FIRST_DATA,
            "hyperk_first_data": HYPERK_FIRST_DATA,
            "expected_sigma_frac": min(HYPERK_EXPECTED_SIGMA_FRAC, JUNO_EXPECTED_SIGMA_FRAC),
            "note": (
                f"JUNO first data ~{JUNO_FIRST_DATA}, Hyper-K ~{HYPERK_FIRST_DATA}. "
                f"Both expect σ(Δm²₃₁) ≈ 0.5%, providing a decisive test of UM NLO prediction."
            ),
        },
        "update_instructions": (
            "When results are available, call:\n"
            "  update_with_measurement(dm2_31_obs, dm2_31_sigma_frac, experiment, year)"
        ),
    }


def sensitivity_projection() -> Dict:
    """Project what Hyper-K / JUNO precision means for UM.

    Returns
    -------
    dict with sensitivity projections for both experiments.
    """
    lo, hi = DM2_31_FALSIFICATION_WINDOW

    def _project(sigma_frac: float, label: str, year: int) -> Dict:
        sigma_abs = DM2_31_PDG * sigma_frac
        t_if_pdg = _tension_abs(DM2_31_UM_NLO, DM2_31_PDG, sigma_abs)
        margin_lo = abs(DM2_31_UM_NLO - lo) / sigma_abs
        margin_hi = abs(DM2_31_UM_NLO - hi) / sigma_abs
        return {
            "experiment": label,
            "first_data_year": year,
            "expected_sigma_frac": sigma_frac,
            "expected_sigma_abs_eV2": sigma_abs,
            "tension_if_pdg_central_holds": t_if_pdg,
            "level_if_pdg_central_holds": (
                "CONSISTENT" if t_if_pdg < 2.0
                else "MARGINAL" if t_if_pdg < 3.0
                else "EXCLUDED"
            ),
            "margin_to_lower_window_edge_sigma": margin_lo,
            "margin_to_upper_window_edge_sigma": margin_hi,
            "note": (
                f"If Δm²₃₁ stays at PDG {DM2_31_PDG:.3e} eV² with σ={sigma_frac*100:.1f}%, "
                f"UM NLO tension = {t_if_pdg:.1f}σ."
            ),
        }

    return {
        "um_prediction_nlo_eV2": DM2_31_UM_NLO,
        "pdg_central_eV2": DM2_31_PDG,
        "falsification_window_eV2": DM2_31_FALSIFICATION_WINDOW,
        "juno": _project(JUNO_EXPECTED_SIGMA_FRAC, "JUNO", JUNO_FIRST_DATA),
        "hyperk": _project(HYPERK_EXPECTED_SIGMA_FRAC, "Hyper-Kamiokande", HYPERK_FIRST_DATA),
        "falsification_condition": (
            f"Δm²₃₁ ∉ [{lo:.2e}, {hi:.2e}] eV² at σ < 1% → UM geometric estimate excluded"
        ),
        "note_on_residual": (
            f"UM NLO is {abs(DM2_31_UM_NLO - DM2_31_PDG) / DM2_31_PDG * 100:.1f}% below PDG. "
            "If sub-percent measurements confirm PDG value, UM NLO requires revision. "
            "Full NLO calculation (beyond current estimate) may resolve the residual."
        ),
    }
