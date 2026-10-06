# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Streaming readers for cast vote record exports.

Every reader yields EIGE CVR dicts (``id``, ``batch_id``, ``ballot_style``,
``selections`` and optional ``reporting_unit``) one at a time, so exports of
any size are processed in constant memory.

Supported inputs
----------------
``nist-json``
    A NIST SP 1500-103 ``CVR.CastVoteRecordReport`` JSON document.  The ``CVR``
    array is parsed incrementally; the document is never loaded whole.  If the
    report's ``Election`` objects map ``ContestSelection`` ids to
    ``CandidateIds`` (and appear before the ``CVR`` array, as in the NIST
    examples), selection ids are translated to candidate ids; otherwise the
    selection id must equal the candidate id in ``election.json``.
    ``BallotStyleUnitId`` becomes the CVR's ``reporting_unit``.
``nist-jsonl``
    One ``CVR.CVR`` object per line (a common way to ship very large exports).
``csv``
    The EIGE generic CSV (``docs/FORMATS.md``): header
    ``cvr_id,batch_id,ballot_style[,reporting_unit],<contest_id>...``; each
    contest cell is ``|``-separated candidate ids, empty for a contest on the
    ballot with no marks (undervote) and ``~`` for a contest not on the ballot.

Vendor exports that are not NIST SP 1500-103 (for example proprietary
JSON or CSV layouts) must first be converted to one of these formats; the
converter is jurisdiction-specific and is not part of EIGE.
"""

from __future__ import annotations

import csv
import io
import json
from typing import IO, Any, Dict, Iterator, List, Mapping, Optional

from .model.election import ModelError

NOT_ON_BALLOT = "~"
_CHUNK = 1 << 20
MAX_VALUE_CHARS = 64 * 1024 * 1024  # one CVR (or the Election header) must fit in this


class CVRImportError(ValueError):
    """Raised for malformed CVR exports."""


def nist_cvr_to_eige(d: Mapping[str, Any], selection_map: Optional[Mapping[str, str]] = None,
                     contest_map: Optional[Mapping[str, str]] = None) -> dict:
    """Convert one NIST ``CVR.CVR`` object to an EIGE CVR dict (no election validation)."""
    if not isinstance(d, Mapping) or d.get("@type") != "CVR.CVR":
        raise CVRImportError("expected a CVR.CVR object")
    snapshots = d.get("CVRSnapshot")
    if not isinstance(snapshots, list) or not snapshots:
        raise CVRImportError(f"CVR {d.get('UniqueId')!r} has no CVRSnapshot")
    current = d.get("CurrentSnapshotId")
    snap = next((s for s in snapshots if isinstance(s, Mapping) and s.get("@id") == current), None)
    if snap is None:
        if current is not None:
            raise CVRImportError(f"CVR {d.get('UniqueId')!r}: CurrentSnapshotId {current!r} not found")
        snap = snapshots[0]
    if not isinstance(snap, Mapping):
        raise CVRImportError("malformed CVRSnapshot")
    selections: Dict[str, List[str]] = {}
    for cc in snap.get("CVRContest", []) or []:
        if not isinstance(cc, Mapping):
            raise CVRImportError("malformed CVRContest")
        contest_id = str(cc.get("ContestId"))
        if contest_map:
            contest_id = contest_map.get(contest_id, contest_id)
        marks: List[str] = []
        # An overvoted contest is kept as an overvote (all indicated marks), even
        # though tabulators mark those positions IsAllocable="no"; otherwise only
        # allocable indications count (e.g. adjudicated-out marks are dropped).
        overvoted = isinstance(cc.get("Overvotes"), int) and cc["Overvotes"] > 0
        for sel in cc.get("CVRContestSelection", []) or []:
            positions = sel.get("SelectionPosition", []) if isinstance(sel, Mapping) else None
            if not isinstance(positions, list):
                raise CVRImportError("malformed CVRContestSelection")
            if any(isinstance(p, Mapping) and p.get("HasIndication") == "yes"
                   and (overvoted or p.get("IsAllocable", "yes") != "no") for p in positions):
                sid = str(sel.get("ContestSelectionId"))
                marks.append(selection_map.get(sid, sid) if selection_map else sid)
        selections[contest_id] = marks
    out = {"id": d.get("UniqueId"), "batch_id": d.get("BatchId"), "ballot_style": d.get("BallotStyleId"),
           "selections": selections}
    unit = d.get("BallotStyleUnitId")
    if unit is not None:
        out["reporting_unit"] = str(unit)
    return out


def _selection_map_from_election(objs: Any) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for e in objs if isinstance(objs, list) else [objs]:
        if not isinstance(e, Mapping):
            continue
        for c in e.get("Contest", []) or []:
            for s in (c.get("ContestSelection", []) or []) if isinstance(c, Mapping) else []:
                if isinstance(s, Mapping) and s.get("@id") and isinstance(s.get("CandidateIds"), list) and len(s["CandidateIds"]) == 1:
                    out[str(s["@id"])] = str(s["CandidateIds"][0])
    return out


class _Reader:
    """Incremental JSON tokenizer over a text stream (bounded buffer)."""

    def __init__(self, fh: IO[str]) -> None:
        self.fh = fh
        self.buf = ""
        self.pos = 0
        self.eof = False
        self.dec = json.JSONDecoder()

    def _fill(self) -> bool:
        if self.eof:
            return False
        chunk = self.fh.read(_CHUNK)
        if not chunk:
            self.eof = True
            return False
        self.buf = self.buf[self.pos:] + chunk
        self.pos = 0
        return True

    def peek(self) -> str:
        while True:
            while self.pos < len(self.buf) and self.buf[self.pos] in " \t\r\n":
                self.pos += 1
            if self.pos < len(self.buf):
                return self.buf[self.pos]
            if not self._fill():
                return ""

    def expect(self, ch: str) -> None:
        if self.peek() != ch:
            raise CVRImportError(f"expected {ch!r} in CVR report")
        self.pos += 1

    def value(self) -> Any:
        self.peek()
        while True:
            try:
                obj, end = self.dec.raw_decode(self.buf, self.pos)
            except json.JSONDecodeError as exc:
                if len(self.buf) - self.pos > MAX_VALUE_CHARS:
                    raise CVRImportError("CVR report value is malformed or larger than "
                                         f"{MAX_VALUE_CHARS} characters") from exc
                if self._fill():
                    continue
                raise CVRImportError(f"invalid JSON in CVR report: {exc}") from exc
            # a number at the very end of the buffer may be cut off
            if end == len(self.buf) and not self.eof and isinstance(obj, (int, float)):
                if self._fill():
                    continue
            self.pos = end
            return obj


def iter_nist_cvr_report(fh: IO[str]) -> Iterator[dict]:
    """Stream EIGE CVR dicts out of a NIST ``CastVoteRecordReport`` JSON document."""
    r = _Reader(fh)
    r.expect("{")
    selection_map: Dict[str, str] = {}
    seen_cvr = False
    if r.peek() == "}":
        raise CVRImportError("CVR report has no 'CVR' array")
    while True:
        key = r.value()
        if not isinstance(key, str):
            raise CVRImportError("malformed CVR report object")
        r.expect(":")
        if key == "CVR":
            seen_cvr = True
            r.expect("[")
            if r.peek() == "]":
                r.pos += 1
            else:
                while True:
                    yield nist_cvr_to_eige(r.value(), selection_map)
                    c = r.peek()
                    r.pos += 1
                    if c == "]":
                        break
                    if c != ",":
                        raise CVRImportError("expected ',' or ']' in CVR array")
        else:
            v = r.value()
            if key == "Election":
                selection_map.update(_selection_map_from_election(v))
            elif key == "@type" and v != "CVR.CastVoteRecordReport":
                raise CVRImportError(f"not a CastVoteRecordReport (@type {v!r})")
        c = r.peek()
        r.pos += 1
        if c == "}":
            break
        if c != ",":
            raise CVRImportError("expected ',' or '}' in CVR report")
    if not seen_cvr:
        raise CVRImportError("CVR report has no 'CVR' array")


def iter_nist_jsonl(fh: IO[str]) -> Iterator[dict]:
    for n, line in enumerate(fh, start=1):
        if line.strip():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CVRImportError(f"line {n}: invalid JSON ({exc})") from exc
            yield nist_cvr_to_eige(obj)


def iter_csv(fh: IO[str]) -> Iterator[dict]:
    reader = csv.reader(fh)
    try:
        header = next(reader)
    except StopIteration:
        raise CVRImportError("CSV is empty") from None
    fixed = ["cvr_id", "batch_id", "ballot_style"]
    if header[:3] != fixed:
        raise CVRImportError(f"CSV header must start with {','.join(fixed)}")
    has_unit = len(header) > 3 and header[3] == "reporting_unit"
    contests = header[4:] if has_unit else header[3:]
    if not contests or len(set(contests)) != len(contests):
        raise CVRImportError("CSV must name each contest column exactly once")
    width = len(header)
    for n, row in enumerate(reader, start=2):
        if not row:
            continue
        if len(row) != width:
            raise CVRImportError(f"CSV line {n}: expected {width} columns, found {len(row)}")
        sel: Dict[str, List[str]] = {}
        for contest_id, cell in zip(contests, row[4:] if has_unit else row[3:]):
            if cell == NOT_ON_BALLOT:
                continue
            sel[contest_id] = [m for m in cell.split("|")] if cell else []
            if any(m == "" for m in sel[contest_id]):
                raise CVRImportError(f"CSV line {n}: empty candidate id in {contest_id!r}")
        out = {"id": row[0], "batch_id": row[1], "ballot_style": row[2], "selections": sel}
        if has_unit:
            out["reporting_unit"] = row[3]
        yield out


READERS = {"nist-json": iter_nist_cvr_report, "nist-jsonl": iter_nist_jsonl, "csv": iter_csv}


def iter_cvr_file(path: str, fmt: str) -> Iterator[dict]:
    if fmt not in READERS:
        raise CVRImportError(f"unknown CVR format {fmt!r}; expected one of {sorted(READERS)}")
    newline = "" if fmt == "csv" else None
    with open(path, encoding="utf-8-sig", newline=newline) as fh:
        yield from READERS[fmt](fh)


def iter_cvr_text(text: str, fmt: str) -> Iterator[dict]:
    """Convenience for tests and small inputs."""
    yield from READERS[fmt](io.StringIO(text, newline="" if fmt == "csv" else None))


__all__ = ["CVRImportError", "ModelError", "NOT_ON_BALLOT", "iter_cvr_file", "iter_cvr_text",
           "iter_csv", "iter_nist_cvr_report", "iter_nist_jsonl", "nist_cvr_to_eige"]
