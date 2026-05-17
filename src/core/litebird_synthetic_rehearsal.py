# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/litebird_synthetic_rehearsal.py
=========================================
Systematic LiteBIRD Synthetic Measurement Rehearsal — v10.31.

This module runs Monte-Carlo rehearsals of LiteBIRD birefringence β
measurements to validate classification pipeline performance before the
real data arrive (~2032).

PHYSICS BACKGROUND
------------------
The UM predicts two discrete β modes:
  β₁ = 0.331°  (5,7) primary sector
  β₂ = 0.273°  (5,6) shadow sector

Falsification conditions:
  A. β < 0.22° at ≥ 3σ  → FALSIFIED (below broad window)
  B. β > 0.38° at ≥ 3σ  → FALSIFIED (above broad window)
  C. β ∈ (0.29°, 0.31°) at ≥ 3σ → FALSIFIED (inter-sector gap)

LiteBIRD is expected to achieve σ_β ≈ 0.020° (1σ), which yields ~2.9σ
inter-sector discrimination (|β₁ − β₂| / σ = 0.058 / 0.020 = 2.9).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

__all__ = [
    # Constants
    "N_SYNTHETIC_RUNS",
    "SIGMA_LITEBIRD",
    "BETA_MODE_1",
    "BETA_MODE_2",
    "BETA_GAP_LOWER",
    "BETA_GAP_UPPER",
    "BETA_BROAD_LOWER",
    "BETA_BROAD_UPPER",
    # Functions
    "generate_synthetic_measurements",
    "rehearsal_run",
    "full_rehearsal_suite",
    "gap_rehearsal_power",
    "sector_discrimination_power",
    "litebird_rehearsal_report",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default number of synthetic measurement draws per rehearsal.
N_SYNTHETIC_RUNS: int = 500

#: Expected LiteBIRD 1σ precision on β [degrees].
SIGMA_LITEBIRD: float = 0.020

#: UM predicted primary (5,7) sector mode [degrees].
BETA_MODE_1: float = 0.331

#: UM predicted shadow (5,6) sector mode [degrees].
BETA_MODE_2: float = 0.273

#: Lower boundary of forbidden inter-sector gap [degrees].
BETA_GAP_LOWER: float = 0.290

#: Upper boundary of forbidden inter-sector gap [degrees].
BETA_GAP_UPPER: float = 0.310

#: Lower boundary of broad falsification window [degrees].
BETA_BROAD_LOWER: float = 0.220

#: Upper boundary of broad falsification window [degrees].
BETA_BROAD_UPPER: float = 0.380

# Derived discrimination σ
_DISCRIMINATION_SIGMA: float = abs(BETA_MODE_1 - BETA_MODE_2) / SIGMA_LITEBIRD  # ≈ 2.9

# Confidence threshold (σ) for zone assignment
_CONF: float = 3.0

# ---------------------------------------------------------------------------
# Internal classification helper (standalone; mirrors litebird_gap_hardening)
# ---------------------------------------------------------------------------


def _classify(beta_obs: float, sigma: float) -> str:
    """Return a verdict string for a single β measurement.

    Classification uses point-estimate region assignment for the broad window
    and inter-sector gap (no σ margin required), and nearest-mode logic for
    discriminating between the two predicted sectors.

    Returns one of:
        "PRIMARY_SECTOR"   β nearest mode 1 and within 2.5σ of it
        "SHADOW_SECTOR"    β nearest mode 2 and within 2.5σ of it
        "GAP_FALSIFIED"    β point estimate falls inside (GAP_LOWER, GAP_UPPER)
        "FALSIFIED"        β point estimate outside broad window
        "AMBIGUOUS"        within window but not within 2.5σ of either mode
    """
    # --- outside broad window? (point-estimate check) ---
    if beta_obs < BETA_BROAD_LOWER:
        return "FALSIFIED"
    if beta_obs > BETA_BROAD_UPPER:
        return "FALSIFIED"

    # --- in inter-sector gap? (point-estimate check) ---
    if BETA_GAP_LOWER < beta_obs < BETA_GAP_UPPER:
        return "GAP_FALSIFIED"

    # --- nearest-mode assignment within 2.5σ ---
    dist_mode1 = abs(beta_obs - BETA_MODE_1) / sigma
    dist_mode2 = abs(beta_obs - BETA_MODE_2) / sigma

    if dist_mode1 <= 2.5 and dist_mode1 <= dist_mode2:
        return "PRIMARY_SECTOR"
    if dist_mode2 <= 2.5 and dist_mode2 < dist_mode1:
        return "SHADOW_SECTOR"

    return "AMBIGUOUS"


def _expected_verdict(true_beta: float) -> str:
    """Return the expected verdict for a perfectly measured true_beta.

    Uses the same logic as _classify but with σ → 0 limit (tiny σ).
    """
    tiny = 1e-9
    return _classify(true_beta, tiny)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_synthetic_measurements(
    n_runs: int,
    true_beta: float,
    sigma: float,
    seed: int = 42,
) -> List[float]:
    """Draw n_runs synthetic β measurements from Normal(true_beta, sigma).

    Parameters
    ----------
    n_runs    : int   Number of synthetic draws.
    true_beta : float True (underlying) β value [degrees].
    sigma     : float Measurement 1σ uncertainty [degrees].
    seed      : int   RNG seed for reproducibility.

    Returns
    -------
    list[float]
        List of n_runs float β measurements.
    """
    rng = np.random.default_rng(seed)
    return rng.normal(loc=true_beta, scale=sigma, size=n_runs).tolist()


def rehearsal_run(
    true_beta: float,
    sigma: float = SIGMA_LITEBIRD,
    n_runs: int = N_SYNTHETIC_RUNS,
    seed: int = 42,
) -> Dict:
    """Run a single rehearsal and return classification statistics.

    Each synthetic measurement is classified independently, then the
    distribution of verdicts is tabulated.

    Parameters
    ----------
    true_beta : float True β [degrees].
    sigma     : float Measurement σ [degrees].
    n_runs    : int   Number of draws.
    seed      : int   RNG seed.

    Returns
    -------
    dict with keys:
        true_beta                 : float
        expected_verdict          : str
        verdict_distribution      : dict[str, int] — verdict → count
        falsified_count           : int
        supported_count           : int
        ambiguous_count           : int
        correct_classification_rate: float (0–1)
        false_positive_rate       : float (fraction falsified when should not be)
    """
    measurements = generate_synthetic_measurements(
        n_runs=n_runs, true_beta=true_beta, sigma=sigma, seed=seed
    )
    expected = _expected_verdict(true_beta)

    verdict_distribution: Dict[str, int] = {}
    for m in measurements:
        v = _classify(m, sigma)
        verdict_distribution[v] = verdict_distribution.get(v, 0) + 1

    falsified_verdicts = {"FALSIFIED", "GAP_FALSIFIED"}
    supported_verdicts = {"PRIMARY_SECTOR", "SHADOW_SECTOR"}

    falsified_count = sum(
        cnt for v, cnt in verdict_distribution.items() if v in falsified_verdicts
    )
    supported_count = sum(
        cnt for v, cnt in verdict_distribution.items() if v in supported_verdicts
    )
    ambiguous_count = verdict_distribution.get("AMBIGUOUS", 0)

    correct_count = verdict_distribution.get(expected, 0)
    correct_classification_rate = correct_count / n_runs

    # False positive rate = fraction classified as FALSIFIED when expected is not FALSIFIED
    if expected in falsified_verdicts:
        false_positive_rate = 0.0  # can't false-positive a true positive
    else:
        false_positive_rate = falsified_count / n_runs

    return {
        "true_beta": true_beta,
        "expected_verdict": expected,
        "verdict_distribution": verdict_distribution,
        "falsified_count": falsified_count,
        "supported_count": supported_count,
        "ambiguous_count": ambiguous_count,
        "correct_classification_rate": correct_classification_rate,
        "false_positive_rate": false_positive_rate,
    }


def full_rehearsal_suite() -> Dict[str, Dict]:
    """Run all six canonical scenarios and return the results.

    Scenarios
    ---------
    mode_1          true β = 0.331° → expect PRIMARY_SECTOR
    mode_2          true β = 0.273° → expect SHADOW_SECTOR
    gap_centre      true β = 0.300° → expect GAP_FALSIFIED
    below_window    true β = 0.180° → expect FALSIFIED
    above_window    true β = 0.420° → expect FALSIFIED
    ambiguous       true β = 0.250° → expect AMBIGUOUS

    Returns
    -------
    dict[str, dict]
        Scenario name → rehearsal_run output dict.
    """
    scenarios = {
        "mode_1": BETA_MODE_1,
        "mode_2": BETA_MODE_2,
        "gap_centre": (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0,
        "below_window": 0.180,
        "above_window": 0.420,
        "ambiguous": 0.250,
    }
    return {
        name: rehearsal_run(true_beta=beta, sigma=SIGMA_LITEBIRD)
        for name, beta in scenarios.items()
    }


def gap_rehearsal_power(
    sigma: float = SIGMA_LITEBIRD,
    n_runs: int = N_SYNTHETIC_RUNS,
    seed: int = 42,
    n_trials: int = 1000,
) -> Dict:
    """Compute the statistical power to detect the inter-sector gap at LiteBIRD precision.

    Power is defined as: given that the true β is at the gap centre (0.300°),
    what fraction of LiteBIRD "experiments" (each consisting of n_runs
    independent measurements) correctly place the combined β estimate inside
    the gap?

    The combined estimate after n_runs measurements has precision
    σ_combined = σ / sqrt(n_runs), giving approximately 11σ clearance from
    each gap edge when true β = 0.300° and σ = 0.020°, n_runs = 500.

    Parameters
    ----------
    sigma   : float  Per-measurement 1σ precision [degrees].
    n_runs  : int    Measurements per LiteBIRD experiment.
    seed    : int    RNG seed.
    n_trials: int    Number of independent experiments to simulate.

    Returns
    -------
    dict with keys:
        gap_centre        : float — gap centre value
        sigma             : float — per-measurement sigma
        n_runs            : int   — measurements per experiment
        gap_detection_rate: float — fraction of experiments where mean β ∈ gap
        gap_sigma_margin  : float — gap half-width / sigma (single measurement)
        power_exceeds_0p99: bool
    """
    gap_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
    gap_half_width = (BETA_GAP_UPPER - BETA_GAP_LOWER) / 2.0
    gap_sigma_margin = gap_half_width / sigma  # = 0.5 for LiteBIRD

    rng = np.random.default_rng(seed)
    # Each row = one LiteBIRD experiment of n_runs measurements
    draws = rng.normal(loc=gap_centre, scale=sigma, size=(n_trials, n_runs))
    means = draws.mean(axis=1)  # combined estimates, shape (n_trials,)
    in_gap = ((means > BETA_GAP_LOWER) & (means < BETA_GAP_UPPER)).sum()
    gap_detection_rate = float(in_gap) / n_trials

    return {
        "gap_centre": gap_centre,
        "sigma": sigma,
        "n_runs": n_runs,
        "gap_detection_rate": gap_detection_rate,
        "gap_sigma_margin": gap_sigma_margin,
        "power_exceeds_0p99": gap_detection_rate > 0.99,
    }


def sector_discrimination_power(
    sigma: float = SIGMA_LITEBIRD,
    n_runs: int = N_SYNTHETIC_RUNS,
    seed: int = 42,
) -> Dict:
    """Statistical power to discriminate mode 1 (0.331°) from mode 2 (0.273°).

    The metric: given true β = mode 1, what fraction of draws are classified
    PRIMARY_SECTOR (not SHADOW_SECTOR or AMBIGUOUS)?  And vice versa.

    Parameters
    ----------
    sigma  : float Measurement σ.
    n_runs : int   Number of draws per mode.
    seed   : int   RNG seed.

    Returns
    -------
    dict with keys:
        discrimination_sigma     : float  — |β₁ − β₂| / σ
        mode_1_correct_rate      : float  — fraction correctly classified PRIMARY
        mode_2_correct_rate      : float  — fraction correctly classified SHADOW
        mode_1_misclassified_rate: float  — fraction classified SHADOW (confusion)
        mode_2_misclassified_rate: float  — fraction classified PRIMARY (confusion)
        both_above_0p90          : bool
    """
    run1 = rehearsal_run(
        true_beta=BETA_MODE_1, sigma=sigma, n_runs=n_runs, seed=seed
    )
    run2 = rehearsal_run(
        true_beta=BETA_MODE_2, sigma=sigma, n_runs=n_runs, seed=seed + 1
    )

    mode1_correct = run1["verdict_distribution"].get("PRIMARY_SECTOR", 0) / n_runs
    mode2_correct = run2["verdict_distribution"].get("SHADOW_SECTOR", 0) / n_runs

    mode1_as_shadow = run1["verdict_distribution"].get("SHADOW_SECTOR", 0) / n_runs
    mode2_as_primary = run2["verdict_distribution"].get("PRIMARY_SECTOR", 0) / n_runs

    return {
        "discrimination_sigma": _DISCRIMINATION_SIGMA,
        "mode_1_correct_rate": mode1_correct,
        "mode_2_correct_rate": mode2_correct,
        "mode_1_misclassified_rate": mode1_as_shadow,
        "mode_2_misclassified_rate": mode2_as_primary,
        "both_above_0p90": mode1_correct > 0.90 and mode2_correct > 0.90,
    }


def litebird_rehearsal_report() -> Dict:
    """Produce the full LiteBIRD synthetic rehearsal report.

    Includes:
    - All six scenario results.
    - Gap detection power analysis.
    - Sector discrimination power analysis.
    - Key summary metrics.

    Returns
    -------
    dict
        Full structured report.
    """
    suite = full_rehearsal_suite()
    gap_power = gap_rehearsal_power()
    discrimination = sector_discrimination_power()

    scenario_summaries = {
        name: {
            "true_beta": r["true_beta"],
            "expected_verdict": r["expected_verdict"],
            "correct_classification_rate": r["correct_classification_rate"],
            "false_positive_rate": r["false_positive_rate"],
            "verdict_distribution": r["verdict_distribution"],
        }
        for name, r in suite.items()
    }

    return {
        "version": "v10.31",
        "title": "LiteBIRD Synthetic Measurement Rehearsal Report",
        "n_synthetic_runs": N_SYNTHETIC_RUNS,
        "sigma_litebird": SIGMA_LITEBIRD,
        "prediction_summary": {
            "mode_1": f"β = {BETA_MODE_1}° (5,7 primary sector)",
            "mode_2": f"β = {BETA_MODE_2}° (5,6 shadow sector)",
            "gap": f"β ∈ ({BETA_GAP_LOWER}°, {BETA_GAP_UPPER}°) — FALSIFIED",
            "broad_window": f"[{BETA_BROAD_LOWER}°, {BETA_BROAD_UPPER}°]",
        },
        "scenarios": scenario_summaries,
        "gap_power": gap_power,
        "sector_discrimination": discrimination,
        "key_findings": {
            "gap_detection_power": gap_power["gap_detection_rate"],
            "gap_power_exceeds_0p99": gap_power["power_exceeds_0p99"],
            "mode_discrimination_sigma": discrimination["discrimination_sigma"],
            "sector_discrimination_both_above_0p90": discrimination["both_above_0p90"],
        },
    }
