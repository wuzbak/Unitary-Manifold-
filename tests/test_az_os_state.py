# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_az_os_state.py — StateDB Persistence Tests

Tests for the SQLite state database using the real StateDB API.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
import json
import pickle
import pytest
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from az_os.state import StateDB, AgentRecord, TaskRecord


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    """A fresh StateDB for each test."""
    return StateDB(tmp_path / "test_state.db")


def _make_task(agent_id="M4", description="test task", status="pending") -> TaskRecord:
    return TaskRecord(
        task_id=str(uuid.uuid4())[:8],
        agent_id=agent_id,
        description=description,
        status=status,
    )


# ── Agent CRUD ─────────────────────────────────────────────────────────────

def test_upsert_and_get_agent(db):
    record = AgentRecord(
        agent_id="M1", manager="M1", role="manager", status="idle", kk_level=0,
    )
    db.upsert_agent(record)
    result = db.get_agent("M1")
    assert result is not None
    assert result.agent_id == "M1"
    assert result.kk_level == 0


def test_upsert_agent_updates_existing(db):
    rec = AgentRecord(agent_id="M3", manager="M3", role="manager", status="idle", kk_level=1)
    db.upsert_agent(rec)
    rec2 = AgentRecord(agent_id="M3", manager="M3", role="manager", status="running", kk_level=1)
    db.upsert_agent(rec2)
    result = db.get_agent("M3")
    assert result.status == "running"


def test_all_agents_empty(db):
    agents = db.all_agents()
    assert isinstance(agents, list)
    assert len(agents) == 0


def test_all_agents_populated(db):
    for i in range(1, 4):
        db.upsert_agent(AgentRecord(
            agent_id=f"M{i}", manager=f"M{i}", role="manager",
            status="idle", kk_level=i - 1
        ))
    agents = db.all_agents()
    assert len(agents) == 3


# ── Task lifecycle ─────────────────────────────────────────────────────────

def test_create_task(db):
    task = _make_task()
    db.create_task(task)
    assert task.task_id is not None
    assert task.status == "pending"


def test_update_task_status(db):
    task = _make_task(agent_id="M4")
    db.create_task(task)
    db.update_task_status(task.task_id, "running")
    # Verify via pending_tasks (running tasks not in pending)
    pending = db.pending_tasks()
    assert not any(t.task_id == task.task_id for t in pending)


def test_update_task_to_done(db):
    task = _make_task(agent_id="M3")
    db.create_task(task)
    db.update_task_status(task.task_id, "done", result={"ok": True})
    # Done tasks are no longer pending
    pending = db.pending_tasks()
    assert not any(t.task_id == task.task_id for t in pending)


def test_list_pending_tasks(db):
    for _ in range(3):
        db.create_task(_make_task(agent_id="M7"))
    pending = db.pending_tasks()
    assert len(pending) >= 3


# ── Checkpoint save/restore ────────────────────────────────────────────────

def test_save_and_load_checkpoint(db):
    payload = {"manager": "M4", "iteration": 5, "results": [1, 2, 3]}
    blob = pickle.dumps(payload)
    db.save_checkpoint("cp_001", "M4", blob)
    loaded_blob = db.load_checkpoint("cp_001")
    assert loaded_blob is not None
    loaded = pickle.loads(loaded_blob)
    assert loaded["manager"] == "M4"
    assert loaded["iteration"] == 5


def test_load_nonexistent_checkpoint_returns_none(db):
    result = db.load_checkpoint("nonexistent_cp")
    assert result is None


def test_checkpoint_overwrite(db):
    blob1 = pickle.dumps({"v": 1})
    blob2 = pickle.dumps({"v": 2})
    db.save_checkpoint("cp_x", "M1", blob1)
    db.save_checkpoint("cp_x", "M1", blob2)
    loaded = pickle.loads(db.load_checkpoint("cp_x"))
    assert loaded["v"] == 2


# ── HILS log ──────────────────────────────────────────────────────────────

def test_log_hils_approved(db):
    db.log_hils(event="APPROVED", action="KERNEL_RING0_ACCESS",
                token_hash="abc123", metadata={"agent": "M7"})
    # No assertion error = success (no public read API, just test no crash)


def test_log_hils_violation(db):
    db.log_hils(event="BLOCKED", action="PILLAR_CANONICALISE",
                token_hash=None, metadata={})


def test_log_hils_multiple_entries(db):
    for i in range(5):
        db.log_hils(event="BLOCKED", action="TEST_DELETE",
                    token_hash=None, metadata={"attempt": i})


# ── φ-debt ledger ─────────────────────────────────────────────────────────

def test_phi_debt_record(db):
    db.record_phi_delta(agent_id="M4", delta=1.5, reason="test_patch_cycle")
    total = db.total_phi_debt("M4")
    assert abs(total - 1.5) < 1e-9


def test_phi_debt_multiple_agents(db):
    db.record_phi_delta("M1", 0.5, "geometry")
    db.record_phi_delta("M2", 0.3, "field")
    assert db.total_phi_debt("M1") == pytest.approx(0.5)
    assert db.total_phi_debt("M2") == pytest.approx(0.3)


def test_total_phi_debt_accumulates(db):
    db.record_phi_delta("M4", 2.0, "patch1")
    db.record_phi_delta("M4", 1.0, "patch2")
    total = db.total_phi_debt("M4")
    assert total >= 3.0


def test_total_phi_debt_zero_for_new_agent(db):
    assert db.total_phi_debt("M_NONEXISTENT") == pytest.approx(0.0)


# ── M4 retry counting ─────────────────────────────────────────────────────

def test_increment_and_check_retry_count(db):
    task = _make_task(agent_id="M4")
    db.create_task(task)
    assert not db.has_exceeded_max_retries(task.task_id)
    for _ in range(5):
        db.increment_retry(task.task_id)
    assert db.has_exceeded_max_retries(task.task_id)


def test_retry_count_starts_at_zero(db):
    task = _make_task(agent_id="M4")
    db.create_task(task)
    assert task.retry_count == 0
