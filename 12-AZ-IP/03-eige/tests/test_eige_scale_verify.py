# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Streaming/parallel verification, precinct results, multi-contest audits, statewide roll-up."""

import json
import tracemalloc
from pathlib import Path

import pytest

from eige.audit import rla
from eige.bundle import read_bundle
from eige.canonical import CanonicalEncodingError, canonical_bytes, decode_canonical
from eige.dedup import DuplicateDetector
from eige.model.election import parse_election, parse_manifest
from eige.parallel_scan import split_ranges
from eige.pipeline import SYNTHETIC_ELECTION, build_synthetic_bundle
from eige.statewide import verify_state
from eige.synthetic_scale import build_county
from eige.verify import verify_bundle, verify_bundle_data


def failed(report):
    return {c.check: c.detail for c in report.checks if c.status == "failed"}


def status(report, check):
    return next(c.status for c in report.checks if c.check == check)


# ----------------------------------------------------------------- building blocks
@pytest.mark.parametrize("limit", [10, 1_000_000])
def test_duplicate_detector_is_exact_in_memory_and_when_spilled(tmp_path, limit):
    with DuplicateDetector(memory_limit=limit, tmpdir=str(tmp_path)) as d:
        for i in range(500):
            d.add(f"id-{i}")
        for i in (3, 3, 77, 499):
            d.add(f"id-{i}")
        assert d.spilled == (limit == 10)
        assert d.duplicates() == {"id-3": 3, "id-77": 2, "id-499": 2}


def test_decode_canonical_accepts_only_canonical_text():
    obj = {"a": [1, -2, "x\u00e9"], "b": {"c": None, "d": True}}
    assert decode_canonical(canonical_bytes(obj)) == obj
    for bad in [b'{"b":1,"a":2}', b'{"a": 1}', b'{"a":1.0}', b'{"a":1e3}', b'{"a":-0}', b'{"a":NaN}',
                b'{"a":1,"a":1}', b'{"a":"\\u00e9"}', b'{"a":"\\/"}', b'\xff', b'{"a":1}\n']:
        with pytest.raises(CanonicalEncodingError):
            decode_canonical(bad)


def test_manifest_locate_skips_zero_count_batches():
    m = parse_manifest({"jurisdiction": "J", "batches": [
        {"batch_id": "A", "ballot_count": 2, "container_id": "a", "tabulator_id": "t"},
        {"batch_id": "Z", "ballot_count": 0, "container_id": "z", "tabulator_id": "t"},
        {"batch_id": "B", "ballot_count": 3, "container_id": "b", "tabulator_id": "t"}]})
    assert [m.locate(p) for p in range(1, 6)] == [("A", 1), ("A", 2), ("B", 1), ("B", 2), ("B", 3)]
    with pytest.raises(Exception):
        m.locate(6)


def test_missing_ballot_or_cvr_counts_as_worst_case_overstatement():
    election = parse_election(SYNTHETIC_ELECTION)
    mayor = election.contest("mayor")
    a = rla.plurality_assertions(mayor, {"alvarez": 60, "brooks": 30, "chen": 10}, 100)
    assert rla.overstatement(a, rla.CVR_NOT_FOUND, rla.BALLOT_NOT_FOUND) == 2
    # a lost ballot or missing CVR can never confirm an outcome on its own
    res = rla.comparison_audit(mayor, {"alvarez": 60, "brooks": 30, "chen": 10}, 100,
                               [(rla.CVR_NOT_FOUND, rla.BALLOT_NOT_FOUND)] * 20, 0.05)
    assert not res.confirmed


def test_split_ranges_cover_the_file_on_line_boundaries(tmp_path):
    p = tmp_path / "log.jsonl"
    lines = [b'{"i":%d,"pad":"%s"}\n' % (i, b"x" * (i % 17)) for i in range(301)]
    p.write_bytes(b"".join(lines))
    for parts in (1, 2, 3, 7, 50, 500):
        ranges = split_ranges(str(p), parts)
        data = p.read_bytes()
        assert ranges[0][0] == 0 and ranges[-1][1] == len(data)
        assert all(a[1] == b[0] for a, b in zip(ranges, ranges[1:]))
        assert all(s == 0 or data[s - 1:s] == b"\n" for s, _ in ranges)


# ------------------------------------------------- streaming == in-memory == parallel
def _stuff(state):
    state["entries"].append(canonical_bytes({"type": "cvr", "cvr": {"id": "EXTRA", "batch_id": "B00", "ballot_style": "1",
                                                                    "selections": {"mayor": ["alvarez"], "measure-1": ["yes"]}}}))


def _non_canonical(state):
    state["entries"][5] = state["entries"][5].replace(b'"type":"cvr"', b'"type": "cvr"')


def _bad_candidate(state):
    before = state["entries"][9]
    state["entries"][9] = before.replace(b'"measure-1":["no"]', b'"measure-1":["mallory"]').replace(b'"measure-1":["yes"]', b'"measure-1":["mallory"]')
    assert state["entries"][9] != before


def _dup_id(state):
    state["entries"][300] = state["entries"][301]


TAMPERS = {"clean": None, "stuffing": _stuff, "non_canonical": _non_canonical,
           "bad_candidate": _bad_candidate, "duplicate_id": _dup_id}


@pytest.mark.parametrize("name", sorted(TAMPERS))
def test_serial_parallel_and_in_memory_reports_are_identical(tmp_path, name):
    d = tmp_path / name
    build_synthetic_bundle(d, tamper=TAMPERS[name])
    serial = verify_bundle(str(d)).as_dict()
    assert serial["passed"] == (name == "clean")
    for workers in (2, 3):
        assert verify_bundle(str(d), workers=workers).as_dict() == serial
    assert verify_bundle_data(read_bundle(d)).as_dict() == serial
    assert verify_bundle(str(d), dedup_memory_limit=5).as_dict() == serial
    if name == "duplicate_id":
        assert any("DUPLICATE_CVR_ID" in k for k in failed(verify_bundle(str(d))))


def test_parallel_scan_with_many_small_chunks_matches_serial(tmp_path, monkeypatch):
    import eige.parallel_scan as ps

    d = tmp_path / "b"
    build_synthetic_bundle(d, tamper=_dup_id)
    serial = verify_bundle(str(d)).as_dict()
    monkeypatch.setattr(ps, "CHUNK_BYTES", 2048)  # ~100 jobs, at most 2 × workers in flight
    assert verify_bundle(str(d), workers=2).as_dict() == serial


def test_truncated_log_is_reported_identically_serial_and_parallel(tmp_path):
    d = tmp_path / "b"
    build_synthetic_bundle(d)
    log = d / "log.jsonl"
    log.write_bytes(log.read_bytes()[:-30])
    serial = verify_bundle(str(d))
    assert "Log file readable" in failed(serial)
    assert verify_bundle(str(d), workers=3).as_dict() == serial.as_dict()


# ------------------------------------------- full-population features (scale generator)
@pytest.fixture(scope="module")
def county(tmp_path_factory):
    d = tmp_path_factory.mktemp("county") / "bundle"
    info = build_county(d, 4000, n_contests=4, n_units=12, batch_size=300, seed="t")
    return d, info


def _copy(src: Path, dst: Path) -> Path:
    dst.mkdir(parents=True)
    for f in src.iterdir():
        (dst / f.name).write_bytes(f.read_bytes())
    return dst


def test_generated_county_verifies_every_contest_and_precinct(county):
    d, info = county
    report = verify_bundle(str(d))
    assert report.passed, failed(report)
    audits = [c for c in report.checks if c.check.startswith("Risk-limiting audit of ")]
    assert len(audits) == 4 and all(c.status == "verified" for c in audits)
    assert "Reporting-unit (precinct) results" not in {c.check for c in report.checks}
    assert verify_bundle(str(d), workers=3).as_dict() == report.as_dict()


def test_votes_moved_between_precincts_are_detected_even_when_totals_match(county, tmp_path):
    d = _copy(county[0], tmp_path / "moved")
    res = json.loads((d / "results.json").read_text())
    counts = res["Contest"][0]["ContestSelection"][0]["VoteCounts"]
    counts[0]["Count"] += 5
    counts[1]["Count"] -= 5  # contest total unchanged
    (d / "results.json").write_text(json.dumps(res))
    report = verify_bundle(str(d))
    rows = [k for k in failed(report) if "REPORTED_UNIT_TOTAL_MISMATCH" in k]
    assert len(rows) == 2  # both precincts are named


def test_v2_audit_fails_only_the_contest_whose_paper_disagrees(county, tmp_path):
    d = _copy(county[0], tmp_path / "audit")
    audit = json.loads((d / "audit.json").read_text())
    for m in audit["mvrs"][:6]:
        sel = m["selections"]
        sel["c01"] = ["c"] if sel["c01"] != ["c"] else ["b"]
    (d / "audit.json").write_text(json.dumps(audit))
    report = verify_bundle(str(d))
    statuses = {c.check: c.status for c in report.checks if c.check.startswith("Risk-limiting audit of ")}
    assert statuses["Risk-limiting audit of c01"] == "failed"
    assert statuses["Risk-limiting audit of c00"] == "verified"


def test_lost_ballots_cannot_confirm_an_outcome(county, tmp_path):
    d = _copy(county[0], tmp_path / "lost")
    audit = json.loads((d / "audit.json").read_text())
    for m in audit["mvrs"]:
        m["selections"] = None
    (d / "audit.json").write_text(json.dumps(audit))
    report = verify_bundle(str(d))
    statuses = [c.status for c in report.checks if c.check.startswith("Risk-limiting audit of ")]
    assert statuses and all(s == "failed" for s in statuses)


def test_audited_draw_must_be_in_the_published_sample(county, tmp_path):
    d = _copy(county[0], tmp_path / "draw")
    audit = json.loads((d / "audit.json").read_text())
    audit["mvrs"][0]["draw"] = 10_000
    (d / "audit.json").write_text(json.dumps(audit))
    assert "not in the published sample" in failed(verify_bundle(str(d)))["Risk-limiting audit of c00"]


# ------------------------------------------------------------------ statewide
@pytest.fixture(scope="module")
def counties(tmp_path_factory):
    base = tmp_path_factory.mktemp("state")
    dirs = []
    for i, j in enumerate(("ADAMS", "BAKER", "CLARK")):
        d = base / j
        build_county(d, 1500 + 250 * i, n_contests=3, n_units=5, batch_size=250, seed=j, jurisdiction=j)
        dirs.append(d)
    return dirs


def _state_doc(dirs):
    sels = {}
    for d in dirs:
        res = json.loads((d / "results.json").read_text())
        for con in res["Contest"]:
            for s in con["ContestSelection"]:
                sels.setdefault(con["@id"], {}).setdefault(s["CandidateId"], []).append(
                    {"Count": sum(v["Count"] for v in s["VoteCounts"]), "GpUnitId": res["Jurisdiction"]})
    return {"Jurisdiction": "STATE", "Contest": [
        {"@id": c, "ContestSelection": [{"CandidateId": k, "VoteCounts": v} for k, v in sorted(cs.items())]}
        for c, cs in sorted(sels.items())]}


def test_statewide_rollup_verifies(counties):
    report, per_county = verify_state(counties, _state_doc(counties), workers=3)
    assert report.passed, failed(report)
    assert status(report, "State totals equal the sum of county results") == "verified"
    assert len(per_county) == 3


def test_statewide_detects_altered_county_figure_and_bad_sum(counties):
    doc = _state_doc(counties)
    doc["Contest"][0]["ContestSelection"][0]["VoteCounts"][1]["Count"] += 7
    report, _ = verify_state(counties, doc)
    detail = failed(report)["State totals equal the sum of county results"]
    assert "BAKER" in detail and "!= sum of county results" in detail


def test_statewide_detects_missing_and_repeated_counties(counties):
    report, _ = verify_state(counties[:2] + [counties[0]], _state_doc(counties))
    f = failed(report)
    assert "repeated jurisdiction: ADAMS" in f["Counties are distinct"]
    assert "CLARK" in f["State totals equal the sum of county results"]
    report, _ = verify_state(counties, _state_doc(counties[:2]))
    assert "missing from the state roll-up: CLARK" in failed(report)["State totals equal the sum of county results"]


def test_statewide_fails_when_any_county_fails(counties, tmp_path):
    bad = _copy(counties[1], tmp_path / "BAKER")
    log = bad / "log.jsonl"
    lines = log.read_bytes().splitlines(keepends=True)
    log.write_bytes(b"".join(lines[:-1]))  # drop a logged CVR
    report, _ = verify_state([counties[0], bad, counties[2]], None)
    assert not report.passed
    assert "County bundle BAKER" in failed(report)
    assert status(report, "State totals equal the sum of county results") == "not_checked"


# ------------------------------------------------------------------- scale
@pytest.mark.slow
def test_verification_memory_is_bounded_at_scale(tmp_path):
    """200k ballots × 5 contests: peak traced memory stays far below the log size."""
    d = tmp_path / "big"
    build_county(d, 200_000, n_contests=5, n_units=100, batch_size=1000, seed="big")
    log_bytes = (d / "log.jsonl").stat().st_size
    tracemalloc.start()
    report = verify_bundle(str(d), dedup_memory_limit=20_000, tmpdir=str(tmp_path))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert report.passed, failed(report)
    assert log_bytes > 30 * 2**20
    assert peak < 32 * 2**20, f"peak {peak / 2**20:.1f} MiB"
    assert verify_bundle(str(d), workers=4).as_dict() == report.as_dict()
