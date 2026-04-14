# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/medicine/systemic.py
=========================
Healthcare Systems as FTUM Fixed-Point Attractors — Pillar 17: Health & Medicine.

Theory
------
A functioning healthcare system is a societal-scale FTUM fixed point: a
stable attractor that minimises systemic entropy (waste, inequality, and
avoidable mortality) by routing the information current J_info efficiently
from patients to providers and from prevention to treatment.

Every systemic failure maps onto a φ-field instability:

Fragmentation
    Broken information current between payers, providers, and patients
    (∂_μ J^μ_info ≠ 0) leads to duplicated tests, missed diagnoses, and
    preventable adverse events.

Inequality
    A φ-gradient without corrective flow: high-φ (well-resourced) regions
    and low-φ (under-resourced) regions coexist without redistribution.
    In equilibrium the Unitary Manifold predicts flow proportional to ∇φ;
    in the healthcare context this flow is absent or reversed.

Administrative overhead
    Bureaucratic processes (prior authorisation, billing, denial management)
    inject B_μ noise into the clinician's workflow, masking the clinical
    signal and displacing time from care to paperwork.

Preventive care underinvestment
    Investing little φ-capacity in prevention forces the system to operate
    far from its fixed point.  Early Δφ accumulation via preventive care
    prevents the catastrophic collapses (hospitalisations, ICU admissions)
    that are far more costly to restore.

Workforce burnout
    Clinician burnout is the depletion of φ_clinician below the minimum
    required to sustain the system's fixed point.  High administrative
    fraction and excessive hours drive φ_clinician → 0.

Actionable suggestions
----------------------
* Universal prior-auth reform: reduce the B_μ administrative noise floor by
  streamlining or automating prior-authorisation and billing processes, so
  clinicians can focus their φ on patients.
* Single-payer information current: consolidate fragmented payer/provider
  information systems so ∂_μ J^μ_info → 0 across the entire system.
* Prevention-first φ investment: re-allocate at least λ_opt = λ / r of the
  system budget to preventive care (the FTUM-optimal allocation).
* Equitable φ redistribution: implement geographic and demographic flow
  corrections that transfer clinical capacity from over-resourced to
  under-resourced regions.

Public API
----------
system_entropy(fragmentation_index, inequality_gini) -> float
    S_sys = fragmentation_index + inequality_gini

administrative_overhead_fraction(admin_cost, total_cost) -> float
    fraction = admin_cost / (total_cost + ε)  clipped [0, 1)

preventive_roi(phi_prevention_investment, lambda_prevention, time_horizon) -> float
    ROI = lambda_prevention × phi_prevention_investment × time_horizon

inequality_phi_gradient(phi_rich, phi_poor) -> float
    gradient = (phi_rich − phi_poor) / (phi_rich + phi_poor + ε)  ∈ [0, 1)

clinician_burnout_risk(hours_per_week, admin_fraction, phi_support) -> float
    risk = hours_per_week × admin_fraction / (phi_support + ε)  clipped [0, 1)

information_current_efficiency(claims_denied_fraction, interop_score) -> float
    eta = interop_score × (1 − claims_denied_fraction)  clipped [0, 1]

universal_coverage_phi(phi_insured, phi_uninsured, coverage_fraction) -> float
    phi_eff = coverage_fraction × phi_insured + (1 − coverage_fraction) × phi_uninsured

prevention_investment_optimal(lambda_prevention, discount_rate) -> float
    phi_opt = lambda_prevention / (discount_rate + ε)

avoidable_mortality_index(phi_actual, phi_optimal, population) -> float
    AMI = population × (phi_optimal − phi_actual) / (phi_optimal + ε)

health_equity_index(phi_values) -> float
    HEI = 1 − std(phi_values) / (mean(phi_values) + ε)  ∈ (−∞, 1]
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

def system_entropy(
    fragmentation_index: float,
    inequality_gini: float,
) -> float:
    """Total systemic entropy from fragmentation and inequality.

    The two primary sources of healthcare system entropy are additive in the
    Unitary Manifold model:

        S_sys = fragmentation_index + inequality_gini

    fragmentation_index quantifies broken information currents;
    inequality_gini (Gini coefficient of health outcomes) quantifies
    unaddressed φ-gradients.

    Parameters
    ----------
    fragmentation_index : float — information-current fragmentation measure (≥ 0)
    inequality_gini     : float — Gini coefficient of health outcomes ∈ [0, 1]

    Returns
    -------
    S_sys : float ≥ 0

    Raises
    ------
    ValueError
        If fragmentation_index < 0 or inequality_gini not in [0, 1].
    """
    if fragmentation_index < 0.0:
        raise ValueError(
            f"fragmentation_index must be ≥ 0, got {fragmentation_index!r}"
        )
    if not (0.0 <= inequality_gini <= 1.0):
        raise ValueError(
            f"inequality_gini must be in [0, 1], got {inequality_gini!r}"
        )
    return float(fragmentation_index + inequality_gini)


def administrative_overhead_fraction(
    admin_cost: float,
    total_cost: float,
) -> float:
    """Fraction of total healthcare spending consumed by administration.

    High administrative overhead injects B_μ noise into the clinical φ
    field, reducing the signal available for patient care:

        overhead = admin_cost / (total_cost + ε),   clipped [0, 1)

    Parameters
    ----------
    admin_cost  : float — administrative expenditure (must be ≥ 0)
    total_cost  : float — total system expenditure (must be ≥ 0)

    Returns
    -------
    fraction : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If admin_cost < 0 or total_cost < 0.
    """
    if admin_cost < 0.0:
        raise ValueError(f"admin_cost must be ≥ 0, got {admin_cost!r}")
    if total_cost < 0.0:
        raise ValueError(f"total_cost must be ≥ 0, got {total_cost!r}")
    raw = admin_cost / (total_cost + _EPSILON)
    return float(np.clip(raw, 0.0, np.nextafter(1.0, 0.0)))


def preventive_roi(
    phi_prevention_investment: float,
    lambda_prevention: float,
    time_horizon: float,
) -> float:
    """Return on investment from preventive care spending.

    Investing φ_prevention_investment units of capacity in prevention yields
    downstream φ savings proportional to the prevention coupling λ and the
    planning horizon:

        ROI = λ_prevention × φ_prevention_investment × time_horizon

    Parameters
    ----------
    phi_prevention_investment : float — prevention investment level (must be ≥ 0)
    lambda_prevention         : float — prevention-to-outcome coupling λ (must be ≥ 0)
    time_horizon              : float — planning horizon in years (must be > 0)

    Returns
    -------
    roi : float ≥ 0

    Raises
    ------
    ValueError
        If any argument violates its domain constraint.
    """
    if phi_prevention_investment < 0.0:
        raise ValueError(
            f"phi_prevention_investment must be ≥ 0, got {phi_prevention_investment!r}"
        )
    if lambda_prevention < 0.0:
        raise ValueError(
            f"lambda_prevention must be ≥ 0, got {lambda_prevention!r}"
        )
    if time_horizon <= 0.0:
        raise ValueError(f"time_horizon must be > 0, got {time_horizon!r}")
    return float(lambda_prevention * phi_prevention_investment * time_horizon)


def inequality_phi_gradient(
    phi_rich: float,
    phi_poor: float,
) -> float:
    """Normalised φ-gradient between well-resourced and under-resourced populations.

    In equilibrium, φ-gradients drive corrective flows.  In a dysfunctional
    healthcare system this flow is absent.  The normalised gradient is:

        gradient = (φ_rich − φ_poor) / (φ_rich + φ_poor + ε)  ∈ [0, 1)

    gradient = 0 → full equity; gradient → 1 → extreme inequality.

    Parameters
    ----------
    phi_rich : float — health outcome φ of the well-resourced group (must be ≥ 0)
    phi_poor : float — health outcome φ of the under-resourced group (must be ≥ 0)

    Returns
    -------
    gradient : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If phi_rich < 0 or phi_poor < 0 or phi_rich < phi_poor.
    """
    if phi_rich < 0.0:
        raise ValueError(f"phi_rich must be ≥ 0, got {phi_rich!r}")
    if phi_poor < 0.0:
        raise ValueError(f"phi_poor must be ≥ 0, got {phi_poor!r}")
    if phi_rich < phi_poor:
        raise ValueError(
            f"phi_rich must be ≥ phi_poor, got phi_rich={phi_rich!r}, phi_poor={phi_poor!r}"
        )
    raw = (phi_rich - phi_poor) / (phi_rich + phi_poor + _EPSILON)
    return float(np.clip(raw, 0.0, 1.0 - _EPSILON))


def clinician_burnout_risk(
    hours_per_week: float,
    admin_fraction: float,
    phi_support: float,
) -> float:
    """Probability that a clinician's φ will fall below the burnout threshold.

    Burnout risk rises with hours worked and the fraction of that time spent
    on administrative tasks, and falls with organisational support (φ_support):

        risk = hours_per_week × admin_fraction / (φ_support + ε),  clipped [0, 1)

    Parameters
    ----------
    hours_per_week : float — weekly clinical hours (must be ≥ 0)
    admin_fraction : float — fraction of time spent on administration ∈ [0, 1]
    phi_support    : float — organisational support level (must be ≥ 0)

    Returns
    -------
    risk : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If hours_per_week < 0, admin_fraction not in [0, 1], or phi_support < 0.
    """
    if hours_per_week < 0.0:
        raise ValueError(f"hours_per_week must be ≥ 0, got {hours_per_week!r}")
    if not (0.0 <= admin_fraction <= 1.0):
        raise ValueError(
            f"admin_fraction must be in [0, 1], got {admin_fraction!r}"
        )
    if phi_support < 0.0:
        raise ValueError(f"phi_support must be ≥ 0, got {phi_support!r}")
    # Michaelis–Menten saturation keeps risk strictly in [0, 1).
    load = hours_per_week * admin_fraction
    return float(load / (load + phi_support + _EPSILON))


def information_current_efficiency(
    claims_denied_fraction: float,
    interop_score: float,
) -> float:
    """Efficiency of the healthcare information current.

    Information flows efficiently when claims are accepted and payer/provider
    systems are interoperable:

        η = interop_score × (1 − claims_denied_fraction),   clipped [0, 1]

    Parameters
    ----------
    claims_denied_fraction : float — fraction of claims denied ∈ [0, 1]
    interop_score          : float — interoperability score ∈ [0, 1]

    Returns
    -------
    eta : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If either argument is outside [0, 1].
    """
    if not (0.0 <= claims_denied_fraction <= 1.0):
        raise ValueError(
            f"claims_denied_fraction must be in [0, 1], got {claims_denied_fraction!r}"
        )
    if not (0.0 <= interop_score <= 1.0):
        raise ValueError(
            f"interop_score must be in [0, 1], got {interop_score!r}"
        )
    raw = interop_score * (1.0 - claims_denied_fraction)
    return float(np.clip(raw, 0.0, 1.0))


def universal_coverage_phi(
    phi_insured: float,
    phi_uninsured: float,
    coverage_fraction: float,
) -> float:
    """Population-average health capacity φ as a function of coverage.

    As coverage_fraction increases toward 1, the effective φ shifts from
    the uninsured average toward the insured average:

        φ_eff = coverage_fraction × φ_insured + (1 − coverage_fraction) × φ_uninsured

    Parameters
    ----------
    phi_insured       : float — average health capacity of insured individuals (must be ≥ 0)
    phi_uninsured     : float — average health capacity of uninsured individuals (must be ≥ 0)
    coverage_fraction : float — fraction of the population insured ∈ [0, 1]

    Returns
    -------
    phi_eff : float ≥ 0

    Raises
    ------
    ValueError
        If phi_insured < 0, phi_uninsured < 0, or coverage_fraction not in [0, 1].
    """
    if phi_insured < 0.0:
        raise ValueError(f"phi_insured must be ≥ 0, got {phi_insured!r}")
    if phi_uninsured < 0.0:
        raise ValueError(f"phi_uninsured must be ≥ 0, got {phi_uninsured!r}")
    if not (0.0 <= coverage_fraction <= 1.0):
        raise ValueError(
            f"coverage_fraction must be in [0, 1], got {coverage_fraction!r}"
        )
    return float(
        coverage_fraction * phi_insured + (1.0 - coverage_fraction) * phi_uninsured
    )


def prevention_investment_optimal(
    lambda_prevention: float,
    discount_rate: float,
) -> float:
    """FTUM-optimal prevention investment level.

    The fixed-point condition for the system entropy balances prevention ROI
    against future discounting.  The optimal φ investment in prevention is:

        φ_opt = λ_prevention / (discount_rate + ε)

    A low discount_rate (long time horizon) justifies large prevention spend;
    a high discount_rate (short-term pressure) suppresses it.

    Parameters
    ----------
    lambda_prevention : float — prevention-to-outcome coupling λ (must be ≥ 0)
    discount_rate     : float — temporal discount rate (must be ≥ 0)

    Returns
    -------
    phi_opt : float ≥ 0

    Raises
    ------
    ValueError
        If lambda_prevention < 0 or discount_rate < 0.
    """
    if lambda_prevention < 0.0:
        raise ValueError(
            f"lambda_prevention must be ≥ 0, got {lambda_prevention!r}"
        )
    if discount_rate < 0.0:
        raise ValueError(f"discount_rate must be ≥ 0, got {discount_rate!r}")
    return float(lambda_prevention / (discount_rate + _EPSILON))


def avoidable_mortality_index(
    phi_actual: float,
    phi_optimal: float,
    population: float,
) -> float:
    """Estimated avoidable mortality due to a sub-optimal healthcare φ.

    The gap between the actual system φ and the attainable optimum translates
    into avoidable deaths proportional to the population:

        AMI = population × (φ_optimal − φ_actual) / (φ_optimal + ε)

    AMI = 0 means the system is operating at its best-practice fixed point.

    Parameters
    ----------
    phi_actual  : float — current system-average health capacity (must be ≥ 0)
    phi_optimal : float — best-practice health capacity (must be > 0)
    population  : float — population size (must be ≥ 0)

    Returns
    -------
    AMI : float ≥ 0

    Raises
    ------
    ValueError
        If phi_actual < 0, phi_optimal ≤ 0, or population < 0.
    """
    if phi_actual < 0.0:
        raise ValueError(f"phi_actual must be ≥ 0, got {phi_actual!r}")
    if phi_optimal <= 0.0:
        raise ValueError(f"phi_optimal must be > 0, got {phi_optimal!r}")
    if population < 0.0:
        raise ValueError(f"population must be ≥ 0, got {population!r}")
    gap = phi_optimal - phi_actual
    return float(population * gap / (phi_optimal + _EPSILON))


def health_equity_index(
    phi_values: np.ndarray,
) -> float:
    """Health equity index: 1 minus the coefficient of variation of φ.

    A perfectly equitable system has identical health capacity across all
    demographic groups: std(φ) = 0 → HEI = 1.  Increasing dispersion
    reduces HEI:

        HEI = 1 − std(φ) / (mean(φ) + ε)

    Parameters
    ----------
    phi_values : ndarray — health capacity φ across demographic groups or regions

    Returns
    -------
    HEI : float ∈ (−∞, 1]  (HEI = 1 ↔ perfect equity)

    Raises
    ------
    ValueError
        If phi_values is empty.
    """
    phi_arr = np.asarray(phi_values, dtype=float)
    if phi_arr.size == 0:
        raise ValueError("phi_values must not be empty")
    return float(1.0 - np.std(phi_arr) / (np.mean(phi_arr) + _EPSILON))
