# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_workflow_engine.py
=========================================
Pentad-native declarative workflow / orchestration engine — Sprint A.

Overview
--------
Workflows are expressed as :class:`PentadWorkflowSchema` dataclasses that are
fully serialisable to/from plain Python dicts.  Each schema contains an ordered
list of :class:`AgentJob` entries, each mapped to one of the five constitutional
core lanes (:class:`CoreLabel`).  :class:`HILGate` objects define human-approval
checkpoints that the engine evaluates before executing each job.

:class:`WorkflowEngine` runs a schema step-by-step:

* Emits :class:`WorkflowEvent` objects to an audit log at every significant
  state transition.
* Enforces trust/safety stop conditions derived from the live
  :class:`FiveCoresSystem`.
* Remains **deterministic and pure-Python** — no async, no threads.  All
  HIL callbacks are synchronous.

Public API
----------
HILGateType
    String constants for the five supported gate categories.

HIL_GATE_TYPES : tuple[str, ...]
    Canonical ordered tuple of gate type strings.

StopCondition
    String constants for the six stop-condition codes.

WorkflowEventType
    String constants for the nine workflow event types.

WorkflowEvent
    Frozen dataclass representing one audit-log entry.

HILGate
    Frozen dataclass representing a single human-approval checkpoint.

AgentJob
    Mutable dataclass describing one executable workflow step.

PentadWorkflowSchema
    Mutable dataclass describing a complete workflow.

WorkflowResult
    Return value of :meth:`WorkflowEngine.run`.

WorkflowEngineContext
    Runtime mutable context passed into job handlers and HIL gates.

WorkflowEngine
    Stateful engine that evaluates a :class:`PentadWorkflowSchema`.

build_workflow(...)
    Convenience builder that infers ``handoff_order`` and ``required_cores``.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "sprint": "A — Constitutional Orchestration",
}

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import sys
import os

# ---------------------------------------------------------------------------
# Path bootstrap — identical pattern used by unitary_pentad.py
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ---------------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------------

from unitary_pentad import (  # noqa: E402
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    TRUST_PHI_MIN,
    trust_modulation,
    pentad_defect,
)
from five_cores.five_cores_system import (  # noqa: E402
    FiveCoresSystem,
    CoreLabel,
    CORE_LABELS,
    SystemStatus,
    SystemHealthReport,
)
from pentad_cloud_adjunct import (  # noqa: E402
    CloudAdjunctRole,
    CloudAdjunctRequest,
    evaluate_cloud_adjunct,
    default_cloud_adjunct_policy,
)
from pentad_scenarios import (  # noqa: E402
    detect_collapse_mode,
    CollapseMode,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class HILGateType:
    """String constants for the five supported HIL gate categories."""

    SAFETY = "safety"
    LEGITIMACY = "legitimacy"
    BIFURCATION = "bifurcation"
    CRITICALITY = "criticality"
    MANDATORY_REVIEW = "mandatory_review"


#: Canonical ordered tuple of all HIL gate type strings.
HIL_GATE_TYPES: Tuple[str, ...] = (
    HILGateType.SAFETY,
    HILGateType.LEGITIMACY,
    HILGateType.BIFURCATION,
    HILGateType.CRITICALITY,
    HILGateType.MANDATORY_REVIEW,
)


class StopCondition:
    """String constants for the six workflow stop-condition codes."""

    TRUST_BELOW_FLOOR = "trust_below_floor"
    SAFETY_HALT = "safety_halt"
    LEGITIMACY_REJECTED = "legitimacy_rejected"
    COLLAPSE_DETECTED = "collapse_detected"
    MAX_STEPS_EXCEEDED = "max_steps_exceeded"
    HIL_TIMEOUT = "hil_timeout"


class WorkflowEventType:
    """String constants for the nine workflow event types."""

    WORKFLOW_STARTED = "workflow_started"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    HIL_GATE_TRIGGERED = "hil_gate_triggered"
    HIL_GATE_APPROVED = "hil_gate_approved"
    HIL_GATE_REJECTED = "hil_gate_rejected"
    STOP_CONDITION_FIRED = "stop_condition_fired"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkflowEvent:
    """
    Immutable audit-log entry emitted at every significant state transition.

    Attributes
    ----------
    event_id : str
        UUID4 string — globally unique.
    timestamp : float
        ``time.monotonic()`` at emission.
    event_type : str
        One of :class:`WorkflowEventType` constants.
    workflow_id : str
        Owning workflow identifier.
    job_id : str
        Active job identifier, or ``""`` for workflow-level events.
    core_lane : str
        :class:`CoreLabel` of the active job, or ``""`` when not applicable.
    gate_id : str
        :class:`HILGate`.gate_id, or ``""`` when not gate-related.
    payload : dict
        Free dictionary for supplementary context (e.g. health scores,
        stop-condition reasons, handler return values).
    """

    event_id: str
    timestamp: float
    event_type: str
    workflow_id: str
    job_id: str
    core_lane: str
    gate_id: str
    payload: dict


@dataclass(frozen=True)
class HILGate:
    """
    Human-approval checkpoint evaluated before a job is executed.

    Attributes
    ----------
    gate_id : str
        Unique identifier for this gate.
    gate_type : str
        One of :class:`HILGateType` constants.
    description : str
        Human-readable description of what approval entails.
    required : bool
        If ``True`` (default), rejection blocks the workflow.
        If ``False``, rejection emits a warning but does not halt execution.
    """

    gate_id: str
    gate_type: str
    description: str
    required: bool = True


@dataclass
class AgentJob:
    """
    One executable step in a :class:`PentadWorkflowSchema`.

    Attributes
    ----------
    job_id : str
        Unique identifier for this job.
    description : str
        Human-readable description of the job's purpose.
    core_lane : str
        Constitutional supervision lane — one of :class:`CoreLabel` constants.
    hil_gates : list[HILGate]
        Ordered gates that must pass before job execution.
    cloud_adjunct_eligible : bool
        Whether this job may be routed to cloud compute.
    cloud_role : str | None
        :class:`CloudAdjunctRole` constant, or ``None`` if not cloud-eligible.
    trust_threshold : float
        Minimum trust required to run this job (defaults to TRUST_PHI_MIN).
    stop_conditions : tuple[str, ...]
        Additional stop conditions to monitor (beyond global defaults).
    handler : callable | None
        ``(job, ctx) → dict`` called during execution.  ``None`` → no-op.
    """

    job_id: str
    description: str
    core_lane: str
    hil_gates: List[HILGate]
    cloud_adjunct_eligible: bool = False
    cloud_role: Optional[str] = None
    trust_threshold: float = TRUST_PHI_MIN
    stop_conditions: Tuple[str, ...] = ()
    handler: Any = field(default=None, repr=False)


@dataclass
class PentadWorkflowSchema:
    """
    Declarative specification of a complete Pentad workflow.

    Attributes
    ----------
    workflow_id : str
        Unique identifier for this workflow.
    name : str
        Short human-readable name.
    description : str
        Full description of the workflow's purpose and scope.
    agent_jobs : list[AgentJob]
        All jobs defined in this workflow (may include jobs not in handoff_order
        for reference / future use).
    handoff_order : list[str]
        Ordered sequence of job_ids to execute.
    required_cores : tuple[str, ...]
        Core lanes that must be represented in the job set.
    trust_floor : float
        Minimum system trust below which the workflow is aborted.
    max_autonomous_steps : int
        Maximum number of job iterations before MAX_STEPS_EXCEEDED fires.
    hil_timeout_steps : int
        Number of steps after which a pending HIL gate triggers HIL_TIMEOUT.
    """

    workflow_id: str
    name: str
    description: str
    agent_jobs: List[AgentJob]
    handoff_order: List[str]
    required_cores: Tuple[str, ...]
    trust_floor: float = TRUST_PHI_MIN
    max_autonomous_steps: int = 50
    hil_timeout_steps: int = 10


@dataclass
class WorkflowResult:
    """
    Return value of :meth:`WorkflowEngine.run`.

    Attributes
    ----------
    workflow_id : str
    status : str
        ``"completed"`` | ``"failed"`` | ``"stopped"``.
    stop_reason : str
        ``""`` on success, or a :class:`StopCondition` constant on failure.
    jobs_completed : list[str]
        job_ids that finished successfully.
    jobs_pending : list[str]
        job_ids that were not reached.
    event_log : list[WorkflowEvent]
        Full ordered audit trail for this run.
    final_health : float
        System health score at the end of the run.
    """

    workflow_id: str
    status: str
    stop_reason: str
    jobs_completed: List[str]
    jobs_pending: List[str]
    event_log: List[WorkflowEvent]
    final_health: float


# ---------------------------------------------------------------------------
# Runtime context
# ---------------------------------------------------------------------------


class WorkflowEngineContext:
    """
    Mutable runtime context passed into job handlers and HIL callbacks.

    Attributes
    ----------
    workflow_id : str
    current_job_id : str
    system : FiveCoresSystem
        Live system reference — handlers may call ``system.tick()`` etc.
    pending_gates : list[HILGate]
        Gates not yet resolved in the current job.
    event_log : list[WorkflowEvent]
        Shared audit log (same list as the engine's internal log).
    step : int
        Current iteration counter (0-indexed).
    """

    def __init__(
        self,
        workflow_id: str,
        system: FiveCoresSystem,
        event_log: List[WorkflowEvent],
    ) -> None:
        self.workflow_id: str = workflow_id
        self.current_job_id: str = ""
        self.system: FiveCoresSystem = system
        self.pending_gates: List[HILGate] = []
        self.event_log: List[WorkflowEvent] = event_log
        self.step: int = 0
        self._approved_gates: set = set()
        self._rejected_gates: set = set()

    # ------------------------------------------------------------------
    # Gate resolution helpers (may be called from handlers)
    # ------------------------------------------------------------------

    def approve_gate(self, gate_id: str) -> None:
        """Mark a gate as approved."""
        self._approved_gates.add(gate_id)
        self._rejected_gates.discard(gate_id)

    def reject_gate(self, gate_id: str) -> None:
        """Mark a gate as rejected."""
        self._rejected_gates.add(gate_id)
        self._approved_gates.discard(gate_id)

    def is_approved(self, gate_id: str) -> bool:
        """Return ``True`` if the gate has been approved."""
        return gate_id in self._approved_gates

    def is_rejected(self, gate_id: str) -> bool:
        """Return ``True`` if the gate has been rejected."""
        return gate_id in self._rejected_gates


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class WorkflowEngine:
    """
    Stateful engine that evaluates a :class:`PentadWorkflowSchema`.

    Parameters
    ----------
    system : FiveCoresSystem
        Live Five-Cores system that the engine will tick during execution.

    Notes
    -----
    * The engine is **not** thread-safe.
    * A single engine instance may run multiple schemas sequentially; the
      internal event log accumulates across runs.
    * All HIL callbacks are **synchronous** — no async/await.
    """

    def __init__(self, system: FiveCoresSystem) -> None:
        self._system = system
        self._event_log: List[WorkflowEvent] = []
        self._pending_gates: List[HILGate] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(
        self,
        event_type: str,
        workflow_id: str,
        *,
        job_id: str = "",
        core_lane: str = "",
        gate_id: str = "",
        payload: Optional[Dict[str, Any]] = None,
    ) -> WorkflowEvent:
        """Create and append a :class:`WorkflowEvent` to the audit log."""
        evt = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.monotonic(),
            event_type=event_type,
            workflow_id=workflow_id,
            job_id=job_id,
            core_lane=core_lane,
            gate_id=gate_id,
            payload=payload or {},
        )
        self._event_log.append(evt)
        return evt

    def _make_failed(
        self,
        schema: PentadWorkflowSchema,
        stop_reason: str,
        completed: List[str],
        pending: List[str],
        health: float,
    ) -> WorkflowResult:
        self._emit(
            WorkflowEventType.WORKFLOW_FAILED,
            schema.workflow_id,
            payload={"stop_reason": stop_reason},
        )
        return WorkflowResult(
            workflow_id=schema.workflow_id,
            status="failed",
            stop_reason=stop_reason,
            jobs_completed=list(completed),
            jobs_pending=list(pending),
            event_log=list(self._event_log),
            final_health=health,
        )

    def _current_health(self) -> float:
        """Return the last recorded health score, or 0.0 if no ticks yet."""
        hist = self._system.history()
        if hist:
            return hist[-1].health_score
        return 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        schema: PentadWorkflowSchema,
        *,
        hil_handler: Optional[Callable[[HILGate, WorkflowEngineContext], bool]] = None,
    ) -> WorkflowResult:
        """
        Execute a workflow schema and return a :class:`WorkflowResult`.

        Parameters
        ----------
        schema : PentadWorkflowSchema
            The workflow to execute.
        hil_handler : callable | None
            ``(gate, ctx) → bool`` called for each required HIL gate.
            Return ``True`` = approved, ``False`` = rejected.
            If ``None``, all required gates are **auto-approved** (batch mode).

        Returns
        -------
        WorkflowResult
            Execution result with full audit log.
        """
        wid = schema.workflow_id

        # Build job lookup
        job_map: Dict[str, AgentJob] = {j.job_id: j for j in schema.agent_jobs}

        ctx = WorkflowEngineContext(
            workflow_id=wid,
            system=self._system,
            event_log=self._event_log,
        )

        self._emit(
            WorkflowEventType.WORKFLOW_STARTED,
            wid,
            payload={
                "name": schema.name,
                "handoff_order": schema.handoff_order,
                "trust_floor": schema.trust_floor,
                "max_autonomous_steps": schema.max_autonomous_steps,
            },
        )

        jobs_completed: List[str] = []
        jobs_pending: List[str] = list(schema.handoff_order)

        for step_idx, job_id in enumerate(schema.handoff_order):
            ctx.step = step_idx
            ctx.current_job_id = job_id

            # ---- Max-steps guard ----------------------------------------
            if step_idx >= schema.max_autonomous_steps:
                self._emit(
                    WorkflowEventType.STOP_CONDITION_FIRED,
                    wid,
                    job_id=job_id,
                    payload={"stop_condition": StopCondition.MAX_STEPS_EXCEEDED},
                )
                return self._make_failed(
                    schema,
                    StopCondition.MAX_STEPS_EXCEEDED,
                    jobs_completed,
                    jobs_pending,
                    self._current_health(),
                )

            # ---- Trust floor check --------------------------------------
            if self._system.phi_trust < schema.trust_floor:
                self._emit(
                    WorkflowEventType.STOP_CONDITION_FIRED,
                    wid,
                    job_id=job_id,
                    payload={
                        "stop_condition": StopCondition.TRUST_BELOW_FLOOR,
                        "phi_trust": self._system.phi_trust,
                        "trust_floor": schema.trust_floor,
                    },
                )
                return self._make_failed(
                    schema,
                    StopCondition.TRUST_BELOW_FLOOR,
                    jobs_completed,
                    jobs_pending,
                    self._current_health(),
                )

            # ---- Tick the system ----------------------------------------
            report: SystemHealthReport = self._system.tick()

            # ---- Safety halt check --------------------------------------
            if report.status == SystemStatus.HALTED:
                self._emit(
                    WorkflowEventType.STOP_CONDITION_FIRED,
                    wid,
                    job_id=job_id,
                    payload={
                        "stop_condition": StopCondition.SAFETY_HALT,
                        "health_score": report.health_score,
                    },
                )
                return self._make_failed(
                    schema,
                    StopCondition.SAFETY_HALT,
                    jobs_completed,
                    jobs_pending,
                    report.health_score,
                )

            job = job_map[job_id]
            ctx.current_job_id = job_id

            self._emit(
                WorkflowEventType.JOB_STARTED,
                wid,
                job_id=job_id,
                core_lane=job.core_lane,
                payload={
                    "description": job.description,
                    "cloud_adjunct_eligible": job.cloud_adjunct_eligible,
                    "health_score": report.health_score,
                },
            )

            # ---- HIL gates ----------------------------------------------
            gate_rejected = False
            for gate in job.hil_gates:
                self._emit(
                    WorkflowEventType.HIL_GATE_TRIGGERED,
                    wid,
                    job_id=job_id,
                    core_lane=job.core_lane,
                    gate_id=gate.gate_id,
                    payload={
                        "gate_type": gate.gate_type,
                        "description": gate.description,
                        "required": gate.required,
                    },
                )

                # Resolve gate via handler or auto-approve
                if hil_handler is not None:
                    approved = bool(hil_handler(gate, ctx))
                else:
                    approved = True  # auto-approve in batch mode

                if approved:
                    ctx.approve_gate(gate.gate_id)
                    self._emit(
                        WorkflowEventType.HIL_GATE_APPROVED,
                        wid,
                        job_id=job_id,
                        core_lane=job.core_lane,
                        gate_id=gate.gate_id,
                    )
                else:
                    ctx.reject_gate(gate.gate_id)
                    self._emit(
                        WorkflowEventType.HIL_GATE_REJECTED,
                        wid,
                        job_id=job_id,
                        core_lane=job.core_lane,
                        gate_id=gate.gate_id,
                        payload={"required": gate.required},
                    )
                    if gate.required:
                        self._emit(
                            WorkflowEventType.STOP_CONDITION_FIRED,
                            wid,
                            job_id=job_id,
                            core_lane=job.core_lane,
                            gate_id=gate.gate_id,
                            payload={
                                "stop_condition": StopCondition.LEGITIMACY_REJECTED,
                                "gate_id": gate.gate_id,
                            },
                        )
                        gate_rejected = True
                        break

            if gate_rejected:
                return self._make_failed(
                    schema,
                    StopCondition.LEGITIMACY_REJECTED,
                    jobs_completed,
                    jobs_pending,
                    report.health_score,
                )

            # ---- Job handler execution ----------------------------------
            if job.handler is not None:
                try:
                    result_payload = job.handler(job, ctx)
                    if not isinstance(result_payload, dict):
                        result_payload = {"result": result_payload}
                except Exception as exc:
                    self._emit(
                        WorkflowEventType.STOP_CONDITION_FIRED,
                        wid,
                        job_id=job_id,
                        core_lane=job.core_lane,
                        payload={
                            "stop_condition": StopCondition.COLLAPSE_DETECTED,
                            "exception": str(exc),
                        },
                    )
                    return self._make_failed(
                        schema,
                        StopCondition.COLLAPSE_DETECTED,
                        jobs_completed,
                        jobs_pending,
                        report.health_score,
                    )
            else:
                result_payload = {"no_op": True}

            # ---- Mark job complete ---------------------------------------
            self._emit(
                WorkflowEventType.JOB_COMPLETED,
                wid,
                job_id=job_id,
                core_lane=job.core_lane,
                payload={"handler_result": result_payload},
            )
            jobs_completed.append(job_id)
            jobs_pending.remove(job_id)

        # ---- All jobs done -----------------------------------------------
        final_health = self._current_health()
        self._emit(
            WorkflowEventType.WORKFLOW_COMPLETED,
            wid,
            payload={
                "jobs_completed": jobs_completed,
                "final_health": final_health,
            },
        )
        return WorkflowResult(
            workflow_id=wid,
            status="completed",
            stop_reason="",
            jobs_completed=list(jobs_completed),
            jobs_pending=[],
            event_log=list(self._event_log),
            final_health=final_health,
        )

    def get_event_log(self) -> List[WorkflowEvent]:
        """Return the full accumulated audit log across all runs."""
        return list(self._event_log)

    def replay_events(
        self,
        from_step: int = 0,
        to_step: int = -1,
    ) -> List[WorkflowEvent]:
        """
        Return a slice of the audit log by index.

        Parameters
        ----------
        from_step : int
            Start index (inclusive, 0-based).
        to_step : int
            End index (inclusive).  ``-1`` means the last event.

        Returns
        -------
        list[WorkflowEvent]
        """
        log = self._event_log
        if not log:
            return []
        end = len(log) if to_step == -1 else min(to_step + 1, len(log))
        return list(log[from_step:end])

    def pending_gates(self) -> List[HILGate]:
        """Return gates that are currently awaiting resolution."""
        return list(self._pending_gates)


# ---------------------------------------------------------------------------
# Convenience builder
# ---------------------------------------------------------------------------


def build_workflow(
    workflow_id: str,
    name: str,
    description: str,
    jobs: List[AgentJob],
    *,
    trust_floor: float = TRUST_PHI_MIN,
    max_autonomous_steps: int = 50,
) -> PentadWorkflowSchema:
    """
    Build a :class:`PentadWorkflowSchema`, inferring structural fields.

    The ``handoff_order`` is taken directly from the order of ``jobs``.
    The ``required_cores`` is derived as the de-duplicated set of
    ``job.core_lane`` values, preserving first-occurrence order.

    Parameters
    ----------
    workflow_id : str
        Unique workflow identifier.
    name : str
        Short human-readable name.
    description : str
        Full description of the workflow's purpose.
    jobs : list[AgentJob]
        Ordered list of jobs.
    trust_floor : float
        Minimum trust floor (default: TRUST_PHI_MIN).
    max_autonomous_steps : int
        Maximum iteration count before MAX_STEPS_EXCEEDED fires.

    Returns
    -------
    PentadWorkflowSchema
    """
    handoff_order = [j.job_id for j in jobs]

    # Preserve insertion order while de-duplicating
    seen: dict = {}
    for j in jobs:
        seen[j.core_lane] = None
    required_cores: Tuple[str, ...] = tuple(seen.keys())

    return PentadWorkflowSchema(
        workflow_id=workflow_id,
        name=name,
        description=description,
        agent_jobs=list(jobs),
        handoff_order=handoff_order,
        required_cores=required_cores,
        trust_floor=trust_floor,
        max_autonomous_steps=max_autonomous_steps,
    )
