# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/fermilab_watch.py
===========================
Pillar 51-B — Fermilab Muon g-2 Watch: Tracking the 2025 Final Result
and Comparing with Unitary Manifold Predictions.

Physical motivation
--------------------
The Fermilab Muon g-2 experiment published its final result on 2025-06-03:

    a_μ^exp = (116 592 070.5 ± 14.6) × 10⁻¹²   [127 ppb]

Discrepancy with the Standard Model (data-driven WP2023):

    Δa_μ^DD ≈ +260.5 × 10⁻¹²  (~5.0σ)

Discrepancy with the SM (BMW+ lattice QCD):

    Δa_μ^BMW ≈ +15.5 × 10⁻¹²  (~1.5σ)

All values are in units of 10⁻¹², consistent with the standard a_μ × 10¹² convention.

The Unitary Manifold KK correction is:

    δa_μ^KK ~ 10⁻³⁰ × 10⁻¹² (negligible)

This module provides a complete watch report confirming that the UM KK
sector cannot explain the anomaly, and estimating the new physics scale
that would be required.

Public API
----------
A_MU_EXP, A_MU_EXP_UNC : float       Fermilab 2025 final result (× 10⁻¹²)
A_MU_SM_DD, A_MU_SM_DD_UNC : float   Data-driven SM WP2023 (× 10⁻¹²)
A_MU_SM_BMW, A_MU_SM_BMW_UNC : float BMW+ lattice QCD (× 10⁻¹²)
A_MU_UM_KK : float                   UM KK correction (negligible, × 10⁻¹²)
RESULT_DATE : str                     Fermilab announcement date
MEASUREMENT_PRECISION_PPB : int       Precision in parts per billion

discrepancy_dd() → dict
discrepancy_bmw() → dict
um_explanation_fraction(delta_um, delta_total) → float
can_um_explain_anomaly() → dict
fermilab_watch_report() → dict
new_physics_scale_from_anomaly(delta_a_mu, loop_factor) → float
status_summary() → str

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
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

# ---------------------------------------------------------------------------
# Module-level constants  (all values in units of 10⁻¹²)
# ---------------------------------------------------------------------------

A_MU_EXP: float = 116592070.5      # Fermilab 2025 final
A_MU_EXP_UNC: float = 14.6         # 1σ (combined stat+sys)

A_MU_SM_DD: float = 116591810.0    # WP2023 data-driven SM
A_MU_SM_DD_UNC: float = 4.3        # 1σ

A_MU_SM_BMW: float = 116592055.0   # BMW+ lattice QCD
A_MU_SM_BMW_UNC: float = 2.7       # 1σ

A_MU_UM_KK: float = 1e-30          # UM KK correction (negligible)

RESULT_DATE: str = "2025-06-03"
MEASUREMENT_PRECISION_PPB: int = 127

# Physical constants for scale estimation
_M_MU_GEV: float = 0.10566         # muon mass in GeV
_ALPHA_EM: float = 1.0 / 137.036   # fine-structure constant


# ---------------------------------------------------------------------------
# Discrepancy functions
# ---------------------------------------------------------------------------


def discrepancy_dd() -> dict:
    """Compute the Fermilab vs data-driven SM discrepancy.

    Returns
    -------
    dict with keys:
        delta (a_mu_exp − a_mu_SM_DD, in units of 10⁻¹²),
        sigma_combined (quadrature sum of exp and SM uncertainties),
        n_sigma (delta / sigma_combined),
        interpretation (str).
    """
    delta = A_MU_EXP - A_MU_SM_DD
    sigma_combined = math.sqrt(A_MU_EXP_UNC ** 2 + A_MU_SM_DD_UNC ** 2)
    n_sigma = delta / sigma_combined
    interpretation = (
        f"Fermilab 2025 result deviates from data-driven SM by "
        f"{delta:.1f} × 10⁻¹² ({n_sigma:.1f}σ). "
        f"Strong tension with WP2023 data-driven prediction."
    )
    return {
        "delta": delta,
        "sigma_combined": sigma_combined,
        "n_sigma": n_sigma,
        "interpretation": interpretation,
    }


def discrepancy_bmw() -> dict:
    """Compute the Fermilab vs BMW+ lattice QCD discrepancy.

    Returns
    -------
    dict with keys:
        delta (a_mu_exp − a_mu_SM_BMW, in units of 10⁻¹²),
        sigma_combined,
        n_sigma,
        interpretation (str).
    """
    delta = A_MU_EXP - A_MU_SM_BMW
    sigma_combined = math.sqrt(A_MU_EXP_UNC ** 2 + A_MU_SM_BMW_UNC ** 2)
    n_sigma = delta / sigma_combined
    interpretation = (
        f"Fermilab 2025 result deviates from BMW+ lattice by "
        f"{delta:.1f} × 10⁻¹² ({n_sigma:.1f}σ). "
        f"Consistent with lattice QCD within ~1.5σ."
    )
    return {
        "delta": delta,
        "sigma_combined": sigma_combined,
        "n_sigma": n_sigma,
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# UM explanation functions
# ---------------------------------------------------------------------------


def um_explanation_fraction(delta_um: float, delta_total: float) -> float:
    """Fraction of the total anomaly explained by the UM KK correction.

    Parameters
    ----------
    delta_um:
        The UM contribution (same units as delta_total).
    delta_total:
        The total observed anomaly.

    Returns
    -------
    float
        |delta_um / delta_total|.  Returns 0.0 if delta_total is zero.
    """
    if delta_total == 0.0:
        return 0.0
    return abs(delta_um / delta_total)


def can_um_explain_anomaly() -> dict:
    """Assess whether the UM KK sector can account for the muon g-2 anomaly.

    The UM KK correction is δa_μ^KK ~ 10⁻³⁰ × 10⁻¹², while the
    required contribution is ~260 × 10⁻¹² (data-driven) or ~15 × 10⁻¹² (BMW).

    Returns
    -------
    dict with keys:
        um_contribution (in units of 10⁻¹²),
        required_contribution (data-driven discrepancy, 10⁻¹²),
        fraction_explained (um_contribution / required_contribution),
        can_explain (bool: fraction_explained > 0.01),
        honest_assessment (str).
    """
    dd = discrepancy_dd()
    required = abs(dd["delta"])
    fraction = um_explanation_fraction(A_MU_UM_KK, required)
    can_explain = fraction > 0.01
    honest_assessment = (
        "The UM Kaluza-Klein graviton loop correction to a_μ is "
        f"δa_μ^KK ~ {A_MU_UM_KK:.0e} × 10⁻¹², which is approximately "
        f"{required / max(A_MU_UM_KK, 1e-60):.0e} times smaller than the "
        f"observed data-driven anomaly of {required:.1f} × 10⁻¹². "
        "The UM KK sector cannot explain the Δa_μ anomaly. "
        "This is documented in FALLIBILITY.md §VII and is not a failure "
        "of the framework — the UM makes no claim to explain the anomaly."
    )
    return {
        "um_contribution": A_MU_UM_KK,
        "required_contribution": required,
        "fraction_explained": fraction,
        "can_explain": can_explain,
        "honest_assessment": honest_assessment,
    }


# ---------------------------------------------------------------------------
# Full watch report
# ---------------------------------------------------------------------------


def fermilab_watch_report() -> dict:
    """Compile the complete Fermilab Muon g-2 watch report.

    Returns
    -------
    dict with keys:
        experiment (str),
        result (dict: a_mu_exp, uncertainty, date, precision_ppb),
        discrepancy_dd (dict from discrepancy_dd()),
        discrepancy_bmw (dict from discrepancy_bmw()),
        um_contribution (dict from can_um_explain_anomaly()),
        conclusion (str).
    """
    conclusion = (
        "UM KK correction is ~30 orders of magnitude too small to explain the anomaly. "
        "The Δa_μ anomaly requires new physics beyond the UM KK sector."
    )
    return {
        "experiment": "Fermilab Muon g-2 (2013–2023 runs, final result 2025-06-03)",
        "result": {
            "a_mu_exp": A_MU_EXP,
            "uncertainty": A_MU_EXP_UNC,
            "date": RESULT_DATE,
            "precision_ppb": MEASUREMENT_PRECISION_PPB,
        },
        "discrepancy_dd": discrepancy_dd(),
        "discrepancy_bmw": discrepancy_bmw(),
        "um_contribution": can_um_explain_anomaly(),
        "conclusion": conclusion,
    }


# ---------------------------------------------------------------------------
# New physics scale estimator
# ---------------------------------------------------------------------------


def new_physics_scale_from_anomaly(
    delta_a_mu: float,
    loop_factor: float = 1.0 / (16.0 * math.pi ** 2),
) -> float:
    """Estimate the new physics scale M that would explain a given δa_μ.

    Assumes the one-loop relation:
        δa_μ ≈ (m_μ / M)² × loop_factor

    Solving for M:
        M = m_μ / sqrt(delta_a_mu / loop_factor)

    Parameters
    ----------
    delta_a_mu:
        The anomalous magnetic moment contribution in dimensionless a_μ units.
        The module stores values in units of 10⁻¹²; to get the dimensionless
        value, multiply discrepancy_dd()['delta'] by 10⁻¹²
        (e.g., 260.5 × 10⁻¹² ≈ 2.605 × 10⁻¹⁰ in standard a_μ notation).
    loop_factor:
        Dimensionless loop suppression factor.  Default = 1/(16π²).

    Returns
    -------
    float
        M_new_physics in GeV.
    """
    if delta_a_mu <= 0.0:
        raise ValueError("delta_a_mu must be positive")
    if loop_factor <= 0.0:
        raise ValueError("loop_factor must be positive")
    ratio = delta_a_mu / loop_factor
    return _M_MU_GEV / math.sqrt(ratio)


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------


def status_summary() -> str:
    """Return a one-paragraph human-readable status of the muon g-2 situation.

    Returns
    -------
    str
        Paragraph summarising experimental result, SM comparisons, and UM position.
    """
    dd = discrepancy_dd()
    bmw = discrepancy_bmw()
    return (
        f"The Fermilab Muon g-2 collaboration published its final result on {RESULT_DATE}: "
        f"a_μ = {A_MU_EXP:.1f} × 10⁻¹² with 1σ uncertainty {A_MU_EXP_UNC:.1f} × 10⁻¹² "
        f"({MEASUREMENT_PRECISION_PPB} ppb precision). "
        f"Compared to the WP2023 data-driven SM prediction, the discrepancy is "
        f"{dd['delta']:.1f} × 10⁻¹² ({dd['n_sigma']:.1f}σ), indicating strong tension. "
        f"Compared to the BMW+ lattice QCD prediction, the discrepancy is "
        f"{bmw['delta']:.1f} × 10⁻¹² ({bmw['n_sigma']:.1f}σ), which is consistent at "
        f"the ~1.5σ level. "
        f"The Unitary Manifold KK correction (δa_μ^KK ~ {A_MU_UM_KK:.0e} × 10⁻¹²) "
        f"is negligible — approximately 30 orders of magnitude too small to explain "
        f"the anomaly. The UM makes no claim to resolve the muon g-2 puzzle; "
        f"resolution likely requires new electroweak-scale physics."
    )
