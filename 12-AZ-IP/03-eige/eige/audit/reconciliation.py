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
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from ..dedup import DuplicateDetector
from ..model.election import BallotManifest, CVR, ContestTotals, Election

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


class CanvassAccumulator:
    """Single-pass, bounded-memory accumulation of everything reconciliation needs.

    Feed CVRs one at a time with :meth:`add`; memory grows with the number of
    batches, contests and (optionally) reporting units, not with the number of
    ballots.  Duplicate CVR ids are found exactly with a disk-spilling
    :class:`~eige.dedup.DuplicateDetector`.
    """

    def __init__(self, election: Election, track_units: bool = False, dedup_memory_limit: int = 2_000_000,
                 tmpdir: Optional[str] = None) -> None:
        self.election = election
        self.contests = election.contest_map
        self.totals: Dict[str, ContestTotals] = {
            c.id: ContestTotals(c.id, c.vote_for, candidate_votes={k: 0 for k in c.candidate_ids})
            for c in election.contests
        }
        self.counted: Counter = Counter()
        self.ids = DuplicateDetector(dedup_memory_limit, tmpdir)
        self.track_units = track_units
        self.unit_votes: Dict[Tuple[str, str], Counter] = {}
        self.unit_contests: set = set()  # (contest, unit) pairs that appear on at least one ballot
        self.cvrs_without_unit = 0
        self.n = 0

    def add(self, cvr: CVR) -> None:
        self.n += 1
        self.ids.add(cvr.id)
        self.counted[cvr.batch_id] += 1
        if self.track_units and cvr.reporting_unit is None:
            self.cvrs_without_unit += 1
        for contest_id, marks in cvr.selections.items():
            contest = self.contests[contest_id]
            t = self.totals[contest_id]
            t.ballots += 1
            if self.track_units and cvr.reporting_unit is not None:
                self.unit_contests.add((contest_id, cvr.reporting_unit))
            if len(marks) > contest.vote_for:
                t.overvoted_ballots += 1
                continue
            t.undervotes += contest.vote_for - len(marks)
            cv = t.candidate_votes
            for m in marks:
                cv[m] += 1
            if self.track_units and cvr.reporting_unit is not None and marks:
                key = (contest_id, cvr.reporting_unit)
                c = self.unit_votes.get(key)
                if c is None:
                    c = self.unit_votes[key] = Counter()
                c.update(marks)

    def close(self) -> None:
        self.ids.close()

    def discrepancies(
        self,
        manifest: BallotManifest,
        cast_by_batch: Optional[Mapping[str, int]] = None,
        reported: Optional[Mapping[str, Mapping[str, int]]] = None,
        provisional: Optional[ProvisionalAccount] = None,
        reported_units: Optional[Mapping[Tuple[str, str], Mapping[str, int]]] = None,
    ) -> List[Discrepancy]:
        out: List[Discrepancy] = []
        for cvr_id, n in sorted(self.ids.duplicates().items()):
            out.append(Discrepancy("DUPLICATE_CVR_ID", BLOCKING, f"cvr {cvr_id}", f"CVR id appears {n} times", 1, n))

        counted = self.counted
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

        for contest_id, t in self.totals.items():
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

        if reported_units is not None:
            out.extend(self._unit_discrepancies(reported_units))

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

    def _unit_discrepancies(self, reported_units: Mapping[Tuple[str, str], Mapping[str, int]]) -> List[Discrepancy]:
        out: List[Discrepancy] = []
        if self.cvrs_without_unit:
            out.append(Discrepancy("CVR_REPORTING_UNIT_MISSING", BLOCKING, "cast vote records",
                                   "results are reported by precinct/reporting unit but some CVRs do not name one, "
                                   "so unit-level totals cannot be recomputed", 0, self.cvrs_without_unit))
        for key in sorted(set(reported_units) | set(self.unit_votes)):
            contest_id, unit = key
            contest = self.contests.get(contest_id)
            rep = reported_units.get(key, {})
            got = self.unit_votes.get(key, Counter())
            cands = sorted(set(rep) | set(got) | (set(contest.candidate_ids) if contest else set()))
            for cand in cands:
                r, g = int(rep.get(cand, 0)), got.get(cand, 0)
                if r != g:
                    out.append(Discrepancy("REPORTED_UNIT_TOTAL_MISMATCH", BLOCKING,
                                           f"contest {contest_id} / unit {unit} / {cand}",
                                           "reporting-unit total differs from the total recomputed from CVRs", g, r))
        return out


def reconcile(
    election: Election,
    manifest: BallotManifest,
    cvrs: Iterable[CVR],
    cast_by_batch: Optional[Mapping[str, int]] = None,
    reported: Optional[Mapping[str, Mapping[str, int]]] = None,
    provisional: Optional[ProvisionalAccount] = None,
) -> List[Discrepancy]:
    acc = CanvassAccumulator(election)
    try:
        for c in cvrs:
            acc.add(c)
        return acc.discrepancies(manifest, cast_by_batch, reported, provisional)
    finally:
        acc.close()


def summary(discrepancies: Sequence[Discrepancy]) -> Dict[str, object]:
    blocking = [d for d in discrepancies if d.severity == BLOCKING]
    return {
        "format": "eige.reconciliation.v1",
        "ready_to_certify": not blocking,
        "blocking": len(blocking),
        "review": len(discrepancies) - len(blocking),
        "discrepancies": [d.as_dict() for d in discrepancies],
    }
