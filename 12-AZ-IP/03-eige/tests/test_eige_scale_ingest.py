# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""CVR import (NIST SP 1500-103 JSON / JSONL, CSV) and the county operations CLI."""

import json

import pytest

import eige.cvr_import as ci
from eige import county
from eige.cvr_import import CVRImportError, iter_cvr_text, nist_cvr_to_eige
from eige.crypto.signing import DevelopmentSigner, KeyRegistry
from eige.ledger.store import DurableMerkleLog
from eige.model.election import parse_cvr, parse_election
from eige.pipeline import SYNTHETIC_ELECTION
from eige.verify import verify_bundle

ELECTION = parse_election(SYNTHETIC_ELECTION)


def nist_cvr(uid, batch, marks, unit=None, overvotes=0, allocable="yes", snapshots=None, current="s1"):
    contests = []
    for contest_id, sels in marks.items():
        c = {"@type": "CVR.CVRContest", "ContestId": contest_id, "CVRContestSelection": [
            {"@type": "CVR.CVRContestSelection", "ContestSelectionId": s,
             "SelectionPosition": [{"@type": "CVR.SelectionPosition", "HasIndication": "yes", "IsAllocable": allocable,
                                    "NumberVotes": 1}]} for s in sels]}
        if overvotes:
            c["Overvotes"] = overvotes
        contests.append(c)
    d = {"@type": "CVR.CVR", "UniqueId": uid, "BatchId": batch, "BallotStyleId": "1", "CurrentSnapshotId": current,
         "CVRSnapshot": snapshots or [{"@type": "CVR.CVRSnapshot", "@id": "s1", "Type": "original", "CVRContest": contests}]}
    if unit:
        d["BallotStyleUnitId"] = unit
    return d


def report_doc(cvrs, election_first=True, selection_ids=False):
    el = {"@type": "CVR.Election", "Contest": [{"@id": "mayor", "ContestSelection": [
        {"@id": f"sel-{c}", "CandidateIds": [c]} for c in ("alvarez", "brooks", "chen")]}]}
    doc = {"@type": "CVR.CastVoteRecordReport", "Version": "1.0.0"}
    if election_first:
        doc["Election"] = [el]
    doc["CVR"] = cvrs
    doc["GeneratedDate"] = "2026-11-04T00:00:00Z"
    doc["ReportGeneratingDeviceIds"] = ["dev-1", 2, -3.5e2, True, None]
    return json.dumps(doc, indent=1)


@pytest.mark.parametrize("chunk", [1, 3, 7, 64, 1 << 20])
def test_nist_report_streams_identically_at_any_buffer_size(monkeypatch, chunk):
    monkeypatch.setattr(ci, "_CHUNK", chunk)
    docs = [nist_cvr(f"c{i}", "B00", {"mayor": ["sel-alvarez"] if i % 2 else ["sel-brooks"]}, unit="P1") for i in range(6)]
    out = list(iter_cvr_text(report_doc(docs), "nist-json"))
    assert [c["id"] for c in out] == [f"c{i}" for i in range(6)]
    assert out[1]["selections"] == {"mayor": ["alvarez"]}  # selection id translated through Election
    assert out[0]["selections"] == {"mayor": ["brooks"]}
    assert all(c["reporting_unit"] == "P1" for c in out)
    for i, c in enumerate(out):
        parse_cvr(c, ELECTION, f"cvr {i}")


def test_nist_selection_ids_pass_through_without_election_mapping():
    out = list(iter_cvr_text(report_doc([nist_cvr("x", "B00", {"mayor": ["chen"]})], election_first=False), "nist-json"))
    assert out[0]["selections"] == {"mayor": ["chen"]}


def test_non_allocable_marks_are_dropped_but_overvotes_are_kept():
    d = nist_cvr("x", "B", {"mayor": ["alvarez"]}, allocable="no")
    assert nist_cvr_to_eige(d)["selections"] == {"mayor": []}
    d = nist_cvr("y", "B", {"mayor": ["alvarez", "brooks"]}, allocable="no", overvotes=1)
    assert nist_cvr_to_eige(d)["selections"] == {"mayor": ["alvarez", "brooks"]}


def test_current_snapshot_is_used_and_must_exist():
    snaps = [
        {"@id": "orig", "CVRContest": [{"ContestId": "mayor", "CVRContestSelection": [
            {"ContestSelectionId": "alvarez", "SelectionPosition": [{"HasIndication": "yes"}]}]}]},
        {"@id": "adj", "CVRContest": [{"ContestId": "mayor", "CVRContestSelection": [
            {"ContestSelectionId": "brooks", "SelectionPosition": [{"HasIndication": "yes"}]}]}]},
    ]
    assert nist_cvr_to_eige(nist_cvr("x", "B", {}, snapshots=snaps, current="adj"))["selections"] == {"mayor": ["brooks"]}
    with pytest.raises(CVRImportError):
        nist_cvr_to_eige(nist_cvr("x", "B", {}, snapshots=snaps, current="missing"))


@pytest.mark.parametrize("text", [
    "", "[]", '{"@type": "CVR.CastVoteRecordReport"}', '{"@type": "Other", "CVR": []}',
    '{"CVR": [{"@type": "CVR.CVR"} {"x": 1}]}', '{"CVR": [', '{"CVR": [] "x": 1}',
])
def test_malformed_nist_reports_are_rejected(text):
    with pytest.raises(CVRImportError):
        list(iter_cvr_text(text, "nist-json"))


def test_nist_jsonl():
    text = "\n".join(json.dumps(nist_cvr(f"c{i}", "B00", {"mayor": ["alvarez"]})) for i in range(3)) + "\n\n"
    assert [c["id"] for c in iter_cvr_text(text, "nist-jsonl")] == ["c0", "c1", "c2"]
    with pytest.raises(CVRImportError, match="line 2"):
        list(iter_cvr_text('{"@type":"CVR.CVR","CVRSnapshot":[{}]}\n{bad\n', "nist-jsonl"))


def test_csv_with_and_without_reporting_unit():
    text = "cvr_id,batch_id,ballot_style,reporting_unit,mayor,measure-1\r\na,B,1,P1,alvarez,~\r\nb,B,1,P2,,yes|no\r\n"
    out = list(iter_cvr_text(text, "csv"))
    assert out[0] == {"id": "a", "batch_id": "B", "ballot_style": "1", "selections": {"mayor": ["alvarez"]}, "reporting_unit": "P1"}
    assert out[1]["selections"] == {"mayor": [], "measure-1": ["yes", "no"]}
    out = list(iter_cvr_text("cvr_id,batch_id,ballot_style,mayor\nz,B,1,chen\n", "csv"))
    assert out == [{"id": "z", "batch_id": "B", "ballot_style": "1", "selections": {"mayor": ["chen"]}}]


@pytest.mark.parametrize("text", [
    "", "id,batch,style,mayor\n", "cvr_id,batch_id,ballot_style\n", "cvr_id,batch_id,ballot_style,mayor,mayor\n",
    "cvr_id,batch_id,ballot_style,mayor\na,B,1\n", "cvr_id,batch_id,ballot_style,mayor\na,B,1,alvarez||brooks\n",
])
def test_malformed_csv_is_rejected(text):
    with pytest.raises(CVRImportError):
        list(iter_cvr_text(text, "csv"))


# ---------------------------------------------------------------- county CLI
CSV_HEADER = "cvr_id,batch_id,ballot_style,reporting_unit,mayor,measure-1\n"
MANIFEST = {"jurisdiction": "SYNTH-COUNTY", "batches": [
    {"batch_id": "B00", "ballot_count": 3, "container_id": "BOX-0", "tabulator_id": "T"},
    {"batch_id": "B01", "ballot_count": 2, "container_id": "BOX-1", "tabulator_id": "T"}]}


@pytest.fixture
def county_dir(tmp_path):
    (tmp_path / "election.json").write_text(json.dumps(SYNTHETIC_ELECTION))
    (tmp_path / "manifest.json").write_text(json.dumps(MANIFEST))
    (tmp_path / "dev.key").write_text("11" * 32)
    (tmp_path / "a.csv").write_text(CSV_HEADER + "a1,B00,1,P1,alvarez,yes\na2,B00,1,P1,brooks,no\na3,B00,1,P2,alvarez,~\n")
    (tmp_path / "b.csv").write_text(CSV_HEADER + "b1,B01,1,P2,chen,yes\nb2,B01,1,P2,,no\n")
    return tmp_path


def run(capsys, *argv):
    rc = county.main([str(a) for a in argv])
    cap = capsys.readouterr()
    return rc, (json.loads(cap.out) if cap.out.strip() else None), cap.err


def test_county_end_to_end_bundle_verifies(county_dir, capsys):
    d = county_dir
    db = d / "county.db"
    assert run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")[0] == 0
    assert run(capsys, "commit-manifest", db, "--manifest", d / "manifest.json")[0] == 0
    rc, out, _ = run(capsys, "ingest", db, "--election", d / "election.json", "--manifest", d / "manifest.json",
                     "--cvrs", d / "a.csv", d / "b.csv", "--format", "csv", "--require-reporting-unit")
    assert rc == 0 and [f["logged"] for f in out["files"]] == [True, True]
    assert out["size"] == 1 + (1 + 3) + (1 + 2)  # manifest + provenance records + CVRs
    rc, _, err = run(capsys, "export", db, "--out", d / "bundle")
    assert rc == 2 and "no signed tree head" in err
    assert run(capsys, "sign-head", db, "--timestamp", 1000, "--dev-key-file", d / "dev.key")[0] == 0
    rc, out, _ = run(capsys, "results", db, "--election", d / "election.json", "--out", d / "results.json", "--by-reporting-unit")
    assert rc == 0
    reg = KeyRegistry()
    reg.register_signer(DevelopmentSigner(bytes.fromhex("11" * 32)), owner="SYNTH-COUNTY", role="county-log", valid_from=0)
    (d / "registry.json").write_text(json.dumps(reg.as_dict()))
    rc, out, _ = run(capsys, "export", db, "--out", d / "bundle", "--file", f"registry.json={d / 'registry.json'}",
                     "--file", f"election.json={d / 'election.json'}", "--file", f"manifest.json={d / 'manifest.json'}",
                     "--file", f"results.json={d / 'results.json'}")
    assert rc == 0
    report = verify_bundle(str(d / "bundle"))
    assert report.passed, [c.detail for c in report.by_status("failed")]
    names = {c.check: c.status for c in report.checks}
    assert names["Canvass reconciliation"] == "verified"
    assert "Reporting-unit (precinct) results" not in names  # unit-level results were published and checked
    rc, out, _ = run(capsys, "status", db, "--check-integrity")
    assert rc == 0 and out["integrity"] == "ok" and out["size"] == 8


def test_ingest_is_all_or_nothing_and_never_logs_a_cvr_twice(county_dir, capsys):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    base = ["ingest", db, "--election", d / "election.json", "--manifest", d / "manifest.json", "--format", "csv"]
    assert run(capsys, *base, "--cvrs", d / "a.csv")[0] == 0
    rc, out, _ = run(capsys, *base, "--cvrs", d / "a.csv")  # same export again
    assert rc == 1 and out["size"] == 4 and not out["files"][0]["logged"]
    assert sum("already in the log" in e for e in out["files"][0]["errors"]) == 3
    bad = d / "bad.csv"
    bad.write_text(CSV_HEADER + "x1,B01,1,P1,alvarez,yes\nx2,B99,1,P1,alvarez,yes\nx3,B01,1,P1,nobody,yes\n"
                   "x1,B01,1,P1,brooks,no\nx4,B01,1,P1,alvarez|brooks|chen|alvarez,yes\n")
    rc, out, _ = run(capsys, *base, "--cvrs", bad)
    errors = " ".join(out["files"][0]["errors"])
    assert rc == 1 and out["size"] == 4
    assert "B99" in errors and "nobody" in errors and "'x1' appears 2 times" in errors
    with DurableMerkleLog(db) as log:
        assert not log.has_key("cvr:x1")


def test_ingest_requires_reporting_unit_when_asked(county_dir, capsys):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    f = d / "nounit.csv"
    f.write_text("cvr_id,batch_id,ballot_style,mayor\nq,B00,1,alvarez\n")
    rc, out, _ = run(capsys, "ingest", db, "--election", d / "election.json", "--cvrs", f, "--format", "csv",
                     "--require-reporting-unit")
    assert rc == 1 and "no reporting_unit" in out["files"][0]["errors"][0]


def test_dev_key_signing_refused_in_production(county_dir, capsys, monkeypatch):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    monkeypatch.setenv("EIGE_MODE", "production")
    rc, _, err = run(capsys, "sign-head", db, "--timestamp", 1, "--dev-key-file", d / "dev.key")
    assert rc == 2 and "production" in err
    rc, _, err = run(capsys, "sign-head", db, "--timestamp", 1, "--pkcs11-lib", "/nonexistent.so", "--token", "t", "--key-label", "k")
    assert rc == 2 and "EIGE_PKCS11_PIN" in err


def test_init_refuses_existing_database_and_commands_require_init(county_dir, capsys):
    d = county_dir
    db = d / "county.db"
    assert run(capsys, "status", db)[0] == 2
    run(capsys, "init", db, "--log-id", "X")
    assert run(capsys, "init", db, "--log-id", "X")[0] == 2
    assert run(capsys, "event", db, "--type", "cvr")[0] == 2


def test_export_refuses_unsigned_tail(county_dir, capsys):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    run(capsys, "commit-manifest", db, "--manifest", d / "manifest.json")
    run(capsys, "sign-head", db, "--timestamp", 5, "--dev-key-file", d / "dev.key")
    (d / "ev.json").write_text('{"seal": "S-1"}')
    run(capsys, "event", db, "--type", "chain_of_custody", "--details", d / "ev.json")
    rc, _, err = run(capsys, "export", db, "--out", d / "bundle")
    assert rc == 2 and "after the last signed head" in err


def test_interrupted_ingest_leaves_the_log_unchanged_and_can_be_retried(county_dir, capsys, monkeypatch):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    real = county.iter_cvr_file
    calls = {"n": 0}

    def flaky(path, fmt):
        calls["n"] += 1
        for i, item in enumerate(real(path, fmt)):
            if calls["n"] == 2 and i == 2:  # second (writing) pass dies part-way
                raise OSError("disk read error")
            yield item

    monkeypatch.setattr(county, "iter_cvr_file", flaky)
    election = parse_election(SYNTHETIC_ELECTION)
    with DurableMerkleLog(db) as log:
        with pytest.raises(OSError):
            county.ingest_file(log, election, d / "a.csv", "csv", batch_size=1)
        assert log.size == 0
        monkeypatch.setattr(county, "iter_cvr_file", real)
        rep = county.ingest_file(log, election, d / "a.csv", "csv", batch_size=1)
        assert rep.logged and log.size == 4


def test_export_changed_during_ingest_is_not_logged(county_dir, capsys, monkeypatch):
    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    real = county._sha256_file
    calls = {"n": 0}

    def changing(path):
        calls["n"] += 1
        return real(path) if calls["n"] == 1 else "0" * 64

    monkeypatch.setattr(county, "_sha256_file", changing)
    with DurableMerkleLog(db) as log:
        with pytest.raises(county.CountyError, match="changed while it was being ingested"):
            county.ingest_file(log, parse_election(SYNTHETIC_ELECTION), d / "a.csv", "csv")
        assert log.size == 0 and not log.has_key("cvr:a1")


def test_edited_database_blocks_status_signing_and_export(county_dir, capsys):
    import sqlite3

    d = county_dir
    db = d / "county.db"
    run(capsys, "init", db, "--log-id", "SYNTH-COUNTY")
    run(capsys, "ingest", db, "--election", d / "election.json", "--cvrs", d / "a.csv", "--format", "csv")
    run(capsys, "sign-head", db, "--timestamp", 10, "--dev-key-file", d / "dev.key")
    conn = sqlite3.connect(db)
    conn.execute("UPDATE leaves SET data=? WHERE idx=2", (b'{"type":"cvr","cvr":{"id":"forged"}}',))
    conn.commit()
    conn.close()
    rc, _, err = run(capsys, "status", db, "--check-integrity")
    assert rc == 2 and "leaf 2" in err
    rc, _, err = run(capsys, "sign-head", db, "--timestamp", 11, "--dev-key-file", d / "dev.key")
    assert rc == 2 and "integrity check failed" in err
    rc, _, err = run(capsys, "export", db, "--out", d / "bundle")
    assert rc == 2 and "integrity check failed" in err
