# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/litebird_forecast.py
==============================
Pillar 45-D — LiteBIRD Enhanced Forecast: Full Observational Prediction
with Uncertainty Bands for the Birefringence Measurement.

Physical motivation
--------------------
The Unitary Manifold makes four quantitative predictions for the CMB
birefringence angle β measurable by the LiteBIRD satellite (launch ~2032):

    β_canonical  = 0.273°   (primary SOS resonance)
    β_derived    = 0.331°   (secondary: braided causal-order mixing)
    β_full_1     ≈ 0.290°   (with Kibble-Zurek correction)
    β_full_2     ≈ 0.351°   (with full (5,7) + CS-mixing correction)

This module provides the full statistical machinery to evaluate:
  * Gaussian likelihoods for each prediction
  * Combined mixture likelihood over all four peaks
  * Detection significance for any measured value
  * Forecast scenarios covering confirmation and falsification
  * Full theoretical uncertainty budget
  * Detection power to distinguish the two canonical peaks
  * Timeline from launch to published result

The Falsification Criterion
-----------------------------
The theory is falsified if the measured β is:
  (a) outside the admissible window [0.22°, 0.38°], OR
  (b) inside the predicted forbidden gap [0.29°, 0.31°].

Public API
----------
BETA_CANONICAL, BETA_DERIVED, BETA_FULL_1, BETA_FULL_2 : float
SIGMA_LITEBIRD, SIGMA_THEORY : float
GAP_LOWER, GAP_UPPER : float
ADMISSIBLE_LOWER, ADMISSIBLE_UPPER : float
LAUNCH_YEAR, N_PEAKS : int

gaussian_likelihood(beta_measured, beta_predicted, sigma) → float
combined_likelihood(beta_measured, betas_predicted, weights, sigma_litebird) → float
detection_significance(beta_measured, sigma_measurement) → dict
forecast_scenarios() → dict
uncertainty_budget() → dict
detection_power(n_sigma_threshold) → dict
timeline_to_result() → dict

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
from typing import Sequence

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

BETA_CANONICAL: float = 0.273   # degrees — primary SOS resonance
BETA_DERIVED: float = 0.331     # degrees — braided causal-order mixing
BETA_FULL_1: float = 0.290      # degrees — with Kibble-Zurek correction
BETA_FULL_2: float = 0.351      # degrees — with full (5,7)+CS-mixing correction

SIGMA_LITEBIRD: float = 0.02    # degrees — LiteBIRD 1σ measurement uncertainty
SIGMA_THEORY: float = 0.01      # degrees — theoretical 1σ uncertainty

GAP_LOWER: float = 0.29         # degrees — lower edge of forbidden gap
GAP_UPPER: float = 0.31         # degrees — upper edge of forbidden gap

ADMISSIBLE_LOWER: float = 0.22  # degrees — minimum admissible β
ADMISSIBLE_UPPER: float = 0.38  # degrees — maximum admissible β

LAUNCH_YEAR: int = 2032
N_PEAKS: int = 4

# Internal: ordered list of the four predicted peaks
_PREDICTED_BETAS: tuple[float, ...] = (
    BETA_CANONICAL, BETA_FULL_1, BETA_DERIVED, BETA_FULL_2
)

_SQRT_2PI: float = math.sqrt(2.0 * math.pi)

# ---------------------------------------------------------------------------
# Core statistical functions
# ---------------------------------------------------------------------------


def gaussian_likelihood(
    beta_measured: float,
    beta_predicted: float,
    sigma: float,
) -> float:
    """Evaluate a normalised Gaussian likelihood.

    Parameters
    ----------
    beta_measured:
        Observed (or hypothetical) birefringence angle in degrees.
    beta_predicted:
        Predicted central value in degrees.
    sigma:
        Total 1σ uncertainty in degrees.

    Returns
    -------
    float
        L = exp(-z²/2) / (sqrt(2π) × sigma),  where z = (beta_measured − beta_predicted)/sigma.
    """
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    z = (beta_measured - beta_predicted) / sigma
    return math.exp(-0.5 * z * z) / (_SQRT_2PI * sigma)


def combined_likelihood(
    beta_measured: float,
    betas_predicted: Sequence[float] | None = None,
    weights: Sequence[float] | None = None,
    sigma_litebird: float = SIGMA_LITEBIRD,
) -> float:
    """Evaluate the mixture (combined) Gaussian likelihood over all predicted peaks.

    Each component has a total uncertainty
        sigma_i = sqrt(sigma_litebird² + sigma_theory²).

    Parameters
    ----------
    beta_measured:
        Observed (or hypothetical) birefringence angle in degrees.
    betas_predicted:
        Sequence of predicted central values.  Defaults to all four UM peaks.
    weights:
        Mixture weights; must sum to 1.  Defaults to equal weights.
    sigma_litebird:
        Instrumental 1σ uncertainty.  Defaults to SIGMA_LITEBIRD.

    Returns
    -------
    float
        Weighted sum of Gaussian likelihoods.
    """
    if betas_predicted is None:
        betas_predicted = _PREDICTED_BETAS
    n = len(betas_predicted)
    if weights is None:
        weights = [1.0 / n] * n
    if len(weights) != n:
        raise ValueError("weights and betas_predicted must have the same length")

    sigma_total = math.sqrt(sigma_litebird ** 2 + SIGMA_THEORY ** 2)
    result = sum(
        w * gaussian_likelihood(beta_measured, bp, sigma_total)
        for w, bp in zip(weights, betas_predicted)
    )
    return result


def detection_significance(
    beta_measured: float,
    sigma_measurement: float = SIGMA_LITEBIRD,
) -> dict:
    """Compute detection significance metrics for a measured β.

    Parameters
    ----------
    beta_measured:
        The measured birefringence angle in degrees.
    sigma_measurement:
        The measurement 1σ uncertainty in degrees.

    Returns
    -------
    dict with keys:
        beta_measured, sigma_measurement,
        best_peak (nearest predicted β),
        sigma_offset (|beta_measured − best_peak| / sigma_measurement),
        in_admissible_window (bool),
        in_forbidden_gap (bool),
        passes_test (bool: in_admissible_window AND NOT in_forbidden_gap).
    """
    best_peak = min(_PREDICTED_BETAS, key=lambda bp: abs(beta_measured - bp))
    sigma_offset = abs(beta_measured - best_peak) / sigma_measurement
    in_admissible = ADMISSIBLE_LOWER <= beta_measured <= ADMISSIBLE_UPPER
    in_gap = GAP_LOWER <= beta_measured <= GAP_UPPER
    passes = in_admissible and not in_gap
    return {
        "beta_measured": beta_measured,
        "sigma_measurement": sigma_measurement,
        "best_peak": best_peak,
        "sigma_offset": sigma_offset,
        "in_admissible_window": in_admissible,
        "in_forbidden_gap": in_gap,
        "passes_test": passes,
    }


# ---------------------------------------------------------------------------
# Scenario and budget functions
# ---------------------------------------------------------------------------

_SCENARIOS: dict[str, dict] = {
    "canonical_primary": {
        "beta": 0.273,
        "label": "β = 0.273° (canonical, primary)",
        "expected_outcome": "CONFIRMATION",
    },
    "canonical_secondary": {
        "beta": 0.331,
        "label": "β = 0.331° (canonical, secondary)",
        "expected_outcome": "CONFIRMATION",
    },
    "full_formula": {
        "beta": 0.351,
        "label": "β = 0.351° (full formula)",
        "expected_outcome": "CONFIRMATION",
    },
    "forbidden_gap": {
        "beta": 0.300,
        "label": "β = 0.300° (forbidden gap — FALSIFICATION)",
        "expected_outcome": "FALSIFICATION",
    },
    "outside_window": {
        "beta": 0.500,
        "label": "β = 0.500° (outside window — FALSIFICATION)",
        "expected_outcome": "FALSIFICATION",
    },
}


def forecast_scenarios() -> dict:
    """Compute expected outcomes for five observational scenarios.

    Returns
    -------
    dict
        Keys: 'canonical_primary', 'canonical_secondary', 'full_formula',
              'forbidden_gap', 'outside_window'.
        Each value is a dict containing:
            beta, label, expected_outcome,
            significance (result of detection_significance),
            sigmas_per_peak (dict: peak_label → sigma_offset),
            passes_test (bool),
            interpretation (str).
    """
    results: dict = {}
    for key, meta in _SCENARIOS.items():
        beta = meta["beta"]
        sig = detection_significance(beta)
        sigmas_per_peak = {
            "beta_canonical": abs(beta - BETA_CANONICAL) / SIGMA_LITEBIRD,
            "beta_full_1":    abs(beta - BETA_FULL_1)    / SIGMA_LITEBIRD,
            "beta_derived":   abs(beta - BETA_DERIVED)   / SIGMA_LITEBIRD,
            "beta_full_2":    abs(beta - BETA_FULL_2)    / SIGMA_LITEBIRD,
        }
        if sig["passes_test"]:
            interpretation = (
                f"Measurement β = {beta}° is inside the admissible window and "
                f"outside the forbidden gap. Theory PASSES."
            )
        elif sig["in_forbidden_gap"]:
            interpretation = (
                f"Measurement β = {beta}° falls inside the predicted forbidden gap "
                f"[{GAP_LOWER}°, {GAP_UPPER}°]. Theory FALSIFIED."
            )
        else:
            interpretation = (
                f"Measurement β = {beta}° is outside the admissible window "
                f"[{ADMISSIBLE_LOWER}°, {ADMISSIBLE_UPPER}°]. Theory FALSIFIED."
            )
        results[key] = {
            "beta": beta,
            "label": meta["label"],
            "expected_outcome": meta["expected_outcome"],
            "significance": sig,
            "sigmas_per_peak": sigmas_per_peak,
            "passes_test": sig["passes_test"],
            "interpretation": interpretation,
        }
    return results


def uncertainty_budget() -> dict:
    """Enumerate contributions to the total theoretical uncertainty on β.

    Returns
    -------
    dict with keys:
        kinematics (σ_kin),
        cosmic_variance (σ_cv),
        instrumental (σ_inst),
        foreground (σ_fg),
        total (σ_total = sqrt(sum of squares)).
    All values in degrees.
    """
    components = {
        "kinematics":      0.005,   # from (5,7) braid quantisation
        "cosmic_variance": 0.003,   # ℓ-mode sampling
        "instrumental":    0.010,   # LiteBIRD systematic
        "foreground":      0.008,   # dust/synchrotron subtraction
    }
    total = math.sqrt(sum(v ** 2 for v in components.values()))
    return {**components, "total": total}


def detection_power(n_sigma_threshold: float = 2.0) -> dict:
    """Assess LiteBIRD's power to distinguish the two canonical β peaks.

    Parameters
    ----------
    n_sigma_threshold:
        The n-sigma threshold required to call a distinction significant.

    Returns
    -------
    dict with keys:
        peak_separation_deg (|β_canonical − β_derived|),
        sigma_litebird,
        separation_significance (separation / sigma_litebird),
        distinguishable (bool: separation_significance >= n_sigma_threshold).
    """
    separation = abs(BETA_CANONICAL - BETA_DERIVED)
    sep_sig = separation / SIGMA_LITEBIRD
    return {
        "peak_separation_deg": separation,
        "sigma_litebird": SIGMA_LITEBIRD,
        "separation_significance": sep_sig,
        "distinguishable": sep_sig >= n_sigma_threshold,
    }


def timeline_to_result() -> dict:
    """Compute the projected timeline from LiteBIRD launch to published result.

    Uses LAUNCH_YEAR = 2032 and assumes:
        first_light:       LAUNCH_YEAR + 1
        survey_complete:   LAUNCH_YEAR + 3
        result_expected:   LAUNCH_YEAR + 4
        years_from_now:    result_expected − 2026

    Returns
    -------
    dict with all timeline fields.
    """
    present_year = 2026
    first_light = LAUNCH_YEAR + 1
    survey_complete = LAUNCH_YEAR + 3
    result_expected = LAUNCH_YEAR + 4
    return {
        "launch_year": LAUNCH_YEAR,
        "first_light": first_light,
        "survey_complete": survey_complete,
        "result_expected": result_expected,
        "years_from_now": result_expected - present_year,
    }
