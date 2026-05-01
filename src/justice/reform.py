# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/justice/reform.py
======================
Justice Reform Dynamics — Pillar 18c: Judicial & Justice Systems (American Focus).

Theory
------
Reform is FTUM basin re-routing.  The current US justice system sits in a
meta-stable high-entropy fixed point characterised by mass incarceration,
racial disparity, and cash bail.  Reform pathways are perturbations that
can transition the system to the lower-entropy, higher-φ justice fixed
point.  The activation energy for reform equals the political B_μ noise
that must be overcome for the transition to occur.

The FTUM perspective on reform:

    U · ψ_current = ψ_current   (current meta-stable attractor)
    U · ψ_just    = ψ_just      (target just-society fixed point)

Reform is the process of applying a perturbation operator Δ such that the
system escapes the current basin:

    (U + Δ) · ψ_current → ψ_just

The perturbation Δ must exceed the B_μ activation barrier to be effective.

American-Specific Bottlenecks
------------------------------
**Political capture by prison-industrial lobby** — campaign contributions,
revolving-door employment, and mandatory-occupancy contracts create a B_μ
distortion that suppresses reform signals before they reach legislative
thresholds.  The information current for reform is attenuated by the lobby's
counter-field.

**"Tough on crime" electoral B_μ** — politicians optimise their re-election
φ, not the justice φ.  This misalignment means that reforms that would
reduce B_μ in the justice system may increase B_μ in the political system
(electoral risk).  The two φ-landscapes are anti-coupled.

**Federalism fragmentation** — 50 state systems, 3,000+ counties, create an
information-current barrier.  Best-practice reforms propagate slowly across
jurisdiction boundaries; failure modes propagate even more slowly.  The
absence of a national sentencing database means the φ-measurement needed
for reform is blocked.

**Under-resourced public defenders** — the structural φ inequality created
by underfunding persists until budget parity is achieved.  Landmark court
decisions (Gideon v. Wainwright) established the right but not the funding
mechanism; the structural B_μ persists 60 years later.

**Lack of data transparency** — sealing of court records, proprietary risk-
assessment algorithms, and fragmented databases prevent the φ-measurement
needed to identify and correct disparity.  Reform cannot be evidence-based
without evidence.

Actionable Suggestions
-----------------------
- **Police accountability legislation** — body-camera mandates, use-of-force
  standards, and independent oversight boards directly reduce the B_μ noise
  of excessive force, restoring civil trust.
- **Qualified immunity reform** — removing or narrowing QI restores the civil
  liability φ-correction mechanism that allows victims to seek redress.
- **National sentencing database** — a public, demographic-disaggregated
  database with mandatory annual disparity audits enables evidence-based
  reform at every jurisdiction.
- **Public defender parity funding** — matching prosecution budgets dollar-
  for-dollar is the single most direct lever for equalising φ-access.
- **Drug decriminalisation + treatment-first** — shifting the φ-flow from
  punitive incarceration to therapeutic rehabilitation reduces total social
  entropy while decreasing recidivism.

Public API
----------
reform_activation_energy(B_political, n_stakeholders) -> float
    Energy barrier to reform: B_political · sqrt(n_stakeholders).

policy_phi_shift(phi_current, delta_phi_policy, decay_rate) -> float
    φ after policy implementation with exponential decay discount.

reform_coalition_strength(phi_values) -> float
    Mean φ of coalition members; proxy for collective reform capacity.

public_defender_parity_gap(budget_defense, budget_prosecution) -> float
    Fractional funding gap, ∈ [0, 1).

transparency_score(n_public_records, n_total_records) -> float
    Fraction of records publicly accessible, ∈ [0, 1].

drug_decrim_phi_gain(phi_treatment, phi_incarceration, decrim_fraction) -> float
    Net φ-gain from shifting decrim_fraction of cases to treatment.

police_accountability_reduction(B_misconduct, accountability_factor) -> float
    Reduced misconduct B_μ after accountability measures.

reform_timeline(activation_energy, coalition_phi, time_constant) -> float
    Expected time for reform to take effect.

recidivism_reduction_from_reform(base_recidivism, reform_phi_gain) -> float
    Absolute reduction in recidivism rate attributable to reform.

justice_system_phi(phi_fairness, phi_access, phi_rehabilitation, phi_accountability) -> float
    Composite justice-system φ as arithmetic mean of four pillars.
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

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Reform activation energy
# ---------------------------------------------------------------------------

def reform_activation_energy(
    B_political: float,
    n_stakeholders: int,
) -> float:
    """Energy barrier that reform must overcome.

    Political B_μ noise scales linearly with the bias amplitude, while the
    number of stakeholders introduces a collective-action cost that grows
    as the square root (mean-field approximation):

        E_reform = B_political · sqrt(n_stakeholders)

    Parameters
    ----------
    B_political    : float — political bias field magnitude (≥ 0)
    n_stakeholders : int   — number of stakeholders involved (≥ 1)

    Returns
    -------
    E_reform : float ≥ 0

    Raises
    ------
    ValueError
        If B_political < 0 or n_stakeholders < 1.
    """
    if B_political < 0.0:
        raise ValueError(f"B_political must be ≥ 0, got {B_political!r}")
    if n_stakeholders < 1:
        raise ValueError(f"n_stakeholders must be ≥ 1, got {n_stakeholders!r}")
    return float(B_political * np.sqrt(n_stakeholders))


# ---------------------------------------------------------------------------
# Policy φ-shift
# ---------------------------------------------------------------------------

def policy_phi_shift(
    phi_current: float,
    delta_phi_policy: float,
    decay_rate: float,
) -> float:
    """φ after a policy is implemented, discounted by implementation decay.

    Policies rarely deliver their full theoretical φ-shift due to
    enforcement lag, stakeholder resistance, and institutional friction.
    An exponential decay factor models this attenuation:

        phi_new = phi_current + delta_phi_policy · exp(−decay_rate)

    Parameters
    ----------
    phi_current      : float — current system φ (> 0)
    delta_phi_policy : float — theoretical φ-shift of the policy (any sign)
    decay_rate       : float — implementation decay constant (≥ 0)

    Returns
    -------
    phi_new : float

    Raises
    ------
    ValueError
        If phi_current ≤ 0 or decay_rate < 0.
    """
    if phi_current <= 0.0:
        raise ValueError(f"phi_current must be > 0, got {phi_current!r}")
    if decay_rate < 0.0:
        raise ValueError(f"decay_rate must be ≥ 0, got {decay_rate!r}")
    return float(phi_current + delta_phi_policy * np.exp(-decay_rate))


# ---------------------------------------------------------------------------
# Reform coalition strength
# ---------------------------------------------------------------------------

def reform_coalition_strength(phi_values: np.ndarray) -> float:
    """Mean φ of coalition members as a proxy for collective reform capacity.

    A reform coalition's ability to overcome the activation barrier is
    proportional to the mean entanglement capacity of its members:

        strength = sum(φ_i) / (N + ε)

    Parameters
    ----------
    phi_values : array-like — φ of each coalition member (each > 0).
                 Must have at least 1 element.

    Returns
    -------
    strength : float > 0

    Raises
    ------
    ValueError
        If phi_values is empty or any element is ≤ 0.
    """
    vals = np.asarray(phi_values, dtype=float)
    if vals.size == 0:
        raise ValueError("phi_values must not be empty")
    if np.any(vals <= 0.0):
        raise ValueError("all phi_values must be > 0")
    return float(vals.sum() / (vals.size + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Public defender parity gap
# ---------------------------------------------------------------------------

def public_defender_parity_gap(
    budget_defense: float,
    budget_prosecution: float,
) -> float:
    """Fractional funding gap between defense and prosecution.

    Parity requires budget_defense == budget_prosecution.  The gap measures
    how much the defense is under-resourced relative to the prosecution:

        gap = (budget_prosecution − budget_defense) / (budget_prosecution + ε)

    Clipped to [0, 1).

    Parameters
    ----------
    budget_defense     : float — public defender budget (≥ 0)
    budget_prosecution : float — prosecution budget (≥ 0)

    Returns
    -------
    gap : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if budget_defense < 0.0:
        raise ValueError(f"budget_defense must be ≥ 0, got {budget_defense!r}")
    if budget_prosecution < 0.0:
        raise ValueError(f"budget_prosecution must be ≥ 0, got {budget_prosecution!r}")
    raw = (budget_prosecution - budget_defense) / (budget_prosecution + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, np.nextafter(1.0, 0.0)))


# ---------------------------------------------------------------------------
# Transparency score
# ---------------------------------------------------------------------------

def transparency_score(
    n_public_records: int,
    n_total_records: int,
) -> float:
    """Fraction of court records publicly accessible.

    Transparency is necessary for evidence-based reform; sealed records
    prevent φ-measurement of systemic bias:

        score = n_public_records / (n_total_records + ε)

    Clipped to [0, 1].

    Parameters
    ----------
    n_public_records : int — records available to the public (≥ 0)
    n_total_records  : int — total records in the system (≥ 0)

    Returns
    -------
    score : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If either argument is negative or n_public_records > n_total_records.
    """
    if n_public_records < 0:
        raise ValueError(f"n_public_records must be ≥ 0, got {n_public_records!r}")
    if n_total_records < 0:
        raise ValueError(f"n_total_records must be ≥ 0, got {n_total_records!r}")
    if n_public_records > n_total_records:
        raise ValueError("n_public_records cannot exceed n_total_records")
    raw = n_public_records / (n_total_records + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Drug decriminalisation φ-gain
# ---------------------------------------------------------------------------

def drug_decrim_phi_gain(
    phi_treatment: float,
    phi_incarceration: float,
    decrim_fraction: float,
) -> float:
    """Net φ-gain from decriminalising drug offences and redirecting to treatment.

    For each decriminalised case the φ flow shifts from the punitive
    incarceration pathway to the therapeutic treatment pathway:

        gain = decrim_fraction · (phi_treatment − phi_incarceration)

    Parameters
    ----------
    phi_treatment      : float — φ generated per person through treatment (≥ 0)
    phi_incarceration  : float — φ generated per person through incarceration (≥ 0)
    decrim_fraction    : float — fraction of cases decriminalised ∈ [0, 1]

    Returns
    -------
    gain : float (can be negative if treatment φ < incarceration φ)

    Raises
    ------
    ValueError
        If phi_treatment < 0, phi_incarceration < 0, or
        decrim_fraction ∉ [0, 1].
    """
    if phi_treatment < 0.0:
        raise ValueError(f"phi_treatment must be ≥ 0, got {phi_treatment!r}")
    if phi_incarceration < 0.0:
        raise ValueError(f"phi_incarceration must be ≥ 0, got {phi_incarceration!r}")
    if not 0.0 <= decrim_fraction <= 1.0:
        raise ValueError(f"decrim_fraction must be in [0, 1], got {decrim_fraction!r}")
    return float(decrim_fraction * (phi_treatment - phi_incarceration))


# ---------------------------------------------------------------------------
# Police accountability B_μ reduction
# ---------------------------------------------------------------------------

def police_accountability_reduction(
    B_misconduct: float,
    accountability_factor: float,
) -> float:
    """Residual misconduct B_μ after accountability measures are applied.

    Accountability mechanisms (oversight boards, body cameras, independent
    prosecutors) reduce the B_μ noise field proportionally:

        B_reduced = B_misconduct · (1 − accountability_factor)

    Parameters
    ----------
    B_misconduct          : float — baseline misconduct B_μ (≥ 0)
    accountability_factor : float — fractional reduction achieved ∈ [0, 1]

    Returns
    -------
    B_reduced : float ≥ 0

    Raises
    ------
    ValueError
        If B_misconduct < 0 or accountability_factor ∉ [0, 1].
    """
    if B_misconduct < 0.0:
        raise ValueError(f"B_misconduct must be ≥ 0, got {B_misconduct!r}")
    if not 0.0 <= accountability_factor <= 1.0:
        raise ValueError(
            f"accountability_factor must be in [0, 1], got {accountability_factor!r}"
        )
    return float(B_misconduct * (1.0 - accountability_factor))


# ---------------------------------------------------------------------------
# Reform timeline
# ---------------------------------------------------------------------------

def reform_timeline(
    activation_energy: float,
    coalition_phi: float,
    time_constant: float,
) -> float:
    """Expected time for a reform to take effect.

    The reform timeline is proportional to the activation energy and
    inversely proportional to the coalition's φ capacity:

        T = time_constant · activation_energy / (coalition_φ + ε)

    Parameters
    ----------
    activation_energy : float — barrier to reform (≥ 0)
    coalition_phi     : float — aggregate coalition φ (> 0)
    time_constant     : float — system-specific timescale (> 0)

    Returns
    -------
    T : float ≥ 0

    Raises
    ------
    ValueError
        If activation_energy < 0, coalition_phi ≤ 0, or time_constant ≤ 0.
    """
    if activation_energy < 0.0:
        raise ValueError(f"activation_energy must be ≥ 0, got {activation_energy!r}")
    if coalition_phi <= 0.0:
        raise ValueError(f"coalition_phi must be > 0, got {coalition_phi!r}")
    if time_constant <= 0.0:
        raise ValueError(f"time_constant must be > 0, got {time_constant!r}")
    return float(time_constant * activation_energy / (coalition_phi + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Recidivism reduction from reform
# ---------------------------------------------------------------------------

def recidivism_reduction_from_reform(
    base_recidivism: float,
    reform_phi_gain: float,
) -> float:
    """Absolute reduction in recidivism attributable to a reform measure.

    A reform that raises system φ by reform_phi_gain reduces the recidivism
    rate by a fraction that saturates toward base_recidivism:

        reduction = base_recidivism · (1 − exp(−reform_phi_gain))

    Parameters
    ----------
    base_recidivism  : float — pre-reform recidivism rate ∈ (0, 1]
    reform_phi_gain  : float — φ-gain delivered by the reform (≥ 0)

    Returns
    -------
    reduction : float ∈ [0, base_recidivism]

    Raises
    ------
    ValueError
        If base_recidivism ∉ (0, 1] or reform_phi_gain < 0.
    """
    if not 0.0 < base_recidivism <= 1.0:
        raise ValueError(f"base_recidivism must be in (0, 1], got {base_recidivism!r}")
    if reform_phi_gain < 0.0:
        raise ValueError(f"reform_phi_gain must be ≥ 0, got {reform_phi_gain!r}")
    return float(base_recidivism * (1.0 - np.exp(-reform_phi_gain)))


# ---------------------------------------------------------------------------
# Justice system composite φ
# ---------------------------------------------------------------------------

def justice_system_phi(
    phi_fairness: float,
    phi_access: float,
    phi_rehabilitation: float,
    phi_accountability: float,
) -> float:
    """Composite justice-system φ as arithmetic mean of four pillars.

    The overall φ of the justice system is characterised by four independent
    entanglement-capacity dimensions.  Each must be high for the system to
    approach the FTUM fixed point:

        total = (φ_fairness + φ_access + φ_rehabilitation + φ_accountability) / 4

    Parameters
    ----------
    phi_fairness        : float — equal-protection φ (≥ 0)
    phi_access          : float — access-to-justice φ (≥ 0)
    phi_rehabilitation  : float — rehabilitation programme φ (≥ 0)
    phi_accountability  : float — police/judicial accountability φ (≥ 0)

    Returns
    -------
    total : float ≥ 0

    Raises
    ------
    ValueError
        If any argument is negative.
    """
    for name, val in (
        ("phi_fairness", phi_fairness),
        ("phi_access", phi_access),
        ("phi_rehabilitation", phi_rehabilitation),
        ("phi_accountability", phi_accountability),
    ):
        if val < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {val!r}")
    return float((phi_fairness + phi_access + phi_rehabilitation + phi_accountability) / 4.0)
