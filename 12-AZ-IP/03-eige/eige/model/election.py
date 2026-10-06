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

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class Election:
    id: str
    name: str
    date: str
    jurisdiction: str
    contests: Tuple[Contest, ...]

    def contest(self, contest_id: str) -> Contest:
        for c in self.contests:
            if c.id == contest_id:
                return c
        raise ModelError(f"unknown contest {contest_id!r}")


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

    def outcome(self, contest: Contest) -> Optional[ContestOutcome]:
        """Return the outcome for ``contest`` or ``None`` if not on this ballot."""
        if contest.id not in self.selections:
            return None
        marks = self.selections[contest.id]
        if len(marks) > contest.vote_for:
            return ContestOutcome((), True, 0)
        return ContestOutcome(tuple(marks), False, contest.vote_for - len(marks))


def parse_cvrs(items: Sequence[Any], election: Election) -> List[CVR]:
    if not isinstance(items, list):
        raise ModelError("cvrs must be a list")
    contests = {c.id: c for c in election.contests}
    out: List[CVR] = []
    seen: set = set()
    for i, item in enumerate(items):
        where = f"cvrs[{i}]"
        if not isinstance(item, Mapping):
            raise ModelError(f"{where}: must be an object")
        cvr_id = _req_str(item, "id", where)
        if cvr_id in seen:
            raise ModelError(f"duplicate CVR id {cvr_id!r}")
        seen.add(cvr_id)
        raw_sel = item.get("selections")
        if not isinstance(raw_sel, Mapping):
            raise ModelError(f"{where}: 'selections' must be an object")
        sel: Dict[str, Tuple[str, ...]] = {}
        for contest_id, marks in raw_sel.items():
            contest = contests.get(contest_id)
            if contest is None:
                raise ModelError(f"{where}: unknown contest {contest_id!r}")
            if not isinstance(marks, list) or not all(isinstance(m, str) for m in marks):
                raise ModelError(f"{where}: selections for {contest_id!r} must be a list of candidate ids")
            if len(set(marks)) != len(marks):
                raise ModelError(f"{where}: repeated candidate in {contest_id!r}")
            unknown = [m for m in marks if m not in contest.candidate_ids]
            if unknown:
                raise ModelError(f"{where}: unknown candidate(s) {unknown} in {contest_id!r}")
            sel[contest_id] = tuple(marks)
        out.append(CVR(cvr_id, _req_str(item, "batch_id", where), _req_str(item, "ballot_style", where), sel))
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

    @property
    def total_ballots(self) -> int:
        return sum(b.ballot_count for b in self.batches)

    def batch(self, batch_id: str) -> ManifestBatch:
        for b in self.batches:
            if b.batch_id == batch_id:
                return b
        raise ModelError(f"unknown batch {batch_id!r}")

    def locate(self, position: int) -> Tuple[str, int]:
        """Map a 1-based ballot position across the manifest to (batch_id, 1-based index in batch)."""
        if not 1 <= position <= self.total_ballots:
            raise ModelError(f"position {position} outside manifest of {self.total_ballots} ballots")
        remaining = position
        for b in self.batches:
            if remaining <= b.ballot_count:
                return b.batch_id, remaining
            remaining -= b.ballot_count
        raise ModelError("unreachable")  # pragma: no cover


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


def results_report(election: Election, cvrs: Iterable[CVR]) -> dict:
    """Per-contest results in a NIST SP 1500-100–style JSON subset."""
    totals = tally(election, cvrs)
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
                     "VoteCounts": [{"@type": "ElectionResults.VoteCounts", "Count": v, "GpUnitId": election.jurisdiction}]}
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
