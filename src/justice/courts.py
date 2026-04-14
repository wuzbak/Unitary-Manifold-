# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/justice/courts.py
======================
Courts and Judicial Fairness — Pillar 18a: Judicial & Justice Systems (American Focus).

Theory
------
A just court system is a FTUM fixed point of social φ equilibrium.  Justice is
the minimum-entropy resolution of a social conflict, achieved when the decision
maximises information flow (φ) while minimising B_μ noise (bias, procedural
error, resource inequality).  A fair verdict is one that returns both parties
to their equilibrium φ basins.  Injustice equals a displaced φ that is not
restored, which acts as a persistent source of social entropy.

The FTUM operator U here acts on the social ψ-state of the parties in conflict.
The fixed-point condition U·ψ* = ψ* is satisfied only when every defendant has
equal access to high-φ representation and when the B_μ bias field vanishes.

American-Specific Bottlenecks
------------------------------
**Wealth disparity in access** — φ-coupling to legal representation ∝ income.
Rich clients occupy high-φ basins; poor clients remain trapped in low-φ wells.
The Gideon guarantee is systematically underfunded, leaving public defenders
carrying caseloads that preclude meaningful advocacy.

**Implicit bias** — B_μ noise field systematically shifts verdicts by race,
gender, and class.  Studies show Black defendants receive harsher outcomes
controlling for offence severity; women receive more lenient sentences —
both represent B_μ asymmetries in the verdict manifold.

**Prosecutorial discretion → charging disparity** — the same Δφ offence (same
objective harm) routinely attracts vastly different charges depending on the
defendant's demographics, jurisdiction, and the prosecutor's electoral calculus.

**Mandatory minimums** — fixed-point collapse: all sentencing trajectories
converge to a single attractor regardless of individual φ context.  The FTUM
landscape is artificially flattened, removing the judge's ability to find the
true minimum-entropy basin.

**Civil asset forfeiture** — the system extracts φ before conviction, a
pre-trial entropy robbery that destabilises the defendant's φ-basin prior to
any adjudication.  Innocent owners bear the full burden of reclaiming assets.

**Plea-bargain pressure** — 97 % of federal cases never reach trial.  The φ
landscape of factual innocence/guilt is never explored; defendants accept
sub-optimal fixed points under coercion to avoid trial-sentence risk premiums.

Actionable Suggestions
-----------------------
- **Public defender funding parity** — equalise λ_legal across income brackets
  so every defendant enters the same φ-basin regardless of wealth.
- **Blind charging protocols** — strip demographic metadata from initial
  charging decisions to reduce B_μ racial/class noise at the earliest stage.
- **Eliminate cash bail** — restore pre-trial φ-equilibrium; detention should
  reflect flight risk, not income.
- **Abolish mandatory minimums for non-violent offences** — restore judicial
  φ-discretion and allow the FTUM landscape to reach its true minimum.
- **Algorithmic-bias audits** — require regular demographic-parity audits of
  risk-assessment tools (COMPAS, PSA, etc.) to measure and correct B_μ drift.

Public API
----------
verdict_phi_shift(phi_defendant_pre, phi_defendant_post) -> float
    Delta φ experienced by defendant: phi_defendant_post − phi_defendant_pre.

representation_quality(income, income_median, lam_public, lam_private) -> float
    Effective representation coupling λ_eff blended by income relative to median.

bias_noise_floor(B_racial, B_gender, B_class) -> float
    Quadrature sum of bias components: sqrt(B_r² + B_g² + B_c²).

plea_pressure_index(trial_sentence, plea_sentence) -> float
    Normalised coercion index PPI ∈ [0, 1).

charging_disparity(phi_offense, sentence_a, sentence_b) -> float
    Absolute sentence difference normalised by offence φ.

mandatory_minimum_entropy(sentence_mandatory, sentence_just, n_cases) -> float
    Aggregate entropy injected by mandatory minimums across n_cases.

civil_asset_phi_loss(asset_value, conviction_probability) -> float
    Expected φ-loss from forfeiture weighted by P(innocent).

case_backlog_entropy(n_pending, n_resolved_per_year) -> float
    Normalised backlog pressure on the court system.

equal_protection_score(outcome_rates) -> float
    EPS ∈ [0, 1]: 1 = perfectly equal conviction rates across demographics.

bail_phi_impact(bail_amount, monthly_income) -> float
    Fractional φ-impact of bail on defendant, clipped to [0, 1].
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Verdict φ-shift
# ---------------------------------------------------------------------------

def verdict_phi_shift(
    phi_defendant_pre: float,
    phi_defendant_post: float,
) -> float:
    """Change in defendant's entanglement capacity caused by the verdict.

    A negative shift indicates that justice has been denied — the defendant
    exits the process with lower φ than the social equilibrium warrants.  A
    zero shift is the ideal fixed point; a positive shift may occur in
    exonerations or restorative outcomes.

    Parameters
    ----------
    phi_defendant_pre  : float — defendant φ before the verdict (must be > 0)
    phi_defendant_post : float — defendant φ after the verdict (must be ≥ 0)

    Returns
    -------
    delta_phi : float — phi_defendant_post − phi_defendant_pre

    Raises
    ------
    ValueError
        If phi_defendant_pre ≤ 0 or phi_defendant_post < 0.
    """
    if phi_defendant_pre <= 0.0:
        raise ValueError(f"phi_defendant_pre must be > 0, got {phi_defendant_pre!r}")
    if phi_defendant_post < 0.0:
        raise ValueError(f"phi_defendant_post must be ≥ 0, got {phi_defendant_post!r}")
    return float(phi_defendant_post - phi_defendant_pre)


# ---------------------------------------------------------------------------
# Representation quality
# ---------------------------------------------------------------------------

def representation_quality(
    income: float,
    income_median: float,
    lam_public: float,
    lam_private: float,
) -> float:
    """Effective representation coupling blended by income.

    Models the reality that wealthier defendants receive higher-φ legal
    representation.  The effective coupling interpolates between the public-
    defender floor (lam_public) and the private-attorney ceiling (lam_private)
    using a hyperbolic income model:

        λ_eff = λ_pub + (λ_priv − λ_pub) · income / (income + income_median)

    Parameters
    ----------
    income        : float — defendant's annual income (≥ 0)
    income_median : float — community median income (> 0)
    lam_public    : float — representation quality of public defender (≥ 0)
    lam_private   : float — representation quality of private counsel (≥ lam_public)

    Returns
    -------
    lambda_eff : float

    Raises
    ------
    ValueError
        If income < 0, income_median ≤ 0, lam_public < 0, or
        lam_private < lam_public.
    """
    if income < 0.0:
        raise ValueError(f"income must be ≥ 0, got {income!r}")
    if income_median <= 0.0:
        raise ValueError(f"income_median must be > 0, got {income_median!r}")
    if lam_public < 0.0:
        raise ValueError(f"lam_public must be ≥ 0, got {lam_public!r}")
    if lam_private < lam_public:
        raise ValueError("lam_private must be ≥ lam_public")
    fraction = income / (income + income_median)
    return float(lam_public + (lam_private - lam_public) * fraction)


# ---------------------------------------------------------------------------
# Bias noise floor
# ---------------------------------------------------------------------------

def bias_noise_floor(
    B_racial: float,
    B_gender: float,
    B_class: float,
) -> float:
    """Quadrature sum of independent bias components.

    Each bias dimension contributes an independent B_μ noise field.  The
    total effective noise is the Euclidean norm:

        B_total = sqrt(B_racial² + B_gender² + B_class²)

    Parameters
    ----------
    B_racial : float — racial bias magnitude (≥ 0)
    B_gender : float — gender bias magnitude (≥ 0)
    B_class  : float — class/wealth bias magnitude (≥ 0)

    Returns
    -------
    B_total : float

    Raises
    ------
    ValueError
        If any component is negative.
    """
    for name, val in (("B_racial", B_racial), ("B_gender", B_gender), ("B_class", B_class)):
        if val < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {val!r}")
    return float(np.sqrt(B_racial**2 + B_gender**2 + B_class**2))


# ---------------------------------------------------------------------------
# Plea-pressure index
# ---------------------------------------------------------------------------

def plea_pressure_index(
    trial_sentence: float,
    plea_sentence: float,
) -> float:
    """Normalised coercion pressure to accept a plea deal.

    Captures the "trial penalty" — the gap between the expected trial
    sentence and the offered plea.  A PPI near 1 means near-total coercion;
    0 means no penalty for exercising trial rights.

        PPI = (trial_sentence − plea_sentence) / (trial_sentence + ε)

    Result is clipped to [0, 1).

    Parameters
    ----------
    trial_sentence : float — expected sentence if convicted at trial (≥ 0)
    plea_sentence  : float — sentence offered via plea (≥ 0)

    Returns
    -------
    PPI : float ∈ [0, 1)

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if trial_sentence < 0.0:
        raise ValueError(f"trial_sentence must be ≥ 0, got {trial_sentence!r}")
    if plea_sentence < 0.0:
        raise ValueError(f"plea_sentence must be ≥ 0, got {plea_sentence!r}")
    raw = (trial_sentence - plea_sentence) / (trial_sentence + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0 - _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Charging disparity
# ---------------------------------------------------------------------------

def charging_disparity(
    phi_offense: float,
    sentence_a: float,
    sentence_b: float,
) -> float:
    """Charging disparity for the same offence φ across two defendants.

    Equal protection requires that the same offence (same Δφ harm to society)
    results in equivalent charges.  Departures signal B_μ noise:

        disparity = |sentence_a − sentence_b| / (phi_offense + ε)

    Parameters
    ----------
    phi_offense : float — objective φ-harm of the offence (≥ 0)
    sentence_a  : float — sentence for defendant A (≥ 0)
    sentence_b  : float — sentence for defendant B (≥ 0)

    Returns
    -------
    disparity : float ≥ 0

    Raises
    ------
    ValueError
        If phi_offense, sentence_a, or sentence_b is negative.
    """
    if phi_offense < 0.0:
        raise ValueError(f"phi_offense must be ≥ 0, got {phi_offense!r}")
    if sentence_a < 0.0:
        raise ValueError(f"sentence_a must be ≥ 0, got {sentence_a!r}")
    if sentence_b < 0.0:
        raise ValueError(f"sentence_b must be ≥ 0, got {sentence_b!r}")
    return float(abs(sentence_a - sentence_b) / (phi_offense + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Mandatory minimum entropy
# ---------------------------------------------------------------------------

def mandatory_minimum_entropy(
    sentence_mandatory: float,
    sentence_just: float,
    n_cases: int,
) -> float:
    """Aggregate entropy injected by mandatory minimum sentencing.

    When every case is forced to the same attractor regardless of individual
    φ context, the excess entropy per case scales as:

        S_mm = n_cases · (sentence_mandatory − sentence_just)² / (sentence_just² + ε)

    Parameters
    ----------
    sentence_mandatory : float — mandatory minimum sentence (months/years) (≥ 0)
    sentence_just      : float — individuated just sentence (≥ 0)
    n_cases            : int   — number of cases affected (≥ 0)

    Returns
    -------
    S_mm : float ≥ 0

    Raises
    ------
    ValueError
        If any argument is negative.
    """
    if sentence_mandatory < 0.0:
        raise ValueError(f"sentence_mandatory must be ≥ 0, got {sentence_mandatory!r}")
    if sentence_just < 0.0:
        raise ValueError(f"sentence_just must be ≥ 0, got {sentence_just!r}")
    if n_cases < 0:
        raise ValueError(f"n_cases must be ≥ 0, got {n_cases!r}")
    return float(
        n_cases * (sentence_mandatory - sentence_just) ** 2
        / (sentence_just**2 + _NUMERICAL_EPSILON)
    )


# ---------------------------------------------------------------------------
# Civil asset forfeiture φ-loss
# ---------------------------------------------------------------------------

def civil_asset_phi_loss(
    asset_value: float,
    conviction_probability: float,
) -> float:
    """Expected φ-loss from civil asset forfeiture prior to conviction.

    Forfeiture seizes assets before any finding of guilt; the expected unjust
    φ-drain on an innocent party is:

        expected_loss = asset_value · (1 − conviction_probability)

    Parameters
    ----------
    asset_value           : float — monetary value of seized assets (≥ 0)
    conviction_probability: float — P(eventual conviction) ∈ [0, 1]

    Returns
    -------
    expected_loss : float ≥ 0

    Raises
    ------
    ValueError
        If asset_value < 0 or conviction_probability ∉ [0, 1].
    """
    if asset_value < 0.0:
        raise ValueError(f"asset_value must be ≥ 0, got {asset_value!r}")
    if not 0.0 <= conviction_probability <= 1.0:
        raise ValueError(
            f"conviction_probability must be in [0, 1], got {conviction_probability!r}"
        )
    return float(asset_value * (1.0 - conviction_probability))


# ---------------------------------------------------------------------------
# Case backlog entropy
# ---------------------------------------------------------------------------

def case_backlog_entropy(
    n_pending: int,
    n_resolved_per_year: float,
) -> float:
    """Normalised backlog pressure on the court system.

    A high ratio signals that the φ-restoration pipeline is saturated.
    Justice delayed is justice denied — each unit of backlog represents a
    φ-displaced party whose equilibrium is not being restored:

        entropy = n_pending / (n_resolved_per_year + ε)

    Parameters
    ----------
    n_pending           : int   — cases awaiting resolution (≥ 0)
    n_resolved_per_year : float — cases resolved annually (≥ 0)

    Returns
    -------
    entropy : float ≥ 0

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if n_pending < 0:
        raise ValueError(f"n_pending must be ≥ 0, got {n_pending!r}")
    if n_resolved_per_year < 0.0:
        raise ValueError(f"n_resolved_per_year must be ≥ 0, got {n_resolved_per_year!r}")
    return float(n_pending / (n_resolved_per_year + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Equal protection score
# ---------------------------------------------------------------------------

def equal_protection_score(outcome_rates: np.ndarray) -> float:
    """Demographic parity score for conviction rates across groups.

    Measures how uniformly the court system applies convictions across
    demographic groups.  A score of 1 indicates perfect equal protection;
    lower values reflect systematic B_μ disparity:

        EPS = 1 − std(outcome_rates) / (mean(outcome_rates) + ε)

    Result is clipped to [0, 1].

    Parameters
    ----------
    outcome_rates : array-like — conviction rates per demographic group,
                    each ∈ [0, 1].  Must have at least 2 elements.

    Returns
    -------
    EPS : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If outcome_rates has fewer than 2 elements or any rate ∉ [0, 1].
    """
    rates = np.asarray(outcome_rates, dtype=float)
    if rates.ndim != 1 or rates.size < 2:
        raise ValueError("outcome_rates must be a 1-D array with at least 2 elements")
    if np.any(rates < 0.0) or np.any(rates > 1.0):
        raise ValueError("all outcome_rates must be in [0, 1]")
    eps_raw = 1.0 - float(np.std(rates)) / (float(np.mean(rates)) + _NUMERICAL_EPSILON)
    return float(np.clip(eps_raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Bail φ-impact
# ---------------------------------------------------------------------------

def bail_phi_impact(
    bail_amount: float,
    monthly_income: float,
) -> float:
    """Fractional φ-impact of cash bail relative to monthly income.

    Cash bail constitutes a φ-displacement proportional to how many months
    of income must be surrendered.  The metric is normalised and clipped:

        impact = min(bail_amount / (monthly_income + ε), 1.0)

    Parameters
    ----------
    bail_amount    : float — bail set by court (≥ 0)
    monthly_income : float — defendant's monthly income (≥ 0)

    Returns
    -------
    impact : float ∈ [0, 1]

    Raises
    ------
    ValueError
        If bail_amount < 0 or monthly_income < 0.
    """
    if bail_amount < 0.0:
        raise ValueError(f"bail_amount must be ≥ 0, got {bail_amount!r}")
    if monthly_income < 0.0:
        raise ValueError(f"monthly_income must be ≥ 0, got {monthly_income!r}")
    raw = bail_amount / (monthly_income + _NUMERICAL_EPSILON)
    return float(min(raw, 1.0))
