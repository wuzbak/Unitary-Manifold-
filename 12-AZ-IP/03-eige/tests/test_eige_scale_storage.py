# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Scale storage: levelled Merkle tree, compact range and the durable SQLite log."""

import hashlib
import sqlite3

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from eige.crypto import merkle
from eige.crypto.signing import DevelopmentSigner
from eige.ledger.log import LogError, MerkleLog
from eige.ledger.store import DurableMerkleLog
from eige.verify import verify_bundle


def _ref_root(hashes):
    """RFC 9162 §2.1.1 MTH, written recursively as in the RFC (reference only)."""
    n = len(hashes)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return hashes[0]
    k = 1
    while k * 2 < n:
        k *= 2
    return merkle.node_hash(_ref_root(hashes[:k]), _ref_root(hashes[k:]))


def _leaves(n):
    return [merkle.leaf_hash(f"entry {i}".encode()) for i in range(n)]


@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=0, max_value=130))
def test_compact_range_and_levelled_tree_match_rfc_reference(n):
    hashes = _leaves(n)
    acc = merkle.CompactRange()
    tree = merkle.LevelledTree()
    for h in hashes:
        acc.append(h)
        tree.append(h)
    assert acc.size == n
    assert acc.root() == _ref_root(hashes)
    for m in range(n + 1):
        assert tree.root(m) == _ref_root(hashes[:m])


@settings(max_examples=40, deadline=None)
@given(st.integers(min_value=1, max_value=70), st.data())
def test_levelled_tree_proofs_verify_for_every_prefix(n, data):
    hashes = _leaves(n)
    tree = merkle.LevelledTree()
    for h in hashes:
        tree.append(h)
    size = data.draw(st.integers(min_value=1, max_value=n))
    idx = data.draw(st.integers(min_value=0, max_value=size - 1))
    root = tree.root(size)
    assert merkle.verify_inclusion(hashes[idx], idx, size, tree.inclusion_proof(idx, size), root)
    old = data.draw(st.integers(min_value=1, max_value=size))
    assert merkle.verify_consistency(old, size, tree.root(old), root, tree.consistency_proof(old, size))
    # a wrong leaf never verifies
    assert not merkle.verify_inclusion(merkle.leaf_hash(b"forged"), idx, size, tree.inclusion_proof(idx, size), root)


def test_levelled_tree_rejects_out_of_range_requests():
    tree = merkle.LevelledTree()
    for h in _leaves(5):
        tree.append(h)
    with pytest.raises(merkle.ProofError):
        tree.root(6)
    with pytest.raises(merkle.ProofError):
        tree.inclusion_proof(5, 5)
    with pytest.raises(merkle.ProofError):
        tree.consistency_proof(6, 5)


def _records(n, start=0):
    return [{"type": "cvr", "cvr": {"id": f"C{i}", "batch_id": "B", "ballot_style": "1", "selections": {}}}
            for i in range(start, start + n)]


def test_durable_log_matches_in_memory_log_and_survives_reopen(tmp_path):
    db = tmp_path / "log.db"
    mem = MerkleLog("L")
    with DurableMerkleLog(db, "L") as log:
        log.append_many(_records(37), batch_size=8)
        for r in _records(37):
            mem.append(r)
        assert log.root() == mem.root()
        assert log.entries() == mem.entries()
    with DurableMerkleLog(db) as log:  # reopen, log id read from the file
        assert log.log_id == "L" and log.size == 37
        log.append_many(_records(30, start=37), batch_size=7)
        for r in _records(30, start=37):
            mem.append(r)
        assert log.root() == mem.root()
        for m in (1, 13, 37, 67):
            assert log.root(m) == mem.root(m)
        assert log.inclusion_proof(20, 50) == mem.inclusion_proof(20, 50)
        assert log.consistency_proof(37, 67) == mem.consistency_proof(37, 67)
        assert log.check_integrity() == []


def test_durable_log_refuses_a_different_log_id(tmp_path):
    db = tmp_path / "log.db"
    DurableMerkleLog(db, "A").close()
    with pytest.raises(LogError):
        DurableMerkleLog(db, "B")


def test_unique_key_violation_rolls_back_the_whole_batch(tmp_path):
    key = lambda r: "cvr:" + r["cvr"]["id"]  # noqa: E731
    with DurableMerkleLog(tmp_path / "log.db", "L") as log:
        log.append_many(_records(5), unique_key=key)
        root = log.root()
        with pytest.raises(LogError, match="already in the log"):
            log.append_many(_records(3, start=10) + _records(1, start=2), batch_size=100, unique_key=key)
        assert log.size == 5 and log.root() == root
        assert not log.has_key("cvr:C10")
        # the tree still accepts appends after the rollback
        log.append_many(_records(3, start=10), unique_key=key)
        assert log.size == 8 and log.check_integrity() == []


def test_integrity_check_detects_edited_leaf_bytes(tmp_path):
    db = tmp_path / "log.db"
    with DurableMerkleLog(db, "L") as log:
        log.append_many(_records(20))
        log.sign_head(DevelopmentSigner(b"\x01" * 32), 100)
    conn = sqlite3.connect(db)
    conn.execute("UPDATE leaves SET data=? WHERE idx=7", (b'{"type":"cvr","cvr":{}}',))
    conn.commit()
    conn.close()
    with DurableMerkleLog(db) as log:
        problems = log.check_integrity()
    assert any("leaf 7" in p for p in problems)


def test_head_timestamps_must_not_go_backwards(tmp_path):
    signer = DevelopmentSigner(b"\x02" * 32)
    with DurableMerkleLog(tmp_path / "log.db", "L") as log:
        log.append_many(_records(3))
        log.sign_head(signer, 200)
        with pytest.raises(LogError):
            log.sign_head(signer, 199)
        assert [h.tree_size for h in log.heads()] == [3]


def test_durable_log_exports_a_bundle_that_verifies(tmp_path):
    from eige.pipeline import build_synthetic_bundle

    state = build_synthetic_bundle(tmp_path / "ref")
    signer = state["signers"]["county"]
    with DurableMerkleLog(tmp_path / "log.db", "SYNTH-COUNTY") as log:
        log.append_encoded(state["entries"])
        log.sign_head(signer, 1_793_710_000)
        files = {k: v for k, v in state["files"].items() if k not in ("heads.json", "cosignatures.json", "sample.json", "audit.json")}
        log.export_bundle(tmp_path / "out", files)
    report = verify_bundle(str(tmp_path / "out"))
    assert report.passed, [c.detail for c in report.by_status("failed")]


def test_failed_commit_restores_tree_even_if_sqlite_already_rolled_back(tmp_path):
    with DurableMerkleLog(tmp_path / "log.db", "L") as log:
        log.append_many(_records(4))
        root = log.root()

        def sqlite_gave_up():
            log._conn.execute("ROLLBACK")  # as SQLite does itself on SQLITE_FULL / SQLITE_IOERR
            raise sqlite3.OperationalError("database or disk is full")

        with pytest.raises(sqlite3.OperationalError):
            log.append_many(_records(6, start=4), atomic=True, before_commit=sqlite_gave_up)
        assert log.size == 4 and log.root() == root
        log.append_many(_records(6, start=4), batch_size=4)
        mem = MerkleLog("L")
        for r in _records(10):
            mem.append(r)
        assert log.root() == mem.root() and log.check_integrity() == []


def test_atomic_append_commits_nothing_when_the_input_fails_part_way(tmp_path):
    def records():
        yield from _records(25)
        raise OSError("export unreadable")

    with DurableMerkleLog(tmp_path / "log.db", "L") as log:
        log.append_many(_records(2, start=100))
        with pytest.raises(OSError):
            log.append_many(records(), batch_size=4, atomic=True)
        assert log.size == 2
    with DurableMerkleLog(tmp_path / "log.db") as log:
        assert log.size == 2 and log.check_integrity() == []
