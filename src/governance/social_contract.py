# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/governance/social_contract.py
===================================
Social Contract as FTUM Fixed-Point Equilibrium — Pillar 19a.

Theory
------
The social contract is the FTUM fixed-point condition for a stable society.
Every member contributes entanglement capacity φ to the collective field; the
collective field returns φ to each member through public goods — infrastructure,
security, health, and education.  A stable society is one where the net φ flow
is zero in equilibrium: contributions balance returns.

    FTUM fixed point:  UΨ* = Ψ*   ↔   Σ φ_returns = Σ φ_contributions

The social contract breaks down when the irreversibility field B_μ — here
instantiated as corruption, inequality, and extraction — disrupts this balance,
pushing the system toward a high-entropy attractor where φ concentrates in a
few sinks rather than circulating through the whole network.

Mapping to canonical political philosophy
-----------------------------------------
Rousseau's "general will"
    The collective φ-field attractor: the emergent consensus trajectory that
    maximises total societal φ rather than any individual agent's φ.

Hobbes' Leviathan
    The minimum-B_μ enforcement mechanism: an institutional structure that
    suppresses noise (violence, defection, non-compliance) so that φ flows
    can propagate without disruption.

Rawls' "veil of ignorance"
    Symmetry in the φ-initial conditions: each citizen is assigned to a random
    position in the φ-distribution before the rules are set, producing a
    Rawlsian preference for designs that maximise the minimum φ (max-min).

Bottlenecks addressed
---------------------
1. Inequality as φ-gradient without corrective flow
   Wealth concentrates in a φ-sink when there is no redistribution current.
   Uncorrected φ-gradients grow exponentially via Mathew-effect dynamics
   (φ_rich → more φ_rich), eventually destabilising the social contract.

2. Corruption as B_μ noise
   Corruption inserts stochastic extraction events that divert φ from the
   public-goods basin to a private-capture attractor.  Each extraction event
   increases the effective B_μ noise floor, degrading all φ flows in the
   network.

3. Free-rider problem
   φ-coupling asymmetry: some agents consume collective φ (public goods) while
   contributing zero to the field.  Above a critical fraction of free-riders
   the φ-field collapses because net contributions can no longer sustain the
   public-goods basin.

4. Legitimacy deficit
   When perceived unfairness causes citizens to believe that the contract is
   broken, their willingness to contribute φ falls below the stability
   threshold, accelerating the collapse.

5. Short-termism
   The political cycle T_pol is often shorter than τ_phi, the timescale on
   which φ investments (e.g., education, infrastructure) compound and return
   value.  This creates a temporal mismatch that systematically underinvests
   in long-horizon φ.

Actionable suggestions
----------------------
- Progressive taxation as φ-redistribution flow: restores equilibrium by
  redirecting φ from high-φ sinks back into the public field.
- Transparency and anti-corruption measures: reduce B_μ noise at source.
- Universal basic services: maintain minimum φ for every citizen, preventing
  the φ-floor from falling below the viability threshold.
- Long-term governance institutions (sovereign wealth funds, constitutional
  fiscal rules): overcome the T_pol < τ_phi short-termism barrier.
- Participatory democracy mechanisms (citizens' assemblies, deliberative
  polling): increase φ-coupling density across the network.

Public API
----------
social_phi_balance(phi_contributions, phi_returns) -> float
    balance = sum(phi_returns) - sum(phi_contributions)
    Positive ↔ net φ gain for society.

contract_stability(phi_collective, phi_minimum_viable) -> bool
    True iff phi_collective >= phi_minimum_viable.

inequality_index(phi_values) -> float
    Gini-analog: I = std(phi_values) / (mean(phi_values) + 1e-30)  ≥ 0.

corruption_phi_drain(B_corruption, phi_public, drain_rate) -> float
    drain = drain_rate * B_corruption * phi_public.

free_rider_fraction(phi_taken, phi_contributed) -> float
    fr = max(0, 1 - phi_contributed / (phi_taken + 1e-30)).

legitimacy_score(phi_perceived_fairness, phi_required) -> float
    score = min(phi_perceived_fairness / (phi_required + 1e-30), 1.0).

redistribution_effectiveness(phi_before, phi_after, phi_transferred) -> float
    eff = (phi_after - phi_before) / (phi_transferred + 1e-30).

public_goods_phi(phi_total_tax, provision_efficiency) -> float
    phi_goods = provision_efficiency * phi_total_tax.

trust_decay(phi_trust_initial, B_scandal, time, tau) -> float
    phi_trust = phi_trust_initial * exp(-B_scandal * time / tau).

intergenerational_phi_transfer(phi_current, investment_fraction, discount_rate) -> float
    phi_future = phi_current * investment_fraction / (discount_rate + 1e-30).
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Social contract balance and stability
# ---------------------------------------------------------------------------

def social_phi_balance(
    phi_contributions: np.ndarray | list[float],
    phi_returns: np.ndarray | list[float],
) -> float:
    """Net φ balance of the social contract.

    Computes the difference between the total φ returned to citizens through
    public goods and the total φ contributed through taxes and cooperation:

        balance = Σ φ_returns − Σ φ_contributions

    A positive balance means society generates more φ than it consumes
    (a growing commons); a negative balance signals unsustainable extraction.

    Parameters
    ----------
    phi_contributions : array-like — φ contributed by each citizen/sector.
    phi_returns       : array-like — φ received by each citizen/sector.

    Returns
    -------
    balance : float — net φ flow (positive = net societal gain).

    Raises
    ------
    ValueError
        If either array is empty.
    """
    c = np.asarray(phi_contributions, dtype=float)
    r = np.asarray(phi_returns, dtype=float)
    if c.size == 0 or r.size == 0:
        raise ValueError("phi_contributions and phi_returns must be non-empty.")
    return float(np.sum(r) - np.sum(c))


def contract_stability(
    phi_collective: float,
    phi_minimum_viable: float,
) -> bool:
    """Test whether the collective φ meets the minimum viability threshold.

    A stable social contract requires that the collective φ — the total
    entanglement capacity circulating through public institutions — is at least
    equal to the minimum viable level below which the contract dissolves.

    Parameters
    ----------
    phi_collective      : float — current collective φ field strength (≥ 0).
    phi_minimum_viable  : float — minimum φ required for stability (≥ 0).

    Returns
    -------
    stable : bool — True iff phi_collective >= phi_minimum_viable.

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_collective < 0.0:
        raise ValueError(f"phi_collective must be >= 0, got {phi_collective!r}")
    if phi_minimum_viable < 0.0:
        raise ValueError(f"phi_minimum_viable must be >= 0, got {phi_minimum_viable!r}")
    return bool(phi_collective >= phi_minimum_viable)


# ---------------------------------------------------------------------------
# Inequality and corruption
# ---------------------------------------------------------------------------

def inequality_index(phi_values: np.ndarray | list[float]) -> float:
    """Gini-analog inequality index for a φ distribution.

    Measures the dispersion of the φ field across citizens relative to its
    mean.  A perfectly equal society (all φ identical) gives I = 0; a highly
    unequal distribution gives I >> 0.

        I = std(φ) / (mean(φ) + ε)

    Parameters
    ----------
    phi_values : array-like — φ values across agents (must be non-empty).

    Returns
    -------
    I : float — inequality index (≥ 0).

    Raises
    ------
    ValueError
        If phi_values is empty.
    """
    arr = np.asarray(phi_values, dtype=float)
    if arr.size == 0:
        raise ValueError("phi_values must be non-empty.")
    return float(np.std(arr) / (np.mean(arr) + _NUMERICAL_EPSILON))


def corruption_phi_drain(
    B_corruption: float,
    phi_public: float,
    drain_rate: float,
) -> float:
    """φ drained from the public basin by corruption.

    Corruption acts as a B_μ noise field that extracts φ from the public-goods
    attractor and redirects it into private-capture basins:

        drain = drain_rate × B_corruption × φ_public

    Parameters
    ----------
    B_corruption : float — corruption intensity (B_μ field amplitude, ≥ 0).
    phi_public   : float — current public φ field strength (≥ 0).
    drain_rate   : float — extraction coupling constant (≥ 0).

    Returns
    -------
    drain : float — φ extracted per unit time (≥ 0).

    Raises
    ------
    ValueError
        If any argument is negative.
    """
    if B_corruption < 0.0:
        raise ValueError(f"B_corruption must be >= 0, got {B_corruption!r}")
    if phi_public < 0.0:
        raise ValueError(f"phi_public must be >= 0, got {phi_public!r}")
    if drain_rate < 0.0:
        raise ValueError(f"drain_rate must be >= 0, got {drain_rate!r}")
    return float(drain_rate * B_corruption * phi_public)


# ---------------------------------------------------------------------------
# Free-rider problem and legitimacy
# ---------------------------------------------------------------------------

def free_rider_fraction(
    phi_taken: float,
    phi_contributed: float,
) -> float:
    """Fraction of φ consumed without contributing.

    Quantifies the free-rider asymmetry: how much of the φ taken from the
    collective field is not matched by a corresponding contribution.

        fr = max(0, 1 − φ_contributed / (φ_taken + ε))

    A value of 0 means full reciprocity; 1 means the agent contributes nothing.

    Parameters
    ----------
    phi_taken        : float — φ consumed from public goods (≥ 0).
    phi_contributed  : float — φ contributed to the collective (≥ 0).

    Returns
    -------
    fr : float — free-rider fraction in [0, 1].

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_taken < 0.0:
        raise ValueError(f"phi_taken must be >= 0, got {phi_taken!r}")
    if phi_contributed < 0.0:
        raise ValueError(f"phi_contributed must be >= 0, got {phi_contributed!r}")
    return float(max(0.0, 1.0 - phi_contributed / (phi_taken + _NUMERICAL_EPSILON)))


def legitimacy_score(
    phi_perceived_fairness: float,
    phi_required: float,
) -> float:
    """Legitimacy of the social contract as perceived by citizens.

    When citizens perceive the system as fair — i.e., their φ_perceived_fairness
    meets or exceeds the φ they consider morally required — the contract enjoys
    full legitimacy.  Below that threshold, legitimacy erodes linearly.

        score = min(φ_perceived_fairness / (φ_required + ε), 1.0)

    Parameters
    ----------
    phi_perceived_fairness : float — perceived φ of the system (≥ 0).
    phi_required           : float — φ threshold for full legitimacy (≥ 0).

    Returns
    -------
    score : float — legitimacy score in [0, 1].

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_perceived_fairness < 0.0:
        raise ValueError(
            f"phi_perceived_fairness must be >= 0, got {phi_perceived_fairness!r}"
        )
    if phi_required < 0.0:
        raise ValueError(f"phi_required must be >= 0, got {phi_required!r}")
    return float(min(phi_perceived_fairness / (phi_required + _NUMERICAL_EPSILON), 1.0))


# ---------------------------------------------------------------------------
# Redistribution and public goods
# ---------------------------------------------------------------------------

def redistribution_effectiveness(
    phi_before: float,
    phi_after: float,
    phi_transferred: float,
) -> float:
    """Effectiveness of a redistribution policy.

    Measures how much of the transferred φ actually improves the collective
    field, accounting for leakage, administrative overhead, and policy friction:

        eff = (φ_after − φ_before) / (φ_transferred + ε)

    A value of 1 means every unit of transferred φ raises collective φ by one
    unit (perfect efficiency).  Values < 1 indicate losses; values > 1 indicate
    that the redistribution unlocked additional φ through multiplier effects.

    Parameters
    ----------
    phi_before      : float — collective φ before redistribution.
    phi_after       : float — collective φ after redistribution.
    phi_transferred : float — total φ transferred (≥ 0).

    Returns
    -------
    eff : float — redistribution effectiveness.

    Raises
    ------
    ValueError
        If phi_transferred is negative.
    """
    if phi_transferred < 0.0:
        raise ValueError(f"phi_transferred must be >= 0, got {phi_transferred!r}")
    return float((phi_after - phi_before) / (phi_transferred + _NUMERICAL_EPSILON))


def public_goods_phi(
    phi_total_tax: float,
    provision_efficiency: float,
) -> float:
    """φ delivered as public goods from tax revenue.

    Models the conversion of tax receipts (φ extracted from citizens) into
    public-goods φ (infrastructure, health, education, security):

        φ_goods = η × φ_total_tax

    where η = provision_efficiency ∈ [0, 1] captures bureaucratic overhead,
    corruption leakage, and policy design quality.

    Parameters
    ----------
    phi_total_tax        : float — total φ collected as tax (≥ 0).
    provision_efficiency : float — fraction of tax converted to public goods
                           (clipped to [0, 1]).

    Returns
    -------
    phi_goods : float — public-goods φ delivered (≥ 0).

    Raises
    ------
    ValueError
        If phi_total_tax is negative.
    """
    if phi_total_tax < 0.0:
        raise ValueError(f"phi_total_tax must be >= 0, got {phi_total_tax!r}")
    eta = float(np.clip(provision_efficiency, 0.0, 1.0))
    return float(eta * phi_total_tax)


# ---------------------------------------------------------------------------
# Trust dynamics and intergenerational transfer
# ---------------------------------------------------------------------------

def trust_decay(
    phi_trust_initial: float,
    B_scandal: float,
    time: float,
    tau: float,
) -> float:
    """Exponential decay of institutional trust under scandal or B_μ shocks.

    A scandal or institutional failure acts as a B_μ impulse that drives
    exponential erosion of the φ-trust field:

        φ_trust(t) = φ_trust_initial × exp(−B_scandal × t / τ)

    Parameters
    ----------
    phi_trust_initial : float — initial trust φ (≥ 0).
    B_scandal         : float — scandal intensity (B_μ field strength, ≥ 0).
    time              : float — elapsed time since the shock (≥ 0).
    tau               : float — institutional memory timescale (> 0).

    Returns
    -------
    phi_trust : float — remaining trust φ after decay (≥ 0).

    Raises
    ------
    ValueError
        If any argument is out of range.
    """
    if phi_trust_initial < 0.0:
        raise ValueError(f"phi_trust_initial must be >= 0, got {phi_trust_initial!r}")
    if B_scandal < 0.0:
        raise ValueError(f"B_scandal must be >= 0, got {B_scandal!r}")
    if time < 0.0:
        raise ValueError(f"time must be >= 0, got {time!r}")
    if tau <= 0.0:
        raise ValueError(f"tau must be > 0, got {tau!r}")
    return float(phi_trust_initial * np.exp(-B_scandal * time / tau))


def intergenerational_phi_transfer(
    phi_current: float,
    investment_fraction: float,
    discount_rate: float,
) -> float:
    """φ transferred to the next generation through long-horizon investment.

    Short-termism prevents democratic systems from investing in slow-return
    φ projects (education, climate, infrastructure).  This function estimates
    the effective intergenerational φ transfer:

        φ_future = φ_current × f_invest / (r + ε)

    where f_invest is the fraction of current φ invested rather than consumed,
    and r is the temporal discount rate applied by policymakers.  A lower
    discount rate → larger φ_future (more intergenerational solidarity).

    Parameters
    ----------
    phi_current         : float — current societal φ (≥ 0).
    investment_fraction : float — fraction of φ re-invested (clipped [0, 1]).
    discount_rate       : float — political discount rate applied to future φ
                          (≥ 0).

    Returns
    -------
    phi_future : float — intergenerational φ transfer (≥ 0).

    Raises
    ------
    ValueError
        If phi_current is negative.
    """
    if phi_current < 0.0:
        raise ValueError(f"phi_current must be >= 0, got {phi_current!r}")
    f = float(np.clip(investment_fraction, 0.0, 1.0))
    return float(phi_current * f / (discount_rate + _NUMERICAL_EPSILON))
