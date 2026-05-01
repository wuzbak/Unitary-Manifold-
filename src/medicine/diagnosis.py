# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/medicine/diagnosis.py
==========================
Disease as φ-Homeostatic Fixed-Point Disruption — Pillar 17: Health & Medicine.

Theory
------
In the Unitary Manifold framework every healthy tissue maintains a stable
FTUM fixed point at φ_h — the homeostatic entanglement capacity.  Disease
is the displacement of that fixed point:

    Δφ = φ_tissue − φ_healthy

where φ_tissue is the measured tissue φ and φ_healthy is the population-level
healthy reference.  Diagnosis is therefore pattern-recognition in φ-space:
detecting the deviation |Δφ| above the irreversibility-field noise floor B_μ.

The signal-to-noise ratio for a diagnostic reading is:

    SNR = |Δφ| / (|B_μ| + ε)

A signal buried below the noise floor (SNR < 1) explains late diagnosis:
the deviation is real but undetectable until it grows large enough relative
to the measurement noise.

Bottlenecks addressed
---------------------
Late diagnosis
    The SNR |Δφ| / |B_μ| is too low in early disease because |Δφ| is small
    and B_μ (biological measurement noise) is relatively large.  Population-
    level φ baseline screening lowers the effective noise floor by providing
    a tighter reference, increasing SNR at sub-clinical stages.

Diagnostic deserts
    Rural and underserved areas have low provider density → high φ-uncertainty.
    The diagnostic desert index DDI = area_km² / (n_providers + ε) quantifies
    this gap.  Universal telemedicine routing (information-current routing)
    reduces DDI by decoupling physical distance from measurement capacity.

Fragmented data silos
    Independent φ measurements that are never combined experience information-
    current loss: J_lost = J_full × fraction_siloed.  Federated learning —
    aggregating local φ estimates without sharing raw data — recovers the
    full information current while respecting privacy.

Algorithmic bias
    If training data are drawn from a non-representative population,
    φ_reference is biased away from φ_ref_true.  The bias correction factor
    correction = φ_ref_true / φ_ref_population must be applied before
    computing Δφ.  Monitoring this factor across demographic groups flags
    systematic under- or over-diagnosis.

Actionable suggestions
----------------------
* Population-level φ baseline screening: deploy lightweight wearable B_μ
  monitors to build representative φ_healthy distributions per demographic,
  lowering the detection threshold.
* Information-current routing (federated learning): aggregate φ measurements
  from distributed sources without centralising raw data, recovering the full
  diagnostic information current J_full.
* Universal diagnostic noise floor monitoring: flag any measurement context
  where B_μ > threshold and require confirmatory testing.

Public API
----------
diagnostic_snr(delta_phi, B_noise) -> float
    SNR = |Δφ| / (|B_noise| + ε)

disease_phi_deviation(phi_tissue, phi_healthy) -> float
    Δφ = phi_tissue − phi_healthy

detection_threshold(B_noise, sensitivity_factor) -> float
    Minimum detectable Δφ = sensitivity_factor × B_noise

phi_screening_coverage(n_screened, n_population) -> float
    Fraction screened ∈ [0, 1]

diagnostic_uncertainty(B_noise, n_samples) -> float
    σ_diag = B_noise / sqrt(n_samples)

information_current_loss(J_full, fraction_siloed) -> float
    J_lost = J_full × fraction_siloed

federated_phi_estimate(local_phi_estimates, weights) -> float
    Weighted mean φ across federated nodes

bias_correction_factor(phi_ref_population, phi_ref_true) -> float
    correction = phi_ref_true / phi_ref_population

early_detection_benefit(phi_deviation_early, phi_deviation_late, lam) -> float
    benefit = lam × (phi_deviation_late² − phi_deviation_early²)

diagnostic_desert_index(n_providers, area_km2) -> float
    DDI = area_km² / (n_providers + ε)
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

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_EPSILON: float = 1e-30
_LAM_DEFAULT: float = 1.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def diagnostic_snr(
    delta_phi: float,
    B_noise: float,
) -> float:
    """Signal-to-noise ratio of a diagnostic reading.

    The φ-deviation Δφ must overcome the irreversibility-field noise floor
    B_μ for a diagnosis to be made reliably:

        SNR = |Δφ| / (|B_μ| + ε)

    SNR < 1 means the disease signal is buried in noise — the primary cause
    of late or missed diagnosis.

    Parameters
    ----------
    delta_phi : float — φ deviation Δφ = φ_tissue − φ_healthy
    B_noise   : float — irreversibility-field noise floor B_μ (must be ≥ 0)

    Returns
    -------
    snr : float — signal-to-noise ratio (≥ 0)

    Raises
    ------
    ValueError
        If B_noise < 0.
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(abs(delta_phi) / (abs(B_noise) + _EPSILON))


def disease_phi_deviation(
    phi_tissue: float,
    phi_healthy: float,
) -> float:
    """Signed φ deviation of diseased tissue from the healthy reference.

    Computes:

        Δφ = φ_tissue − φ_healthy

    Negative Δφ indicates a depleted (hypo-active) tissue state;
    positive Δφ indicates a hyperactive or proliferative state.

    Parameters
    ----------
    phi_tissue  : float — measured entanglement capacity of the tissue
    phi_healthy : float — healthy-reference entanglement capacity φ_h

    Returns
    -------
    delta_phi : float — signed deviation (negative ↔ depleted)
    """
    return float(phi_tissue - phi_healthy)


def detection_threshold(
    B_noise: float,
    sensitivity_factor: float,
) -> float:
    """Minimum detectable φ deviation given the noise floor.

    A diagnostic test can reliably detect deviations above:

        Δφ_min = sensitivity_factor × B_noise

    Lowering B_noise (e.g. via better sensors or population screening) or
    increasing sensitivity_factor raises the specificity of the test.

    Parameters
    ----------
    B_noise            : float — irreversibility-field noise floor (must be ≥ 0)
    sensitivity_factor : float — multiplier ≥ 1 (must be > 0)

    Returns
    -------
    threshold : float — minimum detectable |Δφ| (≥ 0)

    Raises
    ------
    ValueError
        If B_noise < 0 or sensitivity_factor ≤ 0.
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    if sensitivity_factor <= 0.0:
        raise ValueError(f"sensitivity_factor must be > 0, got {sensitivity_factor!r}")
    return float(sensitivity_factor * B_noise)


def phi_screening_coverage(
    n_screened: float,
    n_population: float,
) -> float:
    """Population fraction that has received φ baseline screening.

    Coverage = n_screened / n_population, clipped to [0, 1].

    Parameters
    ----------
    n_screened   : float — number of individuals screened (must be ≥ 0)
    n_population : float — total population size (must be > 0)

    Returns
    -------
    coverage : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If n_screened < 0 or n_population ≤ 0.
    """
    if n_screened < 0.0:
        raise ValueError(f"n_screened must be ≥ 0, got {n_screened!r}")
    if n_population <= 0.0:
        raise ValueError(f"n_population must be > 0, got {n_population!r}")
    return float(np.clip(n_screened / n_population, 0.0, 1.0))


def diagnostic_uncertainty(
    B_noise: float,
    n_samples: int,
) -> float:
    """Uncertainty in a φ estimate from n independent diagnostic samples.

    By the central-limit theorem the uncertainty in the mean decreases as:

        σ_diag = B_noise / sqrt(n_samples)

    More samples reduce the effective noise floor — a direct argument for
    population-level screening programmes.

    Parameters
    ----------
    B_noise   : float — per-sample noise level B_μ (must be ≥ 0)
    n_samples : int   — number of independent samples (must be ≥ 1)

    Returns
    -------
    sigma : float — estimated uncertainty (≥ 0)

    Raises
    ------
    ValueError
        If B_noise < 0 or n_samples < 1.
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    if n_samples < 1:
        raise ValueError(f"n_samples must be ≥ 1, got {n_samples!r}")
    return float(B_noise / np.sqrt(n_samples))


def information_current_loss(
    J_full: float,
    fraction_siloed: float,
) -> float:
    """Diagnostic information current lost to data silos.

    When a fraction of measurements are trapped in isolated silos and never
    aggregated, the lost information current is:

        J_lost = J_full × fraction_siloed

    Federated learning or interoperable EHR systems recover J_lost.

    Parameters
    ----------
    J_full          : float — maximum possible information current J_full (must be ≥ 0)
    fraction_siloed : float — fraction of data inaccessible ∈ [0, 1]

    Returns
    -------
    J_lost : float — lost information current (≥ 0)

    Raises
    ------
    ValueError
        If J_full < 0 or fraction_siloed not in [0, 1].
    """
    if J_full < 0.0:
        raise ValueError(f"J_full must be ≥ 0, got {J_full!r}")
    if not (0.0 <= fraction_siloed <= 1.0):
        raise ValueError(
            f"fraction_siloed must be in [0, 1], got {fraction_siloed!r}"
        )
    return float(J_full * fraction_siloed)


def federated_phi_estimate(
    local_phi_estimates: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Weighted mean φ estimate aggregated across federated diagnostic nodes.

    Each node i holds a local estimate φ_i with associated weight w_i
    (e.g. the reciprocal of node-level diagnostic uncertainty).  The
    federated estimate is:

        φ_fed = Σ w_i φ_i / Σ w_i

    With uniform weights this reduces to the arithmetic mean.

    Parameters
    ----------
    local_phi_estimates : ndarray — φ estimates from each federated node
    weights             : ndarray or None — non-negative weights (default: uniform)

    Returns
    -------
    phi_federated : float — weighted mean φ

    Raises
    ------
    ValueError
        If local_phi_estimates is empty or any weight is negative.
    """
    phi_arr = np.asarray(local_phi_estimates, dtype=float)
    if phi_arr.size == 0:
        raise ValueError("local_phi_estimates must not be empty")
    if weights is None:
        w = np.ones_like(phi_arr)
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != phi_arr.shape:
            raise ValueError("weights must have the same shape as local_phi_estimates")
        if np.any(w < 0.0):
            raise ValueError("all weights must be ≥ 0")
    total_weight = w.sum() + _EPSILON
    return float(np.sum(w * phi_arr) / total_weight)


def bias_correction_factor(
    phi_ref_population: float,
    phi_ref_true: float,
) -> float:
    """Correction factor for algorithmic bias in the φ reference.

    If the training population's reference φ_ref_population differs from the
    true population φ_ref_true, all diagnoses carry a systematic error.
    The correction factor to apply before computing Δφ is:

        correction = φ_ref_true / φ_ref_population

    A value > 1 means the reference was under-estimated (under-diagnosis
    risk); < 1 means it was over-estimated (over-diagnosis risk).

    Parameters
    ----------
    phi_ref_population : float — φ reference derived from biased training data (must be > 0)
    phi_ref_true       : float — true population φ reference (must be > 0)

    Returns
    -------
    correction : float — multiplicative correction factor (> 0)

    Raises
    ------
    ValueError
        If either argument is ≤ 0.
    """
    if phi_ref_population <= 0.0:
        raise ValueError(
            f"phi_ref_population must be > 0, got {phi_ref_population!r}"
        )
    if phi_ref_true <= 0.0:
        raise ValueError(f"phi_ref_true must be > 0, got {phi_ref_true!r}")
    return float(phi_ref_true / phi_ref_population)


def early_detection_benefit(
    phi_deviation_early: float,
    phi_deviation_late: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Thermodynamic benefit of early versus late diagnosis.

    The φ-field energy stored in a disease deviation scales as Δφ².
    Detecting disease at |Δφ_early| rather than |Δφ_late| avoids an
    energy expenditure proportional to the difference:

        benefit = λ (Δφ_late² − Δφ_early²)

    Positive benefit means early detection is advantageous; a larger λ
    reflects higher treatment cost or mortality rate associated with
    disease progression.

    Parameters
    ----------
    phi_deviation_early : float — |Δφ| at early detection
    phi_deviation_late  : float — |Δφ| at late detection
    lam                 : float — cost-of-progression coupling λ (default 1)

    Returns
    -------
    benefit : float — energy benefit of early detection (≥ 0 when early < late)
    """
    return float(lam * (phi_deviation_late**2 - phi_deviation_early**2))


def diagnostic_desert_index(
    n_providers: float,
    area_km2: float,
) -> float:
    """Diagnostic desert index: inverse provider density.

    A high DDI indicates that residents must travel long distances for care,
    increasing effective B_μ (uncertainty) in their diagnostic pathway:

        DDI = area_km² / (n_providers + ε)

    Parameters
    ----------
    n_providers : float — number of diagnostic providers in the region (must be ≥ 0)
    area_km2    : float — geographic area of the region in km² (must be > 0)

    Returns
    -------
    DDI : float — km² per provider (higher → more underserved)

    Raises
    ------
    ValueError
        If n_providers < 0 or area_km2 ≤ 0.
    """
    if n_providers < 0.0:
        raise ValueError(f"n_providers must be ≥ 0, got {n_providers!r}")
    if area_km2 <= 0.0:
        raise ValueError(f"area_km2 must be > 0, got {area_km2!r}")
    return float(area_km2 / (n_providers + _EPSILON))
