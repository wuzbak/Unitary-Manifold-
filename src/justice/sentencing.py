# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/justice/sentencing.py
==========================
Sentencing Theory — Pillar 18b: Judicial & Justice Systems (American Focus).

Theory
------
Sentencing is FTUM-basin assignment.  A just sentence returns the defendant's
φ to the social equilibrium basin while minimising entropy exported to victims,
the community, and the defendant's family network.  Over-sentencing exports
excess entropy outward; under-sentencing leaves the victim's φ unrestored.

The FTUM fixed-point condition for sentencing reads:

    U · ψ_defendant = ψ_equilibrium

where ψ_equilibrium is the social φ-basin that the defendant occupied before
the offence.  The sentence length is the coupling constant of the return
trajectory; optimal sentencing finds the minimum L such that the fixed point
is reached without unnecessary entropy spillover.

American-Specific Bottlenecks
------------------------------
**Racial sentencing disparity** — Black defendants receive sentences ~19.1 %
longer than white defendants for the same offence (Brennan Center, 2019).
This is a direct manifestation of the B_μ noise field injecting systematic
bias into the FTUM operator.  The φ-landscape is tilted, not level.

**Mass incarceration** — 2.1 million incarcerated, the world's highest rate.
This represents a φ-field collapse in low-income communities: each removed
person is a node extracted from the community φ-network, depressing the
collective entanglement capacity of entire neighbourhoods.

**Recidivism at 68 % (3-year rate)** — if incarceration were returning
defendants to the equilibrium basin, re-offending would fall.  The high
recidivism rate proves that the current fixed point is meta-stable, not the
true minimum-entropy state.  The system is cycling in the wrong attractor.

**Solitary confinement** — extreme φ-depletion: prolonged isolation severs
every social entanglement bond.  This violates the Eighth Amendment's
analogy in the Unitary Manifold — it drives φ to zero without any
rehabilitative return trajectory.

**Prison-industrial complex** — private-prison contracts create an economic
B_μ incentive to maximise φ-drain (occupancy) rather than to minimise it.
The profit motive is anti-aligned with the justice fixed point.

**Collateral consequences** — lifetime voting disenfranchisement, employment
barriers, housing exclusion: each is a φ-coupling severed permanently,
preventing the defendant from ever reaching the social equilibrium basin
even after sentence completion.  This is permanent φ-exile.

Actionable Suggestions
-----------------------
- **Evidence-based sentencing guidelines** with mandatory demographic-bias
  audit requirements — measure and correct B_μ annually.
- **Rehabilitation investment** — prison education, mental health treatment,
  and substance-use programmes directly raise φ_rehabilitation and lower
  recidivism probability.
- **Abolish for-profit prisons** — remove the economic B_μ distortion that
  incentivises longer sentences and higher occupancy.
- **Automatic record expungement** after sentence served — restore full
  φ-coupling to employment, housing, and civic participation.
- **Restorative justice circles** as alternative φ-restoration pathway —
  direct victim–offender dialogue can achieve true φ-equilibrium for both
  parties, something carceral sentences rarely do.

Public API
----------
just_sentence_length(phi_offense_severity, phi_community_impact, lam_restorative) -> float
    Minimum sentence that restores φ equilibrium.

recidivism_probability(phi_rehabilitation, phi_reentry_support, base_rate) -> float
    P(re-offend) suppressed by rehabilitation and reentry φ.

sentencing_disparity_index(sentences, group_labels) -> float
    Ratio of max-to-min group-mean sentence minus 1; 0 = equal.

incarceration_community_entropy(n_incarcerated, community_size) -> float
    Fraction of community φ-network removed by incarceration, ∈ [0, 1].

rehabilitation_phi_gain(phi_intake, program_intensity, duration_months) -> float
    φ gained through rehabilitation programmes.

collateral_damage_index(sentence_years, n_dependents) -> float
    Entropy exported to dependents by sentence length.

solitary_phi_depletion(days_solitary, depletion_rate) -> float
    Fractional φ-loss from solitary confinement, ∈ [0, 1].

prison_overcrowding_entropy(n_inmates, capacity) -> float
    Excess normalised entropy from overcrowded facilities.

restorative_justice_phi_restoration(phi_victim_pre, phi_victim_post) -> float
    Fractional φ restored to victim through restorative process.

mass_incarceration_social_cost(phi_per_inmate_loss, n_incarcerated, multiplier) -> float
    Total social φ cost of current incarceration levels.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Just sentence length
# ---------------------------------------------------------------------------

def just_sentence_length(
    phi_offense_severity: float,
    phi_community_impact: float,
    lam_restorative: float,
) -> float:
    """Minimum sentence length that restores φ equilibrium.

    The sentence duration is the integral of the return trajectory back to
    the social equilibrium basin.  It is proportional to the total φ
    disruption (offence + community harm) scaled by the restorative coupling:

        L = λ_restorative · (φ_offense + φ_community)

    Parameters
    ----------
    phi_offense_severity : float — φ-harm of the offence (≥ 0)
    phi_community_impact : float — broader community φ disruption (≥ 0)
    lam_restorative      : float — restorative coupling constant (> 0)

    Returns
    -------
    L : float — just sentence length (same units as φ inputs)

    Raises
    ------
    ValueError
        If any argument violates its constraint.
    """
    if phi_offense_severity < 0.0:
        raise ValueError(f"phi_offense_severity must be ≥ 0, got {phi_offense_severity!r}")
    if phi_community_impact < 0.0:
        raise ValueError(f"phi_community_impact must be ≥ 0, got {phi_community_impact!r}")
    if lam_restorative <= 0.0:
        raise ValueError(f"lam_restorative must be > 0, got {lam_restorative!r}")
    return float(lam_restorative * (phi_offense_severity + phi_community_impact))


# ---------------------------------------------------------------------------
# Recidivism probability
# ---------------------------------------------------------------------------

def recidivism_probability(
    phi_rehabilitation: float,
    phi_reentry_support: float,
    base_rate: float,
) -> float:
    """Probability of re-offending suppressed by rehabilitation φ.

    Without intervention, the base recidivism rate governs.  φ-raising
    programmes (education, mental health, substance treatment) and reentry
    support (housing, employment) jointly suppress re-offending:

        P = base_rate · exp(−φ_rehab · φ_reentry)

    Parameters
    ----------
    phi_rehabilitation  : float — rehabilitation programme intensity (≥ 0)
    phi_reentry_support : float — reentry support quality (≥ 0)
    base_rate           : float — baseline recidivism rate ∈ (0, 1]

    Returns
    -------
    P : float ∈ (0, 1]

    Raises
    ------
    ValueError
        If phi_rehabilitation < 0, phi_reentry_support < 0, or
        base_rate ∉ (0, 1].
    """
    if phi_rehabilitation < 0.0:
        raise ValueError(f"phi_rehabilitation must be ≥ 0, got {phi_rehabilitation!r}")
    if phi_reentry_support < 0.0:
        raise ValueError(f"phi_reentry_support must be ≥ 0, got {phi_reentry_support!r}")
    if not 0.0 < base_rate <= 1.0:
        raise ValueError(f"base_rate must be in (0, 1], got {base_rate!r}")
    return float(base_rate * np.exp(-phi_rehabilitation * phi_reentry_support))


# ---------------------------------------------------------------------------
# Sentencing disparity index
# ---------------------------------------------------------------------------

def sentencing_disparity_index(
    sentences: np.ndarray,
    group_labels: np.ndarray,
) -> float:
    """Ratio of max-to-min group-mean sentence, minus 1.

    A value of 0 indicates perfectly equal sentencing across demographic
    groups.  Positive values quantify the B_μ asymmetry — how much more
    the most-disadvantaged group receives relative to the least:

        SDI = max(group_means) / min(group_means) − 1

    Parameters
    ----------
    sentences    : array-like — sentence lengths (≥ 0), shape (N,)
    group_labels : array-like — integer or string group IDs, shape (N,)

    Returns
    -------
    SDI : float ≥ 0

    Raises
    ------
    ValueError
        If sentences and group_labels have different lengths, fewer than 2
        distinct groups are present, or any sentence is negative.
    """
    s = np.asarray(sentences, dtype=float)
    g = np.asarray(group_labels)
    if s.shape != g.shape:
        raise ValueError("sentences and group_labels must have the same length")
    if np.any(s < 0.0):
        raise ValueError("all sentences must be ≥ 0")
    unique_groups = np.unique(g)
    if unique_groups.size < 2:
        raise ValueError("at least 2 distinct groups are required")
    group_means = np.array([s[g == grp].mean() for grp in unique_groups])
    return float(group_means.max() / (group_means.min() + _NUMERICAL_EPSILON) - 1.0)


# ---------------------------------------------------------------------------
# Incarceration community entropy
# ---------------------------------------------------------------------------

def incarceration_community_entropy(
    n_incarcerated: int,
    community_size: int,
) -> float:
    """Fraction of community φ-network removed by incarceration.

    Each incarcerated individual represents a severed node in the community
    entanglement network.  The resulting entropy is proportional to the
    extraction fraction, clipped to [0, 1]:

        S_comm = n_incarcerated / community_size

    Parameters
    ----------
    n_incarcerated : int — number of incarcerated community members (≥ 0)
    community_size : int — total community population (> 0)

    Returns
    -------
    S_comm : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If n_incarcerated < 0 or community_size ≤ 0.
    """
    if n_incarcerated < 0:
        raise ValueError(f"n_incarcerated must be ≥ 0, got {n_incarcerated!r}")
    if community_size <= 0:
        raise ValueError(f"community_size must be > 0, got {community_size!r}")
    return float(np.clip(n_incarcerated / community_size, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Rehabilitation φ-gain
# ---------------------------------------------------------------------------

def rehabilitation_phi_gain(
    phi_intake: float,
    program_intensity: float,
    duration_months: float,
) -> float:
    """φ accumulated through rehabilitation programmes.

    An individual entering with φ_intake grows their entanglement capacity
    proportionally to programme intensity and duration:

        φ_out = φ_intake · (1 + program_intensity · duration_months / 12)

    Parameters
    ----------
    phi_intake         : float — defendant's φ at programme start (> 0)
    program_intensity  : float — normalised programme quality ∈ [0, 1]
    duration_months    : float — programme duration in months (≥ 0)

    Returns
    -------
    phi_out : float ≥ phi_intake

    Raises
    ------
    ValueError
        If phi_intake ≤ 0, program_intensity ∉ [0, 1], or duration_months < 0.
    """
    if phi_intake <= 0.0:
        raise ValueError(f"phi_intake must be > 0, got {phi_intake!r}")
    if not 0.0 <= program_intensity <= 1.0:
        raise ValueError(f"program_intensity must be in [0, 1], got {program_intensity!r}")
    if duration_months < 0.0:
        raise ValueError(f"duration_months must be ≥ 0, got {duration_months!r}")
    return float(phi_intake * (1.0 + program_intensity * duration_months / 12.0))


# ---------------------------------------------------------------------------
# Collateral damage index
# ---------------------------------------------------------------------------

def collateral_damage_index(
    sentence_years: float,
    n_dependents: int,
) -> float:
    """Entropy exported to dependents by the sentence.

    Children and other dependents suffer φ-displacement proportional to
    both the sentence duration and the number of affected people:

        CDI = sentence_years · n_dependents

    Parameters
    ----------
    sentence_years : float — sentence length in years (≥ 0)
    n_dependents   : int   — number of dependents (≥ 0)

    Returns
    -------
    CDI : float ≥ 0

    Raises
    ------
    ValueError
        If sentence_years < 0 or n_dependents < 0.
    """
    if sentence_years < 0.0:
        raise ValueError(f"sentence_years must be ≥ 0, got {sentence_years!r}")
    if n_dependents < 0:
        raise ValueError(f"n_dependents must be ≥ 0, got {n_dependents!r}")
    return float(sentence_years * n_dependents)


# ---------------------------------------------------------------------------
# Solitary confinement φ-depletion
# ---------------------------------------------------------------------------

def solitary_phi_depletion(
    days_solitary: float,
    depletion_rate: float,
) -> float:
    """Fractional φ-loss from solitary confinement.

    Social isolation exponentially depletes entanglement capacity.  The
    fractional loss saturates at 1 (total φ depletion) for long durations:

        phi_loss = 1 − exp(−depletion_rate · days_solitary)

    Result is clipped to [0, 1].

    Parameters
    ----------
    days_solitary  : float — days spent in solitary confinement (≥ 0)
    depletion_rate : float — per-day φ-depletion rate (> 0)

    Returns
    -------
    phi_loss : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If days_solitary < 0 or depletion_rate ≤ 0.
    """
    if days_solitary < 0.0:
        raise ValueError(f"days_solitary must be ≥ 0, got {days_solitary!r}")
    if depletion_rate <= 0.0:
        raise ValueError(f"depletion_rate must be > 0, got {depletion_rate!r}")
    return float(np.clip(1.0 - np.exp(-depletion_rate * days_solitary), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Prison overcrowding entropy
# ---------------------------------------------------------------------------

def prison_overcrowding_entropy(
    n_inmates: int,
    capacity: int,
) -> float:
    """Normalised excess entropy from overcrowded prison facilities.

    Overcrowding degrades every aspect of the prison environment — health,
    safety, rehabilitation access.  The excess normalised entropy is:

        S_over = max(0, n_inmates − capacity) / (capacity + ε)

    Parameters
    ----------
    n_inmates : int — current inmate population (≥ 0)
    capacity  : int — designed facility capacity (> 0)

    Returns
    -------
    S_over : float ≥ 0

    Raises
    ------
    ValueError
        If n_inmates < 0 or capacity ≤ 0.
    """
    if n_inmates < 0:
        raise ValueError(f"n_inmates must be ≥ 0, got {n_inmates!r}")
    if capacity <= 0:
        raise ValueError(f"capacity must be > 0, got {capacity!r}")
    excess = max(0, n_inmates - capacity)
    return float(excess / (capacity + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Restorative justice φ-restoration
# ---------------------------------------------------------------------------

def restorative_justice_phi_restoration(
    phi_victim_pre: float,
    phi_victim_post: float,
) -> float:
    """Fractional φ restored to the victim through a restorative process.

    A successful restorative justice circle brings the victim's φ back toward
    (or beyond) its pre-offence level.  The restoration fraction is:

        restoration = (phi_victim_post − phi_victim_pre) / (phi_victim_pre + ε)

    Positive = φ restored; negative = victim further harmed by process.

    Parameters
    ----------
    phi_victim_pre  : float — victim φ before restorative process (> 0)
    phi_victim_post : float — victim φ after restorative process (≥ 0)

    Returns
    -------
    restoration : float

    Raises
    ------
    ValueError
        If phi_victim_pre ≤ 0 or phi_victim_post < 0.
    """
    if phi_victim_pre <= 0.0:
        raise ValueError(f"phi_victim_pre must be > 0, got {phi_victim_pre!r}")
    if phi_victim_post < 0.0:
        raise ValueError(f"phi_victim_post must be ≥ 0, got {phi_victim_post!r}")
    return float((phi_victim_post - phi_victim_pre) / (phi_victim_pre + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Mass incarceration social cost
# ---------------------------------------------------------------------------

def mass_incarceration_social_cost(
    phi_per_inmate_loss: float,
    n_incarcerated: int,
    multiplier: float,
) -> float:
    """Total social φ cost of mass incarceration.

    Each incarcerated individual represents a φ-loss to themselves, their
    family, and their community.  The multiplier captures the network
    cascade (families, employers, neighbourhoods):

        cost = multiplier · phi_per_inmate_loss · n_incarcerated

    Parameters
    ----------
    phi_per_inmate_loss : float — individual φ-loss per inmate (≥ 0)
    n_incarcerated      : int   — total incarcerated population (≥ 0)
    multiplier          : float — social cascade multiplier (≥ 1)

    Returns
    -------
    cost : float ≥ 0

    Raises
    ------
    ValueError
        If phi_per_inmate_loss < 0, n_incarcerated < 0, or multiplier < 1.
    """
    if phi_per_inmate_loss < 0.0:
        raise ValueError(f"phi_per_inmate_loss must be ≥ 0, got {phi_per_inmate_loss!r}")
    if n_incarcerated < 0:
        raise ValueError(f"n_incarcerated must be ≥ 0, got {n_incarcerated!r}")
    if multiplier < 1.0:
        raise ValueError(f"multiplier must be ≥ 1, got {multiplier!r}")
    return float(multiplier * phi_per_inmate_loss * n_incarcerated)
