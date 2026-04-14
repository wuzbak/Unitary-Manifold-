# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling/producer_responsibility.py
======================================
Producer Return Obligation — Pillar 16d.

**The Problem**
---------------
In 4D spacetime, once a product leaves the factory it disperses across
supply chains, geographies, and ownership chains.  When it reaches
end-of-life it is usually far from its origin — geographically, legally,
and in φ-field terms.  Without an enforcement mechanism, waste collapses
to landfill (A_score → 0) and the producer's φ-debt is never repaid.

**The Manifold Answer**
-----------------------
The 5D geometry offers two complementary enforcement mechanisms:

1. **Physical** — Every manufactured product inherits a φ-origin label
   (a topological winding-number fingerprint tied to the producer's field
   at the moment of manufacture).  The producer's φ-field creates a
   persistent return gradient:

       F_return(r) = κ · (φ_origin − φ_waste) · exp(−r / ξ)

   This gradient represents the energetic tendency of the degraded product
   to flow back toward its origin's φ-well — the same physics that drives
   entropy minimisation in every attractor in the manifold.  Deposit-
   refund schemes are the human engineering analogue: they convert this
   latent φ-potential into an explicit economic force.

2. **Legal** — Manufacture creates a φ-debt equal to the virgin φ.  If
   the producer recovers the product at alignment A_score, the remaining
   debt is:

       D_remaining = φ_virgin · (1 − A_score)

   An Extended Producer Responsibility (EPR) levy converts the entropy
   gap between manufacture and disposal into an economic cost:

       L_epr = c_levy · k_B · ln(φ_virgin / φ_waste)

   This makes entropy laundering (mass-recovery at low A_score) more
   expensive than genuine closed-loop recovery (A_score ≥ 0.95).

**What Humans Get Wrong**
--------------------------
1. *Mass accounting ≠ φ accounting.*  A product returned at 30 % φ-
   alignment still carries 70 % of its φ-debt.  Current EPR regulations
   count mass collected, not φ recovered.
2. *Geographic distance is a proxy for φ-separation.*  The further a
   product travels from its origin, the higher the return cost — but the
   manifold shows this cost is also proportional to φ_origin − φ_waste,
   not only to transport distance.
3. *Voluntary return collapses without incentive.*  The return probability
   follows a Boltzmann distribution in φ-debt; without a deposit or levy
   the effective "economic temperature" k_econ is too high and voluntary
   return is suppressed.
4. *Deposit sizing is guesswork.*  The equilibrium deposit is the φ-
   return energy — exactly the product's φ-debt discounted by collection
   efficiency.  Setting it lower under-incentivises return; higher wastes
   revenue.

Theory summary
--------------
Return force (radial φ-gradient from producer's origin):
    F_return(r) = κ · (φ_origin − φ_waste) · exp(−r / ξ)

Producer φ-debt after partial recovery:
    D_remaining = φ_virgin · max(1 − A_score, 0)

EPR entropy levy:
    L_epr = c_levy · k_B · ln(φ_virgin / φ_waste)

Equilibrium deposit:
    δ_eq = c_levy · (φ_virgin − φ_waste) / η_collection

Closed-loop enforcement radius (geographic range for economic return):
    r_max = ξ · ln(κ · (φ_origin − φ_waste) / F_min)

Return probability (Boltzmann factor over φ-debt):
    P_return = exp(−D_remaining / k_econ)

Take-back efficiency (fraction of φ-debt cleared):
    η_takeback = A_score · R_collection

φ-origin label (topological fingerprint from virgin φ and winding number):
    Λ = (φ_virgin · N_w · producer_seed) mod φ_max

Systemic entropy saved by EPR vs. municipal collection:
    ΔS = N_products · φ_virgin · (A_epr − A_municipal)

Lifecycle return incentive (levy at each lifecycle stage):
    I_i = c_levy · max(φ_{i-1} − φ_i, 0)   for each step i

Public API
----------
phi_return_force(phi_origin, phi_waste, r, kappa, xi)
    Radial φ-gradient force pulling end-of-life product back to its origin.

producer_phi_debt(phi_virgin, a_score)
    Remaining φ-debt after a recovery with alignment score a_score.

epr_levy(phi_virgin, phi_waste, c_levy, k_B)
    Economic EPR levy derived from the entropy gap at end-of-life.

deposit_refund_amount(phi_virgin, phi_waste, c_levy, collection_efficiency)
    Equilibrium deposit that makes voluntary return the rational choice.

closed_loop_radius(phi_origin, phi_waste, kappa, xi, F_min)
    Maximum geographic separation at which economical return is possible.

return_probability(phi_debt, k_econ)
    Boltzmann-weighted probability of voluntary return given φ-debt.

takeback_efficiency(a_score, collection_rate)
    Fraction of φ-debt cleared by a producer take-back programme.

phi_origin_label(phi_virgin, n_w, producer_seed, phi_max)
    Topological fingerprint that identifies the producer from the product.

systemic_entropy_saved(n_products, phi_virgin, a_score_epr, a_score_municipal)
    System-level entropy benefit of EPR over municipal waste collection.

lifecycle_return_incentive(phi_trace, c_levy)
    EPR levy incentive at each stage of the product lifecycle.
"""

from __future__ import annotations

import numpy as np

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Physical enforcement — the φ-return gradient
# ---------------------------------------------------------------------------

def phi_return_force(
    phi_origin: float,
    phi_waste: float,
    r: float,
    kappa: float = 1.0,
    xi: float = 1.0,
) -> float:
    """Radial φ-gradient force pulling end-of-life product back to its origin.

    In the 5D geometry every producer maintains a φ-field centred on their
    manufacturing facility.  When a product reaches end-of-life its φ has
    decayed to φ_waste < φ_origin.  The gradient of the origin field drives
    a return force that decays exponentially with the supply-chain separation
    distance r:

        F_return(r) = κ · (φ_origin − φ_waste) · exp(−r / ξ)

    κ is the return coupling constant (how strongly the origin field binds
    the product); ξ is the correlation length of the producer's φ-field
    (how far that field reaches into the supply chain).  Deposit-refund
    schemes are the economic engineering of this physical potential.

    Parameters
    ----------
    phi_origin : float — φ at the producer's manufacturing origin (> 0)
    phi_waste  : float — φ of the product at end-of-life (≥ 0, ≤ phi_origin)
    r          : float — supply-chain separation distance (≥ 0)
    kappa      : float — return coupling constant (> 0, default 1)
    xi         : float — correlation length of the origin φ-field (> 0, default 1)

    Returns
    -------
    F : float — return force (≥ 0; zero when phi_origin == phi_waste)

    Raises
    ------
    ValueError
        If phi_origin ≤ 0, phi_waste < 0, r < 0, kappa ≤ 0, or xi ≤ 0.
    """
    if phi_origin <= 0.0:
        raise ValueError(f"phi_origin must be > 0, got {phi_origin!r}")
    if phi_waste < 0.0:
        raise ValueError(f"phi_waste must be ≥ 0, got {phi_waste!r}")
    if r < 0.0:
        raise ValueError(f"r must be ≥ 0, got {r!r}")
    if kappa <= 0.0:
        raise ValueError(f"kappa must be > 0, got {kappa!r}")
    if xi <= 0.0:
        raise ValueError(f"xi must be > 0, got {xi!r}")
    delta_phi = max(phi_origin - phi_waste, 0.0)
    return float(kappa * delta_phi * np.exp(-r / xi))


# ---------------------------------------------------------------------------
# Legal enforcement — the φ-debt
# ---------------------------------------------------------------------------

def producer_phi_debt(
    phi_virgin: float,
    a_score: float,
) -> float:
    """Remaining φ-debt after a recovery with alignment score a_score.

    When a producer manufactures a product they incur a φ-debt equal to
    φ_virgin — the full entanglement-capacity of the virgin material.  If
    they subsequently recover the product at alignment score A_score (see
    `entropy_ledger.alignment_score`), the debt is partially discharged:

        D_remaining = φ_virgin · max(1 − A_score, 0)

    A perfect closed-loop recovery (A_score = 1) clears the debt entirely.
    Landfilling (A_score = 0) leaves it unpaid.

    Parameters
    ----------
    phi_virgin : float — φ of the virgin material at manufacture (> 0)
    a_score    : float — alignment score at recovery ∈ [0, 1]

    Returns
    -------
    D_remaining : float — remaining φ-debt (≥ 0)

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0 or a_score is outside [0, 1].
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if not (0.0 <= a_score <= 1.0):
        raise ValueError(f"a_score must be in [0, 1], got {a_score!r}")
    return float(phi_virgin * max(1.0 - a_score, 0.0))


def epr_levy(
    phi_virgin: float,
    phi_waste: float,
    c_levy: float = 1.0,
    k_B: float = 1.0,
) -> float:
    """Economic EPR levy derived from the entropy gap at end-of-life.

    Extended Producer Responsibility (EPR) converts the φ-entropy gap
    between the virgin product and its end-of-life state into a financial
    obligation.  The manifold entropy gap is:

        ΔS = k_B · ln(φ_virgin / φ_waste)

    Multiplying by a policy-set cost-per-entropy-unit c_levy gives the
    levy:

        L_epr = c_levy · k_B · ln(φ_virgin / φ_waste)

    This makes pure entropy laundering (mass-recovered but low φ) more
    expensive than genuine closed-loop recovery, because a high alignment
    score means φ_waste ≈ φ_virgin and ΔS → 0.  A producer who achieves
    A_score ≥ 0.95 pays a levy close to zero.

    Parameters
    ----------
    phi_virgin : float — φ of the virgin material (> 0)
    phi_waste  : float — φ of the material at end-of-life (> 0)
    c_levy     : float — cost per entropy unit (≥ 0, default 1)
    k_B        : float — Boltzmann constant (default 1, Planck units)

    Returns
    -------
    L : float — EPR levy (≥ 0)

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0, phi_waste ≤ 0, or c_levy < 0.
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_waste <= 0.0:
        raise ValueError(f"phi_waste must be > 0, got {phi_waste!r}")
    if c_levy < 0.0:
        raise ValueError(f"c_levy must be ≥ 0, got {c_levy!r}")
    ratio = phi_virgin / phi_waste
    if ratio < 1.0:
        ratio = 1.0  # recycled φ cannot exceed virgin; clamp
    return float(c_levy * k_B * np.log(ratio))


def deposit_refund_amount(
    phi_virgin: float,
    phi_waste: float,
    c_levy: float = 1.0,
    collection_efficiency: float = 1.0,
) -> float:
    """Equilibrium deposit that makes voluntary return the rational choice.

    The deposit must equal the full φ-return energy — the cost of closing
    the φ-loop from waste back to virgin — discounted by the probability
    of collection:

        δ_eq = c_levy · (φ_virgin − φ_waste) / η_collection

    When the deposit is set at δ_eq, a rational consumer will return the
    product (capturing the deposit) rather than discard it, because the
    return reward exactly equals the φ-entropy cost of disposal.  Setting
    δ < δ_eq under-incentivises return; setting δ > δ_eq over-collects
    revenue without improving return rates beyond η_collection.

    Parameters
    ----------
    phi_virgin          : float — φ of the virgin material (> 0)
    phi_waste           : float — φ at end-of-life (≥ 0)
    c_levy              : float — cost per unit φ (≥ 0, default 1)
    collection_efficiency : float — expected collection rate η ∈ (0, 1]

    Returns
    -------
    delta : float — equilibrium deposit amount (≥ 0)

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0, phi_waste < 0, c_levy < 0, or
        collection_efficiency not in (0, 1].
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_waste < 0.0:
        raise ValueError(f"phi_waste must be ≥ 0, got {phi_waste!r}")
    if c_levy < 0.0:
        raise ValueError(f"c_levy must be ≥ 0, got {c_levy!r}")
    if not (0.0 < collection_efficiency <= 1.0):
        raise ValueError(
            f"collection_efficiency must be in (0, 1], got {collection_efficiency!r}"
        )
    delta_phi = max(phi_virgin - phi_waste, 0.0)
    return float(c_levy * delta_phi / collection_efficiency)


# ---------------------------------------------------------------------------
# Geographic enforcement radius
# ---------------------------------------------------------------------------

def closed_loop_radius(
    phi_origin: float,
    phi_waste: float,
    kappa: float = 1.0,
    xi: float = 1.0,
    F_min: float = 1e-3,
) -> float:
    """Maximum supply-chain distance at which economical return is possible.

    The return force F_return(r) = κ·(φ_origin−φ_waste)·exp(−r/ξ) decays
    with separation distance.  The closed-loop enforcement radius is the
    distance at which the return force drops to the minimum economically
    actionable force F_min:

        r_max = ξ · ln(κ · (φ_origin − φ_waste) / F_min)

    Products distributed beyond r_max cannot be economically returned to
    the producer without subsidising the transport cost above the φ-return
    value.  The manifold prescription is to design supply chains with
    r ≤ r_max — a hard topological constraint on distribution.

    Returns −∞ (negative infinity as -1) if φ_origin ≤ φ_waste (no gradient,
    no return force), or if the force at r = 0 is already below F_min.

    Parameters
    ----------
    phi_origin : float — φ at the producer's origin (> 0)
    phi_waste  : float — φ at end-of-life (≥ 0)
    kappa      : float — return coupling constant (> 0, default 1)
    xi         : float — correlation length (> 0, default 1)
    F_min      : float — minimum actionable return force (> 0, default 1e-3)

    Returns
    -------
    r_max : float — maximum return radius (≥ 0), or -1.0 if no viable radius.

    Raises
    ------
    ValueError
        If phi_origin ≤ 0, phi_waste < 0, kappa ≤ 0, xi ≤ 0, or F_min ≤ 0.
    """
    if phi_origin <= 0.0:
        raise ValueError(f"phi_origin must be > 0, got {phi_origin!r}")
    if phi_waste < 0.0:
        raise ValueError(f"phi_waste must be ≥ 0, got {phi_waste!r}")
    if kappa <= 0.0:
        raise ValueError(f"kappa must be > 0, got {kappa!r}")
    if xi <= 0.0:
        raise ValueError(f"xi must be > 0, got {xi!r}")
    if F_min <= 0.0:
        raise ValueError(f"F_min must be > 0, got {F_min!r}")
    delta_phi = phi_origin - phi_waste
    if delta_phi <= 0.0:
        return -1.0
    F0 = kappa * delta_phi
    if F0 <= F_min:
        return -1.0
    return float(xi * np.log(F0 / F_min))


# ---------------------------------------------------------------------------
# Voluntary return probability
# ---------------------------------------------------------------------------

def return_probability(
    phi_debt: float,
    k_econ: float = 1.0,
) -> float:
    """Boltzmann-weighted probability of voluntary return given a φ-debt.

    Without any financial incentive (deposit or levy), voluntary return is
    governed by the effective economic temperature k_econ (analogous to
    k_B·T in the statistical-mechanical sense but capturing economic
    rationality and friction):

        P_return = exp(−D_remaining / k_econ)

    A large φ-debt with a small k_econ (rational, low-friction environment)
    makes voluntary return exponentially unlikely — the manifold prediction
    for why litter rates are high for low-value, high-φ-debt packaging.
    Introducing a deposit or levy effectively lowers k_econ, making the
    Boltzmann weight larger and voluntary return more probable.

    Parameters
    ----------
    phi_debt : float — remaining φ-debt (D_remaining ≥ 0)
    k_econ   : float — economic temperature scale (> 0, default 1)

    Returns
    -------
    P : float — return probability ∈ (0, 1]

    Raises
    ------
    ValueError
        If phi_debt < 0 or k_econ ≤ 0.
    """
    if phi_debt < 0.0:
        raise ValueError(f"phi_debt must be ≥ 0, got {phi_debt!r}")
    if k_econ <= 0.0:
        raise ValueError(f"k_econ must be > 0, got {k_econ!r}")
    return float(np.exp(-phi_debt / k_econ))


# ---------------------------------------------------------------------------
# Take-back efficiency
# ---------------------------------------------------------------------------

def takeback_efficiency(
    a_score: float,
    collection_rate: float,
) -> float:
    """Fraction of φ-debt cleared by a producer take-back programme.

    A take-back programme simultaneously achieves a physical-recovery
    quality (alignment score A_score, which measures how much of the φ is
    restored per collected unit) and a logistical collection rate R (the
    fraction of products actually retrieved).  The fraction of the total
    φ-debt cleared is:

        η_takeback = A_score · R_collection

    A programme with perfect logistics (R = 1) but only 50 % φ-alignment
    clears half the debt — it is not a closed-loop programme.

    Parameters
    ----------
    a_score         : float — alignment score per collected item ∈ [0, 1]
    collection_rate : float — fraction of products collected ∈ [0, 1]

    Returns
    -------
    eta : float — take-back efficiency ∈ [0, 1]

    Raises
    ------
    ValueError
        If a_score or collection_rate is outside [0, 1].
    """
    if not (0.0 <= a_score <= 1.0):
        raise ValueError(f"a_score must be in [0, 1], got {a_score!r}")
    if not (0.0 <= collection_rate <= 1.0):
        raise ValueError(f"collection_rate must be in [0, 1], got {collection_rate!r}")
    return float(a_score * collection_rate)


# ---------------------------------------------------------------------------
# Topological origin fingerprint
# ---------------------------------------------------------------------------

def phi_origin_label(
    phi_virgin: float,
    n_w: int,
    producer_seed: float,
    phi_max: float = 10.0,
) -> float:
    """Topological fingerprint that identifies the producer from the product.

    Every product manufactured at a specific facility inherits a
    φ-origin label Λ — a scalar derived from the product's virgin φ, its
    winding number N_w, and the producer's own φ-field seed.  The label
    is the modular reduction of their product onto [0, phi_max):

        Λ = (φ_virgin · N_w · producer_seed) mod φ_max

    This label is invariant across the product's lifecycle as long as the
    winding-number topology is intact (i.e., no chemical recycling has
    occurred).  It can in principle be measured spectroscopically or
    derived from molecular-weight fingerprinting.  Its decay with
    mechanical recycling cycles mirrors the φ decay model in polymers.py.

    Parameters
    ----------
    phi_virgin    : float — φ of the virgin material (> 0)
    n_w           : int   — polymer winding number (≥ 1)
    producer_seed : float — φ-field seed identifying the producer (> 0)
    phi_max       : float — range of the label space (> 0, default 10)

    Returns
    -------
    Lambda : float — origin label ∈ [0, phi_max)

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0, n_w < 1, producer_seed ≤ 0, or phi_max ≤ 0.
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    if producer_seed <= 0.0:
        raise ValueError(f"producer_seed must be > 0, got {producer_seed!r}")
    if phi_max <= 0.0:
        raise ValueError(f"phi_max must be > 0, got {phi_max!r}")
    return float((phi_virgin * n_w * producer_seed) % phi_max)


# ---------------------------------------------------------------------------
# Systemic benefit of EPR over municipal collection
# ---------------------------------------------------------------------------

def systemic_entropy_saved(
    n_products: float,
    phi_virgin: float,
    a_score_epr: float,
    a_score_municipal: float,
) -> float:
    """System-level φ-entropy benefit of EPR over municipal waste collection.

    Municipal waste collection typically achieves lower alignment scores
    than a well-designed EPR programme because mixed streams increase B_μ
    noise and reduce sorting discriminability.  The total entropy saved
    across a product cohort is:

        ΔS = N_products · φ_virgin · (A_epr − A_municipal)

    This is the manifold quantification of the societal benefit of
    mandating EPR.  When ΔS > 0 the EPR programme recovers more of the
    collectively-invested φ-debt than municipal collection.

    Parameters
    ----------
    n_products        : float — number of products in the cohort (≥ 0)
    phi_virgin        : float — φ of the virgin material (> 0)
    a_score_epr       : float — mean alignment score under EPR ∈ [0, 1]
    a_score_municipal : float — mean alignment score under municipal ∈ [0, 1]

    Returns
    -------
    delta_S : float — entropy saved (may be negative if EPR underperforms)

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0, n_products < 0, or either alignment score is
        outside [0, 1].
    """
    if n_products < 0.0:
        raise ValueError(f"n_products must be ≥ 0, got {n_products!r}")
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if not (0.0 <= a_score_epr <= 1.0):
        raise ValueError(f"a_score_epr must be in [0, 1], got {a_score_epr!r}")
    if not (0.0 <= a_score_municipal <= 1.0):
        raise ValueError(
            f"a_score_municipal must be in [0, 1], got {a_score_municipal!r}"
        )
    return float(n_products * phi_virgin * (a_score_epr - a_score_municipal))


# ---------------------------------------------------------------------------
# Lifecycle return incentive
# ---------------------------------------------------------------------------

def lifecycle_return_incentive(
    phi_trace: list[float],
    c_levy: float = 1.0,
) -> list[float]:
    """EPR levy incentive accumulated at each stage of the product lifecycle.

    Given the φ-trace of a product (one φ value per lifecycle stage, as
    returned by `entropy_ledger.lifecycle_phi_trace`), compute the levy
    triggered at each transition where φ decreases:

        I_i = c_levy · max(φ_{i-1} − φ_i, 0)   for i ≥ 1

    I_0 = 0 (manufacture creates the debt but does not trigger a levy yet).

    This vector makes explicit at which lifecycle stage the φ-entropy is
    being lost.  Stages with high I_i are the priority targets for design-
    for-disassembly or process improvement.

    Parameters
    ----------
    phi_trace : list of float — φ value at each lifecycle stage (all > 0)
    c_levy    : float — cost per unit φ-loss (≥ 0, default 1)

    Returns
    -------
    incentives : list of float — levy at each stage (length = len(phi_trace))

    Raises
    ------
    ValueError
        If phi_trace is empty, any φ is ≤ 0, or c_levy < 0.
    """
    if len(phi_trace) == 0:
        raise ValueError("phi_trace must be non-empty")
    if c_levy < 0.0:
        raise ValueError(f"c_levy must be ≥ 0, got {c_levy!r}")
    for i, phi in enumerate(phi_trace):
        if phi <= 0.0:
            raise ValueError(
                f"All φ values must be > 0; phi_trace[{i}] = {phi!r}"
            )
    incentives = [0.0]
    for i in range(1, len(phi_trace)):
        loss = max(phi_trace[i - 1] - phi_trace[i], 0.0)
        incentives.append(float(c_levy * loss))
    return incentives
