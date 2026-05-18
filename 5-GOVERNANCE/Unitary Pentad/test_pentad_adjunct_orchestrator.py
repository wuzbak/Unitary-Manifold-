# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_pentad_adjunct_orchestrator.py
====================================
Tests for Sprint D — Adjunct Orchestration layer.
"""

from __future__ import annotations

import pytest

from pentad_adjunct_orchestrator import (
    TaskStatus,
    TASK_STATUSES,
    AdjunctTask,
    VerificationResult,
    AdjunctOrchestrator,
    default_local_verifier,
    strict_local_verifier,
    make_research_task,
    make_batch_task,
    make_model_task,
)
from pentad_cloud_adjunct import (
    CloudAdjunctDecision,
    CloudAdjunctRole,
    default_cloud_adjunct_policy,
)
from five_cores.five_cores_system import FiveCoresSystem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def system() -> FiveCoresSystem:
    """A default five-cores system with full trust."""
    return FiveCoresSystem(phi_trust=1.0)


@pytest.fixture()
def orchestrator(system: FiveCoresSystem) -> AdjunctOrchestrator:
    """A default orchestrator backed by the default system."""
    return AdjunctOrchestrator(system)


# ---------------------------------------------------------------------------
# TaskStatus constants
# ---------------------------------------------------------------------------

class TestTaskStatus:
    def test_queued_exists(self):
        assert TaskStatus.QUEUED == "queued"

    def test_routing_exists(self):
        assert TaskStatus.ROUTING == "routing"

    def test_dispatched_exists(self):
        assert TaskStatus.DISPATCHED == "dispatched"

    def test_awaiting_verification_exists(self):
        assert TaskStatus.AWAITING_VERIFICATION == "awaiting_verification"

    def test_verified_exists(self):
        assert TaskStatus.VERIFIED == "verified"

    def test_rejected_by_policy_exists(self):
        assert TaskStatus.REJECTED_BY_POLICY == "rejected_by_policy"

    def test_verification_failed_exists(self):
        assert TaskStatus.VERIFICATION_FAILED == "verification_failed"

    def test_completed_exists(self):
        assert TaskStatus.COMPLETED == "completed"

    def test_failed_exists(self):
        assert TaskStatus.FAILED == "failed"

    def test_task_statuses_tuple_has_all(self):
        expected = {
            "queued", "routing", "dispatched", "awaiting_verification",
            "verified", "rejected_by_policy", "verification_failed",
            "completed", "failed",
        }
        assert set(TASK_STATUSES) == expected


# ---------------------------------------------------------------------------
# AdjunctTask creation
# ---------------------------------------------------------------------------

class TestAdjunctTask:
    def test_minimal_creation(self):
        task = AdjunctTask(
            task_id="abc",
            role=CloudAdjunctRole.TRUTH_QUERY,
            description="Test task",
        )
        assert task.task_id == "abc"
        assert task.role == CloudAdjunctRole.TRUTH_QUERY
        assert task.status == TaskStatus.QUEUED
        assert task.criticality == 0.5
        assert task.payload == {}
        assert task.decision is None
        assert task.result is None
        assert task.error == ""

    def test_custom_criticality(self):
        task = AdjunctTask(
            task_id="xyz",
            role=CloudAdjunctRole.BATCH_COMPUTE,
            description="Batch job",
            criticality=0.9,
        )
        assert task.criticality == 0.9

    def test_payload_defaults_to_empty_dict(self):
        t1 = AdjunctTask(task_id="t1", role=CloudAdjunctRole.ARCHIVE, description="a")
        t2 = AdjunctTask(task_id="t2", role=CloudAdjunctRole.ARCHIVE, description="b")
        # Each instance gets its own dict
        assert t1.payload is not t2.payload


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.submit
# ---------------------------------------------------------------------------

class TestSubmit:
    def test_returns_string_task_id(self, orchestrator):
        task = make_research_task("Test query")
        tid = orchestrator.submit(task)
        assert isinstance(tid, str)
        assert len(tid) > 0

    def test_task_id_matches_task(self, orchestrator):
        task = make_research_task("Query")
        tid = orchestrator.submit(task)
        assert tid == task.task_id

    def test_submit_resets_status_to_queued(self, orchestrator):
        task = make_research_task("Query")
        task.status = TaskStatus.FAILED  # simulate dirty state
        orchestrator.submit(task)
        assert task.status == TaskStatus.QUEUED

    def test_submitted_task_retrievable(self, orchestrator):
        task = make_research_task("Lookup")
        tid = orchestrator.submit(task)
        retrieved = orchestrator.get_task(tid)
        assert retrieved is task


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.route
# ---------------------------------------------------------------------------

class TestRoute:
    def test_truth_query_returns_decision(self, orchestrator):
        task = make_research_task("What is the birefringence angle?")
        orchestrator.submit(task)
        decision = orchestrator.route(task.task_id)
        assert isinstance(decision, CloudAdjunctDecision)

    def test_truth_query_dispatched(self, orchestrator):
        task = make_research_task("External dataset lookup")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        assert task.status == TaskStatus.DISPATCHED
        assert task.decision is not None
        assert task.decision.cloud_enabled is True

    def test_archive_task_dispatched(self, orchestrator):
        task = AdjunctTask(
            task_id="arch-01",
            role=CloudAdjunctRole.ARCHIVE,
            description="Archive system snapshot",
        )
        orchestrator.submit(task)
        decision = orchestrator.route(task.task_id)
        assert decision.cloud_enabled is True
        assert task.status == TaskStatus.DISPATCHED

    def test_phase_lock_required_rejected(self, orchestrator):
        """A task with requires_human_confirmation=True maps to phase_lock_required=True."""
        task = AdjunctTask(
            task_id="pl-01",
            role=CloudAdjunctRole.TRUTH_QUERY,
            description="Phase-locked query",
            requires_human_confirmation=True,
        )
        orchestrator.submit(task)
        decision = orchestrator.route(task.task_id)
        # phase_lock_required=True → cloud cannot participate
        assert decision.cloud_enabled is False
        assert task.status == TaskStatus.REJECTED_BY_POLICY

    def test_decision_stored_on_task(self, orchestrator):
        task = make_batch_task("Batch simulation", payload={"n": 1000})
        orchestrator.submit(task)
        decision = orchestrator.route(task.task_id)
        assert task.decision is decision


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.verify
# ---------------------------------------------------------------------------

class TestVerify:
    def test_default_verifier_non_empty_result_verified(self, orchestrator):
        task = make_research_task("Query")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        vr = orchestrator.verify(task.task_id, {"answer": 42})
        assert vr.passed is True
        assert task.status == TaskStatus.VERIFIED

    def test_strict_verifier_empty_result_verification_failed(self, system):
        orch = AdjunctOrchestrator(system, local_verifier=strict_local_verifier)
        task = make_research_task("Query")
        orch.submit(task)
        orch.route(task.task_id)
        vr = orch.verify(task.task_id, {})
        assert vr.passed is False
        assert task.status == TaskStatus.VERIFICATION_FAILED

    def test_strict_verifier_passes_good_result(self, system):
        orch = AdjunctOrchestrator(system, local_verifier=strict_local_verifier)
        task = make_batch_task("Simulation", payload={"n": 10})
        orch.submit(task)
        orch.route(task.task_id)
        vr = orch.verify(task.task_id, {"result": [1, 2, 3]})
        assert vr.passed is True
        assert task.status == TaskStatus.VERIFIED

    def test_strict_verifier_error_key_fails(self, system):
        orch = AdjunctOrchestrator(system, local_verifier=strict_local_verifier)
        task = make_research_task("Query")
        orch.submit(task)
        orch.route(task.task_id)
        vr = orch.verify(task.task_id, {"error": "timeout"})
        assert vr.passed is False
        assert task.status == TaskStatus.VERIFICATION_FAILED

    def test_default_verifier_empty_result_still_passes(self, orchestrator):
        task = make_research_task("Lenient query")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        vr = orchestrator.verify(task.task_id, {})
        # Default verifier is lenient — empty result still passes
        assert vr.passed is True
        assert "empty" in " ".join(vr.issues).lower()


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.complete
# ---------------------------------------------------------------------------

class TestComplete:
    def test_complete_verified_task(self, orchestrator):
        task = make_research_task("Complete me")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        orchestrator.verify(task.task_id, {"data": "ok"})
        completed = orchestrator.complete(task.task_id)
        assert completed.status == TaskStatus.COMPLETED

    def test_complete_non_verified_raises(self, orchestrator):
        task = make_research_task("Not yet verified")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        # do NOT call verify — task is still DISPATCHED
        with pytest.raises(ValueError, match="VERIFIED"):
            orchestrator.complete(task.task_id)

    def test_complete_queued_raises(self, orchestrator):
        task = make_research_task("Queued only")
        orchestrator.submit(task)
        with pytest.raises(ValueError):
            orchestrator.complete(task.task_id)


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.fail
# ---------------------------------------------------------------------------

class TestFail:
    def test_fail_marks_task(self, orchestrator):
        task = make_research_task("Will fail")
        orchestrator.submit(task)
        orchestrator.fail(task.task_id, "network timeout")
        assert task.status == TaskStatus.FAILED
        assert "timeout" in task.error

    def test_failed_task_not_in_pending(self, orchestrator):
        task = make_research_task("Failed")
        orchestrator.submit(task)
        orchestrator.fail(task.task_id, "error")
        assert task not in orchestrator.pending_tasks()


# ---------------------------------------------------------------------------
# AdjunctOrchestrator.queue_status
# ---------------------------------------------------------------------------

class TestQueueStatus:
    def test_has_total_key(self, orchestrator):
        qs = orchestrator.queue_status()
        assert "total" in qs

    def test_has_by_status_key(self, orchestrator):
        qs = orchestrator.queue_status()
        assert "by_status" in qs

    def test_has_trust_level_key(self, orchestrator):
        qs = orchestrator.queue_status()
        assert "trust_level" in qs

    def test_total_matches_submitted_tasks(self, orchestrator):
        for _ in range(3):
            task = make_research_task("Task")
            orchestrator.submit(task)
        qs = orchestrator.queue_status()
        assert qs["total"] == 3

    def test_by_status_counts_correct(self, orchestrator):
        t1 = make_research_task("T1")
        t2 = make_research_task("T2")
        orchestrator.submit(t1)
        orchestrator.submit(t2)
        qs = orchestrator.queue_status()
        assert qs["by_status"][TaskStatus.QUEUED] == 2


# ---------------------------------------------------------------------------
# pending_tasks / completed_tasks / flush_completed
# ---------------------------------------------------------------------------

class TestTaskLists:
    def test_pending_excludes_completed(self, orchestrator):
        task = make_research_task("Query")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        orchestrator.verify(task.task_id, {"x": 1})
        orchestrator.complete(task.task_id)
        assert task not in orchestrator.pending_tasks()
        assert task in orchestrator.completed_tasks()

    def test_pending_includes_queued(self, orchestrator):
        task = make_research_task("Pending query")
        orchestrator.submit(task)
        assert task in orchestrator.pending_tasks()

    def test_flush_completed_removes_from_queue(self, orchestrator):
        task = make_research_task("Flush me")
        orchestrator.submit(task)
        orchestrator.route(task.task_id)
        orchestrator.verify(task.task_id, {"ok": True})
        orchestrator.complete(task.task_id)
        flushed = orchestrator.flush_completed()
        assert task in flushed
        assert orchestrator.queue_status()["total"] == 0


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

class TestConvenienceConstructors:
    def test_make_research_task_role(self):
        task = make_research_task("Research question")
        assert task.role == CloudAdjunctRole.TRUTH_QUERY

    def test_make_research_task_has_uuid_id(self):
        task = make_research_task("Question")
        assert len(task.task_id) == 36  # UUID4 format

    def test_make_research_task_custom_criticality(self):
        task = make_research_task("Q", criticality=0.2)
        assert task.criticality == 0.2

    def test_make_batch_task_role(self):
        task = make_batch_task("Simulation", payload={"n": 100})
        assert task.role == CloudAdjunctRole.BATCH_COMPUTE

    def test_make_batch_task_payload(self):
        payload = {"key": "value", "count": 42}
        task = make_batch_task("Job", payload=payload)
        assert task.payload == payload

    def test_make_batch_task_roundtrip_ms(self):
        task = make_batch_task("Job", payload={})
        assert task.estimated_roundtrip_ms == 2000.0

    def test_make_model_task_role(self):
        task = make_model_task("Inference request")
        assert task.role == CloudAdjunctRole.MODEL_HOST

    def test_make_model_task_criticality(self):
        task = make_model_task("Inference")
        assert task.criticality == 0.6

    def test_two_tasks_have_different_ids(self):
        t1 = make_research_task("Q1")
        t2 = make_research_task("Q2")
        assert t1.task_id != t2.task_id


# ---------------------------------------------------------------------------
# Standalone verifier tests
# ---------------------------------------------------------------------------

class TestVerifiers:
    def _make_task_with_result(self, result) -> AdjunctTask:
        task = AdjunctTask(
            task_id="vtest",
            role=CloudAdjunctRole.TRUTH_QUERY,
            description="Verifier test task",
        )
        task.result = result
        return task

    def test_default_verifier_passes_none_result_as_failed(self):
        task = self._make_task_with_result(None)
        vr = default_local_verifier(task)
        assert vr.passed is False

    def test_default_verifier_passes_non_empty_dict(self):
        task = self._make_task_with_result({"key": "val"})
        vr = default_local_verifier(task)
        assert vr.passed is True
        assert vr.confidence == 0.8

    def test_strict_verifier_fails_none(self):
        task = self._make_task_with_result(None)
        vr = strict_local_verifier(task)
        assert vr.passed is False
        assert vr.confidence == 0.0

    def test_strict_verifier_passes_good_dict(self):
        task = self._make_task_with_result({"value": 3.14})
        vr = strict_local_verifier(task)
        assert vr.passed is True
        assert len(vr.issues) == 0

    def test_strict_verifier_verified_payload_matches(self):
        raw = {"result": 99}
        task = self._make_task_with_result(raw)
        vr = strict_local_verifier(task)
        assert vr.verified_payload == raw
