# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from az_weave.memory import ReadOnlyFederation, ScopedMemory


def test_owner_scope_promotion_and_restart(tmp_path):
    database = tmp_path / "private" / "memory.sqlite"
    memory = ScopedMemory(database)
    private = memory.put("alice", "private project note")
    public = memory.put("alice", "shared weave reference", scope="public")

    assert private["status"] == public["status"] == "candidate"
    assert memory.search("bob", "project") == []
    assert memory.search("bob", "weave") == []
    assert memory.promote("alice", private["id"])["scope"] == "private"
    assert memory.search("bob", "project") == []
    assert memory.promote("alice", public["id"])["status"] == "validated"
    assert [record["id"] for record in memory.search("bob", "weave")] == [public["id"]]
    assert ScopedMemory(database).search("alice", "private")[0]["id"] == private["id"]
    assert database.stat().st_mode & 0o777 == 0o600
    assert database.parent.stat().st_mode & 0o777 == 0o700


def test_source_snapshots_survive_and_delete_purges_payload(tmp_path):
    memory = ScopedMemory(tmp_path / "memory.sqlite")
    snapshot = {"source": "docs/TRUTH_LAYER.md", "sha256": "abc", "line": 7}
    secret = "synthetic-secret-payload-" * 100
    record = memory.put("owner", secret + " evidence", sources=[snapshot])
    assert memory.search("owner", "evidence")[0]["sources"] == [snapshot]
    assert memory.delete("owner", record["id"])
    assert not memory.delete("owner", record["id"])
    assert memory.search("owner", "evidence") == []
    with sqlite3.connect(tmp_path / "memory.sqlite") as db:
        assert db.execute("SELECT COUNT(*) FROM memories WHERE id = ?", (record["id"],)).fetchone()[0] == 0
    assert secret.encode() not in (tmp_path / "memory.sqlite").read_bytes()


def test_cross_owner_mutations_and_invalid_inputs_are_rejected(tmp_path):
    memory = ScopedMemory(tmp_path / "memory.sqlite")
    record = memory.put("owner", "owner-only text")
    with pytest.raises(KeyError):
        memory.promote("intruder", record["id"])
    assert not memory.delete("intruder", record["id"])
    with pytest.raises(ValueError):
        memory.put("owner", "x", scope="public-ish")
    with pytest.raises(ValueError):
        memory.put("owner", "x", sources=[{"bad": object()}])
    with pytest.raises(ValueError):
        memory.put("owner", "x" * 100_001)
    with pytest.raises(ValueError):
        memory.search("owner", "query", limit=True)


def test_database_symlink_rejected(tmp_path):
    target = tmp_path / "target.sqlite"
    ScopedMemory(target)
    link = tmp_path / "linked.sqlite"
    link.symlink_to(target)
    with pytest.raises(ValueError):
        ScopedMemory(link)


def test_invalid_payloads_and_no_approval_inferred_from_text(tmp_path):
    memory = ScopedMemory(tmp_path / "memory.sqlite")
    for owner, text in [(None, "text"), ("owner", []), (" " * 2, "text")]:
        with pytest.raises(ValueError):
            memory.put(owner, text)
    with pytest.raises(ValueError):
        memory.put("owner", "text", sources=[{"number": float("nan")}])
    with pytest.raises(ValueError):
        memory.put("owner", "text", scope=[])
    record = memory.put("owner", "approved validated public now", scope="public")
    assert record["status"] == "candidate"
    assert memory.search("other", "approved") == []
    assert memory.search("' OR 1=1 --", "approved") == []


def test_read_only_federation_preserves_lineage_and_never_promotes():
    original = {
        "id": "native-synthetic-id", "owner": "original-author", "status": "approved",
        "source_clock": {"logical": 19}, "lineage": ["parent-id"], "text": "woven archive note",
        "metadata": {"native_entity": "MemoryNode", "unknown_field": [1, 2]},
    }
    view = ReadOnlyFederation([original], owner="importing-owner")
    original["source_clock"]["logical"] = 20
    result = view.search("importing-owner", "woven")[0]
    assert result["payload"]["source_clock"] == {"logical": 19}
    assert result["payload"]["owner"] == "original-author"
    assert result["payload"]["status"] == "approved"
    assert result["status"] == "candidate" and result["scope"] == "private"
    assert result["current"] is False
    assert view.search("another-owner", "woven") == []
    assert not hasattr(view, "promote") and not hasattr(view, "delete")
    with pytest.raises(ValueError):
        ReadOnlyFederation([{"invalid": float("inf")}], owner="owner")


def test_threaded_connections_are_durable(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    memory = ScopedMemory(tmp_path / "memory.sqlite")
    with ThreadPoolExecutor(max_workers=4) as workers:
        records = list(workers.map(
            lambda number: memory.put("owner", f"thread note {number}"), range(12)
        ))
    persisted = ScopedMemory(tmp_path / "memory.sqlite").search("owner", "thread", limit=20)
    assert {record["id"] for record in persisted} == {record["id"] for record in records}
