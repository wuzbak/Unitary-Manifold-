# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Parallel scan of a large ``log.jsonl`` across worker processes.

The file is split into byte ranges on line boundaries.  Each worker checks
canonical form, hashes leaves, parses CVRs and accumulates batch counts,
tallies and reporting-unit totals for its range; CVR identifiers are spilled to
hash-bucketed files for exact duplicate detection.  The parent consumes the
worker results strictly in file order, so Merkle roots, entry indices, error
positions and audit-sample positions are identical to the serial scan in
:mod:`eige.verify` (this equivalence is tested).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from typing import Any, Deque, Dict, Iterator, List, Optional, Set, Tuple

from .audit import reconciliation as recon
from .bundle import MAX_ENTRY_BYTES
from .canonical import CanonicalEncodingError, decode_canonical
from .crypto import merkle
from .model.election import parse_cvr, parse_election

_MALFORMED = (ValueError, KeyError, TypeError, AttributeError, IndexError)


def split_ranges(path: str, parts: int) -> List[Tuple[int, int]]:
    """Split a file into ``parts`` byte ranges that start and end on line boundaries."""
    size = os.path.getsize(path)
    if size == 0 or parts <= 1:
        return [(0, size)]
    cuts = [0]
    with open(path, "rb") as fh:
        for k in range(1, parts):
            target = max(size * k // parts, cuts[-1])
            fh.seek(target)
            if target > 0:
                fh.seek(target - 1)
                if fh.read(1) != b"\n":
                    fh.readline()
            pos = fh.tell()
            if pos > cuts[-1] and pos < size:
                cuts.append(pos)
    cuts.append(size)
    return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]


def _worker(args: tuple) -> dict:
    path, start, end, election_doc, track_units, wanted_batches, id_dir, max_entry = args
    election = parse_election(election_doc) if election_doc is not None else None
    contests = election.contest_map if election else {}
    hashes = bytearray()
    out: Dict[str, Any] = {"n": 0, "bad": [], "bad_count": 0, "cvr_count": 0, "cvr_error": None,
                           "read_error": None, "counted": Counter(), "totals": {}, "units": {},
                           "without_unit": 0, "offsets": {}}
    totals: Dict[str, list] = {}
    if election:
        for c in election.contests:
            totals[c.id] = [0, 0, 0, {k: 0 for k in c.candidate_ids}]
    units: Dict[Tuple[str, str], Counter] = {}
    os.makedirs(id_dir, exist_ok=True)
    files: Dict[int, Any] = {}  # bucket files are opened on first use
    stack = ExitStack()  # closes every bucket file opened below, whatever happens

    def bucket(b: int):
        f = files.get(b)
        if f is None:
            f = files[b] = stack.enter_context(
                open(os.path.join(id_dir, f"{b:02x}.jsonl"), "w", encoding="utf-8", buffering=1 << 16))
        return f

    try:
        with open(path, "rb") as fh:
            fh.seek(start)
            pos = start
            while pos < end:
                line = fh.readline(max_entry + 2)
                if not line:
                    break
                line_start = pos
                pos += len(line)
                if not line.endswith(b"\n"):
                    out["read_error"] = (f"log entry exceeds {max_entry} bytes" if len(line) > max_entry
                                         else "log.jsonl is truncated (last entry has no newline)")
                    break
                line = line[:-1]
                i = out["n"]
                out["n"] += 1
                hashes += merkle.leaf_hash(line)
                try:
                    obj = decode_canonical(line)
                    ok = isinstance(obj, dict)
                except (CanonicalEncodingError, RecursionError):
                    obj, ok = None, False
                if not ok:
                    out["bad_count"] += 1
                    if len(out["bad"]) < 10:
                        out["bad"].append(i)
                    continue
                if election is None or out["cvr_error"] is not None or obj.get("type") != "cvr":
                    continue
                k = out["cvr_count"]
                out["cvr_count"] += 1
                try:
                    cvr = parse_cvr(obj["cvr"], election, f"cvrs[{k}]")
                except _MALFORMED as exc:
                    out["cvr_error"] = (k, str(exc))
                    continue
                bucket(hashlib.sha256(cvr.id.encode("utf-8")).digest()[0]).write(json.dumps(cvr.id, ensure_ascii=False) + "\n")
                out["counted"][cvr.batch_id] += 1
                if cvr.batch_id in wanted_batches:
                    out["offsets"].setdefault(cvr.batch_id, []).append(line_start)
                if track_units and cvr.reporting_unit is None:
                    out["without_unit"] += 1
                for contest_id, marks in cvr.selections.items():
                    contest = contests[contest_id]
                    t = totals[contest_id]
                    t[0] += 1
                    if len(marks) > contest.vote_for:
                        t[1] += 1
                        continue
                    t[2] += contest.vote_for - len(marks)
                    cv = t[3]
                    for m in marks:
                        cv[m] += 1
                    if track_units and cvr.reporting_unit is not None and marks:
                        key = (contest_id, cvr.reporting_unit)
                        c = units.get(key)
                        if c is None:
                            c = units[key] = Counter()
                        c.update(marks)
    finally:
        stack.close()
    out["hashes"] = bytes(hashes)
    out["totals"] = totals
    out["units"] = units
    return out


class _SpilledIds:
    """Duplicate counting over bucket files written by several workers."""

    def __init__(self, root: str, dirs: List[str]) -> None:
        self._root = root
        self._dirs = dirs

    def duplicates(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for b in range(256):
            c: Counter = Counter()
            for d in self._dirs:
                p = os.path.join(d, f"{b:02x}.jsonl")
                if os.path.exists(p):
                    with open(p, encoding="utf-8") as fh:
                        c.update(json.loads(line) for line in fh)
            out.update({k: n for k, n in c.items() if n > 1})
        return out

    def close(self) -> None:
        shutil.rmtree(self._root, ignore_errors=True)


def _merge_buckets(src: str, dst: str) -> None:
    """Append one job's bucket files to the shared buckets and delete them (bounded file count)."""
    if not os.path.isdir(src):
        return
    for name in sorted(os.listdir(src)):
        with open(os.path.join(src, name), "rb") as fin, open(os.path.join(dst, name), "ab") as fout:
            shutil.copyfileobj(fin, fout, 1 << 20)
    shutil.rmtree(src, ignore_errors=True)


CHUNK_BYTES = 16 * 1024 * 1024  # bytes of log per job; bounds each job's returned leaf hashes


def _ordered(pool: ProcessPoolExecutor, fn, jobs: List[tuple], window: int) -> Iterator[dict]:
    """Like ``pool.map`` but with at most ``window`` jobs in flight (bounded parent memory)."""
    pending: Deque = deque()
    it = iter(jobs)
    for job in it:
        pending.append(pool.submit(fn, job))
        if len(pending) >= window:
            break
    while pending:
        result = pending.popleft().result()
        nxt = next(it, None)
        if nxt is not None:
            pending.append(pool.submit(fn, nxt))
        yield result


def parallel_scan(path: str, workers: int, head_sizes: Set[int], election_doc: Optional[dict],
                  acc: Optional[recon.CanvassAccumulator], wanted: Set[Tuple[str, int]],
                  tmpdir: Optional[str] = None, chunks_per_worker: int = 4,
                  chunk_bytes: Optional[int] = None):
    """Return a scan result equivalent to the serial ``_scan_log``."""
    from .verify import _Scan  # local import to avoid a cycle

    s = _Scan()
    tree = merkle.CompactRange()
    if 0 in head_sizes:
        s.roots[0] = tree.root()
    size = os.path.getsize(path)
    chunk_bytes = chunk_bytes or CHUNK_BYTES
    ranges = split_ranges(path, max(1, workers * chunks_per_worker, -(-size // max(1, chunk_bytes))))
    root = tempfile.mkdtemp(prefix="eige-scan-", dir=tmpdir)
    wanted_batches = {b for b, _ in wanted}
    track_units = bool(acc and acc.track_units)
    dirs = [os.path.join(root, f"w{k:06d}") for k in range(len(ranges))]
    merged = os.path.join(root, "ids")
    os.makedirs(merged)
    jobs = [(path, a, b, election_doc, track_units, wanted_batches, d, MAX_ENTRY_BYTES)
            for (a, b), d in zip(ranges, dirs)]
    batch_seen: Counter = Counter()
    locate: List[Tuple[str, int, int]] = []  # (batch, global position, byte offset)
    cvr_error_seen = False
    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for k, r in enumerate(_ordered(pool, _worker, jobs, window=2 * workers)):
                _merge_buckets(dirs[k], merged)
                base = s.n
                hb = r["hashes"]
                for off in range(0, len(hb), 32):
                    tree.append(hb[off:off + 32])
                    if tree.size in head_sizes:
                        s.roots[tree.size] = tree.root()
                s.n += r["n"]
                for i in r["bad"]:
                    if len(s.bad) < 10:
                        s.bad.append(base + i)
                s.bad_count += r["bad_count"]
                if r["read_error"]:
                    s.read_error = r["read_error"]
                if not cvr_error_seen:
                    if r["cvr_error"] is not None:
                        k, msg = r["cvr_error"]
                        idx = s.cvr_count + k
                        msg = msg.replace(f"cvrs[{k}]", f"cvrs[{idx}]", 1)
                        s.cvr_error = f"malformed or inconsistent input: {msg}"
                        s.cvr_count += k + 1
                        cvr_error_seen = True
                    else:
                        s.cvr_count += r["cvr_count"]
                if acc is not None and not cvr_error_seen:
                    for batch, offs in r["offsets"].items():
                        prior = batch_seen[batch]
                        for j, off in enumerate(offs):
                            if (batch, prior + j + 1) in wanted:
                                locate.append((batch, prior + j + 1, off))
                    batch_seen.update(r["counted"])
                    acc.counted.update(r["counted"])
                    acc.n += sum(r["counted"].values())
                    acc.cvrs_without_unit += r["without_unit"]
                    for cid, (ballots, over, under, votes) in r["totals"].items():
                        t = acc.totals[cid]
                        t.ballots += ballots
                        t.overvoted_ballots += over
                        t.undervotes += under
                        for cand, v in votes.items():
                            t.candidate_votes[cand] += v
                    for key, c in r["units"].items():
                        acc.unit_votes.setdefault(key, Counter()).update(c)
                if s.read_error:
                    break  # the serial scan stops at the first unreadable entry
        if acc is not None:
            acc.ids.close()
            acc.ids = _SpilledIds(root, [merged])
            root = None  # now owned by the accumulator
            election = acc.election
            with open(path, "rb") as fh:
                for batch, gpos, off in locate:
                    fh.seek(off)
                    obj = decode_canonical(fh.readline()[:-1])
                    s.captured[(batch, gpos)] = parse_cvr(obj["cvr"], election, "sampled cvr")
    finally:
        if root is not None:
            shutil.rmtree(root, ignore_errors=True)
    return s
