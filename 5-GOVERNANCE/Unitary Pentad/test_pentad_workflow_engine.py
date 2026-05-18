# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_pentad_workflow_engine.py
==============================================
Tests for the Pentad-native workflow/orchestration engine (Sprint A).

All tests are self-contained.  They import directly from the local package
path so they can be run with::

    cd "5-GOVERNANCE/Unitary Pentad"
    python -m pytest test_pentad_workflow_engine.py -q --tb=short
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
    "sprint": "A — Constitutional Orchestration",
}

import dataclasses
import sys
import os

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from pentad_workflow_engine import (
    HILGateType,
    HIL_GATE_TYPES,
    StopCondition,
    WorkflowEventType,
    WorkflowEvent,
    HILGate,
    AgentJob,
    PentadWorkflowSchema,
    WorkflowResult,
    WorkflowEngineContext,
    WorkflowEngine,
    build_workflow,
)
from five_cores.five_cores_system import (
    FiveCoresSystem,
    CoreLabel,
    CORE_LABELS,
)
from unitary_pentad import TRUST_PHI_MIN


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def system() -> FiveCoresSystem:
    """Default Five-Cores system at full trust."""
    return FiveCoresSystem.default()


@pytest.fixture()
def simple_job() -> AgentJob:
    """A single no-op STRATEGIC job with no gates."""
    return AgentJob(
        job_id="job_strategic",
        description="A simple strategic no-op",
        core_lane=CoreLabel.STRATEGIC,
        hil_gates=[],
    )


@pytest.fixture()
def simple_schema(simple_job: AgentJob) -> PentadWorkflowSchema:
    """Minimal single-job schema for basic engine tests."""
    return build_workflow(
        workflow_id="wf_simple",
        name="Simple Workflow",
        description="Minimal workflow for testing",
        jobs=[simple_job],
    )


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------


class TestHILGateTypeConstants:
    def test_all_five_types_exist(self) -> None:
        assert HILGateType.SAFETY == "safety"
        assert HILGateType.LEGITIMACY == "legitimacy"
        assert HILGateType.BIFURCATION == "bifurcation"
        assert HILGateType.CRITICALITY == "criticality"
        assert HILGateType.MANDATORY_REVIEW == "mandatory_review"

    def test_hil_gate_types_tuple_length(self) -> None:
        assert len(HIL_GATE_TYPES) == 5

    def test_hil_gate_types_contains_all(self) -> None:
        for attr in ("safety", "legitimacy", "bifurcation", "criticality", "mandatory_review"):
            assert attr in HIL_GATE_TYPES


class TestStopConditionConstants:
    def test_trust_below_floor(self) -> None:
        assert StopCondition.TRUST_BELOW_FLOOR == "trust_below_floor"

    def test_safety_halt(self) -> None:
        assert StopCondition.SAFETY_HALT == "safety_halt"

    def test_legitimacy_rejected(self) -> None:
        assert StopCondition.LEGITIMACY_REJECTED == "legitimacy_rejected"

    def test_collapse_detected(self) -> None:
        assert StopCondition.COLLAPSE_DETECTED == "collapse_detected"

    def test_max_steps_exceeded(self) -> None:
        assert StopCondition.MAX_STEPS_EXCEEDED == "max_steps_exceeded"

    def test_hil_timeout(self) -> None:
        assert StopCondition.HIL_TIMEOUT == "hil_timeout"


# ---------------------------------------------------------------------------
# WorkflowEvent immutability
# ---------------------------------------------------------------------------


class TestWorkflowEventImmutability:
    def test_is_frozen(self) -> None:
        evt = WorkflowEvent(
            event_id="abc",
            timestamp=1.0,
            event_type=WorkflowEventType.WORKFLOW_STARTED,
            workflow_id="wf1",
            job_id="",
            core_lane="",
            gate_id="",
            payload={},
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            evt.event_id = "xyz"  # type: ignore[misc]

    def test_is_dataclass(self) -> None:
        assert dataclasses.is_dataclass(WorkflowEvent)

    def test_fields_accessible(self) -> None:
        evt = WorkflowEvent(
            event_id="e1",
            timestamp=42.0,
            event_type=WorkflowEventType.JOB_STARTED,
            workflow_id="wf2",
            job_id="j1",
            core_lane=CoreLabel.STRATEGIC,
            gate_id="",
            payload={"key": "val"},
        )
        assert evt.workflow_id == "wf2"
        assert evt.payload == {"key": "val"}


# ---------------------------------------------------------------------------
# build_workflow()
# ---------------------------------------------------------------------------


class TestBuildWorkflow:
    def test_handoff_order_matches_job_order(self) -> None:
        jobs = [
            AgentJob("j1", "desc1", CoreLabel.STRATEGIC, []),
            AgentJob("j2", "desc2", CoreLabel.OPERATIONAL, []),
            AgentJob("j3", "desc3", CoreLabel.SAFETY, []),
        ]
        schema = build_workflow("wf_test", "Test", "desc", jobs)
        assert schema.handoff_order == ["j1", "j2", "j3"]

    def test_required_cores_inferred(self) -> None:
        jobs = [
            AgentJob("j1", "d", CoreLabel.STRATEGIC, []),
            AgentJob("j2", "d", CoreLabel.OPERATIONAL, []),
            AgentJob("j3", "d", CoreLabel.STRATEGIC, []),  # duplicate
        ]
        schema = build_workflow("wf2", "T", "D", jobs)
        # STRATEGIC appears twice but required_cores has it once
        assert CoreLabel.STRATEGIC in schema.required_cores
        assert CoreLabel.OPERATIONAL in schema.required_cores
        assert len(schema.required_cores) == 2

    def test_trust_floor_default(self) -> None:
        schema = build_workflow("wf3", "T", "D", [])
        assert schema.trust_floor == TRUST_PHI_MIN

    def test_custom_trust_floor(self) -> None:
        schema = build_workflow("wf4", "T", "D", [], trust_floor=0.5)
        assert schema.trust_floor == 0.5

    def test_max_autonomous_steps_default(self) -> None:
        schema = build_workflow("wf5", "T", "D", [])
        assert schema.max_autonomous_steps == 50

    def test_custom_max_steps(self) -> None:
        schema = build_workflow("wf6", "T", "D", [], max_autonomous_steps=10)
        assert schema.max_autonomous_steps == 10

    def test_empty_jobs(self) -> None:
        schema = build_workflow("wf7", "T", "D", [])
        assert schema.handoff_order == []
        assert schema.required_cores == ()


# ---------------------------------------------------------------------------
# WorkflowEngine.run() — no gates
# ---------------------------------------------------------------------------


class TestRunNoGates:
    def test_completes_successfully(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        assert result.status == "completed"

    def test_stop_reason_empty_on_success(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        assert result.stop_reason == ""

    def test_jobs_completed_contains_job(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        assert "job_strategic" in result.jobs_completed

    def test_jobs_pending_empty_on_success(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        assert result.jobs_pending == []

    def test_event_log_non_empty(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        assert len(result.event_log) > 0

    def test_workflow_started_event_present(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        types = [e.event_type for e in result.event_log]
        assert WorkflowEventType.WORKFLOW_STARTED in types

    def test_workflow_completed_event_present(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        result = engine.run(simple_schema)
        types = [e.event_type for e in result.event_log]
        assert WorkflowEventType.WORKFLOW_COMPLETED in types

    def test_handler_return_captured(self, system: FiveCoresSystem) -> None:
        def my_handler(job, ctx):
            return {"custom_output": 42}

        job = AgentJob(
            job_id="j_handler",
            description="handler test",
            core_lane=CoreLabel.OPERATIONAL,
            hil_gates=[],
            handler=my_handler,
        )
        schema = build_workflow("wf_h", "H", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        assert result.status == "completed"


# ---------------------------------------------------------------------------
# WorkflowEngine.run() — auto-approving HIL handler
# ---------------------------------------------------------------------------


class TestRunAutoApprovingHandler:
    def test_completes_with_auto_approve(self, system: FiveCoresSystem) -> None:
        gate = HILGate(
            gate_id="g_safety",
            gate_type=HILGateType.SAFETY,
            description="Safety check",
        )
        job = AgentJob(
            job_id="j_gated",
            description="Gated job",
            core_lane=CoreLabel.SAFETY,
            hil_gates=[gate],
        )
        schema = build_workflow("wf_approve", "Approve", "d", [job])
        engine = WorkflowEngine(system)

        result = engine.run(schema, hil_handler=lambda g, ctx: True)
        assert result.status == "completed"

    def test_approved_event_emitted(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g1", HILGateType.LEGITIMACY, "Legitimacy check")
        job = AgentJob("j1", "d", CoreLabel.SAFETY, [gate])
        schema = build_workflow("wf_a2", "A2", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: True)
        types = [e.event_type for e in result.event_log]
        assert WorkflowEventType.HIL_GATE_APPROVED in types

    def test_multiple_gates_all_approved(self, system: FiveCoresSystem) -> None:
        gates = [
            HILGate("g_s", HILGateType.SAFETY, "Safety"),
            HILGate("g_l", HILGateType.LEGITIMACY, "Legitimacy"),
        ]
        job = AgentJob("j_multi", "multi-gate", CoreLabel.BIOLOGICAL, gates)
        schema = build_workflow("wf_multi", "Multi", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: True)
        assert result.status == "completed"
        approved = [e for e in result.event_log if e.event_type == WorkflowEventType.HIL_GATE_APPROVED]
        assert len(approved) == 2


# ---------------------------------------------------------------------------
# WorkflowEngine.run() — rejecting HIL handler
# ---------------------------------------------------------------------------


class TestRunRejectingHandler:
    def test_fails_on_required_gate_rejection(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g_req", HILGateType.CRITICALITY, "Critical gate", required=True)
        job = AgentJob("j_req", "required gate job", CoreLabel.STRATEGIC, [gate])
        schema = build_workflow("wf_reject", "Reject", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        assert result.status == "failed"

    def test_stop_reason_is_legitimacy_rejected(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g_req2", HILGateType.MANDATORY_REVIEW, "Review gate", required=True)
        job = AgentJob("j_req2", "d", CoreLabel.OPERATIONAL, [gate])
        schema = build_workflow("wf_rej2", "R2", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        assert result.stop_reason == StopCondition.LEGITIMACY_REJECTED

    def test_rejected_event_emitted(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g_rej3", HILGateType.SAFETY, "Safety reject", required=True)
        job = AgentJob("j_rej3", "d", CoreLabel.SAFETY, [gate])
        schema = build_workflow("wf_rej3", "R3", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        types = [e.event_type for e in result.event_log]
        assert WorkflowEventType.HIL_GATE_REJECTED in types

    def test_stop_condition_fired_event_present(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g_rej4", HILGateType.BIFURCATION, "Bifurcation", required=True)
        job = AgentJob("j_rej4", "d", CoreLabel.SCIENCES, [gate])
        schema = build_workflow("wf_rej4", "R4", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        types = [e.event_type for e in result.event_log]
        assert WorkflowEventType.STOP_CONDITION_FIRED in types

    def test_optional_gate_rejection_does_not_block(self, system: FiveCoresSystem) -> None:
        """A non-required gate rejection emits REJECTED but does not halt."""
        gate = HILGate("g_opt", HILGateType.LEGITIMACY, "Optional gate", required=False)
        job = AgentJob("j_opt", "optional gate", CoreLabel.STRATEGIC, [gate])
        schema = build_workflow("wf_opt", "Opt", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        assert result.status == "completed"


# ---------------------------------------------------------------------------
# WorkflowEngine.run() — trust floor enforcement
# ---------------------------------------------------------------------------


class TestTrustFloor:
    def test_fails_when_trust_below_floor(self) -> None:
        # Create system with very low trust so it is below any reasonable floor
        system = FiveCoresSystem(phi_trust=0.0)
        job = AgentJob("j_trust", "trust test", CoreLabel.STRATEGIC, [])
        # Set trust_floor well above the system's phi_trust (0.0)
        schema = build_workflow("wf_trust", "Trust", "d", [job], trust_floor=0.5)
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        assert result.status == "failed"

    def test_stop_reason_is_trust_below_floor(self) -> None:
        system = FiveCoresSystem(phi_trust=0.0)
        job = AgentJob("j_t2", "d", CoreLabel.OPERATIONAL, [])
        schema = build_workflow("wf_t2", "T2", "d", [job], trust_floor=0.5)
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        assert result.stop_reason == StopCondition.TRUST_BELOW_FLOOR

    def test_passes_when_trust_at_floor(self) -> None:
        """Exact equality: phi_trust == trust_floor → should NOT fail (≥ floor)."""
        floor = 0.3
        system = FiveCoresSystem(phi_trust=floor)
        job = AgentJob("j_exact", "d", CoreLabel.STRATEGIC, [])
        schema = build_workflow("wf_exact", "Exact", "d", [job], trust_floor=floor)
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        # phi_trust == floor means not below floor, so should complete
        assert result.status == "completed"


# ---------------------------------------------------------------------------
# get_event_log()
# ---------------------------------------------------------------------------


class TestGetEventLog:
    def test_returns_list(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        log = engine.get_event_log()
        assert isinstance(log, list)

    def test_all_entries_are_workflow_events(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        log = engine.get_event_log()
        for entry in log:
            assert isinstance(entry, WorkflowEvent)

    def test_accumulates_across_runs(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        count_after_first = len(engine.get_event_log())
        engine.run(simple_schema)
        count_after_second = len(engine.get_event_log())
        assert count_after_second > count_after_first

    def test_returns_copy_not_reference(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        log1 = engine.get_event_log()
        log2 = engine.get_event_log()
        # Mutating the returned list should not affect the engine's internal log
        log1.clear()
        assert len(engine.get_event_log()) == len(log2)


# ---------------------------------------------------------------------------
# replay_events()
# ---------------------------------------------------------------------------


class TestReplayEvents:
    def test_returns_list(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        assert isinstance(engine.replay_events(), list)

    def test_default_returns_all(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        assert engine.replay_events() == engine.get_event_log()

    def test_from_step_zero(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        full = engine.get_event_log()
        replayed = engine.replay_events(from_step=0)
        assert replayed == full

    def test_from_step_slices_start(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        full = engine.get_event_log()
        if len(full) >= 2:
            replayed = engine.replay_events(from_step=1)
            assert replayed == full[1:]

    def test_to_step_slices_end(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        full = engine.get_event_log()
        if len(full) >= 3:
            replayed = engine.replay_events(from_step=0, to_step=1)
            assert replayed == full[0:2]

    def test_empty_log_returns_empty(self, system: FiveCoresSystem) -> None:
        engine = WorkflowEngine(system)
        assert engine.replay_events() == []

    def test_from_beyond_end_returns_empty(self, system: FiveCoresSystem, simple_schema: PentadWorkflowSchema) -> None:
        engine = WorkflowEngine(system)
        engine.run(simple_schema)
        full = engine.get_event_log()
        result = engine.replay_events(from_step=len(full) + 100)
        assert result == []


# ---------------------------------------------------------------------------
# Multi-job workflow
# ---------------------------------------------------------------------------


class TestMultiJobWorkflow:
    def test_all_jobs_completed_in_order(self, system: FiveCoresSystem) -> None:
        completed_order = []

        def make_handler(label):
            def h(job, ctx):
                completed_order.append(job.job_id)
                return {}
            return h

        jobs = [
            AgentJob("j1", "d", CoreLabel.STRATEGIC, [], handler=make_handler("j1")),
            AgentJob("j2", "d", CoreLabel.OPERATIONAL, [], handler=make_handler("j2")),
            AgentJob("j3", "d", CoreLabel.SAFETY, [], handler=make_handler("j3")),
        ]
        schema = build_workflow("wf_multi3", "Multi3", "d", jobs)
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        assert result.status == "completed"
        assert completed_order == ["j1", "j2", "j3"]

    def test_handler_exception_causes_collapse_stop(self, system: FiveCoresSystem) -> None:
        def bad_handler(job, ctx):
            raise RuntimeError("simulated collapse")

        job = AgentJob("j_bad", "d", CoreLabel.SCIENCES, [], handler=bad_handler)
        schema = build_workflow("wf_collapse", "Collapse", "d", [job])
        engine = WorkflowEngine(system)
        result = engine.run(schema)
        assert result.status == "failed"
        assert result.stop_reason == StopCondition.COLLAPSE_DETECTED

    def test_pending_jobs_listed_on_failure(self, system: FiveCoresSystem) -> None:
        gate = HILGate("g_stop", HILGateType.SAFETY, "Gate that rejects", required=True)
        job1 = AgentJob("j_first", "d", CoreLabel.STRATEGIC, [])
        job2 = AgentJob("j_blocked", "d", CoreLabel.OPERATIONAL, [gate])
        job3 = AgentJob("j_never", "d", CoreLabel.SAFETY, [])
        schema = build_workflow("wf_pending", "Pending", "d", [job1, job2, job3])
        engine = WorkflowEngine(system)
        result = engine.run(schema, hil_handler=lambda g, ctx: False)
        assert "j_first" in result.jobs_completed
        assert "j_blocked" in result.jobs_pending
        assert "j_never" in result.jobs_pending


# ---------------------------------------------------------------------------
# HILGate dataclass
# ---------------------------------------------------------------------------


class TestHILGateDataclass:
    def test_is_frozen(self) -> None:
        gate = HILGate("g1", HILGateType.SAFETY, "d")
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            gate.gate_id = "new"  # type: ignore[misc]

    def test_required_default_true(self) -> None:
        gate = HILGate("g2", HILGateType.LEGITIMACY, "d")
        assert gate.required is True

    def test_required_false_explicit(self) -> None:
        gate = HILGate("g3", HILGateType.BIFURCATION, "d", required=False)
        assert gate.required is False


# ---------------------------------------------------------------------------
# WorkflowEngineContext
# ---------------------------------------------------------------------------


class TestWorkflowEngineContext:
    def test_approve_gate(self, system: FiveCoresSystem) -> None:
        log: list = []
        ctx = WorkflowEngineContext("wf_ctx", system, log)
        ctx.approve_gate("g1")
        assert ctx.is_approved("g1")
        assert not ctx.is_rejected("g1")

    def test_reject_gate(self, system: FiveCoresSystem) -> None:
        log: list = []
        ctx = WorkflowEngineContext("wf_ctx2", system, log)
        ctx.reject_gate("g2")
        assert ctx.is_rejected("g2")
        assert not ctx.is_approved("g2")

    def test_approve_overrides_reject(self, system: FiveCoresSystem) -> None:
        log: list = []
        ctx = WorkflowEngineContext("wf_ctx3", system, log)
        ctx.reject_gate("g3")
        ctx.approve_gate("g3")
        assert ctx.is_approved("g3")
        assert not ctx.is_rejected("g3")
