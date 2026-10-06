# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Election definitions, cast vote records (CVRs) and ballot manifests.

The model is a deliberately small subset of the NIST common data formats:

* NIST SP 1500-103 *Cast Vote Records* — ``UniqueId``, ``BatchId``,
  ``BallotStyleId`` and per-contest selections, overvotes and undervotes;
  :func:`cvr_from_nist` / :func:`cvr_to_nist` convert to and from the JSON
  serialisation (``CVR.CVR`` objects).
* NIST SP 1500-100 *Election Results Reporting* — per-contest candidate totals,
  overvotes and undervotes (:func:`results_report`).

It is not a complete implementation of either specification; fields EIGE does
not use (ranked choice, fractional votes, party-specific CVR fields, etc.) are
not represented.  All parsing is strict: unknown contests, unknown candidates,
duplicate identifiers and negative counts are rejected with :class:`ModelError`.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class ModelError(ValueError):
    """Raised for malformed or inconsistent election data."""


def _req_str(d: Mapping[str, Any], key: str, where: str) -> str:
    value = d.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{where}: '{key}' must be a non-empty string")
    return value


def _req_int(d: Mapping[str, Any], key: str, where: str, minimum: int = 0) -> int:
    value = d.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ModelError(f"{where}: '{key}' must be an integer >= {minimum}")
    return value


@dataclass(frozen=True)
class Candidate:
    id: str
    name: str
    party: Optional[str] = None


@dataclass(frozen=True)
class Contest:
    id: str
    name: str
    vote_for: int
    candidates: Tuple[Candidate, ...]

    @property
    def candidate_ids(self) -> List[str]:
        return [c.id for c in self.candidates]

    @cached_property
    def candidate_set(self) -> frozenset:
        return frozenset(c.id for c in self.candidates)


@dataclass(frozen=True)
class Election:
    id: str
    name: str
    date: str
    jurisdiction: str
    contests: Tuple[Contest, ...]

    @cached_property
    def contest_map(self) -> Dict[str, Contest]:
        return {c.id: c for c in self.contests}

    def contest(self, contest_id: str) -> Contest:
        c = self.contest_map.get(contest_id)
        if c is None:
            raise ModelError(f"unknown contest {contest_id!r}")
        return c


def parse_election(d: Mapping[str, Any]) -> Election:
    if not isinstance(d, Mapping):
        raise ModelError("election must be an object")
    contests: List[Contest] = []
    seen: set = set()
    raw_contests = d.get("contests")
    if not isinstance(raw_contests, list) or not raw_contests:
        raise ModelError("election: 'contests' must be a non-empty list")
    for i, rc in enumerate(raw_contests):
        where = f"contests[{i}]"
        if not isinstance(rc, Mapping):
            raise ModelError(f"{where}: must be an object")
        cid = _req_str(rc, "id", where)
        if cid in seen:
            raise ModelError(f"duplicate contest id {cid!r}")
        seen.add(cid)
        raw_cands = rc.get("candidates")
        if not isinstance(raw_cands, list) or len(raw_cands) < 1:
            raise ModelError(f"{where}: 'candidates' must be a non-empty list")
        cands: List[Candidate] = []
        cand_ids: set = set()
        for j, cc in enumerate(raw_cands):
            cw = f"{where}.candidates[{j}]"
            if not isinstance(cc, Mapping):
                raise ModelError(f"{cw}: must be an object")
            cand = Candidate(_req_str(cc, "id", cw), _req_str(cc, "name", cw), cc.get("party"))
            if cand.id in cand_ids:
                raise ModelError(f"{where}: duplicate candidate id {cand.id!r}")
            cand_ids.add(cand.id)
            cands.append(cand)
        vote_for = _req_int(rc, "vote_for", where, minimum=1)
        if vote_for > len(cands):
            raise ModelError(f"{where}: vote_for exceeds number of candidates")
        contests.append(Contest(cid, _req_str(rc, "name", where), vote_for, tuple(cands)))
    return Election(
        _req_str(d, "id", "election"),
        _req_str(d, "name", "election"),
        _req_str(d, "date", "election"),
        _req_str(d, "jurisdiction", "election"),
        tuple(contests),
    )


@dataclass(frozen=True)
class ContestOutcome:
    """Interpretation of one CVR for one contest."""

    votes: Tuple[str, ...]  # candidates receiving a vote (empty if overvoted)
    overvoted: bool
    undervotes: int  # unused vote opportunities (0 if overvoted)


@dataclass(frozen=True)
class CVR:
    id: str
    batch_id: str
    ballot_style: str
    selections: Mapping[str, Tuple[str, ...]]  # contest_id -> marked candidate ids
    reporting_unit: Optional[str] = None  # precinct / GpUnit the ballot is reported under

    def outcome(self, contest: Contest) -> Optional[ContestOutcome]:
        """Return the outcome for ``contest`` or ``None`` if not on this ballot."""
        if contest.id not in self.selections:
            return None
        marks = self.selections[contest.id]
        if len(marks) > contest.vote_for:
            return ContestOutcome((), True, 0)
        return ContestOutcome(tuple(marks), False, contest.vote_for - len(marks))


def parse_cvr(item: Any, election: Election, where: str = "cvr") -> CVR:
    """Strictly parse one CVR object (no cross-CVR checks)."""
    if not isinstance(item, Mapping):
        raise ModelError(f"{where}: must be an object")
    cvr_id = _req_str(item, "id", where)
    raw_sel = item.get("selections")
    if not isinstance(raw_sel, Mapping):
        raise ModelError(f"{where}: 'selections' must be an object")
    contests = election.contest_map
    sel: Dict[str, Tuple[str, ...]] = {}
    for contest_id, marks in raw_sel.items():
        contest = contests.get(contest_id)
        if contest is None:
            raise ModelError(f"{where}: unknown contest {contest_id!r}")
        if not isinstance(marks, list) or not all(isinstance(m, str) for m in marks):
            raise ModelError(f"{where}: selections for {contest_id!r} must be a list of candidate ids")
        if len(set(marks)) != len(marks):
            raise ModelError(f"{where}: repeated candidate in {contest_id!r}")
        allowed = contest.candidate_set
        unknown = [m for m in marks if m not in allowed]
        if unknown:
            raise ModelError(f"{where}: unknown candidate(s) {unknown} in {contest_id!r}")
        sel[contest_id] = tuple(marks)
    unit = item.get("reporting_unit")
    if unit is not None and (not isinstance(unit, str) or not unit.strip()):
        raise ModelError(f"{where}: 'reporting_unit' must be a non-empty string when present")
    return CVR(cvr_id, _req_str(item, "batch_id", where), _req_str(item, "ballot_style", where), sel, unit)


def parse_cvrs(items: Sequence[Any], election: Election) -> List[CVR]:
    """Parse a list of CVRs, rejecting duplicate ids (for in-memory use)."""
    if not isinstance(items, list):
        raise ModelError("cvrs must be a list")
    out: List[CVR] = []
    seen: set = set()
    for i, item in enumerate(items):
        cvr = parse_cvr(item, election, f"cvrs[{i}]")
        if cvr.id in seen:
            raise ModelError(f"duplicate CVR id {cvr.id!r}")
        seen.add(cvr.id)
        out.append(cvr)
    return out


def cvr_to_nist(cvr: CVR, election: Election) -> dict:
    """Serialise a CVR in the NIST SP 1500-103 JSON shape (subset)."""
    contests = []
    for contest_id, marks in sorted(cvr.selections.items()):
        outcome = cvr.outcome(election.contest(contest_id))
        contests.append({
            "@type": "CVR.CVRContest",
            "ContestId": contest_id,
            "Overvotes": 1 if outcome.overvoted else 0,
            "Undervotes": outcome.undervotes,
            "CVRContestSelection": [
                {
                    "@type": "CVR.CVRContestSelection",
                    "ContestSelectionId": m,
                    "SelectionPosition": [{"@type": "CVR.SelectionPosition", "HasIndication": "yes", "NumberVotes": 1}],
                }
                for m in marks
            ],
        })
    return {
        "@type": "CVR.CVR",
        "UniqueId": cvr.id,
        "BatchId": cvr.batch_id,
        "BallotStyleId": cvr.ballot_style,
        "CurrentSnapshotId": f"{cvr.id}-original",
        "CVRSnapshot": [{"@type": "CVR.CVRSnapshot", "@id": f"{cvr.id}-original", "Type": "original", "CVRContest": contests}],
    }


def cvr_from_nist(d: Mapping[str, Any], election: Election) -> CVR:
    """Parse a NIST SP 1500-103 JSON ``CVR.CVR`` object (subset) into a :class:`CVR`."""
    if not isinstance(d, Mapping) or d.get("@type") != "CVR.CVR":
        raise ModelError("expected a CVR.CVR object")
    snapshots = d.get("CVRSnapshot")
    if not isinstance(snapshots, list) or not snapshots:
        raise ModelError("CVR has no CVRSnapshot")
    current = d.get("CurrentSnapshotId")
    snap = next((s for s in snapshots if isinstance(s, Mapping) and s.get("@id") == current), snapshots[0])
    if not isinstance(snap, Mapping):
        raise ModelError("malformed CVRSnapshot")
    selections: Dict[str, List[str]] = {}
    for cc in snap.get("CVRContest", []) or []:
        if not isinstance(cc, Mapping):
            raise ModelError("malformed CVRContest")
        marks: List[str] = []
        for sel in cc.get("CVRContestSelection", []) or []:
            positions = sel.get("SelectionPosition", []) if isinstance(sel, Mapping) else None
            if not isinstance(positions, list):
                raise ModelError("malformed CVRContestSelection")
            if any(isinstance(p, Mapping) and p.get("HasIndication") == "yes" for p in positions):
                marks.append(sel.get("ContestSelectionId"))
        selections[str(cc.get("ContestId"))] = marks
    return parse_cvrs([{
        "id": d.get("UniqueId"),
        "batch_id": d.get("BatchId"),
        "ballot_style": d.get("BallotStyleId"),
        "selections": selections,
    }], election)[0]


@dataclass(frozen=True)
class ManifestBatch:
    batch_id: str
    ballot_count: int
    container_id: str
    tabulator_id: str = ""


@dataclass(frozen=True)
class BallotManifest:
    jurisdiction: str
    batches: Tuple[ManifestBatch, ...]

    @cached_property
    def _cumulative(self) -> List[int]:
        out, running = [], 0
        for b in self.batches:
            running += b.ballot_count
            out.append(running)
        return out

    @cached_property
    def _by_id(self) -> Dict[str, ManifestBatch]:
        return {b.batch_id: b for b in self.batches}

    @property
    def total_ballots(self) -> int:
        return self._cumulative[-1] if self.batches else 0

    def batch(self, batch_id: str) -> ManifestBatch:
        b = self._by_id.get(batch_id)
        if b is None:
            raise ModelError(f"unknown batch {batch_id!r}")
        return b

    def locate(self, position: int) -> Tuple[str, int]:
        """Map a 1-based ballot position across the manifest to (batch_id, 1-based index in batch).

        O(log B) in the number of batches, so statewide manifests with tens of
        thousands of batches are mapped instantly.
        """
        if not 1 <= position <= self.total_ballots:
            raise ModelError(f"position {position} outside manifest of {self.total_ballots} ballots")
        cum = self._cumulative
        k = bisect.bisect_left(cum, position)
        before = cum[k - 1] if k else 0
        return self.batches[k].batch_id, position - before


def parse_manifest(d: Mapping[str, Any]) -> BallotManifest:
    if not isinstance(d, Mapping):
        raise ModelError("manifest must be an object")
    raw = d.get("batches")
    if not isinstance(raw, list):
        raise ModelError("manifest: 'batches' must be a list")
    batches: List[ManifestBatch] = []
    seen: set = set()
    for i, rb in enumerate(raw):
        where = f"batches[{i}]"
        if not isinstance(rb, Mapping):
            raise ModelError(f"{where}: must be an object")
        b = ManifestBatch(
            _req_str(rb, "batch_id", where),
            _req_int(rb, "ballot_count", where),
            _req_str(rb, "container_id", where),
            str(rb.get("tabulator_id", "")),
        )
        if b.batch_id in seen:
            raise ModelError(f"duplicate batch id {b.batch_id!r}")
        seen.add(b.batch_id)
        batches.append(b)
    return BallotManifest(_req_str(d, "jurisdiction", "manifest"), tuple(batches))


@dataclass
class ContestTotals:
    contest_id: str
    vote_for: int
    ballots: int = 0
    overvoted_ballots: int = 0
    undervotes: int = 0
    candidate_votes: Dict[str, int] = field(default_factory=dict)

    def balances(self) -> bool:
        """Vote-opportunity identity: votes + overvote·vote_for + undervotes == ballots·vote_for."""
        used = sum(self.candidate_votes.values()) + self.overvoted_ballots * self.vote_for + self.undervotes
        return used == self.ballots * self.vote_for

    def winners(self) -> List[str]:
        ranked = sorted(self.candidate_votes.items(), key=lambda kv: (-kv[1], kv[0]))
        return [c for c, _ in ranked[: self.vote_for]]


def tally(election: Election, cvrs: Iterable[CVR]) -> Dict[str, ContestTotals]:
    totals = {c.id: ContestTotals(c.id, c.vote_for, candidate_votes={k: 0 for k in c.candidate_ids}) for c in election.contests}
    contests = {c.id: c for c in election.contests}
    for cvr in cvrs:
        for contest_id in cvr.selections:
            outcome = cvr.outcome(contests[contest_id])
            t = totals[contest_id]
            t.ballots += 1
            if outcome.overvoted:
                t.overvoted_ballots += 1
            else:
                t.undervotes += outcome.undervotes
                for m in outcome.votes:
                    t.candidate_votes[m] += 1
    return totals


def results_report(election: Election, cvrs: Iterable[CVR], by_reporting_unit: bool = False) -> dict:
    """Per-contest results in a NIST SP 1500-100–style JSON subset.

    ``VoteCounts`` entries for a candidate are disjoint parts of its total.
    By default there is one entry for the whole jurisdiction; with
    ``by_reporting_unit=True`` there is one entry per reporting unit (precinct)
    taken from each CVR's ``reporting_unit``, which lets verifiers check
    precinct-level results as well as contest totals.
    """
    from ..audit.reconciliation import CanvassAccumulator

    acc = CanvassAccumulator(election, track_units=by_reporting_unit)
    try:
        for cvr in cvrs:
            if by_reporting_unit and cvr.reporting_unit is None:
                raise ModelError(f"CVR {cvr.id!r} has no reporting_unit")
            acc.add(cvr)
        return results_from_totals(election, acc.totals, acc.unit_votes if by_reporting_unit else None,
                                   acc.unit_contests if by_reporting_unit else None)
    finally:
        acc.close()


def results_from_totals(election: Election, totals: Mapping[str, "ContestTotals"],
                        unit_votes: Optional[Mapping[Tuple[str, str], Mapping[str, int]]] = None,
                        unit_contests: Optional[Iterable[Tuple[str, str]]] = None) -> dict:
    """Build the results document from accumulated totals (see :func:`results_report`)."""
    by_unit = unit_votes is not None
    keys = sorted(set(unit_contests or ()) | set(unit_votes or ()))

    def counts(contest_id: str, cid: str, v: int) -> list:
        if not by_unit:
            return [{"@type": "ElectionResults.VoteCounts", "Count": v, "GpUnitId": election.jurisdiction}]
        return [{"@type": "ElectionResults.VoteCounts", "Count": int(unit_votes.get((c, u), {}).get(cid, 0)), "GpUnitId": u}
                for (c, u) in keys if c == contest_id]

    return {
        "@type": "ElectionResults.ElectionReport",
        "format": "eige.err_subset.v1",
        "Election": {"@id": election.id, "Name": election.name, "StartDate": election.date, "EndDate": election.date},
        "Jurisdiction": election.jurisdiction,
        "Contest": [
            {
                "@type": "ElectionResults.CandidateContest",
                "@id": t.contest_id,
                "VotesAllowed": t.vote_for,
                "BallotsCast": t.ballots,
                "Overvotes": t.overvoted_ballots,
                "Undervotes": t.undervotes,
                "ContestSelection": [
                    {"@type": "ElectionResults.CandidateSelection", "CandidateId": cid,
                     "VoteCounts": counts(t.contest_id, cid, v)}
                    for cid, v in sorted(t.candidate_votes.items())
                ],
            }
            for t in totals.values()
        ],
    }


def reported_totals(report: Mapping[str, Any]) -> Dict[str, Dict[str, int]]:
    """Extract ``{contest_id: {candidate_id: votes}}`` from :func:`results_report` output."""
    out: Dict[str, Dict[str, int]] = {}
    for contest in report.get("Contest", []):
        out[str(contest["@id"])] = {
            str(sel["CandidateId"]): sum(int(vc["Count"]) for vc in sel.get("VoteCounts", []))
            for sel in contest.get("ContestSelection", [])
        }
    return out


def reported_unit_totals(report: Mapping[str, Any]) -> Optional[Dict[Tuple[str, str], Dict[str, int]]]:
    """``{(contest_id, unit): {candidate_id: votes}}`` if results are broken down by reporting unit.

    Returns ``None`` when every ``VoteCounts`` entry is for the whole
    jurisdiction (no unit-level claims to check).
    """
    jurisdiction = report.get("Jurisdiction")
    out: Dict[Tuple[str, str], Dict[str, int]] = {}
    unit_level = False
    for contest in report.get("Contest", []):
        cid = str(contest["@id"])
        for sel in contest.get("ContestSelection", []):
            for vc in sel.get("VoteCounts", []):
                unit = str(vc.get("GpUnitId", jurisdiction))
                if unit != jurisdiction:
                    unit_level = True
                bucket = out.setdefault((cid, unit), {})
                cand = str(sel["CandidateId"])
                bucket[cand] = bucket.get(cand, 0) + int(vc["Count"])
    return out if unit_level else None
