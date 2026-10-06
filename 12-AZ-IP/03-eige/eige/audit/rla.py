# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Risk-limiting audits (RLAs) for plurality / vote-for-k contests.

Structure follows SHANGRLA (Stark 2020): each reported outcome is reduced to
*assertions* — one per (reported winner, reported loser) pair — whose
assorter mean must exceed 1/2.  Two standard statistical tests are provided:

* **Ballot-polling** — BRAVO (Lindeman, Stark & Yates 2012), a Wald sequential
  probability ratio test per assertion.
* **Ballot-level comparison** — the Kaplan–Markov bound used in "super-simple"
  audits (Stark 2010) with error-inflation factor γ, as deployed in Colorado.

Risk is measured as ``min(1, 1/max_t T_t)`` per assertion (Ville's
inequality); the audit can stop only when every assertion's risk is at or
below the risk limit.  Otherwise the audit must escalate, ultimately to a
full hand count, which then determines the outcome.

This module does not import the SHANGRLA reference package; its ``Assertion``
objects map one-to-one onto SHANGRLA plurality assorters, so results can be
cross-checked with that package or with Arlo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from ..model.election import Contest, ContestOutcome

DEFAULT_GAMMA = 1.03905


class AuditError(ValueError):
    """Raised for audit inputs that cannot be audited."""


@dataclass(frozen=True)
class Assertion:
    """``winner`` beat ``loser``: assorter (1 + v_w − v_l)/2 has mean > 1/2."""

    contest_id: str
    winner: str
    loser: str
    winner_votes: int
    loser_votes: int
    ballots: int

    @property
    def margin_votes(self) -> int:
        return self.winner_votes - self.loser_votes

    @property
    def diluted_margin(self) -> float:
        return self.margin_votes / self.ballots if self.ballots else 0.0

    def assorter(self, votes: Sequence[str]) -> float:
        return (1 + (self.winner in votes) - (self.loser in votes)) / 2


def plurality_assertions(contest: Contest, reported: Mapping[str, int], ballots: int) -> List[Assertion]:
    """Assertions implied by reported totals (winners = top ``vote_for``)."""
    unknown = set(reported) - set(contest.candidate_ids)
    if unknown:
        raise AuditError(f"reported totals include unknown candidates {sorted(unknown)}")
    if ballots < 1:
        raise AuditError("ballot universe must be positive")
    ranked = sorted(contest.candidate_ids, key=lambda c: (-int(reported.get(c, 0)), c))
    winners, losers = ranked[: contest.vote_for], ranked[contest.vote_for:]
    out = []
    for w in winners:
        for l in losers:
            out.append(Assertion(contest.id, w, l, int(reported.get(w, 0)), int(reported.get(l, 0)), ballots))
    if any(a.margin_votes <= 0 for a in out):
        raise AuditError("reported outcome has a tie or non-positive margin; a full hand count is required")
    return out


def _votes(outcome: Optional[ContestOutcome]) -> Tuple[str, ...]:
    """Votes counted on a ballot (overvotes and absent contest count as none)."""
    if outcome is None or outcome.overvoted:
        return ()
    return outcome.votes


@dataclass
class AssertionRisk:
    assertion: Assertion
    risk: float

    def as_dict(self) -> dict:
        a = self.assertion
        return {"winner": a.winner, "loser": a.loser, "diluted_margin": round(a.diluted_margin, 6), "risk": self.risk}


@dataclass
class AuditResult:
    method: str
    contest_id: str
    risk_limit: float
    sample_size: int
    assertions: List[AssertionRisk]
    discrepancies: Dict[str, int] = field(default_factory=dict)

    @property
    def max_risk(self) -> float:
        return max(a.risk for a in self.assertions)

    @property
    def confirmed(self) -> bool:
        return self.max_risk <= self.risk_limit

    def as_dict(self) -> dict:
        return {
            "format": "eige.rla_result.v1",
            "method": self.method,
            "contest_id": self.contest_id,
            "risk_limit": self.risk_limit,
            "sample_size": self.sample_size,
            "max_risk": self.max_risk,
            "outcome_confirmed": self.confirmed,
            "next_step": "stop: reported outcome confirmed at the risk limit" if self.confirmed
            else "escalate: draw more ballots (continue the same seeded sequence) or hand count all ballots",
            "assertions": [a.as_dict() for a in self.assertions],
            "discrepancies": dict(self.discrepancies),
        }


def _check_risk_limit(risk_limit: float) -> None:
    if not 0 < risk_limit < 1:
        raise AuditError("risk limit must be in (0, 1)")


# --------------------------------------------------------------------------- BRAVO

def bravo_audit(
    contest: Contest,
    reported: Mapping[str, int],
    ballots: int,
    sample: Sequence[Optional[ContestOutcome]],
    risk_limit: float,
) -> AuditResult:
    """Ballot-polling audit.  ``sample`` holds the hand interpretation of each sampled ballot."""
    _check_risk_limit(risk_limit)
    risks = []
    for a in plurality_assertions(contest, reported, ballots):
        s = a.winner_votes / (a.winner_votes + a.loser_votes)
        t, t_max = 1.0, 1.0
        for outcome in sample:
            v = _votes(outcome)
            if a.winner in v and a.loser not in v:
                t *= 2 * s
            elif a.loser in v and a.winner not in v:
                t *= 2 * (1 - s)
            t_max = max(t_max, t)
        risks.append(AssertionRisk(a, min(1.0, 1.0 / t_max)))
    return AuditResult("ballot-polling/BRAVO", contest.id, risk_limit, len(sample), risks)


def bravo_sample_size(contest: Contest, reported: Mapping[str, int], ballots: int, risk_limit: float) -> int:
    """Expected sample size if the reported results are exactly right (ASN approximation)."""
    _check_risk_limit(risk_limit)
    worst = 0
    for a in plurality_assertions(contest, reported, ballots):
        pw, pl = a.winner_votes / ballots, a.loser_votes / ballots
        s = a.winner_votes / (a.winner_votes + a.loser_votes)
        drift = pw * math.log(2 * s) + pl * math.log(2 * (1 - s))
        if drift <= 0:  # pragma: no cover - only for non-positive margins, rejected above
            return ballots
        worst = max(worst, math.ceil(math.log(1 / risk_limit) / drift))
    return min(worst, ballots)


# --------------------------------------------------------------- Kaplan–Markov

def overstatement(assertions: Sequence[Assertion], cvr: Optional[ContestOutcome], mvr: Optional[ContestOutcome]) -> int:
    """Largest pairwise margin overstatement on one ballot, in votes (−2 … 2)."""
    cv, mv = _votes(cvr), _votes(mvr)
    worst = -3
    for a in assertions:
        o = ((a.winner in cv) - (a.loser in cv)) - ((a.winner in mv) - (a.loser in mv))
        worst = max(worst, o)
    return worst


def _km_log_terms(gamma: float, o1: int, o2: int, u1: int, u2: int) -> float:
    return (
        o1 * math.log(1 - 1 / (2 * gamma))
        + o2 * math.log(1 - 1 / gamma)
        + u1 * math.log(1 + 1 / (2 * gamma))
        + u2 * math.log(1 + 1 / gamma)
    )


def comparison_audit(
    contest: Contest,
    reported: Mapping[str, int],
    ballots: int,
    pairs: Sequence[Tuple[Optional[ContestOutcome], Optional[ContestOutcome]]],
    risk_limit: float,
    gamma: float = DEFAULT_GAMMA,
) -> AuditResult:
    """Ballot-level comparison audit; ``pairs`` are (CVR outcome, hand/MVR outcome) per sampled ballot."""
    _check_risk_limit(risk_limit)
    if gamma <= 1:
        raise AuditError("gamma must exceed 1")
    assertions = plurality_assertions(contest, reported, ballots)
    mu = min(a.diluted_margin for a in assertions)
    counts = {"o1": 0, "o2": 0, "u1": 0, "u2": 0}
    for cvr, mvr in pairs:
        e = overstatement(assertions, cvr, mvr)
        if e == 1:
            counts["o1"] += 1
        elif e == 2:
            counts["o2"] += 1
        elif e == -1:
            counts["u1"] += 1
        elif e == -2:
            counts["u2"] += 1
    n = len(pairs)
    log_p = n * math.log(1 - mu / (2 * gamma)) - _km_log_terms(gamma, **counts)
    risk = min(1.0, math.exp(log_p))
    return AuditResult(
        "ballot-comparison/Kaplan-Markov",
        contest.id,
        risk_limit,
        n,
        [AssertionRisk(a, risk) for a in assertions],
        counts,
    )


def comparison_sample_size(
    contest: Contest,
    reported: Mapping[str, int],
    ballots: int,
    risk_limit: float,
    gamma: float = DEFAULT_GAMMA,
    o1: int = 0,
    o2: int = 0,
    u1: int = 0,
    u2: int = 0,
) -> int:
    """Sample size at which the Kaplan–Markov risk reaches the limit, given assumed discrepancy counts."""
    _check_risk_limit(risk_limit)
    mu = min(a.diluted_margin for a in plurality_assertions(contest, reported, ballots))
    numerator = math.log(risk_limit) + _km_log_terms(gamma, o1, o2, u1, u2)
    n = math.ceil(numerator / math.log(1 - mu / (2 * gamma)))
    return min(max(n, o1 + o2 + u1 + u2), ballots)
