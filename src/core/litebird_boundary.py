# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/litebird_boundary.py
==============================
Pillar 45-C — LiteBIRD Boundary Check: Covariance Matrix and Exact Fail Zone
for the β ≈ 0.351° Birefringence Prediction.

Physical motivation
--------------------
The Unitary Manifold predicts two canonical birefringence angles:

    β_canonical  = 0.273°   (primary SOS resonance: arctan(5/7)×(2/k_cs))
    β_derived    = 0.331°   (secondary: from braided causal-order mixing)

And two derived / full-formula values:

    β_full_1     ≈ 0.290°   (with Kibble-Zurek correction)
    β_full_2     ≈ 0.351°   (with full (5,7) + CS-mixing correction)

The LiteBIRD satellite (launch ~2032) will measure β to σ_LB ≈ 0.02°.

This module answers: **if the measurement comes back 0.34° or 0.36°, does the
theory still pass?**  It generates a high-resolution Gaussian likelihood for
the β ≈ 0.351° prediction, computes a covariance matrix over the full
admissible window [0.22°, 0.38°], and defines exact pass/fail zones.

The Fail Zone
--------------
The theory fails if:

1. The measured β is **outside the admissible window** [0.22°, 0.38°], OR
2. The measured β falls **inside the predicted gap** [0.29°, 0.31°]
   (the gap between β_canonical and β_derived).

Pass condition:
    β_measured ∈ [0.22°, 0.29°) ∪ (0.31°, 0.38°]
    AND the measured value is within the σ_LB prediction interval of one of
    the four canonical peaks.

Covariance matrix
------------------
The prediction is a bimodal (or four-mode) Gaussian mixture.  The covariance
matrix C is the 4×4 matrix:

    C_ij = cov(β_i, β_j)

where (β_1, β_2, β_3, β_4) = (0.273°, 0.290°, 0.331°, 0.351°).  The
diagonal entries are σ_theory² (theoretical uncertainty) and the off-diagonal
entries encode the (5,7)→CS mixing correlation.

Admissible window
------------------
The admissible window [0.22°, 0.38°] is set by:
  * Lower bound: 0.22° = minimum β consistent with n_w = 5 at 3σ
  * Upper bound: 0.38° = maximum β consistent with k_cs = 74 at 3σ

The predicted gap [0.29°, 0.31°] is the forbidden zone between the two
families of predictions.

Public API
----------
BETA_CANONICAL, BETA_DERIVED, BETA_FULL_1, BETA_FULL_2 : float
    The four predicted birefringence angles (degrees).

ADMISSIBLE_LOWER, ADMISSIBLE_UPPER : float
    The admissible window bounds (degrees).

GAP_LOWER, GAP_UPPER : float
    The predicted forbidden gap (degrees).

SIGMA_LITEBIRD : float
    Expected LiteBIRD 1σ measurement uncertainty (degrees).

SIGMA_THEORY : float
    Theoretical 1σ uncertainty on each peak (degrees).

BirefringencePrediction
    Dataclass: beta, sigma_theory, label.

litebird_covariance_matrix() → ndarray, shape (4,4)
    4×4 covariance matrix for the four predicted β values.

is_in_admissible_window(beta) → bool
    True iff β ∈ [0.22°, 0.38°].

is_in_gap(beta) → bool
    True iff β ∈ (0.29°, 0.31°) (the forbidden zone).

theory_passes(beta_measured, sigma_measured) → bool
    True iff the measurement is consistent with any of the four predictions
    within 3σ AND not in the gap AND inside the admissible window.

gaussian_likelihood(beta_measured, sigma_measured) → ndarray, shape (4,)
    Per-peak Gaussian likelihoods L_i = exp(-(β_meas - β_i)²/(2σ_tot²)).

best_fit_peak(beta_measured, sigma_measured) → BirefringencePrediction
    Return the prediction peak closest to the measurement.

fail_zone_report(beta_measured, sigma_measured) → dict
    Full "Yes/No" judge report for a LiteBIRD measurement.

litebird_scan(beta_values, sigma_measured) → list[dict]
    Scan over a range of β values and report pass/fail for each.

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
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Primary canonical birefringence angle (degrees) — arctan(5/7) × (2/k_cs) route
BETA_CANONICAL: float = 0.273

#: Secondary derived angle (degrees) — braided causal-order mixing
BETA_DERIVED: float = 0.331

#: Full-formula angle 1 (degrees) — with Kibble-Zurek correction
BETA_FULL_1: float = 0.290

#: Full-formula angle 2 (degrees) — with full (5,7) + CS-mixing
BETA_FULL_2: float = 0.351

#: All four predicted peaks (ordered)
BETA_PREDICTIONS: List[float] = [BETA_CANONICAL, BETA_FULL_1, BETA_DERIVED, BETA_FULL_2]

#: Labels for the four peaks
BETA_LABELS: List[str] = [
    "canonical (arctan route)",
    "full-formula+KZ",
    "derived (CS-mixing)",
    "full-formula+CS",
]

#: Admissible window lower bound (degrees)
ADMISSIBLE_LOWER: float = 0.22

#: Admissible window upper bound (degrees)
ADMISSIBLE_UPPER: float = 0.38

#: Predicted forbidden gap lower bound (degrees)
GAP_LOWER: float = 0.29

#: Predicted forbidden gap upper bound (degrees)
GAP_UPPER: float = 0.31

#: LiteBIRD expected 1σ measurement uncertainty (degrees)
SIGMA_LITEBIRD: float = 0.02

#: Theoretical 1σ uncertainty on each prediction peak (degrees)
SIGMA_THEORY: float = 0.005

#: Number of σ_total for a "pass" decision
N_SIGMA_PASS: float = 3.0

#: Correlation coefficient between peaks in the same family (canonical/derived)
_RHO_SAME_FAMILY: float = 0.85

#: Correlation coefficient between peaks in different families
_RHO_CROSS_FAMILY: float = 0.30


# ---------------------------------------------------------------------------
# BirefringencePrediction dataclass
# ---------------------------------------------------------------------------

@dataclass
class BirefringencePrediction:
    """A single birefringence prediction peak.

    Attributes
    ----------
    beta         : float — predicted angle (degrees)
    sigma_theory : float — theoretical 1σ uncertainty (degrees)
    label        : str   — human-readable label
    """
    beta: float
    sigma_theory: float
    label: str


#: The four canonical prediction objects
PREDICTIONS: List[BirefringencePrediction] = [
    BirefringencePrediction(beta=b, sigma_theory=SIGMA_THEORY, label=l)
    for b, l in zip(BETA_PREDICTIONS, BETA_LABELS)
]


# ---------------------------------------------------------------------------
# Covariance matrix
# ---------------------------------------------------------------------------

def litebird_covariance_matrix(sigma_theory: float = SIGMA_THEORY) -> np.ndarray:
    """4×4 covariance matrix for the four β prediction peaks.

    C_ii = σ_theory²  (diagonal: per-peak theoretical variance)
    C_ij = ρ_ij × σ_theory²  (off-diagonal: inter-peak correlation)

    The correlation structure reflects the geometric origin of the predictions:
      * Peaks 1 & 2 (0.273°, 0.290°) share the same winding sector → ρ = 0.85
      * Peaks 3 & 4 (0.331°, 0.351°) share the CS-mixing sector → ρ = 0.85
      * Cross-family correlations → ρ = 0.30

    Parameters
    ----------
    sigma_theory : float — theoretical 1σ per peak (default: SIGMA_THEORY)

    Returns
    -------
    ndarray, shape (4, 4)
        Positive semi-definite covariance matrix.
    """
    n = 4
    var = sigma_theory ** 2
    # Base correlation matrix
    rho = np.array([
        [1.0,             _RHO_SAME_FAMILY, _RHO_CROSS_FAMILY, _RHO_CROSS_FAMILY],
        [_RHO_SAME_FAMILY, 1.0,             _RHO_CROSS_FAMILY, _RHO_CROSS_FAMILY],
        [_RHO_CROSS_FAMILY, _RHO_CROSS_FAMILY, 1.0,            _RHO_SAME_FAMILY],
        [_RHO_CROSS_FAMILY, _RHO_CROSS_FAMILY, _RHO_SAME_FAMILY, 1.0],
    ])
    return var * rho


# ---------------------------------------------------------------------------
# Pass/Fail predicates
# ---------------------------------------------------------------------------

def is_in_admissible_window(beta: float) -> bool:
    """True iff β is within the admissible window [0.22°, 0.38°]."""
    return ADMISSIBLE_LOWER <= beta <= ADMISSIBLE_UPPER


def is_in_gap(beta: float) -> bool:
    """True iff β falls inside the predicted forbidden gap (0.29°, 0.31°).

    The gap is an open interval: the endpoints are theoretically allowed.
    """
    return GAP_LOWER < beta < GAP_UPPER


def gaussian_likelihood(
    beta_measured: float,
    sigma_measured: float = SIGMA_LITEBIRD,
    sigma_theory: float = SIGMA_THEORY,
) -> np.ndarray:
    """Per-peak Gaussian likelihood for a measurement.

    L_i = exp(-(β_meas - β_i)² / (2 σ_total²))

    where σ_total = √(σ_measured² + σ_theory²).

    Parameters
    ----------
    beta_measured : float — measured β value (degrees)
    sigma_measured: float — measurement 1σ (default: SIGMA_LITEBIRD = 0.02°)
    sigma_theory  : float — theoretical 1σ per peak (default: SIGMA_THEORY)

    Returns
    -------
    ndarray, shape (4,) — per-peak likelihoods ∈ (0, 1]
    """
    sigma_total = math.sqrt(sigma_measured ** 2 + sigma_theory ** 2)
    likelihoods = np.array([
        math.exp(-0.5 * ((beta_measured - b) / sigma_total) ** 2)
        for b in BETA_PREDICTIONS
    ])
    return likelihoods


def best_fit_peak(
    beta_measured: float,
    sigma_measured: float = SIGMA_LITEBIRD,
) -> BirefringencePrediction:
    """Return the prediction peak with the highest likelihood for the measurement.

    Parameters
    ----------
    beta_measured  : float — measured β value (degrees)
    sigma_measured : float — measurement 1σ

    Returns
    -------
    BirefringencePrediction — the best-fit peak
    """
    likelihoods = gaussian_likelihood(beta_measured, sigma_measured)
    best_idx = int(np.argmax(likelihoods))
    return PREDICTIONS[best_idx]


def theory_passes(
    beta_measured: float,
    sigma_measured: float = SIGMA_LITEBIRD,
    n_sigma: float = N_SIGMA_PASS,
    sigma_theory: float = SIGMA_THEORY,
) -> bool:
    """True iff the measurement is consistent with the theory.

    Pass condition (ALL must hold):
    1. β_measured ∈ [0.22°, 0.38°]  (admissible window)
    2. β_measured ∉ (0.29°, 0.31°)  (not in the forbidden gap)
    3. At least one prediction peak β_i satisfies:
       |β_measured − β_i| ≤ n_sigma × σ_total
       where σ_total = √(σ_measured² + σ_theory²)

    Parameters
    ----------
    beta_measured  : float — measured β value (degrees)
    sigma_measured : float — measurement 1σ (default: SIGMA_LITEBIRD = 0.02°)
    n_sigma        : float — number of σ for the pass window (default: 3.0)
    sigma_theory   : float — theoretical 1σ per peak

    Returns
    -------
    bool
    """
    if not is_in_admissible_window(beta_measured):
        return False
    if is_in_gap(beta_measured):
        return False
    sigma_total = math.sqrt(sigma_measured ** 2 + sigma_theory ** 2)
    for b in BETA_PREDICTIONS:
        if abs(beta_measured - b) <= n_sigma * sigma_total:
            return True
    return False


def fail_zone_report(
    beta_measured: float,
    sigma_measured: float = SIGMA_LITEBIRD,
    n_sigma: float = N_SIGMA_PASS,
) -> Dict:
    """Full "Yes/No" judge report for a LiteBIRD measurement.

    Parameters
    ----------
    beta_measured  : float — measured β value (degrees)
    sigma_measured : float — measurement 1σ (default: SIGMA_LITEBIRD = 0.02°)
    n_sigma        : float — pass threshold in σ (default: 3.0)

    Returns
    -------
    dict with keys:
        ``beta_measured``       : float — the input measurement
        ``sigma_measured``      : float
        ``in_admissible_window``: bool
        ``in_gap``              : bool — True iff in the forbidden zone
        ``theory_passes``       : bool — overall pass/fail
        ``verdict``             : str  — "PASS" or "FAIL" with reason
        ``likelihoods``         : ndarray — per-peak Gaussian likelihoods
        ``best_fit_peak``       : BirefringencePrediction
        ``closest_beta``        : float — nearest prediction peak
        ``closest_delta``       : float — |β_meas − nearest peak| in degrees
        ``closest_delta_sigma`` : float — same in units of σ_total
        ``covariance_matrix``   : ndarray — 4×4 covariance matrix
        ``admissible_window``   : tuple (lower, upper) in degrees
        ``gap``                 : tuple (lower, upper) in degrees
    """
    in_window = is_in_admissible_window(beta_measured)
    in_gap = is_in_gap(beta_measured)
    passes = theory_passes(beta_measured, sigma_measured, n_sigma)
    likelihoods = gaussian_likelihood(beta_measured, sigma_measured)
    best = best_fit_peak(beta_measured, sigma_measured)
    sigma_total = math.sqrt(sigma_measured ** 2 + SIGMA_THEORY ** 2)

    # Find closest peak
    distances = [(abs(beta_measured - b), b) for b in BETA_PREDICTIONS]
    distances.sort()
    closest_delta, closest_beta = distances[0]
    closest_sigma = closest_delta / sigma_total

    # Build verdict string
    if not in_window:
        reason = (
            f"β={beta_measured:.4f}° is outside the admissible window "
            f"[{ADMISSIBLE_LOWER}°, {ADMISSIBLE_UPPER}°]. "
            "Theory falsified."
        )
        verdict = f"FAIL — {reason}"
    elif in_gap:
        reason = (
            f"β={beta_measured:.4f}° falls in the predicted forbidden gap "
            f"({GAP_LOWER}°, {GAP_UPPER}°). "
            "Theory falsified (no viable configuration exists in this range)."
        )
        verdict = f"FAIL — {reason}"
    elif not passes:
        reason = (
            f"β={beta_measured:.4f}° is in the admissible window but more than "
            f"{n_sigma}σ from all four predictions. Theory is inconsistent."
        )
        verdict = f"FAIL — {reason}"
    else:
        reason = (
            f"β={beta_measured:.4f}° is consistent with peak '{best.label}' "
            f"(β={best.beta}°) at {closest_sigma:.2f}σ. Theory survives."
        )
        verdict = f"PASS — {reason}"

    return {
        "beta_measured": beta_measured,
        "sigma_measured": sigma_measured,
        "in_admissible_window": in_window,
        "in_gap": in_gap,
        "theory_passes": passes,
        "verdict": verdict,
        "likelihoods": likelihoods,
        "best_fit_peak": best,
        "closest_beta": closest_beta,
        "closest_delta": closest_delta,
        "closest_delta_sigma": closest_sigma,
        "covariance_matrix": litebird_covariance_matrix(),
        "admissible_window": (ADMISSIBLE_LOWER, ADMISSIBLE_UPPER),
        "gap": (GAP_LOWER, GAP_UPPER),
    }


def litebird_scan(
    beta_values: List[float],
    sigma_measured: float = SIGMA_LITEBIRD,
    n_sigma: float = N_SIGMA_PASS,
) -> List[Dict]:
    """Scan over a range of β values and produce pass/fail reports for each.

    Parameters
    ----------
    beta_values    : list[float] — β values to probe (degrees)
    sigma_measured : float       — assumed LiteBIRD 1σ
    n_sigma        : float       — pass threshold

    Returns
    -------
    list of fail_zone_report dicts, one per β value
    """
    return [fail_zone_report(b, sigma_measured, n_sigma) for b in beta_values]
