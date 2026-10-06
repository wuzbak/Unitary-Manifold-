# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Canvass reconciliation: cast vs. counted vs. manifest, contest accounting, provisionals.

Every discrepancy carries a machine code, a severity (``blocking`` must be
resolved or explained before certification; ``review`` should be explained in
the canvass record), the scope it applies to and a plain-language reason.
Discrepancies are prompts for explanation — most have mundane causes
(mis-keyed batch sheets, ballots set aside for duplication) — not findings of
wrongdoing.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

from ..model.election import BallotManifest, CVR, Election, tally

BLOCKING = "blocking"
REVIEW = "review"


@dataclass(frozen=True)
class Discrepancy:
    code: str
    severity: str
    scope: str
    reason: str
    expected: Optional[int] = None
    observed: Optional[int] = None

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(frozen=True)
class ProvisionalAccount:
    issued: int
    accepted: int
    rejected: int
    pending: int
    accepted_counted: int


def reconcile(
    election: Election,
    manifest: BallotManifest,
    cvrs: Sequence[CVR],
    cast_by_batch: Optional[Mapping[str, int]] = None,
    reported: Optional[Mapping[str, Mapping[str, int]]] = None,
    provisional: Optional[ProvisionalAccount] = None,
) -> List[Discrepancy]:
    out: List[Discrepancy] = []

    ids = Counter(c.id for c in cvrs)
    for cvr_id, n in sorted(ids.items()):
        if n > 1:
            out.append(Discrepancy("DUPLICATE_CVR_ID", BLOCKING, f"cvr {cvr_id}", f"CVR id appears {n} times", 1, n))

    counted = Counter(c.batch_id for c in cvrs)
    manifest_ids = {b.batch_id for b in manifest.batches}
    for batch_id in sorted(set(counted) - manifest_ids):
        out.append(Discrepancy("BATCH_NOT_IN_MANIFEST", BLOCKING, f"batch {batch_id}",
                               "CVRs reference a batch that is not in the ballot manifest", 0, counted[batch_id]))
    for b in manifest.batches:
        n = counted.get(b.batch_id, 0)
        if n != b.ballot_count:
            out.append(Discrepancy(
                "MANIFEST_COUNTED_MISMATCH", BLOCKING, f"batch {b.batch_id}",
                "number of CVRs differs from the ballot count recorded in the manifest "
                "(check for unscanned, rescanned or duplicated ballots)", b.ballot_count, n))
        if cast_by_batch is not None:
            cast = cast_by_batch.get(b.batch_id)
            if cast is None:
                out.append(Discrepancy("CAST_COUNT_MISSING", REVIEW, f"batch {b.batch_id}",
                                       "no cast (check-in/pollbook) count supplied for this batch"))
            elif cast != n:
                out.append(Discrepancy("CAST_COUNTED_MISMATCH", BLOCKING, f"batch {b.batch_id}",
                                       "ballots cast per pollbook differ from ballots counted", cast, n))

    totals = tally(election, cvrs)
    for contest_id, t in totals.items():
        if not t.balances():
            out.append(Discrepancy("VOTE_OPPORTUNITY_IMBALANCE", BLOCKING, f"contest {contest_id}",
                                   "votes + overvotes·vote_for + undervotes does not equal ballots·vote_for"))
        if reported is not None:
            rep = reported.get(contest_id)
            if rep is None:
                out.append(Discrepancy("REPORTED_CONTEST_MISSING", BLOCKING, f"contest {contest_id}",
                                       "contest missing from reported results"))
                continue
            for cand, votes in sorted(t.candidate_votes.items()):
                if int(rep.get(cand, 0)) != votes:
                    out.append(Discrepancy("REPORTED_TOTAL_MISMATCH", BLOCKING, f"contest {contest_id} / {cand}",
                                           "reported total differs from the total recomputed from CVRs",
                                           votes, int(rep.get(cand, 0))))
            for cand in sorted(set(rep) - set(t.candidate_votes)):
                out.append(Discrepancy("REPORTED_UNKNOWN_CANDIDATE", BLOCKING, f"contest {contest_id} / {cand}",
                                       "reported results include a candidate not defined for this contest"))
        if t.ballots and t.overvoted_ballots / t.ballots > 0.01:
            out.append(Discrepancy("HIGH_OVERVOTE_RATE", REVIEW, f"contest {contest_id}",
                                   "more than 1% of ballots overvoted; check ballot design and scanner thresholds",
                                   None, t.overvoted_ballots))

    if provisional is not None:
        p = provisional
        if p.accepted + p.rejected + p.pending != p.issued:
            out.append(Discrepancy("PROVISIONAL_UNBALANCED", BLOCKING, "provisional ballots",
                                   "issued != accepted + rejected + pending", p.issued, p.accepted + p.rejected + p.pending))
        if p.pending:
            out.append(Discrepancy("PROVISIONAL_PENDING", BLOCKING, "provisional ballots",
                                   "provisional ballots still awaiting adjudication", 0, p.pending))
        if p.accepted_counted != p.accepted:
            out.append(Discrepancy("PROVISIONAL_COUNT_MISMATCH", BLOCKING, "provisional ballots",
                                   "accepted provisional ballots not all counted (or extra counted)", p.accepted, p.accepted_counted))
    return out


def summary(discrepancies: Sequence[Discrepancy]) -> Dict[str, object]:
    blocking = [d for d in discrepancies if d.severity == BLOCKING]
    return {
        "format": "eige.reconciliation.v1",
        "ready_to_certify": not blocking,
        "blocking": len(blocking),
        "review": len(discrepancies) - len(blocking),
        "discrepancies": [d.as_dict() for d in discrepancies],
    }
