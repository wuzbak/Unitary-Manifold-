# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/governance/democracy.py
============================
Democracy as the Maximum-φ Governance Attractor — Pillar 19b.

Theory
------
In the space of all possible governance configurations, democracy maximises the
information-current density: every citizen is a φ-source, and their φ flows
into the collective decision field.  The vote is a φ-measurement: it collapses
the superposition of preferences to a single policy state.

The democratic attractor is thermodynamically MORE STABLE than the
authoritarian attractor because distributed fixed points are more resilient to
perturbation than single-point attractors.  When one distributed node fails,
the remaining N − 1 nodes continue to provide error-correcting information
current.  In a single-fixed-point authoritarian system a shift in the ruler's
preferences propagates unchecked, with no error-correction mechanism.

Democracy vs. Authoritarianism in FTUM language
------------------------------------------------
Democracy
    N-body φ field where all N sources contribute → maximum entropy of
    preference diversity → minimum decision-making noise → maximum legitimacy.
    The Condorcet jury theorem formalises this: P_correct increases with N
    and the error rate scales as 1/√N.

Authoritarianism
    Single-attractor collapse: all φ is forced into one basin controlled by
    one agent (or small coalition).  Low diversity, high fragility.  When the
    attractor's fixed point shifts (death of leader, economic shock), there is
    no distributed error-correction mechanism and the system may undergo
    catastrophic collapse or violent bifurcation.

Why democracy is better — the FTUM argument
--------------------------------------------
From the perspective of the Unitary Manifold, the Universe evolves toward
maximum φ diversity (the UEUM operator maximises information content subject
to conservation laws).  A governance system that harnesses N independent φ
sources is closer to the universal attractor than one that suppresses N − 1
of them.  Democracy is not merely politically preferable; it is the
governance form most aligned with the underlying physics of complex
information-processing systems.

Failure modes of democracy
---------------------------
1. Misinformation: B_μ noise field that scrambles the φ-to-vote mapping,
   causing citizens to act against their actual preferences.

2. Money in politics: wealth buys B_μ amplification of certain φ signals
   over others, breaking the "one citizen, one φ-source" symmetry.

3. Voter suppression: artificially reduces the effective N, degrading the
   Condorcet advantage and increasing the error rate ∝ 1/√N_eff.

4. Gerrymandering: rewires the φ-to-representation mapping so that vote share
   no longer linearly translates to seat share, breaking the measurement
   relationship.

5. Polarisation: bifurcates the φ-basin into two competing attractors.
   Neither can win outright → gridlock → policy stagnation → erosion of
   citizen confidence in the system.

Actionable best practices
--------------------------
- Campaign finance reform: reduce the B_μ-wealth coupling so that each
  citizen's φ is amplified equally.
- Ranked-choice voting: allows voters to express more of the φ-landscape
  per ballot, recovering information lost in first-past-the-post systems.
- Automatic voter registration: maximise N → minimise Condorcet error rate.
- Nonpartisan redistricting commissions: restore φ-to-representation linearity
  by removing partisan manipulation of district boundaries.
- Media literacy and fact-checking infrastructure: reduce B_μ misinformation
  noise floor, preserving the integrity of the φ-to-vote mapping.

Public API
----------
condorcet_phi(n_voters, individual_accuracy) -> float
    P_correct = 0.5 + 0.5 * erf((individual_accuracy - 0.5) * sqrt(n_voters))
    Uses math.erf from the Python standard library.

voter_phi_density(n_registered, n_eligible) -> float
    density = n_registered / (n_eligible + 1e-30)  clipped [0, 1].

democratic_legitimacy(voter_turnout, margin_of_victory, phi_press_freedom) -> float
    legitimacy = voter_turnout * (1 - abs(margin_of_victory - 0.5)) * phi_press_freedom.

authoritarian_fragility(concentration_index, n_institutions) -> float
    fragility = concentration_index / (n_institutions + 1e-30).

misinformation_phi_noise(B_misinformation, n_exposed, correction_factor) -> float
    B_net = B_misinformation * n_exposed * (1 - correction_factor).

gerrymandering_index(votes_fraction, seats_fraction) -> float
    GI = abs(seats_fraction - votes_fraction).

polarisation_index(phi_left, phi_right) -> float
    PI = abs(phi_left - phi_right) / (phi_left + phi_right + 1e-30).

campaign_finance_distortion(B_money, phi_message) -> float
    distortion = B_money / (phi_message + 1e-30).

ranked_choice_phi_gain(n_candidates, n_rounds_eliminated) -> float
    gain = 1 - exp(-n_rounds_eliminated / (n_candidates + 1e-30)).

press_freedom_phi(n_independent_outlets, B_censorship) -> float
    phi_press = n_independent_outlets * exp(-B_censorship).
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Condorcet theorem and voter density
# ---------------------------------------------------------------------------

def condorcet_phi(
    n_voters: int | float,
    individual_accuracy: float,
) -> float:
    """Probability that a democratic majority reaches the correct decision.

    The Condorcet jury theorem states that if each voter independently has
    accuracy p > 0.5, the probability of a majority-correct outcome increases
    with N and approaches 1.  In FTUM language, each voter is a φ-source; N
    sources collectively reduce the decision noise by √N.

        P_correct = 0.5 + 0.5 × erf((p − 0.5) × √N)

    Uses ``math.erf`` from the Python standard library.

    Parameters
    ----------
    n_voters            : int or float — number of voters (must be > 0).
    individual_accuracy : float — per-voter accuracy p ∈ (0, 1).

    Returns
    -------
    P_correct : float — probability of correct collective decision ∈ [0, 1].

    Raises
    ------
    ValueError
        If n_voters <= 0 or individual_accuracy is outside (0, 1).
    """
    if n_voters <= 0:
        raise ValueError(f"n_voters must be > 0, got {n_voters!r}")
    if not (0.0 < individual_accuracy < 1.0):
        raise ValueError(
            f"individual_accuracy must be in (0, 1), got {individual_accuracy!r}"
        )
    argument = (individual_accuracy - 0.5) * math.sqrt(float(n_voters))
    return float(0.5 + 0.5 * math.erf(argument))


def voter_phi_density(
    n_registered: float,
    n_eligible: float,
) -> float:
    """Fraction of eligible citizens registered to vote, clipped to [0, 1].

    The voter φ-density measures how completely the φ-source capacity of the
    eligible population is activated.  Voter suppression, registration
    barriers, and disenfranchisement all reduce this density, degrading the
    Condorcet advantage.

        density = n_registered / (n_eligible + ε),  clipped to [0, 1]

    Parameters
    ----------
    n_registered : float — number of registered voters (≥ 0).
    n_eligible   : float — number of eligible citizens (≥ 0).

    Returns
    -------
    density : float — voter φ-density ∈ [0, 1].

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if n_registered < 0.0:
        raise ValueError(f"n_registered must be >= 0, got {n_registered!r}")
    if n_eligible < 0.0:
        raise ValueError(f"n_eligible must be >= 0, got {n_eligible!r}")
    raw = n_registered / (n_eligible + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Legitimacy and fragility
# ---------------------------------------------------------------------------

def democratic_legitimacy(
    voter_turnout: float,
    margin_of_victory: float,
    phi_press_freedom: float,
) -> float:
    """Composite legitimacy of a democratic outcome.

    Three factors jointly determine legitimacy:
    1. Voter turnout — the fraction of citizens who participated (breadth of
       the φ-measurement).
    2. Margin of victory relative to 50% — competitive elections (margin ≈ 0.5)
       signal genuine φ-diversity; landslides may indicate preference cascade
       or suppression.  The factor (1 − |margin − 0.5|) is maximised at
       margin = 0.5 (perfect competition) and equals 0.5 at margins 0 or 1.
    3. Press freedom φ — free media ensures the φ-to-vote mapping is not
       corrupted by information asymmetries.

        legitimacy = turnout × (1 − |margin − 0.5|) × φ_press_freedom

    Parameters
    ----------
    voter_turnout     : float — fraction of eligible voters who voted ∈ [0, 1].
    margin_of_victory : float — winner's vote share ∈ [0, 1].
    phi_press_freedom : float — press-freedom φ (≥ 0; typically ∈ [0, 1]).

    Returns
    -------
    legitimacy : float — composite legitimacy score (≥ 0).

    Raises
    ------
    ValueError
        If voter_turnout or margin_of_victory is outside [0, 1], or
        phi_press_freedom is negative.
    """
    if not (0.0 <= voter_turnout <= 1.0):
        raise ValueError(f"voter_turnout must be in [0, 1], got {voter_turnout!r}")
    if not (0.0 <= margin_of_victory <= 1.0):
        raise ValueError(
            f"margin_of_victory must be in [0, 1], got {margin_of_victory!r}"
        )
    if phi_press_freedom < 0.0:
        raise ValueError(
            f"phi_press_freedom must be >= 0, got {phi_press_freedom!r}"
        )
    return float(
        voter_turnout * (1.0 - abs(margin_of_victory - 0.5)) * phi_press_freedom
    )


def authoritarian_fragility(
    concentration_index: float,
    n_institutions: float,
) -> float:
    """Fragility of an authoritarian regime.

    An authoritarian system concentrates φ in a single attractor basin.  The
    more concentrated the power (higher concentration_index) and the fewer
    independent institutions providing error-correction (lower n_institutions),
    the more fragile the regime:

        fragility = concentration_index / (n_institutions + ε)

    Parameters
    ----------
    concentration_index : float — power concentration metric (≥ 0).
    n_institutions      : float — number of independent institutions (≥ 0).

    Returns
    -------
    fragility : float — regime fragility (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if concentration_index < 0.0:
        raise ValueError(
            f"concentration_index must be >= 0, got {concentration_index!r}"
        )
    if n_institutions < 0.0:
        raise ValueError(f"n_institutions must be >= 0, got {n_institutions!r}")
    return float(concentration_index / (n_institutions + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Misinformation and election integrity
# ---------------------------------------------------------------------------

def misinformation_phi_noise(
    B_misinformation: float,
    n_exposed: float,
    correction_factor: float,
) -> float:
    """Net B_μ noise injected into the φ-decision field by misinformation.

    Misinformation is a B_μ noise field.  Fact-checking and media literacy
    provide a correction that partially cancels the noise.  The net noise is:

        B_net = B_misinformation × n_exposed × (1 − correction_factor)

    Parameters
    ----------
    B_misinformation : float — misinformation field strength (≥ 0).
    n_exposed        : float — number of citizens exposed (≥ 0).
    correction_factor: float — fraction of misinformation corrected (clipped
                       to [0, 1]).

    Returns
    -------
    B_net : float — net noise injected into the decision field (≥ 0).

    Raises
    ------
    ValueError
        If B_misinformation or n_exposed is negative.
    """
    if B_misinformation < 0.0:
        raise ValueError(
            f"B_misinformation must be >= 0, got {B_misinformation!r}"
        )
    if n_exposed < 0.0:
        raise ValueError(f"n_exposed must be >= 0, got {n_exposed!r}")
    cf = float(np.clip(correction_factor, 0.0, 1.0))
    return float(B_misinformation * n_exposed * (1.0 - cf))


def gerrymandering_index(
    votes_fraction: float,
    seats_fraction: float,
) -> float:
    """Distortion between vote share and seat share introduced by gerrymandering.

    In a fair electoral system, a party receiving a fraction v of votes should
    receive approximately v of seats.  Gerrymandering breaks this linearity:

        GI = |seats_fraction − votes_fraction|

    GI = 0 means proportional representation; GI → 0.5 indicates severe
    gerrymandering.

    Parameters
    ----------
    votes_fraction : float — fraction of votes received ∈ [0, 1].
    seats_fraction : float — fraction of seats won ∈ [0, 1].

    Returns
    -------
    GI : float — gerrymandering index ∈ [0, 1].

    Raises
    ------
    ValueError
        If either fraction is outside [0, 1].
    """
    if not (0.0 <= votes_fraction <= 1.0):
        raise ValueError(f"votes_fraction must be in [0, 1], got {votes_fraction!r}")
    if not (0.0 <= seats_fraction <= 1.0):
        raise ValueError(f"seats_fraction must be in [0, 1], got {seats_fraction!r}")
    return float(abs(seats_fraction - votes_fraction))


def polarisation_index(
    phi_left: float,
    phi_right: float,
) -> float:
    """Normalised φ-distance between two political poles.

    Polarisation occurs when the preference φ-basin bifurcates into two
    competing attractors.  The index measures the normalised separation:

        PI = |φ_left − φ_right| / (φ_left + φ_right + ε)

    PI = 0 means perfect consensus; PI → 1 means one pole has vanished.

    Parameters
    ----------
    phi_left  : float — φ field strength of the left-leaning attractor (≥ 0).
    phi_right : float — φ field strength of the right-leaning attractor (≥ 0).

    Returns
    -------
    PI : float — polarisation index ∈ [0, 1).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_left < 0.0:
        raise ValueError(f"phi_left must be >= 0, got {phi_left!r}")
    if phi_right < 0.0:
        raise ValueError(f"phi_right must be >= 0, got {phi_right!r}")
    return float(abs(phi_left - phi_right) / (phi_left + phi_right + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Campaign finance and ranked-choice voting
# ---------------------------------------------------------------------------

def campaign_finance_distortion(
    B_money: float,
    phi_message: float,
) -> float:
    """Distortion of the information field by money in politics.

    Wealth buys B_μ amplification of certain φ signals at the expense of
    others.  The distortion is the ratio of the money-field strength to the
    underlying message φ:

        distortion = B_money / (φ_message + ε)

    A high distortion means the financial signal drowns out the policy signal.

    Parameters
    ----------
    B_money     : float — financial B_μ field amplitude (≥ 0).
    phi_message : float — substantive message φ (≥ 0).

    Returns
    -------
    distortion : float — campaign finance distortion ratio (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if B_money < 0.0:
        raise ValueError(f"B_money must be >= 0, got {B_money!r}")
    if phi_message < 0.0:
        raise ValueError(f"phi_message must be >= 0, got {phi_message!r}")
    return float(B_money / (phi_message + _NUMERICAL_EPSILON))


def ranked_choice_phi_gain(
    n_candidates: int | float,
    n_rounds_eliminated: int | float,
) -> float:
    """Fractional φ-information gain from ranked-choice voting.

    Ranked-choice voting (RCV) allows each voter to reveal more of their
    φ-landscape.  As candidates are eliminated round by round, preference
    information from voters whose first choice was eliminated is recovered.
    The saturation model gives:

        gain = 1 − exp(−n_rounds_eliminated / (n_candidates + ε))

    gain → 0 when no rounds occur (first-past-the-post); gain → 1 as
    n_rounds_eliminated → n_candidates (full preference revelation).

    Parameters
    ----------
    n_candidates        : int or float — total number of candidates (> 0).
    n_rounds_eliminated : int or float — number of elimination rounds (≥ 0).

    Returns
    -------
    gain : float — φ information gain ∈ [0, 1).

    Raises
    ------
    ValueError
        If n_candidates <= 0 or n_rounds_eliminated < 0.
    """
    if n_candidates <= 0:
        raise ValueError(f"n_candidates must be > 0, got {n_candidates!r}")
    if n_rounds_eliminated < 0:
        raise ValueError(
            f"n_rounds_eliminated must be >= 0, got {n_rounds_eliminated!r}"
        )
    return float(
        1.0 - np.exp(-float(n_rounds_eliminated) / (float(n_candidates) + _NUMERICAL_EPSILON))
    )


def press_freedom_phi(
    n_independent_outlets: float,
    B_censorship: float,
) -> float:
    """Effective press freedom φ after censorship suppression.

    A free press acts as a distributed sensor network of φ-measurement nodes.
    Each independent outlet contributes φ to the public information field.
    Censorship applies an exponential suppression to the total:

        φ_press = n_independent_outlets × exp(−B_censorship)

    Parameters
    ----------
    n_independent_outlets : float — number of independent media outlets (≥ 0).
    B_censorship          : float — censorship B_μ field strength (≥ 0).

    Returns
    -------
    phi_press : float — effective press-freedom φ (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if n_independent_outlets < 0.0:
        raise ValueError(
            f"n_independent_outlets must be >= 0, got {n_independent_outlets!r}"
        )
    if B_censorship < 0.0:
        raise ValueError(f"B_censorship must be >= 0, got {B_censorship!r}")
    return float(n_independent_outlets * np.exp(-B_censorship))
