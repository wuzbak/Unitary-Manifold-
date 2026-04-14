# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/medicine/treatment.py
==========================
Treatment as φ-Field Restoration — Pillar 17: Health & Medicine.

Theory
------
In the Unitary Manifold framework, treatment is the act of restoring the
φ field of diseased tissue to its healthy FTUM fixed point φ_healthy.
Three intervention modalities map onto distinct field operations:

Pharmaceutical intervention
    A drug is a targeted B_μ perturbation that shifts the φ-basin of
    attraction.  The perturbation magnitude is dose-dependent and follows
    the Hill equation (pharmacological EC₅₀):

        φ_response(dose) = φ_max × dose / (EC₅₀ + dose)

    At dose → ∞ the response saturates to φ_max — the maximal achievable
    φ restoration; at dose = EC₅₀ the response is exactly φ_max / 2.

Surgery
    Surgical resection removes a topological defect in the φ field — a
    localised region where φ has become permanently decoupled from the
    healthy fixed point (tumour, obstructed vessel, ruptured organ).

Chronic disease
    A shallow φ fixed point requires continuous energy input (daily
    medication) to maintain.  The fixed point exists but has a small basin
    radius; without continuous B_μ support the system drifts back toward
    the disease state.

Treatment efficacy
    The fraction of the disease deviation corrected by an intervention:

        efficacy = (φ_pre − φ_post) / (φ_pre − φ_target),   clipped [0, 1]

    efficacy = 1 means complete restoration; efficacy = 0 means no change.

Bottlenecks addressed
---------------------
Drug resistance
    Pathogens or cancer cells adapt their own B_μ field to counteract a
    single-mode intervention.  The probability of resistance after n_cycles
    treatment cycles is modelled as:

        P_resist = 1 − (1 − p_base)^{n_cycles} × exp(−B_strength)

    where B_strength quantifies the immune-system or pharmacological
    counter-pressure.  Combination therapy (multiple B_μ modes) dramatically
    lowers P_resist.

Dosing optimisation
    Under-dosing leaves the φ-basin shift insufficient; over-dosing overshoots
    φ_target and may enter an iatrogenic disease state.  The dosing error is:

        dosing_error = |φ_achieved − φ_target| / φ_target

    Personalised φ-target dosing (precision medicine) minimises this error.

Treatment deserts
    Geographic and financial access barriers reduce the effective λ coupling
    between patient and treatment.  The access barrier factor models this
    attenuation as a function of distance and income.

Clinical-trial bottleneck
    Exploring the φ-landscape to find efficacious interventions is slow when
    trials test one arm at a time.  FTUM basin sampling (multi-arm adaptive
    trials) maximises φ-landscape exploration efficiency.

Polypharmacy confusion
    When multiple drugs impose simultaneous B_μ perturbations with random
    phases, the total field magnitude grows only as sqrt(Σ B_i²) rather than
    Σ B_i — destructive interference reduces net efficacy and increases
    side-effect risk.

Actionable suggestions
----------------------
* Multi-mode B_μ combination therapy: combine drugs with orthogonal
  mechanisms to prevent single-mode adaptation (resistance).
* Personalised φ-target dosing: measure individual φ before prescribing
  to set the precise dose that achieves φ_target ± tolerance.
* Accelerated trial design via FTUM basin sampling: use adaptive multi-arm
  trial designs that allocate participants to the highest-efficacy arm based
  on accumulating φ-response data.

Public API
----------
treatment_efficacy(phi_post, phi_target, phi_pre) -> float
    efficacy = (phi_pre − phi_post) / (phi_pre − phi_target)  clipped [0, 1]

drug_dose_response(dose, phi_max, EC50) -> float
    Hill-equation φ-response: phi_max × dose / (EC50 + dose)

resistance_probability(B_strength, n_cycles, base_prob) -> float
    P_resist = 1 − (1 − base_prob)^{n_cycles} × exp(−B_strength)

combination_therapy_synergy(efficacy_a, efficacy_b, rho) -> float
    synergy = efficacy_a + efficacy_b − rho × efficacy_a × efficacy_b

polypharmacy_interference(B_fields) -> float
    Total B_μ magnitude under random-phase interference = sqrt(Σ B_i²)

dosing_error(phi_achieved, phi_target) -> float
    |phi_achieved − phi_target| / phi_target

access_barrier_factor(distance_km, income_ratio) -> float
    barrier = 1 − exp(−distance_km × (1 − income_ratio))  clipped [0, 1)

precision_medicine_gain(phi_population_std, phi_individual_std) -> float
    gain = 1 − phi_individual_std / phi_population_std  clipped [0, 1)

clinical_trial_efficiency(n_arms, phi_basin_width, sigma) -> float
    eta = n_arms × phi_basin_width / (sigma + 1e-30)

cure_criterion(phi_post, phi_healthy, tolerance) -> bool
    True iff |phi_post − phi_healthy| < tolerance
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def treatment_efficacy(
    phi_post: float,
    phi_target: float,
    phi_pre: float,
) -> float:
    """Fraction of disease deviation corrected by treatment.

    Efficacy measures how well the treatment has moved the tissue φ from
    the pre-treatment disease state toward the therapeutic target:

        efficacy = (φ_pre − φ_post) / (φ_pre − φ_target),   clipped [0, 1]

    efficacy = 1 → complete restoration to φ_target.
    efficacy = 0 → no movement; treatment had no effect.

    Parameters
    ----------
    phi_post   : float — post-treatment tissue φ
    phi_target : float — desired healthy-fixed-point φ
    phi_pre    : float — pre-treatment tissue φ

    Returns
    -------
    efficacy : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If phi_pre == phi_target (no disease deviation to correct).
    """
    if phi_pre == phi_target:
        raise ValueError(
            "phi_pre must differ from phi_target (no disease deviation)"
        )
    raw = (phi_pre - phi_post) / (phi_pre - phi_target)
    return float(np.clip(raw, 0.0, 1.0))


def drug_dose_response(
    dose: float,
    phi_max: float,
    EC50: float,
) -> float:
    """Hill-equation φ-response to a pharmaceutical dose.

    The standard Hill/Michaelis-Menten saturation curve models the
    φ-basin shift produced by a drug:

        φ_response = φ_max × dose / (EC₅₀ + dose)

    At dose = EC₅₀ the response is exactly φ_max / 2; as dose → ∞ the
    response saturates to φ_max.

    Parameters
    ----------
    dose    : float — administered dose (must be ≥ 0)
    phi_max : float — maximum achievable φ restoration (must be > 0)
    EC50    : float — half-maximal effective dose (must be > 0)

    Returns
    -------
    phi_response : float ∈ [0, phi_max]

    Raises
    ------
    ValueError
        If dose < 0, phi_max ≤ 0, or EC50 ≤ 0.
    """
    if dose < 0.0:
        raise ValueError(f"dose must be ≥ 0, got {dose!r}")
    if phi_max <= 0.0:
        raise ValueError(f"phi_max must be > 0, got {phi_max!r}")
    if EC50 <= 0.0:
        raise ValueError(f"EC50 must be > 0, got {EC50!r}")
    return float(phi_max * dose / (EC50 + dose))


def resistance_probability(
    B_strength: float,
    n_cycles: int,
    base_prob: float = 1e-6,
) -> float:
    """Probability that a pathogen or tumour develops treatment resistance.

    After n_cycles treatment cycles the probability of resistance given a
    single-mode B_μ intervention of strength B_strength is:

        P_resist = 1 − (1 − p_base)^{n_cycles} × exp(−B_strength)

    A stronger B_μ field (e.g. higher drug concentration or robust immune
    response) suppresses the exp factor, reducing P_resist.

    Parameters
    ----------
    B_strength : float — B_μ field strength of the intervention (must be ≥ 0)
    n_cycles   : int   — number of treatment cycles (must be ≥ 0)
    base_prob  : float — per-cycle base resistance probability ∈ (0, 1) (default 1e-6)

    Returns
    -------
    P_resist : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If B_strength < 0, n_cycles < 0, or base_prob not in (0, 1).
    """
    if B_strength < 0.0:
        raise ValueError(f"B_strength must be ≥ 0, got {B_strength!r}")
    if n_cycles < 0:
        raise ValueError(f"n_cycles must be ≥ 0, got {n_cycles!r}")
    if not (0.0 < base_prob < 1.0):
        raise ValueError(f"base_prob must be in (0, 1), got {base_prob!r}")
    # P = (1 − (1−p)^n) × exp(−B): more cycles → higher risk;
    # stronger B_μ treatment field → lower resistance probability.
    acquisition = 1.0 - (1.0 - base_prob) ** n_cycles
    return float(np.clip(acquisition * np.exp(-B_strength), 0.0, 1.0))


def combination_therapy_synergy(
    efficacy_a: float,
    efficacy_b: float,
    rho: float = 1.0,
) -> float:
    """Combined efficacy of two drugs with a synergy/antagonism parameter.

    Using the Bliss-independence / Unitary Manifold B_μ superposition model:

        synergy = efficacy_a + efficacy_b − ρ × efficacy_a × efficacy_b

    ρ = 1  → Bliss independence (no interaction).
    ρ < 1  → synergy (combined effect exceeds independence).
    ρ > 1  → antagonism (combined effect is less than independence).

    Parameters
    ----------
    efficacy_a : float — efficacy of drug A ∈ [0, 1]
    efficacy_b : float — efficacy of drug B ∈ [0, 1]
    rho        : float — interaction parameter ρ (default 1.0)

    Returns
    -------
    combined_efficacy : float (clipped to [0, 1])

    Raises
    ------
    ValueError
        If efficacy_a or efficacy_b is outside [0, 1].
    """
    if not (0.0 <= efficacy_a <= 1.0):
        raise ValueError(f"efficacy_a must be in [0, 1], got {efficacy_a!r}")
    if not (0.0 <= efficacy_b <= 1.0):
        raise ValueError(f"efficacy_b must be in [0, 1], got {efficacy_b!r}")
    raw = efficacy_a + efficacy_b - rho * efficacy_a * efficacy_b
    return float(np.clip(raw, 0.0, 1.0))


def polypharmacy_interference(
    B_fields: np.ndarray,
) -> float:
    """Total B_μ field magnitude under random-phase polypharmacy interference.

    When n drugs each impose a B_μ perturbation with random relative phases,
    the total field magnitude is the quadrature sum (analogous to incoherent
    addition of waves):

        |B_total| = sqrt(Σ B_i²)

    This is less than the coherent sum Σ B_i, quantifying the reduction in
    net therapeutic efficacy (and increase in side-effect unpredictability)
    in polypharmacy regimens.

    Parameters
    ----------
    B_fields : ndarray — individual drug B_μ field magnitudes (must be ≥ 0)

    Returns
    -------
    B_total : float — total field magnitude (≥ 0)

    Raises
    ------
    ValueError
        If any B_field value is negative.
    """
    B_arr = np.asarray(B_fields, dtype=float)
    if np.any(B_arr < 0.0):
        raise ValueError("all B_field values must be ≥ 0")
    return float(np.sqrt(np.sum(B_arr**2)))


def dosing_error(
    phi_achieved: float,
    phi_target: float,
) -> float:
    """Fractional dosing error relative to the φ target.

    Measures the normalised distance between the achieved and target φ:

        dosing_error = |φ_achieved − φ_target| / φ_target

    Values > 0.1 (10 % miss) are typically clinically significant.

    Parameters
    ----------
    phi_achieved : float — tissue φ achieved by the chosen dose
    phi_target   : float — intended therapeutic target φ (must be > 0)

    Returns
    -------
    error : float ≥ 0

    Raises
    ------
    ValueError
        If phi_target ≤ 0.
    """
    if phi_target <= 0.0:
        raise ValueError(f"phi_target must be > 0, got {phi_target!r}")
    return float(abs(phi_achieved - phi_target) / phi_target)


def access_barrier_factor(
    distance_km: float,
    income_ratio: float,
) -> float:
    """Effective treatment access barrier as a function of geography and income.

    Low income or long travel distance attenuates the λ coupling between
    patient and treatment system.  The barrier is modelled as:

        barrier = 1 − exp(−distance_km × (1 − income_ratio)),   clipped [0, 1)

    barrier → 0 means full access; barrier → 1 means complete exclusion.
    income_ratio = 1 (median income) and distance = 0 → barrier = 0.

    Parameters
    ----------
    distance_km  : float — travel distance to treatment facility (must be ≥ 0)
    income_ratio : float — patient income / median income, capped at [0, 1]

    Returns
    -------
    barrier : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If distance_km < 0.
    """
    if distance_km < 0.0:
        raise ValueError(f"distance_km must be ≥ 0, got {distance_km!r}")
    income_ratio_clipped = float(np.clip(income_ratio, 0.0, 1.0))
    raw = 1.0 - np.exp(-distance_km * (1.0 - income_ratio_clipped))
    return float(np.clip(raw, 0.0, np.nextafter(1.0, 0.0)))


def precision_medicine_gain(
    phi_population_std: float,
    phi_individual_std: float,
) -> float:
    """Gain from personalising treatment to an individual's φ profile.

    Population-average dosing aims for the centre of the φ distribution with
    spread φ_population_std.  Precision medicine narrows this to the
    individual's own φ uncertainty φ_individual_std.  The fractional gain is:

        gain = 1 − φ_individual_std / φ_population_std,   clipped [0, 1)

    gain → 1 means perfect personalisation; gain = 0 means no improvement.

    Parameters
    ----------
    phi_population_std : float — population-level φ standard deviation (must be > 0)
    phi_individual_std : float — individual-level φ standard deviation (must be ≥ 0)

    Returns
    -------
    gain : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If phi_population_std ≤ 0 or phi_individual_std < 0.
    """
    if phi_population_std <= 0.0:
        raise ValueError(
            f"phi_population_std must be > 0, got {phi_population_std!r}"
        )
    if phi_individual_std < 0.0:
        raise ValueError(
            f"phi_individual_std must be ≥ 0, got {phi_individual_std!r}"
        )
    raw = 1.0 - phi_individual_std / phi_population_std
    return float(np.clip(raw, 0.0, 1.0 - _EPSILON))


def clinical_trial_efficiency(
    n_arms: int,
    phi_basin_width: float,
    sigma: float,
) -> float:
    """Efficiency of a clinical trial in exploring the φ-landscape.

    An adaptive multi-arm trial with n_arms simultaneously exploring basins
    of width φ_basin_width in a landscape with noise σ has efficiency:

        η = n_arms × φ_basin_width / (σ + ε)

    Higher η means faster identification of the optimal therapeutic φ target.

    Parameters
    ----------
    n_arms          : int   — number of trial arms (must be ≥ 1)
    phi_basin_width : float — width of each φ basin being tested (must be > 0)
    sigma           : float — landscape noise standard deviation (must be ≥ 0)

    Returns
    -------
    eta : float — trial efficiency (> 0)

    Raises
    ------
    ValueError
        If n_arms < 1, phi_basin_width ≤ 0, or sigma < 0.
    """
    if n_arms < 1:
        raise ValueError(f"n_arms must be ≥ 1, got {n_arms!r}")
    if phi_basin_width <= 0.0:
        raise ValueError(f"phi_basin_width must be > 0, got {phi_basin_width!r}")
    if sigma < 0.0:
        raise ValueError(f"sigma must be ≥ 0, got {sigma!r}")
    return float(n_arms * phi_basin_width / (sigma + _EPSILON))


def cure_criterion(
    phi_post: float,
    phi_healthy: float,
    tolerance: float,
) -> bool:
    """Test whether post-treatment φ is within tolerance of the healthy fixed point.

    A patient is considered cured (or in remission) when:

        |φ_post − φ_healthy| < tolerance

    Parameters
    ----------
    phi_post   : float — post-treatment tissue φ
    phi_healthy : float — healthy reference φ
    tolerance  : float — acceptable deviation (must be > 0)

    Returns
    -------
    bool — True iff the cure criterion is satisfied

    Raises
    ------
    ValueError
        If tolerance ≤ 0.
    """
    if tolerance <= 0.0:
        raise ValueError(f"tolerance must be > 0, got {tolerance!r}")
    return bool(abs(phi_post - phi_healthy) < tolerance)
